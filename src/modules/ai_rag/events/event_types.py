"""
Event Types for AI RAG Module.

This module defines all the event types that can occur in the AI RAG system,
including document processing events, graph generation events, and integration events.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


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
    
    failure_reason: str = Field(..., description="Reason for processing failure")
    failure_code: Optional[str] = Field(None, description="Failure error code")
    suggested_action: Optional[str] = Field(None, description="Suggested action to resolve")


# Graph Generation Events
class GraphGenerationEvent(BaseEvent):
    """Event for graph generation operations."""
    
    content_source: str = Field(..., description="Source of content for graph generation")
    content_type: str = Field(..., description="Type of content being processed")
    graph_config: Dict[str, Any] = Field(default_factory=dict, description="Graph generation configuration")
    expected_nodes: Optional[int] = Field(None, description="Expected number of nodes")
    expected_edges: Optional[int] = Field(None, description="Expected number of edges")


class GraphGenerationStartedEvent(GraphGenerationEvent):
    """Event when graph generation starts."""
    
    extraction_config: Dict[str, Any] = Field(..., description="Entity extraction configuration")
    discovery_config: Dict[str, Any] = Field(..., description="Relationship discovery configuration")
    builder_config: Dict[str, Any] = Field(..., description="Graph builder configuration")


class GraphGenerationCompletedEvent(GraphGenerationEvent):
    """Event when graph generation is completed."""
    
    nodes_created: int = Field(..., description="Number of nodes created")
    edges_created: int = Field(..., description="Number of edges created")
    graph_quality_score: float = Field(..., description="Overall graph quality score")
    validation_passed: bool = Field(..., description="Whether graph validation passed")
    export_formats: List[str] = Field(..., description="Formats the graph was exported to")
    output_directory: str = Field(..., description="Directory where graph files are stored")


class GraphGenerationFailedEvent(GraphGenerationEvent):
    """Event when graph generation fails."""
    
    failure_stage: str = Field(..., description="Stage where generation failed")
    failure_reason: str = Field(..., description="Reason for generation failure")
    partial_results: Optional[Dict[str, Any]] = Field(None, description="Partial results if any")


# KG Integration Events
class KGIntegrationEvent(BaseEvent):
    """Event for KG Neo4j integration operations."""
    
    graph_id: str = Field(..., description="ID of the graph being integrated")
    kg_endpoint: str = Field(..., description="KG Neo4j endpoint")
    integration_type: str = Field(..., description="Type of integration (transfer, sync, lifecycle)")
    graph_metadata: Dict[str, Any] = Field(..., description="Graph metadata for integration")


class GraphTransferEvent(KGIntegrationEvent):
    """Event for graph transfer to KG Neo4j."""
    
    transfer_size: int = Field(..., description="Size of data being transferred")
    transfer_format: str = Field(..., description="Format of transferred data")
    compression_enabled: bool = Field(..., description="Whether compression is enabled")
    encryption_enabled: bool = Field(..., description="Whether encryption is enabled")


class GraphTransferCompletedEvent(GraphTransferEvent):
    """Event when graph transfer is completed."""
    
    transfer_time: float = Field(..., description="Transfer time in seconds")
    transfer_speed: float = Field(..., description="Transfer speed in MB/s")
    kg_graph_id: str = Field(..., description="KG Neo4j graph ID")
    verification_passed: bool = Field(..., description="Whether transfer verification passed")


class GraphTransferFailedEvent(GraphTransferEvent):
    """Event when graph transfer fails."""
    
    failure_reason: str = Field(..., description="Reason for transfer failure")
    network_error: Optional[str] = Field(None, description="Network error details")
    authentication_error: Optional[str] = Field(None, description="Authentication error details")


class GraphSyncEvent(KGIntegrationEvent):
    """Event for graph synchronization operations."""
    
    sync_direction: str = Field(..., description="Direction of synchronization (push, pull, bidirectional)")
    sync_scope: str = Field(..., description="Scope of synchronization (full, incremental, selective)")
    conflict_resolution: str = Field(..., description="Conflict resolution strategy")


class GraphSyncCompletedEvent(GraphSyncEvent):
    """Event when graph synchronization is completed."""
    
    sync_time: float = Field(..., description="Synchronization time in seconds")
    conflicts_resolved: int = Field(..., description="Number of conflicts resolved")
    changes_applied: int = Field(..., description="Number of changes applied")
    sync_status: str = Field(..., description="Final synchronization status")


class GraphLifecycleEvent(KGIntegrationEvent):
    """Event for graph lifecycle management."""
    
    lifecycle_stage: str = Field(..., description="Current lifecycle stage")
    previous_stage: Optional[str] = Field(None, description="Previous lifecycle stage")
    transition_reason: Optional[str] = Field(None, description="Reason for stage transition")
    lifecycle_policy: Dict[str, Any] = Field(..., description="Lifecycle policy configuration")


# Performance Monitoring Events
class PerformanceEvent(BaseEvent):
    """Event for performance monitoring."""
    
    metric_name: str = Field(..., description="Name of the performance metric")
    metric_value: float = Field(..., description="Value of the performance metric")
    metric_unit: str = Field(..., description="Unit of the performance metric")
    threshold_value: Optional[float] = Field(None, description="Threshold value for the metric")
    is_threshold_exceeded: bool = Field(..., description="Whether threshold is exceeded")


class PerformanceThresholdExceededEvent(PerformanceEvent):
    """Event when performance threshold is exceeded."""
    
    severity: str = Field(..., description="Severity of the threshold violation")
    recommended_action: str = Field(..., description="Recommended action to resolve")
    impact_assessment: str = Field(..., description="Impact assessment of the violation")


# System Health Events
class SystemHealthEvent(BaseEvent):
    """Event for system health monitoring."""
    
    component_name: str = Field(..., description="Name of the system component")
    health_status: str = Field(..., description="Current health status")
    previous_status: Optional[str] = Field(None, description="Previous health status")
    health_metrics: Dict[str, Any] = Field(..., description="Health-related metrics")


class SystemHealthChangedEvent(SystemHealthEvent):
    """Event when system health status changes."""
    
    change_reason: str = Field(..., description="Reason for health status change")
    impact_level: str = Field(..., description="Impact level of the health change")
    recovery_time: Optional[float] = Field(None, description="Estimated recovery time")


# Integration Events
class IntegrationEvent(BaseEvent):
    """Event for external integrations."""
    
    integration_name: str = Field(..., description="Name of the external integration")
    integration_type: str = Field(..., description="Type of integration (API, webhook, etc.)")
    endpoint_url: Optional[str] = Field(None, description="Integration endpoint URL")
    request_data: Optional[Dict[str, Any]] = Field(None, description="Request data sent")
    response_data: Optional[Dict[str, Any]] = Field(None, description="Response data received")


class IntegrationSuccessEvent(IntegrationEvent):
    """Event when integration is successful."""
    
    response_time: float = Field(..., description="Response time in seconds")
    status_code: int = Field(..., description="HTTP status code")
    success_message: str = Field(..., description="Success message")


class IntegrationFailureEvent(IntegrationEvent):
    """Event when integration fails."""
    
    failure_reason: str = Field(..., description="Reason for integration failure")
    status_code: Optional[int] = Field(None, description="HTTP status code if applicable")
    retry_scheduled: bool = Field(..., description="Whether retry is scheduled")
    next_retry_time: Optional[datetime] = Field(None, description="Next retry time")


# Error and Warning Events
class ErrorEvent(BaseEvent):
    """Event for error conditions."""
    
    error_code: str = Field(..., description="Error code")
    error_type: str = Field(..., description="Type of error")
    error_context: Dict[str, Any] = Field(..., description="Error context information")
    user_impact: str = Field(..., description="Impact on user operations")
    resolution_steps: List[str] = Field(..., description="Steps to resolve the error")


class WarningEvent(BaseEvent):
    """Event for warning conditions."""
    
    warning_code: str = Field(..., description="Warning code")
    warning_type: str = Field(..., description="Type of warning")
    warning_context: Dict[str, Any] = Field(..., description="Warning context information")
    potential_impact: str = Field(..., description="Potential impact if warning is ignored")
    prevention_measures: List[str] = Field(..., description="Measures to prevent escalation")


# Event Factory
class EventFactory:
    """Factory for creating events with proper configuration."""
    
    @staticmethod
    def create_document_processing_event(
        file_path: str,
        file_type: str,
        file_size: int,
        processor_type: str,
        project_id: Optional[str] = None,
        **kwargs
    ) -> DocumentProcessingEvent:
        """Create a document processing event."""
        return DocumentProcessingEvent(
            event_id=f"doc_proc_{datetime.utcnow().timestamp()}",
            event_type="document_processing",
            event_category=EventCategory.DOCUMENT_PROCESSING,
            source="document_processor",
            target="graph_generation",
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            processor_type=processor_type,
            project_id=project_id,
            **kwargs
        )
    
    @staticmethod
    def create_graph_generation_event(
        content_source: str,
        content_type: str,
        project_id: Optional[str] = None,
        **kwargs
    ) -> GraphGenerationEvent:
        """Create a graph generation event."""
        return GraphGenerationEvent(
            event_id=f"graph_gen_{datetime.utcnow().timestamp()}",
            event_type="graph_generation",
            event_category=EventCategory.GRAPH_GENERATION,
            source="graph_generation",
            target="kg_integration",
            content_source=content_source,
            content_type=content_type,
            project_id=project_id,
            **kwargs
        )
    
    @staticmethod
    def create_kg_integration_event(
        graph_id: str,
        integration_type: str,
        project_id: Optional[str] = None,
        **kwargs
    ) -> KGIntegrationEvent:
        """Create a KG integration event."""
        return KGIntegrationEvent(
            event_id=f"kg_int_{datetime.utcnow().timestamp()}",
            event_type="kg_integration",
            event_category=EventCategory.KG_INTEGRATION,
            source="ai_rag",
            target="kg_neo4j",
            graph_id=graph_id,
            integration_type=integration_type,
            project_id=project_id,
            **kwargs
        )
    
    @staticmethod
    def create_performance_event(
        metric_name: str,
        metric_value: float,
        metric_unit: str,
        **kwargs
    ) -> PerformanceEvent:
        """Create a performance event."""
        return PerformanceEvent(
            event_id=f"perf_{datetime.utcnow().timestamp()}",
            event_type="performance_monitoring",
            event_category=EventCategory.PERFORMANCE_MONITORING,
            source="performance_monitor",
            metric_name=metric_name,
            metric_value=metric_value,
            metric_unit=metric_unit,
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
            event_id=f"error_{datetime.utcnow().timestamp()}",
            event_type="error",
            event_category=EventCategory.ERROR,
            priority=EventPriority.HIGH,
            source="system",
            error_code=error_code,
            error_type=error_type,
            error_message=error_message,
            **kwargs
        )


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
}
