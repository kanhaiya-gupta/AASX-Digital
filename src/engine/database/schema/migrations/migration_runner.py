"""
Migration Runner
===============

High-level orchestrator for database migrations. Provides CLI interface,
batch operations, workflow management, and coordination of multiple
migration managers.
"""

import logging
import asyncio
import argparse
import sys
from typing import Any, Dict, List, Optional, Union, Set
from pathlib import Path
from datetime import datetime
import json

from .migration_manager import MigrationManager
from ..base_schema import BaseSchema
from ...connection_manager import ConnectionManager

logger = logging.getLogger(__name__)


class MigrationRunner:
    """Orchestrates database migrations and provides CLI interface"""
    
    def __init__(self, connection_manager: ConnectionManager, schema_name: str = "default"):
        """
        Initialize the migration runner.
        
        Args:
            connection_manager: Database connection manager instance
            schema_name: Name of the schema to manage
        """
        self.connection_manager = connection_manager
        self.schema_name = schema_name
        self.migration_manager = MigrationManager(connection_manager, schema_name)
        self.logger = logging.getLogger(f"{__name__}.{schema_name}")
        
    async def initialize(self) -> bool:
        """Initialize the migration runner and manager."""
        try:
            if not await self.migration_manager.initialize():
                self.logger.error("Failed to initialize migration manager")
                return False
                
            self.logger.info(f"✅ Migration runner initialized for schema: {self.schema_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize migration runner: {e}")
            return False
    
    async def run_migration(self, migration_id: str, force: bool = False) -> Dict[str, Any]:
        """
        Run a specific migration.
        
        Args:
            migration_id: ID of the migration to run
            force: Force execution even if dependencies aren't met
            
        Returns:
            Dict containing execution results
        """
        try:
            self.logger.info(f"🚀 Running migration: {migration_id}")
            
            if not force:
                # Check dependencies
                pending_migrations = await self.migration_manager.get_pending_migrations()
                target_migration = None
                
                for migration in pending_migrations:
                    if migration['migration_id'] == migration_id:
                        target_migration = migration
                        break
                
                if not target_migration:
                    return {
                        'success': False,
                        'error': f'Migration {migration_id} not found in pending migrations',
                        'migration_id': migration_id
                    }
            
            # Execute migration
            success = await self.migration_manager.apply_migration(migration_id)
            
            if success:
                return {
                    'success': True,
                    'migration_id': migration_id,
                    'message': f'Migration {migration_id} executed successfully'
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to execute migration {migration_id}',
                    'migration_id': migration_id
                }
                
        except Exception as e:
            self.logger.error(f"❌ Error running migration {migration_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'migration_id': migration_id
            }
    
    async def run_all_pending_migrations(self, force: bool = False) -> Dict[str, Any]:
        """
        Run all pending migrations.
        
        Args:
            force: Force execution even if dependencies aren't met
            
        Returns:
            Dict containing execution results
        """
        try:
            self.logger.info("🚀 Running all pending migrations...")
            
            if not force:
                # Get pending migrations
                pending_migrations = await self.migration_manager.get_pending_migrations()
                
                if not pending_migrations:
                    return {
                        'success': True,
                        'message': 'No pending migrations',
                        'total_migrations': 0,
                        'executed_migrations': []
                    }
                
                # Execute all pending migrations
                results = []
                for migration in pending_migrations:
                    migration_id = migration['migration_id']
                    result = await self.run_migration(migration_id, force=False)
                    results.append(result)
                    
                    if not result['success']:
                        # Stop on first failure
                        return {
                            'success': False,
                            'error': f'Migration {migration_id} failed: {result["error"]}',
                            'total_migrations': len(pending_migrations),
                            'executed_migrations': [r for r in results if r['success']],
                            'failed_migrations': [r for r in results if not r['success']]
                        }
                
                return {
                    'success': True,
                    'message': f'All {len(pending_migrations)} migrations executed successfully',
                    'total_migrations': len(pending_migrations),
                    'executed_migrations': results
                }
            else:
                # Force execution using migration manager's method
                return await self.migration_manager.apply_all_pending_migrations()
                
        except Exception as e:
            self.logger.error(f"❌ Error running all pending migrations: {e}")
            return {
                'success': False,
                'error': str(e),
                'total_migrations': 0,
                'executed_migrations': []
            }
    
    async def rollback_migration(self, migration_id: str) -> Dict[str, Any]:
        """
        Rollback a specific migration.
        
        Args:
            migration_id: ID of the migration to rollback
            
        Returns:
            Dict containing rollback results
        """
        try:
            self.logger.info(f"🔄 Rolling back migration: {migration_id}")
            
            success = await self.migration_manager.rollback_migration(migration_id)
            
            if success:
                return {
                    'success': True,
                    'migration_id': migration_id,
                    'message': f'Migration {migration_id} rolled back successfully'
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to rollback migration {migration_id}',
                    'migration_id': migration_id
                }
                
        except Exception as e:
            self.logger.error(f"❌ Error rolling back migration {migration_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'migration_id': migration_id
            }
    
    async def get_migration_status(self) -> Dict[str, Any]:
        """Get comprehensive migration status."""
        try:
            return await self.migration_manager.get_migration_status()
        except Exception as e:
            self.logger.error(f"❌ Error getting migration status: {e}")
            return {
                'schema_name': self.schema_name,
                'error': str(e),
                'status': 'error'
            }
    
    async def validate_migration_scripts(self, migrations_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        Validate all migration scripts in a directory.
        
        Args:
            migrations_dir: Directory containing migration scripts
            
        Returns:
            Dict containing validation results
        """
        try:
            if migrations_dir:
                self.migration_manager.set_migrations_directory(migrations_dir)
            
            # Scan migration scripts
            await self.migration_manager._scan_migration_scripts()
            
            # Get migration info
            pending_migrations = await self.migration_manager.get_pending_migrations()
            applied_migrations = await self.migration_manager.get_applied_migrations()
            
            validation_results = {
                'schema_name': self.schema_name,
                'total_scripts': len(pending_migrations) + len(applied_migrations),
                'pending_migrations': len(pending_migrations),
                'applied_migrations': len(applied_migrations),
                'validation_passed': True,
                'issues': []
            }
            
            # Validate each migration script
            for migration in pending_migrations:
                migration_id = migration['migration_id']
                
                # Check for required fields
                required_fields = ['migration_id', 'version', 'name', 'script_content']
                for field in required_fields:
                    if field not in migration or not migration[field]:
                        validation_results['validation_passed'] = False
                        validation_results['issues'].append({
                            'migration_id': migration_id,
                            'issue': f'Missing or empty required field: {field}',
                            'severity': 'error'
                        })
                
                # Check script content
                if 'script_content' in migration and migration['script_content']:
                    script_content = migration['script_content']
                    
                    # Basic SQL validation
                    if not script_content.strip():
                        validation_results['validation_passed'] = False
                        validation_results['issues'].append({
                            'migration_id': migration_id,
                            'issue': 'Empty migration script',
                            'severity': 'error'
                        })
                    
                    # Check for common SQL keywords
                    sql_keywords = ['CREATE', 'ALTER', 'DROP', 'INSERT', 'UPDATE', 'DELETE']
                    if not any(keyword in script_content.upper() for keyword in sql_keywords):
                        validation_results['issues'].append({
                            'migration_id': migration_id,
                            'issue': 'Script may not contain valid SQL statements',
                            'severity': 'warning'
                        })
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"❌ Error validating migration scripts: {e}")
            return {
                'schema_name': self.schema_name,
                'validation_passed': False,
                'error': str(e),
                'issues': []
            }
    
    async def create_migration_script(self, name: str, description: str = "", 
                                    migrations_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        Create a new migration script template.
        
        Args:
            name: Name of the migration
            description: Description of the migration
            migrations_dir: Directory to create the script in
            
        Returns:
            Dict containing creation results
        """
        try:
            if migrations_dir:
                self.migration_manager.set_migrations_directory(migrations_dir)
            
            if not self.migration_manager._migrations_dir:
                return {
                    'success': False,
                    'error': 'No migrations directory set'
                }
            
            # Get next version number
            existing_migrations = await self.migration_manager.get_applied_migrations()
            next_version = len(existing_migrations) + 1
            
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{next_version:03d}_{name.lower().replace(' ', '_')}_{timestamp}.sql"
            filepath = self.migration_manager._migrations_dir / filename
            
            # Create script template
            script_template = f"""-- Migration: {name}
-- Version: {next_version:03d}
-- Description: {description}
-- Created: {datetime.now().isoformat()}

-- Add your SQL statements here
-- Example:
-- CREATE TABLE example_table (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     name TEXT NOT NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- ROLLBACK:
-- DROP TABLE IF EXISTS example_table;
"""
            
            # Write script file
            filepath.write_text(script_template, encoding='utf-8')
            
            self.logger.info(f"✅ Created migration script: {filepath}")
            
            return {
                'success': True,
                'filepath': str(filepath),
                'filename': filename,
                'version': next_version,
                'message': f'Migration script {filename} created successfully'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error creating migration script: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def print_status(self, status: Dict[str, Any]) -> None:
        """Print migration status in a formatted way."""
        print(f"\n📊 Migration Status for Schema: {status['schema_name']}")
        print("=" * 60)
        
        if 'error' in status:
            print(f"❌ Error: {status['error']}")
            return
        
        print(f"Status: {status['status']}")
        print(f"Applied Migrations: {status['total_applied']}")
        print(f"Pending Migrations: {status['total_pending']}")
        
        if status['total_applied'] > 0:
            print(f"Last Applied: {status['last_applied']}")
        
        if status['total_pending'] > 0:
            print(f"\nPending Migrations:")
            for migration_id in status['pending_migrations']:
                print(f"  - {migration_id}")
    
    def print_validation_results(self, results: Dict[str, Any]) -> None:
        """Print validation results in a formatted way."""
        print(f"\n🔍 Migration Script Validation for Schema: {results['schema_name']}")
        print("=" * 60)
        
        if 'error' in results:
            print(f"❌ Error: {results['error']}")
            return
        
        print(f"Total Scripts: {results['total_scripts']}")
        print(f"Pending: {results['pending_migrations']}")
        print(f"Applied: {results['applied_migrations']}")
        print(f"Validation: {'✅ PASSED' if results['validation_passed'] else '❌ FAILED'}")
        
        if results['issues']:
            print(f"\nIssues Found ({len(results['issues'])}):")
            for issue in results['issues']:
                severity_icon = "❌" if issue['severity'] == 'error' else "⚠️"
                print(f"  {severity_icon} {issue['migration_id']}: {issue['issue']}")


async def main():
    """CLI entry point for migration runner."""
    parser = argparse.ArgumentParser(description='Database Migration Runner')
    parser.add_argument('--schema', default='default', help='Schema name')
    parser.add_argument('--db-path', required=True, help='Database file path')
    parser.add_argument('--migrations-dir', help='Migrations directory path')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    subparsers.add_parser('status', help='Show migration status')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run migrations')
    run_parser.add_argument('--migration-id', help='Specific migration ID to run')
    run_parser.add_argument('--all', action='store_true', help='Run all pending migrations')
    run_parser.add_argument('--force', action='store_true', help='Force execution')
    
    # Rollback command
    rollback_parser = subparsers.add_parser('rollback', help='Rollback migration')
    rollback_parser.add_argument('migration_id', help='Migration ID to rollback')
    
    # Validate command
    subparsers.add_parser('validate', help='Validate migration scripts')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create new migration script')
    create_parser.add_argument('name', help='Migration name')
    create_parser.add_argument('--description', default='', help='Migration description')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        # Create connection manager
        from ....database import DatabaseFactory, DatabaseType
        
        connection_manager = DatabaseFactory.create_connection_manager(
            database_type=DatabaseType.SQLITE,
            connection_config=args.db_path
        )
        
        # Create migration runner
        runner = MigrationRunner(connection_manager, args.schema)
        
        # Initialize
        if not await runner.initialize():
            print("❌ Failed to initialize migration runner")
            sys.exit(1)
        
        # Set migrations directory if provided
        if args.migrations_dir:
            runner.migration_manager.set_migrations_directory(args.migrations_dir)
        
        # Execute command
        if args.command == 'status':
            status = await runner.get_migration_status()
            runner.print_status(status)
            
        elif args.command == 'run':
            if args.migration_id:
                result = await runner.run_migration(args.migration_id, args.force)
                if result['success']:
                    print(f"✅ {result['message']}")
                else:
                    print(f"❌ {result['error']}")
                    sys.exit(1)
            elif args.all:
                result = await runner.run_all_pending_migrations(args.force)
                if result['success']:
                    print(f"✅ {result['message']}")
                else:
                    print(f"❌ {result['error']}")
                    sys.exit(1)
            else:
                print("❌ Please specify --migration-id or --all")
                sys.exit(1)
                
        elif args.command == 'rollback':
            result = await runner.rollback_migration(args.migration_id)
            if result['success']:
                print(f"✅ {result['message']}")
            else:
                print(f"❌ {result['error']}")
                sys.exit(1)
                
        elif args.command == 'validate':
            results = await runner.validate_migration_scripts()
            runner.print_validation_results(results)
            
        elif args.command == 'create':
            result = await runner.create_migration_script(args.name, args.description)
            if result['success']:
                print(f"✅ {result['message']}")
                print(f"📁 File: {result['filepath']}")
            else:
                print(f"❌ {result['error']}")
                sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())




