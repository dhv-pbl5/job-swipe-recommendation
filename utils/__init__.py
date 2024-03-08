from flask import Flask
from flask_cors import CORS

app = None


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)
    return app


def get_app() -> Flask:
    global app
    if app:
        return app

    app = create_app()
    return app
