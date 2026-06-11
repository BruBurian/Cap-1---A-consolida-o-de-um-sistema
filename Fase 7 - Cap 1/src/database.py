import sqlite3
from contextlib import contextmanager
from datetime import datetime

from src.config import DB_PATH


def ensure_database() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS planting_areas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crop TEXT NOT NULL,
                length_m REAL NOT NULL,
                width_m REAL NOT NULL,
                area_m2 REAL NOT NULL,
                estimated_fertilizer_kg REAL NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_ref TEXT NOT NULL,
                temperature REAL,
                humidity REAL,
                rain_mm REAL,
                source TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                soil_moisture REAL NOT NULL,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL,
                ph REAL NOT NULL,
                ldr_value REAL NOT NULL,
                pump_activated INTEGER NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS vision_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                image_name TEXT NOT NULL,
                health_status TEXT NOT NULL,
                confidence REAL NOT NULL,
                details TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                message TEXT NOT NULL,
                sent_to TEXT,
                provider TEXT NOT NULL,
                status TEXT NOT NULL
            )
            """
        )
        conn.commit()


@contextmanager
def get_conn():
    ensure_database()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


def query_df(sql: str, params: tuple = ()): 
    import pandas as pd

    with get_conn() as conn:
        return pd.read_sql_query(sql, conn, params=params)
