"""
Validation Utilities
==================

Common validation functions for the AAS Data Modeling framework.
"""

import re
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ValidationUtils:
    """Utility class for data validation."""
    
    # Common regex patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
    ALPHANUMERIC_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_\.]+$')
    FILENAME_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_\.]+$')
    
    # Validation limits
    MAX_NAME_LENGTH = 255
    MAX_DESCRIPTION_LENGTH = 1000
    MAX_TAG_LENGTH = 50
    MAX_TAGS_COUNT = 10
    MIN_NAME_LENGTH = 1
    
    @staticmethod
    def is_valid_uuid(uuid_string: str) -> bool:
        """Validate if string is a valid UUID."""
        try:
            uuid.UUID(uuid_string)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email format."""
        if not email or not isinstance(email, str):
            return False
        return bool(ValidationUtils.EMAIL_PATTERN.match(email))
    
    @staticmethod
    def is_valid_name(name: str) -> Tuple[bool, List[str]]:
        """Validate name field."""
        errors = []
        
        if not name or not isinstance(name, str):
            errors.append("Name is required and must be a string")
            return False, errors
        
        name = name.strip()
        
        if len(name) < ValidationUtils.MIN_NAME_LENGTH:
            errors.append(f"Name must be at least {ValidationUtils.MIN_NAME_LENGTH} character long")
        
        if len(name) > ValidationUtils.MAX_NAME_LENGTH:
            errors.append(f"Name must be less than {ValidationUtils.MAX_NAME_LENGTH} characters")
        
        if not ValidationUtils.ALPHANUMERIC_PATTERN.match(name):
            errors.append("Name contains invalid characters. Only letters, numbers, spaces, hyphens, underscores, and dots are allowed")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def is_valid_description(description: str) -> Tuple[bool, List[str]]:
        """Validate description field."""
        errors = []
        
        if description is None:
            return True, errors  # Description is optional
        
        if not isinstance(description, str):
            errors.append("Description must be a string")
            return False, errors
        
        if len(description) > ValidationUtils.MAX_DESCRIPTION_LENGTH:
            errors.append(f"Description must be less than {ValidationUtils.MAX_DESCRIPTION_LENGTH} characters")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def is_valid_tags(tags: List[str]) -> Tuple[bool, List[str]]:
        """Validate tags list."""
        errors = []
        
        if not isinstance(tags, list):
            errors.append("Tags must be a list")
            return False, errors
        
        if len(tags) > ValidationUtils.MAX_TAGS_COUNT:
            errors.append(f"Maximum {ValidationUtils.MAX_TAGS_COUNT} tags allowed")
        
        for i, tag in enumerate(tags):
            if not isinstance(tag, str):
                errors.append(f"Tag at index {i} must be a string")
                continue
            
            tag = tag.strip()
            if len(tag) == 0:
                errors.append(f"Tag at index {i} cannot be empty")
                continue
            
            if len(tag) > ValidationUtils.MAX_TAG_LENGTH:
                errors.append(f"Tag at index {i} must be less than {ValidationUtils.MAX_TAG_LENGTH} characters")
            
            if not ValidationUtils.ALPHANUMERIC_PATTERN.match(tag):
                errors.append(f"Tag at index {i} contains invalid characters")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def is_valid_filename(filename: str) -> Tuple[bool, List[str]]:
        """Validate filename."""
        errors = []
        
        if not filename or not isinstance(filename, str):
            errors.append("Filename is required and must be a string")
            return False, errors
        
        filename = filename.strip()
        
        if len(filename) == 0:
            errors.append("Filename cannot be empty")
        
        if len(filename) > 255:
            errors.append("Filename must be less than 255 characters")
        
        # Check for invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            if char in filename:
                errors.append(f"Filename contains invalid character: '{char}'")
                break
        
        # Check for reserved names (Windows)
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL'] + [f'COM{i}' for i in range(1, 10)] + [f'LPT{i}' for i in range(1, 10)]
        if filename.upper() in reserved_names:
            errors.append("Filename is a reserved system name")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def is_valid_filepath(filepath: str) -> Tuple[bool, List[str]]:
        """Validate filepath."""
        errors = []
        
        if not filepath or not isinstance(filepath, str):
            errors.append("Filepath is required and must be a string")
            return False, errors
        
        filepath = filepath.strip()
        
        if len(filepath) == 0:
            errors.append("Filepath cannot be empty")
        
        # Check for path traversal attempts
        if '..' in filepath or filepath.startswith('/') or ':' in filepath:
            errors.append("Filepath contains invalid path components")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def is_valid_integer(value: Any, min_value: Optional[int] = None, max_value: Optional[int] = None) -> Tuple[bool, List[str]]:
        """Validate integer value."""
        errors = []
        
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            errors.append("Value must be a valid integer")
            return False, errors
        
        if min_value is not None and int_value < min_value:
            errors.append(f"Value must be at least {min_value}")
        
        if max_value is not None and int_value > max_value:
            errors.append(f"Value must be at most {max_value}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def is_valid_float(value: Any, min_value: Optional[float] = None, max_value: Optional[float] = None) -> Tuple[bool, List[str]]:
        """Validate float value."""
        errors = []
        
        try:
            float_value = float(value)
        except (ValueError, TypeError):
            errors.append("Value must be a valid number")
            return False, errors
        
        if min_value is not None and float_value < min_value:
            errors.append(f"Value must be at least {min_value}")
        
        if max_value is not None and float_value > max_value:
            errors.append(f"Value must be at most {max_value}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def is_valid_boolean(value: Any) -> Tuple[bool, List[str]]:
        """Validate boolean value."""
        errors = []
        
        if isinstance(value, bool):
            return True, errors
        
        if isinstance(value, str):
            if value.lower() in ['true', 'false', '1', '0', 'yes', 'no']:
                return True, errors
        
        if isinstance(value, int) and value in [0, 1]:
            return True, errors
        
        errors.append("Value must be a valid boolean")
        return False, errors
    
    @staticmethod
    def is_valid_datetime(value: Any) -> Tuple[bool, List[str]]:
        """Validate datetime value."""
        errors = []
        
        if isinstance(value, datetime):
            return True, errors
        
        if isinstance(value, str):
            try:
                datetime.fromisoformat(value.replace('Z', '+00:00'))
                return True, errors
            except ValueError:
                pass
        
        errors.append("Value must be a valid datetime")
        return False, errors
    
    @staticmethod
    def is_valid_json_string(value: str) -> Tuple[bool, List[str]]:
        """Validate JSON string."""
        errors = []
        
        if not isinstance(value, str):
            errors.append("Value must be a string")
            return False, errors
        
        try:
            import json
            json.loads(value)
            return True, errors
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON format: {str(e)}")
            return False, errors
    
    @staticmethod
    def is_valid_dict(value: Any, required_keys: Optional[List[str]] = None, optional_keys: Optional[List[str]] = None) -> Tuple[bool, List[str]]:
        """Validate dictionary structure."""
        errors = []
        
        if not isinstance(value, dict):
            errors.append("Value must be a dictionary")
            return False, errors
        
        if required_keys:
            for key in required_keys:
                if key not in value:
                    errors.append(f"Required key '{key}' is missing")
        
        if optional_keys:
            for key in value.keys():
                if key not in (required_keys or []) and key not in optional_keys:
                    errors.append(f"Unexpected key '{key}' found")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
        """Sanitize string input."""
        if not isinstance(value, str):
            return ""
        
        # Remove leading/trailing whitespace
        sanitized = value.strip()
        
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        
        # Limit length if specified
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for filesystem compatibility."""
        if not isinstance(filename, str):
            return ""
        
        # Remove leading/trailing spaces and dots
        sanitized = filename.strip('. ')
        
        # Replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            sanitized = sanitized.replace(char, '_')
        
        # Limit length
        if len(sanitized) > 255:
            sanitized = sanitized[:255]
        
        return sanitized
    
    @staticmethod
    def validate_use_case_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate use case data."""
        errors = []
        
        # Validate name
        if 'name' in data:
            is_valid, name_errors = ValidationUtils.is_valid_name(data['name'])
            if not is_valid:
                errors.extend(name_errors)
        else:
            errors.append("Name is required")
        
        # Validate description
        if 'description' in data:
            is_valid, desc_errors = ValidationUtils.is_valid_description(data['description'])
            if not is_valid:
                errors.extend(desc_errors)
        
        # Validate category
        if 'category' in data:
            if not isinstance(data['category'], str) or len(data['category'].strip()) == 0:
                errors.append("Category must be a non-empty string")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_project_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate project data."""
        errors = []
        
        # Validate name
        if 'name' in data:
            is_valid, name_errors = ValidationUtils.is_valid_name(data['name'])
            if not is_valid:
                errors.extend(name_errors)
        else:
            errors.append("Name is required")
        
        # Validate description
        if 'description' in data:
            is_valid, desc_errors = ValidationUtils.is_valid_description(data['description'])
            if not is_valid:
                errors.extend(desc_errors)
        
        # Validate tags
        if 'tags' in data:
            is_valid, tag_errors = ValidationUtils.is_valid_tags(data['tags'])
            if not is_valid:
                errors.extend(tag_errors)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_file_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate file data."""
        errors = []
        
        # Validate filename
        if 'filename' in data:
            is_valid, filename_errors = ValidationUtils.is_valid_filename(data['filename'])
            if not is_valid:
                errors.extend(filename_errors)
        else:
            errors.append("Filename is required")
        
        # Validate filepath
        if 'filepath' in data:
            is_valid, filepath_errors = ValidationUtils.is_valid_filepath(data['filepath'])
            if not is_valid:
                errors.extend(filepath_errors)
        
        # Validate size
        if 'size' in data:
            is_valid, size_errors = ValidationUtils.is_valid_integer(data['size'], min_value=0)
            if not is_valid:
                errors.extend(size_errors)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_digital_twin_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate digital twin data."""
        errors = []
        
        # Validate twin_name
        if 'twin_name' in data:
            is_valid, name_errors = ValidationUtils.is_valid_name(data['twin_name'])
            if not is_valid:
                errors.extend(name_errors)
        else:
            errors.append("Twin name is required")
        
        # Validate status
        if 'status' in data:
            valid_statuses = ['created', 'processing', 'active', 'inactive', 'error', 'orphaned']
            if data['status'] not in valid_statuses:
                errors.append(f"Status must be one of: {valid_statuses}")
        
        return len(errors) == 0, errors 