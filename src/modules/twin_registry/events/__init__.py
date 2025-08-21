"""
Twin Registry Events Module

This module provides event-driven functionality for the twin registry population system.
It includes an event bus, event handlers, and event logging capabilities.
"""

from .event_bus import EventBus
from .event_handlers import EventHandlers
from .event_types import EventType, EventPriority
from .event_logger import EventLogger

__all__ = [
    'EventBus',
    'EventHandlers', 
    'EventType',
    'EventPriority',
    'EventLogger'
]

__version__ = "1.0.0"
__description__ = "Twin Registry Events - Event-driven population system"
