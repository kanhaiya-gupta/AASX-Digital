"""
Validation Rules for Twin Registry Population
Defines validation rules and quality thresholds for data validation
"""

import logging
import re
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Validation severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class FieldType(Enum):
    """Field types for validation"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    JSON = "json"
    ARRAY = "array"
    EMAIL = "email"
    URL = "url"
    UUID = "uuid"


@dataclass
class ValidationRule:
    """Individual validation rule"""
    field_name: str
    rule_type: str
    rule_value: Any
    severity: ValidationSeverity = ValidationSeverity.ERROR
    message: Optional[str] = None
    custom_validator: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.message is None:
            self.message = f"Validation failed for {self.field_name}: {self.rule_type}"


@dataclass
class FieldValidation:
    """Field validation configuration"""
    field_name: str
    field_type: FieldType
    required: bool = True
    nullable: bool = False
    default_value: Optional[Any] = None
    validation_rules: List[ValidationRule] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    transform_rules: List[str] = field(default_factory=list)


@dataclass
class QualityThreshold:
    """Quality threshold configuration"""
    metric_name: str
    threshold_value: float
    operator: str = ">="  # >=, <=, ==, !=, >, <
    weight: float = 1.0
    description: Optional[str] = None


class ValidationRules:
    """Validation rules manager for twin registry population"""
    
    def __init__(self):
        self.field_validations: Dict[str, FieldValidation] = {}
        self.quality_thresholds: Dict[str, QualityThreshold] = {}
        self.custom_validators: Dict[str, Callable] = {}
        
        # Initialize default validation rules
        self._init_default_rules()
    
    def _init_default_rules(self) -> None:
        """Initialize default validation rules"""
        # Twin Registry core fields
        self._add_field_validation(
            FieldValidation(
                field_name="twin_name",
                field_type=FieldType.STRING,
                required=True,
                nullable=False,
                validation_rules=[
                    ValidationRule("twin_name", "min_length", 3, ValidationSeverity.ERROR),
                    ValidationRule("twin_name", "max_length", 100, ValidationSeverity.ERROR),
                    ValidationRule("twin_name", "pattern", r"^[a-zA-Z0-9_\-\s]+$", ValidationSeverity.WARNING)
                ]
            )
        )
        
        self._add_field_validation(
            FieldValidation(
                field_name="registry_type",
                field_type=FieldType.STRING,
                required=True,
                nullable=False,
                validation_rules=[
                    ValidationRule("registry_type", "enum", ["extraction", "generation", "hybrid"], ValidationSeverity.ERROR)
                ]
            )
        )
        
        self._add_field_validation(
            FieldValidation(
                field_name="workflow_source",
                field_type=FieldType.STRING,
                required=True,
                nullable=False,
                validation_rules=[
                    ValidationRule("workflow_source", "enum", ["aasx_file", "structured_data", "api", "manual"], ValidationSeverity.ERROR)
                ]
            )
        )
        
        self._add_field_validation(
            FieldValidation(
                field_name="user_id",
                field_type=FieldType.UUID,
                required=True,
                nullable=False,
                validation_rules=[
                    ValidationRule("user_id", "uuid_format", True, ValidationSeverity.ERROR)
                ]
            )
        )
        
        self._add_field_validation(
            FieldValidation(
                field_name="org_id",
                field_type=FieldType.UUID,
                required=True,
                nullable=False,
                validation_rules=[
                    ValidationRule("org_id", "uuid_format", True, ValidationSeverity.ERROR)
                ]
            )
        )
        
        # Optional fields with validation
        self._add_field_validation(
            FieldValidation(
                field_name="description",
                field_type=FieldType.STRING,
                required=False,
                nullable=True,
                validation_rules=[
                    ValidationRule("description", "max_length", 500, ValidationSeverity.WARNING)
                ]
            )
        )
        
        self._add_field_validation(
            FieldValidation(
                field_name="tags",
                field_type=FieldType.ARRAY,
                required=False,
                nullable=True,
                validation_rules=[
                    ValidationRule("tags", "max_count", 10, ValidationSeverity.WARNING),
                    ValidationRule("tags", "max_length", 50, ValidationSeverity.WARNING)
                ]
            )
        )
        
        self._add_field_validation(
            FieldValidation(
                field_name="metadata",
                field_type=FieldType.JSON,
                required=False,
                nullable=True,
                validation_rules=[
                    ValidationRule("metadata", "max_size", 10000, ValidationSeverity.WARNING)  # 10KB
                ]
            )
        )
        
        # Quality thresholds
        self._add_quality_threshold(
            QualityThreshold(
                metric_name="completeness",
                threshold_value=0.8,
                operator=">=",
                weight=0.3,
                description="Minimum data completeness score"
            )
        )
        
        self._add_quality_threshold(
            QualityThreshold(
                metric_name="accuracy",
                threshold_value=0.9,
                operator=">=",
                weight=0.3,
                description="Minimum data accuracy score"
            )
        )
        
        self._add_quality_threshold(
            QualityThreshold(
                metric_name="consistency",
                threshold_value=0.85,
                operator=">=",
                weight=0.2,
                description="Minimum data consistency score"
            )
        )
        
        self._add_quality_threshold(
            QualityThreshold(
                metric_name="timeliness",
                threshold_value=0.95,
                operator=">=",
                weight=0.2,
                description="Minimum data timeliness score"
            )
        )
        
        # Register custom validators
        self._register_custom_validators()
    
    def _add_field_validation(self, field_validation: FieldValidation) -> None:
        """Add field validation configuration"""
        self.field_validations[field_validation.field_name] = field_validation
    
    def _add_quality_threshold(self, threshold: QualityThreshold) -> None:
        """Add quality threshold configuration"""
        self.quality_thresholds[threshold.metric_name] = threshold
    
    def _register_custom_validators(self) -> None:
        """Register custom validation functions"""
        self.custom_validators["uuid_format"] = self._validate_uuid_format
        self.custom_validators["pattern"] = self._validate_pattern
        self.custom_validators["enum"] = self._validate_enum
        self.custom_validators["min_length"] = self._validate_min_length
        self.custom_validators["max_length"] = self._validate_max_length
        self.custom_validators["max_count"] = self._validate_max_count
        self.custom_validators["max_size"] = self._validate_max_size
        self.custom_validators["dependency"] = self._validate_dependency
    
    def validate_field(
        self,
        field_name: str,
        value: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate a single field"""
        validation_result = {
            "field_name": field_name,
            "valid": True,
            "errors": [],
            "warnings": [],
            "info": [],
            "score": 1.0
        }
        
        try:
            if field_name not in self.field_validations:
                validation_result["warnings"].append(f"No validation rules defined for field: {field_name}")
                return validation_result
            
            field_validation = self.field_validations[field_name]
            
            # Check if field is required
            if field_validation.required and value is None:
                validation_result["valid"] = False
                validation_result["errors"].append(f"Field {field_name} is required but value is None")
                validation_result["score"] = 0.0
                return validation_result
            
            # Check if field can be null
            if value is None:
                if not field_validation.nullable:
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"Field {field_name} cannot be null")
                    validation_result["score"] = 0.0
                    return validation_result
                else:
                    return validation_result  # Null value is acceptable
            
            # Validate field type
            type_validation = self._validate_field_type(field_name, value, field_validation.field_type)
            if not type_validation["valid"]:
                validation_result["valid"] = False
                validation_result["errors"].extend(type_validation["errors"])
                validation_result["score"] *= 0.5
            
            # Apply validation rules
            for rule in field_validation.validation_rules:
                rule_result = self._apply_validation_rule(rule, value, context)
                
                if rule_result["valid"]:
                    if rule_result["severity"] == ValidationSeverity.INFO:
                        validation_result["info"].append(rule_result["message"])
                    elif rule_result["severity"] == ValidationSeverity.WARNING:
                        validation_result["warnings"].append(rule_result["message"])
                else:
                    if rule_result["severity"] == ValidationSeverity.ERROR:
                        validation_result["valid"] = False
                        validation_result["errors"].append(rule_result["message"])
                        validation_result["score"] *= 0.7
                    elif rule_result["severity"] == ValidationSeverity.CRITICAL:
                        validation_result["valid"] = False
                        validation_result["errors"].append(rule_result["message"])
                        validation_result["score"] = 0.0
                        break
            
            # Validate dependencies
            if field_validation.dependencies:
                dependency_result = self._validate_dependencies(field_validation.dependencies, context)
                if not dependency_result["valid"]:
                    validation_result["warnings"].extend(dependency_result["warnings"])
                    validation_result["score"] *= 0.9
            
            # Ensure score is between 0 and 1
            validation_result["score"] = max(0.0, min(1.0, validation_result["score"]))
            
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Validation error for {field_name}: {str(e)}")
            validation_result["score"] = 0.0
            logger.error(f"Field validation error for {field_name}: {e}")
        
        return validation_result
    
    def _validate_field_type(
        self,
        field_name: str,
        value: Any,
        expected_type: FieldType
    ) -> Dict[str, Any]:
        """Validate field type"""
        result = {"valid": True, "errors": []}
        
        try:
            if expected_type == FieldType.STRING:
                if not isinstance(value, str):
                    result["valid"] = False
                    result["errors"].append(f"Expected string, got {type(value).__name__}")
            
            elif expected_type == FieldType.INTEGER:
                if not isinstance(value, int):
                    result["valid"] = False
                    result["errors"].append(f"Expected integer, got {type(value).__name__}")
            
            elif expected_type == FieldType.FLOAT:
                if not isinstance(value, (int, float)):
                    result["valid"] = False
                    result["errors"].append(f"Expected number, got {type(value).__name__}")
            
            elif expected_type == FieldType.BOOLEAN:
                if not isinstance(value, bool):
                    result["valid"] = False
                    result["errors"].append(f"Expected boolean, got {type(value).__name__}")
            
            elif expected_type == FieldType.DATETIME:
                if not isinstance(value, (str, datetime)):
                    result["valid"] = False
                    result["errors"].append(f"Expected datetime or string, got {type(value).__name__}")
            
            elif expected_type == FieldType.JSON:
                if not isinstance(value, (dict, list)):
                    result["valid"] = False
                    result["errors"].append(f"Expected JSON object or array, got {type(value).__name__}")
            
            elif expected_type == FieldType.ARRAY:
                if not isinstance(value, (list, tuple)):
                    result["valid"] = False
                    result["errors"].append(f"Expected array, got {type(value).__name__}")
            
            elif expected_type == FieldType.EMAIL:
                if not isinstance(value, str) or not self._is_valid_email(value):
                    result["valid"] = False
                    result["errors"].append(f"Expected valid email address, got {value}")
            
            elif expected_type == FieldType.URL:
                if not isinstance(value, str) or not self._is_valid_url(value):
                    result["valid"] = False
                    result["errors"].append(f"Expected valid URL, got {value}")
            
            elif expected_type == FieldType.UUID:
                if not isinstance(value, str) or not self._is_valid_uuid(value):
                    result["valid"] = False
                    result["errors"].append(f"Expected valid UUID, got {value}")
        
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Type validation error: {str(e)}")
        
        return result
    
    def _apply_validation_rule(
        self,
        rule: ValidationRule,
        value: Any,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Apply a validation rule"""
        result = {
            "valid": True,
            "message": rule.message,
            "severity": rule.severity
        }
        
        try:
            if rule.custom_validator:
                # Use custom validator function
                result["valid"] = rule.custom_validator(value, rule.rule_value, context)
            elif rule.rule_type in self.custom_validators:
                # Use built-in custom validator
                result["valid"] = self.custom_validators[rule.rule_type](value, rule.rule_value, context)
            else:
                # Use default validation logic
                result["valid"] = self._default_validation(rule, value, context)
        
        except Exception as e:
            result["valid"] = False
            result["message"] = f"Validation rule error: {str(e)}"
            logger.error(f"Validation rule error for {rule.field_name}: {e}")
        
        return result
    
    def _default_validation(
        self,
        rule: ValidationRule,
        value: Any,
        context: Optional[Dict[str, Any]]
    ) -> bool:
        """Default validation logic"""
        if rule.rule_type == "min_length":
            return len(str(value)) >= rule.rule_value
        elif rule.rule_type == "max_length":
            return len(str(value)) <= rule.rule_value
        elif rule.rule_type == "min_value":
            return value >= rule.rule_value
        elif rule.rule_type == "max_value":
            return value <= rule.rule_value
        elif rule.rule_type == "pattern":
            return bool(re.match(rule.rule_value, str(value)))
        elif rule.rule_type == "enum":
            return value in rule.rule_value
        else:
            return True
    
    # Custom validator functions
    def _validate_uuid_format(self, value: Any, rule_value: Any, context: Any) -> bool:
        """Validate UUID format"""
        import uuid
        try:
            uuid.UUID(str(value))
            return True
        except ValueError:
            return False
    
    def _validate_pattern(self, value: Any, rule_value: Any, context: Any) -> bool:
        """Validate pattern using regex"""
        return bool(re.match(rule_value, str(value)))
    
    def _validate_enum(self, value: Any, rule_value: Any, context: Any) -> bool:
        """Validate enum value"""
        return value in rule_value
    
    def _validate_min_length(self, value: Any, rule_value: Any, context: Any) -> bool:
        """Validate minimum length"""
        return len(str(value)) >= rule_value
    
    def _validate_max_length(self, value: Any, rule_value: Any, context: Any) -> bool:
        """Validate maximum length"""
        return len(str(value)) <= rule_value
    
    def _validate_max_count(self, value: Any, rule_value: Any, context: Any) -> bool:
        """Validate maximum count for arrays"""
        if isinstance(value, (list, tuple)):
            return len(value) <= rule_value
        return True
    
    def _validate_max_size(self, value: Any, rule_value: Any, context: Any) -> bool:
        """Validate maximum size (for JSON/strings)"""
        if isinstance(value, (dict, list)):
            import json
            size = len(json.dumps(value))
        else:
            size = len(str(value))
        return size <= rule_value
    
    def _validate_dependency(self, value: Any, rule_value: Any, context: Any) -> bool:
        """Validate field dependency"""
        if context and rule_value in context:
            return context[rule_value] is not None
        return True
    
    def _validate_dependencies(
        self,
        dependencies: List[str],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate field dependencies"""
        result = {"valid": True, "warnings": []}
        
        if not context:
            return result
        
        for dependency in dependencies:
            if dependency not in context or context[dependency] is None:
                result["warnings"].append(f"Field depends on {dependency} which is not available")
                result["valid"] = False
        
        return result
    
    def _is_valid_email(self, email: str) -> bool:
        """Check if email is valid"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
        return bool(re.match(pattern, url))
    
    def _is_valid_uuid(self, uuid_str: str) -> bool:
        """Check if UUID is valid"""
        import uuid
        try:
            uuid.UUID(uuid_str)
            return True
        except ValueError:
            return False
    
    def validate_record(
        self,
        record: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate a complete record"""
        validation_result = {
            "valid": True,
            "total_fields": 0,
            "valid_fields": 0,
            "invalid_fields": 0,
            "field_results": {},
            "overall_score": 0.0,
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        try:
            context = context or {}
            context.update(record)  # Add record data to context for dependency validation
            
            total_score = 0.0
            field_count = 0
            
            for field_name, field_validation in self.field_validations.items():
                field_count += 1
                value = record.get(field_name)
                
                field_result = self.validate_field(field_name, value, context)
                validation_result["field_results"][field_name] = field_result
                
                if field_result["valid"]:
                    validation_result["valid_fields"] += 1
                else:
                    validation_result["invalid_fields"] += 1
                    validation_result["errors"].extend(field_result["errors"])
                
                validation_result["warnings"].extend(field_result["warnings"])
                validation_result["info"].extend(field_result["info"])
                
                total_score += field_result["score"]
            
            validation_result["total_fields"] = field_count
            
            if field_count > 0:
                validation_result["overall_score"] = total_score / field_count
            
            # Check if record is overall valid
            validation_result["valid"] = (
                validation_result["invalid_fields"] == 0 and
                validation_result["overall_score"] >= 0.8
            )
            
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Record validation error: {str(e)}")
            logger.error(f"Record validation error: {e}")
        
        return validation_result
    
    def check_quality_thresholds(self, scores: Dict[str, float]) -> Dict[str, Any]:
        """Check if quality scores meet thresholds"""
        threshold_results = {
            "all_passed": True,
            "passed_thresholds": [],
            "failed_thresholds": [],
            "overall_score": 0.0
        }
        
        try:
            total_score = 0.0
            total_weight = 0.0
            
            for metric_name, score in scores.items():
                if metric_name in self.quality_thresholds:
                    threshold = self.quality_thresholds[metric_name]
                    total_weight += threshold.weight
                    
                    # Check if threshold is met
                    threshold_passed = self._evaluate_threshold(score, threshold)
                    
                    if threshold_passed:
                        threshold_results["passed_thresholds"].append(metric_name)
                    else:
                        threshold_results["failed_thresholds"].append(metric_name)
                        threshold_results["all_passed"] = False
                    
                    # Calculate weighted score
                    total_score += score * threshold.weight
            
            if total_weight > 0:
                threshold_results["overall_score"] = total_score / total_weight
            
        except Exception as e:
            threshold_results["all_passed"] = False
            logger.error(f"Quality threshold check error: {e}")
        
        return threshold_results
    
    def _evaluate_threshold(self, score: float, threshold: QualityThreshold) -> bool:
        """Evaluate if a score meets a threshold"""
        if threshold.operator == ">=":
            return score >= threshold.threshold_value
        elif threshold.operator == "<=":
            return score <= threshold.threshold_value
        elif threshold.operator == "==":
            return score == threshold.threshold_value
        elif threshold.operator == "!=":
            return score != threshold.threshold_value
        elif threshold.operator == ">":
            return score > threshold.threshold_value
        elif threshold.operator == "<":
            return score < threshold.threshold_value
        else:
            return False
    
    def add_custom_validator(self, name: str, validator_func: Callable) -> None:
        """Add a custom validation function"""
        self.custom_validators[name] = validator_func
        logger.info(f"Added custom validator: {name}")
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get a summary of validation configuration"""
        return {
            "total_fields": len(self.field_validations),
            "total_thresholds": len(self.quality_thresholds),
            "total_custom_validators": len(self.custom_validators),
            "field_names": list(self.field_validations.keys()),
            "threshold_names": list(self.quality_thresholds.keys()),
            "validator_names": list(self.custom_validators.keys())
        }
