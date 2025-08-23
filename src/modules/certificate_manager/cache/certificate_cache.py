"""
Certificate Cache for Certificate Manager

Handles caching of certificate data for improved performance,
including certificate storage, retrieval, and invalidation.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
import logging
from enum import Enum
from datetime import datetime, timedelta
import json
import hashlib

logger = logging.getLogger(__name__)


class CacheStatus(Enum):
    """Cache entry status values"""
    VALID = "valid"
    EXPIRED = "expired"
    INVALID = "invalid"
    STALE = "stale"
    REFRESHING = "refreshing"
    ERROR = "error"


class CertificateCacheEntry:
    """Certificate cache entry with metadata and lifecycle management"""
    
    def __init__(
        self,
        certificate_id: str,
        certificate_data: Dict[str, Any],
        ttl_seconds: int = 3600,
        created_at: Optional[float] = None
    ):
        """Initialize a certificate cache entry"""
        self.certificate_id = certificate_id
        self.certificate_data = certificate_data
        self.ttl_seconds = ttl_seconds
        self.created_at = created_at or time.time()
        self.last_accessed = self.created_at
        self.access_count = 0
        self.status = CacheStatus.VALID
        self.metadata = {
            "size_bytes": len(json.dumps(certificate_data)),
            "hash": hashlib.sha256(json.dumps(certificate_data, sort_keys=True).encode()).hexdigest(),
            "version": certificate_data.get("version", "1.0"),
            "type": certificate_data.get("type", "unknown")
        }
    
    def is_expired(self) -> bool:
        """Check if the cache entry has expired"""
        return time.time() > (self.created_at + self.ttl_seconds)
    
    def is_stale(self, stale_threshold_seconds: int = 300) -> bool:
        """Check if the cache entry is stale (approaching expiration)"""
        return time.time() > (self.created_at + self.ttl_seconds - stale_threshold_seconds)
    
    def access(self) -> None:
        """Record an access to this cache entry"""
        self.last_accessed = time.time()
        self.access_count += 1
    
    def refresh(self, new_data: Dict[str, Any], new_ttl: Optional[int] = None) -> None:
        """Refresh the cache entry with new data"""
        self.certificate_data = new_data
        self.created_at = time.time()
        self.last_accessed = time.time()
        self.access_count = 0
        self.status = CacheStatus.VALID
        
        if new_ttl is not None:
            self.ttl_seconds = new_ttl
        
        # Update metadata
        self.metadata["size_bytes"] = len(json.dumps(new_data))
        self.metadata["hash"] = hashlib.sha256(json.dumps(new_data, sort_keys=True).encode()).hexdigest()
        self.metadata["version"] = new_data.get("version", "1.0")
        self.metadata["type"] = new_data.get("type", "unknown")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert cache entry to dictionary"""
        return {
            "certificate_id": self.certificate_id,
            "certificate_data": self.certificate_data,
            "ttl_seconds": self.ttl_seconds,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count,
            "status": self.status.value,
            "metadata": self.metadata,
            "is_expired": self.is_expired(),
            "is_stale": self.is_stale()
        }


