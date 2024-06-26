import os

from dotenv import find_dotenv, load_dotenv


class Env:
    load_dotenv(find_dotenv())

    FLASK_HOST = os.environ.get("FLASK_HOST", "localhost").lower()
    FLASK_ENV = os.environ.get("FLASK_ENV", "development").lower()

    FLASK_PASSWORD = os.environ.get("FLASK_PASSWORD", "example-password")
    MOBILE_APP_URL = os.environ.get("MOBILE_APP_URL", "localhost").lower()
    DATABASE_URI = os.environ.get("DATABASE_URI", "")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "example-secret-key")
    DEFAULT_PASSWORD = os.environ.get("DEFAULT_PASSWORD", "example-password")
