"""
Federation Events
=================

Event management for federation lifecycle and operations.
Handles federation creation, updates, and lifecycle events.
"""

import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService


class FederationEventType(Enum):
    """Federation-specific event types"""
    # Lifecycle events
    FEDERATION_CREATED = "federation_created"
    FEDERATION_STARTED = "federation_started"
    FEDERATION_STOPPED = "federation_stopped"
    FEDERATION_COMPLETED = "federation_completed"
    FEDERATION_FAILED = "federation_failed"
    FEDERATION_PAUSED = "federation_paused"
    FEDERATION_RESUMED = "federation_resumed"
    
    # Participation events
    NODE_JOINED = "node_joined"
    NODE_LEFT = "node_left"
    NODE_FAILED = "node_failed"
    PARTICIPATION_UPDATE = "participation_update"
    
    # Configuration events
    CONFIG_UPDATED = "config_updated"
    STRATEGY_CHANGED = "strategy_changed"
    THRESHOLDS_MODIFIED = "thresholds_modified"
    
    # Health events
    HEALTH_DECLINING = "health_declining"
    HEALTH_RECOVERED = "health_recovered"
    CRITICAL_HEALTH = "critical_health"


@dataclass
class FederationEvent:
    """Federation event data structure"""
    event_id: str
    event_type: FederationEventType
    registry_id: str
    federation_name: str
    timestamp: datetime
    source: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = f"fed_event_{self.event_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        if not self.timestamp:
            self.timestamp = datetime.now()


class FederationEventManager:
    """Manager for federation-specific events"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService
    ):
        """Initialize federation event manager"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        
        # Event handlers registry
        self.event_handlers: Dict[FederationEventType, List[Callable]] = {}
        
        # Event history
        self.event_history: List[FederationEvent] = []
        
        # Performance tracking
        self.events_processed = 0
        self.events_failed = 0
    
    async def emit_federation_event(
        self,
        event_type: FederationEventType,
        registry_id: str,
        federation_name: str,
        data: Dict[str, Any],
        source: str = "federation_system",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Emit a federation event"""
        try:
            # Create event
            event = FederationEvent(
                event_type=event_type,
                registry_id=registry_id,
                federation_name=federation_name,
                data=data,
                source=source,
                metadata=metadata or {}
            )
            
            # Add to history
            self.event_history.append(event)
            
            # Limit history size
            if len(self.event_history) > 5000:
                self.event_history = self.event_history[-2500:]
            
            # Process event
            await self._process_federation_event(event)
            
            print(f"📡 Federation event emitted: {event_type.value} for {federation_name}")
            
        except Exception as e:
            print(f"❌ Failed to emit federation event: {e}")
    
    async def _process_federation_event(self, event: FederationEvent):
        """Process a federation event"""
        try:
            # Get registered handlers
            handlers = self.event_handlers.get(event.event_type, [])
            
            # Execute handlers
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    print(f"⚠️  Federation event handler error: {e}")
            
            # Update metrics
            self.events_processed += 1
            
            print(f"✅ Federation event processed: {event.event_type.value}")
            
        except Exception as e:
            print(f"❌ Federation event processing failed: {e}")
            self.events_failed += 1
    
    def register_federation_handler(
        self,
        event_type: FederationEventType,
        handler: Callable
    ):
        """Register a handler for federation events"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        print(f"✅ Federation event handler registered for {event_type.value}")
    
    def unregister_federation_handler(
        self,
        event_type: FederationEventType,
        handler: Callable
    ):
        """Unregister a federation event handler"""
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type].remove(handler)
                print(f"✅ Federation event handler unregistered for {event_type.value}")
            except ValueError:
                print(f"⚠️  Federation event handler not found for {event_type.value}")
    
    async def get_federation_event_statistics(self) -> Dict[str, Any]:
        """Get federation event statistics"""
        return {
            'events_processed': self.events_processed,
            'events_failed': self.events_failed,
            'total_events': len(self.event_history),
            'registered_handlers': sum(len(handlers) for handlers in self.event_handlers.values())
        }
    
    async def get_federation_events(
        self,
        registry_id: Optional[str] = None,
        event_type: Optional[FederationEventType] = None,
        limit: int = 100
    ) -> List[FederationEvent]:
        """Get federation events with optional filtering"""
        events = self.event_history[-limit:] if limit > 0 else self.event_history
        
        if registry_id:
            events = [e for e in events if e.registry_id == registry_id]
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        return events
