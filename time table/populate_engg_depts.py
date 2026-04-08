import sqlite3

def populate():
    conn = sqlite3.connect('timetable.db')
    c = conn.cursor()
    
    depts = [
        "Artificial Intelligence and Data Science",
        "Mechanical Engineering",
        "Civil Engineering",
        "Electrical and Electronics Engineering",
        "Electronics and Communication Engineering",
        "Information Science and Engineering",
        "Biotechnology Engineering",
        "Chemical Engineering",
        "Aerospace Engineering"
    ]
    
    for d in depts:
        try:
            c.execute('INSERT INTO departments (name) VALUES (?)', (d,))
        except sqlite3.IntegrityError:
            pass # ignore duplicates
            
    conn.commit()
    conn.close()
    print("Engineering departments added successfully.")

if __name__ == '__main__':
    populate()
