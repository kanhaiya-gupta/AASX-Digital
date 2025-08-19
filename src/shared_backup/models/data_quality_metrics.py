"""
Data Quality Metrics Model
==========================

Data model for comprehensive quality monitoring in the AAS Data Modeling framework.
"""

from typing import Optional, Dict, Any, List
from .base_model import BaseModel
from pydantic import Field
import json
import uuid

class DataQualityMetrics(BaseModel):
    """Data quality metrics model for comprehensive quality monitoring."""
    
    quality_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique quality metrics identifier")
    entity_type: str = Field(..., description="Type of entity being measured")
    entity_id: str = Field(..., description="ID of entity being measured")
    metric_date: str = Field(..., description="Date when metrics were calculated")
    
    # Quality Dimensions (0-100 scores)
    accuracy_score: float = Field(default=0.0, description="Data accuracy score (0-100)")
    completeness_score: float = Field(default=0.0, description="Data completeness score (0-100)")
    consistency_score: float = Field(default=0.0, description="Data consistency score (0-100)")
    timeliness_score: float = Field(default=0.0, description="Data timeliness score (0-100)")
    validity_score: float = Field(default=0.0, description="Data validity score (0-100)")
    uniqueness_score: float = Field(default=0.0, description="Data uniqueness score (0-100)")
    
    # Overall Quality Score
    overall_quality_score: float = Field(default=0.0, description="Weighted average of all dimensions (0-100)")
    
    # Quality Thresholds and Status
    quality_threshold: float = Field(default=70.0, description="Minimum acceptable quality score (0-100)")
    quality_status: str = Field(default="unknown", description="Quality status classification")
    
    # Quality Issues and Details
    quality_issues: List[Dict[str, Any]] = Field(default_factory=list, description="List of quality issues found")
    quality_improvements: List[Dict[str, Any]] = Field(default_factory=list, description="Suggested improvements")
    
    # Metadata and Tracking
    quality_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional quality information")
    calculated_by: Optional[str] = Field(default=None, description="User who calculated these metrics")
    calculation_method: str = Field(default="automated", description="How metrics were calculated")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")
    
    # Performance tracking
    last_quality_check: Optional[str] = Field(default=None, description="Last quality check timestamp")
    quality_trend: Dict[str, Any] = Field(default_factory=dict, description="Quality trend over time")
    
    def validate(self) -> bool:
        """Validate data quality metrics."""
        valid_entity_types = ["file", "project", "use_case", "user", "organization"]
        if self.entity_type not in valid_entity_types:
            raise ValueError(f"Entity type must be one of: {valid_entity_types}")
        
        valid_quality_statuses = ["excellent", "good", "acceptable", "poor", "critical", "unknown"]
        if self.quality_status not in valid_quality_statuses:
            raise ValueError(f"Quality status must be one of: {valid_quality_statuses}")
        
        valid_calculation_methods = ["automated", "manual", "hybrid", "ml_based"]
        if self.calculation_method not in valid_calculation_methods:
            raise ValueError(f"Calculation method must be one of: {valid_calculation_methods}")
        
        # Validate score ranges (0-100)
        score_fields = [
            'accuracy_score', 'completeness_score', 'consistency_score',
            'timeliness_score', 'validity_score', 'uniqueness_score',
            'overall_quality_score', 'quality_threshold'
        ]
        
        for field in score_fields:
            score_value = getattr(self, field)
            if not (0.0 <= score_value <= 100.0):
                raise ValueError(f"{field} must be between 0.0 and 100.0")
        
        return True
    
    def calculate_overall_score(self) -> float:
        """Calculate overall quality score as weighted average."""
        weights = {
            'accuracy_score': 0.25,
            'completeness_score': 0.20,
            'consistency_score': 0.20,
            'timeliness_score': 0.15,
            'validity_score': 0.15,
            'uniqueness_score': 0.05
        }
        
        total_score = 0.0
        for field, weight in weights.items():
            total_score += getattr(self, field) * weight
        
        self.overall_quality_score = round(total_score, 2)
        return self.overall_quality_score
    
    def update_quality_status(self) -> str:
        """Update quality status based on overall score."""
        if self.overall_quality_score >= 90.0:
            self.quality_status = "excellent"
        elif self.overall_quality_score >= 80.0:
            self.quality_status = "good"
        elif self.overall_quality_score >= 70.0:
            self.quality_status = "acceptable"
        elif self.overall_quality_score >= 50.0:
            self.quality_status = "poor"
        else:
            self.quality_status = "critical"
        
        return self.quality_status
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = super().to_dict()
        data['quality_issues'] = json.dumps(self.quality_issues) if self.quality_issues else "[]"
        data['quality_improvements'] = json.dumps(self.quality_improvements) if self.quality_improvements else "[]"
        data['quality_metadata'] = json.dumps(self.quality_metadata) if self.quality_metadata else "{}"
        data['quality_trend'] = json.dumps(self.quality_trend) if self.quality_trend else "{}"
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataQualityMetrics':
        """Create from dictionary from database."""
        # Parse JSON fields
        json_fields = ['quality_issues', 'quality_improvements', 'quality_metadata', 'quality_trend']
        for field in json_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = json.loads(data[field])
                except json.JSONDecodeError:
                    if field in ['quality_issues', 'quality_improvements']:
                        data[field] = []
                    else:
                        data[field] = {}
        
        return super().from_dict(data)
