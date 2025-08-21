"""
System Configuration for Twin Registry
Comprehensive configuration management for all system components
"""

import json
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime, timezone
import yaml

logger = logging.getLogger(__name__)


class ConfigEnvironment(Enum):
    """Configuration environments"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class ConfigSecurityLevel(Enum):
    """Configuration security levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


@dataclass
class RegistrySettings:
    """Registry core settings"""
    max_twins: int = 10000
    max_instances_per_twin: int = 50
    max_relationships_per_twin: int = 100
    enable_relationships: bool = True
    enable_lifecycle_tracking: bool = True
    enable_performance_monitoring: bool = True
    enable_audit_logging: bool = True
    data_retention_days: int = 2555  # 7 years
    backup_frequency_hours: int = 24
    enable_data_compression: bool = True
    enable_data_encryption: bool = True
    max_concurrent_operations: int = 100
    operation_timeout_seconds: int = 300


@dataclass
class MonitoringSettings:
    """System monitoring settings"""
    enable_monitoring: bool = True
    monitoring_interval_seconds: int = 30
    health_check_interval_seconds: int = 60
    performance_metrics_retention_days: int = 90
    alert_retention_days: int = 30
    enable_real_time_monitoring: bool = True
    enable_predictive_analytics: bool = True
    enable_anomaly_detection: bool = True
    monitoring_dashboard_refresh_seconds: int = 15
    max_monitoring_data_points: int = 10000
    enable_auto_scaling: bool = False
    scaling_threshold_cpu: float = 80.0
    scaling_threshold_memory: float = 85.0


@dataclass
class SecuritySettings:
    """Security configuration settings"""
    enable_authentication: bool = True
    enable_authorization: bool = True
    enable_audit_logging: bool = True
    session_timeout_minutes: int = 30
    max_login_attempts: int = 5
    password_min_length: int = 12
    password_complexity_required: bool = True
    enable_two_factor_auth: bool = False
    enable_api_rate_limiting: bool = True
    max_api_requests_per_minute: int = 1000
    enable_ip_whitelisting: bool = False
    allowed_ip_ranges: List[str] = field(default_factory=list)
    enable_data_encryption_at_rest: bool = True
    enable_data_encryption_in_transit: bool = True
    encryption_algorithm: str = "AES-256-GCM"
    enable_ssl_tls: bool = True
    ssl_certificate_path: Optional[str] = None
    ssl_private_key_path: Optional[str] = None


@dataclass
class IntegrationSettings:
    """External integration settings"""
    enable_etl_integration: bool = True
    etl_sync_interval_seconds: int = 300
    etl_timeout_seconds: int = 60
    enable_file_upload: bool = True
    max_file_size_mb: int = 100
    allowed_file_types: List[str] = field(default_factory=lambda: [".aasx", ".json", ".xml", ".yaml"])
    enable_ai_rag_integration: bool = True
    ai_rag_api_endpoint: Optional[str] = None
    ai_rag_api_key: Optional[str] = None
    enable_external_apis: bool = True
    external_api_timeout_seconds: int = 30
    enable_webhook_notifications: bool = False
    webhook_endpoints: List[str] = field(default_factory=list)
    enable_third_party_connectors: bool = False


@dataclass
class UISettings:
    """User interface configuration"""
    refresh_interval_seconds: int = 30
    show_advanced_options: bool = False
    enable_real_time_updates: bool = True
    enable_dark_mode: bool = True
    enable_animations: bool = True
    max_table_rows_per_page: int = 50
    enable_infinite_scroll: bool = False
    enable_keyboard_shortcuts: bool = True
    enable_tooltips: bool = True
    enable_context_menus: bool = True
    enable_drag_and_drop: bool = True
    enable_search_highlighting: bool = True
    enable_auto_save: bool = True
    auto_save_interval_seconds: int = 60
    enable_undo_redo: bool = True
    max_undo_steps: int = 50


