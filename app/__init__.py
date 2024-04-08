from flask import Blueprint

suggestions_bp = Blueprint("suggestions", __name__, url_prefix="/api/v1/suggestions")
