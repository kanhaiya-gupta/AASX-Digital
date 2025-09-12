"""
Security Utilities
=================

Security and threat detection utility functions for federated learning.
Handles authentication, authorization, threat detection, and security monitoring.
"""

import asyncio
import hashlib
import secrets
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService


@dataclass
class SecurityConfig:
    """Configuration for security utilities"""
    # Security methods
    authentication_enabled: bool = True
    authorization_enabled: bool = True
    threat_detection_enabled: bool = True
    encryption_enabled: bool = True
    
    # Authentication settings
    jwt_secret: str = "default_secret_change_in_production"
    jwt_expiry_hours: int = 24
    password_min_length: int = 12
    password_complexity_required: bool = True
    
    # Authorization settings
    role_based_access_control: bool = True
    permission_validation: bool = True
    session_timeout_minutes: int = 30
    
    # Threat detection settings
    anomaly_detection_enabled: bool = True
    intrusion_detection_enabled: bool = True
    rate_limiting_enabled: bool = True
    
    # Security thresholds
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    suspicious_activity_threshold: float = 0.8


@dataclass
class SecurityMetrics:
    """Metrics for security operations"""
    # Authentication metrics
    successful_logins: int = 0
    failed_logins: int = 0
    locked_accounts: int = 0
    active_sessions: int = 0
    
    # Authorization metrics
    access_denied_count: int = 0
    permission_violations: int = 0
    role_changes: int = 0
    
    # Threat detection metrics
    threats_detected: int = 0
    false_positives: int = 0
    security_incidents: int = 0
    
    # Security scores
    overall_security_score: float = 0.0
    authentication_score: float = 0.0
    authorization_score: float = 0.0
    threat_detection_score: float = 0.0
    
    # Performance metrics
    security_check_time: float = 0.0
    threat_analysis_time: float = 0.0


