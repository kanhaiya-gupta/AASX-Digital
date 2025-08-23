"""
Knowledge Graph Neo4j Webhook Manager

Manages webhook notifications to external systems for real-time updates.
Provides configurable webhook endpoints with retry logic and delivery tracking.
"""

import logging
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timezone
from dataclasses import dataclass, field
import json
import hashlib
import hmac

logger = logging.getLogger(__name__)


@dataclass
class WebhookEndpoint:
    """Webhook endpoint configuration."""
    
    url: str
    name: str
    secret: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    retry_count: int = 3
    retry_delay: float = 1.0
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        """Validate webhook endpoint configuration."""
        if not self.url:
            raise ValueError("Webhook URL is required")
        if not self.name:
            raise ValueError("Webhook name is required")
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        if self.retry_count < 0:
            raise ValueError("Retry count must be non-negative")


@dataclass
class WebhookDelivery:
    """Webhook delivery record."""
    
    webhook_id: str
    endpoint_url: str
    payload: Dict[str, Any]
    status: str = "pending"  # pending, sent, failed, retrying
    attempt_count: int = 0
    last_attempt: Optional[datetime] = None
    next_retry: Optional[datetime] = None
    error_message: Optional[str] = None
    response_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        """Generate webhook ID if not provided."""
        if not self.webhook_id:
            self.webhook_id = f"webhook_{int(self.created_at.timestamp())}_{hash(self.endpoint_url) % 10000}"


