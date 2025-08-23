"""
Federated Learning Events Package
=================================

Event management system for federated learning operations.
Provides event types, handlers, and automation capabilities.
"""

from .federation_events import (
    FederationEventType,
    FederationEvent,
    FederationEventManager
)

from .privacy_events import (
    PrivacyEventType,
    PrivacyEvent,
    PrivacyEventManager
)

from .aggregation_events import (
    AggregationEventType,
    AggregationEvent,
    AggregationEventManager
)

from .compliance_events import (
    ComplianceEventType,
    ComplianceEvent,
    ComplianceEventManager
)

from .event_handlers import (
    EventHandler,
    EventHandlerRegistry,
    EventProcessor
)

__all__ = [
    # Federation Events
    'FederationEventType',
    'FederationEvent', 
    'FederationEventManager',
    
    # Privacy Events
    'PrivacyEventType',
    'PrivacyEvent',
    'PrivacyEventManager',
    
    # Aggregation Events
    'AggregationEventType',
    'AggregationEvent',
    'AggregationEventManager',
    
    # Compliance Events
    'ComplianceEventType',
    'ComplianceEvent',
    'ComplianceEventManager',
    
    # Event Handlers
    'EventHandler',
    'EventHandlerRegistry',
    'EventProcessor',
]
