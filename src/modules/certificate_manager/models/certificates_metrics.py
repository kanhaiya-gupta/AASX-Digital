"""
Certificate Metrics Model
Metrics model for certificates_metrics table with all components
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from uuid import uuid4
from enum import Enum

from pydantic import BaseModel, Field, validator, computed_field, ConfigDict

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class MetricCategory(str, Enum):
    """Metric category classification"""
    PERFORMANCE = "performance"
    USAGE = "usage"
    QUALITY = "quality"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"
    REAL_TIME = "real_time"
    COMPLIANCE = "compliance"
    SECURITY = "security"


class MetricPriority(str, Enum):
    """Metric priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class PerformanceTrend(str, Enum):
    """Performance trend indicators"""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    FLUCTUATING = "fluctuating"
    UNKNOWN = "unknown"


class MetricUnit(str, Enum):
    """Metric measurement units"""
    PERCENTAGE = "percentage"
    COUNT = "count"
    SCORE = "score"
    SECONDS = "seconds"
    MILLISECONDS = "milliseconds"
    BYTES = "bytes"
    KILOBYTES = "kilobytes"
    MEGABYTES = "megabytes"
    GIGABYTES = "gigabytes"
    REQUESTS_PER_SECOND = "requests_per_second"
    TRANSACTIONS_PER_SECOND = "transactions_per_second"
    CUSTOM = "custom"


