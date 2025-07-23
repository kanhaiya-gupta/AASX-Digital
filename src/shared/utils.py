import logging
import sys
import os
from pathlib import Path
from typing import Optional

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

def log_info(message: str) -> None:
    """
    Log an info message.
    
    Args:
        message: Message to log
    """
    logger = logging.getLogger(__name__)
    logger.info(message)

def log_error(message: str) -> None:
    """
    Log an error message.
    
    Args:
        message: Message to log
    """
    logger = logging.getLogger(__name__)
    logger.error(message)
