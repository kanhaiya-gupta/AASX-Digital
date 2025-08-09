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
    
    def _create_users_table(self):
        """Create the users table."""
        query = """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                email TEXT UNIQUE,
                full_name TEXT,
                org_id TEXT,
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