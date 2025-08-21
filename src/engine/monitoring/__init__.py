"""
Monitoring and Observability System

This module provides comprehensive monitoring, metrics collection, health checks,
error tracking, logging, and observability capabilities for the AAS Data Modeling Engine.

Features:
- Real-time metrics collection and aggregation
- Health monitoring and alerting
- Performance profiling and tracing
- Error tracking and categorization
- Advanced logging with multiple formats
- Resource usage monitoring
- Custom metric definitions
- Export and visualization support
"""

from .metrics_collector import MetricsCollector
from .health_monitor import HealthMonitor
from .performance_profiler import PerformanceProfiler
from .resource_monitor import ResourceMonitor
from .alert_manager import AlertManager
from .monitoring_middleware import MonitoringMiddleware
from .monitoring_config import MonitoringConfig
from .error_tracker import ErrorTracker, ErrorSeverity, ErrorCategory, ErrorStatus, ErrorContext, ErrorEvent, ErrorSummary
from .logging import LogManager, StructuredLogger, JSONFormatter, CSVFormatter, PlainTextFormatter, LogstashFormatter, CustomFormatter

__all__ = [
    'MetricsCollector',
    'HealthMonitor', 
    'PerformanceProfiler',
    'ResourceMonitor',
    'AlertManager',
    'MonitoringMiddleware',
    'MonitoringConfig',
    'ErrorTracker',
    'ErrorSeverity',
    'ErrorCategory', 
    'ErrorStatus',
    'ErrorContext',
    'ErrorEvent',
    'ErrorSummary',
    'LogManager',
    'StructuredLogger',
    'JSONFormatter',
    'CSVFormatter',
    'PlainTextFormatter',
    'LogstashFormatter',
    'CustomFormatter'
]

__version__ = "1.0.0"
