from utils import get_app
from utils.env import env

app = get_app()

if __name__ == "__main__":
    app.run(debug=env.SERVER_DEBUG, port=5000, threaded=True)
