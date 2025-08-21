"""
Module Client for External Communication

This module provides HTTP/GRPC client functionality for communicating
with external modules, including connection pooling, retry logic, and
performance monitoring.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import aiohttp
import httpx

from .models import (
    CommunicationMetrics, 
    CommunicationProtocol, 
    ModuleEndpoint,
    EventMessage,
    EventType
)

logger = logging.getLogger(__name__)


class ModuleClient:
    """
    Client for communicating with external modules via HTTP/GRPC.
    
    This client handles:
    - HTTP/HTTPS requests with authentication
    - Connection pooling and retry logic
    - Performance monitoring and metrics
    - Error handling and fallback strategies
    """
    
    def __init__(self, endpoint: ModuleEndpoint):
        """
        Initialize the module client.
        
        Args:
            endpoint: Module endpoint configuration
        """
        self.endpoint = endpoint
        self.metrics = CommunicationMetrics()
        self.session: Optional[aiohttp.ClientSession] = None
        self._lock = asyncio.Lock()
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    async def connect(self) -> None:
        """Establish connection to the module."""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.endpoint.timeout_seconds)
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=30,
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )
            
            headers = {}
            if self.endpoint.auth_required and self.endpoint.auth_token:
                headers["Authorization"] = f"Bearer {self.endpoint.auth_token}"
            
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=headers
            )
            logger.info(f"Connected to module: {self.endpoint.module_name}")
    
    async def disconnect(self) -> None:
        """Close connection to the module."""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info(f"Disconnected from module: {self.endpoint.module_name}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check module health status.
        
        Returns:
            Health status information
        """
        try:
            # Ensure we have a session
            if not self.session:
                await self.connect()
            
            health_url = urljoin(self.endpoint.base_url, self.endpoint.health_endpoint)
            start_time = time.time()
            
            async with self.session.get(health_url) as response:
                response_time = (time.time() - start_time) * 1000
                self.metrics.update_success(response_time)
                
                if response.status == 200:
                    try:
                        health_data = await response.json()
                    except Exception:
                        health_data = await response.text()
                    
                    logger.debug(f"Health check successful for {self.endpoint.module_name}")
                    return {
                        "status": "healthy",
                        "response_time_ms": response_time,
                        "data": health_data
                    }
                else:
                    self.metrics.update_failure()
                    logger.warning(f"Health check failed for {self.endpoint.module_name}: {response.status}")
                    return {
                        "status": "unhealthy",
                        "response_time_ms": response_time,
                        "error": f"HTTP {response.status}"
                    }
                    
        except aiohttp.ClientConnectorError as e:
            # Connection refused or endpoint not reachable
            self.metrics.update_failure()
            logger.debug(f"Health check connection error for {self.endpoint.module_name}: {e}")
            return {
                "status": "unreachable",
                "error": "Connection refused or endpoint not reachable"
            }
        except asyncio.TimeoutError as e:
            # Request timeout
            self.metrics.update_failure()
            logger.debug(f"Health check timeout for {self.endpoint.module_name}: {e}")
            return {
                "status": "timeout",
                "error": "Request timeout"
            }
        except Exception as e:
            self.metrics.update_failure()
            logger.error(f"Health check error for {self.endpoint.module_name}: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def send_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send HTTP request to the module.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request payload
            headers: Additional headers
            timeout: Request timeout in seconds
            
        Returns:
            Response data and metadata
        """
        if not self.session:
            await self.connect()
        
        url = urljoin(self.endpoint.base_url, endpoint)
        request_timeout = timeout or self.endpoint.timeout_seconds
        
        # Prepare headers
        request_headers = {}
        if self.endpoint.auth_required and self.endpoint.auth_token:
            request_headers["Authorization"] = f"Bearer {self.endpoint.auth_token}"
        if headers:
            request_headers.update(headers)
        
        start_time = time.time()
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                headers=request_headers,
                timeout=aiohttp.ClientTimeout(total=request_timeout)
            ) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status < 400:
                    self.metrics.update_success(response_time)
                    response_data = await response.json() if response.content_type == "application/json" else await response.text()
                    
                    logger.debug(f"Request successful: {method} {endpoint} -> {response.status}")
                    return {
                        "success": True,
                        "status_code": response.status,
                        "data": response_data,
                        "response_time_ms": response_time,
                        "headers": dict(response.headers)
                    }
                else:
                    self.metrics.update_failure()
                    error_text = await response.text()
                    logger.warning(f"Request failed: {method} {endpoint} -> {response.status}: {error_text}")
                    
                    return {
                        "success": False,
                        "status_code": response.status,
                        "error": error_text,
                        "response_time_ms": response_time
                    }
                    
        except asyncio.TimeoutError:
            self.metrics.update_failure()
            logger.error(f"Request timeout: {method} {endpoint}")
            return {
                "success": False,
                "error": "Request timeout",
                "timeout_seconds": request_timeout
            }
        except Exception as e:
            self.metrics.update_failure()
            logger.error(f"Request error: {method} {endpoint}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_event(self, event: EventMessage) -> Dict[str, Any]:
        """
        Send event message to the module.
        
        Args:
            event: Event message to send
            
        Returns:
            Response from event endpoint
        """
        event_endpoint = f"{self.endpoint.api_endpoint}/events"
        return await self.send_request(
            method="POST",
            endpoint=event_endpoint,
            data=event.to_dict()
        )
    
    async def get_data(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get data from the module.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            Response data
        """
        if params:
            # Build query string
            query_params = "&".join([f"{k}={v}" for k, v in params.items()])
            endpoint = f"{endpoint}?{query_params}"
        
        return await self.send_request("GET", endpoint)
    
    async def post_data(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post data to the module.
        
        Args:
            endpoint: API endpoint path
            data: Data to post
            
        Returns:
            Response data
        """
        return await self.send_request("POST", endpoint, data=data)
    
    async def put_data(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Put data to the module.
        
        Args:
            endpoint: API endpoint path
            data: Data to put
            
        Returns:
            Response data
        """
        return await self.send_request("PUT", endpoint, data=data)
    
    async def delete_data(self, endpoint: str) -> Dict[str, Any]:
        """
        Delete data from the module.
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            Response data
        """
        return await self.send_request("DELETE", endpoint)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get communication metrics."""
        return {
            "module_name": self.endpoint.module_name,
            "total_requests": self.metrics.total_requests,
            "successful_requests": self.metrics.successful_requests,
            "failed_requests": self.metrics.failed_requests,
            "average_response_time_ms": self.metrics.average_response_time_ms,
            "last_request_time": self.metrics.last_request_time.isoformat() if self.metrics.last_request_time else None,
            "consecutive_failures": self.metrics.consecutive_failures,
            "consecutive_successes": self.metrics.consecutive_successes
        }


class ModuleClientPool:
    """
    Pool of module clients for efficient connection management.
    
    This pool manages multiple client connections and provides
    load balancing and failover capabilities.
    """
    
    def __init__(self, max_clients: int = 10):
        """
        Initialize the client pool.
        
        Args:
            max_clients: Maximum number of clients in the pool
        """
        self.max_clients = max_clients
        self.clients: Dict[str, ModuleClient] = {}
        self.client_metrics: Dict[str, CommunicationMetrics] = {}
        self._lock = asyncio.Lock()
    
    async def get_client(self, endpoint: ModuleEndpoint) -> ModuleClient:
        """
        Get or create a client for the given endpoint.
        
        Args:
            endpoint: Module endpoint configuration
            
        Returns:
            Module client instance
        """
        async with self._lock:
            client_key = f"{endpoint.module_name}_{endpoint.base_url}"
            
            if client_key not in self.clients:
                if len(self.clients) >= self.max_clients:
                    # Remove least used client
                    await self._remove_least_used_client()
                
                client = ModuleClient(endpoint)
                self.clients[client_key] = client
                self.client_metrics[client_key] = CommunicationMetrics()
                logger.info(f"Created new client for {endpoint.module_name}")
            
            return self.clients[client_key]
    
    async def _remove_least_used_client(self) -> None:
        """Remove the least used client from the pool."""
        if not self.clients:
            return
        
        # Find client with lowest request count
        least_used_key = min(
            self.client_metrics.keys(),
            key=lambda k: self.client_metrics[k].total_requests
        )
        
        client = self.clients[least_used_key]
        await client.disconnect()
        
        del self.clients[least_used_key]
        del self.client_metrics[least_used_key]
        
        logger.info(f"Removed least used client: {least_used_key}")
    
    async def close_all(self) -> None:
        """Close all clients in the pool."""
        async with self._lock:
            for client in self.clients.values():
                await client.disconnect()
            
            self.clients.clear()
            self.client_metrics.clear()
            logger.info("Closed all clients in pool")
    
    def get_pool_metrics(self) -> Dict[str, Any]:
        """Get metrics for all clients in the pool."""
        total_requests = sum(m.total_requests for m in self.client_metrics.values())
        total_successes = sum(m.successful_requests for m in self.client_metrics.values())
        total_failures = sum(m.failed_requests for m in self.client_metrics.values())
        
        return {
            "total_clients": len(self.clients),
            "max_clients": self.max_clients,
            "total_requests": total_requests,
            "total_successes": total_successes,
            "total_failures": total_failures,
            "success_rate": (total_successes / total_requests * 100) if total_requests > 0 else 0,
            "client_details": {
                name: self.client_metrics[name] for name in self.client_metrics
            }
        }
