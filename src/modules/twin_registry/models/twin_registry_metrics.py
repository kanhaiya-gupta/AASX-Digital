"""
Twin Registry Metrics Model

Model for twin registry metrics and performance monitoring data.
Matches our new twin_registry_metrics table schema with all 54 fields.
Pure async implementation for modern architecture.
Enhanced with enterprise-grade computed fields, business intelligence methods, and full Certificate Manager method parity.
"""

from pydantic import BaseModel, computed_field, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid
import asyncio


class TwinRegistryMetrics(BaseModel):
    """Model for twin registry metrics and performance data - Pure async implementation"""
    
    model_config = ConfigDict(
        from_attributes=True,
        protected_namespaces=(),  # ✅ Fix Pydantic v2 namespace conflicts
        arbitrary_types_allowed=True
    )
    
    # Primary Identification
    metric_id: Optional[int] = Field(default=None, description="Primary key (INTEGER AUTOINCREMENT)")
    registry_id: str = Field(..., description="Reference to twin_registry table")
    timestamp: datetime = Field(..., description="When this metric was recorded")
    
    # Real-time Health Metrics (Framework Health)
    health_score: Optional[int] = Field(default=None, ge=0, le=100, description="Current health score (0-100)")
    response_time_ms: Optional[float] = Field(default=None, description="Response time in milliseconds")
    uptime_percentage: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Uptime percentage (0.0-100.0)")
    error_rate: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Error rate (0.0-1.0)")
    
    # Twin Registry Performance Metrics (Framework Performance - NOT Data)
    twin_sync_speed_sec: Optional[float] = Field(default=None, description="Time to synchronize twin data")
    relationship_update_speed_sec: Optional[float] = Field(default=None, description="Time to update twin relationships")
    lifecycle_transition_speed_sec: Optional[float] = Field(default=None, description="Time for lifecycle state changes")
    twin_registry_efficiency: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Twin registry efficiency (0.0-1.0)")
    
    # Twin Management Performance (JSON for better framework analysis)
    twin_management_performance: Dict[str, Any] = Field(default={}, description="JSON: twin_creation, twin_sync, relationship_management, lifecycle_management, instance_management")
    
    # Twin Category Performance Metrics (JSON for better framework analysis)
    twin_category_performance_stats: Dict[str, Any] = Field(default={}, description="JSON: manufacturing, energy, component, facility, process, generic")
    
    # User Interaction Metrics (Framework Usage - NOT Content)
    user_interaction_count: int = Field(default=0, description="Number of user interactions")
    twin_access_count: int = Field(default=0, description="Number of twin accesses")
    successful_twin_operations: int = Field(default=0, description="Successful operations")
    failed_twin_operations: int = Field(default=0, description="Failed operations")
    
    # Data Quality Metrics (Framework Quality - NOT Data Content)
    data_freshness_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Data freshness score (0.0-1.0)")
    data_completeness_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Data completeness score (0.0-1.0)")
    data_consistency_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Data consistency score (0.0-1.0)")
    data_accuracy_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Data accuracy score (0.0-1.0)")
    
    # System Resource Metrics (Framework Resources - NOT Data)
    cpu_usage_percent: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="CPU usage percentage (0.0-100.0)")
    memory_usage_percent: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Memory usage percentage (0.0-100.0)")
    network_throughput_mbps: Optional[float] = Field(default=None, description="Network throughput in Mbps")
    storage_usage_percent: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Storage usage percentage (0.0-100.0)")
    disk_io_mb: Optional[float] = Field(default=None, description="Disk I/O in MB")
    
    # Twin Registry Patterns & Analytics (Framework Trends - JSON)
    twin_registry_patterns: Dict[str, Any] = Field(default={}, description="JSON: hourly, daily, weekly, monthly")
    resource_utilization_trends: Dict[str, Any] = Field(default={}, description="JSON: cpu_trend, memory_trend, disk_trend")
    user_activity: Dict[str, Any] = Field(default={}, description="JSON: peak_hours, user_patterns, session_durations")
    twin_operation_patterns: Dict[str, Any] = Field(default={}, description="JSON: operation_types, complexity_distribution, processing_times")
    compliance_status: Dict[str, Any] = Field(default={}, description="JSON: compliance_score, audit_status, last_audit")
    security_events: Dict[str, Any] = Field(default={}, description="JSON: events, threat_level, last_security_scan")
    
    # Twin Registry-Specific Metrics (Framework Capabilities - JSON)
    twin_registry_analytics: Dict[str, Any] = Field(default={}, description="JSON: sync_quality, relationship_quality, lifecycle_quality")
    category_effectiveness: Dict[str, Any] = Field(default={}, description="JSON: category_comparison, best_performing, optimization_suggestions")
    workflow_performance: Dict[str, Any] = Field(default={}, description="JSON: extraction_performance, generation_performance, hybrid_performance")
    twin_size_performance_efficiency: Dict[str, Any] = Field(default={}, description="JSON: performance_by_twin_size, quality_by_twin_size, optimization_opportunities")
    
    # Time-based Analytics (Framework Time Analysis)
    hour_of_day: Optional[int] = Field(default=None, ge=0, le=23, description="Hour of day (0-23)")
    day_of_week: Optional[int] = Field(default=None, ge=1, le=7, description="Day of week (1-7)")
    month: Optional[int] = Field(default=None, ge=1, le=12, description="Month (1-12)")
    
    # Performance Trends (Framework Performance Analysis)
    twin_management_trend: Optional[float] = Field(default=None, description="Compared to historical average")
    resource_efficiency_trend: Optional[float] = Field(default=None, description="Performance over time")
    quality_trend: Optional[float] = Field(default=None, description="Quality metrics over time")
    
    # Enterprise Compliance Metrics (MERGED)
    enterprise_compliance_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Enterprise-wide compliance rating")
    compliance_audit_status: str = Field(default="pending", description="Compliance audit status: pending, passed, failed, under_review")
    compliance_violations_count: int = Field(default=0, description="Number of compliance violations")
    compliance_corrective_actions: Dict[str, Any] = Field(default={}, description="JSON object of corrective actions")
    
    # Enterprise Security Metrics (MERGED)
    enterprise_security_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Enterprise-wide security rating")
    security_threat_level: str = Field(default="low", description="Security threat level: low, medium, high, critical")
    security_vulnerabilities_count: int = Field(default=0, description="Number of security vulnerabilities")
    security_incident_response_time: Optional[float] = Field(default=None, description="Average incident response time")
    security_scan_frequency: str = Field(default="weekly", description="Security scan frequency: daily, weekly, monthly, quarterly")
    
    # Enterprise Performance Analytics (MERGED)
    enterprise_performance_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Enterprise-wide performance rating")
    performance_optimization_status: str = Field(default="none", description="Optimization status: none, scheduled, in_progress, completed")
    resource_optimization_efficiency: float = Field(default=0.0, ge=0.0, le=1.0, description="0.0-1.0 optimization efficiency")
    enterprise_analytics_metadata: Dict[str, Any] = Field(default={}, description="JSON: enterprise analytics data")
    
    # Multi-Tenant Support (REQUIRED for RBAC)
    user_id: str = Field(..., description="User ID for access control")
    org_id: str = Field(..., description="Organization ID for multi-tenant isolation")
    dept_id: str = Field(..., description="Department ID for department-level access control")
    
    # Timestamps
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    
    # Computed Fields for Business Intelligence
    @computed_field
    @property
    def overall_metrics_score(self) -> float:
        """Calculate overall composite score from all metrics"""
        scores = []
        if self.health_score is not None:
            scores.append(self.health_score / 100.0)
        if self.twin_registry_efficiency is not None:
            scores.append(self.twin_registry_efficiency)
        if self.data_freshness_score is not None:
            scores.append(self.data_freshness_score)
        if self.data_completeness_score is not None:
            scores.append(self.data_completeness_score)
        if self.data_consistency_score is not None:
            scores.append(self.data_consistency_score)
        if self.data_accuracy_score is not None:
            scores.append(self.data_accuracy_score)
        if self.enterprise_compliance_score > 0:
            scores.append(self.enterprise_compliance_score)
        if self.enterprise_security_score > 0:
            scores.append(self.enterprise_security_score)
        if self.enterprise_performance_score > 0:
            scores.append(self.enterprise_performance_score)
        return sum(scores) / len(scores) if scores else 0.0
    
    @computed_field
    @property
    def enterprise_health_status(self) -> str:
        """Determine enterprise health status based on multiple factors"""
        if self.health_score and self.health_score >= 80:
            return "excellent"
        elif self.health_score and self.health_score >= 60:
            return "good"
        elif self.health_score and self.health_score >= 40:
            return "fair"
        else:
            return "poor"
    
    @computed_field
    @property
    def risk_assessment(self) -> str:
        """Assess risk level based on various factors"""
        if self.error_rate and self.error_rate > 0.7:
            return "high"
        elif self.error_rate and self.error_rate > 0.3:
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
        if self.user_interaction_count and self.successful_twin_operations:
            engagement_rate = self.successful_twin_operations / max(self.user_interaction_count, 1)
            return min(engagement_rate, 1.0)
        return 0.0
    
    @computed_field
    @property
    def twin_management_efficiency_score(self) -> float:
        """Calculate twin management efficiency based on performance metrics"""
        efficiency_factors = []
        if self.twin_sync_speed_sec and self.twin_sync_speed_sec < 10:
            efficiency_factors.append(0.9)
        elif self.twin_sync_speed_sec and self.twin_sync_speed_sec < 30:
            efficiency_factors.append(0.7)
        else:
            efficiency_factors.append(0.4)
        
        if self.relationship_update_speed_sec and self.relationship_update_speed_sec < 15:
            efficiency_factors.append(0.9)
        elif self.relationship_update_speed_sec and self.relationship_update_speed_sec < 45:
            efficiency_factors.append(0.7)
        else:
            efficiency_factors.append(0.4)
        
        return sum(efficiency_factors) / len(efficiency_factors) if efficiency_factors else 0.0
    
    @classmethod
    async def create_metrics(
        cls,
        registry_id: str,
        health_score: Optional[int] = None,
        response_time_ms: Optional[float] = None,
        **kwargs
    ) -> "TwinRegistryMetrics":
        """Create new metrics entry asynchronously"""
        now = datetime.now(timezone.utc)
        # Simulate async operation
        await asyncio.sleep(0.001)
        return cls(
            registry_id=registry_id,
            timestamp=now,
            health_score=health_score,
            response_time_ms=response_time_ms,
            created_at=now,
            updated_at=now,
            **kwargs
        )
    
    async def update_health_score(self, new_score: int) -> None:
        """Update health score asynchronously"""
        if 0 <= new_score <= 100:
            self.health_score = new_score
            self.timestamp = datetime.now(timezone.utc)
            self.updated_at = datetime.now(timezone.utc)
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def update_performance_metrics(
        self,
        cpu: Optional[float] = None,
        memory: Optional[float] = None,
        network: Optional[float] = None,
        storage: Optional[float] = None
    ) -> None:
        """Update performance metrics asynchronously"""
        if cpu is not None:
            self.cpu_usage_percent = cpu
        if memory is not None:
            self.memory_usage_percent = memory
        if network is not None:
            self.network_throughput_mbps = network
        if storage is not None:
            self.storage_usage_percent = storage
        
        self.timestamp = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        # Simulate async operation
        await asyncio.sleep(0.001)
    
    async def add_twin_management_performance(self, operation_type: str, metrics: Dict[str, Any]) -> None:
        """Add twin management performance metrics asynchronously"""
        if isinstance(metrics, dict):
            self.twin_management_performance[operation_type] = metrics
            self.updated_at = datetime.now(timezone.utc)
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def get_model_analytics(self) -> Dict[str, Any]:
        """Get comprehensive model analytics asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        
        return {
            "performance_analytics": {
                "overall_score": self.overall_metrics_score,
                "health_status": self.enterprise_health_status,
                "risk_level": self.risk_assessment,
                "optimization_priority": self.optimization_priority,
                "maintenance_schedule": self.maintenance_schedule
            },
            "system_metrics": {
                "cpu_usage": self.cpu_usage_percent,
                "memory_usage": self.memory_usage_percent,
                "storage_usage": self.storage_usage_percent,
                "network_throughput": self.network_throughput_mbps,
                "disk_io": self.disk_io_mb
            },
            "twin_registry_metrics": {
                "sync_speed": self.twin_sync_speed_sec,
                "relationship_update_speed": self.relationship_update_speed_sec,
                "lifecycle_transition_speed": self.lifecycle_transition_speed_sec,
                "registry_efficiency": self.twin_registry_efficiency
            },
            "data_quality_metrics": {
                "freshness": self.data_freshness_score,
                "completeness": self.data_completeness_score,
                "consistency": self.data_consistency_score,
                "accuracy": self.data_accuracy_score
            },
            "enterprise_metrics": {
                "compliance_score": self.enterprise_compliance_score,
                "security_score": self.enterprise_security_score,
                "performance_score": self.enterprise_performance_score,
                "compliance_status": self.compliance_audit_status,
                "security_threat_level": self.security_threat_level
            },
            "user_metrics": {
                "interaction_count": self.user_interaction_count,
                "twin_access_count": self.twin_access_count,
                "successful_operations": self.successful_twin_operations,
                "failed_operations": self.failed_twin_operations,
                "engagement_score": self.user_engagement_score
            },
            "computed_scores": {
                "system_efficiency": self.system_efficiency_score,
                "twin_management_efficiency": self.twin_management_efficiency_score
            },
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "registry_id": self.registry_id
        }
    
    async def add_category_performance_stats(self, category: str, stats: Dict[str, Any]) -> None:
        """Add category performance statistics asynchronously"""
        if isinstance(stats, dict):
            self.twin_category_performance_stats[category] = stats
            self.updated_at = datetime.now(timezone.utc)
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def add_resource_utilization_trend(self, resource_type: str, trend_data: List[float]) -> None:
        """Add resource utilization trend data asynchronously"""
        if isinstance(trend_data, list):
            self.resource_utilization_trends[resource_type] = trend_data
            self.updated_at = datetime.now(timezone.utc)
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def add_user_activity_pattern(self, pattern_type: str, pattern_data: Dict[str, Any]) -> None:
        """Add user activity pattern data asynchronously"""
        if isinstance(pattern_data, dict):
            self.user_activity[pattern_type] = pattern_data
            self.updated_at = datetime.now(timezone.utc)
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def add_twin_operation_pattern(self, pattern_type: str, pattern_data: Dict[str, Any]) -> None:
        """Add twin operation pattern data asynchronously"""
        if isinstance(pattern_data, dict):
            self.twin_operation_patterns[pattern_type] = pattern_data
            self.updated_at = datetime.now(timezone.utc)
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def add_compliance_status(self, compliance_data: Dict[str, Any]) -> None:
        """Add compliance status information asynchronously"""
        if isinstance(compliance_data, dict):
            self.compliance_status.update(compliance_data)
            self.updated_at = datetime.now(timezone.utc)
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def add_security_event(self, event: Dict[str, Any]) -> None:
        """Add security event information asynchronously"""
        if isinstance(event, dict):
            if 'events' not in self.security_events:
                self.security_events['events'] = []
            self.security_events['events'].append(event)
            self.updated_at = datetime.now(timezone.utc)
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def add_twin_registry_analytics(self, analytics_type: str, analytics_data: Dict[str, Any]) -> None:
        """Add twin registry analytics asynchronously"""
        if isinstance(analytics_data, dict):
            self.twin_registry_analytics[analytics_type] = analytics_data
            self.updated_at = datetime.now(timezone.utc)
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def add_workflow_performance(self, workflow_type: str, performance_data: Dict[str, Any]) -> None:
        """Add workflow performance data asynchronously"""
        if isinstance(performance_data, dict):
            self.workflow_performance[workflow_type] = performance_data
            self.updated_at = datetime.now(timezone.utc)
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def increment_user_interaction(self) -> None:
        """Increment user interaction count asynchronously"""
        self.user_interaction_count += 1
        self.timestamp = datetime.now(timezone.utc)
        self.updated_at = self.timestamp
        # Simulate async operation
        await asyncio.sleep(0.001)
    
    async def increment_twin_access(self) -> None:
        """Increment twin access count asynchronously"""
        self.twin_access_count += 1
        self.timestamp = datetime.now(timezone.utc)
        self.updated_at = self.timestamp
        # Simulate async operation
        await asyncio.sleep(0.001)
    
    async def record_successful_operation(self) -> None:
        """Record successful operation asynchronously"""
        self.successful_twin_operations += 1
        self.timestamp = datetime.now(timezone.utc)
        self.updated_at = self.timestamp
        # Simulate async operation
        await asyncio.sleep(0.001)
    
    async def record_failed_operation(self) -> None:
        """Record failed operation asynchronously"""
        self.failed_twin_operations += 1
        self.timestamp = datetime.now(timezone.utc)
        self.updated_at = self.timestamp
        # Simulate async operation
        await asyncio.sleep(0.001)
    
    async def update_enterprise_compliance_metrics(
        self,
        compliance_score: Optional[float] = None,
        audit_status: Optional[str] = None,
        violations_count: Optional[int] = None,
        corrective_actions: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update enterprise compliance metrics asynchronously"""
        if compliance_score is not None:
            self.enterprise_compliance_score = compliance_score
        if audit_status is not None:
            self.compliance_audit_status = audit_status
        if violations_count is not None:
            self.compliance_violations_count = violations_count
        if corrective_actions is not None:
            self.compliance_corrective_actions.update(corrective_actions)
        
        self.timestamp = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        # Simulate async operation
        await asyncio.sleep(0.001)
    
    async def update_enterprise_security_metrics(
        self,
        security_score: Optional[float] = None,
        threat_level: Optional[str] = None,
        vulnerabilities_count: Optional[int] = None,
        incident_response_time: Optional[float] = None,
        scan_frequency: Optional[str] = None
    ) -> None:
        """Update enterprise security metrics asynchronously"""
        if security_score is not None:
            self.enterprise_security_score = security_score
        if threat_level is not None:
            self.security_threat_level = threat_level
        if vulnerabilities_count is not None:
            self.security_vulnerabilities_count = vulnerabilities_count
        if incident_response_time is not None:
            self.security_incident_response_time = incident_response_time
        if scan_frequency is not None:
            self.security_scan_frequency = scan_frequency
        
        self.timestamp = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        # Simulate async operation
        await asyncio.sleep(0.001)
    
    async def update_enterprise_performance_metrics(
        self,
        performance_score: Optional[float] = None,
        optimization_status: Optional[str] = None,
        optimization_efficiency: Optional[float] = None,
        analytics_metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update enterprise performance metrics asynchronously"""
        if performance_score is not None:
            self.enterprise_performance_score = performance_score
        if optimization_status is not None:
            self.performance_optimization_status = optimization_status
        if optimization_efficiency is not None:
            self.resource_optimization_efficiency = optimization_efficiency
        if analytics_metadata is not None:
            self.enterprise_analytics_metadata.update(analytics_metadata)
        
        self.timestamp = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        # Simulate async operation
        await asyncio.sleep(0.001)
    
    async def update_time_based_analytics(
        self,
        hour_of_day: Optional[int] = None,
        day_of_week: Optional[int] = None,
        month: Optional[int] = None
    ) -> None:
        """Update time-based analytics asynchronously"""
        if hour_of_day is not None and 0 <= hour_of_day <= 23:
            self.hour_of_day = hour_of_day
        if day_of_week is not None and 1 <= day_of_week <= 7:
            self.day_of_week = day_of_week
        if month is not None and 1 <= month <= 12:
            self.month = month
        
        self.timestamp = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        # Simulate async operation
        await asyncio.sleep(0.001)
    
    async def update_performance_trends(
        self,
        twin_management_trend: Optional[float] = None,
        resource_efficiency_trend: Optional[float] = None,
        quality_trend: Optional[float] = None
    ) -> None:
        """Update performance trends asynchronously"""
        if twin_management_trend is not None:
            self.twin_management_trend = twin_management_trend
        if resource_efficiency_trend is not None:
            self.resource_efficiency_trend = resource_efficiency_trend
        if quality_trend is not None:
            self.quality_trend = quality_trend
        
        self.timestamp = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        # Simulate async operation
        await asyncio.sleep(0.001)
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary asynchronously"""
        # Simulate async operation
        await asyncio.sleep(0.001)
        return {
            'health_score': self.health_score,
            'response_time_ms': self.response_time_ms,
            'uptime_percentage': self.uptime_percentage,
            'error_rate': self.error_rate,
            'twin_sync_speed_sec': self.twin_sync_speed_sec,
            'relationship_update_speed_sec': self.relationship_update_speed_sec,
            'lifecycle_transition_speed_sec': self.lifecycle_transition_speed_sec,
            'twin_registry_efficiency': self.twin_registry_efficiency,
            'cpu_usage_percent': self.cpu_usage_percent,
            'memory_usage_percent': self.memory_usage_percent,
            'storage_usage_percent': self.storage_usage_percent
        }
    
    async def get_quality_summary(self) -> Dict[str, Any]:
        """Get data quality summary asynchronously"""
        # Simulate async operation
        await asyncio.sleep(0.001)
        return {
            'data_freshness_score': self.data_freshness_score,
            'data_completeness_score': self.data_completeness_score,
            'data_consistency_score': self.data_consistency_score,
            'data_accuracy_score': self.data_accuracy_score,
            'compliance_score': self.compliance_status.get('compliance_score'),
            'audit_status': self.compliance_status.get('audit_status')
        }
    
    async def get_usage_summary(self) -> Dict[str, Any]:
        """Get usage summary asynchronously"""
        # Simulate async operation
        await asyncio.sleep(0.001)
        return {
            'user_interaction_count': self.user_interaction_count,
            'twin_access_count': self.twin_access_count,
            'successful_twin_operations': self.successful_twin_operations,
            'failed_twin_operations': self.failed_twin_operations,
            'total_operations': self.successful_twin_operations + self.failed_twin_operations,
            'success_rate': self.successful_twin_operations / (self.successful_twin_operations + self.failed_twin_operations) if (self.successful_twin_operations + self.failed_twin_operations) > 0 else 0.0
        }
    
    async def is_performing_well(self) -> bool:
        """Check if performance is good asynchronously"""
        # Simulate async operation
        await asyncio.sleep(0.001)
        return (
            self.health_score is not None and self.health_score >= 80 and
            self.response_time_ms is not None and self.response_time_ms < 1000 and
            self.error_rate is not None and self.error_rate < 0.05
        )
    
    async def requires_optimization(self) -> bool:
        """Check if optimization is needed asynchronously"""
        # Simulate async operation
        await asyncio.sleep(0.001)
        return (
            self.health_score is not None and self.health_score < 60 or
            self.response_time_ms is not None and self.response_time_ms > 5000 or
            self.error_rate is not None and self.error_rate > 0.1 or
            self.cpu_usage_percent is not None and self.cpu_usage_percent > 90 or
            self.memory_usage_percent is not None and self.memory_usage_percent > 90
        )
    
    async def calculate_efficiency_score(self) -> float:
        """Calculate overall efficiency score asynchronously"""
        # Simulate async calculation
        await asyncio.sleep(0.001)
        scores = []
        if self.health_score is not None:
            scores.append(self.health_score / 100.0)
        if self.twin_registry_efficiency is not None:
            scores.append(self.twin_registry_efficiency)
        if self.data_freshness_score is not None:
            scores.append(self.data_freshness_score)
        if self.data_completeness_score is not None:
            scores.append(self.data_completeness_score)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    async def validate(self) -> bool:
        """Validate metrics data asynchronously"""
        # Simulate async validation
        await asyncio.sleep(0.001)
        
        # Basic required field validation
        basic_validation = (
            bool(self.registry_id) and
            bool(self.timestamp)
        )
        
        if not basic_validation:
            return False
        
        # Validate enterprise compliance fields
        valid_compliance_audit_statuses = ['pending', 'passed', 'failed', 'under_review']
        if self.compliance_audit_status not in valid_compliance_audit_statuses:
            return False
        
        # Validate enterprise security fields
        valid_security_threat_levels = ['low', 'medium', 'high', 'critical']
        valid_security_scan_frequencies = ['daily', 'weekly', 'monthly', 'quarterly']
        
        if self.security_threat_level not in valid_security_threat_levels:
            return False
        
        if self.security_scan_frequency not in valid_security_scan_frequencies:
            return False
        
        # Validate enterprise performance fields
        valid_performance_optimization_statuses = ['none', 'scheduled', 'in_progress', 'completed']
        
        if self.performance_optimization_status not in valid_performance_optimization_statuses:
            return False
        
        # Validate time-based analytics
        if self.hour_of_day is not None and (self.hour_of_day < 0 or self.hour_of_day > 23):
            return False
        
        if self.day_of_week is not None and (self.day_of_week < 1 or self.day_of_week > 7):
            return False
        
        if self.month is not None and (self.month < 1 or self.month > 12):
            return False
        
        return True

    async def is_enterprise_compliant(self) -> bool:
        """Check if metrics show enterprise compliance asynchronously"""
        # Simulate async operation
        await asyncio.sleep(0.001)
        return (
            self.enterprise_compliance_score >= 0.8 and
            self.compliance_audit_status == 'passed' and
            self.compliance_violations_count == 0
        )
    
    async def has_enterprise_security_issues(self) -> bool:
        """Check if metrics show enterprise security issues asynchronously"""
        # Simulate async operation
        await asyncio.sleep(0.001)
        return (
            self.enterprise_security_score < 0.7 or
            self.security_threat_level in ['high', 'critical'] or
            self.security_vulnerabilities_count > 0
        )
    
    async def requires_enterprise_optimization(self) -> bool:
        """Check if metrics show need for enterprise optimization asynchronously"""
        # Simulate async operation
        await asyncio.sleep(0.001)
        return (
            self.enterprise_performance_score < 0.7 or
            self.performance_optimization_status == 'scheduled' or
            self.resource_optimization_efficiency < 0.6
        )
    
    async def get_enterprise_health_status(self) -> str:
        """Get overall enterprise health status asynchronously"""
        # Simulate async operation
        await asyncio.sleep(0.001)
        
        if self.enterprise_compliance_score >= 0.9 and self.enterprise_security_score >= 0.9 and self.enterprise_performance_score >= 0.9:
            return 'excellent'
        elif self.enterprise_compliance_score >= 0.8 and self.enterprise_security_score >= 0.8 and self.enterprise_performance_score >= 0.8:
            return 'good'
        elif self.enterprise_compliance_score >= 0.7 and self.enterprise_security_score >= 0.7 and self.enterprise_performance_score >= 0.7:
            return 'fair'
        else:
            return 'poor'
    
    async def get_optimization_priority(self) -> str:
        """Get optimization priority based on metrics asynchronously"""
        # Simulate async operation
        await asyncio.sleep(0.001)
        
        if self.enterprise_compliance_score < 0.6 or self.enterprise_security_score < 0.6:
            return 'critical'
        elif self.enterprise_performance_score < 0.6:
            return 'high'
        elif self.enterprise_compliance_score < 0.8 or self.enterprise_security_score < 0.8:
            return 'medium'
        else:
            return 'low'
    
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
        
        # Calculate health score based on various metrics
        health_factors = []
        
        if self.health_score is not None:
            health_factors.append(self.health_score / 100.0)
        
        if self.twin_registry_efficiency is not None:
            health_factors.append(self.twin_registry_efficiency)
        
        if self.data_freshness_score is not None:
            health_factors.append(self.data_freshness_score)
        
        if self.data_completeness_score is not None:
            health_factors.append(self.data_completeness_score)
        
        if self.data_consistency_score is not None:
            health_factors.append(self.data_consistency_score)
        
        if self.data_accuracy_score is not None:
            health_factors.append(self.data_accuracy_score)
        
        if self.enterprise_compliance_score > 0:
            health_factors.append(self.enterprise_compliance_score)
        
        if self.enterprise_security_score > 0:
            health_factors.append(self.enterprise_security_score)
        
        if self.enterprise_performance_score > 0:
            health_factors.append(self.enterprise_performance_score)
        
        # Update health score if we have factors
        if health_factors:
            calculated_health = sum(health_factors) / len(health_factors)
            self.health_score = int(calculated_health * 100)
        
        # Update timestamp
        self.updated_at = datetime.now(timezone.utc)
    
    async def generate_summary(self) -> Dict[str, Any]:
        """Generate comprehensive summary asynchronously"""
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
                "twin_sync_speed": self.twin_sync_speed_sec,
                "relationship_update_speed": self.relationship_update_speed_sec,
                "lifecycle_transition_speed": self.lifecycle_transition_speed_sec
            },
            "quality_metrics": {
                "data_freshness": self.data_freshness_score,
                "data_completeness": self.data_completeness_score,
                "data_consistency": self.data_consistency_score,
                "data_accuracy": self.data_accuracy_score
            }
        }
    
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
                    "maintenance_schedule": self.maintenance_schedule,
                    "system_efficiency_score": self.system_efficiency_score,
                    "user_engagement_score": self.user_engagement_score,
                    "twin_management_efficiency_score": self.twin_management_efficiency_score
                },
                "export_timestamp": datetime.now().isoformat(),
                "export_format": format
            }
        else:
            return {"error": f"Unsupported format: {format}"}


