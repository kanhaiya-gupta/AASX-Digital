"""
QI Analytics Routes
FastAPI router for Quality Infrastructure analytics and dashboard functionality.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import random
import os
from webapp.modules.qi_analytics.analytics_manager import analytics_manager

# Create router
router = APIRouter(prefix="/analytics", tags=["analytics"])

# Setup templates
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

# Pydantic models
class AnalyticsRequest(BaseModel):
    twin_id: str
    metric_type: str
    timeframe: str = "30d"
    filters: Optional[Dict[str, Any]] = None

class AnalyticsResponse(BaseModel):
    twin_id: str
    metric_type: str
    data: List[Dict[str, Any]]
    summary: Dict[str, Any]
    timestamp: datetime

# Mock analytics data
def generate_mock_analytics_data(twin_id: str, metric_type: str, days: int = 30):
    """Generate mock analytics data"""
    data = []
    base_date = datetime.now() - timedelta(days=days)
    
    for i in range(days):
        date = base_date + timedelta(days=i)
        
        if metric_type == "quality_metrics":
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "defect_rate": round(random.uniform(0.01, 0.05), 4),
                "throughput": round(random.uniform(85, 98), 2),
                "efficiency": round(random.uniform(0.75, 0.95), 3),
                "compliance_score": round(random.uniform(0.85, 0.99), 3)
            })
        elif metric_type == "performance_metrics":
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "uptime": round(random.uniform(0.92, 0.99), 3),
                "response_time": round(random.uniform(50, 200), 2),
                "throughput": round(random.uniform(100, 500), 2),
                "error_rate": round(random.uniform(0.001, 0.01), 4)
            })
        elif metric_type == "safety_metrics":
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "safety_score": round(random.uniform(0.90, 0.99), 3),
                "incident_count": random.randint(0, 2),
                "maintenance_score": round(random.uniform(0.80, 0.95), 3),
                "compliance_rate": round(random.uniform(0.95, 0.99), 3)
            })
    
    return data

def calculate_summary(data: List[Dict[str, Any]], metric_type: str):
    """Calculate summary statistics"""
    if not data:
        return {}
    
    # Extract numeric values (excluding date)
    numeric_keys = [k for k in data[0].keys() if k != "date"]
    
    summary = {}
    for key in numeric_keys:
        values = [item[key] for item in data if key in item]
        if values:
            summary[f"{key}_avg"] = round(sum(values) / len(values), 3)
            summary[f"{key}_min"] = round(min(values), 3)
            summary[f"{key}_max"] = round(max(values), 3)
            summary[f"{key}_trend"] = "increasing" if values[-1] > values[0] else "decreasing"
    
    return summary

@router.get("/", response_class=HTMLResponse)
async def analytics_dashboard(request: Request):
    """Analytics dashboard with comprehensive features"""
    # Generate sample data for dashboard
    quality_data = generate_mock_analytics_data("dt-001", "quality_metrics", 30)
    performance_data = generate_mock_analytics_data("dt-002", "performance_metrics", 30)
    safety_data = generate_mock_analytics_data("dt-003", "safety_metrics", 30)
    
    return templates.TemplateResponse(
        "qi_analytics/index.html",
        {
            "request": request,
            "title": "QI Analytics Dashboard - QI Digital Platform",
            "quality_data": quality_data,
            "performance_data": performance_data,
            "safety_data": safety_data,
            "quality_summary": calculate_summary(quality_data, "quality_metrics"),
            "performance_summary": calculate_summary(performance_data, "performance_metrics"),
            "safety_summary": calculate_summary(safety_data, "safety_metrics")
        }
    )

@router.get("/overview", response_class=HTMLResponse)
async def analytics_overview(request: Request):
    """Simple analytics overview page"""
    # Generate sample data for dashboard
    quality_data = generate_mock_analytics_data("dt-001", "quality_metrics", 30)
    performance_data = generate_mock_analytics_data("dt-002", "performance_metrics", 30)
    safety_data = generate_mock_analytics_data("dt-003", "safety_metrics", 30)
    
    return templates.TemplateResponse(
        "qi_analytics/index.html",
        {
            "request": request,
            "title": "QI Analytics Overview - QI Digital Platform",
            "quality_data": quality_data,
            "performance_data": performance_data,
            "safety_data": safety_data,
            "quality_summary": calculate_summary(quality_data, "quality_metrics"),
            "performance_summary": calculate_summary(performance_data, "performance_metrics"),
            "safety_summary": calculate_summary(safety_data, "safety_metrics")
        }
    )

@router.post("/api/analytics", response_model=AnalyticsResponse)
async def get_analytics(request: AnalyticsRequest):
    """
    Get analytics data for a digital twin from the analytics table.
    """
    try:
        # Parse timeframe
        if request.timeframe.endswith('d'):
            days = int(request.timeframe[:-1])
        elif request.timeframe.endswith('w'):
            days = int(request.timeframe[:-1]) * 7
        elif request.timeframe.endswith('m'):
            days = int(request.timeframe[:-1]) * 30
        else:
            days = 30
        # Fetch real data
        data = analytics_manager.get_twin_metrics(request.twin_id, request.metric_type, days)
        summary = analytics_manager.aggregate_kpis(request.metric_type, days)
        return AnalyticsResponse(
            twin_id=request.twin_id,
            metric_type=request.metric_type,
            data=data,
            summary=summary,
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/analytics/{twin_id}/{metric_type}")
async def get_analytics_by_type(twin_id: str, metric_type: str, timeframe: str = "30d"):
    """
    Get analytics data by twin ID and metric type from the analytics table.
    """
    try:
        if timeframe.endswith('d'):
            days = int(timeframe[:-1])
        elif timeframe.endswith('w'):
            days = int(timeframe[:-1]) * 7
        elif timeframe.endswith('m'):
            days = int(timeframe[:-1]) * 30
        else:
            days = 30
        data = analytics_manager.get_twin_metrics(twin_id, metric_type, days)
        summary = analytics_manager.aggregate_kpis(metric_type, days)
        return {
            "twin_id": twin_id,
            "metric_type": metric_type,
            "data": data,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/analytics/summary/{twin_id}")
async def get_analytics_summary(twin_id: str):
    """
    Get summary analytics for a digital twin from the analytics table.
    """
    try:
        # Example: get summary for quality_score and status_metric
        quality_data = analytics_manager.get_twin_metrics(twin_id, "quality_score", 30)
        status_data = analytics_manager.get_twin_metrics(twin_id, "status_metric", 30)
        summary = {
            "twin_id": twin_id,
            "quality": quality_data[-1] if quality_data else {},
            "status": status_data[-1] if status_data else {},
            "overall_score": quality_data[-1]["quality_score"] if quality_data else 0.0,
            "last_updated": datetime.now().isoformat()
        }
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/analytics/compare")
async def compare_analytics(twin_ids: str, metric_type: str = "quality_metrics", timeframe: str = "30d"):
    """Compare analytics across multiple digital twins"""
    try:
        twin_id_list = twin_ids.split(',')
        comparison_data = {}
        
        for twin_id in twin_id_list:
            data = generate_mock_analytics_data(twin_id.strip(), metric_type, 30)
            summary = calculate_summary(data, metric_type)
            comparison_data[twin_id.strip()] = {
                "data": data,
                "summary": summary
            }
        
        return {
            "comparison": comparison_data,
            "metric_type": metric_type,
            "timeframe": timeframe,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/analytics/trends/{twin_id}")
async def get_analytics_trends(twin_id: str, metric_type: str = "quality_metrics"):
    """Get trend analysis for a digital twin"""
    try:
        # Generate longer-term data for trend analysis
        data = generate_mock_analytics_data(twin_id, metric_type, 90)
        
        # Calculate trends
        trends = {}
        numeric_keys = [k for k in data[0].keys() if k != "date"]
        
        for key in numeric_keys:
            values = [item[key] for item in data if key in item]
            if len(values) >= 2:
                # Simple trend calculation
                first_half = values[:len(values)//2]
                second_half = values[len(values)//2:]
                
                first_avg = sum(first_half) / len(first_half)
                second_avg = sum(second_half) / len(second_half)
                
                if second_avg > first_avg * 1.05:
                    trends[key] = "improving"
                elif second_avg < first_avg * 0.95:
                    trends[key] = "declining"
                else:
                    trends[key] = "stable"
        
        return {
            "twin_id": twin_id,
            "metric_type": metric_type,
            "trends": trends,
            "data_points": len(data),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 