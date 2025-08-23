"""
Module Summary Cache for Certificate Manager

Handles caching of module summary data for improved performance,
including summary storage, retrieval, and lifecycle management.
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


class SummaryStatus(Enum):
    """Summary cache entry status values"""
    ACTIVE = "active"
    EXPIRED = "expired"
    STALE = "stale"
    REFRESHING = "refreshing"
    ARCHIVED = "archived"
    ERROR = "error"


class SummaryCacheEntry:
    """Module summary cache entry with metadata and lifecycle management"""
    
    def __init__(
        self,
        summary_id: str,
        module_id: str,
        summary_data: Dict[str, Any],
        ttl_seconds: int = 7200,  # 2 hours default for summaries
        created_at: Optional[float] = None
    ):
        """Initialize a module summary cache entry"""
        self.summary_id = summary_id
        self.module_id = module_id
        self.summary_data = summary_data
        self.ttl_seconds = ttl_seconds
        self.created_at = created_at or time.time()
        self.last_accessed = self.created_at
        self.access_count = 0
        self.status = SummaryStatus.ACTIVE
        self.metadata = {
            "size_bytes": len(json.dumps(summary_data)),
            "hash": hashlib.sha256(json.dumps(summary_data, sort_keys=True).encode()).hexdigest(),
            "module_type": summary_data.get("module_type", "unknown"),
            "summary_version": summary_data.get("version", "1.0"),
            "completeness_score": summary_data.get("completeness_score", 0.0),
            "quality_score": summary_data.get("quality_score", 0.0)
        }
    
    def is_expired(self) -> bool:
        """Check if the cache entry has expired"""
        return time.time() > (self.created_at + self.ttl_seconds)
    
    def is_stale(self, stale_threshold_seconds: int = 600) -> bool:
        """Check if the cache entry is stale (approaching expiration)"""
        return time.time() > (self.created_at + self.ttl_seconds - stale_threshold_seconds)
    
    def access(self) -> None:
        """Record an access to this cache entry"""
        self.last_accessed = time.time()
        self.access_count += 1
    
    def refresh(self, new_data: Dict[str, Any], new_ttl: Optional[int] = None) -> None:
        """Refresh the cache entry with new data"""
        self.summary_data = new_data
        self.created_at = time.time()
        self.last_accessed = time.time()
        self.access_count = 0
        self.status = SummaryStatus.ACTIVE
        
        if new_ttl is not None:
            self.ttl_seconds = new_ttl
        
        # Update metadata
        self.metadata["size_bytes"] = len(json.dumps(new_data))
        self.metadata["hash"] = hashlib.sha256(json.dumps(new_data, sort_keys=True).encode()).hexdigest()
        self.metadata["module_type"] = new_data.get("module_type", "unknown")
        self.metadata["summary_version"] = new_data.get("version", "1.0")
        self.metadata["completeness_score"] = new_data.get("completeness_score", 0.0)
        self.metadata["quality_score"] = new_data.get("quality_score", 0.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert cache entry to dictionary"""
        return {
            "summary_id": self.summary_id,
            "module_id": self.module_id,
            "summary_data": self.summary_data,
            "ttl_seconds": self.ttl_seconds,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count,
            "status": self.status.value,
            "metadata": self.metadata,
            "is_expired": self.is_expired(),
            "is_stale": self.is_stale()
        }


