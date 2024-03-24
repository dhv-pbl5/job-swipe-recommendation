from flask import request

from utils import get_app
from utils.environment import Env
from utils.response import response_with_error

app = get_app()


@app.before_request
def authenticate():
    authorization = request.headers.get("Authorization")

    if (not authorization) or ("Bearer" not in authorization):
        return response_with_error("Unauthorized", 401)


if __name__ == "__main__":
    app.run(
        debug=(Env.FLASK_ENV != "production"),
        port=5000,
        threaded=True,
        host=Env.FLASK_HOST,
    )
