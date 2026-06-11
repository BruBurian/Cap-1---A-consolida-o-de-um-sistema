from __future__ import annotations

import argparse

from src.database import ensure_database, query_df
from src.phases.phase1_data import phase1_run
from src.phases.phase2_db import save_sensor_reading, save_vision_event, save_weather_dataframe
from src.phases.phase3_iot import generate_sensor_batch
from src.phases.phase6_vision import run_vision_pipeline
from src.services.alert_service import send_alert


def cmd_phase1() -> None:
    df, stats = phase1_run()
    save_weather_dataframe(df)
    print("[Fase1] Meteorologia salva")
    print(stats)


def cmd_phase3(samples: int) -> None:
    batch = generate_sensor_batch(samples)
    for item in batch:
        save_sensor_reading(item)
    print(f"[Fase3] {len(batch)} leituras salvas")


def cmd_phase6() -> None:
    events = run_vision_pipeline()
    for event in events:
        save_vision_event(event)
    print(f"[Fase6] {len(events)} imagens processadas")


def cmd_alert(alert_type: str, value: str) -> None:
    result = send_alert(alert_type, value)
    print(f"[Fase5] provider={result.provider}, status={result.status}, detail={result.detail}")


def cmd_status() -> None:
    tables = ["planting_areas", "weather_data", "sensor_readings", "vision_events", "alerts_log"]
    for table in tables:
        n = int(query_df(f"SELECT COUNT(*) as n FROM {table}")["n"].iloc[0])
        print(f"{table}: {n}")


def main() -> None:
    ensure_database()

    parser = argparse.ArgumentParser(description="Orquestrador Fase 7")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("phase1", help="Coleta meteorologia e salva no banco")

    p3 = sub.add_parser("phase3", help="Gera leituras IoT simuladas")
    p3.add_argument("--samples", type=int, default=10)

    sub.add_parser("phase6", help="Processa imagens de data/images")

    pa = sub.add_parser("alert", help="Envia alerta")
    pa.add_argument("--type", required=True, choices=["soil_moisture_low", "vision_critical", "ph_out_of_range"])
    pa.add_argument("--value", required=True)

    sub.add_parser("status", help="Mostra quantidade de registros")

    args = parser.parse_args()

    if args.command == "phase1":
        cmd_phase1()
    elif args.command == "phase3":
        cmd_phase3(args.samples)
    elif args.command == "phase6":
        cmd_phase6()
    elif args.command == "alert":
        cmd_alert(args.type, args.value)
    elif args.command == "status":
        cmd_status()


if __name__ == "__main__":
    main()
