"""
Event Handlers
==============

Specialized event handler classes for different types of events and business logic.
Provides domain-specific event handling capabilities.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime
from abc import ABC, abstractmethod

from .types import Event, EventType, EventHandler
from .interfaces import EventEmitterProtocol


logger = logging.getLogger(__name__)


class BaseEventHandler(ABC):
    """Abstract base class for event handlers"""
    
    def __init__(self, name: str = "BaseEventHandler"):
        self.name = name
        self.enabled = True
        self.priority = 0
        self.handler_id = None
        self._stats = {
            'events_processed': 0,
            'events_succeeded': 0,
            'events_failed': 0,
            'last_processed': None
        }
    
    @abstractmethod
    async def handle(self, event: Event) -> bool:
        """Handle an event"""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get handler statistics"""
        return self._stats.copy()
    
    def reset_stats(self) -> None:
        """Reset handler statistics"""
        self._stats = {
            'events_processed': 0,
            'events_succeeded': 0,
            'events_failed': 0,
            'last_processed': None
        }


class DatabaseEventHandler(BaseEventHandler):
    """Handles database-related events"""
    
    def __init__(self, name: str = "DatabaseEventHandler"):
        super().__init__(name)
        self.priority = 10  # High priority for database events
        
    async def handle(self, event: Event) -> bool:
        """Handle database events"""
        try:
            self._stats['events_processed'] += 1
            self._stats['last_processed'] = datetime.utcnow()
            
            if event.type == EventType.DATABASE_CONNECTED:
                return await self._handle_database_connected(event)
            elif event.type == EventType.DATABASE_DISCONNECTED:
                return await self._handle_database_disconnected(event)
            elif event.type == EventType.DATABASE_MIGRATION_STARTED:
                return await self._handle_migration_started(event)
            elif event.type == EventType.DATABASE_MIGRATION_COMPLETED:
                return await self._handle_migration_completed(event)
            else:
                logger.warning(f"Unknown database event type: {event.type}")
                return False
                
        except Exception as e:
            logger.error(f"Error handling database event {event.name}: {e}")
            self._stats['events_failed'] += 1
            return False
    
    async def _handle_database_connected(self, event: Event) -> bool:
        """Handle database connection events"""
        logger.info(f"Database connected: {event.data.get('database_name', 'unknown')}")
        self._stats['events_succeeded'] += 1
        return True
    
    async def _handle_database_disconnected(self, event: Event) -> bool:
        """Handle database disconnection events"""
        logger.info(f"Database disconnected: {event.data.get('database_name', 'unknown')}")
        self._stats['events_succeeded'] += 1
        return True
    
    async def _handle_migration_started(self, event: Event) -> bool:
        """Handle migration start events"""
        migration_name = event.data.get('migration_name', 'unknown')
        logger.info(f"Database migration started: {migration_name}")
        self._stats['events_succeeded'] += 1
        return True
    
    async def _handle_migration_completed(self, event: Event) -> bool:
        """Handle migration completion events"""
        migration_name = event.data.get('migration_name', 'unknown')
        success = event.data.get('success', False)
        if success:
            logger.info(f"Database migration completed successfully: {migration_name}")
        else:
            logger.error(f"Database migration failed: {migration_name}")
        self._stats['events_succeeded'] += 1
        return True


