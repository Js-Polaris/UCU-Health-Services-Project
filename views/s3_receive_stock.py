"""Screen S3: Receive Stock (owner: Abi).

Build a form with a branch dropdown, a medicine dropdown and a quantity field,
then call StockService.receive(branch_id, medicine_code, quantity). Show the
stock for the selected branch in a table. Follow s1_register_medicine.py.

Services available:
  BranchService(conn).list_all()        -> branches for the dropdown
  MedicineService(conn).list_all()      -> medicines for the dropdown
  self._service.receive(...)            -> returns the updated StockItem
  self._service.list_for_branch(id)     -> stock rows for one branch
"""

from tkinter import ttk

from services.stock_service import StockService
from templates.layouts import screen_title


class ReceiveStockView(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent, padding=4)
        self._service = StockService(conn)
        self._build()

    def _build(self):
        screen_title(self, "Receive Stock")
        ttk.Label(
            self,
            text="TODO (Abi): branch + medicine dropdowns and a quantity field.\n"
                 "Call StockService.receive(branch_id, medicine_code, quantity).",
        ).grid(row=1, column=0, sticky="w", padx=10, pady=10)
