##PRIMARY KEY (branch_id, medicine_code)

import sqlite3
from domainExceptions import DuplicateStockError, ValidationError
from StockItem import StockItem

class StockRepository:
    def __init__(self, conn):
        self._conn = conn
    def add(self,item):
        ##this is where we insert a new stock record.
        try:
            self._conn.execute(
                """Insert into STOCK (branch_id, medicine_id, quantity) VALUES(?,?,?)""",
                ##seed order matters here thats why branch and medicin appear first
                (item.branch_id, item.medicine_code, item.qauntity),
            )
        except sqlite3.IntegrityError as exc:
            message = str(exc).upper()
            if "UNIQUE" in message or "PRIMARY KEY" in message:
                raise DuplicateStockError(f"Stock already registered for {item.medicine_code} at {item.branch_id} branch") from exc
            raise ValidationError(f"Invalid stock data: {exc}") from exc

##returning a stock item or none if that pair is not registered
    def get(self, branch_id, medicine_code):
        row = self._conn.execute(
            """SELECT branch_id, medicine_id, quantity FROM stock Where branch_id = ? AND medicine_code =?""",
            (branch_id,str(medicine_code).strip().upper()),
        ).fetchall()
        return self._to_domain(row) if row is not None else None
    def list_for_branch(self, branch_id):
        #for all stock held at a branch
        rows = self._conn.execute("""SELECT branch_id, medicine_code, quantity
                       FROM stock WHERE branch_id = ? ORDER BY medicine_code""",
                       (branch_id,),).fetchall()
        return [self._to_domain(row) for row in rows] 
    def list_all(self):
        rows = self._conn.execute("""SELECT branch_id, medicine_code, quantity
                       FROM stock ORDER BY branch_id, medicine_code"""
        ).fetchall()
        return [self._to_domain(row) for row in rows]
    def save (self, item):
        """Write the current in-memory quantity back to the database.
        Call this after item.receive(n) or item.remove(n). The DB CHECK
        (quantity >= 0) is the second layer of defence."""
        cursor = self._conn.execute(
            """UPDATE stock SET quantity =?
            WHERE branch_id =? AND medicine_code =?""",
            (item.quantity, item.branch_id, item.medicine_code),
        )
        if cursor.rowcount ==0:
            raise ValidationError(f"There is no stock for {item.medicine_code} at the {item.branch_id} branch")
    @staticmethod
    def _to_domain(row):
        return StockItem(branch_id =row["branch_id"], medicine_code=row["medicine_code"], quantity=row["quantity"],)
                