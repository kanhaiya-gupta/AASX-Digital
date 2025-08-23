"""
Base Exporter Interface for Certificate Manager

Defines the contract for all certificate exporters.
All exporters generate data only (no UI rendering) and use async patterns.
"""

import asyncio
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ExportFormat(Enum):
    """Supported export formats"""
    JSON = "json"
    XML = "xml"
    HTML = "html"
    PDF = "pdf"
    MARKDOWN = "markdown"
    CSV = "csv"
    YAML = "yaml"


class ExportOptions:
    """Configuration options for certificate exports"""
    
    def __init__(
        self,
        include_metadata: bool = True,
        include_metrics: bool = True,
        include_versions: bool = False,
        include_lineage: bool = False,
        include_audit_trail: bool = False,
        compression_level: int = 0,
        encryption_enabled: bool = False,
        digital_signature: bool = True,
        qr_code: bool = True,
        watermark: bool = False,
        custom_styling: Optional[Dict[str, Any]] = None
    ):
        self.include_metadata = include_metadata
        self.include_metrics = include_metrics
        self.include_versions = include_versions
        self.include_lineage = include_lineage
        self.include_audit_trail = include_audit_trail
        self.compression_level = compression_level
        self.encryption_enabled = encryption_enabled
        self.digital_signature = digital_signature
        self.qr_code = qr_code
        self.watermark = watermark
        self.custom_styling = custom_styling or {}


class BaseExporter(ABC):
    """
    Abstract base class for all certificate exporters
    
    All exporters must implement these methods to provide
    consistent export functionality across different formats.
    """
    
    def __init__(self, export_format: ExportFormat):
        """Initialize the base exporter"""
        self.export_format = export_format
        self.supported_formats = [export_format]
        self.export_locks: Dict[str, asyncio.Lock] = {}
        
        logger.info(f"Initialized {self.__class__.__name__} for {export_format.value}")
    
    @abstractmethod
    async def export_certificate(
        self,
        certificate_data: Dict[str, Any],
        options: ExportOptions,
        output_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Export certificate data to the specified format
        
        Args:
            certificate_data: Complete certificate data dictionary
            options: Export configuration options
            output_path: Optional path to save the exported file
            
        Returns:
            Dictionary containing export metadata and data
        """
        pass
    
    @abstractmethod
    async def validate_export_data(
        self,
        certificate_data: Dict[str, Any],
        options: ExportOptions
    ) -> bool:
        """
        Validate that the certificate data can be exported
        
        Args:
            certificate_data: Certificate data to validate
            options: Export options to validate against
            
        Returns:
            True if data is valid for export, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_export_metadata(
        self,
        certificate_data: Dict[str, Any],
        options: ExportOptions
    ) -> Dict[str, Any]:
        """
        Get metadata about the export operation
        
        Args:
            certificate_data: Certificate data being exported
            options: Export options being used
            
        Returns:
            Dictionary containing export metadata
        """
        pass
    
    async def _acquire_export_lock(self, certificate_id: str) -> asyncio.Lock:
        """Acquire a lock for concurrent export operations"""
        if certificate_id not in self.export_locks:
            self.export_locks[certificate_id] = asyncio.Lock()
        return self.export_locks[certificate_id]
    
    async def _release_export_lock(self, certificate_id: str) -> None:
        """Release the export lock for a certificate"""
        if certificate_id in self.export_locks:
            del self.export_locks[certificate_id]
    
    async def _prepare_certificate_data(
        self,
        certificate_data: Dict[str, Any],
        options: ExportOptions
    ) -> Dict[str, Any]:
        """
        Prepare certificate data for export based on options
        
        This method filters and structures the data according to
        the export options before passing to specific exporters.
        """
        prepared_data = {
            "certificate_id": certificate_data.get("certificate_id"),
            "export_timestamp": asyncio.get_event_loop().time(),
            "export_format": self.export_format.value,
            "export_options": options.__dict__
        }
        
        # Include metadata if requested
        if options.include_metadata:
            prepared_data["metadata"] = {
                "certificate_name": certificate_data.get("certificate_name"),
                "status": certificate_data.get("status"),
                "created_at": certificate_data.get("created_at"),
                "updated_at": certificate_data.get("updated_at"),
                "completion_percentage": certificate_data.get("completion_percentage"),
                "overall_quality_score": certificate_data.get("overall_quality_score"),
                "compliance_status": certificate_data.get("compliance_status"),
                "security_score": certificate_data.get("security_score")
            }
        
        # Include metrics if requested
        if options.include_metrics:
            prepared_data["metrics"] = certificate_data.get("metrics", {})
        
        # Include versions if requested
        if options.include_versions:
            prepared_data["versions"] = certificate_data.get("versions", [])
        
        # Include lineage if requested
        if options.include_lineage:
            prepared_data["lineage"] = certificate_data.get("lineage", {})
        
        # Include audit trail if requested
        if options.include_audit_trail:
            prepared_data["audit_trail"] = certificate_data.get("audit_trail", [])
        
        # Include core certificate data
        prepared_data["certificate_data"] = certificate_data
        
        return prepared_data
    
    async def _validate_required_fields(
        self,
        certificate_data: Dict[str, Any]
    ) -> List[str]:
        """
        Validate that required fields are present in certificate data
        
        Returns:
            List of missing required field names
        """
        required_fields = [
            "certificate_id",
            "certificate_name",
            "status",
            "created_at"
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in certificate_data or certificate_data[field] is None:
                missing_fields.append(field)
        
        return missing_fields
    
    async def _generate_export_filename(
        self,
        certificate_id: str,
        extension: str
    ) -> str:
        """Generate a filename for the exported certificate"""
        timestamp = asyncio.get_event_loop().time()
        return f"certificate_{certificate_id}_{timestamp}.{extension}"
    
    async def _log_export_operation(
        self,
        certificate_id: str,
        options: ExportOptions,
        success: bool,
        error_message: Optional[str] = None
    ) -> None:
        """Log export operation details"""
        log_data = {
            "certificate_id": certificate_id,
            "export_format": self.export_format.value,
            "options": options.__dict__,
            "success": success,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        if error_message:
            log_data["error"] = error_message
        
        if success:
            logger.info(f"Export completed successfully: {log_data}")
        else:
            logger.error(f"Export failed: {log_data}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health status of the exporter"""
        return {
            "exporter_type": self.__class__.__name__,
            "export_format": self.export_format.value,
            "supported_formats": [fmt.value for fmt in self.supported_formats],
            "active_locks": len(self.export_locks),
            "status": "healthy"
        } 