"""
AI RAG Registry Service
=======================

Business logic layer for AI RAG registry operations.
Orchestrates operations across repositories and models.
Pure async implementation following AASX and Twin Registry convention.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.modules.ai_rag.models.ai_rag_registry import AIRagRegistry
from src.modules.ai_rag.repositories.ai_rag_registry_repository import AIRagRegistryRepository
from src.modules.ai_rag.repositories.ai_rag_metrics_repository import AIRagMetricsRepository
from src.modules.ai_rag.repositories.document_repository import DocumentRepository

logger = logging.getLogger(__name__)


class AIRagRegistryService:
    """
    AI RAG Registry Service - Pure Async Implementation
    
    Orchestrates AI RAG registry operations including:
    - Registry lifecycle management
    - Health monitoring and scoring
    - Integration status management
    - Performance optimization
    """
    
    def __init__(self, registry_repo: AIRagRegistryRepository, 
                 metrics_repo: AIRagMetricsRepository,
                 document_repo: DocumentRepository):
        """Initialize service with required repositories"""
        self.registry_repo = registry_repo
        self.metrics_repo = metrics_repo
        self.document_repo = document_repo
    
    async def create_registry(self, registry_data: Dict[str, Any]) -> Optional[AIRagRegistry]:
        """Create a new AI RAG registry with validation"""
        try:
            logger.info(f"Creating AI RAG registry: {registry_data.get('registry_name', 'Unknown')}")
            
            # Create registry instance
            registry = AIRagRegistry(**registry_data)
            
            # Validate registry before creation
            if not await self._validate_registry(registry):
                logger.error("Registry validation failed")
                return None
            
            # Create in database
            success = await self.registry_repo.create(registry)
            if not success:
                logger.error("Failed to create registry in database")
                return None
            
            logger.info(f"Successfully created AI RAG registry: {registry.registry_id}")
            return registry
            
        except Exception as e:
            logger.error(f"Error creating AI RAG registry: {e}")
            return None
    
    async def get_registry_by_id(self, registry_id: str) -> Optional[AIRagRegistry]:
        """Get AI RAG registry by ID with enhanced data"""
        try:
            registry = await self.registry_repo.get_by_id(registry_id)
            if registry:
                # Enhance with additional data
                await self._enhance_registry_data(registry)
            
            return registry
            
        except Exception as e:
            logger.error(f"Error getting registry by ID: {e}")
            return None
    
    async def get_registry_by_file_id(self, file_id: str) -> Optional[AIRagRegistry]:
        """Get AI RAG registry by file ID"""
        try:
            return await self.registry_repo.get_by_file_id(file_id)
        except Exception as e:
            logger.error(f"Error getting registry by file ID: {e}")
            return None
    
    async def update_registry(self, registry_id: str, update_data: Dict[str, Any]) -> bool:
        """Update AI RAG registry with validation"""
        try:
            logger.info(f"Updating AI RAG registry: {registry_id}")
            
            # Get existing registry
            registry = await self.registry_repo.get_by_id(registry_id)
            if not registry:
                logger.error(f"Registry not found: {registry_id}")
                return False
            
            # Update fields
            for key, value in update_data.items():
                if hasattr(registry, key):
                    setattr(registry, key, value)
            
            # Validate updated registry
            if not await self._validate_registry(registry):
                logger.error("Updated registry validation failed")
                return False
            
            # Update timestamp
            registry.update_timestamp()
            
            # Save to database
            success = await self.registry_repo.update(registry)
            if success:
                logger.info(f"Successfully updated registry: {registry_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating registry: {e}")
            return False
    
    async def delete_registry(self, registry_id: str) -> bool:
        """Delete AI RAG registry with cleanup"""
        try:
            logger.info(f"Deleting AI RAG registry: {registry_id}")
            
            # Check for dependencies
            if await self._has_dependencies(registry_id):
                logger.warning(f"Registry has dependencies, cannot delete: {registry_id}")
                return False
            
            # Delete from database
            success = await self.registry_repo.delete(registry_id)
            if success:
                logger.info(f"Successfully deleted registry: {registry_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting registry: {e}")
            return False
    
    async def get_registries_by_org(self, org_id: str, limit: int = 100) -> List[AIRagRegistry]:
        """Get AI RAG registries by organization with filtering"""
        try:
            registries = await self.registry_repo.get_by_org_id(org_id)
            
            # Apply business logic filtering
            filtered_registries = []
            for registry in registries[:limit]:
                if await self._is_accessible(registry):
                    filtered_registries.append(registry)
            
            return filtered_registries
            
        except Exception as e:
            logger.error(f"Error getting registries by org: {e}")
            return []
    
    async def get_registries_by_status(self, status: str) -> List[AIRagRegistry]:
        """Get AI RAG registries by status"""
        try:
            return await self.registry_repo.get_by_status(status)
        except Exception as e:
            logger.error(f"Error getting registries by status: {e}")
            return []
    
    async def search_registries(self, search_term: str, limit: int = 50) -> List[AIRagRegistry]:
        """Search AI RAG registries with relevance scoring"""
        try:
            registries = await self.registry_repo.search(search_term, limit)
            
            # Score relevance and sort
            scored_registries = []
            for registry in registries:
                relevance_score = await self._calculate_relevance_score(registry, search_term)
                scored_registries.append((registry, relevance_score))
            
            # Sort by relevance score (descending)
            scored_registries.sort(key=lambda x: x[1], reverse=True)
            
            return [registry for registry, _ in scored_registries]
            
        except Exception as e:
            logger.error(f"Error searching registries: {e}")
            return []
    
    async def update_registry_health(self, registry_id: str) -> bool:
        """Update registry health score based on metrics"""
        try:
            logger.info(f"Updating health score for registry: {registry_id}")
            
            # Get latest metrics
            latest_metrics = await self.metrics_repo.get_latest_by_registry_id(registry_id)
            if not latest_metrics:
                logger.warning(f"No metrics found for registry: {registry_id}")
                return False
            
            # Calculate new health score
            new_health_score = latest_metrics.calculate_overall_health_score()
            
            # Update registry
            update_data = {
                "overall_health_score": new_health_score,
                "health_status": self._get_health_status(new_health_score)
            }
            
            success = await self.update_registry(registry_id, update_data)
            if success:
                logger.info(f"Updated health score to {new_health_score} for registry: {registry_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating registry health: {e}")
            return False
    
    async def activate_registry(self, registry_id: str) -> bool:
        """Activate an AI RAG registry"""
        try:
            logger.info(f"Activating registry: {registry_id}")
            
            update_data = {
                "lifecycle_status": "active",
                "operational_status": "running",
                "availability_status": "online",
                "activated_at": datetime.now().isoformat()
            }
            
            success = await self.update_registry(registry_id, update_data)
            if success:
                logger.info(f"Successfully activated registry: {registry_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error activating registry: {e}")
            return False
    
    async def deactivate_registry(self, registry_id: str) -> bool:
        """Deactivate an AI RAG registry"""
        try:
            logger.info(f"Deactivating registry: {registry_id}")
            
            update_data = {
                "lifecycle_status": "inactive",
                "operational_status": "stopped",
                "availability_status": "offline"
            }
            
            success = await self.update_registry(registry_id, update_data)
            if success:
                logger.info(f"Successfully deactivated registry: {registry_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deactivating registry: {e}")
            return False
    
    async def get_registry_statistics(self, org_id: str) -> Dict[str, Any]:
        """Get comprehensive statistics for organization"""
        try:
            registries = await self.registry_repo.get_by_org_id(org_id)
            
            stats = {
                "total_registries": len(registries),
                "active_registries": 0,
                "healthy_registries": 0,
                "by_status": {},
                "by_category": {},
                "by_type": {},
                "average_health_score": 0.0
            }
            
            total_health = 0
            for registry in registries:
                # Count by status
                status = registry.lifecycle_status
                stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
                
                # Count by category
                category = registry.rag_category
                stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
                
                # Count by type
                rag_type = registry.rag_type
                stats["by_type"][rag_type] = stats["by_type"].get(rag_type, 0) + 1
                
                # Count active and healthy
                if registry.lifecycle_status == "active":
                    stats["active_registries"] += 1
                
                if registry.is_healthy():
                    stats["healthy_registries"] += 1
                
                total_health += registry.overall_health_score or 0
            
            if registries:
                stats["average_health_score"] = total_health / len(registries)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting registry statistics: {e}")
            return {}
    
    # Private helper methods
    
    async def _validate_registry(self, registry: AIRagRegistry) -> bool:
        """Validate registry before database operations"""
        try:
            # Check required fields
            if not registry.registry_name or not registry.file_id:
                logger.error("Registry missing required fields")
                return False
            
            # Check business rules
            if registry.rag_priority not in ["low", "medium", "high", "critical"]:
                logger.error("Invalid RAG priority")
                return False
            
            if registry.rag_category not in ["text", "image", "audio", "video", "multimodal"]:
                logger.error("Invalid RAG category")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Registry validation error: {e}")
            return False
    
    async def _enhance_registry_data(self, registry: AIRagRegistry) -> None:
        """Enhance registry with additional computed data"""
        try:
            # Get document count
            doc_count = await self.document_repo.count_by_registry_id(registry.registry_id)
            registry.document_count = doc_count
            
            # Get latest metrics
            latest_metrics = await self.metrics_repo.get_latest_by_registry_id(registry.registry_id)
            if latest_metrics:
                registry.latest_metrics = latest_metrics
                
        except Exception as e:
            logger.warning(f"Error enhancing registry data: {e}")
    
    async def _has_dependencies(self, registry_id: str) -> bool:
        """Check if registry has dependencies that prevent deletion"""
        try:
            # Check documents
            doc_count = await self.document_repo.count_by_registry_id(registry_id)
            if doc_count > 0:
                return True
            
            # Check metrics
            metrics_count = await self.metrics_repo.count_by_registry_id(registry_id)
            if metrics_count > 0:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking dependencies: {e}")
            return True  # Assume dependencies exist on error
    
    async def _is_accessible(self, registry: AIRagRegistry) -> bool:
        """Check if registry is accessible based on business rules"""
        try:
            # Check if active
            if registry.lifecycle_status != "active":
                return False
            
            # Check if healthy
            if not registry.is_healthy():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking accessibility: {e}")
            return False
    
    async def _calculate_relevance_score(self, registry: AIRagRegistry, search_term: str) -> float:
        """Calculate relevance score for search results"""
        try:
            score = 0.0
            
            # Name relevance
            if search_term.lower() in registry.registry_name.lower():
                score += 0.4
            
            # Description relevance
            if registry.description and search_term.lower() in registry.description.lower():
                score += 0.3
            
            # Category relevance
            if search_term.lower() in registry.rag_category.lower():
                score += 0.2
            
            # Type relevance
            if search_term.lower() in registry.rag_type.lower():
                score += 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating relevance score: {e}")
            return 0.0
    
    def _get_health_status(self, health_score: float) -> str:
        """Convert health score to status string"""
        if health_score >= 90:
            return "excellent"
        elif health_score >= 80:
            return "good"
        elif health_score >= 70:
            return "fair"
        elif health_score >= 60:
            return "poor"
        else:
            return "critical"
