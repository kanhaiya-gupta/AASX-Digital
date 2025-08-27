"""
Federated Learning Event Manager
================================

Advanced event-driven architecture for federated learning operations.
Integrates with engine event system using pure async patterns.
"""

import asyncio
from typing import Dict, Any, List, Optional, Callable, Coroutine
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService
from ..services import (
    FederationOrchestrationService,
    PrivacyPreservationService,
    PerformanceAnalyticsService,
    ComplianceMonitoringService
)


class EventType(Enum):
    """Federated Learning Event Types"""
    # Federation lifecycle events
    FEDERATION_CREATED = "federation_created"
    FEDERATION_STARTED = "federation_started"
    FEDERATION_STOPPED = "federation_stopped"
    FEDERATION_COMPLETED = "federation_completed"
    FEDERATION_FAILED = "federation_failed"
    
    # Performance events
    PERFORMANCE_THRESHOLD_EXCEEDED = "performance_threshold_exceeded"
    HEALTH_SCORE_DECLINING = "health_score_declining"
    RESOURCE_UTILIZATION_HIGH = "resource_utilization_high"
    BOTTLENECK_DETECTED = "bottleneck_detected"
    
    # Privacy and security events
    PRIVACY_VIOLATION_DETECTED = "privacy_violation_detected"
    SECURITY_THREAT_DETECTED = "security_threat_detected"
    COMPLIANCE_VIOLATION = "compliance_violation"
    AUDIT_REQUIRED = "audit_required"
    
    # Model training events
    MODEL_TRAINING_STARTED = "model_training_started"
    MODEL_TRAINING_COMPLETED = "model_training_completed"
    MODEL_AGGREGATION_STARTED = "model_aggregation_started"
    MODEL_AGGREGATION_COMPLETED = "model_aggregation_completed"
    
    # System events
    SYSTEM_MAINTENANCE = "system_maintenance"
    BACKUP_REQUIRED = "backup_required"
    SCALING_REQUIRED = "scaling_required"


