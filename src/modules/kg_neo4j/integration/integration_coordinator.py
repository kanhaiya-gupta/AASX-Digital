"""
Knowledge Graph Neo4j Integration Coordinator

Main orchestrator for all integration components.
Coordinates workflows between different modules and external systems.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timezone
import uuid

from ..events import KGNeo4jEventManager
from .module_integrations import (
    get_integration,
    get_available_integrations,
    BaseModuleIntegration
)
from .webhook_manager import WebhookManager, WebhookEndpoint
from .external_api_client import ExternalAPIClient, APIConfig

logger = logging.getLogger(__name__)


class IntegrationWorkflow:
    """Represents a multi-step integration workflow."""
    
    def __init__(self, workflow_id: str, name: str, steps: List[Dict[str, Any]]):
        """Initialize the workflow."""
        self.workflow_id = workflow_id
        self.name = name
        self.steps = steps
        self.current_step = 0
        self.status = "pending"  # pending, running, completed, failed
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.results: List[Dict[str, Any]] = []
        self.error_message: Optional[str] = None
        
        logger.info(f"Integration workflow created: {name} ({workflow_id})")
    
    def start(self) -> None:
        """Start the workflow."""
        self.status = "running"
        self.start_time = datetime.now(timezone.utc)
        logger.info(f"Workflow {self.name} started")
    
    def complete_step(self, step_result: Dict[str, Any]) -> None:
        """Complete a workflow step."""
        self.results.append(step_result)
        self.current_step += 1
        logger.debug(f"Workflow {self.name} completed step {self.current_step}/{len(self.steps)}")
    
    def complete(self) -> None:
        """Mark workflow as completed."""
        self.status = "completed"
        self.end_time = datetime.now(timezone.utc)
        logger.info(f"Workflow {self.name} completed successfully")
    
    def fail(self, error_message: str) -> None:
        """Mark workflow as failed."""
        self.status = "failed"
        self.end_time = datetime.now(timezone.utc)
        self.error_message = error_message
        logger.error(f"Workflow {self.name} failed: {error_message}")
    
    def get_progress(self) -> float:
        """Get workflow progress as percentage."""
        if not self.steps:
            return 0.0
        return (self.current_step / len(self.steps)) * 100.0


class KGNeo4jIntegrationCoordinator:
    """Main coordinator for all integration components."""
    
    def __init__(self, event_manager: KGNeo4jEventManager):
        """Initialize the integration coordinator."""
        self.event_manager = event_manager
        
        # Module integrations
        self.module_integrations: Dict[str, BaseModuleIntegration] = {}
        
        # Webhook manager
        self.webhook_manager = WebhookManager()
        
        # External API clients
        self.api_clients: Dict[str, ExternalAPIClient] = {}
        
        # Workflow management
        self.active_workflows: Dict[str, IntegrationWorkflow] = {}
        self.workflow_history: List[Dict[str, Any]] = []
        
        # Statistics
        self.total_workflows = 0
        self.successful_workflows = 0
        self.failed_workflows = 0
        
        # Event callbacks
        self.on_workflow_complete: Optional[Callable[[IntegrationWorkflow], None]] = None
        self.on_workflow_fail: Optional[Callable[[IntegrationWorkflow], None]] = None
        
        logger.info("KG Neo4j Integration Coordinator initialized")
    
    async def initialize(self) -> None:
        """Initialize all integration components."""
        try:
            # Initialize module integrations
            await self._initialize_module_integrations()
            
            # Initialize webhook manager
            await self._initialize_webhook_manager()
            
            # Initialize external API clients
            await self._initialize_api_clients()
            
            logger.info("Integration Coordinator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Integration Coordinator: {e}")
            raise
    
    async def cleanup(self) -> None:
        """Clean up all integration components."""
        try:
            # Disconnect module integrations
            for integration in self.module_integrations.values():
                await integration.disconnect()
            
            # Close API clients
            for client in self.api_clients.values():
                await client.disconnect()
            
            logger.info("Integration Coordinator cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def _initialize_module_integrations(self) -> None:
        """Initialize all module integrations."""
        available_integrations = get_available_integrations()
        
        for integration_type in available_integrations:
            try:
                integration = get_integration(integration_type, self.event_manager)
                await integration.connect()
                self.module_integrations[integration_type] = integration
                
                logger.debug(f"Module integration {integration_type} initialized")
                
            except Exception as e:
                logger.error(f"Failed to initialize {integration_type} integration: {e}")
    
    async def _initialize_webhook_manager(self) -> None:
        """Initialize webhook manager with default endpoints."""
        try:
            # Add default webhook endpoints (can be configured later)
            default_endpoints = [
                WebhookEndpoint(
                    url="https://api.example.com/webhooks/kg-neo4j",
                    name="Default External System",
                    secret="default_secret"
                )
            ]
            
            for endpoint in default_endpoints:
                self.webhook_manager.add_endpoint(endpoint)
            
            logger.info("Webhook manager initialized with default endpoints")
            
        except Exception as e:
            logger.error(f"Failed to initialize webhook manager: {e}")
    
    async def _initialize_api_clients(self) -> None:
        """Initialize external API clients."""
        try:
            # Add default API clients (can be configured later)
            default_configs = [
                APIConfig(
                    base_url="https://api.example.com",
                    api_key="default_api_key",
                    rate_limit_per_minute=60
                )
            ]
            
            for config in default_configs:
                client = ExternalAPIClient(config)
                await client.connect()
                self.api_clients[config.base_url] = client
            
            logger.info("External API clients initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize API clients: {e}")
    
    # Workflow Management
    
    async def create_workflow(
        self,
        name: str,
        steps: List[Dict[str, Any]],
        workflow_id: Optional[str] = None
    ) -> str:
        """Create a new integration workflow."""
        if not workflow_id:
            workflow_id = f"workflow_{uuid.uuid4().hex[:8]}"
        
        workflow = IntegrationWorkflow(workflow_id, name, steps)
        self.active_workflows[workflow_id] = workflow
        self.total_workflows += 1
        
        logger.info(f"Workflow created: {name} ({workflow_id})")
        return workflow_id
    
    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute a workflow."""
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.active_workflows[workflow_id]
        workflow.start()
        
        try:
            logger.info(f"Executing workflow: {workflow.name}")
            
            for step in workflow.steps:
                step_result = await self._execute_workflow_step(workflow, step)
                workflow.complete_step(step_result)
                
                # Check if step failed
                if step_result.get("status") == "failed":
                    workflow.fail(step_result.get("error", "Step execution failed"))
                    break
            
            # Mark workflow as completed if no failures
            if workflow.status != "failed":
                workflow.complete()
                self.successful_workflows += 1
            
            # Move to history
            workflow_record = self._create_workflow_record(workflow)
            self.workflow_history.append(workflow_record)
            del self.active_workflows[workflow_id]
            
            # Trigger callbacks
            if workflow.status == "completed" and self.on_workflow_complete:
                self.on_workflow_complete(workflow)
            elif workflow.status == "failed" and self.on_workflow_fail:
                self.on_workflow_fail(workflow)
            
            return workflow_record
            
        except Exception as e:
            workflow.fail(str(e))
            self.failed_workflows += 1
            
            # Move to history
            workflow_record = self._create_workflow_record(workflow)
            self.workflow_history.append(workflow_record)
            del self.active_workflows[workflow_id]
            
            # Trigger failure callback
            if self.on_workflow_fail:
                self.on_workflow_fail(workflow)
            
            raise
    
    async def _execute_workflow_step(self, workflow: IntegrationWorkflow, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step."""
        step_type = step.get("type")
        step_name = step.get("name", "Unknown Step")
        
        logger.debug(f"Executing workflow step: {step_name} ({step_type})")
        
        try:
            if step_type == "module_integration":
                return await self._execute_module_integration_step(step)
            elif step_type == "webhook":
                return await self._execute_webhook_step(step)
            elif step_type == "api_call":
                return await self._execute_api_call_step(step)
            elif step_type == "event_publish":
                return await self._execute_event_publish_step(step)
            else:
                return {
                    "status": "failed",
                    "error": f"Unknown step type: {step_type}",
                    "step_name": step_name
                }
                
        except Exception as e:
            logger.error(f"Workflow step failed: {step_name}, Error: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "step_name": step_name
            }
    
    async def _execute_module_integration_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a module integration step."""
        integration_type = step.get("integration_type")
        operation = step.get("operation")
        parameters = step.get("parameters", {})
        
        if integration_type not in self.module_integrations:
            return {
                "status": "failed",
                "error": f"Integration {integration_type} not found"
            }
        
        integration = self.module_integrations[integration_type]
        
        try:
            if operation == "process_aasx_file":
                result = await integration.process_aasx_file(**parameters)
            elif operation == "process_twin_registry_update":
                result = await integration.process_twin_registry_update(**parameters)
            elif operation == "request_ai_analysis":
                result = await integration.request_ai_analysis(**parameters)
            else:
                return {
                    "status": "failed",
                    "error": f"Unknown operation: {operation}"
                }
            
            return {
                "status": "completed",
                "result": result,
                "operation": operation
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "operation": operation
            }
    
    async def _execute_webhook_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a webhook step."""
        endpoint_id = step.get("endpoint_id")
        payload = step.get("payload", {})
        event_type = step.get("event_type", "notification")
        
        try:
            webhook_id = await self.webhook_manager.send_webhook(
                endpoint_id, payload, event_type
            )
            
            return {
                "status": "completed",
                "webhook_id": webhook_id,
                "endpoint_id": endpoint_id
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "endpoint_id": endpoint_id
            }
    
    async def _execute_api_call_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an API call step."""
        client_url = step.get("client_url")
        method = step.get("method", "GET")
        endpoint = step.get("endpoint", "")
        data = step.get("data")
        params = step.get("params")
        
        if client_url not in self.api_clients:
            return {
                "status": "failed",
                "error": f"API client {client_url} not found"
            }
        
        client = self.api_clients[client_url]
        
        try:
            if method == "GET":
                response = await client.get(endpoint, params=params)
            elif method == "POST":
                response = await client.post(endpoint, data=data)
            elif method == "PUT":
                response = await client.put(endpoint, data=data)
            elif method == "DELETE":
                response = await client.delete(endpoint)
            else:
                return {
                    "status": "failed",
                    "error": f"Unsupported HTTP method: {method}"
                }
            
            return {
                "status": "completed",
                "response": {
                    "status_code": response.status_code,
                    "data": response.data,
                    "request_time_ms": response.request_time_ms
                }
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "method": method,
                "endpoint": endpoint
            }
    
    async def _execute_event_publish_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an event publish step."""
        event_type = step.get("event_type")
        event_data = step.get("event_data", {})
        
        try:
            if event_type == "graph_creation":
                event_id = await self.event_manager.publish_graph_creation(**event_data)
            elif event_type == "neo4j_operation":
                event_id = await self.event_manager.publish_neo4j_operation(**event_data)
            elif event_type == "ai_insights":
                event_id = await self.event_manager.publish_ai_insights(**event_data)
            else:
                return {
                    "status": "failed",
                    "error": f"Unknown event type: {event_type}"
                }
            
            return {
                "status": "completed",
                "event_id": event_id,
                "event_type": event_type
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "event_type": event_type
            }
    
    def _create_workflow_record(self, workflow: IntegrationWorkflow) -> Dict[str, Any]:
        """Create a workflow record for history."""
        return {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "status": workflow.status,
            "start_time": workflow.start_time.isoformat() if workflow.start_time else None,
            "end_time": workflow.end_time.isoformat() if workflow.end_time else None,
            "progress": workflow.get_progress(),
            "results": workflow.results,
            "error_message": workflow.error_message
        }
    
    # Predefined Workflows
    
    async def execute_aasx_to_graph_workflow(
        self,
        file_id: str,
        file_path: str,
        user_id: str,
        org_id: str,
        dept_id: str
    ) -> str:
        """Execute AASX to Graph workflow."""
        workflow_steps = [
            {
                "type": "module_integration",
                "name": "Process AASX File",
                "integration_type": "aasx",
                "operation": "process_aasx_file",
                "parameters": {
                    "file_id": file_id,
                    "file_path": file_path,
                    "user_id": user_id,
                    "org_id": org_id,
                    "dept_id": dept_id
                }
            },
            {
                "type": "webhook",
                "name": "Notify External System",
                "endpoint_id": "ep_0",  # Default endpoint
                "payload": {
                    "workflow": "aasx_to_graph",
                    "file_id": file_id,
                    "status": "completed"
                },
                "event_type": "workflow_complete"
            }
        ]
        
        workflow_id = await self.create_workflow(
            name=f"AASX to Graph: {file_id}",
            steps=workflow_steps
        )
        
        # Execute workflow
        await self.execute_workflow(workflow_id)
        return workflow_id
    
    async def execute_twin_enhancement_workflow(
        self,
        graph_id: str,
        twin_data: Dict[str, Any]
    ) -> str:
        """Execute Twin Enhancement workflow."""
        workflow_steps = [
            {
                "type": "module_integration",
                "name": "Enhance Graph with Twin Data",
                "integration_type": "twin_registry",
                "operation": "enhance_existing_graph",
                "parameters": {
                    "graph_id": graph_id,
                    "twin_data": twin_data
                }
            },
            {
                "type": "event_publish",
                "name": "Publish Enhancement Event",
                "event_type": "ai_insights",
                "event_data": {
                    "graph_id": graph_id,
                    "ai_operation_type": "enhancement",
                    "ai_model_version": "twin_registry_v1.0",
                    "confidence_score": 0.95
                }
            }
        ]
        
        workflow_id = await self.create_workflow(
            name=f"Twin Enhancement: {graph_id}",
            steps=workflow_steps
        )
        
        # Execute workflow
        await self.execute_workflow(workflow_id)
        return workflow_id
    
    # Management Methods
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a workflow."""
        # Check active workflows
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            return self._create_workflow_record(workflow)
        
        # Check workflow history
        for record in self.workflow_history:
            if record["workflow_id"] == workflow_id:
                return record
        
        return None
    
    def get_active_workflows(self) -> List[Dict[str, Any]]:
        """Get all active workflows."""
        return [
            self._create_workflow_record(workflow)
            for workflow in self.active_workflows.values()
        ]
    
    def get_workflow_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get workflow history."""
        return self.workflow_history[-limit:] if limit > 0 else self.workflow_history
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get integration coordinator statistics."""
        return {
            "total_workflows": self.total_workflows,
            "successful_workflows": self.successful_workflows,
            "failed_workflows": self.failed_workflows,
            "active_workflows": len(self.active_workflows),
            "workflow_history_size": len(self.workflow_history),
            "module_integrations": len(self.module_integrations),
            "api_clients": len(self.api_clients),
            "webhook_endpoints": len(self.webhook_manager.endpoints)
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a comprehensive health check."""
        try:
            # Check module integrations
            integration_health = {}
            for name, integration in self.module_integrations.items():
                integration_health[name] = await integration.health_check()
            
            # Check webhook manager
            webhook_health = await self.webhook_manager.health_check()
            
            # Check API clients
            api_client_health = {}
            for url, client in self.api_clients.items():
                api_client_health[url] = await client.health_check()
            
            # Overall health
            all_healthy = (
                all(health["status"] == "healthy" for health in integration_health.values()) and
                webhook_health["status"] == "healthy" and
                all(health["status"] == "healthy" for health in api_client_health.values())
            )
            
            return {
                "status": "healthy" if all_healthy else "unhealthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "components": {
                    "module_integrations": integration_health,
                    "webhook_manager": webhook_health,
                    "api_clients": api_client_health
                },
                "overall_health": all_healthy
            }
            
        except Exception as e:
            logger.error(f"Integration coordinator health check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
