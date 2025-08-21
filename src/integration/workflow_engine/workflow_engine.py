"""
Core Workflow Engine Service

This module provides the main workflow engine that orchestrates workflow execution,
manages task dependencies, and coordinates cross-module operations within the
AAS Data Modeling Engine.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Callable
from uuid import UUID

from .models import (
    WorkflowDefinition,
    WorkflowInstance,
    WorkflowTask,
    TaskStatus,
    WorkflowStatus,
    WorkflowTrigger,
    TaskDependency,
    WorkflowPriority
)


logger = logging.getLogger(__name__)


class WorkflowEngine:
    """
    Core workflow engine that orchestrates workflow execution across modules.
    
    The workflow engine manages:
    - Workflow definitions and instances
    - Task execution and dependency resolution
    - Cross-module coordination
    - Workflow monitoring and optimization
    """
    
    def __init__(self):
        """Initialize the workflow engine."""
        self.workflow_definitions: Dict[UUID, WorkflowDefinition] = {}
        self.workflow_instances: Dict[UUID, WorkflowInstance] = {}
        self.running_workflows: Set[UUID] = set()
        self.task_executors: Dict[str, Callable] = {}
        self.module_connectors: Dict[str, Any] = {}
        self.is_running = False
        self._execution_task: Optional[asyncio.Task] = None
        
        # Performance tracking
        self.execution_metrics = {
            "total_workflows": 0,
            "completed_workflows": 0,
            "failed_workflows": 0,
            "active_workflows": 0
        }
        
        logger.info("Workflow engine initialized")
    
    async def start_engine(self) -> None:
        """Start the workflow engine."""
        if self.is_running:
            logger.warning("Workflow engine is already running")
            return
        
        self.is_running = True
        self._execution_task = asyncio.create_task(self._execution_loop())
        logger.info("Workflow engine started")
    
    async def stop_engine(self) -> None:
        """Stop the workflow engine."""
        if not self.is_running:
            logger.warning("Workflow engine is not running")
            return
        
        self.is_running = False
        
        if self._execution_task:
            self._execution_task.cancel()
            try:
                await self._execution_task
            except asyncio.CancelledError:
                pass
        
        # Wait for running workflows to complete
        if self.running_workflows:
            logger.info(f"Waiting for {len(self.running_workflows)} workflows to complete")
            await asyncio.sleep(5)  # Give workflows time to complete
        
        logger.info("Workflow engine stopped")
    
    def register_workflow_definition(self, definition: WorkflowDefinition) -> None:
        """Register a workflow definition."""
        self.workflow_definitions[definition.workflow_id] = definition
        logger.info(f"Registered workflow definition: {definition.workflow_name}")
    
    def unregister_workflow_definition(self, workflow_id: UUID) -> None:
        """Unregister a workflow definition."""
        if workflow_id in self.workflow_definitions:
            del self.workflow_definitions[workflow_id]
            logger.info(f"Unregistered workflow definition: {workflow_id}")
    
    def register_task_executor(self, task_type: str, executor: Callable) -> None:
        """Register a task executor for a specific task type."""
        self.task_executors[task_type] = executor
        logger.info(f"Registered task executor for type: {task_type}")
    
    def register_module_connector(self, module_name: str, connector: Any) -> None:
        """Register a module connector for cross-module communication."""
        self.module_connectors[module_name] = connector
        logger.info(f"Registered module connector: {module_name}")
    
    async def create_workflow_instance(
        self,
        workflow_id: UUID,
        input_data: Optional[Dict[str, Any]] = None,
        created_by: str = "",
        priority: WorkflowPriority = WorkflowPriority.NORMAL
    ) -> Optional[WorkflowInstance]:
        """Create a new workflow instance from a definition."""
        if workflow_id not in self.workflow_definitions:
            logger.error(f"Workflow definition not found: {workflow_id}")
            return None
        
        definition = self.workflow_definitions[workflow_id]
        
        # Create instance with copied tasks
        instance = WorkflowInstance(
            workflow_id=workflow_id,
            workflow_name=definition.workflow_name,
            tasks=[self._copy_task(task) for task in definition.tasks],
            dependencies=definition.dependencies.copy(),
            input_data=input_data or {},
            created_by=created_by,
            priority=priority,
            timeout=definition.timeout
        )
        
        self.workflow_instances[instance.instance_id] = instance
        self.execution_metrics["total_workflows"] += 1
        
        logger.info(f"Created workflow instance: {instance.instance_id} for {definition.workflow_name}")
        return instance
    
    async def start_workflow(self, instance_id: UUID) -> bool:
        """Start a workflow instance."""
        if instance_id not in self.workflow_instances:
            logger.error(f"Workflow instance not found: {instance_id}")
            return False
        
        instance = self.workflow_instances[instance_id]
        
        if instance.status != WorkflowStatus.DRAFT:
            logger.warning(f"Workflow instance {instance_id} is not in DRAFT status")
            return False
        
        # Validate dependencies
        if not self._validate_workflow_dependencies(instance):
            logger.error(f"Workflow instance {instance_id} has invalid dependencies")
            return False
        
        # Start workflow
        instance.status = WorkflowStatus.RUNNING
        instance.started_at = datetime.utcnow()
        self.running_workflows.add(instance_id)
        self.execution_metrics["active_workflows"] += 1
        
        logger.info(f"Started workflow instance: {instance_id}")
        return True
    
    async def pause_workflow(self, instance_id: UUID) -> bool:
        """Pause a running workflow instance."""
        if instance_id not in self.workflow_instances:
            return False
        
        instance = self.workflow_instances[instance_id]
        if instance.status == WorkflowStatus.RUNNING:
            instance.status = WorkflowStatus.PAUSED
            logger.info(f"Paused workflow instance: {instance_id}")
            return True
        
        return False
    
    async def resume_workflow(self, instance_id: UUID) -> bool:
        """Resume a paused workflow instance."""
        if instance_id not in self.workflow_instances:
            return False
        
        instance = self.workflow_instances[instance_id]
        if instance.status == WorkflowStatus.PAUSED:
            instance.status = WorkflowStatus.RUNNING
            logger.info(f"Resumed workflow instance: {instance_id}")
            return True
        
        return False
    
    async def cancel_workflow(self, instance_id: UUID) -> bool:
        """Cancel a workflow instance."""
        if instance_id not in self.workflow_instances:
            return False
        
        instance = self.workflow_instances[instance_id]
        if instance.status in [WorkflowStatus.RUNNING, WorkflowStatus.PAUSED]:
            instance.status = WorkflowStatus.CANCELLED
            instance.completed_at = datetime.utcnow()
            
            if instance_id in self.running_workflows:
                self.running_workflows.remove(instance_id)
                self.execution_metrics["active_workflows"] -= 1
            
            logger.info(f"Cancelled workflow instance: {instance_id}")
            return True
        
        return False
    
    def get_workflow_instance(self, instance_id: UUID) -> Optional[WorkflowInstance]:
        """Get a workflow instance by ID."""
        return self.workflow_instances.get(instance_id)
    
    def get_workflow_instances(
        self,
        status: Optional[WorkflowStatus] = None,
        workflow_id: Optional[UUID] = None
    ) -> List[WorkflowInstance]:
        """Get workflow instances with optional filtering."""
        instances = list(self.workflow_instances.values())
        
        if status:
            instances = [i for i in instances if i.status == status]
        
        if workflow_id:
            instances = [i for i in instances if i.workflow_id == workflow_id]
        
        return instances
    
    def get_workflow_definition(self, workflow_id: UUID) -> Optional[WorkflowDefinition]:
        """Get a workflow definition by ID."""
        return self.workflow_definitions.get(workflow_id)
    
    def get_workflow_definitions(self, workflow_type: Optional[str] = None) -> List[WorkflowDefinition]:
        """Get workflow definitions with optional filtering."""
        definitions = list(self.workflow_definitions.values())
        
        if workflow_type:
            definitions = [d for d in definitions if d.workflow_type == workflow_type]
        
        return definitions
    
    async def _execution_loop(self) -> None:
        """Main execution loop for processing workflows."""
        logger.info("Starting workflow execution loop")
        
        while self.is_running:
            try:
                # Process running workflows
                await self._process_running_workflows()
                
                # Check for scheduled workflows
                await self._check_scheduled_workflows()
                
                # Cleanup completed workflows
                await self._cleanup_completed_workflows()
                
                # Wait before next iteration
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                logger.info("Workflow execution loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in workflow execution loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
        
        logger.info("Workflow execution loop stopped")
    
    async def _process_running_workflows(self) -> None:
        """Process all running workflows."""
        for instance_id in list(self.running_workflows):
            try:
                instance = self.workflow_instances[instance_id]
                if instance.status != WorkflowStatus.RUNNING:
                    continue
                
                await self._execute_workflow_tasks(instance)
                
                # Check if workflow is complete
                if self._is_workflow_complete(instance):
                    await self._complete_workflow(instance)
                
            except Exception as e:
                logger.error(f"Error processing workflow {instance_id}: {e}")
                await self._handle_workflow_error(instance_id, str(e))
    
    async def _execute_workflow_tasks(self, instance: WorkflowInstance) -> None:
        """Execute tasks for a workflow instance."""
        for task in instance.tasks:
            if task.status == TaskStatus.PENDING and self._can_execute_task(task, instance):
                await self._execute_task(task, instance)
            elif task.status == TaskStatus.RETRYING and self._should_retry_task(task):
                await self._retry_task(task, instance)
    
    async def _execute_task(self, task: WorkflowTask, instance: WorkflowInstance) -> None:
        """Execute a single workflow task."""
        try:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            instance.current_task = task.task_id
            
            logger.info(f"Executing task: {task.task_name} in workflow {instance.instance_id}")
            
            # Execute task based on type
            if task.task_type == "module_operation":
                result = await self._execute_module_operation(task, instance)
            else:
                result = await self._execute_generic_task(task, instance)
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.result = result
            
            logger.info(f"Task completed: {task.task_name} in workflow {instance.instance_id}")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            
            logger.error(f"Task failed: {task.task_name} in workflow {instance.instance_id}: {e}")
            
            # Handle retry logic
            if task.retry_count < task.max_retries:
                await self._schedule_task_retry(task)
    
    async def _execute_module_operation(self, task: WorkflowTask, instance: WorkflowInstance) -> Dict[str, Any]:
        """Execute a module operation task."""
        if task.target_module not in self.module_connectors:
            raise ValueError(f"Module connector not found: {task.target_module}")
        
        connector = self.module_connectors[task.target_module]
        
        # This is a placeholder - in a real implementation, you would call the actual module
        # For now, we'll simulate the operation
        await asyncio.sleep(0.1)  # Simulate operation time
        
        return {
            "operation": task.operation_name,
            "module": task.target_module,
            "parameters": task.parameters,
            "result": f"Simulated result for {task.operation_name}",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_generic_task(self, task: WorkflowTask, instance: WorkflowInstance) -> Dict[str, Any]:
        """Execute a generic task."""
        if task.task_type in self.task_executors:
            executor = self.task_executors[task.task_type]
            return await executor(task, instance)
        else:
            # Default generic task execution
            await asyncio.sleep(0.1)  # Simulate task execution
            return {
                "task_type": task.task_type,
                "result": f"Generic execution result for {task.task_name}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _can_execute_task(self, task: WorkflowTask, instance: WorkflowInstance) -> bool:
        """Check if a task can be executed based on dependencies."""
        for dep in task.dependencies:
            source_task = self._find_task_by_id(dep.source_task_id, instance)
            if not source_task or source_task.status != TaskStatus.COMPLETED:
                return False
        return True
    
    def _should_retry_task(self, task: WorkflowTask) -> bool:
        """Check if a task should be retried."""
        if task.retry_count >= task.max_retries:
            return False
        
        # Simple retry logic - could be enhanced with exponential backoff
        return True
    
    async def _schedule_task_retry(self, task: WorkflowTask) -> None:
        """Schedule a task for retry."""
        task.retry_count += 1
        task.status = TaskStatus.RETRYING
        
        # Schedule retry after a delay
        asyncio.create_task(self._delayed_task_retry(task))
    
    async def _delayed_task_retry(self, task: WorkflowTask) -> None:
        """Retry a task after a delay."""
        await asyncio.sleep(2 ** task.retry_count)  # Exponential backoff
        
        if task.status == TaskStatus.RETRYING:
            task.status = TaskStatus.PENDING
    
    async def _retry_task(self, task: WorkflowTask, instance: WorkflowInstance) -> None:
        """Retry a failed task."""
        task.status = TaskStatus.PENDING
        task.error_message = None
        await self._execute_task(task, instance)
    
    def _is_workflow_complete(self, instance: WorkflowInstance) -> bool:
        """Check if a workflow instance is complete."""
        for task in instance.tasks:
            if task.status not in [TaskStatus.COMPLETED, TaskStatus.SKIPPED]:
                return False
        return True
    
    async def _complete_workflow(self, instance: WorkflowInstance) -> None:
        """Mark a workflow instance as complete."""
        instance.status = WorkflowStatus.COMPLETED
        instance.completed_at = datetime.utcnow()
        instance.progress = 100.0
        
        if instance.instance_id in self.running_workflows:
            self.running_workflows.remove(instance.instance_id)
            self.execution_metrics["active_workflows"] -= 1
        
        self.execution_metrics["completed_workflows"] += 1
        
        logger.info(f"Workflow instance completed: {instance.instance_id}")
    
    async def _handle_workflow_error(self, instance_id: UUID, error_message: str) -> None:
        """Handle workflow execution errors."""
        if instance_id in self.workflow_instances:
            instance = self.workflow_instances[instance_id]
            instance.status = WorkflowStatus.FAILED
            instance.error_message = error_message
            instance.completed_at = datetime.utcnow()
            
            if instance_id in self.running_workflows:
                self.running_workflows.remove(instance_id)
                self.execution_metrics["active_workflows"] -= 1
            
            self.execution_metrics["failed_workflows"] += 1
            
            logger.error(f"Workflow instance failed: {instance_id}: {error_message}")
    
    async def _check_scheduled_workflows(self) -> None:
        """Check for scheduled workflows that should start."""
        # This is a placeholder for scheduled workflow logic
        # In a real implementation, you would check cron expressions, intervals, etc.
        pass
    
    async def _cleanup_completed_workflows(self) -> None:
        """Clean up old completed workflows."""
        # This is a placeholder for cleanup logic
        # In a real implementation, you would remove old instances based on retention policies
        pass
    
    def _validate_workflow_dependencies(self, instance: WorkflowInstance) -> bool:
        """Validate workflow dependencies."""
        # This is a placeholder for dependency validation logic
        # In a real implementation, you would check for circular dependencies, etc.
        return True
    
    def _find_task_by_id(self, task_id: UUID, instance: WorkflowInstance) -> Optional[WorkflowTask]:
        """Find a task by ID within a workflow instance."""
        for task in instance.tasks:
            if task.task_id == task_id:
                return task
        return None
    
    def _copy_task(self, task: WorkflowTask) -> WorkflowTask:
        """Create a copy of a task for workflow instance creation."""
        # This is a simplified copy - in a real implementation, you might want deep copying
        return WorkflowTask(
            task_id=task.task_id,
            task_name=task.task_name,
            task_description=task.task_description,
            task_type=task.task_type,
            target_module=task.target_module,
            operation_name=task.operation_name,
            parameters=task.parameters.copy(),
            retry_policy=task.retry_policy.copy(),
            timeout=task.timeout,
            priority=task.priority,
            dependencies=task.dependencies.copy(),
            max_retries=task.max_retries,
            metadata=task.metadata.copy()
        )
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get the current status of the workflow engine."""
        return {
            "is_running": self.is_running,
            "total_workflows": self.execution_metrics["total_workflows"],
            "active_workflows": self.execution_metrics["active_workflows"],
            "completed_workflows": self.execution_metrics["completed_workflows"],
            "failed_workflows": self.execution_metrics["failed_workflows"],
            "registered_definitions": len(self.workflow_definitions),
            "registered_executors": len(self.task_executors),
            "registered_connectors": len(self.module_connectors)
        }
