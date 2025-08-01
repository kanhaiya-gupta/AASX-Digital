"""
Utilities Package
================

Common utilities for the AAS Data Modeling framework.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from .file_utils import FileUtils
from .validation_utils import ValidationUtils
from .security_utils import SecurityUtils
from .logging_utils import LoggingUtils, ColoredFormatter, JSONFormatter

def setup_logging(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up logging for a module.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding handlers multiple times
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

def ensure_dir(path: Path) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Path to the directory
    """
    path.mkdir(parents=True, exist_ok=True)

__all__ = [
    'FileUtils',
    'ValidationUtils', 
    'SecurityUtils',
    'LoggingUtils',
    'ColoredFormatter',
    'JSONFormatter',
    'setup_logging',
    'ensure_dir'
] 