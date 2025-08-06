"""
Registry for physics modeling framework.

This module provides a central registry for managing and accessing all framework components.
It serves as a central point for component discovery and management.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class Registry:
    """
    Central registry for physics modeling framework components.
    
    This class provides a centralized way to register, discover, and access
    various components of the physics modeling framework.
    """
    
    def __init__(self):
        """Initialize the registry."""
        self.components: Dict[str, Any] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self.created_at = datetime.now()
        
        logger.info("Registry initialized")
    
    def register_component(self, component_id: str, component: Any, 
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a component in the registry.
        
        Args:
            component_id: Unique identifier for the component
            component: Component instance to register
            metadata: Optional metadata for the component
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            if component_id in self.components:
                logger.warning(f"Component {component_id} already registered, overwriting")
            
            self.components[component_id] = component
            self.metadata[component_id] = metadata or {}
            self.metadata[component_id]['registered_at'] = datetime.now().isoformat()
            
            logger.info(f"Successfully registered component: {component_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register component {component_id}: {e}")
            return False
    
    def get_component(self, component_id: str) -> Optional[Any]:
        """
        Get a component by ID.
        
        Args:
            component_id: Component ID
            
        Returns:
            Component instance or None if not found
        """
        return self.components.get(component_id)
    
    def get_component_metadata(self, component_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a component.
        
        Args:
            component_id: Component ID
            
        Returns:
            Component metadata or None if not found
        """
        return self.metadata.get(component_id)
    
    def list_components(self) -> List[str]:
        """
        List all registered component IDs.
        
        Returns:
            List of component IDs
        """
        return list(self.components.keys())
    
    def list_components_by_type(self, component_type: str) -> List[str]:
        """
        List components by type.
        
        Args:
            component_type: Type of components to list
            
        Returns:
            List of component IDs of the specified type
        """
        return [
            component_id 
            for component_id, metadata in self.metadata.items()
            if metadata.get('type') == component_type
        ]
    
    def unregister_component(self, component_id: str) -> bool:
        """
        Unregister a component.
        
        Args:
            component_id: Component ID to unregister
            
        Returns:
            True if unregistration successful, False otherwise
        """
        try:
            if component_id in self.components:
                del self.components[component_id]
                del self.metadata[component_id]
                logger.info(f"Successfully unregistered component: {component_id}")
                return True
            else:
                logger.warning(f"Component not found for unregistration: {component_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to unregister component {component_id}: {e}")
            return False
    
    def update_component_metadata(self, component_id: str, 
                                metadata: Dict[str, Any]) -> bool:
        """
        Update metadata for a component.
        
        Args:
            component_id: Component ID
            metadata: New metadata
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            if component_id not in self.components:
                logger.error(f"Component not found: {component_id}")
                return False
            
            self.metadata[component_id].update(metadata)
            self.metadata[component_id]['updated_at'] = datetime.now().isoformat()
            
            logger.info(f"Successfully updated metadata for component: {component_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update component metadata: {e}")
            return False
    
    def get_registry_info(self) -> Dict[str, Any]:
        """
        Get information about the registry.
        
        Returns:
            Registry information dictionary
        """
        return {
            'total_components': len(self.components),
            'created_at': self.created_at.isoformat(),
            'component_types': self._get_component_types(),
            'components': {
                component_id: {
                    'type': metadata.get('type', 'unknown'),
                    'registered_at': metadata.get('registered_at'),
                    'updated_at': metadata.get('updated_at')
                }
                for component_id, metadata in self.metadata.items()
            }
        }
    
    def clear_registry(self) -> bool:
        """
        Clear all components from the registry.
        
        Returns:
            True if clearing successful, False otherwise
        """
        try:
            self.components.clear()
            self.metadata.clear()
            logger.info("Successfully cleared registry")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear registry: {e}")
            return False
    
    def _get_component_types(self) -> Dict[str, int]:
        """
        Get count of components by type.
        
        Returns:
            Dictionary of component_type -> count
        """
        type_counts = {}
        for metadata in self.metadata.values():
            component_type = metadata.get('type', 'unknown')
            type_counts[component_type] = type_counts.get(component_type, 0) + 1
        return type_counts
    
    def search_components(self, search_term: str) -> List[str]:
        """
        Search for components by name or metadata.
        
        Args:
            search_term: Search term
            
        Returns:
            List of matching component IDs
        """
        matching_components = []
        search_term_lower = search_term.lower()
        
        for component_id, metadata in self.metadata.items():
            # Search in component ID
            if search_term_lower in component_id.lower():
                matching_components.append(component_id)
                continue
            
            # Search in metadata
            for key, value in metadata.items():
                if isinstance(value, str) and search_term_lower in value.lower():
                    matching_components.append(component_id)
                    break
        
        return matching_components
    
    def get_component_dependencies(self, component_id: str) -> List[str]:
        """
        Get dependencies for a component.
        
        Args:
            component_id: Component ID
            
        Returns:
            List of dependency component IDs
        """
        metadata = self.get_component_metadata(component_id)
        if metadata:
            return metadata.get('dependencies', [])
        return []
    
    def validate_dependencies(self, component_id: str) -> Dict[str, bool]:
        """
        Validate dependencies for a component.
        
        Args:
            component_id: Component ID
            
        Returns:
            Dictionary of dependency_id -> exists
        """
        dependencies = self.get_component_dependencies(component_id)
        return {
            dep_id: dep_id in self.components
            for dep_id in dependencies
        } 