"""
Cache Decorator
==============

Easy-to-use decorators for function and method caching.
Provides automatic key generation, TTL management, and cache invalidation.
"""

import logging
import time
import functools
import hashlib
import inspect
from typing import Any, Callable, Dict, List, Optional, Union
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def _generate_cache_key(func: Callable, args: tuple, kwargs: dict, 
                       key_prefix: str = "") -> str:
    """
    Generate a cache key for function call.
    
    Args:
        func: Function being cached
        args: Function arguments
        kwargs: Function keyword arguments
        key_prefix: Optional prefix for the cache key
        
    Returns:
        Cache key string
    """
    # Get function name and module
    func_name = func.__name__
    module_name = func.__module__ or "unknown"
    
    # Create a string representation of arguments
    args_str = str(args) + str(sorted(kwargs.items()))
    
    # Generate hash for arguments
    args_hash = hashlib.md5(args_str.encode()).hexdigest()[:8]
    
    # Build cache key
    key_parts = [key_prefix, module_name, func_name, args_hash]
    key_parts = [part for part in key_parts if part]  # Remove empty parts
    
    return ":".join(key_parts)


def cache(ttl: Optional[int] = None, key_prefix: str = "", 
          cache_manager: Optional[Any] = None, level: str = "both"):
    """
    Cache decorator for synchronous functions.
    
    Args:
        ttl: Time to live in seconds (default: use cache manager's default)
        key_prefix: Prefix for cache keys
        cache_manager: Cache manager instance (default: use global cache manager)
        level: Cache level ("L1", "L2", or "both")
    
    Returns:
        Decorated function with caching
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = _generate_cache_key(func, args, kwargs, key_prefix)
            
            # Get cache manager
            cm = cache_manager or _get_global_cache_manager()
            if not cm:
                return func(*args, **kwargs)
            
            try:
                # Try to get from cache
                cached_value = cm.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache HIT for key: {cache_key}")
                    return cached_value
                
                # Cache miss, execute function
                logger.debug(f"Cache MISS for key: {cache_key}")
                start_time = time.time()
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Cache the result
                cm.set(cache_key, result, ttl=ttl, level=level)
                
                # Record operation time if metrics available
                if hasattr(cm, 'metrics'):
                    cm.metrics.record_operation('get', cache_key, duration, True)
                
                return result
                
            except Exception as e:
                logger.error(f"Cache error for key {cache_key}: {e}")
                # Fall back to executing function without caching
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def async_cache(ttl: Optional[int] = None, key_prefix: str = "", 
                cache_manager: Optional[Any] = None, level: str = "both"):
    """
    Cache decorator for asynchronous functions.
    
    Args:
        ttl: Time to live in seconds (default: use cache manager's default)
        key_prefix: Prefix for cache keys
        cache_manager: Cache manager instance (default: use global cache manager)
        level: Cache level ("L1", "L2", or "both")
    
    Returns:
        Decorated async function with caching
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = _generate_cache_key(func, args, kwargs, key_prefix)
            
            # Get cache manager
            cm = cache_manager or _get_global_cache_manager()
            if not cm:
                return await func(*args, **kwargs)
            
            try:
                # Try to get from cache
                cached_value = await cm.get_async(cache_key)
                if cached_value is not None:
                    logger.debug(f"Async Cache HIT for key: {cache_key}")
                    return cached_value
                
                # Cache miss, execute function
                logger.debug(f"Async Cache MISS for key: {cache_key}")
                start_time = time.time()
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Cache the result
                await cm.set_async(cache_key, result, ttl=ttl, level=level)
                
                # Record operation time if metrics available
                if hasattr(cm, 'metrics'):
                    cm.metrics.record_operation('get_async', cache_key, duration, True)
                
                return result
                
            except Exception as e:
                logger.error(f"Async cache error for key {cache_key}: {e}")
                # Fall back to executing function without caching
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def cache_invalidate(pattern: str = "*", cache_manager: Optional[Any] = None, 
                     level: str = "both"):
    """
    Decorator to invalidate cache entries after function execution.
    
    Args:
        pattern: Pattern to match cache keys for invalidation
        cache_manager: Cache manager instance (default: use global cache manager)
        level: Cache level ("L1", "L2", or "both")
    
    Returns:
        Decorated function that invalidates cache after execution
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Execute function first
            result = func(*args, **kwargs)
            
            # Invalidate cache
            cm = cache_manager or _get_global_cache_manager()
            if cm:
                try:
                    # Get keys matching pattern
                    keys_to_invalidate = cm.get_keys(pattern)
                    for key in keys_to_invalidate:
                        cm.delete(key, level=level)
                        logger.debug(f"Invalidated cache key: {key}")
                except Exception as e:
                    logger.error(f"Cache invalidation error: {e}")
            
            return result
        
        return wrapper
    return decorator


def cache_invalidate_async(pattern: str = "*", cache_manager: Optional[Any] = None,
                          level: str = "both"):
    """
    Decorator to invalidate cache entries after async function execution.
    
    Args:
        pattern: Pattern to match cache keys for invalidation
        cache_manager: Cache manager instance (default: use global cache manager)
        level: Cache level ("L1", "L2", or "both")
    
    Returns:
        Decorated async function that invalidates cache after execution
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Execute function first
            result = await func(*args, **kwargs)
            
            # Invalidate cache
            cm = cache_manager or _get_global_cache_manager()
            if cm:
                try:
                    # Get keys matching pattern
                    keys_to_invalidate = cm.get_keys(pattern)
                    for key in keys_to_invalidate:
                        await cm.delete_async(key, level=level)
                        logger.debug(f"Invalidated async cache key: {key}")
                except Exception as e:
                    logger.error(f"Async cache invalidation error: {e}")
            
            return result
        
        return wrapper
    return decorator


def cache_method(ttl: Optional[int] = None, key_prefix: str = "", 
                 include_self: bool = True, level: str = "both"):
    """
    Cache decorator specifically for class methods.
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache keys
        include_self: Whether to include 'self' in cache key generation
        level: Cache level ("L1", "L2", or "both")
    
    Returns:
        Decorated method with caching
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Generate cache key
            if include_self:
                # Include class name and instance id in key
                class_name = self.__class__.__name__
                instance_id = id(self)
                method_key_prefix = f"{key_prefix}:{class_name}:{instance_id}"
            else:
                method_key_prefix = key_prefix
            
            cache_key = _generate_cache_key(func, args, kwargs, method_key_prefix)
            
            # Try to get cache manager from instance or global
            cm = getattr(self, '_cache_manager', None) or _get_global_cache_manager()
            if not cm:
                return func(self, *args, **kwargs)
            
            try:
                # Try to get from cache
                cached_value = cm.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Method Cache HIT for key: {cache_key}")
                    return cached_value
                
                # Cache miss, execute method
                logger.debug(f"Method Cache MISS for key: {cache_key}")
                start_time = time.time()
                result = func(self, *args, **kwargs)
                duration = time.time() - start_time
                
                # Cache the result
                cm.set(cache_key, result, ttl=ttl, level=level)
                
                # Record operation time if metrics available
                if hasattr(cm, 'metrics'):
                    cm.metrics.record_operation('method_get', cache_key, duration, True)
                
                return result
                
            except Exception as e:
                logger.error(f"Method cache error for key {cache_key}: {e}")
                # Fall back to executing method without caching
                return func(self, *args, **kwargs)
        
        return wrapper
    return decorator


def cache_property(ttl: Optional[int] = None, key_prefix: str = "", level: str = "both"):
    """
    Cache decorator for class properties.
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache keys
        level: Cache level ("L1", "L2", or "both")
    
    Returns:
        Decorated property with caching
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self):
            # Generate cache key
            class_name = self.__class__.__name__
            instance_id = id(self)
            method_name = func.__name__
            cache_key = f"{key_prefix}:{class_name}:{instance_id}:{method_name}"
            
            # Try to get cache manager from instance or global
            cm = getattr(self, '_cache_manager', None) or _get_global_cache_manager()
            if not cm:
                return func(self)
            
            try:
                # Try to get from cache
                cached_value = cm.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Property Cache HIT for key: {cache_key}")
                    return cached_value
                
                # Cache miss, execute property getter
                logger.debug(f"Property Cache MISS for key: {cache_key}")
                start_time = time.time()
                result = func(self)
                duration = time.time() - start_time
                
                # Cache the result
                cm.set(cache_key, result, ttl=ttl, level=level)
                
                # Record operation time if metrics available
                if hasattr(cm, 'metrics'):
                    cm.metrics.record_operation('property_get', cache_key, duration, True)
                
                return result
                
            except Exception as e:
                logger.error(f"Property cache error for key {cache_key}: {e}")
                # Fall back to executing property without caching
                return func(self)
        
        return wrapper
    return decorator


