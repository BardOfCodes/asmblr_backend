"""
Main Flask application entry point for asmblr_backend.
Uses blueprints for organized API routing and modular architecture.
"""

from flask import Flask
from flask_cors import CORS
import logging
import os
from asmblr_backend.api import register_blueprints
from asmblr_backend.utils.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS for React frontend
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Register all API blueprints
    register_blueprints(app)
    
    # Add error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Endpoint not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return {'error': 'Internal server error'}, 500
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    # Configuration
    PORT = int(os.environ.get('FLASK_PORT', 5002))  # Using 5002 to avoid conflicts
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    DEBUG = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    logger.info(f"Starting asmblr_backend Flask server on {HOST}:{PORT}")
    logger.info(f"Debug mode: {DEBUG}")
    logger.info(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    
    app.run(host=HOST, port=PORT, debug=DEBUG)
