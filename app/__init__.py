from flask import Blueprint

sugg_bp = Blueprint("suggestions", __name__, url_prefix="/api/v1/suggestions")
