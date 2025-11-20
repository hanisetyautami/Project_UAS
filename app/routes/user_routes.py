# app/routes/user_routes.py
from flask import Blueprint, jsonify, request
from app.models.user_model import User
from app.extensions import db

user_bp = Blueprint('user_bp', __name__)   # <-- perbaikan: use __name__

# CREATE (POST)
@user_bp.route('/', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    username = data.get('username')
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not (username and name and email and password):
        return jsonify({"error": "username, name, email, and password are required"}), 400

    # check duplicate username/email
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "username or email already exists"}), 409

    new_user = User(username=username, name=name, email=email)
    new_user.password = password  # uses setter to hash password
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully", "user": new_user.to_dict()}), 201

# READ ALL (GET)
@user_bp.route('/', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200
