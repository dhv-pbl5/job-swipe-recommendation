import jwt
import psycopg2
from flask import Flask, Request
from flask_cors import CORS

from utils.environment import Env

app = None


def create_app() -> Flask:
    """
    Create and configure the Flask application.

    Returns:
        Flask: The configured Flask application.
    """
    app = Flask(__name__)
    CORS(
        app,
        origins=Env.MOBILE_APP_URL,
        allow_headers=["Content-Type", "Authorization"],
        supports_credentials=True,
    )
    return app


def get_app() -> Flask:
    """
    Get the Flask application instance.

    Returns:
        Flask: The Flask application instance.
    """
    global app
    if app:
        return app

    app = create_app()
    return app


import psycopg2


def get_db_connection():
    """
    Establishes a connection to the database.

    Returns:
        psycopg2.extensions.connection: The database connection object.
    """
    return psycopg2.connect(Env.DATABASE_URI)


def get_session(request: Request):
    """
    Retrieves the session ID from the request's Authorization header.

    Args:
        request (Request): The request object containing the Authorization header.

    Returns:
        str or None: The session ID if it exists in the database, otherwise None.
    """
    authorization = request.headers.get("Authorization", "").split(" ")[1]

    if not authorization:
        return None

    payload = jwt.decode(authorization, Env.JWT_SECRET_KEY, algorithms=["HS256"])

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT refresh_token FROM accounts WHERE account_id = %s", payload["accountId"]
    )
    record = cur.fetchone()
    conn.close()
    return payload["accountId"] if record else None
