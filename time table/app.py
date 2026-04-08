import os
import random
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_FILE = 'timetable.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # Departments table
    c.execute('''CREATE TABLE IF NOT EXISTS departments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL)''')
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT)''')
    # Faculty table
    c.execute('''CREATE TABLE IF NOT EXISTS faculty (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    department TEXT,
                    max_hours INTEGER DEFAULT 40)''')
    # Rooms table
    c.execute('''CREATE TABLE IF NOT EXISTS rooms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_number TEXT UNIQUE NOT NULL,
                    capacity INTEGER)''')
    # Subjects table
    c.execute('''CREATE TABLE IF NOT EXISTS subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    code TEXT,
                    department TEXT)''')
    # Timetables table
    c.execute('''CREATE TABLE IF NOT EXISTS timetables (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    department TEXT,
                    semester TEXT,
                    section TEXT,
                    subject_id INTEGER,
                    faculty_id INTEGER,
                    room_id INTEGER,
                    day_of_week TEXT,
                    time_slot TEXT,
                    FOREIGN KEY(subject_id) REFERENCES subjects(id),
                    FOREIGN KEY(faculty_id) REFERENCES faculty(id),
                    FOREIGN KEY(room_id) REFERENCES rooms(id)
                 )''')

    # Insert default admin if none exists
    c.execute('SELECT COUNT(*) FROM users WHERE username = "admin"')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO users (username, password) VALUES ("admin", "admin123")')
        
    # Insert default departments if none exists
    c.execute('SELECT COUNT(*) FROM departments')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO departments (name) VALUES ("Computer Science")')
        c.execute('INSERT INTO departments (name) VALUES ("Mathematics")')
        c.execute('INSERT INTO departments (name) VALUES ("Physics")')
        
    conn.commit()
    conn.close()

# Initialize DB on startup
if not os.path.exists(DB_FILE):
    print("Initializing Database...")
init_db()

# --- API Endpoints ---

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
    conn.close()
    
    if user:
        return jsonify({"success": True, "message": "Login successful"}), 200
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/api/dashboard', methods=['GET'])
def dashboard_stats():
    conn = get_db_connection()
    faculty_count = conn.execute('SELECT COUNT(*) FROM faculty').fetchone()[0]
    rooms_count = conn.execute('SELECT COUNT(*) FROM rooms').fetchone()[0]
    classes_count = conn.execute('SELECT COUNT(*) FROM timetables').fetchone()[0]
    conn.close()
    return jsonify({
        "faculty": faculty_count,
        "rooms": rooms_count,
        "classes": classes_count
    })

# --- Endpoint: Departments ---
@app.route('/api/departments', methods=['GET', 'POST'])
def handle_departments():
    conn = get_db_connection()
    if request.method == 'GET':
        depts = conn.execute('SELECT * FROM departments').fetchall()
        conn.close()
        return jsonify([dict(d) for d in depts])
    elif request.method == 'POST':
        data = request.json
        try:
            conn.execute('INSERT INTO departments (name) VALUES (?)', (data['name'],))
            conn.commit()
        except sqlite3.IntegrityError:
            pass # Ignore if exists
        conn.close()
        return jsonify({"success": True}), 201

@app.route('/api/departments/<int:id>', methods=['DELETE'])
def delete_department(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM departments WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

# --- Faculty Endpoints ---
@app.route('/api/faculty', methods=['GET', 'POST'])
def handle_faculty():
    conn = get_db_connection()
    if request.method == 'GET':
        faculty = conn.execute('SELECT * FROM faculty').fetchall()
        # attach workload
        result = []
        for f in faculty:
            f_dict = dict(f)
            # count hours (each slot = 1 hour for simplicity)
            workload = conn.execute('SELECT COUNT(*) FROM timetables WHERE faculty_id = ?', (f_dict['id'],)).fetchone()[0]
            f_dict['workload'] = workload
            result.append(f_dict)
        conn.close()
        return jsonify(result)
        
    elif request.method == 'POST':
        data = request.json
        c = conn.cursor()
        c.execute('INSERT INTO faculty (name, department, max_hours) VALUES (?, ?, ?)',
                  (data['name'], data['department'], data.get('max_hours', 40)))
        conn.commit()
        conn.close()
        return jsonify({"success": True}), 201

@app.route('/api/faculty/<int:id>', methods=['DELETE'])
def delete_faculty(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM faculty WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

# --- Room Endpoints ---
@app.route('/api/rooms', methods=['GET', 'POST'])
def handle_rooms():
    conn = get_db_connection()
    if request.method == 'GET':
        rooms = conn.execute('SELECT * FROM rooms').fetchall()
        conn.close()
        return jsonify([dict(r) for r in rooms])
    elif request.method == 'POST':
        data = request.json
        conn.execute('INSERT INTO rooms (room_number, capacity) VALUES (?, ?)',
                     (data['room_number'], data.get('capacity', 30)))
        conn.commit()
        conn.close()
        return jsonify({"success": True}), 201

@app.route('/api/rooms/<int:id>', methods=['DELETE'])
def delete_room(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM rooms WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

# --- Subject Endpoints ---
@app.route('/api/subjects', methods=['GET', 'POST'])
def handle_subjects():
    conn = get_db_connection()
    if request.method == 'GET':
        subjects = conn.execute('SELECT * FROM subjects').fetchall()
        conn.close()
        return jsonify([dict(s) for s in subjects])
    elif request.method == 'POST':
        data = request.json
        conn.execute('INSERT INTO subjects (name, code, department) VALUES (?, ?, ?)',
                     (data['name'], data.get('code', ''), data['department']))
        conn.commit()
        conn.close()
        return jsonify({"success": True}), 201

@app.route('/api/subjects/<int:id>', methods=['DELETE'])
def delete_subject(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM subjects WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

# --- Timetable Endpoints ---
@app.route('/api/timetables', methods=['GET', 'POST'])
def handle_timetables():
    conn = get_db_connection()
    if request.method == 'GET':
        # Optional filters
        dept = request.args.get('department')
        sec = request.args.get('section')
        fac = request.args.get('faculty_id')
        
        query = '''
            SELECT t.*, s.name as subject_name, f.name as faculty_name, r.room_number 
            FROM timetables t
            LEFT JOIN subjects s ON t.subject_id = s.id
            LEFT JOIN faculty f ON t.faculty_id = f.id
            LEFT JOIN rooms r ON t.room_id = r.id
            WHERE 1=1
        '''
        params = []
        if dept:
            query += " AND t.department = ?"
            params.append(dept)
        if sec:
            query += " AND t.section = ?"
            params.append(sec)
        if fac:
            query += " AND t.faculty_id = ?"
            params.append(fac)
            
        entries = conn.execute(query, params).fetchall()
        conn.close()
        return jsonify([dict(e) for e in entries])
        
    elif request.method == 'POST':
        data = request.json
        faculty_id = data['faculty_id']
        room_id = data['room_id']
        day = data['day_of_week']
        time = data['time_slot']
        section = data['section']
        
        # Conflict Detection
        # 1. Faculty constraint: Same faculty, same day, same time
        fac_conflict = conn.execute(
            'SELECT * FROM timetables WHERE faculty_id = ? AND day_of_week = ? AND time_slot = ?',
            (faculty_id, day, time)
        ).fetchone()
        
        if fac_conflict:
            conn.close()
            return jsonify({"success": False, "message": "Conflict: Faculty is already assigned to a class during this time slot."}), 409
            
        # 2. Room constraint: Same room, same day, same time
        room_conflict = conn.execute(
            'SELECT * FROM timetables WHERE room_id = ? AND day_of_week = ? AND time_slot = ?',
            (room_id, day, time)
        ).fetchone()
        
        if room_conflict:
            conn.close()
            return jsonify({"success": False, "message": "Conflict: Room is already booked during this time slot."}), 409
            
        # 3. Section constraint: Same section, same day, same time
        sec_conflict = conn.execute(
            'SELECT * FROM timetables WHERE section = ? AND day_of_week = ? AND time_slot = ?',
            (section, day, time)
        ).fetchone()
        
        if sec_conflict:
            conn.close()
            return jsonify({"success": False, "message": f"Conflict: Section {section} already has a class scheduled at this time."}), 409

        # 4. Global constraint: Only one subject per time slot (requested by user)
        global_conflict = conn.execute(
            'SELECT * FROM timetables WHERE day_of_week = ? AND time_slot = ?',
            (day, time)
        ).fetchone()
        
        if global_conflict:
            conn.close()
            return jsonify({"success": False, "message": "Conflict: Another subject is already scheduled at this day and time slot."}), 409

        # Save Entry
        c = conn.cursor()
        c.execute('''INSERT INTO timetables (department, semester, section, subject_id, faculty_id, room_id, day_of_week, time_slot)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (data['department'], data['semester'], data['section'], data['subject_id'], data['faculty_id'], data['room_id'], data['day_of_week'], data['time_slot']))
        conn.commit()
        conn.close()
        return jsonify({"success": True}), 201

