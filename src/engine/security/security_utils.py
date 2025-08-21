"""
Security Utilities
=================

Security utility functions including password management, token management,
security validation, and audit logging.
"""

import asyncio
import json
import logging
import re
import secrets
import string
import time
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class SecurityUtils:
    """Static security utility functions"""
    
    @staticmethod
    def generate_secure_password(length: int = 16) -> str:
        """Generate a secure random password"""
        if length < 8:
            raise ValueError("Password length must be at least 8 characters")
        
        # Character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Ensure at least one character from each set
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(symbols)
        ]
        
        # Fill remaining length with random characters
        all_chars = lowercase + uppercase + digits + symbols
        password.extend(secrets.choice(all_chars) for _ in range(length - 4))
        
        # Shuffle the password
        secrets.SystemRandom().shuffle(password)
        return ''.join(password)
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength and return score"""
        score = 0
        feedback = []
        
        if len(password) < 8:
            feedback.append("Password too short")
        elif len(password) >= 12:
            score += 20
            feedback.append("Good length")
        else:
            score += 10
        
        # Check character variety
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        if has_lower:
            score += 5
        if has_upper:
            score += 5
        if has_digit:
            score += 5
        if has_symbol:
            score += 10
        
        # Check for common patterns
        if password.lower() in ['password', '123456', 'qwerty']:
            score -= 20
            feedback.append("Common password detected")
        
        # Check for repeated characters
        if len(set(password)) < len(password) * 0.7:
            score -= 5
            feedback.append("Too many repeated characters")
        
        # Determine strength level
        if score >= 40:
            strength = "strong"
        elif score >= 25:
            strength = "medium"
        else:
            strength = "weak"
        
        return {
            'valid': score >= 20,
            'score': score,
            'strength': strength,
            'feedback': feedback
        }
    
    @staticmethod
    def sanitize_input(input_string: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        if not input_string:
            return input_string
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '{', '}']
        sanitized = input_string
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        # Limit length
        if len(sanitized) > 1000:
            sanitized = sanitized[:1000]
        
        return sanitized.strip()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email or '@' not in email:
            return False
        
        # Basic email validation
        parts = email.split('@')
        if len(parts) != 2:
            return False
        
        local, domain = parts
        
        if not local or not domain:
            return False
        
        if '.' not in domain:
            return False
        
        return True
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format"""
        if not username:
            return False
        
        # Username requirements
        if len(username) < 3 or len(username) > 30:
            return False
        
        # Only allow alphanumeric characters, underscores, and hyphens
        allowed_chars = string.ascii_letters + string.digits + '_-'
        if not all(c in allowed_chars for c in username):
            return False
        
        # Cannot start or end with underscore or hyphen
        if username[0] in '_-' or username[-1] in '_-':
            return False
        
        return True
    
    @staticmethod
    def is_common_password(password: str) -> bool:
        """Check if password is in common password list"""
        common_passwords = {
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey'
        }
        
        return password.lower() in common_passwords


class PasswordManager:
    """Configurable password policy manager"""
    
    def __init__(self, min_length: int = 8, require_uppercase: bool = True,
                 require_lowercase: bool = True, require_digits: bool = True,
                 require_symbols: bool = False, max_length: int = 128):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_symbols = require_symbols
        self.max_length = max_length
    
    def is_password_acceptable(self, password: str) -> bool:
        """Check if password meets policy requirements"""
        if not password:
            return False
        
        if len(password) < self.min_length or len(password) > self.max_length:
            return False
        
        if self.require_uppercase and not any(c.isupper() for c in password):
            return False
        
        if self.require_lowercase and not any(c.islower() for c in password):
            return False
        
        if self.require_digits and not any(c.isdigit() for c in password):
            return False
        
        if self.require_symbols and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False
        
        return True
    
    def generate_password(self, length: int = None) -> str:
        """Generate password meeting policy requirements"""
        if length is None:
            length = max(self.min_length, 12)
        
        if length < self.min_length:
            raise ValueError(f"Length must be at least {self.min_length}")
        
        # Generate password that meets requirements
        while True:
            password = SecurityUtils.generate_secure_password(length)
            if self.is_password_acceptable(password):
                return password


