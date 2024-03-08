import os

from dotenv import load_dotenv


class env(object):
    load_dotenv()

    SERVER_DEBUG = bool(os.environ.get("SERVER_DEBUG", False))

    SERVER_PRIVATE_KEY = os.environ.get("SERVER_PRIVATE_KEY")
