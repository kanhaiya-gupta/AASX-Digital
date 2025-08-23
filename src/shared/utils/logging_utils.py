"""
Logging Utilities
================

Logging configuration and utilities for the AAS Data Modeling framework.
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for console logging."""
    
    # Color codes for different log levels
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to the log level
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)

class LoggingUtils:
    """Utility class for logging configuration."""
    
    # Default logging configuration
    DEFAULT_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(funcName)s(): %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'json': {
                '()': 'src.shared.utils.logging_utils.JSONFormatter'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'filename': 'logs/aas_data_modeling.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': 'logs/errors.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            }
        },
        'loggers': {
            '': {  # Root logger
                'handlers': ['console', 'file', 'error_file'],
                'level': 'INFO',
                'propagate': False
            },
            'src.shared': {
                'handlers': ['console', 'file', 'error_file'],
                'level': 'DEBUG',
                'propagate': False
            },
            'webapp': {
                'handlers': ['console', 'file', 'error_file'],
                'level': 'INFO',
                'propagate': False
            }
        }
    }
    
    @staticmethod
    def setup_logging(
        log_level: str = 'INFO',
        log_file: Optional[str] = None,
        error_file: Optional[str] = None,
        enable_console: bool = True,
        enable_colors: bool = True,
        enable_json: bool = False
    ) -> None:
        """Setup logging configuration."""
        try:
            # Create logs directory if it doesn't exist
            if log_file:
                log_path = Path(log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
            
            if error_file:
                error_path = Path(error_file)
                error_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Configure root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(getattr(logging, log_level.upper()))
            
            # Clear existing handlers
            root_logger.handlers.clear()
            
            # Create formatters
            if enable_json:
                formatter = JSONFormatter()
            elif enable_colors and enable_console:
                formatter = ColoredFormatter(
                    '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
            else:
                formatter = logging.Formatter(
                    '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
            
            # Console handler
            if enable_console:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(getattr(logging, log_level.upper()))
                console_handler.setFormatter(formatter)
                root_logger.addHandler(console_handler)
            
            # File handler
            if log_file:
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file,
                    maxBytes=10*1024*1024,  # 10MB
                    backupCount=5
                )
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)
            
            # Error file handler
            if error_file:
                error_handler = logging.handlers.RotatingFileHandler(
                    error_file,
                    maxBytes=10*1024*1024,  # 10MB
                    backupCount=5
                )
                error_handler.setLevel(logging.ERROR)
                error_handler.setFormatter(formatter)
                root_logger.addHandler(error_handler)
            
            # Set specific logger levels
            logging.getLogger('src.shared').setLevel(logging.DEBUG)
            logging.getLogger('webapp').setLevel(logging.INFO)
            
            # Suppress noisy loggers
            logging.getLogger('urllib3').setLevel(logging.WARNING)
            logging.getLogger('requests').setLevel(logging.WARNING)
            
            logger = logging.getLogger(__name__)
            logger.info(f"Logging configured - Level: {log_level}, Console: {enable_console}, File: {log_file}")
            
        except Exception as e:
            print(f"Error setting up logging: {e}")
            # Fallback to basic logging
            logging.basicConfig(
                level=getattr(logging, log_level.upper()),
                format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
    
    @staticmethod
    def setup_logging_from_config(config_file: str) -> None:
        """Setup logging from a configuration file."""
        try:
            import yaml
            
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Create logs directory if specified
            if 'handlers' in config:
                for handler_name, handler_config in config['handlers'].items():
                    if 'filename' in handler_config:
                        log_path = Path(handler_config['filename'])
                        log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Apply configuration
            logging.config.dictConfig(config)
            
            logger = logging.getLogger(__name__)
            logger.info(f"Logging configured from file: {config_file}")
            
        except Exception as e:
            print(f"Error loading logging config from {config_file}: {e}")
            # Fallback to default configuration
            LoggingUtils.setup_logging()
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a logger with the specified name."""
        return logging.getLogger(name)
    
    @staticmethod
    def log_function_call(func):
        """Decorator to log function calls."""
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)
            logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func.__name__} returned: {result}")
                return result
            except Exception as e:
                logger.error(f"{func.__name__} raised exception: {e}")
                raise
        return wrapper
    
    @staticmethod
    def log_execution_time(func):
        """Decorator to log function execution time."""
        import time
        
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"{func.__name__} executed in {execution_time:.4f} seconds")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"{func.__name__} failed after {execution_time:.4f} seconds: {e}")
                raise
        return wrapper
    
    @staticmethod
    def create_structured_log(logger: logging.Logger, level: str, message: str, **kwargs) -> None:
        """Create a structured log entry with additional fields."""
        record = logger.makeRecord(
            logger.name,
            getattr(logging, level.upper()),
            '',
            0,
            message,
            (),
            None
        )
        record.extra_fields = kwargs
        logger.handle(record)
    
    @staticmethod
    def log_database_operation(operation: str, table: str, record_id: Optional[str] = None, **kwargs):
        """Log database operations."""
        logger = logging.getLogger('database')
        extra_fields = {
            'operation': operation,
            'table': table,
            'record_id': record_id,
            **kwargs
        }
        LoggingUtils.create_structured_log(logger, 'INFO', f"Database {operation} on {table}", **extra_fields)
    
    @staticmethod
    def log_file_operation(operation: str, file_path: str, file_size: Optional[int] = None, **kwargs):
        """Log file operations."""
        logger = logging.getLogger('file_operations')
        extra_fields = {
            'operation': operation,
            'file_path': file_path,
            'file_size': file_size,
            **kwargs
        }
        LoggingUtils.create_structured_log(logger, 'INFO', f"File {operation}: {file_path}", **extra_fields)
    
    @staticmethod
    def log_api_request(method: str, endpoint: str, status_code: int, response_time: float, **kwargs):
        """Log API requests."""
        logger = logging.getLogger('api')
        extra_fields = {
            'method': method,
            'endpoint': endpoint,
            'status_code': status_code,
            'response_time': response_time,
            **kwargs
        }
        level = 'ERROR' if status_code >= 400 else 'INFO'
        LoggingUtils.create_structured_log(logger, level, f"{method} {endpoint} - {status_code}", **extra_fields)
    
    @staticmethod
    def log_security_event(event_type: str, user_id: Optional[str] = None, ip_address: Optional[str] = None, **kwargs):
        """Log security events."""
        logger = logging.getLogger('security')
        extra_fields = {
            'event_type': event_type,
            'user_id': user_id,
            'ip_address': ip_address,
            **kwargs
        }
        LoggingUtils.create_structured_log(logger, 'WARNING', f"Security event: {event_type}", **extra_fields)
    
    @staticmethod
    def rotate_logs(log_directory: str = 'logs') -> None:
        """Manually rotate log files."""
        try:
            log_dir = Path(log_directory)
            if not log_dir.exists():
                return
            
            for log_file in log_dir.glob('*.log'):
                if log_file.stat().st_size > 10 * 1024 * 1024:  # 10MB
                    # Create backup
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    backup_file = log_file.with_suffix(f'.{timestamp}.log')
                    log_file.rename(backup_file)
                    
                    # Create new log file
                    log_file.touch()
                    
                    logger = logging.getLogger(__name__)
                    logger.info(f"Rotated log file: {log_file} -> {backup_file}")
        
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error rotating logs: {e}")
    
    @staticmethod
    def cleanup_old_logs(log_directory: str = 'logs', days_to_keep: int = 30) -> None:
        """Clean up old log files."""
        try:
            from datetime import timedelta
            
            log_dir = Path(log_directory)
            if not log_dir.exists():
                return
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            for log_file in log_dir.glob('*.log.*'):
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    log_file.unlink()
                    
                    logger = logging.getLogger(__name__)
                    logger.info(f"Cleaned up old log file: {log_file}")
        
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error cleaning up old logs: {e}")
    
    @staticmethod
    def get_log_statistics(log_file: str) -> Dict[str, Any]:
        """Get statistics from a log file."""
        try:
            stats = {
                'total_lines': 0,
                'level_counts': {},
                'error_count': 0,
                'warning_count': 0,
                'info_count': 0,
                'debug_count': 0
            }
            
            with open(log_file, 'r') as f:
                for line in f:
                    stats['total_lines'] += 1
                    
                    # Simple parsing of log levels
                    if '[ERROR]' in line:
                        stats['error_count'] += 1
                        stats['level_counts']['ERROR'] = stats['level_counts'].get('ERROR', 0) + 1
                    elif '[WARNING]' in line:
                        stats['warning_count'] += 1
                        stats['level_counts']['WARNING'] = stats['level_counts'].get('WARNING', 0) + 1
                    elif '[INFO]' in line:
                        stats['info_count'] += 1
                        stats['level_counts']['INFO'] = stats['level_counts'].get('INFO', 0) + 1
                    elif '[DEBUG]' in line:
                        stats['debug_count'] += 1
                        stats['level_counts']['DEBUG'] = stats['level_counts'].get('DEBUG', 0) + 1
            
            return stats
        
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting log statistics for {log_file}: {e}")
            return {} 