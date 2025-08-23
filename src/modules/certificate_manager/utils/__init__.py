"""
Certificate Manager Utils Package

This package provides comprehensive utility and helper services including:
- QR code generation utilities
- PDF generation utilities (backend)
- HTML generation utilities (backend)
- XML generation utilities
- JSON processing utilities
- Cryptographic utilities
- Data validation utilities
- Data formatting utilities
- Business intelligence utilities
- Real-time processing utilities
"""

from .qr_generator import QRGenerator, QRCodeType, QRCodeStyle
from .pdf_utils import PDFGenerator, PDFTemplate, PDFStyle
from .html_utils import HTMLGenerator, HTMLTemplate, HTMLStyle
from .xml_utils import XMLGenerator, XMLTemplate, XMLStyle
from .json_utils import JSONProcessor, JSONSchema, JSONValidator
from .crypto_utils import CryptoUtils, CryptoAlgorithm, CryptoMode
from .validation_utils import ValidationUtils, ValidationRule, ValidationResult
from .formatting_utils import FormattingUtils, FormatType, FormatStyle
from .business_logic_utils import BusinessLogicUtils, BusinessRule, BusinessMetric
from .real_time_utils import RealTimeUtils, RealTimeEvent, RealTimeProcessor

__all__ = [
    # QR code utilities
    "QRGenerator",
    "QRCodeType",
    "QRCodeStyle",
    
    # PDF utilities
    "PDFGenerator",
    "PDFTemplate", 
    "PDFStyle",
    
    # HTML utilities
    "HTMLGenerator",
    "HTMLTemplate",
    "HTMLStyle",
    
    # XML utilities
    "XMLGenerator",
    "XMLTemplate",
    "XMLStyle",
    
    # JSON utilities
    "JSONProcessor",
    "JSONSchema",
    "JSONValidator",
    
    # Cryptographic utilities
    "CryptoUtils",
    "CryptoAlgorithm",
    "CryptoMode",
    
    # Validation utilities
    "ValidationUtils",
    "ValidationRule",
    "ValidationResult",
    
    # Formatting utilities
    "FormattingUtils",
    "FormatType",
    "FormatStyle",
    
    # Business logic utilities
    "BusinessLogicUtils",
    "BusinessRule",
    "BusinessMetric",
    
    # Real-time utilities
    "RealTimeUtils",
    "RealTimeEvent",
    "RealTimeProcessor"
]
