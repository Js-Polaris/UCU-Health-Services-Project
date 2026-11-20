from db.connection import connect

conn = connect()
print("medicine.code column:", list(conn.execute("PRAGMA table_info(medicine)")))
print("branches:", [r[0] for r in conn.execute("SELECT name FROM branch")])
print("medicines:", [r[0] for r in conn.execute("SELECT code FROM medicine")])
print("stock codes:", [r[1] for r in conn.execute("SELECT branch_id, medicine_code FROM stock")])