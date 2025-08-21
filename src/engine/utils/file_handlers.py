"""
File Handling Utilities

Provides comprehensive file handling utilities for the AAS Data Modeling Engine.
Includes file operations, compression, encryption, and format detection.
"""

import os
import shutil
import hashlib
import mimetypes
import zipfile
import tarfile
import gzip
import bz2
import lzma
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable, BinaryIO
import logging
from dataclasses import dataclass
from enum import Enum
import json
import tempfile
import contextlib

logger = logging.getLogger(__name__)


class CompressionType(Enum):
    """Supported compression types"""
    NONE = "none"
    GZIP = "gzip"
    BZIP2 = "bzip2"
    LZMA = "lzma"
    ZIP = "zip"
    TAR = "tar"


@dataclass
class FileInfo:
    """File information structure"""
    path: Path
    size: int
    modified_time: float
    created_time: float
    is_file: bool
    is_dir: bool
    is_symlink: bool
    permissions: int
    owner: Optional[str] = None
    group: Optional[str] = None
    mime_type: Optional[str] = None
    encoding: Optional[str] = None
    checksum: Optional[str] = None


class FileHandlers:
    """Collection of file handling utilities"""
    
    @staticmethod
    def get_file_info(file_path: Union[str, Path]) -> FileInfo:
        """
        Get comprehensive file information
        
        Args:
            file_path: Path to the file
            
        Returns:
            FileInfo object with file details
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        stat = path.stat()
        
        # Get MIME type
        mime_type, encoding = mimetypes.guess_type(str(path))
        
        # Calculate checksum for files
        checksum = None
        if path.is_file():
            checksum = FileHandlers.calculate_checksum(path)
        
        return FileInfo(
            path=path,
            size=stat.st_size,
            modified_time=stat.st_mtime,
            created_time=stat.st_ctime,
            is_file=path.is_file(),
            is_dir=path.is_dir(),
            is_symlink=path.is_symlink(),
            permissions=stat.st_mode,
            mime_type=mime_type,
            encoding=encoding,
            checksum=checksum
        )
    
    @staticmethod
    def calculate_checksum(file_path: Union[str, Path], algorithm: str = "sha256") -> str:
        """
        Calculate file checksum
        
        Args:
            file_path: Path to the file
            algorithm: Hash algorithm to use
            
        Returns:
            Hexadecimal checksum string
        """
        path = Path(file_path)
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")
        
        hash_func = hashlib.new(algorithm)
        
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    @staticmethod
    def compress_file(
        source_path: Union[str, Path],
        target_path: Optional[Union[str, Path]] = None,
        compression_type: CompressionType = CompressionType.GZIP,
        remove_source: bool = False
    ) -> Path:
        """
        Compress a file
        
        Args:
            source_path: Path to source file
            target_path: Path for compressed file (auto-generated if None)
            compression_type: Type of compression to use
            remove_source: Whether to remove source file after compression
            
        Returns:
            Path to compressed file
        """
        source = Path(source_path)
        
        if not source.is_file():
            raise ValueError(f"Source path is not a file: {source}")
        
        if target_path is None:
            target = source.with_suffix(source.suffix + FileHandlers._get_compression_extension(compression_type))
        else:
            target = Path(target_path)
        
        try:
            if compression_type == CompressionType.GZIP:
                with open(source, 'rb') as f_in:
                    with gzip.open(target, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            
            elif compression_type == CompressionType.BZIP2:
                with open(source, 'rb') as f_in:
                    with bz2.open(target, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            
            elif compression_type == CompressionType.LZMA:
                with open(source, 'rb') as f_in:
                    with lzma.open(target, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            
            elif compression_type == CompressionType.ZIP:
                with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(source, source.name)
            
            elif compression_type == CompressionType.TAR:
                with tarfile.open(target, 'w:gz') as tarf:
                    tarf.add(source, arcname=source.name)
            
            else:
                raise ValueError(f"Unsupported compression type: {compression_type}")
            
            if remove_source:
                source.unlink()
            
            logger.info(f"File compressed: {source} -> {target}")
            return target
            
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            if target.exists():
                target.unlink()
            raise
    
    @staticmethod
    def _get_compression_extension(compression_type: CompressionType) -> str:
        """Get file extension for compression type"""
        extension_map = {
            CompressionType.GZIP: ".gz",
            CompressionType.BZIP2: ".bz2",
            CompressionType.LZMA: ".xz",
            CompressionType.ZIP: ".zip",
            CompressionType.TAR: ".tar.gz"
        }
        return extension_map.get(compression_type, "")
    
    @staticmethod
    def decompress_file(
        source_path: Union[str, Path],
        target_path: Optional[Union[str, Path]] = None,
        remove_source: bool = False
    ) -> Path:
        """
        Decompress a file
        
        Args:
            source_path: Path to compressed file
            target_path: Path for decompressed file (auto-generated if None)
            remove_source: Whether to remove source file after decompression
            
        Returns:
            Path to decompressed file
        """
        source = Path(source_path)
        
        if not source.is_file():
            raise ValueError(f"Source path is not a file: {source}")
        
        # Auto-detect compression type
        compression_type = FileHandlers._detect_compression_type(source)
        
        if target_path is None:
            target = FileHandlers._get_decompressed_path(source, compression_type)
        else:
            target = Path(target_path)
        
        try:
            if compression_type == CompressionType.GZIP:
                with gzip.open(source, 'rb') as f_in:
                    with open(target, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            
            elif compression_type == CompressionType.BZIP2:
                with bz2.open(source, 'rb') as f_in:
                    with open(target, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            
            elif compression_type == CompressionType.LZMA:
                with lzma.open(source, 'rb') as f_in:
                    with open(target, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            
            elif compression_type == CompressionType.ZIP:
                with zipfile.ZipFile(source, 'r') as zipf:
                    zipf.extractall(target.parent)
                    # For single file archives, rename extracted file
                    if len(zipf.namelist()) == 1:
                        extracted_file = target.parent / zipf.namelist()[0]
                        if extracted_file != target:
                            extracted_file.rename(target)
            
            elif compression_type == CompressionType.TAR:
                with tarfile.open(source, 'r:*') as tarf:
                    tarf.extractall(target.parent)
                    # For single file archives, rename extracted file
                    if len(tarf.getnames()) == 1:
                        extracted_file = target.parent / tarf.getnames()[0]
                        if extracted_file != target:
                            extracted_file.rename(target)
            
            else:
                raise ValueError(f"Unsupported compression type: {compression_type}")
            
            if remove_source:
                source.unlink()
            
            logger.info(f"File decompressed: {source} -> {target}")
            return target
            
        except Exception as e:
            logger.error(f"Decompression failed: {e}")
            if target.exists():
                target.unlink()
            raise
    
    @staticmethod
    def _detect_compression_type(file_path: Path) -> CompressionType:
        """Detect compression type from file extension and magic bytes"""
        # Check by extension first
        suffix = file_path.suffix.lower()
        if suffix == '.gz':
            return CompressionType.GZIP
        elif suffix == '.bz2':
            return CompressionType.BZIP2
        elif suffix == '.xz':
            return CompressionType.LZMA
        elif suffix == '.zip':
            return CompressionType.ZIP
        elif suffix in ['.tar', '.tar.gz', '.tgz']:
            return CompressionType.TAR
        
        # Check by magic bytes
        try:
            with open(file_path, 'rb') as f:
                magic = f.read(4)
                
                if magic.startswith(b'\x1f\x8b'):
                    return CompressionType.GZIP
                elif magic.startswith(b'BZ'):
                    return CompressionType.BZIP2
                elif magic.startswith(b'\xfd7zXZ'):
                    return CompressionType.LZMA
                elif magic.startswith(b'PK'):
                    return CompressionType.ZIP
                elif magic.startswith(b'\x75\x73\x74\x61\x72'):
                    return CompressionType.TAR
        except Exception:
            pass
        
        return CompressionType.NONE
    
    @staticmethod
    def _get_decompressed_path(compressed_path: Path, compression_type: CompressionType) -> Path:
        """Get path for decompressed file"""
        if compression_type == CompressionType.NONE:
            return compressed_path
        
        # Remove compression extensions
        name = compressed_path.stem
        if compression_type == CompressionType.TAR and name.endswith('.tar'):
            name = name[:-4]
        
        return compressed_path.parent / name
    
    @staticmethod
    def copy_file(
        source: Union[str, Path],
        target: Union[str, Path],
        preserve_metadata: bool = True,
        overwrite: bool = False
    ) -> Path:
        """
        Copy file with metadata preservation
        
        Args:
            source: Source file path
            target: Target file path
            preserve_metadata: Whether to preserve file metadata
            overwrite: Whether to overwrite existing target
            
        Returns:
            Path to copied file
        """
        source_path = Path(source)
        target_path = Path(target)
        
        if not source_path.is_file():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        if target_path.exists() and not overwrite:
            raise FileExistsError(f"Target file already exists: {target_path}")
        
        # Ensure target directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        if preserve_metadata:
            shutil.copy2(source_path, target_path)
        else:
            shutil.copy(source_path, target_path)
        
        logger.info(f"File copied: {source_path} -> {target_path}")
        return target_path
    
    @staticmethod
    def move_file(
        source: Union[str, Path],
        target: Union[str, Path],
        overwrite: bool = False
    ) -> Path:
        """
        Move file to new location
        
        Args:
            source: Source file path
            target: Target file path
            overwrite: Whether to overwrite existing target
            
        Returns:
            Path to moved file
        """
        source_path = Path(source)
        target_path = Path(target)
        
        if not source_path.is_file():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        if target_path.exists() and not overwrite:
            raise FileExistsError(f"Target file already exists: {target_path}")
        
        # Ensure target directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.move(str(source_path), str(target_path))
        
        logger.info(f"File moved: {source_path} -> {target_path}")
        return target_path
    
    @staticmethod
    def safe_delete(
        file_path: Union[str, Path],
        backup: bool = True,
        backup_dir: Optional[Union[str, Path]] = None
    ) -> bool:
        """
        Safely delete file with optional backup
        
        Args:
            file_path: Path to file to delete
            backup: Whether to create backup before deletion
            backup_dir: Directory for backup (auto-generated if None)
            
        Returns:
            True if deletion successful
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.warning(f"File does not exist: {path}")
            return True
        
        try:
            if backup:
                if backup_dir is None:
                    backup_dir = path.parent / ".backups"
                
                backup_path = Path(backup_dir) / f"{path.name}.{int(path.stat().st_mtime)}"
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.copy2(path, backup_path)
                logger.info(f"Backup created: {backup_path}")
            
            path.unlink()
            logger.info(f"File deleted: {path}")
            return True
            
        except Exception as e:
            logger.error(f"File deletion failed: {e}")
            return False
    
    @staticmethod
    def find_files(
        directory: Union[str, Path],
        pattern: str = "*",
        recursive: bool = True,
        include_dirs: bool = False,
        include_files: bool = True
    ) -> List[Path]:
        """
        Find files matching pattern
        
        Args:
            directory: Directory to search
            pattern: File pattern to match
            recursive: Whether to search recursively
            include_dirs: Whether to include directories
            include_files: Whether to include files
            
        Returns:
            List of matching paths
        """
        dir_path = Path(directory)
        
        if not dir_path.is_dir():
            raise ValueError(f"Directory not found: {dir_path}")
        
        matches = []
        
        if recursive:
            for item in dir_path.rglob(pattern):
                if (include_dirs and item.is_dir()) or (include_files and item.is_file()):
                    matches.append(item)
        else:
            for item in dir_path.glob(pattern):
                if (include_dirs and item.is_dir()) or (include_files and item.is_file()):
                    matches.append(item)
        
        return sorted(matches)
    
    @staticmethod
    def get_directory_size(directory: Union[str, Path]) -> int:
        """
        Calculate total size of directory
        
        Args:
            directory: Directory path
            
        Returns:
            Total size in bytes
        """
        dir_path = Path(directory)
        
        if not dir_path.is_dir():
            raise ValueError(f"Path is not a directory: {dir_path}")
        
        total_size = 0
        
        for item in dir_path.rglob("*"):
            if item.is_file():
                total_size += item.stat().st_size
        
        return total_size
    
    @staticmethod
    def create_temp_file(
        suffix: str = "",
        prefix: str = "temp_",
        directory: Optional[Union[str, Path]] = None,
        delete_on_close: bool = True
    ) -> Path:
        """
        Create temporary file
        
        Args:
            suffix: File suffix
            prefix: File prefix
            directory: Directory for temp file
            delete_on_close: Whether to delete file when closed
            
        Returns:
            Path to temporary file
        """
        temp_file = tempfile.NamedTemporaryFile(
            suffix=suffix,
            prefix=prefix,
            dir=directory,
            delete=delete_on_close
        )
        temp_file.close()
        return Path(temp_file.name)
    
    @staticmethod
    def create_temp_directory(
        suffix: str = "",
        prefix: str = "temp_",
        directory: Optional[Union[str, Path]] = None
    ) -> Path:
        """
        Create temporary directory
        
        Args:
            suffix: Directory suffix
            prefix: Directory prefix
            directory: Parent directory for temp directory
            
        Returns:
            Path to temporary directory
        """
        temp_dir = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=directory)
        return Path(temp_dir)
    
    @staticmethod
    @contextlib.contextmanager
    def temp_file_context(
        suffix: str = "",
        prefix: str = "temp_",
        directory: Optional[Union[str, Path]] = None
    ):
        """
        Context manager for temporary file
        
        Args:
            suffix: File suffix
            prefix: File prefix
            directory: Directory for temp file
            
        Yields:
            Path to temporary file
        """
        temp_file = FileHandlers.create_temp_file(suffix, prefix, directory, delete_on_close=False)
        try:
            yield temp_file
        finally:
            if temp_file.exists():
                temp_file.unlink()
    
    @staticmethod
    @contextlib.contextmanager
    def temp_directory_context(
        suffix: str = "",
        prefix: str = "temp_",
        directory: Optional[Union[str, Path]] = None
    ):
        """
        Context manager for temporary directory
        
        Args:
            suffix: Directory suffix
            prefix: Directory prefix
            directory: Parent directory for temp directory
            
        Yields:
            Path to temporary directory
        """
        temp_dir = FileHandlers.create_temp_directory(suffix, prefix, directory)
        try:
            yield temp_dir
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
    
    @staticmethod
    def read_text_file(
        file_path: Union[str, Path],
        encoding: str = "utf-8",
        errors: str = "strict"
    ) -> str:
        """
        Read text file content
        
        Args:
            file_path: Path to text file
            encoding: File encoding
            errors: Error handling strategy
            
        Returns:
            File content as string
        """
        path = Path(file_path)
        
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")
        
        with open(path, 'r', encoding=encoding, errors=errors) as f:
            return f.read()
    
    @staticmethod
    def write_text_file(
        file_path: Union[str, Path],
        content: str,
        encoding: str = "utf-8",
        create_dirs: bool = True
    ) -> Path:
        """
        Write content to text file
        
        Args:
            file_path: Path to text file
            content: Content to write
            encoding: File encoding
            create_dirs: Whether to create parent directories
            
        Returns:
            Path to written file
        """
        path = Path(file_path)
        
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
        
        logger.info(f"Text file written: {path}")
        return path
    
    @staticmethod
    def read_json_file(
        file_path: Union[str, Path],
        encoding: str = "utf-8"
    ) -> Any:
        """
        Read JSON file content
        
        Args:
            file_path: Path to JSON file
            encoding: File encoding
            
        Returns:
            Parsed JSON content
        """
        content = FileHandlers.read_text_file(file_path, encoding)
        return json.loads(content)
    
    @staticmethod
    def write_json_file(
        file_path: Union[str, Path],
        data: Any,
        indent: int = 2,
        encoding: str = "utf-8",
        create_dirs: bool = True
    ) -> Path:
        """
        Write data to JSON file
        
        Args:
            file_path: Path to JSON file
            data: Data to write
            indent: JSON indentation
            encoding: File encoding
            create_dirs: Whether to create parent directories
            
        Returns:
            Path to written file
        """
        content = json.dumps(data, indent=indent, ensure_ascii=False, default=str)
        return FileHandlers.write_text_file(file_path, content, encoding, create_dirs)


