"""
Configuration settings for AASX Digital Twin Analytics Framework
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application settings
    app_name: str = "AASX Digital Twin Analytics Framework"
    app_version: str = "1.0.0"
    debug: bool = False
    app_env: str = "development"
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    workers: int = 1
    
    # Database settings
    database_url: Optional[str] = None
    
    # Neo4j settings
    neo4j_uri: str = "neo4j://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "Neo4j123"
    neo4j_database: str = "neo4j"
    neo4j_port: str = "7687"
    
    # Qdrant settings
    qdrant_host: str = "localhost"
    qdrant_port: str = "6333"
    qdrant_url: str = "http://localhost:6333"
    
    # Redis settings
    redis_url: str = "redis://localhost:6379"
    
    # AI API settings
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None
    
    # CORS settings
    allowed_origins: list = ["*"]
    allowed_methods: list = ["*"]
    allowed_headers: list = ["*"]
    allowed_hosts: str = "localhost,127.0.0.1"
    
    # File upload settings
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    upload_dir: str = "uploads"
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # WebSocket settings
    websocket_ping_interval: int = 20
    websocket_ping_timeout: int = 20
    
    # Performance settings
    max_connections: int = 100
    timeout: int = 30
    
    # SSL/TLS settings
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    
    # Backup settings
    backup_enabled: bool = False
    backup_schedule: Optional[str] = None
    backup_retention_days: int = 7
    
    # Monitoring settings
    monitoring_enabled: bool = False
    metrics_endpoint: str = "/metrics"
    access_log: bool = True
    
    # Module-specific settings
    aasx_enabled: bool = True
    ai_rag_enabled: bool = True
    twin_registry_enabled: bool = True
    certificate_manager_enabled: bool = True

    kg_neo4j_enabled: bool = True
    federated_learning_enabled: bool = True
    physics_modeling_enabled: bool = True
    
    class Config:
        env_file = None  # We'll handle this manually
        case_sensitive = False


def get_env_file() -> str:
    """Determine which .env file to use based on environment"""
    env = os.getenv('NODE_ENV', 'development').lower()
    
    if env == 'production':
        return 'production.env'
    else:
        return 'local.env'


# Load environment variables from the appropriate .env file
env_file = get_env_file()
if os.path.exists(env_file):
    from dotenv import load_dotenv
    load_dotenv(env_file)
    print(f"✅ Loaded environment from {env_file}")
else:
    print(f"⚠️  Environment file {env_file} not found, using defaults")

# Global settings instance
settings = Settings()

# Set default SECRET_KEY for development if not provided
if not os.environ.get('SECRET_KEY'):
    os.environ['SECRET_KEY'] = settings.secret_key 