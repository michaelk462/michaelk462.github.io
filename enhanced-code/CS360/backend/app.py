"""
*****CODE INFORMATION*****
Name: Michael King
Date: 7/31/2026
File: app.py
CS-360 Enhancement: WeightTracker REST API

Replaces the local SQLite storage used by the original Android app with a
cloud-accessible MongoDB backend, exposed through a Flask REST API secured
with JWT authentication.

Run locally:
    pip install -r requirements.txt
    export MONGO_URI="mongodb+srv://<user>:<pass>@<cluster>/weighttracker"
    export JWT_SECRET_KEY="change-me"
    python app.py
"""

import os
import re
from datetime import timedelta

from bson import ObjectId
from bson.errors import InvalidId
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from pymongo import ASCENDING, MongoClient
from pymongo.errors import DuplicateKeyError
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv

load_dotenv() # reads MONGO_URI / JWT_SECRET_KEY from a local .env file, if present

#************************************************************************
# App / DB Configuration
#************************************************************************
app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "dev-secret-change-me")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=12)
jwt = JWTManager(app)

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/weighttracker")
client = MongoClient(MONGO_URI)
db = client["weighttracker"]

users_col = db["users"]
entries_col = db["weight_entries"]

#***INDEXES***
#Enforce unique usernames at the database layer (defense in depth,
#not just application-level checks) and speed up per-user entry lookups.
users_col.create_index([("username", ASCENDING)], unique=True)
entries_col.create_index([("username", ASCENDING)])

USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")
DATE_RE = re.compile(r"^\d{2}/\d{2}/\d{4}$") # MM/DD/YYYY, matches the Android UI

#************************************************************************
# Validation Helpers
#************************************************************************

def validation_error(message, status=400):
    return jsonify({"error": message}), status


def valid_username(username):
    return isinstance(username, str) and USERNAME_RE.match(username)


def valid_password(password):
    # Only length/type is enforced here; never log or echo the password
    return isinstance(password, str) and 6 <= len(password) <= 128

def valid_weight(weight):
    return isinstance(weight, (int, float)) and 0 < weight <= 2000

def valid_date(date_str):
    return isinstance(date_str, str) and bool(DATE_RE.match(date_str))

def entry_to_json(doc):
    return {
        "id": str(doc["_id"]),
        "date": doc["date"],
        "weight": doc["weight"],
    }

#************************************************************************
# Auth Routes (Login/Register with Username and Password)
#************************************************************************
@app.route("/api/register", methods=["POST"])
def register():
    body = request.get_json(silent=True) or {}
    username = body.get("username")
    password = body.get("password")

    if not valid_username(username):
        return validation_error(
            "ERROR: Username must be 3-32 characters (letters, numbers, '_', '.', '-')"
        )
    if not valid_password(password):
        return validation_error("ERROR: Password must be 6-128 characters.")

    try:
        users_col.insert_one(
            {
                "username": username,
                "password_hash": generate_password_hash(password),
                "goal_weight": None,
                "phone_number": None,
            }
        )
    except DuplicateKeyError:
        return validation_error("ERROR: Username already exists.", status=409)

    return jsonify({"message": "Account Created."}), 201

@app.route("/api/login", methods=["POST"])
def login():
    body = request.get_json(silent=True) or {}
    username = body.get("username")
    password = body.get("password")

    # Explicit type checks before hitting MongoDB
    # A raw dict/list here instead of a string is how NoSQL-injection-style
    # operator payloads (e.g. {"$ne": null}) get through if you pass user
    # input straight into a query filter.
    if not isinstance(username, str) or not isinstance(password, str):
        return validation_error("ERROR: Invalid Credentials.", status=401)

    user = users_col.find_one({"username": username})
    if not user or not check_password_hash(user["password_hash"], password):
        return validation_error("ERROR: Invalid username/password.", status=401)

    token = create_access_token(identity=username)
    return jsonify({"token": token}), 200

