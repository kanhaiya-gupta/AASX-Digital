"""
Document Service
===============

Business logic layer for document operations.
Handles document processing, validation, and quality assessment.
Pure async implementation following AASX and Twin Registry convention.
"""

import logging
import hashlib
import os
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.modules.ai_rag.models.document import Document
from src.modules.ai_rag.repositories.document_repository import DocumentRepository
from src.modules.ai_rag.repositories.ai_rag_registry_repository import AIRagRegistryRepository

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Document Service - Pure Async Implementation
    
    Orchestrates document operations including:
    - Document processing and validation
    - Quality assessment and scoring
    - Content extraction and analysis
    - File type handling and conversion
    """
    
    def __init__(self, document_repo: DocumentRepository,
                 registry_repo: AIRagRegistryRepository):
        """Initialize service with required repositories"""
        self.document_repo = document_repo
        self.registry_repo = registry_repo
    
    async def create_document(self, document_data: Dict[str, Any]) -> Optional[Document]:
        """Create a new document with validation and processing"""
        try:
            logger.info(f"Creating document: {document_data.get('file_path', 'Unknown')}")
            
            # Validate file exists
            file_path = document_data.get('file_path')
            if file_path and not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None
            
            # Calculate file hash if not provided
            if file_path and not document_data.get('content_hash'):
                content_hash = await self._calculate_file_hash(file_path)
                document_data['content_hash'] = content_hash
            
            # Set file size if not provided
            if file_path and not document_data.get('file_size'):
                file_size = os.path.getsize(file_path)
                document_data['file_size'] = file_size
            
            # Create document instance
            document = Document(**document_data)
            
            # Validate document before creation
            if not await self._validate_document(document):
                logger.error("Document validation failed")
                return None
            
            # Process document content
            await self._process_document_content(document)
            
            # Create in database
            success = await self.document_repo.create(document)
            if not success:
                logger.error("Failed to create document in database")
                return None
            
            logger.info(f"Successfully created document: {document.document_id}")
            return document
            
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            return None
    
    async def get_document_by_id(self, document_id: str) -> Optional[Document]:
        """Get document by ID with enhanced data"""
        try:
            document = await self.document_repo.get_by_id(document_id)
            if document:
                # Enhance with additional data
                await self._enhance_document_data(document)
            
            return document
            
        except Exception as e:
            logger.error(f"Error getting document by ID: {e}")
            return None
    
    async def get_documents_by_registry(self, registry_id: str) -> List[Document]:
        """Get documents by registry ID with processing status"""
        try:
            documents = await self.document_repo.get_by_registry_id(registry_id)
            
            # Enhance each document
            for document in documents:
                await self._enhance_document_data(document)
            
            return documents
            
        except Exception as e:
            logger.error(f"Error getting documents by registry: {e}")
            return []
    
    async def update_document(self, document_id: str, update_data: Dict[str, Any]) -> bool:
        """Update existing document with validation"""
        try:
            logger.info(f"Updating document: {document_id}")
            
            # Get existing document
            document = await self.document_repo.get_by_id(document_id)
            if not document:
                logger.error(f"Document not found: {document_id}")
                return False
            
            # Update fields
            for key, value in update_data.items():
                if hasattr(document, key):
                    setattr(document, key, value)
            
            # Validate updated document
            if not await self._validate_document(document):
                logger.error("Updated document validation failed")
                return False
            
            # Update timestamp
            document.update_timestamp()
            
            # Save to database
            success = await self.document_repo.update(document)
            if success:
                logger.info(f"Successfully updated document: {document_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            return False
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete document with cleanup"""
        try:
            logger.info(f"Deleting document: {document_id}")
            
            # Get document to find file path before deletion
            document = await self.document_repo.get_by_id(document_id)
            if not document:
                logger.error(f"Document not found: {document_id}")
                return False
            
            # Check if file should be deleted
            file_path = document.file_path
            if file_path and os.path.exists(file_path):
                # For now, just log - in production you might want to delete the file
                logger.info(f"File exists at: {file_path} (not deleted)")
            
            # Delete from database
            success = await self.document_repo.delete(document_id)
            if success:
                logger.info(f"Successfully deleted document: {document_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False
    
    async def process_document(self, document_id: str) -> bool:
        """Process document content and update status"""
        try:
            logger.info(f"Processing document: {document_id}")
            
            # Get document
            document = await self.document_repo.get_by_id(document_id)
            if not document:
                logger.error(f"Document not found: {document_id}")
                return False
            
            # Check if document needs processing
            if document.processing_status == "completed":
                logger.info(f"Document already processed: {document_id}")
                return True
            
            # Start processing
            await self._start_processing(document)
            
            # Process content based on file type
            success = await self._extract_content(document)
            if not success:
                await self._mark_processing_failed(document, "Content extraction failed")
                return False
            
            # Calculate quality scores
            await self._calculate_quality_scores(document)
            
            # Mark as completed
            await self._mark_processing_completed(document)
            
            logger.info(f"Successfully processed document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            await self._mark_processing_failed(document, str(e))
            return False
    
    async def get_documents_by_status(self, status: str) -> List[Document]:
        """Get documents by processing status"""
        try:
            return await self.document_repo.get_by_status(status)
        except Exception as e:
            logger.error(f"Error getting documents by status: {e}")
            return []
    
    async def get_documents_by_file_type(self, file_type: str) -> List[Document]:
        """Get documents by file type"""
        try:
            return await self.document_repo.get_by_file_type(file_type)
        except Exception as e:
            logger.error(f"Error getting documents by file type: {e}")
            return []
    
    async def reprocess_document(self, document_id: str) -> bool:
        """Reprocess a document from scratch"""
        try:
            logger.info(f"Reprocessing document: {document_id}")
            
            # Reset processing status
            reset_data = {
                "processing_status": "pending",
                "processing_start_time": None,
                "processing_end_time": None,
                "processing_duration_ms": None,
                "content_summary": None,
                "extracted_text": None,
                "quality_score": None,
                "confidence_score": None,
                "validation_errors": None
            }
            
            success = await self.update_document(document_id, reset_data)
            if not success:
                return False
            
            # Process document
            return await self.process_document(document_id)
            
        except Exception as e:
            logger.error(f"Error reprocessing document: {e}")
            return False
    
    async def validate_document_quality(self, document_id: str) -> Dict[str, Any]:
        """Validate document quality and return detailed assessment"""
        try:
            logger.info(f"Validating document quality: {document_id}")
            
            document = await self.document_repo.get_by_id(document_id)
            if not document:
                return {"error": "Document not found"}
            
            # Perform quality validation
            validation_result = await self._perform_quality_validation(document)
            
            # Update document with validation results
            if validation_result.get("is_valid"):
                update_data = {
                    "quality_score": validation_result.get("quality_score"),
                    "confidence_score": validation_result.get("confidence_score"),
                    "validation_errors": validation_result.get("errors")
                }
                await self.update_document(document_id, update_data)
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating document quality: {e}")
            return {"error": str(e)}
    
    async def get_document_statistics(self, registry_id: str) -> Dict[str, Any]:
        """Get comprehensive statistics for documents in a registry"""
        try:
            documents = await self.document_repo.get_by_registry_id(registry_id)
            
            stats = {
                "total_documents": len(documents),
                "by_status": {},
                "by_file_type": {},
                "by_quality": {
                    "excellent": 0,
                    "good": 0,
                    "fair": 0,
                    "poor": 0
                },
                "total_size_bytes": 0,
                "average_quality_score": 0.0,
                "average_confidence_score": 0.0
            }
            
            total_quality = 0
            total_confidence = 0
            quality_count = 0
            confidence_count = 0
            
            for document in documents:
                # Count by status
                status = document.processing_status
                stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
                
                # Count by file type
                file_type = document.file_type
                stats["by_file_type"][file_type] = stats["by_file_type"].get(file_type, 0) + 1
                
                # Accumulate size
                if document.file_size:
                    stats["total_size_bytes"] += document.file_size
                
                # Categorize quality scores
                if document.quality_score is not None:
                    total_quality += document.quality_score
                    quality_count += 1
                    
                    if document.quality_score >= 0.9:
                        stats["by_quality"]["excellent"] += 1
                    elif document.quality_score >= 0.8:
                        stats["by_quality"]["good"] += 1
                    elif document.quality_score >= 0.7:
                        stats["by_quality"]["fair"] += 1
                    else:
                        stats["by_quality"]["poor"] += 1
                
                # Accumulate confidence scores
                if document.confidence_score is not None:
                    total_confidence += document.confidence_score
                    confidence_count += 1
            
            # Calculate averages
            if quality_count > 0:
                stats["average_quality_score"] = total_quality / quality_count
            
            if confidence_count > 0:
                stats["average_confidence_score"] = total_confidence / confidence_count
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting document statistics: {e}")
            return {}
    
    # Private helper methods
    
    async def _validate_document(self, document: Document) -> bool:
        """Validate document before database operations"""
        try:
            # Check required fields
            if not document.registry_id:
                logger.error("Document missing registry_id")
                return False
            
            if not document.file_path:
                logger.error("Document missing file_path")
                return False
            
            # Check file type
            if document.file_type and document.file_type not in ["pdf", "docx", "txt", "html", "xml", "json", "csv"]:
                logger.error(f"Unsupported file type: {document.file_type}")
                return False
            
            # Check processing status
            if document.processing_status and document.processing_status not in ["pending", "processing", "completed", "failed"]:
                logger.error(f"Invalid processing status: {document.processing_status}")
                return False
            
            # Check quality score range
            if document.quality_score is not None and (document.quality_score < 0 or document.quality_score > 1):
                logger.error("Quality score out of valid range")
                return False
            
            # Check confidence score range
            if document.confidence_score is not None and (document.confidence_score < 0 or document.confidence_score > 1):
                logger.error("Confidence score out of valid range")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Document validation error: {e}")
            return False
    
    async def _enhance_document_data(self, document: Document) -> None:
        """Enhance document with additional computed data"""
        try:
            # Add file name if not present
            if document.file_path and not hasattr(document, 'file_name'):
                document.file_name = os.path.basename(document.file_path)
            
            # Add file extension if not present
            if document.file_path and not hasattr(document, 'file_extension'):
                document.file_extension = os.path.splitext(document.file_path)[1]
            
            # Add file size in human readable format
            if document.file_size and not hasattr(document, 'file_size_human'):
                document.file_size_human = self._format_file_size(document.file_size)
                
        except Exception as e:
            logger.warning(f"Error enhancing document data: {e}")
    
    async def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file content"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating file hash: {e}")
            return ""
    
    async def _process_document_content(self, document: Document) -> None:
        """Process document content based on file type"""
        try:
            # Set default processing status
            if not document.processing_status:
                document.processing_status = "pending"
            
            # Set default quality and confidence scores
            if document.quality_score is None:
                document.quality_score = 0.8  # Default quality
            
            if document.confidence_score is None:
                document.confidence_score = 0.9  # Default confidence
                
        except Exception as e:
            logger.warning(f"Error processing document content: {e}")
    
    async def _start_processing(self, document: Document) -> None:
        """Mark document as processing started"""
        try:
            document.processing_status = "processing"
            document.processing_start_time = datetime.now().isoformat()
            await self.document_repo.update(document)
        except Exception as e:
            logger.error(f"Error starting processing: {e}")
    
    async def _extract_content(self, document: Document) -> bool:
        """Extract content from document based on file type"""
        try:
            # Simulate content extraction
            if document.file_type == "pdf":
                document.content_summary = "PDF content extracted successfully"
                document.extracted_text = "This is extracted text from the PDF document..."
            elif document.file_type == "docx":
                document.content_summary = "Word document content extracted successfully"
                document.extracted_text = "This is extracted text from the Word document..."
            elif document.file_type == "txt":
                document.content_summary = "Text file content extracted successfully"
                document.extracted_text = "This is extracted text from the text file..."
            else:
                document.content_summary = "Content extracted successfully"
                document.extracted_text = "This is extracted content from the document..."
            
            return True
            
        except Exception as e:
            logger.error(f"Error extracting content: {e}")
            return False
    
    async def _calculate_quality_scores(self, document: Document) -> None:
        """Calculate quality and confidence scores for document"""
        try:
            # Simple scoring based on content length and file type
            base_score = 0.8
            
            # Adjust based on file type
            if document.file_type in ["pdf", "docx"]:
                base_score += 0.1
            elif document.file_type == "txt":
                base_score += 0.05
            
            # Adjust based on content length
            if document.extracted_text:
                text_length = len(document.extracted_text)
                if text_length > 1000:
                    base_score += 0.1
                elif text_length > 500:
                    base_score += 0.05
            
            # Ensure score is within bounds
            document.quality_score = min(max(base_score, 0.0), 1.0)
            document.confidence_score = min(document.quality_score + 0.1, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating quality scores: {e}")
    
    async def _mark_processing_completed(self, document: Document) -> None:
        """Mark document as processing completed"""
        try:
            document.processing_status = "completed"
            document.processing_end_time = datetime.now().isoformat()
            
            # Calculate processing duration
            if document.processing_start_time:
                start_time = datetime.fromisoformat(document.processing_start_time.replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(document.processing_end_time.replace('Z', '+00:00'))
                duration_ms = (end_time - start_time).total_seconds() * 1000
                document.processing_duration_ms = int(duration_ms)
            
            await self.document_repo.update(document)
        except Exception as e:
            logger.error(f"Error marking processing completed: {e}")
    
    async def _mark_processing_failed(self, document: Document, error_message: str) -> None:
        """Mark document as processing failed"""
        try:
            document.processing_status = "failed"
            document.processing_end_time = datetime.now().isoformat()
            document.validation_errors = error_message
            await self.document_repo.update(document)
        except Exception as e:
            logger.error(f"Error marking processing failed: {e}")
    
    async def _perform_quality_validation(self, document: Document) -> Dict[str, Any]:
        """Perform comprehensive quality validation"""
        try:
            validation_result = {
                "is_valid": True,
                "quality_score": 0.0,
                "confidence_score": 0.0,
                "errors": [],
                "warnings": []
            }
            
            # Check if document has content
            if not document.extracted_text:
                validation_result["is_valid"] = False
                validation_result["errors"].append("No extracted text content")
            
            # Check content length
            if document.extracted_text and len(document.extracted_text) < 10:
                validation_result["warnings"].append("Extracted text is very short")
            
            # Check file size
            if document.file_size and document.file_size < 100:
                validation_result["warnings"].append("File size is very small")
            
            # Calculate quality score
            quality_score = 0.8  # Base score
            
            if document.extracted_text:
                quality_score += 0.1
            
            if document.content_summary:
                quality_score += 0.05
            
            if document.file_size and document.file_size > 1000:
                quality_score += 0.05
            
            validation_result["quality_score"] = min(quality_score, 1.0)
            validation_result["confidence_score"] = min(quality_score + 0.1, 1.0)
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error performing quality validation: {e}")
            return {
                "is_valid": False,
                "quality_score": 0.0,
                "confidence_score": 0.0,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": []
            }
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        try:
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.1f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.1f} TB"
        except Exception:
            return "Unknown size"
