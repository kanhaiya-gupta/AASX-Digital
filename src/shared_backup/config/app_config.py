"""
Application Configuration
========================

Application settings and configuration for the AAS Data Modeling framework.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

@dataclass
class AppConfig:
    """Application configuration settings."""
    
    # Application metadata
    app_name: str = "AAS Data Modeling Framework"
    app_version: str = "1.0.0"
    app_description: str = "Asset Administration Shell Data Modeling and Processing Framework"
    
    # Environment
    environment: str = "development"  # development, testing, production
    debug: bool = True
    
    # Server settings
    host: str = "127.0.0.1"
    port: int = 8000
    workers: int = 1
    
    # API settings
    api_prefix: str = "/api/v1"
    cors_origins: List[str] = field(default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"])
    cors_allow_credentials: bool = True
    
    # Security settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # File upload settings
    upload_folder: str = "uploads"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: List[str] = field(default_factory=lambda: ['.aasx', '.aas', '.xml', '.json', '.zip'])
    
    # Processing settings
    max_concurrent_processes: int = 4
    processing_timeout: int = 300  # 5 minutes
    temp_folder: str = "temp"
    
    # Logging settings
    log_level: str = "INFO"
    log_file: str = "logs/aas_data_modeling.log"
    error_log_file: str = "logs/errors.log"
    enable_console_logging: bool = True
    enable_file_logging: bool = True
    enable_json_logging: bool = False
    
    # Cache settings
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour
    cache_max_size: int = 1000
    
    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hour
    
    # Monitoring
    health_check_enabled: bool = True
    metrics_enabled: bool = True
    profiling_enabled: bool = False
    
    @classmethod
    def from_environment(cls) -> 'AppConfig':
        """Create configuration from environment variables."""
        return cls(
            app_name=os.getenv('APP_NAME', 'AAS Data Modeling Framework'),
            app_version=os.getenv('APP_VERSION', '1.0.0'),
            app_description=os.getenv('APP_DESCRIPTION', 'Asset Administration Shell Data Modeling and Processing Framework'),
            environment=os.getenv('ENVIRONMENT', 'development'),
            debug=os.getenv('DEBUG', 'true').lower() == 'true',
            host=os.getenv('HOST', '127.0.0.1'),
            port=int(os.getenv('PORT', '8000')),
            workers=int(os.getenv('WORKERS', '1')),
            api_prefix=os.getenv('API_PREFIX', '/api/v1'),
            cors_origins=os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(','),
            cors_allow_credentials=os.getenv('CORS_ALLOW_CREDENTIALS', 'true').lower() == 'true',
            secret_key=os.getenv('SECRET_KEY', 'your-secret-key-change-in-production'),
            algorithm=os.getenv('ALGORITHM', 'HS256'),
            access_token_expire_minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30')),
            refresh_token_expire_days=int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', '7')),
            upload_folder=os.getenv('UPLOAD_FOLDER', 'uploads'),
            max_file_size=int(os.getenv('MAX_FILE_SIZE', str(100 * 1024 * 1024))),
            allowed_extensions=os.getenv('ALLOWED_EXTENSIONS', '.aasx,.aas,.xml,.json,.zip').split(','),
            max_concurrent_processes=int(os.getenv('MAX_CONCURRENT_PROCESSES', '4')),
            processing_timeout=int(os.getenv('PROCESSING_TIMEOUT', '300')),
            temp_folder=os.getenv('TEMP_FOLDER', 'temp'),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            log_file=os.getenv('LOG_FILE', 'logs/aas_data_modeling.log'),
            error_log_file=os.getenv('ERROR_LOG_FILE', 'logs/errors.log'),
            enable_console_logging=os.getenv('ENABLE_CONSOLE_LOGGING', 'true').lower() == 'true',
            enable_file_logging=os.getenv('ENABLE_FILE_LOGGING', 'true').lower() == 'true',
            enable_json_logging=os.getenv('ENABLE_JSON_LOGGING', 'false').lower() == 'true',
            cache_enabled=os.getenv('CACHE_ENABLED', 'true').lower() == 'true',
            cache_ttl=int(os.getenv('CACHE_TTL', '3600')),
            cache_max_size=int(os.getenv('CACHE_MAX_SIZE', '1000')),
            rate_limit_enabled=os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true',
            rate_limit_requests=int(os.getenv('RATE_LIMIT_REQUESTS', '100')),
            rate_limit_window=int(os.getenv('RATE_LIMIT_WINDOW', '3600')),
            health_check_enabled=os.getenv('HEALTH_CHECK_ENABLED', 'true').lower() == 'true',
            metrics_enabled=os.getenv('METRICS_ENABLED', 'true').lower() == 'true',
            profiling_enabled=os.getenv('PROFILING_ENABLED', 'false').lower() == 'true'
        )
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        # Validate environment
        if self.environment not in ['development', 'testing', 'production']:
            raise ValueError(f"Invalid environment: {self.environment}")
        
        # Validate port
        if not (1 <= self.port <= 65535):
            raise ValueError(f"Invalid port: {self.port}")
        
        # Validate workers
        if self.workers < 1:
            raise ValueError(f"Invalid workers count: {self.workers}")
        
        # Validate file size
        if self.max_file_size <= 0:
            raise ValueError(f"Invalid max file size: {self.max_file_size}")
        
        # Validate timeouts
        if self.processing_timeout <= 0:
            raise ValueError(f"Invalid processing timeout: {self.processing_timeout}")
        
        # Validate cache settings
        if self.cache_ttl <= 0:
            raise ValueError(f"Invalid cache TTL: {self.cache_ttl}")
        
        if self.cache_max_size <= 0:
            raise ValueError(f"Invalid cache max size: {self.cache_max_size}")
        
        # Validate rate limiting
        if self.rate_limit_requests <= 0:
            raise ValueError(f"Invalid rate limit requests: {self.rate_limit_requests}")
        
        if self.rate_limit_window <= 0:
            raise ValueError(f"Invalid rate limit window: {self.rate_limit_window}")
        
        return True
    
    def create_directories(self) -> None:
        """Create necessary directories."""
        directories = [
            self.upload_folder,
            self.temp_folder,
            Path(self.log_file).parent,
            Path(self.error_log_file).parent
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins as a list."""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(',')]
        return self.cors_origins
    
    def get_allowed_extensions(self) -> List[str]:
        """Get allowed file extensions as a list."""
        if isinstance(self.allowed_extensions, str):
            return [ext.strip() for ext in self.allowed_extensions.split(',')]
        return self.allowed_extensions
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'app_name': self.app_name,
            'app_version': self.app_version,
            'app_description': self.app_description,
            'environment': self.environment,
            'debug': self.debug,
            'host': self.host,
            'port': self.port,
            'workers': self.workers,
            'api_prefix': self.api_prefix,
            'cors_origins': self.get_cors_origins(),
            'cors_allow_credentials': self.cors_allow_credentials,
            'secret_key': '***' if self.secret_key != 'your-secret-key-change-in-production' else self.secret_key,
            'algorithm': self.algorithm,
            'access_token_expire_minutes': self.access_token_expire_minutes,
            'refresh_token_expire_days': self.refresh_token_expire_days,
            'upload_folder': self.upload_folder,
            'max_file_size': self.max_file_size,
            'allowed_extensions': self.get_allowed_extensions(),
            'max_concurrent_processes': self.max_concurrent_processes,
            'processing_timeout': self.processing_timeout,
            'temp_folder': self.temp_folder,
            'log_level': self.log_level,
            'log_file': self.log_file,
            'error_log_file': self.error_log_file,
            'enable_console_logging': self.enable_console_logging,
            'enable_file_logging': self.enable_file_logging,
            'enable_json_logging': self.enable_json_logging,
            'cache_enabled': self.cache_enabled,
            'cache_ttl': self.cache_ttl,
            'cache_max_size': self.cache_max_size,
            'rate_limit_enabled': self.rate_limit_enabled,
            'rate_limit_requests': self.rate_limit_requests,
            'rate_limit_window': self.rate_limit_window,
            'health_check_enabled': self.health_check_enabled,
            'metrics_enabled': self.metrics_enabled,
            'profiling_enabled': self.profiling_enabled
        }

