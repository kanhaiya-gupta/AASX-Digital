"""
Database Module
===============

Core database infrastructure for the AAS Data Modeling framework.
Handles database connections, schema management, and base operations.
"""

from .sqlite_manager import SQLiteConnectionManager
from .database_factory import DatabaseFactory, DatabaseType
from .connection_manager import ConnectionManager

__all__ = [
    'SQLiteConnectionManager', 
    'DatabaseFactory',
    'DatabaseType',
    'ConnectionManager'
] 