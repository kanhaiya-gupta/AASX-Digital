"""
Configuration for AI RAG Processor Integration Service.

This module provides configuration options for connecting existing AI RAG processors
to the new graph generation pipeline.
"""

from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class EntityExtractionConfig:
    """Configuration for entity extraction from processor outputs."""
    
    # Confidence thresholds
    min_confidence: float = 0.7
    max_confidence: float = 1.0
    
    # Entity limits
    max_entities: int = 100
    min_entities: int = 5
    
    # Entity types to extract
    entity_types: List[str] = field(default_factory=lambda: [
        "person", "organization", "location", "concept", 
        "technology", "product", "process", "system"
    ])
    
    # Content requirements
    min_content_length: int = 50
    max_content_length: int = 10000
    
    # Processing options
    enable_nlp_enhancement: bool = True
    enable_domain_knowledge: bool = True
    enable_entity_linking: bool = True


@dataclass
class RelationshipDiscoveryConfig:
    """Configuration for relationship discovery between entities."""
    
    # Confidence thresholds
    min_confidence: float = 0.6
    max_confidence: float = 1.0
    
    # Relationship limits
    max_relationships: int = 200
    min_relationships: int = 3
    
    # Relationship types to discover
    relationship_types: List[str] = field(default_factory=lambda: [
        "is_a", "part_of", "located_in", "uses", "creates",
        "depends_on", "interacts_with", "contains", "belongs_to"
    ])
    
    # Discovery algorithms
    enable_semantic_analysis: bool = True
    enable_pattern_matching: bool = True
    enable_context_analysis: bool = True
    
    # Processing options
    max_discovery_time: int = 30  # seconds
    enable_parallel_processing: bool = True


@dataclass
class GraphBuildingConfig:
    """Configuration for building graph structures."""
    
    # Graph size limits
    max_nodes: int = 1000
    max_edges: int = 2000
    min_nodes: int = 5
    min_edges: int = 3
    
    # Graph structure options
    enable_cycles: bool = True
    enable_loops: bool = False
    enable_directed_edges: bool = True
    enable_weighted_edges: bool = True
    
    # Node and edge properties
    max_node_properties: int = 20
    max_edge_properties: int = 10
    
    # Quality settings
    min_connectivity: float = 0.1
    max_isolated_nodes: int = 5
    
    # Processing options
    enable_optimization: bool = True
    enable_validation: bool = True


@dataclass
class GraphValidationConfig:
    """Configuration for graph validation."""
    
    # Quality thresholds
    min_quality_score: float = 0.5
    max_validation_time: int = 30  # seconds
    
    # Validation checks
    enable_schema_validation: bool = True
    enable_structure_validation: bool = True
    enable_property_validation: bool = True
    enable_connectivity_validation: bool = True
    
    # Quality metrics
    min_node_coverage: float = 0.8
    min_edge_coverage: float = 0.7
    max_duplicate_entities: int = 5
    
    # Error handling
    fail_on_critical_errors: bool = False
    max_validation_warnings: int = 10


@dataclass
class GraphExportConfig:
    """Configuration for graph export formats."""
    
    # Export formats
    formats: List[str] = field(default_factory=lambda: [
        "cypher", "graphml", "json_ld", "html"
    ])
    
    # Export options
    include_metadata: bool = True
    include_properties: bool = True
    include_statistics: bool = True
    enable_compression: bool = False
    
    # Output settings
    output_directory: str = "output/graphs/ai_rag/"
    filename_template: str = "{graph_id}_{timestamp}_{format}"
    
    # Format-specific options
    cypher_options: Dict[str, Any] = field(default_factory=lambda: {
        "include_labels": True,
        "include_properties": True,
        "include_constraints": True
    })
    
    graphml_options: Dict[str, Any] = field(default_factory=lambda: {
        "include_attributes": True,
        "include_metadata": True
    })
    
    json_ld_options: Dict[str, Any] = field(default_factory=lambda: {
        "context_url": "https://schema.org/",
        "include_schema": True
    })


@dataclass
class TransferConfig:
    """Configuration for transferring graphs to KG Neo4j."""
    
    # API settings
    api_endpoint: str = "http://localhost:7474/api"
    api_timeout: int = 30
    api_retry_attempts: int = 3
    api_retry_delay: int = 5
    
    # Authentication
    username: str = "neo4j"
    password: str = "password"
    use_ssl: bool = False
    
    # Transfer options
    transfer_mode: str = "automatic"  # automatic, manual, scheduled
    priority: str = "normal"  # low, normal, high, urgent
    
    # Batch processing
    batch_size: int = 10
    enable_parallel_transfer: bool = True
    max_concurrent_transfers: int = 5
    
    # Error handling
    retry_failed_transfers: bool = True
    max_retry_attempts: int = 3
    quarantine_failed_graphs: bool = True


