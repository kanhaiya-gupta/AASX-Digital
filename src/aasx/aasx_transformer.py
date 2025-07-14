"""
AASX Data Transformation Module

This module handles the transformation of extracted AASX data into various formats
and structures suitable for different use cases in the QI Digital Platform.
"""

import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import logging
from datetime import datetime
import csv
import yaml
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class TransformationConfig:
    """Configuration for AASX data transformation"""
    output_format: str = "json"  # json, xml, csv, yaml, graph
    include_metadata: bool = True
    flatten_structures: bool = False
    normalize_ids: bool = True
    add_timestamps: bool = True
    enrich_with_external_data: bool = False
    quality_checks: bool = True

class AASXTransformer:
    """
    Comprehensive AASX data transformer for the QI Digital Platform.
    
    Supports multiple output formats and transformation strategies.
    """
    
    def __init__(self, config: Optional[TransformationConfig] = None):
        """
        Initialize AASX transformer.
        
        Args:
            config: Transformation configuration
        """
        self.config = config or TransformationConfig()
        self.transformed_data = {}
        self.quality_metrics = {}
    
    def transform_aasx_data(self, aasx_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform AASX data according to configuration.
        
        Args:
            aasx_data: Raw AASX data from processor
            
        Returns:
            Transformed data in specified format
        """
        logger.info("Starting AASX data transformation")
        
        try:
            # Step 1: Clean and normalize data
            cleaned_data = self._clean_and_normalize(aasx_data)
            
            # Step 2: Apply quality checks
            if self.config.quality_checks:
                self._perform_quality_checks(cleaned_data)
            
            # Step 3: Enrich data if configured
            if self.config.enrich_with_external_data:
                cleaned_data = self._enrich_data(cleaned_data)
            
            # Step 4: Transform to target format
            transformed_data = self._transform_to_format(cleaned_data)
            
            # Step 5: Add metadata if configured
            if self.config.include_metadata:
                transformed_data = self._add_metadata(transformed_data)
            
            self.transformed_data = transformed_data
            logger.info("AASX data transformation completed successfully")
            
            return transformed_data
            
        except Exception as e:
            logger.error(f"Error during AASX transformation: {e}")
            raise
    
    def _clean_and_normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize AASX data"""
        logger.info("Cleaning and normalizing AASX data")
        
        cleaned_data = {
            'assets': [],
            'submodels': [],
            'documents': [],
            'relationships': []
        }
        
        # Clean assets
        for asset in data.get('assets', []):
            cleaned_asset = self._clean_asset(asset)
            if cleaned_asset:
                cleaned_data['assets'].append(cleaned_asset)
        
        # Clean submodels
        for submodel in data.get('submodels', []):
            cleaned_submodel = self._clean_submodel(submodel)
            if cleaned_submodel:
                cleaned_data['submodels'].append(cleaned_submodel)
        
        # Clean documents
        for document in data.get('documents', []):
            cleaned_document = self._clean_document(document)
            if cleaned_document:
                cleaned_data['documents'].append(cleaned_document)
        
        # Extract relationships
        cleaned_data['relationships'] = self._extract_relationships(cleaned_data)
        
        return cleaned_data
    
    def _clean_asset(self, asset: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Clean and normalize asset data"""
        if not asset:
            return None
        
        cleaned_asset = {
            'id': self._normalize_id(asset.get('id', '')),
            'id_short': asset.get('id_short', ''),
            'description': self._clean_description(asset.get('description', '')),
            'type': asset.get('kind', 'Unknown'),
            'asset_information': asset.get('asset_information', {}),
            'submodels': asset.get('submodels', []),
            'metadata': {
                'source': asset.get('source', ''),
                'format': asset.get('format', ''),
                'cleaned_at': datetime.now().isoformat()
            }
        }
        
        # Normalize IDs if configured
        if self.config.normalize_ids:
            cleaned_asset['normalized_id'] = self._create_normalized_id(cleaned_asset['id'])
        
        return cleaned_asset
    
    def _clean_submodel(self, submodel: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Clean and normalize submodel data"""
        if not submodel:
            return None
        
        cleaned_submodel = {
            'id': self._normalize_id(submodel.get('id', '')),
            'id_short': submodel.get('id_short', ''),
            'description': self._clean_description(submodel.get('description', '')),
            'type': submodel.get('kind', 'Unknown'),
            'semantic_id': submodel.get('semantic_id', {}),
            'elements': self._clean_submodel_elements(submodel.get('submodel_elements', [])),
            'metadata': {
                'source': submodel.get('source', ''),
                'format': submodel.get('format', ''),
                'cleaned_at': datetime.now().isoformat()
            }
        }
        
        # Normalize IDs if configured
        if self.config.normalize_ids:
            cleaned_submodel['normalized_id'] = self._create_normalized_id(cleaned_submodel['id'])
        
        return cleaned_submodel
    
    def _clean_submodel_elements(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean submodel elements"""
        cleaned_elements = []
        
        for element in elements:
            if element:
                cleaned_element = {
                    'id_short': element.get('id_short', ''),
                    'type': element.get('type', 'Unknown'),
                    'value': element.get('value', ''),
                    'semantic_id': element.get('semantic_id', {}),
                    'metadata': {
                        'cleaned_at': datetime.now().isoformat()
                    }
                }
                cleaned_elements.append(cleaned_element)
        
        return cleaned_elements
    
    def _clean_document(self, document: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Clean and normalize document data"""
        if not document:
            return None
        
        cleaned_document = {
            'filename': document.get('filename', ''),
            'size': document.get('size', 0),
            'type': document.get('type', ''),
            'metadata': {
                'cleaned_at': datetime.now().isoformat()
            }
        }
        
        return cleaned_document
    
    def _extract_relationships(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract relationships between assets and submodels"""
        relationships = []
        
        # Asset-Submodel relationships
        for asset in data.get('assets', []):
            for submodel_id in asset.get('submodels', []):
                relationship = {
                    'source_id': asset.get('id'),
                    'target_id': submodel_id,
                    'type': 'asset_has_submodel',
                    'metadata': {
                        'extracted_at': datetime.now().isoformat()
                    }
                }
                relationships.append(relationship)
        
        return relationships
    
    def _normalize_id(self, id_value: str) -> str:
        """Normalize ID values"""
        if not id_value:
            return ""
        
        # Remove special characters and normalize
        normalized = str(id_value).strip()
        normalized = normalized.replace(' ', '_')
        normalized = normalized.replace('-', '_')
        
        return normalized
    
    def _create_normalized_id(self, id_value: str) -> str:
        """Create a normalized ID for the asset/submodel"""
        normalized = self._normalize_id(id_value)
        if normalized:
            return f"normalized_{normalized}"
        return f"auto_id_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _clean_description(self, description: Union[str, Dict[str, Any]]) -> str:
        """Clean and extract description text"""
        if isinstance(description, str):
            return description.strip()
        elif isinstance(description, dict):
            # Extract text from description object
            if 'text' in description:
                return str(description['text']).strip()
            elif 'langString' in description:
                lang_strings = description['langString']
                if isinstance(lang_strings, list) and lang_strings:
                    return str(lang_strings[0].get('text', '')).strip()
        return ""
    
    def _perform_quality_checks(self, data: Dict[str, Any]) -> None:
        """Perform quality checks on transformed data"""
        logger.info("Performing quality checks")
        
        self.quality_metrics = {
            'total_assets': len(data.get('assets', [])),
            'total_submodels': len(data.get('submodels', [])),
            'total_documents': len(data.get('documents', [])),
            'total_relationships': len(data.get('relationships', [])),
            'assets_with_ids': 0,
            'submodels_with_ids': 0,
            'assets_with_descriptions': 0,
            'submodels_with_descriptions': 0,
            'quality_score': 0.0
        }
        
        # Check asset quality
        for asset in data.get('assets', []):
            if asset.get('id'):
                self.quality_metrics['assets_with_ids'] += 1
            if asset.get('description'):
                self.quality_metrics['assets_with_descriptions'] += 1
        
        # Check submodel quality
        for submodel in data.get('submodels', []):
            if submodel.get('id'):
                self.quality_metrics['submodels_with_ids'] += 1
            if submodel.get('description'):
                self.quality_metrics['submodels_with_descriptions'] += 1
        
        # Calculate quality score
        total_entities = self.quality_metrics['total_assets'] + self.quality_metrics['total_submodels']
        if total_entities > 0:
            id_score = (self.quality_metrics['assets_with_ids'] + self.quality_metrics['submodels_with_ids']) / total_entities
            desc_score = (self.quality_metrics['assets_with_descriptions'] + self.quality_metrics['submodels_with_descriptions']) / total_entities
            self.quality_metrics['quality_score'] = (id_score + desc_score) / 2
        
        logger.info(f"Quality score: {self.quality_metrics['quality_score']:.2f}")
    
    def _enrich_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich data with external information"""
        logger.info("Enriching data with external information")
        
        # Add quality infrastructure specific enrichments
        for asset in data.get('assets', []):
            asset['qi_metadata'] = {
                'quality_level': self._determine_quality_level(asset),
                'compliance_status': self._check_compliance(asset),
                'enriched_at': datetime.now().isoformat()
            }
        
        for submodel in data.get('submodels', []):
            submodel['qi_metadata'] = {
                'quality_level': self._determine_quality_level(submodel),
                'compliance_status': self._check_compliance(submodel),
                'enriched_at': datetime.now().isoformat()
            }
        
        return data
    
    def _determine_quality_level(self, entity: Dict[str, Any]) -> str:
        """Determine quality level of an entity"""
        score = 0
        
        if entity.get('id'):
            score += 1
        if entity.get('description'):
            score += 1
        if entity.get('id_short'):
            score += 1
        
        if score >= 3:
            return "HIGH"
        elif score >= 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _check_compliance(self, entity: Dict[str, Any]) -> str:
        """Check compliance status"""
        if entity.get('id') and entity.get('description'):
            return "COMPLIANT"
        elif entity.get('id'):
            return "PARTIAL"
        else:
            return "NON_COMPLIANT"
    
    def _transform_to_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data to target format"""
        format_methods = {
            'json': self._to_json_format,
            'xml': self._to_xml_format,
            'csv': self._to_csv_format,
            'yaml': self._to_yaml_format,
            'graph': self._to_graph_format,
            'flattened': self._to_flattened_format
        }
        
        method = format_methods.get(self.config.output_format.lower(), self._to_json_format)
        return method(data)
    
    def _to_json_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform to JSON format"""
        return {
            'format': 'json',
            'version': '1.0',
            'data': data,
            'quality_metrics': self.quality_metrics
        }
    
    def _to_xml_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform to XML format"""
        # Create XML structure
        root = ET.Element('aasx_data')
        root.set('version', '1.0')
        root.set('format', 'xml')
        
        # Add assets
        assets_elem = ET.SubElement(root, 'assets')
        for asset in data.get('assets', []):
            asset_elem = ET.SubElement(assets_elem, 'asset')
            asset_elem.set('id', asset.get('id', ''))
            asset_elem.set('id_short', asset.get('id_short', ''))
            
            desc_elem = ET.SubElement(asset_elem, 'description')
            desc_elem.text = asset.get('description', '')
        
        # Add submodels
        submodels_elem = ET.SubElement(root, 'submodels')
        for submodel in data.get('submodels', []):
            submodel_elem = ET.SubElement(submodels_elem, 'submodel')
            submodel_elem.set('id', submodel.get('id', ''))
            submodel_elem.set('id_short', submodel.get('id_short', ''))
            
            desc_elem = ET.SubElement(submodel_elem, 'description')
            desc_elem.text = submodel.get('description', '')
        
        return {
            'format': 'xml',
            'version': '1.0',
            'xml_string': ET.tostring(root, encoding='unicode'),
            'quality_metrics': self.quality_metrics
        }
    
    def _to_csv_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform to CSV format"""
        csv_data = {
            'assets': [],
            'submodels': [],
            'documents': []
        }
        
        # Convert assets to CSV format
        for asset in data.get('assets', []):
            csv_data['assets'].append({
                'id': asset.get('id', ''),
                'id_short': asset.get('id_short', ''),
                'description': asset.get('description', ''),
                'type': asset.get('type', ''),
                'quality_level': asset.get('qi_metadata', {}).get('quality_level', '')
            })
        
        # Convert submodels to CSV format
        for submodel in data.get('submodels', []):
            csv_data['submodels'].append({
                'id': submodel.get('id', ''),
                'id_short': submodel.get('id_short', ''),
                'description': submodel.get('description', ''),
                'type': submodel.get('type', ''),
                'quality_level': submodel.get('qi_metadata', {}).get('quality_level', '')
            })
        
        return {
            'format': 'csv',
            'version': '1.0',
            'data': csv_data,
            'quality_metrics': self.quality_metrics
        }
    
    def _to_yaml_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform to YAML format"""
        return {
            'format': 'yaml',
            'version': '1.0',
            'data': data,
            'quality_metrics': self.quality_metrics
        }
    
    def _to_graph_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform to graph format for graph databases"""
        nodes = []
        edges = []
        
        # Add asset nodes
        for asset in data.get('assets', []):
            nodes.append({
                'id': asset.get('id', ''),
                'type': 'asset',
                'properties': {
                    'id_short': asset.get('id_short', ''),
                    'description': asset.get('description', ''),
                    'quality_level': asset.get('qi_metadata', {}).get('quality_level', '')
                }
            })
        
        # Add submodel nodes
        for submodel in data.get('submodels', []):
            nodes.append({
                'id': submodel.get('id', ''),
                'type': 'submodel',
                'properties': {
                    'id_short': submodel.get('id_short', ''),
                    'description': submodel.get('description', ''),
                    'quality_level': submodel.get('qi_metadata', {}).get('quality_level', '')
                }
            })
        
        # Add relationships as edges
        for relationship in data.get('relationships', []):
            edges.append({
                'source': relationship.get('source_id', ''),
                'target': relationship.get('target_id', ''),
                'type': relationship.get('type', ''),
                'properties': relationship.get('metadata', {})
            })
        
        return {
            'format': 'graph',
            'version': '1.0',
            'nodes': nodes,
            'edges': edges,
            'quality_metrics': self.quality_metrics
        }
    
    def _to_flattened_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform to flattened format for analytics"""
        flattened = []
        
        for asset in data.get('assets', []):
            flattened.append({
                'entity_id': asset.get('id', ''),
                'entity_type': 'asset',
                'id_short': asset.get('id_short', ''),
                'description': asset.get('description', ''),
                'type': asset.get('type', ''),
                'quality_level': asset.get('qi_metadata', {}).get('quality_level', ''),
                'compliance_status': asset.get('qi_metadata', {}).get('compliance_status', '')
            })
        
        for submodel in data.get('submodels', []):
            flattened.append({
                'entity_id': submodel.get('id', ''),
                'entity_type': 'submodel',
                'id_short': submodel.get('id_short', ''),
                'description': submodel.get('description', ''),
                'type': submodel.get('type', ''),
                'quality_level': submodel.get('qi_metadata', {}).get('quality_level', ''),
                'compliance_status': submodel.get('qi_metadata', {}).get('compliance_status', '')
            })
        
        return {
            'format': 'flattened',
            'version': '1.0',
            'data': flattened,
            'quality_metrics': self.quality_metrics
        }
    
    def _add_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add metadata to transformed data"""
        metadata = {
            'transformation_timestamp': datetime.now().isoformat(),
            'transformer_version': '1.0.0',
            'configuration': asdict(self.config),
            'quality_metrics': self.quality_metrics
        }
        
        if isinstance(data, dict):
            data['metadata'] = metadata
        
        return data
    
    def export_transformed_data(self, output_path: str, format_type: Optional[str] = None) -> str:
        """
        Export transformed data to file.
        
        Args:
            output_path: Path for output file
            format_type: Override output format
            
        Returns:
            Path to exported file
        """
        if not self.transformed_data:
            raise ValueError("No transformed data available. Call transform_aasx_data() first.")
        
        output_format = format_type or self.config.output_format
        
        if output_format.lower() == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.transformed_data, f, indent=2, ensure_ascii=False)
        
        elif output_format.lower() == 'yaml':
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.transformed_data, f, default_flow_style=False, allow_unicode=True)
        
        elif output_format.lower() == 'csv':
            # Export flattened data as CSV
            if 'data' in self.transformed_data and isinstance(self.transformed_data['data'], list):
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    if self.transformed_data['data']:
                        writer = csv.DictWriter(f, fieldnames=self.transformed_data['data'][0].keys())
                        writer.writeheader()
                        writer.writerows(self.transformed_data['data'])
        
        logger.info(f"Transformed data exported to: {output_path}")
        return output_path
    
    def get_quality_report(self) -> Dict[str, Any]:
        """Get quality report for transformed data"""
        return {
            'quality_metrics': self.quality_metrics,
            'transformation_config': asdict(self.config),
            'timestamp': datetime.now().isoformat()
        } 