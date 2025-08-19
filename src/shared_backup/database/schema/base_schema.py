"""
Base Schema Module
==================

Abstract base class for all database schema modules.
Provides common interface and utilities for table creation and management.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from .base_manager import BaseDatabaseManager

logger = logging.getLogger(__name__)


class BaseSchemaModule(ABC):
    """
    Abstract base class for all database schema modules.
    
    Each module (core_system, ai_rag, twin_registry, etc.) should inherit
    from this class and implement the required methods.
    """
    
    def __init__(self, db_manager: BaseDatabaseManager):
        """
        Initialize the schema module.
        
        Args:
            db_manager: Database manager instance for executing queries
        """
        self.db_manager = db_manager
        self.module_name = self.__class__.__name__.replace('Schema', '').lower()
        logger.info(f"Initializing {self.module_name} schema module")
    
    @abstractmethod
    def create_tables(self) -> bool:
        """
        Create all tables for this module.
        
        Returns:
            bool: True if all tables created successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def get_table_names(self) -> List[str]:
        """
        Get list of table names managed by this module.
        
        Returns:
            List[str]: List of table names
        """
        pass
    
    @abstractmethod
    def get_module_description(self) -> str:
        """
        Get human-readable description of this module.
        
        Returns:
            str: Module description
        """
        pass
    
    def create_table(self, table_name: str, query: str) -> bool:
        """
        Create a single table with error handling.
        
        Args:
            table_name: Name of the table to create
            query: SQL CREATE TABLE query
            
        Returns:
            bool: True if table created successfully, False otherwise
        """
        try:
            self.db_manager.execute_update(query)
            logger.info(f"✅ Created table: {table_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create table {table_name}: {e}")
            return False
    
    def create_indexes(self, table_name: str, index_queries: List[str]) -> bool:
        """
        Create indexes for a table with error handling.
        
        Args:
            table_name: Name of the table
            index_queries: List of CREATE INDEX queries
            
        Returns:
            bool: True if all indexes created successfully, False otherwise
        """
        success_count = 0
        total_count = len(index_queries)
        
        for index_query in index_queries:
            try:
                self.db_manager.execute_update(index_query)
                success_count += 1
            except Exception as e:
                logger.warning(f"Failed to create index for {table_name}: {e}")
        
        if success_count == total_count:
            logger.info(f"✅ Created all {total_count} indexes for {table_name}")
            return True
        elif success_count > 0:
            logger.warning(f"⚠️ Created {success_count}/{total_count} indexes for {table_name}")
            return True
        else:
            logger.error(f"❌ Failed to create any indexes for {table_name}")
            return False
    
    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists.
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            bool: True if table exists, False otherwise
        """
        try:
            query = """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """
            result = self.db_manager.execute_query(query, [table_name])
            return len(result) > 0
        except Exception as e:
            logger.error(f"Error checking if table {table_name} exists: {e}")
            return False
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get information about a table's schema.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List[Dict[str, Any]]: List of column information
        """
        try:
            query = f"PRAGMA table_info({table_name})"
            result = self.db_manager.execute_query(query)
            return result
        except Exception as e:
            logger.error(f"Error getting table info for {table_name}: {e}")
            return []
    
    def validate_module_tables(self) -> Dict[str, bool]:
        """
        Validate that all expected tables exist and have correct structure.
        
        Returns:
            Dict[str, bool]: Dictionary mapping table names to validation status
        """
        validation_results = {}
        expected_tables = self.get_table_names()
        
        for table_name in expected_tables:
            exists = self.table_exists(table_name)
            validation_results[table_name] = exists
            
            if exists:
                logger.info(f"✅ Table validation passed: {table_name}")
            else:
                logger.error(f"❌ Table validation failed: {table_name}")
        
        return validation_results
    
    def get_module_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of this module.
        
        Returns:
            Dict[str, Any]: Module summary including table count, status, etc.
        """
        table_names = self.get_table_names()
        validation_results = self.validate_module_tables()
        
        summary = {
            'module_name': self.module_name,
            'description': self.get_module_description(),
            'total_tables': len(table_names),
            'tables': table_names,
            'validation_status': validation_results,
            'all_tables_valid': all(validation_results.values()),
            'valid_table_count': sum(validation_results.values()),
            'invalid_table_count': len(validation_results) - sum(validation_results.values())
        }
        
        return summary
