import mysql.connector

try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="subi",
        database="sapdatabase"
    )

    def insert_student_data(students):
        mycursor = mydb.cursor()
        sql = """
            INSERT INTO students (
                student_rollno, 
                student_name, 
                program, 
                enrollment_status, 
                date_of_enrollment, 
                expected_graduation_date
            ) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        for student in students:
            value = (
                int(student['student_rollno']), 
                student['student_name'], 
                student['program_of_study'], 
                student['enrollment_status'], 
                student['date_of_enrollment'], 
                student['expected_graduation_date']
            )
            mycursor.execute(sql, value)
        mydb.commit()

    def display_student_data():
        mycursor = mydb.cursor()
        sql = "SELECT * FROM students"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        for data in myresult:
            print(data)

    def insert_grades_data(grades):
        mycursor = mydb.cursor()
        sql = "INSERT INTO grades (student_rollno, course_id, grade, semester) VALUES (%s, %s, %s, %s)"
        for grade in grades:
            value = (
                grade['student_rollno'], 
                grade['course_id'], 
                grade['grade'], 
                grade['semester']
            )
            mycursor.execute(sql, value)
        mydb.commit()

    def insert_courses(courses):
        mycursor = mydb.cursor()
        sql = "INSERT INTO courses (course_id, course_name, credit_hours) VALUES (%s, %s, %s)"
        for course in courses:
            value = (
                course['course_id'],
                course['course_name'],
                course['credit_hours']
            )
            mycursor.execute(sql, value)
        mydb.commit()

    def course_exists(course_id):
        mycursor = mydb.cursor()
        sql = "SELECT 1 FROM courses WHERE course_id = %s"
        mycursor.execute(sql, (course_id,))
        return mycursor.fetchone() is not None

    def add_course_if_not_exists(course_id, course_name, credit_hours):
        if not course_exists(course_id):
            insert_courses([{
                'course_id': course_id,
                'course_name': course_name,
                'credit_hours': credit_hours
            }])

    def insert_academic_requirements(db, requirements):
        cursor = db.cursor()
        sql = "INSERT INTO academic_requirements (minimum_gpa, minimum_completion_rate, maximum_time_frame) VALUES (%s, %s, %s)"
        val = (requirements['minimum_gpa'], requirements['minimum_completion_rate'], requirements['maximum_time_frame'])
        cursor.execute(sql, val)
        db.commit()

    def calculate_gpa(db, student_rollno):
        cursor = db.cursor()
        cursor.execute("""
            SELECT g.grade, c.credit_hours
            FROM grades g
            JOIN courses c ON g.course_id = c.course_id
            WHERE g.student_rollno = %s
        """, (student_rollno,))
        
        grades = cursor.fetchall()
        total_points = 0
        total_credits = 0
        grade_points = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}
        
        for grade, credit_hours in grades:
            if grade in grade_points:
                total_points += grade_points[grade] * credit_hours
                total_credits += credit_hours
        
        if total_credits == 0:
            return 0.0
        return total_points / total_credits

    def calculate_completion_rate(db, student_rollno):
        cursor = db.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM grades WHERE student_rollno = %s
        """, (student_rollno,))
        total_courses = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM grades WHERE student_rollno = %s AND grade != 'F'
        """, (student_rollno,))
        completed_courses = cursor.fetchone()[0]
        
        if total_courses == 0:
            return 0
        return (completed_courses / total_courses) * 100

    def get_total_credit_hours_attempted_and_completed(db, student_rollno):
        cursor = db.cursor()
        cursor.execute("""
            SELECT SUM(c.credit_hours)
            FROM grades g
            JOIN courses c ON g.course_id = c.course_id
            WHERE g.student_rollno = %s
        """, (student_rollno,))
        total_credit_hours_attempted = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT SUM(c.credit_hours)
            FROM grades g
            JOIN courses c ON g.course_id = c.course_id
            WHERE g.student_rollno = %s AND g.grade != 'F'
        """, (student_rollno,))
        credit_hours_completed = cursor.fetchone()[0] or 0

        return total_credit_hours_attempted, credit_hours_completed

    def get_time_elapsed_since_enrollment(db, student_rollno):
        cursor = db.cursor()
        cursor.execute("""
            SELECT date_of_enrollment FROM students WHERE student_rollno = %s
        """, (student_rollno,))
        date_of_enrollment = cursor.fetchone()[0]

        cursor.execute("SELECT CURDATE()")
        current_date = cursor.fetchone()[0]

        time_elapsed = current_date - date_of_enrollment
        return time_elapsed.days // 365

    def generate_sap_report(db, student_rollno, requirements):
        gpa = calculate_gpa(db, student_rollno)
        completion_rate = calculate_completion_rate(db, student_rollno)
        
        cursor = db.cursor()
        cursor.execute("SELECT * FROM students WHERE student_rollno = %s", (student_rollno,))
        student = cursor.fetchone()

        total_credit_hours_attempted, credit_hours_completed = get_total_credit_hours_attempted_and_completed(db, student_rollno)
        time_elapsed_since_enrollment = get_time_elapsed_since_enrollment(db, student_rollno)

        report = {
            'student_id': student[0],
            'name': student[1],
            'current_semester_gpa': gpa,
            'cumulative_gpa': gpa,
            'minimum_gpa_required': requirements['minimum_gpa'],
            'credit_hours_attempted': total_credit_hours_attempted,
            'credit_hours_completed': credit_hours_completed,
            'completion_rate': completion_rate,
            'minimum_completion_rate_required': requirements['minimum_completion_rate'],
            'total_credit_hours_required': requirements['total_credit_hours_required'],  
            'credit_hours_completed_to_date': credit_hours_completed,
            'time_elapsed_since_enrollment': f"{time_elapsed_since_enrollment} years",
            'maximum_time_frame': requirements['maximum_time_frame'],
            'academic_standing': 'Good' if gpa >= requirements['minimum_gpa'] and completion_rate >= requirements['minimum_completion_rate'] else 'Warning',
            'financial_aid_status': 'Eligible' if gpa >= requirements['minimum_gpa'] and completion_rate >= requirements['minimum_completion_rate'] else 'Not Eligible'
        }

        return report

    print('\t\t\tSAP Point Collector')
    
    while True:
        print("Menu:")
        print("1. Insert Student Data")
        print("2. Display Student Data")
        print("3. Generate SAP Report")
        print("4. Exit")
        choice = int(input('Enter Choice: '))
        
        match choice:
            case 1:
                no_of_student = int(input('Enter the Number of Students: '))
                students = []
                
                print("Enter Student Details")
                for i in range(no_of_student):
                    student = {
                        'student_rollno': int(input('Enter student_rollno: ')),
                        'student_name': input('Enter student_name: '),
                        'program_of_study': input('Enter program_of_study: '),
                        'enrollment_status': input('Enter enrollment_status: '),
                        'date_of_enrollment': input('Enter date_of_enrollment (YYYY-MM-DD): '),
                        'expected_graduation_date': input('Enter expected_graduation_date (YYYY-MM-DD): ')
                    }
                    students.append(student)

                insert_student_data(students)
                
                grades = []
                print("Enter Course Details")
                for student in students:
                    no_of_courses = int(input(f"Enter the number of courses for student {student['student_name']} (Roll No: {student['student_rollno']}): "))
                    for _ in range(no_of_courses):
                        course_id = input('Enter course_id: ')
                        course_name = input('Enter course_name: ')
                        credit_hours = int(input('Enter credit_hours: '))
                        add_course_if_not_exists(course_id, course_name, credit_hours)
                        
                        grade = {
                            'student_rollno': student['student_rollno'],
                            'course_id': course_id,
                            'grade': input('Enter grade: '),
                            'semester': input('Enter semester: ')
                        }
                        grades.append(grade)

                insert_grades_data(grades)
            
            case 2:
                display_student_data()
            
            case 3:
                student_rollno = int(input('Enter the student roll number to generate the SAP report: '))
                requirements = {
                    'minimum_gpa': float(input('Minimum_gpa: ')),
                    'minimum_completion_rate': int(input('Minimum completion rate: ')),
                    'maximum_time_frame': '150%',
                    'total_credit_hours_required' : int(input('Total credit hours required: '))
                }
                report = generate_sap_report(mydb, student_rollno, requirements)
                for key, value in report.items():
                    print(f"{key}: {value}")
            
            case 4:
                print("Exiting...")
                break

            case _:
                print("Invalid choice. Please try again.")

except mysql.connector.Error as err:
    print(f"Error: {err}")
