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
import re
import base64

# Configure logging
logger = logging.getLogger(__name__)


def auto_setup_dotnet_processor() -> bool:
    """
    Automatically set up the .NET AAS processor if not available.
    
    Returns:
        True if setup successful, False otherwise
    """
    try:
        from .dotnet_bridge import DotNetAasBridge
        
        bridge = DotNetAasBridge()
        
        if bridge.is_available():
            logger.info("✅ .NET AAS processor already available")
            return True
        
        logger.info("🔧 Auto-setting up .NET AAS processor...")
        
        # Try to build the processor
        if bridge._build_processor():
            logger.info("✅ .NET AAS processor auto-built successfully")
            return True
        else:
            logger.error("❌ Failed to auto-build .NET AAS processor")
            return False
            
    except Exception as e:
        logger.error(f"❌ Auto-setup failed: {e}")
        return False


# Try to import .NET bridge (primary method for AASX processing)
try:
    from .dotnet_bridge import DotNetAasBridge
    DOTNET_BRIDGE_AVAILABLE = True
    dotnet_bridge = DotNetAasBridge()
    
    # Auto-setup: If .NET processor not available, try to build it
    if not dotnet_bridge.is_available():
        logger.warning("⚠️  .NET processor not available. Auto-building it...")
        if auto_setup_dotnet_processor():
            # Re-initialize bridge after setup
            dotnet_bridge = DotNetAasBridge()
            if dotnet_bridge.is_available():
                logger.info("✅ .NET AAS processor ready after auto-setup")
            else:
                DOTNET_BRIDGE_AVAILABLE = False
        else:
            DOTNET_BRIDGE_AVAILABLE = False
            
except ImportError:
    DOTNET_BRIDGE_AVAILABLE = False
    dotnet_bridge = None
    logger.error("❌ DotNet bridge not available. This is required for proper AASX processing!")
    raise ImportError("DotNet bridge is required but not available")
except Exception as e:
    DOTNET_BRIDGE_AVAILABLE = False
    dotnet_bridge = None
    logger.error(f"❌ DotNet bridge initialization failed: {e}")
    raise ImportError(f"DotNet bridge initialization failed: {e}")

# Set Python AAS libraries as unavailable (they don't exist)
AAS_CORE_AVAILABLE = False
AASX_PACKAGE_AVAILABLE = False

