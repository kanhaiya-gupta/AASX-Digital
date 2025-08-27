"""
Database Factory Pattern
========================

Creates the appropriate database connection manager based on configuration.
Supports SQLite, PostgreSQL, and MySQL with pure async implementations.
All managers are designed for high-performance, non-blocking operations.
"""

import logging
from typing import Dict, Any, Union, Optional
from pathlib import Path
from enum import Enum

from .connection_manager import ConnectionManager
from .sqlite_manager import SQLiteConnectionManager
from .postgres_manager import PostgresConnectionManager
from .mysql_manager import MySQLConnectionManager

logger = logging.getLogger(__name__)

class DatabaseType(Enum):
    """Supported database types"""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"

class ConnectionMode(Enum):
    """Connection modes"""
    SYNC = "sync"
    ASYNC = "async"

class DatabaseFactory:
    """Factory for creating database connection managers"""
    
    @staticmethod
    def create_connection_manager(
        database_type: Union[str, DatabaseType],
        connection_config: Union[str, Path, Dict[str, Any]],
        mode: Union[str, ConnectionMode] = ConnectionMode.ASYNC
    ) -> ConnectionManager:
        """
        Create a database connection manager based on type and configuration.
        
        Args:
            database_type: Type of database (sqlite, postgresql, mysql)
            connection_config: Connection configuration
                - For SQLite: Path to database file
                - For PostgreSQL/MySQL: Connection parameters dict
            mode: Connection mode (async only - maintained for compatibility)
            
        Returns:
            Database connection manager instance (all are pure async)
            
        Raises:
            ValueError: If database type is not supported
            ImportError: If required dependencies are not available
        """
        
        # Normalize database type
        if isinstance(database_type, str):
            database_type = DatabaseType(database_type.lower())
        
        # Normalize mode
        if isinstance(mode, str):
            mode = ConnectionMode(mode.lower())
        
        logger.info(f"🏗️ Creating {mode.value} {database_type.value} connection manager")
        
        try:
            if database_type == DatabaseType.SQLITE:
                # SQLiteConnectionManager is pure async
                return SQLiteConnectionManager(connection_config)
                
            elif database_type == DatabaseType.POSTGRESQL:
                if not isinstance(connection_config, dict):
                    raise ValueError("PostgreSQL requires connection parameters dictionary")
                
                # PostgresConnectionManager is pure async
                return PostgresConnectionManager(connection_config)
                    
            elif database_type == DatabaseType.MYSQL:
                if not isinstance(connection_config, dict):
                    raise ValueError("MySQL requires connection parameters dictionary")
                
                # MySQLConnectionManager is pure async
                return MySQLConnectionManager(connection_config)
                    
            else:
                raise ValueError(f"Unsupported database type: {database_type}")
                
        except Exception as e:
            logger.error(f"❌ Failed to create {database_type.value} connection manager: {e}")
            raise
    
    @staticmethod
    def create_from_config(config: Dict[str, Any]) -> ConnectionManager:
        """
        Create database connection manager from configuration dictionary.
        
        Args:
            config: Configuration dictionary with keys:
                - type: Database type (sqlite, postgresql, mysql)
                - mode: Connection mode (sync, async) - optional, defaults to sync
                - connection: Connection configuration
                    - For SQLite: path string
                    - For PostgreSQL/MySQL: connection parameters dict
                
        Returns:
            Database connection manager instance
        """
        
        required_keys = ['type', 'connection']
        missing_keys = [key for key in required_keys if key not in config]
        
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {missing_keys}")
        
        database_type = config['type']
        connection_config = config['connection']
        mode = config.get('mode', 'async')
        
        return DatabaseFactory.create_connection_manager(
            database_type=database_type,
            connection_config=connection_config,
            mode=mode
        )
    
    @staticmethod
    def create_from_url(
        database_url: str,
        mode: Union[str, ConnectionMode] = ConnectionMode.ASYNC
    ) -> ConnectionManager:
        """
        Create database connection manager from URL string.
        
        Args:
            database_url: Database URL in format:
                - SQLite: sqlite:///path/to/database.db
                - PostgreSQL: postgresql://user:password@host:port/database
                - MySQL: mysql://user:password@host:port/database
            mode: Connection mode (async only - maintained for compatibility)
            
        Returns:
            Database connection manager instance (all are pure async)
        """
        
        try:
            if database_url.startswith('sqlite:///'):
                # SQLite: sqlite:///path/to/database.db
                db_path = database_url.replace('sqlite:///', '')
                return DatabaseFactory.create_connection_manager(
                    database_type=DatabaseType.SQLITE,
                    connection_config=db_path,
                    mode=mode
                )
                
            elif database_url.startswith('postgresql://'):
                # PostgreSQL: postgresql://user:password@host:port/database
                connection_params = DatabaseFactory._parse_postgresql_url(database_url)
                return DatabaseFactory.create_connection_manager(
                    database_type=DatabaseType.POSTGRESQL,
                    connection_config=connection_params,
                    mode=mode
                )
                
            elif database_url.startswith('mysql://'):
                # MySQL: mysql://user:password@host:port/database
                connection_params = DatabaseFactory._parse_mysql_url(database_url)
                return DatabaseFactory.create_connection_manager(
                    database_type=DatabaseType.MYSQL,
                    connection_config=connection_params,
                    mode=mode
                )
                
            else:
                raise ValueError(f"Unsupported database URL format: {database_url}")
                
        except Exception as e:
            logger.error(f"❌ Failed to create connection manager from URL: {e}")
            raise
    
    @staticmethod
    def _parse_postgresql_url(url: str) -> Dict[str, Any]:
        """Parse PostgreSQL URL into connection parameters"""
        # Remove postgresql:// prefix
        url = url.replace('postgresql://', '')
        
        # Split into user:password@host:port/database
        if '@' in url:
            auth_part, rest = url.split('@', 1)
        else:
            auth_part, rest = '', url
        
        # Parse authentication
        if auth_part:
            if ':' in auth_part:
                user, password = auth_part.split(':', 1)
            else:
                user, password = auth_part, ''
        else:
            user, password = 'postgres', ''
        
        # Parse host:port/database
        if '/' in rest:
            host_port, database = rest.split('/', 1)
        else:
            host_port, database = rest, 'postgres'
        
        # Parse host and port
        if ':' in host_port:
            host, port = host_port.split(':', 1)
            port = int(port)
        else:
            host, port = host_port, 5432
        
        return {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
    
    @staticmethod
    def _parse_mysql_url(url: str) -> Dict[str, Any]:
        """Parse MySQL URL into connection parameters"""
        # Remove mysql:// prefix
        url = url.replace('mysql://', '')
        
        # Split into user:password@host:port/database
        if '@' in url:
            auth_part, rest = url.split('@', 1)
        else:
            auth_part, rest = '', url
        
        # Parse authentication
        if auth_part:
            if ':' in auth_part:
                user, password = auth_part.split(':', 1)
            else:
                user, password = auth_part, ''
        else:
            user, password = 'root', ''
        
        # Parse host:port/database
        if '/' in rest:
            host_port, database = rest.split('/', 1)
        else:
            host_port, database = rest, 'mysql'
        
        # Parse host and port
        if ':' in host_port:
            host, port = host_port.split(':', 1)
            port = int(port)
        else:
            host, port = host_port, 3306
        
        return {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
    
    @staticmethod
    def get_supported_databases() -> Dict[str, Dict[str, Any]]:
        """Get information about supported database types"""
        return {
            'sqlite': {
                'description': 'SQLite database (file-based) - Pure Async',
                'sync_support': False,
                'async_support': True,
                'connection_pooling': False,
                'requirements': ['aiosqlite'],
                'url_format': 'sqlite:///path/to/database.db'
            },
            'postgresql': {
                'description': 'PostgreSQL database server - Pure Async',
                'sync_support': False,
                'async_support': True,
                'connection_pooling': True,
                'requirements': ['asyncpg'],
                'url_format': 'postgresql://user:password@host:port/database'
            },
            'mysql': {
                'description': 'MySQL database server - Pure Async',
                'sync_support': False,
                'async_support': True,
                'connection_pooling': True,
                'requirements': ['aiomysql'],
                'url_format': 'mysql://user:password@host:port/database'
            }
        }
    
    @staticmethod
    def test_connection(connection_manager: ConnectionManager) -> bool:
        """Test if a database connection is working"""
        try:
            return connection_manager.test_connection()
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False
    
    @staticmethod
    def get_connection_info(connection_manager: ConnectionManager) -> Dict[str, Any]:
        """Get database connection information"""
        try:
            return connection_manager.get_database_info()
        except Exception as e:
            logger.error(f"❌ Failed to get connection info: {e}")
            return {'error': str(e)}

# Convenience functions for common use cases
def create_sqlite_manager(db_path: Union[str, Path]) -> SQLiteConnectionManager:
    """Create SQLite connection manager (Pure Async)"""
    return DatabaseFactory.create_connection_manager(
        database_type=DatabaseType.SQLITE,
        connection_config=db_path
    )

def create_postgresql_manager(
    host: str = 'localhost',
    port: int = 5432,
    database: str = 'postgres',
    user: str = 'postgres',
    password: str = '',
    **kwargs
) -> PostgresConnectionManager:
    """Create PostgreSQL connection manager (Pure Async)"""
    config = {
        'host': host,
        'port': port,
        'database': database,
        'user': user,
        'password': password,
        **kwargs
    }
    return DatabaseFactory.create_connection_manager(
        database_type=DatabaseType.POSTGRESQL,
        connection_config=config
    )

def create_mysql_manager(
    host: str = 'localhost',
    port: int = 3306,
    database: str = 'mysql',
    user: str = 'root',
    password: str = '',
    **kwargs
) -> MySQLConnectionManager:
    """Create MySQL connection manager (Pure Async)"""
    config = {
        'host': host,
        'port': port,
        'database': database,
        'user': user,
        'password': password,
        **kwargs
    }
    return DatabaseFactory.create_connection_manager(
        database_type=DatabaseType.MYSQL,
        connection_config=config
    )
