"""
Physics Modeling Metrics Model

This model represents the unified performance metrics table with integrated
enterprise features for comprehensive tracking and analytics.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import Field, validator
from src.engine.models import BaseModel
import asyncio


class PhysicsModelingMetrics(BaseModel):
    """
    Physics Modeling Metrics Model
    
    Represents unified performance metrics with integrated enterprise features
    for comprehensive tracking, analytics, and monitoring.
    """
    
    # Core Metrics Fields
    metric_id: str = Field(..., description="Unique identifier for the metric")
    metric_name: str = Field(..., description="Name of the metric")
    metric_type: str = Field(..., description="Type of metric (performance, quality, compliance, etc.)")
    metric_category: str = Field(..., description="Category of metric (simulation, ml, validation, etc.)")
    metric_value: float = Field(..., description="Numeric value of the metric")
    metric_unit: str = Field(..., description="Unit of measurement for the metric")
    
    # Metric Context and Scope
    model_id: Optional[str] = Field(None, description="Associated physics model ID")
    ml_model_id: Optional[str] = Field(None, description="Associated ML model ID")
    simulation_id: Optional[str] = Field(None, description="Associated simulation ID")
    solver_id: Optional[str] = Field(None, description="Associated solver ID")
    plugin_id: Optional[str] = Field(None, description="Associated plugin ID")
    
    # Metric Timestamps and Lifecycle
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Metric timestamp")
    collection_date: datetime = Field(default_factory=datetime.utcnow, description="Date when metric was collected")
    valid_from: Optional[datetime] = Field(None, description="Valid from timestamp")
    valid_until: Optional[datetime] = Field(None, description="Valid until timestamp")
    
    # Metric Quality and Validation
    confidence_level: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence level (0-1)")
    data_quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Data quality score (0-1)")
    validation_status: str = Field(default="pending", description="Validation status")
    validation_notes: Optional[str] = Field(None, description="Validation notes and comments")
    
    # Enterprise Metric Features (Integrated)
    enterprise_metric_type: Optional[str] = Field(None, description="Type of enterprise metric")
    enterprise_metric_value: Optional[float] = Field(None, description="Enterprise metric value")
    enterprise_metric_timestamp: Optional[datetime] = Field(None, description="Enterprise metric timestamp")
    enterprise_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional enterprise metadata")
    
    # Compliance Tracking Features (Integrated)
    compliance_tracking_status: str = Field(default="pending", description="Compliance tracking status")
    compliance_tracking_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Compliance tracking score (0-1)")
    compliance_tracking_details: Optional[Dict[str, Any]] = Field(None, description="Compliance tracking details")
    
    # Security Metrics Features (Integrated)
    security_metrics_status: str = Field(default="pending", description="Security metrics status")
    security_metrics_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Security metrics score (0-1)")
    security_metrics_details: Optional[Dict[str, Any]] = Field(None, description="Security metrics details")
    
    # Performance Analytics Features (Integrated)
    performance_analytics_status: str = Field(default="pending", description="Performance analytics status")
    performance_analytics_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Performance analytics score (0-1)")
    performance_analytics_details: Optional[Dict[str, Any]] = Field(None, description="Performance analytics details")
    
    # Thresholds and Alerts
    warning_threshold: Optional[float] = Field(None, description="Warning threshold value")
    critical_threshold: Optional[float] = Field(None, description="Critical threshold value")
    alert_status: str = Field(default="normal", description="Current alert status")
    alert_history: List[Dict[str, Any]] = Field(default_factory=list, description="Alert history")
    
    # Metadata and Tags
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        schema_extra = {
            "example": {
                "metric_id": "simulation_performance_001",
                "metric_name": "Simulation Execution Time",
                "metric_type": "performance",
                "metric_category": "simulation",
                "metric_value": 45.2,
                "metric_unit": "seconds",
                "model_id": "structural_beam_001",
                "confidence_level": 0.95,
                "compliance_tracking_status": "compliant",
                "security_metrics_score": 0.88
            }
        }
    
    @validator('confidence_level', 'data_quality_score', 'compliance_tracking_score', 
               'security_metrics_score', 'performance_analytics_score')
    def validate_score_range(cls, v):
        """Validate score fields are within 0-1 range"""
        if v is not None and (v < 0.0 or v > 1.0):
            raise ValueError('Score must be between 0.0 and 1.0')
        return v
    
    @validator('validation_status')
    def validate_validation_status(cls, v):
        """Validate validation status"""
        valid_statuses = ['pending', 'passed', 'failed', 'warning', 'error']
        if v not in valid_statuses:
            raise ValueError(f'Validation status must be one of: {valid_statuses}')
        return v
    
    @validator('alert_status')
    def validate_alert_status(cls, v):
        """Validate alert status"""
        valid_statuses = ['normal', 'warning', 'critical', 'resolved']
        if v not in valid_statuses:
            raise ValueError(f'Alert status must be one of: {valid_statuses}')
        return v
    
    async def calculate_metric_score(self) -> float:
        """Async calculation of overall metric score"""
        await asyncio.sleep(0)  # Ensure async context
        
        # Base score from metric value and thresholds
        base_score = 0.5
        
        # Adjust based on confidence level
        if self.confidence_level:
            base_score = (base_score + self.confidence_level) / 2
        
        # Adjust based on data quality
        if self.data_quality_score:
            base_score = (base_score + self.data_quality_score) / 2
        
        # Adjust based on compliance score
        if self.compliance_tracking_score:
            base_score = (base_score + self.compliance_tracking_score) / 2
        
        # Adjust based on security score
        if self.security_metrics_score:
            base_score = (base_score + self.security_metrics_score) / 2
        
        return min(1.0, max(0.0, base_score))
    
    async def evaluate_thresholds(self) -> Dict[str, str]:
        """Async evaluation of metric thresholds"""
        await asyncio.sleep(0)  # Ensure async context
        
        threshold_results = {}
        
        # Check warning threshold
        if self.warning_threshold is not None:
            if self.metric_value >= self.warning_threshold:
                threshold_results["warning"] = "exceeded"
            else:
                threshold_results["warning"] = "normal"
        
        # Check critical threshold
        if self.critical_threshold is not None:
            if self.metric_value >= self.critical_threshold:
                threshold_results["critical"] = "exceeded"
                self.alert_status = "critical"
            else:
                threshold_results["critical"] = "normal"
        
        return threshold_results
    
    async def update_alert_status(self, new_status: str, reason: str) -> None:
        """Async update of alert status"""
        await asyncio.sleep(0)  # Ensure async context
        
        old_status = self.alert_status
        self.alert_status = new_status
        
        # Add to alert history
        self.alert_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "old_status": old_status,
            "new_status": new_status,
            "reason": reason
        })
    
    async def validate_metric_data(self) -> bool:
        """Async validation of metric data"""
        await asyncio.sleep(0)  # Ensure async context
        
        # Basic validation logic
        if not self.metric_name or not self.metric_type:
            return False
        
        # Check metric value is numeric
        if not isinstance(self.metric_value, (int, float)):
            return False
        
        # Check timestamp validity
        if self.timestamp > datetime.utcnow():
            return False
        
        # Check score ranges
        score_fields = [
            self.confidence_level, self.data_quality_score,
            self.compliance_tracking_score, self.security_metrics_score,
            self.performance_analytics_score
        ]
        
        for score in score_fields:
            if score is not None and (score < 0.0 or score > 1.0):
                return False
        
        return True
    
    async def calculate_trend_analysis(self, historical_data: List['PhysicsModelingMetrics']) -> Dict[str, Any]:
        """Async calculation of trend analysis"""
        await asyncio.sleep(0)  # Ensure async context
        
        if not historical_data:
            return {"trend": "insufficient_data", "slope": 0.0, "confidence": 0.0}
        
        # Sort by timestamp
        sorted_data = sorted(historical_data, key=lambda x: x.timestamp)
        
        # Calculate trend (simplified linear regression)
        n = len(sorted_data)
        if n < 2:
            return {"trend": "insufficient_data", "slope": 0.0, "confidence": 0.0}
        
        # Calculate slope
        x_values = [i for i in range(n)]
        y_values = [m.metric_value for m in sorted_data]
        
        # Simple linear regression
        x_mean = sum(x_values) / n
        y_mean = sum(y_values) / n
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            slope = 0.0
        else:
            slope = numerator / denominator
        
        # Determine trend
        if slope > 0.01:
            trend = "increasing"
        elif slope < -0.01:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "slope": slope,
            "confidence": min(0.9, n / 10),  # Simple confidence based on data points
            "data_points": n
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary"""
        return {
            "metric_id": self.metric_id,
            "metric_name": self.metric_name,
            "metric_type": self.metric_type,
            "metric_category": self.metric_category,
            "metric_value": self.metric_value,
            "metric_unit": self.metric_unit,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "alert_status": self.alert_status,
            "compliance_tracking_status": self.compliance_tracking_status,
            "security_metrics_score": self.security_metrics_score
        }