# Convenience functions
def get_file_info(file_path: Union[str, Path]) -> FileInfo:
    """Convenience function for getting file info"""
    return FileHandlers.get_file_info(file_path)


def compress_file(
    source_path: Union[str, Path],
    target_path: Optional[Union[str, Path]] = None,
    compression_type: CompressionType = CompressionType.GZIP,
    remove_source: bool = False
) -> Path:
    """Convenience function for file compression"""
    return FileHandlers.compress_file(source_path, target_path, compression_type, remove_source)


def decompress_file(
    source_path: Union[str, Path],
    target_path: Optional[Union[str, Path]] = None,
    remove_source: bool = False
) -> Path:
    """Convenience function for file decompression"""
    return FileHandlers.decompress_file(source_path, target_path, remove_source)


def copy_file(
    source: Union[str, Path],
    target: Union[str, Path],
    preserve_metadata: bool = True,
    overwrite: bool = False
) -> Path:
    """Convenience function for file copying"""
    return FileHandlers.copy_file(source, target, preserve_metadata, overwrite)


def move_file(
    source: Union[str, Path],
    target: Union[str, Path],
    overwrite: bool = False
) -> Path:
    """Convenience function for file moving"""
    return FileHandlers.move_file(source, target, overwrite)


def safe_delete(
    file_path: Union[str, Path],
    backup: bool = True,
    backup_dir: Optional[Union[str, Path]] = None
) -> bool:
    """Convenience function for safe file deletion"""
    return FileHandlers.safe_delete(file_path, backup, backup_dir)
