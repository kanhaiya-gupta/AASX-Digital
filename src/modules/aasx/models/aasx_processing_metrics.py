"""
AASX Processing Metrics Model

Pydantic model for the aasx_processing_metrics table with pure async support.
Extends the engine BaseModel and represents the existing database schema.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from pydantic_core import PydanticCustomError
import asyncio

from src.engine.models.base_model import BaseModel as EngineBaseModel


class AasxProcessingMetrics(EngineBaseModel):
    """
    AASX Processing Metrics Model - Performance and Health Monitoring
    
    Represents the aasx_processing_metrics table with comprehensive metrics tracking,
    performance analysis, and health monitoring for AASX processing operations.
    Pure async implementation for modern architecture.
    """
    
    # Primary Identification
    metric_id: Optional[int] = Field(None, description="Unique metric identifier")
    job_id: str = Field(..., description="Reference to the AASX processing job")
    timestamp: str = Field(..., description="When this metric was recorded")
    
    # Real-time Health Metrics (Framework Health)
    health_score: Optional[int] = Field(None, ge=0, le=100, description="Current health score (0-100)")
    response_time_ms: Optional[float] = Field(None, ge=0.0, description="Response time in milliseconds")
    uptime_percentage: Optional[float] = Field(None, ge=0.0, le=100.0, description="Uptime percentage")
    error_rate: Optional[float] = Field(None, ge=0.0, le=1.0, description="Error rate (0.0-1.0)")
    
    # AASX Processing Performance Metrics (Framework Performance)
    processing_time_trend: Optional[float] = Field(None, description="Processing time trend analysis")
    extraction_speed_sec: Optional[float] = Field(None, ge=0.0, description="Extraction speed in seconds")
    generation_speed_sec: Optional[float] = Field(None, ge=0.0, description="Generation speed in seconds")
    validation_speed_sec: Optional[float] = Field(None, ge=0.0, description="Validation speed in seconds")
    aasx_processing_efficiency: Optional[float] = Field(None, ge=0.0, le=1.0, description="AASX processing efficiency")
    
    # AASX Management Performance (JSON for better framework analysis)
    aasx_management_performance: Dict[str, Any] = Field(default_factory=dict, description="JSON: file_processing, data_extraction, model_generation, validation_quality")
    
    # AASX Category Performance Metrics (JSON for better framework analysis)
    aasx_category_performance_stats: Dict[str, Any] = Field(default_factory=dict, description="JSON: manufacturing, energy, component, facility, process, generic")
    
    # User Interaction Metrics (Framework Usage)
    user_interaction_count: int = Field(default=0, ge=0, description="Number of user interactions")
    file_access_count: int = Field(default=0, ge=0, description="Number of file accesses")
    successful_operations: int = Field(default=0, ge=0, description="Successful operations")
    failed_operations: int = Field(default=0, ge=0, description="Failed operations")
    job_execution_count: int = Field(default=0, ge=0, description="Number of jobs executed")
    successful_processing_operations: int = Field(default=0, ge=0, description="Successful processing operations")
    failed_processing_operations: int = Field(default=0, ge=0, description="Failed processing operations")
    
    # Data Quality Metrics (Framework Quality)
    data_freshness_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Data freshness score")
    data_completeness_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Data completeness score")
    data_consistency_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Data consistency score")
    data_accuracy_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Data accuracy score")
    
    # System Resource Metrics (Framework Resources)
    cpu_usage_percent: Optional[float] = Field(None, ge=0.0, le=100.0, description="CPU usage percentage")
    memory_usage_percent: Optional[float] = Field(None, ge=0.0, le=100.0, description="Memory usage percentage")
    network_throughput_mbps: Optional[float] = Field(None, ge=0.0, description="Network throughput in Mbps")
    storage_usage_percent: Optional[float] = Field(None, ge=0.0, le=100.0, description="Storage usage percentage")
    disk_io_mb: Optional[float] = Field(None, ge=0.0, description="Disk I/O in MB")
    
    # AASX Processing Patterns & Analytics (Framework Trends - JSON)
    aasx_processing_patterns: Dict[str, Any] = Field(default_factory=dict, description="JSON: hourly, daily, weekly, monthly")
    resource_utilization_trends: Dict[str, Any] = Field(default_factory=dict, description="JSON: cpu_trend, memory_trend, disk_trend")
    user_activity: Dict[str, Any] = Field(default_factory=dict, description="JSON: peak_hours, user_patterns, session_durations")
    file_operation_patterns: Dict[str, Any] = Field(default_factory=dict, description="JSON: operation_types, complexity_distribution, processing_times")
    compliance_status: Dict[str, Any] = Field(default_factory=dict, description="JSON: compliance_score, audit_status, last_audit")
    security_events: Dict[str, Any] = Field(default_factory=dict, description="JSON: events, threat_level, last_security_scan")
    
    # Processing Patterns & Analytics (Framework Trends - JSON)
    processing_patterns: Dict[str, Any] = Field(default_factory=dict, description="JSON: hourly, daily, weekly, monthly patterns")
    job_patterns: Dict[str, Any] = Field(default_factory=dict, description="JSON: job types, complexity distribution, processing times")
    
    # AASX Processing-Specific Metrics (Framework Capabilities - JSON)
    aasx_processing_analytics: Dict[str, Any] = Field(default_factory=dict, description="JSON: extraction_quality, generation_quality, validation_quality")
    category_effectiveness: Dict[str, Any] = Field(default_factory=dict, description="JSON: category_comparison, best_performing, optimization_suggestions")
    workflow_performance: Dict[str, Any] = Field(default_factory=dict, description="JSON: extraction_performance, generation_performance, hybrid_performance")
    file_size_performance_efficiency: Dict[str, Any] = Field(default_factory=dict, description="JSON: performance_by_file_size, quality_by_file_size, optimization_opportunities")
    
    # Processing Technique Performance (JSON for better framework analysis)
    processing_technique_performance: Dict[str, Any] = Field(default_factory=dict, description="JSON: extraction, generation, validation, batch_processing, streaming_processing")
    
    # File Type Processing Metrics (JSON for better framework analysis)
    file_type_processing_stats: Dict[str, Any] = Field(default_factory=dict, description="JSON: aasx, json, yaml, xml, ttl processing statistics")
    
    # AASX-Specific Metrics (Framework Capabilities - JSON)
    aasx_analytics: Dict[str, Any] = Field(default_factory=dict, description="JSON: extraction_quality, generation_quality, validation_quality")
    technique_effectiveness: Dict[str, Any] = Field(default_factory=dict, description="JSON: technique comparison, best performing, optimization suggestions")
    format_performance: Dict[str, Any] = Field(default_factory=dict, description="JSON: aasx, json, yaml, xml, ttl performance")
    file_size_processing_efficiency: Dict[str, Any] = Field(default_factory=dict, description="JSON: processing speed by size, quality by size, optimization opportunities")
    
    # Time-based Analytics (Framework Time Analysis)
    hour_of_day: Optional[int] = Field(None, ge=0, le=23, description="Hour of day (0-23)")
    day_of_week: Optional[int] = Field(None, ge=1, le=7, description="Day of week (1-7)")
    month: Optional[int] = Field(None, ge=1, le=12, description="Month (1-12)")
    
    # Performance Trends (Framework Performance Analysis)
    aasx_management_trend: Optional[float] = Field(None, description="Compared to historical average")
    resource_efficiency_trend: Optional[float] = Field(None, description="Performance over time")
    quality_trend: Optional[float] = Field(None, description="Quality metrics over time")
    
    # Timestamps
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    
    # Pydantic Configuration
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_id": "aasx_job_001",
                "timestamp": "2025-08-20T10:00:00Z",
                "health_score": 95,
                "response_time_ms": 150.5,
                "uptime_percentage": 99.8,
                "error_rate": 0.02,
                "extraction_speed_sec": 2.5,
                "generation_speed_sec": 3.2,
                "validation_speed_sec": 1.8,
                "cpu_usage_percent": 45.2,
                "memory_usage_percent": 62.1
            }
        },
        validate_assignment=True,
        extra="forbid"
    )
    
    # Field Validators
    @field_validator('health_score')
    @classmethod
    def validate_health_score(cls, v: Optional[int]) -> Optional[int]:
        """Validate health score range."""
        if v is not None and (v < 0 or v > 100):
            raise PydanticCustomError(
                'invalid_health_score',
                'Health score must be between 0 and 100'
            )
        return v
    
    @field_validator('uptime_percentage')
    @classmethod
    def validate_uptime_percentage(cls, v: Optional[float]) -> Optional[float]:
        """Validate uptime percentage range."""
        if v is not None and (v < 0.0 or v > 100.0):
            raise PydanticCustomError(
                'invalid_uptime_percentage',
                'Uptime percentage must be between 0.0 and 100.0'
            )
        return v
    
    @field_validator('error_rate')
    @classmethod
    def validate_error_rate(cls, v: Optional[float]) -> Optional[float]:
        """Validate error rate range."""
        if v is not None and (v < 0.0 or v > 1.0):
            raise PydanticCustomError(
                'invalid_error_rate',
                'Error rate must be between 0.0 and 1.0'
            )
        return v
    
    @field_validator('hour_of_day')
    @classmethod
    def validate_hour_of_day(cls, v: Optional[int]) -> Optional[int]:
        """Validate hour of day range."""
        if v is not None and (v < 0 or v > 23):
            raise PydanticCustomError(
                'invalid_hour_of_day',
                'Hour of day must be between 0 and 23'
            )
        return v
    
    @field_validator('day_of_week')
    @classmethod
    def validate_day_of_week(cls, v: Optional[int]) -> Optional[int]:
        """Validate day of week range."""
        if v is not None and (v < 1 or v > 7):
            raise PydanticCustomError(
                'invalid_day_of_week',
                'Day of week must be between 1 and 7'
            )
        return v
    
    @field_validator('month')
    @classmethod
    def validate_month(cls, v: Optional[int]) -> Optional[int]:
        """Validate month range."""
        if v is not None and (v < 1 or v > 12):
            raise PydanticCustomError(
                'invalid_month',
                'Month must be between 1 and 12'
            )
        return v
    
    # Model Validators
    @model_validator(mode='after')
    def validate_processing_speeds(self) -> 'AasxProcessingMetrics':
        """Validate that processing speeds are reasonable."""
        if self.extraction_speed_sec is not None and self.extraction_speed_sec < 0:
            raise PydanticCustomError(
                'invalid_extraction_speed',
                'Extraction speed cannot be negative'
            )
        
        if self.generation_speed_sec is not None and self.generation_speed_sec < 0:
            raise PydanticCustomError(
                'invalid_generation_speed',
                'Generation speed cannot be negative'
            )
        
        if self.validation_speed_sec is not None and self.validation_speed_sec < 0:
            raise PydanticCustomError(
                'invalid_validation_speed',
                'Validation speed cannot be negative'
            )
        
        return self
    
    # Pure Async Business Logic Methods
    
    async def update_health_score(self, new_score: int) -> None:
        """Update health score asynchronously."""
        if 0 <= new_score <= 100:
            self.health_score = new_score
            self.timestamp = datetime.now().isoformat()
            self.updated_at = self.timestamp
            
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def update_performance_metrics(
        self,
        cpu: Optional[float] = None,
        memory: Optional[float] = None,
        network: Optional[float] = None,
        storage: Optional[float] = None,
        disk_io: Optional[float] = None
    ) -> None:
        """Update performance metrics asynchronously."""
        if cpu is not None:
            self.cpu_usage_percent = cpu
        if memory is not None:
            self.memory_usage_percent = memory
        if network is not None:
            self.network_throughput_mbps = network
        if storage is not None:
            self.storage_usage_percent = storage
        if disk_io is not None:
            self.disk_io_mb = disk_io
        
        self.timestamp = datetime.now().isoformat()
        self.updated_at = self.timestamp
        
        # Simulate async operation
        await asyncio.sleep(0.001)
    
    async def update_processing_speeds(
        self,
        extraction_speed: Optional[float] = None,
        generation_speed: Optional[float] = None,
        validation_speed: Optional[float] = None
    ) -> None:
        """Update AASX processing speeds asynchronously."""
        if extraction_speed is not None:
            self.extraction_speed_sec = extraction_speed
        if generation_speed is not None:
            self.generation_speed_sec = generation_speed
        if validation_speed is not None:
            self.validation_speed_sec = validation_speed
        
        self.timestamp = datetime.now().isoformat()
        self.updated_at = self.timestamp
        
        # Simulate async operation
        await asyncio.sleep(0.001)
    
    async def update_data_quality_scores(
        self,
        freshness_score: Optional[float] = None,
        completeness_score: Optional[float] = None,
        consistency_score: Optional[float] = None,
        accuracy_score: Optional[float] = None
    ) -> None:
        """Update data quality scores asynchronously."""
        if freshness_score is not None:
            self.data_freshness_score = freshness_score
        if completeness_score is not None:
            self.data_completeness_score = completeness_score
        if consistency_score is not None:
            self.data_consistency_score = consistency_score
        if accuracy_score is not None:
            self.data_accuracy_score = accuracy_score
        
        self.timestamp = datetime.now().isoformat()
        self.updated_at = self.timestamp
        
        # Simulate async operation
        await asyncio.sleep(0.001)
    
    async def add_aasx_management_performance(self, operation_type: str, metrics: Dict[str, Any]) -> None:
        """Add AASX management performance metrics asynchronously."""
        if isinstance(metrics, dict):
            self.aasx_management_performance[operation_type] = metrics
            self.updated_at = datetime.now().isoformat()
            
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def add_category_performance_stats(self, category: str, stats: Dict[str, Any]) -> None:
        """Add category performance statistics asynchronously."""
        if isinstance(stats, dict):
            self.aasx_category_performance_stats[category] = stats
            self.updated_at = datetime.now().isoformat()
            
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def add_resource_utilization_trend(self, resource_type: str, trend_data: List[float]) -> None:
        """Add resource utilization trend data asynchronously."""
        if isinstance(trend_data, list):
            self.resource_utilization_trends[resource_type] = trend_data
            self.updated_at = datetime.now().isoformat()
            
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def add_user_activity_pattern(self, pattern_type: str, pattern_data: Dict[str, Any]) -> None:
        """Add user activity pattern data asynchronously."""
        if isinstance(pattern_data, dict):
            self.user_activity[pattern_type] = pattern_data
            self.updated_at = datetime.now().isoformat()
            
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def add_file_operation_pattern(self, pattern_type: str, pattern_data: Dict[str, Any]) -> None:
        """Add file operation pattern data asynchronously."""
        if isinstance(pattern_data, dict):
            self.file_operation_patterns[pattern_type] = pattern_data
            self.updated_at = datetime.now().isoformat()
            
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def add_compliance_status(self, compliance_data: Dict[str, Any]) -> None:
        """Add compliance status information asynchronously."""
        if isinstance(compliance_data, dict):
            self.compliance_status.update(compliance_data)
            self.updated_at = datetime.now().isoformat()
            
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def add_security_event(self, event: Dict[str, Any]) -> None:
        """Add security event information asynchronously."""
        if isinstance(event, dict):
            if 'events' not in self.security_events:
                self.security_events['events'] = []
            self.security_events['events'].append(event)
            self.updated_at = datetime.now().isoformat()
            
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def add_aasx_processing_analytics(self, analytics_type: str, analytics_data: Dict[str, Any]) -> None:
        """Add AASX processing analytics asynchronously."""
        if isinstance(analytics_data, dict):
            self.aasx_processing_analytics[analytics_type] = analytics_data
            self.updated_at = datetime.now().isoformat()
            
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def add_workflow_performance(self, workflow_type: str, performance_data: Dict[str, Any]) -> None:
        """Add workflow performance data asynchronously."""
        if isinstance(performance_data, dict):
            self.workflow_performance[workflow_type] = performance_data
            self.updated_at = datetime.now().isoformat()
            
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def increment_user_interaction(self) -> None:
        """Increment user interaction count asynchronously."""
        self.user_interaction_count += 1
        self.timestamp = datetime.now().isoformat()
        self.updated_at = self.timestamp
        
        # Simulate async operation
        await asyncio.sleep(0.001)
    
    async def increment_file_access(self) -> None:
        """Increment file access count asynchronously."""
        self.file_access_count += 1
        self.timestamp = datetime.now().isoformat()
        self.updated_at = self.timestamp
        
        # Simulate async operation
        await asyncio.sleep(0.001)
    
    async def record_successful_operation(self) -> None:
        """Record successful operation asynchronously."""
        self.successful_operations += 1
        self.timestamp = datetime.now().isoformat()
        self.updated_at = self.timestamp
        
        # Simulate async operation
        await asyncio.sleep(0.001)
    
    async def record_failed_operation(self) -> None:
        """Record failed operation asynchronously."""
        self.failed_operations += 1
        self.timestamp = datetime.now().isoformat()
        self.updated_at = self.timestamp
        
        # Simulate async operation
        await asyncio.sleep(0.001)
    
    async def update_time_based_analytics(
        self,
        hour_of_day: Optional[int] = None,
        day_of_week: Optional[int] = None,
        month: Optional[int] = None
    ) -> None:
        """Update time-based analytics asynchronously."""
        if hour_of_day is not None and 0 <= hour_of_day <= 23:
            self.hour_of_day = hour_of_day
        if day_of_week is not None and 1 <= day_of_week <= 7:
            self.day_of_week = day_of_week
        if month is not None and 1 <= month <= 12:
            self.month = month
        
        self.timestamp = datetime.now().isoformat()
        self.updated_at = self.timestamp
        
        # Simulate async operation
        await asyncio.sleep(0.001)
    
    async def update_performance_trends(
        self,
        aasx_management_trend: Optional[float] = None,
        resource_efficiency_trend: Optional[float] = None,
        quality_trend: Optional[float] = None
    ) -> None:
        """Update performance trends asynchronously."""
        if aasx_management_trend is not None:
            self.aasx_management_trend = aasx_management_trend
        if resource_efficiency_trend is not None:
            self.resource_efficiency_trend = resource_efficiency_trend
        if quality_trend is not None:
            self.quality_trend = quality_trend
        
        self.timestamp = datetime.now().isoformat()
        self.updated_at = self.timestamp
        
        # Simulate async operation
        await asyncio.sleep(0.001)
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary asynchronously."""
        # Simulate async operation
        await asyncio.sleep(0.001)
        
        return {
            'health_score': self.health_score,
            'response_time_ms': self.response_time_ms,
            'uptime_percentage': self.uptime_percentage,
            'error_rate': self.error_rate,
            'extraction_speed_sec': self.extraction_speed_sec,
            'generation_speed_sec': self.generation_speed_sec,
            'validation_speed_sec': self.validation_speed_sec,
            'aasx_processing_efficiency': self.aasx_processing_efficiency,
            'cpu_usage_percent': self.cpu_usage_percent,
            'memory_usage_percent': self.memory_usage_percent,
            'storage_usage_percent': self.storage_usage_percent
        }
    
    async def get_quality_summary(self) -> Dict[str, Any]:
        """Get data quality summary asynchronously."""
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
        """Get usage summary asynchronously."""
        # Simulate async operation
        await asyncio.sleep(0.001)
        
        return {
            'user_interaction_count': self.user_interaction_count,
            'file_access_count': self.file_access_count,
            'successful_operations': self.successful_operations,
            'failed_operations': self.failed_operations,
            'total_operations': self.successful_operations + self.failed_operations,
            'success_rate': self.successful_operations / (self.successful_operations + self.failed_operations) if (self.successful_operations + self.failed_operations) > 0 else 0.0
        }
    
    async def is_performing_well(self) -> bool:
        """Check if performance is good asynchronously."""
        # Simulate async operation
        await asyncio.sleep(0.001)
        
        return (
            self.health_score is not None and self.health_score >= 80 and
            self.response_time_ms is not None and self.response_time_ms < 1000 and
            self.error_rate is not None and self.error_rate < 0.05
        )
    
    async def requires_optimization(self) -> bool:
        """Check if optimization is needed asynchronously."""
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
        """Calculate overall efficiency score asynchronously."""
        # Simulate async calculation
        await asyncio.sleep(0.001)
        
        scores = []
        if self.health_score is not None:
            scores.append(self.health_score / 100.0)
        if self.aasx_processing_efficiency is not None:
            scores.append(self.aasx_processing_efficiency)
        if self.data_freshness_score is not None:
            scores.append(self.data_freshness_score)
        if self.data_completeness_score is not None:
            scores.append(self.data_completeness_score)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    async def validate(self) -> bool:
        """Validate metrics data asynchronously."""
        # Simulate async validation
        await asyncio.sleep(0.001)
        
        return (
            bool(self.job_id) and
            bool(self.timestamp)
        )
    
    # Async Methods for Database Operations
    async def save(self) -> bool:
        """Async method to save the model to database."""
        # This will be implemented in the repository layer
        raise NotImplementedError("Save method should be implemented in repository layer")
    
    async def update(self) -> bool:
        """Async method to update the model in database."""
        # This will be implemented in the repository layer
        raise NotImplementedError("Update method should be implemented in repository layer")
    
    async def delete(self) -> bool:
        """Async method to delete the model from database."""
        # This will be implemented in the repository layer
        raise NotImplementedError("Delete method should be implemented in repository layer")
    
    async def refresh(self) -> bool:
        """Async method to refresh the model from database."""
        # This will be implemented in the repository layer
        raise NotImplementedError("Refresh method should be implemented in repository layer")


