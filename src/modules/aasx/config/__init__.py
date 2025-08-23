"""
AASX Configuration Package

This package contains configuration management for AASX processing operations.
"""

from .settings import (
    AASXConfig,
    DatabaseConfig,
    ProcessingConfig,
    SecurityConfig,
    IntegrationConfig,
    MonitoringConfig,
    StorageConfig,
    ValidationConfig,
    get_config,
    load_config_from_file,
    get_environment_config,
    default_config
)

from .validation_rules import (
    ValidationRulesConfig,
    ValidationRule,
    ValidationSeverity,
    FileValidationRules,
    ContentValidationRules,
    ProcessingValidationRules,
    SecurityValidationRules,
    get_default_validation_rules,
    get_validation_rules_for_environment
)

__version__ = "1.0.0"
__author__ = "AAS Data Modeling Team"

__all__ = [
    # Main configuration
    'AASXConfig',
    'default_config',
    'get_config',
    'load_config_from_file',
    'get_environment_config',
    
    # Configuration components
    'DatabaseConfig',
    'ProcessingConfig',
    'SecurityConfig',
    'IntegrationConfig',
    'MonitoringConfig',
    'StorageConfig',
    'ValidationConfig',
    
    # Validation rules
    'ValidationRulesConfig',
    'ValidationRule',
    'ValidationSeverity',
    'FileValidationRules',
    'ContentValidationRules',
    'ProcessingValidationRules',
    'SecurityValidationRules',
    'get_default_validation_rules',
    'get_validation_rules_for_environment'
]
