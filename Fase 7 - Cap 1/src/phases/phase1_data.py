from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Tuple

import numpy as np
import pandas as pd
import requests

from src.config import DEFAULT_LOCATION


@dataclass
class PlantingInput:
    crop: str
    length_m: float
    width_m: float
    fertilizer_rate_kg_m2: float = 0.12


def calculate_planting_metrics(data: PlantingInput) -> Dict[str, float]:
    area_m2 = data.length_m * data.width_m
    fertilizer_kg = area_m2 * data.fertilizer_rate_kg_m2
    return {
        "area_m2": round(area_m2, 2),
        "estimated_fertilizer_kg": round(fertilizer_kg, 2),
    }


def _simulate_weather(days: int = 7) -> pd.DataFrame:
    base_date = datetime.utcnow().date()
    rows = []
    for i in range(days):
        d = base_date - timedelta(days=(days - i - 1))
        temp = np.random.normal(27, 4)
        humidity = np.clip(np.random.normal(65, 12), 20, 95)
        rain = max(0.0, np.random.normal(6, 8))
        rows.append(
            {
                "date_ref": d.isoformat(),
                "temperature": round(float(temp), 2),
                "humidity": round(float(humidity), 2),
                "rain_mm": round(float(rain), 2),
                "source": "simulated",
            }
        )
    return pd.DataFrame(rows)


def fetch_weather_data(latitude: float, longitude: float, days: int = 7) -> pd.DataFrame:
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        "&hourly=temperature_2m,relative_humidity_2m,precipitation"
        "&forecast_days=7"
    )
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        payload = response.json()

        hourly = payload.get("hourly", {})
        times = pd.to_datetime(hourly.get("time", []))
        if len(times) == 0:
            return _simulate_weather(days)

        df_hourly = pd.DataFrame(
            {
                "time": times,
                "temperature": hourly.get("temperature_2m", []),
                "humidity": hourly.get("relative_humidity_2m", []),
                "rain_mm": hourly.get("precipitation", []),
            }
        )
        df_hourly["date_ref"] = df_hourly["time"].dt.date.astype(str)

        df_daily = (
            df_hourly.groupby("date_ref", as_index=False)
            .agg(
                {
                    "temperature": "mean",
                    "humidity": "mean",
                    "rain_mm": "sum",
                }
            )
            .tail(days)
        )
        df_daily["temperature"] = df_daily["temperature"].round(2)
        df_daily["humidity"] = df_daily["humidity"].round(2)
        df_daily["rain_mm"] = df_daily["rain_mm"].round(2)
        df_daily["source"] = "open-meteo"
        return df_daily
    except Exception:
        return _simulate_weather(days)


def phase1_run(location: Dict[str, float] | None = None) -> Tuple[pd.DataFrame, Dict[str, float]]:
    location = location or DEFAULT_LOCATION
    df = fetch_weather_data(location["latitude"], location["longitude"], days=7)
    stats = {
        "temp_media": round(float(df["temperature"].mean()), 2),
        "umidade_media": round(float(df["humidity"].mean()), 2),
        "chuva_total": round(float(df["rain_mm"].sum()), 2),
    }
    return df, stats
