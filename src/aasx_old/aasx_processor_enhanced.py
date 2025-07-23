"""
Enhanced AASX Processor
Advanced AASX processing with complete structure preservation for perfect round-trip conversion.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from .dotnet_bridge import DotNetAasBridge

logger = logging.getLogger(__name__)

class EnhancedAasxProcessor:
    """
    Enhanced AASX processor that preserves complete structure for perfect round-trip conversion.
    """
    
    def __init__(self, dotnet_project_path: str = "aas-processor"):
        """
        Initialize the enhanced AASX processor.
        
        Args:
            dotnet_project_path: Path to the .NET AAS processor project
        """
        self.bridge = DotNetAasBridge(dotnet_project_path)
        
    def process_aasx_file(self, aasx_file_path: str, output_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Process an AASX file with enhanced processing for complete structure preservation.
        
        Args:
            aasx_file_path: Path to the AASX file
            output_path: Optional path to save the enhanced JSON output
            
        Returns:
            Dictionary containing enhanced AAS data with complete structure or None if failed
        """
        try:
            logger.info(f"Processing AASX file with enhanced processor: {aasx_file_path}")
            
            # Use the enhanced .NET processor
            result = self.bridge.process_aasx_file_enhanced(aasx_file_path)
            
            if result is None:
                logger.error("Enhanced processing failed")
                return None
            
            # Save to output file if specified
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                logger.info(f"Enhanced AASX data saved to: {output_path}")
            
            logger.info("Enhanced AASX processing completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in enhanced AASX processing: {e}")
            return None
    
    def extract_embedded_files(self, aasx_file_path: str, output_dir: str) -> Optional[Dict[str, Any]]:
        """
        Extract embedded files from AASX with enhanced metadata.
        
        Args:
            aasx_file_path: Path to the AASX file
            output_dir: Directory to extract embedded files to
            
        Returns:
            Dictionary containing extraction results or None if failed
        """
        try:
            logger.info(f"Extracting embedded files from: {aasx_file_path}")
            
            # Process the AASX file first
            result = self.process_aasx_file(aasx_file_path)
            if result is None:
                return None
            
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            extracted_files = []
            embedded_files = result.get('embeddedFiles', {})
            
            # Extract each embedded file
            for file_path, file_info in embedded_files.items():
                if isinstance(file_info, dict) and not file_info.get('is_directory', False):
                    try:
                        # Extract the file from AASX
                        from zipfile import ZipFile
                        with ZipFile(aasx_file_path, 'r') as zip_file:
                            zip_file.extract(file_path, output_dir)
                        
                        extracted_files.append({
                            'original_path': file_path,
                            'extracted_path': str(output_path / file_path),
                            'size': file_info.get('size', 0),
                            'type': file_info.get('type', ''),
                            'compression_method': file_info.get('compression_method', ''),
                            'last_modified': file_info.get('last_modified', ''),
                            'crc32': file_info.get('crc32', '')
                        })
                        
                        logger.info(f"Extracted: {file_path}")
                        
                    except Exception as e:
                        logger.warning(f"Failed to extract {file_path}: {e}")
            
            extraction_result = {
                'aasx_file': aasx_file_path,
                'output_directory': str(output_path),
                'extracted_files': extracted_files,
                'total_files': len(extracted_files),
                'enhanced_data': result
            }
            
            logger.info(f"Extracted {len(extracted_files)} files to: {output_path}")
            return extraction_result
            
        except Exception as e:
            logger.error(f"Error extracting embedded files: {e}")
            return None
    
    def analyze_structure(self, aasx_file_path: str) -> Optional[Dict[str, Any]]:
        """
        Analyze the complete structure of an AASX file.
        
        Args:
            aasx_file_path: Path to the AASX file
            
        Returns:
            Dictionary containing structure analysis or None if failed
        """
        try:
            logger.info(f"Analyzing AASX structure: {aasx_file_path}")
            
            # Process the AASX file
            result = self.process_aasx_file(aasx_file_path)
            if result is None:
                return None
            
            # Analyze the structure
            analysis = {
                'aasx_file': aasx_file_path,
                'aas_version': result.get('aasVersion', 'UNKNOWN'),
                'namespaces': result.get('namespaces', {}),
                'structure_summary': {
                    'total_entries': result.get('aasxStructure', {}).get('total_entries', 0),
                    'assets_count': len(result.get('assets', [])),
                    'submodels_count': len(result.get('submodels', [])),
                    'documents_count': len(result.get('documents', [])),
                    'images_count': len(result.get('images', [])),
                    'other_files_count': len(result.get('other_files', [])),
                    'embedded_files_count': len(result.get('embeddedFiles', {}))
                },
                'relationships': {
                    'asset_submodel_relationships': len(result.get('assetSubmodelRelationships', [])),
                    'file_relationships': len(result.get('fileRelationships', []))
                },
                'aasx_structure': result.get('aasxStructure', {}),
                'aas_xml_files': list(result.get('aasXmlContent', {}).keys()),
                'processing_method': result.get('processing_method', ''),
                'processing_timestamp': result.get('processing_timestamp', '')
            }
            
            logger.info(f"Structure analysis completed for: {aasx_file_path}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing AASX structure: {e}")
            return None
    
    def validate_round_trip_compatibility(self, aasx_file_path: str) -> Optional[Dict[str, Any]]:
        """
        Validate that the AASX file contains all information needed for perfect round-trip conversion.
        
        Args:
            aasx_file_path: Path to the AASX file
            
        Returns:
            Dictionary containing validation results or None if failed
        """
        try:
            logger.info(f"Validating round-trip compatibility: {aasx_file_path}")
            
            # Process the AASX file
            result = self.process_aasx_file(aasx_file_path)
            if result is None:
                return None
            
            validation = {
                'aasx_file': aasx_file_path,
                'validation_timestamp': result.get('processing_timestamp', ''),
                'checks': {}
            }
            
            # Check 1: AAS XML Content
            aas_xml_content = result.get('aasXmlContent', {})
            validation['checks']['aas_xml_content'] = {
                'present': len(aas_xml_content) > 0,
                'count': len(aas_xml_content),
                'files': list(aas_xml_content.keys())
            }
            
            # Check 2: Namespaces
            namespaces = result.get('namespaces', {})
            validation['checks']['namespaces'] = {
                'present': len(namespaces) > 0,
                'count': len(namespaces),
                'namespaces': namespaces
            }
            
            # Check 3: AASX Structure
            aasx_structure = result.get('aasxStructure', {})
            validation['checks']['aasx_structure'] = {
                'present': len(aasx_structure) > 0,
                'has_origin': 'aasx_origin' in aasx_structure,
                'has_relationships': any(k.startswith('rels_') for k in aasx_structure.keys())
            }
            
            # Check 4: Relationships
            asset_relationships = result.get('assetSubmodelRelationships', [])
            file_relationships = result.get('fileRelationships', [])
            validation['checks']['relationships'] = {
                'asset_submodel_relationships': len(asset_relationships),
                'file_relationships': len(file_relationships)
            }
            
            # Check 5: Embedded Files
            embedded_files = result.get('embeddedFiles', {})
            validation['checks']['embedded_files'] = {
                'present': len(embedded_files) > 0,
                'count': len(embedded_files),
                'has_metadata': all(isinstance(v, dict) for v in embedded_files.values())
            }
            
            # Overall compatibility score
            checks = validation['checks']
            score = 0
            total_checks = 5
            
            if checks['aas_xml_content']['present']:
                score += 1
            if checks['namespaces']['present']:
                score += 1
            if checks['aasx_structure']['present']:
                score += 1
            if checks['relationships']['asset_submodel_relationships'] > 0 or checks['relationships']['file_relationships'] > 0:
                score += 1
            if checks['embedded_files']['present']:
                score += 1
            
            validation['compatibility_score'] = score / total_checks
            validation['compatible_for_round_trip'] = score >= 4  # At least 80% compatibility
            
            logger.info(f"Round-trip compatibility validation completed: {validation['compatibility_score']:.2%}")
            return validation
            
        except Exception as e:
            logger.error(f"Error validating round-trip compatibility: {e}")
            return None

