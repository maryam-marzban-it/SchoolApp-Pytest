# main.py

from fastapi import FastAPI, HTTPException, status, Depends
from psycopg2.extras import RealDictCursor
import psycopg2
from dotenv import load_dotenv
from setup import get_connection
import os
from typing import List, Optional
from fastapi import Query
from schemas import (
    CourseCreate,
    StudentCreate,
    StudentUpdate,
    CourseUpdate,
    InstructorUpdate,
    InstructorCreate,
    AverageGradeResponse,
    InstructorPatch
)

app = FastAPI()


# ----------------------  students  -------------------------

# Fetch all students
@app.get("/students", status_code=status.HTTP_200_OK)
def list_students():
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
            SELECT * FROM STUDENTS;
            """
            cursor.execute(query)
            result = cursor.fetchall()

    return result

# Search a student by using query parameter
@app.get("/students/filter", status_code=status.HTTP_200_OK)
def search_students(name: str = Query(..., min_length=1)):
    """
    Search for students by name (partial match).
    Example usage: /students/filter?name=arm
    """
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
            SELECT * FROM students 
            WHERE first_name ILIKE %s OR last_name ILIKE %s;
            """
            cursor.execute(query, (f"%{name}%", f"%{name}%"))
            results = cursor.fetchall()

    return results



# Fetch a specific student by ID
@app.get("/students/{student_id}")
def get_student(student_id: int):
    """Fetch a specific student by their ID."""
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM students WHERE student_id = %s;", (student_id,))
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Student not found")
    return result




# Delete a student by id
@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("DELETE FROM students WHERE student_id = %s RETURNING student_id;", (student_id,))
            deleted = cursor.fetchone()
            if not deleted:
                raise HTTPException(status_code=404, detail="Student not found")
    return {"message": f"Student with ID {student_id} deleted successfully."}


