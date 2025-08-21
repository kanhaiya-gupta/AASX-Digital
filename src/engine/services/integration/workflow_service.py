"""
Cross-Domain Workflow Service

Coordinates workflows that span multiple business domains, authentication, and data governance services.
Provides comprehensive workflow orchestration, state management, and cross-service coordination.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
from enum import Enum

from ...repositories.business_domain_repository import BusinessDomainRepository
from ...repositories.auth_repository import AuthRepository
from ...repositories.data_governance_repository import DataGovernanceRepository
from ...models.business_domain import Organization, Project, File
from ...models.auth import User
from ...models.data_governance import DataLineage, DataQualityMetrics, ChangeRequest, DataVersion, GovernancePolicy
from ..base.base_service import BaseService

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class WorkflowStepStatus(Enum):
    """Workflow step status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """Represents a step in a cross-domain workflow."""
    step_id: str
    step_name: str
    step_type: str  # business_domain, auth, data_governance
    service: str
    operation: str
    parameters: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)  # IDs of steps this depends on
    status: WorkflowStepStatus = WorkflowStepStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class CrossDomainWorkflow:
    """Represents a workflow that spans multiple domains."""
    workflow_id: str
    workflow_name: str
    description: str
    created_by: str
    created_at: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    steps: List[WorkflowStep] = field(default_factory=list)
    current_step: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class WorkflowExecutionResult:
    """Represents the result of workflow execution."""
    workflow_id: str
    execution_id: str
    status: WorkflowStatus
    steps_completed: int
    steps_failed: int
    steps_skipped: int
    total_steps: int
    execution_time: float
    results: Dict[str, Any]
    errors: List[str]
    recommendations: List[str]


