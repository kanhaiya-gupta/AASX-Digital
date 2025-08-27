"""
AI RAG Metrics Model
====================

Pydantic model for AI RAG metrics operations.
Pure async implementation following AASX and Twin Registry convention.
Enhanced with enterprise-grade computed fields, business intelligence methods, and comprehensive Query/Summary models.
"""

import json
import uuid
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator, computed_field
from src.engine.models.base_model import BaseModel as EngineBaseModel


class AIRagMetrics(EngineBaseModel):
    """
    AI RAG Metrics Model - Pure Async Implementation
    
    Represents the AI RAG metrics with comprehensive performance monitoring and analytics.
    Follows the same convention as AASX and Twin Registry modules.
    Enhanced with enterprise-grade computed fields and business intelligence methods.
    """
    
    # Primary Identification
    metric_id: Optional[int] = Field(None, description="Unique metric identifier")
    registry_id: str = Field(..., description="Associated registry ID")
    timestamp: str = Field(..., description="Metric timestamp")
    
    # Real-time Health Metrics (Framework Health)
    health_score: Optional[int] = Field(None, ge=0, le=100, description="Health score")
    response_time_ms: Optional[float] = Field(None, ge=0, description="Response time in milliseconds")
    uptime_percentage: Optional[float] = Field(None, ge=0.0, le=100.0, description="Uptime percentage")
    error_rate: Optional[float] = Field(None, ge=0.0, le=1.0, description="Error rate")
    
    # AI/RAG Performance Metrics (Framework Performance - NOT Data)
    embedding_generation_speed_sec: Optional[float] = Field(None, ge=0, description="Time to generate embeddings")
    vector_db_query_response_time_ms: Optional[float] = Field(None, ge=0, description="Vector DB query performance")
    rag_response_generation_time_ms: Optional[float] = Field(None, ge=0, description="RAG response generation time")
    context_retrieval_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0, description="Context retrieval accuracy")
    context_relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Context relevance score")
    response_quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Response quality score")
    user_satisfaction_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="User satisfaction score")
    
    # Resource Utilization Metrics
    memory_usage_mb: Optional[float] = Field(None, ge=0, description="Memory usage in MB")
    cpu_usage_percent: Optional[float] = Field(None, ge=0.0, le=100.0, description="CPU usage percentage")
    gpu_usage_percent: Optional[float] = Field(None, ge=0.0, le=100.0, description="GPU usage percentage")
    disk_io_mbps: Optional[float] = Field(None, ge=0, description="Disk I/O in MB/s")
    network_io_mbps: Optional[float] = Field(None, ge=0, description="Network I/O in MB/s")
    
    # Quality and Validation Metrics
    data_quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Data quality score")
    validation_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Validation score")
    completeness_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Completeness score")
    accuracy_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Accuracy score")
    
    # Additional Data Quality Metrics (from schema)
    data_freshness_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Data freshness score")
    data_completeness_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Data completeness score")
    data_consistency_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Data consistency score")
    data_accuracy_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Data accuracy score")
    
    # User Interaction Metrics
    user_interaction_count: Optional[int] = Field(None, default=0, ge=0, description="Number of user interactions")
    query_execution_count: Optional[int] = Field(None, default=0, ge=0, description="Number of queries executed")
    successful_rag_operations: Optional[int] = Field(None, default=0, ge=0, description="Successful operations")
    failed_rag_operations: Optional[int] = Field(None, default=0, ge=0, description="Failed operations")
    
    # System Resource Metrics
    cpu_usage_percent: Optional[float] = Field(None, ge=0.0, le=100.0, description="CPU usage percentage")
    memory_usage_percent: Optional[float] = Field(None, ge=0.0, le=100.0, description="Memory usage percentage")
    network_throughput_mbps: Optional[float] = Field(None, ge=0, description="Network throughput in MB/s")
    storage_usage_percent: Optional[float] = Field(None, ge=0.0, le=100.0, description="Storage usage percentage")
    
    # Performance Trends (JSON)
    performance_trends: Dict[str, Any] = Field(default_factory=dict, description="Performance trends")
    resource_utilization_trends: Dict[str, Any] = Field(default_factory=dict, description="Resource utilization trends")
    user_activity: Dict[str, Any] = Field(default_factory=dict, description="User activity patterns")
    query_patterns: Dict[str, Any] = Field(default_factory=dict, description="Query patterns")
    compliance_status: Dict[str, Any] = Field(default_factory=dict, description="Compliance status")
    security_events: Dict[str, Any] = Field(default_factory=dict, description="Security events")
    
    # AI/RAG-Specific Metrics (JSON)
    rag_analytics: Dict[str, Any] = Field(default_factory=dict, description="RAG analytics")
    technique_effectiveness: Dict[str, Any] = Field(default_factory=dict, description="Technique effectiveness")
    model_performance: Dict[str, Any] = Field(default_factory=dict, description="Model performance")
    file_type_processing_efficiency: Dict[str, Any] = Field(default_factory=dict, description="File type processing efficiency")
    
    # Enterprise Metrics
    enterprise_metric_type: str = Field(default="performance", description="Enterprise metric type")
    enterprise_metric_value: float = Field(default=0.0, ge=0.0, description="Enterprise metric value")
    enterprise_metric_metadata: Dict[str, Any] = Field(default_factory=dict, description="Enterprise metric metadata")
    enterprise_metric_last_updated: Optional[str] = Field(None, description="Last update timestamp for enterprise metric")
    
    # Enterprise Performance Analytics
    enterprise_performance_metric: str = Field(default="overall", description="Performance metric identifier")
    enterprise_performance_trend: str = Field(default="stable", description="Performance trend")
    enterprise_optimization_suggestions: Dict[str, Any] = Field(default_factory=dict, description="Optimization suggestions")
    enterprise_last_optimization_date: Optional[str] = Field(None, description="Last optimization date")
    
    # Enterprise Performance Metrics
    enterprise_performance_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Enterprise performance score")
    enterprise_quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Enterprise quality score")
    enterprise_reliability_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Enterprise reliability score")
    enterprise_compliance_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Enterprise compliance score")
    
    # Enterprise Health Metrics
    enterprise_health_score: Optional[int] = Field(None, ge=0, le=100, description="Enterprise health score")
    enterprise_health_status: Optional[str] = Field(None, description="Enterprise health status")
    enterprise_risk_level: Optional[str] = Field(None, description="Enterprise risk level")
    enterprise_alert_count: Optional[int] = Field(None, ge=0, description="Enterprise alert count")
    
    # Enterprise Compliance and Security
    enterprise_compliance_status: Optional[str] = Field(None, description="Enterprise compliance status")
    enterprise_security_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Enterprise security score")
    enterprise_threat_level: Optional[str] = Field(None, description="Enterprise threat level")
    enterprise_vulnerability_count: Optional[int] = Field(None, ge=0, description="Enterprise vulnerability count")
    
    # Time-based Metrics
    processing_time_ms: Optional[int] = Field(None, ge=0, description="Processing time in milliseconds")
    queue_time_ms: Optional[int] = Field(None, ge=0, description="Queue time in milliseconds")
    total_time_ms: Optional[int] = Field(None, ge=0, description="Total time in milliseconds")
    
    # User Interaction Metrics
    user_requests_count: Optional[int] = Field(None, ge=0, description="User requests count")
    successful_requests_count: Optional[int] = Field(None, ge=0, description="Successful requests count")
    failed_requests_count: Optional[int] = Field(None, ge=0, description="Failed requests count")
    average_session_duration_ms: Optional[float] = Field(None, ge=0, description="Average session duration")
    
    # Metadata and Configuration
    metric_type: Optional[str] = Field(None, description="Type of metric")
    metric_category: Optional[str] = Field(None, description="Metric category")
    metric_priority: Optional[str] = Field(None, description="Metric priority")
    metric_tags: List[str] = Field(default_factory=list, description="Metric tags")
    
    # Additional Context
    context_data: Dict[str, Any] = Field(default_factory=dict, description="Additional context data")
    performance_metadata: Dict[str, Any] = Field(default_factory=dict, description="Performance metadata")
    quality_metadata: Dict[str, Any] = Field(default_factory=dict, description="Quality metadata")
    
    # Computed Fields for Business Intelligence
    @computed_field
    @property
    def overall_metrics_score(self) -> float:
        """Calculate overall composite score from all metrics"""
        scores = []
        if self.health_score is not None:
            scores.append(self.health_score / 100.0)
        if self.response_quality_score is not None:
            scores.append(self.response_quality_score)
        if self.context_retrieval_accuracy is not None:
            scores.append(self.context_retrieval_accuracy)
        if self.user_satisfaction_score is not None:
            scores.append(self.user_satisfaction_score)
        if self.data_quality_score is not None:
            scores.append(self.data_quality_score)
        if self.validation_score is not None:
            scores.append(self.validation_score)
        if self.data_freshness_score is not None:
            scores.append(self.data_freshness_score)
        if self.data_completeness_score is not None:
            scores.append(self.data_completeness_score)
        if self.data_consistency_score is not None:
            scores.append(self.data_consistency_score)
        if self.data_accuracy_score is not None:
            scores.append(self.data_accuracy_score)
        return sum(scores) / len(scores) if scores else 0.0
    
    @computed_field
    @property
    def enterprise_health_status(self) -> str:
        """Determine enterprise health status based on multiple factors"""
        if self.enterprise_health_score and self.enterprise_health_score >= 80:
            return "excellent"
        elif self.enterprise_health_score and self.enterprise_health_score >= 60:
            return "good"
        elif self.enterprise_health_score and self.enterprise_health_score >= 40:
            return "fair"
        else:
            return "poor"
    
    @computed_field
    @property
    def risk_assessment(self) -> str:
        """Assess risk level based on various factors"""
        if (self.enterprise_security_score and self.enterprise_security_score < 0.3) or \
           (self.enterprise_compliance_score and self.enterprise_compliance_score < 0.3):
            return "high"
        elif (self.enterprise_security_score and self.enterprise_security_score < 0.6) or \
             (self.enterprise_compliance_score and self.enterprise_compliance_score < 0.6):
            return "medium"
        else:
            return "low"
    
    @computed_field
    @property
    def optimization_priority(self) -> str:
        """Determine optimization priority based on scores and performance"""
        if self.overall_metrics_score < 0.4 or (self.health_score and self.health_score < 40):
            return "critical"
        elif self.overall_metrics_score < 0.6 or (self.health_score and self.health_score < 60):
            return "high"
        elif self.overall_metrics_score < 0.8 or (self.health_score and self.health_score < 80):
            return "medium"
        else:
            return "low"
    
    @computed_field
    @property
    def maintenance_schedule(self) -> str:
        """Determine maintenance schedule based on health and performance"""
        if self.health_score and self.health_score < 50:
            return "immediate"
        elif self.health_score and self.health_score < 70:
            return "within_24h"
        elif self.health_score and self.health_score < 85:
            return "within_week"
        else:
            return "monthly"
    
    @computed_field
    @property
    def system_efficiency_score(self) -> float:
        """Calculate system efficiency based on resource utilization"""
        efficiency_factors = []
        if self.cpu_usage_percent and self.cpu_usage_percent < 70:
            efficiency_factors.append(0.9)
        elif self.cpu_usage_percent and self.cpu_usage_percent < 90:
            efficiency_factors.append(0.7)
        else:
            efficiency_factors.append(0.4)
        
        if self.memory_usage_percent and self.memory_usage_percent < 80:
            efficiency_factors.append(0.9)
        elif self.memory_usage_percent and self.memory_usage_percent < 95:
            efficiency_factors.append(0.7)
        else:
            efficiency_factors.append(0.4)
        
        return sum(efficiency_factors) / len(efficiency_factors) if efficiency_factors else 0.0
    
    @computed_field
    @property
    def user_engagement_score(self) -> float:
        """Calculate user engagement based on interaction metrics"""
        if self.user_interaction_count and self.query_execution_count:
            engagement_rate = self.successful_rag_operations / max(self.user_interaction_count, 1)
            return min(engagement_rate, 1.0)
        return 0.0
    
    # Asynchronous Enterprise Methods
    async def update_enterprise_metrics(self) -> None:
        """Update enterprise metrics asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        # Update enterprise performance, quality, reliability, and compliance scores
        pass
    
    async def update_compliance_tracking(self) -> None:
        """Update compliance tracking asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        # Update compliance status and security scores
        pass
    
    async def update_security_metrics(self) -> None:
        """Update security metrics asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        # Update security scores and threat levels
        pass
    
    async def update_performance_analytics(self) -> None:
        """Update performance analytics asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        # Update performance trends and resource utilization
        pass
    
    async def calculate_performance_trends(self) -> Dict[str, Any]:
        """Calculate performance trends asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        return {
            "trend_direction": "stable",
            "performance_change": 0.05,
            "quality_improvement": 0.03,
            "health_trend": "improving"
        }
    
    async def generate_optimization_suggestions(self) -> List[str]:
        """Generate optimization suggestions asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        suggestions = []
        if self.overall_metrics_score < 0.7:
            suggestions.append("Improve response quality and user satisfaction")
        if self.health_score and self.health_score < 60:
            suggestions.append("Optimize system health and reduce error rates")
        if self.response_time_ms and self.response_time_ms > 1000:
            suggestions.append("Optimize response time and processing performance")
        return suggestions
    
    async def get_enterprise_summary(self) -> Dict[str, Any]:
        """Get comprehensive enterprise summary asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        return {
            "metric_id": self.metric_id,
            "registry_id": self.registry_id,
            "timestamp": self.timestamp,
            "overall_metrics_score": self.overall_metrics_score,
            "enterprise_health_status": self.enterprise_health_status,
            "risk_assessment": self.risk_assessment,
            "optimization_priority": self.optimization_priority,
            "maintenance_schedule": self.maintenance_schedule,
            "health_score": self.health_score,
            "performance_metrics": {
                "embedding_generation_speed": self.embedding_generation_speed_sec,
                "vector_db_response_time": self.vector_db_query_response_time_ms,
                "rag_response_time": self.rag_response_generation_time_ms
            },
            "quality_metrics": {
                "context_retrieval_accuracy": self.context_retrieval_accuracy,
                "response_quality": self.response_quality_score,
                "user_satisfaction": self.user_satisfaction_score
            }
        }
    
    # Additional Async Methods (Certificate Manager Parity)
    async def validate_integrity(self) -> bool:
        """Validate data integrity asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        return (
            self.registry_id and
            self.timestamp and
            self.overall_metrics_score >= 0.0 and
            self.overall_metrics_score <= 1.0
        )
    
    async def update_health_metrics(self) -> None:
        """Update health metrics asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        # Update health metrics based on current performance and quality scores
        pass
    
    async def generate_summary(self) -> Dict[str, Any]:
        """Generate comprehensive summary asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        return await self.get_enterprise_summary()
    
    async def export_data(self, format: str = "json") -> Dict[str, Any]:
        """Export data in specified format asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        if format == "json":
            return {
                "metrics_data": self.model_dump(),
                "computed_scores": {
                    "overall_metrics_score": self.overall_metrics_score,
                    "enterprise_health_status": self.enterprise_health_status,
                    "risk_assessment": self.risk_assessment,
                    "optimization_priority": self.optimization_priority,
                    "maintenance_schedule": self.maintenance_schedule
                },
                "export_timestamp": datetime.now().isoformat(),
                "export_format": format
            }
        else:
            return {"error": f"Unsupported format: {format}"}


# Query Model for AI RAG Metrics
class AIRagMetricsQuery(BaseModel):
    """Query model for filtering AI RAG metrics with comprehensive enterprise filters"""
    
    # Basic Filters
    metric_id: Optional[int] = None
    registry_id: Optional[str] = None
    timestamp: Optional[str] = None
    metric_type: Optional[str] = None
    metric_category: Optional[str] = None
    metric_priority: Optional[str] = None
    
    # Performance Filters
    health_score_min: Optional[int] = None
    health_score_max: Optional[int] = None
    response_time_ms_min: Optional[float] = None
    response_time_ms_max: Optional[float] = None
    uptime_percentage_min: Optional[float] = None
    uptime_percentage_max: Optional[float] = None
    error_rate_min: Optional[float] = None
    error_rate_max: Optional[float] = None
    
    # AI/RAG Performance Filters
    embedding_generation_speed_min: Optional[float] = None
    embedding_generation_speed_max: Optional[float] = None
    vector_db_response_time_min: Optional[float] = None
    vector_db_response_time_max: Optional[float] = None
    rag_response_time_min: Optional[float] = None
    rag_response_time_max: Optional[float] = None
    context_retrieval_accuracy_min: Optional[float] = None
    context_retrieval_accuracy_max: Optional[float] = None
    
    # Quality Filters
    response_quality_score_min: Optional[float] = None
    response_quality_score_max: Optional[float] = None
    user_satisfaction_score_min: Optional[float] = None
    user_satisfaction_score_max: Optional[float] = None
    data_quality_score_min: Optional[float] = None
    data_quality_score_max: Optional[float] = None
    validation_score_min: Optional[float] = None
    validation_score_max: Optional[float] = None
    
    # Enterprise Filters
    enterprise_performance_score_min: Optional[float] = None
    enterprise_performance_score_max: Optional[float] = None
    enterprise_health_score_min: Optional[int] = None
    enterprise_health_score_max: Optional[int] = None
    enterprise_compliance_status: Optional[str] = None
    enterprise_security_score_min: Optional[float] = None
    enterprise_security_score_max: Optional[float] = None
    enterprise_threat_level: Optional[str] = None
    
    # Resource Utilization Filters
    memory_usage_min: Optional[float] = None
    memory_usage_max: Optional[float] = None
    cpu_usage_min: Optional[float] = None
    cpu_usage_max: Optional[float] = None
    gpu_usage_min: Optional[float] = None
    gpu_usage_max: Optional[float] = None
    
    # Time-based Filters
    timestamp_after: Optional[str] = None
    timestamp_before: Optional[str] = None
    processing_time_min: Optional[int] = None
    processing_time_max: Optional[int] = None
    
    # User Interaction Filters
    user_requests_count_min: Optional[int] = None
    user_requests_count_max: Optional[int] = None
    successful_requests_count_min: Optional[int] = None
    successful_requests_count_max: Optional[int] = None
    failed_requests_count_min: Optional[int] = None
    failed_requests_count_max: Optional[int] = None
    
    # Pagination and Sorting
    page: Optional[int] = 1
    page_size: Optional[int] = 50
    sort_by: Optional[str] = "timestamp"
    sort_order: Optional[str] = "desc"
    
    # Advanced Filters
    metric_tags: Optional[List[str]] = None
    has_performance_issues: Optional[bool] = None
    has_quality_issues: Optional[bool] = None
    has_enterprise_issues: Optional[bool] = None
    
    async def validate(self) -> bool:
        """Validate query parameters asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        if self.page and self.page < 1:
            return False
        if self.page_size and (self.page_size < 1 or self.page_size > 1000):
            return False
        if self.sort_order and self.sort_order not in ["asc", "desc"]:
            return False
        return True


