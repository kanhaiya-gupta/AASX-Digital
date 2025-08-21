"""
Certificate Event Model

Event tracking for certificate lifecycle and module interactions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
import hashlib
import json

from src.shared.models.base_model import BaseModel


class EventType(str, Enum):
    """Certificate event types."""
    # Certificate lifecycle events
    CERTIFICATE_CREATED = "certificate_created"
    CERTIFICATE_UPDATED = "certificate_updated"
    CERTIFICATE_COMPLETED = "certificate_completed"
    CERTIFICATE_ARCHIVED = "certificate_archived"
    
    # Module integration events
    ETL_COMPLETED = "etl_completed"
    AI_RAG_COMPLETED = "ai_rag_completed"
    KNOWLEDGE_GRAPH_UPDATED = "knowledge_graph_updated"
    FEDERATED_LEARNING_UPDATED = "federated_learning_updated"
    PHYSICS_MODELING_COMPLETED = "physics_modeling_completed"
    
    # Export and verification events
    EXPORT_GENERATED = "export_generated"
    SIGNATURE_APPLIED = "signature_applied"
    VERIFICATION_REQUESTED = "verification_requested"
    
    # System events
    ERROR_OCCURRED = "error_occurred"
    STATUS_CHANGED = "status_changed"
    VERSION_CREATED = "version_created"


class EventStatus(str, Enum):
    """Event processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class CertificateEvent(BaseModel):
    """Certificate event data model."""
    
    # Core identification - make these optional with defaults
    certificate_id: str = field(default="")
    event_id: str = field(default="")
    event_type: EventType = EventType.CERTIFICATE_CREATED
    
    # Module information
    module_name: str = field(default="system")
    
    # Event data
    event_hash: str = field(default="")
    data_snapshot: Optional[Dict[str, Any]] = None
    
    # Processing status
    status: EventStatus = EventStatus.PENDING
    processed_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Post-initialization setup."""
        super().__post_init__()
        
        # Generate event ID if not provided
        if not self.event_id:
            self.event_id = self._generate_event_id()
        
        # Generate event hash if not provided
        if not self.event_hash:
            self.event_hash = self._calculate_event_hash()
    
    def _generate_event_id(self) -> str:
        """Generate a unique event ID."""
        base_string = f"{self.certificate_id}_{self.event_type.value}_{self.created_at.isoformat()}"
        return hashlib.sha256(base_string.encode()).hexdigest()[:16]
    
    def _calculate_event_hash(self) -> str:
        """Calculate hash of event data."""
        event_data = {
            'certificate_id': self.certificate_id,
            'event_type': self.event_type.value,
            'module_name': self.module_name,
            'data_snapshot': self.data_snapshot or {},
            'created_at': self.created_at.isoformat()
        }
        
        event_string = json.dumps(event_data, sort_keys=True, default=str)
        return hashlib.sha256(event_string.encode()).hexdigest()
    
    def mark_processing(self) -> None:
        """Mark event as processing."""
        self.status = EventStatus.PROCESSING
    
    def mark_completed(self) -> None:
        """Mark event as completed."""
        self.status = EventStatus.COMPLETED
        self.processed_at = datetime.now()
    
    def mark_failed(self) -> None:
        """Mark event as failed."""
        self.status = EventStatus.FAILED
        self.processed_at = datetime.now()
    
    def mark_skipped(self) -> None:
        """Mark event as skipped."""
        self.status = EventStatus.SKIPPED
        self.processed_at = datetime.now()
    
    def update_data_snapshot(self, data: Dict[str, Any]) -> None:
        """Update the data snapshot."""
        self.data_snapshot = data
        self.event_hash = self._calculate_event_hash()
    
    def add_data_to_snapshot(self, key: str, value: Any) -> None:
        """Add data to the snapshot."""
        if self.data_snapshot is None:
            self.data_snapshot = {}
        
        self.data_snapshot[key] = value
        self.event_hash = self._calculate_event_hash()
    
    def get_data_from_snapshot(self, key: str, default: Any = None) -> Any:
        """Get data from the snapshot."""
        if self.data_snapshot:
            return self.data_snapshot.get(key, default)
        return default
    
    def is_processed(self) -> bool:
        """Check if event has been processed."""
        return self.status in [EventStatus.COMPLETED, EventStatus.FAILED, EventStatus.SKIPPED]
    
    def is_pending(self) -> bool:
        """Check if event is pending."""
        return self.status == EventStatus.PENDING
    
    def is_processing(self) -> bool:
        """Check if event is being processed."""
        return self.status == EventStatus.PROCESSING
    
    def get_processing_duration(self) -> Optional[float]:
        """Get processing duration in seconds."""
        if self.processed_at and self.created_at:
            return (self.processed_at - self.created_at).total_seconds()
        return None
    
    def is_module_event(self) -> bool:
        """Check if this is a module-related event."""
        module_events = [
            EventType.ETL_COMPLETED,
            EventType.AI_RAG_COMPLETED,
            EventType.KNOWLEDGE_GRAPH_UPDATED,
            EventType.FEDERATED_LEARNING_UPDATED,
            EventType.PHYSICS_MODELING_COMPLETED
        ]
        return self.event_type in module_events
    
    def is_lifecycle_event(self) -> bool:
        """Check if this is a lifecycle event."""
        lifecycle_events = [
            EventType.CERTIFICATE_CREATED,
            EventType.CERTIFICATE_UPDATED,
            EventType.CERTIFICATE_COMPLETED,
            EventType.CERTIFICATE_ARCHIVED
        ]
        return self.event_type in lifecycle_events
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            'id': self.id,
            'certificate_id': self.certificate_id,
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'module_name': self.module_name,
            'event_hash': self.event_hash,
            'data_snapshot': self.data_snapshot,
            'status': self.status.value,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'created_at': self.created_at.isoformat(),
            'is_processed': self.is_processed(),
            'is_module_event': self.is_module_event(),
            'is_lifecycle_event': self.is_lifecycle_event(),
            'processing_duration': self.get_processing_duration()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CertificateEvent':
        """Create event from dictionary."""
        # Convert sqlite3.Row to dict if needed
        if hasattr(data, 'keys'):  # sqlite3.Row object
            data = dict(data)
        
        # Remove database-specific fields that don't exist in the model
        data_copy = data.copy()
        data_copy.pop('id', None)  # Remove database auto-increment ID
        
        # Convert string enums back to enum values
        if 'event_type' in data_copy and isinstance(data_copy['event_type'], str):
            data_copy['event_type'] = EventType(data_copy['event_type'])
        
        if 'status' in data_copy and isinstance(data_copy['status'], str):
            data_copy['status'] = EventStatus(data_copy['status'])
        
        # Convert timestamp strings back to datetime
        for field in ['created_at', 'processed_at']:
            if field in data_copy and data_copy[field] and isinstance(data_copy[field], str):
                data_copy[field] = datetime.fromisoformat(data_copy[field])
        
        # Deserialize JSON fields back to dictionaries
        import json
        if 'data_snapshot' in data_copy and data_copy['data_snapshot'] and isinstance(data_copy['data_snapshot'], str):
            try:
                data_copy['data_snapshot'] = json.loads(data_copy['data_snapshot'])
            except (json.JSONDecodeError, TypeError):
                # Keep as string if JSON parsing fails
                pass
        
        return cls(**data_copy)
    
    def __str__(self) -> str:
        """String representation."""
        return f"CertificateEvent({self.event_id}, {self.event_type.value}, {self.status.value})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"CertificateEvent(event_id='{self.event_id}', event_type='{self.event_type.value}', status='{self.status.value}')" 