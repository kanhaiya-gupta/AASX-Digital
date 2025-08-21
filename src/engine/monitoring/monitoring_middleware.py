"""
Monitoring Middleware

Middleware components for integrating monitoring into web frameworks and APIs.
Provides request/response monitoring, performance tracking, and error handling.
"""

import time
import asyncio
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
import logging
import json
import uuid

from .monitoring_config import MonitoringConfig
from .metrics_collector import MetricsCollector
from .performance_profiler import PerformanceProfiler
from .alert_manager import AlertManager, AlertSeverity


@dataclass
class RequestContext:
    """Request context for monitoring"""
    request_id: str
    method: str
    path: str
    query_params: Dict[str, Any]
    headers: Dict[str, str]
    start_time: float
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class ResponseContext:
    """Response context for monitoring"""
    request_id: str
    status_code: int
    response_time: float
    response_size: int
    end_time: float
    error_message: Optional[str] = None


class MonitoringMiddleware:
    """Middleware for monitoring web requests and API calls"""
    
    def __init__(self, config: MonitoringConfig, metrics_collector: MetricsCollector,
                 performance_profiler: PerformanceProfiler, alert_manager: AlertManager):
        self.config = config
        self.metrics_collector = metrics_collector
        self.performance_profiler = performance_profiler
        self.alert_manager = alert_manager
        self.logger = logging.getLogger(__name__)
        
        # Request tracking
        self.active_requests: Dict[str, RequestContext] = {}
        self.request_history: List[Dict[str, Any]] = []
        
        # Performance thresholds
        self._slow_request_threshold = 5.0  # seconds
        self._error_rate_threshold = 0.05  # 5%
        
        # Initialize metrics
        self._init_metrics()
    
    def _init_metrics(self):
        """Initialize monitoring metrics"""
        # Request metrics
        self.metrics_collector.create_metric(
            "http.requests.total", "Total HTTP requests", "count", "counter"
        )
        self.metrics_collector.create_metric(
            "http.requests.active", "Active HTTP requests", "count", "gauge"
        )
        self.metrics_collector.create_metric(
            "http.requests.duration", "HTTP request duration", "seconds", "histogram"
        )
        self.metrics_collector.create_metric(
            "http.requests.size", "HTTP request/response size", "bytes", "histogram"
        )
        
        # Response metrics
        self.metrics_collector.create_metric(
            "http.responses.total", "Total HTTP responses", "count", "counter"
        )
        self.metrics_collector.create_metric(
            "http.responses.success", "Successful HTTP responses", "count", "counter"
        )
        self.metrics_collector.create_metric(
            "http.responses.error", "Error HTTP responses", "count", "counter"
        )
        self.metrics_collector.create_metric(
            "http.responses.status_codes", "HTTP response status codes", "count", "counter"
        )
    
    def start_request(self, method: str, path: str, query_params: Optional[Dict[str, Any]] = None,
                     headers: Optional[Dict[str, str]] = None, client_ip: Optional[str] = None,
                     user_agent: Optional[str] = None, user_id: Optional[str] = None,
                     session_id: Optional[str] = None) -> str:
        """Start monitoring a request"""
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Create request context
        request_context = RequestContext(
            request_id=request_id,
            method=method.upper(),
            path=path,
            query_params=query_params or {},
            headers=headers or {},
            start_time=start_time,
            client_ip=client_ip,
            user_agent=user_agent,
            user_id=user_id,
            session_id=session_id
        )
        
        # Store active request
        self.active_requests[request_id] = request_context
        
        # Update metrics
        self.metrics_collector.increment_counter("http.requests.total")
        self.metrics_collector.set_gauge("http.requests.active", len(self.active_requests))
        
        # Start performance profiling
        if self.config.performance.profile_api:
            self.performance_profiler.start_operation(
                f"http.{method.lower()}.{path.replace('/', '_')}",
                operation_id=request_id,
                tags=["http", "api", method.lower()],
                metadata={
                    "path": path,
                    "method": method,
                    "client_ip": client_ip,
                    "user_id": user_id
                }
            )
        
        self.logger.debug(f"Started monitoring request {request_id}: {method} {path}")
        return request_id
    
    def end_request(self, request_id: str, status_code: int, response_size: int = 0,
                   error_message: Optional[str] = None):
        """End monitoring a request"""
        if request_id not in self.active_requests:
            self.logger.warning(f"Request {request_id} not found in active requests")
            return
        
        request_context = self.active_requests.pop(request_id)
        end_time = time.time()
        response_time = end_time - request_context.start_time
        
        # Create response context
        response_context = ResponseContext(
            request_id=request_id,
            status_code=status_code,
            response_time=response_time,
            response_size=response_size,
            error_message=error_message,
            end_time=end_time
        )
        
        # Update metrics
        self.metrics_collector.set_gauge("http.requests.active", len(self.active_requests))
        self.metrics_collector.increment_counter("http.responses.total")
        
        # Record response time
        self.metrics_collector.record_histogram("http.requests.duration", response_time)
        self.metrics_collector.record_histogram("http.requests.size", response_size)
        
        # Record status code
        self.metrics_collector.increment_counter(
            "http.responses.status_codes",
            labels={"status_code": str(status_code)}
        )
        
        # Record success/error
        if 200 <= status_code < 400:
            self.metrics_collector.increment_counter("http.responses.success")
        else:
            self.metrics_collector.increment_counter("http.responses.error")
        
        # End performance profiling
        if self.config.performance.profile_api:
            self.performance_profiler.end_operation(
                request_id,
                success=(200 <= status_code < 400),
                error_message=error_message,
                metadata={
                    "status_code": status_code,
                    "response_size": response_size,
                    "response_time": response_time
                }
            )
        
        # Check for slow requests
        if response_time > self._slow_request_threshold:
            self._handle_slow_request(request_context, response_context)
        
        # Check for errors
        if status_code >= 400:
            self._handle_error_response(request_context, response_context)
        
        # Store request history
        self._store_request_history(request_context, response_context)
        
        # Cleanup old history
        self._cleanup_request_history()
        
        self.logger.debug(f"Ended monitoring request {request_id}: {status_code} in {response_time:.3f}s")
    
    def _handle_slow_request(self, request_context: RequestContext, response_context: ResponseContext):
        """Handle slow request detection"""
        self.logger.warning(
            f"Slow request detected: {request_context.method} {request_context.path} "
            f"took {response_context.response_time:.3f}s (threshold: {self._slow_request_threshold:.3f}s)"
        )
        
        # Create alert for slow request
        self.alert_manager.create_alert(
            title="Slow API Request Detected",
            message=f"Request {request_context.method} {request_context.path} took {response_context.response_time:.3f}s",
            severity=AlertSeverity.WARNING,
            source="api_monitoring",
            metadata={
                "method": request_context.method,
                "path": request_context.path,
                "response_time": response_context.response_time,
                "threshold": self._slow_request_threshold,
                "request_id": request_context.request_id
            },
            tags=["slow_request", "api", "performance"]
        )
    
    def _handle_error_response(self, request_context: RequestContext, response_context: ResponseContext):
        """Handle error response detection"""
        self.logger.error(
            f"Error response: {request_context.method} {request_context.path} "
            f"returned {response_context.status_code}: {response_context.error_message}"
        )
        
        # Create alert for error response
        severity = AlertSeverity.ERROR if response_context.status_code < 500 else AlertSeverity.CRITICAL
        
        self.alert_manager.create_alert(
            title=f"API Error Response: {response_context.status_code}",
            message=f"Request {request_context.method} {request_context.path} failed with status {response_context.status_code}",
            severity=severity,
            source="api_monitoring",
            metadata={
                "method": request_context.method,
                "path": request_context.path,
                "status_code": response_context.status_code,
                "error_message": response_context.error_message,
                "request_id": request_context.request_id
            },
            tags=["error_response", "api", "http_error"]
        )
    
    def _store_request_history(self, request_context: RequestContext, response_context: ResponseContext):
        """Store request/response history"""
        history_entry = {
            "request_id": request_context.request_id,
            "timestamp": datetime.fromtimestamp(request_context.start_time).isoformat(),
            "method": request_context.method,
            "path": request_context.path,
            "query_params": request_context.query_params,
            "client_ip": request_context.client_ip,
            "user_id": request_context.user_id,
            "session_id": request_context.session_id,
            "status_code": response_context.status_code,
            "response_time": response_context.response_time,
            "response_size": response_context.response_size,
            "error_message": response_context.error_message
        }
        
        self.request_history.append(history_entry)
    
    def _cleanup_request_history(self):
        """Clean up old request history"""
        max_history = 10000
        if len(self.request_history) > max_history:
            self.request_history = self.request_history[-max_history:]
    
    def get_request_summary(self, window_minutes: int = 60) -> Dict[str, Any]:
        """Get request summary for the specified time window"""
        cutoff_time = time.time() - (window_minutes * 60)
        
        # Filter recent requests
        recent_requests = [
            entry for entry in self.request_history
            if datetime.fromisoformat(entry["timestamp"]).timestamp() >= cutoff_time
        ]
        
        if not recent_requests:
            return {"error": "No request data available for the specified time window"}
        
        # Calculate statistics
        total_requests = len(recent_requests)
        successful_requests = len([r for r in recent_requests if 200 <= r["status_code"] < 400])
        error_requests = len([r for r in recent_requests if r["status_code"] >= 400])
        
        response_times = [r["response_time"] for r in recent_requests]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        # Group by method and path
        method_counts = {}
        path_counts = {}
        status_code_counts = {}
        
        for request in recent_requests:
            method = request["method"]
            path = request["path"]
            status_code = request["status_code"]
            
            method_counts[method] = method_counts.get(method, 0) + 1
            path_counts[path] = path_counts.get(path, 0) + 1
            status_code_counts[str(status_code)] = status_code_counts.get(str(status_code), 0) + 1
        
        return {
            "time_window_minutes": window_minutes,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "error_requests": error_requests,
            "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
            "error_rate": error_requests / total_requests if total_requests > 0 else 0,
            "response_time": {
                "average": avg_response_time,
                "maximum": max_response_time
            },
            "method_breakdown": method_counts,
            "path_breakdown": path_counts,
            "status_code_breakdown": status_code_counts,
            "active_requests": len(self.active_requests)
        }
    
    def get_active_requests(self) -> List[Dict[str, Any]]:
        """Get currently active requests"""
        active_requests = []
        
        for request_id, request_context in self.active_requests.items():
            active_time = time.time() - request_context.start_time
            
            active_requests.append({
                "request_id": request_id,
                "method": request_context.method,
                "path": request_context.path,
                "start_time": datetime.fromtimestamp(request_context.start_time).isoformat(),
                "active_time": active_time,
                "client_ip": request_context.client_ip,
                "user_id": request_context.user_id
            })
        
        return active_requests
    
    def get_slow_requests(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get slowest requests"""
        slow_requests = sorted(
            self.request_history,
            key=lambda x: x["response_time"],
            reverse=True
        )[:limit]
        
        return slow_requests
    
    def get_error_requests(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent error requests"""
        error_requests = [
            request for request in self.request_history
            if request["status_code"] >= 400
        ][-limit:]
        
        return error_requests
    
    def set_slow_request_threshold(self, threshold: float):
        """Set slow request threshold in seconds"""
        if threshold > 0:
            self._slow_request_threshold = threshold
            self.logger.info(f"Slow request threshold set to {threshold}s")
        else:
            raise ValueError("Slow request threshold must be positive")
    
    def set_error_rate_threshold(self, threshold: float):
        """Set error rate threshold (0.0 to 1.0)"""
        if 0.0 <= threshold <= 1.0:
            self._error_rate_threshold = threshold
            self.logger.info(f"Error rate threshold set to {threshold}")
        else:
            raise ValueError("Error rate threshold must be between 0.0 and 1.0")
    
    def reset_request_data(self):
        """Reset all request monitoring data"""
        self.active_requests.clear()
        self.request_history.clear()
        self.logger.info("All request monitoring data reset")
    
    # Flask/Django middleware integration methods
    
    def flask_middleware(self, app):
        """Flask middleware integration"""
        @app.before_request
        def before_request():
            # Extract request information
            method = request.method
            path = request.path
            query_params = dict(request.args)
            headers = dict(request.headers)
            client_ip = request.remote_addr
            user_agent = request.headers.get('User-Agent')
            
            # Get user info if available
            user_id = None
            session_id = None
            if hasattr(request, 'user') and request.user:
                user_id = str(request.user.id)
            if hasattr(request, 'session'):
                session_id = request.session.get('session_id')
            
            # Start monitoring
            request_id = self.start_request(
                method=method,
                path=path,
                query_params=query_params,
                headers=headers,
                client_ip=client_ip,
                user_agent=user_agent,
                user_id=user_id,
                session_id=session_id
            )
            
            # Store request ID for later use
            request.monitoring_request_id = request_id
        
        @app.after_request
        def after_request(response):
            if hasattr(request, 'monitoring_request_id'):
                request_id = request.monitoring_request_id
                
                # End monitoring
                self.end_request(
                    request_id=request_id,
                    status_code=response.status_code,
                    response_size=len(response.get_data()),
                    error_message=None
                )
            
            return response
        
        @app.errorhandler(Exception)
        def handle_exception(error):
            if hasattr(request, 'monitoring_request_id'):
                request_id = request.monitoring_request_id
                
                # End monitoring with error
                self.end_request(
                    request_id=request_id,
                    status_code=500,
                    response_size=0,
                    error_message=str(error)
                )
            
            # Re-raise the exception
            raise error
        
        return app
    
    def django_middleware(self):
        """Django middleware class"""
        class DjangoMonitoringMiddleware:
            def __init__(self, get_response):
                self.get_response = get_response
                self.monitoring = self  # Reference to monitoring instance
            
            def __call__(self, request):
                # Extract request information
                method = request.method
                path = request.path
                query_params = dict(request.GET)
                headers = dict(request.headers)
                client_ip = self._get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT')
                
                # Get user info if available
                user_id = None
                session_id = None
                if hasattr(request, 'user') and request.user.is_authenticated:
                    user_id = str(request.user.id)
                if hasattr(request, 'session'):
                    session_id = request.session.session_key
                
                # Start monitoring
                request_id = self.monitoring.start_request(
                    method=method,
                    path=path,
                    query_params=query_params,
                    headers=headers,
                    client_ip=client_ip,
                    user_agent=user_agent,
                    user_id=user_id,
                    session_id=session_id
                )
                
                # Store request ID
                request.monitoring_request_id = request_id
                
                # Process request
                response = self.get_response(request)
                
                # End monitoring
                self.monitoring.end_request(
                    request_id=request_id,
                    status_code=response.status_code,
                    response_size=len(response.content) if hasattr(response, 'content') else 0,
                    error_message=None
                )
                
                return response
            
            def _get_client_ip(self, request):
                """Get client IP address"""
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    return x_forwarded_for.split(',')[0].strip()
                return request.META.get('REMOTE_ADDR')
        
        return DjangoMonitoringMiddleware
    
    def fastapi_middleware(self, app):
        """FastAPI middleware integration"""
        from fastapi import Request, Response
        from starlette.middleware.base import BaseHTTPMiddleware
        
        class FastAPIMonitoringMiddleware(BaseHTTPMiddleware):
            def __init__(self, app, monitoring):
                super().__init__(app)
                self.monitoring = monitoring
            
            async def dispatch(self, request: Request, call_next):
                # Extract request information
                method = request.method
                path = request.url.path
                query_params = dict(request.query_params)
                headers = dict(request.headers)
                client_ip = request.client.host if request.client else None
                user_agent = request.headers.get('user-agent')
                
                # Start monitoring
                request_id = self.monitoring.start_request(
                    method=method,
                    path=path,
                    query_params=query_params,
                    headers=headers,
                    client_ip=client_ip,
                    user_agent=user_agent
                )
                
                # Store request ID
                request.state.monitoring_request_id = request_id
                
                try:
                    # Process request
                    response = await call_next(request)
                    
                    # End monitoring
                    self.monitoring.end_request(
                        request_id=request_id,
                        status_code=response.status_code,
                        response_size=0,  # FastAPI doesn't provide content length easily
                        error_message=None
                    )
                    
                    return response
                    
                except Exception as error:
                    # End monitoring with error
                    self.monitoring.end_request(
                        request_id=request_id,
                        status_code=500,
                        response_size=0,
                        error_message=str(error)
                    )
                    raise
        
        app.add_middleware(FastAPIMonitoringMiddleware, monitoring=self)
        return app
