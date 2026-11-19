class PharmarcyError(Exception): #This is the base class for all exceptions we are going to work with.
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class DispenseError(PharmarcyError):
    pass
class ValidationError(PharmarcyError):
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
class InvalidStatusTransitionError(PharmarcyError):
    pass
        

