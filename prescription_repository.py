import sqlite3 # this imports sql library for database operations

from domainExceptions import ValidationError
from prescription import Prescription, PrescriptionLine, PrescriptionStatus


class PrescriptionRepository:# a repository class for managing prescriptions in the database
    def __init__(self, conn):
        self._conn = conn

    def add(self, prescription):
        if prescription.prescription_id is not None:
            raise ValidationError("Prescription already has an identifier.")

        try:
            cursor = self._conn.execute(
                """INSERT INTO prescription
                   (patient_id, branch_id, prescriber_code, status)
                   VALUES (?, ?, ?, ?)""",
                (prescription.patient_id,
                 prescription.branch_id,
                 prescription.prescriber_code,
                 prescription.status.value),
            )
        except sqlite3.IntegrityError as exc:
            self._translate(exc)

        prescription_id = cursor.lastrowid
        for line in prescription.lines: # save each line in the prescription_line table
            try:
                self._conn.execute(
                    """INSERT INTO prescription_line
                       (prescription_id, medicine_code, quantity)
                       VALUES (?, ?, ?)""",
                    (prescription_id, line.medicine_code, line.quantity),
                )
            except sqlite3.IntegrityError as exc:
                self._translate(exc)

        prescription.assign_id(prescription_id)

    def get(self, prescription_id):# returns a Prescription object for the given prescription_id, or None if not found
        row = self._conn.execute(
            """SELECT prescription_id, patient_id, branch_id, prescriber_code,
                      status, created_at
               FROM prescription WHERE prescription_id = ?""",
            (prescription_id,),
        ).fetchone()
        return self._to_domain(row) if row is not None else None

    def list_all(self):# returns a list of all prescriptions, ordered by prescription_id descending
        rows = self._conn.execute(
            """SELECT prescription_id, patient_id, branch_id, prescriber_code,
                      status, created_at
               FROM prescription ORDER BY prescription_id DESC"""
        ).fetchall()
        return [self._to_domain(row) for row in rows]

    def list_pending(self):# returns a list of all pending prescriptions, ordered by prescription_id descending
        rows = self._conn.execute(
            """SELECT prescription_id, patient_id, branch_id, prescriber_code,
                      status, created_at
               FROM prescription WHERE status = 'pending'
               ORDER BY prescription_id DESC"""
        ).fetchall()
        return [self._to_domain(row) for row in rows]

    def save_status(self, prescription): # updates the status of an existing prescription in the database
        cursor = self._conn.execute(
            "UPDATE prescription SET status = ? WHERE prescription_id = ?",
            (prescription.status.value, prescription.prescription_id),
        )
        if cursor.rowcount == 0:
            raise ValidationError("Prescription not found.")

    def _to_domain(self, row): #translates a database row into a domain Prescription object, including its lines
        line_rows = self._conn.execute(
            """SELECT medicine_code, quantity FROM prescription_line
               WHERE prescription_id = ? ORDER BY medicine_code""",
            (row["prescription_id"],),
        ).fetchall()
        lines = [PrescriptionLine(r["medicine_code"], r["quantity"])
                 for r in line_rows]

        return Prescription(
            patient_id=row["patient_id"],
            branch_id=row["branch_id"],
            lines=lines,
            prescriber_code=row["prescriber_code"],
            status=PrescriptionStatus(row["status"]),  # string -> enum
            prescription_id=row["prescription_id"],
            created_at=row["created_at"],
        )

    @staticmethod
    def _translate(exc):# the following method translates database integrity errors into domain validation errors
        message = str(exc).upper()
        if "FOREIGN KEY" in message:
            raise ValidationError(
                "Unknown patient, branch, medicine or prescriber.") from exc
        if "UNIQUE" in message or "PRIMARY KEY" in message:
            raise ValidationError(
                "Duplicate medicine line on this prescription.") from exc
        raise ValidationError(f"Invalid prescription data: {exc}") from exc
