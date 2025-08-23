"""
AASX Validation Utilities

Utility functions for AASX validation operations.
"""

import re
import hashlib
import os
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime

from ..config.validation_rules import ValidationRule, ValidationSeverity, ValidationRulesConfig


class ValidationResult:
    """Result of a validation operation."""
    
    def __init__(self, rule_id: str, severity: ValidationSeverity, message: str, suggestion: Optional[str] = None):
        self.rule_id = rule_id
        self.severity = severity
        self.message = message
        self.suggestion = suggestion
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'rule_id': self.rule_id,
            'severity': self.severity.value,
            'message': self.message,
            'suggestion': self.suggestion,
            'timestamp': self.timestamp.isoformat()
        }
    
    def __str__(self) -> str:
        return f"[{self.severity.value.upper()}] {self.message}"


class ValidationEngine:
    """Engine for executing validation rules."""
    
    def __init__(self, rules_config: ValidationRulesConfig):
        """
        Initialize validation engine.
        
        Args:
            rules_config: Validation rules configuration
        """
        self.rules_config = rules_config
        self.results: List[ValidationResult] = []
    
    def validate_file(self, file_path: str) -> List[ValidationResult]:
        """
        Validate an AASX file.
        
        Args:
            file_path: Path to the AASX file
            
        Returns:
            List[ValidationResult]: Validation results
        """
        self.results.clear()
        
        # File-level validation
        self._validate_file_basic(file_path)
        
        # Content validation if file is valid
        if not self._has_critical_errors():
            self._validate_file_content(file_path)
        
        return self.results.copy()
    
    def _validate_file_basic(self, file_path: str) -> None:
        """Perform basic file validation."""
        try:
            # Check file existence
            if not os.path.exists(file_path):
                self._add_result(
                    "file_not_found",
                    ValidationSeverity.CRITICAL,
                    f"File not found: {file_path}"
                )
                return
            
            # Check file size
            file_size = os.path.getsize(file_path)
            max_size = self.rules_config.file_rules.max_file_size_mb * 1024 * 1024
            min_size = self.rules_config.file_rules.min_file_size_kb * 1024
            
            if file_size > max_size:
                self._add_result(
                    "file_size_limit",
                    ValidationSeverity.ERROR,
                    f"File size {file_size} bytes exceeds maximum {max_size} bytes"
                )
            
            if file_size < min_size:
                self._add_result(
                    "file_size_minimum",
                    ValidationSeverity.WARNING,
                    f"File size {file_size} bytes is below minimum {min_size} bytes"
                )
            
            # Check file extension
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in self.rules_config.file_rules.allowed_extensions:
                self._add_result(
                    "file_extension",
                    ValidationSeverity.ERROR,
                    f"File extension '{file_ext}' is not supported. Allowed: {self.rules_config.file_rules.allowed_extensions}"
                )
            
            # Check file integrity
            if self.rules_config.file_rules.validate_file_integrity:
                self._validate_file_integrity(file_path)
                
        except Exception as e:
            self._add_result(
                "file_validation_error",
                ValidationSeverity.CRITICAL,
                f"File validation error: {str(e)}"
            )
    
    def _validate_file_integrity(self, file_path: str) -> None:
        """Validate file integrity."""
        try:
            # Check if file is readable
            with open(file_path, 'rb') as f:
                # Read first few bytes to check if file is accessible
                f.read(1024)
            
            # For AASX files, check if it's a valid ZIP
            if file_path.lower().endswith('.aasx'):
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_file:
                        # Check if it contains required AASX files
                        file_list = zip_file.namelist()
                        if 'aasx/aasx-origin' not in file_list:
                            self._add_result(
                                "aasx_structure",
                                ValidationSeverity.ERROR,
                                "AASX file missing required 'aasx/aasx-origin' file"
                            )
                        
                        # Check for AAS content
                        aas_files = [f for f in file_list if f.endswith('.xml') and 'aas/' in f]
                        if not aas_files:
                            self._add_result(
                                "aasx_content",
                                ValidationSeverity.WARNING,
                                "AASX file contains no AAS XML content"
                            )
                            
                except zipfile.BadZipFile:
                    self._add_result(
                        "aasx_integrity",
                        ValidationSeverity.ERROR,
                        "AASX file is not a valid ZIP archive"
                    )
                    
        except Exception as e:
            self._add_result(
                "integrity_check_error",
                ValidationSeverity.WARNING,
                f"File integrity check error: {str(e)}"
            )
    
    def _validate_file_content(self, file_path: str) -> None:
        """Validate file content."""
        try:
            if file_path.lower().endswith('.aasx'):
                self._validate_aasx_content(file_path)
            elif file_path.lower().endswith('.xml'):
                self._validate_xml_content(file_path)
            elif file_path.lower().endswith('.aas'):
                self._validate_aas_content(file_path)
                
        except Exception as e:
            self._add_result(
                "content_validation_error",
                ValidationSeverity.WARNING,
                f"Content validation error: {str(e)}"
            )
    
    def _validate_aasx_content(self, file_path: str) -> None:
        """Validate AASX file content."""
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # Validate AASX origin file
                if 'aasx/aasx-origin' in zip_file.namelist():
                    origin_content = zip_file.read('aasx/aasx-origin').decode('utf-8')
                    self._validate_aasx_origin(origin_content)
                
                # Validate AAS XML files
                aas_files = [f for f in zip_file.namelist() if f.endswith('.xml') and 'aas/' in f]
                for aas_file in aas_files[:5]:  # Limit to first 5 files
                    try:
                        xml_content = zip_file.read(aas_file).decode('utf-8')
                        self._validate_aas_xml(xml_content)
                    except Exception as e:
                        self._add_result(
                            "aas_xml_validation",
                            ValidationSeverity.WARNING,
                            f"Failed to validate AAS XML file {aas_file}: {str(e)}"
                        )
                        
        except Exception as e:
            self._add_result(
                "aasx_content_validation",
                ValidationSeverity.ERROR,
                f"AASX content validation error: {str(e)}"
            )
    
    def _validate_aasx_origin(self, content: str) -> None:
        """Validate AASX origin file content."""
        try:
            # Basic XML validation
            ET.fromstring(content)
            
            # Check for required elements (basic check)
            if '<aasx:origin' not in content:
                self._add_result(
                    "aasx_origin_structure",
                    ValidationSeverity.WARNING,
                    "AASX origin file missing required structure"
                )
                
        except ET.ParseError as e:
            self._add_result(
                "aasx_origin_xml",
                ValidationSeverity.ERROR,
                f"AASX origin file is not valid XML: {str(e)}"
            )
    
    def _validate_aas_xml(self, content: str) -> None:
        """Validate AAS XML content."""
        try:
            # Basic XML validation
            root = ET.fromstring(content)
            
            # Check for AAS namespace
            namespaces = {'aas': 'http://www.admin-shell.io/aas/3/0'}
            
            # Check for required AAS elements
            if root.find('.//aas:assetAdministrationShell', namespaces) is None and \
               root.find('.//aas:submodel', namespaces) is None and \
               root.find('.//aas:conceptDescription', namespaces) is None:
                self._add_result(
                    "aas_content_structure",
                    ValidationSeverity.WARNING,
                    "AAS XML file does not contain expected AAS elements"
                )
                
        except ET.ParseError as e:
            self._add_result(
                "aas_xml_parse",
                ValidationSeverity.ERROR,
                f"AAS XML file is not valid XML: {str(e)}"
            )
    
    def _validate_xml_content(self, file_path: str) -> None:
        """Validate XML file content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic XML validation
            ET.fromstring(content)
            
        except ET.ParseError as e:
            self._add_result(
                "xml_parse_error",
                ValidationSeverity.ERROR,
                f"XML file is not valid: {str(e)}"
            )
        except UnicodeDecodeError as e:
            self._add_result(
                "xml_encoding_error",
                ValidationSeverity.ERROR,
                f"XML file encoding error: {str(e)}"
            )
    
    def _validate_aas_content(self, file_path: str) -> None:
        """Validate AAS file content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if it's JSON
            if content.strip().startswith('{'):
                import json
                json.loads(content)
            # Check if it's XML
            elif content.strip().startswith('<'):
                ET.fromstring(content)
            else:
                self._add_result(
                    "aas_format",
                    ValidationSeverity.WARNING,
                    "AAS file format not recognized (expected JSON or XML)"
                )
                
        except (json.JSONDecodeError, ET.ParseError) as e:
            self._add_result(
                "aas_parse_error",
                ValidationSeverity.ERROR,
                f"AAS file parse error: {str(e)}"
            )
        except Exception as e:
            self._add_result(
                "aas_validation_error",
                ValidationSeverity.ERROR,
                f"AAS file validation error: {str(e)}"
            )
    
    def _add_result(self, rule_id: str, severity: ValidationSeverity, message: str, suggestion: Optional[str] = None) -> None:
        """Add a validation result."""
        result = ValidationResult(rule_id, severity, message, suggestion)
        self.results.append(result)
        
        # Check if we should fail fast
        if self.rules_config.fail_fast and severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]:
            raise ValidationError(f"Validation failed: {message}")
        
        # Check if we've reached the maximum number of errors
        if len(self.results) >= self.rules_config.max_validation_errors:
            raise ValidationError(f"Maximum validation errors ({self.rules_config.max_validation_errors}) reached")
    
    def _has_critical_errors(self) -> bool:
        """Check if there are any critical errors."""
        return any(r.severity == ValidationSeverity.CRITICAL for r in self.results)
    
    def get_results_summary(self) -> Dict[str, Any]:
        """Get a summary of validation results."""
        if not self.results:
            return {"status": "no_validation_performed"}
        
        critical_count = sum(1 for r in self.results if r.severity == ValidationSeverity.CRITICAL)
        error_count = sum(1 for r in self.results if r.severity == ValidationSeverity.ERROR)
        warning_count = sum(1 for r in self.results if r.severity == ValidationSeverity.WARNING)
        info_count = sum(1 for r in self.results if r.severity == ValidationSeverity.INFO)
        
        if critical_count > 0 or error_count > 0:
            status = "failed"
        elif warning_count > 0:
            status = "warning"
        else:
            status = "passed"
        
        return {
            "status": status,
            "total_results": len(self.results),
            "critical": critical_count,
            "errors": error_count,
            "warnings": warning_count,
            "info": info_count,
            "passed": status == "passed"
        }


