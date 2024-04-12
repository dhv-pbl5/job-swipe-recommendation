from flask import jsonify


def response_with_data(data="", message="200 Success", status_code=200):
    return (
        jsonify({"success": True, "data": data, "message": message}),
        status_code,
    )


def response_with_error(message="400 Bad Request", status_code=400):
    return jsonify({"success": False, "message": message}), status_code
