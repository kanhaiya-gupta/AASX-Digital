"""
Cache Manager
============

Central orchestrator for multi-level caching system.
Manages L1 (memory) and L2 (persistent) cache stores.
"""

import asyncio
import logging
import threading
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

from .cache_store import CacheStore
from .cache_policy import CachePolicy, EvictionPolicy, TTLPolicy
from .cache_metrics import CacheMetrics

logger = logging.getLogger(__name__)


class CacheManager:
    """Synchronous cache manager for multi-level caching"""
    
    def __init__(self, name: str = "CacheManager", 
                 l1_store: Optional[CacheStore] = None,
                 l2_store: Optional[CacheStore] = None,
                 policy: Optional[CachePolicy] = None):
        self.name = name
        self.l1_store = l1_store or MemoryCacheStore(f"{name}_L1")
        self.l2_store = l2_store
        self.policy = policy or CachePolicy()
        self.metrics = CacheMetrics()
        self._lock = threading.RLock()
        self._enabled = True
        
        # Cache warming and invalidation callbacks
        self._warming_callbacks: List[Callable] = []
        self._invalidation_callbacks: List[Callable] = []
        
        logger.info(f"CacheManager {name} initialized with L1: {self.l1_store.name}")
        if self.l2_store:
            logger.info(f"CacheManager {name} initialized with L2: {self.l2_store.name}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache using multi-level strategy.
        
        Args:
            key: Cache key
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        if not self._enabled:
            return default
        
        try:
            # Try L1 cache first
            value = self.l1_store.get(key)
            if value is not None:
                self.metrics.record_hit("L1")
                return value
            
            # Try L2 cache if available
            if self.l2_store:
                value = self.l2_store.get(key)
                if value is not None:
                    # Promote to L1 cache
                    self.l1_store.set(key, value, ttl=self.policy.ttl_policy.get_ttl(key))
                    self.metrics.record_hit("L2")
                    return value
            
            self.metrics.record_miss(key)
            return default
            
        except Exception as e:
            logger.error(f"Error getting key {key} from cache: {e}")
            self.metrics.record_error()
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
            level: str = "both") -> bool:
        """
        Set value in cache at specified level(s).
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            level: Cache level ("L1", "L2", or "both")
            
        Returns:
            True if successful
        """
        if not self._enabled:
            return False
        
        try:
            success = True
            ttl = ttl or self.policy.ttl_policy.get_ttl(key)
            
            # Set in L1 cache
            if level in ["L1", "both"]:
                success &= self.l1_store.set(key, value, ttl)
            
            # Set in L2 cache
            if level in ["L2", "both"] and self.l2_store:
                success &= self.l2_store.set(key, value, ttl)
            
            if success:
                self.metrics.record_set(key)
                self._notify_invalidation_callbacks(key, "set")
            
            return success
            
        except Exception as e:
            logger.error(f"Error setting key {key} in cache: {e}")
            self.metrics.record_error()
            return False
    
    def delete(self, key: str, level: str = "both") -> bool:
        """
        Delete key from cache at specified level(s).
        
        Args:
            key: Cache key to delete
            level: Cache level ("L1", "L2", or "both")
            
        Returns:
            True if successful
        """
        if not self._enabled:
            return False
        
        try:
            success = True
            
            # Delete from L1 cache
            if level in ["L1", "both"]:
                success &= self.l1_store.delete(key)
            
            # Delete from L2 cache
            if level in ["L2", "both"] and self.l2_store:
                success &= self.l2_store.delete(key)
            
            if success:
                self.metrics.record_delete(key)
                self._notify_invalidation_callbacks(key, "delete")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting key {key} from cache: {e}")
            self.metrics.record_error()
            return False
    
    def clear(self, level: str = "both") -> bool:
        """
        Clear all cache data at specified level(s).
        
        Args:
            level: Cache level ("L1", "L2", or "both")
            
        Returns:
            True if successful
        """
        if not self._enabled:
            return False
        
        try:
            success = True
            
            # Clear L1 cache
            if level in ["L1", "both"]:
                success &= self.l1_store.clear()
            
            # Clear L2 cache
            if level in ["L2", "both"] and self.l2_store:
                success &= self.l2_store.clear()
            
            if success:
                self.metrics.record_clear()
                self._notify_invalidation_callbacks(None, "clear")
            
            return success
            
        except Exception as e:
            logger.error(f"Error clearing cache level {level}: {e}")
            self.metrics.record_error()
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in any cache level"""
        if not self._enabled:
            return False
        
        try:
            # Check L1 cache
            if self.l1_store.exists(key):
                return True
            
            # Check L2 cache
            if self.l2_store and self.l2_store.exists(key):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking existence of key {key}: {e}")
            return False
    
    def get_keys(self, pattern: str = "*") -> List[str]:
        """Get all keys matching pattern from all cache levels"""
        if not self._enabled:
            return []
        
        try:
            keys = set()
            
            # Get keys from L1 cache
            l1_keys = self.l1_store.get_keys(pattern)
            keys.update(l1_keys)
            
            # Get keys from L2 cache
            if self.l2_store:
                l2_keys = self.l2_store.get_keys(pattern)
                keys.update(l2_keys)
            
            return list(keys)
            
        except Exception as e:
            logger.error(f"Error getting keys with pattern {pattern}: {e}")
            return []
    
    def warm_cache(self, keys: List[str]) -> int:
        """
        Warm cache by pre-loading specified keys.
        
        Args:
            keys: List of keys to warm
            
        Returns:
            Number of keys successfully warmed
        """
        if not self._enabled:
            return 0
        
        try:
            warmed_count = 0
            
            for key in keys:
                # Try to get from L2 and promote to L1
                if self.l2_store:
                    value = self.l2_store.get(key)
                    if value is not None:
                        self.l1_store.set(key, value, ttl=self.policy.ttl_policy.get_ttl(key))
                        warmed_count += 1
            
            self.metrics.record_warm(warmed_count)
            logger.info(f"Cache warmed with {warmed_count}/{len(keys)} keys")
            
            return warmed_count
            
        except Exception as e:
            logger.error(f"Error warming cache: {e}")
            return 0
    
    def add_warming_callback(self, callback: Callable) -> None:
        """Add callback for cache warming events"""
        self._warming_callbacks.append(callback)
    
    def add_invalidation_callback(self, callback: Callable) -> None:
        """Add callback for cache invalidation events"""
        self._invalidation_callbacks.append(callback)
    
    def _notify_invalidation_callbacks(self, key: Optional[str], action: str) -> None:
        """Notify invalidation callbacks"""
        for callback in self._invalidation_callbacks:
            try:
                callback(key, action)
            except Exception as e:
                logger.error(f"Error in invalidation callback: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        stats = {
            'manager': {
                'name': self.name,
                'enabled': self._enabled,
                'l1_store': self.l1_store.name if self.l1_store else None,
                'l2_store': self.l2_store.name if self.l2_store else None
            },
            'metrics': self.metrics.get_stats(),
            'l1_stats': self.l1_store.get_stats() if self.l1_store else None,
            'l2_stats': self.l2_store.get_stats() if self.l2_store else None
        }
        
        if self.policy:
            stats['policy'] = self.policy.get_stats()
        
        return stats
    
    def enable(self) -> None:
        """Enable the cache manager"""
        self._enabled = True
        logger.info(f"CacheManager {self.name} enabled")
    
    def disable(self) -> None:
        """Disable the cache manager"""
        self._enabled = False
        logger.info(f"CacheManager {self.name} disabled")
    
    def is_enabled(self) -> bool:
        """Check if cache manager is enabled"""
        return self._enabled


class AsyncCacheManager(CacheManager):
    """Asynchronous cache manager for multi-level caching"""
    
    def __init__(self, name: str = "AsyncCacheManager", 
                 l1_store: Optional[CacheStore] = None,
                 l2_store: Optional[CacheStore] = None,
                 policy: Optional[CachePolicy] = None):
        super().__init__(name, l1_store, l2_store, policy)
        self._async_lock = asyncio.Lock()
    
    async def get_async(self, key: str, default: Any = None) -> Any:
        """Asynchronous version of get method"""
        if not self._enabled:
            return default
        
        try:
            async with self._async_lock:
                # Try L1 cache first
                value = await self.l1_store.get_async(key)
                if value is not None:
                    self.metrics.record_hit("L1")
                    return value
                
                # Try L2 cache if available
                if self.l2_store:
                    value = await self.l2_store.get_async(key)
                    if value is not None:
                        # Promote to L1 cache
                        await self.l1_store.set_async(key, value, 
                                                     ttl=self.policy.ttl_policy.get_ttl(key))
                        self.metrics.record_hit("L2")
                        return value
                
                self.metrics.record_miss(key)
                return default
                
        except Exception as e:
            logger.error(f"Error getting key {key} from async cache: {e}")
            self.metrics.record_error()
            return default
    
    async def set_async(self, key: str, value: Any, ttl: Optional[int] = None,
                       level: str = "both") -> bool:
        """Asynchronous version of set method"""
        if not self._enabled:
            return False
        
        try:
            async with self._async_lock:
                success = True
                ttl = ttl or self.policy.ttl_policy.get_ttl(key)
                
                # Set in L1 cache
                if level in ["L1", "both"]:
                    success &= await self.l1_store.set_async(key, value, ttl)
                
                # Set in L2 cache
                if level in ["L2", "both"] and self.l2_store:
                    success &= await self.l2_store.set_async(key, value, ttl)
                
                if success:
                    self.metrics.record_set(key)
                    self._notify_invalidation_callbacks(key, "set")
                
                return success
                
        except Exception as e:
            logger.error(f"Error setting key {key} in async cache: {e}")
            self.metrics.record_error()
            return False
    
    async def delete_async(self, key: str, level: str = "both") -> bool:
        """Asynchronous version of delete method"""
        if not self._enabled:
            return False
        
        try:
            async with self._async_lock:
                success = True
                
                # Delete from L1 cache
                if level in ["L1", "both"]:
                    success &= await self.l1_store.delete_async(key)
                
                # Delete from L2 cache
                if level in ["L2", "both"] and self.l2_store:
                    success &= await self.l2_store.delete_async(key)
                
                if success:
                    self.metrics.record_delete(key)
                    self._notify_invalidation_callbacks(key, "delete")
                
                return success
                
        except Exception as e:
            logger.error(f"Error deleting key {key} from async cache: {e}")
            self.metrics.record_error()
            return False
    
    async def clear_async(self, level: str = "both") -> bool:
        """Asynchronous version of clear method"""
        if not self._enabled:
            return False
        
        try:
            async with self._async_lock:
                success = True
                
                # Clear L1 cache
                if level in ["L1", "both"]:
                    success &= await self.l1_store.clear_async()
                
                # Clear L2 cache
                if level in ["L2", "both"] and self.l2_store:
                    success &= await self.l2_store.clear_async()
                
                if success:
                    self.metrics.record_clear()
                    self._notify_invalidation_callbacks(None, "clear")
                
                return success
                
        except Exception as e:
            logger.error(f"Error clearing async cache level {level}: {e}")
            self.metrics.record_error()
            return False
    
    async def warm_cache_async(self, keys: List[str]) -> int:
        """Asynchronous version of warm_cache method"""
        if not self._enabled:
            return 0
        
        try:
            async with self._async_lock:
                warmed_count = 0
                
                for key in keys:
                    # Try to get from L2 and promote to L1
                    if self.l2_store:
                        value = await self.l2_store.get_async(key)
                        if value is not None:
                            await self.l1_store.set_async(key, value, 
                                                        ttl=self.policy.ttl_policy.get_ttl(key))
                            warmed_count += 1
                
                self.metrics.record_warm(warmed_count)
                logger.info(f"Async cache warmed with {warmed_count}/{len(keys)} keys")
                
                return warmed_count
                
        except Exception as e:
            logger.error(f"Error warming async cache: {e}")
            return 0
