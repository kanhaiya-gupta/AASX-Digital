"""
Core framework components for the engine system.

This module provides the foundational building blocks including:
- Abstract base classes
- Protocol interfaces
- Custom exceptions
- System constants
- Common decorators
"""

from .base_classes import (
    BaseService,
    BaseRepository,
    BaseManager,
    BaseValidator,
    BaseCache,
    BaseEventEmitter,
    BaseTaskManager
)

from .interfaces import (
    ServiceProtocol,
    RepositoryProtocol,
    ManagerProtocol,
    ValidatorProtocol,
    CacheProtocol,
    EventEmitterProtocol,
    TaskManagerProtocol
)

from .exceptions import (
    EngineException,
    DatabaseException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    ConfigurationException,
    ServiceException,
    RepositoryException
)

from .constants import (
    DatabaseType,
    ConnectionStrategy,
    CacheStrategy,
    LogLevel,
    TaskPriority,
    EventType
)

from .decorators import (
    retry,
    timeout,
    cache,
    validate,
    log_execution,
    measure_performance,
    require_auth,
    require_permission
)

__all__ = [
    # Base Classes
    'BaseService',
    'BaseRepository', 
    'BaseManager',
    'BaseValidator',
    'BaseCache',
    'BaseEventEmitter',
    'BaseTaskManager',
    
    # Interfaces
    'ServiceProtocol',
    'RepositoryProtocol',
    'ManagerProtocol',
    'ValidatorProtocol',
    'CacheProtocol',
    'EventEmitterProtocol',
    'TaskManagerProtocol',
    
    # Exceptions
    'EngineException',
    'DatabaseException',
    'ValidationException',
    'AuthenticationException',
    'AuthorizationException',
    'ConfigurationException',
    'ServiceException',
    'RepositoryException',
    
    # Constants
    'DatabaseType',
    'ConnectionStrategy',
    'CacheStrategy',
    'LogLevel',
    'TaskPriority',
    'EventType',
    
    # Decorators
    'retry',
    'timeout',
    'cache',
    'validate',
    'log_execution',
    'measure_performance',
    'require_auth',
    'require_permission'
]
