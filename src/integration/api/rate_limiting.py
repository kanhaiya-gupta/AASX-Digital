"""
Rate Limiting Service

This module provides advanced rate limiting capabilities for the API layer,
including multiple algorithms, configurable limits, and monitoring.

The rate limiting service supports:
- Token bucket algorithm
- Fixed window algorithm
- Sliding window algorithm
- Per-user and per-IP rate limiting
- Dynamic rate limit adjustment
- Rate limit monitoring and analytics
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple
from collections import defaultdict, deque
import json


logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Advanced rate limiter with multiple algorithms and monitoring.
    
    Supports different rate limiting strategies:
    - Token bucket (smooth, burst-friendly)
    - Fixed window (simple, predictable)
    - Sliding window (accurate, memory-efficient)
    """
    
    def __init__(self, default_algorithm: str = "token_bucket"):
        """Initialize the rate limiter."""
        self.default_algorithm = default_algorithm
        self.limiters: Dict[str, Any] = {}
        self.global_config = {
            "default_limit": 100,
            "default_window": 60,
            "max_burst": 200,
            "enabled": True
        }
        
        # Monitoring and analytics
        self.rate_limit_events: deque = deque(maxlen=10000)
        self.blocked_requests = 0
        self.total_requests = 0
        
        logger.info(f"Rate limiter initialized with algorithm: {default_algorithm}")
    
    def create_limiter(
        self,
        client_id: str,
        algorithm: str = None,
        limit: int = None,
        window_seconds: int = None,
        **kwargs
    ) -> bool:
        """Create a new rate limiter for a client."""
        try:
            algo = algorithm or self.default_algorithm
            limit_val = limit or self.global_config["default_limit"]
            window = window_seconds or self.global_config["default_window"]
            
            if algo == "token_bucket":
                limiter = TokenBucketLimiter(limit_val, window, **kwargs)
            elif algo == "fixed_window":
                limiter = FixedWindowLimiter(limit_val, window)
            elif algo == "sliding_window":
                limiter = SlidingWindowLimiter(limit_val, window)
            else:
                logger.error(f"Unknown rate limiting algorithm: {algo}")
                return False
            
            self.limiters[client_id] = {
                "limiter": limiter,
                "algorithm": algo,
                "config": {
                    "limit": limit_val,
                    "window_seconds": window,
                    **kwargs
                },
                "created_at": datetime.utcnow(),
                "last_used": datetime.utcnow()
            }
            
            logger.info(f"Rate limiter created for {client_id}: {algo} ({limit_val}/{window}s)")
            return True
            
        except Exception as e:
            logger.error(f"Error creating rate limiter for {client_id}: {e}")
            return False
    
    async def check_rate_limit(self, client_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Check if a client is within rate limits."""
        if not self.global_config["enabled"]:
            return True, {"status": "rate_limiting_disabled"}
        
        self.total_requests += 1
        
        try:
            # Create limiter if it doesn't exist
            if client_id not in self.limiters:
                self.create_limiter(client_id)
            
            limiter_info = self.limiters[client_id]
            limiter = limiter_info["limiter"]
            
            # Check rate limit
            allowed, details = await limiter.check_limit()
            
            # Update last used timestamp
            limiter_info["last_used"] = datetime.utcnow()
            
            # Record event
            self._record_event(client_id, allowed, details)
            
            if not allowed:
                self.blocked_requests += 1
            
            return allowed, details
            
        except Exception as e:
            logger.error(f"Rate limit check error for {client_id}: {e}")
            # Allow request on error (fail open)
            return True, {"status": "error", "message": str(e)}
    
    def _record_event(self, client_id: str, allowed: bool, details: Dict[str, Any]) -> None:
        """Record a rate limiting event for monitoring."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "client_id": client_id,
            "allowed": allowed,
            "details": details
        }
        
        self.rate_limit_events.append(event)
    
    def get_limiter_status(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a rate limiter."""
        if client_id not in self.limiters:
            return None
        
        limiter_info = self.limiters[client_id]
        limiter = limiter_info["limiter"]
        
        return {
            "client_id": client_id,
            "algorithm": limiter_info["algorithm"],
            "config": limiter_info["config"],
            "status": limiter.get_status(),
            "created_at": limiter_info["created_at"].isoformat(),
            "last_used": limiter_info["last_used"].isoformat()
        }
    
    def update_limiter_config(
        self,
        client_id: str,
        limit: Optional[int] = None,
        window_seconds: Optional[int] = None,
        **kwargs
    ) -> bool:
        """Update the configuration of an existing rate limiter."""
        if client_id not in self.limiters:
            logger.warning(f"Cannot update non-existent limiter: {client_id}")
            return False
        
        try:
            limiter_info = self.limiters[client_id]
            limiter = limiter_info["limiter"]
            
            # Update configuration
            if limit is not None:
                limiter_info["config"]["limit"] = limit
                limiter.update_limit(limit)
            
            if window_seconds is not None:
                limiter_info["config"]["window_seconds"] = window_seconds
                limiter.update_window(window_seconds)
            
            # Update other kwargs
            for key, value in kwargs.items():
                limiter_info["config"][key] = value
                if hasattr(limiter, f"update_{key}"):
                    getattr(limiter, f"update_{key}")(value)
            
            logger.info(f"Rate limiter config updated for {client_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating rate limiter config for {client_id}: {e}")
            return False
    
    def remove_limiter(self, client_id: str) -> bool:
        """Remove a rate limiter for a client."""
        if client_id in self.limiters:
            del self.limiters[client_id]
            logger.info(f"Rate limiter removed for {client_id}")
            return True
        return False
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global rate limiting statistics."""
        return {
            "total_limiters": len(self.limiters),
            "total_requests": self.total_requests,
            "blocked_requests": self.blocked_requests,
            "success_rate": (self.total_requests - self.blocked_requests) / max(self.total_requests, 1) * 100,
            "enabled": self.global_config["enabled"],
            "default_algorithm": self.default_algorithm,
            "recent_events": len(self.rate_limit_events)
        }
    
    def get_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent rate limiting events."""
        return list(self.rate_limit_events)[-limit:]
    
    def set_global_config(self, **kwargs) -> None:
        """Update global rate limiting configuration."""
        for key, value in kwargs.items():
            if key in self.global_config:
                self.global_config[key] = value
                logger.info(f"Global config updated: {key} = {value}")
    
    def enable_global_rate_limiting(self) -> None:
        """Enable global rate limiting."""
        self.global_config["enabled"] = True
        logger.info("Global rate limiting enabled")
    
    def disable_global_rate_limiting(self) -> None:
        """Disable global rate limiting."""
        self.global_config["enabled"] = False
        logger.info("Global rate limiting disabled")
    
    def cleanup_inactive_limiters(self, max_inactive_hours: int = 24) -> int:
        """Remove inactive rate limiters to free memory."""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_inactive_hours)
        removed_count = 0
        
        inactive_clients = [
            client_id for client_id, info in self.limiters.items()
            if info["last_used"] < cutoff_time
        ]
        
        for client_id in inactive_clients:
            self.remove_limiter(client_id)
            removed_count += 1
        
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} inactive rate limiters")
        
        return removed_count


class TokenBucketLimiter:
    """
    Token bucket rate limiter implementation.
    
    Provides smooth rate limiting with burst capability.
    Tokens are added at a constant rate and consumed per request.
    """
    
    def __init__(self, limit: int, window_seconds: int, max_burst: int = None):
        """Initialize the token bucket limiter."""
        self.limit = limit
        self.window_seconds = window_seconds
        self.max_burst = max_burst or (limit * 2)
        self.tokens = self.max_burst
        self.last_refill = time.time()
        self.refill_rate = limit / window_seconds
        
        logger.debug(f"TokenBucketLimiter initialized: {limit}/{window_seconds}s, burst: {self.max_burst}")
    
    async def check_limit(self) -> Tuple[bool, Dict[str, Any]]:
        """Check if a request is allowed."""
        now = time.time()
        
        # Refill tokens
        time_passed = now - self.last_refill
        tokens_to_add = time_passed * self.refill_rate
        
        self.tokens = min(self.max_burst, self.tokens + tokens_to_add)
        self.last_refill = now
        
        # Check if tokens are available
        if self.tokens >= 1:
            self.tokens -= 1
            return True, {
                "status": "allowed",
                "tokens_remaining": self.tokens,
                "limit": self.limit,
                "window_seconds": self.window_seconds
            }
        else:
            return False, {
                "status": "blocked",
                "tokens_remaining": self.tokens,
                "limit": self.limit,
                "window_seconds": self.window_seconds,
                "retry_after": self._calculate_retry_after()
            }
    
    def _calculate_retry_after(self) -> float:
        """Calculate when the next token will be available."""
        tokens_needed = 1 - self.tokens
        return tokens_needed / self.refill_rate
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the limiter."""
        return {
            "tokens": self.tokens,
            "max_burst": self.max_burst,
            "refill_rate": self.refill_rate,
            "last_refill": self.last_refill
        }
    
    def update_limit(self, new_limit: int) -> None:
        """Update the rate limit."""
        self.limit = new_limit
        self.refill_rate = new_limit / self.window_seconds
    
    def update_window(self, new_window: int) -> None:
        """Update the time window."""
        self.window_seconds = new_window
        self.refill_rate = self.limit / new_window


class FixedWindowLimiter:
    """
    Fixed window rate limiter implementation.
    
    Simple rate limiting where limits reset at fixed time intervals.
    Less accurate but more predictable than sliding window.
    """
    
    def __init__(self, limit: int, window_seconds: int):
        """Initialize the fixed window limiter."""
        self.limit = limit
        self.window_seconds = window_seconds
        self.current_window = self._get_current_window()
        self.request_count = 0
        
        logger.debug(f"FixedWindowLimiter initialized: {limit}/{window_seconds}s")
    
    async def check_limit(self) -> Tuple[bool, Dict[str, Any]]:
        """Check if a request is allowed."""
        current_window = self._get_current_window()
        
        # Reset counter for new window
        if current_window != self.current_window:
            self.current_window = current_window
            self.request_count = 0
        
        # Check limit
        if self.request_count < self.limit:
            self.request_count += 1
            return True, {
                "status": "allowed",
                "requests_remaining": self.limit - self.request_count,
                "limit": self.limit,
                "window_seconds": self.window_seconds,
                "window_start": self.current_window
            }
        else:
            return False, {
                "status": "blocked",
                "requests_remaining": 0,
                "limit": self.limit,
                "window_seconds": self.window_seconds,
                "window_start": self.current_window,
                "retry_after": self._calculate_retry_after()
            }
    
    def _get_current_window(self) -> int:
        """Get the current time window identifier."""
        return int(time.time() // self.window_seconds)
    
    def _calculate_retry_after(self) -> float:
        """Calculate when the next window starts."""
        current_time = time.time()
        next_window = (int(current_time // self.window_seconds) + 1) * self.window_seconds
        return next_window - current_time
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the limiter."""
        return {
            "current_window": self.current_window,
            "request_count": self.request_count,
            "window_start": self.current_window * self.window_seconds
        }
    
    def update_limit(self, new_limit: int) -> None:
        """Update the rate limit."""
        self.limit = new_limit
    
    def update_window(self, new_window: int) -> None:
        """Update the time window."""
        self.window_seconds = new_window
        # Reset current window to force immediate reset
        self.current_window = self._get_current_window()
        self.request_count = 0


class SlidingWindowLimiter:
    """
    Sliding window rate limiter implementation.
    
    More accurate rate limiting that considers requests within
    a sliding time window rather than fixed intervals.
    """
    
    def __init__(self, limit: int, window_seconds: int):
        """Initialize the sliding window limiter."""
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests = deque()
        
        logger.debug(f"SlidingWindowLimiter initialized: {limit}/{window_seconds}s")
    
    async def check_limit(self) -> Tuple[bool, Dict[str, Any]]:
        """Check if a request is allowed."""
        now = time.time()
        
        # Remove old requests outside the window
        while self.requests and self.requests[0] < now - self.window_seconds:
            self.requests.popleft()
        
        # Check if we can add a new request
        if len(self.requests) < self.limit:
            self.requests.append(now)
            return True, {
                "status": "allowed",
                "requests_remaining": self.limit - len(self.requests),
                "limit": self.limit,
                "window_seconds": self.window_seconds,
                "current_requests": len(self.requests)
            }
        else:
            return False, {
                "status": "blocked",
                "requests_remaining": 0,
                "limit": self.limit,
                "window_seconds": self.window_seconds,
                "current_requests": len(self.requests),
                "retry_after": self._calculate_retry_after()
            }
    
    def _calculate_retry_after(self) -> float:
        """Calculate when the oldest request will expire."""
        if not self.requests:
            return 0
        return self.requests[0] + self.window_seconds - time.time()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the limiter."""
        return {
            "current_requests": len(self.requests),
            "window_seconds": self.window_seconds,
            "oldest_request": self.requests[0] if self.requests else None
        }
    
    def update_limit(self, new_limit: int) -> None:
        """Update the rate limit."""
        self.limit = new_limit
    
    def update_window(self, new_window: int) -> None:
        """Update the time window."""
        self.window_seconds = new_window
        # Clean up old requests based on new window
        now = time.time()
        while self.requests and self.requests[0] < now - new_window:
            self.requests.popleft()
