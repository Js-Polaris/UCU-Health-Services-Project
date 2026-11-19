
import re

from domainExceptions import PharmacyError, ValidationError, DispenseError, InvalidPatientIdError

# "PT-" followed by exactly 4 digits
_PATIENT_ID_PATTERN = re.compile(r"PT-[0-9]{4}")

MAX_LABEL_LENGTH = 100


class Patient:
    """A fictional patient.

    Encapsulation (INV-06): patient_id can be read but never changed.
    label can be changed, but only to valid text or None.
    """

    def __init__(self, patient_id, label=None):
        # Values are checked BEFORE being stored, so a bad Patient can't exist.
        # The underscore means "private, use the property instead".
        self._patient_id = self._validate_patient_id(patient_id)
        self._label = self._validate_label(label)

    @staticmethod
    def _validate_patient_id(patient_id):
        # isinstance stops numbers/None from crashing the check;
        # fullmatch requires the WHOLE text to fit PT-0001.
        if not isinstance(patient_id, str) or not _PATIENT_ID_PATTERN.fullmatch(patient_id):
            raise InvalidPatientIdError("Patient ID must look like PT-0001.")
        return patient_id

    @staticmethod
    def _validate_label(label):
        if label is None:
            return None
        if not isinstance(label, str):
            raise ValidationError("Patient label must be text.")
        label = label.strip()
        if len(label) > MAX_LABEL_LENGTH:
            raise ValidationError(
                f"Patient label must be {MAX_LABEL_LENGTH} characters or fewer."
            )
        return label or None  # blank text becomes None

    @property
    def patient_id(self):
        # No setter exists, so the ID is read-only (this enforces INV-06).
        return self._patient_id

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        # Same checks as the constructor.
        self._label = self._validate_label(value)

    def __eq__(self, other):
        # Operator overloading: two patients are equal if their IDs match.
        if not isinstance(other, Patient):
            return NotImplemented
        return self._patient_id == other._patient_id

    def __hash__(self):
        # Required whenever __eq__ is defined; equal patients need equal hashes.
        return hash(self._patient_id)

    def __str__(self):
        # Text shown in lists and dropdowns, e.g. "PT-0001 - Test patient A".
        if self._label:
            return f"{self._patient_id} - {self._label}"
        return self._patient_id

    def __repr__(self):
        return f"Patient(patient_id={self._patient_id!r}, label={self._label!r})"