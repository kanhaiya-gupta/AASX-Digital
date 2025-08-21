"""
Cache Policy
===========

Cache policies for TTL management, eviction strategies, and behavior configuration.
"""

import logging
import time
import re
from typing import Any, Dict, List, Optional, Union, Callable
from abc import ABC, abstractmethod
from enum import Enum

logger = logging.getLogger(__name__)


class EvictionStrategy(Enum):
    """Cache eviction strategies"""
    LRU = "lru"           # Least Recently Used
    LFU = "lfu"           # Least Frequently Used
    FIFO = "fifo"         # First In, First Out
    RANDOM = "random"     # Random eviction
    TTL = "ttl"           # Time To Live based


class TTLStrategy(Enum):
    """TTL (Time To Live) strategies"""
    FIXED = "fixed"           # Fixed TTL for all keys
    SLIDING = "sliding"       # Sliding TTL (reset on access)
    ADAPTIVE = "adaptive"     # Adaptive TTL based on access patterns
    PATTERN_BASED = "pattern" # TTL based on key patterns


class TTLPolicy:
    """Time To Live policy management"""
    
    def __init__(self, default_ttl: int = 3600, 
                 strategy: TTLStrategy = TTLStrategy.FIXED,
                 pattern_rules: Optional[Dict[str, int]] = None):
        self.default_ttl = default_ttl
        self.strategy = strategy
        self.pattern_rules = pattern_rules or {}
        self._access_times: Dict[str, float] = {}
        self._access_counts: Dict[str, int] = {}
        
        logger.info(f"TTLPolicy initialized with strategy: {strategy.value}, default_ttl: {default_ttl}")
    
    def get_ttl(self, key: str) -> int:
        """
        Get TTL for a specific key based on policy.
        
        Args:
            key: Cache key
            
        Returns:
            TTL in seconds
        """
        # Check pattern-based rules first
        for pattern, ttl in self.pattern_rules.items():
            if re.match(pattern, key):
                return ttl
        
        # Return default TTL
        return self.default_ttl
    
    def update_access(self, key: str) -> None:
        """Update access information for a key"""
        current_time = time.time()
        self._access_times[key] = current_time
        self._access_counts[key] = self._access_counts.get(key, 0) + 1
    
    def get_adaptive_ttl(self, key: str) -> int:
        """Get adaptive TTL based on access patterns"""
        if key not in self._access_counts:
            return self.default_ttl
        
        access_count = self._access_counts[key]
        base_ttl = self.default_ttl
        
        # Increase TTL for frequently accessed keys
        if access_count > 10:
            return base_ttl * 2
        elif access_count > 5:
            return int(base_ttl * 1.5)
        else:
            return base_ttl
    
    def get_sliding_ttl(self, key: str) -> int:
        """Get sliding TTL (reset on access)"""
        return self.get_ttl(key)
    
    def should_extend_ttl(self, key: str) -> bool:
        """Check if TTL should be extended for a key"""
        if self.strategy == TTLStrategy.SLIDING:
            return True
        elif self.strategy == TTLStrategy.ADAPTIVE:
            return self._access_counts.get(key, 0) > 5
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get TTL policy statistics"""
        return {
            'strategy': self.strategy.value,
            'default_ttl': self.default_ttl,
            'pattern_rules': self.pattern_rules,
            'tracked_keys': len(self._access_times),
            'total_accesses': sum(self._access_counts.values())
        }


class EvictionPolicy:
    """Cache eviction policy management"""
    
    def __init__(self, strategy: EvictionStrategy = EvictionStrategy.LRU,
                 max_size: int = 1000,
                 max_memory_mb: Optional[int] = None):
        self.strategy = strategy
        self.max_size = max_size
        self.max_memory_mb = max_memory_mb
        self._access_times: Dict[str, float] = {}
        self._access_counts: Dict[str, int] = {}
        self._insertion_times: Dict[str, float] = {}
        
        logger.info(f"EvictionPolicy initialized with strategy: {strategy.value}, max_size: {max_size}")
    
    def should_evict(self, current_size: int, current_memory_mb: Optional[float] = None) -> bool:
        """
        Check if eviction should occur.
        
        Args:
            current_size: Current number of items
            current_memory_mb: Current memory usage in MB
            
        Returns:
            True if eviction should occur
        """
        if current_size >= self.max_size:
            return True
        
        if self.max_memory_mb and current_memory_mb and current_memory_mb >= self.max_memory_mb:
            return True
        
        return False
    
    def get_keys_to_evict(self, keys: List[str], count: int = 1) -> List[str]:
        """
        Get keys that should be evicted based on policy.
        
        Args:
            keys: List of available keys
            count: Number of keys to evict
            
        Returns:
            List of keys to evict
        """
        if not keys:
            return []
        
        if self.strategy == EvictionStrategy.LRU:
            return self._get_lru_keys(keys, count)
        elif self.strategy == EvictionStrategy.LFU:
            return self._get_lfu_keys(keys, count)
        elif self.strategy == EvictionStrategy.FIFO:
            return self._get_fifo_keys(keys, count)
        elif self.strategy == EvictionStrategy.RANDOM:
            return self._get_random_keys(keys, count)
        elif self.strategy == EvictionStrategy.TTL:
            return self._get_ttl_keys(keys, count)
        else:
            return self._get_lru_keys(keys, count)
    
    def _get_lru_keys(self, keys: List[str], count: int) -> List[str]:
        """Get least recently used keys"""
        if not keys:
            return []
        
        # Sort by access time (oldest first)
        sorted_keys = sorted(keys, key=lambda k: self._access_times.get(k, 0))
        return sorted_keys[:count]
    
    def _get_lfu_keys(self, keys: List[str], count: int) -> List[str]:
        """Get least frequently used keys"""
        if not keys:
            return []
        
        # Sort by access count (lowest first)
        sorted_keys = sorted(keys, key=lambda k: self._access_counts.get(k, 0))
        return sorted_keys[:count]
    
    def _get_fifo_keys(self, keys: List[str], count: int) -> List[str]:
        """Get first in, first out keys"""
        if not keys:
            return []
        
        # Sort by insertion time (oldest first)
        sorted_keys = sorted(keys, key=lambda k: self._insertion_times.get(k, 0))
        return sorted_keys[:count]
    
    def _get_random_keys(self, keys: List[str], count: int) -> List[str]:
        """Get random keys for eviction"""
        import random
        if len(keys) <= count:
            return keys
        return random.sample(keys, count)
    
    def _get_ttl_keys(self, keys: List[str], count: int) -> List[str]:
        """Get keys based on TTL (expired first)"""
        if not keys:
            return []
        
        current_time = time.time()
        # Sort by remaining TTL (expired first)
        sorted_keys = sorted(keys, key=lambda k: self._get_remaining_ttl(k, current_time))
        return sorted_keys[:count]
    
    def _get_remaining_ttl(self, key: str, current_time: float) -> float:
        """Get remaining TTL for a key"""
        # This is a simplified implementation
        # In practice, you'd store TTL information
        return 0.0
    
    def update_access(self, key: str) -> None:
        """Update access information for a key"""
        current_time = time.time()
        self._access_times[key] = current_time
        self._access_counts[key] = self._access_counts.get(key, 0) + 1
    
    def update_insertion(self, key: str) -> None:
        """Update insertion time for a key"""
        self._insertion_times[key] = time.time()
    
    def remove_key(self, key: str) -> None:
        """Remove tracking information for a key"""
        self._access_times.pop(key, None)
        self._access_counts.pop(key, None)
        self._insertion_times.pop(key, None)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get eviction policy statistics"""
        return {
            'strategy': self.strategy.value,
            'max_size': self.max_size,
            'max_memory_mb': self.max_memory_mb,
            'tracked_keys': len(self._access_times),
            'total_accesses': sum(self._access_counts.values())
        }


