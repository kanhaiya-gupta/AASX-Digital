"""
Engine Configuration

Main configuration classes for all engine components including
database, messaging, caching, security, monitoring, and utilities.
"""

import os
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
from datetime import timedelta

from .environment_config import EnvironmentConfig, ConfigEnvironment


# Database Configuration
@dataclass
class DatabaseSettings:
    """Database connection and pool settings."""
    type: str = "sqlite"  # sqlite, postgresql, mysql
    host: str = "localhost"
    port: int = 5432
    name: str = "aas_engine"
    username: str = "aas_user"
    password: str = ""
    url: Optional[str] = None
    
    # Connection pool settings
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    pool_pre_ping: bool = True
    
    # SSL settings
    ssl_mode: str = "prefer"
    ssl_cert: Optional[str] = None
    ssl_key: Optional[str] = None
    ssl_ca: Optional[str] = None
    
    # Timeout settings
    connect_timeout: int = 10
    read_timeout: int = 30
    write_timeout: int = 30


@dataclass
class DatabaseConfig:
    """Complete database configuration."""
    enabled: bool = True
    settings: DatabaseSettings = field(default_factory=DatabaseSettings)
    auto_migrate: bool = True
    backup_enabled: bool = False
    backup_interval: int = 86400  # 24 hours
    backup_retention: int = 7  # days


# Cache Configuration
@dataclass
class CacheSettings:
    """Cache configuration settings."""
    type: str = "memory"  # memory, redis, disk
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    
    # Memory cache settings
    max_size: int = 1000
    default_ttl: int = 3600  # 1 hour
    
    # Redis settings
    redis_url: Optional[str] = None
    redis_cluster: bool = False
    redis_sentinel: bool = False
    
    # Disk cache settings
    disk_path: str = "cache"
    disk_max_size: int = 1024 * 1024 * 1024  # 1GB
    disk_compression: bool = True


@dataclass
class CachingConfig:
    """Complete caching configuration."""
    enabled: bool = True
    settings: CacheSettings = field(default_factory=CacheSettings)
    multi_level: bool = True
    metrics_enabled: bool = True
    eviction_policy: str = "lru"  # lru, lfu, fifo, random


# Messaging Configuration
@dataclass
class MessagingSettings:
    """Messaging system configuration."""
    type: str = "memory"  # memory, redis, rabbitmq, kafka
    host: str = "localhost"
    port: int = 5672
    username: str = "guest"
    password: str = "guest"
    
    # Queue settings
    default_queue: str = "default"
    max_queue_size: int = 10000
    message_ttl: int = 86400  # 24 hours
    
    # Event store settings
    event_store_enabled: bool = True
    event_retention: int = 30  # days
    event_compression: bool = True
    
    # Pub/Sub settings
    pubsub_enabled: bool = True
    topic_retention: int = 7  # days


@dataclass
class MessagingConfig:
    """Complete messaging configuration."""
    enabled: bool = True
    settings: MessagingSettings = field(default_factory=MessagingSettings)
    async_enabled: bool = True
    event_sourcing: bool = True
    metrics_enabled: bool = True


# Security Configuration
@dataclass
class SecuritySettings:
    """Security configuration settings."""
    # Authentication
    auth_enabled: bool = True
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600  # 1 hour
    jwt_refresh_expiration: int = 604800  # 7 days
    
    # Password policies
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_digits: bool = True
    password_require_special: bool = True
    
    # Encryption
    encryption_enabled: bool = True
    encryption_algorithm: str = "AES"
    key_rotation_enabled: bool = False
    key_rotation_interval: int = 90  # days
    
    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100  # per minute
    rate_limit_window: int = 60  # seconds
    
    # Session management
    session_timeout: int = 1800  # 30 minutes
    max_sessions_per_user: int = 5


@dataclass
class SecurityConfig:
    """Complete security configuration."""
    enabled: bool = True
    settings: SecuritySettings = field(default_factory=SecuritySettings)
    audit_logging: bool = True
    mfa_enabled: bool = False
    oauth_enabled: bool = False


# Monitoring Configuration
@dataclass
class MonitoringSettings:
    """Monitoring system configuration."""
    # Metrics
    metrics_enabled: bool = True
    metrics_interval: int = 60  # seconds
    metrics_retention: int = 86400  # 24 hours
    
    # Health checks
    health_enabled: bool = True
    health_interval: int = 30  # seconds
    health_timeout: int = 10  # seconds
    
    # Performance profiling
    profiling_enabled: bool = True
    profiling_sampling_rate: float = 0.1  # 10%
    profiling_max_traces: int = 1000
    
    # Resource monitoring
    resource_enabled: bool = True
    resource_interval: int = 15  # seconds
    
    # Alerting
    alerting_enabled: bool = True
    alert_channels: List[str] = field(default_factory=lambda: ["log", "email"])
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "cpu_usage": 80.0,
        "memory_usage": 85.0,
        "disk_usage": 90.0,
        "response_time": 5.0,
        "error_rate": 5.0
    })


@dataclass
class MonitoringConfig:
    """Complete monitoring configuration."""
    enabled: bool = True
    settings: MonitoringSettings = field(default_factory=MonitoringSettings)
    error_tracking: bool = True
    log_aggregation: bool = True
    dashboard_enabled: bool = True


# Logging Configuration
@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "json"  # json, csv, plain, logstash, custom
    output: str = "file"  # file, console, both
    file_path: Optional[Path] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    rotation: str = "size"  # size, time, both
    rotation_interval: str = "1 day"
    compression: bool = True
    retention_days: int = 30
    structured_logging: bool = True
    custom_formatter: Optional[str] = None


