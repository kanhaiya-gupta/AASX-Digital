"""
Twin Registry Schema Module
===========================

Manages Twin Registry database tables for the AASX Digital Twin Framework.
Provides comprehensive digital twin lifecycle management, synchronization tracking,
and performance metrics while maintaining world-class traceability and framework integration.

ENTERPRISE-GRADE FEATURES:
- Advanced digital twin lifecycle management with ML-powered insights
- Automated performance monitoring and optimization for twin operations
- Comprehensive health assessment and alerting for twin pipelines
- Enterprise-grade metrics and analytics for twin operations
- Advanced security and compliance capabilities for twin management
"""

import logging
from typing import List
import asyncio
from ..base_schema import BaseSchema

logger = logging.getLogger(__name__)


class TwinRegistrySchema(BaseSchema):
    """
    Enterprise-Grade Twin Registry Schema Module

    Manages the following tables:
    - twin_registry: Main twin registry and lifecycle management
    - twin_registry_metrics: Performance metrics and analytics
    """

    def __init__(self, connection_manager, schema_name: str = "twin_registry"):
        super().__init__(connection_manager, schema_name)

    def get_module_description(self) -> str:
        """Get human-readable description of this module."""
        return "Digital Twin Registry module with consolidated enterprise features for comprehensive twin lifecycle management, synchronization, relationship tracking, compliance, security, and performance analytics"

    def get_table_names(self) -> List[str]:
        """Get list of table names managed by this module."""
        return ["twin_registry", "twin_registry_metrics"]

    async def initialize(self) -> bool:
        """Initialize the Twin Registry schema with enterprise-grade features."""
        try:
            # Create the Twin Registry tables (following aasx_etl.py pattern)
            if not await self.create_tables():
                return False
            
            # Enterprise metadata tables have been merged into main tables
            # Business logic methods have been moved to repositories
            
            logger.info("✅ Twin Registry Schema initialized with enterprise-grade features")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Twin Registry Schema: {e}")
            return False

    async def create_tables(self) -> bool:
        """Create all Twin Registry tables."""
        try:
            logger.info("🔄 Creating Twin Registry Module Tables...")

            # Create tables in dependency order
            tables_created = []

            # 1. Create Twin Registry Table
            if await self._create_twin_registry_table():
                tables_created.append("twin_registry")
            else:
                logger.error("Failed to create twin_registry table")
                return False

            # 2. Create Twin Registry Metrics Table
            if await self._create_twin_registry_metrics_table():
                tables_created.append("twin_registry_metrics")
            else:
                logger.error("Failed to create twin_registry_metrics table")
                return False

            logger.info(f"✅ Twin Registry Module: Created {len(tables_created)} tables successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create Twin Registry tables: {e}")
            return False

    async def _create_twin_registry_table(self) -> bool:
        """Create the twin registry table with comprehensive twin lifecycle management capabilities."""
        query = """
            CREATE TABLE IF NOT EXISTS twin_registry (
                -- Primary Identification
                registry_id TEXT PRIMARY KEY,                    -- Unique registry identifier
                twin_id TEXT NOT NULL UNIQUE,                    -- Digital twin identifier
                twin_name TEXT NOT NULL,                         -- Human-readable twin name
                registry_name TEXT NOT NULL,                     -- Registry instance name
                
                -- Twin Classification & Metadata
                twin_category TEXT NOT NULL DEFAULT 'generic' CHECK (twin_category IN ('manufacturing', 'energy', 'component', 'facility', 'process', 'generic')),
                twin_type TEXT NOT NULL DEFAULT 'physical' CHECK (twin_type IN ('physical', 'virtual', 'hybrid', 'composite')),
                twin_priority TEXT NOT NULL DEFAULT 'normal' CHECK (twin_priority IN ('low', 'normal', 'high', 'critical', 'emergency')),
                twin_version TEXT NOT NULL DEFAULT '1.0.0',      -- Semantic versioning (major.minor.patch)
                
                -- Workflow Classification (CRITICAL for dual workflow support)
                registry_type TEXT NOT NULL CHECK (registry_type IN ('extraction', 'generation', 'hybrid')),
                workflow_source TEXT NOT NULL CHECK (workflow_source IN ('aasx_file', 'structured_data', 'both')),
                
                -- Module Integration References (Links to other modules - NO data duplication)
                aasx_integration_id TEXT,                        -- Reference to aasx_processing table
                physics_modeling_id TEXT,                        -- Reference to physics_modeling table
                federated_learning_id TEXT,                      -- Reference to federated_learning table
                data_pipeline_id TEXT,                           -- Reference to data_pipeline table
                kg_neo4j_id TEXT,                                -- Reference to knowledge graph module
                certificate_manager_id TEXT,                     -- Reference to certificate module
                
                -- Integration Status & Health
                integration_status TEXT NOT NULL DEFAULT 'pending' CHECK (integration_status IN ('pending', 'active', 'inactive', 'error', 'maintenance', 'deprecated')),
                overall_health_score INTEGER DEFAULT 0 CHECK (overall_health_score >= 0 AND overall_health_score <= 100),
                health_status TEXT NOT NULL DEFAULT 'unknown' CHECK (health_status IN ('unknown', 'healthy', 'warning', 'critical', 'offline')),
                
                -- Lifecycle Management
                lifecycle_status TEXT NOT NULL DEFAULT 'created' CHECK (lifecycle_status IN ('created', 'active', 'suspended', 'archived', 'retired')),
                lifecycle_phase TEXT NOT NULL DEFAULT 'development' CHECK (lifecycle_phase IN ('development', 'testing', 'production', 'maintenance', 'sunset')),
                
                -- Operational Status
                operational_status TEXT NOT NULL DEFAULT 'stopped' CHECK (operational_status IN ('running', 'stopped', 'paused', 'error', 'maintenance')),
                availability_status TEXT NOT NULL DEFAULT 'offline' CHECK (availability_status IN ('online', 'offline', 'degraded', 'maintenance')),
                
                -- Synchronization & Data Management
                sync_status TEXT NOT NULL DEFAULT 'pending' CHECK (sync_status IN ('pending', 'in_progress', 'completed', 'failed', 'scheduled')),
                sync_frequency TEXT NOT NULL DEFAULT 'daily' CHECK (sync_frequency IN ('real_time', 'hourly', 'daily', 'weekly', 'manual')),
                last_sync_at TIMESTAMP,                          -- Last synchronization timestamp
                next_sync_at TIMESTAMP,                          -- Next scheduled synchronization
                sync_error_count INTEGER DEFAULT 0,              -- Count of consecutive sync failures
                sync_error_message TEXT,                         -- Last sync error message
                
                -- Performance & Quality Metrics
                performance_score REAL DEFAULT 0.0,              -- 0.0-1.0 performance rating
                data_quality_score REAL DEFAULT 0.0,             -- 0.0-1.0 data quality rating
                reliability_score REAL DEFAULT 0.0,              -- 0.0-1.0 reliability rating
                compliance_score REAL DEFAULT 0.0,               -- 0.0-1.0 compliance rating
                
                -- Security & Access Control
                security_level TEXT NOT NULL DEFAULT 'internal' CHECK (security_level IN ('public', 'internal', 'confidential', 'secret', 'top_secret')),
                access_control_level TEXT NOT NULL DEFAULT 'user' CHECK (access_control_level IN ('public', 'user', 'admin', 'system', 'restricted')),
                encryption_enabled BOOLEAN DEFAULT FALSE,        -- Whether data is encrypted
                audit_logging_enabled BOOLEAN DEFAULT TRUE,      -- Whether audit logging is enabled
                
                -- Enterprise Compliance & Audit Fields (MERGED)
                compliance_type TEXT DEFAULT 'standard',         -- standard, regulatory, industry, custom
                compliance_status TEXT DEFAULT 'pending',        -- pending, compliant, non_compliant, under_review
                last_audit_date TIMESTAMP,                      -- Last compliance audit date
                next_audit_date TIMESTAMP,                      -- Next scheduled audit date
                audit_details TEXT DEFAULT '{}',                -- JSON: audit findings, recommendations
                
                -- Enterprise Security Fields (MERGED)
                security_event_type TEXT DEFAULT 'none',         -- none, threat_detected, vulnerability, breach
                threat_assessment TEXT DEFAULT 'low',            -- low, medium, high, critical
                last_security_scan TIMESTAMP,                   -- Last security scan timestamp
                security_details TEXT DEFAULT '{}',              -- JSON: security events, threat details
                security_trend TEXT DEFAULT 'stable',            -- improving, stable, degrading, critical
                
                -- Enterprise Performance Analytics Fields (MERGED)
                performance_trend TEXT DEFAULT 'stable',         -- improving, stable, degrading
                optimization_suggestions TEXT DEFAULT '{}',      -- JSON object of optimization recommendations
                last_optimization_date TIMESTAMP,                -- Last optimization performed
                enterprise_metrics TEXT DEFAULT '{}',            -- JSON: enterprise-level metrics
                
                -- User Management & Ownership
                user_id TEXT NOT NULL,                           -- Current user who owns/accesses this registry
                org_id TEXT NOT NULL,                            -- Organization this registry belongs to
                dept_id TEXT,                                    -- Department for complete traceability
                owner_team TEXT,                                 -- Team responsible for this twin
                steward_user_id TEXT,                            -- Data steward for this twin
                
                -- Timestamps & Audit (TIMESTAMP for better analytics)
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                activated_at TIMESTAMP,                          -- When twin was first activated
                last_accessed_at TIMESTAMP,                      -- Last time any user accessed this twin
                last_modified_at TIMESTAMP,                      -- Last time twin data was modified
                
                -- Configuration & Metadata (JSON fields for flexibility)
                registry_config TEXT DEFAULT '{}',               -- Registry configuration settings
                registry_metadata TEXT DEFAULT '{}',              -- Additional metadata
                custom_attributes TEXT DEFAULT '{}',              -- User-defined custom attributes
                tags TEXT DEFAULT '{}',                          -- JSON object of tags for categorization
                
                -- Relationships & Dependencies (JSON objects)
                relationships TEXT DEFAULT '{}',                  -- JSON object of relationship objects
                dependencies TEXT DEFAULT '{}',                   -- JSON object of dependency objects
                instances TEXT DEFAULT '{}'                      -- JSON object of instance objects
                
                -- Foreign Key Constraints (Commented out for testing - enable in production)
                -- FOREIGN KEY (aasx_integration_id) REFERENCES aasx_processing(job_id) ON DELETE SET NULL,
                -- FOREIGN KEY (physics_modeling_id) REFERENCES physics_modeling_registry(registry_id) ON DELETE SET NULL,
                -- FOREIGN KEY (federated_learning_id) REFERENCES federated_learning_registry(registry_id) ON DELETE SET NULL,
                -- FOREIGN KEY (data_pipeline_id) REFERENCES data_pipeline_registry(registry_id) ON DELETE SET NULL,
                -- FOREIGN KEY (kg_neo4j_id) REFERENCES kg_graph_registry(graph_id) ON DELETE SET NULL,
                -- FOREIGN KEY (certificate_manager_id) REFERENCES certificate_manager_registry(registry_id) ON DELETE SET NULL,
                -- FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                -- FOREIGN KEY (org_id) REFERENCES organizations(org_id) ON DELETE CASCADE,
                -- FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE SET NULL,
                -- FOREIGN KEY (steward_user_id) REFERENCES users(user_id) ON DELETE SET NULL
            )
        """

        # Create the table using connection manager
        await self.connection_manager.execute_query(query)

        # Create indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_twin_id ON twin_registry (twin_id)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_user_id ON twin_registry (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_org_id ON twin_registry (org_id)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_dept_id ON twin_registry (dept_id)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_category ON twin_registry (twin_category)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_type ON twin_registry (twin_type)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_priority ON twin_registry (twin_priority)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_registry_type ON twin_registry (registry_type)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_workflow_source ON twin_registry (workflow_source)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_status ON twin_registry (integration_status)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_health ON twin_registry (health_status)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_lifecycle ON twin_registry (lifecycle_status)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_operational ON twin_registry (operational_status)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_sync ON twin_registry (sync_status, sync_frequency)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_created ON twin_registry (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_updated ON twin_registry (updated_at)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_integration ON twin_registry (aasx_integration_id, physics_modeling_id, kg_neo4j_id)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_performance ON twin_registry (performance_score, data_quality_score, reliability_score)",
            # Enterprise field indexes (MERGED)
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_compliance ON twin_registry (compliance_type, compliance_status, compliance_score)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_security ON twin_registry (security_event_type, threat_assessment, security_trend)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_enterprise ON twin_registry (performance_trend, last_optimization_date)"
        ]

        # Create indexes using BaseSchema method
        return await self.create_indexes("twin_registry", index_queries)

    async def _create_twin_registry_metrics_table(self) -> bool:
        """Create the twin registry metrics table with comprehensive performance monitoring."""
        query = """
            CREATE TABLE IF NOT EXISTS twin_registry_metrics (
                -- Primary Identification
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                registry_id TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                
                -- Real-time Health Metrics (Framework Health)
                health_score INTEGER CHECK (health_score >= 0 AND health_score <= 100),
                response_time_ms REAL,
                uptime_percentage REAL CHECK (uptime_percentage >= 0.0 AND uptime_percentage <= 100.0),
                error_rate REAL CHECK (error_rate >= 0.0 AND error_rate <= 1.0),
                
                -- Twin Registry Performance Metrics (Framework Performance - NOT Data)
                twin_sync_speed_sec REAL, -- Time to synchronize twin data
                relationship_update_speed_sec REAL, -- Time to update twin relationships
                lifecycle_transition_speed_sec REAL, -- Time for lifecycle state changes
                twin_registry_efficiency REAL CHECK (twin_registry_efficiency >= 0.0 AND twin_registry_efficiency <= 1.0),
                
                -- Twin Management Performance (JSON for better framework analysis)
                twin_management_performance TEXT DEFAULT '{}', -- JSON: {
                                                                 --   "twin_creation": {"usage_count": 150, "avg_processing_time": 2.3, "success_rate": 0.98, "last_used": "2024-01-15T10:30:00Z"},
                                                                 --   "twin_sync": {"usage_count": 300, "avg_processing_time": 1.8, "success_rate": 0.96, "last_used": "2024-01-15T10:15:00Z"},
                                                                 --   "relationship_management": {"usage_count": 200, "avg_processing_time": 3.1, "success_rate": 0.94, "last_used": "2024-01-15T10:00:00Z"},
                                                                 --   "lifecycle_management": {"usage_count": 100, "avg_processing_time": 4.2, "success_rate": 0.92, "last_used": "2024-01-15T09:45:00Z"},
                                                                 --   "instance_management": {"usage_count": 120, "avg_processing_time": 2.8, "success_rate": 0.95, "last_used": "2024-01-15T09:30:00Z"}
                                                                 -- }
                
                -- Twin Category Performance Metrics (JSON for better framework analysis)
                twin_category_performance_stats TEXT DEFAULT '{}', -- JSON: {
                                                                   --   "manufacturing": {"twins": 250, "active": 245, "inactive": 5, "avg_sync_time": 2.1, "health_distribution": {"healthy": 200, "warning": 35, "critical": 10}},
                                                                   --   "energy": {"twins": 180, "active": 175, "inactive": 5, "avg_sync_time": 3.2, "health_distribution": {"healthy": 150, "warning": 20, "critical": 10}},
                                                                   --   "component": {"twins": 320, "active": 315, "inactive": 5, "avg_sync_time": 1.5, "health_distribution": {"healthy": 280, "warning": 30, "critical": 10}},
                                                                   --   "facility": {"twins": 95, "active": 90, "inactive": 5, "avg_sync_time": 4.8, "health_distribution": {"healthy": 75, "warning": 15, "critical": 5}},
                                                                   --   "process": {"twins": 140, "active": 135, "inactive": 5, "avg_sync_time": 2.9, "health_distribution": {"healthy": 120, "warning": 10, "critical": 5}},
                                                                   --   "generic": {"twins": 75, "active": 70, "inactive": 5, "avg_sync_time": 2.3, "health_distribution": {"healthy": 65, "warning": 5, "critical": 0}}
                                                                   -- }
                
                -- User Interaction Metrics (Framework Usage - NOT Content)
                user_interaction_count INTEGER DEFAULT 0, -- Number of user interactions
                twin_access_count INTEGER DEFAULT 0, -- Number of twin accesses
                successful_twin_operations INTEGER DEFAULT 0, -- Successful operations
                failed_twin_operations INTEGER DEFAULT 0, -- Failed operations
                
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
                
                -- Twin Registry Patterns & Analytics (Framework Trends - JSON)
                twin_registry_patterns TEXT DEFAULT '{}', -- JSON: hourly, daily, weekly, monthly patterns
                resource_utilization_trends TEXT DEFAULT '{}', -- JSON: {"cpu_trend": [...], "memory_trend": [...], "disk_trend": [...]}
                user_activity TEXT DEFAULT '{}', -- JSON: {"peak_hours": [...], "user_patterns": {...}, "session_durations": [...]}
                twin_operation_patterns TEXT DEFAULT '{}', -- JSON: {"operation_types": {...}, "complexity_distribution": {...}, "processing_times": [...]}
                compliance_status TEXT DEFAULT '{}', -- JSON: {"compliance_score": 0.95, "audit_status": "passed", "last_audit": "2024-01-15T00:00:00Z"}
                security_events TEXT DEFAULT '{}', -- JSON: {"events": [...], "threat_level": "low", "last_security_scan": "2024-01-15T00:00:00Z"}
                
                -- Twin Registry-Specific Metrics (Framework Capabilities - JSON)
                twin_registry_analytics TEXT DEFAULT '{}', -- JSON: {"sync_quality": 0.94, "relationship_quality": 0.92, "lifecycle_quality": 0.96}
                category_effectiveness TEXT DEFAULT '{}', -- JSON: {"category_comparison": {...}, "best_performing": "component", "optimization_suggestions": [...]}
                workflow_performance TEXT DEFAULT '{}', -- JSON: {"extraction_performance": {...}, "generation_performance": {...}, "hybrid_performance": {...}}
                twin_size_performance_efficiency TEXT DEFAULT '{}', -- JSON: {"performance_by_twin_size": {...}, "quality_by_twin_size": {...}, "optimization_opportunities": [...]}
                
                -- Time-based Analytics (Framework Time Analysis)
                hour_of_day INTEGER CHECK (hour_of_day >= 0 AND hour_of_day <= 23),
                day_of_week INTEGER CHECK (day_of_week >= 1 AND day_of_week <= 7),
                month INTEGER CHECK (month >= 1 AND month <= 12),
                
                -- Performance Trends (Framework Performance Analysis)
                twin_management_trend REAL, -- Compared to historical average
                resource_efficiency_trend REAL, -- Performance over time
                quality_trend REAL, -- Quality metrics over time
                
                -- Enterprise Compliance Metrics (MERGED)
                enterprise_compliance_score REAL DEFAULT 0.0,              -- Enterprise-wide compliance rating
                compliance_audit_status TEXT DEFAULT 'pending',            -- pending, passed, failed, under_review
                compliance_violations_count INTEGER DEFAULT 0,             -- Number of compliance violations
                compliance_corrective_actions TEXT DEFAULT '{}',           -- JSON object of corrective actions
                
                -- Enterprise Security Metrics (MERGED)
                enterprise_security_score REAL DEFAULT 0.0,                -- Enterprise-wide security rating
                security_threat_level TEXT DEFAULT 'low',                  -- low, medium, high, critical
                security_vulnerabilities_count INTEGER DEFAULT 0,          -- Number of security vulnerabilities
                security_incident_response_time REAL,                      -- Average incident response time
                security_scan_frequency TEXT DEFAULT 'weekly',             -- daily, weekly, monthly, quarterly
                
                -- Enterprise Performance Analytics (MERGED)
                enterprise_performance_score REAL DEFAULT 0.0,             -- Enterprise-wide performance rating
                performance_optimization_status TEXT DEFAULT 'none',       -- none, scheduled, in_progress, completed
                resource_optimization_efficiency REAL DEFAULT 0.0,         -- 0.0-1.0 optimization efficiency
                enterprise_analytics_metadata TEXT DEFAULT '{}',           -- JSON: enterprise analytics data
                
                -- Multi-Tenant Support (REQUIRED for RBAC)
                user_id TEXT NOT NULL,                                    -- User ID for access control
                org_id TEXT NOT NULL,                                     -- Organization ID for multi-tenant isolation
                dept_id TEXT NOT NULL,                                    -- Department ID for department-level access control
                
                -- Timestamps
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,            -- Creation timestamp
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,            -- Last update timestamp
                
                -- Foreign Key Constraints
                FOREIGN KEY (registry_id) REFERENCES twin_registry (registry_id) ON DELETE CASCADE
            )
        """

        # Create the table using connection manager
        await self.connection_manager.execute_query(query)

        # Create indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_metrics_registry_id ON twin_registry_metrics (registry_id)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_metrics_timestamp ON twin_registry_metrics (timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_metrics_health ON twin_registry_metrics (health_score)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_metrics_performance ON twin_registry_metrics (twin_sync_speed_sec, relationship_update_speed_sec, lifecycle_transition_speed_sec)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_metrics_quality ON twin_registry_metrics (data_freshness_score, data_completeness_score)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_metrics_resources ON twin_registry_metrics (cpu_usage_percent, memory_usage_percent, disk_io_mb)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_metrics_user_activity ON twin_registry_metrics (user_interaction_count, twin_access_count)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_metrics_time_analysis ON twin_registry_metrics (hour_of_day, day_of_week, month)",
            # Enterprise field indexes (MERGED)
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_metrics_enterprise_compliance ON twin_registry_metrics (enterprise_compliance_score, compliance_audit_status, compliance_violations_count)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_metrics_enterprise_security ON twin_registry_metrics (enterprise_security_score, security_threat_level, security_vulnerabilities_count)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_metrics_enterprise_performance ON twin_registry_metrics (enterprise_performance_score, performance_optimization_status, resource_optimization_efficiency)"
        ]

        # Create indexes using BaseSchema method
        return await self.create_indexes("twin_registry_metrics", index_queries)

    