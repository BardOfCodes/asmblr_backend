"""System information endpoints."""

import os
import platform
from flask import Blueprint, jsonify

system_bp = Blueprint('system', __name__, url_prefix='/api/system')

@system_bp.route('/info')
def info():
    """Get basic system information."""
    return jsonify({
        'platform': platform.system(),
        'release': platform.release(),
        'python_version': platform.python_version(),
        'cwd': os.getcwd(),
        'user': os.environ.get('USER', 'unknown')
    })

@system_bp.route('/env')
def environment():
    """Get safe environment variables."""
    safe_vars = ['PATH', 'HOME', 'USER', 'SHELL', 'PYTHONPATH']
    env = {var: os.environ.get(var) for var in safe_vars if var in os.environ}
    return jsonify(env)