def test_enhanced_processor():
    """
    Test the enhanced AASX processor with a sample file.
    """
    processor = EnhancedAasxProcessor()
    
    # Test with a sample AASX file
    sample_file = "data/aasx-examples/Example_AAS_ServoDCMotor_21.aasx"
    
    if Path(sample_file).exists():
        print(f"Testing enhanced processor with: {sample_file}")
        
        # Test basic processing
        result = processor.process_aasx_file(sample_file)
        if result:
            print("✓ Enhanced processing successful")
            print(f"  AAS Version: {result.get('aasVersion', 'UNKNOWN')}")
            print(f"  Assets: {len(result.get('assets', []))}")
            print(f"  Submodels: {len(result.get('submodels', []))}")
            print(f"  Embedded Files: {len(result.get('embeddedFiles', {}))}")
        else:
            print("✗ Enhanced processing failed")
        
        # Test structure analysis
        analysis = processor.analyze_structure(sample_file)
        if analysis:
            print("✓ Structure analysis successful")
            print(f"  Structure Summary: {analysis['structure_summary']}")
        else:
            print("✗ Structure analysis failed")
        
        # Test round-trip validation
        validation = processor.validate_round_trip_compatibility(sample_file)
        if validation:
            print("✓ Round-trip validation successful")
            print(f"  Compatibility Score: {validation['compatibility_score']:.2%}")
            print(f"  Compatible for Round-trip: {validation['compatible_for_round_trip']}")
        else:
            print("✗ Round-trip validation failed")
    else:
        print(f"Sample file not found: {sample_file}")

if __name__ == "__main__":
    test_enhanced_processor() 