class EventSeverity(Enum):
    """Event Severity Levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class FederatedLearningEvent:
    """Federated Learning Event Data Structure"""
    event_id: str
    event_type: EventType
    severity: EventSeverity
    registry_id: str
    federation_name: str
    timestamp: datetime
    source: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = f"fl_event_{self.event_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        if not self.timestamp:
            self.timestamp = datetime.now()


class FederatedLearningEventManager:
    """Advanced event manager for federated learning operations"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService
    ):
        """Initialize event manager with dependencies"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        
        # Initialize services
        self.federation_service = FederationOrchestrationService(
            connection_manager, registry_service, metrics_service
        )
        self.privacy_service = PrivacyPreservationService(
            connection_manager, registry_service, metrics_service
        )
        self.performance_service = PerformanceAnalyticsService(
            connection_manager, registry_service, metrics_service
        )
        self.compliance_service = ComplianceMonitoringService(
            connection_manager, registry_service, metrics_service
        )
        
        # Event handlers registry
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        
        # Event queue for processing
        self.event_queue: asyncio.Queue = asyncio.Queue()
        
        # Event processing state
        self.is_processing = False
        self.processing_task: Optional[asyncio.Task] = None
        
        # Event history for analytics
        self.event_history: List[FederatedLearningEvent] = []
        
        # Performance monitoring
        self.events_processed = 0
        self.events_failed = 0
        self.avg_processing_time = 0.0
    
    async def start_event_processing(self):
        """Start the event processing loop"""
        if self.is_processing:
            return
        
        self.is_processing = True
        self.processing_task = asyncio.create_task(self._event_processing_loop())
        print("✅ Federated Learning Event Manager started")
    
    async def stop_event_processing(self):
        """Stop the event processing loop"""
        if not self.is_processing:
            return
        
        self.is_processing = False
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        
        print("✅ Federated Learning Event Manager stopped")
    
    async def _event_processing_loop(self):
        """Main event processing loop"""
        while self.is_processing:
            try:
                # Wait for events with timeout
                try:
                    event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # Process event
                start_time = datetime.now()
                await self._process_event(event)
                processing_time = (datetime.now() - start_time).total_seconds()
                
                # Update performance metrics
                self.events_processed += 1
                self.avg_processing_time = (
                    (self.avg_processing_time * (self.events_processed - 1) + processing_time) 
                    / self.events_processed
                )
                
                # Mark task as done
                self.event_queue.task_done()
                
            except Exception as e:
                print(f"❌ Event processing error: {e}")
                self.events_failed += 1
    
    async def emit_event(
        self,
        event_type: EventType,
        severity: EventSeverity,
        registry_id: str,
        federation_name: str,
        data: Dict[str, Any],
        source: str = "system",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Emit a new federated learning event"""
        try:
            # Create event
            event = FederatedLearningEvent(
                event_type=event_type,
                severity=severity,
                registry_id=registry_id,
                federation_name=federation_name,
                data=data,
                source=source,
                metadata=metadata or {}
            )
            
            # Add to queue for processing
            await self.event_queue.put(event)
            
            # Add to history
            self.event_history.append(event)
            
            # Limit history size
            if len(self.event_history) > 10000:
                self.event_history = self.event_history[-5000:]
            
            print(f"📡 Event emitted: {event_type.value} for {federation_name}")
            
        except Exception as e:
            print(f"❌ Failed to emit event: {e}")
    
    async def _process_event(self, event: FederatedLearningEvent):
        """Process a single event"""
        try:
            # Get registered handlers for this event type
            handlers = self.event_handlers.get(event.event_type, [])
            
            if not handlers:
                # Use default event handling
                await self._handle_default_event(event)
            else:
                # Execute custom handlers
                for handler in handlers:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(event)
                        else:
                            handler(event)
                    except Exception as e:
                        print(f"⚠️  Handler error for {event.event_type.value}: {e}")
            
            # Log event processing
            print(f"✅ Event processed: {event.event_type.value} ({event.severity.value})")
            
        except Exception as e:
            print(f"❌ Event processing failed: {e}")
            self.events_failed += 1
    
    async def _handle_default_event(self, event: FederatedLearningEvent):
        """Handle events with default behavior"""
        try:
            if event.event_type == EventType.FEDERATION_CREATED:
                await self._handle_federation_created(event)
            
            elif event.event_type == EventType.PERFORMANCE_THRESHOLD_EXCEEDED:
                await self._handle_performance_threshold_exceeded(event)
            
            elif event.event_type == EventType.PRIVACY_VIOLATION_DETECTED:
                await self._handle_privacy_violation(event)
            
            elif event.event_type == EventType.COMPLIANCE_VIOLATION:
                await self._handle_compliance_violation(event)
            
            elif event.event_type == EventType.MODEL_TRAINING_COMPLETED:
                await self._handle_model_training_completed(event)
            
            else:
                # Generic event handling
                await self._handle_generic_event(event)
                
        except Exception as e:
            print(f"⚠️  Default event handler error: {e}")
    
    async def _handle_federation_created(self, event: FederatedLearningEvent):
        """Handle federation creation events"""
        try:
            # Initialize monitoring for new federation
            await self._initialize_federation_monitoring(event.registry_id)
            
            # Schedule initial health check
            await self._schedule_health_check(event.registry_id, delay_minutes=5)
            
            print(f"✅ Federation monitoring initialized for {event.federation_name}")
            
        except Exception as e:
            print(f"⚠️  Federation creation handler error: {e}")
    
    async def _handle_performance_threshold_exceeded(self, event: FederatedLearningEvent):
        """Handle performance threshold events"""
        try:
            # Get performance analysis
            performance_summary = await self.performance_service.get_performance_summary(
                event.registry_id
            )
            
            # Generate optimization recommendations
            if 'error' not in performance_summary:
                recommendations = performance_summary.get('optimization_recommendations', [])
                
                # Emit optimization event
                await self.emit_event(
                    EventType.SYSTEM_MAINTENANCE,
                    EventSeverity.WARNING,
                    event.registry_id,
                    event.federation_name,
                    {
                        'action': 'performance_optimization',
                        'recommendations': recommendations,
                        'triggered_by': event.event_type.value
                    },
                    source="performance_analytics"
                )
            
            print(f"⚠️  Performance threshold exceeded for {event.federation_name}")
            
        except Exception as e:
            print(f"⚠️  Performance threshold handler error: {e}")
    
    async def _handle_privacy_violation(self, event: FederatedLearningEvent):
        """Handle privacy violation events"""
        try:
            # Assess privacy risk
            risk_assessment = await self.privacy_service.assess_privacy_risk(
                event.registry_id
            )
            
            # Generate privacy recommendations
            if 'error' not in risk_assessment:
                recommendations = risk_assessment.get('recommendations', [])
                
                # Emit privacy action event
                await self.emit_event(
                    EventType.SECURITY_THREAT_DETECTED,
                    EventSeverity.ERROR,
                    event.registry_id,
                    event.federation_name,
                    {
                        'action': 'privacy_mitigation',
                        'risk_level': risk_assessment.get('risk_assessment', {}).get('risk_level'),
                        'recommendations': recommendations,
                        'triggered_by': event.event_type.value
                    },
                    source="privacy_preservation"
                )
            
            print(f"🚨 Privacy violation detected for {event.federation_name}")
            
        except Exception as e:
            print(f"⚠️  Privacy violation handler error: {e}")
    
    async def _handle_compliance_violation(self, event: FederatedLearningEvent):
        """Handle compliance violation events"""
        try:
            # Get compliance status
            compliance_status = await self.compliance_service.monitor_compliance_status(
                event.registry_id
            )
            
            # Schedule compliance audit if needed
            if 'error' not in compliance_status:
                overall_status = compliance_status.get('overall_status')
                if overall_status in ['non_compliant', 'partially_compliant']:
                    await self._schedule_compliance_audit(event.registry_id)
            
            print(f"⚠️  Compliance violation for {event.federation_name}")
            
        except Exception as e:
            print(f"⚠️  Compliance violation handler error: {e}")
    
    async def _handle_model_training_completed(self, event: FederatedLearningEvent):
        """Handle model training completion events"""
        try:
            # Update federation status
            await self.federation_service.update_federation_config(
                event.registry_id,
                {'aggregation_status': 'ready_for_aggregation'}
            )
            
            # Emit aggregation event
            await self.emit_event(
                EventType.MODEL_AGGREGATION_STARTED,
                EventSeverity.INFO,
                event.registry_id,
                event.federation_name,
                {
                    'action': 'start_aggregation',
                    'training_completed_at': event.timestamp.isoformat(),
                    'triggered_by': event.event_type.value
                },
                source="federation_orchestration"
            )
            
            print(f"✅ Model training completed for {event.federation_name}")
            
        except Exception as e:
            print(f"⚠️  Model training completion handler error: {e}")
    
    async def _handle_generic_event(self, event: FederatedLearningEvent):
        """Handle generic events"""
        try:
            # Log event for analytics
            await self._log_event_for_analytics(event)
            
            # Check if event requires escalation
            if event.severity in [EventSeverity.ERROR, EventSeverity.CRITICAL]:
                await self._escalate_critical_event(event)
            
        except Exception as e:
            print(f"⚠️  Generic event handler error: {e}")
    
    async def _initialize_federation_monitoring(self, registry_id: str):
        """Initialize monitoring for a new federation"""
        try:
            # Set up performance monitoring
            await self.performance_service.analyze_performance_trends(registry_id, days=1)
            
            # Set up compliance monitoring
            await self.compliance_service.monitor_compliance_status(registry_id)
            
            print(f"✅ Monitoring initialized for federation {registry_id}")
            
        except Exception as e:
            print(f"⚠️  Failed to initialize monitoring: {e}")
    
    async def _schedule_health_check(self, registry_id: str, delay_minutes: int):
        """Schedule a health check for a federation"""
        try:
            # Schedule delayed health check
            await asyncio.sleep(delay_minutes * 60)
            
            # Perform health check
            federation_status = await self.federation_service.get_federation_status(registry_id)
            
            if 'error' not in federation_status:
                health_score = federation_status.get('health', {}).get('overall_score', 0)
                
                if health_score < 70.0:
                    await self.emit_event(
                        EventType.HEALTH_SCORE_DECLINING,
                        EventSeverity.WARNING,
                        registry_id,
                        federation_status.get('federation_name', 'Unknown'),
                        {
                            'health_score': health_score,
                            'threshold': 70.0,
                            'action': 'health_monitoring'
                        },
                        source="health_monitoring"
                    )
            
        except Exception as e:
            print(f"⚠️  Health check failed: {e}")
    
    async def _schedule_compliance_audit(self, registry_id: str):
        """Schedule a compliance audit for a federation"""
        try:
            # Schedule audit for next week
            audit_date = datetime.now() + timedelta(days=7)
            
            await self.compliance_service.schedule_compliance_audit(
                registry_id,
                audit_date,
                "System Auditor",
                "Compliance violation remediation"
            )
            
            print(f"✅ Compliance audit scheduled for {registry_id}")
            
        except Exception as e:
            print(f"⚠️  Failed to schedule compliance audit: {e}")
    
    async def _log_event_for_analytics(self, event: FederatedLearningEvent):
        """Log event for analytics purposes"""
        try:
            # Store event in database for analytics
            # This would integrate with the engine's analytics system
            pass
            
        except Exception as e:
            print(f"⚠️  Failed to log event for analytics: {e}")
    
    async def _escalate_critical_event(self, event: FederatedLearningEvent):
        """Escalate critical events"""
        try:
            # Send notifications
            await self._send_critical_notification(event)
            
            # Create incident ticket
            await self._create_incident_ticket(event)
            
            print(f"🚨 Critical event escalated: {event.event_type.value}")
            
        except Exception as e:
            print(f"⚠️  Failed to escalate critical event: {e}")
    
    async def _send_critical_notification(self, event: FederatedLearningEvent):
        """Send critical event notifications"""
        # Implementation would integrate with notification system
        pass
    
    async def _create_incident_ticket(self, event: FederatedLearningEvent):
        """Create incident ticket for critical events"""
        # Implementation would integrate with ticketing system
        pass
    
    def register_event_handler(
        self,
        event_type: EventType,
        handler: Callable
    ):
        """Register a custom event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        print(f"✅ Event handler registered for {event_type.value}")
    
    def unregister_event_handler(
        self,
        event_type: EventType,
        handler: Callable
    ):
        """Unregister an event handler"""
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type].remove(handler)
                print(f"✅ Event handler unregistered for {event_type.value}")
            except ValueError:
                print(f"⚠️  Handler not found for {event_type.value}")
    
    async def get_event_statistics(self) -> Dict[str, Any]:
        """Get event processing statistics"""
        return {
            'events_processed': self.events_processed,
            'events_failed': self.events_failed,
            'avg_processing_time': round(self.avg_processing_time, 3),
            'queue_size': self.event_queue.qsize(),
            'is_processing': self.is_processing,
            'total_events': len(self.event_history)
        }
    
    async def get_recent_events(
        self,
        limit: int = 100,
        event_type: Optional[EventType] = None,
        severity: Optional[EventSeverity] = None
    ) -> List[FederatedLearningEvent]:
        """Get recent events with optional filtering"""
        events = self.event_history[-limit:] if limit > 0 else self.event_history
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if severity:
            events = [e for e in events if e.severity == severity]
        
        return events


