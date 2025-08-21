"""
Processor manager for coordinating different data processors.
"""

from pathlib import Path
from typing import Dict, Any, List
from .base_processor import BaseDataProcessor
from .structured_data_processor import StructuredDataProcessor
from .graph_data_processor import GraphDataProcessor
from .document_processor import DocumentProcessor
from .image_processor import ImageProcessor
from .code_processor import CodeProcessor
from .spreadsheet_processor import SpreadsheetProcessor
from .cad_processor import CADProcessor


class ProcessorManager:
    """Manages different data processors."""
    
    def __init__(self, text_embedding_manager=None, vector_db=None):
        """
        Initialize processor manager.
        
        Args:
            text_embedding_manager: Text embedding manager instance
            vector_db: Vector database client instance
        """
        import logging
        self.logger = logging.getLogger(__name__)
        self.text_embedding_manager = text_embedding_manager
        self.vector_db = vector_db
        
        # Initialize processors in order of specificity
        self.processors: List[BaseDataProcessor] = [
            # Most specific processors first
            GraphDataProcessor(text_embedding_manager, vector_db),
            StructuredDataProcessor(text_embedding_manager, vector_db),
            CADProcessor(text_embedding_manager, vector_db),
            SpreadsheetProcessor(text_embedding_manager, vector_db),
            DocumentProcessor(text_embedding_manager, vector_db),
            ImageProcessor(text_embedding_manager, vector_db),
            CodeProcessor(text_embedding_manager, vector_db),
        ]
    
    def get_processor(self, file_path: Path) -> BaseDataProcessor:
        """
        Get the appropriate processor for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Processor that can handle the file, or None if no processor found
        """
        # Check processors in order of specificity
        # More specific processors should be checked first
        for processor in self.processors:
            if processor.can_process(file_path):
                # Log which processor was selected for debugging
                self.logger.debug(f"Selected {processor.__class__.__name__} for {file_path.name}")
                return processor
        return None
    
    def can_process_file(self, file_path: Path) -> bool:
        """
        Check if any processor can handle the file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if a processor can handle the file
        """
        return self.get_processor(file_path) is not None
    
    def process_file(self, project_id: str, file_info: Dict[str, Any], file_path: Path) -> Dict[str, Any]:
        """
        Process a file using the appropriate processor.
        
        Args:
            project_id: Project identifier
            file_info: File information from project manager
            file_path: Path to the file to process
            
        Returns:
            Dictionary containing processing results
        """
        processor = self.get_processor(file_path)
        if not processor:
            return {
                'file_id': file_info.get('file_id'),
                'filename': file_path.name,
                'status': 'skipped',
                'reason': f'No processor available for file type: {file_path.suffix}'
            }
        
        return processor.process(project_id, file_info, file_path)
    

    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        extensions = set()
        for processor in self.processors:
            # This is a simplified approach - in practice, you might want to
            # add a method to each processor to return supported extensions
            if isinstance(processor, StructuredDataProcessor):
                extensions.update(['.json', '.yaml', '.yml'])
            elif isinstance(processor, GraphDataProcessor):
                extensions.add('.json')  # Only graph JSON files
            elif isinstance(processor, DocumentProcessor):
                extensions.update(['.pdf', '.docx', '.doc', '.txt', '.rtf', '.odt'])
            elif isinstance(processor, ImageProcessor):
                extensions.update(['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp'])
            elif isinstance(processor, SpreadsheetProcessor):
                extensions.update(['.xlsx', '.xls', '.csv', '.tsv', '.ods', '.xlsm', '.xlsb'])
            elif isinstance(processor, CADProcessor):
                extensions.update([
                    '.dwg', '.dxf', '.dwt', '.dws', '.step', '.stp', '.iges', '.igs', '.stl', '.obj', '.ply', '.3ds', '.dae',
                    '.sldprt', '.sldasm', '.prt', '.asm', '.ipt', '.iam', '.catpart', '.catproduct',
                    '.par', '.psm', '.x_t', '.x_b', '.sat', '.neu', '.svg', '.ai', '.eps', '.cdr'
                ])
            elif isinstance(processor, CodeProcessor):
                extensions.update([
                    '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.cc', '.cxx',
                    '.h', '.hpp', '.hxx', '.cs', '.go', '.rs', '.php', '.rb', '.swift', '.kt',
                    '.scala', '.r', '.m', '.sh', '.ps1', '.bat', '.sql', '.md', '.markdown',
                    '.xml', '.html', '.htm', '.css', '.scss', '.sass', '.less', '.tf', '.tfvars'
                ])
        return list(extensions)
    
    def list_processors(self) -> List[str]:
        """List all available processors."""
        return [processor.__class__.__name__ for processor in self.processors]
    
    def get_processor_info(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed information about each processor."""
        info = {}
        for processor in self.processors:
            processor_name = processor.__class__.__name__
            info[processor_name] = {
                'name': processor_name,
                'description': processor.__doc__ or 'No description available',
                'supported_extensions': self._get_processor_extensions(processor),
                'type': self._get_processor_type(processor)
            }
        return info
    
    def _get_processor_extensions(self, processor: BaseDataProcessor) -> List[str]:
        """Get supported extensions for a specific processor."""
        if isinstance(processor, StructuredDataProcessor):
            return ['.json', '.yaml', '.yml']
        elif isinstance(processor, GraphDataProcessor):
            return ['.json']  # Only graph JSON files
        elif isinstance(processor, DocumentProcessor):
            return ['.pdf', '.docx', '.doc', '.txt', '.rtf', '.odt']
        elif isinstance(processor, ImageProcessor):
            return ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp']
        elif isinstance(processor, SpreadsheetProcessor):
            return ['.xlsx', '.xls', '.csv', '.tsv', '.ods', '.xlsm', '.xlsb']
        elif isinstance(processor, CADProcessor):
            return [
                '.dwg', '.dxf', '.dwt', '.dws', '.step', '.stp', '.iges', '.igs', '.stl', '.obj', '.ply', '.3ds', '.dae',
                '.sldprt', '.sldasm', '.prt', '.asm', '.ipt', '.iam', '.catpart', '.catproduct',
                '.par', '.psm', '.x_t', '.x_b', '.sat', '.neu', '.svg', '.ai', '.eps', '.cdr'
            ]
        elif isinstance(processor, CodeProcessor):
            return [
                '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.cc', '.cxx',
                '.h', '.hpp', '.hxx', '.cs', '.go', '.rs', '.php', '.rb', '.swift', '.kt',
                '.scala', '.r', '.m', '.sh', '.ps1', '.bat', '.sql', '.md', '.markdown',
                '.xml', '.html', '.htm', '.css', '.scss', '.sass', '.less', '.tf', '.tfvars'
            ]
        else:
            return []
    
    def _get_processor_type(self, processor: BaseDataProcessor) -> str:
        """Get the type/category of a processor."""
        if isinstance(processor, StructuredDataProcessor):
            return 'structured_data'
        elif isinstance(processor, GraphDataProcessor):
            return 'graph_data'
        elif isinstance(processor, DocumentProcessor):
            return 'document'
        elif isinstance(processor, ImageProcessor):
            return 'image'
        elif isinstance(processor, SpreadsheetProcessor):
            return 'spreadsheet'
        elif isinstance(processor, CADProcessor):
            return 'cad'
        elif isinstance(processor, CodeProcessor):
            return 'code'
        else:
            return 'unknown' 