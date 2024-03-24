from flask import jsonify


def response_with_data(data):
    return (
        jsonify(
            {
                "success": True,
                "data": data,
            }
        ),
        200,
    )


def response_with_error(error="Bad Request", status_code: int = 400):
    return (
        jsonify(
            {
                "success": False,
                "message": str(error),
            }
        ),
        status_code,
    )
