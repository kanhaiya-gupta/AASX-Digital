"""
Workflow Service - Business Domain Service
=========================================

Manages business workflows, processes, and automation.
This service provides comprehensive workflow management capabilities.

Features:
- Workflow definition and execution
- Process automation and orchestration
- Task routing and assignment
- Workflow monitoring and analytics
- Business rule engine integration
"""

import logging
import asyncio
import json
from typing import Dict, Any, List, Optional, Set, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from ..base import BaseService
from ...models.base_model import BaseModel
from ...repositories.base_repository import BaseRepository
from ...models.enums import EventType, SystemCategory, SecurityLevel

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow status values."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


class TaskStatus(Enum):
    """Task status values."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowTriggerType(Enum):
    """Workflow trigger types."""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT_DRIVEN = "event_driven"
    CONDITION_BASED = "condition_based"


@dataclass
class WorkflowDefinition:
    """Workflow definition structure."""
    workflow_id: str
    name: str
    description: str
    version: str
    status: WorkflowStatus
    org_id: str
    created_by: str
    trigger_type: WorkflowTriggerType
    trigger_config: Dict[str, Any]
    steps: List[Dict[str, Any]]
    variables: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass
class WorkflowInstance:
    """Workflow instance structure."""
    instance_id: str
    workflow_id: str
    name: str
    status: WorkflowStatus
    org_id: str
    initiated_by: str
    current_step: int
    variables: Dict[str, Any]
    start_time: datetime
    end_time: Optional[datetime]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass
class WorkflowTask:
    """Workflow task structure."""
    task_id: str
    instance_id: str
    step_id: str
    name: str
    description: str
    status: TaskStatus
    assignee_id: Optional[str]
    due_date: Optional[datetime]
    completed_date: Optional[datetime]
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    error_message: Optional[str]
    retry_count: int
    max_retries: int
    created_at: datetime
    updated_at: datetime


@dataclass
class WorkflowEvent:
    """Workflow event structure."""
    event_id: str
    workflow_id: str
    instance_id: Optional[str]
    event_type: str
    event_data: Dict[str, Any]
    timestamp: datetime
    user_id: Optional[str]
    metadata: Dict[str, Any]


class WorkflowService(BaseService[BaseModel, BaseRepository]):
    """
    Business domain service for workflow management.
    
    Provides:
    - Workflow definition and execution
    - Process automation and orchestration
    - Task routing and assignment
    - Workflow monitoring and analytics
    - Business rule engine integration
    """

    def __init__(self, repository: Optional[BaseRepository] = None):
        super().__init__(repository, "WorkflowService")
        
        # Workflow storage
        self._workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self._workflow_instances: Dict[str, WorkflowInstance] = {}
        self._workflow_tasks: Dict[str, WorkflowTask] = {}
        self._workflow_events: Dict[str, WorkflowEvent] = {}
        
        # Workflow relationships
        self._org_workflows: Dict[str, Set[str]] = {}  # org_id -> workflows
        self._instance_tasks: Dict[str, Set[str]] = {}  # instance_id -> tasks
        self._user_tasks: Dict[str, Set[str]] = {}  # user_id -> tasks
        
        # Workflow execution
        self._active_instances: Set[str] = set()
        self._task_queue: List[str] = []
        self._execution_engine: Optional[Callable] = None
        
        # Configuration
        self._workflow_config = {
            'max_concurrent_instances': 100,
            'max_task_retries': 3,
            'task_timeout_seconds': 3600,  # 1 hour
            'cleanup_interval_hours': 24
        }
        
        logger.info("Workflow service initialized")

    async def _initialize_service_resources(self) -> None:
        """Initialize workflow service resources."""
        # Load existing workflows from repository
        await self._load_workflows()
        
        # Build relationship indexes
        await self._build_workflow_indexes()
        
        # Start workflow execution engine
        await self._start_execution_engine()
        
        logger.info("Workflow service resources initialized")

    async def _cleanup_service_resources(self) -> None:
        """Cleanup workflow service resources."""
        # Stop execution engine
        await self._stop_execution_engine()
        
        # Save workflows to repository
        await self._save_workflows()
        
        # Clear in-memory data
        self._workflow_definitions.clear()
        self._workflow_instances.clear()
        self._workflow_tasks.clear()
        self._workflow_events.clear()
        self._org_workflows.clear()
        self._instance_tasks.clear()
        self._user_tasks.clear()
        self._active_instances.clear()
        self._task_queue.clear()
        
        logger.info("Workflow service resources cleaned up")

    async def get_service_info(self) -> Dict[str, Any]:
        """Get workflow service information."""
        return {
            'service_name': self.service_name,
            'total_workflows': len(self._workflow_definitions),
            'total_instances': len(self._workflow_instances),
            'total_tasks': len(self._workflow_tasks),
            'active_instances': len(self._active_instances),
            'queued_tasks': len(self._task_queue),
            'workflow_statuses': [s.value for s in WorkflowStatus],
            'task_statuses': [s.value for s in TaskStatus],
            'health_status': self.health_status,
            'uptime': str(self.get_uptime()),
            'last_health_check': self.last_health_check.isoformat()
        }

    # Workflow Definition Management

    async def create_workflow(self, name: str, description: str, org_id: str,
                            created_by: str, steps: List[Dict[str, Any]],
                            trigger_type: WorkflowTriggerType = WorkflowTriggerType.MANUAL,
                            trigger_config: Dict[str, Any] = None,
                            variables: Dict[str, Any] = None,
                            **kwargs) -> Optional[str]:
        """
        Create a new workflow definition.
        
        Args:
            name: Workflow name
            description: Workflow description
            org_id: Organization ID
            created_by: User ID who created the workflow
            steps: List of workflow steps
            trigger_type: Type of workflow trigger
            trigger_config: Trigger configuration
            variables: Workflow variables
            **kwargs: Additional workflow properties
            
        Returns:
            Workflow ID if successful, None otherwise
        """
        try:
            # Validate workflow data
            if not await self._validate_workflow_data(name, org_id, steps):
                return None
            
            # Generate workflow ID
            workflow_id = f"wf_{name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create workflow definition
            workflow_def = WorkflowDefinition(
                workflow_id=workflow_id,
                name=name,
                description=description,
                version="1.0.0",
                status=WorkflowStatus.DRAFT,
                org_id=org_id,
                created_by=created_by,
                trigger_type=trigger_type,
                trigger_config=trigger_config or {},
                steps=steps,
                variables=variables or {},
                metadata=kwargs.get('metadata', {}),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Store workflow definition
            self._workflow_definitions[workflow_id] = workflow_def
            
            # Update indexes
            await self._update_workflow_indexes(workflow_id, workflow_def)
            
            # Log audit event
            await self.log_audit_event(
                EventType.PROJECT_CREATED,
                SystemCategory.APPLICATION,
                f"Workflow created: {name}",
                {'workflow_id': workflow_id, 'org_id': org_id, 'steps_count': len(steps)},
                SecurityLevel.INTERNAL
            )
            
            logger.info(f"Workflow created: {workflow_id} ({name})")
            return workflow_id
            
        except Exception as e:
            logger.error(f"Failed to create workflow {name}: {e}")
            return None

    async def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Get workflow definition by ID."""
        try:
            return self._workflow_definitions.get(workflow_id)
        except Exception as e:
            logger.error(f"Failed to get workflow {workflow_id}: {e}")
            return None

    async def update_workflow(self, workflow_id: str, **kwargs) -> bool:
        """Update workflow definition."""
        try:
            if workflow_id not in self._workflow_definitions:
                logger.warning(f"Workflow {workflow_id} not found")
                return False
            
            workflow_def = self._workflow_definitions[workflow_id]
            
            # Check if workflow can be updated
            if workflow_def.status == WorkflowStatus.ACTIVE:
                logger.warning(f"Cannot update active workflow {workflow_id}")
                return False
            
            # Update allowed fields
            allowed_fields = {
                'name', 'description', 'steps', 'variables', 'trigger_config', 'metadata'
            }
            
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(workflow_def, field):
                    setattr(workflow_def, field, value)
            
            workflow_def.updated_at = datetime.now()
            
            # Log audit event
            await self.log_audit_event(
                EventType.PROJECT_UPDATED,
                SystemCategory.APPLICATION,
                f"Workflow updated: {workflow_id}",
                {'workflow_id': workflow_id, 'updated_fields': list(kwargs.keys())},
                SecurityLevel.INTERNAL
            )
            
            logger.info(f"Workflow updated: {workflow_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update workflow {workflow_id}: {e}")
            return False

    async def activate_workflow(self, workflow_id: str) -> bool:
        """Activate a workflow definition."""
        try:
            if workflow_id not in self._workflow_definitions:
                logger.warning(f"Workflow {workflow_id} not found")
                return False
            
            workflow_def = self._workflow_definitions[workflow_id]
            
            # Validate workflow before activation
            if not await self._validate_workflow_for_activation(workflow_def):
                return False
            
            # Activate workflow
            workflow_def.status = WorkflowStatus.ACTIVE
            workflow_def.updated_at = datetime.now()
            
            # Log audit event
            await self.log_audit_event(
                EventType.PROJECT_UPDATED,
                SystemCategory.APPLICATION,
                f"Workflow activated: {workflow_id}",
                {'workflow_id': workflow_id, 'name': workflow_def.name},
                SecurityLevel.INTERNAL
            )
            
            logger.info(f"Workflow activated: {workflow_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to activate workflow {workflow_id}: {e}")
            return False

    # Workflow Execution

    async def start_workflow(self, workflow_id: str, initiated_by: str,
                           variables: Dict[str, Any] = None,
                           metadata: Dict[str, Any] = None) -> Optional[str]:
        """
        Start a new workflow instance.
        
        Args:
            workflow_id: Workflow definition ID
            initiated_by: User ID who initiated the workflow
            variables: Initial workflow variables
            metadata: Additional metadata
            
        Returns:
            Instance ID if successful, None otherwise
        """
        try:
            if workflow_id not in self._workflow_definitions:
                logger.warning(f"Workflow {workflow_id} not found")
                return False
            
            workflow_def = self._workflow_definitions[workflow_id]
            
            # Check if workflow is active
            if workflow_def.status != WorkflowStatus.ACTIVE:
                logger.warning(f"Cannot start inactive workflow {workflow_id}")
                return None
            
            # Check concurrent instance limit
            if len(self._active_instances) >= self._workflow_config['max_concurrent_instances']:
                logger.warning("Maximum concurrent workflow instances reached")
                return None
            
            # Generate instance ID
            instance_id = f"inst_{workflow_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            # Create workflow instance
            instance = WorkflowInstance(
                instance_id=instance_id,
                workflow_id=workflow_id,
                name=workflow_def.name,
                status=WorkflowStatus.ACTIVE,
                org_id=workflow_def.org_id,
                initiated_by=initiated_by,
                current_step=0,
                variables=variables or {},
                start_time=datetime.now(),
                end_time=None,
                metadata=metadata or {},
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Store instance
            self._workflow_instances[instance_id] = instance
            self._active_instances.add(instance_id)
            
            # Update indexes
            await self._update_instance_indexes(instance_id, instance)
            
            # Create initial tasks
            await self._create_workflow_tasks(instance_id, workflow_def)
            
            # Add to execution queue
            self._task_queue.append(instance_id)
            
            # Log audit event
            await self.log_audit_event(
                EventType.PROJECT_CREATED,
                SystemCategory.APPLICATION,
                f"Workflow instance started: {workflow_id}",
                {'instance_id': instance_id, 'workflow_id': workflow_id, 'initiated_by': initiated_by},
                SecurityLevel.INTERNAL
            )
            
            logger.info(f"Workflow instance started: {instance_id} for workflow {workflow_id}")
            return instance_id
            
        except Exception as e:
            logger.error(f"Failed to start workflow {workflow_id}: {e}")
            return None

    async def get_workflow_instance(self, instance_id: str) -> Optional[WorkflowInstance]:
        """Get workflow instance by ID."""
        try:
            return self._workflow_instances.get(instance_id)
        except Exception as e:
            logger.error(f"Failed to get workflow instance {instance_id}: {e}")
            return None

    async def get_instance_tasks(self, instance_id: str) -> List[WorkflowTask]:
        """Get all tasks for a workflow instance."""
        try:
            if instance_id not in self._instance_tasks:
                return []
            
            return [self._workflow_tasks[task_id] for task_id in self._instance_tasks[instance_id] 
                   if task_id in self._workflow_tasks]
        except Exception as e:
            logger.error(f"Failed to get tasks for instance {instance_id}: {e}")
            return []

    # Task Management

    async def assign_task(self, task_id: str, assignee_id: str) -> bool:
        """Assign a task to a user."""
        try:
            if task_id not in self._workflow_tasks:
                logger.warning(f"Task {task_id} not found")
                return False
            
            task = self._workflow_tasks[task_id]
            
            # Check if task can be assigned
            if task.status != TaskStatus.PENDING:
                logger.warning(f"Task {task_id} is not in pending status")
                return False
            
            # Assign task
            task.assignee_id = assignee_id
            task.status = TaskStatus.ASSIGNED
            task.updated_at = datetime.now()
            
            # Update user task index
            if assignee_id not in self._user_tasks:
                self._user_tasks[assignee_id] = set()
            self._user_tasks[assignee_id].add(task_id)
            
            # Log audit event
            await self.log_audit_event(
                EventType.PROJECT_UPDATED,
                SystemCategory.APPLICATION,
                f"Task assigned: {task_id}",
                {'task_id': task_id, 'assignee_id': assignee_id, 'instance_id': task.instance_id},
                SecurityLevel.INTERNAL
            )
            
            logger.info(f"Task {task_id} assigned to {assignee_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to assign task {task_id}: {e}")
            return False

    async def start_task(self, task_id: str) -> bool:
        """Start a task execution."""
        try:
            if task_id not in self._workflow_tasks:
                logger.warning(f"Task {task_id} not found")
                return False
            
            task = self._workflow_tasks[task_id]
            
            # Check if task can be started
            if task.status not in [TaskStatus.ASSIGNED, TaskStatus.WAITING]:
                logger.warning(f"Task {task_id} cannot be started in current status")
                return False
            
            # Start task
            task.status = TaskStatus.IN_PROGRESS
            task.updated_at = datetime.now()
            
            logger.info(f"Task {task_id} started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start task {task_id}: {e}")
            return False

    async def complete_task(self, task_id: str, output_data: Dict[str, Any] = None) -> bool:
        """Complete a task execution."""
        try:
            if task_id not in self._workflow_tasks:
                logger.warning(f"Task {task_id} not found")
                return False
            
            task = self._workflow_tasks[task_id]
            
            # Check if task can be completed
            if task.status != TaskStatus.IN_PROGRESS:
                logger.warning(f"Task {task_id} is not in progress")
                return False
            
            # Complete task
            task.status = TaskStatus.COMPLETED
            task.completed_date = datetime.now()
            task.output_data = output_data or {}
            task.updated_at = datetime.now()
            
            # Update workflow instance
            await self._advance_workflow_instance(task.instance_id)
            
            logger.info(f"Task {task_id} completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to complete task {task_id}: {e}")
            return False

    async def fail_task(self, task_id: str, error_message: str) -> bool:
        """Mark a task as failed."""
        try:
            if task_id not in self._workflow_tasks:
                logger.warning(f"Task {task_id} not found")
                return False
            
            task = self._workflow_tasks[task_id]
            
            # Check if task can be failed
            if task.status not in [TaskStatus.IN_PROGRESS, TaskStatus.ASSIGNED]:
                logger.warning(f"Task {task_id} cannot be failed in current status")
                return False
            
            # Check retry limit
            if task.retry_count < task.max_retries:
                # Retry task
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                task.error_message = error_message
                task.updated_at = datetime.now()
                
                logger.info(f"Task {task_id} failed, retrying ({task.retry_count}/{task.max_retries})")
            else:
                # Mark as permanently failed
                task.status = TaskStatus.FAILED
                task.error_message = error_message
                task.updated_at = datetime.now()
                
                # Mark workflow instance as failed
                await self._mark_instance_failed(task.instance_id, error_message)
                
                logger.warning(f"Task {task_id} failed permanently after {task.max_retries} retries")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to fail task {task_id}: {e}")
            return False

    # Workflow Execution Engine

    async def _start_execution_engine(self) -> None:
        """Start the workflow execution engine."""
        try:
            logger.info("Starting workflow execution engine")
            
            # Start background task processing
            asyncio.create_task(self._process_task_queue())
            
        except Exception as e:
            logger.error(f"Failed to start execution engine: {e}")

    async def _stop_execution_engine(self) -> None:
        """Stop the workflow execution engine."""
        try:
            logger.info("Stopping workflow execution engine")
            
            # Cancel all active instances
            for instance_id in list(self._active_instances):
                await self._cancel_workflow_instance(instance_id)
            
        except Exception as e:
            logger.error(f"Failed to stop execution engine: {e}")

    async def _process_task_queue(self) -> None:
        """Process the task queue."""
        try:
            while True:
                if self._task_queue:
                    instance_id = self._task_queue.pop(0)
                    await self._execute_workflow_instance(instance_id)
                
                await asyncio.sleep(1)  # Process every second
                
        except Exception as e:
            logger.error(f"Task queue processing error: {e}")

    async def _execute_workflow_instance(self, instance_id: str) -> None:
        """Execute a workflow instance."""
        try:
            if instance_id not in self._workflow_instances:
                return
            
            instance = self._workflow_instances[instance_id]
            
            # Get current step
            current_step = instance.current_step
            if current_step >= len(instance.steps):
                # Workflow completed
                await self._complete_workflow_instance(instance_id)
                return
            
            # Execute current step
            step_config = instance.steps[current_step]
            await self._execute_workflow_step(instance_id, step_config)
            
        except Exception as e:
            logger.error(f"Failed to execute workflow instance {instance_id}: {e}")
            await self._mark_instance_failed(instance_id, str(e))

    async def _execute_workflow_step(self, instance_id: str, step_config: Dict[str, Any]) -> None:
        """Execute a single workflow step."""
        try:
            step_type = step_config.get('type', 'task')
            
            if step_type == 'task':
                # Create task for this step
                await self._create_task_for_step(instance_id, step_config)
            elif step_type == 'condition':
                # Evaluate condition
                await self._evaluate_condition(instance_id, step_config)
            elif step_type == 'parallel':
                # Execute parallel steps
                await self._execute_parallel_steps(instance_id, step_config)
            else:
                logger.warning(f"Unknown step type: {step_type}")
                
        except Exception as e:
            logger.error(f"Failed to execute workflow step: {e}")

    # Workflow Instance Management

    async def _advance_workflow_instance(self, instance_id: str) -> None:
        """Advance workflow instance to next step."""
        try:
            if instance_id not in self._workflow_instances:
                return
            
            instance = self._workflow_instances[instance_id]
            
            # Check if all current tasks are completed
            instance_tasks = await self.get_instance_tasks(instance_id)
            current_step_tasks = [t for t in instance_tasks if t.step_id == str(instance.current_step)]
            
            if all(t.status == TaskStatus.COMPLETED for t in current_step_tasks):
                # Move to next step
                instance.current_step += 1
                instance.updated_at = datetime.now()
                
                # Add back to execution queue
                self._task_queue.append(instance_id)
                
                logger.info(f"Workflow instance {instance_id} advanced to step {instance.current_step}")
                
        except Exception as e:
            logger.error(f"Failed to advance workflow instance {instance_id}: {e}")

    async def _complete_workflow_instance(self, instance_id: str) -> None:
        """Mark workflow instance as completed."""
        try:
            if instance_id not in self._workflow_instances:
                return
            
            instance = self._workflow_instances[instance_id]
            instance.status = WorkflowStatus.COMPLETED
            instance.end_time = datetime.now()
            instance.updated_at = datetime.now()
            
            # Remove from active instances
            self._active_instances.discard(instance_id)
            
            logger.info(f"Workflow instance {instance_id} completed")
            
        except Exception as e:
            logger.error(f"Failed to complete workflow instance {instance_id}: {e}")

    async def _mark_instance_failed(self, instance_id: str, error_message: str) -> None:
        """Mark workflow instance as failed."""
        try:
            if instance_id not in self._workflow_instances:
                return
            
            instance = self._workflow_instances[instance_id]
            instance.status = WorkflowStatus.ERROR
            instance.end_time = datetime.now()
            instance.updated_at = datetime.now()
            
            # Remove from active instances
            self._active_instances.discard(instance_id)
            
            logger.error(f"Workflow instance {instance_id} failed: {error_message}")
            
        except Exception as e:
            logger.error(f"Failed to mark instance {instance_id} as failed: {e}")

    async def _cancel_workflow_instance(self, instance_id: str) -> None:
        """Cancel a workflow instance."""
        try:
            if instance_id not in self._workflow_instances:
                return
            
            instance = self._workflow_instances[instance_id]
            instance.status = WorkflowStatus.CANCELLED
            instance.end_time = datetime.now()
            instance.updated_at = datetime.now()
            
            # Cancel all pending tasks
            instance_tasks = await self.get_instance_tasks(instance_id)
            for task in instance_tasks:
                if task.status in [TaskStatus.PENDING, TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS]:
                    task.status = TaskStatus.CANCELLED
                    task.updated_at = datetime.now()
            
            # Remove from active instances
            self._active_instances.discard(instance_id)
            
            logger.info(f"Workflow instance {instance_id} cancelled")
            
        except Exception as e:
            logger.error(f"Failed to cancel workflow instance {instance_id}: {e}")

    # Task Creation and Management

    async def _create_workflow_tasks(self, instance_id: str, workflow_def: WorkflowDefinition) -> None:
        """Create tasks for workflow instance."""
        try:
            instance = self._workflow_instances[instance_id]
            current_step = instance.current_step
            
            if current_step >= len(workflow_def.steps):
                return
            
            step_config = workflow_def.steps[current_step]
            
            if step_config.get('type') == 'task':
                await self._create_task_for_step(instance_id, step_config)
                
        except Exception as e:
            logger.error(f"Failed to create workflow tasks: {e}")

    async def _create_task_for_step(self, instance_id: str, step_config: Dict[str, Any]) -> None:
        """Create a task for a workflow step."""
        try:
            task_id = f"task_{instance_id}_{step_config.get('id', 'step')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            task = WorkflowTask(
                task_id=task_id,
                instance_id=instance_id,
                step_id=str(step_config.get('id', '')),
                name=step_config.get('name', 'Unnamed Task'),
                description=step_config.get('description', ''),
                status=TaskStatus.PENDING,
                assignee_id=None,
                due_date=None,
                completed_date=None,
                input_data=step_config.get('input', {}),
                output_data={},
                error_message=None,
                retry_count=0,
                max_retries=step_config.get('max_retries', self._workflow_config['max_task_retries']),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Store task
            self._workflow_tasks[task_id] = task
            
            # Update indexes
            await self._update_task_indexes(task_id, task)
            
            logger.info(f"Task created: {task_id} for step {step_config.get('id')}")
            
        except Exception as e:
            logger.error(f"Failed to create task for step: {e}")

    # Validation Methods

    async def _validate_workflow_data(self, name: str, org_id: str, steps: List[Dict[str, Any]]) -> bool:
        """Validate workflow data before creation."""
        try:
            # Check name uniqueness within organization
            for workflow in self._workflow_definitions.values():
                if workflow.org_id == org_id and workflow.name.lower() == name.lower():
                    logger.warning(f"Workflow name '{name}' already exists in organization {org_id}")
                    return False
            
            # Validate steps
            if not steps:
                logger.warning("Workflow must have at least one step")
                return False
            
            for i, step in enumerate(steps):
                if 'type' not in step:
                    logger.warning(f"Step {i} missing type")
                    return False
                
                if 'id' not in step:
                    logger.warning(f"Step {i} missing ID")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Workflow validation error: {e}")
            return False

    async def _validate_workflow_for_activation(self, workflow_def: WorkflowDefinition) -> bool:
        """Validate workflow before activation."""
        try:
            # Check if workflow has steps
            if not workflow_def.steps:
                logger.warning(f"Workflow {workflow_def.workflow_id} has no steps")
                return False
            
            # Validate step configuration
            for i, step in enumerate(workflow_def.steps):
                if step.get('type') == 'task':
                    if 'name' not in step:
                        logger.warning(f"Task step {i} missing name")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Workflow activation validation error: {e}")
            return False

    # Index Management

    async def _update_workflow_indexes(self, workflow_id: str, workflow_def: WorkflowDefinition) -> None:
        """Update workflow indexes."""
        try:
            # Organization index
            if workflow_def.org_id not in self._org_workflows:
                self._org_workflows[workflow_def.org_id] = set()
            self._org_workflows[workflow_def.org_id].add(workflow_id)
            
        except Exception as e:
            logger.error(f"Failed to update workflow indexes: {e}")

    async def _update_instance_indexes(self, instance_id: str, instance: WorkflowInstance) -> None:
        """Update instance indexes."""
        try:
            # Organization workflows (inherited from workflow definition)
            workflow_def = self._workflow_definitions.get(instance.workflow_id)
            if workflow_def and workflow_def.org_id not in self._org_workflows:
                self._org_workflows[workflow_def.org_id] = set()
            if workflow_def:
                self._org_workflows[workflow_def.org_id].add(instance.workflow_id)
            
        except Exception as e:
            logger.error(f"Failed to update instance indexes: {e}")

    async def _update_task_indexes(self, task_id: str, task: WorkflowTask) -> None:
        """Update task indexes."""
        try:
            # Instance tasks index
            if task.instance_id not in self._instance_tasks:
                self._instance_tasks[task.instance_id] = set()
            self._instance_tasks[task.instance_id].add(task_id)
            
            # User tasks index (if assigned)
            if task.assignee_id:
                if task.assignee_id not in self._user_tasks:
                    self._user_tasks[task.assignee_id] = set()
                self._user_tasks[task.assignee_id].add(task_id)
            
        except Exception as e:
            logger.error(f"Failed to update task indexes: {e}")

    # Data Loading and Saving

    async def _load_workflows(self) -> None:
        """Load workflows from repository."""
        try:
            # This would typically load from a database or file
            logger.info("Loading workflows from repository")
            
        except Exception as e:
            logger.error(f"Failed to load workflows: {e}")

    async def _save_workflows(self) -> None:
        """Save workflows to repository."""
        try:
            # This would typically save to a database or file
            logger.info("Saving workflows to repository")
            
        except Exception as e:
            logger.error(f"Failed to save workflows: {e}")

    async def _build_workflow_indexes(self) -> None:
        """Build workflow indexes from loaded data."""
        try:
            # Build all indexes from loaded data
            for workflow_id, workflow_def in self._workflow_definitions.items():
                await self._update_workflow_indexes(workflow_id, workflow_def)
            
            for instance_id, instance in self._workflow_instances.items():
                await self._update_instance_indexes(instance_id, instance)
            
            for task_id, task in self._workflow_tasks.items():
                await self._update_task_indexes(task_id, task)
            
            logger.info("Workflow indexes built successfully")
            
        except Exception as e:
            logger.error(f"Failed to build workflow indexes: {e}")

    # Business Intelligence

    async def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get comprehensive workflow statistics."""
        try:
            stats = {
                'total_workflows': len(self._workflow_definitions),
                'total_instances': len(self._workflow_instances),
                'total_tasks': len(self._workflow_tasks),
                'workflow_status_distribution': {},
                'instance_status_distribution': {},
                'task_status_distribution': {},
                'execution_metrics': {},
                'performance_metrics': {}
            }
            
            # Count by workflow status
            for workflow in self._workflow_definitions.values():
                status = workflow.status.value
                stats['workflow_status_distribution'][status] = stats['workflow_status_distribution'].get(status, 0) + 1
            
            # Count by instance status
            for instance in self._workflow_instances.values():
                status = instance.status.value
                stats['instance_status_distribution'][status] = stats['instance_status_distribution'].get(status, 0) + 1
            
            # Count by task status
            for task in self._workflow_tasks.values():
                status = task.status.value
                stats['task_status_distribution'][status] = stats['task_status_distribution'].get(status, 0) + 1
            
            # Execution metrics
            active_instances = len(self._active_instances)
            queued_tasks = len(self._task_queue)
            completed_instances = len([i for i in self._workflow_instances.values() if i.status == WorkflowStatus.COMPLETED])
            failed_instances = len([i for i in self._workflow_instances.values() if i.status == WorkflowStatus.ERROR])
            
            stats['execution_metrics'] = {
                'active_instances': active_instances,
                'queued_tasks': queued_tasks,
                'completed_instances': completed_instances,
                'failed_instances': failed_instances,
                'success_rate': completed_instances / (completed_instances + failed_instances) if (completed_instances + failed_instances) > 0 else 0
            }
            
            # Performance metrics
            if completed_instances > 0:
                completion_times = []
                for instance in self._workflow_instances.values():
                    if instance.status == WorkflowStatus.COMPLETED and instance.end_time:
                        duration = (instance.end_time - instance.start_time).total_seconds()
                        completion_times.append(duration)
                
                if completion_times:
                    stats['performance_metrics'] = {
                        'average_completion_time_seconds': sum(completion_times) / len(completion_times),
                        'min_completion_time_seconds': min(completion_times),
                        'max_completion_time_seconds': max(completion_times)
                    }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get workflow statistics: {e}")
            return {'error': str(e)}
