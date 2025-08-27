"""
Async Base Repository
====================

Async base class for all repositories with common CRUD operations.
Provides async support for the Knowledge Graph module and future async adoption.
"""

import logging
from typing import Dict, Any, List, Optional, TypeVar, Generic
from abc import ABC, abstractmethod

from ..database.async_base_manager import AsyncBaseDatabaseManager
from ..models.base_model import BaseModel

T = TypeVar('T', bound=BaseModel)

logger = logging.getLogger(__name__)

class AsyncBaseRepository(ABC, Generic[T]):
    """Async base repository with common CRUD operations."""
    
    def __init__(self, db_manager: AsyncBaseDatabaseManager, model_class: type[T]):
        self.db_manager = db_manager
        self.model_class = model_class
        self.table_name = self._get_table_name()
    
    @abstractmethod
    def _get_table_name(self) -> str:
        """Get the table name for this repository."""
        pass
    
    @abstractmethod
    def _get_columns(self) -> List[str]:
        """Get the list of column names for this table."""
        pass
    
    def _get_primary_key_column(self) -> str:
        """Get the primary key column name. Defaults to 'id' but can be overridden."""
        return "id"
    
    async def create(self, model: T) -> T:
        """Create a new record asynchronously."""
        try:
            model.validate()
            data = model.to_dict()
            
            # Ensure the id in data matches model.id
            if hasattr(model, 'id') and model.id:
                data['id'] = model.id
            
            columns = self._get_columns()
            placeholders = ', '.join(['?' for _ in columns])
            column_names = ', '.join(columns)
            
            query = f"""
                INSERT INTO {self.table_name} ({column_names})
                VALUES ({placeholders})
            """
            
            values = tuple(data[col] for col in columns)
            await self.db_manager.execute_update(query, values)
            
            logger.info(f"Created {self.table_name} record: {model.id}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to create {self.table_name} record: {e}")
            raise
    
    async def get_by_id(self, record_id: str) -> Optional[T]:
        """Get a record by ID asynchronously."""
        try:
            pk_column = self._get_primary_key_column()
            query = f"SELECT * FROM {self.table_name} WHERE {pk_column} = ?"
            results = await self.db_manager.execute_query(query, (record_id,))
            
            if results:
                return self.model_class.from_dict(results[0])
            return None
            
        except Exception as e:
            logger.error(f"Failed to get {self.table_name} by ID {record_id}: {e}")
            raise
    
    async def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
        """Get all records with optional pagination asynchronously."""
        try:
            query = f"SELECT * FROM {self.table_name}"
            params = []
            
            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)
                
                if offset is not None:
                    query += " OFFSET ?"
                    params.append(offset)
            
            results = await self.db_manager.execute_query(query, tuple(params))
            return [self.model_class.from_dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Failed to get all {self.table_name} records: {e}")
            raise
    
    async def update(self, model: T) -> T:
        """Update an existing record asynchronously."""
        try:
            model.validate()
            data = model.to_dict()
            pk_column = self._get_primary_key_column()
            
            # Remove the primary key from the update data
            if pk_column in data:
                del data[pk_column]
            
            columns = [col for col in self._get_columns() if col != pk_column]
            set_clause = ', '.join([f"{col} = ?" for col in columns])
            
            query = f"""
                UPDATE {self.table_name}
                SET {set_clause}
                WHERE {pk_column} = ?
            """
            
            values = tuple(data[col] for col in columns) + (getattr(model, pk_column),)
            await self.db_manager.execute_update(query, values)
            
            logger.info(f"Updated {self.table_name} record: {getattr(model, pk_column)}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to update {self.table_name} record: {e}")
            raise
    
    async def delete(self, record_id: str) -> bool:
        """Delete a record by ID asynchronously."""
        try:
            pk_column = self._get_primary_key_column()
            query = f"DELETE FROM {self.table_name} WHERE {pk_column} = ?"
            affected_rows = await self.db_manager.execute_update(query, (record_id,))
            
            if affected_rows > 0:
                logger.info(f"Deleted {self.table_name} record: {record_id}")
                return True
            else:
                logger.warning(f"No {self.table_name} record found to delete: {record_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete {self.table_name} record {record_id}: {e}")
            raise
    
    async def count(self) -> int:
        """Get the total count of records asynchronously."""
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name}"
            results = await self.db_manager.execute_query(query)
            return results[0]['count'] if results else 0
            
        except Exception as e:
            logger.error(f"Failed to count {self.table_name} records: {e}")
            raise
    
    async def exists(self, record_id: str) -> bool:
        """Check if a record exists by ID asynchronously."""
        try:
            pk_column = self._get_primary_key_column()
            query = f"SELECT 1 FROM {self.table_name} WHERE {pk_column} = ?"
            results = await self.db_manager.execute_query(query, (record_id,))
            return len(results) > 0
            
        except Exception as e:
            logger.error(f"Failed to check existence of {self.table_name} record {record_id}: {e}")
            raise




