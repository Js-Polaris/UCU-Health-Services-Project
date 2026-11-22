"""Application service for dispensing a prescription.

Fix reference (Milestone 2 / Step 7):
  * The previous version had dispense(), _dispense() and _build_allow_list()
    INDENTED INSIDE __init__, so the class had no usable methods at all.
  * It used self._conn but only set self.conn; self._stock was never created;
    self._medicine did not match self._medicines.
  * The prescriber check must use PrescriberRepository, not PrescriberAllowList
    with a connection passed to its constructor.
  * InvalidTransitionError does not exist; the exception is
    InvalidStatusTransitionError.

This is the transaction boundary. Every repository is built from the SAME
connection, so all writes succeed together or none of them do. Repositories
never commit or roll back; this class does, once, at the end.

NOTE: this module imports `prescription`, `repositories.medicine_repository`
and `repositories.prescription_repository`, which are on Samuel's and Abi's
branches until they are merged into main. Run `python -m db.seed` first; it
does not need those files.
"""

from domainExceptions import (
    InsufficientStockError,
    InvalidStatusTransitionError,
    UnauthorizedPrescriberError,
    ValidationError,
)
from PrescriberAllowList import PrescriberAllowList
from prescription import PrescriptionStatus
from repositories.medicine_repository import MedicineRepository
from repositories.prescriber_repository import PrescriberRepository
from repositories.prescription_repository import PrescriptionRepository
from repositories.stock_repository import StockRepository


class DispensingService:
    def __init__(self, conn):
        self._conn = conn
        self._medicines = MedicineRepository(conn)
        self._stock = StockRepository(conn)
        self._prescriptions = PrescriptionRepository(conn)
        self._prescribers = PrescriberRepository(conn)

    def dispense(self, prescription_id):
        """Dispense one prescription atomically; return the updated object.

        On any failure the whole transaction is rolled back: no stock is
        deducted and the prescription stays pending.
        """
        try:
            prescription = self._dispense(prescription_id)
        except Exception:
            self._conn.rollback()
            raise
        self._conn.commit()
        return prescription

    def _dispense(self, prescription_id):
        prescription = self._prescriptions.get(prescription_id)
        if prescription is None:
            raise ValidationError("Prescription not found.")

        if prescription.status is not PrescriptionStatus.PENDING:
            raise InvalidStatusTransitionError(
                "Only a pending prescription can be dispensed.")

        allow_list = self._build_allow_list()

        # Validation pass: read and check everything BEFORE writing anything.
        deductions = []
        for line in prescription.lines:
            medicine = self._medicines.get(line.medicine_code)
            if medicine is None:
                raise ValidationError(f"Unknown medicine: {line.medicine_code}")

            if not medicine.dispensed_by(prescription.prescriber_code, allow_list):
                raise UnauthorizedPrescriberError(
                    f"{medicine.code} needs an authorised prescriber.")

            item = self._stock.get(prescription.branch_id, line.medicine_code)
            if item is None:
                raise InsufficientStockError(
                    f"No stock record for {line.medicine_code} "
                    f"at branch {prescription.branch_id}.")
            if item.quantity < line.quantity:
                raise InsufficientStockError(
                    f"Insufficient stock for {line.medicine_code} "
                    f"at branch {prescription.branch_id}.")

            deductions.append((item, line.quantity))

        # Apply pass: every check passed, so deduct and close the prescription.
        for item, quantity in deductions:
            item.remove(quantity)
            self._stock.save(item)

        prescription.mark_dispensed()
        self._prescriptions.save_status(prescription)
        return prescription

    def cancel(self, prescription_id):
        """Cancel a pending prescription (Screen S5).

        Uses the same transaction boundary as dispense(): one commit on
        success, one rollback on any failure. Samuel's S5 View calls this.
        """
        try:
            prescription = self._prescriptions.get(prescription_id)
            if prescription is None:
                raise ValidationError("Prescription not found.")
            prescription.cancel()
            self._prescriptions.save_status(prescription)
        except Exception:
            self._conn.rollback()
            raise
        self._conn.commit()
        return prescription

    def _build_allow_list(self):
        """Load the authorised prescriber codes from the database."""
        allow_list = PrescriberAllowList()
        for code in self._prescribers.list_all():
            allow_list.add(code)
        return allow_list
