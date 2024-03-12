from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from utils import get_app

db = None


def get_db():
    global db
    if db:
        return db

    class Base(DeclarativeBase):
        pass

    db = SQLAlchemy(app=get_app(), model_class=Base)
    return db
