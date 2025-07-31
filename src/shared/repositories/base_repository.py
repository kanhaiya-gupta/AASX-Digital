"""
Base Repository
==============

Base class for all repositories with common CRUD operations.
"""

import logging
from typing import Dict, Any, List, Optional, TypeVar, Generic
from abc import ABC, abstractmethod

from ..database.base_manager import BaseDatabaseManager
from ..models.base_model import BaseModel

T = TypeVar('T', bound=BaseModel)

logger = logging.getLogger(__name__)

class BaseRepository(ABC, Generic[T]):
    """Base repository with common CRUD operations."""
    
    def __init__(self, db_manager: BaseDatabaseManager, model_class: type[T]):
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
    
    def create(self, model: T) -> T:
        """Create a new record."""
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
            self.db_manager.execute_update(query, values)
            
            logger.info(f"Created {self.table_name} record: {model.id}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to create {self.table_name} record: {e}")
            raise
    
    def get_by_id(self, record_id: str) -> Optional[T]:
        """Get a record by ID."""
        try:
            pk_column = self._get_primary_key_column()
            query = f"SELECT * FROM {self.table_name} WHERE {pk_column} = ?"
            results = self.db_manager.execute_query(query, (record_id,))
            
            if results:
                return self.model_class.from_dict(results[0])
            return None
            
        except Exception as e:
            logger.error(f"Failed to get {self.table_name} by ID {record_id}: {e}")
            raise
    
    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
        """Get all records with optional pagination."""
        try:
            query = f"SELECT * FROM {self.table_name}"
            params = []
            
            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)
                
                if offset is not None:
                    query += " OFFSET ?"
                    params.append(offset)
            
            results = self.db_manager.execute_query(query, tuple(params))
            return [self.model_class.from_dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Failed to get all {self.table_name} records: {e}")
            raise
    
    def update(self, entity_id: str, data: Dict[str, Any]) -> Optional[T]:
        """Update an existing record."""
        try:
            # Get existing record
            existing_record = self.get_by_id(entity_id)
            if not existing_record:
                return None
            
            # Update the record with new data
            for key, value in data.items():
                if hasattr(existing_record, key):
                    setattr(existing_record, key, value)
            
            # Validate the updated model
            existing_record.validate()
            
            # Prepare update data
            update_data = existing_record.to_dict()
            columns = self._get_columns()
            pk_column = self._get_primary_key_column()
            set_clause = ', '.join([f"{col} = ?" for col in columns if col != pk_column])
            
            query = f"""
                UPDATE {self.table_name}
                SET {set_clause}
                WHERE {pk_column} = ?
            """
            
            values = tuple(update_data[col] for col in columns if col != pk_column) + (entity_id,)
            self.db_manager.execute_update(query, values)
            
            logger.info(f"Updated {self.table_name} record: {entity_id}")
            return existing_record
            
        except Exception as e:
            logger.error(f"Failed to update {self.table_name} record {entity_id}: {e}")
            raise
    
    def delete(self, record_id: str) -> bool:
        """Delete a record by ID."""
        try:
            pk_column = self._get_primary_key_column()
            query = f"DELETE FROM {self.table_name} WHERE {pk_column} = ?"
            affected_rows = self.db_manager.execute_update(query, (record_id,))
            
            if affected_rows > 0:
                logger.info(f"Deleted {self.table_name} record: {record_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete {self.table_name} record {record_id}: {e}")
            raise
    
    def exists(self, record_id: str) -> bool:
        """Check if a record exists."""
        try:
            pk_column = self._get_primary_key_column()
            query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE {pk_column} = ?"
            results = self.db_manager.execute_query(query, (record_id,))
            return results[0]['count'] > 0
            
        except Exception as e:
            logger.error(f"Failed to check existence of {self.table_name} record {record_id}: {e}")
            raise
    
    def count(self) -> int:
        """Get the total count of records."""
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name}"
            results = self.db_manager.execute_query(query)
            return results[0]['count']
            
        except Exception as e:
            logger.error(f"Failed to get count of {self.table_name} records: {e}")
            raise 