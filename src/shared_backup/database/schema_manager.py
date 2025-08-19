"""
Database Schema Manager
======================

Handles database schema creation, migration, and management.

ARCHITECTURE OVERVIEW:
=====================

This schema manager implements a modular, layered architecture designed for enterprise-grade
data management with clear separation of concerns:

LAYER 1: CORE SYSTEM (Foundation)
---------------------------------
- organizations: Organization management and hierarchy
- users: User authentication, authorization, and consent management

LAYER 2: BUSINESS DOMAIN (Business Logic)
-----------------------------------------
- use_cases: Business use case definitions
- projects: Project management and lifecycle
- files: File storage, metadata, and versioning
- project_use_case_links: Business entity relationships

LAYER 3: SPECIALIZED MODULES (Functional Extensions)
---------------------------------------------------
AASX-ETL MODULE:
- aasx_processing: AASX file processing jobs and status
- aasx_processing_metrics: Processing performance and resource metrics

TWIN REGISTRY MODULE:
- twin_registry: Digital twin registry and metadata
- twin_registry_metrics: Twin performance and operational metrics

LAYER 4: DATA GOVERNANCE (Enterprise Features)
----------------------------------------------
Phase 1: Foundation & Governance
- data_lineage: Data transformation and lineage tracking
- data_quality_metrics: Quality monitoring and scoring

Phase 2: Advanced Governance & Workflows
- change_requests: Change management and approval workflows
- data_versions: Data versioning and historical tracking
- governance_policies: Policy enforcement and compliance

Phase 3: Analytics & Intelligence
- data_usage_analytics: Usage patterns and engagement metrics
- performance_metrics: System and data performance tracking

MODULAR EXTENSION PATTERN:
=========================
Each new module should:
1. Have its own dedicated section in create_tables()
2. Include clear documentation of its purpose
3. Maintain separation from other modules
4. Follow consistent naming conventions
5. Include appropriate indexes and constraints

COMPREHENSIVE MODULE ARCHITECTURE:
==================================
CURRENTLY IMPLEMENTED:
- Core System: Foundation tables
- Business Domain: Business logic tables
- AASX-ETL: AASX file processing and transformation
- Twin Registry: Digital twin management
- Data Management: Governance, quality, and compliance

PLANNED FUTURE MODULES:
- Data Processing: Advanced data transformation pipelines
- Management: System administration and control
- AI/RAG: Artificial Intelligence and Retrieval-Augmented Generation
- Analysis: Advanced analytics and business intelligence
- Knowledge Graph: Knowledge representation and reasoning
- Relationships: Entity relationship management
- Federated Learning: Distributed machine learning
- Collaboration: Team and workflow collaboration
- Physics Modeling: Physical system modeling
- Simulation: Simulation and scenario management
- Certificate Manager: Digital certificate management
- Validation: Data and process validation

DEPENDENCY ORDER:
================
Tables are created in dependency order to ensure foreign key constraints
can be properly established during creation.
"""

import logging
from typing import List, Dict, Any
from pathlib import Path

from .base_manager import BaseDatabaseManager

logger = logging.getLogger(__name__)

