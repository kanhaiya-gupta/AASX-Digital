"""
AASX Processing Metrics Repository

Data access layer for AASX processing metrics operations.
Uses the engine ConnectionManager for database access with async support.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import select, update, delete, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.engine.database.connection_manager import ConnectionManager
from src.engine.database.schema.modules.aasx_etl import AasxProcessingMetricsTable
from ..models.aasx_processing_metrics import AasxProcessingMetrics


class AasxProcessingMetricsRepository:
    """
    Repository for AASX processing metrics operations.
    
    Provides async CRUD operations and analytics queries
    for the aasx_processing_metrics table.
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        """
        Initialize repository with connection manager.
        
        Args:
            connection_manager: Engine connection manager instance
        """
        self.connection_manager = connection_manager
        self.table = AasxProcessingMetricsTable
    
    async def create(self, metrics: AasxProcessingMetrics) -> bool:
        """
        Create a new AASX processing metrics record.
        
        Args:
            metrics: AASX processing metrics model instance
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            async with self.connection_manager.get_session() as session:
                # Convert Pydantic model to database dict
                db_data = self._model_to_dict(metrics)
                
                # Create database record
                db_record = self.table(**db_data)
                session.add(db_record)
                await session.commit()
                
                return True
                
        except SQLAlchemyError as e:
            print(f"Error creating AASX processing metrics record: {e}")
            return False
    
    async def get_by_id(self, metric_id: int) -> Optional[AasxProcessingMetrics]:
        """
        Get AASX processing metrics record by metric ID.
        
        Args:
            metric_id: Unique metric identifier
            
        Returns:
            Optional[AasxProcessingMetrics]: AASX processing metrics model or None
        """
        try:
            async with self.connection_manager.get_session() as session:
                query = select(self.table).where(self.table.metric_id == metric_id)
                result = await session.execute(query)
                db_record = result.scalar_one_or_none()
                
                if db_record:
                    return self._dict_to_model(db_record.__dict__)
                return None
                
        except SQLAlchemyError as e:
            print(f"Error retrieving AASX processing metrics record: {e}")
            return None
    
    async def get_by_job_id(self, job_id: str) -> List[AasxProcessingMetrics]:
        """
        Get all metrics records for a specific job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            List[AasxProcessingMetrics]: List of AASX processing metrics models
        """
        try:
            async with self.connection_manager.get_session() as session:
                query = select(self.table).where(self.table.job_id == job_id).order_by(desc(self.table.timestamp))
                result = await session.execute(query)
                db_records = result.scalars().all()
                
                return [self._dict_to_model(record.__dict__) for record in db_records]
                
        except SQLAlchemyError as e:
            print(f"Error retrieving AASX processing metrics by job ID: {e}")
            return []
    
    async def get_latest_by_job_id(self, job_id: str) -> Optional[AasxProcessingMetrics]:
        """
        Get the latest metrics record for a specific job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Optional[AasxProcessingMetrics]: Latest AASX processing metrics model or None
        """
        try:
            async with self.connection_manager.get_session() as session:
                query = select(self.table).where(self.table.job_id == job_id).order_by(desc(self.table.timestamp)).limit(1)
                result = await session.execute(query)
                db_record = result.scalar_one_or_none()
                
                if db_record:
                    return self._dict_to_model(db_record.__dict__)
                return None
                
        except SQLAlchemyError as e:
            print(f"Error retrieving latest AASX processing metrics: {e}")
            return None
    
    async def get_by_timestamp_range(self, start_timestamp: str, end_timestamp: str, job_id: Optional[str] = None) -> List[AasxProcessingMetrics]:
        """
        Get metrics records within a timestamp range.
        
        Args:
            start_timestamp: Start timestamp in ISO format
            end_timestamp: End timestamp in ISO format
            job_id: Optional job ID to filter by
            
        Returns:
            List[AasxProcessingMetrics]: List of AASX processing metrics models
        """
        try:
            async with self.connection_manager.get_session() as session:
                query = select(self.table).where(
                    and_(
                        self.table.timestamp >= start_timestamp,
                        self.table.timestamp <= end_timestamp
                    )
                )
                
                if job_id:
                    query = query.where(self.table.job_id == job_id)
                
                query = query.order_by(desc(self.table.timestamp))
                result = await session.execute(query)
                db_records = result.scalars().all()
                
                return [self._dict_to_model(record.__dict__) for record in db_records]
                
        except SQLAlchemyError as e:
            print(f"Error retrieving AASX processing metrics by timestamp range: {e}")
            return []
    
    async def get_by_health_score_range(self, min_score: int, max_score: int, job_id: Optional[str] = None) -> List[AasxProcessingMetrics]:
        """
        Get metrics records within a health score range.
        
        Args:
            min_score: Minimum health score
            max_score: Maximum health score
            job_id: Optional job ID to filter by
            
        Returns:
            List[AasxProcessingMetrics]: List of AASX processing metrics models
        """
        try:
            async with self.connection_manager.get_session() as session:
                query = select(self.table).where(
                    and_(
                        self.table.health_score >= min_score,
                        self.table.health_score <= max_score
                    )
                )
                
                if job_id:
                    query = query.where(self.table.job_id == job_id)
                
                query = query.order_by(desc(self.table.timestamp))
                result = await session.execute(query)
                db_records = result.scalars().all()
                
                return [self._dict_to_model(record.__dict__) for record in db_records]
                
        except SQLAlchemyError as e:
            print(f"Error retrieving AASX processing metrics by health score range: {e}")
            return []
    
    async def update(self, metrics: AasxProcessingMetrics) -> bool:
        """
        Update an existing AASX processing metrics record.
        
        Args:
            metrics: AASX processing metrics model with updated values
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            async with self.connection_manager.get_session() as session:
                # Convert Pydantic model to database dict
                db_data = self._model_to_dict(metrics)
                
                # Remove metric_id from update data (it's the primary key)
                metric_id = db_data.pop('metric_id')
                
                # Update database record
                query = update(self.table).where(self.table.metric_id == metric_id).values(**db_data)
                await session.execute(query)
                await session.commit()
                
                return True
                
        except SQLAlchemyError as e:
            print(f"Error updating AASX processing metrics record: {e}")
            return False
    
    async def delete(self, metric_id: int) -> bool:
        """
        Delete an AASX processing metrics record by metric ID.
        
        Args:
            metric_id: Unique metric identifier
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            async with self.connection_manager.get_session() as session:
                query = delete(self.table).where(self.table.metric_id == metric_id)
                await session.execute(query)
                await session.commit()
                
                return True
                
        except SQLAlchemyError as e:
            print(f"Error deleting AASX processing metrics record: {e}")
            return False
    
    async def get_performance_trends(self, job_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get performance trends for a specific job over a time period.
        
        Args:
            job_id: Job identifier
            days: Number of days to analyze
            
        Returns:
            Dict[str, Any]: Performance trends data
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            metrics = await self.get_by_timestamp_range(
                start_date.isoformat(),
                end_date.isoformat(),
                job_id
            )
            
            if not metrics:
                return {}
            
            # Calculate trends
            health_scores = [m.health_score for m in metrics if m.health_score is not None]
            response_times = [m.response_time_ms for m in metrics if m.response_time_ms is not None]
            extraction_speeds = [m.extraction_speed_sec for m in metrics if m.extraction_speed_sec is not None]
            generation_speeds = [m.generation_speed_sec for m in metrics if m.generation_speed_sec is not None]
            
            trends = {
                'health_score_trend': self._calculate_trend(health_scores),
                'response_time_trend': self._calculate_trend(response_times),
                'extraction_speed_trend': self._calculate_trend(extraction_speeds),
                'generation_speed_trend': self._calculate_trend(generation_speeds),
                'total_metrics': len(metrics),
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }
            
            return trends
            
        except Exception as e:
            print(f"Error calculating performance trends: {e}")
            return {}
    
    async def get_system_health_summary(self, org_id: Optional[str] = None, hours: int = 24) -> Dict[str, Any]:
        """
        Get system health summary across all jobs.
        
        Args:
            org_id: Optional organization ID to filter by
            hours: Number of hours to analyze
            
        Returns:
            Dict[str, Any]: System health summary
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(hours=hours)
            
            # Get metrics within time range
            metrics = await self.get_by_timestamp_range(
                start_date.isoformat(),
                end_date.isoformat()
            )
            
            if not metrics:
                return {}
            
            # Filter by org_id if provided (this would require joining with aasx_processing table)
            # For now, we'll work with all metrics
            
            # Calculate summary statistics
            health_scores = [m.health_score for m in metrics if m.health_score is not None]
            response_times = [m.response_time_ms for m in metrics if m.response_time_ms is not None]
            cpu_usage = [m.cpu_usage_percent for m in metrics if m.cpu_usage_percent is not None]
            memory_usage = [m.memory_usage_percent for m in metrics if m.memory_usage_percent is not None]
            
            summary = {
                'total_metrics': len(metrics),
                'time_range_hours': hours,
                'health_score': {
                    'average': sum(health_scores) / len(health_scores) if health_scores else 0,
                    'min': min(health_scores) if health_scores else 0,
                    'max': max(health_scores) if health_scores else 0
                },
                'response_time_ms': {
                    'average': sum(response_times) / len(response_times) if response_times else 0,
                    'min': min(response_times) if response_times else 0,
                    'max': max(response_times) if response_times else 0
                },
                'cpu_usage_percent': {
                    'average': sum(cpu_usage) / len(cpu_usage) if cpu_usage else 0,
                    'min': min(cpu_usage) if cpu_usage else 0,
                    'max': max(cpu_usage) if cpu_usage else 0
                },
                'memory_usage_percent': {
                    'average': sum(memory_usage) / len(memory_usage) if memory_usage else 0,
                    'min': min(memory_usage) if memory_usage else 0,
                    'max': max(memory_usage) if memory_usage else 0
                }
            }
            
            # Determine overall health status
            avg_health = summary['health_score']['average']
            if avg_health >= 90:
                summary['overall_status'] = 'excellent'
            elif avg_health >= 80:
                summary['overall_status'] = 'good'
            elif avg_health >= 70:
                summary['overall_status'] = 'fair'
            else:
                summary['overall_status'] = 'poor'
            
            return summary
            
        except Exception as e:
            print(f"Error calculating system health summary: {e}")
            return {}
    
    async def get_anomaly_detection(self, job_id: str, threshold: float = 2.0) -> List[Dict[str, Any]]:
        """
        Detect anomalies in metrics for a specific job.
        
        Args:
            job_id: Job identifier
            threshold: Standard deviation threshold for anomaly detection
            
        Returns:
            List[Dict[str, Any]]: List of detected anomalies
        """
        try:
            # Get recent metrics for the job
            metrics = await self.get_by_job_id(job_id)
            
            if len(metrics) < 3:  # Need at least 3 data points for anomaly detection
                return []
            
            anomalies = []
            
            # Check for anomalies in key metrics
            health_scores = [m.health_score for m in metrics if m.health_score is not None]
            if len(health_scores) >= 3:
                health_anomalies = self._detect_anomalies(health_scores, threshold)
                for idx in health_anomalies:
                    anomalies.append({
                        'metric_type': 'health_score',
                        'timestamp': metrics[idx].timestamp,
                        'value': metrics[idx].health_score,
                        'expected_range': self._get_expected_range(health_scores, idx),
                        'severity': 'high' if abs(metrics[idx].health_score - sum(health_scores) / len(health_scores)) > 20 else 'medium'
                    })
            
            response_times = [m.response_time_ms for m in metrics if m.response_time_ms is not None]
            if len(response_times) >= 3:
                response_anomalies = self._detect_anomalies(response_times, threshold)
                for idx in response_anomalies:
                    anomalies.append({
                        'metric_type': 'response_time_ms',
                        'timestamp': metrics[idx].timestamp,
                        'value': metrics[idx].response_time_ms,
                        'expected_range': self._get_expected_range(response_times, idx),
                        'severity': 'high' if metrics[idx].response_time_ms > 1000 else 'medium'
                    })
            
            return anomalies
            
        except Exception as e:
            print(f"Error detecting anomalies: {e}")
            return []
    
    def _calculate_trend(self, values: List[float]) -> str:
        """
        Calculate trend direction from a list of values.
        
        Args:
            values: List of numeric values
            
        Returns:
            str: Trend direction ('increasing', 'decreasing', 'stable')
        """
        if len(values) < 2:
            return 'stable'
        
        # Simple linear trend calculation
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        if not first_half or not second_half:
            return 'stable'
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        change_percent = abs(second_avg - first_avg) / first_avg * 100 if first_avg != 0 else 0
        
        if change_percent < 5:
            return 'stable'
        elif second_avg > first_avg:
            return 'increasing'
        else:
            return 'decreasing'
    
    def _detect_anomalies(self, values: List[float], threshold: float) -> List[int]:
        """
        Detect anomalies in a list of values using statistical methods.
        
        Args:
            values: List of numeric values
            threshold: Standard deviation threshold
            
        Returns:
            List[int]: Indices of anomalous values
        """
        if len(values) < 3:
            return []
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        anomalies = []
        for i, value in enumerate(values):
            z_score = abs(value - mean) / std_dev if std_dev != 0 else 0
            if z_score > threshold:
                anomalies.append(i)
        
        return anomalies
    
    def _get_expected_range(self, values: List[float], exclude_idx: int) -> Dict[str, float]:
        """
        Get expected range excluding a specific index.
        
        Args:
            values: List of numeric values
            exclude_idx: Index to exclude
            
        Returns:
            Dict[str, float]: Expected range (min, max, mean)
        """
        filtered_values = [v for i, v in enumerate(values) if i != exclude_idx]
        
        if not filtered_values:
            return {'min': 0, 'max': 0, 'mean': 0}
        
        return {
            'min': min(filtered_values),
            'max': max(filtered_values),
            'mean': sum(filtered_values) / len(filtered_values)
        }
    
    def _model_to_dict(self, model: AasxProcessingMetrics) -> Dict[str, Any]:
        """
        Convert Pydantic model to database dictionary.
        
        Args:
            model: AASX processing metrics model instance
            
        Returns:
            Dict[str, Any]: Database dictionary
        """
        # Convert model to dict and handle any special conversions
        data = model.model_dump()
        
        # Ensure timestamp is in correct format
        if 'timestamp' in data and data['timestamp']:
            if isinstance(data['timestamp'], datetime):
                data['timestamp'] = data['timestamp'].isoformat()
        
        return data
    
    def _dict_to_model(self, db_dict: Dict[str, Any]) -> AasxProcessingMetrics:
        """
        Convert database dictionary to Pydantic model.
        
        Args:
            db_dict: Database dictionary
            
        Returns:
            AasxProcessingMetrics: AASX processing metrics model instance
        """
        # Clean up database dict (remove SQLAlchemy internal fields)
        clean_dict = {k: v for k, v in db_dict.items() if not k.startswith('_')}
        
        # Create model instance
        return AasxProcessingMetrics(**clean_dict)

