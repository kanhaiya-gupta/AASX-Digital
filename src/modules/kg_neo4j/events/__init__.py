"""
Knowledge Graph Neo4j Events Package

Event-driven automation system for Knowledge Graph operations.
Provides event types, event manager, handlers, and event bus for decoupled communication.
"""

from .event_types import (
    KGNeo4jEvent,
    GraphCreationEvent,
    GraphStatusChangeEvent,
    Neo4jOperationEvent,
    AIInsightsEvent,
    HealthMonitoringEvent,
    EventPriority,
    EventStatus
)

from .event_manager import KGNeo4jEventManager
from .event_handlers import (
    GraphLifecycleEventHandler,
    Neo4jOperationEventHandler,
    AIInsightsEventHandler,
    HealthMonitoringEventHandler
)
from .event_bus import KGNeo4jEventBus

__all__ = [
    # Event Types
    'KGNeo4jEvent',
    'GraphCreationEvent',
    'GraphStatusChangeEvent',
    'Neo4jOperationEvent',
    'AIInsightsEvent',
    'HealthMonitoringEvent',
    'EventPriority',
    'EventStatus',
    
    # Core Components
    'KGNeo4jEventManager',
    'KGNeo4jEventBus',
    
    # Event Handlers
    'GraphLifecycleEventHandler',
    'Neo4jOperationEventHandler',
    'AIInsightsEventHandler',
    'HealthMonitoringEventHandler'
]