class TwinMetricsQuery(BaseModel):
    """Query model for twin registry metrics with comprehensive filtering options"""
    
    model_config = ConfigDict(from_attributes=True)
    
    # Basic Filters
    registry_id: Optional[str] = Field(default=None, description="Registry ID")
    start_timestamp: Optional[datetime] = Field(default=None, description="Start timestamp for query")
    end_timestamp: Optional[datetime] = Field(default=None, description="End timestamp for query")
    min_health_score: Optional[int] = Field(default=None, ge=0, le=100, description="Minimum health score")
    max_health_score: Optional[int] = Field(default=None, ge=0, le=100, description="Maximum health score")
    
    # Enterprise Compliance Filters
    min_enterprise_compliance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Minimum enterprise compliance score")
    max_enterprise_compliance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Maximum enterprise compliance score")
    compliance_audit_status: Optional[str] = Field(default=None, description="Compliance audit status")
    min_compliance_violations: Optional[int] = Field(default=None, ge=0, description="Minimum compliance violations")
    max_compliance_violations: Optional[int] = Field(default=None, ge=0, description="Maximum compliance violations")
    
    # Enterprise Security Filters
    min_enterprise_security_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Minimum enterprise security score")
    max_enterprise_security_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Maximum enterprise security score")
    security_threat_level: Optional[str] = Field(default=None, description="Security threat level")
    min_security_vulnerabilities: Optional[int] = Field(default=None, ge=0, description="Minimum security vulnerabilities")
    max_security_vulnerabilities: Optional[int] = Field(default=None, ge=0, description="Maximum security vulnerabilities")
    security_scan_frequency: Optional[str] = Field(default=None, description="Security scan frequency")
    
    # Enterprise Performance Filters
    min_enterprise_performance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Minimum enterprise performance score")
    max_enterprise_performance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Maximum enterprise performance score")
    performance_optimization_status: Optional[str] = Field(default=None, description="Optimization status")
    min_optimization_efficiency: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Minimum optimization efficiency")
    max_optimization_efficiency: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Maximum optimization efficiency")
    
    # Data Quality Filters
    min_data_freshness_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Minimum data freshness score")
    max_data_freshness_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Maximum data freshness score")
    min_data_completeness_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Minimum data completeness score")
    max_data_completeness_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Maximum data completeness score")
    min_data_consistency_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Minimum data consistency score")
    max_data_consistency_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Maximum data consistency score")
    min_data_accuracy_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Minimum data accuracy score")
    max_data_accuracy_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Maximum data accuracy score")
    
    # System Resource Filters
    min_cpu_usage: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Minimum CPU usage percentage")
    max_cpu_usage: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Maximum CPU usage percentage")
    min_memory_usage: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Minimum memory usage percentage")
    max_memory_usage: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Maximum memory usage percentage")
    min_storage_usage: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Minimum storage usage percentage")
    max_storage_usage: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Maximum storage usage percentage")
    
    # Time-based Filters
    hour_of_day: Optional[int] = Field(default=None, ge=0, le=23, description="Hour of day (0-23)")
    day_of_week: Optional[int] = Field(default=None, ge=1, le=7, description="Day of week (1-7)")
    month: Optional[int] = Field(default=None, ge=1, le=12, description="Month (1-12)")
    
    # Performance Trend Filters
    min_twin_management_trend: Optional[float] = Field(default=None, description="Minimum twin management trend")
    max_twin_management_trend: Optional[float] = Field(default=None, description="Maximum twin management trend")
    min_resource_efficiency_trend: Optional[float] = Field(default=None, description="Minimum resource efficiency trend")
    max_resource_efficiency_trend: Optional[float] = Field(default=None, description="Maximum resource efficiency trend")
    min_quality_trend: Optional[float] = Field(default=None, description="Minimum quality trend")
    max_quality_trend: Optional[float] = Field(default=None, description="Maximum quality trend")
    
    # Pagination and Limits
    limit: int = Field(default=100, ge=1, le=1000, description="Number of results per page")
    offset: int = Field(default=0, ge=0, description="Number of results to skip")
    
    async def validate(self) -> bool:
        """Validate query parameters asynchronously with enhanced validation"""
        # Simulate async validation
        await asyncio.sleep(0.001)
        
        # Validate score ranges
        if self.min_health_score is not None and (self.min_health_score < 0 or self.min_health_score > 100):
            return False
        if self.max_health_score is not None and (self.max_health_score < 0 or self.max_health_score > 100):
            return False
            
        # Validate enterprise score ranges
        for field in ['min_enterprise_compliance_score', 'max_enterprise_compliance_score',
                     'min_enterprise_security_score', 'max_enterprise_security_score',
                     'min_enterprise_performance_score', 'max_enterprise_performance_score']:
            value = getattr(self, field)
            if value is not None and (value < 0.0 or value > 1.0):
                return False
        
        # Validate data quality score ranges
        for field in ['min_data_freshness_score', 'max_data_freshness_score',
                     'min_data_completeness_score', 'max_data_completeness_score',
                     'min_data_consistency_score', 'max_data_consistency_score',
                     'min_data_accuracy_score', 'max_data_accuracy_score']:
            value = getattr(self, field)
            if value is not None and (value < 0.0 or value > 1.0):
                return False
        
        # Validate system resource ranges
        for field in ['min_cpu_usage', 'max_cpu_usage', 'min_memory_usage', 'max_memory_usage',
                     'min_storage_usage', 'max_storage_usage']:
            value = getattr(self, field)
            if value is not None and (value < 0.0 or value > 100.0):
                return False
        
        # Validate time ranges
        if self.hour_of_day is not None and (self.hour_of_day < 0 or self.hour_of_day > 23):
            return False
        if self.day_of_week is not None and (self.day_of_week < 1 or self.day_of_week > 7):
            return False
        if self.month is not None and (self.month < 1 or self.month > 12):
            return False
        
        # Validate pagination
        if self.limit < 1 or self.limit > 1000:
            return False
        if self.offset < 0:
            return False
            
        return True
    
    def get_filter_summary(self) -> Dict[str, Any]:
        """Get a summary of active filters for logging/debugging"""
        active_filters = {}
        
        for field, value in self.__dict__.items():
            if value is not None and field not in ['limit', 'offset']:
                active_filters[field] = value
                
        return {
            'active_filters': active_filters,
            'total_filters': len(active_filters),
            'pagination': {'limit': self.limit, 'offset': self.offset}
        }


