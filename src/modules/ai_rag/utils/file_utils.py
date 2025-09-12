"""
File utilities for AI RAG module
Provides common file handling and manipulation functions
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional, Union
import logging

logger = logging.getLogger(__name__)


def ensure_directory(directory_path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, create it if it doesn't.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        Path object of the ensured directory
    """
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_extension(file_path: Union[str, Path]) -> str:
    """
    Get the file extension from a file path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File extension (without the dot)
    """
    return Path(file_path).suffix.lower().lstrip('.')


def validate_file_path(file_path: Union[str, Path]) -> bool:
    """
    Validate if a file path exists and is accessible.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file is valid and accessible, False otherwise
    """
    try:
        path = Path(file_path)
        return path.exists() and path.is_file() and os.access(path, os.R_OK)
    except Exception as e:
        logger.warning(f"File path validation failed: {e}")
        return False


def create_temp_file(
    prefix: str = "ai_rag_",
    suffix: str = ".tmp",
    directory: Optional[Union[str, Path]] = None
) -> Path:
    """
    Create a temporary file with specified parameters.
    
    Args:
        prefix: File name prefix
        suffix: File name suffix
        directory: Directory to create temp file in
        
    Returns:
        Path to the created temporary file
    """
    try:
        temp_file = tempfile.NamedTemporaryFile(
            prefix=prefix,
            suffix=suffix,
            dir=directory,
            delete=False
        )
        temp_file.close()
        return Path(temp_file.name)
    except Exception as e:
        logger.error(f"Failed to create temporary file: {e}")
        raise


def cleanup_temp_files(temp_files: List[Union[str, Path]]) -> None:
    """
    Clean up a list of temporary files.
    
    Args:
        temp_files: List of temporary file paths to clean up
    """
    for temp_file in temp_files:
        try:
            path = Path(temp_file)
            if path.exists():
                path.unlink()
                logger.debug(f"Cleaned up temporary file: {path}")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary file {temp_file}: {e}")


def get_file_size(file_path: Union[str, Path]) -> int:
    """
    Get the size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes
    """
    try:
        return Path(file_path).stat().st_size
    except Exception as e:
        logger.error(f"Failed to get file size for {file_path}: {e}")
        return 0


def copy_file_with_metadata(
    source: Union[str, Path],
    destination: Union[str, Path],
    preserve_metadata: bool = True
) -> bool:
    """
    Copy a file with optional metadata preservation.
    
    Args:
        source: Source file path
        destination: Destination file path
        preserve_metadata: Whether to preserve file metadata
        
    Returns:
        True if copy was successful, False otherwise
    """
    try:
        source_path = Path(source)
        dest_path = Path(destination)
        
        # Ensure destination directory exists
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        if preserve_metadata:
            shutil.copy2(source_path, dest_path)
        else:
            shutil.copy(source_path, dest_path)
            
        logger.debug(f"Copied file from {source} to {destination}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to copy file from {source} to {destination}: {e}")
        return False


def find_files_by_pattern(
    directory: Union[str, Path],
    pattern: str,
    recursive: bool = True
) -> List[Path]:
    """
    Find files matching a pattern in a directory.
    
    Args:
        directory: Directory to search in
        pattern: File pattern to match (e.g., "*.txt")
        recursive: Whether to search recursively
        
    Returns:
        List of matching file paths
    """
    try:
        dir_path = Path(directory)
        if recursive:
            return list(dir_path.rglob(pattern))
        else:
            return list(dir_path.glob(pattern))
    except Exception as e:
        logger.error(f"Failed to find files with pattern {pattern} in {directory}: {e}")
        return []


def safe_filename(filename: str, max_length: int = 255) -> str:
    """
    Convert a filename to a safe filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename
        max_length: Maximum length for the filename
        
    Returns:
        Safe filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    safe_name = filename
    for char in invalid_chars:
        safe_name = safe_name.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    safe_name = safe_name.strip(' .')
    
    # Ensure filename is not empty
    if not safe_name:
        safe_name = "unnamed_file"
    
    # Truncate if too long
    if len(safe_name) > max_length:
        name_part = safe_name[:max_length-10]
        safe_name = f"{name_part}_truncated"
    
    return safe_name





