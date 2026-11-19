from abc import ABC, abstractmethod
from domainExceptions import ValidationError, InvalidPriceError, InvalidReorderLevelError


class Medicine(ABC):
    def __init__(self, code, name, unit_price, reorder_level):
        #checks the code the user entered, then stores the cleaned result inside the object
        self._code = self._validate_code(code)
        self.name = name 
        self.unit_price = unit_price
        self.reorder_level = reorder_level

    def _validate_code(code):
        #must be text and not empty or only spaces
        if not isinstance(code, str) or not code.strip():
            raise ValidationError("Medicine code is required")
        #.strip() removes spaces, and upper() ensures things are in uppercase

    @staticmethod
    def _to_whole_number(value):
        #Return value as an int; raise ValueError if it isn't a whole number
        if isinstance(value, bool):
            raise ValueError
        if isinstance(value, float):
            if not value.is_integer():
                raise ValueError
            return int(value)
        return int(value)

    @property
    def code(self):
        return self._code

    @property
    def name(self):
        return self._name

    #for the setter it runs everytime a value (e.g name, unit_price) is set 
    @name.setter
    def name(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValidationError("Medicine name is required")
        self._name = value.strip()

    @property
    def unit_price(self):
        return self._unit_price

    @unit_price.setter
    def unit_price(self, value):
        try:
            #float(value) converts the input to a number 
            price = self._to_whole_number(value)
        except (TypeError, ValueError):
            raise InvalidPriceError("Unit price must be a number")
        if price <= 0 :
            raise InvalidPriceError("Unit price must be greater than 0")
        #its only the after checks are passed that the value is stored
        self._unit_price = price

    @property
    def reorder_level(self):
       return self._reorder_level

    @reorder_level.setter
    def reorder_level(self, value):
        try:
            #int(value) is used so that the coverted value is a whole number
            level = self._to_whole_number(value)
        except (TypeError, ValueError):
            raise InvalidReorderLevelError("Reorder level must be a whole number")
        if level < 0:
            raise InvalidReorderLevelError("Reorder level cannot be negative")
        self._reorder_level = level

    #@abstractmethod means the subclasses must write their own version of this
    @abstractmethod
    def category(self): 
        """ ordinary or controlled""" 

    @abstractmethod
    def requires_authoristion(self):
        """ True if a prescriber check is needed"""

    @abstractmethod
    def dispensed_by(self, prescriber_code, allow_list):
        """Return True or False. The service raises the error"""

    #describe gives a readable line 
    def describe(self):  
        return f"{self.code} - {self.name} (UGX {self.unit_price})"

    #__repr__ gives a string for debugging and !r shows the value with quotes, so the spaces can be seen clearly
    def __repr__(self): 
        return (f"{type(self).__name__}(code={self.code!r}, name={self.name!r}, "
                f"unit_price={self.unit_price}, reorder_level={self.reorder_level})")

class OrdinaryMedicine(Medicine):
    @property
    def category(self):
        return "ordinary"

    def requires_authorisation(self):
        return False

    def dispensed_by(self, prescriber_code, allow_list):
        return True

class ControlledMedicine(Medicine):

    @property
    def category(self):
        return "controlled"

    def requires_authorisation(self):
        return True
    
    def dispensed_by(self, prescriber_code, allow_list):
        return allow_list.isauthorised(prescriber_code)