# Pure async factory function for creating new AASX processing metrics
async def create_aasx_processing_metrics(
    job_id: str,
    health_score: Optional[int] = None,
    response_time_ms: Optional[float] = None,
    **kwargs
) -> AasxProcessingMetrics:
    """
    Async factory function to create new AASX processing metrics.
    
    Args:
        job_id: Reference to the AASX processing job
        health_score: Initial health score (0-100)
        response_time_ms: Initial response time in milliseconds
        **kwargs: Additional fields to set
        
    Returns:
        AasxProcessingMetrics: New metrics instance
    """
    now = datetime.now().isoformat()
    
    # Simulate async operation
    await asyncio.sleep(0.001)
    
    return AasxProcessingMetrics(
        job_id=job_id,
        timestamp=now,
        health_score=health_score,
        response_time_ms=response_time_ms,
        created_at=now,
        updated_at=now,
        **kwargs
    )


class MetricsQuery(BaseModel):
    """Query model for filtering metrics"""
    
    job_id: Optional[str] = None
    start_timestamp: Optional[str] = None
    end_timestamp: Optional[str] = None
    min_health_score: Optional[int] = None
    max_health_score: Optional[int] = None
    
    class Config:
        json_encoders = {
            str: lambda v: v
        }


class MetricsSummary(BaseModel):
    """Summary model for metrics statistics"""
    
    total_metrics: int
    average_health_score: float
    average_response_time: float
    metrics_by_job: Dict[str, int]
    metrics_by_timestamp: Dict[str, int]
    
    class Config:
        json_encoders = {
            str: lambda v: v
        }
