"""
AAS Data Modeling Engine - World-Class Models Package
====================================================

Comprehensive, enterprise-grade models with:
- Enhanced Pydantic models with business logic
- Comprehensive enums and constants
- Enterprise patterns (Factory, Builder, Observer, Strategy, Command)
- Audit trail and compliance tracking
- Performance optimization and caching
- Security and encryption support
- Plugin architecture and extensibility
"""

# Core Models
from .base_model import (
    BaseModel, AuditInfo, ValidationContext, BusinessRuleViolation,
    ModelObserver, ModelFactory, ModelBuilder
)

from .core_system import (
    CoreSystemRegistry, CoreSystemMetrics
)

from .business_domain import (
    Organization, UseCase, Project, File, ProjectUseCaseLink
)

from .auth import (
    User, CustomRole, RoleAssignment, UserMetrics
)

from .data_governance import (
    DataLineage, DataQualityMetrics, ChangeRequest, DataVersion, GovernancePolicy
)

# Enums and Constants
from .enums import (
    # System Enums
    SystemCategory, SystemType, SystemPriority, RegistryType, WorkflowSource,
    SecurityLevel, HealthStatus,
    
    # Business Enums
    CompanySize, SubscriptionTier, DataDomain, BusinessCriticality,
    ProjectPhase, PriorityLevel, FileStatus, SourceType,
    
    # User and Role Enums
    UserRole, RoleType, AssignmentType, MetricType,
    
    # Event Types
    EventType,
    
    # Business Constants
    BusinessConstants, ValidationRules, StatusMappings, BusinessLogicConstants,
    CacheConfig, PerformanceConstants, SecurityConstants, PluginConstants
)

# Enterprise Patterns
from .enterprise_patterns import (
    # Factory Pattern
    ModelFactoryRegistry, AbstractModelFactory, CoreSystemFactory, 
    BusinessDomainFactory, AuthFactory,
    
    # Builder Pattern
    ModelBuilder, CoreSystemBuilder, BusinessDomainBuilder,
    
    # Observer Pattern
    ModelEventBus, AuditObserver, MetricsObserver,
    
    # Strategy Pattern
    ValidationStrategy, StrictValidationStrategy, RelaxedValidationStrategy, ValidationContext,
    
    # Command Pattern
    ModelCommand, CreateModelCommand, UpdateModelCommand, CommandInvoker,
    
    # Singleton Pattern
    ModelRegistry
)

# Version and metadata
__version__ = "2.0.0"
__author__ = "AAS Data Modeling Engine Team"
__description__ = "World-Class Models for AAS Data Modeling Engine"

# Export all public components
__all__ = [
    # Core Models
    'BaseModel', 'AuditInfo', 'ValidationContext', 'BusinessRuleViolation',
    'ModelObserver', 'ModelFactory', 'ModelBuilder',
    
    # Domain Models
    'CoreSystemRegistry', 'CoreSystemMetrics',
    'Organization', 'UseCase', 'Project', 'File', 'ProjectUseCaseLink',
    'User', 'CustomRole', 'RoleAssignment', 'UserMetrics',
    'DataLineage', 'DataQualityMetrics', 'ChangeRequest', 'DataVersion', 'GovernancePolicy',
    
    # Enums and Constants
    'SystemCategory', 'SystemType', 'SystemPriority', 'RegistryType', 'WorkflowSource',
    'SecurityLevel', 'HealthStatus', 'CompanySize', 'SubscriptionTier', 'DataDomain',
    'BusinessCriticality', 'ProjectPhase', 'PriorityLevel', 'FileStatus', 'SourceType',
    'UserRole', 'RoleType', 'AssignmentType', 'MetricType', 'EventType',
    'BusinessConstants', 'ValidationRules', 'StatusMappings', 'BusinessLogicConstants',
    'CacheConfig', 'PerformanceConstants', 'SecurityConstants', 'PluginConstants',
    
    # Enterprise Patterns
    'ModelFactoryRegistry', 'AbstractModelFactory', 'CoreSystemFactory', 
    'BusinessDomainFactory', 'AuthFactory', 'ModelBuilder', 'CoreSystemBuilder',
    'BusinessDomainBuilder', 'ModelEventBus', 'AuditObserver', 'MetricsObserver',
    'ValidationStrategy', 'StrictValidationStrategy', 'RelaxedValidationStrategy', 'ValidationContext',
    'ModelCommand', 'CreateModelCommand', 'UpdateModelCommand', 'CommandInvoker', 'ModelRegistry'
]

# Convenience imports for common use cases
def get_model_factory() -> ModelRegistry:
    """Get the global model registry instance."""
    return ModelRegistry()

def get_validation_context(strategy: str = "strict") -> ValidationContext:
    """Get a validation context with the specified strategy."""
    if strategy == "strict":
        return ValidationContext(StrictValidationStrategy())
    elif strategy == "relaxed":
        return ValidationContext(RelaxedValidationStrategy())
    else:
        raise ValueError(f"Unknown validation strategy: {strategy}")

def get_event_bus() -> ModelEventBus:
    """Get the global event bus instance."""
    return ModelRegistry().get_event_bus()

def get_command_invoker() -> CommandInvoker:
    """Get the global command invoker instance."""
    return ModelRegistry().get_command_invoker()

# Initialize the global registry
_model_registry = ModelRegistry()

# Register default factories
_model_registry.get_factory_registry().register_factory('core_system', CoreSystemFactory())
_model_registry.get_factory_registry().register_factory('business_domain', BusinessDomainFactory())
_model_registry.get_factory_registry().register_factory('auth', AuthFactory())

# Register default observers
_event_bus = _model_registry.get_event_bus()
_event_bus.subscribe_global(AuditObserver())
_event_bus.subscribe_global(MetricsObserver())

print("🚀 AAS Data Modeling Engine - World-Class Models Package Initialized")
print(f"📦 Version: {__version__}")
print(f"🏭 Registered Factories: {_model_registry.get_factory_registry().list_registered_types()}")
print(f"👁️  Global Observers: {len(_event_bus._global_observers)}")
print("✨ Ready for enterprise-grade operations!")
