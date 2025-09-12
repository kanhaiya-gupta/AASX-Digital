"""
Certificate Manager Schema Module

Comprehensive digital certificate system for AASX Digital Twin Analytics.
Automatically generates, maintains, and exports verifiable digital certificates
for every processed AASX sample with complete business entity relationships.

ENTERPRISE-GRADE FEATURES (MERGED INTO MAIN TABLES):
- Advanced certificate lifecycle management with digital trust and verification
- Automated compliance monitoring and audit trail management (merged into certificates_registry)
- Comprehensive security and access control for certificate operations (merged into certificates_registry)
- Enterprise-grade metrics and analytics for certificate management (merged into certificates_metrics)
- Advanced governance and policy enforcement capabilities

TABLE STRUCTURE:
- certificates_registry: Main certificate table with compliance and security fields
- certificates_versions: Version tracking with complete change history
- certificates_metrics: Performance metrics with enterprise analytics
"""

import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import json
import asyncio
from ..base_schema import BaseSchema

logger = logging.getLogger(__name__)


class CertificateManagerSchema(BaseSchema):
    """
    Enterprise-Grade Certificate Manager Schema Module (Merged Table Structure)
    
    Comprehensive digital certificate system for AASX Digital Twin Analytics.
    Automatically generates, maintains, and exports verifiable digital certificates
    for every processed AASX sample with complete business entity relationships.
    
    MERGED TABLE ARCHITECTURE:
    - certificates_registry: Enhanced with compliance tracking and security metrics
    - certificates_versions: Complete version history with change tracking
    - certificates_metrics: Enhanced with enterprise performance analytics
    
    All enterprise functionality is now consolidated into these three main tables
    for improved performance, maintainability, and data consistency.
    """
    
    def __init__(self, connection_manager, schema_name: str = "certificate_manager"):
        super().__init__(connection_manager, schema_name)
        self._certificate_metrics = {}
        self._performance_analytics = {}
        self._compliance_status = {}
        self._security_metrics = {}
        self.description = "Digital Certificate Management System for AASX Digital Twin Analytics"
        self.version = "1.0.0"
    

    async def _create_certificates_registry_table(self) -> bool:
        """Create the main certificates registry table."""
        query = """
        CREATE TABLE IF NOT EXISTS certificates_registry (
            certificate_id TEXT PRIMARY KEY,
            
            -- Core Business Entity Relationships (MANDATORY)
            file_id TEXT NOT NULL,                       -- Reference to the AASX file
            user_id TEXT NOT NULL,                       -- User who created/manages
            org_id TEXT NOT NULL,                        -- Organization that owns
            dept_id TEXT,                                -- Department for complete traceability
            project_id TEXT,                             -- Project context
            use_case_id TEXT,                            -- Use case context
            twin_id TEXT,                                -- Digital twin reference
            
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
            digital_product_passport_status TEXT DEFAULT 'pending' CHECK (digital_product_passport_status IN ('pending', 'in_progress', 'completed', 'failed', 'skipped')),
            
            -- Module Completion Tracking
            completed_modules_count INTEGER DEFAULT 0,   -- Number of completed modules
            total_modules_count INTEGER DEFAULT 8,      -- Total expected modules (including DPP)
            completion_percentage REAL DEFAULT 0.0 CHECK (completion_percentage >= 0.0 AND completion_percentage <= 100.0),
            

            
            -- Module Integration IDs (for cross-module references)
            aasx_etl_job_id TEXT,                        -- AASX ETL job identifier
            twin_registry_id TEXT,                        -- Twin registry integration ID
            ai_rag_registry_id TEXT,                      -- AI RAG registry integration ID
            kg_neo4j_registry_id TEXT,                    -- KG Neo4j registry integration ID
            federated_learning_registry_id TEXT,          -- Federated learning registry integration ID
            physics_modeling_registry_id TEXT,            -- Physics modeling registry integration ID
            data_governance_registry_id TEXT,             -- Data governance registry integration ID
            digital_product_passport_registry_id TEXT,    -- Digital Product Passport registry integration ID
            
            -- Module Data Summaries (JSON format for easy querying)
            aasx_etl_summary JSON DEFAULT '{}',           -- AASX ETL processing summary
            twin_registry_summary JSON DEFAULT '{}',      -- Twin registry processing summary
            ai_rag_summary JSON DEFAULT '{}',             -- AI RAG processing summary
            kg_neo4j_summary JSON DEFAULT '{}',           -- KG Neo4j processing summary
            federated_learning_summary JSON DEFAULT '{}', -- Federated learning processing summary
            physics_modeling_summary JSON DEFAULT '{}',   -- Physics modeling processing summary
            data_governance_summary JSON DEFAULT '{}',    -- Data governance processing summary
            digital_product_passport_summary JSON DEFAULT '{}', -- Digital Product Passport (DPP) summary
            
            -- Quality Assessment Scores
            overall_quality_score REAL DEFAULT 0.0 CHECK (overall_quality_score >= 0.0 AND overall_quality_score <= 100.0),
            data_completeness_score REAL DEFAULT 0.0 CHECK (data_completeness_score >= 0.0 AND data_completeness_score <= 100.0),
            data_accuracy_score REAL DEFAULT 0.0 CHECK (data_accuracy_score >= 0.0 AND data_accuracy_score <= 100.0),
            data_reliability_score REAL DEFAULT 0.0 CHECK (data_reliability_score >= 0.0 AND data_reliability_score <= 100.0),
            data_consistency_score REAL DEFAULT 0.0 CHECK (data_consistency_score >= 0.0 AND data_consistency_score <= 100.0),
            
            -- Enterprise Compliance Tracking
            compliance_type TEXT DEFAULT 'standard' CHECK (compliance_type IN ('standard', 'gdpr', 'sox', 'iso27001', 'custom')),
            compliance_status TEXT DEFAULT 'pending' CHECK (compliance_status IN ('pending', 'compliant', 'non_compliant', 'requires_review', 'audit_in_progress')),
            compliance_score REAL DEFAULT 0.0 CHECK (compliance_score >= 0.0 AND compliance_score <= 100.0),
            last_audit_date TEXT,                         -- Last compliance audit date
            next_audit_date TEXT,                         -- Next scheduled audit date
            audit_details JSON DEFAULT '{}',              -- JSON: detailed audit information
            
            -- Enterprise Security Metrics
            security_event_type TEXT DEFAULT 'none' CHECK (security_event_type IN ('none', 'access_attempt', 'data_breach', 'policy_violation', 'security_scan')),
            security_level TEXT DEFAULT 'standard' CHECK (security_level IN ('basic', 'standard', 'enhanced', 'enterprise', 'military')),
            threat_assessment TEXT DEFAULT 'low' CHECK (threat_assessment IN ('low', 'medium', 'high', 'critical')),
            security_score REAL DEFAULT 0.0 CHECK (security_score >= 0.0 AND security_score <= 100.0),
            last_security_scan TEXT,                      -- Last security scan date
            security_details JSON DEFAULT '{}',            -- JSON: security scan results and details
            
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
            created_by TEXT NOT NULL,                      -- User who created the certificate
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
            tags JSON DEFAULT '{}',                        -- JSON object of tags for categorization
            custom_attributes JSON DEFAULT '{}',           -- JSON object for custom fields
            
            -- Soft Delete Support
            is_deleted BOOLEAN DEFAULT FALSE,              -- Soft delete flag
            deleted_at TEXT,                               -- When certificate was soft deleted
            deleted_by TEXT                               -- User who soft deleted the certificate
            
            -- Constraints (ALL BUSINESS ENTITY RELATIONSHIPS) - DISABLED FOR TESTING
            -- FOREIGN KEY (file_id) REFERENCES files(file_id) ON DELETE CASCADE,
            -- FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            -- FOREIGN KEY (org_id) REFERENCES organizations(org_id) ON DELETE CASCADE,
            -- FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE SET NULL,
            -- FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
            -- FOREIGN KEY (use_case_id) REFERENCES use_cases(use_case_id) ON DELETE CASCADE,
            -- FOREIGN KEY (twin_id) REFERENCES twin_registry(twin_id) ON DELETE CASCADE,
            
            -- Additional Constraints
            --UNIQUE(file_id, twin_id),                      -- One certificate per file-twin combination
            --CHECK (completion_percentage >= 0.0 AND completion_percentage <= 100.0),
            --CHECK (overall_quality_score >= 0.0 AND overall_quality_score <= 100.0)
        )
        """
        
        # Create the table using connection manager
        await self.connection_manager.execute_query(query)
        
        # Create indexes for this table
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_certificates_file_id ON certificates_registry(file_id);",
            "CREATE INDEX IF NOT EXISTS idx_certificates_user_id ON certificates_registry(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_certificates_org_id ON certificates_registry(org_id);",
            "CREATE INDEX IF NOT EXISTS idx_certificates_dept_id ON certificates_registry(dept_id);",
            "CREATE INDEX IF NOT EXISTS idx_certificates_project_id ON certificates_registry(project_id);",
            "CREATE INDEX IF NOT EXISTS idx_certificates_use_case_id ON certificates_registry(use_case_id);",
            "CREATE INDEX IF NOT EXISTS idx_certificates_twin_id ON certificates_registry(twin_id);",
            "CREATE INDEX IF NOT EXISTS idx_certificates_status ON certificates_registry(status);",
            "CREATE INDEX IF NOT EXISTS idx_certificates_created_at ON certificates_registry(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_certificates_org_user ON certificates_registry(org_id, user_id);",
            "CREATE INDEX IF NOT EXISTS idx_certificates_project_user ON certificates_registry(project_id, user_id);",
            "CREATE INDEX IF NOT EXISTS idx_certificates_completion ON certificates_registry(completion_percentage);",
            "CREATE INDEX IF NOT EXISTS idx_certificates_quality ON certificates_registry(overall_quality_score);",
            "CREATE INDEX IF NOT EXISTS idx_certificates_compliance ON certificates_registry(compliance_status, compliance_score);",
            "CREATE INDEX IF NOT EXISTS idx_certificates_security ON certificates_registry(security_level, security_score);",
            "CREATE INDEX IF NOT EXISTS idx_certificates_audit ON certificates_registry(last_audit_date, next_audit_date);"
        ]
        
        return await self.create_indexes("certificates_registry", index_queries)
    
    async def _create_certificates_versions_table(self) -> bool:
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
            version_status TEXT DEFAULT 'draft',          -- Version status
            
            -- Complete Data Snapshot (JSON)
            module_data_snapshot JSON NOT NULL,           -- Complete data from ALL modules at this version
            consolidated_summary JSON NOT NULL,           -- Consolidated view at this version
            change_summary JSON DEFAULT '{}',             -- JSON: what changed in this version
            diff_summary JSON DEFAULT '{}',               -- JSON: detailed changes from previous version
            
            -- Complex Component Models (JSON)
            version_metadata JSON DEFAULT '{}',           -- VersionMetadata component
            data_snapshots JSON DEFAULT '{}',             -- DataSnapshots component
            change_tracking JSON DEFAULT '{}',            -- ChangeTracking component
            approval_workflow JSON DEFAULT '{}',          -- ApprovalWorkflow component
            digital_verification JSON DEFAULT '{}',       -- DigitalVerification component
            business_intelligence JSON DEFAULT '{}',      -- BusinessIntelligence component
            
            -- Version Metadata
            change_reason TEXT,                           -- Why this version was created
            change_request_id TEXT,                       -- Reference to change request
            change_category TEXT CHECK (change_category IN ('module_update', 'quality_improvement', 'template_change', 'correction', 'enhancement')),
            change_priority TEXT DEFAULT 'normal' CHECK (change_priority IN ('low', 'normal', 'high', 'critical')),
            change_description TEXT DEFAULT '',           -- Detailed description of changes
            
            -- Approval & Review
            approved_by TEXT,                             -- User who approved this version
            approval_timestamp TEXT,                      -- When approval was given
            approval_status TEXT DEFAULT 'pending' CHECK (approval_status IN ('pending', 'approved', 'rejected', 'requires_changes')),
            is_approved BOOLEAN DEFAULT FALSE,            -- Whether this version is approved
            is_rejected BOOLEAN DEFAULT FALSE,            -- Whether this version is rejected
            is_pending_approval BOOLEAN DEFAULT TRUE,     -- Whether this version is pending approval
            approval_notes TEXT,                          -- Notes from approval process
            reviewer_user_id TEXT,                        -- User who reviewed this version
            rejected_by TEXT,                             -- User who rejected this version
            rejected_at TEXT,                             -- When rejection occurred
            rejection_reason TEXT,                        -- Reason for rejection
            
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
            updated_at TEXT,                               -- When version was last updated
            created_by TEXT NOT NULL,                     -- User who created this version
            updated_by TEXT,                               -- User who last updated this version
            created_from TEXT,                            -- Source of version creation (manual, auto, system)
            review_timestamp TEXT,                        -- When version was reviewed
            published_at TEXT,                            -- When version was published
            
            -- Soft Delete Support
            is_deleted BOOLEAN DEFAULT FALSE,              -- Soft delete flag
            deleted_at TEXT,                               -- When version was soft deleted
            deleted_by TEXT,                               -- User who soft deleted the version
            
            -- Additional Metadata
            tags JSON DEFAULT '{}',                        -- Version tags (JSON object)
            metadata JSON DEFAULT '{}',                    -- Additional metadata (JSON object)
            
            -- Environment Management
            deployment_environment TEXT DEFAULT 'development', -- Current deployment environment
            deployment_status TEXT DEFAULT 'not_deployed' CHECK (deployment_status IN ('not_deployed', 'deployed', 'failed', 'rolling_back')),
            is_deployed BOOLEAN DEFAULT FALSE,            -- Whether this version is deployed
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
            is_high_security BOOLEAN DEFAULT FALSE,        -- Whether this version has high security level
            encryption_status TEXT DEFAULT 'none' CHECK (encryption_status IN ('none', 'encrypted', 'encryption_failed')),
            is_encrypted BOOLEAN DEFAULT FALSE,            -- Whether this version data is encrypted
            
            -- Reporting & Compliance
            compliance_status JSON DEFAULT '{}',           -- JSON: compliance data
            audit_trail_data JSON DEFAULT '{}',            -- JSON: audit trail
            reporting_metadata JSON DEFAULT '{}',          -- JSON: reporting metadata
            
            -- Version Lifecycle Management
            archive_status TEXT DEFAULT 'active' CHECK (archive_status IN ('active', 'archived', 'restored')),
            is_archived BOOLEAN DEFAULT FALSE,            -- Whether this version is archived
            archive_timestamp TEXT,                        -- When version was archived
            archive_reason TEXT,                           -- Reason for archiving
            restore_timestamp TEXT                          -- When version was restored
            
            -- Constraints - DISABLED FOR TESTING
            -- FOREIGN KEY (certificate_id) REFERENCES certificates_registry(certificate_id) ON DELETE CASCADE,
            -- FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE CASCADE,
            -- FOREIGN KEY (approved_by) REFERENCES users(user_id) ON DELETE SET NULL,
            -- FOREIGN KEY (reviewer_user_id) REFERENCES users(user_id) ON DELETE SET NULL,
            --UNIQUE(certificate_id, version_number)
        )
        """
        
        # Create the table using connection manager
        await self.connection_manager.execute_query(query)
        
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
        
        return await self.create_indexes("certificates_versions", index_queries)
    
    async def _create_certificates_metrics_table(self) -> bool:
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
            
            -- Enterprise Performance Analytics
            performance_trend TEXT DEFAULT 'stable' CHECK (performance_trend IN ('improving', 'stable', 'declining', 'volatile')),
            optimization_suggestions TEXT DEFAULT '{}',   -- JSON object: performance optimization suggestions
            last_optimization_date TEXT,                 -- Last performance optimization date
            sla_compliance_rate REAL DEFAULT 100.0 CHECK (sla_compliance_rate >= 0.0 AND sla_compliance_rate <= 100.0),
            resource_utilization_rate REAL DEFAULT 0.0 CHECK (resource_utilization_rate >= 0.0 AND resource_utilization_rate <= 100.0),
            scalability_score REAL DEFAULT 0.0 CHECK (scalability_score >= 0.0 AND scalability_score <= 100.0),
            
            -- Timestamps & Audit
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            last_metric_update TEXT,                     -- Last time metrics were updated
            metrics_collection_frequency TEXT DEFAULT 'daily', -- How often metrics are collected
            
            -- Soft Delete Support
            is_deleted BOOLEAN DEFAULT FALSE,              -- Soft delete flag
            deleted_at TEXT,                               -- When metrics were soft deleted
            deleted_by TEXT                               -- User who soft deleted the metrics
            
            -- Constraints - DISABLED FOR TESTING
            -- FOREIGN KEY (certificate_id) REFERENCES certificates_registry(certificate_id) ON DELETE CASCADE
        )
        """
        
        # Create the table using connection manager
        await self.connection_manager.execute_query(query)
        
        # Create indexes for this table
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_certificate_metrics_cert_id ON certificates_metrics(certificate_id);",
            "CREATE INDEX IF NOT EXISTS idx_certificate_metrics_created_at ON certificates_metrics(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_certificate_metrics_quality ON certificates_metrics(data_quality_score);",
            "CREATE INDEX IF NOT EXISTS idx_certificate_metrics_performance ON certificates_metrics(generation_time_ms);",
            "CREATE INDEX IF NOT EXISTS idx_certificate_metrics_usage ON certificates_metrics(view_count, export_count);",
            "CREATE INDEX IF NOT EXISTS idx_certificate_metrics_performance_trend ON certificates_metrics(performance_trend);",
            "CREATE INDEX IF NOT EXISTS idx_certificate_metrics_sla ON certificates_metrics(sla_compliance_rate);",
            "CREATE INDEX IF NOT EXISTS idx_certificate_metrics_scalability ON certificates_metrics(scalability_score);"
        ]
        
        return await self.create_indexes("certificates_metrics", index_queries)
    
    async def create_tables(self) -> bool:
        """Create all tables for the certificate manager module."""
        try:
            logger.info("🔐 Creating Certificate Manager Module Tables...")
            
            # Create tables in dependency order
            tables_created = []
            
            # 1. Create certificates registry table
            if await self._create_certificates_registry_table():
                tables_created.append("certificates_registry")
            else:
                logger.error("Failed to create certificates_registry table")
                return False
            
            # 2. Create certificates versions table
            if await self._create_certificates_versions_table():
                tables_created.append("certificates_versions")
            else:
                logger.error("Failed to create certificates_versions table")
                return False
            
            # 3. Create certificates metrics table
            if await self._create_certificates_metrics_table():
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

    async def initialize(self) -> bool:
        """Initialize the Certificate Manager schema with enhanced features."""
        try:
            # Call parent initialization
            if not await super().initialize():
                return False
            
            # Create core tables
            if not await self._create_core_tables():
                return False
            
            logger.info("✅ Certificate Manager Schema initialized with enhanced features")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Certificate Manager Schema: {e}")
            return False

    # Core Helper Methods

    async def _create_core_tables(self) -> bool:
        """Create all core Certificate Manager tables."""
        try:
            # Create core tables
            if not await self._create_certificates_registry_table():
                return False
            
            if not await self._create_certificates_versions_table():
                return False
            
            if not await self._create_certificates_metrics_table():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create core tables: {e}")
            return False
