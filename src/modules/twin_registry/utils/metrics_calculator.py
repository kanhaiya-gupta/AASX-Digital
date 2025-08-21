"""
Database-Based Metrics Calculator for Twin Registry

Provides real-time calculations of metrics based on actual database data
instead of hardcoded values.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone, timedelta
from pathlib import Path
import sqlite3
import json

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """
    Database-based metrics calculator for twin registry.
    
    Calculates real metrics based on actual database data including
    uptime, error rates, data volume, and historical trends.
    """
    
    def __init__(self, db_path: str = "data/aasx_database.db"):
        """
        Initialize the metrics calculator.
        
        Args:
            db_path: Path to the database file
        """
        self.db_path = db_path
        self._ensure_database_connection()
    
    def _ensure_database_connection(self):
        """Ensure database connection is available."""
        try:
            # Test connection
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("SELECT 1")
            logger.debug(f"Database connection established: {self.db_path}")
        except Exception as e:
            logger.warning(f"Database connection failed: {e}")
    
    async def calculate_uptime(self, registry_id: str) -> float:
        """
        Calculate actual uptime percentage from registry creation to now.
        
        Args:
            registry_id: Registry identifier
            
        Returns:
            float: Uptime percentage (0.0 to 100.0)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get registry creation time
                cursor.execute(
                    "SELECT created_at, updated_at FROM twin_registry WHERE registry_id = ?",
                    (registry_id,)
                )
                result = cursor.fetchone()
                
                if not result:
                    return 0.0
                
                created_at_str, updated_at_str = result
                
                # Parse timestamps and ensure they are timezone-aware
                try:
                    # Handle both ISO format and SQLite datetime format
                    if 'Z' in created_at_str:
                        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    elif '+' in created_at_str:
                        created_at = datetime.fromisoformat(created_at_str)
                    else:
                        # SQLite datetime format - assume UTC
                        created_at = datetime.fromisoformat(created_at_str + '+00:00')
                    
                    if 'Z' in updated_at_str:
                        updated_at = datetime.fromisoformat(updated_at_str.replace('Z', '+00:00'))
                    elif '+' in updated_at_str:
                        updated_at = datetime.fromisoformat(updated_at_str)
                    else:
                        # SQLite datetime format - assume UTC
                        updated_at = datetime.fromisoformat(updated_at_str + '+00:00')
                        
                except ValueError:
                    # Fallback to current time
                    created_at = datetime.now(timezone.utc) - timedelta(hours=1)
                    updated_at = datetime.now(timezone.utc)
                
                # Calculate uptime (all datetimes are now timezone-aware)
                now = datetime.now(timezone.utc)
                total_time = (now - created_at).total_seconds()
                active_time = (updated_at - created_at).total_seconds()
                
                if total_time <= 0:
                    return 100.0
                
                uptime_percentage = (active_time / total_time) * 100
                return min(100.0, max(0.0, uptime_percentage))
                
        except Exception as e:
            logger.warning(f"Failed to calculate uptime for registry {registry_id}: {e}")
            return 0.0
    
    async def calculate_error_rate(self, registry_id: str) -> float:
        """
        Calculate error rate from sync errors and validation results.
        
        Args:
            registry_id: Registry identifier
            
        Returns:
            float: Error rate (0.0 to 1.0)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get error count from existing column
                cursor.execute(
                    "SELECT error_count FROM twin_registry WHERE registry_id = ?",
                    (registry_id,)
                )
                result = cursor.fetchone()
                
                if not result or not result[0]:
                    return 0.0
                
                error_count = int(result[0]) or 0
                
                # Get total operations count (approximate)
                cursor.execute(
                    "SELECT COUNT(*) FROM twin_registry_metrics WHERE registry_id = ?",
                    (registry_id,)
                )
                total_operations = cursor.fetchone()[0] or 1
                
                # Calculate error rate
                error_rate = error_count / total_operations
                return min(1.0, max(0.0, error_rate))
                
        except Exception as e:
            logger.warning(f"Failed to calculate error rate for registry {registry_id}: {e}")
            return 0.0
    
    async def calculate_data_volume(self, registry_id: str) -> float:
        """
        Calculate actual data volume from registry metadata.
        
        Args:
            registry_id: Registry identifier
            
        Returns:
            float: Data volume in MB
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get registry metadata from existing metadata column
                cursor.execute(
                    "SELECT metadata FROM twin_registry WHERE registry_id = ?",
                    (registry_id,)
                )
                result = cursor.fetchone()
                
                if not result or not result[0]:
                    return 0.0
                
                registry_metadata = result[0]
                total_volume_mb = 0.0
                
                # Parse metadata JSON to estimate data volume
                try:
                    metadata = json.loads(registry_metadata)
                    if isinstance(metadata, dict):
                        # Estimate based on metadata size
                        if "file_size_bytes" in metadata:
                            total_volume_mb += metadata["file_size_bytes"] / (1024 * 1024)
                        elif "data_points" in metadata:
                            # Estimate: 1KB per data point
                            total_volume_mb += (metadata["data_points"] * 1024) / (1024 * 1024)
                        elif "extracted_size_bytes" in metadata:
                            total_volume_mb += metadata["extracted_size_bytes"] / (1024 * 1024)
                except (json.JSONDecodeError, TypeError):
                    pass
                
                return round(total_volume_mb, 2)
                
        except Exception as e:
            logger.warning(f"Failed to calculate data volume for registry {registry_id}: {e}")
            return 0.0
    
    async def calculate_response_time(self, registry_id: str) -> float:
        """
        Calculate actual response time from registry timestamps.
        
        Args:
            registry_id: Registry identifier
            
        Returns:
            float: Response time in milliseconds
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get registry timestamps
                cursor.execute(
                    "SELECT created_at, updated_at FROM twin_registry WHERE registry_id = ?",
                    (registry_id,)
                )
                result = cursor.fetchone()
                
                if not result:
                    return 0.0
                
                created_at_str, updated_at_str = result
                
                # Calculate response time from creation to update
                if created_at_str and updated_at_str:
                    try:
                        # Handle both ISO format and SQLite datetime format
                        if 'Z' in created_at_str:
                            created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                        elif '+' in created_at_str:
                            created_at = datetime.fromisoformat(created_at_str)
                        else:
                            # SQLite datetime format - assume UTC
                            created_at = datetime.fromisoformat(created_at_str + '+00:00')
                        
                        if 'Z' in updated_at_str:
                            updated_at = datetime.fromisoformat(updated_at_str.replace('Z', '+00:00'))
                        elif '+' in updated_at_str:
                            updated_at = datetime.fromisoformat(updated_at_str)
                        else:
                            # SQLite datetime format - assume UTC
                            updated_at = datetime.fromisoformat(updated_at_str + '+00:00')
                        
                        response_time_ms = (updated_at - created_at).total_seconds() * 1000
                        return max(0.0, response_time_ms)
                    except ValueError:
                        pass
                
                return 0.0
                
        except Exception as e:
            logger.warning(f"Failed to calculate response time for registry {registry_id}: {e}")
            return 0.0
    
    async def calculate_transaction_count(self, registry_id: str) -> int:
        """
        Calculate actual transaction count from registry metadata.
        
        Args:
            registry_id: Registry identifier
            
        Returns:
            int: Number of transactions
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get registry metadata from existing metadata column
                cursor.execute(
                    "SELECT metadata FROM twin_registry WHERE registry_id = ?",
                    (registry_id,)
                )
                result = cursor.fetchone()
                
                if not result or not result[0]:
                    return 1  # Default to 1 for creation
                
                try:
                    metadata = json.loads(result[0])
                    if isinstance(metadata, dict):
                        # Count various types of operations
                        transaction_count = 0
                        
                        # Count extracted assets
                        if "extracted_assets" in metadata:
                            transaction_count += metadata["extracted_assets"]
                        
                        # Count output formats processed
                        if "output_formats" in metadata:
                            transaction_count += len(metadata["output_formats"])
                        
                        # Count documents extracted
                        if "documents_extracted" in metadata:
                            transaction_count += metadata["documents_extracted"]
                        
                        # Count relationships extracted
                        if "relationships_extracted" in metadata:
                            transaction_count += metadata["relationships_extracted"]
                        
                        return max(1, transaction_count)  # Minimum 1 transaction
                    
                    return 1
                    
                except (json.JSONDecodeError, TypeError):
                    return 1
                
        except Exception as e:
            logger.warning(f"Failed to calculate transaction count for registry {registry_id}: {e}")
            return 1
    
    async def calculate_user_interactions(self, registry_id: str) -> int:
        """
        Calculate user interaction count from registry updates and metadata.
        
        Args:
            registry_id: Registry identifier
            
        Returns:
            int: Number of user interactions
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get registry metadata and timestamps from existing columns
                cursor.execute(
                    "SELECT metadata, created_at, updated_at FROM twin_registry WHERE registry_id = ?",
                    (registry_id,)
                )
                result = cursor.fetchone()
                
                if not result:
                    return 1  # Default to 1 for creation
                
                metadata, created_at, updated_at = result
                interaction_count = 1  # Start with 1 for creation
                
                # Count interactions from metadata if available
                if metadata:
                    try:
                        metadata_dict = json.loads(metadata)
                        if isinstance(metadata_dict, dict):
                            # Count various interaction indicators
                            if "interaction_count" in metadata_dict:
                                interaction_count += metadata_dict["interaction_count"]
                            elif "update_count" in metadata_dict:
                                interaction_count += metadata_dict["update_count"]
                            elif "access_count" in metadata_dict:
                                interaction_count += metadata_dict["access_count"]
                    except (json.JSONDecodeError, TypeError):
                        pass
                
                # Count updates (rough estimate)
                if created_at and updated_at:
                    try:
                        # Handle both ISO format and SQLite datetime format
                        if 'Z' in created_at:
                            created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        elif '+' in created_at:
                            created_time = datetime.fromisoformat(created_at)
                        else:
                            # SQLite datetime format - assume UTC
                            created_time = datetime.fromisoformat(created_at + '+00:00')
                        
                        if 'Z' in updated_at:
                            updated_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                        elif '+' in updated_at:
                            updated_time = datetime.fromisoformat(updated_at)
                        else:
                            # SQLite datetime format - assume UTC
                            updated_time = datetime.fromisoformat(updated_at + '+00:00')
                        
                        # Estimate interactions based on time difference
                        time_diff_hours = (updated_time - created_time).total_seconds() / 3600
                        estimated_interactions = max(1, int(time_diff_hours * 0.5))  # 0.5 interactions per hour
                        interaction_count = max(interaction_count, estimated_interactions)
                    except ValueError:
                        pass
                
                return max(1, interaction_count)
                
        except Exception as e:
            logger.warning(f"Failed to calculate user interactions for registry {registry_id}: {e}")
            return 1
    
    async def calculate_health_score(self, registry_id: str) -> float:
        """
        Calculate comprehensive health score based on multiple factors.
        
        Args:
            registry_id: Registry identifier
            
        Returns:
            float: Health score (0.0 to 100.0)
        """
        try:
            # Get various metrics
            uptime = await self.calculate_uptime(registry_id)
            error_rate = await self.calculate_error_rate(registry_id)
            response_time = await self.calculate_response_time(registry_id)
            
            # Base score
            base_score = 50.0
            
            # Uptime contribution (0-25 points)
            uptime_score = (uptime / 100.0) * 25.0
            
            # Error rate contribution (0-15 points)
            error_score = (1.0 - error_rate) * 15.0
            
            # Response time contribution (0-10 points)
            if response_time < 1000:  # Less than 1 second
                response_score = 10.0
            elif response_time < 5000:  # Less than 5 seconds
                response_score = 7.0
            elif response_time < 10000:  # Less than 10 seconds
                response_score = 4.0
            else:
                response_score = 1.0
            
            # Calculate final score
            final_score = base_score + uptime_score + error_score + response_score
            
            return min(100.0, max(0.0, final_score))
            
        except Exception as e:
            logger.warning(f"Failed to calculate health score for registry {registry_id}: {e}")
            return 50.0
    
    async def get_historical_trends(self, registry_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get historical trends for a registry.
        
        Args:
            registry_id: Registry identifier
            days: Number of days to look back
            
        Returns:
            Dict containing historical trend data
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get metrics over time
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
                cutoff_str = cutoff_date.isoformat()
                
                cursor.execute(
                    """
                    SELECT timestamp, health_score, response_time_ms, error_rate
                    FROM twin_registry_metrics 
                    WHERE registry_id = ? AND timestamp >= ?
                    ORDER BY timestamp
                    """,
                    (registry_id, cutoff_str)
                )
                
                results = cursor.fetchall()
                
                if not results:
                    return {"error": "No historical data available"}
                
                # Process trends
                timestamps = []
                health_scores = []
                response_times = []
                error_rates = []
                
                for row in results:
                    timestamp, health_score, response_time, error_rate = row
                    timestamps.append(timestamp)
                    health_scores.append(health_score or 0)
                    response_times.append(response_time or 0)
                    error_rates.append(error_rate or 0)
                
                # Calculate trends
                health_trend = self._calculate_trend(health_scores)
                response_trend = self._calculate_trend(response_times)
                error_trend = self._calculate_trend(error_rates)
                
                return {
                    "registry_id": registry_id,
                    "period_days": days,
                    "data_points": len(results),
                    "trends": {
                        "health_score": health_trend,
                        "response_time": response_trend,
                        "error_rate": error_trend
                    },
                    "current_values": {
                        "health_score": health_scores[-1] if health_scores else 0,
                        "response_time_ms": response_times[-1] if response_times else 0,
                        "error_rate": error_rates[-1] if error_rates else 0
                    },
                    "averages": {
                        "health_score": sum(health_scores) / len(health_scores) if health_scores else 0,
                        "response_time_ms": sum(response_times) / len(response_times) if response_times else 0,
                        "error_rate": sum(error_rates) / len(error_rates) if error_rates else 0
                    }
                }
                
        except Exception as e:
            logger.warning(f"Failed to get historical trends for registry {registry_id}: {e}")
            return {"error": str(e)}
    
    def _calculate_trend(self, values: List[float]) -> str:
        """
        Calculate trend direction from a list of values.
        
        Args:
            values: List of numeric values
            
        Returns:
            str: Trend direction ("increasing", "decreasing", "stable")
        """
        if len(values) < 2:
            return "stable"
        
        # Calculate slope
        x_values = list(range(len(values)))
        n = len(values)
        
        sum_x = sum(x_values)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(x_values, values))
        sum_x2 = sum(x * x for x in x_values)
        
        if n * sum_x2 - sum_x * sum_x == 0:
            return "stable"
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Determine trend
        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"
    
    async def get_registry_summary_metrics(self) -> Dict[str, Any]:
        """
        Get summary metrics for all registries.
        
        Returns:
            Dict containing summary metrics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get basic counts
                cursor.execute("SELECT COUNT(*) FROM twin_registry")
                total_registries = cursor.fetchone()[0] or 0
                
                # Use lifecycle_status instead of processing_status
                cursor.execute("SELECT COUNT(*) FROM twin_registry WHERE lifecycle_status = 'active'")
                active_registries = cursor.fetchone()[0] or 0
                
                cursor.execute("SELECT COUNT(*) FROM twin_registry WHERE lifecycle_status = 'inactive'")
                inactive_registries = cursor.fetchone()[0] or 0
                
                cursor.execute("SELECT COUNT(*) FROM twin_registry_metrics")
                total_metrics = cursor.fetchone()[0] or 0
                
                # Calculate percentages
                active_rate = (active_registries / total_registries * 100) if total_registries > 0 else 0
                inactive_rate = (inactive_registries / total_registries * 100) if total_registries > 0 else 0
                metrics_coverage = (total_metrics / total_registries * 100) if total_registries > 0 else 0
                
                return {
                    "total_registries": total_registries,
                    "active_registries": active_registries,
                    "inactive_registries": inactive_registries,
                    "total_metrics": total_metrics,
                    "active_rate_percent": round(active_rate, 2),
                    "inactive_rate_percent": round(inactive_rate, 2),
                    "metrics_coverage_percent": round(metrics_coverage, 2)
                }
                
        except Exception as e:
            logger.warning(f"Failed to get registry summary metrics: {e}")
            return {"error": str(e)}
    
    async def calculate_registry_metrics(self, registry_id: str) -> Dict[str, Any]:
        """
        Calculate all metrics for a specific registry.
        
        Args:
            registry_id: Registry identifier
            
        Returns:
            Dict containing all calculated metrics
        """
        try:
            return {
                "uptime_percentage": await self.calculate_uptime(registry_id),
                "error_rate": await self.calculate_error_rate(registry_id),
                "data_volume_mb": await self.calculate_data_volume(registry_id),
                "response_time_ms": await self.calculate_response_time(registry_id),
                "transaction_count": await self.calculate_transaction_count(registry_id),
                "user_interaction_count": await self.calculate_user_interactions(registry_id),
                "health_score": await self.calculate_health_score(registry_id)
            }
        except Exception as e:
            logger.warning(f"Failed to calculate registry metrics for {registry_id}: {e}")
            return {
                "uptime_percentage": 0.0,
                "error_rate": 0.0,
                "data_volume_mb": 0.0,
                "response_time_ms": 0.0,
                "transaction_count": 0,
                "user_interaction_count": 0,
                "health_score": 0.0
            }


# Convenience function for quick metrics calculation
async def calculate_registry_metrics(registry_id: str, db_path: str = "data/aasx_database.db") -> Dict[str, Any]:
    """
    Quick function to calculate all metrics for a registry.
    
    Args:
        registry_id: Registry identifier
        db_path: Path to database file
        
    Returns:
        Dict containing all calculated metrics
    """
    calculator = MetricsCalculator(db_path)
    
    return {
        "uptime_percentage": await calculator.calculate_uptime(registry_id),
        "error_rate": await calculator.calculate_error_rate(registry_id),
        "data_volume_mb": await calculator.calculate_data_volume(registry_id),
        "response_time_ms": await calculator.calculate_response_time(registry_id),
        "transaction_count": await calculator.calculate_transaction_count(registry_id),
        "user_interaction_count": await calculator.calculate_user_interactions(registry_id),
        "health_score": await calculator.calculate_health_score(registry_id)
    }
