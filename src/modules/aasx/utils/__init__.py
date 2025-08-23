"""
AASX Utilities Package

This package contains utility functions for AASX processing operations.
"""

from .validation_utils import (
    ValidationEngine,
    ValidationResult,
    ValidationError,
    create_validation_engine,
    validate_file_extension,
    validate_file_size,
    calculate_file_checksum,
    validate_identifier_format,
    validate_required_fields,
    validate_quality_score,
    validate_processing_time
)

from .format_utils import (
    FormatConverter,
    convert_aasx_to_json,
    convert_aasx_to_xml,
    convert_aasx_to_yaml,
    convert_json_to_aasx,
    convert_xml_to_aasx,
    convert_yaml_to_aasx,
    batch_convert_format,
    validate_conversion
)

__version__ = "1.0.0"
__author__ = "AAS Data Modeling Team"

__all__ = [
    # Validation utilities
    'ValidationEngine',
    'ValidationResult',
    'ValidationError',
    'create_validation_engine',
    'validate_file_extension',
    'validate_file_size',
    'calculate_file_checksum',
    'validate_identifier_format',
    'validate_required_fields',
    'validate_quality_score',
    'validate_processing_time',
    
    # Format conversion utilities
    'FormatConverter',
    'convert_aasx_to_json',
    'convert_aasx_to_xml',
    'convert_aasx_to_yaml',
    'convert_json_to_aasx',
    'convert_xml_to_aasx',
    'convert_yaml_to_aasx',
    'batch_convert_format',
    'validate_conversion'
]
