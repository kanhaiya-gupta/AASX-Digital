"""
Processing Metrics Service

This service manages comprehensive tracking and analytics for AASX processing jobs.
Updated to use the new architecture with Pydantic models and repositories.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import statistics

from ..models.aasx_processing_metrics import AasxProcessingMetrics, create_aasx_processing_metrics
from ..repositories.aasx_processing_metrics_repository import AasxProcessingMetricsRepository
from src.engine.database.connection_manager import ConnectionManager

logger = logging.getLogger(__name__)


class ProcessingMetricsService:
    """Service for managing comprehensive processing metrics using the new architecture."""
    
    def __init__(self, connection_manager: ConnectionManager):
        """
        Initialize the service with connection manager.
        
        Args:
            connection_manager: Engine connection manager instance
        """
        self.connection_manager = connection_manager
        self.repository = AasxProcessingMetricsRepository(connection_manager)
        logger.info("ProcessingMetricsService initialized with new architecture")
    
    async def create_metrics_record(self, job_id: str, metrics_data: Dict[str, Any]) -> str:
        """
        Create a new metrics record for a processing job.
        
        Args:
            job_id: Reference to aasx_processing.job_id
            metrics_data: Dictionary containing metrics information
            
        Returns:
            str: Created metric ID
        """
        try:
            # Create Pydantic model instance
            metrics = create_aasx_processing_metrics(
                job_id=job_id,
                **metrics_data
            )
            
            # Save to database via repository
            metric_id = await self.repository.create(metrics)
            
            logger.info(f"Created metrics record {metric_id} for job {job_id}")
            return metric_id
            
        except Exception as e:
            logger.error(f"Failed to create metrics record: {e}")
            raise
    
    async def create_metrics_from_etl_results(self, job_id: str, etl_results: Dict[str, Any]) -> str:
        """
        Automatically create metrics record from ETL completion results.
        
        Args:
            job_id: Reference to aasx_processing.job_id
            etl_results: ETL processing results containing metrics
            
        Returns:
            str: Created metric ID
        """
        try:
            # Extract metrics from ETL results and map to actual database columns
            metrics_data = {
                # Primary Identification
                "job_id": job_id,
                "timestamp": datetime.utcnow().isoformat(),
                "dept_id": etl_results.get("dept_id"),  # Department ID for complete traceability
                
                # Real-time Health Metrics (from schema)
                "health_score": etl_results.get("health_score", 95),  # Default healthy score
                "response_time_ms": etl_results.get("response_time_ms", 0.0),
                "uptime_percentage": etl_results.get("uptime_percentage", 99.9),
                "error_rate": etl_results.get("error_rate", 0.0),
                
                # AASX Processing Performance Metrics (from schema)
                "extraction_speed_sec": etl_results.get("extraction_time_ms", 0) / 1000.0,  # Convert ms to seconds
                "generation_speed_sec": etl_results.get("generation_time_ms", 0) / 1000.0,  # Convert ms to seconds
                "validation_speed_sec": etl_results.get("validation_time_ms", 0) / 1000.0,  # Convert ms to seconds
                "file_processing_efficiency": etl_results.get("data_quality_score", 0.0),
                
                # Processing Technique Performance (JSON)
                "processing_technique_performance": {
                    "extraction": {
                        "usage_count": 1,
                        "avg_processing_time": etl_results.get("extraction_time_ms", 0) / 1000.0,
                        "success_rate": 1.0 if etl_results.get("completion_status") == "success" else 0.0,
                        "last_used": datetime.utcnow().isoformat()
                    },
                    "generation": {
                        "usage_count": 1,
                        "avg_processing_time": etl_results.get("generation_time_ms", 0) / 1000.0,
                        "success_rate": 1.0 if etl_results.get("completion_status") == "success" else 0.0,
                        "last_used": datetime.utcnow().isoformat()
                    },
                    "validation": {
                        "usage_count": 1,
                        "avg_processing_time": etl_results.get("validation_time_ms", 0) / 1000.0,
                        "success_rate": 1.0 if etl_results.get("completion_status") == "success" else 0.0,
                        "last_used": datetime.utcnow().isoformat()
                    }
                },
                
                # File Type Processing Metrics (JSON)
                "file_type_processing_stats": {
                    "aasx": {
                        "processed": 1,
                        "successful": 1 if etl_results.get("completion_status") == "success" else 0,
                        "failed": 0 if etl_results.get("completion_status") == "success" else 1,
                        "avg_processing_time": etl_results.get("processing_time_ms", 0) / 1000.0,
                        "file_sizes": {"medium": 1}
                    }
                },
                
                # User Interaction Metrics
                "user_interaction_count": 1,
                "job_execution_count": 1,
                "successful_processing_operations": 1 if etl_results.get("completion_status") == "success" else 0,
                "failed_processing_operations": 0 if etl_results.get("completion_status") == "success" else 1,
                
                # Data Quality Metrics (from schema)
                "data_freshness_score": etl_results.get("data_freshness_score", 1.0),
                "data_completeness_score": etl_results.get("data_completeness_score", 1.0),
                "data_consistency_score": etl_results.get("data_consistency_score", 1.0),
                "data_accuracy_score": etl_results.get("data_accuracy_score", etl_results.get("data_quality_score", 1.0)),
                
                # System Resource Metrics (from schema)
                "cpu_usage_percent": etl_results.get("cpu_usage_percent", 0.0),
                "memory_usage_percent": etl_results.get("memory_usage_mb", 0.0) / 100.0,  # Convert MB to percentage
                "network_throughput_mbps": etl_results.get("network_io_mb", 0.0) * 8.0,  # Convert MB to Mbps
                "storage_usage_percent": 0.0,  # Default value
                "disk_io_mb": etl_results.get("disk_io_mb", 0.0),
                
                # Processing Patterns & Analytics (JSON)
                "processing_patterns": {
                    "hourly": {"current_hour": 1},
                    "daily": {"current_day": 1},
                    "weekly": {"current_week": 1},
                    "monthly": {"current_month": 1}
                },
                "resource_utilization_trends": {
                    "cpu_trend": [etl_results.get("cpu_usage_percent", 0.0)],
                    "memory_trend": [etl_results.get("memory_usage_mb", 0.0)],
                    "disk_trend": [etl_results.get("disk_io_mb", 0.0)]
                },
                "user_activity": {
                    "peak_hours": [datetime.utcnow().hour],
                    "user_patterns": {"single_user": 1},
                    "session_durations": [etl_results.get("processing_time_ms", 0) / 1000.0]
                },
                "job_patterns": {
                    "job_types": {"extraction": 1},
                    "complexity_distribution": {"simple": 1},
                    "processing_times": [etl_results.get("processing_time_ms", 0) / 1000.0]
                },
                "compliance_status": {
                    "compliance_score": 0.95,
                    "audit_status": "passed",
                    "last_audit": datetime.utcnow().isoformat()
                },
                "security_events": {
                    "events": [],
                    "threat_level": "low",
                    "last_security_scan": datetime.utcnow().isoformat()
                },
                
                # AASX-Specific Metrics (JSON)
                "aasx_analytics": {
                    "extraction_quality": etl_results.get("data_quality_score", 1.0),
                    "generation_quality": etl_results.get("data_quality_score", 1.0),
                    "validation_quality": etl_results.get("data_quality_score", 1.0)
                },
                "technique_effectiveness": {
                    "technique_comparison": {
                        "extraction": "effective",
                        "generation": "effective",
                        "validation": "effective"
                    },
                    "best_performing": "extraction",
                    "optimization_suggestions": []
                },
                "format_performance": {
                    "aasx_performance": {"success_rate": 1.0, "avg_time": etl_results.get("processing_time_ms", 0) / 1000.0}
                },
                "file_size_processing_efficiency": {
                    "processing_speed_by_size": {"medium": etl_results.get("processing_time_ms", 0) / 1000.0},
                    "quality_by_size": {"medium": etl_results.get("data_quality_score", 1.0)},
                    "optimization_opportunities": []
                },
                
                # Time-based Analytics (from schema)
                "hour_of_day": datetime.utcnow().hour,
                "day_of_week": datetime.utcnow().isoweekday(),
                "month": datetime.utcnow().month,
                
                # Performance Trends (from schema)
                "processing_time_trend": 0.0,  # Default stable trend
                "resource_efficiency_trend": 0.0,  # Default stable trend
                "quality_trend": 0.0  # Default stable trend
            }
            
            # Create the metrics record
            metric_id = await self.create_metrics_record(job_id, metrics_data)
            
            logger.info(f"Auto-created metrics record {metric_id} from ETL results for job {job_id} with all schema columns")
            return metric_id
            
        except Exception as e:
            logger.error(f"Failed to create metrics from ETL results for job {job_id}: {e}")
            raise
    
    async def create_batch_metrics(self, batch_job_id: str, individual_metrics: List[Dict[str, Any]]) -> str:
        """
        Create aggregated metrics for a batch processing job.
        
        Args:
            batch_job_id: Reference to the batch aasx_processing.job_id
            individual_metrics: List of metrics from individual file processing
            
        Returns:
            str: Created batch metric ID
        """
        try:
            if not individual_metrics:
                raise ValueError("Individual metrics list cannot be empty")
            
            # Aggregate metrics across all files
            total_processing_time = sum(m.get("processing_time_ms", 0) for m in individual_metrics)
            total_file_size = sum(m.get("file_size_bytes", 0) for m in individual_metrics)
            total_errors = sum(m.get("error_count", 0) for m in individual_metrics)
            total_warnings = sum(m.get("warning_count", 0) for m in individual_metrics)
            
            # Calculate averages
            avg_quality_score = statistics.mean([m.get("data_quality_score", 0.0) for m in individual_metrics])
            avg_accuracy = statistics.mean([m.get("processing_accuracy", 0.0) for m in individual_metrics])
            avg_throughput = statistics.mean([m.get("throughput_files_per_second", 0.0) for m in individual_metrics])
            
            # Calculate success rate
            successful_jobs = sum(1 for m in individual_metrics if m.get("completion_status") == "success")
            total_jobs = len(individual_metrics)
            success_rate = successful_jobs / total_jobs if total_jobs > 0 else 0.0
            
            # Prepare batch metrics data
            batch_metrics_data = {
                "processing_time_ms": total_processing_time,
                "file_size_bytes": total_file_size,
                "data_quality_score": avg_quality_score,
                "processing_accuracy": avg_accuracy,
                "error_count": total_errors,
                "warning_count": total_warnings,
                "success_rate": success_rate,
                "throughput_files_per_second": avg_throughput,
                "concurrent_jobs": total_jobs,
                "completion_status": "success" if success_rate == 1.0 else "partial_success",
                "batch_size": total_jobs,
                "batch_metadata": {
                    "individual_metrics_count": len(individual_metrics),
                    "successful_jobs": successful_jobs,
                    "failed_jobs": total_jobs - successful_jobs,
                    "aggregation_method": "mean_for_averages_sum_for_totals"
                },
                "timestamp": datetime.utcnow()
            }
            
            # Create the batch metrics record
            metric_id = await self.create_metrics_record(batch_job_id, batch_metrics_data)
            
            logger.info(f"Created batch metrics record {metric_id} for batch job {batch_job_id}")
            return metric_id
            
        except Exception as e:
            logger.error(f"Failed to create batch metrics for job {batch_job_id}: {e}")
            raise
    
    async def get_metrics_by_job_id(self, job_id: str) -> Optional[AasxProcessingMetrics]:
        """
        Get metrics for a specific job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Optional[AasxProcessingMetrics]: Metrics instance or None
        """
        try:
            return await self.repository.get_by_job_id(job_id)
        except Exception as e:
            logger.error(f"Failed to get metrics for job {job_id}: {e}")
            return None
    
    async def get_metrics_by_date_range(self, start_date: datetime, end_date: datetime, 
                                       limit: int = 100) -> List[AasxProcessingMetrics]:
        """
        Get metrics within a date range.
        
        Args:
            start_date: Start date
            end_date: End date
            limit: Maximum number of records to return
            
        Returns:
            List[AasxProcessingMetrics]: List of metrics records
        """
        try:
            return await self.repository.get_by_date_range(start_date, end_date, limit)
        except Exception as e:
            logger.error(f"Failed to get metrics by date range: {e}")
            return []
    
    async def get_performance_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        Get performance trends over a specified period.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict[str, Any]: Performance trend data
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            metrics = await self.repository.get_by_date_range(start_date, end_date, limit=1000)
            
            if not metrics:
                return {"message": "No metrics data available for the specified period"}
            
            # Calculate trends
            processing_times = [m.processing_time_ms for m in metrics if m.processing_time_ms]
            quality_scores = [m.data_quality_score for m in metrics if m.data_quality_score]
            success_rates = [m.success_rate for m in metrics if m.success_rate]
            
            trends = {
                "period_days": days,
                "total_records": len(metrics),
                "processing_time": {
                    "mean": statistics.mean(processing_times) if processing_times else 0,
                    "median": statistics.median(processing_times) if processing_times else 0,
                    "min": min(processing_times) if processing_times else 0,
                    "max": max(processing_times) if processing_times else 0,
                    "trend": "stable"  # Could be enhanced with linear regression
                },
                "quality_score": {
                    "mean": statistics.mean(quality_scores) if quality_scores else 0,
                    "median": statistics.median(quality_scores) if quality_scores else 0,
                    "min": min(quality_scores) if quality_scores else 0,
                    "max": max(quality_scores) if quality_scores else 0,
                    "trend": "stable"
                },
                "success_rate": {
                    "mean": statistics.mean(success_rates) if success_rates else 0,
                    "median": statistics.median(success_rates) if success_rates else 0,
                    "min": min(success_rates) if success_rates else 0,
                    "max": max(success_rates) if success_rates else 0,
                    "trend": "stable"
                }
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to get performance trends: {e}")
            return {"error": str(e)}
    
    async def get_anomaly_detection(self, threshold_std: float = 2.0) -> List[Dict[str, Any]]:
        """
        Detect anomalies in processing metrics.
        
        Args:
            threshold_std: Standard deviation threshold for anomaly detection
            
        Returns:
            List[Dict[str, Any]]: List of detected anomalies
        """
        try:
            # Get recent metrics for analysis
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=7)  # Last week
            
            metrics = await self.repository.get_by_date_range(start_date, end_date, limit=500)
            
            if not metrics:
                return []
            
            # Extract key metrics for analysis
            processing_times = [m.processing_time_ms for m in metrics if m.processing_time_ms]
            quality_scores = [m.data_quality_score for m in metrics if m.data_quality_score]
            
            anomalies = []
            
            if processing_times:
                mean_time = statistics.mean(processing_times)
                std_time = statistics.stdev(processing_times) if len(processing_times) > 1 else 0
                
                for metric in metrics:
                    if metric.processing_time_ms:
                        z_score = abs((metric.processing_time_ms - mean_time) / std_time) if std_time > 0 else 0
                        if z_score > threshold_std:
                            anomalies.append({
                                "metric_id": metric.metric_id,
                                "job_id": metric.job_id,
                                "anomaly_type": "processing_time",
                                "value": metric.processing_time_ms,
                                "mean": mean_time,
                                "std": std_time,
                                "z_score": z_score,
                                "severity": "high" if z_score > 3 else "medium",
                                "timestamp": metric.timestamp
                            })
            
            if quality_scores:
                mean_quality = statistics.mean(quality_scores)
                std_quality = statistics.stdev(quality_scores) if len(quality_scores) > 1 else 0
                
                for metric in metrics:
                    if metric.data_quality_score:
                        z_score = abs((metric.data_quality_score - mean_quality) / std_quality) if std_quality > 0 else 0
                        if z_score > threshold_std:
                            anomalies.append({
                                "metric_id": metric.metric_id,
                                "job_id": metric.job_id,
                                "anomaly_type": "quality_score",
                                "value": metric.data_quality_score,
                                "mean": mean_quality,
                                "std": std_quality,
                                "z_score": z_score,
                                "severity": "high" if z_score > 3 else "medium",
                                "timestamp": metric.timestamp
                            })
            
            # Sort by severity and z-score
            anomalies.sort(key=lambda x: (x["severity"] == "high", x["z_score"]), reverse=True)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Failed to detect anomalies: {e}")
            return []
    
    async def get_metrics_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive metrics statistics.
        
        Returns:
            Dict[str, Any]: Metrics statistics
        """
        try:
            stats = await self.repository.get_statistics()
            return stats
        except Exception as e:
            logger.error(f"Failed to get metrics statistics: {e}")
            return {}
    
    async def cleanup_old_metrics(self, days_old: int = 90) -> int:
        """
        Clean up old metrics records.
        
        Args:
            days_old: Age threshold in days
            
        Returns:
            int: Number of records cleaned up
        """
        try:
            count = await self.repository.cleanup_old_metrics(days_old)
            logger.info(f"Cleaned up {count} old metrics records")
            return count
        except Exception as e:
            logger.error(f"Failed to cleanup old metrics: {e}")
            return 0
