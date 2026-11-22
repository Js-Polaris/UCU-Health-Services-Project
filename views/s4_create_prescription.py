"""Screen S4: Create Prescription (owner: Matthew).

Drop-in replacement for views/s4_create_prescription.py.

Pick a patient, a branch and an optional prescriber code. Add one or more
medicine/quantity lines, then click Create prescription. The whole
prescription (parent + all lines) is saved in one transaction by the service.

MVT rules followed:
  * No SQL here -- PrescriptionService owns the database work.
  * No business rules here -- Prescription/PrescriptionLine validate.
  * This View only manages temporary UI state: the list of lines being built.
  * Errors are shown exactly as received: show_error(str(exc)).
"""

import tkinter as tk
from tkinter import ttk

from services.branch_service import BranchService
from services.medicine_service import MedicineService
from services.patient_service import PatientService
from services.prescription_service import PrescriptionService
from templates.layouts import (
    form_section, make_expandable, screen_title, table_section,
)
from templates.widgets import (
    button_bar, clear_variables, data_table, labelled_combobox,
    labelled_entry, populate_table, show_error, show_info,
)


def _whole_number(text, field_name):
    """Turn form text into an int so the domain sees a real number."""
    try:
        return int(str(text).strip())
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a whole number.") from None


class CreatePrescriptionView(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent, padding=4)
        self._service = PrescriptionService(conn)
        patients = PatientService(conn)
        branches = BranchService(conn)
        medicines = MedicineService(conn)

        self._patient_options = {
            str(patient): patient.patient_id
            for patient in patients.list_all()
        }
        self._branch_options = {
            f"{b.branch_id} - {b.name}": b.branch_id
            for b in branches.list_all()
        }
        self._medicine_options = {
            f"{m.code} - {m.name}": m.code
            for m in medicines.list_all()
        }

        self._lines = []          # temporary UI state: [(code, quantity)]
        self._patient_var = tk.StringVar()
        self._branch_var = tk.StringVar()
        self._prescriber_var = tk.StringVar()
        self._line_medicine_var = tk.StringVar()
        self._line_qty_var = tk.StringVar()

        self._build()
        self._set_defaults()
        self.refresh_lines()

    def _build(self):
        screen_title(self, "Create Prescription", row=0)

        details = form_section(self, "Prescription details", row=1)
        labelled_combobox(
            details, "Patient", 0, list(self._patient_options),
            variable=self._patient_var,
        )
        labelled_combobox(
            details, "Branch", 1, list(self._branch_options),
            variable=self._branch_var,
        )
        labelled_entry(
            details, "Prescriber code (optional)", 2,
            variable=self._prescriber_var,
        )

        line_form = form_section(self, "Add a medicine line", row=2)
        labelled_combobox(
            line_form, "Medicine", 0, list(self._medicine_options),
            variable=self._line_medicine_var,
        )
        labelled_entry(line_form, "Quantity", 1, variable=self._line_qty_var)
        button_bar(line_form, [
            ("Add line", self._on_add_line),
            ("Remove selected line", self._on_remove_line),
        ], row=2)

        table_frame = table_section(self, "Lines on this prescription", row=3)
        self._lines_table = data_table(table_frame, [
            ("Medicine code", "code", 160),
            ("Quantity", "qty", 110),
        ])

        actions = ttk.Frame(self)
        actions.grid(row=4, column=0, columnspan=2, pady=(10, 6))
        ttk.Button(
            actions, text="Create prescription",
            command=self._on_create,
        ).grid(row=0, column=0, padx=6)
        ttk.Button(
            actions, text="Clear lines",
            command=self._clear_lines,
        ).grid(row=0, column=1, padx=6)

        make_expandable(self, row=3)

    def _set_defaults(self):
        if self._patient_options:
            self._patient_var.set(next(iter(self._patient_options)))
        if self._branch_options:
            self._branch_var.set(next(iter(self._branch_options)))
        if self._medicine_options:
            self._line_medicine_var.set(next(iter(self._medicine_options)))

    def _on_add_line(self):
        try:
            code = self._medicine_options.get(self._line_medicine_var.get())
            if code is None:
                raise ValueError("Select a medicine.")
            quantity = _whole_number(self._line_qty_var.get(), "Quantity")
            self._lines.append((code, quantity))
        except Exception as exc:
            show_error(str(exc))
            return
        self._line_qty_var.set("")
        self.refresh_lines()

    def _on_remove_line(self):
        selection = self._lines_table.selection()
        if not selection:
            show_error("Select a line to remove.")
            return
        index = self._lines_table.index(selection[0])
        del self._lines[index]
        self.refresh_lines()

    def _on_create(self):
        try:
            patient_id = self._patient_options.get(self._patient_var.get())
            branch_id = self._branch_options.get(self._branch_var.get())
            if patient_id is None:
                raise ValueError("Select a patient.")
            if branch_id is None:
                raise ValueError("Select a branch.")
            prescriber = self._prescriber_var.get() or None
            prescription = self._service.create(
                patient_id, branch_id, list(self._lines), prescriber)
        except Exception as exc:
            show_error(str(exc))
            return
        show_info(f"Prescription #{prescription.prescription_id} created.")
        self._clear_lines()

    def _clear_lines(self):
        self._lines = []
        self._line_qty_var.set("")
        clear_variables([self._prescriber_var])
        self.refresh_lines()

    def refresh_lines(self):
        populate_table(self._lines_table, [
            (code, quantity) for code, quantity in self._lines
        ])
