"""
Connection Pool Manager
======================

Provides efficient connection pooling for all database types.
Supports connection lifecycle management, health checks, and load balancing.
"""

import logging
import asyncio
import time
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass
from enum import Enum
from contextlib import asynccontextmanager, contextmanager
import threading
from collections import deque

logger = logging.getLogger(__name__)

class PoolStrategy(Enum):
    """Connection pool strategies"""
    FIFO = "fifo"  # First In, First Out
    LIFO = "lifo"  # Last In, First Out
    ROUND_ROBIN = "round_robin"  # Round Robin
    LEAST_CONNECTIONS = "least_connections"  # Least Connections

@dataclass
class PoolConfig:
    """Connection pool configuration"""
    min_size: int = 1
    max_size: int = 10
    max_overflow: int = 20
    timeout: float = 30.0
    recycle: int = 3600  # seconds
    echo: bool = False
    strategy: PoolStrategy = PoolStrategy.FIFO
    pre_ping: bool = True
    health_check_interval: int = 60  # seconds

@dataclass
class ConnectionInfo:
    """Connection information and metadata"""
    connection: Any
    created_at: float
    last_used: float
    use_count: int
    is_active: bool
    last_health_check: float
    health_status: bool

class BaseConnectionPool:
    """Base connection pool implementation"""
    
    def __init__(self, config: PoolConfig):
        self.config = config
        self._pool: deque = deque()
        self._overflow_pool: deque = deque()
        self._active_connections: int = 0
        self._total_connections: int = 0
        self._lock = threading.Lock()
        self._health_check_task = None
        self._last_health_check = time.time()
        
        logger.info(f"🏊 Connection pool initialized: min={config.min_size}, max={config.max_size}, overflow={config.max_overflow}")
    
    def _get_connection_strategy(self) -> Optional[Any]:
        """Get connection based on pool strategy"""
        if not self._pool:
            return None
        
        if self.config.strategy == PoolStrategy.FIFO:
            return self._pool.popleft()
        elif self.config.strategy == PoolStrategy.LIFO:
            return self._pool.pop()
        elif self.config.strategy == PoolStrategy.ROUND_ROBIN:
            conn = self._pool.popleft()
            self._pool.append(conn)
            return conn
        elif self.config.strategy == PoolStrategy.LEAST_CONNECTIONS:
            # Find connection with least use count
            min_use = float('inf')
            min_conn = None
            min_index = -1
            
            for i, conn_info in enumerate(self._pool):
                if conn_info.use_count < min_use:
                    min_use = conn_info.use_count
                    min_conn = conn_info
                    min_index = i
            
            if min_conn:
                self._pool.remove(min_conn)
                return min_conn
        
        return self._pool.popleft()
    
    def _add_connection(self, connection: Any) -> None:
        """Add connection to pool"""
        conn_info = ConnectionInfo(
            connection=connection,
            created_at=time.time(),
            last_used=time.time(),
            use_count=0,
            is_active=True,
            last_health_check=time.time(),
            health_status=True
        )
        
        with self._lock:
            if len(self._pool) < self.config.max_size:
                self._pool.append(conn_info)
            else:
                self._overflow_pool.append(conn_info)
    
    def _remove_connection(self, connection: Any) -> None:
        """Remove connection from pool"""
        with self._lock:
            # Remove from main pool
            for conn_info in self._pool:
                if conn_info.connection == connection:
                    self._pool.remove(conn_info)
                    self._active_connections -= 1
                    return
            
            # Remove from overflow pool
            for conn_info in self._overflow_pool:
                if conn_info.connection == connection:
                    self._overflow_pool.remove(conn_info)
                    self._active_connections -= 1
                    return
    
    def _cleanup_expired_connections(self) -> None:
        """Remove expired connections based on recycle time"""
        current_time = time.time()
        
        with self._lock:
            # Clean main pool
            expired = [conn for conn in self._pool if current_time - conn.created_at > self.config.recycle]
            for conn_info in expired:
                self._pool.remove(conn_info)
                self._active_connections -= 1
                try:
                    conn_info.connection.close()
                except:
                    pass
            
            # Clean overflow pool
            expired = [conn for conn in self._overflow_pool if current_time - conn.created_at > self.config.recycle]
            for conn_info in expired:
                self._overflow_pool.remove(conn_info)
                self._active_connections -= 1
                try:
                    conn_info.connection.close()
                except:
                    pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics"""
        with self._lock:
            return {
                'pool_size': len(self._pool),
                'overflow_size': len(self._overflow_pool),
                'active_connections': self._active_connections,
                'total_connections': self._total_connections,
                'max_size': self.config.max_size,
                'max_overflow': self.config.max_overflow,
                'strategy': self.config.strategy.value
            }
    
    def close(self) -> None:
        """Close all connections in the pool"""
        with self._lock:
            # Close main pool connections
            for conn_info in self._pool:
                try:
                    conn_info.connection.close()
                except:
                    pass
            self._pool.clear()
            
            # Close overflow pool connections
            for conn_info in self._overflow_pool:
                try:
                    conn_info.connection.close()
                except:
                    pass
            self._overflow_pool.clear()
            
            self._active_connections = 0
            self._total_connections = 0
        
        logger.info("🏊 Connection pool closed")

class SyncConnectionPool(BaseConnectionPool):
    """Synchronous connection pool"""
    
    def __init__(self, config: PoolConfig, connection_factory: Callable[[], Any]):
        super().__init__(config)
        self.connection_factory = connection_factory
        self._initialize_pool()
    
    def _initialize_pool(self) -> None:
        """Initialize pool with minimum connections"""
        for _ in range(self.config.min_size):
            try:
                connection = self.connection_factory()
                self._add_connection(connection)
                self._total_connections += 1
            except Exception as e:
                logger.warning(f"⚠️ Failed to create initial connection: {e}")
    
    @contextmanager
    def get_connection(self):
        """Get a connection from the pool (context manager)"""
        connection = None
        try:
            connection = self._get_connection()
            if connection is None:
                # Create new connection if pool is empty and we haven't reached max overflow
                if self._active_connections < self.config.max_size + self.config.max_overflow:
                    connection = self.connection_factory()
                    self._total_connections += 1
                else:
                    raise RuntimeError("No connections available and max overflow reached")
            
            self._active_connections += 1
            yield connection
            
        except Exception as e:
            logger.error(f"❌ Error getting connection from pool: {e}")
            raise
        finally:
            if connection:
                self._return_connection(connection)
    
    def _get_connection(self) -> Optional[Any]:
        """Get connection from pool"""
        with self._lock:
            if self._pool:
                conn_info = self._get_connection_strategy()
                if conn_info:
                    conn_info.last_used = time.time()
                    conn_info.use_count += 1
                    return conn_info.connection
            
            return None
    
    def _return_connection(self, connection: Any) -> None:
        """Return connection to pool"""
        with self._lock:
            self._active_connections -= 1
            
            # Check if connection should be returned to pool
            if len(self._pool) < self.config.max_size:
                self._add_connection(connection)
            else:
                # Close overflow connection
                try:
                    connection.close()
                except:
                    pass
                self._total_connections -= 1

class AsyncConnectionPool(BaseConnectionPool):
    """Asynchronous connection pool"""
    
    def __init__(self, config: PoolConfig, connection_factory: Callable[[], Any]):
        super().__init__(config)
        self.connection_factory = connection_factory
        self._loop = asyncio.get_event_loop()
        # Replace threading lock with asyncio lock for async operations
        self._async_lock = asyncio.Lock()
        self._initialize_pool()
    
    def _initialize_pool(self) -> None:
        """Initialize pool with minimum connections"""
        async def _init():
            for _ in range(self.config.min_size):
                try:
                    connection = await self.connection_factory()
                    self._add_connection(connection)
                    self._total_connections += 1
                except Exception as e:
                    logger.warning(f"⚠️ Failed to create initial async connection: {e}")
        
        # Schedule initialization only if we have a running event loop
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(_init())
        except RuntimeError:
            # No running event loop, we'll initialize when the first connection is requested
            logger.info("ℹ️ No running event loop, async pool will initialize on first use")
            # Don't set _total_connections here - let it be initialized on first use
    
    async def _initialize_pool_async(self):
        """Initialize pool asynchronously"""
        for _ in range(self.config.min_size):
            try:
                connection = await self.connection_factory()
                self._add_connection(connection)
                self._total_connections += 1
            except Exception as e:
                logger.warning(f"⚠️ Failed to create initial async connection: {e}")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get a connection from the pool (async context manager)"""
        connection = None
        try:
            # Initialize pool if not already done
            if self._total_connections == 0:
                await self._initialize_pool_async()
            
            connection = await self._get_connection()
            if connection is None:
                # Create new connection if pool is empty and we haven't reached max overflow
                if self._active_connections < self.config.max_size + self.config.max_overflow:
                    connection = await self.connection_factory()
                    self._total_connections += 1
                else:
                    raise RuntimeError("No connections available and max overflow reached")
            
            self._active_connections += 1
            yield connection
            
        except Exception as e:
            logger.error(f"❌ Error getting async connection from pool: {e}")
            raise
        finally:
            if connection:
                await self._return_connection(connection)
    
    async def _get_connection(self) -> Optional[Any]:
        """Get connection from pool"""
        async with self._async_lock:
            if self._pool:
                conn_info = self._get_connection_strategy()
                if conn_info:
                    conn_info.last_used = time.time()
                    conn_info.use_count += 1
                    return conn_info.connection
            
            return None
    
    async def _return_connection(self, connection: Any) -> None:
        """Return connection to pool"""
        async with self._async_lock:
            self._active_connections -= 1
            
            # Check if connection should be returned to pool
            if len(self._pool) < self.config.max_size:
                self._add_connection(connection)
            else:
                # Close overflow connection
                try:
                    if hasattr(connection, 'close'):
                        await connection.close()
                    else:
                        connection.close()
                except:
                    pass
                self._total_connections -= 1
    
    def close(self) -> None:
        """Close all connections in the async pool"""
        with self._lock:
            # Close main pool connections
            for conn_info in self._pool:
                try:
                    # For async connections, we need to handle this differently
                    if hasattr(conn_info.connection, 'close'):
                        conn_info.connection.close()
                except:
                    pass
            self._pool.clear()
            
            # Close overflow pool connections
            for conn_info in self._overflow_pool:
                try:
                    if hasattr(conn_info.connection, 'close'):
                        conn_info.connection.close()
                except:
                    pass
            self._overflow_pool.clear()
            
            self._active_connections = 0
            self._total_connections = 0
        
        logger.info("🏊 Async connection pool closed")

