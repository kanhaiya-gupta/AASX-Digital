#!/usr/bin/env python3
"""
AAS Processor Diagnostic Tool
============================

This script provides comprehensive diagnostics for the AAS processor to identify
and troubleshoot issues with AASX processing, ID extraction, and data validation.

Features:
- XML structure analysis
- Namespace detection
- Version identification
- ID extraction debugging
- File extraction verification
- Validation error analysis
- Performance metrics
- Detailed reporting

Usage:
    python scripts/diagnose_aas_processor.py [aasx_file_path]
    python scripts/diagnose_aas_processor.py --batch [directory]
    python scripts/diagnose_aas_processor.py --compare [file1] [file2]
"""

import os
import sys
import json
import time
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging
import argparse
import subprocess
import re
from dataclasses import dataclass, asdict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.aasx.aasx_processor import AASXProcessor
from src.shared.utils import setup_logging

@dataclass
class DiagnosticResult:
    """Structured diagnostic result"""
    timestamp: str
    file_path: str
    file_size: int
    processing_method: str
    aas_version: str
    namespaces_found: List[str]
    xml_structure: Dict[str, Any]
    id_extraction_status: Dict[str, Any]
    file_extraction_status: Dict[str, Any]
    validation_errors: List[str]
    performance_metrics: Dict[str, float]
    recommendations: List[str]
    raw_output: Dict[str, Any]

