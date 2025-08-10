"""
Middleware configuration for AASX Digital Twin Analytics Framework
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time
import logging
from webapp.config.settings import settings

logger = logging.getLogger(__name__)


class ForwardedHeadersMiddleware(BaseHTTPMiddleware):
    """Custom middleware to handle forwarded headers"""
    
    async def dispatch(self, request: Request, call_next):
        # Handle forwarded headers for proxy setups
        if "x-forwarded-for" in request.headers:
            request.scope["client"] = (
                request.headers["x-forwarded-for"].split(",")[0].strip(),
                request.scope["client"][1] if request.scope["client"] else None
            )
        
        if "x-forwarded-proto" in request.headers:
            request.scope["scheme"] = request.headers["x-forwarded-proto"]
        
        if "x-forwarded-host" in request.headers:
            request.scope["headers"] = [
                (b"host", request.headers["x-forwarded-host"].encode())
            ] + [
                (k, v) for k, v in request.scope["headers"] 
                if k != b"host"
            ]
        
        response = await call_next(request)
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Custom middleware for request logging"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url}")
        
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} - {process_time:.4f}s")
        
        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


def setup_middleware(app: FastAPI) -> None:
    """Setup all middleware for the FastAPI application"""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=settings.allowed_methods,
        allow_headers=settings.allowed_headers,
    )
    
    # Trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure based on your deployment
    )
    
    # Custom middleware
    app.add_middleware(ForwardedHeadersMiddleware)
    app.add_middleware(LoggingMiddleware)
    
    # Authentication middleware (should be added last to ensure it runs after other middleware)
    try:
        from webapp.core.middleware.auth_middleware import AuthMiddleware
        app.add_middleware(AuthMiddleware)
        logger.info("✅ Authentication middleware loaded")
    except ImportError as e:
        logger.warning(f"Could not load authentication middleware: {e}")
    except Exception as e:
        logger.error(f"Error loading authentication middleware: {e}") 