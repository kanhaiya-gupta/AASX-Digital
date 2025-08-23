"""
Privacy Events
==============

Event management for privacy and security operations.
Handles privacy violations, security threats, and compliance events.
"""

import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService


class PrivacyEventType(Enum):
    """Privacy and security event types"""
    # Privacy events
    PRIVACY_VIOLATION_DETECTED = "privacy_violation_detected"
    DATA_LEAK_DETECTED = "data_leak_detected"
    PRIVACY_BUDGET_EXCEEDED = "privacy_budget_exceeded"
    DIFFERENTIAL_PRIVACY_VIOLATION = "differential_privacy_violation"
    
    # Security events
    SECURITY_THREAT_DETECTED = "security_threat_detected"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    ENCRYPTION_FAILURE = "encryption_failure"
    AUTHENTICATION_FAILURE = "authentication_failure"
    
    # Compliance events
    COMPLIANCE_VIOLATION = "compliance_violation"
    AUDIT_REQUIRED = "audit_required"
    REGULATORY_UPDATE = "regulatory_update"
    COMPLIANCE_CHECK_FAILED = "compliance_check_failed"
    
    # Privacy protection events
    PRIVACY_ENHANCEMENT_APPLIED = "privacy_enhancement_applied"
    SECURITY_UPGRADE_COMPLETED = "security_upgrade_completed"
    COMPLIANCE_IMPROVED = "compliance_improved"


@dataclass
class PrivacyEvent:
    """Privacy event data structure"""
    event_id: str
    event_type: PrivacyEventType
    registry_id: str
    federation_name: str
    timestamp: datetime
    source: str
    severity: str  # low, medium, high, critical
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = f"privacy_event_{self.event_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        if not self.timestamp:
            self.timestamp = datetime.now()


class PrivacyEventManager:
    """Manager for privacy and security events"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService
    ):
        """Initialize privacy event manager"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        
        # Event handlers registry
        self.event_handlers: Dict[PrivacyEventType, List[Callable]] = {}
        
        # Event history
        self.event_history: List[PrivacyEvent] = []
        
        # Performance tracking
        self.events_processed = 0
        self.events_failed = 0
        
        # Security tracking
        self.critical_events = 0
        self.security_threats = 0
    
    async def emit_privacy_event(
        self,
        event_type: PrivacyEventType,
        registry_id: str,
        federation_name: str,
        severity: str,
        data: Dict[str, Any],
        source: str = "privacy_system",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Emit a privacy event"""
        try:
            # Create event
            event = PrivacyEvent(
                event_type=event_type,
                registry_id=registry_id,
                federation_name=federation_name,
                severity=severity,
                data=data,
                source=source,
                metadata=metadata or {}
            )
            
            # Add to history
            self.event_history.append(event)
            
            # Limit history size
            if len(self.event_history) > 5000:
                self.event_history = self.event_history[-2500:]
            
            # Track critical events
            if severity in ['high', 'critical']:
                self.critical_events += 1
            
            if event_type.value.startswith('security_') or event_type.value.startswith('unauthorized_'):
                self.security_threats += 1
            
            # Process event
            await self._process_privacy_event(event)
            
            print(f"🔒 Privacy event emitted: {event_type.value} ({severity}) for {federation_name}")
            
        except Exception as e:
            print(f"❌ Failed to emit privacy event: {e}")
    
    async def _process_privacy_event(self, event: PrivacyEvent):
        """Process a privacy event"""
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
                    print(f"⚠️  Privacy event handler error: {e}")
            
            # Update metrics
            self.events_processed += 1
            
            print(f"✅ Privacy event processed: {event.event_type.value}")
            
        except Exception as e:
            print(f"❌ Privacy event processing failed: {e}")
            self.events_failed += 1
    
    def register_privacy_handler(
        self,
        event_type: PrivacyEventType,
        handler: Callable
    ):
        """Register a handler for privacy events"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        print(f"✅ Privacy event handler registered for {event_type.value}")
    
    def unregister_privacy_handler(
        self,
        event_type: PrivacyEventType,
        handler: Callable
    ):
        """Unregister a privacy event handler"""
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type].remove(handler)
                print(f"✅ Privacy event handler unregistered for {event_type.value}")
            except ValueError:
                print(f"⚠️  Privacy event handler not found for {event_type.value}")
    
    async def get_privacy_event_statistics(self) -> Dict[str, Any]:
        """Get privacy event statistics"""
        return {
            'events_processed': self.events_processed,
            'events_failed': self.events_failed,
            'total_events': len(self.event_history),
            'critical_events': self.critical_events,
            'security_threats': self.security_threats,
            'registered_handlers': sum(len(handlers) for handlers in self.event_handlers.values())
        }
    
    async def get_privacy_events(
        self,
        registry_id: Optional[str] = None,
        event_type: Optional[PrivacyEventType] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> List[PrivacyEvent]:
        """Get privacy events with optional filtering"""
        events = self.event_history[-limit:] if limit > 0 else self.event_history
        
        if registry_id:
            events = [e for e in events if e.registry_id == registry_id]
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if severity:
            events = [e for e in events if e.severity == severity]
        
        return events
    
    async def get_critical_privacy_events(self, limit: int = 50) -> List[PrivacyEvent]:
        """Get critical privacy events"""
        critical_events = [e for e in self.event_history if e.severity in ['high', 'critical']]
        return critical_events[-limit:] if limit > 0 else critical_events
    
    async def get_security_threats(self, limit: int = 50) -> List[PrivacyEvent]:
        """Get security threat events"""
        security_events = [e for e in self.event_history if e.event_type.value.startswith('security_') or e.event_type.value.startswith('unauthorized_')]
        return security_events[-limit:] if limit > 0 else security_events
