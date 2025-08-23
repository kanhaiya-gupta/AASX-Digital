"""
AASX Processing Repository

Data access layer for AASX processing operations.
Uses the engine ConnectionManager for database access with async support.
"""

import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.engine.database.connection_manager import ConnectionManager
from src.engine.database.schema.modules.aasx_etl import AasxProcessingTable
from ..models.aasx_processing import AasxProcessing


class AasxProcessingRepository:
    """
    Repository for AASX processing operations.
    
    Provides async CRUD operations and business logic queries
    for the aasx_processing table.
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        """
        Initialize repository with connection manager.
        
        Args:
            connection_manager: Engine connection manager instance
        """
        self.connection_manager = connection_manager
        self.table = AasxProcessingTable
    
    async def create(self, aasx_processing: AasxProcessing) -> bool:
        """
        Create a new AASX processing record.
        
        Args:
            aasx_processing: AASX processing model instance
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            async with self.connection_manager.get_session() as session:
                # Convert Pydantic model to database dict
                db_data = self._model_to_dict(aasx_processing)
                
                # Create database record
                db_record = self.table(**db_data)
                session.add(db_record)
                await session.commit()
                
                return True
                
        except SQLAlchemyError as e:
            # Log error here
            print(f"Error creating AASX processing record: {e}")
            return False
    
    async def get_by_id(self, job_id: str) -> Optional[AasxProcessing]:
        """
        Get AASX processing record by job ID.
        
        Args:
            job_id: Unique job identifier
            
        Returns:
            Optional[AasxProcessing]: AASX processing model or None
        """
        try:
            async with self.connection_manager.get_session() as session:
                query = select(self.table).where(self.table.job_id == job_id)
                result = await session.execute(query)
                db_record = result.scalar_one_or_none()
                
                if db_record:
                    return self._dict_to_model(db_record.__dict__)
                return None
                
        except SQLAlchemyError as e:
            print(f"Error retrieving AASX processing record: {e}")
            return None
    
    async def get_by_file_id(self, file_id: str) -> List[AasxProcessing]:
        """
        Get all AASX processing records for a specific file.
        
        Args:
            file_id: File identifier
            
        Returns:
            List[AasxProcessing]: List of AASX processing models
        """
        try:
            async with self.connection_manager.get_session() as session:
                query = select(self.table).where(self.table.file_id == file_id)
                result = await session.execute(query)
                db_records = result.scalars().all()
                
                return [self._dict_to_model(record.__dict__) for record in db_records]
                
        except SQLAlchemyError as e:
            print(f"Error retrieving AASX processing records by file ID: {e}")
            return []
    
    async def get_by_project_id(self, project_id: str) -> List[AasxProcessing]:
        """
        Get all AASX processing records for a specific project.
        
        Args:
            project_id: Project identifier
            
        Returns:
            List[AasxProcessing]: List of AASX processing models
        """
        try:
            async with self.connection_manager.get_session() as session:
                query = select(self.table).where(self.table.project_id == project_id)
                result = await session.execute(query)
                db_records = result.scalars().all()
                
                return [self._dict_to_model(record.__dict__) for record in db_records]
                
        except SQLAlchemyError as e:
            print(f"Error retrieving AASX processing records by project ID: {e}")
            return []
    
    async def get_by_status(self, status: str) -> List[AasxProcessing]:
        """
        Get AASX processing records by processing status.
        
        Args:
            status: Processing status to filter by
            
        Returns:
            List[AasxProcessing]: List of AASX processing models
        """
        try:
            async with self.connection_manager.get_session() as session:
                query = select(self.table).where(self.table.processing_status == status)
                result = await session.execute(query)
                db_records = result.scalars().all()
                
                return [self._dict_to_model(record.__dict__) for record in db_records]
                
        except SQLAlchemyError as e:
            print(f"Error retrieving AASX processing records by status: {e}")
            return []
    
    async def get_by_org_id(self, org_id: str) -> List[AasxProcessing]:
        """
        Get AASX processing records by organization ID.
        
        Args:
            org_id: Organization identifier
            
        Returns:
            List[AasxProcessing]: List of AASX processing models
        """
        try:
            async with self.connection_manager.get_session() as session:
                query = select(self.table).where(self.table.org_id == org_id)
                result = await session.execute(query)
                db_records = result.scalars().all()
                
                return [self._dict_to_model(record.__dict__) for record in db_records]
                
        except SQLAlchemyError as e:
            print(f"Error retrieving AASX processing records by org ID: {e}")
            return []
    
    async def update(self, aasx_processing: AasxProcessing) -> bool:
        """
        Update an existing AASX processing record.
        
        Args:
            aasx_processing: AASX processing model with updated values
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            async with self.connection_manager.get_session() as session:
                # Convert Pydantic model to database dict
                db_data = self._model_to_dict(aasx_processing)
                
                # Update timestamp
                db_data['updated_at'] = datetime.now().isoformat()
                
                # Remove job_id from update data (it's the primary key)
                job_id = db_data.pop('job_id')
                
                # Update database record
                query = update(self.table).where(self.table.job_id == job_id).values(**db_data)
                await session.execute(query)
                await session.commit()
                
                return True
                
        except SQLAlchemyError as e:
            print(f"Error updating AASX processing record: {e}")
            return False
    
    async def delete(self, job_id: str) -> bool:
        """
        Delete an AASX processing record by job ID.
        
        Args:
            job_id: Unique job identifier
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            async with self.connection_manager.get_session() as session:
                query = delete(self.table).where(self.table.job_id == job_id)
                await session.execute(query)
                await session.commit()
                
                return True
                
        except SQLAlchemyError as e:
            print(f"Error deleting AASX processing record: {e}")
            return False
    
    async def update_status(self, job_id: str, new_status: str, user_id: str) -> bool:
        """
        Update processing status for a specific job.
        
        Args:
            job_id: Unique job identifier
            new_status: New processing status
            user_id: User performing the update
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            async with self.connection_manager.get_session() as session:
                query = update(self.table).where(self.table.job_id == job_id).values(
                    processing_status=new_status,
                    updated_at=datetime.now().isoformat()
                )
                await session.execute(query)
                await session.commit()
                
                return True
                
        except SQLAlchemyError as e:
            print(f"Error updating AASX processing status: {e}")
            return False
    
    async def get_failed_jobs(self, org_id: Optional[str] = None) -> List[AasxProcessing]:
        """
        Get all failed AASX processing jobs.
        
        Args:
            org_id: Optional organization ID to filter by
            
        Returns:
            List[AasxProcessing]: List of failed AASX processing models
        """
        try:
            async with self.connection_manager.get_session() as session:
                query = select(self.table).where(self.table.processing_status == 'failed')
                
                if org_id:
                    query = query.where(self.table.org_id == org_id)
                
                result = await session.execute(query)
                db_records = result.scalars().all()
                
                return [self._dict_to_model(record.__dict__) for record in db_records]
                
        except SQLAlchemyError as e:
            print(f"Error retrieving failed AASX processing jobs: {e}")
            return []
    
    async def get_jobs_by_priority(self, priority: str, org_id: Optional[str] = None) -> List[AasxProcessing]:
        """
        Get AASX processing jobs by priority level.
        
        Args:
            priority: Priority level to filter by
            org_id: Optional organization ID to filter by
            
        Returns:
            List[AasxProcessing]: List of AASX processing models
        """
        try:
            async with self.connection_manager.get_session() as session:
                query = select(self.table).where(self.table.processing_priority == priority)
                
                if org_id:
                    query = query.where(self.table.org_id == org_id)
                
                result = await session.execute(query)
                db_records = result.scalars().all()
                
                return [self._dict_to_model(record.__dict__) for record in db_records]
                
        except SQLAlchemyError as e:
            print(f"Error retrieving AASX processing jobs by priority: {e}")
            return []
    
    async def get_jobs_by_type(self, job_type: str, org_id: Optional[str] = None) -> List[AasxProcessing]:
        """
        Get AASX processing jobs by job type.
        
        Args:
            job_type: Job type to filter by (extraction or generation)
            org_id: Optional organization ID to filter by
            
        Returns:
            List[AasxProcessing]: List of AASX processing models
        """
        try:
            async with self.connection_manager.get_session() as session:
                query = select(self.table).where(self.table.job_type == job_type)
                
                if org_id:
                    query = query.where(self.table.org_id == org_id)
                
                result = await session.execute(query)
                db_records = result.scalars().all()
                
                return [self._dict_to_model(record.__dict__) for record in db_records]
                
        except SQLAlchemyError as e:
            print(f"Error retrieving AASX processing jobs by type: {e}")
            return []
    
    async def get_jobs_by_date_range(self, start_date: str, end_date: str, org_id: Optional[str] = None) -> List[AasxProcessing]:
        """
        Get AASX processing jobs within a date range.
        
        Args:
            start_date: Start date in ISO format
            end_date: End date in ISO format
            org_id: Optional organization ID to filter by
            
        Returns:
            List[AasxProcessing]: List of AASX processing models
        """
        try:
            async with self.connection_manager.get_session() as session:
                query = select(self.table).where(
                    and_(
                        self.table.created_at >= start_date,
                        self.table.created_at <= end_date
                    )
                )
                
                if org_id:
                    query = query.where(self.table.org_id == org_id)
                
                result = await session.execute(query)
                db_records = result.scalars().all()
                
                return [self._dict_to_model(record.__dict__) for record in db_records]
                
        except SQLAlchemyError as e:
            print(f"Error retrieving AASX processing jobs by date range: {e}")
            return []
    
    async def get_job_count_by_status(self, org_id: Optional[str] = None) -> Dict[str, int]:
        """
        Get count of jobs by processing status.
        
        Args:
            org_id: Optional organization ID to filter by
            
        Returns:
            Dict[str, int]: Dictionary mapping status to count
        """
        try:
            async with self.connection_manager.get_session() as session:
                query = select(
                    self.table.processing_status,
                    func.count(self.table.job_id).label('count')
                ).group_by(self.table.processing_status)
                
                if org_id:
                    query = query.where(self.table.org_id == org_id)
                
                result = await session.execute(query)
                status_counts = result.all()
                
                return {status: count for status, count in status_counts}
                
        except SQLAlchemyError as e:
            print(f"Error retrieving job count by status: {e}")
            return {}
    
    async def get_health_summary(self, org_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get health summary for AASX processing jobs.
        
        Args:
            org_id: Optional organization ID to filter by
            
        Returns:
            Dict[str, Any]: Health summary statistics
        """
        try:
            async with self.connection_manager.get_session() as session:
                # Base query
                base_query = select(self.table)
                if org_id:
                    base_query = base_query.where(self.table.org_id == org_id)
                
                # Get total count
                total_result = await session.execute(select(func.count()).select_from(base_query.subquery()))
                total_count = total_result.scalar()
                
                # Get counts by status
                status_counts = await self.get_job_count_by_status(org_id)
                
                # Get average processing time
                time_query = select(func.avg(self.table.processing_time)).select_from(base_query.subquery())
                time_result = await session.execute(time_query)
                avg_processing_time = time_result.scalar() or 0.0
                
                # Get average health score
                health_query = select(func.avg(self.table.overall_health_score)).select_from(base_query.subquery())
                health_result = await session.execute(health_query)
                avg_health_score = health_result.scalar() or 0.0
                
                return {
                    'total_jobs': total_count,
                    'status_counts': status_counts,
                    'average_processing_time': avg_processing_time,
                    'average_health_score': avg_health_score,
                    'health_status': 'healthy' if avg_health_score >= 70 else 'warning' if avg_health_score >= 50 else 'critical'
                }
                
        except SQLAlchemyError as e:
            print(f"Error retrieving health summary: {e}")
            return {}
    
    def _model_to_dict(self, model: AasxProcessing) -> Dict[str, Any]:
        """
        Convert Pydantic model to database dictionary.
        
        Args:
            model: AASX processing model instance
            
        Returns:
            Dict[str, Any]: Database dictionary
        """
        # Convert model to dict and handle any special conversions
        data = model.model_dump()
        
        # Ensure timestamps are in correct format
        if 'created_at' in data and data['created_at']:
            if isinstance(data['created_at'], datetime):
                data['created_at'] = data['created_at'].isoformat()
        
        if 'updated_at' in data and data['updated_at']:
            if isinstance(data['updated_at'], datetime):
                data['updated_at'] = data['updated_at'].isoformat()
        
        return data
    
    def _dict_to_model(self, db_dict: Dict[str, Any]) -> AasxProcessing:
        """
        Convert database dictionary to Pydantic model.
        
        Args:
            db_dict: Database dictionary
            
        Returns:
            AasxProcessing: AASX processing model instance
        """
        # Clean up database dict (remove SQLAlchemy internal fields)
        clean_dict = {k: v for k, v in db_dict.items() if not k.startswith('_')}
        
        # Create model instance
        return AasxProcessing(**clean_dict)
