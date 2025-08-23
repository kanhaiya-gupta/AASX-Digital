"""
AI RAG Metrics Model
====================

Pydantic model for AI RAG metrics operations.
Pure async implementation following AASX and Twin Registry convention.
"""

import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from src.engine.models.base_model import BaseModel as EngineBaseModel


class AIRagMetrics(EngineBaseModel):
    """
    AI RAG Metrics Model - Pure Async Implementation
    
    Represents comprehensive performance metrics for AI RAG operations.
    Follows the same convention as AASX and Twin Registry modules.
    """
    
    # Primary Identification
    metric_id: Optional[int] = Field(None, description="Auto-incrementing metric ID")
    registry_id: str = Field(..., description="Associated registry ID")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Metric timestamp")
    
    # Real-time Health Metrics (Framework Health)
    health_score: Optional[int] = Field(None, ge=0, le=100, description="Health score (0-100)")
    response_time_ms: Optional[float] = Field(None, description="Response time in milliseconds")
    uptime_percentage: Optional[float] = Field(None, ge=0.0, le=100.0, description="Uptime percentage")
    error_rate: Optional[float] = Field(None, ge=0.0, le=1.0, description="Error rate (0.0-1.0)")
    
    # AI/RAG Performance Metrics (Framework Performance - NOT Data)
    embedding_generation_speed_sec: Optional[float] = Field(None, description="Time to generate embeddings in seconds")
    vector_db_query_response_time_ms: Optional[float] = Field(None, description="Vector DB query response time in milliseconds")
    rag_response_generation_time_ms: Optional[float] = Field(None, description="RAG response generation time in milliseconds")
    context_retrieval_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0, description="Context retrieval accuracy (0.0-1.0)")
    
    # RAG Technique Performance (JSON for better framework analysis)
    rag_technique_performance: Dict[str, Any] = Field(default_factory=dict, description="RAG technique performance metrics")
    document_processing_stats: Dict[str, Any] = Field(default_factory=dict, description="Document processing statistics")
    performance_trends: Dict[str, Any] = Field(default_factory=dict, description="Performance trends data")
    resource_utilization_trends: Dict[str, Any] = Field(default_factory=dict, description="Resource utilization trends")
    user_activity: Dict[str, Any] = Field(default_factory=dict, description="User activity patterns")
    query_patterns: Dict[str, Any] = Field(default_factory=dict, description="Query pattern analysis")
    compliance_status: Dict[str, Any] = Field(default_factory=dict, description="Compliance status information")
    security_events: Dict[str, Any] = Field(default_factory=dict, description="Security events tracking")
    
    # User Interaction Metrics (Framework Usage - NOT Content)
    user_interaction_count: int = Field(default=0, description="Number of user interactions")
    query_execution_count: int = Field(default=0, description="Number of queries executed")
    successful_rag_operations: int = Field(default=0, description="Successful RAG operations")
    failed_rag_operations: int = Field(default=0, description="Failed RAG operations")
    
    # Data Quality Metrics (Framework Quality - NOT Data Content)
    data_freshness_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Data freshness score (0.0-1.0)")
    data_completeness_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Data completeness score (0.0-1.0)")
    data_consistency_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Data consistency score (0.0-1.0)")
    data_accuracy_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Data accuracy score (0.0-1.0)")
    
    # System Resource Metrics (Framework Resources - NOT Data)
    cpu_usage_percent: Optional[float] = Field(None, ge=0.0, le=100.0, description="CPU usage percentage")
    memory_usage_percent: Optional[float] = Field(None, ge=0.0, le=100.0, description="Memory usage percentage")
    network_throughput_mbps: Optional[float] = Field(None, description="Network throughput in Mbps")
    storage_usage_percent: Optional[float] = Field(None, ge=0.0, le=100.0, description="Storage usage percentage")
    
    # AI/RAG-Specific Metrics (Framework Capabilities - JSON)
    rag_analytics: Dict[str, Any] = Field(default_factory=dict, description="RAG-specific analytics")
    technique_effectiveness: Dict[str, Any] = Field(default_factory=dict, description="Technique effectiveness analysis")
    model_performance: Dict[str, Any] = Field(default_factory=dict, description="Model performance metrics")
    file_type_processing_efficiency: Dict[str, Any] = Field(default_factory=dict, description="File type processing efficiency")
    
    # Timestamps
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Creation timestamp")
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Last update timestamp")
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }
        validate_assignment = True
        arbitrary_types_allowed = True
    
    # Validators
    @validator('health_score')
    def validate_health_score(cls, v):
        """Validate health score"""
        if v is not None and not 0 <= v <= 100:
            raise ValueError('Health score must be between 0 and 100')
        return v
    
    @validator('uptime_percentage')
    def validate_uptime_percentage(cls, v):
        """Validate uptime percentage"""
        if v is not None and not 0.0 <= v <= 100.0:
            raise ValueError('Uptime percentage must be between 0.0 and 100.0')
        return v
    
    @validator('error_rate')
    def validate_error_rate(cls, v):
        """Validate error rate"""
        if v is not None and not 0.0 <= v <= 1.0:
            raise ValueError('Error rate must be between 0.0 and 1.0')
        return v
    
    @validator('context_retrieval_accuracy')
    def validate_context_retrieval_accuracy(cls, v):
        """Validate context retrieval accuracy"""
        if v is not None and not 0.0 <= v <= 1.0:
            raise ValueError('Context retrieval accuracy must be between 0.0 and 1.0')
        return v
    
    @validator('data_freshness_score', 'data_completeness_score', 'data_consistency_score', 'data_accuracy_score')
    def validate_data_quality_scores(cls, v):
        """Validate data quality scores"""
        if v is not None and not 0.0 <= v <= 1.0:
            raise ValueError('Data quality score must be between 0.0 and 1.0')
        return v
    
    @validator('cpu_usage_percent', 'memory_usage_percent', 'storage_usage_percent')
    def validate_usage_percentages(cls, v):
        """Validate usage percentages"""
        if v is not None and not 0.0 <= v <= 100.0:
            raise ValueError('Usage percentage must be between 0.0 and 100.0')
        return v
    
    # Async methods for database operations
    async def save_to_database(self) -> bool:
        """Save the metrics to database - to be implemented with repository"""
        # This will be implemented when we create the repository
        raise NotImplementedError("Repository not yet implemented")
    
    async def update_in_database(self) -> bool:
        """Update the metrics in database - to be implemented with repository"""
        # This will be implemented when we create the repository
        raise NotImplementedError("Repository not yet implemented")
    
    async def delete_from_database(self) -> bool:
        """Delete the metrics from database - to be implemented with repository"""
        # This will be implemented when we create the repository
        raise NotImplementedError("Repository not yet implemented")
    
    # Business logic methods
    def calculate_overall_health_score(self) -> int:
        """Calculate overall health score based on various metrics"""
        if self.health_score is not None:
            return self.health_score
        
        # Calculate from component scores
        base_score = 50
        component_scores = []
        
        # Performance component (up to 25 points)
        if self.response_time_ms is not None:
            if self.response_time_ms < 100:  # Fast response
                component_scores.append(25)
            elif self.response_time_ms < 500:  # Good response
                component_scores.append(20)
            elif self.response_time_ms < 1000:  # Acceptable response
                component_scores.append(15)
            else:  # Slow response
                component_scores.append(10)
        
        # Quality component (up to 25 points)
        if self.data_quality_score is not None:
            component_scores.append(int(self.data_quality_score * 25))
        
        # Availability component (up to 25 points)
        if self.uptime_percentage is not None:
            component_scores.append(int(self.uptime_percentage * 0.25))
        
        # Calculate final score
        if component_scores:
            final_score = base_score + sum(component_scores) / len(component_scores)
            return min(int(final_score), 100)
        
        return base_score
    
    def is_healthy(self) -> bool:
        """Check if the metrics indicate healthy operation"""
        health_score = self.calculate_overall_health_score()
        return health_score >= 70
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of performance metrics"""
        return {
            "health_score": self.calculate_overall_health_score(),
            "response_time_ms": self.response_time_ms,
            "uptime_percentage": self.uptime_percentage,
            "error_rate": self.error_rate,
            "embedding_generation_speed_sec": self.embedding_generation_speed_sec,
            "vector_db_query_response_time_ms": self.vector_db_query_response_time_ms,
            "rag_response_generation_time_ms": self.rag_response_generation_time_ms,
            "context_retrieval_accuracy": self.context_retrieval_accuracy
        }
    
    def get_resource_utilization(self) -> Dict[str, Any]:
        """Get resource utilization summary"""
        return {
            "cpu_usage_percent": self.cpu_usage_percent,
            "memory_usage_percent": self.memory_usage_percent,
            "network_throughput_mbps": self.network_throughput_mbps,
            "storage_usage_percent": self.storage_usage_percent
        }
    
    def get_data_quality_summary(self) -> Dict[str, Any]:
        """Get data quality summary"""
        return {
            "freshness_score": self.data_freshness_score,
            "completeness_score": self.data_completeness_score,
            "consistency_score": self.data_consistency_score,
            "accuracy_score": self.data_accuracy_score
        }
    
    def get_rag_technique_performance(self, technique_name: str) -> Optional[Dict[str, Any]]:
        """Get performance metrics for a specific RAG technique"""
        return self.rag_technique_performance.get(technique_name)
    
    def get_document_processing_stats(self, file_type: str) -> Optional[Dict[str, Any]]:
        """Get processing statistics for a specific file type"""
        return self.document_processing_stats.get(file_type)
    
    def get_performance_trend(self, trend_type: str) -> Optional[Dict[str, Any]]:
        """Get performance trend data for a specific type"""
        return self.performance_trends.get(trend_type)
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return self.dict()
    
    def to_json(self) -> str:
        """Convert model to JSON string"""
        return self.json()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIRagMetrics':
        """Create model from dictionary"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AIRagMetrics':
        """Create model from JSON string"""
        data = json.loads(json_str)
        return cls(**data)
    
    @classmethod
    def create_performance_metrics(cls, registry_id: str, **kwargs) -> 'AIRagMetrics':
        """Create performance metrics with default values"""
        return cls(
            registry_id=registry_id,
            **kwargs
        )
    
    @classmethod
    def create_health_metrics(cls, registry_id: str, health_score: int, **kwargs) -> 'AIRagMetrics':
        """Create health metrics with specified health score"""
        return cls(
            registry_id=registry_id,
            health_score=health_score,
            **kwargs
        )
    
    @classmethod
    def create_performance_metrics(cls, registry_id: str, response_time_ms: float, **kwargs) -> 'AIRagMetrics':
        """Create performance metrics with response time"""
        return cls(
            registry_id=registry_id,
            response_time_ms=response_time_ms,
            **kwargs
        )
