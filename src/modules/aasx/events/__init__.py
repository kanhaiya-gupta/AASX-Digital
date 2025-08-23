"""
AASX Event Package

This package contains event management for AASX processing operations.
"""

from .event_manager import (
    EventManager,
    Event,
    EventType,
    EventPriority,
    EventHandler,
    LoggingEventHandler,
    WebhookEventHandler,
    DatabasePopulationEventHandler,
    BatchDetector,
    ProcessingController,
    get_event_manager,
    start_event_manager,
    stop_event_manager,
    emit_file_uploaded,
    emit_etl_started,
    emit_etl_completed,
    emit_etl_failed,
    emit_batch_detected,
    emit_processing_started,
    emit_processing_completed,
    emit_processing_failed,
    emit_validation_started,
    emit_validation_completed,
    emit_validation_failed
)

__version__ = "1.0.0"
__author__ = "AAS Data Modeling Team"

__all__ = [
    # Event management
    'EventManager',
    'Event',
    'EventType',
    'EventPriority',
    'EventHandler',
    'LoggingEventHandler',
    'WebhookEventHandler',
    'DatabasePopulationEventHandler',
    
    # Hybrid architecture components
    'BatchDetector',
    'ProcessingController',
    
    # Global event manager functions
    'get_event_manager',
    'start_event_manager',
    'stop_event_manager',
    
    # File upload and ETL events
    'emit_file_uploaded',
    'emit_etl_started',
    'emit_etl_completed',
    'emit_etl_failed',
    'emit_batch_detected',
    
    # Processing events
    'emit_processing_started',
    'emit_processing_completed',
    'emit_processing_failed',
    
    # Validation events
    'emit_validation_started',
    'emit_validation_completed',
    'emit_validation_failed'
]
