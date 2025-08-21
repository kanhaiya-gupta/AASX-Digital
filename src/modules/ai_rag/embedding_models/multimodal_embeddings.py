"""
Multimodal Embeddings Module

This module provides unified embedding capabilities for multiple data types:
- Text data
- Image data  
- Structured data (JSON, XML, etc.)
- Graph data
- Mixed content

It integrates with various embedding models and provides a consistent interface
for generating embeddings across different modalities.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
import numpy as np
from PIL import Image
import io
import base64

# Import specialized embedding modules
from .text_embeddings import TextEmbeddingModel
from .image_embeddings import ImageEmbeddingModel
from .base_embeddings import BaseEmbeddingModel

logger = logging.getLogger(__name__)


@dataclass
class MultimodalContent:
    """Represents content that can contain multiple data types."""
    text_content: Optional[str] = None
    image_content: Optional[bytes] = None
    structured_content: Optional[Dict[str, Any]] = None
    graph_content: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MultimodalEmbedding:
    """Represents embeddings for multimodal content."""
    text_embedding: Optional[List[float]] = None
    image_embedding: Optional[List[float]] = None
    structured_embedding: Optional[List[float]] = None
    graph_embedding: Optional[List[float]] = None
    combined_embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None


class MultimodalEmbeddingModel(BaseEmbeddingModel):
    """
    Unified embedding model for multiple data types.
    
    This class provides a single interface for generating embeddings
    from various types of content, including text, images, structured data,
    and graphs.
    """
    
    def __init__(self, 
                 text_model_name: str = "text-embedding-ada-002",
                 image_model_name: str = "clip-vit-base-patch32",
                 structured_model_name: str = "text-embedding-ada-002",
                 graph_model_name: str = "text-embedding-ada-002",
                 embedding_dimension: int = 1536,
                 max_text_length: int = 8192,
                 image_size: Tuple[int, int] = (224, 224),
                 combine_strategy: str = "weighted_average"):
        """
        Initialize the multimodal embedding model.
        
        Args:
            text_model_name: Name of the text embedding model
            image_model_name: Name of the image embedding model
            structured_model_name: Name of the structured data embedding model
            graph_model_name: Name of the graph embedding model
            embedding_dimension: Dimension of the output embeddings
            max_text_length: Maximum text length for embeddings
            image_size: Target size for image processing
            combine_strategy: Strategy for combining multiple embeddings
        """
        super().__init__(embedding_dimension=embedding_dimension)
        
        self.text_model_name = text_model_name
        self.image_model_name = image_model_name
        self.structured_model_name = structured_model_name
        self.graph_model_name = graph_model_name
        self.max_text_length = max_text_length
        self.image_size = image_size
        self.combine_strategy = combine_strategy
        
        # Initialize specialized embedding models
        self.text_embedder = TextEmbeddingModel(
            model_name=text_model_name,
            embedding_dimension=embedding_dimension,
            max_length=max_text_length
        )
        
        self.image_embedder = ImageEmbeddingModel(
            model_name=image_model_name,
            embedding_dimension=embedding_dimension,
            image_size=image_size
        )
        
        # For structured and graph data, we'll use text embedding with JSON serialization
        self.structured_embedder = TextEmbeddingModel(
            model_name=structured_model_name,
            embedding_dimension=embedding_dimension,
            max_length=max_text_length
        )
        
        self.graph_embedder = TextEmbeddingModel(
            model_name=graph_model_name,
            embedding_dimension=embedding_dimension,
            max_length=max_text_length
        )
        
        logger.info(f"Initialized MultimodalEmbeddingModel with {combine_strategy} strategy")
    
    async def generate_embedding(self, content: MultimodalContent) -> MultimodalEmbedding:
        """
        Generate embeddings for multimodal content.
        
        Args:
            content: MultimodalContent object containing various data types
            
        Returns:
            MultimodalEmbedding object with embeddings for each content type
        """
        try:
            embedding = MultimodalEmbedding(metadata=content.metadata or {})
            
            # Generate text embedding if text content exists
            if content.text_content:
                embedding.text_embedding = await self.text_embedder.generate_embedding(
                    content.text_content
                )
                logger.debug(f"Generated text embedding: {len(embedding.text_embedding)} dimensions")
            
            # Generate image embedding if image content exists
            if content.image_content:
                embedding.image_embedding = await self.image_embedder.generate_embedding(
                    content.image_content
                )
                logger.debug(f"Generated image embedding: {len(embedding.image_embedding)} dimensions")
            
            # Generate structured data embedding if structured content exists
            if content.structured_content:
                structured_text = self._serialize_structured_content(content.structured_content)
                embedding.structured_embedding = await self.structured_embedder.generate_embedding(
                    structured_text
                )
                logger.debug(f"Generated structured embedding: {len(embedding.structured_embedding)} dimensions")
            
            # Generate graph embedding if graph content exists
            if content.graph_content:
                graph_text = self._serialize_graph_content(content.graph_content)
                embedding.graph_embedding = await self.graph_embedder.generate_embedding(
                    graph_text
                )
                logger.debug(f"Generated graph embedding: {len(embedding.graph_embedding)} dimensions")
            
            # Combine embeddings if multiple types exist
            embedding.combined_embedding = self._combine_embeddings(embedding)
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating multimodal embedding: {e}")
            raise
    
    def _serialize_structured_content(self, content: Dict[str, Any]) -> str:
        """
        Serialize structured content to text for embedding.
        
        Args:
            content: Structured data dictionary
            
        Returns:
            Serialized text representation
        """
        try:
            # Convert to JSON and clean up for embedding
            json_str = json.dumps(content, sort_keys=True, separators=(',', ':'))
            
            # Truncate if too long
            if len(json_str) > self.max_text_length:
                json_str = json_str[:self.max_text_length-3] + "..."
            
            return f"structured_data: {json_str}"
            
        except Exception as e:
            logger.warning(f"Error serializing structured content: {e}")
            return f"structured_data: {str(content)}"
    
    def _serialize_graph_content(self, content: Dict[str, Any]) -> str:
        """
        Serialize graph content to text for embedding.
        
        Args:
            content: Graph data dictionary
            
        Returns:
            Serialized text representation
        """
        try:
            # Extract key graph information
            nodes = content.get('nodes', [])
            edges = content.get('edges', [])
            
            # Create a text representation
            graph_text = f"graph with {len(nodes)} nodes and {len(edges)} edges"
            
            # Add node information (first few nodes)
            if nodes:
                node_info = []
                for i, node in enumerate(nodes[:5]):  # Limit to first 5 nodes
                    node_type = node.get('type', 'unknown')
                    node_label = node.get('label', 'unnamed')
                    node_info.append(f"node{i}: {node_type} - {node_label}")
                
                graph_text += f". Nodes: {', '.join(node_info)}"
                if len(nodes) > 5:
                    graph_text += f" and {len(nodes) - 5} more"
            
            # Add edge information (first few edges)
            if edges:
                edge_info = []
                for i, edge in enumerate(edges[:5]):  # Limit to first 5 edges
                    source = edge.get('source', 'unknown')
                    target = edge.get('target', 'unknown')
                    edge_type = edge.get('type', 'unknown')
                    edge_info.append(f"edge{i}: {source}->{target} ({edge_type})")
                
                graph_text += f". Edges: {', '.join(edge_info)}"
                if len(edges) > 5:
                    graph_text += f" and {len(edges) - 5} more"
            
            # Truncate if too long
            if len(graph_text) > self.max_text_length:
                graph_text = graph_text[:self.max_text_length-3] + "..."
            
            return f"graph_data: {graph_text}"
            
        except Exception as e:
            logger.warning(f"Error serializing graph content: {e}")
            return f"graph_data: {str(content)}"
    
    def _combine_embeddings(self, embedding: MultimodalEmbedding) -> Optional[List[float]]:
        """
        Combine multiple embeddings into a single embedding.
        
        Args:
            embedding: MultimodalEmbedding object with individual embeddings
            
        Returns:
            Combined embedding vector
        """
        try:
            # Collect all available embeddings
            available_embeddings = []
            
            if embedding.text_embedding:
                available_embeddings.append(('text', embedding.text_embedding))
            if embedding.image_embedding:
                available_embeddings.append(('image', embedding.image_embedding))
            if embedding.structured_embedding:
                available_embeddings.append(('structured', embedding.structured_embedding))
            if embedding.graph_embedding:
                available_embeddings.append(('graph', embedding.graph_embedding))
            
            if not available_embeddings:
                return None
            
            if len(available_embeddings) == 1:
                # Only one embedding type, return it directly
                return available_embeddings[0][1]
            
            # Multiple embeddings, combine them
            if self.combine_strategy == "weighted_average":
                return self._weighted_average_combine(available_embeddings)
            elif self.combine_strategy == "concatenation":
                return self._concatenation_combine(available_embeddings)
            elif self.combine_strategy == "max_pooling":
                return self._max_pooling_combine(available_embeddings)
            else:
                logger.warning(f"Unknown combine strategy: {self.combine_strategy}, using weighted average")
                return self._weighted_average_combine(available_embeddings)
                
        except Exception as e:
            logger.error(f"Error combining embeddings: {e}")
            return None
    
    def _weighted_average_combine(self, embeddings: List[Tuple[str, List[float]]]) -> List[float]:
        """
        Combine embeddings using weighted average.
        
        Args:
            embeddings: List of (type, embedding) tuples
            
        Returns:
            Combined embedding vector
        """
        # Define weights for different content types
        weights = {
            'text': 0.4,
            'image': 0.3,
            'structured': 0.2,
            'graph': 0.1
        }
        
        # Normalize weights for available types
        available_weights = {emb_type: weights.get(emb_type, 0.1) for emb_type, _ in embeddings}
        total_weight = sum(available_weights.values())
        normalized_weights = {emb_type: weight / total_weight for emb_type, weight in available_weights.items()}
        
        # Calculate weighted average
        combined = np.zeros(self.embedding_dimension)
        for emb_type, embedding in embeddings:
            weight = normalized_weights[emb_type]
            combined += np.array(embedding) * weight
        
        return combined.tolist()
    
    def _concatenation_combine(self, embeddings: List[Tuple[str, List[float]]]) -> List[float]:
        """
        Combine embeddings using concatenation.
        
        Args:
            embeddings: List of (type, embedding) tuples
            
        Returns:
            Combined embedding vector
        """
        # Concatenate all embeddings
        combined = []
        for _, embedding in embeddings:
            combined.extend(embedding)
        
        # If the combined vector is too long, truncate or pad
        if len(combined) > self.embedding_dimension:
            combined = combined[:self.embedding_dimension]
        elif len(combined) < self.embedding_dimension:
            # Pad with zeros
            combined.extend([0.0] * (self.embedding_dimension - len(combined)))
        
        return combined
    
    def _max_pooling_combine(self, embeddings: List[Tuple[str, List[float]]]) -> List[float]:
        """
        Combine embeddings using max pooling.
        
        Args:
            embeddings: List of (type, embedding) tuples
            
        Returns:
            Combined embedding vector
        """
        # Convert to numpy arrays
        embedding_arrays = [np.array(embedding) for _, embedding in embeddings]
        
        # Stack arrays and take maximum along axis 0
        stacked = np.stack(embedding_arrays)
        combined = np.max(stacked, axis=0)
        
        return combined.tolist()
    
    async def generate_batch_embeddings(self, contents: List[MultimodalContent]) -> List[MultimodalEmbedding]:
        """
        Generate embeddings for a batch of multimodal content.
        
        Args:
            contents: List of MultimodalContent objects
            
        Returns:
            List of MultimodalEmbedding objects
        """
        try:
            tasks = [self.generate_embedding(content) for content in contents]
            embeddings = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions
            results = []
            for i, embedding in enumerate(embeddings):
                if isinstance(embedding, Exception):
                    logger.error(f"Error generating embedding for content {i}: {embedding}")
                    results.append(None)
                else:
                    results.append(embedding)
            
            return results
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embeddings."""
        return self.embedding_dimension
    
    def get_supported_content_types(self) -> List[str]:
        """Get list of supported content types."""
        return ['text', 'image', 'structured', 'graph']
    
    def get_combine_strategies(self) -> List[str]:
        """Get list of available combination strategies."""
        return ['weighted_average', 'concatenation', 'max_pooling']


