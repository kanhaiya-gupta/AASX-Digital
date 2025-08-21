"""
Enterprise Patterns - World-Class Implementation
==============================================

Comprehensive enterprise patterns implementation for the AAS Data Modeling Engine.
Includes Factory, Builder, Observer, Strategy, Command, and other enterprise patterns.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type, TypeVar, Generic, Callable
from enum import Enum
import uuid
from datetime import datetime, timezone

from .base_model import BaseModel, ModelObserver, ModelFactory, ModelBuilder
from .enums import EventType, BusinessConstants, ValidationRules


# Generic type for models
T = TypeVar('T', bound=BaseModel)


# ============================================================================
# FACTORY PATTERN IMPLEMENTATIONS
# ============================================================================

class ModelFactoryRegistry:
    """Registry for model factories with lazy loading and caching."""
    
    def __init__(self):
        self._factories: Dict[str, 'AbstractModelFactory'] = {}
        self._factory_instances: Dict[str, 'AbstractModelFactory'] = {}
        self._cache_enabled = True
    
    def register_factory(self, model_type: str, factory_instance: 'AbstractModelFactory'):
        """Register a factory for a model type."""
        self._factories[model_type] = factory_instance
        print(f"Registered factory for model type: {model_type}")
    
    def get_factory(self, model_type: str) -> Optional['AbstractModelFactory']:
        """Get factory for a model type with caching."""
        if not self._cache_enabled:
            return self._factories.get(model_type)
        
        if model_type not in self._factory_instances:
            factory_instance = self._factories.get(model_type)
            if factory_instance:
                self._factory_instances[model_type] = factory_instance
        
        return self._factory_instances.get(model_type)
    
    def create_model(self, model_type: str, **kwargs) -> Optional[BaseModel]:
        """Create a model using the registered factory."""
        factory = self.get_factory(model_type)
        if factory:
            return factory.create_model(**kwargs)
        raise ValueError(f"No factory registered for model type: {model_type}")
    
    def list_registered_types(self) -> List[str]:
        """List all registered model types."""
        return list(self._factories.keys())
    
    def clear_cache(self):
        """Clear the factory cache."""
        self._factory_instances.clear()


class AbstractModelFactory(ABC):
    """Abstract base class for model factories."""
    
    @abstractmethod
    def create_model(self, **kwargs) -> BaseModel:
        """Create a model instance."""
        pass
    
    @abstractmethod
    def validate_creation_params(self, **kwargs) -> bool:
        """Validate creation parameters."""
        pass


class CoreSystemFactory(AbstractModelFactory):
    """Factory for creating core system models."""
    
    def create_model(self, **kwargs) -> BaseModel:
        """Create a core system model."""
        if not self.validate_creation_params(**kwargs):
            raise ValueError("Invalid creation parameters for core system model")
        
        # Import here to avoid circular imports
        from .core_system import CoreSystemRegistry, CoreSystemMetrics
        
        model_type = kwargs.get('model_type', 'registry')
        
        # Remove model_type from kwargs as it's not part of the actual model
        model_kwargs = {k: v for k, v in kwargs.items() if k != 'model_type'}
        
        if model_type == 'registry':
            return CoreSystemRegistry(**model_kwargs)
        elif model_type == 'metrics':
            return CoreSystemMetrics(**model_kwargs)
        else:
            raise ValueError(f"Unknown core system model type: {model_type}")
    
    def validate_creation_params(self, **kwargs) -> bool:
        """Validate creation parameters for core system models."""
        required_fields = ['model_type']
        
        if kwargs.get('model_type') == 'registry':
            required_fields.extend(['registry_id', 'system_name', 'registry_name'])
        elif kwargs.get('model_type') == 'metrics':
            required_fields.extend(['registry_id', 'metric_type'])
        
        return all(field in kwargs for field in required_fields)


class BusinessDomainFactory(AbstractModelFactory):
    """Factory for creating business domain models."""
    
    def create_model(self, **kwargs) -> BaseModel:
        """Create a business domain model."""
        if not self.validate_creation_params(**kwargs):
            raise ValueError("Invalid creation parameters for business domain model")
        
        # Import here to avoid circular imports
        from .business_domain import Organization, UseCase, Project, File, ProjectUseCaseLink
        from datetime import datetime, timezone
        
        model_type = kwargs.get('model_type')
        
        model_map = {
            'organization': Organization,
            'usecase': UseCase,
            'project': Project,
            'file': File,
            'projectusecaselink': ProjectUseCaseLink
        }
        
        if model_type not in model_map:
            raise ValueError(f"Unknown business domain model type: {model_type}")
        
        # Remove model_type from kwargs as it's not part of the actual model
        model_kwargs = {k: v for k, v in kwargs.items() if k != 'model_type'}
        
        # Add required timestamp fields for models that need them
        if model_type == 'organization':
            timestamp = datetime.now(timezone.utc).isoformat()
            if 'created_at' not in model_kwargs:
                model_kwargs['created_at'] = timestamp
            if 'updated_at' not in model_kwargs:
                model_kwargs['updated_at'] = timestamp
        
        return model_map[model_type](**model_kwargs)
    
    def validate_creation_params(self, **kwargs) -> bool:
        """Validate creation parameters for business domain models."""
        required_fields = ['model_type']
        
        model_type = kwargs.get('model_type')
        if model_type == 'organization':
            required_fields.extend(['org_id', 'name'])
        elif model_type == 'usecase':
            required_fields.extend(['use_case_id', 'name'])
        elif model_type == 'project':
            required_fields.extend(['project_id', 'name'])
        elif model_type == 'file':
            required_fields.extend(['filename', 'original_filename', 'project_id', 'filepath'])
        elif model_type == 'projectusecaselink':
            required_fields.extend(['project_id', 'use_case_id'])
        
        return all(field in kwargs for field in required_fields)


class AuthFactory(AbstractModelFactory):
    """Factory for creating authentication models."""
    
    def create_model(self, **kwargs) -> BaseModel:
        """Create an authentication model."""
        if not self.validate_creation_params(**kwargs):
            raise ValueError("Invalid creation parameters for authentication model")
        
        # Import here to avoid circular imports
        from .auth import User, CustomRole, RoleAssignment, UserMetrics
        
        model_type = kwargs.get('model_type')
        
        model_map = {
            'user': User,
            'customrole': CustomRole,
            'roleassignment': RoleAssignment,
            'usermetrics': UserMetrics
        }
        
        if model_type not in model_map:
            raise ValueError(f"Unknown authentication model type: {model_type}")
        
        # Remove model_type from kwargs as it's not part of the actual model
        model_kwargs = {k: v for k, v in kwargs.items() if k != 'model_type'}
        
        return model_map[model_type](**model_kwargs)
    
    def validate_creation_params(self, **kwargs) -> bool:
        """Validate creation parameters for authentication models."""
        required_fields = ['model_type']
        
        model_type = kwargs.get('model_type')
        if model_type == 'user':
            required_fields.extend(['user_id', 'username', 'email', 'full_name', 'password_hash', 'role'])
        elif model_type == 'customrole':
            required_fields.extend(['role_id', 'role_name', 'role_type'])
        elif model_type == 'roleassignment':
            required_fields.extend(['assignment_id', 'user_id', 'role_id', 'assignment_type', 'assigned_at'])
        elif model_type == 'usermetrics':
            required_fields.extend(['metric_id', 'user_id', 'metric_type', 'metric_timestamp'])
        
        return all(field in kwargs for field in required_fields)


# ============================================================================
# BUILDER PATTERN IMPLEMENTATIONS
# ============================================================================

class ModelBuilder(Generic[T]):
    """Enhanced builder with fluent interface and validation."""
    
    def __init__(self, model_class: Type[T]):
        self.model_class = model_class
        self._data = {}
        self._validation_context = None
        self._build_hooks: List[Callable] = []
    
    def with_field(self, field_name: str, value: Any) -> 'ModelBuilder[T]':
        """Set a field value."""
        self._data[field_name] = value
        return self
    
    def with_validation_context(self, context: Any) -> 'ModelBuilder[T]':
        """Set validation context."""
        self._validation_context = context
        return self
    
    def with_build_hook(self, hook: Callable) -> 'ModelBuilder[T]':
        """Add a build hook."""
        self._build_hooks.append(hook)
        return self
    
    def with_audit_info(self, user_id: str, **audit_data) -> 'ModelBuilder[T]':
        """Set audit information."""
        from .base_model import AuditInfo
        
        audit_info = AuditInfo(
            created_by=user_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_by=user_id,
            updated_at=datetime.now(timezone.utc).isoformat(),
            **audit_data
        )
        
        self._data['audit_info'] = audit_info
        return self
    
    def with_tags(self, *tags: str) -> 'ModelBuilder[T]':
        """Set tags."""
        self._data['tags'] = list(tags)
        return self
    
    def with_metadata(self, **metadata) -> 'ModelBuilder[T]':
        """Set metadata."""
        self._data['metadata'] = metadata
        return self
    
    def build(self) -> T:
        """Build and return the model instance."""
        # Run build hooks
        for hook in self._build_hooks:
            hook(self._data)
        
        # Create instance
        instance = self.model_class(**self._data)
        
        # Set validation context if provided
        if self._validation_context:
            instance.set_validation_context(self._validation_context)
        
        return instance
    
    def build_and_validate(self) -> T:
        """Build, validate, and return the model instance."""
        instance = self.build()
        
        # Validate business rules
        if hasattr(instance, '_validate_business_rules'):
            instance._validate_business_rules()
        
        return instance


class CoreSystemBuilder(ModelBuilder):
    """Specialized builder for core system models."""
    
    def with_health_monitoring(self, health_score: float = 100.0) -> 'CoreSystemBuilder':
        """Configure health monitoring."""
        self._data['health_score'] = health_score
        self._data['performance_metrics'] = {}
        return self
    
    def with_security_config(self, security_level: str, compliance_standards: List[str] = None) -> 'CoreSystemBuilder':
        """Configure security settings."""
        self._data['security_level'] = security_level
        if compliance_standards:
            self._data['compliance_standards'] = compliance_standards
        return self
    
    def with_performance_thresholds(self, **thresholds) -> 'CoreSystemBuilder':
        """Set performance thresholds."""
        if 'performance_metrics' not in self._data:
            self._data['performance_metrics'] = {}
        self._data['performance_metrics']['thresholds'] = thresholds
        return self


class BusinessDomainBuilder(ModelBuilder):
    """Specialized builder for business domain models."""
    
    def with_business_context(self, org_id: str, project_id: str = None) -> 'BusinessDomainBuilder':
        """Set business context."""
        self._data['org_id'] = org_id
        if project_id:
            self._data['project_id'] = project_id
        return self
    
    def with_classification(self, category: str, priority: str = 'medium') -> 'BusinessDomainBuilder':
        """Set business classification."""
        # Only set fields that exist in the actual model
        if hasattr(self.model_class, 'industry_sector'):
            self._data['industry_sector'] = category
        if hasattr(self.model_class, 'company_size'):
            self._data['company_size'] = priority
        return self
    
    def with_required_timestamps(self) -> 'BusinessDomainBuilder':
        """Set required timestamp fields."""
        from datetime import datetime, timezone
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Check if the model class has these fields by examining model_fields
        if hasattr(self.model_class, 'model_fields'):
            model_fields = self.model_class.model_fields
            if 'created_at' in model_fields:
                self._data['created_at'] = timestamp
            if 'updated_at' in model_fields:
                self._data['updated_at'] = timestamp
        else:
            # Fallback: try to set common timestamp fields
            self._data['created_at'] = timestamp
            self._data['updated_at'] = timestamp
        
        return self


# ============================================================================
# OBSERVER PATTERN IMPLEMENTATIONS
# ============================================================================

class ModelEventBus:
    """Event bus for model events with filtering and routing."""
    
    def __init__(self):
        self._observers: Dict[EventType, List[ModelObserver]] = {}
        self._global_observers: List[ModelObserver] = []
        self._event_history: List[Dict[str, Any]] = []
        self._max_history = 1000
    
    def subscribe(self, event_type: EventType, observer: ModelObserver):
        """Subscribe to specific event type."""
        if event_type not in self._observers:
            self._observers[event_type] = []
        self._observers[event_type].append(observer)
    
    def subscribe_global(self, observer: ModelObserver):
        """Subscribe to all events."""
        self._global_observers.append(observer)
    
    def unsubscribe(self, event_type: EventType, observer: ModelObserver):
        """Unsubscribe from specific event type."""
        if event_type in self._observers:
            self._observers[event_type] = [obs for obs in self._observers[event_type] if obs != observer]
    
    def unsubscribe_global(self, observer: ModelObserver):
        """Unsubscribe from all events."""
        self._global_observers = [obs for obs in self._global_observers if obs != observer]
    
    def publish(self, event_type: EventType, model: BaseModel, **kwargs):
        """Publish an event to all subscribers."""
        event_data = {
            'event_type': event_type,
            'model_type': model.__class__.__name__,
            'model_id': getattr(model, 'id', None),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': kwargs
        }
        
        # Store in history
        self._event_history.append(event_data)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        # Notify specific observers
        if event_type in self._observers:
            for observer in self._observers[event_type]:
                try:
                    observer.on_model_event(model, event_type, **kwargs)
                except Exception as e:
                    print(f"Error in observer {observer}: {e}")
        
        # Notify global observers
        for observer in self._global_observers:
            try:
                observer.on_model_event(model, event_type, **kwargs)
            except Exception as e:
                print(f"Error in global observer {observer}: {e}")
    
    def get_event_history(self, event_type: EventType = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get event history with optional filtering."""
        if event_type:
            filtered_history = [event for event in self._event_history if event['event_type'] == event_type]
        else:
            filtered_history = self._event_history
        
        return filtered_history[-limit:]


