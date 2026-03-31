# Big Data Sentiment Analysis Project

Este proyecto simula un pipeline de Big Data para análisis de sentimiento de texto en tiempo real.

## Objetivo

Simular comentarios tipo Twitter que son enviados por Kafka, almacenados en MongoDB y procesados por un modelo de Deep Learning para clasificar su sentimiento. Los resultados se guardan en MySQL y se visualizan con Metabase.

## Arquitectura

Kafka + Zookeeper -> MongoDB -> Pipeline en Python (PyTorch + HuggingFace) -> MySQL -> Metabase

## Requisitos

- Docker
- Docker Compose
- Python 3.10+

## Estructura del proyecto

bigdata-sentiment-project/
├── clients/
│ └── clients.py
├── consumer/
│ └── consumer.py
├── pipeline/
│ └── run_pipeline.py
├── docker/
│ └── docker-compose.yml
├── requirements.txt
└── README.md

## Pasos para ejecutar el proyecto

### 1. Levantar la infraestructura con Docker
cd docker
docker compose up -d

### 2. Crear el entorno virtual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

### 3. Ejecutar el Producer (clientes)
cd clients
python clients.py

### 4. Ejecutar el Consumer
cd consumer
python consumer.py

### 5. Ejecutar el Pipeline de Machine Learning
cd pipeline
python run_pipeline.py

### 6. Dashboard en Metabase
Abrir en el navegador:

http://localhost:3000