"""
Authentication Middleware for AASX Digital Twin Analytics Framework
================================================================

This middleware handles authentication, authorization, and user context
for all requests across the framework.
"""

import logging
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from webapp.modules.auth.utils import get_user_from_request, get_user_permissions
from webapp.core.context.user_context import UserContext

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for authentication and authorization"""
    
    def __init__(self, app):
        super().__init__(app)
        self.public_paths = {
            "/",  # Root route - home page
            "/dashboard",  # Dashboard page
            "/api/dashboard",  # Dashboard API route (main homepage)
            "/api/twin-registry",  # Twin Registry page
            "/api/ai-rag",  # AI/RAG page
            "/api/kg-neo4j",  # Knowledge Graph page
            "/api/certificate-manager",  # Certificate Manager page
            "/api/federated-learning",  # Federated Learning page
            "/api/physics-modeling",  # Physics Modeling page
            "/api/aasx-etl",  # AASX page
            "/api/flowchart",  # Flowchart page
            "/api/auth/",  # Authentication page (correct path with trailing slash)
            "/api/auth/login",
            "/api/auth/signup", 
            "/api/auth/forgot-password",
            "/api/auth/reset-password",
            "/api/auth/check-auth",
            "/api/health",
            "/static",
            "/docs",
            "/redoc",
            "/openapi.json"
        }
        
        # Paths that require authentication but allow independent users
        self.independent_user_paths = {
            "/api/aasx-etl",
            "/api/twin-registry", 
            "/api/ai-rag",
            "/api/kg-neo4j"
        }
        
        # Paths that require organization membership
        self.organization_required_paths = {
            "/api/certificate-manager",
            "/api/federated-learning", 
            "/api/physics-modeling"
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process the request through authentication middleware"""
        
        # Debug logging
        logger.info(f"Auth middleware processing path: {request.url.path}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Full URL: {request.url}")
        
        # Skip authentication for public paths
        if self._is_public_path(request.url.path):
            logger.info(f"Path {request.url.path} is public, skipping authentication")
            response = await call_next(request)
            return response
        
        logger.info(f"Path {request.url.path} requires authentication")
        
        try:
            # Get user from request (token or session)
            user_data = self._get_user_data(request)
            
            if not user_data:
                # No authentication - create demo user for ANY unauthenticated request
                logger.info(f"Creating demo user context for unauthenticated request to {request.url.path}")
                demo_user_data = {
                    'user_id': '6bc1814c-5705-5b6e-af99-104b91962282',
                    'username': 'demo',
                    'email': 'demo@aasx-digital.de',
                    'role': 'guest',
                    'organization_id': '0451d3fa-dcca-d693-2636-7ff967e66219',
                    'permissions': ['read', 'write'],  # Demo users can read AND write
                    'is_active': True
                }
                user_context = UserContext(demo_user_data)
                request.state.user_context = user_context
                
                # Add demo user headers
                request.state.user_headers = {
                    "x-user-id": str(user_context.user_id),
                    "x-username": user_context.username,
                    "x-user-role": user_context.role,
                    "x-organization-id": str(user_context.organization_id or ""),
                    "x-user-type": user_context.get_user_type()
                }
                
                # Process the request with demo user context
                response = await call_next(request)
                
                # Add demo user context headers to response
                response.headers["X-User-ID"] = str(user_context.user_id)
                response.headers["X-User-Role"] = user_context.role
                response.headers["X-User-Type"] = user_context.get_user_type()
                response.headers["X-Demo-User"] = "true"
                
                return response
            
            # Create user context for authenticated users
            user_context = UserContext(user_data)
            
            # Check if user can access the requested path
            if not self._can_access_path(user_context, request.url.path):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
            
            # Add user context to request state
            request.state.user_context = user_context
            
            # Add user info to request headers for downstream services
            # Note: We need to be careful with headers modification
            # For now, we'll add them to the request state instead
            request.state.user_headers = {
                "x-user-id": str(user_context.user_id),
                "x-username": user_context.username,
                "x-user-role": user_context.role,
                "x-organization-id": str(user_context.organization_id or ""),
                "x-user-type": user_context.get_user_type()
            }
            
            # Process the request
            response = await call_next(request)
            
            # Add user context headers to response
            response.headers["X-User-ID"] = str(user_context.user_id)
            response.headers["X-User-Role"] = user_context.role
            response.headers["X-User-Type"] = user_context.get_user_type()
            
            return response
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Error in auth middleware: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    def _is_public_path(self, path: str) -> bool:
        """Check if the path is public (no authentication required)"""
        logger.info(f"Checking if path '{path}' is public")
        logger.info(f"Public paths: {self.public_paths}")
        
        # Check exact matches first (highest priority)
        if path in self.public_paths:
            logger.info(f"Path '{path}' found as exact match in public paths")
            return True
        
        # Check if path starts with any public path (but be more careful)
        for public_path in self.public_paths:
            # Skip empty paths and root path for startswith check
            if public_path == "/":
                logger.info(f"Skipping root path '{public_path}' for startswith check")
                continue  # Root path is handled by exact match above
            
            if path.startswith(public_path):
                # Special handling for module root paths - only exact matches are public
                # e.g., "/api/aasx-etl" is public, but "/api/aasx-etl/projects" is not
                if public_path in ["/api/aasx-etl", "/api/twin-registry", "/api/ai-rag", "/api/kg-neo4j", "/api/certificate-manager", "/api/federated-learning", "/api/physics-modeling"]:
                    # Only exact matches for module roots are public
                    if path == public_path:
                        logger.info(f"Path '{path}' is exact match for module root '{public_path}'")
                        return True
                    else:
                        logger.info(f"Path '{path}' starts with module root '{public_path}' but is not exact match - requires authentication")
                        continue
                
                # For other public paths, allow startswith
                if public_path in self.public_paths:
                    logger.info(f"Path '{path}' starts with public path '{public_path}'")
                    return True
                else:
                    logger.info(f"Path '{path}' starts with '{public_path}' but it's not in public_paths")
        
        logger.info(f"Path '{path}' is NOT public")
        return False
    
    def _get_user_data(self, request: Request) -> Optional[Dict[str, Any]]:
        """Get user data from request (token or session)"""
        try:
            # Debug: Check Authorization header
            auth_header = request.headers.get("Authorization")
            logger.info(f"🔍 Authorization header: {auth_header}")
            
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                logger.info(f"🔑 Token extracted: {token[:20]}...")
            else:
                logger.info("❌ No valid Authorization header found")
                token = None
            
            # Try to get user from request using existing auth utils
            user_data = get_user_from_request(request)
            logger.info(f"👤 User data from request: {user_data is not None}")
            
            if user_data:
                # Add permissions to user data
                user_data["permissions"] = get_user_permissions(user_data["role"])
                logger.info(f"✅ User authenticated: {user_data['username']} (role: {user_data['role']})")
                return user_data
            
            logger.warning("⚠️ No user data returned from request - will create demo user")
            return None
        except Exception as e:
            logger.error(f"Error getting user data: {e}")
            return None
    
    def _can_access_path(self, user_context: UserContext, path: str) -> bool:
        """Check if user can access the requested path"""
        
        # Super admins can access everything
        if user_context.role == "super_admin":
            return True
        
        # Check organization-required paths
        if self._is_organization_required_path(path):
            if user_context.is_independent:
                return False
            if not user_context.organization_id:
                return False
        
        # Check independent user paths
        if self._is_independent_user_path(path):
            # Independent users can access these paths
            return True
        
        # For other paths, check if user has required permissions
        required_permissions = self._get_required_permissions(path)
        if required_permissions:
            return any(user_context.has_permission(perm) for perm in required_permissions)
        
        return True
    
    def _is_organization_required_path(self, path: str) -> bool:
        """Check if path requires organization membership"""
        for org_path in self.organization_required_paths:
            if path.startswith(org_path):
                return True
        return False
    
    def _is_independent_user_path(self, path: str) -> bool:
        """Check if path allows independent users"""
        for ind_path in self.independent_user_paths:
            if path.startswith(ind_path):
                return True
        return False
    
    def _get_required_permissions(self, path: str) -> list:
        """Get required permissions for a path"""
        # Define permission requirements for different paths
        permission_map = {
            "/api/aasx-etl": ["read"],
            "/api/twin-registry": ["read"],
            "/api/ai-rag": ["read"],
            "/api/kg-neo4j": ["read"],
            "/api/certificate-manager": ["read", "write"],
            "/api/federated-learning": ["read", "write"],
            "/api/physics-modeling": ["read", "write"]
        }
        
        for path_prefix, permissions in permission_map.items():
            if path.startswith(path_prefix):
                return permissions
        
        return []
