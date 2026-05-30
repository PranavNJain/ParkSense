"""
ParkSense - ANPR (Automatic Number Plate Recognition)
Uses EasyOCR to extract license plate text from vehicle ROIs.
"""

import re
import cv2
import numpy as np
import easyocr


class ANPRProcessor:
    def __init__(self, languages: list = None):
        if languages is None:
            languages = ["en"]
        self.reader = easyocr.Reader(languages, gpu=False)
        # Indian number plate pattern: MH12AB1234 or MH-12-AB-1234
        self._plate_pattern = re.compile(r"[A-Z]{2}[\s\-]?\d{2}[\s\-]?[A-Z]{1,2}[\s\-]?\d{4}")
        print("[ANPR] EasyOCR reader initialized.")

    def read_plate(self, roi: np.ndarray) -> str | None:
        """
        Extract and validate a license plate from a cropped vehicle ROI.

        Args:
            roi: BGR image crop containing the vehicle/plate area.

        Returns:
            Cleaned plate string (e.g., "MH12AB1234") or None if not found.
        """
        preprocessed = self._preprocess(roi)
        results      = self.reader.readtext(preprocessed)

        for (_, text, confidence) in results:
            if confidence < 0.4:
                continue
            cleaned = self._clean(text)
            if self._plate_pattern.match(cleaned):
                return cleaned

        return None

    def _preprocess(self, img: np.ndarray) -> np.ndarray:
        """Enhance the ROI for better OCR accuracy."""
        gray    = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
        blurred = cv2.GaussianBlur(resized, (3, 3), 0)
        thresh  = cv2.adaptiveThreshold(
            blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        return thresh

    @staticmethod
    def _clean(text: str) -> str:
        """Remove spaces/dashes and convert to uppercase."""
        return re.sub(r"[\s\-]", "", text).upper()
