"""
Federated Learning Schema Module
================================

Manages Federated Learning database tables for the AASX Digital Twin Framework.
Provides comprehensive federation management, model tracking, and performance monitoring
with metadata and references only - no raw data storage to prevent database explosion.

ENTERPRISE-GRADE FEATURES:
- Advanced federated learning lifecycle management with privacy-preserving insights
- Automated performance monitoring and optimization for federation operations
- Comprehensive health assessment and alerting for federated learning pipelines
- Enterprise-grade metrics and analytics for federation operations
- Advanced security and compliance capabilities for federated learning management
"""

import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import json
import asyncio
from ..base_schema import BaseSchema

logger = logging.getLogger(__name__)


class FederatedLearningSchema(BaseSchema):
    """
    Enterprise-Grade Federated Learning Schema Module

    Manages the following tables with enterprise functionality integrated:
    - federated_learning_registry: Main registry for federation sessions, models, metadata, compliance, security, and performance analytics
    - federated_learning_metrics: Performance metrics, contribution tracking, analytics, and enterprise metrics
    """

    def __init__(self, connection_manager, schema_name: str = "federated_learning"):
        super().__init__(connection_manager, schema_name)
        self._federated_learning_metrics = {}
        self._performance_analytics = {}
        self._compliance_status = {}
        self._security_metrics = {}

    def get_module_description(self) -> str:
        """Get human-readable description of this module."""
        return "Federated Learning module for collaborative machine learning across organizations with privacy preservation, enterprise compliance, security, and performance analytics integrated into main tables"

    def get_table_names(self) -> List[str]:
        """Get list of table names managed by this module."""
        return ["federated_learning_registry", "federated_learning_metrics"]

    async def initialize(self) -> bool:
        """Initialize the Federated Learning schema with enterprise-grade features."""
        try:
            # Call parent initialization
            if not await super().initialize():
                return False
            
            # Create core tables
            if not await self._create_enterprise_tables():
                return False
            
            logger.info("✅ Federated Learning Schema initialized with enterprise-grade features")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Federated Learning Schema: {e}")
            return False

    async def create_table(self, table_name: str, table_definition: Union[str, Dict[str, Any]]) -> bool:
        """Create a table with enterprise-grade features."""
        try:
            # Create the base table
            if isinstance(table_definition, str):
                # Direct SQL definition
                return await super().create_table(table_name, table_definition)
            else:
                # Dictionary definition
                return await super().create_table(table_name, table_definition)
            
        except Exception as e:
            logger.error(f"Failed to create table {table_name}: {e}")
            return False

    async def create_tables(self) -> bool:
        """
        Create all Federated Learning tables.

        Returns:
            bool: True if all tables created successfully, False otherwise
        """
        try:
            logger.info("🤝 Creating Federated Learning Module Tables...")

            # Create tables in dependency order
            tables_created = []

            # 1. Create Federated Learning Registry Table (no dependencies)
            if await self._create_federated_learning_registry_table():
                tables_created.append("federated_learning_registry")
            else:
                logger.error("Failed to create federated_learning_registry table")
                return False

            # 2. Create Federated Learning Metrics Table (depends on registry)
            if await self._create_federated_learning_metrics_table():
                tables_created.append("federated_learning_metrics")
            else:
                logger.error("Failed to create federated_learning_metrics table")
                return False

            logger.info(f"✅ Federated Learning Module: Created {len(tables_created)} tables successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create Federated Learning tables: {e}")
            return False

    async def _create_federated_learning_registry_table(self) -> bool:
        """Create the federated_learning_registry table for comprehensive federation management."""
        query = """
            CREATE TABLE IF NOT EXISTS federated_learning_registry (
                -- Primary Identification
                registry_id TEXT PRIMARY KEY,
                federation_name TEXT NOT NULL,
                registry_name TEXT NOT NULL,
                
                -- Federation Classification & Metadata
                federation_category TEXT NOT NULL DEFAULT 'collaborative_learning' -- collaborative_learning, privacy_preserving, secure_aggregation, hybrid
                    CHECK (federation_category IN ('collaborative_learning', 'privacy_preserving', 'secure_aggregation', 'hybrid')),
                federation_type TEXT NOT NULL DEFAULT 'fedavg' -- fedavg, secure_aggregation, differential_privacy, performance_weighting, hybrid
                    CHECK (federation_type IN ('fedavg', 'secure_aggregation', 'differential_privacy', 'performance_weighting', 'hybrid')),
                federation_priority TEXT NOT NULL DEFAULT 'normal' -- low, normal, high, critical, emergency
                    CHECK (federation_priority IN ('low', 'normal', 'high', 'critical', 'emergency')),
                federation_version TEXT NOT NULL DEFAULT '1.0.0', -- Semantic versioning
                
                -- Workflow Classification (CRITICAL for dual workflow support)
                registry_type TEXT NOT NULL -- extraction, generation, hybrid
                    CHECK (registry_type IN ('extraction', 'generation', 'hybrid')),
                workflow_source TEXT NOT NULL -- aasx_file, structured_data, both
                    CHECK (workflow_source IN ('aasx_file', 'structured_data', 'both')),
                
                -- Module Integration References (Links to other modules - NO data duplication)
                aasx_integration_id TEXT, -- Reference to aasx_processing table
                twin_registry_id TEXT, -- Reference to twin_registry table
                kg_neo4j_id TEXT, -- Reference to kg_graph_registry table
                physics_modeling_id TEXT, -- Reference to physics_modeling table
                ai_rag_id TEXT, -- Reference to ai_rag_registry table
                certificate_manager_id TEXT, -- Reference to certificate module
                
                -- Integration Status & Health
                integration_status TEXT NOT NULL DEFAULT 'pending' -- pending, active, inactive, error, maintenance, deprecated
                    CHECK (integration_status IN ('pending', 'active', 'inactive', 'error', 'maintenance', 'deprecated')),
                overall_health_score INTEGER DEFAULT 0 -- 0-100 health score across all modules
                    CHECK (overall_health_score >= 0 AND overall_health_score <= 100),
                health_status TEXT NOT NULL DEFAULT 'unknown' -- unknown, healthy, warning, critical, offline
                    CHECK (health_status IN ('unknown', 'healthy', 'warning', 'critical', 'offline')),
                
                -- Lifecycle Management
                lifecycle_status TEXT NOT NULL DEFAULT 'created' -- created, active, suspended, archived, retired
                    CHECK (lifecycle_status IN ('created', 'active', 'suspended', 'archived', 'retired')),
                lifecycle_phase TEXT NOT NULL DEFAULT 'setup' -- setup, recruitment, training, aggregation, evaluation, deployment, maintenance
                    CHECK (lifecycle_phase IN ('setup', 'recruitment', 'training', 'aggregation', 'evaluation', 'deployment', 'maintenance')),
                
                -- Operational Status
                operational_status TEXT NOT NULL DEFAULT 'stopped' -- running, stopped, paused, error, maintenance
                    CHECK (operational_status IN ('running', 'stopped', 'paused', 'error', 'maintenance')),
                availability_status TEXT NOT NULL DEFAULT 'offline' -- online, offline, degraded, maintenance
                    CHECK (availability_status IN ('online', 'offline', 'degraded', 'maintenance')),
                
                -- Federation-Specific Status (NEW for Federated Learning)
                federation_participation_status TEXT DEFAULT 'pending' -- pending, in_progress, completed, failed, scheduled
                    CHECK (federation_participation_status IN ('pending', 'in_progress', 'completed', 'failed', 'scheduled')),
                model_aggregation_status TEXT DEFAULT 'pending' -- pending, in_progress, completed, failed, scheduled
                    CHECK (model_aggregation_status IN ('pending', 'in_progress', 'completed', 'failed', 'scheduled')),
                privacy_compliance_status TEXT DEFAULT 'pending' -- pending, in_progress, completed, failed, scheduled
                    CHECK (privacy_compliance_status IN ('pending', 'in_progress', 'completed', 'failed', 'scheduled')),
                algorithm_execution_status TEXT DEFAULT 'pending' -- pending, in_progress, completed, failed, scheduled
                    CHECK (algorithm_execution_status IN ('pending', 'in_progress', 'completed', 'failed', 'scheduled')),
                last_federation_sync_at TEXT, -- Last federation synchronization timestamp
                next_federation_sync_at TEXT, -- Next scheduled federation synchronization
                federation_sync_error_count INTEGER DEFAULT 0, -- Count of consecutive federation sync failures
                federation_sync_error_message TEXT, -- Last federation sync error message
                
                -- Federation Data Metrics (NEW for Federated Learning)
                total_participating_twins INTEGER DEFAULT 0, -- Total number of participating twins
                total_federation_rounds INTEGER DEFAULT 0, -- Total federation rounds completed
                total_models_aggregated INTEGER DEFAULT 0, -- Total models aggregated
                federation_complexity TEXT DEFAULT 'simple' -- simple, moderate, complex, very_complex
                    CHECK (federation_complexity IN ('simple', 'moderate', 'complex', 'very_complex')),
                
                -- Performance & Quality Metrics
                performance_score REAL DEFAULT 0.0, -- 0.0-1.0 performance rating
                data_quality_score REAL DEFAULT 0.0, -- 0.0-1.0 data quality rating
                reliability_score REAL DEFAULT 0.0, -- 0.0-1.0 reliability rating
                compliance_score REAL DEFAULT 0.0, -- 0.0-1.0 compliance rating
                
                -- Enterprise Compliance Tracking (Merged from enterprise table)
                compliance_framework TEXT DEFAULT 'GDPR', -- Compliance framework (GDPR, HIPAA, etc.)
                compliance_status TEXT DEFAULT 'compliant', -- Current compliance status
                last_audit_date TEXT, -- Last audit date
                next_audit_date TEXT, -- Next scheduled audit date
                audit_details TEXT DEFAULT '{}', -- JSON audit details
                risk_level TEXT DEFAULT 'low', -- Risk assessment level
                
                -- Enterprise Security Metrics (Merged from enterprise table)
                security_score REAL DEFAULT 100.0, -- Overall security score
                threat_detection_score REAL DEFAULT 100.0, -- Threat detection effectiveness
                encryption_strength TEXT DEFAULT 'AES-256', -- Encryption strength used
                authentication_method TEXT DEFAULT 'multi_factor', -- Authentication method
                access_control_score REAL DEFAULT 100.0, -- Access control effectiveness
                data_protection_score REAL DEFAULT 100.0, -- Data protection score
                incident_response_time INTEGER DEFAULT 0, -- Incident response time in minutes
                security_audit_score REAL DEFAULT 100.0, -- Security audit score
                last_security_scan TEXT, -- Last security scan timestamp
                security_details TEXT DEFAULT '{}', -- JSON security details
                
                -- Enterprise Performance Analytics (Merged from enterprise table)
                efficiency_score REAL DEFAULT 100.0, -- Federation efficiency score
                scalability_score REAL DEFAULT 100.0, -- Scalability assessment
                optimization_potential REAL DEFAULT 100.0, -- Optimization potential score
                bottleneck_identification TEXT DEFAULT 'none', -- Identified bottlenecks
                performance_trend TEXT DEFAULT 'stable', -- Performance trend direction
                last_optimization_date TEXT, -- Last optimization performed
                optimization_suggestions TEXT DEFAULT '{}', -- JSON optimization suggestions
                
                -- Security & Access Control
                security_level TEXT NOT NULL DEFAULT 'standard' -- public, internal, confidential, secret, top_secret
                    CHECK (security_level IN ('public', 'internal', 'confidential', 'secret', 'top_secret')),
                access_control_level TEXT NOT NULL DEFAULT 'user' -- public, user, admin, system, restricted
                    CHECK (access_control_level IN ('public', 'user', 'admin', 'system', 'restricted')),
                encryption_enabled BOOLEAN DEFAULT TRUE, -- Whether federation data is encrypted
                audit_logging_enabled BOOLEAN DEFAULT TRUE, -- Whether audit logging is enabled
                
                -- User Management & Ownership
                user_id TEXT NOT NULL, -- Current user who owns/accesses this registry
                org_id TEXT NOT NULL, -- Organization this registry belongs to
                dept_id TEXT, -- Department for complete traceability
                owner_team TEXT, -- Team responsible for this federation
                steward_user_id TEXT, -- Data steward for this federation
                
                -- Timestamps & Audit
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                activated_at TEXT, -- When federation was first activated
                last_accessed_at TEXT, -- Last time any user accessed this federation
                last_modified_at TEXT, -- Last time federation data was modified
                
                -- Configuration & Metadata (JSON fields for flexibility)
                registry_config TEXT DEFAULT '{}', -- Registry configuration settings
                registry_metadata TEXT DEFAULT '{}', -- Additional metadata
                custom_attributes TEXT DEFAULT '{}', -- User-defined custom attributes
                tags TEXT DEFAULT '{}', -- JSON object of tags for categorization
                
                -- Relationships & Dependencies (JSON objects)
                relationships TEXT DEFAULT '{}', -- Object of relationship objects
                dependencies TEXT DEFAULT '{}', -- Object of dependency objects
                federation_instances TEXT DEFAULT '{}', -- Object of federation instance objects
                
                -- Constraints
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                FOREIGN KEY (org_id) REFERENCES organizations (org_id) ON DELETE CASCADE,
                FOREIGN KEY (dept_id) REFERENCES departments (dept_id) ON DELETE SET NULL,
                FOREIGN KEY (aasx_integration_id) REFERENCES aasx_processing(job_id) ON DELETE SET NULL,
                FOREIGN KEY (twin_registry_id) REFERENCES twin_registry(registry_id) ON DELETE SET NULL,
                FOREIGN KEY (kg_neo4j_id) REFERENCES kg_graph_registry(graph_id) ON DELETE SET NULL,
                FOREIGN KEY (physics_modeling_id) REFERENCES physics_modeling(physics_id) ON DELETE SET NULL,
                FOREIGN KEY (ai_rag_id) REFERENCES ai_rag_registry(registry_id) ON DELETE SET NULL,
                FOREIGN KEY (certificate_manager_id) REFERENCES certificate_manager(cert_id) ON DELETE SET NULL
            )
        """

        # Create the table using connection manager
        await self.connection_manager.execute_query(query)

        # Create indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_registry_user_id ON federated_learning_registry (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_registry_org_id ON federated_learning_registry (org_id)",
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_registry_dept_id ON federated_learning_registry (dept_id)",
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_registry_category ON federated_learning_registry (federation_category)",
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_registry_type ON federated_learning_registry (federation_type)",
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_registry_priority ON federated_learning_registry (federation_priority)",
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_registry_registry_type ON federated_learning_registry (registry_type)",
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_registry_workflow_source ON federated_learning_registry (workflow_source)",
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_registry_status ON federated_learning_registry (integration_status)",
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_registry_health ON federated_learning_registry (health_status)",
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_registry_lifecycle ON federated_learning_registry (lifecycle_status)",
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_registry_operational ON federated_learning_registry (operational_status)",
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_registry_federation ON federated_learning_registry (federation_participation_status, model_aggregation_status, privacy_compliance_status, algorithm_execution_status)",
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_registry_complexity ON federated_learning_registry (federation_complexity)",
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_registry_created ON federated_learning_registry (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_registry_updated ON federated_learning_registry (updated_at)",
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_registry_integration ON federated_learning_registry (aasx_integration_id, twin_registry_id, kg_neo4j_id, physics_modeling_id, ai_rag_id, certificate_manager_id)",
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_registry_performance ON federated_learning_registry (performance_score, data_quality_score, reliability_score)"
        ]

        return await self.create_indexes("federated_learning_registry", index_queries)

    async def _create_federated_learning_metrics_table(self) -> bool:
        """Create the federated_learning_metrics table for comprehensive performance monitoring."""
        query = """
            CREATE TABLE IF NOT EXISTS federated_learning_metrics (
                -- Primary Identification
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                registry_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                
                -- Real-time Health Metrics (Framework Health)
                health_score INTEGER CHECK (health_score >= 0 AND health_score <= 100),
                response_time_ms REAL,
                uptime_percentage REAL CHECK (uptime_percentage >= 0.0 AND uptime_percentage <= 100.0),
                error_rate REAL CHECK (error_rate >= 0.0 AND error_rate <= 1.0),
                
                -- Federation Performance Metrics (Framework Performance - NOT Data)
                federation_participation_speed_sec REAL, -- Time to manage federation participation
                model_aggregation_speed_sec REAL, -- Time to aggregate models
                privacy_compliance_speed_sec REAL, -- Time to ensure privacy compliance
                algorithm_execution_speed_sec REAL, -- Time to execute algorithms
                federation_efficiency REAL CHECK (federation_efficiency >= 0.0 AND federation_efficiency <= 1.0),
                
                -- Federation Management Performance (JSON for better framework analysis)
                federation_performance TEXT DEFAULT '{}', -- JSON: {
                                                                      --   "participation_management": {"usage_count": 500, "avg_processing_time": 0.8, "success_rate": 0.99, "last_used": "2024-01-15T10:30:00Z"},
                                                                      --   "model_aggregation": {"usage_count": 200, "avg_processing_time": 1.2, "success_rate": 0.98, "last_used": "2024-01-15T10:15:00Z"},
                                                                      --   "privacy_compliance": {"usage_count": 800, "avg_processing_time": 1.5, "success_rate": 0.97, "last_used": "2024-01-15T10:00:00Z"},
                                                                      --   "algorithm_execution": {"usage_count": 1200, "avg_processing_time": 2.1, "success_rate": 0.96, "last_used": "2024-01-15T09:45:00Z"},
                                                                      --   "federation_administration": {"usage_count": 150, "avg_processing_time": 3.2, "success_rate": 0.95, "last_used": "2024-01-15T09:30:00Z"}
                                                                      -- }
                
                -- Federation Category Performance Metrics (JSON for better framework analysis)
                federation_category_performance_stats TEXT DEFAULT '{}', -- JSON: {
                                                                          --   "collaborative_learning": {"federations": 50, "active": 48, "inactive": 2, "avg_response_time": 0.5, "health_distribution": {"healthy": 45, "warning": 3, "critical": 0}},
                                                                          --   "privacy_preserving": {"federations": 25, "active": 24, "inactive": 1, "avg_response_time": 0.8, "health_distribution": {"healthy": 22, "warning": 2, "critical": 0}},
                                                                          --   "secure_aggregation": {"federations": 30, "active": 29, "inactive": 1, "avg_response_time": 1.2, "health_distribution": {"healthy": 27, "warning": 2, "critical": 0}},
                                                                          --   "hybrid": {"federations": 40, "active": 38, "inactive": 2, "avg_response_time": 1.5, "health_distribution": {"healthy": 35, "warning": 3, "critical": 0}}
                                                                          -- }
                
                -- User Interaction Metrics (Framework Usage - NOT Content)
                user_interaction_count INTEGER DEFAULT 0, -- Number of user interactions
                federation_access_count INTEGER DEFAULT 0, -- Number of federation accesses
                successful_federation_operations INTEGER DEFAULT 0, -- Successful operations
                failed_federation_operations INTEGER DEFAULT 0, -- Failed operations
                
                -- Data Quality Metrics (Framework Quality - NOT Data Content)
                data_freshness_score REAL CHECK (data_freshness_score >= 0.0 AND data_freshness_score <= 1.0),
                data_completeness_score REAL CHECK (data_completeness_score >= 0.0 AND data_completeness_score <= 1.0),
                data_consistency_score REAL CHECK (data_consistency_score >= 0.0 AND data_consistency_score <= 1.0),
                data_accuracy_score REAL CHECK (data_accuracy_score >= 0.0 AND data_accuracy_score <= 1.0),
                
                -- Federation Resource Metrics (Framework Resources - NOT Data)
                cpu_usage_percent REAL CHECK (cpu_usage_percent >= 0.0 AND cpu_usage_percent <= 100.0),
                memory_usage_percent REAL CHECK (memory_usage_percent >= 0.0 AND memory_usage_percent <= 100.0),
                network_throughput_mbps REAL,
                storage_usage_percent REAL CHECK (storage_usage_percent >= 0.0 AND storage_usage_percent <= 100.0),
                gpu_usage_percent REAL CHECK (gpu_usage_percent >= 0.0 AND gpu_usage_percent <= 100.0),
                
                -- Federation Patterns & Analytics (Framework Trends - JSON)
                federation_patterns TEXT DEFAULT '{}', -- JSON: {"hourly": {...}, "daily": {...}, "weekly": {...}, "monthly": {...}}
                resource_utilization_trends TEXT DEFAULT '{}', -- JSON: {"cpu_trend": [...], "memory_trend": [...], "gpu_trend": [...]}
                user_activity TEXT DEFAULT '{}', -- JSON: {"peak_hours": [...], "user_patterns": {...}, "session_durations": [...]}
                federation_operation_patterns TEXT DEFAULT '{}', -- JSON: {"operation_types": {...}, "complexity_distribution": {...}, "processing_times": [...]}
                compliance_status TEXT DEFAULT '{}', -- JSON: {"compliance_score": 0.95, "audit_status": "passed", "last_audit": "2024-01-15T00:00:00Z"}
                privacy_events TEXT DEFAULT '{}', -- JSON: {"events": [...], "threat_level": "low", "last_privacy_scan": "2024-01-15T00:00:00Z"}
                
                -- Enterprise Metrics (Merged from enterprise table)
                enterprise_health_score INTEGER DEFAULT 100, -- Enterprise-level health score
                federation_efficiency_score INTEGER DEFAULT 100, -- Federation efficiency rating
                privacy_preservation_score INTEGER DEFAULT 100, -- Privacy preservation effectiveness
                model_quality_score INTEGER DEFAULT 100, -- Model quality assessment
                collaboration_effectiveness INTEGER DEFAULT 100, -- Collaboration effectiveness
                risk_assessment_score INTEGER DEFAULT 100, -- Risk assessment score
                compliance_adherence INTEGER DEFAULT 100, -- Compliance adherence level
                
                -- Federation-Specific Metrics (Framework Capabilities - JSON)
                federation_analytics TEXT DEFAULT '{}', -- JSON: {"participation_quality": 0.94, "aggregation_quality": 0.92, "privacy_quality": 0.96}
                category_effectiveness TEXT DEFAULT '{}', -- JSON: {"category_comparison": {...}, "best_performing": "collaborative_learning", "optimization_suggestions": [...]}
                algorithm_performance TEXT DEFAULT '{}', -- JSON: {"fedavg_performance": {...}, "secure_aggregation_performance": {...}, "hybrid_performance": {...}}
                federation_size_performance_efficiency TEXT DEFAULT '{}', -- JSON: {"performance_by_federation_size": {...}, "quality_by_federation_size": {...}, "optimization_opportunities": [...]}
                
                -- Time-based Analytics (Framework Time Analysis)
                hour_of_day INTEGER CHECK (hour_of_day >= 0 AND hour_of_day <= 23),
                day_of_week INTEGER CHECK (day_of_week >= 1 AND day_of_week <= 7),
                month INTEGER CHECK (month >= 1 AND month <= 12),
                
                -- Performance Trends (Framework Performance Analysis)
                federation_management_trend REAL, -- Compared to historical average
                resource_efficiency_trend REAL, -- Performance over time
                quality_trend REAL, -- Quality metrics over time
                
                -- Foreign Key Constraints
                FOREIGN KEY (registry_id) REFERENCES federated_learning_registry (registry_id) ON DELETE CASCADE
            )
        """

        # Create the table using connection manager
        await self.connection_manager.execute_query(query)

        # Create indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_metrics_registry_id ON federated_learning_metrics (registry_id)",
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_metrics_timestamp ON federated_learning_metrics (timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_metrics_health ON federated_learning_metrics (health_score)",
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_metrics_performance ON federated_learning_metrics (federation_participation_speed_sec, model_aggregation_speed_sec, privacy_compliance_speed_sec, algorithm_execution_speed_sec)",
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_metrics_quality ON federated_learning_metrics (data_freshness_score, data_completeness_score)",
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_metrics_resources ON federated_learning_metrics (cpu_usage_percent, memory_usage_percent, gpu_usage_percent)",
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_metrics_user_activity ON federated_learning_metrics (user_interaction_count, federation_access_count)",
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_metrics_federation ON federated_learning_metrics (federation_performance)",
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_metrics_category ON federated_learning_metrics (federation_category_performance_stats)",
            "CREATE INDEX IF NOT EXISTS idx_federated_learning_metrics_time_analysis ON federated_learning_metrics (hour_of_day, day_of_week, month)"
        ]

        return await self.create_indexes("federated_learning_metrics", index_queries)

    # Enterprise-Grade Helper Methods

    async def _create_enterprise_tables(self) -> bool:
        """Create all enterprise Federated Learning tables."""
        try:
            # Create core tables
            if not await self._create_federated_learning_registry_table():
                return False
            
            if not await self._create_federated_learning_metrics_table():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create enterprise tables: {e}")
            return False
