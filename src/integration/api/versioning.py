"""
API Versioning Service

This module provides comprehensive API versioning capabilities for the
AAS Data Modeling Engine, including version management, backward
compatibility, and version-specific routing.

The versioning service handles:
- API version detection and routing
- Backward compatibility management
- Version deprecation and sunset policies
- Version-specific feature flags
- Migration path management
"""

import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, Union, Tuple
from dataclasses import dataclass
from enum import Enum


logger = logging.getLogger(__name__)


class VersionStatus(str, Enum):
    """Status of API versions."""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"
    BETA = "beta"
    ALPHA = "alpha"


@dataclass
class APIVersion:
    """Represents an API version with metadata."""
    
    version: str
    status: VersionStatus
    release_date: datetime
    sunset_date: Optional[datetime] = None
    deprecation_date: Optional[datetime] = None
    features: List[str] = None
    breaking_changes: List[str] = None
    migration_guide: Optional[str] = None
    documentation_url: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization setup."""
        if self.features is None:
            self.features = []
        if self.breaking_changes is None:
            self.breaking_changes = []
    
    def is_active(self) -> bool:
        """Check if the version is currently active."""
        now = datetime.utcnow()
        return (
            self.status == VersionStatus.ACTIVE and
            (self.sunset_date is None or now < self.sunset_date)
        )
    
    def is_deprecated(self) -> bool:
        """Check if the version is deprecated."""
        now = datetime.utcnow()
        return (
            self.status == VersionStatus.DEPRECATED and
            (self.sunset_date is None or now < self.sunset_date)
        )
    
    def is_sunset(self) -> bool:
        """Check if the version has been sunset."""
        now = datetime.utcnow()
        return (
            self.status == VersionStatus.SUNSET or
            (self.sunset_date is not None and now >= self.sunset_date)
        )
    
    def days_until_sunset(self) -> Optional[int]:
        """Calculate days until sunset."""
        if self.sunset_date is None:
            return None
        
        now = datetime.utcnow()
        delta = self.sunset_date - now
        return max(0, delta.days)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "version": self.version,
            "status": self.status.value,
            "release_date": self.release_date.isoformat(),
            "sunset_date": self.sunset_date.isoformat() if self.sunset_date else None,
            "deprecation_date": self.deprecation_date.isoformat() if self.deprecation_date else None,
            "features": self.features,
            "breaking_changes": self.breaking_changes,
            "migration_guide": self.migration_guide,
            "documentation_url": self.documentation_url,
            "is_active": self.is_active(),
            "is_deprecated": self.is_deprecated(),
            "is_sunset": self.is_sunset(),
            "days_until_sunset": self.days_until_sunset()
        }


class APIVersioning:
    """
    Comprehensive API versioning service.
    
    Manages API versions, provides version detection, handles
    backward compatibility, and manages version-specific features.
    """
    
    def __init__(self):
        """Initialize the API versioning service."""
        self.versions: Dict[str, APIVersion] = {}
        self.default_version = "v1"
        self.version_patterns: List[re.Pattern] = []
        self.version_handlers: Dict[str, Callable] = {}
        self.feature_flags: Dict[str, Dict[str, bool]] = {}
        
        # Initialize default version patterns
        self._setup_default_patterns()
        
        # Initialize default versions
        self._setup_default_versions()
        
        logger.info("API Versioning service initialized")
    
    def _setup_default_patterns(self) -> None:
        """Setup default version detection patterns."""
        patterns = [
            r"/api/v(\d+)/",  # /api/v1/, /api/v2/, etc.
            r"/v(\d+)/",       # /v1/, /v2/, etc.
            r"version=(\d+)"   # ?version=1, ?version=2, etc.
        ]
        
        for pattern in patterns:
            self.version_patterns.append(re.compile(pattern))
        
        logger.debug(f"Initialized {len(self.version_patterns)} version patterns")
    
    def _setup_default_versions(self) -> None:
        """Setup default API versions."""
        now = datetime.utcnow()
        
        # Version 1.0 (Current stable)
        v1 = APIVersion(
            version="v1",
            status=VersionStatus.ACTIVE,
            release_date=now - timedelta(days=30),
            features=["core_workflows", "module_management", "data_processing"],
            breaking_changes=[],
            documentation_url="/docs/api/v1"
        )
        
        # Version 2.0 (Beta)
        v2 = APIVersion(
            version="v2",
            status=VersionStatus.BETA,
            release_date=now - timedelta(days=7),
            features=["advanced_workflows", "ai_integration", "real_time_analytics"],
            breaking_changes=["workflow_schema_changes", "authentication_updates"],
            migration_guide="/docs/migration/v1-to-v2",
            documentation_url="/docs/api/v2"
        )
        
        # Version 0.9 (Alpha - deprecated)
        v09 = APIVersion(
            version="v0.9",
            status=VersionStatus.DEPRECATED,
            release_date=now - timedelta(days=90),
            deprecation_date=now - timedelta(days=30),
            sunset_date=now + timedelta(days=30),
            features=["basic_workflows"],
            breaking_changes=[],
            migration_guide="/docs/migration/v09-to-v1",
            documentation_url="/docs/api/v09"
        )
        
        self.add_version(v1)
        self.add_version(v2)
        self.add_version(v09)
        
        logger.info("Default API versions configured")
    
    def add_version(self, version: APIVersion) -> None:
        """Add a new API version."""
        self.versions[version.version] = version
        logger.info(f"API version added: {version.version} ({version.status.value})")
    
    def remove_version(self, version: str) -> bool:
        """Remove an API version."""
        if version in self.versions:
            del self.versions[version]
            logger.info(f"API version removed: {version}")
            return True
        return False
    
    def get_version(self, version: str) -> Optional[APIVersion]:
        """Get an API version by string."""
        return self.versions.get(version)
    
    def get_active_versions(self) -> List[APIVersion]:
        """Get all currently active versions."""
        return [v for v in self.versions.values() if v.is_active()]
    
    def get_deprecated_versions(self) -> List[APIVersion]:
        """Get all deprecated versions."""
        return [v for v in self.versions.values() if v.is_deprecated()]
    
    def get_sunset_versions(self) -> List[APIVersion]:
        """Get all sunset versions."""
        return [v for v in self.versions.values() if v.is_sunset()]
    
    def detect_version(self, path: str, headers: Dict[str, str], query_params: Dict[str, str]) -> Tuple[str, Dict[str, Any]]:
        """
        Detect API version from request.
        
        Returns:
            Tuple of (detected_version, detection_details)
        """
        detection_details = {
            "method": "unknown",
            "confidence": 0.0,
            "patterns_matched": []
        }
        
        # Try path-based detection first
        for pattern in self.version_patterns:
            match = pattern.search(path)
            if match:
                version = f"v{match.group(1)}"
                if version in self.versions:
                    detection_details["method"] = "path_pattern"
                    detection_details["confidence"] = 1.0
                    detection_details["patterns_matched"].append(pattern.pattern)
                    return version, detection_details
        
        # Try header-based detection
        version_header = headers.get("X-API-Version") or headers.get("Accept-Version")
        if version_header:
            # Clean up version string
            version = version_header.strip().lower()
            if not version.startswith("v"):
                version = f"v{version}"
            
            if version in self.versions:
                detection_details["method"] = "header"
                detection_details["confidence"] = 0.9
                detection_details["patterns_matched"].append(f"header:{version_header}")
                return version, detection_details
        
        # Try query parameter detection
        version_param = query_params.get("version") or query_params.get("v")
        if version_param:
            version = f"v{version_param}"
            if version in self.versions:
                detection_details["method"] = "query_param"
                detection_details["confidence"] = 0.8
                detection_details["patterns_matched"].append(f"query:{version_param}")
                return version, detection_details
        
        # Fall back to default version
        detection_details["method"] = "default"
        detection_details["confidence"] = 0.5
        detection_details["patterns_matched"].append("default_fallback")
        return self.default_version, detection_details
    
    def validate_version(self, version: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate if a version is acceptable for use.
        
        Returns:
            Tuple of (is_valid, validation_details)
        """
        if version not in self.versions:
            return False, {
                "valid": False,
                "error": "Version not found",
                "available_versions": list(self.versions.keys())
            }
        
        api_version = self.versions[version]
        now = datetime.utcnow()
        
        validation_details = {
            "valid": True,
            "version": api_version.to_dict(),
            "warnings": []
        }
        
        # Check if version is sunset
        if api_version.is_sunset():
            validation_details["valid"] = False
            validation_details["error"] = "Version has been sunset"
            return False, validation_details
        
        # Check if version is deprecated
        if api_version.is_deprecated():
            validation_details["warnings"].append("Version is deprecated")
            
            # Check if close to sunset
            days_until_sunset = api_version.days_until_sunset()
            if days_until_sunset is not None and days_until_sunset <= 30:
                validation_details["warnings"].append(f"Version will be sunset in {days_until_sunset} days")
        
        # Check if version is in beta/alpha
        if api_version.status in [VersionStatus.BETA, VersionStatus.ALPHA]:
            validation_details["warnings"].append(f"Version is in {api_version.status.value} status")
        
        return True, validation_details
    
    def get_version_info(self, version: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive information about a version."""
        if version not in self.versions:
            return None
        
        api_version = self.versions[version]
        return api_version.to_dict()
    
    def get_all_versions_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all versions."""
        return {version: api_version.to_dict() for version, api_version in self.versions.items()}
    
    def set_version_status(self, version: str, status: VersionStatus, **kwargs) -> bool:
        """Update the status of a version."""
        if version not in self.versions:
            logger.warning(f"Cannot update status of non-existent version: {version}")
            return False
        
        api_version = self.versions[version]
        api_version.status = status
        
        # Update additional fields based on status
        if status == VersionStatus.DEPRECATED:
            api_version.deprecation_date = kwargs.get("deprecation_date", datetime.utcnow())
        elif status == VersionStatus.SUNSET:
            api_version.sunset_date = kwargs.get("sunset_date", datetime.utcnow())
        
        logger.info(f"Version {version} status updated to {status.value}")
        return True
    
    def deprecate_version(self, version: str, deprecation_date: Optional[datetime] = None, sunset_date: Optional[datetime] = None) -> bool:
        """Deprecate a version with optional sunset date."""
        if not self.set_version_status(version, VersionStatus.DEPRECATED):
            return False
        
        api_version = self.versions[version]
        api_version.deprecation_date = deprecation_date or datetime.utcnow()
        
        if sunset_date:
            api_version.sunset_date = sunset_date
        
        logger.info(f"Version {version} deprecated with sunset date: {sunset_date}")
        return True
    
    def sunset_version(self, version: str, sunset_date: Optional[datetime] = None) -> bool:
        """Sunset a version."""
        if not self.set_version_status(version, VersionStatus.SUNSET):
            return False
        
        api_version = self.versions[version]
        api_version.sunset_date = sunset_date or datetime.utcnow()
        
        logger.info(f"Version {version} sunset at {api_version.sunset_date}")
        return True
    
    def add_feature_flag(self, version: str, feature: str, enabled: bool = True) -> bool:
        """Add or update a feature flag for a version."""
        if version not in self.feature_flags:
            self.feature_flags[version] = {}
        
        self.feature_flags[version][feature] = enabled
        logger.info(f"Feature flag {feature} set to {enabled} for version {version}")
        return True
    
    def get_feature_flag(self, version: str, feature: str) -> bool:
        """Get the value of a feature flag for a version."""
        return self.feature_flags.get(version, {}).get(feature, False)
    
    def get_version_features(self, version: str) -> Dict[str, bool]:
        """Get all feature flags for a version."""
        return self.feature_flags.get(version, {})
    
    def register_version_handler(self, version: str, handler: Callable) -> None:
        """Register a handler for a specific version."""
        self.version_handlers[version] = handler
        logger.info(f"Version handler registered for {version}")
    
    def get_version_handler(self, version: str) -> Optional[Callable]:
        """Get the handler for a specific version."""
        return self.version_handlers.get(version)
    
    def get_migration_path(self, from_version: str, to_version: str) -> Optional[Dict[str, Any]]:
        """Get migration information between versions."""
        if from_version not in self.versions or to_version not in self.versions:
            return None
        
        from_ver = self.versions[from_version]
        to_ver = self.versions[to_version]
        
        migration_info = {
            "from_version": from_ver.to_dict(),
            "to_version": to_ver.to_dict(),
            "breaking_changes": to_ver.breaking_changes,
            "migration_guide": to_ver.migration_guide,
            "recommended": from_ver.is_deprecated() or from_ver.is_sunset()
        }
        
        return migration_info
    
    def get_recommended_version(self, client_version: Optional[str] = None) -> str:
        """Get the recommended version for clients."""
        # If client specifies a version, try to use it or suggest migration
        if client_version and client_version in self.versions:
            api_version = self.versions[client_version]
            if api_version.is_active() and not api_version.is_deprecated():
                return client_version
        
        # Return the most recent active version
        active_versions = self.get_active_versions()
        if not active_versions:
            return self.default_version
        
        # Sort by release date and return the latest
        latest = max(active_versions, key=lambda v: v.release_date)
        return latest.version
    
    def get_version_statistics(self) -> Dict[str, Any]:
        """Get comprehensive version statistics."""
        total_versions = len(self.versions)
        active_count = len(self.get_active_versions())
        deprecated_count = len(self.get_deprecated_versions())
        sunset_count = len(self.get_sunset_versions())
        
        # Calculate average version age
        now = datetime.utcnow()
        version_ages = []
        for version in self.versions.values():
            age = (now - version.release_date).days
            version_ages.append(age)
        
        avg_age = sum(version_ages) / len(version_ages) if version_ages else 0
        
        return {
            "total_versions": total_versions,
            "active_versions": active_count,
            "deprecated_versions": deprecated_count,
            "sunset_versions": sunset_count,
            "average_version_age_days": round(avg_age, 1),
            "default_version": self.default_version,
            "version_distribution": {
                "active": active_count / total_versions * 100 if total_versions > 0 else 0,
                "deprecated": deprecated_count / total_versions * 100 if total_versions > 0 else 0,
                "sunset": sunset_count / total_versions * 100 if total_versions > 0 else 0
            }
        }
    
    def cleanup_old_versions(self, max_age_days: int = 365) -> int:
        """Remove very old sunset versions to free memory."""
        cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
        removed_count = 0
        
        versions_to_remove = [
            version for version, api_version in self.versions.items()
            if (api_version.is_sunset() and 
                api_version.sunset_date and 
                api_version.sunset_date < cutoff_date)
        ]
        
        for version in versions_to_remove:
            self.remove_version(version)
            removed_count += 1
        
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} old sunset versions")
        
        return removed_count
