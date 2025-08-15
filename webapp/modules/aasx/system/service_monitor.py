"""
Service Monitor Service

Provides service health monitoring, status tracking, and dependency checking
for the AASX-ETL platform with user-based access control.
"""

import logging
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    """Service status enumeration"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"
    UNKNOWN = "unknown"

@dataclass
class ServiceHealth:
    """Service health information"""
    service_name: str
    status: ServiceStatus
    timestamp: datetime
    response_time: float
    error_message: Optional[str] = None
    last_check: Optional[datetime] = None
    uptime: Optional[float] = None
    version: Optional[str] = None
    user_id: Optional[str] = None
    org_id: Optional[str] = None

@dataclass
class ServiceDependency:
    """Service dependency information"""
    service_name: str
    endpoint: str
    expected_status: int
    timeout: float
    check_interval: float
    last_check: Optional[datetime] = None
    is_critical: bool = True

class ServiceMonitor:
    """Service health monitoring service with user-based access control"""
    
    def __init__(self):
        self.is_monitoring = False
        self.monitoring_interval = 10.0  # seconds
        self.service_health_history: List[ServiceHealth] = []
        self.max_history_size = 500
        
        # Core AASX-ETL services to monitor
        self.core_services = {
            'aasx_etl_api': {
                'endpoint': '/api/aasx-etl/health',
                'expected_status': 200,
                'timeout': 5.0,
                'check_interval': 30.0,
                'is_critical': True
            },
            'database': {
                'endpoint': '/api/health/database',
                'expected_status': 200,
                'timeout': 3.0,
                'check_interval': 15.0,
                'is_critical': True
            },
            'authentication': {
                'endpoint': '/api/auth/health',
                'expected_status': 200,
                'timeout': 3.0,
                'check_interval': 20.0,
                'is_critical': True
            }
        }
        
        # User-specific service monitoring
        self.user_services = {}
        
    def start_monitoring(self, user_id: str, org_id: Optional[str] = None) -> bool:
        """Start service monitoring for specific user"""
        try:
            self.is_monitoring = True
            logger.info(f"🚀 Service monitoring started for user: {user_id}")
            
            # Initialize user-specific service monitoring
            self._initialize_user_services(user_id, org_id)
            
            return True
        except Exception as e:
            logger.error(f"❌ Failed to start service monitoring for user {user_id}: {e}")
            return False
    
    def stop_monitoring(self) -> bool:
        """Stop service monitoring"""
        try:
            self.is_monitoring = False
            logger.info("🛑 Service monitoring stopped")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to stop service monitoring: {e}")
            return False
    
    def get_service_health(self, user_id: str, org_id: Optional[str] = None) -> Dict[str, Any]:
        """Get current health status of all monitored services for user"""
        try:
            health_status = {}
            
            # Check core services
            for service_name, service_config in self.core_services.items():
                health = self._check_service_health(service_name, service_config, user_id, org_id)
                health_status[service_name] = asdict(health)
            
            # Check user-specific services
            if user_id in self.user_services:
                for service_name, service_config in self.user_services[user_id].items():
                    health = self._check_service_health(service_name, service_config, user_id, org_id)
                    health_status[service_name] = asdict(health)
            
            return {
                'user_id': user_id,
                'org_id': org_id,
                'timestamp': datetime.now().isoformat(),
                'services': health_status,
                'overall_status': self._determine_overall_status(health_status)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get service health for user {user_id}: {e}")
            return self._get_error_service_health(user_id, org_id)
    
    def get_service_status(self, service_name: str, user_id: str, org_id: Optional[str] = None) -> Optional[ServiceHealth]:
        """Get health status of specific service for user"""
        try:
            # Check if user has access to this service
            if not self._user_can_access_service(service_name, user_id, org_id):
                logger.warning(f"⚠️ User {user_id} cannot access service {service_name}")
                return None
            
            # Get service config
            service_config = self._get_service_config(service_name, user_id, org_id)
            if not service_config:
                return None
            
            # Check service health
            return self._check_service_health(service_name, service_config, user_id, org_id)
            
        except Exception as e:
            logger.error(f"❌ Failed to get service status for {service_name} and user {user_id}: {e}")
            return None
    
    def add_user_service(self, user_id: str, service_name: str, service_config: Dict[str, Any]) -> bool:
        """Add custom service monitoring for specific user"""
        try:
            if user_id not in self.user_services:
                self.user_services[user_id] = {}
            
            # Validate service config
            required_fields = ['endpoint', 'expected_status', 'timeout', 'check_interval']
            if not all(field in service_config for field in required_fields):
                raise ValueError(f"Missing required fields: {required_fields}")
            
            self.user_services[user_id][service_name] = service_config
            logger.info(f"✅ Added custom service {service_name} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add user service {service_name} for user {user_id}: {e}")
            return False
    
    def remove_user_service(self, user_id: str, service_name: str) -> bool:
        """Remove custom service monitoring for specific user"""
        try:
            if user_id in self.user_services and service_name in self.user_services[user_id]:
                del self.user_services[user_id][service_name]
                logger.info(f"✅ Removed custom service {service_name} for user {user_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to remove user service {service_name} for user {user_id}: {e}")
            return False
    
    def get_service_history(self, user_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get service health history for specified user and hours"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            user_records = [
                asdict(record) for record in self.service_health_history
                if record.user_id == user_id and record.timestamp > cutoff_time
            ]
            return user_records
        except Exception as e:
            logger.error(f"❌ Failed to get service history for user {user_id}: {e}")
            return []
    
    def get_user_services(self, user_id: str) -> Dict[str, Any]:
        """Get list of services monitored for specific user"""
        try:
            user_services = {}
            
            # Core services (available to all users)
            user_services.update(self.core_services)
            
            # User-specific services
            if user_id in self.user_services:
                user_services.update(self.user_services[user_id])
            
            return user_services
            
        except Exception as e:
            logger.error(f"❌ Failed to get user services for user {user_id}: {e}")
            return {}
    
    def _initialize_user_services(self, user_id: str, org_id: Optional[str] = None):
        """Initialize user-specific service monitoring"""
        try:
            # Add organization-specific services if org_id provided
            if org_id:
                org_services = self._get_organization_services(org_id)
                for service_name, service_config in org_services.items():
                    self.add_user_service(user_id, service_name, service_config)
            
            logger.info(f"✅ Initialized user services for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize user services for user {user_id}: {e}")
    
    def _check_service_health(self, service_name: str, service_config: Dict[str, Any], 
                             user_id: str, org_id: Optional[str] = None) -> ServiceHealth:
        """Check health of specific service"""
        try:
            start_time = time.time()
            
            # Make health check request
            response = requests.get(
                service_config['endpoint'],
                timeout=service_config['timeout'],
                headers={'User-Id': user_id}
            )
            
            response_time = time.time() - start_time
            
            # Determine service status
            if response.status_code == service_config['expected_status']:
                status = ServiceStatus.HEALTHY
                error_message = None
            elif response.status_code >= 500:
                status = ServiceStatus.CRITICAL
                error_message = f"Server error: {response.status_code}"
            elif response.status_code >= 400:
                status = ServiceStatus.WARNING
                error_message = f"Client error: {response.status_code}"
            else:
                status = ServiceStatus.UNKNOWN
                error_message = f"Unexpected status: {response.status_code}"
            
            # Create health record
            health = ServiceHealth(
                service_name=service_name,
                status=status,
                timestamp=datetime.now(),
                response_time=response_time,
                error_message=error_message,
                last_check=datetime.now(),
                user_id=user_id,
                org_id=org_id
            )
            
            # Store in history
            self._store_service_health_record(health)
            
            return health
            
        except requests.exceptions.Timeout:
            return ServiceHealth(
                service_name=service_name,
                status=ServiceStatus.CRITICAL,
                timestamp=datetime.now(),
                response_time=service_config['timeout'],
                error_message="Request timeout",
                user_id=user_id,
                org_id=org_id
            )
        except requests.exceptions.ConnectionError:
            return ServiceHealth(
                service_name=service_name,
                status=ServiceStatus.OFFLINE,
                timestamp=datetime.now(),
                response_time=0.0,
                error_message="Connection failed",
                user_id=user_id,
                org_id=org_id
            )
        except Exception as e:
            logger.error(f"❌ Service health check failed for {service_name}: {e}")
            return ServiceHealth(
                service_name=service_name,
                status=ServiceStatus.UNKNOWN,
                timestamp=datetime.now(),
                response_time=0.0,
                error_message=str(e),
                user_id=user_id,
                org_id=org_id
            )
    
    def _user_can_access_service(self, service_name: str, user_id: str, org_id: Optional[str] = None) -> bool:
        """Check if user has access to specific service"""
        try:
            # Core services are available to all users
            if service_name in self.core_services:
                return True
            
            # Check user-specific services
            if user_id in self.user_services and service_name in self.user_services[user_id]:
                return True
            
            # Check organization services
            if org_id:
                org_services = self._get_organization_services(org_id)
                if service_name in org_services:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to check service access for user {user_id}: {e}")
            return False
    
    def _get_service_config(self, service_name: str, user_id: str, org_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get service configuration for user"""
        try:
            # Check core services
            if service_name in self.core_services:
                return self.core_services[service_name]
            
            # Check user-specific services
            if user_id in self.user_services and service_name in self.user_services[user_id]:
                return self.user_services[user_id][service_name]
            
            # Check organization services
            if org_id:
                org_services = self._get_organization_services(org_id)
                if service_name in org_services:
                    return org_services[service_name]
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get service config for {service_name} and user {user_id}: {e}")
            return None
    
    def _get_organization_services(self, org_id: str) -> Dict[str, Any]:
        """Get organization-specific services (placeholder for future implementation)"""
        # This would typically query a database or configuration service
        # For now, return empty dict
        return {}
    
    def _determine_overall_status(self, health_status: Dict[str, Any]) -> str:
        """Determine overall system status from individual service statuses"""
        try:
            if not health_status:
                return 'unknown'
            
            status_counts = {'healthy': 0, 'warning': 0, 'critical': 0, 'offline': 0, 'unknown': 0}
            
            for service in health_status.values():
                status = service.get('status', 'unknown')
                if isinstance(status, ServiceStatus):
                    status = status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Determine overall status
            if status_counts['critical'] > 0 or status_counts['offline'] > 0:
                return 'critical'
            elif status_counts['warning'] > 0:
                return 'warning'
            elif status_counts['healthy'] > 0:
                return 'healthy'
            else:
                return 'unknown'
                
        except Exception as e:
            logger.error(f"❌ Failed to determine overall status: {e}")
            return 'unknown'
    
    def _store_service_health_record(self, health: ServiceHealth):
        """Store service health record in history"""
        self.service_health_history.append(health)
        
        # Maintain history size limit
        if len(self.service_health_history) > self.max_history_size:
            self.service_health_history.pop(0)
    
    def _get_error_service_health(self, user_id: str, org_id: Optional[str] = None) -> Dict[str, Any]:
        """Return error service health when monitoring fails"""
        return {
            'user_id': user_id,
            'org_id': org_id,
            'timestamp': datetime.now().isoformat(),
            'services': {},
            'overall_status': 'error',
            'error': 'Service monitoring failed'
        }
