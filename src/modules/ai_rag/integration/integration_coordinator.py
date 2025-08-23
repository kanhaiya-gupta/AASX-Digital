"""
Integration Coordinator for AI RAG

This module coordinates all integration components:
- Workflow orchestration
- Integration monitoring
- Error handling
- Performance tracking
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field

from ..events.event_types import (
    BaseEvent, EventPriority, EventStatus, EventCategory,
    IntegrationEvent, PerformanceEvent, SystemHealthEvent
)
from ..events.event_bus import EventBus

from .module_integrations import (
    ModuleIntegrationManager, IntegrationConfig, IntegrationType,
    AASXIntegration, TwinRegistryIntegration, KGNeo4jIntegration
)
from .external_api_client import (
    ExternalAPIManager, APIServiceType, APIEndpointConfig
)
from .webhook_manager import (
    WebhookManager, WebhookConfig, WebhookPayload
)


class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class WorkflowStepStatus(str, Enum):
    """Individual workflow step status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowPriority(str, Enum):
    """Workflow priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class WorkflowStep:
    """Individual workflow step definition"""
    step_id: str
    name: str
    description: str
    step_type: str  # 'module_integration', 'external_api', 'webhook'
    config: Dict[str, Any]
    dependencies: List[str] = None  # List of step IDs this step depends on
    timeout_seconds: int = 300
    retry_count: int = 0
    max_retries: int = 3
    status: WorkflowStepStatus = WorkflowStepStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Any] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class WorkflowDefinition(BaseModel):
    """Complete workflow definition"""
    workflow_id: str
    name: str
    description: str
    version: str = "1.0.0"
    priority: WorkflowPriority = WorkflowPriority.NORMAL
    steps: List[WorkflowStep]
    timeout_seconds: int = 1800  # 30 minutes default
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        arbitrary_types_allowed = True


class WorkflowExecution(BaseModel):
    """Workflow execution instance"""
    execution_id: str
    workflow_definition: WorkflowDefinition
    status: WorkflowStatus = WorkflowStatus.PENDING
    priority: WorkflowPriority
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    current_step: Optional[str] = None
    step_results: Dict[str, Any] = Field(default_factory=dict)
    step_errors: Dict[str, str] = Field(default_factory=dict)
    execution_metrics: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True


class IntegrationMetrics(BaseModel):
    """Integration performance metrics"""
    total_workflows: int = 0
    successful_workflows: int = 0
    failed_workflows: int = 0
    average_execution_time_ms: float = 0.0
    total_execution_time_ms: float = 0.0
    active_workflows: int = 0
    last_execution_time: Optional[datetime] = None
    
    # Module integration metrics
    module_integration_calls: int = 0
    external_api_calls: int = 0
    webhook_deliveries: int = 0
    
    # Error tracking
    total_errors: int = 0
    error_rate: float = 0.0
    
    # Performance tracking
    response_time_95th_percentile: float = 0.0
    response_time_99th_percentile: float = 0.0


class IntegrationCoordinator:
    """Coordinates all integration components and workflows"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        
        # Integration components
        self.module_integration_manager: Optional[ModuleIntegrationManager] = None
        self.external_api_manager: Optional[ExternalAPIManager] = None
        self.webhook_manager: Optional[WebhookManager] = None
        
        # Workflow management
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.execution_queue: asyncio.Queue = asyncio.Queue()
        
        # Metrics and monitoring
        self.metrics = IntegrationMetrics()
        self.health_status = {}
        self.running = False
        
        # Background tasks
        self.execution_task: Optional[asyncio.Task] = None
        self.monitoring_task: Optional[asyncio.Task] = None
    
    def register_module_integrations(self, configs: List[IntegrationConfig]):
        """Register module integrations"""
        self.module_integration_manager = ModuleIntegrationManager(configs, self.event_bus)
        self.logger.info("Module integrations registered")
    
    def register_external_apis(self, api_configs: Dict[APIServiceType, APIEndpointConfig]):
        """Register external API clients"""
        self.external_api_manager = ExternalAPIManager(self.event_bus)
        for service_type, config in api_configs.items():
            self.external_api_manager.register_client(service_type, config)
        self.logger.info("External API clients registered")
    
    def register_webhooks(self, webhook_configs: List[WebhookConfig]):
        """Register webhook endpoints"""
        self.webhook_manager = WebhookManager(self.event_bus)
        for config in webhook_configs:
            self.webhook_manager.register_webhook(config)
        self.logger.info("Webhook endpoints registered")
    
    def register_workflow(self, workflow: WorkflowDefinition):
        """Register a new workflow definition"""
        self.workflow_definitions[workflow.workflow_id] = workflow
        self.logger.info(f"Workflow registered: {workflow.name} ({workflow.workflow_id})")
    
    async def start(self):
        """Start the integration coordinator"""
        if self.running:
            return
        
        self.running = True
        
        # Start webhook manager if available
        if self.webhook_manager:
            await self.webhook_manager.start()
        
        # Start background tasks
        self.execution_task = asyncio.create_task(self._run_workflow_executor())
        self.monitoring_task = asyncio.create_task(self._run_monitoring_loop())
        
        self.logger.info("Integration coordinator started")
    
    async def stop(self):
        """Stop the integration coordinator"""
        if not self.running:
            return
        
        self.running = False
        
        # Cancel background tasks
        if self.execution_task:
            self.execution_task.cancel()
            try:
                await self.execution_task
            except asyncio.CancelledError:
                pass
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        # Stop webhook manager if available
        if self.webhook_manager:
            await self.webhook_manager.stop()
        
        self.logger.info("Integration coordinator stopped")
    
    async def execute_workflow(
        self, 
        workflow_id: str, 
        priority: Optional[WorkflowPriority] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Execute a workflow"""
        if workflow_id not in self.workflow_definitions:
            raise ValueError(f"Workflow '{workflow_id}' not found")
        
        workflow_def = self.workflow_definitions[workflow_id]
        execution_id = f"exec_{workflow_id}_{datetime.now().timestamp()}"
        
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_definition=workflow_def,
            priority=priority or workflow_def.priority,
            started_at=datetime.now()
        )
        
        # Add to execution queue
        await self.execution_queue.put((execution.priority, execution))
        self.active_executions[execution_id] = execution
        
        # Update metrics
        self.metrics.total_workflows += 1
        self.metrics.active_workflows += 1
        
        # Publish integration event
        event = IntegrationEvent(
            event_id=f"workflow_started_{execution_id}",
            workflow_id=workflow_id,
            execution_id=execution_id,
            workflow_name=workflow_def.name,
            priority=EventPriority.NORMAL,
            category=EventCategory.INTEGRATION
        )
        await self.event_bus.publish(event)
        
        self.logger.info(f"Workflow execution queued: {workflow_def.name} ({execution_id})")
        return execution_id
    
    async def _run_workflow_executor(self):
        """Main workflow execution loop"""
        while self.running:
            try:
                # Get next workflow from queue
                priority, execution = await self.execution_queue.get()
                
                # Execute workflow
                await self._execute_workflow(execution)
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in workflow executor: {e}")
                await asyncio.sleep(1)
    
    async def _execute_workflow(self, execution: WorkflowExecution):
        """Execute a single workflow"""
        try:
            execution.status = WorkflowStatus.RUNNING
            workflow_def = execution.workflow_definition
            start_time = time.time()
            
            self.logger.info(f"Starting workflow execution: {workflow_def.name} ({execution.execution_id})")
            
            # Execute steps in dependency order
            completed_steps = set()
            step_results = {}
            
            while len(completed_steps) < len(workflow_def.steps):
                # Find steps that can be executed (dependencies satisfied)
                for step in workflow_def.steps:
                    if step.step_id in completed_steps:
                        continue
                    
                    # Check if dependencies are satisfied
                    if all(dep in completed_steps for dep in step.dependencies):
                        # Execute step
                        step_result = await self._execute_workflow_step(execution, step)
                        step_results[step.step_id] = step_result
                        completed_steps.add(step.step_id)
                        
                        # Update execution state
                        execution.current_step = step.step_id
                        execution.step_results[step.step_id] = step_result
                        
                        if step.status == WorkflowStepStatus.FAILED:
                            execution.step_errors[step.step_id] = step.error_message or "Unknown error"
                            execution.status = WorkflowStatus.FAILED
                            break
                
                # Check for timeout
                if time.time() - start_time > workflow_def.timeout_seconds:
                    execution.status = WorkflowStatus.TIMEOUT
                    break
                
                # Small delay between steps
                await asyncio.sleep(0.1)
            
            # Update execution completion
            execution.completed_at = datetime.now()
            execution_time = (execution.completed_at - execution.started_at).total_seconds() * 1000
            
            if execution.status == WorkflowStatus.RUNNING:
                execution.status = WorkflowStatus.COMPLETED
                execution.execution_metrics["total_time_ms"] = execution_time
                self.metrics.successful_workflows += 1
                
                # Publish completion event
                completion_event = IntegrationEvent(
                    event_id=f"workflow_completed_{execution.execution_id}",
                    workflow_id=workflow_def.workflow_id,
                    execution_id=execution.execution_id,
                    workflow_name=workflow_def.name,
                    execution_status="completed",
                    execution_time_ms=execution_time,
                    priority=EventPriority.NORMAL,
                    category=EventCategory.INTEGRATION
                )
                await self.event_bus.publish(completion_event)
                
                self.logger.info(f"Workflow completed: {workflow_def.name} ({execution.execution_id})")
            else:
                self.metrics.failed_workflows += 1
                
                # Publish failure event
                failure_event = IntegrationEvent(
                    event_id=f"workflow_failed_{execution.execution_id}",
                    workflow_id=workflow_def.workflow_id,
                    execution_id=execution.execution_id,
                    workflow_name=workflow_def.name,
                    execution_status=execution.status.value,
                    error_details=execution.step_errors,
                    priority=EventPriority.NORMAL,
                    category=EventCategory.ERROR
                )
                await self.event_bus.publish(failure_event)
                
                self.logger.error(f"Workflow failed: {workflow_def.name} ({execution.execution_id})")
            
            # Update metrics
            self.metrics.total_execution_time_ms += execution_time
            self.metrics.average_execution_time_ms = (
                self.metrics.total_execution_time_ms / self.metrics.total_workflows
            )
            self.metrics.last_execution_time = datetime.now()
            self.metrics.active_workflows -= 1
            
        except Exception as e:
            self.logger.error(f"Error executing workflow {execution.execution_id}: {e}")
            execution.status = WorkflowStatus.FAILED
            execution.completed_at = datetime.now()
            execution.step_errors["system_error"] = str(e)
            self.metrics.failed_workflows += 1
            self.metrics.active_workflows -= 1
    
    async def _execute_workflow_step(
        self, 
        execution: WorkflowExecution, 
        step: WorkflowStep
    ) -> Any:
        """Execute a single workflow step"""
        try:
            step.status = WorkflowStepStatus.IN_PROGRESS
            step.start_time = datetime.now()
            
            self.logger.debug(f"Executing step: {step.name} ({step.step_id})")
            
            # Execute based on step type
            if step.step_type == "module_integration":
                result = await self._execute_module_integration_step(step)
            elif step.step_type == "external_api":
                result = await self._execute_external_api_step(step)
            elif step.step_type == "webhook":
                result = await self._execute_webhook_step(step)
            else:
                raise ValueError(f"Unknown step type: {step.step_type}")
            
            step.status = WorkflowStepStatus.COMPLETED
            step.end_time = datetime.now()
            step.result = result
            
            return result
            
        except Exception as e:
            step.status = WorkflowStepStatus.FAILED
            step.end_time = datetime.now()
            step.error_message = str(e)
            step.retry_count += 1
            
            # Retry logic
            if step.retry_count < step.max_retries:
                self.logger.warning(f"Step {step.name} failed, retrying ({step.retry_count}/{step.max_retries})")
                await asyncio.sleep(step.retry_count * 2)  # Exponential backoff
                return await self._execute_workflow_step(execution, step)
            else:
                self.logger.error(f"Step {step.name} failed after {step.max_retries} retries: {e}")
                raise
    
    async def _execute_module_integration_step(self, step: WorkflowStep) -> Any:
        """Execute a module integration step"""
        if not self.module_integration_manager:
            raise RuntimeError("Module integration manager not available")
        
        step_config = step.config
        integration_type = IntegrationType(step_config["integration_type"])
        operation = step_config["operation"]
        
        integration = self.module_integration_manager.get_integration(integration_type)
        if not integration:
            raise ValueError(f"Integration {integration_type.value} not found")
        
        # Execute operation based on integration type and operation
        if integration_type == IntegrationType.AASX and operation == "process_file":
            return await integration.process_aasx_file(
                step_config["file_path"], 
                step_config.get("file_metadata", {})
            )
        elif integration_type == IntegrationType.TWIN_REGISTRY and operation == "sync_health_scores":
            return await integration.sync_twin_health_scores(step_config["twin_ids"])
        elif integration_type == IntegrationType.KG_NEO4J and operation == "enhance_graph":
            return await integration.enhance_knowledge_graph(
                step_config["graph_id"], 
                step_config.get("enhancement_config", {})
            )
        else:
            raise ValueError(f"Unknown operation {operation} for integration {integration_type.value}")
    
    async def _execute_external_api_step(self, step: WorkflowStep) -> Any:
        """Execute an external API step"""
        if not self.external_api_manager:
            raise RuntimeError("External API manager not available")
        
        step_config = step.config
        service_type = APIServiceType(step_config["service_type"])
        operation = step_config["operation"]
        
        client = self.external_api_manager.get_client(service_type)
        if not client:
            raise ValueError(f"Client for {service_type.value} not found")
        
        # Execute operation based on service type and operation
        if service_type == APIServiceType.VECTOR_DATABASE and operation == "upsert_vectors":
            return await client.upsert_vectors(
                step_config["collection_name"], 
                step_config["vectors"]
            )
        elif service_type == APIServiceType.LLM_SERVICE and operation == "generate_text":
            return await client.generate_text(
                step_config["prompt"],
                step_config.get("max_tokens", 1000),
                step_config.get("temperature", 0.7)
            )
        else:
            raise ValueError(f"Unknown operation {operation} for service {service_type.value}")
    
    async def _execute_webhook_step(self, step: WorkflowStep) -> Any:
        """Execute a webhook step"""
        if not self.webhook_manager:
            raise RuntimeError("Webhook manager not available")
        
        step_config = step.config
        webhook_name = step_config["webhook_name"]
        
        payload = WebhookPayload(
            event_type=step_config["event_type"],
            event_id=step_config["event_id"],
            data=step_config.get("data", {}),
            metadata=step_config.get("metadata", {})
        )
        
        return await self.webhook_manager.send_webhook(
            webhook_name, 
            payload,
            step_config.get("priority"),
            step_config.get("scheduled_for")
        )
    
    async def _run_monitoring_loop(self):
        """Run monitoring and health check loop"""
        while self.running:
            try:
                # Update health status
                await self._update_health_status()
                
                # Update metrics
                await self._update_metrics()
                
                # Publish system health event
                health_event = SystemHealthEvent(
                    event_id=f"system_health_{datetime.now().timestamp()}",
                    health_status=self.health_status,
                    metrics=self.metrics.dict(),
                    priority=EventPriority.LOW,
                    category=EventCategory.SYSTEM_HEALTH
                )
                await self.event_bus.publish(health_event)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(30)
    
    async def _update_health_status(self):
        """Update health status of all components"""
        self.health_status = {}
        
        # Module integrations health
        if self.module_integration_manager:
            self.health_status["module_integrations"] = await self.module_integration_manager.health_check_all()
        
        # External APIs health
        if self.external_api_manager:
            self.health_status["external_apis"] = await self.external_api_manager.health_check_all()
        
        # Webhooks health
        if self.webhook_manager:
            self.health_status["webhooks"] = await self.webhook_manager.health_check()
        
        # Overall coordinator health
        self.health_status["coordinator"] = {
            "running": self.running,
            "active_workflows": self.metrics.active_workflows,
            "queue_size": self.execution_queue.qsize()
        }
    
    async def _update_metrics(self):
        """Update integration metrics"""
        # Calculate error rate
        if self.metrics.total_workflows > 0:
            self.metrics.error_rate = self.metrics.failed_workflows / self.metrics.total_workflows
        
        # Update API call counts (simplified)
        if self.module_integration_manager:
            self.metrics.module_integration_calls = sum(
                integration.metrics.total_requests 
                for integration in self.module_integration_manager.integrations.values()
            )
        
        if self.webhook_manager:
            webhook_stats = await self.webhook_manager.get_all_webhook_status()
            self.metrics.webhook_deliveries = sum(
                stats["stats"]["total_sent"] 
                for stats in webhook_stats.values()
            )
    
    async def get_workflow_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get status of a specific workflow execution"""
        return self.active_executions.get(execution_id)
    
    async def get_all_workflow_status(self) -> Dict[str, WorkflowExecution]:
        """Get status of all workflow executions"""
        return self.active_executions.copy()
    
    async def get_integration_metrics(self) -> IntegrationMetrics:
        """Get integration performance metrics"""
        return self.metrics
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status"""
        return self.health_status
    
    async def cancel_workflow(self, execution_id: str) -> bool:
        """Cancel a running workflow"""
        if execution_id not in self.active_executions:
            return False
        
        execution = self.active_executions[execution_id]
        if execution.status == WorkflowStatus.RUNNING:
            execution.status = WorkflowStatus.CANCELLED
            execution.completed_at = datetime.now()
            self.metrics.active_workflows -= 1
            
            # Publish cancellation event
            cancellation_event = IntegrationEvent(
                event_id=f"workflow_cancelled_{execution_id}",
                workflow_id=execution.workflow_definition.workflow_id,
                execution_id=execution_id,
                workflow_name=execution.workflow_definition.name,
                execution_status="cancelled",
                priority=EventPriority.NORMAL,
                category=EventCategory.INTEGRATION
            )
            await self.event_bus.publish(cancellation_event)
            
            self.logger.info(f"Workflow cancelled: {execution_id}")
            return True
        
        return False
