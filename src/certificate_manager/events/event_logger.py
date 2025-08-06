"""
Event Logger

Logs and monitors events for Phase 2.
"""

import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class EventLogger:
    """Logs and monitors events."""
    
    def __init__(self, log_file: Optional[str] = None):
        """Initialize the event logger.
        
        Args:
            log_file: Optional file path for event logging
        """
        self.log_file = log_file or "logs/certificate_events.log"
        self._setup_logging()
        
        logger.info("EventLogger initialized successfully")
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        # Ensure logs directory exists
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Create file handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        event_logger = logging.getLogger('certificate_events')
        event_logger.addHandler(file_handler)
        event_logger.setLevel(logging.INFO)
        
        self.event_logger = event_logger
    
    def log_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Log an event.
        
        Args:
            event_type: Type of event
            event_data: Event data dictionary
        """
        try:
            # Create log entry
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'data': event_data
            }
            
            # Log to file
            self.event_logger.info(json.dumps(log_entry))
            
            # Log to console for important events
            if event_type in ['webhook_received', 'event_processed', 'event_error']:
                logger.info(f"Event logged: {event_type}")
                
        except Exception as e:
            logger.error(f"Error logging event: {e}")
    
    def log_webhook_received(self, event_data: Dict[str, Any]) -> None:
        """Log webhook received event."""
        self.log_event('webhook_received', event_data)
    
    def log_event_processed(self, event_id: str, event_type: str, result: Dict[str, Any]) -> None:
        """Log event processed."""
        self.log_event('event_processed', {
            'event_id': event_id,
            'event_type': event_type,
            'result': result
        })
    
    def log_event_error(self, event_data: Dict[str, Any], error: str) -> None:
        """Log event error."""
        self.log_event('event_error', {
            'event_data': event_data,
            'error': error
        })
    
    def log_queue_message_received(self, message: Dict[str, Any]) -> None:
        """Log queue message received."""
        self.log_event('queue_message_received', message)
    
    def log_queue_message_error(self, message: Dict[str, Any], error: str) -> None:
        """Log queue message error."""
        self.log_event('queue_message_error', {
            'message': message,
            'error': error
        })
    
    def get_recent_events(self, limit: int = 100) -> list:
        """Get recent events from log file.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        try:
            events = []
            
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    lines = f.readlines()
                    
                    # Parse last N lines
                    for line in lines[-limit:]:
                        try:
                            # Extract JSON from log line
                            json_start = line.find('{')
                            if json_start != -1:
                                json_str = line[json_start:]
                                event = json.loads(json_str)
                                events.append(event)
                        except json.JSONDecodeError:
                            continue
            
            return events[-limit:]  # Return last N events
            
        except Exception as e:
            logger.error(f"Error reading recent events: {e}")
            return []
    
    def get_events_by_type(self, event_type: str, limit: int = 50) -> list:
        """Get events by type.
        
        Args:
            event_type: Type of event to filter by
            limit: Maximum number of events to return
            
        Returns:
            List of events of specified type
        """
        try:
            all_events = self.get_recent_events(limit * 2)  # Get more to filter
            filtered_events = [
                event for event in all_events 
                if event.get('event_type') == event_type
            ]
            
            return filtered_events[-limit:]
            
        except Exception as e:
            logger.error(f"Error filtering events by type: {e}")
            return []
    
    def get_error_events(self, limit: int = 50) -> list:
        """Get error events.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of error events
        """
        return self.get_events_by_type('event_error', limit)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get logging statistics.
        
        Returns:
            Dictionary with logging stats
        """
        try:
            events = self.get_recent_events(1000)  # Get last 1000 events
            
            # Count event types
            event_counts = {}
            error_count = 0
            
            for event in events:
                event_type = event.get('event_type', 'unknown')
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
                
                if event_type == 'event_error':
                    error_count += 1
            
            return {
                'total_events': len(events),
                'error_count': error_count,
                'event_type_counts': event_counts,
                'log_file_size': os.path.getsize(self.log_file) if os.path.exists(self.log_file) else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting logging stats: {e}")
            return {
                'total_events': 0,
                'error_count': 0,
                'event_type_counts': {},
                'log_file_size': 0
            } 