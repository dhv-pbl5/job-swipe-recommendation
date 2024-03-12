import jwt
from flask import Flask, Request, jsonify
from flask_cors import CORS

from utils.env import env

app = None


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(
        app,
        origins=env.FLASK_HOST,
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


def get_session(request: Request) -> dict | None:
    authorization = request.headers.get("Authorization", "").split(" ")[1]

    if not authorization:
        return None
    else:
        return jwt.decode(authorization, env.JWT_SECRET_KEY, algorithms=["HS256"])


def response_with_data(data: dict):
    return (
        jsonify(
            {
                "success": True,
                "data": data,
            }
        ),
        200,
    )


def response_with_error(error: str = "Bad Request", status_code: int = 400):
    return (
        jsonify(
            {
                "success": False,
                "message": str(error),
            }
        ),
        status_code,
    )
