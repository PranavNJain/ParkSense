"""
ParkSense - UPI Payment Pre-Authorization Handler
Simulates UPI payment pre-auth using Razorpay / custom UPI deep-link flow.
"""

import uuid
import time


class UPIHandler:
    def __init__(self, merchant_upi: str = "parksense@upi",
                 merchant_name: str = "ParkSense Parking"):
        self.merchant_upi  = merchant_upi
        self.merchant_name = merchant_name
        self._ledger: dict[str, dict] = {}  # txn_id -> record

    def pre_authorize(self, plate: str, amount: float) -> str | None:
        """
        Generate a UPI pre-authorization request.

        In production this would call Razorpay's API or generate a UPI intent
        URI displayed as a QR code at the entry gate.

        Args:
            plate  : License plate of the vehicle.
            amount : Amount to pre-authorize in INR.

        Returns:
            Transaction ID string, or None on failure.
        """
        txn_id = f"PS-{uuid.uuid4().hex[:10].upper()}"
        upi_uri = self._build_upi_uri(txn_id, amount)

        record = {
            "txn_id"    : txn_id,
            "plate"     : plate,
            "amount"    : amount,
            "status"    : "pre_authorized",
            "upi_uri"   : upi_uri,
            "created_at": time.time()
        }
        self._ledger[txn_id] = record

        print(f"[UPI] Pre-auth created for {plate} | ₹{amount:.2f} | TxnID: {txn_id}")
        return txn_id

    def capture(self, txn_id: str, actual_amount: float) -> bool:
        """
        Capture (finalize) the payment after vehicle exits.
        Charges actual_amount (based on duration), releases any excess hold.
        """
        if txn_id not in self._ledger:
            print(f"[UPI] TxnID {txn_id} not found.")
            return False

        record = self._ledger[txn_id]
        record["status"]        = "captured"
        record["actual_amount"] = round(actual_amount, 2)
        record["captured_at"]   = time.time()

        print(f"[UPI] Payment captured | TxnID: {txn_id} | ₹{actual_amount:.2f}")
        return True

    def refund(self, txn_id: str) -> bool:
        """Release pre-authorization if vehicle exits without charge."""
        if txn_id not in self._ledger:
            return False
        self._ledger[txn_id]["status"] = "refunded"
        print(f"[UPI] Pre-auth released | TxnID: {txn_id}")
        return True

    def _build_upi_uri(self, txn_id: str, amount: float) -> str:
        """
        Construct a standard UPI deep-link URI.
        This URI can be encoded as a QR code for display at the entry gate.
        """
        return (
            f"upi://pay?pa={self.merchant_upi}"
            f"&pn={self.merchant_name.replace(' ', '%20')}"
            f"&am={amount:.2f}"
            f"&tr={txn_id}"
            f"&tn=ParkSense%20Entry%20Pre-Auth"
            f"&cu=INR"
        )

    def get_status(self, txn_id: str) -> str:
        """Return the current status of a transaction."""
        record = self._ledger.get(txn_id)
        return record["status"] if record else "not_found"
