"""
Analytics Service for AASX-ETL

This service provides business analytics and dashboard data aggregation
for the AASX-ETL platform. It focuses purely on business metrics,
processing performance, and data trends.

IMPORTANT: This is a USER-BASED FRAMEWORK
- All data must be filtered by user_id or org_id
- Users can only access their own data or organization data
- Authentication context is required for all operations

Phase 5.1: Analytics API Backend
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DashboardMetrics:
    """Dashboard overview metrics."""
    total_projects: int
    total_files: int
    processed_files: int
    success_rate: float
    processing_volume_trend: float
    error_rate: float


@dataclass
class PerformanceMetrics:
    """Processing performance metrics."""
    avg_processing_time: float
    processing_efficiency_score: float
    quality_score_trend: float
    resource_utilization_trend: float


class AnalyticsService:
    """Central service for all analytics data aggregation and retrieval."""
    
    def __init__(self, db_connection):
        self.db = db_connection
        logger.info("AnalyticsService initialized for user-based framework")
    
    def get_dashboard_metrics(self, user_context: Dict[str, Any]) -> DashboardMetrics:
        """
        Get comprehensive dashboard metrics for the authenticated user.
        
        Args:
            user_context: Dictionary containing user authentication context
                - user_id: The authenticated user's ID
                - organization_id: The user's organization ID
                - role: User's role in the system
        
        Returns:
            DashboardMetrics object with user-specific data
        """
        try:
            # Extract user context - REQUIRED for user-based framework
            user_id = user_context.get('user_id')
            org_id = user_context.get('organization_id')
            
            if not user_id:
                logger.error("User ID is required for analytics in user-based framework")
                raise ValueError("User authentication required")
            
            logger.info(f"Getting dashboard metrics for user: {user_id}, org: {org_id}")
            
            # Get total projects (user can see their own projects or org projects)
            total_projects = self._get_total_projects(user_id, org_id)
            
            # Get total files (user can see their own files or org files)
            total_files = self._get_total_files(user_id, org_id)
            
            # Get processed files count (user can see their own processing or org processing)
            processed_files = self._get_processed_files_count(user_id, org_id)
            
            # Calculate success rate (user-specific)
            success_rate = self._calculate_success_rate(user_id, org_id)
            
            # Calculate processing volume trend (user-specific)
            processing_volume_trend = self._calculate_processing_volume_trend(user_id, org_id)
            
            # Calculate error rate (user-specific)
            error_rate = self._calculate_error_rate(user_id, org_id)
            
            return DashboardMetrics(
                total_projects=total_projects,
                total_files=total_files,
                processed_files=processed_files,
                success_rate=success_rate,
                processing_volume_trend=processing_volume_trend,
                error_rate=error_rate
            )
            
        except Exception as e:
            logger.error(f"Failed to get dashboard metrics: {e}")
            # Return default metrics on error
            return DashboardMetrics(
                total_projects=0,
                total_files=0,
                processed_files=0,
                success_rate=0.0,
                processing_volume_trend=0.0,
                error_rate=0.0
            )
    
    def get_performance_metrics(self, user_context: Dict[str, Any], days: int = 30) -> PerformanceMetrics:
        """
        Get processing performance metrics for the authenticated user.
        
        Args:
            user_context: Dictionary containing user authentication context
            days: Number of days to look back for metrics
        
        Returns:
            PerformanceMetrics object with user-specific data
        """
        try:
            # Extract user context - REQUIRED for user-based framework
            user_id = user_context.get('user_id')
            org_id = user_context.get('organization_id')
            
            if not user_id:
                logger.error("User ID is required for analytics in user-based framework")
                raise ValueError("User authentication required")
            
            logger.info(f"Getting performance metrics for user: {user_id}, org: {org_id}, days: {days}")
            
            # Calculate average processing time (user-specific)
            avg_processing_time = self._calculate_avg_processing_time(user_id, org_id, days)
            
            # Calculate processing efficiency score (user-specific)
            processing_efficiency_score = self._calculate_processing_efficiency_score(user_id, org_id, days)
            
            # Calculate quality score trend (user-specific)
            quality_score_trend = self._calculate_quality_score_trend(user_id, org_id, days)
            
            # Calculate resource utilization trend (user-specific)
            resource_utilization_trend = self._calculate_resource_utilization_trend(user_id, org_id, days)
            
            return PerformanceMetrics(
                avg_processing_time=avg_processing_time,
                processing_efficiency_score=processing_efficiency_score,
                quality_score_trend=quality_score_trend,
                resource_utilization_trend=resource_utilization_trend
            )
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            # Return default metrics on error
            return PerformanceMetrics(
                avg_processing_time=0.0,
                processing_efficiency_score=0.0,
                quality_score_trend=0.0,
                resource_utilization_trend=0.0
            )
    
    def get_processing_trends(self, user_context: Dict[str, Any], days: int = 30) -> Dict[str, Any]:
        """
        Get processing trends over time for the authenticated user.
        
        Args:
            user_context: Dictionary containing user authentication context
            days: Number of days to look back for trends
        
        Returns:
            Dictionary with user-specific processing trends
        """
        try:
            # Extract user context - REQUIRED for user-based framework
            user_id = user_context.get('user_id')
            org_id = user_context.get('organization_id')
            
            if not user_id:
                logger.error("User ID is required for analytics in user-based framework")
                raise ValueError("User authentication required")
            
            logger.info(f"Getting processing trends for user: {user_id}, org: {org_id}, days: {days}")
            
            trends = {
                'daily_processing_volume': self._get_daily_processing_volume(user_id, org_id, days),
                'job_type_distribution': self._get_job_type_distribution(user_id, org_id, days),
                'source_type_distribution': self._get_source_type_distribution(user_id, org_id, days),
                'quality_score_trends': self._get_quality_score_trends(user_id, org_id, days),
                'processing_time_trends': self._get_processing_time_trends(user_id, org_id, days)
            }
            return trends
            
        except Exception as e:
            logger.error(f"Failed to get processing trends: {e}")
            return {}
    
    def get_quality_metrics(self, user_context: Dict[str, Any], days: int = 30) -> Dict[str, Any]:
        """
        Get data quality metrics for the authenticated user.
        
        Args:
            user_context: Dictionary containing user authentication context
            days: Number of days to look back for metrics
        
        Returns:
            Dictionary with user-specific quality metrics
        """
        try:
            # Extract user context - REQUIRED for user-based framework
            user_id = user_context.get('user_id')
            org_id = user_context.get('organization_id')
            
            if not user_id:
                logger.error("User ID is required for analytics in user-based framework")
                raise ValueError("User authentication required")
            
            logger.info(f"Getting quality metrics for user: {user_id}, org: {org_id}, days: {days}")
            
            quality_metrics = {
                'overall_quality_score': self._calculate_overall_quality_score(user_id, org_id, days),
                'quality_by_job_type': self._get_quality_by_job_type(user_id, org_id, days),
                'quality_trends': self._get_quality_trends(user_id, org_id, days),
                'validation_results': self._get_validation_results_summary(user_id, org_id, days)
            }
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Failed to get quality metrics: {e}")
            return {}
    
    def get_user_behavior_analytics(self, user_context: Dict[str, Any], days: int = 30) -> Dict[str, Any]:
        """
        Get user behavior analytics for the authenticated user.
        
        Args:
            user_context: Dictionary containing user authentication context
            days: Number of days to look back for analytics
        
        Returns:
            Dictionary with user-specific behavior analytics
        """
        try:
            # Extract user context - REQUIRED for user-based framework
            user_id = user_context.get('user_id')
            org_id = user_context.get('organization_id')
            
            if not user_id:
                logger.error("User ID is required for analytics in user-based framework")
                raise ValueError("User authentication required")
            
            logger.info(f"Getting user behavior analytics for user: {user_id}, org: {org_id}, days: {days}")
            
            behavior_analytics = {
                'upload_patterns': self._analyze_upload_patterns(user_id, org_id, days),
                'processing_patterns': self._analyze_processing_patterns(user_id, org_id, days),
                'session_analytics': self._get_session_analytics(user_id, org_id, days),
                'user_efficiency': self._calculate_user_efficiency(user_id, org_id, days)
            }
            return behavior_analytics
            
        except Exception as e:
            logger.error(f"Failed to get user behavior analytics: {e}")
            return {}
    
    # Private helper methods for data aggregation with USER-BASED filtering
    
    def _get_total_projects(self, user_id: str, org_id: str = None) -> int:
        """
        Get total number of projects for the user.
        
        User can see:
        - Their own projects (user_id)
        - Projects in their organization (org_id)
        """
        query = "SELECT COUNT(*) FROM projects"
        params = []
        
        if user_id:
            query += " WHERE user_id = ?"
            params.append(user_id)
        elif org_id:
            query += " WHERE org_id = ?"
            params.append(org_id)
        
        result = self.db.execute_query(query, params)
        return result[0][0] if result else 0
    
    def _get_total_files(self, user_id: str, org_id: str = None) -> int:
        """
        Get total number of files for the user.
        
        User can see:
        - Files in their own projects (user_id)
        - Files in their organization's projects (org_id)
        """
        query = "SELECT COUNT(*) FROM files"
        params = []
        
        if user_id:
            # User can see files in their own projects
            query = """
                SELECT COUNT(*) FROM files f
                JOIN projects p ON f.project_id = p.project_id
                WHERE p.user_id = ?
            """
            params.append(user_id)
        elif org_id:
            # User can see files in their organization's projects
            query = """
                SELECT COUNT(*) FROM files f
                JOIN projects p ON f.project_id = p.project_id
                WHERE p.org_id = ?
            """
            params.append(org_id)
        
        result = self.db.execute_query(query, params)
        return result[0][0] if result else 0
    
    def _get_processed_files_count(self, user_id: str, org_id: str = None) -> int:
        """
        Get count of processed files for the user.
        
        User can see:
        - Their own processing jobs (user_id)
        - Processing jobs in their organization (org_id)
        """
        query = "SELECT COUNT(*) FROM aasx_processing WHERE processing_status = 'completed'"
        params = []
        
        if user_id:
            query += " AND processed_by = ?"
            params.append(user_id)
        elif org_id:
            query += " AND org_id = ?"
            params.append(org_id)
        
        result = self.db.execute_query(query, params)
        return result[0][0] if result else 0
    
    def _calculate_success_rate(self, user_id: str, org_id: str = None) -> float:
        """
        Calculate processing success rate for the user.
        
        User can see:
        - Their own job success rates (user_id)
        - Organization job success rates (org_id)
        """
        try:
            total_jobs = self._get_total_jobs_count(user_id, org_id)
            if total_jobs == 0:
                return 0.0
            
            successful_jobs = self._get_successful_jobs_count(user_id, org_id)
            return (successful_jobs / total_jobs) * 100
            
        except Exception as e:
            logger.error(f"Failed to calculate success rate: {e}")
            return 0.0
    
    def _calculate_processing_volume_trend(self, user_id: str, org_id: str = None) -> float:
        """
        Calculate processing volume trend for the user.
        
        User can see:
        - Their own processing volume trends (user_id)
        - Organization processing volume trends (org_id)
        """
        try:
            # Get current period (last 7 days) vs previous period (7-14 days ago)
            current_period = self._get_jobs_count_in_period(user_id, org_id, 7)
            previous_period = self._get_jobs_count_in_period(user_id, org_id, 14, 7)
            
            if previous_period == 0:
                return 0.0
            
            change = ((current_period - previous_period) / previous_period) * 100
            return round(change, 2)
            
        except Exception as e:
            logger.error(f"Failed to calculate processing volume trend: {e}")
            return 0.0
    
    def _calculate_error_rate(self, user_id: str, org_id: str = None) -> float:
        """
        Calculate error rate for the user.
        
        User can see:
        - Their own error rates (user_id)
        - Organization error rates (org_id)
        """
        try:
            total_jobs = self._get_total_jobs_count(user_id, org_id)
            if total_jobs == 0:
                return 0.0
            
            failed_jobs = self._get_failed_jobs_count(user_id, org_id)
            return (failed_jobs / total_jobs) * 100
            
        except Exception as e:
            logger.error(f"Failed to calculate error rate: {e}")
            return 0.0
    
    def _calculate_avg_processing_time(self, user_id: str, org_id: str = None, days: int = 30) -> float:
        """
        Calculate average processing time for the user.
        
        User can see:
        - Their own processing times (user_id)
        - Organization processing times (org_id)
        """
        query = """
            SELECT AVG(processing_time) FROM aasx_processing 
            WHERE processing_status = 'completed' 
            AND processing_time IS NOT NULL
            AND timestamp >= datetime('now', '-{} days')
        """.format(days)
        
        params = []
        if user_id:
            query += " AND processed_by = ?"
            params.append(user_id)
        elif org_id:
            query += " AND org_id = ?"
            params.append(org_id)
        
        result = self.db.execute_query(query, params)
        return result[0][0] if result and result[0][0] else 0.0
    
    def _calculate_processing_efficiency_score(self, user_id: str, org_id: str = None, days: int = 30) -> float:
        """
        Calculate processing efficiency score for the user.
        
        User can see:
        - Their own efficiency scores (user_id)
        - Organization efficiency scores (org_id)
        """
        query = """
            SELECT AVG(m.processing_efficiency_score) FROM aasx_processing_metrics m
            JOIN aasx_processing p ON m.job_id = p.job_id 
            WHERE p.processing_status = 'completed'
            AND m.processing_efficiency_score IS NOT NULL
            AND m.timestamp >= datetime('now', '-{} days')
        """.format(days)
        
        params = []
        if user_id:
            query += " AND p.processed_by = ?"
            params.append(user_id)
        elif org_id:
            query += " AND p.org_id = ?"
            params.append(org_id)
        
        result = self.db.execute_query(query, params)
        return result[0][0] if result and result[0][0] else 0.0
    
    def _calculate_quality_score_trend(self, user_id: str, org_id: str = None, days: int = 30) -> float:
        """
        Calculate quality score trend for the user.
        
        User can see:
        - Their own quality trends (user_id)
        - Organization quality trends (org_id)
        """
        try:
            # Get current period vs previous period quality scores
            current_quality = self._get_avg_quality_score_in_period(user_id, org_id, 7)
            previous_quality = self._get_avg_quality_score_in_period(user_id, org_id, 14, 7)
            
            if previous_quality == 0:
                return 0.0
            
            change = ((current_quality - previous_quality) / previous_quality) * 100
            return round(change, 2)
            
        except Exception as e:
            logger.error(f"Failed to calculate quality score trend: {e}")
            return 0.0
    
    def _calculate_resource_utilization_trend(self, user_id: str, org_id: str = None, days: int = 30) -> float:
        """
        Calculate resource utilization trend for the user.
        
        User can see:
        - Their own resource trends (user_id)
        - Organization resource trends (org_id)
        """
        try:
            # Get current period vs previous period resource efficiency
            current_efficiency = self._get_avg_resource_efficiency_in_period(user_id, org_id, 7)
            previous_efficiency = self._get_avg_resource_efficiency_in_period(user_id, org_id, 14, 7)
            
            if previous_efficiency == 0:
                return 0.0
            
            change = ((current_efficiency - previous_efficiency) / previous_efficiency) * 100
            return round(change, 2)
            
        except Exception as e:
            logger.error(f"Failed to calculate resource utilization trend: {e}")
            return 0.0
    
    # Additional helper methods for trends and analytics with USER-BASED filtering
    
    def _get_total_jobs_count(self, user_id: str, org_id: str = None) -> int:
        """
        Get total jobs count for the user.
        
        User can see:
        - Their own jobs (user_id)
        - Organization jobs (org_id)
        """
        query = "SELECT COUNT(*) FROM aasx_processing"
        params = []
        
        if user_id:
            query += " WHERE processed_by = ?"
            params.append(user_id)
        elif org_id:
            query += " WHERE org_id = ?"
            params.append(org_id)
        
        result = self.db.execute_query(query, params)
        return result[0][0] if result else 0
    
    def _get_successful_jobs_count(self, user_id: str, org_id: str = None) -> int:
        """
        Get successful jobs count for the user.
        
        User can see:
        - Their own successful jobs (user_id)
        - Organization successful jobs (org_id)
        """
        query = "SELECT COUNT(*) FROM aasx_processing WHERE processing_status = 'completed'"
        params = []
        
        if user_id:
            query += " AND processed_by = ?"
            params.append(user_id)
        elif org_id:
            query += " AND org_id = ?"
            params.append(org_id)
        
        result = self.db.execute_query(query, params)
        return result[0][0] if result else 0
    
    def _get_failed_jobs_count(self, user_id: str, org_id: str = None) -> int:
        """
        Get failed jobs count for the user.
        
        User can see:
        - Their own failed jobs (user_id)
        - Organization failed jobs (org_id)
        """
        query = "SELECT COUNT(*) FROM aasx_processing WHERE processing_status = 'failed'"
        params = []
        
        if user_id:
            query += " AND processed_by = ?"
            params.append(user_id)
        elif org_id:
            query += " AND org_id = ?"
            params.append(org_id)
        
        result = self.db.execute_query(query, params)
        return result[0][0] if result else 0
    
    def _get_jobs_count_in_period(self, user_id: str, org_id: str = None, days: int = 7, offset: int = 0) -> int:
        """
        Get jobs count in a specific time period for the user.
        
        User can see:
        - Their own jobs in period (user_id)
        - Organization jobs in period (org_id)
        """
        query = """
            SELECT COUNT(*) FROM aasx_processing 
            WHERE timestamp >= datetime('now', '-{} days')
            AND timestamp < datetime('now', '-{} days')
        """.format(days + offset, offset)
        
        params = []
        if user_id:
            query += " AND processed_by = ?"
            params.append(user_id)
        elif org_id:
            query += " AND org_id = ?"
            params.append(org_id)
        
        result = self.db.execute_query(query, params)
        return result[0][0] if result else 0
    
    def _get_avg_quality_score_in_period(self, user_id: str, org_id: str = None, days: int = 7, offset: int = 0) -> float:
        """
        Get average quality score in a specific time period for the user.
        
        User can see:
        - Their own quality scores in period (user_id)
        - Organization quality scores in period (org_id)
        """
        query = """
            SELECT AVG(data_quality_score) FROM aasx_processing 
            WHERE data_quality_score IS NOT NULL
            AND timestamp >= datetime('now', '-{} days')
            AND timestamp < datetime('now', '-{} days')
        """.format(days + offset, offset)
        
        params = []
        if user_id:
            query += " AND processed_by = ?"
            params.append(user_id)
        elif org_id:
            query += " AND org_id = ?"
            params.append(org_id)
        
        result = self.db.execute_query(query, params)
        return result[0][0] if result and result[0][0] else 0.0
    
    def _get_avg_resource_efficiency_in_period(self, user_id: str, org_id: str = None, days: int = 7, offset: int = 0) -> float:
        """
        Get average resource efficiency in a specific time period for the user.
        
        User can see:
        - Their own resource efficiency in period (user_id)
        - Organization resource efficiency in period (org_id)
        """
        query = """
            SELECT AVG(m.processing_efficiency_score) FROM aasx_processing_metrics m
            JOIN aasx_processing p ON m.job_id = p.job_id
            WHERE m.processing_efficiency_score IS NOT NULL
            AND m.timestamp >= datetime('now', '-{} days')
            AND m.timestamp < datetime('now', '-{} days')
        """.format(days + offset, offset)
        
        params = []
        if user_id:
            query += " AND p.processed_by = ?"
            params.append(user_id)
        elif org_id:
            query += " AND p.org_id = ?"
            params.append(org_id)
        
        result = self.db.execute_query(query, params)
        return result[0][0] if result and result[0][0] else 0.0
    
    # Placeholder methods for additional analytics (to be implemented with USER-BASED filtering)
    
    def _get_daily_processing_volume(self, user_id: str, org_id: str = None, days: int = 30) -> List[Dict[str, Any]]:
        """Get daily processing volume data for the user."""
        # TODO: Implement daily processing volume aggregation with user filtering
        return []
    
    def _get_job_type_distribution(self, user_id: str, org_id: str = None, days: int = 30) -> Dict[str, int]:
        """Get job type distribution for the user."""
        # TODO: Implement job type distribution calculation with user filtering
        return {}
    
    def _get_source_type_distribution(self, user_id: str, org_id: str = None, days: int = 30) -> Dict[str, int]:
        """Get source type distribution for the user."""
        # TODO: Implement source type distribution calculation with user filtering
        return {}
    
    def _get_quality_score_trends(self, user_id: str, org_id: str = None, days: int = 30) -> List[Dict[str, Any]]:
        """Get quality score trends over time for the user."""
        # TODO: Implement quality score trends calculation with user filtering
        return []
    
    def _get_processing_time_trends(self, user_id: str, org_id: str = None, days: int = 30) -> List[Dict[str, Any]]:
        """Get processing time trends over time for the user."""
        # TODO: Implement processing time trends calculation with user filtering
        return []
    
    def _calculate_overall_quality_score(self, user_id: str, org_id: str = None, days: int = 30) -> float:
        """Calculate overall quality score for the user."""
        # TODO: Implement overall quality score calculation with user filtering
        return 0.0
    
    def _get_quality_by_job_type(self, user_id: str, org_id: str = None, days: int = 30) -> Dict[str, float]:
        """Get quality scores by job type for the user."""
        # TODO: Implement quality by job type calculation with user filtering
        return {}
    
    def _get_quality_trends(self, user_id: str, org_id: str = None, days: int = 30) -> List[Dict[str, Any]]:
        """Get quality trends over time for the user."""
        # TODO: Implement quality trends calculation with user filtering
        return []
    
    def _get_validation_results_summary(self, user_id: str, org_id: str = None, days: int = 30) -> Dict[str, Any]:
        """Get validation results summary for the user."""
        # TODO: Implement validation results summary with user filtering
        return {}
    
    def _analyze_upload_patterns(self, user_id: str, org_id: str = None, days: int = 30) -> Dict[str, Any]:
        """Analyze upload patterns for the user."""
        # TODO: Implement upload patterns analysis with user filtering
        return {}
    
    def _analyze_processing_patterns(self, user_id: str, org_id: str = None, days: int = 30) -> Dict[str, Any]:
        """Analyze processing patterns for the user."""
        # TODO: Implement processing patterns analysis with user filtering
        return {}
    
    def _get_session_analytics(self, user_id: str, org_id: str = None, days: int = 30) -> Dict[str, Any]:
        """Get session analytics for the user."""
        # TODO: Implement session analytics with user filtering
        return {}
    
    def _calculate_user_efficiency(self, user_id: str, org_id: str = None, days: int = 30) -> float:
        """Calculate user efficiency score for the user."""
        # TODO: Implement user efficiency calculation with user filtering
        return 0.0