class AuditObserver(ModelObserver):
    """Observer for audit and compliance events."""
    
    def __init__(self, audit_logger=None):
        self.audit_logger = audit_logger or self._default_logger
    
    def on_model_event(self, model: BaseModel, event_type: EventType, **kwargs):
        """Handle model events for audit purposes."""
        audit_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_type': event_type.value,
            'model_type': model.__class__.__name__,
            'model_id': getattr(model, 'id', None),
            'user_id': kwargs.get('user_id'),
            'ip_address': kwargs.get('ip_address'),
            'details': kwargs
        }
        
        self.audit_logger(audit_entry)
    
    def _default_logger(self, audit_entry: Dict[str, Any]):
        """Default audit logger."""
        print(f"AUDIT: {audit_entry}")


class MetricsObserver(ModelObserver):
    """Observer for metrics collection."""
    
    def __init__(self, metrics_collector=None):
        self.metrics_collector = metrics_collector or self._default_collector
    
    def on_model_event(self, model: BaseModel, event_type: EventType, **kwargs):
        """Handle model events for metrics collection."""
        metric = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_type': event_type.value,
            'model_type': model.__class__.__name__,
            'model_id': getattr(model, 'id', None),
            'event_data': kwargs
        }
        
        self.metrics_collector(metric)
    
    def _default_collector(self, metric: Dict[str, Any]):
        """Default metrics collector."""
        print(f"METRIC: {metric}")


