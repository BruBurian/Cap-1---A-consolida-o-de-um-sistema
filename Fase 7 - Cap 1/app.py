from __future__ import annotations

import pandas as pd
import streamlit as st

from src.database import ensure_database, query_df
from src.phases.phase1_data import PlantingInput, calculate_planting_metrics, phase1_run
from src.phases.phase2_db import (
    save_planting_area,
    save_sensor_reading,
    save_vision_event,
    save_weather_dataframe,
)
from src.phases.phase3_iot import generate_sensor_batch, generate_sensor_reading
from src.phases.phase4_ml import build_training_dataframe, predict_irrigation, train_irrigation_model
from src.phases.phase6_vision import run_vision_pipeline
from src.services.alert_service import send_alert

st.set_page_config(page_title="Fase 7 - Agro Hub", layout="wide")
ensure_database()

st.title("Sistema Integrado de Gestao do Agronegocio - Fase 7")
st.caption("Integracao das fases 1, 2, 3, 4, 5 e 6 em um unico projeto")


def load_table(table_name: str) -> pd.DataFrame:
    return query_df(f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT 200")


tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    [
        "Fase 1 - Dados e Meteorologia",
        "Fase 2 - Banco de Dados",
        "Fase 3 - IoT e Automacao",
        "Fase 4 - Dashboard e ML",
        "Fase 5 - Alertas AWS",
        "Fase 6 - Visao Computacional",
        "Fase 7 - Consolidado",
    ]
)

with tab1:
    st.subheader("Cadastro de area de plantio")
    with st.form("planting_form"):
        crop = st.text_input("Cultura", value="Soja")
        col1, col2, col3 = st.columns(3)
        with col1:
            length_m = st.number_input("Comprimento (m)", min_value=1.0, value=30.0)
        with col2:
            width_m = st.number_input("Largura (m)", min_value=1.0, value=15.0)
        with col3:
            fert_rate = st.number_input("Taxa de insumo kg/m2", min_value=0.01, value=0.12)
        submitted = st.form_submit_button("Calcular e Salvar")

    if submitted:
        metrics = calculate_planting_metrics(
            PlantingInput(crop=crop, length_m=length_m, width_m=width_m, fertilizer_rate_kg_m2=fert_rate)
        )
        save_planting_area(crop, length_m, width_m, metrics["area_m2"], metrics["estimated_fertilizer_kg"])
        st.success(
            f"Area: {metrics['area_m2']} m2 | Insumo estimado: {metrics['estimated_fertilizer_kg']} kg"
        )

    if st.button("Atualizar meteorologia (7 dias)"):
        weather_df, stats = phase1_run()
        save_weather_dataframe(weather_df)
        st.success("Meteorologia coletada e salva no banco")
        st.write(stats)
        st.dataframe(weather_df, use_container_width=True)

with tab2:
    st.subheader("Banco relacional e integracao de dados")
    st.caption("Visualizacao da camada de persistencia da Fase 2")

    table_names = ["planting_areas", "weather_data", "sensor_readings", "vision_events", "alerts_log"]
    counts = {
        name: int(query_df(f"SELECT COUNT(*) as n FROM {name}")["n"].iloc[0])
        for name in table_names
    }

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("planting_areas", counts["planting_areas"])
    c2.metric("weather_data", counts["weather_data"])
    c3.metric("sensor_readings", counts["sensor_readings"])
    c4.metric("vision_events", counts["vision_events"])
    c5.metric("alerts_log", counts["alerts_log"])

    selected_table = st.selectbox("Tabela para inspecionar", table_names)
    sample_df = query_df(f"SELECT * FROM {selected_table} ORDER BY id DESC LIMIT 50")
    st.dataframe(sample_df, use_container_width=True)

with tab3:
    st.subheader("Leituras de sensores (simuladas)")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Gerar 1 leitura"):
            reading = generate_sensor_reading()
            save_sensor_reading(reading)
            st.json(reading)

    with col2:
        if st.button("Gerar 30 leituras"):
            batch = generate_sensor_batch(30)
            for item in batch:
                save_sensor_reading(item)
            st.success("30 leituras salvas")

    sensor_df = load_table("sensor_readings")
    st.dataframe(sensor_df, use_container_width=True)

with tab4:
    st.subheader("Analise preditiva de irrigacao")
    sensor_df = query_df("SELECT * FROM sensor_readings ORDER BY id ASC")
    weather_df = query_df("SELECT * FROM weather_data ORDER BY id ASC")

    if sensor_df.empty:
        st.warning("Gere leituras na Fase 3 para treinar o modelo")
    else:
        training_df = build_training_dataframe(sensor_df, weather_df)
        result = train_irrigation_model(training_df)

        if result is None:
            st.info("Dados insuficientes para treino (minimo recomendado: 20)")
        else:
            st.metric("Acuracia do modelo", f"{result.accuracy * 100:.1f}%")
            st.metric("Registros usados", result.rows_used)

            latest = sensor_df.tail(1).to_dict(orient="records")[0]
            rain_last = float(weather_df["rain_mm"].tail(1).iloc[0]) if not weather_df.empty else 0.0
            pred = predict_irrigation(result.model, latest, rain_mm=rain_last)
            st.write("Ultima leitura:", latest)
            st.success(
                "Recomendacao: ACIONAR irrigacao" if pred == 1 else "Recomendacao: manter bomba desligada"
            )

    if not sensor_df.empty:
        chart_df = sensor_df[["soil_moisture", "temperature", "humidity", "ph"]].tail(60)
        st.line_chart(chart_df)

with tab5:
    st.subheader("Alertas e mensageria")
    alert_type = st.selectbox(
        "Tipo de alerta",
        ["soil_moisture_low", "vision_critical", "ph_out_of_range"],
    )
    value = st.text_input("Valor/contexto", value="Exemplo")
    if st.button("Enviar alerta"):
        result = send_alert(alert_type, value, destination="funcionarios@fazenda")
        if result.ok:
            st.success(f"Alerta processado via {result.provider}: {result.status}")
        else:
            st.error(result.detail)

    alert_df = load_table("alerts_log")
    st.dataframe(alert_df, use_container_width=True)

with tab6:
    st.subheader("Analise visual de saude da lavoura")
    st.info("Coloque imagens em data/images para processar")

    if st.button("Processar imagens"):
        events = run_vision_pipeline()
        if not events:
            st.warning("Nenhuma imagem encontrada em data/images")
        else:
            for event in events:
                save_vision_event(event)
                if event["health_status"] == "critico":
                    send_alert("vision_critical", event["image_name"], destination="funcionarios@fazenda")
            st.success(f"{len(events)} imagens processadas")
            st.dataframe(pd.DataFrame(events), use_container_width=True)

    vision_df = load_table("vision_events")
    st.dataframe(vision_df, use_container_width=True)

with tab7:
    st.subheader("Resumo integrado")
    t_planting = query_df("SELECT COUNT(*) as n FROM planting_areas")
    t_weather = query_df("SELECT COUNT(*) as n FROM weather_data")
    t_sensor = query_df("SELECT COUNT(*) as n FROM sensor_readings")
    t_vision = query_df("SELECT COUNT(*) as n FROM vision_events")
    t_alert = query_df("SELECT COUNT(*) as n FROM alerts_log")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Areas", int(t_planting["n"].iloc[0]))
    c2.metric("Meteorologia", int(t_weather["n"].iloc[0]))
    c3.metric("Sensores", int(t_sensor["n"].iloc[0]))
    c4.metric("Eventos visuais", int(t_vision["n"].iloc[0]))
    c5.metric("Alertas", int(t_alert["n"].iloc[0]))
