class PharmacyError(Exception): #This is the base class for all exceptions we are going to work with.
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class DispenseError(PharmacyError):
    pass
class ValidationError(PharmacyError):
    pass
class InvalidPriceError(ValidationError):
    pass
class InvalidReorderError(ValidationError):
    pass
class DuplicatePatientError(ValidationError):
    pass
class UnknownPatientError(ValidationError):
    pass
class UnauthorizedPrescriberError(DispenseError):
    pass
class InsufficientStockError(DispenseError):
    pass
class InvalidStatusTransitionError(DispenseError):
    pass
class DuplicatePatientIdError(ValidationError):
    pass
class InvalidPatientIdError(ValidationError):
    pass 

class DuplicateCodeError(ValidationError):
    pass

class DuplicateBranchError(ValidationError):
    pass