# Global cache manager reference
_global_cache_manager = None


def set_global_cache_manager(cache_manager: Any) -> None:
    """Set the global cache manager for decorators"""
    global _global_cache_manager
    _global_cache_manager = cache_manager
    logger.info(f"Global cache manager set: {type(cache_manager).__name__}")


def get_global_cache_manager() -> Any:
    """Get the global cache manager"""
    return _global_cache_manager


def _get_global_cache_manager() -> Any:
    """Internal function to get global cache manager"""
    return _global_cache_manager


# Utility functions for cache management
def invalidate_pattern(pattern: str, cache_manager: Optional[Any] = None, 
                      level: str = "both") -> int:
    """
    Invalidate cache keys matching a pattern.
    
    Args:
        pattern: Pattern to match cache keys
        cache_manager: Cache manager instance (default: use global cache manager)
        level: Cache level ("L1", "L2", or "both")
    
    Returns:
        Number of keys invalidated
    """
    cm = cache_manager or _get_global_cache_manager()
    if not cm:
        return 0
    
    try:
        keys_to_invalidate = cm.get_keys(pattern)
        invalidated_count = 0
        
        for key in keys_to_invalidate:
            if cm.delete(key, level=level):
                invalidated_count += 1
                logger.debug(f"Invalidated cache key: {key}")
        
        logger.info(f"Invalidated {invalidated_count} cache keys matching pattern: {pattern}")
        return invalidated_count
        
    except Exception as e:
        logger.error(f"Cache invalidation error: {e}")
        return 0


