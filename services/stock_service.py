"""Service for Screens S3 and S6.

Available methods for the Views:
  receive(branch_id, medicine_code, quantity) -> add stock, creating the
      (branch, medicine) record first if it does not exist yet.
  list_for_branch(branch_id)                  -> stock table for one branch.
  list_all()                                  -> every stock record.
  list_low_stock(branch_id)                   -> [(StockItem, Medicine), ...]
      rows at or below their reorder level for one branch (read-only).
"""

from StockItem import StockItem
from repositories.medicine_repository import MedicineRepository
from repositories.stock_repository import StockRepository


class StockService:
    def __init__(self, conn):
        self._conn = conn
        self._stock = StockRepository(conn)
        self._medicines = MedicineRepository(conn)

    def receive(self, branch_id, medicine_code, quantity):
        """Add stock to an existing record, or create one at quantity 0."""
        try:
            item = self._stock.get(int(branch_id), medicine_code)
            if item is None:
                item = StockItem(int(branch_id), medicine_code, 0)
                self._stock.add(item)
            item.receive(quantity)   # domain validates the amount
            self._stock.save(item)
            self._conn.commit()
            return item
        except Exception:
            self._conn.rollback()
            raise

    def list_low_stock(self, branch_id):
        """Return (stock item, medicine) pairs at or below reorder level.

        The View is read-only, so there is no commit/rollback here. The low
        stock decision belongs to StockItem.is_low(), not to the View.
        """
        low_rows = []
        for item in self._stock.list_for_branch(int(branch_id)):
            medicine = self._medicines.get(item.medicine_code)
            if medicine is None:
                continue
            if item.is_low(medicine.reorder_level):
                low_rows.append((item, medicine))
        return low_rows

    def list_for_branch(self, branch_id):
        return self._stock.list_for_branch(int(branch_id))

    def list_all(self):
        return self._stock.list_all()
