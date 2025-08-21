"""
Configuration Validator

Validates configuration values and ensures they meet requirements
for the AAS Data Modeling Engine.
"""

import re
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

from .engine_config import EngineConfig
from .environment_config import EnvironmentConfig


class ValidationLevel(str, Enum):
    """Validation level types."""
    STRICT = "strict"
    NORMAL = "normal"
    LENIENT = "lenient"


class ValidationSeverity(str, Enum):
    """Validation severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Configuration validation issue."""
    path: str
    message: str
    severity: ValidationSeverity
    current_value: Any
    expected_value: Optional[Any] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Configuration validation result."""
    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    warnings: List[ValidationIssue] = field(default_factory=list)
    errors: List[ValidationIssue] = field(default_factory=list)
    
    def add_issue(self, issue: ValidationIssue) -> None:
        """Add a validation issue."""
        self.issues.append(issue)
        
        if issue.severity == ValidationSeverity.ERROR:
            self.errors.append(issue)
            self.is_valid = False
        elif issue.severity == ValidationSeverity.WARNING:
            self.warnings.append(issue)
        else:
            # INFO level doesn't affect validity
            pass
    
    def has_errors(self) -> bool:
        """Check if there are validation errors."""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are validation warnings."""
        return len(self.warnings) > 0
    
    def get_issues_by_severity(self, severity: ValidationSeverity) -> List[ValidationIssue]:
        """Get issues by severity level."""
        return [issue for issue in self.issues if issue.severity == severity]
    
    def get_issues_by_path(self, path: str) -> List[ValidationIssue]:
        """Get issues by configuration path."""
        return [issue for issue in self.issues if issue.path == path]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert validation result to dictionary."""
        return {
            "is_valid": self.is_valid,
            "total_issues": len(self.issues),
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "issues": [
                {
                    "path": issue.path,
                    "message": issue.message,
                    "severity": issue.severity.value,
                    "current_value": issue.current_value,
                    "expected_value": issue.expected_value,
                    "suggestion": issue.suggestion
                }
                for issue in self.issues
            ]
        }


class ConfigValidator:
    """Configuration validator for engine configurations."""
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.NORMAL):
        """Initialize configuration validator."""
        self.validation_level = validation_level
        self.custom_validators: Dict[str, callable] = {}
    
    def validate_config(self, config: EngineConfig) -> ValidationResult:
        """Validate complete engine configuration."""
        result = ValidationResult(is_valid=True)
        
        # Validate environment configuration
        self._validate_environment(config.environment, result, "environment")
        
        # Validate component configurations
        self._validate_database_config(config.database, result, "database")
        self._validate_messaging_config(config.messaging, result, "messaging")
        self._validate_caching_config(config.caching, result, "caching")
        self._validate_security_config(config.security, result, "security")
        self._validate_monitoring_config(config.monitoring, result, "monitoring")
        self._validate_utils_config(config.utils, result, "utils")
        self._validate_logging_config(config.logging, result, "logging")
        self._validate_performance_config(config.performance, result, "performance")
        
        # Validate custom settings
        self._validate_custom_settings(config.custom_settings, result, "custom_settings")
        
        # Run custom validators
        self._run_custom_validators(config, result)
        
        return result
    
    def add_custom_validator(self, name: str, validator: callable) -> None:
        """Add a custom validation function."""
        self.custom_validators[name] = validator
    
    def _validate_environment(self, env: EnvironmentConfig, result: ValidationResult, path: str) -> None:
        """Validate environment configuration."""
        # Validate paths
        for path_name, path_value in [
            ("base_path", env.base_path),
            ("config_path", env.config_path),
            ("data_path", env.data_path),
            ("log_path", env.log_path),
            ("temp_path", env.temp_path),
            ("cache_path", env.cache_path)
        ]:
            if not isinstance(path_value, Path):
                result.add_issue(ValidationIssue(
                    path=f"{path}.{path_name}",
                    message=f"Path must be a Path object, got {type(path_value)}",
                    severity=ValidationSeverity.ERROR,
                    current_value=path_value,
                    expected_value="Path object"
                ))
        
        # Validate feature flags
        for feature, enabled in env.features.items():
            if not isinstance(enabled, bool):
                result.add_issue(ValidationIssue(
                    path=f"{path}.features.{feature}",
                    message=f"Feature flag must be boolean, got {type(enabled)}",
                    severity=ValidationSeverity.ERROR,
                    current_value=enabled,
                    expected_value="boolean"
                ))
    
    def _validate_database_config(self, db_config: Any, result: ValidationResult, path: str) -> None:
        """Validate database configuration."""
        if not hasattr(db_config, 'enabled'):
            return
        
        if not db_config.enabled:
            return
        
        # Validate database settings
        if hasattr(db_config, 'settings'):
            settings = db_config.settings
            
            # Validate database type
            valid_db_types = ["sqlite", "postgresql", "mysql", "oracle", "sqlserver"]
            if hasattr(settings, 'type') and settings.type not in valid_db_types:
                result.add_issue(ValidationIssue(
                    path=f"{path}.settings.type",
                    message=f"Invalid database type: {settings.type}",
                    severity=ValidationSeverity.ERROR,
                    current_value=settings.type,
                    expected_value=f"one of {valid_db_types}"
                ))
            
            # Validate port numbers
            if hasattr(settings, 'port'):
                if not isinstance(settings.port, int) or settings.port < 1 or settings.port > 65535:
                    result.add_issue(ValidationIssue(
                        path=f"{path}.settings.port",
                        message="Port must be an integer between 1 and 65535",
                        severity=ValidationSeverity.ERROR,
                        current_value=settings.port,
                        expected_value="integer 1-65535"
                    ))
            
            # Validate pool settings
            if hasattr(settings, 'pool_size'):
                if not isinstance(settings.pool_size, int) or settings.pool_size < 1:
                    result.add_issue(ValidationIssue(
                        path=f"{path}.settings.pool_size",
                        message="Pool size must be a positive integer",
                        severity=ValidationSeverity.ERROR,
                        current_value=settings.pool_size,
                        expected_value="positive integer"
                    ))
    
    def _validate_messaging_config(self, msg_config: Any, result: ValidationResult, path: str) -> None:
        """Validate messaging configuration."""
        if not hasattr(msg_config, 'enabled') or not msg_config.enabled:
            return
        
        if hasattr(msg_config, 'settings'):
            settings = msg_config.settings
            
            # Validate messaging type
            valid_msg_types = ["memory", "redis", "rabbitmq", "kafka", "sqs"]
            if hasattr(settings, 'type') and settings.type not in valid_msg_types:
                result.add_issue(ValidationIssue(
                    path=f"{path}.settings.type",
                    message=f"Invalid messaging type: {settings.type}",
                    severity=ValidationSeverity.ERROR,
                    current_value=settings.type,
                    expected_value=f"one of {valid_msg_types}"
                ))
            
            # Validate queue settings
            if hasattr(settings, 'max_queue_size'):
                if not isinstance(settings.max_queue_size, int) or settings.max_queue_size < 1:
                    result.add_issue(ValidationIssue(
                        path=f"{path}.settings.max_queue_size",
                        message="Max queue size must be a positive integer",
                        severity=ValidationSeverity.ERROR,
                        current_value=settings.max_queue_size,
                        expected_value="positive integer"
                    ))
    
    def _validate_caching_config(self, cache_config: Any, result: ValidationResult, path: str) -> None:
        """Validate caching configuration."""
        if not hasattr(cache_config, 'enabled') or not cache_config.enabled:
            return
        
        if hasattr(cache_config, 'settings'):
            settings = cache_config.settings
            
            # Validate cache type
            valid_cache_types = ["memory", "redis", "disk", "memcached"]
            if hasattr(settings, 'type') and settings.type not in valid_cache_types:
                result.add_issue(ValidationIssue(
                    path=f"{path}.settings.type",
                    message=f"Invalid cache type: {settings.type}",
                    severity=ValidationSeverity.ERROR,
                    current_value=settings.type,
                    expected_value=f"one of {valid_cache_types}"
                ))
            
            # Validate TTL
            if hasattr(settings, 'default_ttl'):
                if not isinstance(settings.default_ttl, int) or settings.default_ttl < 0:
                    result.add_issue(ValidationIssue(
                        path=f"{path}.settings.default_ttl",
                        message="Default TTL must be a non-negative integer",
                        severity=ValidationSeverity.ERROR,
                        current_value=settings.default_ttl,
                        expected_value="non-negative integer"
                    ))
    
    def _validate_security_config(self, sec_config: Any, result: ValidationResult, path: str) -> None:
        """Validate security configuration."""
        if not hasattr(sec_config, 'enabled') or not sec_config.enabled:
            return
        
        if hasattr(sec_config, 'settings'):
            settings = sec_config.settings
            
            # Validate JWT secret
            if hasattr(settings, 'jwt_secret'):
                if not settings.jwt_secret or len(settings.jwt_secret) < 32:
                    result.add_issue(ValidationIssue(
                        path=f"{path}.settings.jwt_secret",
                        message="JWT secret must be at least 32 characters long",
                        severity=ValidationSeverity.WARNING,
                        current_value=f"<{len(settings.jwt_secret)} chars>",
                        expected_value="at least 32 characters",
                        suggestion="Use a strong, randomly generated secret key"
                    ))
            
            # Validate password policies
            if hasattr(settings, 'password_min_length'):
                if not isinstance(settings.password_min_length, int) or settings.password_min_length < 8:
                    result.add_issue(ValidationIssue(
                        path=f"{path}.settings.password_min_length",
                        message="Password minimum length should be at least 8",
                        severity=ValidationSeverity.WARNING,
                        current_value=settings.password_min_length,
                        expected_value="at least 8"
                    ))
    
    def _validate_monitoring_config(self, mon_config: Any, result: ValidationResult, path: str) -> None:
        """Validate monitoring configuration."""
        if not hasattr(mon_config, 'enabled') or not mon_config.enabled:
            return
        
        if hasattr(mon_config, 'settings'):
            settings = mon_config.settings
            
            # Validate intervals
            for interval_field in ['metrics_interval', 'health_interval', 'resource_interval']:
                if hasattr(settings, interval_field):
                    value = getattr(settings, interval_field)
                    if not isinstance(value, int) or value < 1:
                        result.add_issue(ValidationIssue(
                            path=f"{path}.settings.{interval_field}",
                            message=f"{interval_field} must be a positive integer",
                            severity=ValidationSeverity.ERROR,
                            current_value=value,
                            expected_value="positive integer"
                        ))
            
            # Validate sampling rate
            if hasattr(settings, 'profiling_sampling_rate'):
                rate = settings.profiling_sampling_rate
                if not isinstance(rate, (int, float)) or rate < 0.0 or rate > 1.0:
                    result.add_issue(ValidationIssue(
                        path=f"{path}.settings.profiling_sampling_rate",
                        message="Profiling sampling rate must be between 0.0 and 1.0",
                        severity=ValidationSeverity.ERROR,
                        current_value=rate,
                        expected_value="float 0.0-1.0"
                    ))
    
    def _validate_utils_config(self, utils_config: Any, result: ValidationResult, path: str) -> None:
        """Validate utilities configuration."""
        if not hasattr(utils_config, 'enabled') or not utils_config.enabled:
            return
        
        if hasattr(utils_config, 'settings'):
            settings = utils_config.settings
            
            # Validate retry settings
            if hasattr(settings, 'retry_max_attempts'):
                attempts = settings.retry_max_attempts
                if not isinstance(attempts, int) or attempts < 1 or attempts > 10:
                    result.add_issue(ValidationIssue(
                        path=f"{path}.settings.retry_max_attempts",
                        message="Retry max attempts must be between 1 and 10",
                        severity=ValidationSeverity.WARNING,
                        current_value=attempts,
                        expected_value="integer 1-10"
                    ))
            
            # Validate file size limits
            if hasattr(settings, 'max_file_size'):
                size = settings.max_file_size
                if not isinstance(size, int) or size < 1024:  # 1KB minimum
                    result.add_issue(ValidationIssue(
                        path=f"{path}.settings.max_file_size",
                        message="Max file size must be at least 1KB",
                        severity=ValidationSeverity.WARNING,
                        current_value=size,
                        expected_value="at least 1024 bytes"
                    ))
    
    def _validate_logging_config(self, log_config: Any, result: ValidationResult, path: str) -> None:
        """Validate logging configuration."""
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if hasattr(log_config, 'level') and log_config.level not in valid_log_levels:
            result.add_issue(ValidationIssue(
                path=f"{path}.level",
                message=f"Invalid log level: {log_config.level}",
                severity=ValidationSeverity.ERROR,
                current_value=log_config.level,
                expected_value=f"one of {valid_log_levels}"
            ))
        
        # Validate log format
        valid_formats = ["json", "csv", "plain", "logstash", "custom"]
        if hasattr(log_config, 'format') and log_config.format not in valid_formats:
            result.add_issue(ValidationIssue(
                path=f"{path}.format",
                message=f"Invalid log format: {log_config.format}",
                severity=ValidationSeverity.ERROR,
                current_value=log_config.format,
                expected_value=f"one of {valid_formats}"
            ))
        
        # Validate file size
        if hasattr(log_config, 'max_file_size'):
            size = log_config.max_file_size
            if not isinstance(size, int) or size < 1024 * 1024:  # 1MB minimum
                result.add_issue(ValidationIssue(
                    path=f"{path}.max_file_size",
                    message="Max file size must be at least 1MB",
                    severity=ValidationSeverity.WARNING,
                    current_value=size,
                    expected_value="at least 1MB"
                ))
    
    def _validate_performance_config(self, perf_config: Any, result: ValidationResult, path: str) -> None:
        """Validate performance configuration."""
        # Validate worker counts
        if hasattr(perf_config, 'max_workers'):
            workers = perf_config.max_workers
            if not isinstance(workers, int) or workers < 1 or workers > 100:
                result.add_issue(ValidationIssue(
                    path=f"{path}.max_workers",
                    message="Max workers must be between 1 and 100",
                    severity=ValidationSeverity.WARNING,
                    current_value=workers,
                    expected_value="integer 1-100"
                ))
        
        # Validate timeouts
        if hasattr(perf_config, 'task_timeout'):
            timeout = perf_config.task_timeout
            if not isinstance(timeout, int) or timeout < 1 or timeout > 3600:
                result.add_issue(ValidationIssue(
                    path=f"{path}.task_timeout",
                    message="Task timeout must be between 1 and 3600 seconds",
                    severity=ValidationSeverity.WARNING,
                    current_value=timeout,
                    expected_value="integer 1-3600"
                ))
    
    def _validate_custom_settings(self, custom_settings: Dict[str, Any], result: ValidationResult, path: str) -> None:
        """Validate custom settings."""
        if not custom_settings:
            return
        
        # Check for potentially dangerous settings
        dangerous_keys = ["eval", "exec", "system", "shell", "command"]
        for key in custom_settings:
            if any(dangerous in key.lower() for dangerous in dangerous_keys):
                result.add_issue(ValidationIssue(
                    path=f"{path}.{key}",
                    message=f"Potentially dangerous custom setting key: {key}",
                    severity=ValidationSeverity.WARNING,
                    current_value=key,
                    suggestion="Avoid using system command related keys"
                ))
    
    def _run_custom_validators(self, config: EngineConfig, result: ValidationResult) -> None:
        """Run custom validation functions."""
        for name, validator in self.custom_validators.items():
            try:
                validator_result = validator(config)
                if validator_result and hasattr(validator_result, 'issues'):
                    # Merge validation results
                    for issue in validator_result.issues:
                        result.add_issue(issue)
            except Exception as e:
                result.add_issue(ValidationIssue(
                    path=f"custom_validator.{name}",
                    message=f"Custom validator '{name}' failed: {e}",
                    severity=ValidationSeverity.ERROR,
                    current_value="validator execution failed"
                ))
    
    def validate_value(self, value: Any, expected_type: type, path: str, 
                      min_value: Optional[Union[int, float]] = None,
                      max_value: Optional[Union[int, float]] = None,
                      allowed_values: Optional[List[Any]] = None,
                      pattern: Optional[str] = None) -> ValidationIssue:
        """Validate a single configuration value."""
        # Type validation
        if not isinstance(value, expected_type):
            return ValidationIssue(
                path=path,
                message=f"Expected {expected_type.__name__}, got {type(value).__name__}",
                severity=ValidationSeverity.ERROR,
                current_value=value,
                expected_value=expected_type.__name__
            )
        
        # Range validation for numbers
        if isinstance(value, (int, float)) and (min_value is not None or max_value is not None):
            if min_value is not None and value < min_value:
                return ValidationIssue(
                    path=path,
                    message=f"Value must be at least {min_value}",
                    severity=ValidationSeverity.ERROR,
                    current_value=value,
                    expected_value=f"at least {min_value}"
                )
            if max_value is not None and value > max_value:
                return ValidationIssue(
                    path=path,
                    message=f"Value must be at most {max_value}",
                    severity=ValidationSeverity.ERROR,
                    current_value=value,
                    expected_value=f"at most {max_value}"
                )
        
        # Allowed values validation
        if allowed_values is not None and value not in allowed_values:
            return ValidationIssue(
                path=path,
                message=f"Value must be one of {allowed_values}",
                severity=ValidationSeverity.ERROR,
                current_value=value,
                expected_value=f"one of {allowed_values}"
            )
        
        # Pattern validation for strings
        if isinstance(value, str) and pattern is not None:
            if not re.match(pattern, value):
                return ValidationIssue(
                    path=path,
                    message=f"Value must match pattern: {pattern}",
                    severity=ValidationSeverity.ERROR,
                    current_value=value,
                    expected_value=f"matches pattern {pattern}"
                )
        
        return None  # No validation issues
