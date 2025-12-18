from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, send, emit
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
import logging

import jwt
from jwcrypto import jwk
import json
import os
import datetime

from servos_controller import ServosController


servos = ServosController(0, 1)

KEY_PRIVATE_PATH = "private_key.pem"
KEY_PUBLIC_PATH = "public_key.pem"

if not (os.path.exists(KEY_PRIVATE_PATH) and os.path.exists(KEY_PUBLIC_PATH)):
    raise FileNotFoundError("Brakuje private_key.pem lub public_key.pem!")

with open(KEY_PRIVATE_PATH, "rb") as f:
    private_pem = f.read()

with open(KEY_PUBLIC_PATH, "rb") as f:
    public_pem = f.read()

public_key_jwk = jwk.JWK.from_pem(public_pem)

public_jwk_json = json.loads(public_key_jwk.export_public())
kid = public_jwk_json["kid"]

app = Flask('rpi_server')

app.config["JWT_ALGORITHM"] = "RS256"
app.config["JWT_PUBLIC_KEY"] = open(KEY_PUBLIC_PATH).read()


jwt_manager = JWTManager(app)

CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/.well-known/jwks.json")
def jwks():
    return jsonify({"keys": [public_jwk_json]})


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if username != "admin" or password != "1234":
        return jsonify({"msg": "bad credentials"}), 401

    now = datetime.datetime.utcnow()
    exp = now + datetime.timedelta(hours=12)

    permissions = [
        {"action": "publish", "path": "cam1"},
        {"action": "read", "path": "cam1"}
    ]

    payload = {
        "sub": username,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "mediamtx_permissions": permissions
    }

    headers = {
        "kid": kid,
        "alg": "RS256",
        "typ": "JWT"
    }

    token = jwt.encode(
        payload,
        private_pem,
        algorithm="RS256",
        headers=headers
    )

    return jsonify({
        "access_token": token,
        "expires_at": exp.isoformat()
    })


@app.route("/alarms", methods=["POST"])
@jwt_required()
def set_alarms():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({"error": "Body must be a list"}), 400

    for index, item in enumerate(data):
        if not isinstance(item, dict):
            return jsonify({"error": f"Item at index {index} is not an object"}), 400

        day = item.get("day")
        hour = item.get("hour")
        minute = item.get("minute")

        if day not in ALLOWED_DAYS:
            return jsonify({"error": f"Invalid day at index {index}"}), 400

        if not isinstance(hour, int) or not (0 <= hour <= 23):
            return jsonify({"error": f"Invalid hour at index {index}"}), 400

        if not isinstance(minute, int) or not (0 <= minute <= 59):
            return jsonify({"error": f"Invalid minute at index {index}"}), 400

    with open("alarms.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    return 200


@app.route("/alarms", methods=["GET"])
@jwt_required()
def get_alarms():
    with open("alarms.json", "r", encoding="utf-8") as file:
        print('file opened')
        c = file.read()
        print(c)
        return c, 200


@jwt_manager.unauthorized_loader
def unauthorized(reason):
    return jsonify(error="unauthorized", reason=reason), 401

@jwt_manager.invalid_token_loader
def invalid(reason):
    return jsonify(error="invalid_token", reason=reason), 422

@jwt_manager.expired_token_loader
def expired(jwt_header, jwt_payload):
    return jsonify(error="token_expired"), 401

@jwt_manager.needs_fresh_token_loader
def fresh_required(jwt_header, jwt_payload):
    return jsonify(error="fresh_token_required"), 401


@socketio.on('connect')
def handle_connect():
    print('Client connected')
    send('Connected to Flask SocketIO server!')

@socketio.on('message')
def handle_message(msg):
    global servos
    servos.move(msg)

def server_loop(queue):
    try:
        message = queue.get(timeout=0.5)
        socketio.emit('message', message)
    except:
        pass


def run_server():
    socketio.run(app, host='0.0.0.0', port=8080, allow_unsafe_werkzeug=True)  # DO NOT USE debug=True https://stackoverflow.com/questions/77707533/busy-gpios-raspberry-pi5
