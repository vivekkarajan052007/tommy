import sqlite3

def populate_rooms():
    conn = sqlite3.connect('timetable.db')
    c = conn.cursor()
    
    rooms = []
    # F1 to F16
    for i in range(1, 17):
        rooms.append(f"F{i}")
    # S1 to S16
    for i in range(1, 17):
        rooms.append(f"S{i}")
        
    for r in rooms:
        try:
            # check if exists
            c.execute('SELECT COUNT(*) FROM rooms WHERE room_number = ?', (r,))
            if c.fetchone()[0] == 0:
                c.execute('INSERT INTO rooms (room_number, capacity) VALUES (?, ?)', (r, 60))
        except Exception as e:
            pass
            
    conn.commit()
    conn.close()
    print("Rooms F1-F16 and S1-S16 added successfully.")

if __name__ == '__main__':
    populate_rooms()
