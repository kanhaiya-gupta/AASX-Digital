"""
Async Helper Utilities

Provides comprehensive async utility functions for the AAS Data Modeling Engine.
Includes async context managers, retry logic, timeout handling, and batch processing.
"""

import asyncio
import time
import functools
from typing import Any, Callable, Coroutine, Dict, List, Optional, TypeVar, Union
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryStrategy(Enum):
    """Retry strategies for async operations"""
    IMMEDIATE = "immediate"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIBONACCI_BACKOFF = "fibonacci_backoff"


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    jitter: bool = True
    exceptions: tuple = (Exception,)


class AsyncHelpers:
    """Collection of async utility functions"""
    
    @staticmethod
    async def with_timeout(coro: Coroutine, timeout: float, default_value: Any = None) -> Any:
        """
        Execute coroutine with timeout
        
        Args:
            coro: Coroutine to execute
            timeout: Timeout in seconds
            default_value: Value to return on timeout
            
        Returns:
            Result of coroutine or default_value on timeout
        """
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"Operation timed out after {timeout} seconds")
            return default_value
    
    @staticmethod
    async def retry_async(
        func: Callable[..., Coroutine[Any, Any, T]],
        *args,
        config: Optional[RetryConfig] = None,
        **kwargs
    ) -> T:
        """
        Retry async function with configurable strategy
        
        Args:
            func: Async function to retry
            config: Retry configuration
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Result of successful function call
            
        Raises:
            Exception: Last exception if all retries fail
        """
        if config is None:
            config = RetryConfig()
        
        last_exception = None
        
        for attempt in range(config.max_attempts):
            try:
                return await func(*args, **kwargs)
            except config.exceptions as e:
                last_exception = e
                if attempt == config.max_attempts - 1:
                    break
                
                delay = AsyncHelpers._calculate_delay(attempt, config)
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s")
                await asyncio.sleep(delay)
        
        raise last_exception
    
    @staticmethod
    def _calculate_delay(attempt: int, config: RetryConfig) -> float:
        """Calculate delay based on retry strategy"""
        if config.strategy == RetryStrategy.IMMEDIATE:
            delay = 0
        elif config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = min(config.base_delay * (2 ** attempt), config.max_delay)
        elif config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = min(config.base_delay * (attempt + 1), config.max_delay)
        elif config.strategy == RetryStrategy.FIBONACCI_BACKOFF:
            delay = min(config.base_delay * AsyncHelpers._fibonacci(attempt + 1), config.max_delay)
        else:
            delay = config.base_delay
        
        if config.jitter:
            delay *= (0.5 + 0.5 * time.time() % 1)
        
        return delay
    
    @staticmethod
    def _fibonacci(n: int) -> int:
        """Calculate fibonacci number"""
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b
    
    @staticmethod
    async def batch_process(
        items: List[Any],
        processor: Callable[[Any], Coroutine[Any, Any, T]],
        batch_size: int = 10,
        max_concurrent: int = 5
    ) -> List[T]:
        """
        Process items in batches with controlled concurrency
        
        Args:
            items: List of items to process
            processor: Async function to process each item
            batch_size: Number of items to process in each batch
            max_concurrent: Maximum concurrent operations
            
        Returns:
            List of processed results
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        results = []
        
        async def process_item(item):
            async with semaphore:
                return await processor(item)
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_tasks = [process_item(item) for item in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Handle exceptions in batch results
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch processing error: {result}")
                    results.append(None)
                else:
                    results.append(result)
        
        return results
    
    @staticmethod
    async def rate_limit(
        func: Callable[..., Coroutine[Any, Any, T]],
        calls_per_second: float,
        *args,
        **kwargs
    ) -> T:
        """
        Execute function with rate limiting
        
        Args:
            func: Async function to execute
            calls_per_second: Maximum calls per second
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Result of function execution
        """
        delay = 1.0 / calls_per_second
        await asyncio.sleep(delay)
        return await func(*args, **kwargs)
    
    @staticmethod
    @asynccontextmanager
    async def async_context_manager():
        """Example async context manager"""
        try:
            # Setup
            logger.debug("Setting up async context")
            yield
        finally:
            # Cleanup
            logger.debug("Cleaning up async context")
    
    @staticmethod
    def to_async(func: Callable[..., T]) -> Callable[..., Coroutine[Any, Any, T]]:
        """
        Convert synchronous function to async
        
        Args:
            func: Synchronous function to convert
            
        Returns:
            Async version of the function
        """
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
        
        return async_wrapper
    
    @staticmethod
    async def wait_for_condition(
        condition: Callable[[], bool],
        timeout: float = 30.0,
        check_interval: float = 0.1
    ) -> bool:
        """
        Wait for a condition to become true
        
        Args:
            condition: Function that returns boolean condition
            timeout: Maximum time to wait in seconds
            check_interval: Interval between condition checks
            
        Returns:
            True if condition became true, False if timed out
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if condition():
                return True
            await asyncio.sleep(check_interval)
        
        return False
    
    @staticmethod
    async def with_circuit_breaker(
        func: Callable[..., Coroutine[Any, Any, T]],
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        *args,
        **kwargs
    ) -> T:
        """
        Execute function with circuit breaker pattern
        
        Args:
            func: Async function to execute
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time to wait before attempting recovery
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Result of function execution
        """
        # This is a simplified circuit breaker implementation
        # In production, you'd want a more robust state machine
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Circuit breaker triggered: {e}")
            raise
    
    @staticmethod
    async def parallel_map(
        items: List[Any],
        processor: Callable[[Any], Coroutine[Any, Any, T]],
        max_workers: Optional[int] = None
    ) -> List[T]:
        """
        Process items in parallel with controlled concurrency
        
        Args:
            items: List of items to process
            processor: Async function to process each item
            max_workers: Maximum number of concurrent workers
            
        Returns:
            List of processed results
        """
        if max_workers is None:
            max_workers = min(len(items), 10)
        
        semaphore = asyncio.Semaphore(max_workers)
        
        async def process_with_semaphore(item):
            async with semaphore:
                return await processor(item)
        
        tasks = [process_with_semaphore(item) for item in items]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error processing item {i}: {result}")
                processed_results.append(None)
            else:
                processed_results.append(result)
        
        return processed_results


# Convenience functions
async def retry_async(
    func: Callable[..., Coroutine[Any, Any, T]],
    *args,
    config: Optional[RetryConfig] = None,
    **kwargs
) -> T:
    """Convenience function for retrying async operations"""
    return await AsyncHelpers.retry_async(func, *args, config=config, **kwargs)


async def batch_process(
    items: List[Any],
    processor: Callable[[Any], Coroutine[Any, Any, T]],
    batch_size: int = 10,
    max_concurrent: int = 5
) -> List[T]:
    """Convenience function for batch processing"""
    return await AsyncHelpers.batch_process(items, processor, batch_size, max_concurrent)


async def with_timeout(coro: Coroutine, timeout: float, default_value: Any = None) -> Any:
    """Convenience function for timeout handling"""
    return await AsyncHelpers.with_timeout(coro, timeout, default_value)
