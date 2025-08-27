"""
Use Case Service - Business Domain Service
=========================================

Manages use cases, their categorization, project hierarchy, and validation.
This service provides comprehensive use case management capabilities.

Features:
- Use case creation and lifecycle management
- Category and domain management
- Project linking and hierarchy management
- Business criticality and compliance tracking
- Data governance and retention policies
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from ..base import BaseService
from ...models.base_model import BaseModel
from ...repositories.base_repository import BaseRepository
from ...models.enums import EventType, SystemCategory, SecurityLevel
from ...models.business_domain import UseCase, ProjectUseCaseLink
from ...repositories.business_domain_repository import BusinessDomainRepository

logger = logging.getLogger(__name__)


class UseCaseStatus(Enum):
    """Use case status values."""
    DRAFT = "draft"
    ACTIVE = "active"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class UseCaseCategory(Enum):
    """Use case category values."""
    GENERAL = "general"
    THERMAL = "thermal"
    STRUCTURAL = "structural"
    FLUID_DYNAMICS = "fluid_dynamics"
    ELECTRICAL = "electrical"
    MECHANICAL = "mechanical"
    CHEMICAL = "chemical"
    BIOLOGICAL = "biological"
    ENVIRONMENTAL = "environmental"
    OTHER = "other"


class BusinessCriticality(Enum):
    """Business criticality levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DataVolumeEstimate(Enum):
    """Data volume estimate levels."""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


class UpdateFrequency(Enum):
    """Update frequency values."""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ON_DEMAND = "on_demand"


@dataclass
class UseCaseInfo:
    """Use case information structure."""
    use_case_id: str
    name: str
    description: Optional[str]
    category: UseCaseCategory
    is_active: bool
    org_id: Optional[str]
    dept_id: Optional[str]
    data_domain: str
    business_criticality: BusinessCriticality
    data_volume_estimate: DataVolumeEstimate
    update_frequency: UpdateFrequency
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]


@dataclass
class UseCaseProjectLink:
    """Use case project link information."""
    link_id: str
    use_case_id: str
    project_id: str
    link_type: str
    created_at: datetime
    metadata: Dict[str, Any]


