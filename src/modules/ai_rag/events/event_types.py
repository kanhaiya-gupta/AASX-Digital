"""
Event Types for AI RAG Module.

This module defines all the event types that can occur in the AI RAG system,
including document processing events, graph generation events, and integration events.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class EventPriority(Enum):
    """Event priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class EventStatus(Enum):
    """Event processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EventCategory(Enum):
    """Event categories for organization."""
    DOCUMENT_PROCESSING = "document_processing"
    GRAPH_GENERATION = "graph_generation"
    KG_INTEGRATION = "kg_integration"
    PERFORMANCE_MONITORING = "performance_monitoring"
    SYSTEM_HEALTH = "system_health"
    INTEGRATION = "integration"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class BaseEvent(BaseModel):
    """Base event model with common fields."""
    
    event_id: str = Field(..., description="Unique event identifier")
    event_type: str = Field(..., description="Type of event")
    event_category: EventCategory = Field(..., description="Event category")
    priority: EventPriority = Field(default=EventPriority.NORMAL, description="Event priority")
    status: EventStatus = Field(default=EventStatus.PENDING, description="Event status")
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Event creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Event processing start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Event completion timestamp")
    
    # Context
    project_id: Optional[str] = Field(None, description="Associated project ID")
    org_id: Optional[str] = Field(None, description="Organization ID")
    dept_id: Optional[str] = Field(None, description="Department ID")
    user_id: Optional[str] = Field(None, description="User who triggered the event")
    
    # Metadata
    source: str = Field(..., description="Event source component")
    target: Optional[str] = Field(None, description="Event target component")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional event metadata")
    
    # Processing
    retry_count: int = Field(default=0, description="Number of retry attempts")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    stack_trace: Optional[str] = Field(None, description="Stack trace if failed")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Document Processing Events
class DocumentProcessingEvent(BaseEvent):
    """Event for document processing operations."""
    
    file_path: str = Field(..., description="Path to the document file")
    file_type: str = Field(..., description="Type of document file")
    file_size: int = Field(..., description="Size of the document file in bytes")
    processor_type: str = Field(..., description="Type of processor used")
    processing_config: Dict[str, Any] = Field(default_factory=dict, description="Processing configuration")
    extracted_content: Optional[str] = Field(None, description="Extracted content from document")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    quality_score: Optional[float] = Field(None, description="Processing quality score")


class DocumentProcessingCompletedEvent(DocumentProcessingEvent):
    """Event when document processing is completed."""
    
    entities_extracted: int = Field(..., description="Number of entities extracted")
    relationships_found: int = Field(..., description="Number of relationships found")
    confidence_score: float = Field(..., description="Overall confidence score")
    output_format: str = Field(..., description="Output format of processed document")


class DocumentProcessingFailedEvent(DocumentProcessingEvent):
    """Event when document processing fails."""
    
    error_message: str = Field(..., description="Error message describing the failure")
    error_code: Optional[str] = Field(None, description="Error code for categorization")
    failure_reason: Optional[str] = Field(None, description="Reason for failure")
    retry_count: int = Field(default=0, description="Number of retry attempts")


# Graph Generation Events
class GraphGenerationEvent(BaseEvent):
    """Event for graph generation operations."""
    
    graph_type: str = Field(..., description="Type of graph being generated")
    source_data: str = Field(..., description="Source data for graph generation")
    generation_config: Dict[str, Any] = Field(default_factory=dict, description="Generation configuration")
    expected_nodes: Optional[int] = Field(None, description="Expected number of nodes")
    expected_edges: Optional[int] = Field(None, description="Expected number of edges")


class GraphGenerationStartedEvent(GraphGenerationEvent):
    """Event when graph generation starts."""
    
    generation_id: str = Field(..., description="Unique generation identifier")
    start_time: datetime = Field(default_factory=datetime.utcnow, description="Generation start time")


class GraphGenerationCompletedEvent(GraphGenerationEvent):
    """Event when graph generation completes successfully."""
    
    nodes_created: int = Field(..., description="Number of nodes created")
    edges_created: int = Field(..., description="Number of edges created")
    generation_duration_ms: float = Field(..., description="Generation duration in milliseconds")
    quality_score: Optional[float] = Field(None, description="Generated graph quality score")


class GraphGenerationFailedEvent(GraphGenerationEvent):
    """Event when graph generation fails."""
    
    error_message: str = Field(..., description="Error message describing the failure")
    error_code: Optional[str] = Field(None, description="Error code for categorization")
    failure_stage: Optional[str] = Field(None, description="Stage where generation failed")


# Knowledge Graph Integration Events
class KGIntegrationEvent(BaseEvent):
    """Event for knowledge graph integration operations."""
    
    integration_type: str = Field(..., description="Type of integration operation")
    source_system: str = Field(..., description="Source system for integration")
    target_system: str = Field(..., description="Target system for integration")
    integration_config: Dict[str, Any] = Field(default_factory=dict, description="Integration configuration")


# Graph Transfer Events
class GraphTransferEvent(BaseEvent):
    """Event for graph transfer operations."""
    
    source_graph: str = Field(..., description="Source graph identifier")
    target_graph: str = Field(..., description="Target graph identifier")
    transfer_type: str = Field(..., description="Type of transfer operation")
    transfer_config: Dict[str, Any] = Field(default_factory=dict, description="Transfer configuration")


class GraphTransferCompletedEvent(GraphTransferEvent):
    """Event when graph transfer completes successfully."""
    
    nodes_transferred: int = Field(..., description="Number of nodes transferred")
    edges_transferred: int = Field(..., description="Number of edges transferred")
    transfer_duration_ms: float = Field(..., description="Transfer duration in milliseconds")
    transfer_size_mb: Optional[float] = Field(None, description="Transfer size in megabytes")


class GraphTransferFailedEvent(GraphTransferEvent):
    """Event when graph transfer fails."""
    
    error_message: str = Field(..., description="Error message describing the failure")
    error_code: Optional[str] = Field(None, description="Error code for categorization")
    failure_stage: Optional[str] = Field(None, description="Stage where transfer failed")


# Graph Synchronization Events
class GraphSyncEvent(BaseEvent):
    """Event for graph synchronization operations."""
    
    sync_type: str = Field(..., description="Type of synchronization operation")
    source_system: str = Field(..., description="Source system for synchronization")
    target_system: str = Field(..., description="Target system for synchronization")
    sync_config: Dict[str, Any] = Field(default_factory=dict, description="Synchronization configuration")


class GraphSyncCompletedEvent(GraphSyncEvent):
    """Event when graph synchronization completes successfully."""
    
    sync_duration_ms: float = Field(..., description="Synchronization duration in milliseconds")
    nodes_synced: Optional[int] = Field(None, description="Number of nodes synchronized")
    edges_synced: Optional[int] = Field(None, description="Number of edges synchronized")
    sync_status: str = Field(default="completed", description="Synchronization status")


class GraphSyncFailedEvent(GraphSyncEvent):
    """Event when graph synchronization fails."""
    
    error_message: str = Field(..., description="Error message describing the failure")
    error_code: Optional[str] = Field(None, description="Error code for categorization")
    failure_stage: Optional[str] = Field(None, description="Stage where synchronization failed")


# Graph Lifecycle Events
class GraphLifecycleEvent(BaseEvent):
    """Event for graph lifecycle operations."""
    
    lifecycle_phase: str = Field(..., description="Current lifecycle phase")
    graph_id: str = Field(..., description="Graph identifier")
    phase_data: Dict[str, Any] = Field(default_factory=dict, description="Phase-specific data")
    transition_reason: Optional[str] = Field(None, description="Reason for phase transition")


# Performance Monitoring Events
class PerformanceEvent(BaseEvent):
    """Event for performance monitoring."""
    
    metric_name: str = Field(..., description="Name of the performance metric")
    metric_value: float = Field(..., description="Value of the performance metric")
    metric_unit: str = Field(..., description="Unit of measurement for the metric")
    threshold_value: Optional[float] = Field(None, description="Threshold value for the metric")


class PerformanceThresholdExceededEvent(PerformanceEvent):
    """Event when performance threshold is exceeded."""
    
    threshold_value: float = Field(..., description="Threshold value that was exceeded")
    severity_level: str = Field(default="warning", description="Severity level of the threshold breach")
    recommended_action: Optional[str] = Field(None, description="Recommended action to resolve the issue")


# System Health Events
class SystemHealthEvent(BaseEvent):
    """Event for system health monitoring."""
    
    health_status: str = Field(..., description="Current health status")
    health_score: float = Field(..., description="Numerical health score (0-100)")
    health_indicators: Dict[str, Any] = Field(default_factory=dict, description="Health indicators and metrics")


class SystemHealthChangedEvent(SystemHealthEvent):
    """Event when system health status changes."""
    
    previous_status: str = Field(..., description="Previous health status")
    previous_score: float = Field(..., description="Previous health score")
    change_reason: Optional[str] = Field(None, description="Reason for health status change")


# Integration Events
class IntegrationEvent(BaseEvent):
    """Event for system integration operations."""
    
    integration_type: str = Field(..., description="Type of integration operation")
    source_system: str = Field(..., description="Source system for integration")
    target_system: str = Field(..., description="Target system for integration")
    integration_config: Dict[str, Any] = Field(default_factory=dict, description="Integration configuration")


class IntegrationSuccessEvent(IntegrationEvent):
    """Event when integration operation succeeds."""
    
    integration_duration_ms: Optional[float] = Field(None, description="Integration duration in milliseconds")
    data_transferred: Optional[int] = Field(None, description="Amount of data transferred")
    success_metrics: Dict[str, Any] = Field(default_factory=dict, description="Success-related metrics")


class IntegrationFailureEvent(IntegrationEvent):
    """Event when integration operation fails."""
    
    error_message: str = Field(..., description="Error message describing the failure")
    error_code: Optional[str] = Field(None, description="Error code for categorization")
    failure_stage: Optional[str] = Field(None, description="Stage where integration failed")
    retry_attempts: int = Field(default=0, description="Number of retry attempts made")


# Error and Warning Events
class ErrorEvent(BaseEvent):
    """Event for error conditions."""
    
    error_code: str = Field(..., description="Error code identifier")
    error_type: str = Field(..., description="Type of error")
    error_message: str = Field(..., description="Error message")
    error_context: Dict[str, Any] = Field(default_factory=dict, description="Error context information")
    stack_trace: Optional[str] = Field(None, description="Stack trace for debugging")


class WarningEvent(BaseEvent):
    """Event for warning conditions."""
    
    warning_level: str = Field(..., description="Warning level (low, medium, high)")
    warning_code: str = Field(..., description="Warning code identifier")
    warning_details: Dict[str, Any] = Field(default_factory=dict, description="Warning details")
    recommended_action: Optional[str] = Field(None, description="Recommended action to resolve warning")


# External API Events
class ExternalAPIEvent(BaseEvent):
    """Event for external API interactions."""
    
    api_endpoint: str = Field(..., description="API endpoint URL")
    api_method: str = Field(..., description="HTTP method used")
    request_payload: Optional[Dict[str, Any]] = Field(None, description="Request payload")
    response_status: Optional[int] = Field(None, description="HTTP response status")
    response_data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    execution_time_ms: Optional[float] = Field(None, description="API execution time in milliseconds")


# Webhook Events
class WebhookEvent(BaseEvent):
    """Event for webhook interactions."""
    
    webhook_url: str = Field(..., description="Webhook URL")
    webhook_type: str = Field(..., description="Type of webhook (incoming, outgoing)")
    payload: Dict[str, Any] = Field(..., description="Webhook payload")
    headers: Dict[str, str] = Field(default_factory=dict, description="HTTP headers")
    response_status: Optional[int] = Field(None, description="Response status code")
    retry_count: int = Field(default=0, description="Number of retry attempts")


# Event Factory
class EventFactory:
    """Factory for creating events with proper configuration."""
    
    @staticmethod
    def create_document_processing_event(
        file_path: str,
        file_type: str,
        file_size: int,
        processor_type: str,
        **kwargs
    ) -> DocumentProcessingEvent:
        """Create a document processing event."""
        return DocumentProcessingEvent(
            event_id=str(uuid.uuid4()),
            event_type="document_processing",
            event_category=EventCategory.DOCUMENT_PROCESSING,
            source="document_processor",
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            processor_type=processor_type,
            **kwargs
        )
    
    @staticmethod
    def create_document_processing_completed_event(
        file_path: str,
        file_type: str,
        file_size: int,
        processor_type: str,
        entities_extracted: int,
        relationships_found: int,
        **kwargs
    ) -> DocumentProcessingCompletedEvent:
        """Create a document processing completed event."""
        return DocumentProcessingCompletedEvent(
            event_id=str(uuid.uuid4()),
            event_type="document_processing_completed",
            event_category=EventCategory.DOCUMENT_PROCESSING,
            status=EventStatus.COMPLETED,
            source="document_processor",
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            processor_type=processor_type,
            entities_extracted=entities_extracted,
            relationships_found=relationships_found,
            **kwargs
        )
    
    @staticmethod
    def create_document_processing_failed_event(
        file_path: str,
        file_type: str,
        file_size: int,
        processor_type: str,
        error_message: str,
        **kwargs
    ) -> DocumentProcessingFailedEvent:
        """Create a document processing failed event."""
        return DocumentProcessingFailedEvent(
            event_id=str(uuid.uuid4()),
            event_type="document_processing_failed",
            event_category=EventCategory.DOCUMENT_PROCESSING,
            status=EventStatus.FAILED,
            source="document_processor",
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            processor_type=processor_type,
            error_message=error_message,
            **kwargs
        )
    
    @staticmethod
    def create_graph_generation_event(
        graph_type: str,
        source_data: str,
        **kwargs
    ) -> GraphGenerationEvent:
        """Create a graph generation event."""
        return GraphGenerationEvent(
            event_id=str(uuid.uuid4()),
            event_type="graph_generation",
            event_category=EventCategory.GRAPH_GENERATION,
            source="graph_generator",
            graph_type=graph_type,
            source_data=source_data,
            **kwargs
        )
    
    @staticmethod
    def create_graph_generation_started_event(
        graph_type: str,
        source_data: str,
        **kwargs
    ) -> GraphGenerationStartedEvent:
        """Create a graph generation started event."""
        return GraphGenerationStartedEvent(
            event_id=str(uuid.uuid4()),
            event_type="graph_generation_started",
            event_category=EventCategory.GRAPH_GENERATION,
            status=EventStatus.PROCESSING,
            source="graph_generator",
            graph_type=graph_type,
            source_data=source_data,
            **kwargs
        )
    
    @staticmethod
    def create_graph_generation_completed_event(
        graph_type: str,
        source_data: str,
        nodes_created: int,
        edges_created: int,
        **kwargs
    ) -> GraphGenerationCompletedEvent:
        """Create a graph generation completed event."""
        return GraphGenerationCompletedEvent(
            event_id=str(uuid.uuid4()),
            event_type="graph_generation_completed",
            event_category=EventCategory.GRAPH_GENERATION,
            status=EventStatus.COMPLETED,
            source="graph_generator",
            graph_type=graph_type,
            source_data=source_data,
            nodes_created=nodes_created,
            edges_created=edges_created,
            **kwargs
        )
    
    @staticmethod
    def create_graph_generation_failed_event(
        graph_type: str,
        source_data: str,
        error_message: str,
        **kwargs
    ) -> GraphGenerationFailedEvent:
        """Create a graph generation failed event."""
        return GraphGenerationFailedEvent(
            event_id=str(uuid.uuid4()),
            event_type="graph_generation_failed",
            event_category=EventCategory.GRAPH_GENERATION,
            status=EventStatus.FAILED,
            source="graph_generator",
            graph_type=graph_type,
            source_data=source_data,
            error_message=error_message,
            **kwargs
        )
    
    @staticmethod
    def create_kg_integration_event(
        integration_type: str,
        source_system: str,
        target_system: str,
        **kwargs
    ) -> KGIntegrationEvent:
        """Create a knowledge graph integration event."""
        return KGIntegrationEvent(
            event_id=str(uuid.uuid4()),
            event_type="kg_integration",
            event_category=EventCategory.KG_INTEGRATION,
            source="kg_integrator",
            integration_type=integration_type,
            source_system=source_system,
            target_system=target_system,
            **kwargs
        )
    
    @staticmethod
    def create_graph_transfer_event(
        source_graph: str,
        target_graph: str,
        transfer_type: str,
        **kwargs
    ) -> GraphTransferEvent:
        """Create a graph transfer event."""
        return GraphTransferEvent(
            event_id=str(uuid.uuid4()),
            event_type="graph_transfer",
            event_category=EventCategory.KG_INTEGRATION,
            source="graph_transfer",
            source_graph=source_graph,
            target_graph=target_graph,
            transfer_type=transfer_type,
            **kwargs
        )
    
    @staticmethod
    def create_graph_transfer_completed_event(
        source_graph: str,
        target_graph: str,
        transfer_type: str,
        nodes_transferred: int,
        edges_transferred: int,
        **kwargs
    ) -> GraphTransferCompletedEvent:
        """Create a graph transfer completed event."""
        return GraphTransferCompletedEvent(
            event_id=str(uuid.uuid4()),
            event_type="graph_transfer_completed",
            event_category=EventCategory.KG_INTEGRATION,
            status=EventStatus.COMPLETED,
            source="graph_transfer",
            source_graph=source_graph,
            target_graph=target_graph,
            transfer_type=transfer_type,
            nodes_transferred=nodes_transferred,
            edges_transferred=edges_transferred,
            **kwargs
        )
    
    @staticmethod
    def create_graph_transfer_failed_event(
        source_graph: str,
        target_graph: str,
        transfer_type: str,
        error_message: str,
        **kwargs
    ) -> GraphTransferFailedEvent:
        """Create a graph transfer failed event."""
        return GraphTransferFailedEvent(
            event_id=str(uuid.uuid4()),
            event_type="graph_transfer_failed",
            event_category=EventCategory.KG_INTEGRATION,
            status=EventStatus.FAILED,
            source="graph_transfer",
            source_graph=source_graph,
            target_graph=target_graph,
            transfer_type=transfer_type,
            error_message=error_message,
            **kwargs
        )
    
    @staticmethod
    def create_graph_sync_event(
        sync_type: str,
        source_system: str,
        target_system: str,
        **kwargs
    ) -> GraphSyncEvent:
        """Create a graph synchronization event."""
        return GraphSyncEvent(
            event_id=str(uuid.uuid4()),
            event_type="graph_sync",
            event_category=EventCategory.KG_INTEGRATION,
            source="graph_sync",
            sync_type=sync_type,
            source_system=source_system,
            target_system=target_system,
            **kwargs
        )
    
    @staticmethod
    def create_graph_sync_completed_event(
        sync_type: str,
        source_system: str,
        target_system: str,
        sync_duration_ms: float,
        **kwargs
    ) -> GraphSyncCompletedEvent:
        """Create a graph synchronization completed event."""
        return GraphSyncCompletedEvent(
            event_id=str(uuid.uuid4()),
            event_type="graph_sync_completed",
            event_category=EventCategory.KG_INTEGRATION,
            status=EventStatus.COMPLETED,
            source="graph_sync",
            sync_type=sync_type,
            source_system=source_system,
            target_system=target_system,
            sync_duration_ms=sync_duration_ms,
            **kwargs
        )
    
    @staticmethod
    def create_graph_sync_failed_event(
        sync_type: str,
        source_system: str,
        target_system: str,
        error_message: str,
        **kwargs
    ) -> GraphSyncFailedEvent:
        """Create a graph synchronization failed event."""
        return GraphSyncFailedEvent(
            event_id=str(uuid.uuid4()),
            event_type="graph_sync_failed",
            event_category=EventCategory.KG_INTEGRATION,
            status=EventStatus.FAILED,
            source="graph_sync",
            sync_type=sync_type,
            source_system=source_system,
            target_system=target_system,
            error_message=error_message,
            **kwargs
        )
    
    @staticmethod
    def create_graph_lifecycle_event(
        lifecycle_phase: str,
        graph_id: str,
        **kwargs
    ) -> GraphLifecycleEvent:
        """Create a graph lifecycle event."""
        return GraphLifecycleEvent(
            event_id=str(uuid.uuid4()),
            event_type="graph_lifecycle",
            event_category=EventCategory.KG_INTEGRATION,
            source="graph_lifecycle",
            lifecycle_phase=lifecycle_phase,
            graph_id=graph_id,
            **kwargs
        )
    
    @staticmethod
    def create_performance_event(
        metric_name: str,
        metric_value: float,
        metric_unit: str,
        **kwargs
    ) -> PerformanceEvent:
        """Create a performance monitoring event."""
        return PerformanceEvent(
            event_id=str(uuid.uuid4()),
            event_type="performance",
            event_category=EventCategory.PERFORMANCE_MONITORING,
            source="performance_monitor",
            metric_name=metric_name,
            metric_value=metric_value,
            metric_unit=metric_unit,
            **kwargs
        )
    
    @staticmethod
    def create_performance_threshold_exceeded_event(
        metric_name: str,
        metric_value: float,
        threshold_value: float,
        metric_unit: str,
        **kwargs
    ) -> PerformanceThresholdExceededEvent:
        """Create a performance threshold exceeded event."""
        return PerformanceThresholdExceededEvent(
            event_id=str(uuid.uuid4()),
            event_type="performance_threshold_exceeded",
            event_category=EventCategory.PERFORMANCE_MONITORING,
            priority=EventPriority.HIGH,
            source="performance_monitor",
            metric_name=metric_name,
            metric_value=metric_value,
            threshold_value=threshold_value,
            metric_unit=metric_unit,
            **kwargs
        )
    
    @staticmethod
    def create_system_health_event(
        health_status: str,
        health_score: float,
        **kwargs
    ) -> SystemHealthEvent:
        """Create a system health event."""
        return SystemHealthEvent(
            event_id=str(uuid.uuid4()),
            event_type="system_health",
            event_category=EventCategory.SYSTEM_HEALTH,
            source="health_monitor",
            health_status=health_status,
            health_score=health_score,
            **kwargs
        )
    
    @staticmethod
    def create_system_health_changed_event(
        previous_status: str,
        current_status: str,
        previous_score: float,
        current_score: float,
        **kwargs
    ) -> SystemHealthChangedEvent:
        """Create a system health changed event."""
        return SystemHealthChangedEvent(
            event_id=str(uuid.uuid4()),
            event_type="system_health_changed",
            event_category=EventCategory.SYSTEM_HEALTH,
            source="health_monitor",
            previous_status=previous_status,
            current_status=current_status,
            previous_score=previous_score,
            current_score=current_score,
            **kwargs
        )
    
    @staticmethod
    def create_integration_event(
        integration_type: str,
        source_system: str,
        target_system: str,
        **kwargs
    ) -> IntegrationEvent:
        """Create an integration event."""
        return IntegrationEvent(
            event_id=str(uuid.uuid4()),
            event_type="integration",
            event_category=EventCategory.INTEGRATION,
            source="integration_manager",
            integration_type=integration_type,
            source_system=source_system,
            target_system=target_system,
            **kwargs
        )
    
    @staticmethod
    def create_integration_success_event(
        integration_type: str,
        source_system: str,
        target_system: str,
        **kwargs
    ) -> IntegrationSuccessEvent:
        """Create an integration success event."""
        return IntegrationSuccessEvent(
            event_id=str(uuid.uuid4()),
            event_type="integration_success",
            event_category=EventCategory.INTEGRATION,
            status=EventStatus.COMPLETED,
            source="integration_manager",
            integration_type=integration_type,
            source_system=source_system,
            target_system=target_system,
            **kwargs
        )
    
    @staticmethod
    def create_integration_failure_event(
        integration_type: str,
        source_system: str,
        target_system: str,
        error_message: str,
        **kwargs
    ) -> IntegrationFailureEvent:
        """Create an integration failure event."""
        return IntegrationFailureEvent(
            event_id=str(uuid.uuid4()),
            event_type="integration_failure",
            event_category=EventCategory.INTEGRATION,
            status=EventStatus.FAILED,
            source="integration_manager",
            integration_type=integration_type,
            source_system=source_system,
            target_system=target_system,
            error_message=error_message,
            **kwargs
        )
    
    @staticmethod
    def create_error_event(
        error_code: str,
        error_type: str,
        error_message: str,
        **kwargs
    ) -> ErrorEvent:
        """Create an error event."""
        return ErrorEvent(
            event_id=str(uuid.uuid4()),
            event_type="error",
            event_category=EventCategory.ERROR,
            priority=EventPriority.HIGH,
            status=EventStatus.FAILED,
            source="error_handler",
            error_code=error_code,
            error_type=error_type,
            error_message=error_message,
            **kwargs
        )
    
    @staticmethod
    def create_warning_event(
        warning_level: str,
        warning_code: str,
        warning_message: str,
        **kwargs
    ) -> WarningEvent:
        """Create a warning event."""
        return WarningEvent(
            event_id=str(uuid.uuid4()),
            event_type="warning",
            event_category=EventCategory.WARNING,
            priority=EventPriority.NORMAL,
            source="warning_handler",
            warning_level=warning_level,
            warning_code=warning_code,
            warning_message=warning_message,
            **kwargs
        )
    
    @staticmethod
    def create_external_api_event(
        api_endpoint: str,
        api_method: str,
        **kwargs
    ) -> ExternalAPIEvent:
        """Create an external API event."""
        return ExternalAPIEvent(
            event_id=str(uuid.uuid4()),
            event_type="external_api",
            event_category=EventCategory.INTEGRATION,
            source="external_api_client",
            api_endpoint=api_endpoint,
            api_method=api_method,
            **kwargs
        )


# Webhook Events
class WebhookEvent(BaseEvent):
    """Event for webhook interactions."""
    
    webhook_url: str = Field(..., description="Webhook URL")
    webhook_type: str = Field(..., description="Type of webhook (incoming, outgoing)")
    payload: Dict[str, Any] = Field(..., description="Webhook payload")
    headers: Dict[str, str] = Field(default_factory=dict, description="HTTP headers")
    response_status: Optional[int] = Field(None, description="Response status code")
    retry_count: int = Field(default=0, description="Number of retry attempts")


# Event type registry for easy lookup
EVENT_TYPE_REGISTRY = {
    "document_processing": DocumentProcessingEvent,
    "document_processing_completed": DocumentProcessingCompletedEvent,
    "document_processing_failed": DocumentProcessingFailedEvent,
    "graph_generation": GraphGenerationEvent,
    "graph_generation_started": GraphGenerationStartedEvent,
    "graph_generation_completed": GraphGenerationCompletedEvent,
    "graph_generation_failed": GraphGenerationFailedEvent,
    "kg_integration": KGIntegrationEvent,
    "graph_transfer": GraphTransferEvent,
    "graph_transfer_completed": GraphTransferCompletedEvent,
    "graph_transfer_failed": GraphTransferFailedEvent,
    "graph_sync": GraphSyncEvent,
    "graph_sync_completed": GraphSyncCompletedEvent,
    "graph_sync_failed": GraphSyncFailedEvent,
    "graph_lifecycle": GraphLifecycleEvent,
    "performance": PerformanceEvent,
    "performance_threshold_exceeded": PerformanceThresholdExceededEvent,
    "system_health": SystemHealthEvent,
    "system_health_changed": SystemHealthChangedEvent,
    "integration": IntegrationEvent,
    "integration_success": IntegrationSuccessEvent,
    "integration_failure": IntegrationFailureEvent,
    "error": ErrorEvent,
    "warning": WarningEvent,
    "external_api": ExternalAPIEvent,
}
