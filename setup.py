# setup.py

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(override=True)

DATABASE_NAME = os.getenv("DATABASE")
PASSWORD = os.getenv("PASSWORD")


def get_connection(database_name="university_db"):
    """Returnerar en anslutning till databasen"""
    return psycopg2.connect(
        dbname=database_name,
        user="postgres",
        password=PASSWORD,
        host="localhost",
        port="5432",
    )


def clear_data(database_name):
    con = get_connection(database_name)
    with con:
        with con.cursor() as cursor:
            cursor.execute("""
                TRUNCATE TABLE student_courses, enrollments, students, instructors, courses, departments 
                RESTART IDENTITY CASCADE;
            """)
    print("Data cleared successfully.")


def seed_data(database_name):
    """Hardcoded data insertion"""
    con = get_connection(database_name)
    with con:
        with con.cursor() as cursor:
            # Insert Courses
            cursor.execute("""
                INSERT INTO Courses (name, credits, department_id) VALUES 
                    ('Python', 5, 1), 
                    ('Geometry', 6, 2), 
                    ('Linear Algebra', 6, 2), 
                    ('Calculus', 4, 2),
                    ('Data Science', 5, 1);
            """)

            # Insert Instructors
            cursor.execute("""
                INSERT INTO instructors (first_name, last_name, email, department_id) VALUES
                    ('John', 'Doe', 'new_email@test.com', 2),
                    ('Bob', 'Brown', 'bob.brown@nackademin.se', 2),
                    ('Tobias', 'Fors', 'tobias.fors@ua.se', 1),
                    ('Dan', 'Söderlund', 'dan@nackademin.se', 1);
            """)

            # Insert Students
            cursor.execute("SELECT COUNT(*) FROM students;")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO students (first_name, last_name, email, enrollment_date) VALUES
                        ('Jesper', 'Nilsson', 'jesper.nilsson@yh.se', '2025-01-20'),
                        ('Jacob', 'Åkerblom', 'jacob.akerblom@yh.se', '2024-08-21'),
                        ('Armando', 'Charlesston', 'armando.charlesston@yh.se', '2025-01-20'),
                        ('Arina', 'Gustavsson', 'arina@yh.se', '2025-01-28'),
                        ('Maryam', 'Marz', 'maryam@yh.se', '2024-02-02'),
                        ('Mahta', 'Ghorbani', 'mahta.ghorbani@yh.se', '2024-08-30');
                """)

            # Insert Departments
            cursor.execute("""
                INSERT INTO departments (name, location) VALUES 
                    ('Computer Science', 'Building A'), 
                    ('Mathematics', 'Building B');
            """)

            # Insert Enrollments
            cursor.execute("""
                INSERT INTO enrollments (student_id, course_id, enrollment_date, grade) VALUES 
                    (1, 1, '2024-08-21', 'A'), 
                    (2, 1, '2023-09-01', 'B'), 
                    (3, 2, '2025-01-20', 'A'), 
                    (4, 3, '2024-08-21', 'C'), 
                    (5, 4, '2023-09-01', 'B'),
                    (6, 2, '2025-01-20', 'A');
            """)


            # Insert student_courses
            cursor.execute("""
                INSERT INTO student_courses (student_id, course_id, grade) VALUES 
                    (3, 4, 3), 
                    (3, 1, 4), 
                    (3, 5, 3), 
                    (4, 2, 4),
                    (4, 1, 5),
                    (6, 5, 4),
                    (6, 4, 3),
                    (6, 1, 3),
                    (6, 3, 3),
                    (2, 5, 4),
                    (2, 2, 4),
                    (2, 3, 5), 
                    (2, 1, 3);
            """)
        
    print("Data seeded successfully.")


# Create tables if not exists
def create_tables(DATABASE_NAME):
    con = get_connection(DATABASE_NAME)

    create_courses_table_query = """
    CREATE TABLE IF NOT EXISTS Courses (
        course_id SERIAL PRIMARY KEY,
        name VARCHAR(150) UNIQUE,
        credits INT,
        department_id INT
    );
    """

    create_instructors_table_query = """
    CREATE TABLE IF NOT EXISTS Instructors (
        instructor_id SERIAL PRIMARY KEY,
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        email VARCHAR(200),
        department_id INT
    );
    """

    create_students_table_query = """
    CREATE TABLE IF NOT EXISTS Students (
        student_id SERIAL PRIMARY KEY,
        first_name VARCHAR(150),
        last_name VARCHAR(150),
        email VARCHAR(255) UNIQUE,
        enrollment_date DATE
    );
    """

    create_departments_table_query = """
    CREATE TABLE IF NOT EXISTS Departments (
        department_id SERIAL PRIMARY KEY,
        name VARCHAR(250),
        location VARCHAR(300)
    );
    """

    create_enrollments_table_query = """
    CREATE TABLE IF NOT EXISTS Enrollments (
        enrollment_id SERIAL PRIMARY KEY,
        student_id INT,
        course_id INT,
        enrollment_date DATE,
        grade CHAR(1) CHECK (grade IN ('A', 'B', 'C', 'D', 'F'))
    );
    """

    create_student_courses_table_query = """
    CREATE TABLE IF NOT EXISTS student_courses (
                student_id int,
                course_id int,
                grade DECIMAL(2,1) CHECK (grade IN (1.0, 2.0, 3.0, 4.0, 5.0)),
                PRIMARY KEY (student_id, course_id),
                FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES Courses(course_id) ON DELETE CASCADE
            );
            """

    with con.cursor() as cursor:
        cursor.execute(create_courses_table_query)
        print("Courses table created.")

        cursor.execute(create_instructors_table_query)
        print("Instructors table created.")

        cursor.execute(create_students_table_query)
        print("Students table created.")

        cursor.execute(create_departments_table_query)
        print("Departments table created.")

        cursor.execute(create_enrollments_table_query)
        print("Enrollments table created.")

        cursor.execute(create_student_courses_table_query)
        print("student_courses table created.")

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_student_id ON Enrollments (student_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_course_id ON Enrollments (course_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS inst_email ON Instructors (email);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_email ON Students (email);")


    if con:
        con.commit()
        con.close()


if __name__ == "__main__":
    # 1. create tables
    create_tables(DATABASE_NAME)
    print("Tables created successfully.")

    # 2. clear data
    clear_data(DATABASE_NAME)

    # 3. insert new data
    seed_data(DATABASE_NAME)
