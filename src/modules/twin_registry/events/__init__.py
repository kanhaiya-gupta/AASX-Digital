"""
Twin Registry Events Module

Event-driven automation for twin registry operations.
Phase 3: Event System & Automation with pure async support.
"""

from .event_manager import (
    TwinRegistryEventManager,
    EventType,
    EventPriority,
    TwinRegistryEvent,
    EventHandler,
    FileUploadEventHandler,
    ETLSuccessEventHandler,
    ETLFailureEventHandler,
    LifecycleChangeEventHandler,
    PerformanceAlertEventHandler,
    emit_file_upload_event,
    emit_etl_success_event,
    emit_etl_failure_event
)

__all__ = [
    "TwinRegistryEventManager",
    "EventType",
    "EventPriority", 
    "TwinRegistryEvent",
    "EventHandler",
    "FileUploadEventHandler",
    "ETLSuccessEventHandler",
    "ETLFailureEventHandler",
    "LifecycleChangeEventHandler",
    "PerformanceAlertEventHandler",
    "emit_file_upload_event",
    "emit_etl_success_event",
    "emit_etl_failure_event"
]

__version__ = "3.3.0"
__description__ = "Event-driven automation for Twin Registry operations"
