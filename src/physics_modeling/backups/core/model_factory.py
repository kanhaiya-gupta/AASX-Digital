"""
Dynamic Model Factory

This module provides a factory pattern for creating physics model instances
dynamically based on physics type definitions and parameters.
"""

from typing import Dict, List, Optional, Any, Type
import logging
from abc import ABC, abstractmethod

from .dynamic_types import DynamicPhysicsType, PhysicsParameter
from .plugin_manager import PhysicsPlugin, PhysicsPluginManager


class PhysicsModel(ABC):
    """
    Abstract base class for physics models.
    
    All physics models must inherit from this class and implement
    the required methods.
    """
    
    def __init__(self, physics_type: DynamicPhysicsType, parameters: Dict[str, Any]):
        """
        Initialize a physics model.
        
        Args:
            physics_type: The physics type definition
            parameters: Model parameters
        """
        self.physics_type = physics_type
        self.parameters = parameters
        self.results = {}
        self.metadata = {}
    
    @abstractmethod
    def setup(self) -> bool:
        """
        Set up the physics model with the given parameters.
        
        Returns:
            True if setup was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def solve(self) -> Dict[str, Any]:
        """
        Solve the physics problem.
        
        Returns:
            Dictionary containing simulation results
        """
        pass
    
    @abstractmethod
    def validate(self) -> Dict[str, str]:
        """
        Validate the model parameters and setup.
        
        Returns:
            Dictionary of validation errors (empty if valid)
        """
        pass
    
    def get_parameter(self, name: str) -> Any:
        """Get a model parameter by name."""
        return self.parameters.get(name)
    
    def set_parameter(self, name: str, value: Any) -> None:
        """Set a model parameter."""
        self.parameters[name] = value
    
    def get_results(self) -> Dict[str, Any]:
        """Get the simulation results."""
        return self.results.copy()
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata."""
        return self.metadata.copy()


