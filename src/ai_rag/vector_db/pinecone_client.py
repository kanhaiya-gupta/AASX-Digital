"""
Pinecone Vector Database Client

This module provides integration with Pinecone vector database for:
- Storing embeddings and metadata
- Performing similarity searches
- Managing vector collections
- Batch operations
- Index management
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
import pinecone
from pinecone import Pinecone, ServerlessSpec
import numpy as np
import json
import time

logger = logging.getLogger(__name__)


@dataclass
class VectorRecord:
    """Represents a vector record in Pinecone."""
    id: str
    vector: List[float]
    metadata: Optional[Dict[str, Any]] = None
    sparse_values: Optional[Dict[str, List[float]]] = None


@dataclass
class SearchResult:
    """Represents a search result from Pinecone."""
    id: str
    score: float
    metadata: Optional[Dict[str, Any]] = None
    sparse_values: Optional[Dict[str, List[float]]] = None


class PineconeClient:
    """
    Pinecone vector database client.
    
    Provides comprehensive interface for:
    - Index management
    - Vector operations (upsert, query, delete)
    - Batch operations
    - Metadata filtering
    - Similarity search
    """
    
    def __init__(self,
                 api_key: str,
                 environment: str = "gcp-starter",
                 index_name: str = "aasx-vectors",
                 dimension: int = 1536,
                 metric: str = "cosine",
                 pod_type: str = "p1.x1",
                 enable_serverless: bool = False):
        """
        Initialize the Pinecone client.
        
        Args:
            api_key: Pinecone API key
            environment: Pinecone environment
            index_name: Name of the index
            dimension: Vector dimension
            metric: Distance metric (cosine, euclidean, dotproduct)
            pod_type: Pod type for the index
            enable_serverless: Whether to use serverless spec
        """
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
        self.dimension = dimension
        self.metric = metric
        self.pod_type = pod_type
        self.enable_serverless = enable_serverless
        
        # Initialize Pinecone
        self.pc = None
        self.index = None
        
        self._initialize_pinecone()
        
        logger.info(f"Initialized PineconeClient for index: {index_name}")
    
    def _initialize_pinecone(self):
        """Initialize Pinecone connection and index."""
        try:
            # Initialize Pinecone
            self.pc = Pinecone(api_key=self.api_key)
            
            # Check if index exists
            if self.index_name not in self.pc.list_indexes().names():
                self._create_index()
            else:
                # Connect to existing index
                self.index = self.pc.Index(self.index_name)
                logger.info(f"Connected to existing index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Error initializing Pinecone: {e}")
            raise
    
    def _create_index(self):
        """Create a new Pinecone index."""
        try:
            logger.info(f"Creating new index: {self.index_name}")
            
            if self.enable_serverless:
                # Create serverless index
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric=self.metric,
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
            else:
                # Create pod-based index
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric=self.metric,
                    pod_type=self.pod_type
                )
            
            # Wait for index to be ready
            while not self.pc.describe_index(self.index_name).status['ready']:
                time.sleep(1)
            
            # Connect to the index
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Index created and ready: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            raise
    
    def upsert_vector(self, vector_record: VectorRecord) -> bool:
        """
        Upsert a single vector record.
        
        Args:
            vector_record: VectorRecord object
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare upsert data
            upsert_data = {
                'id': vector_record.id,
                'values': vector_record.vector
            }
            
            if vector_record.metadata:
                upsert_data['metadata'] = vector_record.metadata
            
            if vector_record.sparse_values:
                upsert_data['sparse_values'] = vector_record.sparse_values
            
            # Upsert to index
            self.index.upsert(vectors=[upsert_data])
            
            logger.debug(f"Upserted vector: {vector_record.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting vector {vector_record.id}: {e}")
            return False
    
    def upsert_vectors(self, vector_records: List[VectorRecord]) -> Dict[str, Any]:
        """
        Upsert multiple vector records in batch.
        
        Args:
            vector_records: List of VectorRecord objects
            
        Returns:
            Dictionary with upsert results
        """
        try:
            # Prepare batch upsert data
            upsert_data = []
            for record in vector_records:
                data = {
                    'id': record.id,
                    'values': record.vector
                }
                
                if record.metadata:
                    data['metadata'] = record.metadata
                
                if record.sparse_values:
                    data['sparse_values'] = record.sparse_values
                
                upsert_data.append(data)
            
            # Batch upsert
            response = self.index.upsert(vectors=upsert_data)
            
            logger.info(f"Batch upserted {len(vector_records)} vectors")
            return {
                'success': True,
                'upserted_count': response.upserted_count,
                'total_count': len(vector_records)
            }
            
        except Exception as e:
            logger.error(f"Error batch upserting vectors: {e}")
            return {
                'success': False,
                'error': str(e),
                'total_count': len(vector_records)
            }
    
    def query_vector(self, 
                    query_vector: List[float],
                    top_k: int = 10,
                    filter_dict: Optional[Dict[str, Any]] = None,
                    include_metadata: bool = True,
                    include_values: bool = False) -> List[SearchResult]:
        """
        Query the index with a vector.
        
        Args:
            query_vector: Query vector
            top_k: Number of top results to return
            filter_dict: Metadata filter dictionary
            include_metadata: Whether to include metadata in results
            include_values: Whether to include vector values in results
            
        Returns:
            List of SearchResult objects
        """
        try:
            # Prepare query parameters
            query_params = {
                'vector': query_vector,
                'top_k': top_k,
                'include_metadata': include_metadata,
                'include_values': include_values
            }
            
            if filter_dict:
                query_params['filter'] = filter_dict
            
            # Query the index
            response = self.index.query(**query_params)
            
            # Convert to SearchResult objects
            results = []
            for match in response.matches:
                result = SearchResult(
                    id=match.id,
                    score=match.score,
                    metadata=match.metadata if include_metadata else None,
                    sparse_values=match.sparse_values if hasattr(match, 'sparse_values') else None
                )
                results.append(result)
            
            logger.debug(f"Query returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error querying vector: {e}")
            return []
    
    def query_text(self,
                  text: str,
                  text_embedding_model,
                  top_k: int = 10,
                  filter_dict: Optional[Dict[str, Any]] = None,
                  include_metadata: bool = True) -> List[SearchResult]:
        """
        Query the index with text (converts to embedding first).
        
        Args:
            text: Query text
            text_embedding_model: Model to generate embeddings
            top_k: Number of top results to return
            filter_dict: Metadata filter dictionary
            include_metadata: Whether to include metadata in results
            
        Returns:
            List of SearchResult objects
        """
        try:
            # Generate embedding for text
            embedding = asyncio.run(text_embedding_model.generate_embedding(text))
            
            # Query with embedding
            return self.query_vector(
                query_vector=embedding,
                top_k=top_k,
                filter_dict=filter_dict,
                include_metadata=include_metadata
            )
            
        except Exception as e:
            logger.error(f"Error querying text: {e}")
            return []
    
    def delete_vector(self, vector_id: str) -> bool:
        """
        Delete a vector by ID.
        
        Args:
            vector_id: ID of the vector to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.index.delete(ids=[vector_id])
            logger.debug(f"Deleted vector: {vector_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vector {vector_id}: {e}")
            return False
    
    def delete_vectors(self, vector_ids: List[str]) -> Dict[str, Any]:
        """
        Delete multiple vectors by IDs.
        
        Args:
            vector_ids: List of vector IDs to delete
            
        Returns:
            Dictionary with delete results
        """
        try:
            response = self.index.delete(ids=vector_ids)
            
            logger.info(f"Deleted {len(vector_ids)} vectors")
            return {
                'success': True,
                'deleted_count': len(vector_ids)
            }
            
        except Exception as e:
            logger.error(f"Error deleting vectors: {e}")
            return {
                'success': False,
                'error': str(e),
                'deleted_count': 0
            }
    
    def delete_by_filter(self, filter_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete vectors by metadata filter.
        
        Args:
            filter_dict: Metadata filter dictionary
            
        Returns:
            Dictionary with delete results
        """
        try:
            response = self.index.delete(filter=filter_dict)
            
            logger.info(f"Deleted vectors by filter: {filter_dict}")
            return {
                'success': True,
                'filter': filter_dict
            }
            
        except Exception as e:
            logger.error(f"Error deleting by filter: {e}")
            return {
                'success': False,
                'error': str(e),
                'filter': filter_dict
            }
    
    def fetch_vector(self, vector_id: str) -> Optional[VectorRecord]:
        """
        Fetch a vector by ID.
        
        Args:
            vector_id: ID of the vector to fetch
            
        Returns:
            VectorRecord object or None if not found
        """
        try:
            response = self.index.fetch(ids=[vector_id])
            
            if vector_id in response.vectors:
                vector_data = response.vectors[vector_id]
                return VectorRecord(
                    id=vector_id,
                    vector=vector_data.values,
                    metadata=vector_data.metadata,
                    sparse_values=vector_data.sparse_values if hasattr(vector_data, 'sparse_values') else None
                )
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error fetching vector {vector_id}: {e}")
            return None
    
    def fetch_vectors(self, vector_ids: List[str]) -> Dict[str, VectorRecord]:
        """
        Fetch multiple vectors by IDs.
        
        Args:
            vector_ids: List of vector IDs to fetch
            
        Returns:
            Dictionary mapping IDs to VectorRecord objects
        """
        try:
            response = self.index.fetch(ids=vector_ids)
            
            results = {}
            for vector_id, vector_data in response.vectors.items():
                results[vector_id] = VectorRecord(
                    id=vector_id,
                    vector=vector_data.values,
                    metadata=vector_data.metadata,
                    sparse_values=vector_data.sparse_values if hasattr(vector_data, 'sparse_values') else None
                )
            
            logger.debug(f"Fetched {len(results)} vectors")
            return results
            
        except Exception as e:
            logger.error(f"Error fetching vectors: {e}")
            return {}
    
    def update_metadata(self, vector_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Update metadata for a vector.
        
        Args:
            vector_id: ID of the vector
            metadata: New metadata dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Fetch current vector
            vector_record = self.fetch_vector(vector_id)
            if not vector_record:
                return False
            
            # Update metadata and upsert
            vector_record.metadata = metadata
            return self.upsert_vector(vector_record)
            
        except Exception as e:
            logger.error(f"Error updating metadata for {vector_id}: {e}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get index statistics.
        
        Returns:
            Dictionary with index statistics
        """
        try:
            stats = self.index.describe_index_stats()
            
            return {
                'total_vector_count': stats.total_vector_count,
                'dimension': stats.dimension,
                'index_fullness': stats.index_fullness,
                'namespaces': stats.namespaces
            }
            
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {}
    
    def list_namespaces(self) -> List[str]:
        """
        List all namespaces in the index.
        
        Returns:
            List of namespace names
        """
        try:
            stats = self.index.describe_index_stats()
            return list(stats.namespaces.keys())
            
        except Exception as e:
            logger.error(f"Error listing namespaces: {e}")
            return []
    
    def delete_namespace(self, namespace: str) -> bool:
        """
        Delete all vectors in a namespace.
        
        Args:
            namespace: Namespace to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.index.delete(namespace=namespace)
            logger.info(f"Deleted namespace: {namespace}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting namespace {namespace}: {e}")
            return False
    
    def create_namespace(self, namespace: str) -> bool:
        """
        Create a namespace (implicitly created when first vector is added).
        
        Args:
            namespace: Namespace name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Namespaces are created implicitly when vectors are added
            # This method is for documentation purposes
            logger.info(f"Namespace {namespace} will be created when first vector is added")
            return True
            
        except Exception as e:
            logger.error(f"Error creating namespace {namespace}: {e}")
            return False
    
    def search_similar(self,
                      query_vector: List[float],
                      namespace: str = "",
                      top_k: int = 10,
                      filter_dict: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """
        Search for similar vectors in a specific namespace.
        
        Args:
            query_vector: Query vector
            namespace: Namespace to search in
            top_k: Number of top results to return
            filter_dict: Metadata filter dictionary
            
        Returns:
            List of SearchResult objects
        """
        try:
            # Prepare query parameters
            query_params = {
                'vector': query_vector,
                'top_k': top_k,
                'include_metadata': True
            }
            
            if namespace:
                query_params['namespace'] = namespace
            
            if filter_dict:
                query_params['filter'] = filter_dict
            
            # Query the index
            response = self.index.query(**query_params)
            
            # Convert to SearchResult objects
            results = []
            for match in response.matches:
                result = SearchResult(
                    id=match.id,
                    score=match.score,
                    metadata=match.metadata
                )
                results.append(result)
            
            logger.debug(f"Similarity search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []
    
    def close(self):
        """Close the Pinecone connection."""
        try:
            if self.index:
                self.index.close()
            logger.info("Pinecone connection closed")
        except Exception as e:
            logger.error(f"Error closing Pinecone connection: {e}")


# Utility functions
def create_pinecone_client(api_key: str,
                          index_name: str = "aasx-vectors",
                          dimension: int = 1536,
                          environment: str = "gcp-starter") -> PineconeClient:
    """
    Create a Pinecone client with default settings.
    
    Args:
        api_key: Pinecone API key
        index_name: Name of the index
        dimension: Vector dimension
        environment: Pinecone environment
        
    Returns:
        PineconeClient instance
    """
    return PineconeClient(
        api_key=api_key,
        environment=environment,
        index_name=index_name,
        dimension=dimension
    )


def validate_vector(vector: List[float], dimension: int) -> bool:
    """
    Validate vector format and dimension.
    
    Args:
        vector: Vector to validate
        dimension: Expected dimension
        
    Returns:
        True if valid, False otherwise
    """
    try:
        if not isinstance(vector, list):
            return False
        
        if len(vector) != dimension:
            return False
        
        if not all(isinstance(x, (int, float)) for x in vector):
            return False
        
        return True
        
    except Exception:
        return False


def normalize_vector(vector: List[float]) -> List[float]:
    """
    Normalize a vector to unit length.
    
    Args:
        vector: Vector to normalize
        
    Returns:
        Normalized vector
    """
    try:
        vector_array = np.array(vector)
        norm = np.linalg.norm(vector_array)
        
        if norm > 0:
            normalized = vector_array / norm
            return normalized.tolist()
        else:
            return vector
            
    except Exception as e:
        logger.error(f"Error normalizing vector: {e}")
        return vector





