"""
Data Models for External Communication

This module defines the core data structures used by the external
communication layer for managing module communication, events, and
data pipelines.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4


class EventType(str, Enum):
    """Types of events that can be communicated between modules."""
    DATA_UPDATE = "data_update"
    MODULE_HEALTH = "module_health"
    WORKFLOW_START = "workflow_start"
    WORKFLOW_COMPLETE = "workflow_complete"
    ERROR_OCCURRED = "error_occurred"
    DATA_SYNC = "data_sync"
    CONFIG_CHANGE = "config_change"
    USER_ACTION = "user_action"
    SYSTEM_ALERT = "system_alert"
    CUSTOM = "custom"


class PipelineStatus(str, Enum):
    """Status of a data pipeline stage."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class CommunicationProtocol(str, Enum):
    """Supported communication protocols."""
    HTTP = "http"
    HTTPS = "https"
    GRPC = "grpc"
    WEBSOCKET = "websocket"
    MQTT = "mqtt"


@dataclass
class EventMessage:
    """Represents a message sent through the event bridge."""
    
    event_id: UUID = field(default_factory=uuid4)
    event_type: EventType = EventType.CUSTOM
    source_module: str = ""
    target_module: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[UUID] = None
    priority: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type.value,
            "source_module": self.source_module,
            "target_module": self.target_module,
            "timestamp": self.timestamp.isoformat(),
            "payload": self.payload,
            "metadata": self.metadata,
            "correlation_id": str(self.correlation_id) if self.correlation_id else None,
            "priority": self.priority
        }


@dataclass
class ModuleEndpoint:
    """Represents an endpoint for an external module."""
    
    module_id: UUID = field(default_factory=uuid4)
    module_name: str = ""
    base_url: str = ""
    protocol: CommunicationProtocol = CommunicationProtocol.HTTP
    api_version: str = "v1"
    health_endpoint: str = "/health"
    api_endpoint: str = "/api"
    auth_required: bool = False
    auth_token: Optional[str] = None
    timeout_seconds: int = 30
    retry_attempts: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_seen: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


@dataclass
class PipelineStage:
    """Represents a stage in a data pipeline."""
    
    stage_id: UUID = field(default_factory=uuid4)
    stage_name: str = ""
    stage_order: int = 0
    module_name: str = ""
    operation: str = ""
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 60
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    status: PipelineStatus = PipelineStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineConfig:
    """Configuration for a data pipeline."""
    
    pipeline_id: UUID = field(default_factory=uuid4)
    pipeline_name: str = ""
    description: str = ""
    stages: List[PipelineStage] = field(default_factory=list)
    max_concurrent_stages: int = 3
    timeout_seconds: int = 300
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    error_handling: Dict[str, Any] = field(default_factory=dict)
    monitoring: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CommunicationMetrics:
    """Metrics for communication performance."""
    
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time_ms: float = 0.0
    average_response_time_ms: float = 0.0
    last_request_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    
    def update_success(self, response_time_ms: float) -> None:
        """Update metrics for successful request."""
        self.total_requests += 1
        self.successful_requests += 1
        self.total_response_time_ms += response_time_ms
        self.average_response_time_ms = self.total_response_time_ms / self.total_requests
        self.last_request_time = datetime.utcnow()
        self.last_success_time = datetime.utcnow()
        self.consecutive_successes += 1
        self.consecutive_failures = 0
    
    def update_failure(self) -> None:
        """Update metrics for failed request."""
        self.total_requests += 1
        self.failed_requests += 1
        self.last_request_time = datetime.utcnow()
        self.last_failure_time = datetime.utcnow()
        self.consecutive_failures += 1
        self.consecutive_successes = 0
