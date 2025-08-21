"""
Module Connector Service

This service establishes and manages connections to external task modules,
enabling communication and data exchange between the integration layer
and individual modules.

The connector service handles connection pooling, retry logic, and
graceful degradation when modules are unavailable.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from uuid import UUID

import aiohttp
import httpx

from .models import ModuleInfo, ModuleConnection, ModuleStatus


logger = logging.getLogger(__name__)


class ModuleConnectorService:
    """
    Service for establishing and managing connections to external modules.
    
    This service handles connection establishment, health checking,
    connection pooling, and graceful degradation when modules are
    unavailable or experiencing issues.
    """
    
    def __init__(self, max_connections: int = 100, connection_timeout: int = 30):
        """
        Initialize the module connector service.
        
        Args:
            max_connections: Maximum number of concurrent connections
            connection_timeout: Connection timeout in seconds
        """
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.active_connections: Dict[str, ModuleConnection] = {}
        self.connection_pool: Dict[str, List[ModuleConnection]] = {}
        self.connection_history: List[Dict] = []
        self.retry_policies: Dict[str, Dict] = {}
        
        # Default retry policy
        self.default_retry_policy = {
            "max_retries": 3,
            "retry_delay": 1.0,  # seconds
            "backoff_factor": 2.0,
            "max_delay": 60.0  # seconds
        }
    
    async def connect_to_module(self, module_info: ModuleInfo) -> Optional[ModuleConnection]:
        """
        Establish a connection to a specific module.
        
        Args:
            module_info: Information about the module to connect to
            
        Returns:
            ModuleConnection if successful, None otherwise
        """
        try:
            logger.info(f"Attempting to connect to module: {module_info.name}")
            
            # Check if we already have an active connection
            existing_connection = self.active_connections.get(module_info.name)
            if existing_connection and existing_connection.is_active:
                existing_connection.update_activity()
                logger.debug(f"Reusing existing connection to {module_info.name}")
                return existing_connection
            
            # Create new connection
            connection = await self._establish_connection(module_info)
            if connection:
                self.active_connections[module_info.name] = connection
                await self._add_to_connection_pool(module_info.name, connection)
                
                # Record connection history
                self._record_connection_event("connect", module_info.name, "success")
                
                logger.info(f"Successfully connected to module: {module_info.name}")
                return connection
            else:
                self._record_connection_event("connect", module_info.name, "failed")
                logger.error(f"Failed to connect to module: {module_info.name}")
                return None
                
        except Exception as e:
            logger.error(f"Error connecting to module {module_info.name}: {e}")
            self._record_connection_event("connect", module_info.name, "error", str(e))
            return None
    
    async def disconnect_from_module(self, module_name: str) -> bool:
        """
        Disconnect from a specific module.
        
        Args:
            module_name: Name of the module to disconnect from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if module_name in self.active_connections:
                connection = self.active_connections[module_name]
                connection.close()
                del self.active_connections[module_name]
                
                # Remove from connection pool
                if module_name in self.connection_pool:
                    self.connection_pool[module_name] = [
                        conn for conn in self.connection_pool[module_name]
                        if conn.connection_id != connection.connection_id
                    ]
                
                self._record_connection_event("disconnect", module_name, "success")
                logger.info(f"Disconnected from module: {module_name}")
                return True
            else:
                logger.warning(f"No active connection to module: {module_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error disconnecting from module {module_name}: {e}")
            self._record_connection_event("disconnect", module_name, "error", str(e))
            return False
    
    async def execute_module_operation(
        self,
        module_name: str,
        operation: str,
        parameters: Dict[str, Any] = None,
        timeout: int = None
    ) -> Optional[Any]:
        """
        Execute an operation on a specific module.
        
        Args:
            module_name: Name of the module to execute operation on
            operation: Operation to execute
            parameters: Parameters for the operation
            timeout: Operation timeout in seconds
            
        Returns:
            Operation result if successful, None otherwise
        """
        try:
            # Get or establish connection
            connection = await self._get_or_establish_connection(module_name)
            if not connection:
                logger.error(f"Cannot execute operation on module {module_name}: no connection")
                return None
            
            # Execute operation with retry logic
            result = await self._execute_with_retry(
                module_name, operation, parameters, timeout
            )
            
            if result is not None:
                connection.update_activity()
                logger.debug(f"Successfully executed {operation} on module {module_name}")
            else:
                logger.error(f"Failed to execute {operation} on module {module_name}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing operation {operation} on module {module_name}: {e}")
            return None
    
    async def check_module_health(self, module_name: str) -> Dict[str, Any]:
        """
        Check the health status of a specific module.
        
        Args:
            module_name: Name of the module to check
            
        Returns:
            Health status information
        """
        try:
            connection = self.active_connections.get(module_name)
            if not connection:
                return {
                    "status": "disconnected",
                    "message": "No active connection",
                    "last_check": datetime.utcnow().isoformat()
                }
            
            # Try to ping the module
            start_time = time.time()
            try:
                # Simple health check - try to connect to health endpoint
                health_result = await self._perform_health_check(connection)
                response_time = (time.time() - start_time) * 1000
                
                health_status = {
                    "status": "healthy" if health_result else "degraded",
                    "response_time_ms": response_time,
                    "last_check": datetime.utcnow().isoformat(),
                    "connection_id": str(connection.connection_id),
                    "connection_age": (datetime.utcnow() - connection.established_at).total_seconds()
                }
                
                if not health_result:
                    health_status["message"] = "Health check failed"
                
                return health_status
                
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "message": f"Health check error: {str(e)}",
                    "last_check": datetime.utcnow().isoformat(),
                    "connection_id": str(connection.connection_id)
                }
                
        except Exception as e:
            logger.error(f"Error checking health of module {module_name}: {e}")
            return {
                "status": "error",
                "message": f"Health check failed: {str(e)}",
                "last_check": datetime.utcnow().isoformat()
            }
    
    async def get_connection_status(self) -> Dict[str, Any]:
        """Get overall connection service status."""
        return {
            "active_connections": len(self.active_connections),
            "total_connections": sum(len(conns) for conns in self.connection_pool.values()),
            "max_connections": self.max_connections,
            "connection_timeout": self.connection_timeout,
            "connection_history_count": len(self.connection_history),
            "modules_with_connections": list(self.active_connections.keys())
        }
    
    async def _establish_connection(self, module_info: ModuleInfo) -> Optional[ModuleConnection]:
        """Establish a new connection to a module."""
        try:
            # Create connection object
            connection = ModuleConnection(module_info=module_info)
            
            # Test the connection by performing a health check
            if await self._test_connection(connection):
                logger.debug(f"Connection test successful for {module_info.name}")
                return connection
            else:
                logger.warning(f"Connection test failed for {module_info.name}")
                return None
                
        except Exception as e:
            logger.error(f"Error establishing connection to {module_info.name}: {e}")
            return None
    
    async def _test_connection(self, connection: ModuleConnection) -> bool:
        """Test if a connection is working."""
        try:
            # Try to access the module's health endpoint or basic functionality
            module_info = connection.module_info
            
            if module_info.metadata.get("discovery_source") == "webapp_modules":
                # For webapp modules, we can test by checking if the module directory exists
                return True  # Assume webapp modules are available if discovered
            elif module_info.metadata.get("discovery_source") == "src_modules":
                # For src modules, check if the module can be imported
                try:
                    module_path = module_info.metadata.get("module_path", "")
                    if module_path:
                        # Try to import the module
                        import importlib.util
                        spec = importlib.util.spec_from_file_location(
                            module_info.name, 
                            f"{module_path}/__init__.py"
                        )
                        if spec and spec.loader:
                            return True
                except Exception:
                    pass
                return False
            elif module_info.metadata.get("discovery_source") == "environment":
                # For external modules, try to ping the health endpoint
                return await self._test_external_connection(module_info)
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error testing connection: {e}")
            return False
    
    async def _test_external_connection(self, module_info: ModuleInfo) -> bool:
        """Test connection to external module via HTTP."""
        try:
            timeout = aiohttp.ClientTimeout(total=self.connection_timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                health_url = f"{module_info.base_url}{module_info.health_endpoint}"
                async with session.get(health_url) as response:
                    return response.status == 200
        except Exception as e:
            logger.debug(f"External connection test failed for {module_info.name}: {e}")
            return False
    
    async def _perform_health_check(self, connection: ModuleConnection) -> bool:
        """Perform a health check on an established connection."""
        try:
            module_info = connection.module_info
            
            if module_info.metadata.get("discovery_source") == "webapp_modules":
                # For webapp modules, check if routes file exists and is accessible
                routes_path = module_info.metadata.get("module_path", "")
                if routes_path:
                    import os
                    return os.path.exists(f"{routes_path}/routes.py")
                return False
            elif module_info.metadata.get("discovery_source") == "src_modules":
                # For src modules, try to import and check basic functionality
                try:
                    module_path = module_info.metadata.get("module_path", "")
                    if module_path:
                        import importlib.util
                        spec = importlib.util.spec_from_file_location(
                            module_info.name, 
                            f"{module_path}/__init__.py"
                        )
                        if spec and spec.loader:
                            return True
                except Exception:
                    pass
                return False
            elif module_info.metadata.get("discovery_source") == "environment":
                # For external modules, ping health endpoint
                return await self._test_external_connection(module_info)
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error performing health check: {e}")
            return False
    
    async def _get_or_establish_connection(self, module_name: str) -> Optional[ModuleConnection]:
        """Get existing connection or establish new one."""
        # Check for existing active connection
        if module_name in self.active_connections:
            connection = self.active_connections[module_name]
            if connection.is_active:
                return connection
        
        # Try to establish new connection
        # Note: This would require module_info, which we don't have here
        # In a real implementation, we'd need to get this from the discovery service
        logger.warning(f"Cannot establish connection to {module_name}: module_info not available")
        return None
    
    async def _execute_with_retry(
        self,
        module_name: str,
        operation: str,
        parameters: Dict[str, Any],
        timeout: int
    ) -> Optional[Any]:
        """Execute operation with retry logic."""
        retry_policy = self.retry_policies.get(module_name, self.default_retry_policy)
        max_retries = retry_policy["max_retries"]
        retry_delay = retry_policy["retry_delay"]
        backoff_factor = retry_policy["backoff_factor"]
        
        for attempt in range(max_retries + 1):
            try:
                # Execute operation (placeholder for actual implementation)
                result = await self._execute_operation(module_name, operation, parameters, timeout)
                if result is not None:
                    return result
                    
            except Exception as e:
                if attempt == max_retries:
                    logger.error(f"Operation {operation} failed after {max_retries} retries: {e}")
                    return None
                
                # Calculate delay with exponential backoff
                delay = min(retry_delay * (backoff_factor ** attempt), retry_policy["max_delay"])
                logger.warning(f"Operation {operation} failed, retrying in {delay}s (attempt {attempt + 1})")
                await asyncio.sleep(delay)
        
        return None
    
    async def _execute_operation(
        self,
        module_name: str,
        operation: str,
        parameters: Dict[str, Any],
        timeout: int
    ) -> Optional[Any]:
        """Execute a single operation on a module."""
        # This is a placeholder implementation
        # In a real system, this would:
        # 1. Determine the module's interface
        # 2. Call the appropriate method/API
        # 3. Handle the response
        
        logger.debug(f"Executing operation {operation} on module {module_name}")
        
        # For now, return a mock result
        return {
            "module": module_name,
            "operation": operation,
            "parameters": parameters,
            "result": "mock_result",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _add_to_connection_pool(self, module_name: str, connection: ModuleConnection):
        """Add connection to the connection pool."""
        if module_name not in self.connection_pool:
            self.connection_pool[module_name] = []
        self.connection_pool[module_name].append(connection)
    
    def _record_connection_event(self, event_type: str, module_name: str, status: str, details: str = None):
        """Record a connection event in the history."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "module_name": module_name,
            "status": status,
            "details": details
        }
        self.connection_history.append(event)
        
        # Keep only recent history
        if len(self.connection_history) > 1000:
            self.connection_history = self.connection_history[-1000:]