async def invalidate_pattern_async(pattern: str, cache_manager: Optional[Any] = None,
                                 level: str = "both") -> int:
    """
    Asynchronously invalidate cache keys matching a pattern.
    
    Args:
        pattern: Pattern to match cache keys
        cache_manager: Cache manager instance (default: use global cache manager)
        level: Cache level ("L1", "L2", or "both")
    
    Returns:
        Number of keys invalidated
    """
    cm = cache_manager or _get_global_cache_manager()
    if not cm:
        return 0
    
    try:
        keys_to_invalidate = cm.get_keys(pattern)
        invalidated_count = 0
        
        for key in keys_to_invalidate:
            if await cm.delete_async(key, level=level):
                invalidated_count += 1
                logger.debug(f"Invalidated async cache key: {key}")
        
        logger.info(f"Invalidated {invalidated_count} async cache keys matching pattern: {pattern}")
        return invalidated_count
        
    except Exception as e:
        logger.error(f"Async cache invalidation error: {e}")
        return 0


def clear_all_caches(cache_manager: Optional[Any] = None, level: str = "both") -> bool:
    """
    Clear all caches.
    
    Args:
        cache_manager: Cache manager instance (default: use global cache manager)
        level: Cache level ("L1", "L2", or "both")
    
    Returns:
        True if successful
    """
    cm = cache_manager or _get_global_cache_manager()
    if not cm:
        return False
    
    try:
        success = cm.clear(level=level)
        if success:
            logger.info(f"Cleared all caches at level: {level}")
        return success
        
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        return False


async def clear_all_caches_async(cache_manager: Optional[Any] = None, 
                                level: str = "both") -> bool:
    """
    Asynchronously clear all caches.
    
    Args:
        cache_manager: Cache manager instance (default: use global cache manager)
        level: Cache level ("L1", "L2", or "both")
    
    Returns:
        True if successful
    """
    cm = cache_manager or _get_global_cache_manager()
    if not cm:
        return False
    
    try:
        success = await cm.clear_async(level=level)
        if success:
            logger.info(f"Cleared all async caches at level: {level}")
        return success
        
    except Exception as e:
        logger.error(f"Async cache clear error: {e}")
        return False
