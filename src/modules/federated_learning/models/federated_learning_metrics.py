"""
Federated Learning Metrics Model
================================

Data model for federated learning metrics with integrated enterprise metrics.
Extends the engine's BaseModel for compatibility with the merged schema.
Uses pure async patterns for optimal performance.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
from src.engine.models.base_model import EngineBaseModel
from pydantic import BaseModel, Field, validator, computed_field, ConfigDict


class FederatedLearningMetrics(BaseModel):
    """Model for federated learning metrics with enterprise metrics"""
    
    model_config = ConfigDict(
        from_attributes=True,
        protected_namespaces=(),
        arbitrary_types_allowed=True,
        extra="allow",  # Allow extra fields to prevent validation errors
    )

    # Primary identification
    metric_id: Optional[int] = Field(None, description="Auto-incrementing metric ID")
    registry_id: str = Field(..., description="Foreign key to federated_learning_registry")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp for this metric")
    
    # Organizational hierarchy (REQUIRED for proper access control)
    user_id: str = Field(..., description="User who generated this metric")
    org_id: str = Field(..., description="Organization this metric belongs to")  
    dept_id: str = Field(..., description="Department for complete traceability")
    
    # Real-time Health Metrics
    health_score: int = Field(default=0, description="Health score (0-100)")
    response_time_ms: float = Field(default=0.0, description="Response time in milliseconds")
    uptime_percentage: float = Field(default=0.0, description="Uptime percentage (0.0-100.0)")
    error_rate: float = Field(default=0.0, description="Error rate (0.0-1.0)")
    
    # Federation Performance Metrics
    federation_participation_speed_sec: float = Field(default=0.0, description="Federation participation speed in seconds")
    model_aggregation_speed_sec: float = Field(default=0.0, description="Model aggregation speed in seconds")
    privacy_compliance_speed_sec: float = Field(default=0.0, description="Privacy compliance speed in seconds")
    algorithm_execution_speed_sec: float = Field(default=0.0, description="Algorithm execution speed in seconds")
    federation_efficiency: float = Field(default=0.0, description="Federation efficiency (0.0-1.0)")
    
    # Federation Management Performance (JSON)
    federation_performance: Dict[str, Any] = Field(default_factory=dict, description="Federation performance metrics")
    federation_category_performance_stats: Dict[str, Any] = Field(default_factory=dict, description="Category performance statistics")
    
    # User Interaction Metrics
    user_interaction_count: int = Field(default=0, description="Number of user interactions")
    federation_access_count: int = Field(default=0, description="Number of federation accesses")
    successful_federation_operations: int = Field(default=0, description="Successful operations")
    failed_federation_operations: int = Field(default=0, description="Failed operations")
    
    # Data Quality Metrics
    data_freshness_score: float = Field(default=0.0, description="Data freshness score (0.0-1.0)")
    data_completeness_score: float = Field(default=0.0, description="Data completeness score (0.0-1.0)")
    data_consistency_score: float = Field(default=0.0, description="Data consistency score (0.0-1.0)")
    data_accuracy_score: float = Field(default=0.0, description="Data accuracy score (0.0-1.0)")
    
    # Federation Resource Metrics
    cpu_usage_percent: float = Field(default=0.0, description="CPU usage percentage (0.0-100.0)")
    memory_usage_percent: float = Field(default=0.0, description="Memory usage percentage (0.0-100.0)")
    network_throughput_mbps: float = Field(default=0.0, description="Network throughput in Mbps")
    storage_usage_percent: float = Field(default=0.0, description="Storage usage percentage (0.0-100.0)")
    gpu_usage_percent: float = Field(default=0.0, description="GPU usage percentage (0.0-100.0)")
    
    # Federation Patterns & Analytics (JSON)
    federation_patterns: Dict[str, Any] = Field(default_factory=dict, description="Federation patterns analysis")
    resource_utilization_trends: Dict[str, Any] = Field(default_factory=dict, description="Resource utilization trends")
    user_activity: Dict[str, Any] = Field(default_factory=dict, description="User activity patterns")
    federation_operation_patterns: Dict[str, Any] = Field(default_factory=dict, description="Federation operation patterns")
    compliance_status: Dict[str, Any] = Field(default_factory=dict, description="Compliance status details")
    privacy_events: Dict[str, Any] = Field(default_factory=dict, description="Privacy events and threats")
    
    # Enterprise Metrics
    enterprise_health_score: int = Field(default=100, description="Enterprise-level health score")
    federation_efficiency_score: int = Field(default=100, description="Federation efficiency rating")
    privacy_preservation_score: int = Field(default=100, description="Privacy preservation effectiveness")
    model_quality_score: int = Field(default=100, description="Model quality assessment")
    collaboration_effectiveness: int = Field(default=100, description="Collaboration effectiveness")
    risk_assessment_score: int = Field(default=100, description="Risk assessment score")
    compliance_adherence: int = Field(default=100, description="Compliance adherence level")
    
    # Federation-Specific Metrics (JSON)
    federation_analytics: Dict[str, Any] = Field(default_factory=dict, description="Federation analytics")
    category_effectiveness: Dict[str, Any] = Field(default_factory=dict, description="Category effectiveness analysis")
    algorithm_performance: Dict[str, Any] = Field(default_factory=dict, description="Algorithm performance metrics")
    federation_size_performance_efficiency: Dict[str, Any] = Field(default_factory=dict, description="Size-based performance analysis")
    
    # Time-based Analytics
    hour_of_day: int = Field(default=0, description="Hour of day (0-23)")
    day_of_week: int = Field(default=1, description="Day of week (1-7)")
    month: int = Field(default=1, description="Month (1-12)")
    
    # Performance Trends
    federation_management_trend: float = Field(default=0.0, description="Federation management trend")
    resource_efficiency_trend: float = Field(default=0.0, description="Resource efficiency trend")
    quality_trend: float = Field(default=0.0, description="Quality metrics trend")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    
    # Computed Fields
    @computed_field
    @property
    def overall_metrics_score(self) -> float:
        """Overall metrics score based on multiple performance indicators"""
        scores = [
            self.health_score,
            (100.0 - self.error_rate * 100),
            self.uptime_percentage,
            self.federation_efficiency * 100,
            self.data_freshness_score * 100,
            self.data_completeness_score * 100
        ]
        valid_scores = [s for s in scores if s is not None and s >= 0]
        return sum(valid_scores) / len(valid_scores) if valid_scores else 0.0

    @computed_field
    @property
    def enterprise_health_status(self) -> str:
        """Enterprise health status based on comprehensive metrics"""
        if self.overall_metrics_score >= 90:
            return "excellent"
        elif self.overall_metrics_score >= 80:
            return "good"
        elif self.overall_metrics_score >= 70:
            return "healthy"
        elif self.overall_metrics_score >= 50:
            return "warning"
        else:
            return "critical"

    @computed_field
    @property
    def risk_assessment(self) -> str:
        """Risk assessment based on error rates and performance metrics"""
        if self.error_rate > 0.1 or self.health_score < 50:
            return "high"
        elif self.error_rate > 0.05 or self.health_score < 70:
            return "medium"
        else:
            return "low"

    @computed_field
    @property
    def optimization_priority(self) -> str:
        """Optimization priority based on current performance"""
        if self.overall_metrics_score < 50 or self.error_rate > 0.1:
            return "high"
        elif self.overall_metrics_score < 70:
            return "medium"
        else:
            return "low"

    @computed_field
    @property
    def maintenance_schedule(self) -> str:
        """Maintenance schedule recommendation"""
        if self.enterprise_health_status in ["critical", "warning"]:
            return "immediate"
        elif self.uptime_percentage < 95:
            return "scheduled"
        else:
            return "routine"

    @computed_field
    @property
    def system_efficiency_score(self) -> float:
        """System efficiency score based on resource utilization"""
        efficiency_factors = [
            (100.0 - self.cpu_usage_percent),
            (100.0 - self.memory_usage_percent),
            (100.0 - self.gpu_usage_percent),
            (100.0 - self.storage_usage_percent)
        ]
        return sum(efficiency_factors) / len(efficiency_factors)

    @computed_field
    @property
    def user_engagement_score(self) -> float:
        """User engagement score based on interaction metrics"""
        if self.user_interaction_count == 0:
            return 0.0
        
        success_rate = self.successful_federation_operations / max(self.user_interaction_count, 1)
        engagement_factors = [
            success_rate * 100,
            min(self.federation_access_count / 10, 100),  # Normalize to 0-100
            (100.0 - self.error_rate * 100)
        ]
        return sum(engagement_factors) / len(engagement_factors)

    @computed_field
    @property
    def federation_performance_score(self) -> float:
        """Federation performance score based on speed and efficiency metrics"""
        performance_factors = [
            max(0, 100 - self.federation_participation_speed_sec / 60 * 100),  # Normalize speed to score
            max(0, 100 - self.model_aggregation_speed_sec / 120 * 100),
            max(0, 100 - self.privacy_compliance_speed_sec / 30 * 100),
            self.federation_efficiency * 100
        ]
        return sum(performance_factors) / len(performance_factors)

    # Validators
    @validator('health_score', 'enterprise_health_score', 'federation_efficiency_score', 'privacy_preservation_score', 'model_quality_score', 'collaboration_effectiveness', 'risk_assessment_score', 'compliance_adherence')
    def validate_percentage_range(cls, v):
        """Validate percentage ranges"""
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Percentage must be between 0 and 100')
        return v
    
    @validator('uptime_percentage', 'error_rate', 'cpu_usage_percent', 'memory_usage_percent', 'gpu_usage_percent', 'storage_usage_percent')
    def validate_percentage_range_0_100(cls, v):
        """Validate percentage ranges (0.0-100.0)"""
        if v is not None and (v < 0.0 or v > 100.0):
            raise ValueError('Percentage must be between 0.0 and 100.0')
        return v
    
    @validator('data_freshness_score', 'data_completeness_score', 'data_consistency_score', 'data_accuracy_score', 'federation_efficiency')
    def validate_score_range_0_1(cls, v):
        """Validate score ranges (0.0-1.0)"""
        if v is not None and (v < 0.0 or v > 1.0):
            raise ValueError('Score must be between 0.0 and 1.0')
        return v
    
    @validator('response_time_ms', 'federation_participation_speed_sec', 'model_aggregation_speed_sec', 'privacy_compliance_speed_sec', 'algorithm_execution_speed_sec')
    def validate_positive_float(cls, v):
        """Validate positive float values"""
        if v is not None and v < 0.0:
            raise ValueError('Time values must be positive')
        return v

    @validator('hour_of_day')
    def validate_hour_of_day(cls, v):
        """Validate hour of day"""
        if v is not None and (v < 0 or v > 23):
            raise ValueError('Hour of day must be between 0 and 23')
        return v

    @validator('day_of_week')
    def validate_day_of_week(cls, v):
        """Validate day of week"""
        if v is not None and (v < 1 or v > 7):
            raise ValueError('Day of week must be between 1 and 7')
        return v

    @validator('month')
    def validate_month(cls, v):
        """Validate month"""
        if v is not None and (v < 1 or v > 12):
            raise ValueError('Month must be between 1 and 12')
        return v

    # Certificate Manager Parity Methods
    async def validate_integrity(self) -> bool:
        """Validate metrics integrity and consistency (Certificate Manager parity method)"""
        await asyncio.sleep(0.001)  # Simulate async operation
        
        try:
            # Check required fields
            if not self.registry_id:
                return False
            
            # Validate score ranges
            if not (0 <= self.health_score <= 100):
                return False
            
            if not (0.0 <= self.error_rate <= 1.0):
                return False
            
            if not (0.0 <= self.uptime_percentage <= 100.0):
                return False
            
            # Check timestamp consistency
            if self.created_at and self.updated_at and self.created_at > self.updated_at:
                return False
            
            return True
            
        except Exception:
            return False

    async def update_health_metrics(self) -> Dict[str, Any]:
        """Update health metrics based on current state (Certificate Manager parity method)"""
        await asyncio.sleep(0.001)  # Simulate async operation
        
        # Calculate new health score
        new_health_score = int(self.overall_metrics_score)
        self.health_score = new_health_score
        
        # Update timestamp
        self.updated_at = datetime.now()
        
        return {
            "health_score": new_health_score,
            "overall_metrics_score": round(self.overall_metrics_score, 2),
            "enterprise_health_status": self.enterprise_health_status,
            "updated_at": self.updated_at.isoformat()
        }

    async def generate_summary(self) -> Dict[str, Any]:
        """Generate comprehensive metrics summary (Certificate Manager parity method)"""
        await asyncio.sleep(0.001)  # Simulate async operation
        
        return {
            "metric_id": self.metric_id,
            "registry_id": self.registry_id,
            "overall_metrics_score": round(self.overall_metrics_score, 2),
            "enterprise_health_status": self.enterprise_health_status,
            "risk_assessment": self.risk_assessment,
            "optimization_priority": self.optimization_priority,
            "maintenance_schedule": self.maintenance_schedule,
            "system_efficiency_score": round(self.system_efficiency_score, 2),
            "user_engagement_score": round(self.user_engagement_score, 2),
            "federation_performance_score": round(self.federation_performance_score, 2),
            "health_score": self.health_score,
            "error_rate": round(self.error_rate, 3),
            "uptime_percentage": round(self.uptime_percentage, 2),
            "federation_efficiency": round(self.federation_efficiency, 3),
            "cpu_usage": round(self.cpu_usage_percent, 2),
            "memory_usage": round(self.memory_usage_percent, 2),
            "gpu_usage": round(self.gpu_usage_percent, 2),
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

    async def export_data(self) -> Dict[str, Any]:
        """Export metrics data for external systems (Certificate Manager parity method)"""
        await asyncio.sleep(0.001)  # Simulate async operation
        
        return {
            "federation_metrics": {
                "basic_info": {
                    "metric_id": self.metric_id,
                    "registry_id": self.registry_id,
                    "timestamp": self.timestamp.isoformat() if self.timestamp else None
                },
                "health_metrics": {
                    "health_score": self.health_score,
                    "overall_metrics_score": self.overall_metrics_score,
                    "enterprise_health_status": self.enterprise_health_status,
                    "response_time_ms": self.response_time_ms,
                    "uptime_percentage": self.uptime_percentage,
                    "error_rate": self.error_rate
                },
                "federation_performance": {
                    "federation_participation_speed_sec": self.federation_participation_speed_sec,
                    "model_aggregation_speed_sec": self.model_aggregation_speed_sec,
                    "privacy_compliance_speed_sec": self.privacy_compliance_speed_sec,
                    "algorithm_execution_speed_sec": self.algorithm_execution_speed_sec,
                    "federation_efficiency": self.federation_efficiency
                },
                "resource_metrics": {
                    "cpu_usage_percent": self.cpu_usage_percent,
                    "memory_usage_percent": self.memory_usage_percent,
                    "gpu_usage_percent": self.gpu_usage_percent,
                    "storage_usage_percent": self.storage_usage_percent,
                    "network_throughput_mbps": self.network_throughput_mbps
                },
                "data_quality_metrics": {
                    "data_freshness_score": self.data_freshness_score,
                    "data_completeness_score": self.data_completeness_score,
                    "data_consistency_score": self.data_consistency_score,
                    "data_accuracy_score": self.data_accuracy_score
                },
                "enterprise_metrics": {
                    "enterprise_health_score": self.enterprise_health_score,
                    "federation_efficiency_score": self.federation_efficiency_score,
                    "privacy_preservation_score": self.privacy_preservation_score,
                    "model_quality_score": self.model_quality_score,
                    "collaboration_effectiveness": self.collaboration_effectiveness,
                    "risk_assessment_score": self.risk_assessment_score,
                    "compliance_adherence": self.compliance_adherence
                },
                "computed_metrics": {
                    "overall_metrics_score": self.overall_metrics_score,
                    "risk_assessment": self.risk_assessment,
                    "optimization_priority": self.optimization_priority,
                    "maintenance_schedule": self.maintenance_schedule,
                    "system_efficiency_score": self.system_efficiency_score,
                    "user_engagement_score": self.user_engagement_score,
                    "federation_performance_score": self.federation_performance_score
                },
                "timestamps": {
                    "created_at": self.created_at.isoformat() if self.created_at else None,
                    "updated_at": self.updated_at.isoformat() if self.updated_at else None
                }
            }
        }

    # Additional Enterprise Methods
    async def calculate_overall_performance_score(self) -> float:
        """Calculate overall performance score (async)"""
        await asyncio.sleep(0.001)  # Simulate async operation
        
        # Base performance metrics (40%)
        base_performance = (
            (100.0 - self.error_rate * 100) * 0.2 +
            max(0, 100.0 - self.response_time_ms / 1000.0) * 0.1 +
            self.uptime_percentage * 0.1
        )
        
        # FL performance metrics (30%)
        fl_performance = (
            max(0, 100.0 - self.federation_participation_speed_sec / 60.0) * 0.15 +
            max(0, 100.0 - self.model_aggregation_speed_sec / 60.0) * 0.15
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
        await asyncio.sleep(0.001)  # Simulate async operation
        
        performance_score = await self.calculate_overall_performance_score()
        return (
            performance_score >= 70.0 and
            self.error_rate < 0.05 and
            self.uptime_percentage >= 95.0
        )

    async def get_resource_utilization_summary(self) -> Dict[str, Any]:
        """Get resource utilization summary (async)"""
        await asyncio.sleep(0.001)  # Simulate async operation
        
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
            'storage': {
                'usage': self.storage_usage_percent,
                'status': 'optimal' if self.storage_usage_percent < 70.0 else 'high' if self.storage_usage_percent < 90.0 else 'critical'
            },
            'network': {
                'throughput': self.network_throughput_mbps,
                'status': 'optimal' if self.network_throughput_mbps > 100.0 else 'good' if self.network_throughput_mbps > 50.0 else 'poor'
            }
        }

    async def get_federation_performance_summary(self) -> Dict[str, Any]:
        """Get federation performance summary (async)"""
        await asyncio.sleep(0.001)  # Simulate async operation
        
        return {
            'participation_speed': {
                'value': self.federation_participation_speed_sec,
                'status': 'fast' if self.federation_participation_speed_sec < 30.0 else 'normal' if self.federation_participation_speed_sec < 60.0 else 'slow'
            },
            'aggregation_speed': {
                'value': self.model_aggregation_speed_sec,
                'status': 'fast' if self.model_aggregation_speed_sec < 60.0 else 'normal' if self.model_aggregation_speed_sec < 120.0 else 'slow'
            },
            'privacy_compliance_speed': {
                'value': self.privacy_compliance_speed_sec,
                'status': 'fast' if self.privacy_compliance_speed_sec < 10.0 else 'normal' if self.privacy_compliance_speed_sec < 30.0 else 'slow'
            },
            'algorithm_execution_speed': {
                'value': self.algorithm_execution_speed_sec,
                'status': 'fast' if self.algorithm_execution_speed_sec < 60.0 else 'normal' if self.algorithm_execution_speed_sec < 120.0 else 'slow'
            }
        }

    async def get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations based on current metrics (async)"""
        await asyncio.sleep(0.001)  # Simulate async operation
        
        recommendations = []
        
        # Performance recommendations
        if self.error_rate > 0.05:
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
        if self.storage_usage_percent > 80.0:
            recommendations.append("High storage usage - consider cleanup or expansion")
        
        # FL performance optimization
        if self.federation_participation_speed_sec > 60.0:
            recommendations.append("Slow federation participation - optimize communication")
        if self.model_aggregation_speed_sec > 120.0:
            recommendations.append("Slow model aggregation - optimize aggregation algorithm")
        if self.privacy_compliance_speed_sec > 30.0:
            recommendations.append("Slow privacy compliance - optimize compliance checks")
        
        # Data quality optimization
        if self.data_freshness_score < 0.7:
            recommendations.append("Low data freshness - improve data update frequency")
        if self.data_completeness_score < 0.7:
            recommendations.append("Low data completeness - enhance data collection")
        
        return recommendations

    async def update_performance_metrics(self, new_metrics: Dict[str, Any]) -> None:
        """Update performance metrics (async)"""
        await asyncio.sleep(0.001)  # Simulate async operation
        
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
        if 'model_aggregation_speed_sec' in new_metrics:
            self.model_aggregation_speed_sec = new_metrics['model_aggregation_speed_sec']
        if 'privacy_compliance_speed_sec' in new_metrics:
            self.privacy_compliance_speed_sec = new_metrics['privacy_compliance_speed_sec']
        if 'algorithm_execution_speed_sec' in new_metrics:
            self.algorithm_execution_speed_sec = new_metrics['algorithm_execution_speed_sec']
        if 'federation_efficiency' in new_metrics:
            self.federation_efficiency = new_metrics['federation_efficiency']
        
        # Update resource metrics
        if 'cpu_usage_percent' in new_metrics:
            self.cpu_usage_percent = new_metrics['cpu_usage_percent']
        if 'memory_usage_percent' in new_metrics:
            self.memory_usage_percent = new_metrics['memory_usage_percent']
        if 'gpu_usage_percent' in new_metrics:
            self.gpu_usage_percent = new_metrics['gpu_usage_percent']
        if 'storage_usage_percent' in new_metrics:
            self.storage_usage_percent = new_metrics['storage_usage_percent']
        if 'network_throughput_mbps' in new_metrics:
            self.network_throughput_mbps = new_metrics['network_throughput_mbps']
        
        # Update data quality metrics
        if 'data_freshness_score' in new_metrics:
            self.data_freshness_score = new_metrics['data_freshness_score']
        if 'data_completeness_score' in new_metrics:
            self.data_completeness_score = new_metrics['data_completeness_score']
        if 'data_consistency_score' in new_metrics:
            self.data_consistency_score = new_metrics['data_consistency_score']
        if 'data_accuracy_score' in new_metrics:
            self.data_accuracy_score = new_metrics['data_accuracy_score']
        
        # Update enterprise metrics
        if 'enterprise_health_score' in new_metrics:
            self.enterprise_health_score = new_metrics['enterprise_health_score']
        if 'federation_efficiency_score' in new_metrics:
            self.federation_efficiency_score = new_metrics['federation_efficiency_score']
        if 'privacy_preservation_score' in new_metrics:
            self.privacy_preservation_score = new_metrics['privacy_preservation_score']
        if 'model_quality_score' in new_metrics:
            self.model_quality_score = new_metrics['model_quality_score']
        if 'collaboration_effectiveness' in new_metrics:
            self.collaboration_effectiveness = new_metrics['collaboration_effectiveness']
        if 'risk_assessment_score' in new_metrics:
            self.risk_assessment_score = new_metrics['risk_assessment_score']
        if 'compliance_adherence' in new_metrics:
            self.compliance_adherence = new_metrics['compliance_adherence']
        
        # Update timestamp
        self.updated_at = datetime.now()

    async def get_federation_analytics_summary(self) -> Dict[str, Any]:
        """Get comprehensive federation analytics summary"""
        await asyncio.sleep(0.001)  # Simulate async operation
        
        return {
            "performance_overview": {
                "overall_score": round(self.overall_metrics_score, 2),
                "health_status": self.enterprise_health_status,
                "risk_level": self.risk_assessment,
                "optimization_priority": self.optimization_priority
            },
            "federation_metrics": {
                "efficiency": round(self.federation_efficiency, 3),
                "participation_speed": self.federation_participation_speed_sec,
                "aggregation_speed": self.model_aggregation_speed_sec,
                "compliance_speed": self.privacy_compliance_speed_sec
            },
            "resource_utilization": {
                "cpu": f"{self.cpu_usage_percent:.1f}%",
                "memory": f"{self.memory_usage_percent:.1f}%",
                "gpu": f"{self.gpu_usage_percent:.1f}%",
                "storage": f"{self.storage_usage_percent:.1f}%"
            },
            "data_quality": {
                "freshness": round(self.data_freshness_score, 3),
                "completeness": round(self.data_completeness_score, 3),
                "consistency": round(self.data_consistency_score, 3),
                "accuracy": round(self.data_accuracy_score, 3)
            },
            "enterprise_health": {
                "enterprise_score": self.enterprise_health_score,
                "federation_efficiency": self.federation_efficiency_score,
                "privacy_preservation": self.privacy_preservation_score,
                "model_quality": self.model_quality_score
            }
        }


