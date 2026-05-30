"""
ParkSense - Parking Slot Detector
Uses YOLOv8 (ultralytics) to classify each defined slot as empty or occupied.
"""

from ultralytics import YOLO
import numpy as np


SLOT_COORDS = [
    {"id": 1, "bbox": (50,  100, 200, 260)},
    {"id": 2, "bbox": (220, 100, 370, 260)},
    {"id": 3, "bbox": (390, 100, 540, 260)},
    {"id": 4, "bbox": (560, 100, 710, 260)},
    {"id": 5, "bbox": (50,  300, 200, 460)},
    {"id": 6, "bbox": (220, 300, 370, 460)},
]


class ParkingSlotDetector:
    def __init__(self, model_path: str = "models/parksense_yolov8.pt"):
        """
        Args:
            model_path: Path to the fine-tuned YOLOv8 .pt weights.
                        Falls back to YOLOv8n if file not found (demo mode).
        """
        try:
            self.model = YOLO(model_path)
            print(f"[SlotDetector] Loaded custom model: {model_path}")
        except Exception:
            self.model = YOLO("yolov8n.pt")
            print("[SlotDetector] Custom model not found — using YOLOv8n (demo mode).")

        self.conf_threshold = 0.45
        self.occupied_class = "car"  # COCO class for vehicle detection

    def detect(self, frame: np.ndarray) -> list[dict]:
        """
        Run inference and return slot status list.

        Returns:
            List of dicts: [{"id": int, "status": "empty"|"occupied", "bbox": tuple}]
        """
        results = self.model(frame, verbose=False)[0]

        # Collect bounding boxes of detected vehicles
        vehicle_boxes = []
        for box in results.boxes:
            cls_name = self.model.names[int(box.cls)]
            conf     = float(box.conf)
            if cls_name in ("car", "truck", "motorbike", "bus") and conf >= self.conf_threshold:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                vehicle_boxes.append((x1, y1, x2, y2))

        # Check each pre-defined slot for overlap with a vehicle
        slot_results = []
        for slot in SLOT_COORDS:
            sx1, sy1, sx2, sy2 = slot["bbox"]
            status = "empty"
            for vx1, vy1, vx2, vy2 in vehicle_boxes:
                iou = self._iou((sx1, sy1, sx2, sy2), (vx1, vy1, vx2, vy2))
                if iou > 0.25:
                    status = "occupied"
                    break
            slot_results.append({"id": slot["id"], "status": status, "bbox": slot["bbox"]})

        return slot_results

    @staticmethod
    def _iou(boxA: tuple, boxB: tuple) -> float:
        """Compute Intersection over Union between two bounding boxes."""
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        inter = max(0, xB - xA) * max(0, yB - yA)
        if inter == 0:
            return 0.0

        areaA = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        areaB = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
        return inter / float(areaA + areaB - inter)
