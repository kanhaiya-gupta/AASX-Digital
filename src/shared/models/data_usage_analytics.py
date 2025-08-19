"""
Data Usage Analytics Model
==========================

Data model for tracking data usage patterns and engagement in the AAS Data Modeling framework.
"""

from typing import Optional, Dict, Any, List
from .base_model import BaseModel
from pydantic import Field
import json
import uuid
from datetime import datetime

class DataUsageAnalytics(BaseModel):
    """Data usage analytics model for tracking data usage patterns and engagement."""
    
    analytics_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique analytics identifier")
    entity_type: str = Field(..., description="Type of entity being analyzed")
    entity_id: str = Field(..., description="ID of entity being analyzed")
    analytics_date: str = Field(..., description="Date when analytics were calculated")
    
    # Access Pattern Tracking
    total_accesses: int = Field(default=0, description="Total number of accesses")
    unique_users: int = Field(default=0, description="Number of unique users who accessed")
    access_frequency: float = Field(default=0.0, description="Average accesses per day")
    peak_usage_time: Optional[str] = Field(default=None, description="Time of day with highest usage")
    usage_pattern: Dict[str, Any] = Field(default_factory=dict, description="Hourly/daily/weekly usage patterns")
    
    # User Engagement Scoring
    user_engagement_score: float = Field(default=0.0, description="0-100 engagement score")
    active_users_count: int = Field(default=0, description="Number of actively engaged users")
    user_retention_rate: float = Field(default=0.0, description="User retention percentage")
    user_satisfaction_score: float = Field(default=0.0, description="User satisfaction rating")
    engagement_metrics: Dict[str, Any] = Field(default_factory=dict, description="Detailed engagement data")
    
    # Data Freshness Metrics
    last_updated: Optional[str] = Field(default=None, description="When data was last updated")
    data_age_days: int = Field(default=0, description="Age of data in days")
    freshness_score: float = Field(default=0.0, description="0-100 freshness score")
    update_frequency: float = Field(default=0.0, description="How often data is updated")
    staleness_indicators: List[str] = Field(default_factory=list, description="Indicators of stale data")
    
    # Business Value Scoring
    business_value_score: float = Field(default=0.0, description="0-100 business value score")
    roi_estimate: float = Field(default=0.0, description="Return on investment estimate")
    cost_benefit_ratio: float = Field(default=0.0, description="Cost vs benefit ratio")
    strategic_importance: str = Field(default="low", description="Strategic importance level")
    business_impact_metrics: Dict[str, Any] = Field(default_factory=dict, description="Business impact details")
    
    # Performance Metrics
    response_time_avg: float = Field(default=0.0, description="Average response time in ms")
    throughput_ops_per_sec: float = Field(default=0.0, description="Operations per second")
    error_rate: float = Field(default=0.0, description="Error rate percentage")
    performance_score: float = Field(default=0.0, description="0-100 performance score")
    performance_trends: Dict[str, Any] = Field(default_factory=dict, description="Performance over time")
    
    # Metadata & Tracking
    analytics_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional analytics information")
    calculated_by: Optional[str] = Field(default=None, description="User who calculated these analytics")
    calculation_method: str = Field(default="automated", description="How analytics were calculated")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")
    
    # Performance tracking
    last_analytics_run: Optional[str] = Field(default=None, description="Last analytics run timestamp")
    analytics_trend: Dict[str, Any] = Field(default_factory=dict, description="Analytics trend over time")
    
    def validate(self) -> bool:
        """Validate data usage analytics."""
        valid_entity_types = ["file", "project", "use_case", "user", "organization", "data_lineage", "quality_metrics"]
        if self.entity_type not in valid_entity_types:
            raise ValueError(f"Entity type must be one of: {valid_entity_types}")
        
        valid_strategic_importance = ["low", "medium", "high", "critical"]
        if self.strategic_importance not in valid_strategic_importance:
            raise ValueError(f"Strategic importance must be one of: {valid_strategic_importance}")
        
        if self.total_accesses < 0:
            raise ValueError("Total accesses cannot be negative")
        
        if self.unique_users < 0:
            raise ValueError("Unique users cannot be negative")
        
        if self.access_frequency < 0.0:
            raise ValueError("Access frequency cannot be negative")
        
        if not (0.0 <= self.user_engagement_score <= 100.0):
            raise ValueError("User engagement score must be between 0.0 and 100.0")
        
        if not (0.0 <= self.user_retention_rate <= 100.0):
            raise ValueError("User retention rate must be between 0.0 and 100.0")
        
        if not (0.0 <= self.user_satisfaction_score <= 100.0):
            raise ValueError("User satisfaction score must be between 0.0 and 100.0")
        
        if self.data_age_days < 0:
            raise ValueError("Data age days cannot be negative")
        
        if not (0.0 <= self.freshness_score <= 100.0):
            raise ValueError("Freshness score must be between 0.0 and 100.0")
        
        if self.update_frequency < 0.0:
            raise ValueError("Update frequency cannot be negative")
        
        if not (0.0 <= self.business_value_score <= 100.0):
            raise ValueError("Business value score must be between 0.0 and 100.0")
        
        if self.cost_benefit_ratio < 0.0:
            raise ValueError("Cost benefit ratio cannot be negative")
        
        if self.response_time_avg < 0.0:
            raise ValueError("Response time cannot be negative")
        
        if self.throughput_ops_per_sec < 0.0:
            raise ValueError("Throughput cannot be negative")
        
        if not (0.0 <= self.error_rate <= 100.0):
            raise ValueError("Error rate must be between 0.0 and 100.0")
        
        if not (0.0 <= self.performance_score <= 100.0):
            raise ValueError("Performance score must be between 0.0 and 100.0")
        
        return True
    
    def calculate_overall_score(self) -> float:
        """Calculate overall analytics score based on all metrics."""
        weights = {
            'user_engagement': 0.25,
            'data_freshness': 0.20,
            'business_value': 0.30,
            'performance': 0.25
        }
        
        scores = {
            'user_engagement': (self.user_engagement_score + self.user_retention_rate + self.user_satisfaction_score) / 3,
            'data_freshness': self.freshness_score,
            'business_value': self.business_value_score,
            'performance': self.performance_score
        }
        
        overall_score = sum(scores[key] * weights[key] for key in weights)
        return round(overall_score, 2)
    
    def update_usage_pattern(self, hour: int, day: str, week: str, access_count: int) -> None:
        """Update usage pattern with new access data."""
        if "hourly" not in self.usage_pattern:
            self.usage_pattern["hourly"] = {}
        if "daily" not in self.usage_pattern:
            self.usage_pattern["daily"] = {}
        if "weekly" not in self.usage_pattern:
            self.usage_pattern["weekly"] = {}
        
        # Update hourly pattern
        hour_key = str(hour).zfill(2)
        self.usage_pattern["hourly"][hour_key] = self.usage_pattern["hourly"].get(hour_key, 0) + access_count
        
        # Update daily pattern
        self.usage_pattern["daily"][day] = self.usage_pattern["daily"].get(day, 0) + access_count
        
        # Update weekly pattern
        self.usage_pattern["weekly"][week] = self.usage_pattern["weekly"].get(week, 0) + access_count
    
    def calculate_freshness_score(self) -> float:
        """Calculate data freshness score based on age and update frequency."""
        if self.data_age_days <= 1:
            base_score = 100.0
        elif self.data_age_days <= 7:
            base_score = 90.0
        elif self.data_age_days <= 30:
            base_score = 70.0
        elif self.data_age_days <= 90:
            base_score = 50.0
        else:
            base_score = 30.0
        
        # Adjust based on update frequency
        if self.update_frequency >= 1.0:  # Daily or more frequent
            frequency_bonus = 10.0
        elif self.update_frequency >= 0.14:  # Weekly or more frequent
            frequency_bonus = 5.0
        else:
            frequency_bonus = 0.0
        
        self.freshness_score = min(100.0, base_score + frequency_bonus)
        return self.freshness_score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = super().to_dict()
        
        # Handle JSON fields
        data['usage_pattern'] = json.dumps(self.usage_pattern) if self.usage_pattern else "{}"
        data['engagement_metrics'] = json.dumps(self.engagement_metrics) if self.engagement_metrics else "{}"
        data['staleness_indicators'] = json.dumps(self.staleness_indicators) if self.staleness_indicators else "[]"
        data['business_impact_metrics'] = json.dumps(self.business_impact_metrics) if self.business_impact_metrics else "{}"
        data['performance_trends'] = json.dumps(self.performance_trends) if self.performance_trends else "{}"
        data['analytics_metadata'] = json.dumps(self.analytics_metadata) if self.analytics_metadata else "{}"
        data['analytics_trend'] = json.dumps(self.analytics_trend) if self.analytics_trend else "{}"
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataUsageAnalytics':
        """Create from dictionary from database."""
        # Parse JSON fields
        json_fields = [
            'usage_pattern', 'engagement_metrics', 'staleness_indicators',
            'business_impact_metrics', 'performance_trends', 'analytics_metadata', 'analytics_trend'
        ]
        
        for field in json_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = json.loads(data[field])
                except json.JSONDecodeError:
                    if field == 'staleness_indicators':
                        data[field] = []
                    else:
                        data[field] = {}
        
        return super().from_dict(data)
