"""
SQLite Database Connection Manager
==================================

Implements the ConnectionManager interface for SQLite databases.
Supports both sync and async operations.
"""

import sqlite3
import asyncio
import logging
from pathlib import Path
from typing import Optional, Any, Dict, List, Union, Tuple
from contextlib import contextmanager, asynccontextmanager

from .connection_manager import ConnectionManager

logger = logging.getLogger(__name__)

class SQLiteConnectionManager(ConnectionManager):
    """SQLite database connection manager implementing ConnectionManager"""
    
    def __init__(self, connection_config: Union[str, Path, Dict[str, Any]]):
        """
        Initialize SQLite connection manager.
        
        Args:
            connection_config: Database connection configuration
                - For SQLite: Path to database file or ":memory:" for in-memory
        """
        super().__init__(connection_config)
        
        # Handle different config types
        if isinstance(connection_config, (str, Path)):
            self.db_path = Path(connection_config)
        elif isinstance(connection_config, dict):
            self.db_path = Path(connection_config.get('db_path', ':memory:'))
        else:
            self.db_path = Path(':memory:')
        
        self._connection: Optional[sqlite3.Connection] = None
        self._in_transaction: bool = False
        
    def connect(self) -> bool:
        """Establish SQLite database connection"""
        try:
            if self._connection is None:
                self._connection = self._create_connection()
            self._is_connected = True
            logger.info(f"✅ Connected to SQLite: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to SQLite: {e}")
            self._is_connected = False
            return False
    
    async def connect_async(self) -> bool:
        """Establish SQLite database connection asynchronously"""
        return self.connect()
    
    def disconnect(self) -> bool:
        """Close SQLite database connection"""
        try:
            if self._connection:
                self._connection.close()
                self._connection = None
            self._is_connected = False
            logger.info("✅ Disconnected from SQLite")
            return True
        except Exception as e:
            logger.error(f"❌ Error disconnecting from SQLite: {e}")
            return False
    
    async def disconnect_async(self) -> bool:
        """Close SQLite database connection asynchronously"""
        return self.disconnect()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get the active database connection"""
        if not self._is_connected:
            raise ConnectionError("Not connected to SQLite")
        if self._connection is None:
            self._connection = self._create_connection()
        return self._connection
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection."""
        try:
            # Handle in-memory database
            if str(self.db_path) == ":memory:":
                connection = sqlite3.connect(":memory:")
            else:
                # Ensure database directory exists for file-based databases
                self.db_path.parent.mkdir(parents=True, exist_ok=True)
                connection = sqlite3.connect(str(self.db_path))
            
            # Configure connection
            connection.row_factory = sqlite3.Row  # Return rows as dictionaries
            connection.execute("PRAGMA foreign_keys = ON")  # Enable foreign keys
            
            # Only use WAL mode for file-based databases
            if str(self.db_path) != ":memory:":
                connection.execute("PRAGMA journal_mode = WAL")  # Use WAL mode for better concurrency
            
            logger.info(f"Database connection established: {self.db_path}")
            return connection
            
        except Exception as e:
            logger.error(f"Failed to create database connection: {e}")
            raise
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query"""
        return self._execute_query_sync(query, params)
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE query"""
        return self._execute_update_sync(query, params)
    
    def execute_transaction(self, queries: List[Tuple[str, Optional[tuple]]]) -> bool:
        """Execute multiple queries in a transaction"""
        conn = None
        try:
            conn = self.get_connection()
            conn.execute("BEGIN TRANSACTION")
            
            cursor = conn.cursor()
            try:
                for query, params in queries:
                    if params is None:
                        params = ()
                    cursor.execute(query, params)
            finally:
                cursor.close()
            
            conn.commit()
            logger.info(f"✅ Transaction executed successfully: {len(queries)} queries")
            return True
            
        except Exception as e:
            logger.error(f"❌ Transaction failed: {e}")
            if conn:
                conn.rollback()
            return False
    
    def begin_transaction(self) -> bool:
        """Begin a new transaction"""
        try:
            if self._in_transaction:
                logger.warning("⚠️ Transaction already in progress")
                return False
            
            self._connection = self.get_connection()
            self._connection.execute("BEGIN TRANSACTION")
            self._in_transaction = True
            logger.info("✅ Transaction started")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start transaction: {e}")
            return False
    
    def commit_transaction(self) -> bool:
        """Commit the current transaction"""
        try:
            if not self._in_transaction or not self._connection:
                logger.warning("⚠️ No transaction to commit")
                return False
            
            self._connection.commit()
            self._in_transaction = False
            logger.info("✅ Transaction committed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to commit transaction: {e}")
            return False
    
    def rollback_transaction(self) -> bool:
        """Rollback the current transaction"""
        try:
            if not self._in_transaction or not self._connection:
                logger.warning("⚠️ No transaction to rollback")
                return False
            
            self._connection.rollback()
            self._in_transaction = False
            logger.info("✅ Transaction rolled back")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to rollback transaction: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test if the SQLite connection is working"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result[0] == 1
            finally:
                cursor.close()
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get SQLite version and connection information"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            try:
                # Get SQLite version
                cursor.execute("SELECT sqlite_version()")
                version = cursor.fetchone()[0]
                
                return {
                    'version': version,
                    'database': str(self.db_path),
                    'path': str(self.db_path),
                    'type': 'sqlite'
                }
            finally:
                cursor.close()
                
        except Exception as e:
            logger.error(f"❌ Failed to get database info: {e}")
            return {'error': str(e)}
    
    # Add async versions of execute methods for compatibility
    async def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query asynchronously (delegates to sync version)"""
        # Use a different name to avoid recursion
        return self._execute_query_sync(query, params)
    
    async def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE query asynchronously (delegates to sync version)"""
        # Use a different name to avoid recursion
        return self._execute_update_sync(query, params)
    
    def _execute_query_sync(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Internal sync version of execute_query"""
        if params is None:
            params = ()
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(query, params)
                results = cursor.fetchall()
                # Convert sqlite3.Row objects to dictionaries
                return [dict(row) for row in results]
            finally:
                cursor.close()
        except Exception as e:
            logger.error(f"❌ Query execution failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
        finally:
            if conn and not self._in_transaction:
                # Don't close connection if in transaction
                pass
    
    def _execute_update_sync(self, query: str, params: Optional[tuple] = None) -> int:
        """Internal sync version of execute_update"""
        if params is None:
            params = ()
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount
            finally:
                cursor.close()
        except Exception as e:
            logger.error(f"❌ Update execution failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn and not self._in_transaction:
                # Don't close connection if in transaction
                pass
    
    @property
    def connection_string(self) -> str:
        """Get the connection string"""
        return f"sqlite:///{self.db_path}"
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database cursors."""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            yield cursor
            if not self._in_transaction:
                connection.commit()
        except Exception as e:
            if not self._in_transaction:
                connection.rollback()
            raise
        finally:
            cursor.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


class AsyncSQLiteConnectionManager(ConnectionManager):
    """Async SQLite database connection manager implementing ConnectionManager"""
    
    def __init__(self, connection_config: Union[str, Path, Dict[str, Any]]):
        """
        Initialize async SQLite connection manager.
        
        Args:
            connection_config: Database connection configuration
                - For SQLite: Path to database file or ":memory:" for in-memory
        """
        super().__init__(connection_config)
        
        # Handle different config types
        if isinstance(connection_config, (str, Path)):
            self.db_path = Path(connection_config)
        elif isinstance(connection_config, dict):
            self.db_path = Path(connection_config.get('db_path', ':memory:'))
        else:
            self.db_path = Path(':memory:')
        
        self._connection: Optional[sqlite3.Connection] = None
        self._in_transaction: bool = False
        self._loop = None
        
    async def connect(self) -> bool:
        """Establish async SQLite database connection"""
        try:
            if self._connection is None:
                self._connection = await self._create_connection_async()
            self._is_connected = True
            logger.info(f"✅ Connected to SQLite (async): {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to SQLite (async): {e}")
            self._is_connected = False
            return False
    
    async def connect_async(self) -> bool:
        """Establish async SQLite database connection (alias for connect)"""
        return await self.connect()
    
    async def disconnect(self) -> bool:
        """Close async SQLite database connection"""
        try:
            if self._connection:
                self._connection.close()
                self._connection = None
            self._is_connected = False
            logger.info("✅ Disconnected from SQLite (async)")
            return True
        except Exception as e:
            logger.error(f"❌ Error disconnecting from SQLite (async): {e}")
            return False
    
    async def disconnect_async(self) -> bool:
        """Close async SQLite database connection (alias for disconnect)"""
        return await self.disconnect()
    
    async def get_connection(self) -> sqlite3.Connection:
        """Get the active database connection"""
        if not self._is_connected:
            raise ConnectionError("Not connected to SQLite")
        if self._connection is None:
            self._connection = await self._create_connection_async()
        return self._connection
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection."""
        try:
            # Handle in-memory database
            if str(self.db_path) == ":memory:":
                connection = sqlite3.connect(":memory:")
            else:
                # Ensure database directory exists for file-based databases
                self.db_path.parent.mkdir(parents=True, exist_ok=True)
                connection = sqlite3.connect(str(self.db_path))
            
            # Configure connection
            connection.row_factory = sqlite3.Row  # Return rows as dictionaries
            connection.execute("PRAGMA foreign_keys = ON")  # Enable foreign keys
            
            return connection
            
        except Exception as e:
            logger.error(f"Failed to create database connection: {e}")
            raise
    
    async def _create_connection_async(self) -> sqlite3.Connection:
        """Create a new database connection asynchronously"""
        try:
            # Run the blocking SQLite connection in a thread pool
            loop = asyncio.get_event_loop()
            connection = await loop.run_in_executor(None, self._create_connection)
            return connection
        except Exception as e:
            logger.error(f"Failed to create async database connection: {e}")
            raise
    
    async def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query asynchronously"""
        if params is None:
            params = ()
        conn = None
        try:
            conn = await self.get_connection()
            # Run the blocking query in a thread pool
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(None, self._execute_query_sync, conn, query, params)
            return results
        except Exception as e:
            logger.error(f"❌ Async query execution failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
    
    def _execute_query_sync(self, conn: sqlite3.Connection, query: str, params: tuple) -> List[Dict[str, Any]]:
        """Execute a SELECT query synchronously (for thread pool execution)"""
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
            # Convert sqlite3.Row objects to dictionaries
            return [dict(row) for row in results]
        finally:
            cursor.close()
    
    async def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE query asynchronously"""
        if params is None:
            params = ()
        conn = None
        try:
            conn = await self.get_connection()
            # Run the blocking update in a thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._execute_update_sync, conn, query, params)
            return result
        except Exception as e:
            logger.error(f"❌ Async update execution failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
    
    def _execute_update_sync(self, conn: sqlite3.Connection, query: str, params: tuple) -> int:
        """Execute an INSERT, UPDATE, or DELETE query synchronously (for thread pool execution)"""
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
        finally:
            cursor.close()
    
    async def execute_transaction(self, queries: List[Tuple[str, Optional[tuple]]]) -> bool:
        """Execute multiple queries in a transaction asynchronously"""
        conn = None
        try:
            conn = await self.get_connection()
            # Run the blocking transaction in a thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._execute_transaction_sync, conn, queries)
            return result
        except Exception as e:
            logger.error(f"❌ Async transaction failed: {e}")
            raise
    
    def _execute_transaction_sync(self, conn: sqlite3.Connection, queries: List[Tuple[str, Optional[tuple]]]) -> bool:
        """Execute multiple queries in a transaction synchronously (for thread pool execution)"""
        try:
            conn.execute("BEGIN TRANSACTION")
            
            cursor = conn.cursor()
            try:
                for query, params in queries:
                    if params is None:
                        params = ()
                    cursor.execute(query, params)
            finally:
                cursor.close()
            
            conn.commit()
            logger.info(f"✅ Transaction executed successfully: {len(queries)} queries")
            return True
            
        except Exception as e:
            logger.error(f"❌ Transaction failed: {e}")
            if conn:
                conn.rollback()
            return False
    
    async def begin_transaction(self) -> bool:
        """Begin a new async transaction"""
        try:
            if self._in_transaction:
                logger.warning("⚠️ Async transaction already in progress")
                return False
            
            self._connection = await self.get_connection()
            # Run the blocking transaction start in a thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: self._connection.execute("BEGIN TRANSACTION"))
            self._in_transaction = True
            logger.info("✅ Async transaction started")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start async transaction: {e}")
            return False
    
    async def commit_transaction(self) -> bool:
        """Commit the current async transaction"""
        try:
            if not self._in_transaction or not self._connection:
                logger.warning("⚠️ No async transaction to commit")
                return False
            
            # Run the blocking commit in a thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._connection.commit)
            self._in_transaction = False
            logger.info("✅ Async transaction committed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to commit async transaction: {e}")
            return False
    
    async def rollback_transaction(self) -> bool:
        """Rollback the current async transaction"""
        try:
            if not self._in_transaction or not self._connection:
                logger.warning("⚠️ No async transaction to rollback")
                return False
            
            # Run the blocking rollback in a thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._connection.rollback)
            self._in_transaction = False
            logger.info("✅ Async transaction rolled back")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to rollback async transaction: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Test if the async SQLite connection is working"""
        try:
            conn = await self.get_connection()
            # Run the blocking test in a thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._test_connection_sync, conn)
            return result
        except Exception as e:
            logger.error(f"❌ Async connection test failed: {e}")
            return False
    
    def _test_connection_sync(self, conn: sqlite3.Connection) -> bool:
        """Test if the SQLite connection is working synchronously (for thread pool execution)"""
        try:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result[0] == 1
            finally:
                cursor.close()
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False
    
    async def get_database_info(self) -> Dict[str, Any]:
        """Get async SQLite version and connection information"""
        try:
            conn = await self.get_connection()
            # Run the blocking info retrieval in a thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._get_database_info_sync, conn)
            return result
        except Exception as e:
            logger.error(f"❌ Failed to get async database info: {e}")
            return {'error': str(e)}
    
    def _get_database_info_sync(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Get SQLite version and connection information synchronously (for thread pool execution)"""
        try:
            cursor = conn.cursor()
            try:
                # Get SQLite version
                cursor.execute("SELECT sqlite_version()")
                version = cursor.fetchone()[0]
                
                return {
                    'version': version,
                    'database': str(self.db_path),
                    'path': str(self.db_path),
                    'type': 'sqlite'
                }
            finally:
                cursor.close()
                
        except Exception as e:
            logger.error(f"❌ Failed to get database info: {e}")
            return {'error': str(e)}
    
    @property
    def connection_string(self) -> str:
        """Get the connection string"""
        return f"sqlite:///{self.db_path}"
    
    @asynccontextmanager
    async def get_cursor_async(self):
        """Async context manager for database cursors."""
        connection = await self.get_connection()
        cursor = connection.cursor()
        try:
            yield cursor
            if not self._in_transaction:
                # Run the blocking commit in a thread pool
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, connection.commit)
        except Exception as e:
            if not self._in_transaction:
                # Run the blocking rollback in a thread pool
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, connection.rollback)
            raise
        finally:
            cursor.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