class WorkflowService(BaseService):
    """
    Cross-domain workflow service that coordinates workflows across all services.
    
    Provides comprehensive workflow orchestration, state management, and cross-service
    coordination for business domain, authentication, and data governance operations.
    """
    
    def __init__(self, 
                 business_repo: BusinessDomainRepository,
                 auth_repo: AuthRepository,
                 governance_repo: DataGovernanceRepository):
        super().__init__("WorkflowService")
        
        # Repository dependencies for cross-domain operations
        self.business_repo = business_repo
        self.auth_repo = auth_repo
        self.governance_repo = governance_repo
        
        # In-memory workflow cache for performance
        self._workflow_cache = {}
        self._execution_cache = {}
        self._step_cache = {}
        
        # Workflow configuration
        self.max_concurrent_workflows = 10
        self.default_timeout_minutes = 30
        self.retry_delay_seconds = 60
        
        # Performance metrics
        self.workflows_created = 0
        self.workflows_executed = 0
        self.workflows_completed = 0
        self.workflows_failed = 0
        self.steps_executed = 0
        
        # Initialize service resources
        asyncio.create_task(self._initialize_service_resources())
    
    async def _initialize_service_resources(self) -> None:
        """Initialize service resources and load initial data."""
        try:
            logger.info("Initializing Workflow Service resources...")
            
            # Load existing workflows into cache
            await self._load_workflow_cache()
            
            # Initialize workflow monitoring
            await self._initialize_workflow_monitoring()
            
            logger.info("Workflow Service resources initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Workflow Service resources: {e}")
            self.handle_error("_initialize_service_resources", e)
    
    async def get_service_info(self) -> Dict[str, Any]:
        """Get service information and status."""
        return {
            'service_name': self.service_name,
            'service_type': 'integration.workflow',
            'status': 'active' if self.is_active else 'inactive',
            'uptime': str(datetime.now() - self.start_time),
            'cache_size': len(self._workflow_cache),
            'workflows_created': self.workflows_created,
            'workflows_executed': self.workflows_executed,
            'workflows_completed': self.workflows_completed,
            'workflows_failed': self.workflows_failed,
            'steps_executed': self.steps_executed
        }
    
    async def _cleanup_service_resources(self) -> None:
        """Cleanup service-specific resources."""
        try:
            # Clear caches
            self._workflow_cache.clear()
            self._execution_cache.clear()
            self._step_cache.clear()
            
            logger.info(f"{self.service_name}: Cleaned up service resources")
            
        except Exception as e:
            logger.error(f"{self.service_name}: Error during cleanup: {e}")
            self.handle_error("cleanup", e)
    
    async def create_workflow(self, workflow_data: Dict[str, Any]) -> CrossDomainWorkflow:
        """Create a new cross-domain workflow."""
        try:
            self._log_operation("create_workflow", f"workflow_name: {workflow_data.get('workflow_name')}")
            
            # Validate required fields
            required_fields = ['workflow_name', 'description', 'created_by', 'steps']
            for field in required_fields:
                if not workflow_data.get(field):
                    raise ValueError(f"Missing required field: {field}")
            
            # Generate workflow ID
            workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(workflow_data)}"
            
            # Create workflow steps
            steps = []
            for step_data in workflow_data['steps']:
                step = WorkflowStep(
                    step_id=f"step_{len(steps)}_{workflow_id}",
                    step_name=step_data['step_name'],
                    step_type=step_data['step_type'],
                    service=step_data['service'],
                    operation=step_data['operation'],
                    parameters=step_data.get('parameters', {}),
                    dependencies=step_data.get('dependencies', []),
                    max_retries=step_data.get('max_retries', 3)
                )
                steps.append(step)
            
            # Create workflow
            workflow = CrossDomainWorkflow(
                workflow_id=workflow_id,
                workflow_name=workflow_data['workflow_name'],
                description=workflow_data['description'],
                created_by=workflow_data['created_by'],
                created_at=datetime.now().isoformat(),
                steps=steps,
                max_retries=workflow_data.get('max_retries', 3)
            )
            
            # Store workflow
            await self._store_workflow(workflow)
            
            # Update cache
            self._update_workflow_cache(workflow)
            
            # Update metrics
            self.workflows_created += 1
            
            logger.info(f"Workflow created successfully: {workflow_id}")
            return workflow
            
        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            self.handle_error("create_workflow", e)
            raise
    
    async def execute_workflow(self, workflow_id: str) -> WorkflowExecutionResult:
        """Execute a cross-domain workflow."""
        try:
            self._log_operation("execute_workflow", f"workflow_id: {workflow_id}")
            
            # Get workflow
            workflow = await self.get_workflow(workflow_id)
            if not workflow:
                raise ValueError(f"Workflow not found: {workflow_id}")
            
            # Check if workflow can be executed
            if workflow.status not in [WorkflowStatus.PENDING, WorkflowStatus.FAILED]:
                raise ValueError(f"Workflow cannot be executed in status: {workflow.status}")
            
            # Generate execution ID
            execution_id = f"exec_{workflow_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Update workflow status
            workflow.status = WorkflowStatus.RUNNING
            workflow.started_at = datetime.now().isoformat()
            workflow.current_step = None
            
            # Execute workflow steps
            execution_result = await self._execute_workflow_steps(workflow, execution_id)
            
            # Update workflow status based on execution result
            if execution_result.status == WorkflowStatus.COMPLETED:
                workflow.status = WorkflowStatus.COMPLETED
                workflow.completed_at = datetime.now().isoformat()
                self.workflows_completed += 1
            else:
                workflow.status = WorkflowStatus.FAILED
                workflow.error = execution_result.errors[0] if execution_result.errors else "Unknown error"
                self.workflows_failed += 1
            
            # Update cache
            self._update_workflow_cache(workflow)
            
            # Update metrics
            self.workflows_executed += 1
            
            return execution_result
            
        except Exception as e:
            logger.error(f"Failed to execute workflow: {e}")
            self.handle_error("execute_workflow", e)
            raise
    
    async def get_workflow(self, workflow_id: str) -> Optional[CrossDomainWorkflow]:
        """Get workflow by ID."""
        try:
            # Check cache first
            if workflow_id in self._workflow_cache:
                return self._workflow_cache[workflow_id]
            
            # Get from repository
            workflow = await self._get_workflow_from_storage(workflow_id)
            
            if workflow:
                # Update cache
                self._update_workflow_cache(workflow)
            
            return workflow
            
        except Exception as e:
            logger.error(f"Failed to get workflow: {e}")
            self.handle_error("get_workflow", e)
            return None
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get current status of a workflow."""
        try:
            workflow = await self.get_workflow(workflow_id)
            if not workflow:
                return {'error': 'Workflow not found'}
            
            # Calculate progress
            total_steps = len(workflow.steps)
            completed_steps = sum(1 for s in workflow.steps if s.status == WorkflowStepStatus.COMPLETED)
            failed_steps = sum(1 for s in workflow.steps if s.status == WorkflowStepStatus.FAILED)
            running_steps = sum(1 for s in workflow.steps if s.status == WorkflowStepStatus.RUNNING)
            
            progress = (completed_steps / total_steps * 100) if total_steps > 0 else 0
            
            return {
                'workflow_id': workflow_id,
                'status': workflow.status.value,
                'progress': progress,
                'total_steps': total_steps,
                'completed_steps': completed_steps,
                'failed_steps': failed_steps,
                'running_steps': running_steps,
                'current_step': workflow.current_step,
                'started_at': workflow.started_at,
                'completed_at': workflow.completed_at,
                'error': workflow.error
            }
            
        except Exception as e:
            logger.error(f"Failed to get workflow status: {e}")
            self.handle_error("get_workflow_status", e)
            return {'error': str(e)}
    
    async def pause_workflow(self, workflow_id: str) -> bool:
        """Pause a running workflow."""
        try:
            workflow = await self.get_workflow(workflow_id)
            if not workflow:
                return False
            
            if workflow.status == WorkflowStatus.RUNNING:
                workflow.status = WorkflowStatus.PAUSED
                self._update_workflow_cache(workflow)
                logger.info(f"Workflow paused: {workflow_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to pause workflow: {e}")
            self.handle_error("pause_workflow", e)
            return False
    
    async def resume_workflow(self, workflow_id: str) -> bool:
        """Resume a paused workflow."""
        try:
            workflow = await self.get_workflow(workflow_id)
            if not workflow:
                return False
            
            if workflow.status == WorkflowStatus.PAUSED:
                workflow.status = WorkflowStatus.RUNNING
                self._update_workflow_cache(workflow)
                logger.info(f"Workflow resumed: {workflow_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to resume workflow: {e}")
            self.handle_error("resume_workflow", e)
            return False
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a workflow."""
        try:
            workflow = await self.get_workflow(workflow_id)
            if not workflow:
                return False
            
            if workflow.status in [WorkflowStatus.PENDING, WorkflowStatus.RUNNING, WorkflowStatus.PAUSED]:
                workflow.status = WorkflowStatus.CANCELLED
                self._update_workflow_cache(workflow)
                logger.info(f"Workflow cancelled: {workflow_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to cancel workflow: {e}")
            self.handle_error("cancel_workflow", e)
            return False
    
    # Private helper methods
    
    async def _load_workflow_cache(self):
        """Load existing workflows into cache."""
        try:
            # For now, start with empty cache
            # In a real implementation, this would load from persistent storage
            logger.info("Workflow cache initialized")
            
        except Exception as e:
            logger.warning(f"Failed to load workflow cache: {e}")
    
    async def _initialize_workflow_monitoring(self):
        """Initialize workflow monitoring."""
        try:
            # Set up periodic workflow monitoring
            asyncio.create_task(self._periodic_workflow_monitoring())
            logger.info("Workflow monitoring initialized")
            
        except Exception as e:
            logger.warning(f"Failed to initialize workflow monitoring: {e}")
    
    async def _store_workflow(self, workflow: CrossDomainWorkflow):
        """Store workflow in persistent storage."""
        try:
            # For now, just log the workflow
            # In a real implementation, this would store in database
            logger.debug(f"Storing workflow: {workflow.workflow_id}")
            
        except Exception as e:
            logger.error(f"Failed to store workflow: {e}")
    
    async def _get_workflow_from_storage(self, workflow_id: str) -> Optional[CrossDomainWorkflow]:
        """Get workflow from persistent storage."""
        try:
            # For now, return None
            # In a real implementation, this would query the workflow database
            return None
            
        except Exception as e:
            logger.error(f"Failed to get workflow from storage: {e}")
            return None
    
    async def _execute_workflow_steps(self, workflow: CrossDomainWorkflow, execution_id: str) -> WorkflowExecutionResult:
        """Execute all steps in a workflow."""
        try:
            start_time = datetime.now()
            steps_completed = 0
            steps_failed = 0
            steps_skipped = 0
            results = {}
            errors = []
            
            # Sort steps by dependencies (topological sort)
            sorted_steps = self._sort_steps_by_dependencies(workflow.steps)
            
            # Execute steps in order
            for step in sorted_steps:
                try:
                    # Check if step can be executed
                    if not self._can_execute_step(step, workflow.steps):
                        step.status = WorkflowStepStatus.SKIPPED
                        steps_skipped += 1
                        continue
                    
                    # Execute step
                    step.status = WorkflowStepStatus.RUNNING
                    step.started_at = datetime.now().isoformat()
                    workflow.current_step = step.step_id
                    
                    step_result = await self._execute_workflow_step(step)
                    
                    if step_result['success']:
                        step.status = WorkflowStepStatus.COMPLETED
                        step.result = step_result['result']
                        step.completed_at = datetime.now().isoformat()
                        steps_completed += 1
                        results[step.step_id] = step_result['result']
                    else:
                        step.status = WorkflowStepStatus.FAILED
                        step.error = step_result['error']
                        steps_failed += 1
                        errors.append(f"Step {step.step_name} failed: {step_result['error']}")
                        
                        # Check if we should retry
                        if step.retry_count < step.max_retries:
                            step.retry_count += 1
                            step.status = WorkflowStepStatus.PENDING
                            # In a real implementation, we would schedule retry
                        else:
                            # Max retries exceeded, workflow fails
                            execution_time = (datetime.now() - start_time).total_seconds()
                            return WorkflowExecutionResult(
                                workflow_id=workflow.workflow_id,
                                execution_id=execution_id,
                                status=WorkflowStatus.FAILED,
                                steps_completed=steps_completed,
                                steps_failed=steps_failed,
                                steps_skipped=steps_skipped,
                                total_steps=len(workflow.steps),
                                execution_time=execution_time,
                                results=results,
                                errors=errors,
                                recommendations=['Review failed steps', 'Check system configuration']
                            )
                    
                    self.steps_executed += 1
                    
                except Exception as e:
                    step.status = WorkflowStepStatus.FAILED
                    step.error = str(e)
                    steps_failed += 1
                    errors.append(f"Step {step.step_name} failed with exception: {str(e)}")
            
            # Determine final status
            if steps_failed == 0:
                final_status = WorkflowStatus.COMPLETED
            else:
                final_status = WorkflowStatus.FAILED
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return WorkflowExecutionResult(
                workflow_id=workflow.workflow_id,
                execution_id=execution_id,
                status=final_status,
                steps_completed=steps_completed,
                steps_failed=steps_failed,
                steps_skipped=steps_skipped,
                total_steps=len(workflow.steps),
                execution_time=execution_time,
                results=results,
                errors=errors,
                recommendations=self._generate_workflow_recommendations(workflow, steps_completed, steps_failed)
            )
            
        except Exception as e:
            logger.error(f"Failed to execute workflow steps: {e}")
            execution_time = (datetime.now() - start_time).total_seconds()
            return WorkflowExecutionResult(
                workflow_id=workflow.workflow_id,
                execution_id=execution_id,
                status=WorkflowStatus.FAILED,
                steps_completed=0,
                steps_failed=len(workflow.steps),
                steps_skipped=0,
                total_steps=len(workflow.steps),
                execution_time=execution_time,
                results={},
                errors=[f"Workflow execution failed: {str(e)}"],
                recommendations=['Contact system administrator', 'Review workflow configuration']
            )
    
    async def _execute_workflow_step(self, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a single workflow step."""
        try:
            # Route to appropriate service based on step type
            if step.step_type == "business_domain":
                result = await self._execute_business_domain_step(step)
            elif step.step_type == "auth":
                result = await self._execute_auth_step(step)
            elif step.step_type == "data_governance":
                result = await self._execute_data_governance_step(step)
            else:
                result = {
                    'success': False,
                    'error': f'Unknown step type: {step.step_type}',
                    'result': None
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute workflow step: {e}")
            return {
                'success': False,
                'error': str(e),
                'result': None
            }
    
    async def _execute_business_domain_step(self, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a business domain workflow step."""
        try:
            # For now, return basic success
            # In a real implementation, this would call the appropriate business domain service
            return {
                'success': True,
                'error': None,
                'result': {
                    'message': f'Business domain step {step.step_name} executed successfully',
                    'operation': step.operation,
                    'parameters': step.parameters
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'result': None
            }
    
    async def _execute_auth_step(self, step: WorkflowStep) -> Dict[str, Any]:
        """Execute an authentication workflow step."""
        try:
            # For now, return basic success
            # In a real implementation, this would call the appropriate auth service
            return {
                'success': True,
                'error': None,
                'result': {
                    'message': f'Auth step {step.step_name} executed successfully',
                    'operation': step.operation,
                    'parameters': step.parameters
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'result': None
            }
    
    async def _execute_data_governance_step(self, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a data governance workflow step."""
        try:
            # For now, return basic success
            # In a real implementation, this would call the appropriate data governance service
            return {
                'success': True,
                'error': None,
                'result': {
                    'message': f'Data governance step {step.step_name} executed successfully',
                    'operation': step.operation,
                    'parameters': step.parameters
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'result': None
            }
    
    def _sort_steps_by_dependencies(self, steps: List[WorkflowStep]) -> List[WorkflowStep]:
        """Sort steps by dependencies using topological sort."""
        try:
            # Create dependency graph
            step_map = {step.step_id: step for step in steps}
            in_degree = {step.step_id: 0 for step in steps}
            
            for step in steps:
                for dep_id in step.dependencies:
                    if dep_id in in_degree:
                        in_degree[dep_id] += 1
            
            # Topological sort
            queue = [step_id for step_id, degree in in_degree.items() if degree == 0]
            sorted_steps = []
            
            while queue:
                current_id = queue.pop(0)
                sorted_steps.append(step_map[current_id])
                
                for step in steps:
                    if current_id in step.dependencies:
                        in_degree[step.step_id] -= 1
                        if in_degree[step.step_id] == 0:
                            queue.append(step.step_id)
            
            # Check for cycles
            if len(sorted_steps) != len(steps):
                logger.warning("Circular dependency detected in workflow steps")
                # Return original order if circular dependency
                return steps
            
            return sorted_steps
            
        except Exception as e:
            logger.error(f"Failed to sort steps by dependencies: {e}")
            return steps
    
    def _can_execute_step(self, step: WorkflowStep, all_steps: List[WorkflowStep]) -> bool:
        """Check if a step can be executed based on its dependencies."""
        try:
            if not step.dependencies:
                return True
            
            # Check if all dependencies are completed
            step_map = {s.step_id: s for s in all_steps}
            
            for dep_id in step.dependencies:
                if dep_id not in step_map:
                    return False
                
                dep_step = step_map[dep_id]
                if dep_step.status != WorkflowStepStatus.COMPLETED:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check if step can be executed: {e}")
            return False
    
    def _generate_workflow_recommendations(self, workflow: CrossDomainWorkflow, steps_completed: int, steps_failed: int) -> List[str]:
        """Generate recommendations based on workflow execution results."""
        recommendations = []
        
        if steps_failed > 0:
            recommendations.append(f"Review {steps_failed} failed steps")
            recommendations.append("Check step dependencies and configurations")
        
        if steps_completed == len(workflow.steps):
            recommendations.append("Workflow completed successfully")
        elif steps_completed > 0:
            recommendations.append(f"Workflow partially completed ({steps_completed}/{len(workflow.steps)} steps)")
        
        if workflow.retry_count > 0:
            recommendations.append("Consider reviewing workflow configuration to reduce retries")
        
        return recommendations
    
    def _update_workflow_cache(self, workflow: CrossDomainWorkflow):
        """Update the workflow cache with new data."""
        self._workflow_cache[workflow.workflow_id] = workflow
        
        # Maintain cache size
        if len(self._workflow_cache) > 1000:
            # Remove oldest entries
            oldest_keys = sorted(self._workflow_cache.keys())[:100]
            for key in oldest_keys:
                del self._workflow_cache[key]
    
    async def _periodic_workflow_monitoring(self):
        """Periodic workflow monitoring."""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                # Perform periodic workflow tasks
                # This would typically include cleanup, retry scheduling, etc.
                logger.info("Completed periodic workflow monitoring")
                
            except Exception as e:
                logger.error(f"Periodic workflow monitoring failed: {e}")
                await asyncio.sleep(600)  # Wait 10 minutes before retry
