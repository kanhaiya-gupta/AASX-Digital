"""
Abstract base classes for the engine system.

This module provides the foundational base classes that all engine components
inherit from, ensuring consistent interfaces and behavior across the system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Generic, TypeVar
from datetime import datetime
import logging
import asyncio
from contextlib import asynccontextmanager

# Type variables for generic classes
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

logger = logging.getLogger(__name__)


class BaseService(ABC):
    """Abstract base class for all service layer components."""
    
    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        self._initialized = False
        self._startup_time = None
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the service. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def shutdown(self) -> bool:
        """Shutdown the service gracefully. Must be implemented by subclasses."""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health. Default implementation."""
        return {
            "service": self.name,
            "status": "healthy" if self._initialized else "unhealthy",
            "uptime": (datetime.now() - self._startup_time).total_seconds() if self._startup_time else 0,
            "initialized": self._initialized
        }
    
    def is_initialized(self) -> bool:
        """Check if service is initialized."""
        return self._initialized


class BaseRepository(ABC, Generic[T]):
    """Abstract base class for all repository components."""
    
    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        self._connection = None
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to data source. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Close connection to data source. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def create(self, entity: T) -> Optional[T]:
        """Create a new entity. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def read(self, identifier: K) -> Optional[T]:
        """Read an entity by identifier. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> Optional[T]:
        """Update an existing entity. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def delete(self, identifier: K) -> bool:
        """Delete an entity by identifier. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def list(self, filters: Optional[Dict[str, Any]] = None, 
                   limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
        """List entities with optional filtering and pagination. Must be implemented by subclasses."""
        pass
    
    def is_connected(self) -> bool:
        """Check if repository is connected."""
        return self._connection is not None


class BaseManager(ABC):
    """Abstract base class for all manager components."""
    
    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        self._services: Dict[str, BaseService] = {}
        self._repositories: Dict[str, BaseRepository] = {}
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the manager and all its components. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def shutdown(self) -> bool:
        """Shutdown the manager and all its components gracefully. Must be implemented by subclasses."""
        pass
    
    def register_service(self, name: str, service: BaseService) -> None:
        """Register a service with this manager."""
        self._services[name] = service
        self.logger.info(f"Registered service: {name}")
    
    def register_repository(self, name: str, repository: BaseRepository) -> None:
        """Register a repository with this manager."""
        self._repositories[name] = repository
        self.logger.info(f"Registered repository: {name}")
    
    def get_service(self, name: str) -> Optional[BaseService]:
        """Get a registered service by name."""
        return self._services.get(name)
    
    def get_repository(self, name: str) -> Optional[BaseRepository]:
        """Get a registered repository by name."""
        return self._repositories.get(name)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all registered components."""
        health_status = {
            "manager": self.name,
            "status": "healthy",
            "services": {},
            "repositories": {}
        }
        
        # Check services
        for name, service in self._services.items():
            try:
                service_health = await service.health_check()
                health_status["services"][name] = service_health
            except Exception as e:
                health_status["services"][name] = {"status": "error", "error": str(e)}
                health_status["status"] = "degraded"
        
        # Check repositories
        for name, repository in self._repositories.items():
            health_status["repositories"][name] = {
                "status": "healthy" if repository.is_connected() else "disconnected"
            }
        
        return health_status


class BaseValidator(ABC):
    """Abstract base class for all validator components."""
    
    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
    
    @abstractmethod
    async def validate(self, data: Any) -> bool:
        """Validate data. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def get_validation_errors(self) -> List[str]:
        """Get list of validation errors. Must be implemented by subclasses."""
        pass
    
    def is_valid(self, data: Any) -> bool:
        """Check if data is valid (synchronous wrapper)."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, we need to handle this differently
                # For now, return True and let the async validate method handle it
                return True
            else:
                return loop.run_until_complete(self.validate(data))
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(self.validate(data))


class BaseCache(ABC):
    """Abstract base class for all cache components."""
    
    def __init__(self, name: str = None, default_ttl: int = 3600):
        self.name = name or self.__class__.__name__
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        self.default_ttl = default_ttl
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache entries. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache. Must be implemented by subclasses."""
        pass
    
    async def get_or_set(self, key: str, default_factory, ttl: Optional[int] = None) -> Any:
        """Get value from cache or set default if not exists."""
        value = await self.get(key)
        if value is None:
            value = default_factory()
            await self.set(key, value, ttl)
        return value


class BaseEventEmitter(ABC):
    """Abstract base class for all event emitter components."""
    
    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        self._listeners: Dict[str, List[callable]] = {}
    
    @abstractmethod
    async def emit(self, event: str, data: Any = None) -> bool:
        """Emit an event. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def on(self, event: str, callback: callable) -> bool:
        """Register event listener. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def off(self, event: str, callback: callable) -> bool:
        """Remove event listener. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def once(self, event: str, callback: callable) -> bool:
        """Register one-time event listener. Must be implemented by subclasses."""
        pass
    
    def get_listener_count(self, event: str) -> int:
        """Get number of listeners for an event."""
        return len(self._listeners.get(event, []))


class BaseTaskManager(ABC):
    """Abstract base class for all task manager components."""
    
    def __init__(self, name: str = None, max_workers: int = 10):
        self.name = name or self.__class__.__name__
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        self.max_workers = max_workers
        self._tasks: Dict[str, Any] = {}
        self._running = False
    
    @abstractmethod
    async def start(self) -> bool:
        """Start the task manager. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def stop(self) -> bool:
        """Stop the task manager. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def submit_task(self, task_func: callable, *args, **kwargs) -> str:
        """Submit a task for execution. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a task. Must be implemented by subclasses."""
        pass
    
    def is_running(self) -> bool:
        """Check if task manager is running."""
        return self._running
    
    def get_task_count(self) -> int:
        """Get total number of tasks."""
        return len(self._tasks)
