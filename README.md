# ParkSense 🅿️

> Smart Parking Management System using YOLOv8, ANPR, Firebase & UPI Pre-Authorization

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-purple)
![Firebase](https://img.shields.io/badge/Firebase-Realtime%20DB-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📌 Problem Statement

Urban parking lots suffer from inefficiency — no real-time occupancy data, manual entry/exit logging, and cash-only payments cause congestion and revenue loss. ParkSense automates the entire pipeline using computer vision and digital payments.

---

## 🏗️ System Architecture

```
Camera Feed
    │
    ▼
YOLOv8 Slot Detection ──► Slot Status (Empty / Occupied)
    │
    ▼
ANPR (EasyOCR) ──► License Plate Text
    │
    ├──► Firebase Realtime DB ──► Live Dashboard
    │
    └──► UPI Pre-Authorization ──► QR Code at Gate
```

---

## ✨ Features

- **Real-time slot detection** using fine-tuned YOLOv8
- **Automatic Number Plate Recognition** (ANPR) via EasyOCR
- **Firebase Realtime Database** for live occupancy tracking
- **UPI payment pre-authorization** on vehicle entry
- **Auto-capture** payment on exit based on duration
- Supports Indian number plate format (e.g., MH12AB1234)

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Object Detection | YOLOv8 (Ultralytics) |
| License Plate OCR | EasyOCR |
| Database | Firebase Realtime Database |
| Payments | UPI Deep Link / Razorpay |
| Language | Python 3.10+ |
| CV Library | OpenCV |

---

## 📁 Project Structure

```
ParkSense/
├── main.py               # Entry point — runs full pipeline
├── slot_detector.py      # YOLOv8 parking slot detection
├── anpr.py               # EasyOCR license plate recognition
├── firebase_handler.py   # Firebase read/write operations
├── upi_handler.py        # UPI pre-auth and capture logic
├── requirements.txt      # Python dependencies
├── models/
│   └── parksense_yolov8.pt   # Trained YOLOv8 weights (not tracked by git)
└── config/
    └── serviceAccountKey.json  # Firebase credentials (not tracked by git)
```

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/your-username/ParkSense.git
cd ParkSense
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add Firebase credentials
- Download `serviceAccountKey.json` from your Firebase Console
- Place it in the `config/` folder

### 4. Run
```bash
# Webcam
python main.py --source 0

# Video file
python main.py --source parking_lot.mp4 --rate 20
```

---

## 📊 Firebase Data Schema

```json
{
  "parking": {
    "slots": {
      "1": {
        "plate": "MH12AB1234",
        "entry_time": "2024-03-15T10:30:00",
        "exit_time": "2024-03-15T12:00:00",
        "status": "empty",
        "txn_id": "PS-A1B2C3D4E5",
        "amount_charged": 30.0
      }
    }
  }
}
```

---

## 👨‍💻 Author

**Pranav** — AI & Data Science, VIT Pune  
[GitHub](https://github.com/your-username)

---

## 📄 License

MIT License — feel free to use and modify.
