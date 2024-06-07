from flask import Blueprint

from utils import get_instance

_, db = get_instance()

prepare_bp = Blueprint("prepare", __name__, url_prefix="/api/v1/prepare")
