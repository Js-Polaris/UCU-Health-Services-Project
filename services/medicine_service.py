"""Service for Screen S1: Register Medicine.

The View passes raw text from the form; this service builds the domain object
and owns the transaction. Domain validation errors are re-raised unchanged so
the View can show the exact message.
"""

from domainExceptions import ValidationError
from Medicine import OrdinaryMedicine, ControlledMedicine
from repositories.medicine_repository import MedicineRepository

_CLASSES = {
    "ordinary": OrdinaryMedicine,
    "controlled": ControlledMedicine,
}


class MedicineService:
    def __init__(self, conn):
        self._conn = conn
        self._medicines = MedicineRepository(conn)

    def register(self, code, name, unit_price, reorder_level, category):
        """Create and save a medicine. Returns the domain object."""
        try:
            key = str(category).strip().lower()
            medicine_class = _CLASSES.get(key)
            if medicine_class is None:
                raise ValidationError(
                    "Category must be 'ordinary' or 'controlled'.")
            medicine = medicine_class(code, name, unit_price, reorder_level)
            self._medicines.add(medicine)
            self._conn.commit()
            return medicine
        except Exception:
            self._conn.rollback()
            raise

    def list_all(self):
        """All medicines, for the screen's table."""
        return self._medicines.list_all()
