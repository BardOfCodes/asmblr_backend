"""
Flask backend for command execution.
Organized with blueprints for different API types.
"""

from flask import Flask
from flask_cors import CORS
from asmblr_backend.api import register_blueprints


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # CORS configuration
    # WARNING: In production, replace "*" with specific allowed origins
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=True,
    )

    register_blueprints(app)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
