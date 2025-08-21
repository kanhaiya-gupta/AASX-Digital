"""
Database Schema Management Package
=================================

This package provides comprehensive database schema management including:
- Schema creation and management
- Database migrations
- Schema validation
- Table structure validation

Components:
- BaseSchema: Abstract base class for schema operations
- SchemaManager: Main orchestrator for schema management
- MigrationManager: Handles database schema evolution
- Validators: Schema and data validation components
"""

from .base_schema import BaseSchema
from .schema_manager import SchemaManager
from .migrations import MigrationManager, MigrationRunner

__all__ = [
    'BaseSchema',
    'SchemaManager',
    'MigrationManager',
    'MigrationRunner'
]