# Performance Configuration
@dataclass
class PerformanceConfig:
    """Performance configuration."""
    # Threading
    max_workers: int = 4
    thread_pool_size: int = 10
    
    # Async
    max_concurrent_tasks: int = 100
    task_timeout: int = 300  # 5 minutes
    
    # Database
    query_timeout: int = 30
    connection_timeout: int = 10
    max_connections: int = 50
    
    # Cache
    cache_timeout: int = 60
    max_cache_size: int = 1000
    
    # API
    api_timeout: int = 30
    max_request_size: int = 100 * 1024 * 1024  # 100MB


# Utils Configuration
@dataclass
class UtilsSettings:
    """Utility functions configuration."""
    # Async helpers
    retry_max_attempts: int = 3
    retry_base_delay: float = 0.1
    retry_max_delay: float = 10.0
    
    # File handlers
    temp_dir: str = "temp"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: List[str] = field(default_factory=lambda: [".txt", ".json", ".csv", ".xml"])
    
    # Data transformers
    max_data_size: int = 10 * 1024 * 1024  # 10MB
    compression_enabled: bool = True
    
    # Time utilities
    default_timezone: str = "UTC"
    business_hours: Dict[str, tuple] = field(default_factory=lambda: {
        "monday": (9, 17),
        "tuesday": (9, 17),
        "wednesday": (9, 17),
        "thursday": (9, 17),
        "friday": (9, 17)
    })


@dataclass
class UtilsConfig:
    """Complete utilities configuration."""
    enabled: bool = True
    settings: UtilsSettings = field(default_factory=UtilsSettings)
    async_helpers: bool = True
    data_transformers: bool = True
    file_handlers: bool = True
    time_utils: bool = True
    validators: bool = True


# Main Engine Configuration
@dataclass
class EngineConfig:
    """Complete engine configuration."""
    
    # Basic identification
    config_id: str = field(default_factory=lambda: f"config_{os.getenv('ENVIRONMENT', 'dev')}_{os.getpid()}")
    version: str = "1.0.0"
    name: str = "AAS Data Modeling Engine"
    description: str = "Asset Administration Shell Data Modeling and Processing Engine"
    
    # Environment
    environment: EnvironmentConfig = field(default_factory=EnvironmentConfig.from_environment)
    
    # Component configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    messaging: MessagingConfig = field(default_factory=MessagingConfig)
    caching: CachingConfig = field(default_factory=CachingConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    utils: UtilsConfig = field(default_factory=UtilsConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    # Custom configurations
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    created_at: str = field(default_factory=lambda: os.getenv("CONFIG_CREATED_AT", ""))
    updated_at: str = field(default_factory=lambda: os.getenv("CONFIG_UPDATED_AT", ""))
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization setup."""
        # Set logging file path if not specified
        if self.logging.file_path is None:
            self.logging.file_path = self.environment.log_path / "engine.log"
        
        # Create necessary directories
        self.environment.create_directories()
    
    def get_component_config(self, component: str) -> Any:
        """Get configuration for a specific component."""
        component_map = {
            "database": self.database,
            "messaging": self.messaging,
            "caching": self.caching,
            "security": self.security,
            "monitoring": self.monitoring,
            "utils": self.utils,
            "logging": self.logging,
            "performance": self.performance
        }
        return component_map.get(component)
    
    def is_component_enabled(self, component: str) -> bool:
        """Check if a component is enabled."""
        config = self.get_component_config(component)
        return config is not None and getattr(config, "enabled", True)
    
    def get_setting(self, path: str, default: Any = None) -> Any:
        """Get a nested configuration setting using dot notation."""
        keys = path.split(".")
        value = self
        
        try:
            for key in keys:
                if hasattr(value, key):
                    value = getattr(value, key)
                elif isinstance(value, dict):
                    value = value[key]
                else:
                    return default
            return value
        except (KeyError, AttributeError):
            return default
    
    def set_setting(self, path: str, value: Any) -> bool:
        """Set a nested configuration setting using dot notation."""
        keys = path.split(".")
        target = self
        
        try:
            for key in keys[:-1]:
                if hasattr(target, key):
                    target = getattr(target, key)
                elif isinstance(target, dict):
                    if key not in target:
                        target[key] = {}
                    target = target[key]
                else:
                    return False
            
            last_key = keys[-1]
            if hasattr(target, last_key):
                setattr(target, last_key, value)
            elif isinstance(target, dict):
                target[last_key] = value
            else:
                return False
            
            return True
        except (AttributeError, TypeError):
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "config_id": self.config_id,
            "version": self.version,
            "name": self.name,
            "description": self.description,
            "environment": self.environment.to_dict(),
            "database": {
                "enabled": self.database.enabled,
                "settings": self.database.settings.__dict__
            },
            "messaging": {
                "enabled": self.messaging.enabled,
                "settings": self.messaging.settings.__dict__
            },
            "caching": {
                "enabled": self.caching.enabled,
                "settings": self.caching.settings.__dict__
            },
            "security": {
                "enabled": self.security.enabled,
                "settings": self.security.settings.__dict__
            },
            "monitoring": {
                "enabled": self.monitoring.enabled,
                "settings": self.monitoring.settings.__dict__
            },
            "utils": {
                "enabled": self.utils.enabled,
                "settings": self.utils.settings.__dict__
            },
            "logging": self.logging.__dict__,
            "performance": self.performance.__dict__,
            "custom_settings": self.custom_settings,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by,
            "updated_by": self.updated_by
        }
    
    def __str__(self) -> str:
        """String representation."""
        return f"EngineConfig(version={self.version}, environment={self.environment.environment.value})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"EngineConfig(version={self.version}, name='{self.name}', environment={self.environment.environment})"
