import sqlite3

def populate_engg_subjects():
    conn = sqlite3.connect('timetable.db')
    c = conn.cursor()
    
    subjects_data = [
        # AI & DS
        ("Introduction to AI", "AIDS101", "Artificial Intelligence and Data Science"),
        ("Data Structures", "AIDS102", "Artificial Intelligence and Data Science"),
        ("Machine Learning", "AIDS201", "Artificial Intelligence and Data Science"),
        ("Deep Learning", "AIDS301", "Artificial Intelligence and Data Science"),
        ("Big Data Analytics", "AIDS302", "Artificial Intelligence and Data Science"),
        ("Natural Language Processing", "AIDS401", "Artificial Intelligence and Data Science"),
        
        # Mechanical Engineering
        ("Engineering Mechanics", "ME101", "Mechanical Engineering"),
        ("Thermodynamics", "ME201", "Mechanical Engineering"),
        ("Fluid Mechanics", "ME202", "Mechanical Engineering"),
        ("Heat and Mass Transfer", "ME301", "Mechanical Engineering"),
        ("Kinematics of Machinery", "ME302", "Mechanical Engineering"),
        ("Automobile Engineering", "ME401", "Mechanical Engineering"),
        
        # Civil Engineering
        ("Surveying", "CE101", "Civil Engineering"),
        ("Strength of Materials", "CE201", "Civil Engineering"),
        ("Structural Analysis", "CE202", "Civil Engineering"),
        ("Geotechnical Engineering", "CE301", "Civil Engineering"),
        ("Transportation Engineering", "CE302", "Civil Engineering"),
        ("Environmental Engineering", "CE401", "Civil Engineering"),
        
        # EEE (Electrical and Electronics)
        ("Electric Circuit Analysis", "EE101", "Electrical and Electronics Engineering"),
        ("Analog Electronics", "EE201", "Electrical and Electronics Engineering"),
        ("Electrical Machines I", "EE202", "Electrical and Electronics Engineering"),
        ("Power Systems", "EE301", "Electrical and Electronics Engineering"),
        ("Control Systems", "EE302", "Electrical and Electronics Engineering"),
        ("Power Electronics", "EE401", "Electrical and Electronics Engineering"),
        
        # ECE (Electronics and Communication)
        ("Digital Logic Design", "EC101", "Electronics and Communication Engineering"),
        ("Signals and Systems", "EC201", "Electronics and Communication Engineering"),
        ("Microprocessors and Microcontrollers", "EC301", "Electronics and Communication Engineering"),
        ("Digital Signal Processing", "EC302", "Electronics and Communication Engineering"),
        ("VLSI Design", "EC401", "Electronics and Communication Engineering"),
        ("Antennas and Wave Propagation", "EC402", "Electronics and Communication Engineering"),
        
        # ISE (Information Science)
        ("Data Structures with C", "IS101", "Information Science and Engineering"),
        ("Database Management Systems", "IS201", "Information Science and Engineering"),
        ("Software Engineering", "IS202", "Information Science and Engineering"),
        ("Computer Networks", "IS301", "Information Science and Engineering"),
        ("Web Technology", "IS302", "Information Science and Engineering"),
        ("Cloud Computing", "IS401", "Information Science and Engineering"),
        
        # Biotechnology
        ("Microbiology", "BT101", "Biotechnology Engineering"),
        ("Biochemistry", "BT201", "Biotechnology Engineering"),
        ("Cell Biology", "BT202", "Biotechnology Engineering"),
        ("Genetic Engineering", "BT301", "Biotechnology Engineering"),
        ("Bioprocess Engineering", "BT302", "Biotechnology Engineering"),
        ("Bioinformatics", "BT401", "Biotechnology Engineering"),
        
        # Chemical Engineering
        ("Chemical Process Calculations", "CH101", "Chemical Engineering"),
        ("Fluid Mechanics for Chemical Eng.", "CH201", "Chemical Engineering"),
        ("Heat Transfer Operations", "CH202", "Chemical Engineering"),
        ("Mass Transfer Operations I", "CH301", "Chemical Engineering"),
        ("Chemical Reaction Engineering", "CH302", "Chemical Engineering"),
        ("Process Dynamics and Control", "CH401", "Chemical Engineering"),
        
        # Aerospace Engineering
        ("Aerodynamics I", "AE101", "Aerospace Engineering"),
        ("Aircraft Structures I", "AE201", "Aerospace Engineering"),
        ("Flight Mechanics", "AE202", "Aerospace Engineering"),
        ("Propulsion I", "AE301", "Aerospace Engineering"),
        ("Space Mechanics", "AE302", "Aerospace Engineering"),
        ("Aircraft Design", "AE401", "Aerospace Engineering")
    ]
    
    for s in subjects_data:
        try:
            c.execute('SELECT COUNT(*) FROM subjects WHERE code = ?', (s[1],))
            if c.fetchone()[0] == 0:
                c.execute('INSERT INTO subjects (name, code, department) VALUES (?, ?, ?)', s)
        except Exception as e:
            pass
            
    conn.commit()
    conn.close()
    print("Subjects added for all engineering departments successfully.")

if __name__ == '__main__':
    populate_engg_subjects()
