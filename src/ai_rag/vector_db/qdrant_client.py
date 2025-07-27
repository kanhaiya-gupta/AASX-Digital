"""
Qdrant vector database client implementation.
"""

from typing import Dict, List, Any, Optional
from qdrant_client import QdrantClient as QdrantClientBase
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from qdrant_client.http.exceptions import UnexpectedResponse

from .base_client import VectorDBClient, VectorDBConnectionError, VectorDBOperationError


class QdrantClient(VectorDBClient):
    """Qdrant vector database client implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Qdrant client.
        
        Args:
            config: Configuration dictionary containing:
                - host: Qdrant server host
                - port: Qdrant server port
                - collection_name: Default collection name
                - api_key: API key (optional)
        """
        super().__init__(config)
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 6333)
        self.api_key = config.get('api_key')
        self.client = None
    
    def connect(self) -> bool:
        """Connect to Qdrant server."""
        try:
            if self.api_key:
                self.client = QdrantClientBase(
                    host=self.host,
                    port=self.port,
                    api_key=self.api_key
                )
            else:
                self.client = QdrantClientBase(
                    host=self.host,
                    port=self.port
                )
            
            # Test connection
            self.client.get_collections()
            self.is_connected = True
            
            # Ensure default collection exists
            self.ensure_collection()
            
            return True
            
        except Exception as e:
            raise VectorDBConnectionError(f"Failed to connect to Qdrant: {e}")
    
    def ensure_collection(self, collection_name: str = None, vector_size: int = 1536) -> bool:
        """Ensure collection exists, create if it doesn't."""
        collection_name = collection_name or self.collection_name
        
        try:
            if not self.collection_exists(collection_name):
                return self.create_collection(collection_name, vector_size)
            return True
        except Exception as e:
            raise VectorDBOperationError(f"Failed to ensure collection {collection_name}: {e}")
    
    def disconnect(self):
        """Disconnect from Qdrant server."""
        if self.client:
            self.client.close()
        self.is_connected = False
    
    def create_collection(self, collection_name: str = None, vector_size: int = 1536) -> bool:
        """Create a new collection in Qdrant."""
        if not self.is_connected:
            raise VectorDBConnectionError("Not connected to Qdrant")
        
        collection_name = collection_name or self.collection_name
        
        try:
            # Check if collection already exists
            collections = self.client.get_collections()
            existing_collections = [col.name for col in collections.collections]
            
            if collection_name in existing_collections:
                return True  # Collection already exists
            
            # Create collection
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            return True
            
        except Exception as e:
            raise VectorDBOperationError(f"Failed to create collection {collection_name}: {e}")
    
    def collection_exists(self, collection_name: str = None) -> bool:
        """Check if a collection exists."""
        if not self.is_connected:
            raise VectorDBConnectionError("Not connected to Qdrant")
        
        collection_name = collection_name or self.collection_name
        
        try:
            collections = self.client.get_collections()
            existing_collections = [col.name for col in collections.collections]
            return collection_name in existing_collections
            
        except Exception as e:
            raise VectorDBOperationError(f"Failed to check collection existence: {e}")
    
    def upsert_vectors(self, vectors: List[Dict[str, Any]], collection_name: str = None) -> bool:
        """Insert or update vectors in Qdrant."""
        if not self.is_connected:
            raise VectorDBConnectionError("Not connected to Qdrant")
        
        collection_name = collection_name or self.collection_name
        
        try:
            # Prepare points for Qdrant
            points = []
            for vector_data in vectors:
                vector_id = vector_data.get('id')
                if not vector_id:
                    # Generate ID from payload if not provided
                    payload = vector_data.get('payload', {})
                    project_id = payload.get('project_id', 'unknown')
                    filename = payload.get('source_file', 'unknown')
                    vector_id = self.generate_vector_id(project_id, filename)
                
                vector = vector_data.get('vector')
                payload = self.prepare_metadata(vector_data.get('payload', {}))
                
                # Validate vector
                if not self.validate_vector(vector):
                    raise VectorDBOperationError(f"Invalid vector format for ID {vector_id}")
                
                point = PointStruct(
                    id=vector_id,
                    vector=vector,
                    payload=payload
                )
                points.append(point)
            
            # Upsert points
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            return True
            
        except Exception as e:
            raise VectorDBOperationError(f"Failed to upsert vectors: {e}")
    
    def search_vectors(self, query_vector: List[float], limit: int = 10, 
                      collection_name: str = None, filter_dict: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search for similar vectors in Qdrant."""
        if not self.is_connected:
            raise VectorDBConnectionError("Not connected to Qdrant")
        
        collection_name = collection_name or self.collection_name
        
        try:
            # Prepare filter if provided
            filter_condition = None
            if filter_dict:
                filter_condition = self._build_filter(filter_dict)
            
            # Search vectors
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=filter_condition
            )
            
            # Convert results to standard format
            results = []
            for scored_point in search_result:
                result = {
                    'id': scored_point.id,
                    'score': scored_point.score,
                    'payload': scored_point.payload
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            raise VectorDBOperationError(f"Failed to search vectors: {e}")
    
    def delete_vectors(self, vector_ids: List[str], collection_name: str = None) -> bool:
        """Delete vectors by their IDs."""
        if not self.is_connected:
            raise VectorDBConnectionError("Not connected to Qdrant")
        
        collection_name = collection_name or self.collection_name
        
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=vector_ids
            )
            return True
            
        except Exception as e:
            raise VectorDBOperationError(f"Failed to delete vectors: {e}")
    
    def get_collection_info(self, collection_name: str = None) -> Dict[str, Any]:
        """Get information about a collection."""
        if not self.is_connected:
            raise VectorDBConnectionError("Not connected to Qdrant")
        
        collection_name = collection_name or self.collection_name
        
        try:
            collection_info = self.client.get_collection(collection_name)
            
            info = {
                'name': collection_info.name,
                'vectors_count': collection_info.vectors_count,
                'points_count': collection_info.points_count,
                'segments_count': collection_info.segments_count,
                'config': {
                    'vector_size': collection_info.config.params.vectors.size,
                    'distance': str(collection_info.config.params.vectors.distance)
                }
            }
            
            return info
            
        except Exception as e:
            raise VectorDBOperationError(f"Failed to get collection info: {e}")
    
    def _build_filter(self, filter_dict: Dict[str, Any]) -> Filter:
        """Build Qdrant filter from dictionary."""
        conditions = []
        
        for key, value in filter_dict.items():
            if isinstance(value, (str, int, float, bool)):
                condition = FieldCondition(
                    key=key,
                    match=MatchValue(value=value)
                )
                conditions.append(condition)
            elif isinstance(value, list):
                # Handle list values (e.g., "in" conditions)
                condition = FieldCondition(
                    key=key,
                    match=MatchValue(value=value)
                )
                conditions.append(condition)
        
        return Filter(must=conditions) if conditions else None
    
    def list_collections(self) -> List[str]:
        """List all collections in Qdrant."""
        if not self.is_connected:
            raise VectorDBConnectionError("Not connected to Qdrant")
        
        try:
            collections = self.client.get_collections()
            return [col.name for col in collections.collections]
            
        except Exception as e:
            raise VectorDBOperationError(f"Failed to list collections: {e}")
    
    def delete_collection(self, collection_name: str = None) -> bool:
        """Delete a collection."""
        if not self.is_connected:
            raise VectorDBConnectionError("Not connected to Qdrant")
        
        collection_name = collection_name or self.collection_name
        
        try:
            self.client.delete_collection(collection_name)
            return True
            
        except Exception as e:
            raise VectorDBOperationError(f"Failed to delete collection: {e}")
    
    def get_collection_name(self) -> str:
        """Get the current collection name."""
        return self.collection_name
