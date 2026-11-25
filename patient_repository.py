#Takes an open sqlite3 connection. the connection helper must run PRAGMA foreign keys = ON
import sqlite3
from patient import Patient
from domainExceptions import DuplicatePatientError, UnknownPatientError

PATIENT_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS patient (
    patient_id TEXT PRIMARY KEY NOT NULL
        CHECK (patient_id GLOB 'PT-[0-9][0-9][0-9][0-9]'),
    label      TEXT
);
"""

class PatientRepository:
    def __init__(self, connection):
        self._conn = connection

    def add(self, patient):
        #save new patient. Raises duplicatepatienterror if the id exists
        try:
            with self._conn:
                self._conn.execute(
                    (patient.patient_id, patient.label),
                )
        except sqlite3.IntegrityError:
            raise DuplicatePatientError("Patient ID already exists") from None

    def get(self, patient_id):
        #return the patient, or raise unknownpatienterror
        row = self._conn.execute(
            (patient_id,),).fetchone()
        if row is None:
            raise UnknownPatientError("Select a registered patient.")
        return Patient(row[0], row[1])

    def exists(self, patient_id):
        row = self._conn.execute(
            "SELECT 1 FROM patient WHERE patient_id = ?", (patient_id,)
        ).fetchone()
        return row is not None

    def list(self):
        #all patients, ordered by ID
        rows = self._conn.execute(
            "SELECT patient_id, label FROM patient ORDER BY patient_id"
        ).fetchall()
        return [Patient(row[0], row[1]) for row in rows]

    def  save(self, patient):
        #update the label of an existing patient (id never changes)
        with self._conn:
            cur = self._conn.execute(
                "UPDATE patient SET label = ? WHERE patient_id = ?",
                (patient.label, patient.patient_id),
        )

        if cur.rowcount == 0:
            raise UnknownPatientError("Select a registered patient.")

