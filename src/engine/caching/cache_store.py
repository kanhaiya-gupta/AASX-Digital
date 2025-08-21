"""
Cache Store
==========

Abstract base class and concrete implementations for cache stores.
Supports both synchronous and asynchronous operations.
"""

import asyncio
import logging
import threading
import time
import json
import pickle
import os
import hashlib
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from collections import OrderedDict
from pathlib import Path

logger = logging.getLogger(__name__)


class CacheStore(ABC):
    """Abstract base class for cache stores"""
    
    def __init__(self, name: str = "CacheStore"):
        self.name = name
        self.enabled = True
        self._stats = {
            'gets': 0,
            'sets': 0,
            'deletes': 0,
            'hits': 0,
            'misses': 0,
            'errors': 0,
            'size': 0
        }
    
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache store"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None, level: str = "L1") -> bool:
        """Set value in cache store"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete key from cache store"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache store"""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Clear all data from cache store"""
        pass
    
    @abstractmethod
    def get_keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern"""
        pass
    
    # Async methods with default implementations
    async def get_async(self, key: str, default: Any = None) -> Any:
        """Asynchronous version of get method"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get, key, default)
    
    async def set_async(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Asynchronous version of set method"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.set, key, value, ttl)
    
    async def delete_async(self, key: str) -> bool:
        """Asynchronous version of delete method"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.delete, key)
    
    async def clear_async(self) -> bool:
        """Asynchronous version of clear method"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.clear)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache store statistics"""
        return self._stats.copy()
    
    def reset_stats(self) -> None:
        """Reset cache store statistics"""
        self._stats = {
            'gets': 0,
            'sets': 0,
            'deletes': 0,
            'hits': 0,
            'misses': 0,
            'errors': 0,
            'size': 0
        }
    
    def enable(self) -> None:
        """Enable the cache store"""
        self.enabled = True
        logger.info(f"CacheStore {self.name} enabled")
    
    def disable(self) -> None:
        """Disable the cache store"""
        self.enabled = False
        logger.info(f"CacheStore {self.name} disabled")
    
    def is_enabled(self) -> bool:
        """Check if cache store is enabled"""
        return self.enabled


