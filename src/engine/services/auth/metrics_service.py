"""
Metrics Service - Handles user metrics and analytics.

This service provides business logic for metrics operations including:
- UserMetrics collection
- User behavior analytics
- Performance tracking
- Usage reporting
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter

from ...repositories.auth_repository import AuthRepository
from ...models.auth import User
from .user_service import UserService
from .auth_service import AuthService
from ..base.base_service import BaseService

logger = logging.getLogger(__name__)


@dataclass
class UserMetrics:
    """User metrics data structure."""
    user_id: str
    login_count: int = 0
    last_login: Optional[str] = None
    session_duration_avg: float = 0.0
    total_session_time: float = 0.0
    failed_login_attempts: int = 0
    password_changes: int = 0
    last_activity: Optional[str] = None
    activity_count: int = 0
    created_at: str = None
    updated_at: str = None


@dataclass
class SystemMetrics:
    """System-wide metrics data structure."""
    total_users: int = 0
    active_users: int = 0
    total_sessions: int = 0
    active_sessions: int = 0
    failed_logins: int = 0
    successful_logins: int = 0
    password_resets: int = 0
    account_lockouts: int = 0
    last_updated: str = None


@dataclass
class ActivityMetrics:
    """Activity metrics data structure."""
    user_id: str
    activity_type: str
    count: int = 0
    last_occurrence: Optional[str] = None
    first_occurrence: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    metric_name: str
    value: float
    unit: str
    timestamp: str
    context: Dict[str, Any] = None


class MetricsService(BaseService):
    """
    Service for managing user metrics and analytics.
    
    Handles metrics collection, analysis, reporting, and performance
    tracking across the authentication system.
    """
    
    def __init__(self, auth_repository: AuthRepository, 
                 user_service: UserService, auth_service: AuthService):
        """
        Initialize the MetricsService.
        
        Args:
            auth_repository: Repository for metrics data operations
            user_service: Service for user operations
            auth_service: Service for authentication operations
        """
        super().__init__()
        self.auth_repository = auth_repository
        self.user_service = user_service
        self.auth_service = auth_service
        
        # In-memory data structures for fast access
        self._user_metrics: Dict[str, UserMetrics] = {}
        self._system_metrics: SystemMetrics = SystemMetrics()
        self._activity_metrics: Dict[str, Dict[str, ActivityMetrics]] = {}  # user_id -> activity_type -> metrics
        self._performance_metrics: List[PerformanceMetrics] = []
        self._metrics_cache: Dict[str, Any] = {}
        self._last_metrics_update: Optional[datetime] = None
        
        # Metrics collection settings
        self._collection_interval = 300  # 5 minutes
        self._retention_days = 90
        
        # Initialize metrics
        asyncio.create_task(self._initialize_service_resources())
    
    async def collect_user_metrics(self, user_id: str) -> Optional[UserMetrics]:
        """
        Collect comprehensive metrics for a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            User metrics or None if failed
        """
        try:
            self._log_operation("collect_user_metrics", f"user_id: {user_id}")
            
            # Get user
            user = await self.user_service.get_user_by_id(user_id)
            if not user:
                return None
            
            # Get user activity
            activities = await self.user_service.get_user_activity(user_id, limit=1000)
            
            # Calculate metrics
            metrics = UserMetrics(
                user_id=user_id,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            # Login metrics
            login_activities = [a for a in activities if a.get('type') == 'login_successful']
            metrics.login_count = len(login_activities)
            if login_activities:
                metrics.last_login = login_activities[-1]['timestamp']
            
            # Session metrics
            session_activities = [a for a in activities if a.get('type') in ['login_successful', 'logout']]
            if len(session_activities) >= 2:
                total_duration = 0
                session_count = 0
                for i in range(0, len(session_activities) - 1, 2):
                    if i + 1 < len(session_activities):
                        login_time = datetime.fromisoformat(session_activities[i]['timestamp'])
                        logout_time = datetime.fromisoformat(session_activities[i + 1]['timestamp'])
                        duration = (logout_time - login_time).total_seconds() / 60  # minutes
                        total_duration += duration
                        session_count += 1
                
                if session_count > 0:
                    metrics.session_duration_avg = total_duration / session_count
                    metrics.total_session_time = total_duration
            
            # Failed login attempts
            failed_logins = [a for a in activities if a.get('type') == 'login_failed']
            metrics.failed_login_attempts = len(failed_logins)
            
            # Password changes
            password_changes = [a for a in activities if a.get('type') == 'password_changed']
            metrics.password_changes = len(password_changes)
            
            # General activity
            metrics.activity_count = len(activities)
            if activities:
                metrics.last_activity = activities[-1]['timestamp']
            
            # Store metrics
            self._user_metrics[user_id] = metrics
            
            # Update system metrics
            await self._update_system_metrics()
            
            logger.info(f"User metrics collected for: {user_id}")
            return metrics
            
        except Exception as e:
            self.handle_error("collect_user_metrics", e)
            return None
    
    async def get_user_metrics(self, user_id: str) -> Optional[UserMetrics]:
        """
        Get metrics for a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            User metrics or None if not found
        """
        try:
            # Check cache first
            if user_id in self._user_metrics:
                return self._user_metrics[user_id]
            
            # Collect metrics if not available
            return await self.collect_user_metrics(user_id)
            
        except Exception as e:
            self.handle_error("get_user_metrics", e)
            return None
    
    async def get_all_user_metrics(self) -> List[UserMetrics]:
        """
        Get metrics for all users.
        
        Returns:
            List of all user metrics
        """
        try:
            # Get all users
            users = await self.user_service.get_user_by_id("all")  # This would need to be implemented
            if not users:
                return list(self._user_metrics.values())
            
            # Collect metrics for all users
            all_metrics = []
            for user in users:
                metrics = await self.get_user_metrics(user.user_id)
                if metrics:
                    all_metrics.append(metrics)
            
            return all_metrics
            
        except Exception as e:
            self.handle_error("get_all_user_metrics", e)
            return list(self._user_metrics.values())
    
    async def get_system_metrics(self) -> SystemMetrics:
        """
        Get system-wide metrics.
        
        Returns:
            System metrics
        """
        try:
            # Update system metrics if needed
            if (not self._last_metrics_update or 
                (datetime.now() - self._last_metrics_update).total_seconds() > self._collection_interval):
                await self._update_system_metrics()
            
            return self._system_metrics
            
        except Exception as e:
            self.handle_error("get_system_metrics", e)
            return self._system_metrics
    
    async def track_activity(self, user_id: str, activity_type: str, 
                           metadata: Dict[str, Any] = None) -> bool:
        """
        Track user activity for metrics.
        
        Args:
            user_id: User identifier
            activity_type: Type of activity
            metadata: Additional activity metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Initialize activity metrics for user if not exists
            if user_id not in self._activity_metrics:
                self._activity_metrics[user_id] = {}
            
            if activity_type not in self._activity_metrics[user_id]:
                self._activity_metrics[user_id][activity_type] = ActivityMetrics(
                    user_id=user_id,
                    activity_type=activity_type,
                    first_occurrence=datetime.now().isoformat()
                )
            
            # Update activity metrics
            activity_metrics = self._activity_metrics[user_id][activity_type]
            activity_metrics.count += 1
            activity_metrics.last_occurrence = datetime.now().isoformat()
            if metadata:
                activity_metrics.metadata = metadata
            
            # Update user metrics
            if user_id in self._user_metrics:
                self._user_metrics[user_id].activity_count += 1
                self._user_metrics[user_id].last_activity = datetime.now().isoformat()
                self._user_metrics[user_id].updated_at = datetime.now().isoformat()
            
            return True
            
        except Exception as e:
            self.handle_error("track_activity", e)
            return False
    
    async def get_activity_metrics(self, user_id: str = None, 
                                 activity_type: str = None) -> List[ActivityMetrics]:
        """
        Get activity metrics for users or specific activity types.
        
        Args:
            user_id: User identifier (optional, if None returns all users)
            activity_type: Activity type (optional, if None returns all types)
            
        Returns:
            List of activity metrics
        """
        try:
            if user_id:
                if user_id not in self._activity_metrics:
                    return []
                
                if activity_type:
                    return [self._activity_metrics[user_id].get(activity_type)] if self._activity_metrics[user_id].get(activity_type) else []
                else:
                    return list(self._activity_metrics[user_id].values())
            else:
                all_metrics = []
                for user_metrics in self._activity_metrics.values():
                    if activity_type:
                        if activity_type in user_metrics:
                            all_metrics.append(user_metrics[activity_type])
                    else:
                        all_metrics.extend(user_metrics.values())
                return all_metrics
                
        except Exception as e:
            self.handle_error("get_activity_metrics", e)
            return []
    
    async def record_performance_metric(self, metric_name: str, value: float, 
                                      unit: str, context: Dict[str, Any] = None) -> bool:
        """
        Record a performance metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
            context: Additional context information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            metric = PerformanceMetrics(
                metric_name=metric_name,
                value=value,
                unit=unit,
                timestamp=datetime.now().isoformat(),
                context=context or {}
            )
            
            self._performance_metrics.append(metric)
            
            # Keep only recent metrics (last 1000)
            if len(self._performance_metrics) > 1000:
                self._performance_metrics = self._performance_metrics[-1000:]
            
            return True
            
        except Exception as e:
            self.handle_error("record_performance_metric", e)
            return False
    
    async def get_performance_metrics(self, metric_name: str = None, 
                                    limit: int = 100) -> List[PerformanceMetrics]:
        """
        Get performance metrics.
        
        Args:
            metric_name: Filter by metric name (optional)
            limit: Maximum number of metrics to return
            
        Returns:
            List of performance metrics
        """
        try:
            if metric_name:
                filtered_metrics = [m for m in self._performance_metrics if m.metric_name == metric_name]
                return filtered_metrics[-limit:]
            else:
                return self._performance_metrics[-limit:]
                
        except Exception as e:
            self.handle_error("get_performance_metrics", e)
            return []
    
    async def generate_usage_report(self, start_date: str = None, 
                                  end_date: str = None) -> Dict[str, Any]:
        """
        Generate a comprehensive usage report.
        
        Args:
            start_date: Report start date (ISO format)
            end_date: Report end date (ISO format)
            
        Returns:
            Usage report data
        """
        try:
            self._log_operation("generate_usage_report", f"start: {start_date}, end: {end_date}")
            
            # Parse dates
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).isoformat()
            if not end_date:
                end_date = datetime.now().isoformat()
            
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
            
            # Get system metrics
            system_metrics = await self.get_system_metrics()
            
            # Get user metrics for the period
            user_metrics = []
            for metrics in self._user_metrics.values():
                if metrics.created_at:
                    created_dt = datetime.fromisoformat(metrics.created_at)
                    if start_dt <= created_dt <= end_dt:
                        user_metrics.append(metrics)
            
            # Calculate period statistics
            period_stats = {
                "new_users": len([m for m in user_metrics if m.created_at and start_dt <= datetime.fromisoformat(m.created_at) <= end_dt]),
                "active_users": len([m for m in user_metrics if m.last_activity and start_dt <= datetime.fromisoformat(m.last_activity) <= end_dt]),
                "total_logins": sum(m.login_count for m in user_metrics),
                "total_activities": sum(m.activity_count for m in user_metrics),
                "avg_session_duration": sum(m.session_duration_avg for m in user_metrics) / len(user_metrics) if user_metrics else 0
            }
            
            # Generate report
            report = {
                "report_period": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "system_overview": {
                    "total_users": system_metrics.total_users,
                    "active_users": system_metrics.active_users,
                    "total_sessions": system_metrics.total_sessions,
                    "active_sessions": system_metrics.active_sessions
                },
                "period_statistics": period_stats,
                "top_users": sorted(user_metrics, key=lambda x: x.activity_count, reverse=True)[:10],
                "activity_breakdown": await self._get_activity_breakdown(start_dt, end_dt),
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info("Usage report generated successfully")
            return report
            
        except Exception as e:
            self.handle_error("generate_usage_report", e)
            return {}
    
    async def get_user_behavior_analytics(self, user_id: str) -> Dict[str, Any]:
        """
        Get behavioral analytics for a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            User behavior analytics
        """
        try:
            # Get user metrics
            metrics = await self.get_user_metrics(user_id)
            if not metrics:
                return {}
            
            # Get activity metrics
            activities = await self.user_service.get_user_activity(user_id, limit=1000)
            
            # Analyze behavior patterns
            behavior_analytics = {
                "user_id": user_id,
                "engagement_level": self._calculate_engagement_level(metrics),
                "activity_patterns": self._analyze_activity_patterns(activities),
                "session_behavior": self._analyze_session_behavior(activities),
                "security_metrics": {
                    "failed_logins": metrics.failed_login_attempts,
                    "password_changes": metrics.password_changes,
                    "last_login": metrics.last_login
                },
                "recommendations": self._generate_user_recommendations(metrics, activities)
            }
            
            return behavior_analytics
            
        except Exception as e:
            self.handle_error("get_user_behavior_analytics", e)
            return {}
    
    async def _update_system_metrics(self) -> None:
        """Update system-wide metrics."""
        try:
            # Get user counts
            total_users = await self.user_service.get_total_users_count()
            active_users = await self.user_service.get_active_users_count()
            
            # Get session counts
            total_sessions = 0
            active_sessions = 0
            for user_id in self._user_metrics:
                if user_id in self._user_metrics:
                    metrics = self._user_metrics[user_id]
                    total_sessions += metrics.login_count
                    if metrics.last_activity:
                        last_activity = datetime.fromisoformat(metrics.last_activity)
                        if (datetime.now() - last_activity).total_seconds() < 3600:  # 1 hour
                            active_sessions += 1
            
            # Update system metrics
            self._system_metrics.total_users = total_users
            self._system_metrics.active_users = active_users
            self._system_metrics.total_sessions = total_sessions
            self._system_metrics.active_sessions = active_sessions
            self._system_metrics.last_updated = datetime.now().isoformat()
            
            self._last_metrics_update = datetime.now()
            
        except Exception as e:
            logger.error(f"Failed to update system metrics: {e}")
    
    async def _get_activity_breakdown(self, start_dt: datetime, end_dt: datetime) -> Dict[str, int]:
        """Get activity breakdown for a time period."""
        try:
            activity_counts = Counter()
            
            for user_metrics in self._activity_metrics.values():
                for activity_type, metrics in user_metrics.items():
                    if metrics.last_occurrence:
                        last_occurrence = datetime.fromisoformat(metrics.last_occurrence)
                        if start_dt <= last_occurrence <= end_dt:
                            activity_counts[activity_type] += metrics.count
            
            return dict(activity_counts)
            
        except Exception as e:
            logger.error(f"Failed to get activity breakdown: {e}")
            return {}
    
    def _calculate_engagement_level(self, metrics: UserMetrics) -> str:
        """Calculate user engagement level."""
        try:
            if metrics.activity_count >= 100:
                return "high"
            elif metrics.activity_count >= 50:
                return "medium"
            elif metrics.activity_count >= 10:
                return "low"
            else:
                return "minimal"
                
        except Exception as e:
            logger.error(f"Failed to calculate engagement level: {e}")
            return "unknown"
    
    def _analyze_activity_patterns(self, activities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user activity patterns."""
        try:
            if not activities:
                return {}
            
            # Group activities by hour of day
            hourly_patterns = defaultdict(int)
            for activity in activities:
                if activity.get('timestamp'):
                    hour = datetime.fromisoformat(activity['timestamp']).hour
                    hourly_patterns[hour] += 1
            
            # Find peak activity hours
            peak_hours = sorted(hourly_patterns.items(), key=lambda x: x[1], reverse=True)[:3]
            
            return {
                "total_activities": len(activities),
                "hourly_patterns": dict(hourly_patterns),
                "peak_activity_hours": [hour for hour, _ in peak_hours],
                "activity_frequency": "daily" if len(activities) > 10 else "occasional"
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze activity patterns: {e}")
            return {}
    
    def _analyze_session_behavior(self, activities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user session behavior."""
        try:
            login_activities = [a for a in activities if a.get('type') == 'login_successful']
            logout_activities = [a for a in activities if a.get('type') == 'logout']
            
            session_count = min(len(login_activities), len(logout_activities))
            
            return {
                "total_sessions": session_count,
                "session_frequency": "frequent" if session_count > 5 else "moderate" if session_count > 2 else "occasional",
                "last_session": login_activities[-1]['timestamp'] if login_activities else None
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze session behavior: {e}")
            return {}
    
    def _generate_user_recommendations(self, metrics: UserMetrics, 
                                     activities: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations for user improvement."""
        try:
            recommendations = []
            
            if metrics.failed_login_attempts > 3:
                recommendations.append("Consider enabling two-factor authentication for enhanced security")
            
            if metrics.activity_count < 5:
                recommendations.append("Explore more features to increase engagement")
            
            if not metrics.last_login or (datetime.now() - datetime.fromisoformat(metrics.last_login)).days > 30:
                recommendations.append("Your account has been inactive - consider logging in to stay updated")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return []
    
    def _initialize_metrics(self) -> None:
        """Initialize metrics data structures."""
        try:
            self._system_metrics = SystemMetrics(
                last_updated=datetime.now().isoformat()
            )
            self._last_metrics_update = datetime.now()
            
            logger.info("Metrics service initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize metrics: {e}")
    
    async def _initialize_service_resources(self) -> None:
        """Initialize service-specific resources."""
        try:
            # Initialize metrics-related resources
            self._user_metrics = {}
            self._activity_metrics = {}
            self._performance_metrics = []
            self._metrics_cache = {}
            self._last_metrics_update = None
            
            # Initialize metrics
            self._initialize_metrics()
            logger.info("Metrics service resources initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize metrics service resources: {e}")
    
    async def get_service_info(self) -> Dict[str, Any]:
        """Get service information and status."""
        return {
            "service_name": "MetricsService",
            "service_type": "authentication",
            "status": "active" if self.is_active else "inactive",
            "start_time": self.start_time.isoformat(),
            "total_user_metrics": len(self._user_metrics),
            "total_activity_metrics": sum(len(metrics) for metrics in self._activity_metrics.values()),
            "performance_metrics_count": len(self._performance_metrics),
            "metrics_cache_size": len(self._metrics_cache),
            "last_metrics_update": self._last_metrics_update.isoformat() if self._last_metrics_update else None,
            "collection_interval_seconds": self._collection_interval,
            "retention_days": self._retention_days,
            "health_status": self.health_status,
            "last_health_check": self.last_health_check.isoformat(),
            "dependencies": self.dependencies,
            "performance_metrics": self.get_performance_summary()
        }
    
    async def _cleanup_service_resources(self) -> None:
        """Clean up service resources."""
        try:
            # Clear in-memory structures
            self._user_metrics.clear()
            self._activity_metrics.clear()
            self._performance_metrics.clear()
            self._metrics_cache.clear()
            
            logger.info("Metrics service resources cleaned up")
            
        except Exception as e:
            logger.error(f"Failed to cleanup metrics service resources: {e}")
    
    async def shutdown(self) -> None:
        """Shutdown the metrics service."""
        try:
            await self._cleanup_service_resources()
            logger.info("Metrics service shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during metrics service shutdown: {e}")
