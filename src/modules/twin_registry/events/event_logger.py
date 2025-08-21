"""
Event Logger for Twin Registry Population
Provides comprehensive logging and monitoring for the event system
"""

import logging
import json
import sqlite3
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, asdict

from .event_types import Event, EventType, EventPriority, EventStatus

logger = logging.getLogger(__name__)


@dataclass
class LogEntry:
    """Log entry for events"""
    log_id: str
    event_id: str
    event_type: str
    event_priority: str
    timestamp: datetime
    source: str
    message: str
    details: Dict[str, Any]
    log_level: str
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    org_id: Optional[str] = None


class EventLogger:
    """Comprehensive event logging system"""
    
    def __init__(self, db_path: Optional[Path] = None, max_entries: int = 10000):
        self.db_path = db_path or Path("data/event_logs.db")
        self.max_entries = max_entries
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Configure logging
        self._setup_logging()
    
    def _init_database(self) -> None:
        """Initialize the event logging database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create event logs table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS event_logs (
                        log_id TEXT PRIMARY KEY,
                        event_id TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        event_priority TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        source TEXT NOT NULL,
                        message TEXT NOT NULL,
                        details TEXT NOT NULL,
                        log_level TEXT NOT NULL,
                        correlation_id TEXT,
                        user_id TEXT,
                        org_id TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for better query performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_event_logs_timestamp 
                    ON event_logs(timestamp)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_event_logs_event_type 
                    ON event_logs(event_type)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_event_logs_log_level 
                    ON event_logs(log_level)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_event_logs_correlation_id 
                    ON event_logs(correlation_id)
                """)
                
                conn.commit()
                logger.info(f"Event logging database initialized: {self.db_path}")
                
        except Exception as e:
            logger.error(f"Failed to initialize event logging database: {e}")
            raise
    
    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create file handler
        log_file = self.db_path.parent / "event_system.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        # Get root logger and add handlers
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        root_logger.setLevel(logging.DEBUG)
    
    async def log_event(
        self,
        event: Event,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        log_level: str = "INFO",
        correlation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None
    ) -> str:
        """Log an event with comprehensive details"""
        try:
            import uuid
            
            log_id = str(uuid.uuid4())
            timestamp = datetime.now(timezone.utc)
            
            # Prepare log entry
            log_entry = LogEntry(
                log_id=log_id,
                event_id=event.event_id,
                event_type=event.event_type.value,
                event_priority=event.event_priority.value,
                timestamp=timestamp,
                source=event.source,
                message=message,
                details=details or {},
                log_level=log_level.upper(),
                correlation_id=correlation_id,
                user_id=user_id,
                org_id=org_id
            )
            
            # Store in database
            await self._store_log_entry(log_entry)
            
            # Also log to standard logging system
            self._log_to_standard_system(log_entry)
            
            logger.debug(f"Event logged successfully: {log_id}")
            return log_id
            
        except Exception as e:
            logger.error(f"Failed to log event: {e}")
            raise
    
    async def _store_log_entry(self, log_entry: LogEntry) -> None:
        """Store log entry in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert log entry
                cursor.execute("""
                    INSERT INTO event_logs (
                        log_id, event_id, event_type, event_priority, timestamp,
                        source, message, details, log_level, correlation_id,
                        user_id, org_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    log_entry.log_id, log_entry.event_id, log_entry.event_type,
                    log_entry.event_priority, log_entry.timestamp.isoformat(),
                    log_entry.source, log_entry.message, json.dumps(log_entry.details),
                    log_entry.log_level, log_entry.correlation_id,
                    log_entry.user_id, log_entry.org_id
                ))
                
                # Cleanup old entries if exceeding max limit
                await self._cleanup_old_entries(cursor)
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to store log entry: {e}")
            raise
    
    def _log_to_standard_system(self, log_entry: LogEntry) -> None:
        """Log to standard Python logging system"""
        log_message = f"[{log_entry.event_type}] {log_entry.message}"
        
        if log_entry.log_level == "DEBUG":
            logger.debug(log_message, extra={"event_details": log_entry.details})
        elif log_entry.log_level == "INFO":
            logger.info(log_message, extra={"event_details": log_entry.details})
        elif log_entry.log_level == "WARNING":
            logger.warning(log_message, extra={"event_details": log_entry.details})
        elif log_entry.log_level == "ERROR":
            logger.error(log_message, extra={"event_details": log_entry.details})
        elif log_entry.log_level == "CRITICAL":
            logger.critical(log_message, extra={"event_details": log_entry.details})
    
    async def _cleanup_old_entries(self, cursor: sqlite3.Cursor) -> None:
        """Cleanup old log entries to maintain performance"""
        try:
            # Count total entries
            cursor.execute("SELECT COUNT(*) FROM event_logs")
            total_count = cursor.fetchone()[0]
            
            if total_count > self.max_entries:
                # Delete oldest entries
                delete_count = total_count - self.max_entries + 1000  # Keep some buffer
                cursor.execute("""
                    DELETE FROM event_logs 
                    WHERE log_id IN (
                        SELECT log_id FROM event_logs 
                        ORDER BY timestamp ASC 
                        LIMIT ?
                    )
                """, (delete_count,))
                
                logger.info(f"Cleaned up {delete_count} old log entries")
                
        except Exception as e:
            logger.warning(f"Failed to cleanup old log entries: {e}")
    
    async def get_logs(
        self,
        event_type: Optional[str] = None,
        log_level: Optional[str] = None,
        correlation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[LogEntry]:
        """Retrieve logs with filtering options"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build query
                query = "SELECT * FROM event_logs WHERE 1=1"
                params = []
                
                if event_type:
                    query += " AND event_type = ?"
                    params.append(event_type)
                
                if log_level:
                    query += " AND log_level = ?"
                    params.append(log_level)
                
                if correlation_id:
                    query += " AND correlation_id = ?"
                    params.append(correlation_id)
                
                if user_id:
                    query += " AND user_id = ?"
                    params.append(user_id)
                
                if org_id:
                    query += " AND org_id = ?"
                    params.append(org_id)
                
                if start_time:
                    query += " AND timestamp >= ?"
                    params.append(start_time.isoformat())
                
                if end_time:
                    query += " AND timestamp <= ?"
                    params.append(end_time.isoformat())
                
                # Add ordering and pagination
                query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                # Execute query
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Convert to LogEntry objects
                log_entries = []
                for row in rows:
                    try:
                        log_entry = LogEntry(
                            log_id=row[0],
                            event_id=row[1],
                            event_type=row[2],
                            event_priority=row[3],
                            timestamp=datetime.fromisoformat(row[4]),
                            source=row[5],
                            message=row[6],
                            details=json.loads(row[7]),
                            log_level=row[8],
                            correlation_id=row[9],
                            user_id=row[10],
                            org_id=row[11]
                        )
                        log_entries.append(log_entry)
                    except Exception as e:
                        logger.warning(f"Failed to parse log entry row: {e}")
                
                return log_entries
                
        except Exception as e:
            logger.error(f"Failed to retrieve logs: {e}")
            raise
    
    async def get_log_statistics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get log statistics for monitoring"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build time filter
                time_filter = ""
                params = []
                if start_time and end_time:
                    time_filter = "WHERE timestamp BETWEEN ? AND ?"
                    params = [start_time.isoformat(), end_time.isoformat()]
                elif start_time:
                    time_filter = "WHERE timestamp >= ?"
                    params = [start_time.isoformat()]
                elif end_time:
                    time_filter = "WHERE timestamp <= ?"
                    params = [end_time.isoformat()]
                
                # Get total count
                cursor.execute(f"SELECT COUNT(*) FROM event_logs {time_filter}", params)
                total_logs = cursor.fetchone()[0]
                
                # Get count by event type
                cursor.execute(f"""
                    SELECT event_type, COUNT(*) 
                    FROM event_logs {time_filter}
                    GROUP BY event_type
                """, params)
                event_type_counts = dict(cursor.fetchall())
                
                # Get count by log level
                cursor.execute(f"""
                    SELECT log_level, COUNT(*) 
                    FROM event_logs {time_filter}
                    GROUP BY log_level
                """, params)
                log_level_counts = dict(cursor.fetchall())
                
                # Get count by priority
                cursor.execute(f"""
                    SELECT event_priority, COUNT(*) 
                    FROM event_logs {time_filter}
                    GROUP BY event_priority
                """, params)
                priority_counts = dict(cursor.fetchall())
                
                # Get recent activity (last 24 hours)
                recent_time = datetime.now(timezone.utc).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                cursor.execute("""
                    SELECT COUNT(*) FROM event_logs 
                    WHERE timestamp >= ?
                """, [recent_time.isoformat()])
                recent_logs = cursor.fetchone()[0]
                
                return {
                    "total_logs": total_logs,
                    "recent_logs_24h": recent_logs,
                    "event_type_counts": event_type_counts,
                    "log_level_counts": log_level_counts,
                    "priority_counts": priority_counts,
                    "time_range": {
                        "start": start_time.isoformat() if start_time else None,
                        "end": end_time.isoformat() if end_time else None
                    }
                }
                
        except Exception as e:
            logger.error(f"Failed to get log statistics: {e}")
            raise
    
    async def export_logs(
        self,
        output_path: Path,
        format: str = "json",
        **filter_kwargs
    ) -> bool:
        """Export logs to file in various formats"""
        try:
            logs = await self.get_logs(**filter_kwargs)
            
            if format.lower() == "json":
                # Export as JSON
                export_data = []
                for log in logs:
                    log_dict = asdict(log)
                    log_dict["timestamp"] = log_dict["timestamp"].isoformat()
                    export_data.append(log_dict)
                
                with open(output_path, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
                    
            elif format.lower() == "csv":
                # Export as CSV
                import csv
                with open(output_path, 'w', newline='') as f:
                    if logs:
                        writer = csv.DictWriter(f, fieldnames=asdict(logs[0]).keys())
                        writer.writeheader()
                        for log in logs:
                            log_dict = asdict(log)
                            log_dict["timestamp"] = log_dict["timestamp"].isoformat()
                            writer.writerow(log_dict)
                            
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            logger.info(f"Logs exported successfully to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export logs: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Cleanup event logger resources"""
        try:
            # Close any open connections
            logger.info("Event logger cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during event logger cleanup: {e}")
            raise
