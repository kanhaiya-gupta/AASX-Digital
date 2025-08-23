#!/usr/bin/env python3
"""
User Consent Service
===================

Service layer for user consent business logic.
Handles consent validation, privacy compliance, and federated learning integration.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path

from ..models.user_consent import UserConsent
from ..repositories.user_consent_repository import UserConsentRepository


class UserConsentService:
    """
    Service for user consent operations
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize UserConsentService
        
        Args:
            db_path: Path to database file (optional)
        """
        self.repository = UserConsentRepository(db_path)
        self.logger = logging.getLogger(__name__)
    
    def create_consent(self, user_id: str, consent_type: str = "federated_learning", 
                      project_id: Optional[str] = None, file_id: Optional[str] = None,
                      data_privacy_level: str = "private", consent_terms: Optional[str] = None) -> Optional[UserConsent]:
        """
        Create a new user consent record
        
        Args:
            user_id: User ID
            consent_type: Type of consent (federated_learning, data_sharing, analytics, research)
            project_id: Associated project ID (optional)
            file_id: Associated file ID (optional)
            data_privacy_level: Privacy level (private, shared, public)
            consent_terms: Consent terms text (optional)
            
        Returns:
            Optional[UserConsent]: Created consent object or None if failed
        """
        try:
            # Validate input parameters
            if not user_id:
                raise ValueError("user_id is required")
            
            # Check if user already has active consent for this type
            existing_consents = self.repository.get_active_consents(user_id, consent_type)
            if existing_consents:
                self.logger.warning(f"User {user_id} already has active {consent_type} consent")
                return existing_consents[0]  # Return existing active consent
            
            # Create new consent
            consent = UserConsent(
                user_id=user_id,
                consent_type=consent_type,
                consent_given=True,
                data_privacy_level=data_privacy_level,
                project_id=project_id,
                file_id=file_id,
                consent_terms=consent_terms
            )
            
            # Save to database
            created_consent = self.repository.create(consent)
            if created_consent:
                self.logger.info(f"Created consent {created_consent.consent_id} for user {user_id}")
                return created_consent
            else:
                self.logger.error(f"Failed to create consent for user {user_id}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating consent for user {user_id}: {e}")
            return None
    
    def get_user_consents(self, user_id: str) -> List[UserConsent]:
        """
        Get all consents for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List[UserConsent]: List of consent objects
        """
        try:
            return self.repository.get_by_user_id(user_id)
        except Exception as e:
            self.logger.error(f"Error getting consents for user {user_id}: {e}")
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
            return self.repository.get_active_consents(user_id, consent_type)
        except Exception as e:
            self.logger.error(f"Error getting active consents for user {user_id}: {e}")
            return []
    
    def has_active_consent(self, user_id: str, consent_type: str = "federated_learning") -> bool:
        """
        Check if user has active consent for a specific type
        
        Args:
            user_id: User ID
            consent_type: Type of consent to check
            
        Returns:
            bool: True if user has active consent
        """
        try:
            active_consents = self.get_active_consents(user_id, consent_type)
            return len(active_consents) > 0
        except Exception as e:
            self.logger.error(f"Error checking active consent for user {user_id}: {e}")
            return False
    
    def update_consent(self, consent_id: str, consent_given: bool, 
                      consent_terms: Optional[str] = None) -> bool:
        """
        Update consent status
        
        Args:
            consent_id: Consent ID to update
            consent_given: New consent status
            consent_terms: Updated consent terms (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get existing consent
            consent = self.repository.get_by_id(consent_id)
            if not consent:
                self.logger.error(f"Consent {consent_id} not found")
                return False
            
            # Update consent
            consent.update_consent(consent_given, consent_terms)
            
            # Save to database
            if self.repository.update(consent):
                self.logger.info(f"Updated consent {consent_id}")
                return True
            else:
                self.logger.error(f"Failed to update consent {consent_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating consent {consent_id}: {e}")
            return False
    
    def revoke_consent(self, consent_id: str) -> bool:
        """
        Revoke a user consent
        
        Args:
            consent_id: Consent ID to revoke
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.repository.revoke_consent(consent_id):
                self.logger.info(f"Revoked consent {consent_id}")
                return True
            else:
                self.logger.error(f"Failed to revoke consent {consent_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error revoking consent {consent_id}: {e}")
            return False
    
    def delete_consent(self, consent_id: str) -> bool:
        """
        Delete a user consent
        
        Args:
            consent_id: Consent ID to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.repository.delete(consent_id):
                self.logger.info(f"Deleted consent {consent_id}")
                return True
            else:
                self.logger.error(f"Failed to delete consent {consent_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting consent {consent_id}: {e}")
            return False
    
    def get_consent_statistics(self) -> Dict[str, Any]:
        """
        Get consent statistics
        
        Returns:
            Dict[str, Any]: Statistics about consents
        """
        try:
            return self.repository.get_consent_statistics()
        except Exception as e:
            self.logger.error(f"Error getting consent statistics: {e}")
            return {}
    
    def check_federated_learning_eligibility(self, user_id: str, project_id: Optional[str] = None, 
                                           file_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Check if user is eligible for federated learning
        
        Args:
            user_id: User ID
            project_id: Project ID (optional)
            file_id: File ID (optional)
            
        Returns:
            Dict[str, Any]: Eligibility status and details
        """
        try:
            # Check for active federated learning consent
            active_consents = self.get_active_consents(user_id, "federated_learning")
            
            if not active_consents:
                return {
                    'eligible': False,
                    'reason': 'No active federated learning consent',
                    'required_action': 'Obtain user consent for federated learning'
                }
            
            # Get the most recent active consent
            latest_consent = active_consents[0]
            
            # Check privacy level
            if latest_consent.data_privacy_level == "private":
                return {
                    'eligible': False,
                    'reason': 'Privacy level is set to private',
                    'required_action': 'User must change privacy level to shared or public'
                }
            
            # Check if consent is project/file specific
            if project_id and latest_consent.project_id and latest_consent.project_id != project_id:
                return {
                    'eligible': False,
                    'reason': 'Consent is project-specific and does not match',
                    'required_action': 'Obtain consent for this specific project'
                }
            
            if file_id and latest_consent.file_id and latest_consent.file_id != file_id:
                return {
                    'eligible': False,
                    'reason': 'Consent is file-specific and does not match',
                    'required_action': 'Obtain consent for this specific file'
                }
            
            return {
                'eligible': True,
                'consent_id': latest_consent.consent_id,
                'privacy_level': latest_consent.data_privacy_level,
                'consent_timestamp': latest_consent.consent_timestamp,
                'expires_at': self._calculate_expiry_date(latest_consent.consent_timestamp)
            }
            
        except Exception as e:
            self.logger.error(f"Error checking federated learning eligibility for user {user_id}: {e}")
            return {
                'eligible': False,
                'reason': f'Error checking eligibility: {str(e)}',
                'required_action': 'Contact administrator'
            }
    
    def _calculate_expiry_date(self, consent_timestamp: str) -> str:
        """
        Calculate consent expiry date (1 year from consent timestamp)
        
        Args:
            consent_timestamp: ISO format timestamp
            
        Returns:
            str: Expiry date in ISO format
        """
        try:
            consent_date = datetime.fromisoformat(consent_timestamp)
            expiry_date = consent_date + timedelta(days=365)  # 1 year
            return expiry_date.isoformat()
        except Exception:
            return ""
    
    def cleanup_expired_consents(self) -> int:
        """
        Clean up expired consents (mark as inactive)
        
        Returns:
            int: Number of consents cleaned up
        """
        try:
            all_consents = self.repository.get_by_user_id("*")  # Get all consents
            cleaned_count = 0
            
            for consent in all_consents:
                if not consent.is_active():
                    if self.repository.revoke_consent(consent.consent_id):
                        cleaned_count += 1
            
            self.logger.info(f"Cleaned up {cleaned_count} expired consents")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up expired consents: {e}")
            return 0 