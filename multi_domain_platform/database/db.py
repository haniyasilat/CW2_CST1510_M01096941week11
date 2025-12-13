import sqlite3
from pathlib import Path

DB_PATH = Path("database") / "intelligence_platform.db"

def connect_database(db_path=DB_PATH):
    """Connect to SQLite database."""
    return sqlite3.connect(str(db_path))
import sqlite3
conn = sqlite3.connect("database/intelligence_platform.db")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Existing tables:", tables)
conn.close()