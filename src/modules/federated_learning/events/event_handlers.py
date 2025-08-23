"""
Event Handlers
==============

Core event processing infrastructure and handler registry.
Provides event handling, processing, and automation capabilities.
"""

import asyncio
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime
from abc import ABC, abstractmethod
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService
from .federation_events import FederationEvent, FederationEventType
from .privacy_events import PrivacyEvent, PrivacyEventType
from .aggregation_events import AggregationEvent, AggregationEventType
from .compliance_events import ComplianceEvent, ComplianceEventType


class EventHandler(ABC):
    """Abstract base class for event handlers"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService
    ):
        """Initialize event handler with dependencies"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
    
    @abstractmethod
    async def handle_event(self, event: Union[FederationEvent, PrivacyEvent, AggregationEvent, ComplianceEvent]):
        """Handle an event - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def get_handler_name(self) -> str:
        """Get the name of this handler - must be implemented by subclasses"""
        pass


class FederationEventHandler(EventHandler):
    """Handler for federation events"""
    
    async def handle_event(self, event: FederationEvent):
        """Handle federation events"""
        try:
            print(f"🔄 Federation event handler processing: {event.event_type.value}")
            
            # Handle different event types
            if event.event_type == FederationEventType.FEDERATION_CREATED:
                await self._handle_federation_created(event)
            elif event.event_type == FederationEventType.FEDERATION_STARTED:
                await self._handle_federation_started(event)
            elif event.event_type == FederationEventType.HEALTH_DECLINING:
                await self._handle_health_declining(event)
            else:
                await self._handle_generic_federation_event(event)
                
        except Exception as e:
            print(f"❌ Federation event handler error: {e}")
    
    def get_handler_name(self) -> str:
        return "FederationEventHandler"
    
    async def _handle_federation_created(self, event: FederationEvent):
        """Handle federation creation events"""
        print(f"✅ New federation created: {event.federation_name}")
        # Implementation for federation creation handling
    
    async def _handle_federation_started(self, event: FederationEvent):
        """Handle federation start events"""
        print(f"🚀 Federation started: {event.federation_name}")
        # Implementation for federation start handling
    
    async def _handle_health_declining(self, event: FederationEvent):
        """Handle health declining events"""
        print(f"⚠️  Health declining for federation: {event.federation_name}")
        # Implementation for health monitoring
    
    async def _handle_generic_federation_event(self, event: FederationEvent):
        """Handle generic federation events"""
        print(f"📊 Generic federation event: {event.event_type.value}")


class PrivacyEventHandler(EventHandler):
    """Handler for privacy events"""
    
    async def handle_event(self, event: PrivacyEvent):
        """Handle privacy events"""
        try:
            print(f"🔒 Privacy event handler processing: {event.event_type.value} ({event.severity})")
            
            # Handle different event types
            if event.event_type == PrivacyEventType.PRIVACY_VIOLATION_DETECTED:
                await self._handle_privacy_violation(event)
            elif event.event_type == PrivacyEventType.SECURITY_THREAT_DETECTED:
                await self._handle_security_threat(event)
            elif event.event_type == PrivacyEventType.COMPLIANCE_VIOLATION:
                await self._handle_compliance_violation(event)
            else:
                await self._handle_generic_privacy_event(event)
                
        except Exception as e:
            print(f"❌ Privacy event handler error: {e}")
    
    def get_handler_name(self) -> str:
        return "PrivacyEventHandler"
    
    async def _handle_privacy_violation(self, event: PrivacyEvent):
        """Handle privacy violation events"""
        print(f"🚨 Privacy violation detected: {event.federation_name}")
        # Implementation for privacy violation handling
    
    async def _handle_security_threat(self, event: PrivacyEvent):
        """Handle security threat events"""
        print(f"⚠️  Security threat detected: {event.federation_name}")
        # Implementation for security threat handling
    
    async def _handle_compliance_violation(self, event: PrivacyEvent):
        """Handle compliance violation events"""
        print(f"📋 Compliance violation: {event.federation_name}")
        # Implementation for compliance violation handling
    
    async def _handle_generic_privacy_event(self, event: PrivacyEvent):
        """Handle generic privacy events"""
        print(f"🔒 Generic privacy event: {event.event_type.value}")


class AggregationEventHandler(EventHandler):
    """Handler for aggregation events"""
    
    async def handle_event(self, event: AggregationEvent):
        """Handle aggregation events"""
        try:
            print(f"🔄 Aggregation event handler processing: {event.event_type.value}")
            
            # Handle different event types
            if event.event_type == AggregationEventType.MODEL_TRAINING_STARTED:
                await self._handle_training_started(event)
            elif event.event_type == AggregationEventType.MODEL_AGGREGATION_COMPLETED:
                await self._handle_aggregation_completed(event)
            elif event.event_type == AggregationEventType.QUALITY_THRESHOLD_EXCEEDED:
                await self._handle_quality_threshold_exceeded(event)
            else:
                await self._handle_generic_aggregation_event(event)
                
        except Exception as e:
            print(f"❌ Aggregation event handler error: {e}")
    
    def get_handler_name(self) -> str:
        return "AggregationEventHandler"
    
    async def _handle_training_started(self, event: AggregationEvent):
        """Handle training start events"""
        print(f"🚀 Model training started: {event.federation_name}")
        # Implementation for training start handling
    
    async def _handle_aggregation_completed(self, event: AggregationEvent):
        """Handle aggregation completion events"""
        print(f"✅ Model aggregation completed: {event.federation_name}")
        # Implementation for aggregation completion handling
    
    async def _handle_quality_threshold_exceeded(self, event: AggregationEvent):
        """Handle quality threshold events"""
        print(f"⚠️  Quality threshold exceeded: {event.federation_name}")
        # Implementation for quality monitoring
    
    async def _handle_generic_aggregation_event(self, event: AggregationEvent):
        """Handle generic aggregation events"""
        print(f"🔄 Generic aggregation event: {event.event_type.value}")


class ComplianceEventHandler(EventHandler):
    """Handler for compliance events"""
    
    async def handle_event(self, event: ComplianceEvent):
        """Handle compliance events"""
        try:
            print(f"📋 Compliance event handler processing: {event.event_type.value}")
            
            # Handle different event types
            if event.event_type == ComplianceEventType.COMPLIANCE_VIOLATION:
                await self._handle_compliance_violation(event)
            elif event.event_type == ComplianceEventType.AUDIT_REQUIRED:
                await self._handle_audit_required(event)
            elif event.event_type == ComplianceEventType.REGULATORY_DEADLINE_APPROACHING:
                await self._handle_deadline_approaching(event)
            else:
                await self._handle_generic_compliance_event(event)
                
        except Exception as e:
            print(f"❌ Compliance event handler error: {e}")
    
    def get_handler_name(self) -> str:
        return "ComplianceEventHandler"
    
    async def _handle_compliance_violation(self, event: ComplianceEvent):
        """Handle compliance violation events"""
        print(f"🚨 Compliance violation: {event.federation_name}")
        # Implementation for compliance violation handling
    
    async def _handle_audit_required(self, event: ComplianceEvent):
        """Handle audit required events"""
        print(f"📋 Audit required: {event.federation_name}")
        # Implementation for audit scheduling
    
    async def _handle_deadline_approaching(self, event: ComplianceEvent):
        """Handle deadline approaching events"""
        print(f"⏰ Deadline approaching: {event.federation_name}")
        # Implementation for deadline monitoring
    
    async def _handle_generic_compliance_event(self, event: ComplianceEvent):
        """Handle generic compliance events"""
        print(f"📋 Generic compliance event: {event.event_type.value}")


class EventHandlerRegistry:
    """Registry for managing event handlers"""
    
    def __init__(self):
        """Initialize event handler registry"""
        self.handlers: Dict[str, List[EventHandler]] = {}
        self.handler_instances: Dict[str, EventHandler] = {}
    
    def register_handler(self, event_type: str, handler: EventHandler):
        """Register a handler for an event type"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        
        self.handlers[event_type].append(handler)
        self.handler_instances[handler.get_handler_name()] = handler
        
        print(f"✅ Handler registered: {handler.get_handler_name()} for {event_type}")
    
    def unregister_handler(self, event_type: str, handler: EventHandler):
        """Unregister a handler for an event type"""
        if event_type in self.handlers:
            try:
                self.handlers[event_type].remove(handler)
                print(f"✅ Handler unregistered: {handler.get_handler_name()} for {event_type}")
            except ValueError:
                print(f"⚠️  Handler not found: {handler.get_handler_name()} for {event_type}")
    
    def get_handlers(self, event_type: str) -> List[EventHandler]:
        """Get handlers for an event type"""
        return self.handlers.get(event_type, [])
    
    def get_all_handlers(self) -> Dict[str, List[EventHandler]]:
        """Get all registered handlers"""
        return self.handlers.copy()
    
    def get_handler_instance(self, handler_name: str) -> Optional[EventHandler]:
        """Get a specific handler instance by name"""
        return self.handler_instances.get(handler_name)


