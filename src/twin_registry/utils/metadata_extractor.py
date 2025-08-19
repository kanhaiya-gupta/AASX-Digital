"""
Metadata Extractor for Twin Registry Population
Provides functions for extracting metadata from various sources
"""
import logging
import json
import sqlite3
import hashlib
import mimetypes
from typing import Dict, Any, Optional, List, Union, Tuple
from pathlib import Path
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
import yaml
import zipfile
import tarfile

logger = logging.getLogger(__name__)

class MetadataExtractor:
    """Metadata extraction utilities for twin registry population"""
    
    def __init__(self):
        self.supported_file_types = {
            '.aasx': self._extract_aasx_metadata,
            '.json': self._extract_json_metadata,
            '.xml': self._extract_xml_metadata,
            '.yaml': self._extract_yaml_metadata,
            '.yml': self._extract_yaml_metadata,
            '.csv': self._extract_csv_metadata,
            '.txt': self._extract_text_metadata,
            '.zip': self._extract_archive_metadata,
            '.tar': self._extract_archive_metadata,
            '.gz': self._extract_archive_metadata,
            '.7z': self._extract_archive_metadata
        }
        
        self.metadata_patterns = {
            'version': r'version["\']?\s*[:=]\s*["\']?([^"\']+)["\']?',
            'author': r'author["\']?\s*[:=]\s*["\']?([^"\']+)["\']?',
            'description': r'description["\']?\s*[:=]\s*["\']?([^"\']+)["\']?',
            'created': r'created["\']?\s*[:=]\s*["\']?([^"\']+)["\']?',
            'modified': r'modified["\']?\s*[:=]\s*["\']?([^"\']+)["\']?',
            'license': r'license["\']?\s*[:=]\s*["\']?([^"\']+)["\']?',
            'keywords': r'keywords?["\']?\s*[:=]\s*\[([^\]]+)\]',
            'tags': r'tags?["\']?\s*[:=]\s*\[([^\]]+)\]'
        }
    
    async def extract_file_metadata(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Extract metadata from a file based on its type"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Basic file metadata
            basic_metadata = self._extract_basic_file_metadata(file_path)
            
            # Type-specific metadata
            file_extension = file_path.suffix.lower()
            type_metadata = {}
            
            if file_extension in self.supported_file_types:
                try:
                    type_metadata = await self.supported_file_types[file_extension](file_path)
                except Exception as e:
                    logger.warning(f"Failed to extract type-specific metadata for {file_path}: {e}")
                    type_metadata = {}
            
            # Pattern-based metadata extraction
            pattern_metadata = self._extract_pattern_metadata(file_path)
            
            # Combine all metadata
            combined_metadata = {
                **basic_metadata,
                **type_metadata,
                **pattern_metadata,
                'extraction_timestamp': datetime.now(timezone.utc).isoformat(),
                'extraction_method': 'automatic'
            }
            
            return combined_metadata
            
        except Exception as e:
            logger.error(f"Failed to extract metadata from {file_path}: {e}")
            return self._create_error_metadata(e, {'file_path': str(file_path)})
    
    def _extract_basic_file_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract basic file system metadata"""
        try:
            stat = file_path.stat()
            
            return {
                'file_name': file_path.name,
                'file_path': str(file_path),
                'file_size': stat.st_size,
                'file_extension': file_path.suffix.lower(),
                'mime_type': mimetypes.guess_type(str(file_path))[0] or 'unknown',
                'created_time': datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat(),
                'modified_time': datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                'accessed_time': datetime.fromtimestamp(stat.st_atime, tz=timezone.utc).isoformat(),
                'file_hash': self._calculate_file_hash(file_path),
                'is_file': file_path.is_file(),
                'is_directory': file_path.is_dir(),
                'is_symlink': file_path.is_symlink(),
                'permissions': oct(stat.st_mode)[-3:]
            }
        except Exception as e:
            logger.error(f"Failed to extract basic metadata for {file_path}: {e}")
            return {}
    
    async def _extract_aasx_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from AASX files"""
        try:
            metadata = {
                'file_type': 'aasx',
                'aasx_version': 'unknown',
                'aas_elements': 0,
                'submodels': 0,
                'assets': 0,
                'concept_descriptions': 0,
                'aas_metadata': {}
            }
            
            # Try to extract from AASX package
            if zipfile.is_zipfile(file_path):
                with zipfile.ZipFile(file_path, 'r') as zip_file:
                    # Look for AASX manifest
                    manifest_files = [f for f in zip_file.namelist() if 'manifest' in f.lower()]
                    
                    for manifest_file in manifest_files:
                        try:
                            with zip_file.open(manifest_file) as manifest:
                                manifest_content = manifest.read().decode('utf-8', errors='ignore')
                                manifest_metadata = self._parse_aasx_manifest(manifest_content)
                                metadata.update(manifest_metadata)
                        except Exception as e:
                            logger.warning(f"Failed to parse manifest {manifest_file}: {e}")
                    
                    # Count AAS elements
                    aas_files = [f for f in zip_file.namelist() if f.endswith('.xml') or f.endswith('.json')]
                    metadata['aas_elements'] = len(aas_files)
                    
                    # Look for specific AAS files
                    for aas_file in aas_files:
                        if 'submodel' in aas_file.lower():
                            metadata['submodels'] += 1
                        elif 'asset' in aas_file.lower():
                            metadata['assets'] += 1
                        elif 'concept' in aas_file.lower():
                            metadata['concept_descriptions'] += 1
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to extract AASX metadata from {file_path}: {e}")
            return {'file_type': 'aasx', 'error': str(e)}
    
    async def _extract_json_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from JSON files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                data = json.loads(content)
            
            metadata = {
                'file_type': 'json',
                'json_structure': self._analyze_json_structure(data),
                'json_size': len(content),
                'root_keys': list(data.keys()) if isinstance(data, dict) else [],
                'data_types': self._get_json_data_types(data)
            }
            
            # Extract common metadata fields
            if isinstance(data, dict):
                metadata.update(self._extract_json_common_fields(data))
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to extract JSON metadata from {file_path}: {e}")
            return {'file_type': 'json', 'error': str(e)}
    
    async def _extract_xml_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from XML files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse XML
            root = ET.fromstring(content)
            
            metadata = {
                'file_type': 'xml',
                'xml_size': len(content),
                'root_tag': root.tag,
                'xml_namespaces': self._extract_xml_namespaces(root),
                'element_count': len(root.findall('.//*')),
                'attribute_count': len(root.attrib),
                'max_depth': self._calculate_xml_depth(root)
            }
            
            # Extract common XML metadata
            metadata.update(self._extract_xml_common_fields(root))
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to extract XML metadata from {file_path}: {e}")
            return {'file_type': 'xml', 'error': str(e)}
    
    async def _extract_yaml_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from YAML files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                data = yaml.safe_load(content)
            
            metadata = {
                'file_type': 'yaml',
                'yaml_size': len(content),
                'yaml_structure': self._analyze_yaml_structure(data),
                'root_keys': list(data.keys()) if isinstance(data, dict) else [],
                'data_types': self._get_yaml_data_types(data)
            }
            
            # Extract common metadata fields
            if isinstance(data, dict):
                metadata.update(self._extract_yaml_common_fields(data))
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to extract YAML metadata from {file_path}: {e}")
            return {'file_type': 'yaml', 'error': str(e)}
    
    async def _extract_csv_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from CSV files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            metadata = {
                'file_type': 'csv',
                'csv_size': len(''.join(lines)),
                'line_count': len(lines),
                'has_header': len(lines) > 0,
                'column_count': 0,
                'sample_data': []
            }
            
            if lines:
                # Count columns (assuming comma-separated)
                first_line = lines[0].strip()
                metadata['column_count'] = len(first_line.split(','))
                
                # Sample data (first few lines)
                metadata['sample_data'] = [line.strip() for line in lines[:5]]
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to extract CSV metadata from {file_path}: {e}")
            return {'file_type': 'csv', 'error': str(e)}
    
    async def _extract_text_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from text files"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            metadata = {
                'file_type': 'text',
                'text_size': len(content),
                'line_count': len(content.splitlines()),
                'word_count': len(content.split()),
                'character_count': len(content),
                'encoding': 'utf-8',
                'has_bom': content.startswith('\ufeff')
            }
            
            # Try to detect language/format
            metadata['detected_format'] = self._detect_text_format(content)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to extract text metadata from {file_path}: {e}")
            return {'file_type': 'text', 'error': str(e)}
    
    async def _extract_archive_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from archive files"""
        try:
            metadata = {
                'file_type': 'archive',
                'archive_type': file_path.suffix.lower(),
                'file_count': 0,
                'total_size': 0,
                'compressed_size': file_path.stat().st_size,
                'compression_ratio': 0.0,
                'archive_contents': []
            }
            
            if zipfile.is_zipfile(file_path):
                with zipfile.ZipFile(file_path, 'r') as zip_file:
                    file_list = zip_file.filelist
                    metadata['file_count'] = len(file_list)
                    metadata['total_size'] = sum(f.file_size for f in file_list)
                    metadata['archive_contents'] = [f.filename for f in file_list[:10]]  # First 10 files
                    
                    if metadata['total_size'] > 0:
                        metadata['compression_ratio'] = metadata['compressed_size'] / metadata['total_size']
            
            elif file_path.suffix.lower() in ['.tar', '.gz']:
                try:
                    with tarfile.open(file_path, 'r:*') as tar_file:
                        file_list = tar_file.getmembers()
                        metadata['file_count'] = len(file_list)
                        metadata['total_size'] = sum(f.size for f in file_list if f.isfile())
                        metadata['archive_contents'] = [f.name for f in file_list[:10] if f.isfile()]
                        
                        if metadata['total_size'] > 0:
                            metadata['compression_ratio'] = metadata['compressed_size'] / metadata['total_size']
                except Exception as e:
                    logger.warning(f"Failed to extract tar metadata: {e}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to extract archive metadata from {file_path}: {e}")
            return {'file_type': 'archive', 'error': str(e)}
    
    def _extract_pattern_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata using pattern matching"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            metadata = {}
            
            for field_name, pattern in self.metadata_patterns.items():
                import re
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    metadata[field_name] = match.group(1).strip()
            
            return metadata
            
        except Exception as e:
            logger.warning(f"Failed to extract pattern metadata from {file_path}: {e}")
            return {}
    
    def _calculate_file_hash(self, file_path: Path, algorithm: str = 'sha256') -> str:
        """Calculate file hash"""
        try:
            hash_func = hashlib.new(algorithm)
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate hash for {file_path}: {e}")
            return ""
    
    def _parse_aasx_manifest(self, manifest_content: str) -> Dict[str, Any]:
        """Parse AASX manifest content"""
        try:
            # Simple parsing for common manifest formats
            metadata = {}
            
            # Look for version information
            if 'version' in manifest_content.lower():
                metadata['aasx_version'] = 'detected'
            
            # Look for AAS-specific elements
            if 'submodel' in manifest_content.lower():
                metadata['has_submodels'] = True
            
            if 'asset' in manifest_content.lower():
                metadata['has_assets'] = True
            
            return metadata
            
        except Exception as e:
            logger.warning(f"Failed to parse AASX manifest: {e}")
            return {}
    
    def _analyze_json_structure(self, data: Any, max_depth: int = 3) -> Dict[str, Any]:
        """Analyze JSON structure recursively"""
        if max_depth <= 0:
            return {'type': 'max_depth_reached'}
        
        if isinstance(data, dict):
            return {
                'type': 'object',
                'key_count': len(data),
                'keys': list(data.keys())[:10],  # First 10 keys
                'nested_structures': {
                    k: self._analyze_json_structure(v, max_depth - 1) 
                    for k, v in list(data.items())[:5]  # First 5 items
                }
            }
        elif isinstance(data, list):
            return {
                'type': 'array',
                'length': len(data),
                'item_types': list(set(type(item).__name__ for item in data[:10])),
                'sample_items': [
                    self._analyze_json_structure(item, max_depth - 1) 
                    for item in data[:3]  # First 3 items
                ]
            }
        else:
            return {
                'type': type(data).__name__,
                'value': str(data)[:100]  # First 100 characters
            }
    
    def _get_json_data_types(self, data: Any) -> Dict[str, int]:
        """Get count of different data types in JSON"""
        type_counts = {}
        
        def count_types(obj):
            if isinstance(obj, dict):
                type_counts['object'] = type_counts.get('object', 0) + 1
                for value in obj.values():
                    count_types(value)
            elif isinstance(obj, list):
                type_counts['array'] = type_counts.get('array', 0) + 1
                for item in obj:
                    count_types(item)
            else:
                obj_type = type(obj).__name__
                type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
        
        count_types(data)
        return type_counts
    
    def _extract_json_common_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract common metadata fields from JSON"""
        common_fields = {}
        
        # Common metadata keys
        metadata_keys = ['version', 'author', 'description', 'created', 'modified', 'license', 'keywords', 'tags']
        
        for key in metadata_keys:
            if key in data:
                common_fields[key] = data[key]
        
        return common_fields
    
    def _extract_xml_namespaces(self, root: ET.Element) -> Dict[str, str]:
        """Extract XML namespaces"""
        namespaces = {}
        
        # Get namespaces from root element
        for prefix, uri in root.nsmap.items() if hasattr(root, 'nsmap') else []:
            namespaces[prefix or 'default'] = uri
        
        # Also check for xmlns attributes
        for attr, value in root.attrib.items():
            if attr.startswith('xmlns'):
                prefix = attr.replace('xmlns:', '') if ':' in attr else 'default'
                namespaces[prefix] = value
        
        return namespaces
    
    def _calculate_xml_depth(self, element: ET.Element, current_depth: int = 0) -> int:
        """Calculate maximum depth of XML tree"""
        if not element:
            return current_depth
        
        max_depth = current_depth
        for child in element:
            child_depth = self._calculate_xml_depth(child, current_depth + 1)
            max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def _extract_xml_common_fields(self, root: ET.Element) -> Dict[str, Any]:
        """Extract common metadata fields from XML"""
        common_fields = {}
        
        # Look for common metadata elements
        metadata_elements = ['version', 'author', 'description', 'created', 'modified', 'license']
        
        for element_name in metadata_elements:
            element = root.find(f'.//{element_name}')
            if element is not None and element.text:
                common_fields[element_name] = element.text.strip()
        
        return common_fields
    
    def _analyze_yaml_structure(self, data: Any) -> Dict[str, Any]:
        """Analyze YAML structure (similar to JSON)"""
        return self._analyze_json_structure(data)
    
    def _get_yaml_data_types(self, data: Any) -> Dict[str, int]:
        """Get count of different data types in YAML"""
        return self._get_json_data_types(data)
    
    def _extract_yaml_common_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract common metadata fields from YAML"""
        return self._extract_json_common_fields(data)
    
    def _detect_text_format(self, content: str) -> str:
        """Detect text file format"""
        content_lower = content.lower()
        
        if '<?xml' in content_lower:
            return 'xml'
        elif content_lower.startswith('{') or content_lower.startswith('['):
            return 'json'
        elif '---' in content_lower[:100] and ':' in content_lower[:200]:
            return 'yaml'
        elif ',' in content_lower and '\n' in content_lower:
            return 'csv'
        else:
            return 'plain_text'
    
    def _create_error_metadata(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create metadata for error cases"""
        return {
            'error': str(error),
            'error_type': type(error).__name__,
            'context': context or {},
            'extraction_timestamp': datetime.now(timezone.utc).isoformat(),
            'extraction_method': 'error_fallback'
        }
    
    async def extract_database_metadata(self, db_path: Union[str, Path], table_name: str) -> Dict[str, Any]:
        """Extract metadata from database table"""
        try:
            db_path = Path(db_path)
            if not db_path.exists():
                raise FileNotFoundError(f"Database not found: {db_path}")
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            # Get sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            sample_data = cursor.fetchall()
            
            metadata = {
                'source_type': 'database',
                'database_path': str(db_path),
                'table_name': table_name,
                'column_count': len(columns),
                'row_count': row_count,
                'columns': [
                    {
                        'name': col[1],
                        'type': col[2],
                        'not_null': bool(col[3]),
                        'default_value': col[4],
                        'primary_key': bool(col[5])
                    }
                    for col in columns
                ],
                'sample_data': sample_data,
                'extraction_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            conn.close()
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to extract database metadata from {db_path}.{table_name}: {e}")
            return self._create_error_metadata(e, {
                'db_path': str(db_path),
                'table_name': table_name
            })
    
    async def extract_etl_metadata(self, etl_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from ETL processing data"""
        try:
            metadata = {
                'source_type': 'etl',
                'etl_version': etl_data.get('version', 'unknown'),
                'processing_timestamp': etl_data.get('timestamp'),
                'input_files': etl_data.get('input_files', []),
                'output_files': etl_data.get('output_files', []),
                'processing_status': etl_data.get('status', 'unknown'),
                'error_count': etl_data.get('error_count', 0),
                'warning_count': etl_data.get('warning_count', 0),
                'processing_time': etl_data.get('processing_time'),
                'data_quality_score': etl_data.get('quality_score'),
                'extraction_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Extract file information
            if 'input_files' in etl_data:
                metadata['input_file_count'] = len(etl_data['input_files'])
                metadata['input_file_types'] = list(set(
                    Path(f).suffix.lower() for f in etl_data['input_files']
                ))
            
            if 'output_files' in etl_data:
                metadata['output_file_count'] = len(etl_data['output_files'])
                metadata['output_file_types'] = list(set(
                    Path(f).suffix.lower() for f in etl_data['output_files']
                ))
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to extract ETL metadata: {e}")
            return self._create_error_metadata(e, {'etl_data': str(etl_data)})
    
    def get_extraction_summary(self) -> Dict[str, Any]:
        """Get summary of metadata extraction capabilities"""
        return {
            'supported_file_types': list(self.supported_file_types.keys()),
            'metadata_patterns': list(self.metadata_patterns.keys()),
            'extraction_methods': ['file', 'database', 'etl', 'pattern'],
            'version': '1.0.0',
            'description': 'Metadata extraction utilities for twin registry population'
        }
