"""Screen S4: Create Prescription (owner: Matthew).

Build a form with a patient dropdown, a branch dropdown, an optional
prescriber code, and one or more medicine+quantity lines. Call
PrescriptionService.create(patient_id, branch_id, line_pairs, prescriber_code).

Services available:
  PatientService(conn).list_all()       -> patients for dropdown
  BranchService(conn).list_all()        -> branches for dropdown
  MedicineService(conn).list_all()      -> medicines for line dropdown
  self._service.create(...)             -> returns a Prescription
  self._service.list_pending()          -> pending prescriptions table
"""

from tkinter import ttk

from services.prescription_service import PrescriptionService
from templates.layouts import screen_title


class CreatePrescriptionView(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent, padding=4)
        self._service = PrescriptionService(conn)
        self._build()

    def _build(self):
        screen_title(self, "Create Prescription")
        ttk.Label(
            self,
            text="TODO (Matthew): patient + branch dropdowns, prescriber code,\n"
                 "and medicine/quantity lines. Call PrescriptionService.create(...).",
        ).grid(row=1, column=0, sticky="w", padx=10, pady=10)