# ============================================================================
# STRATEGY PATTERN IMPLEMENTATIONS
# ============================================================================

class ValidationStrategy(ABC):
    """Abstract validation strategy."""
    
    @abstractmethod
    def validate(self, model: BaseModel) -> bool:
        """Validate a model."""
        pass
    
    @abstractmethod
    def get_validation_errors(self) -> List[str]:
        """Get validation errors."""
        pass


class StrictValidationStrategy(ValidationStrategy):
    """Strict validation strategy."""
    
    def __init__(self):
        self.errors = []
    
    def validate(self, model: BaseModel) -> bool:
        """Perform strict validation."""
        self.errors = []
        
        # Validate all required fields
        for field_name, field_info in model.model_fields.items():
            if field_info.is_required():
                value = getattr(model, field_name, None)
                if value is None:
                    self.errors.append(f"Required field '{field_name}' is missing")
        
        # Validate business rules
        if hasattr(model, '_validate_business_rules'):
            try:
                model._validate_business_rules()
            except Exception as e:
                self.errors.append(f"Business rule validation failed: {e}")
        
        return len(self.errors) == 0
    
    def get_validation_errors(self) -> List[str]:
        """Get validation errors."""
        return self.errors.copy()


class RelaxedValidationStrategy(ValidationStrategy):
    """Relaxed validation strategy."""
    
    def __init__(self):
        self.errors = []
    
    def validate(self, model: BaseModel) -> bool:
        """Perform relaxed validation."""
        self.errors = []
        
        # Only validate critical fields
        critical_fields = ['id', 'name', 'created_at']
        for field_name in critical_fields:
            if hasattr(model, field_name):
                value = getattr(model, field_name, None)
                if value is None:
                    self.errors.append(f"Critical field '{field_name}' is missing")
        
        return len(self.errors) == 0
    
    def get_validation_errors(self) -> List[str]:
        """Get validation errors."""
        return self.errors.copy()


