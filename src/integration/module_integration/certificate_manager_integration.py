"""
Certificate Manager Integration Module

This module provides comprehensive integration services for the Certificate Manager
including cross-module communication, workflow orchestration, and external integrations.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from pathlib import Path

logger = logging.getLogger(__name__)


class IntegrationStatus(Enum):
    """Integration operation status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class IntegrationType(Enum):
    """Types of integrations"""
    CROSS_MODULE = "cross_module"
    WORKFLOW_ORCHESTRATION = "workflow_orchestration"
    EXTERNAL_API = "external_api"
    DATA_SYNC = "data_sync"
    EVENT_BROADCAST = "event_broadcast"
    HEALTH_CHECK = "health_check"
    PERFORMANCE_MONITORING = "performance_monitoring"


class CertificateOperation(Enum):
    """Certificate-related operations"""
    ISSUE_CERTIFICATE = "issue_certificate"
    VALIDATE_CERTIFICATE = "validate_certificate"
    REVOKE_CERTIFICATE = "revoke_certificate"
    RENEW_CERTIFICATE = "renew_certificate"
    VERIFY_CHAIN = "verify_chain"
    GENERATE_REPORT = "generate_report"
    EXPORT_CERTIFICATE = "export_certificate"
    IMPORT_CERTIFICATE = "import_certificate"
    AUDIT_TRAIL = "audit_trail"
    COMPLIANCE_CHECK = "compliance_check"


