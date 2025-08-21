"""
API Gateway Service

This module provides the main API gateway that serves as the entry point
for all external API requests to the AAS Data Modeling Engine.

The API gateway handles:
- Request routing and dispatching
- Request/response transformation
- Error handling and logging
- Cross-cutting concerns
- Load balancing and failover
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable, Union
from uuid import UUID

from ..workflow_engine import WorkflowEngine
from ..module_integration import ModuleOrchestratorService
from ..external_communication import ExternalModuleRegistry


logger = logging.getLogger(__name__)


class APIGateway:
    """
    Main API gateway for external module communication.
    
    The API gateway provides:
    - RESTful endpoint routing
    - Request/response handling
    - Integration with core services
    - Error handling and logging
    """
    
    def __init__(self):
        """Initialize the API gateway."""
        self.routes: Dict[str, Dict[str, Callable]] = {}
        self.middleware: List[Callable] = []
        self.workflow_engine: Optional[WorkflowEngine] = None
        self.module_orchestrator: Optional[ModuleOrchestratorService] = None
        self.module_registry: Optional[ExternalModuleRegistry] = None
        self.is_running = False
        self._request_count = 0
        self._error_count = 0
        
        # Initialize default routes
        self._setup_default_routes()
        
        logger.info("API Gateway initialized")
    
    def _setup_default_routes(self) -> None:
        """Setup default API routes."""
        # Health check routes
        self.add_route("GET", "/health", self._health_check)
        self.add_route("GET", "/health/detailed", self._detailed_health_check)
        
        # Workflow routes
        self.add_route("GET", "/api/v1/workflows", self._list_workflows)
        self.add_route("POST", "/api/v1/workflows", self._create_workflow)
        self.add_route("GET", "/api/v1/workflows/{workflow_id}", self._get_workflow)
        self.add_route("PUT", "/api/v1/workflows/{workflow_id}", self._update_workflow)
        self.add_route("DELETE", "/api/v1/workflows/{workflow_id}", self._delete_workflow)
        
        # Module routes
        self.add_route("GET", "/api/v1/modules", self._list_modules)
        self.add_route("GET", "/api/v1/modules/{module_id}", self._get_module)
        self.add_route("POST", "/api/v1/modules/{module_id}/connect", self._connect_module)
        self.add_route("DELETE", "/api/v1/modules/{module_id}/disconnect", self._disconnect_module)
        
        # Data routes
        self.add_route("GET", "/api/v1/data", self._list_data_sources)
        self.add_route("POST", "/api/v1/data/process", self._process_data)
        self.add_route("GET", "/api/v1/data/status/{job_id}", self._get_data_status)
        
        logger.info("Default API routes configured")
    
    def add_route(self, method: str, path: str, handler: Callable) -> None:
        """Add a new API route."""
        if method not in self.routes:
            self.routes[method] = {}
        
        self.routes[method][path] = handler
        logger.info(f"Added route: {method} {path}")
    
    def route(self, path: str, methods: List[str] = None) -> Callable:
        """Decorator for adding routes."""
        if methods is None:
            methods = ["GET"]
        
        def decorator(handler: Callable) -> Callable:
            for method in methods:
                self.add_route(method, path, handler)
            return handler
        return decorator
    
    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware to the request processing pipeline."""
        self.middleware.append(middleware)
        logger.info("Middleware added to API gateway")
    
    def set_workflow_engine(self, engine: WorkflowEngine) -> None:
        """Set the workflow engine instance."""
        self.workflow_engine = engine
        logger.info("Workflow engine connected to API gateway")
    
    def set_module_orchestrator(self, orchestrator: ModuleOrchestratorService) -> None:
        """Set the module orchestrator instance."""
        self.module_orchestrator = orchestrator
        logger.info("Module orchestrator connected to API gateway")
    
    def set_module_registry(self, registry: ExternalModuleRegistry) -> None:
        """Set the module registry instance."""
        self.module_registry = registry
        logger.info("Module registry connected to API gateway")
    
    async def start_gateway(self) -> None:
        """Start the API gateway."""
        if self.is_running:
            logger.warning("API Gateway is already running")
            return
        
        self.is_running = True
        logger.info("API Gateway started")
    
    async def stop_gateway(self) -> None:
        """Stop the API gateway."""
        if not self.is_running:
            logger.warning("API Gateway is not running")
            return
        
        self.is_running = False
        logger.info("API Gateway stopped")
    
    async def process_request(
        self,
        method: str = None,
        path: str = None,
        headers: Dict[str, str] = None,
        body: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, str]] = None,
        request: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process an incoming API request."""
        if not self.is_running:
            return self._create_error_response("Service unavailable", 503)
        
        # Handle both parameter-based and request dict-based calls
        if request is not None:
            method = request.get("method")
            path = request.get("path")
            headers = request.get("headers", {})
            body = request.get("body")
            query_params = request.get("query_params")
        
        if not method or not path:
            return self._create_error_response("Invalid request: missing method or path", 400)
        
        self._request_count += 1
        start_time = datetime.utcnow()
        
        try:
            # Apply middleware
            processed_request = await self._apply_middleware({
                "method": method,
                "path": path,
                "headers": headers or {},
                "body": body,
                "query_params": query_params
            })
            
            # Find and execute route handler
            response = await self._execute_route(processed_request)
            
            # Log request
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Request processed: {method} {path} - {response.get('status_code', 200)} - {duration:.3f}s")
            
            return response
            
        except Exception as e:
            self._error_count += 1
            logger.error(f"Error processing request {method} {path}: {e}")
            return self._create_error_response(f"Internal server error: {str(e)}", 500)
    
    async def _apply_middleware(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Apply all middleware to the request."""
        processed_request = request.copy()
        
        for middleware in self.middleware:
            try:
                processed_request = await middleware(processed_request)
            except Exception as e:
                logger.error(f"Middleware error: {e}")
                # Continue with other middleware even if one fails
        
        return processed_request
    
    async def _execute_route(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the appropriate route handler."""
        method = request["method"]
        path = request["path"]
        
        # Find exact path match first
        if method in self.routes and path in self.routes[method]:
            handler = self.routes[method][path]
            return await handler(request)
        
        # Try to find path with parameters
        for route_path, handler in self.routes.get(method, {}).items():
            if self._path_matches(route_path, path):
                return await handler(request)
        
        return self._create_error_response("Endpoint not found", 404)
    
    def _path_matches(self, route_path: str, request_path: str) -> bool:
        """Check if a request path matches a route path with parameters."""
        route_parts = route_path.split('/')
        request_parts = request_path.split('/')
        
        if len(route_parts) != len(request_parts):
            return False
        
        for route_part, request_part in zip(route_parts, request_parts):
            if route_part.startswith('{') and route_part.endswith('}'):
                continue  # Parameter placeholder
            if route_part != request_part:
                return False
        
        return True
    
    def _create_error_response(self, message: str, status_code: int) -> Dict[str, Any]:
        """Create a standardized error response."""
        return {
            "success": False,
            "error": {
                "message": message,
                "code": status_code,
                "timestamp": datetime.utcnow().isoformat()
            },
            "status_code": status_code
        }
    
    def _create_success_response(self, data: Any, status_code: int = 200) -> Dict[str, Any]:
        """Create a standardized success response."""
        return {
            "success": True,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "status_code": status_code
        }
    
    # Default route handlers
    async def _health_check(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle health check requests."""
        return self._create_success_response({
            "status": "healthy",
            "service": "AAS Data Modeling Engine API",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _detailed_health_check(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle detailed health check requests."""
        health_status = {
            "status": "healthy",
            "service": "AAS Data Modeling Engine API",
            "components": {
                "workflow_engine": self.workflow_engine is not None,
                "module_orchestrator": self.module_orchestrator is not None,
                "module_registry": self.module_registry is not None
            },
            "metrics": {
                "total_requests": self._request_count,
                "error_count": self._error_count,
                "uptime": "running" if self.is_running else "stopped"
            }
        }
        
        return self._create_success_response(health_status)
    
    async def _list_workflows(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle workflow listing requests."""
        if not self.workflow_engine:
            return self._create_error_response("Workflow engine not available", 503)
        
        workflows = self.workflow_engine.get_workflow_definitions()
        return self._create_success_response([{
            "id": str(wf.workflow_id),
            "name": wf.workflow_name,
            "type": wf.workflow_type,
            "version": wf.version
        } for wf in workflows])
    
    async def _create_workflow(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle workflow creation requests."""
        if not self.workflow_engine:
            return self._create_error_response("Workflow engine not available", 503)
        
        # This is a placeholder - in a real implementation, you would parse the request body
        # and create the workflow definition
        return self._create_success_response({
            "message": "Workflow creation endpoint - implementation pending",
            "workflow_id": "placeholder"
        }, 201)
    
    async def _get_workflow(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle workflow retrieval requests."""
        if not self.workflow_engine:
            return self._create_error_response("Workflow engine not available", 503)
        
        # Extract workflow ID from path
        path_parts = request["path"].split('/')
        workflow_id = path_parts[-1]
        
        # This is a placeholder - in a real implementation, you would retrieve the workflow
        return self._create_success_response({
            "message": "Workflow retrieval endpoint - implementation pending",
            "workflow_id": workflow_id
        })
    
    async def _update_workflow(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle workflow update requests."""
        if not self.workflow_engine:
            return self._create_error_response("Workflow engine not available", 503)
        
        # This is a placeholder - in a real implementation, you would update the workflow
        return self._create_success_response({
            "message": "Workflow update endpoint - implementation pending"
        })
    
    async def _delete_workflow(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle workflow deletion requests."""
        if not self.workflow_engine:
            return self._create_error_response("Workflow engine not available", 503)
        
        # This is a placeholder - in a real implementation, you would delete the workflow
        return self._create_success_response({
            "message": "Workflow deletion endpoint - implementation pending"
        })
    
    async def _list_modules(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle module listing requests."""
        if not self.module_registry:
            return self._create_error_response("Module registry not available", 503)
        
        # This is a placeholder - in a real implementation, you would list modules
        return self._create_success_response({
            "message": "Module listing endpoint - implementation pending",
            "modules": []
        })
    
    async def _get_module(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle module retrieval requests."""
        if not self.module_registry:
            return self._create_error_response("Module registry not available", 503)
        
        # This is a placeholder - in a real implementation, you would retrieve the module
        return self._create_success_response({
            "message": "Module retrieval endpoint - implementation pending"
        })
    
    async def _connect_module(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle module connection requests."""
        if not self.module_orchestrator:
            return self._create_error_response("Module orchestrator not available", 503)
        
        # This is a placeholder - in a real implementation, you would connect the module
        return self._create_success_response({
            "message": "Module connection endpoint - implementation pending"
        })
    
    async def _disconnect_module(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle module disconnection requests."""
        if not self.module_orchestrator:
            return self._create_error_response("Module orchestrator not available", 503)
        
        # This is a placeholder - in a real implementation, you would disconnect the module
        return self._create_success_response({
            "message": "Module disconnection endpoint - implementation pending"
        })
    
    async def _list_data_sources(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data source listing requests."""
        # This is a placeholder - in a real implementation, you would list data sources
        return self._create_success_response({
            "message": "Data source listing endpoint - implementation pending",
            "data_sources": []
        })
    
    async def _process_data(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data processing requests."""
        # This is a placeholder - in a real implementation, you would process data
        return self._create_success_response({
            "message": "Data processing endpoint - implementation pending",
            "job_id": "placeholder"
        }, 202)
    
    async def _get_data_status(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data processing status requests."""
        # This is a placeholder - in a real implementation, you would get job status
        return self._create_success_response({
            "message": "Data status endpoint - implementation pending",
            "status": "pending"
        })
    
    def get_gateway_status(self) -> Dict[str, Any]:
        """Get the current status of the API gateway."""
        return {
            "is_running": self.is_running,
            "total_requests": self._request_count,
            "error_count": self._error_count,
            "registered_routes": sum(len(routes) for routes in self.routes.values()),
            "middleware_count": len(self.middleware),
            "connected_services": {
                "workflow_engine": self.workflow_engine is not None,
                "module_orchestrator": self.module_orchestrator is not None,
                "module_registry": self.module_registry is not None
            }
        }
