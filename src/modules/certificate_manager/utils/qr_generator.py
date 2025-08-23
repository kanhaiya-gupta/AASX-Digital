"""
QR Code Generation Utilities

This module provides comprehensive QR code generation, validation, and management utilities
for certificates and other document types.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


class QRCodeType(Enum):
    """QR code types for different use cases"""
    TEXT = "text"
    URL = "url"
    JSON = "json"
    XML = "xml"
    V_CARD = "vcard"
    WIFI = "wifi"
    EMAIL = "email"
    PHONE = "phone"
    SMS = "sms"
    GEO = "geo"
    CALENDAR = "calendar"
    CERTIFICATE = "certificate"


class QRCodeStyle(Enum):
    """QR code styling options"""
    STANDARD = "standard"
    ROUNDED = "rounded"
    CIRCULAR = "circular"
    GRADIENT = "gradient"
    CUSTOM = "custom"


@dataclass
class QRCodeConfig:
    """Configuration for QR code generation"""
    size: int = 256
    error_correction: str = "M"  # L, M, Q, H
    border: int = 4
    foreground_color: str = "#000000"
    background_color: str = "#FFFFFF"
    logo_path: Optional[str] = None
    logo_size: float = 0.3
    style: QRCodeStyle = QRCodeStyle.STANDARD


class QRGenerator:
    """
    QR code generation and management utility
    
    Handles:
    - QR code generation for various data types
    - Custom styling and branding
    - Batch generation and validation
    - QR code metadata management
    - Performance optimization
    """
    
    def __init__(self):
        """Initialize the QR generator utility"""
        self.qr_types = list(QRCodeType)
        self.qr_styles = list(QRCodeStyle)
        
        # QR code storage and metadata
        self.generated_codes: Dict[str, Dict[str, Any]] = {}
        self.qr_templates: Dict[str, QRCodeConfig] = {}
        self.generation_history: List[Dict[str, Any]] = []
        
        # Generation locks and queues
        self.generation_locks: Dict[str, asyncio.Lock] = {}
        self.generation_queue: asyncio.Queue = asyncio.Queue()
        
        # Performance tracking
        self.generation_stats = {
            "total_generated": 0,
            "successful": 0,
            "failed": 0,
            "average_time": 0.0
        }
        
        # Initialize default templates
        self._initialize_default_templates()
        
        logger.info("QR Generator utility initialized successfully")
    
    async def generate_qr_code(
        self,
        data: Union[str, Dict[str, Any]],
        qr_type: QRCodeType = QRCodeType.TEXT,
        config: Optional[QRCodeConfig] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a QR code with the specified data and configuration
        
        Args:
            data: Data to encode in the QR code
            qr_type: Type of QR code to generate
            config: QR code configuration
            metadata: Additional metadata for the QR code
            
        Returns:
            Dictionary containing QR code information and generated data
        """
        start_time = time.time()
        qr_id = f"qr_{int(time.time() * 1000)}"
        
        try:
            # Validate input parameters
            await self._validate_generation_params(data, qr_type, config)
            
            # Prepare data for encoding
            encoded_data = await self._prepare_data_for_encoding(data, qr_type)
            
            # Apply configuration
            qr_config = config or self.qr_templates.get(qr_type.value, QRCodeConfig())
            
            # Generate QR code (simulated)
            qr_code_data = await self._generate_qr_code_data(encoded_data, qr_config)
            
            # Create metadata
            qr_metadata = await self._create_qr_metadata(
                qr_id, data, qr_type, qr_config, metadata
            )
            
            # Store generated QR code
            qr_info = {
                "id": qr_id,
                "data": encoded_data,
                "qr_type": qr_type.value,
                "config": qr_config.__dict__,
                "metadata": qr_metadata,
                "generated_at": time.time(),
                "size_bytes": len(str(qr_code_data)),
                "status": "success"
            }
            
            self.generated_codes[qr_id] = qr_info
            self.generation_history.append(qr_info)
            
            # Update statistics
            await self._update_generation_stats(True, time.time() - start_time)
            
            logger.info(f"QR code generated successfully: {qr_id}")
            return qr_info
            
        except Exception as e:
            await self._update_generation_stats(False, time.time() - start_time)
            logger.error(f"Failed to generate QR code: {str(e)}")
            raise
    
    async def generate_batch_qr_codes(
        self,
        data_list: List[Union[str, Dict[str, Any]]],
        qr_type: QRCodeType = QRCodeType.TEXT,
        config: Optional[QRCodeConfig] = None,
        batch_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple QR codes in batch
        
        Args:
            data_list: List of data items to encode
            qr_type: Type of QR codes to generate
            config: QR code configuration
            batch_metadata: Additional metadata for the batch
            
        Returns:
            List of generated QR code information
        """
        batch_id = f"batch_{int(time.time() * 1000)}"
        results = []
        
        logger.info(f"Starting batch QR code generation: {batch_id}")
        
        # Create tasks for concurrent generation
        tasks = []
        for i, data in enumerate(data_list):
            task = asyncio.create_task(
                self.generate_qr_code(data, qr_type, config, {
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
                logger.error(f"Failed to generate QR code {i} in batch {batch_id}: {str(result)}")
                results.append({
                    "id": f"failed_{batch_id}_{i}",
                    "status": "failed",
                    "error": str(result),
                    "batch_id": batch_id,
                    "batch_index": i
                })
            else:
                results.append(result)
        
        logger.info(f"Batch QR code generation completed: {batch_id}, {len(results)} results")
        return results
    
    async def validate_qr_code(self, qr_id: str) -> Dict[str, Any]:
        """
        Validate a generated QR code
        
        Args:
            qr_id: ID of the QR code to validate
            
        Returns:
            Validation result information
        """
        if qr_id not in self.generated_codes:
            raise ValueError(f"QR code not found: {qr_id}")
        
        qr_info = self.generated_codes[qr_id]
        
        # Perform validation checks
        validation_result = await self._perform_validation_checks(qr_info)
        
        return {
            "qr_id": qr_id,
            "validation_result": validation_result,
            "validated_at": time.time(),
            "status": "validated"
        }
    
    async def get_qr_code_info(self, qr_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a generated QR code
        
        Args:
            qr_id: ID of the QR code
            
        Returns:
            QR code information
        """
        if qr_id not in self.generated_codes:
            raise ValueError(f"QR code not found: {qr_id}")
        
        return self.generated_codes[qr_id]
    
    async def get_qr_code_history(
        self,
        qr_type: Optional[QRCodeType] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get QR code generation history
        
        Args:
            qr_type: Filter by QR code type
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of QR code history entries
        """
        history = self.generation_history
        
        if qr_type:
            history = [h for h in history if h.get("qr_type") == qr_type.value]
        
        # Sort by generation time (newest first)
        history.sort(key=lambda x: x.get("generated_at", 0), reverse=True)
        
        return history[offset:offset + limit]
    
    async def create_qr_template(
        self,
        template_name: str,
        config: QRCodeConfig
    ) -> Dict[str, Any]:
        """
        Create a reusable QR code template
        
        Args:
            template_name: Name of the template
            config: QR code configuration
            
        Returns:
            Template creation result
        """
        if template_name in self.qr_templates:
            raise ValueError(f"Template already exists: {template_name}")
        
        self.qr_templates[template_name] = config
        
        return {
            "template_name": template_name,
            "config": config.__dict__,
            "created_at": time.time(),
            "status": "created"
        }
    
    async def get_generation_statistics(self) -> Dict[str, Any]:
        """
        Get QR code generation statistics
        
        Returns:
            Generation statistics
        """
        return self.generation_stats.copy()
    
    async def cleanup_expired_codes(self, max_age_hours: int = 24) -> int:
        """
        Clean up expired QR codes
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
            
        Returns:
            Number of codes cleaned up
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        expired_codes = []
        for qr_id, qr_info in self.generated_codes.items():
            if current_time - qr_info.get("generated_at", 0) > max_age_seconds:
                expired_codes.append(qr_id)
        
        # Remove expired codes
        for qr_id in expired_codes:
            del self.generated_codes[qr_id]
        
        logger.info(f"Cleaned up {len(expired_codes)} expired QR codes")
        return len(expired_codes)
    
    # Private helper methods
    
    def _initialize_default_templates(self):
        """Initialize default QR code templates"""
        # Standard text template
        self.qr_templates["standard_text"] = QRCodeConfig(
            size=256,
            error_correction="M",
            border=4,
            style=QRCodeStyle.STANDARD
        )
        
        # Certificate template
        self.qr_templates["certificate"] = QRCodeConfig(
            size=512,
            error_correction="H",
            border=6,
            foreground_color="#1a365d",
            background_color="#f7fafc",
            style=QRCodeStyle.ROUNDED
        )
        
        # URL template
        self.qr_templates["url"] = QRCodeConfig(
            size=320,
            error_correction="Q",
            border=5,
            style=QRCodeStyle.STANDARD
        )
    
    async def _validate_generation_params(
        self,
        data: Union[str, Dict[str, Any]],
        qr_type: QRCodeType,
        config: Optional[QRCodeConfig]
    ):
        """Validate QR code generation parameters"""
        if not data:
            raise ValueError("Data cannot be empty")
        
        if not isinstance(qr_type, QRCodeType):
            raise ValueError("Invalid QR code type")
        
        if config and not isinstance(config, QRCodeConfig):
            raise ValueError("Invalid configuration object")
    
    async def _prepare_data_for_encoding(
        self,
        data: Union[str, Dict[str, Any]],
        qr_type: QRCodeType
    ) -> str:
        """Prepare data for QR code encoding based on type"""
        if qr_type == QRCodeType.JSON:
            if isinstance(data, dict):
                return str(data)
            else:
                return str(data)
        elif qr_type == QRCodeType.XML:
            if isinstance(data, dict):
                # Convert dict to XML-like string (simulated)
                return f"<data>{str(data)}</data>"
            else:
                return str(data)
        elif qr_type == QRCodeType.V_CARD:
            if isinstance(data, dict):
                # Convert dict to vCard format (simulated)
                return f"BEGIN:VCARD\n{str(data)}\nEND:VCARD"
            else:
                return str(data)
        elif qr_type == QRCodeType.WIFI:
            if isinstance(data, dict):
                # Convert dict to WiFi format (simulated)
                return f"WIFI:S:{data.get('ssid', '')};T:{data.get('type', 'WPA')};P:{data.get('password', '')};;"
            else:
                return str(data)
        else:
            return str(data)
    
    async def _generate_qr_code_data(self, data: str, config: QRCodeConfig) -> str:
        """Generate QR code data (simulated)"""
        # Simulate QR code generation
        qr_data = f"QR_CODE_DATA:{data}"
        
        # Apply size configuration
        if config.size > 256:
            qr_data += f"_LARGE_{config.size}"
        
        # Apply style configuration
        if config.style != QRCodeStyle.STANDARD:
            qr_data += f"_STYLE_{config.style.value}"
        
        return qr_data
    
    async def _create_qr_metadata(
        self,
        qr_id: str,
        data: Union[str, Dict[str, Any]],
        qr_type: QRCodeType,
        config: QRCodeConfig,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create metadata for the generated QR code"""
        base_metadata = {
            "generator": "CertificateManager",
            "version": "1.0.0",
            "qr_type": qr_type.value,
            "config_hash": hash(str(config.__dict__)),
            "data_hash": hash(str(data)),
            "timestamp": time.time()
        }
        
        if metadata:
            base_metadata.update(metadata)
        
        return base_metadata
    
    async def _perform_validation_checks(self, qr_info: Dict[str, Any]) -> Dict[str, Any]:
        """Perform validation checks on a QR code"""
        checks = {
            "data_integrity": True,
            "config_validity": True,
            "metadata_completeness": True,
            "size_appropriateness": True
        }
        
        # Check data integrity
        if not qr_info.get("data"):
            checks["data_integrity"] = False
        
        # Check config validity
        config = qr_info.get("config", {})
        if not config.get("size") or config["size"] <= 0:
            checks["config_validity"] = False
        
        # Check metadata completeness
        metadata = qr_info.get("metadata", {})
        required_fields = ["generator", "version", "timestamp"]
        for field in required_fields:
            if field not in metadata:
                checks["metadata_completeness"] = False
                break
        
        # Check size appropriateness
        data_size = len(str(qr_info.get("data", "")))
        qr_size = config.get("size", 256)
        if data_size > qr_size * 0.8:  # 80% capacity rule
            checks["size_appropriateness"] = False
        
        return checks
    
    async def _update_generation_stats(self, success: bool, generation_time: float):
        """Update generation statistics"""
        self.generation_stats["total_generated"] += 1
        
        if success:
            self.generation_stats["successful"] += 1
        else:
            self.generation_stats["failed"] += 1
        
        # Update average generation time
        total_successful = self.generation_stats["successful"]
        if total_successful > 0:
            current_avg = self.generation_stats["average_time"]
            self.generation_stats["average_time"] = (
                (current_avg * (total_successful - 1) + generation_time) / total_successful
            )
