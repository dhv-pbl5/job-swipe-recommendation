from flask import jsonify

from utils.environment import Env


def response_with_data(data):
    response = {
        "success": True,
        "data": data,
    }
    return jsonify(response), 200


def response_with_error(
    message: str = "400 Bad Request", status_code: int = 400, error=None
):
    if Env.FLASK_ENV == "development":
        print(error)

    response = {
        "success": False,
        "message": message,
    }
    return jsonify(response), status_code
