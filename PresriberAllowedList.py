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
            raise InvalidNameError("Branch name is required") #if the value is invalid raise the error
        self._name = value.strip() #removes unnecassary spaces

    def describe(self):#describing the branch
        if self.is_main:
            branch_type = "Main"
        else:
            branch_type = "(Branch)"

        return f"{self.name} {branch_type}"

    def __str__(self):
        return self.describe()

mukono_branch = Branch(101, "Mukono", True)
kampala_branch = Branch(102, "Kampala", False)
kabale_branch = Branch(103, "Kabale",False) 

branches = [mukono_branch, kampala_branch, kabale_branch]

print("BANK BRANCHES")
print("----------------------------------------------")
for branch in branches:
    print(f"Branch ID: {branch.branch_id}")
    print(f"Branch Name: {branch.name}")
    print(f"Branch Type: {branch.describe()}")
    print("----------------------------------------------")

class PrescriberAllowList:
    def __init__(self):
        self._codes = set() #an empty set for approved prescribers Note:We have an underscore (_.code) which is for internal use
    def add(self, code): #adding and approving the prescriber code
        if not isinstance(code, str) or not code.strip():
            raise ValueError("Prescriber code is required")
            self._code.add(code.strip().upper())
     #self._codes - access our set of approved prescribers
     #.strip - remove unnecassary spaces
     #.upper - converts the letter to uppercase
     # .add() - adds the code to the set       

    def remove(self, code):#remove the prescriber incase they loose their authorization
        if not isinstance(code, str) or not code.strip():
            raise ValueError("Prescriber code is required")
        self._codes.discard(code.strip().upper())

    def is_authorised(self, code): #this method checks whether a particular prescriber is on our approved list
        if not isinstance(code, str) or not code.strip():
            return False

        return code.strip().upper() in self._codes   

        
      