@dataclass
class SyncConfig:
    """Configuration for graph synchronization."""
    
    # Sync settings
    sync_interval: int = 300  # seconds
    enable_auto_sync: bool = True
    enable_background_sync: bool = True
    
    # Conflict resolution
    conflict_resolution: str = "ai_rag_wins"  # ai_rag_wins, kg_neo4j_wins, merge, manual
    enable_conflict_detection: bool = True
    max_conflict_resolution_time: int = 60
    
    # Sync strategies
    sync_strategies: List[str] = field(default_factory=lambda: [
        "full_sync", "incremental_sync", "selective_sync"
    ])
    
    # Monitoring
    enable_sync_monitoring: bool = True
    sync_health_check_interval: int = 60
    max_sync_failures: int = 5


@dataclass
class LifecycleConfig:
    """Configuration for graph lifecycle management."""
    
    # Lifecycle stages
    stages: List[str] = field(default_factory=lambda: [
        "created", "processing", "validated", "published", "active", "archived"
    ])
    
    # Stage transitions
    auto_transitions: bool = True
    transition_timeout: int = 300  # seconds
    enable_stage_validation: bool = True
    
    # Workflow management
    default_workflow: str = "standard"
    available_workflows: List[str] = field(default_factory=lambda: [
        "standard", "fast_track", "quality_focused", "manual_review"
    ])
    
    # Cleanup and maintenance
    cleanup_interval: int = 3600  # seconds
    max_graph_age: int = 2592000  # 30 days in seconds
    enable_auto_archiving: bool = True
    
    # Event handling
    enable_event_logging: bool = True
    max_event_history: int = 1000
    event_retention_days: int = 90


