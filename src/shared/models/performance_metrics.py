"""
Performance Metrics Model
========================

Data model for tracking system and data performance in the AAS Data Modeling framework.
"""

from typing import Optional, Dict, Any, List
from .base_model import BaseModel
from pydantic import Field
import json
import uuid
from datetime import datetime

class PerformanceMetrics(BaseModel):
    """Performance metrics model for tracking system and data performance."""
    
    metric_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique metric identifier")
    metric_type: str = Field(..., description="Type of performance metric")
    metric_name: str = Field(..., description="Specific metric name")
    metric_category: str = Field(..., description="Category of the metric")
    entity_type: Optional[str] = Field(default=None, description="Type of entity being measured")
    entity_id: Optional[str] = Field(default=None, description="ID of entity being measured")
    metric_date: str = Field(..., description="Date when metric was measured")
    
    # Metric Values
    current_value: float = Field(..., description="Current metric value")
    previous_value: Optional[float] = Field(default=None, description="Previous measurement value")
    baseline_value: Optional[float] = Field(default=None, description="Baseline/expected value")
    target_value: Optional[float] = Field(default=None, description="Target/optimal value")
    threshold_min: Optional[float] = Field(default=None, description="Minimum acceptable value")
    threshold_max: Optional[float] = Field(default=None, description="Maximum acceptable value")
    
    # Performance Analysis
    performance_score: float = Field(default=0.0, description="0-100 performance score")
    performance_status: str = Field(default="normal", description="Current performance status")
    trend_direction: str = Field(default="stable", description="Direction of performance trend")
    trend_strength: float = Field(default=0.0, description="Strength of trend (0-100)")
    
    # Alert System
    alert_enabled: bool = Field(default=True, description="Whether alerts are enabled")
    alert_threshold: Optional[float] = Field(default=None, description="Threshold for triggering alerts")
    alert_priority: str = Field(default="medium", description="Priority level for alerts")
    alert_message: Optional[str] = Field(default=None, description="Custom alert message")
    last_alert_sent: Optional[str] = Field(default=None, description="When last alert was sent")
    
    # Performance Trends
    historical_values: List[Dict[str, Any]] = Field(default_factory=list, description="Historical metric values")
    trend_analysis: Dict[str, Any] = Field(default_factory=dict, description="Trend analysis results")
    seasonality_patterns: Dict[str, Any] = Field(default_factory=dict, description="Seasonal patterns")
    anomaly_detection: Dict[str, Any] = Field(default_factory=dict, description="Anomaly detection results")
    
    # Metadata & Tracking
    metric_description: Optional[str] = Field(default=None, description="Description of what this metric measures")
    unit_of_measure: Optional[str] = Field(default=None, description="Unit of measurement")
    calculation_method: str = Field(default="automated", description="How metric is calculated")
    data_source: Optional[str] = Field(default=None, description="Source of metric data")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")
    
    # Performance tracking
    last_metric_calculation: Optional[str] = Field(default=None, description="Last metric calculation timestamp")
    calculation_frequency: str = Field(default="hourly", description="How often metric is calculated")
    
    def validate(self) -> bool:
        """Validate performance metrics."""
        valid_metric_types = ["system", "data", "user", "business", "infrastructure"]
        if self.metric_type not in valid_metric_types:
            raise ValueError(f"Metric type must be one of: {valid_metric_types}")
        
        valid_performance_statuses = ["excellent", "good", "normal", "warning", "critical", "unknown"]
        if self.performance_status not in valid_performance_statuses:
            raise ValueError(f"Performance status must be one of: {valid_performance_statuses}")
        
        valid_trend_directions = ["improving", "stable", "declining", "fluctuating"]
        if self.trend_direction not in valid_trend_directions:
            raise ValueError(f"Trend direction must be one of: {valid_trend_directions}")
        
        valid_alert_priorities = ["low", "medium", "high", "critical"]
        if self.alert_priority not in valid_alert_priorities:
            raise ValueError(f"Alert priority must be one of: {valid_alert_priorities}")
        
        valid_calculation_frequencies = ["minutely", "hourly", "daily", "weekly", "monthly", "on_demand"]
        if self.calculation_frequency not in valid_calculation_frequencies:
            raise ValueError(f"Calculation frequency must be one of: {valid_calculation_frequencies}")
        
        if not self.metric_name or not self.metric_name.strip():
            raise ValueError("Metric name is required")
        
        if not (0.0 <= self.performance_score <= 100.0):
            raise ValueError("Performance score must be between 0.0 and 100.0")
        
        if not (0.0 <= self.trend_strength <= 100.0):
            raise ValueError("Trend strength must be between 0.0 and 100.0")
        
        if len(self.metric_name) > 255:
            raise ValueError("Metric name must be less than 255 characters")
        
        if self.metric_description and len(self.metric_description) > 1000:
            raise ValueError("Metric description must be less than 1000 characters")
        
        return True
    
    def calculate_performance_score(self) -> float:
        """Calculate performance score based on current value and thresholds."""
        if self.baseline_value is None or self.target_value is None:
            return self.performance_score
        
        # Calculate score based on distance from target
        if self.current_value >= self.target_value:
            # Above target - excellent performance
            score = 100.0
        elif self.current_value >= self.baseline_value:
            # Between baseline and target - proportional score
            range_size = self.target_value - self.baseline_value
            if range_size > 0:
                progress = (self.current_value - self.baseline_value) / range_size
                score = 70.0 + (progress * 30.0)  # 70-100 range
            else:
                score = 70.0
        else:
            # Below baseline - poor performance
            if self.baseline_value > 0:
                ratio = self.current_value / self.baseline_value
                score = max(0.0, ratio * 70.0)  # 0-70 range
            else:
                score = 0.0
        
        self.performance_score = round(score, 2)
        return self.performance_score
    
    def update_performance_status(self) -> str:
        """Update performance status based on current score and thresholds."""
        if self.performance_score >= 90.0:
            status = "excellent"
        elif self.performance_score >= 80.0:
            status = "good"
        elif self.performance_score >= 60.0:
            status = "normal"
        elif self.performance_score >= 40.0:
            status = "warning"
        else:
            status = "critical"
        
        self.performance_status = status
        return status
    
    def add_historical_value(self, value: float, timestamp: str = None) -> None:
        """Add a new historical value to the metrics."""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        historical_entry = {
            "value": value,
            "timestamp": timestamp,
            "date": timestamp.split('T')[0] if 'T' in timestamp else timestamp
        }
        
        self.historical_values.append(historical_entry)
        
        # Keep only last 1000 entries
        if len(self.historical_values) > 1000:
            self.historical_values = self.historical_values[-1000:]
        
        # Update previous value
        if len(self.historical_values) > 1:
            self.previous_value = self.historical_values[-2]["value"]
    
    def calculate_trend(self) -> Dict[str, Any]:
        """Calculate trend analysis based on historical values."""
        if len(self.historical_values) < 2:
            return {"trend": "insufficient_data", "strength": 0.0, "direction": "stable"}
        
        # Calculate trend direction and strength
        recent_values = [entry["value"] for entry in self.historical_values[-10:]]  # Last 10 values
        if len(recent_values) < 2:
            return {"trend": "insufficient_data", "strength": 0.0, "direction": "stable"}
        
        # Simple linear trend calculation
        x_values = list(range(len(recent_values)))
        y_values = recent_values
        
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        if n * sum_x2 - sum_x * sum_x == 0:
            slope = 0
        else:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Determine trend direction
        if slope > 0.01:
            direction = "improving"
        elif slope < -0.01:
            direction = "declining"
        else:
            direction = "stable"
        
        # Calculate trend strength (0-100)
        if len(recent_values) >= 3:
            variance = sum((y - sum_y/n) ** 2 for y in recent_values) / n
            if variance > 0:
                trend_strength = min(100.0, abs(slope) * 100 / (variance ** 0.5))
            else:
                trend_strength = 0.0
        else:
            trend_strength = 0.0
        
        self.trend_direction = direction
        self.trend_strength = round(trend_strength, 2)
        
        return {
            "trend": "calculated",
            "strength": self.trend_strength,
            "direction": self.trend_direction,
            "slope": round(slope, 4)
        }
    
    def should_trigger_alert(self) -> bool:
        """Check if an alert should be triggered based on current value and thresholds."""
        if not self.alert_enabled or self.alert_threshold is None:
            return False
        
        # Check if current value exceeds alert threshold
        if self.threshold_max is not None and self.current_value > self.threshold_max:
            return True
        
        if self.threshold_min is not None and self.current_value < self.threshold_min:
            return True
        
        # Check if performance score is below alert threshold
        if self.alert_threshold is not None and self.performance_score < self.alert_threshold:
            return True
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = super().to_dict()
        
        # Handle JSON fields
        data['historical_values'] = json.dumps(self.historical_values) if self.historical_values else "[]"
        data['trend_analysis'] = json.dumps(self.trend_analysis) if self.trend_analysis else "{}"
        data['seasonality_patterns'] = json.dumps(self.seasonality_patterns) if self.seasonality_patterns else "{}"
        data['anomaly_detection'] = json.dumps(self.anomaly_detection) if self.anomaly_detection else "{}"
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PerformanceMetrics':
        """Create from dictionary from database."""
        # Parse JSON fields
        json_fields = ['historical_values', 'trend_analysis', 'seasonality_patterns', 'anomaly_detection']
        
        for field in json_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = json.loads(data[field])
                except json.JSONDecodeError:
                    if field == 'historical_values':
                        data[field] = []
                    else:
                        data[field] = {}
        
        return super().from_dict(data)