class UseCaseService(BaseService[UseCase, BusinessDomainRepository]):
    """Service for use case business logic and operations."""
    
    def __init__(self, repository: BusinessDomainRepository = None):
        """Initialize the use case service."""
        super().__init__(repository or BusinessDomainRepository())
        self._repository = repository or BusinessDomainRepository()
        logger.info("✅ Use case service initialized successfully")
    
    async def create_use_case(self, use_case_data: Dict[str, Any]) -> UseCase:
        """Create a new use case with business validation."""
        try:
            # Validate business rules
            self._validate_use_case_creation(use_case_data)
            
            # Create use case model
            use_case = UseCase(**use_case_data)
            
            # Create in repository
            created_use_case = await self._repository.create_use_case(use_case)
            
            logger.info(f"Created use case: {created_use_case.name} (ID: {created_use_case.use_case_id})")
            return created_use_case
            
        except Exception as e:
            logger.error(f"Error creating use case: {e}")
            raise
    
    async def get_use_case_by_id(self, use_case_id: str) -> Optional[UseCase]:
        """Get use case by ID."""
        try:
            use_case = await self._repository.get_use_case_by_id(use_case_id)
            if use_case:
                logger.debug(f"Retrieved use case: {use_case_id}")
            return use_case
            
        except Exception as e:
            logger.error(f"Error getting use case by ID: {e}")
            raise
    
    async def get_use_cases_by_organization(self, org_id: str) -> List[UseCase]:
        """Get all use cases for an organization."""
        try:
            use_cases = await self._repository.get_use_cases_by_organization(org_id)
            logger.debug(f"Retrieved {len(use_cases)} use cases for organization: {org_id}")
            return use_cases
            
        except Exception as e:
            logger.error(f"Error getting use cases by organization: {e}")
            raise
    
    async def get_use_cases_by_department(self, dept_id: str) -> List[UseCase]:
        """Get all use cases for a department."""
        try:
            use_cases = await self._repository.get_use_cases_by_department(dept_id)
            logger.debug(f"Retrieved {len(use_cases)} use cases for department: {dept_id}")
            return use_cases
            
        except Exception as e:
            logger.error(f"Error getting use cases by department: {e}")
            raise
    
    async def get_use_cases_by_domain(self, data_domain: str) -> List[UseCase]:
        """Get all use cases for a specific data domain."""
        try:
            use_cases = await self._repository.get_use_cases_by_domain(data_domain)
            logger.debug(f"Retrieved {len(use_cases)} use cases for domain: {data_domain}")
            return use_cases
            
        except Exception as e:
            logger.error(f"Error getting use cases by domain: {e}")
            raise
    
    async def update_use_case(self, use_case_id: str, update_data: Dict[str, Any]) -> Optional[UseCase]:
        """Update an existing use case."""
        try:
            # Get existing use case
            existing_use_case = await self.get_use_case_by_id(use_case_id)
            if not existing_use_case:
                logger.warning(f"Use case not found for update: {use_case_id}")
                return None
            
            # Validate update data
            self._validate_use_case_update(update_data)
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(existing_use_case, field):
                    setattr(existing_use_case, field, value)
            
            # Update timestamp
            existing_use_case.updated_at = datetime.utcnow().isoformat()
            
            # Save to repository
            updated_use_case = await self._repository.update_use_case(existing_use_case)
            
            logger.info(f"Updated use case: {use_case_id}")
            return updated_use_case
            
        except Exception as e:
            logger.error(f"Error updating use case: {e}")
            raise
    
    async def delete_use_case(self, use_case_id: str) -> bool:
        """Delete a use case."""
        try:
            # Check if use case exists
            existing_use_case = await self.get_use_case_by_id(use_case_id)
            if not existing_use_case:
                logger.warning(f"Use case not found for deletion: {use_case_id}")
                return False
            
            # Check if use case has linked projects
            project_links = await self._repository.get_links_by_use_case(use_case_id)
            if project_links:
                logger.warning(f"Cannot delete use case {use_case_id} - has {len(project_links)} linked projects")
                return False
            
            # Delete from repository
            success = await self._repository.delete_use_case(use_case_id)
            
            if success:
                logger.info(f"Deleted use case: {use_case_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting use case: {e}")
            raise
    
    async def get_use_case_with_projects(self, use_case_id: str) -> Optional[Dict[str, Any]]:
        """Get use case with all its linked projects."""
        try:
            # Get use case
            use_case = await self.get_use_case_by_id(use_case_id)
            if not use_case:
                return None
            
            # Get project links
            project_links = await self._repository.get_links_by_use_case(use_case_id)
            
            return {
                "use_case": use_case,
                "project_links": project_links,
                "project_count": len(project_links)
            }
            
        except Exception as e:
            logger.error(f"Error getting use case with projects: {e}")
            raise
    
    async def link_project_to_use_case(self, use_case_id: str, project_id: str, 
                                     link_type: str = "primary") -> ProjectUseCaseLink:
        """Link a project to a use case."""
        try:
            # Validate use case exists
            use_case = await self.get_use_case_by_id(use_case_id)
            if not use_case:
                raise ValueError(f"Use case not found: {use_case_id}")
            
            # Create project-use case link
            link_data = {
                "link_id": f"{use_case_id}_{project_id}",
                "use_case_id": use_case_id,
                "project_id": project_id,
                "link_type": link_type,
                "created_at": datetime.utcnow().isoformat(),
                "metadata": {}
            }
            
            link = ProjectUseCaseLink(**link_data)
            created_link = await self._repository.create_project_use_case_link(link)
            
            logger.info(f"Linked project {project_id} to use case {use_case_id}")
            return created_link
            
        except Exception as e:
            logger.error(f"Error linking project to use case: {e}")
            raise
    
    async def unlink_project_from_use_case(self, use_case_id: str, project_id: str) -> bool:
        """Unlink a project from a use case."""
        try:
            # Find the link
            project_links = await self._repository.get_links_by_use_case(use_case_id)
            target_link = None
            
            for link in project_links:
                if link.project_id == project_id:
                    target_link = link
                    break
            
            if not target_link:
                logger.warning(f"Project {project_id} not linked to use case {use_case_id}")
                return False
            
            # Delete the link
            success = await self._repository.delete_project_use_case_link(target_link.link_id)
            
            if success:
                logger.info(f"Unlinked project {project_id} from use case {use_case_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error unlinking project from use case: {e}")
            raise
    
    async def get_use_case_statistics(self, org_id: str = None) -> Dict[str, Any]:
        """Get comprehensive statistics for use cases."""
        try:
            stats = {
                "total_use_cases": 0,
                "active_use_cases": 0,
                "use_cases_by_category": {},
                "use_cases_by_domain": {},
                "use_cases_by_criticality": {},
                "recent_use_cases": [],
                "organization_id": org_id
            }
            
            # Get use cases
            if org_id:
                use_cases = await self.get_use_cases_by_organization(org_id)
            else:
                # Get all use cases (this would need a method in repository)
                use_cases = []
            
            stats["total_use_cases"] = len(use_cases)
            stats["active_use_cases"] = len([uc for uc in use_cases if uc.is_active])
            
            # Categorize by category
            for use_case in use_cases:
                category = use_case.category or "general"
                if category not in stats["use_cases_by_category"]:
                    stats["use_cases_by_category"][category] = 0
                stats["use_cases_by_category"][category] += 1
                
                # Categorize by domain
                domain = use_case.data_domain or "general"
                if domain not in stats["use_cases_by_domain"]:
                    stats["use_cases_by_domain"][domain] = 0
                stats["use_cases_by_domain"][domain] += 1
                
                # Categorize by criticality
                criticality = use_case.business_criticality or "low"
                if criticality not in stats["use_cases_by_criticality"]:
                    stats["use_cases_by_criticality"][criticality] = 0
                stats["use_cases_by_criticality"][criticality] += 1
            
            # Get recent use cases (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_use_cases = [
                uc for uc in use_cases 
                if datetime.fromisoformat(uc.created_at) > thirty_days_ago
            ]
            stats["recent_use_cases"] = [
                {"id": uc.use_case_id, "name": uc.name, "created_at": uc.created_at}
                for uc in recent_use_cases[:10]  # Top 10
            ]
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting use case statistics: {e}")
            raise
    
    def _validate_use_case_creation(self, use_case_data: Dict[str, Any]):
        """Validate use case creation data."""
        required_fields = ["use_case_id", "name"]
        for field in required_fields:
            if field not in use_case_data or not use_case_data[field]:
                raise ValueError(f"Required field missing: {field}")
        
        # Validate category if provided
        if "category" in use_case_data and use_case_data["category"]:
            valid_categories = [cat.value for cat in UseCaseCategory]
            if use_case_data["category"] not in valid_categories:
                raise ValueError(f"Invalid category. Must be one of: {valid_categories}")
        
        # Validate data domain if provided
        if "data_domain" in use_case_data and use_case_data["data_domain"]:
            valid_domains = [domain.value for domain in UseCaseCategory]
            if use_case_data["data_domain"] not in valid_domains:
                raise ValueError(f"Invalid data domain. Must be one of: {valid_domains}")
        
        # Validate business criticality if provided
        if "business_criticality" in use_case_data and use_case_data["business_criticality"]:
            valid_criticalities = [crit.value for crit in BusinessCriticality]
            if use_case_data["business_criticality"] not in valid_criticalities:
                raise ValueError(f"Invalid business criticality. Must be one of: {valid_criticalities}")
    
    def _validate_use_case_update(self, update_data: Dict[str, Any]):
        """Validate use case update data."""
        # Validate category if provided
        if "category" in update_data and update_data["category"]:
            valid_categories = [cat.value for cat in UseCaseCategory]
            if update_data["category"] not in valid_categories:
                raise ValueError(f"Invalid category. Must be one of: {valid_categories}")
        
        # Validate data domain if provided
        if "data_domain" in update_data and update_data["data_domain"]:
            valid_domains = [domain.value for domain in UseCaseCategory]
            if update_data["data_domain"] not in valid_domains:
                raise ValueError(f"Invalid data domain. Must be one of: {valid_domains}")
        
        # Validate business criticality if provided
        if "business_criticality" in update_data and update_data["business_criticality"]:
            valid_criticalities = [crit.value for crit in BusinessCriticality]
            if update_data["business_criticality"] not in valid_criticalities:
                raise ValueError(f"Invalid business criticality. Must be one of: {valid_criticalities}")
    
    async def search_use_cases(self, search_term: str, org_id: str = None) -> List[UseCase]:
        """Search use cases by name or description."""
        try:
            if not search_term or len(search_term.strip()) < 2:
                raise ValueError("Search term must be at least 2 characters")
            
            # Get use cases for organization
            if org_id:
                use_cases = await self.get_use_cases_by_organization(org_id)
            else:
                # This would need a method to get all use cases
                use_cases = []
            
            # Simple text search
            search_term_lower = search_term.lower()
            matching_use_cases = []
            
            for use_case in use_cases:
                if (search_term_lower in use_case.name.lower() or
                    (use_case.description and search_term_lower in use_case.description.lower())):
                    matching_use_cases.append(use_case)
            
            logger.debug(f"Found {len(matching_use_cases)} use cases matching '{search_term}'")
            return matching_use_cases
            
        except Exception as e:
            logger.error(f"Error searching use cases: {e}")
            raise
    
    async def get_use_case_templates(self) -> List[Dict[str, Any]]:
        """Get predefined use case templates."""
        templates = [
            {
                "name": "Thermal Analysis",
                "category": "thermal",
                "data_domain": "thermal",
                "business_criticality": "medium",
                "data_volume_estimate": "medium",
                "update_frequency": "daily",
                "description": "Standard template for thermal analysis use cases"
            },
            {
                "name": "Structural Analysis",
                "category": "structural",
                "data_domain": "structural",
                "business_criticality": "high",
                "data_volume_estimate": "large",
                "update_frequency": "weekly",
                "description": "Standard template for structural analysis use cases"
            },
            {
                "name": "Fluid Dynamics",
                "category": "fluid_dynamics",
                "data_domain": "fluid_dynamics",
                "business_criticality": "medium",
                "data_volume_estimate": "large",
                "update_frequency": "real_time",
                "description": "Standard template for fluid dynamics use cases"
            },
            {
                "name": "General Purpose",
                "category": "general",
                "data_domain": "general",
                "business_criticality": "low",
                "data_volume_estimate": "small",
                "update_frequency": "on_demand",
                "description": "General purpose use case template"
            }
        ]
        
        return templates
