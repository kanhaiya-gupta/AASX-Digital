"""
Knowledge Graph Metrics Model

Updated to match our comprehensive database schema with all fields.
Supports real-time performance monitoring and analytics for knowledge graphs.
"""

from src.shared.models.base_model import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone


class KGGraphMetrics(BaseModel):
    """Knowledge Graph metrics model for real-time monitoring & analytics"""
    
    # Primary Identification
    metric_id: Optional[int] = None
    graph_id: str
    timestamp: datetime
    
    # Real-time Health Metrics (Same pattern as twin_registry_metrics)
    health_score: Optional[int] = None                           # Current health score (0-100)
    response_time_ms: Optional[float] = None                     # Response time in milliseconds
    uptime_percentage: Optional[float] = None                    # Uptime percentage
    error_rate: Optional[float] = None                           # Error rate (0.0-1.0)
    
    # Neo4j Performance Metrics (NEW for Knowledge Graph)
    neo4j_connection_status: Optional[str] = None               # connected, disconnected, error
    neo4j_query_response_time_ms: Optional[float] = None        # Query response time
    neo4j_import_speed_nodes_per_sec: Optional[float] = None    # Import performance
    neo4j_import_speed_rels_per_sec: Optional[float] = None     # Import performance
    neo4j_memory_usage_mb: Optional[float] = None               # Memory usage
    neo4j_disk_usage_mb: Optional[float] = None                 # Disk usage
    
    # Graph Analytics Metrics (NEW for Knowledge Graph)
    graph_traversal_speed_ms: Optional[float] = None            # Traversal performance
    graph_query_complexity_score: Optional[float] = None         # Query complexity
    graph_visualization_performance: Optional[float] = None      # Visualization performance
    graph_analysis_accuracy: Optional[float] = None              # Analysis accuracy
    
    # User Interaction Metrics (NEW for Knowledge Graph)
    user_interaction_count: Optional[int] = None                 # User interactions
    query_execution_count: Optional[int] = None                  # Queries executed
    visualization_view_count: Optional[int] = None               # Visualization views
    export_operation_count: Optional[int] = None                 # Export operations
    
    # Data Quality Metrics (NEW for Knowledge Graph)
    data_freshness_score: Optional[float] = None                 # Data freshness
    data_completeness_score: Optional[float] = None              # Data completeness
    data_consistency_score: Optional[float] = None               # Data consistency
    data_accuracy_score: Optional[float] = None                  # Data accuracy
    
    # System Resource Metrics (Same pattern as twin_registry_metrics)
    cpu_usage_percent: Optional[float] = None                    # CPU usage
    memory_usage_percent: Optional[float] = None                 # Memory usage
    network_throughput_mbps: Optional[float] = None              # Network performance
    storage_usage_percent: Optional[float] = None                # Storage usage
    
    # Performance Trends (Same pattern as twin_registry_metrics)
    performance_trends: Dict[str, Any] = {}                      # Performance trends
    resource_utilization_trends: Dict[str, Any] = {}             # Resource trends
    
    # User Activity (Same pattern as twin_registry_metrics)
    user_activity: Dict[str, Any] = {}                           # User activity
    query_patterns: Dict[str, Any] = {}                          # Query patterns
    
    # Compliance & Security (Same pattern as twin_registry_metrics)
    compliance_status: Dict[str, Any] = {}                       # Compliance data
    security_events: List[Dict[str, Any]] = []                   # Security events
    
    # Graph-Specific Metrics (NEW for Knowledge Graph)
    graph_analytics: Dict[str, Any] = {}                         # Graph analytics
    relationship_patterns: Dict[str, Any] = {}                   # Relationship patterns
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def __init__(self, **data):
        # Set timestamp if not provided
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now(timezone.utc)
        
        super().__init__(**data)
    
    def update_neo4j_metrics(self, connection_status: str, query_time: float, memory: float, disk: float):
        """Update Neo4j-specific performance metrics"""
        self.neo4j_connection_status = connection_status
        self.neo4j_query_response_time_ms = query_time
        self.neo4j_memory_usage_mb = memory
        self.neo4j_disk_usage_mb = disk
        self.timestamp = datetime.now(timezone.utc)
    
    def update_graph_performance(self, traversal_speed: float, query_complexity: float, 
                                visualization_perf: float, analysis_accuracy: float):
        """Update graph-specific performance metrics"""
        self.graph_traversal_speed_ms = traversal_speed
        self.graph_query_complexity_score = query_complexity
        self.graph_visualization_performance = visualization_perf
        self.graph_analysis_accuracy = analysis_accuracy
        self.timestamp = datetime.now(timezone.utc)
    
    def update_user_activity(self, interactions: int, queries: int, views: int, exports: int):
        """Update user interaction metrics"""
        self.user_interaction_count = interactions
        self.query_execution_count = queries
        self.visualization_view_count = views
        self.export_operation_count = exports
        self.timestamp = datetime.now(timezone.utc)
    
    def update_data_quality(self, freshness: float, completeness: float, consistency: float, accuracy: float):
        """Update data quality metrics"""
        self.data_freshness_score = max(0.0, min(1.0, freshness))
        self.data_completeness_score = max(0.0, min(1.0, completeness))
        self.data_consistency_score = max(0.0, min(1.0, consistency))
        self.data_accuracy_score = max(0.0, min(1.0, accuracy))
        self.timestamp = datetime.now(timezone.utc)
    
    def update_system_resources(self, cpu: float, memory: float, network: float, storage: float):
        """Update system resource metrics"""
        self.cpu_usage_percent = max(0.0, min(100.0, cpu))
        self.memory_usage_percent = max(0.0, min(100.0, memory))
        self.network_throughput_mbps = max(0.0, network)
        self.storage_usage_percent = max(0.0, min(100.0, storage))
        self.timestamp = datetime.now(timezone.utc)
    
    def add_performance_trend(self, trend_name: str, trend_data: Dict[str, Any]):
        """Add performance trend data"""
        self.performance_trends[trend_name] = trend_data
        self.timestamp = datetime.now(timezone.utc)
    
    def add_resource_trend(self, resource_name: str, trend_data: Dict[str, Any]):
        """Add resource utilization trend data"""
        self.resource_utilization_trends[resource_name] = trend_data
        self.timestamp = datetime.now(timezone.utc)
    
    def add_user_activity(self, activity_type: str, activity_data: Dict[str, Any]):
        """Add user activity data"""
        self.user_activity[activity_type] = activity_data
        self.timestamp = datetime.now(timezone.utc)
    
    def add_query_pattern(self, pattern_name: str, pattern_data: Dict[str, Any]):
        """Add query pattern analysis data"""
        self.query_patterns[pattern_name] = pattern_data
        self.timestamp = datetime.now(timezone.utc)
    
    def add_security_event(self, event_type: str, event_details: Dict[str, Any]):
        """Add security event data"""
        security_event = {
            "type": event_type,
            "details": event_details,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.security_events.append(security_event)
        self.timestamp = datetime.now(timezone.utc)
    
    def add_graph_analytics(self, analytics_name: str, analytics_data: Dict[str, Any]):
        """Add graph analytics data"""
        self.graph_analytics[analytics_name] = analytics_data
        self.timestamp = datetime.now(timezone.utc)
    
    def add_relationship_pattern(self, pattern_name: str, pattern_data: Dict[str, Any]):
        """Add relationship pattern analysis data"""
        self.relationship_patterns[pattern_name] = pattern_data
        self.timestamp = datetime.now(timezone.utc)
    
    def calculate_overall_health_score(self) -> int:
        """Calculate overall health score based on various metrics"""
        scores = []
        
        # Health score (if available)
        if self.health_score is not None:
            scores.append(self.health_score)
        
        # Performance scores (convert 0.0-1.0 to 0-100)
        if self.graph_visualization_performance is not None:
            scores.append(int(self.graph_visualization_performance * 100))
        if self.graph_analysis_accuracy is not None:
            scores.append(int(self.graph_analysis_accuracy * 100))
        
        # Data quality scores (convert 0.0-1.0 to 0-100)
        if self.data_quality_score is not None:
            scores.append(int(self.data_quality_score * 100))
        
        # Neo4j connection status
        if self.neo4j_connection_status == "connected":
            scores.append(100)
        elif self.neo4j_connection_status == "disconnected":
            scores.append(0)
        elif self.neo4j_connection_status == "error":
            scores.append(25)
        
        # Calculate average if we have scores
        if scores:
            return int(sum(scores) / len(scores))
        else:
            return 0


# Query and Summary models for API responses
class KGGraphMetricsQuery(BaseModel):
    """Query model for filtering graph metrics"""
    graph_id: Optional[str] = None
    start_timestamp: Optional[datetime] = None
    end_timestamp: Optional[datetime] = None
    metric_type: Optional[str] = None  # health, performance, user_activity, etc.
    limit: int = 100
    offset: int = 0


class KGGraphMetricsSummary(BaseModel):
    """Summary model for graph metrics overview"""
    total_metrics: int
    avg_health_score: float
    avg_response_time: float
    total_user_interactions: int
    total_queries_executed: int
    avg_data_quality: float
    performance_trend: str  # improving, stable, declining
