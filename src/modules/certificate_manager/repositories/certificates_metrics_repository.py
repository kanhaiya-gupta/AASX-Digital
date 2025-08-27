"""
Certificate Metrics Repository - Database Access Layer

This repository handles all CRUD operations for the certificates_metrics table.
It provides comprehensive database access for certificate metrics management, including
performance metrics, usage analytics, quality analytics, business metrics,
enterprise analytics, and real-time metrics operations.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
import json
import asyncio
from src.engine.database.connection_manager import ConnectionManager

from ..models.certificates_metrics import (
    CertificateMetrics,
    PerformanceTrend,
    MetricCategory,
    MetricPriority
)


logger = logging.getLogger(__name__)


class CertificatesMetricsRepository:
    """Repository for certificates_metrics table operations"""
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize with connection manager for raw SQL operations."""
        self.connection_manager = connection_manager
        self.table_name = "certificates_metrics"
        logger.info("Certificate Metrics Repository initialized with ConnectionManager")
    
    async def create_metrics(self, metrics: CertificateMetrics) -> bool:
        """Create new certificate metrics in the database using raw SQL"""
        try:
            # Convert model to dictionary for database storage
            metrics_data = await metrics.to_dict()
            
            # Prepare SQL insert statement
            columns = list(metrics_data.keys())
            placeholders = [f":{col}" for col in columns]
            
            query = f"""
                INSERT INTO {self.table_name} 
                ({', '.join(columns)}) 
                VALUES ({', '.join(placeholders)})
            """
            
            # Execute insert using ConnectionManager
            await self.execute_query(query, metrics_data)
            
            logger.info(f"Created certificate metrics: {metrics.metrics_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating certificate metrics: {e}")
            return False
    
    async def get_metrics_by_id(self, metrics_id: str) -> Optional[CertificateMetrics]:
        """Retrieve certificate metrics by ID using raw SQL"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE metrics_id = :metrics_id"
            result = await self.fetch_one(query, {"metrics_id": metrics_id})
            
            if result:
                # Create model instance
                metrics = CertificateMetrics(**result)
                return metrics
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving certificate metrics {metrics_id}: {e}")
            return None
    
    async def get_metrics_by_certificate(self, certificate_id: str, limit: int = 100) -> List[CertificateMetrics]:
        """Retrieve all metrics for a specific certificate using raw SQL"""
        try:
            query = f"""
                SELECT * FROM {self.table_name} 
                WHERE certificate_id = :cert_id 
                ORDER BY created_at DESC 
                LIMIT :limit
            """
            
            params = {"cert_id": certificate_id, "limit": limit}
            result = await self.execute_query(query, params)
            
            return [CertificateMetrics(**row) for row in result]
            
        except Exception as e:
            logger.error(f"Error retrieving metrics for certificate {certificate_id}: {e}")
            return []
    
    async def get_latest_metrics(self, certificate_id: str) -> Optional[CertificateMetrics]:
        """Get the latest metrics for a certificate"""
        try:
            query = f"""
                SELECT * FROM {self.table_name} 
                WHERE certificate_id = :cert_id 
                ORDER BY created_at DESC 
                LIMIT 1
            """
            result = await self.fetch_one(query, {"cert_id": certificate_id})
            
            if result:
                metrics = CertificateMetrics(**result)
                return metrics
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving latest metrics for certificate {certificate_id}: {e}")
            return None
    
    async def get_metrics_by_org(self, org_id: str, limit: int = 100) -> List[CertificateMetrics]:
        """Retrieve metrics by organization ID"""
        try:
            query = f"""
                SELECT * FROM {self.table_name} 
                WHERE org_id = :org_id 
                ORDER BY created_at DESC 
                LIMIT :limit
            """
            result = await self.execute_query(query, {"org_id": org_id, "limit": limit})
            return [CertificateMetrics(**row) for row in result]
            
        except Exception as e:
            logger.error(f"Error retrieving metrics for org {org_id}: {e}")
            return []
    
    async def get_metrics_by_dept(self, dept_id: str, limit: int = 100) -> List[CertificateMetrics]:
        """Retrieve metrics by department ID"""
        try:
            query = f"""
                SELECT * FROM {self.table_name} 
                WHERE dept_id = :dept_id 
                ORDER BY created_at DESC 
                LIMIT :limit
            """
            result = await self.execute_query(query, {"dept_id": dept_id, "limit": limit})
            return [CertificateMetrics(**row) for row in result]
            
        except Exception as e:
            logger.error(f"Error retrieving metrics for dept {dept_id}: {e}")
            return []
    
    async def get_metrics_by_category(self, certificate_id: str, category: MetricCategory, limit: int = 100) -> List[CertificateMetrics]:
        """Get metrics by category for a certificate"""
        try:
            query = f"""
                SELECT * FROM {self.table_name} 
                WHERE certificate_id = :cert_id AND metric_category = :cat
                ORDER BY created_at DESC 
                LIMIT :limit
            """
            result = await self.execute_query(query, {
                "cert_id": certificate_id, 
                "cat": category.value, 
                "limit": limit
            })
            return [CertificateMetrics(**row) for row in result]
            
        except Exception as e:
            logger.error(f"Error retrieving {category.value} metrics for certificate {certificate_id}: {e}")
            return []
    
    async def update_metrics(self, metrics: CertificateMetrics) -> bool:
        """Update existing certificate metrics"""
        try:
            # Convert model to dictionary
            metrics_data = await metrics.to_dict()
            metrics_id = metrics_data.pop("metrics_id")  # Remove ID from update data
            
            # Prepare update statement
            set_clause = ", ".join([f"{col} = :{col}" for col in metrics_data.keys()])
            query = f"""
                UPDATE {self.table_name} 
                SET {set_clause}, updated_at = :updated_at
                WHERE metrics_id = :metrics_id
            """
            
            # Add back the metrics_id for WHERE clause
            update_data = {**metrics_data, "metrics_id": metrics_id, "updated_at": datetime.utcnow().isoformat()}
            
            # Execute update using ConnectionManager
            await self.execute_query(query, update_data)
            
            if result.rowcount > 0:
                logger.info(f"Updated certificate metrics: {metrics.metrics_id}")
                return True
            else:
                logger.warning(f"No metrics found to update: {metrics.metrics_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating certificate metrics {metrics.metrics_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating certificate metrics {metrics.metrics_id}: {e}")
            return False
    
    async def delete_metrics(self, metrics_id: str) -> bool:
        """Delete certificate metrics by ID"""
        try:
            query = f"DELETE FROM {self.table_name} WHERE metrics_id = :metrics_id"
            result = await self.execute_query(query, {"metrics_id": metrics_id})
            
            if result.rowcount > 0:
                logger.info(f"Deleted certificate metrics: {metrics_id}")
                return True
            else:
                logger.warning(f"No metrics found to delete: {metrics_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting certificate metrics {metrics_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting certificate metrics {metrics_id}: {e}")
            return False
    

    
    # Trend Analysis Operations
    async def calculate_performance_trends(self, certificate_id: str, days: int = 30) -> Dict[str, Any]:
        """Calculate performance trends over a specified period"""
        try:
            # Get metrics for the specified period
            start_date = datetime.utcnow() - timedelta(days=days)
            
            query = f"""
                SELECT * FROM {self.table_name} 
                WHERE certificate_id = :cert_id AND created_at >= :start_date
                ORDER BY created_at ASC
            """
            result = await self.execute_query(query, {
                "cert_id": certificate_id,
                "start_date": start_date.isoformat()
            })
            
            if not result:
                return {"trend": "insufficient_data", "message": "No metrics data available for trend analysis"}
            
            # Calculate trends
            trends = {
                "period_days": days,
                "total_metrics": len(result),
                "performance_trend": "stable",
                "quality_trend": "stable",
                "usage_trend": "stable",
                "business_trend": "stable"
            }
            
            # Analyze performance trends
            performance_scores = []
            for row in result:
                metrics_data = dict(row)
                if "performance_metrics_data" in metrics_data and metrics_data["performance_metrics_data"]:
                    try:
                        perf_data = json.loads(metrics_data["performance_metrics_data"])
                        if "overall_score" in perf_data:
                            performance_scores.append(perf_data["overall_score"])
                    except json.JSONDecodeError:
                        continue
            
            if len(performance_scores) >= 2:
                if performance_scores[-1] > performance_scores[0] * 1.1:
                    trends["performance_trend"] = "improving"
                elif performance_scores[-1] < performance_scores[0] * 0.9:
                    trends["performance_trend"] = "declining"
            
            return trends
            
        except Exception as e:
            logger.error(f"Error calculating performance trends for certificate {certificate_id}: {e}")
            return {"trend": "error", "message": str(e)}
    
    # Search and Filter Operations
    async def search_metrics(self, search_criteria: Dict[str, Any], limit: int = 100) -> List[CertificateMetrics]:
        """Search certificate metrics based on multiple criteria"""
        try:
            # Build dynamic WHERE clause
            where_conditions = []
            params = {}
            
            for key, value in search_criteria.items():
                if value is not None:
                    where_conditions.append(f"{key} = :{key}")
                    params[key] = value
            
            if not where_conditions:
                # If no criteria, return all metrics
                query = f"SELECT * FROM {self.table_name} ORDER BY created_at DESC LIMIT :limit"
                params = {"limit": limit}
            else:
                where_clause = " AND ".join(where_conditions)
                query = f"""
                    SELECT * FROM {self.table_name} 
                    WHERE {where_clause} 
                    ORDER BY created_at DESC 
                    LIMIT :limit
                """
                params["limit"] = limit
            
            result = await self.execute_query(query, params)
            return [CertificateMetrics(**row) for row in result]
            
        except Exception as e:
            logger.error(f"Error searching certificate metrics: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error searching certificate metrics: {e}")
            return []
    
    # Bulk Operations
    async def bulk_update_metrics(self, updates: List[Tuple[str, Dict[str, Any]]]) -> bool:
        """Bulk update metrics for multiple certificates"""
        try:
            success_count = 0
            total_count = len(updates)
            
            for metrics_id, update_data in updates:
                # Get existing metrics
                metrics = await self.get_metrics_by_id(metrics_id)
                if metrics:
                    # Update with new data
                    for key, value in update_data.items():
                        if hasattr(metrics, key):
                            setattr(metrics, key, value)
                    
                    if await self.update_metrics(metrics):
                        success_count += 1
            
            logger.info(f"Bulk update completed: {success_count}/{total_count} successful")
            return success_count == total_count
            
        except Exception as e:
            logger.error(f"Error in bulk update metrics: {e}")
            return False
    
    # Statistics and Analytics
    async def get_all_metrics(
        self,
        limit: int = 1000,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[CertificateMetrics]:
        """Get all metrics with optional filtering"""
        try:
            where_conditions = []
            params = {}
            
            if filters:
                for key, value in filters.items():
                    if value is not None:
                        where_conditions.append(f"{key} = :{key}")
                        params[key] = value
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            query = f"""
                SELECT * FROM {self.table_name} 
                WHERE {where_clause} 
                ORDER BY created_at DESC 
                LIMIT :limit OFFSET :offset
            """
            params["limit"] = limit
            params["offset"] = offset
            
            result = await self.execute_query(query, params)
            return [CertificateMetrics(**row) for row in result]
            
        except Exception as e:
            logger.error(f"Error retrieving all metrics: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error retrieving all metrics: {e}")
            return []
    
    async def get_metrics_stats(self, org_id: Optional[str] = None, dept_id: Optional[str] = None) -> Dict[str, Any]:
        """Get metrics statistics and analytics"""
        try:
            where_conditions = []
            params = {}
            
            if org_id:
                where_conditions.append("org_id = :org_id")
                params["org_id"] = org_id
            
            if dept_id:
                where_conditions.append("dept_id = :dept_id")
                params["dept_id"] = dept_id
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            # Get total count
            count_query = f"SELECT COUNT(*) as total FROM {self.table_name} WHERE {where_clause}"
            count_result = await self.execute_query(count_query, params)
            total_count = count_result[0][0] if count_result else 0
            
            # Get metric category distribution
            category_query = f"""
                SELECT metric_category, COUNT(*) as count 
                FROM {self.table_name} 
                WHERE {where_clause} 
                GROUP BY metric_category
            """
            category_result = await self.execute_query(category_query, params)
            category_distribution = {row[0]: row[1] for row in category_result}
            
            # Get metric priority distribution
            priority_query = f"""
                SELECT metric_priority, COUNT(*) as count 
                FROM {self.table_name} 
                WHERE {where_clause} 
                GROUP BY metric_priority
            """
            priority_result = await self.execute_query(priority_query, params)
            priority_distribution = {row[0]: row[1] for row in priority_result}
            
            # Get average performance scores
            performance_query = f"""
                SELECT AVG(CAST(performance_score AS FLOAT)) as avg_performance
                FROM {self.table_name} 
                WHERE {where_clause} AND performance_score IS NOT NULL
            """
            performance_result = await self.execute_query(performance_query, params)
            avg_performance = performance_result[0][0] if performance_result else 0.0
            
            return {
                "total_metrics": total_count,
                "category_distribution": category_distribution,
                "priority_distribution": priority_distribution,
                "average_performance_score": round(avg_performance, 2),
                "org_id": org_id,
                "dept_id": dept_id
            }
            
        except Exception as e:
            logger.error(f"Error getting metrics stats: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error getting metrics stats: {e}")
            return {}
    
    # Health Check
    async def health_check(self) -> bool:
        """Check repository health by performing a simple query"""
        try:
            query = f"SELECT 1 FROM {self.table_name} LIMIT 1"
            result = await self.execute_query(query)
            return bool(result)
        except Exception as e:
            logger.error(f"Repository health check failed: {e}")
            return False
    
    # ========================================================================
    # PERFORMANCE TRACKING OPERATIONS
    # ========================================================================
    
    async def update_performance_metrics(
        self,
        metrics_id: str,
        performance_data: Dict[str, Any]
    ) -> bool:
        """Update performance metrics data"""
        try:
            metrics = await self.get_metrics_by_id(metrics_id)
            if not metrics:
                return False
            
            # Update performance metrics fields
            for key, value in performance_data.items():
                if hasattr(metrics.performance_metrics, key):
                    setattr(metrics.performance_metrics, key, value)
            
            # Recalculate performance score
            scores = []
            if metrics.performance_metrics.generation_time_ms > 0:
                # Lower time is better (inverse scoring)
                time_score = max(0, 100 - (metrics.performance_metrics.generation_time_ms / 10))
                scores.append(time_score)
            
            if metrics.performance_metrics.memory_usage_mb > 0:
                # Lower memory usage is better
                memory_score = max(0, 100 - (metrics.performance_metrics.memory_usage_mb / 10))
                scores.append(memory_score)
            
            if metrics.performance_metrics.cpu_usage_percent > 0:
                # Lower CPU usage is better
                cpu_score = max(0, 100 - metrics.performance_metrics.cpu_usage_percent)
                scores.append(cpu_score)
            
            if scores:
                metrics.performance_metrics.performance_score = sum(scores) / len(scores)
            
            # Update performance trend
            if metrics.performance_metrics.performance_score >= 90:
                metrics.performance_metrics.performance_trend = PerformanceTrend.EXCELLENT
            elif metrics.performance_metrics.performance_score >= 80:
                metrics.performance_metrics.performance_trend = PerformanceTrend.GOOD
            elif metrics.performance_metrics.performance_score >= 70:
                metrics.performance_metrics.performance_trend = PerformanceTrend.AVERAGE
            elif metrics.performance_metrics.performance_score >= 60:
                metrics.performance_metrics.performance_trend = PerformanceTrend.BELOW_AVERAGE
            else:
                metrics.performance_metrics.performance_trend = PerformanceTrend.POOR
            
            await self.update_metrics(metrics)
            logger.info(f"Updated performance metrics for {metrics_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")
            return False
    
    async def get_metrics_by_performance_trend(
        self,
        performance_trend: PerformanceTrend,
        limit: int = 100
    ) -> List[CertificateMetrics]:
        """Get metrics by performance trend"""
        try:
            all_metrics = await self.get_all_metrics(limit=1000)
            
            filtered_metrics = []
            for metrics in all_metrics:
                if metrics.performance_metrics.performance_trend == performance_trend:
                    filtered_metrics.append(metrics)
                    if len(filtered_metrics) >= limit:
                        break
            
            return filtered_metrics
            
        except Exception as e:
            logger.error(f"Error getting metrics by performance trend: {e}")
            return []
    
    async def get_performance_statistics(self) -> Dict[str, Any]:
        """Get performance metrics statistics"""
        try:
            all_metrics = await self.get_all_metrics(limit=1000)
            
            total_metrics = len(all_metrics)
            trend_counts = {trend: 0 for trend in PerformanceTrend}
            total_generation_time = 0
            total_memory_usage = 0
            total_cpu_usage = 0
            total_performance_score = 0
            
            for metrics in all_metrics:
                trend_counts[metrics.performance_metrics.performance_trend] += 1
                total_generation_time += metrics.performance_metrics.generation_time_ms
                total_memory_usage += metrics.performance_metrics.memory_usage_mb
                total_cpu_usage += metrics.performance_metrics.cpu_usage_percent
                total_performance_score += metrics.performance_metrics.performance_score
            
            return {
                "total_metrics": total_metrics,
                "performance_trend_distribution": trend_counts,
                "average_generation_time_ms": total_generation_time / total_metrics if total_metrics > 0 else 0,
                "average_memory_usage_mb": total_memory_usage / total_metrics if total_metrics > 0 else 0,
                "average_cpu_usage_percent": total_cpu_usage / total_metrics if total_metrics > 0 else 0,
                "average_performance_score": total_performance_score / total_metrics if total_metrics > 0 else 0,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting performance statistics: {e}")
            return {}
    
    # ========================================================================
    # USAGE ANALYTICS OPERATIONS
    # ========================================================================
    
    async def update_usage_analytics(
        self,
        metrics_id: str,
        usage_data: Dict[str, Any]
    ) -> bool:
        """Update usage analytics data"""
        try:
            metrics = await self.get_metrics_by_id(metrics_id)
            if not metrics:
                return False
            
            # Update usage analytics fields
            for key, value in usage_data.items():
                if hasattr(metrics.usage_analytics, key):
                    setattr(metrics.usage_analytics, key, value)
            
            # Recalculate engagement score
            scores = []
            
            # User activity score
            if metrics.usage_analytics.active_users_count > 0:
                user_score = min(100, (metrics.usage_analytics.active_users_count / 100) * 100)
                scores.append(user_score)
            
            # Session duration score
            if metrics.usage_analytics.avg_session_duration_minutes > 0:
                duration_score = min(100, (metrics.usage_analytics.avg_session_duration_minutes / 60) * 100)
                scores.append(duration_score)
            
            # Feature adoption score
            if metrics.usage_analytics.features_used_count > 0:
                feature_score = min(100, (metrics.usage_analytics.features_used_count / 10) * 100)
                scores.append(feature_score)
            
            if scores:
                metrics.usage_analytics.engagement_score = sum(scores) / len(scores)
            
            await self.update_metrics(metrics)
            logger.info(f"Updated usage analytics for {metrics_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating usage analytics: {e}")
            return False
    
    async def get_metrics_by_engagement_level(
        self,
        engagement_level: str,
        limit: int = 100
    ) -> List[CertificateMetrics]:
        """Get metrics by engagement level"""
        try:
            all_metrics = await self.get_all_metrics(limit=1000)
            
            filtered_metrics = []
            for metrics in all_metrics:
                if metrics.usage_analytics.engagement_level == engagement_level:
                    filtered_metrics.append(metrics)
                    if len(filtered_metrics) >= limit:
                        break
            
            return filtered_metrics
            
        except Exception as e:
            logger.error(f"Error getting metrics by engagement level: {e}")
            return []
    
    async def get_usage_analytics_statistics(self) -> Dict[str, Any]:
        """Get usage analytics statistics"""
        try:
            all_metrics = await self.get_all_metrics(limit=1000)
            
            total_metrics = len(all_metrics)
            engagement_level_counts = {"low": 0, "medium": 0, "high": 0, "very_high": 0}
            total_active_users = 0
            total_session_duration = 0
            total_features_used = 0
            total_engagement_score = 0
            
            for metrics in all_metrics:
                engagement_level_counts[metrics.usage_analytics.engagement_level] += 1
                total_active_users += metrics.usage_analytics.active_users_count
                total_session_duration += metrics.usage_analytics.avg_session_duration_minutes
                total_features_used += metrics.usage_analytics.features_used_count
                total_engagement_score += metrics.usage_analytics.engagement_score
            
            return {
                "total_metrics": total_metrics,
                "engagement_level_distribution": engagement_level_counts,
                "average_active_users": total_active_users / total_metrics if total_metrics > 0 else 0,
                "average_session_duration_minutes": total_session_duration / total_metrics if total_metrics > 0 else 0,
                "average_features_used": total_features_used / total_metrics if total_metrics > 0 else 0,
                "average_engagement_score": total_engagement_score / total_metrics if total_metrics > 0 else 0,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting usage analytics statistics: {e}")
            return {}
    
    # ========================================================================
    # QUALITY MONITORING OPERATIONS
    # ========================================================================
    
    async def update_quality_analytics(
        self,
        metrics_id: str,
        quality_data: Dict[str, Any]
    ) -> bool:
        """Update quality analytics data"""
        try:
            metrics = await self.get_metrics_by_id(metrics_id)
            if not metrics:
                return False
            
            # Update quality analytics fields
            for key, value in quality_data.items():
                if hasattr(metrics.quality_analytics, key):
                    setattr(metrics.quality_analytics, key, value)
            
            # Recalculate overall quality score
            scores = [
                metrics.quality_analytics.data_quality_score,
                metrics.quality_analytics.process_quality_score,
                metrics.quality_analytics.output_quality_score,
                metrics.quality_analytics.user_satisfaction_score
            ]
            metrics.quality_analytics.overall_quality_score = sum(scores) / len(scores)
            
            # Update quality level
            if metrics.quality_analytics.overall_quality_score >= 90:
                metrics.quality_analytics.quality_level = "excellent"
            elif metrics.quality_analytics.overall_quality_score >= 80:
                metrics.quality_analytics.quality_level = "good"
            elif metrics.quality_analytics.overall_quality_score >= 70:
                metrics.quality_analytics.quality_level = "average"
            elif metrics.quality_analytics.overall_quality_score >= 60:
                metrics.quality_analytics.quality_level = "below_average"
            else:
                metrics.quality_analytics.quality_level = "poor"
            
            await self.update_metrics(metrics)
            logger.info(f"Updated quality analytics for {metrics_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating quality analytics: {e}")
            return False
    
    async def get_metrics_by_quality_level(
        self,
        quality_level: str,
        limit: int = 100
    ) -> List[CertificateMetrics]:
        """Get metrics by quality level"""
        try:
            all_metrics = await self.get_all_metrics(limit=1000)
            
            filtered_metrics = []
            for metrics in all_metrics:
                if metrics.quality_analytics.quality_level == quality_level:
                    filtered_metrics.append(metrics)
                    if len(filtered_metrics) >= limit:
                        break
            
            return filtered_metrics
            
        except Exception as e:
            logger.error(f"Error getting metrics by quality level: {e}")
            return []
    
    async def get_quality_analytics_statistics(self) -> Dict[str, Any]:
        """Get quality analytics statistics"""
        try:
            all_metrics = await self.get_all_metrics(limit=1000)
            
            total_metrics = len(all_metrics)
            quality_level_counts = {"poor": 0, "below_average": 0, "average": 0, "good": 0, "excellent": 0}
            total_data_quality = 0
            total_process_quality = 0
            total_output_quality = 0
            total_user_satisfaction = 0
            total_overall_quality = 0
            
            for metrics in all_metrics:
                quality_level_counts[metrics.quality_analytics.quality_level] += 1
                total_data_quality += metrics.quality_analytics.data_quality_score
                total_process_quality += metrics.quality_analytics.process_quality_score
                total_output_quality += metrics.quality_analytics.output_quality_score
                total_user_satisfaction += metrics.quality_analytics.user_satisfaction_score
                total_overall_quality += metrics.quality_analytics.overall_quality_score
            
            return {
                "total_metrics": total_metrics,
                "quality_level_distribution": quality_level_counts,
                "average_data_quality_score": total_data_quality / total_metrics if total_metrics > 0 else 0,
                "average_process_quality_score": total_process_quality / total_metrics if total_metrics > 0 else 0,
                "average_output_quality_score": total_output_quality / total_metrics if total_metrics > 0 else 0,
                "average_user_satisfaction_score": total_user_satisfaction / total_metrics if total_metrics > 0 else 0,
                "average_overall_quality_score": total_overall_quality / total_metrics if total_metrics > 0 else 0,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting quality analytics statistics: {e}")
            return {}
    
    # ========================================================================
    # BUSINESS ANALYTICS OPERATIONS
    # ========================================================================
    
    async def update_business_metrics(
        self,
        metrics_id: str,
        business_data: Dict[str, Any]
    ) -> bool:
        """Update business metrics data"""
        try:
            metrics = await self.get_metrics_by_id(metrics_id)
            if not metrics:
                return False
            
            # Update business metrics fields
            for key, value in business_data.items():
                if hasattr(metrics.business_metrics, key):
                    setattr(metrics.business_metrics, key, value)
            
            # Recalculate overall business score
            scores = [
                metrics.business_metrics.business_value_score,
                metrics.business_metrics.cost_efficiency_score,
                metrics.business_metrics.risk_mitigation_score,
                metrics.business_metrics.strategic_alignment_score
            ]
            metrics.business_metrics.overall_business_score = sum(scores) / len(scores)
            
            # Update business impact level
            if metrics.business_metrics.overall_business_score >= 90:
                metrics.business_metrics.business_impact_level = "high"
            elif metrics.business_metrics.overall_business_score >= 70:
                metrics.business_metrics.business_impact_level = "medium"
            else:
                metrics.business_metrics.business_impact_level = "low"
            
            await self.update_metrics(metrics)
            logger.info(f"Updated business metrics for {metrics_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating business metrics: {e}")
            return False
    
    async def get_metrics_by_business_impact(
        self,
        business_impact_level: str,
        limit: int = 100
    ) -> List[CertificateMetrics]:
        """Get metrics by business impact level"""
        try:
            all_metrics = await self.get_all_metrics(limit=1000)
            
            filtered_metrics = []
            for metrics in all_metrics:
                if metrics.business_metrics.business_impact_level == business_impact_level:
                    filtered_metrics.append(metrics)
                    if len(filtered_metrics) >= limit:
                        break
            
            return filtered_metrics
            
        except Exception as e:
            logger.error(f"Error getting metrics by business impact: {e}")
            return []
    
    async def get_business_metrics_statistics(self) -> Dict[str, Any]:
        """Get business metrics statistics"""
        try:
            all_metrics = await self.get_all_metrics(limit=1000)
            
            total_metrics = len(all_metrics)
            business_impact_counts = {"low": 0, "medium": 0, "high": 0}
            total_business_value = 0
            total_cost_efficiency = 0
            total_risk_mitigation = 0
            total_strategic_alignment = 0
            total_overall_business = 0
            
            for metrics in all_metrics:
                business_impact_counts[metrics.business_metrics.business_impact_level] += 1
                total_business_value += metrics.business_metrics.business_value_score
                total_cost_efficiency += metrics.business_metrics.cost_efficiency_score
                total_risk_mitigation += metrics.business_metrics.risk_mitigation_score
                total_strategic_alignment += metrics.business_metrics.strategic_alignment_score
                total_overall_business += metrics.business_metrics.overall_business_score
            
            return {
                "total_metrics": total_metrics,
                "business_impact_distribution": business_impact_counts,
                "average_business_value_score": total_business_value / total_metrics if total_metrics > 0 else 0,
                "average_cost_efficiency_score": total_cost_efficiency / total_metrics if total_metrics > 0 else 0,
                "average_risk_mitigation_score": total_risk_mitigation / total_metrics if total_metrics > 0 else 0,
                "average_strategic_alignment_score": total_strategic_alignment / total_metrics if total_metrics > 0 else 0,
                "average_overall_business_score": total_overall_business / total_metrics if total_metrics > 0 else 0,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting business metrics statistics: {e}")
            return {}
    
    # ========================================================================
    # ENTERPRISE ANALYTICS OPERATIONS
    # ========================================================================
    
    async def update_enterprise_analytics(
        self,
        metrics_id: str,
        enterprise_data: Dict[str, Any]
    ) -> bool:
        """Update enterprise analytics data"""
        try:
            metrics = await self.get_metrics_by_id(metrics_id)
            if not metrics:
                return False
            
            # Update enterprise analytics fields
            for key, value in enterprise_data.items():
                if hasattr(metrics.enterprise_analytics, key):
                    setattr(metrics.enterprise_analytics, key, value)
            
            # Recalculate enterprise health score
            scores = [
                metrics.enterprise_analytics.sla_compliance_score,
                metrics.enterprise_analytics.scalability_score,
                metrics.enterprise_analytics.governance_score,
                metrics.enterprise_analytics.risk_management_score
            ]
            metrics.enterprise_analytics.enterprise_health_score = sum(scores) / len(scores)
            
            # Update enterprise maturity level
            if metrics.enterprise_analytics.enterprise_health_score >= 90:
                metrics.enterprise_analytics.enterprise_maturity_level = "mature"
            elif metrics.enterprise_analytics.enterprise_health_score >= 70:
                metrics.enterprise_analytics.enterprise_maturity_level = "developing"
            else:
                metrics.enterprise_analytics.enterprise_maturity_level = "emerging"
            
            await self.update_metrics(metrics)
            logger.info(f"Updated enterprise analytics for {metrics_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating enterprise analytics: {e}")
            return False
    
    async def get_metrics_by_enterprise_maturity(
        self,
        enterprise_maturity_level: str,
        limit: int = 100
    ) -> List[CertificateMetrics]:
        """Get metrics by enterprise maturity level"""
        try:
            all_metrics = await self.get_all_metrics(limit=1000)
            
            filtered_metrics = []
            for metrics in all_metrics:
                if metrics.enterprise_analytics.enterprise_maturity_level == enterprise_maturity_level:
                    filtered_metrics.append(metrics)
                    if len(filtered_metrics) >= limit:
                        break
            
            return filtered_metrics
            
        except Exception as e:
            logger.error(f"Error getting metrics by enterprise maturity: {e}")
            return []
    
    async def get_enterprise_analytics_statistics(self) -> Dict[str, Any]:
        """Get enterprise analytics statistics"""
        try:
            all_metrics = await self.get_all_metrics(limit=1000)
            
            total_metrics = len(all_metrics)
            enterprise_maturity_counts = {"emerging": 0, "developing": 0, "mature": 0}
            total_sla_compliance = 0
            total_scalability = 0
            total_governance = 0
            total_risk_management = 0
            total_enterprise_health = 0
            
            for metrics in all_metrics:
                enterprise_maturity_counts[metrics.enterprise_analytics.enterprise_maturity_level] += 1
                total_sla_compliance += metrics.enterprise_analytics.sla_compliance_score
                total_scalability += metrics.enterprise_analytics.scalability_score
                total_governance += metrics.enterprise_analytics.governance_score
                total_risk_management += metrics.enterprise_analytics.risk_management_score
                total_enterprise_health += metrics.enterprise_analytics.enterprise_health_score
            
            return {
                "total_metrics": total_metrics,
                "enterprise_maturity_distribution": enterprise_maturity_counts,
                "average_sla_compliance_score": total_sla_compliance / total_metrics if total_metrics > 0 else 0,
                "average_scalability_score": total_scalability / total_metrics if total_metrics > 0 else 0,
                "average_governance_score": total_governance / total_metrics if total_metrics > 0 else 0,
                "average_risk_management_score": total_risk_management / total_metrics if total_metrics > 0 else 0,
                "average_enterprise_health_score": total_enterprise_health / total_metrics if total_metrics > 0 else 0,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting enterprise analytics statistics: {e}")
            return {}
    
    # ========================================================================
    # REAL-TIME METRICS OPERATIONS
    # ========================================================================
    
    async def update_real_time_metrics(
        self,
        metrics_id: str,
        real_time_data: Dict[str, Any]
    ) -> bool:
        """Update real-time metrics data"""
        try:
            metrics = await self.get_metrics_by_id(metrics_id)
            if not metrics:
                return False
            
            # Update real-time metrics fields
            for key, value in real_time_data.items():
                if hasattr(metrics.real_time_metrics, key):
                    setattr(metrics.real_time_metrics, key, value)
            
            # Recalculate real-time health score
            scores = [
                metrics.real_time_metrics.system_health_score,
                metrics.real_time_metrics.performance_health_score,
                metrics.real_time_metrics.security_health_score,
                metrics.real_time_metrics.availability_health_score
            ]
            metrics.real_time_metrics.real_time_health_score = sum(scores) / len(scores)
            
            # Update alert level based on health score
            if metrics.real_time_metrics.real_time_health_score >= 90:
                metrics.real_time_metrics.alert_level = AlertLevel.NONE
            elif metrics.real_time_metrics.real_time_health_score >= 80:
                metrics.real_time_metrics.alert_level = AlertLevel.LOW
            elif metrics.real_time_metrics.real_time_health_score >= 70:
                metrics.real_time_metrics.alert_level = AlertLevel.MEDIUM
            elif metrics.real_time_metrics.real_time_health_score >= 60:
                metrics.real_time_metrics.alert_level = AlertLevel.HIGH
            else:
                metrics.real_time_metrics.alert_level = AlertLevel.CRITICAL
            
            await self.update_metrics(metrics)
            logger.info(f"Updated real-time metrics for {metrics_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating real-time metrics: {e}")
            return False
    
    async def get_metrics_by_alert_level(
        self,
        alert_level: AlertLevel,
        limit: int = 100
    ) -> List[CertificateMetrics]:
        """Get metrics by alert level"""
        try:
            all_metrics = await self.get_all_metrics(limit=1000)
            
            filtered_metrics = []
            for metrics in all_metrics:
                if metrics.real_time_metrics.alert_level == alert_level:
                    filtered_metrics.append(metrics)
                    if len(filtered_metrics) >= limit:
                        break
            
            return filtered_metrics
            
        except Exception as e:
            logger.error(f"Error getting metrics by alert level: {e}")
            return []
    
    async def get_real_time_metrics_statistics(self) -> Dict[str, Any]:
        """Get real-time metrics statistics"""
        try:
            all_metrics = await self.get_all_metrics(limit=1000)
            
            total_metrics = len(all_metrics)
            alert_level_counts = {level: 0 for level in AlertLevel}
            total_system_health = 0
            total_performance_health = 0
            total_security_health = 0
            total_availability_health = 0
            total_real_time_health = 0
            
            for metrics in all_metrics:
                alert_level_counts[metrics.real_time_metrics.alert_level] += 1
                total_system_health += metrics.real_time_metrics.system_health_score
                total_performance_health += metrics.real_time_metrics.performance_health_score
                total_security_health += metrics.real_time_metrics.security_health_score
                total_availability_health += metrics.real_time_metrics.availability_health_score
                total_real_time_health += metrics.real_time_metrics.real_time_health_score
            
            return {
                "total_metrics": total_metrics,
                "alert_level_distribution": alert_level_counts,
                "average_system_health_score": total_system_health / total_metrics if total_metrics > 0 else 0,
                "average_performance_health_score": total_performance_health / total_metrics if total_metrics > 0 else 0,
                "average_security_health_score": total_security_health / total_metrics if total_metrics > 0 else 0,
                "average_availability_health_score": total_availability_health / total_metrics if total_metrics > 0 else 0,
                "average_real_time_health_score": total_real_time_health / total_metrics if total_metrics > 0 else 0,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time metrics statistics: {e}")
            return {}
    
    # ========================================================================
    # COMPREHENSIVE ANALYTICS OPERATIONS
    # ========================================================================
    
    async def get_comprehensive_metrics_analytics(
        self,
        org_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get comprehensive metrics analytics across all components"""
        try:
            all_metrics = await self.get_all_metrics(limit=1000)
            
            # Filter by date range if provided
            if start_date and end_date:
                all_metrics = [
                    m for m in all_metrics
                    if start_date <= m.created_at <= end_date
                ]
            
            # Get statistics from all components
            performance_stats = await self.get_performance_statistics()
            usage_stats = await self.get_usage_analytics_statistics()
            quality_stats = await self.get_quality_analytics_statistics()
            business_stats = await self.get_business_metrics_statistics()
            enterprise_stats = await self.get_enterprise_analytics_statistics()
            real_time_stats = await self.get_real_time_metrics_statistics()
            
            # Calculate overall metrics score
            total_metrics = len(all_metrics)
            total_overall_score = 0
            
            for metrics in all_metrics:
                total_overall_score += metrics.overall_metrics_score
            
            average_overall_score = total_overall_score / total_metrics if total_metrics > 0 else 0
            
            return {
                "total_metrics": total_metrics,
                "overall_metrics_score": round(average_overall_score, 2),
                "performance_analytics": performance_stats,
                "usage_analytics": usage_stats,
                "quality_analytics": quality_stats,
                "business_analytics": business_stats,
                "enterprise_analytics": enterprise_stats,
                "real_time_analytics": real_time_stats,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive metrics analytics: {e}")
            return {}
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _model_to_dict(self, metrics: CertificateMetrics) -> Dict[str, Any]:
        """Convert Pydantic model to database dictionary."""
        return metrics.model_dump()
    
    def _dict_to_model(self, data: Dict[str, Any]) -> CertificateMetrics:
        """Convert database dictionary to Pydantic model."""
        return CertificateMetrics(**data)
    
    # ========================================================================
    # CONNECTION MANAGER METHODS
    # ========================================================================
    
    async def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute a query using the connection manager."""
        try:
            if query.strip().upper().startswith('SELECT'):
                return await self.connection_manager.execute_query(query, params or {})
            else:
                await self.connection_manager.execute_update(query, params or {})
                return []
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            raise
    
    async def fetch_one(self, query: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Fetch a single row using the connection manager."""
        try:
            result = await self.connection_manager.execute_query(query, params or {})
            return result[0] if result and len(result) > 0 else None
        except Exception as e:
            logger.error(f"Failed to fetch one: {e}")
            return None
