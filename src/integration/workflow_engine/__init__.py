"""
Cross-Module Workflow Engine Package

This package provides workflow orchestration and management capabilities
for coordinating complex business processes across multiple external modules
within the AAS Data Modeling Engine.

The workflow engine enables:
- Workflow definition and management
- Task orchestration and scheduling
- Workflow monitoring and optimization
- Cross-module workflow coordination
"""

from .workflow_engine import WorkflowEngine
from .workflow_manager import WorkflowManager
from .task_orchestrator import TaskOrchestrator
from .workflow_monitor import WorkflowMonitor
from .models import (
    WorkflowDefinition,
    WorkflowInstance,
    WorkflowTask,
    TaskStatus,
    WorkflowStatus,
    WorkflowTrigger,
    WorkflowSchedule,
    TaskDependency,
    WorkflowMetrics,
    WorkflowPriority
)

__version__ = "1.0.0"
__author__ = "AAS Data Modeling Team"

__all__ = [
    "WorkflowEngine",
    "WorkflowManager",
    "TaskOrchestrator",
    "WorkflowMonitor",
    "WorkflowDefinition",
    "WorkflowInstance",
    "WorkflowTask",
    "TaskStatus",
    "WorkflowStatus",
    "WorkflowTrigger",
    "WorkflowSchedule",
    "TaskDependency",
    "WorkflowMetrics",
    "WorkflowPriority"
]
