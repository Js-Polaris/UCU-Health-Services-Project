"""Screen S3: Receive Stock (owner: Abi).

Drop-in replacement for views/s3_receive_stock.py.

Pick a branch, pick a medicine, enter a quantity, then click Receive stock.
If the (branch, medicine) pair is new, StockService creates the record first.

MVT rules followed:
  * No SQL here -- StockService owns the database work.
  * No business rules here -- StockItem validates the quantity.
  * Errors are shown exactly as received: show_error(str(exc)).
"""

import tkinter as tk
from tkinter import ttk

from services.branch_service import BranchService
from services.medicine_service import MedicineService
from services.stock_service import StockService
from templates.layouts import (
    form_section, make_expandable, screen_title, table_section,
)
from templates.widgets import (
    button_bar, data_table, labelled_combobox, labelled_entry,
    populate_table, show_error, show_info,
)


def _whole_number(text, field_name):
    """Turn form text into an int so the domain sees a real number."""
    try:
        return int(str(text).strip())
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a whole number.") from None


class ReceiveStockView(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent, padding=4)
        self._service = StockService(conn)
        branches = BranchService(conn)
        medicines = MedicineService(conn)

        # Display text -> real id/code. Avoids parsing strings later.
        self._branch_options = {
            f"{b.branch_id} - {b.name}": b.branch_id
            for b in branches.list_all()
        }
        self._medicine_options = {
            f"{m.code} - {m.name}": m.code
            for m in medicines.list_all()
        }

        self._branch_var = tk.StringVar()
        self._medicine_var = tk.StringVar()
        self._quantity_var = tk.StringVar()

        self._build()
        # Refresh the table whenever a different branch is chosen.
        self._branch_var.trace_add("write", self._on_branch_changed)
        if self._branch_options:
            self._branch_var.set(next(iter(self._branch_options)))
        if self._medicine_options:
            self._medicine_var.set(next(iter(self._medicine_options)))
        self.refresh_table()

    def _build(self):
        screen_title(self, "Receive Stock", row=0)

        form = form_section(self, "New stock receipt", row=1)
        labelled_combobox(
            form, "Branch", 0, list(self._branch_options),
            variable=self._branch_var,
        )
        labelled_combobox(
            form, "Medicine", 1, list(self._medicine_options),
            variable=self._medicine_var,
        )
        labelled_entry(form, "Quantity to add", 2, variable=self._quantity_var)
        button_bar(form, [
            ("Receive stock", self._on_receive),
            ("Clear quantity", self._clear_quantity),
        ], row=3)

        table_frame = table_section(self, "Stock at the selected branch", row=2)
        self._table = data_table(table_frame, [
            ("Medicine code", "code", 150),
            ("Quantity", "qty", 120),
        ])

        make_expandable(self, row=2)

    def _on_branch_changed(self, *_args):
        self.refresh_table()

    def _on_receive(self):
        try:
            branch_id = self._branch_options.get(self._branch_var.get())
            medicine_code = self._medicine_options.get(self._medicine_var.get())
            if branch_id is None:
                raise ValueError("Select a branch.")
            if medicine_code is None:
                raise ValueError("Select a medicine.")
            quantity = _whole_number(self._quantity_var.get(), "Quantity")
            self._service.receive(branch_id, medicine_code, quantity)
        except Exception as exc:
            show_error(str(exc))
            return
        show_info("Stock received.")
        self._clear_quantity()
        self.refresh_table()

    def _clear_quantity(self):
        self._quantity_var.set("")

    def refresh_table(self):
        branch_id = self._branch_options.get(self._branch_var.get())
        if branch_id is None:
            populate_table(self._table, [])
            return
        items = self._service.list_for_branch(branch_id)
        populate_table(self._table, [
            (item.medicine_code, item.quantity) for item in items
        ])
