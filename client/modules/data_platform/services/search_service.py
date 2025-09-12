"""
Search Service - Data Platform Advanced Discovery
===============================================

Advanced search capabilities across all data platform entities including
files, projects, use cases, and organizations. Provides full-text search,
faceted filtering, and intelligent result ranking.

Pattern: Lazy initialization with async services for world-class standards
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import re

# Import from backend engine
from src.engine.services.business_domain.file_service import FileService
from src.engine.services.business_domain.project_service import ProjectService
from src.engine.services.business_domain.use_case_service import UseCaseService
from src.engine.services.business_domain.organization_service import OrganizationService
from src.engine.repositories.business_domain_repository import BusinessDomainRepository

logger = logging.getLogger(__name__)


class SearchService:
    """Advanced search service for data platform discovery"""
    
    def __init__(self):
        """Initialize with backend services - lazy initialization to avoid async issues"""
        self._initialized = False
        self._file_service = None
        self._project_service = None
        self._use_case_service = None
        self._organization_service = None
        self._file_repo = None
        self._project_repo = None
        self._use_case_repo = None
        self._organization_repo = None
        
        logger.info("✅ Search service created (lazy initialization)")
    
    async def _ensure_initialized(self):
        """Ensure services are initialized (lazy initialization)"""
        if self._initialized:
            return
            
        try:
            # Initialize backend services
            self._file_service = FileService()
            self._project_service = ProjectService()
            self._use_case_service = UseCaseService()
            self._organization_service = OrganizationService()
            
            # Initialize repositories
            self._file_repo = FileRepository()
            self._project_repo = ProjectRepository()
            self._use_case_repo = UseCaseRepository()
            self._organization_repo = OrganizationRepository()
            
            self._initialized = True
            logger.info("✅ Search service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize search service: {e}")
            raise
    
    async def global_search(self, query: str, filters: Dict[str, Any] = None, 
                           user_id: str = None, organization_id: str = None,
                           limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Perform global search across all entities with intelligent ranking"""
        await self._ensure_initialized()
        
        try:
            # Parse and clean search query
            search_terms = self._parse_search_query(query)
            
            # Apply filters
            filters = filters or {}
            
            # Perform searches across all entities
            results = {
                "files": await self._search_files(search_terms, filters, user_id, organization_id, limit, offset),
                "projects": await self._search_projects(search_terms, filters, user_id, organization_id, limit, offset),
                "use_cases": await self._search_use_cases(search_terms, filters, user_id, organization_id, limit, offset),
                "organizations": await self._search_organizations(search_terms, filters, user_id, organization_id, limit, offset)
            }
            
            # Calculate total results
            total_results = sum(len(entity_results) for entity_results in results.values())
            
            # Rank and combine results
            ranked_results = self._rank_search_results(results, search_terms)
            
            return {
                "query": query,
                "total_results": total_results,
                "results": ranked_results,
                "facets": await self._generate_search_facets(filters, user_id, organization_id),
                "search_metadata": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "user_id": user_id,
                    "organization_id": organization_id
                }
            }
            
        except Exception as e:
            logger.error(f"Error performing global search: {e}")
            raise
    
    async def advanced_search(self, search_config: Dict[str, Any], 
                            user_id: str, organization_id: str) -> Dict[str, Any]:
        """Advanced search with complex queries and filters"""
        await self._ensure_initialized()
        
        try:
            # Parse advanced search configuration
            query = search_config.get("query", "")
            entity_types = search_config.get("entity_types", ["files", "projects", "use_cases"])
            date_range = search_config.get("date_range", {})
            size_range = search_config.get("size_range", {})
            tags = search_config.get("tags", [])
            status_filters = search_config.get("status", [])
            
            # Build advanced filters
            advanced_filters = {
                "date_range": date_range,
                "size_range": size_range,
                "tags": tags,
                "status": status_filters,
                "entity_types": entity_types
            }
            
            # Perform advanced search
            results = await self.global_search(query, advanced_filters, user_id, organization_id)
            
            # Add advanced search metadata
            results["search_type"] = "advanced"
            results["search_config"] = search_config
            
            return results
            
        except Exception as e:
            logger.error(f"Error performing advanced search: {e}")
            raise
    
    async def get_search_suggestions(self, partial_query: str, 
                                   user_id: str, organization_id: str) -> List[str]:
        """Get search suggestions based on partial query"""
        await self._ensure_initialized()
        
        try:
            suggestions = []
            
            # Get suggestions from different entity types
            if len(partial_query) >= 2:
                # File name suggestions
                file_suggestions = await self._get_file_suggestions(partial_query, user_id, organization_id)
                suggestions.extend(file_suggestions)
                
                # Project name suggestions
                project_suggestions = await self._get_project_suggestions(partial_query, user_id, organization_id)
                suggestions.extend(project_suggestions)
                
                # Use case suggestions
                use_case_suggestions = await self._get_use_case_suggestions(partial_query, user_id, organization_id)
                suggestions.extend(use_case_suggestions)
                
                # Tag suggestions
                tag_suggestions = await self._get_tag_suggestions(partial_query, user_id, organization_id)
                suggestions.extend(tag_suggestions)
            
            # Remove duplicates and limit results
            unique_suggestions = list(set(suggestions))[:20]
            
            return sorted(unique_suggestions)
            
        except Exception as e:
            logger.error(f"Error getting search suggestions: {e}")
            raise
    
    async def get_search_analytics(self, user_id: str, organization_id: str, 
                                  time_range: str = "30d") -> Dict[str, Any]:
        """Get search analytics and insights"""
        await self._ensure_initialized()
        
        try:
            # Calculate time range
            end_date = datetime.utcnow()
            if time_range == "7d":
                start_date = end_date - timedelta(days=7)
            elif time_range == "30d":
                start_date = end_date - timedelta(days=30)
            elif time_range == "90d":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Get search statistics
            search_stats = await self._get_search_statistics(start_date, end_date, user_id, organization_id)
            
            # Get popular search terms
            popular_terms = await self._get_popular_search_terms(start_date, end_date, user_id, organization_id)
            
            # Get search performance metrics
            performance_metrics = await self._get_search_performance_metrics(start_date, end_date, user_id, organization_id)
            
            return {
                "time_range": time_range,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "search_statistics": search_stats,
                "popular_search_terms": popular_terms,
                "performance_metrics": performance_metrics
            }
            
        except Exception as e:
            logger.error(f"Error getting search analytics: {e}")
            raise
    
    def _parse_search_query(self, query: str) -> List[str]:
        """Parse search query into search terms"""
        # Remove special characters and split into terms
        cleaned_query = re.sub(r'[^\w\s]', ' ', query.lower())
        terms = [term.strip() for term in cleaned_query.split() if len(term.strip()) > 1]
        return terms
    
    async def _search_files(self, search_terms: List[str], filters: Dict[str, Any],
                           user_id: str, organization_id: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Search files with advanced filtering"""
        try:
            # Build file search query
            search_query = " ".join(search_terms)
            
            # Get files from repository
            files = await self._file_repo.search_files(search_query)
            
            # Apply filters
            filtered_files = self._apply_file_filters(files, filters)
            
            # Apply user/organization access control
            accessible_files = await self._filter_accessible_files(filtered_files, user_id, organization_id)
            
            return accessible_files[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Error searching files: {e}")
            return []
    
    async def _search_projects(self, search_terms: List[str], filters: Dict[str, Any],
                              user_id: str, organization_id: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Search projects with advanced filtering"""
        try:
            # Build project search query
            search_query = " ".join(search_terms)
            
            # Get projects from repository
            projects = await self._project_repo.search_projects(search_query)
            
            # Apply filters
            filtered_projects = self._apply_project_filters(projects, filters)
            
            # Apply user/organization access control
            accessible_projects = await self._filter_accessible_projects(filtered_projects, user_id, organization_id)
            
            return accessible_projects[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Error searching projects: {e}")
            return []
    
    async def _search_use_cases(self, search_terms: List[str], filters: Dict[str, Any],
                               user_id: str, organization_id: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Search use cases with advanced filtering"""
        try:
            # Build use case search query
            search_query = " ".join(search_terms)
            
            # Get use cases from repository
            use_cases = await self._use_case_repo.search_use_cases(search_query)
            
            # Apply filters
            filtered_use_cases = self._apply_use_case_filters(use_cases, filters)
            
            # Apply user/organization access control
            accessible_use_cases = await self._filter_accessible_use_cases(filtered_use_cases, user_id, organization_id)
            
            return accessible_use_cases[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Error searching use cases: {e}")
            return []
    
    async def _search_organizations(self, search_terms: List[str], filters: Dict[str, Any],
                                   user_id: str, organization_id: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Search organizations with advanced filtering"""
        try:
            # Build organization search query
            search_query = " ".join(search_terms)
            
            # Get organizations from repository
            organizations = await self._organization_repo.search_organizations(search_query)
            
            # Apply filters
            filtered_organizations = self._apply_organization_filters(organizations, filters)
            
            # Apply user/organization access control
            accessible_organizations = await self._filter_accessible_organizations(filtered_organizations, user_id, organization_id)
            
            return accessible_organizations[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Error searching organizations: {e}")
            return []
    
    def _apply_file_filters(self, files: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filters to file search results"""
        filtered_files = files
        
        # Apply date range filter
        if filters.get("date_range"):
            date_range = filters["date_range"]
            start_date = datetime.fromisoformat(date_range.get("start", "1900-01-01"))
            end_date = datetime.fromisoformat(date_range.get("end", "2100-12-31"))
            
            filtered_files = [
                f for f in filtered_files
                if start_date <= datetime.fromisoformat(f.get("upload_date", "1900-01-01")) <= end_date
            ]
        
        # Apply size range filter
        if filters.get("size_range"):
            size_range = filters["size_range"]
            min_size = size_range.get("min", 0)
            max_size = size_range.get("max", float('inf'))
            
            filtered_files = [
                f for f in filtered_files
                if min_size <= f.get("size_bytes", 0) <= max_size
            ]
        
        # Apply tag filter
        if filters.get("tags"):
            required_tags = set(filters["tags"])
            filtered_files = [
                f for f in filtered_files
                if required_tags.issubset(set(f.get("tags", [])))
            ]
        
        # Apply status filter
        if filters.get("status"):
            status_list = filters["status"]
            filtered_files = [
                f for f in filtered_files
                if f.get("status") in status_list
            ]
        
        return filtered_files
    
    def _apply_project_filters(self, projects: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filters to project search results"""
        filtered_projects = projects
        
        # Apply date range filter
        if filters.get("date_range"):
            date_range = filters["date_range"]
            start_date = datetime.fromisoformat(date_range.get("start", "1900-01-01"))
            end_date = datetime.fromisoformat(date_range.get("end", "2100-12-31"))
            
            filtered_projects = [
                p for p in filtered_projects
                if start_date <= datetime.fromisoformat(p.get("created_at", "1900-01-01")) <= end_date
            ]
        
        return filtered_projects
    
    def _apply_use_case_filters(self, use_cases: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filters to use case search results"""
        filtered_use_cases = use_cases
        
        # Apply category filter
        if filters.get("category"):
            category_list = filters["category"]
            filtered_use_cases = [
                uc for uc in filtered_use_cases
                if uc.get("category") in category_list
            ]
        
        return filtered_use_cases
    
    def _apply_organization_filters(self, organizations: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filters to organization search results"""
        filtered_organizations = organizations
        
        # Apply subscription tier filter
        if filters.get("subscription_tier"):
            tier_list = filters["subscription_tier"]
            filtered_organizations = [
                org for org in filtered_organizations
                if org.get("subscription_tier") in tier_list
            ]
        
        return filtered_organizations
    
    async def _filter_accessible_files(self, files: List[Dict[str, Any]], 
                                     user_id: str, organization_id: str) -> List[Dict[str, Any]]:
        """Filter files based on user access permissions"""
        # For now, return all files - implement proper access control later
        return files
    
    async def _filter_accessible_projects(self, projects: List[Dict[str, Any]], 
                                        user_id: str, organization_id: str) -> List[Dict[str, Any]]:
        """Filter projects based on user access permissions"""
        # For now, return all projects - implement proper access control later
        return projects
    
    async def _filter_accessible_use_cases(self, use_cases: List[Dict[str, Any]], 
                                         user_id: str, organization_id: str) -> List[Dict[str, Any]]:
        """Filter use cases based on user access permissions"""
        # For now, return all use cases - implement proper access control later
        return use_cases
    
    async def _filter_accessible_organizations(self, organizations: List[Dict[str, Any]], 
                                             user_id: str, organization_id: str) -> List[Dict[str, Any]]:
        """Filter organizations based on user access permissions"""
        # For now, return all organizations - implement proper access control later
        return organizations
    
    def _rank_search_results(self, results: Dict[str, List[Dict[str, Any]]], 
                           search_terms: List[str]) -> List[Dict[str, Any]]:
        """Rank search results by relevance"""
        all_results = []
        
        # Add entity type to each result
        for entity_type, entity_results in results.items():
            for result in entity_results:
                result["entity_type"] = entity_type
                result["relevance_score"] = self._calculate_relevance_score(result, search_terms)
                all_results.append(result)
        
        # Sort by relevance score (highest first)
        ranked_results = sorted(all_results, key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return ranked_results
    
    def _calculate_relevance_score(self, result: Dict[str, Any], search_terms: List[str]) -> float:
        """Calculate relevance score for search result"""
        score = 0.0
        
        # Exact matches get highest score
        for term in search_terms:
            # Check in name/title fields
            if term.lower() in result.get("name", "").lower():
                score += 10.0
            if term.lower() in result.get("title", "").lower():
                score += 10.0
            if term.lower() in result.get("original_filename", "").lower():
                score += 10.0
            
            # Check in description fields
            if term.lower() in result.get("description", "").lower():
                score += 5.0
            
            # Check in tags
            if term.lower() in [tag.lower() for tag in result.get("tags", [])]:
                score += 8.0
        
        # Boost recent items
        if "created_at" in result:
            try:
                created_date = datetime.fromisoformat(result["created_at"])
                days_old = (datetime.utcnow() - created_date).days
                if days_old <= 7:
                    score += 3.0
                elif days_old <= 30:
                    score += 1.0
            except:
                pass
        
        return score
    
    async def _generate_search_facets(self, filters: Dict[str, Any], 
                                    user_id: str, organization_id: str) -> Dict[str, Any]:
        """Generate search facets for filtering"""
        try:
            facets = {
                "file_types": await self._get_file_type_facets(user_id, organization_id),
                "date_ranges": [
                    {"label": "Last 24 hours", "value": "24h"},
                    {"label": "Last 7 days", "value": "7d"},
                    {"label": "Last 30 days", "value": "30d"},
                    {"label": "Last 90 days", "value": "90d"}
                ],
                "statuses": [
                    {"label": "Active", "value": "active"},
                    {"label": "Inactive", "value": "inactive"},
                    {"label": "Archived", "value": "archived"}
                ],
                "categories": await self._get_category_facets(user_id, organization_id)
            }
            
            return facets
            
        except Exception as e:
            logger.error(f"Error generating search facets: {e}")
            return {}
    
    async def _get_file_type_facets(self, user_id: str, organization_id: str) -> List[Dict[str, Any]]:
        """Get file type facets"""
        try:
            # This would query the database for actual file type counts
            # For now, return common file types
            return [
                {"label": "Documents", "value": "document", "count": 0},
                {"label": "Images", "value": "image", "count": 0},
                {"label": "Videos", "value": "video", "count": 0},
                {"label": "Data Files", "value": "data", "count": 0},
                {"label": "Archives", "value": "archive", "count": 0}
            ]
        except Exception as e:
            logger.error(f"Error getting file type facets: {e}")
            return []
    
    async def _get_category_facets(self, user_id: str, organization_id: str) -> List[Dict[str, Any]]:
        """Get category facets"""
        try:
            # This would query the database for actual category counts
            # For now, return common categories
            return [
                {"label": "Manufacturing", "value": "manufacturing", "count": 0},
                {"label": "Healthcare", "value": "healthcare", "count": 0},
                {"label": "Finance", "value": "finance", "count": 0},
                {"label": "Education", "value": "education", "count": 0},
                {"label": "Research", "value": "research", "count": 0}
            ]
        except Exception as e:
            logger.error(f"Error getting category facets: {e}")
            return []
    
    async def _get_file_suggestions(self, partial_query: str, user_id: str, organization_id: str) -> List[str]:
        """Get file name suggestions"""
        try:
            # This would query the database for actual suggestions
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Error getting file suggestions: {e}")
            return []
    
    async def _get_project_suggestions(self, partial_query: str, user_id: str, organization_id: str) -> List[str]:
        """Get project name suggestions"""
        try:
            # This would query the database for actual suggestions
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Error getting project suggestions: {e}")
            return []
    
    async def _get_use_case_suggestions(self, partial_query: str, user_id: str, organization_id: str) -> List[str]:
        """Get use case suggestions"""
        try:
            # This would query the database for actual suggestions
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Error getting use case suggestions: {e}")
            return []
    
    async def _get_tag_suggestions(self, partial_query: str, user_id: str, organization_id: str) -> List[str]:
        """Get tag suggestions"""
        try:
            # This would query the database for actual suggestions
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Error getting tag suggestions: {e}")
            return []
    
    async def _get_search_statistics(self, start_date: datetime, end_date: datetime, 
                                   user_id: str, organization_id: str) -> Dict[str, Any]:
        """Get search statistics for analytics"""
        try:
            # This would query the database for actual search statistics
            # For now, return mock data
            return {
                "total_searches": 0,
                "unique_users": 0,
                "average_results_per_search": 0,
                "most_searched_terms": []
            }
        except Exception as e:
            logger.error(f"Error getting search statistics: {e}")
            return {}
    
    async def _get_popular_search_terms(self, start_date: datetime, end_date: datetime, 
                                       user_id: str, organization_id: str) -> List[Dict[str, Any]]:
        """Get popular search terms for analytics"""
        try:
            # This would query the database for actual popular terms
            # For now, return mock data
            return []
        except Exception as e:
            logger.error(f"Error getting popular search terms: {e}")
            return []
    
    async def _get_search_performance_metrics(self, start_date: datetime, end_date: datetime, 
                                            user_id: str, organization_id: str) -> Dict[str, Any]:
        """Get search performance metrics for analytics"""
        try:
            # This would query the database for actual performance metrics
            # For now, return mock data
            return {
                "average_search_time": 0,
                "search_success_rate": 0,
                "zero_result_searches": 0
            }
        except Exception as e:
            logger.error(f"Error getting search performance metrics: {e}")
            return {}
