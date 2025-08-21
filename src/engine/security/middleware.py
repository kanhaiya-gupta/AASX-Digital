"""
Security Middleware
==================

Middleware components for security, authentication, authorization,
rate limiting, and audit logging.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Union
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass

from .models import SecurityContext, User
from .authentication import Authenticator
from .authorization import AuthorizationManager

logger = logging.getLogger(__name__)


@dataclass
class RequestContext:
    """Request context for middleware processing"""
    request_id: str
    user_id: Optional[str] = None
    username: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    method: str = ""
    path: str = ""
    headers: Dict[str, str] = None
    body: Any = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        if self.headers is None:
            self.headers = {}


class SecurityMiddleware(ABC):
    """Abstract base class for security middleware"""
    
    def __init__(self, name: str = "SecurityMiddleware"):
        self.name = name
        self.enabled = True
        self.priority = 100  # Lower numbers = higher priority
    
    @abstractmethod
    def process_request(self, context: RequestContext) -> Union[RequestContext, Dict[str, Any]]:
        """Process incoming request"""
        pass
    
    @abstractmethod
    def process_response(self, context: RequestContext, response: Any) -> Any:
        """Process outgoing response"""
        pass
    
    def is_enabled(self) -> bool:
        """Check if middleware is enabled"""
        return self.enabled
    
    def enable(self) -> None:
        """Enable middleware"""
        self.enabled = True
        logger.info(f"Enabled middleware: {self.name}")
    
    def disable(self) -> None:
        """Disable middleware"""
        self.enabled = False
        logger.info(f"Disabled middleware: {self.name}")


class AuthenticationMiddleware(SecurityMiddleware):
    """Middleware for authentication"""
    
    def __init__(self, authenticator: Authenticator, 
                 token_header: str = "Authorization",
                 token_prefix: str = "Bearer"):
        super().__init__("AuthenticationMiddleware")
        self.authenticator = authenticator
        self.token_header = token_header
        self.token_prefix = token_prefix
        self.priority = 10  # High priority - run first
    
    def process_request(self, context: RequestContext) -> Union[RequestContext, Dict[str, Any]]:
        """Process authentication for incoming request"""
        if not self.enabled:
            return context
        
        try:
            # Extract token from headers
            auth_header = context.headers.get(self.token_header, "")
            
            if not auth_header:
                return {
                    'error': 'authentication_required',
                    'message': 'Authentication token required',
                    'status_code': 401
                }
            
            # Parse token
            if not auth_header.startswith(self.token_prefix):
                return {
                    'error': 'invalid_token_format',
                    'message': f'Token must start with {self.token_prefix}',
                    'status_code': 401
                }
            
            token = auth_header[len(self.token_prefix):].strip()
            if not token:
                return {
                    'error': 'invalid_token',
                    'message': 'Empty authentication token',
                    'status_code': 401
                }
            
            # Validate token
            security_context = self.authenticator.validate_token(token)
            if not security_context:
                return {
                    'error': 'invalid_token',
                    'message': 'Invalid or expired authentication token',
                    'status_code': 401
                }
            
            # Update request context with user information
            context.user_id = security_context.user_id
            context.username = security_context.username
            
            # Store security context for later use
            context.security_context = security_context
            
            logger.debug(f"Authenticated user: {context.username} ({context.user_id})")
            return context
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return {
                'error': 'authentication_error',
                'message': 'Authentication processing error',
                'status_code': 500
            }
    
    def process_response(self, context: RequestContext, response: Any) -> Any:
        """Process authentication for outgoing response"""
        if not self.enabled:
            return response
        
        # Add authentication headers if needed
        if hasattr(response, 'headers'):
            response.headers['X-Authenticated-User'] = context.username or 'anonymous'
        
        return response


class AuthorizationMiddleware(SecurityMiddleware):
    """Middleware for authorization"""
    
    def __init__(self, authorization_manager: AuthorizationManager,
                 default_policy: str = "deny"):
        super().__init__("AuthorizationMiddleware")
        self.authorization_manager = authorization_manager
        self.default_policy = default_policy
        self.priority = 20  # Run after authentication
        
        # Define resource-action mappings
        self._resource_mappings = {
            'GET': 'read',
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete'
        }
    
    def process_request(self, context: RequestContext) -> Union[RequestContext, Dict[str, Any]]:
        """Process authorization for incoming request"""
        if not self.enabled:
            return context
        
        try:
            # Skip authorization for unauthenticated requests
            if not context.user_id:
                return context
            
            # Determine resource and action from request
            resource = self._extract_resource(context.path)
            action = self._extract_action(context.method)
            
            if not resource or not action:
                return context
            
            # Check authorization
            security_context = getattr(context, 'security_context', None)
            if not security_context:
                # Create minimal security context
                security_context = SecurityContext(
                    user_id=context.user_id,
                    username=context.username
                )
            
            auth_result = self.authorization_manager.check_permission(
                security_context, resource, action
            )
            
            if not auth_result.allowed:
                logger.warning(f"Access denied: {context.username} cannot {action} {resource}")
                return {
                    'error': 'access_denied',
                    'message': f'Access denied: insufficient permissions for {action} on {resource}',
                    'status_code': 403,
                    'details': {
                        'resource': resource,
                        'action': action,
                        'required_permissions': auth_result.required_permissions
                    }
                }
            
            logger.debug(f"Authorization granted: {context.username} can {action} {resource}")
            return context
            
        except Exception as e:
            logger.error(f"Authorization error: {e}")
            return {
                'error': 'authorization_error',
                'message': 'Authorization processing error',
                'status_code': 500
            }
    
    def process_response(self, context: RequestContext, response: Any) -> Any:
        """Process authorization for outgoing response"""
        if not self.enabled:
            return response
        
        # Add authorization headers if needed
        if hasattr(response, 'headers'):
            response.headers['X-Authorization-Status'] = 'granted'
        
        return response
    
    def _extract_resource(self, path: str) -> str:
        """Extract resource from request path"""
        if not path:
            return None
        
        # Remove leading slash and split
        path_parts = path.lstrip('/').split('/')
        
        # First part is usually the resource
        if path_parts:
            return path_parts[0]
        
        return None
    
    def _extract_action(self, method: str) -> str:
        """Extract action from HTTP method"""
        return self._resource_mappings.get(method.upper(), 'unknown')


class RateLimitMiddleware(SecurityMiddleware):
    """Middleware for rate limiting"""
    
    def __init__(self, 
                 requests_per_minute: int = 60,
                 requests_per_hour: int = 1000,
                 burst_limit: int = 10):
        super().__init__("RateLimitMiddleware")
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_limit = burst_limit
        self.priority = 30  # Run after authentication/authorization
        
        # Rate limiting storage
        self._minute_requests: Dict[str, List[float]] = {}
        self._hour_requests: Dict[str, List[float]] = {}
        self._burst_requests: Dict[str, List[float]] = {}
    
    def process_request(self, context: RequestContext) -> Union[RequestContext, Dict[str, Any]]:
        """Process rate limiting for incoming request"""
        if not self.enabled:
            return context
        
        try:
            # Determine client identifier
            client_id = self._get_client_id(context)
            current_time = time.time()
            
            # Check minute limit
            if not self._check_rate_limit(client_id, current_time, 
                                       self._minute_requests, 60, self.requests_per_minute):
                return {
                    'error': 'rate_limit_exceeded',
                    'message': 'Too many requests per minute',
                    'status_code': 429,
                    'retry_after': 60
                }
            
            # Check hour limit
            if not self._check_rate_limit(client_id, current_time,
                                       self._hour_requests, 3600, self.requests_per_hour):
                return {
                    'error': 'rate_limit_exceeded',
                    'message': 'Too many requests per hour',
                    'status_code': 429,
                    'retry_after': 3600
                }
            
            # Check burst limit
            if not self._check_rate_limit(client_id, current_time,
                                       self._burst_requests, 1, self.burst_limit):
                return {
                    'error': 'rate_limit_exceeded',
                    'message': 'Burst limit exceeded',
                    'status_code': 429,
                    'retry_after': 1
                }
            
            # Record request
            self._record_request(client_id, current_time)
            
            return context
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return context  # Allow request on error
    
    def process_response(self, context: RequestContext, response: Any) -> Any:
        """Process rate limiting for outgoing response"""
        if not self.enabled:
            return response
        
        # Add rate limit headers
        if hasattr(response, 'headers'):
            client_id = self._get_client_id(context)
            response.headers['X-RateLimit-Limit-Minute'] = str(self.requests_per_minute)
            response.headers['X-RateLimit-Limit-Hour'] = str(self.requests_per_hour)
            response.headers['X-RateLimit-Remaining-Minute'] = str(self._get_remaining_requests(
                client_id, self._minute_requests, 60, self.requests_per_minute))
            response.headers['X-RateLimit-Remaining-Hour'] = str(self._get_remaining_requests(
                client_id, self._hour_requests, 3600, self.requests_per_hour))
        
        return response
    
    def _get_client_id(self, context: RequestContext) -> str:
        """Get unique client identifier"""
        # Use user ID if authenticated, otherwise use IP address
        if context.user_id:
            return f"user:{context.user_id}"
        else:
            return f"ip:{context.ip_address or 'unknown'}"
    
    def _check_rate_limit(self, client_id: str, current_time: float,
                         request_store: Dict[str, List[float]], 
                         window_seconds: int, max_requests: int) -> bool:
        """Check if rate limit is exceeded"""
        if client_id not in request_store:
            return True
        
        # Remove old requests outside the window
        cutoff_time = current_time - window_seconds
        request_store[client_id] = [t for t in request_store[client_id] if t > cutoff_time]
        
        # Check if limit exceeded
        return len(request_store[client_id]) < max_requests
    
    def _record_request(self, client_id: str, timestamp: float) -> None:
        """Record a request for rate limiting"""
        # Record for minute window
        if client_id not in self._minute_requests:
            self._minute_requests[client_id] = []
        self._minute_requests[client_id].append(timestamp)
        
        # Record for hour window
        if client_id not in self._hour_requests:
            self._hour_requests[client_id] = []
        self._hour_requests[client_id].append(timestamp)
        
        # Record for burst window
        if client_id not in self._burst_requests:
            self._burst_requests[client_id] = []
        self._burst_requests[client_id].append(timestamp)
    
    def _get_remaining_requests(self, client_id: str, request_store: Dict[str, List[float]],
                               window_seconds: int, max_requests: int) -> int:
        """Get remaining requests for a client"""
        if client_id not in request_store:
            return max_requests
        
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        # Count recent requests
        recent_requests = len([t for t in request_store[client_id] if t > cutoff_time])
        
        return max(0, max_requests - recent_requests)
    
    def cleanup_old_requests(self) -> None:
        """Clean up old rate limiting data"""
        current_time = time.time()
        
        # Clean minute requests
        for client_id in list(self._minute_requests.keys()):
            cutoff_time = current_time - 60
            self._minute_requests[client_id] = [t for t in self._minute_requests[client_id] if t > cutoff_time]
            if not self._minute_requests[client_id]:
                del self._minute_requests[client_id]
        
        # Clean hour requests
        for client_id in list(self._hour_requests.keys()):
            cutoff_time = current_time - 3600
            self._hour_requests[client_id] = [t for t in self._hour_requests[client_id] if t > cutoff_time]
            if not self._hour_requests[client_id]:
                del self._hour_requests[client_id]
        
        # Clean burst requests
        for client_id in list(self._burst_requests.keys()):
            cutoff_time = current_time - 1
            self._burst_requests[client_id] = [t for t in self._burst_requests[client_id] if t > cutoff_time]
            if not self._burst_requests[client_id]:
                del self._burst_requests[client_id]


class AuditMiddleware(SecurityMiddleware):
    """Middleware for audit logging"""
    
    def __init__(self, audit_logger=None):
        super().__init__("AuditMiddleware")
        self.audit_logger = audit_logger
        self.priority = 40  # Run last to capture all information
    
    def process_request(self, context: RequestContext) -> Union[RequestContext, Dict[str, Any]]:
        """Process audit logging for incoming request"""
        if not self.enabled:
            return context
        
        # Store start time for performance measurement
        context.audit_start_time = time.time()
        
        return context
    
    def process_response(self, context: RequestContext, response: Any) -> Any:
        """Process audit logging for outgoing response"""
        if not self.enabled:
            return response
        
        try:
            if hasattr(context, 'audit_start_time'):
                duration = time.time() - context.audit_start_time
            else:
                duration = 0
            
            # Log the request
            self._log_request(context, response, duration)
            
        except Exception as e:
            logger.error(f"Audit logging error: {e}")
        
        return response
    
    def _log_request(self, context: RequestContext, response: Any, duration: float) -> None:
        """Log request details for audit"""
        if not self.audit_logger:
            return
        
        # Determine action type
        action = self._determine_action(context.method, response)
        
        # Determine resource
        resource = context.path or "unknown"
        
        # Determine success
        success = self._is_successful_response(response)
        
        # Create audit details
        details = {
            'method': context.method,
            'path': context.path,
            'duration': duration,
            'ip_address': context.ip_address,
            'user_agent': context.user_agent,
            'headers': dict(context.headers),
            'response_status': getattr(response, 'status_code', None),
            'response_size': len(str(response)) if response else 0
        }
        
        # Log the event
        if context.user_id and context.username:
            self.audit_logger.log_data_access(
                user_id=context.user_id,
                username=context.username,
                action=action,
                resource=resource,
                details=details
            )
        else:
            # Anonymous request
            self.audit_logger.log_event(
                AuditEvent(
                    timestamp=context.timestamp,
                    user_id=None,
                    username=None,
                    action=f"anonymous_{action}",
                    resource=resource,
                    details=details,
                    ip_address=context.ip_address,
                    user_agent=context.user_agent,
                    success=success
                )
            )
    
    def _determine_action(self, method: str, response: Any) -> str:
        """Determine the action performed based on method and response"""
        method_actions = {
            'GET': 'read',
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete',
            'HEAD': 'read',
            'OPTIONS': 'read'
        }
        
        return method_actions.get(method.upper(), 'unknown')
    
    def _is_successful_response(self, response: Any) -> bool:
        """Determine if response indicates success"""
        if hasattr(response, 'status_code'):
            return 200 <= response.status_code < 400
        return True


class SecurityMiddlewareChain:
    """Chain of security middleware for processing requests"""
    
    def __init__(self):
        self.middleware: List[SecurityMiddleware] = []
        self._sorted_middleware = []
    
    def add_middleware(self, middleware: SecurityMiddleware) -> None:
        """Add middleware to the chain"""
        self.middleware.append(middleware)
        self._sort_middleware()
        logger.info(f"Added middleware to chain: {middleware.name}")
    
    def remove_middleware(self, name: str) -> bool:
        """Remove middleware by name"""
        for i, middleware in enumerate(self.middleware):
            if middleware.name == name:
                del self.middleware[i]
                self._sort_middleware()
                logger.info(f"Removed middleware from chain: {name}")
                return True
        return False
    
    def _sort_middleware(self) -> None:
        """Sort middleware by priority"""
        self._sorted_middleware = sorted(self.middleware, key=lambda m: m.priority)
    
    def process_request(self, context: RequestContext) -> Union[RequestContext, Dict[str, Any]]:
        """Process request through all middleware"""
        current_context = context
        
        for middleware in self._sorted_middleware:
            if not middleware.is_enabled():
                continue
            
            try:
                result = middleware.process_request(current_context)
                
                # Check if middleware returned an error
                if isinstance(result, dict) and 'error' in result:
                    return result
                
                current_context = result
                
            except Exception as e:
                logger.error(f"Middleware {middleware.name} error: {e}")
                return {
                    'error': 'middleware_error',
                    'message': f'Middleware {middleware.name} processing error',
                    'status_code': 500
                }
        
        return current_context
    
    def process_response(self, context: RequestContext, response: Any) -> Any:
        """Process response through all middleware in reverse order"""
        current_response = response
        
        for middleware in reversed(self._sorted_middleware):
            if not middleware.is_enabled():
                continue
            
            try:
                current_response = middleware.process_response(context, current_response)
            except Exception as e:
                logger.error(f"Middleware {middleware.name} response error: {e}")
                # Continue processing other middleware
        
        return current_response
    
    def get_middleware_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all middleware"""
        status = {}
        for middleware in self.middleware:
            status[middleware.name] = {
                'enabled': middleware.is_enabled(),
                'priority': middleware.priority,
                'type': middleware.__class__.__name__
            }
        return status
    
    def enable_middleware(self, name: str) -> bool:
        """Enable middleware by name"""
        for middleware in self.middleware:
            if middleware.name == name:
                middleware.enable()
                return True
        return False
    
    def disable_middleware(self, name: str) -> bool:
        """Disable middleware by name"""
        for middleware in self.middleware:
            if middleware.name == name:
                middleware.disable()
                return True
        return False
