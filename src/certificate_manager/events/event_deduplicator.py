"""
Event Deduplicator

Prevents duplicate event processing for Phase 2.
"""

import hashlib
import json
import logging
from typing import Dict, Any, Set
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class EventDeduplicator:
    """Prevents duplicate event processing."""
    
    def __init__(self, event_ttl: int = 3600):
        """Initialize the deduplicator.
        
        Args:
            event_ttl: Time to live for processed events in seconds (default: 1 hour)
        """
        self.processed_events: Set[str] = set()
        self.event_ttl = event_ttl
        self.event_timestamps: Dict[str, datetime] = {}
        
        logger.info(f"EventDeduplicator initialized with TTL: {event_ttl}s")
    
    def is_duplicate(self, event: Dict[str, Any]) -> bool:
        """Check if event has been processed recently.
        
        Args:
            event: Event data dictionary
            
        Returns:
            True if event is a duplicate, False otherwise
        """
        try:
            # Generate event hash
            event_hash = self._generate_event_hash(event)
            
            # Clean up expired events
            self._cleanup_expired_events()
            
            # Check if event hash exists
            if event_hash in self.processed_events:
                logger.info(f"Duplicate event detected: {event.get('event_type')}")
                return True
            
            # Add to processed set with timestamp
            self.processed_events.add(event_hash)
            self.event_timestamps[event_hash] = datetime.now()
            
            logger.debug(f"New event processed: {event.get('event_type')}")
            return False
            
        except Exception as e:
            logger.error(f"Error checking for duplicates: {e}")
            return False  # Allow processing if deduplication fails
    
    def _generate_event_hash(self, event: Dict[str, Any]) -> str:
        """Generate deterministic hash for event deduplication.
        
        Args:
            event: Event data dictionary
            
        Returns:
            SHA256 hash string
        """
        # Create hash from event content
        content = {
            'certificate_id': event.get('certificate_id'),
            'event_type': event.get('event_type'),
            'module_name': event.get('module_name'),
            'timestamp': event.get('timestamp'),
            'data_hash': self._hash_data(event.get('data', {}))
        }
        
        # Sort keys for deterministic ordering
        content_str = json.dumps(content, sort_keys=True, default=str)
        
        # Generate SHA256 hash
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    def _hash_data(self, data: Dict[str, Any]) -> str:
        """Generate hash for event data.
        
        Args:
            data: Event data dictionary
            
        Returns:
            SHA256 hash string
        """
        if not data:
            return ""
        
        # Convert data to sorted JSON string
        data_str = json.dumps(data, sort_keys=True, default=str)
        
        # Generate hash
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _cleanup_expired_events(self) -> None:
        """Remove expired events from memory."""
        try:
            current_time = datetime.now()
            expired_hashes = []
            
            for event_hash, timestamp in self.event_timestamps.items():
                if current_time - timestamp > timedelta(seconds=self.event_ttl):
                    expired_hashes.append(event_hash)
            
            # Remove expired events
            for event_hash in expired_hashes:
                self.processed_events.discard(event_hash)
                del self.event_timestamps[event_hash]
            
            if expired_hashes:
                logger.debug(f"Cleaned up {len(expired_hashes)} expired events")
                
        except Exception as e:
            logger.error(f"Error cleaning up expired events: {e}")
    
    def clear_all_events(self) -> None:
        """Clear all processed events (for testing/debugging)."""
        self.processed_events.clear()
        self.event_timestamps.clear()
        logger.info("All processed events cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get deduplicator statistics.
        
        Returns:
            Dictionary with deduplicator stats
        """
        return {
            'processed_events_count': len(self.processed_events),
            'event_ttl_seconds': self.event_ttl,
            'memory_usage_estimate': len(self.processed_events) * 64  # Approximate bytes per hash
        } 