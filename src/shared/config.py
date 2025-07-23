"""
Configuration for AASX processing modules.
"""

from pathlib import Path

# Path to the aas-processor executable
AAS_PROCESSOR_PATH = Path(__file__).parent.parent.parent / "aas-processor" / "bin" / "Release" / "net8.0" / "AasProcessor.exe" 