@dataclass
class PerformanceSettings:
    """Performance optimization settings"""
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    max_cache_size_mb: int = 512
    enable_query_optimization: bool = True
    enable_index_optimization: bool = True
    enable_connection_pooling: bool = True
    max_database_connections: int = 50
    database_connection_timeout_seconds: int = 30
    enable_background_processing: bool = True
    background_worker_threads: int = 4
    enable_async_operations: bool = True
    max_concurrent_async_operations: int = 20
    enable_batch_processing: bool = True
    batch_size: int = 100
    enable_streaming: bool = True


@dataclass
class NotificationSettings:
    """Notification and alerting settings"""
    enable_email_notifications: bool = False
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    enable_sms_notifications: bool = False
    sms_provider: Optional[str] = None
    sms_api_key: Optional[str] = None
    enable_push_notifications: bool = False
    push_service_endpoint: Optional[str] = None
    enable_slack_notifications: bool = False
    slack_webhook_url: Optional[str] = None
    enable_teams_notifications: bool = False
    teams_webhook_url: Optional[str] = None
    notification_retry_attempts: int = 3
    notification_retry_delay_seconds: int = 60


@dataclass
class BackupSettings:
    """Backup and recovery settings"""
    enable_automatic_backups: bool = True
    backup_schedule: str = "0 2 * * *"  # Cron format: daily at 2 AM
    backup_retention_days: int = 30
    backup_compression: bool = True
    backup_encryption: bool = True
    backup_storage_path: str = "./backups"
    backup_storage_type: str = "local"  # local, s3, azure, gcp
    backup_verification: bool = True
    enable_incremental_backups: bool = True
    enable_point_in_time_recovery: bool = False
    max_backup_size_gb: int = 10


