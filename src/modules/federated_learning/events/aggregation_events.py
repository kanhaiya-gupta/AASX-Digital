"""
Aggregation Events
==================

Event management for model aggregation and training operations.
Handles model training, aggregation, and quality assessment events.
"""

import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService


class AggregationEventType(Enum):
    """Model aggregation and training event types"""
    # Training events
    MODEL_TRAINING_STARTED = "model_training_started"
    MODEL_TRAINING_COMPLETED = "model_training_completed"
    MODEL_TRAINING_FAILED = "model_training_failed"
    TRAINING_EPOCH_COMPLETED = "training_epoch_completed"
    
    # Aggregation events
    MODEL_AGGREGATION_STARTED = "model_aggregation_started"
    MODEL_AGGREGATION_COMPLETED = "model_aggregation_completed"
    MODEL_AGGREGATION_FAILED = "model_aggregation_failed"
    PARTIAL_AGGREGATION = "partial_aggregation"
    
    # Quality events
    MODEL_QUALITY_ASSESSMENT = "model_quality_assessment"
    QUALITY_THRESHOLD_EXCEEDED = "quality_threshold_exceeded"
    MODEL_OPTIMIZATION_REQUIRED = "model_optimization_required"
    CONVERGENCE_ACHIEVED = "convergence_achieved"
    
    # Performance events
    PERFORMANCE_DEGRADATION = "performance_degradation"
    PERFORMANCE_IMPROVEMENT = "performance_improvement"
    RESOURCE_UTILIZATION_HIGH = "resource_utilization_high"
    BOTTLENECK_DETECTED = "bottleneck_detected"


@dataclass
class AggregationEvent:
    """Aggregation event data structure"""
    event_id: str
    event_type: AggregationEventType
    registry_id: str
    federation_name: str
    timestamp: datetime
    source: str
    model_id: Optional[str] = None
    training_round: Optional[int] = None
    data: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = f"agg_event_{self.event_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        if not self.timestamp:
            self.timestamp = datetime.now()
        
        if self.data is None:
            self.data = {}
        
        if self.metadata is None:
            self.metadata = {}


class AggregationEventManager:
    """Manager for model aggregation and training events"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService
    ):
        """Initialize aggregation event manager"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        
        # Event handlers registry
        self.event_handlers: Dict[AggregationEventType, List[Callable]] = {}
        
        # Event history
        self.event_history: List[AggregationEvent] = []
        
        # Performance tracking
        self.events_processed = 0
        self.events_failed = 0
        
        # Training tracking
        self.training_events = 0
        self.aggregation_events = 0
        self.quality_events = 0
    
    async def emit_aggregation_event(
        self,
        event_type: AggregationEventType,
        registry_id: str,
        federation_name: str,
        model_id: Optional[str] = None,
        training_round: Optional[int] = None,
        data: Optional[Dict[str, Any]] = None,
        source: str = "aggregation_system",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Emit an aggregation event"""
        try:
            # Create event
            event = AggregationEvent(
                event_type=event_type,
                registry_id=registry_id,
                federation_name=federation_name,
                model_id=model_id,
                training_round=training_round,
                data=data or {},
                source=source,
                metadata=metadata or {}
            )
            
            # Add to history
            self.event_history.append(event)
            
            # Limit history size
            if len(self.event_history) > 5000:
                self.event_history = self.event_history[-2500:]
            
            # Track event types
            if event_type.value.startswith('model_training'):
                self.training_events += 1
            elif event_type.value.startswith('model_aggregation'):
                self.aggregation_events += 1
            elif event_type.value.startswith('model_quality') or event_type.value.startswith('quality_'):
                self.quality_events += 1
            
            # Process event
            await self._process_aggregation_event(event)
            
            print(f"🔄 Aggregation event emitted: {event_type.value} for {federation_name}")
            
        except Exception as e:
            print(f"❌ Failed to emit aggregation event: {e}")
    
    async def _process_aggregation_event(self, event: AggregationEvent):
        """Process an aggregation event"""
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
                    print(f"⚠️  Aggregation event handler error: {e}")
            
            # Update metrics
            self.events_processed += 1
            
            print(f"✅ Aggregation event processed: {event.event_type.value}")
            
        except Exception as e:
            print(f"❌ Aggregation event processing failed: {e}")
            self.events_failed += 1
    
    def register_aggregation_handler(
        self,
        event_type: AggregationEventType,
        handler: Callable
    ):
        """Register a handler for aggregation events"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        print(f"✅ Aggregation event handler registered for {event_type.value}")
    
    def unregister_aggregation_handler(
        self,
        event_type: AggregationEventType,
        handler: Callable
    ):
        """Unregister an aggregation event handler"""
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type].remove(handler)
                print(f"✅ Aggregation event handler unregistered for {event_type.value}")
            except ValueError:
                print(f"⚠️  Aggregation event handler not found for {event_type.value}")
    
    async def get_aggregation_event_statistics(self) -> Dict[str, Any]:
        """Get aggregation event statistics"""
        return {
            'events_processed': self.events_processed,
            'events_failed': self.events_failed,
            'total_events': len(self.event_history),
            'training_events': self.training_events,
            'aggregation_events': self.aggregation_events,
            'quality_events': self.quality_events,
            'registered_handlers': sum(len(handlers) for handlers in self.event_handlers.values())
        }
    
    async def get_aggregation_events(
        self,
        registry_id: Optional[str] = None,
        event_type: Optional[AggregationEventType] = None,
        model_id: Optional[str] = None,
        training_round: Optional[int] = None,
        limit: int = 100
    ) -> List[AggregationEvent]:
        """Get aggregation events with optional filtering"""
        events = self.event_history[-limit:] if limit > 0 else self.event_history
        
        if registry_id:
            events = [e for e in events if e.registry_id == registry_id]
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if model_id:
            events = [e for e in events if e.model_id == model_id]
        
        if training_round is not None:
            events = [e for e in events if e.training_round == training_round]
        
        return events
    
    async def get_training_events(self, limit: int = 100) -> List[AggregationEvent]:
        """Get training-related events"""
        training_events = [e for e in self.event_history if e.event_type.value.startswith('model_training')]
        return training_events[-limit:] if limit > 0 else training_events
    
    async def get_aggregation_events_by_round(self, training_round: int, limit: int = 50) -> List[AggregationEvent]:
        """Get aggregation events for a specific training round"""
        round_events = [e for e in self.event_history if e.training_round == training_round and e.event_type.value.startswith('model_aggregation')]
        return round_events[-limit:] if limit > 0 else round_events
    
    async def get_model_quality_events(self, model_id: str, limit: int = 50) -> List[AggregationEvent]:
        """Get quality events for a specific model"""
        quality_events = [e for e in self.event_history if e.model_id == model_id and (e.event_type.value.startswith('model_quality') or e.event_type.value.startswith('quality_'))]
        return quality_events[-limit:] if limit > 0 else quality_events
