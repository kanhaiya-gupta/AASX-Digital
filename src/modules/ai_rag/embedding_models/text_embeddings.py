"""
Text embedding models for generating vector embeddings from text content.
"""

import os
from typing import List, Dict, Any, Optional
import openai
from sentence_transformers import SentenceTransformer
import numpy as np

from src.ai_rag.config import EMBEDDING_MODELS_CONFIG
from src.shared.utils import setup_logging


class TextEmbeddingModel:
    """Text embedding model supporting multiple providers."""
    
    def __init__(self, provider: str = None, model_name: str = None, api_key: str = None):
        """
        Initialize text embedding model.
        
        Args:
            provider: Embedding provider ('openai' or 'sentence_transformers')
            model_name: Model name to use
            api_key: API key for the provider
        """
        self.logger = setup_logging("text_embeddings")
        
        # Get configuration
        config = EMBEDDING_MODELS_CONFIG.get('text', {})
        self.provider = provider or config.get('provider', 'openai')
        self.model_name = model_name or config.get('model', 'text-embedding-ada-002')
        self.api_key = api_key or config.get('api_key')
        self.dimensions = config.get('dimensions', 1536)
        
        # Initialize provider
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the embedding provider."""
        if self.provider == 'openai':
            self._initialize_openai()
        elif self.provider == 'sentence_transformers':
            self._initialize_sentence_transformers()
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _initialize_openai(self):
        """Initialize OpenAI embedding provider."""
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        # Use new OpenAI client format
        self.client = openai.OpenAI(api_key=self.api_key)
        self.logger.info(f"Initialized OpenAI embedding model: {self.model_name}")
    
    def _initialize_sentence_transformers(self):
        """Initialize SentenceTransformers embedding provider."""
        try:
            self.model = SentenceTransformer(self.model_name)
            self.logger.info(f"Initialized SentenceTransformers model: {self.model_name}")
        except Exception as e:
            raise ValueError(f"Failed to initialize SentenceTransformers model: {e}")
    
    def embed_text(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding, or None if failed
        """
        try:
            if self.provider == 'openai':
                return self._embed_openai(text)
            elif self.provider == 'sentence_transformers':
                return self._embed_sentence_transformers(text)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            self.logger.error(f"Failed to embed text: {e}")
            return None
    
    def embed_texts(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings (some may be None if failed)
        """
        embeddings = []
        
        for text in texts:
            embedding = self.embed_text(text)
            embeddings.append(embedding)
        
        return embeddings
    
    def _embed_openai(self, text: str) -> List[float]:
        """Generate embedding using OpenAI."""
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model_name
            )
            return response.data[0].embedding
            
        except Exception as e:
            self.logger.error(f"OpenAI embedding failed: {e}")
            raise
    
    def _embed_sentence_transformers(self, text: str) -> List[float]:
        """Generate embedding using SentenceTransformers."""
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
            
        except Exception as e:
            self.logger.error(f"SentenceTransformers embedding failed: {e}")
            raise
    
    def get_embedding_dimensions(self) -> int:
        """Get the dimensionality of the embeddings."""
        return self.dimensions
    
    def validate_text(self, text: str) -> bool:
        """
        Validate text for embedding.
        
        Args:
            text: Text to validate
            
        Returns:
            True if text is valid for embedding
        """
        if not text or not isinstance(text, str):
            return False
        
        if len(text.strip()) == 0:
            return False
        
        # Check for maximum length (OpenAI has limits)
        # OpenAI text-embedding-ada-002 has a limit of ~8192 tokens
        # Roughly 1 token = 4 characters, so limit to ~32000 characters
        if self.provider == 'openai' and len(text) > 32000:
            self.logger.warning(f"Text too long for OpenAI embedding: {len(text)} characters")
            return False
        
        return True
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """
        Split text into chunks for embedding.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum size of each chunk (in characters)
            overlap: Overlap between chunks (in characters)
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at word boundary
            if end < len(text):
                # Find last space before end
                last_space = text.rfind(' ', start, end)
                if last_space > start:
                    end = last_space
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    def embed_text_with_chunking(self, text: str, chunk_size: int = 1000, 
                                overlap: int = 100) -> List[Dict[str, Any]]:
        """
        Embed text with automatic chunking.
        
        Args:
            text: Text to embed
            chunk_size: Maximum size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of dictionaries containing chunk text and embedding
        """
        if not self.validate_text(text):
            return []
        
        chunks = self.chunk_text(text, chunk_size, overlap)
        results = []
        
        for i, chunk in enumerate(chunks):
            embedding = self.embed_text(chunk)
            if embedding:
                result = {
                    'chunk_index': i,
                    'chunk_text': chunk,
                    'embedding': embedding,
                    'chunk_size': len(chunk)
                }
                results.append(result)
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            'provider': self.provider,
            'model_name': self.model_name,
            'dimensions': self.dimensions,
            'api_key_configured': bool(self.api_key) if self.provider == 'openai' else True
        }


class TextEmbeddingManager:
    """Manager for text embedding operations."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize text embedding manager.
        
        Args:
            config: Configuration dictionary
        """
        self.logger = setup_logging("text_embedding_manager")
        self.config = config or {}
        self.models = {}
    
    def get_model(self, provider: str = None) -> TextEmbeddingModel:
        """
        Get or create an embedding model for the specified provider.
        
        Args:
            provider: Embedding provider
            
        Returns:
            TextEmbeddingModel instance
        """
        provider = provider or 'openai'
        
        if provider not in self.models:
            self.models[provider] = TextEmbeddingModel(provider=provider)
            self.logger.info(f"Created new embedding model for provider: {provider}")
        
        return self.models[provider]
    
    def embed_project_texts(self, project_id: str, texts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Embed multiple texts for a project.
        
        Args:
            project_id: Project identifier
            texts: List of dictionaries containing text data
            
        Returns:
            List of dictionaries with embeddings
        """
        model = self.get_model()
        results = []
        
        for text_data in texts:
            text = text_data.get('text', '')
            metadata = text_data.get('metadata', {})
            
            if not model.validate_text(text):
                self.logger.warning(f"Invalid text for project {project_id}")
                continue
            
            embedding = model.embed_text(text)
            if embedding:
                result = {
                    'project_id': project_id,
                    'text': text,
                    'embedding': embedding,
                    'metadata': metadata,
                    'embedding_model': model.get_model_info()
                }
                results.append(result)
        
        return results
    
    def close(self):
        """Clean up resources."""
        self.models.clear()
        self.logger.info("Text embedding manager closed")