class WebhookManager:
    """Manages webhook notifications to external systems."""
    
    def __init__(self, max_concurrent_deliveries: int = 10):
        """Initialize the webhook manager."""
        self.endpoints: Dict[str, WebhookEndpoint] = {}
        self.deliveries: List[WebhookDelivery] = []
        self.max_concurrent_deliveries = max_concurrent_deliveries
        self.active_deliveries = 0
        self.delivery_semaphore = asyncio.Semaphore(max_concurrent_deliveries)
        
        # Statistics
        self.total_deliveries = 0
        self.successful_deliveries = 0
        self.failed_deliveries = 0
        self.retry_deliveries = 0
        
        # Event callbacks
        self.on_delivery_success: Optional[Callable[[WebhookDelivery], None]] = None
        self.on_delivery_failure: Optional[Callable[[WebhookDelivery], None]] = None
        
        logger.info("Webhook Manager initialized")
    
    def add_endpoint(self, endpoint: WebhookEndpoint) -> str:
        """Add a webhook endpoint."""
        try:
            # Validate endpoint
            if not endpoint.url.startswith(('http://', 'https://')):
                raise ValueError("Webhook URL must use HTTP or HTTPS protocol")
            
            # Generate endpoint ID
            endpoint_id = f"ep_{hash(endpoint.url) % 10000}"
            
            self.endpoints[endpoint_id] = endpoint
            logger.info(f"Webhook endpoint added: {endpoint.name} -> {endpoint.url}")
            
            return endpoint_id
            
        except Exception as e:
            logger.error(f"Failed to add webhook endpoint: {e}")
            raise
    
    def remove_endpoint(self, endpoint_id: str) -> bool:
        """Remove a webhook endpoint."""
        if endpoint_id in self.endpoints:
            endpoint = self.endpoints[endpoint_id]
            del self.endpoints[endpoint_id]
            logger.info(f"Webhook endpoint removed: {endpoint.name}")
            return True
        return False
    
    def get_endpoint(self, endpoint_id: str) -> Optional[WebhookEndpoint]:
        """Get a webhook endpoint by ID."""
        return self.endpoints.get(endpoint_id)
    
    def list_endpoints(self) -> List[Dict[str, Any]]:
        """List all webhook endpoints."""
        return [
            {
                "id": endpoint_id,
                "name": endpoint.name,
                "url": endpoint.url,
                "is_active": endpoint.is_active,
                "created_at": endpoint.created_at.isoformat()
            }
            for endpoint_id, endpoint in self.endpoints.items()
        ]
    
    async def send_webhook(
        self,
        endpoint_id: str,
        payload: Dict[str, Any],
        event_type: str = "notification"
    ) -> str:
        """Send a webhook to a specific endpoint."""
        try:
            if endpoint_id not in self.endpoints:
                raise ValueError(f"Webhook endpoint {endpoint_id} not found")
            
            endpoint = self.endpoints[endpoint_id]
            if not endpoint.is_active:
                raise ValueError(f"Webhook endpoint {endpoint.name} is not active")
            
            # Create delivery record
            delivery = WebhookDelivery(
                webhook_id=f"webhook_{event_type}_{int(datetime.now(timezone.utc).timestamp())}",
                endpoint_url=endpoint.url,
                payload=payload
            )
            
            self.deliveries.append(delivery)
            self.total_deliveries += 1
            
            # Schedule delivery
            asyncio.create_task(self._deliver_webhook(delivery, endpoint))
            
            logger.info(f"Webhook scheduled for delivery: {delivery.webhook_id} -> {endpoint.name}")
            return delivery.webhook_id
            
        except Exception as e:
            logger.error(f"Failed to schedule webhook: {e}")
            raise
    
    async def send_webhook_to_all(
        self,
        payload: Dict[str, Any],
        event_type: str = "notification"
    ) -> List[str]:
        """Send a webhook to all active endpoints."""
        delivery_ids = []
        
        for endpoint_id, endpoint in self.endpoints.items():
            if endpoint.is_active:
                try:
                    delivery_id = await self.send_webhook(endpoint_id, payload, event_type)
                    delivery_ids.append(delivery_id)
                except Exception as e:
                    logger.error(f"Failed to send webhook to {endpoint.name}: {e}")
        
        return delivery_ids
    
    async def _deliver_webhook(self, delivery: WebhookDelivery, endpoint: WebhookEndpoint) -> None:
        """Deliver a webhook to an endpoint."""
        async with self.delivery_semaphore:
            self.active_deliveries += 1
            
            try:
                await self._attempt_delivery(delivery, endpoint)
            finally:
                self.active_deliveries -= 1
    
    async def _attempt_delivery(self, delivery: WebhookDelivery, endpoint: WebhookEndpoint) -> None:
        """Attempt to deliver a webhook with retry logic."""
        delivery.attempt_count += 1
        delivery.last_attempt = datetime.now(timezone.utc)
        
        try:
            # Prepare payload
            payload_json = json.dumps(delivery.payload, default=str)
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "KG-Neo4j-Webhook/1.0",
                **endpoint.headers
            }
            
            # Add HMAC signature if secret is provided
            if endpoint.secret:
                signature = self._generate_hmac_signature(payload_json, endpoint.secret)
                headers["X-Webhook-Signature"] = signature
            
            # Send webhook
            start_time = datetime.now(timezone.utc)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint.url,
                    data=payload_json,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=endpoint.timeout)
                ) as response:
                    
                    response_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                    delivery.response_time_ms = response_time
                    delivery.response_code = response.status
                    
                    if 200 <= response.status < 300:
                        # Success
                        delivery.status = "sent"
                        self.successful_deliveries += 1
                        
                        logger.info(f"Webhook {delivery.webhook_id} delivered successfully to {endpoint.name}")
                        
                        # Trigger success callback
                        if self.on_delivery_success:
                            self.on_delivery_success(delivery)
                    
                    else:
                        # HTTP error
                        error_msg = f"HTTP {response.status}: {response.reason}"
                        await self._handle_delivery_failure(delivery, endpoint, error_msg)
            
        except asyncio.TimeoutError:
            error_msg = f"Timeout after {endpoint.timeout}s"
            await self._handle_delivery_failure(delivery, endpoint, error_msg)
            
        except Exception as e:
            error_msg = str(e)
            await self._handle_delivery_failure(delivery, endpoint, error_msg)
    
    async def _handle_delivery_failure(self, delivery: WebhookDelivery, endpoint: WebhookEndpoint, error_msg: str) -> None:
        """Handle webhook delivery failure."""
        delivery.error_message = error_msg
        
        if delivery.attempt_count < endpoint.retry_count:
            # Schedule retry
            delivery.status = "retrying"
            retry_delay = endpoint.retry_delay * (2 ** (delivery.attempt_count - 1))  # Exponential backoff
            delivery.next_retry = datetime.now(timezone.utc) + asyncio.get_event_loop().time() + retry_delay
            
            self.retry_deliveries += 1
            
            logger.warning(f"Webhook {delivery.webhook_id} failed, retrying in {retry_delay:.1f}s: {error_msg}")
            
            # Schedule retry
            asyncio.create_task(self._schedule_retry(delivery, endpoint, retry_delay))
            
        else:
            # Max retries exceeded
            delivery.status = "failed"
            self.failed_deliveries += 1
            
            logger.error(f"Webhook {delivery.webhook_id} failed after {delivery.attempt_count} attempts: {error_msg}")
            
            # Trigger failure callback
            if self.on_delivery_failure:
                self.on_delivery_failure(delivery)
    
    async def _schedule_retry(self, delivery: WebhookDelivery, endpoint: WebhookEndpoint, delay: float) -> None:
        """Schedule a retry for a failed webhook."""
        await asyncio.sleep(delay)
        
        # Check if delivery is still in retrying status
        if delivery.status == "retrying":
            await self._attempt_delivery(delivery, endpoint)
    
    def _generate_hmac_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC-SHA256 signature for payload verification."""
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    # Management Methods
    
    def get_delivery_status(self, webhook_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a webhook delivery."""
        for delivery in self.deliveries:
            if delivery.webhook_id == webhook_id:
                return {
                    "webhook_id": delivery.webhook_id,
                    "endpoint_url": delivery.endpoint_url,
                    "status": delivery.status,
                    "attempt_count": delivery.attempt_count,
                    "last_attempt": delivery.last_attempt.isoformat() if delivery.last_attempt else None,
                    "next_retry": delivery.next_retry.isoformat() if delivery.next_retry else None,
                    "error_message": delivery.error_message,
                    "response_code": delivery.response_code,
                    "response_time_ms": delivery.response_time_ms,
                    "created_at": delivery.created_at.isoformat()
                }
        return None
    
    def get_recent_deliveries(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent webhook deliveries."""
        recent_deliveries = self.deliveries[-limit:] if limit > 0 else self.deliveries
        
        return [
            {
                "webhook_id": delivery.webhook_id,
                "endpoint_url": delivery.endpoint_url,
                "status": delivery.status,
                "attempt_count": delivery.attempt_count,
                "created_at": delivery.created_at.isoformat()
            }
            for delivery in recent_deliveries
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get webhook manager statistics."""
        return {
            "total_deliveries": self.total_deliveries,
            "successful_deliveries": self.successful_deliveries,
            "failed_deliveries": self.failed_deliveries,
            "retry_deliveries": self.retry_deliveries,
            "active_deliveries": self.active_deliveries,
            "endpoint_count": len(self.endpoints),
            "delivery_history_size": len(self.deliveries),
            "success_rate": (self.successful_deliveries / max(self.total_deliveries, 1)) * 100
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the webhook manager."""
        try:
            # Check if endpoints are accessible
            endpoint_health = {}
            for endpoint_id, endpoint in self.endpoints.items():
                if endpoint.is_active:
                    try:
                        # Simple connectivity check
                        async with aiohttp.ClientSession() as session:
                            async with session.head(endpoint.url, timeout=5) as response:
                                endpoint_health[endpoint_id] = {
                                    "status": "healthy" if response.status < 500 else "unhealthy",
                                    "response_code": response.status,
                                    "name": endpoint.name
                                }
                    except Exception as e:
                        endpoint_health[endpoint_id] = {
                            "status": "unhealthy",
                            "error": str(e),
                            "name": endpoint.name
                        }
            
            # Overall health
            healthy_endpoints = sum(1 for health in endpoint_health.values() if health["status"] == "healthy")
            total_endpoints = len(endpoint_health)
            overall_healthy = total_endpoints > 0 and healthy_endpoints == total_endpoints
            
            return {
                "status": "healthy" if overall_healthy else "unhealthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "endpoints": endpoint_health,
                "overall_health": overall_healthy,
                "healthy_endpoints": healthy_endpoints,
                "total_endpoints": total_endpoints
            }
            
        except Exception as e:
            logger.error(f"Webhook manager health check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def clear_delivery_history(self, older_than_days: int = 30) -> int:
        """Clear old delivery history."""
        cutoff_date = datetime.now(timezone.utc) - asyncio.get_event_loop().time() - (older_than_days * 24 * 3600)
        
        original_count = len(self.deliveries)
        self.deliveries = [
            delivery for delivery in self.deliveries
            if delivery.created_at > cutoff_date
        ]
        
        cleared_count = original_count - len(self.deliveries)
        logger.info(f"Cleared {cleared_count} old webhook deliveries")
        
        return cleared_count
    
    def set_delivery_callbacks(
        self,
        on_success: Optional[Callable[[WebhookDelivery], None]] = None,
        on_failure: Optional[Callable[[WebhookDelivery], None]] = None
    ) -> None:
        """Set delivery event callbacks."""
        self.on_delivery_success = on_success
        self.on_delivery_failure = on_failure
        
        logger.info("Webhook delivery callbacks configured")
