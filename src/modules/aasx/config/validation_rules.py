"""
AASX Validation Rules Configuration

Comprehensive validation rules for AASX processing operations.
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum


class ValidationSeverity(str, Enum):
    """Validation severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationRule(BaseModel):
    """Individual validation rule definition."""
    
    rule_id: str = Field(..., description="Unique rule identifier")
    name: str = Field(..., description="Human-readable rule name")
    description: str = Field(..., description="Rule description")
    severity: ValidationSeverity = Field(default=ValidationSeverity.ERROR, description="Rule severity")
    enabled: bool = Field(default=True, description="Whether the rule is enabled")
    
    # Rule conditions
    condition: str = Field(..., description="Rule condition expression")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Rule parameters")
    
    # Error handling
    error_message: str = Field(..., description="Error message template")
    suggestion: Optional[str] = Field(None, description="Suggestion for fixing the issue")
    
    # Metadata
    category: str = Field(..., description="Rule category")
    tags: List[str] = Field(default_factory=list, description="Rule tags")
    version: str = Field(default="1.0.0", description="Rule version")


class FileValidationRules(BaseModel):
    """File-level validation rules."""
    
    # File format validation
    validate_file_extension: bool = Field(default=True, description="Validate file extension")
    allowed_extensions: List[str] = Field(
        default=[".aasx", ".aas", ".xml"],
        description="Allowed file extensions"
    )
    
    # File size validation
    validate_file_size: bool = Field(default=True, description="Validate file size")
    max_file_size_mb: int = Field(default=100, description="Maximum file size in MB")
    min_file_size_kb: int = Field(default=1, description="Minimum file size in KB")
    
    # File integrity validation
    validate_file_integrity: bool = Field(default=True, description="Validate file integrity")
    validate_checksum: bool = Field(default=True, description="Validate file checksum")
    validate_file_structure: bool = Field(default=True, description="Validate file structure")
    
    # Content validation
    validate_content_type: bool = Field(default=True, description="Validate content type")
    validate_encoding: bool = Field(default=True, description="Validate file encoding")
    allowed_encodings: List[str] = Field(
        default=["utf-8", "ascii"],
        description="Allowed file encodings"
    )


class ContentValidationRules(BaseModel):
    """Content-level validation rules."""
    
    # Schema validation
    validate_schema: bool = Field(default=True, description="Validate against AAS schema")
    schema_version: str = Field(default="3.0", description="AAS schema version")
    strict_schema_validation: bool = Field(default=False, description="Enable strict schema validation")
    
    # Structure validation
    validate_structure: bool = Field(default=True, description="Validate content structure")
    validate_references: bool = Field(default=True, description="Validate internal references")
    validate_relationships: bool = Field(default=True, description="Validate relationships")
    
    # Content quality validation
    validate_content_quality: bool = Field(default=True, description="Validate content quality")
    min_description_length: int = Field(default=10, description="Minimum description length")
    require_identifiers: bool = Field(default=True, description="Require identifiers")
    validate_metadata: bool = Field(default=True, description="Validate metadata")


class ProcessingValidationRules(BaseModel):
    """Processing-level validation rules."""
    
    # Job validation
    validate_job_parameters: bool = Field(default=True, description="Validate job parameters")
    required_job_fields: List[str] = Field(
        default=["file_id", "project_id", "job_type", "processed_by", "org_id"],
        description="Required job fields"
    )
    
    # Processing limits
    validate_processing_limits: bool = Field(default=True, description="Validate processing limits")
    max_processing_time: int = Field(default=3600, description="Maximum processing time in seconds")
    max_memory_usage: int = Field(default=2048, description="Maximum memory usage in MB")
    
    # Quality thresholds
    validate_quality_thresholds: bool = Field(default=True, description="Validate quality thresholds")
    min_quality_score: float = Field(default=0.7, description="Minimum quality score")
    min_accuracy_score: float = Field(default=0.8, description="Minimum accuracy score")


class SecurityValidationRules(BaseModel):
    """Security validation rules."""
    
    # Access control validation
    validate_access_control: bool = Field(default=True, description="Validate access control")
    require_authentication: bool = Field(default=True, description="Require authentication")
    validate_permissions: bool = Field(default=True, description="Validate user permissions")
    
    # Data sensitivity validation
    validate_data_sensitivity: bool = Field(default=True, description="Validate data sensitivity")
    sensitive_data_patterns: List[str] = Field(
        default=["password", "token", "key", "secret"],
        description="Sensitive data patterns"
    )
    
    # Compliance validation
    validate_compliance: bool = Field(default=True, description="Validate compliance requirements")
    compliance_standards: List[str] = Field(
        default=["GDPR", "ISO27001"],
        description="Compliance standards to validate"
    )


