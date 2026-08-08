import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'backend', 'data', 'deepfake.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE jobs ADD COLUMN investigation_status VARCHAR(32) DEFAULT 'Needs Review' NOT NULL;")
    print("Added investigation_status column.")
except sqlite3.OperationalError as e:
    print("Error (might already exist):", e)

try:
    cursor.execute("ALTER TABLE jobs ADD COLUMN investigation_notes TEXT;")
    print("Added investigation_notes column.")
except sqlite3.OperationalError as e:
    print("Error (might already exist):", e)

conn.commit()
conn.close()