# Delete a student by name
@app.delete("/students/")
def delete_student_by_name(first_name: str, last_name: str):
    """
    Deletes a student by their first and last name.
    """
    with get_connection() as con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                DELETE FROM students 
                WHERE first_name = %s AND last_name = %s 
                RETURNING student_id, first_name, last_name;
            """, (first_name, last_name))
            
            deleted = cursor.fetchone()
            
            if not deleted:
                raise HTTPException(status_code=404, detail="Student not found")
    
    return {"message": f"Student '{first_name} {last_name}' deleted successfully.", "deleted_student": deleted}


# Create a student
@app.post("/students")
def create_student(student_input: StudentCreate):
    """
    Create a new student in the 'students' table.
    Returns the newly created student object with its ID.
    """
    with get_connection() as con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(
                    """
                    INSERT INTO students (first_name, last_name, email, enrollment_date)
                    VALUES (%s, %s, %s, %s)
                    RETURNING student_id;
                    """,
                    (student_input.first_name, student_input.last_name, 
                     student_input.email, student_input.enrollment_date)
                )
                inserted = cursor.fetchone()
            except psycopg2.errors.UniqueViolation:
                raise HTTPException(status_code=400, detail="Student already exists.")

    return {
        "id": inserted["student_id"],
        "first_name": student_input.first_name,
        "last_name": student_input.last_name,
        "email": student_input.email,
        "enrollment_date": student_input.enrollment_date
    }


# Update a student
@app.put("/students/{student_id}", response_model=StudentUpdate)
def update_student(student_id: int, student_update: StudentUpdate):
    """
    Updates a student's data.
    Returns the updated student object.
    """
    with get_connection() as con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute("""UPDATE students SET first_name = %s, last_name = %s, 
                                  email = %s, enrollment_date = %s 
                                  WHERE student_id = %s RETURNING *;""", 
                               (student_update.first_name, student_update.last_name, 
                                student_update.email, student_update.enrollment_date, student_id))
                
                updated_student = cursor.fetchone()
                
                if not updated_student:
                    raise HTTPException(status_code=404, detail="Student not found")
            except psycopg2.errors.ForeignKeyViolation:
                raise HTTPException(status_code=400, detail="Provided enrollment_date not valid")
            except psycopg2.errors.UniqueViolation:
                raise HTTPException(status_code=400, detail="Email already exists")
    
    return updated_student


# Avrerage grade for a student
@app.get("/students/{student_id}/average-grade", response_model=AverageGradeResponse)
def get_average_grade(student_id: int):
    """
    Gets average grade for a student.
    """
    with get_connection() as con:
        with con.cursor() as cursor:
            cursor.execute("""
                SELECT AVG(grade) 
                FROM student_courses 
                WHERE student_id = %s;
            """, (student_id,))
            avg_grade = cursor.fetchone()[0]

            if avg_grade is None:
                raise HTTPException(status_code=404, detail="Not found grade for this student")

    return AverageGradeResponse(student_id=student_id, average_grade=round(avg_grade, 2))



# -----------------------  Courses  ---------------------


# Fetch all courses
@app.get("/courses",status_code=status.HTTP_200_OK)
def list_course():
    """Fetch all courses from the database."""
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM courses;")
            result = cursor.fetchall()
    return result



# Fetch all courses from a specific department
@app.get("/departments/{department_id}/courses")
def list_courses_by_department(department_id: int):
    """Fetch all courses for a specific department."""
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM courses WHERE department_id = %s;", (department_id,))
            results = cursor.fetchall()
    return results


# Delete a course by ID
@app.delete("/courses/{course_id}")
def delete_course(course_id: int):
    """
    Deletes a course by its ID.
    """
    with get_connection() as con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("DELETE FROM courses WHERE course_id = %s RETURNING course_id;", (course_id,))
            deleted = cursor.fetchone()
            if not deleted:
                raise HTTPException(status_code=404, detail="Course not found")
    return {"message": f"Course with ID {course_id} deleted successfully."}



# Create a course
@app.post("/courses")
def create_course(course_input: CourseCreate):
    """
    Create a new course in the 'courses' table.
    Returns the newly created course object with its ID.
    """
    with get_connection() as con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(
                    """
                    INSERT INTO courses (name, credits, department_id)
                    VALUES (%s, %s, %s)
                    RETURNING course_id;
                    """,
                    (course_input.name, course_input.credits, 
                     course_input.department_id)
                )
                inserted = cursor.fetchone()
            except psycopg2.errors.UniqueViolation:
                raise HTTPException(status_code=400, detail="Course already exists.")

    return {
        "id": inserted["course_id"],
        "name": course_input.name,
        "credits": course_input.credits,
        "department_id": course_input.department_id,
    }


# Update a course
@app.put("/courses/{course_id}", response_model=CourseUpdate)
def update_course(course_id: int, course_update: CourseUpdate):
    """
    Updates a course's data.
    Returns the updated course object.
    """
    with get_connection() as con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute("""UPDATE courses SET name = %s, credits = %s, 
                                  department_id = %s WHERE course_id = %s RETURNING *;""", 
                               (course_update.name, course_update.credits, 
                                course_update.department_id, course_id))
                
                updated_course = cursor.fetchone()
                
                if not updated_course:
                    raise HTTPException(status_code=404, detail="Course not found")
            except psycopg2.errors.ForeignKeyViolation:
                raise HTTPException(status_code=400, detail="Provided department_id not valid")
            except psycopg2.errors.UniqueViolation:
                raise HTTPException(status_code=400, detail="Course name already exists")
    
    return updated_course



# ----------------------- Instructors  ---------------------------

# Fetch all instructors
@app.get("/instructors", status_code=status.HTTP_200_OK)
def list_instructors():
    """Fetch all instructors from the database."""
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM instructors;")
            result = cursor.fetchall()
    return result

@app.get("/instructors/{instructor_id}")
def get_instructor(instructor_id: int):
    """Fetch a specific instructor by their ID."""
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM instructors WHERE instructor_id = %s;", (instructor_id,))
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Instructor not found")
    return result


# Create an instructor
@app.post("/instructors")
def create_instructor(instructor_input: InstructorCreate):
    """
    Create a new instructor in the 'instructors' table.
    Returns the newly created instructor object with its ID.
    """
    with get_connection() as con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(
                    """
                    INSERT INTO instructors (first_name, last_name, email, department_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING instructor_id;
                    """,
                    (instructor_input.first_name, instructor_input.last_name, 
                     instructor_input.email, instructor_input.department_id
                ))
                inserted = cursor.fetchone()
            except psycopg2.errors.UniqueViolation as e:
                print(f"❌ UNIQUE CONSTRAINT ERROR: {e}")
                raise HTTPException(status_code=400, detail="Instructor already exists.")

    return {
        "id": inserted["instructor_id"],
        "first_name": instructor_input.first_name,
        "last_name": instructor_input.last_name,
        "email": instructor_input.email,
        "department_id": instructor_input.department_id,
    }


# Update instructor
@app.put("/instructors/{instructor_id}", response_model=InstructorUpdate)
def update_instructor(instructor_id: int, instructor_update: InstructorUpdate):
    """
    Updates an instructor's data.
    Returns the updated instructor object.
    """
    with get_connection() as con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute("""UPDATE instructors SET first_name = %s, last_name = %s, 
                                  email = %s, department_id = %s WHERE instructor_id = %s RETURNING *;""", 
                               (instructor_update.first_name, instructor_update.last_name, 
                                instructor_update.email, instructor_update.department_id, instructor_id))
                
                updated_instructor = cursor.fetchone()
                
                if not updated_instructor:
                    raise HTTPException(status_code=404, detail="Instructor not found")
            except psycopg2.errors.ForeignKeyViolation:
                raise HTTPException(status_code=400, detail="Provided department_id not valid")
            except psycopg2.errors.UniqueViolation:
                raise HTTPException(status_code=400, detail="Email already exists")
    
    return updated_instructor



#PATCH endpoints (funkar inte som det ska =( jag har även GPT-at men hittar inte felet!)
            # OCH JAG HAR STRÄVAT EFTER VG DEN GÅNGEN!!!
@app.patch("/instructors/", response_model=InstructorPatch)
def instructor_patch(instructor_id: int, instructors: InstructorPatch):
    """
    Partially updates an instructor's data.
    Returns the updated instructor object.
    """
    con = get_connection()
  
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM Instructors WHERE instructor_id = %s", (instructor_id,))
            instructor = cursor.fetchone()
            if not instructor:
                raise HTTPException(status_code=404, detail="Instructor not found")
            
            email = instructors.email if instructors.email is not None else instructor["email"]
            department_id = instructors.department_id if instructors.department_id is not None else instructor["department_id"]

            update_query = """
                UPDATE Instructors
                SET email = %s, department_id = %s
                WHERE instructor_id = %s
                returning *;
            """
            cursor.execute(update_query, (email,department_id, instructor_id))
            updated_instructor = cursor.fetchone()

           
            if not updated_instructor:
                raise HTTPException(status_code=400, detail="Instructor update failed")
    return updated_instructor

  

@app.get("/departments", status_code=status.HTTP_200_OK, tags= ["list_endpoints"])
def list_departments():
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            department_query = """select * from departments;"""
            cursor.execute(department_query)
            result = cursor.fetchall()

    return result

@app.get("/enrollments", status_code=status.HTTP_200_OK, tags= ["list_endpoints"])
def list_enrollments():
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            enrollment_query = """SELECT 
            enrollments.enrollment_id,
            students.first_name || ' ' || students.last_name AS student_name,
            courses.name AS course_name,
            enrollments.enrollment_date,
            enrollments.grade
            FROM enrollments
            JOIN students ON enrollments.student_id = students.student_id
            JOIN courses ON enrollments.course_id = courses.course_id;"""
            cursor.execute(enrollment_query)
            result = cursor.fetchall()

    return result