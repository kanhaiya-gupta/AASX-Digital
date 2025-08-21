"""
Cache Metrics
============

Performance monitoring and statistics tracking for cache operations.
"""

import logging
import time
from typing import Any, Dict, List, Optional
from collections import defaultdict, deque
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CacheMetrics:
    """Cache performance metrics and statistics tracking"""
    
    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self._start_time = time.time()
        
        # Basic counters
        self._hits = defaultdict(int)
        self._misses = defaultdict(int)
        self._sets = defaultdict(int)
        self._deletes = defaultdict(int)
        self._errors = defaultdict(int)
        self._warm_operations = 0
        
        # Performance tracking
        self._operation_times = defaultdict(list)
        self._recent_operations = deque(maxlen=history_size)
        
        # Hit rate tracking
        self._hit_rate_history = deque(maxlen=100)
        
        logger.info(f"CacheMetrics initialized with history_size={history_size}")
    
    def record_hit(self, level: str = "L1") -> None:
        """Record a cache hit"""
        self._hits[level] += 1
        self._update_hit_rate()
    
    def record_miss(self, key: str) -> None:
        """Record a cache miss"""
        self._misses["total"] += 1
        self._update_hit_rate()
    
    def record_set(self, key: str) -> None:
        """Record a cache set operation"""
        self._sets["total"] += 1
    
    def record_delete(self, key: str) -> None:
        """Record a cache delete operation"""
        self._deletes["total"] += 1
    
    def record_error(self, operation: str = "unknown") -> None:
        """Record a cache error"""
        self._errors[operation] += 1
    
    def record_warm(self, count: int) -> None:
        """Record cache warming operation"""
        self._warm_operations += count
    
    def record_operation_time(self, operation: str, duration: float) -> None:
        """Record operation duration for performance tracking"""
        if len(self._operation_times[operation]) >= self.history_size:
            self._operation_times[operation].pop(0)
        self._operation_times[operation].append(duration)
    
    def record_operation(self, operation: str, key: str, duration: float, 
                        success: bool = True) -> None:
        """Record a complete operation"""
        timestamp = time.time()
        operation_record = {
            'timestamp': timestamp,
            'operation': operation,
            'key': key,
            'duration': duration,
            'success': success
        }
        
        self._recent_operations.append(operation_record)
        self.record_operation_time(operation, duration)
        
        if not success:
            self.record_error(operation)
    
    def _update_hit_rate(self) -> None:
        """Update hit rate history"""
        total_requests = self.get_total_requests()
        if total_requests > 0:
            hit_rate = self.get_hit_rate()
            self._hit_rate_history.append({
                'timestamp': time.time(),
                'hit_rate': hit_rate,
                'total_requests': total_requests
            })
    
    def get_hit_rate(self, level: str = "total") -> float:
        """Get current hit rate for specified level"""
        if level == "total":
            total_hits = sum(self._hits.values())
            total_requests = total_hits + self._misses["total"]
        else:
            total_hits = self._hits[level]
            total_requests = total_hits + self._misses.get(level, 0)
        
        if total_requests == 0:
            return 0.0
        
        return total_hits / total_requests
    
    def get_hit_rate_by_level(self) -> Dict[str, float]:
        """Get hit rates for all cache levels"""
        hit_rates = {}
        for level in self._hits.keys():
            hit_rates[level] = self.get_hit_rate(level)
        return hit_rates
    
    def get_total_requests(self) -> int:
        """Get total number of requests"""
        total_hits = sum(self._hits.values())
        total_misses = self._misses["total"]
        return total_hits + total_misses
    
    def get_operation_count(self, operation: str) -> int:
        """Get count for specific operation"""
        if operation == "hits":
            return sum(self._hits.values())
        elif operation == "misses":
            return sum(self._misses.values())
        elif operation == "sets":
            return sum(self._sets.values())
        elif operation == "deletes":
            return sum(self._deletes.values())
        elif operation == "errors":
            return sum(self._errors.values())
        else:
            return 0
    
    def get_average_operation_time(self, operation: str) -> float:
        """Get average time for specific operation"""
        times = self._operation_times.get(operation, [])
        if not times:
            return 0.0
        return sum(times) / len(times)
    
    def get_percentile_operation_time(self, operation: str, percentile: float) -> float:
        """Get percentile time for specific operation"""
        times = self._operation_times.get(operation, [])
        if not times:
            return 0.0
        
        sorted_times = sorted(times)
        index = int(len(sorted_times) * percentile)
        return sorted_times[index]
    
    def get_recent_operations(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent operations"""
        return list(self._recent_operations)[-count:]
    
    def get_hit_rate_trend(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """Get hit rate trend over specified time period"""
        cutoff_time = time.time() - (minutes * 60)
        trend = []
        
        for record in self._hit_rate_history:
            if record['timestamp'] >= cutoff_time:
                trend.append(record)
        
        return trend
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        total_requests = self.get_total_requests()
        uptime = time.time() - self._start_time
        
        summary = {
            'uptime_seconds': uptime,
            'uptime_human': str(timedelta(seconds=int(uptime))),
            'total_requests': total_requests,
            'requests_per_second': total_requests / uptime if uptime > 0 else 0,
            'hit_rate': self.get_hit_rate(),
            'hit_rate_by_level': self.get_hit_rate_by_level(),
            'operation_counts': {
                'hits': self.get_operation_count('hits'),
                'misses': self.get_operation_count('misses'),
                'sets': self.get_operation_count('sets'),
                'deletes': self.get_operation_count('deletes'),
                'errors': self.get_operation_count('errors'),
                'warm_operations': self._warm_operations
            },
            'performance': {}
        }
        
        # Add performance metrics for each operation type
        for operation in ['get', 'set', 'delete', 'clear']:
            avg_time = self.get_average_operation_time(operation)
            p95_time = self.get_percentile_operation_time(operation, 0.95)
            p99_time = self.get_percentile_operation_time(operation, 0.99)
            
            summary['performance'][operation] = {
                'average_time_ms': avg_time * 1000,
                'p95_time_ms': p95_time * 1000,
                'p99_time_ms': p99_time * 1000
            }
        
        return summary
    
    def get_stats(self) -> Dict[str, Any]:
        """Get basic statistics"""
        return {
            'hits': dict(self._hits),
            'misses': dict(self._misses),
            'sets': dict(self._sets),
            'deletes': dict(self._deletes),
            'errors': dict(self._errors),
            'warm_operations': self._warm_operations,
            'hit_rate': self.get_hit_rate(),
            'total_requests': self.get_total_requests()
        }
    
    def reset(self) -> None:
        """Reset all metrics"""
        self._hits.clear()
        self._misses.clear()
        self._sets.clear()
        self._deletes.clear()
        self._errors.clear()
        self._warm_operations = 0
        self._operation_times.clear()
        self._recent_operations.clear()
        self._hit_rate_history.clear()
        self._start_time = time.time()
        
        logger.info("CacheMetrics reset")


class CacheStats:
    """Simplified cache statistics for quick access"""
    
    def __init__(self, metrics: CacheMetrics):
        self.metrics = metrics
        self._last_update = 0
        self._cached_stats = {}
        self._cache_ttl = 5  # Cache stats for 5 seconds
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cached statistics with TTL"""
        current_time = time.time()
        
        if current_time - self._last_update > self._cache_ttl:
            self._cached_stats = self.metrics.get_stats()
            self._last_update = current_time
        
        return self._cached_stats
    
    def get_hit_rate(self) -> float:
        """Get current hit rate"""
        stats = self.get_stats()
        return stats.get('hit_rate', 0.0)
    
    def get_total_requests(self) -> int:
        """Get total requests"""
        stats = self.get_stats()
        return stats.get('total_requests', 0)
    
    def get_operation_count(self, operation: str) -> int:
        """Get operation count"""
        stats = self.get_stats()
        if operation == 'hits':
            return sum(stats.get('hits', {}).values())
        elif operation == 'misses':
            return sum(stats.get('misses', {}).values())
        elif operation == 'sets':
            return sum(stats.get('sets', {}).values())
        elif operation == 'deletes':
            return sum(stats.get('deletes', {}).values())
        elif operation == 'errors':
            return sum(stats.get('errors', {}).values())
        return 0
