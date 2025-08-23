"""
Event Logger for AI RAG Module.

This module implements event logging, persistence, querying, and analytics
for the AI RAG event system.
"""

import asyncio
import logging
import json
import sqlite3
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from pathlib import Path
import threading
from collections import defaultdict, deque
import gzip
import pickle

from .event_types import BaseEvent, EventCategory, EventPriority, EventStatus


class EventLogger:
    """
    Event logger for AI RAG module.
    
    This class provides:
    - Event persistence to database and files
    - Event querying and filtering
    - Event analytics and reporting
    - Event cleanup and archival
    - Performance monitoring
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the event logger."""
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
        
        # Database connection
        self.db_path = self.config.get("database_path", "ai_rag_events.db")
        self.db_connection: Optional[sqlite3.Connection] = None
        self.db_lock = threading.Lock()
        
        # File storage
        self.storage_dir = Path(self.config.get("storage_directory", "logs/events"))
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache
        self.event_cache: deque = deque(maxlen=self.config.get("cache_size", 1000))
        self.cache_lock = threading.Lock()
        
        # Performance metrics
        self.metrics = {
            "events_logged": 0,
            "events_queried": 0,
            "events_archived": 0,
            "events_deleted": 0,
            "database_operations": 0,
            "file_operations": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        # Initialize database
        self._init_database()
        
        # Start background tasks
        self.cleanup_task: Optional[asyncio.Task] = None
        self.archival_task: Optional[asyncio.Task] = None
        self.is_running = False
    
    async def start(self) -> None:
        """Start the event logger."""
        if self.is_running:
            self.logger.warning("Event logger is already running")
            return
        
        self.logger.info("Starting AI RAG Event Logger...")
        self.is_running = True
        
        # Start background tasks
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.archival_task = asyncio.create_task(self._archival_loop())
        
        self.logger.info("AI RAG Event Logger started successfully")
    
    async def stop(self) -> None:
        """Stop the event logger."""
        if not self.is_running:
            self.logger.warning("Event logger is not running")
            return
        
        self.logger.info("Stopping AI RAG Event Logger...")
        self.is_running = False
        
        # Cancel background tasks
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        if self.archival_task:
            self.archival_task.cancel()
            try:
                await self.archival_task
            except asyncio.CancelledError:
                pass
        
        # Close database connection
        self._close_database()
        
        self.logger.info("AI RAG Event Logger stopped successfully")
    
    async def log_event(self, event: BaseEvent) -> str:
        """
        Log an event to the system.
        
        Args:
            event: The event to log
            
        Returns:
            Event ID for tracking
        """
        try:
            # Add to cache
            with self.cache_lock:
                self.event_cache.append(event)
                self.metrics["events_logged"] += 1
            
            # Store to database
            await self._store_event_to_database(event)
            
            # Store to file (optional)
            if self.config.get("enable_file_logging", True):
                await self._store_event_to_file(event)
            
            self.logger.debug(f"Event logged: {event.event_type} (ID: {event.event_id})")
            return event.event_id
            
        except Exception as e:
            self.logger.error(f"Failed to log event: {e}")
            raise
    
    async def query_events(
        self,
        event_types: Optional[List[str]] = None,
        event_categories: Optional[List[EventCategory]] = None,
        priority_levels: Optional[List[EventPriority]] = None,
        source_components: Optional[List[str]] = None,
        target_components: Optional[List[str]] = None,
        project_ids: Optional[List[str]] = None,
        org_ids: Optional[List[str]] = None,
        date_range: Optional[Tuple[datetime, datetime]] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "created_at",
        order_direction: str = "DESC"
    ) -> List[Dict[str, Any]]:
        """
        Query events based on various criteria.
        
        Args:
            event_types: List of event types to filter by
            event_categories: List of event categories to filter by
            priority_levels: List of priority levels to filter by
            source_components: List of source components to filter by
            target_components: List of target components to filter by
            project_ids: List of project IDs to filter by
            org_ids: List of organization IDs to filter by
            date_range: Tuple of (start_date, end_date) to filter by
            limit: Maximum number of events to return
            offset: Number of events to skip
            order_by: Field to order by
            order_direction: Order direction (ASC or DESC)
            
        Returns:
            List of event dictionaries
        """
        try:
            # Check cache first
            cached_events = self._query_cache(
                event_types, event_categories, priority_levels,
                source_components, target_components, project_ids,
                org_ids, date_range
            )
            
            if len(cached_events) >= limit:
                self.metrics["cache_hits"] += 1
                return self._format_events(cached_events[offset:offset + limit])
            
            # Query database
            db_events = await self._query_database(
                event_types, event_categories, priority_levels,
                source_components, target_components, project_ids,
                org_ids, date_range, limit, offset, order_by, order_direction
            )
            
            self.metrics["events_queried"] += 1
            return db_events
            
        except Exception as e:
            self.logger.error(f"Failed to query events: {e}")
            return []
    
    async def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific event by ID.
        
        Args:
            event_id: ID of the event to retrieve
            
        Returns:
            Event dictionary if found, None otherwise
        """
        try:
            # Check cache first
            with self.cache_lock:
                for event in self.event_cache:
                    if event.event_id == event_id:
                        self.metrics["cache_hits"] += 1
                        return self._event_to_dict(event)
            
            # Query database
            db_event = await self._get_event_from_database(event_id)
            if db_event:
                self.metrics["cache_misses"] += 1
            
            return db_event
            
        except Exception as e:
            self.logger.error(f"Failed to get event by ID: {e}")
            return None
    
    async def get_event_statistics(
        self,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """
        Get event statistics for a given date range.
        
        Args:
            date_range: Tuple of (start_date, end_date) to analyze
            
        Returns:
            Dictionary containing event statistics
        """
        try:
            stats = {
                "total_events": 0,
                "events_by_type": {},
                "events_by_category": {},
                "events_by_priority": {},
                "events_by_source": {},
                "events_by_status": {},
                "events_by_hour": {},
                "events_by_day": {},
                "performance_metrics": {
                    "average_processing_time": 0.0,
                    "total_processing_time": 0.0,
                    "events_per_minute": 0.0
                }
            }
            
            # Get events for the date range
            events = await self.query_events(
                date_range=date_range,
                limit=10000  # Get more events for statistics
            )
            
            if not events:
                return stats
            
            stats["total_events"] = len(events)
            
            # Calculate statistics
            for event in events:
                # By type
                event_type = event.get("event_type", "unknown")
                stats["events_by_type"][event_type] = stats["events_by_type"].get(event_type, 0) + 1
                
                # By category
                event_category = event.get("event_category", "unknown")
                stats["events_by_category"][event_category] = stats["events_by_category"].get(event_category, 0) + 1
                
                # By priority
                priority = event.get("priority", "unknown")
                stats["events_by_priority"][priority] = stats["events_by_priority"].get(priority, 0) + 1
                
                # By source
                source = event.get("source", "unknown")
                stats["events_by_source"][source] = stats["events_by_source"].get(source, 0) + 1
                
                # By status
                status = event.get("status", "unknown")
                stats["events_by_status"][status] = stats["events_by_status"].get(status, 0) + 1
                
                # By hour
                created_at = event.get("created_at")
                if created_at:
                    try:
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        hour = dt.hour
                        stats["events_by_hour"][hour] = stats["events_by_hour"].get(hour, 0) + 1
                    except:
                        pass
                
                # By day
                if created_at:
                    try:
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        day = dt.strftime("%Y-%m-%d")
                        stats["events_by_day"][day] = stats["events_by_day"].get(day, 0) + 1
                    except:
                        pass
                
                # Performance metrics
                if event.get("processing_time"):
                    stats["performance_metrics"]["total_processing_time"] += event["processing_time"]
            
            # Calculate averages
            if stats["performance_metrics"]["total_processing_time"] > 0:
                stats["performance_metrics"]["average_processing_time"] = (
                    stats["performance_metrics"]["total_processing_time"] / stats["total_events"]
                )
            
            # Calculate events per minute
            if date_range and len(events) > 0:
                start_date, end_date = date_range
                duration_minutes = (end_date - start_date).total_seconds() / 60
                if duration_minutes > 0:
                    stats["performance_metrics"]["events_per_minute"] = len(events) / duration_minutes
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get event statistics: {e}")
            return {}
    
    async def archive_events(
        self,
        date_range: Tuple[datetime, datetime],
        archive_format: str = "json",
        compress: bool = True
    ) -> str:
        """
        Archive events for a given date range.
        
        Args:
            date_range: Tuple of (start_date, end_date) to archive
            archive_format: Format for archive (json, csv, pickle)
            compress: Whether to compress the archive
            
        Returns:
            Path to the archive file
        """
        try:
            # Get events for the date range
            events = await self.query_events(
                date_range=date_range,
                limit=100000  # Get all events in range
            )
            
            if not events:
                self.logger.warning("No events found for archiving")
                return ""
            
            # Create archive filename
            start_date, end_date = date_range
            archive_name = f"events_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
            
            if archive_format == "json":
                archive_path = self.storage_dir / f"{archive_name}.json"
                await self._create_json_archive(events, archive_path, compress)
            elif archive_format == "csv":
                archive_path = self.storage_dir / f"{archive_name}.csv"
                await self._create_csv_archive(events, archive_path, compress)
            elif archive_format == "pickle":
                archive_path = self.storage_dir / f"{archive_name}.pkl"
                await self._create_pickle_archive(events, archive_path, compress)
            else:
                raise ValueError(f"Unsupported archive format: {archive_format}")
            
            self.metrics["events_archived"] += len(events)
            self.logger.info(f"Archived {len(events)} events to {archive_path}")
            
            return str(archive_path)
            
        except Exception as e:
            self.logger.error(f"Failed to archive events: {e}")
            raise
    
    async def cleanup_old_events(self, retention_days: int = 30) -> int:
        """
        Clean up old events based on retention policy.
        
        Args:
            retention_days: Number of days to retain events
            
        Returns:
            Number of events deleted
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            # Delete from database
            deleted_count = await self._delete_events_from_database(cutoff_date)
            
            # Clean up cache
            with self.cache_lock:
                original_cache_size = len(self.event_cache)
                self.event_cache = deque(
                    [event for event in self.event_cache if event.created_at > cutoff_date],
                    maxlen=self.event_cache.maxlen
                )
                cache_cleaned = original_cache_size - len(self.event_cache)
            
            self.metrics["events_deleted"] += deleted_count + cache_cleaned
            
            self.logger.info(f"Cleaned up {deleted_count} events from database and {cache_cleaned} from cache")
            return deleted_count + cache_cleaned
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old events: {e}")
            return 0
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current logger metrics."""
        return self.metrics.copy()
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage information."""
        try:
            db_size = Path(self.db_path).stat().st_size if Path(self.db_path).exists() else 0
            log_files = list(self.storage_dir.glob("*.log"))
            archive_files = list(self.storage_dir.glob("*.json")) + list(self.storage_dir.glob("*.csv")) + list(self.storage_dir.glob("*.pkl"))
            
            total_file_size = sum(f.stat().st_size for f in log_files + archive_files)
            
            return {
                "database_size_bytes": db_size,
                "database_size_mb": db_size / (1024 * 1024),
                "log_files_count": len(log_files),
                "archive_files_count": len(archive_files),
                "total_file_size_bytes": total_file_size,
                "total_file_size_mb": total_file_size / (1024 * 1024),
                "cache_size": len(self.event_cache),
                "cache_max_size": self.event_cache.maxlen
            }
        except Exception as e:
            self.logger.error(f"Failed to get storage info: {e}")
            return {}
    
    def _init_database(self) -> None:
        """Initialize the SQLite database."""
        try:
            with self.db_lock:
                self.db_connection = sqlite3.connect(self.db_path)
                self.db_connection.row_factory = sqlite3.Row
                
                # Create events table
                cursor = self.db_connection.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        event_id TEXT PRIMARY KEY,
                        event_type TEXT NOT NULL,
                        event_category TEXT NOT NULL,
                        priority TEXT NOT NULL,
                        status TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        started_at TEXT,
                        completed_at TEXT,
                        project_id TEXT,
                        org_id TEXT,
                        dept_id TEXT,
                        user_id TEXT,
                        source TEXT NOT NULL,
                        target TEXT,
                        metadata TEXT,
                        retry_count INTEGER DEFAULT 0,
                        max_retries INTEGER DEFAULT 3,
                        error_message TEXT,
                        stack_trace TEXT,
                        raw_event_data TEXT
                    )
                """)
                
                # Create indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_category ON events(event_category)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_priority ON events(priority)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_status ON events(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_project_id ON events(project_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_org_id ON events(org_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_source ON events(source)")
                
                self.db_connection.commit()
                self.logger.info("Event database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _close_database(self) -> None:
        """Close the database connection."""
        try:
            with self.db_lock:
                if self.db_connection:
                    self.db_connection.close()
                    self.db_connection = None
        except Exception as e:
            self.logger.error(f"Failed to close database: {e}")
    
    async def _store_event_to_database(self, event: BaseEvent) -> None:
        """Store an event to the database."""
        try:
            with self.db_lock:
                if not self.db_connection:
                    return
                
                cursor = self.db_connection.cursor()
                
                # Convert event to database format
                event_data = {
                    "event_id": event.event_id,
                    "event_type": event.event_type,
                    "event_category": event.event_category.value,
                    "priority": event.priority.value,
                    "status": event.status.value,
                    "created_at": event.created_at.isoformat(),
                    "started_at": event.started_at.isoformat() if event.started_at else None,
                    "completed_at": event.completed_at.isoformat() if event.completed_at else None,
                    "project_id": event.project_id,
                    "org_id": event.org_id,
                    "dept_id": event.dept_id,
                    "user_id": event.user_id,
                    "source": event.source,
                    "target": event.target,
                    "metadata": json.dumps(event.metadata) if event.metadata else None,
                    "retry_count": event.retry_count,
                    "max_retries": event.max_retries,
                    "error_message": event.error_message,
                    "stack_trace": event.stack_trace,
                    "raw_event_data": json.dumps(self._event_to_dict(event))
                }
                
                cursor.execute("""
                    INSERT OR REPLACE INTO events (
                        event_id, event_type, event_category, priority, status,
                        created_at, started_at, completed_at, project_id, org_id,
                        dept_id, user_id, source, target, metadata,
                        retry_count, max_retries, error_message, stack_trace, raw_event_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event_data["event_id"], event_data["event_type"], event_data["event_category"],
                    event_data["priority"], event_data["status"], event_data["created_at"],
                    event_data["started_at"], event_data["completed_at"], event_data["project_id"],
                    event_data["org_id"], event_data["dept_id"], event_data["user_id"],
                    event_data["source"], event_data["target"], event_data["metadata"],
                    event_data["retry_count"], event_data["max_retries"], event_data["error_message"],
                    event_data["stack_trace"], event_data["raw_event_data"]
                ))
                
                self.db_connection.commit()
                self.metrics["database_operations"] += 1
                
        except Exception as e:
            self.logger.error(f"Failed to store event to database: {e}")
            raise
    
    async def _store_event_to_file(self, event: BaseEvent) -> None:
        """Store an event to a log file."""
        try:
            # Create daily log file
            today = datetime.utcnow().strftime("%Y-%m-%d")
            log_file = self.storage_dir / f"events_{today}.log"
            
            # Format event for logging
            event_line = self._format_event_for_logging(event)
            
            # Append to log file
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(event_line + "\n")
            
            self.metrics["file_operations"] += 1
            
        except Exception as e:
            self.logger.error(f"Failed to store event to file: {e}")
    
    def _query_cache(
        self,
        event_types: Optional[List[str]] = None,
        event_categories: Optional[List[EventCategory]] = None,
        priority_levels: Optional[List[EventPriority]] = None,
        source_components: Optional[List[str]] = None,
        target_components: Optional[List[str]] = None,
        project_ids: Optional[List[str]] = None,
        org_ids: Optional[List[str]] = None,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> List[BaseEvent]:
        """Query events from cache."""
        with self.cache_lock:
            filtered_events = []
            
            for event in self.event_cache:
                # Apply filters
                if event_types and event.event_type not in event_types:
                    continue
                if event_categories and event.event_category not in event_categories:
                    continue
                if priority_levels and event.priority not in priority_levels:
                    continue
                if source_components and event.source not in source_components:
                    continue
                if target_components and event.target not in target_components:
                    continue
                if project_ids and event.project_id not in project_ids:
                    continue
                if org_ids and event.org_id not in org_ids:
                    continue
                if date_range:
                    start_date, end_date = date_range
                    if not (start_date <= event.created_at <= end_date):
                        continue
                
                filtered_events.append(event)
            
            return filtered_events
    
    async def _query_database(
        self,
        event_types: Optional[List[str]] = None,
        event_categories: Optional[List[EventCategory]] = None,
        priority_levels: Optional[List[EventPriority]] = None,
        source_components: Optional[List[str]] = None,
        target_components: Optional[List[str]] = None,
        project_ids: Optional[List[str]] = None,
        org_ids: Optional[List[str]] = None,
        date_range: Optional[Tuple[datetime, datetime]] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "created_at",
        order_direction: str = "DESC"
    ) -> List[Dict[str, Any]]:
        """Query events from database."""
        try:
            with self.db_lock:
                if not self.db_connection:
                    return []
                
                # Build query
                query = "SELECT * FROM events WHERE 1=1"
                params = []
                
                if event_types:
                    placeholders = ",".join(["?" for _ in event_types])
                    query += f" AND event_type IN ({placeholders})"
                    params.extend(event_types)
                
                if event_categories:
                    placeholders = ",".join(["?" for _ in event_categories])
                    query += f" AND event_category IN ({placeholders})"
                    params.extend([cat.value for cat in event_categories])
                
                if priority_levels:
                    placeholders = ",".join(["?" for _ in priority_levels])
                    query += f" AND priority IN ({placeholders})"
                    params.extend([pri.value for pri in priority_levels])
                
                if source_components:
                    placeholders = ",".join(["?" for _ in source_components])
                    query += f" AND source IN ({placeholders})"
                    params.extend(source_components)
                
                if target_components:
                    placeholders = ",".join(["?" for _ in target_components])
                    query += f" AND target IN ({placeholders})"
                    params.extend(target_components)
                
                if project_ids:
                    placeholders = ",".join(["?" for _ in project_ids])
                    query += f" AND project_id IN ({placeholders})"
                    params.extend(project_ids)
                
                if org_ids:
                    placeholders = ",".join(["?" for _ in org_ids])
                    query += f" AND org_id IN ({placeholders})"
                    params.extend(org_ids)
                
                if date_range:
                    start_date, end_date = date_range
                    query += " AND created_at BETWEEN ? AND ?"
                    params.extend([start_date.isoformat(), end_date.isoformat()])
                
                # Add ordering and limits
                query += f" ORDER BY {order_by} {order_direction}"
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                # Execute query
                cursor = self.db_connection.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Convert to dictionaries
                events = []
                for row in rows:
                    event_dict = dict(row)
                    # Parse metadata and raw_event_data
                    if event_dict.get("metadata"):
                        try:
                            event_dict["metadata"] = json.loads(event_dict["metadata"])
                        except:
                            pass
                    if event_dict.get("raw_event_data"):
                        try:
                            event_dict["raw_event_data"] = json.loads(event_dict["raw_event_data"])
                        except:
                            pass
                    events.append(event_dict)
                
                return events
                
        except Exception as e:
            self.logger.error(f"Failed to query database: {e}")
            return []
    
    async def _get_event_from_database(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific event from database."""
        try:
            with self.db_lock:
                if not self.db_connection:
                    return None
                
                cursor = self.db_connection.cursor()
                cursor.execute("SELECT * FROM events WHERE event_id = ?", (event_id,))
                row = cursor.fetchone()
                
                if row:
                    event_dict = dict(row)
                    # Parse metadata and raw_event_data
                    if event_dict.get("metadata"):
                        try:
                            event_dict["metadata"] = json.loads(event_dict["metadata"])
                        except:
                            pass
                    if event_dict.get("raw_event_data"):
                        try:
                            event_dict["raw_event_data"] = json.loads(event_dict["raw_event_data"])
                        except:
                            pass
                    return event_dict
                
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get event from database: {e}")
            return None
    
    async def _delete_events_from_database(self, cutoff_date: datetime) -> int:
        """Delete events from database before a cutoff date."""
        try:
            with self.db_lock:
                if not self.db_connection:
                    return 0
                
                cursor = self.db_connection.cursor()
                cursor.execute("DELETE FROM events WHERE created_at < ?", (cutoff_date.isoformat(),))
                deleted_count = cursor.rowcount
                
                self.db_connection.commit()
                return deleted_count
                
        except Exception as e:
            self.logger.error(f"Failed to delete events from database: {e}")
            return 0
    
    def _event_to_dict(self, event: BaseEvent) -> Dict[str, Any]:
        """Convert an event to a dictionary."""
        return {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "event_category": event.event_category.value,
            "priority": event.priority.value,
            "status": event.status.value,
            "created_at": event.created_at.isoformat(),
            "started_at": event.started_at.isoformat() if event.started_at else None,
            "completed_at": event.completed_at.isoformat() if event.completed_at else None,
            "project_id": event.project_id,
            "org_id": event.org_id,
            "dept_id": event.dept_id,
            "user_id": event.user_id,
            "source": event.source,
            "target": event.target,
            "metadata": event.metadata,
            "retry_count": event.retry_count,
            "max_retries": event.max_retries,
            "error_message": event.error_message,
            "stack_trace": event.stack_trace
        }
    
    def _format_events(self, events: List[BaseEvent]) -> List[Dict[str, Any]]:
        """Format a list of events to dictionaries."""
        return [self._event_to_dict(event) for event in events]
    
    def _format_event_for_logging(self, event: BaseEvent) -> str:
        """Format an event for logging."""
        timestamp = event.created_at.strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] {event.event_type} | {event.event_category.value} | {event.priority.value} | {event.source} -> {event.target or 'N/A'} | {event.event_id}"
    
    async def _create_json_archive(self, events: List[Dict[str, Any]], archive_path: Path, compress: bool) -> None:
        """Create a JSON archive of events."""
        try:
            if compress:
                archive_path = archive_path.with_suffix('.json.gz')
                with gzip.open(archive_path, 'wt', encoding='utf-8') as f:
                    json.dump(events, f, indent=2, default=str)
            else:
                with open(archive_path, 'w', encoding='utf-8') as f:
                    json.dump(events, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Failed to create JSON archive: {e}")
            raise
    
    async def _create_csv_archive(self, events: List[Dict[str, Any]], archive_path: Path, compress: bool) -> None:
        """Create a CSV archive of events."""
        try:
            import csv
            
            if compress:
                archive_path = archive_path.with_suffix('.csv.gz')
                with gzip.open(archive_path, 'wt', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=events[0].keys() if events else [])
                    writer.writeheader()
                    writer.writerows(events)
            else:
                with open(archive_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=events[0].keys() if events else [])
                    writer.writeheader()
                    writer.writerows(events)
        except Exception as e:
            self.logger.error(f"Failed to create CSV archive: {e}")
            raise
    
    async def _create_pickle_archive(self, events: List[Dict[str, Any]], archive_path: Path, compress: bool) -> None:
        """Create a pickle archive of events."""
        try:
            if compress:
                archive_path = archive_path.with_suffix('.pkl.gz')
                with gzip.open(archive_path, 'wb') as f:
                    pickle.dump(events, f)
            else:
                with open(archive_path, 'wb') as f:
                    pickle.dump(events, f)
        except Exception as e:
            self.logger.error(f"Failed to create pickle archive: {e}")
            raise
    
    async def _cleanup_loop(self) -> None:
        """Periodic cleanup loop."""
        while self.is_running:
            try:
                await asyncio.sleep(self.config.get("cleanup_interval", 3600))  # 1 hour
                await self.cleanup_old_events(self.config.get("retention_days", 30))
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
    
    async def _archival_loop(self) -> None:
        """Periodic archival loop."""
        while self.is_running:
            try:
                await asyncio.sleep(self.config.get("archival_interval", 86400))  # 24 hours
                
                # Archive events from yesterday
                yesterday = datetime.utcnow() - timedelta(days=1)
                start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
                
                await self.archive_events(
                    date_range=(start_date, end_date),
                    archive_format="json",
                    compress=True
                )
                
            except Exception as e:
                self.logger.error(f"Error in archival loop: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "database_path": "ai_rag_events.db",
            "storage_directory": "logs/events",
            "cache_size": 1000,
            "enable_file_logging": True,
            "retention_days": 30,
            "cleanup_interval": 3600,  # 1 hour
            "archival_interval": 86400,  # 24 hours
        }
