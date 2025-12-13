import sqlite3
import pandas as pd
from typing import Any, Iterable
class DatabaseManager:
    """Handles SQLite database connections and queries."""
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._connection: sqlite3.Connection | None = None
    def connect(self) -> None:
        if self._connection is None:
            self._connection = sqlite3.connect(self._db_path)
    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None
    def execute_query(self, sql: str, params: Iterable[Any] = ()):
        """Execute a write query (INSERT, UPDATE, DELETE)."""
        if self._connection is None:
            self.connect()
        cur = self._connection.cursor()
        cur.execute(sql, tuple(params))
        self._connection.commit()
        return cur
    def fetch_one(self, sql: str, params: Iterable[Any] = ()):
        if self._connection is None:
            self.connect()
        cur = self._connection.cursor()
        cur.execute(sql, tuple(params))
        return cur.fetchone()
    def fetch_all(self, sql: str, params: Iterable[Any] = ()):
        if self._connection is None:
            self.connect()
        cur = self._connection.cursor() 
        cur.execute(sql, tuple(params))
        return cur.fetchall()
    def get_incidents_data():
        conn = sqlite3.connect("intelligence_platform.db")
        df = pd.read_sql_query("SELECT * FROM cyber_incidents", conn)
        conn.close()
        return df

def ensure_tables_exist(self):
    """Create tables if they don't exist."""
    self.connect()
    
    # Create cyber_incidents table
    self._connection.execute("""
        CREATE TABLE IF NOT EXISTS cyber_incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_type TEXT,
            severity TEXT,
            status TEXT DEFAULT 'Open',
            description TEXT
        )
    """)
    
    self._connection.commit()