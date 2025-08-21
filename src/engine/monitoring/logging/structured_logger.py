"""
Structured Logger

Structured logging system that provides consistent, context-aware logging
with metadata, correlation IDs, and structured output for the monitoring system.
"""

import logging
import json
import time
import uuid
import copy
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field, asdict
from contextlib import contextmanager
import threading
import sys


@dataclass
class LogContext:
    """Context information for structured logging"""
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    component: Optional[str] = None
    operation: Optional[str] = None
    environment: Optional[str] = None
    version: Optional[str] = None
    correlation_id: Optional[str] = None
    parent_request_id: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: str
    level: str
    logger: str
    message: str
    context: LogContext
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    duration_ms: Optional[float] = None
    error_details: Optional[Dict[str, Any]] = None


class StructuredLogger:
    """Structured logger with context and metadata support"""
    
    def __init__(self, name: str, log_manager=None, default_context: Optional[LogContext] = None):
        """Initialize structured logger"""
        self.name = name
        self.log_manager = log_manager
        self.default_context = default_context or LogContext()
        
        # Get underlying logger
        if log_manager:
            self.logger = log_manager.get_logger(name)
        else:
            self.logger = logging.getLogger(name)
        
        # Thread-local storage for context
        self._local = threading.local()
        self._local.context = copy.deepcopy(self.default_context)
        
        # Performance tracking
        self._operation_start_times = {}
    
    def _get_current_context(self) -> LogContext:
        """Get current thread-local context"""
        if not hasattr(self._local, 'context'):
            self._local.context = copy.deepcopy(self.default_context)
        return self._local.context
    
    def _set_context_field(self, field_name: str, value: Any):
        """Set a context field"""
        context = self._get_current_context()
        setattr(context, field_name, value)
    
    def _get_context_dict(self) -> Dict[str, Any]:
        """Get context as dictionary"""
        context = self._get_current_context()
        return asdict(context)
    
    def set_request_id(self, request_id: str):
        """Set request ID for current context"""
        self._set_context_field('request_id', request_id)
    
    def set_user_id(self, user_id: str):
        """Set user ID for current context"""
        self._set_context_field('user_id', user_id)
    
    def set_session_id(self, session_id: str):
        """Set session ID for current context"""
        self._set_context_field('session_id', session_id)
    
    def set_component(self, component: str):
        """Set component for current context"""
        self._set_context_field('component', component)
    
    def set_operation(self, operation: str):
        """Set operation for current context"""
        self._set_context_field('operation', operation)
    
    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for current context"""
        self._set_context_field('correlation_id', correlation_id)
    
    def set_parent_request_id(self, parent_request_id: str):
        """Set parent request ID for current context"""
        self._set_context_field('parent_request_id', parent_request_id)
    
    def add_context_data(self, key: str, value: Any):
        """Add additional context data"""
        context = self._get_current_context()
        context.additional_data[key] = value
    
    def add_tag(self, tag: str):
        """Add a tag to the current context"""
        context = self._get_current_context()
        if tag not in context.additional_data.get('tags', []):
            if 'tags' not in context.additional_data:
                context.additional_data['tags'] = []
            context.additional_data['tags'].append(tag)
    
    def _create_log_entry(self, level: str, message: str, **kwargs) -> LogEntry:
        """Create a structured log entry"""
        context = self._get_current_context()
        
        # Extract tags from context
        tags = context.additional_data.get('tags', [])
        
        # Create log entry
        entry = LogEntry(
            timestamp=datetime.utcnow().isoformat(),
            level=level.upper(),
            logger=self.name,
            message=message,
            context=context,
            metadata=kwargs,
            tags=tags
        )
        
        return entry
    
    def _log_structured(self, level: str, message: str, **kwargs):
        """Log with structured format"""
        try:
            entry = self._create_log_entry(level, message, **kwargs)
            
            # Convert to JSON for structured logging
            log_data = asdict(entry)
            log_message = json.dumps(log_data, default=str)
            
            # Log using underlying logger
            if level.upper() == "DEBUG":
                self.logger.debug(log_message)
            elif level.upper() == "INFO":
                self.logger.info(log_message)
            elif level.upper() == "WARNING":
                self.logger.warning(log_message)
            elif level.upper() == "ERROR":
                self.logger.error(log_message)
            elif level.upper() == "CRITICAL":
                self.logger.critical(log_message)
            else:
                self.logger.info(log_message)
                
        except Exception as e:
            # Fallback to basic logging if structured logging fails
            self.logger.error(f"Structured logging failed: {e}. Original message: {message}")
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log_structured("DEBUG", message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log_structured("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log_structured("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self._log_structured("ERROR", message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self._log_structured("CRITICAL", message, **kwargs)
    
    def exception(self, message: str, exc_info=True, **kwargs):
        """Log exception with traceback"""
        import traceback
        
        # Get exception details
        exc_type, exc_value, exc_traceback = sys.exc_info()
        
        error_details = {
            "exception_type": exc_type.__name__ if exc_type else None,
            "exception_message": str(exc_value) if exc_value else None,
            "traceback": traceback.format_exc() if exc_traceback else None
        }
        
        kwargs['error_details'] = error_details
        self._log_structured("ERROR", message, **kwargs)
    
    def start_operation(self, operation_name: str, **kwargs) -> str:
        """Start timing an operation"""
        operation_id = str(uuid.uuid4())
        start_time = time.time()
        
        self._operation_start_times[operation_id] = start_time
        
        # Set operation context
        self.set_operation(operation_name)
        
        # Log operation start
        self.info(f"Operation started: {operation_name}", 
                 operation_id=operation_id, 
                 operation_status="started", **kwargs)
        
        return operation_id
    
    def end_operation(self, operation_id: str, status: str = "completed", **kwargs):
        """End timing an operation"""
        if operation_id in self._operation_start_times:
            start_time = self._operation_start_times.pop(operation_id)
            duration_ms = (time.time() - start_time) * 1000
            
            # Log operation end
            self.info(f"Operation ended: {kwargs.get('operation_name', 'unknown')}", 
                     operation_id=operation_id,
                     operation_status=status,
                     duration_ms=round(duration_ms, 2), **kwargs)
    
    @contextmanager
    def operation_context(self, operation_name: str, **kwargs):
        """Context manager for operation timing"""
        operation_id = self.start_operation(operation_name, **kwargs)
        try:
            yield operation_id
            self.end_operation(operation_id, "completed", operation_name=operation_name, **kwargs)
        except Exception as e:
            self.end_operation(operation_id, "failed", 
                             operation_name=operation_name, 
                             error=str(e), **kwargs)
            raise
    
    def log_metric(self, metric_name: str, value: Union[int, float], 
                   unit: str = "count", **kwargs):
        """Log a metric value"""
        self.info(f"Metric: {metric_name}", 
                 metric_name=metric_name,
                 metric_value=value,
                 metric_unit=unit,
                 log_type="metric", **kwargs)
    
    def log_event(self, event_type: str, event_data: Dict[str, Any], **kwargs):
        """Log an event with structured data"""
        self.info(f"Event: {event_type}", 
                 event_type=event_type,
                 event_data=event_data,
                 log_type="event", **kwargs)
    
    def log_audit(self, action: str, resource: str, user_id: Optional[str] = None, 
                  success: bool = True, **kwargs):
        """Log an audit event"""
        self.info(f"Audit: {action} on {resource}", 
                 audit_action=action,
                 audit_resource=resource,
                 audit_user_id=user_id,
                 audit_success=success,
                 log_type="audit", **kwargs)
    
    def log_security(self, event_type: str, user_id: Optional[str] = None, 
                     ip_address: Optional[str] = None, **kwargs):
        """Log a security event"""
        self.warning(f"Security event: {event_type}", 
                     security_event_type=event_type,
                     security_user_id=user_id,
                     security_ip_address=ip_address,
                     log_type="security", **kwargs)
    
    def log_performance(self, operation: str, duration_ms: float, 
                       success: bool = True, **kwargs):
        """Log a performance measurement"""
        level = "WARNING" if duration_ms > 1000 else "INFO"  # Warn if > 1 second
        
        self._log_structured(level, f"Performance: {operation}", 
                           performance_operation=operation,
                           performance_duration_ms=round(duration_ms, 2),
                           performance_success=success,
                           log_type="performance", **kwargs)
    
    def log_dependency(self, dependency_name: str, status: str, 
                      response_time_ms: Optional[float] = None, **kwargs):
        """Log a dependency status"""
        self.info(f"Dependency: {dependency_name} - {status}", 
                 dependency_name=dependency_name,
                 dependency_status=status,
                 dependency_response_time_ms=response_time_ms,
                 log_type="dependency", **kwargs)
    
    def log_business(self, business_event: str, business_data: Dict[str, Any], **kwargs):
        """Log a business event"""
        self.info(f"Business event: {business_event}", 
                 business_event=business_event,
                 business_data=business_data,
                 log_type="business", **kwargs)
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get current context summary"""
        context = self._get_current_context()
        return {
            "logger_name": self.name,
            "context": asdict(context),
            "active_operations": list(self._operation_start_times.keys())
        }
    
    def clear_context(self):
        """Clear current context"""
        self._local.context = copy.deepcopy(self.default_context)
        self._operation_start_times.clear()
    
    def create_child_logger(self, name: str, inherit_context: bool = True) -> 'StructuredLogger':
        """Create a child logger that inherits context"""
        child_name = f"{self.name}.{name}"
        child_logger = StructuredLogger(child_name, self.log_manager)
        
        if inherit_context:
            child_logger._local.context = self._get_current_context()
        
        return child_logger


# Convenience functions for quick logging
def get_logger(name: str, log_manager=None) -> StructuredLogger:
    """Get a structured logger"""
    return StructuredLogger(name, log_manager)


def log_function_call(logger: StructuredLogger, func_name: str = None):
    """Decorator to log function calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            operation_name = func_name or func.__name__
            
            with logger.operation_context(operation_name, 
                                       function_name=func.__name__,
                                       args_count=len(args),
                                       kwargs_count=len(kwargs)):
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    logger.exception(f"Function {func.__name__} failed")
                    raise
        
        return wrapper
    return decorator


def log_class_methods(logger: StructuredLogger):
    """Decorator to log all method calls in a class"""
    def decorator(cls):
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if callable(attr) and not attr_name.startswith('_'):
                setattr(cls, attr_name, log_function_call(logger, attr_name)(attr))
        return cls
    return decorator
