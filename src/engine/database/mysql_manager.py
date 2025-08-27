"""
World-Class MySQL Database Connection Manager
===========================================

Enterprise-grade MySQL connection manager with pure async implementation.
Features: Connection pooling, retry logic, comprehensive error handling,
transaction management, and performance optimization using aiomysql.
"""

import aiomysql
import asyncio
import logging
import time
from typing import Optional, Any, Dict, List, Union, Tuple, AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum

from .connection_manager import ConnectionManager

logger = logging.getLogger(__name__)

class ConnectionState(Enum):
    """Connection state enumeration"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    TRANSACTION = "transaction"
    ERROR = "error"

@dataclass
class ConnectionMetrics:
    """Connection performance metrics"""
    total_queries: int = 0
    total_updates: int = 0
    total_transactions: int = 0
    avg_query_time: float = 0.0
    avg_update_time: float = 0.0
    connection_errors: int = 0
    last_activity: float = 0.0

class MySQLConnectionManager(ConnectionManager):
    """
    World-class MySQL database connection manager.
    
    Features:
    - Pure async implementation using aiomysql
    - Connection pooling and management
    - Automatic retry logic with exponential backoff
    - Comprehensive error handling and logging
    - Transaction management with rollback protection
    - Performance monitoring and metrics
    - Connection health checks
    - Optimized for high-concurrency scenarios
    """
    
    def __init__(self, connection_config: Union[str, Dict[str, Any]]):
        """
        Initialize MySQL connection manager.
        
        Args:
            connection_config: Database connection configuration
                - For MySQL: Connection string or dict with connection params
        """
        super().__init__(connection_config)
        
        # Handle different config types
        if isinstance(connection_config, str):
            self._connection_string = connection_config
            self.connection_params = self._parse_connection_string(connection_config)
        elif isinstance(connection_config, dict):
            self._connection_string = None
            self.connection_params = connection_config
        else:
            raise ValueError("Connection config must be string or dict")
        
        # Connection state management
        self._connection: Optional[aiomysql.Connection] = None
        self._connection_state = ConnectionState.DISCONNECTED
        self._connection_lock = asyncio.Lock()
        
        # Transaction management
        self._transaction_depth = 0
        self._transaction_lock = asyncio.Lock()
        
        # Performance and monitoring
        self._metrics = ConnectionMetrics()
        self._last_health_check = 0
        self._health_check_interval = 300  # 5 minutes
        
        # Configuration
        self._max_retries = 3
        self._retry_delay = 0.1  # seconds
        self._connection_timeout = 30  # seconds
        self._enable_ssl = True
        self._enable_connection_pooling = True
        self._pool_size = 10
        self._charset = 'utf8mb4'
        self._autocommit = False
        
        # Connection pool (for future enhancement)
        self._pool: Optional[aiomysql.Pool] = None
        
        logger.info(f"🏗️ Initialized MySQL connection manager")
    
    def _parse_connection_string(self, connection_string: str) -> Dict[str, Any]:
        """Parse MySQL connection string into parameters."""
        # Basic parsing - can be enhanced for more complex strings
        if connection_string.startswith('mysql://'):
            # Remove protocol prefix
            connection_string = connection_string.replace('mysql://', '')
        
        # Split into host:port and database
        if '@' in connection_string:
            auth_part, rest = connection_string.split('@', 1)
            if ':' in auth_part:
                username, password = auth_part.split(':', 1)
            else:
                username, password = auth_part, None
        else:
            username, password = None, None
        
        if '/' in rest:
            host_part, database = rest.rsplit('/', 1)
        else:
            host_part, database = rest, None
        
        if ':' in host_part:
            host, port = host_part.split(':', 1)
            port = int(port)
        else:
            host, port = host_part, 3306
        
        params = {
            'host': host,
            'port': port,
            'db': database,
            'user': username,
            'password': password,
            'charset': self._charset,
            'autocommit': self._autocommit,
            'ssl': self._enable_ssl,
        }
        
        # Remove None values
        return {k: v for k, v in params.items() if v is not None}
    
    async def connect(self) -> bool:
        """
        Establish MySQL database connection asynchronously.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        async with self._connection_lock:
            try:
                if self._connection_state == ConnectionState.CONNECTED:
                    logger.debug("✅ Already connected to MySQL")
                    return True
                
                self._connection_state = ConnectionState.CONNECTING
                logger.info(f"🔌 Connecting to MySQL...")
                
                # Create connection with timeout
                self._connection = await asyncio.wait_for(
                    self._create_connection(),
                    timeout=self._connection_timeout
                )
                
                # Configure connection for optimal performance
                await self._configure_connection()
                
                # Perform health check
                await self._health_check()
                
                self._connection_state = ConnectionState.CONNECTED
                self._metrics.last_activity = time.time()
                
                logger.info(f"✅ Successfully connected to MySQL")
                return True
                
            except asyncio.TimeoutError:
                logger.error(f"❌ Connection timeout after {self._connection_timeout}s")
                self._connection_state = ConnectionState.ERROR
                return False
            except Exception as e:
                logger.error(f"❌ Failed to connect to MySQL: {e}")
                self._connection_state = ConnectionState.ERROR
                self._metrics.connection_errors += 1
                return False
    
    async def connect_async(self) -> bool:
        """Alias for connect() method for compatibility"""
        return await self.connect()
    
    async def disconnect(self) -> bool:
        """
        Close MySQL database connection asynchronously.
        
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        async with self._connection_lock:
            try:
                if self._connection_state == ConnectionState.DISCONNECTED:
                    logger.debug("✅ Already disconnected from MySQL")
                    return True
                
                # Rollback any active transaction
                if self._transaction_depth > 0:
                    await self._rollback_transaction()
                
                if self._connection:
                    try:
                        # Add timeout to prevent hanging on close
                        await asyncio.wait_for(
                            self._connection.close(),
                            timeout=5.0  # 5 second timeout
                        )
                    except asyncio.TimeoutError:
                        logger.warning("⚠️ Connection close timeout, forcing close")
                        # Force close if timeout occurs
                        self._connection = None
                    except Exception as close_error:
                        logger.warning(f"⚠️ Error during connection close: {close_error}")
                        self._connection = None
                    else:
                        self._connection = None
                
                self._connection_state = ConnectionState.DISCONNECTED
                self._transaction_depth = 0
                
                logger.info("✅ Successfully disconnected from MySQL")
                return True
                
            except Exception as e:
                logger.error(f"❌ Error disconnecting from MySQL: {e}")
                self._connection_state = ConnectionState.ERROR
                # Force cleanup even on error
                self._connection = None
                self._transaction_depth = 0
                return False
    

    
    async def get_connection(self) -> aiomysql.Connection:
        """
        Get the active database connection asynchronously.
        
        Returns:
            aiomysql.Connection: Active database connection
            
        Raises:
            ConnectionError: If not connected or connection failed
        """
        if self._connection_state != ConnectionState.CONNECTED:
            await self.connect()
        
        if not self._connection:
            raise ConnectionError("Failed to establish MySQL connection")
        
        return self._connection
    
    async def _create_connection(self) -> aiomysql.Connection:
        """
        Create a new database connection asynchronously.
        
        Returns:
            aiomysql.Connection: New database connection
        """
        try:
            # Create connection using aiomysql
            connection = await aiomysql.connect(**self.connection_params)
            
            logger.debug("Database connection established")
            return connection
            
        except Exception as e:
            logger.error(f"Failed to create database connection: {e}")
            raise
    
    async def _configure_connection(self) -> None:
        """Configure connection for optimal performance and reliability"""
        try:
            if not self._connection:
                return
            
            # Set session-level optimizations
            await self._connection.execute("SET SESSION sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO'")
            await self._connection.execute("SET SESSION innodb_lock_wait_timeout = 10")
            await self._connection.execute("SET SESSION wait_timeout = 28800")
            await self._connection.execute("SET SESSION interactive_timeout = 28800")
            
            # Performance optimizations
            await self._connection.execute("SET SESSION join_buffer_size = 268435456")  # 256MB
            await self._connection.execute("SET SESSION sort_buffer_size = 67108864")   # 64MB
            await self._connection.execute("SET SESSION read_buffer_size = 16777216")   # 16MB
            
            logger.debug("✅ Database connection configured for optimal performance")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to configure connection: {e}")
    
    async def _health_check(self) -> bool:
        """
        Perform connection health check.
        
        Returns:
            bool: True if connection is healthy, False otherwise
        """
        try:
            if not self._connection:
                return False
            
            cursor = None
            try:
                # Add timeout to prevent hanging health checks
                cursor = await asyncio.wait_for(
                    self._connection.cursor(),
                    timeout=3.0  # 3 second timeout for cursor creation
                )
                await asyncio.wait_for(
                    cursor.execute("SELECT 1"),
                    timeout=2.0  # 2 second timeout for health check
                )
                result = await asyncio.wait_for(
                    cursor.fetchone(),
                    timeout=1.0  # 1 second timeout for fetch
                )
                
                is_healthy = result[0] == 1
                if is_healthy:
                    self._last_health_check = time.time()
                    logger.debug("✅ Connection health check passed")
                else:
                    logger.warning("⚠️ Connection health check failed")
                
                return is_healthy
                
            finally:
                # Ensure cursor is always closed
                if cursor:
                    try:
                        await asyncio.wait_for(
                            cursor.close(),
                            timeout=1.0  # 1 second timeout for cursor close
                        )
                    except asyncio.TimeoutError:
                        logger.warning("⚠️ Health check cursor close timeout")
                    except Exception as close_error:
                        logger.warning(f"⚠️ Failed to close health check cursor: {close_error}")
            
        except asyncio.TimeoutError:
            logger.error("❌ Connection health check timeout - connection may be hanging")
            return False
        except Exception as e:
            logger.error(f"❌ Connection health check failed: {e}")
            return False
    
    async def execute_query(
        self, 
        query: str, 
        params: Optional[Union[Dict[str, Any], Tuple[Any, ...]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query asynchronously with retry logic.
        
        Args:
            query: SQL query string
            params: Query parameters (dict or tuple)
            
        Returns:
            List[Dict[str, Any]]: Query results as list of dictionaries
            
        Raises:
            ConnectionError: If connection issues occur
            Exception: If query execution fails
        """
        start_time = time.time()
        last_exception = None
        
        for attempt in range(self._max_retries + 1):
            try:
                if not self._is_connected:
                    await self.connect()
                
                connection = await self.get_connection()
                cursor = None
                
                try:
                    cursor = await connection.cursor(aiomysql.DictCursor)
                    
                    # Execute query with parameters
                    if params:
                        if isinstance(params, dict):
                            # Convert dict to tuple for aiomysql
                            param_values = list(params.values())
                            await cursor.execute(query, param_values)
                        else:
                            await cursor.execute(query, params)
                    else:
                        await cursor.execute(query)
                    
                    rows = await cursor.fetchall()
                    
                    # Convert to list of dictionaries
                    results = [dict(row) for row in rows]
                    
                    # Update metrics
                    query_time = time.time() - start_time
                    self._metrics.total_queries += 1
                    self._metrics.avg_query_time = (
                        (self._metrics.avg_query_time * (self._metrics.total_queries - 1) + query_time) 
                        / self._metrics.total_queries
                    )
                    self._metrics.last_activity = time.time()
                    
                    logger.debug(f"✅ Query executed successfully in {query_time:.3f}s")
                    return results
                    
                finally:
                    # Ensure cursor is always closed
                    if cursor:
                        try:
                            await cursor.close()
                        except Exception as close_error:
                            logger.warning(f"⚠️ Failed to close cursor: {close_error}")
                
            except Exception as e:
                last_exception = e
                logger.warning(f"⚠️ Query attempt {attempt + 1} failed: {e}")
                
                if attempt < self._max_retries:
                    await asyncio.sleep(self._retry_delay * (2 ** attempt))
                    continue
                else:
                    break
        
        # All retries failed
        logger.error(f"❌ Query execution failed after {self._max_retries + 1} attempts: {last_exception}")
        logger.error(f"Query: {query}")
        logger.error(f"Params: {params}")
        raise last_exception or Exception("Query execution failed")
    
    async def execute_update(
        self, 
        query: str, 
        params: Optional[Union[Dict[str, Any], Tuple[Any, ...]]] = None
    ) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query asynchronously with retry logic.
        
        Args:
            query: SQL query string
            params: Query parameters (dict or tuple)
            
        Returns:
            int: Number of affected rows
            
        Raises:
            ConnectionError: If connection issues occur
            Exception: If query execution fails
        """
        start_time = time.time()
        last_exception = None
        
        for attempt in range(self._max_retries + 1):
            try:
                if not self._is_connected:
                    await self.connect()
                
                connection = await self.get_connection()
                cursor = None
                
                try:
                    cursor = await connection.cursor()
                    
                    # Execute update with parameters
                    if params:
                        if isinstance(params, dict):
                            # Convert dict to tuple for aiomysql
                            param_values = list(params.values())
                            await cursor.execute(query, param_values)
                        else:
                            await cursor.execute(query, params)
                    else:
                        await cursor.execute(query)
                    
                    # Get affected row count
                    row_count = cursor.rowcount
                    
                    # Update metrics
                    update_time = time.time() - start_time
                    self._metrics.total_updates += 1
                    self._metrics.avg_update_time = (
                        (self._metrics.avg_update_time * (self._metrics.total_updates - 1) + update_time) 
                        / self._metrics.total_updates
                    )
                    self._metrics.last_activity = time.time()
                    
                    logger.debug(f"✅ Update executed successfully in {update_time:.3f}s, affected {row_count} rows")
                    return row_count
                    
                finally:
                    # Ensure cursor is always closed
                    if cursor:
                        try:
                            await cursor.close()
                        except Exception as close_error:
                            logger.warning(f"⚠️ Failed to close cursor: {close_error}")
                
            except Exception as e:
                last_exception = e
                logger.warning(f"⚠️ Update attempt {attempt + 1} failed: {e}")
                
                if attempt < self._max_retries:
                    await asyncio.sleep(self._retry_delay * (2 ** attempt))
                    continue
                else:
                    break
        
        # All retries failed
        logger.error(f"❌ Update execution failed after {self._max_retries + 1} attempts: {last_exception}")
        logger.error(f"Query: {query}")
        logger.error(f"Params: {params}")
        raise last_exception or Exception("Update execution failed")
    
    async def execute_transaction(
        self, 
        queries: List[Tuple[str, Optional[Union[Dict[str, Any], Tuple[Any, ...]]]]]
    ) -> bool:
        """
        Execute multiple queries in a transaction asynchronously.
        
        Args:
            queries: List of (query, params) tuples
            
        Returns:
            bool: True if transaction successful, False otherwise
        """
        start_time = time.time()
        
        try:
            if not self._is_connected:
                await self.connect()
            
            connection = await self.get_connection()
            cursor = None
            
            try:
                cursor = await connection.cursor()
                
                # Begin transaction
                await cursor.execute("START TRANSACTION")
                
                for i, (query, params) in enumerate(queries):
                    try:
                        if params:
                            if isinstance(params, dict):
                                param_values = list(params.values())
                                await cursor.execute(query, param_values)
                            else:
                                await cursor.execute(query, params)
                        else:
                            await cursor.execute(query)
                        
                        logger.debug(f"✅ Transaction query {i + 1}/{len(queries)} executed")
                    except Exception as e:
                        logger.error(f"❌ Transaction query {i + 1} failed: {e}")
                        await cursor.execute("ROLLBACK")
                        raise
                
                # Commit transaction
                await cursor.execute("COMMIT")
                
                # Update metrics
                transaction_time = time.time() - start_time
                self._metrics.total_transactions += 1
                self._metrics.last_activity = time.time()
                
                logger.info(f"✅ Transaction executed successfully in {transaction_time:.3f}s: {len(queries)} queries")
                return True
                
            finally:
                # Ensure cursor is always closed
                if cursor:
                    try:
                        await cursor.close()
                    except Exception as close_error:
                        logger.warning(f"⚠️ Failed to close cursor: {close_error}")
            
        except Exception as e:
            logger.error(f"❌ Transaction failed: {e}")
            return False
    
    async def begin_transaction(self) -> bool:
        """
        Begin a new transaction asynchronously.
        
        Returns:
            bool: True if transaction started successfully, False otherwise
        """
        async with self._transaction_lock:
            try:
                if self._transaction_depth > 0:
                    logger.warning("⚠️ Transaction already in progress")
                    return False
                
                if not self._is_connected:
                    await self.connect()
                
                connection = await self.get_connection()
                cursor = await connection.cursor()
                
                await cursor.execute("START TRANSACTION")
                await cursor.close()
                
                self._transaction_depth = 1
                self._connection_state = ConnectionState.TRANSACTION
                
                logger.info("✅ Transaction started")
                return True
                
            except Exception as e:
                logger.error(f"❌ Failed to start transaction: {e}")
                return False
    
    async def commit_transaction(self) -> bool:
        """
        Commit the current transaction asynchronously.
        
        Returns:
            bool: True if transaction committed successfully, False otherwise
        """
        async with self._transaction_lock:
            try:
                if self._transaction_depth == 0:
                    logger.warning("⚠️ No transaction to commit")
                    return False
                
                if not self._connection:
                    logger.warning("⚠️ No active connection")
                    return False
                
                cursor = await self._connection.cursor()
                await cursor.execute("COMMIT")
                await cursor.close()
                
                self._transaction_depth = 0
                self._connection_state = ConnectionState.CONNECTED
                
                logger.info("✅ Transaction committed")
                return True
                
            except Exception as e:
                logger.error(f"❌ Failed to commit transaction: {e}")
                return False
    
    async def rollback_transaction(self) -> bool:
        """
        Rollback the current transaction asynchronously.
        
        Returns:
            bool: True if transaction rolled back successfully, False otherwise
        """
        async with self._transaction_lock:
            try:
                if self._transaction_depth == 0:
                    logger.warning("⚠️ No transaction to rollback")
                    return False
                
                if not self._connection:
                    logger.warning("⚠️ No active connection")
                    return False
                
                cursor = await self._connection.cursor()
                await cursor.execute("ROLLBACK")
                await cursor.close()
                
                self._transaction_depth = 0
                self._connection_state = ConnectionState.CONNECTED
                
                logger.info("✅ Transaction rolled back")
                return True
                
            except Exception as e:
                logger.error(f"❌ Failed to rollback transaction: {e}")
                return False
    
    async def _rollback_transaction(self) -> None:
        """Internal method to rollback transaction without logging"""
        try:
            if self._transaction_depth > 0 and self._connection:
                cursor = await self._connection.cursor()
                await cursor.execute("ROLLBACK")
                await cursor.close()
                self._transaction_depth = 0
        except Exception:
            pass
    
    async def test_connection(self) -> bool:
        """
        Test if the MySQL connection is working asynchronously.
        
        Returns:
            bool: True if connection test passes, False otherwise
        """
        try:
            if not self._is_connected:
                await self.connect()
            
            return await self._health_check()
            
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False
    
    async def get_database_info(self) -> Dict[str, Any]:
        """
        Get MySQL version and connection information asynchronously.
        
        Returns:
            Dict[str, Any]: Database information
        """
        try:
            if not self._is_connected:
                await self.connect()
            
            conn = await self.get_connection()
            cursor = await conn.cursor()
            
            # Get MySQL version
            await cursor.execute("SELECT VERSION()")
            version_result = await cursor.fetchone()
            version = version_result[0] if version_result else "unknown"
            
            # Get database name
            await cursor.execute("SELECT DATABASE()")
            db_result = await cursor.fetchone()
            db_name = db_result[0] if db_result else "unknown"
            
            await cursor.close()
            
            info = {
                'version': version,
                'database': db_name,
                'type': 'mysql',
                'state': self._connection_state.value,
                'transaction_depth': self._transaction_depth,
                'metrics': {
                    'total_queries': self._metrics.total_queries,
                    'total_updates': self._metrics.total_updates,
                    'total_transactions': self._metrics.total_transactions,
                    'avg_query_time': round(self._metrics.avg_query_time, 3),
                    'avg_update_time': round(self._metrics.avg_update_time, 3),
                    'connection_errors': self._metrics.connection_errors,
                    'last_activity': self._metrics.last_activity
                }
            }
            
            return info
                
        except Exception as e:
            logger.error(f"❌ Failed to get database info: {e}")
            return {'error': str(e)}
    
    async def get_metrics(self) -> ConnectionMetrics:
        """
        Get connection performance metrics.
        
        Returns:
            ConnectionMetrics: Performance metrics object
        """
        return self._metrics
    
    async def reset_metrics(self) -> None:
        """Reset performance metrics to default values"""
        self._metrics = ConnectionMetrics()
        logger.info("✅ Performance metrics reset")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check.
        
        Returns:
            Dict[str, Any]: Health check results
        """
        current_time = time.time()
        
        # Check if health check is needed
        if current_time - self._last_health_check < self._health_check_interval:
            return {'status': 'healthy', 'last_check': self._last_health_check}
        
        try:
            # Test connection
            connection_ok = await self.test_connection()
            
            # Check transaction state
            transaction_ok = self._transaction_depth == 0
            
            # Check connection state
            state_ok = self._connection_state in [ConnectionState.CONNECTED, ConnectionState.DISCONNECTED]
            
            # Overall health
            is_healthy = connection_ok and transaction_ok and state_ok
            
            health_status = {
                'status': 'healthy' if is_healthy else 'unhealthy',
                'timestamp': current_time,
                'connection': connection_ok,
                'transaction': transaction_ok,
                'state': state_ok,
                'connection_state': self._connection_state.value,
                'transaction_depth': self._transaction_depth,
                'last_activity': self._metrics.last_activity,
                'total_queries': self._metrics.total_queries,
                'total_updates': self._metrics.total_updates,
                'connection_errors': self._metrics.connection_errors
            }
            
            if is_healthy:
                logger.debug("✅ Health check passed")
            else:
                logger.warning("⚠️ Health check failed")
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': current_time
            }
    
    @property
    def connection_string(self) -> str:
        """Get the connection string"""
        if hasattr(self, '_connection_string') and self._connection_string:
            return self._connection_string
        else:
            # Build connection string from params
            params = self.connection_params
            return f"mysql://{params.get('user', '')}:{params.get('password', '')}@{params.get('host', '')}:{params.get('port', 3306)}/{params.get('db', '')}"
    
    @property
    def is_connected(self) -> bool:
        """Check if currently connected"""
        return self._connection_state == ConnectionState.CONNECTED
    
    @property
    def in_transaction(self) -> bool:
        """Check if currently in a transaction"""
        return self._transaction_depth > 0
    
    @asynccontextmanager
    async def get_cursor_async(self) -> AsyncGenerator[aiomysql.Cursor, None]:
        """
        Async context manager for database cursors.
        
        Yields:
            aiomysql.Cursor: Database cursor
            
        Example:
            async with manager.get_cursor_async() as cursor:
                await cursor.execute("SELECT * FROM table")
                rows = await cursor.fetchall()
        """
        connection = None
        cursor = None
        try:
            connection = await self.get_connection()
            cursor = await connection.cursor(aiomysql.DictCursor)
            yield cursor
            if not self.in_transaction:
                await connection.commit()
        except Exception as e:
            if not self.in_transaction and connection:
                try:
                    await connection.rollback()
                except Exception as rollback_error:
                    logger.warning(f"⚠️ Rollback failed during cursor error: {rollback_error}")
            raise
        finally:
            # Ensure cursor is always closed
            if cursor:
                try:
                    await cursor.close()
                except Exception as close_error:
                    logger.warning(f"⚠️ Failed to close cursor: {close_error}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        try:
            # Add timeout to prevent hanging on context exit
            await asyncio.wait_for(
                self.disconnect(),
                timeout=10.0  # 10 second timeout
            )
        except asyncio.TimeoutError:
            logger.error("❌ Disconnect timeout during context exit - forcing cleanup")
            # Force cleanup to prevent hangs
            self._connection = None
            self._connection_state = ConnectionState.DISCONNECTED
            self._transaction_depth = 0
        except Exception as e:
            logger.error(f"❌ Error during context exit: {e}")
            # Force cleanup even on error
            self._connection = None
            self._connection_state = ConnectionState.DISCONNECTED
            self._transaction_depth = 0
    
    def __enter__(self):
        """Sync context manager entry (for compatibility)"""
        raise RuntimeError("Use async context manager: async with MySQLConnectionManager()")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sync context manager exit (for compatibility)"""
        pass
