from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Salle
import threading
from consumer import start_consumer
from models import Base
from database import engine

# Crée les tables si elles n'existent pas encore
Base.metadata.create_all(bind=engine)


app = Flask(__name__)
CORS(app)

# Démarrer le consumer Kafka dans un thread séparé
kafka_thread = threading.Thread(target=start_consumer)
kafka_thread.daemon = True
kafka_thread.start()

# --- CREATE ---
@app.route('/salles', methods=['POST'])
def create_salle():
    data = request.json
    required_fields = ['name', 'capacity']
    
    if not all(field in data for field in required_fields):
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    db: Session = SessionLocal()
    salle = Salle(
        name=data['name'],
        capacity=data['capacity'],
        available=True  # Par défaut, la salle est disponible
    )
    db.add(salle)
    db.commit()

    return jsonify({"status": "success", "salle": {"id": salle.id, "name": salle.name}}), 201

# --- READ ALL ---
@app.route('/salles', methods=['GET'])
def get_salles():
    db: Session = SessionLocal()
    salles = db.query(Salle).all()
    return jsonify([
        {
            "id": salle.id,
            "name": salle.name,
            "capacity": salle.capacity,
            "available": salle.available
        } for salle in salles
    ])

# --- READ ONE ---
@app.route('/salles/<int:salle_id>', methods=['GET'])
def get_salle(salle_id):
    db: Session = SessionLocal()
    salle = db.query(Salle).filter(Salle.id == salle_id).first()
    if salle:
        return jsonify({
            "id": salle.id,
            "name": salle.name,
            "capacity": salle.capacity,
            "available": salle.available
        })
    return jsonify({"status": "error", "message": "Salle not found"}), 404

# --- UPDATE ---
@app.route('/salles/<int:salle_id>', methods=['PUT'])
def update_salle(salle_id):
    data = request.json
    db: Session = SessionLocal()
    salle = db.query(Salle).filter(Salle.id == salle_id).first()
    
    if not salle:
        return jsonify({"status": "error", "message": "Salle not found"}), 404

    salle.name = data.get('name', salle.name)
    salle.capacity = data.get('capacity', salle.capacity)
    salle.available = data.get('available', salle.available)
    db.commit()

    return jsonify({"status": "success", "message": "Salle updated"})

# --- DELETE ---
@app.route('/salles/<int:salle_id>', methods=['DELETE'])
def delete_salle(salle_id):
    db: Session = SessionLocal()
    salle = db.query(Salle).filter(Salle.id == salle_id).first()

    if not salle:
        return jsonify({"status": "error", "message": "Salle not found"}), 404

    db.delete(salle)
    db.commit()

    return jsonify({"status": "success", "message": "Salle deleted"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
