from data import data_bp
from recommend import recommend_bp
from seeder import seed_bp
from utils import get_instance
from utils.environment import Env

if __name__ == "__main__":
    # Get the app instance
    app, _ = get_instance()

    # Register blueprints
    app.register_blueprint(data_bp)
    app.register_blueprint(seed_bp)
    app.register_blueprint(recommend_bp)

    # Run the app
    app.run(
        debug=(Env.FLASK_ENV != "production"),
        port=8081,
        threaded=True,
    )
