"""
Twin Registry User-Specific Service
===================================

This service handles all user-specific data operations for the Twin Registry module,
distinguishing between independent users and organization members.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from webapp.core.context.user_context import UserContext

logger = logging.getLogger(__name__)


class TwinRegistryUserSpecificService:
    """
    Service for handling user-specific twin registry operations.
    
    This service provides user-specific data access, filtering, and management
    based on the user's context (independent vs organization member).
    """
    
    def __init__(self, user_context: UserContext):
        """
        Initialize the service with user context.
        
        Args:
            user_context: The authenticated user's context
        """
        self.user_context = user_context
        self.user_id = getattr(user_context, 'user_id', None)
        self.organization_id = getattr(user_context, 'organization_id', None)
        
        # Check if user is independent based on organization_id
        user_is_independent = getattr(user_context, 'is_independent', None)
        if user_is_independent is None:
            self.is_independent = self.organization_id is None
        else:
            self.is_independent = user_is_independent
            
        self.user_type = getattr(user_context, 'get_user_type', lambda: 'independent')()
        self.role = getattr(user_context, 'role', 'viewer')
        self.permissions = getattr(user_context, 'permissions', [])
        
        logger.info(f"Initialized TwinRegistryUserSpecificService for user {self.user_id} "
                   f"(type: {self.user_type}, independent: {self.is_independent})")
    
    def get_user_twins(self) -> List[Dict[str, Any]]:
        """
        Get twins for the current user based on user type.
        
        Returns:
            List of twins accessible to the current user
        """
        try:
            if self.is_independent:
                # Independent users only see their own twins
                return self._get_personal_twins()
            else:
                # Organization users see organization twins + personal twins
                org_twins = self._get_organization_twins()
                personal_twins = self._get_personal_twins()
                return org_twins + personal_twins
        except Exception as e:
            logger.error(f"Error getting user twins: {e}")
            raise Exception(f"Failed to get user twins: {str(e)}")
    
    def get_user_twin_relationships(self) -> List[Dict[str, Any]]:
        """
        Get twin relationships for the current user.
        
        Returns:
            List of twin relationships accessible to the current user
        """
        try:
            if self.is_independent:
                return self._get_personal_twin_relationships()
            else:
                org_relationships = self._get_organization_twin_relationships()
                personal_relationships = self._get_personal_twin_relationships()
                return org_relationships + personal_relationships
        except Exception as e:
            logger.error(f"Error getting user twin relationships: {e}")
            raise Exception(f"Failed to get user twin relationships: {str(e)}")
    
    def get_user_twin_instances(self) -> List[Dict[str, Any]]:
        """
        Get twin instances for the current user.
        
        Returns:
            List of twin instances accessible to the current user
        """
        try:
            if self.is_independent:
                return self._get_personal_twin_instances()
            else:
                org_instances = self._get_organization_twin_instances()
                personal_instances = self._get_personal_twin_instances()
                return org_instances + personal_instances
        except Exception as e:
            logger.error(f"Error getting user twin instances: {e}")
            raise Exception(f"Failed to get user twin instances: {str(e)}")
    
    def get_user_twin_statistics(self) -> Dict[str, Any]:
        """
        Get twin statistics for the current user.
        
        Returns:
            Dictionary containing user-specific twin statistics
        """
        try:
            user_twins = self.get_user_twins()
            user_relationships = self.get_user_twin_relationships()
            user_instances = self.get_user_twin_instances()
            
            stats = {
                "total_twins": len(user_twins),
                "total_relationships": len(user_relationships),
                "total_instances": len(user_instances),
                "active_twins": len([t for t in user_twins if t.get('status') == 'active']),
                "inactive_twins": len([t for t in user_twins if t.get('status') == 'inactive']),
                "user_id": self.user_id,
                "user_type": self.user_type,
                "role": self.role,
                "permissions": self.permissions,
                "is_independent": self.is_independent,
                "organization_id": self.organization_id
            }
            
            return stats
        except Exception as e:
            logger.error(f"Error getting user twin statistics: {e}")
            raise Exception(f"Failed to get user twin statistics: {str(e)}")
    
    def can_access_twin(self, twin_id: str) -> bool:
        """
        Check if the current user can access a specific twin.
        
        Args:
            twin_id: The ID of the twin to check access for
            
        Returns:
            True if user can access the twin, False otherwise
        """
        try:
            # Super admins can access all twins
            if self.role == "super_admin":
                return True
            
            # Get the twin to check ownership/organization
            twin = self._get_twin_by_id(twin_id)
            if not twin:
                return False
            
            # Check if user owns the twin
            if twin.get('created_by') == self.user_id:
                return True
            
            # Check if user is in the same organization
            if not self.is_independent and twin.get('organization_id') == self.organization_id:
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking twin access: {e}")
            return False
    
    def can_access_relationship(self, relationship_id: str) -> bool:
        """
        Check if the current user can access a specific relationship.
        
        Args:
            relationship_id: The ID of the relationship to check access for
            
        Returns:
            True if user can access the relationship, False otherwise
        """
        try:
            # Super admins can access all relationships
            if self.role == "super_admin":
                return True
            
            # Get the relationship to check access
            relationship = self._get_relationship_by_id(relationship_id)
            if not relationship:
                return False
            
            # Check if user can access both source and target twins
            source_twin_id = relationship.get('source_twin_id')
            target_twin_id = relationship.get('target_twin_id')
            
            return (self.can_access_twin(source_twin_id) and 
                   self.can_access_twin(target_twin_id))
        except Exception as e:
            logger.error(f"Error checking relationship access: {e}")
            return False
    
    def can_access_instance(self, instance_id: str) -> bool:
        """
        Check if the current user can access a specific instance.
        
        Args:
            instance_id: The ID of the instance to check access for
            
        Returns:
            True if user can access the instance, False otherwise
        """
        try:
            # Super admins can access all instances
            if self.role == "super_admin":
                return True
            
            # Get the instance to check access
            instance = self._get_instance_by_id(instance_id)
            if not instance:
                return False
            
            # Check if user can access the parent twin
            twin_id = instance.get('twin_id')
            return self.can_access_twin(twin_id)
        except Exception as e:
            logger.error(f"Error checking instance access: {e}")
            return False
    
    def create_user_twin(self, twin_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new twin for the current user.
        
        Args:
            twin_data: The twin data to create
            
        Returns:
            The created twin data
        """
        try:
            # Add user context to twin data
            twin_data['created_by'] = self.user_id
            twin_data['created_at'] = datetime.utcnow().isoformat()
            
            if self.is_independent:
                # Independent users don't have organization_id
                twin_data['organization_id'] = None
            else:
                twin_data['organization_id'] = self.organization_id
            
            # Create the twin (this would call the actual twin registry service)
            # For now, return the prepared data
            return twin_data
        except Exception as e:
            logger.error(f"Error creating user twin: {e}")
            raise Exception(f"Failed to create user twin: {str(e)}")
    
    def get_user_twin_limits(self) -> Dict[str, Any]:
        """
        Get twin creation limits for the current user.
        
        Returns:
            Dictionary containing user's twin limits
        """
        try:
            if self.is_independent:
                return {
                    "max_twins": 10,
                    "max_relationships": 50,
                    "max_instances": 100,
                    "limit_type": "personal",
                    "current_twins": len(self.get_user_twins()),
                    "current_relationships": len(self.get_user_twin_relationships()),
                    "current_instances": len(self.get_user_twin_instances())
                }
            else:
                return {
                    "max_twins": 100,
                    "max_relationships": 500,
                    "max_instances": 1000,
                    "limit_type": "organization",
                    "current_twins": len(self.get_user_twins()),
                    "current_relationships": len(self.get_user_twin_relationships()),
                    "current_instances": len(self.get_user_twin_instances())
                }
        except Exception as e:
            logger.error(f"Error getting user twin limits: {e}")
            raise Exception(f"Failed to get user twin limits: {str(e)}")
    
    # Private helper methods (these would integrate with actual twin registry services)
    
    def _get_personal_twins(self) -> List[Dict[str, Any]]:
        """Get personal twins for the current user."""
        # This would call the actual twin registry service
        # For now, return empty list
        return []
    
    def _get_organization_twins(self) -> List[Dict[str, Any]]:
        """Get organization twins for the current user."""
        # This would call the actual twin registry service
        # For now, return empty list
        return []
    
    def _get_personal_twin_relationships(self) -> List[Dict[str, Any]]:
        """Get personal twin relationships for the current user."""
        # This would call the actual twin registry service
        # For now, return empty list
        return []
    
    def _get_organization_twin_relationships(self) -> List[Dict[str, Any]]:
        """Get organization twin relationships for the current user."""
        # This would call the actual twin registry service
        # For now, return empty list
        return []
    
    def _get_personal_twin_instances(self) -> List[Dict[str, Any]]:
        """Get personal twin instances for the current user."""
        # This would call the actual twin registry service
        # For now, return empty list
        return []
    
    def _get_organization_twin_instances(self) -> List[Dict[str, Any]]:
        """Get organization twin instances for the current user."""
        # This would call the actual twin registry service
        # For now, return empty list
        return []
    
    def _get_twin_by_id(self, twin_id: str) -> Optional[Dict[str, Any]]:
        """Get a twin by ID."""
        # This would call the actual twin registry service
        # For now, return None
        return None
    
    def _get_relationship_by_id(self, relationship_id: str) -> Optional[Dict[str, Any]]:
        """Get a relationship by ID."""
        # This would call the actual twin registry service
        # For now, return None
        return None
    
    def _get_instance_by_id(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Get an instance by ID."""
        # This would call the actual twin registry service
        # For now, return None
        return None

