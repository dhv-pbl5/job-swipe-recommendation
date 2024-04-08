from flask import jsonify

from utils.environment import Env


def response_with_data(data):
    """
    Create a JSON response with the provided data.

    Args:
        data: The data to be included in the response.

    Returns:
        A JSON response containing the provided data and a success status code (200).
    """
    return jsonify({"success": True, "data": data}), 200


def response_with_error(
    message: str = "400 Bad Request", status_code: int = 400, error=""
):
    """
    Create a response object with an error message.

    Args:
        message (str, optional): The error message to include in the response. Defaults to "400 Bad Request".
        status_code (int, optional): The HTTP status code to include in the response. Defaults to 400.
        error (str, optional): Additional error information to include in the response. Defaults to "".

    Returns:
        tuple: A tuple containing the JSON response object and the HTTP status code.
    """
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