class CertificateCache:
    """
    Certificate data caching service
    
    Handles:
    - Certificate data storage and retrieval
    - Cache lifecycle management
    - Cache invalidation and refresh
    - Cache statistics and monitoring
    - Cache warming and optimization
    """
    
    def __init__(self):
        """Initialize the certificate cache service"""
        self.cache_statuses = list(CacheStatus)
        
        # Certificate cache storage
        self.certificate_cache: Dict[str, CertificateCacheEntry] = {}
        self.cache_index: Dict[str, List[str]] = {}  # Index by type, status, etc.
        
        # Cache management locks
        self.cache_locks: Dict[str, asyncio.Lock] = {}
        self.global_lock = asyncio.Lock()
        
        # Cache settings
        self.cache_settings = self._initialize_cache_settings()
        
        # Cache statistics
        self.cache_stats = {
            "total_entries": 0,
            "valid_entries": 0,
            "expired_entries": 0,
            "total_hits": 0,
            "total_misses": 0,
            "total_evictions": 0,
            "total_refreshes": 0
        }
        
        # Cache maintenance
        self.maintenance_tasks: List[asyncio.Task] = []
        self.cleanup_interval_seconds = 300  # 5 minutes
        
        logger.info("Certificate Cache service initialized successfully")
    
    def _initialize_cache_settings(self) -> Dict[str, Any]:
        """Initialize cache settings"""
        return {
            "default_ttl_seconds": 3600,  # 1 hour
            "max_cache_size_mb": 512,      # 512 MB
            "max_cache_entries": 10000,    # 10,000 entries
            "stale_threshold_seconds": 300,  # 5 minutes
            "cleanup_interval_seconds": 300,  # 5 minutes
            "cache_warming_enabled": True,
            "auto_refresh_enabled": True,
            "compression_enabled": False
        }
    
    async def cache_certificate(
        self,
        certificate_id: str,
        certificate_data: Dict[str, Any],
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Cache a certificate
        
        Args:
            certificate_id: Unique certificate identifier
            certificate_data: Certificate data to cache
            ttl_seconds: Time to live in seconds (defaults to system default)
            metadata: Additional metadata for the cache entry
            
        Returns:
            Dictionary containing cache operation result
        """
        async with self.global_lock:
            # Use default TTL if none specified
            if ttl_seconds is None:
                ttl_seconds = self.cache_settings["default_ttl_seconds"]
            
            # Check cache size limits
            await self._check_cache_limits()
            
            # Create cache entry
            cache_entry = CertificateCacheEntry(
                certificate_id=certificate_id,
                certificate_data=certificate_data,
                ttl_seconds=ttl_seconds
            )
            
            # Add metadata if provided
            if metadata:
                cache_entry.metadata.update(metadata)
            
            # Store in cache
            self.certificate_cache[certificate_id] = cache_entry
            
            # Update cache index
            await self._update_cache_index(certificate_id, cache_entry)
            
            # Update statistics
            self.cache_stats["total_entries"] += 1
            self.cache_stats["valid_entries"] += 1
            
            logger.info(f"Certificate '{certificate_id}' cached with TTL {ttl_seconds}s")
            
            return {
                "status": "success",
                "certificate_id": certificate_id,
                "cached_at": cache_entry.created_at,
                "expires_at": cache_entry.created_at + cache_entry.ttl_seconds,
                "size_bytes": cache_entry.metadata["size_bytes"]
            }
    
    async def get_certificate(
        self,
        certificate_id: str,
        include_metadata: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a certificate from cache
        
        Args:
            certificate_id: Certificate identifier
            include_metadata: Whether to include cache metadata
            
        Returns:
            Certificate data or None if not found/expired
        """
        # Check if certificate exists in cache
        if certificate_id not in self.certificate_cache:
            self.cache_stats["total_misses"] += 1
            return None
        
        cache_entry = self.certificate_cache[certificate_id]
        
        # Check if entry is expired
        if cache_entry.is_expired():
            # Remove expired entry
            await self._remove_cache_entry(certificate_id)
            self.cache_stats["total_misses"] += 1
            return None
        
        # Check if entry is stale and needs refresh
        if cache_entry.is_stale(self.cache_settings["stale_threshold_seconds"]):
            cache_entry.status = CacheStatus.STALE
            if self.cache_settings["auto_refresh_enabled"]:
                await self._schedule_refresh(certificate_id)
        
        # Record access
        cache_entry.access()
        self.cache_stats["total_hits"] += 1
        
        # Return certificate data
        result = {"certificate_data": cache_entry.certificate_data}
        
        if include_metadata:
            result["cache_metadata"] = cache_entry.to_dict()
        
        return result
    
    async def refresh_certificate(
        self,
        certificate_id: str,
        new_data: Dict[str, Any],
        new_ttl: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Refresh a cached certificate with new data
        
        Args:
            certificate_id: Certificate identifier
            new_data: New certificate data
            new_ttl: New time to live (optional)
            
        Returns:
            Dictionary containing refresh operation result
        """
        if certificate_id not in self.certificate_cache:
            raise ValueError(f"Certificate '{certificate_id}' not found in cache")
        
        cache_entry = self.certificate_cache[certificate_id]
        
        # Refresh the cache entry
        cache_entry.refresh(new_data, new_ttl)
        
        # Update cache index
        await self._update_cache_index(certificate_id, cache_entry)
        
        # Update statistics
        self.cache_stats["total_refreshes"] += 1
        
        logger.info(f"Certificate '{certificate_id}' refreshed")
        
        return {
            "status": "success",
            "certificate_id": certificate_id,
            "refreshed_at": cache_entry.created_at,
            "new_expires_at": cache_entry.created_at + cache_entry.ttl_seconds
        }
    
    async def invalidate_certificate(self, certificate_id: str) -> bool:
        """
        Invalidate a cached certificate
        
        Args:
            certificate_id: Certificate identifier
            
        Returns:
            True if certificate was invalidated, False if not found
        """
        if certificate_id not in self.cache_cache:
            return False
        
        # Remove from cache
        await self._remove_cache_entry(certificate_id)
        
        logger.info(f"Certificate '{certificate_id}' invalidated")
        
        return True
    
    async def invalidate_certificates_by_type(self, certificate_type: str) -> int:
        """
        Invalidate all certificates of a specific type
        
        Args:
            certificate_type: Type of certificates to invalidate
            
        Returns:
            Number of certificates invalidated
        """
        certificate_ids = self.cache_index.get(certificate_type, [])
        invalidated_count = 0
        
        for cert_id in certificate_ids:
            if await self.invalidate_certificate(cert_id):
                invalidated_count += 1
        
        logger.info(f"Invalidated {invalidated_count} certificates of type '{certificate_type}'")
        
        return invalidated_count
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        current_time = time.time()
        
        # Calculate current cache state
        valid_entries = 0
        expired_entries = 0
        stale_entries = 0
        total_size_bytes = 0
        
        for entry in self.certificate_cache.values():
            if entry.is_expired():
                expired_entries += 1
            elif entry.is_stale(self.cache_settings["stale_threshold_seconds"]):
                stale_entries += 1
            else:
                valid_entries += 1
            
            total_size_bytes += entry.metadata["size_bytes"]
        
        # Calculate hit rate
        total_operations = self.cache_stats["total_hits"] + self.cache_stats["total_misses"]
        hit_rate = (self.cache_stats["total_hits"] / total_operations * 100) if total_operations > 0 else 0
        
        # Calculate cache efficiency
        cache_efficiency = (valid_entries / self.cache_stats["total_entries"] * 100) if self.cache_stats["total_entries"] > 0 else 0
        
        return {
            "cache_state": {
                "total_entries": self.cache_stats["total_entries"],
                "valid_entries": valid_entries,
                "expired_entries": expired_entries,
                "stale_entries": stale_entries,
                "total_size_mb": round(total_size_bytes / (1024 * 1024), 2)
            },
            "performance_metrics": {
                "total_hits": self.cache_stats["total_hits"],
                "total_misses": self.cache_stats["total_misses"],
                "hit_rate_percentage": round(hit_rate, 2),
                "cache_efficiency_percentage": round(cache_efficiency, 2)
            },
            "operations": {
                "total_evictions": self.cache_stats["total_evictions"],
                "total_refreshes": self.cache_stats["total_refreshes"]
            },
            "settings": {
                "default_ttl_seconds": self.cache_settings["default_ttl_seconds"],
                "max_cache_size_mb": self.cache_settings["max_cache_size_mb"],
                "max_cache_entries": self.cache_settings["max_cache_entries"],
                "stale_threshold_seconds": self.cache_settings["stale_threshold_seconds"]
            },
            "timestamp": current_time
        }
    
    async def warm_cache(
        self,
        certificates_data: List[Dict[str, Any]],
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        Warm the cache with pre-loaded certificates
        
        Args:
            certificates_data: List of certificate data to pre-load
            priority: Warming priority (low, normal, high)
            
        Returns:
            Dictionary containing warming results
        """
        if not self.cache_settings["cache_warming_enabled"]:
            return {"status": "warming_disabled"}
        
        warming_results = {
            "status": "success",
            "total_certificates": len(certificates_data),
            "successfully_cached": 0,
            "failed_certificates": [],
            "priority": priority,
            "timestamp": time.time()
        }
        
        # Cache each certificate
        for cert_data in certificates_data:
            try:
                certificate_id = cert_data.get("id") or cert_data.get("certificate_id")
                if not certificate_id:
                    continue
                
                await self.cache_certificate(
                    certificate_id=certificate_id,
                    certificate_data=cert_data,
                    ttl_seconds=self.cache_settings["default_ttl_seconds"]
                )
                
                warming_results["successfully_cached"] += 1
                
            except Exception as e:
                warming_results["failed_certificates"].append({
                    "certificate_id": cert_data.get("id", "unknown"),
                    "error": str(e)
                })
        
        logger.info(f"Cache warming completed: {warming_results['successfully_cached']}/{len(certificates_data)} certificates cached")
        
        return warming_results
    
    async def cleanup_expired_entries(self) -> int:
        """Clean up expired cache entries"""
        expired_ids = []
        
        for cert_id, entry in self.cache_cache.items():
            if entry.is_expired():
                expired_ids.append(cert_id)
        
        # Remove expired entries
        for cert_id in expired_ids:
            await self._remove_cache_entry(cert_id)
        
        if expired_ids:
            logger.info(f"Cleaned up {len(expired_ids)} expired cache entries")
        
        return len(expired_ids)
    
    async def start_cache_maintenance(self):
        """Start cache maintenance tasks"""
        async def maintenance_worker():
            while True:
                try:
                    # Clean up expired entries
                    expired_count = await self.cleanup_expired_entries()
                    
                    # Update cache statistics
                    await self._update_cache_statistics()
                    
                    # Wait for next maintenance cycle
                    await asyncio.sleep(self.cleanup_interval_seconds)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in cache maintenance worker: {e}")
        
        # Start maintenance task
        maintenance_task = asyncio.create_task(maintenance_worker())
        self.maintenance_tasks.append(maintenance_task)
        
        logger.info("Cache maintenance started")
    
    async def _check_cache_limits(self) -> None:
        """Check and enforce cache size limits"""
        # Check entry count limit
        if len(self.certificate_cache) >= self.cache_settings["max_cache_entries"]:
            # Remove oldest entries (LRU-like behavior)
            await self._evict_oldest_entries(100)  # Remove 100 oldest entries
        
        # Check size limit (simplified calculation)
        total_size_mb = sum(entry.metadata["size_bytes"] for entry in self.certificate_cache.values()) / (1024 * 1024)
        if total_size_mb >= self.cache_settings["max_cache_size_mb"]:
            # Remove largest entries
            await self._evict_largest_entries(50)  # Remove 50 largest entries
    
    async def _evict_oldest_entries(self, count: int) -> None:
        """Evict oldest cache entries"""
        # Sort by creation time (oldest first)
        sorted_entries = sorted(
            self.certificate_cache.items(),
            key=lambda x: x[1].created_at
        )
        
        # Remove oldest entries
        for i in range(min(count, len(sorted_entries))):
            cert_id = sorted_entries[i][0]
            await self._remove_cache_entry(cert_id)
    
    async def _evict_largest_entries(self, count: int) -> None:
        """Evict largest cache entries"""
        # Sort by size (largest first)
        sorted_entries = sorted(
            self.cache_cache.items(),
            key=lambda x: x[1].metadata["size_bytes"],
            reverse=True
        )
        
        # Remove largest entries
        for i in range(min(count, len(sorted_entries))):
            cert_id = sorted_entries[i][0]
            await self._remove_cache_entry(cert_id)
    
    async def _remove_cache_entry(self, certificate_id: str) -> None:
        """Remove a cache entry and update statistics"""
        if certificate_id in self.certificate_cache:
            entry = self.certificate_cache[certificate_id]
            
            # Update statistics
            if entry.status == CacheStatus.VALID:
                self.cache_stats["valid_entries"] -= 1
            
            self.cache_stats["total_entries"] -= 1
            self.cache_stats["total_evictions"] += 1
            
            # Remove from cache
            del self.certificate_cache[certificate_id]
            
            # Remove from index
            await self._remove_from_cache_index(certificate_id, entry)
    
    async def _update_cache_index(self, certificate_id: str, cache_entry: CertificateCacheEntry) -> None:
        """Update cache index for a certificate"""
        # Index by type
        cert_type = cache_entry.metadata.get("type", "unknown")
        if cert_type not in self.cache_index:
            self.cache_index[cert_type] = []
        
        if certificate_id not in self.cache_index[cert_type]:
            self.cache_index[cert_type].append(certificate_id)
        
        # Index by status
        status = cache_entry.status.value
        status_key = f"status_{status}"
        if status_key not in self.cache_index:
            self.cache_index[status_key] = []
        
        if certificate_id not in self.cache_index[status_key]:
            self.cache_index[status_key].append(certificate_id)
    
    async def _remove_from_cache_index(self, certificate_id: str, cache_entry: CertificateCacheEntry) -> None:
        """Remove certificate from cache index"""
        # Remove from type index
        cert_type = cache_entry.metadata.get("type", "unknown")
        if cert_type in self.cache_index and certificate_id in self.cache_index[cert_type]:
            self.cache_index[cert_type].remove(certificate_id)
        
        # Remove from status index
        status = cache_entry.status.value
        status_key = f"status_{status}"
        if status_key in self.cache_index and certificate_id in self.cache_index[status_key]:
            self.cache_index[status_key].remove(certificate_id)
    
    async def _schedule_refresh(self, certificate_id: str) -> None:
        """Schedule a certificate refresh"""
        # This would typically add to a refresh queue
        # For now, we'll just log the refresh need
        logger.debug(f"Certificate '{certificate_id}' scheduled for refresh")
    
    async def _update_cache_statistics(self) -> None:
        """Update cache statistics based on current state"""
        # This method would recalculate statistics
        # For now, we'll just ensure consistency
        pass
    
    async def get_cache_entry_info(self, certificate_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a cache entry"""
        if certificate_id not in self.certificate_cache:
            return None
        
        entry = self.certificate_cache[certificate_id]
        return entry.to_dict()
    
    async def search_certificates(
        self,
        search_criteria: Dict[str, Any],
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search certificates in cache based on criteria
        
        Args:
            search_criteria: Search criteria (type, status, etc.)
            limit: Maximum number of results
            
        Returns:
            List of matching certificates
        """
        matching_certificates = []
        
        for cert_id, entry in self.certificate_cache.items():
            if await self._matches_search_criteria(entry, search_criteria):
                matching_certificates.append({
                    "certificate_id": cert_id,
                    "certificate_data": entry.certificate_data,
                    "cache_metadata": entry.to_dict()
                })
                
                if len(matching_certificates) >= limit:
                    break
        
        return matching_certificates
    
    async def _matches_search_criteria(
        self,
        cache_entry: CertificateCacheEntry,
        search_criteria: Dict[str, Any]
    ) -> bool:
        """Check if a cache entry matches search criteria"""
        for key, value in search_criteria.items():
            if key == "type" and cache_entry.metadata.get("type") != value:
                return False
            elif key == "status" and cache_entry.status.value != value:
                return False
            elif key == "version" and cache_entry.metadata.get("version") != value:
                return False
            # Add more search criteria as needed
        
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health status of the certificate cache service"""
        return {
            "status": "healthy",
            "cache_statuses_count": len(self.cache_statuses),
            "total_cache_entries": len(self.certificate_cache),
            "cache_index_size": len(self.cache_index),
            "maintenance_tasks_count": len(self.maintenance_tasks),
            "cache_settings": {
                "default_ttl_seconds": self.cache_settings["default_ttl_seconds"],
                "max_cache_size_mb": self.cache_settings["max_cache_size_mb"],
                "max_cache_entries": self.cache_settings["max_cache_entries"],
                "cache_warming_enabled": self.cache_settings["cache_warming_enabled"]
            },
            "timestamp": time.time()
        }
    
    async def cleanup(self):
        """Cleanup certificate cache resources"""
        # Cancel all maintenance tasks
        for task in self.maintenance_tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Clear maintenance tasks list
        self.maintenance_tasks.clear()
        
        logger.info("Certificate Cache cleanup completed")
