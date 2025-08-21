"""
Common decorators for the engine system.

This module provides useful decorators for common functionality like
retry logic, caching, validation, logging, and performance measurement.
"""

import functools
import time
import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional, Union, Type
from functools import wraps
import inspect

from .exceptions import (
    TimeoutException, 
    RetryException, 
    ValidationException,
    AuthenticationException,
    AuthorizationException
)
from .constants import RetryStrategy, LogLevel

logger = logging.getLogger(__name__)


def retry(max_attempts: int = 3, 
          delay: float = 1.0, 
          backoff_factor: float = 2.0,
          exceptions: tuple = (Exception,),
          strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF):
    """
    Retry decorator for functions that may fail.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay on each retry
        exceptions: Tuple of exceptions to catch and retry
        strategy: Retry strategy to use
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts - 1:
                        raise RetryException(
                            f"Function {func.__name__} failed after {max_attempts} attempts",
                            max_retries=max_attempts,
                            retry_count=attempt + 1,
                            last_exception=last_exception
                        )
                    
                    logger.warning(
                        f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                        f"Retrying in {current_delay} seconds..."
                    )
                    
                    time.sleep(current_delay)
                    
                    # Calculate next delay based on strategy
                    if strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
                        current_delay *= backoff_factor
                    elif strategy == RetryStrategy.LINEAR_BACKOFF:
                        current_delay += delay
                    elif strategy == RetryStrategy.FIBONACCI_BACKOFF:
                        current_delay = delay * (1.618 ** attempt)
                    # For IMMEDIATE and RANDOM, delay stays the same
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts - 1:
                        raise RetryException(
                            f"Function {func.__name__} failed after {max_attempts} attempts",
                            max_retries=max_attempts,
                            retry_count=attempt + 1,
                            last_exception=last_exception
                        )
                    
                    logger.warning(
                        f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                        f"Retrying in {current_delay} seconds..."
                    )
                    
                    await asyncio.sleep(current_delay)
                    
                    # Calculate next delay based on strategy
                    if strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
                        current_delay *= backoff_factor
                    elif strategy == RetryStrategy.LINEAR_BACKOFF:
                        current_delay += delay
                    elif strategy == RetryStrategy.FIBONACCI_BACKOFF:
                        current_delay = delay * (1.618 ** attempt)
                    # For IMMEDIATE and RANDOM, delay stays the same
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def timeout(seconds: float):
    """
    Timeout decorator for functions.
    
    Args:
        seconds: Maximum execution time in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutException(
                    f"Function {func.__name__} timed out after {seconds} seconds",
                    timeout_duration=seconds,
                    operation=func.__name__
                )
            
            # Set signal handler
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(seconds))
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # Restore signal handler
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                raise TimeoutException(
                    f"Function {func.__name__} timed out after {seconds} seconds",
                    timeout_duration=seconds,
                    operation=func.__name__
                )
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def cache(ttl: Optional[int] = None, key_func: Optional[Callable] = None):
    """
    Cache decorator for function results.
    
    Args:
        ttl: Time to live for cached results in seconds
        key_func: Function to generate cache key from function arguments
    """
    def decorator(func: Callable) -> Callable:
        # Simple in-memory cache (in production, use Redis or similar)
        cache_store = {}
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                args_str = str(args)
                kwargs_str = str(sorted(kwargs.items()))
                cache_key = f"{func.__name__}:{hash(args_str + kwargs_str)}"
            
            # Check cache
            if cache_key in cache_store:
                cached_result, timestamp = cache_store[cache_key]
                if ttl is None or (time.time() - timestamp) < ttl:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_store[cache_key] = (result, time.time())
            logger.debug(f"Cache miss for {func.__name__}, result cached")
            
            return result
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                args_str = str(args)
                kwargs_str = str(sorted(kwargs.items()))
                cache_key = f"{func.__name__}:{hash(args_str + kwargs_str)}"
            
            # Check cache
            if cache_key in cache_store:
                cached_result, timestamp = cache_store[cache_key]
                if ttl is None or (time.time() - timestamp) < ttl:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache_store[cache_key] = (result, time.time())
            logger.debug(f"Cache miss for {func.__name__}, result cached")
            
            return result
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def validate(validator_func: Callable, error_message: Optional[str] = None):
    """
    Validation decorator for function arguments.
    
    Args:
        validator_func: Function that validates arguments and returns bool
        error_message: Custom error message for validation failures
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not validator_func(*args, **kwargs):
                msg = error_message or f"Validation failed for {func.__name__}"
                raise ValidationException(msg)
            return func(*args, **kwargs)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not validator_func(*args, **kwargs):
                msg = error_message or f"Validation failed for {func.__name__}"
                raise ValidationException(msg)
            return await func(*args, **kwargs)
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def log_execution(level: LogLevel = LogLevel.INFO, 
                  include_args: bool = True, 
                  include_result: bool = False,
                  include_execution_time: bool = True):
    """
    Logging decorator for function execution.
    
    Args:
        level: Log level for execution logs
        include_args: Whether to log function arguments
        include_result: Whether to log function result
        include_execution_time: Whether to log execution time
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Log function entry
            log_msg = f"Executing {func.__name__}"
            if include_args:
                log_msg += f" with args={args}, kwargs={kwargs}"
            
            logger.log(getattr(logging, level.upper()), log_msg)
            
            try:
                result = func(*args, **kwargs)
                
                # Log function exit
                log_msg = f"Completed {func.__name__}"
                if include_execution_time:
                    execution_time = time.time() - start_time
                    log_msg += f" in {execution_time:.4f}s"
                if include_result:
                    log_msg += f" with result={result}"
                
                logger.log(getattr(logging, level.upper()), log_msg)
                
                return result
                
            except Exception as e:
                # Log function failure
                log_msg = f"Failed {func.__name__}"
                if include_execution_time:
                    execution_time = time.time() - start_time
                    log_msg += f" after {execution_time:.4f}s"
                log_msg += f" with error: {e}"
                
                logger.error(log_msg)
                raise
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Log function entry
            log_msg = f"Executing {func.__name__}"
            if include_args:
                log_msg += f" with args={args}, kwargs={kwargs}"
            
            logger.log(getattr(logging, level.upper()), log_msg)
            
            try:
                result = await func(*args, **kwargs)
                
                # Log function exit
                log_msg = f"Completed {func.__name__}"
                if include_execution_time:
                    execution_time = time.time() - start_time
                    log_msg += f" in {execution_time:.4f}s"
                if include_result:
                    log_msg += f" with result={result}"
                
                logger.log(getattr(logging, level.upper()), log_msg)
                
                return result
                
            except Exception as e:
                # Log function failure
                log_msg = f"Failed {func.__name__}"
                if include_execution_time:
                    execution_time = time.time() - start_time
                    log_msg += f" after {execution_time:.4f}s"
                log_msg += f" with error: {e}"
                
                logger.error(log_msg)
                raise
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def measure_performance(threshold_seconds: Optional[float] = None):
    """
    Performance measurement decorator.
    
    Args:
        threshold_seconds: Log warning if execution time exceeds this threshold
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            if threshold_seconds and execution_time > threshold_seconds:
                logger.warning(
                    f"Function {func.__name__} took {execution_time:.4f}s "
                    f"(threshold: {threshold_seconds}s)"
                )
            else:
                logger.debug(
                    f"Function {func.__name__} took {execution_time:.4f}s"
                )
            
            return result
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            if threshold_seconds and execution_time > threshold_seconds:
                logger.warning(
                    f"Function {func.__name__} took {execution_time:.4f}s "
                    f"(threshold: {threshold_seconds}s)"
                )
            else:
                logger.debug(
                    f"Function {func.__name__} took {execution_time:.4f}s"
                )
            
            return result
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def require_auth(permission: Optional[str] = None):
    """
    Authentication decorator for functions.
    
    Args:
        permission: Required permission for the function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # This is a placeholder - in a real implementation, you would:
            # 1. Extract user from request context
            # 2. Check if user is authenticated
            # 3. Check if user has required permission
            # 4. Raise AuthenticationException or AuthorizationException if needed
            
            # For now, we'll just log and continue
            logger.debug(f"Authentication check for {func.__name__}")
            if permission:
                logger.debug(f"Permission required: {permission}")
            
            return func(*args, **kwargs)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Same placeholder logic as sync version
            logger.debug(f"Authentication check for {func.__name__}")
            if permission:
                logger.debug(f"Permission required: {permission}")
            
            return await func(*args, **kwargs)
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def require_permission(permissions: Union[str, List[str]]):
    """
    Permission decorator for functions.
    
    Args:
        permissions: Required permission(s) for the function
    """
    if isinstance(permissions, str):
        permissions = [permissions]
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # This is a placeholder - in a real implementation, you would:
            # 1. Extract user from request context
            # 2. Check if user has all required permissions
            # 3. Raise AuthorizationException if needed
            
            logger.debug(f"Permission check for {func.__name__}: {permissions}")
            return func(*args, **kwargs)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Same placeholder logic as sync version
            logger.debug(f"Permission check for {func.__name__}: {permissions}")
            return await func(*args, **kwargs)
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def singleton(cls: Type):
    """
    Singleton decorator for classes.
    
    Args:
        cls: Class to make singleton
    """
    instances = {}
    
    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance


