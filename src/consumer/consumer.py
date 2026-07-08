import json
import time
from confluent_kafka import Consumer
from pymongo import MongoClient

kafka_conf = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "sentiment-consumer",
    "auto.offset.reset": "earliest",
}

consumer = Consumer(kafka_conf)
consumer.subscribe(["twitter-comments"])

mongo = MongoClient("mongodb://localhost:27017")
db = mongo["sentiment_db"]
collection = db["raw_comments"]

print("Consumer started. Listening for messages...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Kafka error: {msg.error()}")
            continue

        data = json.loads(msg.value().decode("utf-8"))

        enriched = {
            "user_id": data["user_id"],
            "comment": data["comment"],
            "received_at": time.time(),
            "topic": msg.topic(),
            "partition": msg.partition(),
            "offset": msg.offset(),
            "processed": False,
        }

        collection.insert_one(enriched)
        print("Stored:", enriched["comment"][:60])

except KeyboardInterrupt:
    print("Shutting down consumer.")
finally:
    consumer.close()
    mongo.close()
