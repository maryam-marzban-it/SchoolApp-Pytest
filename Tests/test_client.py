# test_client.py

import pytest
from fastapi.testclient import TestClient
from main import app
from setup import create_tables, get_connection, seed_data
import os
from dotenv import load_dotenv

# client-fixturen
@pytest.fixture
def client():
    return TestClient(app)


load_dotenv(override=True)

DATABASE = os.getenv("DATABASE")
BASE_URL = os.getenv("BASE_URL")


def drop_all_tables(database_name):
    """Drop all tables in the test database."""
    print(f"⚠️ Rensar databasen: {database_name}")
    with get_connection(database_name) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SET session_replication_role = 'replica';")
            cursor.execute("""
                DO $$ 
                DECLARE 
                    r RECORD;
                BEGIN
                    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                    END LOOP;
                END $$;
            """)
            cursor.execute("SET session_replication_role = 'origin';")
            conn.commit()


@pytest.fixture(scope="function")
def setup_db():
    """
    Setup och teardown för testdatabasen.
    Drops all tables, recreates them, and seeds test data.
    """
    drop_all_tables(DATABASE)
    create_tables(DATABASE)
    seed_data(DATABASE)

    yield  

    drop_all_tables(DATABASE)

#------------- Test for courses ---------------------

def test_get_courses(client, setup_db):
    response = client.get("/courses")
    assert response.status_code == 200, "Test fetch courses"
    courses = response.json()
    assert isinstance(courses, list), "Test list of courses"
    assert len(courses) > 0, "Expected at least one course"


@pytest.mark.createcourse
def test_create_course(client, setup_db):
    """Test registering a new course."""
    new_course = {
        "name": "Testing3",
        "credits": 5,
        "department_id": 1
    }
    response = client.post("/courses", json=new_course)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == new_course["name"]
    assert data["credits"] == new_course["credits"]
    assert data["department_id"] == new_course["department_id"]
    assert "id" in data 

     
    

@pytest.mark.course
def test_update_course(client, setup_db):
    """Test updating a course's details."""

    course_id = 1
    updated_course = {
        "name": "Updated Course Name",
        "credits": 5,
        "department_id": 2,  
    }

    response = client.put(f"/courses/{course_id}", json=updated_course)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    course = response.json()
    assert course["name"] == updated_course["name"], "Course name was not updated correctly"
    assert course["credits"] == updated_course["credits"], "Credits were not updated correctly"
    assert course["department_id"] == updated_course["department_id"], "Department ID was not updated correctly"


# ------------------ Test for instructors ---------------------------

# def test_get_instructors(setup_db):
    
#     response = client.get("/instructors")
#     assert response.status_code == 200 ,"Test fetch instructors"
#     instructors = response.json()
#     assert isinstance(instructors, list), "Test fetching all instructors"


def test_get_instructors(client, setup_db):
    """Test fetching all instructors."""
    response = client.get("/instructors")
    assert response.status_code == 200
    instructors = response.json()
    assert isinstance(instructors, list)


def test_create_instructor(client, setup_db):
    """Test registering a new instructor."""
    new_instructor = {
        "first_name": "Sara",
        "last_name": "Isacsson",
        "email": "sara.isacsson@nackademin.se",
        "department_id": 2
    }
    response = client.post("/instructors", json=new_instructor)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == new_instructor["first_name"]
    assert data["last_name"] == new_instructor["last_name"]
    assert data["email"] == new_instructor["email"]
    assert data["department_id"] == new_instructor["department_id"]
    assert "id" in data


@pytest.mark.instructor
def test_update_instructor(client, setup_db):
    """Test updating a instructor's details."""

    instructor_id = 1
    updated_instructor = {
        "first_name": "Updated_first_name",
        "last_name": "Updated_last_name",
        "email": "instructor_update@example.com",
        "department_id": 1,
    }

    response = client.put(f"/instructors/{instructor_id}", json=updated_instructor)

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    instructor = response.json()
    assert instructor["first_name"] == updated_instructor["first_name"]
    assert instructor["last_name"] == updated_instructor["last_name"]
    assert instructor["email"] == updated_instructor["email"]
    assert instructor["department_id"] == updated_instructor["department_id"]

@pytest.mark.instructorpatch
def test_patch_instructor(client,setup_db):
    response = client.get("/instructors")
    assert response.status_code == 200, "Get error"

    inst = response.json()
    assert isinstance(inst,list), "The list is tom"
    assert len(inst) > 0, "The list is empty"

    instructor_id = inst[2]["instructor_id"]
    
    update_instructor={"email": "patched@email.com"}
    response = client.patch(f"/instructors/?instructor_id={instructor_id}", json=update_instructor)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    response2 = client.get(f"/instructors/{instructor_id}")
    upd_inst = response2.json()
    assert upd_inst["email"] == "patched@email.com", "Email wasn't uppdated"


# ------------------ Test for students ------------------------

@pytest.mark.student
def test_get_students(client, setup_db):
    """Test fetching all students."""
    response = client.get("/students")
    assert response.status_code == 200
    students = response.json()
    assert isinstance(students, list)

@pytest.mark.student  
def test_create_student(client, setup_db):
    """Test registering a new student."""
    new_student = {
        "first_name": "Mary",
        "last_name": "abi",
        "email": "maryg@yh.se",
        "enrollment_date": "2024-01-15"
    }
    response = client.post("/students", json=new_student)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == new_student["first_name"]
    assert data["last_name"] == new_student["last_name"]
    assert data["email"] == new_student["email"]
    assert data["enrollment_date"] == new_student["enrollment_date"]
    assert "id" in data 


@pytest.mark.student
def test_update_student(client, setup_db):
    """Test updating a student's details."""

    student_id = 1
    updated_student = {
        "first_name": "Updated_first_name",
        "last_name": "Updated_last_name",
        "email": "updated_student@example.com",
        "enrollment_date": "2024-01-01",
    }

    response = client.put(f"/students/{student_id}", json=updated_student)

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    student = response.json()
    assert student["first_name"] == updated_student["first_name"]
    assert student["last_name"] == updated_student["last_name"]
    assert student["email"] == updated_student["email"]
    assert student["enrollment_date"] == updated_student["enrollment_date"]

@pytest.mark.student
def test_delete_student_by_id(client, setup_db):
    """Test deleting student by id"""

    temp_student = {
        "first_name":"temp_first",
        "last_name": "temp_last",
        "email":"temp@student.se",
        "enrollment_date": "2024-09-13",
    }

    response =client.post("/students", json=temp_student)
  
   
    temp_id = response.json()["id"]
    print(f"Deleting student with ID: {temp_id} (Type: {type(temp_id)})")


    delete_temp = client.delete(f"/students/{temp_id}")
    assert delete_temp.status_code == 200

    response = client.get(f"/students/{temp_id}")
    assert response.status_code == 404, "Student should not exist after deletion"

    message = delete_temp.json()
    assert "deleted successfully" in message.get("message", "")

@pytest.mark.student
def test_delete_student_by_name(client, setup_db):
    """Test deleting student by name"""

    temp_student = {
        "first_name":"temp_first",
        "last_name": "temp_last",
        "email":"temp@student.se",
        "enrollment_date": "2024-09-13",
    }

    response = client.post("/students", json=temp_student)
    print("POST Response:", response.json())  # Debugga API-responsen

    temp_first = response.json()["first_name"]
    temp_last = response.json()["last_name"]


    delete_temp = client.delete(f"/students/?first_name={temp_first}&last_name={temp_last}")
    assert delete_temp.status_code == 200

    message = delete_temp.json()
    assert "deleted successfully" in message.get("message", "")

