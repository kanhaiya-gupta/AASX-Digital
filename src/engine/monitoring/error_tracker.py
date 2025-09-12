"""
Error Tracking and Reporting System

Comprehensive error tracking, categorization, and reporting for the AAS Data Modeling Engine.
Provides error aggregation, trend analysis, and integration with alerting and monitoring systems.
"""

import asyncio
import time
import json
import traceback
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
from collections import defaultdict, deque
import uuid


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification"""
    DATABASE = "database"
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    SYSTEM = "system"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    UNKNOWN = "unknown"


class ErrorStatus(Enum):
    """Error status tracking"""
    OPEN = "open"
    INVESTIGATING = "investigating"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    IGNORED = "ignored"


@dataclass
class ErrorContext:
    """Context information for an error"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    component: Optional[str] = None
    operation: Optional[str] = None
    environment: Optional[str] = None
    version: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorEvent:
    """Individual error event"""
    id: str
    timestamp: datetime
    error_type: str
    error_message: str
    error_details: str
    severity: ErrorSeverity
    category: ErrorCategory
    status: ErrorStatus = ErrorStatus.OPEN
    context: ErrorContext = field(default_factory=ErrorContext)
    stack_trace: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        # Handle both enum and string values
        data['severity'] = self.severity.value if hasattr(self.severity, 'value') else self.severity
        data['category'] = self.category.value if hasattr(self.category, 'value') else self.category
        data['status'] = self.status.value if hasattr(self.status, 'value') else self.status
        return data


@dataclass
class ErrorSummary:
    """Error summary statistics"""
    total_errors: int = 0
    errors_by_severity: Dict[str, int] = field(default_factory=dict)
    errors_by_category: Dict[str, int] = field(default_factory=dict)
    errors_by_status: Dict[str, int] = field(default_factory=dict)
    errors_by_hour: Dict[int, int] = field(default_factory=dict)
    errors_by_day: Dict[str, int] = field(default_factory=dict)
    recent_errors: List[ErrorEvent] = field(default_factory=list)
    error_trends: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)


