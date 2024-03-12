from flask import Response, jsonify


def response_with_data(data: dict) -> tuple[Response, int]:
    return (
        jsonify(
            {
                "success": True,
                "data": data,
            }
        ),
        200,
    )


def response_with_error(
    error: str = "Bad Request", status_code: int = 400
) -> tuple[Response, int]:
    return (
        jsonify(
            {
                "success": False,
                "message": str(error),
            }
        ),
        status_code,
    )
