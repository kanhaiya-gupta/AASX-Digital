"""
Event Handlers for AI RAG Module.

This module implements event handlers that process different types of events
in the AI RAG system, including document processing, graph generation,
and KG integration events.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import traceback
import json

from .event_types import (
    BaseEvent, EventCategory, EventPriority, EventStatus,
    DocumentProcessingEvent, DocumentProcessingCompletedEvent, DocumentProcessingFailedEvent,
    GraphGenerationEvent, GraphGenerationStartedEvent, GraphGenerationCompletedEvent, GraphGenerationFailedEvent,
    KGIntegrationEvent, GraphTransferEvent, GraphTransferCompletedEvent, GraphTransferFailedEvent,
    PerformanceEvent, ErrorEvent, WarningEvent, EventFactory
)
from .event_bus import EventBus


class BaseEventHandler:
    """Base class for all event handlers."""
    
    def __init__(self, event_bus: EventBus, config: Optional[Dict[str, Any]] = None):
        """Initialize the base event handler."""
        self.event_bus = event_bus
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.handler_id: Optional[str] = None
        self.is_registered = False
    
    async def register(self) -> str:
        """Register this handler with the event bus."""
        if self.is_registered:
            return self.handler_id
        
        self.handler_id = await self.event_bus.subscribe(
            handler_func=self.handle_event,
            event_types=self.get_supported_event_types(),
            event_categories=self.get_supported_event_categories(),
            priority=self.get_handler_priority()
        )
        self.is_registered = True
        self.logger.info(f"Handler registered with ID: {self.handler_id}")
        return self.handler_id
    
    async def unregister(self) -> bool:
        """Unregister this handler from the event bus."""
        if not self.is_registered or not self.handler_id:
            return False
        
        success = await self.event_bus.unsubscribe(self.handler_id)
        if success:
            self.is_registered = False
            self.handler_id = None
            self.logger.info("Handler unregistered successfully")
        
        return success
    
    async def handle_event(self, event: BaseEvent) -> None:
        """Handle an event. Override in subclasses."""
        self.logger.warning(f"Base event handler called for event: {event.event_type}")
    
    def get_supported_event_types(self) -> List[str]:
        """Get list of supported event types. Override in subclasses."""
        return []
    
    def get_supported_event_categories(self) -> List[EventCategory]:
        """Get list of supported event categories. Override in subclasses."""
        return []
    
    def get_handler_priority(self) -> EventPriority:
        """Get handler priority. Override in subclasses."""
        return EventPriority.NORMAL


class DocumentProcessingEventHandler(BaseEventHandler):
    """Handler for document processing events."""
    
    def __init__(self, event_bus: EventBus, config: Optional[Dict[str, Any]] = None):
        """Initialize the document processing event handler."""
        super().__init__(event_bus, config)
        self.processing_stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "total_processing_time": 0.0,
            "average_processing_time": 0.0
        }
    
    def get_supported_event_types(self) -> List[str]:
        """Get supported event types."""
        return [
            "document_processing",
            "document_processing_completed",
            "document_processing_failed"
        ]
    
    def get_supported_event_categories(self) -> List[EventCategory]:
        """Get supported event categories."""
        return [EventCategory.DOCUMENT_PROCESSING]
    
    def get_handler_priority(self) -> EventPriority:
        """Get handler priority."""
        return EventPriority.HIGH
    
    async def handle_event(self, event: BaseEvent) -> None:
        """Handle document processing events."""
        try:
            if isinstance(event, DocumentProcessingEvent):
                await self._handle_document_processing(event)
            elif isinstance(event, DocumentProcessingCompletedEvent):
                await self._handle_document_processing_completed(event)
            elif isinstance(event, DocumentProcessingFailedEvent):
                await self._handle_document_processing_failed(event)
            else:
                self.logger.warning(f"Unknown document processing event type: {type(event)}")
        
        except Exception as e:
            self.logger.error(f"Error handling document processing event: {e}")
            await self._publish_error_event("DOC_PROC_HANDLER_ERROR", str(e), event)
    
    async def _handle_document_processing(self, event: DocumentProcessingEvent) -> None:
        """Handle document processing started event."""
        self.logger.info(f"Document processing started: {event.file_path}")
        
        # Update processing statistics
        self.processing_stats["total_processed"] += 1
        
        # Log processing details
        self.logger.debug(f"Processing file: {event.file_path}")
        self.logger.debug(f"File type: {event.file_type}")
        self.logger.debug(f"File size: {event.file_size} bytes")
        self.logger.debug(f"Processor: {event.processor_type}")
        
        # Additional processing logic can be added here
        # For example, updating database status, sending notifications, etc.
    
    async def _handle_document_processing_completed(self, event: DocumentProcessingCompletedEvent) -> None:
        """Handle document processing completed event."""
        self.logger.info(f"Document processing completed: {event.file_path}")
        
        # Update processing statistics
        self.processing_stats["successful"] += 1
        if event.processing_time:
            self.processing_stats["total_processing_time"] += event.processing_time
            self.processing_stats["average_processing_time"] = (
                self.processing_stats["total_processing_time"] / self.processing_stats["successful"]
            )
        
        # Log completion details
        self.logger.info(f"Entities extracted: {event.entities_extracted}")
        self.logger.info(f"Relationships found: {event.relationships_found}")
        self.logger.info(f"Confidence score: {event.confidence_score}")
        self.logger.info(f"Output format: {event.output_format}")
        
        # Trigger graph generation if entities were extracted
        if event.entities_extracted > 0:
            await self._trigger_graph_generation(event)
    
    async def _handle_document_processing_failed(self, event: DocumentProcessingFailedEvent) -> None:
        """Handle document processing failed event."""
        self.logger.error(f"Document processing failed: {event.file_path}")
        
        # Update processing statistics
        self.processing_stats["failed"] += 1
        
        # Log failure details
        self.logger.error(f"Failure reason: {event.failure_reason}")
        if event.failure_code:
            self.logger.error(f"Failure code: {event.failure_code}")
        if event.suggested_action:
            self.logger.info(f"Suggested action: {event.suggested_action}")
        
        # Additional failure handling logic can be added here
        # For example, retry logic, error reporting, etc.
    
    async def _trigger_graph_generation(self, event: DocumentProcessingCompletedEvent) -> None:
        """Trigger graph generation for successfully processed document."""
        try:
            # Create graph generation event
            graph_event = EventFactory.create_graph_generation_event(
                content_source=event.file_path,
                content_type=event.file_type,
                project_id=event.project_id,
                org_id=event.org_id,
                dept_id=event.dept_id,
                user_id=event.user_id,
                graph_config={
                    "entities_extracted": event.entities_extracted,
                    "relationships_found": event.relationships_found,
                    "confidence_score": event.confidence_score,
                    "source_processor": event.processor_type
                }
            )
            
            # Publish graph generation event
            await self.event_bus.publish_event(graph_event)
            self.logger.info(f"Graph generation triggered for: {event.file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to trigger graph generation: {e}")
    
    async def _publish_error_event(self, error_code: str, error_message: str, original_event: BaseEvent) -> None:
        """Publish an error event."""
        try:
            error_event = EventFactory.create_error_event(
                error_code=error_code,
                error_type="handler_error",
                error_message=error_message,
                project_id=original_event.project_id,
                org_id=original_event.org_id,
                dept_id=original_event.dept_id,
                user_id=original_event.user_id,
                error_context={
                    "original_event_id": original_event.event_id,
                    "original_event_type": original_event.event_type,
                    "handler_class": self.__class__.__name__
                },
                user_impact="Document processing may be affected",
                resolution_steps=[
                    "Check handler logs for detailed error information",
                    "Verify event data format and content",
                    "Check system resources and dependencies"
                ]
            )
            
            await self.event_bus.publish_event(error_event)
            
        except Exception as e:
            self.logger.error(f"Failed to publish error event: {e}")
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics."""
        return self.processing_stats.copy()


