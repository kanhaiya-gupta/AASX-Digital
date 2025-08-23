"""
Logging Configuration
===================

Logging configuration settings for the AAS Data Modeling framework.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    
    # Log levels
    root_level: str = "INFO"
    app_level: str = "INFO"
    database_level: str = "WARNING"
    security_level: str = "WARNING"
    api_level: str = "INFO"
    file_operations_level: str = "INFO"
    
    # File settings
    log_directory: str = "logs"
    main_log_file: str = "aas_data_modeling.log"
    error_log_file: str = "errors.log"
    access_log_file: str = "access.log"
    security_log_file: str = "security.log"
    
    # File rotation settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    rotation_when: str = "midnight"  # midnight, daily, hourly
    
    # Format settings
    console_format: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    file_format: str = "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(funcName)s(): %(message)s"
    json_format: bool = False
    
    # Output settings
    enable_console: bool = True
    enable_file: bool = True
    enable_colors: bool = True
    enable_json: bool = False
    
    # Performance settings
    disable_existing_loggers: bool = False
    propagate: bool = False
    
    @classmethod
    def from_environment(cls) -> 'LoggingConfig':
        """Create configuration from environment variables."""
        return cls(
            root_level=os.getenv('LOG_ROOT_LEVEL', 'INFO'),
            app_level=os.getenv('LOG_APP_LEVEL', 'INFO'),
            database_level=os.getenv('LOG_DATABASE_LEVEL', 'WARNING'),
            security_level=os.getenv('LOG_SECURITY_LEVEL', 'WARNING'),
            api_level=os.getenv('LOG_API_LEVEL', 'INFO'),
            file_operations_level=os.getenv('LOG_FILE_OPERATIONS_LEVEL', 'INFO'),
            log_directory=os.getenv('LOG_DIRECTORY', 'logs'),
            main_log_file=os.getenv('LOG_MAIN_FILE', 'aas_data_modeling.log'),
            error_log_file=os.getenv('LOG_ERROR_FILE', 'errors.log'),
            access_log_file=os.getenv('LOG_ACCESS_FILE', 'access.log'),
            security_log_file=os.getenv('LOG_SECURITY_FILE', 'security.log'),
            max_file_size=int(os.getenv('LOG_MAX_FILE_SIZE', str(10 * 1024 * 1024))),
            backup_count=int(os.getenv('LOG_BACKUP_COUNT', '5')),
            rotation_when=os.getenv('LOG_ROTATION_WHEN', 'midnight'),
            console_format=os.getenv('LOG_CONSOLE_FORMAT', '%(asctime)s [%(levelname)s] %(name)s: %(message)s'),
            file_format=os.getenv('LOG_FILE_FORMAT', '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(funcName)s(): %(message)s'),
            json_format=os.getenv('LOG_JSON_FORMAT', 'false').lower() == 'true',
            enable_console=os.getenv('LOG_ENABLE_CONSOLE', 'true').lower() == 'true',
            enable_file=os.getenv('LOG_ENABLE_FILE', 'true').lower() == 'true',
            enable_colors=os.getenv('LOG_ENABLE_COLORS', 'true').lower() == 'true',
            enable_json=os.getenv('LOG_ENABLE_JSON', 'false').lower() == 'true',
            disable_existing_loggers=os.getenv('LOG_DISABLE_EXISTING_LOGGERS', 'false').lower() == 'true',
            propagate=os.getenv('LOG_PROPAGATE', 'false').lower() == 'true'
        )
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        for level_name, level_value in [
            ('root_level', self.root_level),
            ('app_level', self.app_level),
            ('database_level', self.database_level),
            ('security_level', self.security_level),
            ('api_level', self.api_level),
            ('file_operations_level', self.file_operations_level)
        ]:
            if level_value not in valid_levels:
                raise ValueError(f"Invalid log level for {level_name}: {level_value}")
        
        valid_rotation_when = ['midnight', 'daily', 'hourly']
        if self.rotation_when not in valid_rotation_when:
            raise ValueError(f"Invalid rotation_when: {self.rotation_when}")
        
        if self.max_file_size <= 0:
            raise ValueError(f"Invalid max_file_size: {self.max_file_size}")
        
        if self.backup_count < 0:
            raise ValueError(f"Invalid backup_count: {self.backup_count}")
        
        return True
    
    def create_log_directory(self) -> None:
        """Create log directory if it doesn't exist."""
        Path(self.log_directory).mkdir(parents=True, exist_ok=True)
    
    def get_log_file_path(self, filename: str) -> str:
        """Get full path for a log file."""
        return str(Path(self.log_directory) / filename)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'root_level': self.root_level,
            'app_level': self.app_level,
            'database_level': self.database_level,
            'security_level': self.security_level,
            'api_level': self.api_level,
            'file_operations_level': self.file_operations_level,
            'log_directory': self.log_directory,
            'main_log_file': self.main_log_file,
            'error_log_file': self.error_log_file,
            'access_log_file': self.access_log_file,
            'security_log_file': self.security_log_file,
            'max_file_size': self.max_file_size,
            'backup_count': self.backup_count,
            'rotation_when': self.rotation_when,
            'console_format': self.console_format,
            'file_format': self.file_format,
            'json_format': self.json_format,
            'enable_console': self.enable_console,
            'enable_file': self.enable_file,
            'enable_colors': self.enable_colors,
            'enable_json': self.enable_json,
            'disable_existing_loggers': self.disable_existing_loggers,
            'propagate': self.propagate
        }

