from routes.normalize import normalize_bp
from routes.recommend import recommend_bp
from seed import seed_bp
from utils import get_instance
from utils.environment import Env

app, _ = get_instance()

app.register_blueprint(seed_bp)
app.register_blueprint(recommend_bp)
app.register_blueprint(normalize_bp)

if __name__ == "__main__":
    app.run(
        debug=(Env.FLASK_ENV == "development"),
        port=Env.FLASK_PORT,
        threaded=True,
    )
