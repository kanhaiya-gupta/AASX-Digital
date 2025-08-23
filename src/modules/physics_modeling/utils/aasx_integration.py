"""
AASX Integration for Physics Modeling
Handles processing, parsing, and mapping AASX files to physics modeling concepts
"""

import asyncio
import logging
import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
import zipfile
import tempfile
import shutil

logger = logging.getLogger(__name__)

@dataclass
class AASXFile:
    """AASX file data structure"""
    file_path: str
    file_name: str
    file_size: int
    creation_date: datetime
    modification_date: datetime
    aas_content: Dict[str, Any]
    submodels: List[Dict[str, Any]]
    assets: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]

@dataclass
class AASXValidationResult:
    """AASX validation results"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    validation_timestamp: datetime

@dataclass
class PhysicsModelingAASXMapping:
    """Physics modeling mapping from AASX content"""
    mapping_id: str
    created_at: datetime
    physics_constraints: Dict[str, Any]
    mesh_requirements: Dict[str, Any]
    solver_recommendations: List[str]
    validation_criteria: Dict[str, Any]

class AASXIntegration:
    """Integration with AASX files for physics modeling"""

    def __init__(self):
        self.processed_files = []
        self.validation_history = []
        self.mapping_history = []
        self.extraction_history = []
        logger.info("✅ AASX Integration initialized")

    async def process_aasx_file(self, file_path: str) -> AASXFile:
        """Process and parse an AASX file"""
        await asyncio.sleep(0)
        
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"AASX file not found: {file_path}")
            
            # Extract AASX content
            aas_content = await self._parse_aasx_content(file_path)
            
            # Create AASX file object
            aasx_file = AASXFile(
                file_path=str(file_path),
                file_name=file_path.name,
                file_size=file_path.stat().st_size,
                creation_date=datetime.fromtimestamp(file_path.stat().st_ctime),
                modification_date=datetime.fromtimestamp(file_path.stat().st_mtime),
                aas_content=aas_content,
                submodels=aas_content.get('submodels', []),
                assets=aas_content.get('assets', []),
                relationships=aas_content.get('relationships', [])
            )
            
            self.processed_files.append(str(file_path))
            logger.info(f"✅ AASX file processed: {file_path.name}")
            
            return aasx_file
            
        except Exception as e:
            logger.error(f"❌ Failed to process AASX file {file_path}: {str(e)}")
            raise

    async def _parse_aasx_content(self, file_path: Path) -> Dict[str, Any]:
        """Parse AASX file content"""
        await asyncio.sleep(0)
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # Extract main AASX content
                aas_content = {}
                
                # Parse AASX file
                if 'aasx' in zip_file.namelist():
                    with zip_file.open('aasx') as aasx_file:
                        aas_content['aasx'] = await self._xml_to_dict(aasx_file)
                
                # Extract submodels
                submodels = []
                for name in zip_file.namelist():
                    if name.endswith('.aas') and 'submodel' in name.lower():
                        with zip_file.open(name) as submodel_file:
                            submodel_content = await self._parse_submodel_file(submodel_file)
                            submodels.append(submodel_content)
                
                aas_content['submodels'] = submodels
                
                # Extract assets
                assets = []
                for name in zip_file.namelist():
                    if name.endswith('.aas') and 'asset' in name.lower():
                        with zip_file.open(name) as asset_file:
                            asset_content = await self._parse_asset_file(asset_file)
                            assets.append(asset_content)
                
                aas_content['assets'] = assets
                
                # Extract relationships
                relationships = []
                for name in zip_file.namelist():
                    if name.endswith('.aas') and 'relationship' in name.lower():
                        with zip_file.open(name) as relationship_file:
                            relationship_content = await self._parse_relationship_file(relationship_file)
                            relationships.append(relationship_content)
                
                aas_content['relationships'] = relationships
                
                return aas_content
                
        except Exception as e:
            logger.error(f"❌ Failed to parse AASX content: {str(e)}")
            raise

    async def _xml_to_dict(self, xml_file) -> Dict[str, Any]:
        """Convert XML content to dictionary"""
        await asyncio.sleep(0)
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            def element_to_dict(element):
                result = {}
                if element.attrib:
                    result['@attributes'] = dict(element.attrib)
                
                for child in element:
                    child_data = element_to_dict(child)
                    if child.tag in result:
                        if not isinstance(result[child.tag], list):
                            result[child.tag] = [result[child.tag]]
                        result[child.tag].append(child_data)
                    else:
                        result[child.tag] = child_data
                
                if element.text and element.text.strip():
                    result['#text'] = element.text.strip()
                
                return result
            
            return element_to_dict(root)
            
        except Exception as e:
            logger.error(f"❌ Failed to convert XML to dict: {str(e)}")
            return {}

    async def _parse_submodel_file(self, submodel_file) -> Dict[str, Any]:
        """Parse submodel file content"""
        await asyncio.sleep(0)
        
        try:
            content = submodel_file.read().decode('utf-8')
            return {
                'type': 'submodel',
                'content': content,
                'parsed': await self._xml_to_dict(submodel_file)
            }
        except Exception as e:
            logger.error(f"❌ Failed to parse submodel file: {str(e)}")
            return {'type': 'submodel', 'content': '', 'parsed': {}}

    async def _parse_asset_file(self, asset_file) -> Dict[str, Any]:
        """Parse asset file content"""
        await asyncio.sleep(0)
        
        try:
            content = asset_file.read().decode('utf-8')
            return {
                'type': 'asset',
                'content': content,
                'parsed': await self._xml_to_dict(asset_file)
            }
        except Exception as e:
            logger.error(f"❌ Failed to parse asset file: {str(e)}")
            return {'type': 'asset', 'content': '', 'parsed': {}}

    async def _parse_relationship_file(self, relationship_file) -> Dict[str, Any]:
        """Parse relationship file content"""
        await asyncio.sleep(0)
        
        try:
            content = relationship_file.read().decode('utf-8')
            return {
                'type': 'relationship',
                'content': content,
                'parsed': await self._xml_to_dict(relationship_file)
            }
        except Exception as e:
            logger.error(f"❌ Failed to parse relationship file: {str(e)}")
            return {'type': 'relationship', 'content': '', 'parsed': {}}

    async def validate_aasx_file(self, file_path: str) -> AASXValidationResult:
        """Validate an AASX file"""
        await asyncio.sleep(0)
        
        try:
            file_path = Path(file_path)
            errors = []
            warnings = []
            
            # Check file exists
            if not file_path.exists():
                errors.append(f"File not found: {file_path}")
                return AASXValidationResult(
                    is_valid=False,
                    errors=errors,
                    warnings=warnings,
                    validation_timestamp=datetime.now()
                )
            
            # Check file extension
            if not file_path.suffix.lower() == '.aasx':
                warnings.append(f"File extension is not .aasx: {file_path.suffix}")
            
            # Check if it's a valid ZIP file
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_file:
                    # Check for required AASX structure
                    file_list = zip_file.namelist()
                    
                    if 'aasx' not in file_list:
                        errors.append("Missing 'aasx' file in AASX package")
                    
                    if not any(name.endswith('.aas') for name in file_list):
                        warnings.append("No .aas files found in AASX package")
                    
            except zipfile.BadZipFile:
                errors.append("File is not a valid ZIP archive")
            
            # Check file size
            file_size = file_path.stat().st_size
            if file_size == 0:
                errors.append("File is empty")
            elif file_size > 100 * 1024 * 1024:  # 100MB limit
                warnings.append("File size is very large (>100MB)")
            
            is_valid = len(errors) == 0
            
            validation_result = AASXValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                validation_timestamp=datetime.now()
            )
            
            self.validation_history.append(validation_result)
            logger.info(f"✅ AASX validation completed: {file_path.name} - Valid: {is_valid}")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ AASX validation failed: {str(e)}")
            return AASXValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"],
                warnings=[],
                validation_timestamp=datetime.now()
            )

    async def _extract_physics_modeling_elements(self, aasx_file: AASXFile) -> Dict[str, Any]:
        """Extract physics modeling relevant elements from AASX"""
        await asyncio.sleep(0)
        
        physics_elements = {
            'constraints': [],
            'mesh_info': [],
            'solver_hints': [],
            'validation_rules': []
        }
        
        try:
            # Extract from submodels
            for submodel in aasx_file.submodels:
                submodel_elements = await self._extract_from_submodel(submodel)
                physics_elements['constraints'].extend(submodel_elements.get('constraints', []))
                physics_elements['mesh_info'].extend(submodel_elements.get('mesh_info', []))
                physics_elements['solver_hints'].extend(submodel_elements.get('solver_hints', []))
                physics_elements['validation_rules'].extend(submodel_elements.get('validation_rules', []))
            
            # Extract from assets
            for asset in aasx_file.assets:
                asset_elements = await self._extract_from_asset(asset)
                physics_elements['constraints'].extend(asset_elements.get('constraints', []))
                physics_elements['mesh_info'].extend(asset_elements.get('mesh_info', []))
                physics_elements['solver_hints'].extend(asset_elements.get('solver_hints', []))
                physics_elements['validation_rules'].extend(asset_elements.get('validation_rules', []))
            
            # Extract from relationships
            for relationship in aasx_file.relationships:
                relationship_elements = await self._extract_from_relationship(relationship)
                physics_elements['constraints'].extend(relationship_elements.get('constraints', []))
                physics_elements['mesh_info'].extend(relationship_elements.get('mesh_info', []))
                physics_elements['solver_hints'].extend(relationship_elements.get('solver_hints', []))
                physics_elements['validation_rules'].extend(relationship_elements.get('validation_rules', []))
            
            # Extract from main content
            main_elements = await self._extract_from_main_content(aasx_file.aas_content)
            physics_elements['constraints'].extend(main_elements.get('constraints', []))
            physics_elements['mesh_info'].extend(main_elements.get('mesh_info', []))
            physics_elements['solver_hints'].extend(main_elements.get('solver_hints', []))
            physics_elements['validation_rules'].extend(main_elements.get('validation_rules', []))
            
        except Exception as e:
            logger.error(f"❌ Failed to extract physics modeling elements: {str(e)}")
        
        return physics_elements

    async def _extract_from_submodel(self, submodel: Dict[str, Any]) -> Dict[str, Any]:
        """Extract physics elements from submodel"""
        await asyncio.sleep(0)
        
        elements = {
            'constraints': [],
            'mesh_info': [],
            'solver_hints': [],
            'validation_rules': []
        }
        
        try:
            parsed = submodel.get('parsed', {})
            
            # Search for physics-related properties
            physics_props = await self._search_recursively(parsed, [
                'constraint', 'boundary', 'material', 'mesh', 'solver', 'validation'
            ])
            
            for prop in physics_props:
                if 'constraint' in str(prop).lower():
                    elements['constraints'].append(prop)
                elif 'mesh' in str(prop).lower():
                    elements['mesh_info'].append(prop)
                elif 'solver' in str(prop).lower():
                    elements['solver_hints'].append(prop)
                elif 'validation' in str(prop).lower():
                    elements['validation_rules'].append(prop)
                    
        except Exception as e:
            logger.error(f"❌ Failed to extract from submodel: {str(e)}")
        
        return elements

    async def _extract_from_asset(self, asset: Dict[str, Any]) -> Dict[str, Any]:
        """Extract physics elements from asset"""
        await asyncio.sleep(0)
        
        elements = {
            'constraints': [],
            'mesh_info': [],
            'solver_hints': [],
            'validation_rules': []
        }
        
        try:
            parsed = asset.get('parsed', {})
            
            # Search for physics-related properties
            physics_props = await self._search_recursively(parsed, [
                'constraint', 'boundary', 'material', 'mesh', 'solver', 'validation'
            ])
            
            for prop in physics_props:
                if 'constraint' in str(prop).lower():
                    elements['constraints'].append(prop)
                elif 'mesh' in str(prop).lower():
                    elements['mesh_info'].append(prop)
                elif 'solver' in str(prop).lower():
                    elements['solver_hints'].append(prop)
                elif 'validation' in str(prop).lower():
                    elements['validation_rules'].append(prop)
                    
        except Exception as e:
            logger.error(f"❌ Failed to extract from asset: {str(e)}")
        
        return elements

    async def _extract_from_relationship(self, relationship: Dict[str, Any]) -> Dict[str, Any]:
        """Extract physics elements from relationship"""
        await asyncio.sleep(0)
        
        elements = {
            'constraints': [],
            'mesh_info': [],
            'solver_hints': [],
            'validation_rules': []
        }
        
        try:
            parsed = relationship.get('parsed', {})
            
            # Search for physics-related properties
            physics_props = await self._search_recursively(parsed, [
                'constraint', 'boundary', 'material', 'mesh', 'solver', 'validation'
            ])
            
            for prop in physics_props:
                if 'constraint' in str(prop).lower():
                    elements['constraints'].append(prop)
                elif 'mesh' in str(prop).lower():
                    elements['mesh_info'].append(prop)
                elif 'solver' in str(prop).lower():
                    elements['solver_hints'].append(prop)
                elif 'validation' in str(prop).lower():
                    elements['validation_rules'].append(prop)
                    
        except Exception as e:
            logger.error(f"❌ Failed to extract from relationship: {str(e)}")
        
        return elements

    async def _extract_from_main_content(self, main_content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract physics elements from main content"""
        await asyncio.sleep(0)
        
        elements = {
            'constraints': [],
            'mesh_info': [],
            'solver_hints': [],
            'validation_rules': []
        }
        
        try:
            # Search for physics-related properties
            physics_props = await self._search_recursively(main_content, [
                'constraint', 'boundary', 'material', 'mesh', 'solver', 'validation'
            ])
            
            for prop in physics_props:
                if 'constraint' in str(prop).lower():
                    elements['constraints'].append(prop)
                elif 'mesh' in str(prop).lower():
                    elements['mesh_info'].append(prop)
                elif 'solver' in str(prop).lower():
                    elements['solver_hints'].append(prop)
                elif 'validation' in str(prop).lower():
                    elements['validation_rules'].append(prop)
                    
        except Exception as e:
            logger.error(f"❌ Failed to extract from main content: {str(e)}")
        
        return elements

    async def _search_recursively(self, data: Any, keywords: List[str]) -> List[Any]:
        """Search recursively for keywords in data"""
        await asyncio.sleep(0)
        
        results = []
        
        try:
            if isinstance(data, dict):
                for key, value in data.items():
                    # Check if key contains any keywords
                    if any(keyword.lower() in key.lower() for keyword in keywords):
                        results.append({key: value})
                    
                    # Recursively search values
                    if isinstance(value, (dict, list)):
                        results.extend(await self._search_recursively(value, keywords))
                        
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, (dict, list)):
                        results.extend(await self._search_recursively(item, keywords))
                        
        except Exception as e:
            logger.error(f"❌ Recursive search failed: {str(e)}")
        
        return results

    async def create_physics_modeling_mapping(self, aasx_file: AASXFile) -> PhysicsModelingAASXMapping:
        """Create physics modeling mapping from AASX content"""
        await asyncio.sleep(0)
        
        try:
            # Extract physics modeling elements
            physics_elements = await self._extract_physics_modeling_elements(aasx_file)
            
            # Create mapping
            mapping = PhysicsModelingAASXMapping(
                mapping_id=f"mapping_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                created_at=datetime.now(),
                physics_constraints=await self._create_constraints_mapping(physics_elements['constraints']),
                mesh_requirements=await self._create_mesh_mapping(physics_elements['mesh_info']),
                solver_recommendations=await self._create_solver_mapping(physics_elements['solver_hints']),
                validation_criteria=await self._create_validation_mapping(physics_elements['validation_rules'])
            )
            
            self.mapping_history.append(mapping)
            logger.info(f"✅ Physics modeling mapping created: {mapping.mapping_id}")
            
            return mapping
            
        except Exception as e:
            logger.error(f"❌ Failed to create physics modeling mapping: {str(e)}")
            raise

    async def _create_constraints_mapping(self, constraints: List[Any]) -> Dict[str, Any]:
        """Create constraints mapping"""
        await asyncio.sleep(0)
        
        mapping = {
            'boundary_conditions': [],
            'material_properties': [],
            'geometric_constraints': [],
            'physical_constraints': []
        }
        
        for constraint in constraints:
            constraint_str = str(constraint).lower()
            
            if 'boundary' in constraint_str:
                mapping['boundary_conditions'].append(constraint)
            elif 'material' in constraint_str:
                mapping['material_properties'].append(constraint)
            elif 'geometric' in constraint_str or 'geometry' in constraint_str:
                mapping['geometric_constraints'].append(constraint)
            else:
                mapping['physical_constraints'].append(constraint)
        
        return mapping

    async def _create_mesh_mapping(self, mesh_info: List[Any]) -> Dict[str, Any]:
        """Create mesh mapping"""
        await asyncio.sleep(0)
        
        mapping = {
            'mesh_type': 'unstructured',  # Default
            'element_types': [],
            'resolution_hints': [],
            'quality_requirements': []
        }
        
        for info in mesh_info:
            info_str = str(info).lower()
            
            if 'structured' in info_str:
                mapping['mesh_type'] = 'structured'
            elif 'unstructured' in info_str:
                mapping['mesh_type'] = 'unstructured'
            elif 'hybrid' in info_str:
                mapping['mesh_type'] = 'hybrid'
            
            if 'element' in info_str:
                mapping['element_types'].append(info)
            elif 'resolution' in info_str or 'refinement' in info_str:
                mapping['resolution_hints'].append(info)
            elif 'quality' in info_str:
                mapping['quality_requirements'].append(info)
        
        return mapping

    async def _create_solver_mapping(self, solver_hints: List[Any]) -> Dict[str, Any]:
        """Create solver mapping"""
        await asyncio.sleep(0)
        
        mapping = {
            'recommended_solvers': [],
            'solver_parameters': [],
            'convergence_criteria': []
        }
        
        for hint in solver_hints:
            hint_str = str(hint).lower()
            
            if 'solver' in hint_str:
                mapping['recommended_solvers'].append(hint)
            elif 'parameter' in hint_str:
                mapping['solver_parameters'].append(hint)
            elif 'convergence' in hint_str:
                mapping['convergence_criteria'].append(hint)
        
        return mapping

    async def _create_validation_mapping(self, validation_rules: List[Any]) -> Dict[str, Any]:
        """Create validation mapping"""
        await asyncio.sleep(0)
        
        mapping = {
            'validation_rules': validation_rules,
            'tolerance_levels': [],
            'error_thresholds': []
        }
        
        for rule in validation_rules:
            rule_str = str(rule).lower()
            
            if 'tolerance' in rule_str:
                mapping['tolerance_levels'].append(rule)
            elif 'threshold' in rule_str or 'error' in rule_str:
                mapping['error_thresholds'].append(rule)
        
        return mapping

    async def export_mapping(self, mapping: PhysicsModelingAASXMapping, export_path: str) -> bool:
        """Export mapping to file"""
        await asyncio.sleep(0)
        
        try:
            export_data = {
                'mapping_id': mapping.mapping_id,
                'created_at': mapping.created_at.isoformat(),
                'physics_constraints': mapping.physics_constraints,
                'mesh_requirements': mapping.mesh_requirements,
                'solver_recommendations': mapping.solver_recommendations,
                'validation_criteria': mapping.validation_criteria
            }
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"✅ Mapping exported to: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to export mapping: {str(e)}")
            return False

    async def get_processed_files(self) -> List[str]:
        """Get list of processed files"""
        await asyncio.sleep(0)
        return self.processed_files

    async def get_validation_history(self) -> List[AASXValidationResult]:
        """Get validation history"""
        await asyncio.sleep(0)
        return self.validation_history

    async def get_mapping_history(self) -> List[PhysicsModelingAASXMapping]:
        """Get mapping history"""
        await asyncio.sleep(0)
        return self.mapping_history

    async def get_extraction_history(self) -> List[Dict[str, Any]]:
        """Get extraction history"""
        await asyncio.sleep(0)
        return self.extraction_history

    async def clear_history(self):
        """Clear all history"""
        await asyncio.sleep(0)
        self.processed_files.clear()
        self.validation_history.clear()
        self.mapping_history.clear()
        self.extraction_history.clear()
        logger.info("✅ History cleared")
