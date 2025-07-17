#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AASX Digital Twin Analytics Framework
Main FastAPI application for the AASX Digital Twin Analytics Framework.
"""

import os
# Set default SECRET_KEY for development
if not os.environ.get('SECRET_KEY'):
    os.environ['SECRET_KEY'] = 'dev-secret-key-change-in-production'

from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import uvicorn
import time
import json
from pathlib import Path
from datetime import datetime
import asyncio
from typing import List, Dict, Any
import sqlite3
import random

# Create FastAPI app
app = FastAPI(
    title="AASX Digital Twin Analytics Framework",
    description="A comprehensive framework for processing AASX files and building digital twin analytics with ETL, Knowledge Graph, and AI/RAG capabilities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
current_dir = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")

# Setup templates
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.analytics_subscribers: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, connection_type: str = "general"):
        await websocket.accept()
        if connection_type == "analytics":
            self.analytics_subscribers.append(websocket)
        else:
            self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket, connection_type: str = "general"):
        if connection_type == "analytics":
            if websocket in self.analytics_subscribers:
                self.analytics_subscribers.remove(websocket)
        else:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, connection_type: str = "general"):
        connections = self.analytics_subscribers if connection_type == "analytics" else self.active_connections
        for connection in connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected connections
                if connection_type == "analytics":
                    self.analytics_subscribers.remove(connection)
                else:
                    self.active_connections.remove(connection)

manager = ConnectionManager()

# Import routers from individual modules (with error handling)
ai_rag_router = None
twin_registry_router = None
certificate_manager_router = None
qi_analytics_router = None
aasx_router = None
kg_neo4j_router = None
aasx_explorer_router = None
federated_learning_router = None

try:
    from webapp.ai_rag.routes import router as ai_rag_router
    app.include_router(ai_rag_router, prefix="/ai-rag", tags=["ai-rag"])
    print("✅ AI/RAG router loaded successfully")
except Exception as e:
    print(f"⚠️  AI/RAG router failed to load: {e}")

try:
    from webapp.kg_neo4j.routes import router as kg_neo4j_router
    app.include_router(kg_neo4j_router, prefix="/kg-neo4j", tags=["kg-neo4j"])
    print("✅ Knowledge Graph router loaded successfully")
except Exception as e:
    print(f"⚠️  Knowledge Graph router failed to load: {e}")

# Import twin registry router
try:
    from webapp.twin_registry.routes import router as twin_registry_router
    print("✅ Twin Registry router imported successfully")
    app.include_router(twin_registry_router, prefix="/twin-registry", tags=["twin-registry"])
except Exception as e:
    print(f"❌ Error importing Twin Registry router: {e}")
    twin_registry_router = None

try:
    from webapp.certificate_manager.routes import router as certificate_manager_router
    app.include_router(certificate_manager_router, prefix="/certificates", tags=["certificates"])
    print("✅ Certificate Manager router loaded successfully")
except Exception as e:
    print(f"⚠️  Certificate Manager router failed to load: {e}")

try:
    from webapp.qi_analytics.routes import router as qi_analytics_router
    app.include_router(qi_analytics_router, prefix="/analytics", tags=["analytics"])
    print("✅ QI Analytics router loaded successfully")
except Exception as e:
    print(f"⚠️  QI Analytics router failed to load: {e}")

try:
    from webapp.aasx.routes import router as aasx_router
    app.include_router(aasx_router, prefix="/aasx", tags=["aasx"])
    print("✅ AASX router loaded successfully")
except Exception as e:
    print(f"⚠️  AASX router failed to load: {e}")

try:
    from webapp.aasx_explorer.routes import router as aasx_explorer_router
    app.include_router(aasx_explorer_router, prefix="/aasx-explorer", tags=["aasx-explorer"])
    print("✅ AASX Explorer router loaded successfully")
except Exception as e:
    print(f"⚠️  AASX Explorer router failed to load: {e}")

# Import federated learning router
try:
    from webapp.federated_learning.routes import router as federated_learning_router
    app.include_router(federated_learning_router, prefix="/federated-learning", tags=["federated-learning"])
    print("✅ Federated Learning router loaded successfully")
except Exception as e:
    print(f"⚠️  Federated Learning router failed to load: {e}")

# Main dashboard route
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "AASX Digital Twin Analytics Framework",
            "modules": [
                {
                    "id": "aasx-etl",
                    "name": "AASX ETL Pipeline",
                    "description": "Advanced Extract, Transform, Load pipeline with project-based organization, real-time progress tracking, and SQLite integration",
                    "url": "/aasx",
                    "icon": "⚙️",
                    "available": aasx_router is not None
                },
                {
                    "id": "kg-neo4j",
                    "name": "Knowledge Graph",
                    "description": "Neo4j knowledge graph explorer with interactive D3.js visualizations, relationship mapping, and comprehensive analytics",
                    "url": "/kg-neo4j",
                    "icon": "🕸️",
                    "available": kg_neo4j_router is not None
                },
                {
                    "id": "ai-rag",
                    "name": "AI/RAG System",
                    "description": "AI-powered analysis with multiple RAG techniques, LLM integration, and intelligent insights for digital twins",
                    "url": "/ai-rag",
                    "icon": "🤖",
                    "available": ai_rag_router is not None
                },
                {
                    "id": "twin-registry",
                    "name": "Digital Twin Registry",
                    "description": "Advanced digital twin management with real-time monitoring, performance tracking, health analytics, and AASX integration",
                    "url": "/twin-registry",
                    "icon": "🔄",
                    "available": twin_registry_router is not None
                },
                {
                    "id": "certificates",
                    "name": "Certificate Manager",
                    "description": "Digital certificates and compliance management with automated validation and security features",
                    "url": "/certificates",
                    "icon": "📜",
                    "available": certificate_manager_router is not None
                },
                {
                    "id": "analytics",
                    "name": "QI Analytics",
                    "description": "Quality Intelligence analytics with comprehensive data analysis, visualization, and reporting capabilities",
                    "url": "/analytics",
                    "icon": "📊",
                    "available": qi_analytics_router is not None
                },
                {
                    "id": "federated-learning",
                    "name": "Federated Learning",
                    "description": "Privacy-preserving collaborative AI across digital twins with cross-domain knowledge sharing and performance optimization",
                    "url": "/federated-learning",
                    "icon": "🧠",
                    "available": federated_learning_router is not None
                }
            ]
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "aasx-digital-twin-analytics-framework",
        "version": "1.0.0",
        "timestamp": time.time(),
        "modules": {
            "ai_rag": ai_rag_router is not None,
            "kg_neo4j": kg_neo4j_router is not None,
            "twin_registry": twin_registry_router is not None,
            "certificate_manager": certificate_manager_router is not None,
            "qi_analytics": qi_analytics_router is not None,
            "aasx": aasx_router is not None,
            "federated_learning": federated_learning_router is not None
        }
    }

# API status endpoint (for frontend compatibility)
@app.get("/api/status")
async def api_status():
    """API status endpoint for frontend compatibility"""
    return {
        "status": "available",
        "service": "aasx-digital-twin-analytics-framework",
        "version": "1.0.0",
        "timestamp": time.time(),
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "aasx": "/aasx",
            "kg_neo4j": "/kg-neo4j",
            "ai_rag": "/ai-rag",
            "twin_registry": "/twin-registry",
            "certificates": "/certificates",
            "analytics": "/analytics",
            "federated_learning": "/federated-learning"
        }
    }

# PyTorch status endpoint (for frontend compatibility)
@app.get("/api/pytorch/status")
async def pytorch_status():
    """PyTorch status endpoint for frontend compatibility"""
    try:
        import torch
        return {
            "status": "available",
            "pytorch_version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
            "timestamp": time.time()
        }
    except ImportError:
        return {
            "status": "unavailable",
            "error": "PyTorch not installed",
            "timestamp": time.time()
        }

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    try:
        while True:
            # Send periodic status updates
            status_data = {
                "type": "status",
                "timestamp": time.time(),
                "services": {
                    "ai_rag": ai_rag_router is not None,
                    "kg_neo4j": kg_neo4j_router is not None,
                    "twin_registry": twin_registry_router is not None,
                    "certificate_manager": certificate_manager_router is not None,
                    "qi_analytics": qi_analytics_router is not None,
                    "aasx": aasx_router is not None,
                    "federated_learning": federated_learning_router is not None
                }
            }
            await websocket.send_text(json.dumps(status_data))
            
            # Wait for 30 seconds before next update
            await asyncio.sleep(30)
            
    except WebSocketDisconnect:
        print("WebSocket client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass

# WebSocket endpoint for analytics
@app.websocket("/ws/analytics")
async def websocket_analytics_endpoint(websocket: WebSocket):
    await manager.connect(websocket, "analytics")
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "subscribe":
                # Send initial analytics data
                analytics_data = {
                    "type": "analytics_update",
                    "data": {
                        "timestamp": datetime.now().isoformat(),
                        "quality_score": 94.2 + random.uniform(-2, 2),
                        "performance_score": 87.3 + random.uniform(-3, 3),
                        "compliance_rate": 98.7 + random.uniform(-1, 1),
                        "efficiency_index": 89.1 + random.uniform(-2, 2)
                    }
                }
                await manager.send_personal_message(json.dumps(analytics_data), websocket)
            
            elif message.get("type") == "request_update":
                # Send real-time update
                update_data = {
                    "type": "analytics_update",
                    "data": {
                        "timestamp": datetime.now().isoformat(),
                        "subscriber_count": len(manager.analytics_subscribers),
                        "connected_twins": random.randint(5, 15),
                        "data_rate": random.randint(10, 50),
                        "quality_score": 94.2 + random.uniform(-2, 2),
                        "performance_score": 87.3 + random.uniform(-3, 3)
                    }
                }
                await manager.send_personal_message(json.dumps(update_data), websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, "analytics")
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, "analytics")

# WebSocket endpoint for twin registry
@app.websocket("/ws/twin-registry")
async def websocket_twin_registry_endpoint(websocket: WebSocket):
    await manager.connect(websocket, "twin-registry")
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle twin registry messages
            if message.get("type") == "subscribe":
                # Send initial twin data
                twin_data = {
                    "type": "twin_status_update",
                    "data": {
                        "timestamp": datetime.now().isoformat(),
                        "total_twins": 12,
                        "active_twins": 8,
                        "connected_twins": 6,
                        "subscriber_count": len(manager.active_connections)
                    }
                }
                await manager.send_personal_message(json.dumps(twin_data), websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, "twin-registry")
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, "twin-registry")

# Background task to send periodic updates
async def send_periodic_updates():
    while True:
        try:
            # Send analytics updates
            if manager.analytics_subscribers:
                analytics_update = {
                    "type": "analytics_update",
                    "data": {
                        "timestamp": datetime.now().isoformat(),
                        "quality_score": 94.2 + random.uniform(-2, 2),
                        "performance_score": 87.3 + random.uniform(-3, 3),
                        "compliance_rate": 98.7 + random.uniform(-1, 1),
                        "efficiency_index": 89.1 + random.uniform(-2, 2),
                        "subscriber_count": len(manager.analytics_subscribers)
                    }
                }
                await manager.broadcast(json.dumps(analytics_update), "analytics")
            
            # Send twin registry updates
            if manager.active_connections:
                twin_update = {
                    "type": "twin_status_update",
                    "data": {
                        "timestamp": datetime.now().isoformat(),
                        "total_twins": 12,
                        "active_twins": 8 + random.randint(-1, 1),
                        "connected_twins": 6 + random.randint(-1, 1),
                        "data_points": 1500 + random.randint(-50, 50),
                        "alerts": random.randint(0, 3)
                    }
                }
                await manager.broadcast(json.dumps(twin_update), "twin-registry")
                
        except Exception as e:
            print(f"Error in periodic updates: {e}")
        
        await asyncio.sleep(5)  # Send updates every 5 seconds

# Start background task
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(send_periodic_updates())

# ETL status endpoint (for frontend compatibility)
@app.get("/etl/status")
async def get_etl_status():
    """ETL pipeline status endpoint for frontend compatibility"""
    try:
        if aasx_router is None:
            return {
                "status": "unavailable",
                "error": "AASX router not loaded",
                "timestamp": time.time()
            }
        
        # Import the function from aasx routes
        from webapp.aasx.routes import get_etl_pipeline
        
        pipeline = get_etl_pipeline()
        
        # Get pipeline validation status
        validation_status = "unknown"
        try:
            validation_result = pipeline.validate_pipeline()
            validation_status = "valid" if validation_result else "invalid"
        except Exception:
            validation_status = "error"
        
        # Get pipeline stats
        stats = {}
        try:
            stats = pipeline.get_pipeline_stats()
        except Exception:
            stats = {"error": "Failed to get pipeline stats"}
        
        return {
            "status": "available",
            "pipeline": "ready",
            "validation": validation_status,
            "stats": stats,
            "timestamp": time.time()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }

# Twin Registry status endpoint (for frontend compatibility)
@app.get("/twin-registry/status")
async def get_twin_registry_status():
    """Twin registry status endpoint for frontend compatibility"""
    try:
        if twin_registry_router is None:
            return {
                "status": "unavailable",
                "error": "Twin registry router not loaded",
                "timestamp": time.time()
            }
        
        # Import the function from twin registry routes
        from webapp.twin_registry.routes import get_twin_registry_status as get_status
        
        return await get_status()
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }

# API documentation redirect
@app.get("/docs")
async def api_docs():
    """Redirect to API documentation"""
    return {"message": "API documentation available at /docs"}

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors"""
    try:
        return templates.TemplateResponse(
            "404.html",
            {
                "request": request,
                "title": "Page Not Found - AASX Digital Twin Analytics Framework"
            },
            status_code=404
        )
    except Exception:
        # Fallback to simple JSON response if template fails
        return {"error": "Page not found", "status_code": 404}

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    """Handle 500 errors"""
    try:
        return templates.TemplateResponse(
            "500.html",
            {
                "request": request,
                "title": "Internal Server Error - AASX Digital Twin Analytics Framework"
            },
            status_code=500
        )
    except Exception:
        # Fallback to simple JSON response if template fails
        return {"error": "Internal server error", "status_code": 500}

