"""
Validation Utilities

Provides comprehensive validation utilities for the AAS Data Modeling Engine.
Includes data validation, schema validation, and custom validation rules.
"""

import re
import json
import logging
from typing import Any, Dict, List, Optional, Union, Callable, Type, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import email_validator
import ipaddress

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Validation result structure"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)
    field_results: Dict[str, 'ValidationResult'] = field(default_factory=dict)
    
    def add_error(self, error: str):
        """Add validation error"""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add validation warning"""
        self.warnings.append(warning)
    
    def add_info(self, info: str):
        """Add validation info"""
        self.info.append(info)
    
    def merge(self, other: 'ValidationResult'):
        """Merge another validation result"""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.info.extend(other.info)
        self.field_results.update(other.field_results)
        if not other.is_valid:
            self.is_valid = False


class Validators:
    """Collection of validation utilities"""
    
    @staticmethod
    def validate_email(email: str, check_deliverability: bool = False) -> ValidationResult:
        """
        Validate email address
        
        Args:
            email: Email address to validate
            check_deliverability: Whether to check domain deliverability
            
        Returns:
            ValidationResult object
        """
        result = ValidationResult(is_valid=True)
        
        try:
            # Use email-validator library for comprehensive validation
            email_validator.validate_email(
                email,
                check_deliverability=check_deliverability
            )
        except email_validator.EmailNotValidError as e:
            result.add_error(f"Invalid email format: {e}")
        
        return result
    
    @staticmethod
    def validate_url(
        url: str,
        allowed_schemes: Optional[List[str]] = None,
        require_ssl: bool = False
    ) -> ValidationResult:
        """
        Validate URL
        
        Args:
            url: URL to validate
            allowed_schemes: List of allowed URL schemes
            require_ssl: Whether to require HTTPS
            
        Returns:
            ValidationResult object
        """
        result = ValidationResult(is_valid=True)
        
        if allowed_schemes is None:
            allowed_schemes = ['http', 'https', 'ftp', 'sftp']
        
        # Basic URL pattern
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )
        
        if not url_pattern.match(url):
            result.add_error("Invalid URL format")
            return result
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            
            # Check scheme
            if parsed.scheme not in allowed_schemes:
                result.add_error(f"URL scheme '{parsed.scheme}' not allowed. Allowed: {allowed_schemes}")
            
            # Check SSL requirement
            if require_ssl and parsed.scheme != 'https':
                result.add_error("HTTPS required for this URL")
            
            # Check if domain is valid
            if parsed.hostname:
                if not Validators._is_valid_domain(parsed.hostname):
                    result.add_warning(f"Domain '{parsed.hostname}' may not be valid")
            
        except Exception as e:
            result.add_error(f"URL parsing failed: {e}")
        
        return result
    
    @staticmethod
    def _is_valid_domain(domain: str) -> bool:
        """Check if domain is valid"""
        # Basic domain validation
        domain_pattern = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
        )
        return bool(domain_pattern.match(domain))
    
    @staticmethod
    def validate_ip_address(
        ip: str,
        ip_version: Optional[int] = None,
        allow_private: bool = True,
        allow_reserved: bool = False
    ) -> ValidationResult:
        """
        Validate IP address
        
        Args:
            ip: IP address to validate
            ip_version: IP version (4 or 6), None for auto-detect
            allow_private: Whether to allow private IP addresses
            allow_reserved: Whether to allow reserved IP addresses
            
        Returns:
            ValidationResult object
        """
        result = ValidationResult(is_valid=True)
        
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            # Check IP version
            if ip_version and ip_obj.version != ip_version:
                result.add_error(f"Expected IPv{ip_version}, got IPv{ip_obj.version}")
            
            # Check if private
            if ip_obj.is_private and not allow_private:
                result.add_error("Private IP addresses not allowed")
            
            # Check if reserved
            if ip_obj.is_reserved and not allow_reserved:
                result.add_error("Reserved IP addresses not allowed")
            
            # Check if loopback
            if ip_obj.is_loopback:
                result.add_info("Loopback IP address detected")
            
            # Check if multicast
            if ip_obj.is_multicast:
                result.add_info("Multicast IP address detected")
            
        except ValueError as e:
            result.add_error(f"Invalid IP address: {e}")
        
        return result
    
    @staticmethod
    def validate_phone_number(
        phone: str,
        country_code: Optional[str] = None,
        strict: bool = False
    ) -> ValidationResult:
        """
        Validate phone number
        
        Args:
            phone: Phone number to validate
            country_code: Country code for validation
            strict: Whether to use strict validation rules
            
        Returns:
            ValidationResult object
        """
        result = ValidationResult(is_valid=True)
        
        # Remove common separators
        cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
        
        # Basic phone number pattern (international format)
        phone_pattern = re.compile(r'^\+?[1-9]\d{1,14}$')
        
        if not phone_pattern.match(cleaned):
            result.add_error("Invalid phone number format")
            return result
        
        # Length validation
        if len(cleaned) < 7:
            result.add_error("Phone number too short")
        elif len(cleaned) > 15:
            result.add_error("Phone number too long")
        
        # Country-specific validation (basic)
        if country_code:
            result.merge(Validators._validate_country_phone(cleaned, country_code))
        
        return result
    
    @staticmethod
    def _validate_country_phone(phone: str, country_code: str) -> ValidationResult:
        """Validate phone number for specific country"""
        result = ValidationResult(is_valid=True)
        
        # Basic country-specific patterns
        country_patterns = {
            'US': r'^\+?1?\d{10}$',
            'UK': r'^\+?44\d{10}$',
            'DE': r'^\+?49\d{10,11}$',
            'FR': r'^\+?33\d{9}$',
            'IN': r'^\+?91\d{10}$',
        }
        
        if country_code.upper() in country_patterns:
            pattern = country_patterns[country_code.upper()]
            if not re.match(pattern, phone):
                result.add_warning(f"Phone number may not match {country_code} format")
        
        return result
    
    @staticmethod
    def validate_credit_card(card_number: str) -> ValidationResult:
        """
        Validate credit card number using Luhn algorithm
        
        Args:
            card_number: Credit card number to validate
            
        Returns:
            ValidationResult object
        """
        result = ValidationResult(is_valid=True)
        
        # Remove spaces and dashes
        cleaned = re.sub(r'[\s\-]', '', card_number)
        
        # Check if it's all digits
        if not cleaned.isdigit():
            result.add_error("Credit card number must contain only digits")
            return result
        
        # Check length
        if len(cleaned) < 13 or len(cleaned) > 19:
            result.add_error("Invalid credit card number length")
            return result
        
        # Luhn algorithm validation
        if not Validators._luhn_check(cleaned):
            result.add_error("Invalid credit card number (failed Luhn check)")
            return result
        
        # Identify card type
        card_type = Validators._identify_card_type(cleaned)
        if card_type:
            result.add_info(f"Card type: {card_type}")
        
        return result
    
    @staticmethod
    def _luhn_check(card_number: str) -> bool:
        """Perform Luhn algorithm check"""
        digits = [int(d) for d in card_number]
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(divmod(d * 2, 10))
        
        return checksum % 10 == 0
    
    @staticmethod
    def _identify_card_type(card_number: str) -> Optional[str]:
        """Identify credit card type"""
        # Card type patterns
        patterns = {
            'Visa': r'^4[0-9]{12}(?:[0-9]{3})?$',
            'Mastercard': r'^5[1-5][0-9]{14}$',
            'American Express': r'^3[47][0-9]{13}$',
            'Discover': r'^6(?:011|5[0-9]{2})[0-9]{12}$',
            'JCB': r'^(?:2131|1800|35\d{3})\d{11}$',
        }
        
        for card_type, pattern in patterns.items():
            if re.match(pattern, card_number):
                return card_type
        
        return None
    
    @staticmethod
    def validate_password_strength(
        password: str,
        min_length: int = 8,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digits: bool = True,
        require_special: bool = True,
        max_length: int = 128
    ) -> ValidationResult:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            min_length: Minimum password length
            require_uppercase: Whether to require uppercase letters
            require_lowercase: Whether to require lowercase letters
            require_digits: Whether to require digits
            require_special: Whether to require special characters
            max_length: Maximum password length
            
        Returns:
            ValidationResult object
        """
        result = ValidationResult(is_valid=True)
        
        # Length validation
        if len(password) < min_length:
            result.add_error(f"Password too short. Minimum length: {min_length}")
        elif len(password) > max_length:
            result.add_error(f"Password too long. Maximum length: {max_length}")
        
        # Character type validation
        if require_uppercase and not re.search(r'[A-Z]', password):
            result.add_error("Password must contain at least one uppercase letter")
        
        if require_lowercase and not re.search(r'[a-z]', password):
            result.add_error("Password must contain at least one lowercase letter")
        
        if require_digits and not re.search(r'\d', password):
            result.add_error("Password must contain at least one digit")
        
        if require_special and not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
            result.add_error("Password must contain at least one special character")
        
        # Common password check
        if Validators._is_common_password(password):
            result.add_warning("Password is commonly used and may be insecure")
        
        # Sequential character check
        if Validators._has_sequential_chars(password):
            result.add_warning("Password contains sequential characters")
        
        # Repeated character check
        if Validators._has_repeated_chars(password):
            result.add_warning("Password contains repeated characters")
        
        return result
    
    @staticmethod
    def _is_common_password(password: str) -> bool:
        """Check if password is commonly used"""
        # This is a simplified check. In production, use a comprehensive dictionary
        common_passwords = {
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey'
        }
        return password.lower() in common_passwords
    
    @staticmethod
    def _has_sequential_chars(password: str) -> bool:
        """Check for sequential characters"""
        for i in range(len(password) - 2):
            if (password[i].isdigit() and password[i+1].isdigit() and password[i+2].isdigit()):
                if (int(password[i+1]) == int(password[i]) + 1 and 
                    int(password[i+2]) == int(password[i+1]) + 1):
                    return True
        return False
    
    @staticmethod
    def _has_repeated_chars(password: str) -> bool:
        """Check for repeated characters"""
        for i in range(len(password) - 2):
            if password[i] == password[i+1] == password[i+2]:
                return True
        return False
    
    @staticmethod
    def validate_json_schema(
        data: Any,
        schema: Dict[str, Any],
        strict: bool = False
    ) -> ValidationResult:
        """
        Validate data against JSON schema
        
        Args:
            data: Data to validate
            schema: JSON schema definition
            strict: Whether to use strict validation
            
        Returns:
            ValidationResult object
        """
        result = ValidationResult(is_valid=True)
        
        try:
            # Basic schema validation
            if not isinstance(schema, dict):
                result.add_error("Schema must be a dictionary")
                return result
            
            # Validate required fields
            required_fields = schema.get('required', [])
            if isinstance(data, dict):
                for field in required_fields:
                    if field not in data:
                        result.add_error(f"Required field '{field}' is missing")
            
            # Validate field types
            properties = schema.get('properties', {})
            if isinstance(data, dict):
                for field_name, field_value in data.items():
                    if field_name in properties:
                        field_schema = properties[field_name]
                        field_result = Validators._validate_field_value(
                            field_value, field_schema, strict
                        )
                        result.field_results[field_name] = field_result
                        if not field_result.is_valid:
                            result.is_valid = False
            
            # Validate array items
            if schema.get('type') == 'array' and isinstance(data, list):
                items_schema = schema.get('items', {})
                for i, item in enumerate(data):
                    item_result = Validators._validate_field_value(
                        item, items_schema, strict
                    )
                    result.field_results[f"item_{i}"] = item_result
                    if not item_result.is_valid:
                        result.is_valid = False
            
        except Exception as e:
            result.add_error(f"Schema validation failed: {e}")
        
        return result
    
    @staticmethod
    def _validate_field_value(
        value: Any,
        schema: Dict[str, Any],
        strict: bool
    ) -> ValidationResult:
        """Validate individual field value against schema"""
        result = ValidationResult(is_valid=True)
        
        # Type validation
        expected_type = schema.get('type')
        if expected_type:
            if expected_type == 'string' and not isinstance(value, str):
                result.add_error(f"Expected string, got {type(value).__name__}")
            elif expected_type == 'number' and not isinstance(value, (int, float)):
                result.add_error(f"Expected number, got {type(value).__name__}")
            elif expected_type == 'integer' and not isinstance(value, int):
                result.add_error(f"Expected integer, got {type(value).__name__}")
            elif expected_type == 'boolean' and not isinstance(value, bool):
                result.add_error(f"Expected boolean, got {type(value).__name__}")
            elif expected_type == 'array' and not isinstance(value, list):
                result.add_error(f"Expected array, got {type(value).__name__}")
            elif expected_type == 'object' and not isinstance(value, dict):
                result.add_error(f"Expected object, got {type(value).__name__}")
        
        # String validations
        if isinstance(value, str):
            if 'minLength' in schema and len(value) < schema['minLength']:
                result.add_error(f"String too short. Minimum length: {schema['minLength']}")
            
            if 'maxLength' in schema and len(value) > schema['maxLength']:
                result.add_error(f"String too long. Maximum length: {schema['maxLength']}")
            
            if 'pattern' in schema:
                if not re.match(schema['pattern'], value):
                    result.add_error(f"String does not match pattern: {schema['pattern']}")
            
            if 'enum' in schema and value not in schema['enum']:
                result.add_error(f"Value not in allowed values: {schema['enum']}")
        
        # Number validations
        if isinstance(value, (int, float)):
            if 'minimum' in schema and value < schema['minimum']:
                result.add_error(f"Value too small. Minimum: {schema['minimum']}")
            
            if 'maximum' in schema and value > schema['maximum']:
                result.add_error(f"Value too large. Maximum: {schema['maximum']}")
            
            if 'exclusiveMinimum' in schema and value <= schema['exclusiveMinimum']:
                result.add_error(f"Value must be greater than: {schema['exclusiveMinimum']}")
            
            if 'exclusiveMaximum' in schema and value >= schema['exclusiveMaximum']:
                result.add_error(f"Value must be less than: {schema['exclusiveMaximum']}")
        
        # Array validations
        if isinstance(value, list):
            if 'minItems' in schema and len(value) < schema['minItems']:
                result.add_error(f"Array too short. Minimum items: {schema['minItems']}")
            
            if 'maxItems' in schema and len(value) > schema['maxItems']:
                result.add_error(f"Array too long. Maximum items: {schema['maxItems']}")
            
            if 'uniqueItems' in schema and schema['uniqueItems']:
                if len(value) != len(set(value)):
                    result.add_error("Array items must be unique")
        
        return result
    
    @staticmethod
    def validate_file_path(
        file_path: Union[str, Path],
        must_exist: bool = False,
        must_be_file: bool = False,
        must_be_dir: bool = False,
        allowed_extensions: Optional[List[str]] = None,
        max_size: Optional[int] = None
    ) -> ValidationResult:
        """
        Validate file path
        
        Args:
            file_path: File path to validate
            must_exist: Whether file must exist
            must_be_file: Whether path must be a file
            must_be_dir: Whether path must be a directory
            allowed_extensions: List of allowed file extensions
            max_size: Maximum file size in bytes
            
        Returns:
            ValidationResult object
        """
        result = ValidationResult(is_valid=True)
        
        path = Path(file_path)
        
        # Existence check
        if must_exist and not path.exists():
            result.add_error(f"Path does not exist: {path}")
            return result
        
        # Type checks
        if path.exists():
            if must_be_file and not path.is_file():
                result.add_error(f"Path is not a file: {path}")
            
            if must_be_dir and not path.is_dir():
                result.add_error(f"Path is not a directory: {path}")
            
            # Extension check
            if allowed_extensions and path.is_file():
                if path.suffix.lower() not in [ext.lower() for ext in allowed_extensions]:
                    result.add_error(f"File extension not allowed. Allowed: {allowed_extensions}")
            
            # Size check
            if max_size and path.is_file():
                if path.stat().st_size > max_size:
                    result.add_error(f"File too large. Maximum size: {max_size} bytes")
        
        return result
    
    @staticmethod
    def validate_regex_pattern(pattern: str) -> ValidationResult:
        """
        Validate regex pattern
        
        Args:
            pattern: Regex pattern to validate
            
        Returns:
            ValidationResult object
        """
        result = ValidationResult(is_valid=True)
        
        try:
            re.compile(pattern)
        except re.error as e:
            result.add_error(f"Invalid regex pattern: {e}")
        
        return result