class ConnectionPoolManager:
    """Manages multiple connection pools for different database types"""
    
    def __init__(self):
        self.pools: Dict[str, Union[SyncConnectionPool, AsyncConnectionPool]] = {}
        self._lock = threading.Lock()
    
    def create_pool(
        self,
        name: str,
        config: PoolConfig,
        connection_factory: Callable[[], Any],
        is_async: bool = False
    ) -> Union[SyncConnectionPool, AsyncConnectionPool]:
        """Create a new connection pool"""
        with self._lock:
            if name in self.pools:
                logger.warning(f"⚠️ Pool '{name}' already exists, replacing it")
                self.close_pool(name)
            
            if is_async:
                pool = AsyncConnectionPool(config, connection_factory)
            else:
                pool = SyncConnectionPool(config, connection_factory)
            
            self.pools[name] = pool
            logger.info(f"🏊 Created {name} connection pool")
            return pool
    
    def get_pool(self, name: str) -> Optional[Union[SyncConnectionPool, AsyncConnectionPool]]:
        """Get a connection pool by name"""
        return self.pools.get(name)
    
    def close_pool(self, name: str) -> bool:
        """Close a specific connection pool"""
        with self._lock:
            if name in self.pools:
                self.pools[name].close()
                del self.pools[name]
                logger.info(f"🏊 Closed {name} connection pool")
                return True
            return False
    
    def close_all_pools(self) -> None:
        """Close all connection pools"""
        with self._lock:
            for name in list(self.pools.keys()):
                self.close_pool(name)
        
        logger.info("🏊 All connection pools closed")
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all pools"""
        return {name: pool.get_stats() for name, pool in self.pools.items()}
    
    def health_check_all_pools(self) -> Dict[str, bool]:
        """Perform health check on all pools"""
        results = {}
        for name, pool in self.pools.items():
            try:
                # Basic health check - check if pool has connections
                stats = pool.get_stats()
                results[name] = stats['pool_size'] > 0
            except Exception as e:
                logger.error(f"❌ Health check failed for pool {name}: {e}")
                results[name] = False
        
        return results

# Global pool manager instance
pool_manager = ConnectionPoolManager()

# Convenience functions
def create_sync_pool(
    name: str,
    config: PoolConfig,
    connection_factory: Callable[[], Any]
) -> SyncConnectionPool:
    """Create a synchronous connection pool"""
    return pool_manager.create_pool(name, config, connection_factory, is_async=False)

def create_async_pool(
    name: str,
    config: PoolConfig,
    connection_factory: Callable[[], Any]
) -> AsyncConnectionPool:
    """Create an asynchronous connection pool"""
    return pool_manager.create_pool(name, config, connection_factory, is_async=True)

def get_pool(name: str) -> Optional[Union[SyncConnectionPool, AsyncConnectionPool]]:
    """Get a connection pool by name"""
    return pool_manager.get_pool(name)

def close_all_pools() -> None:
    """Close all connection pools"""
    pool_manager.close_all_pools()
