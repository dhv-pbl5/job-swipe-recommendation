from app import sugg_bp
from utils import get_app
from utils.environment import Env

app = get_app()

app.register_blueprint(sugg_bp)


if __name__ == "__main__":
    app.run(
        debug=(Env.FLASK_ENV != "production"),
        port=5000,
        threaded=True,
        host=Env.FLASK_HOST,
    )
