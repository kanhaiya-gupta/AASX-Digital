"""
Cache Manager for Certificate Manager

Main cache management service that coordinates all caching operations,
policies, and strategies across the certificate management system.
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


class CachePolicy(Enum):
    """Cache policy types"""
    LRU = "lru"                 # Least Recently Used
    LFU = "lfu"                 # Least Frequently Used
    FIFO = "fifo"               # First In, First Out
    TTL = "ttl"                 # Time To Live
    ADAPTIVE = "adaptive"       # Adaptive policy
    HYBRID = "hybrid"           # Hybrid policy


class CacheStrategy(Enum):
    """Cache strategy types"""
    WRITE_THROUGH = "write_through"     # Write to cache and storage simultaneously
    WRITE_BEHIND = "write_behind"       # Write to cache first, then storage
    WRITE_AROUND = "write_around"       # Write directly to storage, bypass cache
    READ_THROUGH = "read_through"       # Read from cache, populate if miss
    CACHE_ASIDE = "cache_aside"        # Application manages cache explicitly


class CacheManager:
    """
    Main cache management service
    
    Handles:
    - Cache coordination and management
    - Policy enforcement and strategy selection
    - Cache statistics and monitoring
    - Cache warming and optimization
    - Cross-cache coordination
    """
    
    def __init__(self):
        """Initialize the cache manager service"""
        self.cache_policies = list(CachePolicy)
        self.cache_strategies = list(CacheStrategy)
        
        # Cache registry and coordination
        self.registered_caches: Dict[str, Dict[str, Any]] = {}
        self.cache_coordination: Dict[str, Dict[str, Any]] = {}
        self.global_cache_stats: Dict[str, Any] = {}
        
        # Cache management locks
        self.cache_locks: Dict[str, asyncio.Lock] = {}
        self.global_lock = asyncio.Lock()
        
        # Cache manager settings
        self.cache_settings = self._initialize_cache_settings()
        
        # Cache warming and optimization
        self.cache_warming_queue = asyncio.Queue()
        self.optimization_tasks: List[asyncio.Task] = []
        
        # Performance monitoring
        self.performance_metrics = {
            "total_cache_operations": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "cache_evictions": 0,
            "cache_warming_operations": 0,
            "optimization_operations": 0
        }
        
        logger.info("Cache Manager service initialized successfully")
    
    def _initialize_cache_settings(self) -> Dict[str, Any]:
        """Initialize cache manager settings"""
        return {
            "default_cache_policy": CachePolicy.LRU,
            "default_cache_strategy": CacheStrategy.CACHE_ASIDE,
            "max_cache_size_mb": 1024,  # 1GB default
            "cache_warming_enabled": True,
            "cache_optimization_interval_minutes": 15,
            "cache_coordination_enabled": True,
            "performance_monitoring_enabled": True,
            "cache_health_check_interval_minutes": 5
        }
    
    async def register_cache(
        self,
        cache_name: str,
        cache_type: str,
        cache_policy: CachePolicy = None,
        cache_strategy: CacheStrategy = None,
        max_size_mb: int = None,
        ttl_seconds: int = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Register a new cache with the manager
        
        Args:
            cache_name: Unique cache identifier
            cache_type: Type of cache (e.g., 'certificate', 'summary', 'performance')
            cache_policy: Cache eviction policy
            cache_strategy: Cache strategy
            max_size_mb: Maximum cache size in MB
            ttl_seconds: Time to live in seconds
            metadata: Additional cache metadata
            
        Returns:
            Dictionary containing cache registration information
        """
        async with self.global_lock:
            # Validate input parameters
            await self._validate_cache_registration(cache_name, cache_type)
            
            # Check if cache already registered
            if cache_name in self.registered_caches:
                raise ValueError(f"Cache '{cache_name}' already registered")
            
            # Use default values if none specified
            if cache_policy is None:
                cache_policy = self.cache_settings["default_cache_policy"]
            if cache_strategy is None:
                cache_strategy = self.cache_settings["default_cache_strategy"]
            if max_size_mb is None:
                max_size_mb = self.cache_settings["max_cache_size_mb"]
            
            # Create cache record
            cache_record = {
                "cache_name": cache_name,
                "cache_type": cache_type,
                "cache_policy": cache_policy.value,
                "cache_strategy": cache_strategy.value,
                "max_size_mb": max_size_mb,
                "ttl_seconds": ttl_seconds,
                "current_size_mb": 0,
                "current_items": 0,
                "status": "active",
                "created_at": time.time(),
                "last_accessed": time.time(),
                "metadata": metadata or {}
            }
            
            # Store cache record
            self.registered_caches[cache_name] = cache_record
            
            # Initialize cache coordination
            self.cache_coordination[cache_name] = {
                "cache_name": cache_name,
                "coordination_locks": {},
                "cross_cache_dependencies": [],
                "performance_metrics": {
                    "hits": 0,
                    "misses": 0,
                    "evictions": 0,
                    "operations": 0
                }
            }
            
            # Create cache-specific lock
            self.cache_locks[cache_name] = asyncio.Lock()
            
            logger.info(f"Cache '{cache_name}' registered with {cache_policy.value} policy")
            
            return cache_record
    
    async def unregister_cache(self, cache_name: str) -> bool:
        """Unregister a cache from the manager"""
        async with self.global_lock:
            if cache_name not in self.registered_caches:
                return False
            
            # Remove cache records
            del self.registered_caches[cache_name]
            del self.cache_coordination[cache_name]
            
            # Remove cache lock
            if cache_name in self.cache_locks:
                del self.cache_locks[cache_name]
            
            logger.info(f"Cache '{cache_name}' unregistered")
            return True
    
    async def get_cache_info(self, cache_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a registered cache"""
        return self.registered_caches.get(cache_name)
    
    async def list_registered_caches(self) -> List[Dict[str, Any]]:
        """Get list of all registered caches"""
        return list(self.registered_caches.values())
    
    async def update_cache_policy(
        self,
        cache_name: str,
        new_policy: CachePolicy,
        new_strategy: CacheStrategy = None
    ) -> Dict[str, Any]:
        """
        Update cache policy and strategy
        
        Args:
            cache_name: Cache identifier
            new_policy: New cache policy
            new_strategy: New cache strategy (optional)
            
        Returns:
            Updated cache information
        """
        if cache_name not in self.registered_caches:
            raise ValueError(f"Cache '{cache_name}' not found")
        
        cache_record = self.registered_caches[cache_name]
        
        # Update policy
        old_policy = cache_record["cache_policy"]
        cache_record["cache_policy"] = new_policy.value
        
        # Update strategy if provided
        if new_strategy:
            old_strategy = cache_record["cache_strategy"]
            cache_record["cache_strategy"] = new_strategy.value
            logger.info(f"Cache '{cache_name}' strategy updated from {old_strategy} to {new_strategy.value}")
        
        cache_record["last_updated"] = time.time()
        
        logger.info(f"Cache '{cache_name}' policy updated from {old_policy} to {new_policy.value}")
        
        return cache_record
    
    async def coordinate_cache_operations(
        self,
        operation_type: str,
        cache_names: List[str],
        operation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Coordinate operations across multiple caches
        
        Args:
            operation_type: Type of operation (e.g., 'invalidate', 'warm', 'optimize')
            cache_names: List of cache names to coordinate
            operation_data: Operation-specific data
            
        Returns:
            Dictionary containing coordination results
        """
        if not self.cache_settings["cache_coordination_enabled"]:
            return {"status": "coordination_disabled"}
        
        coordination_results = {
            "operation_type": operation_type,
            "cache_names": cache_names,
            "results": {},
            "timestamp": time.time()
        }
        
        # Execute operation on each cache
        for cache_name in cache_names:
            if cache_name not in self.registered_caches:
                coordination_results["results"][cache_name] = {
                    "status": "error",
                    "error": "Cache not found"
                }
                continue
            
            try:
                result = await self._execute_coordinated_operation(
                    cache_name, operation_type, operation_data
                )
                coordination_results["results"][cache_name] = result
            except Exception as e:
                coordination_results["results"][cache_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        logger.info(f"Coordinated {operation_type} operation across {len(cache_names)} caches")
        
        return coordination_results
    
    async def warm_cache(
        self,
        cache_name: str,
        warm_data: Dict[str, Any],
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        Warm a cache with pre-loaded data
        
        Args:
            cache_name: Cache to warm
            warm_data: Data to pre-load into cache
            priority: Warming priority (low, normal, high)
            
        Returns:
            Dictionary containing warming results
        """
        if not self.cache_settings["cache_warming_enabled"]:
            return {"status": "warming_disabled"}
        
        if cache_name not in self.registered_caches:
            raise ValueError(f"Cache '{cache_name}' not found")
        
        # Add to warming queue
        warming_task = {
            "cache_name": cache_name,
            "warm_data": warm_data,
            "priority": priority,
            "timestamp": time.time()
        }
        
        await self.cache_warming_queue.put(warming_task)
        
        # Update performance metrics
        self.performance_metrics["cache_warming_operations"] += 1
        
        logger.info(f"Cache warming task queued for '{cache_name}' with {priority} priority")
        
        return {
            "status": "queued",
            "cache_name": cache_name,
            "priority": priority,
            "queue_position": self.cache_warming_queue.qsize()
        }
    
    async def optimize_cache(self, cache_name: str) -> Dict[str, Any]:
        """
        Optimize a specific cache
        
        Args:
            cache_name: Cache to optimize
            
        Returns:
            Dictionary containing optimization results
        """
        if cache_name not in self.registered_caches:
            raise ValueError(f"Cache '{cache_name}' not found")
        
        cache_record = self.registered_caches[cache_name]
        
        # Perform cache-specific optimization
        optimization_result = await self._perform_cache_optimization(cache_name, cache_record)
        
        # Update performance metrics
        self.performance_metrics["optimization_operations"] += 1
        
        logger.info(f"Cache '{cache_name}' optimization completed")
        
        return optimization_result
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        total_caches = len(self.registered_caches)
        active_caches = len([c for c in self.registered_caches.values() if c.get("status") == "active"])
        
        # Aggregate statistics across all caches
        total_size_mb = sum(c.get("current_size_mb", 0) for c in self.registered_caches.values())
        total_items = sum(c.get("current_items", 0) for c in self.registered_caches.values())
        
        # Aggregate performance metrics
        total_hits = sum(c.get("performance_metrics", {}).get("hits", 0) for c in self.cache_coordination.values())
        total_misses = sum(c.get("performance_metrics", {}).get("misses", 0) for c in self.cache_coordination.values())
        total_evictions = sum(c.get("performance_metrics", {}).get("evictions", 0) for c in self.cache_coordination.values())
        
        # Calculate hit rate
        total_operations = total_hits + total_misses
        hit_rate = (total_hits / total_operations * 100) if total_operations > 0 else 0
        
        return {
            "total_caches": total_caches,
            "active_caches": active_caches,
            "total_size_mb": total_size_mb,
            "total_items": total_items,
            "performance_metrics": {
                "total_hits": total_hits,
                "total_misses": total_misses,
                "total_evictions": total_evictions,
                "hit_rate_percentage": round(hit_rate, 2),
                "cache_warming_operations": self.performance_metrics["cache_warming_operations"],
                "optimization_operations": self.performance_metrics["optimization_operations"]
            },
            "cache_policies": {
                policy.value: len([c for c in self.registered_caches.values() if c.get("cache_policy") == policy.value])
                for policy in CachePolicy
            },
            "cache_strategies": {
                strategy.value: len([c for c in self.registered_caches.values() if c.get("cache_strategy") == strategy.value])
                for strategy in CacheStrategy
            },
            "timestamp": time.time()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health status of all caches"""
        health_status = {
            "status": "healthy",
            "total_caches": len(self.registered_caches),
            "cache_health": {},
            "coordination_status": "healthy",
            "warming_queue_size": self.cache_warming_queue.qsize(),
            "active_optimization_tasks": len(self.optimization_tasks),
            "timestamp": time.time()
        }
        
        # Check individual cache health
        for cache_name, cache_record in self.registered_caches.items():
            cache_health = await self._check_cache_health(cache_name, cache_record)
            health_status["cache_health"][cache_name] = cache_health
            
            # Update overall status if any cache is unhealthy
            if cache_health["status"] != "healthy":
                health_status["status"] = "degraded"
        
        return health_status
    
    async def _validate_cache_registration(
        self,
        cache_name: str,
        cache_type: str
    ) -> None:
        """Validate cache registration parameters"""
        # Validate cache name
        if not cache_name or len(cache_name) < 3:
            raise ValueError("Cache name must be at least 3 characters long")
        
        if not cache_name.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Cache name must contain only alphanumeric characters, underscores, and hyphens")
        
        # Validate cache type
        valid_types = ["certificate", "summary", "performance", "general", "custom"]
        if cache_type not in valid_types:
            raise ValueError(f"Cache type must be one of: {', '.join(valid_types)}")
    
    async def _execute_coordinated_operation(
        self,
        cache_name: str,
        operation_type: str,
        operation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a coordinated operation on a specific cache"""
        cache_lock = self.cache_locks.get(cache_name)
        if not cache_lock:
            raise ValueError(f"No lock found for cache '{cache_name}'")
        
        async with cache_lock:
            # This would typically delegate to the actual cache implementation
            # For now, we'll simulate the operation
            if operation_type == "invalidate":
                return await self._simulate_cache_invalidation(cache_name, operation_data)
            elif operation_type == "warm":
                return await self._simulate_cache_warming(cache_name, operation_data)
            elif operation_type == "optimize":
                return await self._simulate_cache_optimization(cache_name, operation_data)
            else:
                return {
                    "status": "error",
                    "error": f"Unknown operation type: {operation_type}"
                }
    
    async def _simulate_cache_invalidation(
        self,
        cache_name: str,
        operation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate cache invalidation operation"""
        # Update cache statistics
        if cache_name in self.cache_coordination:
            self.cache_coordination[cache_name]["performance_metrics"]["evictions"] += 1
        
        return {
            "status": "success",
            "operation": "invalidate",
            "cache_name": cache_name,
            "timestamp": time.time()
        }
    
    async def _simulate_cache_warming(
        self,
        cache_name: str,
        operation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate cache warming operation"""
        # Update cache statistics
        if cache_name in self.cache_coordination:
            self.cache_coordination[cache_name]["performance_metrics"]["operations"] += 1
        
        return {
            "status": "success",
            "operation": "warm",
            "cache_name": cache_name,
            "timestamp": time.time()
        }
    
    async def _simulate_cache_optimization(
        self,
        cache_name: str,
        operation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate cache optimization operation"""
        return {
            "status": "success",
            "operation": "optimize",
            "cache_name": cache_name,
            "timestamp": time.time()
        }
    
    async def _perform_cache_optimization(
        self,
        cache_name: str,
        cache_record: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform cache-specific optimization"""
        optimization_result = {
            "cache_name": cache_name,
            "optimization_type": "general",
            "before_size_mb": cache_record.get("current_size_mb", 0),
            "before_items": cache_record.get("current_items", 0),
            "optimizations_applied": [],
            "timestamp": time.time()
        }
        
        # Apply policy-specific optimizations
        policy = cache_record.get("cache_policy")
        if policy == CachePolicy.LRU.value:
            optimization_result["optimizations_applied"].append("LRU optimization applied")
        elif policy == CachePolicy.LFU.value:
            optimization_result["optimizations_applied"].append("LFU optimization applied")
        elif policy == CachePolicy.TTL.value:
            optimization_result["optimizations_applied"].append("TTL cleanup applied")
        
        # Simulate size reduction
        optimization_result["after_size_mb"] = max(0, optimization_result["before_size_mb"] - 10)
        optimization_result["after_items"] = max(0, optimization_result["before_items"] - 5)
        
        # Update cache record
        cache_record["current_size_mb"] = optimization_result["after_size_mb"]
        cache_record["current_items"] = optimization_result["after_items"]
        cache_record["last_updated"] = time.time()
        
        return optimization_result
    
    async def _check_cache_health(
        self,
        cache_name: str,
        cache_record: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check health of a specific cache"""
        current_time = time.time()
        last_accessed = cache_record.get("last_accessed", 0)
        
        # Check if cache is stale
        max_stale_time = 3600  # 1 hour
        is_stale = (current_time - last_accessed) > max_stale_time
        
        # Check size constraints
        current_size = cache_record.get("current_size_mb", 0)
        max_size = cache_record.get("max_size_mb", 0)
        size_ratio = (current_size / max_size * 100) if max_size > 0 else 0
        
        # Determine health status
        if is_stale and size_ratio > 90:
            status = "critical"
        elif is_stale or size_ratio > 80:
            status = "warning"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "is_stale": is_stale,
            "size_ratio_percentage": round(size_ratio, 2),
            "last_accessed_seconds_ago": round(current_time - last_accessed, 2),
            "current_size_mb": current_size,
            "max_size_mb": max_size
        }
    
    async def start_cache_warming_worker(self):
        """Start the cache warming worker task"""
        async def warming_worker():
            while True:
                try:
                    # Get warming task from queue
                    warming_task = await self.cache_warming_queue.get()
                    
                    # Process warming task
                    await self._process_warming_task(warming_task)
                    
                    # Mark task as done
                    self.cache_warming_queue.task_done()
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in cache warming worker: {e}")
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.1)
        
        # Start the worker task
        worker_task = asyncio.create_task(warming_worker())
        self.optimization_tasks.append(worker_task)
        
        logger.info("Cache warming worker started")
    
    async def _process_warming_task(self, warming_task: Dict[str, Any]):
        """Process a cache warming task"""
        cache_name = warming_task["cache_name"]
        warm_data = warming_task["warm_data"]
        priority = warming_task["priority"]
        
        logger.info(f"Processing warming task for cache '{cache_name}' with {priority} priority")
        
        # Simulate warming operation
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # Update cache statistics
        if cache_name in self.cache_coordination:
            self.cache_coordination[cache_name]["performance_metrics"]["operations"] += 1
        
        logger.info(f"Warming task completed for cache '{cache_name}'")
    
    async def cleanup(self):
        """Cleanup cache manager resources"""
        # Cancel all optimization tasks
        for task in self.optimization_tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Clear optimization tasks list
        self.optimization_tasks.clear()
        
        logger.info("Cache Manager cleanup completed")