@dataclass
class ProcessorIntegrationConfig:
    """Main configuration for the processor integration service."""
    
    # Service settings
    service_name: str = "AI RAG Processor Integration Service"
    service_version: str = "1.0.0"
    enable_logging: bool = True
    log_level: str = "INFO"
    
    # Integration modes
    integration_mode: str = "automatic"  # automatic, manual, hybrid
    enable_real_time_processing: bool = True
    enable_batch_processing: bool = True
    
    # Processor handlers
    enabled_processors: List[str] = field(default_factory=lambda: [
        "document", "spreadsheet", "code", "image", "cad", 
        "structured_data", "graph_data"
    ])
    
    # Processing options
    max_concurrent_processing: int = 5
    processing_timeout: int = 300  # seconds
    enable_processing_queue: bool = True
    max_queue_size: int = 100
    
    # Error handling
    max_retry_attempts: int = 3
    retry_delay: int = 5
    enable_error_recovery: bool = True
    quarantine_failed_items: bool = True
    
    # Monitoring and metrics
    enable_metrics_collection: bool = True
    metrics_interval: int = 60  # seconds
    enable_health_checks: bool = True
    health_check_interval: int = 30
    
    # Component configurations
    entity_extraction: EntityExtractionConfig = field(default_factory=EntityExtractionConfig)
    relationship_discovery: RelationshipDiscoveryConfig = field(default_factory=RelationshipDiscoveryConfig)
    graph_building: GraphBuildingConfig = field(default_factory=GraphBuildingConfig)
    graph_validation: GraphValidationConfig = field(default_factory=GraphValidationConfig)
    graph_export: GraphExportConfig = field(default_factory=GraphExportConfig)
    transfer: TransferConfig = field(default_factory=TransferConfig)
    sync: SyncConfig = field(default_factory=SyncConfig)
    lifecycle: LifecycleConfig = field(default_factory=LifecycleConfig)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary format."""
        return {
            "service_name": self.service_name,
            "service_version": self.service_version,
            "enable_logging": self.enable_logging,
            "log_level": self.log_level,
            "integration_mode": self.integration_mode,
            "enable_real_time_processing": self.enable_real_time_processing,
            "enable_batch_processing": self.enable_batch_processing,
            "enabled_processors": self.enabled_processors,
            "max_concurrent_processing": self.max_concurrent_processing,
            "processing_timeout": self.processing_timeout,
            "enable_processing_queue": self.enable_processing_queue,
            "max_queue_size": self.max_queue_size,
            "max_retry_attempts": self.max_retry_attempts,
            "retry_delay": self.retry_delay,
            "enable_error_recovery": self.enable_error_recovery,
            "quarantine_failed_items": self.quarantine_failed_items,
            "enable_metrics_collection": self.enable_metrics_collection,
            "metrics_interval": self.metrics_interval,
            "enable_health_checks": self.enable_health_checks,
            "health_check_interval": self.health_check_interval,
            "entity_extraction": {
                "min_confidence": self.entity_extraction.min_confidence,
                "max_confidence": self.entity_extraction.max_confidence,
                "max_entities": self.entity_extraction.max_entities,
                "min_entities": self.entity_extraction.min_entities,
                "entity_types": self.entity_extraction.entity_types,
                "min_content_length": self.entity_extraction.min_content_length,
                "max_content_length": self.entity_extraction.max_content_length,
                "enable_nlp_enhancement": self.entity_extraction.enable_nlp_enhancement,
                "enable_domain_knowledge": self.entity_extraction.enable_domain_knowledge,
                "enable_entity_linking": self.entity_extraction.enable_entity_linking
            },
            "relationship_discovery": {
                "min_confidence": self.relationship_discovery.min_confidence,
                "max_confidence": self.relationship_discovery.max_confidence,
                "max_relationships": self.relationship_discovery.max_relationships,
                "min_relationships": self.relationship_discovery.min_relationships,
                "relationship_types": self.relationship_discovery.relationship_types,
                "enable_semantic_analysis": self.relationship_discovery.enable_semantic_analysis,
                "enable_pattern_matching": self.relationship_discovery.enable_pattern_matching,
                "enable_context_analysis": self.relationship_discovery.enable_context_analysis,
                "max_discovery_time": self.relationship_discovery.max_discovery_time,
                "enable_parallel_processing": self.relationship_discovery.enable_parallel_processing
            },
            "graph_building": {
                "max_nodes": self.graph_building.max_nodes,
                "max_edges": self.graph_building.max_edges,
                "min_nodes": self.graph_building.min_nodes,
                "min_edges": self.graph_building.min_edges,
                "enable_cycles": self.graph_building.enable_cycles,
                "enable_loops": self.graph_building.enable_loops,
                "enable_directed_edges": self.graph_building.enable_directed_edges,
                "enable_weighted_edges": self.graph_building.enable_weighted_edges,
                "max_node_properties": self.graph_building.max_node_properties,
                "max_edge_properties": self.graph_building.max_edge_properties,
                "min_connectivity": self.graph_building.min_connectivity,
                "max_isolated_nodes": self.graph_building.max_isolated_nodes,
                "enable_optimization": self.graph_building.enable_optimization,
                "enable_validation": self.graph_building.enable_validation
            },
            "graph_validation": {
                "min_quality_score": self.graph_validation.min_quality_score,
                "max_validation_time": self.graph_validation.max_validation_time,
                "enable_schema_validation": self.graph_validation.enable_schema_validation,
                "enable_structure_validation": self.graph_validation.enable_structure_validation,
                "enable_property_validation": self.graph_validation.enable_property_validation,
                "enable_connectivity_validation": self.graph_validation.enable_connectivity_validation,
                "min_node_coverage": self.graph_validation.min_node_coverage,
                "min_edge_coverage": self.graph_validation.min_edge_coverage,
                "max_duplicate_entities": self.graph_validation.max_duplicate_entities,
                "fail_on_critical_errors": self.graph_validation.fail_on_critical_errors,
                "max_validation_warnings": self.graph_validation.max_validation_warnings
            },
            "graph_export": {
                "formats": self.graph_export.formats,
                "include_metadata": self.graph_export.include_metadata,
                "include_properties": self.graph_export.include_properties,
                "include_statistics": self.graph_export.include_statistics,
                "enable_compression": self.graph_export.enable_compression,
                "output_directory": self.graph_export.output_directory,
                "filename_template": self.graph_export.filename_template,
                "cypher_options": self.graph_export.cypher_options,
                "graphml_options": self.graph_export.graphml_options,
                "json_ld_options": self.graph_export.json_ld_options
            },
            "transfer": {
                "api_endpoint": self.transfer.api_endpoint,
                "api_timeout": self.transfer.api_timeout,
                "api_retry_attempts": self.transfer.api_retry_attempts,
                "api_retry_delay": self.transfer.api_retry_delay,
                "username": self.transfer.username,
                "password": self.transfer.password,
                "use_ssl": self.transfer.use_ssl,
                "transfer_mode": self.transfer.transfer_mode,
                "priority": self.transfer.priority,
                "batch_size": self.transfer.batch_size,
                "enable_parallel_transfer": self.transfer.enable_parallel_transfer,
                "max_concurrent_transfers": self.transfer.max_concurrent_transfers,
                "retry_failed_transfers": self.transfer.retry_failed_transfers,
                "max_retry_attempts": self.transfer.max_retry_attempts,
                "quarantine_failed_graphs": self.transfer.quarantine_failed_graphs
            },
            "sync": {
                "sync_interval": self.sync.sync_interval,
                "enable_auto_sync": self.sync.enable_auto_sync,
                "enable_background_sync": self.sync.enable_background_sync,
                "conflict_resolution": self.sync.conflict_resolution,
                "enable_conflict_detection": self.sync.enable_conflict_detection,
                "max_conflict_resolution_time": self.sync.max_conflict_resolution_time,
                "sync_strategies": self.sync.sync_strategies,
                "enable_sync_monitoring": self.sync.enable_sync_monitoring,
                "sync_health_check_interval": self.sync.sync_health_check_interval,
                "max_sync_failures": self.sync.max_sync_failures
            },
            "lifecycle": {
                "stages": self.lifecycle.stages,
                "auto_transitions": self.lifecycle.auto_transitions,
                "transition_timeout": self.lifecycle.transition_timeout,
                "enable_stage_validation": self.lifecycle.enable_stage_validation,
                "default_workflow": self.lifecycle.default_workflow,
                "available_workflows": self.lifecycle.available_workflows,
                "cleanup_interval": self.lifecycle.cleanup_interval,
                "max_graph_age": self.lifecycle.max_graph_age,
                "enable_auto_archiving": self.lifecycle.enable_auto_archiving,
                "enable_event_logging": self.lifecycle.enable_event_logging,
                "max_event_history": self.lifecycle.max_event_history,
                "event_retention_days": self.lifecycle.event_retention_days
            }
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ProcessorIntegrationConfig':
        """Create configuration from dictionary."""
        config = cls()
        
        # Update basic settings
        for key, value in config_dict.items():
            if hasattr(config, key) and not key.startswith('_'):
                setattr(config, key, value)
        
        # Update component configurations if provided
        if 'entity_extraction' in config_dict:
            for key, value in config_dict['entity_extraction'].items():
                if hasattr(config.entity_extraction, key):
                    setattr(config.entity_extraction, key, value)
        
        if 'relationship_discovery' in config_dict:
            for key, value in config_dict['relationship_discovery'].items():
                if hasattr(config.relationship_discovery, key):
                    setattr(config.relationship_discovery, key, value)
        
        if 'graph_building' in config_dict:
            for key, value in config_dict['graph_building'].items():
                if hasattr(config.graph_building, key):
                    setattr(config.graph_building, key, value)
        
        if 'graph_validation' in config_dict:
            for key, value in config_dict['graph_validation'].items():
                if hasattr(config.graph_validation, key):
                    setattr(config.graph_validation, key, value)
        
        if 'graph_export' in config_dict:
            for key, value in config_dict['graph_export'].items():
                if hasattr(config.graph_export, key):
                    setattr(config.graph_export, key, value)
        
        if 'transfer' in config_dict:
            for key, value in config_dict['transfer'].items():
                if hasattr(config.transfer, key):
                    setattr(config.transfer, key, value)
        
        if 'sync' in config_dict:
            for key, value in config_dict['sync'].items():
                if hasattr(config.sync, key):
                    setattr(config.sync, key, value)
        
        if 'lifecycle' in config_dict:
            for key, value in config_dict['lifecycle'].items():
                if hasattr(config.lifecycle, key):
                    setattr(config.lifecycle, key, value)
        
        return config


# Default configuration instance
DEFAULT_CONFIG = ProcessorIntegrationConfig()

# Environment-specific configurations
DEVELOPMENT_CONFIG = ProcessorIntegrationConfig(
    log_level="DEBUG",
    enable_metrics_collection=True,
    enable_health_checks=True,
    processing_timeout=600,  # Longer timeout for development
    max_retry_attempts=5
)

PRODUCTION_CONFIG = ProcessorIntegrationConfig(
    log_level="WARNING",
    enable_metrics_collection=True,
    enable_health_checks=True,
    processing_timeout=180,  # Shorter timeout for production
    max_retry_attempts=3,
    enable_error_recovery=True,
    quarantine_failed_items=True
)

TESTING_CONFIG = ProcessorIntegrationConfig(
    log_level="DEBUG",
    enable_metrics_collection=False,
    enable_health_checks=False,
    processing_timeout=60,  # Short timeout for testing
    max_retry_attempts=1,
    enable_error_recovery=False,
    quarantine_failed_items=False
)
