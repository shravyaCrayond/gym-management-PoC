import sqlite3
from pathlib import Path

DB_PATH = "gym_management.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Attendance table
    c.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id TEXT NOT NULL,
            role TEXT NOT NULL,
            zone TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    # Violations table
    c.execute("""
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trainer_id TEXT NOT NULL,
            member_id TEXT NOT NULL,
            violation_type TEXT NOT NULL,
            zone TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            evidence_path TEXT
        )
    """)

    # Detected IDs table
    c.execute("""
        CREATE TABLE IF NOT EXISTS detected_ids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized and tables created (if not exist).")

def insert_attendance(person_id, role, zone, timestamp):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO attendance (person_id, role, zone, timestamp) VALUES (?, ?, ?, ?)",
        (person_id, role, zone, timestamp)
    )
    conn.commit()
    conn.close()
    print(f"📝 Logged attendance: {person_id} ({role}) in {zone} at {timestamp}")

def insert_violation(trainer_id, member_id, violation_type, zone, timestamp, evidence_path=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """INSERT INTO violations (trainer_id, member_id, violation_type, zone, timestamp, evidence_path)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (trainer_id, member_id, violation_type, zone, timestamp, evidence_path)
    )
    conn.commit()
    conn.close()
    print(f"⚠️ Logged violation: {trainer_id} with {member_id} in {zone} at {timestamp}")

def insert_detected_id(person_id, timestamp):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO detected_ids (person_id, timestamp) VALUES (?, ?)",
        (person_id, timestamp)
    )
    conn.commit()
    conn.close()
    print(f"🟢 Logged detected ID: {person_id} at {timestamp}")

init_db()