class SchemaEventHandler(BaseEventHandler):
    """Handles schema-related events"""
    
    def __init__(self, name: str = "SchemaEventHandler"):
        super().__init__(name)
        self.priority = 8  # High priority for schema events
        
    async def handle(self, event: Event) -> bool:
        """Handle schema events"""
        try:
            self._stats['events_processed'] += 1
            self._stats['last_processed'] = datetime.utcnow()
            
            if event.type == EventType.SCHEMA_CREATED:
                return await self._handle_schema_created(event)
            elif event.type == EventType.SCHEMA_UPDATED:
                return await self._handle_schema_updated(event)
            elif event.type == EventType.SCHEMA_DELETED:
                return await self._handle_schema_deleted(event)
            elif event.type == EventType.SCHEMA_VALIDATION_STARTED:
                return await self._handle_validation_started(event)
            elif event.type == EventType.SCHEMA_VALIDATION_COMPLETED:
                return await self._handle_validation_completed(event)
            else:
                logger.warning(f"Unknown schema event type: {event.type}")
                return False
                
        except Exception as e:
            logger.error(f"Error handling schema event {event.name}: {e}")
            self._stats['events_failed'] += 1
            return False
    
    async def _handle_schema_created(self, event: Event) -> bool:
        """Handle schema creation events"""
        table_name = event.data.get('table_name', 'unknown')
        logger.info(f"Schema created for table: {table_name}")
        self._stats['events_succeeded'] += 1
        return True
    
    async def _handle_schema_updated(self, event: Event) -> bool:
        """Handle schema update events"""
        table_name = event.data.get('table_name', 'unknown')
        logger.info(f"Schema updated for table: {table_name}")
        self._stats['events_succeeded'] += 1
        return True
    
    async def _handle_schema_deleted(self, event: Event) -> bool:
        """Handle schema deletion events"""
        table_name = event.data.get('table_name', 'unknown')
        logger.info(f"Schema deleted for table: {table_name}")
        self._stats['events_succeeded'] += 1
        return True
    
    async def _handle_validation_started(self, event: Event) -> bool:
        """Handle validation start events"""
        table_name = event.data.get('table_name', 'unknown')
        logger.info(f"Schema validation started for table: {table_name}")
        self._stats['events_succeeded'] += 1
        return True
    
    async def _handle_validation_completed(self, event: Event) -> bool:
        """Handle validation completion events"""
        table_name = event.data.get('table_name', 'unknown')
        success = event.data.get('success', False)
        if success:
            logger.info(f"Schema validation completed successfully for table: {table_name}")
        else:
            logger.error(f"Schema validation failed for table: {table_name}")
        self._stats['events_succeeded'] += 1
        return True


class BusinessEventHandler(BaseEventHandler):
    """Handles business domain events"""
    
    def __init__(self, name: str = "BusinessEventHandler"):
        super().__init__(name)
        self.priority = 5  # Medium priority for business events
        
    async def handle(self, event: Event) -> bool:
        """Handle business domain events"""
        try:
            self._stats['events_processed'] += 1
            self._stats['last_processed'] = datetime.utcnow()
            
            if event.type == EventType.USER_CREATED:
                return await self._handle_user_created(event)
            elif event.type == EventType.USER_UPDATED:
                return await self._handle_user_updated(event)
            elif event.type == EventType.USER_DELETED:
                return await self._handle_user_deleted(event)
            elif event.type == EventType.ORGANIZATION_CREATED:
                return await self._handle_organization_created(event)
            elif event.type == EventType.PROJECT_CREATED:
                return await self._handle_project_created(event)
            else:
                logger.warning(f"Unknown business event type: {event.type}")
                return False
                
        except Exception as e:
            logger.error(f"Error handling business event {event.name}: {e}")
            self._stats['events_failed'] += 1
            return False
    
    async def _handle_user_created(self, event: Event) -> bool:
        """Handle user creation events"""
        user_id = event.data.get('user_id', 'unknown')
        email = event.data.get('email', 'unknown')
        logger.info(f"User created: {user_id} ({email})")
        self._stats['events_succeeded'] += 1
        return True
    
    async def _handle_user_updated(self, event: Event) -> bool:
        """Handle user update events"""
        user_id = event.data.get('user_id', 'unknown')
        logger.info(f"User updated: {user_id}")
        self._stats['events_succeeded'] += 1
        return True
    
    async def _handle_user_deleted(self, event: Event) -> bool:
        """Handle user deletion events"""
        user_id = event.data.get('user_id', 'unknown')
        logger.info(f"User deleted: {user_id}")
        self._stats['events_succeeded'] += 1
        return True
    
    async def _handle_organization_created(self, event: Event) -> bool:
        """Handle organization creation events"""
        org_id = event.data.get('org_id', 'unknown')
        org_name = event.data.get('name', 'unknown')
        logger.info(f"Organization created: {org_id} ({org_name})")
        self._stats['events_succeeded'] += 1
        return True
    
    async def _handle_project_created(self, event: Event) -> bool:
        """Handle project creation events"""
        project_id = event.data.get('project_id', 'unknown')
        project_name = event.data.get('name', 'unknown')
        logger.info(f"Project created: {project_id} ({project_name})")
        self._stats['events_succeeded'] += 1
        return True


