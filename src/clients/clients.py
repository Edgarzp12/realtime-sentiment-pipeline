import json
import time
import random
from confluent_kafka import Producer

COMMENTS = [
    "I love this!",
    "This is terrible.",
    "What a great day!",
    "I hate waiting like this.",
    "Amazing work, seriously impressed.",
    "This makes no sense at all.",
    "Feeling really good today.",
    "Worst experience I've had in a while.",
    "Feeling grateful for everything lately.",
    "This completely ruined my mood.",
    "Can't believe how awesome this turned out!",
    "I'm extremely disappointed with this.",
    "Such a beautiful moment, loved it.",
    "Why is everything always so complicated?",
    "Absolutely thrilled with the results!",
    "This was honestly a terrible idea.",
    "Proud of what I accomplished today.",
    "Nothing seems to be going right.",
    "Best news I've heard all week!",
    "I wish I hadn't seen this.",
    "Feeling inspired after that.",
    "Not impressed, not even a little.",
    "This made my whole day better.",
    "Completely unacceptable behavior.",
    "Full of hope again after this.",
    "This is so frustrating I can't deal.",
    "Just wonderful, thank you.",
    "What an absolute disaster.",
    "So excited, can barely contain it!",
    "I already regret this decision.",
    "This is honestly perfect.",
    "Could have been so much better.",
    "Overjoyed with how this went.",
    "I'm losing my patience with this.",
    "That made me smile so much.",
    "Terrible outcome, very disappointed.",
    "Feeling calm and really happy today.",
    "This is the definition of failure.",
    "Loving the positive energy here.",
    "Everything about this is just wrong.",
    "Insanely good, did not expect that!",
    "This bothers me more than it should.",
    "Impressive job all around.",
    "Not my kind of thing at all.",
    "Feeling hopeful for the first time in a while.",
    "Complete failure from start to finish.",
    "This exceeded every single expectation!",
    "Nothing here makes any sense.",
    "Energized and ready to go!",
    "This is honestly embarrassing.",
    "So heartwarming, really appreciated.",
    "I just can't take this anymore.",
    "Made my whole week so much better.",
    "Terrible, just absolutely terrible.",
    "This brought me so much joy.",
    "I seriously dislike this a lot.",
    "Such positive energy in here!",
    "Not what I was expecting at all.",
    "Feeling super motivated right now.",
    "This is a huge disappointment.",
    "Today was honestly amazing.",
    "I'm just done with all of this.",
]

USERS = [f"user_{i}" for i in range(1, 101)]

def send_message(producer):
    msg = {
        "user_id": random.choice(USERS),
        "comment": random.choice(COMMENTS),
    }
    producer.produce("twitter-comments", json.dumps(msg).encode("utf-8"))
    producer.flush()
    print("Sent:", msg)

def main():
    producer = Producer({"bootstrap.servers": "localhost:9092"})
    print("Client started.")
    n = random.randint(5, 200)
    for _ in range(n):
        send_message(producer)
        time.sleep(random.uniform(0.5, 3))
    print(f"Client finished. Sent {n} messages.")

if __name__ == "__main__":
    main()
