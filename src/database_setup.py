import sqlite3
conn = sqlite3.connect('gym_management.db')
cursor = conn.cursor()

# Trainers table
cursor.execute('''
CREATE TABLE IF NOT EXISTS trainers (
    trainer_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    zone_assigned TEXT,
    shift_start TEXT,
    shift_end TEXT
)
''')

# Members table
cursor.execute('''
CREATE TABLE IF NOT EXISTS members (
    member_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    membership_type TEXT
)
''')

# Sessions table
cursor.execute('''
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    trainer_id TEXT,
    member_id TEXT,
    zone TEXT,
    start_time TEXT,
    end_time TEXT,
    FOREIGN KEY (trainer_id) REFERENCES trainers(trainer_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id)
)
''')

# Attendance table
cursor.execute('''
CREATE TABLE IF NOT EXISTS attendance (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id TEXT,
    role TEXT,
    zone TEXT,
    timestamp TEXT
)
''')

# Violations table
cursor.execute('''
CREATE TABLE IF NOT EXISTS violations (
    violation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    trainer_id TEXT,
    member_id TEXT,
    violation_type TEXT,
    zone TEXT,
    timestamp TEXT,
    evidence_path TEXT
)
''')

conn.commit()
conn.close()

print("Gym database setup complete: gym_management.db created!")
