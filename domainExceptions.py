class PharmarcyError(Exception): #This is the base class for all exceptions we are going to work with.
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class DispenseError(PharmarcyError):
    def __init__(self, message):
        self.message = message
        super(). __init__(self.message)

class ValidationError(PharmarcyError):
    def __init__(self, message):
        self.message = message
        super(). __init__(self.message)
class InvalidPriceError(ValidationError):
    def __init__(self, message):
        self.message = message
        super(). __init__(self.message)
class InvalidReorderError(ValidationError):
    def __init__(self, message):
        self.message = message
        super(). __init__(self.message)
class DuplicatePatientError(ValidationError):
    def __init__(self, message):
        self.message = message
        super(). __init__(self.message)
class UnknownPatientError(ValidationError):
    def __init__(self, message):
        self.message = message
        super(). __init__(self.message)
class UnauthorizedPrescriberError(DispenseError):
    def __init__(self, message):
        self.message = message
        super(). __init__(self.message)
class InsufficientStockError(DispenseError):
    def __init__(self, message):
        self.message = message
        super(). __init__(self.message)
class InvalidStatusTransitionError(PharmarcyError):
    def __init__(self, message):
        self.message = message
        super(). __init__(self.message)

        

