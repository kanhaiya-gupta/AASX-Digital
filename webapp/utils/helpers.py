"""
Helper utility functions for AASX Digital Twin Analytics Framework
"""
import os
import json
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)


def generate_id() -> str:
    """Generate a unique ID"""
    return str(uuid.uuid4())


def generate_hash(data: str) -> str:
    """Generate SHA-256 hash of data"""
    return hashlib.sha256(data.encode()).hexdigest()


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def format_timestamp(timestamp: Union[datetime, str, float]) -> str:
    """Format timestamp to ISO format"""
    if isinstance(timestamp, str):
        return timestamp
    elif isinstance(timestamp, float):
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
    elif isinstance(timestamp, datetime):
        return timestamp.isoformat()
    else:
        return datetime.utcnow().isoformat()


def safe_json_dumps(obj: Any) -> str:
    """Safely serialize object to JSON string"""
    try:
        return json.dumps(obj, default=str, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error serializing object to JSON: {e}")
        return json.dumps({"error": "Serialization failed"}, default=str)


def safe_json_loads(json_str: str) -> Any:
    """Safely deserialize JSON string to object"""
    try:
        return json.loads(json_str)
    except Exception as e:
        logger.error(f"Error deserializing JSON: {e}")
        return None


def ensure_directory(path: str) -> bool:
    """Ensure directory exists, create if it doesn't"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {path}: {e}")
        return False


def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return os.path.splitext(filename)[1].lower()


def is_valid_filename(filename: str) -> bool:
    """Check if filename is valid"""
    if not filename or len(filename) > 255:
        return False
    
    # Check for invalid characters
    invalid_chars = '<>:"/\\|?*'
    return not any(char in filename for char in invalid_chars)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Merge two dictionaries, dict2 takes precedence"""
    result = dict1.copy()
    result.update(dict2)
    return result


def deep_merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """Flatten nested dictionary"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def retry_operation(func, max_retries: int = 3, delay: float = 1.0):
    """Retry operation with exponential backoff"""
    import time
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            logger.warning(f"Operation failed, retrying in {delay}s (attempt {attempt + 1}/{max_retries}): {e}")
            time.sleep(delay)
            delay *= 2


def validate_email(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_url(url: str) -> bool:
    """Validate URL format"""
    import re
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
    return re.match(pattern, url) is not None


def get_environment_info() -> Dict[str, Any]:
    """Get environment information"""
    return {
        "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        "platform": os.sys.platform,
        "working_directory": os.getcwd(),
        "environment_variables": {k: v for k, v in os.environ.items() if not k.lower().startswith(('secret', 'password', 'key'))}
    } 