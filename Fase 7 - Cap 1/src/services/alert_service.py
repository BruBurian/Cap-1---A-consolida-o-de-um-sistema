from __future__ import annotations

import os
from dataclasses import dataclass

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv

from src.phases.phase2_db import save_alert_log

load_dotenv()


@dataclass
class AlertResult:
    ok: bool
    provider: str
    status: str
    detail: str


def build_action_message(alert_type: str, value: float | str) -> str:
    if alert_type == "soil_moisture_low":
        return f"Umidade do solo baixa ({value}). Acionar irrigacao por 15 minutos e reavaliar em 30 minutos."
    if alert_type == "vision_critical":
        return f"Analise visual critica detectada ({value}). Enviar equipe para inspecao de pragas/doencas no setor afetado."
    if alert_type == "ph_out_of_range":
        return f"pH fora da faixa ideal ({value}). Ajustar nutrientes e executar nova coleta apos correcao."
    return f"Alerta {alert_type}: {value}. Verificar operacao da fazenda."


def _send_sns(message: str, subject: str = "Alerta Fazenda Fase 7") -> AlertResult:
    region = os.getenv("AWS_REGION")
    topic_arn = os.getenv("AWS_SNS_TOPIC_ARN")

    if not region or not topic_arn:
        return AlertResult(False, "local", "missing_env", "AWS_REGION ou AWS_SNS_TOPIC_ARN nao configurado")

    try:
        client = boto3.client("sns", region_name=region)
        client.publish(TopicArn=topic_arn, Subject=subject[:100], Message=message)
        return AlertResult(True, "aws_sns", "sent", "Mensagem publicada no SNS")
    except (BotoCoreError, ClientError) as exc:
        return AlertResult(False, "aws_sns", "error", str(exc))


def send_alert(alert_type: str, value: float | str, destination: str = "equipe") -> AlertResult:
    msg = build_action_message(alert_type, value)
    result = _send_sns(msg)

    if not result.ok:
        result = AlertResult(True, "local", "logged_only", f"Simulado localmente: {msg}")

    save_alert_log(
        alert_type=alert_type,
        message=msg,
        sent_to=destination,
        provider=result.provider,
        status=result.status,
    )
    return result
