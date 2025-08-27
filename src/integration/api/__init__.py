"""
API Integration Layer
====================

Provides API gateway, middleware, rate limiting, versioning, documentation,
and other API-related services for the AAS Data Modeling Framework.

This layer handles:
- API gateway and routing
- Authentication and authorization middleware
- Rate limiting and throttling
- API versioning and compatibility
- Documentation generation
- Request/response transformation
- Health monitoring and metrics
- Security and compliance
- Performance optimization
"""

# Core API Services
from .gateway import APIGateway
from .middleware import APIMiddleware
from .rate_limiting import RateLimiter
from .versioning import APIVersioning
from .documentation import APIDocumentation
from .health_check import HealthCheckService

# FastAPI Dependencies (NEW - Added for authentication)
from .dependencies import (
    get_current_user,
    get_request_context,
    require_auth,
    require_read_permission,
    require_write_permission,
    require_manage_permission,
    require_admin_permission,
    require_super_admin_permission,
    CurrentUser,
    RequestContext,
    AuthenticatedUser,
    ReadUser,
    WriteUser,
    ManageUser,
    AdminUser,
    SuperAdminUser
)

# Version and metadata
__version__ = "2.0.0"
__author__ = "AAS Data Modeling Team"
__license__ = "MIT"
__description__ = "World-Class API Integration Layer for AAS Data Modeling Framework"

# Export all public components
__all__ = [
    # Core API Services
    "APIGateway",
    "APIMiddleware", 
    "RateLimiter",
    "APIVersioning",
    "APIDocumentation",
    "HealthCheckService",
    
    # FastAPI Dependencies (NEW)
    "get_current_user",
    "get_request_context", 
    "require_auth",
    "require_read_permission",
    "require_write_permission",
    "require_manage_permission",
    "require_admin_permission",
    "require_super_admin_permission",
    "CurrentUser",
    "RequestContext",
    "AuthenticatedUser",
    "ReadUser",
    "WriteUser",
    "ManageUser",
    "AdminUser",
    "SuperAdminUser"
]

# Initialize core services
_api_gateway = APIGateway()
_api_middleware = APIMiddleware()
_rate_limiter = RateLimiter()
_api_versioning = APIVersioning()
_api_documentation = APIDocumentation()
_health_check = HealthCheckService()

print("🚀 AAS Data Modeling Framework - API Integration Layer Initialized")
print(f"📦 Version: {__version__}")
print(f"🔌 API Gateway: {_api_gateway.__class__.__name__}")
print(f"🛡️  Middleware: {_api_middleware.__class__.__name__}")
print(f"⚡ Rate Limiter: {_rate_limiter.__class__.__name__}")
print(f"📚 Documentation: {_api_documentation.__class__.__name__}")
print(f"💚 Health Check: {_health_check.__class__.__name__}")
print("✨ Ready for enterprise-grade API operations!")
