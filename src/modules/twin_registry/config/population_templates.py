"""
Population Templates for Twin Registry
Defines templates for different types of twin registry population scenarios
"""

import logging
import json
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class TemplateType(Enum):
    """Template types"""
    BASIC_UPLOAD = "basic_upload"
    ETL_ENHANCED = "etl_enhanced"
    AI_RAG_ENHANCED = "ai_rag_enhanced"
    MANUAL_ENTRY = "manual_entry"
    BATCH_IMPORT = "batch_import"
    API_CREATED = "api_created"


class RegistryCategory(Enum):
    """Registry categories"""
    MANUFACTURING = "manufacturing"
    ENERGY = "energy"
    TRANSPORTATION = "transportation"
    HEALTHCARE = "healthcare"
    AGRICULTURE = "agriculture"
    SMART_CITY = "smart_city"
    RESEARCH = "research"
    OTHER = "other"


@dataclass
class PopulationTemplate:
    """Population template configuration"""
    template_id: str
    template_name: str
    template_type: TemplateType
    description: str
    registry_category: RegistryCategory
    registry_type: str  # extraction, generation, hybrid
    workflow_source: str
    
    # Template fields and defaults
    required_fields: List[str] = field(default_factory=list)
    optional_fields: List[str] = field(default_factory=list)
    field_defaults: Dict[str, Any] = field(default_factory=dict)
    field_transforms: Dict[str, str] = field(default_factory=dict)
    
    # Validation and quality settings
    validation_level: str = "standard"
    quality_thresholds: Dict[str, float] = field(default_factory=dict)
    
    # Metadata and configuration
    metadata_template: Dict[str, Any] = field(default_factory=dict)
    config_template: Dict[str, Any] = field(default_factory=dict)
    tags_template: List[str] = field(default_factory=list)
    
    # Phase-specific settings
    phase1_settings: Dict[str, Any] = field(default_factory=dict)
    phase2_settings: Dict[str, Any] = field(default_factory=dict)
    
    # Template metadata
    version: str = "1.0.0"
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    is_active: bool = True


