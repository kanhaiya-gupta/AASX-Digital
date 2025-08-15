"""
Processing Metrics Service for AASX-ETL

This service manages comprehensive tracking and analytics for AASX processing jobs.
Part of Phase 4: Comprehensive Tracking & Analytics
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SystemResources:
    """System resource metrics during processing."""
    memory_usage_mb: float
    cpu_usage_percent: float
    disk_io_mb: float
    network_usage_mb: float
    timestamp: datetime


@dataclass
class QualityMetrics:
    """Quality assessment metrics."""
    data_quality_score: float  # 0-100
    file_integrity_checksum: str
    processing_accuracy: float  # 0-100
    validation_results: Dict[str, Any]


class ProcessingMetricsService:
    """Service for managing comprehensive processing metrics."""
    
    def __init__(self, db_connection):
        self.db = db_connection
        logger.info("ProcessingMetricsService initialized")
    
    def create_metrics_record(self, job_id: str, metrics_data: Dict[str, Any]) -> str:
        """Create a new metrics record for a processing job."""
        try:
            # Extract current timestamp components
            now = datetime.now()
            hour_of_day = now.hour
            day_of_week = now.isoweekday()  # 1=Monday, 7=Sunday
            month = now.month
            
            # Prepare the insert query
            query = """
                INSERT INTO aasx_processing_metrics (
                    job_id, timestamp, hour_of_day, day_of_week, month,
                    memory_usage_mb, cpu_usage_percent, disk_io_mb, network_usage_mb,
                    validation_results, quality_metrics, peak_memory_mb, peak_cpu_percent,
                    total_disk_io_mb, processing_efficiency_score, session_duration_seconds,
                    consecutive_jobs_count, user_behavior_patterns, processing_time_trend,
                    resource_efficiency_trend, data_sensitivity_level, compliance_requirements,
                    access_logs, security_events, retention_policy, scheduled_deletion_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # Extract values from metrics_data
            values = (
                job_id,
                now.isoformat(),
                hour_of_day,
                day_of_week,
                month,
                metrics_data.get('system_resources', {}).get('memory_usage_mb'),
                metrics_data.get('system_resources', {}).get('cpu_usage_percent'),
                metrics_data.get('system_resources', {}).get('disk_io_mb'),
                metrics_data.get('system_resources', {}).get('network_usage_mb'),
                json.dumps(metrics_data.get('validation_results', {})),
                json.dumps(metrics_data.get('quality_metrics', {})),
                metrics_data.get('system_resources', {}).get('peak_memory_mb'),
                metrics_data.get('system_resources', {}).get('peak_cpu_percent'),
                metrics_data.get('system_resources', {}).get('total_disk_io_mb'),
                metrics_data.get('processing_efficiency_score', 0.0),
                metrics_data.get('session_duration_seconds'),
                metrics_data.get('consecutive_jobs_count', 1),
                json.dumps(metrics_data.get('user_behavior_patterns', {})),
                metrics_data.get('processing_time_trend'),
                metrics_data.get('resource_efficiency_trend'),
                metrics_data.get('compliance_data', {}).get('data_sensitivity_level', 'internal'),
                json.dumps(metrics_data.get('compliance_data', {}).get('compliance_requirements', [])),
                json.dumps(metrics_data.get('compliance_data', {}).get('access_logs', [])),
                json.dumps(metrics_data.get('compliance_data', {}).get('security_events', [])),
                metrics_data.get('compliance_data', {}).get('retention_policy', 'default'),
                metrics_data.get('compliance_data', {}).get('scheduled_deletion_date')
            )
            
            # Execute the insert
            cursor = self.db.cursor()
            cursor.execute(query, values)
            metrics_id = cursor.lastrowid
            self.db.commit()
            
            logger.info(f"Created metrics record {metrics_id} for job {job_id}")
            return str(metrics_id)
            
        except Exception as e:
            logger.error(f"Failed to create metrics record for job {job_id}: {e}")
            raise
    
    def update_metrics(self, metrics_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing metrics record."""
        try:
            # Build dynamic update query
            set_clauses = []
            values = []
            
            for key, value in updates.items():
                if key in ['validation_results', 'quality_metrics', 'user_behavior_patterns', 
                          'compliance_requirements', 'access_logs', 'security_events']:
                    # JSON fields
                    set_clauses.append(f"{key} = ?")
                    values.append(json.dumps(value))
                else:
                    # Regular fields
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            
            if not set_clauses:
                logger.warning("No valid fields to update")
                return False
            
            # Add metrics_id to values
            values.append(metrics_id)
            
            query = f"UPDATE aasx_processing_metrics SET {', '.join(set_clauses)} WHERE id = ?"
            
            cursor = self.db.cursor()
            cursor.execute(query, values)
            self.db.commit()
            
            logger.info(f"Updated metrics record {metrics_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update metrics record {metrics_id}: {e}")
            return False
    
    def get_job_metrics(self, job_id: str) -> Dict[str, Any]:
        """Get all metrics for a specific job."""
        try:
            query = """
                SELECT * FROM aasx_processing_metrics 
                WHERE job_id = ? 
                ORDER BY timestamp DESC
            """
            
            cursor = self.db.cursor()
            cursor.execute(query, (job_id,))
            row = cursor.fetchone()
            
            if not row:
                logger.warning(f"No metrics found for job {job_id}")
                return {}
            
            # Convert row to dict
            columns = [description[0] for description in cursor.description]
            metrics = dict(zip(columns, row))
            
            # Parse JSON fields
            for field in ['validation_results', 'quality_metrics', 'user_behavior_patterns', 
                         'compliance_requirements', 'access_logs', 'security_events']:
                if metrics.get(field):
                    try:
                        metrics[field] = json.loads(metrics[field])
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse JSON for {field}")
                        metrics[field] = {}
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get metrics for job {job_id}: {e}")
            return {}
    
    def get_performance_trends(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get performance trends over time for a user."""
        try:
            # Get user's jobs from aasx_processing
            jobs_query = """
                SELECT id, processing_time, timestamp 
                FROM aasx_processing 
                WHERE processed_by = ? 
                AND timestamp >= datetime('now', '-{} days')
                ORDER BY timestamp
            """.format(days)
            
            cursor = self.db.cursor()
            cursor.execute(jobs_query, (user_id,))
            jobs = cursor.fetchall()
            
            if not jobs:
                return {"message": "No jobs found for the specified period"}
            
            # Calculate trends
            processing_times = [job[1] for job in jobs if job[1] is not None]
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
            
            # Get metrics data for these jobs
            job_ids = [str(job[0]) for job in jobs]
            placeholders = ','.join(['?' for _ in job_ids])
            
            metrics_query = f"""
                SELECT processing_efficiency_score, resource_efficiency_trend
                FROM aasx_processing_metrics 
                WHERE job_id IN ({placeholders})
                AND processing_efficiency_score IS NOT NULL
            """
            
            cursor.execute(metrics_query, job_ids)
            metrics = cursor.fetchall()
            
            efficiency_scores = [m[0] for m in metrics if m[0] is not None]
            avg_efficiency = sum(efficiency_scores) / len(efficiency_scores) if efficiency_scores else 0
            
            trends = {
                "period_days": days,
                "total_jobs": len(jobs),
                "average_processing_time": avg_processing_time,
                "average_efficiency_score": avg_efficiency,
                "processing_times": processing_times,
                "efficiency_scores": efficiency_scores,
                "trend_analysis": {
                    "processing_time_trend": "stable",  # Could be calculated based on slope
                    "efficiency_trend": "stable"
                }
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to get performance trends for user {user_id}: {e}")
            return {"error": str(e)}
    
    def get_system_resource_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get system resource usage summary for the last N hours."""
        try:
            query = """
                SELECT 
                    AVG(memory_usage_mb) as avg_memory,
                    MAX(memory_usage_mb) as peak_memory,
                    AVG(cpu_usage_percent) as avg_cpu,
                    MAX(cpu_usage_percent) as peak_cpu,
                    AVG(disk_io_mb) as avg_disk_io,
                    SUM(disk_io_mb) as total_disk_io,
                    COUNT(*) as total_jobs
                FROM aasx_processing_metrics 
                WHERE timestamp >= datetime('now', '-{} hours')
                AND memory_usage_mb IS NOT NULL
            """.format(hours)
            
            cursor = self.db.cursor()
            cursor.execute(query)
            row = cursor.fetchone()
            
            if not row:
                return {"message": "No metrics data found for the specified period"}
            
            columns = [description[0] for description in cursor.description]
            summary = dict(zip(columns, row))
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get system resource summary: {e}")
            return {"error": str(e)}
    
    def cleanup_old_metrics(self, days: int = 90) -> int:
        """Clean up metrics older than specified days. Returns number of deleted records."""
        try:
            query = """
                DELETE FROM aasx_processing_metrics 
                WHERE timestamp < datetime('now', '-{} days')
            """.format(days)
            
            cursor = self.db.cursor()
            cursor.execute(query)
            deleted_count = cursor.rowcount
            self.db.commit()
            
            logger.info(f"Cleaned up {deleted_count} old metrics records")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old metrics: {e}")
            return 0
