"""
Event Receiver

Handles incoming events from webhooks and message queues for Phase 2.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json

from ..core.certificate_manager import CertificateManager
from .event_deduplicator import EventDeduplicator
from .event_router import EventRouter
from .event_logger import EventLogger

logger = logging.getLogger(__name__)


class EventReceiver:
    """Handles incoming events from webhooks and message queues."""
    
    def __init__(self, certificate_manager: Optional[CertificateManager] = None):
        """Initialize the event receiver."""
        self.certificate_manager = certificate_manager or CertificateManager()
        self.deduplicator = EventDeduplicator()
        self.router = EventRouter(self.certificate_manager)
        self.logger = EventLogger()
        
        logger.info("EventReceiver initialized successfully")
    
    async def receive_webhook(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Receive webhook events from modules."""
        try:
            # Log incoming event
            self.logger.log_event('webhook_received', event_data)
            
            # Validate event structure
            event = self._validate_event(event_data)
            
            # Check for duplicates
            if self.deduplicator.is_duplicate(event):
                logger.info(f"Duplicate event ignored: {event.get('event_type')}")
                return {
                    'status': 'ignored', 
                    'reason': 'duplicate_event',
                    'event_id': event.get('event_id')
                }
            
            # Route to appropriate processor
            result = await self.router.route_event(event)
            
            # Log successful processing
            self.logger.log_event('event_processed', {
                'event_id': event.get('event_id'),
                'event_type': event.get('event_type'),
                'result': result
            })
            
            return {
                'status': 'processed', 
                'result': result,
                'event_id': event.get('event_id')
            }
            
        except Exception as e:
            logger.error(f"Error processing webhook event: {e}")
            self.logger.log_event('event_error', {
                'event_data': event_data,
                'error': str(e)
            })
            return {
                'status': 'error', 
                'error': str(e),
                'event_id': event_data.get('event_id')
            }
    
    async def receive_message_queue(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Receive events from message queue (Redis/RabbitMQ)."""
        try:
            # Log incoming message
            self.logger.log_event('queue_message_received', message)
            
            # Extract event data from message
            event_data = self._extract_event_from_message(message)
            
            # Process as webhook event
            return await self.receive_webhook(event_data)
            
        except Exception as e:
            logger.error(f"Error processing queue message: {e}")
            self.logger.log_event('queue_message_error', {
                'message': message,
                'error': str(e)
            })
            return {
                'status': 'error', 
                'error': str(e)
            }
    
    def _validate_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate event structure and add required fields."""
        required_fields = ['event_type', 'module_name', 'timestamp']
        
        for field in required_fields:
            if field not in event_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Add event_id if not present
        if 'event_id' not in event_data:
            event_data['event_id'] = self._generate_event_id(event_data)
        
        # Ensure timestamp is in ISO format
        if isinstance(event_data['timestamp'], str):
            try:
                datetime.fromisoformat(event_data['timestamp'])
            except ValueError:
                event_data['timestamp'] = datetime.now().isoformat()
        else:
            event_data['timestamp'] = datetime.now().isoformat()
        
        # Add certificate_id if not present (for some event types)
        if 'certificate_id' not in event_data and 'twin_id' in event_data:
            event_data['certificate_id'] = event_data['twin_id']
        
        return event_data
    
    def _extract_event_from_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Extract event data from message queue message."""
        # Handle different message formats
        if 'event' in message:
            return message['event']
        elif 'data' in message:
            return message['data']
        elif 'payload' in message:
            return message['payload']
        else:
            return message
    
    def _generate_event_id(self, event_data: Dict[str, Any]) -> str:
        """Generate a unique event ID."""
        import hashlib
        
        # Create a unique string from event data
        unique_string = f"{event_data.get('event_type')}_{event_data.get('module_name')}_{event_data.get('timestamp')}"
        
        # Generate hash
        return hashlib.sha256(unique_string.encode()).hexdigest()[:16]
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the event receiver."""
        try:
            # Check if certificate manager is accessible
            certificates = self.certificate_manager.list_certificates()
            
            return {
                'status': 'healthy',
                'certificate_count': len(certificates),
                'deduplicator_status': 'active',
                'router_status': 'active',
                'logger_status': 'active'
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            } 