class AasProcessorDiagnostic:
    """Comprehensive AAS processor diagnostic tool"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.logger = setup_logging("aas_diagnostic", level=logging.DEBUG if verbose else logging.INFO)
        # Don't create processor here - create it when needed
        
    def diagnose_single_file(self, aasx_path: str) -> DiagnosticResult:
        """Diagnose a single AASX file"""
        start_time = time.time()
        
        self.logger.info(f"🔍 Starting diagnostic analysis for: {aasx_path}")
        
        # Basic file info
        file_path = Path(aasx_path)
        file_size = file_path.stat().st_size if file_path.exists() else 0
        
        # Step 1: Analyze AASX structure
        aasx_analysis = self._analyze_aasx_structure(aasx_path)
        
        # Step 2: Analyze XML content
        xml_analysis = self._analyze_xml_content(aasx_path)
        
        # Step 3: Test processor output
        processor_analysis = self._analyze_processor_output(aasx_path)
        
        # Step 4: Validate results
        validation_analysis = self._validate_results(processor_analysis)
        
        # Step 5: Generate recommendations
        recommendations = self._generate_recommendations(
            aasx_analysis, xml_analysis, processor_analysis, validation_analysis
        )
        
        processing_time = time.time() - start_time
        
        return DiagnosticResult(
            timestamp=datetime.now().isoformat(),
            file_path=str(aasx_path),
            file_size=file_size,
            processing_method=processor_analysis.get('processing_method', 'unknown'),
            aas_version=xml_analysis.get('detected_version', 'unknown'),
            namespaces_found=xml_analysis.get('namespaces', []),
            xml_structure=xml_analysis,
            id_extraction_status=validation_analysis.get('id_extraction', {}),
            file_extraction_status=validation_analysis.get('file_extraction', {}),
            validation_errors=validation_analysis.get('errors', []),
            performance_metrics={'processing_time_seconds': processing_time},
            recommendations=recommendations,
            raw_output=processor_analysis
        )
    
    def _analyze_aasx_structure(self, aasx_path: str) -> Dict[str, Any]:
        """Analyze AASX ZIP structure"""
        self.logger.info("📦 Analyzing AASX structure...")
        
        analysis = {
            'is_valid_zip': False,
            'total_files': 0,
            'file_types': {},
            'xml_files': [],
            'json_files': [],
            'document_files': [],
            'image_files': [],
            'other_files': [],
            'aasx_origin': None,
            'aasx_spec': None
        }
        
        try:
            with zipfile.ZipFile(aasx_path, 'r') as zip_file:
                analysis['is_valid_zip'] = True
                analysis['total_files'] = len(zip_file.namelist())
                
                for file_info in zip_file.filelist:
                    filename = file_info.filename
                    file_size = file_info.file_size
                    extension = Path(filename).suffix.lower()
                    
                    # Categorize files
                    if filename.endswith('.xml'):
                        analysis['xml_files'].append({
                            'name': filename,
                            'size': file_size,
                            'compressed_size': file_info.compress_size
                        })
                    elif filename.endswith('.json'):
                        analysis['json_files'].append({
                            'name': filename,
                            'size': file_size,
                            'compressed_size': file_info.compress_size
                        })
                    elif filename == 'aasx-origin':
                        analysis['aasx_origin'] = {
                            'name': filename,
                            'size': file_size,
                            'content': zip_file.read(filename).decode('utf-8', errors='ignore')
                        }
                    elif filename == 'aasx-spec':
                        analysis['aasx_spec'] = {
                            'name': filename,
                            'size': file_size,
                            'content': zip_file.read(filename).decode('utf-8', errors='ignore')
                        }
                    elif extension in ['.pdf', '.doc', '.docx', '.txt']:
                        analysis['document_files'].append({
                            'name': filename,
                            'size': file_size,
                            'type': extension
                        })
                    elif extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                        analysis['image_files'].append({
                            'name': filename,
                            'size': file_size,
                            'type': extension
                        })
                    else:
                        analysis['other_files'].append({
                            'name': filename,
                            'size': file_size,
                            'type': extension
                        })
                    
                    # Count file types
                    analysis['file_types'][extension] = analysis['file_types'].get(extension, 0) + 1
                
        except Exception as e:
            analysis['error'] = str(e)
            self.logger.error(f"Error analyzing AASX structure: {e}")
        
        return analysis
    
    def _analyze_xml_content(self, aasx_path: str) -> Dict[str, Any]:
        """Analyze XML content for AAS structure"""
        self.logger.info("📄 Analyzing XML content...")
        
        analysis = {
            'detected_version': 'unknown',
            'namespaces': [],
            'root_elements': [],
            'asset_elements': [],
            'submodel_elements': [],
            'id_elements': [],
            'description_elements': [],
            'xml_errors': []
        }
        
        try:
            with zipfile.ZipFile(aasx_path, 'r') as zip_file:
                xml_files = [f for f in zip_file.namelist() if f.endswith('.xml')]
                
                for xml_file in xml_files:
                    try:
                        xml_content = zip_file.read(xml_file).decode('utf-8', errors='ignore')
                        root = ET.fromstring(xml_content)
                        
                        # Analyze namespaces
                        namespaces = self._extract_namespaces(root)
                        analysis['namespaces'].extend(namespaces)
                        
                        # Detect AAS version
                        version = self._detect_aas_version_from_xml(root, namespaces)
                        if version != 'unknown':
                            analysis['detected_version'] = version
                        
                        # Analyze structure
                        structure = self._analyze_xml_structure(root, namespaces)
                        analysis['root_elements'].extend(structure.get('roots', []))
                        analysis['asset_elements'].extend(structure.get('assets', []))
                        analysis['submodel_elements'].extend(structure.get('submodels', []))
                        analysis['id_elements'].extend(structure.get('ids', []))
                        analysis['description_elements'].extend(structure.get('descriptions', []))
                        
                    except ET.ParseError as e:
                        analysis['xml_errors'].append(f"Parse error in {xml_file}: {e}")
                    except Exception as e:
                        analysis['xml_errors'].append(f"Error processing {xml_file}: {e}")
        
        except Exception as e:
            analysis['error'] = str(e)
            self.logger.error(f"Error analyzing XML content: {e}")
        
        # Remove duplicates
        analysis['namespaces'] = list(set(analysis['namespaces']))
        
        return analysis
    
    def _extract_namespaces(self, root: ET.Element) -> List[str]:
        """Extract all namespaces from XML"""
        namespaces = []
        
        # Get namespaces from root
        for prefix, uri in root.nsmap.items() if hasattr(root, 'nsmap') else []:
            namespaces.append(f"{prefix}:{uri}")
        
        # Get namespaces from attributes
        for key, value in root.attrib.items():
            if key.startswith('xmlns'):
                namespaces.append(f"{key}:{value}")
        
        # Extract namespaces from element tags (this is the key fix)
        for elem in root.iter():
            tag = elem.tag
            if tag.startswith('{') and '}' in tag:
                # Extract namespace from tag like "{http://www.admin-shell.io/aas/2/0}aasenv"
                namespace_start = tag.find('{') + 1
                namespace_end = tag.find('}')
                if namespace_start > 0 and namespace_end > namespace_start:
                    namespace = tag[namespace_start:namespace_end]
                    if namespace not in namespaces:
                        namespaces.append(namespace)
        
        return namespaces
    
    def _detect_aas_version_from_xml(self, root: ET.Element, namespaces: List[str]) -> str:
        """Detect AAS version from XML structure"""
        # Check for AAS 3.0 namespaces
        aas30_patterns = [
            'http://www.admin-shell.io/aas/3/0',
            'aas:3.0',
            'aas3'
        ]
        
        # Check for AAS 2.0 namespaces
        aas20_patterns = [
            'http://www.admin-shell.io/aas/2/0',
            'aas:2.0',
            'aas2'
        ]
        
        # Check for AAS 1.0 namespaces
        aas10_patterns = [
            'http://www.admin-shell.io/aas/1/0',
            'aas:1.0',
            'aas1'
        ]
        
        # Check extracted namespaces
        for ns in namespaces:
            for pattern in aas30_patterns:
                if pattern in ns:
                    return '3.0'
            for pattern in aas20_patterns:
                if pattern in ns:
                    return '2.0'
            for pattern in aas10_patterns:
                if pattern in ns:
                    return '1.0'
        
        # Check element names as fallback
        element_names = [elem.tag for elem in root.iter()]
        
        if any('aas3' in name.lower() for name in element_names):
            return '3.0'
        elif any('aas2' in name.lower() for name in element_names):
            return '2.0'
        elif any('aas1' in name.lower() for name in element_names):
            return '1.0'
        
        return 'unknown'
    
    def _analyze_xml_structure(self, root: ET.Element, namespaces: List[str]) -> Dict[str, List[str]]:
        """Analyze XML structure for AAS elements"""
        structure = {
            'roots': [],
            'assets': [],
            'submodels': [],
            'ids': [],
            'descriptions': []
        }
        
        # Find root elements
        structure['roots'].append(root.tag)
        
        # Find AAS-specific elements
        for elem in root.iter():
            tag = elem.tag.lower()
            
            if 'asset' in tag:
                structure['assets'].append(elem.tag)
            elif 'submodel' in tag:
                structure['submodels'].append(elem.tag)
            elif 'id' in tag:
                structure['ids'].append(elem.tag)
            elif 'description' in tag:
                structure['descriptions'].append(elem.tag)
        
        return structure
    
    def _analyze_processor_output(self, aasx_path: str) -> Dict[str, Any]:
        """Analyze processor output"""
        self.logger.info("⚙️ Analyzing processor output...")
        
        try:
            processor = AASXProcessor(aasx_path)
            result = processor.process()
            return result
        except Exception as e:
            self.logger.error(f"Error in processor analysis: {e}")
            return {'error': str(e)}
    
    def _validate_results(self, processor_output: Dict[str, Any]) -> Dict[str, Any]:
        """Validate processor results"""
        self.logger.info("✅ Validating results...")
        
        validation = {
            'id_extraction': {
                'assets_with_ids': 0,
                'assets_without_ids': 0,
                'submodels_with_ids': 0,
                'submodels_without_ids': 0,
                'total_assets': 0,
                'total_submodels': 0
            },
            'file_extraction': {
                'documents_found': 0,
                'images_found': 0,
                'other_files_found': 0,
                'total_files': 0
            },
            'errors': [],
            'warnings': []
        }
        
        try:
            # Validate assets
            assets = processor_output.get('assets', [])
            validation['id_extraction']['total_assets'] = len(assets)
            
            for asset in assets:
                asset_id = asset.get('id', '')
                if asset_id and asset_id.strip():
                    validation['id_extraction']['assets_with_ids'] += 1
                else:
                    validation['id_extraction']['assets_without_ids'] += 1
                    validation['warnings'].append(f"Asset '{asset.get('idShort', 'unknown')}' missing ID")
            
            # Validate submodels
            submodels = processor_output.get('submodels', [])
            validation['id_extraction']['total_submodels'] = len(submodels)
            
            for submodel in submodels:
                submodel_id = submodel.get('id', '')
                if submodel_id and submodel_id.strip():
                    validation['id_extraction']['submodels_with_ids'] += 1
                else:
                    validation['id_extraction']['submodels_without_ids'] += 1
                    validation['warnings'].append(f"Submodel '{submodel.get('idShort', 'unknown')}' missing ID")
            
            # Validate file extraction
            documents = processor_output.get('documents', [])
            images = processor_output.get('images', [])
            other_files = processor_output.get('other_files', [])
            
            validation['file_extraction']['documents_found'] = len(documents)
            validation['file_extraction']['images_found'] = len(images)
            validation['file_extraction']['other_files_found'] = len(other_files)
            validation['file_extraction']['total_files'] = len(documents) + len(images) + len(other_files)
            
            # Check for critical issues
            if validation['id_extraction']['assets_without_ids'] > 0:
                validation['errors'].append(f"{validation['id_extraction']['assets_without_ids']} assets missing IDs")
            
            if validation['id_extraction']['submodels_without_ids'] > 0:
                validation['errors'].append(f"{validation['id_extraction']['submodels_without_ids']} submodels missing IDs")
            
            if validation['file_extraction']['total_files'] == 0:
                validation['warnings'].append("No embedded files found")
        
        except Exception as e:
            validation['errors'].append(f"Validation error: {e}")
        
        return validation
    
    def _generate_recommendations(self, aasx_analysis: Dict, xml_analysis: Dict, 
                                processor_analysis: Dict, validation_analysis: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Check AASX structure
        if not aasx_analysis.get('is_valid_zip', False):
            recommendations.append("❌ AASX file is not a valid ZIP archive")
        
        if not aasx_analysis.get('xml_files'):
            recommendations.append("❌ No XML files found in AASX")
        
        # Check AAS version
        version = xml_analysis.get('detected_version', 'unknown')
        if version == 'unknown':
            recommendations.append("⚠️ Could not detect AAS version - may need namespace updates")
        else:
            recommendations.append(f"✅ Detected AAS version: {version}")
        
        # Check ID extraction
        id_extraction = validation_analysis.get('id_extraction', {})
        if id_extraction.get('assets_without_ids', 0) > 0:
            recommendations.append(f"🔧 {id_extraction['assets_without_ids']} assets missing IDs - check XML structure")
        
        if id_extraction.get('submodels_without_ids', 0) > 0:
            recommendations.append(f"🔧 {id_extraction['submodels_without_ids']} submodels missing IDs - check XML structure")
        
        # Check file extraction
        file_extraction = validation_analysis.get('file_extraction', {})
        if file_extraction.get('total_files', 0) == 0:
            recommendations.append("⚠️ No embedded files found - check AASX structure")
        
        # Check for specific issues
        if xml_analysis.get('xml_errors'):
            recommendations.append(f"❌ {len(xml_analysis['xml_errors'])} XML parsing errors found")
        
        if validation_analysis.get('errors'):
            recommendations.append(f"❌ {len(validation_analysis['errors'])} validation errors found")
        
        # Performance recommendations
        if processor_analysis.get('processing_time', 0) > 10:
            recommendations.append("🐌 Processing time > 10 seconds - consider optimization")
        
        return recommendations
    
    def diagnose_batch(self, directory: str) -> List[DiagnosticResult]:
        """Diagnose multiple AASX files"""
        self.logger.info(f"🔍 Starting batch diagnosis for directory: {directory}")
        
        results = []
        aasx_files = list(Path(directory).rglob("*.aasx"))
        
        self.logger.info(f"Found {len(aasx_files)} AASX files")
        
        for aasx_file in aasx_files:
            try:
                result = self.diagnose_single_file(str(aasx_file))
                results.append(result)
                self.logger.info(f"✅ Diagnosed: {aasx_file.name}")
            except Exception as e:
                self.logger.error(f"❌ Failed to diagnose {aasx_file.name}: {e}")
        
        return results
    
    def compare_results(self, result1: DiagnosticResult, result2: DiagnosticResult) -> Dict[str, Any]:
        """Compare two diagnostic results"""
        comparison = {
            'file1': result1.file_path,
            'file2': result2.file_path,
            'differences': {},
            'similarities': {},
            'recommendations': []
        }
        
        # Compare basic properties
        if result1.aas_version != result2.aas_version:
            comparison['differences']['aas_version'] = {
                'file1': result1.aas_version,
                'file2': result2.aas_version
            }
        
        if result1.file_size != result2.file_size:
            comparison['differences']['file_size'] = {
                'file1': result1.file_size,
                'file2': result2.file_size
            }
        
        # Compare ID extraction
        id1 = result1.id_extraction_status
        id2 = result2.id_extraction_status
        
        if id1.get('assets_with_ids', 0) != id2.get('assets_with_ids', 0):
            comparison['differences']['asset_ids'] = {
                'file1': id1.get('assets_with_ids', 0),
                'file2': id2.get('assets_with_ids', 0)
            }
        
        if id1.get('submodels_with_ids', 0) != id2.get('submodels_with_ids', 0):
            comparison['differences']['submodel_ids'] = {
                'file1': id1.get('submodels_with_ids', 0),
                'file2': id2.get('submodels_with_ids', 0)
            }
        
        # Generate recommendations
        if comparison['differences']:
            comparison['recommendations'].append("Files have different characteristics - may need different processing approaches")
        else:
            comparison['recommendations'].append("Files are similar - same processing approach should work")
        
        return comparison
    
    def generate_report(self, result: DiagnosticResult, output_file: Optional[str] = None) -> str:
        """Generate a detailed diagnostic report"""
        report = []
        report.append("=" * 80)
        report.append("🔍 AAS PROCESSOR DIAGNOSTIC REPORT")
        report.append("=" * 80)
        report.append(f"📅 Timestamp: {result.timestamp}")
        report.append(f"📁 File: {result.file_path}")
        report.append(f"📊 Size: {result.file_size:,} bytes")
        report.append(f"⚙️ Method: {result.processing_method}")
        report.append(f"🏷️ AAS Version: {result.aas_version}")
        report.append("")
        
        # Namespaces
        report.append("🏷️ NAMESPACES FOUND:")
        for ns in result.namespaces_found:
            report.append(f"  • {ns}")
        report.append("")
        
        # ID Extraction Status
        report.append("🆔 ID EXTRACTION STATUS:")
        id_status = result.id_extraction_status
        report.append(f"  • Assets with IDs: {id_status.get('assets_with_ids', 0)}/{id_status.get('total_assets', 0)}")
        report.append(f"  • Submodels with IDs: {id_status.get('submodels_with_ids', 0)}/{id_status.get('total_submodels', 0)}")
        report.append("")
        
        # File Extraction Status
        report.append("📁 FILE EXTRACTION STATUS:")
        file_status = result.file_extraction_status
        report.append(f"  • Documents: {file_status.get('documents_found', 0)}")
        report.append(f"  • Images: {file_status.get('images_found', 0)}")
        report.append(f"  • Other files: {file_status.get('other_files_found', 0)}")
        report.append("")
        
        # Validation Errors
        if result.validation_errors:
            report.append("❌ VALIDATION ERRORS:")
            for error in result.validation_errors:
                report.append(f"  • {error}")
            report.append("")
        
        # Performance Metrics
        report.append("⏱️ PERFORMANCE METRICS:")
        for metric, value in result.performance_metrics.items():
            report.append(f"  • {metric}: {value}")
        report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS:")
        for rec in result.recommendations:
            report.append(f"  • {rec}")
        report.append("")
        
        report.append("=" * 80)
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            self.logger.info(f"Report saved to: {output_file}")
        
        return report_text

def main():
    parser = argparse.ArgumentParser(description="AAS Processor Diagnostic Tool")
    parser.add_argument("input", nargs="?", help="AASX file or directory to diagnose")
    parser.add_argument("--batch", action="store_true", help="Process all AASX files in directory")
    parser.add_argument("--compare", nargs=2, metavar=("FILE1", "FILE2"), help="Compare two diagnostic results")
    parser.add_argument("--output", "-o", help="Output file for report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    
    args = parser.parse_args()
    
    if not args.input and not args.compare:
        parser.error("Please provide an input file/directory or use --compare")
    
    diagnostic = AasProcessorDiagnostic(verbose=args.verbose)
    
    if args.compare:
        # Compare two files
        result1 = diagnostic.diagnose_single_file(args.compare[0])
        result2 = diagnostic.diagnose_single_file(args.compare[1])
        comparison = diagnostic.compare_results(result1, result2)
        
        if args.json:
            print(json.dumps(comparison, indent=2))
        else:
            print("COMPARISON RESULTS:")
            print(json.dumps(comparison, indent=2))
    
    elif args.batch:
        # Batch processing
        results = diagnostic.diagnose_batch(args.input)
        
        if args.json:
            print(json.dumps([asdict(r) for r in results], indent=2))
        else:
            for result in results:
                report = diagnostic.generate_report(result)
                print(report)
                print("\n" + "="*80 + "\n")
    
    else:
        # Single file processing
        result = diagnostic.diagnose_single_file(args.input)
        
        if args.json:
            print(json.dumps(asdict(result), indent=2))
        else:
            report = diagnostic.generate_report(result, args.output)
            print(report)

if __name__ == "__main__":
    main() 