class AIEventHandler(BaseEventHandler):
    """Handles AI/RAG-related events"""
    
    def __init__(self, name: str = "AIEventHandler"):
        super().__init__(name)
        self.priority = 6  # Medium-high priority for AI events
        
    async def handle(self, event: Event) -> bool:
        """Handle AI/RAG events"""
        try:
            self._stats['events_processed'] += 1
            self._stats['last_processed'] = datetime.utcnow()
            
            if event.type == EventType.AI_MODEL_TRAINED:
                return await self._handle_model_trained(event)
            elif event.type == EventType.AI_EMBEDDING_GENERATED:
                return await self._handle_embedding_generated(event)
            elif event.type == EventType.RAG_QUERY_EXECUTED:
                return await self._handle_rag_query(event)
            else:
                logger.warning(f"Unknown AI event type: {event.type}")
                return False
                
        except Exception as e:
            logger.error(f"Error handling AI event {event.name}: {e}")
            self._stats['events_failed'] += 1
            return False
    
    async def _handle_model_trained(self, event: Event) -> bool:
        """Handle model training events"""
        model_name = event.data.get('model_name', 'unknown')
        accuracy = event.data.get('accuracy', 'unknown')
        logger.info(f"AI model trained: {model_name} (accuracy: {accuracy})")
        self._stats['events_succeeded'] += 1
        return True
    
    async def _handle_embedding_generated(self, event: Event) -> bool:
        """Handle embedding generation events"""
        model_name = event.data.get('model_name', 'unknown')
        dimensions = event.data.get('dimensions', 'unknown')
        logger.info(f"AI embedding generated: {model_name} ({dimensions} dimensions)")
        self._stats['events_succeeded'] += 1
        return True
    
    async def _handle_rag_query(self, event: Event) -> bool:
        """Handle RAG query events"""
        query_id = event.data.get('query_id', 'unknown')
        response_time = event.data.get('response_time', 'unknown')
        logger.info(f"RAG query executed: {query_id} (response time: {response_time}ms)")
        self._stats['events_succeeded'] += 1
        return True


class CertificateEventHandler(BaseEventHandler):
    """Handles certificate-related events"""
    
    def __init__(self, name: str = "CertificateEventHandler"):
        super().__init__(name)
        self.priority = 7  # High priority for certificate events
        
    async def handle(self, event: Event) -> bool:
        """Handle certificate events"""
        try:
            self._stats['events_processed'] += 1
            self._stats['last_processed'] = datetime.utcnow()
            
            if event.type == EventType.CERTIFICATE_ISSUED:
                return await self._handle_certificate_issued(event)
            elif event.type == EventType.CERTIFICATE_EXPIRED:
                return await self._handle_certificate_expired(event)
            elif event.type == EventType.CERTIFICATE_REVOKED:
                return await self._handle_certificate_revoked(event)
            else:
                logger.warning(f"Unknown certificate event type: {event.type}")
                return False
                
        except Exception as e:
            logger.error(f"Error handling certificate event {event.name}: {e}")
            self._stats['events_failed'] += 1
            return False
    
    async def _handle_certificate_issued(self, event: Event) -> bool:
        """Handle certificate issuance events"""
        cert_id = event.data.get('certificate_id', 'unknown')
        cert_type = event.data.get('certificate_type', 'unknown')
        logger.info(f"Certificate issued: {cert_id} (type: {cert_type})")
        self._stats['events_succeeded'] += 1
        return True
    
    async def _handle_certificate_expired(self, event: Event) -> bool:
        """Handle certificate expiration events"""
        cert_id = event.data.get('certificate_id', 'unknown')
        logger.warning(f"Certificate expired: {cert_id}")
        self._stats['events_succeeded'] += 1
        return True
    
    async def _handle_certificate_revoked(self, event: Event) -> bool:
        """Handle certificate revocation events"""
        cert_id = event.data.get('certificate_id', 'unknown')
        reason = event.data.get('reason', 'unknown')
        logger.warning(f"Certificate revoked: {cert_id} (reason: {reason})")
        self._stats['events_succeeded'] += 1
        return True


class SystemEventHandler(BaseEventHandler):
    """Handles system-level events"""
    
    def __init__(self, name: str = "SystemEventHandler"):
        super().__init__(name)
        self.priority = 9  # Very high priority for system events
        
    async def handle(self, event: Event) -> bool:
        """Handle system events"""
        try:
            self._stats['events_processed'] += 1
            self._stats['last_processed'] = datetime.utcnow()
            
            if event.type == EventType.SYSTEM_STARTUP:
                return await self._handle_system_startup(event)
            elif event.type == EventType.SYSTEM_SHUTDOWN:
                return await self._handle_system_shutdown(event)
            elif event.type == EventType.SYSTEM_HEALTH_CHECK:
                return await self._handle_health_check(event)
            else:
                logger.warning(f"Unknown system event type: {event.type}")
                return False
                
        except Exception as e:
            logger.error(f"Error handling system event {event.name}: {e}")
            self._stats['events_failed'] += 1
            return False
    
    async def _handle_system_startup(self, event: Event) -> bool:
        """Handle system startup events"""
        startup_time = event.data.get('startup_time', 'unknown')
        logger.info(f"System startup completed at: {startup_time}")
        self._stats['events_succeeded'] += 1
        return True
    
    async def _handle_system_shutdown(self, event: Event) -> bool:
        """Handle system shutdown events"""
        shutdown_time = event.data.get('shutdown_time', 'unknown')
        logger.info(f"System shutdown initiated at: {shutdown_time}")
        self._stats['events_succeeded'] += 1
        return True
    
    async def _handle_health_check(self, event: Event) -> bool:
        """Handle health check events"""
        status = event.data.get('status', 'unknown')
        response_time = event.data.get('response_time', 'unknown')
        logger.debug(f"System health check: {status} (response time: {response_time}ms)")
        self._stats['events_succeeded'] += 1
        return True


