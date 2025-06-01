from flask import Flask

from src.routes.collection_routes import collection_bp
from src.database import init_app as init_db

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)

    # Initialize the database
    init_db(app)

    # Register Blueprints
    app.register_blueprint(collection_bp)

    @app.route('/')
    def hello_world():
        return 'Hello, MTG Collection API!'

    return app

if __name__ == '__main__':
    app = create_app()
    # Runs the app on 0.0.0.0 to be accessible from outside the container
    # and enables debug mode.
    app.run(debug=True, host='0.0.0.0', port=5000)
