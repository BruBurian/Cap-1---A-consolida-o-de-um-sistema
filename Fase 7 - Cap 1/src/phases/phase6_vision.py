from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import cv2
import numpy as np

from src.config import IMAGE_DIR
from src.database import now_iso


def _analyze_image_health(image_path: Path) -> Dict[str, float]:
    # cv2.imread may fail on Windows when the file path contains non-ASCII chars.
    img = cv2.imread(str(image_path))
    if img is None:
        try:
            file_bytes = np.fromfile(str(image_path), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        except Exception:
            img = None

    if img is None:
        return {
            "status": "error",
            "confidence": 0.0,
            "details": "Imagem invalida ou corrompida",
        }

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    green_mask = cv2.inRange(hsv, (35, 40, 40), (90, 255, 255))
    green_ratio = float(np.sum(green_mask > 0) / (img.shape[0] * img.shape[1]))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bright_ratio = float(np.sum(gray > 210) / (img.shape[0] * img.shape[1]))

    if green_ratio > 0.45 and bright_ratio < 0.2:
        status = "saudavel"
        confidence = min(0.98, 0.65 + green_ratio)
    elif green_ratio > 0.25:
        status = "alerta"
        confidence = 0.65
    else:
        status = "critico"
        confidence = 0.8

    details = f"green_ratio={green_ratio:.2f}, bright_ratio={bright_ratio:.2f}"
    return {"status": status, "confidence": round(confidence, 2), "details": details}


def run_vision_pipeline(image_dir: Path | None = None) -> List[dict]:
    image_dir = image_dir or IMAGE_DIR
    image_dir.mkdir(parents=True, exist_ok=True)

    events = []
    for path in sorted(image_dir.glob("*")):
        if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            continue
        result = _analyze_image_health(path)
        event = {
            "timestamp": now_iso(),
            "image_name": path.name,
            "health_status": result["status"],
            "confidence": result["confidence"],
            "details": result["details"],
        }
        events.append(event)

    return events
