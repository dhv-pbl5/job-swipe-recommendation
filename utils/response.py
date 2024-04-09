from flask import jsonify

from utils.environment import Env


def response_with_data(data="", status_code=200, message=""):
    response = {
        "success": True,
    }

    if message:
        response["message"] = message

    if data:
        response["data"] = data

    return jsonify(response), status_code


def response_with_error(message="400 Bad Request", status_code=400, error=""):
    if error and Env.FLASK_ENV == "development":
        print("Exception caught:", error)

    return (
        jsonify(
            {
                "success": False,
                "message": message,
            }
        ),
        status_code,
    )
