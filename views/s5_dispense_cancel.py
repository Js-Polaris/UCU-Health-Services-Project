"""Screen S5: Dispense / Cancel Prescription (owner: Samuel).

Show pending prescriptions in a table. Selecting a row exposes two buttons:
Dispense and Cancel. Confirm destructive actions with ask_yes_no().

Services available:
  PrescriptionService(conn).list_pending() -> pending prescriptions table
  self._service.dispense(prescription_id)  -> atomic dispense
  self._service.cancel(prescription_id)    -> atomic cancel
"""

from tkinter import ttk

from services.dispensing_service import DispensingService
from templates.layouts import screen_title


class DispenseCancelView(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent, padding=4)
        self._service = DispensingService(conn)
        self._build()

    def _build(self):
        screen_title(self, "Dispense / Cancel Prescription")
        ttk.Label(
            self,
            text="TODO (Samuel): pending-prescription table with Dispense and\n"
                 "Cancel buttons. Call dispense(id) / cancel(id) in try/except.",
        ).grid(row=1, column=0, sticky="w", padx=10, pady=10)
