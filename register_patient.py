import tkinter as tk
from tkinter import ttk
from services.patient_service import PatientService #reads/writes patients in SQLite for us.
from templates.layouts import (
    from_section, make_expandable, screen_title, table_section,
)
from templates.widgets import(
    button_bar, clear_variables, data_table, labelled_entry,
    populate_table, show_error, show_info,
)

class RegisterPatientView(ttk.Frame):
    def __init__(self, parent, conn): 
        super(). __init__(parent, padding= 4)
        self._service = PatientService(conn)
        self._patient_id_var = tk.StringVar()
        self._label_var = tk.StringVar()
        self.build()
        self.refresh_table()

    def _build(self):
        screen_title(self, "Register Patient", row=0)
        form = form_section(self, "New patient", row=1)
        labelled_entry(
            form, "Label (optional)",1, variable=self._label_var)
        button_bar(form, [
            ("Register patient", self._on_register),
            ("Clear form", self._clear_form),
        ], row = 2)   

        table_frame = table_section(self, "Registered Patients" , row=2)
        self.table = data_table(table_frame, [
            ("Patient ID", "id", 150)
            ("Label". "label", 300) #300 pixels wide
        ])

        make_expandable(self, row=2)
    def _on_register(self):
        try:
            self._service.register(
                self._patient_id_var.get(), self._label_var.get())
        except Exception as exc:
            show_error(str(exc))
            return
        show_info("Patient registered.")
        clear_variable([self.patient_id_var, self._label_var])
        self.refresh_table()

    def _clear_form(self):
        clear_variable([self._patient_id_var, self._label_var]) 

    def refresh_table(self):
        populate_table(self._table, [
            (patient.patient_id, patient.label or "")
            for patient in self._service.list_all()
        ])       
           