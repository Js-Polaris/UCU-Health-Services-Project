"""All SQL for prescription and prescription_line lives in this file.

Fix reference: this is Samuel's repository moved from the repo root into the
`repositories/` package (where all the other repositories live). The SQL and
logic were already correct; only the location needed changing so DispensingService
can import `repositories.prescription_repository`.

A prescription is one parent row plus one or more line rows. Loading it means
rebuilding the full object graph, including converting the status string back
into a PrescriptionStatus enum member. The connection is injected and this
repository never commits or rolls back.
"""

import sqlite3

from domainExceptions import ValidationError
from prescription import Prescription, PrescriptionLine, PrescriptionStatus


class PrescriptionRepository:
    def __init__(self, conn):
        self._conn = conn

    def add(self, prescription):
        """Insert the parent and all its lines. Caller owns commit/rollback."""
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
        for line in prescription.lines:
            try:
                self._conn.execute(
                    """INSERT INTO prescription_line
                       (prescription_id, medicine_code, quantity)
                       VALUES (?, ?, ?)""",
                    (prescription_id, line.medicine_code, line.quantity),
                )
            except sqlite3.IntegrityError as exc:
                self._translate(exc)

        # The domain class exposes assign_id() precisely for this moment.
        prescription.assign_id(prescription_id)

    def get(self, prescription_id):
        """Return a fully rebuilt Prescription, or None."""
        row = self._conn.execute(
            """SELECT prescription_id, patient_id, branch_id, prescriber_code,
                      status, created_at
               FROM prescription WHERE prescription_id = ?""",
            (prescription_id,),
        ).fetchone()
        return self._to_domain(row) if row is not None else None

    def list_all(self):
        rows = self._conn.execute(
            """SELECT prescription_id, patient_id, branch_id, prescriber_code,
                      status, created_at
               FROM prescription ORDER BY prescription_id DESC"""
        ).fetchall()
        return [self._to_domain(row) for row in rows]

    def list_pending(self):
        """Screen 5: the prescriptions a pharmacist may dispense."""
        rows = self._conn.execute(
            """SELECT prescription_id, patient_id, branch_id, prescriber_code,
                      status, created_at
               FROM prescription WHERE status = 'pending'
               ORDER BY prescription_id DESC"""
        ).fetchall()
        return [self._to_domain(row) for row in rows]

    def save_status(self, prescription):
        """Write status back after mark_dispensed() or cancel()."""
        cursor = self._conn.execute(
            "UPDATE prescription SET status = ? WHERE prescription_id = ?",
            (prescription.status.value, prescription.prescription_id),
        )
        if cursor.rowcount == 0:
            raise ValidationError("Prescription not found.")

    def _to_domain(self, row):
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
    def _translate(exc):
        """Turn a raw sqlite3 error into one of our exceptions."""
        message = str(exc).upper()
        if "FOREIGN KEY" in message:
            raise ValidationError(
                "Unknown patient, branch, medicine or prescriber.") from exc
        if "UNIQUE" in message or "PRIMARY KEY" in message:
            raise ValidationError(
                "Duplicate medicine line on this prescription.") from exc
        raise ValidationError(f"Invalid prescription data: {exc}") from exc
