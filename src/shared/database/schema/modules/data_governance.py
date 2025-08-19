"""
Data Governance Schema Module
============================

Manages Data Governance database tables for the AASX Digital Twin Framework.
Provides comprehensive data lineage tracking, quality monitoring, change management,
versioning, and policy enforcement for enterprise-grade data governance.
"""

import logging
from typing import List, Dict, Any
from ..base_schema import BaseSchemaModule

logger = logging.getLogger(__name__)


class DataGovernanceSchema(BaseSchemaModule):
    """
    Data Governance Schema Module

    Manages the following tables:
    - data_lineage: Data lineage & transformation tracking
    - data_quality_metrics: Data quality monitoring & scoring
    - change_requests: Change management workflows
    - data_versions: Data versioning & history
    - governance_policies: Policy enforcement & compliance
    """

    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.module_name = "data_governance"

    def get_module_description(self) -> str:
        """Get human-readable description of this module."""
        return "Data Governance module for comprehensive data lineage, quality monitoring, change management, versioning, and policy enforcement"

    def get_table_names(self) -> List[str]:
        """Get list of table names managed by this module."""
        return ["data_lineage", "data_quality_metrics", "change_requests", "data_versions", "governance_policies"]

    def create_tables(self) -> bool:
        """
        Create all Data Governance tables.

        Returns:
            bool: True if all tables created successfully, False otherwise
        """
        logger.info("🏛️ Creating Data Governance Module Tables...")

        # Create tables in dependency order
        tables_created = []

        # 1. Create Data Lineage Table (no dependencies)
        if self._create_data_lineage_table():
            tables_created.append("data_lineage")
        else:
            logger.error("Failed to create data_lineage table")
            return False

        # 2. Create Data Quality Metrics Table (no dependencies)
        if self._create_data_quality_metrics_table():
            tables_created.append("data_quality_metrics")
        else:
            logger.error("Failed to create data_quality_metrics table")
            return False

        # 3. Create Change Requests Table (no dependencies)
        if self._create_change_requests_table():
            tables_created.append("change_requests")
        else:
            logger.error("Failed to create change_requests table")
            return False

        # 4. Create Data Versions Table (depends on change_requests)
        if self._create_data_versions_table():
            tables_created.append("data_versions")
        else:
            logger.error("Failed to create data_versions table")
            return False

        # 5. Create Governance Policies Table (no dependencies)
        if self._create_governance_policies_table():
            tables_created.append("governance_policies")
        else:
            logger.error("Failed to create governance_policies table")
            return False

        logger.info(f"✅ Data Governance Module: Created {len(tables_created)} tables successfully")
        return True

    def _create_data_lineage_table(self) -> bool:
        """Create the data_lineage table for tracking data relationships and transformations."""
        query = """
            CREATE TABLE IF NOT EXISTS data_lineage (
                lineage_id TEXT PRIMARY KEY,
                source_entity_type TEXT NOT NULL CHECK (source_entity_type IN ('file', 'project', 'use_case', 'user', 'organization')),
                source_entity_id TEXT NOT NULL,
                target_entity_type TEXT NOT NULL CHECK (target_entity_type IN ('file', 'project', 'use_case', 'user', 'organization')),
                target_entity_id TEXT NOT NULL,
                relationship_type TEXT NOT NULL CHECK (relationship_type IN ('derived_from', 'depends_on', 'contains', 'belongs_to', 'processed_by', 'owned_by')),
                lineage_depth INTEGER DEFAULT 1, -- How many levels deep this relationship goes
                confidence_score REAL DEFAULT 1.0, -- Confidence in this lineage relationship (0.0-1.0)
                transformation_type TEXT DEFAULT 'none' CHECK (transformation_type IN ('none', 'extraction', 'processing', 'aggregation', 'filtering', 'enrichment')),
                transformation_details TEXT DEFAULT '{}', -- JSON: details about the transformation
                lineage_metadata TEXT DEFAULT '{}', -- JSON: additional lineage information
                is_active BOOLEAN DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                
                -- Performance and tracking
                last_accessed TEXT,
                access_count INTEGER DEFAULT 0,
                validation_status TEXT DEFAULT 'pending' CHECK (validation_status IN ('pending', 'validated', 'invalid', 'needs_review')),
                
                -- Enhanced Lineage Features (Phase 2)
                transformation_steps TEXT DEFAULT '[]', -- JSON: step-by-step transformation process
                data_quality_impact REAL DEFAULT 0.0, -- Impact on data quality scores
                business_value_score REAL DEFAULT 0.0, -- Business value of this lineage
                lineage_complexity TEXT DEFAULT 'simple' CHECK (lineage_complexity IN ('simple', 'moderate', 'complex')),
                validation_rules TEXT DEFAULT '[]', -- JSON: validation rules applied
                lineage_confidence_factors TEXT DEFAULT '{}', -- JSON: factors affecting confidence
                lineage_impact_analysis TEXT DEFAULT '{}', -- JSON: impact analysis results
                
                -- Dependency Management (Phase 2)
                dependency_level TEXT DEFAULT 'direct' CHECK (dependency_level IN ('direct', 'indirect', 'transitive')),
                dependency_criticality TEXT DEFAULT 'low' CHECK (dependency_criticality IN ('low', 'medium', 'high', 'critical')),
                dependency_risk_score REAL DEFAULT 0.0, -- Risk assessment score
                dependency_mitigation TEXT DEFAULT '{}', -- JSON: risk mitigation strategies
                dependency_alerts TEXT DEFAULT '[]', -- JSON: alert configurations
                dependency_visualization TEXT DEFAULT '{}' -- JSON: visualization preferences
            )
        """

        # Create the table
        if not self.create_table("data_lineage", query):
            return False

        # Create indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_source ON data_lineage (source_entity_type, source_entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_target ON data_lineage (target_entity_type, target_entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_relationship ON data_lineage (relationship_type)",
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_depth ON data_lineage (lineage_depth)",
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_confidence ON data_lineage (confidence_score)",
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_validation ON data_lineage (validation_status)",
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_transformation ON data_lineage (transformation_type)",
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_complexity ON data_lineage (lineage_complexity)",
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_quality_impact ON data_lineage (data_quality_impact)",
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_business_value ON data_lineage (business_value_score)",
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_dependency_level ON data_lineage (dependency_level)",
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_dependency_criticality ON data_lineage (dependency_criticality)",
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_dependency_risk ON data_lineage (dependency_risk_score)",
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_created_at ON data_lineage (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_updated_at ON data_lineage (updated_at)"
        ]

        return self.create_indexes("data_lineage", index_queries)

    def _create_data_quality_metrics_table(self) -> bool:
        """Create the data_quality_metrics table for comprehensive quality monitoring."""
        query = """
            CREATE TABLE IF NOT EXISTS data_quality_metrics (
                quality_id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL CHECK (entity_type IN ('file', 'project', 'use_case', 'user', 'organization')),
                entity_id TEXT NOT NULL,
                metric_date TEXT NOT NULL, -- Date when metrics were calculated
                
                -- Quality Dimensions (0-100 scores)
                accuracy_score REAL DEFAULT 0.0, -- Data accuracy score
                completeness_score REAL DEFAULT 0.0, -- Data completeness score
                consistency_score REAL DEFAULT 0.0, -- Data consistency score
                timeliness_score REAL DEFAULT 0.0, -- Data timeliness score
                validity_score REAL DEFAULT 0.0, -- Data validity score
                uniqueness_score REAL DEFAULT 0.0, -- Data uniqueness score
                
                -- Overall Quality Score
                overall_quality_score REAL DEFAULT 0.0, -- Weighted average of all dimensions
                
                -- Quality Thresholds and Status
                quality_threshold REAL DEFAULT 70.0, -- Minimum acceptable quality score
                quality_status TEXT DEFAULT 'unknown' CHECK (quality_status IN ('excellent', 'good', 'acceptable', 'poor', 'critical', 'unknown')),
                
                -- Quality Issues and Details
                quality_issues TEXT DEFAULT '[]', -- JSON: list of quality issues found
                quality_improvements TEXT DEFAULT '[]', -- JSON: suggested improvements
                
                -- Metadata and Tracking
                quality_metadata TEXT DEFAULT '{}', -- JSON: additional quality information
                calculated_by TEXT, -- User who calculated these metrics
                calculation_method TEXT DEFAULT 'automated', -- How metrics were calculated
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                
                -- Performance tracking
                last_quality_check TEXT,
                quality_trend TEXT DEFAULT '{}' -- JSON: quality trend over time
            )
        """

        # Create the table
        if not self.create_table("data_quality_metrics", query):
            return False

        # Create indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_data_quality_metrics_entity ON data_quality_metrics (entity_type, entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_data_quality_metrics_date ON data_quality_metrics (metric_date)",
            "CREATE INDEX IF NOT EXISTS idx_data_quality_metrics_score ON data_quality_metrics (overall_quality_score)",
            "CREATE INDEX IF NOT EXISTS idx_data_quality_metrics_status ON data_quality_metrics (quality_status)",
            "CREATE INDEX IF NOT EXISTS idx_data_quality_metrics_threshold ON data_quality_metrics (quality_threshold)",
            "CREATE INDEX IF NOT EXISTS idx_data_quality_metrics_calculated_by ON data_quality_metrics (calculated_by)",
            "CREATE INDEX IF NOT EXISTS idx_data_quality_metrics_created_at ON data_quality_metrics (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_data_quality_metrics_updated_at ON data_quality_metrics (updated_at)"
        ]

        return self.create_indexes("data_quality_metrics", index_queries)

    def _create_change_requests_table(self) -> bool:
        """Create the change_requests table for managing data change workflows."""
        query = """
            CREATE TABLE IF NOT EXISTS change_requests (
                request_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                change_type TEXT NOT NULL CHECK (change_type IN ('create', 'update', 'delete', 'restore', 'bulk_update', 'schema_change')),
                entity_type TEXT NOT NULL CHECK (entity_type IN ('file', 'project', 'use_case', 'user', 'organization', 'data_lineage', 'quality_metrics')),
                entity_id TEXT,
                requested_by TEXT NOT NULL,
                requested_at TEXT NOT NULL,
                
                -- Change Details
                change_details TEXT DEFAULT '{}', -- JSON: specific changes requested
                current_state TEXT DEFAULT '{}', -- JSON: current state before change
                proposed_state TEXT DEFAULT '{}', -- JSON: proposed state after change
                impact_analysis TEXT DEFAULT '{}', -- JSON: impact assessment
                
                -- Workflow Status
                status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'under_review', 'approved', 'rejected', 'in_progress', 'completed', 'cancelled')),
                priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
                urgency TEXT DEFAULT 'normal' CHECK (urgency IN ('normal', 'high', 'urgent', 'emergency')),
                
                -- Approval Process
                assigned_to TEXT, -- User assigned to review/approve
                assigned_at TEXT,
                review_deadline TEXT,
                approval_required BOOLEAN DEFAULT TRUE,
                approval_chain TEXT DEFAULT '[]', -- JSON: approval hierarchy
                
                -- Review & Approval
                review_notes TEXT,
                review_date TEXT,
                reviewed_by TEXT,
                approval_date TEXT,
                approved_by TEXT,
                rejection_reason TEXT,
                
                -- Implementation
                implementation_notes TEXT,
                implementation_date TEXT,
                implemented_by TEXT,
                rollback_plan TEXT DEFAULT '{}', -- JSON: rollback strategy
                
                -- Metadata & Tracking
                tags TEXT DEFAULT '[]', -- JSON: tags for categorization
                metadata TEXT DEFAULT '{}', -- JSON: additional information
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """

        # Create the table
        if not self.create_table("change_requests", query):
            return False

        # Create indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_change_requests_status ON change_requests (status)",
            "CREATE INDEX IF NOT EXISTS idx_change_requests_type ON change_requests (change_type)",
            "CREATE INDEX IF NOT EXISTS idx_change_requests_entity ON change_requests (entity_type, entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_change_requests_requested_by ON change_requests (requested_by)",
            "CREATE INDEX IF NOT EXISTS idx_change_requests_assigned_to ON change_requests (assigned_to)",
            "CREATE INDEX IF NOT EXISTS idx_change_requests_priority ON change_requests (priority)",
            "CREATE INDEX IF NOT EXISTS idx_change_requests_requested_at ON change_requests (requested_at)",
            "CREATE INDEX IF NOT EXISTS idx_change_requests_deadline ON change_requests (review_deadline)",
            "CREATE INDEX IF NOT EXISTS idx_change_requests_urgency ON change_requests (urgency)",
            "CREATE INDEX IF NOT EXISTS idx_change_requests_created_at ON change_requests (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_change_requests_updated_at ON change_requests (updated_at)"
        ]

        return self.create_indexes("change_requests", index_queries)

    def _create_data_versions_table(self) -> bool:
        """Create the data_versions table for tracking data versioning and changes."""
        query = """
            CREATE TABLE IF NOT EXISTS data_versions (
                version_id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL CHECK (entity_type IN ('file', 'project', 'use_case', 'user', 'organization', 'data_lineage', 'quality_metrics')),
                entity_id TEXT NOT NULL,
                version_number TEXT NOT NULL, -- Semantic versioning (e.g., 1.0.0, 1.1.0)
                version_type TEXT NOT NULL CHECK (version_type IN ('major', 'minor', 'patch', 'hotfix')),
                
                -- Version Content
                previous_version_id TEXT, -- Link to previous version
                change_summary TEXT, -- Summary of changes in this version
                change_details TEXT DEFAULT '{}', -- JSON: detailed change information
                data_snapshot TEXT DEFAULT '{}', -- JSON: complete data state at this version
                
                -- Change Information
                change_type TEXT NOT NULL CHECK (change_type IN ('create', 'update', 'delete', 'restore')),
                change_reason TEXT, -- Why this change was made
                change_request_id TEXT, -- Link to change request if applicable
                
                -- Version Metadata
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                is_current BOOLEAN DEFAULT FALSE, -- Is this the current active version
                is_deprecated BOOLEAN DEFAULT FALSE, -- Is this version deprecated
                deprecation_date TEXT,
                deprecation_reason TEXT,
                
                -- Performance & Access
                last_accessed TEXT,
                access_count INTEGER DEFAULT 0,
                storage_size INTEGER DEFAULT 0, -- Size of version data in bytes
                
                -- Compliance & Audit
                compliance_status TEXT DEFAULT 'unknown' CHECK (compliance_status IN ('compliant', 'non_compliant', 'pending_review', 'unknown')),
                audit_notes TEXT,
                retention_expiry TEXT -- When this version should be archived/deleted
            )
        """

        # Create the table
        if not self.create_table("data_versions", query):
            return False

        # Create indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_data_versions_entity ON data_versions (entity_type, entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_data_versions_version ON data_versions (version_number)",
            "CREATE INDEX IF NOT EXISTS idx_data_versions_current ON data_versions (is_current)",
            "CREATE INDEX IF NOT EXISTS idx_data_versions_type ON data_versions (version_type)",
            "CREATE INDEX IF NOT EXISTS idx_data_versions_created_at ON data_versions (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_data_versions_change_type ON data_versions (change_type)",
            "CREATE INDEX IF NOT EXISTS idx_data_versions_compliance ON data_versions (compliance_status)",
            "CREATE INDEX IF NOT EXISTS idx_data_versions_previous ON data_versions (previous_version_id)",
            "CREATE INDEX IF NOT EXISTS idx_data_versions_change_request ON data_versions (change_request_id)",
            "CREATE INDEX IF NOT EXISTS idx_data_versions_created_by ON data_versions (created_by)"
        ]

        return self.create_indexes("data_versions", index_queries)

    def _create_governance_policies_table(self) -> bool:
        """Create the governance_policies table for managing data governance policies."""
        query = """
            CREATE TABLE IF NOT EXISTS governance_policies (
                policy_id TEXT PRIMARY KEY,
                policy_name TEXT NOT NULL,
                policy_type TEXT NOT NULL CHECK (policy_type IN ('data_classification', 'access_control', 'retention', 'compliance', 'quality', 'lineage')),
                policy_category TEXT NOT NULL CHECK (policy_category IN ('mandatory', 'recommended', 'optional', 'deprecated')),
                
                -- Policy Content
                policy_description TEXT NOT NULL,
                policy_rules TEXT DEFAULT '{}', -- JSON: specific policy rules
                policy_conditions TEXT DEFAULT '[]', -- JSON: conditions when policy applies
                policy_actions TEXT DEFAULT '[]', -- JSON: actions to take when policy is violated
                
                -- Policy Scope
                applicable_entities TEXT DEFAULT '[]', -- JSON: entity types this policy applies to
                applicable_organizations TEXT DEFAULT '[]', -- JSON: organizations this policy applies to
                applicable_users TEXT DEFAULT '[]', -- JSON: users this policy applies to
                geographic_scope TEXT DEFAULT 'global', -- Geographic scope of policy
                
                -- Policy Enforcement
                enforcement_level TEXT DEFAULT 'monitor' CHECK (enforcement_level IN ('monitor', 'warn', 'block', 'auto_correct')),
                compliance_required BOOLEAN DEFAULT TRUE,
                audit_required BOOLEAN DEFAULT TRUE,
                auto_remediation BOOLEAN DEFAULT FALSE,
                
                -- Policy Status
                status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'suspended', 'deprecated', 'archived')),
                effective_date TEXT,
                expiry_date TEXT,
                review_frequency TEXT DEFAULT 'monthly', -- How often to review policy
                
                -- Policy Ownership
                policy_owner TEXT NOT NULL, -- User responsible for policy
                policy_stewards TEXT DEFAULT '[]', -- JSON: users who can modify policy
                approval_required BOOLEAN DEFAULT TRUE,
                approved_by TEXT,
                approval_date TEXT,
                
                -- Policy Metrics
                compliance_rate REAL DEFAULT 0.0, -- Current compliance rate
                violation_count INTEGER DEFAULT 0, -- Number of violations
                last_compliance_check TEXT,
                compliance_trend TEXT DEFAULT '{}', -- JSON: compliance trend over time
                
                -- Metadata
                tags TEXT DEFAULT '[]', -- JSON: tags for categorization
                metadata TEXT DEFAULT '{}', -- JSON: additional information
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """

        # Create the table
        if not self.create_table("governance_policies", query):
            return False

        # Create indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_governance_policies_type ON governance_policies (policy_type)",
            "CREATE INDEX IF NOT EXISTS idx_governance_policies_category ON governance_policies (policy_category)",
            "CREATE INDEX IF NOT EXISTS idx_governance_policies_status ON governance_policies (status)",
            "CREATE INDEX IF NOT EXISTS idx_governance_policies_enforcement ON governance_policies (enforcement_level)",
            "CREATE INDEX IF NOT EXISTS idx_governance_policies_owner ON governance_policies (policy_owner)",
            "CREATE INDEX IF NOT EXISTS idx_governance_policies_effective_date ON governance_policies (effective_date)",
            "CREATE INDEX IF NOT EXISTS idx_governance_policies_compliance ON governance_policies (compliance_rate)",
            "CREATE INDEX IF NOT EXISTS idx_governance_policies_entities ON governance_policies (applicable_entities)",
            "CREATE INDEX IF NOT EXISTS idx_governance_policies_approved_by ON governance_policies (approved_by)",
            "CREATE INDEX IF NOT EXISTS idx_governance_policies_created_at ON governance_policies (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_governance_policies_updated_at ON governance_policies (updated_at)"
        ]

        return self.create_indexes("governance_policies", index_queries)
