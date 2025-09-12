"""
AASX Metrics Client - Thin Client Wrapper
========================================

Thin client wrapper around src.modules.aasx.services.processing_metrics_service
Provides client-specific interface for AASX metrics and monitoring operations.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

# Import from engine services
from src.modules.aasx.services.aasx_processing_metrics_service import ProcessingMetricsService
from src.engine.database.connection_manager import ConnectionManager

logger = logging.getLogger(__name__)


class AASXMetricsClient:
    """Thin client wrapper for AASX metrics and monitoring operations."""
    
    def __init__(self, connection_manager: ConnectionManager = None):
        """
        Initialize the AASX metrics client.
        
        Args:
            connection_manager: Engine connection manager instance
        """
        self.connection_manager = connection_manager
        self.metrics_service = ProcessingMetricsService(connection_manager) if connection_manager else None
        logger.info("AASX Metrics Client initialized")
    
    async def get_processing_metrics(self, project_id: str = None, 
                                   time_range: str = "24h") -> Dict[str, Any]:
        """
        Get processing metrics for projects.
        
        Args:
            project_id: Optional project ID to filter metrics
            time_range: Time range for metrics (24h, 7d, 30d, 90d)
            
        Returns:
            Dict[str, Any]: Processing metrics data
        """
        try:
            if not self.metrics_service:
                return {'error': 'Metrics service not initialized'}
            
            # Calculate date range based on time_range parameter
            end_date = datetime.utcnow()
            if time_range == "24h":
                start_date = end_date - timedelta(days=1)
            elif time_range == "7d":
                start_date = end_date - timedelta(days=7)
            elif time_range == "30d":
                start_date = end_date - timedelta(days=30)
            elif time_range == "90d":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=1)  # Default to 24h
            
            # Get metrics by date range
            metrics = await self.metrics_service.get_metrics_by_date_range(start_date, end_date)
            
            # Filter by project if specified
            if project_id:
                metrics = [m for m in metrics if m.get('project_id') == project_id]
            
            # Aggregate metrics
            aggregated_metrics = self._aggregate_metrics(metrics)
            
            return {
                'status': 'success',
                'time_range': time_range,
                'project_id': project_id,
                'metrics_count': len(metrics),
                'aggregated_metrics': aggregated_metrics,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get processing metrics: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def get_quality_metrics(self, file_id: str = None, 
                                project_id: str = None) -> Dict[str, Any]:
        """
        Get quality metrics for files or projects.
        
        Args:
            file_id: Optional file ID to filter metrics
            project_id: Optional project ID to filter metrics
            
        Returns:
            Dict[str, Any]: Quality metrics data
        """
        try:
            if not self.metrics_service:
                return {'error': 'Metrics service not initialized'}
            
            # Get metrics statistics which include quality metrics
            stats = await self.metrics_service.get_metrics_statistics()
            
            # Filter quality-related metrics
            quality_metrics = {
                'overall_quality_score': stats.get('avg_health_score', 0.0),
                'data_quality_score': stats.get('avg_file_processing_efficiency', 0.0),
                'validation_success_rate': stats.get('avg_validation_success_rate', 0.0),
                'extraction_accuracy': stats.get('avg_extraction_accuracy', 0.0),
                'generation_quality': stats.get('avg_generation_quality', 0.0),
                'error_rate': stats.get('avg_error_rate', 0.0),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return {
                'status': 'success',
                'file_id': file_id,
                'project_id': project_id,
                'quality_metrics': quality_metrics
            }
            
        except Exception as e:
            logger.error(f"Failed to get quality metrics: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def get_performance_metrics(self, time_range: str = "24h") -> Dict[str, Any]:
        """
        Get performance metrics for AASX processing.
        
        Args:
            time_range: Time range for metrics (24h, 7d, 30d, 90d)
            
        Returns:
            Dict[str, Any]: Performance metrics data
        """
        try:
            if not self.metrics_service:
                return {'error': 'Metrics service not initialized'}
            
            # Get performance trends
            trends = await self.metrics_service.get_performance_trends(days=self._get_days_from_range(time_range))
            
            # Extract performance metrics
            performance_metrics = {
                'extraction_speed': {
                    'current_avg': trends.get('extraction_speed', {}).get('current_avg', 0.0),
                    'trend': trends.get('extraction_speed', {}).get('trend', 'stable'),
                    'improvement': trends.get('extraction_speed', {}).get('improvement_percentage', 0.0)
                },
                'generation_speed': {
                    'current_avg': trends.get('generation_speed', {}).get('current_avg', 0.0),
                    'trend': trends.get('generation_speed', {}).get('trend', 'stable'),
                    'improvement': trends.get('generation_speed', {}).get('improvement_percentage', 0.0)
                },
                'throughput': {
                    'jobs_per_hour': trends.get('throughput', {}).get('jobs_per_hour', 0),
                    'files_per_job': trends.get('throughput', {}).get('files_per_job', 0),
                    'efficiency': trends.get('throughput', {}).get('efficiency_percentage', 0.0)
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return {
                'status': 'success',
                'time_range': time_range,
                'performance_metrics': performance_metrics
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def get_resource_usage_metrics(self) -> Dict[str, Any]:
        """
        Get resource usage metrics (CPU, memory, disk).
        
        Returns:
            Dict[str, Any]: Resource usage metrics data
        """
        try:
            if not self.metrics_service:
                return {'error': 'Metrics service not initialized'}
            
            # Get current metrics statistics
            stats = await self.metrics_service.get_metrics_statistics()
            
            # Extract resource-related metrics
            resource_metrics = {
                'system_health': {
                    'uptime_percentage': stats.get('avg_uptime_percentage', 99.9),
                    'health_score': stats.get('avg_health_score', 95.0),
                    'response_time_ms': stats.get('avg_response_time_ms', 0.0)
                },
                'processing_efficiency': {
                    'file_processing_efficiency': stats.get('avg_file_processing_efficiency', 0.0),
                    'batch_processing_efficiency': stats.get('avg_batch_processing_efficiency', 0.0),
                    'resource_utilization': stats.get('avg_resource_utilization', 0.0)
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return {
                'status': 'success',
                'resource_metrics': resource_metrics
            }
            
        except Exception as e:
            logger.error(f"Failed to get resource usage metrics: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def get_error_metrics(self, time_range: str = "24h") -> Dict[str, Any]:
        """
        Get error metrics and failure rates.
        
        Args:
            time_range: Time range for metrics (24h, 7d, 30d, 90d)
            
        Returns:
            Dict[str, Any]: Error metrics data
        """
        try:
            if not self.metrics_service:
                return {'error': 'Metrics service not initialized'}
            
            # Get anomaly detection for errors
            anomalies = await self.metrics_service.get_anomaly_detection(threshold_std=2.0)
            
            # Filter error-related anomalies
            error_anomalies = [a for a in anomalies if a.get('metric_type') in ['error_rate', 'failure_rate']]
            
            # Get current error statistics
            stats = await self.metrics_service.get_metrics_statistics()
            
            error_metrics = {
                'current_error_rate': stats.get('avg_error_rate', 0.0),
                'failure_rate': stats.get('avg_failure_rate', 0.0),
                'anomalies_detected': len(error_anomalies),
                'error_trends': {
                    'critical_errors': len([a for a in error_anomalies if a.get('severity') == 'critical']),
                    'warning_errors': len([a for a in error_anomalies if a.get('severity') == 'warning']),
                    'info_errors': len([a for a in error_anomalies if a.get('severity') == 'info'])
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return {
                'status': 'success',
                'time_range': time_range,
                'error_metrics': error_metrics
            }
            
        except Exception as e:
            logger.error(f"Failed to get error metrics: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def get_user_behavior_metrics(self, user_id: str = None, 
                                      time_range: str = "24h") -> Dict[str, Any]:
        """
        Get user behavior and interaction metrics.
        
        Args:
            user_id: Optional user ID to filter metrics
            time_range: Time range for metrics (24h, 7d, 30d, 90d)
            
        Returns:
            Dict[str, Any]: User behavior metrics data
        """
        try:
            if not self.metrics_service:
                return {'error': 'Metrics service not initialized'}
            
            # Get performance trends which include user behavior patterns
            trends = await self.metrics_service.get_performance_trends(days=self._get_days_from_range(time_range))
            
            # Extract user behavior metrics
            user_metrics = {
                'usage_patterns': {
                    'peak_hours': trends.get('usage_patterns', {}).get('peak_hours', []),
                    'avg_session_duration': trends.get('usage_patterns', {}).get('avg_session_duration', 0.0),
                    'concurrent_users': trends.get('usage_patterns', {}).get('concurrent_users', 0)
                },
                'feature_usage': {
                    'extraction_usage': trends.get('feature_usage', {}).get('extraction_count', 0),
                    'generation_usage': trends.get('feature_usage', {}).get('generation_count', 0),
                    'validation_usage': trends.get('feature_usage', {}).get('validation_count', 0)
                },
                'user_satisfaction': {
                    'quality_score': trends.get('user_satisfaction', {}).get('avg_quality_score', 0.0),
                    'success_rate': trends.get('user_satisfaction', {}).get('success_rate', 0.0),
                    'feedback_score': trends.get('user_satisfaction', {}).get('feedback_score', 0.0)
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return {
                'status': 'success',
                'user_id': user_id,
                'time_range': time_range,
                'user_metrics': user_metrics
            }
            
        except Exception as e:
            logger.error(f"Failed to get user behavior metrics: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def create_metrics_from_etl_results(self, job_id: str, etl_results: Dict[str, Any]) -> str:
        """
        Create metrics record from ETL completion results.
        
        Args:
            job_id: Reference to aasx_processing.job_id
            etl_results: ETL processing results containing metrics
            
        Returns:
            str: Created metric ID
        """
        try:
            if not self.metrics_service:
                raise ValueError('Metrics service not initialized')
            
            # Delegate to engine service
            metric_id = await self.metrics_service.create_metrics_from_etl_results(job_id, etl_results)
            
            logger.info(f"Created metrics record {metric_id} for job {job_id}")
            return metric_id
            
        except Exception as e:
            logger.error(f"Failed to create metrics from ETL results: {e}")
            raise
    
    async def get_metrics_by_job_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metrics for a specific job.
        
        Args:
            job_id: Job ID to get metrics for
            
        Returns:
            Optional[Dict[str, Any]]: Metrics data for the job
        """
        try:
            if not self.metrics_service:
                return None
            
            metrics = await self.metrics_service.get_metrics_by_job_id(job_id)
            return metrics.dict() if metrics else None
            
        except Exception as e:
            logger.error(f"Failed to get metrics for job {job_id}: {e}")
            return None
    
    def _aggregate_metrics(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate metrics data for summary view."""
        if not metrics:
            return {}
        
        try:
            # Extract numeric values for aggregation
            health_scores = [m.get('health_score', 0) for m in metrics if m.get('health_score')]
            response_times = [m.get('response_time_ms', 0) for m in metrics if m.get('response_time_ms')]
            error_rates = [m.get('error_rate', 0) for m in metrics if m.get('error_rate')]
            
            aggregated = {
                'total_jobs': len(metrics),
                'avg_health_score': sum(health_scores) / len(health_scores) if health_scores else 0,
                'avg_response_time_ms': sum(response_times) / len(response_times) if response_times else 0,
                'avg_error_rate': sum(error_rates) / len(error_rates) if error_rates else 0,
                'success_rate': len([m for m in metrics if m.get('completion_status') == 'success']) / len(metrics) * 100 if metrics else 0
            }
            
            return aggregated
            
        except Exception as e:
            logger.error(f"Failed to aggregate metrics: {e}")
            return {}
    
    def _get_days_from_range(self, time_range: str) -> int:
        """Convert time range string to number of days."""
        range_mapping = {
            "24h": 1,
            "7d": 7,
            "30d": 30,
            "90d": 90
        }
        return range_mapping.get(time_range, 1)
