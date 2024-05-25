from data import data_bp
from recommend import recommend_bp
from seed import seed_bp
from utils import get_instance
from utils.environment import Env

app, _ = get_instance()

app.register_blueprint(data_bp)
app.register_blueprint(seed_bp)
app.register_blueprint(recommend_bp)

if __name__ == "__main__":
    app.run(
        debug=False if Env.FLASK_ENV == "production" else True, port=8081, threaded=True
    )
