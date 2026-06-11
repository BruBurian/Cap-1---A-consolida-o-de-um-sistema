# Projeto Integrado - Fase 7 (Agro Hub)

Sistema integrado para gestão do agronegócio em Python, reunindo as entregas das Fases 1 a 6 em uma única aplicação com dashboard, execução por terminal, persistência em banco local e envio de alertas.

## Objetivo

Consolidar as fases anteriores em um único projeto executável no VS Code, permitindo:

- uso por dashboard com Streamlit;
- execução de rotinas pelo terminal;
- armazenamento centralizado em SQLite;
- alertas operacionais via AWS SNS ou fallback local.

## Funcionalidades por fase

### Fase 1 - Dados e meteorologia

- Cadastro de área de plantio e cálculo de insumos.
- Coleta meteorológica com API pública e fallback simulado.
- Salvamento em `planting_areas` e `weather_data`.

### Fase 2 - Banco de dados

- Persistência relacional em SQLite.
- Tabelas: `planting_areas`, `weather_data`, `sensor_readings`, `vision_events` e `alerts_log`.

### Fase 3 - IoT e automação

- Simulação de sensores de umidade, temperatura, pH e luminosidade.
- Registro das leituras no banco.
- Apoio à decisão de irrigação.

### Fase 4 - Dashboard e ML

- Treinamento de modelo para recomendação de irrigação.
- Exibição de métricas, histórico e previsão operacional.

### Fase 5 - Alertas e mensageria

- Integração com AWS SNS para envio de alertas.
- Fallback local quando a AWS não estiver configurada.
- Registro dos alertas em `alerts_log`.

### Fase 6 - Visão computacional

- Processamento das imagens da pasta `data/images`.
- Classificação da saúde da plantação em `saudavel`, `alerta` ou `critico`.
- Envio de alerta quando houver evento crítico.

### Fase 7 - Consolidação

- Integração das fases em um único projeto.
- Uso pelo dashboard em `app.py` e pela CLI em `main.py`.
- Visão consolidada dos dados na última aba do dashboard.

## Estrutura do projeto

- `app.py`: dashboard principal.
- `main.py`: orquestrador por linha de comando.
- `src/database.py`: criação e consulta do banco.
- `src/phases/`: implementação das fases.
- `src/services/`: serviços externos, como alertas.
- `data/images/`: imagens usadas na Fase 6.
- `data/agro_fase7.db`: banco local gerado pela aplicação.

## Como executar

1. Criar e ativar um ambiente virtual.
2. Instalar as dependências:

```bash
pip install -r requirements.txt
```

3. Executar o dashboard:

```bash
streamlit run app.py
```

4. Executar comandos opcionais no terminal:

```bash
python main.py phase1
python main.py phase3 --samples 20
python main.py phase6
python main.py alert --type soil_moisture_low --value 28
python main.py status
```
