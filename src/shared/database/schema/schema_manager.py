"""
Modular Database Schema Manager
===============================

Coordinates all database schema modules for the AASX Digital Twin Framework.
This is the new, modular approach that replaces the monolithic schema manager.
"""

import logging
from typing import List, Dict, Any, Optional
from ..base_manager import BaseDatabaseManager
from .modules import get_all_schema_modules, get_schema_module

logger = logging.getLogger(__name__)


class ModularSchemaManager:
    """
    Modular Database Schema Manager
    
    Coordinates all schema modules instead of having all table creation
    logic in one massive file. This provides:
    - Better organization and maintainability
    - Easier testing and debugging
    - Clear separation of concerns
    - Scalability for new modules
    """
    
    def __init__(self, db_manager: BaseDatabaseManager):
        """
        Initialize the modular schema manager.
        
        Args:
            db_manager: Database manager instance for executing queries
        """
        self.db_manager = db_manager
        self.schema_modules = {}
        self.module_results = {}
        
        # Initialize all available schema modules
        self._initialize_modules()
        
        logger.info(f"🔧 Modular Schema Manager initialized with {len(self.schema_modules)} modules")
    
    def _initialize_modules(self):
        """Initialize all available schema modules."""
        available_modules = get_all_schema_modules()
        
        for module_name, module_class in available_modules.items():
            try:
                module_instance = module_class(self.db_manager)
                self.schema_modules[module_name] = module_instance
                logger.info(f"✅ Initialized schema module: {module_name}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize schema module {module_name}: {e}")
    
    def create_all_tables(self) -> bool:
        """
        Create all tables from all schema modules.
        
        Returns:
            bool: True if all tables created successfully, False otherwise
        """
        logger.info("🚀 Creating all database tables using modular approach...")
        
        all_success = True
        total_tables = 0
        successful_tables = 0
        
        # Create tables from each module
        for module_name, module_instance in self.schema_modules.items():
            logger.info(f"🔧 Creating tables for module: {module_name}")
            
            try:
                # Create tables for this module
                module_success = module_instance.create_tables()
                
                if module_success:
                    # Get module summary
                    module_summary = module_instance.get_module_summary()
                    module_tables = module_summary['total_tables']
                    total_tables += module_tables
                    successful_tables += module_tables
                    
                    logger.info(f"✅ {module_name}: Created {module_tables} tables successfully")
                    self.module_results[module_name] = {
                        'status': 'success',
                        'tables_created': module_tables,
                        'summary': module_summary
                    }
                else:
                    logger.error(f"❌ {module_name}: Failed to create tables")
                    self.module_results[module_name] = {
                        'status': 'failed',
                        'tables_created': 0,
                        'summary': None
                    }
                    all_success = False
                    
            except Exception as e:
                logger.error(f"❌ {module_name}: Exception during table creation: {e}")
                self.module_results[module_name] = {
                    'status': 'error',
                    'tables_created': 0,
                    'summary': None,
                    'error': str(e)
                }
                all_success = False
        
        # Log final results
        if all_success:
            logger.info(f"🎉 All database tables created successfully!")
            logger.info(f"📊 Total tables created: {total_tables}")
        else:
            logger.error(f"❌ Some database tables failed to create")
            logger.info(f"📊 Successful tables: {successful_tables}/{total_tables}")
        
        return all_success
    
    def create_module_tables(self, module_name: str) -> bool:
        """
        Create tables for a specific module.
        
        Args:
            module_name: Name of the module to create tables for
            
        Returns:
            bool: True if tables created successfully, False otherwise
        """
        if module_name not in self.schema_modules:
            logger.error(f"❌ Schema module '{module_name}' not found")
            return False
        
        module_instance = self.schema_modules[module_name]
        logger.info(f"🔧 Creating tables for module: {module_name}")
        
        try:
            success = module_instance.create_tables()
            if success:
                logger.info(f"✅ {module_name}: Tables created successfully")
            else:
                logger.error(f"❌ {module_name}: Failed to create tables")
            return success
        except Exception as e:
            logger.error(f"❌ {module_name}: Exception during table creation: {e}")
            return False
    
    def validate_all_modules(self) -> Dict[str, Dict[str, Any]]:
        """
        Validate all schema modules.
        
        Returns:
            Dict mapping module names to validation results
        """
        validation_results = {}
        
        for module_name, module_instance in self.schema_modules.items():
            try:
                module_summary = module_instance.get_module_summary()
                validation_results[module_name] = module_summary
                
                if module_summary['all_tables_valid']:
                    logger.info(f"✅ {module_name}: All tables valid")
                else:
                    logger.warning(f"⚠️ {module_name}: Some tables invalid")
                    
            except Exception as e:
                logger.error(f"❌ {module_name}: Validation failed: {e}")
                validation_results[module_name] = {
                    'module_name': module_name,
                    'error': str(e),
                    'all_tables_valid': False
                }
        
        return validation_results
    
    def get_module_status(self, module_name: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific module.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Module status dictionary or None if not found
        """
        if module_name not in self.schema_modules:
            return None
        
        module_instance = self.schema_modules[module_name]
        return module_instance.get_module_summary()
    
    def get_all_modules_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all modules.
        
        Returns:
            Dict mapping module names to their status
        """
        return {
            module_name: module_instance.get_module_summary()
            for module_name, module_instance in self.schema_modules.items()
        }
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get information about a table's schema.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of column information
        """
        try:
            query = f"PRAGMA table_info({table_name})"
            result = self.db_manager.execute_query(query)
            return result
        except Exception as e:
            logger.error(f"Error getting table info for {table_name}: {e}")
            return []
    
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
    
    def get_all_tables(self) -> List[str]:
        """
        Get all table names in the database.
        
        Returns:
            List of table names
        """
        query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """
        try:
            results = self.db_manager.execute_query(query)
            return [row['name'] for row in results]
        except Exception as e:
            logger.error(f"Error getting all tables: {e}")
            return []
    
    def get_creation_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of table creation results.
        
        Returns:
            Dictionary with creation summary
        """
        total_modules = len(self.schema_modules)
        successful_modules = sum(
            1 for result in self.module_results.values() 
            if result['status'] == 'success'
        )
        failed_modules = total_modules - successful_modules
        
        total_tables = sum(
            result['tables_created'] 
            for result in self.module_results.values() 
            if result['status'] == 'success'
        )
        
        return {
            'total_modules': total_modules,
            'successful_modules': successful_modules,
            'failed_modules': failed_modules,
            'total_tables': total_tables,
            'module_results': self.module_results,
            'all_successful': failed_modules == 0
        }
