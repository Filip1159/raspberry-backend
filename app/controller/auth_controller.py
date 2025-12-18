from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
import json
import jwt
from jwcrypto import jwk

from app.secret_provider import get_keys


auth = Blueprint("auth", __name__)

private_pem, public_pem = get_keys()

public_key_jwk = jwk.JWK.from_pem(public_pem)
public_jwk_json = json.loads(public_key_jwk.export_public())
kid = public_jwk_json["kid"]


@auth.route("/.well-known/jwks.json")
def jwks():
    return jsonify({"keys": [public_jwk_json]})


@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if username != "admin" or password != "1234":
        return jsonify({"msg": "bad credentials"}), 401

    return prepare_token(username)


def prepare_token(username):
    now = datetime.utcnow()
    exp = now + timedelta(hours=12)

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

    token = jwt.encode(payload, private_pem, algorithm="RS256", headers=headers)

    return jsonify({
        "access_token": token,
        "expires_at": exp.isoformat()
    })
