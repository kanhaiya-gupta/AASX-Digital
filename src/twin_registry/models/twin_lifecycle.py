"""
Twin Lifecycle Model

Manages lifecycle events and status of digital twins.
"""

from src.shared.models.base_model import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
from enum import Enum


class LifecycleEventType(str, Enum):
    """Types of lifecycle events"""
    CREATED = "created"
    STARTED = "started"
    STOPPED = "stopped"
    SYNC_STARTED = "sync_started"
    SYNC_COMPLETED = "sync_completed"
    SYNC_FAILED = "sync_failed"
    UPDATED = "updated"
    DELETED = "deleted"
    ERROR = "error"


class LifecycleStatus(str, Enum):
    """Twin lifecycle status"""
    CREATED = "created"
    RUNNING = "running"
    STOPPED = "stopped"
    SYNCING = "syncing"
    ERROR = "error"
    DELETED = "deleted"


class TwinLifecycleEvent(BaseModel):
    """Model for tracking twin lifecycle events"""
    
    event_id: str
    twin_id: str
    event_type: LifecycleEventType
    event_data: Optional[Dict[str, Any]] = None
    event_metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime
    triggered_by: Optional[str] = None
    status: str = "completed"  # completed, failed, in_progress
    error_message: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def create_event(
        cls,
        twin_id: str,
        event_type: LifecycleEventType,
        event_data: Optional[Dict[str, Any]] = None,
        event_metadata: Optional[Dict[str, Any]] = None,
        triggered_by: Optional[str] = None
    ) -> "TwinLifecycleEvent":
        """Create a new lifecycle event"""
        now = datetime.utcnow()
        return cls(
            event_id=str(uuid.uuid4()),
            twin_id=twin_id,
            event_type=event_type,
            event_data=event_data or {},
            event_metadata=event_metadata or {},
            timestamp=now,
            triggered_by=triggered_by,
            status="completed"
        )
    
    def mark_failed(self, error_message: str) -> None:
        """Mark the event as failed"""
        self.status = "failed"
        self.error_message = error_message
    
    def mark_in_progress(self) -> None:
        """Mark the event as in progress"""
        self.status = "in_progress"
    
    def mark_completed(self) -> None:
        """Mark the event as completed"""
        self.status = "completed"


class TwinLifecycleStatus(BaseModel):
    """Model for current twin lifecycle status"""
    
    twin_id: str
    current_status: LifecycleStatus
    last_event: Optional[TwinLifecycleEvent] = None
    last_updated: datetime
    lifecycle_metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def create_status(
        cls,
        twin_id: str,
        initial_status: LifecycleStatus = LifecycleStatus.CREATED
    ) -> "TwinLifecycleStatus":
        """Create a new lifecycle status"""
        now = datetime.utcnow()
        return cls(
            twin_id=twin_id,
            current_status=initial_status,
            last_updated=now,
            lifecycle_metadata={}
        )
    
    def update_status(self, new_status: LifecycleStatus, event: Optional[TwinLifecycleEvent] = None) -> None:
        """Update the lifecycle status"""
        self.current_status = new_status
        if event:
            self.last_event = event
        self.last_updated = datetime.utcnow()
    
    def update_metadata(self, metadata: Dict[str, Any]) -> None:
        """Update lifecycle metadata"""
        if self.lifecycle_metadata is None:
            self.lifecycle_metadata = {}
        self.lifecycle_metadata.update(metadata)


class TwinLifecycleQuery(BaseModel):
    """Query model for filtering lifecycle events"""
    
    twin_id: Optional[str] = None
    event_type: Optional[LifecycleEventType] = None
    status: Optional[str] = None
    triggered_by: Optional[str] = None
    timestamp_after: Optional[datetime] = None
    timestamp_before: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TwinLifecycleSummary(BaseModel):
    """Summary model for twin lifecycle statistics"""
    
    total_events: int
    events_by_type: Dict[str, int]
    events_by_status: Dict[str, int]
    recent_events: List[TwinLifecycleEvent]
    status_distribution: Dict[str, int]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 