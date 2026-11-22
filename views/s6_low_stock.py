"""Screen S6: Low Stock Report (owner: Jjumba -- small first task).

Drop-in replacement for views/s6_low_stock.py.

READ-ONLY screen: pick a branch, see medicines whose quantity is at or below
their reorder level. No forms to submit, no save buttons, no transactions.

MVT rules followed:
  * No SQL here -- LowStockService gathers the data.
  * No business rules here -- StockItem.is_low() decides.
  * Errors are shown exactly as received: show_error(str(exc)).
"""

import tkinter as tk
from tkinter import ttk

from services.stock_service import LowStockService
from templates.layouts import (
    form_section, make_expandable, screen_title, table_section,
)
from templates.widgets import (
    button_bar, data_table, labelled_combobox, populate_table, show_error,
)


class LowStockView(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent, padding=4)
        self._service = LowStockService(conn)
        self._branch_options = {
            f"{b.branch_id} - {b.name}": b.branch_id
            for b in self._service.list_branches()
        }
        self._branch_var = tk.StringVar()

        self._build()
        # Refresh the report whenever a different branch is chosen.
        self._branch_var.trace_add("write", self._on_branch_changed)
        if self._branch_options:
            self._branch_var.set(next(iter(self._branch_options)))
        else:
            self.refresh_table()

    def _build(self):
        screen_title(self, "Low Stock Report", row=0)

        form = form_section(self, "Filter", row=1)
        labelled_combobox(
            form, "Branch", 0, list(self._branch_options),
            variable=self._branch_var,
        )
        button_bar(form, [("Refresh", self.refresh_table)], row=1)

        table_frame = table_section(
            self, "Medicines at or below reorder level", row=2)
        self._table = data_table(table_frame, [
            ("Medicine code", "code", 140),
            ("Name", "name", 230),
            ("In stock", "qty", 100),
            ("Reorder level", "level", 130),
        ])

        make_expandable(self, row=2)

    def _on_branch_changed(self, *_args):
        self.refresh_table()

    def refresh_table(self):
        branch_id = self._branch_options.get(self._branch_var.get())
        if branch_id is None:
            populate_table(self._table, [])
            return
        try:
            low_rows = self._service.list_low_stock(branch_id)
        except Exception as exc:
            show_error(str(exc))
            return
        populate_table(self._table, [
            (medicine.code, medicine.name, item.quantity,
             medicine.reorder_level)
            for item, medicine in low_rows
        ])
