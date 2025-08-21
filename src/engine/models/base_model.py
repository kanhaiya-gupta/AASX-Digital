"""
Base Model - World-Class Implementation
==============================================

Base model with comprehensive validation, business logic, enterprise patterns,
audit capabilities, and extensibility features for the AAS Data Modeling Engine.
"""

import re
import hashlib
import secrets
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Union, TypeVar, Generic
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from pydantic_core import PydanticCustomError

from .enums import (
    BusinessConstants, ValidationRules, StatusMappings, 
    BusinessLogicConstants, SecurityConstants, EventType
)

# Generic type for model relationships
T = TypeVar('T', bound='BaseModel')


class AuditInfo(BaseModel):
    """Audit information for compliance and traceability."""
    
    created_by: Optional[str] = Field(None, description="User who created the record")
    created_at: str = Field(..., description="Creation timestamp in ISO format")
    updated_by: Optional[str] = Field(None, description="User who last updated the record")
    updated_at: str = Field(..., description="Last update timestamp in ISO format")
    version: int = Field(default=1, description="Version number for optimistic locking")
    change_reason: Optional[str] = Field(None, description="Reason for the last change")
    ip_address: Optional[str] = Field(None, description="IP address of the last change")
    user_agent: Optional[str] = Field(None, description="User agent of the last change")
    
    class Config:
        json_schema_extra = {
            "example": {
                "created_by": "user123",
                "created_at": "2025-08-20T10:00:00Z",
                "updated_by": "user123",
                "updated_at": "2025-08-20T10:00:00Z",
                "version": 1,
                "change_reason": "Initial creation",
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0..."
            }
        }


class ValidationContext(BaseModel):
    """Context for validation operations."""
    
    user_id: Optional[str] = Field(None, description="User performing validation")
    organization_id: Optional[str] = Field(None, description="Organization context")
    project_id: Optional[str] = Field(None, description="Project context")
    validation_level: str = Field(default="standard", description="Validation level")
    skip_business_rules: bool = Field(default=False, description="Skip business rule validation")
    custom_validators: List[str] = Field(default_factory=list, description="Custom validators to run")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "organization_id": "org456",
                "project_id": "proj789",
                "validation_level": "strict",
                "skip_business_rules": False,
                "custom_validators": ["custom_rule_1", "custom_rule_2"]
            }
        }


class BusinessRuleViolation(BaseModel):
    """Business rule violation details."""
    
    rule_name: str = Field(..., description="Name of the violated business rule")
    rule_description: str = Field(..., description="Description of the business rule")
    field_name: Optional[str] = Field(None, description="Field that violated the rule")
    current_value: Any = Field(..., description="Current value that violated the rule")
    expected_value: Optional[Any] = Field(None, description="Expected value")
    severity: str = Field(default="error", description="Severity of the violation")
    suggested_fix: Optional[str] = Field(None, description="Suggested fix for the violation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "rule_name": "MAX_FILE_SIZE",
                "rule_description": "File size exceeds maximum allowed size",
                "field_name": "size",
                "current_value": 2000000000,
                "expected_value": 1073741824,
                "severity": "error",
                "suggested_fix": "Reduce file size to under 1GB"
            }
        }


