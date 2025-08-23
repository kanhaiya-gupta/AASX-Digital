"""
Certificate Manager Cache Package

This package provides comprehensive caching and performance optimization services including:
- Main cache management and coordination
- Performance optimization caching
- Certificate data caching
- Module summary caching
- Cache eviction policies and strategies
"""

from .cache_manager import CacheManager, CachePolicy, CacheStrategy
from .performance_cache import PerformanceCache, PerformanceMetrics, CacheHitRate
from .certificate_cache import CertificateCache, CertificateCacheEntry, CacheStatus
from .module_summary_cache import ModuleSummaryCache, SummaryCacheEntry, SummaryStatus
from .cache_eviction import CacheEvictionPolicy, EvictionStrategy, EvictionReason

__all__ = [
    # Main cache management
    "CacheManager",
    "CachePolicy", 
    "CacheStrategy",
    
    # Performance optimization
    "PerformanceCache",
    "PerformanceMetrics",
    "CacheHitRate",
    
    # Certificate data caching
    "CertificateCache",
    "CertificateCacheEntry",
    "CacheStatus",
    
    # Module summary caching
    "ModuleSummaryCache",
    "SummaryCacheEntry",
    "SummaryStatus",
    
    # Cache eviction
    "CacheEvictionPolicy",
    "EvictionStrategy",
    "EvictionReason"
]
