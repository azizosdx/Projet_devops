from flask import Flask, jsonify, request
from flask_cors import CORS
from producer import send_reservation
from database import SessionLocal, engine
from models import Reservation, Base
from sqlalchemy.orm import Session
import threading
from consumer import start_consumer
from datetime import datetime

# Create the tables if they don't exist yet
Base.metadata.create_all(bind=engine)

app = Flask(__name__)
CORS(app)

# Start the Kafka consumer in a separate thread
kafka_thread = threading.Thread(target=start_consumer)
kafka_thread.daemon = True
kafka_thread.start()

# Helper to serialize datetime
def serialize_datetime(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return value

# --- CREATE RESERVATION ---
@app.route('/reserve', methods=['POST'])
def create_reservation():
    data = request.json
    required_fields = ['user_id', 'salle_id', 'start_time', 'end_time']

    if not all(field in data for field in required_fields):
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    data['action'] = 'create'  # Add action field

    topic = "reservations_topic"  # Kafka topic name

    # Send data to Kafka
    send_reservation(topic, data)
    return jsonify({
        "status": "success",
        "message": "Reservation sent to processing"
    }), 202

# --- READ ALL RESERVATIONS ---
@app.route('/reservations', methods=['GET'])
def get_reservations():
    db: Session = SessionLocal()
    try:
        reservations = db.query(Reservation).all()
        result = [{
            "id": reservation.id,
            "user_id": reservation.user_id,
            "salle_id": reservation.salle_id,
            "start_time": serialize_datetime(reservation.start_time),
            "end_time": serialize_datetime(reservation.end_time)
        } for reservation in reservations]
        return jsonify(result)
    finally:
        db.close()

# --- READ SINGLE RESERVATION ---
@app.route('/reservations/<int:reservation_id>', methods=['GET'])
def get_reservation(reservation_id):
    db: Session = SessionLocal()
    try:
        reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if reservation:
            return jsonify({
                "id": reservation.id,
                "user_id": reservation.user_id,
                "salle_id": reservation.salle_id,
                "start_time": serialize_datetime(reservation.start_time),
                "end_time": serialize_datetime(reservation.end_time)
            })
        return jsonify({"status": "error", "message": "Reservation not found"}), 404
    finally:
        db.close()

# --- UPDATE RESERVATION ---
@app.route('/reservations/<int:reservation_id>', methods=['PUT'])
def update_reservation(reservation_id):
    data = request.json
    db: Session = SessionLocal()
    try:
        reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()

        if not reservation:
            return jsonify({"status": "error", "message": "Reservation not found"}), 404

        reservation.user_id = data.get('user_id', reservation.user_id)
        reservation.salle_id = data.get('salle_id', reservation.salle_id)
        reservation.start_time = data.get('start_time', reservation.start_time)
        reservation.end_time = data.get('end_time', reservation.end_time)

        db.commit()
        return jsonify({"status": "success", "message": "Reservation updated"})
    finally:
        db.close()

# --- DELETE RESERVATION ---
@app.route('/reservations/<int:reservation_id>', methods=['DELETE'])
def delete_reservation(reservation_id):
    db: Session = SessionLocal()
    try:
        reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()

        if not reservation:
            return jsonify({"status": "error", "message": "Reservation not found"}), 404

        db.delete(reservation)
        db.commit()

        return jsonify({"status": "success", "message": "Reservation deleted"})
    finally:
        db.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
