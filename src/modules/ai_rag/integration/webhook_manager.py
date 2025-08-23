"""
Webhook Manager for AI RAG

This module handles external notifications and webhook delivery:
- External notifications
- Webhook delivery tracking
- Security validation
- Delivery monitoring
"""

import asyncio
import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse

import aiohttp
from pydantic import BaseModel, Field, validator

from ..events.event_types import (
    BaseEvent, EventPriority, EventStatus, EventCategory,
    WebhookEvent, IntegrationEvent
)
from ..events.event_bus import EventBus


class WebhookStatus(str, Enum):
    """Webhook delivery status"""
    PENDING = "pending"
    SENDING = "sending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    EXPIRED = "expired"


class WebhookPriority(str, Enum):
    """Webhook priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class WebhookSecurityType(str, Enum):
    """Webhook security types"""
    NONE = "none"
    HMAC_SHA256 = "hmac_sha256"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    JWT = "jwt"


@dataclass
class WebhookDeliveryAttempt:
    """Webhook delivery attempt record"""
    attempt_number: int
    timestamp: datetime
    status_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    response_time_ms: float = 0.0


class WebhookConfig(BaseModel):
    """Configuration for webhook endpoints"""
    url: str
    name: str
    description: Optional[str] = None
    enabled: bool = True
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: int = 5
    max_retry_delay_seconds: int = 300
    security_type: WebhookSecurityType = WebhookSecurityType.NONE
    secret_key: Optional[str] = None
    api_key: Optional[str] = None
    headers: Dict[str, str] = Field(default_factory=dict)
    priority: WebhookPriority = WebhookPriority.NORMAL
    
    @validator('url')
    def validate_url(cls, v):
        """Validate webhook URL"""
        try:
            result = urlparse(v)
            if not all([result.scheme, result.netloc]):
                raise ValueError("Invalid URL format")
            return v
        except Exception:
            raise ValueError("Invalid URL format")


class WebhookPayload(BaseModel):
    """Webhook payload structure"""
    event_type: str
    event_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    source: str = "ai_rag"
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def to_json(self) -> str:
        """Convert payload to JSON string"""
        return self.json(exclude_none=True)


class WebhookDelivery(BaseModel):
    """Webhook delivery record"""
    webhook_id: str
    payload: WebhookPayload
    status: WebhookStatus = WebhookStatus.PENDING
    priority: WebhookPriority
    created_at: datetime = Field(default_factory=datetime.now)
    scheduled_for: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    attempts: List[WebhookDeliveryAttempt] = Field(default_factory=list)
    max_attempts: int = 3
    retry_until: Optional[datetime] = None
    
    class Config:
        arbitrary_types_allowed = True


class WebhookSecurityValidator:
    """Validates webhook security and signatures"""
    
    @staticmethod
    def validate_hmac_signature(
        payload: str, 
        signature: str, 
        secret_key: str
    ) -> bool:
        """Validate HMAC-SHA256 signature"""
        try:
            expected_signature = hmac.new(
                secret_key.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception:
            return False
    
    @staticmethod
    def validate_api_key(
        provided_key: str, 
        expected_key: str
    ) -> bool:
        """Validate API key"""
        return hmac.compare_digest(provided_key, expected_key)
    
    @staticmethod
    def generate_hmac_signature(
        payload: str, 
        secret_key: str
    ) -> str:
        """Generate HMAC-SHA256 signature"""
        return hmac.new(
            secret_key.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()


class WebhookDeliveryManager:
    """Manages webhook delivery and retry logic"""
    
    def __init__(self, config: WebhookConfig, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        self.delivery_queue: asyncio.Queue = asyncio.Queue()
        self.active_deliveries: Dict[str, WebhookDelivery] = {}
        self.delivery_stats = {
            "total_sent": 0,
            "total_delivered": 0,
            "total_failed": 0,
            "total_retries": 0
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
    
    async def queue_webhook(
        self, 
        payload: WebhookPayload, 
        priority: Optional[WebhookPriority] = None,
        scheduled_for: Optional[datetime] = None
    ) -> str:
        """Queue a webhook for delivery"""
        webhook_id = f"webhook_{datetime.now().timestamp()}_{hash(payload.event_id)}"
        
        delivery = WebhookDelivery(
            webhook_id=webhook_id,
            payload=payload,
            priority=priority or self.config.priority,
            scheduled_for=scheduled_for
        )
        
        # Add to delivery queue
        await self.delivery_queue.put((delivery.priority, delivery))
        self.active_deliveries[webhook_id] = delivery
        
        # Publish webhook event
        event = WebhookEvent(
            event_id=f"webhook_queued_{webhook_id}",
            webhook_id=webhook_id,
            webhook_url=self.config.url,
            webhook_name=self.config.name,
            payload_event_type=payload.event_type,
            payload_event_id=payload.event_id,
            priority=EventPriority.LOW,
            category=EventCategory.INTEGRATION
        )
        await self.event_bus.publish(event)
        
        self.logger.info(f"Queued webhook {webhook_id} for {self.config.url}")
        return webhook_id
    
    async def deliver_webhook(self, delivery: WebhookDelivery) -> bool:
        """Attempt to deliver a webhook"""
        if delivery.status == WebhookStatus.DELIVERED:
            return True
        
        if len(delivery.attempts) >= delivery.max_attempts:
            delivery.status = WebhookStatus.EXPIRED
            self.delivery_stats["total_failed"] += 1
            return False
        
        # Check if it's time to retry
        if delivery.status == WebhookStatus.RETRYING:
            last_attempt = delivery.attempts[-1] if delivery.attempts else None
            if last_attempt:
                retry_delay = min(
                    self.config.retry_delay_seconds * (2 ** len(delivery.attempts)),
                    self.config.max_retry_delay_seconds
                )
                if (datetime.now() - last_attempt.timestamp).total_seconds() < retry_delay:
                    return False
        
        delivery.status = WebhookStatus.SENDING
        attempt_number = len(delivery.attempts) + 1
        start_time = time.time()
        
        try:
            # Prepare headers
            headers = self.config.headers.copy()
            
            # Add security headers
            if self.config.security_type == WebhookSecurityType.HMAC_SHA256 and self.config.secret_key:
                payload_json = delivery.payload.to_json()
                signature = WebhookSecurityValidator.generate_hmac_signature(
                    payload_json, 
                    self.config.secret_key
                )
                headers["X-Webhook-Signature"] = f"sha256={signature}"
            
            elif self.config.security_type == WebhookSecurityType.API_KEY and self.config.api_key:
                headers["X-API-Key"] = self.config.api_key
            
            # Add content type
            headers["Content-Type"] = "application/json"
            
            # Make HTTP request
            async with self.session.post(
                self.config.url,
                json=delivery.payload.dict(),
                headers=headers
            ) as response:
                response_time = (time.time() - start_time) * 1000
                response_body = await response.text()
                
                # Record attempt
                attempt = WebhookDeliveryAttempt(
                    attempt_number=attempt_number,
                    timestamp=datetime.now(),
                    status_code=response.status,
                    response_body=response_body,
                    response_time_ms=response_time
                )
                delivery.attempts.append(attempt)
                
                if response.status == 200:
                    delivery.status = WebhookStatus.DELIVERED
                    delivery.delivered_at = datetime.now()
                    self.delivery_stats["total_delivered"] += 1
                    
                    # Publish success event
                    success_event = WebhookEvent(
                        event_id=f"webhook_delivered_{delivery.webhook_id}",
                        webhook_id=delivery.webhook_id,
                        webhook_url=self.config.url,
                        webhook_name=self.config.name,
                        payload_event_type=delivery.payload.event_type,
                        payload_event_id=delivery.payload.event_id,
                        delivery_status="success",
                        attempt_count=attempt_number,
                        response_time_ms=response_time,
                        priority=EventPriority.LOW,
                        category=EventCategory.INTEGRATION
                    )
                    await self.event_bus.publish(success_event)
                    
                    return True
                else:
                    delivery.status = WebhookStatus.FAILED
                    attempt.error_message = f"HTTP {response.status}: {response_body}"
                    
                    # Publish failure event
                    failure_event = WebhookEvent(
                        event_id=f"webhook_failed_{delivery.webhook_id}",
                        webhook_id=delivery.webhook_id,
                        webhook_url=self.config.url,
                        webhook_name=self.config.name,
                        payload_event_type=delivery.payload.event_type,
                        payload_event_id=delivery.payload.event_id,
                        delivery_status="failed",
                        attempt_count=attempt_number,
                        error_message=attempt.error_message,
                        response_time_ms=response_time,
                        priority=EventPriority.NORMAL,
                        category=EventCategory.ERROR
                    )
                    await self.event_bus.publish(failure_event)
                    
                    return False
                    
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            # Record attempt
            attempt = WebhookDeliveryAttempt(
                attempt_number=attempt_number,
                timestamp=datetime.now(),
                error_message=str(e),
                response_time_ms=response_time
            )
            delivery.attempts.append(attempt)
            
            delivery.status = WebhookStatus.FAILED
            
            # Publish error event
            error_event = WebhookEvent(
                event_id=f"webhook_error_{delivery.webhook_id}",
                webhook_id=delivery.webhook_id,
                webhook_url=self.config.url,
                webhook_name=self.config.name,
                payload_event_type=delivery.payload.event_type,
                payload_event_id=delivery.payload.event_id,
                delivery_status="error",
                attempt_count=attempt_number,
                error_message=str(e),
                response_time_ms=response_time,
                priority=EventPriority.NORMAL,
                category=EventCategory.ERROR
            )
            await self.event_bus.publish(error_event)
            
            return False
    
    async def retry_failed_webhooks(self):
        """Retry failed webhooks"""
        for webhook_id, delivery in self.active_deliveries.items():
            if delivery.status == WebhookStatus.FAILED:
                if len(delivery.attempts) < delivery.max_attempts:
                    delivery.status = WebhookStatus.RETRYING
                    await self.delivery_queue.put((delivery.priority, delivery))
                    self.delivery_stats["total_retries"] += 1
                else:
                    delivery.status = WebhookStatus.EXPIRED
    
    async def process_delivery_queue(self):
        """Process the webhook delivery queue"""
        while True:
            try:
                # Get next webhook from queue
                priority, delivery = await self.delivery_queue.get()
                
                # Check if scheduled for future
                if delivery.scheduled_for and delivery.scheduled_for > datetime.now():
                    # Re-queue for later
                    await asyncio.sleep(1)
                    await self.delivery_queue.put((priority, delivery))
                    continue
                
                # Attempt delivery
                success = await self.deliver_webhook(delivery)
                
                if success:
                    self.delivery_stats["total_sent"] += 1
                    # Remove from active deliveries
                    self.active_deliveries.pop(delivery.webhook_id, None)
                else:
                    # Will be retried by retry_failed_webhooks
                    pass
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error processing delivery queue: {e}")
                await asyncio.sleep(1)
    
    async def get_delivery_status(self, webhook_id: str) -> Optional[WebhookDelivery]:
        """Get status of a specific webhook delivery"""
        return self.active_deliveries.get(webhook_id)
    
    async def get_delivery_stats(self) -> Dict[str, Any]:
        """Get webhook delivery statistics"""
        return {
            **self.delivery_stats,
            "active_deliveries": len(self.active_deliveries),
            "queue_size": self.delivery_queue.qsize(),
            "config": {
                "url": self.config.url,
                "name": self.config.name,
                "enabled": self.config.enabled,
                "max_retries": self.config.max_retries
            }
        }


class WebhookManager:
    """Centralized webhook management system"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        self.webhook_configs: Dict[str, WebhookConfig] = {}
        self.delivery_managers: Dict[str, WebhookDeliveryManager] = {}
        self.running = False
        self.delivery_task: Optional[asyncio.Task] = None
        self.retry_task: Optional[asyncio.Task] = None
    
    def register_webhook(self, config: WebhookConfig) -> str:
        """Register a new webhook configuration"""
        webhook_id = f"webhook_{config.name}_{len(self.webhook_configs)}"
        
        self.webhook_configs[webhook_id] = config
        self.delivery_managers[webhook_id] = WebhookDeliveryManager(config, self.event_bus)
        
        self.logger.info(f"Registered webhook: {config.name} -> {config.url}")
        return webhook_id
    
    async def start(self):
        """Start the webhook manager"""
        if self.running:
            return
        
        self.running = True
        
        # Start delivery managers
        for webhook_id, manager in self.delivery_managers.items():
            await manager.__aenter__()
        
        # Start background tasks
        self.delivery_task = asyncio.create_task(self._run_delivery_managers())
        self.retry_task = asyncio.create_task(self._run_retry_loop())
        
        self.logger.info("Webhook manager started")
    
    async def stop(self):
        """Stop the webhook manager"""
        if not self.running:
            return
        
        self.running = False
        
        # Cancel background tasks
        if self.delivery_task:
            self.delivery_task.cancel()
            try:
                await self.delivery_task
            except asyncio.CancelledError:
                pass
        
        if self.retry_task:
            self.retry_task.cancel()
            try:
                await self.retry_task
            except asyncio.CancelledError:
                pass
        
        # Stop delivery managers
        for webhook_id, manager in self.delivery_managers.items():
            await manager.__aexit__(None, None, None)
        
        self.logger.info("Webhook manager stopped")
    
    async def _run_delivery_managers(self):
        """Run all delivery managers concurrently"""
        tasks = []
        for manager in self.delivery_managers.values():
            tasks.append(manager.process_delivery_queue())
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _run_retry_loop(self):
        """Run retry loop for failed webhooks"""
        while self.running:
            try:
                for manager in self.delivery_managers.values():
                    await manager.retry_failed_webhooks()
                
                await asyncio.sleep(10)  # Check every 10 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in retry loop: {e}")
                await asyncio.sleep(10)
    
    async def send_webhook(
        self, 
        webhook_name: str, 
        payload: WebhookPayload,
        priority: Optional[WebhookPriority] = None,
        scheduled_for: Optional[datetime] = None
    ) -> Optional[str]:
        """Send a webhook to a specific endpoint"""
        # Find webhook by name
        webhook_id = None
        for wid, config in self.webhook_configs.items():
            if config.name == webhook_name and config.enabled:
                webhook_id = wid
                break
        
        if not webhook_id:
            self.logger.warning(f"Webhook '{webhook_name}' not found or disabled")
            return None
        
        # Queue for delivery
        manager = self.delivery_managers[webhook_id]
        return await manager.queue_webhook(payload, priority, scheduled_for)
    
    async def get_webhook_status(self, webhook_name: str) -> Dict[str, Any]:
        """Get status of all webhooks with a specific name"""
        status = {}
        
        for webhook_id, config in self.webhook_configs.items():
            if config.name == webhook_name:
                manager = self.delivery_managers[webhook_id]
                stats = await manager.get_delivery_stats()
                status[webhook_id] = {
                    "config": config.dict(),
                    "stats": stats
                }
        
        return status
    
    async def get_all_webhook_status(self) -> Dict[str, Any]:
        """Get status of all webhooks"""
        status = {}
        
        for webhook_id, config in self.webhook_configs.items():
            manager = self.delivery_managers[webhook_id]
            stats = await manager.get_delivery_stats()
            status[webhook_id] = {
                "config": config.dict(),
                "stats": stats
            }
        
        return status
    
    async def health_check(self) -> Dict[str, bool]:
        """Perform health check on all webhooks"""
        health_status = {}
        
        for webhook_id, manager in self.delivery_managers.items():
            try:
                # Simple health check based on manager state
                health_status[webhook_id] = manager.session is not None
            except Exception as e:
                self.logger.error(f"Health check failed for {webhook_id}: {e}")
                health_status[webhook_id] = False
        
        return health_status