# Module-specific routes (with availability checks)
@app.get("/ai-rag", response_class=HTMLResponse)
async def ai_rag_page(request: Request):
    """AI/RAG System page"""
    if ai_rag_router is None:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "title": "AI/RAG System - Not Available",
                "error": "AI/RAG module is not available. Please check the src services.",
                "back_url": "/"
            }
        )
    
    return templates.TemplateResponse(
        "ai_rag/index.html",
        {
            "request": request,
            "title": "AI/RAG System",
            "module_name": "AI/RAG System",
            "description": "AI-powered analysis and insights for digital twins"
        }
    )

@app.get("/twin-registry", response_class=HTMLResponse)
async def twin_registry_page(request: Request):
    """Twin registry page"""
    print(f"🔍 Twin Registry page requested. Router available: {twin_registry_router is not None}")
    
    if twin_registry_router is None:
        print("❌ Twin Registry router is None, showing error page")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "title": "Digital Twin Registry - AASX Digital Twin Analytics Framework",
                "error": "Twin Registry module is not available."
            }
        )
    
    print("✅ Serving Twin Registry page")
    return templates.TemplateResponse(
        "twin_registry/index.html",
        {
            "request": request,
            "title": "Digital Twin Registry - AASX Digital Twin Analytics Framework"
        }
    )