def deprecated(reason: str = "This function is deprecated"):
    """
    Deprecation decorator for functions.
    
    Args:
        reason: Reason for deprecation
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger.warning(f"DEPRECATED: {func.__name__} - {reason}")
            return func(*args, **kwargs)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger.warning(f"DEPRECATED: {func.__name__} - {reason}")
            return await func(*args, **kwargs)
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def rate_limit(max_calls: int, time_window: float):
    """
    Rate limiting decorator.
    
    Args:
        max_calls: Maximum number of calls allowed in time window
        time_window: Time window in seconds
    """
    def decorator(func: Callable) -> Callable:
        # Simple in-memory rate limiting (in production, use Redis or similar)
        call_times = []
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            current_time = time.time()
            
            # Remove old calls outside the time window
            call_times[:] = [t for t in call_times if current_time - t < time_window]
            
            if len(call_times) >= max_calls:
                raise Exception(f"Rate limit exceeded for {func.__name__}")
            
            call_times.append(current_time)
            return func(*args, **kwargs)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            current_time = time.time()
            
            # Remove old calls outside the time window
            call_times[:] = [t for t in call_times if current_time - t < time_window]
            
            if len(call_times) >= max_calls:
                raise Exception(f"Rate limit exceeded for {func.__name__}")
            
            call_times.append(current_time)
            return await func(*args, **kwargs)
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
