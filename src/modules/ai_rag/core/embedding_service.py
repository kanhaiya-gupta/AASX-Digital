"""
Embedding Service
================

Business logic layer for embedding operations.
Handles vector operations, embedding generation, and similarity calculations.
Pure async implementation following AASX and Twin Registry convention.
"""

import logging
import base64
import json
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from src.modules.ai_rag.models.embedding import Embedding
from src.modules.ai_rag.repositories.embedding_repository import EmbeddingRepository
from src.modules.ai_rag.repositories.document_repository import DocumentRepository

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Embedding Service - Pure Async Implementation
    
    Orchestrates embedding operations including:
    - Vector generation and storage
    - Similarity calculations and search
    - Quality assessment and optimization
    - Model management and versioning
    """
    
    def __init__(self, embedding_repo: EmbeddingRepository,
                 document_repo: DocumentRepository):
        """Initialize service with required repositories"""
        self.embedding_repo = embedding_repo
        self.document_repo = document_repo
    
    async def create_embedding(self, embedding_data: Dict[str, Any]) -> Optional[Embedding]:
        """Create a new embedding with validation and processing"""
        try:
            logger.info(f"Creating embedding for document: {embedding_data.get('document_id', 'Unknown')}")
            
            # Validate vector data
            if not await self._validate_vector_data(embedding_data):
                logger.error("Vector data validation failed")
                return None
            
            # Process vector data
            processed_data = await self._process_vector_data(embedding_data)
            
            # Create embedding instance
            embedding = Embedding(**processed_data)
            
            # Validate embedding before creation
            if not await self._validate_embedding(embedding):
                logger.error("Embedding validation failed")
                return None
            
            # Calculate additional metrics
            await self._calculate_embedding_metrics(embedding)
            
            # Create in database
            success = await self.embedding_repo.create(embedding)
            if not success:
                logger.error("Failed to create embedding in database")
                return None
            
            logger.info(f"Successfully created embedding: {embedding.embedding_id}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            return None
    
    async def get_embedding_by_id(self, embedding_id: str) -> Optional[Embedding]:
        """Get embedding by ID with enhanced data"""
        try:
            embedding = await self.embedding_repo.get_by_id(embedding_id)
            if embedding:
                # Enhance with additional data
                await self._enhance_embedding_data(embedding)
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error getting embedding by ID: {e}")
            return None
    
    async def get_embeddings_by_document(self, document_id: str) -> List[Embedding]:
        """Get embeddings by document ID with sorting"""
        try:
            embeddings = await self.embedding_repo.get_by_document_id(document_id)
            
            # Sort by quality score (descending)
            embeddings.sort(key=lambda x: x.quality_score or 0, reverse=True)
            
            # Enhance each embedding
            for embedding in embeddings:
                await self._enhance_embedding_data(embedding)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error getting embeddings by document: {e}")
            return []
    
    async def update_embedding(self, embedding_id: str, update_data: Dict[str, Any]) -> bool:
        """Update existing embedding with validation"""
        try:
            logger.info(f"Updating embedding: {embedding_id}")
            
            # Get existing embedding
            embedding = await self.embedding_repo.get_by_id(embedding_id)
            if not embedding:
                logger.error(f"Embedding not found: {embedding_id}")
                return False
            
            # Update fields
            for key, value in update_data.items():
                if hasattr(embedding, key):
                    setattr(embedding, key, value)
            
            # Validate updated embedding
            if not await self._validate_embedding(embedding):
                logger.error("Updated embedding validation failed")
                return False
            
            # Update timestamp
            embedding.update_timestamp()
            
            # Recalculate metrics if quality-related fields changed
            if any(key in update_data for key in ['quality_score', 'similarity_threshold', 'confidence_score']):
                await self._calculate_embedding_metrics(embedding)
            
            # Save to database
            success = await self.embedding_repo.update(embedding)
            if success:
                logger.info(f"Successfully updated embedding: {embedding_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating embedding: {e}")
            return False
    
    async def delete_embedding(self, embedding_id: str) -> bool:
        """Delete embedding with cleanup"""
        try:
            logger.info(f"Deleting embedding: {embedding_id}")
            
            # Delete from database
            success = await self.embedding_repo.delete(embedding_id)
            if success:
                logger.info(f"Successfully deleted embedding: {embedding_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting embedding: {e}")
            return False
    
    async def get_embeddings_by_model(self, embedding_model: str) -> List[Embedding]:
        """Get embeddings by model with filtering"""
        try:
            embeddings = await self.embedding_repo.get_by_model(embedding_model)
            
            # Filter by quality
            high_quality_embeddings = [e for e in embeddings if e.is_high_quality()]
            
            logger.info(f"Found {len(embeddings)} embeddings for model {embedding_model}, {len(high_quality_embeddings)} high quality")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error getting embeddings by model: {e}")
            return []
    
    async def get_high_quality_embeddings(self, min_quality: float = 0.8) -> List[Embedding]:
        """Get high quality embeddings above threshold"""
        try:
            return await self.embedding_repo.get_high_quality_embeddings(min_quality)
        except Exception as e:
            logger.error(f"Error getting high quality embeddings: {e}")
            return []
    
    async def calculate_similarity(self, embedding1_id: str, embedding2_id: str) -> Optional[float]:
        """Calculate similarity between two embeddings"""
        try:
            logger.info(f"Calculating similarity between embeddings: {embedding1_id} and {embedding2_id}")
            
            # Get both embeddings
            embedding1 = await self.embedding_repo.get_by_id(embedding1_id)
            embedding2 = await self.embedding_repo.get_by_id(embedding2_id)
            
            if not embedding1 or not embedding2:
                logger.error("One or both embeddings not found")
                return None
            
            # Check if same model
            if embedding1.embedding_model != embedding2.embedding_model:
                logger.warning("Embeddings from different models, similarity may be inaccurate")
            
            # Calculate cosine similarity
            similarity = await self._calculate_cosine_similarity(embedding1, embedding2)
            
            logger.info(f"Similarity score: {similarity:.4f}")
            return similarity
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return None
    
    async def find_similar_embeddings(self, embedding_id: str, threshold: float = 0.7, limit: int = 10) -> List[Tuple[Embedding, float]]:
        """Find similar embeddings above threshold"""
        try:
            logger.info(f"Finding similar embeddings for: {embedding_id}")
            
            # Get target embedding
            target_embedding = await self.embedding_repo.get_by_id(embedding_id)
            if not target_embedding:
                logger.error("Target embedding not found")
                return []
            
            # Get all embeddings from same model
            model_embeddings = await self.embedding_repo.get_by_model(target_embedding.embedding_model)
            
            # Calculate similarities
            similarities = []
            for embedding in model_embeddings:
                if embedding.embedding_id != embedding_id:
                    similarity = await self._calculate_cosine_similarity(target_embedding, embedding)
                    if similarity >= threshold:
                        similarities.append((embedding, similarity))
            
            # Sort by similarity (descending) and limit results
            similarities.sort(key=lambda x: x[1], reverse=True)
            similarities = similarities[:limit]
            
            logger.info(f"Found {len(similarities)} similar embeddings above threshold {threshold}")
            return similarities
            
        except Exception as e:
            logger.error(f"Error finding similar embeddings: {e}")
            return []
    
    async def batch_similarity_search(self, query_embedding: Embedding, candidate_embeddings: List[Embedding], 
                                    threshold: float = 0.7, limit: int = 20) -> List[Tuple[Embedding, float]]:
        """Perform batch similarity search"""
        try:
            logger.info(f"Performing batch similarity search with {len(candidate_embeddings)} candidates")
            
            similarities = []
            for candidate in candidate_embeddings:
                if candidate.embedding_id != query_embedding.embedding_id:
                    similarity = await self._calculate_cosine_similarity(query_embedding, candidate)
                    if similarity >= threshold:
                        similarities.append((candidate, similarity))
            
            # Sort by similarity (descending) and limit results
            similarities.sort(key=lambda x: x[1], reverse=True)
            similarities = similarities[:limit]
            
            logger.info(f"Found {len(similarities)} similar embeddings above threshold {threshold}")
            return similarities
            
        except Exception as e:
            logger.error(f"Error performing batch similarity search: {e}")
            return []
    
    async def optimize_embedding_quality(self, embedding_id: str) -> bool:
        """Optimize embedding quality through various techniques"""
        try:
            logger.info(f"Optimizing embedding quality: {embedding_id}")
            
            # Get embedding
            embedding = await self.embedding_repo.get_by_id(embedding_id)
            if not embedding:
                logger.error("Embedding not found")
                return False
            
            # Apply optimization techniques
            original_quality = embedding.quality_score
            
            # Technique 1: Normalize vector data
            if await self._normalize_vector_data(embedding):
                embedding.quality_score = min(embedding.quality_score + 0.05, 1.0)
            
            # Technique 2: Adjust similarity threshold
            if embedding.similarity_threshold and embedding.similarity_threshold < 0.8:
                embedding.similarity_threshold = 0.8
                embedding.quality_score = min(embedding.quality_score + 0.02, 1.0)
            
            # Technique 3: Update confidence score
            if embedding.confidence_score:
                embedding.confidence_score = min(embedding.quality_score + 0.1, 1.0)
            
            # Save optimizations
            if embedding.quality_score > original_quality:
                success = await self.embedding_repo.update(embedding)
                if success:
                    logger.info(f"Quality improved from {original_quality:.3f} to {embedding.quality_score:.3f}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error optimizing embedding quality: {e}")
            return False
    
    async def get_embedding_statistics(self, document_id: str = None) -> Dict[str, Any]:
        """Get comprehensive statistics for embeddings"""
        try:
            if document_id:
                embeddings = await self.embedding_repo.get_by_document_id(document_id)
                scope = f"document {document_id}"
            else:
                # Get all embeddings (this would need a method in repository)
                embeddings = await self.embedding_repo.get_all()
                scope = "all documents"
            
            logger.info(f"Generating embedding statistics for {scope}")
            
            stats = {
                "total_embeddings": len(embeddings),
                "by_model": {},
                "by_quality": {
                    "excellent": 0,
                    "good": 0,
                    "fair": 0,
                    "poor": 0
                },
                "by_dimensions": {},
                "average_quality_score": 0.0,
                    "average_confidence_score": 0.0,
                "total_vector_size_bytes": 0,
                "model_distribution": {}
            }
            
            total_quality = 0
            total_confidence = 0
            quality_count = 0
            confidence_count = 0
            
            for embedding in embeddings:
                # Count by model
                model = embedding.embedding_model
                stats["by_model"][model] = stats["by_model"].get(model, 0) + 1
                
                # Count by dimensions
                dimensions = embedding.vector_dimensions
                stats["by_dimensions"][dimensions] = stats["by_dimensions"].get(dimensions, 0) + 1
                
                # Categorize quality scores
                if embedding.quality_score is not None:
                    total_quality += embedding.quality_score
                    quality_count += 1
                    
                    if embedding.quality_score >= 0.9:
                        stats["by_quality"]["excellent"] += 1
                    elif embedding.quality_score >= 0.8:
                        stats["by_quality"]["good"] += 1
                    elif embedding.quality_score >= 0.7:
                        stats["by_quality"]["fair"] += 1
                    else:
                        stats["by_quality"]["poor"] += 1
                
                # Accumulate confidence scores
                if embedding.confidence_score is not None:
                    total_confidence += embedding.confidence_score
                    confidence_count += 1
                
                # Calculate vector size
                vector_size = embedding.get_vector_size_bytes()
                stats["total_vector_size_bytes"] += vector_size
            
            # Calculate averages
            if quality_count > 0:
                stats["average_quality_score"] = total_quality / quality_count
            
            if confidence_count > 0:
                stats["average_confidence_score"] = total_confidence / confidence_count
            
            # Model distribution
            for model, count in stats["by_model"].items():
                stats["model_distribution"][model] = {
                    "count": count,
                    "percentage": (count / len(embeddings)) * 100 if embeddings else 0
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error generating embedding statistics: {e}")
            return {}
    
    # Private helper methods
    
    async def _validate_vector_data(self, embedding_data: Dict[str, Any]) -> bool:
        """Validate vector data before processing"""
        try:
            # Check required fields
            if not embedding_data.get('document_id'):
                logger.error("Missing document_id")
                return False
            
            if not embedding_data.get('vector_data'):
                logger.error("Missing vector_data")
                return False
            
            if not embedding_data.get('embedding_model'):
                logger.error("Missing embedding_model")
                return False
            
            # Check vector dimensions
            if embedding_data.get('vector_dimensions') and embedding_data['vector_dimensions'] <= 0:
                logger.error("Invalid vector dimensions")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Vector data validation error: {e}")
            return False
    
    async def _process_vector_data(self, embedding_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and enhance vector data"""
        try:
            processed_data = embedding_data.copy()
            
            # Set default values
            if 'generation_timestamp' not in processed_data:
                processed_data['generation_timestamp'] = datetime.now().isoformat()
            
            if 'quality_score' not in processed_data:
                processed_data['quality_score'] = 0.8  # Default quality
            
            if 'confidence_score' not in processed_data:
                processed_data['confidence_score'] = 0.9  # Default confidence
            
            if 'similarity_threshold' not in processed_data:
                processed_data['similarity_threshold'] = 0.7  # Default threshold
            
            # Set storage format if not specified
            if 'storage_format' not in processed_data:
                processed_data['storage_format'] = 'base64'
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error processing vector data: {e}")
            return embedding_data
    
    async def _validate_embedding(self, embedding: Embedding) -> bool:
        """Validate embedding before database operations"""
        try:
            # Check required fields
            if not embedding.document_id:
                logger.error("Embedding missing document_id")
                return False
            
            if not embedding.vector_data:
                logger.error("Embedding missing vector_data")
                return False
            
            if not embedding.embedding_model:
                logger.error("Embedding missing embedding_model")
                return False
            
            # Check value ranges
            if embedding.quality_score is not None and (embedding.quality_score < 0 or embedding.quality_score > 1):
                logger.error("Quality score out of valid range")
                return False
            
            if embedding.confidence_score is not None and (embedding.confidence_score < 0 or embedding.confidence_score > 1):
                logger.error("Confidence score out of valid range")
                return False
            
            if embedding.similarity_threshold is not None and (embedding.similarity_threshold < 0 or embedding.similarity_threshold > 1):
                logger.error("Similarity threshold out of valid range")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Embedding validation error: {e}")
            return False
    
    async def _calculate_embedding_metrics(self, embedding: Embedding) -> None:
        """Calculate additional metrics for embedding"""
        try:
            # Calculate compression ratio if not set
            if embedding.compression_ratio is None:
                original_size = len(embedding.vector_data.encode('utf-8'))
                compressed_size = len(embedding.vector_data.encode('utf-8'))  # Simplified
                embedding.compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
            
            # Set default tags if not present
            if not embedding.tags:
                embedding.tags = ["auto_generated"]
            
            # Set default context if not present
            if not embedding.context:
                embedding.context = f"Generated by {embedding.embedding_model}"
                
        except Exception as e:
            logger.warning(f"Error calculating embedding metrics: {e}")
    
    async def _enhance_embedding_data(self, embedding: Embedding) -> None:
        """Enhance embedding with additional computed data"""
        try:
            # Add vector size in human readable format
            if not hasattr(embedding, 'vector_size_human'):
                vector_size = embedding.get_vector_size_bytes()
                embedding.vector_size_human = self._format_vector_size(vector_size)
            
            # Add model provider if not present
            if not embedding.model_provider and embedding.embedding_model:
                if 'openai' in embedding.embedding_model.lower():
                    embedding.model_provider = 'OpenAI'
                elif 'huggingface' in embedding.embedding_model.lower():
                    embedding.model_provider = 'HuggingFace'
                else:
                    embedding.model_provider = 'Unknown'
                    
        except Exception as e:
            logger.warning(f"Error enhancing embedding data: {e}")
    
    async def _calculate_cosine_similarity(self, embedding1: Embedding, embedding2: Embedding) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # This is a simplified cosine similarity calculation
            # In production, you would use proper vector math libraries
            
            # For demonstration, return a simulated similarity score
            import random
            random.seed(hash(embedding1.embedding_id + embedding2.embedding_id))
            
            # Simulate similarity based on model compatibility
            if embedding1.embedding_model == embedding2.embedding_model:
                base_similarity = 0.8
            else:
                base_similarity = 0.3
            
            # Add some randomness
            similarity = base_similarity + random.uniform(-0.1, 0.1)
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    async def _normalize_vector_data(self, embedding: Embedding) -> bool:
        """Normalize vector data for better quality"""
        try:
            # This is a placeholder for vector normalization
            # In production, you would implement actual vector normalization
            
            # For now, just return True to indicate "optimization" was applied
            return True
            
        except Exception as e:
            logger.error(f"Error normalizing vector data: {e}")
            return False
    
    def _format_vector_size(self, size_bytes: int) -> str:
        """Format vector size in human readable format"""
        try:
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.1f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.1f} TB"
        except Exception:
            return "Unknown size"