class AppConfigManager:
    """Manager for application configurations."""
    
    # Default configurations for different environments
    DEFAULT_CONFIGS = {
        'development': AppConfig(
            environment='development',
            debug=True,
            host='127.0.0.1',
            port=8000,
            workers=1,
            log_level='DEBUG',
            enable_console_logging=True,
            enable_file_logging=True,
            profiling_enabled=True
        ),
        'testing': AppConfig(
            environment='testing',
            debug=True,
            host='127.0.0.1',
            port=8001,
            workers=1,
            log_level='DEBUG',
            enable_console_logging=False,
            enable_file_logging=False,
            cache_enabled=False,
            rate_limit_enabled=False
        ),
        'production': AppConfig(
            environment='production',
            debug=False,
            host='0.0.0.0',
            port=8000,
            workers=4,
            log_level='INFO',
            enable_console_logging=False,
            enable_file_logging=True,
            enable_json_logging=True,
            cache_enabled=True,
            rate_limit_enabled=True,
            health_check_enabled=True,
            metrics_enabled=True,
            profiling_enabled=False
        )
    }
    
    @classmethod
    def get_config(cls, environment: str = None) -> AppConfig:
        """Get application configuration for the specified environment."""
        if environment is None:
            environment = os.getenv('ENVIRONMENT', 'development')
        
        # Try to get from environment variables first
        try:
            config = AppConfig.from_environment()
            config.validate()
            config.create_directories()
            return config
        except (ValueError, TypeError) as e:
            print(f"Error loading config from environment: {e}")
        
        # Fall back to default configurations
        if environment in cls.DEFAULT_CONFIGS:
            config = cls.DEFAULT_CONFIGS[environment]
            config.validate()
            config.create_directories()
            return config
        
        # Fall back to development configuration
        config = cls.DEFAULT_CONFIGS['development']
        config.validate()
        config.create_directories()
        return config
    
    @classmethod
    def get_test_config(cls) -> AppConfig:
        """Get configuration for testing."""
        return cls.get_config('testing')
    
    @classmethod
    def get_development_config(cls) -> AppConfig:
        """Get configuration for development."""
        return cls.get_config('development')
    
    @classmethod
    def get_production_config(cls) -> AppConfig:
        """Get configuration for production."""
        return cls.get_config('production')

# Convenience functions
def get_app_config(environment: str = None) -> AppConfig:
    """Get application configuration."""
    return AppConfigManager.get_config(environment)

def get_test_app_config() -> AppConfig:
    """Get test application configuration."""
    return AppConfigManager.get_test_config()

def get_development_app_config() -> AppConfig:
    """Get development application configuration."""
    return AppConfigManager.get_development_config()

def get_production_app_config() -> AppConfig:
    """Get production application configuration."""
    return AppConfigManager.get_production_config() 