class EventProcessor:
    """Main event processor for coordinating event handling"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService
    ):
        """Initialize event processor"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        
        # Initialize handler registry
        self.handler_registry = EventHandlerRegistry()
        
        # Initialize default handlers
        self._initialize_default_handlers()
        
        # Performance tracking
        self.events_processed = 0
        self.events_failed = 0
    
    def _initialize_default_handlers(self):
        """Initialize default event handlers"""
        # Federation event handlers
        federation_handler = FederationEventHandler(
            self.connection_manager, self.registry_service, self.metrics_service
        )
        self.handler_registry.register_handler("federation", federation_handler)
        
        # Privacy event handlers
        privacy_handler = PrivacyEventHandler(
            self.connection_manager, self.registry_service, self.metrics_service
        )
        self.handler_registry.register_handler("privacy", privacy_handler)
        
        # Aggregation event handlers
        aggregation_handler = AggregationEventHandler(
            self.connection_manager, self.registry_service, self.metrics_service
        )
        self.handler_registry.register_handler("aggregation", aggregation_handler)
        
        # Compliance event handlers
        compliance_handler = ComplianceEventHandler(
            self.connection_manager, self.registry_service, self.metrics_service
        )
        self.handler_registry.register_handler("compliance", compliance_handler)
        
        print("✅ Default event handlers initialized")
    
    async def process_event(self, event: Union[FederationEvent, PrivacyEvent, AggregationEvent, ComplianceEvent]):
        """Process an event using appropriate handlers"""
        try:
            # Determine event type
            if isinstance(event, FederationEvent):
                event_type = "federation"
            elif isinstance(event, PrivacyEvent):
                event_type = "privacy"
            elif isinstance(event, AggregationEvent):
                event_type = "aggregation"
            elif isinstance(event, ComplianceEvent):
                event_type = "compliance"
            else:
                print(f"⚠️  Unknown event type: {type(event)}")
                return
            
            # Get handlers for this event type
            handlers = self.handler_registry.get_handlers(event_type)
            
            if not handlers:
                print(f"⚠️  No handlers found for event type: {event_type}")
                return
            
            # Process event with all handlers
            for handler in handlers:
                try:
                    await handler.handle_event(event)
                except Exception as e:
                    print(f"⚠️  Handler error: {handler.get_handler_name()} - {e}")
            
            # Update metrics
            self.events_processed += 1
            print(f"✅ Event processed successfully: {event_type}")
            
        except Exception as e:
            print(f"❌ Event processing failed: {e}")
            self.events_failed += 1
    
    async def get_processor_statistics(self) -> Dict[str, Any]:
        """Get event processor statistics"""
        return {
            'events_processed': self.events_processed,
            'events_failed': self.events_failed,
            'total_handlers': len(self.handler_registry.get_all_handlers()),
            'handler_instances': len(self.handler_registry.handler_instances)
        }
