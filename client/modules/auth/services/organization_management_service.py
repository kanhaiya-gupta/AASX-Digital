"""
Organization Management Integration Service - Soft Connection to Backend
=====================================================================

Thin integration layer that connects webapp to backend organization management services.
Handles frontend-specific logic while delegating organization operations to backend.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import from backend engine
from src.engine.services.business_domain.organization_service import OrganizationService

logger = logging.getLogger(__name__)


class OrganizationManagementService:
    """Integration service for organization management operations"""
    
    def __init__(self):
        """Initialize with backend services"""
        try:
            # Initialize backend services
            self.organization_service = OrganizationService()
            
            logger.info("✅ Organization management integration service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize organization management integration service: {e}")
            raise
    
    async def get_organization_settings(self, organization_id: str) -> Optional[Dict[str, Any]]:
        """Get organization settings via backend"""
        try:
            # Get organization details
            organization = await self.organization_service.get_organization_by_id(organization_id)
            if not organization:
                return None
            
            # Extract settings from organization model
            settings = {
                "organization_id": organization.org_id,
                "name": organization.name,
                "branding": {
                    "logo_url": getattr(organization, 'logo_url', None),
                    "primary_color": getattr(organization, 'primary_color', '#1e3c72'),
                    "secondary_color": getattr(organization, 'secondary_color', '#2a5298'),
                    "accent_color": getattr(organization, 'accent_color', '#ffd700'),
                    "company_name": organization.name,
                    "tagline": getattr(organization, 'tagline', None)
                },
                "configuration": {
                    "default_language": getattr(organization, 'default_language', 'en'),
                    "default_timezone": getattr(organization, 'default_timezone', 'UTC'),
                    "session_timeout": getattr(organization, 'session_timeout', 30),
                    "require_mfa": getattr(organization, 'require_mfa', False),
                    "allow_public_profiles": getattr(organization, 'allow_public_profiles', True),
                    "max_file_size_mb": getattr(organization, 'max_file_size_mb', 100),
                    "allowed_file_types": getattr(organization, 'allowed_file_types', 
                                                ["pdf", "doc", "docx", "xls", "xlsx", "txt", "json", "xml"])
                },
                "notifications": {
                    "email_notifications": getattr(organization, 'email_notifications', True),
                    "sms_notifications": getattr(organization, 'sms_notifications', False),
                    "push_notifications": getattr(organization, 'push_notifications', True),
                    "notification_frequency": getattr(organization, 'notification_frequency', 'immediate')
                },
                "security": {
                    "password_policy": {
                        "min_length": getattr(organization, 'password_min_length', 8),
                        "require_uppercase": getattr(organization, 'password_require_uppercase', True),
                        "require_lowercase": getattr(organization, 'password_require_lowercase', True),
                        "require_numbers": getattr(organization, 'password_require_numbers', True),
                        "require_special_chars": getattr(organization, 'password_require_special_chars', False)
                    },
                    "session_management": {
                        "max_concurrent_sessions": getattr(organization, 'max_concurrent_sessions', 5),
                        "session_timeout_minutes": getattr(organization, 'session_timeout_minutes', 30),
                        "remember_me_days": getattr(organization, 'remember_me_days', 30)
                    }
                }
            }
            
            return settings
            
        except Exception as e:
            logger.error(f"Error getting organization settings for {organization_id}: {e}")
            return None
    
    async def update_organization_settings(self, organization_id: str, settings: Dict[str, Any]) -> bool:
        """Update organization settings via backend"""
        try:
            # Validate settings data
            validated_settings = self._validate_settings_data(settings)
            
            # Update organization with new settings
            update_data = {}
            
            # Map settings to organization fields
            if "branding" in validated_settings:
                branding = validated_settings["branding"]
                if "logo_url" in branding:
                    update_data["logo_url"] = branding["logo_url"]
                if "primary_color" in branding:
                    update_data["primary_color"] = branding["primary_color"]
                if "secondary_color" in branding:
                    update_data["secondary_color"] = branding["secondary_color"]
                if "accent_color" in branding:
                    update_data["accent_color"] = branding["accent_color"]
                if "tagline" in branding:
                    update_data["tagline"] = branding["tagline"]
            
            if "configuration" in validated_settings:
                config = validated_settings["configuration"]
                if "default_language" in config:
                    update_data["default_language"] = config["default_language"]
                if "default_timezone" in config:
                    update_data["default_timezone"] = config["default_timezone"]
                if "session_timeout" in config:
                    update_data["session_timeout"] = config["session_timeout"]
                if "require_mfa" in config:
                    update_data["require_mfa"] = config["require_mfa"]
                if "allow_public_profiles" in config:
                    update_data["allow_public_profiles"] = config["allow_public_profiles"]
                if "max_file_size_mb" in config:
                    update_data["max_file_size_mb"] = config["max_file_size_mb"]
                if "allowed_file_types" in config:
                    update_data["allowed_file_types"] = config["allowed_file_types"]
            
            if "notifications" in validated_settings:
                notifications = validated_settings["notifications"]
                if "email_notifications" in notifications:
                    update_data["email_notifications"] = notifications["email_notifications"]
                if "sms_notifications" in notifications:
                    update_data["sms_notifications"] = notifications["sms_notifications"]
                if "push_notifications" in notifications:
                    update_data["push_notifications"] = notifications["push_notifications"]
                if "notification_frequency" in notifications:
                    update_data["notification_frequency"] = notifications["notification_frequency"]
            
            if "security" in validated_settings:
                security = validated_settings["security"]
                if "password_policy" in security:
                    policy = security["password_policy"]
                    if "min_length" in policy:
                        update_data["password_min_length"] = policy["min_length"]
                    if "require_uppercase" in policy:
                        update_data["password_require_uppercase"] = policy["require_uppercase"]
                    if "require_lowercase" in policy:
                        update_data["password_require_lowercase"] = policy["require_lowercase"]
                    if "require_numbers" in policy:
                        update_data["password_require_numbers"] = policy["require_numbers"]
                    if "require_special_chars" in policy:
                        update_data["password_require_special_chars"] = policy["require_special_chars"]
                
                if "session_management" in security:
                    session = security["session_management"]
                    if "max_concurrent_sessions" in session:
                        update_data["max_concurrent_sessions"] = session["max_concurrent_sessions"]
                    if "session_timeout_minutes" in session:
                        update_data["session_timeout_minutes"] = session["session_timeout_minutes"]
                    if "remember_me_days" in session:
                        update_data["remember_me_days"] = session["remember_me_days"]
            
            # Update organization via backend service
            success = await self.organization_service.update_organization(organization_id, update_data)
            
            if success:
                logger.info(f"Organization settings updated for {organization_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating organization settings for {organization_id}: {e}")
            return False
    
    async def get_organization_analytics(self, organization_id: str) -> Optional[Dict[str, Any]]:
        """Get organization analytics via backend"""
        try:
            # Get organization details
            organization = await self.organization_service.get_organization_by_id(organization_id)
            if not organization:
                return None
            
            # Get departments for the organization
            departments = await self.organization_service.get_organization_departments(organization_id)
            
            # Calculate analytics based on organization data
            analytics = {
                "organization_id": organization_id,
                "organization_name": organization.name,
                "user_analytics": {
                    "total_users": getattr(organization, 'total_users', 0),
                    "active_users": getattr(organization, 'active_users', 0),
                    "new_users_this_month": getattr(organization, 'new_users_this_month', 0),
                    "user_growth_rate": getattr(organization, 'user_growth_rate', 0.0)
                },
                "department_analytics": {
                    "total_departments": len(departments),
                    "active_departments": len([d for d in departments if getattr(d, 'is_active', True)]),
                    "department_headcount": sum(getattr(d, 'headcount', 0) for d in departments),
                    "average_department_size": len(departments) > 0 and sum(getattr(d, 'headcount', 0) for d in departments) / len(departments) or 0
                },
                "usage_analytics": {
                    "total_projects": getattr(organization, 'total_projects', 0),
                    "total_files": getattr(organization, 'total_files', 0),
                    "storage_used_gb": getattr(organization, 'storage_used_gb', 0.0),
                    "storage_limit_gb": getattr(organization, 'storage_limit_gb', 10),
                    "api_requests_this_month": getattr(organization, 'api_requests_this_month', 0)
                },
                "performance_metrics": {
                    "average_response_time_ms": getattr(organization, 'average_response_time_ms', 0),
                    "uptime_percentage": getattr(organization, 'uptime_percentage', 99.9),
                    "error_rate": getattr(organization, 'error_rate', 0.0)
                },
                "activity_insights": {
                    "most_active_users": getattr(organization, 'most_active_users', []),
                    "most_used_features": getattr(organization, 'most_used_features', []),
                    "peak_usage_hours": getattr(organization, 'peak_usage_hours', [])
                }
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting organization analytics for {organization_id}: {e}")
            return None
    
    async def update_organization_analytics(self, organization_id: str, analytics: Dict[str, Any]) -> bool:
        """Update organization analytics via backend"""
        try:
            # Validate analytics data
            validated_analytics = self._validate_analytics_data(analytics)
            
            # Update organization with analytics data
            update_data = {}
            
            # Map analytics to organization fields
            if "user_analytics" in validated_analytics:
                user_analytics = validated_analytics["user_analytics"]
                for key, value in user_analytics.items():
                    update_data[f"user_{key}"] = value
            
            if "usage_analytics" in validated_analytics:
                usage_analytics = validated_analytics["usage_analytics"]
                for key, value in usage_analytics.items():
                    update_data[f"usage_{key}"] = value
            
            if "performance_metrics" in validated_analytics:
                performance = validated_analytics["performance_metrics"]
                for key, value in performance.items():
                    update_data[f"performance_{key}"] = value
            
            if "activity_insights" in validated_analytics:
                activity = validated_analytics["activity_insights"]
                for key, value in activity.items():
                    update_data[f"activity_{key}"] = value
            
            # Update organization via backend service
            success = await self.organization_service.update_organization(organization_id, update_data)
            
            if success:
                logger.info(f"Organization analytics updated for {organization_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating organization analytics for {organization_id}: {e}")
            return False
    
    async def get_organization_billing(self, organization_id: str) -> Optional[Dict[str, Any]]:
        """Get organization billing information via backend"""
        try:
            # Get organization details
            organization = await self.organization_service.get_organization_by_id(organization_id)
            if not organization:
                return None
            
            # Extract billing information from organization model
            billing = {
                "organization_id": organization_id,
                "organization_name": organization.name,
                "subscription": {
                    "tier": getattr(organization, 'subscription_tier', 'basic'),
                    "status": getattr(organization, 'subscription_status', 'active'),
                    "start_date": getattr(organization, 'subscription_start_date', None),
                    "end_date": getattr(organization, 'subscription_end_date', None),
                    "auto_renew": getattr(organization, 'subscription_auto_renew', True)
                },
                "billing_info": {
                    "billing_email": getattr(organization, 'billing_email', None),
                    "billing_address": getattr(organization, 'billing_address', None),
                    "payment_method": getattr(organization, 'payment_method', None),
                    "tax_id": getattr(organization, 'tax_id', None)
                },
                "usage_billing": {
                    "current_period_start": getattr(organization, 'billing_period_start', None),
                    "current_period_end": getattr(organization, 'billing_period_end', None),
                    "usage_amount": getattr(organization, 'billing_usage_amount', 0.0),
                    "billing_amount": getattr(organization, 'billing_amount', 0.0),
                    "currency": getattr(organization, 'billing_currency', 'USD')
                },
                "payment_history": getattr(organization, 'payment_history', [])
            }
            
            return billing
            
        except Exception as e:
            logger.error(f"Error getting organization billing for {organization_id}: {e}")
            return None
    
    async def update_organization_billing(self, organization_id: str, billing_data: Dict[str, Any]) -> bool:
        """Update organization billing information via backend"""
        try:
            # Validate billing data
            validated_billing = self._validate_billing_data(billing_data)
            
            # Update organization with billing data
            update_data = {}
            
            # Map billing data to organization fields
            if "subscription" in validated_billing:
                subscription = validated_billing["subscription"]
                for key, value in subscription.items():
                    update_data[f"subscription_{key}"] = value
            
            if "billing_info" in validated_billing:
                billing_info = validated_billing["billing_info"]
                for key, value in billing_info.items():
                    update_data[f"billing_{key}"] = value
            
            if "usage_billing" in validated_billing:
                usage_billing = validated_billing["usage_billing"]
                for key, value in usage_billing.items():
                    update_data[f"billing_{key}"] = value
            
            if "payment_history" in validated_billing:
                update_data["payment_history"] = validated_billing["payment_history"]
            
            # Update organization via backend service
            success = await self.organization_service.update_organization(organization_id, update_data)
            
            if success:
                logger.info(f"Organization billing updated for {organization_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating organization billing for {organization_id}: {e}")
            return False
    
    def _validate_settings_data(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize organization settings data"""
        if not isinstance(settings, dict):
            return {}
        
        validated = {}
        
        # Validate branding settings
        if "branding" in settings and isinstance(settings["branding"], dict):
            branding = settings["branding"]
            validated["branding"] = {}
            
            if "logo_url" in branding:
                validated["branding"]["logo_url"] = str(branding["logo_url"]).strip()
            if "primary_color" in branding and self._is_valid_color(branding["primary_color"]):
                validated["branding"]["primary_color"] = branding["primary_color"]
            if "secondary_color" in branding and self._is_valid_color(branding["secondary_color"]):
                validated["branding"]["secondary_color"] = branding["secondary_color"]
            if "accent_color" in branding and self._is_valid_color(branding["accent_color"]):
                validated["branding"]["accent_color"] = branding["accent_color"]
            if "tagline" in branding:
                tagline = str(branding["tagline"]).strip()
                if len(tagline) <= 200:
                    validated["branding"]["tagline"] = tagline
        
        # Validate configuration settings
        if "configuration" in settings and isinstance(settings["configuration"], dict):
            config = settings["configuration"]
            validated["configuration"] = {}
            
            if "default_language" in config and config["default_language"] in ["en", "es", "fr", "de", "zh", "ja"]:
                validated["configuration"]["default_language"] = config["default_language"]
            if "default_timezone" in config:
                validated["configuration"]["default_timezone"] = str(config["default_timezone"]).strip()
            if "session_timeout" in config:
                timeout = int(config["session_timeout"])
                if 5 <= timeout <= 480:
                    validated["configuration"]["session_timeout"] = timeout
            if "require_mfa" in config:
                validated["configuration"]["require_mfa"] = bool(config["require_mfa"])
            if "allow_public_profiles" in config:
                validated["configuration"]["allow_public_profiles"] = bool(config["allow_public_profiles"])
            if "max_file_size_mb" in config:
                size = int(config["max_file_size_mb"])
                if 1 <= size <= 1000:
                    validated["configuration"]["max_file_size_mb"] = size
            if "allowed_file_types" in config and isinstance(config["allowed_file_types"], list):
                validated["configuration"]["allowed_file_types"] = config["allowed_file_types"]
        
        # Validate notification settings
        if "notifications" in settings and isinstance(settings["notifications"], dict):
            notifications = settings["notifications"]
            validated["notifications"] = {}
            
            if "email_notifications" in notifications:
                validated["notifications"]["email_notifications"] = bool(notifications["email_notifications"])
            if "sms_notifications" in notifications:
                validated["notifications"]["sms_notifications"] = bool(notifications["sms_notifications"])
            if "push_notifications" in notifications:
                validated["notifications"]["push_notifications"] = bool(notifications["push_notifications"])
            if "notification_frequency" in notifications and notifications["notification_frequency"] in ["immediate", "daily", "weekly"]:
                validated["notifications"]["notification_frequency"] = notifications["notification_frequency"]
        
        # Validate security settings
        if "security" in settings and isinstance(settings["security"], dict):
            security = settings["security"]
            validated["security"] = {}
            
            if "password_policy" in security and isinstance(security["password_policy"], dict):
                policy = security["password_policy"]
                validated["security"]["password_policy"] = {}
                
                if "min_length" in policy:
                    length = int(policy["min_length"])
                    if 6 <= length <= 32:
                        validated["security"]["password_policy"]["min_length"] = length
                if "require_uppercase" in policy:
                    validated["security"]["password_policy"]["require_uppercase"] = bool(policy["require_uppercase"])
                if "require_lowercase" in policy:
                    validated["security"]["password_policy"]["require_lowercase"] = bool(policy["require_lowercase"])
                if "require_numbers" in policy:
                    validated["security"]["password_policy"]["require_numbers"] = bool(policy["require_numbers"])
                if "require_special_chars" in policy:
                    validated["security"]["password_policy"]["require_special_chars"] = bool(policy["require_special_chars"])
            
            if "session_management" in security and isinstance(security["session_management"], dict):
                session = security["session_management"]
                validated["security"]["session_management"] = {}
                
                if "max_concurrent_sessions" in session:
                    sessions = int(session["max_concurrent_sessions"])
                    if 1 <= sessions <= 20:
                        validated["security"]["session_management"]["max_concurrent_sessions"] = sessions
                if "session_timeout_minutes" in session:
                    timeout = int(session["session_timeout_minutes"])
                    if 5 <= timeout <= 480:
                        validated["security"]["session_management"]["session_timeout_minutes"] = timeout
                if "remember_me_days" in session:
                    days = int(session["remember_me_days"])
                    if 1 <= days <= 365:
                        validated["security"]["session_management"]["remember_me_days"] = days
        
        return validated
    
    def _validate_analytics_data(self, analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize analytics data"""
        if not isinstance(analytics, dict):
            return {}
        
        validated = {}
        
        # Validate user analytics
        if "user_analytics" in analytics and isinstance(analytics["user_analytics"], dict):
            user_analytics = analytics["user_analytics"]
            validated["user_analytics"] = {}
            
            for key in ["total_users", "active_users", "new_users_this_month"]:
                if key in user_analytics:
                    try:
                        validated["user_analytics"][key] = int(user_analytics[key])
                    except (ValueError, TypeError):
                        pass
            
            if "user_growth_rate" in user_analytics:
                try:
                    rate = float(user_analytics["user_growth_rate"])
                    if -100 <= rate <= 1000:
                        validated["user_analytics"]["user_growth_rate"] = rate
                except (ValueError, TypeError):
                    pass
        
        # Validate usage analytics
        if "usage_analytics" in analytics and isinstance(analytics["usage_analytics"], dict):
            usage_analytics = analytics["usage_analytics"]
            validated["usage_analytics"] = {}
            
            for key in ["total_projects", "total_files", "api_requests_this_month"]:
                if key in usage_analytics:
                    try:
                        validated["usage_analytics"][key] = int(usage_analytics[key])
                    except (ValueError, TypeError):
                        pass
            
            for key in ["storage_used_gb", "storage_limit_gb"]:
                if key in usage_analytics:
                    try:
                        value = float(usage_analytics[key])
                        if 0 <= value <= 10000:
                            validated["usage_analytics"][key] = value
                    except (ValueError, TypeError):
                        pass
        
        # Validate performance metrics
        if "performance_metrics" in analytics and isinstance(analytics["performance_metrics"], dict):
            performance = analytics["performance_metrics"]
            validated["performance_metrics"] = {}
            
            if "average_response_time_ms" in performance:
                try:
                    time = float(performance["average_response_time_ms"])
                    if 0 <= time <= 10000:
                        validated["performance_metrics"]["average_response_time_ms"] = time
                except (ValueError, TypeError):
                    pass
            
            if "uptime_percentage" in performance:
                try:
                    uptime = float(performance["uptime_percentage"])
                    if 0 <= uptime <= 100:
                        validated["performance_metrics"]["uptime_percentage"] = uptime
                except (ValueError, TypeError):
                    pass
            
            if "error_rate" in performance:
                try:
                    rate = float(performance["error_rate"])
                    if 0 <= rate <= 100:
                        validated["performance_metrics"]["error_rate"] = rate
                except (ValueError, TypeError):
                    pass
        
        return validated
    
    def _validate_billing_data(self, billing: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize billing data"""
        if not isinstance(billing, dict):
            return {}
        
        validated = {}
        
        # Validate subscription data
        if "subscription" in billing and isinstance(billing["subscription"], dict):
            subscription = billing["subscription"]
            validated["subscription"] = {}
            
            if "tier" in subscription and subscription["tier"] in ["basic", "pro", "enterprise"]:
                validated["subscription"]["tier"] = subscription["tier"]
            if "status" in subscription and subscription["status"] in ["active", "inactive", "suspended", "cancelled"]:
                validated["subscription"]["status"] = subscription["status"]
            if "auto_renew" in subscription:
                validated["subscription"]["auto_renew"] = bool(subscription["auto_renew"])
        
        # Validate billing info
        if "billing_info" in billing and isinstance(billing["billing_info"], dict):
            billing_info = billing["billing_info"]
            validated["billing_info"] = {}
            
            if "billing_email" in billing_info:
                email = str(billing_info["billing_email"]).strip()
                if "@" in email:
                    validated["billing_info"]["billing_email"] = email
            if "billing_address" in billing_info:
                address = str(billing_info["billing_address"]).strip()
                if len(address) <= 500:
                    validated["billing_info"]["billing_address"] = address
            if "payment_method" in billing_info:
                validated["billing_info"]["payment_method"] = str(billing_info["payment_method"]).strip()
            if "tax_id" in billing_info:
                validated["billing_info"]["tax_id"] = str(billing_info["tax_id"]).strip()
        
        # Validate usage billing
        if "usage_billing" in billing and isinstance(billing["usage_billing"], dict):
            usage_billing = billing["usage_billing"]
            validated["usage_billing"] = {}
            
            if "currency" in usage_billing and usage_billing["currency"] in ["USD", "EUR", "GBP", "JPY"]:
                validated["usage_billing"]["currency"] = usage_billing["currency"]
            
            for key in ["usage_amount", "billing_amount"]:
                if key in usage_billing:
                    try:
                        value = float(usage_billing[key])
                        if 0 <= value <= 1000000:
                            validated["usage_billing"][key] = value
                    except (ValueError, TypeError):
                        pass
        
        # Validate payment history
        if "payment_history" in billing and isinstance(billing["payment_history"], list):
            validated["payment_history"] = billing["payment_history"]
        
        return validated
    
    def _is_valid_color(self, color: str) -> bool:
        """Check if color is valid hex color"""
        import re
        hex_pattern = re.compile(r'^#(?:[0-9a-fA-F]{3}){1,2}$')
        return bool(hex_pattern.match(color))


# Export the integration service
__all__ = ['OrganizationManagementService']
