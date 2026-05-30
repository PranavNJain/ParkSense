"""
ParkSense - Smart Parking Management System
Main entry point: runs YOLOv8 slot detection + ANPR pipeline
"""

import cv2
import time
import argparse
from slot_detector import ParkingSlotDetector
from anpr import ANPRProcessor
from firebase_handler import FirebaseHandler
from upi_handler import UPIHandler

def main(args):
    cap = cv2.VideoCapture(args.source)
    if not cap.isOpened():
        print("[ERROR] Cannot open video source.")
        return

    detector   = ParkingSlotDetector(model_path=args.model)
    anpr       = ANPRProcessor()
    firebase   = FirebaseHandler()
    upi        = UPIHandler()

    print("[INFO] ParkSense started. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # --- Step 1: Detect parking slots ---
        slots = detector.detect(frame)

        for slot in slots:
            slot_id   = slot["id"]
            status    = slot["status"]        # "empty" | "occupied"
            bbox      = slot["bbox"]          # (x1, y1, x2, y2)

            color = (0, 255, 0) if status == "empty" else (0, 0, 255)
            x1, y1, x2, y2 = bbox
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"S{slot_id}:{status[:3].upper()}",
                        (x1, y1 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

            # --- Step 2: Run ANPR on newly occupied slots ---
            if status == "occupied":
                roi        = frame[y1:y2, x1:x2]
                plate_text = anpr.read_plate(roi)

                if plate_text:
                    print(f"[ANPR] Slot {slot_id} → Plate: {plate_text}")

                    # --- Step 3: Log entry to Firebase ---
                    firebase.log_entry(slot_id=slot_id,
                                       plate=plate_text,
                                       timestamp=time.time())

                    # --- Step 4: Pre-authorize UPI payment ---
                    txn_id = upi.pre_authorize(plate=plate_text,
                                               amount=args.rate)
                    if txn_id:
                        print(f"[UPI] Pre-auth successful. TxnID: {txn_id}")
                        firebase.update_txn(slot_id, txn_id)

        # --- Summary overlay ---
        total   = len(slots)
        occupied = sum(1 for s in slots if s["status"] == "occupied")
        empty    = total - occupied
        cv2.putText(frame, f"Slots: {total}  |  Free: {empty}  |  Occupied: {occupied}",
                    (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("ParkSense", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] ParkSense stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ParkSense Smart Parking System")
    parser.add_argument("--source", type=str, default="0",
                        help="Video source: 0 = webcam, or path to video file")
    parser.add_argument("--model",  type=str, default="models/parksense_yolov8.pt",
                        help="Path to trained YOLOv8 model weights")
    parser.add_argument("--rate",   type=float, default=20.0,
                        help="Parking rate per hour (INR)")
    args = parser.parse_args()

    # Allow string "0" to be treated as webcam int
    if args.source.isdigit():
        args.source = int(args.source)

    main(args)
