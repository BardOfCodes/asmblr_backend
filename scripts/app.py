"""
Flask backend for command execution.
Organized with blueprints for different API types.
"""

from flask import Flask
from flask_cors import CORS
from asmblr_backend.api import register_blueprints

app = Flask(__name__)
CORS(app)

# Register all API blueprints
register_blueprints(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)