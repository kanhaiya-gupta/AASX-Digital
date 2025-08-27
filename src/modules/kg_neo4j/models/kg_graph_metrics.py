"""
Knowledge Graph Metrics Model

Comprehensive metrics model for knowledge graph performance, health, and analytics.
Supports real-time monitoring, ML training metrics, and enterprise-grade analytics.
Enhanced with computed fields and business intelligence methods.
"""

from src.engine.models.engine_base_model import EngineBaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from pydantic import Field, ConfigDict, computed_field
import uuid
import asyncio


class KGGraphMetrics(EngineBaseModel):
    """
    Metrics model for knowledge graph performance, health, and analytics.
    
    This model represents the kg_graph_metrics table with all fields from the database schema.
    Supports real-time monitoring, ML training metrics, and enterprise-grade analytics.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    # Primary Identification
    metric_id: int = Field(..., description="Unique metric identifier")
    graph_id: str = Field(..., description="Reference to kg_graph_registry")
    timestamp: datetime = Field(..., description="Timestamp when metrics were recorded")
    
    # Real-time Health Metrics (Framework Health)
    health_score: Optional[int] = Field(default=None, ge=0, le=100, description="Real-time health score (0-100)")
    response_time_ms: Optional[float] = Field(default=None, description="Response time in milliseconds")
    uptime_percentage: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Uptime percentage (0.0-100.0)")
    error_rate: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Error rate (0.0-1.0)")
    
    # ML Training Metrics (NEW for ML traceability - NO raw data)
    active_training_sessions: int = Field(default=0, description="Number of active ML training sessions")
    completed_sessions: int = Field(default=0, description="Number of completed training sessions")
    failed_sessions: int = Field(default=0, description="Number of failed training sessions")
    avg_model_accuracy: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Average model accuracy (0.0-1.0)")
    training_success_rate: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Training success rate (0.0-1.0)")
    model_deployment_rate: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Model deployment rate (0.0-1.0)")
    
    # Schema Quality Metrics (NEW for schema traceability - NO raw data)
    schema_validation_rate: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Schema validation rate (0.0-1.0)")
    ontology_consistency_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Ontology consistency score (0.0-1.0)")
    quality_rule_effectiveness: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Quality rule effectiveness (0.0-1.0)")
    validation_rule_count: int = Field(default=0, description="Number of active validation rules")
    
    # Neo4j Performance Metrics (ORIGINAL SCHEMA - Framework Performance)
    neo4j_connection_status: Optional[str] = Field(default=None, description="Neo4j connection status: connected, disconnected, error")
    neo4j_query_response_time_ms: Optional[float] = Field(default=None, description="Neo4j query response time in milliseconds")
    neo4j_import_speed_nodes_per_sec: Optional[float] = Field(default=None, description="Neo4j import speed (nodes per second)")
    neo4j_import_speed_rels_per_sec: Optional[float] = Field(default=None, description="Neo4j import speed (relationships per second)")
    neo4j_memory_usage_mb: Optional[float] = Field(default=None, description="Neo4j memory usage in MB")
    neo4j_disk_usage_mb: Optional[float] = Field(
        default=None, 
        description="Neo4j disk usage in MB"
    )
    
    # Graph Size Metrics (Framework Performance - Graph Scale)
    total_nodes: int = Field(
        default=0, 
        description="Total number of nodes in the graph"
    )
    total_relationships: int = Field(
        default=0, 
        description="Total number of relationships in the graph"
    )
    graph_complexity: str = Field(
        default="simple", 
        description="Graph complexity: simple, moderate, complex, very_complex"
    )
    
    # Graph Analytics Metrics (ORIGINAL SCHEMA - Framework Performance)
    graph_traversal_speed_ms: Optional[float] = Field(
        default=None, 
        description="Graph traversal speed in milliseconds"
    )
    graph_query_complexity_score: Optional[float] = Field(
        default=None, 
        ge=0.0, 
        le=1.0, 
        description="Graph query complexity score (0.0-1.0)"
    )
    graph_visualization_performance: Optional[float] = Field(
        default=None, 
        ge=0.0, 
        le=1.0, 
        description="Graph visualization performance (0.0-1.0)"
    )
    graph_analysis_accuracy: Optional[float] = Field(
        default=None, 
        ge=0.0, 
        le=1.0, 
        description="Graph analysis accuracy (0.0-1.0)"
    )
    
    # Knowledge Graph Performance Metrics (Framework Performance - NOT Data)
    graph_query_speed_sec: Optional[float] = Field(
        default=None, 
        description="Time to execute graph queries in seconds"
    )
    relationship_traversal_speed_sec: Optional[float] = Field(
        default=None, 
        description="Time to traverse relationships in seconds"
    )
    node_creation_speed_sec: Optional[float] = Field(
        default=None, 
        description="Time to create new nodes in seconds"
    )
    graph_analysis_efficiency: Optional[float] = Field(
        default=None, 
        ge=0.0, 
        le=1.0, 
        description="Graph analysis efficiency (0.0-1.0)"
    )
    
    # Neo4j Performance Metrics (JSON for better framework analysis)
    neo4j_performance: Dict[str, Any] = Field(
        default={}, 
        description="JSON: Neo4j performance metrics including import, export, sync, query, and analysis operations"
    )
    
    # Graph Category Performance Metrics (JSON for better framework analysis)
    graph_category_performance_stats: Dict[str, Any] = Field(
        default={}, 
        description="JSON: Performance statistics by graph category (aasx, structured_data, hybrid, custom)"
    )
    
    # User Interaction Metrics (ORIGINAL SCHEMA - Framework Usage)
    user_interaction_count: int = Field(default=0, description="Number of user interactions")
    query_execution_count: int = Field(default=0, description="Number of queries executed")
    visualization_view_count: int = Field(default=0, description="Number of visualization views")
    export_operation_count: int = Field(default=0, description="Number of export operations")
    graph_access_count: int = Field(default=0, description="Number of graph accesses")
    successful_graph_operations: int = Field(default=0, description="Successful operations")
    failed_graph_operations: int = Field(default=0, description="Failed operations")
    
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
    
    # Performance Trends (ORIGINAL SCHEMA - JSON fields)
    performance_trends: Dict[str, Any] = Field(default={}, description="JSON: Performance trends over time")
    resource_utilization_trends: Dict[str, Any] = Field(default={}, description="JSON: Resource utilization trends over time")
    user_activity: Dict[str, Any] = Field(default={}, description="JSON: User activity patterns")
    query_patterns: Dict[str, Any] = Field(
        default={}, 
        description="JSON: Query execution patterns"
    )
    relationship_patterns: Dict[str, Any] = Field(
        default={}, 
        description="JSON: Relationship traversal patterns"
    )
    
    # Knowledge Graph Patterns & Analytics (Framework Trends - JSON)
    knowledge_graph_patterns: Dict[str, Any] = Field(
        default={}, 
        description="JSON: Knowledge graph patterns and analytics over time"
    )
    graph_operation_patterns: Dict[str, Any] = Field(
        default={}, 
        description="JSON: Graph operation patterns and complexity distribution"
    )
    compliance_status: Dict[str, Any] = Field(
        default={}, 
        description="JSON: Compliance status and audit information"
    )
    security_events: Dict[str, Any] = Field(
        default={}, 
        description="JSON: Security events and threat assessment"
    )
    
    # Knowledge Graph-Specific Metrics (Framework Capabilities - JSON)
    knowledge_graph_analytics: Dict[str, Any] = Field(
        default={}, 
        description="JSON: Knowledge graph analytics including query quality, traversal quality, and analysis quality"
    )
    category_effectiveness: Dict[str, Any] = Field(
        default={}, 
        description="JSON: Category effectiveness analysis and optimization suggestions"
    )
    workflow_performance: Dict[str, Any] = Field(
        default={}, 
        description="JSON: Workflow performance analysis by type"
    )
    graph_size_performance_efficiency: Dict[str, Any] = Field(
        default={}, 
        description="JSON: Performance efficiency analysis by graph size"
    )
    
    # Enterprise Metrics (Merged from enterprise tables)
    enterprise_metrics: Dict[str, Any] = Field(
        default={}, 
        description="JSON: Comprehensive enterprise metrics and monitoring data"
    )
    enterprise_compliance_metrics: Dict[str, Any] = Field(
        default={}, 
        description="JSON: Compliance tracking and auditing metrics"
    )
    enterprise_security_metrics: Dict[str, Any] = Field(
        default={}, 
        description="JSON: Security metrics and threat assessment data"
    )
    enterprise_performance_analytics: Dict[str, Any] = Field(
        default={}, 
        description="JSON: Performance analytics and optimization data"
    )
    
    # Additional Enterprise Fields (Complete coverage)
    metric_type: str = Field(default="standard", description="Type of metric being tracked")
    metric_timestamp: Optional[datetime] = Field(default=None, description="Specific timestamp for the metric")
    compliance_type: str = Field(default="standard", description="Type of compliance being tracked")
    security_event_type: str = Field(default="none", description="Type of security event")
    performance_metric: str = Field(default="standard", description="Specific performance metric identifier")
    performance_value: Optional[float] = Field(default=None, description="Actual performance value")
    
    # Time-based Analytics (Framework Time Analysis)
    hour_of_day: Optional[int] = Field(default=None, ge=0, le=23, description="Hour of day (0-23)")
    day_of_week: Optional[int] = Field(default=None, ge=1, le=7, description="Day of week (1-7)")
    month: Optional[int] = Field(default=None, ge=1, le=12, description="Month (1-12)")
    
    # Performance Trends (Framework Performance Analysis)
    graph_management_trend: Optional[float] = Field(default=None, description="Compared to historical average")
    resource_efficiency_trend: Optional[float] = Field(default=None, description="Performance over time")
    quality_trend: Optional[float] = Field(default=None, description="Quality metrics over time")
    
    # Foreign Key Constraints

    # Computed Fields for Business Intelligence
    @computed_field
    def overall_performance_score(self) -> float:
        """Calculate overall performance score from all metrics"""
        scores = []
        
        if self.health_score is not None:
            scores.append(self.health_score / 100.0)
        if self.uptime_percentage is not None:
            scores.append(self.uptime_percentage / 100.0)
        if self.error_rate is not None:
            scores.append(1.0 - self.error_rate)
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
    def neo4j_health_status(self) -> str:
        """Determine Neo4j health status based on multiple factors"""
        if self.neo4j_connection_status == "error":
            return "critical"
        elif self.neo4j_connection_status == "disconnected":
            return "offline"
        elif self.neo4j_connection_status == "connected":
            if self.neo4j_query_response_time_ms and self.neo4j_query_response_time_ms > 1000:
                return "warning"
            elif self.neo4j_memory_usage_mb and self.neo4j_memory_usage_mb > 8000:
                return "warning"
            else:
                return "healthy"
        else:
            return "unknown"

    @computed_field
    def graph_performance_rating(self) -> str:
        """Rate graph performance based on multiple factors"""
        if self.overall_performance_score >= 0.9:
            return "excellent"
        elif self.overall_performance_score >= 0.7:
            return "good"
        elif self.overall_performance_score >= 0.5:
            return "fair"
        else:
            return "poor"

    @computed_field
    def ml_training_health(self) -> str:
        """Assess ML training health based on training metrics"""
        if self.active_training_sessions == 0 and self.completed_sessions == 0:
            return "no_activity"
        
        if self.failed_sessions > 0 and self.completed_sessions == 0:
            return "critical"
        elif self.failed_sessions > self.completed_sessions * 0.3:
            return "warning"
        elif self.training_success_rate and self.training_success_rate < 0.7:
            return "warning"
        else:
            return "healthy"

    @computed_field
    def resource_health_status(self) -> str:
        """Assess resource health based on system metrics"""
        resource_scores = []
        
        if self.cpu_usage_percent is not None:
            if self.cpu_usage_percent > 90:
                resource_scores.append(0.0)
            elif self.cpu_usage_percent > 80:
                resource_scores.append(0.3)
            elif self.cpu_usage_percent > 60:
                resource_scores.append(0.7)
            else:
                resource_scores.append(1.0)
        
        if self.memory_usage_percent is not None:
            if self.memory_usage_percent > 90:
                resource_scores.append(0.0)
            elif self.memory_usage_percent > 80:
                resource_scores.append(0.3)
            elif self.memory_usage_percent > 60:
                resource_scores.append(0.7)
            else:
                resource_scores.append(1.0)
        
        if self.storage_usage_percent is not None:
            if self.storage_usage_percent > 90:
                resource_scores.append(0.0)
            elif self.storage_usage_percent > 80:
                resource_scores.append(0.3)
            elif self.storage_usage_percent > 60:
                resource_scores.append(0.7)
            else:
                resource_scores.append(1.0)
        
        if not resource_scores:
            return "unknown"
        
        avg_score = sum(resource_scores) / len(resource_scores)
        if avg_score >= 0.8:
            return "healthy"
        elif avg_score >= 0.6:
            return "warning"
        else:
            return "critical"

    @computed_field
    def data_quality_health(self) -> str:
        """Assess data quality health based on quality metrics"""
        quality_scores = []
        
        if self.data_freshness_score is not None:
            quality_scores.append(self.data_freshness_score)
        if self.data_completeness_score is not None:
            quality_scores.append(self.data_completeness_score)
        if self.data_consistency_score is not None:
            quality_scores.append(self.data_consistency_score)
        if self.data_accuracy_score is not None:
            quality_scores.append(self.data_accuracy_score)
        
        if not quality_scores:
            return "unknown"
        
        avg_quality = sum(quality_scores) / len(quality_scores)
        if avg_quality >= 0.9:
            return "excellent"
        elif avg_quality >= 0.7:
            return "good"
        elif avg_quality >= 0.5:
            return "fair"
        else:
            return "poor"

    @computed_field
    def operational_efficiency_score(self) -> float:
        """Calculate operational efficiency score"""
        efficiency_factors = []
        
        # Query efficiency
        if self.query_execution_count > 0:
            success_rate = self.successful_graph_operations / self.query_execution_count
            efficiency_factors.append(success_rate)
        
        # Response time efficiency
        if self.response_time_ms is not None:
            if self.response_time_ms < 100:
                efficiency_factors.append(1.0)
            elif self.response_time_ms < 500:
                efficiency_factors.append(0.8)
            elif self.response_time_ms < 1000:
                efficiency_factors.append(0.6)
            else:
                efficiency_factors.append(0.4)
        
        # Resource efficiency
        if self.cpu_usage_percent is not None and self.memory_usage_percent is not None:
            cpu_efficiency = max(0, 1.0 - (self.cpu_usage_percent / 100))
            memory_efficiency = max(0, 1.0 - (self.memory_usage_percent / 100))
            resource_efficiency = (cpu_efficiency + memory_efficiency) / 2
            efficiency_factors.append(resource_efficiency)
        
        return sum(efficiency_factors) / len(efficiency_factors) if efficiency_factors else 0.0

    @computed_field
    def scalability_assessment(self) -> str:
        """Assess system scalability based on performance under load"""
        if self.total_nodes > 100000 or self.total_relationships > 500000:
            if self.response_time_ms and self.response_time_ms < 2000:
                return "excellent"
            elif self.response_time_ms and self.response_time_ms < 5000:
                return "good"
            else:
                return "needs_optimization"
        elif self.total_nodes > 10000 or self.total_relationships > 50000:
            if self.response_time_ms and self.response_time_ms < 1000:
                return "excellent"
            elif self.response_time_ms and self.response_time_ms < 2000:
                return "good"
            else:
                return "needs_optimization"
        else:
            return "adequate"

    @computed_field
    def maintenance_priority(self) -> str:
        """Determine maintenance priority based on health indicators"""
        critical_issues = 0
        warning_issues = 0
        
        if self.neo4j_health_status == "critical":
            critical_issues += 1
        elif self.neo4j_health_status == "warning":
            warning_issues += 1
        
        if self.resource_health_status == "critical":
            critical_issues += 1
        elif self.resource_health_status == "warning":
            warning_issues += 1
        
        if self.data_quality_health == "poor":
            critical_issues += 1
        elif self.data_quality_health == "fair":
            warning_issues += 1
        
        if self.ml_training_health == "critical":
            critical_issues += 1
        elif self.ml_training_health == "warning":
            warning_issues += 1
        
        if critical_issues > 0:
            return "immediate"
        elif warning_issues > 2:
            return "high"
        elif warning_issues > 0:
            return "medium"
        else:
            return "low"

    @computed_field
    def enterprise_health_score(self) -> float:
        """Calculate enterprise health score for business intelligence"""
        health_factors = []
        
        # Performance health
        if self.overall_performance_score is not None:
            health_factors.append(self.overall_performance_score * 0.3)
        
        # Operational efficiency
        if self.operational_efficiency_score is not None:
            health_factors.append(self.operational_efficiency_score * 0.25)
        
        # Data quality
        if self.data_quality_health != "unknown":
            quality_scores = {"excellent": 1.0, "good": 0.8, "fair": 0.6, "poor": 0.3}
            health_factors.append(quality_scores.get(self.data_quality_health, 0.0) * 0.25)
        
        # Resource health
        if self.resource_health_status != "unknown":
            resource_scores = {"healthy": 1.0, "warning": 0.6, "critical": 0.2}
            health_factors.append(resource_scores.get(self.resource_health_status, 0.0) * 0.2)
        
        return sum(health_factors) if health_factors else 0.0

    def __init__(self, **data):
        # Generate metric_id if not provided
        if 'metric_id' not in data:
            data['metric_id'] = int(uuid.uuid4().hex[:8], 16)
        
        # Set timestamp if not provided
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now(timezone.utc)
        
        super().__init__(**data)
    
    # Asynchronous Enterprise Methods for Business Intelligence
    async def update_health_metrics(self) -> None:
        """Update health metrics asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        
        # Update health score based on current metrics
        if self.health_score is None:
            self.health_score = int(self.enterprise_health_score * 100)
        
        # Update timestamp
        self.timestamp = datetime.now(timezone.utc)

    async def update_performance_metrics(self, response_time: float, cpu_usage: float, memory_usage: float) -> None:
        """Update performance metrics asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        
        self.response_time_ms = response_time
        self.cpu_usage_percent = cpu_usage
        self.memory_usage_percent = memory_usage
        self.timestamp = datetime.now(timezone.utc)

    async def update_neo4j_metrics(self, connection_status: str, query_time: float, memory_usage: float) -> None:
        """Update Neo4j-specific metrics asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        
        self.neo4j_connection_status = connection_status
        self.neo4j_query_response_time_ms = query_time
        self.neo4j_memory_usage_mb = memory_usage
        self.timestamp = datetime.now(timezone.utc)

    async def update_graph_metrics(self, nodes: int, relationships: int, complexity: str) -> None:
        """Update graph size and complexity metrics asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        
        self.total_nodes = nodes
        self.total_relationships = relationships
        self.graph_complexity = complexity
        self.timestamp = datetime.now(timezone.utc)

    async def update_ml_training_metrics(self, active_sessions: int, completed: int, failed: int) -> None:
        """Update ML training metrics asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        
        self.active_training_sessions = active_sessions
        self.completed_sessions = completed
        self.failed_sessions = failed
        
        # Calculate success rate
        total_sessions = completed + failed
        if total_sessions > 0:
            self.training_success_rate = completed / total_sessions
        
        self.timestamp = datetime.now(timezone.utc)

    async def update_data_quality_metrics(self, freshness: float, completeness: float, consistency: float, accuracy: float) -> None:
        """Update data quality metrics asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        
        self.data_freshness_score = freshness
        self.data_completeness_score = completeness
        self.data_consistency_score = consistency
        self.data_accuracy_score = accuracy
        self.timestamp = datetime.now(timezone.utc)

    async def calculate_performance_trends(self) -> Dict[str, Any]:
        """Calculate performance trends asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        
        trends = {
            "performance_trend": "stable",
            "health_trend": "stable",
            "resource_trend": "stable",
            "quality_trend": "stable"
        }
        
        # Analyze performance trends based on current metrics
        if self.overall_performance_score and self.overall_performance_score > 0.8:
            trends["performance_trend"] = "improving"
        elif self.overall_performance_score and self.overall_performance_score < 0.5:
            trends["performance_trend"] = "declining"
        
        if self.enterprise_health_score and self.enterprise_health_score > 0.8:
            trends["health_trend"] = "improving"
        elif self.enterprise_health_score and self.enterprise_health_score < 0.5:
            trends["health_trend"] = "declining"
        
        return trends

    async def generate_optimization_suggestions(self) -> List[str]:
        """Generate optimization suggestions asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        suggestions = []
        
        if self.overall_performance_score and self.overall_performance_score < 0.7:
            suggestions.append("Review and optimize graph structure and query patterns")
        
        if self.resource_health_status == "critical":
            suggestions.append("Immediate resource optimization required - consider scaling or optimization")
        
        if self.neo4j_health_status == "warning":
            suggestions.append("Neo4j performance optimization recommended")
        
        if self.data_quality_health == "poor":
            suggestions.append("Data quality improvement required - review data sources and validation")
        
        if self.ml_training_health == "warning":
            suggestions.append("ML training process optimization recommended")
        
        return suggestions

    async def get_comprehensive_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        
        return {
            "metric_id": self.metric_id,
            "graph_id": self.graph_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "overall_performance_score": self.overall_performance_score,
            "enterprise_health_score": self.enterprise_health_score,
            "graph_performance_rating": self.graph_performance_rating,
            "neo4j_health_status": self.neo4j_health_status,
            "ml_training_health": self.ml_training_health,
            "resource_health_status": self.resource_health_status,
            "data_quality_health": self.data_quality_health,
            "operational_efficiency_score": self.operational_efficiency_score,
            "scalability_assessment": self.scalability_assessment,
            "maintenance_priority": self.maintenance_priority,
            "performance_metrics": {
                "health_score": self.health_score,
                "response_time_ms": self.response_time_ms,
                "uptime_percentage": self.uptime_percentage,
                "error_rate": self.error_rate
            },
            "graph_metrics": {
                "total_nodes": self.total_nodes,
                "total_relationships": self.total_relationships,
                "graph_complexity": self.graph_complexity
            },
            "ml_metrics": {
                "active_training_sessions": self.active_training_sessions,
                "completed_sessions": self.completed_sessions,
                "failed_sessions": self.failed_sessions,
                "training_success_rate": self.training_success_rate
            },
            "neo4j_metrics": {
                "connection_status": self.neo4j_connection_status,
                "query_response_time": self.neo4j_query_response_time_ms,
                "memory_usage": self.neo4j_memory_usage_mb,
                "disk_usage": self.neo4j_disk_usage_mb
            },
            "resource_metrics": {
                "cpu_usage": self.cpu_usage_percent,
                "memory_usage": self.memory_usage_percent,
                "storage_usage": self.storage_usage_percent
            },
            "quality_metrics": {
                "data_freshness": self.data_freshness_score,
                "data_completeness": self.data_completeness_score,
                "data_consistency": self.data_consistency_score,
                "data_accuracy": self.data_accuracy_score
            }
        }

    # ========================================================================
    # ADDITIONAL ASYNC METHODS (Matching Certificate Manager)
    # ========================================================================
    
    async def validate_integrity(self) -> bool:
        """Validate metrics data integrity"""
        try:
            # Validate required fields
            if not all([self.metric_id, self.graph_id, self.timestamp]):
                return False
            
            # Validate business rules
            if self.health_score is not None and (self.health_score < 0 or self.health_score > 100):
                return False
            
            if self.uptime_percentage is not None and (self.uptime_percentage < 0.0 or self.uptime_percentage > 100.0):
                return False
            
            if self.error_rate is not None and (self.error_rate < 0.0 or self.error_rate > 1.0):
                return False
            
            if self.cpu_usage_percent is not None and (self.cpu_usage_percent < 0.0 or self.cpu_usage_percent > 100.0):
                return False
            
            if self.memory_usage_percent is not None and (self.memory_usage_percent < 0.0 or self.memory_usage_percent > 100.0):
                return False
            
            return True
            
        except Exception as e:
            return False
    
    async def update_health_metrics(self) -> None:
        """Update health metrics based on current state"""
        try:
            # Update enterprise health score
            if self.enterprise_health_score is not None:
                self.health_score = int(self.enterprise_health_score * 100)
            
            # Update timestamp
            self.timestamp = datetime.now(timezone.utc)
            
        except Exception as e:
            pass
    
    async def generate_summary(self) -> Dict[str, Any]:
        """Generate comprehensive metrics summary"""
        try:
            await self.update_health_metrics()
            
            summary = {
                "metric_id": self.metric_id,
                "graph_id": self.graph_id,
                "timestamp": self.timestamp.isoformat() if self.timestamp else None,
                "overall_performance_score": self.overall_performance_score,
                "enterprise_health_score": self.enterprise_health_score,
                "graph_performance_rating": self.graph_performance_rating,
                "neo4j_health_status": self.neo4j_health_status,
                "ml_training_health": self.ml_training_health,
                "resource_health_status": self.resource_health_status,
                "data_quality_health": self.data_quality_health,
                "operational_efficiency_score": self.operational_efficiency_score,
                "scalability_assessment": self.scalability_assessment,
                "maintenance_priority": self.maintenance_priority,
                "performance_metrics": {
                    "health_score": self.health_score,
                    "response_time_ms": self.response_time_ms,
                    "uptime_percentage": self.uptime_percentage,
                    "error_rate": self.error_rate
                },
                "graph_metrics": {
                    "total_nodes": self.total_nodes,
                    "total_relationships": self.total_relationships,
                    "graph_complexity": self.graph_complexity
                },
                "ml_metrics": {
                    "active_training_sessions": self.active_training_sessions,
                    "completed_sessions": self.completed_sessions,
                    "failed_sessions": self.failed_sessions,
                    "training_success_rate": self.training_success_rate
                },
                "neo4j_metrics": {
                    "connection_status": self.neo4j_connection_status,
                    "query_response_time": self.neo4j_query_response_time_ms,
                    "memory_usage": self.neo4j_memory_usage_mb
                },
                "resource_metrics": {
                    "cpu_usage": self.cpu_usage_percent,
                    "memory_usage": self.memory_usage_percent,
                    "storage_usage": self.storage_usage_percent
                },
                "quality_metrics": {
                    "data_freshness": self.data_freshness_score,
                    "data_completeness": self.data_completeness_score,
                    "data_consistency": self.data_consistency_score,
                    "data_accuracy": self.data_accuracy_score
                }
            }
            
            return summary
            
        except Exception as e:
            return {"error": f"Failed to generate summary: {str(e)}"}
    
    async def export_data(self, format: str = "json") -> Dict[str, Any]:
        """Export metrics data in specified format"""
        try:
            if format.lower() == "json":
                return {
                    "metric_id": self.metric_id,
                    "graph_id": self.graph_id,
                    "timestamp": self.timestamp.isoformat() if self.timestamp else None,
                    "metric_type": self.metric_type,
                    "overall_performance_score": self.overall_performance_score,
                    "enterprise_health_score": self.enterprise_health_score,
                    "health_score": self.health_score,
                    "response_time_ms": self.response_time_ms,
                    "uptime_percentage": self.uptime_percentage,
                    "error_rate": self.error_rate,
                    "graph_metrics": {
                        "total_nodes": self.total_nodes,
                        "total_relationships": self.total_relationships,
                        "graph_complexity": self.graph_complexity
                    },
                    "ml_training_metrics": {
                        "active_sessions": self.active_training_sessions,
                        "completed_sessions": self.completed_sessions,
                        "failed_sessions": self.failed_sessions,
                        "avg_model_accuracy": self.avg_model_accuracy,
                        "training_success_rate": self.training_success_rate
                    },
                    "neo4j_metrics": {
                        "connection_status": self.neo4j_connection_status,
                        "query_response_time": self.neo4j_query_response_time_ms,
                        "import_speed_nodes": self.neo4j_import_speed_nodes_per_sec,
                        "import_speed_rels": self.neo4j_import_speed_rels_per_sec,
                        "memory_usage": self.neo4j_memory_usage_mb,
                        "disk_usage": self.neo4j_disk_usage_mb
                    },
                    "system_metrics": {
                        "cpu_usage": self.cpu_usage_percent,
                        "memory_usage": self.memory_usage_percent,
                        "storage_usage": self.storage_usage_percent,
                        "network_throughput": self.network_throughput_mbps
                    },
                    "data_quality_metrics": {
                        "freshness_score": self.data_freshness_score,
                        "completeness_score": self.data_completeness_score,
                        "consistency_score": self.data_consistency_score,
                        "accuracy_score": self.data_accuracy_score
                    },
                    "computed_fields": {
                        "graph_performance_rating": self.graph_performance_rating,
                        "neo4j_health_status": self.neo4j_health_status,
                        "ml_training_health": self.ml_training_health,
                        "resource_health_status": self.resource_health_status,
                        "data_quality_health": self.data_quality_health,
                        "operational_efficiency_score": self.operational_efficiency_score,
                        "scalability_assessment": self.scalability_assessment,
                        "maintenance_priority": self.maintenance_priority
                    },
                    "user_interaction_metrics": {
                        "interaction_count": self.user_interaction_count,
                        "query_count": self.query_execution_count,
                        "visualization_count": self.visualization_view_count,
                        "export_count": self.export_operation_count,
                        "successful_operations": self.successful_graph_operations,
                        "failed_operations": self.failed_graph_operations
                    }
                }
            else:
                return {"error": f"Unsupported format: {format}"}
                
        except Exception as e:
            return {"error": f"Failed to export data: {str(e)}"}


# Query Models for API Operations
class KGGraphMetricsQuery(BaseModel):
    """Query model for filtering KG graph metrics"""
    
    # Basic filters
    graph_id: Optional[str] = None
    metric_type: Optional[str] = None
    
    # Performance filters
    min_health_score: Optional[int] = None
    max_health_score: Optional[int] = None
    min_performance_score: Optional[float] = None
    max_performance_score: Optional[float] = None
    
    # Health status filters
    neo4j_health_status: Optional[str] = None
    ml_training_health: Optional[str] = None
    resource_health_status: Optional[str] = None
    data_quality_health: Optional[str] = None
    
    # Graph metrics filters
    min_nodes: Optional[int] = None
    max_nodes: Optional[int] = None
    min_relationships: Optional[int] = None
    max_relationships: Optional[int] = None
    graph_complexity: Optional[str] = None
    
    # Resource filters
    min_cpu_usage: Optional[float] = None
    max_cpu_usage: Optional[float] = None
    min_memory_usage: Optional[float] = None
    max_memory_usage: Optional[float] = None
    
    # Date filters
    timestamp_after: Optional[datetime] = None
    timestamp_before: Optional[datetime] = None
    
    # Pagination
    limit: Optional[int] = 100
    offset: Optional[int] = 0
    sort_by: Optional[str] = "timestamp"
    sort_order: Optional[str] = "desc"


# Summary Models for Analytics
class KGGraphMetricsSummary(BaseModel):
    """Summary model for KG graph metrics analytics"""
    
    # Counts
    total_metrics: int
    healthy_metrics: int
    warning_metrics: int
    critical_metrics: int
    
    # Performance averages
    avg_health_score: float
    avg_performance_score: float
    avg_response_time: float
    avg_uptime_percentage: float
    
    # Health distribution
    neo4j_health_distribution: Dict[str, int]
    ml_training_health_distribution: Dict[str, int]
    resource_health_distribution: Dict[str, int]
    data_quality_health_distribution: Dict[str, int]
    
    # Graph metrics
    total_nodes: int
    total_relationships: int
    graph_complexity_distribution: Dict[str, int]
    
    # ML metrics
    avg_training_success_rate: float
    total_training_sessions: int
    failed_training_sessions: int
    
    # Resource metrics
    avg_cpu_usage: float
    avg_memory_usage: float
    avg_storage_usage: float
    
    # Quality metrics
    avg_data_freshness: float
    avg_data_completeness: float
    avg_data_consistency: float
    avg_data_accuracy: float
    
    # Performance trends
    performance_trend: str
    health_trend: str
    resource_trend: str
    
    # Timestamps
    summary_generated_at: datetime
    data_from_date: Optional[datetime] = None
    data_to_date: Optional[datetime] = None
