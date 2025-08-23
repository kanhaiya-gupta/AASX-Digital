"""
Knowledge Graph Neo4j Event Types

Defines all event types, priorities, and statuses for the event-driven automation system.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """Event priority levels for processing order."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class EventStatus(Enum):
    """Event processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRY = "retry"


@dataclass
class KGNeo4jEvent:
    """Base event class for all Knowledge Graph Neo4j events."""
    
    event_id: str
    event_type: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    priority: EventPriority = EventPriority.NORMAL
    status: EventStatus = EventStatus.PENDING
    source: str = "kg_neo4j"
    user_id: Optional[str] = None
    org_id: Optional[str] = None
    dept_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    processing_time_ms: Optional[float] = None
    
    def __post_init__(self):
        """Validate event data after initialization."""
        if not self.event_id:
            raise ValueError("Event ID is required")
        if not self.event_type:
            raise ValueError("Event type is required")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority.value,
            "status": self.status.value,
            "source": self.source,
            "user_id": self.user_id,
            "org_id": self.org_id,
            "dept_id": self.dept_id,
            "metadata": self.metadata,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "error_message": self.error_message,
            "processing_time_ms": self.processing_time_ms
        }
    
    def update_status(self, status: EventStatus, error_message: Optional[str] = None) -> None:
        """Update event status and error message."""
        self.status = status
        if error_message:
            self.error_message = error_message
        logger.debug(f"Event {self.event_id} status updated to {status.value}")
    
    def increment_retry(self) -> bool:
        """Increment retry count and check if retry is allowed."""
        self.retry_count += 1
        if self.retry_count > self.max_retries:
            self.status = EventStatus.FAILED
            logger.warning(f"Event {self.event_id} exceeded max retries")
            return False
        self.status = EventStatus.RETRY
        logger.info(f"Event {self.event_id} retry {self.retry_count}/{self.max_retries}")
        return True


@dataclass
class GraphCreationEvent(KGNeo4jEvent):
    """Event for knowledge graph creation operations."""
    
    file_id: str
    graph_name: str
    workflow_source: str = "aasx_file"  # aasx_file, twin_registry, ai_rag
    graph_config: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize as graph creation event."""
        super().__post_init__()
        self.event_type = "graph_creation"
        if not self.file_id:
            raise ValueError("File ID is required for graph creation")
        if not self.graph_name:
            raise ValueError("Graph name is required for graph creation")


@dataclass
class GraphStatusChangeEvent(KGNeo4jEvent):
    """Event for graph status changes."""
    
    graph_id: str
    old_status: Dict[str, Any]
    new_status: Dict[str, Any]
    change_reason: str = "manual_update"
    change_source: str = "system"
    
    def __post_init__(self):
        """Initialize as graph status change event."""
        super().__post_init__()
        self.event_type = "graph_status_change"
        if not self.graph_id:
            raise ValueError("Graph ID is required for status change")
        if not self.new_status:
            raise ValueError("New status is required for status change")


@dataclass
class Neo4jOperationEvent(KGNeo4jEvent):
    """Event for Neo4j operations."""
    
    graph_id: str
    operation_type: str  # import, export, sync, query, cleanup
    operation_config: Dict[str, Any] = field(default_factory=dict)
    neo4j_connection_id: Optional[str] = None
    cypher_query: Optional[str] = None
    query_parameters: Optional[Dict[str, Any]] = None
    batch_size: Optional[int] = None
    
    def __post_init__(self):
        """Initialize as Neo4j operation event."""
        super().__post_init__()
        self.event_type = "neo4j_operation"
        if not self.graph_id:
            raise ValueError("Graph ID is required for Neo4j operation")
        if not self.operation_type:
            raise ValueError("Operation type is required for Neo4j operation")


@dataclass
class AIInsightsEvent(KGNeo4jEvent):
    """Event for AI/RAG insights operations."""
    
    graph_id: str
    ai_operation_type: str  # analysis, enhancement, validation, training
    ai_model_version: Optional[str] = None
    confidence_score: Optional[float] = None
    analysis_data: Dict[str, Any] = field(default_factory=dict)
    insights_count: Optional[int] = None
    processing_duration_ms: Optional[float] = None
    
    def __post_init__(self):
        """Initialize as AI insights event."""
        super().__post_init__()
        self.event_type = "ai_insights"
        if not self.graph_id:
            raise ValueError("Graph ID is required for AI insights")
        if not self.ai_operation_type:
            raise ValueError("AI operation type is required for AI insights")


@dataclass
class HealthMonitoringEvent(KGNeo4jEvent):
    """Event for health monitoring and alerting."""
    
    graph_id: str
    health_metric_type: str  # performance, data_quality, neo4j_status, system_health
    current_value: float
    threshold_value: float
    severity: str = "warning"  # info, warning, error, critical
    alert_message: str = ""
    recommended_action: Optional[str] = None
    historical_trend: Optional[List[float]] = None
    
    def __post_init__(self):
        """Initialize as health monitoring event."""
        super().__post_init__()
        self.event_type = "health_monitoring"
        if not self.graph_id:
            raise ValueError("Graph ID is required for health monitoring")
        if not self.health_metric_type:
            raise ValueError("Health metric type is required for health monitoring")


# Event Type Registry for dynamic event creation
EVENT_TYPE_REGISTRY = {
    "graph_creation": GraphCreationEvent,
    "graph_status_change": GraphStatusChangeEvent,
    "neo4j_operation": Neo4jOperationEvent,
    "ai_insights": AIInsightsEvent,
    "health_monitoring": HealthMonitoringEvent
}


def create_event(event_type: str, **kwargs) -> KGNeo4jEvent:
    """Factory function to create events by type."""
    if event_type not in EVENT_TYPE_REGISTRY:
        raise ValueError(f"Unknown event type: {event_type}")
    
    event_class = EVENT_TYPE_REGISTRY[event_type]
    return event_class(**kwargs)


def get_event_types() -> List[str]:
    """Get list of available event types."""
    return list(EVENT_TYPE_REGISTRY.keys())