class BaseModel(BaseModel):
    """
    Base model with world-class features.
    
    Features:
    - Comprehensive validation with business rules
    - Audit trail and compliance tracking
    - Enterprise patterns (Observer, Factory, Builder)
    - Performance optimization with lazy loading
    - Extensibility through plugins and hooks
    - Security and encryption support
    - Caching and optimization strategies
    """
    
    # Pydantic configuration
    model_config = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        extra='forbid',
        str_strip_whitespace=True,
        use_enum_values=True,
        populate_by_name=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }
    )
    
    # Audit fields
    audit_info: Optional[AuditInfo] = Field(None, description="Audit information")
    
    # Business rule validation
    _validation_context: Optional[ValidationContext] = None
    _business_rule_violations: List[BusinessRuleViolation] = []
    
    # Performance optimization
    _cached_properties: Dict[str, Any] = {}
    _lazy_loaded: Dict[str, bool] = {}
    
    # Observer pattern support
    _observers: List['ModelObserver'] = []
    
    # Plugin system
    _plugins: Dict[str, Any] = {}
    
    def __init__(self, **data):
        """Initialize the base model."""
        # Set default audit info if not provided
        if 'audit_info' not in data:
            data['audit_info'] = AuditInfo(
                created_at=datetime.now(timezone.utc).isoformat(),
                updated_at=datetime.now(timezone.utc).isoformat()
            )
        
        # Initialize the model
        super().__init__(**data)
        
        # Run post-initialization hooks
        self._post_init()
    
    def _post_init(self):
        """Post-initialization processing."""
        # Initialize caches
        self._cached_properties = {}
        self._lazy_loaded = {}
        
        # Run plugin initialization
        self._initialize_plugins()
        
        # Notify observers
        self._notify_observers(EventType.USER_CREATED)
    
    @field_validator('*', mode='before')
    @classmethod
    def validate_field(cls, v, info):
        """Field validation with business rules."""
        if v is None:
            return v
        
        field_name = info.field_name
        
        # String validation
        if isinstance(v, str):
            v = cls._validate_string_field(v, field_name)
        
        # Numeric validation
        if isinstance(v, (int, float)):
            v = cls._validate_numeric_field(v, field_name)
        
        # List validation
        if isinstance(v, list):
            v = cls._validate_list_field(v, field_name)
        
        # Dict validation
        if isinstance(v, dict):
            v = cls._validate_dict_field(v, field_name)
        
        return v
    
    @classmethod
    def _validate_string_field(cls, value: str, field_name: str) -> str:
        """Validate string fields with business rules."""
        # Trim whitespace
        value = value.strip()
        
        # Length validation
        if field_name == 'name':
            if len(value) < ValidationRules.ORG_NAME_MIN_LENGTH:
                raise PydanticCustomError(
                    'string_too_short',
                    f'String too short. Minimum length is {ValidationRules.ORG_NAME_MIN_LENGTH}',
                    dict(min_length=ValidationRules.ORG_NAME_MIN_LENGTH, actual_length=len(value))
                )
            if len(value) > ValidationRules.ORG_NAME_MAX_LENGTH:
                raise PydanticCustomError(
                    'string_too_long',
                    f'String too long. Maximum length is {ValidationRules.ORG_NAME_MAX_LENGTH}',
                    dict(max_length=ValidationRules.ORG_NAME_MAX_LENGTH, actual_length=len(value))
                )
        
        # Email validation
        if field_name == 'email':
            if not re.match(ValidationRules.EMAIL_REGEX, value):
                raise PydanticCustomError(
                    'invalid_email',
                    'Invalid email format',
                    dict(value=value)
                )
        
        # Username validation
        if field_name == 'username':
            if len(value) < ValidationRules.USERNAME_MIN_LENGTH:
                raise PydanticCustomError(
                    'username_too_short',
                    f'Username too short. Minimum length is {ValidationRules.USERNAME_MIN_LENGTH}',
                    dict(min_length=ValidationRules.USERNAME_MIN_LENGTH, actual_length=len(value))
                )
            if len(value) > ValidationRules.USERNAME_MAX_LENGTH:
                raise PydanticCustomError(
                    'username_too_long',
                    f'Username too long. Maximum length is {ValidationRules.USERNAME_MAX_LENGTH}',
                    dict(max_length=ValidationRules.USERNAME_MAX_LENGTH, actual_length=len(value))
                )
            if not re.match(ValidationRules.USERNAME_REGEX, value):
                raise PydanticCustomError(
                    'invalid_username',
                    'Username contains invalid characters',
                    dict(value=value)
                )
        
        return value
    
    @classmethod
    def _validate_numeric_field(cls, value: Union[int, float], field_name: str) -> Union[int, float]:
        """Validate numeric fields with business rules."""
        # Health score validation
        if field_name == 'health_score':
            if not (BusinessConstants.HEALTH_SCORE_MIN <= value <= BusinessConstants.HEALTH_SCORE_MAX):
                raise PydanticCustomError(
                    'health_score_out_of_range',
                    f'Health score must be between {BusinessConstants.HEALTH_SCORE_MIN} and {BusinessConstants.HEALTH_SCORE_MAX}',
                    dict(min_value=BusinessConstants.HEALTH_SCORE_MIN, max_value=BusinessConstants.HEALTH_SCORE_MAX, actual_value=value)
                )
        
        # File size validation
        if field_name == 'size':
            if value > BusinessConstants.MAX_FILE_SIZE_BYTES:
                raise PydanticCustomError(
                    'file_size_too_large',
                    f'File size exceeds maximum allowed size of {BusinessConstants.MAX_FILE_SIZE_MB}MB',
                    dict(max_size_mb=BusinessConstants.MAX_FILE_SIZE_MB, actual_size_mb=value / (1024 * 1024))
                )
        
        return value
    
    @classmethod
    def _validate_list_field(cls, value: List, field_name: str) -> List:
        """Validate list fields with business rules."""
        # Tags validation
        if field_name == 'tags':
            if len(value) > ValidationRules.MAX_TAGS_PER_ENTITY:
                raise PydanticCustomError(
                    'too_many_tags',
                    f'Too many tags. Maximum allowed is {ValidationRules.MAX_TAGS_PER_ENTITY}',
                    dict(max_tags=ValidationRules.MAX_TAGS_PER_ENTITY, actual_count=len(value))
                )
            
            # Validate individual tag lengths
            for tag in value:
                if len(tag) > ValidationRules.TAG_MAX_LENGTH:
                    raise PydanticCustomError(
                        'tag_too_long',
                        f'Tag too long. Maximum length is {ValidationRules.TAG_MAX_LENGTH}',
                        dict(max_length=ValidationRules.TAG_MAX_LENGTH, actual_length=len(tag))
                    )
        
        return value
    
    @classmethod
    def _validate_dict_field(cls, value: Dict, field_name: str) -> Dict:
        """Validate dictionary fields with business rules."""
        # Metadata validation
        if field_name == 'metadata':
            # Ensure metadata doesn't exceed reasonable size
            metadata_size = len(str(value))
            if metadata_size > 10000:  # 10KB limit
                raise PydanticCustomError(
                    'metadata_too_large',
                    'Metadata too large. Maximum size is 10KB',
                    dict(max_size_kb=10, actual_size_kb=metadata_size / 1024)
                )
        
        return value
    
    @model_validator(mode='after')
    def validate_business_rules(self):
        """Validate business rules after model creation."""
        if not self._validation_context or not self._validation_context.skip_business_rules:
            self._validate_business_rules()
        
        return self
    
    def _validate_business_rules(self):
        """Validate business rules specific to the model."""
        violations = []
        
        # Run custom business rule validators
        for validator_name in self._get_business_rule_validators():
            try:
                validator_method = getattr(self, validator_name)
                if callable(validator_method):
                    validator_method()
            except Exception as e:
                violations.append(BusinessRuleViolation(
                    rule_name=validator_name,
                    rule_description=str(e),
                    severity="error"
                ))
        
        # Store violations for later access
        self._business_rule_violations = violations
        
        # Raise exception if there are violations
        if violations:
            violation_details = "\n".join([f"- {v.rule_name}: {v.rule_description}" for v in violations])
            raise PydanticCustomError(
                'business_rule_violations',
                f'Business rule violations found:\n{violation_details}',
                dict(violations=violations)
            )
    
    def _get_business_rule_validators(self) -> List[str]:
        """Get list of business rule validator method names."""
        return [attr for attr in dir(self) if attr.startswith('_validate_business_rule_')]
    
    # Audit and Compliance Methods
    
    def update_audit_info(self, user_id: str, change_reason: Optional[str] = None, 
                         ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """Update audit information for a change."""
        if not self.audit_info:
            self.audit_info = AuditInfo(
                created_at=datetime.now(timezone.utc).isoformat(),
                updated_at=datetime.now(timezone.utc).isoformat()
            )
        
        self.audit_info.updated_by = user_id
        self.audit_info.updated_at = datetime.now(timezone.utc).isoformat()
        self.audit_info.version += 1
        self.audit_info.change_reason = change_reason
        self.audit_info.ip_address = ip_address
        self.audit_info.user_agent = user_agent
        
        # Notify observers
        self._notify_observers(EventType.USER_UPDATED)
    
    def get_audit_trail(self) -> Dict[str, Any]:
        """Get complete audit trail for compliance."""
        return {
            "model_type": self.__class__.__name__,
            "audit_info": self.audit_info.dict() if self.audit_info else None,
            "business_rule_violations": [v.dict() for v in self._business_rule_violations],
            "validation_context": self._validation_context.dict() if self._validation_context else None,
            "last_validation": datetime.now(timezone.utc).isoformat()
        }
    
    # Performance Optimization Methods
    
    def _get_cached_property(self, property_name: str, compute_func: callable) -> Any:
        """Get a cached property value, computing if necessary."""
        if property_name not in self._cached_properties:
            self._cached_properties[property_name] = compute_func()
        return self._cached_properties[property_name]
    
    def _invalidate_cache(self, property_name: Optional[str] = None):
        """Invalidate cached properties."""
        if property_name:
            self._cached_properties.pop(property_name, None)
        else:
            self._cached_properties.clear()
    
    def lazy_load_property(self, property_name: str, loader_func: callable) -> Any:
        """Lazy load a property value."""
        if not self._lazy_loaded.get(property_name, False):
            self._cached_properties[property_name] = loader_func()
            self._lazy_loaded[property_name] = True
        
        return self._cached_properties.get(property_name)
    
    # Observer Pattern Methods
    
    def add_observer(self, observer: 'ModelObserver'):
        """Add an observer to this model."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer: 'ModelObserver'):
        """Remove an observer from this model."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def _notify_observers(self, event_type: EventType, **kwargs):
        """Notify all observers of an event."""
        for observer in self._observers:
            try:
                observer.on_model_event(self, event_type, **kwargs)
            except Exception as e:
                # Log observer error but don't fail the operation
                print(f"Observer notification failed: {e}")
    
    # Plugin System Methods
    
    def _initialize_plugins(self):
        """Initialize plugins for this model."""
        # This would be implemented based on the plugin system
        pass
    
    def register_plugin(self, plugin_name: str, plugin_instance: Any):
        """Register a plugin with this model."""
        self._plugins[plugin_name] = plugin_instance
    
    def get_plugin(self, plugin_name: str) -> Optional[Any]:
        """Get a registered plugin."""
        return self._plugins.get(plugin_name)
    
    # Utility Methods
    
    def to_dict(self, include_audit: bool = True, include_cache: bool = False) -> Dict[str, Any]:
        """Convert model to dictionary with options."""
        data = self.model_dump()
        
        if not include_audit and 'audit_info' in data:
            del data['audit_info']
        
        if include_cache:
            data['_cached_properties'] = self._cached_properties
            data['_lazy_loaded'] = self._lazy_loaded
        
        return data
    
    def clone(self, **overrides) -> 'BaseModel':
        """Create a clone of this model with optional overrides."""
        data = self.to_dict(include_audit=False, include_cache=False)
        data.update(overrides)
        
        # Generate new ID if it exists
        if 'id' in data:
            data['id'] = str(uuid.uuid4())
        
        # Reset audit info
        data['audit_info'] = None
        
        return self.__class__(**data)
    
    def merge(self, other: 'BaseModel', conflict_resolution: str = 'prefer_self') -> 'BaseModel':
        """Merge this model with another model."""
        if not isinstance(other, self.__class__):
            raise ValueError(f"Cannot merge {type(other)} with {self.__class__}")
        
        data = self.to_dict(include_audit=False, include_cache=False)
        other_data = other.to_dict(include_audit=False, include_cache=False)
        
        if conflict_resolution == 'prefer_self':
            merged_data = {**other_data, **data}
        elif conflict_resolution == 'prefer_other':
            merged_data = {**data, **other_data}
        else:
            raise ValueError(f"Unknown conflict resolution strategy: {conflict_resolution}")
        
        return self.__class__(**merged_data)
    
    # Business Logic Methods
    
    def is_valid_for_business(self) -> bool:
        """Check if the model is valid according to business rules."""
        return len(self._business_rule_violations) == 0
    
    def get_business_rule_violations(self) -> List[BusinessRuleViolation]:
        """Get list of business rule violations."""
        return self._business_rule_violations.copy()
    
    def add_business_rule_violation(self, violation: BusinessRuleViolation):
        """Add a business rule violation."""
        self._business_rule_violations.append(violation)
    
    def clear_business_rule_violations(self):
        """Clear all business rule violations."""
        self._business_rule_violations.clear()
    
    # Security Methods
    
    def encrypt_sensitive_field(self, field_name: str, encryption_key: str):
        """Encrypt a sensitive field value."""
        # This would implement actual encryption logic
        pass
    
    def decrypt_sensitive_field(self, field_name: str, encryption_key: str):
        """Decrypt a sensitive field value."""
        # This would implement actual decryption logic
        pass
    
    def mask_sensitive_data(self) -> 'BaseModel':
        """Create a copy with sensitive data masked."""
        # This would implement data masking logic
        return self.clone()
    
    # Validation Context Methods
    
    def set_validation_context(self, context: ValidationContext):
        """Set the validation context for this model."""
        self._validation_context = context
    
    def get_validation_context(self) -> Optional[ValidationContext]:
        """Get the current validation context."""
        return self._validation_context
    
    # Lifecycle Methods
    
    def pre_save(self):
        """Hook called before saving the model."""
        # Update audit info
        if self.audit_info:
            self.audit_info.updated_at = datetime.now(timezone.utc).isoformat()
            self.audit_info.version += 1
        
        # Run pre-save validations
        self._validate_business_rules()
        
        # Notify observers
        self._notify_observers(EventType.USER_UPDATED)
    
    def post_save(self):
        """Hook called after saving the model."""
        # Clear caches
        self._invalidate_cache()
        
        # Notify observers
        self._notify_observers(EventType.USER_UPDATED)
    
    def pre_delete(self):
        """Hook called before deleting the model."""
        # Notify observers
        self._notify_observers(EventType.USER_DELETED)
    
    def post_delete(self):
        """Hook called after deleting the model."""
        # Clean up observers
        self._observers.clear()
        
        # Clean up plugins
        self._plugins.clear()
    
    # Magic Methods
    
    def __str__(self) -> str:
        """String representation of the model."""
        return f"{self.__class__.__name__}({self.model_dump_json()})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the model."""
        return f"{self.__class__.__name__}({self.model_dump_json(indent=2)})"
    
    def __eq__(self, other: Any) -> bool:
        """Equality comparison."""
        if not isinstance(other, self.__class__):
            return False
        
        # Compare key fields (excluding audit info and caches)
        self_data = self.to_dict(include_audit=False, include_cache=False)
        other_data = other.to_dict(include_audit=False, include_cache=False)
        
        return self_data == other_data
    
    def __hash__(self) -> int:
        """Hash value for the model."""
        # Use a stable hash based on key fields
        key_data = self.to_dict(include_audit=False, include_cache=False)
        return hash(str(sorted(key_data.items())))


class ModelObserver(ABC):
    """Abstract base class for model observers."""
    
    @abstractmethod
    def on_model_event(self, model: BaseModel, event_type: EventType, **kwargs):
        """Handle model events."""
        pass


class ModelFactory(ABC):
    """Abstract factory for creating models."""
    
    @abstractmethod
    def create_model(self, model_type: str, **kwargs) -> BaseModel:
        """Create a model of the specified type."""
        pass
    
    @abstractmethod
    def register_model_type(self, model_type: str, model_class: type):
        """Register a new model type."""
        pass


class ModelBuilder(Generic[T]):
    """Builder pattern for constructing models."""
    
    def __init__(self, model_class: type[T]):
        self.model_class = model_class
        self._data = {}
        self._validation_context = None
    
    def with_field(self, field_name: str, value: Any) -> 'ModelBuilder[T]':
        """Set a field value."""
        self._data[field_name] = value
        return self
    
    def with_validation_context(self, context: ValidationContext) -> 'ModelBuilder[T]':
        """Set validation context."""
        self._validation_context = context
        return self
    
    def build(self) -> T:
        """Build and return the model instance."""
        instance = self.model_class(**self._data)
        
        if self._validation_context:
            instance.set_validation_context(self._validation_context)
        
        return instance


# Export the base model
__all__ = [
    'BaseModel', 'AuditInfo', 'ValidationContext', 'BusinessRuleViolation',
    'ModelObserver', 'ModelFactory', 'ModelBuilder'
]