class DynamicModelFactory:
    """
    Factory for creating physics model instances dynamically.
    
    This class provides methods to create physics models based on
    physics type definitions and parameters, with automatic validation
    and plugin integration.
    """
    
    def __init__(self, plugin_manager: Optional[PhysicsPluginManager] = None):
        """
        Initialize the model factory.
        
        Args:
            plugin_manager: Plugin manager instance (optional)
        """
        self.plugin_manager = plugin_manager or PhysicsPluginManager()
        self.model_registry: Dict[str, Type[PhysicsModel]] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_model_class(self, physics_type_id: str, model_class: Type[PhysicsModel]) -> None:
        """
        Register a model class for a specific physics type.
        
        Args:
            physics_type_id: Physics type identifier
            model_class: Model class to register
        """
        if not issubclass(model_class, PhysicsModel):
            raise ValueError("Model class must inherit from PhysicsModel")
        
        self.model_registry[physics_type_id] = model_class
        self.logger.info(f"Registered model class for physics type: {physics_type_id}")
    
    def create_model(self, physics_type_id: str, parameters: Dict[str, Any]) -> Optional[PhysicsModel]:
        """
        Create a physics model instance.
        
        Args:
            physics_type_id: Physics type identifier
            parameters: Model parameters
            
        Returns:
            Physics model instance or None if creation failed
        """
        try:
            # Get the physics type definition
            physics_type = self._get_physics_type(physics_type_id)
            if not physics_type:
                self.logger.error(f"Physics type not found: {physics_type_id}")
                return None
            
            # Validate parameters against physics type definition
            validation_errors = physics_type.validate_parameters(parameters)
            if validation_errors:
                self.logger.error(f"Parameter validation failed: {validation_errors}")
                return None
            
            # Try to get model class from registry
            model_class = self.model_registry.get(physics_type_id)
            
            if model_class:
                # Create model using registered class
                model = model_class(physics_type, parameters)
            else:
                # Try to create model using plugin
                model = self._create_model_from_plugin(physics_type_id, physics_type, parameters)
            
            if model:
                # Validate the model
                model_validation = model.validate()
                if model_validation:
                    self.logger.error(f"Model validation failed: {model_validation}")
                    return None
                
                # Set up the model
                if not model.setup():
                    self.logger.error(f"Model setup failed for physics type: {physics_type_id}")
                    return None
                
                self.logger.info(f"Successfully created model for physics type: {physics_type_id}")
                return model
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error creating model for physics type {physics_type_id}: {str(e)}")
            return None
    
    def _get_physics_type(self, physics_type_id: str) -> Optional[DynamicPhysicsType]:
        """
        Get physics type definition from plugin manager or registry.
        
        Args:
            physics_type_id: Physics type identifier
            
        Returns:
            Physics type definition or None if not found
        """
        # Try to get from plugin manager first
        plugin = self.plugin_manager.get_plugin(physics_type_id)
        if plugin:
            return plugin.get_physics_type()
        
        # TODO: Try to get from database registry
        # This would be implemented when database integration is added
        
        return None
    
    def _create_model_from_plugin(self, physics_type_id: str, physics_type: DynamicPhysicsType, parameters: Dict[str, Any]) -> Optional[PhysicsModel]:
        """
        Create a model using a plugin.
        
        Args:
            physics_type_id: Physics type identifier
            physics_type: Physics type definition
            parameters: Model parameters
            
        Returns:
            Physics model instance or None if creation failed
        """
        plugin = self.plugin_manager.get_plugin(physics_type_id)
        if not plugin:
            return None
        
        # Create a wrapper model that uses the plugin
        return PluginWrapperModel(physics_type, parameters, plugin)
    
    def get_available_physics_types(self) -> List[str]:
        """
        Get list of available physics types.
        
        Returns:
            List of physics type identifiers
        """
        # Get from plugin manager
        plugin_types = list(self.plugin_manager.get_all_plugins().keys())
        
        # Get from model registry
        registry_types = list(self.model_registry.keys())
        
        # Combine and remove duplicates
        all_types = list(set(plugin_types + registry_types))
        return all_types
    
    def get_model_info(self, physics_type_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a model type.
        
        Args:
            physics_type_id: Physics type identifier
            
        Returns:
            Model information dictionary or None if not found
        """
        physics_type = self._get_physics_type(physics_type_id)
        if not physics_type:
            return None
        
        model_class = self.model_registry.get(physics_type_id)
        plugin = self.plugin_manager.get_plugin(physics_type_id)
        
        return {
            'physics_type_id': physics_type_id,
            'physics_type': physics_type.to_dict(),
            'has_model_class': model_class is not None,
            'has_plugin': plugin is not None,
            'model_class_name': model_class.__name__ if model_class else None,
            'plugin_name': plugin.__class__.__name__ if plugin else None
        }
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        List all available models.
        
        Returns:
            List of model information dictionaries
        """
        models_info = []
        
        for physics_type_id in self.get_available_physics_types():
            model_info = self.get_model_info(physics_type_id)
            if model_info:
                models_info.append(model_info)
        
        return models_info


class PluginWrapperModel(PhysicsModel):
    """
    Wrapper model that uses a plugin for implementation.
    
    This class provides a bridge between the model factory and plugins,
    allowing plugins to be used as physics models.
    """
    
    def __init__(self, physics_type: DynamicPhysicsType, parameters: Dict[str, Any], plugin: PhysicsPlugin):
        """
        Initialize the plugin wrapper model.
        
        Args:
            physics_type: Physics type definition
            parameters: Model parameters
            plugin: Plugin instance
        """
        super().__init__(physics_type, parameters)
        self.plugin = plugin
    
    def setup(self) -> bool:
        """Set up the model (no-op for plugin wrapper)."""
        return True
    
    def solve(self) -> Dict[str, Any]:
        """
        Solve using the plugin.
        
        Returns:
            Simulation results from the plugin
        """
        try:
            self.results = self.plugin.solve(self.parameters)
            return self.results
        except Exception as e:
            self.logger.error(f"Plugin solve failed: {str(e)}")
            return {}
    
    def validate(self) -> Dict[str, str]:
        """
        Validate using the plugin.
        
        Returns:
            Validation errors from the plugin
        """
        try:
            return self.plugin.validate_input(self.parameters)
        except Exception as e:
            return {'plugin_error': f"Plugin validation failed: {str(e)}"}
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata including plugin information."""
        metadata = super().get_metadata()
        metadata.update({
            'plugin_name': self.plugin.__class__.__name__,
            'plugin_metadata': self.plugin.get_metadata()
        })
        return metadata 