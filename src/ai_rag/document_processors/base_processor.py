"""
Base document processor providing common interface for different document types.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import json
import hashlib

from src.shared.utils import setup_logging


class DocumentProcessor(ABC):
    """Abstract base class for document processors."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize document processor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.logger = setup_logging(self.__class__.__name__)
        self.supported_extensions = []
    
    @abstractmethod
    def can_process(self, file_path: Path) -> bool:
        """
        Check if this processor can handle the given file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file can be processed
        """
        pass
    
    @abstractmethod
    def process_file(self, file_path: Path, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a single file and extract content.
        
        Args:
            file_path: Path to the file to process
            metadata: Additional metadata for the file
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        pass
    
    @abstractmethod
    def extract_text(self, file_path: Path) -> str:
        """
        Extract text content from the file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text content
        """
        pass
    
    def get_file_hash(self, file_path: Path) -> str:
        """
        Generate a hash for the file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            SHA256 hash of the file
        """
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            return file_hash
        except Exception as e:
            self.logger.error(f"Failed to generate hash for {file_path}: {e}")
            return ""
    
    def get_file_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Get basic file metadata.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing file metadata
        """
        try:
            stat = file_path.stat()
            return {
                'filename': file_path.name,
                'file_path': str(file_path),
                'file_size': stat.st_size,
                'file_extension': file_path.suffix.lower(),
                'file_hash': self.get_file_hash(file_path),
                'modified_time': stat.st_mtime
            }
        except Exception as e:
            self.logger.error(f"Failed to get metadata for {file_path}: {e}")
            return {}
    
    def validate_file(self, file_path: Path) -> bool:
        """
        Validate that the file exists and is readable.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file is valid
        """
        if not file_path.exists():
            self.logger.error(f"File does not exist: {file_path}")
            return False
        
        if not file_path.is_file():
            self.logger.error(f"Path is not a file: {file_path}")
            return False
        
        if not file_path.stat().st_size > 0:
            self.logger.error(f"File is empty: {file_path}")
            return False
        
        return True
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        return self.supported_extensions.copy()
    
    def save_processing_result(self, result: Dict[str, Any], output_path: Path) -> bool:
        """
        Save processing result to a file.
        
        Args:
            result: Processing result dictionary
            output_path: Path to save the result
            
        Returns:
            True if saved successfully
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save processing result: {e}")
            return False
    
    def load_processing_result(self, output_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load processing result from a file.
        
        Args:
            output_path: Path to the result file
            
        Returns:
            Processing result dictionary or None if failed
        """
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load processing result: {e}")
            return None


class DocumentProcessorError(Exception):
    """Custom exception for document processing operations."""
    pass


class DocumentProcessorManager:
    """Manager for document processors."""
    
    def __init__(self):
        """Initialize document processor manager."""
        self.logger = setup_logging("document_processor_manager")
        self.processors = {}
    
    def register_processor(self, processor: DocumentProcessor):
        """
        Register a document processor.
        
        Args:
            processor: Document processor instance
        """
        processor_name = processor.__class__.__name__
        self.processors[processor_name] = processor
        self.logger.info(f"Registered processor: {processor_name}")
    
    def get_processor_for_file(self, file_path: Path) -> Optional[DocumentProcessor]:
        """
        Get the appropriate processor for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Document processor that can handle the file, or None
        """
        for processor in self.processors.values():
            if processor.can_process(file_path):
                return processor
        
        return None
    
    def process_file(self, file_path: Path, metadata: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Process a file using the appropriate processor.
        
        Args:
            file_path: Path to the file
            metadata: Additional metadata
            
        Returns:
            Processing result or None if no processor found
        """
        processor = self.get_processor_for_file(file_path)
        if not processor:
            self.logger.warning(f"No processor found for file: {file_path}")
            return None
        
        try:
            return processor.process_file(file_path, metadata)
        except Exception as e:
            self.logger.error(f"Failed to process file {file_path}: {e}")
            return None
    
    def get_supported_extensions(self) -> List[str]:
        """Get all supported file extensions."""
        extensions = set()
        for processor in self.processors.values():
            extensions.update(processor.get_supported_extensions())
        return list(extensions)
    
    def list_processors(self) -> List[str]:
        """Get list of registered processor names."""
        return list(self.processors.keys())
