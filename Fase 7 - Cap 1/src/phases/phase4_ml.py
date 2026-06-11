from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from src.config import ML_FEATURES, TARGET_COLUMN


@dataclass
class MLResult:
    model: RandomForestClassifier
    accuracy: float
    rows_used: int


def build_training_dataframe(sensor_df: pd.DataFrame, weather_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    if sensor_df.empty:
        return pd.DataFrame()

    df = sensor_df.copy()
    df["rain_mm"] = 0.0

    if weather_df is not None and not weather_df.empty:
        rain_value = float(weather_df["rain_mm"].tail(1).iloc[0])
        df["rain_mm"] = rain_value

    if TARGET_COLUMN not in df.columns:
        df[TARGET_COLUMN] = np.where(
            (df["soil_moisture"] < 35) | ((df["temperature"] > 33) & (df["humidity"] < 55)),
            1,
            0,
        )

    return df


def train_irrigation_model(training_df: pd.DataFrame) -> Optional[MLResult]:
    if training_df.empty or len(training_df) < 20:
        return None

    X = training_df[ML_FEATURES]
    y = training_df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=120, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)

    return MLResult(model=model, accuracy=float(acc), rows_used=len(training_df))


def predict_irrigation(model: RandomForestClassifier, reading: dict, rain_mm: float = 0.0) -> int:
    X = pd.DataFrame(
        [
            {
                "soil_moisture": reading["soil_moisture"],
                "temperature": reading["temperature"],
                "humidity": reading["humidity"],
                "ph": reading["ph"],
                "rain_mm": rain_mm,
            }
        ]
    )
    pred = model.predict(X)[0]
    return int(pred)
