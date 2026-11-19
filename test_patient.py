"""Unit tests for the Patient domain class only (no database).

Run from the project's top folder with:  python -m unittest -v
"""

import unittest

from patient import Patient
from domainExceptions import InvalidPatientIdError, PharmacyError, ValidationError, DispenseError


# Inheritance: TestCase provides assertEqual, assertRaises and the test runner.
class TestPatientDomain(unittest.TestCase):

    def test_valid_patient(self):
        p = Patient("PT-0001", "Test patient A")
        self.assertEqual(p.patient_id, "PT-0001")
        self.assertEqual(p.label, "Test patient A")

    def test_label_is_optional(self):
        self.assertIsNone(Patient("PT-0002").label)
        # Spaces only: stored as None, not as blank text.
        self.assertIsNone(Patient("PT-0002", " ").label)

    def test_invalid_ids_rejected(self):
        for bad in ["PT-1", "PT-00011", "pt-0001", "PT0001", "PT-ABCD",
                    "John Doe", "", " PT-0001", "PT-0001\n", None, 1234]:
            # subTest reports each bad value separately.
            with self.subTest(bad=bad):
                with self.assertRaises(InvalidPatientIdError) as ctx:
                    Patient(bad)
                self.assertEqual(str(ctx.exception), "Patient ID must look like PT-0001.")

    # Encapsulation: patient_id has no setter, so it cannot be overwritten.
    def test_id_is_read_only(self):
        p = Patient("PT-0001")
        with self.assertRaises(AttributeError):
            p.patient_id = "PT-0002"
        self.assertEqual(p.patient_id, "PT-0001")

    # Encapsulation: the label setter trims spaces and rejects bad values.
    def test_label_setter_validates(self):
        p = Patient("PT-0001")
        p.label = " New label "
        self.assertEqual(p.label, "New label")
        with self.assertRaises(ValidationError):
            p.label = 42
        with self.assertRaises(ValidationError):
            p.label = "x" * 101
        # A failed update must leave the old label unchanged.
        self.assertEqual(p.label, "New label")

    # Operator overloading: equality is based on the ID, not the label.
    def test_equality_and_hash_use_id(self):
        self.assertEqual(Patient("PT-0001", "A"), Patient("PT-0001", "B"))
        self.assertNotEqual(Patient("PT-0001"), Patient("PT-0002"))
        self.assertEqual(len({Patient("PT-0001"), Patient("PT-0001")}), 1)

    # Inheritance: InvalidPatientIdError is a kind of PharmacyError.
    def test_errors_are_pharmacy_errors(self):
        with self.assertRaises(PharmacyError):
            Patient("bad")

    def test_str(self):
        self.assertEqual(str(Patient("PT-0001", "A")), "PT-0001 - A")
        self.assertEqual(str(Patient("PT-0001")), "PT-0001")


if __name__ == "__main__":
    unittest.main()