
import os

import pytest
import requests
from dotenv import load_dotenv

from setup import create_tables, get_connection, seed_data

load_dotenv(override=True)

DATABASE = os.getenv("DATABASE")
BASE_URL = os.getenv("BASE_URL")

def drop_all_tables(database_name):
    """Drop all tables in the test database."""
    with get_connection(database_name) as conn:
        with conn.cursor() as cursor:
            # Disable foreign key checks while dropping tables
            cursor.execute("SET session_replication_role = 'replica';")

            # Drop all tables
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

            # Re-enable foreign key checks
            cursor.execute("SET session_replication_role = 'origin';")
            conn.commit()


@pytest.fixture(scope="function")
def setup_db():
    """
    Setup and teardown logic for the test database.
    Drops all tables, recreates them, and seeds test data.
    In a real environment, we might even copy the development or production database
    """
    # Drop all existing tables
    drop_all_tables(DATABASE)

    # Create fresh tables
    create_tables(DATABASE)

    # Seed with test data
    seed_data(DATABASE)

    yield  # Tests run here

    # Cleanup after tests
    drop_all_tables(DATABASE)

# --------------- Test GET -------------------

@pytest.mark.instructors
def test_list_instructors(setup_db):
    """Test retrieving all instructors."""
    response = requests.get(f"{BASE_URL}/instructors")
    assert response.status_code == 200, "Failed to fetch instructors"
    instructors = response.json()
    assert isinstance(instructors, list), "Expected a list of instructors"
    assert len(instructors) > 0, "Expected at least one instructors"
    for instructor in instructors:
        assert "instructor_id" in instructor, "No id in instructor"
        assert "first_name" in instructor, "No title in instructor"
        assert "last_name" in instructor, "No release_date in instructor"
        assert "email" in instructor, "No genre_id in instructor"
        assert "department_id" in instructor, "No departent_id in instructor"


@pytest.mark.student
def test_create_student(setup_db):
    """Test creating a new student."""
    new_student = {
        "first_name": "Mary",
        "last_name": "Abi", 
        "email": "madea@gmail.se",
        "enrollment_date": "2024-01-15"
        }
    response = requests.post(f"{BASE_URL}/students", json=new_student)
    print("🛠 API Response:", response.status_code, response.json())
    assert response.status_code == 200, "Student creation failed"
    student = response.json()
    assert "id" in student, "Expected 'id' in response"
    assert student["first_name"] == new_student["first_name"]
    assert student["email"] == new_student["email"]

    


@pytest.mark.student
def test_get_students(setup_db):
    response = requests.get(f"{BASE_URL}/students")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data,list)
    assert len(data) >= 2

# --------- Test PUT -------------------

@pytest.mark.course
def test_update_existing_course(setup_db):
    """Test updating a course."""
    
    course_id = 1
    
    updated_course = {
        "name": "Updated Course Name",
        "credits": 5,
        "department_id": 1
    }
    
    response = requests.put(f"{BASE_URL}/courses/{course_id}", json=updated_course)
    assert response.status_code == 200, f"Failed to update course: {response.text}"
    updated_data = response.json()
    
    assert updated_data["name"] == updated_course["name"]
    assert updated_data["credits"] == updated_course["credits"]
    assert updated_data["department_id"] == updated_course["department_id"]


# --------- Test Delete -------------------

@pytest.mark.student
def test_delete_student_by_name(setup_db):
    """Test deleting student by id"""

    temp_student = {
        "first_name":"temp_first",
        "last_name": "temp_last",
        "email":"temp@student.se",
        "enrollment_date": "2024-09-13",
    }

    response = requests.post(f"{BASE_URL}/students", json= temp_student)
    assert response.status_code == 200 , "Failed to create student"

    del_response = response.json()
    temp_first = del_response.get("first_name")
    temp_last = del_response.get("last_name")

    assert temp_first is not None, "first_name not in response"
    assert temp_last is not None, "last_name not in response"

    delete_temp = requests.delete(f"{BASE_URL}/students/?first_name={temp_first}&last_name={temp_last}")
    assert delete_temp.status_code == 200, "Delete error"

    msg = delete_temp.json()
    assert "deleted successfully" in msg.get("message", "")

@pytest.mark.instructor
def test_patch_instructor(setup_db):
    response = requests.get(f"{BASE_URL}/instructors")
    assert response.status_code == 200, "Failed to fetch instructors"

    inst = response.json()
    assert isinstance(inst,list), "The list is tom"
    assert len(inst) > 0, "The list is empty"

    instructor_id = inst[1]["instructor_id"]
    
    update_instructor={"email": "requestpatched@email.com"}
    response = requests.patch(f"{BASE_URL}/instructors/?instructor_id={instructor_id}", json=update_instructor)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    response2 = requests.get(f"{BASE_URL}/instructors/{instructor_id}")
    upd_inst = response2.json()
    assert upd_inst["email"] == "requestpatched@email.com", "Email wasn't uppdated"
