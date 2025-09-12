"""
Knowledge Graph (KG) Neo4j Module

A comprehensive Knowledge Graph module with Neo4j integration for AASX data modeling.
Provides world-class graph operations, analytics, and visualization capabilities.

Architecture:
- Core Services: Heavy lifting business logic
- Operational Services: Workflow management
- Neo4j Operations: Direct Neo4j database operations
- Data Models: Pydantic models for data validation
- Repositories: Data access layer with async support
- Utilities: Helper functions and Docker management
"""

# Core Services (Heavy Lifting Business Logic)
from .core.kg_graph import KGGraphService
from .core.kg_metrics import KGMetricsService
from .core.kg_neo4j_integration import KGNeo4jIntegrationService

# Operational Services (Workflow Management)
from .core.kg_graph_operations import KGGraphOperationsService
from .core.kg_analytics import KGAnalyticsService

# Data Models
from .models.kg_graph_registry import KGGraphRegistry, KGGraphRegistryQuery
from .models.kg_graph_metrics import KGGraphMetrics, KGGraphMetricsQuery

# Data Access Layer
from .repositories.kg_graph_registry_repository import KGGraphRegistryRepository
from .repositories.kg_graph_metrics_repository import KGGraphMetricsRepository

# Neo4j Operations (Direct Access)
from .neo4j import Neo4jManager, AASXGraphAnalyzer, CypherQueries

# Utility Functions
from .utils import (
    # Helper Functions
    generate_graph_id,
    validate_graph_config,
    sanitize_graph_name,
    format_timestamp,
    calculate_health_score,
    parse_graph_query,
    validate_neo4j_connection_config,
    calculate_performance_metrics,
    generate_export_filename,
    
    # Docker Management
    check_docker_status,
    start_neo4j,
    stop_neo4j,
    restart_neo4j,
    remove_neo4j,
    show_logs,
    check_browser,
    run_command
)

__all__ = [
    # Core Services
    'KGGraphService',
    'KGMetricsService', 
    'KGNeo4jIntegrationService',
    
    # Operational Services
    'KGGraphOperationsService',
    'KGAnalyticsService',
    
    # Data Models
    'KGGraphRegistry',
    'KGGraphRegistryQuery',
    'KGGraphMetrics',
    'KGGraphMetricsQuery',
    
    # Data Access Layer
    'KGGraphRegistryRepository',
    'KGGraphMetricsRepository',
    
    # Neo4j Operations
    'Neo4jManager',
    'AASXGraphAnalyzer',
    'CypherQueries',
    
    # Utility Functions
    'generate_graph_id',
    'validate_graph_config',
    'sanitize_graph_name',
    'format_timestamp',
    'calculate_health_score',
    'parse_graph_query',
    'validate_neo4j_connection_config',
    'calculate_performance_metrics',
    'generate_export_filename',
    
    # Docker Management
    'check_docker_status',
    'start_neo4j',
    'stop_neo4j',
    'restart_neo4j',
    'remove_neo4j',
    'show_logs',
    'check_browser',
    'run_command'
] 