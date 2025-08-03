"""
AI/RAG Query Processing Service
Handles all query processing, technique comparison, and recommendations business logic.
Enhanced with src/shared/ integration for reverse engineering capabilities.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

# Import the extraction service
from .extraction_service import FileIDExtractionService

logger = logging.getLogger(__name__)

class QueryService:
    def __init__(self, rag_manager, project_service=None):
        """Initialize query service with RAG manager and project service for context"""
        self.rag_manager = rag_manager
        self.project_service = project_service
        
        # Initialize extraction service
        self.extraction_service = FileIDExtractionService(project_service)
        
        logger.info("Query Service initialized with enhanced context capabilities and file ID extraction")
    
    def process_query(self, query: str, technique_id: Optional[str] = None, 
                     project_id: Optional[str] = None, search_limit: int = 10, 
                     llm_model: str = "gpt-3.5-turbo", enable_auto_selection: bool = True) -> Dict[str, Any]:
        """Process a query using the RAG system"""
        try:
            logger.info(f"🔍 Processing query: {query[:50]}...")
            logger.info(f"🔧 Query Service: technique_id={technique_id}, enable_auto_selection={enable_auto_selection}")
            
            # Determine which technique_id to use
            # If user explicitly chose a technique, respect that choice regardless of auto-selection setting
            if technique_id and technique_id != "auto":
                final_technique_id = technique_id
                logger.info(f"🔧 Query Service: User explicitly chose technique: {technique_id}")
            elif enable_auto_selection:
                final_technique_id = None
                logger.info(f"🔧 Query Service: Auto-selection enabled, technique_id set to None")
            else:
                final_technique_id = technique_id
                logger.info(f"🔧 Query Service: Auto-selection disabled, using technique_id: {technique_id}")
            
            logger.info(f"🔧 Query Service: Final technique_id being sent to RAG manager: {final_technique_id}")
            
            result = self.rag_manager.process_query(
                query=query,
                technique_id=final_technique_id,
                project_id=project_id,
                search_limit=search_limit,
                llm_model=llm_model
            )
            
            # Check for errors
            if 'error' in result:
                raise Exception(result['error'])
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            raise e

    def process_query_with_context(self, query: str, file_id: Optional[str] = None,
                                  technique_id: Optional[str] = None, search_limit: int = 10,
                                  llm_model: str = "gpt-3.5-turbo", enable_auto_selection: bool = True) -> Dict[str, Any]:
        """
        Process a query with complete file context using src/shared/ methods.
        This enables reverse engineering capabilities.
        """
        try:
            logger.info(f"🔍 Processing query with context: {query[:50]}... (file_id: {file_id})")
            
            # Get complete file context if file_id is provided
            file_context = None
            if file_id and self.project_service:
                file_context = self.project_service.get_file_with_complete_context(file_id)
                if file_context:
                    logger.info(f"✅ Retrieved complete context for file: {file_id}")
                else:
                    logger.warning(f"⚠️ Could not retrieve context for file: {file_id}")
            
            # Process the query with RAG system
            # If user explicitly chose a technique, respect that choice regardless of auto-selection setting
            if technique_id and technique_id != "auto":
                final_technique_id = technique_id
            elif enable_auto_selection:
                final_technique_id = None
            else:
                final_technique_id = technique_id
            
            result = self.rag_manager.process_query(
                query=query,
                technique_id=final_technique_id,
                project_id=file_context.get("complete_trace", {}).get("project_id") if file_context else None,
                search_limit=search_limit,
                llm_model=llm_model
            )
            
            # Check for errors
            if 'error' in result:
                raise Exception(result['error'])
            
            # Enhance result with file context
            enhanced_result = {
                **result,
                "file_context": file_context,
                "has_context": file_context is not None,
                "context_summary": self._build_context_summary(file_context) if file_context else None
            }
            
            logger.info(f"✅ Query processed with context: {file_id}")
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error processing query with context: {e}")
            raise e

    def process_query_with_auto_extraction(self, query: str, technique_id: Optional[str] = None,
                                          search_limit: int = 10, llm_model: str = "gpt-3.5-turbo",
                                          enable_auto_selection: bool = True) -> Dict[str, Any]:
        """
        Process a query with automatic file_id extraction from natural language.
        This is the main method for "Ask anything about any file" capability.
        """
        try:
            logger.info(f"🔍 Processing query with auto extraction: {query[:50]}...")
            
            # Extract file_id from query
            extracted_file_id = self.extraction_service.extract_file_id_from_query(query)
            
            if extracted_file_id:
                logger.info(f"✅ Extracted file_id: {extracted_file_id}")
                # Process with extracted file_id
                return self.process_query_with_context(
                    query=query,
                    file_id=extracted_file_id,
                    technique_id=technique_id,
                    search_limit=search_limit,
                    llm_model=llm_model,
                    enable_auto_selection=enable_auto_selection
                )
            else:
                logger.info("⚠️ No file_id extracted, processing as regular query")
                # Process as regular query without context
                return self.process_query(
                    query=query,
                    technique_id=technique_id,
                    search_limit=search_limit,
                    llm_model=llm_model,
                    enable_auto_selection=enable_auto_selection
                )
            
        except Exception as e:
            logger.error(f"Error processing query with auto extraction: {e}")
            raise e

    def extract_file_id_from_query(self, query: str) -> Optional[str]:
        """Extract file_id from natural language query using extraction service."""
        try:
            return self.extraction_service.extract_file_id_from_query(query)
        except Exception as e:
            logger.error(f"Error extracting file_id from query: {e}")
            return None

    def test_file_id_extraction(self, test_queries: List[str]) -> List[Dict[str, Any]]:
        """Test file_id extraction with a list of queries."""
        try:
            return self.extraction_service.test_extraction(test_queries)
        except Exception as e:
            logger.error(f"Error testing file_id extraction: {e}")
            return [{"error": str(e)}]

    def get_extraction_statistics(self) -> Dict[str, Any]:
        """Get statistics about file_id extraction performance."""
        try:
            return self.extraction_service.get_extraction_statistics()
        except Exception as e:
            logger.error(f"Error getting extraction statistics: {e}")
            return {"error": str(e)}

    def _build_context_summary(self, file_context: Dict[str, Any]) -> Dict[str, Any]:
        """Build a summary of the file context for the response."""
        try:
            file_info = file_context.get("file_trace", {}).get("file_info", {})
            project_context = file_context.get("project_context", {})
            use_case_context = file_context.get("use_case_context", {})
            digital_twin = file_context.get("digital_twin", {})
            
            summary = {
                "file_name": file_info.get("original_filename") if file_info else "Unknown",
                "file_id": file_info.get("file_id") if file_info else "Unknown",
                "project_name": project_context.get("project", {}).get("name") if project_context else "Unknown",
                "use_case_name": use_case_context.get("use_case", {}).get("name") if use_case_context else "Unknown",
                "digital_twin_status": digital_twin.get("status") if digital_twin else "Not Available",
                "related_files_count": len(file_context.get("related_files", [])),
                "complete_trace": file_context.get("complete_trace", {})
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error building context summary: {e}")
            return {"error": "Could not build context summary"}

    def get_file_context(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get complete context for a file using src/shared/ methods."""
        try:
            if not self.project_service:
                logger.warning("Project service not available for context retrieval")
                return None
            
            context = self.project_service.get_file_with_complete_context(file_id)
            return context
            
        except Exception as e:
            logger.error(f"Error getting file context for {file_id}: {e}")
            return None

    def get_file_trace(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file trace information."""
        try:
            if not self.project_service:
                return None
            
            trace = self.project_service.get_file_trace(file_id)
            return trace
            
        except Exception as e:
            logger.error(f"Error getting file trace for {file_id}: {e}")
            return None

    def get_project_context_for_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get project context for a file."""
        try:
            if not self.project_service:
                return None
            
            context = self.project_service.get_project_context_for_file(file_id)
            return context
            
        except Exception as e:
            logger.error(f"Error getting project context for file {file_id}: {e}")
            return None

    def get_use_case_context_for_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get use case context for a file."""
        try:
            if not self.project_service:
                return None
            
            context = self.project_service.get_use_case_context_for_file(file_id)
            return context
            
        except Exception as e:
            logger.error(f"Error getting use case context for file {file_id}: {e}")
            return None

    def get_digital_twin_context_for_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get digital twin context for a file."""
        try:
            if not self.project_service:
                return None
            
            context = self.project_service.get_digital_twin_context_for_file(file_id)
            return context
            
        except Exception as e:
            logger.error(f"Error getting digital twin context for file {file_id}: {e}")
            return None

    def search_files_by_content(self, search_term: str, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search files by content using src/shared/ methods."""
        try:
            if not self.project_service:
                return []
            
            files = self.project_service.search_files_by_content(search_term, project_id)
            return files
            
        except Exception as e:
            logger.error(f"Error searching files with term '{search_term}': {e}")
            return []

    def get_related_files_for_file(self, file_id: str) -> List[Dict[str, Any]]:
        """Get related files for a file (same project)."""
        try:
            if not self.project_service:
                return []
            
            files = self.project_service.get_related_files_for_file(file_id)
            return files
            
        except Exception as e:
            logger.error(f"Error getting related files for file {file_id}: {e}")
            return []

    def get_digital_twin_health_for_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get digital twin health information for a file."""
        try:
            if not self.project_service:
                return None
            
            health = self.project_service.get_digital_twin_health_for_file(file_id)
            return health
            
        except Exception as e:
            logger.error(f"Error getting digital twin health for file {file_id}: {e}")
            return None
    
    def compare_techniques(self, query: str, technique_ids: List[str], 
                          project_id: Optional[str] = None, search_limit: int = 10) -> Dict[str, Any]:
        """Compare multiple RAG techniques on the same query"""
        try:
            logger.info(f"🔍 Comparing techniques: {technique_ids} for query: {query[:50]}...")
            
            comparison = self.rag_manager.compare_techniques(
                query=query,
                technique_ids=technique_ids,
                project_id=project_id,
                search_limit=search_limit
            )
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing techniques: {e}")
            raise e
    
    def get_technique_recommendations(self, query: str) -> List[Dict[str, Any]]:
        """Get technique recommendations for a query"""
        try:
            logger.info(f"🔍 Getting recommendations for query: {query[:50]}...")
            
            recommendations = self.rag_manager.get_technique_recommendations(query)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting technique recommendations: {e}")
            raise e
    
    def get_available_techniques(self) -> List[Dict[str, Any]]:
        """Get list of available RAG techniques"""
        try:
            logger.info("🔍 Getting available techniques...")
            
            techniques = self.rag_manager.get_available_techniques()
            
            return techniques
            
        except Exception as e:
            logger.error(f"Error getting available techniques: {e}")
            raise e
    
    def run_demo_queries(self) -> Dict[str, Any]:
        """Run demo queries to showcase the system"""
        try:
            logger.info("🚀 Running demo queries...")
            
            # Demo queries
            demo_queries = [
                "What are the motor specifications?",
                "Explain the system architecture",
                "What are the key components?",
                "How does the control system work?"
            ]
            
            results = []
            successful_queries = 0
            
            for query in demo_queries:
                try:
                    result = self.rag_manager.process_query(
                        query=query,
                        search_limit=5
                    )
                    
                    if 'error' not in result:
                        successful_queries += 1
                    
                    results.append({
                        "query": query,
                        "result": result,
                        "success": 'error' not in result
                    })
                    
                except Exception as e:
                    results.append({
                        "query": query,
                        "error": str(e),
                        "success": False
                    })
            
            return {
                "queries": results,
                "total_queries": len(demo_queries),
                "successful_queries": successful_queries
            }
            
        except Exception as e:
            logger.error(f"Error running demo queries: {e}")
            raise e
    
    def search_similar_documents(self, query: str, project_id: Optional[str] = None, 
                                limit: int = 10) -> Dict[str, Any]:
        """Search for similar documents using vector similarity"""
        try:
            logger.info(f"🔍 Searching similar documents for: {query[:50]}...")
            
            results = self.rag_manager.search_similar_documents(
                query=query,
                limit=limit,
                project_id=project_id
            )
            
            return {
                "query": query,
                "project_id": project_id,
                "results": results,
                "total_results": len(results)
            }
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise e 