@app.route('/api/timetables/<int:id>', methods=['DELETE'])
def delete_timetable(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM timetables WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/auto_schedule', methods=['POST'])
def auto_schedule():
    data = request.json
    dept = data.get('department')
    sem = data.get('semester')
    sec = data.get('section')
    reqs = data.get('requirements', [])

    conn = get_db_connection()
    rooms = conn.execute('SELECT id FROM rooms').fetchall()
    if not rooms:
        conn.close()
        return jsonify({"success": False, "message": "No rooms available."}), 400

    room_ids = [r['id'] for r in rooms]
    existing_entries = conn.execute('SELECT room_id, faculty_id, section, day_of_week, time_slot FROM timetables').fetchall()
    occupied = [(e['room_id'], e['faculty_id'], e['section'], e['day_of_week'], e['time_slot']) for e in existing_entries]
    
    TIME_SLOTS = [
        "09:00 - 09:50", "09:50 - 10:40", "11:00 - 11:50", "11:50 - 12:40",
        "01:20 - 02:10", "02:10 - 03:00", "03:20 - 04:10"
    ]
    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    all_slots = [(d, t) for d in DAYS for t in TIME_SLOTS]
            
    scheduled_new = []
    for req in reqs:
        sub_id = int(req['subject_id'])
        fac_id = int(req['faculty_id'])
        count = int(req['count'])
        
        available_slots = list(all_slots)
        random.shuffle(available_slots)
        
        placed = 0
        for day, time in available_slots:
            if placed >= count:
                break
            
            # Global slot constraint: only one subject can exist in this day/time globally
            global_conflict = any(e[3] == day and e[4] == time for e in occupied)
            if global_conflict: continue
            
            fac_conflict = any(e[1] == fac_id and e[3] == day and e[4] == time for e in occupied)
            if fac_conflict: continue
            sec_conflict = any(e[2] == sec and e[3] == day and e[4] == time for e in occupied)
            if sec_conflict: continue
            taken_rooms = [e[0] for e in occupied if e[3] == day and e[4] == time]
            free_rooms = [r for r in room_ids if r not in taken_rooms]
            if not free_rooms: continue
                
            chosen_room = free_rooms[0]
            new_entry = (chosen_room, fac_id, sec, day, time, sub_id)
            occupied.append((chosen_room, fac_id, sec, day, time))
            scheduled_new.append(new_entry)
            placed += 1
            
        if placed < count:
            conn.close()
            return jsonify({"success": False, "message": f"Could only place {placed}/{count} classes for subject ID {sub_id} due to constraints."}), 409
            
    c = conn.cursor()
    for entry in scheduled_new:
        room_id, fac_id, section, day, time, sub_id = entry
        c.execute('''INSERT INTO timetables (department, semester, section, subject_id, faculty_id, room_id, day_of_week, time_slot)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (dept, sem, section, sub_id, fac_id, room_id, day, time))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

if __name__ == '__main__':
    # Add some sample data if db is newly created
    conn = get_db_connection()
    count = conn.execute('SELECT COUNT(*) FROM subjects').fetchone()[0]
    if count == 0:
        print("Populating sample data...")
        conn.execute('INSERT INTO faculty (name, department) VALUES ("Dr. Alan Turing", "Computer Science")')
        conn.execute('INSERT INTO faculty (name, department) VALUES ("Dr. Grace Hopper", "Computer Science")')
        conn.execute('INSERT INTO rooms (room_number, capacity) VALUES ("Room 101", 60)')
        conn.execute('INSERT INTO rooms (room_number, capacity) VALUES ("Room 102", 40)')
        conn.execute('INSERT INTO subjects (name, code, department) VALUES ("Data Structures", "CS201", "Computer Science")')
        conn.execute('INSERT INTO subjects (name, code, department) VALUES ("Operating Systems", "CS301", "Computer Science")')
        conn.commit()
    conn.close()
    app.run(debug=True, port=5000)
