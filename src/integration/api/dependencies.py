"""
FastAPI Dependencies - Integration Layer
========================================

Provides FastAPI dependency injection functions for authentication, authorization,
and user context. All dependencies are pure async and integrate with the engine.
"""

import logging
from typing import Optional, List, Annotated
from fastapi import Depends, Request, HTTPException, status

from src.engine.core.request_context import request_context_service
from src.engine.models.request_context import UserContext, PermissionLevel

logger = logging.getLogger(__name__)


async def get_current_user(request: Request) -> Optional[UserContext]:
    """
    FastAPI dependency to get current user context from request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        UserContext if authenticated, None if not authenticated
        
    Note:
        This dependency does NOT raise exceptions for unauthenticated requests.
        Use require_auth() for endpoints that require authentication.
    """
    try:
        user_context = await request_context_service.get_user_context(request)
        return user_context
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        return None


async def get_request_context(request: Request):
    """
    FastAPI dependency to get complete request context.
    
    Args:
        request: FastAPI request object
        
    Returns:
        RequestContext with all request information
    """
    try:
        return await request_context_service.get_request_context(request)
    except Exception as e:
        logger.error(f"Error getting request context: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get request context"
        )


async def require_auth(
    request: Request,
    required_permissions: Optional[List[PermissionLevel]] = None,
    allow_independent: bool = True
) -> UserContext:
    """
    FastAPI dependency that requires authentication and optionally specific permissions.
    
    Args:
        request: FastAPI request object
        required_permissions: List of required permissions (optional)
        allow_independent: Whether to allow independent users (default: True)
        
    Returns:
        UserContext if authenticated and authorized
        
    Raises:
        HTTPException: If authentication fails or insufficient permissions
    """
    try:
        # Validate authentication and authorization
        is_authorized = await request_context_service.validate_request_auth(
            request, required_permissions
        )
        
        if not is_authorized:
            if required_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {required_permissions}"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
        
        # Get user context
        user_context = await request_context_service.get_user_context(request)
        if not user_context:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
        
        return user_context
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error in require_auth dependency: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )


# Convenience dependency functions for common permission levels
async def require_read_permission(request: Request) -> UserContext:
    """Require read permission."""
    return await require_auth(request, [PermissionLevel.READ])


async def require_write_permission(request: Request) -> UserContext:
    """Require write permission."""
    return await require_auth(request, [PermissionLevel.READ, PermissionLevel.WRITE])


async def require_manage_permission(request: Request) -> UserContext:
    """Require manage permission."""
    return await require_auth(request, [PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.MANAGE])


async def require_admin_permission(request: Request) -> UserContext:
    """Require admin permission."""
    return await require_auth(request, [PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.MANAGE, PermissionLevel.ADMIN])


async def require_super_admin_permission(request: Request) -> UserContext:
    """Require super admin permission."""
    return await require_auth(request, [PermissionLevel.SUPER_ADMIN])


# Type aliases for easy use in route definitions
CurrentUser = Annotated[Optional[UserContext], Depends(get_current_user)]
RequestContext = Annotated[dict, Depends(get_request_context)]
AuthenticatedUser = Annotated[UserContext, Depends(require_auth)]
ReadUser = Annotated[UserContext, Depends(require_read_permission)]
WriteUser = Annotated[UserContext, Depends(require_write_permission)]
ManageUser = Annotated[UserContext, Depends(require_manage_permission)]
AdminUser = Annotated[UserContext, Depends(require_admin_permission)]
SuperAdminUser = Annotated[UserContext, Depends(require_super_admin_permission)]


# Export all dependencies
__all__ = [
    'get_current_user',
    'get_request_context', 
    'require_auth',
    'require_read_permission',
    'require_write_permission',
    'require_manage_permission',
    'require_admin_permission',
    'require_super_admin_permission',
    'CurrentUser',
    'RequestContext',
    'AuthenticatedUser',
    'ReadUser',
    'WriteUser',
    'ManageUser',
    'AdminUser',
    'SuperAdminUser'
]
