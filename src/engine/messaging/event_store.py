"""
Event Store
==========

Persistent event storage and replay system for event sourcing and audit trails.
"""

import asyncio
import logging
import threading
import json
import sqlite3
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from pathlib import Path
import pickle

from .types import Event, EventType
from .interfaces import EventStoreProtocol


logger = logging.getLogger(__name__)


class EventStore:
    """Synchronous event store for persistent event storage and replay"""
    
    def __init__(self, name: str = "EventStore", storage_path: str = "events.db"):
        self.name = name
        self.storage_path = Path(storage_path)
        self._lock = threading.RLock()
        self._enabled = True
        self._stats = {
            'events_stored': 0,
            'events_retrieved': 0,
            'replays_executed': 0,
            'errors': 0
        }
        
        # Initialize storage
        self._init_storage()
    
    def _init_storage(self) -> None:
        """Initialize the event storage"""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(self.storage_path) as conn:
                cursor = conn.cursor()
                
                # Create events table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id TEXT PRIMARY KEY,
                        type TEXT NOT NULL,
                        name TEXT NOT NULL,
                        data TEXT,
                        metadata TEXT,
                        timestamp TEXT NOT NULL,
                        source TEXT NOT NULL,
                        version TEXT NOT NULL,
                        correlation_id TEXT,
                        causation_id TEXT,
                        created_at TEXT NOT NULL
                    )
                """)
                
                # Create indexes for performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_source ON events(source)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_correlation_id ON events(correlation_id)")
                
                conn.commit()
                logger.info(f"EventStore {self.name} initialized with storage: {self.storage_path}")
                
        except Exception as e:
            logger.error(f"Failed to initialize EventStore storage: {e}")
            raise
    
    def store_event(self, event: Event) -> bool:
        """
        Store an event in the event store.
        
        Args:
            event: The event to store
            
        Returns:
            bool: True if event was stored successfully
        """
        if not self._enabled:
            logger.warning(f"EventStore {self.name} is disabled, ignoring event: {event.id}")
            return False
        
        if not isinstance(event, Event):
            logger.error(f"Invalid event type: {type(event)}")
            return False
        
        try:
            with self._lock:
                with sqlite3.connect(self.storage_path) as conn:
                    cursor = conn.cursor()
                    
                    # Serialize data and metadata
                    data_json = json.dumps(event.data) if event.data else None
                    metadata_json = json.dumps(event.metadata) if event.metadata else None
                    
                    cursor.execute("""
                        INSERT INTO events (
                            id, type, name, data, metadata, timestamp, source, version,
                            correlation_id, causation_id, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        event.id,
                        event.type.value,
                        event.name,
                        data_json,
                        metadata_json,
                        event.timestamp.isoformat(),
                        event.source,
                        event.version,
                        event.correlation_id,
                        event.causation_id,
                        datetime.utcnow().isoformat()
                    ))
                    
                    conn.commit()
                    
                    self._stats['events_stored'] += 1
                    logger.debug(f"Event {event.id} stored successfully")
                    return True
                    
        except Exception as e:
            logger.error(f"Error storing event {event.id}: {e}")
            self._stats['errors'] += 1
            return False
    
    def get_event(self, event_id: str) -> Optional[Event]:
        """
        Retrieve an event by ID.
        
        Args:
            event_id: The ID of the event to retrieve
            
        Returns:
            Optional[Event]: The event or None if not found
        """
        try:
            with self._lock:
                with sqlite3.connect(self.storage_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        SELECT id, type, name, data, metadata, timestamp, source, version,
                               correlation_id, causation_id
                        FROM events WHERE id = ?
                    """, (event_id,))
                    
                    row = cursor.fetchone()
                    if not row:
                        return None
                    
                    # Parse the event data
                    event = Event(
                        id=row[0],
                        type=EventType(row[1]),
                        name=row[2],
                        data=json.loads(row[3]) if row[3] else {},
                        metadata=json.loads(row[4]) if row[4] else {},
                        timestamp=datetime.fromisoformat(row[5]),
                        source=row[6],
                        version=row[7],
                        correlation_id=row[8],
                        causation_id=row[9]
                    )
                    
                    self._stats['events_retrieved'] += 1
                    return event
                    
        except Exception as e:
            logger.error(f"Error retrieving event {event_id}: {e}")
            self._stats['errors'] += 1
            return None
    
    def get_events(self, event_type: Optional[EventType] = None, 
                   start_time: Optional[str] = None, end_time: Optional[str] = None,
                   limit: Optional[int] = None) -> List[Event]:
        """
        Retrieve events with optional filtering.
        
        Args:
            event_type: Optional event type filter
            start_time: Optional start time filter (ISO format string)
            end_time: Optional end time filter (ISO format string)
            limit: Optional limit on number of events returned
            
        Returns:
            List[Event]: List of matching events
        """
        try:
            with self._lock:
                with sqlite3.connect(self.storage_path) as conn:
                    cursor = conn.cursor()
                    
                    # Build query
                    query = """
                        SELECT id, type, name, data, metadata, timestamp, source, version,
                               correlation_id, causation_id
                        FROM events
                    """
                    params = []
                    conditions = []
                    
                    if event_type:
                        conditions.append("type = ?")
                        params.append(event_type.value)
                    
                    if start_time:
                        conditions.append("timestamp >= ?")
                        params.append(start_time)
                    
                    if end_time:
                        conditions.append("timestamp <= ?")
                        params.append(end_time)
                    
                    if conditions:
                        query += " WHERE " + " AND ".join(conditions)
                    
                    query += " ORDER BY timestamp ASC"
                    
                    if limit:
                        query += " LIMIT ?"
                        params.append(limit)
                    
                    cursor.execute(query, params)
                    rows = cursor.fetchall()
                    
                    # Parse events
                    events = []
                    for row in rows:
                        try:
                            event = Event(
                                id=row[0],
                                type=EventType(row[1]),
                                name=row[2],
                                data=json.loads(row[3]) if row[3] else {},
                                metadata=json.loads(row[4]) if row[4] else {},
                                timestamp=datetime.fromisoformat(row[5]),
                                source=row[6],
                                version=row[7],
                                correlation_id=row[8],
                                causation_id=row[9]
                            )
                            events.append(event)
                        except Exception as e:
                            logger.warning(f"Error parsing event row: {e}")
                            continue
                    
                    self._stats['events_retrieved'] += len(events)
                    logger.debug(f"Retrieved {len(events)} events")
                    return events
                    
        except Exception as e:
            logger.error(f"Error retrieving events: {e}")
            self._stats['errors'] += 1
            return []
    
    def replay_events(self, event_type: Optional[EventType] = None,
                      start_time: Optional[str] = None, end_time: Optional[str] = None,
                      handler: Optional[Callable[[Event], None]] = None) -> int:
        """
        Replay events to a handler.
        
        Args:
            event_type: Optional event type filter
            start_time: Optional start time filter (ISO format string)
            end_time: Optional end time filter (ISO format string)
            handler: Optional handler function for events
            
        Returns:
            int: Number of events replayed
        """
        if not handler:
            logger.warning("No handler provided for event replay")
            return 0
        
        events = self.get_events(event_type, start_time, end_time)
        replayed_count = 0
        
        try:
            for event in events:
                try:
                    handler(event)
                    replayed_count += 1
                except Exception as e:
                    logger.error(f"Error in event replay handler for event {event.id}: {e}")
                    self._stats['errors'] += 1
            
            self._stats['replays_executed'] += 1
            logger.info(f"Replayed {replayed_count} events")
            return replayed_count
            
        except Exception as e:
            logger.error(f"Error during event replay: {e}")
            self._stats['errors'] += 1
            return replayed_count
    
    def get_event_count(self, event_type: Optional[EventType] = None) -> int:
        """
        Get the total number of events.
        
        Args:
            event_type: Optional event type filter
            
        Returns:
            int: Number of events
        """
        try:
            with self._lock:
                with sqlite3.connect(self.storage_path) as conn:
                    cursor = conn.cursor()
                    
                    if event_type:
                        cursor.execute("SELECT COUNT(*) FROM events WHERE type = ?", (event_type.value,))
                    else:
                        cursor.execute("SELECT COUNT(*) FROM events")
                    
                    count = cursor.fetchone()[0]
                    return count
                    
        except Exception as e:
            logger.error(f"Error getting event count: {e}")
            self._stats['errors'] += 1
            return 0
    
    def clear_events(self, event_type: Optional[EventType] = None,
                     before_time: Optional[str] = None) -> int:
        """
        Clear events from the store.
        
        Args:
            event_type: Optional event type filter
            before_time: Optional time filter (ISO format string)
            
        Returns:
            int: Number of events cleared
        """
        try:
            with self._lock:
                with sqlite3.connect(self.storage_path) as conn:
                    cursor = conn.cursor()
                    
                    # Build delete query
                    query = "DELETE FROM events"
                    params = []
                    conditions = []
                    
                    if event_type:
                        conditions.append("type = ?")
                        params.append(event_type.value)
                    
                    if before_time:
                        conditions.append("timestamp < ?")
                        params.append(before_time)
                    
                    if conditions:
                        query += " WHERE " + " AND ".join(conditions)
                    
                    cursor.execute(query, params)
                    deleted_count = cursor.rowcount
                    conn.commit()
                    
                    logger.info(f"Cleared {deleted_count} events from EventStore")
                    return deleted_count
                    
        except Exception as e:
            logger.error(f"Error clearing events: {e}")
            self._stats['errors'] += 1
            return 0
    
    def enable(self) -> None:
        """Enable the event store"""
        self._enabled = True
        logger.info(f"EventStore {self.name} enabled")
    
    def disable(self) -> None:
        """Disable the event store"""
        self._enabled = False
        logger.info(f"EventStore {self.name} disabled")
    
    def is_enabled(self) -> bool:
        """Check if the event store is enabled"""
        return self._enabled
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event store statistics"""
        with self._lock:
            return self._stats.copy()
    
    def reset_stats(self) -> None:
        """Reset event store statistics"""
        with self._lock:
            self._stats = {
                'events_stored': 0,
                'events_retrieved': 0,
                'replays_executed': 0,
                'errors': 0
            }


class AsyncEventStore(EventStore):
    """Asynchronous event store for persistent event storage and replay"""
    
    def __init__(self, name: str = "AsyncEventStore", storage_path: str = "events.db"):
        super().__init__(name, storage_path)
    
    def store_event_async(self, event: Event) -> bool:
        """
        Store an event asynchronously in the event store.
        
        Args:
            event: The event to store
            
        Returns:
            bool: True if event was scheduled for storage
        """
        if not self._enabled:
            logger.warning(f"AsyncEventStore {self.name} is disabled, ignoring event: {event.id}")
            return False
        
        try:
            # Schedule async storage
            asyncio.create_task(self._store_event_async_internal(event))
            return True
        except Exception as e:
            logger.error(f"Error scheduling async event storage {event.id}: {e}")
            return False
    
    async def _store_event_async_internal(self, event: Event) -> None:
        """Internal async event storage method"""
        try:
            # Run sync storage in executor
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.store_event, event)
        except Exception as e:
            logger.error(f"Error in async event storage {event.id}: {e}")
            self._stats['errors'] += 1
    
    async def get_events_async(self, event_type: Optional[EventType] = None,
                         start_time: Optional[str] = None, end_time: Optional[str] = None,
                         limit: Optional[int] = None) -> List[Event]:
        """
        Retrieve events asynchronously with optional filtering.
        
        Args:
            event_type: Optional event type filter
            start_time: Optional start time filter (ISO format string)
            end_time: Optional end time filter (ISO format string)
            limit: Optional limit on number of events returned
            
        Returns:
            List[Event]: List of matching events
        """
        try:
            # Run sync retrieval in executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, 
                self.get_events, 
                event_type, 
                start_time, 
                end_time, 
                limit
            )
        except Exception as e:
            logger.error(f"Error in async event retrieval: {e}")
            self._stats['errors'] += 1
            return []
    
    async def replay_events_async(self, event_type: Optional[EventType] = None,
                            start_time: Optional[str] = None, end_time: Optional[str] = None,
                            handler: Optional[Callable[[Event], None]] = None) -> int:
        """
        Replay events asynchronously to a handler.
        
        Args:
            event_type: Optional event type filter
            start_time: Optional start time filter (ISO format string)
            end_time: Optional end time filter (ISO format string)
            handler: Optional handler function for events
            
        Returns:
            int: Number of events replayed
        """
        try:
            # Run sync replay in executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                self.replay_events,
                event_type,
                start_time,
                end_time,
                handler
            )
        except Exception as e:
            logger.error(f"Error in async event replay: {e}")
            self._stats['errors'] += 1
            return 0
