from app import suggestions_bp
from seeders import seeders_bp
from utils import get_instance
from utils.environment import Env

if __name__ == "__main__":
    # Get the app instance
    app, _ = get_instance()

    # Register blueprints
    app.register_blueprint(suggestions_bp)
    app.register_blueprint(seeders_bp)

    # Run the app
    app.run(
        debug=(Env.FLASK_ENV != "production"),
        port=8081,
        threaded=True,
    )
