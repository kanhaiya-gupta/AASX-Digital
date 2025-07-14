"""
AASX File Processing Module
Comprehensive Python module for processing AASX (Asset Administration Shell Exchange) files.
"""

import os
import zipfile
import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import logging
from datetime import datetime
import io

# Try to import AAS-specific libraries if available
try:
    import aas_core3 as aas
    AAS_CORE_AVAILABLE = True
except ImportError:
    AAS_CORE_AVAILABLE = False
    logging.warning("aas_core3 not available. Using basic AASX processing.")

try:
    from aasx_package import AASXPackage
    AASX_PACKAGE_AVAILABLE = True
except ImportError:
    AASX_PACKAGE_AVAILABLE = False
    logging.warning("aasx_package not available. Using basic ZIP processing.")

# Try to import .NET bridge
try:
    from .dotnet_bridge import DotNetAasBridge
    DOTNET_BRIDGE_AVAILABLE = True
    dotnet_bridge = DotNetAasBridge()
except ImportError:
    DOTNET_BRIDGE_AVAILABLE = False
    dotnet_bridge = None
    logging.warning("DotNet bridge not available. Using basic AASX processing.")
except Exception as e:
    DOTNET_BRIDGE_AVAILABLE = False
    dotnet_bridge = None
    logging.warning(f"DotNet bridge initialization failed: {e}")

# Configure logging
logger = logging.getLogger(__name__)

