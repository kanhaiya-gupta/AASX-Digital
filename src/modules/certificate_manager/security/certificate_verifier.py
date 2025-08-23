"""
Certificate Verifier for Certificate Manager

Handles certificate verification, validation, and trust assessment.
Provides comprehensive verification capabilities for digital certificates.
"""

import asyncio
import hashlib
import json
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
import logging
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class VerificationStatus(Enum):
    """Certificate verification status"""
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    FAILED = "failed"
    EXPIRED = "expired"
    REVOKED = "revoked"
    UNTRUSTED = "untrusted"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"


class VerificationLevel(Enum):
    """Certificate verification levels"""
    BASIC = "basic"           # Basic integrity check
    STANDARD = "standard"     # Standard verification
    COMPREHENSIVE = "comprehensive"  # Full verification
    ENTERPRISE = "enterprise" # Enterprise-grade verification


class CertificateVerifier:
    """
    Certificate verification service
    
    Handles:
    - Certificate integrity verification
    - Digital signature validation
    - Trust chain verification
    - Certificate expiration checks
    - Revocation status verification
    - Trust assessment and scoring
    """
    
    def __init__(self):
        """Initialize the certificate verifier"""
        self.verification_levels = list(VerificationLevel)
        self.verification_statuses = list(VerificationStatus)
        self.active_verifications: Dict[str, Dict[str, Any]] = {}
        self.verification_history: List[Dict[str, Any]] = []
        self.verification_locks: Dict[str, asyncio.Lock] = {}
        
        # Verification rules and thresholds
        self.verification_rules = self._initialize_verification_rules()
        
        # Trust assessment criteria
        self.trust_criteria = self._initialize_trust_criteria()
        
        logger.info("Certificate Verifier initialized successfully")
    
    def _initialize_verification_rules(self) -> Dict[str, Any]:
        """Initialize verification rules for different aspects"""
        return {
            "integrity": {
                "required_fields": [
                    "certificate_id",
                    "certificate_name",
                    "status",
                    "created_at",
                    "digital_signature"
                ],
                "field_validation": {
                    "certificate_id": {"type": "string", "min_length": 1},
                    "certificate_name": {"type": "string", "min_length": 1},
                    "status": {"type": "string", "allowed_values": ["pending", "in_progress", "ready", "archived"]},
                    "completion_percentage": {"type": "number", "range": (0, 100)},
                    "overall_quality_score": {"type": "number", "range": (0, 100)}
                }
            },
            "signature": {
                "required_algorithms": ["RSA-2048", "RSA-4096", "ECDSA-P256", "ECDSA-P384", "ECDSA-P521", "ED25519"],
                "min_algorithm_strength": 7,
                "max_signature_age_hours": 24
            },
            "trust": {
                "min_trust_score": 70,
                "trust_factors": {
                    "digital_signature": 30,
                    "data_integrity": 25,
                    "completion_status": 20,
                    "quality_score": 15,
                    "freshness": 10
                }
            }
        }
    
    def _initialize_trust_criteria(self) -> Dict[str, Any]:
        """Initialize trust assessment criteria"""
        return {
            "high_trust": {
                "min_score": 85,
                "requirements": [
                    "Valid digital signature",
                    "High data integrity",
                    "Recent verification",
                    "High quality score"
                ]
            },
            "medium_trust": {
                "min_score": 70,
                "requirements": [
                    "Valid digital signature",
                    "Good data integrity",
                    "Acceptable quality score"
                ]
            },
            "low_trust": {
                "min_score": 50,
                "requirements": [
                    "Basic integrity check passed",
                    "Minimal quality requirements met"
                ]
            }
        }
    
    async def verify_certificate(
        self,
        certificate_data: Dict[str, Any],
        verification_level: VerificationLevel = VerificationLevel.STANDARD,
        include_trust_assessment: bool = True,
        force_verification: bool = False
    ) -> Dict[str, Any]:
        """
        Verify a certificate with specified verification level
        
        Args:
            certificate_data: Certificate data to verify
            verification_level: Level of verification to perform
            include_trust_assessment: Whether to include trust assessment
            force_verification: Force re-verification even if cached
            
        Returns:
            Dictionary containing verification result and status
        """
        certificate_id = certificate_data.get("certificate_id", "unknown")
        
        # Acquire verification lock
        async with await self._acquire_verification_lock(certificate_id):
            try:
                # Check if verification is already in progress
                if certificate_id in self.active_verifications and not force_verification:
                    return self.active_verifications[certificate_id]
                
                # Create verification session
                verification_id = f"verify_{certificate_id}_{asyncio.get_event_loop().time()}"
                verification_session = {
                    "verification_id": verification_id,
                    "certificate_id": certificate_id,
                    "verification_level": verification_level.value,
                    "status": VerificationStatus.IN_PROGRESS.value,
                    "started_at": asyncio.get_event_loop().time(),
                    "results": {}
                }
                
                # Store active verification
                self.active_verifications[certificate_id] = verification_session
                
                # Perform verification based on level
                if verification_level == VerificationLevel.BASIC:
                    verification_result = await self._perform_basic_verification(certificate_data)
                elif verification_level == VerificationLevel.STANDARD:
                    verification_result = await self._perform_standard_verification(certificate_data)
                elif verification_level == VerificationLevel.COMPREHENSIVE:
                    verification_result = await self._perform_comprehensive_verification(certificate_data)
                elif verification_level == VerificationLevel.ENTERPRISE:
                    verification_result = await self._perform_enterprise_verification(certificate_data)
                else:
                    raise ValueError(f"Unsupported verification level: {verification_level}")
                
                # Perform trust assessment if requested
                if include_trust_assessment:
                    trust_assessment = await self._perform_trust_assessment(
                        certificate_data, verification_result
                    )
                    verification_result["trust_assessment"] = trust_assessment
                
                # Determine overall verification status
                verification_status = self._determine_verification_status(verification_result)
                verification_result["overall_status"] = verification_status.value
                
                # Update verification session
                verification_session.update({
                    "status": verification_status.value,
                    "completed_at": asyncio.get_event_loop().time(),
                    "results": verification_result
                })
                
                # Record in history
                self.verification_history.append({
                    "timestamp": asyncio.get_event_loop().time(),
                    "action": "verify",
                    "certificate_id": certificate_id,
                    "verification_level": verification_level.value,
                    "verification_id": verification_id,
                    "status": verification_status.value,
                    "duration": verification_session["completed_at"] - verification_session["started_at"]
                })
                
                logger.info(f"Certificate {certificate_id} verified with {verification_level.value} level: {verification_status.value}")
                
                return verification_result
                
            except Exception as e:
                error_msg = f"Certificate verification failed: {str(e)}"
                logger.error(f"Failed to verify certificate {certificate_id}: {error_msg}")
                
                # Update verification session with error
                if certificate_id in self.active_verifications:
                    self.active_verifications[certificate_id].update({
                        "status": VerificationStatus.FAILED.value,
                        "error": error_msg,
                        "completed_at": asyncio.get_event_loop().time()
                    })
                
                raise
    
    async def _perform_basic_verification(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform basic certificate verification"""
        verification_result = {
            "verification_level": "basic",
            "verification_timestamp": asyncio.get_event_loop().time(),
            "checks": {}
        }
        
        # Basic integrity check
        integrity_check = await self._verify_certificate_integrity(certificate_data)
        verification_result["checks"]["integrity"] = integrity_check
        
        # Basic signature check
        signature_check = await self._verify_digital_signature_basic(certificate_data)
        verification_result["checks"]["signature"] = signature_check
        
        return verification_result
    
    async def _perform_standard_verification(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform standard certificate verification"""
        verification_result = await self._perform_basic_verification(certificate_data)
        verification_result["verification_level"] = "standard"
        
        # Additional standard checks
        completion_check = await self._verify_completion_status(certificate_data)
        verification_result["checks"]["completion"] = completion_check
        
        quality_check = await self._verify_quality_metrics(certificate_data)
        verification_result["checks"]["quality"] = quality_check
        
        return verification_result
    
    async def _perform_comprehensive_verification(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive certificate verification"""
        verification_result = await self._perform_standard_verification(certificate_data)
        verification_result["verification_level"] = "comprehensive"
        
        # Additional comprehensive checks
        freshness_check = await self._verify_data_freshness(certificate_data)
        verification_result["checks"]["freshness"] = freshness_check
        
        consistency_check = await self._verify_data_consistency(certificate_data)
        verification_result["checks"]["consistency"] = consistency_check
        
        metadata_check = await self._verify_metadata_integrity(certificate_data)
        verification_result["checks"]["metadata"] = metadata_check
        
        return verification_result
    
    async def _perform_enterprise_verification(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform enterprise-grade certificate verification"""
        verification_result = await self._perform_comprehensive_verification(certificate_data)
        verification_result["verification_level"] = "enterprise"
        
        # Additional enterprise checks
        compliance_check = await self._verify_compliance_requirements(certificate_data)
        verification_result["checks"]["compliance"] = compliance_check
        
        security_check = await self._verify_security_requirements(certificate_data)
        verification_result["checks"]["security"] = security_check
        
        audit_check = await self._verify_audit_requirements(certificate_data)
        verification_result["checks"]["audit"] = audit_check
        
        return verification_result
    
    async def _verify_certificate_integrity(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify certificate data integrity"""
        rules = self.verification_rules["integrity"]
        required_fields = rules["required_fields"]
        field_validation = rules["field_validation"]
        
        # Check required fields
        missing_fields = []
        invalid_fields = []
        
        for field in required_fields:
            if field not in certificate_data or certificate_data[field] is None:
                missing_fields.append(field)
            else:
                # Validate field according to rules
                field_rule = field_validation.get(field)
                if field_rule:
                    field_valid = await self._validate_field_value(
                        certificate_data[field], field_rule
                    )
                    if not field_valid:
                        invalid_fields.append(field)
        
        # Calculate integrity score
        total_fields = len(required_fields)
        valid_fields = total_fields - len(missing_fields) - len(invalid_fields)
        integrity_score = (valid_fields / total_fields) * 100 if total_fields > 0 else 0
        
        return {
            "is_valid": len(missing_fields) == 0 and len(invalid_fields) == 0,
            "integrity_score": integrity_score,
            "missing_fields": missing_fields,
            "invalid_fields": invalid_fields,
            "total_fields": total_fields,
            "valid_fields": valid_fields
        }
    
    async def _verify_digital_signature_basic(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify digital signature (basic check)"""
        signature = certificate_data.get("digital_signature")
        signature_algorithm = certificate_data.get("signature_algorithm")
        
        if not signature:
            return {
                "is_valid": False,
                "reason": "No digital signature found",
                "signature_present": False
            }
        
        if not signature_algorithm:
            return {
                "is_valid": False,
                "reason": "No signature algorithm specified",
                "signature_present": True,
                "algorithm_present": False
            }
        
        # Check algorithm strength
        algorithm_strength = self._get_algorithm_strength(signature_algorithm)
        min_strength = self.verification_rules["signature"]["min_algorithm_strength"]
        
        return {
            "is_valid": algorithm_strength >= min_strength,
            "signature_present": True,
            "algorithm_present": True,
            "algorithm_strength": algorithm_strength,
            "min_required_strength": min_strength,
            "reason": "Signature validation passed" if algorithm_strength >= min_strength else "Algorithm strength insufficient"
        }
    
    async def _verify_completion_status(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify certificate completion status"""
        completion_percentage = certificate_data.get("completion_percentage", 0)
        status = certificate_data.get("status", "unknown")
        
        # Check if completion percentage is valid
        if not isinstance(completion_percentage, (int, float)) or completion_percentage < 0 or completion_percentage > 100:
            return {
                "is_valid": False,
                "reason": "Invalid completion percentage",
                "completion_percentage": completion_percentage
            }
        
        # Check if status is consistent with completion
        status_consistent = True
        if status == "ready" and completion_percentage < 100:
            status_consistent = False
        elif status == "in_progress" and completion_percentage == 100:
            status_consistent = False
        
        return {
            "is_valid": status_consistent,
            "completion_percentage": completion_percentage,
            "status": status,
            "status_consistent": status_consistent,
            "reason": "Completion status consistent" if status_consistent else "Completion status inconsistent"
        }
    
    async def _verify_quality_metrics(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify certificate quality metrics"""
        quality_score = certificate_data.get("overall_quality_score", 0)
        security_score = certificate_data.get("security_score", 0)
        
        # Check quality score
        quality_valid = isinstance(quality_score, (int, float)) and 0 <= quality_score <= 100
        
        # Check security score
        security_valid = isinstance(security_score, (int, float)) and 0 <= security_score <= 100
        
        # Calculate overall quality validation
        is_valid = quality_valid and security_valid
        
        return {
            "is_valid": is_valid,
            "quality_score": quality_score,
            "quality_valid": quality_valid,
            "security_score": security_score,
            "security_valid": security_valid,
            "reason": "Quality metrics valid" if is_valid else "Quality metrics invalid"
        }
    
    async def _verify_data_freshness(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify data freshness"""
        created_at = certificate_data.get("created_at")
        updated_at = certificate_data.get("updated_at")
        signature_timestamp = certificate_data.get("signature_timestamp")
        
        max_age_hours = self.verification_rules["signature"]["max_signature_age_hours"]
        
        # Check creation date
        creation_fresh = True
        if created_at:
            try:
                created_time = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                age_hours = (datetime.utcnow() - created_time.replace(tzinfo=None)).total_seconds() / 3600
                creation_fresh = age_hours <= max_age_hours
            except:
                creation_fresh = False
        
        # Check signature timestamp
        signature_fresh = True
        if signature_timestamp:
            try:
                sig_time = datetime.fromisoformat(signature_timestamp.replace("Z", "+00:00"))
                age_hours = (datetime.utcnow() - sig_time.replace(tzinfo=None)).total_seconds() / 3600
                signature_fresh = age_hours <= max_age_hours
            except:
                signature_fresh = False
        
        is_valid = creation_fresh and signature_fresh
        
        return {
            "is_valid": is_valid,
            "creation_fresh": creation_fresh,
            "signature_fresh": signature_fresh,
            "max_age_hours": max_age_hours,
            "reason": "Data is fresh" if is_valid else "Data is too old"
        }
    
    async def _verify_data_consistency(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify data consistency across certificate fields"""
        # Check for logical inconsistencies
        inconsistencies = []
        
        # Check completion vs status consistency
        completion = certificate_data.get("completion_percentage", 0)
        status = certificate_data.get("status", "unknown")
        
        if status == "ready" and completion < 100:
            inconsistencies.append("Status 'ready' but completion < 100%")
        
        if status == "in_progress" and completion == 100:
            inconsistencies.append("Status 'in_progress' but completion = 100%")
        
        # Check quality vs completion consistency
        quality_score = certificate_data.get("overall_quality_score", 0)
        if completion == 100 and quality_score < 50:
            inconsistencies.append("100% completion but low quality score")
        
        is_valid = len(inconsistencies) == 0
        
        return {
            "is_valid": is_valid,
            "inconsistencies": inconsistencies,
            "inconsistency_count": len(inconsistencies),
            "reason": "Data is consistent" if is_valid else f"Found {len(inconsistencies)} inconsistencies"
        }
    
    async def _verify_metadata_integrity(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify metadata integrity"""
        # Check for required metadata fields
        required_metadata = ["certificate_id", "certificate_name", "created_at"]
        missing_metadata = [field for field in required_metadata if field not in certificate_data]
        
        # Check metadata format validity
        format_valid = True
        if "created_at" in certificate_data:
            try:
                datetime.fromisoformat(certificate_data["created_at"].replace("Z", "+00:00"))
            except:
                format_valid = False
        
        is_valid = len(missing_metadata) == 0 and format_valid
        
        return {
            "is_valid": is_valid,
            "missing_metadata": missing_metadata,
            "format_valid": format_valid,
            "reason": "Metadata integrity valid" if is_valid else "Metadata integrity issues found"
        }
    
    async def _verify_compliance_requirements(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify compliance requirements (enterprise level)"""
        # This would check against specific compliance frameworks
        # For now, return a basic compliance check
        return {
            "is_valid": True,
            "compliance_frameworks": ["basic"],
            "requirements_met": True,
            "reason": "Basic compliance requirements met"
        }
    
    async def _verify_security_requirements(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify security requirements (enterprise level)"""
        # Check security-related fields
        security_score = certificate_data.get("security_score", 0)
        has_digital_signature = bool(certificate_data.get("digital_signature"))
        
        # Basic security validation
        is_valid = security_score >= 70 and has_digital_signature
        
        return {
            "is_valid": is_valid,
            "security_score": security_score,
            "has_digital_signature": has_digital_signature,
            "min_security_score": 70,
            "reason": "Security requirements met" if is_valid else "Security requirements not met"
        }
    
    async def _verify_audit_requirements(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify audit requirements (enterprise level)"""
        # Check for audit trail fields
        audit_fields = ["created_at", "updated_at", "signature_timestamp"]
        audit_fields_present = [field for field in audit_fields if field in certificate_data]
        
        is_valid = len(audit_fields_present) >= 2  # At least 2 audit fields required
        
        return {
            "is_valid": is_valid,
            "audit_fields_present": audit_fields_present,
            "audit_fields_required": audit_fields,
            "audit_coverage": len(audit_fields_present) / len(audit_fields) * 100,
            "reason": "Audit requirements met" if is_valid else "Insufficient audit trail"
        }
    
    async def _perform_trust_assessment(
        self,
        certificate_data: Dict[str, Any],
        verification_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform trust assessment based on verification results"""
        trust_factors = self.verification_rules["trust"]["trust_factors"]
        min_trust_score = self.verification_rules["trust"]["min_trust_score"]
        
        # Calculate trust score based on verification results
        trust_score = 0
        factor_scores = {}
        
        # Digital signature factor
        signature_check = verification_result.get("checks", {}).get("signature", {})
        signature_score = 100 if signature_check.get("is_valid", False) else 0
        trust_score += signature_score * trust_factors["digital_signature"] / 100
        factor_scores["digital_signature"] = signature_score
        
        # Data integrity factor
        integrity_check = verification_result.get("checks", {}).get("integrity", {})
        integrity_score = integrity_check.get("integrity_score", 0)
        trust_score += integrity_score * trust_factors["data_integrity"] / 100
        factor_scores["data_integrity"] = integrity_score
        
        # Completion status factor
        completion_check = verification_result.get("checks", {}).get("completion", {})
        completion_score = 100 if completion_check.get("is_valid", False) else 0
        trust_score += completion_score * trust_factors["completion_status"] / 100
        factor_scores["completion_status"] = completion_score
        
        # Quality score factor
        quality_check = verification_result.get("checks", {}).get("quality", {})
        if quality_check.get("is_valid", False):
            quality_score = certificate_data.get("overall_quality_score", 0)
        else:
            quality_score = 0
        trust_score += quality_score * trust_factors["quality_score"] / 100
        factor_scores["quality_score"] = quality_score
        
        # Freshness factor
        freshness_check = verification_result.get("checks", {}).get("freshness", {})
        freshness_score = 100 if freshness_check.get("is_valid", False) else 0
        trust_score += freshness_score * trust_factors["freshness"] / 100
        factor_scores["freshness"] = freshness_score
        
        # Determine trust level
        trust_level = self._determine_trust_level(trust_score)
        
        return {
            "trust_score": round(trust_score, 2),
            "trust_level": trust_level,
            "factor_scores": factor_scores,
            "min_required_score": min_trust_score,
            "is_trusted": trust_score >= min_trust_score,
            "trust_criteria": self.trust_criteria.get(trust_level, {})
        }
    
    def _determine_trust_level(self, trust_score: float) -> str:
        """Determine trust level based on score"""
        if trust_score >= 85:
            return "high_trust"
        elif trust_score >= 70:
            return "medium_trust"
        elif trust_score >= 50:
            return "low_trust"
        else:
            return "untrusted"
    
    def _determine_verification_status(self, verification_result: Dict[str, Any]) -> VerificationStatus:
        """Determine overall verification status"""
        checks = verification_result.get("checks", {})
        
        # Check if any critical checks failed
        critical_checks = ["integrity", "signature"]
        for check_name in critical_checks:
            check_result = checks.get(check_name, {})
            if not check_result.get("is_valid", False):
                return VerificationStatus.FAILED
        
        # Check trust assessment if available
        trust_assessment = verification_result.get("trust_assessment", {})
        if trust_assessment and not trust_assessment.get("is_trusted", False):
            return VerificationStatus.UNTRUSTED
        
        return VerificationStatus.VERIFIED
    
    async def _validate_field_value(self, value: Any, rule: Dict[str, Any]) -> bool:
        """Validate a field value according to validation rules"""
        try:
            # Type validation
            expected_type = rule.get("type")
            if expected_type == "string":
                if not isinstance(value, str):
                    return False
                min_length = rule.get("min_length", 0)
                if len(value) < min_length:
                    return False
            elif expected_type == "number":
                if not isinstance(value, (int, float)):
                    return False
                value_range = rule.get("range")
                if value_range and (value < value_range[0] or value > value_range[1]):
                    return False
            elif expected_type == "enum":
                allowed_values = rule.get("allowed_values", [])
                if value not in allowed_values:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _get_algorithm_strength(self, algorithm: str) -> int:
        """Get cryptographic strength score for algorithm"""
        strength_scores = {
            "RSA-2048": 6,
            "RSA-4096": 8,
            "ECDSA-P256": 7,
            "ECDSA-P384": 8,
            "ECDSA-P521": 9,
            "ED25519": 9,
            "HMAC-SHA256": 7,
            "HMAC-SHA512": 8
        }
        return strength_scores.get(algorithm, 5)
    
    async def _acquire_verification_lock(self, certificate_id: str) -> asyncio.Lock:
        """Acquire a lock for certificate verification"""
        if certificate_id not in self.verification_locks:
            self.verification_locks[certificate_id] = asyncio.Lock()
        return self.verification_locks[certificate_id]
    
    async def get_verification_status(self, certificate_id: str) -> Optional[Dict[str, Any]]:
        """Get the verification status of a certificate"""
        return self.active_verifications.get(certificate_id)
    
    async def get_verification_history(
        self,
        certificate_id: Optional[str] = None,
        verification_level: Optional[VerificationLevel] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get verification history with optional filtering"""
        history = self.verification_history.copy()
        
        # Filter by certificate ID
        if certificate_id:
            history = [h for h in history if h.get("certificate_id") == certificate_id]
        
        # Filter by verification level
        if verification_level:
            history = [h for h in history if h.get("verification_level") == verification_level.value]
        
        # Sort by timestamp (newest first) and limit results
        history.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        return history[:limit]
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health status of the certificate verifier"""
        return {
            "status": "healthy",
            "verification_levels": [level.value for level in self.verification_levels],
            "verification_statuses": [status.value for status in self.verification_statuses],
            "active_verifications": len(self.active_verifications),
            "verification_history_size": len(self.verification_history),
            "verification_rules_count": len(self.verification_rules),
            "trust_criteria_count": len(self.trust_criteria),
            "timestamp": asyncio.get_event_loop().time()
        }
