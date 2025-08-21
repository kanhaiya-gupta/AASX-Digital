"""
Log Manager

Centralized log management system for the AAS Data Modeling Engine monitoring system.
Handles log configuration, rotation, filtering, and integration with monitoring components.
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
import json
import threading
import queue


@dataclass
class LogConfig:
    """Log configuration settings"""
    level: str = "INFO"
    format: str = "json"  # json, csv, plain, logstash, custom
    output: str = "file"  # file, console, both
    file_path: Optional[Path] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    rotation: str = "size"  # size, time, both
    rotation_interval: str = "1 day"  # 1 hour, 1 day, 1 week
    compression: bool = True
    retention_days: int = 30
    enable_metrics: bool = True
    enable_audit: bool = True
    custom_formatter: Optional[str] = None


class LogManager:
    """Centralized log management system"""
    
    def __init__(self, config):
        """Initialize log manager"""
        self.config = config
        self.loggers: Dict[str, logging.Logger] = {}
        self.handlers: Dict[str, logging.Handler] = {}
        self.formatters: Dict[str, logging.Formatter] = {}
        self.log_queue = queue.Queue()
        self.log_metrics = {
            "total_logs": 0,
            "logs_by_level": {},
            "logs_by_logger": {},
            "logs_by_hour": {},
            "errors": 0,
            "warnings": 0
        }
        
        # Setup default configuration
        self._setup_default_config()
        self._setup_formatters()
        self._setup_handlers()
        
        # Start log processing thread
        self._start_log_processor()
    
    def _setup_default_config(self):
        """Setup default logging configuration"""
        if not hasattr(self.config, 'logging'):
            self.config.logging = LogConfig()
        
        # Set default file path if not specified
        if not self.config.logging.file_path:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            self.config.logging.file_path = log_dir / "aas_engine.log"
    
    def _setup_formatters(self):
        """Setup log formatters"""
        from .log_formatters import (
            JSONFormatter, CSVFormatter, PlainTextFormatter, 
            LogstashFormatter, CustomFormatter
        )
        
        self.formatters = {
            "json": JSONFormatter(),
            "csv": CSVFormatter(),
            "plain": PlainTextFormatter(),
            "logstash": LogstashFormatter(),
            "custom": CustomFormatter(self.config.logging.custom_formatter)
        }
    
    def _setup_handlers(self):
        """Setup log handlers"""
        # File handler with rotation
        if self.config.logging.output in ["file", "both"]:
            self._setup_file_handler()
        
        # Console handler
        if self.config.logging.output in ["console", "both"]:
            self._setup_console_handler()
        
        # Error handler for critical errors
        self._setup_error_handler()
    
    def _setup_file_handler(self):
        """Setup file handler with rotation"""
        log_file = self.config.logging.file_path
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        if self.config.logging.rotation == "size":
            handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=self.config.logging.max_file_size,
                backupCount=self.config.logging.backup_count
            )
        elif self.config.logging.rotation == "time":
            interval = self._parse_rotation_interval(self.config.logging.rotation_interval)
            handler = logging.handlers.TimedRotatingFileHandler(
                log_file,
                when=interval["unit"],
                interval=interval["value"],
                backupCount=self.config.logging.backup_count
            )
        else:  # both
            handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=self.config.logging.max_file_size,
                backupCount=self.config.logging.backup_count
            )
        
        # Create a custom handler that updates metrics
        metrics_handler = MetricsUpdateHandler(self, handler)
        metrics_handler.setLevel(self._get_log_level(self.config.logging.level))
        metrics_handler.setFormatter(self.formatters[self.config.logging.format])
        
        self.handlers["file"] = metrics_handler
    
    def _setup_console_handler(self):
        """Setup console handler"""
        handler = logging.StreamHandler(sys.stdout)
        
        # Create a custom handler that updates metrics
        metrics_handler = MetricsUpdateHandler(self, handler)
        metrics_handler.setLevel(self._get_log_level(self.config.logging.level))
        metrics_handler.setFormatter(self.formatters[self.config.logging.format])
        
        self.handlers["console"] = metrics_handler
    
    def _setup_error_handler(self):
        """Setup error handler for critical errors"""
        error_file = self.config.logging.file_path.parent / "errors.log"
        handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=self.config.logging.max_file_size,
            backupCount=self.config.logging.backup_count
        )
        
        # Create a custom handler that updates metrics
        metrics_handler = MetricsUpdateHandler(self, handler)
        metrics_handler.setLevel(logging.ERROR)
        metrics_handler.setFormatter(self.formatters[self.config.logging.format])
        
        self.handlers["error"] = metrics_handler
    
    def _parse_rotation_interval(self, interval_str: str) -> Dict[str, Any]:
        """Parse rotation interval string"""
        parts = interval_str.split()
        if len(parts) != 2:
            return {"unit": "D", "value": 1}
        
        value = int(parts[0])
        unit = parts[1][0].upper()
        
        # Map units to logging constants
        unit_map = {
            "H": "H",  # Hour
            "D": "D",  # Day
            "W": "W0", # Week
            "M": "MIDNIGHT"  # Month
        }
        
        return {
            "unit": unit_map.get(unit, "D"),
            "value": value
        }
    
    def _get_log_level(self, level_str: str) -> int:
        """Get logging level from string"""
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return level_map.get(level_str.upper(), logging.INFO)
    
    def _start_log_processor(self):
        """Start background log processing thread"""
        def process_logs():
            while True:
                try:
                    log_record = self.log_queue.get(timeout=1)
                    if log_record is None:  # Shutdown signal
                        break
                    
                    self._process_log_record(log_record)
                    self.log_queue.task_done()
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    # Don't let log processing errors break the system
                    print(f"Log processing error: {e}")
        
        self.log_thread = threading.Thread(target=process_logs, daemon=True)
        self.log_thread.start()
    
    def _process_log_record(self, log_record: logging.LogRecord):
        """Process a log record and update metrics"""
        # Update metrics
        self.log_metrics["total_logs"] += 1
        
        # Count by level
        level_name = logging.getLevelName(log_record.levelno)
        self.log_metrics["logs_by_level"][level_name] = \
            self.log_metrics["logs_by_level"].get(level_name, 0) + 1
        
        # Count by logger
        logger_name = log_record.name
        self.log_metrics["logs_by_logger"][logger_name] = \
            self.log_metrics["logs_by_logger"].get(logger_name, 0) + 1
        
        # Count by hour
        hour = datetime.now().hour
        self.log_metrics["logs_by_hour"][hour] = \
            self.log_metrics["logs_by_hour"].get(hour, 0) + 1
        
        # Count errors and warnings
        if log_record.levelno >= logging.ERROR:
            self.log_metrics["errors"] += 1
        elif log_record.levelno >= logging.WARNING:
            self.log_metrics["warnings"] += 1
    
    def get_logger(self, name: str, level: Optional[str] = None) -> logging.Logger:
        """Get or create a logger with the specified name"""
        if name in self.loggers:
            return self.loggers[name]
        
        # Create new logger
        logger = logging.getLogger(name)
        
        # Set level
        if level:
            logger.setLevel(self._get_log_level(level))
        else:
            logger.setLevel(self._get_log_level(self.config.logging.level))
        
        # Add handlers
        for handler in self.handlers.values():
            logger.addHandler(handler)
        
        # Prevent propagation to root logger
        logger.propagate = False
        
        # Store logger
        self.loggers[name] = logger
        
        return logger
    
    def set_log_level(self, logger_name: str, level: str):
        """Set log level for a specific logger"""
        if logger_name in self.loggers:
            self.loggers[logger_name].setLevel(self._get_log_level(level))
    
    def set_global_log_level(self, level: str):
        """Set global log level for all loggers"""
        self.config.logging.level = level
        level_int = self._get_log_level(level)
        
        # Update all handlers
        for handler in self.handlers.values():
            handler.setLevel(level_int)
        
        # Update all loggers
        for logger in self.loggers.values():
            logger.setLevel(level_int)
    
    def add_handler(self, name: str, handler: logging.Handler):
        """Add a custom handler"""
        self.handlers[name] = handler
        
        # Add to all existing loggers
        for logger in self.loggers.values():
            logger.addHandler(handler)
    
    def remove_handler(self, name: str):
        """Remove a handler"""
        if name in self.handlers:
            handler = self.handlers.pop(name)
            
            # Remove from all loggers
            for logger in self.loggers.values():
                logger.removeHandler(handler)
    
    def get_log_metrics(self) -> Dict[str, Any]:
        """Get logging metrics"""
        return self.log_metrics.copy()
    
    def get_log_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get log summary for specified time period"""
        current_time = datetime.now()
        start_time = current_time - timedelta(hours=hours)
        
        # Filter metrics by time (this is a simplified approach)
        # In a real implementation, you'd store timestamps with each log entry
        
        summary = {
            "period_hours": hours,
            "total_logs": self.log_metrics["total_logs"],
            "logs_by_level": self.log_metrics["logs_by_level"],
            "logs_by_logger": self.log_metrics["logs_by_logger"],
            "errors": self.log_metrics["errors"],
            "warnings": self.log_metrics["warnings"],
            "log_files": self._get_log_files_info()
        }
        
        return summary
    
    def _get_log_files_info(self) -> List[Dict[str, Any]]:
        """Get information about log files"""
        log_dir = self.config.logging.file_path.parent
        log_files = []
        
        if log_dir.exists():
            for log_file in log_dir.glob("*.log*"):
                try:
                    stat = log_file.stat()
                    log_files.append({
                        "name": log_file.name,
                        "size_bytes": stat.st_size,
                        "size_mb": round(stat.st_size / (1024 * 1024), 2),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "path": str(log_file)
                    })
                except Exception:
                    continue
        
        return sorted(log_files, key=lambda x: x["modified"], reverse=True)
    
    def rotate_logs(self):
        """Manually trigger log rotation"""
        for handler in self.handlers.values():
            if hasattr(handler, 'doRollover'):
                try:
                    handler.doRollover()
                except Exception as e:
                    print(f"Log rotation failed: {e}")
    
    def cleanup_old_logs(self):
        """Clean up old log files based on retention policy"""
        if not self.config.logging.retention_days:
            return
        
        log_dir = self.config.logging.file_path.parent
        cutoff_time = datetime.now() - timedelta(days=self.config.logging.retention_days)
        
        if log_dir.exists():
            for log_file in log_dir.glob("*.log*"):
                try:
                    if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_time:
                        log_file.unlink()
                        print(f"Removed old log file: {log_file}")
                except Exception as e:
                    print(f"Failed to remove old log file {log_file}: {e}")
    
    def export_logs(self, format: str = "json", filepath: Optional[Path] = None) -> Path:
        """Export log metrics and configuration"""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"log_export_{timestamp}.{format}"
            filepath = self.config.export.export_directory / filename
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "config": {
                "level": self.config.logging.level,
                "format": self.config.logging.format,
                "output": self.config.logging.output,
                "rotation": self.config.logging.rotation,
                "retention_days": self.config.logging.retention_days
            },
            "metrics": self.log_metrics,
            "loggers": list(self.loggers.keys()),
            "handlers": list(self.handlers.keys()),
            "formatters": list(self.formatters.keys())
        }
        
        if format.lower() == "json":
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
        elif format.lower() == "csv":
            import csv
            # Flatten the data for CSV export
            flat_data = []
            for key, value in export_data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        flat_data.append({"category": key, "key": sub_key, "value": str(sub_value)})
                else:
                    flat_data.append({"category": "general", "key": key, "value": str(value)})
            
            with open(filepath, 'w', newline='') as f:
                if flat_data:
                    writer = csv.DictWriter(f, fieldnames=flat_data[0].keys())
                    writer.writeheader()
                    writer.writerows(flat_data)
        
        return filepath
    
    def shutdown(self):
        """Shutdown log manager"""
        # Send shutdown signal to log processor
        self.log_queue.put(None)
        
        # Wait for thread to finish
        if hasattr(self, 'log_thread'):
            self.log_thread.join(timeout=5)
        
        # Close all handlers
        for handler in self.handlers.values():
            handler.close()
        
        # Clear loggers
        self.loggers.clear()
        self.handlers.clear()


class MetricsUpdateHandler(logging.Handler):
    """Custom handler that updates metrics when logs are emitted"""
    
    def __init__(self, log_manager, wrapped_handler):
        super().__init__()
        self.log_manager = log_manager
        self.wrapped_handler = wrapped_handler
    
    def emit(self, record):
        """Emit a log record and update metrics"""
        try:
            # Update metrics first
            self.log_manager._process_log_record(record)
            
            # Then emit to the wrapped handler
            self.wrapped_handler.emit(record)
        except Exception as e:
            # Don't let metrics errors break logging
            print(f"Metrics update error: {e}")
            # Still try to emit to wrapped handler
            try:
                self.wrapped_handler.emit(record)
            except Exception:
                pass
    
    def setFormatter(self, formatter):
        """Set formatter on wrapped handler"""
        self.wrapped_handler.setFormatter(formatter)
    
    def setLevel(self, level):
        """Set level on wrapped handler"""
        self.wrapped_handler.setLevel(level)