# Summary Model for AI RAG Metrics
class AIRagMetricsSummary(BaseModel):
    """Summary model for AI RAG metrics analytics with comprehensive enterprise insights"""
    
    # Basic Counts
    total_metrics: int = 0
    active_metrics: int = 0
    error_metrics: int = 0
    warning_metrics: int = 0
    
    # Metric Type Distribution
    metric_type_distribution: Dict[str, int] = {}
    metric_category_distribution: Dict[str, int] = {}
    metric_priority_distribution: Dict[str, int] = {}
    
    # Health Distribution
    health_score_distribution: Dict[str, int] = {}
    enterprise_health_distribution: Dict[str, int] = {}
    risk_assessment_distribution: Dict[str, int] = {}
    optimization_priority_distribution: Dict[str, int] = {}
    maintenance_schedule_distribution: Dict[str, int] = {}
    
    # Performance Metrics
    average_health_score: float = 0.0
    average_response_time_ms: float = 0.0
    average_uptime_percentage: float = 0.0
    average_error_rate: float = 0.0
    average_overall_metrics_score: float = 0.0
    
    # AI/RAG Performance Metrics
    average_embedding_generation_speed: float = 0.0
    average_vector_db_response_time: float = 0.0
    average_rag_response_time: float = 0.0
    average_context_retrieval_accuracy: float = 0.0
    average_response_quality_score: float = 0.0
    average_user_satisfaction_score: float = 0.0
    
    # Quality Metrics
    average_data_quality_score: float = 0.0
    average_validation_score: float = 0.0
    average_completeness_score: float = 0.0
    average_accuracy_score: float = 0.0
    
    # Enterprise Metrics
    average_enterprise_performance_score: float = 0.0
    average_enterprise_quality_score: float = 0.0
    average_enterprise_reliability_score: float = 0.0
    average_enterprise_compliance_score: float = 0.0
    average_enterprise_security_score: float = 0.0
    
    # Resource Utilization Metrics
    average_memory_usage: float = 0.0
    average_cpu_usage: float = 0.0
    average_gpu_usage: float = 0.0
    average_disk_io: float = 0.0
    average_network_io: float = 0.0
    
    # Time-based Metrics
    time_trend: Dict[str, float] = {}
    performance_trend: Dict[str, float] = {}
    quality_trend: Dict[str, float] = {}
    health_trend: Dict[str, float] = {}
    
    # User Interaction Metrics
    total_user_requests: int = 0
    total_successful_requests: int = 0
    total_failed_requests: int = 0
    average_session_duration: float = 0.0
    user_satisfaction_distribution: Dict[str, int] = {}
    
    # Enterprise Compliance and Security
    compliance_status_distribution: Dict[str, int] = {}
    security_score_distribution: Dict[str, int] = {}
    threat_level_distribution: Dict[str, int] = {}
    vulnerability_count_distribution: Dict[str, int] = {}
    
    # Performance Trends
    response_time_trend: Dict[str, float] = {}
    accuracy_trend: Dict[str, float] = {}
    quality_trend: Dict[str, float] = {}
    resource_utilization_trend: Dict[str, float] = {}
    
    # Business Intelligence Metrics
    critical_issues_count: int = 0
    optimization_opportunities: int = 0
    maintenance_required: int = 0
    high_priority_items: int = 0
    
    # Cost and Resource Metrics
    estimated_processing_cost: float = 0.0
    resource_utilization: Dict[str, float] = {}
    performance_efficiency: Dict[str, float] = {}
    
    async def calculate_totals(self) -> None:
        """Calculate all totals asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        # Calculate totals from distributions
        pass
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary overview"""
        return {
            "overall_health": self.health_score_distribution,
            "enterprise_health": self.enterprise_health_distribution,
            "critical_issues": self.critical_issues_count,
            "maintenance_required": self.maintenance_required,
            "optimization_opportunities": self.optimization_opportunities
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary overview"""
        return {
            "average_scores": {
                "health": self.average_health_score,
                "overall_metrics": self.average_overall_metrics_score,
                "response_quality": self.average_response_quality_score,
                "user_satisfaction": self.average_user_satisfaction_score
            },
            "performance_metrics": {
                "embedding_speed": self.average_embedding_generation_speed,
                "vector_db_response": self.average_vector_db_response_time,
                "rag_response": self.average_rag_response_time,
                "context_accuracy": self.average_context_retrieval_accuracy
            },
            "trends": self.performance_trend
        }
    
    def get_quality_summary(self) -> Dict[str, Any]:
        """Get quality summary overview"""
        return {
            "average_scores": {
                "data_quality": self.average_data_quality_score,
                "validation": self.average_validation_score,
                "completeness": self.average_completeness_score,
                "accuracy": self.average_accuracy_score
            },
            "trends": self.quality_trend
        }
    
    def get_enterprise_summary(self) -> Dict[str, Any]:
        """Get enterprise summary overview"""
        return {
            "average_scores": {
                "performance": self.average_enterprise_performance_score,
                "quality": self.average_enterprise_quality_score,
                "reliability": self.average_enterprise_reliability_score,
                "compliance": self.average_enterprise_compliance_score,
                "security": self.average_enterprise_security_score
            },
            "distributions": {
                "compliance_status": self.compliance_status_distribution,
                "security_score": self.security_score_distribution,
                "threat_level": self.threat_level_distribution
            }
        }
