"""
Core Middleware Setup

Provides basic middleware setup for FastAPI applications.
"""

import logging
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware

logger = logging.getLogger(__name__)




def setup_middleware(app: FastAPI) -> None:
    """
    Setup basic middleware for FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    try:
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure based on your needs
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Add trusted host middleware
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure based on your needs
        )
        
        # Add GZip compression middleware
        app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        logger.info("✅ Middleware setup completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to setup middleware: {e}")
        # Don't raise - allow app to continue without middleware
