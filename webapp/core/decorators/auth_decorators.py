"""
Authentication Decorators for AASX Digital Twin Analytics Framework
================================================================

This module provides decorators for route protection and permission enforcement.
"""

import logging
from functools import wraps
from typing import Optional, Callable, Any
from fastapi import HTTPException, Request, status, Depends
from webapp.core.context.user_context import UserContext

logger = logging.getLogger(__name__)


def require_auth(required_permission: Optional[str] = None, allow_independent: bool = True):
    """
    Decorator to require authentication and optional permission
    
    Args:
        required_permission: Optional permission required for access
        allow_independent: Whether to allow independent users (default: True)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request from args or kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                for key, value in kwargs.items():
                    if isinstance(value, Request):
                        request = value
                        break
            
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Request object not found"
                )
            
            # Get user context from request state
            user_context = getattr(request.state, 'user_context', None)
            if not user_context:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check if independent users are allowed
            if not allow_independent and user_context.is_independent:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Organization membership required"
                )
            
            # Check permission if required
            if required_permission and not user_context.has_permission(required_permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{required_permission}' required"
                )
            
            # Add user context to kwargs if not already present
            if 'user_context' not in kwargs:
                kwargs['user_context'] = user_context
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(required_role: str, allow_independent: bool = True):
    """
    Decorator to require specific role
    
    Args:
        required_role: Role required for access
        allow_independent: Whether to allow independent users (default: True)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request from args or kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                for key, value in kwargs.items():
                    if isinstance(value, Request):
                        request = value
                        break
            
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Request object not found"
                )
            
            # Get user context from request state
            user_context = getattr(request.state, 'user_context', None)
            if not user_context:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check if independent users are allowed
            if not allow_independent and user_context.is_independent:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Organization membership required"
                )
            
            # Check role
            if not user_context.has_role(required_role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role '{required_role}' required"
                )
            
            # Add user context to kwargs if not already present
            if 'user_context' not in kwargs:
                kwargs['user_context'] = user_context
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_organization(allow_independent: bool = False):
    """
    Decorator to require organization membership
    
    Args:
        allow_independent: Whether to allow independent users (default: False)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request from args or kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                for key, value in kwargs.items():
                    if isinstance(value, Request):
                        request = value
                        break
            
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Request object not found"
                )
            
            # Get user context from request state
            user_context = getattr(request.state, 'user_context', None)
            if not user_context:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check if user has organization
            if not user_context.organization_id:
                if not allow_independent:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Organization membership required"
                    )
            
            # Add user context to kwargs if not already present
            if 'user_context' not in kwargs:
                kwargs['user_context'] = user_context
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_module_access(module: str, allow_independent: bool = True):
    """
    Decorator to require access to specific module
    
    Args:
        module: Module name required for access
        allow_independent: Whether to allow independent users (default: True)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request from args or kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                for key, value in kwargs.items():
                    if isinstance(value, Request):
                        request = value
                        break
            
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Request object not found"
                )
            
            # Get user context from request state
            user_context = getattr(request.state, 'user_context', None)
            if not user_context:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check if independent users are allowed
            if not allow_independent and user_context.is_independent:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Organization membership required"
                )
            
            # Check module access
            if not user_context.can_access_module(module):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access to module '{module}' required"
                )
            
            # Add user context to kwargs if not already present
            if 'user_context' not in kwargs:
                kwargs['user_context'] = user_context
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Dependency functions for FastAPI
def get_current_user(request: Request) -> UserContext:
    """
    Dependency to get current user context
    
    Args:
        request: FastAPI request object
        
    Returns:
        UserContext: User context object
        
    Raises:
        HTTPException: If user is not authenticated
    """
    user_context = getattr(request.state, 'user_context', None)
    if not user_context:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return user_context


def require_permission(permission: str, allow_independent: bool = True):
    """
    Dependency to require specific permission
    
    Args:
        permission: Permission required
        allow_independent: Whether to allow independent users
        
    Returns:
        Callable: Dependency function
    """
    def dependency(user_context: UserContext = Depends(get_current_user)) -> UserContext:
        # Check if independent users are allowed
        if not allow_independent and user_context.is_independent:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organization membership required"
            )
        
        # Check permission
        if not user_context.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        
        return user_context
    
    return dependency


def require_role_dependency(role: str, allow_independent: bool = True):
    """
    Dependency to require specific role
    
    Args:
        role: Role required
        allow_independent: Whether to allow independent users
        
    Returns:
        Callable: Dependency function
    """
    def dependency(user_context: UserContext = Depends(get_current_user)) -> UserContext:
        # Check if independent users are allowed
        if not allow_independent and user_context.is_independent:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organization membership required"
            )
        
        # Check role
        if not user_context.has_role(role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' required"
            )
        
        return user_context
    
    return dependency


def require_organization_dependency(allow_independent: bool = False):
    """
    Dependency to require organization membership
    
    Args:
        allow_independent: Whether to allow independent users
        
    Returns:
        Callable: Dependency function
    """
    def dependency(user_context: UserContext = Depends(get_current_user)) -> UserContext:
        # Check if user has organization
        if not user_context.organization_id:
            if not allow_independent:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Organization membership required"
                )
        
        return user_context
    
    return dependency

