"""
API Layer Package

This package provides the external API interface for the AAS Data Modeling Engine,
including API gateway, middleware, rate limiting, versioning, documentation,
and health check capabilities.

The API layer enables:
- External module communication via RESTful endpoints
- Authentication and authorization middleware
- Rate limiting and throttling
- API versioning support
- OpenAPI/Swagger documentation
- Health monitoring endpoints
"""

from .gateway import APIGateway
from .middleware import APIMiddleware
from .rate_limiting import RateLimiter
from .versioning import APIVersioning
from .documentation import APIDocumentation
from .health_check import HealthCheckService

__version__ = "1.0.0"
__author__ = "AAS Data Modeling Team"

__all__ = [
    "APIGateway",
    "APIMiddleware", 
    "RateLimiter",
    "APIVersioning",
    "APIDocumentation",
    "HealthCheckService"
]
