import sqlite3

def populate_cse():
    conn = sqlite3.connect('timetable.db')
    c = conn.cursor()
    
    dept_name = "Computer Science Engineering"
    
    # Ensure department exists
    try:
        c.execute('INSERT INTO departments (name) VALUES (?)', (dept_name,))
    except sqlite3.IntegrityError:
        pass # ignore if exists
        
    subjects = [
        ("Programming in C", "CSE101", dept_name),
        ("Programming in C Lab", "CSE101L", dept_name),
        ("Object Oriented Programming", "CSE102", dept_name),
        ("Object Oriented Programming Lab", "CSE102L", dept_name),
        ("Design and Analysis of Algorithms", "CSE201", dept_name),
        ("Design and Analysis of Algorithms Lab", "CSE201L", dept_name),
        ("Computer Organization and Architecture", "CSE202", dept_name),
        ("Database Management Systems", "CSE301", dept_name),
        ("Database Management Systems Lab", "CSE301L", dept_name),
        ("Operating Systems", "CSE302", dept_name),
        ("Operating Systems Lab", "CSE302L", dept_name),
        ("Computer Networks", "CSE401", dept_name),
        ("Computer Networks Lab", "CSE401L", dept_name),
        ("Software Engineering", "CSE402", dept_name),
        ("Software Engineering Lab", "CSE402L", dept_name),
        ("Theory of Computation", "CSE501", dept_name),
        ("Compiler Design", "CSE502", dept_name),
        ("Compiler Design Lab", "CSE502L", dept_name),
        ("Artificial Intelligence", "CSE601", dept_name),
        ("Machine Learning", "CSE602", dept_name),
        ("Machine Learning Lab", "CSE602L", dept_name),
        ("Cryptography and Network Security", "CSE701", dept_name),
        ("Cloud Computing", "CSE702", dept_name),
        ("Data Science", "CSE801", dept_name),
        ("Data Science Lab", "CSE801L", dept_name),
        ("Internet of Things", "CSE802", dept_name),
        ("Internet of Things Lab", "CSE802L", dept_name),
        ("Web Technologies", "CSE403", dept_name),
        ("Web Technologies Lab", "CSE403L", dept_name),
        ("Mobile Application Development", "CSE503", dept_name),
        ("Mobile Application Development Lab", "CSE503L", dept_name),
        ("Human Computer Interaction", "CSE603", dept_name),
        ("Distributed Systems", "CSE703", dept_name)
    ]
    
    for s in subjects:
        try:
            c.execute('SELECT COUNT(*) FROM subjects WHERE code = ?', (s[1],))
            if c.fetchone()[0] == 0:
                c.execute('INSERT INTO subjects (name, code, department) VALUES (?, ?, ?)', s)
        except Exception as e:
            pass
            
    conn.commit()
    conn.close()
    print("CSE Subjects added successfully.")

if __name__ == '__main__':
    populate_cse()
