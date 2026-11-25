
import tkinter as tk
from tkinter import ttk
from typing import Self

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

import patient
from patient import Patient

#messages from milestone one
MSG_NO_PATIENT = "Select a registered patient."
MSG_BAD_QUANTITY = "Line quantity must be a positive whole number."
MSG_DUPLICATE_LINE = "Medicine already added to this prescription."

def _positive_whole_number(text):
    """
    Turn from text into an int greater than 0, or raise the message above
    Text boxes always give back text, so 5 must become the number 5
    isascii + isdigit rejects "", "-3", "2.5", "abc" and "1_0" before int() sees them
    """
    text = str(text).strip()
    if not (text.isascii() and text.isdigit()) or int(text) <= 0:
        raise ValueError(MSG_BAD_QUANTITY)
    return int(text)

class CreatePrescriptionView(ttk.Frame):
    def __init__(self, parent,conn):
        super().__init__(parent, padding = 4)
        #The view never touches SQL. It asks services, which use the database
        # connection (conn) that the main window passes in
        self._service = PrescriptionService(conn)
        self._patient = PatientService(conn)
        self._branch_service = BranchService(conn)
        self._medicine_service = MedicineService(conn)

        self._lines = [] #temp UI state: {(code, quantity)]
        #A StringVar is a tkinter variable linked to a widget: what the user picks or types in the widget is read back with .get()
        self._patient_var = tk.StringVar()
        self._branch_var = tk.StringVar()
        self._prescriber_var = tk.StringVar()
        self._line_medicine_var = tk.StringVar()
        self._line_qty_var = tk.StringVar()

        self._load_options()
        self._build()
        self._set_defaults()
        self.refresh_lines()

    def _load_options(self):
        """Read patients, branches and medicines from the database."""
        # Each dictionary maps the TEXT the user sees in the dropdown to the
        # real value we need, e.g. "M001 - Paracetamol" -> "M001".
        self._patient_options = {
            str(patient): patient.patient_id
            for patient in self._patient.service.list_all()
        }
        self._branch_options = {
            f"{b.branch_id} - {b.name}": b.branch_id
            for b in self._branch_service.list_all()
        }

        self._medicine_options = {
            f"{m.code} - {m.name}": m.code
            for m in self._medicine_service.list_all()
        }

    def refresh_options(self):
        """Reload the dropdowns so new patients/medicines/branches appear.

        The main window should call this when the S4 tab is shown.
        """
        # Without this, a patient registered on S7 would only appear after
        # restarting the app, because the lists are otherwise loaded once.
        self._load_options()
        self._patient_box["values"] = list(self._patient_options)
        self._branch_box["values"] = list(self._branch_options)
        self._medicine_box["values"] = (self._medicine_options)
        #forget a choice that no longer exists
        for var, options in ((self._patient_var, self._patient_options),
                             (self._branch_var, self._branch_options),
                             (self._line_medicine_var, self._medicine_options)):
            if var.get() not in options:
                var.set("")
        self._set_defaults()

    def _build(self):
        screen_title(self, "Creeate prescription", row=0)

        details = form_section(self, "prescription_details", row = 1)
        # NOTE: labelled_combobox must return the Combobox widget, because
        # refresh_options() needs it to update the dropdown list later.

        self._patient_box = labelled_combobox(
            details, "Patient", 0, list(self._patient_options),
            variable = self._patient_var,
        )

        self._branch_box = labelled_combobox(
            details, "Branch", 1, list(self._branch_options),
            variable = self._branch_var,
        )

        labelled_entry(
            details, "Prescriber code (optional)", 2,
            variable = self._prescriber_var,
        )

        line_form = form_section(self, "Add a medicine line", row = 2)
        self._medicine_box = labelled_combobox(
            line_form, "Medicine", 0, list(self._medicine_options),
            variable = self._line_medicine_var,

        )
        labelled_entry(line_form, "Quantity", 1, variable = self._line_qty_var)
        button_bar(line_form, [
            ("Add line", self._on_add_line),
            ("remove selected line", self._on_remove_line),
        ], row = 2)

        table_frame = table_section(self, "lines on this prescription", row = 3)
        self._lines_table = data_table(table_frame, [
            ("Medicine code", "code", 160),
            ("Quantity", "qty", 110 ),
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
# The patient is NOT pre-selected: the pharmacist must choose one, so a
# prescription can't be created for the wrong person by accident.
        if not self._branch_var.get() and self._branch_options:
            self._branch_var.set(next(iter(self._branch_options)))
        if not self._line_medicine_var.get() and self._medicine_options:
            self._line_medicine_var.set(next(iter(self._medicine_options)))

    def _on_add_line(self):
        try:
            # .get() on a dictionary returns None if the key is missing,
            # instead of crashing. None means "nothing valid was chosen".
            code  = self._medicine_options.get(self._line_medicine_var.get())
            if code is None:
                raise ValueError("Select a medicine")
            quantity = _positive_whole_number(self._line_qty_var.get())
            # Instant feedback; Prescription and the database enforce this too.
            if any(existing == code for existing, _ in self._lines):
                raise ValueError(MSG_DUPLICATE_LINE)
            self._lines.append((code, quantity))
        except Exception as exc:
            # Any error is shown to the user exactly as raised (FR-19).
            show_error(str(exc))
            return
        self._line_qty_var.set("")
        self.refresh_lines()

    def _on_remove_line(self):
        selection = self._lines_table.selection()
        if not selection:
            show_error("Select a line to remove.")
            return
        # The row's position in the table is also its position in self._lines.
        index = self._lines_table.index(selection[0])
        del self._lines[index]
        self.refresh_lines()

    def _on_create(self):
        try:
            patient_id = self._patient_options.get(self._patient_var.get())
            branch_id = self._branch_options.get(self._branch_var.get())
            if patient_id is None:
                raise ValueError(MSG_NO_PATIENT)
            if branch_id is None:
                raise ValueError("Select a branch.")
            # .strip() makes a box of only spaces count as blank; "or None"
            # turns blank into None (allowed for ordinary medicines).
            prescriber = self._prescriber_var.get().strip() or None
            # The service validates the rules and saves the prescription and
            # all its lines in ONE transaction (all or nothing).
            prescription = self._service.create(
                patient_id, branch_id, list(self._lines), prescriber)
        except Exception as exc:
            show_error(str(exc))
            return
        # Only reached when the save worked; a failed save keeps the lines so
        # the user can fix the problem and try again.
        show_info(f"Prescription #{prescription.prescription_id} created.")
        self._clear_lines()

    def _clear_lines(self):
        self._lines = []
        self._line_qty_var.set("")
        clear_variables([self._prescriber_var])
        self.refresh_lines()

    def refresh_lines(self):
        # Redraw the table from self._lines, which is the single source of truth.
        populate_table(self._lines_table, [
            (code, quantity) for code, quantity in self._lines
        ])