class MemoryCacheStore(CacheStore):
    """In-memory cache store using OrderedDict with LRU eviction"""
    
    def __init__(self, name: str = "MemoryCacheStore", max_size: int = 1000):
        super().__init__(name)
        self.max_size = max_size
        self._cache: OrderedDict = OrderedDict()
        self._expiry: Dict[str, float] = {}
        self._lock = threading.RLock()
        
        logger.info(f"MemoryCacheStore {name} initialized with max_size={max_size}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from memory cache"""
        if not self.enabled:
            return default
        
        try:
            with self._lock:
                self._stats['gets'] += 1
                
                # Check if key exists and is not expired
                if key in self._cache:
                    expiry = self._expiry.get(key)
                    if expiry is None or time.time() < expiry:
                        # Move to end (LRU)
                        value = self._cache.pop(key)
                        self._cache[key] = value
                        self._stats['hits'] += 1
                        return value
                    else:
                        # Key expired, remove it
                        del self._cache[key]
                        del self._expiry[key]
                        self._stats['size'] = len(self._cache)
                
                self._stats['misses'] += 1
                return default
                
        except Exception as e:
            logger.error(f"Error getting key {key} from memory cache: {e}")
            self._stats['errors'] += 1
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, level: str = "L1") -> bool:
        """Set value in memory cache"""
        if not self.enabled:
            return False
        
        try:
            with self._lock:
                # Remove existing key if present
                if key in self._cache:
                    del self._cache[key]
                    if key in self._expiry:
                        del self._expiry[key]
                
                # Check if we need to evict items
                while len(self._cache) >= self.max_size:
                    # Remove oldest item (LRU)
                    oldest_key = next(iter(self._cache))
                    del self._cache[oldest_key]
                    if oldest_key in self._expiry:
                        del self._expiry[oldest_key]
                
                # Add new item
                self._cache[key] = value
                if ttl:
                    self._expiry[key] = time.time() + ttl
                
                self._stats['sets'] += 1
                self._stats['size'] = len(self._cache)
                
                return True
                
        except Exception as e:
            logger.error(f"Error setting key {key} in memory cache: {e}")
            self._stats['errors'] += 1
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from memory cache"""
        if not self.enabled:
            return False
        
        try:
            with self._lock:
                if key in self._cache:
                    del self._cache[key]
                    if key in self._expiry:
                        del self._expiry[key]
                    self._stats['deletes'] += 1
                    self._stats['size'] = len(self._cache)
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error deleting key {key} from memory cache: {e}")
            self._stats['errors'] += 1
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired"""
        if not self.enabled:
            return False
        
        try:
            with self._lock:
                if key in self._cache:
                    expiry = self._expiry.get(key)
                    if expiry is None or time.time() < expiry:
                        return True
                    else:
                        # Key expired, remove it
                        del self._cache[key]
                        del self._expiry[key]
                        self._stats['size'] = len(self._cache)
                return False
                
        except Exception as e:
            logger.error(f"Error checking existence of key {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all data from memory cache"""
        if not self.enabled:
            return False
        
        try:
            with self._lock:
                self._cache.clear()
                self._expiry.clear()
                self._stats['size'] = 0
                return True
                
        except Exception as e:
            logger.error(f"Error clearing memory cache: {e}")
            return False
    
    def get_keys(self, pattern: str = "*") -> List[str]:
        """Get all keys (simple pattern matching)"""
        if not self.enabled:
            return []
        
        try:
            with self._lock:
                keys = []
                current_time = time.time()
                
                for key in self._cache.keys():
                    # Check if key is not expired
                    expiry = self._expiry.get(key)
                    if expiry is None or current_time < expiry:
                        # Simple pattern matching
                        if pattern == "*" or pattern in key:
                            keys.append(key)
                
                return keys
                
        except Exception as e:
            logger.error(f"Error getting keys from memory cache: {e}")
            return []
    
    def cleanup_expired(self) -> int:
        """Remove expired keys and return count of removed keys"""
        if not self.enabled:
            return 0
        
        try:
            with self._lock:
                current_time = time.time()
                expired_keys = []
                
                for key, expiry in self._expiry.items():
                    if current_time >= expiry:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self._cache[key]
                    del self._expiry[key]
                
                self._stats['size'] = len(self._cache)
                return len(expired_keys)
                
        except Exception as e:
            logger.error(f"Error cleaning up expired keys: {e}")
            return 0


class DiskCacheStore(CacheStore):
    """Disk-based cache store for persistent file caching"""
    
    def __init__(self, name: str = "DiskCacheStore", 
                 cache_dir: str = ".cache",
                 max_size_mb: int = 100,
                 compression_enabled: bool = False):
        super().__init__(name)
        self.cache_dir = Path(cache_dir)
        self.max_size_mb = max_size_mb
        self.compression_enabled = compression_enabled
        self._lock = threading.RLock()
        self._metadata_file = self.cache_dir / "metadata.json"
        self._metadata: Dict[str, Dict[str, Any]] = {}
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing metadata
        self._load_metadata()
        
        logger.info(f"DiskCacheStore {name} initialized at {self.cache_dir}")
    
    def _get_key_path(self, key: str) -> Path:
        """Get file path for a cache key"""
        # Create a safe filename from the key
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{safe_key}.cache"
    
    def _load_metadata(self) -> None:
        """Load metadata from disk"""
        try:
            if self._metadata_file.exists():
                with open(self._metadata_file, 'r') as f:
                    self._metadata = json.load(f)
                    
                # Clean up expired entries
                self._cleanup_expired()
                
                # Update size stats
                self._update_size_stats()
                
        except Exception as e:
            logger.warning(f"Could not load metadata: {e}")
            self._metadata = {}
    
    def _save_metadata(self) -> None:
        """Save metadata to disk"""
        try:
            with open(self._metadata_file, 'w') as f:
                json.dump(self._metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries from metadata"""
        current_time = time.time()
        expired_keys = []
        
        for key, info in self._metadata.items():
            if 'expiry' in info and current_time >= info['expiry']:
                expired_keys.append(key)
        
        for key in expired_keys:
            self._delete_file(key)
            del self._metadata[key]
        
        if expired_keys:
            self._save_metadata()
    
    def _delete_file(self, key: str) -> None:
        """Delete cache file for a key"""
        try:
            file_path = self._get_key_path(key)
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            logger.warning(f"Error deleting cache file for key {key}: {e}")
    
    def _update_size_stats(self) -> None:
        """Update size statistics"""
        total_size = 0
        for key, info in self._metadata.items():
            total_size += info.get('size', 0)
        
        self._stats['size'] = len(self._metadata)
    
    def _check_size_limit(self) -> bool:
        """Check if cache size is within limits"""
        total_size_mb = sum(info.get('size', 0) for info in self._metadata.values()) / (1024 * 1024)
        return total_size_mb <= self.max_size_mb
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from disk cache"""
        if not self.enabled:
            return default
        
        try:
            with self._lock:
                self._stats['gets'] += 1
                
                # Check if key exists in metadata
                if key not in self._metadata:
                    self._stats['misses'] += 1
                    return default
                
                info = self._metadata[key]
                
                # Check if expired
                if 'expiry' in info and time.time() >= info['expiry']:
                    self.delete(key)
                    self._stats['misses'] += 1
                    return default
                
                # Read from file
                file_path = self._get_key_path(key)
                if not file_path.exists():
                    # File missing, remove from metadata
                    del self._metadata[key]
                    self._stats['misses'] += 1
                    return default
                
                try:
                    with open(file_path, 'rb') as f:
                        data = f.read()
                    
                    # Deserialize based on format
                    format_type = info.get('format', 'pickle')
                    if format_type == 'json':
                        value = json.loads(data.decode('utf-8'))
                    else:
                        value = pickle.loads(data)
                    
                    self._stats['hits'] += 1
                    return value
                    
                except Exception as e:
                    logger.warning(f"Error reading cache file for key {key}: {e}")
                    self.delete(key)
                    self._stats['misses'] += 1
                    return default
                
        except Exception as e:
            logger.error(f"Error getting key {key} from disk cache: {e}")
            self._stats['errors'] += 1
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, level: str = "L2") -> bool:
        """Set value in disk cache"""
        if not self.enabled:
            return False
        
        try:
            with self._lock:
                # Check size limit
                if not self._check_size_limit():
                    # Remove oldest entries to make space
                    self._evict_oldest()
                
                # Determine serialization format
                if isinstance(value, (dict, list, tuple)):
                    format_type = 'json'
                    serialized = json.dumps(value).encode('utf-8')
                else:
                    format_type = 'pickle'
                    serialized = pickle.dumps(value)
                
                # Write to file
                file_path = self._get_key_path(key)
                with open(file_path, 'wb') as f:
                    f.write(serialized)
                
                # Update metadata
                self._metadata[key] = {
                    'size': len(serialized),
                    'format': format_type,
                    'created': time.time(),
                    'expiry': time.time() + ttl if ttl else None
                }
                
                self._save_metadata()
                self._stats['sets'] += 1
                self._update_size_stats()
                
                return True
                
        except Exception as e:
            logger.error(f"Error setting key {key} in disk cache: {e}")
            self._stats['errors'] += 1
            return False
    
    def _evict_oldest(self) -> None:
        """Evict oldest cache entries to make space"""
        # Sort by creation time (oldest first)
        sorted_keys = sorted(
            self._metadata.items(),
            key=lambda x: x[1].get('created', 0)
        )
        
        # Remove oldest entries until we're under the limit
        for key, _ in sorted_keys:
            if self._check_size_limit():
                break
            self.delete(key)
    
    def delete(self, key: str) -> bool:
        """Delete key from disk cache"""
        if not self.enabled:
            return False
        
        try:
            with self._lock:
                if key in self._metadata:
                    self._delete_file(key)
                    del self._metadata[key]
                    self._save_metadata()
                    self._stats['deletes'] += 1
                    self._update_size_stats()
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error deleting key {key} from disk cache: {e}")
            self._stats['errors'] += 1
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired"""
        if not self.enabled:
            return False
        
        try:
            with self._lock:
                if key not in self._metadata:
                    return False
                
                info = self._metadata[key]
                
                # Check if expired
                if 'expiry' in info and time.time() >= info['expiry']:
                    self.delete(key)
                    return False
                
                # Check if file exists
                file_path = self._get_key_path(key)
                return file_path.exists()
                
        except Exception as e:
            logger.error(f"Error checking existence of key {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all data from disk cache"""
        if not self.enabled:
            return False
        
        try:
            with self._lock:
                # Delete all cache files
                for key in list(self._metadata.keys()):
                    self._delete_file(key)
                
                # Clear metadata
                self._metadata.clear()
                self._save_metadata()
                self._stats['size'] = 0
                return True
                
        except Exception as e:
            logger.error(f"Error clearing disk cache: {e}")
            return False
    
    def get_keys(self, pattern: str = "*") -> List[str]:
        """Get all keys matching pattern"""
        if not self.enabled:
            return []
        
        try:
            with self._lock:
                keys = []
                current_time = time.time()
                
                for key, info in self._metadata.items():
                    # Check if not expired
                    if 'expiry' not in info or current_time < info['expiry']:
                        # Simple pattern matching
                        if pattern == "*" or pattern in key:
                            keys.append(key)
                
                return keys
                
        except Exception as e:
            logger.error(f"Error getting keys from disk cache: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get disk cache statistics including disk usage"""
        stats = super().get_stats()
        
        try:
            total_size_bytes = sum(info.get('size', 0) for info in self._metadata.values())
            stats['disk_usage'] = {
                'total_size_mb': total_size_bytes / (1024 * 1024),
                'max_size_mb': self.max_size_mb,
                'cache_dir': str(self.cache_dir),
                'files_count': len(self._metadata)
            }
        except Exception as e:
            logger.warning(f"Could not calculate disk usage: {e}")
        
        return stats


class RedisCacheStore(CacheStore):
    """Redis-based cache store for persistent caching"""
    
    def __init__(self, name: str = "RedisCacheStore", 
                 host: str = "localhost", port: int = 6379, 
                 db: int = 0, password: Optional[str] = None,
                 max_connections: int = 10):
        super().__init__(name)
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.max_connections = max_connections
        self._redis = None
        self._lock = threading.RLock()
        
        # Try to import redis
        try:
            import redis
            self._redis_client = redis
            logger.info(f"RedisCacheStore {name} initialized for {host}:{port}")
        except ImportError:
            logger.warning("Redis package not installed. Install with: pip install redis")
            self._redis_client = None
    
    def _get_redis(self):
        """Get Redis connection"""
        if not self._redis_client:
            return None
        
        try:
            if not self._redis:
                with self._lock:
                    if not self._redis:
                        self._redis = self._redis_client.Redis(
                            host=self.host,
                            port=self.port,
                            db=self.db,
                            password=self.password,
                            max_connections=self.max_connections,
                            decode_responses=True
                        )
                        # Test connection
                        self._redis.ping()
            return self._redis
        except Exception as e:
            logger.error(f"Error connecting to Redis: {e}")
            return None
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from Redis cache"""
        if not self.enabled:
            return default
        
        redis_client = self._get_redis()
        if not redis_client:
            return default
        
        try:
            self._stats['gets'] += 1
            
            # Try to get value
            value = redis_client.get(key)
            if value is not None:
                # Try to deserialize
                try:
                    if value.startswith('json:'):
                        deserialized = json.loads(value[5:])
                    elif value.startswith('pickle:'):
                        deserialized = pickle.loads(value[7:].encode())
                    else:
                        deserialized = value
                    
                    self._stats['hits'] += 1
                    return deserialized
                except Exception as e:
                    logger.warning(f"Error deserializing value for key {key}: {e}")
                    return value
            else:
                self._stats['misses'] += 1
                return default
                
        except Exception as e:
            logger.error(f"Error getting key {key} from Redis cache: {e}")
            self._stats['errors'] += 1
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, level: str = "L2") -> bool:
        """Set value in Redis cache"""
        if not self.enabled:
            return False
        
        redis_client = self._get_redis()
        if not redis_client:
            return False
        
        try:
            # Serialize value
            if isinstance(value, (dict, list, tuple)):
                serialized = f"json:{json.dumps(value)}"
            else:
                try:
                    serialized = f"pickle:{pickle.dumps(value).decode('latin1')}"
                except Exception:
                    serialized = str(value)
            
            # Set in Redis
            if ttl:
                success = redis_client.setex(key, ttl, serialized)
            else:
                success = redis_client.set(key, serialized)
            
            if success:
                self._stats['sets'] += 1
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error setting key {key} in Redis cache: {e}")
            self._stats['errors'] += 1
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from Redis cache"""
        if not self.enabled:
            return False
        
        redis_client = self._get_redis()
        if not redis_client:
            return False
        
        try:
            result = redis_client.delete(key)
            if result > 0:
                self._stats['deletes'] += 1
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting key {key} from Redis cache: {e}")
            self._stats['errors'] += 1
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache"""
        if not self.enabled:
            return False
        
        redis_client = self._get_redis()
        if not redis_client:
            return False
        
        try:
            return bool(redis_client.exists(key))
        except Exception as e:
            logger.error(f"Error checking existence of key {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all data from Redis cache (flush current database)"""
        if not self.enabled:
            return False
        
        redis_client = self._get_redis()
        if not redis_client:
            return False
        
        try:
            redis_client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Error clearing Redis cache: {e}")
            return False
    
    def get_keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern from Redis cache"""
        if not self.enabled:
            return []
        
        redis_client = self._get_redis()
        if not redis_client:
            return []
        
        try:
            if pattern == "*":
                pattern = "*"
            return redis_client.keys(pattern)
        except Exception as e:
            logger.error(f"Error getting keys from Redis cache: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics including Redis info"""
        stats = super().get_stats()
        
        redis_client = self._get_redis()
        if redis_client:
            try:
                info = redis_client.info()
                stats['redis_info'] = {
                    'version': info.get('redis_version'),
                    'connected_clients': info.get('connected_clients'),
                    'used_memory': info.get('used_memory_human'),
                    'keyspace': info.get('db0', {}).get('keys', 0)
                }
            except Exception as e:
                logger.warning(f"Could not get Redis info: {e}")
        
        return stats