class DatabaseSchemaManager:
    """Manages database schema and migrations."""
    
    def __init__(self, db_manager: BaseDatabaseManager):
        self.db_manager = db_manager
    
    def create_tables(self):
        """Create all database tables."""
        logger.info("Creating database tables...")
        
        try:
            # =============================================================================
            # CORE SYSTEM TABLES (Foundation Layer)
            # =============================================================================
            # These tables form the foundation of the entire system
            logger.info("🔧 Creating Core System Tables...")
            self._create_organizations_table()            # Organization management
            self._create_users_table()                    # User management & authentication
            
            # =============================================================================
            # BUSINESS DOMAIN TABLES (Business Logic Layer)
            # =============================================================================
            # Core business entities and their relationships
            logger.info("🏢 Creating Business Domain Tables...")
            self._create_use_cases_table()                # Use case definitions
            self._create_projects_table()                 # Project management
            self._create_files_table()                    # File storage & metadata
            self._create_project_use_case_links_table()   # Project-use case relationships
            
            # =============================================================================
            # WORLD-CLASS DATA MANAGEMENT TABLES (Governance Layer)
            # =============================================================================
            # Enterprise-grade data governance, quality, and compliance
            logger.info("🏛️ Creating Data Management & Governance Tables...")
            
            # Phase 1: Foundation & Governance
            self._create_data_lineage_table()             # Data lineage & transformation tracking
            self._create_data_quality_metrics_table()     # Data quality monitoring & scoring
            
            # Phase 2: Advanced Governance & Workflows
            self._create_change_requests_table()          # Change management workflows
            self._create_data_versions_table()            # Data versioning & history
            self._create_governance_policies_table()      # Policy enforcement & compliance
            
            # Phase 3: Analytics & Intelligence
            self._create_data_usage_analytics_table()     # Usage patterns & engagement metrics
            self._create_performance_metrics_table()      # System & data performance tracking
            
            # =============================================================================
            # AASX-ETL MODULE TABLES (Data Processing Layer)
            # =============================================================================
            # Handles AASX file processing, transformation, and ETL operations
            logger.info("📊 Creating AASX-ETL Module Tables...")
            self._create_aasx_processing_table()          # Main processing jobs
            self._create_aasx_processing_metrics_table()  # Processing performance metrics
            
            # =============================================================================
            # TWIN REGISTRY MODULE TABLES (Digital Twin Management)
            # =============================================================================
            # Manages digital twin lifecycle, relationships, and operations
            logger.info("🤖 Creating Twin Registry Module Tables...")
            self._create_twin_registry_table()            # Digital twin registry
            self._create_twin_registry_metrics_table()    # Twin performance metrics
            
            # =============================================================================
            # KNOWLEDGE GRAPH MODULE TABLES (Graph Management & Visualization)
            # =============================================================================
            # Manages knowledge graph lifecycle, Neo4j integration, and analytics
            logger.info("🧠 Creating Knowledge Graph Module Tables...")
            self._create_kg_graph_registry_table()        # Graph registry and metadata
            self._create_kg_graph_metrics_table()         # Graph performance metrics
            
            # =============================================================================
            # AI/RAG MODULE TABLES (Artificial Intelligence & RAG)
            # =============================================================================
            # Manages AI/RAG operations, vector embeddings, and intelligent insights
            logger.info("🤖 Creating AI/RAG Module Tables...")
            self._create_ai_rag_registry_table()          # AI/RAG registry and metadata
            self._create_ai_rag_metrics_table()           # AI/RAG performance metrics
            
            
            # =============================================================================
            # FUTURE MODULE EXTENSIONS (Modular Architecture)
            # =============================================================================
            # Reserved sections for future modules - maintain clear separation
            # Each module should have its own section with clear boundaries
            #- Knowledge Graph: Knowledge representation and reasoning
            #- Federated Learning: Distributed machine learning
            #- Physics Modeling: Physical system modeling
            #- Certificate Manager: Digital certificate management
            # Example future modules (commented out until implemented):
            # self._create_ml_pipeline_tables()           # Machine Learning Pipeline Module
            # self._create_iot_connector_tables()         # IoT Device Connector Module
            # self._create_api_gateway_tables()           # API Gateway & Management Module
            # self._create_workflow_engine_tables()       # Workflow Engine Module
            # self._create_reporting_dashboard_tables()   # Reporting & Dashboard Module
            
            logger.info("✅ All database tables created successfully")
            logger.info("📋 Table Summary:")
            logger.info("   - Core System: 2 tables")
            logger.info("   - Business Domain: 4 tables") 
            logger.info("   - AASX-ETL Module: 2 tables")
            logger.info("   - Twin Registry Module: 2 tables")
            logger.info("   - Knowledge Graph Module: 2 tables")
            logger.info("   - AI/RAG Module: 2 tables")
            logger.info("   - Data Management & Governance: 7 tables")
            logger.info("   - Total: 21 tables")
            
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    def _create_organizations_table(self):
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
        self.db_manager.execute_update(query)
        logger.info("Created comprehensive organizations table with world-class tracing")
    
    def _create_use_cases_table(self):
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
                
                -- Data Governance Fields
                data_domain TEXT DEFAULT 'general' CHECK (data_domain IN ('general', 'thermal', 'structural', 'fluid_dynamics', 'electrical', 'mechanical', 'chemical', 'biological', 'environmental', 'other')),
                business_criticality TEXT DEFAULT 'low' CHECK (business_criticality IN ('low', 'medium', 'high', 'critical')),
                data_volume_estimate TEXT DEFAULT 'unknown' CHECK (data_volume_estimate IN ('small', 'medium', 'large', 'enterprise')),
                update_frequency TEXT DEFAULT 'on_demand' CHECK (update_frequency IN ('real_time', 'hourly', 'daily', 'weekly', 'monthly', 'on_demand')),
                retention_policy TEXT DEFAULT '{}', -- JSON: retention rules and policies
                compliance_requirements TEXT DEFAULT '{}', -- JSON: compliance needs and regulations
                data_owners TEXT DEFAULT '{}', -- JSON: ownership information and responsibilities
                stakeholders TEXT DEFAULT '{}' -- JSON: stakeholder details and interests
            )
        """
        self.db_manager.execute_update(query)
        logger.info("Created comprehensive use_cases table with governance fields")
    
    def _create_projects_table(self):
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
                risk_mitigation TEXT DEFAULT '{}' -- JSON: risk strategies and mitigation plans
            )
        """
        self.db_manager.execute_update(query)
        logger.info("Created comprehensive projects table with governance fields")
    
    def _create_files_table(self):
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
        self.db_manager.execute_update(query)
        logger.info("Created files table")
        
        # Create indexes for the files table
        self.db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_files_project_id ON files (project_id)")
        self.db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_files_user_id ON files (user_id)")
        self.db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_files_status ON files (status)")
        self.db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_files_file_type ON files (file_type)")
        self.db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_files_source_type ON files (source_type)")
        self.db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_files_upload_date ON files (upload_date)")
    
    # REMOVED: _create_digital_twins_table method - old digital twins table not needed for new twin registry
    
    def _create_project_use_case_links_table(self):
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
        self.db_manager.execute_update(query)
        logger.info("Created project_use_case_links table")
    
    def _create_aasx_processing_table(self):
        """Create the aasx_processing table for AASX job tracking."""
        query = """
            CREATE TABLE IF NOT EXISTS aasx_processing (
                job_id TEXT PRIMARY KEY,
                file_id TEXT NOT NULL,
                project_id TEXT NOT NULL,
                processing_status TEXT NOT NULL,
                processing_time REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                output_directory TEXT,
                
                -- Results based on job type
                extraction_results TEXT DEFAULT NULL, -- JSON: for extraction jobs (multiple formats)
                generation_results TEXT DEFAULT NULL, -- JSON: for generation jobs (AASX only)
                
                error_message TEXT,
                processed_by TEXT,  -- user_id of the user who processed the job
                org_id TEXT,        -- organization_id of the user who processed the job
                
                -- Job-specific fields
                job_type TEXT NOT NULL CHECK (job_type IN ('extraction', 'generation')),
                source_type TEXT NOT NULL CHECK (source_type IN ('manual_upload', 'url_upload')),
                extraction_options TEXT DEFAULT '{}', -- JSON: extraction settings
                generation_options TEXT DEFAULT '{}', -- JSON: generation settings
                
                -- Phase 4.1: Essential Quality Metrics (frequently queried)
                data_quality_score REAL, -- 0-100 quality score
                file_integrity_checksum TEXT, -- MD5/SHA256 checksum
                processing_accuracy REAL, -- 0-100 accuracy rate
                
                -- Federated Learning Consent & Settings
                federated_learning TEXT DEFAULT 'not_allowed' CHECK (federated_learning IN ('allowed', 'not_allowed', 'conditional')),
                user_consent_timestamp TEXT,
                consent_terms_version TEXT,
                federated_participation_status TEXT DEFAULT 'inactive',
                
                -- Timestamps
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                
                FOREIGN KEY (file_id) REFERENCES files (file_id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE,
                FOREIGN KEY (processed_by) REFERENCES users (user_id),
                FOREIGN KEY (org_id) REFERENCES organizations (org_id) ON DELETE SET NULL
            )
        """
        self.db_manager.execute_update(query)
        
        # Create performance indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_file_id ON aasx_processing (file_id)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_project_id ON aasx_processing (project_id)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_status ON aasx_processing (processing_status)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_job_type ON aasx_processing (job_type)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_timestamp ON aasx_processing (timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_processed_by ON aasx_processing (processed_by)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_org_id ON aasx_processing (org_id)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_source_type ON aasx_processing (source_type)",
            # Phase 4.1: Quality metrics indexes
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_quality_score ON aasx_processing (data_quality_score)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_accuracy ON aasx_processing (processing_accuracy)",
            # Federated Learning indexes
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_federated_learning ON aasx_processing (federated_learning)",
            "CREATE INDEX IF NOT EXISTS idx_aasx_processing_participation_status ON aasx_processing (federated_participation_status)"
        ]
        
        for index_query in indexes:
            try:
                self.db_manager.execute_update(index_query)
            except Exception as e:
                logger.warning(f"Failed to create index: {e}")
        
        logger.info("Created aasx_processing table with indexes")
    
    def _create_aasx_processing_metrics_table(self):
        """Create the aasx_processing_metrics table for comprehensive tracking."""
        query = """
            CREATE TABLE IF NOT EXISTS aasx_processing_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- System Resources
                memory_usage_mb REAL,
                cpu_usage_percent REAL,
                disk_io_mb REAL,
                network_usage_mb REAL,
                
                -- Quality & Validation
                validation_results TEXT, -- JSON: detailed validation data
                quality_metrics TEXT, -- JSON: comprehensive quality scores
                
                -- Processing Patterns & Analytics
                hour_of_day INTEGER CHECK (hour_of_day >= 0 AND hour_of_day <= 23),
                day_of_week INTEGER CHECK (day_of_week >= 1 AND day_of_week <= 7),
                month INTEGER CHECK (month >= 1 AND month <= 12),
                
                -- Resource Utilization Trends
                peak_memory_mb REAL,
                peak_cpu_percent REAL,
                total_disk_io_mb REAL,
                processing_efficiency_score REAL, -- 0-100 score
                
                -- User Behavior Patterns
                session_duration_seconds REAL,
                consecutive_jobs_count INTEGER DEFAULT 1,
                user_behavior_patterns TEXT, -- JSON: user interaction data
                
                -- Performance Trends
                processing_time_trend REAL, -- Compared to historical average
                resource_efficiency_trend REAL, -- Performance over time
                
                -- Compliance & Security
                data_sensitivity_level TEXT CHECK (data_sensitivity_level IN ('public', 'internal', 'confidential', 'restricted')),
                compliance_requirements TEXT, -- JSON array of requirements
                access_logs TEXT, -- JSON: access audit trail
                security_events TEXT, -- JSON: security monitoring data
                retention_policy TEXT,
                scheduled_deletion_date TIMESTAMP,
                
                -- Foreign Keys
                FOREIGN KEY (job_id) REFERENCES aasx_processing (job_id) ON DELETE CASCADE
            )
        """
        self.db_manager.execute_update(query)
        
        # Create performance indexes for metrics table
        metrics_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_processing_metrics_job_id ON aasx_processing_metrics (job_id)",
            "CREATE INDEX IF NOT EXISTS idx_processing_metrics_timestamp ON aasx_processing_metrics (timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_processing_metrics_user_patterns ON aasx_processing_metrics (hour_of_day, day_of_week)",
            "CREATE INDEX IF NOT EXISTS idx_processing_metrics_performance ON aasx_processing_metrics (processing_efficiency_score, processing_time_trend)",
            "CREATE INDEX IF NOT EXISTS idx_processing_metrics_sensitivity ON aasx_processing_metrics (data_sensitivity_level)",
            "CREATE INDEX IF NOT EXISTS idx_processing_metrics_efficiency ON aasx_processing_metrics (processing_efficiency_score)"
        ]
        
        for index_query in metrics_indexes:
            try:
                self.db_manager.execute_update(index_query)
            except Exception as e:
                logger.warning(f"Failed to create metrics index: {e}")
        
        logger.info("Created aasx_processing_metrics table with indexes")
    
    def _create_twin_registry_table(self):
        """Create the twin_registry table - Master Coordination Hub for Digital Twins."""
        query = """
            CREATE TABLE IF NOT EXISTS twin_registry (
                -- Primary Identification
                registry_id TEXT PRIMARY KEY,                    -- Unique registry identifier
                twin_id TEXT NOT NULL UNIQUE,                    -- Digital twin identifier
                twin_name TEXT NOT NULL,                         -- Human-readable twin name
                registry_name TEXT NOT NULL,                     -- Registry instance name
                
                -- Twin Classification & Metadata
                twin_category TEXT NOT NULL DEFAULT 'generic'    -- manufacturing, energy, component, facility, process, generic
                    CHECK (twin_category IN ('manufacturing', 'energy', 'component', 'facility', 'process', 'generic')),
                twin_type TEXT NOT NULL DEFAULT 'physical'      -- physical, virtual, hybrid, composite
                    CHECK (twin_type IN ('physical', 'virtual', 'hybrid', 'composite')),
                twin_priority TEXT NOT NULL DEFAULT 'normal'     -- low, normal, high, critical, emergency
                    CHECK (twin_priority IN ('low', 'normal', 'high', 'critical', 'emergency')),
                twin_version TEXT NOT NULL DEFAULT '1.0.0',      -- Semantic versioning (major.minor.patch)
                
                -- Workflow Classification (CRITICAL for dual workflow support)
                registry_type TEXT NOT NULL                      -- extraction, generation, hybrid
                    CHECK (registry_type IN ('extraction', 'generation', 'hybrid')),
                workflow_source TEXT NOT NULL                    -- aasx_file, structured_data, both
                    CHECK (workflow_source IN ('aasx_file', 'structured_data', 'both')),
                
                -- Module Integration References (Links to other modules - NO data duplication)
                aasx_integration_id TEXT,                        -- Reference to aasx_processing table
                physics_modeling_id TEXT,                        -- Reference to physics_modeling table
                federated_learning_id TEXT,                      -- Reference to federated_learning table
                data_pipeline_id TEXT,                           -- Reference to data_pipeline table
                kg_neo4j_id TEXT,                                -- Reference to knowledge graph module
                certificate_manager_id TEXT,                     -- Reference to certificate module
                
                -- Integration Status & Health
                integration_status TEXT NOT NULL DEFAULT 'pending' -- pending, active, inactive, error, maintenance, deprecated
                    CHECK (integration_status IN ('pending', 'active', 'inactive', 'error', 'maintenance', 'deprecated')),
                overall_health_score INTEGER DEFAULT 0           -- 0-100 health score across all modules
                    CHECK (overall_health_score >= 0 AND overall_health_score <= 100),
                health_status TEXT NOT NULL DEFAULT 'unknown'    -- unknown, healthy, warning, critical, offline
                    CHECK (health_status IN ('unknown', 'healthy', 'warning', 'critical', 'offline')),
                
                -- Lifecycle Management
                lifecycle_status TEXT NOT NULL DEFAULT 'created' -- created, active, suspended, archived, retired
                    CHECK (lifecycle_status IN ('created', 'active', 'suspended', 'archived', 'retired')),
                lifecycle_phase TEXT NOT NULL DEFAULT 'development' -- development, testing, production, maintenance, sunset
                    CHECK (lifecycle_phase IN ('development', 'testing', 'production', 'maintenance', 'sunset')),
                
                -- Operational Status
                operational_status TEXT NOT NULL DEFAULT 'stopped' -- running, stopped, paused, error, maintenance
                    CHECK (operational_status IN ('running', 'stopped', 'paused', 'error', 'maintenance')),
                availability_status TEXT NOT NULL DEFAULT 'offline' -- online, offline, degraded, maintenance
                    CHECK (availability_status IN ('online', 'offline', 'degraded', 'maintenance')),
                
                -- Synchronization & Data Management
                sync_status TEXT NOT NULL DEFAULT 'pending'      -- pending, in_progress, completed, failed, scheduled
                    CHECK (sync_status IN ('pending', 'in_progress', 'completed', 'failed', 'scheduled')),
                sync_frequency TEXT NOT NULL DEFAULT 'daily'     -- real_time, hourly, daily, weekly, manual
                    CHECK (sync_frequency IN ('real_time', 'hourly', 'daily', 'weekly', 'manual')),
                last_sync_at TEXT,                               -- Last synchronization timestamp
                next_sync_at TEXT,                               -- Next scheduled synchronization
                sync_error_count INTEGER DEFAULT 0,              -- Count of consecutive sync failures
                sync_error_message TEXT,                         -- Last sync error message
                
                -- Performance & Quality Metrics
                performance_score REAL DEFAULT 0.0,              -- 0.0-1.0 performance rating
                data_quality_score REAL DEFAULT 0.0,             -- 0.0-1.0 data quality rating
                reliability_score REAL DEFAULT 0.0,              -- 0.0-1.0 reliability rating
                compliance_score REAL DEFAULT 0.0,               -- 0.0-1.0 compliance rating
                
                -- Security & Access Control
                security_level TEXT NOT NULL DEFAULT 'standard'  -- public, internal, confidential, secret, top_secret
                    CHECK (security_level IN ('public', 'internal', 'confidential', 'secret', 'top_secret')),
                access_control_level TEXT NOT NULL DEFAULT 'user' -- public, user, admin, system, restricted
                    CHECK (access_control_level IN ('public', 'user', 'admin', 'system', 'restricted')),
                encryption_enabled BOOLEAN DEFAULT FALSE,        -- Whether data is encrypted
                audit_logging_enabled BOOLEAN DEFAULT TRUE,      -- Whether audit logging is enabled
                
                -- User Management & Ownership
                user_id TEXT NOT NULL,                           -- Current user who owns/accesses this registry
                org_id TEXT NOT NULL,                            -- Organization this registry belongs to
                owner_team TEXT,                                 -- Team responsible for this twin
                steward_user_id TEXT,                            -- Data steward for this twin
                
                -- Timestamps & Audit
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                activated_at TEXT,                               -- When twin was first activated
                last_accessed_at TEXT,                           -- Last time any user accessed this twin
                last_modified_at TEXT,                           -- Last time twin data was modified
                
                -- Configuration & Metadata (JSON fields for flexibility)
                registry_config TEXT DEFAULT '{}',               -- Registry configuration settings
                registry_metadata TEXT DEFAULT '{}',              -- Additional metadata
                custom_attributes TEXT DEFAULT '{}',              -- User-defined custom attributes
                tags TEXT DEFAULT '[]',                          -- JSON array of tags for categorization
                
                -- Relationships & Dependencies (JSON arrays)
                relationships TEXT DEFAULT '[]',                  -- Array of relationship objects
                dependencies TEXT DEFAULT '[]',                   -- Array of dependency objects
                instances TEXT DEFAULT '[]',                      -- Array of instance objects
                
                -- Constraints
                FOREIGN KEY (aasx_integration_id) REFERENCES aasx_processing(file_id) ON DELETE SET NULL
                -- FOREIGN KEY (user_id) REFERENCES users(user_id), -- Removed: not needed for testing
                -- FOREIGN KEY (org_id) REFERENCES organizations(org_id), -- Removed: not needed for testing
                -- FOREIGN KEY (steward_user_id) REFERENCES users(user_id) ON DELETE SET NULL -- Removed: not needed for testing
            )
        """
        self.db_manager.execute_update(query)
        
        # Create performance indexes for twin registry table
        twin_indexes = [
            # Primary Performance Indexes
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_twin_id ON twin_registry (twin_id)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_twin_name ON twin_registry (twin_name)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_category ON twin_registry (twin_category)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_priority ON twin_registry (twin_priority)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_type ON twin_registry (registry_type)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_workflow_source ON twin_registry (workflow_source)",
            
            # Integration & Status Indexes
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_integration_status ON twin_registry (integration_status)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_health_status ON twin_registry (health_status)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_lifecycle_status ON twin_registry (lifecycle_status)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_operational_status ON twin_registry (operational_status)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_sync_status ON twin_registry (sync_status)",
            
            # User & Organization Indexes
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_user_id ON twin_registry (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_org_id ON twin_registry (org_id)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_steward ON twin_registry (steward_user_id)",
            
            # Composite Indexes for Complex Queries
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_health_priority ON twin_registry (health_status, twin_priority)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_category_status ON twin_registry (twin_category, integration_status)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_workflow_health ON twin_registry (registry_type, health_status)"
        ]
        
        for index_query in twin_indexes:
            try:
                self.db_manager.execute_update(index_query)
            except Exception as e:
                logger.warning(f"Failed to create twin registry index: {e}")
        
        logger.info("Created twin_registry table with comprehensive indexes")
    
    def _create_twin_registry_metrics_table(self):
        """Create the twin_registry_metrics table for real-time monitoring & analytics."""
        query = """
            CREATE TABLE IF NOT EXISTS twin_registry_metrics (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                registry_id TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Real-time Health Metrics
                health_score INTEGER,                            -- Current health score (0-100)
                response_time_ms REAL,                           -- Response time in milliseconds
                uptime_percentage REAL,                          -- Uptime percentage
                error_rate REAL,                                 -- Error rate (0.0-1.0)
                
                -- Performance Metrics
                cpu_usage_percent REAL,                          -- CPU usage percentage
                memory_usage_percent REAL,                       -- Memory usage percentage
                network_throughput_mbps REAL,                    -- Network throughput
                storage_usage_percent REAL,                      -- Storage usage percentage
                
                -- Business Metrics
                transaction_count INTEGER,                       -- Number of transactions processed
                data_volume_mb REAL,                            -- Data volume processed in MB
                user_interaction_count INTEGER,                  -- Number of user interactions
                
                -- Lifecycle Events (JSON array)
                lifecycle_events TEXT DEFAULT '[]',              -- Array of lifecycle event objects
                
                -- Performance Trends (JSON)
                performance_trends TEXT DEFAULT '{}',            -- Performance trend data
                
                -- User Activity (JSON)
                user_activity TEXT DEFAULT '{}',                 -- User activity metrics
                
                -- Compliance & Security (JSON)
                compliance_status TEXT DEFAULT '{}',             -- Compliance status data
                security_events TEXT DEFAULT '[]',               -- Security event log
                
                FOREIGN KEY (registry_id) REFERENCES twin_registry(registry_id) ON DELETE CASCADE
            )
        """
        self.db_manager.execute_update(query)
        
        # Create performance indexes for metrics table
        metrics_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_metrics_registry_id ON twin_registry_metrics (registry_id)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_metrics_timestamp ON twin_registry_metrics (timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_metrics_health_score ON twin_registry_metrics (health_score)",
            "CREATE INDEX IF NOT EXISTS idx_twin_registry_metrics_performance ON twin_registry_metrics (performance_trends)"
        ]
        
        for index_query in metrics_indexes:
            try:
                self.db_manager.execute_update(index_query)
            except Exception as e:
                logger.warning(f"Failed to create twin registry metrics index: {e}")
        
        logger.info("Created twin_registry_metrics table with indexes")
    
    def _create_data_lineage_table(self):
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
                dependency_visualization TEXT DEFAULT '{}', -- JSON: visualization preferences
                
                FOREIGN KEY (source_entity_id) REFERENCES use_cases(use_case_id) ON DELETE CASCADE,
                FOREIGN KEY (target_entity_id) REFERENCES projects(project_id) ON DELETE CASCADE
            )
        """
        self.db_manager.execute_update(query)
        
        # Create performance indexes for enhanced lineage table
        lineage_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_source ON data_lineage (source_entity_type, source_entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_target ON data_lineage (target_entity_type, target_entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_relationship ON data_lineage (relationship_type)",
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_depth ON data_lineage (lineage_depth)",
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_confidence ON data_lineage (confidence_score)",
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_validation ON data_lineage (validation_status)",
            # Enhanced lineage indexes
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_transformation ON data_lineage (transformation_type)",
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_complexity ON data_lineage (lineage_complexity)",
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_quality_impact ON data_lineage (data_quality_impact)",
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_business_value ON data_lineage (business_value_score)",
            # Dependency indexes
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_dependency_level ON data_lineage (dependency_level)",
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_dependency_criticality ON data_lineage (dependency_criticality)",
            "CREATE INDEX IF NOT EXISTS idx_data_lineage_dependency_risk ON data_lineage (dependency_risk_score)"
        ]
        
        for index_query in lineage_indexes:
            try:
                self.db_manager.execute_update(index_query)
            except Exception as e:
                logger.warning(f"Failed to create data lineage index: {e}")
        
        logger.info("Created enhanced data_lineage table with advanced governance indexes")
    
    def _create_data_quality_metrics_table(self):
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
                quality_trend TEXT DEFAULT '{}', -- JSON: quality trend over time
                
                FOREIGN KEY (calculated_by) REFERENCES users(user_id) ON DELETE SET NULL
            )
        """
        self.db_manager.execute_update(query)
        
        # Create performance indexes for quality metrics table
        quality_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_data_quality_metrics_entity ON data_quality_metrics (entity_type, entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_data_quality_metrics_date ON data_quality_metrics (metric_date)",
            "CREATE INDEX IF NOT EXISTS idx_data_quality_metrics_score ON data_quality_metrics (overall_quality_score)",
            "CREATE INDEX IF NOT EXISTS idx_data_quality_metrics_status ON data_quality_metrics (quality_status)",
            "CREATE INDEX IF NOT EXISTS idx_data_quality_metrics_threshold ON data_quality_metrics (quality_threshold)"
        ]
        
        for index_query in quality_indexes:
            try:
                self.db_manager.execute_update(index_query)
            except Exception as e:
                logger.warning(f"Failed to create data quality metrics index: {e}")
        
        logger.info("Created data_quality_metrics table with governance indexes")
    
    def _create_change_requests_table(self):
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
                updated_at TEXT NOT NULL,
                
                FOREIGN KEY (requested_by) REFERENCES users(user_id),
                FOREIGN KEY (assigned_to) REFERENCES users(user_id),
                FOREIGN KEY (reviewed_by) REFERENCES users(user_id),
                FOREIGN KEY (approved_by) REFERENCES users(user_id),
                FOREIGN KEY (implemented_by) REFERENCES users(user_id)
            )
        """
        self.db_manager.execute_update(query)
        
        # Create performance indexes for change requests table
        change_request_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_change_requests_status ON change_requests (status)",
            "CREATE INDEX IF NOT EXISTS idx_change_requests_type ON change_requests (change_type)",
            "CREATE INDEX IF NOT EXISTS idx_change_requests_entity ON change_requests (entity_type, entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_change_requests_requested_by ON change_requests (requested_by)",
            "CREATE INDEX IF NOT EXISTS idx_change_requests_assigned_to ON change_requests (assigned_to)",
            "CREATE INDEX IF NOT EXISTS idx_change_requests_priority ON change_requests (priority)",
            "CREATE INDEX IF NOT EXISTS idx_change_requests_requested_at ON change_requests (requested_at)",
            "CREATE INDEX IF NOT EXISTS idx_change_requests_deadline ON change_requests (review_deadline)"
        ]
        
        for index_query in change_request_indexes:
            try:
                self.db_manager.execute_update(index_query)
            except Exception as e:
                logger.warning(f"Failed to create change request index: {e}")
        
        logger.info("Created change_requests table with workflow indexes")
    
    def _create_data_versions_table(self):
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
                retention_expiry TEXT, -- When this version should be archived/deleted
                
                FOREIGN KEY (previous_version_id) REFERENCES data_versions(version_id),
                FOREIGN KEY (change_request_id) REFERENCES change_requests(request_id),
                FOREIGN KEY (created_by) REFERENCES users(user_id)
            )
        """
        self.db_manager.execute_update(query)
        
        # Create performance indexes for data versions table
        version_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_data_versions_entity ON data_versions (entity_type, entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_data_versions_version ON data_versions (version_number)",
            "CREATE INDEX IF NOT EXISTS idx_data_versions_current ON data_versions (is_current)",
            "CREATE INDEX IF NOT EXISTS idx_data_versions_type ON data_versions (version_type)",
            "CREATE INDEX IF NOT EXISTS idx_data_versions_created_at ON data_versions (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_data_versions_change_type ON data_versions (change_type)",
            "CREATE INDEX IF NOT EXISTS idx_data_versions_compliance ON data_versions (compliance_status)"
        ]
        
        for index_query in version_indexes:
            try:
                self.db_manager.execute_update(index_query)
            except Exception as e:
                logger.warning(f"Failed to create data version index: {e}")
        
        logger.info("Created data_versions table with versioning indexes")
    
    def _create_governance_policies_table(self):
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
                updated_at TEXT NOT NULL,
                
                FOREIGN KEY (policy_owner) REFERENCES users(user_id),
                FOREIGN KEY (approved_by) REFERENCES users(user_id)
            )
        """
        self.db_manager.execute_update(query)
        
        # Create performance indexes for governance policies table
        policy_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_governance_policies_type ON governance_policies (policy_type)",
            "CREATE INDEX IF NOT EXISTS idx_governance_policies_category ON governance_policies (policy_category)",
            "CREATE INDEX IF NOT EXISTS idx_governance_policies_status ON governance_policies (status)",
            "CREATE INDEX IF NOT EXISTS idx_governance_policies_enforcement ON governance_policies (enforcement_level)",
            "CREATE INDEX IF NOT EXISTS idx_governance_policies_owner ON governance_policies (policy_owner)",
            "CREATE INDEX IF NOT EXISTS idx_governance_policies_effective_date ON governance_policies (effective_date)",
            "CREATE INDEX IF NOT EXISTS idx_governance_policies_compliance ON governance_policies (compliance_rate)",
            "CREATE INDEX IF NOT EXISTS idx_governance_policies_entities ON governance_policies (applicable_entities)"
        ]
        
        for index_query in policy_indexes:
            try:
                self.db_manager.execute_update(index_query)
            except Exception as e:
                logger.warning(f"Failed to create governance policy index: {e}")
        
        logger.info("Created governance_policies table with policy management indexes")
    
    def _create_data_usage_analytics_table(self):
        """Create the data_usage_analytics table for tracking data usage patterns and engagement."""
        query = """
            CREATE TABLE IF NOT EXISTS data_usage_analytics (
                analytics_id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL CHECK (entity_type IN ('file', 'project', 'use_case', 'user', 'organization', 'data_lineage', 'quality_metrics')),
                entity_id TEXT NOT NULL,
                analytics_date TEXT NOT NULL, -- Date when analytics were calculated
                
                -- Access Pattern Tracking
                total_accesses INTEGER DEFAULT 0, -- Total number of accesses
                unique_users INTEGER DEFAULT 0, -- Number of unique users who accessed
                access_frequency REAL DEFAULT 0.0, -- Average accesses per day
                peak_usage_time TEXT, -- Time of day with highest usage
                usage_pattern TEXT DEFAULT '{}', -- JSON: hourly/daily/weekly usage patterns
                
                -- User Engagement Scoring
                user_engagement_score REAL DEFAULT 0.0, -- 0-100 engagement score
                active_users_count INTEGER DEFAULT 0, -- Number of actively engaged users
                user_retention_rate REAL DEFAULT 0.0, -- User retention percentage
                user_satisfaction_score REAL DEFAULT 0.0, -- User satisfaction rating
                engagement_metrics TEXT DEFAULT '{}', -- JSON: detailed engagement data
                
                -- Data Freshness Metrics
                last_updated TEXT, -- When data was last updated
                data_age_days INTEGER DEFAULT 0, -- Age of data in days
                freshness_score REAL DEFAULT 0.0, -- 0-100 freshness score
                update_frequency REAL DEFAULT 0.0, -- How often data is updated
                staleness_indicators TEXT DEFAULT '[]', -- JSON: indicators of stale data
                
                -- Business Value Scoring
                business_value_score REAL DEFAULT 0.0, -- 0-100 business value score
                roi_estimate REAL DEFAULT 0.0, -- Return on investment estimate
                cost_benefit_ratio REAL DEFAULT 0.0, -- Cost vs benefit ratio
                strategic_importance TEXT DEFAULT 'low' CHECK (strategic_importance IN ('low', 'medium', 'high', 'critical')),
                business_impact_metrics TEXT DEFAULT '{}', -- JSON: business impact details
                
                -- Performance Metrics
                response_time_avg REAL DEFAULT 0.0, -- Average response time in ms
                throughput_ops_per_sec REAL DEFAULT 0.0, -- Operations per second
                error_rate REAL DEFAULT 0.0, -- Error rate percentage
                performance_score REAL DEFAULT 0.0, -- 0-100 performance score
                performance_trends TEXT DEFAULT '{}', -- JSON: performance over time
                
                -- Metadata & Tracking
                analytics_metadata TEXT DEFAULT '{}', -- JSON: additional analytics information
                calculated_by TEXT, -- User who calculated these analytics
                calculation_method TEXT DEFAULT 'automated', -- How analytics were calculated
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                
                -- Performance tracking
                last_analytics_run TEXT,
                analytics_trend TEXT DEFAULT '{}', -- JSON: analytics trend over time
                
                FOREIGN KEY (calculated_by) REFERENCES users(user_id) ON DELETE SET NULL
            )
        """
        self.db_manager.execute_update(query)
        
        # Create performance indexes for data usage analytics table
        analytics_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_data_usage_analytics_entity ON data_usage_analytics (entity_type, entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_data_usage_analytics_date ON data_usage_analytics (analytics_date)",
            "CREATE INDEX IF NOT EXISTS idx_data_usage_analytics_engagement ON data_usage_analytics (user_engagement_score)",
            "CREATE INDEX IF NOT EXISTS idx_data_usage_analytics_freshness ON data_usage_analytics (freshness_score)",
            "CREATE INDEX IF NOT EXISTS idx_data_usage_analytics_business_value ON data_usage_analytics (business_value_score)",
            "CREATE INDEX IF NOT EXISTS idx_data_usage_analytics_performance ON data_usage_analytics (performance_score)",
            "CREATE INDEX IF NOT EXISTS idx_data_usage_analytics_strategic ON data_usage_analytics (strategic_importance)",
            "CREATE INDEX IF NOT EXISTS idx_data_usage_analytics_accesses ON data_usage_analytics (total_accesses)"
        ]
        
        for index_query in analytics_indexes:
            try:
                self.db_manager.execute_update(index_query)
            except Exception as e:
                logger.warning(f"Failed to create data usage analytics index: {e}")
        
        logger.info("Created data_usage_analytics table with analytics indexes")
    
    def _create_performance_metrics_table(self):
        """Create the performance_metrics table for tracking system and data performance."""
        query = """
            CREATE TABLE IF NOT EXISTS performance_metrics (
                metric_id TEXT PRIMARY KEY,
                metric_type TEXT NOT NULL CHECK (metric_type IN ('system', 'data', 'user', 'business', 'infrastructure')),
                metric_name TEXT NOT NULL, -- Specific metric name
                metric_category TEXT NOT NULL, -- Category of the metric
                entity_type TEXT, -- Type of entity being measured
                entity_id TEXT, -- ID of entity being measured
                metric_date TEXT NOT NULL, -- Date when metric was measured
                
                -- Metric Values
                current_value REAL NOT NULL, -- Current metric value
                previous_value REAL, -- Previous measurement value
                baseline_value REAL, -- Baseline/expected value
                target_value REAL, -- Target/optimal value
                threshold_min REAL, -- Minimum acceptable value
                threshold_max REAL, -- Maximum acceptable value
                
                -- Performance Analysis
                performance_score REAL DEFAULT 0.0, -- 0-100 performance score
                performance_status TEXT DEFAULT 'normal' CHECK (performance_status IN ('excellent', 'good', 'normal', 'warning', 'critical', 'unknown')),
                trend_direction TEXT DEFAULT 'stable' CHECK (trend_direction IN ('improving', 'stable', 'declining', 'fluctuating')),
                trend_strength REAL DEFAULT 0.0, -- Strength of trend (0-100)
                
                -- Alert System
                alert_enabled BOOLEAN DEFAULT TRUE, -- Whether alerts are enabled
                alert_threshold REAL, -- Threshold for triggering alerts
                alert_priority TEXT DEFAULT 'medium' CHECK (alert_priority IN ('low', 'medium', 'high', 'critical')),
                alert_message TEXT, -- Custom alert message
                last_alert_sent TEXT, -- When last alert was sent
                
                -- Performance Trends
                historical_values TEXT DEFAULT '[]', -- JSON: historical metric values
                trend_analysis TEXT DEFAULT '{}', -- JSON: trend analysis results
                seasonality_patterns TEXT DEFAULT '{}', -- JSON: seasonal patterns
                anomaly_detection TEXT DEFAULT '{}', -- JSON: anomaly detection results
                
                -- Metadata & Tracking
                metric_description TEXT, -- Description of what this metric measures
                unit_of_measure TEXT, -- Unit of measurement
                calculation_method TEXT DEFAULT 'automated', -- How metric is calculated
                data_source TEXT, -- Source of metric data
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                
                -- Performance tracking
                last_metric_calculation TEXT,
                calculation_frequency TEXT DEFAULT 'hourly', -- How often metric is calculated
                
                FOREIGN KEY (entity_type, entity_id) REFERENCES data_usage_analytics(entity_type, entity_id)
            )
        """
        self.db_manager.execute_update(query)
        
        # Create performance indexes for performance metrics table
        performance_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_performance_metrics_type ON performance_metrics (metric_type)",
            "CREATE INDEX IF NOT EXISTS idx_performance_metrics_category ON performance_metrics (metric_category)",
            "CREATE INDEX IF NOT EXISTS idx_performance_metrics_entity ON performance_metrics (entity_type, entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_performance_metrics_date ON performance_metrics (metric_date)",
            "CREATE INDEX IF NOT EXISTS idx_performance_metrics_score ON performance_metrics (performance_score)",
            "CREATE INDEX IF NOT EXISTS idx_performance_metrics_status ON performance_metrics (performance_status)",
            "CREATE INDEX IF NOT EXISTS idx_performance_metrics_trend ON performance_metrics (trend_direction)",
            "CREATE INDEX IF NOT EXISTS idx_performance_metrics_alert ON performance_metrics (alert_enabled, alert_priority)"
        ]
        
        for index_query in performance_indexes:
            try:
                self.db_manager.execute_update(index_query)
            except Exception as e:
                logger.warning(f"Failed to create performance metrics index: {e}")
        
        logger.info("Created performance_metrics table with performance tracking indexes")
    
    def _create_users_table(self):
        """Create the users table with comprehensive world-class user management fields."""
        query = """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                email TEXT UNIQUE,
                full_name TEXT,
                org_id TEXT,
                phone TEXT,
                job_title TEXT,
                department TEXT,
                bio TEXT,
                password_hash TEXT,
                role TEXT DEFAULT 'user',
                is_active BOOLEAN DEFAULT 1,
                last_login TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                
                -- User Verification & Security
                is_verified BOOLEAN DEFAULT FALSE,
                email_verified BOOLEAN DEFAULT FALSE,
                phone_verified BOOLEAN DEFAULT FALSE,
                verification_token TEXT,
                reset_token TEXT,
                reset_token_expires TEXT,
                mfa_enabled BOOLEAN DEFAULT FALSE,
                mfa_secret TEXT,
                last_password_change TEXT,
                failed_login_attempts INTEGER DEFAULT 0,
                account_locked_until TEXT,
                
                -- User Preferences & Settings
                preferences TEXT DEFAULT '{}',
                avatar_url TEXT,
                timezone TEXT DEFAULT 'UTC',
                language TEXT DEFAULT 'en',
                
                -- User Consent & Privacy Management
                consent_version TEXT DEFAULT '1.0',
                consent_granted_at TEXT,
                consent_revoked_at TEXT,
                privacy_preferences TEXT DEFAULT '{}',
                data_processing_consent TEXT DEFAULT '{}',
                marketing_consent BOOLEAN DEFAULT FALSE,
                third_party_sharing_consent BOOLEAN DEFAULT FALSE,
                data_retention_consent BOOLEAN DEFAULT FALSE,
                
                -- Advanced User Management
                last_activity TEXT,
                session_count INTEGER DEFAULT 0,
                ip_whitelist TEXT DEFAULT '[]',
                device_fingerprint TEXT,
                
                -- Compliance & Audit
                data_access_level TEXT DEFAULT 'standard' CHECK (data_access_level IN ('restricted', 'standard', 'elevated', 'admin')),
                compliance_requirements TEXT DEFAULT '[]',
                audit_log_enabled BOOLEAN DEFAULT TRUE,
                data_classification TEXT DEFAULT 'internal' CHECK (data_classification IN ('public', 'internal', 'confidential', 'restricted')),
                
                FOREIGN KEY (org_id) REFERENCES organizations (org_id) ON DELETE SET NULL
            )
        """
        self.db_manager.execute_update(query)
        
        # Create world-class indexes for users table
        user_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users (username)",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)",
            "CREATE INDEX IF NOT EXISTS idx_users_org_id ON users (org_id)",
            "CREATE INDEX IF NOT EXISTS idx_users_role ON users (role)",
            "CREATE INDEX IF NOT EXISTS idx_users_is_active ON users (is_active)",
            "CREATE INDEX IF NOT EXISTS idx_users_consent ON users (consent_version, consent_granted_at)",
            "CREATE INDEX IF NOT EXISTS idx_users_verification ON users (is_verified, email_verified, phone_verified)",
            "CREATE INDEX IF NOT EXISTS idx_users_compliance ON users (data_access_level, data_classification)",
            "CREATE INDEX IF NOT EXISTS idx_users_activity ON users (last_activity, last_login)",
            "CREATE INDEX IF NOT EXISTS idx_users_security ON users (mfa_enabled, failed_login_attempts)"
        ]
        
        for index_query in user_indexes:
            try:
                self.db_manager.execute_update(index_query)
            except Exception as e:
                logger.warning(f"Failed to create user index: {e}")
        
        logger.info("Created world-class users table with comprehensive fields and indexes")
    
    def _create_kg_graph_registry_table(self):
        """Create the knowledge graph registry table with comprehensive graph management capabilities."""
        query = """
            CREATE TABLE IF NOT EXISTS kg_graph_registry (
                -- Primary Identification
                graph_id TEXT PRIMARY KEY,
                file_id TEXT NOT NULL,
                graph_name TEXT NOT NULL,
                registry_name TEXT NOT NULL,
                
                -- Graph Classification & Metadata
                graph_category TEXT DEFAULT 'generic' CHECK (graph_category IN ('aasx', 'structured_data', 'hybrid', 'custom')),
                graph_type TEXT DEFAULT 'asset_graph' CHECK (graph_type IN ('asset_graph', 'relationship_graph', 'process_graph', 'composite')),
                graph_priority TEXT DEFAULT 'normal' CHECK (graph_priority IN ('low', 'normal', 'high', 'critical')),
                graph_version TEXT DEFAULT '1.0.0',
                
                -- Workflow Classification
                registry_type TEXT NOT NULL CHECK (registry_type IN ('extraction', 'generation', 'hybrid')),
                workflow_source TEXT NOT NULL CHECK (workflow_source IN ('aasx_file', 'structured_data', 'both')),
                
                -- Module Integration References
                aasx_integration_id TEXT,
                twin_registry_id TEXT,
                physics_modeling_id TEXT,
                federated_learning_id TEXT,
                certificate_manager_id TEXT,
                
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
                
                -- Neo4j-Specific Status
                neo4j_import_status TEXT DEFAULT 'pending' CHECK (neo4j_import_status IN ('pending', 'in_progress', 'completed', 'failed', 'scheduled')),
                neo4j_export_status TEXT DEFAULT 'pending' CHECK (neo4j_export_status IN ('pending', 'in_progress', 'completed', 'failed', 'scheduled')),
                last_neo4j_sync_at TEXT,
                next_neo4j_sync_at TEXT,
                neo4j_sync_error_count INTEGER DEFAULT 0,
                neo4j_sync_error_message TEXT,
                
                -- Graph Data Metrics
                total_nodes INTEGER DEFAULT 0,
                total_relationships INTEGER DEFAULT 0,
                graph_complexity TEXT DEFAULT 'simple' CHECK (graph_complexity IN ('simple', 'moderate', 'complex', 'very_complex')),
                
                -- Performance & Quality Metrics
                performance_score REAL DEFAULT 0.0 CHECK (performance_score >= 0.0 AND performance_score <= 1.0),
                data_quality_score REAL DEFAULT 0.0 CHECK (data_quality_score >= 0.0 AND data_quality_score <= 1.0),
                reliability_score REAL DEFAULT 0.0 CHECK (reliability_score >= 0.0 AND reliability_score <= 1.0),
                compliance_score REAL DEFAULT 0.0 CHECK (compliance_score >= 0.0 AND compliance_score <= 1.0),
                
                -- Security & Access Control
                security_level TEXT DEFAULT 'standard' CHECK (security_level IN ('public', 'internal', 'confidential', 'secret', 'top_secret')),
                access_control_level TEXT DEFAULT 'user' CHECK (access_control_level IN ('public', 'user', 'admin', 'system', 'restricted')),
                encryption_enabled BOOLEAN DEFAULT FALSE,
                audit_logging_enabled BOOLEAN DEFAULT TRUE,
                
                -- User Management & Ownership
                user_id TEXT NOT NULL,
                org_id TEXT NOT NULL,
                owner_team TEXT,
                steward_user_id TEXT,
                
                -- Timestamps & Audit
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                activated_at TEXT,
                last_accessed_at TEXT,
                last_modified_at TEXT,
                
                -- Configuration & Metadata (JSON fields)
                registry_config TEXT DEFAULT '{}',
                registry_metadata TEXT DEFAULT '{}',
                custom_attributes TEXT DEFAULT '{}',
                tags TEXT DEFAULT '[]',
                
                -- Relationships & Dependencies (JSON arrays)
                relationships TEXT DEFAULT '[]',
                dependencies TEXT DEFAULT '[]',
                graph_instances TEXT DEFAULT '[]',
                
                -- Foreign Key Constraints
                FOREIGN KEY (file_id) REFERENCES files (file_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                FOREIGN KEY (org_id) REFERENCES organizations (org_id) ON DELETE CASCADE,
                FOREIGN KEY (aasx_integration_id) REFERENCES aasx_processing (job_id) ON DELETE SET NULL,
                FOREIGN KEY (twin_registry_id) REFERENCES twin_registry (twin_id) ON DELETE SET NULL
            )
        """
        self.db_manager.execute_update(query)
        
        # Create world-class indexes for knowledge graph registry table
        kg_registry_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_file_id ON kg_graph_registry (file_id)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_user_id ON kg_graph_registry (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_org_id ON kg_graph_registry (org_id)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_category ON kg_graph_registry (graph_category)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_type ON kg_graph_registry (graph_type)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_status ON kg_graph_registry (integration_status)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_health ON kg_graph_registry (health_status)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_lifecycle ON kg_graph_registry (lifecycle_status)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_neo4j ON kg_graph_registry (neo4j_import_status, neo4j_export_status)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_created ON kg_graph_registry (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_updated ON kg_graph_registry (updated_at)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_workflow ON kg_graph_registry (workflow_source, registry_type)",
            "CREATE INDEX IF NOT EXISTS idx_kg_registry_complexity ON kg_graph_registry (graph_complexity, total_nodes, total_relationships)"
        ]
        
        for index_query in kg_registry_indexes:
            try:
                self.db_manager.execute_update(index_query)
            except Exception as e:
                logger.warning(f"Failed to create knowledge graph registry index: {e}")
        
        logger.info("Created world-class knowledge graph registry table with comprehensive fields and indexes")
    
    def _create_kg_graph_metrics_table(self):
        """Create the knowledge graph metrics table with comprehensive performance monitoring."""
        query = """
            CREATE TABLE IF NOT EXISTS kg_graph_metrics (
                -- Primary Identification
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                graph_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                
                -- Real-time Health Metrics
                health_score INTEGER CHECK (health_score >= 0 AND health_score <= 100),
                response_time_ms REAL,
                uptime_percentage REAL CHECK (uptime_percentage >= 0.0 AND uptime_percentage <= 100.0),
                error_rate REAL CHECK (error_rate >= 0.0 AND error_rate <= 1.0),
                
                -- Neo4j Performance Metrics
                neo4j_connection_status TEXT CHECK (neo4j_connection_status IN ('connected', 'disconnected', 'error')),
                neo4j_query_response_time_ms REAL,
                neo4j_import_speed_nodes_per_sec REAL,
                neo4j_import_speed_rels_per_sec REAL,
                neo4j_memory_usage_mb REAL,
                neo4j_disk_usage_mb REAL,
                
                -- Graph Analytics Metrics
                graph_traversal_speed_ms REAL,
                graph_query_complexity_score REAL CHECK (graph_query_complexity_score >= 0.0 AND graph_query_complexity_score <= 1.0),
                graph_visualization_performance REAL CHECK (graph_visualization_performance >= 0.0 AND graph_visualization_performance <= 1.0),
                graph_analysis_accuracy REAL CHECK (graph_analysis_accuracy >= 0.0 AND graph_analysis_accuracy <= 1.0),
                
                -- User Interaction Metrics
                user_interaction_count INTEGER DEFAULT 0,
                query_execution_count INTEGER DEFAULT 0,
                visualization_view_count INTEGER DEFAULT 0,
                export_operation_count INTEGER DEFAULT 0,
                
                -- Data Quality Metrics
                data_freshness_score REAL CHECK (data_freshness_score >= 0.0 AND data_freshness_score <= 1.0),
                data_completeness_score REAL CHECK (data_completeness_score >= 0.0 AND data_completeness_score <= 1.0),
                data_consistency_score REAL CHECK (data_consistency_score >= 0.0 AND data_consistency_score <= 1.0),
                data_accuracy_score REAL CHECK (data_accuracy_score >= 0.0 AND data_accuracy_score <= 1.0),
                
                -- System Resource Metrics
                cpu_usage_percent REAL CHECK (cpu_usage_percent >= 0.0 AND cpu_usage_percent <= 100.0),
                memory_usage_percent REAL CHECK (memory_usage_percent >= 0.0 AND memory_usage_percent <= 100.0),
                network_throughput_mbps REAL,
                storage_usage_percent REAL CHECK (storage_usage_percent >= 0.0 AND storage_usage_percent <= 100.0),
                
                -- Performance Trends (JSON fields)
                performance_trends TEXT DEFAULT '{}',
                resource_utilization_trends TEXT DEFAULT '{}',
                user_activity TEXT DEFAULT '{}',
                query_patterns TEXT DEFAULT '{}',
                compliance_status TEXT DEFAULT '{}',
                security_events TEXT DEFAULT '[]',
                graph_analytics TEXT DEFAULT '{}',
                relationship_patterns TEXT DEFAULT '{}',
                
                -- Foreign Key Constraints
                FOREIGN KEY (graph_id) REFERENCES kg_graph_registry (graph_id) ON DELETE CASCADE
            )
        """
        self.db_manager.execute_update(query)
        
        # Create world-class indexes for knowledge graph metrics table
        kg_metrics_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_kg_metrics_graph_id ON kg_graph_metrics (graph_id)",
            "CREATE INDEX IF NOT EXISTS idx_kg_metrics_timestamp ON kg_graph_metrics (timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_kg_metrics_health ON kg_graph_metrics (health_score)",
            "CREATE INDEX IF NOT EXISTS idx_kg_metrics_neo4j ON kg_graph_metrics (neo4j_connection_status)",
            "CREATE INDEX IF NOT EXISTS idx_kg_metrics_performance ON kg_graph_metrics (graph_visualization_performance, graph_analysis_accuracy)",
            "CREATE INDEX IF NOT EXISTS idx_kg_metrics_quality ON kg_graph_metrics (data_freshness_score, data_completeness_score)",
            "CREATE INDEX IF NOT EXISTS idx_kg_metrics_resources ON kg_graph_metrics (cpu_usage_percent, memory_usage_percent)",
            "CREATE INDEX IF NOT EXISTS idx_kg_metrics_user_activity ON kg_graph_metrics (user_interaction_count, query_execution_count)"
        ]
        
        for index_query in kg_metrics_indexes:
            try:
                self.db_manager.execute_update(index_query)
            except Exception as e:
                logger.warning(f"Failed to create knowledge graph metrics index: {e}")
        
        logger.info("Created world-class knowledge graph metrics table with comprehensive fields and indexes")
    
    def _create_ai_rag_registry_table(self):
        """Create the AI/RAG registry table with comprehensive AI/RAG management capabilities."""
        query = """
            CREATE TABLE IF NOT EXISTS ai_rag_registry (
                -- Primary Identification
                registry_id TEXT PRIMARY KEY,
                file_id TEXT NOT NULL,
                registry_name TEXT NOT NULL,
                
                -- RAG Classification & Metadata
                rag_category TEXT DEFAULT 'generic' CHECK (rag_category IN ('text', 'image', 'multimodal', 'hybrid', 'graph_enhanced')),
                rag_type TEXT DEFAULT 'basic_rag' CHECK (rag_type IN ('basic', 'advanced', 'graph', 'hybrid', 'multi_step')),
                rag_priority TEXT DEFAULT 'normal' CHECK (rag_priority IN ('low', 'normal', 'high', 'critical')),
                rag_version TEXT DEFAULT '1.0.0',
                
                -- Workflow Classification
                registry_type TEXT NOT NULL CHECK (registry_type IN ('extraction', 'generation', 'hybrid')),
                workflow_source TEXT NOT NULL CHECK (workflow_source IN ('aasx_file', 'structured_data', 'both')),
                
                -- Module Integration References (Framework Integration)
                aasx_integration_id TEXT,
                twin_registry_id TEXT,
                kg_neo4j_id TEXT,
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
                
                -- RAG-Specific Integration Status (Framework Integration Points)
                embedding_generation_status TEXT DEFAULT 'pending' CHECK (embedding_generation_status IN ('pending', 'in_progress', 'completed', 'failed', 'scheduled')),
                vector_db_sync_status TEXT DEFAULT 'pending' CHECK (vector_db_sync_status IN ('pending', 'in_progress', 'completed', 'failed', 'scheduled')),
                last_embedding_generated_at TEXT,
                last_vector_db_sync_at TEXT,
                
                -- RAG Configuration (Framework Configuration - NOT Raw Data)
                embedding_model TEXT,                    -- Model name/version, not the model itself
                vector_db_type TEXT,                     -- 'qdrant', 'pinecone', etc.
                vector_collection_id TEXT,               -- Collection identifier, not the collection
                
                -- RAG Techniques Configuration (JSON for better framework flexibility)
                rag_techniques_config TEXT DEFAULT '{}', -- JSON: {
                                                         --   "basic": {"enabled": true, "priority": 1, "config": {...}},
                                                         --   "advanced": {"enabled": false, "priority": 2, "config": {...}},
                                                         --   "graph": {"enabled": true, "priority": 3, "config": {...}},
                                                         --   "hybrid": {"enabled": false, "priority": 4, "config": {...}},
                                                         --   "multi_step": {"enabled": true, "priority": 5, "config": {...}}
                                                         -- }
                
                -- Document Type Support (JSON for better framework capabilities)
                supported_file_types_config TEXT DEFAULT '{}', -- JSON: {
                                                              --   "documents": {"extensions": [".pdf", ".docx", ".txt"], "enabled": true, "processor": "DocumentProcessor"},
                                                              --   "images": {"extensions": [".jpg", ".png", ".gif"], "enabled": true, "processor": "ImageProcessor"},
                                                              --   "code": {"extensions": [".py", ".js", ".java"], "enabled": true, "processor": "CodeProcessor"},
                                                              --   "spreadsheets": {"extensions": [".xlsx", ".csv"], "enabled": true, "processor": "SpreadsheetProcessor"},
                                                              --   "cad": {"extensions": [".dwg", ".step", ".stl"], "enabled": true, "processor": "CADProcessor"},
                                                              --   "graph_data": {"extensions": [".graphml", ".gml"], "enabled": true, "processor": "GraphDataProcessor"},
                                                              --   "structured_data": {"extensions": [".json", ".yaml", ".xml"], "enabled": true, "processor": "StructuredDataProcessor"}
                                                              -- }
                
                -- Document Processor Capabilities (JSON for framework capabilities)
                processor_capabilities_config TEXT DEFAULT '{}', -- JSON: {
                                                                 --   "DocumentProcessor": {"ocr_enabled": true, "image_extraction": true, "text_processing": true},
                                                                 --   "ImageProcessor": {"tesseract": true, "easyocr": true, "paddleocr": true},
                                                                 --   "CodeProcessor": {"syntax_highlighting": true, "semantic_analysis": true, "dependency_analysis": true},
                                                                 --   "SpreadsheetProcessor": {"semantic_analysis": true, "pattern_detection": true, "data_quality": true},
                                                                 --   "CADProcessor": {"technical_analysis": true, "metadata_extraction": true, "3d_analysis": true}
                                                                 -- }
                
                -- Performance & Quality Metrics (Framework Performance)
                performance_score REAL DEFAULT 0.0 CHECK (performance_score >= 0.0 AND performance_score <= 1.0),
                data_quality_score REAL DEFAULT 0.0 CHECK (data_quality_score >= 0.0 AND data_quality_score <= 1.0),
                reliability_score REAL DEFAULT 0.0 CHECK (reliability_score >= 0.0 AND reliability_score <= 1.0),
                compliance_score REAL DEFAULT 0.0 CHECK (compliance_score >= 0.0 AND compliance_score <= 1.0),
                
                -- Security & Access Control (Framework Security)
                security_level TEXT DEFAULT 'standard' CHECK (security_level IN ('public', 'internal', 'confidential', 'secret', 'top_secret')),
                access_control_level TEXT DEFAULT 'user' CHECK (access_control_level IN ('public', 'user', 'admin', 'system', 'restricted')),
                encryption_enabled BOOLEAN DEFAULT FALSE,
                audit_logging_enabled BOOLEAN DEFAULT TRUE,
                
                -- User Management & Ownership (Framework Access Control)
                user_id TEXT NOT NULL,
                org_id TEXT NOT NULL,
                owner_team TEXT,
                steward_user_id TEXT,
                
                -- Timestamps & Audit (Framework Audit Trail)
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                activated_at TEXT,
                last_accessed_at TEXT,
                last_modified_at TEXT,
                
                -- Configuration & Metadata (Framework Configuration - JSON)
                registry_config TEXT DEFAULT '{}',      -- JSON: Framework settings, not data
                registry_metadata TEXT DEFAULT '{}',    -- JSON: Framework metadata, not content
                custom_attributes TEXT DEFAULT '{}',    -- JSON: Custom framework attributes
                tags_config TEXT DEFAULT '{}',          -- JSON: {"tags": ["ai", "rag", "nlp"], "categories": ["ml", "ai"], "keywords": ["vector", "embedding"]}
                
                -- Relationships & Dependencies (Framework Dependencies - JSON)
                relationships_config TEXT DEFAULT '{}', -- JSON: {"depends_on": ["twin_registry", "kg_neo4j"], "provides_to": ["certificate_manager"], "integrates_with": ["aasx_processing"]}
                dependencies_config TEXT DEFAULT '{}',  -- JSON: {"required_modules": ["vector_db", "embedding_models"], "optional_modules": ["neo4j", "physics_modeling"]}
                rag_instances_config TEXT DEFAULT '{}', -- JSON: {"active_instances": ["instance_1", "instance_2"], "instance_configs": {...}}
                
                -- Foreign Key Constraints
                FOREIGN KEY (file_id) REFERENCES files (file_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                FOREIGN KEY (org_id) REFERENCES organizations (org_id) ON DELETE CASCADE,
                FOREIGN KEY (aasx_integration_id) REFERENCES aasx_processing (job_id) ON DELETE SET NULL,
                FOREIGN KEY (twin_registry_id) REFERENCES twin_registry (registry_id) ON DELETE SET NULL,
                FOREIGN KEY (kg_neo4j_id) REFERENCES kg_graph_registry (graph_id) ON DELETE SET NULL
            )
        """
        self.db_manager.execute_update(query)
        
        # Create world-class indexes for AI/RAG registry table
        ai_rag_registry_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_file_id ON ai_rag_registry (file_id)",
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_user_id ON ai_rag_registry (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_org_id ON ai_rag_registry (org_id)",
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_category ON ai_rag_registry (rag_category)",
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_type ON ai_rag_registry (rag_type)",
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_status ON ai_rag_registry (integration_status)",
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_health ON ai_rag_registry (health_status)",
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_lifecycle ON ai_rag_registry (lifecycle_status)",
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_embedding ON ai_rag_registry (embedding_generation_status, vector_db_sync_status)",
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_created ON ai_rag_registry (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_updated ON ai_rag_registry (updated_at)",
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_workflow ON ai_rag_registry (workflow_source, registry_type)",
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_integration ON ai_rag_registry (aasx_integration_id, twin_registry_id, kg_neo4j_id)",
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_performance ON ai_rag_registry (performance_score, data_quality_score, reliability_score)"
        ]
        
        for index_query in ai_rag_registry_indexes:
            try:
                self.db_manager.execute_update(index_query)
            except Exception as e:
                logger.warning(f"Failed to create AI/RAG registry index: {e}")
        
        logger.info("Created world-class AI/RAG registry table with comprehensive fields and indexes")
    
    def _create_ai_rag_metrics_table(self):
        """Create the AI/RAG metrics table with comprehensive performance monitoring."""
        query = """
            CREATE TABLE IF NOT EXISTS ai_rag_metrics (
                -- Primary Identification
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                registry_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                
                -- Real-time Health Metrics (Framework Health)
                health_score INTEGER CHECK (health_score >= 0 AND health_score <= 100),
                response_time_ms REAL,
                uptime_percentage REAL CHECK (uptime_percentage >= 0.0 AND uptime_percentage <= 100.0),
                error_rate REAL CHECK (error_rate >= 0.0 AND error_rate <= 1.0),
                
                -- AI/RAG Performance Metrics (Framework Performance - NOT Data)
                embedding_generation_speed_sec REAL,           -- Time to generate embeddings
                vector_db_query_response_time_ms REAL,         -- Vector DB query performance
                rag_response_generation_time_ms REAL,          -- RAG response generation time
                context_retrieval_accuracy REAL CHECK (context_retrieval_accuracy >= 0.0 AND context_retrieval_accuracy <= 1.0),
                
                -- RAG Technique Performance (JSON for better framework analysis)
                rag_technique_performance TEXT DEFAULT '{}',   -- JSON: {
                                                               --   "basic": {"usage_count": 150, "avg_response_time": 2.3, "success_rate": 0.98, "last_used": "2024-01-15T10:30:00Z"},
                                                               --   "advanced": {"usage_count": 75, "avg_response_time": 5.7, "success_rate": 0.95, "last_used": "2024-01-15T09:15:00Z"},
                                                               --   "graph": {"usage_count": 45, "avg_response_time": 3.2, "success_rate": 0.92, "last_used": "2024-01-15T08:45:00Z"},
                                                               --   "hybrid": {"usage_count": 60, "avg_response_time": 4.1, "success_rate": 0.96, "last_used": "2024-01-15T10:00:00Z"},
                                                               --   "multi_step": {"usage_count": 30, "avg_response_time": 8.9, "success_rate": 0.88, "last_used": "2024-01-15T07:30:00Z"}
                                                               -- }
                
                -- Document Processing Metrics (JSON for better framework analysis)
                document_processing_stats TEXT DEFAULT '{}',   -- JSON: {
                                                               --   "documents": {"processed": 250, "successful": 245, "failed": 5, "avg_processing_time": 1.2, "file_types": {".pdf": 120, ".docx": 80, ".txt": 50}},
                                                               --   "images": {"processed": 180, "successful": 175, "failed": 5, "avg_processing_time": 2.8, "file_types": {".jpg": 100, ".png": 60, ".gif": 20}},
                                                               --   "code": {"processed": 320, "successful": 315, "failed": 5, "avg_processing_time": 0.8, "file_types": {".py": 150, ".js": 80, ".java": 50, ".cpp": 40}},
                                                               --   "spreadsheets": {"processed": 95, "successful": 92, "failed": 3, "avg_processing_time": 1.5, "file_types": {".xlsx": 60, ".csv": 25, ".ods": 10}},
                                                               --   "cad": {"processed": 45, "successful": 42, "failed": 3, "avg_processing_time": 4.2, "file_types": {".dwg": 20, ".step": 15, ".stl": 10}},
                                                               --   "graph_data": {"processed": 30, "successful": 28, "failed": 2, "avg_processing_time": 2.1, "file_types": {".graphml": 20, ".gml": 10}},
                                                               --   "structured_data": {"processed": 110, "successful": 108, "failed": 2, "avg_processing_time": 0.6, "file_types": {".json": 70, ".yaml": 25, ".xml": 15}}
                                                               -- }
                
                -- User Interaction Metrics (Framework Usage - NOT Content)
                user_interaction_count INTEGER DEFAULT 0,      -- Number of user interactions
                query_execution_count INTEGER DEFAULT 0,       -- Number of queries executed
                successful_rag_operations INTEGER DEFAULT 0,   -- Successful operations
                failed_rag_operations INTEGER DEFAULT 0,       -- Failed operations
                
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
                
                -- Performance Trends (Framework Trends - JSON)
                performance_trends TEXT DEFAULT '{}',           -- JSON: {"hourly": {...}, "daily": {...}, "weekly": {...}, "monthly": {...}}
                resource_utilization_trends TEXT DEFAULT '{}', -- JSON: {"cpu_trend": [...], "memory_trend": [...], "network_trend": [...]}
                user_activity TEXT DEFAULT '{}',               -- JSON: {"peak_hours": [...], "user_patterns": {...}, "session_durations": [...]}
                query_patterns TEXT DEFAULT '{}',              -- JSON: {"query_types": {...}, "complexity_distribution": {...}, "response_times": [...]}
                compliance_status TEXT DEFAULT '{}',           -- JSON: {"compliance_score": 0.95, "audit_status": "passed", "last_audit": "2024-01-15T00:00:00Z"}
                security_events TEXT DEFAULT '{}',             -- JSON: {"events": [...], "threat_level": "low", "last_security_scan": "2024-01-15T00:00:00Z"}
                
                -- AI/RAG-Specific Metrics (Framework Capabilities - JSON)
                rag_analytics TEXT DEFAULT '{}',               -- JSON: {"embedding_quality": 0.92, "retrieval_accuracy": 0.89, "generation_quality": 0.94}
                technique_effectiveness TEXT DEFAULT '{}',     -- JSON: {"technique_comparison": {...}, "best_performing": "hybrid", "optimization_suggestions": [...]}
                model_performance TEXT DEFAULT '{}',           -- JSON: {"embedding_model": {...}, "llm_model": {...}, "model_versions": [...]}
                file_type_processing_efficiency TEXT DEFAULT '{}', -- JSON: {"processing_speed_by_type": {...}, "quality_by_type": {...}, "optimization_opportunities": [...]}
                
                -- Foreign Key Constraints
                FOREIGN KEY (registry_id) REFERENCES ai_rag_registry (registry_id) ON DELETE CASCADE
            )
        """
        self.db_manager.execute_update(query)
        
        # Create world-class indexes for AI/RAG metrics table
        ai_rag_metrics_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_metrics_registry_id ON ai_rag_metrics (registry_id)",
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_metrics_timestamp ON ai_rag_metrics (timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_metrics_health ON ai_rag_metrics (health_score)",
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_metrics_performance ON ai_rag_metrics (embedding_generation_speed_sec, vector_db_query_response_time_ms)",
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_metrics_quality ON ai_rag_metrics (data_freshness_score, data_completeness_score)",
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_metrics_resources ON ai_rag_metrics (cpu_usage_percent, memory_usage_percent)",
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_metrics_user_activity ON ai_rag_metrics (user_interaction_count, query_execution_count)",
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_metrics_technique ON ai_rag_metrics (rag_technique_performance)",
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_metrics_document_processing ON ai_rag_metrics (document_processing_stats)"
        ]
        
        for index_query in ai_rag_metrics_indexes:
            try:
                self.db_manager.execute_update(index_query)
            except Exception as e:
                logger.warning(f"Failed to create AI/RAG metrics index: {e}")
        
        logger.info("Created world-class AI/RAG metrics table with comprehensive fields and indexes")
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """Get information about a table."""
        return self.db_manager.get_table_schema(table_name)
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        return self.db_manager.table_exists(table_name)
    
    def get_all_tables(self) -> List[str]:
        """Get all table names in the database."""
        query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """
        results = self.db_manager.execute_query(query)
        return [row['name'] for row in results] 