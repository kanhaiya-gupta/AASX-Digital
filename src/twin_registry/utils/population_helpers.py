"""
Population Helpers for Twin Registry
Provides helper functions for the population system
"""

import logging
import re
import hashlib
from typing import Dict, Any, Optional, List, Union, Tuple
from pathlib import Path
from datetime import datetime, timezone
import json

logger = logging.getLogger(__name__)


class PopulationHelpers:
    """Helper functions for twin registry population"""
    
    @staticmethod
    def generate_twin_name(
        base_name: str,
        registry_type: str,
        workflow_source: str,
        suffix: Optional[str] = None
    ) -> str:
        """Generate a standardized twin name"""
        try:
            # Clean base name
            clean_base = re.sub(r'[^a-zA-Z0-9_\-\s]', '', base_name).strip()
            clean_base = re.sub(r'\s+', '_', clean_base)
            
            # Create standardized name
            name_parts = [clean_base, registry_type, workflow_source]
            if suffix:
                name_parts.append(suffix)
            
            twin_name = "_".join(name_parts).lower()
            
            # Ensure reasonable length
            if len(twin_name) > 100:
                twin_name = twin_name[:97] + "..."
            
            return twin_name
            
        except Exception as e:
            logger.error(f"Failed to generate twin name: {e}")
            return f"twin_{int(datetime.now(timezone.utc).timestamp())}"
    
    @staticmethod
    def extract_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
        """Extract information from file path"""
        try:
            file_path = Path(file_path)
            
            # Basic file info
            file_info = {
                "filename": file_path.name,
                "extension": file_path.suffix.lower(),
                "size": file_path.stat().st_size if file_path.exists() else 0,
                "path": str(file_path.absolute()),
                "parent_dir": str(file_path.parent),
                "exists": file_path.exists()
            }
            
            # File type detection
            if file_path.suffix.lower() in ['.aasx', '.aas']:
                file_info["file_type"] = "aasx"
                file_info["content_type"] = "application/octet-stream"
            elif file_path.suffix.lower() in ['.xml']:
                file_info["file_type"] = "xml"
                file_info["content_type"] = "application/xml"
            elif file_path.suffix.lower() in ['.json']:
                file_info["file_type"] = "json"
                file_info["content_type"] = "application/json"
            elif file_path.suffix.lower() in ['.csv']:
                file_info["file_type"] = "csv"
                file_info["content_type"] = "text/csv"
            else:
                file_info["file_type"] = "unknown"
                file_info["content_type"] = "application/octet-stream"
            
            # Timestamps
            if file_path.exists():
                stat = file_path.stat()
                file_info["created_time"] = datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat()
                file_info["modified_time"] = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
                file_info["accessed_time"] = datetime.fromtimestamp(stat.st_atime, tz=timezone.utc).isoformat()
            
            # File hash
            if file_path.exists() and file_path.stat().st_size < 100 * 1024 * 1024:  # 100MB limit
                file_info["file_hash"] = PopulationHelpers._calculate_file_hash(file_path)
            
            return file_info
            
        except Exception as e:
            logger.error(f"Failed to extract file info: {e}")
            return {
                "filename": str(file_path),
                "extension": "",
                "size": 0,
                "path": str(file_path),
                "file_type": "unknown",
                "content_type": "application/octet-stream",
                "exists": False
            }
    
    @staticmethod
    def _calculate_file_hash(file_path: Path) -> str:
        """Calculate SHA-256 hash of file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate file hash: {e}")
            return ""
    
    @staticmethod
    def determine_twin_category(
        file_info: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Determine twin category based on file info and metadata"""
        try:
            # Check metadata first
            if metadata:
                if "category" in metadata:
                    return metadata["category"]
                if "domain" in metadata:
                    return metadata["domain"]
                if "industry" in metadata:
                    return metadata["industry"]
            
            # Check file content hints
            if file_info.get("file_type") == "aasx":
                # AASX files are typically manufacturing/industrial
                return "manufacturing"
            elif file_info.get("file_type") == "xml":
                # XML could be various domains
                return "other"
            elif file_info.get("file_type") == "json":
                # JSON could be various domains
                return "other"
            elif file_info.get("file_type") == "csv":
                # CSV could be various domains
                return "other"
            
            # Default category
            return "other"
            
        except Exception as e:
            logger.error(f"Failed to determine twin category: {e}")
            return "other"
    
    @staticmethod
    def determine_twin_type(
        file_info: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Determine twin type based on file info and metadata"""
        try:
            # Check metadata first
            if metadata:
                if "twin_type" in metadata:
                    return metadata["twin_type"]
                if "type" in metadata:
                    return metadata["type"]
            
            # Check file content hints
            if file_info.get("file_type") == "aasx":
                # AASX files typically represent physical assets
                return "physical_asset"
            elif file_info.get("file_type") == "xml":
                # XML could be various types
                return "data_model"
            elif file_info.get("file_type") == "json":
                # JSON typically represents data models
                return "data_model"
            elif file_info.get("file_type") == "csv":
                # CSV typically represents data
                return "data_model"
            
            # Default type
            return "unknown"
            
        except Exception as e:
            logger.error(f"Failed to determine twin type: {e}")
            return "unknown"
    
    @staticmethod
    def create_basic_metadata(
        file_info: Dict[str, Any],
        user_id: str,
        org_id: str,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create basic metadata for twin registry entry"""
        try:
            metadata = {
                "file_info": file_info,
                "upload_details": {
                    "upload_time": datetime.now(timezone.utc).isoformat(),
                    "user_id": user_id,
                    "org_id": org_id
                },
                "processing_status": "pending",
                "metadata_version": "1.0"
            }
            
            # Add additional metadata if provided
            if additional_metadata:
                metadata.update(additional_metadata)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to create basic metadata: {e}")
            return {
                "error": str(e),
                "upload_time": datetime.now(timezone.utc).isoformat()
            }
    
    @staticmethod
    def create_basic_config(
        registry_type: str,
        workflow_source: str,
        validation_level: str = "basic"
    ) -> Dict[str, Any]:
        """Create basic configuration for twin registry entry"""
        try:
            config = {
                "auto_population": True,
                "validation_level": validation_level,
                "quality_checks": False,
                "registry_type": registry_type,
                "workflow_source": workflow_source,
                "config_version": "1.0"
            }
            
            return config
            
        except Exception as e:
            logger.error(f"Failed to create basic config: {e}")
            return {
                "error": str(e),
                "auto_population": False
            }
    
    @staticmethod
    def create_basic_tags(
        file_info: Dict[str, Any],
        registry_type: str,
        workflow_source: str
    ) -> List[str]:
        """Create basic tags for twin registry entry"""
        try:
            tags = []
            
            # Add file type tag
            if file_info.get("file_type"):
                tags.append(f"file_type:{file_info['file_type']}")
            
            # Add registry type tag
            tags.append(f"registry_type:{registry_type}")
            
            # Add workflow source tag
            tags.append(f"workflow_source:{workflow_source}")
            
            # Add upload tag
            tags.append("upload")
            
            # Add pending processing tag
            tags.append("pending_processing")
            
            # Ensure unique tags
            tags = list(set(tags))
            
            # Limit tag length
            tags = [tag[:50] for tag in tags]
            
            return tags
            
        except Exception as e:
            logger.error(f"Failed to create basic tags: {e}")
            return ["error", "pending_processing"]
    
    @staticmethod
    def validate_required_fields(
        data: Dict[str, Any],
        required_fields: List[str]
    ) -> Tuple[bool, List[str]]:
        """Validate that required fields are present"""
        try:
            missing_fields = []
            
            for field in required_fields:
                if field not in data or data[field] is None:
                    missing_fields.append(field)
            
            return len(missing_fields) == 0, missing_fields
            
        except Exception as e:
            logger.error(f"Failed to validate required fields: {e}")
            return False, ["validation_error"]
    
    @staticmethod
    def sanitize_string_field(
        value: Any,
        max_length: int = 255,
        allow_empty: bool = False
    ) -> Optional[str]:
        """Sanitize string field value"""
        try:
            if value is None:
                return None if allow_empty else ""
            
            # Convert to string
            string_value = str(value).strip()
            
            # Check if empty
            if not string_value and not allow_empty:
                return ""
            
            # Truncate if too long
            if len(string_value) > max_length:
                string_value = string_value[:max_length-3] + "..."
            
            return string_value
            
        except Exception as e:
            logger.error(f"Failed to sanitize string field: {e}")
            return "" if allow_empty else None
    
    @staticmethod
    def sanitize_json_field(
        value: Any,
        max_size: int = 10000
    ) -> Optional[Dict[str, Any]]:
        """Sanitize JSON field value"""
        try:
            if value is None:
                return {}
            
            # Convert to dict if it's a string
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    return {}
            
            # Ensure it's a dict
            if not isinstance(value, dict):
                return {}
            
            # Check size
            json_str = json.dumps(value)
            if len(json_str) > max_size:
                # Truncate large JSON
                truncated = {"truncated": True, "original_size": len(json_str)}
                return truncated
            
            return value
            
        except Exception as e:
            logger.error(f"Failed to sanitize JSON field: {e}")
            return {}
    
    @staticmethod
    def sanitize_array_field(
        value: Any,
        max_count: int = 100,
        max_item_length: int = 100
    ) -> List[str]:
        """Sanitize array field value"""
        try:
            if value is None:
                return []
            
            # Convert to list if it's a string
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    value = [value]
            
            # Ensure it's a list
            if not isinstance(value, (list, tuple)):
                value = [value]
            
            # Convert items to strings and sanitize
            sanitized_items = []
            for item in value[:max_count]:
                item_str = str(item).strip()
                if item_str:
                    # Truncate long items
                    if len(item_str) > max_item_length:
                        item_str = item_str[:max_item_length-3] + "..."
                    sanitized_items.append(item_str)
            
            return sanitized_items
            
        except Exception as e:
            logger.error(f"Failed to sanitize array field: {e}")
            return []
    
    @staticmethod
    def calculate_data_quality_score(
        data: Dict[str, Any],
        required_fields: List[str],
        optional_fields: List[str]
    ) -> float:
        """Calculate data quality score"""
        try:
            total_fields = len(required_fields) + len(optional_fields)
            if total_fields == 0:
                return 0.0
            
            score = 0.0
            
            # Check required fields
            for field in required_fields:
                if field in data and data[field] is not None:
                    score += 1.0
            
            # Check optional fields
            for field in optional_fields:
                if field in data and data[field] is not None:
                    score += 0.5
            
            # Calculate percentage
            quality_score = score / total_fields
            
            return min(1.0, max(0.0, quality_score))
            
        except Exception as e:
            logger.error(f"Failed to calculate data quality score: {e}")
            return 0.0
    
    @staticmethod
    def generate_correlation_id(
        source: str,
        identifier: str,
        timestamp: Optional[datetime] = None
    ) -> str:
        """Generate correlation ID for tracking"""
        try:
            if timestamp is None:
                timestamp = datetime.now(timezone.utc)
            
            # Create unique string
            unique_string = f"{source}_{identifier}_{timestamp.isoformat()}"
            
            # Generate hash
            correlation_id = hashlib.md5(unique_string.encode()).hexdigest()
            
            return correlation_id
            
        except Exception as e:
            logger.error(f"Failed to generate correlation ID: {e}")
            return f"corr_{int(datetime.now(timezone.utc).timestamp())}"
    
    @staticmethod
    def format_timestamp(timestamp: Union[datetime, str, None]) -> Optional[str]:
        """Format timestamp consistently"""
        try:
            if timestamp is None:
                return None
            
            if isinstance(timestamp, str):
                # Parse string timestamp
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except ValueError:
                    return None
            elif isinstance(timestamp, datetime):
                dt = timestamp
            else:
                return None
            
            # Ensure timezone info
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            
            # Format consistently
            return dt.isoformat()
            
        except Exception as e:
            logger.error(f"Failed to format timestamp: {e}")
            return None
    
    @staticmethod
    def merge_metadata(
        base_metadata: Dict[str, Any],
        new_metadata: Dict[str, Any],
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """Merge metadata dictionaries"""
        try:
            if not base_metadata:
                return new_metadata.copy()
            
            if not new_metadata:
                return base_metadata.copy()
            
            merged = base_metadata.copy()
            
            for key, value in new_metadata.items():
                if key not in merged or overwrite:
                    merged[key] = value
                elif isinstance(merged[key], dict) and isinstance(value, dict):
                    # Recursively merge nested dictionaries
                    merged[key] = PopulationHelpers.merge_metadata(
                        merged[key], value, overwrite
                    )
                elif isinstance(merged[key], list) and isinstance(value, list):
                    # Merge lists
                    merged[key] = list(set(merged[key] + value))
            
            return merged
            
        except Exception as e:
            logger.error(f"Failed to merge metadata: {e}")
            return base_metadata.copy()
    
    @staticmethod
    def create_error_metadata(
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create error metadata for failed operations"""
        try:
            error_metadata = {
                "error": {
                    "type": type(error).__name__,
                    "message": str(error),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                "status": "error"
            }
            
            if context:
                error_metadata["context"] = context
            
            return error_metadata
            
        except Exception as e:
            logger.error(f"Failed to create error metadata: {e}")
            return {
                "error": "Failed to create error metadata",
                "status": "error"
            }
    
    @staticmethod
    def validate_uuid(uuid_string: str) -> bool:
        """Validate UUID format"""
        try:
            import uuid
            uuid.UUID(uuid_string)
            return True
        except (ValueError, AttributeError):
            return False
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        try:
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(pattern, email))
        except Exception:
            return False
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        try:
            pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
            return bool(re.match(pattern, url))
        except Exception:
            return False
