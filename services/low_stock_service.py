"""Service for Screen S6: Low Stock Report (owner: Jjumba).

Available methods for the View:
  list_low_stock(branch_id) -> rows at or below reorder level for that branch
  list_branches()           -> branches for the branch selector
"""

from repositories.branch_repository import BranchRepository
from repositories.stock_repository import StockRepository
from repositories.medicine_repository import MedicineRepository


class LowStockService:
    def __init__(self, conn):
        self._conn = conn
        self._branches = BranchRepository(conn)
        self._stock = StockRepository(conn)
        self._medicines = MedicineRepository(conn)

    def list_branches(self):
        return self._branches.list_all()

    def list_low_stock(self, branch_id):
        """Stock rows at or below reorder level for one branch.

        The View is read-only, so no commit/rollback is needed. The service
        joins the stock row with the medicine so the View can display name and
        reorder level without knowing SQL.
        """
        branch_id = int(branch_id)
        low_rows = []
        for item in self._stock.list_for_branch(branch_id):
            medicine = self._medicines.get(item.medicine_code)
            if medicine is None:
                continue
            if item.is_low(medicine.reorder_level):
                low_rows.append((item, medicine))
        return low_rows
