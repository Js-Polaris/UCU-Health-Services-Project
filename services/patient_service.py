"""Service for Screen S7: Register Patient (owner: Brenda).

Available methods for the View:
  register(patient_id, label) -> create a patient (label is optional)
  list_all()                  -> patients for dropdowns/table
"""

from patient import Patient
from repositories.patient_repository import PatientRepository


class PatientService:
    def __init__(self, conn):
        self._conn = conn
        self._patients = PatientRepository(conn)

    def register(self, patient_id, label=None):
        try:
            patient = Patient(patient_id, label)
            self._patients.add(patient)
            self._conn.commit()
            return patient
        except Exception:
            self._conn.rollback()
            raise

    def list_all(self):
        return self._patients.list_all()
