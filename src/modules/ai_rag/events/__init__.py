"""
AI RAG Events Package.

This package provides the complete event system for the AI RAG module,
including event types, event bus, event handlers, and event logging.
"""

from .event_types import (
    BaseEvent,
    EventPriority,
    EventStatus,
    EventCategory,
    DocumentProcessingEvent,
    DocumentProcessingCompletedEvent,
    DocumentProcessingFailedEvent,
    GraphGenerationEvent,
    GraphGenerationStartedEvent,
    GraphGenerationCompletedEvent,
    GraphGenerationFailedEvent,
    KGIntegrationEvent,
    GraphTransferEvent,
    GraphTransferCompletedEvent,
    GraphTransferFailedEvent,
    GraphSyncEvent,
    GraphSyncCompletedEvent,
    GraphSyncFailedEvent,
    GraphLifecycleEvent,
    PerformanceEvent,
    PerformanceThresholdExceededEvent,
    SystemHealthEvent,
    SystemHealthChangedEvent,
    IntegrationEvent,
    IntegrationSuccessEvent,
    IntegrationFailureEvent,
    ErrorEvent,
    WarningEvent,
    ExternalAPIEvent,
    WebhookEvent,
    EventFactory,
    EVENT_TYPE_REGISTRY
)

from .event_bus import (
    EventBus,
    EventHandler,
    EventFilter
)

from .event_handlers import (
    BaseEventHandler,
    DocumentProcessingEventHandler,
    GraphGenerationEventHandler,
    KGIntegrationEventHandler,
    PerformanceMonitoringEventHandler,
    EventHandlerManager
)

from .event_logger import EventLogger

__all__ = [
    # Event Types
    'BaseEvent',
    'EventPriority',
    'EventStatus',
    'EventCategory',
    'DocumentProcessingEvent',
    'DocumentProcessingCompletedEvent',
    'DocumentProcessingFailedEvent',
    'GraphGenerationEvent',
    'GraphGenerationStartedEvent',
    'GraphGenerationCompletedEvent',
    'GraphGenerationFailedEvent',
    'KGIntegrationEvent',
    'GraphTransferEvent',
    'GraphTransferCompletedEvent',
    'GraphTransferFailedEvent',
    'GraphSyncEvent',
    'GraphSyncCompletedEvent',
    'GraphSyncFailedEvent',
    'GraphLifecycleEvent',
    'PerformanceEvent',
    'PerformanceThresholdExceededEvent',
    'SystemHealthEvent',
    'SystemHealthChangedEvent',
    'IntegrationEvent',
    'IntegrationSuccessEvent',
    'IntegrationFailureEvent',
    'ErrorEvent',
    'WarningEvent',
    'ExternalAPIEvent',
    'WebhookEvent',
    'EventFactory',
    'EVENT_TYPE_REGISTRY',
    
    # Event Bus
    'EventBus',
    'EventHandler',
    'EventFilter',
    
    # Event Handlers
    'BaseEventHandler',
    'DocumentProcessingEventHandler',
    'GraphGenerationEventHandler',
    'KGIntegrationEventHandler',
    'PerformanceMonitoringEventHandler',
    'EventHandlerManager',
    
    # Event Logger
    'EventLogger'
]
