CREATE TABLE Enrollments (
    enrollment_id SERIAL PRIMARY KEY,
	student_id INT,
    course_id INT,
    enrollment_date DATE,
    grade VARCHAR(100)
	);

	CREATE INDEX idx_student_id ON Enrollments (student_id);
	CREATE INDEX idx_course_id ON Enrollments (course_id);

CREATE TABLE Courses (
	course_id SERIAL PRIMARY KEY,
	name varchar(150),
	credits INT,
	department_id INT
);

CREATE TABLE Students (
	student_id SERIAL PRIMARY KEY,
	first_name varchar (150),
	last_name varchar (150),
	email VARCHAR(255) UNIQUE,
    enrollment_date DATE
);

	CREATE INDEX idx_email ON Students (email);

CREATE TABLE Departments (
	department_id SERIAL PRIMARY KEY,
	name VARCHAR (250),
	location VARCHAR (300)
);

CREATE TABLE Instructors (
	instrutor_id SERIAL PRIMARY KEY,
	first_name VARCHAR (100),
	last_name VARCHAR (100),
	email VARCHAR (200),
	department_id INT
);

	CREATE INDEX inst_email ON Instructors (email);

INSERT INTO Departments (name, location)
VALUES
    ('Computer Science', 'Building A'),
    ('Mathematics', 'Building B');

INSERT INTO Courses (name, credits, department_id)
VALUES
    ('Database', 5, 1),
    ('Python', 5, 1),
    ('Geometry', 6, 2),
    ('Linear Algebra', 6, 2);

INSERT INTO Instructors (first_name, last_name, email, department_id)
VALUES
    ('John', 'Doe', 'john.doe@ua.se', 1),
    ('Jane', 'Smith', 'jane.smith@ua.se', 1),
    ('Alice', 'Johnson', 'alice.johnson@ua.se', 2),
    ('Bob', 'Brown', 'bob.brown@ua.se', 2),
    ('Eve', 'Davis', 'eve.davis@ua.se', 1);

INSERT INTO Students (first_name, last_name, email, enrollment_date)
VALUES
    ('Mahta', 'Ghorbani', 'mahta.ghorbanit@yh.se', '2024-08-21'),
    ('Maryam', 'Marzban', 'maryam.marzban@yh.se', '2023-09-01'),
    ('Jesper', 'Nilsson', 'jesper.nilsson@yh.se', '2025-01-20'),
    ('Jacob', 'Åkerblom', 'jakob.akerblom@yh.se', '2024-08-21'),
    ('sara', 'Känngård', 'sara.kanngard@yh.se', '2023-09-01'),
    ('Armando', 'Charlesston', 'armando.charlesston@yh.se', '2025-01-20');

INSERT INTO Enrollments (student_id, course_id, enrollment_date, grade)
VALUES
    (1, 1, '2024-08-21', 'A'), 
    (2, 1, '2023-09-01', 'B'), 
    (3, 2, '2025-01-20', 'A'), 
    (4, 3, '2024-08-21', 'C'), 
    (5, 4, '2023-09-01', 'B'), 
    (6, 2, '2025-01-20', 'A'); 