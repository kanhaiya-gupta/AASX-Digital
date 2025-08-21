import argparse
import subprocess
import shutil
from pathlib import Path
import sys
import logging
from src.shared.utils.file_utils import FileUtils
from src.shared.utils.logging_utils import LoggingUtils

# Setup logging
logger = LoggingUtils.get_logger(__name__)

# AAS Processor project path
AAS_PROCESSOR_PROJECT = Path(__file__).parent.parent.parent / "aas-processor"

def run_command(cmd, description):
    """Run a command and return the result"""
    logger.info(f"🔄 {description}")
    logger.info(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"✅ Success: {description}")
        return {'status': 'completed', 'output': result.stdout}
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error: {description}")
        logger.error(f"STDOUT: {e.stdout}")
        logger.error(f"STDERR: {e.stderr}")
        return {'status': 'failed', 'error': e.stderr}
    except FileNotFoundError as e:
        logger.error(f"❌ Command not found: {cmd[0]}")
        logger.error(f"Error: {str(e)}")
        return {'status': 'failed', 'error': str(e)}

# ============================================================================
# EXTRACTION FUNCTIONS
# ============================================================================

def extract_aasx(aasx_path: Path, output_dir: Path, formats: list = None, mode: str = "process-enhanced"):
    """
    Extract structured data and documents from a single AASX file using dotnet commands.
    
    Args:
        aasx_path: Path to the AASX file
        output_dir: Output directory for extracted data
        formats: List of formats to export ['json', 'graph', 'rdf', 'yaml'] (default: all)
        mode: Processing mode - 'process', 'process-enhanced', 'process-aas20', 'process-aas30' (default: process-enhanced)
    """
    if formats is None:
        formats = ['json', 'graph', 'rdf', 'yaml']
    
    # Use FileUtils to create directory
    FileUtils.create_directory_structure(str(output_dir), "", "")
    file_stem = aasx_path.stem
    
    # Save a copy of the original AASX file
    original_copy_path = output_dir / f"{file_stem}_original.aasx"
    try:
        shutil.copy2(aasx_path, original_copy_path)
        logger.info(f"Saved original AASX file copy to {original_copy_path}")
    except Exception as e:
        logger.error(f"Failed to save original AASX file copy: {e}")
    
    results = {}
    
    # JSON extraction using dotnet run (this also creates YAML automatically)
    if 'json' in formats or 'yaml' in formats:
        json_output = output_dir / f"{file_stem}.json"
        cmd = [
            "dotnet", "run", "--project", str(AAS_PROCESSOR_PROJECT),
            mode,
            str(aasx_path),
            str(json_output)
        ]
        result = run_command(cmd, f"JSON extraction ({mode}): {aasx_path.name}")
        results['json'] = result
        
        # Check if YAML was also created (aas-processor creates both automatically)
        yaml_output = output_dir / f"{file_stem}.yaml"
        if yaml_output.exists():
            logger.info(f"YAML file automatically created: {yaml_output}")
            results['yaml'] = {'status': 'completed', 'output': str(yaml_output)}
        else:
            logger.warning(f"YAML file not found: {yaml_output}")
            results['yaml'] = {'status': 'failed', 'error': 'YAML file not created'}
    
    # Graph export using dotnet run
    if 'graph' in formats:
        graph_output = output_dir / f"{file_stem}_graph.json"
        cmd = [
            "dotnet", "run", "--project", str(AAS_PROCESSOR_PROJECT),
            "export-graph",
            str(aasx_path),
            str(graph_output)
        ]
        result = run_command(cmd, f"Graph export: {aasx_path.name}")
        results['graph'] = result
    
    # RDF/Turtle export using dotnet run
    if 'rdf' in formats:
        rdf_output = output_dir / f"{file_stem}.ttl"
        cmd = [
            "dotnet", "run", "--project", str(AAS_PROCESSOR_PROJECT),
            "export-rdf",
            str(aasx_path),
            str(rdf_output)
        ]
        result = run_command(cmd, f"RDF export: {aasx_path.name}")
        results['rdf'] = result
    
    # Add original file info to results
    results['original'] = {'status': 'completed', 'output': str(original_copy_path)}
    
    # Check for documents directory (created by enhanced processing)
    documents_dir = output_dir / f"{file_stem}_documents"
    if documents_dir.exists():
        logger.info(f"Documents directory found: {documents_dir}")
        doc_files = list(documents_dir.rglob("*"))
        results['documents'] = {
            'status': 'completed',
            'output': str(documents_dir),
            'file_count': len([f for f in doc_files if f.is_file()]),
            'files': [str(f.relative_to(documents_dir)) for f in doc_files if f.is_file()]
        }
    else:
        logger.warning(f"Documents directory not found: {documents_dir}")
        results['documents'] = {'status': 'failed', 'error': 'Documents directory not found'}
    
    # Determine overall status
    successful_formats = [fmt for fmt, result in results.items() if result.get('status') == 'completed']
    failed_formats = [fmt for fmt, result in results.items() if result.get('status') == 'failed']
    
    overall_status = 'completed' if successful_formats else 'failed'
    
    # Return standardized result format
    return {
        'status': overall_status,
        'formats': successful_formats,
        'failed_formats': failed_formats,
        'results': results,
        'processing_time': 0,  # TODO: Add actual timing
        'aas_data': None  # TODO: Extract AAS data from JSON if available
    }

