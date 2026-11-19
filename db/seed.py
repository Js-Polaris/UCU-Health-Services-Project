from db.connection import connect, create_schema
BRANCHES = [(101, "Mukono"),(102, "Kampala"), (103, "Kabale"),]
MEDICINES = [("MED-001", "Paracetamol", 500, 20, "ordinary"),
             ("MED-002", "Amoxicillin", 1200, 15, "ordinary"),
             ("MED-003", "Oral Rehydration Salts", 800, 30, "ordinary"),
             ("MED-004", "Pethidine", 15000, 3,"controlled"),
             ("MED-005", "Amitriptyline", 9000, 5, "controlled")]###digit one is the unit_price and digit two is the reorder_level
PATIENTS = [
    ("PT-0001", "Kyaligonza Toyota"),
    ("PT-0002", "Hyundai Deare"),
    ("PT-0003", "Ipsum Charlie"),
    ("PT-0004", "Hossana Asanide"),
    ("PT-0005", "Cliff Hanger"),
]
PRESCRIBERS = ["DR-001", "DR-002", "DR-003"]
STOCK= [(101, "MED-001", 120),
        (101, "MED-002", 60),
        (101, "MED-003", 200),
        (101, "MED-004", 8),
        (101, "MED-005", 3),#At reoder level
        (102, "MED-001", 18),##Below reorder level
        (102, "MED-002", 40),
        (102, "MED-003", 90),
        (102, "MED-004", 12),
        (102, "MED-005", 6),
        (103, "MED-001", 75),
        (103, "MED-002",10),##Below reorder level
        (103, "MED-003", 50),
        (103, "MED-004", 4),##below the reorder level
        (103, "MED-005",9)
        ]
TABLES = {
    "branch" : "branch",
    "medicine": "medicine",
    "patient" : "patient",
    "prescriber" :"prescriber",
    "stock" : "stock",
}
##Inserts the respective classes
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
    ##it has the foreign keys to medicine and branch. It takes an injected connection and deosn't commit

def counts(conn):
    return {name: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for name, table in TABLES.items()}
def main():
    conn = connect()
    try:
        create_schema(conn)
        seed(conn)
        conn.commit()
        for name, total in counts(conn).items():
            print(f"{name:12} {total}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
