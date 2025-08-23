"""
AASX Module Configuration Settings

Comprehensive configuration management for AASX processing operations.
"""

import os
from typing import Dict, Any, Optional, List
from pathlib import Path
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseModel):
    """Database configuration settings."""
    
    connection_timeout: int = Field(default=30, description="Database connection timeout in seconds")
    pool_size: int = Field(default=10, description="Database connection pool size")
    max_overflow: int = Field(default=20, description="Maximum database connection overflow")
    echo: bool = Field(default=False, description="Enable SQL query logging")


class ProcessingConfig(BaseModel):
    """AASX processing configuration settings."""
    
    # File processing limits
    max_file_size_mb: int = Field(default=100, description="Maximum file size in MB")
    max_concurrent_jobs: int = Field(default=5, description="Maximum concurrent processing jobs")
    job_timeout_seconds: int = Field(default=3600, description="Job timeout in seconds")
    
    # Processing options
    enable_validation: bool = Field(default=True, description="Enable AASX validation")
    enable_checksum_verification: bool = Field(default=True, description="Enable file checksum verification")
    enable_metadata_extraction: bool = Field(default=True, description="Enable metadata extraction")
    
    # Output formats
    supported_output_formats: List[str] = Field(
        default=["json", "xml", "yaml", "ttl"],
        description="Supported output formats"
    )
    
    # Quality settings
    min_quality_score: float = Field(default=0.7, description="Minimum quality score threshold")
    enable_quality_metrics: bool = Field(default=True, description="Enable quality metrics collection")
    
    # Performance settings
    enable_performance_monitoring: bool = Field(default=True, description="Enable performance monitoring")
    metrics_collection_interval: int = Field(default=60, description="Metrics collection interval in seconds")
    
    @validator('min_quality_score')
    def validate_quality_score(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Quality score must be between 0.0 and 1.0')
        return v


class SecurityConfig(BaseModel):
    """Security configuration settings."""
    
    # Access control
    enable_access_control: bool = Field(default=True, description="Enable access control")
    default_security_level: str = Field(default="standard", description="Default security level")
    allowed_security_levels: List[str] = Field(
        default=["low", "standard", "high", "critical"],
        description="Allowed security levels"
    )
    
    # Encryption
    enable_encryption: bool = Field(default=False, description="Enable data encryption")
    encryption_algorithm: str = Field(default="AES-256", description="Encryption algorithm")
    
    # Audit logging
    enable_audit_logging: bool = Field(default=True, description="Enable audit logging")
    audit_log_retention_days: int = Field(default=365, description="Audit log retention in days")
    
    @validator('default_security_level')
    def validate_security_level(cls, v, values):
        if 'allowed_security_levels' in values and v not in values['allowed_security_levels']:
            raise ValueError(f'Security level must be one of: {values["allowed_security_levels"]}')
        return v


class IntegrationConfig(BaseModel):
    """Integration configuration settings."""
    
    # External tools
    aasx_processor_path: Optional[str] = Field(default=None, description="Path to AASX processor executable")
    enable_external_processor: bool = Field(default=True, description="Enable external AASX processor")
    
    # API integration
    enable_api_integration: bool = Field(default=True, description="Enable API integration")
    api_timeout_seconds: int = Field(default=30, description="API request timeout in seconds")
    api_retry_attempts: int = Field(default=3, description="API retry attempts")
    
    # Webhook settings
    enable_webhooks: bool = Field(default=False, description="Enable webhook notifications")
    webhook_timeout_seconds: int = Field(default=10, description="Webhook timeout in seconds")
    
    # Event streaming
    enable_event_streaming: bool = Field(default=False, description="Enable event streaming")
    event_stream_batch_size: int = Field(default=100, description="Event stream batch size")


class MonitoringConfig(BaseModel):
    """Monitoring and alerting configuration settings."""
    
    # Health monitoring
    enable_health_monitoring: bool = Field(default=True, description="Enable health monitoring")
    health_check_interval: int = Field(default=300, description="Health check interval in seconds")
    health_score_threshold: int = Field(default=70, description="Health score threshold")
    
    # Alerting
    enable_alerts: bool = Field(default=True, description="Enable alerting")
    alert_channels: List[str] = Field(
        default=["email", "slack"],
        description="Alert notification channels"
    )
    
    # Metrics retention
    metrics_retention_days: int = Field(default=90, description="Metrics retention in days")
    enable_metrics_aggregation: bool = Field(default=True, description="Enable metrics aggregation")
    
    # Performance thresholds
    max_processing_time_seconds: int = Field(default=1800, description="Maximum processing time threshold")
    max_memory_usage_percent: int = Field(default=80, description="Maximum memory usage threshold")
    max_cpu_usage_percent: int = Field(default=90, description="Maximum CPU usage threshold")


class StorageConfig(BaseModel):
    """Storage configuration settings."""
    
    # File storage
    base_output_directory: str = Field(default="./output", description="Base output directory")
    enable_file_compression: bool = Field(default=True, description="Enable file compression")
    compression_format: str = Field(default="zip", description="File compression format")
    
    # Temporary storage
    temp_directory: str = Field(default="./temp", description="Temporary file directory")
    cleanup_temp_files: bool = Field(default=True, description="Clean up temporary files")
    temp_file_retention_hours: int = Field(default=24, description="Temporary file retention in hours")
    
    # Backup settings
    enable_backups: bool = Field(default=True, description="Enable automatic backups")
    backup_retention_days: int = Field(default=30, description="Backup retention in days")
    backup_schedule: str = Field(default="daily", description="Backup schedule")


class ValidationConfig(BaseModel):
    """Validation configuration settings."""
    
    # AASX validation
    enable_schema_validation: bool = Field(default=True, description="Enable AASX schema validation")
    strict_validation: bool = Field(default=False, description="Enable strict validation mode")
    validation_timeout_seconds: int = Field(default=300, description="Validation timeout in seconds")
    
    # Content validation
    validate_file_integrity: bool = Field(default=True, description="Validate file integrity")
    validate_content_structure: bool = Field(default=True, description="Validate content structure")
    validate_references: bool = Field(default=True, description="Validate internal references")
    
    # Error handling
    max_validation_errors: int = Field(default=100, description="Maximum validation errors to report")
    fail_fast: bool = Field(default=False, description="Fail validation on first error")


class AASXConfig(BaseSettings):
    """Main AASX configuration class."""
    
    # Environment
    environment: str = Field(default="development", description="Environment (development, staging, production)")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Module configuration
    module_name: str = Field(default="aasx", description="Module name")
    module_version: str = Field(default="2.0.0", description="Module version")
    
    # Sub-configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    integration: IntegrationConfig = Field(default_factory=IntegrationConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    
    class Config:
        env_prefix = "AASX_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration."""
        return {
            "environment": self.environment,
            "debug": self.debug,
            "log_level": self.log_level,
            "module_version": self.module_version,
            "processing": {
                "max_file_size_mb": self.processing.max_file_size_mb,
                "max_concurrent_jobs": self.processing.max_concurrent_jobs,
                "enable_validation": self.processing.enable_validation
            },
            "security": {
                "enable_access_control": self.security.enable_access_control,
                "enable_encryption": self.security.enable_encryption,
                "enable_audit_logging": self.security.enable_audit_logging
            },
            "monitoring": {
                "enable_health_monitoring": self.monitoring.enable_health_monitoring,
                "enable_alerts": self.monitoring.enable_alerts,
                "health_score_threshold": self.monitoring.health_score_threshold
            }
        }
    
    def validate_configuration(self) -> List[str]:
        """Validate the configuration and return any issues."""
        issues = []
        
        # Check required directories
        if not os.path.exists(self.storage.base_output_directory):
            issues.append(f"Output directory does not exist: {self.storage.base_output_directory}")
        
        if not os.path.exists(self.storage.temp_directory):
            issues.append(f"Temp directory does not exist: {self.storage.temp_directory}")
        
        # Check external processor
        if self.integration.enable_external_processor and self.integration.aasx_processor_path:
            if not os.path.exists(self.integration.aasx_processor_path):
                issues.append(f"AASX processor not found: {self.integration.aasx_processor_path}")
        
        # Check security configuration
        if self.security.enable_encryption and self.security.encryption_algorithm not in ["AES-256", "AES-128"]:
            issues.append(f"Unsupported encryption algorithm: {self.security.encryption_algorithm}")
        
        return issues


# Default configuration instance
default_config = AASXConfig()

# Environment-specific configurations
def get_config(environment: Optional[str] = None) -> AASXConfig:
    """
    Get configuration for a specific environment.
    
    Args:
        environment: Environment name (development, staging, production)
        
    Returns:
        AASXConfig: Configuration instance
    """
    if environment:
        return AASXConfig(environment=environment)
    return default_config


def load_config_from_file(config_file: str) -> AASXConfig:
    """
    Load configuration from a file.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        AASXConfig: Configuration instance
    """
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    
    return AASXConfig(_env_file=config_file)


def get_environment_config() -> AASXConfig:
    """
    Get configuration based on current environment.
    
    Returns:
        AASXConfig: Configuration instance for current environment
    """
    env = os.getenv("AASX_ENVIRONMENT", "development")
    return get_config(env)
