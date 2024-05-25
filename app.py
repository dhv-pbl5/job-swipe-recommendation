from data import data_bp
from recommend import recommend_bp
from seed import seed_bp
from utils import get_instance
from utils.environment import Env

if __name__ == "__main__":
    # Get the app instance
    app, _ = get_instance()

    # Register blueprints
    app.register_blueprint(data_bp)
    app.register_blueprint(seed_bp)
    app.register_blueprint(recommend_bp)

    if Env.FLASK_ENV == "production":
        app.run(debug=False, port=8081, threaded=True)
    else:
        app.run(debug=True, port=8081, threaded=True)
