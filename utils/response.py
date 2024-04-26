from flask import jsonify

from utils import log_prefix


def response_with_data(data, message="200 Success", status_code=200):
    return (
        jsonify({"success": True, "data": data, "message": message}),
        status_code,
    )


def response_with_message(message="200 Success", status_code=200):
    return jsonify({"success": True, "message": message}), status_code


def response_with_error(file, message="400 Bad Request", status_code=400, error=None):
    if error:
        print(log_prefix(__file__), error)

    return jsonify({"success": False, "message": message}), status_code
