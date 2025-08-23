"""
Federated Learning Metrics Model
================================

Data model for federated learning metrics with integrated enterprise metrics.
Extends the engine's BaseModel for compatibility with the merged schema.
Uses pure async patterns for optimal performance.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from src.engine.models.base_model import BaseModel
from pydantic import Field, validator


class FederatedLearningMetrics(BaseModel):
    """Model for federated learning metrics with enterprise metrics"""
    
    # Primary identification
    metric_id: Optional[int] = Field(None, description="Auto-incrementing metric ID")
    registry_id: str = Field(..., description="Foreign key to federated_learning_registry")
    
    # Health Metrics
    health_score: float = Field(default=0.0, description="Health score")
    response_time_ms: float = Field(default=0.0, description="Response time in milliseconds")
    uptime_percentage: float = Field(default=0.0, description="Uptime percentage")
    error_rate: float = Field(default=0.0, description="Error rate")
    
    # FL Performance
    federation_participation_speed_sec: float = Field(default=0.0, description="Federation participation speed in seconds")
    aggregation_speed_sec: float = Field(default=0.0, description="Model aggregation speed in seconds")
    privacy_compliance_speed_sec: float = Field(default=0.0, description="Privacy compliance speed in seconds")
    
    # Resource Metrics
    cpu_usage_percent: float = Field(default=0.0, description="CPU usage percentage")
    memory_usage_percent: float = Field(default=0.0, description="Memory usage percentage")
    gpu_usage_percent: float = Field(default=0.0, description="GPU usage percentage")
    network_throughput_mbps: float = Field(default=0.0, description="Network throughput in Mbps")
    
    # Enterprise Metrics (merged from enterprise table)
    enterprise_health_score: Optional[float] = Field(None, description="Enterprise health score")
    federation_efficiency_score: Optional[float] = Field(None, description="Federation efficiency score")
    privacy_preservation_score: Optional[float] = Field(None, description="Privacy preservation score")
    quality_score: Optional[float] = Field(None, description="Model quality score")
    collaboration_effectiveness: Optional[float] = Field(None, description="Collaboration effectiveness score")
    risk_assessment_score: Optional[float] = Field(None, description="Risk assessment score")
    compliance_adherence: Optional[float] = Field(None, description="Compliance adherence score")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        validate_assignment = True
    
    @validator('health_score', 'uptime_percentage', 'error_rate', 'cpu_usage_percent', 'memory_usage_percent', 'gpu_usage_percent')
    def validate_percentage_range(cls, v):
        """Validate percentage ranges"""
        if v is not None and (v < 0.0 or v > 100.0):
            raise ValueError('Percentage must be between 0.0 and 100.0')
        return v
    
    @validator('response_time_ms', 'federation_participation_speed_sec', 'aggregation_speed_sec', 'privacy_compliance_speed_sec')
    def validate_positive_float(cls, v):
        """Validate positive float values"""
        if v is not None and v < 0.0:
            raise ValueError('Time values must be positive')
        return v
    
    async def calculate_overall_performance_score(self) -> float:
        """Calculate overall performance score (async)"""
        # Base performance metrics (40%)
        base_performance = (
            (100.0 - self.error_rate) * 0.2 +
            (100.0 - self.response_time_ms / 1000.0) * 0.1 +
            self.uptime_percentage * 0.1
        )
        
        # FL performance metrics (30%)
        fl_performance = (
            (100.0 - self.federation_participation_speed_sec / 60.0) * 0.15 +
            (100.0 - self.aggregation_speed_sec / 60.0) * 0.15
        )
        
        # Resource efficiency (20%)
        resource_efficiency = (
            (100.0 - self.cpu_usage_percent) * 0.1 +
            (100.0 - self.memory_usage_percent) * 0.1
        )
        
        # Enterprise metrics (10%)
        enterprise_score = 0.0
        if self.enterprise_health_score is not None:
            enterprise_score = self.enterprise_health_score * 0.1
        
        total_score = base_performance + fl_performance + resource_efficiency + enterprise_score
        return min(max(total_score, 0.0), 100.0)
    
    async def is_performing_well(self) -> bool:
        """Check if metrics indicate good performance (async)"""
        performance_score = await self.calculate_overall_performance_score()
        return (
            performance_score >= 70.0 and
            self.error_rate < 5.0 and
            self.uptime_percentage >= 95.0
        )
    
    async def get_resource_utilization_summary(self) -> Dict[str, Any]:
        """Get resource utilization summary (async)"""
        return {
            'cpu': {
                'usage': self.cpu_usage_percent,
                'status': 'optimal' if self.cpu_usage_percent < 70.0 else 'high' if self.cpu_usage_percent < 90.0 else 'critical'
            },
            'memory': {
                'usage': self.memory_usage_percent,
                'status': 'optimal' if self.memory_usage_percent < 70.0 else 'high' if self.memory_usage_percent < 90.0 else 'critical'
            },
            'gpu': {
                'usage': self.gpu_usage_percent,
                'status': 'optimal' if self.gpu_usage_percent < 70.0 else 'high' if self.gpu_usage_percent < 90.0 else 'critical'
            },
            'network': {
                'throughput': self.network_throughput_mbps,
                'status': 'optimal' if self.network_throughput_mbps > 100.0 else 'good' if self.network_throughput_mbps > 50.0 else 'poor'
            }
        }
    
    async def get_federation_performance_summary(self) -> Dict[str, Any]:
        """Get federation performance summary (async)"""
        return {
            'participation_speed': {
                'value': self.federation_participation_speed_sec,
                'status': 'fast' if self.federation_participation_speed_sec < 30.0 else 'normal' if self.federation_participation_speed_sec < 60.0 else 'slow'
            },
            'aggregation_speed': {
                'value': self.aggregation_speed_sec,
                'status': 'fast' if self.aggregation_speed_sec < 60.0 else 'normal' if self.aggregation_speed_sec < 120.0 else 'slow'
            },
            'privacy_compliance_speed': {
                'value': self.privacy_compliance_speed_sec,
                'status': 'fast' if self.privacy_compliance_speed_sec < 10.0 else 'normal' if self.privacy_compliance_speed_sec < 30.0 else 'slow'
            }
        }
    
    async def to_summary_dict(self) -> Dict[str, Any]:
        """Convert to summary dictionary for display (async)"""
        performance_score = await self.calculate_overall_performance_score()
        is_performing = await self.is_performing_well()
        
        return {
            'metric_id': self.metric_id,
            'registry_id': self.registry_id,
            'overall_performance_score': round(performance_score, 2),
            'health_score': round(self.health_score, 2),
            'error_rate': round(self.error_rate, 2),
            'uptime_percentage': round(self.uptime_percentage, 2),
            'response_time_ms': round(self.response_time_ms, 2),
            'cpu_usage': round(self.cpu_usage_percent, 2),
            'memory_usage': round(self.memory_usage_percent, 2),
            'is_performing_well': is_performing,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    async def update_performance_metrics(self, new_metrics: Dict[str, Any]) -> None:
        """Update performance metrics (async)"""
        # Update basic metrics
        if 'health_score' in new_metrics:
            self.health_score = new_metrics['health_score']
        if 'response_time_ms' in new_metrics:
            self.response_time_ms = new_metrics['response_time_ms']
        if 'uptime_percentage' in new_metrics:
            self.uptime_percentage = new_metrics['uptime_percentage']
        if 'error_rate' in new_metrics:
            self.error_rate = new_metrics['error_rate']
        
        # Update FL performance metrics
        if 'federation_participation_speed_sec' in new_metrics:
            self.federation_participation_speed_sec = new_metrics['federation_participation_speed_sec']
        if 'aggregation_speed_sec' in new_metrics:
            self.aggregation_speed_sec = new_metrics['aggregation_speed_sec']
        if 'privacy_compliance_speed_sec' in new_metrics:
            self.privacy_compliance_speed_sec = new_metrics['privacy_compliance_speed_sec']
        
        # Update resource metrics
        if 'cpu_usage_percent' in new_metrics:
            self.cpu_usage_percent = new_metrics['cpu_usage_percent']
        if 'memory_usage_percent' in new_metrics:
            self.memory_usage_percent = new_metrics['memory_usage_percent']
        if 'gpu_usage_percent' in new_metrics:
            self.gpu_usage_percent = new_metrics['gpu_usage_percent']
        if 'network_throughput_mbps' in new_metrics:
            self.network_throughput_mbps = new_metrics['network_throughput_mbps']
        
        # Update enterprise metrics
        if 'enterprise_health_score' in new_metrics:
            self.enterprise_health_score = new_metrics['enterprise_health_score']
        if 'federation_efficiency_score' in new_metrics:
            self.federation_efficiency_score = new_metrics['federation_efficiency_score']
        if 'privacy_preservation_score' in new_metrics:
            self.privacy_preservation_score = new_metrics['privacy_preservation_score']
        if 'quality_score' in new_metrics:
            self.quality_score = new_metrics['quality_score']
        if 'collaboration_effectiveness' in new_metrics:
            self.collaboration_effectiveness = new_metrics['collaboration_effectiveness']
        if 'risk_assessment_score' in new_metrics:
            self.risk_assessment_score = new_metrics['risk_assessment_score']
        if 'compliance_adherence' in new_metrics:
            self.compliance_adherence = new_metrics['compliance_adherence']
        
        # Update timestamp
        self.updated_at = datetime.now()
    
    async def get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations based on current metrics (async)"""
        recommendations = []
        
        # Performance recommendations
        if self.error_rate > 5.0:
            recommendations.append("High error rate detected - investigate system stability")
        if self.response_time_ms > 1000.0:
            recommendations.append("Slow response time - optimize processing pipeline")
        if self.uptime_percentage < 95.0:
            recommendations.append("Low uptime - improve system reliability")
        
        # Resource optimization
        if self.cpu_usage_percent > 80.0:
            recommendations.append("High CPU usage - consider scaling or optimization")
        if self.memory_usage_percent > 80.0:
            recommendations.append("High memory usage - optimize memory management")
        if self.gpu_usage_percent > 80.0:
            recommendations.append("High GPU usage - consider additional GPU resources")
        
        # FL performance optimization
        if self.federation_participation_speed_sec > 60.0:
            recommendations.append("Slow federation participation - optimize communication")
        if self.aggregation_speed_sec > 120.0:
            recommendations.append("Slow model aggregation - optimize aggregation algorithm")
        
        return recommendations
