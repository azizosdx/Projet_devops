from kafka import KafkaConsumer
import json
import os
from database import SessionLocal
from models import Salle

def start_consumer():
    consumer = KafkaConsumer(
        'reservation-events',
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    print("Kafka Consumer started for salle-service...")
    for message in consumer:
        reservation = message.value
        print(f"Received reservation: {reservation}")

        db = SessionLocal()

        # Mettre à jour la disponibilité de la salle
        salle = db.query(Salle).filter(Salle.id == reservation['salle_id']).first()
        if salle:
            salle.available = False
            db.commit()
            print(f"Salle {salle.name} marquée comme occupée")
