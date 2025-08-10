"""
Physics Modeling User-Specific Service
Handles user-specific data operations for the Physics Modeling module.
Distinguishes between independent users and organization members.
"""

import logging
from typing import Dict, Any, List, Optional
from webapp.core.context.user_context import UserContext

logger = logging.getLogger(__name__)


class PhysicsModelingUserSpecificService:
    """Service for handling user-specific physics modeling operations."""
    
    def __init__(self, user_context: UserContext):
        self.user_context = user_context
        self.user_id = getattr(user_context, 'user_id', None)
        self.organization_id = getattr(user_context, 'organization_id', None)
        user_is_independent = getattr(user_context, 'is_independent', None)
        if user_is_independent is None:
            self.is_independent = self.organization_id is None
        else:
            self.is_independent = user_is_independent
        self.user_type = getattr(user_context, 'get_user_type', lambda: 'independent')()
        self.role = getattr(user_context, 'role', 'viewer')
        self.permissions = getattr(user_context, 'permissions', [])
        logger.info(f"Initialized PhysicsModelingUserSpecificService for user {self.user_id} "
                   f"(type: {self.user_type}, independent: {self.is_independent})")

    def get_user_models(self) -> List[Dict[str, Any]]:
        """Get physics models accessible to the current user."""
        if self.is_independent:
            # Independent users see only their own models
            return self._get_independent_user_models()
        else:
            # Organization members see organization models + their own
            return self._get_organization_user_models()

    def get_user_simulations(self) -> List[Dict[str, Any]]:
        """Get simulations accessible to the current user."""
        if self.is_independent:
            return self._get_independent_user_simulations()
        else:
            return self._get_organization_user_simulations()

    def get_user_validations(self) -> List[Dict[str, Any]]:
        """Get validations accessible to the current user."""
        if self.is_independent:
            return self._get_independent_user_validations()
        else:
            return self._get_organization_user_validations()

    def get_user_use_cases(self) -> List[Dict[str, Any]]:
        """Get use cases accessible to the current user."""
        if self.is_independent:
            return self._get_independent_user_use_cases()
        else:
            return self._get_organization_user_use_cases()

    def get_user_statistics(self) -> Dict[str, Any]:
        """Get user-specific statistics."""
        if self.is_independent:
            return self._get_independent_user_statistics()
        else:
            return self._get_organization_user_statistics()

    def can_access_model(self, model_id: str) -> bool:
        """Check if user can access a specific model."""
        if self.is_independent:
            return self._can_access_independent_model(model_id)
        else:
            return self._can_access_organization_model(model_id)

    def can_create_model(self) -> bool:
        """Check if user can create a new model."""
        required_permissions = ['create']
        return any(perm in self.permissions for perm in required_permissions)

    def can_update_model(self, model_id: str) -> bool:
        """Check if user can update a specific model."""
        if not any(perm in self.permissions for perm in ['update']):
            return False
        
        if self.is_independent:
            return self._can_access_independent_model(model_id)
        else:
            return self._can_access_organization_model(model_id)

    def can_delete_model(self, model_id: str) -> bool:
        """Check if user can delete a specific model."""
        if not any(perm in self.permissions for perm in ['delete']):
            return False
        
        if self.is_independent:
            return self._can_access_independent_model(model_id)
        else:
            return self._can_access_organization_model(model_id)

    def can_run_simulation(self, model_id: str) -> bool:
        """Check if user can run simulation on a specific model."""
        if not any(perm in self.permissions for perm in ['create']):
            return False
        
        return self.can_access_model(model_id)

    def can_validate_model(self, model_id: str) -> bool:
        """Check if user can validate a specific model."""
        if not any(perm in self.permissions for perm in ['create']):
            return False
        
        return self.can_access_model(model_id)

    def get_user_model_limits(self) -> Dict[str, Any]:
        """Get user's model creation and usage limits."""
        if self.is_independent:
            return {
                'max_models': 10,
                'max_simulations': 50,
                'max_storage_gb': 5.0,
                'concurrent_simulations': 2
            }
        else:
            # Organization limits depend on user role
            if self.role in ['admin', 'manager']:
                return {
                    'max_models': 100,
                    'max_simulations': 500,
                    'max_storage_gb': 50.0,
                    'concurrent_simulations': 10
                }
            else:
                return {
                    'max_models': 25,
                    'max_simulations': 100,
                    'max_storage_gb': 10.0,
                    'concurrent_simulations': 3
                }

    def _get_independent_user_models(self) -> List[Dict[str, Any]]:
        """Get models for independent user."""
        # Mock implementation - replace with actual database query
        return [
            {
                'id': 'model_001',
                'name': 'Thermal Analysis Model',
                'type': 'thermal',
                'created_by': self.user_id,
                'status': 'active',
                'created_at': '2024-01-15T10:00:00Z'
            }
        ]

    def _get_organization_user_models(self) -> List[Dict[str, Any]]:
        """Get models for organization user."""
        # Mock implementation - replace with actual database query
        return [
            {
                'id': 'model_001',
                'name': 'Structural Analysis Model',
                'type': 'structural',
                'created_by': self.user_id,
                'organization_id': self.organization_id,
                'status': 'active',
                'created_at': '2024-01-15T10:00:00Z'
            },
            {
                'id': 'model_002',
                'name': 'Fluid Dynamics Model',
                'type': 'fluid',
                'created_by': 'other_user',
                'organization_id': self.organization_id,
                'status': 'active',
                'created_at': '2024-01-14T15:30:00Z'
            }
        ]

    def _get_independent_user_simulations(self) -> List[Dict[str, Any]]:
        """Get simulations for independent user."""
        # Mock implementation
        return [
            {
                'id': 'sim_001',
                'model_id': 'model_001',
                'status': 'completed',
                'progress': 100.0,
                'created_at': '2024-01-15T11:00:00Z'
            }
        ]

    def _get_organization_user_simulations(self) -> List[Dict[str, Any]]:
        """Get simulations for organization user."""
        # Mock implementation
        return [
            {
                'id': 'sim_001',
                'model_id': 'model_001',
                'status': 'completed',
                'progress': 100.0,
                'created_at': '2024-01-15T11:00:00Z'
            },
            {
                'id': 'sim_002',
                'model_id': 'model_002',
                'status': 'running',
                'progress': 45.0,
                'created_at': '2024-01-15T12:00:00Z'
            }
        ]

    def _get_independent_user_validations(self) -> List[Dict[str, Any]]:
        """Get validations for independent user."""
        # Mock implementation
        return [
            {
                'id': 'val_001',
                'model_id': 'model_001',
                'accuracy_score': 0.95,
                'status': 'completed',
                'timestamp': '2024-01-15T13:00:00Z'
            }
        ]

    def _get_organization_user_validations(self) -> List[Dict[str, Any]]:
        """Get validations for organization user."""
        # Mock implementation
        return [
            {
                'id': 'val_001',
                'model_id': 'model_001',
                'accuracy_score': 0.95,
                'status': 'completed',
                'timestamp': '2024-01-15T13:00:00Z'
            },
            {
                'id': 'val_002',
                'model_id': 'model_002',
                'accuracy_score': 0.92,
                'status': 'completed',
                'timestamp': '2024-01-15T14:00:00Z'
            }
        ]

    def _get_independent_user_use_cases(self) -> List[Dict[str, Any]]:
        """Get use cases for independent user."""
        # Mock implementation
        return [
            {
                'id': 'uc_001',
                'name': 'Thermal Management',
                'category': 'thermal',
                'description': 'Thermal analysis for electronic components'
            }
        ]

    def _get_organization_user_use_cases(self) -> List[Dict[str, Any]]:
        """Get use cases for organization user."""
        # Mock implementation
        return [
            {
                'id': 'uc_001',
                'name': 'Structural Analysis',
                'category': 'structural',
                'description': 'Structural integrity analysis'
            },
            {
                'id': 'uc_002',
                'name': 'Fluid Dynamics',
                'category': 'fluid',
                'description': 'Fluid flow analysis in complex geometries'
            }
        ]

    def _get_independent_user_statistics(self) -> Dict[str, Any]:
        """Get statistics for independent user."""
        return {
            'total_models': 1,
            'active_simulations': 0,
            'completed_simulations': 1,
            'total_validations': 1,
            'storage_used_gb': 0.5,
            'storage_limit_gb': 5.0
        }

    def _get_organization_user_statistics(self) -> Dict[str, Any]:
        """Get statistics for organization user."""
        return {
            'total_models': 2,
            'active_simulations': 1,
            'completed_simulations': 1,
            'total_validations': 2,
            'storage_used_gb': 1.2,
            'storage_limit_gb': 10.0 if self.role in ['admin', 'manager'] else 10.0
        }

    def _can_access_independent_model(self, model_id: str) -> bool:
        """Check if independent user can access a specific model."""
        # Mock implementation - replace with actual database query
        return model_id == 'model_001'  # Only their own model

    def _can_access_organization_model(self, model_id: str) -> bool:
        """Check if organization user can access a specific model."""
        # Mock implementation - replace with actual database query
        # Organization members can access any model in their organization
        return model_id in ['model_001', 'model_002']

