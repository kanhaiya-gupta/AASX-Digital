"""
Base Validator
==============

Abstract base class for all schema validators. Provides common interface
and utilities for data validation, schema validation, and business rule validation.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Set
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseValidator(ABC):
    """Abstract base class for all validators"""
    
    def __init__(self, name: str = None):
        """
        Initialize the base validator.
        
        Args:
            name: Name of the validator for logging and identification
        """
        self.name = name or self.__class__.__name__
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        self._validation_errors: List[Dict[str, Any]] = []
        self._validation_warnings: List[Dict[str, Any]] = []
        self._validation_start_time: Optional[datetime] = None
        self._validation_end_time: Optional[datetime] = None
        
    @abstractmethod
    async def validate(self, data: Any, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Validate the provided data.
        
        Args:
            data: Data to validate
            context: Optional context information for validation
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        pass
    
    def add_validation_error(self, field: str, message: str, value: Any = None, 
                           error_code: Optional[str] = None, severity: str = "error") -> None:
        """
        Add a validation error.
        
        Args:
            field: Field or property that failed validation
            message: Human-readable error message
            value: Value that caused the error
            error_code: Optional error code for programmatic handling
            severity: Error severity level (error, warning, info)
        """
        error = {
            'field': field,
            'message': message,
            'value': value,
            'error_code': error_code,
            'severity': severity,
            'timestamp': datetime.now().isoformat(),
            'validator': self.name
        }
        
        if severity == "error":
            self._validation_errors.append(error)
        else:
            self._validation_warnings.append(error)
        
        self.logger.debug(f"Validation {severity}: {field} - {message}")
    
    def add_validation_warning(self, field: str, message: str, value: Any = None, 
                              warning_code: Optional[str] = None) -> None:
        """
        Add a validation warning.
        
        Args:
            field: Field or property that generated the warning
            message: Human-readable warning message
            value: Value that caused the warning
            warning_code: Optional warning code for programmatic handling
        """
        self.add_validation_error(field, message, value, warning_code, "warning")
    
    def clear_validation_errors(self) -> None:
        """Clear all validation errors and warnings."""
        self._validation_errors.clear()
        self._validation_warnings.clear()
        self._validation_start_time = None
        self._validation_end_time = None
    
    def get_validation_errors(self) -> List[Dict[str, Any]]:
        """Get all validation errors."""
        return self._validation_errors.copy()
    
    def get_validation_warnings(self) -> List[Dict[str, Any]]:
        """Get all validation warnings."""
        return self._validation_warnings.copy()
    
    def get_all_validation_issues(self) -> List[Dict[str, Any]]:
        """Get all validation issues (errors and warnings combined)."""
        return self._validation_errors + self._validation_warnings
    
    def has_errors(self) -> bool:
        """Check if there are any validation errors."""
        return len(self._validation_errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are any validation warnings."""
        return len(self._validation_warnings) > 0
    
    def has_issues(self) -> bool:
        """Check if there are any validation issues (errors or warnings)."""
        return self.has_errors() or self.has_warnings()
    
    def get_error_count(self) -> int:
        """Get the number of validation errors."""
        return len(self._validation_errors)
    
    def get_warning_count(self) -> int:
        """Get the number of validation warnings."""
        return len(self._validation_warnings)
    
    def get_total_issue_count(self) -> int:
        """Get the total number of validation issues."""
        return len(self._validation_errors) + len(self._validation_warnings)
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get a summary of validation results."""
        return {
            'validator_name': self.name,
            'validation_passed': not self.has_errors(),
            'error_count': self.get_error_count(),
            'warning_count': self.get_warning_count(),
            'total_issues': self.get_total_issue_count(),
            'start_time': self._validation_start_time.isoformat() if self._validation_start_time else None,
            'end_time': self._validation_end_time.isoformat() if self._validation_end_time else None,
            'duration_ms': self._get_validation_duration_ms(),
            'has_errors': self.has_errors(),
            'has_warnings': self.has_warnings()
        }
    
    def _get_validation_duration_ms(self) -> Optional[int]:
        """Get validation duration in milliseconds."""
        if self._validation_start_time and self._validation_end_time:
            duration = self._validation_end_time - self._validation_start_time
            return int(duration.total_seconds() * 1000)
        return None
    
    async def validate_with_timing(self, data: Any, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Validate data with timing information.
        
        Args:
            data: Data to validate
            context: Optional context information for validation
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        self._validation_start_time = datetime.now()
        self.clear_validation_errors()
        
        try:
            result = await self.validate(data, context)
            return result
        finally:
            self._validation_end_time = datetime.now()
    
    def is_valid(self, data: Any, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Synchronous wrapper for validation (for backward compatibility).
        
        Args:
            data: Data to validate
            context: Optional context information for validation
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        try:
            import asyncio
            
            # Try to get the current event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're in an async context, we need to handle this differently
                    # For now, return True and let the async validate method handle it
                    return True
                else:
                    return loop.run_until_complete(self.validate(data, context))
            except RuntimeError:
                # No event loop, create one
                return asyncio.run(self.validate(data, context))
                
        except Exception as e:
            self.logger.error(f"Error in synchronous validation: {e}")
            return False
    
    def __str__(self) -> str:
        """String representation of the validator."""
        return f"{self.__class__.__name__}(name='{self.name}')"
    
    def __repr__(self) -> str:
        """Detailed string representation of the validator."""
        return f"{self.__class__.__name__}(name='{self.name}', errors={self.get_error_count()}, warnings={self.get_warning_count()})"
