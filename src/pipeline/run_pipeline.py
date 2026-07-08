import os
import torch
from pymongo import MongoClient
import mysql.connector
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

HF_MODEL = os.getenv("HF_MODEL")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

LIMIT = int(os.getenv("LIMIT", 200))

# Labels match nlptown/bert-base-multilingual-uncased-sentiment output order (1-5 stars)
LABELS = ["very_negative", "negative", "neutral", "positive", "very_positive"]


def get_mongo():
    client = MongoClient(MONGO_URI)
    return client, client[MONGO_DB][MONGO_COLLECTION]

def get_mysql():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
    )

def load_model():
    print(f"Loading model: {HF_MODEL}")
    tokenizer = AutoTokenizer.from_pretrained(HF_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(HF_MODEL)
    model.to(DEVICE)
    model.eval()
    print("Model ready.")
    return tokenizer, model

def predict(texts, tokenizer, model):
    inputs = tokenizer(texts, padding=True, truncation=True,
                       return_tensors="pt", max_length=256)
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
    probs = torch.softmax(outputs.logits, dim=1)
    scores = probs.max(dim=1).values.cpu().numpy().tolist()
    classes = probs.argmax(dim=1).cpu().numpy().tolist()
    return [LABELS[c] for c in classes], scores

def run_pipeline():
    mongo_client, collection = get_mongo()
    mysql_db = get_mysql()
    cursor = mysql_db.cursor()
    tokenizer, model = load_model()

    print("Fetching unprocessed comments from MongoDB...")
    docs = list(collection.find({"processed": False}).limit(LIMIT))

    if not docs:
        print("Nothing to process.")
        cursor.close()
        mysql_db.close()
        mongo_client.close()
        return

    print(f"Running inference on {len(docs)} comments...")
    texts = [d["comment"] for d in docs]
    labels, scores = predict(texts, tokenizer, model)

    processed_at = datetime.utcnow()

    try:
        for doc, label, score in zip(docs, labels, scores):
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {
                    "processed": True,
                    "sentiment": label,
                    "score": float(score),
                    "processed_at": processed_at,
                }},
            )
            cursor.execute(
                """
                INSERT INTO sentiment_predictions
                    (user_id, comment, sentiment_label, sentiment_score, processed_at)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (doc["user_id"], doc["comment"], label, float(score), processed_at),
            )
        mysql_db.commit()
        print(f"Done. {len(docs)} comments processed.")
    except Exception as e:
        print(f"Error during processing: {e}")
        mysql_db.rollback()
        raise
    finally:
        cursor.close()
        mysql_db.close()
        mongo_client.close()

if __name__ == "__main__":
    run_pipeline()