class CachePolicy:
    """Comprehensive cache policy configuration"""
    
    def __init__(self, ttl_policy: Optional[TTLPolicy] = None,
                 eviction_policy: Optional[EvictionPolicy] = None,
                 compression_enabled: bool = False,
                 serialization_format: str = "auto"):
        self.ttl_policy = ttl_policy or TTLPolicy()
        self.eviction_policy = eviction_policy or EvictionPolicy()
        self.compression_enabled = compression_enabled
        self.serialization_format = serialization_format
        
        logger.info(f"CachePolicy initialized with compression: {compression_enabled}")
    
    def should_compress(self, value: Any) -> bool:
        """Check if value should be compressed"""
        if not self.compression_enabled:
            return False
        
        # Simple heuristic: compress if value is string and large
        if isinstance(value, str) and len(value) > 1024:
            return True
        
        return False
    
    def get_serialization_format(self, value: Any) -> str:
        """Get preferred serialization format for value"""
        if self.serialization_format == "auto":
            if isinstance(value, (dict, list, tuple)):
                return "json"
            else:
                return "pickle"
        return self.serialization_format
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive policy statistics"""
        return {
            'ttl_policy': self.ttl_policy.get_stats(),
            'eviction_policy': self.eviction_policy.get_stats(),
            'compression_enabled': self.compression_enabled,
            'serialization_format': self.serialization_format
        }
