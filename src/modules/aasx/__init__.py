"""
AASX Backend Processing Package

This package contains the core AASX processing logic including:
- ETL pipeline for AASX data processing using external .NET processor
- AASX file extraction and generation orchestration
- Data transformation and validation
- Round-trip conversion capabilities
"""

# Unified AASX processor imports
from .aasx_processor import (
    extract_aasx, 
    batch_extract,
    generate_aasx, 
    generate_aasx_from_structured,
    batch_generate,
    round_trip_conversion
)

__all__ = [
    'extract_aasx',
    'batch_extract', 
    'generate_aasx',
    'generate_aasx_from_structured',
    'batch_generate',
    'round_trip_conversion'
]

__version__ = '2.0.0' 