class ErrorTracker:
    """Comprehensive error tracking and reporting system"""
    
    def __init__(self, config):
        """Initialize error tracker"""
        self.config = config
        self.errors: List[ErrorEvent] = []
        self.error_patterns: Dict[str, Dict[str, Any]] = {}
        self.error_rules: List[Dict[str, Any]] = []
        self.error_handlers: List[Callable[[ErrorEvent], None]] = []
        self.error_filters: List[Callable[[ErrorEvent], bool]] = []
        
        # Error storage and limits
        self.max_errors = getattr(config, 'max_errors', 10000)
        self.error_retention_days = getattr(config, 'error_retention_days', 30)
        self.error_aggregation_window = getattr(config, 'error_aggregation_window', 3600)  # 1 hour
        
        # Error patterns for automatic categorization
        self._setup_default_patterns()
        self._setup_default_rules()
    
    def _setup_default_patterns(self):
        """Setup default error patterns for automatic categorization"""
        self.error_patterns = {
            "database": {
                "patterns": [
                    "connection refused", "timeout", "deadlock", "constraint violation",
                    "table not found", "column not found", "syntax error"
                ],
                "category": ErrorCategory.DATABASE,
                "severity": ErrorSeverity.HIGH
            },
            "network": {
                "patterns": [
                    "connection timeout", "network unreachable", "dns resolution failed",
                    "connection reset", "connection refused"
                ],
                "category": ErrorCategory.NETWORK,
                "severity": ErrorSeverity.MEDIUM
            },
            "authentication": {
                "patterns": [
                    "invalid credentials", "authentication failed", "token expired",
                    "unauthorized access", "permission denied"
                ],
                "category": ErrorCategory.AUTHENTICATION,
                "severity": ErrorSeverity.HIGH
            },
            "validation": {
                "patterns": [
                    "invalid input", "validation failed", "required field missing",
                    "format error", "type error"
                ],
                "category": ErrorCategory.VALIDATION,
                "severity": ErrorSeverity.LOW
            }
        }
    
    def _setup_default_rules(self):
        """Setup default error handling rules"""
        self.error_rules = [
            {
                "name": "critical_errors_alert",
                "condition": lambda error: error.severity == ErrorSeverity.CRITICAL,
                "action": "alert",
                "enabled": True
            },
            {
                "name": "database_errors_retry",
                "condition": lambda error: error.category == ErrorCategory.DATABASE,
                "action": "retry",
                "enabled": True
            },
            {
                "name": "rate_limit_errors",
                "condition": lambda error: "rate limit" in error.error_message.lower(),
                "action": "throttle",
                "enabled": True
            }
        ]
    
    async def track_error(self, error_type: str, error_message: str, error_details: str = "",
                   severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                   category: Optional[ErrorCategory] = None,
                   context: Optional[ErrorContext] = None,
                   stack_trace: Optional[str] = None,
                   tags: Optional[List[str]] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Track a new error event"""
        
        # Auto-categorize if not provided
        if category is None:
            category = self._auto_categorize_error(error_message)
        
        # Auto-adjust severity if needed
        if severity == ErrorSeverity.MEDIUM:
            severity = self._auto_adjust_severity(error_message, category)
        
        # Create error event
        error_event = ErrorEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            error_type=error_type,
            error_message=error_message,
            error_details=error_details,
            severity=severity,
            category=category,
            context=context or ErrorContext(),
            stack_trace=stack_trace,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        # Apply filters
        if not self._should_track_error(error_event):
            return ""
        
        # Add to errors list
        self.errors.append(error_event)
        
        # Enforce storage limits
        self._enforce_storage_limits()
        
        # Process error rules
        self._process_error_rules(error_event)
        
        # Call error handlers
        self._call_error_handlers(error_event)
        
        return error_event.id
    
    def _auto_categorize_error(self, error_message: str) -> ErrorCategory:
        """Automatically categorize error based on message patterns"""
        error_lower = error_message.lower()
        
        for pattern_name, pattern_info in self.error_patterns.items():
            for pattern in pattern_info["patterns"]:
                if pattern in error_lower:
                    return pattern_info["category"]
        
        return ErrorCategory.UNKNOWN
    
    def _auto_adjust_severity(self, error_message: str, category: ErrorCategory) -> ErrorSeverity:
        """Automatically adjust error severity based on context"""
        error_lower = error_message.lower()
        
        # Critical keywords
        if any(keyword in error_lower for keyword in ["fatal", "critical", "emergency", "panic"]):
            return ErrorSeverity.CRITICAL
        
        # High severity patterns
        if any(keyword in error_lower for keyword in ["timeout", "connection failed", "authentication failed"]):
            return ErrorSeverity.HIGH
        
        # Category-based severity
        if category in [ErrorCategory.AUTHENTICATION, ErrorCategory.AUTHORIZATION]:
            return ErrorSeverity.HIGH
        
        return ErrorSeverity.MEDIUM
    
    def _should_track_error(self, error_event: ErrorEvent) -> bool:
        """Check if error should be tracked based on filters"""
        for error_filter in self.error_filters:
            if not error_filter(error_event):
                return False
        return True
    
    def _enforce_storage_limits(self):
        """Enforce storage limits and retention policies"""
        current_time = datetime.utcnow()
        cutoff_time = current_time - timedelta(days=self.error_retention_days)
        
        # Remove old errors
        self.errors = [e for e in self.errors if e.timestamp > cutoff_time]
        
        # Enforce max errors limit
        if len(self.errors) > self.max_errors:
            # Remove oldest errors first
            self.errors.sort(key=lambda x: x.timestamp)
            self.errors = self.errors[-self.max_errors:]
    
    def _process_error_rules(self, error_event: ErrorEvent):
        """Process error handling rules"""
        for rule in self.error_rules:
            if rule.get("enabled", True) and rule["condition"](error_event):
                self._execute_rule_action(rule, error_event)
    
    def _execute_rule_action(self, rule: Dict[str, Any], error_event: ErrorEvent):
        """Execute rule action"""
        action = rule.get("action")
        if action == "alert":
            # Trigger alert (would integrate with AlertManager)
            pass
        elif action == "retry":
            # Mark for retry
            pass
        elif action == "throttle":
            # Apply throttling
            pass
    
    def _call_error_handlers(self, error_event: ErrorEvent):
        """Call registered error handlers"""
        for handler in self.error_handlers:
            try:
                handler(error_event)
            except Exception as e:
                # Don't let handler errors break error tracking
                pass
    
    def add_error_handler(self, handler: Callable[[ErrorEvent], None]):
        """Add custom error handler"""
        self.error_handlers.append(handler)
    
    def add_error_filter(self, error_filter: Callable[[ErrorEvent], bool]):
        """Add custom error filter"""
        self.error_filters.append(error_filter)
    
    def get_error(self, error_id: str) -> Optional[ErrorEvent]:
        """Get error by ID"""
        for error in self.errors:
            if error.id == error_id:
                return error
        return None
    
    def get_errors(self, 
                   severity: Optional[ErrorSeverity] = None,
                   category: Optional[ErrorCategory] = None,
                   status: Optional[ErrorStatus] = None,
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   limit: Optional[int] = None) -> List[ErrorEvent]:
        """Get filtered errors"""
        filtered_errors = self.errors
        
        if severity:
            filtered_errors = [e for e in filtered_errors if e.severity == severity]
        
        if category:
            filtered_errors = [e for e in filtered_errors if e.category == category]
        
        if status:
            filtered_errors = [e for e in filtered_errors if e.status == status]
        
        if start_time:
            filtered_errors = [e for e in filtered_errors if e.timestamp >= start_time]
        
        if end_time:
            filtered_errors = [e for e in filtered_errors if e.timestamp <= end_time]
        
        # Sort by timestamp (newest first)
        filtered_errors.sort(key=lambda x: x.timestamp, reverse=True)
        
        if limit:
            filtered_errors = filtered_errors[:limit]
        
        return filtered_errors
    
    def update_error_status(self, error_id: str, status: ErrorStatus, 
                           updated_by: Optional[str] = None, 
                           notes: Optional[str] = None):
        """Update error status"""
        error = self.get_error(error_id)
        if error:
            error.status = status
            if notes:
                error.metadata["status_notes"] = notes
            if updated_by:
                error.metadata["updated_by"] = updated_by
    
    def get_error_summary(self, window_hours: int = 24) -> ErrorSummary:
        """Get error summary for specified time window"""
        current_time = datetime.utcnow()
        start_time = current_time - timedelta(hours=window_hours)
        
        window_errors = [e for e in self.errors if e.timestamp >= start_time]
        
        summary = ErrorSummary()
        summary.total_errors = len(window_errors)
        
        # Count by severity
        for error in window_errors:
            severity_key = error.severity.value if hasattr(error.severity, 'value') else error.severity
            summary.errors_by_severity[severity_key] = summary.errors_by_severity.get(severity_key, 0) + 1
        
        # Count by category
        for error in window_errors:
            category_key = error.category.value if hasattr(error.category, 'value') else error.category
            summary.errors_by_category[category_key] = summary.errors_by_category.get(category_key, 0) + 1
        
        # Count by status
        for error in window_errors:
            status_key = error.status.value if hasattr(error.status, 'value') else error.status
            summary.errors_by_status[status_key] = summary.errors_by_status.get(status_key, 0) + 1
        
        # Count by hour
        for error in window_errors:
            hour = error.timestamp.hour
            summary.errors_by_hour[hour] = summary.errors_by_hour.get(hour, 0) + 1
        
        # Count by day
        for error in window_errors:
            day = error.timestamp.strftime("%Y-%m-%d")
            summary.errors_by_day[day] = summary.errors_by_day.get(day, 0) + 1
        
        # Recent errors
        summary.recent_errors = sorted(window_errors, key=lambda x: x.timestamp, reverse=True)[:10]
        
        # Error trends (hourly for last 24 hours)
        for i in range(24):
            hour = (current_time - timedelta(hours=i)).hour
            count = summary.errors_by_hour.get(hour, 0)
            summary.error_trends["hourly"] = summary.error_trends.get("hourly", [])
            summary.error_trends["hourly"].append({
                "hour": hour,
                "count": count,
                "timestamp": (current_time - timedelta(hours=i)).isoformat()
            })
        
        return summary
    
    async def initialize(self):
        """Initialize the error tracker"""
        try:
            # Setup default patterns and rules
            self._setup_default_patterns()
            self._setup_default_rules()
            
            # Initialize error storage
            self.errors = []
            self.error_patterns = {}
            self.error_rules = []
            
            print("Error tracker initialized successfully")
        except Exception as e:
            print(f"Failed to initialize error tracker: {e}")
            raise

    async def get_health(self) -> Dict[str, Any]:
        """Get health status of the error tracker"""
        try:
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "total_errors": len(self.errors),
                "error_patterns_count": len(self.error_patterns),
                "error_rules_count": len(self.error_rules),
                "message": "Error tracker is operational"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "message": "Error tracker has errors"
            }
    
    async def cleanup(self):
        """Cleanup error tracker resources"""
        try:
            # Clear errors
            self.errors.clear()
            self.error_patterns.clear()
            self.error_rules.clear()
            self.error_handlers.clear()
            self.error_filters.clear()
            
            print("Error tracker cleaned up successfully")
        except Exception as e:
            print(f"Failed to cleanup error tracker: {e}")
            raise

    def get_error_patterns(self) -> Dict[str, Any]:
        """Get error pattern analysis"""
        patterns = {}
        
        # Group errors by type
        error_types = defaultdict(list)
        for error in self.errors:
            error_types[error.error_type].append(error)
        
        # Analyze patterns for each error type
        for error_type, errors in error_types.items():
            if len(errors) < 2:  # Skip single occurrences
                continue
            
            patterns[error_type] = {
                "count": len(errors),
                "first_occurrence": min(e.timestamp for e in errors).isoformat(),
                "last_occurrence": max(e.timestamp for e in errors).isoformat(),
                "severity_distribution": defaultdict(int),
                "category_distribution": defaultdict(int),
                "common_contexts": defaultdict(int)
            }
            
            for error in errors:
                severity_key = error.severity.value if hasattr(error.severity, 'value') else error.severity
                category_key = error.category.value if hasattr(error.category, 'value') else error.category
                patterns[error_type]["severity_distribution"][severity_key] += 1
                patterns[error_type]["category_distribution"][category_key] += 1
                
                if error.context.component:
                    patterns[error_type]["common_contexts"][error.context.component] += 1
        
        return patterns
    
    def export_errors(self, format: str = "json", filepath: Optional[Path] = None) -> Path:
        """Export errors to file"""
        if filepath is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"errors_export_{timestamp}.{format}"
            filepath = self.config.export.export_directory / filename
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == "json":
            with open(filepath, 'w') as f:
                json.dump([error.to_dict() for error in self.errors], f, indent=2)
        elif format.lower() == "csv":
            import csv
            with open(filepath, 'w', newline='') as f:
                if self.errors:
                    writer = csv.DictWriter(f, fieldnames=self.errors[0].to_dict().keys())
                    writer.writeheader()
                    for error in self.errors:
                        writer.writerow(error.to_dict())
        
        return filepath
    
    def clear_errors(self, before_date: Optional[datetime] = None):
        """Clear errors, optionally before a specific date"""
        if before_date:
            self.errors = [e for e in self.errors if e.timestamp >= before_date]
        else:
            self.errors.clear()
    
    def get_error_metrics(self) -> Dict[str, Any]:
        """Get error metrics for monitoring"""
        current_time = datetime.utcnow()
        last_hour = current_time - timedelta(hours=1)
        last_24_hours = current_time - timedelta(hours=24)
        
        recent_errors = [e for e in self.errors if e.timestamp >= last_hour]
        daily_errors = [e for e in self.errors if e.timestamp >= last_24_hours]
        
        return {
            "errors_last_hour": len(recent_errors),
            "errors_last_24_hours": len(daily_errors),
            "total_errors": len(self.errors),
            "errors_by_severity": {s.value: len([e for e in self.errors if e.severity == s]) 
                                 for s in ErrorSeverity},
            "errors_by_category": {c.value: len([e for e in self.errors if e.category == c]) 
                                 for c in ErrorCategory},
            "open_errors": len([e for e in self.errors if e.status == ErrorStatus.OPEN]),
            "critical_errors": len([e for e in self.errors if e.severity == ErrorSeverity.CRITICAL])
        }
