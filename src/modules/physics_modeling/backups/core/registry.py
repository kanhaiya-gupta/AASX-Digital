"""
Central Registry

This module provides a central registry for managing all components in the
physics modeling framework including physics types, solvers, templates,
and other resources.
"""

from typing import Dict, List, Optional, Any, Type
import logging
from datetime import datetime
import json
import threading

from .dynamic_types import DynamicPhysicsType
from .plugin_manager import PhysicsPlugin
from .model_factory import PhysicsModel


class Registry:
    """
    Central registry for managing all physics modeling framework components.
    
    This class provides a unified interface for registering, discovering,
    and managing physics types, solvers, templates, and other resources
    in a thread-safe manner.
    """
    
    def __init__(self):
        """Initialize the central registry."""
        self._lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
        
        # Component registries
        self._physics_types: Dict[str, DynamicPhysicsType] = {}
        self._solvers: Dict[str, Dict[str, Any]] = {}
        self._templates: Dict[str, Dict[str, Any]] = {}
        self._models: Dict[str, Type[PhysicsModel]] = {}
        self._plugins: Dict[str, PhysicsPlugin] = {}
        
        # Metadata
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._statistics: Dict[str, int] = {
            'physics_types': 0,
            'solvers': 0,
            'templates': 0,
            'models': 0,
            'plugins': 0
        }
    
    # Physics Types Management
    def register_physics_type(self, physics_type: DynamicPhysicsType) -> bool:
        """
        Register a physics type.
        
        Args:
            physics_type: Physics type to register
            
        Returns:
            True if registration was successful, False otherwise
        """
        with self._lock:
            try:
                if not isinstance(physics_type, DynamicPhysicsType):
                    self.logger.error("Invalid physics type object")
                    return False
                
                if not physics_type.type_id or not physics_type.type_id.strip():
                    self.logger.error("Physics type must have a valid ID")
                    return False
                
                self._physics_types[physics_type.type_id] = physics_type
                self._statistics['physics_types'] = len(self._physics_types)
                
                # Store metadata
                self._metadata[physics_type.type_id] = {
                    'type': 'physics_type',
                    'name': physics_type.name,
                    'category': physics_type.category,
                    'registered_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                self.logger.info(f"Registered physics type: {physics_type.type_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Error registering physics type: {str(e)}")
                return False
    
    def get_physics_type(self, type_id: str) -> Optional[DynamicPhysicsType]:
        """
        Get a physics type by ID.
        
        Args:
            type_id: Physics type identifier
            
        Returns:
            Physics type or None if not found
        """
        with self._lock:
            return self._physics_types.get(type_id)
    
    def get_physics_types(self) -> List[str]:
        """
        Get list of all physics type IDs.
        
        Returns:
            List of physics type identifiers
        """
        with self._lock:
            return list(self._physics_types.keys())
    
    def get_physics_types_by_category(self, category: str) -> List[str]:
        """
        Get physics types by category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of physics type identifiers in the category
        """
        with self._lock:
            return [
                type_id for type_id, physics_type in self._physics_types.items()
                if physics_type.category == category
            ]
    
    def unregister_physics_type(self, type_id: str) -> bool:
        """
        Unregister a physics type.
        
        Args:
            type_id: Physics type identifier
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        with self._lock:
            if type_id in self._physics_types:
                del self._physics_types[type_id]
                self._statistics['physics_types'] = len(self._physics_types)
                
                if type_id in self._metadata:
                    del self._metadata[type_id]
                
                self.logger.info(f"Unregistered physics type: {type_id}")
                return True
            
            return False
    
    # Solvers Management
    def register_solver(self, solver_id: str, solver_data: Dict[str, Any]) -> bool:
        """
        Register a solver.
        
        Args:
            solver_id: Solver identifier
            solver_data: Solver data
            
        Returns:
            True if registration was successful, False otherwise
        """
        with self._lock:
            try:
                required_fields = ['name', 'physics_types', 'capabilities']
                for field in required_fields:
                    if field not in solver_data:
                        self.logger.error(f"Solver data missing required field: {field}")
                        return False
                
                self._solvers[solver_id] = solver_data.copy()
                self._statistics['solvers'] = len(self._solvers)
                
                # Store metadata
                self._metadata[solver_id] = {
                    'type': 'solver',
                    'name': solver_data['name'],
                    'physics_types': solver_data['physics_types'],
                    'registered_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                self.logger.info(f"Registered solver: {solver_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Error registering solver: {str(e)}")
                return False
    
    def get_solver(self, solver_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a solver by ID.
        
        Args:
            solver_id: Solver identifier
            
        Returns:
            Solver data or None if not found
        """
        with self._lock:
            return self._solvers.get(solver_id)
    
    def get_solvers_for_physics_type(self, physics_type: str) -> List[str]:
        """
        Get solvers that support a specific physics type.
        
        Args:
            physics_type: Physics type identifier
            
        Returns:
            List of solver identifiers
        """
        with self._lock:
            return [
                solver_id for solver_id, solver_data in self._solvers.items()
                if physics_type in solver_data.get('physics_types', [])
            ]
    
    def get_all_solvers(self) -> List[str]:
        """
        Get list of all solver IDs.
        
        Returns:
            List of solver identifiers
        """
        with self._lock:
            return list(self._solvers.keys())
    
    def unregister_solver(self, solver_id: str) -> bool:
        """
        Unregister a solver.
        
        Args:
            solver_id: Solver identifier
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        with self._lock:
            if solver_id in self._solvers:
                del self._solvers[solver_id]
                self._statistics['solvers'] = len(self._solvers)
                
                if solver_id in self._metadata:
                    del self._metadata[solver_id]
                
                self.logger.info(f"Unregistered solver: {solver_id}")
                return True
            
            return False
    
    # Templates Management
    def register_template(self, template_id: str, template_data: Dict[str, Any]) -> bool:
        """
        Register a template.
        
        Args:
            template_id: Template identifier
            template_data: Template data
            
        Returns:
            True if registration was successful, False otherwise
        """
        with self._lock:
            try:
                required_fields = ['name', 'physics_type_id', 'parameters']
                for field in required_fields:
                    if field not in template_data:
                        self.logger.error(f"Template data missing required field: {field}")
                        return False
                
                self._templates[template_id] = template_data.copy()
                self._statistics['templates'] = len(self._templates)
                
                # Store metadata
                self._metadata[template_id] = {
                    'type': 'template',
                    'name': template_data['name'],
                    'physics_type_id': template_data['physics_type_id'],
                    'registered_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                self.logger.info(f"Registered template: {template_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Error registering template: {str(e)}")
                return False
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a template by ID.
        
        Args:
            template_id: Template identifier
            
        Returns:
            Template data or None if not found
        """
        with self._lock:
            return self._templates.get(template_id)
    
    def get_templates_for_physics_type(self, physics_type_id: str) -> List[str]:
        """
        Get templates for a specific physics type.
        
        Args:
            physics_type_id: Physics type identifier
            
        Returns:
            List of template identifiers
        """
        with self._lock:
            return [
                template_id for template_id, template_data in self._templates.items()
                if template_data.get('physics_type_id') == physics_type_id
            ]
    
    def get_all_templates(self) -> List[str]:
        """
        Get list of all template IDs.
        
        Returns:
            List of template identifiers
        """
        with self._lock:
            return list(self._templates.keys())
    
    def unregister_template(self, template_id: str) -> bool:
        """
        Unregister a template.
        
        Args:
            template_id: Template identifier
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        with self._lock:
            if template_id in self._templates:
                del self._templates[template_id]
                self._statistics['templates'] = len(self._templates)
                
                if template_id in self._metadata:
                    del self._metadata[template_id]
                
                self.logger.info(f"Unregistered template: {template_id}")
                return True
            
            return False
    
    # Models Management
    def register_model(self, physics_type_id: str, model_class: Type[PhysicsModel]) -> bool:
        """
        Register a model class for a physics type.
        
        Args:
            physics_type_id: Physics type identifier
            model_class: Model class to register
            
        Returns:
            True if registration was successful, False otherwise
        """
        with self._lock:
            try:
                if not issubclass(model_class, PhysicsModel):
                    self.logger.error("Model class must inherit from PhysicsModel")
                    return False
                
                self._models[physics_type_id] = model_class
                self._statistics['models'] = len(self._models)
                
                # Store metadata
                self._metadata[f"model_{physics_type_id}"] = {
                    'type': 'model',
                    'physics_type_id': physics_type_id,
                    'model_class_name': model_class.__name__,
                    'registered_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                self.logger.info(f"Registered model for physics type: {physics_type_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Error registering model: {str(e)}")
                return False
    
    def get_model_class(self, physics_type_id: str) -> Optional[Type[PhysicsModel]]:
        """
        Get a model class for a physics type.
        
        Args:
            physics_type_id: Physics type identifier
            
        Returns:
            Model class or None if not found
        """
        with self._lock:
            return self._models.get(physics_type_id)
    
    def get_all_models(self) -> List[str]:
        """
        Get list of all physics types with registered models.
        
        Returns:
            List of physics type identifiers
        """
        with self._lock:
            return list(self._models.keys())
    
    def unregister_model(self, physics_type_id: str) -> bool:
        """
        Unregister a model class.
        
        Args:
            physics_type_id: Physics type identifier
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        with self._lock:
            if physics_type_id in self._models:
                del self._models[physics_type_id]
                self._statistics['models'] = len(self._models)
                
                metadata_key = f"model_{physics_type_id}"
                if metadata_key in self._metadata:
                    del self._metadata[metadata_key]
                
                self.logger.info(f"Unregistered model for physics type: {physics_type_id}")
                return True
            
            return False
    
    # Plugins Management
    def register_plugin(self, plugin_id: str, plugin: PhysicsPlugin) -> bool:
        """
        Register a plugin.
        
        Args:
            plugin_id: Plugin identifier
            plugin: Plugin instance
            
        Returns:
            True if registration was successful, False otherwise
        """
        with self._lock:
            try:
                if not isinstance(plugin, PhysicsPlugin):
                    self.logger.error("Invalid plugin object")
                    return False
                
                self._plugins[plugin_id] = plugin
                self._statistics['plugins'] = len(self._plugins)
                
                # Store metadata
                self._metadata[plugin_id] = {
                    'type': 'plugin',
                    'name': plugin.__class__.__name__,
                    'registered_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                self.logger.info(f"Registered plugin: {plugin_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Error registering plugin: {str(e)}")
                return False
    
    def get_plugin(self, plugin_id: str) -> Optional[PhysicsPlugin]:
        """
        Get a plugin by ID.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Plugin instance or None if not found
        """
        with self._lock:
            return self._plugins.get(plugin_id)
    
    def get_all_plugins(self) -> List[str]:
        """
        Get list of all plugin IDs.
        
        Returns:
            List of plugin identifiers
        """
        with self._lock:
            return list(self._plugins.keys())
    
    def unregister_plugin(self, plugin_id: str) -> bool:
        """
        Unregister a plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        with self._lock:
            if plugin_id in self._plugins:
                del self._plugins[plugin_id]
                self._statistics['plugins'] = len(self._plugins)
                
                if plugin_id in self._metadata:
                    del self._metadata[plugin_id]
                
                self.logger.info(f"Unregistered plugin: {plugin_id}")
                return True
            
            return False
    
    # General Registry Operations
    def get_statistics(self) -> Dict[str, int]:
        """
        Get registry statistics.
        
        Returns:
            Dictionary of component counts
        """
        with self._lock:
            return self._statistics.copy()
    
    def get_metadata(self, component_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a component.
        
        Args:
            component_id: Component identifier
            
        Returns:
            Component metadata or None if not found
        """
        with self._lock:
            return self._metadata.get(component_id)
    
    def list_components(self, component_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all components with their metadata.
        
        Args:
            component_type: Optional filter by component type
            
        Returns:
            List of component information dictionaries
        """
        with self._lock:
            components = []
            
            for component_id, metadata in self._metadata.items():
                if component_type is None or metadata.get('type') == component_type:
                    components.append({
                        'id': component_id,
                        **metadata
                    })
            
            return components
    
    def clear(self) -> None:
        """Clear all registries."""
        with self._lock:
            self._physics_types.clear()
            self._solvers.clear()
            self._templates.clear()
            self._models.clear()
            self._plugins.clear()
            self._metadata.clear()
            
            for key in self._statistics:
                self._statistics[key] = 0
            
            self.logger.info("Cleared all registries")
    
    def export_registry(self) -> Dict[str, Any]:
        """
        Export the entire registry state.
        
        Returns:
            Dictionary containing all registry data
        """
        with self._lock:
            return {
                'physics_types': {
                    type_id: physics_type.to_dict()
                    for type_id, physics_type in self._physics_types.items()
                },
                'solvers': self._solvers.copy(),
                'templates': self._templates.copy(),
                'models': {
                    type_id: model_class.__name__
                    for type_id, model_class in self._models.items()
                },
                'plugins': {
                    plugin_id: plugin.__class__.__name__
                    for plugin_id, plugin in self._plugins.items()
                },
                'metadata': self._metadata.copy(),
                'statistics': self._statistics.copy(),
                'exported_at': datetime.now().isoformat()
            }
    
    def import_registry(self, registry_data: Dict[str, Any]) -> bool:
        """
        Import registry state from exported data.
        
        Args:
            registry_data: Registry data to import
            
        Returns:
            True if import was successful, False otherwise
        """
        with self._lock:
            try:
                # Clear existing data
                self.clear()
                
                # Import physics types
                for type_id, type_data in registry_data.get('physics_types', {}).items():
                    physics_type = DynamicPhysicsType.from_dict(type_data)
                    self.register_physics_type(physics_type)
                
                # Import solvers
                for solver_id, solver_data in registry_data.get('solvers', {}).items():
                    self.register_solver(solver_id, solver_data)
                
                # Import templates
                for template_id, template_data in registry_data.get('templates', {}).items():
                    self.register_template(template_id, template_data)
                
                # Note: Models and plugins cannot be imported from serialized data
                # as they require actual class instances
                
                self.logger.info("Successfully imported registry data")
                return True
                
            except Exception as e:
                self.logger.error(f"Error importing registry data: {str(e)}")
                return False 