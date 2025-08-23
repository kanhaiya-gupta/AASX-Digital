"""
Validation Utilities

This module provides comprehensive validation utilities for data validation, rule management,
and validation result handling.
"""

import asyncio
import logging
import time
import re
from typing import Dict, List, Optional, Union, Any, Tuple, Callable
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


class ValidationRule(Enum):
    """Validation rule types"""
    REQUIRED = "required"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    PATTERN = "pattern"
    RANGE = "range"
    EMAIL = "email"
    URL = "url"
    PHONE = "phone"
    DATE = "date"
    CUSTOM = "custom"
    NESTED = "nested"
    ARRAY = "array"
    OBJECT = "object"


class ValidationSeverity(Enum):
    """Validation severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"


@dataclass
class ValidationResult:
    """Validation result information"""
    field: str
    value: Any
    rule: ValidationRule
    severity: ValidationSeverity
    message: str
    is_valid: bool
    timestamp: float
    metadata: Optional[Dict[str, Any]] = None


class ValidationUtils:
    """
    Validation utilities and management service
    
    Handles:
    - Data validation using various rules
    - Custom validation rule creation
    - Validation result management
    - Batch validation operations
    - Validation rule storage
    - Performance optimization
    """
    
    def __init__(self):
        """Initialize the validation utilities service"""
        self.validation_rules = list(ValidationRule)
        self.validation_severities = list(ValidationSeverity)
        
        # Validation storage and metadata
        self.validation_rules_config: Dict[str, Dict[str, Any]] = {}
        self.validation_history: List[Dict[str, Any]] = []
        self.custom_validators: Dict[str, Callable] = {}
        
        # Validation locks and queues
        self.validation_locks: Dict[str, asyncio.Lock] = {}
        self.validation_queue: asyncio.Queue = asyncio.Queue()
        
        # Performance tracking
        self.validation_stats = {
            "total_validations": 0,
            "successful": 0,
            "failed": 0,
            "average_time": 0.0,
            "total_fields_validated": 0
        }
        
        # Initialize default validation rules
        self._initialize_default_rules()
        
        logger.info("Validation utilities service initialized successfully")
    
    async def validate_data(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        schema: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate data using the specified schema
        
        Args:
            data: Data to validate
            schema: Validation schema
            metadata: Additional metadata for the validation
            
        Returns:
            Dictionary containing validation results and metadata
        """
        start_time = time.time()
        validation_id = f"validation_{int(time.time() * 1000)}"
        
        try:
            # Validate input parameters
            await self._validate_validation_params(data, schema)
            
            # Prepare data for validation
            prepared_data = await self._prepare_data_for_validation(data)
            
            # Perform validation
            validation_results = await self._perform_validation(prepared_data, schema)
            
            # Create metadata
            validation_metadata = await self._create_validation_metadata(
                validation_id, data, schema, metadata
            )
            
            # Store validation results
            validation_info = {
                "id": validation_id,
                "data": prepared_data,
                "schema": schema,
                "results": validation_results,
                "metadata": validation_metadata,
                "validated_at": time.time(),
                "total_fields": len(validation_results),
                "valid_fields": sum(1 for r in validation_results if r.is_valid),
                "invalid_fields": sum(1 for r in validation_results if not r.is_valid),
                "status": "completed"
            }
            
            self.validation_history.append(validation_info)
            
            # Update statistics
            await self._update_validation_stats(True, time.time() - start_time, len(validation_results))
            
            logger.info(f"Data validation completed successfully: {validation_id}")
            return validation_info
            
        except Exception as e:
            await self._update_validation_stats(False, time.time() - start_time, 0)
            logger.error(f"Failed to validate data: {str(e)}")
            raise
    
    async def validate_batch_data(
        self,
        data_list: List[Union[Dict[str, Any], List[Dict[str, Any]]]],
        schema: Dict[str, Any],
        batch_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Validate multiple data items in batch
        
        Args:
            data_list: List of data items to validate
            schema: Validation schema
            batch_metadata: Additional metadata for the batch
            
        Returns:
            List of validation results
        """
        batch_id = f"batch_{int(time.time() * 1000)}"
        results = []
        
        logger.info(f"Starting batch data validation: {batch_id}")
        
        # Create tasks for concurrent validation
        tasks = []
        for i, data in enumerate(data_list):
            task = asyncio.create_task(
                self.validate_data(data, schema, {
                    "batch_id": batch_id,
                    "batch_index": i,
                    **(batch_metadata or {})
                })
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(batch_results):
            if isinstance(result, Exception):
                logger.error(f"Failed to validate data {i} in batch {batch_id}: {str(result)}")
                results.append({
                    "id": f"failed_{batch_id}_{i}",
                    "status": "failed",
                    "error": str(result),
                    "batch_id": batch_id,
                    "batch_index": i
                })
            else:
                results.append(result)
        
        logger.info(f"Batch data validation completed: {batch_id}, {len(results)} results")
        return results
    
    async def create_validation_rule(
        self,
        rule_name: str,
        rule_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a custom validation rule
        
        Args:
            rule_name: Name of the validation rule
            rule_config: Rule configuration
            
        Returns:
            Rule creation result
        """
        if rule_name in self.validation_rules_config:
            raise ValueError(f"Validation rule already exists: {rule_name}")
        
        self.validation_rules_config[rule_name] = rule_config
        
        return {
            "rule_name": rule_name,
            "config": rule_config,
            "created_at": time.time(),
            "status": "created"
        }
    
    async def add_custom_validator(
        self,
        validator_name: str,
        validator_func: Callable
    ) -> Dict[str, Any]:
        """
        Add a custom validator function
        
        Args:
            validator_name: Name of the custom validator
            validator_func: Validator function
            
        Returns:
            Validator addition result
        """
        if validator_name in self.custom_validators:
            raise ValueError(f"Custom validator already exists: {validator_name}")
        
        self.custom_validators[validator_name] = validator_func
        
        return {
            "validator_name": validator_name,
            "added_at": time.time(),
            "status": "added"
        }
    
    async def validate_field(
        self,
        field_name: str,
        field_value: Any,
        field_rules: List[Dict[str, Any]]
    ) -> List[ValidationResult]:
        """
        Validate a single field using specified rules
        
        Args:
            field_name: Name of the field
            field_value: Value of the field
            field_rules: List of validation rules
            
        Returns:
            List of validation results for the field
        """
        results = []
        
        for rule_config in field_rules:
            rule_type = ValidationRule(rule_config.get("type", "required"))
            severity = ValidationSeverity(rule_config.get("severity", "error"))
            
            # Apply validation rule
            is_valid, message = await self._apply_validation_rule(
                field_value, rule_type, rule_config
            )
            
            # Create validation result
            result = ValidationResult(
                field=field_name,
                value=field_value,
                rule=rule_type,
                severity=severity,
                message=message,
                is_valid=is_valid,
                timestamp=time.time(),
                metadata=rule_config
            )
            
            results.append(result)
        
        return results
    
    async def get_validation_info(self, validation_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a validation operation
        
        Args:
            validation_id: ID of the validation operation
            
        Returns:
            Validation operation information
        """
        for validation_info in self.validation_history:
            if validation_info.get("id") == validation_id:
                return validation_info
        
        raise ValueError(f"Validation operation not found: {validation_id}")
    
    async def get_validation_history(
        self,
        schema: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get validation operation history
        
        Args:
            schema: Filter by schema name
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of validation operation history entries
        """
        history = self.validation_history
        
        if schema:
            history = [h for h in history if h.get("schema_name") == schema]
        
        # Sort by validation time (newest first)
        history.sort(key=lambda x: x.get("validated_at", 0), reverse=True)
        
        return history[offset:offset + limit]
    
    async def get_validation_statistics(self) -> Dict[str, Any]:
        """
        Get validation operation statistics
        
        Returns:
            Validation operation statistics
        """
        return self.validation_stats.copy()
    
    async def cleanup_expired_validations(self, max_age_hours: int = 24) -> int:
        """
        Clean up expired validation operations
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
            
        Returns:
            Number of validations cleaned up
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        expired_validations = []
        for validation_info in self.validation_history:
            if current_time - validation_info.get("validated_at", 0) > max_age_seconds:
                expired_validations.append(validation_info.get("id"))
        
        # Remove expired validations
        self.validation_history = [
            v for v in self.validation_history
            if v.get("id") not in expired_validations
        ]
        
        logger.info(f"Cleaned up {len(expired_validations)} expired validations")
        return len(expired_validations)
    
    # Private helper methods
    
    def _initialize_default_rules(self):
        """Initialize default validation rules"""
        # Required field rule
        self.validation_rules_config["required"] = {
            "type": "required",
            "severity": "error",
            "message": "Field is required"
        }
        
        # Min length rule
        self.validation_rules_config["min_length"] = {
            "type": "min_length",
            "severity": "error",
            "message": "Field value is too short"
        }
        
        # Max length rule
        self.validation_rules_config["max_length"] = {
            "type": "max_length",
            "severity": "error",
            "message": "Field value is too long"
        }
        
        # Pattern rule
        self.validation_rules_config["pattern"] = {
            "type": "pattern",
            "severity": "error",
            "message": "Field value does not match pattern"
        }
        
        # Email rule
        self.validation_rules_config["email"] = {
            "type": "email",
            "severity": "error",
            "message": "Field value is not a valid email"
        }
        
        # URL rule
        self.validation_rules_config["url"] = {
            "type": "url",
            "severity": "error",
            "message": "Field value is not a valid URL"
        }
    
    async def _validate_validation_params(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        schema: Dict[str, Any]
    ):
        """Validate validation parameters"""
        if not data:
            raise ValueError("Data cannot be empty")
        
        if not schema:
            raise ValueError("Schema cannot be empty")
        
        if not isinstance(schema, dict):
            raise ValueError("Schema must be a dictionary")
    
    async def _prepare_data_for_validation(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Prepare data for validation"""
        if isinstance(data, list):
            return {"array_data": data}
        elif isinstance(data, dict):
            return data
        else:
            return {"raw_data": str(data)}
    
    async def _perform_validation(
        self,
        data: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Perform validation using the schema"""
        results = []
        
        for field_name, field_rules in schema.items():
            field_value = data.get(field_name)
            
            # Validate field
            field_results = await self.validate_field(field_name, field_value, field_rules)
            results.extend(field_results)
        
        return results
    
    async def _apply_validation_rule(
        self,
        value: Any,
        rule_type: ValidationRule,
        rule_config: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Apply a validation rule to a value"""
        try:
            if rule_type == ValidationRule.REQUIRED:
                return await self._validate_required(value, rule_config)
            elif rule_type == ValidationRule.MIN_LENGTH:
                return await self._validate_min_length(value, rule_config)
            elif rule_type == ValidationRule.MAX_LENGTH:
                return await self._validate_max_length(value, rule_config)
            elif rule_type == ValidationRule.PATTERN:
                return await self._validate_pattern(value, rule_config)
            elif rule_type == ValidationRule.EMAIL:
                return await self._validate_email(value, rule_config)
            elif rule_type == ValidationRule.URL:
                return await self._validate_url(value, rule_config)
            elif rule_type == ValidationRule.CUSTOM:
                return await self._validate_custom(value, rule_config)
            else:
                return True, "Rule type not implemented"
        
        except Exception as e:
            logger.error(f"Error applying validation rule {rule_type.value}: {str(e)}")
            return False, f"Validation error: {str(e)}"
    
    async def _validate_required(self, value: Any, rule_config: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate required field"""
        if value is None or (isinstance(value, str) and not value.strip()):
            return False, rule_config.get("message", "Field is required")
        return True, "Field is valid"
    
    async def _validate_min_length(self, value: Any, rule_config: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate minimum length"""
        min_length = rule_config.get("value", 0)
        
        if value is None:
            return True, "Field is optional"
        
        if isinstance(value, (str, list, dict)):
            if len(value) < min_length:
                return False, rule_config.get("message", f"Minimum length is {min_length}")
        
        return True, "Field length is valid"
    
    async def _validate_max_length(self, value: Any, rule_config: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate maximum length"""
        max_length = rule_config.get("value", float('inf'))
        
        if value is None:
            return True, "Field is optional"
        
        if isinstance(value, (str, list, dict)):
            if len(value) > max_length:
                return False, rule_config.get("message", f"Maximum length is {max_length}")
        
        return True, "Field length is valid"
    
    async def _validate_pattern(self, value: Any, rule_config: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate pattern"""
        pattern = rule_config.get("value", "")
        
        if value is None:
            return True, "Field is optional"
        
        if not isinstance(value, str):
            return False, "Field must be a string for pattern validation"
        
        if not re.match(pattern, value):
            return False, rule_config.get("message", f"Value does not match pattern: {pattern}")
        
        return True, "Field pattern is valid"
    
    async def _validate_email(self, value: Any, rule_config: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate email format"""
        if value is None:
            return True, "Field is optional"
        
        if not isinstance(value, str):
            return False, "Field must be a string for email validation"
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            return False, rule_config.get("message", "Field value is not a valid email")
        
        return True, "Field email format is valid"
    
    async def _validate_url(self, value: Any, rule_config: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate URL format"""
        if value is None:
            return True, "Field is optional"
        
        if not isinstance(value, str):
            return False, "Field must be a string for URL validation"
        
        url_pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
        if not re.match(url_pattern, value):
            return False, rule_config.get("message", "Field value is not a valid URL")
        
        return True, "Field URL format is valid"
    
    async def _validate_custom(self, value: Any, rule_config: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate using custom validator"""
        validator_name = rule_config.get("validator")
        
        if not validator_name or validator_name not in self.custom_validators:
            return False, "Custom validator not found"
        
        try:
            validator_func = self.custom_validators[validator_name]
            result = validator_func(value)
            
            if isinstance(result, bool):
                return result, rule_config.get("message", "Custom validation result")
            elif isinstance(result, tuple) and len(result) == 2:
                return result[0], result[1]
            else:
                return False, "Invalid custom validator return value"
        
        except Exception as e:
            logger.error(f"Error in custom validator {validator_name}: {str(e)}")
            return False, f"Custom validation error: {str(e)}"
    
    async def _create_validation_metadata(
        self,
        validation_id: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        schema: Dict[str, Any],
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create metadata for validation operations"""
        base_metadata = {
            "generator": "CertificateManager",
            "version": "1.0.0",
            "schema_hash": hash(str(schema)),
            "data_hash": hash(str(data)),
            "timestamp": time.time()
        }
        
        if metadata:
            base_metadata.update(metadata)
        
        return base_metadata
    
    async def _update_validation_stats(self, success: bool, validation_time: float, fields_count: int):
        """Update validation statistics"""
        self.validation_stats["total_validations"] += 1
        
        if success:
            self.validation_stats["successful"] += 1
            self.validation_stats["total_fields_validated"] += fields_count
        else:
            self.validation_stats["failed"] += 1
        
        # Update average validation time
        total_successful = self.validation_stats["successful"]
        if total_successful > 0:
            current_avg = self.validation_stats["average_time"]
            self.validation_stats["average_time"] = (
                (current_avg * (total_successful - 1) + validation_time) / total_successful
            )
