"""
Async Base Database Manager
==========================

Async base class for database operations with common functionality.
Provides async support for the Knowledge Graph module and future async adoption.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import sqlite3
import aiosqlite

from .connection_manager import DatabaseConnectionManager

logger = logging.getLogger(__name__)

class AsyncBaseDatabaseManager:
    """Async base class for database operations."""
    
    def __init__(self, connection_manager: DatabaseConnectionManager):
        self.connection_manager = connection_manager
        self.db_path = connection_manager.db_path
        self._async_connection: Optional[aiosqlite.Connection] = None
    
    async def get_async_connection(self) -> aiosqlite.Connection:
        """Get an async database connection, creating one if it doesn't exist."""
        if self._async_connection is None:
            self._async_connection = await self._create_async_connection()
        return self._async_connection
    
    async def _create_async_connection(self) -> aiosqlite.Connection:
        """Create a new async database connection."""
        try:
            # Handle in-memory database
            if str(self.db_path) == ":memory:":
                connection = await aiosqlite.connect(":memory:")
            else:
                # Ensure database directory exists for file-based databases
                self.db_path.parent.mkdir(parents=True, exist_ok=True)
                connection = await aiosqlite.connect(str(self.db_path))
            
            # Configure connection
            connection.row_factory = aiosqlite.Row  # Return rows as dictionaries
            
            # Enable foreign keys
            await connection.execute("PRAGMA foreign_keys = ON")
            
            # Only use WAL mode for file-based databases
            if str(self.db_path) != ":memory:":
                await connection.execute("PRAGMA journal_mode = WAL")
            
            logger.info(f"Async database connection established: {self.db_path}")
            return connection
            
        except Exception as e:
            logger.error(f"Failed to create async database connection: {e}")
            raise
    
    async def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a query asynchronously and return results as dictionaries."""
        try:
            connection = await self.get_async_connection()
            async with connection.execute(query, params) as cursor:
                results = await cursor.fetchall()
                return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Async query execution failed: {e}")
            raise
    
    async def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an update query asynchronously and return affected rows."""
        try:
            connection = await self.get_async_connection()
            async with connection.execute(query, params) as cursor:
                await connection.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Async update execution failed: {e}")
            raise
    
    async def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute an insert query asynchronously and return the last row ID."""
        try:
            connection = await self.get_async_connection()
            async with connection.execute(query, params) as cursor:
                await connection.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Async insert execution failed: {e}")
            raise
    
    async def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database asynchronously."""
        query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """
        results = await self.execute_query(query, (table_name,))
        return len(results) > 0
    
    async def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Get the schema for a table asynchronously."""
        query = f"PRAGMA table_info({table_name})"
        return await self.execute_query(query, ())
    
    async def begin_transaction(self):
        """Begin a database transaction asynchronously."""
        connection = await self.get_async_connection()
        await connection.execute("BEGIN TRANSACTION")
    
    async def commit_transaction(self):
        """Commit the current transaction asynchronously."""
        connection = await self.get_async_connection()
        await connection.commit()
    
    async def rollback_transaction(self):
        """Rollback the current transaction asynchronously."""
        connection = await self.get_async_connection()
        await connection.rollback()
    
    async def close(self):
        """Close the async database connection."""
        if self._async_connection:
            await self._async_connection.close()
            self._async_connection = None
            logger.info("Async database connection closed")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()



