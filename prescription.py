"""Prescription domain objects (from Samuel's branch, with code fixes).

Fix reference:
  * PrescriptionLine now stores medicine codes stripped and UPPERCASED, so
    they match the `medicine.code` primary key and the stock table's
    `medicine_code` column.
  * Prescription._clean_code() now calls .upper(). The prescriber table
    stores codes like 'DR-001', so a lowercase entry would fail the FK.
  * Otherwise identical to Samuel's version -- status rules, line rules and
    the public API are unchanged.
"""

from enum import Enum

from domainExceptions import (
    ValidationError,
    DispenseError,
    InvalidStatusTransitionError,
)


class PrescriptionStatus(Enum):
    """The closed set of valid statuses."""

    PENDING = "pending"
    DISPENSED = "dispensed"
    CANCELLED = "cancelled"


class PrescriptionLine:
    """One medicine and quantity on a prescription."""

    def __init__(self, medicine_code, quantity):
        if (not isinstance(quantity, int) or isinstance(quantity, bool)
                or quantity <= 0):
            raise ValidationError("Line quantity must be a positive whole number.")
        if medicine_code is None or not str(medicine_code).strip():
            raise ValidationError("Select a medicine for the line.")
        self._medicine_code = str(medicine_code).strip().upper()
        self._quantity = quantity

    # Read-only: the repository sets these only through the constructor.
    @property
    def medicine_code(self):
        return self._medicine_code

    @property
    def quantity(self):
        return self._quantity

    def __repr__(self):
        return f"PrescriptionLine({self._medicine_code!r}, {self._quantity})"


class Prescription:
    def __init__(self, patient_id, branch_id, lines, prescriber_code=None,
                 status=PrescriptionStatus.PENDING, prescription_id=None,
                 created_at=None):
        if not patient_id:
            raise ValidationError("Select a registered patient.")
        if branch_id is None:
            raise ValidationError("Select a branch.")
        lines = list(lines)
        if not lines:
            raise ValidationError("Add at least one medicine line.")

        self._prescription_id = prescription_id
        self._patient_id = patient_id
        self._branch_id = branch_id
        self._prescriber_code = self._clean_code(prescriber_code)
        self._status = PrescriptionStatus(status)
        self._created_at = created_at
        self._lines = []

        # Raises ValidationError if any line is invalid or duplicated.
        for line in lines:
            self._check_new_line(line)
            self._lines.append(line)

    # These are read-only; the repository uses the constructor / assign_id().
    @property
    def prescription_id(self):
        return self._prescription_id

    @property
    def patient_id(self):
        return self._patient_id

    @property
    def branch_id(self):
        return self._branch_id

    @property
    def prescriber_code(self):
        return self._prescriber_code

    @property
    def status(self):
        return self._status

    @property
    def created_at(self):
        return self._created_at

    @property
    def lines(self):
        return list(self._lines)  # a copy, so callers cannot edit the list

    def assign_id(self, prescription_id):
        """Called once by the repository after the INSERT."""
        if self._prescription_id is not None:
            raise ValidationError("Prescription already has an identifier.")
        self._prescription_id = prescription_id

    def add_line(self, line):
        if self._status is not PrescriptionStatus.PENDING:
            raise InvalidStatusTransitionError(
                "Lines can only be added to a pending prescription.")
        self._check_new_line(line)
        self._lines.append(line)

    def mark_dispensed(self):
        if self._status is PrescriptionStatus.DISPENSED:
            raise InvalidStatusTransitionError("Prescription is already dispensed.")
        if self._status is PrescriptionStatus.CANCELLED:
            raise InvalidStatusTransitionError(
                "Cancelled prescriptions cannot be dispensed.")
        self._status = PrescriptionStatus.DISPENSED

    def cancel(self):
        if self._status is PrescriptionStatus.DISPENSED:
            raise InvalidStatusTransitionError(
                "A dispensed prescription cannot be cancelled.")
        if self._status is PrescriptionStatus.CANCELLED:
            raise InvalidStatusTransitionError("Prescription is already cancelled.")
        self._status = PrescriptionStatus.CANCELLED

    def _check_new_line(self, line):
        if not isinstance(line, PrescriptionLine):
            raise ValidationError("Each line must be a PrescriptionLine.")
        if any(l.medicine_code == line.medicine_code for l in self._lines):
            raise ValidationError("Medicine already added to this prescription.")

    @staticmethod
    def _clean_code(code):
        """Optional prescriber code: blanks become None."""
        if code is None:
            return None
        # Match PrescriberAllowList, which stores codes stripped and uppercased,
        # so the FK to prescriber(code) resolves.
        code = str(code).strip().upper()
        return code or None

    def __repr__(self):
        return (f"Prescription(id={self._prescription_id}, patient={self._patient_id}, "
                f"branch={self._branch_id}, status={self._status.value}, "
                f"lines={len(self._lines)})")