class SecurityUtils:
    """Security utility functions for federated learning"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService,
        config: Optional[SecurityConfig] = None
    ):
        """Initialize Security Utils"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        self.config = config or SecurityConfig()
        
        # Security state
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.failed_login_attempts: Dict[str, Dict[str, Any]] = {}
        self.security_alerts: List[Dict[str, Any]] = []
        
        # Metrics tracking
        self.metrics = SecurityMetrics()
        
        # Security monitoring state
        self.monitoring_active = False
        self.threat_detection_active = False
        
    async def authenticate_user(
        self,
        username: str,
        password: str,
        additional_factors: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Authenticate a user with credentials and optional additional factors"""
        try:
            start_time = datetime.now()
            
            print(f"🔐 Authenticating user: {username}")
            
            # Check if account is locked
            if await self._is_account_locked(username):
                return {
                    'success': False,
                    'error': 'Account is temporarily locked due to multiple failed attempts',
                    'lockout_remaining': await self._get_lockout_remaining(username)
                }
            
            # Validate credentials (simplified for demonstration)
            # In practice, this would check against a secure user database
            if await self._validate_credentials(username, password):
                # Generate JWT token
                token = await self._generate_jwt_token(username, additional_factors)
                
                # Create session
                session = await self._create_user_session(username, token)
                
                # Update metrics
                self.metrics.successful_logins += 1
                self.metrics.active_sessions += 1
                
                # Reset failed login attempts
                if username in self.failed_login_attempts:
                    del self.failed_login_attempts[username]
                
                # Calculate authentication time
                auth_time = (datetime.now() - start_time).total_seconds()
                self.metrics.security_check_time = auth_time
                
                print(f"✅ User {username} authenticated successfully")
                
                return {
                    'success': True,
                    'token': token,
                    'session_id': session['session_id'],
                    'expires_at': session['expires_at'],
                    'user_info': session['user_info']
                }
            else:
                # Record failed login attempt
                await self._record_failed_login(username)
                
                # Update metrics
                self.metrics.failed_logins += 1
                
                return {
                    'success': False,
                    'error': 'Invalid credentials',
                    'remaining_attempts': self.config.max_login_attempts - self.failed_login_attempts.get(username, {}).get('attempts', 0)
                }
                
        except Exception as e:
            print(f"❌ User authentication failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _is_account_locked(self, username: str) -> bool:
        """Check if user account is locked"""
        try:
            if username not in self.failed_login_attempts:
                return False
            
            user_attempts = self.failed_login_attempts[username]
            if user_attempts['attempts'] >= self.config.max_login_attempts:
                lockout_time = user_attempts['last_attempt']
                lockout_end = lockout_time + timedelta(minutes=self.config.lockout_duration_minutes)
                
                if datetime.now() < lockout_end:
                    return True
                else:
                    # Lockout expired, reset attempts
                    del self.failed_login_attempts[username]
            
            return False
            
        except Exception as e:
            print(f"⚠️  Account lock check failed: {e}")
            return False
    
    async def _get_lockout_remaining(self, username: str) -> int:
        """Get remaining lockout time in minutes"""
        try:
            if username not in self.failed_login_attempts:
                return 0
            
            user_attempts = self.failed_login_attempts[username]
            lockout_time = user_attempts['last_attempt']
            lockout_end = lockout_time + timedelta(minutes=self.config.lockout_duration_minutes)
            
            remaining = (lockout_end - datetime.now()).total_seconds() / 60
            return max(0, int(remaining))
            
        except Exception as e:
            print(f"⚠️  Lockout remaining calculation failed: {e}")
            return 0
    
    async def _validate_credentials(self, username: str, password: str) -> bool:
        """Validate user credentials"""
        try:
            # Simplified credential validation
            # In practice, this would use secure password hashing and database lookup
            
            # Check password length
            if len(password) < self.config.password_min_length:
                return False
            
            # Check password complexity
            if self.config.password_complexity_required:
                if not self._check_password_complexity(password):
                    return False
            
            # Simulate credential check (80% success rate for demonstration)
            return np.random.choice([True, False], p=[0.8, 0.2])
            
        except Exception as e:
            print(f"⚠️  Credential validation failed: {e}")
            return False
    
    def _check_password_complexity(self, password: str) -> bool:
        """Check password complexity requirements"""
        try:
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
            
            return has_upper and has_lower and has_digit and has_special
            
        except Exception as e:
            print(f"⚠️  Password complexity check failed: {e}")
            return False
    
    async def _generate_jwt_token(self, username: str, additional_factors: Dict[str, Any] = None) -> str:
        """Generate JWT token for authenticated user"""
        try:
            # Simplified JWT generation
            # In practice, use proper JWT libraries like PyJWT
            
            payload = {
                'username': username,
                'iat': datetime.now().timestamp(),
                'exp': (datetime.now() + timedelta(hours=self.config.jwt_expiry_hours)).timestamp(),
                'additional_factors': additional_factors or {}
            }
            
            # Create token (simplified)
            token_data = f"{username}:{payload['exp']}:{self.config.jwt_secret}"
            token_hash = hashlib.sha256(token_data.encode()).hexdigest()
            
            return f"jwt.{token_hash[:32]}.{token_hash[32:64]}"
            
        except Exception as e:
            print(f"❌ JWT token generation failed: {e}")
            raise
    
    async def _create_user_session(self, username: str, token: str) -> Dict[str, Any]:
        """Create user session"""
        try:
            session_id = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(minutes=self.config.session_timeout_minutes)
            
            session = {
                'session_id': session_id,
                'username': username,
                'token': token,
                'created_at': datetime.now(),
                'expires_at': expires_at,
                'last_activity': datetime.now(),
                'user_info': {
                    'username': username,
                    'roles': ['user'],  # Default role
                    'permissions': ['read', 'write']  # Default permissions
                }
            }
            
            self.active_sessions[session_id] = session
            
            return session
            
        except Exception as e:
            print(f"❌ Session creation failed: {e}")
            raise
    
    async def _record_failed_login(self, username: str):
        """Record failed login attempt"""
        try:
            if username not in self.failed_login_attempts:
                self.failed_login_attempts[username] = {
                    'attempts': 0,
                    'first_attempt': datetime.now(),
                    'last_attempt': datetime.now()
                }
            
            self.failed_login_attempts[username]['attempts'] += 1
            self.failed_login_attempts[username]['last_attempt'] = datetime.now()
            
            # Check if account should be locked
            if self.failed_login_attempts[username]['attempts'] >= self.config.max_login_attempts:
                self.metrics.locked_accounts += 1
                print(f"🔒 Account {username} locked due to multiple failed attempts")
            
        except Exception as e:
            print(f"⚠️  Failed login recording failed: {e}")
    
    async def authorize_access(
        self,
        session_id: str,
        resource: str,
        action: str
    ) -> Dict[str, Any]:
        """Authorize user access to a resource"""
        try:
            # Validate session
            if session_id not in self.active_sessions:
                return {'authorized': False, 'error': 'Invalid session'}
            
            session = self.active_sessions[session_id]
            
            # Check session expiration
            if datetime.now() > session['expires_at']:
                await self._terminate_session(session_id)
                return {'authorized': False, 'error': 'Session expired'}
            
            # Update last activity
            session['last_activity'] = datetime.now()
            
            # Check permissions
            if await self._check_permissions(session['user_info'], resource, action):
                return {'authorized': True, 'user_info': session['user_info']}
            else:
                # Record access denial
                self.metrics.access_denied_count += 1
                return {'authorized': False, 'error': 'Insufficient permissions'}
                
        except Exception as e:
            print(f"❌ Access authorization failed: {e}")
            return {'authorized': False, 'error': str(e)}
    
    async def _check_permissions(self, user_info: Dict[str, Any], resource: str, action: str) -> bool:
        """Check if user has permission for resource and action"""
        try:
            # Simplified permission checking
            # In practice, this would use a proper RBAC system
            
            user_permissions = user_info.get('permissions', [])
            user_roles = user_info.get('roles', [])
            
            # Check if user has required permission
            required_permission = f"{action}:{resource}"
            
            # Admin role has all permissions
            if 'admin' in user_roles:
                return True
            
            # Check specific permissions
            if required_permission in user_permissions:
                return True
            
            # Check wildcard permissions
            if f"{action}:*" in user_permissions:
                return True
            
            return False
            
        except Exception as e:
            print(f"⚠️  Permission check failed: {e}")
            return False
    
    async def _terminate_session(self, session_id: str):
        """Terminate user session"""
        try:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
                self.metrics.active_sessions -= 1
                print(f"🔓 Session {session_id} terminated")
            
        except Exception as e:
            print(f"⚠️  Session termination failed: {e}")
    
    async def detect_threats(
        self,
        activity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect security threats from activity data"""
        try:
            start_time = datetime.now()
            
            print("🔍 Analyzing activity for security threats...")
            
            threat_analysis = {
                'threats_detected': [],
                'risk_score': 0.0,
                'recommendations': [],
                'timestamp': datetime.now().isoformat()
            }
            
            # Anomaly detection
            if self.config.anomaly_detection_enabled:
                anomalies = await self._detect_anomalies(activity_data)
                threat_analysis['threats_detected'].extend(anomalies)
            
            # Intrusion detection
            if self.config.intrusion_detection_enabled:
                intrusions = await self._detect_intrusions(activity_data)
                threat_analysis['threats_detected'].extend(intrusions)
            
            # Rate limiting check
            if self.config.rate_limiting_enabled:
                rate_violations = await self._check_rate_limiting(activity_data)
                threat_analysis['threats_detected'].extend(rate_violations)
            
            # Calculate risk score
            threat_analysis['risk_score'] = await self._calculate_risk_score(threat_analysis['threats_detected'])
            
            # Generate recommendations
            threat_analysis['recommendations'] = await self._generate_security_recommendations(threat_analysis)
            
            # Update metrics
            self.metrics.threats_detected += len(threat_analysis['threats_detected'])
            self.metrics.threat_analysis_time = (datetime.now() - start_time).total_seconds()
            
            # Record security alerts
            if threat_analysis['threats_detected']:
                await self._record_security_alert(threat_analysis)
            
            print(f"✅ Threat analysis completed: {len(threat_analysis['threats_detected'])} threats detected")
            
            return threat_analysis
            
        except Exception as e:
            print(f"❌ Threat detection failed: {e}")
            return {'error': str(e)}
    
    async def _detect_anomalies(self, activity_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalous behavior patterns"""
        try:
            anomalies = []
            
            # Check for unusual login patterns
            if 'login_attempts' in activity_data:
                login_count = activity_data['login_attempts']
                if login_count > 10:  # Threshold for unusual activity
                    anomalies.append({
                        'type': 'anomaly',
                        'category': 'login_pattern',
                        'severity': 'medium',
                        'description': f"Unusual number of login attempts: {login_count}",
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Check for unusual access patterns
            if 'resource_access' in activity_data:
                access_patterns = activity_data['resource_access']
                if len(access_patterns) > 50:  # Threshold for unusual access
                    anomalies.append({
                        'type': 'anomaly',
                        'category': 'access_pattern',
                        'severity': 'medium',
                        'description': f"Unusual number of resource accesses: {len(access_patterns)}",
                        'timestamp': datetime.now().isoformat()
                    })
            
            return anomalies
            
        except Exception as e:
            print(f"⚠️  Anomaly detection failed: {e}")
            return []
    
    async def _detect_intrusions(self, activity_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect potential intrusion attempts"""
        try:
            intrusions = []
            
            # Check for failed authentication attempts
            if 'failed_auth' in activity_data:
                failed_auth = activity_data['failed_auth']
                if failed_auth > 5:  # Threshold for intrusion detection
                    intrusions.append({
                        'type': 'intrusion',
                        'category': 'authentication',
                        'severity': 'high',
                        'description': f"Multiple failed authentication attempts: {failed_auth}",
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Check for suspicious IP addresses
            if 'suspicious_ips' in activity_data:
                suspicious_ips = activity_data['suspicious_ips']
                if suspicious_ips:
                    intrusions.append({
                        'type': 'intrusion',
                        'category': 'network',
                        'severity': 'medium',
                        'description': f"Suspicious IP addresses detected: {suspicious_ips}",
                        'timestamp': datetime.now().isoformat()
                    })
            
            return intrusions
            
        except Exception as e:
            print(f"⚠️  Intrusion detection failed: {e}")
            return []
    
    async def _check_rate_limiting(self, activity_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for rate limiting violations"""
        try:
            violations = []
            
            # Check API rate limiting
            if 'api_calls' in activity_data:
                api_calls = activity_data['api_calls']
                if api_calls > 100:  # Threshold for API rate limiting
                    violations.append({
                        'type': 'rate_limit',
                        'category': 'api',
                        'severity': 'low',
                        'description': f"API rate limit exceeded: {api_calls} calls",
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Check login rate limiting
            if 'login_rate' in activity_data:
                login_rate = activity_data['login_rate']
                if login_rate > 10:  # Threshold for login rate limiting
                    violations.append({
                        'type': 'rate_limit',
                        'category': 'authentication',
                        'severity': 'medium',
                        'description': f"Login rate limit exceeded: {login_rate} attempts per minute",
                        'timestamp': datetime.now().isoformat()
                    })
            
            return violations
            
        except Exception as e:
            print(f"⚠️  Rate limiting check failed: {e}")
            return []
    
    async def _calculate_risk_score(self, threats: List[Dict[str, Any]]) -> float:
        """Calculate overall security risk score"""
        try:
            if not threats:
                return 0.0
            
            # Calculate risk score based on threat severity and count
            severity_weights = {
                'low': 0.1,
                'medium': 0.5,
                'high': 1.0,
                'critical': 2.0
            }
            
            total_risk = 0.0
            for threat in threats:
                severity = threat.get('severity', 'low')
                weight = severity_weights.get(severity, 0.1)
                total_risk += weight
            
            # Normalize risk score to 0-1 range
            max_possible_risk = len(threats) * 2.0  # Assuming all threats are critical
            risk_score = min(1.0, total_risk / max_possible_risk) if max_possible_risk > 0 else 0.0
            
            return risk_score
            
        except Exception as e:
            print(f"⚠️  Risk score calculation failed: {e}")
            return 0.0
    
    async def _generate_security_recommendations(self, threat_analysis: Dict[str, Any]) -> List[str]:
        """Generate security improvement recommendations"""
        try:
            recommendations = []
            
            # General recommendations
            if threat_analysis['risk_score'] > 0.7:
                recommendations.append("High security risk detected. Immediate action required.")
            
            if threat_analysis['risk_score'] > 0.5:
                recommendations.append("Medium security risk detected. Review and address threats promptly.")
            
            # Specific recommendations based on threat types
            threat_types = [threat['type'] for threat in threat_analysis['threats_detected']]
            
            if 'intrusion' in threat_types:
                recommendations.append("Implement additional intrusion detection measures.")
                recommendations.append("Review and strengthen authentication mechanisms.")
            
            if 'anomaly' in threat_types:
                recommendations.append("Enhance anomaly detection algorithms.")
                recommendations.append("Implement behavioral analysis for user activity.")
            
            if 'rate_limit' in threat_types:
                recommendations.append("Adjust rate limiting thresholds based on normal usage patterns.")
                recommendations.append("Implement adaptive rate limiting.")
            
            # Always include general security recommendations
            recommendations.extend([
                "Regular security audits and penetration testing",
                "Employee security awareness training",
                "Keep security systems and software updated",
                "Implement multi-factor authentication where possible"
            ])
            
            return recommendations
            
        except Exception as e:
            print(f"⚠️  Security recommendation generation failed: {e}")
            return ["Unable to generate recommendations due to error"]
    
    async def _record_security_alert(self, threat_analysis: Dict[str, Any]):
        """Record security alert for threat analysis"""
        try:
            alert = {
                'timestamp': datetime.now().isoformat(),
                'threat_count': len(threat_analysis['threats_detected']),
                'risk_score': threat_analysis['risk_score'],
                'threat_types': list(set([threat['type'] for threat in threat_analysis['threats_detected']])),
                'recommendations_count': len(threat_analysis['recommendations'])
            }
            
            self.security_alerts.append(alert)
            
            # Update metrics
            self.metrics.security_incidents += 1
            
        except Exception as e:
            print(f"⚠️  Security alert recording failed: {e}")
    
    async def get_security_report(self) -> Dict[str, Any]:
        """Get comprehensive security report"""
        try:
            return {
                'security_metrics': self.metrics.__dict__,
                'security_alerts': self.security_alerts,
                'active_sessions_count': len(self.active_sessions),
                'locked_accounts_count': len([u for u, data in self.failed_login_attempts.items() 
                                           if data['attempts'] >= self.config.max_login_attempts]),
                'current_config': self.config.__dict__
            }
            
        except Exception as e:
            print(f"❌ Security report generation failed: {e}")
            return {'error': str(e)}
    
    async def reset_metrics(self):
        """Reset security metrics"""
        try:
            self.metrics = SecurityMetrics()
            self.security_alerts.clear()
            print("🔄 Security metrics reset")
            
        except Exception as e:
            print(f"❌ Metrics reset failed: {e}")