# Utility functions for creating multimodal content
def create_text_content(text: str, metadata: Optional[Dict[str, Any]] = None) -> MultimodalContent:
    """Create multimodal content with text only."""
    return MultimodalContent(
        text_content=text,
        metadata=metadata
    )


def create_image_content(image_bytes: bytes, metadata: Optional[Dict[str, Any]] = None) -> MultimodalContent:
    """Create multimodal content with image only."""
    return MultimodalContent(
        image_content=image_bytes,
        metadata=metadata
    )


def create_structured_content(data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> MultimodalContent:
    """Create multimodal content with structured data only."""
    return MultimodalContent(
        structured_content=data,
        metadata=metadata
    )


def create_graph_content(graph_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> MultimodalContent:
    """Create multimodal content with graph data only."""
    return MultimodalContent(
        graph_content=graph_data,
        metadata=metadata
    )


def create_mixed_content(text: Optional[str] = None,
                        image_bytes: Optional[bytes] = None,
                        structured_data: Optional[Dict[str, Any]] = None,
                        graph_data: Optional[Dict[str, Any]] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> MultimodalContent:
    """Create multimodal content with multiple data types."""
    return MultimodalContent(
        text_content=text,
        image_content=image_bytes,
        structured_content=structured_data,
        graph_content=graph_data,
        metadata=metadata
    )
