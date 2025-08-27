"""
Request Context Service - Engine Layer
=====================================

Provides centralized request context handling, user authentication, and authorization.
All operations are pure async and designed for FastAPI integration.
"""

import logging
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status

from ..models.request_context import (
    UserContext, RequestContext, AuthenticationResult, 
    AuthorizationResult, PermissionLevel, SessionInfo
)
from ..models.auth import User
from ..services.auth.auth_service import AuthService
from ..services.auth.user_service import UserService
from ..services.auth.role_service import RoleService
from ..repositories.auth_repository import AuthRepository

logger = logging.getLogger(__name__)


class RequestContextService:
    """
    Centralized service for handling request context, user authentication, and authorization.
    
    This service provides a unified interface for:
    - Extracting user context from requests
    - Validating authentication tokens
    - Checking user permissions
    - Managing request context
    """
    
    def __init__(self):
        """Initialize the request context service."""
        self._initialized = False
        self._auth_service = None
        self._user_service = None
        self._role_service = None
        self._auth_repo = None
        
        logger.info("✅ Request Context Service created (lazy initialization)")
    
    async def _ensure_initialized(self) -> None:
        """Ensure services are initialized (lazy initialization)."""
        if self._initialized:
            return
            
        try:
            # Initialize backend services
            self._auth_repo = AuthRepository()
            self._user_service = UserService(self._auth_repo)
            self._role_service = RoleService(self._auth_repo)
            self._auth_service = AuthService(self._auth_repo, self._user_service, self._role_service)
            
            self._initialized = True
            logger.info("✅ Request Context Service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize request context service: {e}")
            raise
    
    async def get_current_user(self, request: Request) -> Optional[User]:
        """
        Extract current user from FastAPI request.
        
        Args:
            request: FastAPI request object
            
        Returns:
            User object if authenticated, None otherwise
        """
        await self._ensure_initialized()
        
        try:
            # Extract token from request headers
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return None
            
            token = auth_header[7:]  # Remove "Bearer " prefix
            
            # Validate token using auth service
            auth_result = await self._auth_service.authenticate_with_token(token)
            
            if auth_result.success and auth_result.user:
                return auth_result.user
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting current user from request: {e}")
            return None
    
    async def get_user_context(self, request: Request) -> Optional[UserContext]:
        """
        Extract complete user context from FastAPI request.
        
        Args:
            request: FastAPI request object
            
        Returns:
            UserContext object if authenticated, None otherwise
        """
        await self._ensure_initialized()
        
        try:
            # Get current user
            user = await self.get_current_user(request)
            if not user:
                return None
            
            # Get user permissions
            permissions = await self._role_service.get_user_permissions(user.user_id)
            permission_levels = set()
            
            # Convert permissions to PermissionLevel enum
            for perm in permissions:
                if perm.get("permission") == "read":
                    permission_levels.add(PermissionLevel.READ)
                elif perm.get("permission") == "write":
                    permission_levels.add(PermissionLevel.WRITE)
                elif perm.get("permission") == "manage":
                    permission_levels.add(PermissionLevel.MANAGE)
                elif perm.get("permission") == "admin":
                    permission_levels.add(PermissionLevel.ADMIN)
                elif perm.get("permission") == "super_admin":
                    permission_levels.add(PermissionLevel.SUPER_ADMIN)
            
            # Get session information
            session_info = None
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]
                # Find session by token
                for session in self._auth_service._sessions.values():
                    if session.token == token and session.is_active:
                        session_info = SessionInfo(
                            session_id=session.session_id,
                            token=session.token,
                            created_at=datetime.fromisoformat(session.created_at),
                            expires_at=datetime.fromisoformat(session.expires_at),
                            last_activity=datetime.fromisoformat(session.last_activity),
                            ip_address=session.ip_address,
                            user_agent=session.user_agent,
                            is_active=session.is_active
                        )
                        break
            
            # Create user context
            user_context = UserContext(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                role=user.role,
                organization_id=user.org_id,
                department_id=user.dept_id,
                permissions=permission_levels,
                security_level=user.security_classification,
                is_active=user.is_active,
                session_info=session_info,
                metadata={
                    "last_login": user.last_login,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at
                }
            )
            
            return user_context
            
        except Exception as e:
            logger.error(f"Error creating user context: {e}")
            return None
    
    async def get_request_context(self, request: Request) -> RequestContext:
        """
        Create complete request context from FastAPI request.
        
        Args:
            request: FastAPI request object
            
        Returns:
            RequestContext object with all request information
        """
        await self._ensure_initialized()
        
        try:
            # Generate unique request ID
            request_id = str(uuid.uuid4())
            
            # Extract user context if authenticated
            user_context = await self.get_user_context(request)
            is_authenticated = user_context is not None
            
            # Get client information
            client = request.client
            ip_address = client.host if client else None
            user_agent = request.headers.get("User-Agent")
            
            # Extract headers (excluding sensitive ones)
            headers = dict(request.headers)
            sensitive_headers = ["authorization", "cookie", "x-api-key"]
            for header in sensitive_headers:
                if header in headers:
                    headers[header] = "[REDACTED]"
            
            # Create request context
            request_context = RequestContext(
                request_id=request_id,
                timestamp=datetime.utcnow(),
                user_context=user_context,
                is_authenticated=is_authenticated,
                authentication_method="bearer_token" if is_authenticated else None,
                ip_address=ip_address,
                user_agent=user_agent,
                headers=headers,
                query_params=dict(request.query_params),
                path_params=dict(request.path_params),
                metadata={
                    "method": request.method,
                    "url": str(request.url),
                    "path": request.url.path
                }
            )
            
            return request_context
            
        except Exception as e:
            logger.error(f"Error creating request context: {e}")
            # Return minimal request context on error
            return RequestContext(
                request_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                is_authenticated=False,
                error_message=str(e)
            )
    
    async def validate_request_auth(self, request: Request, required_permissions: List[PermissionLevel] = None) -> bool:
        """
        Validate request authentication and authorization.
        
        Args:
            request: FastAPI request object
            required_permissions: List of required permissions
            
        Returns:
            True if request is authorized, False otherwise
        """
        await self._ensure_initialized()
        
        try:
            # Get user context
            user_context = await self.get_user_context(request)
            if not user_context:
                return False
            
            # Check if user is active
            if not user_context.is_active:
                return False
            
            # If no specific permissions required, just check authentication
            if not required_permissions:
                return True
            
            # Check if user has all required permissions
            user_permissions = user_context.permissions
            for required_perm in required_permissions:
                if required_perm not in user_permissions:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating request auth: {e}")
            return False
    
    async def require_auth(self, required_permissions: List[PermissionLevel] = None):
        """
        Decorator factory for requiring authentication and permissions.
        
        Args:
            required_permissions: List of required permissions
            
        Returns:
            Decorator function
        """
        async def decorator(request: Request):
            if not await self.validate_request_auth(request, required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required or insufficient permissions"
                )
            return await self.get_user_context(request)
        
        return decorator
    
    async def get_user_permissions(self, user_id: str) -> List[str]:
        """
        Get user permissions.
        
        Args:
            user_id: User ID
            
        Returns:
            List of permission strings
        """
        await self._ensure_initialized()
        
        try:
            permissions = await self._role_service.get_user_permissions(user_id)
            return [perm.get("permission", "") for perm in permissions if perm.get("permission")]
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            return []
    
    async def check_user_permission(self, user_id: str, required_permission: str) -> bool:
        """
        Check if user has specific permission.
        
        Args:
            user_id: User ID
            required_permission: Required permission
            
        Returns:
            True if user has permission, False otherwise
        """
        await self._ensure_initialized()
        
        try:
            user_permissions = await self.get_user_permissions(user_id)
            return required_permission in user_permissions
        except Exception as e:
            logger.error(f"Error checking user permission: {e}")
            return False


# Create global instance
request_context_service = RequestContextService()


# Export the service and convenience functions
__all__ = [
    'RequestContextService',
    'request_context_service'
]
