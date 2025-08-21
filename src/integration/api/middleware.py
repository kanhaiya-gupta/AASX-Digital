"""
API Middleware Service

This module provides middleware components for the API layer, including
authentication, authorization, request validation, logging, and other
cross-cutting concerns.

The middleware handles:
- Authentication and authorization
- Request/response validation
- Logging and monitoring
- CORS and security headers
- Request transformation
"""

import asyncio
import json
import logging
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, Union
from uuid import UUID

logger = logging.getLogger(__name__)


class APIMiddleware:
    """
    Base middleware class for API request processing.
    
    All middleware components should inherit from this class and implement
    the process_request method.
    """
    
    def __init__(self, name: str = "BaseMiddleware"):
        """Initialize the middleware."""
        self.name = name
        self.enabled = True
        logger.info(f"Middleware {name} initialized")
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the request and return the modified request.
        
        This method should be overridden by subclasses to implement
        specific middleware functionality.
        """
        return request
    
    def enable(self) -> None:
        """Enable the middleware."""
        self.enabled = True
        logger.info(f"Middleware {self.name} enabled")
    
    def disable(self) -> None:
        """Disable the middleware."""
        self.enabled = False
        logger.info(f"Middleware {self.name} disabled")
    
    def is_enabled(self) -> bool:
        """Check if the middleware is enabled."""
        return self.enabled


class AuthenticationMiddleware(APIMiddleware):
    """
    Middleware for handling API authentication.
    
    Supports multiple authentication methods:
    - API Key authentication
    - JWT token authentication
    - HMAC signature authentication
    """
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None, jwt_secret: Optional[str] = None):
        """Initialize the authentication middleware."""
        super().__init__("AuthenticationMiddleware")
        self.api_keys = api_keys or {}
        self.jwt_secret = jwt_secret or "default_secret"
        self.authenticated_users: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Authentication middleware initialized")
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process the request and authenticate the user."""
        if not self.enabled:
            return request
        
        try:
            headers = request.get("headers", {})
            
            # Try different authentication methods
            user = await self._authenticate_api_key(headers)
            if not user:
                user = await self._authenticate_jwt(headers)
            if not user:
                user = await self._authenticate_hmac(request)
            
            if user:
                request["authenticated_user"] = user
                request["is_authenticated"] = True
                logger.info(f"User authenticated: {user.get('user_id', 'unknown')}")
            else:
                request["is_authenticated"] = False
                request["auth_error"] = "Authentication failed"
                logger.warning("Authentication failed for request")
            
            return request
            
        except Exception as e:
            logger.error(f"Authentication middleware error: {e}")
            request["is_authenticated"] = False
            request["auth_error"] = str(e)
            return request
    
    async def _authenticate_api_key(self, headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Authenticate using API key."""
        api_key = headers.get("X-API-Key") or headers.get("Authorization", "").replace("Bearer ", "")
        
        if not api_key:
            return None
        
        if api_key in self.api_keys:
            return {
                "user_id": f"api_user_{api_key[:8]}",
                "auth_method": "api_key",
                "permissions": ["read", "write"],
                "authenticated_at": datetime.utcnow().isoformat()
            }
        
        return None
    
    async def _authenticate_jwt(self, headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Authenticate using JWT token."""
        auth_header = headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        
        try:
            # This is a simplified JWT validation - in a real implementation,
            # you would use a proper JWT library
            if self._validate_jwt_token(token):
                return {
                    "user_id": "jwt_user",
                    "auth_method": "jwt",
                    "permissions": ["read", "write"],
                    "authenticated_at": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"JWT validation error: {e}")
        
        return None
    
    async def _authenticate_hmac(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Authenticate using HMAC signature."""
        headers = request.get("headers", {})
        signature = headers.get("X-HMAC-Signature")
        timestamp = headers.get("X-Timestamp")
        
        if not signature or not timestamp:
            return None
        
        try:
            # Validate timestamp (prevent replay attacks)
            request_time = datetime.fromisoformat(timestamp)
            if abs((datetime.utcnow() - request_time).total_seconds()) > 300:  # 5 minutes
                logger.warning("Request timestamp too old")
                return None
            
            # This is a placeholder for HMAC validation
            # In a real implementation, you would validate the signature
            if self._validate_hmac_signature(request, signature):
                return {
                    "user_id": "hmac_user",
                    "auth_method": "hmac",
                    "permissions": ["read", "write"],
                    "authenticated_at": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"HMAC validation error: {e}")
        
        return None
    
    def _validate_jwt_token(self, token: str) -> bool:
        """Validate JWT token (placeholder implementation)."""
        # This is a placeholder - in a real implementation, you would:
        # 1. Decode the JWT token
        # 2. Validate the signature
        # 3. Check expiration
        # 4. Verify claims
        return token.startswith("eyJ")  # Simple check for JWT format
    
    def _validate_hmac_signature(self, request: Dict[str, Any], signature: str) -> bool:
        """Validate HMAC signature (placeholder implementation)."""
        # This is a placeholder - in a real implementation, you would:
        # 1. Reconstruct the message
        # 2. Generate HMAC using shared secret
        # 3. Compare with provided signature
        return len(signature) >= 32  # Simple length check
    
    def add_api_key(self, key: str, user_id: str) -> None:
        """Add a new API key for authentication."""
        self.api_keys[key] = user_id
        logger.info(f"API key added for user: {user_id}")
    
    def remove_api_key(self, key: str) -> None:
        """Remove an API key."""
        if key in self.api_keys:
            del self.api_keys[key]
            logger.info("API key removed")


class AuthorizationMiddleware(APIMiddleware):
    """
    Middleware for handling API authorization.
    
    Checks if authenticated users have permission to access
    specific endpoints and resources.
    """
    
    def __init__(self):
        """Initialize the authorization middleware."""
        super().__init__("AuthorizationMiddleware")
        self.permission_rules: Dict[str, List[str]] = {
            "/health": ["read"],
            "/health/detailed": ["read"],
            "/api/v1/workflows": ["read", "write"],
            "/api/v1/modules": ["read", "write"],
            "/api/v1/data": ["read", "write"]
        }
        
        logger.info("Authorization middleware initialized")
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process the request and check authorization."""
        if not self.enabled:
            return request
        
        try:
            # Skip authorization for health checks
            if request.get("path", "").startswith("/health"):
                request["is_authorized"] = True
                return request
            
            # Check if user is authenticated
            if not request.get("is_authenticated", False):
                request["is_authorized"] = False
                request["auth_error"] = "Authentication required"
                return request
            
            # Check permissions
            user = request.get("authenticated_user", {})
            user_permissions = user.get("permissions", [])
            path = request.get("path", "")
            method = request.get("method", "")
            
            required_permissions = self._get_required_permissions(path, method)
            
            if self._check_permissions(user_permissions, required_permissions):
                request["is_authorized"] = True
                logger.info(f"User {user.get('user_id')} authorized for {method} {path}")
            else:
                request["is_authorized"] = False
                request["auth_error"] = "Insufficient permissions"
                logger.warning(f"User {user.get('user_id')} denied access to {method} {path}")
            
            return request
            
        except Exception as e:
            logger.error(f"Authorization middleware error: {e}")
            request["is_authorized"] = False
            request["auth_error"] = str(e)
            return request
    
    def _get_required_permissions(self, path: str, method: str) -> List[str]:
        """Get required permissions for a path and method."""
        base_path = self._get_base_path(path)
        
        if method in ["GET", "HEAD"]:
            return ["read"]
        elif method in ["POST", "PUT", "PATCH"]:
            return ["write"]
        elif method == "DELETE":
            return ["write", "delete"]
        else:
            return ["read"]
    
    def _get_base_path(self, path: str) -> str:
        """Get the base path without parameters."""
        # Remove path parameters like {workflow_id}
        parts = path.split('/')
        base_parts = []
        
        for part in parts:
            if part.startswith('{') and part.endswith('}'):
                base_parts.append('{param}')
            else:
                base_parts.append(part)
        
        return '/'.join(base_parts)
    
    def _check_permissions(self, user_permissions: List[str], required_permissions: List[str]) -> bool:
        """Check if user has required permissions."""
        return all(perm in user_permissions for perm in required_permissions)
    
    def add_permission_rule(self, path: str, permissions: List[str]) -> None:
        """Add a new permission rule."""
        self.permission_rules[path] = permissions
        logger.info(f"Permission rule added for {path}: {permissions}")


class RateLimitingMiddleware(APIMiddleware):
    """
    Middleware for rate limiting API requests.
    
    Implements token bucket algorithm for rate limiting
    with configurable limits per user/IP.
    """
    
    def __init__(self, default_limit: int = 100, window_seconds: int = 60):
        """Initialize the rate limiting middleware."""
        super().__init__("RateLimitingMiddleware")
        self.default_limit = default_limit
        self.window_seconds = window_seconds
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"Rate limiting middleware initialized: {default_limit} requests per {window_seconds}s")
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process the request and check rate limits."""
        if not self.enabled:
            return request
        
        try:
            # Get client identifier
            client_id = self._get_client_id(request)
            
            # Check rate limit
            if await self._check_rate_limit(client_id):
                request["rate_limit_status"] = "allowed"
                return request
            else:
                request["rate_limit_status"] = "blocked"
                request["rate_limit_error"] = "Rate limit exceeded"
                return request
                
        except Exception as e:
            logger.error(f"Rate limiting middleware error: {e}")
            request["rate_limit_status"] = "error"
            request["rate_limit_error"] = str(e)
            return request
    
    def _get_client_id(self, request: Dict[str, Any]) -> str:
        """Get client identifier for rate limiting."""
        headers = request.get("headers", {})
        
        # Try to get user ID from authentication
        if request.get("authenticated_user"):
            return f"user_{request['authenticated_user']['user_id']}"
        
        # Fall back to IP address
        return f"ip_{headers.get('X-Forwarded-For', 'unknown')}"
    
    async def _check_rate_limit(self, client_id: str) -> bool:
        """Check if client is within rate limits."""
        now = datetime.utcnow()
        
        if client_id not in self.rate_limits:
            self.rate_limits[client_id] = {
                "tokens": self.default_limit,
                "last_refill": now,
                "limit": self.default_limit
            }
        
        client_limit = self.rate_limits[client_id]
        
        # Refill tokens based on time passed
        time_passed = (now - client_limit["last_refill"]).total_seconds()
        tokens_to_add = int(time_passed / self.window_seconds) * client_limit["limit"]
        
        if tokens_to_add > 0:
            client_limit["tokens"] = min(
                client_limit["limit"],
                client_limit["tokens"] + tokens_to_add
            )
            client_limit["last_refill"] = now
        
        # Check if tokens are available
        if client_limit["tokens"] > 0:
            client_limit["tokens"] -= 1
            return True
        
        return False
    
    def set_client_limit(self, client_id: str, limit: int) -> None:
        """Set custom rate limit for a specific client."""
        if client_id not in self.rate_limits:
            self.rate_limits[client_id] = {
                "tokens": limit,
                "last_refill": datetime.utcnow(),
                "limit": limit
            }
        else:
            self.rate_limits[client_id]["limit"] = limit
            self.rate_limits[client_id]["tokens"] = limit
        
        logger.info(f"Rate limit set for {client_id}: {limit} requests per {self.window_seconds}s")
    
    def get_rate_limit_status(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get current rate limit status for a client."""
        if client_id not in self.rate_limits:
            return None
        
        client_limit = self.rate_limits[client_id]
        return {
            "client_id": client_id,
            "tokens_remaining": client_limit["tokens"],
            "limit": client_limit["limit"],
            "window_seconds": self.window_seconds,
            "last_refill": client_limit["last_refill"].isoformat()
        }


class LoggingMiddleware(APIMiddleware):
    """
    Middleware for comprehensive request/response logging.
    
    Logs all API requests and responses with detailed information
    for monitoring and debugging purposes.
    """
    
    def __init__(self, log_level: str = "INFO"):
        """Initialize the logging middleware."""
        super().__init__("LoggingMiddleware")
        self.log_level = log_level.upper()
        self.request_logger = logging.getLogger("api.requests")
        self.response_logger = logging.getLogger("api.responses")
        
        logger.info(f"Logging middleware initialized with level: {log_level}")
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process the request and log it."""
        if not self.enabled:
            return request
        
        try:
            # Add request ID for tracking
            request["request_id"] = self._generate_request_id()
            request["request_timestamp"] = datetime.utcnow().isoformat()
            
            # Log request details
            self._log_request(request)
            
            return request
            
        except Exception as e:
            logger.error(f"Logging middleware error: {e}")
            return request
    
    def _generate_request_id(self) -> str:
        """Generate a unique request ID."""
        return f"req_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(str(datetime.utcnow().timestamp()))}"
    
    def _log_request(self, request: Dict[str, Any]) -> None:
        """Log request details."""
        log_data = {
            "request_id": request.get("request_id"),
            "timestamp": request.get("request_timestamp"),
            "method": request.get("method"),
            "path": request.get("path"),
            "headers": self._sanitize_headers(request.get("headers", {})),
            "query_params": request.get("query_params", {}),
            "body_size": len(str(request.get("body", ""))),
            "client_ip": request.get("headers", {}).get("X-Forwarded-For", "unknown")
        }
        
        if self.log_level == "DEBUG":
            log_data["body"] = request.get("body")
        
        self.request_logger.info(f"API Request: {json.dumps(log_data, default=str)}")
    
    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Remove sensitive information from headers."""
        sensitive_keys = ["authorization", "cookie", "x-api-key", "x-hmac-signature"]
        sanitized = headers.copy()
        
        for key in sensitive_keys:
            if key.lower() in sanitized:
                sanitized[key.lower()] = "***REDACTED***"
        
        return sanitized
    
    def log_response(self, request: Dict[str, Any], response: Dict[str, Any], duration: float) -> None:
        """Log response details."""
        log_data = {
            "request_id": request.get("request_id"),
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.get("method"),
            "path": request.get("path"),
            "status_code": response.get("status_code", 200),
            "duration_ms": round(duration * 1000, 2),
            "response_size": len(str(response.get("data", ""))),
            "success": response.get("success", True)
        }
        
        if self.log_level == "DEBUG":
            log_data["response_data"] = response.get("data")
        
        self.response_logger.info(f"API Response: {json.dumps(log_data, default=str)}")


class ValidationMiddleware(APIMiddleware):
    """
    Middleware for request validation.
    
    Validates request structure, required fields, and data types
    before processing the request.
    """
    
    def __init__(self):
        """Initialize the validation middleware."""
        super().__init__("ValidationMiddleware")
        self.validation_rules: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Validation middleware initialized")
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process the request and validate it."""
        if not self.enabled:
            return request
        
        try:
            # Validate request structure
            validation_result = await self._validate_request(request)
            
            if validation_result["is_valid"]:
                request["validation_status"] = "valid"
                return request
            else:
                request["validation_status"] = "invalid"
                request["validation_errors"] = validation_result["errors"]
                return request
                
        except Exception as e:
            logger.error(f"Validation middleware error: {e}")
            request["validation_status"] = "error"
            request["validation_errors"] = [str(e)]
            return request
    
    async def _validate_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the request according to rules."""
        errors = []
        
        # Basic request structure validation
        required_fields = ["method", "path"]
        for field in required_fields:
            if field not in request:
                errors.append(f"Missing required field: {field}")
        
        # Method validation
        method = request.get("method", "")
        if method not in ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]:
            errors.append(f"Invalid HTTP method: {method}")
        
        # Path validation
        path = request.get("path", "")
        if not path or not path.startswith("/"):
            errors.append("Invalid path format")
        
        # Body validation for POST/PUT requests
        if method in ["POST", "PUT", "PATCH"]:
            body = request.get("body")
            if body is None:
                errors.append("Request body is required for this method")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
    
    def add_validation_rule(self, path: str, rule: Dict[str, Any]) -> None:
        """Add a validation rule for a specific path."""
        self.validation_rules[path] = rule
        logger.info(f"Validation rule added for {path}")


