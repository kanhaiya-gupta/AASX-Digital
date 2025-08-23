"""
Business Domain Schema Module
============================

Manages Business Domain database tables for the AASX Digital Twin Framework.
Provides comprehensive user management, organization management, use case definitions,
project management, file management, and business entity relationships.
"""

import logging
from typing import List, Dict, Any
from ..base_schema import BaseSchemaModule

logger = logging.getLogger(__name__)


class BusinessDomainSchema(BaseSchemaModule):
    """
    Business Domain Schema Module

    Manages the following tables:
    - users: User management & authentication
    - organizations: Organization management and hierarchy
    - use_cases: Use case definitions and governance
    - projects: Project management and lifecycle
    - files: File storage, metadata, and versioning
    - project_use_case_links: Project-use case relationships
    """

    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.module_name = "business_domain"

    def get_module_description(self) -> str:
        """Get human-readable description of this module."""
        return "Core business domain tables for organizations, use cases, projects, and files"

    def get_table_names(self) -> List[str]:
        """Get list of table names managed by this module."""
        return ["organizations", "use_cases", "projects", "files", "project_use_case_links"]

    def create_tables(self) -> bool:
        """Create all business domain tables"""
        success = True
        
        # Create tables in dependency order
        success &= self._create_organizations_table()
        success &= self._create_use_cases_table()
        success &= self._create_projects_table()
        success &= self._create_files_table()
        success &= self._create_project_use_case_links_table()
        
        return success

    def _create_organizations_table(self) -> bool:
        """Create the organizations table with world-class tracing capabilities."""
        query = """
            CREATE TABLE IF NOT EXISTS organizations (
                org_id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                domain TEXT,
                contact_email TEXT,
                contact_phone TEXT,
                address TEXT,
                is_active BOOLEAN DEFAULT 1,
                subscription_tier TEXT DEFAULT 'basic',
                max_users INTEGER DEFAULT 10,
                max_projects INTEGER DEFAULT 100,
                max_storage_gb INTEGER DEFAULT 10,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                
                -- Audit & Compliance Fields
                audit_log_enabled BOOLEAN DEFAULT TRUE,
                audit_retention_days INTEGER DEFAULT 2555,
                compliance_framework TEXT DEFAULT 'ISO27001',
                compliance_status TEXT DEFAULT 'pending',
                last_compliance_audit TEXT,
                next_compliance_audit TEXT,
                compliance_score REAL DEFAULT 0.0,
                
                -- Security & Access Control
                security_level TEXT DEFAULT 'standard',
                mfa_required BOOLEAN DEFAULT FALSE,
                session_timeout_minutes INTEGER DEFAULT 480,
                max_failed_logins INTEGER DEFAULT 5,
                ip_whitelist TEXT DEFAULT '[]',
                vpn_required BOOLEAN DEFAULT FALSE,
                
                -- Data Governance
                data_classification TEXT DEFAULT 'internal',
                data_retention_policy TEXT DEFAULT '{}',
                gdpr_compliant BOOLEAN DEFAULT FALSE,
                data_processing_consent BOOLEAN DEFAULT FALSE,
                data_export_restrictions TEXT DEFAULT '[]',
                
                -- Operational Monitoring
                operational_status TEXT DEFAULT 'active',
                health_score REAL DEFAULT 100.0,
                last_health_check TEXT,
                uptime_percentage REAL DEFAULT 99.9,
                performance_metrics TEXT DEFAULT '{}',
                
                -- Business Intelligence
                industry_sector TEXT,
                company_size TEXT DEFAULT 'smb',
                annual_revenue_range TEXT DEFAULT '1M-10M',
                customer_count INTEGER DEFAULT 0,
                partner_ecosystem TEXT DEFAULT '[]',
                
                -- Advanced Tracing
                trace_id TEXT,
                correlation_id TEXT,
                parent_org_id TEXT,
                subsidiary_count INTEGER DEFAULT 0,
                integration_partners TEXT DEFAULT '[]',
                api_usage_limits TEXT DEFAULT '{}',
                
                FOREIGN KEY (parent_org_id) REFERENCES organizations (org_id) ON DELETE SET NULL
            )
        """

        # Create the table
        if not self.create_table("organizations", query):
            return False

        # Create indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_organizations_name ON organizations (name)",
            "CREATE INDEX IF NOT EXISTS idx_organizations_domain ON organizations (domain)",
            "CREATE INDEX IF NOT EXISTS idx_organizations_is_active ON organizations (is_active)",
            "CREATE INDEX IF NOT EXISTS idx_organizations_subscription_tier ON organizations (subscription_tier)",
            "CREATE INDEX IF NOT EXISTS idx_organizations_compliance_status ON organizations (compliance_status)",
            "CREATE INDEX IF NOT EXISTS idx_organizations_security_level ON organizations (security_level)",
            "CREATE INDEX IF NOT EXISTS idx_organizations_operational_status ON organizations (operational_status)",
            "CREATE INDEX IF NOT EXISTS idx_organizations_industry_sector ON organizations (industry_sector)",
            "CREATE INDEX IF NOT EXISTS idx_organizations_company_size ON organizations (company_size)",
            "CREATE INDEX IF NOT EXISTS idx_organizations_parent_org_id ON organizations (parent_org_id)",
            "CREATE INDEX IF NOT EXISTS idx_organizations_created_at ON organizations (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_organizations_updated_at ON organizations (updated_at)"
        ]

        return self.create_indexes("organizations", index_queries)

    def _create_use_cases_table(self) -> bool:
        """Create the use_cases table with comprehensive governance fields."""
        query = """
            CREATE TABLE IF NOT EXISTS use_cases (
                use_case_id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                category TEXT DEFAULT 'general',
                is_active BOOLEAN DEFAULT 1,
                metadata TEXT DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                created_by TEXT,
                
                -- Data Governance Fields
                data_domain TEXT DEFAULT 'general' CHECK (data_domain IN ('general', 'thermal', 'structural', 'fluid_dynamics', 'electrical', 'mechanical', 'chemical', 'biological', 'environmental', 'other')),
                business_criticality TEXT DEFAULT 'low' CHECK (business_criticality IN ('low', 'medium', 'high', 'critical')),
                data_volume_estimate TEXT DEFAULT 'unknown' CHECK (data_volume_estimate IN ('small', 'medium', 'large', 'enterprise')),
                update_frequency TEXT DEFAULT 'on_demand' CHECK (update_frequency IN ('real_time', 'hourly', 'daily', 'weekly', 'monthly', 'on_demand')),
                retention_policy TEXT DEFAULT '{}', -- JSON: retention rules and policies
                compliance_requirements TEXT DEFAULT '{}', -- JSON: compliance needs and regulations
                data_owners TEXT DEFAULT '{}', -- JSON: ownership information and responsibilities
                stakeholders TEXT DEFAULT '{}', -- JSON: stakeholder details and interests
                
                -- Foreign key constraints
                FOREIGN KEY (created_by) REFERENCES users (user_id) ON DELETE SET NULL
            )
        """

        # Create the table
        if not self.create_table("use_cases", query):
            return False

        # Create indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_use_cases_name ON use_cases (name)",
            "CREATE INDEX IF NOT EXISTS idx_use_cases_category ON use_cases (category)",
            "CREATE INDEX IF NOT EXISTS idx_use_cases_is_active ON use_cases (is_active)",
            "CREATE INDEX IF NOT EXISTS idx_use_cases_data_domain ON use_cases (data_domain)",
            "CREATE INDEX IF NOT EXISTS idx_use_cases_business_criticality ON use_cases (business_criticality)",
            "CREATE INDEX IF NOT EXISTS idx_use_cases_data_volume_estimate ON use_cases (data_volume_estimate)",
            "CREATE INDEX IF NOT EXISTS idx_use_cases_update_frequency ON use_cases (update_frequency)",
            "CREATE INDEX IF NOT EXISTS idx_use_cases_created_by ON use_cases (created_by)",
            "CREATE INDEX IF NOT EXISTS idx_use_cases_created_at ON use_cases (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_use_cases_updated_at ON use_cases (updated_at)"
        ]

        return self.create_indexes("use_cases", index_queries)

    def _create_projects_table(self) -> bool:
        """Create the projects table with comprehensive governance fields."""
        query = """
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                tags TEXT DEFAULT '[]',
                file_count INTEGER DEFAULT 0,
                total_size INTEGER DEFAULT 0,
                is_public BOOLEAN DEFAULT 0,
                access_level TEXT DEFAULT 'private',
                user_id TEXT,
                org_id TEXT,
                metadata TEXT DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                
                -- Project Governance Fields
                project_phase TEXT DEFAULT 'planning' CHECK (project_phase IN ('planning', 'development', 'testing', 'deployment', 'maintenance', 'completed', 'on_hold')),
                priority_level TEXT DEFAULT 'medium' CHECK (priority_level IN ('low', 'medium', 'high', 'critical')),
                estimated_completion TEXT, -- Target completion date
                actual_completion TEXT, -- Actual completion date
                budget_allocation REAL DEFAULT 0.0, -- Budget amount
                resource_requirements TEXT DEFAULT '{}', -- JSON: resource needs and allocation
                dependencies TEXT DEFAULT '[]', -- JSON: project dependencies and relationships
                risk_mitigation TEXT DEFAULT '{}', -- JSON: risk strategies and mitigation plans
                
                -- Foreign key constraints
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE SET NULL,
                FOREIGN KEY (org_id) REFERENCES organizations (org_id) ON DELETE SET NULL
            )
        """

        # Create the table
        if not self.create_table("projects", query):
            return False

        # Create indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_projects_name ON projects (name)",
            "CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_projects_org_id ON projects (org_id)",
            "CREATE INDEX IF NOT EXISTS idx_projects_is_public ON projects (is_public)",
            "CREATE INDEX IF NOT EXISTS idx_projects_access_level ON projects (access_level)",
            "CREATE INDEX IF NOT EXISTS idx_projects_project_phase ON projects (project_phase)",
            "CREATE INDEX IF NOT EXISTS idx_projects_priority_level ON projects (priority_level)",
            "CREATE INDEX IF NOT EXISTS idx_projects_estimated_completion ON projects (estimated_completion)",
            "CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_projects_updated_at ON projects (updated_at)"
        ]

        return self.create_indexes("projects", index_queries)

    def _create_files_table(self) -> bool:
        """Create the files table with comprehensive file management fields."""
        query = """
            CREATE TABLE IF NOT EXISTS files (
                file_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                project_id TEXT NOT NULL,
                filepath TEXT NOT NULL,
                size INTEGER DEFAULT 0,
                description TEXT,
                status TEXT DEFAULT 'not_processed',
                file_type TEXT,
                file_type_description TEXT,
                source_type TEXT DEFAULT 'manual_upload' CHECK (source_type IN ('manual_upload', 'url_upload')),
                source_url TEXT,
                user_id TEXT,
                upload_date TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                
                -- Additional file management fields
                org_id TEXT,
                use_case_id TEXT,
                job_type TEXT,
                tags TEXT,
                metadata TEXT,
                
                FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE SET NULL,
                FOREIGN KEY (org_id) REFERENCES organizations (org_id) ON DELETE SET NULL,
                FOREIGN KEY (use_case_id) REFERENCES use_cases (use_case_id) ON DELETE SET NULL
            )
        """

        # Create the table
        if not self.create_table("files", query):
            return False

        # Create indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_files_project_id ON files (project_id)",
            "CREATE INDEX IF NOT EXISTS idx_files_user_id ON files (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_files_status ON files (status)",
            "CREATE INDEX IF NOT EXISTS idx_files_file_type ON files (file_type)",
            "CREATE INDEX IF NOT EXISTS idx_files_source_type ON files (source_type)",
            "CREATE INDEX IF NOT EXISTS idx_files_upload_date ON files (upload_date)",
            "CREATE INDEX IF NOT EXISTS idx_files_org_id ON files (org_id)",
            "CREATE INDEX IF NOT EXISTS idx_files_use_case_id ON files (use_case_id)",
            "CREATE INDEX IF NOT EXISTS idx_files_filename ON files (filename)",
            "CREATE INDEX IF NOT EXISTS idx_files_created_at ON files (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_files_updated_at ON files (updated_at)"
        ]

        return self.create_indexes("files", index_queries)

    def _create_project_use_case_links_table(self) -> bool:
        """Create the project_use_case_links table."""
        query = """
            CREATE TABLE IF NOT EXISTS project_use_case_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                use_case_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE,
                FOREIGN KEY (use_case_id) REFERENCES use_cases (use_case_id) ON DELETE CASCADE,
                UNIQUE(project_id, use_case_id)
            )
        """

        # Create the table
        if not self.create_table("project_use_case_links", query):
            return False

        # Create indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_project_use_case_links_project_id ON project_use_case_links (project_id)",
            "CREATE INDEX IF NOT EXISTS idx_project_use_case_links_use_case_id ON project_use_case_links (use_case_id)",
            "CREATE INDEX IF NOT EXISTS idx_project_use_case_links_created_at ON project_use_case_links (created_at)"
        ]

        return self.create_indexes("project_use_case_links", index_queries)
