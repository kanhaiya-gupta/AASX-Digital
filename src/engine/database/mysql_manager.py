"""
MySQL Database Connection Manager
================================

Implements the ConnectionManager interface for MySQL databases.
Supports both sync and async operations with connection pooling.
"""

import logging
from typing import Optional, Any, Dict, List, Union, Tuple
from pathlib import Path
import asyncio

try:
    import pymysql
    import pymysql.cursors
    from pymysql.constants import CLIENT
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False
    # Don't try to set attributes on None
    pymysql = None
    pymysql.cursors = None
    CLIENT = None

try:
    import aiomysql
    AIOMYSQL_AVAILABLE = True
except ImportError:
    AIOMYSQL_AVAILABLE = False
    aiomysql = None

from .connection_manager import ConnectionManager

logger = logging.getLogger(__name__)

class MySQLConnectionManager(ConnectionManager):
    """MySQL database connection manager"""
    
    def __init__(self, connection_config: Dict[str, Any]):
        """
        Initialize MySQL connection manager.
        
        Args:
            connection_config: Dictionary with connection parameters:
                - host: Database host (default: localhost)
                - port: Database port (default: 3306)
                - database: Database name
                - user: Username
                - password: Password
                - pool_size: Connection pool size (default: 10)
                - max_overflow: Max overflow connections (default: 20)
                - pool_timeout: Pool timeout in seconds (default: 30)
                - pool_recycle: Pool recycle time in seconds (default: 3600)
                - charset: Character set (default: utf8mb4)
                - ssl: SSL configuration (default: None)
        """
        super().__init__(connection_config)
        
        if not PYMYSQL_AVAILABLE:
            raise ImportError("PyMySQL is required for MySQL support. Install with: pip install PyMySQL")
        
        # Set default values
        self.config = {
            'host': 'localhost',
            'port': 3306,
            'database': 'mysql',
            'user': 'root',
            'password': '',
            'pool_size': 10,
            'max_overflow': 20,
            'pool_timeout': 30,
            'pool_recycle': 3600,
            'charset': 'utf8mb4',
            'ssl': None,
            **connection_config
        }
        
        self._pool = None
        self._transaction_connection = None
        self._in_transaction = False
        
    def connect(self) -> bool:
        """Establish MySQL connection with connection pooling"""
        try:
            # For now, we'll use a simple connection approach
            # In production, you might want to implement a proper connection pool
            # Test connection first
            test_conn = pymysql.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                charset=self.config['charset'],
                ssl=self.config['ssl'],
                client_flag=CLIENT.MULTI_STATEMENTS if CLIENT else 0
            )
            
            with test_conn.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
                logger.info(f"✅ Connected to MySQL: {version}")
            
            test_conn.close()
            self._is_connected = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MySQL: {e}")
            self._is_connected = False
            return False
    
    def disconnect(self) -> bool:
        """Close MySQL connection"""
        try:
            if self._transaction_connection:
                self.rollback_transaction()
                self._transaction_connection = None
            
            self._is_connected = False
            logger.info("✅ Disconnected from MySQL")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error disconnecting from MySQL: {e}")
            return False
    
    def get_connection(self):
        """Get a new MySQL connection"""
        if not self._is_connected:
            raise ConnectionError("Not connected to MySQL")
        
        if self._in_transaction and self._transaction_connection:
            return self._transaction_connection
        
        return pymysql.connect(
            host=self.config['host'],
            port=self.config['port'],
            database=self.config['database'],
            user=self.config['user'],
            password=self.config['password'],
            charset=self.config['charset'],
            ssl=self.config['ssl'],
            client_flag=CLIENT.MULTI_STATEMENTS if CLIENT else 0,
            autocommit=True
        )
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query"""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ Query execution failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
        finally:
            if conn and not self._in_transaction:
                conn.close()
    
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
            if conn and not self._in_transaction:
                conn.close()
    
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
                conn.close()
    
    def begin_transaction(self) -> bool:
        """Begin a new transaction"""
        try:
            if self._in_transaction:
                logger.warning("⚠️ Transaction already in progress")
                return False
            
            self._transaction_connection = self.get_connection()
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
            self._transaction_connection.close()
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
            self._transaction_connection.close()
            self._transaction_connection = None
            self._in_transaction = False
            logger.info("✅ Transaction rolled back")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to rollback transaction: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test if the MySQL connection is working"""
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
        """Get MySQL version and connection information"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Get MySQL version
                    cursor.execute("SELECT VERSION()")
                    version = cursor.fetchone()[0]
                    
                    # Get current database
                    cursor.execute("SELECT DATABASE()")
                    current_db = cursor.fetchone()[0]
                    
                    # Get current user
                    cursor.execute("SELECT USER()")
                    current_user = cursor.fetchone()[0]
                    
                    # Get connection info
                    cursor.execute("SELECT @@hostname, @@port")
                    hostname, port = cursor.fetchone()
                    
                    return {
                        'version': version,
                        'database': current_db,
                        'user': current_user,
                        'host': hostname,
                        'port': port,
                        'charset': self.config['charset']
                    }
                    
        except Exception as e:
            logger.error(f"❌ Failed to get database info: {e}")
            return {'error': str(e)}

class AsyncMySQLConnectionManager(ConnectionManager):
    """Async MySQL connection manager"""
    
    def __init__(self, connection_config: Dict[str, Any]):
        """Initialize async MySQL connection manager"""
        super().__init__(connection_config)
        
        if not AIOMYSQL_AVAILABLE:
            raise ImportError("aiomysql is required for async MySQL support. Install with: pip install aiomysql")
        
        self.config = {
            'host': 'localhost',
            'port': 3306,
            'database': 'mysql',
            'user': 'root',
            'password': '',
            'pool_size': 10,
            'charset': 'utf8mb4',
            'ssl': None,
            **connection_config
        }
        
        self._pool = None
        self._transaction_connection = None
        self._in_transaction = False
    
    async def connect(self) -> bool:
        """Establish async MySQL connection with connection pooling"""
        try:
            self._pool = await aiomysql.create_pool(
                host=self.config['host'],
                port=self.config['port'],
                db=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                charset=self.config['charset'],
                ssl=self.config['ssl'],
                minsize=1,
                maxsize=self.config['pool_size']
            )
            
            # Test connection
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT VERSION()")
                    version = await cursor.fetchone()
                    logger.info(f"✅ Connected to MySQL (async): {version[0]}")
            
            self._is_connected = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MySQL (async): {e}")
            self._is_connected = False
            return False
    
    async def disconnect(self) -> bool:
        """Close async MySQL connection and pool"""
        try:
            if self._transaction_connection:
                await self.rollback_transaction()
                self._transaction_connection = None
            
            if self._pool:
                self._pool.close()
                await self._pool.wait_closed()
                self._pool = None
            
            self._is_connected = False
            logger.info("✅ Disconnected from MySQL (async)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error disconnecting from MySQL (async): {e}")
            return False
    
    async def get_connection(self):
        """Get a connection from the async pool"""
        if not self._is_connected:
            raise ConnectionError("Not connected to MySQL")
        
        if self._in_transaction and self._transaction_connection:
            return self._transaction_connection
        
        return await self._pool.acquire()
    
    async def return_connection(self, conn):
        """Return a connection to the async pool"""
        if conn and not self._in_transaction:
            self._pool.release(conn)
    
    async def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query asynchronously"""
        conn = None
        try:
            conn = await self.get_connection()
            async with conn.cursor(aiomysql.cursors.DictCursor) as cursor:
                await cursor.execute(query, params)
                results = await cursor.fetchall()
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
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                await conn.commit()
                return cursor.rowcount
            
        except Exception as e:
            logger.error(f"❌ Async update execution failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            if conn:
                await conn.rollback()
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
            
            await self._transaction_connection.commit()
            self._pool.release(self._transaction_connection)
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
            
            await self._transaction_connection.rollback()
            self._pool.release(self._transaction_connection)
            self._transaction_connection = None
            self._in_transaction = False
            logger.info("✅ Async transaction rolled back")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to rollback async transaction: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Test if the async MySQL connection is working"""
        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1")
                    result = await cursor.fetchone()
                    return result[0] == 1
        except Exception as e:
            logger.error(f"❌ Async connection test failed: {e}")
            return False
    
    async def get_database_info(self) -> Dict[str, Any]:
        """Get async MySQL version and connection information"""
        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    # Get MySQL version
                    await cursor.execute("SELECT VERSION()")
                    version = await cursor.fetchone()
                    
                    # Get current database
                    await cursor.execute("SELECT DATABASE()")
                    current_db = await cursor.fetchone()
                    
                    # Get current user
                    await cursor.execute("SELECT USER()")
                    current_user = await cursor.fetchone()
                    
                    return {
                        'version': version[0] if version else 'unknown',
                        'database': current_db[0] if current_db else 'unknown',
                        'user': current_user[0] if current_user else 'unknown',
                        'host': self.config['host'],
                        'port': self.config['port'],
                        'charset': self.config['charset']
                    }
                    
        except Exception as e:
            logger.error(f"❌ Failed to get async database info: {e}")
            return {'error': str(e)}
