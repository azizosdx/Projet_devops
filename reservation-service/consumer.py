from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
import json
import os
import time
from database import SessionLocal
from models import Reservation
from datetime import datetime

def create_consumer_with_retry(retries=10, delay=5):
    for attempt in range(retries):
        try:
            consumer = KafkaConsumer(
                'reservations_topic',  # ✅ Correct topic name
                bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',
                enable_auto_commit=True
            )
            print("✅ KafkaConsumer connecté avec succès.")
            return consumer
        except NoBrokersAvailable:
            print(f"⏳ Kafka non disponible (tentative {attempt+1}/{retries}), nouvelle tentative dans {delay}s...")
            time.sleep(delay)
    raise Exception("❌ Impossible de se connecter à Kafka.")

def start_consumer():
    consumer = create_consumer_with_retry()

    print("🔄 Kafka Consumer started for reservation-service...")
    try:
        for message in consumer:
            reservation_event = message.value
            print(f"📩 Réception : {reservation_event}")

            db = SessionLocal()
            try:
                if reservation_event.get('action') == 'create':
                    reservation = Reservation(
                        user_id=reservation_event['user_id'],
                        salle_id=reservation_event['salle_id'],
                        start_time=datetime.fromisoformat(reservation_event['start_time']),
                        end_time=datetime.fromisoformat(reservation_event['end_time'])
                    )
                    db.add(reservation)
                    db.commit()
                    print(f"✅ Réservation créée avec ID : {reservation.id}")
            except Exception as e:
                print(f"❌ Erreur pendant le traitement : {e}")
                db.rollback()
            finally:
                db.close()
    except KeyboardInterrupt:
        print("🛑 Arrêt du consumer Kafka.")
    finally:
        consumer.close()
