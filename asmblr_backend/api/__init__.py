"""API package for asmblr_backend."""

from flask import Flask
from .health import health_bp
from .commands import commands_bp
from .system import system_bp
from .geolipi import geolipi_bp
from .sysl import sysl_bp
from .migumi import migumi_bp

# Optional: decor_gumi module (only if decor_gumi package is installed)
try:
    from .decor_gumi import decorgumi_bp
    DECOR_GUMI_AVAILABLE = True
except ImportError:
    DECOR_GUMI_AVAILABLE = False
    decorgumi_bp = None


def register_blueprints(app: Flask):
    """Register all API blueprints."""
    app.register_blueprint(health_bp)
    app.register_blueprint(commands_bp)
    app.register_blueprint(system_bp)
    app.register_blueprint(geolipi_bp)
    app.register_blueprint(sysl_bp)
    app.register_blueprint(migumi_bp)
    
    # Register optional blueprints
    if DECOR_GUMI_AVAILABLE:
        app.register_blueprint(decorgumi_bp)
        print("[asmblr_backend] DecorGumi API enabled")
    else:
        print("[asmblr_backend] DecorGumi API disabled (decor_gumi package not installed)")
