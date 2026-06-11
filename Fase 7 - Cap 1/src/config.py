from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
EXPORT_DIR = DATA_DIR / "exports"
IMAGE_DIR = DATA_DIR / "images"
DB_PATH = DATA_DIR / "agro_fase7.db"

DEFAULT_LOCATION = {
    "latitude": -23.5505,
    "longitude": -46.6333,
    "cidade": "Sao Paulo",
}

SENSOR_THRESHOLDS = {
    "soil_moisture_min": 35.0,
    "soil_moisture_max": 80.0,
    "ph_min": 5.8,
    "ph_max": 7.2,
    "temperature_max": 34.0,
}

ML_FEATURES = ["soil_moisture", "temperature", "humidity", "ph", "rain_mm"]
TARGET_COLUMN = "needs_irrigation"
