"""
Event Sourcing
=============

Event sourcing and CQRS support for building event-driven aggregates.
"""

import asyncio
import logging
import threading
import json
import sqlite3
from typing import Any, Dict, List, Optional, Callable, Type, TypeVar
from datetime import datetime
from pathlib import Path
import pickle

from .types import Event, EventType
from .interfaces import EventSourcingProtocol

T = TypeVar('T')


logger = logging.getLogger(__name__)


class EventSourcing:
    """Synchronous event sourcing for building event-driven aggregates"""
    
    def __init__(self, name: str = "EventSourcing", storage_path: str = "event_sourcing.db"):
        self.name = name
        self.storage_path = Path(storage_path)
        self._lock = threading.RLock()
        self._enabled = True
        self._stats = {
            'events_appended': 0,
            'aggregates_rebuilt': 0,
            'snapshots_created': 0,
            'errors': 0
        }
        
        # Initialize storage
        self._init_storage()
    
    def _init_storage(self) -> None:
        """Initialize the event sourcing storage"""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(self.storage_path) as conn:
                cursor = conn.cursor()
                
                # Create event streams table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS event_streams (
                        aggregate_id TEXT NOT NULL,
                        version INTEGER NOT NULL,
                        event_id TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        event_data TEXT NOT NULL,
                        event_metadata TEXT,
                        timestamp TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        PRIMARY KEY (aggregate_id, version)
                    )
                """)
                
                # Create snapshots table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS snapshots (
                        aggregate_id TEXT NOT NULL,
                        version INTEGER NOT NULL,
                        snapshot_data TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        PRIMARY KEY (aggregate_id, version)
                    )
                """)
                
                # Create indexes for performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_event_streams_aggregate ON event_streams(aggregate_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_event_streams_version ON event_streams(version)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_aggregate ON snapshots(aggregate_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_version ON snapshots(version)")
                
                conn.commit()
                logger.info(f"EventSourcing {self.name} initialized with storage: {self.storage_path}")
                
        except Exception as e:
            logger.error(f"Failed to initialize EventSourcing storage: {e}")
            raise
    
    def append_event(self, aggregate_id: str, event: Event) -> bool:
        """
        Append an event to an aggregate's event stream.
        
        Args:
            aggregate_id: ID of the aggregate
            event: The event to append
            
        Returns:
            bool: True if event was appended successfully
        """
        if not self._enabled:
            logger.warning(f"EventSourcing {self.name} is disabled, ignoring event: {event.id}")
            return False
        
        if not isinstance(event, Event):
            logger.error(f"Invalid event type: {type(event)}")
            return False
        
        try:
            with self._lock:
                with sqlite3.connect(self.storage_path) as conn:
                    cursor = conn.cursor()
                    
                    # Get current version
                    cursor.execute("""
                        SELECT MAX(version) FROM event_streams WHERE aggregate_id = ?
                    """, (aggregate_id,))
                    
                    row = cursor.fetchone()
                    current_version = (row[0] or 0) + 1
                    
                    # Serialize event data
                    event_data = json.dumps(event.to_dict())
                    event_metadata = json.dumps(event.metadata) if event.metadata else None
                    
                    # Insert event
                    cursor.execute("""
                        INSERT INTO event_streams (
                            aggregate_id, version, event_id, event_type, event_data,
                            event_metadata, timestamp, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        aggregate_id,
                        current_version,
                        event.id,
                        event.type.value,
                        event_data,
                        event_metadata,
                        event.timestamp.isoformat(),
                        datetime.utcnow().isoformat()
                    ))
                    
                    conn.commit()
                    
                    self._stats['events_appended'] += 1
                    logger.debug(f"Event {event.id} appended to aggregate {aggregate_id} at version {current_version}")
                    return True
                    
        except Exception as e:
            logger.error(f"Error appending event {event.id} to aggregate {aggregate_id}: {e}")
            self._stats['errors'] += 1
            return False
    
    def get_events(self, aggregate_id: str, start_version: int = 0) -> List[Event]:
        """
        Get all events for an aggregate starting from a version.
        
        Args:
            aggregate_id: ID of the aggregate
            start_version: Starting version (inclusive)
            
        Returns:
            List[Event]: List of events
        """
        try:
            with self._lock:
                with sqlite3.connect(self.storage_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        SELECT event_data FROM event_streams 
                        WHERE aggregate_id = ? AND version >= ?
                        ORDER BY version ASC
                    """, (aggregate_id, start_version))
                    
                    rows = cursor.fetchall()
                    events = []
                    
                    for row in rows:
                        try:
                            event_dict = json.loads(row[0])
                            event = Event.from_dict(event_dict)
                            events.append(event)
                        except Exception as e:
                            logger.warning(f"Error parsing event: {e}")
                            continue
                    
                    logger.debug(f"Retrieved {len(events)} events for aggregate {aggregate_id}")
                    return events
                    
        except Exception as e:
            logger.error(f"Error retrieving events for aggregate {aggregate_id}: {e}")
            self._stats['errors'] += 1
            return []
    
    def get_aggregate_version(self, aggregate_id: str) -> int:
        """
        Get the current version of an aggregate.
        
        Args:
            aggregate_id: ID of the aggregate
            
        Returns:
            int: Current version (0 if no events)
        """
        try:
            with self._lock:
                with sqlite3.connect(self.storage_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        SELECT MAX(version) FROM event_streams WHERE aggregate_id = ?
                    """, (aggregate_id,))
                    
                    row = cursor.fetchone()
                    return row[0] or 0
                    
        except Exception as e:
            logger.error(f"Error getting version for aggregate {aggregate_id}: {e}")
            self._stats['errors'] += 1
            return 0
    
    def snapshot_aggregate(self, aggregate_id: str, snapshot: Any, version: int) -> bool:
        """
        Create a snapshot of an aggregate at a specific version.
        
        Args:
            aggregate_id: ID of the aggregate
            snapshot: Snapshot data to store
            version: Version of the snapshot
            
        Returns:
            bool: True if snapshot was created successfully
        """
        try:
            with self._lock:
                with sqlite3.connect(self.storage_path) as conn:
                    cursor = conn.cursor()
                    
                    # Serialize snapshot data
                    snapshot_data = json.dumps(snapshot)
                    
                    # Insert or update snapshot
                    cursor.execute("""
                        INSERT OR REPLACE INTO snapshots (
                            aggregate_id, version, snapshot_data, created_at
                        ) VALUES (?, ?, ?, ?)
                    """, (
                        aggregate_id,
                        version,
                        snapshot_data,
                        datetime.utcnow().isoformat()
                    ))
                    
                    conn.commit()
                    
                    self._stats['snapshots_created'] += 1
                    logger.debug(f"Snapshot created for aggregate {aggregate_id} at version {version}")
                    return True
                    
        except Exception as e:
            logger.error(f"Error creating snapshot for aggregate {aggregate_id}: {e}")
            self._stats['errors'] += 1
            return False
    
    def get_latest_snapshot(self, aggregate_id: str) -> Optional[Any]:
        """
        Get the latest snapshot for an aggregate.
        
        Args:
            aggregate_id: ID of the aggregate
            
        Returns:
            Optional[Any]: Latest snapshot data or None
        """
        try:
            with self._lock:
                with sqlite3.connect(self.storage_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        SELECT snapshot_data FROM snapshots 
                        WHERE aggregate_id = ? 
                        ORDER BY version DESC 
                        LIMIT 1
                    """, (aggregate_id,))
                    
                    row = cursor.fetchone()
                    if row:
                        snapshot_data = json.loads(row[0])
                        return snapshot_data
                    
                    return None
                    
        except Exception as e:
            logger.error(f"Error retrieving snapshot for aggregate {aggregate_id}: {e}")
            self._stats['errors'] += 1
            return None
    
    def rebuild_aggregate(self, aggregate_id: str, from_version: int = 0) -> Any:
        """
        Rebuild an aggregate from events.
        
        Args:
            aggregate_id: ID of the aggregate
            from_version: Starting version for rebuild
            
        Returns:
            Any: Rebuilt aggregate state
        """
        try:
            # Get events from the specified version
            events = self.get_events(aggregate_id, from_version)
            
            if not events:
                logger.debug(f"No events found for aggregate {aggregate_id}")
                return None
            
            # Start with latest snapshot if available
            current_state = None
            if from_version == 0:
                snapshot = self.get_latest_snapshot(aggregate_id)
                if snapshot:
                    current_state = snapshot
                    logger.debug(f"Using snapshot for aggregate {aggregate_id}")
            
            # Apply events to build current state
            for event in events:
                try:
                    current_state = self._apply_event(current_state, event)
                except Exception as e:
                    logger.error(f"Error applying event {event.id} to aggregate {aggregate_id}: {e}")
                    self._stats['errors'] += 1
            
            self._stats['aggregates_rebuilt'] += 1
            logger.debug(f"Aggregate {aggregate_id} rebuilt from {len(events)} events")
            return current_state
            
        except Exception as e:
            logger.error(f"Error rebuilding aggregate {aggregate_id}: {e}")
            self._stats['errors'] += 1
            return None
    
    def _apply_event(self, current_state: Any, event: Event) -> Any:
        """
        Apply an event to the current state.
        This is a placeholder method that should be overridden by subclasses.
        
        Args:
            current_state: Current aggregate state
            event: Event to apply
            
        Returns:
            Any: Updated aggregate state
        """
        # Default implementation - just return the event data
        # Subclasses should override this to implement domain-specific logic
        return event.data
    
    def enable(self) -> None:
        """Enable the event sourcing"""
        self._enabled = True
        logger.info(f"EventSourcing {self.name} enabled")
    
    def disable(self) -> None:
        """Disable the event sourcing"""
        self._enabled = False
        logger.info(f"EventSourcing {self.name} disabled")
    
    def is_enabled(self) -> bool:
        """Check if the event sourcing is enabled"""
        return self._enabled
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event sourcing statistics"""
        with self._lock:
            return self._stats.copy()
    
    def reset_stats(self) -> None:
        """Reset event sourcing statistics"""
        with self._lock:
            self._stats = {
                'events_appended': 0,
                'aggregates_rebuilt': 0,
                'snapshots_created': 0,
                'errors': 0
            }


class AsyncEventSourcing(EventSourcing):
    """Asynchronous event sourcing for building event-driven aggregates"""
    
    def __init__(self, name: str = "AsyncEventSourcing", storage_path: str = "event_sourcing.db"):
        super().__init__(name, storage_path)
    
    def append_event_async(self, aggregate_id: str, event: Event) -> bool:
        """
        Append an event asynchronously to an aggregate's event stream.
        
        Args:
            aggregate_id: ID of the aggregate
            event: The event to append
            
        Returns:
            bool: True if event was scheduled for appending
        """
        if not self._enabled:
            logger.warning(f"AsyncEventSourcing {self.name} is disabled, ignoring event: {event.id}")
            return False
        
        try:
            # Schedule async append
            asyncio.create_task(self._append_event_async_internal(aggregate_id, event))
            return True
        except Exception as e:
            logger.error(f"Error scheduling async event append {event.id}: {e}")
            return False
    
    async def _append_event_async_internal(self, aggregate_id: str, event: Event) -> None:
        """Internal async event append method"""
        try:
            # Run sync append in executor
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.append_event, aggregate_id, event)
        except Exception as e:
            logger.error(f"Error in async event append {event.id}: {e}")
            self._stats['errors'] += 1
    
    async def get_events_async(self, aggregate_id: str, start_version: int = 0) -> List[Event]:
        """
        Get all events for an aggregate asynchronously starting from a version.
        
        Args:
            aggregate_id: ID of the aggregate
            start_version: Starting version (inclusive)
            
        Returns:
            List[Event]: List of events
        """
        try:
            # Run sync retrieval in executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.get_events, aggregate_id, start_version)
        except Exception as e:
            logger.error(f"Error in async event retrieval for aggregate {aggregate_id}: {e}")
            self._stats['errors'] += 1
            return []
    
    async def rebuild_aggregate_async(self, aggregate_id: str, from_version: int = 0) -> Any:
        """
        Rebuild an aggregate asynchronously from events.
        
        Args:
            aggregate_id: ID of the aggregate
            from_version: Starting version for rebuild
            
        Returns:
            Any: Rebuilt aggregate state
        """
        try:
            # Run sync rebuild in executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.rebuild_aggregate, aggregate_id, from_version)
        except Exception as e:
            logger.error(f"Error in async aggregate rebuild for {aggregate_id}: {e}")
            self._stats['errors'] += 1
            return None


class AggregateBase:
    """Base class for event-sourced aggregates"""
    
    def __init__(self, aggregate_id: str, event_sourcing: EventSourcing):
        self.aggregate_id = aggregate_id
        self.event_sourcing = event_sourcing
        self.version = 0
        self._uncommitted_events: List[Event] = []
    
    def apply_event(self, event: Event) -> None:
        """
        Apply an event to the aggregate.
        This method should be overridden by subclasses to implement domain-specific logic.
        
        Args:
            event: Event to apply
        """
        # Default implementation - just increment version
        self.version += 1
    
    def add_event(self, event_type: EventType, data: Dict[str, Any], 
                  metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add an uncommitted event to the aggregate.
        
        Args:
            event_type: Type of the event
            data: Event data
            metadata: Optional event metadata
        """
        event = Event(
            type=event_type,
            data=data,
            metadata=metadata or {},
            source=self.aggregate_id
        )
        
        self._uncommitted_events.append(event)
        self.apply_event(event)
    
    def commit_events(self) -> bool:
        """
        Commit all uncommitted events to the event store.
        
        Returns:
            bool: True if all events were committed successfully
        """
        try:
            for event in self._uncommitted_events:
                if not self.event_sourcing.append_event(self.aggregate_id, event):
                    return False
            
            self._uncommitted_events.clear()
            return True
            
        except Exception as e:
            logger.error(f"Error committing events for aggregate {self.aggregate_id}: {e}")
            return False
    
    def commit_events_async(self) -> bool:
        """
        Commit all uncommitted events asynchronously to the event store.
        
        Returns:
            bool: True if all events were scheduled for committing
        """
        try:
            for event in self._uncommitted_events:
                if not self.event_sourcing.append_event_async(self.aggregate_id, event):
                    return False
            
            self._uncommitted_events.clear()
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling async event commit for aggregate {self.aggregate_id}: {e}")
            return False
    
    def get_uncommitted_events(self) -> List[Event]:
        """Get all uncommitted events"""
        return self._uncommitted_events.copy()
    
    def has_uncommitted_events(self) -> bool:
        """Check if there are uncommitted events"""
        return len(self._uncommitted_events) > 0
    
    @classmethod
    def load(cls: Type[T], aggregate_id: str, event_sourcing: EventSourcing) -> Optional[T]:
        """
        Load an aggregate from the event store.
        
        Args:
            aggregate_id: ID of the aggregate to load
            event_sourcing: Event sourcing instance
            
        Returns:
            Optional[T]: Loaded aggregate or None
        """
        try:
            # Create aggregate instance
            aggregate = cls(aggregate_id, event_sourcing)
            
            # Rebuild state from events
            state = event_sourcing.rebuild_aggregate(aggregate_id)
            if state:
                aggregate._restore_state(state)
            
            # Set version
            aggregate.version = event_sourcing.get_aggregate_version(aggregate_id)
            
            return aggregate
            
        except Exception as e:
            logger.error(f"Error loading aggregate {aggregate_id}: {e}")
            return None
    
    def _restore_state(self, state: Any) -> None:
        """
        Restore aggregate state from snapshot or rebuilt state.
        This method should be overridden by subclasses.
        
        Args:
            state: State to restore
        """
        # Default implementation - do nothing
        # Subclasses should override this to restore their internal state
        pass
