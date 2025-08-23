"""
QR Code Generator for Certificate Manager

Generates QR codes for certificates with various formats and error correction levels.
Provides QR code generation, validation, and customization options.
"""

import asyncio
import hashlib
import json
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
import logging
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class QRCodeFormat(Enum):
    """Supported QR code formats"""
    TEXT = "text"
    URL = "url"
    JSON = "json"
    XML = "xml"
    BINARY = "binary"
    V_CARD = "vcard"
    WIFI = "wifi"
    EMAIL = "email"
    PHONE = "phone"
    SMS = "sms"


class QRCodeErrorCorrection(Enum):
    """QR code error correction levels"""
    LOW = "L"      # 7% recovery
    MEDIUM = "M"   # 15% recovery
    QUARTILE = "Q" # 25% recovery
    HIGH = "H"     # 30% recovery


class QRCodeGenerator:
    """
    QR code generation service for certificates
    
    Handles:
    - QR code generation for various formats
    - Error correction level configuration
    - QR code customization and styling
    - QR code validation and verification
    - Batch QR code generation
    """
    
    def __init__(self):
        """Initialize the QR code generator"""
        self.supported_formats = list(QRCodeFormat)
        self.error_correction_levels = list(QRCodeErrorCorrection)
        self.generated_qr_codes: Dict[str, Dict[str, Any]] = {}
        self.qr_code_history: List[Dict[str, Any]] = []
        self.generation_locks: Dict[str, asyncio.Lock] = {}
        
        # QR code generation settings
        self.default_settings = {
            "size": 256,
            "border": 4,
            "error_correction": QRCodeErrorCorrection.MEDIUM,
            "foreground_color": "#000000",
            "background_color": "#FFFFFF"
        }
        
        logger.info("QR Code Generator initialized successfully")
    
    async def generate_qr_code(
        self,
        certificate_data: Dict[str, Any],
        format_type: QRCodeFormat = QRCodeFormat.JSON,
        error_correction: QRCodeErrorCorrection = QRCodeErrorCorrection.MEDIUM,
        size: int = 256,
        custom_settings: Optional[Dict[str, Any]] = None,
        output_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Generate QR code for certificate data
        
        Args:
            certificate_data: Certificate data to encode
            format_type: QR code format type
            error_correction: Error correction level
            size: QR code size in pixels
            custom_settings: Custom generation settings
            output_path: Optional path to save QR code
            
        Returns:
            Dictionary containing QR code data and metadata
        """
        certificate_id = certificate_data.get("certificate_id", "unknown")
        
        # Acquire generation lock
        async with await self._acquire_generation_lock(certificate_id):
            try:
                # Validate parameters
                await self._validate_generation_parameters(
                    format_type, error_correction, size, custom_settings
                )
                
                # Prepare data for QR code
                qr_data = await self._prepare_data_for_qr(
                    certificate_data, format_type
                )
                
                # Generate QR code content
                qr_content = await self._generate_qr_content(
                    qr_data, format_type, error_correction
                )
                
                # Create QR code metadata
                qr_metadata = await self._create_qr_metadata(
                    certificate_data, format_type, error_correction, size, custom_settings
                )
                
                # Generate QR code ID
                qr_code_id = f"qr_{certificate_id}_{asyncio.get_event_loop().time()}"
                
                # Create QR code result
                qr_result = {
                    "qr_code_id": qr_code_id,
                    "certificate_id": certificate_id,
                    "format": format_type.value,
                    "error_correction": error_correction.value,
                    "size": size,
                    "content": qr_content,
                    "metadata": qr_metadata,
                    "generated_at": asyncio.get_event_loop().time(),
                    "checksum": await self._generate_content_checksum(qr_content)
                }
                
                # Store generated QR code
                self.generated_qr_codes[qr_code_id] = qr_result
                
                # Record in history
                self.qr_code_history.append({
                    "timestamp": asyncio.get_event_loop().time(),
                    "action": "generate",
                    "certificate_id": certificate_id,
                    "format": format_type.value,
                    "qr_code_id": qr_code_id,
                    "size": size
                })
                
                # Save to file if output path provided
                if output_path:
                    await self._save_qr_code_file(output_path, qr_content, qr_metadata)
                    qr_result["output_path"] = str(output_path)
                
                logger.info(f"QR code generated for certificate {certificate_id} in {format_type.value} format")
                
                return qr_result
                
            except Exception as e:
                error_msg = f"QR code generation failed: {str(e)}"
                logger.error(f"Failed to generate QR code for {certificate_id}: {error_msg}")
                raise
    
    async def generate_batch_qr_codes(
        self,
        certificates_data: List[Dict[str, Any]],
        format_type: QRCodeFormat = QRCodeFormat.JSON,
        error_correction: QRCodeErrorCorrection = QRCodeErrorCorrection.MEDIUM,
        size: int = 256,
        output_dir: Optional[Path] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate QR codes for multiple certificates
        
        Args:
            certificates_data: List of certificate data
            format_type: QR code format type
            error_correction: Error correction level
            size: QR code size in pixels
            output_dir: Directory to save QR codes
            
        Returns:
            List of generated QR code results
        """
        batch_results = []
        
        for certificate_data in certificates_data:
            try:
                # Generate individual QR code
                qr_result = await self.generate_qr_code(
                    certificate_data, format_type, error_correction, size
                )
                
                # Save to output directory if specified
                if output_dir:
                    filename = f"qr_{certificate_data.get('certificate_id', 'unknown')}.txt"
                    output_path = output_dir / filename
                    await self._save_qr_code_file(output_path, qr_result["content"], qr_result["metadata"])
                    qr_result["output_path"] = str(output_path)
                
                batch_results.append(qr_result)
                
            except Exception as e:
                logger.error(f"Failed to generate QR code for certificate: {e}")
                batch_results.append({
                    "error": str(e),
                    "certificate_id": certificate_data.get("certificate_id", "unknown")
                })
        
        return batch_results
    
    async def validate_qr_code(
        self,
        qr_content: str,
        expected_format: QRCodeFormat,
        certificate_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate generated QR code content
        
        Args:
            qr_content: QR code content to validate
            expected_format: Expected format type
            certificate_id: Certificate ID for validation
            
        Returns:
            Dictionary containing validation result
        """
        try:
            # Basic content validation
            content_validation = await self._validate_qr_content(qr_content, expected_format)
            
            # Format-specific validation
            format_validation = await self._validate_format_specific(qr_content, expected_format)
            
            # Certificate data validation if ID provided
            certificate_validation = {}
            if certificate_id:
                certificate_validation = await self._validate_certificate_data(
                    qr_content, certificate_id
                )
            
            # Determine overall validation status
            is_valid = (
                content_validation.get("is_valid", False) and
                format_validation.get("is_valid", False) and
                (not certificate_id or certificate_validation.get("is_valid", False))
            )
            
            validation_result = {
                "is_valid": is_valid,
                "content_validation": content_validation,
                "format_validation": format_validation,
                "certificate_validation": certificate_validation,
                "validation_timestamp": asyncio.get_event_loop().time()
            }
            
            # Record validation
            self.qr_code_history.append({
                "timestamp": asyncio.get_event_loop().time(),
                "action": "validate",
                "certificate_id": certificate_id,
                "format": expected_format.value,
                "validation_result": validation_result
            })
            
            return validation_result
            
        except Exception as e:
            logger.error(f"QR code validation failed: {e}")
            return {
                "is_valid": False,
                "error": str(e),
                "validation_timestamp": asyncio.get_event_loop().time()
            }
    
    async def get_qr_code_info(self, qr_code_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a generated QR code"""
        return self.generated_qr_codes.get(qr_code_id)
    
    async def get_qr_code_history(
        self,
        certificate_id: Optional[str] = None,
        format_type: Optional[QRCodeFormat] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get QR code generation history with optional filtering"""
        history = self.qr_code_history.copy()
        
        # Filter by certificate ID
        if certificate_id:
            history = [h for h in history if h.get("certificate_id") == certificate_id]
        
        # Filter by format
        if format_type:
            history = [h for h in history if h.get("format") == format_type.value]
        
        # Sort by timestamp (newest first) and limit results
        history.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        return history[:limit]
    
    async def _acquire_generation_lock(self, certificate_id: str) -> asyncio.Lock:
        """Acquire a lock for QR code generation"""
        if certificate_id not in self.generation_locks:
            self.generation_locks[certificate_id] = asyncio.Lock()
        return self.generation_locks[certificate_id]
    
    async def _validate_generation_parameters(
        self,
        format_type: QRCodeFormat,
        error_correction: QRCodeErrorCorrection,
        size: int,
        custom_settings: Optional[Dict[str, Any]]
    ) -> None:
        """Validate QR code generation parameters"""
        # Validate format
        if format_type not in self.supported_formats:
            raise ValueError(f"Unsupported QR code format: {format_type}")
        
        # Validate error correction level
        if error_correction not in self.error_correction_levels:
            raise ValueError(f"Unsupported error correction level: {error_correction}")
        
        # Validate size
        if size < 64 or size > 1024:
            raise ValueError(f"QR code size must be between 64 and 1024 pixels, got: {size}")
        
        # Validate custom settings if provided
        if custom_settings:
            await self._validate_custom_settings(custom_settings)
    
    async def _validate_custom_settings(self, custom_settings: Dict[str, Any]) -> None:
        """Validate custom QR code generation settings"""
        # Validate colors
        if "foreground_color" in custom_settings:
            color = custom_settings["foreground_color"]
            if not self._is_valid_hex_color(color):
                raise ValueError(f"Invalid foreground color: {color}")
        
        if "background_color" in custom_settings:
            color = custom_settings["background_color"]
            if not self._is_valid_hex_color(color):
                raise ValueError(f"Invalid background color: {color}")
        
        # Validate border
        if "border" in custom_settings:
            border = custom_settings["border"]
            if not isinstance(border, int) or border < 0 or border > 20:
                raise ValueError(f"Border must be between 0 and 20, got: {border}")
    
    def _is_valid_hex_color(self, color: str) -> bool:
        """Check if a string is a valid hex color"""
        if not color.startswith("#"):
            return False
        
        if len(color) not in [4, 7, 9]:  # #RGB, #RRGGBB, #RRGGBBAA
            return False
        
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False
    
    async def _prepare_data_for_qr(
        self,
        certificate_data: Dict[str, Any],
        format_type: QRCodeFormat
    ) -> str:
        """Prepare certificate data for QR code generation"""
        if format_type == QRCodeFormat.TEXT:
            return await self._prepare_text_format(certificate_data)
        elif format_type == QRCodeFormat.JSON:
            return await self._prepare_json_format(certificate_data)
        elif format_type == QRCodeFormat.XML:
            return await self._prepare_xml_format(certificate_data)
        elif format_type == QRCodeFormat.URL:
            return await self._prepare_url_format(certificate_data)
        elif format_type == QRCodeFormat.V_CARD:
            return await self._prepare_vcard_format(certificate_data)
        elif format_type == QRCodeFormat.WIFI:
            return await self._prepare_wifi_format(certificate_data)
        elif format_type == QRCodeFormat.EMAIL:
            return await self._prepare_email_format(certificate_data)
        elif format_type == QRCodeFormat.PHONE:
            return await self._prepare_phone_format(certificate_data)
        elif format_type == QRCodeFormat.SMS:
            return await self._prepare_sms_format(certificate_data)
        else:
            return await self._prepare_text_format(certificate_data)
    
    async def _prepare_text_format(self, certificate_data: Dict[str, Any]) -> str:
        """Prepare data in plain text format"""
        lines = [
            f"Certificate: {certificate_data.get('certificate_name', 'Unknown')}",
            f"ID: {certificate_data.get('certificate_id', 'Unknown')}",
            f"Status: {certificate_data.get('status', 'Unknown')}",
            f"Completion: {certificate_data.get('completion_percentage', 0)}%",
            f"Quality: {certificate_data.get('overall_quality_score', 0)}%",
            f"Created: {certificate_data.get('created_at', 'Unknown')}"
        ]
        return "\n".join(lines)
    
    async def _prepare_json_format(self, certificate_data: Dict[str, Any]) -> str:
        """Prepare data in JSON format"""
        # Create a simplified version for QR code
        qr_data = {
            "certificate_id": certificate_data.get("certificate_id"),
            "certificate_name": certificate_data.get("certificate_name"),
            "status": certificate_data.get("status"),
            "completion_percentage": certificate_data.get("completion_percentage"),
            "overall_quality_score": certificate_data.get("overall_quality_score"),
            "created_at": certificate_data.get("created_at"),
            "qr_generated_at": datetime.utcnow().isoformat()
        }
        return json.dumps(qr_data, separators=(',', ':'))
    
    async def _prepare_xml_format(self, certificate_data: Dict[str, Any]) -> str:
        """Prepare data in XML format"""
        xml_lines = [
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
            "<certificate>",
            f"  <id>{certificate_data.get('certificate_id', 'Unknown')}</id>",
            f"  <name>{certificate_data.get('certificate_name', 'Unknown')}</name>",
            f"  <status>{certificate_data.get('status', 'Unknown')}</status>",
            f"  <completion>{certificate_data.get('completion_percentage', 0)}</completion>",
            f"  <quality>{certificate_data.get('overall_quality_score', 0)}</quality>",
            f"  <created>{certificate_data.get('created_at', 'Unknown')}</created>",
            f"  <qr_generated>{datetime.utcnow().isoformat()}</qr_generated>",
            "</certificate>"
        ]
        return "\n".join(xml_lines)
    
    async def _prepare_url_format(self, certificate_data: Dict[str, Any]) -> str:
        """Prepare data in URL format"""
        base_url = "https://certificate-manager.org/certificate"
        certificate_id = certificate_data.get("certificate_id", "unknown")
        return f"{base_url}/{certificate_id}"
    
    async def _prepare_vcard_format(self, certificate_data: Dict[str, Any]) -> str:
        """Prepare data in vCard format"""
        vcard_lines = [
            "BEGIN:VCARD",
            "VERSION:3.0",
            f"FN:{certificate_data.get('certificate_name', 'Unknown Certificate')}",
            f"UID:{certificate_data.get('certificate_id', 'unknown')}",
            f"NOTE:Status: {certificate_data.get('status', 'Unknown')}, Completion: {certificate_data.get('completion_percentage', 0)}%",
            f"REV:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
            "END:VCARD"
        ]
        return "\n".join(vcard_lines)
    
    async def _prepare_wifi_format(self, certificate_data: Dict[str, Any]) -> str:
        """Prepare data in WiFi format"""
        # This is a simplified WiFi format for demonstration
        return f"WIFI:S:Certificate_{certificate_data.get('certificate_id', 'unknown')};T:WPA;P:cert123;;"
    
    async def _prepare_email_format(self, certificate_data: Dict[str, Any]) -> str:
        """Prepare data in email format"""
        return f"mailto:admin@certificate-manager.org?subject=Certificate {certificate_data.get('certificate_id', 'unknown')}&body=Status: {certificate_data.get('status', 'Unknown')}"
    
    async def _prepare_phone_format(self, certificate_data: Dict[str, Any]) -> str:
        """Prepare data in phone format"""
        return f"tel:+1234567890"
    
    async def _prepare_sms_format(self, certificate_data: Dict[str, Any]) -> str:
        """Prepare data in SMS format"""
        return f"sms:+1234567890:Certificate {certificate_data.get('certificate_id', 'unknown')} status: {certificate_data.get('status', 'Unknown')}"
    
    async def _generate_qr_content(
        self,
        data: str,
        format_type: QRCodeFormat,
        error_correction: QRCodeErrorCorrection
    ) -> str:
        """Generate QR code content with specified format and error correction"""
        # In a real implementation, this would generate actual QR code image data
        # For now, we'll create a text representation
        
        # Add format and error correction metadata
        qr_content = f"""
QR CODE CONTENT
===============
Format: {format_type.value}
Error Correction: {error_correction.value}
Generated: {datetime.utcnow().isoformat()}
Data Length: {len(data)} characters

DATA:
{data}

END QR CODE
"""
        return qr_content.strip()
    
    async def _create_qr_metadata(
        self,
        certificate_data: Dict[str, Any],
        format_type: QRCodeFormat,
        error_correction: QRCodeErrorCorrection,
        size: int,
        custom_settings: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create comprehensive QR code metadata"""
        metadata = {
            "certificate_name": certificate_data.get("certificate_name"),
            "certificate_status": certificate_data.get("status"),
            "format_type": format_type.value,
            "error_correction": error_correction.value,
            "size": size,
            "generation_settings": {
                "size": size,
                "border": custom_settings.get("border", self.default_settings["border"]) if custom_settings else self.default_settings["border"],
                "foreground_color": custom_settings.get("foreground_color", self.default_settings["foreground_color"]) if custom_settings else self.default_settings["foreground_color"],
                "background_color": custom_settings.get("background_color", self.default_settings["background_color"]) if custom_settings else self.default_settings["background_color"]
            },
            "generator_version": "1.0"
        }
        
        return metadata
    
    async def _generate_content_checksum(self, content: str) -> str:
        """Generate checksum for QR code content"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    async def _save_qr_code_file(
        self,
        output_path: Path,
        content: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Save QR code content to file"""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save content
            output_path.write_text(content, encoding='utf-8')
            
            # Save metadata to separate file
            metadata_path = output_path.with_suffix('.metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"QR code saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save QR code file: {e}")
            raise
    
    async def _validate_qr_content(self, content: str, expected_format: QRCodeFormat) -> Dict[str, Any]:
        """Validate basic QR code content"""
        if not content or len(content.strip()) == 0:
            return {
                "is_valid": False,
                "reason": "Empty or null content"
            }
        
        # Check content length (QR codes have practical limits)
        if len(content) > 2953:  # Maximum for version 40 QR code with low error correction
            return {
                "is_valid": False,
                "reason": f"Content too long: {len(content)} characters (max: 2953)"
            }
        
        return {
            "is_valid": True,
            "content_length": len(content),
            "reason": "Content validation passed"
        }
    
    async def _validate_format_specific(self, content: str, expected_format: QRCodeFormat) -> Dict[str, Any]:
        """Validate content based on expected format"""
        try:
            if expected_format == QRCodeFormat.JSON:
                # Validate JSON format
                json.loads(content)
                return {
                    "is_valid": True,
                    "reason": "Valid JSON format"
                }
            
            elif expected_format == QRCodeFormat.XML:
                # Basic XML validation
                if content.startswith("<?xml") and content.endswith("</certificate>"):
                    return {
                        "is_valid": True,
                        "reason": "Valid XML format"
                    }
                else:
                    return {
                        "is_valid": False,
                        "reason": "Invalid XML format"
                    }
            
            elif expected_format == QRCodeFormat.URL:
                # Basic URL validation
                if content.startswith(("http://", "https://")):
                    return {
                        "is_valid": True,
                        "reason": "Valid URL format"
                    }
                else:
                    return {
                        "is_valid": False,
                        "reason": "Invalid URL format"
                    }
            
            else:
                # For other formats, just check if content exists
                return {
                    "is_valid": True,
                    "reason": f"Format {expected_format.value} validation passed"
                }
                
        except Exception as e:
            return {
                "is_valid": False,
                "reason": f"Format validation error: {str(e)}"
            }
    
    async def _validate_certificate_data(self, content: str, certificate_id: str) -> Dict[str, Any]:
        """Validate that QR code content contains expected certificate data"""
        # Check if certificate ID is present in content
        if certificate_id in content:
            return {
                "is_valid": True,
                "reason": "Certificate ID found in content"
            }
        else:
            return {
                "is_valid": False,
                "reason": "Certificate ID not found in content"
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health status of the QR code generator"""
        return {
            "status": "healthy",
            "supported_formats": [fmt.value for fmt in self.supported_formats],
            "error_correction_levels": [level.value for level in self.error_correction_levels],
            "generated_qr_codes": len(self.generated_qr_codes),
            "qr_code_history_size": len(self.qr_code_history),
            "default_settings": self.default_settings,
            "timestamp": asyncio.get_event_loop().time()
        }
