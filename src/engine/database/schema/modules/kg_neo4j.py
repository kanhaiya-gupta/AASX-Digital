"""
KG Neo4j Schema Module
=======================

Manages Knowledge Graph Neo4j database tables for the AASX Digital Twin Framework.
Provides comprehensive knowledge graph lifecycle management, Neo4j synchronization tracking,
ML training traceability, schema management, and performance metrics while maintaining 
world-class traceability and framework integration with metadata and references only.

ENTERPRISE-GRADE FEATURES:
- Advanced knowledge graph lifecycle management with ML-powered insights
- Automated performance monitoring and optimization for graph operations
- Comprehensive health assessment and alerting for knowledge graph pipelines
- Enterprise-grade metrics and analytics for graph operations
- Advanced security and compliance capabilities for graph management
"""

import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import json
import asyncio
from ..base_schema import BaseSchema

logger = logging.getLogger(__name__)


class KgNeo4jSchema(BaseSchema):
    """
    Enterprise-Grade KG Neo4j Schema Module

    Manages the following tables:
    - kg_graph_registry: Main knowledge graph registry and lifecycle management (Enhanced with ML, Compliance, Security, Multiple Graph Sources)
    - kg_neo4j_ml_registry: ML models and training sessions registry (Enhanced with Performance Analytics)
    - kg_graph_metrics: Performance metrics and analytics (Enhanced with Enterprise Metrics)

    Multiple Graph Source Support:
    - AASX Files: 1 AASX file = 1 graph (single source)
    - Twin Registry: 1 twin = 1 graph (single source)
    - AI RAG: 1 AASX file = Multiple documents = Multiple graphs (multiple sources)
    """

    def __init__(self, connection_manager, schema_name: str = "kg_neo4j"):
        super().__init__(connection_manager, schema_name)
        self._kg_neo4j_metrics = {}
        self._performance_analytics = {}
        self._compliance_status = {}
        self._security_metrics = {}

    def get_module_description(self) -> str:
        """Get human-readable description of this module."""
        return "Knowledge Graph Neo4j module for comprehensive graph lifecycle management, Neo4j synchronization, ML training traceability, schema management, relationship analytics, multiple graph source support, and complete framework integration"

    def get_table_names(self) -> List[str]:
        """Get list of table names managed by this module."""
        return ["kg_graph_registry", "kg_neo4j_ml_registry", "kg_graph_metrics"]

    async def initialize(self) -> bool:
        """Initialize the KG Neo4j schema with enterprise-grade features."""
        try:
            # Call parent initialization
            if not await super().initialize():
                return False
            
            # Create consolidated tables
            await self._create_consolidated_tables()
            
            logger.info("✅ KG Neo4j Schema initialized with enterprise-grade features")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize KG Neo4j Schema: {e}")
            return False



    async def create_tables(self) -> bool:
        """
        Create all KG Neo4j tables.

        Returns:
            bool: True if all tables created successfully, False otherwise
        """
        try:
            logger.info("🧠 Creating KG Neo4j Module Tables...")

            # Create tables in dependency order
            tables_created = []

            # 1. Create KG Graph Registry Table (Enhanced)
            if await self._create_kg_graph_registry_table():
                tables_created.append("kg_graph_registry")
            else:
                logger.error("Failed to create kg_graph_registry table")
                return False

            # 2. Create KG Neo4j ML Registry Table (Enhanced)
            if await self._create_kg_neo4j_ml_registry_table():
                tables_created.append("kg_neo4j_ml_registry")
            else:
                logger.error("Failed to create kg_neo4j_ml_registry table")
                return False

            # 3. Create KG Graph Metrics Table (Enhanced)
            if await self._create_kg_graph_metrics_table():
                tables_created.append("kg_graph_metrics")
            else:
                logger.error("Failed to create kg_graph_metrics table")
                return False

            logger.info(f"✅ KG Neo4j Module: Created {len(tables_created)} tables successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create KG Neo4j tables: {e}")
            return False

    async def _create_kg_graph_registry_table(self) -> bool:
        """Create the enhanced knowledge graph registry table with ML training capabilities and multiple graph source support."""
        query = """
            CREATE TABLE IF NOT EXISTS kg_graph_registry (
                -- Primary Identification
                graph_id TEXT PRIMARY KEY,                        -- Unique graph identifier
                file_id TEXT NOT NULL,                            -- Reference to source file
                graph_name TEXT NOT NULL,                         -- Human-readable graph name
                registry_name TEXT NOT NULL,                      -- Registry instance name
                
                -- Graph Classification & Metadata
                graph_category TEXT DEFAULT 'generic' CHECK (graph_category IN ('aasx', 'structured_data', 'hybrid', 'custom')),
                graph_type TEXT DEFAULT 'asset_graph' CHECK (graph_type IN ('asset_graph', 'relationship_graph', 'process_graph', 'composite')),
                graph_priority TEXT DEFAULT 'normal' CHECK (graph_priority IN ('low', 'normal', 'high', 'critical')),
                graph_version TEXT DEFAULT '1.0.0',
                
                -- Workflow Classification (CRITICAL for dual workflow support)
                registry_type TEXT NOT NULL CHECK (registry_type IN ('extraction', 'generation', 'hybrid')),
                workflow_source TEXT NOT NULL CHECK (workflow_source IN ('aasx_file', 'structured_data', 'both')),
                
                -- ML Training Status (NEW for ML traceability)
                ml_training_enabled BOOLEAN DEFAULT FALSE,         -- Whether ML training is enabled
                active_ml_sessions INTEGER DEFAULT 0,             -- Number of active ML training sessions
                total_models_trained INTEGER DEFAULT 0,           -- Total number of models trained
                ml_model_count INTEGER DEFAULT 0,                 -- Current number of ML models
                
                -- Schema Management (NEW for schema traceability)
                schema_version TEXT DEFAULT '1.0.0',              -- Current schema version
                ontology_version TEXT DEFAULT '1.0.0',            -- Current ontology version
                validation_rules_count INTEGER DEFAULT 0,         -- Number of validation rules
                schema_validation_status TEXT DEFAULT 'pending' CHECK (schema_validation_status IN ('pending', 'validated', 'failed', 'outdated')),
                
                -- Data Quality Management (NEW for quality traceability)
                quality_rules_count INTEGER DEFAULT 0,            -- Number of quality rules
                validation_status TEXT DEFAULT 'pending' CHECK (validation_status IN ('pending', 'validated', 'failed', 'outdated')),
                completeness_score REAL DEFAULT 0.0 CHECK (completeness_score >= 0.0 AND completeness_score <= 1.0),
                data_quality_status TEXT DEFAULT 'unknown' CHECK (data_quality_status IN ('unknown', 'excellent', 'good', 'fair', 'poor')),
                
                -- External Storage References (NEW for ML traceability - NO data storage)
                model_storage_path TEXT,                          -- Path to ML model storage (external)
                dataset_storage_path TEXT,                        -- Path to dataset storage (external)
                config_storage_path TEXT,                         -- Path to configuration storage (external)
                schema_storage_path TEXT,                         -- Path to schema storage (external)
                ontology_storage_path TEXT,                       -- Path to ontology storage (external)
                
                -- Module Integration References (Links to other modules - NO data duplication)
                aasx_integration_id TEXT,                         -- Reference to aasx_processing table
                twin_registry_id TEXT,                             -- Reference to twin_registry table
                physics_modeling_id TEXT,                          -- Reference to physics_modeling table
                federated_learning_id TEXT,                        -- Reference to federated_learning table
                ai_rag_id TEXT,                                    -- Reference to ai_rag_registry table
                certificate_manager_id TEXT,                       -- Reference to certificate module
                
                -- Integration Status & Health
                integration_status TEXT DEFAULT 'pending' CHECK (integration_status IN ('pending', 'active', 'inactive', 'error', 'maintenance', 'deprecated')),
                overall_health_score INTEGER DEFAULT 0 CHECK (overall_health_score >= 0 AND overall_health_score <= 100),
                health_status TEXT DEFAULT 'unknown' CHECK (health_status IN ('unknown', 'healthy', 'warning', 'critical', 'offline')),
                
                -- Lifecycle Management
                lifecycle_status TEXT DEFAULT 'created' CHECK (lifecycle_status IN ('created', 'active', 'suspended', 'archived', 'retired')),
                lifecycle_phase TEXT DEFAULT 'development' CHECK (lifecycle_phase IN ('development', 'testing', 'production', 'maintenance', 'sunset')),
                
                -- Operational Status
                operational_status TEXT DEFAULT 'stopped' CHECK (operational_status IN ('running', 'stopped', 'paused', 'error', 'maintenance')),
                availability_status TEXT DEFAULT 'offline' CHECK (availability_status IN ('online', 'offline', 'degraded', 'maintenance')),
                
                -- Neo4j-Specific Status (NEW for Knowledge Graph)
                neo4j_import_status TEXT DEFAULT 'pending' CHECK (neo4j_import_status IN ('pending', 'in_progress', 'completed', 'failed', 'scheduled')),
                neo4j_export_status TEXT DEFAULT 'pending' CHECK (neo4j_export_status IN ('pending', 'in_progress', 'completed', 'failed', 'scheduled')),
                last_neo4j_sync_at TEXT,                           -- Last Neo4j synchronization timestamp
                next_neo4j_sync_at TEXT,                           -- Next scheduled Neo4j synchronization
                neo4j_sync_error_count INTEGER DEFAULT 0,          -- Count of consecutive Neo4j sync failures
                neo4j_sync_error_message TEXT,                     -- Last Neo4j sync error message
                
                -- Graph Data Metrics (NEW for Knowledge Graph)
                total_nodes INTEGER DEFAULT 0,                     -- Total number of nodes in the graph
                total_relationships INTEGER DEFAULT 0,              -- Total number of relationships in the graph
                graph_complexity TEXT DEFAULT 'simple' CHECK (graph_complexity IN ('simple', 'moderate', 'complex', 'very_complex')),
                
                -- Multiple Graph Support (CONSOLIDATED from multiple sources)
                -- graphs_json: JSON object storing multiple graphs with unique IDs as keys
                --   Example: {"graph_001": {"type": "asset_graph", "source": "aasx", "nodes": 150, "relationships": 300},
                --            "graph_002": {"type": "relationship_graph", "source": "ai_rag_doc_1", "nodes": 75, "relationships": 120},
                --            "graph_003": {"type": "process_graph", "source": "twin_registry", "nodes": 200, "relationships": 450}}
                -- graph_count: Total number of graphs stored in graphs_json
                -- graph_types: JSON object of graph types with counts {"asset_graph": 2, "relationship_graph": 1, "process_graph": 1}
                -- graph_sources: JSON object of graph sources with counts {"aasx": 1, "ai_rag": 1, "twin_registry": 1}
                graphs_json TEXT DEFAULT '{}',                     -- JSON object of all graphs from this source
                graph_count INTEGER DEFAULT 0,                     -- Total number of graphs
                graph_types TEXT DEFAULT '{}',                     -- JSON object of graph types with counts
                graph_sources TEXT DEFAULT '{}',                    -- JSON object of graph sources with counts
                
                -- Performance & Quality Metrics
                performance_score REAL DEFAULT 0.0 CHECK (performance_score >= 0.0 AND performance_score <= 1.0),
                data_quality_score REAL DEFAULT 0.0 CHECK (data_quality_score >= 0.0 AND data_quality_score <= 1.0),
                reliability_score REAL DEFAULT 0.0 CHECK (reliability_score >= 0.0 AND reliability_score <= 1.0),
                
                -- Security & Access Control
                security_level TEXT DEFAULT 'standard' CHECK (security_level IN ('public', 'internal', 'confidential', 'secret', 'top_secret')),
                access_control_level TEXT DEFAULT 'user' CHECK (access_control_level IN ('public', 'user', 'admin', 'system', 'restricted')),
                encryption_enabled BOOLEAN DEFAULT FALSE,           -- Whether graph data is encrypted
                audit_logging_enabled BOOLEAN DEFAULT TRUE,         -- Whether audit logging is enabled
                
                -- Enterprise Compliance & Security (Merged from enterprise tables)
                metric_type TEXT DEFAULT 'standard',               -- Type of metric being tracked
                metric_timestamp TEXT,                             -- Specific timestamp for the metric
                compliance_status TEXT DEFAULT 'pending' CHECK (compliance_status IN ('pending', 'compliant', 'non_compliant', 'requires_review', 'exempt')),
                compliance_type TEXT DEFAULT 'standard',            -- Type of compliance being tracked
                compliance_score REAL DEFAULT 0.0 CHECK (compliance_score >= 0.0 AND compliance_score <= 1.0),
                last_compliance_audit TEXT,                        -- Last compliance audit date
                next_compliance_audit TEXT,                         -- Next scheduled compliance audit
                compliance_audit_details TEXT DEFAULT '{}',         -- JSON: detailed compliance audit information
                compliance_rules_count INTEGER DEFAULT 0,           -- Number of active compliance rules
                compliance_violations_count INTEGER DEFAULT 0,     -- Number of compliance violations
                
                security_threat_level TEXT DEFAULT 'low' CHECK (security_threat_level IN ('low', 'medium', 'high', 'critical')),
                security_event_type TEXT DEFAULT 'none',           -- Type of security event
                threat_assessment TEXT DEFAULT 'low',              -- Detailed threat assessment description
                security_score REAL DEFAULT 0.0 CHECK (security_score >= 0.0 AND security_score <= 1.0),
                last_security_scan TEXT,                           -- Last security scan date
                security_scan_details TEXT DEFAULT '{}',           -- JSON: detailed security scan results
                security_incidents_count INTEGER DEFAULT 0,        -- Number of security incidents
                security_patches_count INTEGER DEFAULT 0,          -- Number of security patches applied
                security_vulnerabilities_count INTEGER DEFAULT 0,  -- Number of known vulnerabilities
                
                -- User Management & Ownership
                user_id TEXT NOT NULL,                             -- Current user who owns/accesses this graph
                org_id TEXT NOT NULL,                              -- Organization this graph belongs to
                dept_id TEXT,                                      -- Department for complete traceability
                owner_team TEXT,                                   -- Team responsible for this graph
                steward_user_id TEXT,                              -- Data steward for this graph
                
                -- Timestamps & Audit
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                activated_at TEXT,                                 -- When graph was first activated
                last_accessed_at TEXT,                             -- Last time any user accessed this graph
                last_modified_at TEXT,                             -- Last time graph data was modified
                
                -- Configuration & Metadata (JSON fields for flexibility)
                registry_config TEXT DEFAULT '{}',                 -- Registry configuration settings
                registry_metadata TEXT DEFAULT '{}',                -- Additional metadata
                custom_attributes TEXT DEFAULT '{}',                -- User-defined custom attributes
                tags TEXT DEFAULT '{}',                            -- JSON object of tags for categorization
                
                -- Relationships & Dependencies (JSON objects)
                relationships TEXT DEFAULT '{}',                    -- Object of relationship objects
                dependencies TEXT DEFAULT '{}',                     -- Object of dependency objects
                graph_instances TEXT DEFAULT '{}',                  -- Object of graph instance objects
                
                -- Constraints (INCLUDING ALL ORIGINAL FOREIGN KEYS)
                FOREIGN KEY (file_id) REFERENCES files (file_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                FOREIGN KEY (org_id) REFERENCES organizations (org_id) ON DELETE CASCADE,
                FOREIGN KEY (dept_id) REFERENCES departments (dept_id) ON DELETE SET NULL,
                FOREIGN KEY (aasx_integration_id) REFERENCES aasx_processing(job_id) ON DELETE SET NULL,
                FOREIGN KEY (twin_registry_id) REFERENCES twin_registry(registry_id) ON DELETE SET NULL,
                FOREIGN KEY (physics_modeling_id) REFERENCES physics_modeling(physics_id) ON DELETE SET NULL,
                FOREIGN KEY (federated_learning_id) REFERENCES federated_learning(learning_id) ON DELETE SET NULL,
                FOREIGN KEY (ai_rag_id) REFERENCES ai_rag_registry(registry_id) ON DELETE SET NULL,
                FOREIGN KEY (certificate_manager_id) REFERENCES certificate_manager(cert_id) ON DELETE SET NULL
            )
        """

        # Create the table using connection manager
        await self.connection_manager.execute_query(query)

        # Create indexes (INCLUDING ALL ORIGINAL INDEXES)
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_file_id ON kg_graph_registry (file_id)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_user_id ON kg_graph_registry (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_org_id ON kg_graph_registry (org_id)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_dept_id ON kg_graph_registry (dept_id)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_category ON kg_graph_registry (graph_category)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_type ON kg_graph_registry (graph_type)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_priority ON kg_graph_registry (graph_priority)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_registry_type ON kg_graph_registry (registry_type)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_workflow_source ON kg_graph_registry (workflow_source)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_status ON kg_graph_registry (integration_status)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_health ON kg_graph_registry (health_status)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_lifecycle ON kg_graph_registry (lifecycle_status)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_operational ON kg_graph_registry (operational_status)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_neo4j ON kg_graph_registry (neo4j_import_status, neo4j_export_status)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_complexity ON kg_graph_registry (graph_complexity)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_created ON kg_graph_registry (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_updated ON kg_graph_registry (updated_at)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_workflow ON kg_graph_registry (workflow_source, registry_type)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_ml ON kg_graph_registry (ml_training_enabled, active_ml_sessions)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_schema ON kg_graph_registry (schema_version, ontology_version)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_quality ON kg_graph_registry (validation_status, completeness_score)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_integration ON kg_graph_registry (aasx_integration_id, twin_registry_id, physics_modeling_id, federated_learning_id, ai_rag_id)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_performance ON kg_graph_registry (performance_score, data_quality_score, reliability_score)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_compliance ON kg_graph_registry (compliance_status, compliance_score, last_compliance_audit)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_security ON kg_graph_registry (security_threat_level, security_score, last_security_scan)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_enterprise_fields ON kg_graph_registry (metric_type, compliance_type, security_event_type)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_ai_rag ON kg_graph_registry (ai_rag_id)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_graph_count ON kg_graph_registry (graph_count)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_graph_sources ON kg_graph_registry (graph_sources)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_multiple_graphs ON kg_graph_registry (graph_count, graph_types, graph_sources)"
        ]

        return await self.create_indexes("kg_graph_registry", index_queries)

    async def _create_kg_neo4j_ml_registry_table(self) -> bool:
        """Create the KG Neo4j ML registry table for ML models and training sessions (METADATA + REFERENCES ONLY)."""
        query = """
            CREATE TABLE IF NOT EXISTS kg_neo4j_ml_registry (
                -- Primary Identification
                ml_registry_id TEXT PRIMARY KEY,                   -- Unique ML registry identifier
                graph_id TEXT NOT NULL,                            -- Reference to kg_graph_registry
                model_id TEXT NOT NULL,                            -- Unique model identifier
                session_id TEXT NOT NULL,                          -- Training session identifier
                
                -- Model Metadata (NO raw data - only metadata)
                model_name TEXT NOT NULL,                          -- Human-readable model name
                model_type TEXT NOT NULL CHECK (model_type IN ('node_classification', 'link_prediction', 'community_detection', 'anomaly_detection', 'graph_embedding', 'gnn', 'hybrid')),
                model_version TEXT DEFAULT '1.0.0',               -- Model version
                model_architecture TEXT,                           -- Model architecture description
                model_framework TEXT,                              -- ML framework used (PyTorch, TensorFlow, etc.)
                
                -- Training Session Metadata (NO raw data - only metadata)
                training_status TEXT DEFAULT 'pending' CHECK (training_status IN ('pending', 'in_progress', 'completed', 'failed', 'cancelled', 'paused')),
                training_type TEXT DEFAULT 'supervised' CHECK (training_type IN ('supervised', 'unsupervised', 'semi_supervised', 'reinforcement', 'transfer')),
                training_algorithm TEXT,                           -- Training algorithm used
                training_parameters TEXT DEFAULT '{}',             -- JSON: hyperparameters, learning rate, etc.
                
                -- External Storage References (NO data storage - only file paths)
                model_file_path TEXT,                             -- Path to trained model file (external storage)
                config_file_path TEXT,                             -- Path to training configuration (external storage)
                dataset_path TEXT,                                 -- Path to training dataset (external storage)
                logs_path TEXT,                                    -- Path to training logs (external storage)
                performance_logs_path TEXT,                        -- Path to performance logs (external storage)
                deployment_config_path TEXT,                       -- Path to deployment configuration (external storage)
                
                -- Training Performance Summary (NO raw data - only summary metrics)
                final_accuracy REAL CHECK (final_accuracy >= 0.0 AND final_accuracy <= 1.0),
                training_duration_seconds INTEGER,                 -- Total training time in seconds
                resource_consumption TEXT DEFAULT '{}',            -- JSON: CPU, memory, GPU usage summary
                training_efficiency_score REAL CHECK (training_efficiency_score >= 0.0 AND training_efficiency_score <= 1.0),
                
                -- Model Performance Metrics (NO raw data - only summary metrics)
                precision_score REAL CHECK (precision_score >= 0.0 AND precision_score <= 1.0),
                recall_score REAL CHECK (recall_score >= 0.0 AND recall_score <= 1.0),
                f1_score REAL CHECK (f1_score >= 0.0 AND f1_score <= 1.0),
                auc_score REAL CHECK (auc_score >= 0.0 AND auc_score <= 1.0),
                
                -- Training Data Metadata (NO raw data - only metadata)
                dataset_size INTEGER,                              -- Number of training samples
                feature_count INTEGER,                             -- Number of features used
                data_quality_score REAL CHECK (data_quality_score >= 0.0 AND data_quality_score <= 1.0),
                data_split_ratio TEXT DEFAULT '0.7:0.2:0.1',     -- Train:Validation:Test split
                
                -- Model Deployment & Usage (NO raw data - only metadata)
                deployment_status TEXT DEFAULT 'not_deployed' CHECK (deployment_status IN ('not_deployed', 'deployed', 'active', 'inactive', 'deprecated')),
                deployment_date TEXT,                              -- When model was deployed
                usage_count INTEGER DEFAULT 0,                     -- Number of times model was used
                last_used_at TEXT,                                -- Last time model was used
                
                -- Enterprise Performance Analytics (Merged from enterprise table)
                performance_trend TEXT DEFAULT 'stable' CHECK (performance_trend IN ('improving', 'stable', 'declining', 'fluctuating')),
                performance_metric TEXT DEFAULT 'standard',         -- Specific performance metric identifier
                performance_value REAL,                             -- Actual performance value
                optimization_suggestions TEXT DEFAULT '{}',         -- JSON: AI-generated optimization recommendations
                last_optimization_date TEXT,                       -- Last optimization performed
                optimization_effectiveness_score REAL CHECK (optimization_effectiveness_score >= 0.0 AND optimization_effectiveness_score <= 1.0),
                performance_benchmarks TEXT DEFAULT '{}',          -- JSON: performance benchmarks and comparisons
                resource_efficiency_score REAL CHECK (resource_efficiency_score >= 0.0 AND resource_efficiency_score <= 1.0),
                scalability_score REAL CHECK (scalability_score >= 0.0 AND scalability_score <= 1.0),
                
                -- Integration References (Links to other modules - NO data duplication)
                aasx_integration_id TEXT,                          -- Reference to aasx_processing table
                twin_registry_id TEXT,                              -- Reference to twin_registry table
                physics_modeling_id TEXT,                           -- Reference to physics_modeling table
                federated_learning_id TEXT,                         -- Reference to federated_learning table
                ai_rag_id TEXT,                                     -- Reference to ai_rag_registry table
                certificate_manager_id TEXT,                        -- Reference to certificate module
                
                -- Quality & Governance (NO raw data - only metadata)
                model_quality_score REAL CHECK (model_quality_score >= 0.0 AND model_quality_score <= 1.0),
                validation_status TEXT DEFAULT 'pending' CHECK (validation_status IN ('pending', 'validated', 'failed', 'requires_review')),
                compliance_score REAL CHECK (compliance_score >= 0.0 AND compliance_score <= 1.0),
                bias_detection_score REAL CHECK (bias_detection_score >= 0.0 AND bias_detection_score <= 1.0),
                
                -- Lifecycle Management (NO raw data - only metadata)
                lifecycle_status TEXT DEFAULT 'development' CHECK (lifecycle_status IN ('development', 'testing', 'production', 'maintenance', 'deprecated')),
                lifecycle_phase TEXT DEFAULT 'training' CHECK (lifecycle_phase IN ('training', 'validation', 'deployment', 'monitoring', 'retirement')),
                
                -- User Management & Ownership (NO raw data - only metadata)
                user_id TEXT NOT NULL,                              -- User who created/trained this model
                org_id TEXT NOT NULL,                               -- Organization this model belongs to
                owner_team TEXT,                                    -- Team responsible for this model
                steward_user_id TEXT,                               -- Data steward for this model
                
                -- Timestamps & Audit (NO raw data - only metadata)
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                training_started_at TEXT,                           -- When training started
                training_completed_at TEXT,                         -- When training completed
                last_accessed_at TEXT,                              -- Last time model was accessed
                
                -- Configuration & Metadata (JSON fields for flexibility - NO raw data)
                ml_config TEXT DEFAULT '{}',                        -- ML configuration settings
                model_metadata TEXT DEFAULT '{}',                    -- Additional model metadata
                custom_attributes TEXT DEFAULT '{}',                 -- User-defined custom attributes
                tags TEXT DEFAULT '{}',                             -- JSON object of tags for categorization
                
                -- Constraints
                FOREIGN KEY (graph_id) REFERENCES kg_graph_registry (graph_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                FOREIGN KEY (org_id) REFERENCES organizations (org_id) ON DELETE CASCADE,
                FOREIGN KEY (aasx_integration_id) REFERENCES aasx_processing(job_id) ON DELETE SET NULL,
                FOREIGN KEY (twin_registry_id) REFERENCES twin_registry(registry_id) ON DELETE SET NULL,
                FOREIGN KEY (physics_modeling_id) REFERENCES physics_modeling(physics_id) ON DELETE SET NULL,
                FOREIGN KEY (federated_learning_id) REFERENCES federated_learning(learning_id) ON DELETE SET NULL,
                FOREIGN KEY (ai_rag_id) REFERENCES ai_rag_registry(registry_id) ON DELETE SET NULL,
                FOREIGN KEY (certificate_manager_id) REFERENCES certificate_manager(cert_id) ON DELETE SET NULL
            )
        """

        # Create the table using connection manager
        await self.connection_manager.execute_query(query)

        # Create indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_kg_neo4j_ml_registry_graph_id ON kg_neo4j_ml_registry (graph_id)",
            "CREATE INDEX IF NOT EXISTS idx_kg_neo4j_ml_registry_model_id ON kg_neo4j_ml_registry (model_id)",
            "CREATE INDEX IF NOT EXISTS idx_kg_neo4j_ml_registry_session_id ON kg_neo4j_ml_registry (session_id)",
            "CREATE INDEX IF NOT EXISTS idx_kg_neo4j_ml_registry_model_type ON kg_neo4j_ml_registry (model_type)",
            "CREATE INDEX IF NOT EXISTS idx_kg_neo4j_ml_registry_training_status ON kg_neo4j_ml_registry (training_status)",
            "CREATE INDEX IF NOT EXISTS idx_kg_neo4j_ml_registry_deployment_status ON kg_neo4j_ml_registry (deployment_status)",
            "CREATE INDEX IF NOT EXISTS idx_kg_neo4j_ml_registry_user_id ON kg_neo4j_ml_registry (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_kg_neo4j_ml_registry_org_id ON kg_neo4j_ml_registry (org_id)",
            "CREATE INDEX IF NOT EXISTS idx_kg_neo4j_ml_registry_created ON kg_neo4j_ml_registry (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_kg_neo4j_ml_registry_performance ON kg_neo4j_ml_registry (final_accuracy, precision_score, recall_score, f1_score)",
            "CREATE INDEX IF NOT EXISTS idx_kg_neo4j_ml_registry_quality ON kg_neo4j_ml_registry (model_quality_score, validation_status, compliance_score)",
            "CREATE INDEX IF NOT EXISTS idx_kg_neo4j_ml_registry_integration ON kg_neo4j_ml_registry (aasx_integration_id, twin_registry_id, physics_modeling_id, federated_learning_id, ai_rag_id)",
            "CREATE INDEX IF NOT EXISTS idx_kg_neo4j_ml_registry_performance ON kg_neo4j_ml_registry (performance_trend, optimization_effectiveness_score, resource_efficiency_score, scalability_score)",
            "CREATE INDEX IF NOT EXISTS idx_kg_neo4j_ml_registry_enterprise_fields ON kg_neo4j_ml_registry (performance_metric, performance_value)"
        ]

        return await self.create_indexes("kg_neo4j_ml_registry", index_queries)

    async def _create_kg_graph_metrics_table(self) -> bool:
        """Create the enhanced knowledge graph metrics table with ML training metrics."""
        query = """
            CREATE TABLE IF NOT EXISTS kg_graph_metrics (
                -- Primary Identification
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                graph_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                
                -- Real-time Health Metrics (Framework Health)
                health_score INTEGER CHECK (health_score >= 0 AND health_score <= 100),
                response_time_ms REAL,
                uptime_percentage REAL CHECK (uptime_percentage >= 0.0 AND uptime_percentage <= 100.0),
                error_rate REAL CHECK (error_rate >= 0.0 AND error_rate <= 1.0),
                
                -- ML Training Metrics (NEW for ML traceability - NO raw data)
                active_training_sessions INTEGER DEFAULT 0,        -- Number of active ML training sessions
                completed_sessions INTEGER DEFAULT 0,              -- Number of completed training sessions
                failed_sessions INTEGER DEFAULT 0,                 -- Number of failed training sessions
                avg_model_accuracy REAL CHECK (avg_model_accuracy >= 0.0 AND avg_model_accuracy <= 1.0),
                training_success_rate REAL CHECK (training_success_rate >= 0.0 AND training_success_rate <= 1.0),
                model_deployment_rate REAL CHECK (model_deployment_rate >= 0.0 AND model_deployment_rate <= 1.0),
                
                -- Schema Quality Metrics (NEW for schema traceability - NO raw data)
                schema_validation_rate REAL CHECK (schema_validation_rate >= 0.0 AND schema_validation_rate <= 1.0),
                ontology_consistency_score REAL CHECK (ontology_consistency_score >= 0.0 AND ontology_consistency_score <= 1.0),
                quality_rule_effectiveness REAL CHECK (quality_rule_effectiveness >= 0.0 AND quality_rule_effectiveness <= 1.0),
                validation_rule_count INTEGER DEFAULT 0,           -- Number of active validation rules
                
                -- Neo4j Performance Metrics (ORIGINAL SCHEMA - Framework Performance)
                neo4j_connection_status TEXT CHECK (neo4j_connection_status IN ('connected', 'disconnected', 'error')),
                neo4j_query_response_time_ms REAL,
                neo4j_import_speed_nodes_per_sec REAL,
                neo4j_import_speed_rels_per_sec REAL,
                neo4j_memory_usage_mb REAL,
                neo4j_disk_usage_mb REAL,
                
                -- Graph Size Metrics (Framework Performance - Graph Scale)
                total_nodes INTEGER DEFAULT 0,                     -- Total number of nodes in the graph
                total_relationships INTEGER DEFAULT 0,              -- Total number of relationships in the graph
                graph_complexity TEXT DEFAULT 'simple' CHECK (graph_complexity IN ('simple', 'moderate', 'complex', 'very_complex')),
                
                -- Graph Analytics Metrics (ORIGINAL SCHEMA - Framework Performance)
                graph_traversal_speed_ms REAL,
                graph_query_complexity_score REAL CHECK (graph_query_complexity_score >= 0.0 AND graph_query_complexity_score <= 1.0),
                graph_visualization_performance REAL CHECK (graph_visualization_performance >= 0.0 AND graph_visualization_performance <= 1.0),
                graph_analysis_accuracy REAL CHECK (graph_analysis_accuracy >= 0.0 AND graph_analysis_accuracy <= 1.0),
                
                -- Knowledge Graph Performance Metrics (Framework Performance - NOT Data)
                graph_query_speed_sec REAL, -- Time to execute graph queries
                relationship_traversal_speed_sec REAL, -- Time to traverse relationships
                node_creation_speed_sec REAL, -- Time to create new nodes
                graph_analysis_efficiency REAL CHECK (graph_analysis_efficiency >= 0.0 AND graph_analysis_efficiency <= 1.0),
                
                -- Neo4j Performance Metrics (JSON for better framework analysis)
                neo4j_performance TEXT DEFAULT '{}', -- JSON: {
                                                       --   "import_operations": {"usage_count": 180, "avg_processing_time": 4.2, "success_rate": 0.97, "last_used": "2024-01-15T10:30:00Z"},
                                                       --   "export_operations": {"usage_count": 120, "avg_processing_time": 3.8, "success_rate": 0.95, "last_used": "2024-01-15T10:15:00Z"},
                                                       --   "sync_operations": {"usage_count": 250, "avg_processing_time": 2.1, "success_rate": 0.98, "last_used": "2024-01-15T10:00:00Z"},
                                                       --   "query_operations": {"usage_count": 500, "avg_processing_time": 0.8, "success_rate": 0.99, "last_used": "2024-01-15T09:45:00Z"},
                                                       --   "analysis_operations": {"usage_count": 90, "avg_processing_time": 5.5, "success_rate": 0.94, "last_used": "2024-01-15T09:30:00Z"}
                                                       -- }
                
                -- Graph Category Performance Metrics (JSON for better framework analysis)
                graph_category_performance_stats TEXT DEFAULT '{}', -- JSON: {
                                                                     --   "aasx": {"graphs": 200, "active": 195, "inactive": 5, "avg_query_time": 1.2, "health_distribution": {"healthy": 160, "warning": 25, "critical": 10}},
                                                                     --   "structured_data": {"graphs": 150, "active": 145, "inactive": 5, "avg_query_time": 0.9, "health_distribution": {"healthy": 130, "warning": 15, "critical": 5}},
                                                                     --   "hybrid": {"graphs": 80, "active": 75, "inactive": 5, "avg_query_time": 2.1, "health_distribution": {"healthy": 65, "warning": 10, "critical": 5}},
                                                                     --   "custom": {"graphs": 45, "active": 40, "inactive": 5, "avg_query_time": 1.8, "health_distribution": {"healthy": 35, "warning": 5, "critical": 0}}
                                                                     -- }
                
                -- User Interaction Metrics (ORIGINAL SCHEMA - Framework Usage)
                user_interaction_count INTEGER DEFAULT 0, -- Number of user interactions
                query_execution_count INTEGER DEFAULT 0, -- Number of queries executed
                visualization_view_count INTEGER DEFAULT 0, -- Number of visualization views
                export_operation_count INTEGER DEFAULT 0, -- Number of export operations
                graph_access_count INTEGER DEFAULT 0, -- Number of graph accesses
                successful_graph_operations INTEGER DEFAULT 0, -- Successful operations
                failed_graph_operations INTEGER DEFAULT 0, -- Failed operations
                
                -- Data Quality Metrics (Framework Quality - NOT Data Content)
                data_freshness_score REAL CHECK (data_freshness_score >= 0.0 AND data_freshness_score <= 1.0),
                data_completeness_score REAL CHECK (data_completeness_score >= 0.0 AND data_completeness_score <= 1.0),
                data_consistency_score REAL CHECK (data_consistency_score >= 0.0 AND data_consistency_score <= 1.0),
                data_accuracy_score REAL CHECK (data_accuracy_score >= 0.0 AND data_accuracy_score <= 1.0),
                
                -- System Resource Metrics (Framework Resources - NOT Data)
                cpu_usage_percent REAL CHECK (cpu_usage_percent >= 0.0 AND cpu_usage_percent <= 100.0),
                memory_usage_percent REAL CHECK (memory_usage_percent >= 0.0 AND memory_usage_percent <= 100.0),
                network_throughput_mbps REAL,
                storage_usage_percent REAL CHECK (storage_usage_percent >= 0.0 AND storage_usage_percent <= 100.0),
                disk_io_mb REAL, -- Disk I/O in MB
                
                -- Performance Trends (ORIGINAL SCHEMA - JSON fields)
                performance_trends TEXT DEFAULT '{}',
                resource_utilization_trends TEXT DEFAULT '{}',
                user_activity TEXT DEFAULT '{}',
                query_patterns TEXT DEFAULT '{}',
                relationship_patterns TEXT DEFAULT '{}',
                
                -- Knowledge Graph Patterns & Analytics (Framework Trends - JSON)
                knowledge_graph_patterns TEXT DEFAULT '{}', -- JSON: {"hourly": {...}, "daily": {...}, "weekly": {...}, "monthly": {...}}
                graph_operation_patterns TEXT DEFAULT '{}', -- JSON: {"operation_types": {...}, "complexity_distribution": {...}, "processing_times": {...}}
                compliance_status TEXT DEFAULT '{}', -- JSON: {"compliance_score": 0.95, "audit_status": "passed", "last_audit": "2024-01-15T00:00:00Z"}
                security_events TEXT DEFAULT '{}', -- JSON: {"events": {...}, "threat_level": "low", "last_security_scan": "2024-01-15T00:00:00Z"}
                
                -- Knowledge Graph-Specific Metrics (Framework Capabilities - JSON)
                knowledge_graph_analytics TEXT DEFAULT '{}', -- JSON: {"query_quality": 0.94, "traversal_quality": 0.92, "analysis_quality": 0.96}
                category_effectiveness TEXT DEFAULT '{}', -- JSON: {"category_comparison": {...}, "best_performing": "structured_data", "optimization_suggestions": {...}}
                workflow_performance TEXT DEFAULT '{}', -- JSON: {"extraction_performance": {...}, "generation_performance": {...}, "hybrid_performance": {...}}
                graph_size_performance_efficiency TEXT DEFAULT '{}', -- JSON: {"performance_by_graph_size": {...}, "quality_by_graph_size": {...}, "optimization_opportunities": {...}}
                
                -- Enterprise Metrics (Merged from enterprise tables)
                enterprise_metrics TEXT DEFAULT '{}', -- JSON: comprehensive enterprise metrics and monitoring data
                enterprise_compliance_metrics TEXT DEFAULT '{}', -- JSON: compliance tracking and auditing metrics
                enterprise_security_metrics TEXT DEFAULT '{}', -- JSON: security metrics and threat assessment data
                enterprise_performance_analytics TEXT DEFAULT '{}', -- JSON: performance analytics and optimization data
                
                -- Additional Enterprise Fields (Complete coverage)
                metric_type TEXT DEFAULT 'standard', -- Type of metric being tracked
                metric_timestamp TEXT, -- Specific timestamp for the metric
                compliance_type TEXT DEFAULT 'standard', -- Type of compliance being tracked
                security_event_type TEXT DEFAULT 'none', -- Type of security event
                performance_metric TEXT DEFAULT 'standard', -- Specific performance metric identifier
                performance_value REAL, -- Actual performance value
                
                -- Time-based Analytics (Framework Time Analysis)
                hour_of_day INTEGER CHECK (hour_of_day >= 0 AND hour_of_day <= 23),
                day_of_week INTEGER CHECK (day_of_week >= 1 AND day_of_week <= 7),
                month INTEGER CHECK (month >= 1 AND month <= 12),
                
                -- Performance Trends (Framework Performance Analysis)
                graph_management_trend REAL, -- Compared to historical average
                resource_efficiency_trend REAL, -- Performance over time
                quality_trend REAL, -- Quality metrics over time
                
                -- Foreign Key Constraints
                FOREIGN KEY (graph_id) REFERENCES kg_graph_registry (graph_id) ON DELETE CASCADE
            )
        """

        # Create the table using connection manager
        await self.connection_manager.execute_query(query)

        # Create indexes (INCLUDING ALL ORIGINAL INDEXES)
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_kg_metrics_graph_id ON kg_graph_metrics (graph_id)",
            "CREATE INDEX IF NOT EXISTS idx_kg_metrics_timestamp ON kg_graph_metrics (timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_kg_metrics_health ON kg_graph_metrics (health_score)",
            "CREATE INDEX IF NOT EXISTS idx_kg_metrics_neo4j ON kg_graph_metrics (neo4j_connection_status)",
            "CREATE INDEX IF NOT EXISTS idx_kg_metrics_graph_size ON kg_graph_metrics (total_nodes, total_relationships, graph_complexity)",
            "CREATE INDEX IF NOT EXISTS idx_kg_metrics_performance ON kg_graph_metrics (graph_visualization_performance, graph_analysis_accuracy)",
            "CREATE INDEX IF NOT EXISTS idx_kg_metrics_quality ON kg_graph_metrics (data_freshness_score, data_completeness_score)",
            "CREATE INDEX IF NOT EXISTS idx_kg_metrics_resources ON kg_graph_metrics (cpu_usage_percent, memory_usage_percent)",
            "CREATE INDEX IF NOT EXISTS idx_kg_metrics_user_activity ON kg_graph_metrics (user_interaction_count, query_execution_count)",
            "CREATE INDEX IF NOT EXISTS idx_kg_metrics_ml ON kg_graph_metrics (active_training_sessions, completed_sessions, failed_sessions)",
            "CREATE INDEX IF NOT EXISTS idx_kg_metrics_schema ON kg_graph_metrics (schema_validation_rate, ontology_consistency_score, quality_rule_effectiveness)",
            "CREATE INDEX IF NOT EXISTS idx_kg_metrics_graph_performance ON kg_graph_metrics (graph_query_speed_sec, relationship_traversal_speed_sec, node_creation_speed_sec)",
            "CREATE INDEX IF NOT EXISTS idx_kg_metrics_time_analysis ON kg_graph_metrics (hour_of_day, day_of_week, month)",
            "CREATE INDEX IF NOT EXISTS idx_kg_metrics_enterprise ON kg_graph_metrics (enterprise_metrics, enterprise_compliance_metrics, enterprise_security_metrics, enterprise_performance_analytics)",
            "CREATE INDEX IF NOT EXISTS idx_kg_metrics_enterprise_fields ON kg_graph_metrics (metric_type, compliance_type, security_event_type, performance_metric)"
        ]

        return await self.create_indexes("kg_graph_metrics", index_queries)

    # Enterprise-Grade Helper Methods (Consolidated into main tables)

    async def _create_consolidated_tables(self) -> bool:
        """Create all consolidated KG Neo4j tables."""
        try:
            # 1. Create KG Graph Registry Table (Enhanced)
            if await self._create_kg_graph_registry_table():
                logger.info("✅ kg_graph_registry table created/updated")
            else:
                logger.error("Failed to create/update kg_graph_registry table")
                return False

            # 2. Create KG Neo4j ML Registry Table (Enhanced)
            if await self._create_kg_neo4j_ml_registry_table():
                logger.info("✅ kg_neo4j_ml_registry table created/updated")
            else:
                logger.error("Failed to create/update kg_neo4j_ml_registry table")
                return False

            # 3. Create KG Graph Metrics Table (Enhanced)
            if await self._create_kg_graph_metrics_table():
                logger.info("✅ kg_graph_metrics table created/updated")
            else:
                logger.error("Failed to create/update kg_graph_metrics table")
                return False

            return True
            
        except Exception as e:
            logger.error(f"Failed to create consolidated KG Neo4j tables: {e}")
            return False




