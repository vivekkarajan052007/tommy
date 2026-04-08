import sqlite3

def populate():
    conn = sqlite3.connect('timetable.db')
    c = conn.cursor()
    
    departments = [
        "Computer Science", "Information Technology", "Mathematics", 
        "Physics", "Chemistry", "Electrical Engineering", 
        "Mechanical Engineering", "Civil Engineering", "Business Administration",
        "English Literature", "Biology", "Psychology"
    ]
    
    subjects = [
        # CS / IT
        ("Introduction to Programming", "CS101", "Computer Science"),
        ("Data Structures", "CS201", "Computer Science"),
        ("Operating Systems", "CS301", "Computer Science"),
        ("Artificial Intelligence", "CS401", "Computer Science"),
        ("Web Development", "IT201", "Information Technology"),
        ("Database Systems", "IT202", "Information Technology"),
        ("Cybersecurity", "IT301", "Information Technology"),
        
        # Engineering
        ("Circuit Analysis", "EE101", "Electrical Engineering"),
        ("Microprocessors", "EE301", "Electrical Engineering"),
        ("Thermodynamics", "ME201", "Mechanical Engineering"),
        ("Fluid Mechanics", "ME301", "Mechanical Engineering"),
        ("Structural Analysis", "CE201", "Civil Engineering"),
        
        # Sciences & Math
        ("Calculus I", "MA101", "Mathematics"),
        ("Linear Algebra", "MA201", "Mathematics"),
        ("Discrete Mathematics", "MA202", "Mathematics"),
        ("Quantum Mechanics", "PH301", "Physics"),
        ("Electromagnetism", "PH201", "Physics"),
        ("Organic Chemistry", "CH201", "Chemistry"),
        ("Genetics", "BI201", "Biology"),
        
        # Arts / Business
        ("Principles of Accounting", "BA101", "Business Administration"),
        ("Marketing Strategies", "BA201", "Business Administration"),
        ("Modern Poetry", "EN201", "English Literature"),
        ("Cognitive Psychology", "PY301", "Psychology")
    ]
    
    # Insert Departments
    for d in departments:
        try:
            c.execute('INSERT INTO departments (name) VALUES (?)', (d,))
        except sqlite3.IntegrityError:
            pass # ignore duplicates
            
    # Insert Subjects
    for s in subjects:
        try:
            # check if exists
            c.execute('SELECT COUNT(*) FROM subjects WHERE code = ?', (s[1],))
            if c.fetchone()[0] == 0:
                c.execute('INSERT INTO subjects (name, code, department) VALUES (?, ?, ?)', s)
        except Exception as e:
            pass
            
    conn.commit()
    conn.close()
    print("Database populated successfully.")

if __name__ == '__main__':
    populate()
