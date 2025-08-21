"""
Log Formatters

Various log formatters for different output formats including JSON, CSV, plain text,
Logstash, and custom formats for the monitoring system.
"""

import logging
import json
import csv
import re
from datetime import datetime
from typing import Any, Dict, Optional, List
from pathlib import Path


class BaseFormatter(logging.Formatter):
    """Base formatter with common functionality"""
    
    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None):
        super().__init__(fmt, datefmt)
        self.timestamp_format = "%Y-%m-%d %H:%M:%S"
    
    def formatTime(self, record: logging.LogRecord, datefmt: Optional[str] = None) -> str:
        """Format timestamp"""
        if datefmt:
            return datetime.fromtimestamp(record.created).strftime(datefmt)
        return datetime.fromtimestamp(record.created).strftime(self.timestamp_format)
    
    def _extract_extra_fields(self, record: logging.LogRecord) -> Dict[str, Any]:
        """Extract extra fields from log record"""
        extra_fields = {}
        
        # Extract fields from record attributes
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 'exc_text', 
                          'stack_info']:
                extra_fields[key] = value
        
        return extra_fields


class JSONFormatter(BaseFormatter):
    """JSON formatter for structured logging"""
    
    def __init__(self, include_timestamp: bool = True, include_level: bool = True,
                 include_logger: bool = True, include_message: bool = True,
                 flatten_extra: bool = False, indent: Optional[int] = None):
        super().__init__()
        self.include_timestamp = include_timestamp
        self.include_level = include_level
        self.include_logger = include_logger
        self.include_message = include_message
        self.flatten_extra = flatten_extra
        self.indent = indent
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {}
        
        # Add basic fields
        if self.include_timestamp:
            log_data['timestamp'] = self.formatTime(record)
        
        if self.include_level:
            log_data['level'] = record.levelname
        
        if self.include_logger:
            log_data['logger'] = record.name
        
        if self.include_message:
            log_data['message'] = record.getMessage()
        
        # Add location information
        log_data['module'] = record.module
        log_data['function'] = record.funcName
        log_data['line'] = record.lineno
        
        # Add process/thread information
        log_data['process'] = record.process
        log_data['thread'] = record.thread
        
        # Add extra fields
        extra_fields = self._extract_extra_fields(record)
        if extra_fields:
            if self.flatten_extra:
                log_data.update(extra_fields)
            else:
                log_data['extra'] = extra_fields
        
        # Add exception information
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': self.formatException(record.exc_info)
            }
        
        # Add stack information
        if record.stack_info:
            log_data['stack_info'] = self.formatStack(record.stack_info)
        
        # Convert to JSON
        try:
            return json.dumps(log_data, default=str, indent=self.indent)
        except (TypeError, ValueError):
            # Fallback to basic JSON if serialization fails
            fallback_data = {
                'timestamp': self.formatTime(record),
                'level': record.levelname,
                'logger': record.name,
                'message': str(record.getMessage()),
                'error': 'JSON serialization failed'
            }
            return json.dumps(fallback_data, indent=self.indent)


