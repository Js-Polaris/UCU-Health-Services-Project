"""Fictional seed data for the UCU pharmacy system.

Safe to run more than once: every INSERT uses the table's primary key, and
INSERT OR IGNORE skips rows that are already present.

Run from the repo root:  python -m db.seed

Fix reference (Milestone 2 / Step 6):
  * INSERT OR IGNORE INTO <table>  -- INTO is required in SQLite.
  * prescriber codes go in the `prescriber` table, not `patient`.
  * stock references `medicine_code`, not `medicine_id`.
  * MEDICINES must contain MED-004 because STOCK references it (foreign key).
  * TABLES values must be real table names (`patient`, not `patients`).
  * commit belongs to main(); seed() itself never commits.
"""

from db.connection import connect, create_schema

# (branch_id, name) -- ids match the Branch constants.
BRANCHES = [
    (101, "Mukono"),
    (102, "Kampala"),
    (103, "Kabale"),
]

# (code, name, unit_price, reorder_level, category)
# MED-004 was MED-006 on main; STOCK points at MED-004, so the FK failed.
MEDICINES = [
    ("MED-001", "Paracetamol", 500, 20, "ordinary"),
    ("MED-002", "Amoxicillin", 1200, 15, "ordinary"),
    ("MED-003", "Oral Rehydration Salts", 800, 30, "ordinary"),
    ("MED-004", "Morphine", 9000, 5, "controlled"),
    ("MED-005", "Pethidine", 15000, 3, "controlled"),
]

PATIENTS = [
    ("PT-0001", "Kyaligonza Toyota"),
    ("PT-0002", "Hyundai Deare"),
    ("PT-0003", "Ipsum Charlie"),
    ("PT-0004", "Hossana Asanide"),
    ("PT-0005", "Cliff Hanger"),
]

PRESCRIBERS = ["DR-001", "DR-002", "DR-003"]

# (branch_id, medicine_code, quantity)
STOCK = [
    (101, "MED-001", 120),
    (101, "MED-002", 60),
    (101, "MED-003", 200),
    (101, "MED-004", 8),
    (101, "MED-005", 3),    # at reorder level -> low
    (102, "MED-001", 18),   # below reorder level -> low
    (102, "MED-002", 40),
    (102, "MED-003", 90),
    (102, "MED-004", 12),
    (102, "MED-005", 6),
    (103, "MED-001", 75),
    (103, "MED-002", 10),   # below reorder level -> low
    (103, "MED-003", 50),
    (103, "MED-004", 4),    # below reorder level -> low
    (103, "MED-005", 9),
]

# key = label printed in the terminal; value = REAL table name in the schema.
TABLES = {
    "branch": "branch",
    "medicine": "medicine",
    "patient": "patient",
    "prescriber": "prescriber",
    "stock": "stock",
}


def seed(conn):
    """Insert all fictional data. Does not commit -- the caller decides."""
    conn.executemany(
        "INSERT OR IGNORE INTO branch (branch_id, name) VALUES (?, ?)",
        BRANCHES,
    )
    conn.executemany(
        """INSERT OR IGNORE INTO medicine
           (code, name, unit_price, reorder_level, category)
           VALUES (?, ?, ?, ?, ?)""",
        MEDICINES,
    )
    conn.executemany(
        "INSERT OR IGNORE INTO patient (patient_id, label) VALUES (?, ?)",
        PATIENTS,
    )
    conn.executemany(
        "INSERT OR IGNORE INTO prescriber (code) VALUES (?)",
        [(code,) for code in PRESCRIBERS],
    )
    # Stock last: its foreign keys need the rows above to exist.
    conn.executemany(
        """INSERT OR IGNORE INTO stock (branch_id, medicine_code, quantity)
           VALUES (?, ?, ?)""",
        STOCK,
    )


def counts(conn):
    return {name: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for name, table in TABLES.items()}


def main():
    conn = connect()
    try:
        create_schema(conn)
        seed(conn)
        conn.commit()   # sqlite3 has no autocommit() method
        for name, total in counts(conn).items():
            print(f"{name:12} {total}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
