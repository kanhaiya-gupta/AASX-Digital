#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AASX Digital Twin Analytics Framework
Main FastAPI application using modular architecture.
"""
from src.integration.app_factory import create_app_with_routers

# Create the FastAPI application with all routers (using sync version)
app = create_app_with_routers()

if __name__ == "__main__":
    import uvicorn
    from src.engine.config.settings import settings
    
    uvicorn.run(
        "app:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.reload,
        log_level=settings.logging.level.lower()
    )
