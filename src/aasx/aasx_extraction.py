import argparse
import subprocess
from pathlib import Path
import sys
from src.shared.utils import ensure_dir, log_info, log_error
from src.shared.config import AAS_PROCESSOR_PATH

def extract_aasx(aasx_path: Path, output_dir: Path, formats: list = None):
    """
    Extract structured data and documents from a single AASX file using aas-processor.
    
    Args:
        aasx_path: Path to the AASX file
        output_dir: Output directory for extracted data
        formats: List of formats to export ['json', 'graph', 'rdf', 'yaml'] (default: all)
    """
    if formats is None:
        formats = ['json', 'graph', 'rdf', 'yaml']
    
    ensure_dir(output_dir)
    file_stem = aasx_path.stem
    
    results = {}
    
    # Standard JSON extraction
    if 'json' in formats:
        json_output = output_dir / f"{file_stem}.json"
        cmd = [
            str(AAS_PROCESSOR_PATH),
            "process",
            str(aasx_path),
            str(json_output)
        ]
        log_info(f"Extracting JSON from {aasx_path} to {json_output}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            log_error(f"JSON extraction failed for {aasx_path}: {result.stderr}")
            results['json'] = {'status': 'failed', 'error': result.stderr}
        else:
            log_info(f"JSON extraction succeeded for {aasx_path}")
            results['json'] = {'status': 'completed', 'output': str(json_output)}
    
    # Graph export
    if 'graph' in formats:
        graph_output = output_dir / f"{file_stem}_graph.json"
        cmd = [
            str(AAS_PROCESSOR_PATH),
            "export-graph",
            str(aasx_path),
            str(graph_output)
        ]
        log_info(f"Exporting graph from {aasx_path} to {graph_output}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            log_error(f"Graph export failed for {aasx_path}: {result.stderr}")
            results['graph'] = {'status': 'failed', 'error': result.stderr}
        else:
            log_info(f"Graph export succeeded for {aasx_path}")
            results['graph'] = {'status': 'completed', 'output': str(graph_output)}
    
    # RDF/Turtle export
    if 'rdf' in formats:
        rdf_output = output_dir / f"{file_stem}.ttl"
        cmd = [
            str(AAS_PROCESSOR_PATH),
            "export-rdf",
            str(aasx_path),
            str(rdf_output)
        ]
        log_info(f"Exporting RDF from {aasx_path} to {rdf_output}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            log_error(f"RDF export failed for {aasx_path}: {result.stderr}")
            results['rdf'] = {'status': 'failed', 'error': result.stderr}
        else:
            log_info(f"RDF export succeeded for {aasx_path}")
            results['rdf'] = {'status': 'completed', 'output': str(rdf_output)}
    
    # YAML export (if supported)
    if 'yaml' in formats:
        yaml_output = output_dir / f"{file_stem}.yaml"
        cmd = [
            str(AAS_PROCESSOR_PATH),
            "export-yaml",
            str(aasx_path),
            str(yaml_output)
        ]
        log_info(f"Exporting YAML from {aasx_path} to {yaml_output}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            log_error(f"YAML export failed for {aasx_path}: {result.stderr}")
            results['yaml'] = {'status': 'failed', 'error': result.stderr}
        else:
            log_info(f"YAML export succeeded for {aasx_path}")
            results['yaml'] = {'status': 'completed', 'output': str(yaml_output)}
    
    return results


def batch_extract(input_path: Path, output_dir: Path, formats: list = None):
    """
    Extract from a single file or all AASX files in a directory.
    
    Args:
        input_path: Path to AASX file or directory
        output_dir: Output directory
        formats: List of formats to export ['json', 'graph', 'rdf', 'yaml'] (default: all)
    """
    if formats is None:
        formats = ['json', 'graph', 'rdf', 'yaml']
    
    if input_path.is_file() and input_path.suffix.lower() == ".aasx":
        return extract_aasx(input_path, output_dir, formats)
    elif input_path.is_dir():
        results = {}
        for aasx_file in input_path.glob("*.aasx"):
            file_output_dir = output_dir / aasx_file.stem
            results[aasx_file.name] = extract_aasx(aasx_file, file_output_dir, formats)
        return results
    else:
        log_error(f"Input {input_path} is not a valid AASX file or directory.")
        return None


def main():
    parser = argparse.ArgumentParser(description="Extract structured data and documents from AASX files.")
    parser.add_argument("input", type=str, help="AASX file or directory containing AASX files")
    parser.add_argument("output", type=str, help="Output directory")
    parser.add_argument("--formats", nargs="+", choices=['json', 'graph', 'rdf', 'yaml'], 
                       default=['json', 'graph', 'rdf', 'yaml'], 
                       help="Formats to export (default: all)")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)
    batch_extract(input_path, output_dir, args.formats)

if __name__ == "__main__":
    main() 