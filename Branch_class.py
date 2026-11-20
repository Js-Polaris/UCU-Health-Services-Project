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

    @name.setter #this setter controls how a branch name is assigned or changed
    def name(self, value):
        if not isinstance(value, str) or not value.strip(): #check whether the value is a string or empty
            raise InvalidNameError("Branch name is required")#if the value is invalid raise the error
        self._name = value.strip()#removes unnecassary spaces

    def describe(self):#describing the branch
        if self.is_main:
            branch_type = "Main"
        else:
            branch_type = "(Branch)"

        return f"{self.name} {branch_type}"

    def __str__(self):
        return self.describe()


# Fictional seed values. The seed script (Step 6) will put these in the DB.
mukono_branch = Branch(101, "Mukono", True)
kampala_branch = Branch(102, "Kampala", False)
kabale_branch = Branch(103, "Kabale", False)

branches = [mukono_branch, kampala_branch, kabale_branch]