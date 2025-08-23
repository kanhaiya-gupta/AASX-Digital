"""
Cache Eviction for Certificate Manager

Handles cache eviction policies and strategies for optimal cache performance,
including eviction algorithms, memory management, and cache optimization.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
import logging
from enum import Enum
from datetime import datetime, timedelta
import json
import heapq

logger = logging.getLogger(__name__)


class EvictionStrategy(Enum):
    """Cache eviction strategy types"""
    LRU = "lru"                 # Least Recently Used
    LFU = "lfu"                 # Least Frequently Used
    FIFO = "fifo"               # First In, First Out
    LIFO = "lifo"               # Last In, First Out
    RANDOM = "random"           # Random eviction
    TTL = "ttl"                 # Time To Live based
    SIZE_BASED = "size_based"   # Size-based eviction
    HYBRID = "hybrid"           # Hybrid strategy


class EvictionReason(Enum):
    """Cache eviction reason types"""
    CAPACITY_LIMIT = "capacity_limit"       # Cache reached capacity limit
    TTL_EXPIRED = "ttl_expired"             # Time to live expired
    MEMORY_PRESSURE = "memory_pressure"     # System memory pressure
    MANUAL_INVALIDATION = "manual_invalidation"  # Manual invalidation
    POLICY_CHANGE = "policy_change"         # Eviction policy changed
    PERFORMANCE_OPTIMIZATION = "performance_optimization"  # Performance optimization
    ERROR_RECOVERY = "error_recovery"       # Error recovery
    MAINTENANCE = "maintenance"             # Scheduled maintenance


class CacheEvictionPolicy:
    """
    Cache eviction policy and strategy management service
    
    Handles:
    - Cache eviction policy enforcement
    - Eviction strategy selection and implementation
    - Memory pressure monitoring and response
    - Cache optimization through intelligent eviction
    - Eviction statistics and analysis
    """
    
    def __init__(self):
        """Initialize the cache eviction policy service"""
        self.eviction_strategies = list(EvictionStrategy)
        self.eviction_reasons = list(EvictionReason)
        
        # Eviction policy configuration
        self.eviction_policies: Dict[str, Dict[str, Any]] = {}
        self.active_policies: Dict[str, str] = {}  # cache_name -> policy_name
        
        # Eviction monitoring and statistics
        self.eviction_stats = {
            "total_evictions": 0,
            "evictions_by_reason": {},
            "evictions_by_strategy": {},
            "evictions_by_cache": {},
            "memory_pressure_events": 0,
            "policy_changes": 0
        }
        
        # Memory pressure monitoring
        self.memory_thresholds = {
            "warning": 0.75,    # 75% memory usage
            "critical": 0.90,   # 90% memory usage
            "emergency": 0.95   # 95% memory usage
        }
        
        # Eviction locks
        self.eviction_locks: Dict[str, asyncio.Lock] = {}
        self.global_lock = asyncio.Lock()
        
        # Eviction queue and workers
        self.eviction_queue = asyncio.Queue()
        self.eviction_workers: List[asyncio.Task] = []
        
        # Initialize default policies
        self._initialize_default_policies()
        
        logger.info("Cache Eviction Policy service initialized successfully")
    
    def _initialize_default_policies(self) -> None:
        """Initialize default eviction policies"""
        self.eviction_policies = {
            "default": {
                "name": "default",
                "strategy": EvictionStrategy.LRU.value,
                "max_entries": 10000,
                "max_size_mb": 1024,
                "ttl_seconds": 3600,
                "eviction_batch_size": 100,
                "memory_pressure_response": "aggressive",
                "description": "Default LRU-based eviction policy"
            },
            "performance_optimized": {
                "name": "performance_optimized",
                "strategy": EvictionStrategy.LFU.value,
                "max_entries": 50000,
                "max_size_mb": 2048,
                "ttl_seconds": 7200,
                "eviction_batch_size": 200,
                "memory_pressure_response": "moderate",
                "description": "Performance-optimized LFU-based policy"
            },
            "memory_efficient": {
                "name": "memory_efficient",
                "strategy": EvictionStrategy.SIZE_BASED.value,
                "max_entries": 5000,
                "max_size_mb": 512,
                "ttl_seconds": 1800,
                "eviction_batch_size": 50,
                "memory_pressure_response": "very_aggressive",
                "description": "Memory-efficient size-based policy"
            },
            "balanced": {
                "name": "balanced",
                "strategy": EvictionStrategy.HYBRID.value,
                "max_entries": 20000,
                "max_size_mb": 1536,
                "ttl_seconds": 5400,
                "eviction_batch_size": 150,
                "memory_pressure_response": "balanced",
                "description": "Balanced hybrid eviction policy"
            }
        }
    
    async def create_eviction_policy(
        self,
        policy_name: str,
        strategy: EvictionStrategy,
        max_entries: int,
        max_size_mb: int,
        ttl_seconds: int = 3600,
        eviction_batch_size: int = 100,
        memory_pressure_response: str = "moderate",
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new eviction policy
        
        Args:
            policy_name: Unique policy name
            strategy: Eviction strategy to use
            max_entries: Maximum number of cache entries
            max_size_mb: Maximum cache size in MB
            ttl_seconds: Default time to live for entries
            eviction_batch_size: Number of entries to evict in each batch
            memory_pressure_response: Response level to memory pressure
            description: Policy description
            metadata: Additional policy metadata
            
        Returns:
            Dictionary containing created policy information
        """
        async with self.global_lock:
            # Validate input parameters
            await self._validate_policy_creation(policy_name, strategy, max_entries, max_size_mb)
            
            # Check if policy already exists
            if policy_name in self.eviction_policies:
                raise ValueError(f"Eviction policy '{policy_name}' already exists")
            
            # Create policy record
            policy_record = {
                "name": policy_name,
                "strategy": strategy.value,
                "max_entries": max_entries,
                "max_size_mb": max_size_mb,
                "ttl_seconds": ttl_seconds,
                "eviction_batch_size": eviction_batch_size,
                "memory_pressure_response": memory_pressure_response,
                "description": description,
                "metadata": metadata or {},
                "created_at": time.time(),
                "last_updated": time.time()
            }
            
            # Store policy
            self.eviction_policies[policy_name] = policy_record
            
            logger.info(f"Eviction policy '{policy_name}' created with {strategy.value} strategy")
            
            return policy_record
    
    async def apply_eviction_policy(
        self,
        cache_name: str,
        policy_name: str
    ) -> Dict[str, Any]:
        """
        Apply an eviction policy to a specific cache
        
        Args:
            cache_name: Name of the cache to apply policy to
            policy_name: Name of the eviction policy to apply
            
        Returns:
            Dictionary containing policy application result
        """
        if policy_name not in self.eviction_policies:
            raise ValueError(f"Eviction policy '{policy_name}' not found")
        
        policy = self.eviction_policies[policy_name]
        
        # Apply policy to cache
        self.active_policies[cache_name] = policy_name
        
        # Create cache-specific eviction lock if needed
        if cache_name not in self.eviction_locks:
            self.eviction_locks[cache_name] = asyncio.Lock()
        
        logger.info(f"Eviction policy '{policy_name}' applied to cache '{cache_name}'")
        
        return {
            "status": "success",
            "cache_name": cache_name,
            "policy_name": policy_name,
            "strategy": policy["strategy"],
            "applied_at": time.time()
        }
    
    async def execute_eviction(
        self,
        cache_name: str,
        eviction_reason: EvictionReason,
        target_count: Optional[int] = None,
        target_size_mb: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Execute eviction on a specific cache
        
        Args:
            cache_name: Name of the cache to evict from
            eviction_reason: Reason for eviction
            target_count: Target number of entries to evict
            target_size_mb: Target size reduction in MB
            
        Returns:
            Dictionary containing eviction results
        """
        if cache_name not in self.active_policies:
            raise ValueError(f"No eviction policy applied to cache '{cache_name}'")
        
        policy_name = self.active_policies[cache_name]
        policy = self.eviction_policies[policy_name]
        
        # Get cache-specific lock
        cache_lock = self.eviction_locks.get(cache_name)
        if not cache_lock:
            raise ValueError(f"No eviction lock found for cache '{cache_name}'")
        
        async with cache_lock:
            # Execute eviction based on strategy
            eviction_result = await self._execute_eviction_strategy(
                cache_name, policy, eviction_reason, target_count, target_size_mb
            )
            
            # Update eviction statistics
            await self._update_eviction_statistics(cache_name, eviction_reason, eviction_result)
            
            logger.info(f"Eviction executed on cache '{cache_name}': {eviction_result['evicted_count']} entries removed")
            
            return eviction_result
    
    async def monitor_memory_pressure(self) -> Dict[str, Any]:
        """
        Monitor system memory pressure and trigger evictions if needed
        
        Returns:
            Dictionary containing memory pressure status and actions taken
        """
        # Simulate memory usage monitoring
        # In a real implementation, this would check actual system memory
        current_memory_usage = await self._get_simulated_memory_usage()
        
        memory_status = {
            "current_usage_percentage": current_memory_usage,
            "thresholds": self.memory_thresholds,
            "status": "normal",
            "actions_taken": [],
            "timestamp": time.time()
        }
        
        # Check memory pressure levels
        if current_memory_usage >= self.memory_thresholds["emergency"]:
            memory_status["status"] = "emergency"
            await self._handle_emergency_memory_pressure()
            memory_status["actions_taken"].append("emergency_eviction_triggered")
            
        elif current_memory_usage >= self.memory_thresholds["critical"]:
            memory_status["status"] = "critical"
            await self._handle_critical_memory_pressure()
            memory_status["actions_taken"].append("critical_eviction_triggered")
            
        elif current_memory_usage >= self.memory_thresholds["warning"]:
            memory_status["status"] = "warning"
            await self._handle_warning_memory_pressure()
            memory_status["actions_taken"].append("warning_eviction_triggered")
        
        # Update statistics
        if memory_status["status"] != "normal":
            self.eviction_stats["memory_pressure_events"] += 1
        
        return memory_status
    
    async def get_eviction_statistics(self) -> Dict[str, Any]:
        """Get comprehensive eviction statistics"""
        return {
            "total_evictions": self.eviction_stats["total_evictions"],
            "evictions_by_reason": self.eviction_stats["evictions_by_reason"],
            "evictions_by_strategy": self.eviction_stats["evictions_by_strategy"],
            "evictions_by_cache": self.eviction_stats["evictions_by_cache"],
            "memory_pressure_events": self.eviction_stats["memory_pressure_events"],
            "policy_changes": self.eviction_stats["policy_changes"],
            "active_policies": self.active_policies,
            "available_policies": list(self.eviction_policies.keys()),
            "timestamp": time.time()
        }
    
    async def start_eviction_workers(self, worker_count: int = 2):
        """Start eviction worker tasks"""
        for i in range(worker_count):
            worker_task = asyncio.create_task(self._eviction_worker(f"worker_{i}"))
            self.eviction_workers.append(worker_task)
        
        logger.info(f"Started {worker_count} eviction workers")
    
    async def _validate_policy_creation(
        self,
        policy_name: str,
        strategy: EvictionStrategy,
        max_entries: int,
        max_size_mb: int
    ) -> None:
        """Validate eviction policy creation parameters"""
        # Validate policy name
        if not policy_name or len(policy_name) < 3:
            raise ValueError("Policy name must be at least 3 characters long")
        
        if not policy_name.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Policy name must contain only alphanumeric characters, underscores, and hyphens")
        
        # Validate strategy
        if strategy not in self.eviction_strategies:
            raise ValueError(f"Invalid eviction strategy: {strategy}")
        
        # Validate limits
        if max_entries <= 0:
            raise ValueError("Max entries must be greater than 0")
        
        if max_size_mb <= 0:
            raise ValueError("Max size must be greater than 0")
    
    async def _execute_eviction_strategy(
        self,
        cache_name: str,
        policy: Dict[str, Any],
        eviction_reason: EvictionReason,
        target_count: Optional[int],
        target_size_mb: Optional[float]
    ) -> Dict[str, Any]:
        """Execute eviction based on the specified strategy"""
        strategy = policy["strategy"]
        
        if strategy == EvictionStrategy.LRU.value:
            return await self._execute_lru_eviction(cache_name, policy, target_count, target_size_mb)
        elif strategy == EvictionStrategy.LFU.value:
            return await self._execute_lfu_eviction(cache_name, policy, target_count, target_size_mb)
        elif strategy == EvictionStrategy.FIFO.value:
            return await self._execute_fifo_eviction(cache_name, policy, target_count, target_size_mb)
        elif strategy == EvictionStrategy.TTL.value:
            return await self._execute_ttl_eviction(cache_name, policy, target_count, target_size_mb)
        elif strategy == EvictionStrategy.SIZE_BASED.value:
            return await self._execute_size_based_eviction(cache_name, policy, target_count, target_size_mb)
        elif strategy == EvictionStrategy.HYBRID.value:
            return await self._execute_hybrid_eviction(cache_name, policy, target_count, target_size_mb)
        else:
            return await self._execute_random_eviction(cache_name, policy, target_count, target_size_mb)
    
    async def _execute_lru_eviction(
        self,
        cache_name: str,
        policy: Dict[str, Any],
        target_count: Optional[int],
        target_size_mb: Optional[float]
    ) -> Dict[str, Any]:
        """Execute LRU (Least Recently Used) eviction"""
        # This would typically interact with the actual cache implementation
        # For now, we'll simulate the eviction process
        
        evicted_count = target_count or policy["eviction_batch_size"]
        evicted_size_mb = target_size_mb or (evicted_count * 0.1)  # Simulate average entry size
        
        await asyncio.sleep(0.01)  # Simulate eviction processing time
        
        return {
            "strategy": "lru",
            "evicted_count": evicted_count,
            "evicted_size_mb": round(evicted_size_mb, 2),
            "eviction_reason": "simulated_lru_eviction",
            "timestamp": time.time()
        }
    
    async def _execute_lfu_eviction(
        self,
        cache_name: str,
        policy: Dict[str, Any],
        target_count: Optional[int],
        target_size_mb: Optional[float]
    ) -> Dict[str, Any]:
        """Execute LFU (Least Frequently Used) eviction"""
        evicted_count = target_count or policy["eviction_batch_size"]
        evicted_size_mb = target_size_mb or (evicted_count * 0.1)
        
        await asyncio.sleep(0.01)  # Simulate eviction processing time
        
        return {
            "strategy": "lfu",
            "evicted_count": evicted_count,
            "evicted_size_mb": round(evicted_size_mb, 2),
            "eviction_reason": "simulated_lfu_eviction",
            "timestamp": time.time()
        }
    
    async def _execute_fifo_eviction(
        self,
        cache_name: str,
        policy: Dict[str, Any],
        target_count: Optional[int],
        target_size_mb: Optional[float]
    ) -> Dict[str, Any]:
        """Execute FIFO (First In, First Out) eviction"""
        evicted_count = target_count or policy["eviction_batch_size"]
        evicted_size_mb = target_size_mb or (evicted_count * 0.1)
        
        await asyncio.sleep(0.01)  # Simulate eviction processing time
        
        return {
            "strategy": "fifo",
            "evicted_count": evicted_count,
            "evicted_size_mb": round(evicted_size_mb, 2),
            "eviction_reason": "simulated_fifo_eviction",
            "timestamp": time.time()
        }
    
    async def _execute_ttl_eviction(
        self,
        cache_name: str,
        policy: Dict[str, Any],
        target_count: Optional[int],
        target_size_mb: Optional[float]
    ) -> Dict[str, Any]:
        """Execute TTL (Time To Live) based eviction"""
        evicted_count = target_count or policy["eviction_batch_size"]
        evicted_size_mb = target_size_mb or (evicted_count * 0.1)
        
        await asyncio.sleep(0.01)  # Simulate eviction processing time
        
        return {
            "strategy": "ttl",
            "evicted_count": evicted_count,
            "evicted_size_mb": round(evicted_size_mb, 2),
            "eviction_reason": "simulated_ttl_eviction",
            "timestamp": time.time()
        }
    
    async def _execute_size_based_eviction(
        self,
        cache_name: str,
        policy: Dict[str, Any],
        target_count: Optional[int],
        target_size_mb: Optional[float]
    ) -> Dict[str, Any]:
        """Execute size-based eviction"""
        evicted_count = target_count or policy["eviction_batch_size"]
        evicted_size_mb = target_size_mb or (evicted_count * 0.1)
        
        await asyncio.sleep(0.01)  # Simulate eviction processing time
        
        return {
            "strategy": "size_based",
            "evicted_count": evicted_count,
            "evicted_size_mb": round(evicted_size_mb, 2),
            "eviction_reason": "simulated_size_based_eviction",
            "timestamp": time.time()
        }
    
    async def _execute_hybrid_eviction(
        self,
        cache_name: str,
        policy: Dict[str, Any],
        target_count: Optional[int],
        target_size_mb: Optional[float]
    ) -> Dict[str, Any]:
        """Execute hybrid eviction strategy"""
        evicted_count = target_count or policy["eviction_batch_size"]
        evicted_size_mb = target_size_mb or (evicted_count * 0.1)
        
        await asyncio.sleep(0.01)  # Simulate eviction processing time
        
        return {
            "strategy": "hybrid",
            "evicted_count": evicted_count,
            "evicted_size_mb": round(evicted_size_mb, 2),
            "eviction_reason": "simulated_hybrid_eviction",
            "timestamp": time.time()
        }
    
    async def _execute_random_eviction(
        self,
        cache_name: str,
        policy: Dict[str, Any],
        target_count: Optional[int],
        target_size_mb: Optional[float]
    ) -> Dict[str, Any]:
        """Execute random eviction strategy"""
        evicted_count = target_count or policy["eviction_batch_size"]
        evicted_size_mb = target_size_mb or (evicted_count * 0.1)
        
        await asyncio.sleep(0.01)  # Simulate eviction processing time
        
        return {
            "strategy": "random",
            "evicted_count": evicted_count,
            "evicted_size_mb": round(evicted_size_mb, 2),
            "eviction_reason": "simulated_random_eviction",
            "timestamp": time.time()
        }
    
    async def _update_eviction_statistics(
        self,
        cache_name: str,
        eviction_reason: EvictionReason,
        eviction_result: Dict[str, Any]
    ) -> None:
        """Update eviction statistics"""
        # Update total evictions
        self.eviction_stats["total_evictions"] += eviction_result["evicted_count"]
        
        # Update evictions by reason
        reason_key = eviction_reason.value
        if reason_key not in self.eviction_stats["evictions_by_reason"]:
            self.eviction_stats["evictions_by_reason"][reason_key] = 0
        self.eviction_stats["evictions_by_reason"][reason_key] += eviction_result["evicted_count"]
        
        # Update evictions by strategy
        strategy_key = eviction_result["strategy"]
        if strategy_key not in self.eviction_stats["evictions_by_strategy"]:
            self.eviction_stats["evictions_by_strategy"][strategy_key] = 0
        self.eviction_stats["evictions_by_strategy"][strategy_key] += eviction_result["evicted_count"]
        
        # Update evictions by cache
        if cache_name not in self.eviction_stats["evictions_by_cache"]:
            self.eviction_stats["evictions_by_cache"][cache_name] = 0
        self.eviction_stats["evictions_by_cache"][cache_name] += eviction_result["evicted_count"]
    
    async def _get_simulated_memory_usage(self) -> float:
        """Get simulated system memory usage"""
        # Simulate memory usage that varies over time
        current_time = time.time()
        base_usage = 0.6  # 60% base usage
        variation = 0.3 * (current_time % 300) / 300  # Varies between 60-90%
        return base_usage + variation
    
    async def _handle_emergency_memory_pressure(self) -> None:
        """Handle emergency memory pressure"""
        logger.warning("Emergency memory pressure detected - triggering aggressive eviction")
        
        # Trigger aggressive eviction on all caches
        for cache_name in self.active_policies:
            await self.execute_eviction(
                cache_name=cache_name,
                eviction_reason=EvictionReason.MEMORY_PRESSURE,
                target_count=1000,  # Large batch
                target_size_mb=100   # Large size reduction
            )
    
    async def _handle_critical_memory_pressure(self) -> None:
        """Handle critical memory pressure"""
        logger.warning("Critical memory pressure detected - triggering moderate eviction")
        
        # Trigger moderate eviction on all caches
        for cache_name in self.active_policies:
            await self.execute_eviction(
                cache_name=cache_name,
                eviction_reason=EvictionReason.MEMORY_PRESSURE,
                target_count=500,   # Medium batch
                target_size_mb=50    # Medium size reduction
            )
    
    async def _handle_warning_memory_pressure(self) -> None:
        """Handle warning memory pressure"""
        logger.info("Warning memory pressure detected - triggering light eviction")
        
        # Trigger light eviction on all caches
        for cache_name in self.active_policies:
            await self.execute_eviction(
                cache_name=cache_name,
                eviction_reason=EvictionReason.MEMORY_PRESSURE,
                target_count=200,   # Small batch
                target_size_mb=20    # Small size reduction
            )
    
    async def _eviction_worker(self, worker_name: str):
        """Eviction worker task"""
        logger.info(f"Eviction worker {worker_name} started")
        
        while True:
            try:
                # Process eviction tasks from queue
                if not self.eviction_queue.empty():
                    eviction_task = await self.eviction_queue.get()
                    await self._process_eviction_task(eviction_task)
                    self.eviction_queue.task_done()
                
                # Wait before next check
                await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in eviction worker {worker_name}: {e}")
        
        logger.info(f"Eviction worker {worker_name} stopped")
    
    async def _process_eviction_task(self, eviction_task: Dict[str, Any]):
        """Process an eviction task"""
        cache_name = eviction_task.get("cache_name")
        eviction_reason = eviction_task.get("eviction_reason")
        
        if cache_name and eviction_reason:
            await self.execute_eviction(
                cache_name=cache_name,
                eviction_reason=eviction_reason
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health status of the cache eviction policy service"""
        return {
            "status": "healthy",
            "eviction_strategies_count": len(self.eviction_strategies),
            "eviction_reasons_count": len(self.eviction_reasons),
            "eviction_policies_count": len(self.eviction_policies),
            "active_policies_count": len(self.active_policies),
            "eviction_workers_count": len(self.eviction_workers),
            "eviction_queue_size": self.eviction_queue.qsize(),
            "memory_thresholds": self.memory_thresholds,
            "timestamp": time.time()
        }
    
    async def cleanup(self):
        """Cleanup cache eviction policy resources"""
        # Cancel all eviction workers
        for worker in self.eviction_workers:
            if not worker.done():
                worker.cancel()
                try:
                    await worker
                except asyncio.CancelledError:
                    pass
        
        # Clear eviction workers list
        self.eviction_workers.clear()
        
        logger.info("Cache Eviction Policy cleanup completed")
