from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
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
@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    required_fields = ['email', 'password', 'role']
    
    if not all(field in data for field in required_fields):
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    db: Session = SessionLocal()
    user = User(
        email=data['email'],
        password=data['password'],
        role=data['role']
    )
    db.add(user)
    db.commit()

    return jsonify({"status": "success", "user": {"email": user.email, "role": user.role}}), 201

# --- READ ALL ---
@app.route('/users', methods=['GET'])
def get_users():
    db: Session = SessionLocal()
    users = db.query(User).all()
    return jsonify([
        {
            "id": user.id,
            "email": user.email,
            "role": user.role
        } for user in users
    ])

# --- READ ONE ---
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        return jsonify({
            "id": user.id,
            "email": user.email,
            "role": user.role
        })
    return jsonify({"status": "error", "message": "User not found"}), 404

# --- UPDATE ---
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    user.email = data.get('email', user.email)
    user.password = data.get('password', user.password)
    user.role = data.get('role', user.role)
    db.commit()

    return jsonify({"status": "success", "message": "User updated"})

# --- DELETE ---
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    db.delete(user)
    db.commit()

    return jsonify({"status": "success", "message": "User deleted"})

# --- LOGIN ---
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    db: Session = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    
    if user and user.password == password:
        return jsonify({
            "status": "success",
            "user": {"email": email, "role": user.role}
        })
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
