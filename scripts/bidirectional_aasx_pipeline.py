#!/usr/bin/env python3
"""
Bidirectional AASX Pipeline
===========================

This script provides a complete bidirectional pipeline for AASX files:
1. Forward: AASX → JSON/YAML (extraction)
2. Reverse: JSON/YAML → AASX (generation)

It can be used for:
- Data migration between formats
- AASX file validation and repair
- Format conversion workflows
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from aasx.aasx_processor import AASXProcessor
from aasx.aasx_generator import AASXGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BidirectionalAASXPipeline:
    """
    Bidirectional pipeline for AASX file processing.
    """
    
    def __init__(self, work_dir: str = "pipeline_workspace"):
        """
        Initialize the pipeline.
        
        Args:
            work_dir: Working directory for intermediate files
        """
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.work_dir / "input_aasx").mkdir(exist_ok=True)
        (self.work_dir / "intermediate_json").mkdir(exist_ok=True)
        (self.work_dir / "intermediate_yaml").mkdir(exist_ok=True)
        (self.work_dir / "output_aasx").mkdir(exist_ok=True)
        (self.work_dir / "reports").mkdir(exist_ok=True)
    
    def forward_process(self, aasx_file: str, preserve_structure: bool = True) -> Dict[str, str]:
        """
        Forward process: AASX → JSON/YAML.
        
        Args:
            aasx_file: Path to AASX file
            preserve_structure: Whether to preserve folder structure
            
        Returns:
            Dictionary with paths to generated JSON and YAML files
        """
        logger.info(f"Starting forward process: {aasx_file}")
        
        try:
            # Process AASX file
            processor = AASXProcessor(aasx_file)
            result = processor.process()
            
            if not result:
                raise RuntimeError("Failed to process AASX file")
            
            # Generate output filenames
            aasx_path = Path(aasx_file)
            base_name = aasx_path.stem
            
            if preserve_structure:
                # Preserve folder structure
                relative_path = aasx_path.parent.name
                json_dir = self.work_dir / "intermediate_json" / relative_path
                yaml_dir = self.work_dir / "intermediate_yaml" / relative_path
                json_dir.mkdir(parents=True, exist_ok=True)
                yaml_dir.mkdir(parents=True, exist_ok=True)
            else:
                json_dir = self.work_dir / "intermediate_json"
                yaml_dir = self.work_dir / "intermediate_yaml"
            
            json_file = json_dir / f"{base_name}.json"
            yaml_file = yaml_dir / f"{base_name}.yaml"
            
            # Save JSON
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
            
            # Save YAML
            import yaml
            with open(yaml_file, 'w', encoding='utf-8') as f:
                yaml.dump(result, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"Forward process completed:")
            logger.info(f"  JSON: {json_file}")
            logger.info(f"  YAML: {yaml_file}")
            
            return {
                'json_file': str(json_file),
                'yaml_file': str(yaml_file),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Forward process failed: {e}")
            return {
                'json_file': None,
                'yaml_file': None,
                'success': False,
                'error': str(e)
            }
    
    def reverse_process(self, json_file: str = None, yaml_file: str = None, 
                       aas_version: str = "2.0") -> Dict[str, str]:
        """
        Reverse process: JSON/YAML → AASX.
        
        Args:
            json_file: Path to JSON file (optional if yaml_file provided)
            yaml_file: Path to YAML file (optional if json_file provided)
            aas_version: AAS version to use for generation
            
        Returns:
            Dictionary with path to generated AASX file
        """
        logger.info("Starting reverse process")
        
        try:
            generator = AASXGenerator(str(self.work_dir / "output_aasx"))
            
            if json_file:
                logger.info(f"Generating AASX from JSON: {json_file}")
                aasx_file = generator.generate_from_json(json_file, aas_version)
            elif yaml_file:
                logger.info(f"Generating AASX from YAML: {yaml_file}")
                aasx_file = generator.generate_from_yaml(yaml_file, aas_version)
            else:
                raise ValueError("Either json_file or yaml_file must be provided")
            
            logger.info(f"Reverse process completed: {aasx_file}")
            
            return {
                'aasx_file': aasx_file,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Reverse process failed: {e}")
            return {
                'aasx_file': None,
                'success': False,
                'error': str(e)
            }
    
    def round_trip_process(self, aasx_file: str, aas_version: str = "2.0") -> Dict[str, Any]:
        """
        Complete round-trip process: AASX → JSON/YAML → AASX.
        
        Args:
            aasx_file: Path to original AASX file
            aas_version: AAS version to use for regeneration
            
        Returns:
            Complete round-trip report
        """
        logger.info(f"Starting round-trip process: {aasx_file}")
        
        # Step 1: Forward process
        forward_result = self.forward_process(aasx_file)
        
        if not forward_result['success']:
            return {
                'success': False,
                'error': f"Forward process failed: {forward_result.get('error')}",
                'step': 'forward'
            }
        
        # Step 2: Reverse process
        reverse_result = self.reverse_process(
            json_file=forward_result['json_file'],
            aas_version=aas_version
        )
        
        if not reverse_result['success']:
            return {
                'success': False,
                'error': f"Reverse process failed: {reverse_result.get('error')}",
                'step': 'reverse'
            }
        
        # Step 3: Compare original and regenerated files
        comparison_result = self._compare_aasx_files(aasx_file, reverse_result['aasx_file'])
        
        # Create complete report
        report = {
            'success': True,
            'original_aasx': aasx_file,
            'intermediate_files': forward_result,
            'regenerated_aasx': reverse_result['aasx_file'],
            'comparison': comparison_result,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save report
        self._save_round_trip_report(report, Path(aasx_file).stem)
        
        logger.info("Round-trip process completed successfully")
        return report
    
    def _compare_aasx_files(self, original_file: str, regenerated_file: str) -> Dict[str, Any]:
        """
        Compare original and regenerated AASX files.
        
        Args:
            original_file: Path to original AASX file
            regenerated_file: Path to regenerated AASX file
            
        Returns:
            Comparison results
        """
        try:
            # Process both files
            original_processor = AASXProcessor(original_file)
            regenerated_processor = AASXProcessor(regenerated_file)
            
            original_data = original_processor.process()
            regenerated_data = regenerated_processor.process()
            
            # Compare key metrics
            comparison = {
                'original_assets': len(original_data.get('assets', [])),
                'regenerated_assets': len(regenerated_data.get('assets', [])),
                'original_submodels': len(original_data.get('submodels', [])),
                'regenerated_submodels': len(regenerated_data.get('submodels', [])),
                'assets_match': len(original_data.get('assets', [])) == len(regenerated_data.get('assets', [])),
                'submodels_match': len(original_data.get('submodels', [])) == len(regenerated_data.get('submodels', []))
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Comparison failed: {e}")
            return {
                'error': str(e),
                'comparison_failed': True
            }
    
    def _save_round_trip_report(self, report: Dict[str, Any], base_name: str):
        """
        Save round-trip report to file.
        
        Args:
            report: Report dictionary
            base_name: Base name for the report file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.work_dir / "reports" / f"round_trip_{base_name}_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Round-trip report saved: {report_file}")
    
    def batch_process(self, input_dir: str, aas_version: str = "2.0") -> Dict[str, Any]:
        """
        Process all AASX files in a directory.
        
        Args:
            input_dir: Directory containing AASX files
            aas_version: AAS version to use
            
        Returns:
            Batch processing report
        """
        logger.info(f"Starting batch processing: {input_dir}")
        
        input_path = Path(input_dir)
        aasx_files = list(input_path.rglob("*.aasx"))
        
        if not aasx_files:
            logger.warning("No AASX files found")
            return {'success': False, 'error': 'No AASX files found'}
        
        results = []
        successful = 0
        failed = 0
        
        for aasx_file in aasx_files:
            logger.info(f"Processing: {aasx_file}")
            
            try:
                result = self.round_trip_process(str(aasx_file), aas_version)
                results.append(result)
                
                if result['success']:
                    successful += 1
                else:
                    failed += 1
                    
            except Exception as e:
                logger.error(f"Error processing {aasx_file}: {e}")
                failed += 1
                results.append({
                    'success': False,
                    'error': str(e),
                    'file': str(aasx_file)
                })
        
        # Create batch report
        batch_report = {
            'total_files': len(aasx_files),
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / len(aasx_files)) * 100,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save batch report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_report_file = self.work_dir / "reports" / f"batch_report_{timestamp}.json"
        
        with open(batch_report_file, 'w', encoding='utf-8') as f:
            json.dump(batch_report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Batch processing completed:")
        logger.info(f"  Total: {len(aasx_files)}")
        logger.info(f"  Successful: {successful}")
        logger.info(f"  Failed: {failed}")
        logger.info(f"  Success rate: {batch_report['success_rate']:.1f}%")
        logger.info(f"  Batch report: {batch_report_file}")
        
        return batch_report


def main():
    """
    Main function.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Bidirectional AASX Pipeline")
    parser.add_argument("--mode", "-m", choices=["forward", "reverse", "roundtrip", "batch"], 
                       default="roundtrip", help="Processing mode")
    parser.add_argument("--input", "-i", required=True, help="Input file or directory")
    parser.add_argument("--output", "-o", help="Output file (for reverse mode)")
    parser.add_argument("--version", "-v", default="2.0", help="AAS version")
    parser.add_argument("--work-dir", "-w", default="pipeline_workspace", help="Working directory")
    
    args = parser.parse_args()
    
    # Create pipeline
    pipeline = BidirectionalAASXPipeline(args.work_dir)
    
    if args.mode == "forward":
        result = pipeline.forward_process(args.input)
        print(f"Forward process result: {result}")
        
    elif args.mode == "reverse":
        if not args.output:
            print("Error: Output file required for reverse mode")
            sys.exit(1)
        result = pipeline.reverse_process(args.input, aas_version=args.version)
        print(f"Reverse process result: {result}")
        
    elif args.mode == "roundtrip":
        result = pipeline.round_trip_process(args.input, args.version)
        print(f"Round-trip process result: {result}")
        
    elif args.mode == "batch":
        result = pipeline.batch_process(args.input, args.version)
        print(f"Batch process result: {result}")


if __name__ == "__main__":
    main() 