#!/usr/bin/env python3
"""
Generate AASX Files from JSON/YAML Data
=======================================

This script performs the reverse process: converts JSON/YAML files back to AASX files.
It's the counterpart to convert_aasx_to_formats.py.
"""

import sys
import json
import yaml
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from aasx.aasx_generator import AASXGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AASXGeneratorConverter:
    """
    Converts JSON/YAML files back to AASX files.
    """
    
    def __init__(self, input_dir: str, output_dir: str, aas_version: str = "2.0"):
        """
        Initialize the converter.
        
        Args:
            input_dir: Directory containing JSON/YAML files
            output_dir: Directory to save generated AASX files
            aas_version: AAS version to use for generation
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.aas_version = aas_version
        self.generator = AASXGenerator(str(output_dir))
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Statistics
        self.total_files = 0
        self.successful = 0
        self.failed = 0
        self.errors = []
    
    def find_input_files(self) -> List[Path]:
        """
        Find all JSON and YAML files in the input directory.
        
        Returns:
            List of file paths
        """
        files = []
        
        if self.input_dir.exists():
            # Find JSON files
            json_files = list(self.input_dir.rglob("*.json"))
            files.extend(json_files)
            
            # Find YAML files
            yaml_files = list(self.input_dir.rglob("*.yaml"))
            yaml_files.extend(list(self.input_dir.rglob("*.yml")))
            files.extend(yaml_files)
        
        return files
    
    def process_file(self, file_path: Path) -> bool:
        """
        Process a single JSON/YAML file and generate AASX.
        
        Args:
            file_path: Path to input file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Processing file: {file_path}")
            
            # Determine file type and process accordingly
            if file_path.suffix.lower() == '.json':
                aasx_path = self.generator.generate_from_json(str(file_path), self.aas_version)
            elif file_path.suffix.lower() in ['.yaml', '.yml']:
                aasx_path = self.generator.generate_from_yaml(str(file_path), self.aas_version)
            else:
                logger.warning(f"Unsupported file type: {file_path}")
                return False
            
            logger.info(f"Successfully generated AASX: {aasx_path}")
            return True
            
        except Exception as e:
            error_msg = f"Error processing {file_path}: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False
    
    def run_conversion(self) -> Dict[str, Any]:
        """
        Run the complete conversion process.
        
        Returns:
            Conversion report
        """
        logger.info("Starting JSON/YAML to AASX conversion process")
        logger.info(f"Input directory: {self.input_dir}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"AAS version: {self.aas_version}")
        
        # Find input files
        input_files = self.find_input_files()
        self.total_files = len(input_files)
        
        if self.total_files == 0:
            logger.warning("No JSON/YAML files found in input directory")
            return self._create_report()
        
        logger.info(f"Found {self.total_files} input files")
        
        # Process each file
        for file_path in input_files:
            logger.info(f"Processing: {file_path}")
            
            if self.process_file(file_path):
                self.successful += 1
                logger.info(f"Successfully converted: {file_path}")
            else:
                self.failed += 1
                logger.error(f"Failed to convert: {file_path}")
        
        # Create and save report
        report = self._create_report()
        self._save_report(report)
        
        logger.info("Conversion process completed")
        logger.info(f"Total files: {self.total_files}")
        logger.info(f"Successful: {self.successful}")
        logger.info(f"Failed: {self.failed}")
        logger.info(f"Success rate: {(self.successful/self.total_files*100):.1f}%")
        logger.info(f"AASX files saved to: {self.output_dir}")
        
        return report
    
    def _create_report(self) -> Dict[str, Any]:
        """
        Create conversion report.
        
        Returns:
            Report dictionary
        """
        return {
            'conversion_type': 'json_yaml_to_aasx',
            'timestamp': datetime.now().isoformat(),
            'input_directory': str(self.input_dir),
            'output_directory': str(self.output_dir),
            'aas_version': self.aas_version,
            'statistics': {
                'total_files': self.total_files,
                'successful': self.successful,
                'failed': self.failed,
                'success_rate': (self.successful/self.total_files*100) if self.total_files > 0 else 0
            },
            'errors': self.errors
        }
    
    def _save_report(self, report: Dict[str, Any]):
        """
        Save conversion report to file.
        
        Args:
            report: Report dictionary
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"generation_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Conversion report saved: {report_file}")


def main():
    """
    Main function.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert JSON/YAML files to AASX files")
    parser.add_argument("--input", "-i", default="data/samples_json", 
                       help="Input directory containing JSON/YAML files")
    parser.add_argument("--output", "-o", default="generated_aasx", 
                       help="Output directory for AASX files")
    parser.add_argument("--version", "-v", default="2.0", 
                       help="AAS version to use (1.0, 2.0, 3.0)")
    
    args = parser.parse_args()
    
    # Create converter and run conversion
    converter = AASXGeneratorConverter(args.input, args.output, args.version)
    report = converter.run_conversion()
    
    # Exit with error code if any failures
    if converter.failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main() 