#************************************************************************
# Weight Entry Routes (JWT Required)
#************************************************************************
@app.route("/api/entries", methods=["GET"])
@jwt_required()
def get_entries():
    username = get_jwt_identity()
    cursor = entries_col.find({"username": username}).sort("date", -1)
    return jsonify([entry_to_json(doc) for doc in cursor]), 200


@app.route("/api/entries", methods=["POST"])
@jwt_required()
def create_entry():
    username = get_jwt_identity()
    body = request.get_json(silent=True) or {}
    date = body.get("date")
    weight = body.get("weight")

    if not valid_date(date):
        return validation_error("ERROR: Date must be in MM/DD/YYYY format.")
    if not valid_weight(weight):
        return validation_error("ERROR: Weight must be a number between 0 and 2000.")

    result = entries_col.insert_one(
        {"username": username, "date": date, "weight": float(weight)}
    )
    doc = entries_col.find_one({"_id": result.inserted_id})
    return jsonify(entry_to_json(doc)), 201


@app.route("/api/entries/<entry_id>", methods=["PUT"])
@jwt_required()
def update_entry(entry_id):
    username = get_jwt_identity()
    body = request.get_json(silent=True) or {}
    date = body.get("date")
    weight = body.get("weight")

    if not valid_date(date):
        return validation_error("ERROR: Date must be in MM/DD/YYYY format.")
    if not valid_weight(weight):
        return validation_error("ERROR: Weight must be a number between 0 and 2000.")

    try:
        oid = ObjectId(entry_id)
    except InvalidId:
        return validation_error("ERROR: Invalid Entry ID.", status=404)

    # Scope the filter to the authenticated user so nobody can edit
    # another user's entry by guessing/incrementing an id.
    result = entries_col.update_one(
        {"_id": oid, "username": username},
        {"$set": {"date": date, "weight": float(weight)}},
    )
    if result.matched_count == 0:
        return validation_error("Entry Not Found.", status=404)

    doc = entries_col.find_one({"_id": oid})
    return jsonify(entry_to_json(doc)), 200


@app.route("/api/entries/<entry_id>", methods=["DELETE"])
@jwt_required()
def delete_entry(entry_id):
    username = get_jwt_identity()
    try:
        oid = ObjectId(entry_id)
    except InvalidId:
        return validation_error("ERROR: Invalid Entry ID.", status=404)

    result = entries_col.delete_one({"_id": oid, "username": username})
    if result.deleted_count == 0:
        return validation_error("Entry Not Found.", status=404)

    return "", 204


#************************************************************************
# Goal Weight Routes (JWT Required)
#************************************************************************
@app.route("/api/goal", methods=["GET"])
@jwt_required()
def get_goal():
    username = get_jwt_identity()
    user = users_col.find_one({"username": username})
    goal = user.get("goal_weight") if user else None
    return jsonify({"goalWeight": goal}), 200


@app.route("/api/goal", methods=["PUT"])
@jwt_required()
def set_goal():
    username = get_jwt_identity()
    body = request.get_json(silent=True) or {}
    goal_weight = body.get("goalWeight")

    if not valid_weight(goal_weight):
        return validation_error("ERROR: Goal weight must be a number between 0 and 2000.")

    users_col.update_one(
        {"username": username}, {"$set": {"goal_weight": float(goal_weight)}}
    )
    return jsonify({"goalWeight": float(goal_weight)}), 200


#************************************************************************
# Error Handlers
# Never leak stack traces / internals to the client
#************************************************************************
@app.errorhandler(404)
def not_found(_e):
    return jsonify({"error": "Not Found"}), 404


@app.errorhandler(500)
def server_error(_e):
    return jsonify({"error": "Internal Server Error"}), 500


if __name__ == "__main__":
    # debug=False in anything resembling production
    # Host 0.0.0.0 so the Android Emulator (10.0.2.2) or a physical device
    # on the same network can reach it.
    app.run(host="0.0.0.0", port=5000, debug=True)