def batch_extract(input_path: Path, output_dir: Path, formats: list = None, mode: str = "process-enhanced"):
    """
    Extract from a single file or all AASX files in a directory.
    
    Args:
        input_path: Path to AASX file or directory
        output_dir: Output directory
        formats: List of formats to export ['json', 'graph', 'rdf', 'yaml'] (default: all)
        mode: Processing mode - 'process', 'process-enhanced', 'process-aas20', 'process-aas30' (default: process-enhanced)
    """
    if formats is None:
        formats = ['json', 'graph', 'rdf', 'yaml']
    
    if input_path.is_file() and input_path.suffix.lower() == ".aasx":
        return extract_aasx(input_path, output_dir, formats, mode)
    elif input_path.is_dir():
        results = {}
        for aasx_file in input_path.glob("*.aasx"):
            file_output_dir = output_dir / aasx_file.stem
            results[aasx_file.name] = extract_aasx(aasx_file, file_output_dir, formats, mode)
        return results
    else:
        logger.error(f"Input {input_path} is not a valid AASX file or directory.")
        return None

# ============================================================================
# GENERATION FUNCTIONS
# ============================================================================

def generate_aasx(output_path: Path, data_source: Path = None):
    """
    Generate AASX file using dotnet run.
    
    Args:
        output_path: Path where the AASX file will be generated
        data_source: Optional path to data source (JSON, YAML, etc.)
    """
    if data_source:
        # Generate from structured data (JSON file + documents directory)
        cmd = [
            "dotnet", "run", "--project", str(AAS_PROCESSOR_PROJECT),
            "generate-structured",
            str(data_source),
            str(output_path)
        ]
        return run_command(cmd, f"Generate AASX from structured data: {data_source.name}")
    else:
        # Generate empty AASX (legacy method)
        cmd = [
            "dotnet", "run", "--project", str(AAS_PROCESSOR_PROJECT),
            "generate",
            "{}",  # Empty JSON data
            str(output_path)
        ]
        return run_command(cmd, f"Generate empty AASX: {output_path.name}")

def generate_aasx_from_structured(json_path: Path, output_aasx: Path):
    """
    Generate AASX file from structured JSON data using dotnet run.
    
    Args:
        json_path: Path to the JSON file
        output_aasx: Path for the output AASX file
    
    Returns:
        Dictionary with status and error information
    """
    cmd = [
        "dotnet", "run", "--project", str(AAS_PROCESSOR_PROJECT),
        "generate-structured",
        str(json_path),
        str(output_aasx)
    ]
    
    return run_command(cmd, f"Generate AASX from structured data: {json_path.name}")

