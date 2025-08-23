"""
JSON Processing Utilities

This module provides comprehensive JSON processing, validation, and management utilities
for certificates and other document types.
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


class JSONSchema(Enum):
    """JSON schema types for different document types"""
    CERTIFICATE = "certificate"
    REPORT = "report"
    CONFIGURATION = "configuration"
    DATA_EXPORT = "data_export"
    API_RESPONSE = "api_response"
    FEED = "feed"
    MANIFEST = "manifest"
    SCHEMA = "schema"
    TRANSFORMATION = "transformation"
    VALIDATION = "validation"


class JSONValidator(Enum):
    """JSON validation types"""
    STRICT = "strict"
    LENIENT = "lenient"
    SCHEMA_BASED = "schema_based"
    CUSTOM = "custom"
    NONE = "none"


@dataclass
class JSONConfig:
    """Configuration for JSON processing"""
    indent: int = 2
    sort_keys: bool = False
    ensure_ascii: bool = False
    separators: Tuple[str, str] = None
    default: Optional[callable] = None
    encoding: str = "UTF-8"
    validate_schema: bool = True
    allow_comments: bool = False
    allow_trailing_commas: bool = False


class JSONProcessor:
    """
    JSON processing and management utility
    
    Handles:
    - JSON generation from various data sources
    - Schema-based validation
    - Custom formatting and styling
    - Batch processing and optimization
    - JSON metadata management
    - Performance optimization
    """
    
    def __init__(self):
        """Initialize the JSON processor utility"""
        self.json_schemas = list(JSONSchema)
        self.json_validators = list(JSONValidator)
        
        # JSON storage and metadata
        self.processed_json: Dict[str, Dict[str, Any]] = {}
        self.json_schemas_config: Dict[str, Dict[str, Any]] = {}
        self.processing_history: List[Dict[str, Any]] = []
        
        # Processing locks and queues
        self.processing_locks: Dict[str, asyncio.Lock] = {}
        self.processing_queue: asyncio.Queue = asyncio.Queue()
        
        # Performance tracking
        self.processing_stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "average_time": 0.0,
            "total_size_bytes": 0
        }
        
        # Initialize default schemas
        self._initialize_default_schemas()
        
        logger.info("JSON Processor utility initialized successfully")
    
    async def process_json(
        self,
        content: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        schema: JSONSchema = JSONSchema.CERTIFICATE,
        validator: JSONValidator = JSONValidator.STRICT,
        config: Optional[JSONConfig] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process JSON content with the specified schema and configuration
        
        Args:
            content: Content to process
            schema: JSON schema to use
            validator: JSON validation type
            config: JSON configuration
            metadata: Additional metadata for the JSON
            
        Returns:
            Dictionary containing JSON information and processed data
        """
        start_time = time.time()
        json_id = f"json_{int(time.time() * 1000)}"
        
        try:
            # Validate input parameters
            await self._validate_processing_params(content, schema, validator, config)
            
            # Prepare content for JSON processing
            prepared_content = await self._prepare_content_for_json(content, schema)
            
            # Apply configuration and validation
            json_config = config or self._get_default_config(schema, validator)
            
            # Process JSON (simulated)
            json_data = await self._process_json_data(prepared_content, json_config, validator)
            
            # Create metadata
            json_metadata = await self._create_json_metadata(
                json_id, content, schema, validator, json_config, metadata
            )
            
            # Store processed JSON
            json_info = {
                "id": json_id,
                "content": prepared_content,
                "schema": schema.value,
                "validator": validator.value,
                "config": json_config.__dict__,
                "metadata": json_metadata,
                "processed_at": time.time(),
                "size_bytes": len(str(json_data)),
                "status": "success"
            }
            
            self.processed_json[json_id] = json_info
            self.processing_history.append(json_info)
            
            # Update statistics
            await self._update_processing_stats(True, time.time() - start_time, len(str(json_data)))
            
            logger.info(f"JSON processed successfully: {json_id}")
            return json_info
            
        except Exception as e:
            await self._update_processing_stats(False, time.time() - start_time, 0)
            logger.error(f"Failed to process JSON: {str(e)}")
            raise
    
    async def process_batch_json(
        self,
        content_list: List[Union[str, Dict[str, Any], List[Dict[str, Any]]]],
        schema: JSONSchema = JSONSchema.CERTIFICATE,
        validator: JSONValidator = JSONValidator.STRICT,
        config: Optional[JSONConfig] = None,
        batch_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Process multiple JSON content items in batch
        
        Args:
            content_list: List of content items to process
            schema: JSON schema to use
            validator: JSON validation type
            config: JSON configuration
            batch_metadata: Additional metadata for the batch
            
        Returns:
            List of processed JSON information
        """
        batch_id = f"batch_{int(time.time() * 1000)}"
        results = []
        
        logger.info(f"Starting batch JSON processing: {batch_id}")
        
        # Create tasks for concurrent processing
        tasks = []
        for i, content in enumerate(content_list):
            task = asyncio.create_task(
                self.process_json(content, schema, validator, config, {
                    "batch_id": batch_id,
                    "batch_index": i,
                    **(batch_metadata or {})
                })
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(batch_results):
            if isinstance(result, Exception):
                logger.error(f"Failed to process JSON {i} in batch {batch_id}: {str(result)}")
                results.append({
                    "id": f"failed_{batch_id}_{i}",
                    "status": "failed",
                    "error": str(result),
                    "batch_id": batch_id,
                    "batch_index": i
                })
            else:
                results.append(result)
        
        logger.info(f"Batch JSON processing completed: {batch_id}, {len(results)} results")
        return results
    
    async def process_json_from_schema(
        self,
        schema_name: str,
        schema_data: Dict[str, Any],
        validator: JSONValidator = JSONValidator.STRICT,
        config: Optional[JSONConfig] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process JSON content using a predefined schema
        
        Args:
            schema_name: Name of the schema to use
            schema_data: Data to populate the schema
            validator: JSON validation type
            config: JSON configuration
            metadata: Additional metadata for the JSON
            
        Returns:
            Dictionary containing JSON information and processed data
        """
        if schema_name not in self.json_schemas_config:
            raise ValueError(f"Schema not found: {schema_name}")
        
        schema_config = self.json_schemas_config[schema_name]
        
        # Merge schema data with provided data
        merged_data = {**schema_config.get("default_data", {}), **schema_data}
        
        # Use schema's default schema type
        schema_type = JSONSchema(schema_config.get("schema_type", "certificate"))
        
        return await self.process_json(
            merged_data, schema_type, validator, config, metadata
        )
    
    async def validate_json(self, json_id: str) -> Dict[str, Any]:
        """
        Validate a processed JSON document
        
        Args:
            json_id: ID of the JSON document to validate
            
        Returns:
            Validation result information
        """
        if json_id not in self.processed_json:
            raise ValueError(f"JSON document not found: {json_id}")
        
        json_info = self.processed_json[json_id]
        
        # Perform validation checks
        validation_result = await self._perform_validation_checks(json_info)
        
        return {
            "json_id": json_id,
            "validation_result": validation_result,
            "validated_at": time.time(),
            "status": "validated"
        }
    
    async def get_json_info(self, json_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a processed JSON document
        
        Args:
            json_id: ID of the JSON document
            
        Returns:
            JSON document information
        """
        if json_id not in self.processed_json:
            raise ValueError(f"JSON document not found: {json_id}")
        
        return self.processed_json[json_id]
    
    async def get_json_history(
        self,
        schema: Optional[JSONSchema] = None,
        validator: Optional[JSONValidator] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get JSON processing history
        
        Args:
            schema: Filter by JSON schema
            validator: Filter by JSON validator
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of JSON history entries
        """
        history = self.processing_history
        
        if schema:
            history = [h for h in history if h.get("schema") == schema.value]
        
        if validator:
            history = [h for h in history if h.get("validator") == validator.value]
        
        # Sort by processing time (newest first)
        history.sort(key=lambda x: x.get("processed_at", 0), reverse=True)
        
        return history[offset:offset + limit]
    
    async def create_json_schema(
        self,
        schema_name: str,
        schema_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a reusable JSON schema
        
        Args:
            schema_name: Name of the schema
            schema_config: Schema configuration
            
        Returns:
            Schema creation result
        """
        if schema_name in self.json_schemas_config:
            raise ValueError(f"Schema already exists: {schema_name}")
        
        self.json_schemas_config[schema_name] = schema_config
        
        return {
            "schema_name": schema_name,
            "config": schema_config,
            "created_at": time.time(),
            "status": "created"
        }
    
    async def get_processing_statistics(self) -> Dict[str, Any]:
        """
        Get JSON processing statistics
        
        Returns:
            Processing statistics
        """
        return self.processing_stats.copy()
    
    async def cleanup_expired_json(self, max_age_hours: int = 24) -> int:
        """
        Clean up expired JSON documents
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
            
        Returns:
            Number of JSON documents cleaned up
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        expired_json = []
        for json_id, json_info in self.processed_json.items():
            if current_time - json_info.get("processed_at", 0) > max_age_seconds:
                expired_json.append(json_id)
        
        # Remove expired JSON documents
        for json_id in expired_json:
            del self.processed_json[json_id]
        
        logger.info(f"Cleaned up {len(expired_json)} expired JSON documents")
        return len(expired_json)
    
    # Private helper methods
    
    def _initialize_default_schemas(self):
        """Initialize default JSON schemas"""
        # Certificate schema
        self.json_schemas_config["certificate"] = {
            "schema_type": "certificate",
            "default_data": {
                "title": "Certificate of Completion",
                "subtitle": "This is to certify that",
                "signature_line": "Authorized Signature",
                "date_format": "YYYY-MM-DD",
                "logo_url": "/static/images/logo.png"
            },
            "structure": ["header", "content", "signature", "footer"],
            "required_fields": ["title", "subtitle", "signature_line"]
        }
        
        # Configuration schema
        self.json_schemas_config["configuration"] = {
            "schema_type": "configuration",
            "default_data": {
                "version": "1.0",
                "environment": "production",
                "debug": False,
                "settings": {}
            },
            "structure": ["version", "environment", "debug", "settings"],
            "required_fields": ["version", "environment"]
        }
        
        # Data export schema
        self.json_schemas_config["data_export"] = {
            "schema_type": "data_export",
            "default_data": {
                "export_date": "YYYY-MM-DD",
                "source": "database",
                "format": "json",
                "data": []
            },
            "structure": ["export_date", "source", "format", "data"],
            "required_fields": ["export_date", "source", "format"]
        }
    
    def _get_default_config(self, schema: JSONSchema, validator: JSONValidator) -> JSONConfig:
        """Get default configuration for schema and validator combination"""
        if schema == JSONSchema.CERTIFICATE:
            return JSONConfig(
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
                validate_schema=True
            )
        elif schema == JSONSchema.CONFIGURATION:
            return JSONConfig(
                indent=4,
                sort_keys=False,
                ensure_ascii=True,
                validate_schema=True
            )
        else:
            return JSONConfig()
    
    async def _validate_processing_params(
        self,
        content: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        schema: JSONSchema,
        validator: JSONValidator,
        config: Optional[JSONConfig]
    ):
        """Validate JSON processing parameters"""
        if not content:
            raise ValueError("Content cannot be empty")
        
        if not isinstance(schema, JSONSchema):
            raise ValueError("Invalid JSON schema")
        
        if not isinstance(validator, JSONValidator):
            raise ValueError("Invalid JSON validator")
        
        if config and not isinstance(config, JSONConfig):
            raise ValueError("Invalid configuration object")
    
    async def _prepare_content_for_json(
        self,
        content: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        schema: JSONSchema
    ) -> Dict[str, Any]:
        """Prepare content for JSON processing based on schema"""
        if isinstance(content, str):
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"text_content": content}
        elif isinstance(content, dict):
            return content
        elif isinstance(content, list):
            return {"list_content": content}
        else:
            return {"raw_content": str(content)}
    
    async def _process_json_data(
        self,
        content: Dict[str, Any],
        config: JSONConfig,
        validator: JSONValidator
    ) -> str:
        """Process JSON data (simulated)"""
        # Simulate JSON processing
        json_data = json.dumps(content, indent=config.indent, sort_keys=config.sort_keys)
        
        # Apply configuration
        if config.ensure_ascii:
            json_data = json_data.encode('ascii', errors='ignore').decode('ascii')
        
        # Apply validation
        if validator != JSONValidator.NONE:
            json_data += f"// Validated with {validator.value}"
        
        return json_data
    
    async def _create_json_metadata(
        self,
        json_id: str,
        content: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        schema: JSONSchema,
        validator: JSONValidator,
        config: JSONConfig,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create metadata for the processed JSON"""
        base_metadata = {
            "generator": "CertificateManager",
            "version": "1.0.0",
            "schema": schema.value,
            "validator": validator.value,
            "config_hash": hash(str(config.__dict__)),
            "content_hash": hash(str(content)),
            "timestamp": time.time()
        }
        
        if metadata:
            base_metadata.update(metadata)
        
        return base_metadata
    
    async def _perform_validation_checks(self, json_info: Dict[str, Any]) -> Dict[str, Any]:
        """Perform validation checks on a JSON document"""
        checks = {
            "content_integrity": True,
            "schema_validity": True,
            "validator_validity": True,
            "config_validity": True,
            "metadata_completeness": True,
            "size_appropriateness": True,
            "json_structure": True,
            "encoding_validity": True
        }
        
        # Check content integrity
        if not json_info.get("content"):
            checks["content_integrity"] = False
        
        # Check schema validity
        if not json_info.get("schema"):
            checks["schema_validity"] = False
        
        # Check validator validity
        if not json_info.get("validator"):
            checks["validator_validity"] = False
        
        # Check config validity
        config = json_info.get("config", {})
        if not config.get("indent"):
            checks["config_validity"] = False
        
        # Check metadata completeness
        metadata = json_info.get("metadata", {})
        required_fields = ["generator", "version", "timestamp"]
        for field in required_fields:
            if field not in metadata:
                checks["metadata_completeness"] = False
                break
        
        # Check size appropriateness
        content_size = len(str(json_info.get("content", "")))
        if content_size > 1000000:  # 1MB limit
            checks["size_appropriateness"] = False
        
        # Check JSON structure
        try:
            json.loads(str(json_info.get("content", "{}")))
            checks["json_structure"] = True
        except json.JSONDecodeError:
            checks["json_structure"] = False
        
        # Check encoding validity
        if "encoding" in str(json_info.get("content", "")):
            checks["encoding_validity"] = True
        else:
            checks["encoding_validity"] = False
        
        return checks
    
    async def _update_processing_stats(self, success: bool, processing_time: float, size_bytes: int):
        """Update processing statistics"""
        self.processing_stats["total_processed"] += 1
        
        if success:
            self.processing_stats["successful"] += 1
            self.processing_stats["total_size_bytes"] += size_bytes
        else:
            self.processing_stats["failed"] += 1
        
        # Update average processing time
        total_successful = self.processing_stats["successful"]
        if total_successful > 0:
            current_avg = self.processing_stats["average_time"]
            self.processing_stats["average_time"] = (
                (current_avg * (total_successful - 1) + processing_time) / total_successful
            )
