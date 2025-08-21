"""
Twin Registry Metrics Model

Model for twin registry metrics and performance monitoring data.
Matches our new twin_registry_metrics table schema.
"""

from src.shared.models.base_model import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid


class TwinRegistryMetrics(BaseModel):
    """Model for twin registry metrics and performance data"""
    
    # Primary Identification
    metric_id: Optional[str] = None  # Primary key
    registry_id: str                 # Reference to twin_registry table
    timestamp: datetime              # When this metric was recorded
    
    # Health & Performance Metrics
    health_score: Optional[float] = None      # Current health score (0-100)
    response_time_ms: Optional[float] = None # Response time in milliseconds
    throughput_ops_per_sec: Optional[float] = None # Throughput operations per second
    error_rate: Optional[float] = None      # Error rate (0.0-1.0)
    availability_percent: Optional[float] = None # Availability percentage
    
    # Resource Usage (JSON)
    resource_usage: Dict[str, Any] = {}      # System resource usage data
    
    # Performance Indicators (JSON)
    performance_indicators: Dict[str, Any] = {} # Performance metrics
    
    # Quality & Compliance (JSON)
    quality_metrics: Dict[str, Any] = {}     # Data quality metrics
    compliance_metrics: Dict[str, Any] = {}  # Compliance status
    security_metrics: Dict[str, Any] = {}    # Security metrics
    
    # Business Metrics (JSON)
    business_metrics: Dict[str, Any] = {}    # Business-related metrics
    custom_metrics: Dict[str, Any] = {}      # Custom application metrics
    
    # Alerts & Recommendations (JSON arrays)
    alerts: List[Dict[str, Any]] = []        # System alerts
    recommendations: List[Dict[str, Any]] = [] # Recommendations
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def create_metrics(
        cls,
        registry_id: str,
        health_score: Optional[int] = None,
        response_time_ms: Optional[float] = None,
        **kwargs
    ) -> "TwinRegistryMetrics":
        """Create new metrics entry"""
        now = datetime.now(timezone.utc)
        return cls(
            registry_id=registry_id,
            timestamp=now,
            health_score=health_score,
            response_time_ms=response_time_ms,
            **kwargs
        )
    
    def update_health_score(self, new_score: int) -> None:
        """Update health score"""
        if 0 <= new_score <= 100:
            self.health_score = new_score
            self.timestamp = datetime.now(timezone.utc)
    
    def update_performance_metrics(
        self,
        cpu: Optional[float] = None,
        memory: Optional[float] = None,
        network: Optional[float] = None,
        storage: Optional[float] = None
    ) -> None:
        """Update performance metrics"""
        if cpu is not None:
            self.cpu_usage_percent = cpu
        if memory is not None:
            self.memory_usage_percent = memory
        if network is not None:
            self.network_throughput_mbps = network
        if storage is not None:
            self.storage_usage_percent = storage
        
        self.timestamp = datetime.now(timezone.utc)
    
    def add_lifecycle_event(self, event: Dict[str, Any]) -> None:
        """Add a lifecycle event"""
        event['timestamp'] = datetime.now(timezone.utc).isoformat()
        self.lifecycle_events.append(event)
        self.timestamp = datetime.now(timezone.utc)
    
    def add_security_event(self, event: Dict[str, Any]) -> None:
        """Add a security event"""
        event['timestamp'] = datetime.now(timezone.utc).isoformat()
        self.security_events.append(event)
        self.timestamp = datetime.now(timezone.utc)
    
    def update_performance_trends(self, trends: Dict[str, Any]) -> None:
        """Update performance trends"""
        self.performance_trends.update(trends)
        self.timestamp = datetime.now(timezone.utc)
    
    def update_user_activity(self, activity: Dict[str, Any]) -> None:
        """Update user activity metrics"""
        self.user_activity.update(activity)
        self.timestamp = datetime.now(timezone.utc)
    
    def update_compliance_status(self, status: Dict[str, Any]) -> None:
        """Update compliance status"""
        self.compliance_status.update(status)
        self.timestamp = datetime.now(timezone.utc)


class MetricsQuery(BaseModel):
    """Query model for filtering metrics"""
    
    registry_id: Optional[str] = None
    start_timestamp: Optional[datetime] = None
    end_timestamp: Optional[datetime] = None
    min_health_score: Optional[int] = None
    max_health_score: Optional[int] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MetricsSummary(BaseModel):
    """Summary model for metrics statistics"""
    
    total_metrics: int
    average_health_score: float
    average_response_time: float
    metrics_by_registry: Dict[str, int]
    metrics_by_timestamp: Dict[str, int]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