class AlertLevel(str, Enum):
    """Alert level for metrics"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


# ============================================================================
# NESTED COMPONENT MODELS
# ============================================================================

class PerformanceMetrics(BaseModel):
    """Generation times, cache rates, processing speeds"""
    model_config = ConfigDict(from_attributes=True)
    
    # Performance timing metrics
    generation_time_ms: float = Field(default=0.0, ge=0.0, description="Certificate generation time in milliseconds")
    processing_time_ms: float = Field(default=0.0, ge=0.0, description="Data processing time in milliseconds")
    validation_time_ms: float = Field(default=0.0, ge=0.0, description="Validation time in milliseconds")
    export_time_ms: float = Field(default=0.0, ge=0.0, description="Export time in milliseconds")
    
    # Throughput metrics
    requests_per_second: float = Field(default=0.0, ge=0.0, description="Requests processed per second")
    transactions_per_second: float = Field(default=0.0, ge=0.0, description="Transactions processed per second")
    concurrent_users: int = Field(default=0, ge=0, description="Number of concurrent users")
    
    # Cache performance
    cache_hit_rate: float = Field(default=0.0, ge=0.0, le=100.0, description="Cache hit rate percentage")
    cache_miss_rate: float = Field(default=0.0, ge=0.0, le=100.0, description="Cache miss rate percentage")
    cache_size_bytes: int = Field(default=0, ge=0, description="Current cache size in bytes")
    cache_eviction_rate: float = Field(default=0.0, ge=0.0, description="Cache eviction rate")
    
    # Database performance
    database_query_time_ms: float = Field(default=0.0, ge=0.0, description="Average database query time")
    database_connection_pool_usage: float = Field(default=0.0, ge=0.0, le=100.0, description="Connection pool usage percentage")
    database_transaction_time_ms: float = Field(default=0.0, ge=0.0, description="Database transaction time")
    
    # Memory and CPU metrics
    memory_usage_bytes: int = Field(default=0, ge=0, description="Memory usage in bytes")
    memory_usage_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Memory usage percentage")
    cpu_usage_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="CPU usage percentage")
    cpu_load_average: float = Field(default=0.0, ge=0.0, description="CPU load average")
    
    # Network performance
    network_latency_ms: float = Field(default=0.0, ge=0.0, description="Network latency in milliseconds")
    network_throughput_mbps: float = Field(default=0.0, ge=0.0, description="Network throughput in Mbps")
    network_error_rate: float = Field(default=0.0, ge=0.0, le=100.0, description="Network error rate percentage")
    
    # Performance thresholds
    performance_thresholds: Dict[str, float] = Field(default_factory=dict, description="Performance thresholds")
    alert_thresholds: Dict[str, float] = Field(default_factory=dict, description="Alert thresholds")
    
    @computed_field
    @property
    def total_processing_time_ms(self) -> float:
        """Calculate total processing time"""
        return (
            self.generation_time_ms +
            self.processing_time_ms +
            self.validation_time_ms +
            self.export_time_ms
        )
    
    @computed_field
    @property
    def cache_efficiency(self) -> float:
        """Calculate cache efficiency"""
        if self.cache_hit_rate + self.cache_miss_rate == 0:
            return 0.0
        return self.cache_hit_rate / (self.cache_hit_rate + self.cache_miss_rate) * 100
    
    @computed_field
    @property
    def performance_score(self) -> float:
        """Calculate overall performance score"""
        scores = []
        
        # Timing scores (lower is better)
        if self.generation_time_ms <= 1000:
            scores.append(100)
        elif self.generation_time_ms <= 5000:
            scores.append(80)
        elif self.generation_time_ms <= 10000:
            scores.append(60)
        else:
            scores.append(40)
        
        # Cache efficiency score
        scores.append(self.cache_efficiency)
        
        # Throughput score
        if self.requests_per_second >= 100:
            scores.append(100)
        elif self.requests_per_second >= 50:
            scores.append(80)
        elif self.requests_per_second >= 10:
            scores.append(60)
        else:
            scores.append(40)
        
        return sum(scores) / len(scores)


class UsageAnalytics(BaseModel):
    """View counts, exports, verifications, downloads"""
    model_config = ConfigDict(from_attributes=True)
    
    # Usage counts
    total_views: int = Field(default=0, ge=0, description="Total number of views")
    unique_views: int = Field(default=0, ge=0, description="Number of unique views")
    total_exports: int = Field(default=0, ge=0, description="Total number of exports")
    total_verifications: int = Field(default=0, ge=0, description="Total number of verifications")
    total_downloads: int = Field(default=0, ge=0, description="Total number of downloads")
    
    # User engagement
    active_users: int = Field(default=0, ge=0, description="Number of active users")
    returning_users: int = Field(default=0, ge=0, description="Number of returning users")
    new_users: int = Field(default=0, ge=0, description="Number of new users")
    user_session_duration_minutes: float = Field(default=0.0, ge=0.0, description="Average session duration")
    
    # Feature usage
    feature_usage_counts: Dict[str, int] = Field(default_factory=dict, description="Usage counts by feature")
    feature_popularity: Dict[str, float] = Field(default_factory=dict, description="Feature popularity scores")
    most_used_features: List[str] = Field(default_factory=list, description="Most frequently used features")
    
    # Geographic usage
    geographic_usage: Dict[str, int] = Field(default_factory=dict, description="Usage by geographic region")
    top_countries: List[str] = Field(default_factory=list, description="Top countries by usage")
    timezone_usage: Dict[str, int] = Field(default_factory=dict, description="Usage by timezone")
    
    # Device and platform usage
    device_types: Dict[str, int] = Field(default_factory=dict, description="Usage by device type")
    browsers: Dict[str, int] = Field(default_factory=dict, description="Usage by browser")
    operating_systems: Dict[str, int] = Field(default_factory=dict, description="Usage by operating system")
    
    # Usage patterns
    hourly_usage_pattern: Dict[int, int] = Field(default_factory=dict, description="Usage by hour of day")
    daily_usage_pattern: Dict[str, int] = Field(default_factory=dict, description="Usage by day of week")
    monthly_usage_pattern: Dict[str, int] = Field(default_factory=dict, description="Usage by month")
    
    # Usage trends
    usage_growth_rate: float = Field(default=0.0, description="Monthly usage growth rate")
    peak_usage_hour: Optional[int] = Field(None, ge=0, le=23, description="Peak usage hour")
    peak_usage_day: Optional[str] = Field(None, description="Peak usage day")
    
    @computed_field
    @property
    def total_interactions(self) -> int:
        """Calculate total user interactions"""
        return (
            self.total_views +
            self.total_exports +
            self.total_verifications +
            self.total_downloads
        )
    
    @computed_field
    @property
    def user_retention_rate(self) -> float:
        """Calculate user retention rate"""
        if self.total_users == 0:
            return 0.0
        return (self.returning_users / self.total_users) * 100
    
    @computed_field
    @property
    def total_users(self) -> int:
        """Calculate total users"""
        return self.new_users + self.returning_users
    
    @computed_field
    @property
    def engagement_score(self) -> float:
        """Calculate user engagement score"""
        if self.total_users == 0:
            return 0.0
        
        # Calculate engagement based on interactions per user
        interactions_per_user = self.total_interactions / self.total_users
        session_score = min(self.user_session_duration_minutes / 30.0, 1.0) * 100
        
        return (interactions_per_user * 10 + session_score) / 2


class QualityAnalytics(BaseModel):
    """Data completeness, validation rates, coverage"""
    model_config = ConfigDict(from_attributes=True)
    
    # Data completeness metrics
    data_completeness_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Overall data completeness score")
    required_fields_completeness: float = Field(default=0.0, ge=0.0, le=100.0, description="Required fields completeness")
    optional_fields_completeness: float = Field(default=0.0, ge=0.0, le=100.0, description="Optional fields completeness")
    nested_data_completeness: float = Field(default=0.0, ge=0.0, le=100.0, description="Nested data completeness")
    
    # Validation metrics
    validation_success_rate: float = Field(default=0.0, ge=0.0, le=100.0, description="Validation success rate")
    validation_errors_count: int = Field(default=0, ge=0, description="Number of validation errors")
    validation_warnings_count: int = Field(default=0, ge=0, description="Number of validation warnings")
    validation_rules_applied: int = Field(default=0, ge=0, description="Number of validation rules applied")
    
    # Data coverage metrics
    data_coverage_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Data coverage percentage")
    module_coverage: Dict[str, float] = Field(default_factory=dict, description="Coverage by module")
    field_coverage: Dict[str, float] = Field(default_factory=dict, description="Coverage by field type")
    temporal_coverage: Dict[str, float] = Field(default_factory=dict, description="Coverage by time period")
    
    # Data quality indicators
    data_accuracy_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Data accuracy score")
    data_consistency_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Data consistency score")
    data_timeliness_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Data timeliness score")
    data_relevance_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Data relevance score")
    
    # Quality issues tracking
    quality_issues: List[str] = Field(default_factory=list, description="List of quality issues")
    critical_quality_issues: int = Field(default=0, ge=0, description="Number of critical quality issues")
    quality_issue_resolution_rate: float = Field(default=0.0, ge=0.0, le=100.0, description="Quality issue resolution rate")
    
    # Quality thresholds
    quality_thresholds: Dict[str, float] = Field(default_factory=dict, description="Quality thresholds")
    quality_alert_levels: Dict[str, AlertLevel] = Field(default_factory=dict, description="Quality alert levels")
    
    @computed_field
    @property
    def overall_quality_score(self) -> float:
        """Calculate overall quality score"""
        scores = [
            self.data_completeness_score,
            self.validation_success_rate,
            self.data_coverage_percentage,
            self.data_accuracy_score,
            self.data_consistency_score,
            self.data_timeliness_score,
            self.data_relevance_score
        ]
        return sum(scores) / len(scores)
    
    @computed_field
    @property
    def quality_grade(self) -> str:
        """Get quality grade based on overall score"""
        if self.overall_quality_score >= 90:
            return "A"
        elif self.overall_quality_score >= 80:
            return "B"
        elif self.overall_quality_score >= 70:
            return "C"
        elif self.overall_quality_score >= 60:
            return "D"
        else:
            return "F"
    
    @computed_field
    @property
    def requires_quality_attention(self) -> bool:
        """Check if quality requires attention"""
        return (
            self.overall_quality_score < 70 or
            self.critical_quality_issues > 0 or
            self.validation_success_rate < 80
        )


class BusinessMetrics(BaseModel):
    """Stakeholder access, compliance checks, requests"""
    model_config = ConfigDict(from_attributes=True)
    
    # Stakeholder metrics
    stakeholder_access_count: int = Field(default=0, ge=0, description="Number of stakeholder accesses")
    stakeholder_satisfaction_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Stakeholder satisfaction score")
    stakeholder_feedback_count: int = Field(default=0, ge=0, description="Number of stakeholder feedback")
    stakeholder_engagement_rate: float = Field(default=0.0, ge=0.0, le=100.0, description="Stakeholder engagement rate")
    
    # Compliance metrics
    compliance_checks_performed: int = Field(default=0, ge=0, description="Number of compliance checks performed")
    compliance_check_success_rate: float = Field(default=0.0, ge=0.0, le=100.0, description="Compliance check success rate")
    compliance_violations_count: int = Field(default=0, ge=0, description="Number of compliance violations")
    compliance_audit_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Compliance audit score")
    
    # Request metrics
    total_requests: int = Field(default=0, ge=0, description="Total number of requests")
    successful_requests: int = Field(default=0, ge=0, description="Number of successful requests")
    failed_requests: int = Field(default=0, ge=0, description="Number of failed requests")
    request_success_rate: float = Field(default=0.0, ge=0.0, le=100.0, description="Request success rate")
    
    # Business process metrics
    business_process_efficiency: float = Field(default=0.0, ge=0.0, le=100.0, description="Business process efficiency")
    process_cycle_time_hours: float = Field(default=0.0, ge=0.0, description="Average process cycle time")
    process_bottlenecks: List[str] = Field(default_factory=list, description="Identified process bottlenecks")
    process_improvement_opportunities: List[str] = Field(default_factory=list, description="Process improvement opportunities")
    
    # ROI and business value metrics
    roi_percentage: float = Field(default=0.0, description="Return on investment percentage")
    cost_savings: float = Field(default=0.0, description="Cost savings achieved")
    business_value_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Business value score")
    stakeholder_value_delivered: float = Field(default=0.0, ge=0.0, le=100.0, description="Stakeholder value delivered")
    
    # Business intelligence
    key_performance_indicators: Dict[str, float] = Field(default_factory=dict, description="Key performance indicators")
    business_trends: List[Dict[str, Any]] = Field(default_factory=list, description="Business trends analysis")
    competitive_analysis: Dict[str, Any] = Field(default_factory=dict, description="Competitive analysis data")
    
    @computed_field
    @property
    def request_failure_rate(self) -> float:
        """Calculate request failure rate"""
        if self.total_requests == 0:
            return 0.0
        return (self.failed_requests / self.total_requests) * 100
    
    @computed_field
    @property
    def overall_business_score(self) -> float:
        """Calculate overall business score"""
        scores = [
            self.stakeholder_satisfaction_score,
            self.compliance_check_success_rate,
            self.request_success_rate,
            self.business_process_efficiency,
            self.business_value_score,
            self.stakeholder_value_delivered
        ]
        return sum(scores) / len(scores)
    
    @computed_field
    @property
    def business_health_indicator(self) -> str:
        """Get business health indicator"""
        if self.overall_business_score >= 80:
            return "healthy"
        elif self.overall_business_score >= 60:
            return "warning"
        else:
            return "critical"


class EnterpriseAnalytics(BaseModel):
    """SLA compliance, resource utilization, scalability"""
    model_config = ConfigDict(from_attributes=True)
    
    # SLA compliance metrics
    sla_compliance_rate: float = Field(default=0.0, ge=0.0, le=100.0, description="SLA compliance rate")
    sla_violations_count: int = Field(default=0, ge=0, description="Number of SLA violations")
    sla_targets: Dict[str, float] = Field(default_factory=dict, description="SLA targets by service")
    sla_performance: Dict[str, float] = Field(default_factory=dict, description="SLA performance by service")
    
    # Resource utilization metrics
    cpu_utilization_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="CPU utilization percentage")
    memory_utilization_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Memory utilization percentage")
    disk_utilization_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Disk utilization percentage")
    network_utilization_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Network utilization percentage")
    
    # Scalability metrics
    horizontal_scalability_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Horizontal scalability score")
    vertical_scalability_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Vertical scalability score")
    auto_scaling_effectiveness: float = Field(default=0.0, ge=0.0, le=100.0, description="Auto-scaling effectiveness")
    load_balancing_efficiency: float = Field(default=0.0, ge=0.0, le=100.0, description="Load balancing efficiency")
    
    # Infrastructure metrics
    infrastructure_health_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Infrastructure health score")
    system_availability_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="System availability percentage")
    mean_time_between_failures_hours: float = Field(default=0.0, ge=0.0, description="Mean time between failures")
    mean_time_to_recovery_minutes: float = Field(default=0.0, ge=0.0, description="Mean time to recovery")
    
    # Capacity planning metrics
    current_capacity_utilization: float = Field(default=0.0, ge=0.0, le=100.0, description="Current capacity utilization")
    projected_capacity_needs: Dict[str, Any] = Field(default_factory=dict, description="Projected capacity needs")
    capacity_planning_recommendations: List[str] = Field(default_factory=list, description="Capacity planning recommendations")
    
    # Cost optimization metrics
    infrastructure_cost_per_month: float = Field(default=0.0, ge=0.0, description="Infrastructure cost per month")
    cost_optimization_opportunities: List[str] = Field(default_factory=list, description="Cost optimization opportunities")
    resource_efficiency_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Resource efficiency score")
    
    @computed_field
    @property
    def overall_resource_utilization(self) -> float:
        """Calculate overall resource utilization"""
        return (
            self.cpu_utilization_percentage +
            self.memory_utilization_percentage +
            self.disk_utilization_percentage +
            self.network_utilization_percentage
        ) / 4
    
    @computed_field
    @property
    def scalability_score(self) -> float:
        """Calculate overall scalability score"""
        return (
            self.horizontal_scalability_score +
            self.vertical_scalability_score +
            self.auto_scaling_effectiveness +
            self.load_balancing_efficiency
        ) / 4
    
    @computed_field
    @property
    def enterprise_health_score(self) -> float:
        """Calculate enterprise health score"""
        scores = [
            self.sla_compliance_rate,
            self.infrastructure_health_score,
            self.system_availability_percentage,
            self.scalability_score,
            self.resource_efficiency_score
        ]
        return sum(scores) / len(scores)
    
    @computed_field
    @property
    def requires_capacity_attention(self) -> bool:
        """Check if capacity attention is required"""
        return (
            self.current_capacity_utilization > 80 or
            self.overall_resource_utilization > 85 or
            self.sla_compliance_rate < 95
        )


class RealTimeMetrics(BaseModel):
    """Live performance monitoring"""
    model_config = ConfigDict(from_attributes=True)
    
    # Real-time performance metrics
    current_response_time_ms: float = Field(default=0.0, ge=0.0, description="Current response time in milliseconds")
    current_throughput_rps: float = Field(default=0.0, ge=0.0, description="Current throughput in requests per second")
    current_error_rate: float = Field(default=0.0, ge=0.0, le=100.0, description="Current error rate percentage")
    current_success_rate: float = Field(default=0.0, ge=0.0, le=100.0, description="Current success rate percentage")
    
    # Real-time resource metrics
    current_cpu_usage: float = Field(default=0.0, ge=0.0, le=100.0, description="Current CPU usage percentage")
    current_memory_usage: float = Field(default=0.0, ge=0.0, le=100.0, description="Current memory usage percentage")
    current_disk_io_mbps: float = Field(default=0.0, ge=0.0, description="Current disk I/O in Mbps")
    current_network_io_mbps: float = Field(default=0.0, ge=0.0, description="Current network I/O in Mbps")
    
    # Real-time queue metrics
    current_queue_length: int = Field(default=0, ge=0, description="Current queue length")
    current_queue_processing_rate: float = Field(default=0.0, ge=0.0, description="Current queue processing rate")
    current_queue_wait_time_ms: float = Field(default=0.0, ge=0.0, description="Current queue wait time")
    
    # Real-time alert status
    active_alerts: List[str] = Field(default_factory=list, description="List of active alerts")
    alert_severity_levels: Dict[str, AlertLevel] = Field(default_factory=dict, description="Alert severity levels")
    critical_alerts_count: int = Field(default=0, ge=0, description="Number of critical alerts")
    
    # Real-time trend indicators
    performance_trend: PerformanceTrend = Field(default=PerformanceTrend.UNKNOWN, description="Current performance trend")
    trend_direction: str = Field(default="stable", description="Trend direction (improving, stable, declining)")
    trend_velocity: float = Field(default=0.0, description="Trend velocity (rate of change)")
    
    # Real-time monitoring metadata
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="When metrics were last updated")
    monitoring_interval_seconds: int = Field(default=30, ge=1, description="Monitoring interval in seconds")
    data_freshness_seconds: float = Field(default=0.0, ge=0.0, description="Data freshness in seconds")
    
    # Real-time thresholds
    performance_thresholds: Dict[str, float] = Field(default_factory=dict, description="Real-time performance thresholds")
    alert_thresholds: Dict[str, float] = Field(default_factory=dict, description="Real-time alert thresholds")
    
    @computed_field
    @property
    def is_performing_well(self) -> bool:
        """Check if system is performing well"""
        return (
            self.current_response_time_ms <= 1000 and
            self.current_error_rate <= 5.0 and
            self.current_success_rate >= 95.0 and
            self.current_cpu_usage <= 80.0 and
            self.current_memory_usage <= 80.0
        )
    
    @computed_field
    @property
    def requires_immediate_attention(self) -> bool:
        """Check if immediate attention is required"""
        return (
            self.critical_alerts_count > 0 or
            self.current_error_rate > 20.0 or
            self.current_success_rate < 80.0 or
            self.current_response_time_ms > 10000
        )
    
    @computed_field
    @property
    def real_time_health_score(self) -> float:
        """Calculate real-time health score"""
        scores = []
        
        # Response time score (lower is better)
        if self.current_response_time_ms <= 500:
            scores.append(100)
        elif self.current_response_time_ms <= 1000:
            scores.append(80)
        elif self.current_response_time_ms <= 5000:
            scores.append(60)
        else:
            scores.append(40)
        
        # Success rate score
        scores.append(self.current_success_rate)
        
        # Resource usage score (lower is better)
        cpu_score = max(0, 100 - self.current_cpu_usage)
        memory_score = max(0, 100 - self.current_memory_usage)
        scores.extend([cpu_score, memory_score])
        
        # Error rate score (lower is better)
        error_score = max(0, 100 - self.current_error_rate)
        scores.append(error_score)
        
        return sum(scores) / len(scores)
    
    @computed_field
    @property
    def data_is_fresh(self) -> bool:
        """Check if data is fresh (less than 2x monitoring interval)"""
        return self.data_freshness_seconds <= (self.monitoring_interval_seconds * 2)


# ============================================================================
# MAIN METRICS MODEL
# ============================================================================

class CertificateMetrics(BaseModel):
    """
    Metrics model for certificates_metrics table
    Comprehensive metrics and analytics with all business components
    """
    model_config = ConfigDict(from_attributes=True)
    
    # ========================================================================
    # PRIMARY IDENTIFIERS
    # ========================================================================
    metrics_id: str = Field(..., description="Unique metrics identifier")
    certificate_id: str = Field(..., description="Reference to the certificate")
    
    # ========================================================================
    # METRIC METADATA
    # ========================================================================
    metric_category: MetricCategory = Field(default=MetricCategory.PERFORMANCE, description="Category of the metric")
    metric_name: str = Field(..., description="Name of the metric")
    metric_value: float = Field(..., description="Value of the metric")
    metric_unit: str = Field(..., description="Unit of measurement")
    priority: MetricPriority = Field(default=MetricPriority.MEDIUM, description="Priority level of the metric")
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    recorded_at: datetime = Field(default_factory=datetime.utcnow, description="When metric was recorded")
    updated_at: Optional[datetime] = Field(None, description="When metric was last updated")
    deleted_at: Optional[datetime] = Field(None, description="Deletion timestamp (if soft deleted)")
    
    # ========================================================================
    # COMPONENT MODELS
    # ========================================================================
    performance_metrics: PerformanceMetrics = Field(default_factory=PerformanceMetrics, description="Performance metrics")
    usage_analytics: UsageAnalytics = Field(default_factory=UsageAnalytics, description="Usage analytics")
    quality_analytics: QualityAnalytics = Field(default_factory=QualityAnalytics, description="Quality analytics")
    business_metrics: BusinessMetrics = Field(default_factory=BusinessMetrics, description="Business metrics")
    enterprise_analytics: EnterpriseAnalytics = Field(default_factory=EnterpriseAnalytics, description="Enterprise analytics")
    real_time_metrics: RealTimeMetrics = Field(default_factory=RealTimeMetrics, description="Real-time metrics")
    
    # ========================================================================
    # ADDITIONAL METADATA
    # ========================================================================
    description: Optional[str] = Field(None, description="Metric description")
    tags: List[str] = Field(default_factory=list, description="Metric tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # ========================================================================
    # AUDIT FIELDS
    # ========================================================================
    recorded_by: Optional[str] = Field(None, description="User who recorded the metric")
    updated_by: Optional[str] = Field(None, description="User who last updated")
    deleted_by: Optional[str] = Field(None, description="User who deleted (if soft deleted)")
    is_deleted: bool = Field(default=False, description="Soft delete flag")
    
    # ========================================================================
    # COMPUTED FIELDS
    # ========================================================================
    
    @computed_field
    @property
    def age_hours(self) -> float:
        """Calculate metric age in hours"""
        delta = datetime.utcnow() - self.recorded_at
        return delta.total_seconds() / 3600
    
    @computed_field
    @property
    def is_recent(self) -> bool:
        """Check if metric is recent (less than 24 hours old)"""
        return self.age_hours < 24.0
    
    @computed_field
    @property
    def is_stale(self) -> bool:
        """Check if metric is stale (more than 7 days old)"""
        return self.age_hours > 168  # 7 days * 24 hours
    
    @computed_field
    @property
    def overall_metrics_score(self) -> float:
        """Calculate overall metrics score from components"""
        scores = [
            self.performance_metrics.performance_score,
            self.usage_analytics.engagement_score,
            self.quality_analytics.overall_quality_score,
            self.business_metrics.overall_business_score,
            self.enterprise_analytics.enterprise_health_score,
            self.real_time_metrics.real_time_health_score
        ]
        return sum(scores) / len(scores)
    
    @computed_field
    @property
    def requires_attention(self) -> bool:
        """Check if metrics require attention"""
        return (
            self.overall_metrics_score < 70 or
            self.quality_analytics.requires_quality_attention or
            self.business_metrics.business_health_indicator == "critical" or
            self.enterprise_analytics.requires_capacity_attention or
            self.real_time_metrics.requires_immediate_attention
        )
    
    @computed_field
    @property
    def metrics_grade(self) -> str:
        """Get metrics grade based on overall score"""
        if self.overall_metrics_score >= 90:
            return "A"
        elif self.overall_metrics_score >= 80:
            return "B"
        elif self.overall_metrics_score >= 70:
            return "C"
        elif self.overall_metrics_score >= 60:
            return "D"
        else:
            return "F"
    
    # ========================================================================
    # VALIDATION METHODS
    # ========================================================================
    
    @validator('metrics_id')
    def validate_metrics_id(cls, v):
        """Validate metrics ID format"""
        if not v or len(v.strip()) == 0:
            raise ValueError('Metrics ID cannot be empty')
        if len(v) > 255:
            raise ValueError('Metrics ID too long')
        return v.strip()
    
    @validator('metric_name')
    def validate_metric_name(cls, v):
        """Validate metric name"""
        if not v or len(v.strip()) == 0:
            raise ValueError('Metric name cannot be empty')
        if len(v) > 200:
            raise ValueError('Metric name too long')
        return v.strip()
    
    @validator('metric_value')
    def validate_metric_value(cls, v):
        """Validate metric value"""
        if not isinstance(v, (int, float)):
            raise ValueError('Metric value must be numeric')
        return v
    
    @validator('metric_unit')
    def validate_metric_unit(cls, v):
        """Validate metric unit"""
        if not v or len(v.strip()) == 0:
            raise ValueError('Metric unit cannot be empty')
        if len(v) > 50:
            raise ValueError('Metric unit too long')
        return v.strip()
    
    # ========================================================================
    # ASYNC METHODS
    # ========================================================================
    
    async def validate_integrity(self) -> bool:
        """Validate metrics data integrity"""
        try:
            # Validate required fields
            if not all([self.metrics_id, self.certificate_id, self.metric_name, self.metric_value, self.metric_unit]):
                return False
            
            # Validate component models
            if not all([
                self.performance_metrics,
                self.usage_analytics,
                self.quality_analytics,
                self.business_metrics,
                self.enterprise_analytics,
                self.real_time_metrics
            ]):
                return False
            
            # Validate business rules
            if self.metric_value < 0 and self.metric_unit in ["percentage", "score"]:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating metrics integrity: {e}")
            return False
    
    async def update_real_time_metrics(self) -> None:
        """Update real-time metrics with current values"""
        try:
            # Update data freshness
            self.real_time_metrics.data_freshness_seconds = 0.0
            self.real_time_metrics.last_updated = datetime.utcnow()
            
            # Update performance trend based on current values
            if self.metric_value > self.metadata.get("previous_value", self.metric_value):
                self.real_time_metrics.performance_trend = PerformanceTrend.IMPROVING
                self.real_time_metrics.trend_direction = "improving"
            elif self.metric_value < self.metadata.get("previous_value", self.metric_value):
                self.real_time_metrics.performance_trend = PerformanceTrend.DECLINING
                self.real_time_metrics.trend_direction = "declining"
            else:
                self.real_time_metrics.performance_trend = PerformanceTrend.STABLE
                self.real_time_metrics.trend_direction = "stable"
            
            # Store current value for next comparison
            self.metadata["previous_value"] = self.metric_value
            
            logger.info(f"Updated real-time metrics for metric {self.metrics_id}")
            
        except Exception as e:
            logger.error(f"Error updating real-time metrics: {e}")
    
    async def generate_metrics_summary(self) -> Dict[str, Any]:
        """Generate comprehensive metrics summary"""
        try:
            await self.update_real_time_metrics()
            
            summary = {
                "metrics_id": self.metrics_id,
                "metric_name": self.metric_name,
                "metric_value": self.metric_value,
                "metric_unit": self.metric_unit,
                "category": self.metric_category.value,
                "priority": self.priority.value,
                "overall_score": self.overall_metrics_score,
                "grade": self.metrics_grade,
                "requires_attention": self.requires_attention,
                "age_hours": self.age_hours,
                "is_recent": self.is_recent,
                "component_scores": {
                    "performance": self.performance_metrics.performance_score,
                    "usage": self.usage_analytics.engagement_score,
                    "quality": self.quality_analytics.overall_quality_score,
                    "business": self.business_metrics.overall_business_score,
                    "enterprise": self.enterprise_analytics.enterprise_health_score,
                    "real_time": self.real_time_metrics.real_time_health_score
                },
                "health_indicators": {
                    "quality_health": self.quality_analytics.quality_grade,
                    "business_health": self.business_metrics.business_health_indicator,
                    "enterprise_health": "healthy" if self.enterprise_analytics.enterprise_health_score >= 80 else "warning",
                    "real_time_health": "healthy" if self.real_time_metrics.real_time_health_score >= 80 else "warning"
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating metrics summary: {e}")
            return {}
    
    async def export_metrics_data(self, format: str = "json") -> Dict[str, Any]:
        """Export metrics data in specified format"""
        try:
            export_data = {
                "export_info": {
                    "format": format,
                    "exported_at": datetime.utcnow().isoformat(),
                    "metrics_id": self.metrics_id
                },
                "metrics_data": self.model_dump(),
                "summary": await self.generate_metrics_summary()
            }
            
            logger.info(f"Exported metrics {self.metrics_id} in {format} format")
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting metrics data: {e}")
            raise
