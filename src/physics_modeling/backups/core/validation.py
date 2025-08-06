"""
Validation Engine

This module provides comprehensive validation capabilities for physics models,
parameters, configurations, and data integrity across the framework.
"""

from typing import Dict, List, Optional, Any, Union, Callable
import re
import json
import logging
from datetime import datetime
from dataclasses import dataclass

from .dynamic_types import DynamicPhysicsType, PhysicsParameter


@dataclass
class ValidationRule:
    """Represents a validation rule."""
    
    name: str
    description: str
    validator: Callable[[Any], bool]
    error_message: str
    severity: str = "error"  # 'error', 'warning', 'info'


@dataclass
class ValidationResult:
    """Represents a validation result."""
    
    is_valid: bool
    errors: List[str] = None
    warnings: List[str] = None
    info: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.info is None:
            self.info = []
        if self.metadata is None:
            self.metadata = {}


class ValidationEngine:
    """
    Comprehensive validation engine for physics modeling framework.
    
    This class provides validation capabilities for physics types, parameters,
    models, and configurations with extensible rule system.
    """
    
    def __init__(self):
        """Initialize the validation engine."""
        self.validation_rules: Dict[str, ValidationRule] = {}
        self.custom_validators: Dict[str, Callable] = {}
        self.logger = logging.getLogger(__name__)
        
        # Register built-in validation rules
        self._register_builtin_rules()
    
    def _register_builtin_rules(self) -> None:
        """Register built-in validation rules."""
        
        # Numeric validation rules
        self.register_rule(
            "positive_number",
            "Value must be a positive number",
            lambda x: isinstance(x, (int, float)) and x > 0,
            "Value must be a positive number"
        )
        
        self.register_rule(
            "non_negative_number",
            "Value must be a non-negative number",
            lambda x: isinstance(x, (int, float)) and x >= 0,
            "Value must be a non-negative number"
        )
        
        self.register_rule(
            "finite_number",
            "Value must be a finite number",
            lambda x: isinstance(x, (int, float)) and not (x == float('inf') or x == float('-inf')),
            "Value must be a finite number"
        )
        
        # String validation rules
        self.register_rule(
            "non_empty_string",
            "String must not be empty",
            lambda x: isinstance(x, str) and len(x.strip()) > 0,
            "String must not be empty"
        )
        
        self.register_rule(
            "valid_email",
            "Value must be a valid email address",
            lambda x: isinstance(x, str) and re.match(r"[^@]+@[^@]+\.[^@]+", x) is not None,
            "Value must be a valid email address"
        )
        
        # Array validation rules
        self.register_rule(
            "non_empty_array",
            "Array must not be empty",
            lambda x: isinstance(x, (list, tuple)) and len(x) > 0,
            "Array must not be empty"
        )
        
        # Object validation rules
        self.register_rule(
            "non_empty_dict",
            "Dictionary must not be empty",
            lambda x: isinstance(x, dict) and len(x) > 0,
            "Dictionary must not be empty"
        )
    
    def register_rule(self, name: str, description: str, validator: Callable[[Any], bool], 
                     error_message: str, severity: str = "error") -> None:
        """
        Register a custom validation rule.
        
        Args:
            name: Rule name
            description: Rule description
            validator: Validation function
            error_message: Error message for failed validation
            severity: Validation severity level
        """
        rule = ValidationRule(name, description, validator, error_message, severity)
        self.validation_rules[name] = rule
        self.logger.info(f"Registered validation rule: {name}")
    
    def register_custom_validator(self, name: str, validator: Callable[[Any, Dict[str, Any]], ValidationResult]) -> None:
        """
        Register a custom validator function.
        
        Args:
            name: Validator name
            validator: Validator function
        """
        self.custom_validators[name] = validator
        self.logger.info(f"Registered custom validator: {name}")
    
    def validate_physics_type(self, physics_type: DynamicPhysicsType) -> ValidationResult:
        """
        Validate a physics type definition.
        
        Args:
            physics_type: Physics type to validate
            
        Returns:
            Validation result
        """
        result = ValidationResult(is_valid=True)
        
        # Validate basic properties
        if not physics_type.type_id or not physics_type.type_id.strip():
            result.errors.append("Physics type ID is required")
            result.is_valid = False
        
        if not physics_type.name or not physics_type.name.strip():
            result.errors.append("Physics type name is required")
            result.is_valid = False
        
        if not physics_type.category or not physics_type.category.strip():
            result.errors.append("Physics type category is required")
            result.is_valid = False
        
        # Validate type ID format (should be alphanumeric with underscores)
        if physics_type.type_id and not re.match(r"^[a-zA-Z0-9_]+$", physics_type.type_id):
            result.errors.append("Physics type ID must contain only alphanumeric characters and underscores")
            result.is_valid = False
        
        # Validate parameters
        for param in physics_type.parameters:
            param_result = self.validate_parameter(param)
            if not param_result.is_valid:
                result.errors.extend(param_result.errors)
                result.is_valid = False
            result.warnings.extend(param_result.warnings)
            result.info.extend(param_result.info)
        
        # Validate equations
        for equation in physics_type.equations:
            equation_result = self.validate_equation(equation)
            if not equation_result.is_valid:
                result.errors.extend(equation_result.errors)
                result.is_valid = False
            result.warnings.extend(equation_result.warnings)
            result.info.extend(equation_result.info)
        
        return result
    
    def validate_parameter(self, parameter: PhysicsParameter) -> ValidationResult:
        """
        Validate a physics parameter.
        
        Args:
            parameter: Parameter to validate
            
        Returns:
            Validation result
        """
        result = ValidationResult(is_valid=True)
        
        # Validate basic properties
        if not parameter.name or not parameter.name.strip():
            result.errors.append("Parameter name is required")
            result.is_valid = False
        
        if not parameter.type or parameter.type not in ['float', 'int', 'string', 'boolean', 'array', 'object']:
            result.errors.append("Parameter type must be one of: float, int, string, boolean, array, object")
            result.is_valid = False
        
        if not parameter.description or not parameter.description.strip():
            result.warnings.append(f"Parameter '{parameter.name}' should have a description")
        
        # Validate range constraints
        if parameter.min_value is not None and parameter.max_value is not None:
            if parameter.min_value > parameter.max_value:
                result.errors.append(f"Parameter '{parameter.name}' min_value cannot be greater than max_value")
                result.is_valid = False
        
        # Validate default value type
        if parameter.default_value is not None:
            default_type_ok = False
            if parameter.type == 'float' and isinstance(parameter.default_value, (int, float)):
                default_type_ok = True
            elif parameter.type == 'int' and isinstance(parameter.default_value, int):
                default_type_ok = True
            elif parameter.type == 'string' and isinstance(parameter.default_value, str):
                default_type_ok = True
            elif parameter.type == 'boolean' and isinstance(parameter.default_value, bool):
                default_type_ok = True
            elif parameter.type == 'array' and isinstance(parameter.default_value, (list, tuple)):
                default_type_ok = True
            elif parameter.type == 'object' and isinstance(parameter.default_value, dict):
                default_type_ok = True
            
            if not default_type_ok:
                result.errors.append(f"Parameter '{parameter.name}' default value type does not match parameter type")
                result.is_valid = False
        
        return result
    
    def validate_equation(self, equation) -> ValidationResult:
        """
        Validate a physics equation.
        
        Args:
            equation: Equation to validate
            
        Returns:
            Validation result
        """
        result = ValidationResult(is_valid=True)
        
        # Validate basic properties
        if not equation.name or not equation.name.strip():
            result.errors.append("Equation name is required")
            result.is_valid = False
        
        if not equation.equation or not equation.equation.strip():
            result.errors.append("Equation expression is required")
            result.is_valid = False
        
        if not equation.description or not equation.description.strip():
            result.warnings.append(f"Equation '{equation.name}' should have a description")
        
        # Basic LaTeX validation (very basic)
        if equation.equation:
            # Check for basic LaTeX syntax
            if '\\' in equation.equation and not re.search(r'\\[a-zA-Z]+', equation.equation):
                result.warnings.append(f"Equation '{equation.name}' may have invalid LaTeX syntax")
        
        return result
    
    def validate_parameters(self, parameters: Dict[str, Any], physics_type: DynamicPhysicsType) -> ValidationResult:
        """
        Validate parameters against a physics type definition.
        
        Args:
            parameters: Parameters to validate
            physics_type: Physics type definition
            
        Returns:
            Validation result
        """
        result = ValidationResult(is_valid=True)
        
        # Use physics type's built-in validation
        type_errors = physics_type.validate_parameters(parameters)
        if type_errors:
            result.errors.extend(type_errors.values())
            result.is_valid = False
        
        # Additional validation
        for param_name, param_value in parameters.items():
            param_def = physics_type.get_parameter(param_name)
            if param_def:
                # Apply custom validation rules
                for rule_name in param_def.validation_rules:
                    rule = self.validation_rules.get(rule_name)
                    if rule and not rule.validator(param_value):
                        if rule.severity == "error":
                            result.errors.append(f"Parameter '{param_name}': {rule.error_message}")
                            result.is_valid = False
                        elif rule.severity == "warning":
                            result.warnings.append(f"Parameter '{param_name}': {rule.error_message}")
                        else:
                            result.info.append(f"Parameter '{param_name}': {rule.error_message}")
        
        return result
    
    def validate_model_configuration(self, config: Dict[str, Any]) -> ValidationResult:
        """
        Validate a model configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Validation result
        """
        result = ValidationResult(is_valid=True)
        
        # Validate required fields
        required_fields = ['physics_type_id', 'parameters']
        for field in required_fields:
            if field not in config:
                result.errors.append(f"Required field '{field}' is missing")
                result.is_valid = False
        
        # Validate physics_type_id
        if 'physics_type_id' in config:
            if not isinstance(config['physics_type_id'], str) or not config['physics_type_id'].strip():
                result.errors.append("physics_type_id must be a non-empty string")
                result.is_valid = False
        
        # Validate parameters
        if 'parameters' in config:
            if not isinstance(config['parameters'], dict):
                result.errors.append("parameters must be a dictionary")
                result.is_valid = False
        
        # Validate optional fields
        if 'metadata' in config and not isinstance(config['metadata'], dict):
            result.errors.append("metadata must be a dictionary")
            result.is_valid = False
        
        if 'validation_rules' in config:
            if not isinstance(config['validation_rules'], list):
                result.errors.append("validation_rules must be a list")
                result.is_valid = False
            else:
                for rule in config['validation_rules']:
                    if not isinstance(rule, str) or rule not in self.validation_rules:
                        result.warnings.append(f"Unknown validation rule: {rule}")
        
        return result
    
    def validate_json_schema(self, data: Any, schema: Dict[str, Any]) -> ValidationResult:
        """
        Validate data against a JSON schema.
        
        Args:
            data: Data to validate
            schema: JSON schema
            
        Returns:
            Validation result
        """
        result = ValidationResult(is_valid=True)
        
        try:
            # This is a simplified JSON schema validation
            # In a production environment, you might want to use a proper JSON schema library
            if not self._validate_json_schema_recursive(data, schema):
                result.errors.append("Data does not conform to JSON schema")
                result.is_valid = False
        except Exception as e:
            result.errors.append(f"JSON schema validation error: {str(e)}")
            result.is_valid = False
        
        return result
    
    def _validate_json_schema_recursive(self, data: Any, schema: Dict[str, Any]) -> bool:
        """
        Recursively validate data against JSON schema.
        
        Args:
            data: Data to validate
            schema: JSON schema
            
        Returns:
            True if valid, False otherwise
        """
        schema_type = schema.get('type')
        
        if schema_type == 'object':
            if not isinstance(data, dict):
                return False
            
            required_properties = schema.get('required', [])
            for prop in required_properties:
                if prop not in data:
                    return False
            
            properties = schema.get('properties', {})
            for prop_name, prop_value in data.items():
                if prop_name in properties:
                    if not self._validate_json_schema_recursive(prop_value, properties[prop_name]):
                        return False
        
        elif schema_type == 'array':
            if not isinstance(data, (list, tuple)):
                return False
            
            items_schema = schema.get('items')
            if items_schema:
                for item in data:
                    if not self._validate_json_schema_recursive(item, items_schema):
                        return False
        
        elif schema_type == 'string':
            if not isinstance(data, str):
                return False
            
            min_length = schema.get('minLength')
            if min_length is not None and len(data) < min_length:
                return False
            
            max_length = schema.get('maxLength')
            if max_length is not None and len(data) > max_length:
                return False
        
        elif schema_type == 'number':
            if not isinstance(data, (int, float)):
                return False
            
            minimum = schema.get('minimum')
            if minimum is not None and data < minimum:
                return False
            
            maximum = schema.get('maximum')
            if maximum is not None and data > maximum:
                return False
        
        elif schema_type == 'integer':
            if not isinstance(data, int):
                return False
        
        elif schema_type == 'boolean':
            if not isinstance(data, bool):
                return False
        
        return True
    
    def get_validation_summary(self, result: ValidationResult) -> Dict[str, Any]:
        """
        Get a summary of validation results.
        
        Args:
            result: Validation result
            
        Returns:
            Validation summary
        """
        return {
            'is_valid': result.is_valid,
            'error_count': len(result.errors),
            'warning_count': len(result.warnings),
            'info_count': len(result.info),
            'errors': result.errors,
            'warnings': result.warnings,
            'info': result.info,
            'metadata': result.metadata
        } 