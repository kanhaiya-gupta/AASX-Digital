"""
Custom exception hierarchy for the engine system.

This module provides a comprehensive set of custom exceptions that follow
best practices for error handling and provide meaningful error information.
"""

from typing import Any, Dict, List, Optional, Union
import traceback


class EngineException(Exception):
    """Base exception for all engine-related errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None, 
                 original_exception: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.original_exception = original_exception
        self.timestamp = self._get_timestamp()
        self.traceback = self._get_traceback()
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for the exception."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _get_traceback(self) -> str:
        """Get current traceback for the exception."""
        return traceback.format_exc()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary format."""
        return {
            "exception_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
            "timestamp": self.timestamp,
            "traceback": self.traceback
        }
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message='{self.message}', error_code='{self.error_code}')"


class DatabaseException(EngineException):
    """Exception raised for database-related errors."""
    
    def __init__(self, message: str, operation: Optional[str] = None, 
                 table: Optional[str] = None, query: Optional[str] = None,
                 **kwargs):
        super().__init__(message, **kwargs)
        self.operation = operation
        self.table = table
        self.query = query
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary format."""
        base_dict = super().to_dict()
        base_dict.update({
            "operation": self.operation,
            "table": self.table,
            "query": self.query
        })
        return base_dict


class ConnectionException(DatabaseException):
    """Exception raised for database connection errors."""
    
    def __init__(self, message: str, connection_string: Optional[str] = None,
                 retry_count: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.connection_string = connection_string
        self.retry_count = retry_count


class QueryException(DatabaseException):
    """Exception raised for query execution errors."""
    
    def __init__(self, message: str, sql: Optional[str] = None,
                 parameters: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.sql = sql
        self.parameters = parameters


class TransactionException(DatabaseException):
    """Exception raised for transaction-related errors."""
    
    def __init__(self, message: str, transaction_id: Optional[str] = None,
                 rollback_successful: Optional[bool] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.transaction_id = transaction_id
        self.rollback_successful = rollback_successful


class ValidationException(EngineException):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None,
                 value: Optional[Any] = None, validation_rules: Optional[List[str]] = None,
                 **kwargs):
        super().__init__(message, **kwargs)
        self.field = field
        self.value = value
        self.validation_rules = validation_rules or []
    
    def add_validation_error(self, field: str, message: str, value: Any = None):
        """Add a validation error for a specific field."""
        if "validation_errors" not in self.details:
            self.details["validation_errors"] = []
        
        self.details["validation_errors"].append({
            "field": field,
            "message": message,
            "value": value
        })
    
    def get_validation_errors(self) -> List[Dict[str, Any]]:
        """Get all validation errors."""
        return self.details.get("validation_errors", [])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary format."""
        base_dict = super().to_dict()
        base_dict.update({
            "field": self.field,
            "value": self.value,
            "validation_rules": self.validation_rules
        })
        return base_dict


class AuthenticationException(EngineException):
    """Exception raised for authentication errors."""
    
    def __init__(self, message: str, user_id: Optional[str] = None,
                 authentication_method: Optional[str] = None, 
                 ip_address: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.user_id = user_id
        self.authentication_method = authentication_method
        self.ip_address = ip_address


class AuthorizationException(EngineException):
    """Exception raised for authorization errors."""
    
    def __init__(self, message: str, user_id: Optional[str] = None,
                 required_permissions: Optional[List[str]] = None,
                 resource: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.user_id = user_id
        self.required_permissions = required_permissions or []
        self.resource = resource


class ConfigurationException(EngineException):
    """Exception raised for configuration errors."""
    
    def __init__(self, message: str, config_key: Optional[str] = None,
                 config_file: Optional[str] = None, 
                 environment_variable: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.config_key = config_key
        self.config_file = config_file
        self.environment_variable = environment_variable


class ServiceException(EngineException):
    """Exception raised for service layer errors."""
    
    def __init__(self, message: str, service_name: Optional[str] = None,
                 operation: Optional[str] = None, retry_count: Optional[int] = None,
                 **kwargs):
        super().__init__(message, **kwargs)
        self.service_name = service_name
        self.operation = operation
        self.retry_count = retry_count


class RepositoryException(EngineException):
    """Exception raised for repository layer errors."""
    
    def __init__(self, message: str, repository_name: Optional[str] = None,
                 entity_type: Optional[str] = None, operation: Optional[str] = None,
                 **kwargs):
        super().__init__(message, **kwargs)
        self.repository_name = repository_name
        self.entity_type = entity_type
        self.operation = operation


class CacheException(EngineException):
    """Exception raised for cache-related errors."""
    
    def __init__(self, message: str, cache_key: Optional[str] = None,
                 cache_type: Optional[str] = None, operation: Optional[str] = None,
                 **kwargs):
        super().__init__(message, **kwargs)
        self.cache_key = cache_key
        self.cache_type = cache_type
        self.operation = operation


class EventException(EngineException):
    """Exception raised for event-related errors."""
    
    def __init__(self, message: str, event_name: Optional[str] = None,
                 event_data: Optional[Any] = None, handler_name: Optional[str] = None,
                 **kwargs):
        super().__init__(message, **kwargs)
        self.event_name = event_name
        self.event_data = event_data
        self.handler_name = handler_name


class TaskException(EngineException):
    """Exception raised for task-related errors."""
    
    def __init__(self, message: str, task_id: Optional[str] = None,
                 task_type: Optional[str] = None, worker_id: Optional[str] = None,
                 **kwargs):
        super().__init__(message, **kwargs)
        self.task_id = task_id
        self.task_type = task_type
        self.worker_id = worker_id


class TimeoutException(EngineException):
    """Exception raised for timeout errors."""
    
    def __init__(self, message: str, timeout_duration: Optional[float] = None,
                 operation: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.timeout_duration = timeout_duration
        self.operation = operation


class RetryException(EngineException):
    """Exception raised when retry attempts are exhausted."""
    
    def __init__(self, message: str, max_retries: Optional[int] = None,
                 retry_count: Optional[int] = None, last_exception: Optional[Exception] = None,
                 **kwargs):
        super().__init__(message, **kwargs)
        self.max_retries = max_retries
        self.retry_count = retry_count
        self.last_exception = last_exception


class ResourceNotFoundException(EngineException):
    """Exception raised when a requested resource is not found."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None,
                 resource_id: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.resource_type = resource_type
        self.resource_id = resource_id


class ResourceAlreadyExistsException(EngineException):
    """Exception raised when trying to create a resource that already exists."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None,
                 resource_id: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.resource_type = resource_type
        self.resource_id = resource_id


class CircularDependencyException(EngineException):
    """Exception raised when circular dependencies are detected."""
    
    def __init__(self, message: str, dependency_chain: Optional[List[str]] = None,
                 **kwargs):
        super().__init__(message, **kwargs)
        self.dependency_chain = dependency_chain or []


class StateException(EngineException):
    """Exception raised for invalid state transitions."""
    
    def __init__(self, message: str, current_state: Optional[str] = None,
                 expected_state: Optional[str] = None, 
                 allowed_transitions: Optional[List[str]] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.current_state = current_state
        self.expected_state = expected_state
        self.allowed_transitions = allowed_transitions or []