class LoggingConfigManager:
    """Manager for logging configurations."""
    
    # Default configurations for different environments
    DEFAULT_CONFIGS = {
        'development': LoggingConfig(
            root_level='DEBUG',
            app_level='DEBUG',
            database_level='INFO',
            security_level='WARNING',
            api_level='INFO',
            file_operations_level='INFO',
            enable_console=True,
            enable_file=True,
            enable_colors=True,
            enable_json=False
        ),
        'testing': LoggingConfig(
            root_level='DEBUG',
            app_level='DEBUG',
            database_level='DEBUG',
            security_level='DEBUG',
            api_level='DEBUG',
            file_operations_level='DEBUG',
            enable_console=False,
            enable_file=False,
            enable_colors=False,
            enable_json=True
        ),
        'production': LoggingConfig(
            root_level='INFO',
            app_level='INFO',
            database_level='WARNING',
            security_level='WARNING',
            api_level='INFO',
            file_operations_level='INFO',
            enable_console=False,
            enable_file=True,
            enable_colors=False,
            enable_json=True,
            max_file_size=50 * 1024 * 1024,  # 50MB
            backup_count=10
        )
    }
    
    @classmethod
    def get_config(cls, environment: str = None) -> LoggingConfig:
        """Get logging configuration for the specified environment."""
        if environment is None:
            environment = os.getenv('ENVIRONMENT', 'development')
        
        # Try to get from environment variables first
        try:
            config = LoggingConfig.from_environment()
            config.validate()
            config.create_log_directory()
            return config
        except (ValueError, TypeError) as e:
            print(f"Error loading logging config from environment: {e}")
        
        # Fall back to default configurations
        if environment in cls.DEFAULT_CONFIGS:
            config = cls.DEFAULT_CONFIGS[environment]
            config.validate()
            config.create_log_directory()
            return config
        
        # Fall back to development configuration
        config = cls.DEFAULT_CONFIGS['development']
        config.validate()
        config.create_log_directory()
        return config
    
    @classmethod
    def create_yaml_config(cls, config: LoggingConfig, output_file: str = "logging_config.yaml") -> str:
        """Create YAML logging configuration file."""
        yaml_config = {
            'version': 1,
            'disable_existing_loggers': config.disable_existing_loggers,
            'formatters': {
                'standard': {
                    'format': config.console_format,
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
                'detailed': {
                    'format': config.file_format,
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
                'json': {
                    '()': 'src.shared.utils.logging_utils.JSONFormatter'
                }
            },
            'handlers': {},
            'loggers': {
                '': {  # Root logger
                    'handlers': [],
                    'level': config.root_level,
                    'propagate': config.propagate
                },
                'src.shared': {
                    'handlers': [],
                    'level': config.app_level,
                    'propagate': config.propagate
                },
                'webapp': {
                    'handlers': [],
                    'level': config.app_level,
                    'propagate': config.propagate
                },
                'database': {
                    'handlers': [],
                    'level': config.database_level,
                    'propagate': config.propagate
                },
                'security': {
                    'handlers': [],
                    'level': config.security_level,
                    'propagate': config.propagate
                },
                'api': {
                    'handlers': [],
                    'level': config.api_level,
                    'propagate': config.propagate
                },
                'file_operations': {
                    'handlers': [],
                    'level': config.file_operations_level,
                    'propagate': config.propagate
                }
            }
        }
        
        # Add console handler
        if config.enable_console:
            yaml_config['handlers']['console'] = {
                'class': 'logging.StreamHandler',
                'level': config.root_level,
                'formatter': 'json' if config.enable_json else 'standard',
                'stream': 'ext://sys.stdout'
            }
            yaml_config['loggers']['']['handlers'].append('console')
            yaml_config['loggers']['src.shared']['handlers'].append('console')
            yaml_config['loggers']['webapp']['handlers'].append('console')
        
        # Add file handlers
        if config.enable_file:
            # Main log file
            yaml_config['handlers']['file'] = {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'json' if config.enable_json else 'detailed',
                'filename': config.get_log_file_path(config.main_log_file),
                'maxBytes': config.max_file_size,
                'backupCount': config.backup_count
            }
            yaml_config['loggers']['']['handlers'].append('file')
            yaml_config['loggers']['src.shared']['handlers'].append('file')
            yaml_config['loggers']['webapp']['handlers'].append('file')
            
            # Error log file
            yaml_config['handlers']['error_file'] = {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'json' if config.enable_json else 'detailed',
                'filename': config.get_log_file_path(config.error_log_file),
                'maxBytes': config.max_file_size,
                'backupCount': config.backup_count
            }
            yaml_config['loggers']['']['handlers'].append('error_file')
            yaml_config['loggers']['src.shared']['handlers'].append('error_file')
            yaml_config['loggers']['webapp']['handlers'].append('error_file')
            
            # Security log file
            yaml_config['handlers']['security_file'] = {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': config.security_level,
                'formatter': 'json' if config.enable_json else 'detailed',
                'filename': config.get_log_file_path(config.security_log_file),
                'maxBytes': config.max_file_size,
                'backupCount': config.backup_count
            }
            yaml_config['loggers']['security']['handlers'].append('security_file')
            
            # Access log file
            yaml_config['handlers']['access_file'] = {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': config.api_level,
                'formatter': 'json' if config.enable_json else 'detailed',
                'filename': config.get_log_file_path(config.access_log_file),
                'maxBytes': config.max_file_size,
                'backupCount': config.backup_count
            }
            yaml_config['loggers']['api']['handlers'].append('access_file')
        
        # Write YAML file
        with open(output_file, 'w') as f:
            yaml.dump(yaml_config, f, default_flow_style=False, indent=2)
        
        return output_file
    
    @classmethod
    def load_yaml_config(cls, config_file: str) -> Dict[str, Any]:
        """Load YAML logging configuration."""
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading YAML config from {config_file}: {e}")
            return {}
    
    @classmethod
    def get_test_config(cls) -> LoggingConfig:
        """Get configuration for testing."""
        return cls.get_config('testing')
    
    @classmethod
    def get_development_config(cls) -> LoggingConfig:
        """Get configuration for development."""
        return cls.get_config('development')
    
    @classmethod
    def get_production_config(cls) -> LoggingConfig:
        """Get configuration for production."""
        return cls.get_config('production')

# Convenience functions
def get_logging_config(environment: str = None) -> LoggingConfig:
    """Get logging configuration."""
    return LoggingConfigManager.get_config(environment)

def get_test_logging_config() -> LoggingConfig:
    """Get test logging configuration."""
    return LoggingConfigManager.get_test_config()

def get_development_logging_config() -> LoggingConfig:
    """Get development logging configuration."""
    return LoggingConfigManager.get_development_config()

def get_production_logging_config() -> LoggingConfig:
    """Get production logging configuration."""
    return LoggingConfigManager.get_production_config()

def create_logging_yaml_config(environment: str = None, output_file: str = "logging_config.yaml") -> str:
    """Create YAML logging configuration file."""
    config = get_logging_config(environment)
    return LoggingConfigManager.create_yaml_config(config, output_file) 