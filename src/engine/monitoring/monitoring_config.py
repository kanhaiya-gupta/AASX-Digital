"""
Monitoring Configuration

Centralized configuration for all monitoring components including
metrics collection, health checks, alerting, and performance profiling.
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class MetricsConfig:
    """Configuration for metrics collection"""
    enabled: bool = True
    collection_interval: int = 60  # seconds
    retention_period: int = 86400  # 24 hours in seconds
    max_metrics_history: int = 10000
    export_formats: List[str] = field(default_factory=lambda: ["json", "csv", "prometheus"])
    custom_metrics: Dict[str, str] = field(default_factory=dict)


@dataclass
class HealthConfig:
    """Configuration for health monitoring"""
    enabled: bool = True
    check_interval: int = 30  # seconds
    timeout: int = 10  # seconds
    max_failures: int = 3
    alert_on_failure: bool = True
    components_to_monitor: List[str] = field(default_factory=lambda: [
        "database", "cache", "messaging", "security", "services"
    ])


@dataclass
class PerformanceConfig:
    """Configuration for performance profiling"""
    enabled: bool = True
    profile_operations: bool = True
    profile_database: bool = True
    profile_cache: bool = True
    profile_api: bool = True
    slow_query_threshold: float = 1.0  # seconds
    max_traces: int = 1000
    sampling_rate: float = 0.1  # 10% of operations


@dataclass
class ResourceConfig:
    """Configuration for resource monitoring"""
    enabled: bool = True
    monitor_cpu: bool = True
    monitor_memory: bool = True
    monitor_disk: bool = True
    monitor_network: bool = True
    monitor_database_connections: bool = True
    monitor_cache_usage: bool = True
    collection_interval: int = 15  # seconds


@dataclass
class AlertConfig:
    """Configuration for alerting"""
    enabled: bool = True
    alert_channels: List[str] = field(default_factory=lambda: ["log", "email"])
    email_recipients: List[str] = field(default_factory=list)
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "cpu_usage": 80.0,
        "memory_usage": 85.0,
        "disk_usage": 90.0,
        "response_time": 5.0,
        "error_rate": 5.0
    })


@dataclass
class LoggingConfig:
    """Configuration for log aggregation and analysis"""
    enabled: bool = True
    level: str = "INFO"
    format: str = "json"  # json, csv, plain, logstash, custom
    output: str = "file"  # file, console, both
    file_path: Optional[Path] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    rotation: str = "size"  # size, time, both
    rotation_interval: str = "1 day"  # 1 hour, 1 day, 1 week
    compression: bool = True
    retention_days: int = 30
    enable_metrics: bool = True
    enable_audit: bool = True
    custom_formatter: Optional[str] = None
    structured_logging: bool = True
    correlation_id: bool = True


@dataclass
class ExportConfig:
    """Configuration for data export and visualization"""
    enabled: bool = True
    export_directory: Path = field(default_factory=lambda: Path("./monitoring_exports"))
    auto_export: bool = True
    export_interval: int = 3600  # 1 hour
    supported_formats: List[str] = field(default_factory=lambda: ["json", "csv", "prometheus", "grafana"])
    compression: bool = True


@dataclass
class MonitoringConfig:
    """Main monitoring configuration class"""
    
    # Component configurations
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    health: HealthConfig = field(default_factory=HealthConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    resources: ResourceConfig = field(default_factory=ResourceConfig)
    alerts: AlertConfig = field(default_factory=AlertConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    export: ExportConfig = field(default_factory=ExportConfig)
    
    # Global settings
    enabled: bool = True
    debug_mode: bool = False
    environment: str = "development"
    service_name: str = "aas-data-modeling-engine"
    version: str = "1.0.0"
    
    def __post_init__(self):
        """Post-initialization setup"""
        # Create export directory if it doesn't exist
        if self.export.enabled:
            self.export.export_directory.mkdir(parents=True, exist_ok=True)
        
        # Set environment from env var if available
        env = os.getenv("MONITORING_ENVIRONMENT")
        if env:
            self.environment = env
            
        # Set debug mode from env var if available
        debug = os.getenv("MONITORING_DEBUG")
        if debug:
            self.debug_mode = debug.lower() in ("true", "1", "yes")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "enabled": self.enabled,
            "debug_mode": self.debug_mode,
            "environment": self.environment,
            "service_name": self.service_name,
            "version": self.version,
            "metrics": self.metrics.__dict__,
            "health": self.health.__dict__,
            "performance": self.performance.__dict__,
            "resources": self.resources.__dict__,
            "alerts": self.alerts.__dict__,
            "logging": self.logging.__dict__,
            "export": self.export.__dict__
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'MonitoringConfig':
        """Create configuration from dictionary"""
        config = cls()
        
        # Update global settings
        for key in ["enabled", "debug_mode", "environment", "service_name", "version"]:
            if key in config_dict:
                setattr(config, key, config_dict[key])
        
        # Update component configurations
        for component in ["metrics", "health", "performance", "resources", "alerts", "logging", "export"]:
            if component in config_dict:
                component_config = getattr(config, component)
                for key, value in config_dict[component].items():
                    if hasattr(component_config, key):
                        setattr(component_config, key, value)
        
        return config
    
    @classmethod
    def from_env(cls) -> 'MonitoringConfig':
        """Create configuration from environment variables"""
        config = cls()
        
        # Override with environment variables
        env_mappings = {
            "MONITORING_ENABLED": "enabled",
            "MONITORING_DEBUG": "debug_mode",
            "MONITORING_ENVIRONMENT": "environment",
            "MONITORING_SERVICE_NAME": "service_name",
            "MONITORING_VERSION": "version"
        }
        
        for env_var, attr in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                if attr == "enabled":
                    setattr(config, attr, value.lower() in ("true", "1", "yes"))
                elif attr == "debug_mode":
                    setattr(config, attr, value.lower() in ("true", "1", "yes"))
                else:
                    setattr(config, attr, value)
        
        return config
