"""
File Utilities
=============

Common file handling utilities for the AAS Data Modeling framework.
"""

import os
import hashlib
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import shutil
import zipfile
import tempfile
import logging

logger = logging.getLogger(__name__)

class FileUtils:
    """Utility class for file operations."""
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = {'.aasx', '.aas', '.xml', '.json', '.zip'}
    
    # Maximum file size (100MB)
    MAX_FILE_SIZE = 100 * 1024 * 1024
    
    @staticmethod
    def get_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
        """Calculate file hash using specified algorithm."""
        try:
            hash_func = hashlib.new(algorithm)
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating file hash for {file_path}: {e}")
            raise
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """Get comprehensive file information."""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            stat = path.stat()
            mime_type, _ = mimetypes.guess_type(str(path))
            
            return {
                'filename': path.name,
                'original_filename': path.name,
                'size': stat.st_size,
                'mime_type': mime_type or 'application/octet-stream',
                'extension': path.suffix.lower(),
                'created_time': stat.st_ctime,
                'modified_time': stat.st_mtime,
                'is_readable': os.access(file_path, os.R_OK),
                'is_writable': os.access(file_path, os.W_OK),
                'hash': FileUtils.get_file_hash(file_path)
            }
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            raise
    
    @staticmethod
    def validate_file(file_path: str) -> Tuple[bool, List[str]]:
        """Validate file for upload/processing."""
        errors = []
        
        try:
            path = Path(file_path)
            
            # Check if file exists
            if not path.exists():
                errors.append("File does not exist")
                return False, errors
            
            # Check if it's a file (not directory)
            if not path.is_file():
                errors.append("Path is not a file")
                return False, errors
            
            # Check file size
            size = path.stat().st_size
            if size > FileUtils.MAX_FILE_SIZE:
                errors.append(f"File size ({size} bytes) exceeds maximum allowed size ({FileUtils.MAX_FILE_SIZE} bytes)")
            
            # Check file extension
            extension = path.suffix.lower()
            if extension not in FileUtils.SUPPORTED_EXTENSIONS:
                errors.append(f"File extension '{extension}' is not supported. Supported: {FileUtils.SUPPORTED_EXTENSIONS}")
            
            # Check if file is readable
            if not os.access(file_path, os.R_OK):
                errors.append("File is not readable")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Error validating file: {str(e)}")
            return False, errors
    
    @staticmethod
    def create_directory_structure(base_path: str, use_case_name: str, project_name: str) -> str:
        """Create hierarchical directory structure for files."""
        try:
            # Sanitize names for filesystem
            safe_use_case = FileUtils._sanitize_filename(use_case_name)
            safe_project = FileUtils._sanitize_filename(project_name)
            
            # Create full path
            full_path = Path(base_path) / safe_use_case / safe_project
            full_path.mkdir(parents=True, exist_ok=True)
            
            return str(full_path)
        except Exception as e:
            logger.error(f"Error creating directory structure: {e}")
            raise
    
    @staticmethod
    def copy_file_to_destination(source_path: str, destination_path: str) -> bool:
        """Copy file to destination with error handling."""
        try:
            # Ensure destination directory exists
            dest_dir = Path(destination_path).parent
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source_path, destination_path)
            logger.info(f"File copied from {source_path} to {destination_path}")
            return True
        except Exception as e:
            logger.error(f"Error copying file from {source_path} to {destination_path}: {e}")
            return False
    
    @staticmethod
    def move_file_to_destination(source_path: str, destination_path: str) -> bool:
        """Move file to destination with error handling."""
        try:
            # Ensure destination directory exists
            dest_dir = Path(destination_path).parent
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Move file
            shutil.move(source_path, destination_path)
            logger.info(f"File moved from {source_path} to {destination_path}")
            return True
        except Exception as e:
            logger.error(f"Error moving file from {source_path} to {destination_path}: {e}")
            return False
    
    @staticmethod
    def delete_file_safely(file_path: str) -> bool:
        """Safely delete file with error handling."""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"File deleted: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False
    
    @staticmethod
    def extract_zip_file(zip_path: str, extract_to: str) -> List[str]:
        """Extract ZIP file and return list of extracted files."""
        extracted_files = []
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
                extracted_files = zip_ref.namelist()
                logger.info(f"Extracted {len(extracted_files)} files from {zip_path}")
                return extracted_files
        except Exception as e:
            logger.error(f"Error extracting ZIP file {zip_path}: {e}")
            raise
    
    @staticmethod
    def create_temp_file(suffix: str = '', prefix: str = 'aas_') -> Tuple[str, str]:
        """Create a temporary file and return (file_path, temp_dir)."""
        try:
            temp_dir = tempfile.mkdtemp(prefix=prefix)
            temp_file = tempfile.NamedTemporaryFile(
                dir=temp_dir, 
                suffix=suffix, 
                delete=False
            )
            temp_file.close()
            return temp_file.name, temp_dir
        except Exception as e:
            logger.error(f"Error creating temporary file: {e}")
            raise
    
    @staticmethod
    def cleanup_temp_directory(temp_dir: str) -> bool:
        """Clean up temporary directory and its contents."""
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error cleaning up temporary directory {temp_dir}: {e}")
            return False
    
    @staticmethod
    def get_directory_size(directory_path: str) -> int:
        """Calculate total size of directory and its contents."""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
            return total_size
        except Exception as e:
            logger.error(f"Error calculating directory size for {directory_path}: {e}")
            return 0
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Sanitize filename for filesystem compatibility."""
        # Replace problematic characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')
        
        # Limit length
        if len(filename) > 255:
            filename = filename[:255]
        
        return filename
    
    @staticmethod
    def is_aasx_file(file_path: str) -> bool:
        """Check if file is an AASX file."""
        try:
            # Check extension
            if not file_path.lower().endswith('.aasx'):
                return False
            
            # Check if it's a valid ZIP file (AASX files are ZIP archives)
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                # Check for AASX-specific files
                file_list = zip_ref.namelist()
                return any(name.endswith('.aas') or name.endswith('.xml') for name in file_list)
        except Exception:
            return False
    
    @staticmethod
    def get_file_metadata(file_path: str) -> Dict[str, Any]:
        """Extract metadata from file."""
        try:
            info = FileUtils.get_file_info(file_path)
            
            # Add additional metadata based on file type
            if FileUtils.is_aasx_file(file_path):
                info['file_type'] = 'aasx'
                info['is_archive'] = True
            elif file_path.lower().endswith('.zip'):
                info['file_type'] = 'zip'
                info['is_archive'] = True
            else:
                info['file_type'] = 'unknown'
                info['is_archive'] = False
            
            return info
        except Exception as e:
            logger.error(f"Error extracting file metadata for {file_path}: {e}")
            raise 