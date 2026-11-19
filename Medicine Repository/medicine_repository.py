import sqlite3

from domainExceptions import DuplicateCodeError, ValidationError
from Medicine import OrdinaryMedicine, ControlledMedicine

class MedicineRepository:
    """Convert medicine rows to domain objects and back.

    The category column decides which subclass to build when loading a row.
    """

    def __init__(self, conn):
        #the open database connection, shared with other repositories
        self._conn = conn

    def add(self, medicine):
        """Insert a medicine. The caller owns commit/rollback."""
        try:
            #"?" these are placeholders that keep user input out of the SQL text
            self._conn.execute(
                """INSERT INTO medicine
                   (code, name, unit_price, reorder_level, category)
                   VALUES (?, ?, ?, ?, ?)""",
                self._to_values(medicine),
            )
        except sqlite3.IntegrityError as exc:
            message = str(exc).upper()
            #a duplicate code breaks the PRIMARY KEY rule
            if "UNIQUE" in message or "PRIMARY KEY" in message:
                raise DuplicateCodeError(
                    f"Medicine code already exists: {medicine.code}") from exc
            # CHECK / NOT NULL failures should already have been caught by the
            # domain setters. Translate them anyway so no raw sqlite3 error escapes.
            raise ValidationError(f"Invalid medicine data: {exc}") from exc

    def get(self, code):
        """Return a medicine, or None if the code is unknown."""
        row = self._conn.execute(
            """SELECT code, name, unit_price, reorder_level, category
               FROM medicine WHERE code = ?""",
               #cleaning the code 
            (self._clean_code(code),),
        ).fetchone()
        #turn the row into an object only if one was found 
        return self._to_domain(row) if row is not None else None

    def list_all(self):
        rows = self._conn.execute(
            """SELECT code, name, unit_price, reorder_level, category
               FROM medicine ORDER BY name"""
        #getting all rows as a list
        ).fetchall()
        #each row becomes an object
        return [self._to_domain(row) for row in rows]

    @staticmethod
    def _clean_code(code):
        # same cleaning, making sure there are no spaces, and everything is in uppercase
        return str(code).strip().upper()

    @staticmethod
    def _to_values(medicine):
        """Domain object -> tuple of column values."""
        #the order must match the columns in the INSERT statement
        return (
            medicine.code,
            medicine.name,
            medicine.unit_price,
            medicine.reorder_level,
            #ordinary or controlled
            medicine.category,
        )

    @staticmethod
    def _to_domain(row):
        """DB row -> the correct Medicine subclass."""
        #the four values both subclasses need 
        values = (row["code"], row["name"],
                  row["unit_price"], row["reorder_level"])
        category = row["category"]
        #the category column decides which class to build
        if category == "ordinary":
            #* unpacks the tuple into arguments
            return OrdinaryMedicine(*values)
        if category == "controlled":
            return ControlledMedicine(*values)
        #any other value means the category column holds something that isn't ordinary or controlled 
        raise ValidationError(f"Unknown medicine category: {category!r}")



    