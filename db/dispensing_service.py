##This class is the one that is responsible for doing all the commist and rollback once at the end.
##This is so because every repo is built from the same connection so all writes succeed together or none at all

from domainExceptions import(
    InsufficientStockError,
    InvalidStatusTransitionError,
    UnauthorizedPrescriberError,
    ValidationError,
    InvalidTransitionError,
)
from PrescriberAllowList import PrescriberAllowList
from prescription import PrescriptionStatus
from prescription_repository import MedicineRepository
from prescriber_repository import PrescriberRepository
from prescription_repository import PrescriptionRepository
from repositories.stock_repository import StockRepository

class DispensingService:
    def __init__(self, conn):
        self.conn = conn
        self._medicines = MedicineRepository(conn)
        self._prescriptions = PrescriptionRepository(conn)
        self._prescribers = PrescriberAllowList(conn)

        def dispense(self, prescription_id):
            ##Dispensing only one prescription and retuening one object. In case of a failure then the whole system is rolled bacjka nd no stiock is dedeucted
            try:
                prescription = self._dispense(prescription_id)
            except Exception:
                self._conn.rollback()
                raise 
            self._conn.commit()
            return prescription
        def _dispense(self, presrciption_id):
            prescription = self._prescriptions.get(prescription_id)
            if prescription is None:
                raise ValidationError("Prescription Not Found")
            if prescription.status is not PrescriptionStatus.PENDING:
                raise InvalidStatusTransitionError( 
                    "Only a pending prescription can be dispensed"
                )
            allow_list = self._build_allow_list()
            deductions = []
            for line in prescription.lines:
                medicine = self._medicine. get(line.medicine_code)
                if medicine is None:
                    raise ValidationError(f"Unkown medicine {line.medicine_code}")
                if not medicine.dispensed_by(prescription.prescriber_code, allow_list):
                    raise UnauthorizedPrescriberError(f" This medicine {medicine.code} can only be dipsensed by authorised prescriber")
                item = self._stock.get(prescription.branch_id, line.medicine_code)
                if item is None:
                    raise InsufficientStockError(f" No Stock record for {line.medicine_code} at the {prescription.branch_id}.")
                deductions.append((item, line.quantity))

                #applying the pass. Every check passed so decut and close the prescriptions
                for item, quantity in deductions:
                    item.remove(quantity)
                    self._stock.save(item)
                prescription.mark_dispensed()
                self._prescriptions.save_status(prescription)
                return prescription
            def _build_allow_list(self):
                #getting the codes for the authorised prescribers form the db
                allow_list = PrescriberAllowList()
                for code in self._prescribers.list_all():
                    allow_list.add(code)
                return allow_list
