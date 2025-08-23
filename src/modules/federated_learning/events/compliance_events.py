"""
Compliance Events
=================

Event management for compliance and regulatory operations.
Handles compliance violations, audits, and regulatory updates.
"""

import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService


class ComplianceEventType(Enum):
    """Compliance and regulatory event types"""
    # Compliance events
    COMPLIANCE_VIOLATION = "compliance_violation"
    COMPLIANCE_IMPROVED = "compliance_improved"
    COMPLIANCE_DEGRADED = "compliance_degraded"
    COMPLIANCE_CHECK_FAILED = "compliance_check_failed"
    
    # Audit events
    AUDIT_REQUIRED = "audit_required"
    AUDIT_SCHEDULED = "audit_scheduled"
    AUDIT_STARTED = "audit_started"
    AUDIT_COMPLETED = "audit_completed"
    AUDIT_FAILED = "audit_failed"
    
    # Regulatory events
    REGULATORY_UPDATE = "regulatory_update"
    REGULATORY_DEADLINE_APPROACHING = "regulatory_deadline_approaching"
    REGULATORY_DEADLINE_MISSED = "regulatory_deadline_missed"
    REGULATORY_COMPLIANCE_ACHIEVED = "regulatory_compliance_achieved"
    
    # Risk events
    RISK_LEVEL_INCREASED = "risk_level_increased"
    RISK_LEVEL_DECREASED = "risk_level_decreased"
    RISK_ASSESSMENT_REQUIRED = "risk_assessment_required"
    RISK_MITIGATION_APPLIED = "risk_mitigation_applied"


@dataclass
class ComplianceEvent:
    """Compliance event data structure"""
    event_id: str
    event_type: ComplianceEventType
    registry_id: str
    federation_name: str
    timestamp: datetime
    source: str
    compliance_framework: Optional[str] = None
    risk_level: Optional[str] = None
    deadline: Optional[datetime] = None
    data: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = f"comp_event_{self.event_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        if not self.timestamp:
            self.timestamp = datetime.now()
        
        if self.data is None:
            self.data = {}
        
        if self.metadata is None:
            self.metadata = {}


class ComplianceEventManager:
    """Manager for compliance and regulatory events"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService
    ):
        """Initialize compliance event manager"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        
        # Event handlers registry
        self.event_handlers: Dict[ComplianceEventType, List[Callable]] = {}
        
        # Event history
        self.event_history: List[ComplianceEvent] = []
        
        # Performance tracking
        self.events_processed = 0
        self.events_failed = 0
        
        # Compliance tracking
        self.compliance_violations = 0
        self.audit_events = 0
        self.regulatory_events = 0
        self.risk_events = 0
    
    async def emit_compliance_event(
        self,
        event_type: ComplianceEventType,
        registry_id: str,
        federation_name: str,
        compliance_framework: Optional[str] = None,
        risk_level: Optional[str] = None,
        deadline: Optional[datetime] = None,
        data: Optional[Dict[str, Any]] = None,
        source: str = "compliance_system",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Emit a compliance event"""
        try:
            # Create event
            event = ComplianceEvent(
                event_type=event_type,
                registry_id=registry_id,
                federation_name=federation_name,
                compliance_framework=compliance_framework,
                risk_level=risk_level,
                deadline=deadline,
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
            if event_type.value.startswith('compliance'):
                if 'violation' in event_type.value:
                    self.compliance_violations += 1
            elif event_type.value.startswith('audit'):
                self.audit_events += 1
            elif event_type.value.startswith('regulatory'):
                self.regulatory_events += 1
            elif event_type.value.startswith('risk'):
                self.risk_events += 1
            
            # Process event
            await self._process_compliance_event(event)
            
            print(f"📋 Compliance event emitted: {event_type.value} for {federation_name}")
            
        except Exception as e:
            print(f"❌ Failed to emit compliance event: {e}")
    
    async def _process_compliance_event(self, event: ComplianceEvent):
        """Process a compliance event"""
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
                    print(f"⚠️  Compliance event handler error: {e}")
            
            # Update metrics
            self.events_processed += 1
            
            print(f"✅ Compliance event processed: {event.event_type.value}")
            
        except Exception as e:
            print(f"❌ Compliance event processing failed: {e}")
            self.events_failed += 1
    
    def register_compliance_handler(
        self,
        event_type: ComplianceEventType,
        handler: Callable
    ):
        """Register a handler for compliance events"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        print(f"✅ Compliance event handler registered for {event_type.value}")
    
    def unregister_compliance_handler(
        self,
        event_type: ComplianceEventType,
        handler: Callable
    ):
        """Unregister a compliance event handler"""
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type].remove(handler)
                print(f"✅ Compliance event handler unregistered for {event_type.value}")
            except ValueError:
                print(f"⚠️  Compliance event handler not found for {event_type.value}")
    
    async def get_compliance_event_statistics(self) -> Dict[str, Any]:
        """Get compliance event statistics"""
        return {
            'events_processed': self.events_processed,
            'events_failed': self.events_failed,
            'total_events': len(self.event_history),
            'compliance_violations': self.compliance_violations,
            'audit_events': self.audit_events,
            'regulatory_events': self.regulatory_events,
            'risk_events': self.risk_events,
            'registered_handlers': sum(len(handlers) for handlers in self.event_handlers.values())
        }
    
    async def get_compliance_events(
        self,
        registry_id: Optional[str] = None,
        event_type: Optional[ComplianceEventType] = None,
        compliance_framework: Optional[str] = None,
        risk_level: Optional[str] = None,
        limit: int = 100
    ) -> List[ComplianceEvent]:
        """Get compliance events with optional filtering"""
        events = self.event_history[-limit:] if limit > 0 else self.event_history
        
        if registry_id:
            events = [e for e in events if e.registry_id == registry_id]
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if compliance_framework:
            events = [e for e in events if e.compliance_framework == compliance_framework]
        
        if risk_level:
            events = [e for e in events if e.risk_level == risk_level]
        
        return events
    
    async def get_compliance_violations(self, limit: int = 50) -> List[ComplianceEvent]:
        """Get compliance violation events"""
        violations = [e for e in self.event_history if 'violation' in e.event_type.value]
        return violations[-limit:] if limit > 0 else violations
    
    async def get_audit_events(self, limit: int = 50) -> List[ComplianceEvent]:
        """Get audit-related events"""
        audit_events = [e for e in self.event_history if e.event_type.value.startswith('audit')]
        return audit_events[-limit:] if limit > 0 else audit_events
    
    async def get_regulatory_events(self, limit: int = 50) -> List[ComplianceEvent]:
        """Get regulatory-related events"""
        regulatory_events = [e for e in self.event_history if e.event_type.value.startswith('regulatory')]
        return regulatory_events[-limit:] if limit > 0 else regulatory_events
    
    async def get_risk_events(self, limit: int = 50) -> List[ComplianceEvent]:
        """Get risk-related events"""
        risk_events = [e for e in self.event_history if e.event_type.value.startswith('risk')]
        return risk_events[-limit:] if limit > 0 else risk_events
    
    async def get_upcoming_deadlines(self, days_ahead: int = 30) -> List[ComplianceEvent]:
        """Get events with upcoming deadlines"""
        cutoff_date = datetime.now() + asyncio.get_event_loop().time() + (days_ahead * 24 * 60 * 60)
        upcoming_events = [e for e in self.event_history if e.deadline and e.deadline <= cutoff_date]
        return sorted(upcoming_events, key=lambda x: x.deadline)