@dataclass
class SystemConfiguration:
    """Complete system configuration"""
    
    # Basic identification
    config_id: str = field(default_factory=lambda: f"config_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    version: str = "1.0.0"
    environment: ConfigEnvironment = ConfigEnvironment.DEVELOPMENT
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    # Security classification
    security_level: ConfigSecurityLevel = ConfigSecurityLevel.INTERNAL
    
    # Component configurations
    registry: RegistrySettings = field(default_factory=RegistrySettings)
    monitoring: MonitoringSettings = field(default_factory=MonitoringSettings)
    security: SecuritySettings = field(default_factory=SecuritySettings)
    integration: IntegrationSettings = field(default_factory=IntegrationSettings)
    ui: UISettings = field(default_factory=UISettings)
    performance: PerformanceSettings = field(default_factory=PerformanceSettings)
    notifications: NotificationSettings = field(default_factory=NotificationSettings)
    backup: BackupSettings = field(default_factory=BackupSettings)
    
    # Custom configurations
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        config_dict = asdict(self)
        config_dict['environment'] = self.environment.value
        config_dict['security_level'] = self.security_level.value
        config_dict['created_at'] = self.created_at.isoformat()
        config_dict['updated_at'] = self.updated_at.isoformat()
        return config_dict
    
    def to_json(self, indent: int = 2) -> str:
        """Convert configuration to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, default=str)
    
    def to_yaml(self) -> str:
        """Convert configuration to YAML string"""
        return yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'SystemConfiguration':
        """Create configuration from dictionary"""
        # Handle enum conversions
        if 'environment' in config_dict:
            config_dict['environment'] = ConfigEnvironment(config_dict['environment'])
        if 'security_level' in config_dict:
            config_dict['security_level'] = ConfigSecurityLevel(config_dict['security_level'])
        
        # Handle datetime conversions
        if 'created_at' in config_dict and isinstance(config_dict['created_at'], str):
            config_dict['created_at'] = datetime.fromisoformat(config_dict['created_at'].replace('Z', '+00:00'))
        if 'updated_at' in config_dict and isinstance(config_dict['updated_at'], str):
            config_dict['updated_at'] = datetime.fromisoformat(config_dict['updated_at'].replace('Z', '+00:00'))
        
        return cls(**config_dict)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SystemConfiguration':
        """Create configuration from JSON string"""
        config_dict = json.loads(json_str)
        return cls.from_dict(config_dict)
    
    @classmethod
    def from_yaml(cls, yaml_str: str) -> 'SystemConfiguration':
        """Create configuration from YAML string"""
        config_dict = yaml.safe_load(yaml_str)
        return cls.from_dict(config_dict)
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        # Validate registry settings
        if self.registry.max_twins <= 0:
            errors.append("max_twins must be positive")
        if self.registry.max_instances_per_twin <= 0:
            errors.append("max_instances_per_twin must be positive")
        if self.registry.data_retention_days <= 0:
            errors.append("data_retention_days must be positive")
        
        # Validate monitoring settings
        if self.monitoring.monitoring_interval_seconds <= 0:
            errors.append("monitoring_interval_seconds must be positive")
        if self.monitoring.health_check_interval_seconds <= 0:
            errors.append("health_check_interval_seconds must be positive")
        
        # Validate security settings
        if self.security.session_timeout_minutes <= 0:
            errors.append("session_timeout_minutes must be positive")
        if self.security.max_login_attempts <= 0:
            errors.append("max_login_attempts must be positive")
        if self.security.password_min_length < 8:
            errors.append("password_min_length must be at least 8")
        
        # Validate UI settings
        if self.ui.refresh_interval_seconds <= 0:
            errors.append("refresh_interval_seconds must be positive")
        if self.ui.max_table_rows_per_page <= 0:
            errors.append("max_table_rows_per_page must be positive")
        
        # Validate performance settings
        if self.performance.cache_ttl_seconds <= 0:
            errors.append("cache_ttl_seconds must be positive")
        if self.performance.max_database_connections <= 0:
            errors.append("max_database_connections must be positive")
        
        # Validate backup settings
        if self.backup.backup_retention_days <= 0:
            errors.append("backup_retention_days must be positive")
        if self.backup.max_backup_size_gb <= 0:
            errors.append("max_backup_size_gb must be positive")
        
        return errors
    
    def is_valid(self) -> bool:
        """Check if configuration is valid"""
        return len(self.validate()) == 0
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values"""
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                # Try to update nested settings
                for attr_name in dir(self):
                    attr = getattr(self, attr_name)
                    if hasattr(attr, key):
                        setattr(attr, key, value)
                        break
        
        self.updated_at = datetime.now(timezone.utc)
    
    def get_setting(self, path: str) -> Any:
        """Get setting value using dot notation (e.g., 'registry.max_twins')"""
        keys = path.split('.')
        current = self
        
        for key in keys:
            if hasattr(current, key):
                current = getattr(current, key)
            else:
                return None
        
        return current
    
    def set_setting(self, path: str, value: Any) -> bool:
        """Set setting value using dot notation (e.g., 'registry.max_twins')"""
        keys = path.split('.')
        current = self
        
        # Navigate to parent object
        for key in keys[:-1]:
            if hasattr(current, key):
                current = getattr(current, key)
            else:
                return False
        
        # Set the value
        if hasattr(current, keys[-1]):
            setattr(current, keys[-1], value)
            self.updated_at = datetime.now(timezone.utc)
            return True
        
        return False


class ConfigurationManager:
    """Manages system configuration"""
    
    def __init__(self, config_file_path: Optional[str] = None):
        self.config_file_path = config_file_path or "config/twin_registry_config.json"
        self.config = SystemConfiguration()
        self.config_history: List[SystemConfiguration] = []
        self.max_history_size = 10
        
        # Load configuration
        self.load_configuration()
    
    def load_configuration(self) -> None:
        """Load configuration from file"""
        try:
            config_path = Path(self.config_file_path)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config_dict = json.load(f)
                    self.config = SystemConfiguration.from_dict(config_dict)
                    logger.info(f"Configuration loaded from {self.config_file_path}")
            else:
                logger.info("No configuration file found, using defaults")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            logger.info("Using default configuration")
    
    def save_configuration(self) -> bool:
        """Save configuration to file"""
        try:
            config_path = Path(self.config_file_path)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Add to history before saving
            self.add_to_history()
            
            with open(config_path, 'w') as f:
                json.dump(self.config.to_dict(), f, indent=2, default=str)
            
            logger.info(f"Configuration saved to {self.config_file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def add_to_history(self) -> None:
        """Add current configuration to history"""
        # Create a copy of current config
        config_copy = SystemConfiguration.from_dict(self.config.to_dict())
        config_copy.config_id = f"config_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        config_copy.created_at = datetime.now(timezone.utc)
        
        self.config_history.append(config_copy)
        
        # Limit history size
        if len(self.config_history) > self.max_history_size:
            self.config_history.pop(0)
    
    def get_configuration(self) -> SystemConfiguration:
        """Get current configuration"""
        return self.config
    
    def update_configuration(self, updates: Dict[str, Any]) -> bool:
        """Update configuration with new values"""
        try:
            self.config.update(updates)
            
            # Validate configuration
            if not self.config.is_valid():
                errors = self.config.validate()
                logger.error(f"Configuration validation failed: {errors}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return False
    
    def reset_configuration(self, reset_type: str = "defaults") -> bool:
        """Reset configuration to defaults or previous version"""
        try:
            if reset_type == "defaults":
                self.config = SystemConfiguration()
            elif reset_type == "previous" and self.config_history:
                self.config = self.config_history[-1]
            else:
                logger.error(f"Invalid reset type: {reset_type}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Failed to reset configuration: {e}")
            return False
    
    def export_configuration(self, format: str = "json") -> str:
        """Export configuration in specified format"""
        try:
            if format.lower() == "yaml":
                return self.config.to_yaml()
            else:
                return self.config.to_json()
        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")
            return ""
    
    def import_configuration(self, config_data: str, format: str = "json") -> bool:
        """Import configuration from string"""
        try:
            if format.lower() == "yaml":
                new_config = SystemConfiguration.from_yaml(config_data)
            else:
                new_config = SystemConfiguration.from_json(config_data)
            
            # Validate imported configuration
            if not new_config.is_valid():
                errors = new_config.validate()
                logger.error(f"Imported configuration validation failed: {errors}")
                return False
            
            # Add to history and replace current
            self.add_to_history()
            self.config = new_config
            
            return True
        except Exception as e:
            logger.error(f"Failed to import configuration: {e}")
            return False
    
    def get_configuration_history(self) -> List[Dict[str, Any]]:
        """Get configuration history"""
        return [config.to_dict() for config in self.config_history]
    
    def rollback_to_version(self, config_id: str) -> bool:
        """Rollback to specific configuration version"""
        try:
            for config in self.config_history:
                if config.config_id == config_id:
                    self.add_to_history()
                    self.config = SystemConfiguration.from_dict(config.to_dict())
                    return True
            
            logger.error(f"Configuration version {config_id} not found")
            return False
        except Exception as e:
            logger.error(f"Failed to rollback configuration: {e}")
            return False
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate current configuration"""
        errors = self.config.validate()
        warnings = []
        
        # Add warnings for potentially problematic settings
        if self.config.registry.max_twins > 100000:
            warnings.append("max_twins is very high, consider reducing for performance")
        if self.config.monitoring.monitoring_interval_seconds < 10:
            warnings.append("monitoring_interval_seconds is very low, may impact performance")
        if self.config.security.password_min_length < 12:
            warnings.append("password_min_length is below recommended security standards")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def get_environment_config(self, environment: ConfigEnvironment) -> Dict[str, Any]:
        """Get environment-specific configuration overrides"""
        # This could load from environment-specific config files
        # For now, return basic overrides
        overrides = {
            ConfigEnvironment.DEVELOPMENT: {
                "monitoring.monitoring_interval_seconds": 10,
                "ui.refresh_interval_seconds": 5,
                "security.enable_two_factor_auth": False
            },
            ConfigEnvironment.PRODUCTION: {
                "monitoring.monitoring_interval_seconds": 60,
                "ui.refresh_interval_seconds": 60,
                "security.enable_two_factor_auth": True
            }
        }
        
        return overrides.get(environment, {})
    
    def apply_environment_overrides(self, environment: ConfigEnvironment) -> None:
        """Apply environment-specific configuration overrides"""
        overrides = self.get_environment_config(environment)
        
        for path, value in overrides.items():
            self.config.set_setting(path, value)
        
        self.config.environment = environment
        logger.info(f"Applied {environment.value} environment overrides")


# Default configuration instance
default_config = SystemConfiguration()
