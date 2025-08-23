"""
Knowledge Graph Neo4j External API Client

Asynchronous HTTP client for making requests to external APIs.
Provides rate limiting, retry logic, and comprehensive error handling.
"""

import logging
import asyncio
import aiohttp
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timezone
from dataclasses import dataclass, field
import json
import time

logger = logging.getLogger(__name__)


@dataclass
class APIConfig:
    """Configuration for an external API client."""
    
    base_url: str
    api_key: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    rate_limit_per_minute: int = 60
    retry_count: int = 3
    retry_delay: float = 1.0
    max_concurrent_requests: int = 10
    
    def __post_init__(self):
        """Validate API configuration."""
        if not self.base_url:
            raise ValueError("Base URL is required")
        if not self.base_url.startswith(('http://', 'https://')):
            raise ValueError("Base URL must use HTTP or HTTPS protocol")
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        if self.rate_limit_per_minute <= 0:
            raise ValueError("Rate limit must be positive")


@dataclass
class APIResponse:
    """Response from an API request."""
    
    status_code: int
    data: Any
    headers: Dict[str, str]
    request_time_ms: float
    url: str
    method: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def is_success(self) -> bool:
        """Check if the response indicates success."""
        return 200 <= self.status_code < 300
    
    def is_client_error(self) -> bool:
        """Check if the response indicates a client error."""
        return 400 <= self.status_code < 500
    
    def is_server_error(self) -> bool:
        """Check if the response indicates a server error."""
        return 500 <= self.status_code < 600


