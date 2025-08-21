"""
Base vector database client providing common interface for different vector databases.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
import uuid
from datetime import datetime
from pathlib import Path

class VectorDBClient(ABC):
    """Abstract base class for vector database clients."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize vector database client.
        
        Args:
            config: Configuration dictionary for the vector database
        """
        self.config = config
        self.collection_name = config.get('collection_name', 'aasx_embeddings')
        self.is_connected = False
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to the vector database."""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Disconnect from the vector database."""
        pass
    
    @abstractmethod
    def create_collection(self, collection_name: str = None, vector_size: int = 1536) -> bool:
        """Create a new collection in the vector database."""
        pass
    
    @abstractmethod
    def collection_exists(self, collection_name: str = None) -> bool:
        """Check if a collection exists."""
        pass
    
    @abstractmethod
    def upsert_vectors(self, vectors: List[Dict[str, Any]], collection_name: str = None) -> bool:
        """
        Insert or update vectors in the database.
        
        Args:
            vectors: List of dictionaries containing:
                - id: Unique identifier
                - vector: Vector embedding
                - payload: Metadata dictionary
            collection_name: Name of the collection (optional)
        """
        pass
    
    @abstractmethod
    def search_vectors(self, query_vector: List[float], limit: int = 10, 
                      collection_name: str = None, filter_dict: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query vector embedding
            limit: Maximum number of results
            collection_name: Name of the collection (optional)
            filter_dict: Filter criteria for metadata
            
        Returns:
            List of dictionaries containing search results
        """
        pass
    
    @abstractmethod
    def delete_vectors(self, vector_ids: List[str], collection_name: str = None) -> bool:
        """Delete vectors by their IDs."""
        pass
    
    @abstractmethod
    def get_collection_info(self, collection_name: str = None) -> Dict[str, Any]:
        """Get information about a collection."""
        pass
    
    def generate_vector_id(self, project_id: str = None, filename: str = None) -> str:
        """
        Generate a unique vector ID using deterministic UUID approach.
        
        Args:
            project_id: Project ID for unique identification
            filename: Filename for unique identification
            
        Returns:
            Vector ID string (UUID format for Qdrant compatibility)
        """
        if project_id and filename:
            # Create a deterministic UUID using SHA256 hash of project_id + filename
            import hashlib
            import uuid
            
            combined_string = f"{project_id}_{filename}"
            hash_object = hashlib.sha256(combined_string.encode())
            hash_bytes = hash_object.digest()
            
            # Create a deterministic UUID using the hash bytes
            # This ensures the same project_id + filename always generates the same UUID
            deterministic_uuid = uuid.UUID(bytes=hash_bytes[:16])
            return str(deterministic_uuid)
        else:
            # Fallback: use hash of available information to create deterministic UUID
            import hashlib
            import uuid
            
            fallback_string = f"{project_id or 'unknown'}_{filename or 'unknown'}"
            hash_object = hashlib.sha256(fallback_string.encode())
            hash_bytes = hash_object.digest()
            
            deterministic_uuid = uuid.UUID(bytes=hash_bytes[:16])
            return str(deterministic_uuid)
    
    def validate_vector(self, vector: List[float], expected_size: int = 1536) -> bool:
        """
        Validate vector format and size.
        
        Args:
            vector: Vector to validate
            expected_size: Expected vector dimensions
            
        Returns:
            True if vector is valid, False otherwise
        """
        if not isinstance(vector, list):
            return False
        
        if len(vector) != expected_size:
            return False
        
        if not all(isinstance(x, (int, float)) for x in vector):
            return False
        
        return True
    
    def prepare_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare metadata for storage in vector database.
        
        Args:
            metadata: Raw metadata dictionary
            
        Returns:
            Processed metadata dictionary
        """
        processed_metadata = metadata.copy()
        
        # Add timestamp if not present
        if 'created_at' not in processed_metadata:
            processed_metadata['created_at'] = datetime.now().isoformat()
        
        # Ensure all values are serializable
        for key, value in processed_metadata.items():
            if isinstance(value, Path):
                processed_metadata[key] = str(value)
            elif not isinstance(value, (str, int, float, bool, list, dict)):
                processed_metadata[key] = str(value)
        
        return processed_metadata
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


class VectorDBError(Exception):
    """Custom exception for vector database operations."""
    pass


class VectorDBConnectionError(VectorDBError):
    """Exception raised when connection to vector database fails."""
    pass


class VectorDBOperationError(VectorDBError):
    """Exception raised when vector database operation fails."""
    pass
