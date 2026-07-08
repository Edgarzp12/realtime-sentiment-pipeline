# Real-Time Sentiment Analysis Pipeline

## Overview

This project implements a data pipeline that simulates streaming social media data and performs sentiment analysis using a transformer-based model. It integrates MongoDB for ingestion, a processing pipeline for inference, and MySQL for structured storage of results.

## Architecture

* **Clients** generate simulated Twitter-like messages
* **Consumer** ingests and stores data in MongoDB
* **Pipeline** processes unstructured text using a HuggingFace model and stores results in MySQL

## Tech Stack

* Python
* MongoDB
* MySQL
* HuggingFace Transformers
* PyTorch
* Docker

## Workflow

1. Generate text data (clients)
2. Store raw messages in MongoDB
3. Retrieve unprocessed data
4. Apply sentiment analysis (transformer model)
5. Store structured results in MySQL

## Key Features

* Batch processing of unprocessed records
* GPU support (CUDA if available)
* Integration of NoSQL and relational databases
* End-to-end ML pipeline

## Project Structure

```text
.
├── docker/
├── src/
│   ├── clients/
│   ├── consumer/
│   └── pipeline/
├── requirements.txt
└── README.md
```

## How to Run

```bash
docker-compose up
python src/pipeline/run_pipeline.py
```

## Key Insight

Separating ingestion (MongoDB) from structured storage (MySQL) enables scalable processing pipelines for unstructured data.

## Author

Edgar Antonio Zeledón Pérez
