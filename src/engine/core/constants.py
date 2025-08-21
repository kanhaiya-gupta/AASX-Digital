"""
System constants and enums for the engine system.

This module provides centralized constants and enumerations that are used
throughout the engine system for consistency and maintainability.
"""

from enum import Enum, auto
from typing import Dict, Any, List


class DatabaseType(Enum):
    """Database types supported by the engine."""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"
    ELASTICSEARCH = "elasticsearch"
    NEO4J = "neo4j"
    INFLUXDB = "influxdb"
    TIMESCALEDB = "timescaledb"
    COCKROACHDB = "cockroachdb"


class ConnectionStrategy(Enum):
    """Database connection strategies."""
    FIFO = "fifo"  # First In, First Out
    LIFO = "lifo"  # Last In, First Out
    ROUND_ROBIN = "round_robin"  # Round Robin
    LEAST_CONNECTIONS = "least_connections"  # Least Connections
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"  # Weighted Round Robin
    RANDOM = "random"  # Random selection


class CacheStrategy(Enum):
    """Cache eviction strategies."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In, First Out
    LIFO = "lifo"  # Last In, First Out
    TTL = "ttl"  # Time To Live
    RANDOM = "random"  # Random eviction


class LogLevel(Enum):
    """Logging levels."""
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


class EventType(Enum):
    """Event types for the event system."""
    # System events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_HEALTH_CHECK = "system.health_check"
    
    # Database events
    DATABASE_CONNECT = "database.connect"
    DATABASE_DISCONNECT = "database.disconnect"
    DATABASE_QUERY = "database.query"
    DATABASE_TRANSACTION = "database.transaction"
    
    # Authentication events
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_REGISTER = "user.register"
    USER_PASSWORD_CHANGE = "user.password_change"
    
    # Business events
    ENTITY_CREATED = "entity.created"
    ENTITY_UPDATED = "entity.updated"
    ENTITY_DELETED = "entity.deleted"
    ENTITY_ACCESSED = "entity.accessed"
    
    # Cache events
    CACHE_HIT = "cache.hit"
    CACHE_MISS = "cache.miss"
    CACHE_EVICT = "cache.evict"
    CACHE_CLEAR = "cache.clear"
    
    # Task events
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_CANCELLED = "task.cancelled"


class HTTPMethod(Enum):
    """HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class HTTPStatus(Enum):
    """HTTP status codes."""
    # Success
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    
    # Client errors
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429
    
    # Server errors
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504


class SecurityLevel(Enum):
    """Security levels for operations."""
    PUBLIC = "public"
    INTERNAL = "internal"
    AUTHENTICATED = "authenticated"
    AUTHORIZED = "authorized"
    ADMIN = "admin"
    SYSTEM = "system"


