"""
Rate Limiting Service
====================

Handles rate limiting for authentication and API endpoints to prevent abuse.
"""

import time
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import json
import ipaddress

logger = logging.getLogger(__name__)

class RateLimitingService:
    """Service for handling rate limiting and security features"""
    
    def __init__(self, auth_db):
        """Initialize rate limiting service with database connection"""
        self.auth_db = auth_db
        
        # In-memory storage for rate limiting (in production, use Redis)
        self.rate_limit_store = defaultdict(list)
        self.ip_blacklist = set()
        self.user_blacklist = set()
        
        # Rate limiting configuration
        self.config = {
            'login_attempts': {
                'max_attempts': 5,
                'window_minutes': 15,
                'lockout_minutes': 30
            },
            'api_requests': {
                'max_requests': 100,
                'window_minutes': 60
            },
            'password_reset': {
                'max_attempts': 3,
                'window_minutes': 60
            },
            'mfa_attempts': {
                'max_attempts': 3,
                'window_minutes': 15
            }
        }
        
        # IP-based restrictions (geographic and security)
        self.ip_restrictions = {
            'blacklisted_ips': set(),  # Manually blacklisted IPs
            'whitelisted_ips': set(),  # Trusted IPs
            'geographic_restrictions': {
                'blocked_countries': set(),  # Country codes to block
                'allowed_countries': set()   # Only allow these countries
            }
        }
        
        # Dynamic rate limiting configuration
        self.dynamic_limits = {
            'adaptive_enabled': True,
            'base_multiplier': 1.0,
            'max_multiplier': 5.0,
            'min_multiplier': 0.1
        }
    
    def check_login_rate_limit(self, username: str, ip_address: str) -> Tuple[bool, Optional[str]]:
        """
        Check if login attempt is allowed for username/IP combination
        
        Returns:
            Tuple[bool, Optional[str]]: (allowed, error_message)
        """
        try:
            # Check IP-based restrictions
            ip_check = self._check_ip_restrictions(ip_address)
            if not ip_check[0]:
                return ip_check
            
            # Check if IP is blacklisted
            if ip_address in self.ip_blacklist:
                return False, "IP address is blacklisted"
            
            # Check if user is blacklisted
            if username in self.user_blacklist:
                return False, "Account is temporarily locked"
            
            # Get current timestamp
            now = datetime.utcnow()
            window_start = now - timedelta(minutes=self.config['login_attempts']['window_minutes'])
            
            # Check recent login attempts for this username/IP combination
            key = f"login:{username}:{ip_address}"
            recent_attempts = [
                attempt for attempt in self.rate_limit_store[key]
                if attempt['timestamp'] > window_start
            ]
            
            # Count failed attempts
            failed_attempts = sum(1 for attempt in recent_attempts if not attempt.get('success', False))
            
            # Apply dynamic limits if enabled
            max_attempts = self._get_dynamic_limit('login_attempts', failed_attempts)
            
            if failed_attempts >= max_attempts:
                # Lock account temporarily
                lockout_until = now + timedelta(minutes=self.config['login_attempts']['lockout_minutes'])
                self._lock_account(username, lockout_until)
                return False, f"Too many failed login attempts. Account locked until {lockout_until.strftime('%Y-%m-%d %H:%M:%S')}"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error checking login rate limit: {e}")
            return False, "Rate limiting error"
    
    def record_login_attempt(self, username: str, ip_address: str, success: bool) -> None:
        """Record a login attempt for rate limiting"""
        try:
            key = f"login:{username}:{ip_address}"
            attempt = {
                'timestamp': datetime.utcnow(),
                'success': success,
                'ip_address': ip_address
            }
            
            self.rate_limit_store[key].append(attempt)
            
            # Clean up old attempts (keep only last 24 hours)
            cutoff = datetime.utcnow() - timedelta(hours=24)
            self.rate_limit_store[key] = [
                attempt for attempt in self.rate_limit_store[key]
                if attempt['timestamp'] > cutoff
            ]
            
            # Update dynamic limits based on success/failure
            if not success:
                self._update_dynamic_limits(username, 'login_attempts', 'failure')
            else:
                self._update_dynamic_limits(username, 'login_attempts', 'success')
                
        except Exception as e:
            logger.error(f"Error recording login attempt: {e}")
    
    def check_api_rate_limit(self, user_id: str, ip_address: str, endpoint: str) -> Tuple[bool, Optional[str]]:
        """
        Check if API request is allowed for user/IP combination
        
        Returns:
            Tuple[bool, Optional[str]]: (allowed, error_message)
        """
        try:
            # Check IP-based restrictions
            ip_check = self._check_ip_restrictions(ip_address)
            if not ip_check[0]:
                return ip_check
            
            # Check if IP is blacklisted
            if ip_address in self.ip_blacklist:
                return False, "IP address is blacklisted"
            
            # Get current timestamp
            now = datetime.utcnow()
            window_start = now - timedelta(minutes=self.config['api_requests']['window_minutes'])
            
            # Check recent API requests for this user/IP combination
            key = f"api:{user_id}:{ip_address}"
            recent_requests = [
                req for req in self.rate_limit_store[key]
                if req['timestamp'] > window_start
            ]
            
            # Apply dynamic limits if enabled
            max_requests = self._get_dynamic_limit('api_requests', len(recent_requests))
            
            if len(recent_requests) >= max_requests:
                return False, "API rate limit exceeded"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error checking API rate limit: {e}")
            return False, "Rate limiting error"
    
    def record_api_request(self, user_id: str, ip_address: str, endpoint: str) -> None:
        """Record an API request for rate limiting"""
        try:
            key = f"api:{user_id}:{ip_address}"
            request = {
                'timestamp': datetime.utcnow(),
                'endpoint': endpoint,
                'ip_address': ip_address
            }
            
            self.rate_limit_store[key].append(request)
            
            # Clean up old requests (keep only last 24 hours)
            cutoff = datetime.utcnow() - timedelta(hours=24)
            self.rate_limit_store[key] = [
                req for req in self.rate_limit_store[key]
                if req['timestamp'] > cutoff
            ]
            
            # Update dynamic limits
            self._update_dynamic_limits(user_id, 'api_requests', 'request')
            
        except Exception as e:
            logger.error(f"Error recording API request: {e}")
    
    def check_password_reset_rate_limit(self, email: str, ip_address: str) -> Tuple[bool, Optional[str]]:
        """
        Check if password reset attempt is allowed
        
        Returns:
            Tuple[bool, Optional[str]]: (allowed, error_message)
        """
        try:
            # Check IP-based restrictions
            ip_check = self._check_ip_restrictions(ip_address)
            if not ip_check[0]:
                return ip_check
            
            # Get current timestamp
            now = datetime.utcnow()
            window_start = now - timedelta(minutes=self.config['password_reset']['window_minutes'])
            
            # Check recent password reset attempts
            key = f"password_reset:{email}:{ip_address}"
            recent_attempts = [
                attempt for attempt in self.rate_limit_store[key]
                if attempt['timestamp'] > window_start
            ]
            
            if len(recent_attempts) >= self.config['password_reset']['max_attempts']:
                return False, "Too many password reset attempts. Please try again later."
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error checking password reset rate limit: {e}")
            return False, "Rate limiting error"
    
    def record_password_reset_attempt(self, email: str, ip_address: str) -> None:
        """Record a password reset attempt"""
        try:
            key = f"password_reset:{email}:{ip_address}"
            attempt = {
                'timestamp': datetime.utcnow(),
                'ip_address': ip_address
            }
            
            self.rate_limit_store[key].append(attempt)
            
            # Clean up old attempts (keep only last 24 hours)
            cutoff = datetime.utcnow() - timedelta(hours=24)
            self.rate_limit_store[key] = [
                attempt for attempt in self.rate_limit_store[key]
                if attempt['timestamp'] > cutoff
            ]
            
        except Exception as e:
            logger.error(f"Error recording password reset attempt: {e}")
    
    def check_mfa_rate_limit(self, user_id: str, ip_address: str) -> Tuple[bool, Optional[str]]:
        """
        Check if MFA attempt is allowed
        
        Returns:
            Tuple[bool, Optional[str]]: (allowed, error_message)
        """
        try:
            # Check IP-based restrictions
            ip_check = self._check_ip_restrictions(ip_address)
            if not ip_check[0]:
                return ip_check
            
            # Get current timestamp
            now = datetime.utcnow()
            window_start = now - timedelta(minutes=self.config['mfa_attempts']['window_minutes'])
            
            # Check recent MFA attempts
            key = f"mfa:{user_id}:{ip_address}"
            recent_attempts = [
                attempt for attempt in self.rate_limit_store[key]
                if attempt['timestamp'] > window_start
            ]
            
            if len(recent_attempts) >= self.config['mfa_attempts']['max_attempts']:
                return False, "Too many MFA attempts. Please try again later."
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error checking MFA rate limit: {e}")
            return False, "Rate limiting error"
    
    def record_mfa_attempt(self, user_id: str, ip_address: str, success: bool) -> None:
        """Record an MFA attempt"""
        try:
            key = f"mfa:{user_id}:{ip_address}"
            attempt = {
                'timestamp': datetime.utcnow(),
                'success': success,
                'ip_address': ip_address
            }
            
            self.rate_limit_store[key].append(attempt)
            
            # Clean up old attempts (keep only last 24 hours)
            cutoff = datetime.utcnow() - timedelta(hours=24)
            self.rate_limit_store[key] = [
                attempt for attempt in self.rate_limit_store[key]
                if attempt['timestamp'] > cutoff
            ]
            
        except Exception as e:
            logger.error(f"Error recording MFA attempt: {e}")
    
    def _check_ip_restrictions(self, ip_address: str) -> Tuple[bool, Optional[str]]:
        """Check IP-based restrictions"""
        try:
            # Check if IP is in blacklist
            if ip_address in self.ip_restrictions['blacklisted_ips']:
                return False, "IP address is blacklisted"
            
            # Check if IP is in whitelist (if whitelist is not empty)
            if self.ip_restrictions['whitelisted_ips'] and ip_address not in self.ip_restrictions['whitelisted_ips']:
                return False, "IP address not in whitelist"
            
            # TODO: Implement geographic restrictions using IP geolocation
            # For now, just return True
            return True, None
            
        except Exception as e:
            logger.error(f"Error checking IP restrictions: {e}")
            return True, None
    
    def _get_dynamic_limit(self, limit_type: str, current_count: int) -> int:
        """Get dynamic limit based on current usage and adaptive settings"""
        try:
            if not self.dynamic_limits['adaptive_enabled']:
                return self.config[limit_type]['max_attempts']
            
            # Calculate dynamic multiplier based on current usage
            base_limit = self.config[limit_type]['max_attempts']
            
            # Simple adaptive logic: reduce limits if high usage detected
            if current_count > base_limit * 0.8:  # 80% of base limit
                multiplier = max(self.dynamic_limits['min_multiplier'], 
                               self.dynamic_limits['base_multiplier'] * 0.5)
            else:
                multiplier = self.dynamic_limits['base_multiplier']
            
            dynamic_limit = int(base_limit * multiplier)
            return max(1, dynamic_limit)  # Ensure minimum of 1
            
        except Exception as e:
            logger.error(f"Error calculating dynamic limit: {e}")
            return self.config[limit_type]['max_attempts']
    
    def _update_dynamic_limits(self, user_id: str, limit_type: str, action: str) -> None:
        """Update dynamic limits based on user behavior"""
        try:
            if not self.dynamic_limits['adaptive_enabled']:
                return
            
            # Simple adaptive logic: adjust limits based on success/failure patterns
            key = f"dynamic_limits:{user_id}:{limit_type}"
            
            if action == 'failure':
                # Reduce limits for failures
                self.dynamic_limits['base_multiplier'] = max(
                    self.dynamic_limits['min_multiplier'],
                    self.dynamic_limits['base_multiplier'] * 0.9
                )
            elif action == 'success':
                # Gradually increase limits for successful patterns
                self.dynamic_limits['base_multiplier'] = min(
                    self.dynamic_limits['max_multiplier'],
                    self.dynamic_limits['base_multiplier'] * 1.1
                )
            
        except Exception as e:
            logger.error(f"Error updating dynamic limits: {e}")
    
    def add_ip_to_blacklist(self, ip_address: str, reason: str = None) -> bool:
        """Add IP to blacklist"""
        try:
            self.ip_restrictions['blacklisted_ips'].add(ip_address)
            self.ip_blacklist.add(ip_address)
            logger.info(f"IP {ip_address} added to blacklist. Reason: {reason}")
            return True
        except Exception as e:
            logger.error(f"Error adding IP to blacklist: {e}")
            return False
    
    def remove_ip_from_blacklist(self, ip_address: str) -> bool:
        """Remove IP from blacklist"""
        try:
            self.ip_restrictions['blacklisted_ips'].discard(ip_address)
            self.ip_blacklist.discard(ip_address)
            logger.info(f"IP {ip_address} removed from blacklist")
            return True
        except Exception as e:
            logger.error(f"Error removing IP from blacklist: {e}")
            return False
    
    def add_ip_to_whitelist(self, ip_address: str) -> bool:
        """Add IP to whitelist"""
        try:
            self.ip_restrictions['whitelisted_ips'].add(ip_address)
            logger.info(f"IP {ip_address} added to whitelist")
            return True
        except Exception as e:
            logger.error(f"Error adding IP to whitelist: {e}")
            return False
    
    def remove_ip_from_whitelist(self, ip_address: str) -> bool:
        """Remove IP from whitelist"""
        try:
            self.ip_restrictions['whitelisted_ips'].discard(ip_address)
            logger.info(f"IP {ip_address} removed from whitelist")
            return True
        except Exception as e:
            logger.error(f"Error removing IP from whitelist: {e}")
            return False
    
    def _lock_account(self, username: str, lockout_until: datetime) -> None:
        """Lock an account temporarily"""
        try:
            # Add to in-memory blacklist
            self.user_blacklist.add(username)
            
            # Update database
            self.auth_db.update_user_lockout(username, lockout_until)
            
            logger.info(f"Account locked for user {username} until {lockout_until}")
            
        except Exception as e:
            logger.error(f"Error locking account: {e}")
    
    def _increment_failed_login_attempts(self, username: str) -> None:
        """Increment failed login attempts for a user"""
        try:
            self.auth_db.increment_failed_login_attempts(username)
        except Exception as e:
            logger.error(f"Error incrementing failed login attempts: {e}")
    
    def is_account_locked(self, username: str) -> bool:
        """Check if account is currently locked"""
        try:
            # Check in-memory blacklist first
            if username in self.user_blacklist:
                return True
            
            # Check database
            user = self.auth_db.get_user_by_username(username)
            if user and hasattr(user, 'account_locked_until') and user.account_locked_until:
                lockout_until = datetime.fromisoformat(user.account_locked_until.replace('Z', '+00:00'))
                if datetime.utcnow() < lockout_until:
                    return True
                else:
                    # Unlock account if lockout period has expired
                    self._unlock_account(username)
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking account lock status: {e}")
            return False
    
    def _unlock_account(self, username: str) -> None:
        """Unlock an account"""
        try:
            # Remove from in-memory blacklist
            self.user_blacklist.discard(username)
            
            # Update database
            self.auth_db.unlock_account(username)
            
            logger.info(f"Account unlocked for user {username}")
            
        except Exception as e:
            logger.error(f"Error unlocking account: {e}")
    
    def get_rate_limit_status(self, username: str = None, ip_address: str = None) -> Dict[str, Any]:
        """Get current rate limit status for user/IP"""
        try:
            status = {
                'login_attempts': {},
                'api_requests': {},
                'password_reset': {},
                'mfa_attempts': {},
                'ip_restrictions': {
                    'blacklisted': ip_address in self.ip_restrictions['blacklisted_ips'] if ip_address else False,
                    'whitelisted': ip_address in self.ip_restrictions['whitelisted_ips'] if ip_address else False
                },
                'dynamic_limits': {
                    'enabled': self.dynamic_limits['adaptive_enabled'],
                    'current_multiplier': self.dynamic_limits['base_multiplier']
                }
            }
            
            if username:
                # Get login attempts for username
                key = f"login:{username}:{ip_address or '*'}"
                recent_attempts = self.rate_limit_store.get(key, [])
                failed_attempts = sum(1 for attempt in recent_attempts if not attempt.get('success', False))
                
                status['login_attempts'] = {
                    'recent_attempts': len(recent_attempts),
                    'failed_attempts': failed_attempts,
                    'max_attempts': self._get_dynamic_limit('login_attempts', failed_attempts),
                    'remaining_attempts': max(0, self._get_dynamic_limit('login_attempts', failed_attempts) - failed_attempts)
                }
            
            if ip_address:
                # Get API requests for IP
                key = f"api:*:{ip_address}"
                recent_requests = self.rate_limit_store.get(key, [])
                
                status['api_requests'] = {
                    'recent_requests': len(recent_requests),
                    'max_requests': self._get_dynamic_limit('api_requests', len(recent_requests)),
                    'remaining_requests': max(0, self._get_dynamic_limit('api_requests', len(recent_requests)) - len(recent_requests))
                }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting rate limit status: {e}")
            return {}
    
    def clear_rate_limits(self, username: str = None, ip_address: str = None) -> None:
        """Clear rate limits for user/IP"""
        try:
            if username:
                # Clear all rate limits for this user
                keys_to_remove = [key for key in self.rate_limit_store.keys() if username in key]
                for key in keys_to_remove:
                    del self.rate_limit_store[key]
                logger.info(f"Cleared rate limits for user {username}")
            
            if ip_address:
                # Clear all rate limits for this IP
                keys_to_remove = [key for key in self.rate_limit_store.keys() if ip_address in key]
                for key in keys_to_remove:
                    del self.rate_limit_store[key]
                logger.info(f"Cleared rate limits for IP {ip_address}")
            
            if not username and not ip_address:
                # Clear all rate limits
                self.rate_limit_store.clear()
                logger.info("Cleared all rate limits")
                
        except Exception as e:
            logger.error(f"Error clearing rate limits: {e}") 