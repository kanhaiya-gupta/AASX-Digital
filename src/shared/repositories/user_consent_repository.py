#!/usr/bin/env python3
"""
User Consent Repository
======================

Repository for managing user consent data in the database.
Handles CRUD operations for user consent tracking.
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models.user_consent import UserConsent
from ..database.connection_manager import DatabaseConnectionManager


class UserConsentRepository:
    """
    Repository for UserConsent database operations
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize UserConsentRepository
        
        Args:
            db_path: Path to database file (optional)
        """
        if db_path is None:
            db_path = Path("data/aasx_database.db")
        
        self.db_path = db_path
        self.connection_manager = DatabaseConnectionManager(db_path)
        self.logger = logging.getLogger(__name__)
    
    def create(self, consent: UserConsent) -> Optional[UserConsent]:
        """
        Create a new user consent record
        
        Args:
            consent: UserConsent object to create
            
        Returns:
            Optional[UserConsent]: Created consent object or None if failed
        """
        try:
            with self.connection_manager.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO user_consents (
                        consent_id, user_id, consent_type, consent_given,
                        consent_timestamp, data_privacy_level, consent_terms_version,
                        consent_terms, project_id, file_id, metadata,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    consent.consent_id,
                    consent.user_id,
                    consent.consent_type,
                    consent.consent_given,
                    consent.consent_timestamp,
                    consent.data_privacy_level,
                    consent.consent_terms_version,
                    consent.consent_terms,
                    consent.project_id,
                    consent.file_id,
                    consent.metadata,
                    consent.created_at,
                    consent.updated_at
                ))
                
                self.logger.info(f"Created user consent: {consent.consent_id}")
                return consent
                
        except Exception as e:
            self.logger.error(f"Failed to create user consent: {e}")
            return None
    
    def get_by_id(self, consent_id: str) -> Optional[UserConsent]:
        """
        Get user consent by ID
        
        Args:
            consent_id: Consent ID to retrieve
            
        Returns:
            Optional[UserConsent]: Consent object or None if not found
        """
        try:
            with self.connection_manager.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM user_consents WHERE consent_id = ?
                """, (consent_id,))
                
                row = cursor.fetchone()
                if row:
                    return self._row_to_consent(row)
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get user consent by ID: {e}")
            return None
    
    def get_by_user_id(self, user_id: str) -> List[UserConsent]:
        """
        Get all consents for a user
        
        Args:
            user_id: User ID to retrieve consents for
            
        Returns:
            List[UserConsent]: List of consent objects
        """
        try:
            with self.connection_manager.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM user_consents WHERE user_id = ?
                    ORDER BY consent_timestamp DESC
                """, (user_id,))
                
                rows = cursor.fetchall()
                return [self._row_to_consent(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to get user consents by user ID: {e}")
            return []
    
    def get_active_consents(self, user_id: str, consent_type: str = "federated_learning") -> List[UserConsent]:
        """
        Get active consents for a user and consent type
        
        Args:
            user_id: User ID
            consent_type: Type of consent to filter by
            
        Returns:
            List[UserConsent]: List of active consent objects
        """
        try:
            with self.connection_manager.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM user_consents 
                    WHERE user_id = ? AND consent_type = ? AND consent_given = 1
                    ORDER BY consent_timestamp DESC
                """, (user_id, consent_type))
                
                rows = cursor.fetchall()
                consents = [self._row_to_consent(row) for row in rows]
                
                # Filter for active consents (not expired)
                return [consent for consent in consents if consent.is_active()]
                
        except Exception as e:
            self.logger.error(f"Failed to get active user consents: {e}")
            return []
    
    def get_by_project(self, project_id: str) -> List[UserConsent]:
        """
        Get all consents for a project
        
        Args:
            project_id: Project ID to retrieve consents for
            
        Returns:
            List[UserConsent]: List of consent objects
        """
        try:
            with self.connection_manager.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM user_consents WHERE project_id = ?
                    ORDER BY consent_timestamp DESC
                """, (project_id,))
                
                rows = cursor.fetchall()
                return [self._row_to_consent(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to get user consents by project: {e}")
            return []
    
    def get_by_file(self, file_id: str) -> List[UserConsent]:
        """
        Get all consents for a file
        
        Args:
            file_id: File ID to retrieve consents for
            
        Returns:
            List[UserConsent]: List of consent objects
        """
        try:
            with self.connection_manager.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM user_consents WHERE file_id = ?
                    ORDER BY consent_timestamp DESC
                """, (file_id,))
                
                rows = cursor.fetchall()
                return [self._row_to_consent(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to get user consents by file: {e}")
            return []
    
    def update(self, consent: UserConsent) -> bool:
        """
        Update an existing user consent
        
        Args:
            consent: UserConsent object to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.connection_manager.get_cursor() as cursor:
                cursor.execute("""
                    UPDATE user_consents SET
                        user_id = ?, consent_type = ?, consent_given = ?,
                        consent_timestamp = ?, data_privacy_level = ?,
                        consent_terms_version = ?, consent_terms = ?,
                        project_id = ?, file_id = ?, metadata = ?,
                        updated_at = ?
                    WHERE consent_id = ?
                """, (
                    consent.user_id,
                    consent.consent_type,
                    consent.consent_given,
                    consent.consent_timestamp,
                    consent.data_privacy_level,
                    consent.consent_terms_version,
                    consent.consent_terms,
                    consent.project_id,
                    consent.file_id,
                    consent.metadata,
                    consent.updated_at,
                    consent.consent_id
                ))
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Updated user consent: {consent.consent_id}")
                    return True
                else:
                    self.logger.warning(f"No user consent found to update: {consent.consent_id}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Failed to update user consent: {e}")
            return False
    
    def delete(self, consent_id: str) -> bool:
        """
        Delete a user consent
        
        Args:
            consent_id: Consent ID to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.connection_manager.get_cursor() as cursor:
                cursor.execute("""
                    DELETE FROM user_consents WHERE consent_id = ?
                """, (consent_id,))
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Deleted user consent: {consent_id}")
                    return True
                else:
                    self.logger.warning(f"No user consent found to delete: {consent_id}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Failed to delete user consent: {e}")
            return False
    
    def revoke_consent(self, consent_id: str) -> bool:
        """
        Revoke a user consent (set consent_given to False)
        
        Args:
            consent_id: Consent ID to revoke
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.connection_manager.get_cursor() as cursor:
                cursor.execute("""
                    UPDATE user_consents SET
                        consent_given = 0,
                        consent_timestamp = ?,
                        updated_at = ?
                    WHERE consent_id = ?
                """, (
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    consent_id
                ))
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Revoked user consent: {consent_id}")
                    return True
                else:
                    self.logger.warning(f"No user consent found to revoke: {consent_id}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Failed to revoke user consent: {e}")
            return False
    
    def get_consent_statistics(self) -> Dict[str, Any]:
        """
        Get consent statistics
        
        Returns:
            Dict[str, Any]: Statistics about consents
        """
        try:
            with self.connection_manager.get_cursor() as cursor:
                # Total consents
                cursor.execute("SELECT COUNT(*) FROM user_consents")
                total_consents = cursor.fetchone()[0]
                
                # Active consents
                cursor.execute("SELECT COUNT(*) FROM user_consents WHERE consent_given = 1")
                active_consents = cursor.fetchone()[0]
                
                # Consents by type
                cursor.execute("""
                    SELECT consent_type, COUNT(*) 
                    FROM user_consents 
                    GROUP BY consent_type
                """)
                consents_by_type = dict(cursor.fetchall())
                
                # Consents by privacy level
                cursor.execute("""
                    SELECT data_privacy_level, COUNT(*) 
                    FROM user_consents 
                    GROUP BY data_privacy_level
                """)
                consents_by_privacy = dict(cursor.fetchall())
                
                return {
                    'total_consents': total_consents,
                    'active_consents': active_consents,
                    'inactive_consents': total_consents - active_consents,
                    'consents_by_type': consents_by_type,
                    'consents_by_privacy': consents_by_privacy
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get consent statistics: {e}")
            return {}
    
    def _row_to_consent(self, row: tuple) -> UserConsent:
        """
        Convert database row to UserConsent object
        
        Args:
            row: Database row tuple
            
        Returns:
            UserConsent: UserConsent object
        """
        # Get column names
        with self.connection_manager.get_cursor() as cursor:
            cursor.execute("PRAGMA table_info(user_consents)")
            columns = [col[1] for col in cursor.fetchall()]
        
        # Create dictionary from row
        row_dict = dict(zip(columns, row))
        
        # Convert boolean
        row_dict['consent_given'] = bool(row_dict['consent_given'])
        
        return UserConsent.from_dict(row_dict) 