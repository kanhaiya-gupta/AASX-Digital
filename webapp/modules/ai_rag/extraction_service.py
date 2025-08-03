"""
File ID Extraction Service
==========================

Extracts file_id from natural language queries to enable reverse engineering.
This service uses pattern matching and search capabilities to identify file references.
"""

import re
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class FileIDExtractionService:
    """
    Service for extracting file_id from natural language queries.
    Uses pattern matching and search capabilities to identify file references.
    """
    
    def __init__(self, project_service=None):
        """Initialize extraction service with project service for search capabilities"""
        self.project_service = project_service
        logger.info("File ID Extraction Service initialized")
    
    def extract_file_id_from_query(self, query: str) -> Optional[str]:
        """
        Extract file_id from natural language query using multiple strategies.
        
        Args:
            query: Natural language query (e.g., "What's in file ABC123?", "Tell me about document XYZ789")
            
        Returns:
            Extracted file_id if found, None otherwise
        """
        try:
            logger.info(f"🔍 Extracting file_id from query: {query[:50]}...")
            
            # Strategy 1: Direct pattern matching
            file_id = self._extract_by_patterns(query)
            if file_id:
                logger.info(f"✅ File ID extracted by pattern: {file_id}")
                return file_id
            
            # Strategy 2: Search by filename
            file_id = self._extract_by_filename_search(query)
            if file_id:
                logger.info(f"✅ File ID extracted by filename search: {file_id}")
                return file_id
            
            # Strategy 3: Search by content keywords
            file_id = self._extract_by_content_search(query)
            if file_id:
                logger.info(f"✅ File ID extracted by content search: {file_id}")
                return file_id
            
            logger.warning(f"⚠️ No file_id found in query: {query[:50]}...")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting file_id from query: {e}")
            return None
    
    def _extract_by_patterns(self, query: str) -> Optional[str]:
        """
        Extract file_id using regex patterns for common file reference formats.
        
        Patterns:
        - "file ABC123" or "document XYZ789"
        - "ABC123" (standalone UUID-like patterns)
        - "file_id: ABC123" or "id: XYZ789"
        - "filename: ABC123.aasx" or "document: XYZ789.json"
        """
        try:
            # Common patterns for file references
            patterns = [
                # Explicit file references
                r'file\s+([A-Za-z0-9_-]{8,})',
                r'document\s+([A-Za-z0-9_-]{8,})',
                r'file_id\s*:\s*([A-Za-z0-9_-]{8,})',
                r'id\s*:\s*([A-Za-z0-9_-]{8,})',
                
                # Filename patterns
                r'filename\s*:\s*([A-Za-z0-9_-]{8,})',
                r'document\s*:\s*([A-Za-z0-9_-]{8,})',
                
                # Standalone UUID-like patterns (8+ characters)
                r'\b([A-Za-z0-9_-]{8,})\b',
                
                # File extensions
                r'([A-Za-z0-9_-]{8,})\.(aasx|json|xml|pdf|txt)',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, query, re.IGNORECASE)
                if matches:
                    # Return the first match that looks like a file_id
                    for match in matches:
                        if self._is_valid_file_id_format(match):
                            return match
            
            return None
            
        except Exception as e:
            logger.error(f"Error in pattern extraction: {e}")
            return None
    
    def _extract_by_filename_search(self, query: str) -> Optional[str]:
        """
        Extract file_id by searching for files with matching filenames.
        Uses the project service to search through available files.
        """
        try:
            if not self.project_service:
                return None
            
            # Extract potential filename keywords from query
            filename_keywords = self._extract_filename_keywords(query)
            if not filename_keywords:
                return None
            
            # Search for files with these keywords
            for keyword in filename_keywords:
                files = self.project_service.search_files_by_content(keyword)
                if files:
                    # Return the first matching file_id
                    return files[0].get("file_id")
            
            return None
            
        except Exception as e:
            logger.error(f"Error in filename search extraction: {e}")
            return None
    
    def _extract_by_content_search(self, query: str) -> Optional[str]:
        """
        Extract file_id by searching for files with content matching the query.
        Uses the project service to search through file content.
        """
        try:
            if not self.project_service:
                return None
            
            # Extract meaningful keywords from query
            keywords = self._extract_content_keywords(query)
            if not keywords:
                return None
            
            # Search for files with these keywords
            for keyword in keywords:
                files = self.project_service.search_files_by_content(keyword)
                if files:
                    # Return the first matching file_id
                    return files[0].get("file_id")
            
            return None
            
        except Exception as e:
            logger.error(f"Error in content search extraction: {e}")
            return None
    
    def _extract_filename_keywords(self, query: str) -> List[str]:
        """Extract potential filename keywords from query."""
        try:
            # Look for words that might be filenames
            words = query.split()
            filename_keywords = []
            
            for word in words:
                # Clean the word
                clean_word = re.sub(r'[^\w\-_.]', '', word)
                
                # Check if it looks like a filename
                if (len(clean_word) >= 3 and 
                    not clean_word.lower() in ['file', 'document', 'what', 'tell', 'about', 'in', 'the', 'is', 'are', 'was', 'were']):
                    filename_keywords.append(clean_word)
            
            return filename_keywords[:5]  # Limit to 5 keywords
            
        except Exception as e:
            logger.error(f"Error extracting filename keywords: {e}")
            return []
    
    def _extract_content_keywords(self, query: str) -> List[str]:
        """Extract meaningful content keywords from query."""
        try:
            # Remove common question words and stop words
            stop_words = {
                'what', 'tell', 'me', 'about', 'in', 'the', 'is', 'are', 'was', 'were',
                'file', 'document', 'show', 'get', 'find', 'search', 'query', 'question'
            }
            
            words = query.lower().split()
            content_keywords = []
            
            for word in words:
                clean_word = re.sub(r'[^\w]', '', word)
                if (len(clean_word) >= 3 and 
                    clean_word not in stop_words and
                    not clean_word.isdigit()):
                    content_keywords.append(clean_word)
            
            return content_keywords[:5]  # Limit to 5 keywords
            
        except Exception as e:
            logger.error(f"Error extracting content keywords: {e}")
            return []
    
    def _is_valid_file_id_format(self, candidate: str) -> bool:
        """
        Check if a candidate string looks like a valid file_id format.
        
        Valid formats:
        - UUID-like: 8-4-4-4-12 characters (e.g., 12345678-1234-1234-1234-123456789012)
        - Simple ID: 8+ alphanumeric characters
        """
        try:
            # Remove any file extensions
            base_id = candidate.split('.')[0]
            
            # Check for UUID format
            uuid_pattern = r'^[A-Za-z0-9]{8}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{12}$'
            if re.match(uuid_pattern, base_id):
                return True
            
            # Check for simple ID format (8+ alphanumeric characters)
            simple_pattern = r'^[A-Za-z0-9_-]{8,}$'
            if re.match(simple_pattern, base_id):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error validating file_id format: {e}")
            return False
    
    def get_extraction_statistics(self) -> Dict[str, Any]:
        """Get statistics about file_id extraction performance."""
        try:
            return {
                "service_name": "FileIDExtractionService",
                "status": "active",
                "strategies": [
                    "pattern_matching",
                    "filename_search", 
                    "content_search"
                ],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting extraction statistics: {e}")
            return {"error": str(e)}
    
    def test_extraction(self, test_queries: List[str]) -> List[Dict[str, Any]]:
        """
        Test file_id extraction with a list of queries.
        Useful for validating extraction accuracy.
        """
        try:
            results = []
            
            for query in test_queries:
                start_time = datetime.now()
                file_id = self.extract_file_id_from_query(query)
                end_time = datetime.now()
                
                result = {
                    "query": query,
                    "extracted_file_id": file_id,
                    "success": file_id is not None,
                    "extraction_time": (end_time - start_time).total_seconds(),
                    "timestamp": datetime.now().isoformat()
                }
                
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing extraction: {e}")
            return [{"error": str(e)}] 