class ValidationContext:
    """Context for validation strategies."""
    
    def __init__(self, strategy: ValidationStrategy):
        self.strategy = strategy
    
    def validate(self, model: BaseModel) -> bool:
        """Validate using the current strategy."""
        return self.strategy.validate(model)
    
    def get_errors(self) -> List[str]:
        """Get validation errors from the current strategy."""
        return self.strategy.get_validation_errors()


# ============================================================================
# COMMAND PATTERN IMPLEMENTATIONS
# ============================================================================

class ModelCommand(ABC):
    """Abstract command for model operations."""
    
    @abstractmethod
    def execute(self) -> bool:
        """Execute the command."""
        pass
    
    @abstractmethod
    def undo(self) -> bool:
        """Undo the command."""
        pass


class CreateModelCommand(ModelCommand):
    """Command for creating models."""
    
    def __init__(self, factory: AbstractModelFactory, **kwargs):
        self.factory = factory
        self.kwargs = kwargs
        self.created_model = None
    
    def execute(self) -> bool:
        """Execute the create command."""
        try:
            self.created_model = self.factory.create_model(**self.kwargs)
            return True
        except Exception as e:
            print(f"Create command failed: {e}")
            return False
    
    def undo(self) -> bool:
        """Undo the create command."""
        # In a real implementation, this would delete the created model
        self.created_model = None
        return True


