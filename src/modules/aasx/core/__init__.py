"""
AASX Core Business Logic Package

This package contains the core business logic services for AASX processing operations.
Includes extraction, generation, validation, conversion, and quality assessment services.
"""

# Core AASX processor
from .aasx_processor import (
    extract_aasx, 
    batch_extract,
    generate_aasx, 
    generate_aasx_from_structured,
    batch_generate,
    round_trip_conversion
)

__version__ = "1.0.0"
__author__ = "AAS Data Modeling Team"

__all__ = [
    'extract_aasx',
    'batch_extract', 
    'generate_aasx',
    'generate_aasx_from_structured',
    'batch_generate',
    'round_trip_conversion'
]
