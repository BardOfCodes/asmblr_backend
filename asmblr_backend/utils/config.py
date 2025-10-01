"""
Configuration management for asmblr_backend.
"""

import os
from typing import Dict, Any


class Config:
    """Base configuration class."""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    # Server configuration
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 5002))
    
    # API configuration
    API_VERSION = 'v1'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size
    
    # CORS configuration
    CORS_ORIGINS = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:3001',
        'http://127.0.0.1:3001'
    ]
    
    # Command execution configuration
    COMMAND_TIMEOUT = int(os.environ.get('COMMAND_TIMEOUT', 300))  # 5 minutes default
    MAX_CONCURRENT_COMMANDS = int(os.environ.get('MAX_CONCURRENT_COMMANDS', 5))
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """Get configuration as dictionary for logging/debugging."""
        return {
            'DEBUG': cls.DEBUG,
            'HOST': cls.HOST,
            'PORT': cls.PORT,
            'API_VERSION': cls.API_VERSION,
            'COMMAND_TIMEOUT': cls.COMMAND_TIMEOUT,
            'MAX_CONCURRENT_COMMANDS': cls.MAX_CONCURRENT_COMMANDS
        }


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'production-secret-key-required'
    
    
class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True


# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
