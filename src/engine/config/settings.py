"""
Application Settings System

Provides centralized management of application settings with defaults,
overrides, and environment-specific configurations.
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, Union, List, TypeVar, Type
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class Environment(Enum):
    """Application environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    DEMO = "demo"


class SettingsScope(Enum):
    """Settings scope levels."""
    GLOBAL = "global"
    ENVIRONMENT = "environment"
    USER = "user"
    PROJECT = "project"
    INSTANCE = "instance"


@dataclass
class DatabaseSettings:
    """Database connection settings."""
    host: str = "localhost"
    port: int = 5432
    database: str = "aas_engine"
    username: str = "postgres"
    password: str = ""
    ssl_mode: str = "prefer"
    connection_timeout: int = 30
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False


@dataclass
class SecuritySettings:
    """Security configuration settings."""
    secret_key: str = ""
    jwt_secret: str = ""
    jwt_expiration: int = 3600  # 1 hour
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_digits: bool = True
    password_require_special: bool = True
    session_timeout: int = 1800  # 30 minutes
    max_login_attempts: int = 5
    lockout_duration: int = 900  # 15 minutes
    enable_mfa: bool = True
    enable_audit_logging: bool = True


@dataclass
class LoggingSettings:
    """Logging configuration settings."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = False
    enable_syslog: bool = False
    syslog_host: str = "localhost"
    syslog_port: int = 514


@dataclass
class CacheSettings:
    """Cache configuration settings."""
    enable_memory_cache: bool = True
    enable_redis_cache: bool = False
    enable_disk_cache: bool = False
    memory_max_size: int = 1000
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    disk_cache_path: str = "./cache"
    default_ttl: int = 3600  # 1 hour


@dataclass
class MessagingSettings:
    """Messaging system settings."""
    enable_event_bus: bool = True
    enable_message_queue: bool = False
    enable_pubsub: bool = True
    max_queue_size: int = 10000
    worker_threads: int = 4
    retry_attempts: int = 3
    retry_delay: float = 1.0


@dataclass
class MonitoringSettings:
    """Monitoring and metrics settings."""
    enable_metrics: bool = True
    enable_health_checks: bool = True
    enable_performance_profiling: bool = False
    metrics_interval: int = 60  # 1 minute
    health_check_interval: int = 300  # 5 minutes
    alert_threshold: float = 0.8
    enable_prometheus: bool = False
    prometheus_port: int = 9090


@dataclass
class APISettings:
    """API framework settings."""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    reload: bool = False
    workers: int = 1
    max_requests: int = 1000
    max_requests_jitter: int = 100
    timeout_keep_alive: int = 5
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    cors_allow_credentials: bool = True
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60


@dataclass
class BackgroundTaskSettings:
    """Background task management settings."""
    enable_task_queue: bool = True
    max_workers: int = 4
    task_timeout: int = 300  # 5 minutes
    enable_scheduling: bool = True
    scheduler_interval: int = 60  # 1 minute
    max_queued_tasks: int = 1000


@dataclass
class IntegrationSettings:
    """External integration settings."""
    http_timeout: int = 30
    http_retries: int = 3
    webhook_timeout: int = 10
    enable_webhook_retries: bool = True
    max_webhook_retries: int = 3
    webhook_retry_delay: float = 1.0


@dataclass
class ApplicationSettings:
    """Main application settings."""
    name: str = "AAS Engine"
    version: str = "1.0.0"
    description: str = "Asset Administration Shell Data Modeling Engine"
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    timezone: str = "UTC"
    locale: str = "en_US"
    encoding: str = "utf-8"
    
    # Webapp-specific settings (for app_factory compatibility)
    app_name: str = "AASX Digital Twin Analytics Framework"
    app_version: str = "1.0.0"
    app_env: str = "development"
    
    # Module-specific settings
    aasx_enabled: bool = True
    ai_rag_enabled: bool = True
    twin_registry_enabled: bool = True
    certificate_manager_enabled: bool = True
    kg_neo4j_enabled: bool = True
    federated_learning_enabled: bool = True
    physics_modeling_enabled: bool = True
    
    # Component settings
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    security: SecuritySettings = field(default_factory=SecuritySettings)
    logging: LoggingSettings = field(default_factory=LoggingSettings)
    cache: CacheSettings = field(default_factory=CacheSettings)
    messaging: MessagingSettings = field(default_factory=MessagingSettings)
    monitoring: MonitoringSettings = field(default_factory=MonitoringSettings)
    api: APISettings = field(default_factory=APISettings)
    background_tasks: BackgroundTaskSettings = field(default_factory=BackgroundTaskSettings)
    integration: IntegrationSettings = field(default_factory=IntegrationSettings)


class SettingsManager:
    """Manages application settings with environment-specific overrides."""
    
    def __init__(self, 
                 config_dir: Optional[str] = None,
                 environment: Optional[Environment] = None):
        """
        Initialize the settings manager.
        
        Args:
            config_dir: Configuration directory path
            environment: Application environment
        """
        self.config_dir = config_dir or os.path.join(
            os.path.expanduser("~"), ".aas_engine", "config"
        )
        
        # Ensure config directory exists
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Detect environment
        self.environment = environment or self._detect_environment()
        
        # Initialize settings
        self.settings = ApplicationSettings(environment=self.environment)
        
        # Load configuration files
        self._load_configuration()
        
        # Apply environment overrides
        self._apply_environment_overrides()
        
        # Apply user overrides
        self._apply_user_overrides()
    
    def _detect_environment(self) -> Environment:
        """Detect the current environment from various sources."""
        # Check environment variable
        env_var = os.getenv("AAS_ENGINE_ENV", "").lower()
        if env_var in [e.value for e in Environment]:
            return Environment(env_var)
        
        # Check if running in test mode
        if "pytest" in sys.modules or "unittest" in sys.modules:
            return Environment.TESTING
        
        # Check if running in debug mode
        if os.getenv("DEBUG", "").lower() in ["true", "1", "yes"]:
            return Environment.DEVELOPMENT
        
        # Default to development
        return Environment.DEVELOPMENT
    
    def _load_configuration(self):
        """Load configuration from files."""
        config_files = [
            "config.yaml",
            "config.yml", 
            "config.json",
            f"config.{self.environment.value}.yaml",
            f"config.{self.environment.value}.yml",
            f"config.{self.environment.value}.json"
        ]
        
        for filename in config_files:
            file_path = os.path.join(self.config_dir, filename)
            if os.path.exists(file_path):
                self._load_config_file(file_path)
                break
    
    def _load_config_file(self, file_path: str):
        """Load configuration from a specific file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith(('.yaml', '.yml')):
                    config_data = yaml.safe_load(f)
                elif file_path.endswith('.json'):
                    config_data = json.load(f)
                else:
                    return
                
                self._update_settings_from_dict(config_data)
                logger.info(f"Loaded configuration from {file_path}")
                
        except Exception as e:
            logger.error(f"Failed to load configuration from {file_path}: {e}")
    
    def _update_settings_from_dict(self, config_data: Dict[str, Any]):
        """Update settings from a configuration dictionary."""
        if not isinstance(config_data, dict):
            return
        
        for key, value in config_data.items():
            if hasattr(self.settings, key):
                current_value = getattr(self.settings, key)
                if isinstance(current_value, (DatabaseSettings, SecuritySettings, 
                                           LoggingSettings, CacheSettings, 
                                           MessagingSettings, MonitoringSettings,
                                           APISettings, BackgroundTaskSettings,
                                           IntegrationSettings)):
                    # Update nested settings
                    if isinstance(value, dict):
                        self._update_nested_settings(current_value, value)
                else:
                    # Update simple value
                    setattr(self.settings, key, value)
    
    def _update_nested_settings(self, settings_obj: Any, config_data: Dict[str, Any]):
        """Update nested settings object from configuration data."""
        for key, value in config_data.items():
            if hasattr(settings_obj, key):
                setattr(settings_obj, key, value)
    
    def _apply_environment_overrides(self):
        """Apply environment-specific setting overrides."""
        env_overrides = self._get_environment_overrides()
        self._update_settings_from_dict(env_overrides)
    
    def _get_environment_overrides(self) -> Dict[str, Any]:
        """Get environment-specific setting overrides."""
        overrides = {}
        
        if self.environment == Environment.PRODUCTION:
            overrides.update({
                "debug": False,
                "logging": {"level": "WARNING", "enable_console": False, "enable_file": True},
                "security": {"enable_mfa": True, "enable_audit_logging": True},
                "monitoring": {"enable_metrics": True, "enable_health_checks": True},
                "cache": {"enable_redis_cache": True, "enable_memory_cache": False}
            })
        
        elif self.environment == Environment.TESTING:
            overrides.update({
                "debug": True,
                "database": {"database": "aas_engine_test"},
                "logging": {"level": "DEBUG", "enable_file": False},
                "cache": {"enable_memory_cache": True, "enable_redis_cache": False},
                "monitoring": {"enable_metrics": False, "enable_health_checks": False}
            })
        
        elif self.environment == Environment.STAGING:
            overrides.update({
                "debug": False,
                "logging": {"level": "INFO", "enable_file": True},
                "monitoring": {"enable_metrics": True, "enable_health_checks": True}
            })
        
        return overrides
    
    def _apply_user_overrides(self):
        """Apply user-specific setting overrides."""
        user_config_file = os.path.join(self.config_dir, "user_config.yaml")
        if os.path.exists(user_config_file):
            self._load_config_file(user_config_file)
    
    def get_setting(self, path: str, default: Any = None) -> Any:
        """
        Get a setting value using dot notation.
        
        Args:
            path: Setting path (e.g., "database.host", "security.secret_key")
            default: Default value if setting not found
            
        Returns:
            Setting value or default
        """
        try:
            keys = path.split('.')
            value = self.settings
            
            for key in keys:
                if hasattr(value, key):
                    value = getattr(value, key)
                else:
                    return default
            
            return value
        except Exception as e:
            logger.error(f"Failed to get setting '{path}': {e}")
            return default
    
    def set_setting(self, path: str, value: Any) -> bool:
        """
        Set a setting value using dot notation.
        
        Args:
            path: Setting path (e.g., "database.host", "security.secret_key")
            value: New value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            keys = path.split('.')
            current = self.settings
            
            # Navigate to the parent object
            for key in keys[:-1]:
                if hasattr(current, key):
                    current = getattr(current, key)
                else:
                    return False
            
            # Set the value on the final object
            final_key = keys[-1]
            if hasattr(current, final_key):
                setattr(current, final_key, value)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to set setting '{path}': {e}")
            return False
    
    def save_configuration(self, filename: str = "config.yaml") -> bool:
        """
        Save current settings to a configuration file.
        
        Args:
            filename: Configuration filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = os.path.join(self.config_dir, filename)
            
            # Convert settings to dictionary
            config_data = asdict(self.settings)
            
            # Handle enum values
            config_data['environment'] = self.environment.value
            
            with open(file_path, 'w', encoding='utf-8') as f:
                if filename.endswith(('.yaml', '.yml')):
                    yaml.dump(config_data, f, default_flow_style=False, indent=2)
                elif filename.endswith('.json'):
                    json.dump(config_data, f, indent=2, default=str)
            
            logger.info(f"Configuration saved to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def export_settings(self, format: str = "yaml") -> str:
        """
        Export settings to a string representation.
        
        Args:
            format: Export format ("yaml" or "json")
            
        Returns:
            Settings as string
        """
        try:
            config_data = asdict(self.settings)
            config_data['environment'] = self.environment.value
            
            if format.lower() == "json":
                return json.dumps(config_data, indent=2, default=str)
            else:
                return yaml.dump(config_data, default_flow_style=False, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to export settings: {e}")
            return ""
    
    def validate_settings(self) -> Dict[str, List[str]]:
        """
        Validate current settings for potential issues.
        
        Returns:
            Dictionary of validation issues by category
        """
        issues = {
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Security validation
        if self.settings.security.secret_key == "":
            issues["errors"].append("Secret key is not set")
        
        if self.settings.security.jwt_secret == "":
            issues["errors"].append("JWT secret is not set")
        
        if self.settings.environment == Environment.PRODUCTION:
            if self.settings.debug:
                issues["warnings"].append("Debug mode is enabled in production")
            
            if not self.settings.logging.enable_file:
                issues["recommendations"].append("File logging should be enabled in production")
        
        # Database validation
        if self.settings.database.password == "":
            issues["warnings"].append("Database password is not set")
        
        # Cache validation
        if not any([self.settings.cache.enable_memory_cache,
                   self.settings.cache.enable_redis_cache,
                   self.settings.cache.enable_disk_cache]):
            issues["warnings"].append("No cache backend is enabled")
        
        return issues


# Global settings manager instance
_global_settings_manager: Optional[SettingsManager] = None


def get_global_settings_manager() -> SettingsManager:
    """Get the global settings manager instance."""
    global _global_settings_manager
    if _global_settings_manager is None:
        _global_settings_manager = SettingsManager()
    return _global_settings_manager


def set_global_settings_manager(manager: SettingsManager):
    """Set the global settings manager instance."""
    global _global_settings_manager
    _global_settings_manager = manager


def get_setting(path: str, default: Any = None) -> Any:
    """Get a setting using the global settings manager."""
    return get_global_settings_manager().get_setting(path, default)


def set_setting(path: str, value: Any) -> bool:
    """Set a setting using the global settings manager."""
    return get_global_settings_manager().set_setting(path, value)


def get_settings() -> ApplicationSettings:
    """Get the current application settings."""
    return get_global_settings_manager().settings


def get_environment() -> Environment:
    """Get the current application environment."""
    return get_global_settings_manager().environment


# Import sys for environment detection
import sys

# Simple settings instance for app_factory compatibility
settings = get_settings()
