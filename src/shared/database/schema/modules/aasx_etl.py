"""
AASX ETL Schema Module
======================

Manages AASX ETL database tables for the AASX Digital Twin Framework.
Provides comprehensive tracking of AASX processing jobs, extraction/generation operations,
and performance metrics while maintaining world-class traceability and framework integration.
"""

import logging
from typing import List, Dict, Any
from ..base_schema import BaseSchemaModule

logger = logging.getLogger(__name__)


class AasxEtlSchema(BaseSchemaModule):
    """
    AASX ETL Schema Module

    Manages the following tables:
    - aasx_processing: Main AASX processing registry and job tracking
    - aasx_processing_metrics: Performance metrics and analytics
    """

    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.module_name = "aasx_etl"

    def get_module_description(self) -> str:
        """Get human-readable description of this module."""
        return "AASX Extraction, Transformation, and Loading (ETL) module for comprehensive job tracking and processing management"

    def get_table_names(self) -> List[str]:
        """Get list of table names managed by this module."""
        return ["aasx_processing", "aasx_processing_metrics"]

    def create_tables(self) -> bool:
        """
        Create all AASX ETL tables.

        Returns:
            bool: True if all tables created successfully, False otherwise
        """
        logger.info("📦 Creating AASX ETL Module Tables...")

        # Create tables in dependency order
        tables_created = []

        # 1. Create AASX Processing Table
        if self._create_aasx_processing_table():
            tables_created.append("aasx_processing")
        else:
            logger.error("Failed to create aasx_processing table")
            return False

        # 2. Create AASX Processing Metrics Table
        if self._create_aasx_processing_metrics_table():
            tables_created.append("aasx_processing_metrics")
        else:
            logger.error("Failed to create aasx_processing_metrics table")
            return False

        logger.info(f"✅ AASX ETL Module: Created {len(tables_created)} tables successfully")
        return True

    def _create_aasx_processing_table(self) -> bool:
        """Create the AASX processing table with comprehensive job tracking capabilities."""
        query = """
            CREATE TABLE IF NOT EXISTS aasx_processing (
                -- Primary Identification
                job_id TEXT PRIMARY KEY,
                file_id TEXT NOT NULL,
                project_id TEXT NOT NULL,
                
                -- Job Classification & Metadata
                job_type TEXT NOT NULL CHECK (job_type IN ('extraction', 'generation')),
                source_type TEXT NOT NULL CHECK (source_type IN ('manual_upload', 'url_upload', 'api_upload', 'batch_upload')),
                processing_status TEXT NOT NULL CHECK (processing_status IN ('pending', 'in_progress', 'completed', 'failed', 'cancelled', 'retrying')),
                processing_priority TEXT DEFAULT 'normal' CHECK (processing_priority IN ('low', 'normal', 'high', 'critical')),
                job_version TEXT DEFAULT '1.0.0',
                
                -- Workflow Classification
                workflow_type TEXT DEFAULT 'standard' CHECK (workflow_type IN ('standard', 'batch', 'streaming', 'real_time', 'scheduled')),
                processing_mode TEXT DEFAULT 'synchronous' CHECK (processing_mode IN ('synchronous', 'asynchronous', 'batch', 'streaming')),
                
                -- Module Integration References (Framework Integration)
                twin_registry_id TEXT,
                kg_neo4j_id TEXT,
                ai_rag_id TEXT,
                physics_modeling_id TEXT,
                federated_learning_id TEXT,
                certificate_manager_id TEXT,
                
                -- Integration Status & Health (Framework Health)
                integration_status TEXT DEFAULT 'pending' CHECK (integration_status IN ('pending', 'active', 'inactive', 'error', 'maintenance', 'deprecated')),
                overall_health_score INTEGER DEFAULT 0 CHECK (overall_health_score >= 0 AND overall_health_score <= 100),
                health_status TEXT DEFAULT 'unknown' CHECK (health_status IN ('unknown', 'healthy', 'warning', 'critical', 'offline')),
                
                -- Lifecycle Management (Framework Lifecycle)
                lifecycle_status TEXT DEFAULT 'created' CHECK (lifecycle_status IN ('created', 'active', 'suspended', 'archived', 'retired')),
                lifecycle_phase TEXT DEFAULT 'development' CHECK (lifecycle_phase IN ('development', 'testing', 'production', 'maintenance', 'sunset')),
                
                -- Operational Status (Framework Operations)
                operational_status TEXT DEFAULT 'stopped' CHECK (operational_status IN ('running', 'stopped', 'paused', 'error', 'maintenance')),
                availability_status TEXT DEFAULT 'offline' CHECK (availability_status IN ('online', 'offline', 'degraded', 'maintenance')),
                
                -- AASX-Specific Processing Status (Framework Processing Points)
                extraction_status TEXT DEFAULT 'pending' CHECK (extraction_status IN ('pending', 'in_progress', 'completed', 'failed', 'scheduled')),
                generation_status TEXT DEFAULT 'pending' CHECK (generation_status IN ('pending', 'in_progress', 'completed', 'failed', 'scheduled')),
                validation_status TEXT DEFAULT 'pending' CHECK (validation_status IN ('pending', 'in_progress', 'completed', 'failed', 'scheduled')),
                last_extraction_at TEXT,
                last_generation_at TEXT,
                last_validation_at TEXT,
                
                -- Processing Configuration (Framework Configuration - NOT Raw Data)
                extraction_options TEXT DEFAULT '{}', -- JSON: extraction settings, not data
                generation_options TEXT DEFAULT '{}', -- JSON: generation settings, not data
                validation_options TEXT DEFAULT '{}', -- JSON: validation settings, not data
                
                -- Processing Results (Framework Results - NOT Raw Data)
                extraction_results TEXT DEFAULT '{}', -- JSON: {
                                                      --   "extracted_formats": ["json", "yaml", "ttl", "xml"],
                                                      --   "output_files": {"json": "path/to/output.json", "yaml": "path/to/output.yaml"},
                                                      --   "extraction_summary": {"total_elements": 150, "successful_extractions": 148, "failed_extractions": 2},
                                                      --   "processing_metadata": {"start_time": "2024-01-15T10:00:00Z", "end_time": "2024-01-15T10:05:00Z"}
                                                      -- }
                
                generation_results TEXT DEFAULT '{}', -- JSON: {
                                                      --   "output_file": {"aasx_path": "path/to/output.aasx", "size_bytes": 1048576, "format_version": "3.0"},
                                                      --   "generation_summary": {"input_sources": 3, "generated_elements": 120, "validation_passed": true},
                                                      --   "processing_metadata": {"start_time": "2024-01-15T10:00:00Z", "end_time": "2024-01-15T10:08:00Z"}
                                                      -- }
                
                validation_results TEXT DEFAULT '{}', -- JSON: {
                                                      --   "validation_status": "passed", "validation_score": 95.5,
                                                      --   "validation_details": {"schema_validation": "passed", "content_validation": "passed", "quality_checks": "passed"},
                                                      --   "validation_metadata": {"validator_version": "2.1.0", "validation_time": "2024-01-15T10:09:00Z"}
                                                      -- }
                
                -- Performance & Quality Metrics (Framework Performance)
                processing_time REAL DEFAULT 0.0, -- Total processing time in seconds
                extraction_time REAL DEFAULT 0.0, -- Extraction time in seconds
                generation_time REAL DEFAULT 0.0, -- Generation time in seconds
                validation_time REAL DEFAULT 0.0, -- Validation time in seconds
                data_quality_score REAL DEFAULT 0.0 CHECK (data_quality_score >= 0.0 AND data_quality_score <= 1.0),
                processing_accuracy REAL DEFAULT 0.0 CHECK (processing_accuracy >= 0.0 AND processing_accuracy <= 1.0),
                file_integrity_checksum TEXT, -- MD5/SHA256 checksum for file integrity
                
                -- Security & Access Control (Framework Security)
                security_level TEXT DEFAULT 'standard' CHECK (security_level IN ('public', 'internal', 'confidential', 'secret', 'top_secret')),
                access_control_level TEXT DEFAULT 'user' CHECK (access_control_level IN ('public', 'user', 'admin', 'system', 'restricted')),
                encryption_enabled BOOLEAN DEFAULT FALSE,
                audit_logging_enabled BOOLEAN DEFAULT TRUE,
                
                -- User Management & Ownership (Framework Access Control)
                processed_by TEXT NOT NULL, -- user_id of the user who processed the job
                org_id TEXT NOT NULL, -- organization_id of the user who processed the job
                owner_team TEXT,
                steward_user_id TEXT,
                
                -- Timestamps & Audit (Framework Audit Trail)
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                activated_at TEXT,
                last_accessed_at TEXT,
                last_modified_at TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Legacy field for compatibility
                
                -- Output & Storage (Framework Storage - NOT Raw Data)
                output_directory TEXT, -- Directory path for output files, not the files themselves
                
                -- Error Handling (Framework Error Management)
                error_message TEXT, -- Error description, not raw error data
                error_code TEXT, -- Error code for categorization
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3,
                
                -- Federated Learning & Consent (Framework Compliance)
                federated_learning TEXT DEFAULT 'not_allowed' CHECK (federated_learning IN ('allowed', 'not_allowed', 'conditional')),
                user_consent_timestamp TEXT,
                consent_terms_version TEXT,
                federated_participation_status TEXT DEFAULT 'inactive',
                
                -- Configuration & Metadata (Framework Configuration - JSON)
                processing_config TEXT DEFAULT '{}', -- JSON: Framework settings, not data
                processing_metadata TEXT DEFAULT '{}', -- JSON: Framework metadata, not content
                custom_attributes TEXT DEFAULT '{}', -- JSON: Custom framework attributes
                tags_config TEXT DEFAULT '{}', -- JSON: {"tags": ["aasx", "etl", "processing"], "categories": ["data_processing", "automation"], "keywords": ["extraction", "generation", "validation"]}
                
                -- Relationships & Dependencies (Framework Dependencies - JSON)
                relationships_config TEXT DEFAULT '{}', -- JSON: {"depends_on": ["twin_registry", "kg_neo4j"], "provides_to": ["ai_rag", "certificate_manager"], "integrates_with": ["aasx_processing"]}
                dependencies_config TEXT DEFAULT '{}', -- JSON: {"required_modules": ["file_processor", "aasx_validator"], "optional_modules": ["neo4j", "physics_modeling"]}
                processing_instances_config TEXT DEFAULT '{}', -- JSON: {"active_instances": ["instance_1", "instance_2"], "instance_configs": {...}}
                
                -- Foreign Key Constraints
                FOREIGN KEY (file_id) REFERENCES files (file_id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE,
                FOREIGN KEY (processed_by) REFERENCES users (user_id) ON DELETE CASCADE,
                FOREIGN KEY (org_id) REFERENCES organizations (org_id) ON DELETE CASCADE,
                FOREIGN KEY (twin_registry_id) REFERENCES twin_registry (registry_id) ON DELETE SET NULL,
                FOREIGN KEY (kg_neo4j_id) REFERENCES kg_graph_registry (graph_id) ON DELETE SET NULL,
                FOREIGN KEY (ai_rag_id) REFERENCES ai_rag_registry (registry_id) ON DELETE SET NULL
            )
        """

        # Create the table
        if not self.create_table("aasx_processing", query):
            return False

        # Create indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_file_id ON aasx_processing (file_id)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_project_id ON aasx_processing (project_id)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_processed_by ON aasx_processing (processed_by)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_org_id ON aasx_processing (org_id)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_job_type ON aasx_processing (job_type)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_source_type ON aasx_processing (source_type)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_status ON aasx_processing (processing_status)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_health ON aasx_processing (health_status)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_lifecycle ON aasx_processing (lifecycle_status)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_extraction ON aasx_processing (extraction_status, generation_status, validation_status)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_created ON aasx_processing (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_updated ON aasx_processing (updated_at)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_workflow ON aasx_processing (workflow_type, processing_mode)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_integration ON aasx_processing (twin_registry_id, kg_neo4j_id, ai_rag_id)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_performance ON aasx_processing (processing_time, data_quality_score, processing_accuracy)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_timestamp ON aasx_processing (timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_priority ON aasx_processing (processing_priority)"
        ]

        return self.create_indexes("aasx_processing", index_queries)

    def _create_aasx_processing_metrics_table(self) -> bool:
        """Create the AASX processing metrics table with comprehensive performance monitoring."""
        query = """
            CREATE TABLE IF NOT EXISTS aasx_processing_metrics (
                -- Primary Identification
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                
                -- Real-time Health Metrics (Framework Health)
                health_score INTEGER CHECK (health_score >= 0 AND health_score <= 100),
                response_time_ms REAL,
                uptime_percentage REAL CHECK (uptime_percentage >= 0.0 AND uptime_percentage <= 100.0),
                error_rate REAL CHECK (error_rate >= 0.0 AND error_rate <= 1.0),
                
                -- AASX Processing Performance Metrics (Framework Performance - NOT Data)
                extraction_speed_sec REAL, -- Time to extract data from AASX
                generation_speed_sec REAL, -- Time to generate AASX from data
                validation_speed_sec REAL, -- Time to validate AASX content
                file_processing_efficiency REAL CHECK (file_processing_efficiency >= 0.0 AND file_processing_efficiency <= 1.0),
                
                -- Processing Technique Performance (JSON for better framework analysis)
                processing_technique_performance TEXT DEFAULT '{}', -- JSON: {
                                                                   --   "extraction": {"usage_count": 250, "avg_processing_time": 3.2, "success_rate": 0.98, "last_used": "2024-01-15T10:30:00Z"},
                                                                   --   "generation": {"usage_count": 180, "avg_processing_time": 5.7, "success_rate": 0.95, "last_used": "2024-01-15T09:15:00Z"},
                                                                   --   "validation": {"usage_count": 320, "avg_processing_time": 1.8, "success_rate": 0.99, "last_used": "2024-01-15T10:00:00Z"},
                                                                   --   "batch_processing": {"usage_count": 45, "avg_processing_time": 12.3, "success_rate": 0.92, "last_used": "2024-01-15T08:45:00Z"},
                                                                   --   "streaming_processing": {"usage_count": 75, "avg_processing_time": 2.1, "success_rate": 0.96, "last_used": "2024-01-15T10:15:00Z"}
                                                                   -- }
                
                -- File Type Processing Metrics (JSON for better framework analysis)
                file_type_processing_stats TEXT DEFAULT '{}', -- JSON: {
                                                              --   "aasx": {"processed": 450, "successful": 445, "failed": 5, "avg_processing_time": 4.2, "file_sizes": {"small": 200, "medium": 150, "large": 100}},
                                                              --   "json": {"processed": 320, "successful": 318, "failed": 2, "avg_processing_time": 1.8, "file_sizes": {"small": 250, "medium": 50, "large": 20}},
                                                              --   "yaml": {"processed": 280, "successful": 275, "failed": 5, "avg_processing_time": 2.1, "file_sizes": {"small": 200, "medium": 60, "large": 20}},
                                                              --   "xml": {"processed": 190, "successful": 185, "failed": 5, "avg_processing_time": 3.5, "file_sizes": {"small": 120, "medium": 50, "large": 20}},
                                                              --   "ttl": {"processed": 95, "successful": 92, "failed": 3, "avg_processing_time": 2.8, "file_sizes": {"small": 80, "medium": 10, "large": 5}}
                                                              -- }
                
                -- User Interaction Metrics (Framework Usage - NOT Content)
                user_interaction_count INTEGER DEFAULT 0, -- Number of user interactions
                job_execution_count INTEGER DEFAULT 0, -- Number of jobs executed
                successful_processing_operations INTEGER DEFAULT 0, -- Successful operations
                failed_processing_operations INTEGER DEFAULT 0, -- Failed operations
                
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
                
                -- Processing Patterns & Analytics (Framework Trends - JSON)
                processing_patterns TEXT DEFAULT '{}', -- JSON: {"hourly": {...}, "daily": {...}, "weekly": {...}, "monthly": {...}}
                resource_utilization_trends TEXT DEFAULT '{}', -- JSON: {"cpu_trend": [...], "memory_trend": [...], "disk_trend": [...]}
                user_activity TEXT DEFAULT '{}', -- JSON: {"peak_hours": [...], "user_patterns": {...}, "session_durations": [...]}
                job_patterns TEXT DEFAULT '{}', -- JSON: {"job_types": {...}, "complexity_distribution": {...}, "processing_times": [...]}
                compliance_status TEXT DEFAULT '{}', -- JSON: {"compliance_score": 0.95, "audit_status": "passed", "last_audit": "2024-01-15T00:00:00Z"}
                security_events TEXT DEFAULT '{}', -- JSON: {"events": [...], "threat_level": "low", "last_security_scan": "2024-01-15T00:00:00Z"}
                
                -- AASX-Specific Metrics (Framework Capabilities - JSON)
                aasx_analytics TEXT DEFAULT '{}', -- JSON: {"extraction_quality": 0.94, "generation_quality": 0.92, "validation_quality": 0.96}
                technique_effectiveness TEXT DEFAULT '{}', -- JSON: {"technique_comparison": {...}, "best_performing": "extraction", "optimization_suggestions": [...]}
                format_performance TEXT DEFAULT '{}', -- JSON: {"aasx_performance": {...}, "json_performance": {...}, "yaml_performance": {...}}
                file_size_processing_efficiency TEXT DEFAULT '{}', -- JSON: {"processing_speed_by_size": {...}, "quality_by_size": {...}, "optimization_opportunities": [...]}
                
                -- Time-based Analytics (Framework Time Analysis)
                hour_of_day INTEGER CHECK (hour_of_day >= 0 AND hour_of_day <= 23),
                day_of_week INTEGER CHECK (day_of_week >= 1 AND day_of_week <= 7),
                month INTEGER CHECK (month >= 1 AND month <= 12),
                
                -- Performance Trends (Framework Performance Analysis)
                processing_time_trend REAL, -- Compared to historical average
                resource_efficiency_trend REAL, -- Performance over time
                quality_trend REAL, -- Quality metrics over time
                
                -- Foreign Key Constraints
                FOREIGN KEY (job_id) REFERENCES aasx_processing (job_id) ON DELETE CASCADE
            )
        """

        # Create the table
        if not self.create_table("aasx_processing_metrics", query):
            return False

        # Create indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_metrics_job_id ON aasx_processing_metrics (job_id)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_metrics_timestamp ON aasx_processing_metrics (timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_metrics_health ON aasx_processing_metrics (health_score)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_metrics_performance ON aasx_processing_metrics (extraction_speed_sec, generation_speed_sec, validation_speed_sec)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_metrics_quality ON aasx_processing_metrics (data_freshness_score, data_completeness_score)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_metrics_resources ON aasx_processing_metrics (cpu_usage_percent, memory_usage_percent, disk_io_mb)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_metrics_user_activity ON aasx_processing_metrics (user_interaction_count, job_execution_count)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_metrics_technique ON aasx_processing_metrics (processing_technique_performance)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_metrics_file_processing ON aasx_processing_metrics (file_type_processing_stats)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_metrics_time_analysis ON aasx_processing_metrics (hour_of_day, day_of_week, month)"
        ]

        return self.create_indexes("aasx_processing_metrics", index_queries)


