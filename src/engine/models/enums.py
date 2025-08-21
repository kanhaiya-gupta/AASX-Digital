"""
Comprehensive Enums & Constants
==============================

World-class enums and constants for the AAS Data Modeling Engine.
Provides type safety, validation, and business rule enforcement.
"""

from enum import Enum, auto
from typing import Dict, Any, List


class SystemCategory(Enum):
    """System categories for classification."""
    INFRASTRUCTURE = "infrastructure"
    APPLICATION = "application"
    DATA = "data"
    INTEGRATION = "integration"
    SECURITY = "security"
    MONITORING = "monitoring"
    ANALYTICS = "analytics"
    AUTOMATION = "automation"


class SystemType(Enum):
    """System types for technical classification."""
    MICROSERVICE = "microservice"
    MONOLITH = "monolith"
    EVENT_DRIVEN = "event_driven"
    API_FIRST = "api_first"
    DATA_LAKE = "data_lake"
    WAREHOUSE = "warehouse"
    STREAMING = "streaming"
    BATCH = "batch"


class SystemPriority(Enum):
    """System priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MAINTENANCE = "maintenance"


class RegistryType(Enum):
    """Registry type classifications."""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    HYBRID = "hybrid"
    FEDERATED = "federated"
    HIERARCHICAL = "hierarchical"


class WorkflowSource(Enum):
    """Workflow source types."""
    MANUAL = "manual"
    AUTOMATED = "automated"
    SCHEDULED = "scheduled"
    EVENT_TRIGGERED = "event_triggered"
    BOTH = "both"


class SecurityLevel(Enum):
    """Security classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"


class HealthStatus(Enum):
    """System health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    MAINTENANCE = "maintenance"


class CompanySize(Enum):
    """Organization size classifications."""
    STARTUP = "startup"
    SMB = "smb"
    ENTERPRISE = "enterprise"
    GOVERNMENT = "government"
    NON_PROFIT = "non_profit"


class SubscriptionTier(Enum):
    """Subscription tier levels."""
    FREE = "free"
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class DataDomain(Enum):
    """Data domain classifications."""
    THERMAL = "thermal"
    ELECTRICAL = "electrical"
    MECHANICAL = "mechanical"
    CHEMICAL = "chemical"
    BIOLOGICAL = "biological"
    ENVIRONMENTAL = "environmental"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"


class BusinessCriticality(Enum):
    """Business criticality levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NON_CRITICAL = "non_critical"


