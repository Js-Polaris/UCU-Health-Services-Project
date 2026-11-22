"""Service for Screen S3.

Available methods for the View:
  receive(branch_id, medicine_code, quantity) -> add stock, creating the
      (branch, medicine) record first if it does not exist yet.
  list_for_branch(branch_id)                  -> stock table for one branch.
  list_all()                                 -> every stock record.
"""

from StockItem import StockItem
from repositories.stock_repository import StockRepository


class StockService:
    def __init__(self, conn):
        self._conn = conn
        self._stock = StockRepository(conn)

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

    def list_for_branch(self, branch_id):
        return self._stock.list_for_branch(int(branch_id))

    def list_all(self):
        return self._stock.list_all()