class UpdateModelCommand(ModelCommand):
    """Command for updating models."""
    
    def __init__(self, model: BaseModel, **updates):
        self.model = model
        self.updates = updates
        self.previous_state = None
    
    def execute(self) -> bool:
        """Execute the update command."""
        try:
            # Store previous state
            self.previous_state = self.model.to_dict()
            
            # Apply updates
            for field, value in self.updates.items():
                if hasattr(self.model, field):
                    setattr(self.model, field, value)
            
            # Update audit info
            if hasattr(self.model, 'update_audit_info'):
                self.model.update_audit_info(
                    user_id=self.updates.get('user_id', 'system'),
                    change_reason=self.updates.get('change_reason', 'Update command')
                )
            
            return True
        except Exception as e:
            print(f"Update command failed: {e}")
            return False
    
    def undo(self) -> bool:
        """Undo the update command."""
        if self.previous_state:
            try:
                for field, value in self.previous_state.items():
                    if hasattr(self.model, field):
                        setattr(self.model, field, value)
                return True
            except Exception as e:
                print(f"Undo update command failed: {e}")
                return False
        return False


class CommandInvoker:
    """Invoker for executing commands."""
    
    def __init__(self):
        self.command_history: List[ModelCommand] = []
        self.max_history = 100
    
    def execute_command(self, command: ModelCommand) -> bool:
        """Execute a command."""
        if command.execute():
            self.command_history.append(command)
            
            # Limit history size
            if len(self.command_history) > self.max_history:
                self.command_history.pop(0)
            
            return True
        return False
    
    def undo_last_command(self) -> bool:
        """Undo the last command."""
        if self.command_history:
            last_command = self.command_history.pop()
            return last_command.undo()
        return False
    
    def get_command_history(self) -> List[ModelCommand]:
        """Get command history."""
        return self.command_history.copy()


# ============================================================================
# SINGLETON PATTERN IMPLEMENTATIONS
# ============================================================================

class ModelRegistry:
    """Singleton registry for managing all models."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.factories = ModelFactoryRegistry()
            self.event_bus = ModelEventBus()
            self.command_invoker = CommandInvoker()
            self._initialized = True
    
    def get_factory_registry(self) -> ModelFactoryRegistry:
        """Get the factory registry."""
        return self.factories
    
    def get_event_bus(self) -> ModelEventBus:
        """Get the event bus."""
        return self.event_bus
    
    def get_command_invoker(self) -> CommandInvoker:
        """Get the command invoker."""
        return self.command_invoker


# ============================================================================
# EXPORT ALL PATTERNS
# ============================================================================

__all__ = [
    # Factory Pattern
    'ModelFactoryRegistry', 'AbstractModelFactory', 'CoreSystemFactory', 
    'BusinessDomainFactory', 'AuthFactory',
    
    # Builder Pattern
    'ModelBuilder', 'CoreSystemBuilder', 'BusinessDomainBuilder',
    
    # Observer Pattern
    'ModelEventBus', 'AuditObserver', 'MetricsObserver',
    
    # Strategy Pattern
    'ValidationStrategy', 'StrictValidationStrategy', 'RelaxedValidationStrategy', 'ValidationContext',
    
    # Command Pattern
    'ModelCommand', 'CreateModelCommand', 'UpdateModelCommand', 'CommandInvoker',
    
    # Singleton Pattern
    'ModelRegistry'
]
