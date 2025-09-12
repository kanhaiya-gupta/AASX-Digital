"""
Notification Service - Data Platform Real-time Alerts
===================================================

Real-time notification service providing alerts, updates, and communications
across the data platform. Handles user notifications, system alerts, and
automated communications.

Pattern: Lazy initialization with async services for world-class standards
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import json
import uuid

# Import from backend engine
from src.engine.services.auth.user_service import UserService
from src.engine.services.business_domain.organization_service import OrganizationService
from src.engine.repositories.auth_repository import AuthRepository

logger = logging.getLogger(__name__)


class NotificationService:
    """Real-time notification service for data platform"""
    
    def __init__(self):
        """Initialize with backend services - lazy initialization to avoid async issues"""
        self._initialized = False
        self._user_service = None
        self._organization_service = None
        self._auth_repo = None
        
        logger.info("✅ Notification service created (lazy initialization)")
    
    async def _ensure_initialized(self):
        """Ensure services are initialized (lazy initialization)"""
        if self._initialized:
            return
            
        try:
            # Initialize backend services
            self._auth_repo = AuthRepository()
            self._user_service = UserService(self._auth_repo)
            self._organization_service = OrganizationService()
            
            self._initialized = True
            logger.info("✅ Notification service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize notification service: {e}")
            raise
    
    async def send_notification(self, notification_data: Dict[str, Any], 
                              recipients: List[str], 
                              notification_type: str = "info") -> Dict[str, Any]:
        """Send notification to specified recipients"""
        await self._ensure_initialized()
        
        try:
            # Validate notification data
            self._validate_notification_data(notification_data)
            
            # Generate notification ID
            notification_id = str(uuid.uuid4())
            
            # Prepare notification
            notification = {
                "notification_id": notification_id,
                "type": notification_type,
                "title": notification_data.get("title", ""),
                "message": notification_data.get("message", ""),
                "data": notification_data.get("data", {}),
                "recipients": recipients,
                "sender": notification_data.get("sender"),
                "priority": notification_data.get("priority", "normal"),
                "category": notification_data.get("category", "general"),
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": notification_data.get("expires_at"),
                "requires_action": notification_data.get("requires_action", False),
                "action_url": notification_data.get("action_url"),
                "status": "sent"
            }
            
            # Store notification in database
            await self._store_notification(notification)
            
            # Send to recipients
            delivery_results = await self._deliver_notifications(notification, recipients)
            
            # Update notification status
            notification["delivery_results"] = delivery_results
            notification["status"] = "delivered"
            
            logger.info(f"Notification {notification_id} sent to {len(recipients)} recipients")
            
            return {
                "notification_id": notification_id,
                "status": "success",
                "recipients_count": len(recipients),
                "delivery_results": delivery_results
            }
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            raise
    
    async def send_system_alert(self, alert_data: Dict[str, Any], 
                               organization_id: str = None) -> Dict[str, Any]:
        """Send system alert to organization or all users"""
        await self._ensure_initialized()
        
        try:
            # Determine recipients based on alert scope
            if organization_id:
                recipients = await self._get_organization_users(organization_id)
                scope = f"organization_{organization_id}"
            else:
                recipients = await self._get_all_users()
                scope = "global"
            
            # Prepare system alert
            alert_notification = {
                "title": alert_data.get("title", "System Alert"),
                "message": alert_data.get("message", ""),
                "data": alert_data.get("data", {}),
                "sender": "system",
                "priority": alert_data.get("priority", "high"),
                "category": "system_alert",
                "requires_action": alert_data.get("requires_action", False),
                "action_url": alert_data.get("action_url"),
                "scope": scope
            }
            
            # Send notification
            result = await self.send_notification(alert_notification, recipients, "alert")
            
            logger.info(f"System alert sent to {len(recipients)} recipients in scope: {scope}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending system alert: {e}")
            raise
    
    async def send_file_upload_notification(self, file_data: Dict[str, Any], 
                                          project_id: str, 
                                          user_id: str) -> Dict[str, Any]:
        """Send notification for file upload events"""
        await self._ensure_initialized()
        
        try:
            # Get project stakeholders
            stakeholders = await self._get_project_stakeholders(project_id)
            
            # Prepare file upload notification
            notification_data = {
                "title": "New File Uploaded",
                "message": f"File '{file_data.get('original_filename', 'Unknown')}' has been uploaded to the project",
                "data": {
                    "file_id": file_data.get("file_id"),
                    "file_name": file_data.get("original_filename"),
                    "file_size": file_data.get("size_bytes"),
                    "project_id": project_id,
                    "uploaded_by": user_id,
                    "upload_date": datetime.utcnow().isoformat()
                },
                "sender": user_id,
                "priority": "normal",
                "category": "file_management",
                "requires_action": False,
                "action_url": f"/files/{file_data.get('file_id')}"
            }
            
            # Send notification to stakeholders
            result = await self.send_notification(notification_data, stakeholders, "info")
            
            logger.info(f"File upload notification sent for file: {file_data.get('file_id')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending file upload notification: {e}")
            raise
    
    async def send_project_update_notification(self, project_data: Dict[str, Any], 
                                            update_type: str, 
                                            user_id: str) -> Dict[str, Any]:
        """Send notification for project updates"""
        await self._ensure_initialized()
        
        try:
            # Get project stakeholders
            project_id = project_data.get("project_id")
            stakeholders = await self._get_project_stakeholders(project_id)
            
            # Prepare project update notification
            notification_data = {
                "title": f"Project {update_type.title()}",
                "message": f"Project '{project_data.get('name', 'Unknown')}' has been {update_type}",
                "data": {
                    "project_id": project_id,
                    "project_name": project_data.get("name"),
                    "update_type": update_type,
                    "updated_by": user_id,
                    "update_date": datetime.utcnow().isoformat(),
                    "changes": project_data.get("changes", {})
                },
                "sender": user_id,
                "priority": "normal",
                "category": "project_management",
                "requires_action": False,
                "action_url": f"/projects/{project_id}"
            }
            
            # Send notification to stakeholders
            result = await self.send_notification(notification_data, stakeholders, "info")
            
            logger.info(f"Project {update_type} notification sent for project: {project_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending project update notification: {e}")
            raise
    
    async def send_storage_alert(self, alert_type: str, 
                               organization_id: str, 
                               alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send storage-related alerts"""
        await self._ensure_initialized()
        
        try:
            # Get organization admins
            admins = await self._get_organization_admins(organization_id)
            
            # Prepare storage alert
            alert_notification = {
                "title": f"Storage {alert_type.title()} Alert",
                "message": alert_data.get("message", f"Storage {alert_type} alert for your organization"),
                "data": {
                    "alert_type": alert_type,
                    "organization_id": organization_id,
                    "current_usage": alert_data.get("current_usage"),
                    "threshold": alert_data.get("threshold"),
                    "alert_date": datetime.utcnow().isoformat()
                },
                "sender": "system",
                "priority": "high" if alert_type in ["critical", "quota_exceeded"] else "normal",
                "category": "storage_management",
                "requires_action": True,
                "action_url": "/storage/analytics"
            }
            
            # Send notification to admins
            result = await self.send_notification(alert_notification, admins, "alert")
            
            logger.info(f"Storage {alert_type} alert sent to organization: {organization_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending storage alert: {e}")
            raise
    
    async def get_user_notifications(self, user_id: str, 
                                   status: str = None, 
                                   limit: int = 50, 
                                   offset: int = 0) -> List[Dict[str, Any]]:
        """Get notifications for a specific user"""
        await self._ensure_initialized()
        
        try:
            # Get user notifications from database
            notifications = await self._get_user_notifications_from_db(user_id, status, limit, offset)
            
            return notifications
            
        except Exception as e:
            logger.error(f"Error getting user notifications: {e}")
            raise
    
    async def mark_notification_read(self, notification_id: str, user_id: str) -> bool:
        """Mark a notification as read for a user"""
        await self._ensure_initialized()
        
        try:
            # Update notification status in database
            success = await self._mark_notification_read_in_db(notification_id, user_id)
            
            if success:
                logger.info(f"Notification {notification_id} marked as read by user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            raise
    
    async def mark_notification_actioned(self, notification_id: str, user_id: str, 
                                       action_taken: str = None) -> bool:
        """Mark a notification as actioned by a user"""
        await self._ensure_initialized()
        
        try:
            # Update notification status in database
            success = await self._mark_notification_actioned_in_db(notification_id, user_id, action_taken)
            
            if success:
                logger.info(f"Notification {notification_id} marked as actioned by user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error marking notification as actioned: {e}")
            raise
    
    async def get_notification_statistics(self, user_id: str, 
                                        organization_id: str = None, 
                                        time_range: str = "30d") -> Dict[str, Any]:
        """Get notification statistics for analytics"""
        await self._ensure_initialized()
        
        try:
            # Calculate time range
            end_date = datetime.utcnow()
            start_date = self._calculate_start_date(end_date, time_range)
            
            # Get notification statistics
            stats = await self._get_notification_stats_from_db(start_date, end_date, user_id, organization_id)
            
            return {
                "time_range": time_range,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "statistics": stats
            }
            
        except Exception as e:
            logger.error(f"Error getting notification statistics: {e}")
            raise
    
    async def update_notification_preferences(self, user_id: str, 
                                           preferences: Dict[str, Any]) -> bool:
        """Update user notification preferences"""
        await self._ensure_initialized()
        
        try:
            # Validate preferences
            self._validate_notification_preferences(preferences)
            
            # Update preferences in database
            success = await self._update_notification_preferences_in_db(user_id, preferences)
            
            if success:
                logger.info(f"Notification preferences updated for user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating notification preferences: {e}")
            raise
    
    def _validate_notification_data(self, notification_data: Dict[str, Any]):
        """Validate notification data"""
        required_fields = ["title", "message"]
        for field in required_fields:
            if not notification_data.get(field):
                raise ValueError(f"Missing required field: {field}")
        
        # Validate priority
        valid_priorities = ["low", "normal", "high", "critical"]
        if notification_data.get("priority") and notification_data["priority"] not in valid_priorities:
            raise ValueError(f"Invalid priority: {notification_data['priority']}")
        
        # Validate category
        valid_categories = ["general", "file_management", "project_management", "user_management", 
                          "organization_management", "system_alert", "storage_management"]
        if notification_data.get("category") and notification_data["category"] not in valid_categories:
            raise ValueError(f"Invalid category: {notification_data['category']}")
    
    def _validate_notification_preferences(self, preferences: Dict[str, Any]):
        """Validate notification preferences"""
        valid_channels = ["email", "in_app", "push", "sms"]
        valid_frequencies = ["immediate", "daily", "weekly", "never"]
        
        for channel, settings in preferences.items():
            if channel not in valid_channels:
                raise ValueError(f"Invalid notification channel: {channel}")
            
            if isinstance(settings, dict):
                if "enabled" in settings and not isinstance(settings["enabled"], bool):
                    raise ValueError(f"Invalid enabled value for {channel}")
                
                if "frequency" in settings and settings["frequency"] not in valid_frequencies:
                    raise ValueError(f"Invalid frequency for {channel}")
    
    async def _store_notification(self, notification: Dict[str, Any]) -> bool:
        """Store notification in database"""
        try:
            # This would store the notification in the database
            # For now, just log the action
            logger.debug(f"Storing notification: {notification['notification_id']}")
            return True
        except Exception as e:
            logger.error(f"Error storing notification: {e}")
            return False
    
    async def _deliver_notifications(self, notification: Dict[str, Any], 
                                   recipients: List[str]) -> Dict[str, Any]:
        """Deliver notifications to recipients"""
        try:
            delivery_results = {
                "total_recipients": len(recipients),
                "successful_deliveries": 0,
                "failed_deliveries": 0,
                "delivery_details": {}
            }
            
            for recipient_id in recipients:
                try:
                    # Get user preferences
                    user_preferences = await self._get_user_notification_preferences(recipient_id)
                    
                    # Deliver based on preferences
                    delivery_success = await self._deliver_to_user(notification, recipient_id, user_preferences)
                    
                    if delivery_success:
                        delivery_results["successful_deliveries"] += 1
                        delivery_results["delivery_details"][recipient_id] = "success"
                    else:
                        delivery_results["failed_deliveries"] += 1
                        delivery_results["delivery_details"][recipient_id] = "failed"
                        
                except Exception as e:
                    logger.error(f"Error delivering to recipient {recipient_id}: {e}")
                    delivery_results["failed_deliveries"] += 1
                    delivery_results["delivery_details"][recipient_id] = "error"
            
            return delivery_results
            
        except Exception as e:
            logger.error(f"Error delivering notifications: {e}")
            return {"error": str(e)}
    
    async def _deliver_to_user(self, notification: Dict[str, Any], 
                              user_id: str, 
                              preferences: Dict[str, Any]) -> bool:
        """Deliver notification to a specific user"""
        try:
            # Check if user has notifications enabled
            if not preferences.get("notifications_enabled", True):
                return False
            
            # Deliver based on channel preferences
            delivery_success = False
            
            # In-app notification (always enabled)
            delivery_success = await self._deliver_in_app(notification, user_id) or delivery_success
            
            # Email notification
            if preferences.get("email", {}).get("enabled", False):
                email_success = await self._deliver_email(notification, user_id)
                delivery_success = email_success or delivery_success
            
            # Push notification
            if preferences.get("push", {}).get("enabled", False):
                push_success = await self._deliver_push(notification, user_id)
                delivery_success = push_success or delivery_success
            
            # SMS notification
            if preferences.get("sms", {}).get("enabled", False):
                sms_success = await self._deliver_sms(notification, user_id)
                delivery_success = sms_success or delivery_success
            
            return delivery_success
            
        except Exception as e:
            logger.error(f"Error delivering to user {user_id}: {e}")
            return False
    
    async def _deliver_in_app(self, notification: Dict[str, Any], user_id: str) -> bool:
        """Deliver in-app notification"""
        try:
            # This would implement in-app notification delivery
            # For now, just return success
            return True
        except Exception as e:
            logger.error(f"Error delivering in-app notification: {e}")
            return False
    
    async def _deliver_email(self, notification: Dict[str, Any], user_id: str) -> bool:
        """Deliver email notification"""
        try:
            # This would implement email notification delivery
            # For now, just return success
            return True
        except Exception as e:
            logger.error(f"Error delivering email notification: {e}")
            return False
    
    async def _deliver_push(self, notification: Dict[str, Any], user_id: str) -> bool:
        """Deliver push notification"""
        try:
            # This would implement push notification delivery
            # For now, just return success
            return True
        except Exception as e:
            logger.error(f"Error delivering push notification: {e}")
            return False
    
    async def _deliver_sms(self, notification: Dict[str, Any], user_id: str) -> bool:
        """Deliver SMS notification"""
        try:
            # This would implement SMS notification delivery
            # For now, just return success
            return True
        except Exception as e:
            logger.error(f"Error delivering SMS notification: {e}")
            return False
    
    async def _get_organization_users(self, organization_id: str) -> List[str]:
        """Get all users in an organization"""
        try:
            # This would query the database for organization users
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Error getting organization users: {e}")
            return []
    
    async def _get_all_users(self) -> List[str]:
        """Get all users in the system"""
        try:
            # This would query the database for all users
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    async def _get_project_stakeholders(self, project_id: str) -> List[str]:
        """Get project stakeholders for notifications"""
        try:
            # This would query the database for project stakeholders
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Error getting project stakeholders: {e}")
            return []
    
    async def _get_organization_admins(self, organization_id: str) -> List[str]:
        """Get organization administrators"""
        try:
            # This would query the database for organization admins
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Error getting organization admins: {e}")
            return []
    
    async def _get_user_notifications_from_db(self, user_id: str, status: str = None, 
                                            limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get user notifications from database"""
        try:
            # This would query the database for user notifications
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Error getting user notifications from database: {e}")
            return []
    
    async def _mark_notification_read_in_db(self, notification_id: str, user_id: str) -> bool:
        """Mark notification as read in database"""
        try:
            # This would update the database
            # For now, return success
            return True
        except Exception as e:
            logger.error(f"Error marking notification as read in database: {e}")
            return False
    
    async def _mark_notification_actioned_in_db(self, notification_id: str, user_id: str, 
                                              action_taken: str = None) -> bool:
        """Mark notification as actioned in database"""
        try:
            # This would update the database
            # For now, return success
            return True
        except Exception as e:
            logger.error(f"Error marking notification as actioned in database: {e}")
            return False
    
    async def _get_notification_stats_from_db(self, start_date: datetime, end_date: datetime, 
                                            user_id: str, organization_id: str = None) -> Dict[str, Any]:
        """Get notification statistics from database"""
        try:
            # This would query the database for notification statistics
            # For now, return mock data
            return {
                "total_notifications": 0,
                "read_notifications": 0,
                "unread_notifications": 0,
                "actioned_notifications": 0,
                "notifications_by_type": {},
                "notifications_by_category": {},
                "delivery_success_rate": 0
            }
        except Exception as e:
            logger.error(f"Error getting notification statistics from database: {e}")
            return {}
    
    async def _update_notification_preferences_in_db(self, user_id: str, 
                                                   preferences: Dict[str, Any]) -> bool:
        """Update notification preferences in database"""
        try:
            # This would update the database
            # For now, return success
            return True
        except Exception as e:
            logger.error(f"Error updating notification preferences in database: {e}")
            return False
    
    async def _get_user_notification_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user notification preferences"""
        try:
            # This would query the database for user preferences
            # For now, return default preferences
            return {
                "notifications_enabled": True,
                "email": {"enabled": True, "frequency": "immediate"},
                "in_app": {"enabled": True, "frequency": "immediate"},
                "push": {"enabled": False, "frequency": "never"},
                "sms": {"enabled": False, "frequency": "never"}
            }
        except Exception as e:
            logger.error(f"Error getting user notification preferences: {e}")
            return {}
    
    def _calculate_start_date(self, end_date: datetime, time_range: str) -> datetime:
        """Calculate start date based on time range"""
        if time_range == "7d":
            return end_date - timedelta(days=7)
        elif time_range == "30d":
            return end_date - timedelta(days=30)
        elif time_range == "90d":
            return end_date - timedelta(days=90)
        else:
            return end_date - timedelta(days=30)
