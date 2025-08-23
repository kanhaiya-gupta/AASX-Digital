"""
Compliance Integration Service - Soft Connection to Backend
=========================================================

Thin integration layer that connects webapp to backend compliance services.
Handles frontend-specific logic while delegating compliance operations to backend.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

# Import from backend engine
from src.engine.services.auth.user_service import UserService
from src.engine.repositories.auth_repository import AuthRepository

logger = logging.getLogger(__name__)


class ComplianceService:
    """Integration service for compliance operations"""
    
    def __init__(self):
        """Initialize with backend services - lazy initialization to avoid async issues"""
        self._initialized = False
        self._auth_repo = None
        self._user_service = None
        
        logger.info("✅ Compliance integration service created (lazy initialization)")
    
    async def _ensure_initialized(self):
        """Ensure services are initialized (lazy initialization)"""
        if self._initialized:
            return
            
        try:
            # Initialize backend services
            self._auth_repo = AuthRepository()
            self._user_service = UserService(self._auth_repo)
            
            self._initialized = True
            logger.info("✅ Compliance integration service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize compliance integration service: {e}")
            raise
    
    @property
    def auth_repo(self):
        """Get auth repository (lazy initialization)"""
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call _ensure_initialized() first.")
        return self._auth_repo
    
    @property
    def user_service(self):
        """Get user service (lazy initialization)"""
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call _ensure_initialized() first.")
        return self._user_service
    
    async def get_audit_logs(self, user_id: str = None, action_type: str = None, 
                            start_date: datetime = None, end_date: datetime = None, 
                            limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get audit logs via backend"""
        await self._ensure_initialized()
        try:
            # Get audit logs from backend service
            # In production, this would call a dedicated audit service
            audit_logs = await self._get_audit_logs_from_backend(
                user_id=user_id,
                action_type=action_type,
                start_date=start_date,
                end_date=end_date,
                limit=limit,
                offset=offset
            )
            
            if not audit_logs:
                return []
            
            # Convert to list of dictionaries
            logs_list = []
            for log in audit_logs:
                log_dict = {
                    "log_id": getattr(log, 'log_id', None),
                    "user_id": getattr(log, 'user_id', None),
                    "username": getattr(log, 'username', None),
                    "action_type": getattr(log, 'action_type', None),
                    "action_description": getattr(log, 'action_description', None),
                    "resource_type": getattr(log, 'resource_type', None),
                    "resource_id": getattr(log, 'resource_id', None),
                    "ip_address": getattr(log, 'ip_address', None),
                    "user_agent": getattr(log, 'user_agent', None),
                    "timestamp": getattr(log, 'timestamp', None),
                    "success": getattr(log, 'success', True),
                    "error_message": getattr(log, 'error_message', None),
                    "metadata": self._parse_json_field(getattr(log, 'metadata', '{}')),
                    "compliance_tags": getattr(log, 'compliance_tags', [])
                }
                logs_list.append(log_dict)
            
            return logs_list
            
        except Exception as e:
            logger.error(f"Error getting audit logs: {e}")
            return []
    
    async def create_audit_log(self, user_id: str, action_type: str, 
                              action_description: str, resource_type: str = None,
                              resource_id: str = None, ip_address: str = None,
                              user_agent: str = None, success: bool = True,
                              error_message: str = None, metadata: Dict[str, Any] = None) -> bool:
        """Create an audit log entry via backend"""
        await self._ensure_initialized()
        try:
            # Prepare audit log data
            audit_data = {
                "user_id": user_id,
                "action_type": action_type,
                "action_description": action_description,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "timestamp": datetime.utcnow().isoformat(),
                "success": success,
                "error_message": error_message,
                "metadata": metadata or {},
                "compliance_tags": self._get_compliance_tags(action_type, resource_type)
            }
            
            # Create audit log via backend service
            success = await self._create_audit_log_in_backend(audit_data)
            
            if success:
                logger.info(f"Audit log created for user {user_id}, action: {action_type}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error creating audit log: {e}")
            return False
    
    async def get_compliance_report(self, report_type: str, organization_id: str = None,
                                  start_date: datetime = None, end_date: datetime = None) -> Optional[Dict[str, Any]]:
        """Generate compliance report via backend"""
        await self._ensure_initialized()
        try:
            # Validate report type
            if report_type not in ['user_activity', 'data_access', 'security_events', 'privacy_compliance', 'regulatory_audit']:
                raise ValueError(f"Unsupported report type: {report_type}")
            
            # Generate report via backend service
            report = await self._generate_compliance_report(
                report_type=report_type,
                organization_id=organization_id,
                start_date=start_date,
                end_date=end_date
            )
            
            if not report:
                return None
            
            # Add report metadata
            report["metadata"] = {
                "report_type": report_type,
                "organization_id": organization_id,
                "generated_at": datetime.utcnow().isoformat(),
                "report_period": {
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None
                }
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            return None
    
    async def get_data_retention_policy(self, organization_id: str) -> Optional[Dict[str, Any]]:
        """Get data retention policy via backend"""
        await self._ensure_initialized()
        try:
            # Get retention policy from backend service
            policy = await self._get_retention_policy_from_backend(organization_id)
            
            if not policy:
                # Return default policy
                return self._get_default_retention_policy()
            
            return policy
            
        except Exception as e:
            logger.error(f"Error getting data retention policy: {e}")
            return self._get_default_retention_policy()
    
    async def update_data_retention_policy(self, organization_id: str, policy: Dict[str, Any]) -> bool:
        """Update data retention policy via backend"""
        await self._ensure_initialized()
        try:
            # Validate policy data
            validated_policy = self._validate_retention_policy(policy)
            
            # Update policy via backend service
            success = await self._update_retention_policy_in_backend(organization_id, validated_policy)
            
            if success:
                logger.info(f"Data retention policy updated for organization {organization_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating data retention policy: {e}")
            return False
    
    async def get_privacy_settings(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user privacy settings via backend"""
        await self._ensure_initialized()
        try:
            # Get user from backend service
            user = await self.user_service.get_user_by_id(user_id)
            if not user:
                return None
            
            # Extract privacy settings from user model
            privacy_settings = {
                "user_id": user_id,
                "data_sharing": {
                    "allow_analytics": getattr(user, 'allow_analytics', True),
                    "allow_marketing": getattr(user, 'allow_marketing', False),
                    "allow_third_party": getattr(user, 'allow_third_party', False),
                    "allow_cookies": getattr(user, 'allow_cookies', True)
                },
                "data_retention": {
                    "retain_personal_data": getattr(user, 'retain_personal_data', True),
                    "retention_period_days": getattr(user, 'retention_period_days', 2555),  # 7 years
                    "auto_delete_expired": getattr(user, 'auto_delete_expired', True)
                },
                "data_access": {
                    "allow_profile_view": getattr(user, 'allow_profile_view', True),
                    "allow_contact": getattr(user, 'allow_contact', True),
                    "show_online_status": getattr(user, 'show_online_status', True),
                    "show_last_seen": getattr(user, 'show_last_seen', False)
                },
                "notifications": {
                    "email_notifications": getattr(user, 'email_notifications', True),
                    "push_notifications": getattr(user, 'push_notifications', True),
                    "sms_notifications": getattr(user, 'sms_notifications', False)
                },
                "gdpr_compliance": {
                    "data_processing_consent": getattr(user, 'data_processing_consent', True),
                    "data_transfer_consent": getattr(user, 'data_transfer_consent', False),
                    "right_to_erasure": getattr(user, 'right_to_erasure', False),
                    "right_to_portability": getattr(user, 'right_to_portability', True)
                }
            }
            
            return privacy_settings
            
        except Exception as e:
            logger.error(f"Error getting privacy settings for user {user_id}: {e}")
            return None
    
    async def update_privacy_settings(self, user_id: str, privacy_settings: Dict[str, Any]) -> bool:
        """Update user privacy settings via backend"""
        await self._ensure_initialized()
        try:
            # Validate privacy settings
            validated_settings = self._validate_privacy_settings(privacy_settings)
            
            # Update user with privacy settings
            update_data = {}
            
            # Map privacy settings to user fields
            if "data_sharing" in validated_settings:
                data_sharing = validated_settings["data_sharing"]
                for key, value in data_sharing.items():
                    update_data[f"allow_{key}"] = value
            
            if "data_retention" in validated_settings:
                data_retention = validated_settings["data_retention"]
                for key, value in data_retention.items():
                    update_data[f"retention_{key}"] = value
            
            if "data_access" in validated_settings:
                data_access = validated_settings["data_access"]
                for key, value in data_access.items():
                    update_data[f"allow_{key}"] = value
            
            if "notifications" in validated_settings:
                notifications = validated_settings["notifications"]
                for key, value in notifications.items():
                    update_data[f"allow_{key}"] = value
            
            if "gdpr_compliance" in validated_settings:
                gdpr = validated_settings["gdpr_compliance"]
                for key, value in gdpr.items():
                    update_data[f"gdpr_{key}"] = value
            
            # Update user via backend service
            success = await self.user_service.update_user(user_id, update_data)
            
            if success:
                # Create audit log for privacy settings change
                await self.create_audit_log(
                    user_id=user_id,
                    action_type="privacy_settings_updated",
                    action_description="User privacy settings updated",
                    resource_type="user",
                    resource_id=user_id,
                    success=True
                )
                
                logger.info(f"Privacy settings updated for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating privacy settings for user {user_id}: {e}")
            return False
    
    async def export_user_data(self, user_id: str, data_types: List[str] = None) -> Optional[Dict[str, Any]]:
        """Export user data for GDPR compliance via backend"""
        await self._ensure_initialized()
        try:
            if not data_types:
                data_types = ["profile", "activity", "preferences", "sessions"]
            
            # Get user data from backend service
            user_data = await self._export_user_data_from_backend(user_id, data_types)
            
            if not user_data:
                return None
            
            # Add export metadata
            export_data = {
                "user_id": user_id,
                "exported_at": datetime.utcnow().isoformat(),
                "data_types": data_types,
                "data": user_data,
                "format": "json",
                "compliance": {
                    "gdpr_compliant": True,
                    "data_processing_basis": "consent",
                    "retention_period": "as_per_policy"
                }
            }
            
            # Create audit log for data export
            await self.create_audit_log(
                user_id=user_id,
                action_type="data_exported",
                action_description="User data exported for GDPR compliance",
                resource_type="user",
                resource_id=user_id,
                success=True,
                metadata={"data_types": data_types}
            )
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting user data for user {user_id}: {e}")
            return None
    
    async def delete_user_data(self, user_id: str, data_types: List[str] = None) -> bool:
        """Delete user data for GDPR right to erasure via backend"""
        await self._ensure_initialized()
        try:
            if not data_types:
                data_types = ["profile", "activity", "preferences", "sessions"]
            
            # Delete user data via backend service
            success = await self._delete_user_data_from_backend(user_id, data_types)
            
            if success:
                # Create audit log for data deletion
                await self.create_audit_log(
                    user_id=user_id,
                    action_type="data_deleted",
                    action_description="User data deleted for GDPR right to erasure",
                    resource_type="user",
                    resource_id=user_id,
                    success=True,
                    metadata={"data_types": data_types}
                )
                
                logger.info(f"User data deleted for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting user data for user {user_id}: {e}")
            return False
    
    def _get_compliance_tags(self, action_type: str, resource_type: str) -> List[str]:
        """Get compliance tags for an action"""
        tags = []
        
        # Add tags based on action type
        if action_type in ["login", "logout", "password_change", "mfa_setup"]:
            tags.extend(["authentication", "security"])
        
        if action_type in ["data_access", "data_export", "data_deletion"]:
            tags.extend(["data_protection", "gdpr"])
        
        if action_type in ["privacy_settings_updated", "consent_given", "consent_withdrawn"]:
            tags.extend(["privacy", "consent"])
        
        if action_type in ["role_assigned", "permission_granted", "permission_revoked"]:
            tags.extend(["access_control", "authorization"])
        
        # Add tags based on resource type
        if resource_type in ["user", "profile", "preferences"]:
            tags.append("personal_data")
        
        if resource_type in ["organization", "department"]:
            tags.append("business_data")
        
        return list(set(tags))  # Remove duplicates
    
    def _get_default_retention_policy(self) -> Dict[str, Any]:
        """Get default data retention policy"""
        return {
            "user_accounts": {
                "active_users": "indefinite",
                "inactive_users": "2_years",
                "deleted_users": "30_days"
            },
            "audit_logs": {
                "security_events": "7_years",
                "user_activity": "2_years",
                "system_logs": "1_year"
            },
            "personal_data": {
                "profile_information": "7_years",
                "preferences": "2_years",
                "activity_history": "1_year"
            },
            "business_data": {
                "organizations": "indefinite",
                "departments": "indefinite",
                "projects": "10_years"
            },
            "compliance_data": {
                "gdpr_consent": "7_years",
                "data_processing_records": "7_years",
                "regulatory_reports": "10_years"
            }
        }
    
    def _validate_retention_policy(self, policy: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize retention policy data"""
        if not isinstance(policy, dict):
            return self._get_default_retention_policy()
        
        validated = {}
        valid_periods = ["30_days", "90_days", "6_months", "1_year", "2_years", "5_years", "7_years", "10_years", "indefinite"]
        
        for category, settings in policy.items():
            if isinstance(settings, dict):
                validated[category] = {}
                for key, value in settings.items():
                    if isinstance(value, str) and value in valid_periods:
                        validated[category][key] = value
                    else:
                        validated[category][key] = "2_years"  # Default fallback
        
        return validated
    
    def _validate_privacy_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize privacy settings data"""
        if not isinstance(settings, dict):
            return {}
        
        validated = {}
        
        # Validate data sharing settings
        if "data_sharing" in settings and isinstance(settings["data_sharing"], dict):
            data_sharing = settings["data_sharing"]
            validated["data_sharing"] = {}
            
            for key in ["analytics", "marketing", "third_party", "cookies"]:
                if key in data_sharing:
                    validated["data_sharing"][key] = bool(data_sharing[key])
        
        # Validate data retention settings
        if "data_retention" in settings and isinstance(settings["data_retention"], dict):
            data_retention = settings["data_retention"]
            validated["data_retention"] = {}
            
            if "retain_personal_data" in data_retention:
                validated["data_retention"]["retain_personal_data"] = bool(data_retention["retain_personal_data"])
            if "retention_period_days" in data_retention:
                days = int(data_retention["retention_period_days"])
                if 30 <= days <= 3650:  # 30 days to 10 years
                    validated["data_retention"]["retention_period_days"] = days
            if "auto_delete_expired" in data_retention:
                validated["data_retention"]["auto_delete_expired"] = bool(data_retention["auto_delete_expired"])
        
        # Validate data access settings
        if "data_access" in settings and isinstance(settings["data_access"], dict):
            data_access = settings["data_access"]
            validated["data_access"] = {}
            
            for key in ["profile_view", "contact", "online_status", "last_seen"]:
                if key in data_access:
                    validated["data_access"][key] = bool(data_access[key])
        
        # Validate notification settings
        if "notifications" in settings and isinstance(settings["notifications"], dict):
            notifications = settings["notifications"]
            validated["notifications"] = {}
            
            for key in ["email_notifications", "push_notifications", "sms_notifications"]:
                if key in notifications:
                    validated["notifications"][key] = bool(notifications[key])
        
        # Validate GDPR compliance settings
        if "gdpr_compliance" in settings and isinstance(settings["gdpr_compliance"], dict):
            gdpr = settings["gdpr_compliance"]
            validated["gdpr_compliance"] = {}
            
            for key in ["data_processing_consent", "data_transfer_consent", "right_to_erasure", "right_to_portability"]:
                if key in gdpr:
                    validated["gdpr_compliance"][key] = bool(gdpr[key])
        
        return validated
    
    def _parse_json_field(self, field_value: Any) -> Any:
        """Parse JSON field from model"""
        if not field_value:
            return {}
        
        if isinstance(field_value, str):
            try:
                import json
                return json.loads(field_value)
            except:
                return {}
        
        return field_value if isinstance(field_value, (dict, list)) else {}
    
    # Mock backend service methods (in production, these would call actual backend services)
    async def _get_audit_logs_from_backend(self, **kwargs) -> List[Any]:
        """Get audit logs from backend (mock implementation)"""
        await self._ensure_initialized()
        # In production, this would call a real audit service
        return []
    
    async def _create_audit_log_in_backend(self, audit_data: Dict[str, Any]) -> bool:
        """Create audit log in backend (mock implementation)"""
        await self._ensure_initialized()
        # In production, this would call a real audit service
        return True
    
    async def _generate_compliance_report(self, **kwargs) -> Optional[Dict[str, Any]]:
        """Generate compliance report (mock implementation)"""
        await self._ensure_initialized()
        # In production, this would call a real compliance service
        return {"status": "generated", "data": {}}
    
    async def _get_retention_policy_from_backend(self, organization_id: str) -> Optional[Dict[str, Any]]:
        """Get retention policy from backend (mock implementation)"""
        await self._ensure_initialized()
        # In production, this would call a real compliance service
        return None
    
    async def _update_retention_policy_in_backend(self, organization_id: str, policy: Dict[str, Any]) -> bool:
        """Update retention policy in backend (mock implementation)"""
        await self._ensure_initialized()
        # In production, this would call a real compliance service
        return True
    
    async def _export_user_data_from_backend(self, user_id: str, data_types: List[str]) -> Optional[Dict[str, Any]]:
        """Export user data from backend (mock implementation)"""
        await self._ensure_initialized()
        # In production, this would call a real data service
        return {"profile": {}, "activity": [], "preferences": {}}
    
    async def _delete_user_data_from_backend(self, user_id: str, data_types: List[str]) -> bool:
        """Delete user data from backend (mock implementation)"""
        await self._ensure_initialized()
        # In production, this would call a real data service
        return True


# Export the integration service
__all__ = ['ComplianceService']
