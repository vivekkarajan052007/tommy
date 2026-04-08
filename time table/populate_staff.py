import sqlite3
import random

first_names = ["Alan", "Grace", "Ada", "Charles", "John", "Jane", "Alice", "Bob", "Charlie", "David", "Eve", "Frank", "George", "Hannah", "Ivan", "Julia", "Kevin", "Laura", "Michael", "Nina", "Oliver", "Paula", "Quinn", "Rachel", "Steve", "Tina", "Ursula", "Victor", "Wendy", "Xavier", "Yvonne", "Zack"]
last_names = ["Turing", "Hopper", "Lovelace", "Babbage", "Von Neumann", "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen"]

conn = sqlite3.connect('timetable.db')
c = conn.cursor()

c.execute('SELECT name FROM departments')
departments = [row[0] for row in c.fetchall()]

added = 0
for dept in departments:
    for _ in range(3):
        first = random.choice(first_names)
        last = random.choice(last_names)
        name = f"Dr. {first} {last}"
        c.execute('INSERT INTO faculty (name, department) VALUES (?, ?)', (name, dept))
        added += 1

conn.commit()
conn.close()
print(f"Successfully added {added} staff members across {len(departments)} departments.")
