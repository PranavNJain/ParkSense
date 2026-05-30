"""
ParkSense - Firebase Realtime Database Handler
Manages slot occupancy records and transaction logs.
"""

import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime


class FirebaseHandler:
    def __init__(self, cred_path: str = "config/serviceAccountKey.json",
                 db_url: str = "https://parksense-default-rtdb.firebaseio.com/"):
        """
        Initialize Firebase Admin SDK.

        Args:
            cred_path : Path to the Firebase service account JSON key.
            db_url    : Realtime Database URL from the Firebase console.
        """
        try:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {"databaseURL": db_url})
            self.db_ref = db.reference("/parking")
            print("[Firebase] Connected to Realtime Database.")
        except Exception as e:
            print(f"[Firebase] Init failed — running in offline mode. Error: {e}")
            self.db_ref = None

    def log_entry(self, slot_id: int, plate: str, timestamp: float) -> None:
        """
        Record a vehicle entry event.

        Schema:
            /parking/slots/{slot_id}/
                plate      : str
                entry_time : ISO string
                status     : "occupied"
        """
        if self.db_ref is None:
            return
        entry_time = datetime.fromtimestamp(timestamp).isoformat()
        self.db_ref.child(f"slots/{slot_id}").set({
            "plate"      : plate,
            "entry_time" : entry_time,
            "status"     : "occupied",
            "txn_id"     : None
        })
        print(f"[Firebase] Slot {slot_id} entry logged — Plate: {plate}")

    def log_exit(self, slot_id: int, timestamp: float, amount_charged: float) -> None:
        """
        Record a vehicle exit and mark slot as free.
        """
        if self.db_ref is None:
            return
        exit_time = datetime.fromtimestamp(timestamp).isoformat()
        self.db_ref.child(f"slots/{slot_id}").update({
            "exit_time"     : exit_time,
            "status"        : "empty",
            "amount_charged": round(amount_charged, 2)
        })
        print(f"[Firebase] Slot {slot_id} exit logged — Charged: ₹{amount_charged:.2f}")

    def update_txn(self, slot_id: int, txn_id: str) -> None:
        """Attach a UPI transaction ID to a slot record."""
        if self.db_ref is None:
            return
        self.db_ref.child(f"slots/{slot_id}").update({"txn_id": txn_id})
        print(f"[Firebase] Slot {slot_id} TxnID updated: {txn_id}")

    def get_slot_status(self, slot_id: int) -> dict | None:
        """Fetch current data for a slot."""
        if self.db_ref is None:
            return None
        return self.db_ref.child(f"slots/{slot_id}").get()

    def get_all_slots(self) -> dict:
        """Return the entire slots snapshot."""
        if self.db_ref is None:
            return {}
        return self.db_ref.child("slots").get() or {}
