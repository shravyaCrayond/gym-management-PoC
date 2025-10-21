import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = "gym_management.db"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

try:
    c.execute("ALTER TABLE attendance ADD COLUMN duration_hours REAL DEFAULT 0")
    print(" Added column: duration_hours")
except sqlite3.OperationalError:
    print("ℹ Column 'duration_hours' already exists")

try:
    c.execute("ALTER TABLE attendance ADD COLUMN end_timestamp TEXT DEFAULT ''")
    print(" Added column: end_timestamp")
except sqlite3.OperationalError:
    print("ℹ Column 'end_timestamp' already exists")

conn.commit()
conn.close()
print(" Attendance table updated successfully")
