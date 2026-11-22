""" Screen S5: Dispense / Cancel Prescription """

from tkinter import ttk

from services.dispensing_service import DispensingService
from services.prescription_service import PrescriptionService
from templates.layouts import make_expandable, screen_title, table_section
from templates.widgets import (
    ask_yes_no, button_bar, data_table, populate_table,
    selected_values, show_error, show_info,
)


class DispenseCancelView(ttk.Frame): # this class represents the GUI view for dispensing or canceling prescriptions
    def __init__(self, parent, conn):
        super().__init__(parent, padding=4)
        self._service = DispensingService(conn)
        self._prescriptions = PrescriptionService(conn)
        self._build()
        self.refresh_table()

    def _build(self): # this method builds the GUI layout for the view
        screen_title(self, "Dispense / Cancel Prescription", row=0)

        table_frame = table_section(self, "Pending prescriptions", row=1)
        self._table = data_table(table_frame, [
            ("ID", "id", 70),
            ("Patient", "patient", 110),
            ("Branch", "branch", 80),
            ("Prescriber", "prescriber", 110),
            ("Medicines", "lines", 240),
            ("Status", "status", 100),
        ])

        button_bar(self, [
            ("Dispense selected", self._on_dispense),
            ("Cancel selected", self._on_cancel),
            ("Refresh", self.refresh_table),
        ], row=2)

        make_expandable(self, row=1)

    def _selected_id(self): # this method gets the ID of the selected prescription
        values = selected_values(self._table)
        if values is None:
            show_error("Select a prescription first.")
            return None
        try:
            return int(values[0])
        except (TypeError, ValueError):
            show_error("Select a valid prescription.")
            return None

    def _on_dispense(self): # this method handles the dispense action for the selected prescription
        prescription_id = self._selected_id()
        if prescription_id is None:
            return
        if not ask_yes_no(f"Dispense prescription #{prescription_id}?"):
            return
        try:
            self._service.dispense(prescription_id)
        except Exception as exc:
            show_error(str(exc))
            return
        show_info(f"Prescription #{prescription_id} dispensed.")
        self.refresh_table()

    def _on_cancel(self): # this method handles the cancel action for the selected prescription
        prescription_id = self._selected_id()
        if prescription_id is None:
            return
        if not ask_yes_no(f"Cancel prescription #{prescription_id}?"):
            return
        try:
            self._service.cancel(prescription_id)
        except Exception as exc:
            show_error(str(exc))
            return
        show_info(f"Prescription #{prescription_id} cancelled.")
        self.refresh_table()

    def refresh_table(self): # this method refreshes the table with the latest prescription data
        rows = []
        for prescription in self._prescriptions.list_pending():
            lines = ", ".join(
                f"{line.medicine_code} x{line.quantity}"
                for line in prescription.lines
            )
            rows.append((
                prescription.prescription_id,
                prescription.patient_id,
                prescription.branch_id,
                prescription.prescriber_code or "-",
                lines,
                prescription.status.value,
            ))
        populate_table(self._table, rows)
