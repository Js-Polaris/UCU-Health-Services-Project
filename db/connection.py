"""Database connection helper.

Every repository and every test gets its connection from here. SQLite leaves
foreign key enforcement OFF by default, so it must be switched on for *every*
connection, including in-memory ones used in tests.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "pharmacy.db"


def connect(db_path=None):
    """Open a connection with foreign keys enabled and named row access.

    Pass connect(":memory:") in tests so the real data file is never touched.
    """
    target = str(db_path) if db_path is not None else str(DB_PATH)
    conn = sqlite3.connect(target)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
