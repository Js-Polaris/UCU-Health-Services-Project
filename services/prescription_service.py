"""Service for Screen S4: Create Prescription (owner: Matthew).

Available methods for the View:
  create(patient_id, branch_id, line_pairs, prescriber_code=None)
      line_pairs is a list of (medicine_code, quantity) tuples.
  list_pending() -> pending prescriptions
  list_all()     -> every prescription
"""

from prescription import Prescription, PrescriptionLine
from repositories.prescription_repository import PrescriptionRepository


class PrescriptionService:
    def __init__(self, conn):
        self._conn = conn
        self._prescriptions = PrescriptionRepository(conn)

    def create(self, patient_id, branch_id, line_pairs, prescriber_code=None):
        """Build the domain object from raw form values, then save it."""
        try:
            lines = [PrescriptionLine(code, quantity)
                     for code, quantity in line_pairs]
            prescription = Prescription(
                patient_id, branch_id, lines, prescriber_code)
            self._prescriptions.add(prescription)
            self._conn.commit()
            return prescription
        except Exception:
            self._conn.rollback()
            raise

    def list_pending(self):
        return self._prescriptions.list_pending()

    def list_all(self):
        return self._prescriptions.list_all()
