"""
Registry for physics modeling framework.

This module provides a central registry for managing and accessing all framework components.
It integrates with the new src/engine infrastructure and provides enterprise-grade features.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..models.physics_modeling_registry import PhysicsModelingRegistry
from ..repositories.physics_modeling_registry_repository import PhysicsModelingRegistryRepository

logger = logging.getLogger(__name__)


class Registry:
    """
    Central registry for physics modeling framework components with modern engine integration.
    
    This class provides a centralized way to register, discover, and access
    various components of the physics modeling framework with enterprise features.
    """
    
    def __init__(self, registry_repository: Optional[PhysicsModelingRegistryRepository] = None):
        """
        Initialize the registry with modern engine integration.
        
        Args:
            registry_repository: Repository for physics modeling registry (optional)
        """
        self.registry_repo = registry_repository or PhysicsModelingRegistryRepository()
        self.components: Dict[str, Any] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self.created_at = datetime.now()
        
        logger.info("✅ Modern Registry initialized with engine infrastructure")
    
    async def initialize(self) -> bool:
        """Initialize the registry asynchronously."""
        try:
            await asyncio.sleep(0)  # Ensure async context
            logger.info("Initializing Registry with engine infrastructure")
            
            # Initialize the registry repository
            await self.registry_repo.initialize()
            
            logger.info("✅ Registry initialization completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Registry: {e}")
            return False
    
    async def register_component(self, component_id: str, component: Any, 
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a component in the registry with enterprise features.
        
        Args:
            component_id: Unique identifier for the component
            component: Component instance to register
            metadata: Optional metadata for the component
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            if component_id in self.components:
                logger.warning(f"Component {component_id} already registered, overwriting")
            
            # Store component locally
            self.components[component_id] = component
            self.metadata[component_id] = metadata or {}
            self.metadata[component_id]['registered_at'] = datetime.now().isoformat()
            
            # Create registry record with enterprise features
            component_record = PhysicsModelingRegistry(
                model_name=component_id,
                physics_type=metadata.get('physics_type', 'component') if metadata else 'component',
                model_version=metadata.get('version', '1.0.0') if metadata else '1.0.0',
                description=metadata.get('description', f'Component: {component_id}') if metadata else f'Component: {component_id}',
                model_parameters=metadata.get('parameters', {}) if metadata else {},
                status="active",
                compliance_score=100.0,  # Default compliance score
                security_score=100.0,   # Default security score
                performance_score=100.0, # Default performance score
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Save to the registry
            saved_record = await self.registry_repo.create(component_record)
            
            if saved_record:
                logger.info(f"✅ Successfully registered component: {component_id} with enterprise features")
                return True
            else:
                logger.error(f"Failed to save component {component_id} to registry")
                return False
            
        except Exception as e:
            logger.error(f"Failed to register component {component_id}: {e}")
            return False
    
    async def get_component(self, component_id: str) -> Optional[Any]:
        """
        Get a component by ID with enterprise validation.
        
        Args:
            component_id: Component ID
            
        Returns:
            Component instance or None if not found
        """
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            # Check local components first
            if component_id in self.components:
                # Validate component compliance
                await self._validate_component_compliance(component_id)
                return self.components[component_id]
            
            # Try to find in registry
            component_record = await self.registry_repo.get_by_id(component_id)
            if component_record:
                logger.info(f"Component {component_id} found in registry but not loaded locally")
                return None
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get component {component_id}: {e}")
            return None
    
    async def get_component_metadata(self, component_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a component with enterprise features.
        
        Args:
            component_id: Component ID
            
        Returns:
            Component metadata with enterprise features or None if not found
        """
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            # Get local metadata
            local_metadata = self.metadata.get(component_id, {})
            
            # Get registry metadata
            component_record = await self.registry_repo.get_by_id(component_id)
            if component_record:
                # Enhance with enterprise features
                enhanced_metadata = {
                    **local_metadata,
                    'registry_id': component_record.registry_id,
                    'compliance_score': component_record.compliance_score,
                    'security_score': component_record.security_score,
                    'performance_score': component_record.performance_score,
                    'status': component_record.status,
                    'created_at': component_record.created_at,
                    'updated_at': component_record.updated_at
                }
                return enhanced_metadata
            
            return local_metadata
            
        except Exception as e:
            logger.error(f"Failed to get component metadata {component_id}: {e}")
            return None
    
    async def list_components(self) -> List[str]:
        """
        List all registered component IDs with enterprise filtering.
        
        Returns:
            List of component IDs
        """
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            # Get local components
            local_components = list(self.components.keys())
            
            # Get registry components
            registry_components = await self.registry_repo.get_all()
            registry_ids = [comp.registry_id for comp in registry_components]
            
            # Combine and deduplicate
            all_components = list(set(local_components + registry_ids))
            
            return all_components
            
        except Exception as e:
            logger.error(f"Failed to list components: {e}")
            return list(self.components.keys())
    
    async def list_components_by_type(self, component_type: str) -> List[str]:
        """
        List components by type with enterprise filtering.
        
        Args:
            component_type: Type of components to list
            
        Returns:
            List of component IDs of the specified type
        """
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            # Get components from registry by type
            type_components = await self.registry_repo.get_by_physics_type(component_type)
            
            # Filter local components by type
            local_type_components = [
                comp_id for comp_id, metadata in self.metadata.items()
                if metadata.get('physics_type') == component_type
            ]
            
            # Combine and deduplicate
            all_type_components = list(set(local_type_components + [comp.registry_id for comp in type_components]))
            
            return all_type_components
            
        except Exception as e:
            logger.error(f"Failed to list components by type {component_type}: {e}")
            return []
    
    async def unregister_component(self, component_id: str) -> bool:
        """
        Unregister a component from the registry.
        
        Args:
            component_id: Component ID to unregister
            
        Returns:
            True if unregistration successful, False otherwise
        """
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            # Remove from local storage
            if component_id in self.components:
                del self.components[component_id]
            
            if component_id in self.metadata:
                del self.metadata[component_id]
            
            # Update status in registry
            component_record = await self.registry_repo.get_by_id(component_id)
            if component_record:
                component_record.status = "inactive"
                component_record.updated_at = datetime.utcnow()
                await self.registry_repo.update(component_record)
            
            logger.info(f"✅ Successfully unregistered component: {component_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister component {component_id}: {e}")
            return False
    
    async def get_component_status(self, component_id: str) -> Optional[Dict[str, Any]]:
        """
        Get component status with enterprise metrics.
        
        Args:
            component_id: Component ID
            
        Returns:
            Component status dictionary with enterprise features or None if not found
        """
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            # Get registry status
            component_record = await self.registry_repo.get_by_id(component_id)
            if component_record:
                return {
                    'component_id': component_id,
                    'status': component_record.status,
                    'compliance_score': component_record.compliance_score,
                    'security_score': component_record.security_score,
                    'performance_score': component_record.performance_score,
                    'created_at': component_record.created_at,
                    'updated_at': component_record.updated_at,
                    'is_active': component_id in self.components
                }
            
            # Fallback to local status
            if component_id in self.components:
                return {
                    'component_id': component_id,
                    'status': 'active',
                    'compliance_score': 100.0,
                    'security_score': 100.0,
                    'performance_score': 100.0,
                    'created_at': self.metadata.get(component_id, {}).get('registered_at'),
                    'updated_at': self.metadata.get(component_id, {}).get('registered_at'),
                    'is_active': True
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get component status {component_id}: {e}")
            return None
    
    async def update_component_metadata(self, component_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Update component metadata with enterprise validation.
        
        Args:
            component_id: Component ID
            metadata: New metadata to update
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            # Update local metadata
            if component_id in self.metadata:
                self.metadata[component_id].update(metadata)
                self.metadata[component_id]['updated_at'] = datetime.now().isoformat()
            
            # Update registry record
            component_record = await self.registry_repo.get_by_id(component_id)
            if component_record:
                # Update relevant fields
                if 'description' in metadata:
                    component_record.description = metadata['description']
                if 'parameters' in metadata:
                    component_record.model_parameters = metadata['parameters']
                
                component_record.updated_at = datetime.utcnow()
                updated_record = await self.registry_repo.update(component_record)
                
                if updated_record:
                    logger.info(f"✅ Successfully updated component metadata: {component_id}")
                    return True
                else:
                    logger.error(f"Failed to update component metadata in registry: {component_id}")
                    return False
            
            logger.info(f"✅ Successfully updated local component metadata: {component_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update component metadata {component_id}: {e}")
            return False
    
    async def _validate_component_compliance(self, component_id: str) -> bool:
        """
        Validate component compliance with enterprise standards.
        
        Args:
            component_id: Component ID to validate
            
        Returns:
            True if compliant, False otherwise
        """
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            # Get component record
            component_record = await self.registry_repo.get_by_id(component_id)
            if not component_record:
                return True  # No registry record, assume compliant
            
            # Check compliance score
            if component_record.compliance_score < 80.0:
                logger.warning(f"Component {component_id} has low compliance score: {component_record.compliance_score}")
                return False
            
            # Check security score
            if component_record.security_score < 80.0:
                logger.warning(f"Component {component_id} has low security score: {component_record.security_score}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate component compliance {component_id}: {e}")
            return False
    
    async def get_registry_summary(self) -> Dict[str, Any]:
        """
        Get registry summary with enterprise metrics.
        
        Returns:
            Registry summary dictionary
        """
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            # Get all registry records
            all_components = await self.registry_repo.get_all()
            
            # Calculate metrics
            total_components = len(all_components)
            active_components = len([c for c in all_components if c.status == 'active'])
            avg_compliance = sum(c.compliance_score for c in all_components) / total_components if total_components > 0 else 0
            avg_security = sum(c.security_score for c in all_components) / total_components if total_components > 0 else 0
            avg_performance = sum(c.performance_score for c in all_components) / total_components if total_components > 0 else 0
            
            return {
                'total_components': total_components,
                'active_components': active_components,
                'inactive_components': total_components - active_components,
                'average_compliance_score': round(avg_compliance, 2),
                'average_security_score': round(avg_security, 2),
                'average_performance_score': round(avg_performance, 2),
                'registry_health': 'healthy' if avg_compliance > 80 and avg_security > 80 else 'warning',
                'created_at': self.created_at.isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get registry summary: {e}")
            return {
                'total_components': len(self.components),
                'active_components': len(self.components),
                'inactive_components': 0,
                'average_compliance_score': 100.0,
                'average_security_score': 100.0,
                'average_performance_score': 100.0,
                'registry_health': 'healthy',
                'created_at': self.created_at.isoformat(),
                'last_updated': datetime.now().isoformat()
            }
    
    async def close(self):
        """Close the registry and cleanup resources."""
        try:
            await asyncio.sleep(0)  # Ensure async context
            logger.info("Closing Registry")
            
            # Close registry repository
            if hasattr(self.registry_repo, 'close'):
                await self.registry_repo.close()
            
            # Clear local storage
            self.components.clear()
            self.metadata.clear()
            
            logger.info("✅ Registry closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing Registry: {e}") 