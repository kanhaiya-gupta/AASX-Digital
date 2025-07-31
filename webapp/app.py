#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AASX Digital Twin Analytics Framework
Main FastAPI application using modular architecture.
"""
from webapp.core.app_factory import create_app_with_routers

# Create the FastAPI application with all routers
app = create_app_with_routers()

if __name__ == "__main__":
    import uvicorn
    from webapp.config.settings import settings
    
    uvicorn.run(
        "app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )
