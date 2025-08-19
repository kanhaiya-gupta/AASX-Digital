"""
Core System Schema Module
=========================

Manages Core System database tables for the AASX Digital Twin Framework.
Provides comprehensive user management, organization management, project management,
and file management while maintaining world-class traceability and framework integration.
"""

import logging
from typing import List, Dict, Any
from ..base_schema import BaseSchemaModule

logger = logging.getLogger(__name__)


class CoreSystemSchema(BaseSchemaModule):
    """
    Core System Schema Module

    Manages the following tables:
    - core_system_registry: Main core system registry and lifecycle management
    - core_system_metrics: Performance metrics and analytics
    """

    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.module_name = "core_system"

    def get_module_description(self) -> str:
        """Get human-readable description of this module."""
        return "Core System module for comprehensive user, organization, project, and file lifecycle management"

    def get_table_names(self) -> List[str]:
        """Get list of table names managed by this module."""
        return ["core_system_registry", "core_system_metrics"]

    def create_tables(self) -> bool:
        """
        Create all Core System tables.

        Returns:
            bool: True if all tables created successfully, False otherwise
        """
        logger.info("🔧 Creating Core System Module Tables...")

        # Create tables in dependency order
        tables_created = []

        # 1. Create Core System Registry Table
        if self._create_core_system_registry_table():
            tables_created.append("core_system_registry")
        else:
            logger.error("Failed to create core_system_registry table")
            return False

        # 2. Create Core System Metrics Table
        if self._create_core_system_metrics_table():
            tables_created.append("core_system_metrics")
        else:
            logger.error("Failed to create core_system_metrics table")
            return False

        logger.info(f"✅ Core System Module: Created {len(tables_created)} tables successfully")
        return True

    def _create_core_system_registry_table(self) -> bool:
        """Create the core system registry table with comprehensive system lifecycle management capabilities."""
        query = """
            CREATE TABLE IF NOT EXISTS core_system_registry (
                -- Primary Identification
                registry_id TEXT PRIMARY KEY,                        -- Unique registry identifier
                system_name TEXT NOT NULL,                          -- System component name
                registry_name TEXT NOT NULL,                        -- Registry instance name
                
                -- System Classification & Metadata
                system_category TEXT NOT NULL DEFAULT 'foundation'  -- foundation, user_management, organization, project, file
                    CHECK (system_category IN ('foundation', 'user_management', 'organization', 'project', 'file')),
                system_type TEXT NOT NULL DEFAULT 'core_service'    -- core_service, management_service, storage_service, auth_service
                    CHECK (system_type IN ('core_service', 'management_service', 'storage_service', 'auth_service')),
                system_priority TEXT NOT NULL DEFAULT 'critical'    -- low, normal, high, critical, emergency
                    CHECK (system_priority IN ('low', 'normal', 'high', 'critical', 'emergency')),
                system_version TEXT NOT NULL DEFAULT '1.0.0',       -- Semantic versioning (major.minor.patch)
                
                -- Workflow Classification (CRITICAL for dual workflow support)
                registry_type TEXT NOT NULL                        -- extraction, generation, hybrid
                    CHECK (registry_type IN ('extraction', 'generation', 'hybrid')),
                workflow_source TEXT NOT NULL                      -- aasx_file, structured_data, both
                    CHECK (workflow_source IN ('aasx_file', 'structured_data', 'both')),
                
                -- Module Integration References (Links to other modules - NO data duplication)
                aasx_integration_id TEXT,                          -- Reference to aasx_processing table
                twin_registry_id TEXT,                             -- Reference to twin_registry table
                kg_neo4j_id TEXT,                                  -- Reference to kg_graph_registry table
                physics_modeling_id TEXT,                          -- Reference to physics_modeling table
                federated_learning_id TEXT,                        -- Reference to federated_learning table
                certificate_manager_id TEXT,                       -- Reference to certificate module
                
                -- Integration Status & Health
                integration_status TEXT NOT NULL DEFAULT 'pending' -- pending, active, inactive, error, maintenance, deprecated
                    CHECK (integration_status IN ('pending', 'active', 'inactive', 'error', 'maintenance', 'deprecated')),
                overall_health_score INTEGER DEFAULT 0             -- 0-100 health score across all modules
                    CHECK (overall_health_score >= 0 AND overall_health_score <= 100),
                health_status TEXT NOT NULL DEFAULT 'unknown'      -- unknown, healthy, warning, critical, offline
                    CHECK (health_status IN ('unknown', 'healthy', 'warning', 'critical', 'offline')),
                
                -- Lifecycle Management
                lifecycle_status TEXT NOT NULL DEFAULT 'created'   -- created, active, suspended, archived, retired
                    CHECK (lifecycle_status IN ('created', 'active', 'suspended', 'archived', 'retired')),
                lifecycle_phase TEXT NOT NULL DEFAULT 'development' -- development, testing, production, maintenance, sunset
                    CHECK (lifecycle_phase IN ('development', 'testing', 'production', 'maintenance', 'sunset')),
                
                -- Operational Status
                operational_status TEXT NOT NULL DEFAULT 'stopped' -- running, stopped, paused, error, maintenance
                    CHECK (operational_status IN ('running', 'stopped', 'paused', 'error', 'maintenance')),
                availability_status TEXT NOT NULL DEFAULT 'offline' -- online, offline, degraded, maintenance
                    CHECK (availability_status IN ('online', 'offline', 'degraded', 'maintenance')),
                
                -- Core System-Specific Status (NEW for Core System)
                user_management_status TEXT DEFAULT 'pending'      -- pending, in_progress, completed, failed, scheduled
                    CHECK (user_management_status IN ('pending', 'in_progress', 'completed', 'failed', 'scheduled')),
                organization_management_status TEXT DEFAULT 'pending' -- pending, in_progress, completed, failed, scheduled
                    CHECK (organization_management_status IN ('pending', 'in_progress', 'completed', 'failed', 'scheduled')),
                project_management_status TEXT DEFAULT 'pending'   -- pending, in_progress, completed, failed, scheduled
                    CHECK (project_management_status IN ('pending', 'in_progress', 'completed', 'failed', 'scheduled')),
                file_management_status TEXT DEFAULT 'pending'      -- pending, in_progress, completed, failed, scheduled
                    CHECK (file_management_status IN ('pending', 'in_progress', 'completed', 'failed', 'scheduled')),
                last_core_sync_at TEXT,                            -- Last core system synchronization timestamp
                next_core_sync_at TEXT,                            -- Next scheduled core system synchronization
                core_sync_error_count INTEGER DEFAULT 0,            -- Count of consecutive core sync failures
                core_sync_error_message TEXT,                      -- Last core sync error message
                
                -- Core System Data Metrics (NEW for Core System)
                total_users INTEGER DEFAULT 0,                     -- Total number of users in the system
                total_organizations INTEGER DEFAULT 0,             -- Total number of organizations
                total_projects INTEGER DEFAULT 0,                  -- Total number of projects
                total_files INTEGER DEFAULT 0,                     -- Total number of files
                system_complexity TEXT DEFAULT 'simple'            -- simple, moderate, complex, very_complex
                    CHECK (system_complexity IN ('simple', 'moderate', 'complex', 'very_complex')),
                
                -- Performance & Quality Metrics
                performance_score REAL DEFAULT 0.0,                -- 0.0-1.0 performance rating
                data_quality_score REAL DEFAULT 0.0,               -- 0.0-1.0 data quality rating
                reliability_score REAL DEFAULT 0.0,                -- 0.0-1.0 reliability rating
                compliance_score REAL DEFAULT 0.0,                 -- 0.0-1.0 compliance rating
                
                -- Security & Access Control
                security_level TEXT NOT NULL DEFAULT 'standard'    -- public, internal, confidential, secret, top_secret
                    CHECK (security_level IN ('public', 'internal', 'confidential', 'secret', 'top_secret')),
                access_control_level TEXT NOT NULL DEFAULT 'user'  -- public, user, admin, system, restricted
                    CHECK (access_control_level IN ('public', 'user', 'admin', 'system', 'restricted')),
                encryption_enabled BOOLEAN DEFAULT FALSE,           -- Whether system data is encrypted
                audit_logging_enabled BOOLEAN DEFAULT TRUE,         -- Whether audit logging is enabled
                
                -- User Management & Ownership
                user_id TEXT NOT NULL,                             -- Current user who owns/accesses this registry
                org_id TEXT NOT NULL,                              -- Organization this registry belongs to
                owner_team TEXT,                                   -- Team responsible for this system
                steward_user_id TEXT,                              -- Data steward for this system
                
                -- Timestamps & Audit
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                activated_at TEXT,                                 -- When system was first activated
                last_accessed_at TEXT,                             -- Last time any user accessed this system
                last_modified_at TEXT,                             -- Last time system data was modified
                
                -- Configuration & Metadata (JSON fields for flexibility)
                registry_config TEXT DEFAULT '{}',                 -- Registry configuration settings
                registry_metadata TEXT DEFAULT '{}',                -- Additional metadata
                custom_attributes TEXT DEFAULT '{}',                -- User-defined custom attributes
                tags TEXT DEFAULT '[]',                            -- JSON array of tags for categorization
                
                -- Relationships & Dependencies (JSON arrays)
                relationships TEXT DEFAULT '[]',                    -- Array of relationship objects
                dependencies TEXT DEFAULT '[]',                     -- Array of dependency objects
                system_instances TEXT DEFAULT '[]',                 -- Array of system instance objects
                
                -- Constraints
                FOREIGN KEY (aasx_integration_id) REFERENCES aasx_processing(job_id) ON DELETE SET NULL,
                FOREIGN KEY (twin_registry_id) REFERENCES twin_registry(registry_id) ON DELETE SET NULL,
                FOREIGN KEY (kg_neo4j_id) REFERENCES kg_graph_registry(graph_id) ON DELETE SET NULL
            )
        """

        # Create the table
        if not self.create_table("core_system_registry", query):
            return False

        # Create indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_core_system_registry_user_id ON core_system_registry (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_core_system_registry_org_id ON core_system_registry (org_id)",
            "CREATE INDEX IF NOT EXISTS idx_core_system_registry_category ON core_system_registry (system_category)",
            "CREATE INDEX IF NOT EXISTS idx_core_system_registry_type ON core_system_registry (system_type)",
            "CREATE INDEX IF NOT EXISTS idx_core_system_registry_priority ON core_system_registry (system_priority)",
            "CREATE INDEX IF NOT EXISTS idx_core_system_registry_registry_type ON core_system_registry (registry_type)",
            "CREATE INDEX IF NOT EXISTS idx_core_system_registry_workflow_source ON core_system_registry (workflow_source)",
            "CREATE INDEX IF NOT EXISTS idx_core_system_registry_status ON core_system_registry (integration_status)",
            "CREATE INDEX IF NOT EXISTS idx_core_system_registry_health ON core_system_registry (health_status)",
            "CREATE INDEX IF NOT EXISTS idx_core_system_registry_lifecycle ON core_system_registry (lifecycle_status)",
            "CREATE INDEX IF NOT EXISTS idx_core_system_registry_operational ON core_system_registry (operational_status)",
            "CREATE INDEX IF NOT EXISTS idx_core_system_registry_core ON core_system_registry (user_management_status, organization_management_status, project_management_status, file_management_status)",
            "CREATE INDEX IF NOT EXISTS idx_core_system_registry_complexity ON core_system_registry (system_complexity)",
            "CREATE INDEX IF NOT EXISTS idx_core_system_registry_created ON core_system_registry (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_core_system_registry_updated ON core_system_registry (updated_at)",
            "CREATE INDEX IF NOT EXISTS idx_core_system_registry_integration ON core_system_registry (aasx_integration_id, twin_registry_id, kg_neo4j_id, physics_modeling_id)",
            "CREATE INDEX IF NOT EXISTS idx_core_system_registry_performance ON core_system_registry (performance_score, data_quality_score, reliability_score)"
        ]

        return self.create_indexes("core_system_registry", index_queries)

    def _create_core_system_metrics_table(self) -> bool:
        """Create the core system metrics table with comprehensive performance monitoring."""
        query = """
            CREATE TABLE IF NOT EXISTS core_system_metrics (
                -- Primary Identification
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                registry_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                
                -- Real-time Health Metrics (Framework Health)
                health_score INTEGER CHECK (health_score >= 0 AND health_score <= 100),
                response_time_ms REAL,
                uptime_percentage REAL CHECK (uptime_percentage >= 0.0 AND uptime_percentage <= 100.0),
                error_rate REAL CHECK (error_rate >= 0.0 AND error_rate <= 1.0),
                
                -- Core System Performance Metrics (Framework Performance - NOT Data)
                user_management_speed_sec REAL, -- Time to manage user operations
                organization_management_speed_sec REAL, -- Time to manage organization operations
                project_management_speed_sec REAL, -- Time to manage project operations
                file_management_speed_sec REAL, -- Time to manage file operations
                core_system_efficiency REAL CHECK (core_system_efficiency >= 0.0 AND core_system_efficiency <= 1.0),
                
                -- Core System Management Performance (JSON for better framework analysis)
                core_system_performance TEXT DEFAULT '{}', -- JSON: {
                                                                  --   "user_management": {"usage_count": 500, "avg_processing_time": 0.8, "success_rate": 0.99, "last_used": "2024-01-15T10:30:00Z"},
                                                                  --   "organization_management": {"usage_count": 200, "avg_processing_time": 1.2, "success_rate": 0.98, "last_used": "2024-01-15T10:15:00Z"},
                                                                  --   "project_management": {"usage_count": 800, "avg_processing_time": 1.5, "success_rate": 0.97, "last_used": "2024-01-15T10:00:00Z"},
                                                                  --   "file_management": {"usage_count": 1200, "avg_processing_time": 2.1, "success_rate": 0.96, "last_used": "2024-01-15T09:45:00Z"},
                                                                  --   "system_administration": {"usage_count": 150, "avg_processing_time": 3.2, "success_rate": 0.95, "last_used": "2024-01-15T09:30:00Z"}
                                                                  -- }
                
                -- Core System Category Performance Metrics (JSON for better framework analysis)
                core_system_category_performance_stats TEXT DEFAULT '{}', -- JSON: {
                                                                          --   "foundation": {"systems": 50, "active": 48, "inactive": 2, "avg_response_time": 0.5, "health_distribution": {"healthy": 45, "warning": 3, "critical": 0}},
                                                                          --   "user_management": {"systems": 25, "active": 24, "inactive": 1, "avg_response_time": 0.8, "health_distribution": {"healthy": 22, "warning": 2, "critical": 0}},
                                                                          --   "organization": {"systems": 30, "active": 29, "inactive": 1, "avg_response_time": 1.2, "health_distribution": {"healthy": 27, "warning": 2, "critical": 0}},
                                                                          --   "project": {"systems": 40, "active": 38, "inactive": 2, "avg_response_time": 1.5, "health_distribution": {"healthy": 35, "warning": 3, "critical": 0}},
                                                                          --   "file": {"systems": 35, "active": 33, "inactive": 2, "avg_response_time": 2.1, "health_distribution": {"healthy": 30, "warning": 3, "critical": 0}}
                                                                          -- }
                
                -- User Interaction Metrics (Framework Usage - NOT Content)
                user_interaction_count INTEGER DEFAULT 0, -- Number of user interactions
                system_access_count INTEGER DEFAULT 0, -- Number of system accesses
                successful_system_operations INTEGER DEFAULT 0, -- Successful operations
                failed_system_operations INTEGER DEFAULT 0, -- Failed operations
                
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
                
                -- Core System Patterns & Analytics (Framework Trends - JSON)
                core_system_patterns TEXT DEFAULT '{}', -- JSON: {"hourly": {...}, "daily": {...}, "weekly": {...}, "monthly": {...}}
                resource_utilization_trends TEXT DEFAULT '{}', -- JSON: {"cpu_trend": [...], "memory_trend": [...], "disk_trend": [...]}
                user_activity TEXT DEFAULT '{}', -- JSON: {"peak_hours": [...], "user_patterns": {...}, "session_durations": [...]}
                system_operation_patterns TEXT DEFAULT '{}', -- JSON: {"operation_types": {...}, "complexity_distribution": {...}, "processing_times": [...]}
                compliance_status TEXT DEFAULT '{}', -- JSON: {"compliance_score": 0.95, "audit_status": "passed", "last_audit": "2024-01-15T00:00:00Z"}
                security_events TEXT DEFAULT '{}', -- JSON: {"events": [...], "threat_level": "low", "last_security_scan": "2024-01-15T00:00:00Z"}
                
                -- Core System-Specific Metrics (Framework Capabilities - JSON)
                core_system_analytics TEXT DEFAULT '{}', -- JSON: {"management_quality": 0.94, "administration_quality": 0.92, "system_quality": 0.96}
                category_effectiveness TEXT DEFAULT '{}', -- JSON: {"category_comparison": {...}, "best_performing": "foundation", "optimization_suggestions": [...]}
                workflow_performance TEXT DEFAULT '{}', -- JSON: {"extraction_performance": {...}, "generation_performance": {...}, "hybrid_performance": {...}}
                system_size_performance_efficiency TEXT DEFAULT '{}', -- JSON: {"performance_by_system_size": {...}, "quality_by_system_size": {...}, "optimization_opportunities": [...]}
                
                -- Time-based Analytics (Framework Time Analysis)
                hour_of_day INTEGER CHECK (hour_of_day >= 0 AND hour_of_day <= 23),
                day_of_week INTEGER CHECK (day_of_week >= 1 AND day_of_week <= 7),
                month INTEGER CHECK (month >= 1 AND month <= 12),
                
                -- Performance Trends (Framework Performance Analysis)
                system_management_trend REAL, -- Compared to historical average
                resource_efficiency_trend REAL, -- Performance over time
                quality_trend REAL, -- Quality metrics over time
                
                -- Foreign Key Constraints
                FOREIGN KEY (registry_id) REFERENCES core_system_registry (registry_id) ON DELETE CASCADE
            )
        """

        # Create the table
        if not self.create_table("core_system_metrics", query):
            return False

        # Create indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_core_system_metrics_registry_id ON core_system_metrics (registry_id)",
            "CREATE INDEX IF NOT EXISTS idx_core_system_metrics_timestamp ON core_system_metrics (timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_core_system_metrics_health ON core_system_metrics (health_score)",
            "CREATE INDEX IF NOT EXISTS idx_core_system_metrics_performance ON core_system_metrics (user_management_speed_sec, organization_management_speed_sec, project_management_speed_sec, file_management_speed_sec)",
            "CREATE INDEX IF NOT EXISTS idx_core_system_metrics_quality ON core_system_metrics (data_freshness_score, data_completeness_score)",
            "CREATE INDEX IF NOT EXISTS idx_core_system_metrics_resources ON core_system_metrics (cpu_usage_percent, memory_usage_percent, disk_io_mb)",
            "CREATE INDEX IF NOT EXISTS idx_core_system_metrics_user_activity ON core_system_metrics (user_interaction_count, system_access_count)",
            "CREATE INDEX IF NOT EXISTS idx_core_system_metrics_core ON core_system_metrics (core_system_performance)",
            "CREATE INDEX IF NOT EXISTS idx_core_system_metrics_category ON core_system_metrics (core_system_category_performance_stats)",
            "CREATE INDEX IF NOT EXISTS idx_core_system_metrics_time_analysis ON core_system_metrics (hour_of_day, day_of_week, month)"
        ]

        return self.create_indexes("core_system_metrics", index_queries)
