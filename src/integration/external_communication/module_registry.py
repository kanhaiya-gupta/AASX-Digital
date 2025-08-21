"""
External Module Registry

This module provides a registry for managing external module endpoints,
including service discovery, health monitoring, and connection management.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict

from .models import ModuleEndpoint, CommunicationProtocol, CommunicationMetrics
from .module_client import ModuleClient, ModuleClientPool


logger = logging.getLogger(__name__)


class ExternalModuleRegistry:
    """
    Registry for managing external module endpoints and connections.
    
    This registry provides:
    - Module endpoint registration and discovery
    - Health monitoring and status tracking
    - Connection pooling and management
    - Load balancing and failover
    - Performance metrics and analytics
    """
    
    def __init__(self, max_endpoints: int = 100):
        """
        Initialize the external module registry.
        
        Args:
            max_endpoints: Maximum number of endpoints to manage
        """
        self.max_endpoints = max_endpoints
        self.endpoints: Dict[str, ModuleEndpoint] = {}
        self.endpoint_health: Dict[str, Dict[str, Any]] = {}
        self.connection_pools: Dict[str, ModuleClientPool] = {}
        self.health_check_interval = 60  # seconds
        self.is_monitoring = False
        self._health_check_task: Optional[asyncio.Task] = None
        self._metrics = {
            "total_endpoints": 0,
            "active_endpoints": 0,
            "unhealthy_endpoints": 0,
            "total_connections": 0,
            "health_checks_performed": 0
        }
    
    async def start_monitoring(self) -> None:
        """Start health monitoring for all endpoints."""
        if self.is_monitoring:
            logger.warning("Health monitoring is already running")
            return
        
        self.is_monitoring = True
        self._health_check_task = asyncio.create_task(self._health_monitoring_loop())
        logger.info("Started external module registry health monitoring")
    
    async def stop_monitoring(self) -> None:
        """Stop health monitoring."""
        self.is_monitoring = False
        
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped external module registry health monitoring")
    
    async def _health_monitoring_loop(self) -> None:
        """Background task for monitoring endpoint health."""
        while self.is_monitoring:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(10)  # Brief pause on error
    
    async def _perform_health_checks(self) -> None:
        """Perform health checks for all endpoints."""
        logger.debug("Performing health checks for all endpoints")
        
        health_check_tasks = []
        for endpoint_id, endpoint in self.endpoints.items():
            if endpoint.is_active:
                task = asyncio.create_task(self._check_endpoint_health(endpoint_id))
                health_check_tasks.append(task)
        
        if health_check_tasks:
            await asyncio.gather(*health_check_tasks, return_exceptions=True)
        
        self._metrics["health_checks_performed"] += 1
        self._update_metrics()
    
    async def _check_endpoint_health(self, endpoint_id: str) -> None:
        """
        Check health of a specific endpoint.
        
        Args:
            endpoint_id: ID of the endpoint to check
        """
        endpoint = self.endpoints.get(endpoint_id)
        if not endpoint:
            return
        
        try:
            # Get or create client pool for this endpoint
            pool = await self._get_or_create_pool(endpoint)
            client = await pool.get_client(endpoint)
            
            # Perform health check
            health_result = await client.health_check()
            
            # Update health status
            self.endpoint_health[endpoint_id] = {
                "status": health_result.get("status", "unknown"),
                "last_check": datetime.utcnow(),
                "response_time_ms": health_result.get("response_time_ms"),
                "details": health_result.get("data", {}),
                "error": health_result.get("error")
            }
            
            # Update endpoint last_seen
            if health_result.get("status") == "healthy":
                endpoint.last_seen = datetime.utcnow()
            
            logger.debug(f"Health check for {endpoint.module_name}: {health_result.get('status')}")
            
        except Exception as e:
            logger.error(f"Health check failed for {endpoint.module_name}: {e}")
            self.endpoint_health[endpoint_id] = {
                "status": "error",
                "last_check": datetime.utcnow(),
                "error": str(e)
            }
    
    async def _get_or_create_pool(self, endpoint: ModuleEndpoint) -> ModuleClientPool:
        """
        Get or create a connection pool for an endpoint.
        
        Args:
            endpoint: Module endpoint
            
        Returns:
            ModuleClientPool instance
        """
        pool_key = f"{endpoint.module_name}_{endpoint.base_url}"
        
        if pool_key not in self.connection_pools:
            pool = ModuleClientPool(max_clients=5)
            self.connection_pools[pool_key] = pool
            logger.debug(f"Created connection pool for {endpoint.module_name}")
        
        return self.connection_pools[pool_key]
    
    def register_endpoint(self, endpoint: ModuleEndpoint) -> str:
        """
        Register a new module endpoint.
        
        Args:
            endpoint: Module endpoint to register
            
        Returns:
            Endpoint ID
        """
        endpoint_id = str(endpoint.module_id)
        
        if len(self.endpoints) >= self.max_endpoints:
            # Remove least recently used endpoint
            self._remove_least_used_endpoint()
        
        self.endpoints[endpoint_id] = endpoint
        self.endpoint_health[endpoint_id] = {
            "status": "unknown",
            "last_check": None,
            "response_time_ms": None,
            "details": {},
            "error": None
        }
        
        self._update_metrics()
        logger.info(f"Registered endpoint: {endpoint.module_name} at {endpoint.base_url}")
        
        return endpoint_id
    
    def unregister_endpoint(self, endpoint_id: str) -> bool:
        """
        Unregister a module endpoint.
        
        Args:
            endpoint_id: ID of the endpoint to unregister
            
        Returns:
            True if unregistered successfully, False otherwise
        """
        if endpoint_id in self.endpoints:
            endpoint = self.endpoints[endpoint_id]
            
            # Close connection pool if it exists
            pool_key = f"{endpoint.module_name}_{endpoint.base_url}"
            if pool_key in self.connection_pools:
                asyncio.create_task(self.connection_pools[pool_key].close_all())
                del self.connection_pools[pool_key]
            
            # Remove endpoint and health data
            del self.endpoints[endpoint_id]
            if endpoint_id in self.endpoint_health:
                del self.endpoint_health[endpoint_id]
            
            self._update_metrics()
            logger.info(f"Unregistered endpoint: {endpoint.module_name}")
            return True
        
        return False
    
    def _remove_least_used_endpoint(self) -> None:
        """Remove the least recently used endpoint."""
        if not self.endpoints:
            return
        
        # Find endpoint with oldest last_seen
        oldest_endpoint_id = min(
            self.endpoints.keys(),
            key=lambda eid: self.endpoints[eid].last_seen
        )
        
        self.unregister_endpoint(oldest_endpoint_id)
        logger.info(f"Removed least used endpoint: {oldest_endpoint_id}")
    
    def get_endpoint(self, endpoint_id: str) -> Optional[ModuleEndpoint]:
        """
        Get endpoint by ID.
        
        Args:
            endpoint_id: Endpoint ID
            
        Returns:
            ModuleEndpoint instance or None
        """
        return self.endpoints.get(endpoint_id)
    
    def get_endpoint_by_name(self, module_name: str) -> Optional[ModuleEndpoint]:
        """
        Get endpoint by module name.
        
        Args:
            module_name: Name of the module
            
        Returns:
            ModuleEndpoint instance or None
        """
        for endpoint in self.endpoints.values():
            if endpoint.module_name == module_name:
                return endpoint
        return None
    
    def get_endpoints_by_type(self, protocol: CommunicationProtocol) -> List[ModuleEndpoint]:
        """
        Get all endpoints of a specific protocol type.
        
        Args:
            protocol: Communication protocol
            
        Returns:
            List of ModuleEndpoint instances
        """
        return [endpoint for endpoint in self.endpoints.values() if endpoint.protocol == protocol]
    
    def get_healthy_endpoints(self) -> List[ModuleEndpoint]:
        """Get all healthy endpoints."""
        healthy = []
        for endpoint_id, endpoint in self.endpoints.items():
            health = self.endpoint_health.get(endpoint_id, {})
            if health.get("status") == "healthy":
                healthy.append(endpoint)
        return healthy
    
    def get_endpoint_health(self, endpoint_id: str) -> Optional[Dict[str, Any]]:
        """
        Get health status for an endpoint.
        
        Args:
            endpoint_id: Endpoint ID
            
        Returns:
            Health status dictionary or None
        """
        return self.endpoint_health.get(endpoint_id)
    
    def update_endpoint_config(
        self,
        endpoint_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update endpoint configuration.
        
        Args:
            endpoint_id: Endpoint ID
            updates: Dictionary of updates to apply
            
        Returns:
            True if updated successfully, False otherwise
        """
        if endpoint_id not in self.endpoints:
            return False
        
        endpoint = self.endpoints[endpoint_id]
        
        # Update allowed fields
        allowed_fields = {
            "timeout_seconds", "retry_attempts", "auth_token",
            "health_endpoint", "api_endpoint", "metadata"
        }
        
        for field, value in updates.items():
            if field in allowed_fields and hasattr(endpoint, field):
                setattr(endpoint, field, value)
        
        endpoint.updated_at = datetime.utcnow()
        logger.info(f"Updated endpoint configuration: {endpoint.module_name}")
        
        return True
    
    async def test_endpoint_connection(self, endpoint_id: str) -> Dict[str, Any]:
        """
        Test connection to an endpoint.
        
        Args:
            endpoint_id: Endpoint ID to test
            
        Returns:
            Connection test results
        """
        endpoint = self.get_endpoint(endpoint_id)
        if not endpoint:
            return {"success": False, "error": "Endpoint not found"}
        
        try:
            pool = await self._get_or_create_pool(endpoint)
            client = await pool.get_client(endpoint)
            
            # Test basic connectivity
            start_time = datetime.utcnow()
            health_result = await client.health_check()
            end_time = datetime.utcnow()
            
            response_time = (end_time - start_time).total_seconds() * 1000
            
            # Safely access health_result dictionary
            health_status = health_result.get("status", "unknown") if health_result else "unknown"
            health_data = health_result.get("data", {}) if health_result else {}
            
            return {
                "success": True,
                "endpoint_name": endpoint.module_name,
                "base_url": endpoint.base_url,
                "protocol": endpoint.protocol.value,
                "response_time_ms": response_time,
                "health_status": health_status,
                "details": health_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "endpoint_name": endpoint.module_name,
                "error": str(e)
            }
    
    def get_registry_summary(self) -> Dict[str, Any]:
        """Get summary of all registered endpoints."""
        summary = {
            "total_endpoints": len(self.endpoints),
            "protocols": defaultdict(int),
            "health_summary": defaultdict(int),
            "endpoints": []
        }
        
        for endpoint_id, endpoint in self.endpoints.items():
            health = self.endpoint_health.get(endpoint_id, {})
            
            summary["protocols"][endpoint.protocol.value] += 1
            summary["health_summary"][health.get("status", "unknown")] += 1
            
            summary["endpoints"].append({
                "endpoint_id": endpoint_id,
                "module_name": endpoint.module_name,
                "base_url": endpoint.base_url,
                "protocol": endpoint.protocol.value,
                "health_status": health.get("status", "unknown"),
                "last_check": health.get("last_check"),
                "last_seen": endpoint.last_seen,
                "is_active": endpoint.is_active
            })
        
        return summary
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get registry metrics."""
        return {
            **self._metrics,
            "endpoints_count": len(self.endpoints),
            "connection_pools_count": len(self.connection_pools),
            "is_monitoring": self.is_monitoring,
            "health_check_interval": self.health_check_interval
        }
    
    def _update_metrics(self) -> None:
        """Update internal metrics."""
        self._metrics["total_endpoints"] = len(self.endpoints)
        self._metrics["active_endpoints"] = len([e for e in self.endpoints.values() if e.is_active])
        self._metrics["unhealthy_endpoints"] = len([
            eid for eid, health in self.endpoint_health.items()
            if health.get("status") not in ["healthy", "unknown"]
        ])
        
        total_connections = 0
        for pool in self.connection_pools.values():
            pool_metrics = pool.get_pool_metrics()
            total_connections += pool_metrics.get("total_clients", 0)
        
        self._metrics["total_connections"] = total_connections
    
    async def cleanup_inactive_endpoints(self, max_inactive_hours: int = 24) -> int:
        """
        Clean up endpoints that have been inactive for too long.
        
        Args:
            max_inactive_hours: Maximum hours of inactivity
            
        Returns:
            Number of endpoints cleaned up
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=max_inactive_hours)
        endpoints_to_remove = []
        
        for endpoint_id, endpoint in self.endpoints.items():
            if endpoint.last_seen < cutoff_time:
                endpoints_to_remove.append(endpoint_id)
        
        for endpoint_id in endpoints_to_remove:
            self.unregister_endpoint(endpoint_id)
        
        if endpoints_to_remove:
            logger.info(f"Cleaned up {len(endpoints_to_remove)} inactive endpoints")
        
        return len(endpoints_to_remove)
    
    async def close_all_connections(self) -> None:
        """Close all connection pools."""
        for pool in self.connection_pools.values():
            await pool.close_all()
        
        self.connection_pools.clear()
        logger.info("Closed all connection pools")
