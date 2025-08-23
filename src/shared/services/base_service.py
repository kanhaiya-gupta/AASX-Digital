"""
Base Service
===========

Base class for all services in the AAS Data Modeling framework.
Provides common business logic patterns, error handling, and validation.
"""

from typing import TypeVar, Generic, List, Optional, Dict, Any
from abc import ABC, abstractmethod
import logging
from ..database.base_manager import BaseDatabaseManager
from ..models.base_model import BaseModel

T = TypeVar('T', bound=BaseModel)

class BaseService(Generic[T], ABC):
    """Base service class providing common business logic patterns."""
    
    def __init__(self, db_manager: BaseDatabaseManager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def get_repository(self):
        """Get the repository for this service."""
        pass
    
    def create(self, data: Dict[str, Any]) -> T:
        """Create a new entity with business logic validation."""
        try:
            # Validate business rules
            self._validate_create(data)
            
            # Create the model object from data
            model_class = self.get_repository().model_class
            entity = model_class.from_dict(data)
            
            # Validate the entity
            entity.validate()
            
            # Create the entity in repository
            created_entity = self.get_repository().create(entity)
            
            # Post-creation business logic
            self._post_create(created_entity)
            
            self.logger.info(f"Created {self.__class__.__name__} with ID: {created_entity.id}")
            return created_entity
            
        except Exception as e:
            self.logger.error(f"Error creating {self.__class__.__name__}: {str(e)}")
            raise
    
    def get_by_id(self, entity_id: str) -> Optional[T]:
        """Get entity by ID with business logic."""
        try:
            entity = self.get_repository().get_by_id(entity_id)
            if entity:
                self._post_get(entity)
            return entity
            
        except Exception as e:
            self.logger.error(f"Error getting {self.__class__.__name__} by ID {entity_id}: {str(e)}")
            raise
    
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """Get all entities with optional filtering."""
        try:
            entities = self.get_repository().get_all()
            
            # Apply business logic filters
            if filters:
                entities = self._apply_business_filters(entities, filters)
            
            # Post-processing for each entity
            for entity in entities:
                self._post_get(entity)
            
            return entities
            
        except Exception as e:
            self.logger.error(f"Error getting all {self.__class__.__name__}: {str(e)}")
            raise
    
    def update(self, entity_id: str, data: Dict[str, Any]) -> Optional[T]:
        """Update entity with business logic validation."""
        try:
            # Validate business rules
            self._validate_update(entity_id, data)
            
            # Update the entity
            entity = self.get_repository().update(entity_id, data)
            
            if entity:
                # Post-update business logic
                self._post_update(entity)
                self.logger.info(f"Updated {self.__class__.__name__} with ID: {entity_id}")
            
            return entity
            
        except Exception as e:
            self.logger.error(f"Error updating {self.__class__.__name__} {entity_id}: {str(e)}")
            raise
    
    def delete(self, entity_id: str) -> bool:
        """Delete entity with business logic validation."""
        try:
            # Validate business rules
            self._validate_delete(entity_id)
            
            # Perform deletion
            success = self.get_repository().delete(entity_id)
            
            if success:
                # Post-deletion business logic
                self._post_delete(entity_id)
                self.logger.info(f"Deleted {self.__class__.__name__} with ID: {entity_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error deleting {self.__class__.__name__} {entity_id}: {str(e)}")
            raise
    
    def exists(self, entity_id: str) -> bool:
        """Check if entity exists."""
        return self.get_repository().exists(entity_id)
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities with optional filtering."""
        entities = self.get_all(filters)
        return len(entities)
    
    # Business Logic Hooks (to be overridden by subclasses)
    
    def _validate_create(self, data: Dict[str, Any]) -> None:
        """Validate business rules for creation."""
        pass
    
    def _validate_update(self, entity_id: str, data: Dict[str, Any]) -> None:
        """Validate business rules for updates."""
        pass
    
    def _validate_delete(self, entity_id: str) -> None:
        """Validate business rules for deletion."""
        pass
    
    def _post_create(self, entity: T) -> None:
        """Post-creation business logic."""
        pass
    
    def _post_get(self, entity: T) -> None:
        """Post-retrieval business logic."""
        pass
    
    def _post_update(self, entity: T) -> None:
        """Post-update business logic."""
        pass
    
    def _post_delete(self, entity_id: str) -> None:
        """Post-deletion business logic."""
        pass
    
    def _apply_business_filters(self, entities: List[T], filters: Dict[str, Any]) -> List[T]:
        """Apply business logic filters to entities."""
        return entities
    
    # Utility Methods
    
    def _log_business_rule_violation(self, rule: str, details: str) -> None:
        """Log business rule violations."""
        self.logger.warning(f"Business rule violation - {rule}: {details}")
    
    def _raise_business_error(self, message: str) -> None:
        """Raise a business logic error."""
        raise ValueError(f"Business Logic Error: {message}")
    
    def _validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> None:
        """Validate that required fields are present."""
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            self._raise_business_error(f"Missing required fields: {', '.join(missing_fields)}")
    
    def _validate_field_length(self, data: Dict[str, Any], field: str, max_length: int) -> None:
        """Validate field length."""
        value = data.get(field)
        if value and len(str(value)) > max_length:
            self._raise_business_error(f"Field '{field}' exceeds maximum length of {max_length}")
    
    def _validate_unique_constraint(self, data: Dict[str, Any], field: str, exclude_id: Optional[str] = None) -> None:
        """Validate unique constraint for a field."""
        # This would be implemented by specific repositories
        pass 