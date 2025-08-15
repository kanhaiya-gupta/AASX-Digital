"""
Use Case Management Service
Handles all use case CRUD operations and business logic.
"""

from typing import List, Dict, Any, Optional
from src.shared.database.base_manager import BaseDatabaseManager
from src.shared.repositories.use_case_repository import UseCaseRepository
from src.shared.repositories.project_repository import ProjectRepository

class UseCaseService:
    def __init__(self):
        from src.shared.database.connection_manager import DatabaseConnectionManager
        from pathlib import Path
        
        # Create data directory and set database path
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        db_path = data_dir / "aasx_database.db"
        
        connection_manager = DatabaseConnectionManager(db_path)
        self.db_manager = BaseDatabaseManager(connection_manager)
        self.use_case_repo = UseCaseRepository(self.db_manager)
        self.project_repo = ProjectRepository(self.db_manager)
    
    def list_use_cases(self, user_context=None) -> List[Dict[str, Any]]:
        """Get use cases based on user context - demo data for guests, user-specific for authenticated users"""
        try:
            # If no user context or demo user, show demo use cases
            if not user_context or getattr(user_context, 'username', None) == 'demo':
                # Get demo use cases (all use cases for inspiration)
                use_cases = self.use_case_repo.get_all()
            else:
                # For authenticated users, get their specific use cases
                # For now, show all use cases (can be filtered later based on user permissions)
                use_cases = self.use_case_repo.get_all()
            
            # Transform to API format
            api_use_cases = []
            for use_case in use_cases:
                # Get category icon based on category
                category_icons = {
                    'thermal': 'fas fa-fire',
                    'structural': 'fas fa-cube', 
                    'fluid_dynamics': 'fas fa-water',
                    'multi_physics': 'fas fa-atom',
                    'industrial': 'fas fa-industry',
                    'general': 'fas fa-chart-line'
                }
                
                # Extract metadata if it exists
                metadata = {}
                if hasattr(use_case, 'metadata') and use_case.metadata:
                    if isinstance(use_case.metadata, str):
                        import json
                        try:
                            metadata = json.loads(use_case.metadata)
                        except:
                            metadata = {}
                    elif isinstance(use_case.metadata, dict):
                        metadata = use_case.metadata
                
                api_use_case = {
                    "use_case_id": use_case.use_case_id,  # ✅ Use consistent field name
                    "name": use_case.name,
                    "description": use_case.description,
                    "category": use_case.category,
                    "icon": category_icons.get(use_case.category, 'fas fa-cog'),
                    "industry": metadata.get('industry'),
                    "complexity": metadata.get('complexity'),
                    "expected_duration": metadata.get('expected_duration'),
                    "data_points": metadata.get('data_points'),
                    "physics_type": metadata.get('physics_type'),
                    "tags": metadata.get('tags', []),
                    "famous_examples": metadata.get('famous_examples', []),
                    "optimization_targets": metadata.get('optimization_targets', []),
                    "materials": metadata.get('materials', [])
                }
                api_use_cases.append(api_use_case)
            
            return api_use_cases
            
        except Exception as e:
            raise Exception(f"Database error: Failed to retrieve use cases. {str(e)}")
    
    def get_use_case(self, use_case_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific use case by ID"""
        try:
            use_case = self.use_case_repo.get_by_id(use_case_id)
            if use_case:
                return use_case.to_dict()
            return None
        except Exception as e:
            raise Exception(f"Failed to get use case {use_case_id}: {str(e)}")
    
    def create_use_case(self, use_case_data: Dict[str, Any]) -> str:
        """Create a new use case"""
        try:
            from src.shared.models.use_case import UseCase
            
            # Create UseCase model object
            use_case_obj = UseCase(**use_case_data)
            
            print(f"🔧 Use Case Service: Created UseCase model object:")
            print(f"   📋 Use Case ID: {getattr(use_case_obj, 'use_case_id', 'N/A')}")
            print(f"   📝 Name: {use_case_obj.name}")
            print(f"   📄 Description: {use_case_obj.description}")
            print(f"   🏷️  Category: {use_case_obj.category}")
            print(f"   📊 Metadata: {use_case_obj.metadata}")
            
            # Create use case using repository
            print(f"🔧 Use Case Service: About to create use case in database...")
            created_use_case = self.use_case_repo.create(use_case_obj)
            print(f"🔧 Use Case Service: Database creation result: {created_use_case is not None}")
            
            if not created_use_case:
                raise Exception("Failed to create use case")
            
            use_case_id = created_use_case.use_case_id if hasattr(created_use_case, 'use_case_id') else created_use_case.id
            
            print(f"✅ Use case created successfully:")
            print(f"   📋 Use Case ID: {use_case_id}")
            print(f"   📝 Name: {created_use_case.name}")
            
            return use_case_id
        except Exception as e:
            raise Exception(f"Failed to create use case: {str(e)}")
    
    def update_use_case(self, use_case_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing use case"""
        try:
            return self.use_case_repo.update(use_case_id, updates)
        except Exception as e:
            raise Exception(f"Failed to update use case {use_case_id}: {str(e)}")
    
    def delete_use_case(self, use_case_id: str) -> bool:
        """Delete a use case and all its projects"""
        try:
            # Get all projects in this use case
            projects = self.project_repo.get_by_use_case_id(use_case_id)
            
            # Delete all projects in this use case
            for project in projects:
                project_id = project.get('project_id')
                if project_id:
                    self.project_repo.delete(project_id)
            
            # Delete the use case
            return self.use_case_repo.delete(use_case_id)
        except Exception as e:
            raise Exception(f"Failed to delete use case {use_case_id}: {str(e)}")
    
    def get_use_case_projects(self, use_case_id: str) -> List[Dict[str, Any]]:
        """Get all projects for a specific use case"""
        try:
            projects = self.project_repo.get_by_use_case_id(use_case_id)
            return [project.to_dict() if hasattr(project, 'to_dict') else project for project in projects]
        except Exception as e:
            raise Exception(f"Failed to get projects for use case {use_case_id}: {str(e)}")
    
    def get_use_case_statistics(self) -> Dict[str, Any]:
        """Get statistics for all use cases"""
        try:
            return self.use_case_repo.get_statistics()
        except Exception as e:
            raise Exception(f"Failed to get use case statistics: {str(e)}")
    
    def get_use_case_id_by_name(self, use_case_name: str) -> Optional[str]:
        """Get use case ID by name (reverse engineering)."""
        try:
            print(f"🔍 UseCaseService: Searching for use case: {use_case_name}")
            
            # Use the repository method to get use case by name
            use_case = self.use_case_repo.get_by_name(use_case_name)
            
            if use_case:
                use_case_id = use_case.use_case_id
                print(f"✅ UseCaseService: Found use case '{use_case_name}' with ID: {use_case_id}")
                return use_case_id
            else:
                print(f"❌ UseCaseService: Use case '{use_case_name}' not found")
                return None
                
        except Exception as e:
            print(f"❌ UseCaseService: Error finding use case by name: {str(e)}")
            return None

# Global instance
use_case_service = UseCaseService() 