@dataclass
class IntegrationRequest:
    """Integration request details"""
    request_id: UUID
    integration_type: IntegrationType
    operation: CertificateOperation
    source_module: str
    target_modules: List[str]
    parameters: Dict[str, Any]
    priority: int = 1
    timeout: int = 30
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class IntegrationResponse:
    """Integration response details"""
    request_id: UUID
    status: IntegrationStatus
    result: Optional[Any] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[float] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class CertificateManagerIntegration:
    """
    Certificate Manager Integration Service
    
    Handles:
    - Cross-module communication and coordination
    - Workflow orchestration for certificate operations
    - External API integrations
    - Data synchronization across modules
    - Event broadcasting and subscription
    - Health monitoring and performance tracking
    """
    
    def __init__(self):
        """Initialize the Certificate Manager integration service"""
        self.integration_statuses = list(IntegrationStatus)
        self.integration_types = list(IntegrationType)
        self.certificate_operations = list(CertificateOperation)
        
        # Integration storage and metadata
        self.integration_requests: Dict[UUID, IntegrationRequest] = {}
        self.integration_responses: Dict[UUID, IntegrationResponse] = {}
        self.integration_history: List[Dict[str, Any]] = []
        
        # Module connections and health
        self.connected_modules: Dict[str, Dict[str, Any]] = {}
        self.module_health: Dict[str, Dict[str, Any]] = {}
        self.module_capabilities: Dict[str, List[str]] = {}
        
        # Integration locks and queues
        self.integration_locks: Dict[str, asyncio.Lock] = {}
        self.integration_queue: asyncio.Queue = asyncio.Queue()
        self.response_queue: asyncio.Queue = asyncio.Queue()
        
        # Performance tracking
        self.integration_stats = {
            "total_requests": 0,
            "successful": 0,
            "failed": 0,
            "average_time": 0.0,
            "active_modules": 0,
            "total_operations": 0
        }
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        
        # Initialize module connections
        self._initialize_module_connections()
        
        # Start background tasks
        self._start_background_tasks()
        
        logger.info("Certificate Manager Integration service initialized successfully")
    
    async def integrate_with_module(
        self,
        target_module: str,
        operation: CertificateOperation,
        parameters: Dict[str, Any],
        timeout: int = 30,
        metadata: Optional[Dict[str, Any]] = None
    ) -> IntegrationResponse:
        """
        Integrate with a specific module for certificate operations
        
        Args:
            target_module: Name of the target module
            operation: Certificate operation to perform
            parameters: Operation parameters
            timeout: Operation timeout in seconds
            metadata: Additional metadata
            
        Returns:
            Integration response with operation results
        """
        request_id = uuid4()
        start_time = time.time()
        
        try:
            # Validate integration parameters
            await self._validate_integration_params(target_module, operation, parameters)
            
            # Create integration request
            integration_request = IntegrationRequest(
                request_id=request_id,
                integration_type=IntegrationType.CROSS_MODULE,
                operation=operation,
                source_module="certificate_manager",
                target_modules=[target_module],
                parameters=parameters,
                timeout=timeout,
                metadata=metadata
            )
            
            # Store request
            self.integration_requests[request_id] = integration_request
            
            # Execute integration
            integration_response = await self._execute_module_integration(
                integration_request, start_time
            )
            
            # Store response
            self.integration_responses[request_id] = integration_response
            
            # Update statistics
            await self._update_integration_stats(True, time.time() - start_time)
            
            logger.info(f"Module integration completed successfully: {request_id}")
            return integration_response
            
        except Exception as e:
            await self._update_integration_stats(False, time.time() - start_time)
            logger.error(f"Failed to integrate with module: {str(e)}")
            raise
    
    async def orchestrate_workflow(
        self,
        workflow_name: str,
        steps: List[Dict[str, Any]],
        workflow_parameters: Optional[Dict[str, Any]] = None,
        timeout: int = 300,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate a multi-step workflow involving multiple modules
        
        Args:
            workflow_name: Name of the workflow
            steps: List of workflow steps
            workflow_parameters: Global workflow parameters
            timeout: Total workflow timeout
            metadata: Additional metadata
            
        Returns:
            Workflow execution results
        """
        workflow_id = f"workflow_{int(time.time() * 1000)}"
        start_time = time.time()
        
        try:
            # Validate workflow parameters
            await self._validate_workflow_params(workflow_name, steps, workflow_parameters)
            
            # Create workflow execution context
            workflow_context = await self._create_workflow_context(
                workflow_id, workflow_name, steps, workflow_parameters, metadata
            )
            
            # Execute workflow steps
            workflow_results = await self._execute_workflow_steps(workflow_context)
            
            # Create workflow response
            workflow_response = {
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "status": "completed",
                "steps_executed": len(steps),
                "results": workflow_results,
                "execution_time": time.time() - start_time,
                "metadata": metadata or {}
            }
            
            # Store workflow history
            self.integration_history.append({
                "type": "workflow",
                "id": workflow_id,
                "name": workflow_name,
                "status": "completed",
                "execution_time": time.time() - start_time,
                "results": workflow_results,
                "timestamp": datetime.utcnow()
            })
            
            logger.info(f"Workflow orchestration completed successfully: {workflow_id}")
            return workflow_response
            
        except Exception as e:
            logger.error(f"Failed to orchestrate workflow: {str(e)}")
            raise
    
    async def broadcast_certificate_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        target_modules: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Broadcast certificate events to other modules
        
        Args:
            event_type: Type of certificate event
            event_data: Event data payload
            target_modules: Specific modules to notify (None for all)
            metadata: Additional metadata
            
        Returns:
            Broadcasting results
        """
        try:
            # Validate event parameters
            await self._validate_event_params(event_type, event_data)
            
            # Determine target modules
            modules_to_notify = target_modules or list(self.connected_modules.keys())
            
            # Create event payload
            event_payload = {
                "event_id": str(uuid4()),
                "event_type": event_type,
                "source_module": "certificate_manager",
                "timestamp": datetime.utcnow().isoformat(),
                "data": event_data,
                "metadata": metadata or {}
            }
            
            # Broadcast to target modules
            broadcast_results = []
            for module_name in modules_to_notify:
                if module_name in self.connected_modules:
                    try:
                        result = await self._send_event_to_module(module_name, event_payload)
                        broadcast_results.append({
                            "module": module_name,
                            "status": "success",
                            "result": result
                        })
                    except Exception as e:
                        broadcast_results.append({
                            "module": module_name,
                            "status": "failed",
                            "error": str(e)
                        })
            
            # Create broadcast response
            broadcast_response = {
                "event_id": event_payload["event_id"],
                "event_type": event_type,
                "modules_notified": len(modules_to_notify),
                "successful_notifications": len([r for r in broadcast_results if r["status"] == "success"]),
                "failed_notifications": len([r for r in broadcast_results if r["status"] == "failed"]),
                "results": broadcast_results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Certificate event broadcast completed: {event_payload['event_id']}")
            return broadcast_response
            
        except Exception as e:
            logger.error(f"Failed to broadcast certificate event: {str(e)}")
            raise
    
    async def sync_data_with_modules(
        self,
        sync_type: str,
        data_payload: Dict[str, Any],
        target_modules: Optional[List[str]] = None,
        sync_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Synchronize data with other modules
        
        Args:
            sync_type: Type of data synchronization
            data_payload: Data to synchronize
            target_modules: Specific modules to sync with (None for all)
            sync_options: Synchronization options
            
        Returns:
            Synchronization results
        """
        try:
            # Validate sync parameters
            await self._validate_sync_params(sync_type, data_payload, sync_options)
            
            # Determine target modules
            modules_to_sync = target_modules or list(self.connected_modules.keys())
            
            # Perform data synchronization
            sync_results = []
            for module_name in modules_to_sync:
                if module_name in self.connected_modules:
                    try:
                        result = await self._sync_data_with_module(
                            module_name, sync_type, data_payload, sync_options
                        )
                        sync_results.append({
                            "module": module_name,
                            "status": "success",
                            "result": result
                        })
                    except Exception as e:
                        sync_results.append({
                            "module": module_name,
                            "status": "failed",
                            "error": str(e)
                        })
            
            # Create sync response
            sync_response = {
                "sync_id": str(uuid4()),
                "sync_type": sync_type,
                "modules_synced": len(modules_to_sync),
                "successful_syncs": len([r for r in sync_results if r["status"] == "success"]),
                "failed_syncs": len([r for r in sync_results if r["status"] == "failed"]),
                "results": sync_results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Data synchronization completed: {sync_response['sync_id']}")
            return sync_response
            
        except Exception as e:
            logger.error(f"Failed to synchronize data: {str(e)}")
            raise
    
    async def check_module_health(self, module_name: str) -> Dict[str, Any]:
        """
        Check health status of a specific module
        
        Args:
            module_name: Name of the module to check
            
        Returns:
            Module health information
        """
        try:
            if module_name not in self.connected_modules:
                raise ValueError(f"Module not connected: {module_name}")
            
            # Perform health check
            health_info = await self._perform_module_health_check(module_name)
            
            # Update module health
            self.module_health[module_name] = health_info
            
            return health_info
            
        except Exception as e:
            logger.error(f"Failed to check module health: {str(e)}")
            raise
    
    async def get_integration_status(self, request_id: UUID) -> IntegrationResponse:
        """
        Get status of an integration request
        
        Args:
            request_id: ID of the integration request
            
        Returns:
            Integration response with current status
        """
        if request_id not in self.integration_responses:
            raise ValueError(f"Integration request not found: {request_id}")
        
        return self.integration_responses[request_id]
    
    async def get_integration_history(
        self,
        integration_type: Optional[IntegrationType] = None,
        operation: Optional[CertificateOperation] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get integration operation history
        
        Args:
            integration_type: Filter by integration type
            operation: Filter by certificate operation
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of integration history entries
        """
        history = self.integration_history
        
        if integration_type:
            history = [h for h in history if h.get("integration_type") == integration_type.value]
        
        if operation:
            history = [h for h in history if h.get("operation") == operation.value]
        
        # Sort by timestamp (newest first)
        history.sort(key=lambda x: x.get("timestamp", datetime.min), reverse=True)
        
        return history[offset:offset + limit]
    
    async def get_integration_statistics(self) -> Dict[str, Any]:
        """
        Get integration operation statistics
        
        Returns:
            Integration operation statistics
        """
        stats = self.integration_stats.copy()
        stats["active_modules"] = len(self.connected_modules)
        stats["total_operations"] = len(self.integration_requests)
        return stats
    
    # Private helper methods
    
    def _initialize_module_connections(self):
        """Initialize connections to other modules"""
        # Twin Registry module
        self.connected_modules["twin_registry"] = {
            "name": "twin_registry",
            "type": "core",
            "base_url": "http://localhost:8001",
            "health_endpoint": "/health",
            "api_endpoint": "/api/v1",
            "capabilities": ["digital_twin_management", "asset_registry", "relationship_management"],
            "status": "connected"
        }
        
        # AASX module
        self.connected_modules["aasx"] = {
            "name": "aasx",
            "type": "core",
            "base_url": "http://localhost:8002",
            "health_endpoint": "/health",
            "api_endpoint": "/api/v1",
            "capabilities": ["aasx_processing", "asset_administration_shell", "submodel_management"],
            "status": "connected"
        }
        
        # AI RAG module
        self.connected_modules["ai_rag"] = {
            "name": "ai_rag",
            "type": "ai",
            "base_url": "http://localhost:8003",
            "health_endpoint": "/health",
            "api_endpoint": "/api/v1",
            "capabilities": ["retrieval_augmented_generation", "knowledge_extraction", "semantic_search"],
            "status": "connected"
        }
        
        # Knowledge Graph module
        self.connected_modules["kg_neo4j"] = {
            "name": "kg_neo4j",
            "type": "knowledge",
            "base_url": "http://localhost:8004",
            "health_endpoint": "/health",
            "api_endpoint": "/api/v1",
            "capabilities": ["graph_queries", "relationship_analysis", "knowledge_inference"],
            "status": "connected"
        }
        
        # Initialize module health
        for module_name in self.connected_modules:
            self.module_health[module_name] = {
                "status": "unknown",
                "last_check": None,
                "response_time": None,
                "error_count": 0
            }
    
    def _start_background_tasks(self):
        """Start background tasks for integration management"""
        # Start integration processor
        task1 = asyncio.create_task(self._integration_processor_worker())
        self.background_tasks.append(task1)
        
        # Start health monitor
        task2 = asyncio.create_task(self._health_monitor_worker())
        self.background_tasks.append(task2)
        
        # Start performance monitor
        task3 = asyncio.create_task(self._performance_monitor_worker())
        self.background_tasks.append(task3)
    
    async def _validate_integration_params(
        self,
        target_module: str,
        operation: CertificateOperation,
        parameters: Dict[str, Any]
    ):
        """Validate integration parameters"""
        if not target_module:
            raise ValueError("Target module cannot be empty")
        
        if not isinstance(operation, CertificateOperation):
            raise ValueError("Invalid certificate operation")
        
        if not parameters:
            raise ValueError("Parameters cannot be empty")
        
        if target_module not in self.connected_modules:
            raise ValueError(f"Target module not connected: {target_module}")
    
    async def _validate_workflow_params(
        self,
        workflow_name: str,
        steps: List[Dict[str, Any]],
        workflow_parameters: Optional[Dict[str, Any]]
    ):
        """Validate workflow parameters"""
        if not workflow_name:
            raise ValueError("Workflow name cannot be empty")
        
        if not steps or not isinstance(steps, list):
            raise ValueError("Workflow steps must be a non-empty list")
        
        for i, step in enumerate(steps):
            if not isinstance(step, dict) or "module" not in step or "operation" not in step:
                raise ValueError(f"Invalid workflow step at index {i}")
    
    async def _validate_event_params(self, event_type: str, event_data: Dict[str, Any]):
        """Validate event parameters"""
        if not event_type:
            raise ValueError("Event type cannot be empty")
        
        if not event_data or not isinstance(event_data, dict):
            raise ValueError("Event data must be a non-empty dictionary")
    
    async def _validate_sync_params(
        self,
        sync_type: str,
        data_payload: Dict[str, Any],
        sync_options: Optional[Dict[str, Any]]
    ):
        """Validate synchronization parameters"""
        if not sync_type:
            raise ValueError("Sync type cannot be empty")
        
        if not data_payload or not isinstance(data_payload, dict):
            raise ValueError("Data payload must be a non-empty dictionary")
    
    async def _execute_module_integration(
        self,
        integration_request: IntegrationRequest,
        start_time: float
    ) -> IntegrationResponse:
        """Execute module integration"""
        try:
            # Simulate module integration
            target_module = integration_request.target_modules[0]
            operation = integration_request.operation
            
            # Check module health
            if not await self._is_module_healthy(target_module):
                raise Exception(f"Module {target_module} is not healthy")
            
            # Execute operation
            result = await self._execute_certificate_operation(
                target_module, operation, integration_request.parameters
            )
            
            execution_time = time.time() - start_time
            
            return IntegrationResponse(
                request_id=integration_request.request_id,
                status=IntegrationStatus.COMPLETED,
                result=result,
                execution_time_ms=execution_time * 1000,
                completed_at=datetime.utcnow(),
                metadata=integration_request.metadata
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            
            return IntegrationResponse(
                request_id=integration_request.request_id,
                status=IntegrationStatus.FAILED,
                error_message=str(e),
                execution_time_ms=execution_time * 1000,
                completed_at=datetime.utcnow(),
                metadata=integration_request.metadata
            )
    
    async def _create_workflow_context(
        self,
        workflow_id: str,
        workflow_name: str,
        steps: List[Dict[str, Any]],
        workflow_parameters: Optional[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create workflow execution context"""
        return {
            "workflow_id": workflow_id,
            "workflow_name": workflow_name,
            "steps": steps,
            "parameters": workflow_parameters or {},
            "metadata": metadata or {},
            "created_at": datetime.utcnow(),
            "status": "pending"
        }
    
    async def _execute_workflow_steps(self, workflow_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute workflow steps"""
        results = []
        
        for i, step in enumerate(workflow_context["steps"]):
            try:
                # Execute step
                step_result = await self._execute_workflow_step(step, workflow_context)
                results.append({
                    "step_index": i,
                    "step": step,
                    "status": "completed",
                    "result": step_result
                })
                
            except Exception as e:
                results.append({
                    "step_index": i,
                    "step": step,
                    "status": "failed",
                    "error": str(e)
                })
                # Stop workflow on step failure
                break
        
        return results
    
    async def _execute_workflow_step(
        self,
        step: Dict[str, Any],
        workflow_context: Dict[str, Any]
    ) -> Any:
        """Execute a single workflow step"""
        module_name = step["module"]
        operation = step["operation"]
        parameters = step.get("parameters", {})
        
        # Merge workflow parameters with step parameters
        if workflow_context["parameters"]:
            parameters.update(workflow_context["parameters"])
        
        # Execute step using module integration
        response = await self.integrate_with_module(
            target_module=module_name,
            operation=CertificateOperation(operation),
            parameters=parameters,
            metadata={"workflow_step": True}
        )
        
        if response.status != IntegrationStatus.COMPLETED:
            raise Exception(f"Workflow step failed: {response.error_message}")
        
        return response.result
    
    async def _send_event_to_module(self, module_name: str, event_payload: Dict[str, Any]) -> Any:
        """Send event to a specific module"""
        # Simulate event sending
        module_info = self.connected_modules[module_name]
        
        # Check if module supports event handling
        if "event_handling" not in module_info.get("capabilities", []):
            logger.warning(f"Module {module_name} does not support event handling")
            return {"status": "not_supported"}
        
        # Simulate event processing
        return {
            "status": "received",
            "module": module_name,
            "event_id": event_payload["event_id"],
            "processed_at": datetime.utcnow().isoformat()
        }
    
    async def _sync_data_with_module(
        self,
        module_name: str,
        sync_type: str,
        data_payload: Dict[str, Any],
        sync_options: Optional[Dict[str, Any]]
    ) -> Any:
        """Synchronize data with a specific module"""
        # Simulate data synchronization
        module_info = self.connected_modules[module_name]
        
        # Check if module supports data sync
        if "data_synchronization" not in module_info.get("capabilities", []):
            logger.warning(f"Module {module_name} does not support data synchronization")
            return {"status": "not_supported"}
        
        # Simulate sync operation
        return {
            "status": "synchronized",
            "module": module_name,
            "sync_type": sync_type,
            "data_size": len(str(data_payload)),
            "synced_at": datetime.utcnow().isoformat()
        }
    
    async def _is_module_healthy(self, module_name: str) -> bool:
        """Check if a module is healthy"""
        if module_name not in self.module_health:
            return False
        
        health_info = self.module_health[module_name]
        return health_info.get("status") == "healthy"
    
    async def _execute_certificate_operation(
        self,
        target_module: str,
        operation: CertificateOperation,
        parameters: Dict[str, Any]
    ) -> Any:
        """Execute a certificate operation on a target module"""
        # Simulate operation execution
        module_info = self.connected_modules[target_module]
        
        # Check if module supports the operation
        if operation.value not in module_info.get("capabilities", []):
            logger.warning(f"Module {target_module} does not support operation {operation.value}")
            return {"status": "operation_not_supported"}
        
        # Simulate operation execution
        return {
            "status": "completed",
            "module": target_module,
            "operation": operation.value,
            "parameters": parameters,
            "result": f"Operation {operation.value} completed successfully on {target_module}",
            "executed_at": datetime.utcnow().isoformat()
        }
    
    async def _perform_module_health_check(self, module_name: str) -> Dict[str, Any]:
        """Perform health check on a specific module"""
        # Simulate health check
        module_info = self.connected_modules[module_name]
        
        # Simulate health check response
        health_info = {
            "module": module_name,
            "status": "healthy",
            "last_check": datetime.utcnow(),
            "response_time_ms": 15.5,
            "error_count": 0,
            "capabilities": module_info.get("capabilities", []),
            "version": "1.0.0"
        }
        
        return health_info
    
    async def _integration_processor_worker(self):
        """Background worker for processing integration requests"""
        try:
            while True:
                try:
                    # Get integration request from queue
                    request_data = await asyncio.wait_for(self.integration_queue.get(), timeout=1.0)
                    
                    # Process integration request
                    await self._process_integration_request(request_data)
                    
                    # Mark task as done
                    self.integration_queue.task_done()
                    
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error in integration processor worker: {str(e)}")
                    await asyncio.sleep(1)
        
        except asyncio.CancelledError:
            logger.info("Integration processor worker cancelled")
        except Exception as e:
            logger.error(f"Error in integration processor worker: {str(e)}")
    
    async def _health_monitor_worker(self):
        """Background worker for monitoring module health"""
        try:
            while True:
                try:
                    # Check health of all connected modules
                    for module_name in self.connected_modules:
                        try:
                            health_info = await self.check_module_health(module_name)
                            logger.debug(f"Health check for {module_name}: {health_info['status']}")
                        except Exception as e:
                            logger.warning(f"Health check failed for {module_name}: {str(e)}")
                    
                    # Wait before next health check
                    await asyncio.sleep(30)
                    
                except Exception as e:
                    logger.error(f"Error in health monitor worker: {str(e)}")
                    await asyncio.sleep(30)
        
        except asyncio.CancelledError:
            logger.info("Health monitor worker cancelled")
        except Exception as e:
            logger.error(f"Error in health monitor worker: {str(e)}")
    
    async def _performance_monitor_worker(self):
        """Background worker for monitoring integration performance"""
        try:
            while True:
                try:
                    # Update performance statistics
                    await self._update_performance_stats()
                    
                    # Wait before next update
                    await asyncio.sleep(60)
                    
                except Exception as e:
                    logger.error(f"Error in performance monitor worker: {str(e)}")
                    await asyncio.sleep(60)
        
        except asyncio.CancelledError:
            logger.info("Performance monitor worker cancelled")
        except Exception as e:
            logger.error(f"Error in performance monitor worker: {str(e)}")
    
    async def _process_integration_request(self, request_data: Dict[str, Any]):
        """Process an integration request"""
        try:
            # Simulate request processing
            request_id = request_data.get("id")
            logger.info(f"Processing integration request: {request_id}")
            
            # Add to integration history
            self.integration_history.append({
                "type": "integration_request",
                "id": request_id,
                "data": request_data,
                "processed_at": datetime.utcnow(),
                "status": "processed"
            })
            
        except Exception as e:
            logger.error(f"Error processing integration request: {str(e)}")
    
    async def _update_integration_stats(self, success: bool, execution_time: float):
        """Update integration statistics"""
        self.integration_stats["total_requests"] += 1
        
        if success:
            self.integration_stats["successful"] += 1
        else:
            self.integration_stats["failed"] += 1
        
        # Update average execution time
        total_successful = self.integration_stats["successful"]
        if total_successful > 0:
            current_avg = self.integration_stats["average_time"]
            self.integration_stats["average_time"] = (
                (current_avg * (total_successful - 1) + execution_time) / total_successful
            )
    
    async def _update_performance_stats(self):
        """Update performance statistics"""
        try:
            # Update active modules count
            self.integration_stats["active_modules"] = len(self.connected_modules)
            
            # Update total operations count
            self.integration_stats["total_operations"] = len(self.integration_requests)
            
        except Exception as e:
            logger.error(f"Error updating performance stats: {str(e)}")
