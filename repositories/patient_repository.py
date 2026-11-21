"""All SQL for the patient table lives in this file (from Matthew's branch).

Fix reference:
  * add() and get() were passing only a tuple to execute(), with no SQL string.
  * `with self._conn` committed inside the repository, breaking the
    one-transaction rule; removed.
  * list() -> list_all() to match the other repositories' naming.
  * The connection is injected; this repository never commits or rolls back.
"""

import sqlite3

from domainExceptions import DuplicatePatientError, UnknownPatientError
from patient import Patient


class PatientRepository:
    def __init__(self, conn):
        self._conn = conn

    def add(self, patient):
        """Insert a patient. The caller owns commit/rollback."""
        try:
            self._conn.execute(
                "INSERT INTO patient (patient_id, label) VALUES (?, ?)",
                (patient.patient_id, patient.label),
            )
        except sqlite3.IntegrityError as exc:
            raise DuplicatePatientError("Patient ID already exists") from exc

    def get(self, patient_id):
        """Return a Patient, or raise UnknownPatientError."""
        row = self._conn.execute(
            "SELECT patient_id, label FROM patient WHERE patient_id = ?",
            (patient_id,),
        ).fetchone()
        if row is None:
            raise UnknownPatientError("Select a registered patient.")
        return Patient(row["patient_id"], row["label"])

    def exists(self, patient_id):
        row = self._conn.execute(
            "SELECT 1 FROM patient WHERE patient_id = ?", (patient_id,)
        ).fetchone()
        return row is not None

    def list_all(self):
        rows = self._conn.execute(
            "SELECT patient_id, label FROM patient ORDER BY patient_id"
        ).fetchall()
        return [Patient(row["patient_id"], row["label"]) for row in rows]

    def save(self, patient):
        """Update the label (the ID never changes)."""
        cursor = self._conn.execute(
            "UPDATE patient SET label = ? WHERE patient_id = ?",
            (patient.label, patient.patient_id),
        )
        if cursor.rowcount == 0:
            raise UnknownPatientError("Select a registered patient.")
