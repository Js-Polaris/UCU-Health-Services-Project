"""Stock of one medicine at one branch.

Invariant (Milestone 1): quantity >= 0 at all times. It is guarded here in the
methods and again by the CHECK constraint on the stock table.

Fix reference (Milestone 2 / Step 5):
  * `receive()` was accidentally nested inside `_check_change()`, so it could
    never be called; both movement methods are now normal instance methods.
  * `remove()` was a @staticmethod but used `self`; removed that decorator.
  * The property was spelt `mdeicine_id`; it is `medicine_code` now.
  * The constructor set `_quantity` directly, bypassing the setter. It now
    assigns 0 first, then goes through `self.quantity = quantity`.
"""

from domainExceptions import ValidationError, InsufficientStockError


class StockItem:
    def __init__(self, branch_id, medicine_code, quantity):
        self._branch_id = branch_id
        self._medicine_code = str(medicine_code).strip().upper()
        self._quantity = 0          # safe starting state
        self.quantity = quantity    # validation happens in the setter

    @property
    def branch_id(self):
        return self._branch_id

    @property
    def medicine_code(self):
        return self._medicine_code

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValidationError(
                "Initial quantity must be zero or a positive whole number.")
        self._quantity = value

    @staticmethod
    def _check_movement(n):
        if isinstance(n, bool) or not isinstance(n, int) or n <= 0:
            raise ValidationError("Quantity must be a positive whole number.")

    def receive(self, n):
        """Screen 3: add stock, returning the new quantity."""
        self._check_movement(n)
        self._quantity += n
        return self._quantity

    def remove(self, n):
        """Screen 5: deduct stock, or raise with no change on insufficient stock."""
        self._check_movement(n)
        if n > self._quantity:
            raise InsufficientStockError(
                f"Insufficient stock for {self._medicine_code} "
                f"at branch {self._branch_id}.")
        self._quantity -= n
        return self._quantity

    def is_low(self, reorder_level):
        """Screen 6: at or below the reorder level."""
        return self._quantity <= reorder_level