class TwinMetricsSummary(BaseModel):
    """Summary model for metrics statistics with comprehensive enterprise analytics"""
    
    model_config = ConfigDict(from_attributes=True)
    
    # Basic Metrics
    total_metrics: int
    average_health_score: float
    average_response_time: float
    metrics_by_registry: Dict[str, int]
    metrics_by_timestamp: Dict[str, int]
    
    # Enterprise Compliance Summary
    average_enterprise_compliance_score: float
    metrics_by_compliance_audit_status: Dict[str, int]
    total_compliance_violations: int
    compliance_trend: str = "stable"  # improving, stable, degrading
    compliance_risk_level: str = "low"  # low, medium, high, critical
    
    # Enterprise Security Summary
    average_enterprise_security_score: float
    metrics_by_security_threat_level: Dict[str, int]
    total_security_vulnerabilities: int
    average_incident_response_time: float
    security_trend: str = "stable"  # improving, stable, degrading
    security_risk_level: str = "low"  # low, medium, high, critical
    
    # Enterprise Performance Summary
    average_enterprise_performance_score: float
    metrics_by_optimization_status: Dict[str, int]
    average_optimization_efficiency: float
    performance_trend: str = "stable"  # improving, stable, degrading
    performance_optimization_opportunities: List[str] = []
    
    # Data Quality Summary
    average_data_freshness_score: float
    average_data_completeness_score: float
    average_data_consistency_score: float
    average_data_accuracy_score: float
    data_quality_trend: str = "stable"  # improving, stable, degrading
    data_quality_issues: List[str] = []
    
    # System Resource Summary
    average_cpu_usage: float
    average_memory_usage: float
    average_storage_usage: float
    resource_utilization_trend: str = "stable"  # improving, stable, degrading
    resource_optimization_opportunities: List[str] = []
    
    # Time-based Summary
    metrics_by_hour: Dict[int, int]
    metrics_by_day: Dict[int, int]
    metrics_by_month: Dict[int, int]
    peak_usage_hours: List[int] = []
    low_usage_hours: List[int] = []
    
    # Performance Trends Summary
    average_twin_management_trend: float
    average_resource_efficiency_trend: float
    average_quality_trend: float
    trend_analysis: Dict[str, str] = {}  # trend direction for each metric
    
    # Enterprise Risk Assessment
    overall_risk_score: float = Field(default=0.0, ge=0.0, le=1.0, description="0.0-1.0 overall risk assessment")
    risk_factors: List[str] = []  # List of identified risk factors
    risk_mitigation_suggestions: List[str] = []  # Suggested risk mitigation actions
    
    # Business Intelligence
    key_performance_indicators: Dict[str, float] = {}  # KPI values
    optimization_recommendations: List[str] = []  # System optimization suggestions
    cost_analysis: Dict[str, float] = {}  # Cost-related metrics
    
    async def calculate_totals(self) -> None:
        """Calculate totals asynchronously with enhanced analytics"""
        # Simulate async calculation
        await asyncio.sleep(0.001)
        
        # Basic calculations
        self.total_metrics = sum(self.metrics_by_registry.values())
        self.average_health_score = sum(self.metrics_by_registry.values()) / len(self.metrics_by_registry) if self.metrics_by_registry else 0.0
        self.average_response_time = sum(self.metrics_by_timestamp.values()) / len(self.metrics_by_timestamp) if self.metrics_by_timestamp else 0.0
        
        # Calculate trends
        await self._calculate_trends()
        
        # Calculate risk assessment
        await self._calculate_risk_assessment()
        
        # Generate optimization recommendations
        await self._generate_optimization_recommendations()
    
    async def _calculate_trends(self) -> None:
        """Calculate trend analysis for various metrics"""
        # Simulate async calculation
        await asyncio.sleep(0.001)
        
        # Determine compliance trend
        if self.average_enterprise_compliance_score > 0.8:
            self.compliance_trend = "improving"
        elif self.average_enterprise_compliance_score < 0.6:
            self.compliance_trend = "degrading"
        else:
            self.compliance_trend = "stable"
            
        # Determine security trend
        if self.average_enterprise_security_score > 0.8:
            self.security_trend = "improving"
        elif self.average_enterprise_security_score < 0.6:
            self.security_trend = "degrading"
        else:
            self.security_trend = "stable"
            
        # Determine performance trend
        if self.average_enterprise_performance_score > 0.8:
            self.performance_trend = "improving"
        elif self.average_enterprise_performance_score < 0.6:
            self.performance_trend = "degrading"
        else:
            self.performance_trend = "stable"
    
    async def _calculate_risk_assessment(self) -> None:
        """Calculate overall risk assessment based on various metrics"""
        # Simulate async calculation
        await asyncio.sleep(0.001)
        
        risk_scores = []
        risk_factors = []
        
        # Compliance risk
        if self.average_enterprise_compliance_score < 0.7:
            risk_scores.append(0.8)
            risk_factors.append("Low compliance score")
        elif self.average_enterprise_compliance_score < 0.8:
            risk_scores.append(0.4)
            risk_factors.append("Moderate compliance concerns")
            
        # Security risk
        if self.average_enterprise_security_score < 0.7:
            risk_scores.append(0.9)
            risk_factors.append("Low security score")
        elif self.average_enterprise_security_score < 0.8:
            risk_scores.append(0.5)
            risk_factors.append("Moderate security concerns")
            
        # Performance risk
        if self.average_enterprise_performance_score < 0.6:
            risk_scores.append(0.7)
            risk_factors.append("Low performance score")
        elif self.average_enterprise_performance_score < 0.7:
            risk_scores.append(0.3)
            risk_factors.append("Moderate performance concerns")
            
        # Calculate overall risk score
        self.overall_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0.0
        self.risk_factors = risk_factors
        
        # Determine risk level
        if self.overall_risk_score > 0.7:
            self.compliance_risk_level = "critical"
            self.security_risk_level = "critical"
        elif self.overall_risk_score > 0.5:
            self.compliance_risk_level = "high"
            self.security_risk_level = "high"
        elif self.overall_risk_score > 0.3:
            self.compliance_risk_level = "medium"
            self.security_risk_level = "medium"
        else:
            self.compliance_risk_level = "low"
            self.security_risk_level = "low"
    
    async def _generate_optimization_recommendations(self) -> None:
        """Generate optimization recommendations based on metrics"""
        # Simulate async calculation
        await asyncio.sleep(0.001)
        
        recommendations = []
        
        # Performance recommendations
        if self.average_enterprise_performance_score < 0.7:
            recommendations.append("Consider performance optimization for twin registry operations")
        if self.average_optimization_efficiency < 0.6:
            recommendations.append("Review and optimize resource allocation strategies")
            
        # Security recommendations
        if self.average_enterprise_security_score < 0.7:
            recommendations.append("Implement additional security measures and monitoring")
        if self.total_security_vulnerabilities > 5:
            recommendations.append("Prioritize security vulnerability remediation")
            
        # Compliance recommendations
        if self.average_enterprise_compliance_score < 0.7:
            recommendations.append("Review compliance policies and implement corrective actions")
        if self.total_compliance_violations > 3:
            recommendations.append("Address compliance violations and update procedures")
            
        # Resource optimization
        if self.average_cpu_usage > 80:
            recommendations.append("Consider CPU optimization or scaling")
        if self.average_memory_usage > 80:
            recommendations.append("Review memory usage patterns and optimize allocation")
        if self.average_storage_usage > 85:
            recommendations.append("Implement storage optimization and cleanup procedures")
            
        self.optimization_recommendations = recommendations

# Standalone factory function for creating new twin registry metrics
async def create_metrics(
    registry_id: str,
    health_score: Optional[int] = None,
    response_time_ms: Optional[float] = None,
    **kwargs
) -> TwinRegistryMetrics:
    """
    Async factory function to create a new twin registry metrics entry.
    
    Args:
        registry_id: Reference to twin_registry table
        health_score: Current health score (0-100)
        response_time_ms: Response time in milliseconds
        **kwargs: Additional fields to set
        
    Returns:
        TwinRegistryMetrics: New twin registry metrics instance
    """
    now = datetime.now(timezone.utc)
    
    # Simulate async operation
    await asyncio.sleep(0.001)
    
    return TwinRegistryMetrics(
        registry_id=registry_id,
        timestamp=now,
        health_score=health_score,
        response_time_ms=response_time_ms,
        **kwargs
    )
