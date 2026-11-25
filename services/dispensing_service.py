"""DispensingService exposed from the services package.

The implementation lives in db/dispensing_service.py because it was written
in Milestone 2. This re-export means every View imports services from one
consistent place: `from services.dispensing_service import DispensingService`.

Available methods for Screen S5 (owner: Samuel):
  dispense(prescription_id) -> dispense a pending prescription atomically
  cancel(prescription_id)   -> cancel a pending prescription atomically
"""

from db.dispensing_service import DispensingService

__all__ = ["DispensingService"]
