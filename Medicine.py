"""Medicine domain classes (from Abi's branch, with two fixes).

Fix reference:
  * `InvalidReorderLevelError` -> `InvalidReorderError` (both names now exist,
    but the short one is the canonical class in domainExceptions.py).
  * `allow_list.isauthorised(...)` -> `allow_list.is_authorised(...)` -- the
    misspelled method did not exist, so every controlled-medicine dispense
    would crash with AttributeError.
"""

from abc import ABC, abstractmethod

from domainExceptions import (
    ValidationError,
    InvalidPriceError,
    InvalidReorderError,
)


class Medicine(ABC):
    def __init__(self, code, name, unit_price, reorder_level):
        # Checks run before storing, so an invalid Medicine cannot exist.
        self._code = self._validate_code(code)
        self.name = name
        self.unit_price = unit_price
        self.reorder_level = reorder_level

    @staticmethod
    def _validate_code(code):
        if not isinstance(code, str) or not code.strip():
            raise ValidationError("Medicine code is required")
        return code.strip().upper()

    @staticmethod
    def _to_whole_number(value):
        """Return value as an int; raise ValueError if it isn't whole."""
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
            price = self._to_whole_number(value)
        except (TypeError, ValueError):
            raise InvalidPriceError("Unit price must be a number")
        if price <= 0:
            raise InvalidPriceError("Unit price must be greater than 0")
        self._unit_price = price

    @property
    def reorder_level(self):
        return self._reorder_level

    @reorder_level.setter
    def reorder_level(self, value):
        try:
            level = self._to_whole_number(value)
        except (TypeError, ValueError):
            raise InvalidReorderError("Reorder level must be a whole number")
        if level < 0:
            raise InvalidReorderError("Reorder level cannot be negative")
        self._reorder_level = level

    @property
    @abstractmethod
    def category(self):
        """ordinary or controlled"""

    @abstractmethod
    def requires_authorisation(self):
        """True if a prescriber check is needed"""

    @abstractmethod
    def dispensed_by(self, prescriber_code, allow_list):
        """Return True or False. The service raises the error."""

    def describe(self):
        return f"{self.code} - {self.name} (UGX {self.unit_price})"

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
        # FIXED: was isauthorised() (typo) -- PrescriberAllowList defines
        # is_authorised(). The service relies on this call for S5.
        return allow_list.is_authorised(prescriber_code)
