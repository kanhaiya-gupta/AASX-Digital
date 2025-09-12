"""
Validation Engine Service

Core validation infrastructure for data validation and schema enforcement.
Provides comprehensive validation capabilities across all system components.

Features:
- Schema validation
- Business rule validation
- Data type validation
- Custom validation rules
- Validation result reporting
- Performance optimization
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
import re

from ...monitoring.monitoring_config import MonitoringConfig


class ValidationSeverity(Enum):
    """Validation severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationResult:
    """Validation result container"""
    
    def __init__(self):
        self.is_valid: bool = True
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.info: List[Dict[str, Any]] = []
        self.sanitized_data: Optional[Dict[str, Any]] = None
        self.validation_time: float = 0.0
        self.rule_count: int = 0
        self.passed_rules: int = 0
        self.failed_rules: int = 0
    
    def add_error(self, field: str, message: str, rule: str, severity: ValidationSeverity = ValidationSeverity.ERROR):
        """Add a validation error"""
        self.errors.append({
            'field': field,
            'message': message,
            'rule': rule,
            'severity': severity.value,
            'timestamp': datetime.now().isoformat()
        })
        self.is_valid = False
        self.failed_rules += 1
    
    def add_warning(self, field: str, message: str, rule: str):
        """Add a validation warning"""
        self.warnings.append({
            'field': field,
            'message': message,
            'rule': rule,
            'timestamp': datetime.now().isoformat()
        })
    
    def add_info(self, field: str, message: str, rule: str):
        """Add validation information"""
        self.info.append({
            'field': field,
            'message': message,
            'rule': rule,
            'timestamp': datetime.now().isoformat()
        })
    
    def set_sanitized_data(self, data: Dict[str, Any]):
        """Set sanitized data after validation"""
        self.sanitized_data = data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert validation result to dictionary"""
        return {
            'is_valid': self.is_valid,
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info,
            'sanitized_data': self.sanitized_data,
            'validation_time': self.validation_time,
            'rule_count': self.rule_count,
            'passed_rules': self.passed_rules,
            'failed_rules': self.failed_rules
        }


class ValidationEngine:
    """
    Core validation engine for comprehensive data validation and schema enforcement.
    
    Provides:
    - Schema validation
    - Business rule validation
    - Data type validation
    - Custom validation rules
    - Validation result reporting
    """
    
    def __init__(self, config: MonitoringConfig):
        """
        Initialize the validation engine.
        
        Args:
            config: Monitoring configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.validation_rules: Dict[str, Dict[str, Any]] = {}
        self.custom_validators: Dict[str, callable] = {}
        
        # Initialize built-in validators
        self._initialize_builtin_validators()
        
        self.logger.info("ValidationEngine initialized with enterprise-grade validation capabilities")
    
    def _initialize_builtin_validators(self):
        """Initialize built-in validation functions"""
        self.custom_validators.update({
            'email': self._validate_email,
            'phone': self._validate_phone,
            'url': self._validate_url,
            'uuid': self._validate_uuid,
            'json': self._validate_json,
            'date_iso': self._validate_date_iso,
            'positive_number': self._validate_positive_number,
            'string_length': self._validate_string_length,
            'enum_values': self._validate_enum_values
        })
    
    async def validate_data(
        self,
        data: Dict[str, Any],
        schema: str = "default",
        rules: str = "standard"
    ) -> ValidationResult:
        """
        Validate data against schema and business rules.
        
        Args:
            data: Data to validate
            schema: Schema name to use
            rules: Rule set to apply
            
        Returns:
            Validation result
        """
        start_time = datetime.now()
        result = ValidationResult()
        
        try:
            # Get validation rules
            validation_rules = self._get_validation_rules(schema, rules)
            result.rule_count = len(validation_rules)
            
            # Validate each field
            for field_name, field_rules in validation_rules.items():
                if field_name in data:
                    field_value = data[field_name]
                    await self._validate_field(field_name, field_value, field_rules, result)
                else:
                    # Check if field is required
                    if field_rules.get('required', False):
                        result.add_error(
                            field_name,
                            f"Required field '{field_name}' is missing",
                            'required_field',
                            ValidationSeverity.ERROR
                        )
            
            # Apply business rules
            await self._apply_business_rules(data, validation_rules, result)
            
            # Sanitize data if validation passed
            if result.is_valid:
                result.sanitized_data = self._sanitize_data(data, validation_rules)
            
            # Calculate passed rules
            result.passed_rules = result.rule_count - result.failed_rules
            
            # Calculate validation time
            end_time = datetime.now()
            result.validation_time = (end_time - start_time).total_seconds()
            
            self.logger.info(f"Validation completed: {result.passed_rules}/{result.rule_count} rules passed")
            
        except Exception as e:
            self.logger.error(f"Error during validation: {e}")
            result.add_error(
                'validation_engine',
                f"Validation engine error: {str(e)}",
                'engine_error',
                ValidationSeverity.CRITICAL
            )
        
        return result
    
    async def _validate_field(
        self,
        field_name: str,
        field_value: Any,
        field_rules: Dict[str, Any],
        result: ValidationResult
    ):
        """Validate a single field against its rules"""
        try:
            # Type validation
            if 'type' in field_rules:
                if not self._validate_type(field_value, field_rules['type']):
                    result.add_error(
                        field_name,
                        f"Field '{field_name}' must be of type {field_rules['type']}",
                        'type_validation',
                        ValidationSeverity.ERROR
                    )
                    return
            
            # Required validation
            if field_rules.get('required', False) and field_value is None:
                result.add_error(
                    field_name,
                    f"Required field '{field_name}' cannot be null",
                    'required_validation',
                    ValidationSeverity.ERROR
                )
                return
            
            # Custom validation
            if 'validator' in field_rules:
                validator_name = field_rules['validator']
                if validator_name in self.custom_validators:
                    if not await self.custom_validators[validator_name](field_value, field_rules):
                        result.add_error(
                            field_name,
                            f"Field '{field_name}' failed custom validation: {field_rules.get('message', '')}",
                            'custom_validation',
                            ValidationSeverity.ERROR
                        )
                        return
            
            # Range validation for numbers
            if isinstance(field_value, (int, float)):
                if 'min' in field_rules and field_value < field_rules['min']:
                    result.add_error(
                        field_name,
                        f"Field '{field_name}' must be >= {field_rules['min']}",
                        'range_validation',
                        ValidationSeverity.ERROR
                    )
                    return
                
                if 'max' in field_rules and field_value > field_rules['max']:
                    result.add_error(
                        field_name,
                        f"Field '{field_name}' must be <= {field_rules['max']}",
                        'range_validation',
                        ValidationSeverity.ERROR
                    )
                    return
            
            # String validation
            if isinstance(field_value, str):
                if 'min_length' in field_rules and len(field_value) < field_rules['min_length']:
                    result.add_error(
                        field_name,
                        f"Field '{field_name}' must be at least {field_rules['min_length']} characters",
                        'length_validation',
                        ValidationSeverity.ERROR
                    )
                    return
                
                if 'max_length' in field_rules and len(field_value) > field_rules['max_length']:
                    result.add_error(
                        field_name,
                        f"Field '{field_name}' must be at most {field_rules['max_length']} characters",
                        'length_validation',
                        ValidationSeverity.ERROR
                    )
                    return
                
                if 'pattern' in field_rules:
                    if not re.match(field_rules['pattern'], field_value):
                        result.add_error(
                            field_name,
                            f"Field '{field_name}' must match pattern: {field_rules['pattern']}",
                            'pattern_validation',
                            ValidationSeverity.ERROR
                        )
                        return
            
            # Enum validation
            if 'enum' in field_rules:
                if field_value not in field_rules['enum']:
                    result.add_error(
                        field_name,
                        f"Field '{field_name}' must be one of: {field_rules['enum']}",
                        'enum_validation',
                        ValidationSeverity.ERROR
                    )
                    return
            
            # Field passed all validations
            result.add_info(
                field_name,
                f"Field '{field_name}' passed validation",
                'field_validation'
            )
            
        except Exception as e:
            result.add_error(
                field_name,
                f"Error validating field '{field_name}': {str(e)}",
                'validation_error',
                ValidationSeverity.ERROR
            )
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate that a value matches the expected type"""
        try:
            if expected_type == 'string':
                return isinstance(value, str)
            elif expected_type == 'integer':
                return isinstance(value, int)
            elif expected_type == 'float':
                return isinstance(value, (int, float))
            elif expected_type == 'boolean':
                return isinstance(value, bool)
            elif expected_type == 'array':
                return isinstance(value, (list, tuple))
            elif expected_type == 'object':
                return isinstance(value, dict)
            elif expected_type == 'null':
                return value is None
            else:
                return True  # Unknown type, assume valid
        except Exception:
            return False
    
    async def _apply_business_rules(
        self,
        data: Dict[str, Any],
        rules: Dict[str, Any],
        result: ValidationResult
    ):
        """Apply business-level validation rules"""
        try:
            # Cross-field validation rules
            business_rules = rules.get('business_rules', [])
            
            for rule in business_rules:
                rule_type = rule.get('type')
                
                if rule_type == 'required_together':
                    # Check if multiple fields are present together
                    fields = rule.get('fields', [])
                    present_fields = [f for f in fields if f in data and data[f] is not None]
                    
                    if len(present_fields) > 0 and len(present_fields) < len(fields):
                        result.add_error(
                            'business_rule',
                            f"Fields {fields} must be present together",
                            'required_together',
                            ValidationSeverity.ERROR
                        )
                
                elif rule_type == 'mutually_exclusive':
                    # Check if only one field from a set is present
                    fields = rule.get('fields', [])
                    present_fields = [f for f in fields if f in data and data[f] is not None]
                    
                    if len(present_fields) > 1:
                        result.add_error(
                            'business_rule',
                            f"Only one of fields {fields} can be present",
                            'mutually_exclusive',
                            ValidationSeverity.ERROR
                        )
                
                elif rule_type == 'conditional':
                    # Check conditional field requirements
                    condition_field = rule.get('condition_field')
                    condition_value = rule.get('condition_value')
                    required_fields = rule.get('required_fields', [])
                    
                    if data.get(condition_field) == condition_value:
                        for field in required_fields:
                            if field not in data or data[field] is None:
                                result.add_error(
                                    'business_rule',
                                    f"Field '{field}' is required when {condition_field} = {condition_value}",
                                    'conditional_required',
                                    ValidationSeverity.ERROR
                                )
            
        except Exception as e:
            self.logger.error(f"Error applying business rules: {e}")
            result.add_error(
                'business_rules',
                f"Error applying business rules: {str(e)}",
                'business_rules_error',
                ValidationSeverity.ERROR
            )
    
    def _sanitize_data(self, data: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize data based on validation rules"""
        sanitized = {}
        
        try:
            for field_name, field_value in data.items():
                if field_name in rules:
                    field_rules = rules[field_name]
                    
                    # Apply sanitization rules
                    if field_value is not None:
                        if 'sanitize' in field_rules:
                            sanitizer = field_rules['sanitize']
                            if sanitizer == 'trim' and isinstance(field_value, str):
                                sanitized[field_name] = field_value.strip()
                            elif sanitizer == 'lowercase' and isinstance(field_value, str):
                                sanitized[field_name] = field_value.lower()
                            elif sanitizer == 'uppercase' and isinstance(field_value, str):
                                sanitized[field_name] = field_value.upper()
                            else:
                                sanitized[field_name] = field_value
                        else:
                            sanitized[field_name] = field_value
                    else:
                        # Handle null values
                        if field_rules.get('default') is not None:
                            sanitized[field_name] = field_rules['default']
                        else:
                            sanitized[field_name] = field_value
                else:
                    # Unknown field, pass through
                    sanitized[field_name] = field_value
            
        except Exception as e:
            self.logger.error(f"Error sanitizing data: {e}")
            return data  # Return original data if sanitization fails
        
        return sanitized
    
    def _get_validation_rules(self, schema: str, rules: str) -> Dict[str, Any]:
        """Get validation rules for the specified schema and rule set"""
        # For now, return default rules
        # In production, this would load from configuration or database
        
        default_rules = {
            'job_id': {
                'type': 'string',
                'required': True,
                'min_length': 1,
                'max_length': 100,
                'pattern': r'^[a-zA-Z0-9_-]+$'
            },
            'file_id': {
                'type': 'string',
                'required': True,
                'min_length': 1,
                'max_length': 100
            },
            'project_id': {
                'type': 'string',
                'required': True,
                'min_length': 1,
                'max_length': 100
            },
            'job_type': {
                'type': 'string',
                'required': True,
                'enum': ['extraction', 'generation', 'validation', 'processing']
            },
            'source_type': {
                'type': 'string',
                'required': True,
                'enum': ['manual_upload', 'api', 'scheduled', 'webhook']
            },
            'processed_by': {
                'type': 'string',
                'required': True,
                'min_length': 1,
                'max_length': 100
            },
            'org_id': {
                'type': 'string',
                'required': True,
                'min_length': 1,
                'max_length': 100
            },
            'dept_id': {
                'type': 'string',
                'required': False,
                'min_length': 1,
                'max_length': 100
            }
        }
        
        return default_rules
    
    # Built-in validation methods
    async def _validate_email(self, value: str, rules: Dict[str, Any]) -> bool:
        """Validate email format"""
        if not isinstance(value, str):
            return False
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, value))
    
    async def _validate_phone(self, value: str, rules: Dict[str, Any]) -> bool:
        """Validate phone number format"""
        if not isinstance(value, str):
            return False
        phone_pattern = r'^\+?1?\d{9,15}$'
        return bool(re.match(phone_pattern, value))
    
    async def _validate_url(self, value: str, rules: Dict[str, Any]) -> bool:
        """Validate URL format"""
        if not isinstance(value, str):
            return False
        url_pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
        return bool(re.match(url_pattern, value))
    
    async def _validate_uuid(self, value: str, rules: Dict[str, Any]) -> bool:
        """Validate UUID format"""
        if not isinstance(value, str):
            return False
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, value.lower()))
    
    async def _validate_json(self, value: str, rules: Dict[str, Any]) -> bool:
        """Validate JSON format"""
        if not isinstance(value, str):
            return False
        try:
            import json
            json.loads(value)
            return True
        except (json.JSONDecodeError, TypeError):
            return False
    
    async def _validate_date_iso(self, value: str, rules: Dict[str, Any]) -> bool:
        """Validate ISO date format"""
        if not isinstance(value, str):
            return False
        try:
            datetime.fromisoformat(value.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False
    
    async def _validate_positive_number(self, value: Any, rules: Dict[str, Any]) -> bool:
        """Validate positive number"""
        if not isinstance(value, (int, float)):
            return False
        return value > 0
    
    async def _validate_string_length(self, value: str, rules: Dict[str, Any]) -> bool:
        """Validate string length"""
        if not isinstance(value, str):
            return False
        min_length = rules.get('min_length', 0)
        max_length = rules.get('max_length', float('inf'))
        return min_length <= len(value) <= max_length
    
    async def _validate_enum_values(self, value: Any, rules: Dict[str, Any]) -> bool:
        """Validate enum values"""
        enum_values = rules.get('enum', [])
        return value in enum_values
    
    def add_custom_validator(self, name: str, validator_func: callable):
        """Add a custom validation function"""
        self.custom_validators[name] = validator_func
        self.logger.info(f"Added custom validator: {name}")
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation engine statistics"""
        return {
            'total_validators': len(self.custom_validators),
            'builtin_validators': len([v for v in self.custom_validators.keys() if not v.startswith('custom_')]),
            'custom_validators': len([v for v in self.custom_validators.keys() if v.startswith('custom_')]),
            'validation_rules': len(self.validation_rules)
        }
