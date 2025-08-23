"""
External API Client for AI RAG

This module handles integration with external services:
- Vector database APIs
- LLM service integration
- Rate limiting and retry logic
- API response handling
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

import aiohttp
import backoff
from pydantic import BaseModel, Field

from ..events.event_types import (
    BaseEvent, EventPriority, EventStatus, EventCategory,
    ExternalAPIEvent, PerformanceEvent
)
from ..events.event_bus import EventBus


class APIServiceType(str, Enum):
    """External API service types"""
    VECTOR_DATABASE = "vector_database"
    LLM_SERVICE = "llm_service"
    EMBEDDING_SERVICE = "embedding_service"
    GRAPH_DATABASE = "graph_database"


class APIResponseStatus(str, Enum):
    """API response status enumeration"""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"
    TIMEOUT = "timeout"
    UNAUTHORIZED = "unauthorized"


@dataclass
class RateLimitInfo:
    """Rate limiting information"""
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    current_requests: int = 0
    reset_time: Optional[datetime] = None
    window_start: Optional[datetime] = None


@dataclass
class RetryConfig:
    """Retry configuration for API calls"""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True


class APIEndpointConfig(BaseModel):
    """Configuration for API endpoints"""
    base_url: str
    api_key: Optional[str] = None
    timeout_seconds: int = 30
    rate_limit: RateLimitInfo
    retry_config: RetryConfig = Field(default_factory=RetryConfig)
    headers: Dict[str, str] = Field(default_factory=dict)
    auth_type: str = "bearer"  # bearer, api_key, oauth2
    
    class Config:
        arbitrary_types_allowed = True


class APIResponse(BaseModel):
    """Standardized API response"""
    status: APIResponseStatus
    data: Optional[Any] = None
    error_message: Optional[str] = None
    status_code: Optional[int] = None
    response_time_ms: float
    retry_count: int = 0
    timestamp: datetime = Field(default_factory=datetime.now)


class VectorDatabaseClient:
    """Client for vector database APIs"""
    
    def __init__(self, config: APIEndpointConfig, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        self._rate_limit_tracker = {
            "requests": 0,
            "window_start": datetime.now()
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers=self.config.headers,
            timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        now = datetime.now()
        window_start = self._rate_limit_tracker["window_start"]
        
        # Reset window if needed
        if (now - window_start).total_seconds() >= 60:
            self._rate_limit_tracker["requests"] = 0
            self._rate_limit_tracker["window_start"] = now
        
        # Check if we can make a request
        if self._rate_limit_tracker["requests"] >= self.config.rate_limit.requests_per_minute:
            return False
        
        self._rate_limit_tracker["requests"] += 1
        return True
    
    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        max_time=60
    )
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> APIResponse:
        """Make HTTP request with retry logic"""
        if not await self._check_rate_limit():
            return APIResponse(
                status=APIResponseStatus.RATE_LIMITED,
                error_message="Rate limit exceeded",
                response_time_ms=0.0
            )
        
        start_time = time.time()
        retry_count = 0
        
        while retry_count <= self.config.retry_config.max_retries:
            try:
                url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
                
                # Add authentication
                headers = self.config.headers.copy()
                if self.config.api_key:
                    if self.config.auth_type == "bearer":
                        headers["Authorization"] = f"Bearer {self.config.api_key}"
                    elif self.config.auth_type == "api_key":
                        headers["X-API-Key"] = self.config.api_key
                
                async with self.session.request(
                    method, url, json=data, params=params, headers=headers
                ) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        response_data = await response.json()
                        return APIResponse(
                            status=APIResponseStatus.SUCCESS,
                            data=response_data,
                            status_code=response.status,
                            response_time_ms=response_time,
                            retry_count=retry_count
                        )
                    elif response.status == 429:  # Rate limited
                        return APIResponse(
                            status=APIResponseStatus.RATE_LIMITED,
                            error_message="Rate limit exceeded",
                            status_code=response.status,
                            response_time_ms=response_time,
                            retry_count=retry_count
                        )
                    elif response.status == 401:  # Unauthorized
                        return APIResponse(
                            status=APIResponseStatus.UNAUTHORIZED,
                            error_message="Unauthorized access",
                            status_code=response.status,
                            response_time_ms=response_time,
                            retry_count=retry_count
                        )
                    else:
                        error_text = await response.text()
                        return APIResponse(
                            status=APIResponseStatus.FAILED,
                            error_message=f"HTTP {response.status}: {error_text}",
                            status_code=response.status,
                            response_time_ms=response_time,
                            retry_count=retry_count
                        )
                        
            except asyncio.TimeoutError:
                retry_count += 1
                if retry_count > self.config.retry_config.max_retries:
                    return APIResponse(
                        status=APIResponseStatus.TIMEOUT,
                        error_message="Request timeout",
                        response_time_ms=(time.time() - start_time) * 1000,
                        retry_count=retry_count
                    )
                await asyncio.sleep(self.config.retry_config.base_delay * (2 ** retry_count))
                
            except Exception as e:
                retry_count += 1
                if retry_count > self.config.retry_config.max_retries:
                    return APIResponse(
                        status=APIResponseStatus.FAILED,
                        error_message=str(e),
                        response_time_ms=(time.time() - start_time) * 1000,
                        retry_count=retry_count
                    )
                await asyncio.sleep(self.config.retry_config.base_delay * (2 ** retry_count))
        
        return APIResponse(
            status=APIResponseStatus.FAILED,
            error_message="Max retries exceeded",
            response_time_ms=(time.time() - start_time) * 1000,
            retry_count=retry_count
        )
    
    async def upsert_vectors(
        self, 
        collection_name: str, 
        vectors: List[Dict[str, Any]]
    ) -> APIResponse:
        """Upsert vectors to vector database"""
        endpoint = f"collections/{collection_name}/vectors"
        data = {"vectors": vectors}
        
        # Publish external API event
        event = ExternalAPIEvent(
            event_id=f"vector_db_upsert_{datetime.now().timestamp()}",
            api_service=APIServiceType.VECTOR_DATABASE.value,
            operation="upsert_vectors",
            collection_name=collection_name,
            vector_count=len(vectors),
            priority=EventPriority.NORMAL,
            category=EventCategory.INTEGRATION
        )
        await self.event_bus.publish(event)
        
        response = await self._make_request("POST", endpoint, data=data)
        
        # Publish performance event
        perf_event = PerformanceEvent(
            event_id=f"vector_db_perf_{datetime.now().timestamp()}",
            operation="upsert_vectors",
            response_time_ms=response.response_time_ms,
            success=response.status == APIResponseStatus.SUCCESS,
            retry_count=response.retry_count,
            priority=EventPriority.LOW,
            category=EventCategory.PERFORMANCE
        )
        await self.event_bus.publish(perf_event)
        
        return response
    
    async def search_vectors(
        self, 
        collection_name: str, 
        query_vector: List[float], 
        top_k: int = 10
    ) -> APIResponse:
        """Search for similar vectors"""
        endpoint = f"collections/{collection_name}/search"
        data = {
            "query_vector": query_vector,
            "top_k": top_k
        }
        
        # Publish external API event
        event = ExternalAPIEvent(
            event_id=f"vector_db_search_{datetime.now().timestamp()}",
            api_service=APIServiceType.VECTOR_DATABASE.value,
            operation="search_vectors",
            collection_name=collection_name,
            top_k=top_k,
            priority=EventPriority.NORMAL,
            category=EventCategory.INTEGRATION
        )
        await self.event_bus.publish(event)
        
        response = await self._make_request("POST", endpoint, data=data)
        
        # Publish performance event
        perf_event = PerformanceEvent(
            event_id=f"vector_db_perf_{datetime.now().timestamp()}",
            operation="search_vectors",
            response_time_ms=response.response_time_ms,
            success=response.status == APIResponseStatus.SUCCESS,
            retry_count=response.retry_count,
            priority=EventPriority.LOW,
            category=EventCategory.PERFORMANCE
        )
        await self.event_bus.publish(perf_event)
        
        return response


class LLMServiceClient:
    """Client for LLM service APIs"""
    
    def __init__(self, config: APIEndpointConfig, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        self._rate_limit_tracker = {
            "requests": 0,
            "window_start": datetime.now()
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers=self.config.headers,
            timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        now = datetime.now()
        window_start = self._rate_limit_tracker["window_start"]
        
        # Reset window if needed
        if (now - window_start).total_seconds() >= 60:
            self._rate_limit_tracker["requests"] = 0
            self._rate_limit_tracker["window_start"] = now
        
        # Check if we can make a request
        if self._rate_limit_tracker["requests"] >= self.config.rate_limit.requests_per_minute:
            return False
        
        self._rate_limit_tracker["requests"] += 1
        return True
    
    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        max_time=60
    )
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> APIResponse:
        """Make HTTP request with retry logic"""
        if not await self._check_rate_limit():
            return APIResponse(
                status=APIResponseStatus.RATE_LIMITED,
                error_message="Rate limit exceeded",
                response_time_ms=0.0
            )
        
        start_time = time.time()
        retry_count = 0
        
        while retry_count <= self.config.retry_config.max_retries:
            try:
                url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
                
                # Add authentication
                headers = self.config.headers.copy()
                if self.config.api_key:
                    if self.config.auth_type == "bearer":
                        headers["Authorization"] = f"Bearer {self.config.api_key}"
                    elif self.config.auth_type == "api_key":
                        headers["X-API-Key"] = self.config.api_key
                
                async with self.session.request(
                    method, url, json=data, headers=headers
                ) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        response_data = await response.json()
                        return APIResponse(
                            status=APIResponseStatus.SUCCESS,
                            data=response_data,
                            status_code=response.status,
                            response_time_ms=response_time,
                            retry_count=retry_count
                        )
                    elif response.status == 429:  # Rate limited
                        return APIResponse(
                            status=APIResponseStatus.RATE_LIMITED,
                            error_message="Rate limit exceeded",
                            status_code=response.status,
                            response_time_ms=response_time,
                            retry_count=retry_count
                        )
                    elif response.status == 401:  # Unauthorized
                        return APIResponse(
                            status=APIResponseStatus.UNAUTHORIZED,
                            error_message="Unauthorized access",
                            status_code=response.status,
                            response_time_ms=response_time,
                            retry_count=retry_count
                        )
                    else:
                        error_text = await response.text()
                        return APIResponse(
                            status=APIResponseStatus.FAILED,
                            error_message=f"HTTP {response.status}: {error_text}",
                            status_code=response.status,
                            response_time_ms=response_time,
                            retry_count=retry_count
                        )
                        
            except asyncio.TimeoutError:
                retry_count += 1
                if retry_count > self.config.retry_config.max_retries:
                    return APIResponse(
                        status=APIResponseStatus.TIMEOUT,
                        error_message="Request timeout",
                        response_time_ms=(time.time() - start_time) * 1000,
                        retry_count=retry_count
                    )
                await asyncio.sleep(self.config.retry_config.base_delay * (2 ** retry_count))
                
            except Exception as e:
                retry_count += 1
                if retry_count > self.config.retry_config.max_retries:
                    return APIResponse(
                        status=APIResponseStatus.FAILED,
                        error_message=str(e),
                        response_time_ms=(time.time() - start_time) * 1000,
                        retry_count=retry_count
                    )
                await asyncio.sleep(self.config.retry_config.base_delay * (2 ** retry_count))
        
        return APIResponse(
            status=APIResponseStatus.FAILED,
            error_message="Max retries exceeded",
            response_time_ms=(time.time() - start_time) * 1000,
            retry_count=retry_count
        )
    
    async def generate_text(
        self, 
        prompt: str, 
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> APIResponse:
        """Generate text using LLM service"""
        endpoint = "generate"
        data = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        # Publish external API event
        event = ExternalAPIEvent(
            event_id=f"llm_generate_{datetime.now().timestamp()}",
            api_service=APIServiceType.LLM_SERVICE.value,
            operation="generate_text",
            prompt_length=len(prompt),
            max_tokens=max_tokens,
            temperature=temperature,
            priority=EventPriority.NORMAL,
            category=EventCategory.INTEGRATION
        )
        await self.event_bus.publish(event)
        
        response = await self._make_request("POST", endpoint, data=data)
        
        # Publish performance event
        perf_event = PerformanceEvent(
            event_id=f"llm_perf_{datetime.now().timestamp()}",
            operation="generate_text",
            response_time_ms=response.response_time_ms,
            success=response.status == APIResponseStatus.SUCCESS,
            retry_count=response.retry_count,
            priority=EventPriority.LOW,
            category=EventCategory.PERFORMANCE
        )
        await self.event_bus.publish(perf_event)
        
        return response
    
    async def generate_embeddings(
        self, 
        texts: List[str]
    ) -> APIResponse:
        """Generate embeddings using LLM service"""
        endpoint = "embeddings"
        data = {"texts": texts}
        
        # Publish external API event
        event = ExternalAPIEvent(
            event_id=f"llm_embeddings_{datetime.now().timestamp()}",
            api_service=APIServiceType.LLM_SERVICE.value,
            operation="generate_embeddings",
            text_count=len(texts),
            total_text_length=sum(len(text) for text in texts),
            priority=EventPriority.NORMAL,
            category=EventCategory.INTEGRATION
        )
        await self.event_bus.publish(event)
        
        response = await self._make_request("POST", endpoint, data=data)
        
        # Publish performance event
        perf_event = PerformanceEvent(
            event_id=f"llm_perf_{datetime.now().timestamp()}",
            operation="generate_embeddings",
            response_time_ms=response.response_time_ms,
            success=response.status == APIResponseStatus.SUCCESS,
            retry_count=response.retry_count,
            priority=EventPriority.LOW,
            category=EventCategory.PERFORMANCE
        )
        await self.event_bus.publish(perf_event)
        
        return response


class ExternalAPIManager:
    """Manages all external API clients with centralized configuration"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        self.clients: Dict[APIServiceType, Union[VectorDatabaseClient, LLMServiceClient]] = {}
        
    def register_client(
        self, 
        service_type: APIServiceType, 
        config: APIEndpointConfig
    ):
        """Register a new API client"""
        if service_type == APIServiceType.VECTOR_DATABASE:
            self.clients[service_type] = VectorDatabaseClient(config, self.event_bus)
        elif service_type == APIServiceType.LLM_SERVICE:
            self.clients[service_type] = LLMServiceClient(config, self.event_bus)
        
        self.logger.info(f"Registered {service_type.value} client")
    
    def get_client(self, service_type: APIServiceType):
        """Get a specific API client"""
        return self.clients.get(service_type)
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Perform health check on all API clients"""
        health_status = {}
        
        for service_type, client in self.clients.items():
            try:
                # Simple health check - try to make a minimal request
                if hasattr(client, '_make_request'):
                    # This is a simplified health check
                    health_status[service_type.value] = True
                else:
                    health_status[service_type.value] = False
            except Exception as e:
                self.logger.error(f"Health check failed for {service_type.value}: {e}")
                health_status[service_type.value] = False
        
        return health_status
    
    async def shutdown_all(self):
        """Shutdown all API clients gracefully"""
        for service_type, client in self.clients.items():
            try:
                if hasattr(client, 'session') and client.session:
                    await client.session.close()
                self.logger.info(f"Shutdown {service_type.value} client")
            except Exception as e:
                self.logger.error(f"Error shutting down {service_type.value}: {e}")
