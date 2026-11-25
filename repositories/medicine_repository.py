"""All SQL for the medicine table lives in this file (from Abi's branch).

Fix reference:
  * The file used to be in a folder called `Medicine Repository` (with a
    space), which is awkward to import. It now lives in `repositories/`.
  * The category column decides which subclass to build when loading a row.
  * The connection is injected; this repository never commits or rolls back.
"""

import sqlite3

from domainExceptions import DuplicateCodeError, ValidationError
from Medicine import OrdinaryMedicine, ControlledMedicine


class MedicineRepository:
    def __init__(self, conn):
        self._conn = conn

    def add(self, medicine):
        """Insert a medicine. The caller owns commit/rollback."""
        try:
            self._conn.execute(
                """INSERT INTO medicine
                   (code, name, unit_price, reorder_level, category)
                   VALUES (?, ?, ?, ?, ?)""",
                self._to_values(medicine),
            )
        except sqlite3.IntegrityError as exc:
            message = str(exc).upper()
            if "UNIQUE" in message or "PRIMARY KEY" in message:
                raise DuplicateCodeError(
                    f"Medicine code already exists: {medicine.code}") from exc
            raise ValidationError(f"Invalid medicine data: {exc}") from exc

    def get(self, code):
        """Return a medicine, or None if the code is unknown."""
        row = self._conn.execute(
            """SELECT code, name, unit_price, reorder_level, category
               FROM medicine WHERE code = ?""",
            (self._clean_code(code),),
        ).fetchone()
        return self._to_domain(row) if row is not None else None

    def list_all(self):
        rows = self._conn.execute(
            """SELECT code, name, unit_price, reorder_level, category
               FROM medicine ORDER BY name"""
        ).fetchall()
        return [self._to_domain(row) for row in rows]

    @staticmethod
    def _clean_code(code):
        # Medicine._validate_code stores codes uppercased and stripped.
        return str(code).strip().upper()

    @staticmethod
    def _to_values(medicine):
        """Domain object -> tuple of column values."""
        return (
            medicine.code,
            medicine.name,
            medicine.unit_price,
            medicine.reorder_level,
            medicine.category,
        )

    @staticmethod
    def _to_domain(row):
        """DB row -> the correct Medicine subclass."""
        values = (row["code"], row["name"],
                  row["unit_price"], row["reorder_level"])
        category = row["category"]
        if category == "ordinary":
            return OrdinaryMedicine(*values)
        if category == "controlled":
            return ControlledMedicine(*values)
        raise ValidationError(f"Unknown medicine category: {category!r}")
