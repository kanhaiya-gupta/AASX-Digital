"""
Protocol interfaces for the engine system.

This module defines the protocol interfaces (structural subtyping) that all
engine components must implement, ensuring type safety and consistency.
"""

from typing import Protocol, Any, Dict, List, Optional, Union, Callable, Awaitable
from typing_extensions import runtime_checkable


@runtime_checkable
class ServiceProtocol(Protocol):
    """Protocol for service layer components."""
    
    name: str
    
    async def initialize(self) -> bool:
        """Initialize the service."""
        ...
    
    async def shutdown(self) -> bool:
        """Shutdown the service gracefully."""
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health."""
        ...
    
    def is_initialized(self) -> bool:
        """Check if service is initialized."""
        ...


@runtime_checkable
class RepositoryProtocol(Protocol):
    """Protocol for repository components."""
    
    name: str
    
    async def connect(self) -> bool:
        """Establish connection to data source."""
        ...
    
    async def disconnect(self) -> bool:
        """Close connection to data source."""
        ...
    
    async def create(self, entity: Any) -> Optional[Any]:
        """Create a new entity."""
        ...
    
    async def read(self, identifier: Any) -> Optional[Any]:
        """Read an entity by identifier."""
        ...
    
    async def update(self, entity: Any) -> Optional[Any]:
        """Update an existing entity."""
        ...
    
    async def delete(self, identifier: Any) -> bool:
        """Delete an entity by identifier."""
        ...
    
    async def list(self, filters: Optional[Dict[str, Any]] = None, 
                   limit: Optional[int] = None, offset: Optional[int] = None) -> List[Any]:
        """List entities with optional filtering and pagination."""
        ...
    
    def is_connected(self) -> bool:
        """Check if repository is connected."""
        ...


@runtime_checkable
class ManagerProtocol(Protocol):
    """Protocol for manager components."""
    
    name: str
    
    async def initialize(self) -> bool:
        """Initialize the manager and all its components."""
        ...
    
    async def shutdown(self) -> bool:
        """Shutdown the manager and all its components gracefully."""
        ...
    
    def register_service(self, name: str, service: ServiceProtocol) -> None:
        """Register a service with this manager."""
        ...
    
    def register_repository(self, name: str, repository: RepositoryProtocol) -> None:
        """Register a repository with this manager."""
        ...
    
    def get_service(self, name: str) -> Optional[ServiceProtocol]:
        """Get a registered service by name."""
        ...
    
    def get_repository(self, name: str) -> Optional[RepositoryProtocol]:
        """Get a registered repository by name."""
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all registered components."""
        ...


@runtime_checkable
class ValidatorProtocol(Protocol):
    """Protocol for validator components."""
    
    name: str
    
    async def validate(self, data: Any) -> bool:
        """Validate data."""
        ...
    
    async def get_validation_errors(self) -> List[str]:
        """Get list of validation errors."""
        ...
    
    def is_valid(self, data: Any) -> bool:
        """Check if data is valid (synchronous wrapper)."""
        ...


@runtime_checkable
class CacheProtocol(Protocol):
    """Protocol for cache components."""
    
    name: str
    default_ttl: int
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        ...
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        ...
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        ...
    
    async def clear(self) -> bool:
        """Clear all cache entries."""
        ...
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        ...
    
    async def get_or_set(self, key: str, default_factory: Callable, ttl: Optional[int] = None) -> Any:
        """Get value from cache or set default if not exists."""
        ...


@runtime_checkable
class EventEmitterProtocol(Protocol):
    """Protocol for event emitter components."""
    
    name: str
    
    async def emit(self, event: str, data: Any = None) -> bool:
        """Emit an event."""
        ...
    
    async def on(self, event: str, callback: Callable) -> bool:
        """Register event listener."""
        ...
    
    async def off(self, event: str, callback: Callable) -> bool:
        """Remove event listener."""
        ...
    
    async def once(self, event: str, callback: Callable) -> bool:
        """Register one-time event listener."""
        ...
    
    def get_listener_count(self, event: str) -> int:
        """Get number of listeners for an event."""
        ...


@runtime_checkable
class TaskManagerProtocol(Protocol):
    """Protocol for task manager components."""
    
    name: str
    max_workers: int
    
    async def start(self) -> bool:
        """Start the task manager."""
        ...
    
    async def stop(self) -> bool:
        """Stop the task manager."""
        ...
    
    async def submit_task(self, task_func: Callable, *args, **kwargs) -> str:
        """Submit a task for execution."""
        ...
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        ...
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a task."""
        ...
    
    def is_running(self) -> bool:
        """Check if task manager is running."""
        ...
    
    def get_task_count(self) -> int:
        """Get total number of tasks."""
        ...


@runtime_checkable
class ConnectionManagerProtocol(Protocol):
    """Protocol for database connection managers."""
    
    connection_string: str
    is_connected: bool
    
    async def connect(self) -> bool:
        """Establish database connection."""
        ...
    
    async def disconnect(self) -> bool:
        """Close database connection."""
        ...
    
    async def test_connection(self) -> bool:
        """Test database connection."""
        ...
    
    async def get_connection(self) -> Any:
        """Get database connection."""
        ...
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a query."""
        ...
    
    async def execute_update(self, query: str, params: Optional[Dict[str, Any]] = None) -> int:
        """Execute an update/insert/delete statement."""
        ...
    
    async def begin_transaction(self) -> bool:
        """Begin a database transaction."""
        ...
    
    async def commit_transaction(self) -> bool:
        """Commit current transaction."""
        ...
    
    async def rollback_transaction(self) -> bool:
        """Rollback current transaction."""
        ...
    
    async def execute_transaction(self, queries: List[Dict[str, Any]]) -> bool:
        """Execute multiple queries in a transaction."""
        ...
    
    async def get_database_info(self) -> Dict[str, Any]:
        """Get database information."""
        ...


@runtime_checkable
class SchemaManagerProtocol(Protocol):
    """Protocol for schema management components."""
    
    async def initialize(self) -> bool:
        """Initialize the schema manager."""
        ...
    
    async def create_all_tables(self) -> bool:
        """Create all tables."""
        ...
    
    async def drop_all_tables(self) -> bool:
        """Drop all tables."""
        ...
    
    async def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get information about a specific table."""
        ...
    
    async def get_all_tables(self) -> List[str]:
        """Get list of all tables."""
        ...
    
    async def table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        ...
    
    async def validate_schema(self) -> Dict[str, Any]:
        """Validate the current schema."""
        ...
