from flask import request

from utils import get_app, response_with_error
from utils.env import env

app = get_app()


@app.before_request
def authenticate():
    authorization = request.headers.get("Authorization")

    if (not authorization) or ("Bearer" not in authorization):
        return response_with_error("Unauthorized", 401)


if __name__ == "__main__":
    app.run(
        debug=True if env.FLASK_ENV != "production" else False,
        port=5000,
        threaded=True,
        host=env.FLASK_HOST,
    )
