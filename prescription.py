# enum and exception classes for the pharmacy domain.
from enum import Enum


class PharmacyError(Exception):
    '''Base class for all pharmacy errors.'''


class ValidationError(PharmacyError):
    '''A validation error on a prescription or line.'''


class DispenseError(PharmacyError):
     '''A dispense or cancel cannot be completed.'''

class InvalidStatusTransitionError(DispenseError):
    """A dispense or cancel cannot be completed because the prescription is
    not in the correct status."""

class PrescriptionStatus(Enum):
    """The closed set of valid statuses"""
    PENDING = "pending"
    DISPENSED = "dispensed"
    CANCELLED = "cancelled"


class PrescriptionLine:
    """One medicine and quantity on a prescription (INV-10)."""
    def __init__(self, medicine_code, quantity):        
        if (not isinstance(quantity, int) or isinstance(quantity, bool)
                or quantity <= 0):
            raise ValidationError("Line quantity must be a positive whole number.")
        if medicine_code is None or str(medicine_code).strip() == "":
            raise ValidationError("Select a medicine for the line.")
        self._medicine_code = medicine_code
        self._quantity = quantity

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

        # Checked directly (not via add_line) so a dispensed or cancelled
        for line in lines:
            self._check_new_line(line)
            self._lines.append(line)
            
    # the following properties are read-only, so the repository can set them only via the constructor or assign_id()
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
        return list(self._lines)   # a copy, so callers cannot edit the list

#the following methods are called by the repository to update the prescription after it has been saved to the database
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
        """pending -> dispensed only (INV-12)."""
        if self._status is PrescriptionStatus.DISPENSED:
            raise InvalidStatusTransitionError("Prescription is already dispensed.")
        if self._status is PrescriptionStatus.CANCELLED:
            raise InvalidStatusTransitionError(
                "Cancelled prescriptions cannot be dispensed.")
        self._status = PrescriptionStatus.DISPENSED

    def cancel(self):
        """pending -> cancelled only (INV-12)."""
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
        """A1: blank prescriber code is allowed (stored as None)."""
        if code is None:
            return None
        code = str(code).strip()
        return code or None

    def __repr__(self):
        return (f"Prescription(id={self._prescription_id}, patient={self._patient_id}, "
                f"branch={self._branch_id}, status={self._status.value}, "
                f"lines={len(self._lines)})")