# Query Models for API Operations
class FederatedLearningMetricsQuery(EngineBaseModel):
    """Query model for filtering federated learning metrics"""
    
    # Basic filters
    registry_id: Optional[str] = None
    metric_id: Optional[int] = None
    
    # Performance filters
    min_health_score: Optional[int] = None
    max_health_score: Optional[int] = None
    min_overall_metrics_score: Optional[float] = None
    max_overall_metrics_score: Optional[float] = None
    
    # Resource filters
    min_cpu_usage: Optional[float] = None
    max_cpu_usage: Optional[float] = None
    min_memory_usage: Optional[float] = None
    max_memory_usage: Optional[float] = None
    min_gpu_usage: Optional[float] = None
    max_gpu_usage: Optional[float] = None
    
    # Federation performance filters
    min_federation_efficiency: Optional[float] = None
    max_federation_efficiency: Optional[float] = None
    max_participation_speed: Optional[float] = None
    max_aggregation_speed: Optional[float] = None
    
    # Data quality filters
    min_data_freshness: Optional[float] = None
    min_data_completeness: Optional[float] = None
    min_data_consistency: Optional[float] = None
    min_data_accuracy: Optional[float] = None
    
    # Enterprise filters
    min_enterprise_health: Optional[int] = None
    max_enterprise_health: Optional[int] = None
    min_privacy_preservation: Optional[int] = None
    max_privacy_preservation: Optional[int] = None
    
    # Time filters
    timestamp_after: Optional[datetime] = None
    timestamp_before: Optional[datetime] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    
    # Pagination
    limit: Optional[int] = 100
    offset: Optional[int] = 0
    sort_by: Optional[str] = "timestamp"
    sort_order: Optional[str] = "desc"


