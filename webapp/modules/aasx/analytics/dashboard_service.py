"""
Dashboard Service for AASX-ETL

This service provides specific dashboard data and metrics
for the main dashboard view. It focuses on overview metrics,
quick insights, and dashboard-specific data aggregation.

IMPORTANT: This is a USER-BASED FRAMEWORK
- All data must be filtered by user_id or org_id
- Users can only access their own data or organization data
- Authentication context is required for all operations

Phase 5.1: Analytics API Backend
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DashboardService:
    """Service for dashboard-specific data and metrics."""
    
    def __init__(self, db_connection):
        self.db = db_connection
        logger.info("DashboardService initialized for user-based framework")
    
    def get_dashboard_overview(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get complete dashboard overview data for the authenticated user.
        
        Args:
            user_context: Dictionary containing user authentication context
                - user_id: The authenticated user's ID
                - organization_id: The user's organization ID
                - role: User's role in the system
        
        Returns:
            Dictionary with user-specific dashboard overview data
        """
        try:
            # Extract user context - REQUIRED for user-based framework
            user_id = user_context.get('user_id')
            org_id = user_context.get('organization_id')
            
            if not user_id:
                logger.error("User ID is required for dashboard in user-based framework")
                raise ValueError("User authentication required")
            
            logger.info(f"Getting dashboard overview for user: {user_id}, org: {org_id}")
            
            overview = {
                'summary_cards': self._get_summary_cards(user_id, org_id),
                'recent_activity': self._get_recent_activity(user_id, org_id),
                'quick_stats': self._get_quick_stats(user_id, org_id),
                'performance_indicators': self._get_performance_indicators(user_id, org_id)
            }
            return overview
            
        except Exception as e:
            logger.error(f"Failed to get dashboard overview: {e}")
            return self._get_default_dashboard_data()
    
    def get_dashboard_summary_cards(self, user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get summary cards data for dashboard for the authenticated user.
        
        Args:
            user_context: Dictionary containing user authentication context
        
        Returns:
            List of summary card data for the user
        """
        try:
            # Extract user context - REQUIRED for user-based framework
            user_id = user_context.get('user_id')
            org_id = user_context.get('organization_id')
            
            if not user_id:
                logger.error("User ID is required for dashboard summary in user-based framework")
                raise ValueError("User authentication required")
            
            logger.info(f"Getting dashboard summary cards for user: {user_id}, org: {org_id}")
            
            cards = [
                {
                    'title': 'Total Projects',
                    'value': self._get_total_projects(user_id, org_id),
                    'icon': 'fas fa-project-diagram',
                    'color': 'primary',
                    'trend': self._get_projects_trend(user_id, org_id)
                },
                {
                    'title': 'Total Files',
                    'value': self._get_total_files(user_id, org_id),
                    'icon': 'fas fa-file-alt',
                    'color': 'info',
                    'trend': self._get_files_trend(user_id, org_id)
                },
                {
                    'title': 'Processed Files',
                    'value': self._get_processed_files_count(user_id, org_id),
                    'icon': 'fas fa-check-circle',
                    'color': 'success',
                    'trend': self._get_processed_files_trend(user_id, org_id)
                },
                {
                    'title': 'Success Rate',
                    'value': f"{self._get_success_rate(user_id, org_id):.1f}%",
                    'icon': 'fas fa-chart-line',
                    'color': 'warning',
                    'trend': self._get_success_rate_trend(user_id, org_id)
                }
            ]
            return cards
            
        except Exception as e:
            logger.error(f"Failed to get summary cards: {e}")
            return self._get_default_summary_cards()
    
    def get_recent_processing_jobs(self, user_context: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent processing jobs for dashboard for the authenticated user.
        
        Args:
            user_context: Dictionary containing user authentication context
            limit: Maximum number of recent jobs to return
        
        Returns:
            List of recent processing jobs for the user
        """
        try:
            # Extract user context - REQUIRED for user-based framework
            user_id = user_context.get('user_id')
            org_id = user_context.get('organization_id')
            
            if not user_id:
                logger.error("User ID is required for recent jobs in user-based framework")
                raise ValueError("User authentication required")
            
            logger.info(f"Getting recent processing jobs for user: {user_id}, org: {org_id}, limit: {limit}")
            
            query = """
                SELECT 
                    p.id,
                    p.job_type,
                    p.processing_status,
                    p.timestamp,
                    p.processing_time,
                    p.data_quality_score,
                    f.filename,
                    pr.name as project_name
                FROM aasx_processing p
                JOIN files f ON p.file_id = f.file_id
                JOIN projects pr ON p.project_id = pr.project_id
                WHERE p.processing_status IN ('completed', 'failed', 'processing')
            """
            
            params = []
            if user_id:
                # User can see their own processing jobs
                query += " AND p.processed_by = ?"
                params.append(user_id)
            elif org_id:
                # User can see processing jobs in their organization
                query += " AND p.org_id = ?"
                params.append(org_id)
            
            query += " ORDER BY p.timestamp DESC LIMIT ?"
            params.append(limit)
            
            results = self.db.execute_query(query, params)
            
            jobs = []
            for row in results:
                job = {
                    'id': row[0],
                    'job_type': row[1],
                    'status': row[2],
                    'timestamp': row[3],
                    'processing_time': row[4],
                    'quality_score': row[5],
                    'filename': row[6],
                    'project_name': row[7]
                }
                jobs.append(job)
            
            return jobs
            
        except Exception as e:
            logger.error(f"Failed to get recent processing jobs: {e}")
            return []
    
    def get_processing_volume_chart_data(self, user_context: Dict[str, Any], days: int = 7) -> Dict[str, Any]:
        """
        Get processing volume chart data for dashboard for the authenticated user.
        
        Args:
            user_context: Dictionary containing user authentication context
            days: Number of days to look back for chart data
        
        Returns:
            Dictionary with chart data for the user
        """
        try:
            # Extract user context - REQUIRED for user-based framework
            user_id = user_context.get('user_id')
            org_id = user_context.get('organization_id')
            
            if not user_id:
                logger.error("User ID is required for chart data in user-based framework")
                raise ValueError("User authentication required")
            
            logger.info(f"Getting processing volume chart data for user: {user_id}, org: {org_id}, days: {days}")
            
            # Get daily processing counts for the last N days
            query = """
                SELECT 
                    DATE(p.timestamp) as date,
                    COUNT(*) as job_count,
                    SUM(CASE WHEN p.processing_status = 'completed' THEN 1 ELSE 0 END) as completed_count,
                    SUM(CASE WHEN p.processing_status = 'failed' THEN 1 ELSE 0 END) as failed_count
                FROM aasx_processing p
                WHERE p.timestamp >= datetime('now', '-{} days')
            """.format(days)
            
            params = []
            if user_id:
                # User can see their own processing volume
                query += " AND p.processed_by = ?"
                params.append(user_id)
            elif org_id:
                # User can see processing volume in their organization
                query += " AND p.org_id = ?"
                params.append(org_id)
            
            query += " GROUP BY DATE(p.timestamp) ORDER BY date"
            
            results = self.db.execute_query(query, params)
            
            chart_data = {
                'labels': [],
                'datasets': [
                    {
                        'label': 'Total Jobs',
                        'data': [],
                        'borderColor': '#007bff',
                        'backgroundColor': 'rgba(0, 123, 255, 0.1)'
                    },
                    {
                        'label': 'Completed',
                        'data': [],
                        'borderColor': '#28a745',
                        'backgroundColor': 'rgba(40, 167, 69, 0.1)'
                    },
                    {
                        'label': 'Failed',
                        'data': [],
                        'borderColor': '#dc3545',
                        'backgroundColor': 'rgba(220, 53, 69, 0.1)'
                    }
                ]
            }
            
            for row in results:
                chart_data['labels'].append(row[0])
                chart_data['datasets'][0]['data'].append(row[1])
                chart_data['datasets'][1]['data'].append(row[2])
                chart_data['datasets'][2]['data'].append(row[3])
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Failed to get processing volume chart data: {e}")
            return self._get_default_chart_data()
    
    def get_job_type_distribution(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get job type distribution for dashboard pie chart for the authenticated user.
        
        Args:
            user_context: Dictionary containing user authentication context
        
        Returns:
            Dictionary with job type distribution data for the user
        """
        try:
            # Extract user context - REQUIRED for user-based framework
            user_id = user_context.get('user_id')
            org_id = user_context.get('organization_id')
            
            if not user_id:
                logger.error("User ID is required for job distribution in user-based framework")
                raise ValueError("User authentication required")
            
            logger.info(f"Getting job type distribution for user: {user_id}, org: {org_id}")
            
            query = """
                SELECT 
                    job_type,
                    COUNT(*) as count
                FROM aasx_processing
                WHERE processing_status = 'completed'
            """
            
            params = []
            if user_id:
                # User can see their own job type distribution
                query += " AND processed_by = ?"
                params.append(user_id)
            elif org_id:
                # User can see job type distribution in their organization
                query += " AND org_id = ?"
                params.append(org_id)
            
            query += " GROUP BY job_type"
            
            results = self.db.execute_query(query, params)
            
            distribution = {
                'labels': [],
                'data': [],
                'colors': ['#007bff', '#28a745', '#ffc107', '#dc3545']
            }
            
            for row in results:
                distribution['labels'].append(row[0].title())
                distribution['data'].append(row[1])
            
            return distribution
            
        except Exception as e:
            logger.error(f"Failed to get job type distribution: {e}")
            return {
                'labels': ['Extraction', 'Generation'],
                'data': [0, 0],
                'colors': ['#007bff', '#28a745']
            }
    
    # Private helper methods with USER-BASED filtering
    
    def _get_summary_cards(self, user_id: str, org_id: str = None) -> List[Dict[str, Any]]:
        """Get summary cards data for the user."""
        return self.get_dashboard_summary_cards({'user_id': user_id, 'organization_id': org_id})
    
    def _get_recent_activity(self, user_id: str, org_id: str = None) -> List[Dict[str, Any]]:
        """Get recent activity data for the user."""
        return self.get_recent_processing_jobs({'user_id': user_id, 'organization_id': org_id}, 5)
    
    def _get_quick_stats(self, user_id: str, org_id: str = None) -> Dict[str, Any]:
        """
        Get quick statistics for the user.
        
        User can see:
        - Their own processing statistics (user_id)
        - Organization processing statistics (org_id)
        """
        try:
            stats = {
                'avg_processing_time': self._get_avg_processing_time(user_id, org_id),
                'total_jobs_today': self._get_jobs_count_today(user_id, org_id),
                'quality_score_avg': self._get_avg_quality_score(user_id, org_id),
                'efficiency_score': self._get_avg_efficiency_score(user_id, org_id)
            }
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get quick stats: {e}")
            return {
                'avg_processing_time': 0.0,
                'total_jobs_today': 0,
                'quality_score_avg': 0.0,
                'efficiency_score': 0.0
            }
    
    def _get_performance_indicators(self, user_id: str, org_id: str = None) -> Dict[str, Any]:
        """
        Get performance indicators for the user.
        
        User can see:
        - Their own performance indicators (user_id)
        - Organization performance indicators (org_id)
        """
        try:
            indicators = {
                'success_rate_trend': self._get_success_rate_trend(user_id, org_id),
                'processing_volume_trend': self._get_processing_volume_trend(user_id, org_id),
                'quality_trend': self._get_quality_trend(user_id, org_id),
                'efficiency_trend': self._get_efficiency_trend(user_id, org_id)
            }
            return indicators
            
        except Exception as e:
            logger.error(f"Failed to get performance indicators: {e}")
            return {
                'success_rate_trend': 0.0,
                'processing_volume_trend': 0.0,
                'quality_trend': 0.0,
                'efficiency_trend': 0.0
            }
    
    def _get_total_projects(self, user_id: str, org_id: str = None) -> int:
        """
        Get total projects count for the user.
        
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
        Get total files count for the user.
        
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
        Get processed files count for the user.
        
        User can see:
        - Their own processed files (user_id)
        - Organization processed files (org_id)
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
    
    def _get_success_rate(self, user_id: str, org_id: str = None) -> float:
        """
        Calculate success rate for the user.
        
        User can see:
        - Their own success rates (user_id)
        - Organization success rates (org_id)
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
    
    def _get_projects_trend(self, user_id: str, org_id: str = None) -> float:
        """Get projects trend percentage for the user."""
        # TODO: Implement projects trend calculation with user filtering
        return 0.0
    
    def _get_files_trend(self, user_id: str, org_id: str = None) -> float:
        """Get files trend percentage for the user."""
        # TODO: Implement files trend calculation with user filtering
        return 0.0
    
    def _get_processed_files_trend(self, user_id: str, org_id: str = None) -> float:
        """Get processed files trend percentage for the user."""
        # TODO: Implement processed files trend calculation with user filtering
        return 0.0
    
    def _get_success_rate_trend(self, user_id: str, org_id: str = None) -> float:
        """Get success rate trend percentage for the user."""
        # TODO: Implement success rate trend calculation with user filtering
        return 0.0
    
    def _get_avg_processing_time(self, user_id: str, org_id: str = None) -> float:
        """
        Get average processing time for the user.
        
        User can see:
        - Their own processing times (user_id)
        - Organization processing times (org_id)
        """
        query = """
            SELECT AVG(processing_time) FROM aasx_processing 
            WHERE processing_status = 'completed' 
            AND processing_time IS NOT NULL
            AND timestamp >= datetime('now', '-7 days')
        """
        
        params = []
        if user_id:
            query += " AND processed_by = ?"
            params.append(user_id)
        elif org_id:
            query += " AND org_id = ?"
            params.append(org_id)
        
        result = self.db.execute_query(query, params)
        return result[0][0] if result and result[0][0] else 0.0
    
    def _get_jobs_count_today(self, user_id: str, org_id: str = None) -> int:
        """
        Get jobs count for today for the user.
        
        User can see:
        - Their own jobs today (user_id)
        - Organization jobs today (org_id)
        """
        query = """
            SELECT COUNT(*) FROM aasx_processing 
            WHERE DATE(timestamp) = DATE('now')
        """
        
        params = []
        if user_id:
            query += " AND processed_by = ?"
            params.append(user_id)
        elif org_id:
            query += " AND org_id = ?"
            params.append(org_id)
        
        result = self.db.execute_query(query, params)
        return result[0][0] if result else 0
    
    def _get_avg_quality_score(self, user_id: str, org_id: str = None) -> float:
        """
        Get average quality score for the user.
        
        User can see:
        - Their own quality scores (user_id)
        - Organization quality scores (org_id)
        """
        query = """
            SELECT AVG(data_quality_score) FROM aasx_processing 
            WHERE data_quality_score IS NOT NULL
            AND timestamp >= datetime('now', '-7 days')
        """
        
        params = []
        if user_id:
            query += " AND processed_by = ?"
            params.append(user_id)
        elif org_id:
            query += " AND org_id = ?"
            params.append(org_id)
        
        result = self.db.execute_query(query, params)
        return result[0][0] if result and result[0][0] else 0.0
    
    def _get_avg_efficiency_score(self, user_id: str, org_id: str = None) -> float:
        """
        Get average efficiency score for the user.
        
        User can see:
        - Their own efficiency scores (user_id)
        - Organization efficiency scores (org_id)
        """
        query = """
            SELECT AVG(m.processing_efficiency_score) FROM aasx_processing_metrics m
            JOIN aasx_processing p ON m.job_id = p.id
            WHERE m.processing_efficiency_score IS NOT NULL
            AND m.timestamp >= datetime('now', '-7 days')
        """
        
        params = []
        if user_id:
            query += " AND p.processed_by = ?"
            params.append(user_id)
        elif org_id:
            query += " AND p.org_id = ?"
            params.append(org_id)
        
        result = self.db.execute_query(query, params)
        return result[0][0] if result and result[0][0] else 0.0
    
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
            query += " AND org_id = ?"
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
    
    def _get_processing_volume_trend(self, user_id: str, org_id: str = None) -> float:
        """Get processing volume trend for the user."""
        # TODO: Implement processing volume trend calculation with user filtering
        return 0.0
    
    def _get_quality_trend(self, user_id: str, org_id: str = None) -> float:
        """Get quality trend for the user."""
        # TODO: Implement quality trend calculation with user filtering
        return 0.0
    
    def _get_efficiency_trend(self, user_id: str, org_id: str = None) -> float:
        """Get efficiency trend for the user."""
        # TODO: Implement efficiency trend calculation with user filtering
        return 0.0
    
    def _get_default_dashboard_data(self) -> Dict[str, Any]:
        """Get default dashboard data on error."""
        return {
            'summary_cards': self._get_default_summary_cards(),
            'recent_activity': [],
            'quick_stats': {
                'avg_processing_time': 0.0,
                'total_jobs_today': 0,
                'quality_score_avg': 0.0,
                'efficiency_score': 0.0
            },
            'performance_indicators': {
                'success_rate_trend': 0.0,
                'processing_volume_trend': 0.0,
                'quality_trend': 0.0,
                'efficiency_trend': 0.0
            }
        }
    
    def _get_default_summary_cards(self) -> List[Dict[str, Any]]:
        """Get default summary cards on error."""
        return [
            {
                'title': 'Total Projects',
                'value': 0,
                'icon': 'fas fa-project-diagram',
                'color': 'primary',
                'trend': 0.0
            },
            {
                'title': 'Total Files',
                'value': 0,
                'icon': 'fas fa-file-alt',
                'color': 'info',
                'trend': 0.0
            },
            {
                'title': 'Processed Files',
                'value': 0,
                'icon': 'fas fa-check-circle',
                'color': 'success',
                'trend': 0.0
            },
            {
                'title': 'Success Rate',
                'value': '0.0%',
                'icon': 'fas fa-chart-line',
                'color': 'warning',
                'trend': 0.0
            }
        ]
    
    def _get_default_chart_data(self) -> Dict[str, Any]:
        """Get default chart data on error."""
        return {
            'labels': [],
            'datasets': [
                {
                    'label': 'Total Jobs',
                    'data': [],
                    'borderColor': '#007bff',
                    'backgroundColor': 'rgba(0, 123, 255, 0.1)'
                },
                {
                    'label': 'Completed',
                    'data': [],
                    'borderColor': '#28a745',
                    'backgroundColor': 'rgba(40, 167, 69, 0.1)'
                },
                {
                    'label': 'Failed',
                    'data': [],
                    'borderColor': '#dc3545',
                    'backgroundColor': 'rgba(220, 53, 69, 0.1)'
                }
            ]
        }