class CORSMiddleware(APIMiddleware):
    """
    Middleware for handling CORS (Cross-Origin Resource Sharing).
    
    Adds appropriate CORS headers to responses and handles
    preflight OPTIONS requests.
    """
    
    def __init__(self, allowed_origins: Optional[List[str]] = None, allowed_methods: Optional[List[str]] = None):
        """Initialize the CORS middleware."""
        super().__init__("CORSMiddleware")
        self.allowed_origins = allowed_origins or ["*"]
        self.allowed_methods = allowed_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allowed_headers = ["Content-Type", "Authorization", "X-API-Key"]
        
        logger.info("CORS middleware initialized")
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process the request and add CORS headers."""
        if not self.enabled:
            return request
        
        try:
            # Handle preflight OPTIONS request
            if request.get("method") == "OPTIONS":
                request["is_preflight"] = True
                request["cors_headers"] = self._get_cors_headers(request)
            else:
                request["cors_headers"] = self._get_cors_headers(request)
            
            return request
            
        except Exception as e:
            logger.error(f"CORS middleware error: {e}")
            return request
    
    def _get_cors_headers(self, request: Dict[str, Any]) -> Dict[str, str]:
        """Get CORS headers for the request."""
        origin = request.get("headers", {}).get("Origin", "")
        
        headers = {
            "Access-Control-Allow-Methods": ", ".join(self.allowed_methods),
            "Access-Control-Allow-Headers": ", ".join(self.allowed_headers),
            "Access-Control-Max-Age": "86400"  # 24 hours
        }
        
        # Handle origin
        if "*" in self.allowed_origins:
            headers["Access-Control-Allow-Origin"] = "*"
        elif origin in self.allowed_origins:
            headers["Access-Control-Allow-Origin"] = origin
        
        return headers
    
    def add_allowed_origin(self, origin: str) -> None:
        """Add an allowed origin."""
        if origin not in self.allowed_origins:
            self.allowed_origins.append(origin)
            logger.info(f"Allowed origin added: {origin}")
    
    def remove_allowed_origin(self, origin: str) -> None:
        """Remove an allowed origin."""
        if origin in self.allowed_origins:
            self.allowed_origins.remove(origin)
            logger.info(f"Allowed origin removed: {origin}")
