"""Branch domain class and the simulated prescriber allow-list.

Fix reference (Milestone 2 / Step 7):
  * The file used to be named `PresriberAllowedList.py` (typo), but every
    import expects `PrescriberAllowList.py`. It has now been renamed.
  * `ValidationError` was used but never imported, so add()/remove() crashed.
  * Branch used to live in a separate `Branch_class.py`; it is consolidated
    here so there is only one definition of the class.
"""

from domainExceptions import InvalidNameError, ValidationError


class Branch:
    def __init__(self, branch_id, name, is_main=False):
        self._branch_id = branch_id
        self.name = name
        self.is_main = bool(is_main)

    @property
    def branch_id(self):
        return self._branch_id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str) or not value.strip():
            raise InvalidNameError("Branch name is required")
        self._name = value.strip()

    def describe(self):
        branch_type = "Main" if self.is_main else "(Branch)"
        return f"{self.name} {branch_type}"

    def __str__(self):
        return self.describe()


# Fictional seed values -- the seed script puts these in the branch table.
mukono_branch = Branch(101, "Mukono", True)
kampala_branch = Branch(102, "Kampala", False)
kabale_branch = Branch(103, "Kabale", False)

branches = [mukono_branch, kampala_branch, kabale_branch]


class PrescriberAllowList:
    """The authorised doctor codes used for controlled medicines."""

    def __init__(self):
        self._codes = set()

    def add(self, code):
        if not isinstance(code, str) or not code.strip():
            raise ValidationError("Prescriber code is required")
        self._codes.add(code.strip().upper())

    def remove(self, code):
        if not isinstance(code, str) or not code.strip():
            raise ValidationError("Prescriber code is required")
        self._codes.discard(code.strip().upper())

    def is_authorised(self, code):
        if not isinstance(code, str) or not code.strip():
            return False
        return code.strip().upper() in self._codes