class AASXProcessor:
    """
    Comprehensive AASX file processor for the QI Digital Platform.
    
    Supports both basic ZIP-based processing and advanced AAS-specific processing
    when specialized libraries are available.
    """
    
    def __init__(self, aasx_file_path: str):
        """
        Initialize AASX processor with file path.
        
        Args:
            aasx_file_path: Path to the AASX file
        """
        self.aasx_file_path = Path(aasx_file_path)
        self.package_data = {}
        self.assets = []
        self.submodels = []
        self.documents = []
        
        if not self.aasx_file_path.exists():
            raise FileNotFoundError(f"AASX file not found: {aasx_file_path}")
        
        if not self.aasx_file_path.suffix.lower() == '.aasx':
            raise ValueError(f"File must have .aasx extension: {aasx_file_path}")
    
    def process(self) -> Dict[str, Any]:
        """
        Process the AASX file and extract all available data.
        
        Returns:
            Dictionary containing all extracted AASX data
        """
        logger.info(f"Processing AASX file: {self.aasx_file_path}")
        
        try:
            # Try .NET processor first (most comprehensive)
            if DOTNET_BRIDGE_AVAILABLE and dotnet_bridge and dotnet_bridge.is_available():
                logger.info("Trying .NET AAS processor...")
                result = dotnet_bridge.process_aasx_file(str(self.aasx_file_path))
                if result and 'error' not in result:
                    logger.info("Successfully processed with .NET processor")
                    return result
            
            # Try Python AAS libraries
            if AASX_PACKAGE_AVAILABLE and AAS_CORE_AVAILABLE:
                logger.info("Trying Python AAS libraries...")
                return self._process_with_aas_libraries()
            
            # Fallback to basic processing
            logger.info("Using basic ZIP processing...")
            return self._process_basic()
                
        except Exception as e:
            logger.error(f"Error processing AASX file: {e}")
            # Fallback to basic processing
            return self._process_basic()
    
    def _process_with_aas_libraries(self) -> Dict[str, Any]:
        """
        Process AASX file using specialized AAS libraries.
        """
        logger.info("Using advanced AAS libraries for processing")
        
        try:
            # Use aasx_package library
            with AASXPackage(self.aasx_file_path) as package:
                # Extract AAS objects
                aas_objects = package.get_aas_objects()
                
                # Process assets
                assets = []
                for obj in aas_objects:
                    if isinstance(obj, aas.AssetAdministrationShell):
                        asset_data = self._extract_asset_data(obj)
                        assets.append(asset_data)
                
                # Process submodels
                submodels = []
                for obj in aas_objects:
                    if isinstance(obj, aas.Submodel):
                        submodel_data = self._extract_submodel_data(obj)
                        submodels.append(submodel_data)
                
                # Extract documents
                documents = package.get_documents()
                
                return {
                    'processing_method': 'advanced_aas_libraries',
                    'assets': assets,
                    'submodels': submodels,
                    'documents': documents,
                    'metadata': {
                        'file_path': str(self.aasx_file_path),
                        'file_size': self.aasx_file_path.stat().st_size,
                        'processing_timestamp': datetime.now().isoformat(),
                        'libraries_used': ['aas_core3', 'aasx_package']
                    }
                }
                
        except Exception as e:
            logger.warning(f"Advanced processing failed: {e}")
            return self._process_basic()
    
    def _process_basic(self) -> Dict[str, Any]:
        """
        Process AASX file using basic ZIP and JSON/XML parsing.
        """
        logger.info("Using basic ZIP processing")
        
        try:
            with zipfile.ZipFile(self.aasx_file_path, 'r') as zip_file:
                # Extract all files
                file_list = zip_file.namelist()
                
                # Process AAS JSON files
                aas_data = {}
                for filename in file_list:
                    if filename.endswith('.json'):
                        try:
                            with zip_file.open(filename) as f:
                                content = f.read().decode('utf-8')
                                aas_data[filename] = json.loads(content)
                        except Exception as e:
                            logger.warning(f"Error reading {filename}: {e}")
                
                # Process XML files
                xml_data = {}
                for filename in file_list:
                    if filename.endswith('.xml'):
                        try:
                            with zip_file.open(filename) as f:
                                content = f.read().decode('utf-8')
                                xml_data[filename] = content
                        except Exception as e:
                            logger.warning(f"Error reading {filename}: {e}")
                
                # Extract documents
                documents = []
                for filename in file_list:
                    if any(filename.endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.txt']):
                        documents.append({
                            'filename': filename,
                            'size': zip_file.getinfo(filename).file_size,
                            'type': Path(filename).suffix
                        })
                
                # Parse AAS data
                assets = self._parse_aas_data(aas_data)
                submodels = self._parse_submodels(aas_data)
                
                return {
                    'processing_method': 'basic_zip_processing',
                    'assets': assets,
                    'submodels': submodels,
                    'documents': documents,
                    'raw_data': {
                        'json_files': list(aas_data.keys()),
                        'xml_files': list(xml_data.keys()),
                        'all_files': file_list
                    },
                    'metadata': {
                        'file_path': str(self.aasx_file_path),
                        'file_size': self.aasx_file_path.stat().st_size,
                        'processing_timestamp': datetime.now().isoformat(),
                        'libraries_used': ['zipfile', 'json', 'xml']
                    }
                }
                
        except Exception as e:
            logger.error(f"Basic processing failed: {e}")
            raise
    
    def _extract_asset_data(self, asset: Any) -> Dict[str, Any]:
        """
        Extract data from AAS Asset object.
        """
        try:
            return {
                'id': getattr(asset, 'id', None),
                'id_short': getattr(asset, 'id_short', None),
                'description': getattr(asset, 'description', None),
                'kind': getattr(asset, 'kind', None),
                'asset_information': self._extract_asset_information(asset),
                'submodels': [sm.id for sm in getattr(asset, 'submodels', [])]
            }
        except Exception as e:
            logger.warning(f"Error extracting asset data: {e}")
            return {}
    
    def _extract_asset_information(self, asset: Any) -> Dict[str, Any]:
        """
        Extract asset information from AAS Asset.
        """
        try:
            asset_info = getattr(asset, 'asset_information', None)
            if asset_info:
                return {
                    'asset_kind': getattr(asset_info, 'asset_kind', None),
                    'global_asset_id': getattr(asset_info, 'global_asset_id', None),
                    'specific_asset_ids': [
                        {
                            'key': getattr(sid, 'key', None),
                            'value': getattr(sid, 'value', None)
                        }
                        for sid in getattr(asset_info, 'specific_asset_ids', [])
                    ]
                }
            return {}
        except Exception as e:
            logger.warning(f"Error extracting asset information: {e}")
            return {}
    
    def _extract_submodel_data(self, submodel: Any) -> Dict[str, Any]:
        """
        Extract data from AAS Submodel object.
        """
        try:
            return {
                'id': getattr(submodel, 'id', None),
                'id_short': getattr(submodel, 'id_short', None),
                'description': getattr(submodel, 'description', None),
                'kind': getattr(submodel, 'kind', None),
                'semantic_id': getattr(submodel, 'semantic_id', None),
                'submodel_elements': self._extract_submodel_elements(submodel)
            }
        except Exception as e:
            logger.warning(f"Error extracting submodel data: {e}")
            return {}
    
    def _extract_submodel_elements(self, submodel: Any) -> List[Dict[str, Any]]:
        """
        Extract submodel elements from AAS Submodel.
        """
        try:
            elements = []
            for element in getattr(submodel, 'submodel_elements', []):
                element_data = {
                    'id_short': getattr(element, 'id_short', None),
                    'kind': getattr(element, 'kind', None),
                    'semantic_id': getattr(element, 'semantic_id', None)
                }
                
                # Extract property values
                if hasattr(element, 'value'):
                    element_data['value'] = getattr(element, 'value', None)
                
                elements.append(element_data)
            
            return elements
        except Exception as e:
            logger.warning(f"Error extracting submodel elements: {e}")
            return []
    
    def _parse_aas_data(self, aas_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse AAS data from JSON files with enhanced extraction.
        """
        assets = []
        
        for filename, data in aas_data.items():
            try:
                logger.info(f"Parsing AAS data from: {filename}")
                
                # Look for asset administration shells
                if 'assetAdministrationShells' in data:
                    for aas_obj in data['assetAdministrationShells']:
                        asset = {
                            'id': aas_obj.get('id'),
                            'id_short': aas_obj.get('idShort'),
                            'description': self._extract_description(aas_obj.get('description', {})),
                            'kind': aas_obj.get('kind'),
                            'asset_information': aas_obj.get('assetInformation', {}),
                            'submodels': aas_obj.get('submodels', []),
                            'derived_from': aas_obj.get('derivedFrom', {}),
                            'administration': aas_obj.get('administration', {}),
                            'semantic_id': aas_obj.get('semanticId', {}),
                            'qualifiers': aas_obj.get('qualifiers', []),
                            'embedded_data_specifications': aas_obj.get('embeddedDataSpecifications', [])
                        }
                        assets.append(asset)
                        logger.info(f"Found asset: {asset.get('id_short', 'Unknown')}")
                
                # Look for assets directly
                elif 'assets' in data:
                    for asset_obj in data['assets']:
                        asset = {
                            'id': asset_obj.get('id'),
                            'id_short': asset_obj.get('idShort'),
                            'description': self._extract_description(asset_obj.get('description', {})),
                            'kind': asset_obj.get('kind'),
                            'asset_information': asset_obj.get('assetInformation', {}),
                            'derived_from': asset_obj.get('derivedFrom', {}),
                            'administration': asset_obj.get('administration', {}),
                            'semantic_id': asset_obj.get('semanticId', {}),
                            'qualifiers': asset_obj.get('qualifiers', []),
                            'embedded_data_specifications': asset_obj.get('embeddedDataSpecifications', [])
                        }
                        assets.append(asset)
                        logger.info(f"Found asset: {asset.get('id_short', 'Unknown')}")
                
                # Look for concept descriptions
                elif 'conceptDescriptions' in data:
                    for concept_obj in data['conceptDescriptions']:
                        asset = {
                            'id': concept_obj.get('id'),
                            'id_short': concept_obj.get('idShort'),
                            'description': self._extract_description(concept_obj.get('description', {})),
                            'kind': 'ConceptDescription',
                            'category': concept_obj.get('category'),
                            'checksum': concept_obj.get('checksum'),
                            'administration': concept_obj.get('administration', {}),
                            'embedded_data_specifications': concept_obj.get('embeddedDataSpecifications', [])
                        }
                        assets.append(asset)
                        logger.info(f"Found concept description: {asset.get('id_short', 'Unknown')}")
                
                # Look for submodels
                elif 'submodels' in data:
                    for submodel_obj in data['submodels']:
                        asset = {
                            'id': submodel_obj.get('id'),
                            'id_short': submodel_obj.get('idShort'),
                            'description': self._extract_description(submodel_obj.get('description', {})),
                            'kind': 'Submodel',
                            'category': submodel_obj.get('category'),
                            'checksum': submodel_obj.get('checksum'),
                            'administration': submodel_obj.get('administration', {}),
                            'semantic_id': submodel_obj.get('semanticId', {}),
                            'qualifiers': submodel_obj.get('qualifiers', []),
                            'embedded_data_specifications': submodel_obj.get('embeddedDataSpecifications', []),
                            'submodel_elements': submodel_obj.get('submodelElements', [])
                        }
                        assets.append(asset)
                        logger.info(f"Found submodel: {asset.get('id_short', 'Unknown')}")
                        
            except Exception as e:
                logger.warning(f"Error parsing AAS data from {filename}: {e}")
        
        return assets
    
    def _extract_description(self, description_obj: Dict[str, Any]) -> str:
        """
        Extract description text from AAS description object.
        """
        if isinstance(description_obj, dict):
            # Try different language keys
            for lang in ['en', 'en-US', 'en-GB', 'de', 'fr', 'es']:
                if lang in description_obj:
                    return description_obj[lang]
            
            # If no language key, try to get any string value
            for key, value in description_obj.items():
                if isinstance(value, str):
                    return value
            
            # If still no string, return the whole object as string
            return str(description_obj)
        
        elif isinstance(description_obj, str):
            return description_obj
        
        return ""
    
    def _parse_submodels(self, aas_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse submodels from JSON files with enhanced extraction.
        """
        submodels = []
        
        for filename, data in aas_data.items():
            try:
                logger.info(f"Parsing submodels from: {filename}")
                
                # Look for submodels
                if 'submodels' in data:
                    for submodel_obj in data['submodels']:
                        submodel = {
                            'id': submodel_obj.get('id'),
                            'id_short': submodel_obj.get('idShort'),
                            'description': self._extract_description(submodel_obj.get('description', {})),
                            'kind': submodel_obj.get('kind'),
                            'category': submodel_obj.get('category'),
                            'checksum': submodel_obj.get('checksum'),
                            'administration': submodel_obj.get('administration', {}),
                            'semantic_id': submodel_obj.get('semanticId', {}),
                            'qualifiers': submodel_obj.get('qualifiers', []),
                            'embedded_data_specifications': submodel_obj.get('embeddedDataSpecifications', []),
                            'submodel_elements': self._parse_submodel_elements(submodel_obj.get('submodelElements', []))
                        }
                        submodels.append(submodel)
                        logger.info(f"Found submodel: {submodel.get('id_short', 'Unknown')}")
                
                # Also look for submodels in asset administration shells
                if 'assetAdministrationShells' in data:
                    for aas_obj in data['assetAdministrationShells']:
                        if 'submodels' in aas_obj:
                            for submodel_ref in aas_obj['submodels']:
                                submodel = {
                                    'id': submodel_ref.get('keys', [{}])[0].get('value', 'Unknown'),
                                    'id_short': f"Submodel_{submodel_ref.get('keys', [{}])[0].get('value', 'Unknown')}",
                                    'description': 'Submodel reference from AAS',
                                    'kind': 'SubmodelReference',
                                    'reference': submodel_ref
                                }
                                submodels.append(submodel)
                                logger.info(f"Found submodel reference: {submodel.get('id_short', 'Unknown')}")
                        
            except Exception as e:
                logger.warning(f"Error parsing submodels from {filename}: {e}")
        
        return submodels
    
    def _parse_submodel_elements(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse submodel elements with detailed extraction.
        """
        parsed_elements = []
        
        for element in elements:
            try:
                element_data = {
                    'id_short': element.get('idShort'),
                    'kind': element.get('kind'),
                    'semantic_id': element.get('semanticId', {}),
                    'qualifiers': element.get('qualifiers', []),
                    'embedded_data_specifications': element.get('embeddedDataSpecifications', [])
                }
                
                # Extract specific element types
                if 'property' in element:
                    element_data.update({
                        'type': 'Property',
                        'value': element['property'].get('value'),
                        'value_type': element['property'].get('valueType'),
                        'category': element['property'].get('category')
                    })
                elif 'collection' in element:
                    element_data.update({
                        'type': 'Collection',
                        'value': element['collection'].get('value', []),
                        'category': element['collection'].get('category')
                    })
                elif 'operation' in element:
                    element_data.update({
                        'type': 'Operation',
                        'input_variables': element['operation'].get('inputVariables', []),
                        'output_variables': element['operation'].get('outputVariables', []),
                        'inoutput_variables': element['operation'].get('inoutputVariables', [])
                    })
                elif 'relationshipElement' in element:
                    element_data.update({
                        'type': 'RelationshipElement',
                        'first': element['relationshipElement'].get('first', {}),
                        'second': element['relationshipElement'].get('second', {})
                    })
                else:
                    element_data['type'] = 'Unknown'
                    element_data['raw_data'] = element
                
                parsed_elements.append(element_data)
                
            except Exception as e:
                logger.warning(f"Error parsing submodel element: {e}")
                parsed_elements.append({
                    'id_short': element.get('idShort', 'Unknown'),
                    'type': 'Error',
                    'error': str(e),
                    'raw_data': element
                })
        
        return parsed_elements
    
    def get_asset_summary(self) -> Dict[str, Any]:
        """
        Get a summary of assets in the AASX file.
        """
        processed_data = self.process()
        
        summary = {
            'total_assets': len(processed_data.get('assets', [])),
            'total_submodels': len(processed_data.get('submodels', [])),
            'total_documents': len(processed_data.get('documents', [])),
            'processing_method': processed_data.get('processing_method'),
            'assets': []
        }
        
        for asset in processed_data.get('assets', []):
            asset_summary = {
                'id': asset.get('id'),
                'name': asset.get('id_short'),
                'description': asset.get('description', '')[:100] + '...' if len(asset.get('description', '')) > 100 else asset.get('description', ''),
                'type': asset.get('kind'),
                'submodel_count': len(asset.get('submodels', []))
            }
            summary['assets'].append(asset_summary)
        
        return summary
    
    def export_to_json(self, output_path: str) -> str:
        """
        Export processed AASX data to JSON file.
        
        Args:
            output_path: Path for the output JSON file
            
        Returns:
            Path to the exported JSON file
        """
        processed_data = self.process()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"AASX data exported to: {output_path}")
        return output_path


class AASXBatchProcessor:
    """
    Batch processor for multiple AASX files.
    """
    
    def __init__(self, directory_path: str):
        """
        Initialize batch processor with directory path.
        
        Args:
            directory_path: Path to directory containing AASX files
        """
        self.directory_path = Path(directory_path)
        self.processors = []
        
        if not self.directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    def find_aasx_files(self) -> List[Path]:
        """
        Find all AASX files in the directory.
        
        Returns:
            List of paths to AASX files
        """
        aasx_files = list(self.directory_path.glob("*.aasx"))
        logger.info(f"Found {len(aasx_files)} AASX files in {self.directory_path}")
        return aasx_files
    
    def process_all(self) -> Dict[str, Any]:
        """
        Process all AASX files in the directory.
        
        Returns:
            Dictionary containing results for all files
        """
        aasx_files = self.find_aasx_files()
        results = {
            'total_files': len(aasx_files),
            'processed_files': 0,
            'failed_files': 0,
            'results': {},
            'summary': {
                'total_assets': 0,
                'total_submodels': 0,
                'total_documents': 0
            }
        }
        
        for aasx_file in aasx_files:
            try:
                logger.info(f"Processing: {aasx_file.name}")
                processor = AASXProcessor(str(aasx_file))
                processed_data = processor.process()
                
                results['results'][aasx_file.name] = processed_data
                results['processed_files'] += 1
                
                # Update summary
                results['summary']['total_assets'] += len(processed_data.get('assets', []))
                results['summary']['total_submodels'] += len(processed_data.get('submodels', []))
                results['summary']['total_documents'] += len(processed_data.get('documents', []))
                
            except Exception as e:
                logger.error(f"Failed to process {aasx_file.name}: {e}")
                results['results'][aasx_file.name] = {'error': str(e)}
                results['failed_files'] += 1
        
        return results


# Utility functions
def validate_aasx_file(file_path: str) -> bool:
    """
    Validate if a file is a valid AASX file.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        True if valid AASX file, False otherwise
    """
    try:
        path = Path(file_path)
        if not path.exists() or path.suffix.lower() != '.aasx':
            return False
        
        with zipfile.ZipFile(path, 'r') as zip_file:
            # Check for AAS-related files
            file_list = zip_file.namelist()
            has_aas_files = any(
                filename.endswith('.json') or filename.endswith('.xml')
                for filename in file_list
            )
            
            return has_aas_files
            
    except Exception:
        return False


def get_aasx_info(file_path: str) -> Dict[str, Any]:
    """
    Get basic information about an AASX file.
    
    Args:
        file_path: Path to the AASX file
        
    Returns:
        Dictionary with basic file information
    """
    try:
        path = Path(file_path)
        info = {
            'filename': path.name,
            'file_path': str(path),
            'file_size': path.stat().st_size,
            'modified_date': datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
            'is_valid': validate_aasx_file(file_path)
        }
        
        if info['is_valid']:
            processor = AASXProcessor(file_path)
            summary = processor.get_asset_summary()
            info.update(summary)
        
        return info
        
    except Exception as e:
        logger.error(f"Error getting AASX info: {e}")
        return {
            'filename': Path(file_path).name,
            'file_path': file_path,
            'error': str(e),
            'is_valid': False
        } 