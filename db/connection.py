import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "health.db"
SCHEMA_PATH = Path(__file__).resolve().parent /"schema.sql"
def connect(db_path =None):
    ##Poening a connection with the foreign keys enabled andnamed row while 
    ##whilepassing (":memory:) in tests

    target = str(db_path) if db_path is not None else str(DB_PATH)
    conn =sqlite3.connect(target)
    conn.row_factory =sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
def create_schema(conn):
    ##Creates all the seven tables on the given connection
    with open(SCHEMA_PATH, encoding= "utf-8") as fh:
        conn.executescript(fh.read())

##parent.parent is my repo root. Our db lives in health.db
##The __file__allows it to run from anywhere as long as you launch python

