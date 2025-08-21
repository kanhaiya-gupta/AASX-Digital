"""
PostgreSQL Database Connection Manager
=====================================

Implements the ConnectionManager interface for PostgreSQL databases.
Supports both sync and async operations with connection pooling.
"""

import logging
from typing import Optional, Any, Dict, List, Union, Tuple
from pathlib import Path
import asyncio
from contextlib import asynccontextmanager

try:
    import psycopg2
    import psycopg2.extras
    from psycopg2.pool import SimpleConnectionPool, ThreadedConnectionPool
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    # Don't try to set attributes on None
    psycopg2 = None
    psycopg2.extras = None
    SimpleConnectionPool = None
    ThreadedConnectionPool = None

try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False
    asyncpg = None

from .connection_manager import ConnectionManager

logger = logging.getLogger(__name__)

class PostgresConnectionManager(ConnectionManager):
    """PostgreSQL database connection manager"""
    
    def __init__(self, connection_config: Dict[str, Any]):
        """
        Initialize PostgreSQL connection manager.
        
        Args:
            connection_config: Dictionary with connection parameters:
                - host: Database host (default: localhost)
                - port: Database port (default: 5432)
                - database: Database name
                - user: Username
                - password: Password
                - pool_size: Connection pool size (default: 10)
                - max_overflow: Max overflow connections (default: 20)
                - pool_timeout: Pool timeout in seconds (default: 30)
                - pool_recycle: Pool recycle time in seconds (default: 3600)
                - ssl_mode: SSL mode (default: prefer)
        """
        super().__init__(connection_config)
        
        if not PSYCOPG2_AVAILABLE:
            raise ImportError("psycopg2 is required for PostgreSQL support. Install with: pip install psycopg2-binary")
        
        # Set default values
        self.config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'postgres',
            'user': 'postgres',
            'password': '',
            'pool_size': 10,
            'max_overflow': 20,
            'pool_timeout': 30,
            'pool_recycle': 3600,
            'ssl_mode': 'prefer',
            **connection_config
        }
        
        self._pool = None
        self._transaction_connection = None
        self._in_transaction = False
        
    def connect(self) -> bool:
        """Establish PostgreSQL connection with connection pooling"""
        try:
            # Create connection pool
            self._pool = ThreadedConnectionPool(
                minconn=1,
                maxconn=self.config['pool_size'],
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                sslmode=self.config['ssl_mode']
            )
            
            # Test connection
            with self._pool.getconn() as conn:
                conn.autocommit = True
                with conn.cursor() as cursor:
                    cursor.execute("SELECT version()")
                    version = cursor.fetchone()[0]
                    logger.info(f"✅ Connected to PostgreSQL: {version}")
            
            self._is_connected = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to PostgreSQL: {e}")
            self._is_connected = False
            return False
    
    def disconnect(self) -> bool:
        """Close PostgreSQL connection and pool"""
        try:
            if self._transaction_connection:
                self.rollback_transaction()
                self._transaction_connection = None
            
            if self._pool:
                self._pool.closeall()
                self._pool = None
            
            self._is_connected = False
            logger.info("✅ Disconnected from PostgreSQL")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error disconnecting from PostgreSQL: {e}")
            return False
    
    def get_connection(self):
        """Get a connection from the pool"""
        if not self._is_connected:
            raise ConnectionError("Not connected to PostgreSQL")
        
        if self._in_transaction and self._transaction_connection:
            return self._transaction_connection
        
        return self._pool.getconn()
    
    def return_connection(self, conn):
        """Return a connection to the pool"""
        if conn and not self._in_transaction:
            self._pool.putconn(conn)
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query"""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor if psycopg2.extras else None) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ Query execution failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
        finally:
            self.return_connection(conn)
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE query"""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount
                
        except Exception as e:
            logger.error(f"❌ Update execution failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            if conn:
                conn.rollback()
            raise
        finally:
            self.return_connection(conn)
    
    def execute_transaction(self, queries: List[Tuple[str, Optional[tuple]]]) -> bool:
        """Execute multiple queries in a transaction"""
        conn = None
        try:
            conn = self.get_connection()
            conn.autocommit = False
            
            with conn.cursor() as cursor:
                for query, params in queries:
                    cursor.execute(query, params)
            
            conn.commit()
            logger.info(f"✅ Transaction executed successfully: {len(queries)} queries")
            return True
            
        except Exception as e:
            logger.error(f"❌ Transaction failed: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.autocommit = True
            self.return_connection(conn)
    
    def begin_transaction(self) -> bool:
        """Begin a new transaction"""
        try:
            if self._in_transaction:
                logger.warning("⚠️ Transaction already in progress")
                return False
            
            self._transaction_connection = self._pool.getconn()
            self._transaction_connection.autocommit = False
            self._in_transaction = True
            logger.info("✅ Transaction started")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start transaction: {e}")
            return False
    
    def commit_transaction(self) -> bool:
        """Commit the current transaction"""
        try:
            if not self._in_transaction or not self._transaction_connection:
                logger.warning("⚠️ No transaction to commit")
                return False
            
            self._transaction_connection.commit()
            self._transaction_connection.autocommit = True
            self._pool.putconn(self._transaction_connection)
            self._transaction_connection = None
            self._in_transaction = False
            logger.info("✅ Transaction committed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to commit transaction: {e}")
            return False
    
    def rollback_transaction(self) -> bool:
        """Rollback the current transaction"""
        try:
            if not self._in_transaction or not self._transaction_connection:
                logger.warning("⚠️ No transaction to rollback")
                return False
            
            self._transaction_connection.rollback()
            self._transaction_connection.autocommit = True
            self._pool.putconn(self._transaction_connection)
            self._transaction_connection = None
            self._in_transaction = False
            logger.info("✅ Transaction rolled back")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to rollback transaction: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test if the PostgreSQL connection is working"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    return result[0] == 1
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get PostgreSQL version and connection information"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Get PostgreSQL version
                    cursor.execute("SELECT version()")
                    version = cursor.fetchone()[0]
                    
                    # Get current database
                    cursor.execute("SELECT current_database()")
                    current_db = cursor.fetchone()[0]
                    
                    # Get current user
                    cursor.execute("SELECT current_user")
                    current_user = cursor.fetchone()[0]
                    
                    # Get connection info
                    cursor.execute("SELECT inet_server_addr(), inet_server_port()")
                    server_addr, server_port = cursor.fetchone()
                    
                    return {
                        'version': version,
                        'database': current_db,
                        'user': current_user,
                        'host': server_addr,
                        'port': server_port,
                        'pool_size': self.config['pool_size'],
                        'max_overflow': self.config['max_overflow']
                    }
                    
        except Exception as e:
            logger.error(f"❌ Failed to get database info: {e}")
            return {'error': str(e)}

class AsyncPostgresConnectionManager(ConnectionManager):
    """Async PostgreSQL connection manager"""
    
    def __init__(self, connection_config: Dict[str, Any]):
        """Initialize async PostgreSQL connection manager"""
        super().__init__(connection_config)
        
        if not ASYNCPG_AVAILABLE:
            raise ImportError("asyncpg is required for async PostgreSQL support. Install with: pip install asyncpg")
        
        self.config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'postgres',
            'user': 'postgres',
            'password': '',
            'pool_size': 10,
            'ssl_mode': 'prefer',
            **connection_config
        }
        
        self._pool = None
        self._transaction_connection = None
        self._in_transaction = False
    
    async def connect(self) -> bool:
        """Establish async PostgreSQL connection with connection pooling"""
        try:
            self._pool = await asyncpg.create_pool(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                ssl=self.config['ssl_mode'] != 'disable',
                min_size=1,
                max_size=self.config['pool_size']
            )
            
            # Test connection
            async with self._pool.acquire() as conn:
                version = await conn.fetchval("SELECT version()")
                logger.info(f"✅ Connected to PostgreSQL (async): {version}")
            
            self._is_connected = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to PostgreSQL (async): {e}")
            self._is_connected = False
            return False
    
    async def disconnect(self) -> bool:
        """Close async PostgreSQL connection and pool"""
        try:
            if self._transaction_connection:
                await self.rollback_transaction()
                self._transaction_connection = None
            
            if self._pool:
                await self._pool.close()
                self._pool = None
            
            self._is_connected = False
            logger.info("✅ Disconnected from PostgreSQL (async)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error disconnecting from PostgreSQL (async): {e}")
            return False
    
    async def get_connection(self):
        """Get a connection from the async pool"""
        if not self._is_connected:
            raise ConnectionError("Not connected to PostgreSQL")
        
        if self._in_transaction and self._transaction_connection:
            return self._transaction_connection
        
        return await self._pool.acquire()
    
    async def return_connection(self, conn):
        """Return a connection to the async pool"""
        if conn and not self._in_transaction:
            await self._pool.release(conn)
    
    async def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query asynchronously"""
        conn = None
        try:
            conn = await self.get_connection()
            if params:
                results = await conn.fetch(query, *params)
            else:
                results = await conn.fetch(query)
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"❌ Async query execution failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
        finally:
            await self.return_connection(conn)
    
    async def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE query asynchronously"""
        conn = None
        try:
            conn = await self.get_connection()
            if params:
                result = await conn.execute(query, *params)
            else:
                result = await conn.execute(query)
            
            return result.split()[-1]  # Extract affected row count
            
        except Exception as e:
            logger.error(f"❌ Async update execution failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
        finally:
            await self.return_connection(conn)
    
    async def begin_transaction(self) -> bool:
        """Begin a new async transaction"""
        try:
            if self._in_transaction:
                logger.warning("⚠️ Async transaction already in progress")
                return False
            
            self._transaction_connection = await self._pool.acquire()
            self._in_transaction = True
            logger.info("✅ Async transaction started")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start async transaction: {e}")
            return False
    
    async def commit_transaction(self) -> bool:
        """Commit the current async transaction"""
        try:
            if not self._in_transaction or not self._transaction_connection:
                logger.warning("⚠️ No async transaction to commit")
                return False
            
            await self._pool.release(self._transaction_connection)
            self._transaction_connection = None
            self._in_transaction = False
            logger.info("✅ Async transaction committed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to commit async transaction: {e}")
            return False
    
    async def rollback_transaction(self) -> bool:
        """Rollback the current async transaction"""
        try:
            if not self._in_transaction or not self._transaction_connection:
                logger.warning("⚠️ No async transaction to rollback")
                return False
            
            await self._pool.release(self._transaction_connection)
            self._transaction_connection = None
            self._in_transaction = False
            logger.info("✅ Async transaction rolled back")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to rollback async transaction: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Test if the async PostgreSQL connection is working"""
        try:
            async with self._pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1")
                return result == 1
        except Exception as e:
            logger.error(f"❌ Async connection test failed: {e}")
            return False
    
    async def get_database_info(self) -> Dict[str, Any]:
        """Get async PostgreSQL version and connection information"""
        try:
            async with self._pool.acquire() as conn:
                version = await conn.fetchval("SELECT version()")
                current_db = await conn.fetchval("SELECT current_database()")
                current_user = await conn.fetchval("SELECT current_user")
                
                return {
                    'version': version,
                    'database': current_db,
                    'user': current_user,
                    'host': self.config['host'],
                    'port': self.config['port'],
                    'pool_size': self.config['pool_size']
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get async database info: {e}")
            return {'error': str(e)}
