from __future__ import annotations

from datetime import datetime
from typing import Dict, List

import numpy as np

from src.config import SENSOR_THRESHOLDS


def evaluate_irrigation(soil_moisture: float, ph: float, temperature: float) -> bool:
    too_dry = soil_moisture < SENSOR_THRESHOLDS["soil_moisture_min"]
    bad_ph = ph < SENSOR_THRESHOLDS["ph_min"] or ph > SENSOR_THRESHOLDS["ph_max"]
    hot_day = temperature > SENSOR_THRESHOLDS["temperature_max"]
    return bool(too_dry or (hot_day and not bad_ph))


def generate_sensor_reading() -> Dict[str, float]:
    soil_moisture = float(np.clip(np.random.normal(48, 18), 5, 98))
    temperature = float(np.clip(np.random.normal(28, 5), 12, 43))
    humidity = float(np.clip(np.random.normal(66, 14), 20, 99))
    ph = float(np.clip(np.random.normal(6.4, 0.6), 4.5, 8.5))
    ldr_value = float(np.clip(np.random.normal(700, 180), 20, 1023))

    pump_activated = evaluate_irrigation(soil_moisture, ph, temperature)

    return {
        "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
        "soil_moisture": round(soil_moisture, 2),
        "temperature": round(temperature, 2),
        "humidity": round(humidity, 2),
        "ph": round(ph, 2),
        "ldr_value": round(ldr_value, 2),
        "pump_activated": int(pump_activated),
    }


def generate_sensor_batch(n: int = 30) -> List[Dict[str, float]]:
    return [generate_sensor_reading() for _ in range(n)]
