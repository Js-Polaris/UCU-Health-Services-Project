"""Screen S2: Manage Branches (owner: Brenda).

Drop-in replacement for views/s2_manage_branches.py.

MVT rules followed:
  * No SQL here -- BranchService owns the database work.
  * No business rules here -- Branch validates the name.
  * Errors are shown exactly as received: show_error(str(exc)).
  * NEVER name a StringVar `self._name` (Tkinter uses `_name` internally).
"""

import tkinter as tk
from tkinter import ttk

from services.branch_service import BranchService
from templates.layouts import (
    form_section, make_expandable, screen_title, table_section,
)
from templates.widgets import (
    button_bar, clear_variables, data_table, labelled_entry,
    populate_table, show_error, show_info,
)


class ManageBranchesView(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent, padding=4)
        self._service = BranchService(conn)
        self._name_var = tk.StringVar()   # suffix _var, never self._name
        self._build()
        self.refresh_table()

    def _build(self):
        screen_title(self, "Manage Branches", row=0)

        form = form_section(self, "New branch", row=1)
        labelled_entry(form, "Branch name", 0, variable=self._name_var)
        button_bar(form, [
            ("Add branch", self._on_add),
            ("Clear form", self._clear_form),
            ("Refresh list", self.refresh_table),
        ], row=1)

        table_frame = table_section(self, "Branches", row=2)
        self._table = data_table(table_frame, [
            ("ID", "id", 80),
            ("Name", "name", 260),
        ])

        make_expandable(self, row=2)

    def _on_add(self):
        try:
            self._service.add(self._name_var.get())
        except Exception as exc:
            show_error(str(exc))
            return
        show_info("Branch added.")
        clear_variables([self._name_var])
        self.refresh_table()

    def _clear_form(self):
        clear_variables([self._name_var])

    def refresh_table(self):
        populate_table(self._table, [
            (branch.branch_id, branch.name)
            for branch in self._service.list_all()
        ])
