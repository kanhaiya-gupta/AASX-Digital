"""
Chart Data Service for AASX-ETL

This service provides specific chart data and visualization data
for the analytics dashboard. It focuses on chart formatting,
data aggregation for charts, and chart-specific data preparation.

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


class ChartDataService:
    """Service for chart-specific data and visualization."""
    
    def __init__(self, db_connection):
        self.db = db_connection
        logger.info("ChartDataService initialized for user-based framework")
    
    def get_processing_trends_chart(self, user_context: Dict[str, Any], days: int = 30) -> Dict[str, Any]:
        """
        Get processing trends chart data for the authenticated user.
        
        Args:
            user_context: Dictionary containing user authentication context
            days: Number of days to look back for trends
        
        Returns:
            Dictionary with chart data for processing trends
        """
        try:
            # Extract user context - REQUIRED for user-based framework
            user_id = user_context.get('user_id')
            org_id = user_context.get('organization_id')
            
            if not user_id:
                logger.error("User ID is required for chart data in user-based framework")
                raise ValueError("User authentication required")
            
            logger.info(f"Getting processing trends chart for user: {user_id}, org: {org_id}, days: {days}")
            
            # Get daily processing data
            daily_data = self._get_daily_processing_data(user_id, org_id, days)
            
            # Get job type distribution
            job_type_data = self._get_job_type_distribution_data(user_id, org_id, days)
            
            # Get source type distribution
            source_type_data = self._get_source_type_distribution_data(user_id, org_id, days)
            
            chart_data = {
                'daily_trends': daily_data,
                'job_type_distribution': job_type_data,
                'source_type_distribution': source_type_data
            }
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Failed to get processing trends chart: {e}")
            return self._get_default_trends_chart()
    
    def get_quality_metrics_chart(self, user_context: Dict[str, Any], days: int = 30) -> Dict[str, Any]:
        """
        Get quality metrics chart data for the authenticated user.
        
        Args:
            user_context: Dictionary containing user authentication context
            days: Number of days to look back for metrics
        
        Returns:
            Dictionary with chart data for quality metrics
        """
        try:
            # Extract user context - REQUIRED for user-based framework
            user_id = user_context.get('user_id')
            org_id = user_context.get('organization_id')
            
            if not user_id:
                logger.error("User ID is required for quality chart data in user-based framework")
                raise ValueError("User authentication required")
            
            logger.info(f"Getting quality metrics chart for user: {user_id}, org: {org_id}, days: {days}")
            
            # Get quality score trends
            quality_trends = self._get_quality_score_trends(user_id, org_id, days)
            
            # Get quality by job type
            quality_by_job_type = self._get_quality_by_job_type_data(user_id, org_id, days)
            
            # Get validation results
            validation_results = self._get_validation_results_data(user_id, org_id, days)
            
            chart_data = {
                'quality_trends': quality_trends,
                'quality_by_job_type': quality_by_job_type,
                'validation_results': validation_results
            }
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Failed to get quality metrics chart: {e}")
            return self._get_default_quality_chart()
    
    def get_performance_metrics_chart(self, user_context: Dict[str, Any], days: int = 30) -> Dict[str, Any]:
        """
        Get performance metrics chart data for the authenticated user.
        
        Args:
            user_context: Dictionary containing user authentication context
            days: Number of days to look back for metrics
        
        Returns:
            Dictionary with chart data for performance metrics
        """
        try:
            # Extract user context - REQUIRED for user-based framework
            user_id = user_context.get('user_id')
            org_id = user_context.get('organization_id')
            
            if not user_id:
                logger.error("User ID is required for performance chart data in user-based framework")
                raise ValueError("User authentication required")
            
            logger.info(f"Getting performance metrics chart for user: {user_id}, org: {org_id}, days: {days}")
            
            # Get processing time trends
            processing_time_trends = self._get_processing_time_trends(user_id, org_id, days)
            
            # Get efficiency trends
            efficiency_trends = self._get_efficiency_trends(user_id, org_id, days)
            
            # Get resource utilization
            resource_utilization = self._get_resource_utilization_data(user_id, org_id, days)
            
            chart_data = {
                'processing_time_trends': processing_time_trends,
                'efficiency_trends': efficiency_trends,
                'resource_utilization': resource_utilization
            }
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics chart: {e}")
            return self._get_default_performance_chart()
    
    def get_user_behavior_chart(self, user_context: Dict[str, Any], days: int = 30) -> Dict[str, Any]:
        """
        Get user behavior chart data for the authenticated user.
        
        Args:
            user_context: Dictionary containing user authentication context
            days: Number of days to look back for behavior data
        
        Returns:
            Dictionary with chart data for user behavior
        """
        try:
            # Extract user context - REQUIRED for user-based framework
            user_id = user_context.get('user_id')
            org_id = user_context.get('organization_id')
            
            if not user_id:
                logger.error("User ID is required for behavior chart data in user-based framework")
                raise ValueError("User authentication required")
            
            logger.info(f"Getting user behavior chart for user: {user_id}, org: {org_id}, days: {days}")
            
            # Get upload patterns
            upload_patterns = self._get_upload_patterns_data(user_id, org_id, days)
            
            # Get processing patterns
            processing_patterns = self._get_processing_patterns_data(user_id, org_id, days)
            
            # Get session analytics
            session_analytics = self._get_session_analytics_data(user_id, org_id, days)
            
            chart_data = {
                'upload_patterns': upload_patterns,
                'processing_patterns': processing_patterns,
                'session_analytics': session_analytics
            }
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Failed to get user behavior chart: {e}")
            return self._get_default_behavior_chart()
    
    # Private helper methods for chart data with USER-BASED filtering
    
    def _get_daily_processing_data(self, user_id: str, org_id: str = None, days: int = 30) -> Dict[str, Any]:
        """
        Get daily processing data for charts for the user.
        
        User can see:
        - Their own daily processing data (user_id)
        - Organization daily processing data (org_id)
        """
        try:
            query = """
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(*) as total_jobs,
                    SUM(CASE WHEN processing_status = 'completed' THEN 1 ELSE 0 END) as completed_jobs,
                    SUM(CASE WHEN processing_status = 'failed' THEN 1 ELSE 0 END) as failed_jobs,
                    AVG(processing_time) as avg_processing_time
                FROM aasx_processing
                WHERE timestamp >= datetime('now', '-{} days')
            """.format(days)
            
            params = []
            if user_id:
                query += " AND processed_by = ?"
                params.append(user_id)
            elif org_id:
                query += " AND org_id = ?"
                params.append(org_id)
            
            query += " GROUP BY DATE(timestamp) ORDER BY date"
            
            results = self.db.execute_query(query, params)
            
            chart_data = {
                'labels': [],
                'datasets': [
                    {
                        'label': 'Total Jobs',
                        'data': [],
                        'borderColor': '#007bff',
                        'backgroundColor': 'rgba(0, 123, 255, 0.1)',
                        'type': 'line'
                    },
                    {
                        'label': 'Completed',
                        'data': [],
                        'borderColor': '#28a745',
                        'backgroundColor': 'rgba(40, 167, 69, 0.1)',
                        'type': 'bar'
                    },
                    {
                        'label': 'Failed',
                        'data': [],
                        'borderColor': '#dc3545',
                        'backgroundColor': 'rgba(220, 53, 69, 0.1)',
                        'type': 'bar'
                    }
                ]
            }
            
            for row in results:
                chart_data['labels'].append(row['date'])
                chart_data['datasets'][0]['data'].append(row['total_jobs'])
                chart_data['datasets'][1]['data'].append(row['completed_jobs'])
                chart_data['datasets'][2]['data'].append(row['failed_jobs'])
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Failed to get daily processing data: {e}")
            return self._get_default_line_chart()
    
    def _get_job_type_distribution_data(self, user_id: str, org_id: str = None, days: int = 30) -> Dict[str, Any]:
        """
        Get job type distribution data for charts for the user.
        
        User can see:
        - Their own job type distribution (user_id)
        - Organization job type distribution (org_id)
        """
        try:
            query = """
                SELECT 
                    job_type,
                    COUNT(*) as count,
                    AVG(data_quality_score) as avg_quality
                FROM aasx_processing
                WHERE processing_status = 'completed'
                AND timestamp >= datetime('now', '-{} days')
            """.format(days)
            
            params = []
            if user_id:
                query += " AND processed_by = ?"
                params.append(user_id)
            elif org_id:
                query += " AND org_id = ?"
                params.append(org_id)
            
            query += " GROUP BY job_type"
            
            results = self.db.execute_query(query, params)
            
            chart_data = {
                'labels': [],
                'data': [],
                'quality_data': [],
                'colors': ['#007bff', '#28a745', '#ffc107', '#dc3545', '#6f42c1']
            }
            
            for row in results:
                chart_data['labels'].append(row['job_type'].title())
                chart_data['data'].append(row['count'])
                chart_data['quality_data'].append(row['avg_quality'] if row['avg_quality'] else 0.0)
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Failed to get job type distribution data: {e}")
            return {
                'labels': ['Extraction', 'Generation'],
                'data': [0, 0],
                'quality_data': [0.0, 0.0],
                'colors': ['#007bff', '#28a745']
            }
    
    def _get_source_type_distribution_data(self, user_id: str, org_id: str = None, days: int = 30) -> Dict[str, Any]:
        """
        Get source type distribution data for charts for the user.
        
        User can see:
        - Their own source type distribution (user_id)
        - Organization source type distribution (org_id)
        """
        try:
            query = """
                SELECT 
                    source_type,
                    COUNT(*) as count
                FROM aasx_processing
                WHERE processing_status = 'completed'
                AND timestamp >= datetime('now', '-{} days')
            """.format(days)
            
            params = []
            if user_id:
                query += " AND processed_by = ?"
                params.append(user_id)
            elif org_id:
                query += " AND org_id = ?"
                params.append(org_id)
            
            query += " GROUP BY source_type"
            
            results = self.db.execute_query(query, params)
            
            chart_data = {
                'labels': [],
                'data': [],
                'colors': ['#007bff', '#28a745', '#ffc107', '#dc3545']
            }
            
            for row in results:
                chart_data['labels'].append(row['source_type'].replace('_', ' ').title())
                chart_data['data'].append(row['count'])
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Failed to get source type distribution data: {e}")
            return {
                'labels': ['Manual Upload', 'URL Upload'],
                'data': [0, 0],
                'colors': ['#007bff', '#28a745']
            }
    
    def _get_quality_score_trends(self, user_id: str, org_id: str = None, days: int = 30) -> Dict[str, Any]:
        """
        Get quality score trends for charts for the user.
        
        User can see:
        - Their own quality trends (user_id)
        - Organization quality trends (org_id)
        """
        try:
            query = """
                SELECT 
                    DATE(timestamp) as date,
                    AVG(data_quality_score) as avg_quality,
                    COUNT(*) as job_count
                FROM aasx_processing
                WHERE data_quality_score IS NOT NULL
                AND timestamp >= datetime('now', '-{} days')
            """.format(days)
            
            params = []
            if user_id:
                query += " AND processed_by = ?"
                params.append(user_id)
            elif org_id:
                query += " AND org_id = ?"
                params.append(org_id)
            
            query += " GROUP BY DATE(timestamp) ORDER BY date"
            
            results = self.db.execute_query(query, params)
            
            chart_data = {
                'labels': [],
                'datasets': [
                    {
                        'label': 'Average Quality Score',
                        'data': [],
                        'borderColor': '#28a745',
                        'backgroundColor': 'rgba(40, 167, 69, 0.1)',
                        'yAxisID': 'y'
                    },
                    {
                        'label': 'Job Count',
                        'data': [],
                        'borderColor': '#007bff',
                        'backgroundColor': 'rgba(0, 123, 255, 0.1)',
                        'yAxisID': 'y1',
                        'type': 'bar'
                    }
                ]
            }
            
            for row in results:
                chart_data['labels'].append(row['date'])
                chart_data['datasets'][0]['data'].append(row['avg_quality'] if row['avg_quality'] else 0.0)
                chart_data['datasets'][1]['data'].append(row['job_count'])
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Failed to get quality score trends: {e}")
            return self._get_default_line_chart()
    
    def _get_quality_by_job_type_data(self, user_id: str, org_id: str = None, days: int = 30) -> Dict[str, Any]:
        """
        Get quality by job type data for charts for the user.
        
        User can see:
        - Their own quality by job type (user_id)
        - Organization quality by job type (org_id)
        """
        try:
            query = """
                SELECT 
                    job_type,
                    AVG(data_quality_score) as avg_quality,
                    COUNT(*) as job_count
                FROM aasx_processing
                WHERE data_quality_score IS NOT NULL
                AND processing_status = 'completed'
                AND timestamp >= datetime('now', '-{} days')
            """.format(days)
            
            params = []
            if user_id:
                query += " AND processed_by = ?"
                params.append(user_id)
            elif org_id:
                query += " AND org_id = ?"
                params.append(org_id)
            
            query += " GROUP BY job_type"
            
            results = self.db.execute_query(query, params)
            
            chart_data = {
                'labels': [],
                'quality_data': [],
                'job_count_data': [],
                'colors': ['#007bff', '#28a745', '#ffc107', '#dc3545']
            }
            
            for row in results:
                chart_data['labels'].append(row['job_type'].title())
                chart_data['quality_data'].append(row['avg_quality'] if row['avg_quality'] else 0.0)
                chart_data['job_count_data'].append(row['job_count'])
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Failed to get quality by job type data: {e}")
            return {
                'labels': ['Extraction', 'Generation'],
                'quality_data': [0.0, 0.0],
                'job_count_data': [0, 0],
                'colors': ['#007bff', '#28a745']
            }
    
    def _get_validation_results_data(self, user_id: str, org_id: str = None, days: int = 30) -> Dict[str, Any]:
        """
        Get validation results data for charts for the user.
        
        User can see:
        - Their own validation results (user_id)
        - Organization validation results (org_id)
        """
        # TODO: Implement validation results data retrieval
        return {
            'labels': ['Valid', 'Invalid', 'Warning'],
            'data': [0, 0, 0],
            'colors': ['#28a745', '#dc3545', '#ffc107']
        }
    
    def _get_processing_time_trends(self, user_id: str, org_id: str = None, days: int = 30) -> Dict[str, Any]:
        """
        Get processing time trends for charts for the user.
        
        User can see:
        - Their own processing time trends (user_id)
        - Organization processing time trends (org_id)
        """
        try:
            query = """
                SELECT 
                    DATE(timestamp) as date,
                    AVG(processing_time) as avg_time,
                    COUNT(*) as job_count
                FROM aasx_processing
                WHERE processing_time IS NOT NULL
                AND processing_status = 'completed'
                AND timestamp >= datetime('now', '-{} days')
            """.format(days)
            
            params = []
            if user_id:
                query += " AND processed_by = ?"
                params.append(user_id)
            elif org_id:
                query += " AND org_id = ?"
                params.append(org_id)
            
            query += " GROUP BY DATE(timestamp) ORDER BY date"
            
            results = self.db.execute_query(query, params)
            
            chart_data = {
                'labels': [],
                'datasets': [
                    {
                        'label': 'Average Processing Time (seconds)',
                        'data': [],
                        'borderColor': '#ffc107',
                        'backgroundColor': 'rgba(255, 193, 7, 0.1)'
                    }
                ]
            }
            
            for row in results:
                chart_data['labels'].append(row['date'])
                chart_data['datasets'][0]['data'].append(row['avg_time'] if row['avg_time'] else 0.0)
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Failed to get processing time trends: {e}")
            return self._get_default_line_chart()
    
    def _get_efficiency_trends(self, user_id: str, org_id: str = None, days: int = 30) -> Dict[str, Any]:
        """
        Get efficiency trends for charts for the user.
        
        User can see:
        - Their own efficiency trends (user_id)
        - Organization efficiency trends (org_id)
        """
        try:
            query = """
                SELECT 
                    DATE(m.timestamp) as date,
                    AVG(m.processing_efficiency_score) as avg_efficiency,
                    COUNT(*) as job_count
                FROM aasx_processing_metrics m
                JOIN aasx_processing p ON m.job_id = p.job_id
                WHERE m.processing_efficiency_score IS NOT NULL
                AND p.processing_status = 'completed'
                AND m.timestamp >= datetime('now', '-{} days')
            """.format(days)
            
            params = []
            if user_id:
                query += " AND p.processed_by = ?"
                params.append(user_id)
            elif org_id:
                query += " AND p.org_id = ?"
                params.append(org_id)
            
            query += " GROUP BY DATE(m.timestamp) ORDER BY date"
            
            results = self.db.execute_query(query, params)
            
            chart_data = {
                'labels': [],
                'datasets': [
                    {
                        'label': 'Average Efficiency Score',
                        'data': [],
                        'borderColor': '#6f42c1',
                        'backgroundColor': 'rgba(111, 66, 193, 0.1)'
                    }
                ]
            }
            
            for row in results:
                chart_data['labels'].append(row['date'])
                chart_data['datasets'][0]['data'].append(row['avg_efficiency'] if row['avg_efficiency'] else 0.0)
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Failed to get efficiency trends: {e}")
            return self._get_default_line_chart()
    
    def _get_resource_utilization_data(self, user_id: str, org_id: str = None, days: int = 30) -> Dict[str, Any]:
        """
        Get resource utilization data for charts for the user.
        
        User can see:
        - Their own resource utilization (user_id)
        - Organization resource utilization (org_id)
        """
        # TODO: Implement resource utilization data retrieval
        return {
            'labels': ['Memory', 'CPU', 'Disk I/O', 'Network'],
            'data': [0.0, 0.0, 0.0, 0.0],
            'colors': ['#007bff', '#28a745', '#ffc107', '#dc3545']
        }
    
    def _get_upload_patterns_data(self, user_id: str, org_id: str = None, days: int = 30) -> Dict[str, Any]:
        """
        Get upload patterns data for charts for the user.
        
        User can see:
        - Their own upload patterns (user_id)
        - Organization upload patterns (org_id)
        """
        # TODO: Implement upload patterns data retrieval
        return {
            'labels': ['Morning', 'Afternoon', 'Evening', 'Night'],
            'data': [0, 0, 0, 0],
            'colors': ['#007bff', '#28a745', '#ffc107', '#dc3545']
        }
    
    def _get_processing_patterns_data(self, user_id: str, org_id: str = None, days: int = 30) -> Dict[str, Any]:
        """
        Get processing patterns data for charts for the user.
        
        User can see:
        - Their own processing patterns (user_id)
        - Organization processing patterns (org_id)
        """
        # TODO: Implement processing patterns data retrieval
        return {
            'labels': ['Weekday', 'Weekend'],
            'data': [0, 0],
            'colors': ['#007bff', '#28a745']
        }
    
    def _get_session_analytics_data(self, user_id: str, org_id: str = None, days: int = 30) -> Dict[str, Any]:
        """
        Get session analytics data for charts for the user.
        
        User can see:
        - Their own session analytics (user_id)
        - Organization session analytics (org_id)
        """
        # TODO: Implement session analytics data retrieval
        return {
            'labels': ['Short', 'Medium', 'Long'],
            'data': [0, 0, 0],
            'colors': ['#007bff', '#28a745', '#ffc107']
        }
    
    # Default chart data methods
    
    def _get_default_trends_chart(self) -> Dict[str, Any]:
        """Get default trends chart data on error."""
        return {
            'daily_trends': self._get_default_line_chart(),
            'job_type_distribution': {
                'labels': ['Extraction', 'Generation'],
                'data': [0, 0],
                'quality_data': [0.0, 0.0],
                'colors': ['#007bff', '#28a745']
            },
            'source_type_distribution': {
                'labels': ['Manual Upload', 'URL Upload'],
                'data': [0, 0],
                'colors': ['#007bff', '#28a745']
            }
        }
    
    def _get_default_quality_chart(self) -> Dict[str, Any]:
        """Get default quality chart data on error."""
        return {
            'quality_trends': self._get_default_line_chart(),
            'quality_by_job_type': {
                'labels': ['Extraction', 'Generation'],
                'quality_data': [0.0, 0.0],
                'job_count_data': [0, 0],
                'colors': ['#007bff', '#28a745']
            },
            'validation_results': {
                'labels': ['Valid', 'Invalid', 'Warning'],
                'data': [0, 0, 0],
                'colors': ['#28a745', '#dc3545', '#ffc107']
            }
        }
    
    def _get_default_performance_chart(self) -> Dict[str, Any]:
        """Get default performance chart data on error."""
        return {
            'processing_time_trends': self._get_default_line_chart(),
            'efficiency_trends': self._get_default_line_chart(),
            'resource_utilization': {
                'labels': ['Memory', 'CPU', 'Disk I/O', 'Network'],
                'data': [0.0, 0.0, 0.0, 0.0],
                'colors': ['#007bff', '#28a745', '#ffc107', '#dc3545']
            }
        }
    
    def _get_default_behavior_chart(self) -> Dict[str, Any]:
        """Get default behavior chart data on error."""
        return {
            'upload_patterns': {
                'labels': ['Morning', 'Afternoon', 'Evening', 'Night'],
                'data': [0, 0, 0, 0],
                'colors': ['#007bff', '#28a745', '#ffc107', '#dc3545']
            },
            'processing_patterns': {
                'labels': ['Weekday', 'Weekend'],
                'data': [0, 0],
                'colors': ['#007bff', '#28a745']
            },
            'session_analytics': {
                'labels': ['Short', 'Medium', 'Long'],
                'data': [0, 0, 0],
                'colors': ['#007bff', '#28a745', '#ffc107']
            }
        }
    
    def _get_default_line_chart(self) -> Dict[str, Any]:
        """Get default line chart data on error."""
        return {
            'labels': [],
            'datasets': [
                {
                    'label': 'Data',
                    'data': [],
                    'borderColor': '#007bff',
                    'backgroundColor': 'rgba(0, 123, 255, 0.1)'
                }
            ]
        }
