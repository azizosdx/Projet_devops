import time
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import json
import os

def create_producer_with_retry(retries=10, delay=5, initial_delay=10):
    
    # Attente initiale avant la première tentative (utile si Kafka met du temps à démarrer)
    print(f"⏳ Attente initiale de {initial_delay} secondes avant de tenter la connexion à Kafka...")
    time.sleep(initial_delay)

    for attempt in range(retries):
        try:
            print(f"⏳ Tentative de connexion à Kafka ({attempt + 1}/{retries})...")
            producer = KafkaProducer(
                bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("✅ KafkaProducer connecté avec succès.")
            return producer
        except NoBrokersAvailable as e:
            print(f"❌ Kafka non disponible : {e} — Nouvelle tentative dans {delay}s...")
            time.sleep(delay)
    
    raise Exception("❌ Échec de connexion à Kafka après plusieurs tentatives.")

# Créer le producteur Kafka avec retry et délai initial de 10 secondes
producer = create_producer_with_retry(retries=10, delay=5, initial_delay=10)


def send_reservation(topic, reservation_data):
    producer.send(topic, reservation_data)
    producer.flush()
    print(f"✅ Message envoyé au topic '{topic}' : {reservation_data}")