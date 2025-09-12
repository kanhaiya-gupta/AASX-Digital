"""
Certificate Manager Schema Module

Comprehensive digital certificate system for AASX Digital Twin Analytics.
Automatically generates, maintains, and exports verifiable digital certificates
for every processed AASX sample with complete business entity relationships.

Author: AASX Digital Twin Analytics Framework
Version: 1.0.0
"""

import logging
from typing import List, Dict, Any
from ..base_schema import BaseSchemaModule

logger = logging.getLogger(__name__)


class CertificateManagerSchema(BaseSchemaModule):
    """Certificate Manager database schema module."""
    
    def __init__(self, db_manager=None):
        super().__init__(db_manager)
        self.module_name = "certificate_manager"
        self.description = "Digital Certificate Management System for AASX Digital Twin Analytics"
        self.version = "1.0.0"
    

    def _create_certificates_registry_table(self) -> bool:
        """Create the main certificates registry table."""
        query = """
        CREATE TABLE IF NOT EXISTS certificates_registry (
            certificate_id TEXT PRIMARY KEY,
            
            -- Core Business Entity Relationships (MANDATORY)
            file_id TEXT NOT NULL,                       -- Reference to the AASX file
            user_id TEXT NOT NULL,                       -- User who created/manages
            org_id TEXT NOT NULL,                        -- Organization that owns
            project_id TEXT NOT NULL,                    -- Project context
            use_case_id TEXT NOT NULL,                   -- Use case context
            twin_id TEXT NOT NULL,                       -- Digital twin reference
            
            -- Certificate Identity & Metadata
            certificate_name TEXT NOT NULL,              -- Human-readable name
            certificate_type TEXT DEFAULT 'standard' CHECK (certificate_type IN ('standard', 'premium', 'enterprise', 'custom')),
            certificate_category TEXT DEFAULT 'aasx_processing' CHECK (certificate_category IN ('aasx_processing', 'quality_assessment', 'compliance_audit', 'performance_analysis')),
            
            -- Module Integration Status (Real-time tracking)
            aasx_etl_status TEXT DEFAULT 'pending' CHECK (aasx_etl_status IN ('pending', 'in_progress', 'completed', 'failed', 'skipped')),
            twin_registry_status TEXT DEFAULT 'pending' CHECK (twin_registry_status IN ('pending', 'in_progress', 'completed', 'failed', 'skipped')),
            ai_rag_status TEXT DEFAULT 'pending' CHECK (ai_rag_status IN ('pending', 'in_progress', 'completed', 'failed', 'skipped')),
            kg_neo4j_status TEXT DEFAULT 'pending' CHECK (kg_neo4j_status IN ('pending', 'in_progress', 'completed', 'failed', 'skipped')),
            physics_modeling_status TEXT DEFAULT 'pending' CHECK (physics_modeling_status IN ('pending', 'in_progress', 'completed', 'failed', 'skipped')),
            federated_learning_status TEXT DEFAULT 'pending' CHECK (federated_learning_status IN ('pending', 'in_progress', 'completed', 'failed', 'skipped')),
            data_governance_status TEXT DEFAULT 'pending' CHECK (data_governance_status IN ('pending', 'in_progress', 'completed', 'failed', 'skipped')),
            
            -- Module Completion Tracking
            completed_modules_count INTEGER DEFAULT 0,   -- Number of completed modules
            total_modules_count INTEGER DEFAULT 7,      -- Total expected modules
            completion_percentage REAL DEFAULT 0.0 CHECK (completion_percentage >= 0.0 AND completion_percentage <= 100.0),
            
            -- Consolidated Module Data (JSON summaries - NO raw data)
            aasx_etl_summary TEXT DEFAULT '{}',           -- Processing status, quality metrics, records count
            twin_registry_summary TEXT DEFAULT '{}',      -- Health score, lifecycle status, metadata
            ai_rag_summary TEXT DEFAULT '{}',             -- Insights, classifications, confidence scores
            kg_neo4j_summary TEXT DEFAULT '{}',           -- Graph metrics, entities, relationships
            physics_modeling_summary TEXT DEFAULT '{}',   -- Simulation results, model performance, progress
            federated_learning_summary TEXT DEFAULT '{}', -- Participation, contribution, performance
            data_governance_summary TEXT DEFAULT '{}',    -- Quality scores, compliance status, governance
            
            -- Quality Assessment Scores
            overall_quality_score REAL DEFAULT 0.0 CHECK (overall_quality_score >= 0.0 AND overall_quality_score <= 100.0),
            data_completeness_score REAL DEFAULT 0.0 CHECK (data_completeness_score >= 0.0 AND data_completeness_score <= 100.0),
            data_accuracy_score REAL DEFAULT 0.0 CHECK (data_accuracy_score >= 0.0 AND data_accuracy_score <= 100.0),
            data_reliability_score REAL DEFAULT 0.0 CHECK (data_reliability_score >= 0.0 AND data_reliability_score <= 100.0),
            data_consistency_score REAL DEFAULT 0.0 CHECK (data_consistency_score >= 0.0 AND data_consistency_score <= 100.0),
            
            -- Digital Trust & Verification
            digital_signature TEXT,                        -- Digital signature for authenticity
            signature_timestamp TEXT,                      -- When signature was applied
            verification_hash TEXT,                        -- Hash for integrity verification
            qr_code_data TEXT,                            -- QR code data for mobile verification
            certificate_chain_status TEXT DEFAULT 'pending' CHECK (certificate_chain_status IN ('pending', 'valid', 'invalid', 'expired')),
            
            -- Certificate Configuration
            template_id TEXT DEFAULT 'default',            -- Certificate template to use
            retention_policy TEXT DEFAULT 'keep_all' CHECK (retention_policy IN ('keep_all', 'keep_last_n', 'archive_after_days', 'delete_after_days')),
            retention_value INTEGER DEFAULT 0,             -- Value for retention policy (days or count)
            visibility TEXT DEFAULT 'private' CHECK (visibility IN ('private', 'public', 'restricted', 'organization')),
            access_level TEXT DEFAULT 'project_members' CHECK (access_level IN ('owner_only', 'project_members', 'organization_members', 'public')),
            
            -- Lifecycle & Status
            status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'ready', 'stale', 'archived', 'error', 'expired')),
            lifecycle_phase TEXT DEFAULT 'creation' CHECK (lifecycle_phase IN ('creation', 'population', 'validation', 'active', 'maintenance', 'archival')),
            current_version TEXT DEFAULT '1.0.0',         -- Current certificate version
            priority TEXT DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'critical', 'urgent')),
            
            -- Timestamps & Audit
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            last_updated_at TEXT,                         -- Last time any field was updated
            last_module_update TEXT,                       -- Last time any module updated
            expires_at TEXT,                               -- When certificate expires
            archived_at TEXT,                              -- When certificate was archived
            
            -- User Management & Ownership
            owner_team TEXT,                               -- Team responsible for this certificate
            steward_user_id TEXT,                          -- Data steward for this certificate
            reviewer_user_id TEXT,                         -- User who reviewed/approved
            approval_status TEXT DEFAULT 'pending' CHECK (approval_status IN ('pending', 'approved', 'rejected', 'requires_changes')),
            approval_timestamp TEXT,                       -- When approval was given
            approval_notes TEXT,                           -- Notes from approval process
            
            -- Business Context
            business_unit TEXT,                            -- Business unit this belongs to
            cost_center TEXT,                              -- Cost center for billing
            tags TEXT DEFAULT '[]',                        -- JSON array of tags for categorization
            custom_attributes TEXT DEFAULT '{}',           -- JSON object for custom fields
            
            -- Constraints (ALL BUSINESS ENTITY RELATIONSHIPS)
            FOREIGN KEY (file_id) REFERENCES files(file_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (org_id) REFERENCES organizations(org_id) ON DELETE CASCADE,
            FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
            FOREIGN KEY (use_case_id) REFERENCES use_cases(use_case_id) ON DELETE CASCADE,
            FOREIGN KEY (twin_id) REFERENCES twin_registry(twin_id) ON DELETE CASCADE,
            
            -- Additional Constraints
            UNIQUE(file_id, twin_id),                      -- One certificate per file-twin combination
            CHECK (completion_percentage >= 0.0 AND completion_percentage <= 100.0),
            CHECK (overall_quality_score >= 0.0 AND overall_quality_score <= 100.0)
        )
        """
        
        # Create the table
        if not self.create_table("certificates_registry", query):
            return False
        
        # Create indexes for this table
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_certificates_file_id ON certificates_registry(file_id);",
            "CREATE INDEX IF NOT EXISTS idx_certificates_user_id ON certificates_registry(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_certificates_org_id ON certificates_registry(org_id);",
            "CREATE INDEX IF NOT EXISTS idx_certificates_project_id ON certificates_registry(project_id);",
            "CREATE INDEX IF NOT EXISTS idx_certificates_use_case_id ON certificates_registry(use_case_id);",
            "CREATE INDEX IF NOT EXISTS idx_certificates_twin_id ON certificates_registry(twin_id);",
            "CREATE INDEX IF NOT EXISTS idx_certificates_status ON certificates_registry(status);",
            "CREATE INDEX IF NOT EXISTS idx_certificates_created_at ON certificates_registry(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_certificates_org_user ON certificates_registry(org_id, user_id);",
            "CREATE INDEX IF NOT EXISTS idx_certificates_project_user ON certificates_registry(project_id, user_id);",
            "CREATE INDEX IF NOT EXISTS idx_certificates_completion ON certificates_registry(completion_percentage);",
            "CREATE INDEX IF NOT EXISTS idx_certificates_quality ON certificates_registry(overall_quality_score);"
        ]
        
        return self.create_indexes("certificates_registry", index_queries)
    
    def _create_certificates_versions_table(self) -> bool:
        """Create the certificate versions table for complete version history."""
        query = """
        CREATE TABLE IF NOT EXISTS certificates_versions (
            version_id TEXT PRIMARY KEY,
            certificate_id TEXT NOT NULL,
            
            -- Version Information
            version_number TEXT NOT NULL,                 -- Semantic version (1.0.0, 1.1.0, etc.)
            version_type TEXT NOT NULL CHECK (version_type IN ('major', 'minor', 'patch', 'draft', 'preview')),
            version_name TEXT,                            -- Human-readable version name
            version_description TEXT,                     -- Description of what this version contains
            
            -- Complete Data Snapshot (JSON)
            module_data_snapshot JSON NOT NULL,           -- Complete data from ALL modules at this version
            consolidated_summary JSON NOT NULL,           -- Consolidated view at this version
            change_summary JSON DEFAULT '{}',             -- JSON: what changed in this version
            diff_summary JSON DEFAULT '{}',               -- JSON: detailed changes from previous version
            
            -- Version Metadata
            change_reason TEXT,                           -- Why this version was created
            change_request_id TEXT,                       -- Reference to change request
            change_category TEXT CHECK (change_category IN ('module_update', 'quality_improvement', 'template_change', 'correction', 'enhancement')),
            change_priority TEXT DEFAULT 'normal' CHECK (change_priority IN ('low', 'normal', 'high', 'critical')),
            
            -- Approval & Review
            approved_by TEXT,                             -- User who approved this version
            approval_timestamp TEXT,                      -- When approval was given
            approval_status TEXT DEFAULT 'pending' CHECK (approval_status IN ('pending', 'approved', 'rejected', 'requires_changes')),
            approval_notes TEXT,                          -- Notes from approval process
            reviewer_user_id TEXT,                        -- User who reviewed this version
            
            -- Digital Trust
            version_signature TEXT,                       -- Digital signature for this version
            version_hash TEXT,                            -- Hash for integrity verification
            signature_timestamp TEXT,                     -- When signature was applied
            
            -- Quality & Validation
            version_quality_score REAL CHECK (version_quality_score >= 0.0 AND version_quality_score <= 100.0),
            validation_status TEXT DEFAULT 'pending' CHECK (validation_status IN ('pending', 'validated', 'failed', 'requires_review')),
            validation_notes TEXT,                        -- Notes from validation process
            
            -- Timestamps & Audit
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            created_by TEXT NOT NULL,                     -- User who created this version
            created_from TEXT,                            -- Source of version creation (manual, auto, system)
            review_timestamp TEXT,                        -- When version was reviewed
            published_at TEXT,                            -- When version was published
            
            -- Soft Delete Support
            is_deleted BOOLEAN DEFAULT FALSE,              -- Soft delete flag
            deleted_at TEXT,                               -- When version was soft deleted
            deleted_by TEXT,                               -- User who soft deleted the version
            
            -- Environment Management
            deployment_environment TEXT DEFAULT 'development', -- Current deployment environment
            deployment_status TEXT DEFAULT 'not_deployed' CHECK (deployment_status IN ('not_deployed', 'deployed', 'failed', 'rolling_back')),
            deployment_timestamp TEXT,                     -- When deployed to environment
            environment_promotion_history JSON DEFAULT '{}', -- JSON: history of environment promotions
            
            -- Performance & Analytics
            performance_metrics JSON DEFAULT '{}',         -- JSON: performance data
            usage_statistics JSON DEFAULT '{}',            -- JSON: usage analytics
            storage_optimization_data JSON DEFAULT '{}',   -- JSON: storage optimization info
            
            -- Security & Access Control
            version_permissions JSON DEFAULT '{}',         -- JSON: version-specific permissions
            access_control_list JSON DEFAULT '{}',         -- JSON: ACL data
            security_level TEXT DEFAULT 'standard' CHECK (security_level IN ('low', 'standard', 'high', 'critical')),
            encryption_status TEXT DEFAULT 'none' CHECK (encryption_status IN ('none', 'encrypted', 'encryption_failed')),
            
            -- Reporting & Compliance
            compliance_status JSON DEFAULT '{}',           -- JSON: compliance data
            audit_trail_data JSON DEFAULT '{}',            -- JSON: audit trail
            reporting_metadata JSON DEFAULT '{}',          -- JSON: reporting metadata
            
            -- Version Lifecycle Management
            archive_status TEXT DEFAULT 'active' CHECK (archive_status IN ('active', 'archived', 'restored')),
            archive_timestamp TEXT,                        -- When version was archived
            archive_reason TEXT,                           -- Reason for archiving
            restore_timestamp TEXT,                        -- When version was restored
            
            -- Constraints
            FOREIGN KEY (certificate_id) REFERENCES certificates_registry(certificate_id) ON DELETE CASCADE,
            FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (approved_by) REFERENCES users(user_id) ON DELETE SET NULL,
            FOREIGN KEY (reviewer_user_id) REFERENCES users(user_id) ON DELETE SET NULL,
            UNIQUE(certificate_id, version_number)
        )
        """
        
        # Create the table
        if not self.create_table("certificates_versions", query):
            return False
        
        # Create indexes for this table
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_certificate_versions_cert_id ON certificates_versions(certificate_id);",
            "CREATE INDEX IF NOT EXISTS idx_certificate_versions_created_at ON certificates_versions(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_certificate_versions_created_by ON certificates_versions(created_by);",
            "CREATE INDEX IF NOT EXISTS idx_certificate_versions_approval ON certificates_versions(approval_status);",
            "CREATE INDEX IF NOT EXISTS idx_certificate_versions_version ON certificates_versions(version_number);",
            "CREATE INDEX IF NOT EXISTS idx_certificate_versions_deployment ON certificates_versions(deployment_environment, deployment_status);",
            "CREATE INDEX IF NOT EXISTS idx_certificate_versions_archive ON certificates_versions(archive_status);",
            "CREATE INDEX IF NOT EXISTS idx_certificate_versions_security ON certificates_versions(security_level);",
            "CREATE INDEX IF NOT EXISTS idx_certificate_versions_encryption ON certificates_versions(encryption_status);"
        ]
        
        return self.create_indexes("certificates_versions", index_queries)
    
    def _create_certificates_metrics_table(self) -> bool:
        """Create the certificate metrics table for performance and analytics."""
        query = """
        CREATE TABLE IF NOT EXISTS certificates_metrics (
            metric_id TEXT PRIMARY KEY,
            certificate_id TEXT NOT NULL,
            
            -- Performance Metrics
            generation_time_ms INTEGER,                   -- Time to generate certificate
            export_time_ms INTEGER,                      -- Time to export in different formats
            viewer_load_time_ms INTEGER,                 -- Time to load in viewer
            cache_hit_rate REAL CHECK (cache_hit_rate >= 0.0 AND cache_hit_rate <= 100.0),
            
            -- Usage Metrics
            view_count INTEGER DEFAULT 0,                -- Number of times viewed
            export_count INTEGER DEFAULT 0,              -- Number of times exported
            verification_count INTEGER DEFAULT 0,        -- Number of times verified
            share_count INTEGER DEFAULT 0,               -- Number of times shared
            download_count INTEGER DEFAULT 0,            -- Number of times downloaded
            
            -- Module Performance Metrics
            active_module_count INTEGER DEFAULT 0,       -- Number of active modules
            module_update_frequency REAL,                -- Average updates per day
            last_module_update TEXT,                     -- Last time any module updated
            module_processing_times TEXT DEFAULT '{}',   -- JSON: processing times for each module
            
            -- Quality Metrics
            data_completeness_score REAL CHECK (data_completeness_score >= 0.0 AND data_completeness_score <= 100.0),
            data_quality_score REAL CHECK (data_quality_score >= 0.0 AND data_quality_score <= 100.0),
            module_coverage_score REAL CHECK (module_coverage_score >= 0.0 AND module_coverage_score <= 100.0),
            validation_success_rate REAL CHECK (validation_success_rate >= 0.0 AND validation_success_rate <= 100.0),
            
            -- Business Metrics
            stakeholder_access_count INTEGER DEFAULT 0,   -- Number of stakeholders who accessed
            compliance_check_count INTEGER DEFAULT 0,     -- Number of compliance checks performed
            audit_trail_length INTEGER DEFAULT 0,        -- Length of audit trail
            change_request_count INTEGER DEFAULT 0,      -- Number of change requests
            
            -- Storage & Performance
            certificate_size_kb INTEGER,                 -- Certificate size in KB
            database_query_count INTEGER DEFAULT 0,      -- Number of database queries
            external_api_calls INTEGER DEFAULT 0,        -- Number of external API calls
            cache_size_kb INTEGER,                       -- Cache size in KB
            
            -- Error & Performance Tracking
            error_count INTEGER DEFAULT 0,               -- Number of errors encountered
            last_error_timestamp TEXT,                   -- Last time an error occurred
            error_types TEXT DEFAULT '{}',               -- JSON: types of errors encountered
            performance_degradation_count INTEGER DEFAULT 0, -- Number of performance issues
            
            -- User Engagement Metrics
            unique_viewers INTEGER DEFAULT 0,            -- Number of unique users who viewed
            average_session_duration_seconds INTEGER,    -- Average time spent viewing
            return_visitor_count INTEGER DEFAULT 0,      -- Number of return visitors
            user_satisfaction_score REAL CHECK (user_satisfaction_score >= 0.0 AND user_satisfaction_score <= 5.0),
            
            -- Timestamps & Audit
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            last_metric_update TEXT,                     -- Last time metrics were updated
            metrics_collection_frequency TEXT DEFAULT 'daily', -- How often metrics are collected
            
            -- Constraints
            FOREIGN KEY (certificate_id) REFERENCES certificates_registry(certificate_id) ON DELETE CASCADE
        )
        """
        
        # Create the table
        if not self.create_table("certificates_metrics", query):
            return False
        
        # Create indexes for this table
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_certificate_metrics_cert_id ON certificates_metrics(certificate_id);",
            "CREATE INDEX IF NOT EXISTS idx_certificate_metrics_created_at ON certificates_metrics(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_certificate_metrics_quality ON certificates_metrics(data_quality_score);",
            "CREATE INDEX IF NOT EXISTS idx_certificate_metrics_performance ON certificates_metrics(generation_time_ms);",
            "CREATE INDEX IF NOT EXISTS idx_certificate_metrics_usage ON certificates_metrics(view_count, export_count);"
        ]
        
        return self.create_indexes("certificates_metrics", index_queries)
    
    def create_tables(self) -> bool:
        """Create all tables for the certificate manager module."""
        try:
            logger.info("🔐 Creating Certificate Manager Module Tables...")
            
            # Create tables in dependency order
            tables_created = []
            
            # 1. Create certificates registry table
            if self._create_certificates_registry_table():
                tables_created.append("certificates_registry")
            else:
                logger.error("Failed to create certificates_registry table")
                return False
            
            # 2. Create certificates versions table
            if self._create_certificates_versions_table():
                tables_created.append("certificates_versions")
            else:
                logger.error("Failed to create certificates_versions table")
                return False
            
            # 3. Create certificates metrics table
            if self._create_certificates_metrics_table():
                tables_created.append("certificates_metrics")
            else:
                logger.error("Failed to create certificates_metrics table")
                return False
            
            logger.info(f"✅ Certificate Manager Module: Created {len(tables_created)} tables successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating certificate manager tables: {e}")
            return False
    
    def get_module_description(self) -> str:
        """Get a description of the certificate manager module."""
        return self.description
    
    def get_table_names(self) -> List[str]:
        """Get the names of all tables in this module."""
        return ['certificates_registry', 'certificates_versions', 'certificates_metrics']
    
    def get_validation_rules(self) -> Dict[str, Any]:
        """Get validation rules for the certificate manager module."""
        return {
            "module_name": "certificate_manager",
            "tables": {
                "certificates_registry": {
                    "required_columns": [
                        "certificate_id", "file_id", "user_id", "org_id", 
                        "project_id", "use_case_id", "twin_id", "certificate_name"
                    ],
                    "foreign_keys": [
                        "files(file_id)", "users(user_id)", "organizations(org_id)",
                        "projects(project_id)", "use_cases(use_case_id)", "twin_registry(twin_id)"
                    ],
                    "check_constraints": [
                        "completion_percentage >= 0.0 AND completion_percentage <= 100.0",
                        "overall_quality_score >= 0.0 AND overall_quality_score <= 100.0"
                    ]
                },
                "certificates_versions": {
                    "required_columns": ["version_id", "certificate_id", "version_number", "created_by"],
                    "foreign_keys": [
                        "certificates_registry(certificate_id)", "users(created_by)"
                    ],
                    "unique_constraints": ["certificate_id, version_number"]
                },
                "certificates_metrics": {
                    "required_columns": ["metric_id", "certificate_id"],
                    "foreign_keys": ["certificates_registry(certificate_id)"],
                    "check_constraints": [
                        "cache_hit_rate >= 0.0 AND cache_hit_rate <= 100.0",
                        "data_quality_score >= 0.0 AND data_quality_score <= 100.0"
                    ]
                }
            },
            "business_rules": [
                "Every certificate must be linked to a file, user, organization, project, use case, and digital twin",
                "Certificate versions must have unique version numbers per certificate",
                "Quality scores must be between 0.0 and 100.0",
                "Completion percentage must be between 0.0 and 100.0",
                "One certificate per file-twin combination"
            ]
        }