class CSVFormatter(BaseFormatter):
    """CSV formatter for tabular log output"""
    
    def __init__(self, fields: Optional[List[str]] = None, delimiter: str = ',',
                 include_headers: bool = True):
        super().__init__()
        self.fields = fields or [
            'timestamp', 'level', 'logger', 'message', 'module', 'function', 'line'
        ]
        self.delimiter = delimiter
        self.include_headers = include_headers
        self._headers_written = False
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as CSV"""
        # Prepare data
        data = {}
        
        # Map record fields
        field_mapping = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': self._escape_csv_field(record.getMessage()),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process': record.process,
            'thread': record.thread,
            'pathname': record.pathname,
            'filename': record.filename
        }
        
        # Add extra fields
        extra_fields = self._extract_extra_fields(record)
        for key, value in extra_fields.items():
            field_mapping[key] = self._escape_csv_field(str(value))
        
        # Build CSV row
        row_data = []
        for field in self.fields:
            value = field_mapping.get(field, '')
            row_data.append(str(value))
        
        # Add headers if needed
        if self.include_headers and not self._headers_written:
            header_row = self.delimiter.join(self.fields)
            self._headers_written = True
            return header_row + '\n' + self.delimiter.join(row_data)
        
        return self.delimiter.join(row_data)
    
    def _escape_csv_field(self, field: str) -> str:
        """Escape CSV field if it contains delimiter or quotes"""
        if self.delimiter in field or '"' in field or '\n' in field:
            escaped_field = field.replace('"', '""')
            return f'"{escaped_field}"'
        return field


class PlainTextFormatter(BaseFormatter):
    """Plain text formatter for human-readable logs"""
    
    def __init__(self, format_string: Optional[str] = None, 
                 include_extra: bool = True, colorize: bool = False):
        if format_string is None:
            format_string = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        
        super().__init__(format_string)
        self.include_extra = include_extra
        self.colorize = colorize
        
        # ANSI color codes
        self.colors = {
            'DEBUG': '\033[36m',      # Cyan
            'INFO': '\033[32m',       # Green
            'WARNING': '\033[33m',    # Yellow
            'ERROR': '\033[31m',      # Red
            'CRITICAL': '\033[35m',   # Magenta
            'RESET': '\033[0m'        # Reset
        }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as plain text"""
        # Get base formatted message
        formatted = super().format(record)
        
        # Add extra fields if requested
        if self.include_extra:
            extra_fields = self._extract_extra_fields(record)
            if extra_fields:
                extra_str = ' '.join([f"{k}={v}" for k, v in extra_fields.items()])
                formatted += f" | {extra_str}"
        
        # Add exception information
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        # Colorize if requested
        if self.colorize and record.levelname in self.colors:
            formatted = f"{self.colors[record.levelname]}{formatted}{self.colors['RESET']}"
        
        return formatted


class LogstashFormatter(BaseFormatter):
    """Logstash-compatible formatter for ELK stack integration"""
    
    def __init__(self, service_name: str = "aas-engine", environment: str = "development",
                 version: str = "1.0.0", include_hostname: bool = True):
        super().__init__()
        self.service_name = service_name
        self.environment = environment
        self.version = version
        self.include_hostname = include_hostname
        
        # Get hostname if requested
        self.hostname = None
        if self.include_hostname:
            try:
                import socket
                self.hostname = socket.gethostname()
            except Exception:
                self.hostname = "unknown"
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record for Logstash"""
        # Create Logstash-compatible structure
        logstash_data = {
            "@timestamp": self.formatTime(record),
            "@version": "1",
            "message": record.getMessage(),
            "logger": record.name,
            "level": record.levelname,
            "level_number": record.levelno,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "pathname": record.pathname,
            "filename": record.filename,
            "process": record.process,
            "thread": record.thread,
            "service": {
                "name": self.service_name,
                "environment": self.environment,
                "version": self.version
            }
        }
        
        # Add hostname if available
        if self.hostname:
            logstash_data["host"] = self.hostname
        
        # Add extra fields
        extra_fields = self._extract_extra_fields(record)
        if extra_fields:
            logstash_data["extra"] = extra_fields
        
        # Add exception information
        if record.exc_info:
            logstash_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info)
            }
        
        # Add stack information
        if record.stack_info:
            logstash_data["stack_info"] = self.formatStack(record.stack_info)
        
        # Convert to JSON
        try:
            return json.dumps(logstash_data, default=str)
        except (TypeError, ValueError):
            # Fallback to basic structure
            fallback_data = {
                "@timestamp": self.formatTime(record),
                "@version": "1",
                "message": str(record.getMessage()),
                "level": record.levelname,
                "error": "Logstash serialization failed"
            }
            return json.dumps(fallback_data)


class CustomFormatter(BaseFormatter):
    """Custom formatter with configurable template"""
    
    def __init__(self, template: Optional[str] = None, 
                 field_mapping: Optional[Dict[str, str]] = None):
        super().__init__()
        self.template = template or "{timestamp} [{level}] {logger}: {message}"
        self.field_mapping = field_mapping or {}
        
        # Compile template for performance
        self._compiled_template = self._compile_template()
    
    def _compile_template(self):
        """Compile template for efficient formatting"""
        # Find all placeholders in template
        placeholders = re.findall(r'\{(\w+)\}', self.template)
        
        # Create a function that replaces placeholders
        def format_record(record, extra_fields):
            result = self.template
            
            # Replace each placeholder
            for placeholder in placeholders:
                value = self._get_field_value(record, placeholder, extra_fields)
                result = result.replace(f"{{{placeholder}}}", str(value))
            
            return result
        
        return format_record
    
    def _get_field_value(self, record: logging.LogRecord, field: str, 
                         extra_fields: Dict[str, Any]) -> Any:
        """Get value for a field from record or extra fields"""
        # Check field mapping first
        if field in self.field_mapping:
            field = self.field_mapping[field]
        
        # Standard record fields
        if field == 'timestamp':
            return self.formatTime(record)
        elif field == 'level':
            return record.levelname
        elif field == 'logger':
            return record.name
        elif field == 'message':
            return record.getMessage()
        elif field == 'module':
            return record.module
        elif field == 'function':
            return record.funcName
        elif field == 'line':
            return record.lineno
        elif field == 'process':
            return record.process
        elif field == 'thread':
            return record.thread
        elif field == 'pathname':
            return record.pathname
        elif field == 'filename':
            return record.filename
        elif field == 'created':
            return record.created
        elif field == 'msecs':
            return record.msecs
        elif field == 'relativeCreated':
            return record.relativeCreated
        elif field == 'threadName':
            return record.threadName
        elif field == 'processName':
            return record.processName
        
        # Check extra fields
        if field in extra_fields:
            return extra_fields[field]
        
        # Return empty string for unknown fields
        return ""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record using custom template"""
        extra_fields = self._extract_extra_fields(record)
        return self._compiled_template(record, extra_fields)


