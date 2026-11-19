from domainExceptions import ValidationError, InsufficientStockError

class StockItem:
    def __init__(self, branch_id: str, medicine_code: str, quantity: int):
        self._branch_id = branch_id
        self._medicine_code = medicine_code
        self._quantity = 0 #creating a safe starting point for the quantities
        self._quantity = quantity
 #where the methods are guarded for the invariants
    @property
    def branch_id(self)-> str:
        return self._branch_id
    @property 
    def mdeicine_id(self)->int:
        return self._medicine_code
    @property
    def quantity(self)-> int:
        return self._quantity
    @quantity.setter #where the invariants are checked and enfored 
    def quantity(self, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value <0:
            raise ValidationError("The starting Stock must be zero and above")
        self._quantity = value
    ##Adding items to stock 
    @staticmethod #With stck movement being at zero is meaningless so the new quantity will be returned as the new quantity
    def _check_change(n: int) -> int: #where n is the curent quantity
        if isinstance(n, bool) or not isinstance(n, int) or n<= 0:
            raise ValidationError("The quantity must be a positive whole number.")
        def receive(self, n: int) -> int:
            self._check_change(n)
            self._quantity += n
            return self._quantity
    ##removing items from stock
    @staticmethod
    def remove(self, n:int)-> int:
        self._check_change(n)
        if n> self._quantity:
            raise InsufficientStockError(f"Insufficient stock of {self._medicine_code} at the {self._branch_id} branch./n Current stock: {self._quantity}units, requested: {n} units")
        ##subtraction happens after the check. This is what our milestone one talked about. ALL OR NOTHING
        self._quantity -=n
        return self._quantity
    