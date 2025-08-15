"""
Database Schema Manager
======================

Handles database schema creation, migration, and management.
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
            # Create tables in dependency order
            self._create_organizations_table()
            self._create_users_table()
            self._create_use_cases_table()
            self._create_projects_table()
            self._create_files_table()
            self._create_digital_twins_table()
            self._create_project_use_case_links_table()
            self._create_aasx_processing_table()
            self._create_aasx_processing_metrics_table()  # Phase 4.2: Comprehensive metrics
            
            logger.info("All database tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    def _create_organizations_table(self):
        """Create the organizations table."""
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
                updated_at TEXT NOT NULL
            )
        """
        self.db_manager.execute_update(query)
        logger.info("Created organizations table")
    
    def _create_use_cases_table(self):
        """Create the use_cases table."""
        query = """
            CREATE TABLE IF NOT EXISTS use_cases (
                use_case_id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                category TEXT DEFAULT 'general',
                is_active BOOLEAN DEFAULT 1,
                metadata TEXT DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """
        self.db_manager.execute_update(query)
        logger.info("Created use_cases table")
    
    def _create_projects_table(self):
        """Create the projects table."""
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
                updated_at TEXT NOT NULL
            )
        """
        self.db_manager.execute_update(query)
        logger.info("Created projects table")
    
    def _create_files_table(self):
        """Create the files table."""
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
                FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE SET NULL
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
    
    def _create_digital_twins_table(self):
        """Create the digital_twins table with enhanced health monitoring and federated learning support."""
        query = """
        CREATE TABLE IF NOT EXISTS digital_twins (
            twin_id TEXT PRIMARY KEY,
            twin_name TEXT NOT NULL,
            file_id TEXT NOT NULL UNIQUE,
            status TEXT DEFAULT 'active',
            metadata TEXT DEFAULT '{}',
            
            -- Health monitoring columns
            health_status TEXT DEFAULT 'unknown',
            last_health_check TEXT,
            health_score INTEGER DEFAULT 0,
            error_count INTEGER DEFAULT 0,
            last_error_message TEXT,
            maintenance_required BOOLEAN DEFAULT 0,
            next_maintenance_date TEXT,
            
            -- Physics modeling integration columns
            extracted_data_path TEXT,
            physics_context TEXT DEFAULT '{}',
            simulation_history TEXT DEFAULT '[]',
            last_simulation_run TEXT,
            simulation_status TEXT DEFAULT 'pending',
            model_version TEXT,
            
            -- Federated Learning Standard Fields
            federated_node_id TEXT,
            federated_participation_status TEXT DEFAULT 'inactive',
            federated_model_version TEXT,
            federated_last_sync TEXT,
            federated_contribution_score INTEGER DEFAULT 0,
            federated_round_number INTEGER DEFAULT 0,
            federated_health_status TEXT DEFAULT 'unknown',
            
            -- Privacy & Security Standard Fields
            data_privacy_level TEXT DEFAULT 'private',
            data_sharing_permissions TEXT DEFAULT '{}',
            differential_privacy_epsilon REAL DEFAULT 1.0,
            secure_aggregation_enabled BOOLEAN DEFAULT 1,
            
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (file_id) REFERENCES files (file_id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(query)
    
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
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                FOREIGN KEY (job_id) REFERENCES aasx_processing (id) ON DELETE CASCADE
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
    
    def _create_users_table(self):
        """Create the users table."""
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
                FOREIGN KEY (org_id) REFERENCES organizations (org_id) ON DELETE SET NULL
            )
        """
        self.db_manager.execute_update(query)
        logger.info("Created users table")
    
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