import argparse
import subprocess
from pathlib import Path
import sys
from src.shared.utils import ensure_dir, log_info, log_error
from src.shared.config import AAS_PROCESSOR_PATH

def generate_aasx(structured_path: Path, output_dir: Path):
    """
    Generate/reconstruct an AASX file from structured data (JSON/YAML) and documents using aas-processor.
    """
    ensure_dir(output_dir)
    aasx_output = output_dir / f"{structured_path.stem}_reconstructed.aasx"
    cmd = [
        str(AAS_PROCESSOR_PATH),
        "generate-structured",
        str(structured_path),
        str(aasx_output)
    ]
    log_info(f"Generating AASX from {structured_path} to {aasx_output}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log_error(f"Generation failed for {structured_path}: {result.stderr}")
    else:
        log_info(f"Generation succeeded for {structured_path}")


def batch_generate(input_path: Path, output_dir: Path):
    """
    Generate AASX from a single structured file or all in a directory.
    """
    if input_path.is_file() and input_path.suffix.lower() in [".json", ".yaml", ".yml"]:
        generate_aasx(input_path, output_dir)
    elif input_path.is_dir():
        for structured_file in input_path.glob("*.json"):
            generate_aasx(structured_file, output_dir / structured_file.stem)
        for structured_file in input_path.glob("*.yaml"):
            generate_aasx(structured_file, output_dir / structured_file.stem)
        for structured_file in input_path.glob("*.yml"):
            generate_aasx(structured_file, output_dir / structured_file.stem)
    else:
        log_error(f"Input {input_path} is not a valid structured file or directory.")


def main():
    parser = argparse.ArgumentParser(description="Generate/reconstruct AASX files from structured data and documents.")
    parser.add_argument("input", type=str, help="Structured data file (JSON/YAML) or directory")
    parser.add_argument("output", type=str, help="Output directory")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)
    batch_generate(input_path, output_dir)

if __name__ == "__main__":
    main() 