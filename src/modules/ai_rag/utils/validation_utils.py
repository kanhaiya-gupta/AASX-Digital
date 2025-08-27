"""
Validation utilities for AI RAG module
Provides common validation and verification functions
"""

import re
import uuid
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def validate_project_id(project_id: str) -> bool:
    """
    Validate if a project ID is in the correct format.
    
    Args:
        project_id: Project ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not project_id or not isinstance(project_id, str):
        return False
    
    # Project ID should be alphanumeric with optional underscores and hyphens
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, project_id))


def validate_file_info(file_info: Dict[str, Any]) -> bool:
    """
    Validate file information dictionary.
    
    Args:
        file_info: File information dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(file_info, dict):
        return False
    
    required_fields = ['filename', 'file_path']
    for field in required_fields:
        if field not in file_info:
            logger.warning(f"Missing required field in file_info: {field}")
            return False
    
    # Validate filename
    if not file_info['filename'] or not isinstance(file_info['filename'], str):
        return False
    
    # Validate file_path
    file_path = file_info.get('file_path')
    if file_path and not isinstance(file_path, (str, Path)):
        return False
    
    return True


def validate_processing_config(config: Dict[str, Any]) -> bool:
    """
    Validate processing configuration dictionary.
    
    Args:
        config: Processing configuration to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(config, dict):
        return False
    
    # Check for required fields
    required_fields = ['extract_entities', 'build_graph']
    for field in required_fields:
        if field not in config:
            logger.warning(f"Missing required field in processing_config: {field}")
            return False
    
    # Validate boolean fields
    boolean_fields = ['extract_entities', 'build_graph']
    for field in boolean_fields:
        if not isinstance(config[field], bool):
            logger.warning(f"Field {field} must be boolean")
            return False
    
    # Validate optional fields
    optional_fields = {
        'chunk_size': int,
        'overlap': int,
        'max_entities': int,
        'quality_threshold': (int, float)
    }
    
    for field, expected_type in optional_fields.items():
        if field in config:
            if not isinstance(config[field], expected_type):
                logger.warning(f"Field {field} must be of type {expected_type}")
                return False
    
    return True


def validate_graph_metadata(metadata: Dict[str, Any]) -> bool:
    """
    Validate graph metadata dictionary.
    
    Args:
        metadata: Graph metadata to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(metadata, dict):
        return False
    
    required_fields = ['graph_id', 'project_id', 'graph_type']
    for field in required_fields:
        if field not in metadata:
            logger.warning(f"Missing required field in graph_metadata: {field}")
            return False
    
    # Validate graph_id
    if not metadata['graph_id'] or not isinstance(metadata['graph_id'], str):
        return False
    
    # Validate project_id
    if not validate_project_id(metadata['project_id']):
        return False
    
    # Validate graph_type
    valid_graph_types = ['document', 'entity', 'relationship', 'concept', 'hybrid']
    if metadata['graph_type'] not in valid_graph_types:
        logger.warning(f"Invalid graph_type: {metadata['graph_type']}")
        return False
    
    return True


def validate_uuid(uuid_string: str) -> bool:
    """
    Validate if a string is a valid UUID.
    
    Args:
        uuid_string: String to validate as UUID
        
    Returns:
        True if valid UUID, False otherwise
    """
    try:
        uuid.UUID(uuid_string)
        return True
    except (ValueError, TypeError):
        return False


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email format, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid URL format, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
    return bool(re.match(pattern, url))


def validate_file_path(file_path: Union[str, Path]) -> bool:
    """
    Validate if a file path is valid and accessible.
    
    Args:
        file_path: File path to validate
        
    Returns:
        True if valid and accessible, False otherwise
    """
    try:
        path = Path(file_path)
        return path.exists() and path.is_file()
    except Exception:
        return False


def validate_directory_path(directory_path: Union[str, Path]) -> bool:
    """
    Validate if a directory path is valid and accessible.
    
    Args:
        directory_path: Directory path to validate
        
    Returns:
        True if valid and accessible, False otherwise
    """
    try:
        path = Path(directory_path)
        return path.exists() and path.is_dir()
    except Exception:
        return False


def validate_config_schema(config: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """
    Validate configuration against a schema definition.
    
    Args:
        config: Configuration to validate
        schema: Schema definition
        
    Returns:
        True if valid according to schema, False otherwise
    """
    if not isinstance(config, dict) or not isinstance(schema, dict):
        return False
    
    for field, field_schema in schema.items():
        if field not in config:
            if field_schema.get('required', False):
                logger.warning(f"Missing required field: {field}")
                return False
            continue
        
        value = config[field]
        expected_type = field_schema.get('type')
        
        if expected_type and not isinstance(value, expected_type):
            logger.warning(f"Field {field} must be of type {expected_type}")
            return False
        
        # Validate nested objects
        if field_schema.get('nested') and isinstance(value, dict):
            if not validate_config_schema(value, field_schema['nested']):
                return False
        
        # Validate enums
        if 'enum' in field_schema and value not in field_schema['enum']:
            logger.warning(f"Field {field} must be one of {field_schema['enum']}")
            return False
    
    return True


def sanitize_input(input_string: str, max_length: int = 1000) -> str:
    """
    Sanitize input string by removing potentially dangerous characters.
    
    Args:
        input_string: Input string to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not input_string:
        return ""
    
    # Remove null bytes and control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f]', '', input_string)
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()


def validate_json_structure(data: Any, expected_structure: Dict[str, Any]) -> bool:
    """
    Validate JSON-like data structure against expected schema.
    
    Args:
        data: Data to validate
        expected_structure: Expected structure definition
        
    Returns:
        True if structure matches, False otherwise
    """
    def _validate_value(value: Any, schema: Any) -> bool:
        if schema == "any":
            return True
        elif schema == "string":
            return isinstance(value, str)
        elif schema == "number":
            return isinstance(value, (int, float))
        elif schema == "boolean":
            return isinstance(value, bool)
        elif schema == "array":
            return isinstance(value, list)
        elif schema == "object":
            return isinstance(value, dict)
        elif isinstance(schema, dict):
            if not isinstance(value, dict):
                return False
            for key, key_schema in schema.items():
                if key not in value:
                    if key_schema.get("required", False):
                        return False
                    continue
                if not _validate_value(value[key], key_schema):
                    return False
            return True
        elif isinstance(schema, list):
            return isinstance(value, list) and all(_validate_value(item, schema[0]) for item in value)
        else:
            return value == schema
    
    return _validate_value(data, expected_structure)