class MultiFormatter(BaseFormatter):
    """Formatter that applies multiple formatters and combines results"""
    
    def __init__(self, formatters: List[BaseFormatter], separator: str = "\n"):
        super().__init__()
        self.formatters = formatters
        self.separator = separator
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record using multiple formatters"""
        formatted_parts = []
        
        for formatter in self.formatters:
            try:
                formatted_part = formatter.format(record)
                formatted_parts.append(formatted_part)
            except Exception as e:
                # Skip failed formatters
                formatted_parts.append(f"Formatter error: {e}")
        
        return self.separator.join(formatted_parts)


class ConditionalFormatter(BaseFormatter):
    """Formatter that applies different formatters based on conditions"""
    
    def __init__(self, conditions: List[tuple]):
        """
        Initialize with list of (condition, formatter) tuples.
        Condition should be a callable that takes a record and returns bool.
        """
        super().__init__()
        self.conditions = conditions
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record using the first matching formatter"""
        for condition, formatter in self.conditions:
            try:
                if condition(record):
                    return formatter.format(record)
            except Exception:
                continue
        
        # Fallback to base formatter if no conditions match
        return super().format(record)


# Factory function for creating formatters
def create_formatter(formatter_type: str, **kwargs) -> BaseFormatter:
    """Factory function to create formatters"""
    formatter_map = {
        'json': JSONFormatter,
        'csv': CSVFormatter,
        'plain': PlainTextFormatter,
        'text': PlainTextFormatter,
        'logstash': LogstashFormatter,
        'custom': CustomFormatter
    }
    
    if formatter_type.lower() not in formatter_map:
        raise ValueError(f"Unknown formatter type: {formatter_type}")
    
    formatter_class = formatter_map[formatter_type.lower()]
    return formatter_class(**kwargs)


# Convenience functions
def json_formatter(**kwargs) -> JSONFormatter:
    """Create a JSON formatter"""
    return JSONFormatter(**kwargs)


def csv_formatter(**kwargs) -> CSVFormatter:
    """Create a CSV formatter"""
    return CSVFormatter(**kwargs)


def plain_text_formatter(**kwargs) -> PlainTextFormatter:
    """Create a plain text formatter"""
    return PlainTextFormatter(**kwargs)


def logstash_formatter(**kwargs) -> LogstashFormatter:
    """Create a Logstash formatter"""
    return LogstashFormatter(**kwargs)


def custom_formatter(template: str, **kwargs) -> CustomFormatter:
    """Create a custom formatter"""
    return CustomFormatter(template, **kwargs)
