import os
import torch
from pymongo import MongoClient
import mysql.connector
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from dotenv import load_dotenv
from datetime import datetime
import time


# ----------------------------------------------------
# 1. Cargar Variables de Entorno
# ----------------------------------------------------
load_dotenv(dotenv_path="/home/edgar_16/bigdata-sentiment-project/.env")

HF_MODEL = os.getenv("HF_MODEL")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

LIMIT = int(os.getenv("LIMIT", 200))

LABELS = ["very_negative", "negative", "neutral", "positive", "very_positive"]


# ----------------------------------------------------
# 2. Conectar a MongoDB
# ----------------------------------------------------
def get_mongo():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    return db[MONGO_COLLECTION]

# ----------------------------------------------------
# 3. Conectar a MySQL
# ----------------------------------------------------
def get_mysql():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )

# ----------------------------------------------------
# 4. Cargar Modelo y Tokenizer
# ----------------------------------------------------
def load_model():
    print("🔄 Cargando modelo desde HuggingFace...")
    tokenizer = AutoTokenizer.from_pretrained(HF_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(HF_MODEL)
    model.to(DEVICE)
    model.eval()
    print("✅ Modelo cargado correctamente.")
    return tokenizer, model

# ----------------------------------------------------
# 5. Predicción
# ----------------------------------------------------
def predict(texts, tokenizer, model):
    inputs = tokenizer(
        texts,
        padding=True,
        truncation=True,
        return_tensors="pt",
        max_length=256
    )
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)

    probs = torch.softmax(outputs.logits, dim=1)
    scores = probs.max(dim=1).values.cpu().numpy().tolist()
    classes = probs.argmax(dim=1).cpu().numpy().tolist()

    labels = [LABELS[c] for c in classes]
    return labels, scores

# ----------------------------------------------------
# 6. Pipeline Principal
# ----------------------------------------------------
def run_pipeline():
    collection = get_mongo()
    mysql_db = get_mysql()
    cursor = mysql_db.cursor()

    tokenizer, model = load_model()

    print("🔍 Buscando comentarios sin procesar en Mongo...")
    docs = list(collection.find({"processed": False}).limit(LIMIT))

    if not docs:
        print("😴 No hay comentarios pendientes.")
        return

    print(f"📌 Procesando {len(docs)} comentarios...")

    texts = [d["comment"] for d in docs]
    labels, scores = predict(texts, tokenizer, model)

    for doc, label, score in zip(docs, labels, scores):

        # 1. Actualizar Mongo
        collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {
                "processed": True,
                "sentiment": label,
                "score": float(score),
                "processed_at": datetime.utcnow()
            }}
        )

        # 2. Insertar en MySQL
        cursor.execute(
            """
            INSERT INTO sentiment_predictions
            (user_id, comment, sentiment_label, sentiment_score, processed_at)
            VALUES (%s, %s, %s, %s, NOW())
            """,
            (doc["user_id"], doc["comment"], label, float(score))
        )
        time.sleep(0.1)

    mysql_db.commit()
    cursor.close()
    mysql_db.close()

    print("🎉 Pipeline ejecutado correctamente.")

# ----------------------------------------------------
# 7. Ejecutar
# ----------------------------------------------------
if __name__ == "__main__":
    run_pipeline()
