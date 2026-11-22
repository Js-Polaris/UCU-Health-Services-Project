"""All SQL for the stock table lives in this file.

The stock table has a composite key (branch_id, medicine_code): one medicine
can be held at several branches, with a different quantity at each.

Fix reference (Milestone 2 / Step 5):
  * `medicine_id` -> `medicine_code` in the INSERT and SELECT (schema column).
  * `item.qauntity` -> `item.quantity` (typo in add()).
  * `get()` used fetchall() but then treated the result as one row -> fetchone().
  * Repositories never commit or roll back; the service owns the transaction.
"""

import sqlite3

from domainExceptions import DuplicateStockError, ValidationError
from StockItem import StockItem


class StockRepository:
    def __init__(self, conn):
        self._conn = conn

    def add(self, item):
        """Insert a new stock record. The caller owns commit/rollback."""
        try:
            self._conn.execute(
                """INSERT INTO stock (branch_id, medicine_code, quantity)
                   VALUES (?, ?, ?)""",
                (item.branch_id, item.medicine_code, item.quantity),
            )
        except sqlite3.IntegrityError as exc:
            message = str(exc).upper()
            if "UNIQUE" in message or "PRIMARY KEY" in message:
                raise DuplicateStockError(
                    f"Stock already registered for {item.medicine_code} "
                    f"at branch {item.branch_id}.") from exc
            raise ValidationError(f"Invalid stock data: {exc}") from exc

    def get(self, branch_id, medicine_code):
        """Return one StockItem, or None if that pair is not registered."""
        row = self._conn.execute(
            """SELECT branch_id, medicine_code, quantity
               FROM stock WHERE branch_id = ? AND medicine_code = ?""",
            (branch_id, str(medicine_code).strip().upper()),
        ).fetchone()
        return self._to_domain(row) if row is not None else None

    def list_for_branch(self, branch_id):
        """All stock held at one branch (Screens 3 and 6)."""
        rows = self._conn.execute(
            """SELECT branch_id, medicine_code, quantity
               FROM stock WHERE branch_id = ? ORDER BY medicine_code""",
            (branch_id,),
        ).fetchall()
        return [self._to_domain(row) for row in rows]

    def list_all(self):
        rows = self._conn.execute(
            """SELECT branch_id, medicine_code, quantity
               FROM stock ORDER BY branch_id, medicine_code"""
        ).fetchall()
        return [self._to_domain(row) for row in rows]

    def save(self, item):
        """Write the in-memory quantity back after receive()/remove().

        The DB CHECK (quantity >= 0) is the second layer of defence.
        """
        cursor = self._conn.execute(
            """UPDATE stock SET quantity = ?
               WHERE branch_id = ? AND medicine_code = ?""",
            (item.quantity, item.branch_id, item.medicine_code),
        )
        if cursor.rowcount == 0:
            raise ValidationError(
                f"No stock record for {item.medicine_code} "
                f"at branch {item.branch_id}.")

    @staticmethod
    def _to_domain(row):
        return StockItem(
            branch_id=row["branch_id"],
            medicine_code=row["medicine_code"],
            quantity=row["quantity"],
        )
