"""
Data validation utilities for AASX Digital Twin Analytics Framework
"""
import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom validation error"""
    pass


def validate_required_fields(data: Dict, required_fields: List[str]) -> bool:
    """Validate that all required fields are present"""
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    if missing_fields:
        raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
    return True


def validate_string_field(value: Any, field_name: str, min_length: int = 0, max_length: Optional[int] = None) -> str:
    """Validate string field"""
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string")
    
    if len(value) < min_length:
        raise ValidationError(f"{field_name} must be at least {min_length} characters long")
    
    if max_length and len(value) > max_length:
        raise ValidationError(f"{field_name} must be at most {max_length} characters long")
    
    return value.strip()


def validate_email_field(value: Any, field_name: str = "email") -> str:
    """Validate email field"""
    email = validate_string_field(value, field_name)
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError(f"{field_name} must be a valid email address")
    
    return email.lower()


def validate_url_field(value: Any, field_name: str = "url") -> str:
    """Validate URL field"""
    url = validate_string_field(value, field_name)
    
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
    if not re.match(pattern, url):
        raise ValidationError(f"{field_name} must be a valid URL")
    
    return url


def validate_integer_field(value: Any, field_name: str, min_value: Optional[int] = None, max_value: Optional[int] = None) -> int:
    """Validate integer field"""
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be an integer")
    
    if min_value is not None and int_value < min_value:
        raise ValidationError(f"{field_name} must be at least {min_value}")
    
    if max_value is not None and int_value > max_value:
        raise ValidationError(f"{field_name} must be at most {max_value}")
    
    return int_value


def validate_float_field(value: Any, field_name: str, min_value: Optional[float] = None, max_value: Optional[float] = None) -> float:
    """Validate float field"""
    try:
        float_value = float(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a number")
    
    if min_value is not None and float_value < min_value:
        raise ValidationError(f"{field_name} must be at least {min_value}")
    
    if max_value is not None and float_value > max_value:
        raise ValidationError(f"{field_name} must be at most {max_value}")
    
    return float_value


def validate_boolean_field(value: Any, field_name: str) -> bool:
    """Validate boolean field"""
    if isinstance(value, bool):
        return value
    elif isinstance(value, str):
        if value.lower() in ('true', '1', 'yes', 'on'):
            return True
        elif value.lower() in ('false', '0', 'no', 'off'):
            return False
        else:
            raise ValidationError(f"{field_name} must be a boolean value")
    else:
        raise ValidationError(f"{field_name} must be a boolean value")


def validate_list_field(value: Any, field_name: str, min_length: int = 0, max_length: Optional[int] = None) -> List:
    """Validate list field"""
    if not isinstance(value, list):
        raise ValidationError(f"{field_name} must be a list")
    
    if len(value) < min_length:
        raise ValidationError(f"{field_name} must have at least {min_length} items")
    
    if max_length and len(value) > max_length:
        raise ValidationError(f"{field_name} must have at most {max_length} items")
    
    return value


def validate_dict_field(value: Any, field_name: str) -> Dict:
    """Validate dictionary field"""
    if not isinstance(value, dict):
        raise ValidationError(f"{field_name} must be a dictionary")
    return value


def validate_datetime_field(value: Any, field_name: str) -> datetime:
    """Validate datetime field"""
    if isinstance(value, datetime):
        return value
    elif isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            raise ValidationError(f"{field_name} must be a valid ISO datetime string")
    else:
        raise ValidationError(f"{field_name} must be a datetime object or ISO datetime string")


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> str:
    """Validate file extension"""
    if not filename:
        raise ValidationError("Filename cannot be empty")
    
    extension = filename.lower().split('.')[-1] if '.' in filename else ''
    if extension not in allowed_extensions:
        raise ValidationError(f"File extension must be one of: {', '.join(allowed_extensions)}")
    
    return filename


def validate_file_size(file_size: int, max_size: int) -> int:
    """Validate file size"""
    if file_size <= 0:
        raise ValidationError("File size must be positive")
    
    if file_size > max_size:
        raise ValidationError(f"File size must be at most {max_size} bytes")
    
    return file_size


def validate_json_schema(data: Dict, schema: Dict) -> bool:
    """Validate data against JSON schema (simplified)"""
    # This is a simplified JSON schema validator
    # For production, consider using jsonschema library
    
    def validate_schema(data: Any, schema: Dict, path: str = "") -> bool:
        schema_type = schema.get("type")
        
        if schema_type == "object":
            if not isinstance(data, dict):
                raise ValidationError(f"{path} must be an object")
            
            required_fields = schema.get("required", [])
            for field in required_fields:
                if field not in data:
                    raise ValidationError(f"{path}.{field} is required")
            
            properties = schema.get("properties", {})
            for field, value in data.items():
                if field in properties:
                    validate_schema(value, properties[field], f"{path}.{field}")
            
        elif schema_type == "array":
            if not isinstance(data, list):
                raise ValidationError(f"{path} must be an array")
            
            items_schema = schema.get("items")
            if items_schema:
                for i, item in enumerate(data):
                    validate_schema(item, items_schema, f"{path}[{i}]")
            
        elif schema_type == "string":
            if not isinstance(data, str):
                raise ValidationError(f"{path} must be a string")
            
            min_length = schema.get("minLength")
            if min_length and len(data) < min_length:
                raise ValidationError(f"{path} must be at least {min_length} characters")
            
            max_length = schema.get("maxLength")
            if max_length and len(data) > max_length:
                raise ValidationError(f"{path} must be at most {max_length} characters")
            
        elif schema_type == "number":
            if not isinstance(data, (int, float)):
                raise ValidationError(f"{path} must be a number")
            
            minimum = schema.get("minimum")
            if minimum is not None and data < minimum:
                raise ValidationError(f"{path} must be at least {minimum}")
            
            maximum = schema.get("maximum")
            if maximum is not None and data > maximum:
                raise ValidationError(f"{path} must be at most {maximum}")
            
        elif schema_type == "integer":
            if not isinstance(data, int):
                raise ValidationError(f"{path} must be an integer")
            
            minimum = schema.get("minimum")
            if minimum is not None and data < minimum:
                raise ValidationError(f"{path} must be at least {minimum}")
            
            maximum = schema.get("maximum")
            if maximum is not None and data > maximum:
                raise ValidationError(f"{path} must be at most {maximum}")
            
        elif schema_type == "boolean":
            if not isinstance(data, bool):
                raise ValidationError(f"{path} must be a boolean")
        
        return True
    
    try:
        validate_schema(data, schema)
        return True
    except ValidationError as e:
        logger.error(f"JSON schema validation failed: {e}")
        raise


def sanitize_input(data: Union[str, Dict, List]) -> Union[str, Dict, List]:
    """Sanitize input data to prevent injection attacks"""
    if isinstance(data, str):
        # Remove potentially dangerous characters
        return re.sub(r'[<>"\']', '', data)
    elif isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    else:
        return data 