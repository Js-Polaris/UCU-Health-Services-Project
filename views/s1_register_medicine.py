"""Screen S1: Register Medicine.

Shows the complete View pattern:
  1. __init__(parent, conn) receives the ONE shared connection.
  2. _build() only constructs widgets, using templates/layouts + widgets.
  3. Button handlers call a service inside try/except and show str(exc)
     unchanged. No SQL, no validation rules, no commits here.
"""

import tkinter as tk
from tkinter import ttk

from services.medicine_service import MedicineService
from templates.layouts import (
    form_section, make_expandable, screen_title, table_section,
)
from templates.widgets import (
    button_bar, clear_variables, data_table, labelled_combobox,
    labelled_entry, populate_table, show_error, show_info,
)


class RegisterMedicineView(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent, padding=4)
        self._service = MedicineService(conn)

        # Form state lives in StringVars; the service does the validating.
        # NOTE: never name a field `self._name` -- Tkinter already uses
        # `_name` internally for the widget name and closing the window
        # will crash. Always suffix form vars with `_var`.
        self._code_var = tk.StringVar()
        self._name_var = tk.StringVar()
        self._price_var = tk.StringVar()
        self._level_var = tk.StringVar()
        self._category_var = tk.StringVar(value="ordinary")

        self._build()
        self.refresh_table()

    # ------------------------------------------------------------------
    # Widget construction only -- no logic here.
    # ------------------------------------------------------------------
    def _build(self):
        screen_title(self, "Register Medicine", row=0)

        form = form_section(self, "New medicine", row=1)
        labelled_entry(form, "Code (e.g. MED-001)", 0, variable=self._code_var)
        labelled_entry(form, "Name", 1, variable=self._name_var)
        labelled_entry(form, "Unit price (UGX)", 2, variable=self._price_var)
        labelled_entry(form, "Reorder level", 3, variable=self._level_var)
        labelled_combobox(
            form, "Category", 4, ("ordinary", "controlled"),
            variable=self._category_var,
        )
        button_bar(form, [
            ("Register medicine", self._on_register),
            ("Clear form", self._clear_form),
            ("Refresh list", self.refresh_table),
        ], row=5)

        table_frame = table_section(self, "Registered medicines", row=2)
        self._table = data_table(table_frame, [
            ("Code", "code", 100),
            ("Name", "name", 220),
            ("Unit price", "price", 110),
            ("Reorder level", "level", 120),
            ("Category", "category", 110),
        ])

        make_expandable(self, row=2)

    # ------------------------------------------------------------------
    # Event handlers -- call the service, show the result/error.
    # ------------------------------------------------------------------
    def _on_register(self):
        try:
            self._service.register(
                self._code_var.get(),
                self._name_var.get(),
                self._price_var.get(),
                self._level_var.get(),
                self._category_var.get(),
            )
        except Exception as exc:
            show_error(str(exc))       # exact message, never rewritten
            return
        show_info("Medicine registered.")
        self._clear_form()
        self.refresh_table()

    def _clear_form(self):
        clear_variables(
            [self._code_var, self._name_var, self._price_var, self._level_var])
        self._category_var.set("ordinary")

    def refresh_table(self):
        medicines = self._service.list_all()
        populate_table(self._table, [
            (m.code, m.name, m.unit_price, m.reorder_level, m.category)
            for m in medicines
        ])
