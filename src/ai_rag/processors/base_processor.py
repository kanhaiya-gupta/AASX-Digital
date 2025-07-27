"""
Base processor for data processing in vector embedding pipeline.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List
from src.shared.utils import setup_logging


class BaseDataProcessor(ABC):
    """Abstract base class for data processors."""
    
    def __init__(self, text_embedding_manager=None, vector_db=None):
        """
        Initialize base processor.
        
        Args:
            text_embedding_manager: Text embedding manager instance
            vector_db: Vector database client instance
        """
        self.text_embedding_manager = text_embedding_manager
        self.vector_db = vector_db
        self.logger = setup_logging(f"{self.__class__.__name__.lower()}")
    
    @abstractmethod
    def process(self, project_id: str, file_info: Dict[str, Any], file_path: Path) -> Dict[str, Any]:
        """
        Process a file and create vector embeddings.
        
        Args:
            project_id: Project identifier
            file_info: File information from project manager
            file_path: Path to the file to process
            
        Returns:
            Dictionary containing processing results
        """
        pass
    
    @abstractmethod
    def can_process(self, file_path: Path) -> bool:
        """
        Check if this processor can handle the given file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if this processor can handle the file
        """
        pass
    
    def _generate_embedding(self, text_content: str, file_path: Path) -> Optional[List[float]]:
        """Generate embedding for text content."""
        try:
            if not self.text_embedding_manager:
                self.logger.error("Text embedding manager not available")
                return None
            
            # Check if text is too long and needs chunking
            model = self.text_embedding_manager.get_model()
            if not model.validate_text(text_content):
                self.logger.info(f"Text too long for direct embedding, using chunking: {len(text_content)} characters")
                
                # Use chunking for long texts
                chunks = model.embed_text_with_chunking(text_content, chunk_size=3000, overlap=200)
                if chunks:
                    # Use the first chunk's embedding as the primary embedding
                    # In a more sophisticated approach, you might want to combine multiple chunks
                    return chunks[0]['embedding']
                else:
                    self.logger.error("Failed to generate embeddings from chunks")
                    return None
            
            # Generate embedding for text within limits
            embedding = self.text_embedding_manager.get_model().embed_text(text_content)
            if embedding:
                self.logger.info(f"Generated embedding for {file_path.name}: {len(embedding)} dimensions")
                return embedding
            else:
                self.logger.error(f"Failed to generate embedding for {file_path.name}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating embedding for {file_path.name}: {e}")
            return None
    
    def _upload_to_vector_db(self, embedding: List[float], metadata: Dict[str, Any], file_path: Path) -> bool:
        """Upload vector to database."""
        if not self.vector_db:
            self.logger.error("Vector database not available")
            return False
        
        try:
            # Get project_id from metadata
            project_id = metadata.get('project_id', 'unknown')
            
            vector_data = {
                'id': self.vector_db.generate_vector_id(project_id, file_path.name),
                'vector': embedding,
                'payload': metadata
            }
            
            success = self.vector_db.upsert_vectors([vector_data])
            
            if success:
                self.logger.info(f"Successfully uploaded vector for {file_path}")
            else:
                self.logger.error(f"Failed to upload vector for {file_path}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error uploading vector for {file_path}: {e}")
            return False
    
    def _save_embedding_locally(self, project_id: str, file_path: Path, vector_data: Dict[str, Any]):
        """Save embedding data locally for backup and reference."""
        try:
            # Create embeddings directory in the project output directory
            # Use absolute path to avoid recursive directory creation
            output_dir = Path("output/projects") / project_id
            embeddings_dir = output_dir / "embeddings"
            embeddings_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a safe filename for the embedding
            safe_filename = file_path.stem.replace(" ", "_").replace(".", "_")
            embedding_file = embeddings_dir / f"{safe_filename}_embedding.json"
            
            # Save embedding data
            import json
            with open(embedding_file, 'w', encoding='utf-8') as f:
                json.dump(vector_data, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Saved embedding locally: {embedding_file}")
                
        except Exception as e:
            self.logger.error(f"Failed to save embedding locally: {e}")
    
    def _create_success_result(self, file_info: Dict[str, Any], file_path: Path, 
                              vector_id: str, embeddings_created: int = 1) -> Dict[str, Any]:
        """Create success result dictionary."""
        return {
            'file_id': file_info.get('file_id'),
            'filename': file_path.name,
            'status': 'success',
            'embeddings_created': embeddings_created,
            'vector_id': vector_id
        }
    
    def _create_error_result(self, file_info: Dict[str, Any], file_path: Path, 
                           error: str) -> Dict[str, Any]:
        """Create error result dictionary."""
        return {
            'file_id': file_info.get('file_id'),
            'filename': file_path.name,
            'status': 'error',
            'error': error
        }
    
    def _create_skipped_result(self, file_info: Dict[str, Any], file_path: Path, 
                             reason: str) -> Dict[str, Any]:
        """Create skipped result dictionary."""
        return {
            'file_id': file_info.get('file_id'),
            'filename': file_path.name,
            'status': 'skipped',
            'reason': reason
        } 