@app.get("/twin-registry-test", response_class=HTMLResponse)
async def twin_registry_test_page(request: Request):
    """Test twin registry template"""
    print("🧪 Serving Twin Registry test page")
    return templates.TemplateResponse(
        "twin_registry/test.html",
        {
            "request": request,
            "title": "Twin Registry Test"
        }
    )

@app.get("/certificates", response_class=HTMLResponse)
async def certificates_page(request: Request):
    """Certificate manager page"""
    if certificate_manager_router is None:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "title": "Certificate Manager - AASX Digital Twin Analytics Framework",
                "error": "Certificate Manager module is not available."
            }
        )
    
    return templates.TemplateResponse(
        "certificate_manager/index.html",
        {
            "request": request,
            "title": "Certificate Manager - AASX Digital Twin Analytics Framework"
        }
    )

@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    """Analytics dashboard page"""
    if qi_analytics_router is None:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "title": "Analytics Dashboard - AASX Digital Twin Analytics Framework",
                "error": "Analytics module is not available."
            }
        )
    
    return templates.TemplateResponse(
        "qi_analytics/index.html",
        {
            "request": request,
            "title": "Analytics Dashboard - AASX Digital Twin Analytics Framework"
        }
    )

@app.get("/kg-neo4j", response_class=HTMLResponse)
async def kg_neo4j_page(request: Request):
    """Knowledge Graph page"""
    if kg_neo4j_router is None:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "title": "Knowledge Graph - AASX Digital Twin Analytics Framework",
                "error": "Knowledge Graph module is not available. Please check Neo4j connection."
            }
        )
    
    return templates.TemplateResponse(
        "kg_neo4j/index.html",
        {
            "request": request,
            "title": "Knowledge Graph - AASX Digital Twin Analytics Framework"
        }
    )

@app.get("/flowchart", response_class=HTMLResponse)
async def flowchart_page(request: Request):
    """Flowchart page showing the complete framework processing flow with tabs"""
    return templates.TemplateResponse(
        "flowchart/framework_flowchart.html",
        {
            "request": request,
            "title": "Processing Flow - AASX Digital Twin Analytics Framework"
        }
    )

@app.get("/etl-flowchart", response_class=HTMLResponse)
async def etl_flowchart_page(request: Request):
    """ETL page flowchart showing detailed user journey and system architecture"""
    return templates.TemplateResponse(
        "flowchart/etl_page_flowchart.html",
        {
            "request": request,
            "title": "ETL Page Flowchart - AASX Digital Twin Analytics Framework"
        }
    )

@app.get("/aasx-integration-flowchart", response_class=HTMLResponse)
async def aasx_integration_flowchart_page(request: Request):
    """AASX Auto Integration flowchart showing digital twin registration process"""
    return templates.TemplateResponse(
        "flowchart/aasx_integration_flowchart.html",
        {
            "request": request,
            "title": "AASX Auto Integration Flowchart - Digital Twin Analytics Framework"
        }
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