# Ensure we have the .NET processor available
if not DOTNET_BRIDGE_AVAILABLE:
    logger.error("❌ .NET AAS processor is required but not available!")
    logger.error("Required: .NET AAS processor for proper AASX processing")
    raise ImportError("NET AAS processor is required but not available")


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
        self.validation_errors = []
        self.validation_warnings = []
        self.consistency_checks = []
        
        if not self.aasx_file_path.exists():
            raise FileNotFoundError(f"AASX file not found: {aasx_file_path}")
        
        if not self.aasx_file_path.suffix.lower() == '.aasx':
            raise ValueError(f"File must have .aasx extension: {aasx_file_path}")
    
    def ensure_processor_ready(self) -> bool:
        """
        Ensure the .NET AAS processor is ready for processing.
        Auto-setup if needed.
        
        Returns:
            True if processor is ready, False otherwise
        """
        global dotnet_bridge, DOTNET_BRIDGE_AVAILABLE
        
        if DOTNET_BRIDGE_AVAILABLE and dotnet_bridge and dotnet_bridge.is_available():
            logger.info(".NET AAS processor is ready")
            return True
        
        logger.warning(".NET processor not ready. Attempting auto-setup...")
        
        if auto_setup_dotnet_processor():
            # Re-initialize after setup
            try:
                dotnet_bridge = DotNetAasBridge()
                DOTNET_BRIDGE_AVAILABLE = dotnet_bridge.is_available()
                
                if DOTNET_BRIDGE_AVAILABLE:
                    logger.info(".NET AAS processor ready after auto-setup")
                    return True
                else:
                    logger.error(".NET processor still not available after setup")
                    return False
            except Exception as e:
                logger.error(f"Failed to re-initialize .NET bridge: {e}")
                return False
        else:
            logger.error("Auto-setup failed")
            return False
    
    def process(self) -> Dict[str, Any]:
        """
        Process the AASX file with complete information extraction.
        This method preserves all AAS XML content, relationships, and metadata for perfect round-trip conversion.
        
        Returns:
            Dictionary containing complete AAS data with full structure preservation
        """
        logger.info(f"Processing AASX file with complete processing: {self.aasx_file_path}")
        
        # Auto-setup: Ensure .NET processor is ready
        if not self.ensure_processor_ready():
            raise RuntimeError(".NET AAS processor setup failed! Cannot proceed with processing.")
        
        try:
            # Use .NET processor with complete processing
            logger.info("Using complete .NET AAS processor...")
            result = dotnet_bridge.process_aasx_file(str(self.aasx_file_path))
            if result and 'error' not in result:
                logger.info("Successfully processed with complete .NET processor")
                processed_result = self._validate_and_clean_result(result)
                return processed_result
            else:
                logger.error(".NET processor returned invalid result")
                raise RuntimeError("NET processor returned invalid result")
                
        except Exception as e:
            logger.error(f"Error processing AASX file: {e}")
            raise RuntimeError(f"Failed to process AASX file: {e}")
    
    def _process_enhanced(self) -> Dict[str, Any]:
        """
        Enhanced AASX processing with comprehensive XML parsing.
        """
        logger.info("Using enhanced ZIP processing with XML parsing")
        
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
                
                # Process XML files with enhanced parsing
                xml_data = {}
                for filename in file_list:
                    if filename.endswith('.xml') and not filename.startswith('[Content_Types]'):
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
                
                # Parse AAS data from both JSON and XML
                assets = self._parse_aas_data_enhanced(aas_data, xml_data)
                submodels = self._parse_submodels_enhanced(aas_data, xml_data)
                
                result = {
                    'processing_method': 'enhanced_zip_processing',
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
                        'libraries_used': ['zipfile', 'json', 'xml.etree.ElementTree']
                    }
                }
                
                return result
                
        except Exception as e:
            logger.error(f"Enhanced processing failed: {e}")
            raise
    
    def _parse_aas_data_enhanced(self, aas_data: Dict[str, Any], xml_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Enhanced AAS data parsing from both JSON and XML files.
        """
        assets = []
        
        # Parse from JSON files
        for filename, data in aas_data.items():
            try:
                logger.info(f"Parsing AAS data from JSON: {filename}")
                
                # Look for asset administration shells
                if 'assetAdministrationShells' in data:
                    for aas_obj in data['assetAdministrationShells']:
                        asset = self._extract_asset_from_json(aas_obj, filename)
                        if asset:
                            assets.append(asset)
                
                # Look for assets directly
                elif 'assets' in data:
                    for asset_obj in data['assets']:
                        asset = self._extract_asset_from_json(asset_obj, filename)
                        if asset:
                            assets.append(asset)
                            
            except Exception as e:
                logger.warning(f"Error parsing JSON AAS data from {filename}: {e}")
        
        # Parse from XML files
        for filename, content in xml_data.items():
            try:
                logger.info(f"Parsing AAS data from XML: {filename}")
                xml_assets = self._parse_xml_aas_data(content, filename)
                assets.extend(xml_assets)
            except Exception as e:
                logger.warning(f"Error parsing XML AAS data from {filename}: {e}")
        
        return assets
    
    def _parse_xml_aas_data(self, xml_content: str, filename: str) -> List[Dict[str, Any]]:
        """
        Parse AAS data from XML content with comprehensive extraction.
        """
        assets = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # Remove namespace for easier parsing
            for elem in root.iter():
                if elem.tag.startswith('{'):
                    elem.tag = elem.tag.split('}', 1)[1]
            
            # Look for AssetAdministrationShell elements
            for aas_elem in root.findall('.//assetAdministrationShell'):
                asset = self._extract_asset_from_xml(aas_elem, filename)
                if asset:
                    assets.append(asset)
            
            # Look for Asset elements
            for asset_elem in root.findall('.//asset'):
                asset = self._extract_asset_from_xml(asset_elem, filename)
                if asset:
                    assets.append(asset)
            
            # Look for Submodel elements
            for submodel_elem in root.findall('.//submodel'):
                submodel = self._extract_submodel_from_xml(submodel_elem, filename)
                if submodel:
                    # Convert submodel to asset format for consistency
                    asset = {
                        'id': submodel.get('id'),
                        'id_short': submodel.get('id_short'),
                        'description': submodel.get('description', ''),
                        'kind': 'Submodel',
                        'source': filename,
                        'format': 'XML'
                    }
                    assets.append(asset)
            
        except Exception as e:
            logger.warning(f"Error parsing XML content from {filename}: {e}")
        
        return assets
    
    def _extract_asset_from_xml(self, elem: ET.Element, filename: str) -> Optional[Dict[str, Any]]:
        """
        Extract asset data from XML element.
        """
        try:
            # Extract basic information
            asset_id = self._get_xml_text(elem, 'id')
            id_short = self._get_xml_text(elem, 'idShort')
            description = self._get_xml_text(elem, 'description')
            kind = self._get_xml_text(elem, 'kind')
            
            # Only return if we have valid data
            if asset_id or id_short:
                return {
                    'id': asset_id,
                    'id_short': id_short,
                    'description': description or '',
                    'kind': kind or 'Asset',
                    'source': filename,
                    'format': 'XML'
                }
            
        except Exception as e:
            logger.warning(f"Error extracting asset from XML: {e}")
        
        return None
    
    def _extract_submodel_from_xml(self, elem: ET.Element, filename: str) -> Optional[Dict[str, Any]]:
        """
        Extract submodel data from XML element.
        """
        try:
            # Extract basic information
            submodel_id = self._get_xml_text(elem, 'id')
            id_short = self._get_xml_text(elem, 'idShort')
            description = self._get_xml_text(elem, 'description')
            kind = self._get_xml_text(elem, 'kind')
            
            # Only return if we have valid data
            if submodel_id or id_short:
                return {
                    'id': submodel_id,
                    'id_short': id_short,
                    'description': description or '',
                    'kind': kind or 'Submodel',
                    'source': filename,
                    'format': 'XML'
                }
            
        except Exception as e:
            logger.warning(f"Error extracting submodel from XML: {e}")
        
        return None
    
    def _get_xml_text(self, elem: ET.Element, tag: str) -> Optional[str]:
        """
        Get text content from XML element safely.
        """
        try:
            child = elem.find(tag)
            if child is not None:
                return child.text.strip() if child.text else None
        except Exception:
            pass
        return None
    
    def _extract_asset_from_json(self, asset_obj: Dict[str, Any], filename: str) -> Optional[Dict[str, Any]]:
        """
        Extract asset data from JSON object with validation.
        """
        try:
            asset_id = asset_obj.get('id')
            id_short = asset_obj.get('idShort')
            description = self._extract_description(asset_obj.get('description', {}))
            kind = asset_obj.get('kind')
            
            # Only return if we have valid data
            if asset_id or id_short:
                return {
                    'id': asset_id,
                    'id_short': id_short,
                    'description': description or '',
                    'kind': kind or 'Asset',
                    'source': filename,
                    'format': 'JSON'
                }
            
        except Exception as e:
            logger.warning(f"Error extracting asset from JSON: {e}")
        
        return None
    
    def _parse_submodels_enhanced(self, aas_data: Dict[str, Any], xml_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Enhanced submodel parsing from both JSON and XML files.
        """
        submodels = []
        
        # Parse from JSON files
        for filename, data in aas_data.items():
            try:
                logger.info(f"Parsing submodels from JSON: {filename}")
                
                if 'submodels' in data:
                    for submodel_obj in data['submodels']:
                        submodel = self._extract_submodel_from_json(submodel_obj, filename)
                        if submodel:
                            submodels.append(submodel)
                            
            except Exception as e:
                logger.warning(f"Error parsing JSON submodels from {filename}: {e}")
        
        # Parse from XML files
        for filename, content in xml_data.items():
            try:
                logger.info(f"Parsing submodels from XML: {filename}")
                xml_submodels = self._parse_xml_submodels(content, filename)
                submodels.extend(xml_submodels)
            except Exception as e:
                logger.warning(f"Error parsing XML submodels from {filename}: {e}")
        
        return submodels
    
    def _parse_xml_submodels(self, xml_content: str, filename: str) -> List[Dict[str, Any]]:
        """
        Parse submodels from XML content.
        """
        submodels = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # Remove namespace for easier parsing
            for elem in root.iter():
                if elem.tag.startswith('{'):
                    elem.tag = elem.tag.split('}', 1)[1]
            
            # Look for Submodel elements
            for submodel_elem in root.findall('.//submodel'):
                submodel = self._extract_submodel_from_xml(submodel_elem, filename)
                if submodel:
                    submodels.append(submodel)
            
        except Exception as e:
            logger.warning(f"Error parsing XML submodels from {filename}: {e}")
        
        return submodels
    
    def _extract_submodel_from_json(self, submodel_obj: Dict[str, Any], filename: str) -> Optional[Dict[str, Any]]:
        """
        Extract submodel data from JSON object with validation.
        """
        try:
            submodel_id = submodel_obj.get('id')
            id_short = submodel_obj.get('idShort')
            description = self._extract_description(submodel_obj.get('description', {}))
            kind = submodel_obj.get('kind')
            
            # Only return if we have valid data
            if submodel_id or id_short:
                return {
                    'id': submodel_id,
                    'id_short': id_short,
                    'description': description or '',
                    'kind': kind or 'Submodel',
                    'source': filename,
                    'format': 'JSON'
                }
            
        except Exception as e:
            logger.warning(f"Error extracting submodel from JSON: {e}")
        
        return None
    
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
    
    def _validate_and_clean_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean the processing result to ensure data quality.
        """
        logger.info("Validating and cleaning processing result")
        
        # Clean assets - remove null entries
        if 'assets' in result:
            original_assets_count = len(result['assets'])
            result['assets'] = [asset for asset in result['assets'] if self._is_valid_asset(asset)]
            cleaned_assets_count = len(result['assets'])
            
            if original_assets_count != cleaned_assets_count:
                logger.info(f"Cleaned assets: {original_assets_count} -> {cleaned_assets_count}")
        
        # Clean submodels - remove null entries
        if 'submodels' in result:
            original_submodels_count = len(result['submodels'])
            result['submodels'] = [submodel for submodel in result['submodels'] if self._is_valid_submodel(submodel)]
            cleaned_submodels_count = len(result['submodels'])
            
            if original_submodels_count != cleaned_submodels_count:
                logger.info(f"Cleaned submodels: {original_submodels_count} -> {cleaned_submodels_count}")
        
        # Add validation metadata
        result['validation'] = {
            'timestamp': datetime.now().isoformat(),
            'total_assets': len(result.get('assets', [])),
            'total_submodels': len(result.get('submodels', [])),
            'total_documents': len(result.get('documents', [])),
            'validation_errors': self.validation_errors,
            'validation_warnings': self.validation_warnings,
            'consistency_checks': self.consistency_checks
        }
        
        return result
    
    def _is_valid_asset(self, asset: Dict[str, Any]) -> bool:
        """
        Check if asset has valid data according to AAS specification.
        In AAS 2.0+, idShort alone can be sufficient for some elements.
        """
        if not asset:
            return False
        
        # Check for different possible field names (handling .NET processor output)
        id_value = asset.get('id') or asset.get('Id') or asset.get('ID')
        id_short = asset.get('idShort') or asset.get('id_short') or asset.get('IdShort') or asset.get('ID_SHORT')
        
        # In AAS 2.0+, idShort alone can be sufficient
        # At least one of id or idShort must be present and non-empty
        has_valid_id = id_value is not None and str(id_value).strip()
        has_valid_id_short = id_short is not None and str(id_short).strip()
        
        if not has_valid_id and not has_valid_id_short:
            logger.debug(f"Asset missing both ID and ID_Short - ID: {id_value}, ID_Short: {id_short}")
            logger.debug(f"Asset keys: {list(asset.keys())}")
            return False
        
        # If we have idShort but no id, that's acceptable in AAS 2.0+
        if has_valid_id_short and not has_valid_id:
            logger.debug(f"Asset has idShort but no id (AAS 2.0+ acceptable): {id_short}")
            return True
        
        # Validate URL format if present
        if has_valid_id and isinstance(id_value, str):
            if not self._is_valid_url(id_value):
                logger.warning(f"Invalid URL format in asset id: {id_value}")
                # Don't fail validation for URL format issues
        
        return True
    
    def _is_valid_submodel(self, submodel: Dict[str, Any]) -> bool:
        """
        Check if submodel has valid data according to AAS specification.
        In AAS 2.0+, idShort alone can be sufficient for some elements.
        """
        if not submodel:
            return False
        
        # Check for different possible field names (handling .NET processor output)
        id_value = submodel.get('id') or submodel.get('Id') or submodel.get('ID')
        id_short = submodel.get('idShort') or submodel.get('id_short') or submodel.get('IdShort') or submodel.get('ID_SHORT')
        
        # In AAS 2.0+, idShort alone can be sufficient
        # At least one of id or idShort must be present and non-empty
        has_valid_id = id_value is not None and str(id_value).strip()
        has_valid_id_short = id_short is not None and str(id_short).strip()
        
        if not has_valid_id and not has_valid_id_short:
            logger.debug(f"Submodel missing both ID and ID_Short - ID: {id_value}, ID_Short: {id_short}")
            logger.debug(f"Submodel keys: {list(submodel.keys())}")
            return False
        
        # If we have idShort but no id, that's acceptable in AAS 2.0+
        if has_valid_id_short and not has_valid_id:
            logger.debug(f"Submodel has idShort but no id (AAS 2.0+ acceptable): {id_short}")
            return True
        
        # Validate URL format if present
        if has_valid_id and isinstance(id_value, str):
            if not self._is_valid_url(id_value):
                logger.warning(f"Invalid URL format in submodel id: {id_value}")
                # Don't fail validation for URL format issues
        
        return True
    
    def _is_valid_entry(self, entry: Dict[str, Any]) -> bool:
        """
        Check if an entry has valid data according to AAS specification.
        """
        if not entry:
            return False
        
        # Check for different possible field names (handling .NET processor output)
        id_value = entry.get('id') or entry.get('Id') or entry.get('ID')
        id_short = entry.get('idShort') or entry.get('id_short') or entry.get('IdShort') or entry.get('ID_SHORT')
        
        # Handle None values and empty strings
        if id_value is None or id_short is None:
            return False
        
        if not str(id_value).strip() or not str(id_short).strip():
            return False
        
        return True
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Validate if a URL is properly formatted.
        """
        if not url:
            return False
        
        try:
            # Basic URL validation - handle common malformations
            url_lower = url.lower()
            
            # Check for common URL schemes
            if url_lower.startswith(('http://', 'https://', 'urn:', 'mailto:')):
                return True
            
            # Handle malformed URLs (like 'http.//' instead of 'http://')
            if url_lower.startswith('http.//'):
                logger.warning(f"Malformed URL detected (http.//): {url}")
                return False
            
            # Handle other malformations
            if url_lower.startswith('http') and '://' not in url:
                logger.warning(f"Malformed URL detected (missing ://): {url}")
                return False
            
            return False
        except:
            return False

    # Note: Python AAS libraries (aas_core3, aasx_package) are not available
    # All processing is done through the .NET AAS processor

    def get_asset_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the processed AASX file.
        """
        return {
            'file_path': str(self.aasx_file_path),
            'file_size': self.aasx_file_path.stat().st_size,
            'total_assets': len(self.assets),
            'total_submodels': len(self.submodels),
            'total_documents': len(self.documents),
            'processing_timestamp': datetime.now().isoformat()
        }
    
    def export_to_json(self, output_path: str) -> str:
        """
        Export processed data to JSON file.
        """
        result = self.process()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        
        return output_path


class AASXBatchProcessor:
    """
    Batch processor for multiple AASX files with validation.
    """
    
    def __init__(self, directory_path: str):
        """
        Initialize batch processor.
        
        Args:
            directory_path: Directory containing AASX files
        """
        self.directory_path = Path(directory_path)
        self.processors = []
        self.results = []
        self.validation_summary = {
            'total_files': 0,
            'successful_processing': 0,
            'failed_processing': 0,
            'validation_errors': [],
            'consistency_issues': []
        }
    
    def find_aasx_files(self) -> List[Path]:
        """
        Find all AASX files in the directory.
        """
        aasx_files = []
        
        if self.directory_path.exists():
            for file_path in self.directory_path.rglob("*.aasx"):
                aasx_files.append(file_path)
        
        return aasx_files
    
    def process_all(self) -> Dict[str, Any]:
        """
        Process all AASX files in the directory.
        """
        aasx_files = self.find_aasx_files()
        self.validation_summary['total_files'] = len(aasx_files)
        
        logger.info(f"Found {len(aasx_files)} AASX files for batch processing")
        
        for file_path in aasx_files:
            try:
                logger.info(f"Processing: {file_path}")
                processor = AASXProcessor(str(file_path))
                result = processor.process()
                
                if result and result.get('validation', {}).get('total_assets', 0) > 0:
                    self.results.append(result)
                    self.validation_summary['successful_processing'] += 1
                    logger.info(f"Successfully processed: {file_path}")
                else:
                    self.validation_summary['failed_processing'] += 1
                    logger.warning(f"Failed to process: {file_path}")
                
                # Collect validation errors
                if result and 'validation' in result:
                    validation = result['validation']
                    if validation.get('validation_errors'):
                        self.validation_summary['validation_errors'].extend(validation['validation_errors'])
                    if validation.get('validation_warnings'):
                        self.validation_summary['validation_warnings'].extend(validation['validation_warnings'])
                    if validation.get('consistency_checks'):
                        self.validation_summary['consistency_issues'].extend(validation['consistency_checks'])
                
            except Exception as e:
                self.validation_summary['failed_processing'] += 1
                logger.error(f"Error processing {file_path}: {e}")
        
        return {
            'results': self.results,
            'validation_summary': self.validation_summary,
            'processing_timestamp': datetime.now().isoformat()
        }


def validate_aasx_file(file_path: str) -> bool:
    """
    Validate AASX file structure and content.
    """
    try:
        processor = AASXProcessor(file_path)
        result = processor.process()
        
        if not result:
            return False
        
        # Check if we have any valid data
        validation = result.get('validation', {})
        total_assets = validation.get('total_assets', 0)
        total_submodels = validation.get('total_submodels', 0)
        
        # File is valid if it has at least some assets or submodels
        return total_assets > 0 or total_submodels > 0
        
    except Exception as e:
        logger.error(f"Validation failed for {file_path}: {e}")
        return False


def get_aasx_info(file_path: str) -> Dict[str, Any]:
    """
    Get basic information about an AASX file.
    """
    try:
        processor = AASXProcessor(file_path)
        return processor.get_asset_summary()
    except Exception as e:
        logger.error(f"Error getting AASX info for {file_path}: {e}")
        return {} 