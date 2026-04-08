import sqlite3

def cleanup():
    conn = sqlite3.connect('timetable.db')
    c = conn.cursor()
    
    kept_depts = [
        "Computer Science", 
        "Information Technology", 
        "Computer Science Engineering", 
        "Mathematics"
    ]
    
    placeholders = ','.join(['?']*len(kept_depts))
    
    # Delete subjects
    c.execute(f"DELETE FROM subjects WHERE department NOT IN ({placeholders})", kept_depts)
    
    # Delete departments
    c.execute(f"DELETE FROM departments WHERE name NOT IN ({placeholders})", kept_depts)
    
    conn.commit()
    conn.close()
    print("Irrelevant subjects and departments removed successfully.")

if __name__ == '__main__':
    cleanup()