def batch_generate(input_path: Path, output_dir: Path):
    """
    Generate AASX from a single structured file or all in a directory.
    """
    if input_path.is_file() and input_path.suffix.lower() in [".json", ".yaml", ".yml"]:
        output_aasx = output_dir / f"{input_path.stem}.aasx"
        return generate_aasx(output_aasx, input_path)
    elif input_path.is_dir():
        results = {}
        for structured_file in input_path.glob("*.json"):
            output_aasx = output_dir / f"{structured_file.stem}.aasx"
            results[structured_file.name] = generate_aasx(output_aasx, structured_file)
        for structured_file in input_path.glob("*.yaml"):
            output_aasx = output_dir / f"{structured_file.stem}.aasx"
            results[structured_file.name] = generate_aasx(output_aasx, structured_file)
        for structured_file in input_path.glob("*.yml"):
            output_aasx = output_dir / f"{structured_file.stem}.aasx"
            results[structured_file.name] = generate_aasx(output_aasx, structured_file)
        return results
    else:
        logger.error(f"Input {input_path} is not a valid structured file or directory.")
        return None

# ============================================================================
# ROUND-TRIP CONVERSION FUNCTIONS
# ============================================================================

def round_trip_conversion(aasx_path: Path, output_dir: Path, formats: list = None, mode: str = "process-enhanced"):
    """
    Perform complete round-trip conversion: AASX → JSON → AASX
    
    Args:
        aasx_path: Path to the original AASX file
        output_dir: Output directory for all files
        formats: List of formats to export during extraction
        mode: Processing mode for extraction
    
    Returns:
        Dictionary with results from both extraction and generation
    """
    file_stem = aasx_path.stem
    
    # Step 1: Extract AASX to structured data
    logger.info(f"🔄 Step 1: Extracting AASX to structured data...")
    extraction_result = extract_aasx(aasx_path, output_dir, formats, mode)
    
    if extraction_result['status'] != 'completed':
        logger.error("❌ Extraction failed, cannot proceed with round-trip conversion")
        return {
            'status': 'failed',
            'extraction': extraction_result,
            'generation': None,
            'round_trip_success': False
        }
    
    # Step 2: Generate AASX from structured data
    logger.info(f"🔄 Step 2: Generating AASX from structured data...")
    json_path = output_dir / f"{file_stem}.json"
    reconstructed_aasx = output_dir / f"{file_stem}_reconstructed.aasx"
    
    generation_result = generate_aasx_from_structured(json_path, reconstructed_aasx)
    
    # Determine overall success
    round_trip_success = (extraction_result['status'] == 'completed' and 
                         generation_result['status'] == 'completed')
    
    return {
        'status': 'completed' if round_trip_success else 'failed',
        'extraction': extraction_result,
        'generation': generation_result,
        'round_trip_success': round_trip_success,
        'original_file': str(aasx_path),
        'reconstructed_file': str(reconstructed_aasx),
        'json_file': str(json_path)
    }

# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="AASX Processor - Extract, Generate, and Convert AASX files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract AASX to structured data
  python aasx_processor.py extract input.aasx output/
  python aasx_processor.py extract input.aasx output/ --formats json yaml graph
  
  # Generate AASX from structured data
  python aasx_processor.py generate input.json output/
  
  # Round-trip conversion
  python aasx_processor.py round-trip input.aasx output/
  
  # Batch processing
  python aasx_processor.py extract-batch input_dir/ output/
  python aasx_processor.py generate-batch input_dir/ output/
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract AASX to structured data')
    extract_parser.add_argument("input", type=str, help="AASX file")
    extract_parser.add_argument("output", type=str, help="Output directory")
    extract_parser.add_argument("--formats", nargs="+", choices=['json', 'graph', 'rdf', 'yaml'], 
                               default=['json', 'graph', 'rdf', 'yaml'], 
                               help="Formats to export (default: all)")
    extract_parser.add_argument("--mode", choices=['process', 'process-enhanced', 'process-aas20', 'process-aas30'], 
                               default='process-enhanced',
                               help="Processing mode (default: process-enhanced)")
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate AASX from structured data')
    generate_parser.add_argument("input", type=str, help="Structured data file (JSON/YAML)")
    generate_parser.add_argument("output", type=str, help="Output directory")
    
    # Round-trip command
    round_trip_parser = subparsers.add_parser('round-trip', help='Perform round-trip conversion')
    round_trip_parser.add_argument("input", type=str, help="AASX file")
    round_trip_parser.add_argument("output", type=str, help="Output directory")
    round_trip_parser.add_argument("--formats", nargs="+", choices=['json', 'graph', 'rdf', 'yaml'], 
                                  default=['json', 'graph', 'rdf', 'yaml'], 
                                  help="Formats to export (default: all)")
    round_trip_parser.add_argument("--mode", choices=['process', 'process-enhanced', 'process-aas20', 'process-aas30'], 
                                  default='process-enhanced',
                                  help="Processing mode (default: process-enhanced)")
    
    # Batch extract command
    batch_extract_parser = subparsers.add_parser('extract-batch', help='Batch extract AASX files')
    batch_extract_parser.add_argument("input", type=str, help="Directory containing AASX files")
    batch_extract_parser.add_argument("output", type=str, help="Output directory")
    batch_extract_parser.add_argument("--formats", nargs="+", choices=['json', 'graph', 'rdf', 'yaml'], 
                                     default=['json', 'graph', 'rdf', 'yaml'], 
                                     help="Formats to export (default: all)")
    batch_extract_parser.add_argument("--mode", choices=['process', 'process-enhanced', 'process-aas20', 'process-aas30'], 
                                     default='process-enhanced',
                                     help="Processing mode (default: process-enhanced)")
    
    # Batch generate command
    batch_generate_parser = subparsers.add_parser('generate-batch', help='Batch generate AASX files')
    batch_generate_parser.add_argument("input", type=str, help="Directory containing structured data files")
    batch_generate_parser.add_argument("output", type=str, help="Output directory")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute the appropriate command
    if args.command == 'extract':
        result = extract_aasx(Path(args.input), Path(args.output), args.formats, args.mode)
        print(f"Extraction result: {result['status']}")
        
    elif args.command == 'generate':
        result = generate_aasx(Path(args.output) / f"{Path(args.input).stem}.aasx", Path(args.input))
        print(f"Generation result: {result['status']}")
        
    elif args.command == 'round-trip':
        result = round_trip_conversion(Path(args.input), Path(args.output), args.formats, args.mode)
        print(f"Round-trip conversion result: {result['status']}")
        if result['round_trip_success']:
            print(f"✅ Round-trip conversion successful!")
            print(f"   Original: {result['original_file']}")
            print(f"   Reconstructed: {result['reconstructed_file']}")
        else:
            print(f"❌ Round-trip conversion failed!")
            
    elif args.command == 'extract-batch':
        result = batch_extract(Path(args.input), Path(args.output), args.formats, args.mode)
        if result:
            successful = sum(1 for r in result.values() if r['status'] == 'completed')
            total = len(result)
            print(f"Batch extraction result: {successful}/{total} files processed successfully")
            
    elif args.command == 'generate-batch':
        result = batch_generate(Path(args.input), Path(args.output))
        if result:
            successful = sum(1 for r in result.values() if r['status'] == 'completed')
            total = len(result)
            print(f"Batch generation result: {successful}/{total} files processed successfully")

if __name__ == "__main__":
    main() 