"""
Data Models for Cross-Module Workflow Engine

This module defines the core data structures used by the workflow engine
for managing workflows, tasks, and orchestration across module boundaries.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Callable
from uuid import UUID, uuid4


class TaskStatus(str, Enum):
    """Status of individual workflow tasks."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class WorkflowStatus(str, Enum):
    """Status of workflow instances."""
    DRAFT = "draft"
    ACTIVE = "active"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    SUSPENDED = "suspended"


class WorkflowTrigger(str, Enum):
    """Types of workflow triggers."""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT_DRIVEN = "event_driven"
    DEPENDENCY_DRIVEN = "dependency_driven"
    API_CALL = "api_call"


class WorkflowPriority(str, Enum):
    """Priority levels for workflows."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class TaskDependency:
    """Represents a dependency between workflow tasks."""
    
    dependency_id: UUID = field(default_factory=uuid4)
    source_task_id: UUID = field(default_factory=uuid4)
    target_task_id: UUID = field(default_factory=uuid4)
    dependency_type: str = "completion"  # completion, success, failure
    condition: Optional[str] = None  # Optional condition expression
    timeout: Optional[timedelta] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "dependency_id": str(self.dependency_id),
            "source_task_id": str(self.source_task_id),
            "target_task_id": str(self.target_task_id),
            "dependency_type": self.dependency_type,
            "condition": self.condition,
            "timeout": str(self.timeout.total_seconds()) if self.timeout else None,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class WorkflowTask:
    """Represents a single task within a workflow."""
    
    task_id: UUID = field(default_factory=uuid4)
    task_name: str = ""
    task_description: str = ""
    task_type: str = ""  # module_operation, data_transformation, validation, etc.
    target_module: str = ""
    operation_name: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    timeout: Optional[timedelta] = None
    priority: WorkflowPriority = WorkflowPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[TaskDependency] = field(default_factory=list)
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "task_id": str(self.task_id),
            "task_name": self.task_name,
            "task_description": self.task_description,
            "task_type": self.task_type,
            "target_module": self.target_module,
            "operation_name": self.operation_name,
            "parameters": self.parameters,
            "retry_policy": self.retry_policy,
            "timeout": str(self.timeout.total_seconds()) if self.timeout else None,
            "priority": self.priority.value,
            "status": self.status.value,
            "dependencies": [dep.to_dict() for dep in self.dependencies],
            "result": self.result,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "metadata": self.metadata
        }


@dataclass
class WorkflowSchedule:
    """Represents a schedule for workflow execution."""
    
    schedule_id: UUID = field(default_factory=uuid4)
    cron_expression: Optional[str] = None
    interval_seconds: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    timezone: str = "UTC"
    is_active: bool = True
    max_executions: Optional[int] = None
    execution_count: int = 0
    last_execution: Optional[datetime] = None
    next_execution: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "schedule_id": str(self.schedule_id),
            "cron_expression": self.cron_expression,
            "interval_seconds": self.interval_seconds,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "timezone": self.timezone,
            "is_active": self.is_active,
            "max_executions": self.max_executions,
            "execution_count": self.execution_count,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "next_execution": self.next_execution.isoformat() if self.next_execution else None,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class WorkflowDefinition:
    """Represents a workflow template or definition."""
    
    workflow_id: UUID = field(default_factory=uuid4)
    workflow_name: str = ""
    workflow_description: str = ""
    version: str = "1.0.0"
    workflow_type: str = ""  # data_pipeline, business_process, etc.
    tasks: List[WorkflowTask] = field(default_factory=list)
    dependencies: List[TaskDependency] = field(default_factory=list)
    schedule: Optional[WorkflowSchedule] = None
    trigger: WorkflowTrigger = WorkflowTrigger.MANUAL
    priority: WorkflowPriority = WorkflowPriority.NORMAL
    timeout: Optional[timedelta] = None
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "workflow_id": str(self.workflow_id),
            "workflow_name": self.workflow_name,
            "workflow_description": self.workflow_description,
            "version": self.version,
            "workflow_type": self.workflow_type,
            "tasks": [task.to_dict() for task in self.tasks],
            "dependencies": [dep.to_dict() for dep in self.dependencies],
            "schedule": self.schedule.to_dict() if self.schedule else None,
            "trigger": self.trigger.value,
            "priority": self.priority.value,
            "timeout": str(self.timeout.total_seconds()) if self.timeout else None,
            "retry_policy": self.retry_policy,
            "is_active": self.is_active,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class WorkflowInstance:
    """Represents an instance of a workflow execution."""
    
    instance_id: UUID = field(default_factory=uuid4)
    workflow_id: UUID = field(default_factory=uuid4)
    workflow_name: str = ""
    status: WorkflowStatus = WorkflowStatus.DRAFT
    current_task: Optional[UUID] = None
    tasks: List[WorkflowTask] = field(default_factory=list)
    dependencies: List[TaskDependency] = field(default_factory=list)
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by: str = ""
    priority: WorkflowPriority = WorkflowPriority.NORMAL
    timeout: Optional[timedelta] = None
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    progress: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "instance_id": str(self.instance_id),
            "workflow_id": str(self.workflow_id),
            "workflow_name": self.workflow_name,
            "status": self.status.value,
            "current_task": str(self.current_task) if self.current_task else None,
            "tasks": [task.to_dict() for task in self.tasks],
            "dependencies": [dep.to_dict() for dep in self.dependencies],
            "input_data": self.input_data,
            "output_data": self.output_data,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_by": self.created_by,
            "priority": self.priority.value,
            "timeout": str(self.timeout.total_seconds()) if self.timeout else None,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "error_message": self.error_message,
            "progress": self.progress,
            "metadata": self.metadata
        }


@dataclass
class WorkflowMetrics:
    """Represents metrics and statistics for workflow execution."""
    
    metrics_id: UUID = field(default_factory=uuid4)
    workflow_id: Optional[UUID] = None
    instance_id: Optional[UUID] = None
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    cancelled_executions: int = 0
    average_execution_time: float = 0.0
    total_execution_time: float = 0.0
    min_execution_time: float = 0.0
    max_execution_time: float = 0.0
    success_rate: float = 0.0
    failure_rate: float = 0.0
    last_execution: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "metrics_id": str(self.metrics_id),
            "workflow_id": str(self.workflow_id) if self.workflow_id else None,
            "instance_id": str(self.instance_id) if self.instance_id else None,
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "failed_executions": self.failed_executions,
            "cancelled_executions": self.cancelled_executions,
            "average_execution_time": self.average_execution_time,
            "total_execution_time": self.total_execution_time,
            "min_execution_time": self.min_execution_time,
            "max_execution_time": self.max_execution_time,
            "success_rate": self.success_rate,
            "failure_rate": self.failure_rate,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "last_failure": self.last_failure.isoformat() if self.last_failure else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
