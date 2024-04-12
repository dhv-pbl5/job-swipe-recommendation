from random import randint

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from utils.environment import Env

app = None
db = None


def create_app() -> tuple[Flask, SQLAlchemy]:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = Env.DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    CORS(app)
    db = SQLAlchemy(app)
    return app, db


def get_instance() -> tuple[Flask, SQLAlchemy]:
    global db, app
    if app and db:
        return app, db

    app, db = create_app()
    return app, db


def fake_phone_numbers():
    return "0" + "".join(str(randint(0, 9)) for _ in range(9))
