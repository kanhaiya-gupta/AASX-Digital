"""
AI/RAG Integration for Twin Registry Population
Provides hooks and integration points with AI/RAG systems for enhanced population
"""

import logging
import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List, Union, Callable
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass

from ..events.event_types import Event, create_system_event
from ..events.event_bus import EventBus

logger = logging.getLogger(__name__)


@dataclass
class AIRAGRequest:
    """AI/RAG request information"""
    request_id: str
    request_type: str
    input_data: Dict[str, Any]
    parameters: Dict[str, Any]
    timestamp: datetime
    user_id: str
    org_id: str
    priority: str = "normal"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class AIRAGResponse:
    """AI/RAG response information"""
    request_id: str
    response_data: Dict[str, Any]
    confidence_score: float
    processing_time: float
    timestamp: datetime
    status: str
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class AIRAGIntegrationConfig:
    """AI/RAG integration configuration"""
    api_endpoint: str
    api_key: Optional[str] = None
    timeout: int = 120  # seconds
    max_retry_attempts: int = 3
    retry_delay: int = 5  # seconds
    batch_size: int = 10
    enable_auto_enhancement: bool = True
    enhancement_delay: int = 30  # seconds after AI/RAG completion
    max_concurrent_requests: int = 5
    request_queue_size: int = 100
    enable_caching: bool = True
    cache_ttl: int = 3600  # 1 hour in seconds
    cleanup_old_requests: bool = True
    max_request_age: int = 86400 * 7  # 7 days in seconds


