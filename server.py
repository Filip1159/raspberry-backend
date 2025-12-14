from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, send, emit
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)

import jwt
from jwcrypto import jwk
import json
import os

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

app.config["JWT_SECRET_KEY"] = "super-secret-key"
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