class ValidationRulesConfig(BaseModel):
    """Complete validation rules configuration."""
    
    # Configuration metadata
    version: str = Field(default="2.0.0", description="Configuration version")
    description: str = Field(default="AASX validation rules configuration", description="Configuration description")
    
    # Validation rule sets
    file_rules: FileValidationRules = Field(default_factory=FileValidationRules)
    content_rules: ContentValidationRules = Field(default_factory=ContentValidationRules)
    processing_rules: ProcessingValidationRules = Field(default_factory=ProcessingValidationRules)
    security_rules: SecurityValidationRules = Field(default_factory=SecurityValidationRules)
    
    # Custom rules
    custom_rules: List[ValidationRule] = Field(default_factory=list, description="Custom validation rules")
    
    # Global settings
    enable_all_rules: bool = Field(default=True, description="Enable all validation rules")
    fail_fast: bool = Field(default=False, description="Fail validation on first error")
    max_validation_errors: int = Field(default=100, description="Maximum validation errors to collect")
    
    def get_enabled_rules(self) -> List[ValidationRule]:
        """Get all enabled validation rules."""
        if not self.enable_all_rules:
            return []
        
        enabled_rules = []
        
        # Add custom rules
        enabled_rules.extend([rule for rule in self.custom_rules if rule.enabled])
        
        return enabled_rules
    
    def get_rules_by_category(self, category: str) -> List[ValidationRule]:
        """Get validation rules by category."""
        return [rule for rule in self.custom_rules if rule.category == category and rule.enabled]
    
    def get_rules_by_severity(self, severity: ValidationSeverity) -> List[ValidationRule]:
        """Get validation rules by severity level."""
        return [rule for rule in self.custom_rules if rule.severity == severity and rule.enabled]
    
    def add_custom_rule(self, rule: ValidationRule) -> None:
        """Add a custom validation rule."""
        # Check if rule ID already exists
        existing_rule_ids = [r.rule_id for r in self.custom_rules]
        if rule.rule_id in existing_rule_ids:
            raise ValueError(f"Rule with ID '{rule.rule_id}' already exists")
        
        self.custom_rules.append(rule)
    
    def remove_custom_rule(self, rule_id: str) -> bool:
        """Remove a custom validation rule."""
        for i, rule in enumerate(self.custom_rules):
            if rule.rule_id == rule_id:
                del self.custom_rules[i]
                return True
        return False
    
    def enable_rule(self, rule_id: str) -> bool:
        """Enable a validation rule."""
        for rule in self.custom_rules:
            if rule.rule_id == rule_id:
                rule.enabled = True
                return True
        return False
    
    def disable_rule(self, rule_id: str) -> bool:
        """Disable a validation rule."""
        for rule in self.custom_rules:
            if rule.rule_id == rule_id:
                rule.enabled = False
                return True
        return False


# Default validation rules
def get_default_validation_rules() -> ValidationRulesConfig:
    """Get default validation rules configuration."""
    config = ValidationRulesConfig()
    
    # Add default custom rules
    default_rules = [
        ValidationRule(
            rule_id="file_size_limit",
            name="File Size Limit",
            description="Validate that file size is within acceptable limits",
            severity=ValidationSeverity.ERROR,
            condition="file_size <= max_file_size",
            parameters={"max_file_size": 100 * 1024 * 1024},  # 100MB
            error_message="File size {file_size} exceeds maximum allowed size {max_file_size}",
            suggestion="Reduce file size or contact administrator for large file processing",
            category="file_validation",
            tags=["size", "limit", "file"]
        ),
        ValidationRule(
            rule_id="file_extension",
            name="File Extension Validation",
            description="Validate that file has supported extension",
            severity=ValidationSeverity.ERROR,
            condition="file_extension in allowed_extensions",
            parameters={"allowed_extensions": [".aasx", ".aas", ".xml"]},
            error_message="File extension '{file_extension}' is not supported",
            suggestion="Use one of the supported extensions: {allowed_extensions}",
            category="file_validation",
            tags=["extension", "format", "file"]
        ),
        ValidationRule(
            rule_id="required_fields",
            name="Required Fields Validation",
            description="Validate that all required fields are present",
            severity=ValidationSeverity.ERROR,
            condition="all(field in data for field in required_fields)",
            parameters={"required_fields": ["id", "idShort", "modelType"]},
            error_message="Missing required fields: {missing_fields}",
            suggestion="Ensure all required fields are provided",
            category="content_validation",
            tags=["fields", "required", "content"]
        ),
        ValidationRule(
            rule_id="identifier_format",
            name="Identifier Format Validation",
            description="Validate identifier format",
            severity=ValidationSeverity.WARNING,
            condition="is_valid_identifier_format(identifier)",
            parameters={"pattern": r"^[a-zA-Z][a-zA-Z0-9_-]*$"},
            error_message="Identifier '{identifier}' does not follow recommended format",
            suggestion="Use alphanumeric characters, hyphens, and underscores, starting with a letter",
            category="content_validation",
            tags=["identifier", "format", "content"]
        ),
        ValidationRule(
            rule_id="processing_timeout",
            name="Processing Timeout Validation",
            description="Validate that processing time is within limits",
            severity=ValidationSeverity.WARNING,
            condition="processing_time <= max_processing_time",
            parameters={"max_processing_time": 3600},  # 1 hour
            error_message="Processing time {processing_time}s exceeds recommended limit {max_processing_time}s",
            suggestion="Consider optimizing processing or increasing timeout limits",
            category="processing_validation",
            tags=["timeout", "performance", "processing"]
        )
    ]
    
    for rule in default_rules:
        config.add_custom_rule(rule)
    
    return config


# Environment-specific validation rules
def get_validation_rules_for_environment(environment: str) -> ValidationRulesConfig:
    """
    Get validation rules configuration for a specific environment.
    
    Args:
        environment: Environment name (development, staging, production)
        
    Returns:
        ValidationRulesConfig: Environment-specific validation rules
    """
    config = get_default_validation_rules()
    
    if environment == "development":
        # Relaxed rules for development
        config.fail_fast = False
        config.max_validation_errors = 1000
        config.processing_rules.max_processing_time = 7200  # 2 hours
        
    elif environment == "staging":
        # Moderate rules for staging
        config.fail_fast = False
        config.max_validation_errors = 500
        config.processing_rules.max_processing_time = 5400  # 1.5 hours
        
    elif environment == "production":
        # Strict rules for production
        config.fail_fast = True
        config.max_validation_errors = 100
        config.processing_rules.max_processing_time = 3600  # 1 hour
        config.security_rules.require_authentication = True
        config.security_rules.validate_permissions = True
    
    return config
