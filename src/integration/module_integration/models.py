"""
Data models for module integration services.

This module defines the core data structures used by the module integration
layer to represent modules, their health status, workflows, and results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4


class ModuleStatus(str, Enum):
    """Module operational status."""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    ERROR = "error"
    UNKNOWN = "unknown"


class ModuleType(str, Enum):
    """Type of task module."""
    TWIN_REGISTRY = "twin_registry"
    AASX = "aasx"
    AI_RAG = "ai_rag"
    KG_NEO4J = "kg_neo4j"
    FEDERATED_LEARNING = "federated_learning"
    PHYSICS_MODELING = "physics_modeling"
    CERTIFICATE_MANAGER = "certificate_manager"


class WorkflowStatus(str, Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class ModuleInfo:
    """Information about a discovered module."""
    
    module_id: UUID = field(default_factory=uuid4)
    name: str = ""
    module_type: ModuleType = ModuleType.TWIN_REGISTRY
    version: str = "1.0.0"
    description: str = ""
    base_url: str = ""
    health_endpoint: str = "/health"
    api_endpoint: str = "/api"
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Set discovered_at and last_seen to current time if not provided."""
        if self.discovered_at is None:
            self.discovered_at = datetime.utcnow()
        if self.last_seen is None:
            self.last_seen = datetime.utcnow()


@dataclass
class ModuleHealth:
    """Health status of a module."""
    
    module_id: UUID
    status: ModuleStatus = ModuleStatus.UNKNOWN
    response_time_ms: Optional[float] = None
    last_check: datetime = field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set last_check to current time if not provided."""
        if self.last_check is None:
            self.last_check = datetime.utcnow()


@dataclass
class WorkflowStep:
    """A single step in a workflow."""
    
    step_id: UUID = field(default_factory=uuid4)
    module_name: str = ""
    operation: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    input_data: Optional[Any] = None
    output_data: Optional[Any] = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time_ms: Optional[float] = None
    
    def start(self):
        """Mark step as started."""
        self.status = WorkflowStatus.RUNNING
        self.started_at = datetime.utcnow()
    
    def complete(self, output_data: Any = None):
        """Mark step as completed."""
        self.status = WorkflowStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.output_data = output_data
        if self.started_at:
            self.execution_time_ms = (self.completed_at - self.started_at).total_seconds() * 1000
    
    def fail(self, error_message: str):
        """Mark step as failed."""
        self.status = WorkflowStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
        if self.started_at:
            self.execution_time_ms = (self.completed_at - self.started_at).total_seconds() * 1000


@dataclass
class WorkflowResult:
    """Result of a workflow execution."""
    
    workflow_id: UUID = field(default_factory=uuid4)
    workflow_name: str = ""
    steps: List[WorkflowStep] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PENDING
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    total_execution_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    final_output: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set started_at to current time if not provided."""
        if self.started_at is None:
            self.started_at = datetime.utcnow()
    
    def add_step(self, step: WorkflowStep):
        """Add a step to the workflow."""
        self.steps.append(step)
    
    def complete(self, final_output: Any = None):
        """Mark workflow as completed."""
        self.status = WorkflowStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.final_output = final_output
        if self.started_at:
            self.total_execution_time_ms = (self.completed_at - self.started_at).total_seconds() * 1000
    
    def fail(self, error_message: str):
        """Mark workflow as failed."""
        self.status = WorkflowStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
        if self.started_at:
            self.total_execution_time_ms = (self.completed_at - self.started_at).total_seconds() * 1000


@dataclass
class ModuleConnection:
    """Connection to a module."""
    
    module_info: ModuleInfo
    connection_id: UUID = field(default_factory=uuid4)
    established_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    last_activity: datetime = field(default_factory=datetime.utcnow)
    connection_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set timestamps to current time if not provided."""
        if self.established_at is None:
            self.established_at = datetime.utcnow()
        if self.last_activity is None:
            self.last_activity = datetime.utcnow()
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()
    
    def close(self):
        """Close the connection."""
        self.is_active = False
        self.last_activity = datetime.utcnow()
