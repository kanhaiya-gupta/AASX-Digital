"""
Embedding Repository
===================

Data access layer for embedding operations.
Pure async implementation following AASX and Twin Registry convention.
"""

import logging
from typing import Optional, List, Dict, Any
from src.engine.database.connection_manager import ConnectionManager
from src.modules.ai_rag.models.embedding import Embedding

logger = logging.getLogger(__name__)


class EmbeddingRepository:
    """
    Embedding Repository - Pure Async Implementation
    
    Handles all database operations for embeddings.
    Follows the same convention as AASX and Twin Registry modules.
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize repository with connection manager"""
        self.connection_manager = connection_manager
        self.table_name = "embeddings"
    
    async def create(self, embedding: Embedding) -> bool:
        """Create a new embedding"""
        try:
            async with self.connection_manager.get_session() as session:
                embedding_data = embedding.to_dict()
                
                query = f"""
                INSERT INTO {self.table_name} (
                    embedding_id, document_id, vector_data, vector_dimensions,
                    vector_type, embedding_model, model_provider, model_parameters,
                    generation_timestamp, generation_duration_ms, generation_cost,
                    quality_score, similarity_threshold, confidence_score,
                    metadata, context, tags, storage_location, storage_format,
                    compression_ratio, created_at, updated_at
                ) VALUES (
                    :embedding_id, :document_id, :vector_data, :vector_dimensions,
                    :vector_type, :embedding_model, :model_provider, :model_parameters,
                    :generation_timestamp, :generation_duration_ms, :generation_cost,
                    :quality_score, :similarity_threshold, :confidence_score,
                    :metadata, :context, :tags, :storage_location, :storage_format,
                    :compression_ratio, :created_at, :updated_at
                )
                """
                
                await session.execute(query, embedding_data)
                await session.commit()
                
                logger.info(f"Created embedding: {embedding.embedding_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            return False
    
    async def get_by_id(self, embedding_id: str) -> Optional[Embedding]:
        """Get embedding by ID"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"SELECT * FROM {self.table_name} WHERE embedding_id = :embedding_id"
                result = await session.execute(query, {"embedding_id": embedding_id})
                row = result.fetchone()
                
                if row:
                    return Embedding.from_dict(dict(row))
                return None
                
        except Exception as e:
            logger.error(f"Error getting embedding by ID: {e}")
            return None
    
    async def get_by_document_id(self, document_id: str) -> List[Embedding]:
        """Get embeddings by document ID"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"SELECT * FROM {self.table_name} WHERE document_id = :document_id"
                result = await session.execute(query, {"document_id": document_id})
                rows = result.fetchall()
                
                return [Embedding.from_dict(dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting embeddings by document ID: {e}")
            return []
    
    async def get_by_model(self, embedding_model: str) -> List[Embedding]:
        """Get embeddings by model"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"SELECT * FROM {self.table_name} WHERE embedding_model = :embedding_model"
                result = await session.execute(query, {"embedding_model": embedding_model})
                rows = result.fetchall()
                
                return [Embedding.from_dict(dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting embeddings by model: {e}")
            return []
    
    async def update(self, embedding: Embedding) -> bool:
        """Update existing embedding"""
        try:
            async with self.connection_manager.get_session() as session:
                embedding.update_timestamp()
                embedding_data = embedding.to_dict()
                
                query = f"""
                UPDATE {self.table_name} SET
                    quality_score = :quality_score, similarity_threshold = :similarity_threshold,
                    confidence_score = :confidence_score, metadata = :metadata,
                    context = :context, tags = :tags, updated_at = :updated_at
                WHERE embedding_id = :embedding_id
                """
                
                await session.execute(query, embedding_data)
                await session.commit()
                
                logger.info(f"Updated embedding: {embedding.embedding_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating embedding: {e}")
            return False
    
    async def delete(self, embedding_id: str) -> bool:
        """Delete embedding"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"DELETE FROM {self.table_name} WHERE embedding_id = :embedding_id"
                await session.execute(query, {"embedding_id": embedding_id})
                await session.commit()
                
                logger.info(f"Deleted embedding: {embedding_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting embedding: {e}")
            return False
    
    async def get_high_quality_embeddings(self, min_quality: float = 0.8) -> List[Embedding]:
        """Get high quality embeddings"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"SELECT * FROM {self.table_name} WHERE quality_score >= :min_quality"
                result = await session.execute(query, {"min_quality": min_quality})
                rows = result.fetchall()
                
                return [Embedding.from_dict(dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting high quality embeddings: {e}")
            return []
    
    async def count_by_document_id(self, document_id: str) -> int:
        """Count embeddings for a document"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE document_id = :document_id"
                result = await session.execute(query, {"document_id": document_id})
                row = result.fetchone()
                
                return row['count'] if row else 0
                
        except Exception as e:
            logger.error(f"Error counting embeddings: {e}")
            return 0
