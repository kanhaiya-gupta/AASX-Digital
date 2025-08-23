"""
AI/RAG Integration for Twin Registry Population
Provides hooks and integration points with AI/RAG systems for enhanced population
Phase 3: Event System & Automation with pure async support
"""

import logging
import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List, Union, Callable
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass

from ..events.event_manager import TwinRegistryEventManager, EventType, EventPriority, TwinRegistryEvent
from ..core.twin_registry_service import TwinRegistryService

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
    dept_id: Optional[str] = None
    project_id: Optional[str] = None
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
    """AI/RAG system integration for enhanced twin registry population - Pure async implementation"""
    
    def __init__(
        self,
        twin_service: TwinRegistryService,
        event_manager: TwinRegistryEventManager,
        config: AIRAGIntegrationConfig
    ):
        self.twin_service = twin_service
        self.event_manager = event_manager
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
        
        # Statistics
        self.stats = {
            "total_requests_processed": 0,
            "successful_enhancements": 0,
            "failed_enhancements": 0,
            "last_enhancement_time": None,
            "average_processing_time": 0.0,
            "total_confidence_score": 0.0
        }
    
    async def start(self) -> None:
        """Start AI/RAG integration processing"""
        try:
            if self.is_active:
                logger.warning("AI/RAG integration is already active")
                return
            
            self.is_active = True
            
            # Start processing task
            self.processing_task = asyncio.create_task(self._process_requests())
            
            logger.info("AI/RAG integration started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start AI/RAG integration: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop AI/RAG integration processing"""
        try:
            if not self.is_active:
                return
            
            self.is_active = False
            
            if self.processing_task:
                self.processing_task.cancel()
                try:
                    await self.processing_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("AI/RAG integration stopped successfully")
            
        except Exception as e:
            logger.error(f"Failed to stop AI/RAG integration: {e}")
            raise
    
    async def submit_request(self, request: AIRAGRequest) -> None:
        """Submit an AI/RAG request for processing"""
        try:
            # Add to tracking
            self.requests[request.request_id] = request
            self.pending_requests.append(request.request_id)
            
            # Add to processing queue
            await self.request_queue.put(request)
            
            logger.info(f"Submitted AI/RAG request: {request.request_id}")
            
        except Exception as e:
            logger.error(f"Failed to submit AI/RAG request {request.request_id}: {e}")
            raise
    
    async def _process_requests(self) -> None:
        """Process AI/RAG requests from the queue"""
        while self.is_active:
            try:
                # Get request from queue
                try:
                    request = await asyncio.wait_for(self.request_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # Process the request
                async with self.semaphore:
                    await self._process_single_request(request)
                
                # Mark task as done
                self.request_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in AI/RAG request processing: {e}")
                await asyncio.sleep(self.config.retry_delay)
    
    async def _process_single_request(self, request: AIRAGRequest) -> None:
        """Process a single AI/RAG request"""
        try:
            start_time = datetime.now(timezone.utc)
            
            # Make API call to AI/RAG system
            response = await self._call_ai_rag_api(request)
            
            # Calculate processing time
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            # Create response object
            ai_response = AIRAGResponse(
                request_id=request.request_id,
                response_data=response.get("data", {}),
                confidence_score=response.get("confidence", 0.0),
                processing_time=processing_time,
                timestamp=datetime.now(timezone.utc),
                status="completed",
                metadata=response.get("metadata", {})
            )
            
            # Store response
            self.responses[request.request_id] = ai_response
            
            # Update tracking
            if request.request_id in self.pending_requests:
                self.pending_requests.remove(request.request_id)
            self.completed_requests.append(request.request_id)
            
            # Update statistics
            self.stats["total_requests_processed"] += 1
            self.stats["successful_enhancements"] += 1
            self.stats["last_enhancement_time"] = datetime.now(timezone.utc)
            self.stats["total_confidence_score"] += ai_response.confidence_score
            
            # Calculate average processing time
            total_time = self.stats["average_processing_time"] * (self.stats["total_requests_processed"] - 1) + processing_time
            self.stats["average_processing_time"] = total_time / self.stats["total_requests_processed"]
            
            # Trigger enhancement event for automatic twin updates
            await self._trigger_enhancement_event(request, ai_response)
            
            logger.info(f"Processed AI/RAG request {request.request_id} successfully")
            
        except Exception as e:
            logger.error(f"Failed to process AI/RAG request {request.request_id}: {e}")
            
            # Mark as failed
            if request.request_id in self.pending_requests:
                self.pending_requests.remove(request.request_id)
            self.failed_requests.append(request.request_id)
            
            # Update statistics
            self.stats["failed_enhancements"] += 1
    
    async def _call_ai_rag_api(self, request: AIRAGRequest) -> Dict[str, Any]:
        """Make API call to AI/RAG system"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Content-Type": "application/json"}
                if self.config.api_key:
                    headers["Authorization"] = f"Bearer {self.config.api_key}"
                
                payload = {
                    "request_type": request.request_type,
                    "input_data": request.input_data,
                    "parameters": request.parameters,
                    "user_id": request.user_id,
                    "org_id": request.org_id
                }
                
                async with session.post(
                    self.config.api_endpoint,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"API call failed with status {response.status}: {error_text}")
                        
        except Exception as e:
            logger.error(f"AI/RAG API call failed: {e}")
            raise
    
    async def _trigger_enhancement_event(self, request: AIRAGRequest, response: AIRAGResponse) -> None:
        """Trigger enhancement event for automatic twin updates"""
        try:
            # Create twin ID from request
            twin_id = f"ai_rag_{request.request_id}"
            
            # Trigger the event using the event manager
            await self.event_manager.emit_event(
                TwinRegistryEvent(
                    event_type=EventType.TWIN_UPDATED,
                    priority=EventPriority.NORMAL,
                    timestamp=datetime.now(),
                    data={
                        'twin_id': twin_id,
                        'request_id': request.request_id,
                        'enhancement_type': request.request_type,
                        'confidence_score': response.confidence_score,
                        'processing_time': response.processing_time,
                        'enhancement_data': response.response_data,
                        'user_id': request.user_id,
                        'org_id': request.org_id,
                        'dept_id': request.dept_id,
                        'project_id': request.project_id
                    },
                    source="ai_rag_integration",
                    correlation_id=request.request_id
                )
            )
            
            logger.info(f"Triggered enhancement event for request {request.request_id}")
            
        except Exception as e:
            logger.error(f"Failed to trigger enhancement event for request {request.request_id}: {e}")
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get the current status of the AI/RAG integration"""
        try:
            return {
                "is_active": self.is_active,
                "total_requests_processed": self.stats["total_requests_processed"],
                "pending_requests": len(self.pending_requests),
                "completed_requests": len(self.completed_requests),
                "failed_requests": len(self.failed_requests),
                "last_enhancement_time": self.stats["last_enhancement_time"],
                "average_processing_time": self.stats["average_processing_time"],
                "average_confidence_score": (
                    self.stats["total_confidence_score"] / self.stats["total_requests_processed"]
                    if self.stats["total_requests_processed"] > 0 else 0.0
                ),
                "queue_size": self.request_queue.qsize()
            }
        except Exception as e:
            logger.error(f"Failed to get AI/RAG integration status: {e}")
            return {"error": str(e)}


class RAGProcessor:
    """Processes AI/RAG requests and triggers events"""
    
    def __init__(self, event_manager: TwinRegistryEventManager):
        self.event_manager = event_manager
    
    async def process_rag_request(self, request: AIRAGRequest, response: AIRAGResponse) -> None:
        """Process an AI/RAG request and trigger the appropriate event"""
        try:
            # Create twin ID from request
            twin_id = f"ai_rag_{request.request_id}"
            
            # Trigger twin updated event
            await self.event_manager.emit_event(
                TwinRegistryEvent(
                    event_type=EventType.TWIN_UPDATED,
                    priority=EventPriority.NORMAL,
                    timestamp=datetime.now(),
                    data={
                        'twin_id': twin_id,
                        'request_id': request.request_id,
                        'enhancement_type': request.request_type,
                        'confidence_score': response.confidence_score,
                        'processing_time': response.processing_time,
                        'enhancement_data': response.response_data,
                        'user_id': request.user_id,
                        'org_id': request.org_id,
                        'dept_id': request.dept_id,
                        'project_id': request.project_id
                    },
                    source="rag_processor",
                    correlation_id=request.request_id
                )
            )
            
            logger.info(f"Processed AI/RAG request: {request.request_id}")
            
        except Exception as e:
            logger.error(f"Failed to process AI/RAG request {request.request_id}: {e}")


class RAGValidator:
    """Validates AI/RAG request and response data"""
    
    @staticmethod
    async def validate_request(request: AIRAGRequest) -> bool:
        """Validate AI/RAG request information"""
        try:
            if not request.request_id:
                return False
            
            if not request.request_type:
                return False
            
            if not request.input_data:
                return False
            
            if not request.user_id:
                return False
            
            if not request.org_id:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate AI/RAG request: {e}")
            return False
    
    @staticmethod
    async def validate_response(response: AIRAGResponse) -> bool:
        """Validate AI/RAG response information"""
        try:
            if not response.request_id:
                return False
            
            if not response.response_data:
                return False
            
            if response.confidence_score < 0.0 or response.confidence_score > 1.0:
                return False
            
            if response.processing_time < 0.0:
                return False
            
            if not response.status:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate AI/RAG response: {e}")
            return False


class RAGMetricsCollector:
    """Collects and processes AI/RAG metrics"""
    
    def __init__(self, twin_service: TwinRegistryService):
        self.twin_service = twin_service
    
    async def collect_rag_metrics(self, request: AIRAGRequest, response: AIRAGResponse) -> Dict[str, Any]:
        """Collect AI/RAG metrics for analysis"""
        try:
            metrics = {
                "request_id": request.request_id,
                "timestamp": datetime.now().isoformat(),
                "request_type": request.request_type,
                "processing_time": response.processing_time,
                "confidence_score": response.confidence_score,
                "status": response.status,
                "user_id": request.user_id,
                "org_id": request.org_id,
                "dept_id": request.dept_id,
                "project_id": request.project_id
            }
            
            logger.info(f"Collected AI/RAG metrics for request {request.request_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect AI/RAG metrics for request {request.request_id}: {e}")
            return {}
