"""
Business Validator
=================

Validates business rules and constraints for database operations.
Handles domain-specific validation logic for different business modules.
"""

import re
import json
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from decimal import Decimal

from .base_validator import BaseValidator


class BusinessValidator(BaseValidator):
    """Validates business rules and constraints for database operations"""
    
    def __init__(self, name: str = "BusinessValidator"):
        super().__init__(name)
        self._business_rules: Dict[str, Dict[str, Any]] = {}
        self._domain_validators: Dict[str, callable] = {}
        
        # Initialize domain-specific validators
        self._setup_domain_validators()
    
    def _setup_domain_validators(self):
        """Setup domain-specific validation functions"""
        self._domain_validators = {
            'auth': self._validate_auth_domain,
            'business_domain': self._validate_business_domain,
            'certificate_manager': self._validate_certificate_domain,
            'ai_rag': self._validate_ai_rag_domain,
            'twin_registry': self._validate_twin_registry_domain,
            'kg_neo4j': self._validate_kg_neo4j_domain,
            'federated_learning': self._validate_federated_learning_domain,
            'physics_modeling': self._validate_physics_modeling_domain,
            'data_governance': self._validate_data_governance_domain,
            'aasx_etl': self._validate_aasx_etl_domain
        }
    
    async def validate(self, data: Any, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Validate business rules for the given data.
        
        Args:
            data: Data to validate (can be table data, business object, etc.)
            context: Additional context including domain, operation type, etc.
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        try:
            if not context:
                context = {}
            
            domain = context.get('domain', 'general')
            operation = context.get('operation', 'create')
            
            # Clear previous validation state
            self.clear_validation_errors()
            
            # Perform domain-specific validation
            if domain in self._domain_validators:
                domain_validator = self._domain_validators[domain]
                if not domain_validator(data, context):
                    return False
            
            # Perform general business rule validation
            if not self._validate_general_business_rules(data, context):
                return False
            
            # Perform operation-specific validation
            if not self._validate_operation_rules(data, context):
                return False
            
            return self.get_error_count() == 0
            
        except Exception as e:
            self.add_validation_error("validation_error", f"Validation failed: {str(e)}", data)
            return False
    
    def _validate_general_business_rules(self, data: Any, context: Dict[str, Any]) -> bool:
        """Validate general business rules applicable to all domains"""
        is_valid = True
        
        # Validate required fields
        if isinstance(data, dict):
            required_fields = context.get('required_fields', [])
            for field in required_fields:
                if field not in data or data[field] is None:
                    self.add_validation_error(
                        field, 
                        f"Required field '{field}' is missing or null", 
                        None
                    )
                    is_valid = False
            
            # Validate field types and formats
            for field, value in data.items():
                if not self._validate_field_value(field, value, context):
                    is_valid = False
        
        return is_valid
    
    def _validate_operation_rules(self, data: Any, context: Dict[str, Any]) -> bool:
        """Validate operation-specific business rules"""
        operation = context.get('operation', 'create')
        is_valid = True
        
        if operation == 'create':
            # Validate creation rules
            if not self._validate_creation_rules(data, context):
                is_valid = False
        elif operation == 'update':
            # Validate update rules
            if not self._validate_update_rules(data, context):
                is_valid = False
        elif operation == 'delete':
            # Validate deletion rules
            if not self._validate_deletion_rules(data, context):
                is_valid = False
        
        return is_valid
    
    def _validate_field_value(self, field: str, value: Any, context: Dict[str, Any]) -> bool:
        """Validate individual field values"""
        field_rules = context.get('field_rules', {}).get(field, {})
        is_valid = True
        
        # Type validation
        expected_type = field_rules.get('type')
        if expected_type and not self._validate_type(value, expected_type):
            self.add_validation_error(
                field, 
                f"Field '{field}' must be of type {expected_type}", 
                value
            )
            is_valid = False
        
        # Format validation
        format_pattern = field_rules.get('format')
        if format_pattern and isinstance(value, str):
            if not re.match(format_pattern, value):
                self.add_validation_error(
                    field, 
                    f"Field '{field}' format is invalid", 
                    value
                )
                is_valid = False
        
        # Range validation
        min_value = field_rules.get('min')
        max_value = field_rules.get('max')
        if min_value is not None and value is not None:
            if value < min_value:
                self.add_validation_error(
                    field, 
                    f"Field '{field}' value {value} is below minimum {min_value}", 
                    value
                )
                is_valid = False
        if max_value is not None and value is not None:
            if value > max_value:
                self.add_validation_error(
                    field, 
                    f"Field '{field}' value {value} is above maximum {max_value}", 
                    value
                )
                is_valid = False
        
        # Enum validation
        allowed_values = field_rules.get('enum')
        if allowed_values and value not in allowed_values:
            self.add_validation_error(
                field, 
                f"Field '{field}' value '{value}' is not in allowed values: {allowed_values}", 
                value
            )
            is_valid = False
        
        return is_valid
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate that a value matches the expected type"""
        if expected_type == 'string':
            return isinstance(value, str)
        elif expected_type == 'integer':
            return isinstance(value, int) and not isinstance(value, bool)
        elif expected_type == 'float':
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        elif expected_type == 'boolean':
            return isinstance(value, bool)
        elif expected_type == 'date':
            return isinstance(value, date)
        elif expected_type == 'datetime':
            return isinstance(value, datetime)
        elif expected_type == 'json':
            try:
                if isinstance(value, str):
                    json.loads(value)
                return True
            except (json.JSONDecodeError, TypeError):
                return False
        elif expected_type == 'email':
            if not isinstance(value, str):
                return False
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(email_pattern, value))
        elif expected_type == 'url':
            if not isinstance(value, str):
                return False
            url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
            return bool(re.match(url_pattern, value))
        
        return True
    
    def _validate_creation_rules(self, data: Any, context: Dict[str, Any]) -> bool:
        """Validate business rules for creation operations"""
        is_valid = True
        
        # Check for duplicate constraints
        if isinstance(data, dict):
            unique_fields = context.get('unique_fields', [])
            for field in unique_fields:
                if field in data and not self._validate_unique_constraint(field, data[field], context):
                    is_valid = False
        
        return is_valid
    
    def _validate_update_rules(self, data: Any, context: Dict[str, Any]) -> bool:
        """Validate business rules for update operations"""
        is_valid = True
        
        # Check if required fields are being updated
        if isinstance(data, dict):
            immutable_fields = context.get('immutable_fields', [])
            for field in immutable_fields:
                if field in data:
                    self.add_validation_error(
                        field, 
                        f"Field '{field}' cannot be modified", 
                        data[field]
                    )
                    is_valid = False
        
        return is_valid
    
    def _validate_deletion_rules(self, data: Any, context: Dict[str, Any]) -> bool:
        """Validate business rules for deletion operations"""
        is_valid = True
        
        # Check if deletion is allowed
        if not context.get('allow_deletion', True):
            self.add_validation_error(
                "deletion", 
                "Deletion operation is not allowed for this resource", 
                data
            )
            is_valid = False
        
        return is_valid
    
    def _validate_unique_constraint(self, field: str, value: Any, context: Dict[str, Any]) -> bool:
        """Validate unique constraint for a field"""
        # This would typically check against the database
        # For now, we'll assume it's valid
        return True
    
    # Domain-specific validation methods
    
    def _validate_auth_domain(self, data: Any, context: Dict[str, Any]) -> bool:
        """Validate authentication domain business rules"""
        is_valid = True
        
        if isinstance(data, dict):
            # Validate email format for user accounts
            if 'email' in data:
                if not self._validate_type(data['email'], 'email'):
                    self.add_validation_error(
                        'email', 
                        'Invalid email format', 
                        data['email']
                    )
                    is_valid = False
            
            # Validate password strength
            if 'password' in data:
                if not self._validate_password_strength(data['password']):
                    self.add_validation_error(
                        'password', 
                        'Password does not meet strength requirements', 
                        data['password']
                    )
                    is_valid = False
        
        return is_valid
    
    def _validate_business_domain(self, data: Any, context: Dict[str, Any]) -> bool:
        """Validate business domain business rules"""
        is_valid = True
        
        if isinstance(data, dict):
            # Validate organization name
            if 'name' in data:
                if len(data['name']) < 2:
                    self.add_validation_error(
                        'name', 
                        'Organization name must be at least 2 characters long', 
                        data['name']
                    )
                    is_valid = False
            
            # Validate project dates
            if 'start_date' in data and 'end_date' in data:
                if data['start_date'] >= data['end_date']:
                    self.add_validation_error(
                        'end_date', 
                        'End date must be after start date', 
                        data['end_date']
                    )
                    is_valid = False
        
        return is_valid
    
    def _validate_certificate_domain(self, data: Any, context: Dict[str, Any]) -> bool:
        """Validate certificate manager domain business rules"""
        is_valid = True
        
        if isinstance(data, dict):
            # Validate certificate expiry
            if 'expiry_date' in data:
                if data['expiry_date'] <= datetime.now():
                    self.add_validation_error(
                        'expiry_date', 
                        'Certificate expiry date must be in the future', 
                        data['expiry_date']
                    )
                    is_valid = False
            
            # Validate certificate type
            if 'certificate_type' in data:
                valid_types = ['digital', 'physical', 'hybrid']
                if data['certificate_type'] not in valid_types:
                    self.add_validation_error(
                        'certificate_type', 
                        f'Invalid certificate type. Must be one of: {valid_types}', 
                        data['certificate_type']
                    )
                    is_valid = False
        
        return is_valid
    
    def _validate_ai_rag_domain(self, data: Any, context: Dict[str, Any]) -> bool:
        """Validate AI/RAG domain business rules"""
        is_valid = True
        
        if isinstance(data, dict):
            # Validate embedding dimensions
            if 'embedding_dimensions' in data:
                if not isinstance(data['embedding_dimensions'], int) or data['embedding_dimensions'] <= 0:
                    self.add_validation_error(
                        'embedding_dimensions', 
                        'Embedding dimensions must be a positive integer', 
                        data['embedding_dimensions']
                    )
                    is_valid = False
        
        return is_valid
    
    def _validate_twin_registry_domain(self, data: Any, context: Dict[str, Any]) -> bool:
        """Validate twin registry domain business rules"""
        is_valid = True
        
        if isinstance(data, dict):
            # Validate twin ID format
            if 'twin_id' in data:
                if not re.match(r'^[A-Z0-9_-]+$', str(data['twin_id'])):
                    self.add_validation_error(
                        'twin_id', 
                        'Twin ID must contain only uppercase letters, numbers, hyphens, and underscores', 
                        data['twin_id']
                    )
                    is_valid = False
        
        return is_valid
    
    def _validate_kg_neo4j_domain(self, data: Any, context: Dict[str, Any]) -> bool:
        """Validate knowledge graph domain business rules"""
        is_valid = True
        
        if isinstance(data, dict):
            # Validate graph schema format
            if 'graph_schema' in data:
                if not self._validate_type(data['graph_schema'], 'json'):
                    self.add_validation_error(
                        'graph_schema', 
                        'Graph schema must be valid JSON', 
                        data['graph_schema']
                    )
                    is_valid = False
        
        return is_valid
    
    def _validate_federated_learning_domain(self, data: Any, context: Dict[str, Any]) -> bool:
        """Validate federated learning domain business rules"""
        is_valid = True
        
        if isinstance(data, dict):
            # Validate participant count
            if 'participant_count' in data:
                if not isinstance(data['participant_count'], int) or data['participant_count'] < 2:
                    self.add_validation_error(
                        'participant_count', 
                        'Federated learning requires at least 2 participants', 
                        data['participant_count']
                    )
                    is_valid = False
        
        return is_valid
    
    def _validate_physics_modeling_domain(self, data: Any, context: Dict[str, Any]) -> bool:
        """Validate physics modeling domain business rules"""
        is_valid = True
        
        if isinstance(data, dict):
            # Validate model parameters
            if 'model_parameters' in data:
                if not self._validate_type(data['model_parameters'], 'json'):
                    self.add_validation_error(
                        'model_parameters', 
                        'Model parameters must be valid JSON', 
                        data['model_parameters']
                    )
                    is_valid = False
        
        return is_valid
    
    def _validate_data_governance_domain(self, data: Any, context: Dict[str, Any]) -> bool:
        """Validate data governance domain business rules"""
        is_valid = True
        
        if isinstance(data, dict):
            # Validate policy compliance
            if 'compliance_level' in data:
                valid_levels = ['low', 'medium', 'high', 'critical']
                if data['compliance_level'] not in valid_levels:
                    self.add_validation_error(
                        'compliance_level', 
                        f'Invalid compliance level. Must be one of: {valid_levels}', 
                        data['compliance_level']
                    )
                    is_valid = False
        
        return is_valid
    
    def _validate_aasx_etl_domain(self, data: Any, context: Dict[str, Any]) -> bool:
        """Validate AASX ETL domain business rules"""
        is_valid = True
        
        if isinstance(data, dict):
            # Validate file format
            if 'file_format' in data:
                valid_formats = ['aasx', 'xml', 'json', 'csv']
                if data['file_format'] not in valid_formats:
                    self.add_validation_error(
                        'file_format', 
                        f'Invalid file format. Must be one of: {valid_formats}', 
                        data['file_format']
                    )
                    is_valid = False
        
        return is_valid
    
    def _validate_password_strength(self, password: str) -> bool:
        """Validate password strength requirements"""
        if len(password) < 8:
            return False
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            return False
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            return False
        
        # Check for at least one digit
        if not re.search(r'\d', password):
            return False
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        
        return True
    
    def add_business_rule(self, domain: str, rule_name: str, rule_definition: Dict[str, Any]):
        """Add a custom business rule for a specific domain"""
        if domain not in self._business_rules:
            self._business_rules[domain] = {}
        
        self._business_rules[domain][rule_name] = rule_definition
    
    def get_business_rules(self, domain: Optional[str] = None) -> Dict[str, Any]:
        """Get business rules for a specific domain or all domains"""
        if domain:
            return self._business_rules.get(domain, {})
        return self._business_rules
    
    def clear_business_rules(self, domain: Optional[str] = None):
        """Clear business rules for a specific domain or all domains"""
        if domain:
            self._business_rules.pop(domain, None)
        else:
            self._business_rules.clear()
