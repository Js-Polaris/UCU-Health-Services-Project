"""Screen S7: Register Patient (owner: Brenda).

Build a form with patient ID (PT-0001 format) and an optional label, then call
PatientService.register(patient_id, label). Show all patients in a table.
Follow the pattern in s1_register_medicine.py.

Services available:
  self._service.register(patient_id, label) -> returns a Patient
  self._service.list_all()                  -> patients for table/dropdown
"""

from tkinter import ttk

from services.patient_service import PatientService
from templates.layouts import screen_title


class RegisterPatientView(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent, padding=4)
        self._service = PatientService(conn)
        self._build()

    def _build(self):
        screen_title(self, "Register Patient")
        ttk.Label(
            self,
            text="TODO (Brenda): patient ID + optional label form and a table.\n"
                 "Call PatientService.register(patient_id, label).",
        ).grid(row=1, column=0, sticky="w", padx=10, pady=10)