class AIRAGIntegration:
    """AI/RAG system integration for enhanced twin registry population"""
    
    def __init__(
        self,
        event_bus: EventBus,
        config: AIRAGIntegrationConfig
    ):
        self.event_bus = event_bus
        self.config = config
        
        # Integration state
        self.is_active = False
        self.processing_task: Optional[asyncio.Task] = None
        self.request_queue: asyncio.Queue = asyncio.Queue(maxsize=config.request_queue_size)
        self.semaphore = asyncio.Semaphore(config.max_concurrent_requests)
        
        # Registered callbacks
        self.registered_callbacks: List[Callable] = []
        
        # Request tracking
        self.requests: Dict[str, AIRAGRequest] = {}
        self.responses: Dict[str, AIRAGResponse] = {}
        self.pending_requests: List[str] = []
        self.completed_requests: List[str] = []
        self.failed_requests: List[str] = []
        
        # Caching
        self.response_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_timestamps: Dict[str, float] = {}
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "successful_enhancements": 0,
            "failed_enhancements": 0,
            "last_enhancement_time": None,
            "average_enhancement_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        # HTTP session
        self.http_session: Optional[aiohttp.ClientSession] = None
    
    async def start(self) -> None:
        """Start AI/RAG integration processing"""
        try:
            if self.is_active:
                logger.warning("AI/RAG integration is already active")
                return
            
            self.is_active = True
            
            # Create HTTP session
            self.http_session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
            
            # Start processing task
            self.processing_task = asyncio.create_task(self._process_requests())
            
            logger.info("AI/RAG integration started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start AI/RAG integration: {e}")
            self.is_active = False
            raise
    
    async def stop(self) -> None:
        """Stop AI/RAG integration processing"""
        try:
            if not self.is_active:
                logger.warning("AI/RAG integration is not active")
                return
            
            self.is_active = False
            
            # Cancel processing task
            if self.processing_task:
                self.processing_task.cancel()
                try:
                    await self.processing_task
                except asyncio.CancelledError:
                    pass
            
            # Close HTTP session
            if self.http_session:
                await self.http_session.close()
                self.http_session = None
            
            logger.info("AI/RAG integration stopped successfully")
            
        except Exception as e:
            logger.error(f"Failed to stop AI/RAG integration: {e}")
            raise
    
    async def _process_requests(self) -> None:
        """Process AI/RAG requests from queue"""
        while self.is_active:
            try:
                # Get request from queue
                try:
                    request = await asyncio.wait_for(
                        self.request_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Process request with semaphore for concurrency control
                async with self.semaphore:
                    await self._process_single_request(request)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in AI/RAG request processing: {e}")
                await asyncio.sleep(1.0)
    
    async def _process_single_request(self, request: AIRAGRequest) -> None:
        """Process a single AI/RAG request"""
        try:
            request_id = request.request_id
            
            # Check cache first
            if self.config.enable_caching:
                cached_response = self._get_cached_response(request_id)
                if cached_response:
                    self.stats["cache_hits"] += 1
                    await self._handle_cached_response(request, cached_response)
                    return
            
            self.stats["cache_misses"] += 1
            
            # Add to pending requests
            if request_id not in self.pending_requests:
                self.pending_requests.append(request_id)
            
            # Update request status
            self.requests[request_id] = request
            
            # Send request to AI/RAG API
            start_time = datetime.now(timezone.utc)
            response = await self._send_ai_rag_request(request)
            
            if response:
                # Calculate processing time
                processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
                
                # Create response object
                ai_response = AIRAGResponse(
                    request_id=request_id,
                    response_data=response,
                    confidence_score=response.get("confidence_score", 0.0),
                    processing_time=processing_time,
                    timestamp=datetime.now(timezone.utc),
                    status="completed",
                    metadata=response.get("metadata", {})
                )
                
                # Store response
                self.responses[request_id] = ai_response
                
                # Update tracking
                if request_id in self.pending_requests:
                    self.pending_requests.remove(request_id)
                if request_id not in self.completed_requests:
                    self.completed_requests.append(request_id)
                
                # Cache response if enabled
                if self.config.enable_caching:
                    self._cache_response(request_id, response)
                
                # Trigger enhancement after delay
                if self.config.enable_auto_enhancement:
                    await asyncio.sleep(self.config.enhancement_delay)
                    await self._trigger_registry_enhancement(request, ai_response)
                
                # Execute callbacks
                await self._execute_callbacks("ai_rag_completion", request, ai_response)
                
                logger.info(f"AI/RAG request completed: {request_id}")
                
            else:
                # Handle failed request
                if request_id in self.pending_requests:
                    self.pending_requests.remove(request_id)
                if request_id not in self.failed_requests:
                    self.failed_requests.append(request_id)
                
                await self._execute_callbacks("ai_rag_failure", request, None)
                logger.error(f"AI/RAG request failed: {request_id}")
            
        except Exception as e:
            logger.error(f"Failed to process AI/RAG request {request.request_id}: {e}")
            
            # Mark as failed
            request_id = request.request_id
            if request_id in self.pending_requests:
                self.pending_requests.remove(request_id)
            if request_id not in self.failed_requests:
                self.failed_requests.append(request_id)
    
    async def _send_ai_rag_request(self, request: AIRAGRequest) -> Optional[Dict[str, Any]]:
        """Send request to AI/RAG API"""
        for attempt in range(self.config.max_retry_attempts):
            try:
                # Prepare request payload
                payload = {
                    "request_type": request.request_type,
                    "input_data": request.input_data,
                    "parameters": request.parameters,
                    "user_id": request.user_id,
                    "org_id": request.org_id,
                    "priority": request.priority,
                    "metadata": request.metadata
                }
                
                # Prepare headers
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "TwinRegistryAIRAG/1.0"
                }
                
                if self.config.api_key:
                    headers["Authorization"] = f"Bearer {self.config.api_key}"
                
                # Send request
                async with self.http_session.post(
                    self.config.api_endpoint,
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        return response_data
                    else:
                        error_text = await response.text()
                        logger.warning(
                            f"AI/RAG API returned status {response.status}: {error_text}"
                        )
                        
            except asyncio.TimeoutError:
                logger.warning(f"AI/RAG request timeout (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"AI/RAG request error (attempt {attempt + 1}): {e}")
            
            # Wait before retry
            if attempt < self.config.max_retry_attempts - 1:
                await asyncio.sleep(self.config.retry_delay)
        
        return None
    
    def _get_cached_response(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get cached response if available and not expired"""
        if not self.config.enable_caching:
            return None
        
        if request_id in self.response_cache:
            cache_time = self.cache_timestamps.get(request_id, 0)
            current_time = datetime.now(timezone.utc).timestamp()
            
            if current_time - cache_time < self.config.cache_ttl:
                return self.response_cache[request_id]
            else:
                # Remove expired cache entry
                del self.response_cache[request_id]
                del self.cache_timestamps[request_id]
        
        return None
    
    def _cache_response(self, request_id: str, response: Dict[str, Any]) -> None:
        """Cache response data"""
        if not self.config.enable_caching:
            return
        
        self.response_cache[request_id] = response
        self.cache_timestamps[request_id] = datetime.now(timezone.utc).timestamp()
    
    async def _handle_cached_response(self, request: AIRAGRequest, cached_response: Dict[str, Any]) -> None:
        """Handle cached response"""
        try:
            # Create response object from cache
            ai_response = AIRAGResponse(
                request_id=request.request_id,
                response_data=cached_response,
                confidence_score=cached_response.get("confidence_score", 0.0),
                processing_time=0.0,  # No processing time for cached response
                timestamp=datetime.now(timezone.utc),
                status="completed_from_cache",
                metadata=cached_response.get("metadata", {})
            )
            
            # Store response
            self.responses[request.request_id] = ai_response
            
            # Update tracking
            if request.request_id not in self.completed_requests:
                self.completed_requests.append(request.request_id)
            
            # Trigger enhancement
            if self.config.enable_auto_enhancement:
                await self._trigger_registry_enhancement(request, ai_response)
            
            # Execute callbacks
            await self._execute_callbacks("ai_rag_completion", request, ai_response)
            
            logger.info(f"AI/RAG request completed from cache: {request.request_id}")
            
        except Exception as e:
            logger.error(f"Failed to handle cached response: {e}")
    
    async def _trigger_registry_enhancement(self, request: AIRAGRequest, response: AIRAGResponse) -> None:
        """Trigger twin registry enhancement using AI/RAG response"""
        try:
            start_time = datetime.now(timezone.utc)
            
            # Create system event for AI/RAG enhancement
            event = create_system_event(
                source="ai_rag_integration",
                event_type="ai_rag_enhancement",
                data={
                    "request_id": request.request_id,
                    "request_type": request.request_type,
                    "response_data": response.response_data,
                    "confidence_score": response.confidence_score,
                    "user_id": request.user_id,
                    "org_id": request.org_id
                },
                priority="high"
            )
            
            # Publish event
            await self.event_bus.publish(event)
            
            # Update statistics
            enhancement_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.stats["successful_enhancements"] += 1
            self.stats["last_enhancement_time"] = start_time
            
            # Update average enhancement time
            total_time = self.stats["average_enhancement_time"] * (self.stats["successful_enhancements"] - 1) + enhancement_time
            self.stats["average_enhancement_time"] = total_time / self.stats["successful_enhancements"]
            
            logger.info(f"Registry enhancement triggered for AI/RAG request: {request.request_id}")
            
        except Exception as e:
            logger.error(f"Failed to trigger registry enhancement: {e}")
            self.stats["failed_enhancements"] += 1
    
    async def _execute_callbacks(self, event_type: str, request: AIRAGRequest, response: Optional[AIRAGResponse]) -> None:
        """Execute registered callbacks"""
        try:
            for callback in self.registered_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event_type, request, response)
                    else:
                        callback(event_type, request, response)
                except Exception as e:
                    logger.error(f"Callback execution failed: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to execute callbacks: {e}")
    
    async def submit_request(
        self,
        request_type: str,
        input_data: Dict[str, Any],
        parameters: Dict[str, Any],
        user_id: str,
        org_id: str,
        priority: str = "normal",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Submit a new AI/RAG request"""
        try:
            import uuid
            
            request_id = str(uuid.uuid4())
            
            # Create request object
            request = AIRAGRequest(
                request_id=request_id,
                request_type=request_type,
                input_data=input_data,
                parameters=parameters,
                timestamp=datetime.now(timezone.utc),
                user_id=user_id,
                org_id=org_id,
                priority=priority,
                metadata=metadata or {}
            )
            
            # Add to queue
            try:
                self.request_queue.put_nowait(request)
                self.stats["total_requests"] += 1
                logger.info(f"AI/RAG request submitted: {request_id}")
                return request_id
            except asyncio.QueueFull:
                logger.error("AI/RAG request queue is full")
                raise RuntimeError("Request queue is full")
            
        except Exception as e:
            logger.error(f"Failed to submit AI/RAG request: {e}")
            raise
    
    async def get_request_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific AI/RAG request"""
        try:
            request = self.requests.get(request_id)
            response = self.responses.get(request_id)
            
            if not request:
                return None
            
            status_info = {
                "request_id": request_id,
                "request_type": request.request_type,
                "timestamp": request.timestamp.isoformat(),
                "user_id": request.user_id,
                "org_id": request.org_id,
                "priority": request.priority,
                "status": "unknown"
            }
            
            if request_id in self.pending_requests:
                status_info["status"] = "pending"
            elif request_id in self.completed_requests:
                status_info["status"] = "completed"
                if response:
                    status_info["response"] = {
                        "confidence_score": response.confidence_score,
                        "processing_time": response.processing_time,
                        "timestamp": response.timestamp.isoformat()
                    }
            elif request_id in self.failed_requests:
                status_info["status"] = "failed"
            
            return status_info
            
        except Exception as e:
            logger.error(f"Failed to get request status: {e}")
            return None
    
    def get_requests_summary(self) -> Dict[str, Any]:
        """Get summary of AI/RAG requests"""
        return {
            "total_requests": len(self.requests),
            "pending_requests": len(self.pending_requests),
            "completed_requests": len(self.completed_requests),
            "failed_requests": len(self.failed_requests),
            "queue_size": self.request_queue.qsize(),
            "cache_size": len(self.response_cache),
            "stats": self.stats.copy()
        }
    
    def register_callback(self, callback: Callable) -> None:
        """Register a callback for AI/RAG events"""
        if callback not in self.registered_callbacks:
            self.registered_callbacks.append(callback)
            logger.info("AI/RAG integration callback registered")
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a callback"""
        if callback in self.registered_callbacks:
            self.registered_callbacks.remove(callback)
            logger.info("AI/RAG integration callback unregistered")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of AI/RAG integration"""
        health_status = {
            "active": self.is_active,
            "processing_task_running": self.processing_task and not self.processing_task.done(),
            "queue_size": self.request_queue.qsize(),
            "queue_full": self.request_queue.full(),
            "total_requests": self.stats["total_requests"],
            "recent_enhancements": self.stats["successful_enhancements"],
            "failed_enhancements": self.stats["failed_enhancements"],
            "last_enhancement": self.stats["last_enhancement_time"].isoformat() if self.stats["last_enhancement_time"] else None,
            "average_enhancement_time": round(self.stats["average_enhancement_time"], 3),
            "cache_hits": self.stats["cache_hits"],
            "cache_misses": self.stats["cache_misses"],
            "registered_callbacks": len(self.registered_callbacks)
        }
        
        # Check API connectivity
        try:
            if self.http_session and not self.http_session.closed:
                async with self.http_session.get(self.config.api_endpoint + "/health") as response:
                    health_status["api_accessible"] = response.status == 200
                    health_status["api_status"] = response.status
            else:
                health_status["api_accessible"] = False
                health_status["api_status"] = "no_session"
        except Exception as e:
            health_status["api_accessible"] = False
            health_status["api_error"] = str(e)
        
        return health_status
    
    async def cleanup(self) -> None:
        """Cleanup AI/RAG integration resources"""
        try:
            await self.stop()
            
            # Clear tracking data
            self.requests.clear()
            self.responses.clear()
            self.pending_requests.clear()
            self.completed_requests.clear()
            self.failed_requests.clear()
            self.registered_callbacks.clear()
            
            # Clear cache
            self.response_cache.clear()
            self.cache_timestamps.clear()
            
            logger.info("AI/RAG integration cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during AI/RAG integration cleanup: {e}")
            raise
