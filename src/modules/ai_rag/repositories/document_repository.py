"""
Document Repository
==================

Data access layer for document operations.
Pure async implementation following AASX and Twin Registry convention.
"""

import logging
from typing import Optional, List, Dict, Any
from src.engine.database.connection_manager import ConnectionManager
from src.modules.ai_rag.models.document import Document

logger = logging.getLogger(__name__)


class DocumentRepository:
    """
    Document Repository - Pure Async Implementation
    
    Handles all database operations for documents.
    Follows the same convention as AASX and Twin Registry modules.
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize repository with connection manager"""
        self.connection_manager = connection_manager
        self.table_name = "documents"
    
    async def create(self, document: Document) -> bool:
        """Create a new document"""
        try:
            async with self.connection_manager.get_session() as session:
                document_data = document.to_dict()
                
                query = f"""
                INSERT INTO {self.table_name} (
                    document_id, registry_id, file_path, file_type, file_size,
                    content_hash, processing_status, processing_start_time,
                    processing_end_time, processing_duration_ms, content_summary,
                    extracted_text, metadata, quality_score, confidence_score,
                    validation_errors, processor_config, extraction_config,
                    created_at, updated_at
                ) VALUES (
                    :document_id, :registry_id, :file_path, :file_type, :file_size,
                    :content_hash, :processing_status, :processing_start_time,
                    :processing_end_time, :processing_duration_ms, :content_summary,
                    :extracted_text, :metadata, :quality_score, :confidence_score,
                    :validation_errors, :processor_config, :extraction_config,
                    :created_at, :updated_at
                )
                """
                
                await session.execute(query, document_data)
                await session.commit()
                
                logger.info(f"Created document: {document.document_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            return False
    
    async def get_by_id(self, document_id: str) -> Optional[Document]:
        """Get document by ID"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"SELECT * FROM {self.table_name} WHERE document_id = :document_id"
                result = await session.execute(query, {"document_id": document_id})
                row = result.fetchone()
                
                if row:
                    return Document.from_dict(dict(row))
                return None
                
        except Exception as e:
            logger.error(f"Error getting document by ID: {e}")
            return None
    
    async def get_by_registry_id(self, registry_id: str) -> List[Document]:
        """Get documents by registry ID"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"SELECT * FROM {self.table_name} WHERE registry_id = :registry_id"
                result = await session.execute(query, {"registry_id": registry_id})
                rows = result.fetchall()
                
                return [Document.from_dict(dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting documents by registry ID: {e}")
            return []
    
    async def get_by_status(self, status: str) -> List[Document]:
        """Get documents by processing status"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"SELECT * FROM {self.table_name} WHERE processing_status = :status"
                result = await session.execute(query, {"status": status})
                rows = result.fetchall()
                
                return [Document.from_dict(dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting documents by status: {e}")
            return []
    
    async def update(self, document: Document) -> bool:
        """Update existing document"""
        try:
            async with self.connection_manager.get_session() as session:
                document.update_timestamp()
                document_data = document.to_dict()
                
                query = f"""
                UPDATE {self.table_name} SET
                    processing_status = :processing_status, processing_start_time = :processing_start_time,
                    processing_end_time = :processing_end_time, processing_duration_ms = :processing_duration_ms,
                    content_summary = :content_summary, extracted_text = :extracted_text,
                    metadata = :metadata, quality_score = :quality_score, confidence_score = :confidence_score,
                    validation_errors = :validation_errors, updated_at = :updated_at
                WHERE document_id = :document_id
                """
                
                await session.execute(query, document_data)
                await session.commit()
                
                logger.info(f"Updated document: {document.document_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            return False
    
    async def delete(self, document_id: str) -> bool:
        """Delete document"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"DELETE FROM {self.table_name} WHERE document_id = :document_id"
                await session.execute(query, {"document_id": document_id})
                await session.commit()
                
                logger.info(f"Deleted document: {document_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False
    
    async def get_by_file_type(self, file_type: str) -> List[Document]:
        """Get documents by file type"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"SELECT * FROM {self.table_name} WHERE file_type = :file_type"
                result = await session.execute(query, {"file_type": file_type})
                rows = result.fetchall()
                
                return [Document.from_dict(dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting documents by file type: {e}")
            return []
    
    async def count_by_registry_id(self, registry_id: str) -> int:
        """Count documents for a registry"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE registry_id = :registry_id"
                result = await session.execute(query, {"registry_id": registry_id})
                row = result.fetchone()
                
                return row['count'] if row else 0
                
        except Exception as e:
            logger.error(f"Error counting documents: {e}")
            return 0
