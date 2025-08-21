"""
Task Orchestrator Service

This module provides task scheduling, execution coordination, and resource
management capabilities for the cross-module workflow engine.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Callable, Tuple
from uuid import UUID, uuid4

from .models import (
    WorkflowTask,
    TaskStatus,
    WorkflowPriority,
    TaskDependency
)


logger = logging.getLogger(__name__)


class TaskOrchestrator:
    """
    Orchestrates task execution, scheduling, and resource management.
    
    The task orchestrator handles:
    - Task scheduling and prioritization
    - Resource allocation and management
    - Parallel execution coordination
    - Task dependency resolution
    - Performance optimization
    """
    
    def __init__(self, max_concurrent_tasks: int = 10):
        """Initialize the task orchestrator."""
        self.max_concurrent_tasks = max_concurrent_tasks
        self.running_tasks: Set[UUID] = set()
        self.queued_tasks: List[Tuple[WorkflowTask, float]] = []  # (task, priority_score)
        self.completed_tasks: Dict[UUID, WorkflowTask] = {}
        self.failed_tasks: Dict[UUID, WorkflowTask] = {}
        
        # Resource tracking
        self.module_resources: Dict[str, Dict[str, Any]] = {}
        self.resource_locks: Dict[str, asyncio.Lock] = {}
        
        # Performance metrics
        self.execution_metrics = {
            "total_tasks_executed": 0,
            "total_execution_time": 0.0,
            "average_execution_time": 0.0,
            "tasks_per_second": 0.0,
            "resource_utilization": 0.0
        }
        
        # Task executors
        self.task_executors: Dict[str, Callable] = {}
        self.module_connectors: Dict[str, Any] = {}
        
        # Background tasks
        self.is_running = False
        self._orchestration_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        logger.info(f"Task orchestrator initialized with max {max_concurrent_tasks} concurrent tasks")
    
    async def start_orchestrator(self) -> None:
        """Start the task orchestrator."""
        if self.is_running:
            logger.warning("Task orchestrator is already running")
            return
        
        self.is_running = True
        self._orchestration_task = asyncio.create_task(self._orchestration_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Task orchestrator started")
    
    async def stop_orchestrator(self) -> None:
        """Stop the task orchestrator."""
        if not self.is_running:
            logger.warning("Task orchestrator is not running")
            return
        
        self.is_running = False
        
        # Cancel background tasks
        if self._orchestration_task:
            self._orchestration_task.cancel()
            try:
                await self._orchestration_task
            except asyncio.CancelledError:
                pass
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Wait for running tasks to complete
        if self.running_tasks:
            logger.info(f"Waiting for {len(self.running_tasks)} tasks to complete")
            await asyncio.sleep(5)  # Give tasks time to complete
        
        logger.info("Task orchestrator stopped")
    
    def register_task_executor(self, task_type: str, executor: Callable) -> None:
        """Register a task executor for a specific task type."""
        self.task_executors[task_type] = executor
        logger.info(f"Registered task executor for type: {task_type}")
    
    def register_module_connector(self, module_name: str, connector: Any) -> None:
        """Register a module connector for cross-module communication."""
        self.module_connectors[module_name] = connector
        
        # Initialize resource tracking for the module
        self.module_resources[module_name] = {
            "available": True,
            "current_load": 0,
            "max_load": 5,
            "last_heartbeat": datetime.utcnow(),
            "performance_metrics": {
                "avg_response_time": 0.0,
                "success_rate": 1.0,
                "error_rate": 0.0
            }
        }
        
        # Create resource lock
        self.resource_locks[module_name] = asyncio.Lock()
        
        logger.info(f"Registered module connector: {module_name}")
    
    async def submit_task(self, task: WorkflowTask, priority: WorkflowPriority = WorkflowPriority.NORMAL) -> bool:
        """Submit a task for execution."""
        if task.task_id in self.running_tasks:
            logger.warning(f"Task {task.task_id} is already running")
            return False
        
        if task.task_id in self.completed_tasks:
            logger.warning(f"Task {task.task_id} is already completed")
            return False
        
        # Calculate priority score
        priority_score = self._calculate_priority_score(task, priority)
        
        # Add to queue
        self.queued_tasks.append((task, priority_score))
        
        # Sort queue by priority score (highest first)
        self.queued_tasks.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"Submitted task {task.task_id} with priority score {priority_score}")
        return True
    
    async def cancel_task(self, task_id: UUID) -> bool:
        """Cancel a queued or running task."""
        # Remove from queue
        self.queued_tasks = [(task, score) for task, score in self.queued_tasks if task.task_id != task_id]
        
        # Mark as cancelled if running
        if task_id in self.running_tasks:
            # In a real implementation, you would signal the running task to stop
            self.running_tasks.remove(task_id)
            logger.info(f"Cancelled running task: {task_id}")
            return True
        
        logger.info(f"Cancelled queued task: {task_id}")
        return True
    
    def get_task_status(self, task_id: UUID) -> Optional[TaskStatus]:
        """Get the status of a task."""
        if task_id in self.running_tasks:
            return TaskStatus.RUNNING
        
        if task_id in self.completed_tasks:
            return TaskStatus.COMPLETED
        
        if task_id in self.failed_tasks:
            return TaskStatus.FAILED
        
        # Check if in queue
        for task, _ in self.queued_tasks:
            if task.task_id == task_id:
                return TaskStatus.PENDING
        
        return None
    
    def get_running_tasks(self) -> List[WorkflowTask]:
        """Get all currently running tasks."""
        # In a real implementation, you would maintain a mapping of task_id to task
        # For now, return empty list as we only track IDs
        return []
    
    def get_queued_tasks(self) -> List[WorkflowTask]:
        """Get all queued tasks."""
        return [task for task, _ in self.queued_tasks]
    
    def get_completed_tasks(self) -> List[WorkflowTask]:
        """Get all completed tasks."""
        return list(self.completed_tasks.values())
    
    def get_failed_tasks(self) -> List[WorkflowTask]:
        """Get all failed tasks."""
        return list(self.failed_tasks.values())
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get the current status of the task orchestrator."""
        return {
            "is_running": self.is_running,
            "running_tasks": len(self.running_tasks),
            "queued_tasks": len(self.queued_tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "execution_metrics": self.execution_metrics.copy(),
            "module_resources": {
                module: {
                    "available": info["available"],
                    "current_load": info["current_load"],
                    "max_load": info["max_load"]
                }
                for module, info in self.module_resources.items()
            }
        }
    
    async def _orchestration_loop(self) -> None:
        """Main orchestration loop for managing task execution."""
        logger.info("Starting task orchestration loop")
        
        while self.is_running:
            try:
                # Check if we can start new tasks
                if len(self.running_tasks) < self.max_concurrent_tasks and self.queued_tasks:
                    await self._start_next_task()
                
                # Monitor running tasks
                await self._monitor_running_tasks()
                
                # Update performance metrics
                await self._update_performance_metrics()
                
                # Wait before next iteration
                await asyncio.sleep(0.1)  # 100ms intervals for responsive orchestration
                
            except asyncio.CancelledError:
                logger.info("Task orchestration loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in task orchestration loop: {e}")
                await asyncio.sleep(1)  # Wait before retrying
        
        logger.info("Task orchestration loop stopped")
    
    async def _start_next_task(self) -> None:
        """Start the next available task from the queue."""
        if not self.queued_tasks:
            return
        
        # Get next task
        task, priority_score = self.queued_tasks.pop(0)
        
        # Check if task can be executed
        if not await self._can_execute_task(task):
            # Put back in queue with lower priority
            self.queued_tasks.append((task, priority_score * 0.9))
            return
        
        # Start task execution
        asyncio.create_task(self._execute_task(task))
        self.running_tasks.add(task.task_id)
        
        logger.info(f"Started task execution: {task.task_id}")
    
    async def _can_execute_task(self, task: WorkflowTask) -> bool:
        """Check if a task can be executed."""
        # Check module availability
        if task.target_module not in self.module_resources:
            logger.warning(f"Module {task.target_module} not registered")
            return False
        
        module_info = self.module_resources[task.target_module]
        
        # Check if module is available
        if not module_info["available"]:
            return False
        
        # Check resource capacity
        if module_info["current_load"] >= module_info["max_load"]:
            return False
        
        # Check dependencies
        if not await self._check_task_dependencies(task):
            return False
        
        return True
    
    async def _check_task_dependencies(self, task: WorkflowTask) -> bool:
        """Check if task dependencies are satisfied."""
        for dep in task.dependencies:
            if dep.source_task_id not in self.completed_tasks:
                return False
        return True
    
    async def _execute_task(self, task: WorkflowTask) -> None:
        """Execute a single task."""
        start_time = datetime.utcnow()
        
        try:
            # Update task status
            task.status = TaskStatus.RUNNING
            task.started_at = start_time
            
            # Acquire module resource
            async with self.resource_locks[task.target_module]:
                # Update module load
                self.module_resources[task.target_module]["current_load"] += 1
                
                # Execute task
                if task.task_type == "module_operation":
                    result = await self._execute_module_operation(task)
                else:
                    result = await self._execute_generic_task(task)
                
                # Update task status
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                task.result = result
                
                # Move to completed tasks
                self.completed_tasks[task.task_id] = task
                
                logger.info(f"Task completed successfully: {task.task_id}")
                
        except Exception as e:
            # Handle task failure
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            
            # Move to failed tasks
            self.failed_tasks[task.task_id] = task
            
            logger.error(f"Task failed: {task.task_id}: {e}")
            
        finally:
            # Release module resource
            if task.target_module in self.module_resources:
                self.module_resources[task.target_module]["current_load"] -= 1
            
            # Remove from running tasks
            self.running_tasks.discard(task.task_id)
            
            # Update execution metrics
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_execution_metrics(execution_time)
    
    async def _execute_module_operation(self, task: WorkflowTask) -> Dict[str, Any]:
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
    
    async def _execute_generic_task(self, task: WorkflowTask) -> Dict[str, Any]:
        """Execute a generic task."""
        if task.task_type in self.task_executors:
            executor = self.task_executors[task.task_type]
            return await executor(task)
        else:
            # Default generic task execution
            await asyncio.sleep(0.1)  # Simulate task execution
            return {
                "task_type": task.task_type,
                "result": f"Generic execution result for {task.task_name}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _monitor_running_tasks(self) -> None:
        """Monitor currently running tasks."""
        # This is a placeholder for task monitoring logic
        # In a real implementation, you would:
        # - Check for stuck tasks
        # - Monitor resource usage
        # - Handle timeouts
        # - Update progress indicators
        pass
    
    async def _update_performance_metrics(self) -> None:
        """Update performance metrics."""
        # This is a placeholder for metrics update logic
        # In a real implementation, you would:
        # - Calculate current throughput
        # - Update resource utilization
        # - Track performance trends
        pass
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop for managing completed/failed tasks."""
        logger.info("Starting task cleanup loop")
        
        while self.is_running:
            try:
                # Clean up old completed tasks
                await self._cleanup_old_tasks()
                
                # Clean up old failed tasks
                await self._cleanup_old_failed_tasks()
                
                # Wait before next cleanup
                await asyncio.sleep(60)  # Cleanup every minute
                
            except asyncio.CancelledError:
                logger.info("Task cleanup loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in task cleanup loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying
        
        logger.info("Task cleanup loop stopped")
    
    async def _cleanup_old_tasks(self) -> None:
        """Clean up old completed tasks."""
        # This is a placeholder for cleanup logic
        # In a real implementation, you would:
        # - Remove tasks older than retention period
        # - Archive important results
        # - Update metrics
        pass
    
    async def _cleanup_old_failed_tasks(self) -> None:
        """Clean up old failed tasks."""
        # This is a placeholder for cleanup logic
        # In a real implementation, you would:
        # - Remove failed tasks older than retention period
        # - Generate failure reports
        # - Update error metrics
        pass
    
    def _calculate_priority_score(self, task: WorkflowTask, priority: WorkflowPriority) -> float:
        """Calculate a priority score for task scheduling."""
        base_score = {
            WorkflowPriority.LOW: 1.0,
            WorkflowPriority.NORMAL: 2.0,
            WorkflowPriority.HIGH: 3.0,
            WorkflowPriority.CRITICAL: 4.0
        }.get(priority, 2.0)
        
        # Add time-based factor (older tasks get higher priority)
        age_factor = 1.0  # In a real implementation, calculate based on task age
        
        # Add dependency factor (tasks with more dependencies get higher priority)
        dependency_factor = 1.0 + (len(task.dependencies) * 0.1)
        
        return base_score * age_factor * dependency_factor
    
    def _update_execution_metrics(self, execution_time: float) -> None:
        """Update execution metrics with new task completion."""
        self.execution_metrics["total_tasks_executed"] += 1
        self.execution_metrics["total_execution_time"] += execution_time
        self.execution_metrics["average_execution_time"] = (
            self.execution_metrics["total_execution_time"] / 
            self.execution_metrics["total_tasks_executed"]
        )
        
        # Update tasks per second (rolling average)
        # This is a simplified calculation
        self.execution_metrics["tasks_per_second"] = 1.0 / execution_time if execution_time > 0 else 0.0