class TokenManager:
    """Secure token generation and management"""
    
    def __init__(self, default_expiry: int = 3600):
        self.default_expiry = default_expiry
        self._tokens: Dict[str, Dict[str, Any]] = {}
    
    def generate_token(self, user_id: str, token_type: str = "access",
                      expiry: int = None) -> str:
        """Generate a secure token"""
        if expiry is None:
            expiry = self.default_expiry
        
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expiry)
        
        self._tokens[token] = {
            'user_id': user_id,
            'type': token_type,
            'created_at': datetime.now(timezone.utc),
            'expires_at': expires_at,
            'is_revoked': False
        }
        
        logger.info(f"Generated {token_type} token for user {user_id}")
        return token
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate a token"""
        token_data = self._tokens.get(token)
        if not token_data:
            return None
        
        # Check if revoked
        if token_data['is_revoked']:
            return None
        
        # Check expiration
        if token_data['expires_at'] < datetime.now(timezone.utc):
            return None
        
        return token_data
    
    def revoke_token(self, token: str) -> bool:
        """Revoke a token"""
        if token in self._tokens:
            self._tokens[token]['is_revoked'] = True
            logger.info(f"Revoked token: {token}")
            return True
        return False
    
    def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens and return count"""
        current_time = datetime.now(timezone.utc)
        expired_tokens = [
            token for token, data in self._tokens.items()
            if data['expires_at'] < current_time
        ]
        
        for token in expired_tokens:
            del self._tokens[token]
        
        if expired_tokens:
            logger.info(f"Cleaned up {len(expired_tokens)} expired tokens")
        
        return len(expired_tokens)


class SecurityValidator:
    """Rule-based input validation"""
    
    def __init__(self):
        self._rules: Dict[str, Dict[str, Any]] = {}
    
    def add_validation_rule(self, field_name: str, rule: Dict[str, Any]) -> None:
        """Add a validation rule for a field"""
        self._rules[field_name] = rule
        logger.info(f"Added validation rule for field: {field_name}")
    
    def validate_field(self, field_name: str, value: Any) -> Tuple[bool, List[str]]:
        """Validate a field value against its rules"""
        if field_name not in self._rules:
            return True, []
        
        rule = self._rules[field_name]
        errors = []
        
        # Type validation
        expected_type = rule.get('type')
        if expected_type:
            if expected_type == 'string' and not isinstance(value, str):
                errors.append(f"Field must be a string")
            elif expected_type == 'email' and not SecurityUtils.validate_email(str(value)):
                errors.append(f"Invalid email format")
            elif expected_type == 'username' and not SecurityUtils.validate_username(str(value)):
                errors.append(f"Invalid username format")
        
        # Length validation
        min_length = rule.get('min_length')
        max_length = rule.get('max_length')
        
        if min_length and len(str(value)) < min_length:
            errors.append(f"Field must be at least {min_length} characters")
        
        if max_length and len(str(value)) > max_length:
            errors.append(f"Field must be no more than {max_length} characters")
        
        # Pattern validation
        pattern = rule.get('pattern')
        if pattern and not re.match(pattern, str(value)):
            errors.append(f"Field does not match required pattern")
        
        # Custom validation
        custom_validator = rule.get('custom_validator')
        if custom_validator and callable(custom_validator):
            try:
                if not custom_validator(value):
                    errors.append(f"Field failed custom validation")
            except Exception as e:
                errors.append(f"Custom validation error: {e}")
        
        return len(errors) == 0, errors
    
    def validate_data(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, List[str]]]:
        """Validate multiple fields"""
        results = {}
        all_valid = True
        
        for field_name, value in data.items():
            is_valid, errors = self.validate_field(field_name, value)
            results[field_name] = errors
            
            if not is_valid:
                all_valid = False
        
        return all_valid, results
    
    def validate_input(self, value: Any, rule_name: str) -> Dict[str, Any]:
        """Validate input against a specific rule (for backward compatibility)"""
        if rule_name not in self._rules:
            return {
                'valid': False,
                'error': f"Validation rule '{rule_name}' not found"
            }
        
        is_valid, errors = self.validate_field(rule_name, value)
        
        return {
            'valid': is_valid,
            'errors': errors
        }


