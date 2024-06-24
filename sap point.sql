CREATE TABLE students (
    student_rollno INT PRIMARY KEY,
    student_name VARCHAR(100),
    program_of_study VARCHAR(100),
    enrollment_status VARCHAR(50),
    date_of_enrollment DATE,
    expected_graduation_date DATE
);

CREATE TABLE courses (
    course_rollno INT PRIMARY KEY,
    course_name VARCHAR(100),
    credit_hours INT
);

CREATE TABLE grades (
    student_rollno INT,
    course_id INT,
    grade VARCHAR(2),
    semester VARCHAR(20),
    FOREIGN KEY (student_rollno) REFERENCES students(student_rollno),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);


CREATE TABLE academic_requirements (
    minimum_gpa FLOAT,
    minimum_completion_rate INT,
    maximum_time_frame INT
);