from kafka import KafkaConsumer
import json
import os
from database import SessionLocal
from models import User

def start_consumer():
    consumer = KafkaConsumer(
        'user-events',
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    print("Kafka Consumer started for user-service...")
    for message in consumer:
        user_event = message.value
        print(f"Received user event: {user_event}")

        db = SessionLocal()

        # Exemple de traitement d'événement de création d'utilisateur
        if user_event['action'] == 'create':
            user = User(
                email=user_event['email'],
                password=user_event['password'],
                role=user_event['role']
            )
            db.add(user)
            db.commit()
            print(f"User {user.email} created")