# Summary Models for Analytics
class FederatedLearningMetricsSummary(BaseModel):
    """Summary model for federated learning metrics analytics"""
    
    # Counts
    total_metrics: int
    high_performance_metrics: int
    medium_performance_metrics: int
    low_performance_metrics: int
    
    # Performance averages
    avg_health_score: float
    avg_overall_metrics_score: float
    avg_federation_efficiency: float
    avg_error_rate: float
    avg_uptime_percentage: float
    
    # Resource utilization averages
    avg_cpu_usage: float
    avg_memory_usage: float
    avg_gpu_usage: float
    avg_storage_usage: float
    
    # Federation performance averages
    avg_participation_speed: float
    avg_aggregation_speed: float
    avg_compliance_speed: float
    avg_algorithm_execution_speed: float
    
    # Data quality averages
    avg_data_freshness: float
    avg_data_completeness: float
    avg_data_consistency: float
    avg_data_accuracy: float
    
    # Enterprise metrics averages
    avg_enterprise_health: float
    avg_federation_efficiency_score: float
    avg_privacy_preservation: float
    avg_model_quality: float
    avg_collaboration_effectiveness: float
    avg_risk_assessment: float
    avg_compliance_adherence: float
    
    # Status distribution
    health_distribution: Dict[str, int]
    risk_distribution: Dict[str, int]
    optimization_priority_distribution: Dict[str, int]
    
    # Performance trends
    performance_trend: str
    resource_efficiency_trend: str
    quality_trend: str
    
    # Timestamps
    summary_generated_at: datetime
    data_from_date: Optional[datetime] = None
    data_to_date: Optional[datetime] = None