class GraphGenerationEventHandler(BaseEventHandler):
    """Handler for graph generation events."""
    
    def __init__(self, event_bus: EventBus, config: Optional[Dict[str, Any]] = None):
        """Initialize the graph generation event handler."""
        super().__init__(event_bus, config)
        self.generation_stats = {
            "total_generated": 0,
            "successful": 0,
            "failed": 0,
            "total_generation_time": 0.0,
            "average_generation_time": 0.0,
            "total_nodes_created": 0,
            "total_edges_created": 0
        }
    
    def get_supported_event_types(self) -> List[str]:
        """Get supported event types."""
        return [
            "graph_generation",
            "graph_generation_started",
            "graph_generation_completed",
            "graph_generation_failed"
        ]
    
    def get_supported_event_categories(self) -> List[EventCategory]:
        """Get supported event categories."""
        return [EventCategory.GRAPH_GENERATION]
    
    def get_handler_priority(self) -> EventPriority:
        """Get handler priority."""
        return EventPriority.HIGH
    
    async def handle_event(self, event: BaseEvent) -> None:
        """Handle graph generation events."""
        try:
            if isinstance(event, GraphGenerationEvent):
                await self._handle_graph_generation(event)
            elif isinstance(event, GraphGenerationStartedEvent):
                await self._handle_graph_generation_started(event)
            elif isinstance(event, GraphGenerationCompletedEvent):
                await self._handle_graph_generation_completed(event)
            elif isinstance(event, GraphGenerationFailedEvent):
                await self._handle_graph_generation_failed(event)
            else:
                self.logger.warning(f"Unknown graph generation event type: {type(event)}")
        
        except Exception as e:
            self.logger.error(f"Error handling graph generation event: {e}")
            await self._publish_error_event("GRAPH_GEN_HANDLER_ERROR", str(e), event)
    
    async def _handle_graph_generation(self, event: GraphGenerationEvent) -> None:
        """Handle graph generation event."""
        self.logger.info(f"Graph generation event received for: {event.content_source}")
        
        # Log generation details
        self.logger.debug(f"Content source: {event.content_source}")
        self.logger.debug(f"Content type: {event.content_type}")
        self.logger.debug(f"Expected nodes: {event.expected_nodes}")
        self.logger.debug(f"Expected edges: {event.expected_edges}")
        
        # Additional processing logic can be added here
    
    async def _handle_graph_generation_started(self, event: GraphGenerationStartedEvent) -> None:
        """Handle graph generation started event."""
        self.logger.info(f"Graph generation started for: {event.content_source}")
        
        # Log configuration details
        self.logger.debug(f"Extraction config: {event.extraction_config}")
        self.logger.debug(f"Discovery config: {event.discovery_config}")
        self.logger.debug(f"Builder config: {event.builder_config}")
        
        # Additional processing logic can be added here
    
    async def _handle_graph_generation_completed(self, event: GraphGenerationCompletedEvent) -> None:
        """Handle graph generation completed event."""
        self.logger.info(f"Graph generation completed for: {event.content_source}")
        
        # Update generation statistics
        self.generation_stats["total_generated"] += 1
        self.generation_stats["successful"] += 1
        self.generation_stats["total_nodes_created"] += event.nodes_created
        self.generation_stats["total_edges_created"] += event.edges_created
        
        # Log completion details
        self.logger.info(f"Nodes created: {event.nodes_created}")
        self.logger.info(f"Edges created: {event.edges_created}")
        self.logger.info(f"Graph quality score: {event.graph_quality_score}")
        self.logger.info(f"Validation passed: {event.validation_passed}")
        self.logger.info(f"Export formats: {event.export_formats}")
        self.logger.info(f"Output directory: {event.output_directory}")
        
        # Trigger KG integration if validation passed
        if event.validation_passed:
            await self._trigger_kg_integration(event)
    
    async def _handle_graph_generation_failed(self, event: GraphGenerationFailedEvent) -> None:
        """Handle graph generation failed event."""
        self.logger.error(f"Graph generation failed for: {event.content_source}")
        
        # Update generation statistics
        self.generation_stats["total_generated"] += 1
        self.generation_stats["failed"] += 1
        
        # Log failure details
        self.logger.error(f"Failure stage: {event.failure_stage}")
        self.logger.error(f"Failure reason: {event.failure_reason}")
        if event.partial_results:
            self.logger.info(f"Partial results available: {event.partial_results}")
        
        # Additional failure handling logic can be added here
    
    async def _trigger_kg_integration(self, event: GraphGenerationCompletedEvent) -> None:
        """Trigger KG Neo4j integration for successfully generated graph."""
        try:
            # Create KG integration event
            kg_event = EventFactory.create_kg_integration_event(
                graph_id=event.event_id,  # Use event ID as graph ID for now
                integration_type="transfer",
                project_id=event.project_id,
                org_id=event.org_id,
                dept_id=event.dept_id,
                user_id=event.user_id,
                graph_metadata={
                    "nodes_count": event.nodes_created,
                    "edges_count": event.edges_created,
                    "quality_score": event.graph_quality_score,
                    "output_directory": event.output_directory,
                    "export_formats": event.export_formats
                }
            )
            
            # Publish KG integration event
            await self.event_bus.publish_event(kg_event)
            self.logger.info(f"KG integration triggered for graph: {event.event_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to trigger KG integration: {e}")
    
    async def _publish_error_event(self, error_code: str, error_message: str, original_event: BaseEvent) -> None:
        """Publish an error event."""
        try:
            error_event = EventFactory.create_error_event(
                error_code=error_code,
                error_type="handler_error",
                error_message=error_message,
                project_id=original_event.project_id,
                org_id=original_event.org_id,
                dept_id=original_event.dept_id,
                user_id=original_event.user_id,
                error_context={
                    "original_event_id": original_event.event_id,
                    "original_event_type": original_event.event_type,
                    "handler_class": self.__class__.__name__
                },
                user_impact="Graph generation may be affected",
                resolution_steps=[
                    "Check handler logs for detailed error information",
                    "Verify event data format and content",
                    "Check graph generation pipeline status"
                ]
            )
            
            await self.event_bus.publish_event(error_event)
            
        except Exception as e:
            self.logger.error(f"Failed to publish error event: {e}")
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get current generation statistics."""
        return self.generation_stats.copy()


class KGIntegrationEventHandler(BaseEventHandler):
    """Handler for KG Neo4j integration events."""
    
    def __init__(self, event_bus: EventBus, config: Optional[Dict[str, Any]] = None):
        """Initialize the KG integration event handler."""
        super().__init__(event_bus, config)
        self.integration_stats = {
            "total_integrations": 0,
            "successful": 0,
            "failed": 0,
            "total_integration_time": 0.0,
            "average_integration_time": 0.0,
            "total_data_transferred": 0
        }
    
    def get_supported_event_types(self) -> List[str]:
        """Get supported event types."""
        return [
            "kg_integration",
            "graph_transfer",
            "graph_transfer_completed",
            "graph_transfer_failed"
        ]
    
    def get_supported_event_categories(self) -> List[EventCategory]:
        """Get supported event categories."""
        return [EventCategory.KG_INTEGRATION]
    
    def get_handler_priority(self) -> EventPriority:
        """Get handler priority."""
        return EventPriority.NORMAL
    
    async def handle_event(self, event: BaseEvent) -> None:
        """Handle KG integration events."""
        try:
            if isinstance(event, KGIntegrationEvent):
                await self._handle_kg_integration(event)
            elif isinstance(event, GraphTransferEvent):
                await self._handle_graph_transfer(event)
            elif isinstance(event, GraphTransferCompletedEvent):
                await self._handle_graph_transfer_completed(event)
            elif isinstance(event, GraphTransferFailedEvent):
                await self._handle_graph_transfer_failed(event)
            else:
                self.logger.warning(f"Unknown KG integration event type: {type(event)}")
        
        except Exception as e:
            self.logger.error(f"Error handling KG integration event: {e}")
            await self._publish_error_event("KG_INT_HANDLER_ERROR", str(e), event)
    
    async def _handle_kg_integration(self, event: KGIntegrationEvent) -> None:
        """Handle KG integration event."""
        self.logger.info(f"KG integration event received for graph: {event.graph_id}")
        
        # Log integration details
        self.logger.debug(f"Graph ID: {event.graph_id}")
        self.logger.debug(f"KG endpoint: {event.kg_endpoint}")
        self.logger.debug(f"Integration type: {event.integration_type}")
        
        # Additional processing logic can be added here
    
    async def _handle_graph_transfer(self, event: GraphTransferEvent) -> None:
        """Handle graph transfer event."""
        self.logger.info(f"Graph transfer started for graph: {event.graph_id}")
        
        # Log transfer details
        self.logger.debug(f"Transfer size: {event.transfer_size}")
        self.logger.debug(f"Transfer format: {event.transfer_format}")
        self.logger.debug(f"Compression enabled: {event.compression_enabled}")
        self.logger.debug(f"Encryption enabled: {event.encryption_enabled}")
        
        # Additional processing logic can be added here
    
    async def _handle_graph_transfer_completed(self, event: GraphTransferCompletedEvent) -> None:
        """Handle graph transfer completed event."""
        self.logger.info(f"Graph transfer completed for graph: {event.graph_id}")
        
        # Update integration statistics
        self.integration_stats["total_integrations"] += 1
        self.integration_stats["successful"] += 1
        self.integration_stats["total_integration_time"] += event.transfer_time
        self.integration_stats["average_integration_time"] = (
            self.integration_stats["total_integration_time"] / self.integration_stats["successful"]
        )
        self.integration_stats["total_data_transferred"] += event.transfer_size
        
        # Log completion details
        self.logger.info(f"Transfer time: {event.transfer_time:.3f}s")
        self.logger.info(f"Transfer speed: {event.transfer_speed:.2f} MB/s")
        self.logger.info(f"KG graph ID: {event.kg_graph_id}")
        self.logger.info(f"Verification passed: {event.verification_passed}")
        
        # Additional completion logic can be added here
    
    async def _handle_graph_transfer_failed(self, event: GraphTransferFailedEvent) -> None:
        """Handle graph transfer failed event."""
        self.logger.error(f"Graph transfer failed for graph: {event.graph_id}")
        
        # Update integration statistics
        self.integration_stats["total_integrations"] += 1
        self.integration_stats["failed"] += 1
        
        # Log failure details
        self.logger.error(f"Failure reason: {event.failure_reason}")
        if event.network_error:
            self.logger.error(f"Network error: {event.network_error}")
        if event.authentication_error:
            self.logger.error(f"Authentication error: {event.authentication_error}")
        
        # Additional failure handling logic can be added here
    
    async def _publish_error_event(self, error_code: str, error_message: str, original_event: BaseEvent) -> None:
        """Publish an error event."""
        try:
            error_event = EventFactory.create_error_event(
                error_code=error_code,
                error_type="handler_error",
                error_message=error_message,
                project_id=original_event.project_id,
                org_id=original_event.org_id,
                dept_id=original_event.dept_id,
                user_id=original_event.user_id,
                error_context={
                    "original_event_id": original_event.event_id,
                    "original_event_type": original_event.event_type,
                    "handler_class": self.__class__.__name__
                },
                user_impact="KG integration may be affected",
                resolution_steps=[
                    "Check handler logs for detailed error information",
                    "Verify KG Neo4j connection and authentication",
                    "Check network connectivity and firewall settings"
                ]
            )
            
            await self.event_bus.publish_event(error_event)
            
        except Exception as e:
            self.logger.error(f"Failed to publish error event: {e}")
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """Get current integration statistics."""
        return self.integration_stats.copy()


class PerformanceMonitoringEventHandler(BaseEventHandler):
    """Handler for performance monitoring events."""
    
    def __init__(self, event_bus: EventBus, config: Optional[Dict[str, Any]] = None):
        """Initialize the performance monitoring event handler."""
        super().__init__(event_bus, config)
        self.performance_metrics = {}
        self.threshold_violations = []
        self.alert_handlers = []
    
    def get_supported_event_types(self) -> List[str]:
        """Get supported event types."""
        return [
            "performance",
            "performance_threshold_exceeded"
        ]
    
    def get_supported_event_categories(self) -> List[EventCategory]:
        """Get supported event categories."""
        return [EventCategory.PERFORMANCE_MONITORING]
    
    def get_handler_priority(self) -> EventPriority:
        """Get handler priority."""
        return EventPriority.LOW
    
    async def handle_event(self, event: BaseEvent) -> None:
        """Handle performance monitoring events."""
        try:
            if isinstance(event, PerformanceEvent):
                await self._handle_performance_event(event)
            else:
                self.logger.warning(f"Unknown performance monitoring event type: {type(event)}")
        
        except Exception as e:
            self.logger.error(f"Error handling performance monitoring event: {e}")
    
    async def _handle_performance_event(self, event: PerformanceEvent) -> None:
        """Handle performance event."""
        # Store metric
        self.performance_metrics[event.metric_name] = {
            "value": event.metric_value,
            "unit": event.metric_unit,
            "timestamp": event.created_at,
            "threshold_exceeded": event.is_threshold_exceeded
        }
        
        # Log metric
        self.logger.debug(f"Performance metric: {event.metric_name} = {event.metric_value} {event.metric_unit}")
        
        # Check for threshold violations
        if event.is_threshold_exceeded:
            await self._handle_threshold_violation(event)
    
    async def _handle_threshold_violation(self, event: PerformanceEvent) -> None:
        """Handle performance threshold violation."""
        violation = {
            "metric_name": event.metric_name,
            "metric_value": event.metric_value,
            "threshold_value": event.threshold_value,
            "timestamp": event.created_at,
            "severity": "warning" if event.metric_value < event.threshold_value * 1.5 else "critical"
        }
        
        self.threshold_violations.append(violation)
        
        # Log violation
        self.logger.warning(f"Performance threshold exceeded: {event.metric_name} = {event.metric_value} {event.metric_unit}")
        if event.threshold_value:
            self.logger.warning(f"Threshold: {event.threshold_value} {event.metric_unit}")
        
        # Trigger alerts
        await self._trigger_alerts(violation)
    
    async def _trigger_alerts(self, violation: Dict[str, Any]) -> None:
        """Trigger performance alerts."""
        # This is a placeholder for alert logic
        # In a real implementation, this could send emails, Slack messages, etc.
        self.logger.warning(f"Performance alert: {violation['metric_name']} threshold exceeded")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self.performance_metrics.copy()
    
    def get_threshold_violations(self) -> List[Dict[str, Any]]:
        """Get threshold violations."""
        return self.threshold_violations.copy()


class EventHandlerManager:
    """Manager for all event handlers."""
    
    def __init__(self, event_bus: EventBus, config: Optional[Dict[str, Any]] = None):
        """Initialize the event handler manager."""
        self.event_bus = event_bus
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize handlers
        self.handlers = {
            "document_processing": DocumentProcessingEventHandler(event_bus, config),
            "graph_generation": GraphGenerationEventHandler(event_bus, config),
            "kg_integration": KGIntegrationEventHandler(event_bus, config),
            "performance_monitoring": PerformanceMonitoringEventHandler(event_bus, config)
        }
        
        self.registered_handlers = {}
    
    async def start_all_handlers(self) -> None:
        """Start all event handlers."""
        self.logger.info("Starting all event handlers...")
        
        for handler_name, handler in self.handlers.items():
            try:
                handler_id = await handler.register()
                self.registered_handlers[handler_name] = handler_id
                self.logger.info(f"Handler {handler_name} started with ID: {handler_id}")
            except Exception as e:
                self.logger.error(f"Failed to start handler {handler_name}: {e}")
    
    async def stop_all_handlers(self) -> None:
        """Stop all event handlers."""
        self.logger.info("Stopping all event handlers...")
        
        for handler_name, handler in self.handlers.items():
            try:
                await handler.unregister()
                self.logger.info(f"Handler {handler_name} stopped")
            except Exception as e:
                self.logger.error(f"Failed to stop handler {handler_name}: {e}")
        
        self.registered_handlers.clear()
    
    def get_handler_stats(self) -> Dict[str, Any]:
        """Get statistics from all handlers."""
        stats = {}
        
        for handler_name, handler in self.handlers.items():
            if hasattr(handler, 'get_processing_stats'):
                stats[f"{handler_name}_processing"] = handler.get_processing_stats()
            if hasattr(handler, 'get_generation_stats'):
                stats[f"{handler_name}_generation"] = handler.get_generation_stats()
            if hasattr(handler, 'get_integration_stats'):
                stats[f"{handler_name}_integration"] = handler.get_integration_stats()
            if hasattr(handler, 'get_performance_metrics'):
                stats[f"{handler_name}_performance"] = handler.get_performance_metrics()
        
        return stats
    
    def get_handler(self, handler_name: str) -> Optional[BaseEventHandler]:
        """Get a specific handler by name."""
        return self.handlers.get(handler_name)
    
    def get_all_handlers(self) -> Dict[str, BaseEventHandler]:
        """Get all handlers."""
        return self.handlers.copy()