class ValidationError(Exception):
    """Exception raised during validation."""
    pass


# Utility functions
def validate_file_extension(file_path: str, allowed_extensions: List[str]) -> bool:
    """Validate file extension."""
    file_ext = Path(file_path).suffix.lower()
    return file_ext in allowed_extensions


def validate_file_size(file_path: str, max_size_mb: int, min_size_kb: int = 1) -> bool:
    """Validate file size."""
    if not os.path.exists(file_path):
        return False
    
    file_size = os.path.getsize(file_path)
    max_size = max_size_mb * 1024 * 1024
    min_size = min_size_kb * 1024
    
    return min_size <= file_size <= max_size


def calculate_file_checksum(file_path: str, algorithm: str = "sha256") -> str:
    """Calculate file checksum."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    hash_func = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


def validate_identifier_format(identifier: str, pattern: str = r"^[a-zA-Z][a-zA-Z0-9_-]*$") -> bool:
    """Validate identifier format."""
    if not identifier:
        return False
    
    return bool(re.match(pattern, identifier))


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, List[str]]:
    """Validate that required fields are present."""
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    return len(missing_fields) == 0, missing_fields


def validate_quality_score(score: float, min_score: float = 0.0, max_score: float = 1.0) -> bool:
    """Validate quality score."""
    return min_score <= score <= max_score


def validate_processing_time(processing_time: float, max_time: float) -> bool:
    """Validate processing time."""
    return 0 <= processing_time <= max_time


# Factory function for validation engine
def create_validation_engine(rules_config: Optional[ValidationRulesConfig] = None) -> ValidationEngine:
    """
    Create a validation engine instance.
    
    Args:
        rules_config: Optional validation rules configuration
        
    Returns:
        ValidationEngine: Validation engine instance
    """
    if rules_config is None:
        from ..config.validation_rules import get_default_validation_rules
        rules_config = get_default_validation_rules()
    
    return ValidationEngine(rules_config)