class RateLimiter:
    """Rate limiter for API requests."""
    
    def __init__(self, requests_per_minute: int):
        """Initialize the rate limiter."""
        self.requests_per_minute = requests_per_minute
        self.request_times: List[float] = []
        self.lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """Acquire permission to make a request."""
        async with self.lock:
            current_time = time.time()
            
            # Remove old request times (older than 1 minute)
            self.request_times = [t for t in self.request_times if current_time - t < 60]
            
            # Check if we're at the rate limit
            if len(self.request_times) >= self.requests_per_minute:
                # Wait until we can make another request
                oldest_request = min(self.request_times)
                wait_time = 60 - (current_time - oldest_request)
                if wait_time > 0:
                    logger.debug(f"Rate limit reached, waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
            
            # Add current request time
            self.request_times.append(current_time)


class ExternalAPIClient:
    """Asynchronous HTTP client for external APIs."""
    
    def __init__(self, config: APIConfig):
        """Initialize the API client."""
        self.config = config
        self.rate_limiter = RateLimiter(config.rate_limit_per_minute)
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore = asyncio.Semaphore(config.max_concurrent_requests)
        
        # Statistics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.retry_requests = 0
        
        # Request history
        self.request_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
        
        logger.info(f"External API client initialized for {config.base_url}")
    
    async def connect(self) -> None:
        """Establish connection and create HTTP session."""
        try:
            # Prepare default headers
            headers = {
                "User-Agent": "KG-Neo4j-API-Client/1.0",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            # Add API key if provided
            if self.config.api_key:
                headers["Authorization"] = f"Bearer {self.config.api_key}"
            
            # Add custom headers
            headers.update(self.config.headers)
            
            # Create session
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
            
            logger.info(f"API client connected to {self.config.base_url}")
            
        except Exception as e:
            logger.error(f"Failed to connect API client: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("API client disconnected")
    
    async def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """Make an HTTP request to the API."""
        if not self.session:
            raise RuntimeError("API client not connected")
        
        # Wait for rate limiter
        await self.rate_limiter.acquire()
        
        # Acquire semaphore for concurrent request limiting
        async with self.semaphore:
            return await self._make_request(method, endpoint, data, params, headers)
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """Make the actual HTTP request with retry logic."""
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        request_headers = headers or {}
        
        for attempt in range(self.config.retry_count + 1):
            try:
                start_time = time.time()
                
                # Prepare request data
                request_data = None
                if data:
                    request_data = json.dumps(data)
                
                # Make request
                async with self.session.request(
                    method=method,
                    url=url,
                    data=request_data,
                    params=params,
                    headers=request_headers
                ) as response:
                    
                    request_time = (time.time() - start_time) * 1000
                    
                    # Read response data
                    try:
                        response_data = await response.json()
                    except (json.JSONDecodeError, aiohttp.ContentTypeError):
                        response_data = await response.text()
                    
                    # Create response object
                    api_response = APIResponse(
                        status_code=response.status,
                        data=response_data,
                        headers=dict(response.headers),
                        request_time_ms=request_time,
                        url=url,
                        method=method
                    )
                    
                    # Record request
                    self._record_request(method, url, api_response, attempt)
                    
                    # Check if request was successful
                    if api_response.is_success():
                        self.successful_requests += 1
                        logger.debug(f"API request successful: {method} {url}")
                        return api_response
                    
                    # Handle client errors (don't retry)
                    if api_response.is_client_error():
                        self.failed_requests += 1
                        logger.warning(f"API client error: {method} {url} - {response.status}")
                        return api_response
                    
                    # Handle server errors (retry if possible)
                    if api_response.is_server_error() and attempt < self.config.retry_count:
                        self.retry_requests += 1
                        wait_time = self.config.retry_delay * (2 ** attempt)  # Exponential backoff
                        
                        logger.warning(f"API server error, retrying in {wait_time:.1f}s: {method} {url}")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    # Max retries exceeded or other error
                    self.failed_requests += 1
                    logger.error(f"API request failed after {attempt + 1} attempts: {method} {url}")
                    return api_response
                
            except asyncio.TimeoutError:
                if attempt < self.config.retry_count:
                    self.retry_requests += 1
                    wait_time = self.config.retry_delay * (2 ** attempt)
                    
                    logger.warning(f"API request timeout, retrying in {wait_time:.1f}s: {method} {url}")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    self.failed_requests += 1
                    logger.error(f"API request timeout after {attempt + 1} attempts: {method} {url}")
                    raise
                    
            except Exception as e:
                if attempt < self.config.retry_count:
                    self.retry_requests += 1
                    wait_time = self.config.retry_delay * (2 ** attempt)
                    
                    logger.warning(f"API request error, retrying in {wait_time:.1f}s: {method} {url} - {e}")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    self.failed_requests += 1
                    logger.error(f"API request failed after {attempt + 1} attempts: {method} {url} - {e}")
                    raise
        
        # This should never be reached, but just in case
        raise RuntimeError(f"API request failed after {self.config.retry_count} attempts")
    
    def _record_request(
        self,
        method: str,
        url: str,
        response: APIResponse,
        attempt: int
    ) -> None:
        """Record a request in the history."""
        self.total_requests += 1
        
        request_record = {
            "method": method,
            "url": url,
            "status_code": response.status_code,
            "request_time_ms": response.request_time_ms,
            "attempt": attempt + 1,
            "timestamp": response.timestamp.isoformat()
        }
        
        self.request_history.append(request_record)
        
        # Maintain history size limit
        if len(self.request_history) > self.max_history_size:
            self.request_history.pop(0)
    
    # Convenience methods for common HTTP methods
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """Make a GET request."""
        return await self.request("GET", endpoint, params=params, headers=headers)
    
    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """Make a POST request."""
        return await self.request("POST", endpoint, data=data, params=params, headers=headers)
    
    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """Make a PUT request."""
        return await self.request("PUT", endpoint, data=data, params=params, headers=headers)
    
    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """Make a DELETE request."""
        return await self.request("DELETE", endpoint, params=params, headers=headers)
    
    async def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """Make a PATCH request."""
        return await self.request("PATCH", endpoint, data=data, params=params, headers=headers)
    
    # Management Methods
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get API client statistics."""
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "retry_requests": self.retry_requests,
            "success_rate": (self.successful_requests / max(self.total_requests, 1)) * 100,
            "request_history_size": len(self.request_history),
            "rate_limit_per_minute": self.config.rate_limit_per_minute,
            "max_concurrent_requests": self.config.max_concurrent_requests
        }
    
    def get_recent_requests(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent request history."""
        return self.request_history[-limit:] if limit > 0 else self.request_history
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the API client."""
        try:
            if not self.session:
                return {
                    "status": "unhealthy",
                    "error": "Client not connected",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Try a simple HEAD request to check connectivity
            start_time = time.time()
            try:
                async with self.session.head(self.config.base_url, timeout=5) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    return {
                        "status": "healthy" if response.status < 500 else "unhealthy",
                        "response_code": response.status,
                        "response_time_ms": response_time,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            logger.error(f"API client health check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def clear_request_history(self, older_than_hours: int = 24) -> int:
        """Clear old request history."""
        cutoff_time = time.time() - (older_than_hours * 3600)
        
        original_count = len(self.request_history)
        self.request_history = [
            record for record in self.request_history
            if time.mktime(datetime.fromisoformat(record["timestamp"]).timetuple()) > cutoff_time
        ]
        
        cleared_count = original_count - len(self.request_history)
        logger.info(f"Cleared {cleared_count} old API request records")
        
        return cleared_count
    
    def update_config(self, **kwargs) -> None:
        """Update client configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.info(f"Updated API client config: {key} = {value}")
            else:
                logger.warning(f"Unknown config key: {key}")
        
        # Update rate limiter if rate limit changed
        if "rate_limit_per_minute" in kwargs:
            self.rate_limiter = RateLimiter(self.config.rate_limit_per_minute)
        
        # Update semaphore if max concurrent requests changed
        if "max_concurrent_requests" in kwargs:
            self.semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
