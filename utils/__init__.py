import jwt
import psycopg2
from flask import Flask, Request
from flask_cors import CORS

from utils.environment import Env

app = None


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(
        app,
        origins=Env.MOBILE_APP_URL,
        allow_headers=["Content-Type", "Authorization"],
        supports_credentials=True,
    )
    return app


def get_app() -> Flask:
    global app
    if app:
        return app

    app = create_app()
    return app


def get_db_connection():
    return psycopg2.connect(Env.DATABASE_URI)


def get_session(request: Request) -> dict | None:
    authorization = request.headers.get("Authorization", "").split(" ")[1]

    return (
        jwt.decode(authorization, Env.JWT_SECRET_KEY, algorithms=["HS256"])
        if authorization
        else None
    )
