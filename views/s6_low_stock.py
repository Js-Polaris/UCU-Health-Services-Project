"""Screen S6: Low Stock Report (owner: Jjumba -- small first task).

This is a READ-ONLY screen: a branch dropdown and a table of medicines whose
quantity is at or below the reorder level. No forms to submit, no save
buttons, no transactions. Perfect for a first MVT task.

Services available:
  self._service.list_branches()       -> branches for the dropdown
  self._service.list_low_stock(id)    -> list of (StockItem, Medicine) tuples
"""

from tkinter import ttk

from services.low_stock_service import LowStockService
from templates.layouts import screen_title


class LowStockView(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent, padding=4)
        self._service = LowStockService(conn)
        self._build()

    def _build(self):
        screen_title(self, "Low Stock Report")
        ttk.Label(
            self,
            text="TODO (Jjumba): branch dropdown + read-only table.\n"
                 "Call LowStockService.list_low_stock(branch_id).",
        ).grid(row=1, column=0, sticky="w", padx=10, pady=10)
