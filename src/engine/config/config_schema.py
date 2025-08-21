"""
Configuration Schema

Defines JSON schemas for configuration validation and documentation
for the AAS Data Modeling Engine.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ConfigSchema:
    """Configuration schema definition."""
    
    @staticmethod
    def get_engine_config_schema() -> Dict[str, Any]:
        """Get the complete engine configuration JSON schema."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "AAS Data Modeling Engine Configuration",
            "description": "Configuration schema for the AAS Data Modeling Engine",
            "type": "object",
            "properties": {
                "config_id": {
                    "type": "string",
                    "description": "Unique configuration identifier",
                    "pattern": "^config_[a-zA-Z0-9_]+$"
                },
                "version": {
                    "type": "string",
                    "description": "Configuration version",
                    "pattern": "^\\d+\\.\\d+\\.\\d+$"
                },
                "name": {
                    "type": "string",
                    "description": "Engine name",
                    "minLength": 1
                },
                "description": {
                    "type": "string",
                    "description": "Engine description"
                },
                "environment": {
                    "$ref": "#/definitions/EnvironmentConfig"
                },
                "database": {
                    "$ref": "#/definitions/DatabaseConfig"
                },
                "messaging": {
                    "$ref": "#/definitions/MessagingConfig"
                },
                "caching": {
                    "$ref": "#/definitions/CachingConfig"
                },
                "security": {
                    "$ref": "#/definitions/SecurityConfig"
                },
                "monitoring": {
                    "$ref": "#/definitions/MonitoringConfig"
                },
                "utils": {
                    "$ref": "#/definitions/UtilsConfig"
                },
                "logging": {
                    "$ref": "#/definitions/LoggingConfig"
                },
                "performance": {
                    "$ref": "#/definitions/PerformanceConfig"
                },
                "custom_settings": {
                    "type": "object",
                    "description": "Custom configuration settings",
                    "additionalProperties": True
                },
                "created_at": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Configuration creation timestamp"
                },
                "updated_at": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Configuration last update timestamp"
                },
                "created_by": {
                    "type": "string",
                    "description": "Configuration creator"
                },
                "updated_by": {
                    "type": "string",
                    "description": "Configuration last updater"
                }
            },
            "required": ["version", "name", "environment"],
            "definitions": {
                "EnvironmentConfig": {
                    "type": "object",
                    "properties": {
                        "environment": {
                            "type": "string",
                            "enum": ["development", "testing", "staging", "production", "demo"],
                            "description": "Environment type"
                        },
                        "name": {
                            "type": "string",
                            "description": "Environment name"
                        },
                        "description": {
                            "type": "string",
                            "description": "Environment description"
                        },
                        "debug": {
                            "type": "boolean",
                            "description": "Enable debug mode"
                        },
                        "verbose": {
                            "type": "boolean",
                            "description": "Enable verbose logging"
                        },
                        "test_mode": {
                            "type": "boolean",
                            "description": "Enable test mode"
                        },
                        "base_path": {
                            "type": "string",
                            "description": "Base directory path"
                        },
                        "config_path": {
                            "type": "string",
                            "description": "Configuration directory path"
                        },
                        "data_path": {
                            "type": "string",
                            "description": "Data directory path"
                        },
                        "log_path": {
                            "type": "string",
                            "description": "Log directory path"
                        },
                        "temp_path": {
                            "type": "string",
                            "description": "Temporary directory path"
                        },
                        "cache_path": {
                            "type": "string",
                            "description": "Cache directory path"
                        },
                        "features": {
                            "type": "object",
                            "properties": {
                                "hot_reload": {"type": "boolean"},
                                "auto_migration": {"type": "boolean"},
                                "debug_endpoints": {"type": "boolean"},
                                "profiling": {"type": "boolean"},
                                "caching": {"type": "boolean"},
                                "monitoring": {"type": "boolean"},
                                "security": {"type": "boolean"},
                                "audit_logging": {"type": "boolean"}
                            },
                            "additionalProperties": {"type": "boolean"}
                        }
                    },
                    "required": ["environment", "name"]
                },
                "DatabaseConfig": {
                    "type": "object",
                    "properties": {
                        "enabled": {
                            "type": "boolean",
                            "description": "Enable database component"
                        },
                        "auto_migrate": {
                            "type": "boolean",
                            "description": "Enable automatic migrations"
                        },
                        "backup_enabled": {
                            "type": "boolean",
                            "description": "Enable database backups"
                        },
                        "backup_interval": {
                            "type": "integer",
                            "minimum": 3600,
                            "description": "Backup interval in seconds"
                        },
                        "backup_retention": {
                            "type": "integer",
                            "minimum": 1,
                            "description": "Backup retention in days"
                        },
                        "settings": {
                            "$ref": "#/definitions/DatabaseSettings"
                        }
                    },
                    "required": ["enabled"]
                },
                "DatabaseSettings": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": ["sqlite", "postgresql", "mysql", "oracle", "sqlserver"],
                            "description": "Database type"
                        },
                        "host": {
                            "type": "string",
                            "description": "Database host"
                        },
                        "port": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 65535,
                            "description": "Database port"
                        },
                        "name": {
                            "type": "string",
                            "description": "Database name"
                        },
                        "username": {
                            "type": "string",
                            "description": "Database username"
                        },
                        "password": {
                            "type": "string",
                            "description": "Database password"
                        },
                        "url": {
                            "type": "string",
                            "description": "Database connection URL"
                        },
                        "pool_size": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "description": "Connection pool size"
                        },
                        "max_overflow": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100,
                            "description": "Maximum pool overflow"
                        },
                        "pool_timeout": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 300,
                            "description": "Pool timeout in seconds"
                        },
                        "pool_recycle": {
                            "type": "integer",
                            "minimum": 300,
                            "maximum": 86400,
                            "description": "Pool recycle time in seconds"
                        },
                        "pool_pre_ping": {
                            "type": "boolean",
                            "description": "Enable pool pre-ping"
                        },
                        "ssl_mode": {
                            "type": "string",
                            "enum": ["disable", "allow", "prefer", "require", "verify-ca", "verify-full"],
                            "description": "SSL mode"
                        },
                        "ssl_cert": {
                            "type": "string",
                            "description": "SSL certificate path"
                        },
                        "ssl_key": {
                            "type": "string",
                            "description": "SSL key path"
                        },
                        "ssl_ca": {
                            "type": "string",
                            "description": "SSL CA certificate path"
                        },
                        "connect_timeout": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 300,
                            "description": "Connection timeout in seconds"
                        },
                        "read_timeout": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 300,
                            "description": "Read timeout in seconds"
                        },
                        "write_timeout": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 300,
                            "description": "Write timeout in seconds"
                        }
                    },
                    "required": ["type"]
                },
                "MessagingConfig": {
                    "type": "object",
                    "properties": {
                        "enabled": {
                            "type": "boolean",
                            "description": "Enable messaging component"
                        },
                        "async_enabled": {
                            "type": "boolean",
                            "description": "Enable async messaging"
                        },
                        "event_sourcing": {
                            "type": "boolean",
                            "description": "Enable event sourcing"
                        },
                        "metrics_enabled": {
                            "type": "boolean",
                            "description": "Enable messaging metrics"
                        },
                        "settings": {
                            "$ref": "#/definitions/MessagingSettings"
                        }
                    },
                    "required": ["enabled"]
                },
                "MessagingSettings": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": ["memory", "redis", "rabbitmq", "kafka", "sqs"],
                            "description": "Messaging type"
                        },
                        "host": {
                            "type": "string",
                            "description": "Messaging host"
                        },
                        "port": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 65535,
                            "description": "Messaging port"
                        },
                        "username": {
                            "type": "string",
                            "description": "Messaging username"
                        },
                        "password": {
                            "type": "string",
                            "description": "Messaging password"
                        },
                        "default_queue": {
                            "type": "string",
                            "description": "Default queue name"
                        },
                        "max_queue_size": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 1000000,
                            "description": "Maximum queue size"
                        },
                        "message_ttl": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 604800,
                            "description": "Message TTL in seconds"
                        },
                        "event_store_enabled": {
                            "type": "boolean",
                            "description": "Enable event store"
                        },
                        "event_retention": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 365,
                            "description": "Event retention in days"
                        },
                        "event_compression": {
                            "type": "boolean",
                            "description": "Enable event compression"
                        },
                        "pubsub_enabled": {
                            "type": "boolean",
                            "description": "Enable pub/sub"
                        },
                        "topic_retention": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 365,
                            "description": "Topic retention in days"
                        }
                    },
                    "required": ["type"]
                },
                "CachingConfig": {
                    "type": "object",
                    "properties": {
                        "enabled": {
                            "type": "boolean",
                            "description": "Enable caching component"
                        },
                        "multi_level": {
                            "type": "boolean",
                            "description": "Enable multi-level caching"
                        },
                        "metrics_enabled": {
                            "type": "boolean",
                            "description": "Enable cache metrics"
                        },
                        "eviction_policy": {
                            "type": "string",
                            "enum": ["lru", "lfu", "fifo", "random"],
                            "description": "Cache eviction policy"
                        },
                        "settings": {
                            "$ref": "#/definitions/CacheSettings"
                        }
                    },
                    "required": ["enabled"]
                },
                "CacheSettings": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": ["memory", "redis", "disk", "memcached"],
                            "description": "Cache type"
                        },
                        "host": {
                            "type": "string",
                            "description": "Cache host"
                        },
                        "port": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 65535,
                            "description": "Cache port"
                        },
                        "db": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 15,
                            "description": "Cache database number"
                        },
                        "password": {
                            "type": "string",
                            "description": "Cache password"
                        },
                        "max_size": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 1000000,
                            "description": "Maximum cache size"
                        },
                        "default_ttl": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 31536000,
                            "description": "Default TTL in seconds"
                        },
                        "redis_url": {
                            "type": "string",
                            "description": "Redis connection URL"
                        },
                        "redis_cluster": {
                            "type": "boolean",
                            "description": "Enable Redis cluster mode"
                        },
                        "redis_sentinel": {
                            "type": "boolean",
                            "description": "Enable Redis sentinel mode"
                        },
                        "disk_path": {
                            "type": "string",
                            "description": "Disk cache path"
                        },
                        "disk_max_size": {
                            "type": "integer",
                            "minimum": 1048576,
                            "description": "Disk cache max size in bytes"
                        },
                        "disk_compression": {
                            "type": "boolean",
                            "description": "Enable disk cache compression"
                        }
                    },
                    "required": ["type"]
                },
                "SecurityConfig": {
                    "type": "object",
                    "properties": {
                        "enabled": {
                            "type": "boolean",
                            "description": "Enable security component"
                        },
                        "audit_logging": {
                            "type": "boolean",
                            "description": "Enable audit logging"
                        },
                        "mfa_enabled": {
                            "type": "boolean",
                            "description": "Enable multi-factor authentication"
                        },
                        "oauth_enabled": {
                            "type": "boolean",
                            "description": "Enable OAuth authentication"
                        },
                        "settings": {
                            "$ref": "#/definitions/SecuritySettings"
                        }
                    },
                    "required": ["enabled"]
                },
                "SecuritySettings": {
                    "type": "object",
                    "properties": {
                        "auth_enabled": {
                            "type": "boolean",
                            "description": "Enable authentication"
                        },
                        "jwt_secret": {
                            "type": "string",
                            "minLength": 32,
                            "description": "JWT secret key"
                        },
                        "jwt_algorithm": {
                            "type": "string",
                            "enum": ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"],
                            "description": "JWT algorithm"
                        },
                        "jwt_expiration": {
                            "type": "integer",
                            "minimum": 60,
                            "maximum": 86400,
                            "description": "JWT expiration in seconds"
                        },
                        "jwt_refresh_expiration": {
                            "type": "integer",
                            "minimum": 3600,
                            "maximum": 2592000,
                            "description": "JWT refresh expiration in seconds"
                        },
                        "password_min_length": {
                            "type": "integer",
                            "minimum": 8,
                            "maximum": 128,
                            "description": "Minimum password length"
                        },
                        "password_require_uppercase": {
                            "type": "boolean",
                            "description": "Require uppercase letters in password"
                        },
                        "password_require_lowercase": {
                            "type": "boolean",
                            "description": "Require lowercase letters in password"
                        },
                        "password_require_digits": {
                            "type": "boolean",
                            "description": "Require digits in password"
                        },
                        "password_require_special": {
                            "type": "boolean",
                            "description": "Require special characters in password"
                        },
                        "encryption_enabled": {
                            "type": "boolean",
                            "description": "Enable encryption"
                        },
                        "encryption_algorithm": {
                            "type": "string",
                            "enum": ["AES", "ChaCha20", "Fernet"],
                            "description": "Encryption algorithm"
                        },
                        "key_rotation_enabled": {
                            "type": "boolean",
                            "description": "Enable key rotation"
                        },
                        "key_rotation_interval": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 365,
                            "description": "Key rotation interval in days"
                        },
                        "rate_limit_enabled": {
                            "type": "boolean",
                            "description": "Enable rate limiting"
                        },
                        "rate_limit_requests": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10000,
                            "description": "Rate limit requests per window"
                        },
                        "rate_limit_window": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 3600,
                            "description": "Rate limit window in seconds"
                        },
                        "session_timeout": {
                            "type": "integer",
                            "minimum": 60,
                            "maximum": 86400,
                            "description": "Session timeout in seconds"
                        },
                        "max_sessions_per_user": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "description": "Maximum sessions per user"
                        }
                    },
                    "required": ["auth_enabled", "jwt_secret", "jwt_algorithm"]
                },
                "MonitoringConfig": {
                    "type": "object",
                    "properties": {
                        "enabled": {
                            "type": "boolean",
                            "description": "Enable monitoring component"
                        },
                        "error_tracking": {
                            "type": "boolean",
                            "description": "Enable error tracking"
                        },
                        "log_aggregation": {
                            "type": "boolean",
                            "description": "Enable log aggregation"
                        },
                        "dashboard_enabled": {
                            "type": "boolean",
                            "description": "Enable monitoring dashboard"
                        },
                        "settings": {
                            "$ref": "#/definitions/MonitoringSettings"
                        }
                    },
                    "required": ["enabled"]
                },
                "MonitoringSettings": {
                    "type": "object",
                    "properties": {
                        "metrics_enabled": {
                            "type": "boolean",
                            "description": "Enable metrics collection"
                        },
                        "metrics_interval": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 3600,
                            "description": "Metrics collection interval in seconds"
                        },
                        "metrics_retention": {
                            "type": "integer",
                            "minimum": 60,
                            "maximum": 2592000,
                            "description": "Metrics retention in seconds"
                        },
                        "max_metrics_history": {
                            "type": "integer",
                            "minimum": 100,
                            "maximum": 1000000,
                            "description": "Maximum metrics history size"
                        },
                        "export_formats": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["json", "csv", "prometheus", "graphite", "influxdb"]
                            },
                            "description": "Metrics export formats"
                        },
                        "custom_metrics": {
                            "type": "object",
                            "description": "Custom metrics definitions",
                            "additionalProperties": {"type": "string"}
                        },
                        "health_enabled": {
                            "type": "boolean",
                            "description": "Enable health checks"
                        },
                        "health_interval": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 3600,
                            "description": "Health check interval in seconds"
                        },
                        "health_timeout": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 300,
                            "description": "Health check timeout in seconds"
                        },
                        "max_failures": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "description": "Maximum consecutive failures"
                        },
                        "alert_on_failure": {
                            "type": "boolean",
                            "description": "Alert on health check failure"
                        },
                        "components_to_monitor": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Components to monitor"
                        },
                        "profiling_enabled": {
                            "type": "boolean",
                            "description": "Enable performance profiling"
                        },
                        "profile_operations": {
                            "type": "boolean",
                            "description": "Profile operations"
                        },
                        "profile_database": {
                            "type": "boolean",
                            "description": "Profile database operations"
                        },
                        "profile_cache": {
                            "type": "boolean",
                            "description": "Profile cache operations"
                        },
                        "profile_api": {
                            "type": "boolean",
                            "description": "Profile API operations"
                        },
                        "slow_query_threshold": {
                            "type": "number",
                            "minimum": 0.001,
                            "maximum": 100.0,
                            "description": "Slow query threshold in seconds"
                        },
                        "max_traces": {
                            "type": "integer",
                            "minimum": 10,
                            "maximum": 100000,
                            "description": "Maximum traces to keep"
                        },
                        "profiling_sampling_rate": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Profiling sampling rate"
                        },
                        "resource_enabled": {
                            "type": "boolean",
                            "description": "Enable resource monitoring"
                        },
                        "monitor_cpu": {
                            "type": "boolean",
                            "description": "Monitor CPU usage"
                        },
                        "monitor_memory": {
                            "type": "boolean",
                            "description": "Monitor memory usage"
                        },
                        "monitor_disk": {
                            "type": "boolean",
                            "description": "Monitor disk usage"
                        },
                        "monitor_network": {
                            "type": "boolean",
                            "description": "Monitor network usage"
                        },
                        "monitor_database_connections": {
                            "type": "boolean",
                            "description": "Monitor database connections"
                        },
                        "monitor_cache_usage": {
                            "type": "boolean",
                            "description": "Monitor cache usage"
                        },
                        "collection_interval": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 3600,
                            "description": "Resource collection interval in seconds"
                        },
                        "alerting_enabled": {
                            "type": "boolean",
                            "description": "Enable alerting"
                        },
                        "alert_channels": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["log", "email", "slack", "webhook", "sms"]
                            },
                            "description": "Alert notification channels"
                        },
                        "email_recipients": {
                            "type": "array",
                            "items": {"type": "string", "format": "email"},
                            "description": "Email alert recipients"
                        },
                        "smtp_server": {
                            "type": "string",
                            "description": "SMTP server address"
                        },
                        "smtp_port": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 65535,
                            "description": "SMTP server port"
                        },
                        "smtp_username": {
                            "type": "string",
                            "description": "SMTP username"
                        },
                        "smtp_password": {
                            "type": "string",
                            "description": "SMTP password"
                        },
                        "alert_thresholds": {
                            "type": "object",
                            "properties": {
                                "cpu_usage": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 100.0,
                                    "description": "CPU usage threshold percentage"
                                },
                                "memory_usage": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 100.0,
                                    "description": "Memory usage threshold percentage"
                                },
                                "disk_usage": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 100.0,
                                    "description": "Disk usage threshold percentage"
                                },
                                "response_time": {
                                    "type": "number",
                                    "minimum": 0.001,
                                    "maximum": 100.0,
                                    "description": "Response time threshold in seconds"
                                },
                                "error_rate": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 100.0,
                                    "description": "Error rate threshold percentage"
                                }
                            },
                            "additionalProperties": {"type": "number"},
                            "description": "Alert thresholds"
                        }
                    },
                    "required": ["metrics_enabled", "health_enabled", "profiling_enabled"]
                },
                "UtilsConfig": {
                    "type": "object",
                    "properties": {
                        "enabled": {
                            "type": "boolean",
                            "description": "Enable utilities component"
                        },
                        "async_helpers": {
                            "type": "boolean",
                            "description": "Enable async helpers"
                        },
                        "data_transformers": {
                            "type": "boolean",
                            "description": "Enable data transformers"
                        },
                        "file_handlers": {
                            "type": "boolean",
                            "description": "Enable file handlers"
                        },
                        "time_utils": {
                            "type": "boolean",
                            "description": "Enable time utilities"
                        },
                        "validators": {
                            "type": "boolean",
                            "description": "Enable validators"
                        },
                        "settings": {
                            "$ref": "#/definitions/UtilsSettings"
                        }
                    },
                    "required": ["enabled"]
                },
                "UtilsSettings": {
                    "type": "object",
                    "properties": {
                        "retry_max_attempts": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10,
                            "description": "Maximum retry attempts"
                        },
                        "retry_base_delay": {
                            "type": "number",
                            "minimum": 0.001,
                            "maximum": 10.0,
                            "description": "Base retry delay in seconds"
                        },
                        "retry_max_delay": {
                            "type": "number",
                            "minimum": 0.1,
                            "maximum": 60.0,
                            "description": "Maximum retry delay in seconds"
                        },
                        "temp_dir": {
                            "type": "string",
                            "description": "Temporary directory path"
                        },
                        "max_file_size": {
                            "type": "integer",
                            "minimum": 1024,
                            "maximum": 1073741824,
                            "description": "Maximum file size in bytes"
                        },
                        "allowed_extensions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Allowed file extensions"
                        },
                        "max_data_size": {
                            "type": "integer",
                            "minimum": 1024,
                            "maximum": 1073741824,
                            "description": "Maximum data size in bytes"
                        },
                        "compression_enabled": {
                            "type": "boolean",
                            "description": "Enable data compression"
                        },
                        "default_timezone": {
                            "type": "string",
                            "description": "Default timezone"
                        },
                        "business_hours": {
                            "type": "object",
                            "properties": {
                                "monday": {
                                    "type": "array",
                                    "items": {"type": "integer"},
                                    "minItems": 2,
                                    "maxItems": 2,
                                    "description": "Monday business hours [start, end]"
                                },
                                "tuesday": {
                                    "type": "array",
                                    "items": {"type": "integer"},
                                    "minItems": 2,
                                    "maxItems": 2,
                                    "description": "Tuesday business hours [start, end]"
                                },
                                "wednesday": {
                                    "type": "array",
                                    "items": {"type": "integer"},
                                    "minItems": 2,
                                    "maxItems": 2,
                                    "description": "Wednesday business hours [start, end]"
                                },
                                "thursday": {
                                    "type": "array",
                                    "items": {"type": "integer"},
                                    "minItems": 2,
                                    "maxItems": 2,
                                    "description": "Thursday business hours [start, end]"
                                },
                                "friday": {
                                    "type": "array",
                                    "items": {"type": "integer"},
                                    "minItems": 2,
                                    "maxItems": 2,
                                    "description": "Friday business hours [start, end]"
                                }
                            },
                            "additionalProperties": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "minItems": 2,
                                "maxItems": 2
                            },
                            "description": "Business hours configuration"
                        }
                    },
                    "required": ["retry_max_attempts", "temp_dir", "max_file_size"]
                },
                "LoggingConfig": {
                    "type": "object",
                    "properties": {
                        "level": {
                            "type": "string",
                            "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                            "description": "Log level"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["json", "csv", "plain", "logstash", "custom"],
                            "description": "Log format"
                        },
                        "output": {
                            "type": "string",
                            "enum": ["file", "console", "both"],
                            "description": "Log output destination"
                        },
                        "file_path": {
                            "type": "string",
                            "description": "Log file path"
                        },
                        "max_file_size": {
                            "type": "integer",
                            "minimum": 1048576,
                            "maximum": 1073741824,
                            "description": "Maximum log file size in bytes"
                        },
                        "backup_count": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100,
                            "description": "Number of backup files to keep"
                        },
                        "rotation": {
                            "type": "string",
                            "enum": ["size", "time", "both"],
                            "description": "Log rotation strategy"
                        },
                        "rotation_interval": {
                            "type": "string",
                            "description": "Log rotation interval"
                        },
                        "compression": {
                            "type": "boolean",
                            "description": "Enable log compression"
                        },
                        "retention_days": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 3650,
                            "description": "Log retention in days"
                        },
                        "enable_metrics": {
                            "type": "boolean",
                            "description": "Enable log metrics"
                        },
                        "enable_audit": {
                            "type": "boolean",
                            "description": "Enable audit logging"
                        },
                        "custom_formatter": {
                            "type": "string",
                            "description": "Custom log formatter"
                        },
                        "structured_logging": {
                            "type": "boolean",
                            "description": "Enable structured logging"
                        }
                    },
                    "required": ["level", "format", "output"]
                },
                "PerformanceConfig": {
                    "type": "object",
                    "properties": {
                        "max_workers": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "description": "Maximum worker threads"
                        },
                        "thread_pool_size": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 1000,
                            "description": "Thread pool size"
                        },
                        "max_concurrent_tasks": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10000,
                            "description": "Maximum concurrent tasks"
                        },
                        "task_timeout": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 3600,
                            "description": "Task timeout in seconds"
                        },
                        "query_timeout": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 300,
                            "description": "Database query timeout in seconds"
                        },
                        "connection_timeout": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 300,
                            "description": "Connection timeout in seconds"
                        },
                        "max_connections": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 1000,
                            "description": "Maximum database connections"
                        },
                        "cache_timeout": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 86400,
                            "description": "Cache timeout in seconds"
                        },
                        "max_cache_size": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 1000000,
                            "description": "Maximum cache size"
                        },
                        "api_timeout": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 300,
                            "description": "API timeout in seconds"
                        },
                        "max_request_size": {
                            "type": "integer",
                            "minimum": 1024,
                            "maximum": 1073741824,
                            "description": "Maximum request size in bytes"
                        }
                    },
                    "required": ["max_workers", "thread_pool_size"]
                }
            }
        }
    
    @staticmethod
    def get_environment_schema() -> Dict[str, Any]:
        """Get the environment configuration JSON schema."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Environment Configuration",
            "description": "Environment-specific configuration schema",
            "type": "object",
            "properties": {
                "environment": {
                    "type": "string",
                    "enum": ["development", "testing", "staging", "production", "demo"],
                    "description": "Environment type"
                },
                "name": {
                    "type": "string",
                    "description": "Environment name"
                },
                "description": {
                    "type": "string",
                    "description": "Environment description"
                },
                "debug": {
                    "type": "boolean",
                    "description": "Enable debug mode"
                },
                "verbose": {
                    "type": "boolean",
                    "description": "Enable verbose logging"
                },
                "test_mode": {
                    "type": "boolean",
                    "description": "Enable test mode"
                },
                "base_path": {
                    "type": "string",
                    "description": "Base directory path"
                },
                "config_path": {
                    "type": "string",
                    "description": "Configuration directory path"
                },
                "data_path": {
                    "type": "string",
                    "description": "Data directory path"
                },
                "log_path": {
                    "type": "string",
                    "description": "Log directory path"
                },
                "temp_path": {
                    "type": "string",
                    "description": "Temporary directory path"
                },
                "cache_path": {
                    "type": "string",
                    "description": "Cache directory path"
                },
                "features": {
                    "type": "object",
                    "properties": {
                        "hot_reload": {"type": "boolean"},
                        "auto_migration": {"type": "boolean"},
                        "debug_endpoints": {"type": "boolean"},
                        "profiling": {"type": "boolean"},
                        "caching": {"type": "boolean"},
                        "monitoring": {"type": "boolean"},
                        "security": {"type": "boolean"},
                        "audit_logging": {"type": "boolean"}
                    },
                    "additionalProperties": {"type": "boolean"}
                }
            },
            "required": ["environment", "name"]
        }
    
    @staticmethod
    def get_database_schema() -> Dict[str, Any]:
        """Get the database configuration JSON schema."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Database Configuration",
            "description": "Database configuration schema",
            "type": "object",
            "properties": {
                "enabled": {
                    "type": "boolean",
                    "description": "Enable database component"
                },
                "auto_migrate": {
                    "type": "boolean",
                    "description": "Enable automatic migrations"
                },
                "backup_enabled": {
                    "type": "boolean",
                    "description": "Enable database backups"
                },
                "backup_interval": {
                    "type": "integer",
                    "minimum": 3600,
                    "description": "Backup interval in seconds"
                },
                "backup_retention": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Backup retention in days"
                },
                "settings": {
                    "$ref": "#/definitions/DatabaseSettings"
                }
            },
            "required": ["enabled"],
            "definitions": {
                "DatabaseSettings": {
                    "$ref": "#/definitions/DatabaseSettings"
                }
            }
        }
    
    @staticmethod
    def get_schema_by_component(component: str) -> Optional[Dict[str, Any]]:
        """Get schema for a specific component."""
        schemas = {
            "environment": ConfigSchema.get_environment_schema(),
            "database": ConfigSchema.get_database_schema(),
            "messaging": ConfigSchema.get_messaging_schema(),
            "caching": ConfigSchema.get_caching_schema(),
            "security": ConfigSchema.get_security_schema(),
            "monitoring": ConfigSchema.get_monitoring_schema(),
            "utils": ConfigSchema.get_utils_schema(),
            "logging": ConfigSchema.get_logging_schema(),
            "performance": ConfigSchema.get_performance_schema()
        }
        return schemas.get(component)
    
    @staticmethod
    def get_messaging_schema() -> Dict[str, Any]:
        """Get the messaging configuration JSON schema."""
        # Implementation would be similar to other schemas
        return {"type": "object", "properties": {}, "required": []}
    
    @staticmethod
    def get_caching_schema() -> Dict[str, Any]:
        """Get the caching configuration JSON schema."""
        # Implementation would be similar to other schemas
        return {"type": "object", "properties": {}, "required": []}
    
    @staticmethod
    def get_security_schema() -> Dict[str, Any]:
        """Get the security configuration JSON schema."""
        # Implementation would be similar to other schemas
        return {"type": "object", "properties": {}, "required": []}
    
    @staticmethod
    def get_monitoring_schema() -> Dict[str, Any]:
        """Get the monitoring configuration JSON schema."""
        # Implementation would be similar to other schemas
        return {"type": "object", "properties": {}, "required": []}
    
    @staticmethod
    def get_utils_schema() -> Dict[str, Any]:
        """Get the utilities configuration JSON schema."""
        # Implementation would be similar to other schemas
        return {"type": "object", "properties": {}, "required": []}
    
    @staticmethod
    def get_logging_schema() -> Dict[str, Any]:
        """Get the logging configuration JSON schema."""
        # Implementation would be similar to other schemas
        return {"type": "object", "properties": {}, "required": []}
    
    @staticmethod
    def get_performance_schema() -> Dict[str, Any]:
        """Get the performance configuration JSON schema."""
        # Implementation would be similar to other schemas
        return {"type": "object", "properties": {}, "required": []}
