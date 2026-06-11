from src.database import get_conn, now_iso


def save_planting_area(crop: str, length_m: float, width_m: float, area_m2: float, fertilizer_kg: float) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO planting_areas (
                crop, length_m, width_m, area_m2, estimated_fertilizer_kg, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (crop, length_m, width_m, area_m2, fertilizer_kg, now_iso()),
        )


def save_weather_dataframe(df) -> None:
    with get_conn() as conn:
        for _, row in df.iterrows():
            conn.execute(
                """
                INSERT INTO weather_data (
                    date_ref, temperature, humidity, rain_mm, source, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    row["date_ref"],
                    float(row["temperature"]),
                    float(row["humidity"]),
                    float(row["rain_mm"]),
                    row.get("source", "unknown"),
                    now_iso(),
                ),
            )


def save_sensor_reading(reading: dict) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO sensor_readings (
                timestamp, soil_moisture, temperature, humidity, ph, ldr_value, pump_activated
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                reading["timestamp"],
                reading["soil_moisture"],
                reading["temperature"],
                reading["humidity"],
                reading["ph"],
                reading["ldr_value"],
                int(reading["pump_activated"]),
            ),
        )


def save_vision_event(event: dict) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO vision_events (
                timestamp, image_name, health_status, confidence, details
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                event["timestamp"],
                event["image_name"],
                event["health_status"],
                float(event["confidence"]),
                event.get("details", ""),
            ),
        )


def save_alert_log(alert_type: str, message: str, sent_to: str, provider: str, status: str) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO alerts_log (timestamp, alert_type, message, sent_to, provider, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (now_iso(), alert_type, message, sent_to, provider, status),
        )
