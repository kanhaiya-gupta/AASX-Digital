"""
Application settings and configuration
"""

import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Src service URLs
    AI_RAG_URL = os.environ.get('AI_RAG_URL', 'http://localhost:8000')
    TWIN_REGISTRY_URL = os.environ.get('TWIN_REGISTRY_URL', 'http://localhost:8001')
    CERTIFICATE_MANAGER_URL = os.environ.get('CERTIFICATE_MANAGER_URL', 'http://localhost:3001')
    ANALYTICS_URL = os.environ.get('ANALYTICS_URL', 'http://localhost:3002')
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Pagination
    ITEMS_PER_PAGE = 20

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    def __init__(self):
        super().__init__()
        # Override with production settings
        self.SECRET_KEY = os.environ.get('SECRET_KEY')
        
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY must be set in production")

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
