"""
Twin Registry Organization Service
==================================

This service handles all organization-based data operations for the Twin Registry module,
supporting multi-tenancy and organization-specific data management.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.engine.models.request_context import UserContext

logger = logging.getLogger(__name__)


class TwinRegistryOrganizationService:
    """
    Service for handling organization-based twin registry operations.
    
    This service provides organization-specific data access, filtering, and management
    for multi-tenant support.
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
        
        logger.info(f"Initialized TwinRegistryOrganizationService for user {self.user_id} "
                   f"(type: {self.user_type}, independent: {self.is_independent})")
    
    def get_organization_twins(self) -> List[Dict[str, Any]]:
        """
        Get all twins for the organization.
        
        Returns:
            List of twins belonging to the organization
        """
        try:
            if self.is_independent:
                return []
            
            # This would call the actual twin registry service to get organization twins
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Error getting organization twins: {e}")
            raise Exception(f"Failed to get organization twins: {str(e)}")
    
    def get_organization_twin_relationships(self) -> List[Dict[str, Any]]:
        """
        Get all twin relationships for the organization.
        
        Returns:
            List of twin relationships belonging to the organization
        """
        try:
            if self.is_independent:
                return []
            
            # This would call the actual twin registry service to get organization relationships
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Error getting organization twin relationships: {e}")
            raise Exception(f"Failed to get organization twin relationships: {str(e)}")
    
    def get_organization_twin_instances(self) -> List[Dict[str, Any]]:
        """
        Get all twin instances for the organization.
        
        Returns:
            List of twin instances belonging to the organization
        """
        try:
            if self.is_independent:
                return []
            
            # This would call the actual twin registry service to get organization instances
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Error getting organization twin instances: {e}")
            raise Exception(f"Failed to get organization twin instances: {str(e)}")
    
    def get_organization_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics for the organization.
        
        Returns:
            Dictionary containing organization statistics
        """
        try:
            if self.is_independent:
                return {
                    "organization_name": None,
                    "organization_id": None,
                    "total_twins": 0,
                    "total_relationships": 0,
                    "total_instances": 0,
                    "active_twins": 0,
                    "inactive_twins": 0,
                    "user_type": "independent",
                    "is_independent": True
                }
            
            org_twins = self.get_organization_twins()
            org_relationships = self.get_organization_twin_relationships()
            org_instances = self.get_organization_twin_instances()
            
            stats = {
                "organization_name": getattr(self.user_context, 'organization_name', 'Unknown'),
                "organization_id": self.organization_id,
                "total_twins": len(org_twins),
                "total_relationships": len(org_relationships),
                "total_instances": len(org_instances),
                "active_twins": len([t for t in org_twins if t.get('status') == 'active']),
                "inactive_twins": len([t for t in org_twins if t.get('status') == 'inactive']),
                "user_type": self.user_type,
                "is_independent": False,
                "organization_member_count": self._get_organization_member_count(),
                "organization_storage_usage": self._get_organization_storage_usage(),
                "organization_limits": self._get_organization_limits()
            }
            
            return stats
        except Exception as e:
            logger.error(f"Error getting organization statistics: {e}")
            raise Exception(f"Failed to get organization statistics: {str(e)}")
    
    def get_organization_members(self) -> List[Dict[str, Any]]:
        """
        Get organization members with their twin registry access.
        
        Returns:
            List of organization members and their access levels
        """
        try:
            if self.is_independent:
                return []
            
            # This would call the user management service to get organization members
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Error getting organization members: {e}")
            raise Exception(f"Failed to get organization members: {str(e)}")
    
    def can_manage_organization(self) -> bool:
        """
        Check if the current user can manage the organization.
        
        Returns:
            True if user can manage organization, False otherwise
        """
        try:
            user_role = getattr(self.user_context, 'role', 'viewer')
            if user_role == "super_admin":
                return True
            if user_role == "admin" and not self.is_independent:
                return True
            return False
        except Exception as e:
            logger.error(f"Error checking organization management permissions: {e}")
            return False
    
    def get_organization_settings(self) -> Dict[str, Any]:
        """
        Get organization settings for twin registry.
        
        Returns:
            Dictionary containing organization settings
        """
        try:
            if self.is_independent:
                return {
                    "max_twins": 10,
                    "max_relationships": 50,
                    "max_instances": 100,
                    "storage_limit_gb": 5,
                    "allow_public_twins": False,
                    "allow_cross_organization_sharing": False
                }
            
            # This would call the organization settings service
            # For now, return default organization settings
            return {
                "max_twins": 100,
                "max_relationships": 500,
                "max_instances": 1000,
                "storage_limit_gb": 100,
                "allow_public_twins": True,
                "allow_cross_organization_sharing": True,
                "organization_id": self.organization_id,
                "organization_name": getattr(self.user_context, 'organization_name', 'Unknown')
            }
        except Exception as e:
            logger.error(f"Error getting organization settings: {e}")
            raise Exception(f"Failed to get organization settings: {str(e)}")
    
    def update_organization_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update organization settings for twin registry.
        
        Args:
            settings: New settings to apply
            
        Returns:
            Updated settings
        """
        try:
            if not self.can_manage_organization():
                raise Exception("User does not have permission to manage organization")
            
            # This would call the organization settings service to update settings
            # For now, return the settings as if they were updated
            logger.info(f"Organization settings updated for organization {self.organization_id}")
            return settings
        except Exception as e:
            logger.error(f"Error updating organization settings: {e}")
            raise Exception(f"Failed to update organization settings: {str(e)}")
    
    def get_organization_health(self) -> Dict[str, Any]:
        """
        Get organization-wide health status.
        
        Returns:
            Dictionary containing organization health information
        """
        try:
            if self.is_independent:
                return {
                    "status": "independent_user",
                    "message": "Independent users do not have organization health metrics"
                }
            
            org_twins = self.get_organization_twins()
            
            # Calculate health metrics
            total_twins = len(org_twins)
            active_twins = len([t for t in org_twins if t.get('status') == 'active'])
            inactive_twins = len([t for t in org_twins if t.get('status') == 'inactive'])
            
            health_score = (active_twins / total_twins * 100) if total_twins > 0 else 100
            
            return {
                "status": "healthy" if health_score >= 80 else "warning" if health_score >= 60 else "critical",
                "health_score": health_score,
                "total_twins": total_twins,
                "active_twins": active_twins,
                "inactive_twins": inactive_twins,
                "organization_id": self.organization_id,
                "organization_name": getattr(self.user_context, 'organization_name', 'Unknown'),
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting organization health: {e}")
            raise Exception(f"Failed to get organization health: {str(e)}")
    
    def get_organization_performance(self) -> Dict[str, Any]:
        """
        Get organization-wide performance metrics.
        
        Returns:
            Dictionary containing organization performance information
        """
        try:
            if self.is_independent:
                return {
                    "status": "independent_user",
                    "message": "Independent users do not have organization performance metrics"
                }
            
            # This would call the performance monitoring service
            # For now, return basic performance structure
            return {
                "response_time_avg": 0.0,
                "throughput_per_minute": 0,
                "error_rate": 0.0,
                "uptime_percentage": 99.9,
                "organization_id": self.organization_id,
                "organization_name": getattr(self.user_context, 'organization_name', 'Unknown'),
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting organization performance: {e}")
            raise Exception(f"Failed to get organization performance: {str(e)}")
    
    # Private helper methods
    
    def _get_organization_member_count(self) -> int:
        """Get the number of members in the organization."""
        # This would call the user management service
        # For now, return a default value
        return 1
    
    def _get_organization_storage_usage(self) -> Dict[str, Any]:
        """Get organization storage usage."""
        # This would call the storage service
        # For now, return default values
        return {
            "used_gb": 0.0,
            "available_gb": 100.0,
            "total_gb": 100.0
        }
    
    def _get_organization_limits(self) -> Dict[str, Any]:
        """Get organization limits."""
        # This would call the organization settings service
        # For now, return default values
        return {
            "max_twins": 100,
            "max_relationships": 500,
            "max_instances": 1000,
            "storage_limit_gb": 100
        }

