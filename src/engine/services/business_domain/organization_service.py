"""
Organization Service - Business Domain Service
============================================

Manages organizational structures, departments, hierarchies, and relationships.
This service provides comprehensive organization management capabilities.

Features:
- Organization creation and management
- Department hierarchy management
- Role and responsibility assignment
- Organizational structure validation
- Cross-organization relationships
"""

import logging
import asyncio
import json
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from ..base import BaseService
from ...models.base_model import BaseModel
from ...repositories.base_repository import BaseRepository
from ...models.enums import EventType, SystemCategory, SecurityLevel

logger = logging.getLogger(__name__)


class OrganizationType(Enum):
    """Types of organizations."""
    COMPANY = "company"
    DEPARTMENT = "department"
    TEAM = "team"
    DIVISION = "division"
    SUBSIDIARY = "subsidiary"
    PARTNER = "partner"


class OrganizationStatus(Enum):
    """Organization status values."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    MERGED = "merged"
    DISSOLVED = "dissolved"


@dataclass
class OrganizationInfo:
    """Organization information structure."""
    org_id: str
    name: str
    display_name: str
    org_type: OrganizationType
    status: OrganizationStatus
    parent_org_id: Optional[str]
    description: Optional[str]
    founded_date: Optional[datetime]
    website: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    address: Optional[Dict[str, str]]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass
class DepartmentInfo:
    """Department information structure."""
    dept_id: str
    name: str
    display_name: str
    org_id: str
    parent_dept_id: Optional[str]
    description: Optional[str]
    manager_id: Optional[str]
    budget: Optional[float]
    headcount: Optional[int]
    location: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class OrganizationService(BaseService[BaseModel, BaseRepository]):
    """
    Business domain service for organization management.
    
    Provides:
    - Organization CRUD operations
    - Department management
    - Organizational hierarchy management
    - Cross-organization relationships
    - Validation and business rules
    """

    def __init__(self, repository: Optional[BaseRepository] = None):
        super().__init__(repository, "OrganizationService")
        
        # Organization storage
        self._organizations: Dict[str, OrganizationInfo] = {}
        self._departments: Dict[str, DepartmentInfo] = {}
        
        # Hierarchy tracking
        self._org_hierarchy: Dict[str, Set[str]] = {}  # parent -> children
        self._dept_hierarchy: Dict[str, Set[str]] = {}  # parent -> children
        
        # Validation rules
        self._validation_rules = {
            'max_hierarchy_depth': 10,
            'max_departments_per_org': 100,
            'max_employees_per_dept': 1000
        }
        
        logger.info("Organization service initialized")

    async def _initialize_service_resources(self) -> None:
        """Initialize organization service resources."""
        # Load existing organizations from repository
        await self._load_organizations()
        
        # Build hierarchy indexes
        await self._build_hierarchy_indexes()
        
        logger.info("Organization service resources initialized")

    async def _cleanup_service_resources(self) -> None:
        """Cleanup organization service resources."""
        # Save organizations to repository
        await self._save_organizations()
        
        # Clear in-memory data
        self._organizations.clear()
        self._departments.clear()
        self._org_hierarchy.clear()
        self._dept_hierarchy.clear()
        
        logger.info("Organization service resources cleaned up")

    async def get_service_info(self) -> Dict[str, Any]:
        """Get organization service information."""
        return {
            'service_name': self.service_name,
            'total_organizations': len(self._organizations),
            'total_departments': len(self._departments),
            'org_types': [t.value for t in OrganizationType],
            'health_status': self.health_status,
            'uptime': str(self.get_uptime()),
            'last_health_check': self.last_health_check.isoformat()
        }

    # Organization Management

    async def create_organization(self, name: str, org_type: OrganizationType,
                                display_name: str = None, description: str = None,
                                parent_org_id: str = None, **kwargs) -> Optional[str]:
        """
        Create a new organization.
        
        Args:
            name: Organization name
            org_type: Type of organization
            display_name: Human-readable display name
            description: Organization description
            parent_org_id: Parent organization ID
            **kwargs: Additional organization properties
            
        Returns:
            Organization ID if successful, None otherwise
        """
        try:
            # Validate organization data
            if not await self._validate_organization_data(name, org_type, parent_org_id):
                return None
            
            # Generate organization ID
            org_id = f"org_{name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create organization info
            org_info = OrganizationInfo(
                org_id=org_id,
                name=name,
                display_name=display_name or name,
                org_type=org_type,
                status=OrganizationStatus.ACTIVE,
                parent_org_id=parent_org_id,
                description=description,
                founded_date=kwargs.get('founded_date'),
                website=kwargs.get('website'),
                contact_email=kwargs.get('contact_email'),
                contact_phone=kwargs.get('contact_phone'),
                address=kwargs.get('address'),
                metadata=kwargs.get('metadata', {}),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Store organization
            self._organizations[org_id] = org_info
            
            # Update hierarchy
            if parent_org_id:
                if parent_org_id not in self._org_hierarchy:
                    self._org_hierarchy[parent_org_id] = set()
                self._org_hierarchy[parent_org_id].add(org_id)
            
            # Log audit event
            await self.log_audit_event(
                EventType.ORG_CREATED,
                SystemCategory.APPLICATION,
                f"Organization created: {name}",
                {'org_id': org_id, 'org_type': org_type.value},
                SecurityLevel.INTERNAL
            )
            
            logger.info(f"Organization created: {org_id} ({name})")
            return org_id
            
        except Exception as e:
            logger.error(f"Failed to create organization {name}: {e}")
            return None

    async def get_organization(self, org_id: str) -> Optional[OrganizationInfo]:
        """Get organization by ID."""
        try:
            return self._organizations.get(org_id)
        except Exception as e:
            logger.error(f"Failed to get organization {org_id}: {e}")
            return None

    async def update_organization(self, org_id: str, **kwargs) -> bool:
        """Update organization information."""
        try:
            if org_id not in self._organizations:
                logger.warning(f"Organization {org_id} not found")
                return False
            
            org_info = self._organizations[org_id]
            
            # Update allowed fields
            allowed_fields = {
                'display_name', 'description', 'status', 'website',
                'contact_email', 'contact_phone', 'address', 'metadata'
            }
            
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(org_info, field):
                    setattr(org_info, field, value)
            
            org_info.updated_at = datetime.now()
            
            # Log audit event
            await self.log_audit_event(
                EventType.ORG_UPDATED,
                SystemCategory.APPLICATION,
                f"Organization updated: {org_id}",
                {'org_id': org_id, 'updated_fields': list(kwargs.keys())},
                SecurityLevel.INTERNAL
            )
            
            logger.info(f"Organization updated: {org_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update organization {org_id}: {e}")
            return False

    async def delete_organization(self, org_id: str) -> bool:
        """Delete an organization."""
        try:
            if org_id not in self._organizations:
                logger.warning(f"Organization {org_id} not found")
                return False
            
            # Check if organization has children
            if org_id in self._org_hierarchy and self._org_hierarchy[org_id]:
                logger.warning(f"Cannot delete organization {org_id} with children")
                return False
            
            # Check if organization has departments
            org_departments = [d for d in self._departments.values() if d.org_id == org_id]
            if org_departments:
                logger.warning(f"Cannot delete organization {org_id} with departments")
                return False
            
            # Remove from parent hierarchy
            org_info = self._organizations[org_id]
            if org_info.parent_org_id and org_info.parent_org_id in self._org_hierarchy:
                self._org_hierarchy[org_info.parent_org_id].discard(org_id)
            
            # Delete organization
            del self._organizations[org_id]
            
            # Log audit event
            await self.log_audit_event(
                EventType.ORG_DELETED,
                SystemCategory.APPLICATION,
                f"Organization deleted: {org_id}",
                {'org_id': org_id},
                SecurityLevel.INTERNAL
            )
            
            logger.info(f"Organization deleted: {org_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete organization {org_id}: {e}")
            return False

    # Department Management

    async def create_department(self, name: str, org_id: str,
                              display_name: str = None, description: str = None,
                              parent_dept_id: str = None, **kwargs) -> Optional[str]:
        """
        Create a new department.
        
        Args:
            name: Department name
            org_id: Parent organization ID
            display_name: Human-readable display name
            description: Department description
            parent_dept_id: Parent department ID
            **kwargs: Additional department properties
            
        Returns:
            Department ID if successful, None otherwise
        """
        try:
            # Validate department data
            if not await self._validate_department_data(name, org_id, parent_dept_id):
                return None
            
            # Generate department ID
            dept_id = f"dept_{name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create department info
            dept_info = DepartmentInfo(
                dept_id=dept_id,
                name=name,
                display_name=display_name or name,
                org_id=org_id,
                parent_dept_id=parent_dept_id,
                description=description,
                manager_id=kwargs.get('manager_id'),
                budget=kwargs.get('budget'),
                headcount=kwargs.get('headcount'),
                location=kwargs.get('location'),
                metadata=kwargs.get('metadata', {}),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Store department
            self._departments[dept_id] = dept_info
            
            # Update hierarchy
            if parent_dept_id:
                if parent_dept_id not in self._dept_hierarchy:
                    self._dept_hierarchy[parent_dept_id] = set()
                self._dept_hierarchy[parent_dept_id].add(dept_id)
            
            # Log audit event
            await self.log_audit_event(
                EventType.ORG_CREATED,
                SystemCategory.APPLICATION,
                f"Department created: {name}",
                {'dept_id': dept_id, 'org_id': org_id},
                SecurityLevel.INTERNAL
            )
            
            logger.info(f"Department created: {dept_id} ({name})")
            return dept_id
            
        except Exception as e:
            logger.error(f"Failed to create department {name}: {e}")
            return None

    async def get_department(self, dept_id: str) -> Optional[DepartmentInfo]:
        """Get department by ID."""
        try:
            return self._departments.get(dept_id)
        except Exception as e:
            logger.error(f"Failed to get department {dept_id}: {e}")
            return None

    async def get_organization_departments(self, org_id: str) -> List[DepartmentInfo]:
        """Get all departments for an organization."""
        try:
            return [d for d in self._departments.values() if d.org_id == org_id]
        except Exception as e:
            logger.error(f"Failed to get departments for organization {org_id}: {e}")
            return []

    # Hierarchy Management

    async def get_organization_hierarchy(self, org_id: str) -> Dict[str, Any]:
        """Get complete hierarchy for an organization."""
        try:
            if org_id not in self._organizations:
                return {}
            
            def build_hierarchy(org_id: str, visited: Set[str] = None) -> Dict[str, Any]:
                if visited is None:
                    visited = set()
                
                if org_id in visited:
                    return {}
                
                visited.add(org_id)
                org_info = self._organizations[org_id]
                
                hierarchy = {
                    'org_id': org_id,
                    'name': org_info.name,
                    'type': org_info.org_type.value,
                    'status': org_info.status.value,
                    'children': []
                }
                
                # Add child organizations
                if org_id in self._org_hierarchy:
                    for child_org_id in self._org_hierarchy[org_id]:
                        child_hierarchy = build_hierarchy(child_org_id, visited)
                        if child_hierarchy:
                            hierarchy['children'].append(child_hierarchy)
                
                # Add departments
                org_departments = [d for d in self._departments.values() if d.org_id == org_id]
                if org_departments:
                    hierarchy['departments'] = [
                        {
                            'dept_id': d.dept_id,
                            'name': d.name,
                            'parent_dept_id': d.parent_dept_id
                        }
                        for d in org_departments
                    ]
                
                return hierarchy
            
            return build_hierarchy(org_id)
            
        except Exception as e:
            logger.error(f"Failed to get hierarchy for organization {org_id}: {e}")
            return {}

    # Validation Methods

    async def _validate_organization_data(self, name: str, org_type: OrganizationType,
                                        parent_org_id: str = None) -> bool:
        """Validate organization data before creation."""
        try:
            # Check name uniqueness
            for org in self._organizations.values():
                if org.name.lower() == name.lower():
                    logger.warning(f"Organization name '{name}' already exists")
                    return False
            
            # Check parent organization exists
            if parent_org_id and parent_org_id not in self._organizations:
                logger.warning(f"Parent organization {parent_org_id} not found")
                return False
            
            # Check hierarchy depth
            if parent_org_id:
                depth = await self._calculate_hierarchy_depth(parent_org_id)
                if depth >= self._validation_rules['max_hierarchy_depth']:
                    logger.warning(f"Maximum hierarchy depth exceeded for {parent_org_id}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Organization validation error: {e}")
            return False

    async def _validate_department_data(self, name: str, org_id: str,
                                      parent_dept_id: str = None) -> bool:
        """Validate department data before creation."""
        try:
            # Check organization exists
            if org_id not in self._organizations:
                logger.warning(f"Organization {org_id} not found")
                return False
            
            # Check name uniqueness within organization
            org_departments = [d for d in self._departments.values() if d.org_id == org_id]
            for dept in org_departments:
                if dept.name.lower() == name.lower():
                    logger.warning(f"Department name '{name}' already exists in organization {org_id}")
                    return False
            
            # Check parent department exists and belongs to same organization
            if parent_dept_id:
                if parent_dept_id not in self._departments:
                    logger.warning(f"Parent department {parent_dept_id} not found")
                    return False
                
                parent_dept = self._departments[parent_dept_id]
                if parent_dept.org_id != org_id:
                    logger.warning(f"Parent department {parent_dept_id} does not belong to organization {org_id}")
                    return False
            
            # Check department limit per organization
            if len(org_departments) >= self._validation_rules['max_departments_per_org']:
                logger.warning(f"Maximum departments per organization exceeded for {org_id}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Department validation error: {e}")
            return False

    async def _calculate_hierarchy_depth(self, org_id: str, visited: Set[str] = None) -> int:
        """Calculate hierarchy depth for an organization."""
        try:
            if visited is None:
                visited = set()
            
            if org_id in visited:
                return 0
            
            visited.add(org_id)
            
            if org_id not in self._org_hierarchy or not self._org_hierarchy[org_id]:
                return 1
            
            max_depth = 1
            for child_id in self._org_hierarchy[org_id]:
                child_depth = await self._calculate_hierarchy_depth(child_id, visited)
                max_depth = max(max_depth, child_depth + 1)
            
            return max_depth
            
        except Exception as e:
            logger.error(f"Failed to calculate hierarchy depth for {org_id}: {e}")
            return 1

    # Data Loading and Saving

    async def _load_organizations(self) -> None:
        """Load organizations and departments from repository."""
        try:
            logger.info("Loading organizations and departments from repository")
            
            # Load organizations from database
            if self.repository and hasattr(self.repository, 'get_all_organizations'):
                orgs = await self.repository.get_all_organizations()
                for org in orgs:
                    # Convert database model to service model
                    org_info = OrganizationInfo(
                        org_id=org.org_id,
                        name=org.name,
                        display_name=org.name,  # Use name as display name if not available
                        org_type=OrganizationType(org.org_type) if hasattr(org, 'org_type') else OrganizationType.COMPANY,
                        status=OrganizationStatus(org.status) if hasattr(org, 'status') else OrganizationStatus.ACTIVE,
                        parent_org_id=org.parent_org_id,
                        description=org.description,
                        founded_date=datetime.fromisoformat(org.founded_date) if hasattr(org, 'founded_date') and org.founded_date else None,
                        website=org.website,
                        contact_email=org.contact_email,
                        contact_phone=org.contact_phone,
                        address=org.address,
                        metadata=json.loads(org.metadata) if hasattr(org, 'metadata') and org.metadata else {},
                        created_at=datetime.fromisoformat(org.created_at),
                        updated_at=datetime.fromisoformat(org.updated_at)
                    )
                    self._organizations[org.org_id] = org_info
            
            # Load departments from database
            if self.repository and hasattr(self.repository, 'get_all_departments'):
                depts = await self.repository.get_all_departments()
                for dept in depts:
                    # Convert database model to service model
                    dept_info = DepartmentInfo(
                        dept_id=dept.dept_id,
                        name=dept.name,
                        display_name=dept.display_name,
                        org_id=dept.org_id,
                        parent_dept_id=dept.parent_dept_id,
                        description=dept.description,
                        manager_id=dept.manager_id,
                        budget=dept.budget,
                        headcount=dept.headcount,
                        location=dept.location,
                        metadata=json.loads(dept.metadata) if hasattr(dept, 'metadata') and dept.metadata else {},
                        created_at=datetime.fromisoformat(dept.created_at),
                        updated_at=datetime.fromisoformat(dept.updated_at)
                    )
                    self._departments[dept.dept_id] = dept_info
            
            logger.info(f"Loaded {len(self._organizations)} organizations and {len(self._departments)} departments")
            
        except Exception as e:
            logger.error(f"Failed to load organizations and departments: {e}")

    async def _save_organizations(self) -> None:
        """Save organizations and departments to repository."""
        try:
            logger.info("Saving organizations and departments to repository")
            
            # Save organizations to database
            if self.repository and hasattr(self.repository, 'create_organization'):
                for org_info in self._organizations.values():
                    # Convert service model to database model
                    org_data = {
                        'org_id': org_info.org_id,
                        'name': org_info.name,
                        'description': org_info.description,
                        'parent_org_id': org_info.parent_org_id,
                        'contact_email': org_info.contact_email,
                        'contact_phone': org_info.contact_phone,
                        'address': json.dumps(org_info.address) if org_info.address else None,
                        'is_active': org_info.status == OrganizationStatus.ACTIVE,
                        'created_at': org_info.created_at.isoformat(),
                        'updated_at': org_info.updated_at.isoformat(),
                        'metadata': json.dumps(org_info.metadata)
                    }
                    await self.repository.create_organization(org_data)
            
            # Save departments to database
            if self.repository and hasattr(self.repository, 'create_department'):
                for dept_info in self._departments.values():
                    # Convert service model to database model
                    dept_data = {
                        'dept_id': dept_info.dept_id,
                        'name': dept_info.name,
                        'display_name': dept_info.display_name,
                        'org_id': dept_info.org_id,
                        'parent_dept_id': dept_info.parent_dept_id,
                        'description': dept_info.description,
                        'manager_id': dept_info.manager_id,
                        'budget': dept_info.budget,
                        'headcount': dept_info.headcount,
                        'location': dept_info.location,
                        'is_active': True,  # Default to active
                        'created_at': dept_info.created_at.isoformat(),
                        'updated_at': dept_info.updated_at.isoformat(),
                        'metadata': json.dumps(dept_info.metadata)
                    }
                    await self.repository.create_department(dept_data)
            
            logger.info(f"Saved {len(self._organizations)} organizations and {len(self._departments)} departments")
            
        except Exception as e:
            logger.error(f"Failed to save organizations and departments: {e}")

    async def _build_hierarchy_indexes(self) -> None:
        """Build hierarchy indexes from loaded data."""
        try:
            # Build organization hierarchy
            for org_id, org_info in self._organizations.items():
                if org_info.parent_org_id:
                    if org_info.parent_org_id not in self._org_hierarchy:
                        self._org_hierarchy[org_info.parent_org_id] = set()
                    self._org_hierarchy[org_info.parent_org_id].add(org_id)
            
            # Build department hierarchy
            for dept_id, dept_info in self._departments.items():
                if dept_info.parent_dept_id:
                    if dept_info.parent_dept_id not in self._dept_hierarchy:
                        self._dept_hierarchy[dept_info.parent_dept_id] = set()
                    self._dept_hierarchy[dept_info.parent_dept_id].add(dept_id)
            
            logger.info("Hierarchy indexes built successfully")
            
        except Exception as e:
            logger.error(f"Failed to build hierarchy indexes: {e}")

    # Business Intelligence

    async def get_organization_statistics(self) -> Dict[str, Any]:
        """Get comprehensive organization statistics."""
        try:
            stats = {
                'total_organizations': len(self._organizations),
                'total_departments': len(self._departments),
                'organization_types': {},
                'status_distribution': {},
                'hierarchy_depth_stats': {},
                'department_distribution': {}
            }
            
            # Count by organization type
            for org in self._organizations.values():
                org_type = org.org_type.value
                stats['organization_types'][org_type] = stats['organization_types'].get(org_type, 0) + 1
            
            # Count by status
            for org in self._organizations.values():
                status = org.status.value
                stats['status_distribution'][status] = stats['status_distribution'].get(status, 0) + 1
            
            # Calculate hierarchy depths
            depths = []
            for org_id in self._organizations:
                depth = await self._calculate_hierarchy_depth(org_id)
                depths.append(depth)
            
            if depths:
                stats['hierarchy_depth_stats'] = {
                    'min': min(depths),
                    'max': max(depths),
                    'average': sum(depths) / len(depths)
                }
            
            # Count departments per organization
            dept_counts = {}
            for dept in self._departments.values():
                org_id = dept.org_id
                dept_counts[org_id] = dept_counts.get(org_id, 0) + 1
            
            if dept_counts:
                stats['department_distribution'] = {
                    'min': min(dept_counts.values()),
                    'max': max(dept_counts.values()),
                    'average': sum(dept_counts.values()) / len(dept_counts)
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get organization statistics: {e}")
            return {'error': str(e)}
