from flask import jsonify

from utils.environment import Env


def response_with_data(data):
    return jsonify({"success": True, "data": data}), 200


def response_with_error(
    message: str = "400 Bad Request", status_code: int = 400, error=""
):
    if Env.FLASK_ENV == "development":
        return (
            jsonify({"success": False, "message": message, "error": str(error)}),
            status_code,
        )
    else:
        return (
            jsonify({"success": False, "message": message}),
            status_code,
        )
