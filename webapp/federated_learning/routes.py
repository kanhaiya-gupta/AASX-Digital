"""
Federated Learning Routes
FastAPI router for federated learning functionality
"""

from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import os

# Import federated learning components
from src.federated_learning import FederatedLearningEngine

# Create router
router = APIRouter(tags=["federated-learning"])

# Setup templates
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

# Initialize federated learning engine
federated_engine = FederatedLearningEngine()

# Pydantic models
class FederationStartRequest(BaseModel):
    auto_start_cycles: bool = False
    cycle_interval: int = 300  # seconds

class FederationStopRequest(BaseModel):
    save_state: bool = True

class TwinPerformanceRequest(BaseModel):
    twin_id: str

@router.get("/", response_class=HTMLResponse)
async def federated_learning_dashboard(request: Request):
    """Federated learning dashboard"""
    print("🧠 Federated Learning dashboard route called")
    
    try:
        # Get federation status
        federation_status = federated_engine.get_federation_status()
        
        # Get cross-twin insights
        cross_twin_insights = federated_engine.get_cross_twin_insights()
        
        # Get twin performance data
        twin_performance = {}
        for twin_id in ['twin_1', 'twin_2', 'twin_3']:
            twin_performance[twin_id] = federated_engine.get_twin_performance(twin_id)
        
        print("🎨 Rendering federated learning template...")
        return templates.TemplateResponse(
            "federated_learning/index.html",
            {
                "request": request,
                "title": "Federated Learning - AASX Digital Twin Platform",
                "federation_status": federation_status,
                "cross_twin_insights": cross_twin_insights,
                "twin_performance": twin_performance
            }
        )
    except Exception as e:
        print(f"❌ Error in federated learning dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Federation Management Endpoints
@router.post("/api/federation/start")
async def start_federation(request: FederationStartRequest):
    """Start federated learning federation"""
    try:
        result = federated_engine.start_federation()
        return {
            "status": "success",
            "message": "Federation started successfully",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/federation/stop")
async def stop_federation(request: FederationStopRequest):
    """Stop federated learning federation"""
    try:
        result = federated_engine.stop_federation()
        return {
            "status": "success",
            "message": "Federation stopped successfully",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/federation/status")
async def get_federation_status():
    """Get federation status"""
    try:
        status = federated_engine.get_federation_status()
        return {
            "status": "success",
            "data": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Federated Learning Cycle Endpoints
@router.post("/api/federation/cycle")
async def run_federated_cycle():
    """Run one federated learning cycle"""
    try:
        result = federated_engine.run_federated_learning_cycle()
        return {
            "status": "success",
            "message": "Federated learning cycle completed",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/federation/cycles")
async def get_federation_cycles():
    """Get federation cycle history"""
    try:
        history = federated_engine.federation_server.get_federation_history()
        return {
            "status": "success",
            "data": {
                "cycles": history,
                "total_cycles": len(history)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Twin Performance Endpoints
@router.get("/api/twins/performance")
async def get_all_twin_performance():
    """Get performance data for all twins"""
    try:
        twin_performance = {}
        for twin_id in ['twin_1', 'twin_2', 'twin_3']:
            twin_performance[twin_id] = federated_engine.get_twin_performance(twin_id)
        
        return {
            "status": "success",
            "data": twin_performance
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/twins/{twin_id}/performance")
async def get_twin_performance(twin_id: str):
    """Get performance data for a specific twin"""
    try:
        performance = federated_engine.get_twin_performance(twin_id)
        return {
            "status": "success",
            "data": performance
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Cross-Twin Learning Endpoints
@router.get("/api/insights/cross-twin")
async def get_cross_twin_insights():
    """Get cross-twin learning insights"""
    try:
        insights = federated_engine.get_cross_twin_insights()
        return {
            "status": "success",
            "data": insights
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/insights/history")
async def get_insights_history():
    """Get insights history"""
    try:
        history = federated_engine.cross_twin_learning.get_insights_history()
        return {
            "status": "success",
            "data": {
                "history": history,
                "total_insights": len(history)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/insights/knowledge-graph")
async def get_knowledge_graph():
    """Get knowledge graph"""
    try:
        knowledge_graph = federated_engine.cross_twin_learning.get_knowledge_graph()
        return {
            "status": "success",
            "data": knowledge_graph
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/insights/relationships")
async def get_twin_relationships():
    """Get twin relationships"""
    try:
        relationships = federated_engine.cross_twin_learning.get_twin_relationships()
        return {
            "status": "success",
            "data": relationships
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/insights/predictions")
async def get_cross_twin_predictions():
    """Get cross-twin benefit predictions"""
    try:
        predictions = federated_engine.cross_twin_learning.predict_cross_twin_benefits()
        return {
            "status": "success",
            "data": predictions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Federation Metrics Endpoints
@router.get("/api/metrics/federation")
async def get_federation_metrics():
    """Get federation metrics"""
    try:
        metrics = federated_engine.get_federation_metrics()
        return {
            "status": "success",
            "data": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/metrics/twin-contributions")
async def get_twin_contributions():
    """Get twin contributions"""
    try:
        contributions = federated_engine.federation_server.get_twin_contributions()
        return {
            "status": "success",
            "data": contributions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Real-time Monitoring Endpoints
@router.websocket("/ws/federated-learning")
async def websocket_federated_learning(websocket: WebSocket):
    """WebSocket for real-time federated learning updates"""
    await websocket.accept()
    try:
        while True:
            # Send real-time updates
            federation_status = federated_engine.get_federation_status()
            twin_performance = {}
            for twin_id in ['twin_1', 'twin_2', 'twin_3']:
                twin_performance[twin_id] = federated_engine.get_twin_performance(twin_id)
            
            update_data = {
                "timestamp": datetime.now().isoformat(),
                "federation_status": federation_status,
                "twin_performance": twin_performance
            }
            
            await websocket.send_text(json.dumps(update_data))
            await asyncio.sleep(5)  # Update every 5 seconds
            
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}") 

# Health Check Endpoint
@router.get("/health")
async def federated_learning_health():
    """Health check for federated learning module"""
    try:
        federation_status = federated_engine.get_federation_status()
        return {
            "status": "healthy",
            "module": "federated_learning",
            "federation_active": federation_status.get('is_active', False),
            "twins_count": federation_status.get('twins_count', 0),
            "aggregation_round": federation_status.get('aggregation_round', 0),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "module": "federated_learning",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        } 