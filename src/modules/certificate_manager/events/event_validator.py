"""
Event Validator

This module provides comprehensive event validation services for certificate management
including schema validation, business rule validation, and data integrity checks.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Event validation status"""
    VALID = "valid"
    INVALID = "invalid"
    PENDING = "pending"
    ERROR = "error"
    WARNING = "warning"


class ValidationRule(Enum):
    """Event validation rules"""
    SCHEMA_VALIDATION = "schema_validation"
    BUSINESS_RULE_VALIDATION = "business_rule_validation"
    DATA_INTEGRITY_VALIDATION = "data_integrity_validation"
    SECURITY_VALIDATION = "security_validation"
    COMPLIANCE_VALIDATION = "compliance_validation"
    FORMAT_VALIDATION = "format_validation"
    SIZE_VALIDATION = "size_validation"
    TIMESTAMP_VALIDATION = "timestamp_validation"


class ValidationSeverity(Enum):
    """Validation severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class ValidationResult:
    """Event validation result"""
    event_id: str
    validation_status: ValidationStatus
    validation_rules: List[ValidationRule]
    validation_errors: List[Dict[str, Any]]
    validation_warnings: List[Dict[str, Any]]
    validation_timestamp: float
    validation_duration: float
    metadata: Dict[str, Any]


class EventValidator:
    """
    Event validation service for certificate management
    
    Handles:
    - Event schema validation
    - Business rule validation
    - Data integrity validation
    - Security validation
    - Compliance validation
    - Performance optimization
    """
    
    def __init__(self):
        """Initialize the event validator service"""
        self.validation_statuses = list(ValidationStatus)
        self.validation_rules = list(ValidationRule)
        self.validation_severities = list(ValidationSeverity)
        
        # Validation storage and metadata
        self.validation_results: Dict[str, ValidationResult] = {}
        self.validation_schemas: Dict[str, Dict[str, Any]] = {}
        self.validation_history: List[Dict[str, Any]] = []
        
        # Validation locks and queues
        self.validation_locks: Dict[str, asyncio.Lock] = {}
        self.validation_queue: asyncio.Queue = asyncio.Queue()
        
        # Performance tracking
        self.validation_stats = {
            "total_validations": 0,
            "successful": 0,
            "failed": 0,
            "average_time": 0.0,
            "total_events_validated": 0
        }
        
        # Initialize default validation schemas
        self._initialize_default_schemas()
        
        logger.info("Event Validator service initialized successfully")
    
    async def validate_event(
        self,
        event_data: Dict[str, Any],
        event_type: str,
        validation_rules: Optional[List[ValidationRule]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate an event using specified validation rules
        
        Args:
            event_data: Event data to validate
            event_type: Type of event to validate
            validation_rules: List of validation rules to apply
            metadata: Additional metadata for validation
            
        Returns:
            Validation result containing status and details
        """
        start_time = time.time()
        event_id = event_data.get("id", f"event_{int(time.time() * 1000)}")
        
        try:
            # Validate input parameters
            await self._validate_validation_params(event_data, event_type, validation_rules)
            
            # Get validation rules to apply
            rules_to_apply = validation_rules or self._get_default_validation_rules(event_type)
            
            # Perform validation
            validation_result = await self._perform_event_validation(
                event_data, event_type, rules_to_apply, metadata
            )
            
            # Store validation result
            self.validation_results[event_id] = validation_result
            self.validation_history.append({
                "event_id": event_id,
                "event_type": event_type,
                "validation_result": validation_result.__dict__,
                "validated_at": time.time(),
                "metadata": metadata or {}
            })
            
            # Update statistics
            await self._update_validation_stats(True, time.time() - start_time)
            
            logger.info(f"Event validation completed successfully: {event_id}")
            return validation_result
            
        except Exception as e:
            await self._update_validation_stats(False, time.time() - start_time)
            logger.error(f"Failed to validate event: {str(e)}")
            raise
    
    async def validate_events_batch(
        self,
        events_data: List[Tuple[Dict[str, Any], str]],
        validation_rules: Optional[List[ValidationRule]] = None,
        batch_metadata: Optional[Dict[str, Any]] = None
    ) -> List[ValidationResult]:
        """
        Validate multiple events in batch
        
        Args:
            events_data: List of tuples containing event data and event types
            validation_rules: List of validation rules to apply
            batch_metadata: Additional metadata for the batch
            
        Returns:
            List of validation results
        """
        batch_id = f"batch_{int(time.time() * 1000)}"
        results = []
        
        logger.info(f"Starting batch event validation: {batch_id}")
        
        # Create tasks for concurrent validation
        tasks = []
        for i, (event_data, event_type) in enumerate(events_data):
            task = asyncio.create_task(
                self.validate_event(event_data, event_type, validation_rules, {
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
                logger.error(f"Failed to validate event {i} in batch {batch_id}: {str(result)}")
                # Create error result
                error_result = ValidationResult(
                    event_id=f"failed_{batch_id}_{i}",
                    validation_status=ValidationStatus.ERROR,
                    validation_rules=validation_rules or [],
                    validation_errors=[{"error": str(result), "batch_id": batch_id, "batch_index": i}],
                    validation_warnings=[],
                    validation_timestamp=time.time(),
                    validation_duration=0.0,
                    metadata={"batch_id": batch_id, "batch_index": i}
                )
                results.append(error_result)
            else:
                results.append(result)
        
        logger.info(f"Batch event validation completed: {batch_id}, {len(results)} results")
        return results
    
    async def create_validation_schema(
        self,
        schema_name: str,
        schema_definition: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new validation schema
        
        Args:
            schema_name: Name of the validation schema
            schema_definition: Schema definition
            
        Returns:
            Schema creation result
        """
        if schema_name in self.validation_schemas:
            raise ValueError(f"Validation schema already exists: {schema_name}")
        
        self.validation_schemas[schema_name] = schema_definition
        
        return {
            "schema_name": schema_name,
            "definition": schema_definition,
            "created_at": time.time(),
            "status": "created"
        }
    
    async def update_validation_schema(
        self,
        schema_name: str,
        schema_definition: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing validation schema
        
        Args:
            schema_name: Name of the validation schema to update
            schema_definition: Updated schema definition
            
        Returns:
            Schema update result
        """
        if schema_name not in self.validation_schemas:
            raise ValueError(f"Validation schema not found: {schema_name}")
        
        self.validation_schemas[schema_name] = schema_definition
        
        return {
            "schema_name": schema_name,
            "definition": schema_definition,
            "updated_at": time.time(),
            "status": "updated"
        }
    
    async def delete_validation_schema(self, schema_name: str) -> Dict[str, Any]:
        """
        Delete a validation schema
        
        Args:
            schema_name: Name of the validation schema to delete
            
        Returns:
            Schema deletion result
        """
        if schema_name not in self.validation_schemas:
            raise ValueError(f"Validation schema not found: {schema_name}")
        
        del self.validation_schemas[schema_name]
        
        return {
            "schema_name": schema_name,
            "deleted_at": time.time(),
            "status": "deleted"
        }
    
    async def get_validation_schema(self, schema_name: str) -> Dict[str, Any]:
        """
        Get a validation schema
        
        Args:
            schema_name: Name of the validation schema
            
        Returns:
            Validation schema definition
        """
        if schema_name not in self.validation_schemas:
            raise ValueError(f"Validation schema not found: {schema_name}")
        
        return self.validation_schemas[schema_name]
    
    async def list_validation_schemas(self) -> List[Dict[str, Any]]:
        """
        List all validation schemas
        
        Returns:
            List of validation schemas
        """
        schemas = []
        
        for schema_name, schema_definition in self.validation_schemas.items():
            schemas.append({
                "schema_name": schema_name,
                "definition": schema_definition
            })
        
        return schemas
    
    async def get_validation_result(self, event_id: str) -> ValidationResult:
        """
        Get validation result for a specific event
        
        Args:
            event_id: ID of the event
            
        Returns:
            Validation result
        """
        if event_id not in self.validation_results:
            raise ValueError(f"Validation result not found: {event_id}")
        
        return self.validation_results[event_id]
    
    async def get_validation_history(
        self,
        event_type: Optional[str] = None,
        validation_status: Optional[ValidationStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get validation history
        
        Args:
            event_type: Filter by event type
            validation_status: Filter by validation status
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of validation history entries
        """
        history = self.validation_history
        
        if event_type:
            history = [h for h in history if h.get("event_type") == event_type]
        
        if validation_status:
            history = [h for h in history if h.get("validation_result", {}).get("validation_status") == validation_status.value]
        
        # Sort by validation time (newest first)
        history.sort(key=lambda x: x.get("validated_at", 0), reverse=True)
        
        return history[offset:offset + limit]
    
    async def get_validation_statistics(self) -> Dict[str, Any]:
        """
        Get validation statistics
        
        Returns:
            Validation statistics
        """
        return self.validation_stats.copy()
    
    async def cleanup_expired_validations(self, max_age_hours: int = 24) -> int:
        """
        Clean up expired validation results
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
            
        Returns:
            Number of validations cleaned up
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        expired_validations = []
        for event_id, validation_result in self.validation_results.items():
            if current_time - validation_result.validation_timestamp > max_age_seconds:
                expired_validations.append(event_id)
        
        # Remove expired validations
        for event_id in expired_validations:
            del self.validation_results[event_id]
        
        logger.info(f"Cleaned up {len(expired_validations)} expired validations")
        return len(expired_validations)
    
    # Private helper methods
    
    def _initialize_default_schemas(self):
        """Initialize default validation schemas"""
        # Certificate event schema
        self.validation_schemas["certificate_event"] = {
            "required_fields": ["id", "type", "timestamp", "data"],
            "field_types": {
                "id": "string",
                "type": "string",
                "timestamp": "number",
                "data": "object"
            },
            "field_validations": {
                "id": {"min_length": 1, "max_length": 100},
                "type": {"allowed_values": ["created", "updated", "deleted", "validated"]},
                "timestamp": {"min_value": 0, "max_value": 9999999999},
                "data": {"required": True}
            }
        }
        
        # Performance event schema
        self.validation_schemas["performance_event"] = {
            "required_fields": ["id", "type", "timestamp", "metrics"],
            "field_types": {
                "id": "string",
                "type": "string",
                "timestamp": "number",
                "metrics": "object"
            },
            "field_validations": {
                "id": {"min_length": 1, "max_length": 100},
                "type": {"allowed_values": ["measurement", "alert", "threshold_exceeded"]},
                "timestamp": {"min_value": 0, "max_value": 9999999999},
                "metrics": {"required": True}
            }
        }
        
        # Security event schema
        self.validation_schemas["security_event"] = {
            "required_fields": ["id", "type", "timestamp", "security_data"],
            "field_types": {
                "id": "string",
                "type": "string",
                "timestamp": "number",
                "security_data": "object"
            },
            "field_validations": {
                "id": {"min_length": 1, "max_length": 100},
                "type": {"allowed_values": ["authentication", "authorization", "audit", "threat"]},
                "timestamp": {"min_value": 0, "max_value": 9999999999},
                "security_data": {"required": True}
            }
        }
    
    async def _validate_validation_params(
        self,
        event_data: Dict[str, Any],
        event_type: str,
        validation_rules: Optional[List[ValidationRule]]
    ):
        """Validate validation parameters"""
        if not event_data:
            raise ValueError("Event data cannot be empty")
        
        if not isinstance(event_data, dict):
            raise ValueError("Event data must be a dictionary")
        
        if not event_type:
            raise ValueError("Event type cannot be empty")
        
        if validation_rules and not isinstance(validation_rules, list):
            raise ValueError("Validation rules must be a list")
    
    def _get_default_validation_rules(self, event_type: str) -> List[ValidationRule]:
        """Get default validation rules for event type"""
        if event_type.startswith("certificate"):
            return [
                ValidationRule.SCHEMA_VALIDATION,
                ValidationRule.BUSINESS_RULE_VALIDATION,
                ValidationRule.DATA_INTEGRITY_VALIDATION
            ]
        elif event_type.startswith("performance"):
            return [
                ValidationRule.SCHEMA_VALIDATION,
                ValidationRule.FORMAT_VALIDATION,
                ValidationRule.TIMESTAMP_VALIDATION
            ]
        elif event_type.startswith("security"):
            return [
                ValidationRule.SCHEMA_VALIDATION,
                ValidationRule.SECURITY_VALIDATION,
                ValidationRule.COMPLIANCE_VALIDATION
            ]
        else:
            return [
                ValidationRule.SCHEMA_VALIDATION,
                ValidationRule.FORMAT_VALIDATION
            ]
    
    async def _perform_event_validation(
        self,
        event_data: Dict[str, Any],
        event_type: str,
        validation_rules: List[ValidationRule],
        metadata: Optional[Dict[str, Any]]
    ) -> ValidationResult:
        """Perform event validation using specified rules"""
        start_time = time.time()
        event_id = event_data.get("id", f"event_{int(time.time() * 1000)}")
        
        validation_errors = []
        validation_warnings = []
        
        try:
            # Apply each validation rule
            for rule in validation_rules:
                rule_result = await self._apply_validation_rule(event_data, event_type, rule)
                
                if rule_result.get("status") == "error":
                    validation_errors.append(rule_result)
                elif rule_result.get("status") == "warning":
                    validation_warnings.append(rule_result)
            
            # Determine overall validation status
            if validation_errors:
                validation_status = ValidationStatus.INVALID
            elif validation_warnings:
                validation_status = ValidationStatus.WARNING
            else:
                validation_status = ValidationStatus.VALID
            
            validation_duration = time.time() - start_time
            
            return ValidationResult(
                event_id=event_id,
                validation_status=validation_status,
                validation_rules=validation_rules,
                validation_errors=validation_errors,
                validation_warnings=validation_warnings,
                validation_timestamp=time.time(),
                validation_duration=validation_duration,
                metadata=metadata or {}
            )
        
        except Exception as e:
            validation_duration = time.time() - start_time
            validation_errors.append({
                "rule": "general",
                "status": "error",
                "message": str(e),
                "severity": ValidationSeverity.CRITICAL.value
            })
            
            return ValidationResult(
                event_id=event_id,
                validation_status=ValidationStatus.ERROR,
                validation_rules=validation_rules,
                validation_errors=validation_errors,
                validation_warnings=validation_warnings,
                validation_timestamp=time.time(),
                validation_duration=validation_duration,
                metadata=metadata or {}
            )
    
    async def _apply_validation_rule(
        self,
        event_data: Dict[str, Any],
        event_type: str,
        rule: ValidationRule
    ) -> Dict[str, Any]:
        """Apply a specific validation rule"""
        try:
            if rule == ValidationRule.SCHEMA_VALIDATION:
                return await self._validate_schema(event_data, event_type)
            elif rule == ValidationRule.BUSINESS_RULE_VALIDATION:
                return await self._validate_business_rules(event_data, event_type)
            elif rule == ValidationRule.DATA_INTEGRITY_VALIDATION:
                return await self._validate_data_integrity(event_data, event_type)
            elif rule == ValidationRule.SECURITY_VALIDATION:
                return await self._validate_security(event_data, event_type)
            elif rule == ValidationRule.COMPLIANCE_VALIDATION:
                return await self._validate_compliance(event_data, event_type)
            elif rule == ValidationRule.FORMAT_VALIDATION:
                return await self._validate_format(event_data, event_type)
            elif rule == ValidationRule.SIZE_VALIDATION:
                return await self._validate_size(event_data, event_type)
            elif rule == ValidationRule.TIMESTAMP_VALIDATION:
                return await self._validate_timestamp(event_data, event_type)
            else:
                return {
                    "rule": rule.value,
                    "status": "warning",
                    "message": f"Unknown validation rule: {rule.value}",
                    "severity": ValidationSeverity.LOW.value
                }
        
        except Exception as e:
            return {
                "rule": rule.value,
                "status": "error",
                "message": str(e),
                "severity": ValidationSeverity.CRITICAL.value
            }
    
    async def _validate_schema(
        self,
        event_data: Dict[str, Any],
        event_type: str
    ) -> Dict[str, Any]:
        """Validate event schema"""
        try:
            schema_name = f"{event_type}_event"
            if schema_name not in self.validation_schemas:
                return {
                    "rule": "schema_validation",
                    "status": "warning",
                    "message": f"No schema found for event type: {event_type}",
                    "severity": ValidationSeverity.LOW.value
                }
            
            schema = self.validation_schemas[schema_name]
            required_fields = schema.get("required_fields", [])
            field_types = schema.get("field_types", {})
            field_validations = schema.get("field_validations", {})
            
            # Check required fields
            for field in required_fields:
                if field not in event_data:
                    return {
                        "rule": "schema_validation",
                        "status": "error",
                        "message": f"Required field missing: {field}",
                        "severity": ValidationSeverity.HIGH.value
                    }
            
            # Check field types and validations
            for field, validations in field_validations.items():
                if field in event_data:
                    field_value = event_data[field]
                    
                    # Type validation
                    expected_type = field_types.get(field, "any")
                    if not await self._validate_field_type(field_value, expected_type):
                        return {
                            "rule": "schema_validation",
                            "status": "error",
                            "message": f"Invalid field type for {field}: expected {expected_type}",
                            "severity": ValidationSeverity.MEDIUM.value
                        }
                    
                    # Field-specific validations
                    for validation_type, validation_value in validations.items():
                        if not await self._validate_field_value(field_value, validation_type, validation_value):
                            return {
                                "rule": "schema_validation",
                                "status": "error",
                                "message": f"Field validation failed for {field}: {validation_type}",
                                "severity": ValidationSeverity.MEDIUM.value
                            }
            
            return {
                "rule": "schema_validation",
                "status": "success",
                "message": "Schema validation passed",
                "severity": ValidationSeverity.INFO.value
            }
        
        except Exception as e:
            return {
                "rule": "schema_validation",
                "status": "error",
                "message": str(e),
                "severity": ValidationSeverity.CRITICAL.value
            }
    
    async def _validate_business_rules(
        self,
        event_data: Dict[str, Any],
        event_type: str
    ) -> Dict[str, Any]:
        """Validate business rules"""
        try:
            # Simulate business rule validation
            if event_type == "certificate_created":
                if not event_data.get("data", {}).get("title"):
                    return {
                        "rule": "business_rule_validation",
                        "status": "error",
                        "message": "Certificate title is required",
                        "severity": ValidationSeverity.HIGH.value
                    }
            
            return {
                "rule": "business_rule_validation",
                "status": "success",
                "message": "Business rule validation passed",
                "severity": ValidationSeverity.INFO.value
            }
        
        except Exception as e:
            return {
                "rule": "business_rule_validation",
                "status": "error",
                "message": str(e),
                "severity": ValidationSeverity.CRITICAL.value
            }
    
    async def _validate_data_integrity(
        self,
        event_data: Dict[str, Any],
        event_type: str
    ) -> Dict[str, Any]:
        """Validate data integrity"""
        try:
            # Simulate data integrity validation
            if "data" in event_data and isinstance(event_data["data"], dict):
                # Check for circular references
                if await self._has_circular_references(event_data["data"]):
                    return {
                        "rule": "data_integrity_validation",
                        "status": "error",
                        "message": "Circular references detected in data",
                        "severity": ValidationSeverity.HIGH.value
                    }
            
            return {
                "rule": "data_integrity_validation",
                "status": "success",
                "message": "Data integrity validation passed",
                "severity": ValidationSeverity.INFO.value
            }
        
        except Exception as e:
            return {
                "rule": "data_integrity_validation",
                "status": "error",
                "message": str(e),
                "severity": ValidationSeverity.CRITICAL.value
            }
    
    async def _validate_security(
        self,
        event_data: Dict[str, Any],
        event_type: str
    ) -> Dict[str, Any]:
        """Validate security aspects"""
        try:
            # Simulate security validation
            if "security_data" in event_data:
                security_data = event_data["security_data"]
                if isinstance(security_data, dict) and "permissions" in security_data:
                    permissions = security_data["permissions"]
                    if not isinstance(permissions, list) or len(permissions) == 0:
                        return {
                            "rule": "security_validation",
                            "status": "warning",
                            "message": "No permissions specified",
                            "severity": ValidationSeverity.MEDIUM.value
                        }
            
            return {
                "rule": "security_validation",
                "status": "success",
                "message": "Security validation passed",
                "severity": ValidationSeverity.INFO.value
            }
        
        except Exception as e:
            return {
                "rule": "security_validation",
                "status": "error",
                "message": str(e),
                "severity": ValidationSeverity.CRITICAL.value
            }
    
    async def _validate_compliance(
        self,
        event_data: Dict[str, Any],
        event_type: str
    ) -> Dict[str, Any]:
        """Validate compliance requirements"""
        try:
            # Simulate compliance validation
            if event_type.startswith("certificate"):
                if "compliance_data" not in event_data:
                    return {
                        "rule": "compliance_validation",
                        "status": "warning",
                        "message": "Compliance data not provided",
                        "severity": ValidationSeverity.LOW.value
                    }
            
            return {
                "rule": "compliance_validation",
                "status": "success",
                "message": "Compliance validation passed",
                "severity": ValidationSeverity.INFO.value
            }
        
        except Exception as e:
            return {
                "rule": "compliance_validation",
                "status": "error",
                "message": str(e),
                "severity": ValidationSeverity.CRITICAL.value
            }
    
    async def _validate_format(
        self,
        event_data: Dict[str, Any],
        event_type: str
    ) -> Dict[str, Any]:
        """Validate data format"""
        try:
            # Simulate format validation
            if "format" in event_data:
                allowed_formats = ["json", "xml", "yaml", "csv"]
                if event_data["format"] not in allowed_formats:
                    return {
                        "rule": "format_validation",
                        "status": "error",
                        "message": f"Invalid format: {event_data['format']}",
                        "severity": ValidationSeverity.MEDIUM.value
                    }
            
            return {
                "rule": "format_validation",
                "status": "success",
                "message": "Format validation passed",
                "severity": ValidationSeverity.INFO.value
            }
        
        except Exception as e:
            return {
                "rule": "format_validation",
                "status": "error",
                "message": str(e),
                "severity": ValidationSeverity.CRITICAL.value
            }
    
    async def _validate_size(
        self,
        event_data: Dict[str, Any],
        event_type: str
    ) -> Dict[str, Any]:
        """Validate data size"""
        try:
            # Simulate size validation
            data_size = len(str(event_data))
            max_size = 1024 * 1024  # 1MB
            
            if data_size > max_size:
                return {
                    "rule": "size_validation",
                    "status": "error",
                    "message": f"Event data too large: {data_size} bytes",
                    "severity": ValidationSeverity.MEDIUM.value
                }
            
            return {
                "rule": "size_validation",
                "status": "success",
                "message": "Size validation passed",
                "severity": ValidationSeverity.INFO.value
            }
        
        except Exception as e:
            return {
                "rule": "size_validation",
                "status": "error",
                "message": str(e),
                "severity": ValidationSeverity.CRITICAL.value
            }
    
    async def _validate_timestamp(
        self,
        event_data: Dict[str, Any],
        event_type: str
    ) -> Dict[str, Any]:
        """Validate timestamp"""
        try:
            # Simulate timestamp validation
            if "timestamp" in event_data:
                timestamp = event_data["timestamp"]
                current_time = time.time()
                
                # Check if timestamp is in the future
                if timestamp > current_time + 300:  # 5 minutes tolerance
                    return {
                        "rule": "timestamp_validation",
                        "status": "warning",
                        "message": "Timestamp is in the future",
                        "severity": ValidationSeverity.LOW.value
                    }
                
                # Check if timestamp is too old (more than 1 year)
                if timestamp < current_time - 31536000:  # 1 year
                    return {
                        "rule": "timestamp_validation",
                        "status": "warning",
                        "message": "Timestamp is very old",
                        "severity": ValidationSeverity.LOW.value
                    }
            
            return {
                "rule": "timestamp_validation",
                "status": "success",
                "message": "Timestamp validation passed",
                "severity": ValidationSeverity.INFO.value
            }
        
        except Exception as e:
            return {
                "rule": "timestamp_validation",
                "status": "error",
                "message": str(e),
                "severity": ValidationSeverity.CRITICAL.value
            }
    
    async def _validate_field_type(self, value: Any, expected_type: str) -> bool:
        """Validate field type"""
        try:
            if expected_type == "string":
                return isinstance(value, str)
            elif expected_type == "number":
                return isinstance(value, (int, float))
            elif expected_type == "object":
                return isinstance(value, dict)
            elif expected_type == "array":
                return isinstance(value, list)
            elif expected_type == "boolean":
                return isinstance(value, bool)
            elif expected_type == "any":
                return True
            else:
                return True  # Unknown type, assume valid
        
        except Exception:
            return False
    
    async def _validate_field_value(self, value: Any, validation_type: str, validation_value: Any) -> bool:
        """Validate field value based on validation type"""
        try:
            if validation_type == "min_length":
                if isinstance(value, (str, list, dict)):
                    return len(value) >= validation_value
                return True
            elif validation_type == "max_length":
                if isinstance(value, (str, list, dict)):
                    return len(value) <= validation_value
                return True
            elif validation_type == "min_value":
                if isinstance(value, (int, float)):
                    return value >= validation_value
                return True
            elif validation_type == "max_value":
                if isinstance(value, (int, float)):
                    return value <= validation_value
                return True
            elif validation_type == "allowed_values":
                return value in validation_value
            elif validation_type == "required":
                return value is not None and value != ""
            else:
                return True  # Unknown validation type, assume valid
        
        except Exception:
            return False
    
    async def _has_circular_references(self, data: Any, visited: Optional[set] = None) -> bool:
        """Check for circular references in data"""
        if visited is None:
            visited = set()
        
        try:
            if id(data) in visited:
                return True
            
            visited.add(id(data))
            
            if isinstance(data, dict):
                for value in data.values():
                    if await self._has_circular_references(value, visited):
                        return True
            elif isinstance(data, list):
                for item in data:
                    if await self._has_circular_references(item, visited):
                        return True
            
            visited.remove(id(data))
            return False
        
        except Exception:
            return False
    
    async def _update_validation_stats(self, success: bool, validation_time: float):
        """Update validation statistics"""
        self.validation_stats["total_validations"] += 1
        
        if success:
            self.validation_stats["successful"] += 1
        else:
            self.validation_stats["failed"] += 1
        
        # Update average validation time
        total_successful = self.validation_stats["successful"]
        if total_successful > 0:
            current_avg = self.validation_stats["average_time"]
            self.validation_stats["average_time"] = (
                (current_avg * (total_successful - 1) + validation_time) / total_successful
            )