class PopulationTemplates:
    """Template manager for twin registry population"""
    
    def __init__(self, templates_path: Optional[Path] = None):
        self.templates_path = templates_path or Path("config/templates")
        self.templates_path.mkdir(parents=True, exist_ok=True)
        
        self.templates: Dict[str, PopulationTemplate] = {}
        
        # Initialize default templates
        self._init_default_templates()
        
        # Load custom templates
        self.load_custom_templates()
    
    def _init_default_templates(self) -> None:
        """Initialize default population templates"""
        
        # Basic Upload Template
        basic_upload = PopulationTemplate(
            template_id="basic_upload_default",
            template_name="Basic Upload Template",
            template_type=TemplateType.BASIC_UPLOAD,
            description="Default template for basic file upload population",
            registry_category=RegistryCategory.MANUFACTURING,
            registry_type="extraction",
            workflow_source="aasx_file",
            required_fields=[
                "twin_name", "registry_type", "workflow_source", "user_id", "org_id"
            ],
            optional_fields=[
                "description", "tags", "metadata", "config"
            ],
            field_defaults={
                "registry_status": "pending",
                "lifecycle_status": "created",
                "health_status": "unknown",
                "integration_status": "pending",
                "operational_status": "inactive",
                "availability_status": "available",
                "sync_status": "not_synced"
            },
            field_transforms={
                "twin_name": "extract_from_filename",
                "description": "generate_from_file_info",
                "tags": "extract_from_file_type"
            },
            metadata_template={
                "file_info": {},
                "upload_details": {},
                "processing_status": "pending"
            },
            config_template={
                "auto_population": True,
                "validation_level": "basic",
                "quality_checks": False
            },
            tags_template=["upload", "pending_processing"],
            phase1_settings={
                "timeout": 60,
                "retry_count": 2,
                "validation_level": "basic"
            },
            phase2_settings={
                "enabled": True,
                "timeout": 300,
                "retry_count": 3,
                "validation_level": "standard"
            }
        )
        self.templates[basic_upload.template_id] = basic_upload
        
        # ETL Enhanced Template
        etl_enhanced = PopulationTemplate(
            template_id="etl_enhanced_default",
            template_name="ETL Enhanced Template",
            template_type=TemplateType.ETL_ENHANCED,
            description="Template for ETL-enhanced registry population",
            registry_category=RegistryCategory.MANUFACTURING,
            registry_type="extraction",
            workflow_source="aasx_file",
            required_fields=[
                "twin_name", "registry_type", "workflow_source", "user_id", "org_id",
                "aasx_integration_id", "digital_twin_id"
            ],
            optional_fields=[
                "description", "tags", "metadata", "config", "relationships",
                "instances", "lifecycle_events", "sync_history"
            ],
            field_defaults={
                "registry_status": "active",
                "lifecycle_status": "running",
                "health_status": "healthy",
                "integration_status": "active",
                "operational_status": "active",
                "availability_status": "available",
                "sync_status": "synced"
            },
            field_transforms={
                "twin_name": "extract_from_aasx",
                "description": "extract_from_aasx_description",
                "tags": "extract_from_aasx_tags",
                "metadata": "extract_from_aasx_metadata",
                "relationships": "extract_from_aasx_relationships",
                "instances": "extract_from_aasx_instances"
            },
            metadata_template={
                "aasx_info": {},
                "etl_processing": {},
                "data_quality": {},
                "relationships": {},
                "instances": {}
            },
            config_template={
                "auto_population": True,
                "validation_level": "standard",
                "quality_checks": True,
                "relationship_mapping": True,
                "instance_tracking": True
            },
            tags_template=["etl_processed", "active", "integrated"],
            quality_thresholds={
                "completeness": 0.9,
                "accuracy": 0.95,
                "consistency": 0.9,
                "timeliness": 0.98
            },
            phase1_settings={
                "timeout": 120,
                "retry_count": 2,
                "validation_level": "basic"
            },
            phase2_settings={
                "enabled": True,
                "timeout": 600,
                "retry_count": 3,
                "validation_level": "strict"
            }
        )
        self.templates[etl_enhanced.template_id] = etl_enhanced
        
        # AI/RAG Enhanced Template
        ai_rag_enhanced = PopulationTemplate(
            template_id="ai_rag_enhanced_default",
            template_name="AI/RAG Enhanced Template",
            template_type=TemplateType.AI_RAG_ENHANCED,
            description="Template for AI/RAG-enhanced registry population",
            registry_category=RegistryCategory.RESEARCH,
            registry_type="hybrid",
            workflow_source="api",
            required_fields=[
                "twin_name", "registry_type", "workflow_source", "user_id", "org_id"
            ],
            optional_fields=[
                "description", "tags", "metadata", "config", "ai_insights",
                "semantic_analysis", "recommendations"
            ],
            field_defaults={
                "registry_status": "active",
                "lifecycle_status": "running",
                "health_status": "healthy",
                "integration_status": "active",
                "operational_status": "active",
                "availability_status": "available",
                "sync_status": "synced"
            },
            field_transforms={
                "twin_name": "ai_generated",
                "description": "ai_generated_description",
                "tags": "ai_generated_tags",
                "metadata": "ai_enhanced_metadata"
            },
            metadata_template={
                "ai_insights": {},
                "semantic_analysis": {},
                "recommendations": {},
                "confidence_scores": {}
            },
            config_template={
                "auto_population": True,
                "validation_level": "strict",
                "quality_checks": True,
                "ai_enhancement": True,
                "semantic_analysis": True
            },
            tags_template=["ai_enhanced", "semantic_analysis", "research"],
            quality_thresholds={
                "completeness": 0.95,
                "accuracy": 0.98,
                "consistency": 0.95,
                "timeliness": 0.99
            },
            phase1_settings={
                "timeout": 180,
                "retry_count": 3,
                "validation_level": "standard"
            },
            phase2_settings={
                "enabled": True,
                "timeout": 900,
                "retry_count": 5,
                "validation_level": "strict"
            }
        )
        self.templates[ai_rag_enhanced.template_id] = ai_rag_enhanced
        
        # Manual Entry Template
        manual_entry = PopulationTemplate(
            template_id="manual_entry_default",
            template_name="Manual Entry Template",
            template_type=TemplateType.MANUAL_ENTRY,
            description="Template for manual registry entry",
            registry_category=RegistryCategory.OTHER,
            registry_type="generation",
            workflow_source="manual",
            required_fields=[
                "twin_name", "registry_type", "workflow_source", "user_id", "org_id"
            ],
            optional_fields=[
                "description", "tags", "metadata", "config"
            ],
            field_defaults={
                "registry_status": "draft",
                "lifecycle_status": "created",
                "health_status": "unknown",
                "integration_status": "pending",
                "operational_status": "inactive",
                "availability_status": "available",
                "sync_status": "not_synced"
            },
            field_transforms={},
            metadata_template={
                "manual_entry": {},
                "user_input": {},
                "validation_status": "pending"
            },
            config_template={
                "auto_population": False,
                "validation_level": "strict",
                "quality_checks": True,
                "manual_review": True
            },
            tags_template=["manual_entry", "draft", "pending_review"],
            phase1_settings={
                "timeout": 300,
                "retry_count": 1,
                "validation_level": "strict"
            },
            phase2_settings={
                "enabled": False,
                "timeout": 0,
                "retry_count": 0,
                "validation_level": "none"
            }
        )
        self.templates[manual_entry.template_id] = manual_entry
        
        # Batch Import Template
        batch_import = PopulationTemplate(
            template_id="batch_import_default",
            template_name="Batch Import Template",
            template_type=TemplateType.BATCH_IMPORT,
            description="Template for batch registry import",
            registry_category=RegistryCategory.MANUFACTURING,
            registry_type="extraction",
            workflow_source="batch_file",
            required_fields=[
                "twin_name", "registry_type", "workflow_source", "user_id", "org_id"
            ],
            optional_fields=[
                "description", "tags", "metadata", "config", "batch_info"
            ],
            field_defaults={
                "registry_status": "pending",
                "lifecycle_status": "created",
                "health_status": "unknown",
                "integration_status": "pending",
                "operational_status": "inactive",
                "availability_status": "available",
                "sync_status": "not_synced"
            },
            field_transforms={
                "twin_name": "extract_from_batch_row",
                "description": "extract_from_batch_description",
                "tags": "extract_from_batch_tags"
            },
            metadata_template={
                "batch_info": {},
                "import_details": {},
                "processing_status": "pending"
            },
            config_template={
                "auto_population": True,
                "validation_level": "standard",
                "quality_checks": True,
                "batch_processing": True
            },
            tags_template=["batch_import", "pending_processing"],
            phase1_settings={
                "timeout": 600,
                "retry_count": 3,
                "validation_level": "standard"
            },
            phase2_settings={
                "enabled": True,
                "timeout": 1200,
                "retry_count": 5,
                "validation_level": "standard"
            }
        )
        self.templates[batch_import.template_id] = batch_import
    
    def load_custom_templates(self) -> None:
        """Load custom templates from files"""
        try:
            for template_file in self.templates_path.glob("*.json"):
                try:
                    with open(template_file, 'r') as f:
                        template_data = json.load(f)
                    
                    # Convert template data to PopulationTemplate object
                    template = self._dict_to_template(template_data)
                    self.templates[template.template_id] = template
                    
                    logger.info(f"Loaded custom template: {template.template_name}")
                    
                except Exception as e:
                    logger.warning(f"Failed to load template {template_file}: {e}")
                    
        except Exception as e:
            logger.warning(f"Failed to load custom templates: {e}")
    
    def _dict_to_template(self, template_data: Dict[str, Any]) -> PopulationTemplate:
        """Convert dictionary to PopulationTemplate object"""
        # Handle datetime fields
        created_at = None
        if template_data.get("created_at"):
            try:
                created_at = datetime.fromisoformat(template_data["created_at"])
            except:
                created_at = None
        
        last_modified = None
        if template_data.get("last_modified"):
            try:
                last_modified = datetime.fromisoformat(template_data["last_modified"])
            except:
                last_modified = None
        
        return PopulationTemplate(
            template_id=template_data["template_id"],
            template_name=template_data["template_name"],
            template_type=TemplateType(template_data["template_type"]),
            description=template_data["description"],
            registry_category=RegistryCategory(template_data["registry_category"]),
            registry_type=template_data["registry_type"],
            workflow_source=template_data["workflow_source"],
            required_fields=template_data.get("required_fields", []),
            optional_fields=template_data.get("optional_fields", []),
            field_defaults=template_data.get("field_defaults", {}),
            field_transforms=template_data.get("field_transforms", {}),
            validation_level=template_data.get("validation_level", "standard"),
            quality_thresholds=template_data.get("quality_thresholds", {}),
            metadata_template=template_data.get("metadata_template", {}),
            config_template=template_data.get("config_template", {}),
            tags_template=template_data.get("tags_template", []),
            phase1_settings=template_data.get("phase1_settings", {}),
            phase2_settings=template_data.get("phase2_settings", {}),
            version=template_data.get("version", "1.0.0"),
            created_by=template_data.get("created_by"),
            created_at=created_at,
            last_modified=last_modified,
            is_active=template_data.get("is_active", True)
        )
    
    def get_template(self, template_id: str) -> Optional[PopulationTemplate]:
        """Get a template by ID"""
        return self.templates.get(template_id)
    
    def get_templates_by_type(self, template_type: TemplateType) -> List[PopulationTemplate]:
        """Get templates by type"""
        return [
            template for template in self.templates.values()
            if template.template_type == template_type and template.is_active
        ]
    
    def get_templates_by_category(self, category: RegistryCategory) -> List[PopulationTemplate]:
        """Get templates by registry category"""
        return [
            template for template in self.templates.values()
            if template.registry_category == category and template.is_active
        ]
    
    def get_templates_by_registry_type(self, registry_type: str) -> List[PopulationTemplate]:
        """Get templates by registry type"""
        return [
            template for template in self.templates.values()
            if template.registry_type == registry_type and template.is_active
        ]
    
    def create_template(self, template: PopulationTemplate) -> bool:
        """Create a new template"""
        try:
            if template.template_id in self.templates:
                logger.warning(f"Template {template.template_id} already exists")
                return False
            
            # Set creation metadata
            template.created_at = datetime.now(timezone.utc)
            template.last_modified = datetime.now(timezone.utc)
            
            # Add to templates
            self.templates[template.template_id] = template
            
            # Save to file
            self._save_template_to_file(template)
            
            logger.info(f"Created new template: {template.template_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create template: {e}")
            return False
    
    def update_template(self, template_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing template"""
        try:
            if template_id not in self.templates:
                logger.warning(f"Template {template_id} not found")
                return False
            
            template = self.templates[template_id]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(template, key):
                    setattr(template, key, value)
            
            # Update modification timestamp
            template.last_modified = datetime.now(timezone.utc)
            
            # Save to file
            self._save_template_to_file(template)
            
            logger.info(f"Updated template: {template.template_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update template {template_id}: {e}")
            return False
    
    def delete_template(self, template_id: str) -> bool:
        """Delete a template"""
        try:
            if template_id not in self.templates:
                logger.warning(f"Template {template_id} not found")
                return False
            
            template = self.templates[template_id]
            
            # Remove from templates
            del self.templates[template_id]
            
            # Delete file
            template_file = self.templates_path / f"{template_id}.json"
            if template_file.exists():
                template_file.unlink()
            
            logger.info(f"Deleted template: {template.template_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete template {template_id}: {e}")
            return False
    
    def _save_template_to_file(self, template: PopulationTemplate) -> None:
        """Save template to file"""
        try:
            template_file = self.templates_path / f"{template.template_id}.json"
            
            # Convert template to dictionary
            template_data = {
                "template_id": template.template_id,
                "template_name": template.template_name,
                "template_type": template.template_type.value,
                "description": template.description,
                "registry_category": template.registry_category.value,
                "registry_type": template.registry_type,
                "workflow_source": template.workflow_source,
                "required_fields": template.required_fields,
                "optional_fields": template.optional_fields,
                "field_defaults": template.field_defaults,
                "field_transforms": template.field_transforms,
                "validation_level": template.validation_level,
                "quality_thresholds": template.quality_thresholds,
                "metadata_template": template.metadata_template,
                "config_template": template.config_template,
                "tags_template": template.tags_template,
                "phase1_settings": template.phase1_settings,
                "phase2_settings": template.phase2_settings,
                "version": template.version,
                "created_by": template.created_by,
                "created_at": template.created_at.isoformat() if template.created_at else None,
                "last_modified": template.last_modified.isoformat() if template.last_modified else None,
                "is_active": template.is_active
            }
            
            with open(template_file, 'w') as f:
                json.dump(template_data, f, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"Failed to save template to file: {e}")
            raise
    
    def get_template_summary(self) -> Dict[str, Any]:
        """Get a summary of all templates"""
        summary = {
            "total_templates": len(self.templates),
            "active_templates": len([t for t in self.templates.values() if t.is_active]),
            "templates_by_type": {},
            "templates_by_category": {},
            "templates_by_registry_type": {}
        }
        
        # Count by type
        for template_type in TemplateType:
            summary["templates_by_type"][template_type.value] = len(
                [t for t in self.templates.values() if t.template_type == template_type and t.is_active]
            )
        
        # Count by category
        for category in RegistryCategory:
            summary["templates_by_category"][category.value] = len(
                [t for t in self.templates.values() if t.registry_category == category and t.is_active]
            )
        
        # Count by registry type
        registry_types = set(t.registry_type for t in self.templates.values())
        for registry_type in registry_types:
            summary["templates_by_registry_type"][registry_type] = len(
                [t for t in self.templates.values() if t.registry_type == registry_type and t.is_active]
            )
        
        return summary
    
    def export_templates(self, output_path: Path, format: str = "json") -> bool:
        """Export all templates to file"""
        try:
            if format.lower() == "json":
                # Export as JSON
                export_data = []
                for template in self.templates.values():
                    template_dict = {
                        "template_id": template.template_id,
                        "template_name": template.template_name,
                        "template_type": template.template_type.value,
                        "description": template.description,
                        "registry_category": template.registry_category.value,
                        "registry_type": template.registry_type,
                        "workflow_source": template.workflow_source,
                        "required_fields": template.required_fields,
                        "optional_fields": template.optional_fields,
                        "field_defaults": template.field_defaults,
                        "field_transforms": template.field_transforms,
                        "validation_level": template.validation_level,
                        "quality_thresholds": template.quality_thresholds,
                        "metadata_template": template.metadata_template,
                        "config_template": template.config_template,
                        "tags_template": template.tags_template,
                        "phase1_settings": template.phase1_settings,
                        "phase2_settings": template.phase2_settings,
                        "version": template.version,
                        "created_by": template.created_by,
                        "created_at": template.created_at.isoformat() if template.created_at else None,
                        "last_modified": template.last_modified.isoformat() if template.last_modified else None,
                        "is_active": template.is_active
                    }
                    export_data.append(template_dict)
                
                with open(output_path, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
                
                logger.info(f"Templates exported to: {output_path}")
                return True
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to export templates: {e}")
            return False
    
    def import_templates(self, import_path: Path) -> bool:
        """Import templates from file"""
        try:
            if not import_path.exists():
                raise FileNotFoundError(f"Import file not found: {import_path}")
            
            with open(import_path, 'r') as f:
                import_data = json.load(f)
            
            imported_count = 0
            for template_data in import_data:
                try:
                    template = self._dict_to_template(template_data)
                    if template.template_id not in self.templates:
                        self.templates[template.template_id] = template
                        imported_count += 1
                        logger.info(f"Imported template: {template.template_name}")
                    else:
                        logger.warning(f"Template {template.template_id} already exists, skipping")
                except Exception as e:
                    logger.warning(f"Failed to import template: {e}")
            
            logger.info(f"Imported {imported_count} templates from: {import_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import templates: {e}")
            return False