@dataclass
class AuditEvent:
    """Audit event record"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    user_id: Optional[str] = None
    username: Optional[str] = None
    resource: str = ""
    action: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    success: bool = True
    error_message: Optional[str] = None


class AuditLogger:
    """Audit logging system"""
    
    def __init__(self, log_file: str = None, max_events: int = 10000):
        self.log_file = log_file
        self.max_events = max_events
        self._events: List[AuditEvent] = []
        self._stats = {
            'total_events': 0,
            'successful_events': 0,
            'failed_events': 0,
            'events_by_type': {},
            'events_by_user': {}
        }
    
    def log_event(self, event: AuditEvent) -> None:
        """Log an audit event"""
        self._events.append(event)
        self._update_stats(event)
        
        # Write to file if configured
        if self.log_file:
            self._write_to_file(event)
        
        # Maintain event limit
        if len(self._events) > self.max_events:
            self._events.pop(0)
        
        logger.info(f"Audit event logged: {event.event_type} by {event.username}")
    
    def _update_stats(self, event: AuditEvent) -> None:
        """Update audit statistics"""
        self._stats['total_events'] += 1
        
        if event.success:
            self._stats['successful_events'] += 1
        else:
            self._stats['failed_events'] += 1
        
        # Count by event type
        event_type = event.event_type
        if event_type not in self._stats['events_by_type']:
            self._stats['events_by_type'][event_type] = 0
        self._stats['events_by_type'][event_type] += 1
        
        # Count by user
        if event.username:
            if event.username not in self._stats['events_by_user']:
                self._stats['events_by_user'][event.username] = 0
            self._stats['events_by_user'][event.username] += 1
    
    def _write_to_file(self, event: AuditEvent) -> None:
        """Write audit event to file"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"{event.timestamp.isoformat()},{event.event_type},{event.username},{event.resource},{event.action},{event.success}\n")
        except Exception as e:
            logger.error(f"Failed to write audit event to file: {e}")
    
    def get_events(self, event_type: str = None, user_id: str = None,
                   start_time: datetime = None, end_time: datetime = None) -> List[AuditEvent]:
        """Get filtered audit events"""
        filtered_events = self._events
        
        if event_type:
            filtered_events = [e for e in filtered_events if e.event_type == event_type]
        
        if user_id:
            filtered_events = [e for e in filtered_events if e.user_id == user_id]
        
        if start_time:
            filtered_events = [e for e in filtered_events if e.timestamp >= start_time]
        
        if end_time:
            filtered_events = [e for e in filtered_events if e.timestamp <= end_time]
        
        return filtered_events
    
    def get_stats(self) -> Dict[str, Any]:
        """Get audit statistics"""
        return self._stats.copy()
    
    def export_events(self, format: str = "csv", file_path: str = None, 
                     user_id: str = None, event_type: str = None,
                     start_time: datetime = None, end_time: datetime = None) -> str:
        """Export audit events to file"""
        # Filter events if parameters provided
        events_to_export = self.get_events(
            event_type=event_type,
            user_id=user_id,
            start_time=start_time,
            end_time=end_time
        )
        
        if format == "csv":
            return self._export_csv(file_path, events_to_export)
        elif format == "json":
            return self._export_json(file_path, events_to_export)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_csv(self, file_path: str = None, events: List[AuditEvent] = None) -> str:
        """Export events to CSV format"""
        if not file_path:
            file_path = f"audit_export_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
        
        if events is None:
            events = self._events
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                # Write header
                f.write("Timestamp,Event Type,Username,Resource,Action,Success,Details\n")
                
                # Write events
                for event in events:
                    details = ','.join([f"{k}={v}" for k, v in event.details.items()])
                    f.write(f"{event.timestamp.isoformat()},{event.event_type},{event.username},{event.resource},{event.action},{event.success},{details}\n")
            
            logger.info(f"Audit events exported to: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to export audit events: {e}")
            raise
    
    def _export_json(self, file_path: str = None, events: List[AuditEvent] = None) -> str:
        """Export events to JSON format"""
        if not file_path:
            file_path = f"audit_export_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        
        if events is None:
            events = self._events
        
        try:
            # Convert events to serializable format
            events_data = []
            for event in events:
                event_dict = {
                    'event_id': event.event_id,
                    'event_type': event.event_type,
                    'user_id': event.user_id,
                    'username': event.username,
                    'resource': event.resource,
                    'action': event.action,
                    'details': event.details,
                    'ip_address': event.ip_address,
                    'user_agent': event.user_agent,
                    'timestamp': event.timestamp.isoformat(),
                    'success': event.success,
                    'error_message': event.error_message
                }
                events_data.append(event_dict)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(events_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Audit events exported to: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to export audit events to JSON: {e}")
            raise
    
    def log_authentication(self, user_id: str, username: str, success: bool,
                          ip_address: str = None, user_agent: str = None,
                          details: Dict[str, Any] = None) -> None:
        """Log authentication event"""
        event = AuditEvent(
            event_type="authentication",
            user_id=user_id,
            username=username,
            resource="auth",
            action="login",
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            success=success
        )
        self.log_event(event)
    
    def log_authorization(self, user_id: str, username: str, action: str,
                         resource: str, success: bool, details: Dict[str, Any] = None) -> None:
        """Log authorization event"""
        event = AuditEvent(
            event_type="authorization",
            user_id=user_id,
            username=username,
            resource=resource,
            action=action,
            details=details or {},
            success=success
        )
        self.log_event(event)
    
    def log_data_access(self, user_id: str, username: str, action: str,
                       resource: str, resource_id: str = None,
                       details: Dict[str, Any] = None) -> None:
        """Log data access event"""
        if details is None:
            details = {}
        
        if resource_id:
            details['resource_id'] = resource_id
        
        event = AuditEvent(
            event_type="data_access",
            user_id=user_id,
            username=username,
            resource=resource,
            action=action,
            details=details,
            success=True
        )
        self.log_event(event)
    
    def clear_events(self) -> None:
        """Clear all audit events"""
        self._events.clear()
        self._stats = {
            'total_events': 0,
            'successful_events': 0,
            'failed_events': 0,
            'events_by_type': {},
            'events_by_user': {}
        }
        logger.info("Cleared all audit events")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get audit statistics (alias for get_stats)"""
        return self.get_stats()