class ModuleSummaryCache:
    """
    Module summary caching service
    
    Handles:
    - Module summary data storage and retrieval
    - Summary cache lifecycle management
    - Summary cache invalidation and refresh
    - Summary cache statistics and monitoring
    - Summary cache warming and optimization
    """
    
    def __init__(self):
        """Initialize the module summary cache service"""
        self.summary_statuses = list(SummaryStatus)
        
        # Summary cache storage
        self.summary_cache: Dict[str, SummaryCacheEntry] = {}
        self.module_index: Dict[str, List[str]] = {}  # Index by module ID
        self.type_index: Dict[str, List[str]] = {}    # Index by module type
        self.status_index: Dict[str, List[str]] = {}  # Index by status
        
        # Cache management locks
        self.cache_locks: Dict[str, asyncio.Lock] = {}
        self.global_lock = asyncio.Lock()
        
        # Cache settings
        self.cache_settings = self._initialize_cache_settings()
        
        # Cache statistics
        self.cache_stats = {
            "total_entries": 0,
            "active_entries": 0,
            "expired_entries": 0,
            "total_hits": 0,
            "total_misses": 0,
            "total_evictions": 0,
            "total_refreshes": 0,
            "total_aggregations": 0
        }
        
        # Cache maintenance
        self.maintenance_tasks: List[asyncio.Task] = []
        self.cleanup_interval_seconds = 600  # 10 minutes for summaries
        
        logger.info("Module Summary Cache service initialized successfully")
    
    def _initialize_cache_settings(self) -> Dict[str, Any]:
        """Initialize cache settings"""
        return {
            "default_ttl_seconds": 7200,    # 2 hours
            "max_cache_size_mb": 256,        # 256 MB
            "max_cache_entries": 5000,       # 5,000 entries
            "stale_threshold_seconds": 600,  # 10 minutes
            "cleanup_interval_seconds": 600, # 10 minutes
            "cache_warming_enabled": True,
            "auto_refresh_enabled": True,
            "aggregation_enabled": True,
            "compression_enabled": False
        }
    
    async def cache_module_summary(
        self,
        summary_id: str,
        module_id: str,
        summary_data: Dict[str, Any],
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Cache a module summary
        
        Args:
            summary_id: Unique summary identifier
            module_id: Module identifier
            summary_data: Summary data to cache
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
            cache_entry = SummaryCacheEntry(
                summary_id=summary_id,
                module_id=module_id,
                summary_data=summary_data,
                ttl_seconds=ttl_seconds
            )
            
            # Add metadata if provided
            if metadata:
                cache_entry.metadata.update(metadata)
            
            # Store in cache
            self.summary_cache[summary_id] = cache_entry
            
            # Update cache indices
            await self._update_cache_indices(summary_id, cache_entry)
            
            # Update statistics
            self.cache_stats["total_entries"] += 1
            self.cache_stats["active_entries"] += 1
            
            logger.info(f"Module summary '{summary_id}' for module '{module_id}' cached with TTL {ttl_seconds}s")
            
            return {
                "status": "success",
                "summary_id": summary_id,
                "module_id": module_id,
                "cached_at": cache_entry.created_at,
                "expires_at": cache_entry.created_at + cache_entry.ttl_seconds,
                "size_bytes": cache_entry.metadata["size_bytes"]
            }
    
    async def get_module_summary(
        self,
        summary_id: str,
        include_metadata: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a module summary from cache
        
        Args:
            summary_id: Summary identifier
            include_metadata: Whether to include cache metadata
            
        Returns:
            Summary data or None if not found/expired
        """
        # Check if summary exists in cache
        if summary_id not in self.summary_cache:
            self.cache_stats["total_misses"] += 1
            return None
        
        cache_entry = self.summary_cache[summary_id]
        
        # Check if entry is expired
        if cache_entry.is_expired():
            # Remove expired entry
            await self._remove_cache_entry(summary_id)
            self.cache_stats["total_misses"] += 1
            return None
        
        # Check if entry is stale and needs refresh
        if cache_entry.is_stale(self.cache_settings["stale_threshold_seconds"]):
            cache_entry.status = SummaryStatus.STALE
            if self.cache_settings["auto_refresh_enabled"]:
                await self._schedule_refresh(summary_id)
        
        # Record access
        cache_entry.access()
        self.cache_stats["total_hits"] += 1
        
        # Return summary data
        result = {"summary_data": cache_entry.summary_data}
        
        if include_metadata:
            result["cache_metadata"] = cache_entry.to_dict()
        
        return result
    
    async def get_summaries_by_module(
        self,
        module_id: str,
        include_metadata: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get all summaries for a specific module
        
        Args:
            module_id: Module identifier
            include_metadata: Whether to include cache metadata
            
        Returns:
            List of module summaries
        """
        module_summaries = []
        
        if module_id in self.module_index:
            for summary_id in self.module_index[module_id]:
                summary_data = await self.get_module_summary(summary_id, include_metadata)
                if summary_data:
                    module_summaries.append(summary_data)
        
        return module_summaries
    
    async def get_summaries_by_type(
        self,
        module_type: str,
        include_metadata: bool = False,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get summaries by module type
        
        Args:
            module_type: Type of modules
            include_metadata: Whether to include cache metadata
            limit: Maximum number of results
            
        Returns:
            List of summaries for the specified module type
        """
        type_summaries = []
        
        if module_type in self.type_index:
            for summary_id in self.type_index[module_type][:limit]:
                summary_data = await self.get_module_summary(summary_id, include_metadata)
                if summary_data:
                    type_summaries.append(summary_data)
        
        return type_summaries
    
    async def aggregate_module_summaries(
        self,
        module_ids: List[str],
        aggregation_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Aggregate multiple module summaries
        
        Args:
            module_ids: List of module identifiers
            aggregation_type: Type of aggregation to perform
            
        Returns:
            Dictionary containing aggregated summary data
        """
        if not self.cache_settings["aggregation_enabled"]:
            return {"status": "aggregation_disabled"}
        
        # Collect summaries for all modules
        all_summaries = []
        for module_id in module_ids:
            module_summaries = await self.get_summaries_by_module(module_id)
            all_summaries.extend(module_summaries)
        
        if not all_summaries:
            return {"status": "no_summaries_found"}
        
        # Perform aggregation based on type
        if aggregation_type == "comprehensive":
            aggregated_data = await self._perform_comprehensive_aggregation(all_summaries)
        elif aggregation_type == "performance":
            aggregated_data = await self._perform_performance_aggregation(all_summaries)
        elif aggregation_type == "quality":
            aggregated_data = await self._perform_quality_aggregation(all_summaries)
        else:
            aggregated_data = await self._perform_basic_aggregation(all_summaries)
        
        # Update statistics
        self.cache_stats["total_aggregations"] += 1
        
        logger.info(f"Aggregated {len(all_summaries)} summaries for {len(module_ids)} modules")
        
        return {
            "status": "success",
            "aggregation_type": aggregation_type,
            "modules_count": len(module_ids),
            "summaries_count": len(all_summaries),
            "aggregated_data": aggregated_data,
            "timestamp": time.time()
        }
    
    async def refresh_module_summary(
        self,
        summary_id: str,
        new_data: Dict[str, Any],
        new_ttl: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Refresh a cached module summary with new data
        
        Args:
            summary_id: Summary identifier
            new_data: New summary data
            new_ttl: New time to live (optional)
            
        Returns:
            Dictionary containing refresh operation result
        """
        if summary_id not in self.summary_cache:
            raise ValueError(f"Summary '{summary_id}' not found in cache")
        
        cache_entry = self.summary_cache[summary_id]
        
        # Refresh the cache entry
        cache_entry.refresh(new_data, new_ttl)
        
        # Update cache indices
        await self._update_cache_indices(summary_id, cache_entry)
        
        # Update statistics
        self.cache_stats["total_refreshes"] += 1
        
        logger.info(f"Module summary '{summary_id}' refreshed")
        
        return {
            "status": "success",
            "summary_id": summary_id,
            "module_id": cache_entry.module_id,
            "refreshed_at": cache_entry.created_at,
            "new_expires_at": cache_entry.created_at + cache_entry.ttl_seconds
        }
    
    async def invalidate_module_summary(self, summary_id: str) -> bool:
        """
        Invalidate a cached module summary
        
        Args:
            summary_id: Summary identifier
            
        Returns:
            True if summary was invalidated, False if not found
        """
        if summary_id not in self.summary_cache:
            return False
        
        # Remove from cache
        await self._remove_cache_entry(summary_id)
        
        logger.info(f"Module summary '{summary_id}' invalidated")
        
        return True
    
    async def invalidate_module_summaries(
        self,
        module_id: str
    ) -> int:
        """
        Invalidate all summaries for a specific module
        
        Args:
            module_id: Module identifier
            
        Returns:
            Number of summaries invalidated
        """
        if module_id not in self.module_index:
            return 0
        
        summary_ids = self.module_index[module_id].copy()
        invalidated_count = 0
        
        for summary_id in summary_ids:
            if await self.invalidate_module_summary(summary_id):
                invalidated_count += 1
        
        logger.info(f"Invalidated {invalidated_count} summaries for module '{module_id}'")
        
        return invalidated_count
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        current_time = time.time()
        
        # Calculate current cache state
        active_entries = 0
        expired_entries = 0
        stale_entries = 0
        total_size_bytes = 0
        
        for entry in self.summary_cache.values():
            if entry.is_expired():
                expired_entries += 1
            elif entry.is_stale(self.cache_settings["stale_threshold_seconds"]):
                stale_entries += 1
            else:
                active_entries += 1
            
            total_size_bytes += entry.metadata["size_bytes"]
        
        # Calculate hit rate
        total_operations = self.cache_stats["total_hits"] + self.cache_stats["total_misses"]
        hit_rate = (self.cache_stats["total_hits"] / total_operations * 100) if total_operations > 0 else 0
        
        # Calculate cache efficiency
        cache_efficiency = (active_entries / self.cache_stats["total_entries"] * 100) if self.cache_stats["total_entries"] > 0 else 0
        
        # Calculate aggregation statistics
        aggregation_rate = (self.cache_stats["total_aggregations"] / self.cache_stats["total_entries"] * 100) if self.cache_stats["total_entries"] > 0 else 0
        
        return {
            "cache_state": {
                "total_entries": self.cache_stats["total_entries"],
                "active_entries": active_entries,
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
                "total_refreshes": self.cache_stats["total_refreshes"],
                "total_aggregations": self.cache_stats["total_aggregations"],
                "aggregation_rate_percentage": round(aggregation_rate, 2)
            },
            "indexing": {
                "modules_indexed": len(self.module_index),
                "types_indexed": len(self.type_index),
                "statuses_indexed": len(self.status_index)
            },
            "settings": {
                "default_ttl_seconds": self.cache_settings["default_ttl_seconds"],
                "max_cache_size_mb": self.cache_settings["max_cache_size_mb"],
                "max_cache_entries": self.cache_settings["max_cache_entries"],
                "aggregation_enabled": self.cache_settings["aggregation_enabled"]
            },
            "timestamp": current_time
        }
    
    async def warm_cache(
        self,
        summaries_data: List[Dict[str, Any]],
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        Warm the cache with pre-loaded module summaries
        
        Args:
            summaries_data: List of summary data to pre-load
            priority: Warming priority (low, normal, high)
            
        Returns:
            Dictionary containing warming results
        """
        if not self.cache_settings["cache_warming_enabled"]:
            return {"status": "warming_disabled"}
        
        warming_results = {
            "status": "success",
            "total_summaries": len(summaries_data),
            "successfully_cached": 0,
            "failed_summaries": [],
            "priority": priority,
            "timestamp": time.time()
        }
        
        # Cache each summary
        for summary_data in summaries_data:
            try:
                summary_id = summary_data.get("id") or summary_data.get("summary_id")
                module_id = summary_data.get("module_id")
                
                if not summary_id or not module_id:
                    continue
                
                await self.cache_module_summary(
                    summary_id=summary_id,
                    module_id=module_id,
                    summary_data=summary_data,
                    ttl_seconds=self.cache_settings["default_ttl_seconds"]
                )
                
                warming_results["successfully_cached"] += 1
                
            except Exception as e:
                warming_results["failed_summaries"].append({
                    "summary_id": summary_data.get("id", "unknown"),
                    "module_id": summary_data.get("module_id", "unknown"),
                    "error": str(e)
                })
        
        logger.info(f"Cache warming completed: {warming_results['successfully_cached']}/{len(summaries_data)} summaries cached")
        
        return warming_results
    
    async def cleanup_expired_entries(self) -> int:
        """Clean up expired cache entries"""
        expired_ids = []
        
        for summary_id, entry in self.summary_cache.items():
            if entry.is_expired():
                expired_ids.append(summary_id)
        
        # Remove expired entries
        for summary_id in expired_ids:
            await self._remove_cache_entry(summary_id)
        
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
        
        logger.info("Module Summary Cache maintenance started")
    
    async def _check_cache_limits(self) -> None:
        """Check and enforce cache size limits"""
        # Check entry count limit
        if len(self.summary_cache) >= self.cache_settings["max_cache_entries"]:
            # Remove oldest entries (LRU-like behavior)
            await self._evict_oldest_entries(50)  # Remove 50 oldest entries
        
        # Check size limit (simplified calculation)
        total_size_mb = sum(entry.metadata["size_bytes"] for entry in self.summary_cache.values()) / (1024 * 1024)
        if total_size_mb >= self.cache_settings["max_cache_size_mb"]:
            # Remove largest entries
            await self._evict_largest_entries(25)  # Remove 25 largest entries
    
    async def _evict_oldest_entries(self, count: int) -> None:
        """Evict oldest cache entries"""
        # Sort by creation time (oldest first)
        sorted_entries = sorted(
            self.summary_cache.items(),
            key=lambda x: x[1].created_at
        )
        
        # Remove oldest entries
        for i in range(min(count, len(sorted_entries))):
            summary_id = sorted_entries[i][0]
            await self._remove_cache_entry(summary_id)
    
    async def _evict_largest_entries(self, count: int) -> None:
        """Evict largest cache entries"""
        # Sort by size (largest first)
        sorted_entries = sorted(
            self.summary_cache.items(),
            key=lambda x: x[1].metadata["size_bytes"],
            reverse=True
        )
        
        # Remove largest entries
        for i in range(min(count, len(sorted_entries))):
            summary_id = sorted_entries[i][0]
            await self._remove_cache_entry(summary_id)
    
    async def _remove_cache_entry(self, summary_id: str) -> None:
        """Remove a cache entry and update statistics"""
        if summary_id in self.summary_cache:
            entry = self.summary_cache[summary_id]
            
            # Update statistics
            if entry.status == SummaryStatus.ACTIVE:
                self.cache_stats["active_entries"] -= 1
            
            self.cache_stats["total_entries"] -= 1
            self.cache_stats["total_evictions"] += 1
            
            # Remove from cache
            del self.summary_cache[summary_id]
            
            # Remove from indices
            await self._remove_from_cache_indices(summary_id, entry)
    
    async def _update_cache_indices(self, summary_id: str, cache_entry: SummaryCacheEntry) -> None:
        """Update cache indices for a summary"""
        # Index by module ID
        module_id = cache_entry.module_id
        if module_id not in self.module_index:
            self.module_index[module_id] = []
        
        if summary_id not in self.module_index[module_id]:
            self.module_index[module_id].append(summary_id)
        
        # Index by module type
        module_type = cache_entry.metadata.get("module_type", "unknown")
        if module_type not in self.type_index:
            self.type_index[module_type] = []
        
        if summary_id not in self.type_index[module_type]:
            self.type_index[module_type].append(summary_id)
        
        # Index by status
        status = cache_entry.status.value
        if status not in self.status_index:
            self.status_index[status] = []
        
        if summary_id not in self.status_index[status]:
            self.status_index[status].append(summary_id)
    
    async def _remove_from_cache_indices(self, summary_id: str, cache_entry: SummaryCacheEntry) -> None:
        """Remove summary from cache indices"""
        # Remove from module index
        module_id = cache_entry.module_id
        if module_id in self.module_index and summary_id in self.module_index[module_id]:
            self.module_index[module_id].remove(summary_id)
        
        # Remove from type index
        module_type = cache_entry.metadata.get("module_type", "unknown")
        if module_type in self.type_index and summary_id in self.type_index[module_type]:
            self.type_index[module_type].remove(summary_id)
        
        # Remove from status index
        status = cache_entry.status.value
        if status in self.status_index and summary_id in self.status_index[status]:
            self.status_index[status].remove(summary_id)
    
    async def _schedule_refresh(self, summary_id: str) -> None:
        """Schedule a summary refresh"""
        # This would typically add to a refresh queue
        # For now, we'll just log the refresh need
        logger.debug(f"Module summary '{summary_id}' scheduled for refresh")
    
    async def _update_cache_statistics(self) -> None:
        """Update cache statistics based on current state"""
        # This method would recalculate statistics
        # For now, we'll just ensure consistency
        pass
    
    async def _perform_comprehensive_aggregation(self, summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform comprehensive aggregation of summaries"""
        if not summaries:
            return {}
        
        # Extract key metrics
        completeness_scores = []
        quality_scores = []
        module_types = set()
        total_size = 0
        
        for summary in summaries:
            summary_data = summary.get("summary_data", {})
            completeness_scores.append(summary_data.get("completeness_score", 0.0))
            quality_scores.append(summary_data.get("quality_score", 0.0))
            module_types.add(summary_data.get("module_type", "unknown"))
            total_size += len(json.dumps(summary_data))
        
        # Calculate aggregated metrics
        avg_completeness = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0.0
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        return {
            "summary_count": len(summaries),
            "average_completeness_score": round(avg_completeness, 3),
            "average_quality_score": round(avg_quality, 3),
            "module_types": list(module_types),
            "total_size_bytes": total_size,
            "aggregation_timestamp": time.time()
        }
    
    async def _perform_performance_aggregation(self, summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform performance-focused aggregation"""
        if not summaries:
            return {}
        
        # Extract performance metrics
        performance_metrics = []
        
        for summary in summaries:
            summary_data = summary.get("summary_data", {})
            if "performance_metrics" in summary_data:
                performance_metrics.append(summary_data["performance_metrics"])
        
        if not performance_metrics:
            return {"status": "no_performance_data"}
        
        # Aggregate performance data
        return {
            "performance_summaries_count": len(performance_metrics),
            "aggregated_performance": performance_metrics,
            "aggregation_timestamp": time.time()
        }
    
    async def _perform_quality_aggregation(self, summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform quality-focused aggregation"""
        if not summaries:
            return {}
        
        # Extract quality metrics
        quality_scores = []
        completeness_scores = []
        
        for summary in summaries:
            summary_data = summary.get("summary_data", {})
            quality_scores.append(summary_data.get("quality_score", 0.0))
            completeness_scores.append(summary_data.get("completeness_score", 0.0))
        
        if not quality_scores:
            return {"status": "no_quality_data"}
        
        # Calculate quality statistics
        avg_quality = sum(quality_scores) / len(quality_scores)
        avg_completeness = sum(completeness_scores) / len(completeness_scores)
        
        return {
            "quality_summaries_count": len(quality_scores),
            "average_quality_score": round(avg_quality, 3),
            "average_completeness_score": round(avg_completeness, 3),
            "quality_distribution": {
                "excellent": len([q for q in quality_scores if q >= 0.9]),
                "good": len([q for q in quality_scores if 0.7 <= q < 0.9]),
                "fair": len([q for q in quality_scores if 0.5 <= q < 0.7]),
                "poor": len([q for q in quality_scores if q < 0.5])
            },
            "aggregation_timestamp": time.time()
        }
    
    async def _perform_basic_aggregation(self, summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform basic aggregation of summaries"""
        if not summaries:
            return {}
        
        # Basic counting and categorization
        module_types = {}
        total_size = 0
        
        for summary in summaries:
            summary_data = summary.get("summary_data", {})
            module_type = summary_data.get("module_type", "unknown")
            module_types[module_type] = module_types.get(module_type, 0) + 1
            total_size += len(json.dumps(summary_data))
        
        return {
            "summary_count": len(summaries),
            "module_type_distribution": module_types,
            "total_size_bytes": total_size,
            "aggregation_timestamp": time.time()
        }
    
    async def get_cache_entry_info(self, summary_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a cache entry"""
        if summary_id not in self.summary_cache:
            return None
        
        entry = self.summary_cache[summary_id]
        return entry.to_dict()
    
    async def search_summaries(
        self,
        search_criteria: Dict[str, Any],
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search summaries in cache based on criteria
        
        Args:
            search_criteria: Search criteria (module_type, status, etc.)
            limit: Maximum number of results
            
        Returns:
            List of matching summaries
        """
        matching_summaries = []
        
        for summary_id, entry in self.summary_cache.items():
            if await self._matches_search_criteria(entry, search_criteria):
                matching_summaries.append({
                    "summary_id": summary_id,
                    "module_id": entry.module_id,
                    "summary_data": entry.summary_data,
                    "cache_metadata": entry.to_dict()
                })
                
                if len(matching_summaries) >= limit:
                    break
        
        return matching_summaries
    
    async def _matches_search_criteria(
        self,
        cache_entry: SummaryCacheEntry,
        search_criteria: Dict[str, Any]
    ) -> bool:
        """Check if a cache entry matches search criteria"""
        for key, value in search_criteria.items():
            if key == "module_type" and cache_entry.metadata.get("module_type") != value:
                return False
            elif key == "status" and cache_entry.status.value != value:
                return False
            elif key == "module_id" and cache_entry.module_id != value:
                return False
            elif key == "min_quality" and cache_entry.metadata.get("quality_score", 0) < value:
                return False
            elif key == "min_completeness" and cache_entry.metadata.get("completeness_score", 0) < value:
                return False
        
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health status of the module summary cache service"""
        return {
            "status": "healthy",
            "summary_statuses_count": len(self.summary_statuses),
            "total_cache_entries": len(self.summary_cache),
            "module_index_size": len(self.module_index),
            "type_index_size": len(self.type_index),
            "status_index_size": len(self.status_index),
            "maintenance_tasks_count": len(self.maintenance_tasks),
            "cache_settings": {
                "default_ttl_seconds": self.cache_settings["default_ttl_seconds"],
                "max_cache_size_mb": self.cache_settings["max_cache_size_mb"],
                "max_cache_entries": self.cache_settings["max_cache_entries"],
                "aggregation_enabled": self.cache_settings["aggregation_enabled"]
            },
            "timestamp": time.time()
        }
    
    async def cleanup(self):
        """Cleanup module summary cache resources"""
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
        
        logger.info("Module Summary Cache cleanup completed")
