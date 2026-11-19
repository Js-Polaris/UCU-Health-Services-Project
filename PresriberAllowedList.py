class PrescriberAllowList:
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
