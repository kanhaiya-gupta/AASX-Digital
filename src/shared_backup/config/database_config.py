"""
Database Configuration
=====================

Database configuration settings for the AAS Data Modeling framework.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    
    # Database type
    database_type: str = "sqlite"  # sqlite, postgresql, mysql
    
    # Connection settings
    host: Optional[str] = None
    port: Optional[int] = None
    database_name: str = "aas_data_modeling"
    username: Optional[str] = None
    password: Optional[str] = None
    
    # SQLite specific
    database_path: str = "database/aas_data_modeling.db"
    
    # Connection pool settings
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    # Performance settings
    echo: bool = False  # SQL echo
    pool_pre_ping: bool = True
    
    # Migration settings
    auto_migrate: bool = True
    backup_before_migrate: bool = True
    
    @classmethod
    def from_environment(cls) -> 'DatabaseConfig':
        """Create configuration from environment variables."""
        return cls(
            database_type=os.getenv('DATABASE_TYPE', 'sqlite'),
            host=os.getenv('DATABASE_HOST'),
            port=int(os.getenv('DATABASE_PORT', '0')) if os.getenv('DATABASE_PORT') else None,
            database_name=os.getenv('DATABASE_NAME', 'aas_data_modeling'),
            username=os.getenv('DATABASE_USERNAME'),
            password=os.getenv('DATABASE_PASSWORD'),
            database_path=os.getenv('DATABASE_PATH', 'database/aas_data_modeling.db'),
            pool_size=int(os.getenv('DATABASE_POOL_SIZE', '10')),
            max_overflow=int(os.getenv('DATABASE_MAX_OVERFLOW', '20')),
            pool_timeout=int(os.getenv('DATABASE_POOL_TIMEOUT', '30')),
            pool_recycle=int(os.getenv('DATABASE_POOL_RECYCLE', '3600')),
            echo=os.getenv('DATABASE_ECHO', 'false').lower() == 'true',
            pool_pre_ping=os.getenv('DATABASE_POOL_PRE_PING', 'true').lower() == 'true',
            auto_migrate=os.getenv('DATABASE_AUTO_MIGRATE', 'true').lower() == 'true',
            backup_before_migrate=os.getenv('DATABASE_BACKUP_BEFORE_MIGRATE', 'true').lower() == 'true'
        )
    
    def get_connection_string(self) -> str:
        """Get database connection string."""
        if self.database_type == 'sqlite':
            return f"sqlite:///{self.database_path}"
        elif self.database_type == 'postgresql':
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database_name}"
        elif self.database_type == 'mysql':
            return f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database_name}"
        else:
            raise ValueError(f"Unsupported database type: {self.database_type}")
    
    def get_engine_kwargs(self) -> Dict[str, Any]:
        """Get SQLAlchemy engine keyword arguments."""
        kwargs = {
            'pool_size': self.pool_size,
            'max_overflow': self.max_overflow,
            'pool_timeout': self.pool_timeout,
            'pool_recycle': self.pool_recycle,
            'echo': self.echo,
            'pool_pre_ping': self.pool_pre_ping
        }
        
        # Remove None values
        return {k: v for k, v in kwargs.items() if v is not None}
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        if self.database_type not in ['sqlite', 'postgresql', 'mysql']:
            raise ValueError(f"Unsupported database type: {self.database_type}")
        
        if self.database_type == 'sqlite':
            # Ensure database directory exists
            db_path = Path(self.database_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            # Check required fields for other database types
            if not self.host:
                raise ValueError("Database host is required for non-SQLite databases")
            if not self.port:
                raise ValueError("Database port is required for non-SQLite databases")
            if not self.username:
                raise ValueError("Database username is required for non-SQLite databases")
            if not self.password:
                raise ValueError("Database password is required for non-SQLite databases")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'database_type': self.database_type,
            'host': self.host,
            'port': self.port,
            'database_name': self.database_name,
            'username': self.username,
            'password': '***' if self.password else None,  # Mask password
            'database_path': self.database_path,
            'pool_size': self.pool_size,
            'max_overflow': self.max_overflow,
            'pool_timeout': self.pool_timeout,
            'pool_recycle': self.pool_recycle,
            'echo': self.echo,
            'pool_pre_ping': self.pool_pre_ping,
            'auto_migrate': self.auto_migrate,
            'backup_before_migrate': self.backup_before_migrate
        }

class DatabaseConfigManager:
    """Manager for database configurations."""
    
    # Default configurations for different environments
    DEFAULT_CONFIGS = {
        'development': DatabaseConfig(
            database_type='sqlite',
            database_path='database/aas_data_modeling_dev.db',
            echo=True,
            auto_migrate=True
        ),
        'testing': DatabaseConfig(
            database_type='sqlite',
            database_path=':memory:',  # In-memory database for testing
            echo=False,
            auto_migrate=True
        ),
        'production': DatabaseConfig(
            database_type='sqlite',  # Can be changed to postgresql/mysql
            database_path='database/aas_data_modeling_prod.db',
            echo=False,
            auto_migrate=False,  # Manual migrations in production
            backup_before_migrate=True
        )
    }
    
    @classmethod
    def get_config(cls, environment: str = None) -> DatabaseConfig:
        """Get database configuration for the specified environment."""
        if environment is None:
            environment = os.getenv('ENVIRONMENT', 'development')
        
        # Try to get from environment variables first
        try:
            config = DatabaseConfig.from_environment()
            config.validate()
            return config
        except (ValueError, TypeError):
            pass
        
        # Fall back to default configurations
        if environment in cls.DEFAULT_CONFIGS:
            config = cls.DEFAULT_CONFIGS[environment]
            config.validate()
            return config
        
        # Fall back to development configuration
        config = cls.DEFAULT_CONFIGS['development']
        config.validate()
        return config
    
    @classmethod
    def create_backup_config(cls, original_config: DatabaseConfig) -> DatabaseConfig:
        """Create a backup configuration."""
        backup_config = DatabaseConfig(
            database_type=original_config.database_type,
            host=original_config.host,
            port=original_config.port,
            database_name=f"{original_config.database_name}_backup",
            username=original_config.username,
            password=original_config.password,
            database_path=f"{original_config.database_path}.backup",
            pool_size=original_config.pool_size,
            max_overflow=original_config.max_overflow,
            pool_timeout=original_config.pool_timeout,
            pool_recycle=original_config.pool_recycle,
            echo=original_config.echo,
            pool_pre_ping=original_config.pool_pre_ping,
            auto_migrate=False,
            backup_before_migrate=False
        )
        return backup_config
    
    @classmethod
    def get_test_config(cls) -> DatabaseConfig:
        """Get configuration for testing."""
        return cls.get_config('testing')
    
    @classmethod
    def get_development_config(cls) -> DatabaseConfig:
        """Get configuration for development."""
        return cls.get_config('development')
    
    @classmethod
    def get_production_config(cls) -> DatabaseConfig:
        """Get configuration for production."""
        return cls.get_config('production')

# Convenience functions
def get_database_config(environment: str = None) -> DatabaseConfig:
    """Get database configuration."""
    return DatabaseConfigManager.get_config(environment)

def get_test_database_config() -> DatabaseConfig:
    """Get test database configuration."""
    return DatabaseConfigManager.get_test_config()

def get_development_database_config() -> DatabaseConfig:
    """Get development database configuration."""
    return DatabaseConfigManager.get_development_config()

def get_production_database_config() -> DatabaseConfig:
    """Get production database configuration."""
    return DatabaseConfigManager.get_production_config() 