class ProjectPhase(Enum):
    """Project lifecycle phases."""
    PLANNING = "planning"
    ANALYSIS = "analysis"
    DESIGN = "design"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    MAINTENANCE = "maintenance"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PriorityLevel(Enum):
    """Project priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    OPTIONAL = "optional"


class FileStatus(Enum):
    """File processing status."""
    NOT_PROCESSED = "not_processed"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    ARCHIVED = "archived"
    DELETED = "deleted"


class SourceType(Enum):
    """File source types."""
    MANUAL_UPLOAD = "manual_upload"
    API_IMPORT = "api_import"
    BATCH_IMPORT = "batch_import"
    STREAMING = "streaming"
    INTEGRATION = "integration"
    BACKUP_RESTORE = "backup_restore"


class UserRole(Enum):
    """User role classifications."""
    ADMIN = "admin"
    USER = "user"
    MANAGER = "manager"
    ANALYST = "analyst"
    DEVELOPER = "developer"
    VIEWER = "viewer"
    GUEST = "guest"


class RoleType(Enum):
    """Role type classifications."""
    SYSTEM = "system"
    CUSTOM = "custom"
    INHERITED = "inherited"
    TEMPORARY = "temporary"
    DELEGATED = "delegated"


class AssignmentType(Enum):
    """Role assignment types."""
    DIRECT = "direct"
    INHERITED = "inherited"
    GROUP = "group"
    DELEGATED = "delegated"
    TEMPORARY = "temporary"


class MetricType(Enum):
    """Metric type classifications."""
    PERFORMANCE = "performance"
    SECURITY = "security"
    AVAILABILITY = "availability"
    USAGE = "usage"
    BUSINESS = "business"
    TECHNICAL = "technical"
    USER = "user"
    SYSTEM = "system"


# Business Constants
class BusinessConstants:
    """Business rule constants."""
    
    # Health Score Ranges
    HEALTH_SCORE_MIN = 0.0
    HEALTH_SCORE_MAX = 100.0
    HEALTH_SCORE_THRESHOLD = 80.0
    
    # File Size Limits
    MAX_FILE_SIZE_MB = 1000  # 1GB
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    
    # Password Requirements
    MIN_PASSWORD_LENGTH = 8
    PASSWORD_COMPLEXITY_REQUIRED = True
    
    # Rate Limiting
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30
    
    # Session Management
    SESSION_TIMEOUT_MINUTES = 60
    MAX_CONCURRENT_SESSIONS = 3
    
    # Audit Retention
    AUDIT_LOG_RETENTION_DAYS = 2555  # 7 years
    USER_ACTIVITY_RETENTION_DAYS = 365  # 1 year


# Validation Rules
class ValidationRules:
    """Business validation rules."""
    
    # Email Validation
    EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Username Validation
    USERNAME_MIN_LENGTH = 3
    USERNAME_MAX_LENGTH = 50
    USERNAME_REGEX = r'^[a-zA-Z0-9_-]+$'
    
    # Organization Name Validation
    ORG_NAME_MIN_LENGTH = 2
    ORG_NAME_MAX_LENGTH = 100
    
    # Project Name Validation
    PROJECT_NAME_MIN_LENGTH = 3
    PROJECT_NAME_MAX_LENGTH = 100
    
    # File Name Validation
    FILENAME_MAX_LENGTH = 255
    FILENAME_INVALID_CHARS = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    
    # Description Validation
    DESCRIPTION_MAX_LENGTH = 1000
    
    # Tags Validation
    MAX_TAGS_PER_ENTITY = 20
    TAG_MAX_LENGTH = 50


# Status Mappings
class StatusMappings:
    """Status and state mappings."""
    
    # Health Score to Status
    HEALTH_STATUS_MAPPING = {
        (90, 100): HealthStatus.HEALTHY,
        (70, 89): HealthStatus.HEALTHY,
        (50, 69): HealthStatus.DEGRADED,
        (30, 49): HealthStatus.DEGRADED,
        (0, 29): HealthStatus.UNHEALTHY
    }
    
    # Priority to SLA Mapping
    PRIORITY_SLA_HOURS = {
        PriorityLevel.CRITICAL: 1,
        PriorityLevel.HIGH: 4,
        PriorityLevel.MEDIUM: 24,
        PriorityLevel.LOW: 72,
        PriorityLevel.OPTIONAL: 168  # 1 week
    }
    
    # Project Phase Transitions
    VALID_PHASE_TRANSITIONS = {
        ProjectPhase.PLANNING: [ProjectPhase.ANALYSIS, ProjectPhase.CANCELLED],
        ProjectPhase.ANALYSIS: [ProjectPhase.DESIGN, ProjectPhase.PLANNING, ProjectPhase.CANCELLED],
        ProjectPhase.DESIGN: [ProjectPhase.DEVELOPMENT, ProjectPhase.ANALYSIS, ProjectPhase.CANCELLED],
        ProjectPhase.DEVELOPMENT: [ProjectPhase.TESTING, ProjectPhase.DESIGN, ProjectPhase.CANCELLED],
        ProjectPhase.TESTING: [ProjectPhase.DEPLOYMENT, ProjectPhase.DEVELOPMENT, ProjectPhase.CANCELLED],
        ProjectPhase.DEPLOYMENT: [ProjectPhase.MAINTENANCE, ProjectPhase.TESTING, ProjectPhase.CANCELLED],
        ProjectPhase.MAINTENANCE: [ProjectPhase.COMPLETED, ProjectPhase.DEPLOYMENT, ProjectPhase.CANCELLED],
        ProjectPhase.COMPLETED: [ProjectPhase.MAINTENANCE],
        ProjectPhase.CANCELLED: []
    }


# Business Logic Constants
class BusinessLogicConstants:
    """Business logic constants."""
    
    # Partner Ecosystem
    MAX_PARTNERS_PER_ORG = 100
    PARTNER_VERIFICATION_REQUIRED = True
    
    # Project Management
    MAX_PROJECTS_PER_ORG = 1000
    MAX_USE_CASES_PER_PROJECT = 50
    PROJECT_ARCHIVAL_THRESHOLD_DAYS = 365
    
    # File Management
    MAX_FILES_PER_PROJECT = 10000
    FILE_PROCESSING_TIMEOUT_SECONDS = 300
    SUPPORTED_FILE_TYPES = [
        '.txt', '.csv', '.json', '.xml', '.yaml', '.yml',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx',
        '.aasx', '.ttl', '.rdf', '.owl'
    ]
    
    # User Management
    MAX_USERS_PER_ORG = 10000
    MAX_ROLES_PER_USER = 20
    PASSWORD_EXPIRY_DAYS = 90
    
    # Metrics Collection
    METRICS_COLLECTION_INTERVAL_SECONDS = 300
    METRICS_RETENTION_DAYS = 1095  # 3 years
    
    # Audit and Compliance
    AUDIT_LOG_ENCRYPTION_REQUIRED = True
    COMPLIANCE_REPORTING_FREQUENCY_DAYS = 30
    DATA_RETENTION_POLICY_ENFORCED = True


# Cache Configuration
class CacheConfig:
    """Cache configuration constants."""
    
    # TTL Values (Time To Live)
    USER_SESSION_TTL_SECONDS = 3600  # 1 hour
    ORGANIZATION_CACHE_TTL_SECONDS = 1800  # 30 minutes
    PROJECT_CACHE_TTL_SECONDS = 900  # 15 minutes
    FILE_METADATA_CACHE_TTL_SECONDS = 600  # 10 minutes
    ROLE_PERMISSIONS_CACHE_TTL_SECONDS = 7200  # 2 hours
    
    # Cache Size Limits
    MAX_CACHE_SIZE_MB = 100
    MAX_CACHE_ENTRIES = 10000
    
    # Eviction Policies
    CACHE_EVICTION_POLICY = "LRU"  # Least Recently Used
    CACHE_CLEANUP_INTERVAL_SECONDS = 300  # 5 minutes


# Performance Constants
class PerformanceConstants:
    """Performance optimization constants."""
    
    # Database Connection Pool
    DB_POOL_MIN_SIZE = 5
    DB_POOL_MAX_SIZE = 20
    DB_POOL_TIMEOUT_SECONDS = 30
    
    # Batch Processing
    BATCH_SIZE_DEFAULT = 100
    BATCH_SIZE_MAX = 1000
    BATCH_TIMEOUT_SECONDS = 60
    
    # Async Processing
    MAX_CONCURRENT_TASKS = 10
    TASK_TIMEOUT_SECONDS = 300
    
    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Rate Limiting
    REQUESTS_PER_MINUTE = 1000
    REQUESTS_PER_HOUR = 10000


# Security Constants
class SecurityConstants:
    """Security configuration constants."""
    
    # Password Hashing
    PASSWORD_HASH_ALGORITHM = "bcrypt"
    PASSWORD_SALT_ROUNDS = 12
    
    # JWT Configuration
    JWT_SECRET_KEY_MIN_LENGTH = 32
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRY_HOURS = 24
    
    # API Security
    API_RATE_LIMIT_ENABLED = True
    API_KEY_REQUIRED = True
    CORS_ENABLED = True
    
    # Data Encryption
    ENCRYPTION_ALGORITHM = "AES-256-GCM"
    ENCRYPTION_KEY_ROTATION_DAYS = 90
    
    # Audit Security
    AUDIT_LOG_IMMUTABLE = True
    AUDIT_LOG_SIGNING_REQUIRED = True
    AUDIT_LOG_BACKUP_ENCRYPTED = True


# Event Types for Observer Pattern
class EventType(Enum):
    """Event types for the observer pattern."""
    
    # User Events
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_ROLE_CHANGED = "user_role_changed"
    
    # Organization Events
    ORG_CREATED = "org_created"
    ORG_UPDATED = "org_updated"
    ORG_DELETED = "org_deleted"
    ORG_PARTNER_ADDED = "org_partner_added"
    ORG_PARTNER_REMOVED = "org_partner_removed"
    
    # Project Events
    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    PROJECT_DELETED = "project_deleted"
    PROJECT_PHASE_CHANGED = "project_phase_changed"
    PROJECT_COMPLETED = "project_completed"
    
    # File Events
    FILE_UPLOADED = "file_uploaded"
    FILE_PROCESSED = "file_processed"
    FILE_DELETED = "file_deleted"
    FILE_STATUS_CHANGED = "file_status_changed"
    
    # System Events
    SYSTEM_HEALTH_CHANGED = "system_health_changed"
    SYSTEM_METRICS_COLLECTED = "system_metrics_collected"
    SYSTEM_MAINTENANCE_STARTED = "system_maintenance_started"
    SYSTEM_MAINTENANCE_COMPLETED = "system_maintenance_completed"
    
    # Security Events
    SECURITY_ALERT = "security_alert"
    ACCESS_DENIED = "access_denied"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    COMPLIANCE_VIOLATION = "compliance_violation"


# Plugin Architecture Constants
class PluginConstants:
    """Plugin architecture constants."""
    
    # Plugin Types
    PLUGIN_TYPES = [
        "validator",
        "processor",
        "exporter",
        "importer",
        "analyzer",
        "reporter",
        "notifier",
        "integrator"
    ]
    
    # Plugin Lifecycle
    PLUGIN_LOAD_TIMEOUT_SECONDS = 30
    PLUGIN_UNLOAD_TIMEOUT_SECONDS = 10
    PLUGIN_HEALTH_CHECK_INTERVAL_SECONDS = 60
    
    # Plugin Security
    PLUGIN_SANDBOX_ENABLED = True
    PLUGIN_PERMISSIONS_REQUIRED = True
    PLUGIN_CODE_SIGNING_REQUIRED = True
    
    # Plugin Registry
    PLUGIN_REGISTRY_URL = "https://plugins.aas-engine.com"
    PLUGIN_UPDATE_CHECK_INTERVAL_HOURS = 24
    PLUGIN_AUTO_UPDATE_ENABLED = False


# Export all enums and constants
__all__ = [
    # Enums
    'SystemCategory', 'SystemType', 'SystemPriority', 'RegistryType', 'WorkflowSource',
    'SecurityLevel', 'HealthStatus', 'CompanySize', 'SubscriptionTier', 'DataDomain',
    'BusinessCriticality', 'ProjectPhase', 'PriorityLevel', 'FileStatus', 'SourceType',
    'UserRole', 'RoleType', 'AssignmentType', 'MetricType', 'EventType',
    
    # Constants
    'BusinessConstants', 'ValidationRules', 'StatusMappings', 'BusinessLogicConstants',
    'CacheConfig', 'PerformanceConstants', 'SecurityConstants', 'PluginConstants'
]
