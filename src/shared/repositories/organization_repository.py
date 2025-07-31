"""
Organization Repository
======================

Data access layer for organizations in the AAS Data Modeling framework.
"""

from typing import List, Optional, Dict, Any
from ..database.base_manager import BaseDatabaseManager
from ..models.organization import Organization
from .base_repository import BaseRepository

class OrganizationRepository(BaseRepository[Organization]):
    """Repository for organization operations."""
    
    def __init__(self, db_manager: BaseDatabaseManager):
        super().__init__(db_manager, Organization)
    
    def _get_table_name(self) -> str:
        return "organizations"
    
    def _get_columns(self) -> List[str]:
        return [
            "id", "name", "description", "domain", "contact_email", "contact_phone",
            "address", "is_active", "subscription_tier", "max_users", "max_projects",
            "max_storage_gb", "created_at", "updated_at"
        ]
    
    def get_by_name(self, name: str) -> Optional[Organization]:
        """Get organization by name."""
        query = "SELECT * FROM organizations WHERE name = ?"
        results = self.db_manager.execute_query(query, (name,))
        if results:
            return self.model_class.from_dict(results[0])
        return None
    
    def get_by_domain(self, domain: str) -> Optional[Organization]:
        """Get organization by domain."""
        query = "SELECT * FROM organizations WHERE domain = ?"
        results = self.db_manager.execute_query(query, (domain,))
        if results:
            return self.model_class.from_dict(results[0])
        return None
    
    def get_by_subscription_tier(self, tier: str) -> List[Organization]:
        """Get organizations by subscription tier."""
        query = "SELECT * FROM organizations WHERE subscription_tier = ?"
        results = self.db_manager.execute_query(query, (tier,))
        return [self.model_class.from_dict(row) for row in results]
    
    def get_active_organizations(self) -> List[Organization]:
        """Get all active organizations."""
        query = "SELECT * FROM organizations WHERE is_active = 1"
        results = self.db_manager.execute_query(query)
        return [self.model_class.from_dict(row) for row in results]
    
    def search_organizations(self, search_term: str) -> List[Organization]:
        """Search organizations by name, description, or domain."""
        query = """
            SELECT * FROM organizations 
            WHERE name LIKE ? OR description LIKE ? OR domain LIKE ?
        """
        search_pattern = f"%{search_term}%"
        results = self.db_manager.execute_query(query, (search_pattern, search_pattern, search_pattern))
        return [self.model_class.from_dict(row) for row in results]
    
    def get_organization_statistics(self) -> Dict[str, Any]:
        """Get organization statistics."""
        query = """
            SELECT 
                COUNT(*) as total_organizations,
                COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_organizations,
                COUNT(CASE WHEN is_active = 0 THEN 1 END) as inactive_organizations,
                subscription_tier,
                COUNT(*) as tier_count
            FROM organizations 
            GROUP BY subscription_tier
        """
        results = self.db_manager.execute_query(query)
        
        stats = {
            "total_organizations": 0,
            "active_organizations": 0,
            "inactive_organizations": 0,
            "subscription_tiers": {}
        }
        
        for row in results:
            stats["total_organizations"] = row["total_organizations"]
            stats["active_organizations"] = row["active_organizations"]
            stats["inactive_organizations"] = row["inactive_organizations"]
            if row["subscription_tier"]:
                stats["subscription_tiers"][row["subscription_tier"]] = row["tier_count"]
        
        return stats
    
    def get_organization_usage(self, organization_id: str) -> Dict[str, Any]:
        """Get organization usage statistics."""
        # Get user count
        user_query = "SELECT COUNT(*) as user_count FROM users WHERE organization_id = ?"
        user_results = self.db_manager.execute_query(user_query, (organization_id,))
        user_count = user_results[0]["user_count"] if user_results else 0
        
        # Get project count
        project_query = "SELECT COUNT(*) as project_count FROM projects WHERE owner_id IN (SELECT id FROM users WHERE organization_id = ?)"
        project_results = self.db_manager.execute_query(project_query, (organization_id,))
        project_count = project_results[0]["project_count"] if project_results else 0
        
        # Get total storage used
        storage_query = """
            SELECT SUM(f.size) as total_storage 
            FROM files f 
            JOIN projects p ON f.project_id = p.id 
            JOIN users u ON p.owner_id = u.id 
            WHERE u.organization_id = ?
        """
        storage_results = self.db_manager.execute_query(storage_query, (organization_id,))
        total_storage = storage_results[0]["total_storage"] if storage_results and storage_results[0]["total_storage"] else 0
        
        # Get organization limits
        org_query = "SELECT max_users, max_projects, max_storage_gb FROM organizations WHERE id = ?"
        org_results = self.db_manager.execute_query(org_query, (organization_id,))
        
        if org_results:
            limits = org_results[0]
            return {
                "user_count": user_count,
                "project_count": project_count,
                "total_storage_bytes": total_storage,
                "total_storage_gb": round(total_storage / (1024**3), 2),
                "max_users": limits["max_users"],
                "max_projects": limits["max_projects"],
                "max_storage_gb": limits["max_storage_gb"],
                "user_usage_percent": round((user_count / limits["max_users"]) * 100, 2) if limits["max_users"] > 0 else 0,
                "project_usage_percent": round((project_count / limits["max_projects"]) * 100, 2) if limits["max_projects"] > 0 else 0,
                "storage_usage_percent": round((total_storage / (limits["max_storage_gb"] * 1024**3)) * 100, 2) if limits["max_storage_gb"] > 0 else 0
            }
        
        return {
            "user_count": user_count,
            "project_count": project_count,
            "total_storage_bytes": total_storage,
            "total_storage_gb": round(total_storage / (1024**3), 2),
            "max_users": 0,
            "max_projects": 0,
            "max_storage_gb": 0,
            "user_usage_percent": 0,
            "project_usage_percent": 0,
            "storage_usage_percent": 0
        }
    
    def check_name_exists(self, name: str) -> bool:
        """Check if organization name already exists."""
        query = "SELECT COUNT(*) as count FROM organizations WHERE name = ?"
        results = self.db_manager.execute_query(query, (name,))
        return results[0]["count"] > 0 if results else False
    
    def check_domain_exists(self, domain: str) -> bool:
        """Check if organization domain already exists."""
        query = "SELECT COUNT(*) as count FROM organizations WHERE domain = ?"
        results = self.db_manager.execute_query(query, (domain,))
        return results[0]["count"] > 0 if results else False
    
    def update_subscription_tier(self, organization_id: str, tier: str, limits: Dict[str, int]) -> bool:
        """Update organization subscription tier and limits."""
        query = """
            UPDATE organizations 
            SET subscription_tier = ?, max_users = ?, max_projects = ?, max_storage_gb = ?, updated_at = datetime('now')
            WHERE id = ?
        """
        try:
            affected_rows = self.db_manager.execute_update(
                query, 
                (tier, limits.get('max_users', 10), limits.get('max_projects', 100), limits.get('max_storage_gb', 10), organization_id)
            )
            return affected_rows > 0
        except Exception:
            return False 