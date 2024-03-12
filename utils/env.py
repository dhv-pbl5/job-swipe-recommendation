import os

from dotenv import find_dotenv, load_dotenv


class env(object):
    load_dotenv(find_dotenv())

    FLASK_HOST = os.environ.get("FLASK_HOST", "localhost").lower()
    FLASK_ENV = os.environ.get("FLASK_ENV", "development").lower()

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
