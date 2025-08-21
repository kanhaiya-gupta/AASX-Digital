"""
Event Types and Definitions

Defines the event types, priorities, and structures used in the twin registry
event system.
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
import uuid


class EventType(Enum):
    """Enumeration of event types."""
    # File upload events
    FILE_UPLOADED = "file_uploaded"
    FILE_PROCESSING_STARTED = "file_processing_started"
    FILE_PROCESSING_COMPLETED = "file_processing_completed"
    FILE_PROCESSING_FAILED = "file_processing_failed"
    
    # ETL events
    ETL_JOB_CREATED = "etl_job_created"
    ETL_JOB_STARTED = "etl_job_started"
    ETL_JOB_COMPLETED = "etl_job_completed"
    ETL_JOB_FAILED = "etl_job_failed"
    ETL_JOB_CANCELLED = "etl_job_cancelled"
    
    # Registry population events
    REGISTRY_POPULATION_STARTED = "registry_population_started"
    REGISTRY_POPULATION_COMPLETED = "registry_population_completed"
    REGISTRY_POPULATION_FAILED = "registry_population_failed"
    REGISTRY_POPULATION_ROLLBACK = "registry_population_rollback"
    
    # Phase events
    PHASE1_STARTED = "phase1_started"
    PHASE1_COMPLETED = "phase1_completed"
    PHASE1_FAILED = "phase1_failed"
    PHASE2_STARTED = "phase2_started"
    PHASE2_COMPLETED = "phase2_completed"
    PHASE2_FAILED = "phase2_failed"
    
    # Validation events
    VALIDATION_STARTED = "validation_started"
    VALIDATION_COMPLETED = "validation_completed"
    VALIDATION_FAILED = "validation_failed"
    
    # System events
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    SYSTEM_ERROR = "system_error"
    SYSTEM_WARNING = "system_warning"
    
    # AI/RAG events
    AI_RAG_STARTED = "ai_rag_started"
    AI_RAG_COMPLETED = "ai_rag_completed"
    AI_RAG_FAILED = "ai_rag_failed"
    
    # Custom events
    CUSTOM_EVENT = "custom_event"


class EventPriority(Enum):
    """Enumeration of event priorities."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class EventStatus(Enum):
    """Enumeration of event statuses."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class EventMetadata:
    """Metadata for events."""
    source: str
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    org_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    tags: Optional[list] = None
    custom_fields: Optional[Dict[str, Any]] = None


@dataclass
class Event:
    """Base event structure."""
    event_id: str
    event_type: EventType
    timestamp: datetime
    priority: EventPriority
    status: EventStatus
    data: Dict[str, Any]
    metadata: EventMetadata
    
    def __post_init__(self):
        """Post-initialization validation."""
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority.value,
            "status": self.status.value,
            "data": self.data,
            "metadata": {
                "source": self.metadata.source,
                "correlation_id": self.metadata.correlation_id,
                "user_id": self.metadata.user_id,
                "org_id": self.metadata.org_id,
                "session_id": self.metadata.session_id,
                "request_id": self.metadata.request_id,
                "tags": self.metadata.tags or [],
                "custom_fields": self.metadata.custom_fields or {}
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create event from dictionary."""
        return cls(
            event_id=data["event_id"],
            event_type=EventType(data["event_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            priority=EventPriority(data["priority"]),
            status=EventStatus(data["status"]),
            data=data["data"],
            metadata=EventMetadata(
                source=data["metadata"]["source"],
                correlation_id=data["metadata"].get("correlation_id"),
                user_id=data["metadata"].get("user_id"),
                org_id=data["metadata"].get("org_id"),
                session_id=data["metadata"].get("session_id"),
                request_id=data["metadata"].get("request_id"),
                tags=data["metadata"].get("tags", []),
                custom_fields=data["metadata"].get("custom_fields", {})
            )
        )


# Event factory functions for common event types
def create_file_upload_event(
    file_id: str,
    file_name: str,
    user_id: str,
    org_id: str,
    correlation_id: Optional[str] = None,
    **kwargs
) -> Event:
    """Create a file upload event."""
    return Event(
        event_id=str(uuid.uuid4()),
        event_type=EventType.FILE_UPLOADED,
        timestamp=datetime.now(timezone.utc),
        priority=EventPriority.NORMAL,
        status=EventStatus.PENDING,
        data={
            "file_id": file_id,
            "file_name": file_name,
            "file_size": kwargs.get("file_size"),
            "file_hash": kwargs.get("file_hash"),
            "upload_time": kwargs.get("upload_time")
        },
        metadata=EventMetadata(
            source="file_upload_system",
            correlation_id=correlation_id,
            user_id=user_id,
            org_id=org_id,
            tags=["file_upload", "population_trigger"]
        )
    )


def create_etl_completion_event(
    job_id: str,
    job_type: str,
    processing_time: float,
    assets_count: int,
    quality_score: float,
    correlation_id: Optional[str] = None,
    **kwargs
) -> Event:
    """Create an ETL completion event."""
    return Event(
        event_id=str(uuid.uuid4()),
        event_type=EventType.ETL_JOB_COMPLETED,
        timestamp=datetime.now(timezone.utc),
        priority=EventPriority.HIGH,
        status=EventStatus.COMPLETED,
        data={
            "job_id": job_id,
            "job_type": job_type,
            "processing_time": processing_time,
            "assets_count": assets_count,
            "quality_score": quality_score,
            "output_formats": kwargs.get("output_formats", []),
            "error_count": kwargs.get("error_count", 0),
            "warning_count": kwargs.get("warning_count", 0)
        },
        metadata=EventMetadata(
            source="etl_pipeline",
            correlation_id=correlation_id,
            tags=["etl", "population_trigger", "job_completion"]
        )
    )


def create_registry_population_event(
    registry_id: str,
    phase: str,
    status: EventStatus,
    correlation_id: Optional[str] = None,
    **kwargs
) -> Event:
    """Create a registry population event."""
    event_type_map = {
        "started": EventType.REGISTRY_POPULATION_STARTED,
        "completed": EventType.REGISTRY_POPULATION_COMPLETED,
        "failed": EventType.REGISTRY_POPULATION_FAILED,
        "rollback": EventType.REGISTRY_POPULATION_ROLLBACK
    }
    
    return Event(
        event_id=str(uuid.uuid4()),
        event_type=event_type_map.get(status.value, EventType.REGISTRY_POPULATION_STARTED),
        timestamp=datetime.now(timezone.utc),
        priority=EventPriority.NORMAL,
        status=status,
        data={
            "registry_id": registry_id,
            "phase": phase,
            "population_data": kwargs.get("population_data", {}),
            "error_message": kwargs.get("error_message"),
            "processing_time": kwargs.get("processing_time")
        },
        metadata=EventMetadata(
            source="twin_registry_populator",
            correlation_id=correlation_id,
            tags=["population", "registry", phase]
        )
    )


def create_validation_event(
    validation_type: str,
    target_id: str,
    status: EventStatus,
    quality_score: float,
    correlation_id: Optional[str] = None,
    **kwargs
) -> Event:
    """Create a validation event."""
    event_type_map = {
        "started": EventType.VALIDATION_STARTED,
        "completed": EventType.VALIDATION_COMPLETED,
        "failed": EventType.VALIDATION_FAILED
    }
    
    return Event(
        event_id=str(uuid.uuid4()),
        event_type=event_type_map.get(status.value, EventType.VALIDATION_STARTED),
        timestamp=datetime.now(timezone.utc),
        priority=EventPriority.NORMAL,
        status=status,
        data={
            "validation_type": validation_type,
            "target_id": target_id,
            "quality_score": quality_score,
            "validation_rules": kwargs.get("validation_rules", []),
            "error_count": kwargs.get("error_count", 0),
            "warning_count": kwargs.get("warning_count", 0),
            "validation_details": kwargs.get("validation_details", {})
        },
        metadata=EventMetadata(
            source="population_validator",
            correlation_id=correlation_id,
            tags=["validation", validation_type]
        )
    )


def create_system_event(
    event_type: EventType,
    message: str,
    severity: str = "info",
    correlation_id: Optional[str] = None,
    **kwargs
) -> Event:
    """Create a system event."""
    priority_map = {
        "info": EventPriority.LOW,
        "warning": EventPriority.NORMAL,
        "error": EventPriority.HIGH,
        "critical": EventPriority.CRITICAL
    }
    
    return Event(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        timestamp=datetime.now(timezone.utc),
        priority=priority_map.get(severity, EventPriority.NORMAL),
        status=EventStatus.COMPLETED,
        data={
            "message": message,
            "severity": severity,
            "component": kwargs.get("component"),
            "stack_trace": kwargs.get("stack_trace"),
            "system_info": kwargs.get("system_info", {})
        },
        metadata=EventMetadata(
            source="system",
            correlation_id=correlation_id,
            tags=["system", severity]
        )
    )