class DataType(Enum):
    """Data types for validation and processing."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    JSON = "json"
    BINARY = "binary"
    UUID = "uuid"
    EMAIL = "email"
    URL = "url"
    IP_ADDRESS = "ip_address"


class ValidationRule(Enum):
    """Common validation rules."""
    REQUIRED = "required"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"
    PATTERN = "pattern"
    EMAIL = "email"
    URL = "url"
    UUID = "uuid"
    IP_ADDRESS = "ip_address"
    CUSTOM = "custom"


class RetryStrategy(Enum):
    """Retry strategies for failed operations."""
    IMMEDIATE = "immediate"
    LINEAR_BACKOFF = "linear_backoff"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    FIBONACCI_BACKOFF = "fibonacci_backoff"
    RANDOM_BACKOFF = "random_backoff"


class TimeUnit(Enum):
    """Time units for durations and intervals."""
    MILLISECONDS = "ms"
    SECONDS = "s"
    MINUTES = "m"
    HOURS = "h"
    DAYS = "d"
    WEEKS = "w"
    MONTHS = "M"
    YEARS = "y"


# Configuration constants
class ConfigKeys:
    """Configuration key constants."""
    # Database
    DATABASE_TYPE = "database.type"
    DATABASE_URL = "database.url"
    DATABASE_HOST = "database.host"
    DATABASE_PORT = "database.port"
    DATABASE_NAME = "database.name"
    DATABASE_USER = "database.user"
    DATABASE_PASSWORD = "database.password"
    DATABASE_POOL_SIZE = "database.pool_size"
    DATABASE_MAX_OVERFLOW = "database.max_overflow"
    DATABASE_POOL_TIMEOUT = "database.pool_timeout"
    DATABASE_POOL_RECYCLE = "database.pool_recycle"
    
    # Cache
    CACHE_TYPE = "cache.type"
    CACHE_HOST = "cache.host"
    CACHE_PORT = "cache.port"
    CACHE_DB = "cache.db"
    CACHE_PASSWORD = "cache.password"
    CACHE_DEFAULT_TTL = "cache.default_ttl"
    
    # Logging
    LOG_LEVEL = "logging.level"
    LOG_FORMAT = "logging.format"
    LOG_FILE = "logging.file"
    LOG_MAX_SIZE = "logging.max_size"
    LOG_BACKUP_COUNT = "logging.backup_count"
    
    # Security
    SECRET_KEY = "security.secret_key"
    JWT_SECRET = "security.jwt_secret"
    JWT_ALGORITHM = "security.jwt_algorithm"
    JWT_EXPIRATION = "security.jwt_expiration"
    PASSWORD_MIN_LENGTH = "security.password_min_length"
    PASSWORD_REQUIRE_SPECIAL = "security.password_require_special"
    
    # API
    API_HOST = "api.host"
    API_PORT = "api.port"
    API_WORKERS = "api.workers"
    API_TIMEOUT = "api.timeout"
    API_RATE_LIMIT = "api.rate_limit"
    
    # Task Queue
    TASK_QUEUE_TYPE = "task_queue.type"
    TASK_QUEUE_HOST = "task_queue.host"
    TASK_QUEUE_PORT = "task_queue.port"
    TASK_QUEUE_DB = "task_queue.db"
    TASK_QUEUE_PASSWORD = "task_queue.password"
    TASK_WORKERS = "task_queue.workers"


# Default values
class Defaults:
    """Default configuration values."""
    # Database
    DATABASE_POOL_SIZE = 10
    DATABASE_MAX_OVERFLOW = 20
    DATABASE_POOL_TIMEOUT = 30
    DATABASE_POOL_RECYCLE = 3600
    
    # Cache
    CACHE_DEFAULT_TTL = 3600  # 1 hour
    
    # Logging
    LOG_LEVEL = LogLevel.INFO
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Security
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION = 3600  # 1 hour
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_SPECIAL = True
    
    # API
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    API_WORKERS = 4
    API_TIMEOUT = 30
    API_RATE_LIMIT = 100  # requests per minute
    
    # Task Queue
    TASK_WORKERS = 4


# Environment variables
class EnvironmentVars:
    """Environment variable names."""
    # Database
    DB_TYPE = "DB_TYPE"
    DB_URL = "DB_URL"
    DB_HOST = "DB_HOST"
    DB_PORT = "DB_PORT"
    DB_NAME = "DB_NAME"
    DB_USER = "DB_USER"
    DB_PASSWORD = "DB_PASSWORD"
    
    # Cache
    CACHE_TYPE = "CACHE_TYPE"
    CACHE_HOST = "CACHE_HOST"
    CACHE_PORT = "CACHE_PORT"
    CACHE_DB = "CACHE_DB"
    CACHE_PASSWORD = "CACHE_PASSWORD"
    
    # Logging
    LOG_LEVEL = "LOG_LEVEL"
    LOG_FILE = "LOG_FILE"
    
    # Security
    SECRET_KEY = "SECRET_KEY"
    JWT_SECRET = "JWT_SECRET"
    
    # API
    API_HOST = "API_HOST"
    API_PORT = "API_PORT"
    API_WORKERS = "API_WORKERS"
    
    # Task Queue
    TASK_QUEUE_TYPE = "TASK_QUEUE_TYPE"
    TASK_QUEUE_HOST = "TASK_QUEUE_HOST"
    TASK_QUEUE_PORT = "TASK_QUEUE_PORT"
    TASK_QUEUE_DB = "TASK_QUEUE_DB"
    TASK_QUEUE_PASSWORD = "TASK_QUEUE_PASSWORD"
    TASK_WORKERS = "TASK_WORKERS"


# File extensions and MIME types
class FileTypes:
    """File type constants."""
    # Extensions
    PYTHON = ".py"
    JSON = ".json"
    YAML = ".yaml"
    YML = ".yml"
    XML = ".xml"
    CSV = ".csv"
    TXT = ".txt"
    LOG = ".log"
    DB = ".db"
    SQLITE = ".sqlite"
    
    # MIME types
    MIME_JSON = "application/json"
    MIME_YAML = "application/x-yaml"
    MIME_XML = "application/xml"
    MIME_CSV = "text/csv"
    MIME_TEXT = "text/plain"
    MIME_BINARY = "application/octet-stream"


# Time constants
class TimeConstants:
    """Time-related constants."""
    # Durations in seconds
    SECOND = 1
    MINUTE = 60
    HOUR = 3600
    DAY = 86400
    WEEK = 604800
    MONTH = 2592000  # 30 days
    YEAR = 31536000  # 365 days
    
    # Common intervals
    HEARTBEAT_INTERVAL = 30
    HEALTH_CHECK_INTERVAL = 60
    CACHE_CLEANUP_INTERVAL = 300
    LOG_ROTATION_INTERVAL = 86400
    METRICS_COLLECTION_INTERVAL = 60
