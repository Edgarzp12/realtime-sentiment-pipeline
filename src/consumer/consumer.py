from confluent_kafka import Consumer
from pymongo import MongoClient
import json
import time

# Kafka
conf = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "sentiment-consumer",
    "auto.offset.reset": "earliest"
}

consumer = Consumer(conf)
consumer.subscribe(["twitter-comments"])

# Mongo
mongo = MongoClient("mongodb://localhost:27017")
db = mongo["sentiment_db"]
collection = db["raw_comments"]

print("Consumer started. Listening for messages...")

while True:
    msg = consumer.poll(1.0)
    if msg is None or msg.error():
        continue

    data = json.loads(msg.value().decode("utf-8"))

    enriched = {
    "user_id": data["user_id"],
    "comment": data["comment"],
    "received_at": time.time(),
    "topic": msg.topic(),
    "partition": msg.partition(),
    "offset": msg.offset(),
    "processed": False
    }


    print("Received:", enriched)
    collection.insert_one(enriched)

    