class EventHandlerRegistry:
    """Registry for managing event handlers"""
    
    def __init__(self):
        self._handlers: Dict[EventType, List[BaseEventHandler]] = {}
        self._handler_map: Dict[str, BaseEventHandler] = {}
        self._enabled = True
    
    def register_handler(self, event_type: EventType, handler: BaseEventHandler) -> bool:
        """Register an event handler for a specific event type"""
        if not isinstance(handler, BaseEventHandler):
            logger.error(f"Invalid handler type: {type(handler)}")
            return False
        
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        # Check if handler already registered
        if handler in self._handlers[event_type]:
            logger.warning(f"Handler {handler.name} already registered for event type {event_type.value}")
            return False
        
        # Add handler and sort by priority
        self._handlers[event_type].append(handler)
        self._handlers[event_type].sort(key=lambda h: h.priority, reverse=True)
        
        # Store in handler map
        self._handler_map[handler.name] = handler
        
        logger.info(f"Registered handler {handler.name} for event type {event_type.value}")
        return True
    
    def unregister_handler(self, event_type: EventType, handler_name: str) -> bool:
        """Unregister an event handler"""
        if event_type not in self._handlers:
            return False
        
        handlers = self._handlers[event_type]
        for handler in handlers:
            if handler.name == handler_name:
                handlers.remove(handler)
                if handler_name in self._handler_map:
                    del self._handler_map[handler_name]
                
                # Clean up empty lists
                if not handlers:
                    del self._handlers[event_type]
                
                logger.info(f"Unregistered handler {handler_name} from event type {event_type.value}")
                return True
        
        return False
    
    def get_handlers(self, event_type: EventType) -> List[BaseEventHandler]:
        """Get all handlers for a specific event type"""
        return self._handlers.get(event_type, []).copy()
    
    def get_handler(self, handler_name: str) -> Optional[BaseEventHandler]:
        """Get a specific handler by name"""
        return self._handler_map.get(handler_name)
    
    def get_all_handlers(self) -> List[BaseEventHandler]:
        """Get all registered handlers"""
        return list(self._handler_map.values())
    
    def clear_handlers(self, event_type: Optional[EventType] = None) -> None:
        """Clear handlers for a specific event type or all handlers"""
        if event_type:
            if event_type in self._handlers:
                count = len(self._handlers[event_type])
                del self._handlers[event_type]
                logger.info(f"Cleared {count} handlers for event type {event_type.value}")
        else:
            count = len(self._handler_map)
            self._handlers.clear()
            self._handler_map.clear()
            logger.info(f"Cleared all {count} handlers")
    
    def enable(self) -> None:
        """Enable the handler registry"""
        self._enabled = True
        logger.info("Event handler registry enabled")
    
    def disable(self) -> None:
        """Disable the handler registry"""
        self._enabled = False
        logger.info("Event handler registry disabled")
    
    def is_enabled(self) -> bool:
        """Check if the handler registry is enabled"""
        return self._enabled
    
    async def handle_event(self, event: Event) -> bool:
        """Handle an event using all registered handlers"""
        if not self._enabled:
            logger.warning("Event handler registry is disabled")
            return False
        
        event_type = event.type
        handlers = self.get_handlers(event_type)
        
        if not handlers:
            logger.debug(f"No handlers registered for event type: {event_type.value}")
            return True
        
        success_count = 0
        total_count = len(handlers)
        
        for handler in handlers:
            if not handler.enabled:
                continue
            
            try:
                if await handler.handle(event):
                    success_count += 1
                else:
                    logger.warning(f"Handler {handler.name} failed to handle event {event.name}")
            except Exception as e:
                logger.error(f"Error in handler {handler.name}: {e}")
        
        logger.debug(f"Event {event.name} handled by {success_count}/{total_count} handlers")
        return success_count > 0