# Convenience functions
def validate_email(email: str, check_deliverability: bool = False) -> ValidationResult:
    """Convenience function for email validation"""
    return Validators.validate_email(email, check_deliverability)


def validate_url(
    url: str,
    allowed_schemes: Optional[List[str]] = None,
    require_ssl: bool = False
) -> ValidationResult:
    """Convenience function for URL validation"""
    return Validators.validate_url(url, allowed_schemes, require_ssl)


def validate_ip_address(
    ip: str,
    ip_version: Optional[int] = None,
    allow_private: bool = True,
    allow_reserved: bool = False
) -> ValidationResult:
    """Convenience function for IP address validation"""
    return Validators.validate_ip_address(ip, ip_version, allow_private, allow_reserved)


def validate_phone_number(
    phone: str,
    country_code: Optional[str] = None,
    strict: bool = False
) -> ValidationResult:
    """Convenience function for phone number validation"""
    return Validators.validate_phone_number(phone, country_code, strict)


def validate_credit_card(card_number: str) -> ValidationResult:
    """Convenience function for credit card validation"""
    return Validators.validate_credit_card(card_number)


def validate_password_strength(
    password: str,
    min_length: int = 8,
    require_uppercase: bool = True,
    require_lowercase: bool = True,
    require_digits: bool = True,
    require_special: bool = True,
    max_length: int = 128
) -> ValidationResult:
    """Convenience function for password strength validation"""
    return Validators.validate_password_strength(
        password, min_length, require_uppercase, require_lowercase,
        require_digits, require_special, max_length
    )


def validate_json_schema(
    data: Any,
    schema: Dict[str, Any],
    strict: bool = False
) -> ValidationResult:
    """Convenience function for JSON schema validation"""
    return Validators.validate_json_schema(data, schema, strict)


def validate_file_path(
    file_path: Union[str, Path],
    must_exist: bool = False,
    must_be_file: bool = False,
    must_be_dir: bool = False,
    allowed_extensions: Optional[List[str]] = None,
    max_size: Optional[int] = None
) -> ValidationResult:
    """Convenience function for file path validation"""
    return Validators.validate_file_path(
        file_path, must_exist, must_be_file, must_be_dir,
        allowed_extensions, max_size
    )

