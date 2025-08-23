"""
AASX Format Conversion Utilities

Utility functions for converting between different AASX formats.
"""

import json
import xml.etree.ElementTree as ET
import yaml
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
import logging

logger = logging.getLogger(__name__)


class FormatConverter:
    """Converter for different AASX formats."""
    
    def __init__(self):
        """Initialize the format converter."""
        self.supported_formats = {
            'input': ['.aasx', '.xml', '.json', '.yaml', '.yml'],
            'output': ['.aasx', '.xml', '.json', '.yaml', '.yml', '.ttl']
        }
    
    def convert_format(self, input_path: str, output_path: str, 
                      input_format: Optional[str] = None, 
                      output_format: Optional[str] = None) -> bool:
        """
        Convert AASX file from one format to another.
        
        Args:
            input_path: Path to input file
            output_path: Path to output file
            input_format: Input format (auto-detected if None)
            output_format: Output format (auto-detected if None)
            
        Returns:
            bool: True if conversion successful, False otherwise
        """
        try:
            # Auto-detect formats if not specified
            if input_format is None:
                input_format = self._detect_format(input_path)
            
            if output_format is None:
                output_format = self._detect_format(output_path)
            
            # Validate formats
            if not self._is_supported_format(input_format, 'input'):
                raise ValueError(f"Unsupported input format: {input_format}")
            
            if not self._is_supported_format(output_format, 'output'):
                raise ValueError(f"Unsupported output format: {output_format}")
            
            # Load input data
            input_data = self._load_format(input_path, input_format)
            
            # Convert to output format
            self._save_format(output_path, input_data, output_format)
            
            logger.info(f"Successfully converted {input_path} ({input_format}) to {output_path} ({output_format})")
            return True
            
        except Exception as e:
            logger.error(f"Format conversion failed: {str(e)}")
            return False
    
    def _detect_format(self, file_path: str) -> str:
        """Auto-detect file format."""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext in self.supported_formats['input']:
            return file_ext
        
        # Try to detect by content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1024).strip()
                
                if content.startswith('{'):
                    return '.json'
                elif content.startswith('<'):
                    return '.xml'
                elif content.startswith('---') or ':' in content:
                    return '.yaml'
                else:
                    return '.aasx'  # Default assumption
                    
        except Exception:
            return '.aasx'  # Default assumption
    
    def _is_supported_format(self, format_ext: str, format_type: str) -> bool:
        """Check if format is supported."""
        return format_ext in self.supported_formats[format_type]
    
    def _load_format(self, file_path: str, format_ext: str) -> Dict[str, Any]:
        """Load data from a specific format."""
        if format_ext == '.aasx':
            return self._load_aasx(file_path)
        elif format_ext == '.xml':
            return self._load_xml(file_path)
        elif format_ext == '.json':
            return self._load_json(file_path)
        elif format_ext in ['.yaml', '.yml']:
            return self._load_yaml(file_path)
        else:
            raise ValueError(f"Unsupported input format: {format_ext}")
    
    def _save_format(self, file_path: str, data: Dict[str, Any], format_ext: str) -> None:
        """Save data to a specific format."""
        if format_ext == '.aasx':
            self._save_aasx(file_path, data)
        elif format_ext == '.xml':
            self._save_xml(file_path, data)
        elif format_ext == '.json':
            self._save_json(file_path, data)
        elif format_ext in ['.yaml', '.yml']:
            self._save_yaml(file_path, data)
        elif format_ext == '.ttl':
            self._save_ttl(file_path, data)
        else:
            raise ValueError(f"Unsupported output format: {format_ext}")
    
    def _load_aasx(self, file_path: str) -> Dict[str, Any]:
        """Load data from AASX file."""
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # Extract AASX origin
                origin_data = {}
                if 'aasx/aasx-origin' in zip_file.namelist():
                    origin_content = zip_file.read('aasx/aasx-origin').decode('utf-8')
                    origin_data = self._parse_xml_content(origin_content)
                
                # Extract AAS content
                aas_data = {}
                aas_files = [f for f in zip_file.namelist() if f.endswith('.xml') and 'aas/' in f]
                
                for aas_file in aas_files:
                    try:
                        xml_content = zip_file.read(aas_file).decode('utf-8')
                        file_data = self._parse_xml_content(xml_content)
                        aas_data[aas_file] = file_data
                    except Exception as e:
                        logger.warning(f"Failed to parse AAS file {aas_file}: {str(e)}")
                
                return {
                    'format': 'aasx',
                    'origin': origin_data,
                    'aas_content': aas_data,
                    'metadata': {
                        'total_files': len(zip_file.namelist()),
                        'aas_files': len(aas_files),
                        'origin_file': 'aasx/aasx-origin' in zip_file.namelist()
                    }
                }
                
        except Exception as e:
            raise ValueError(f"Failed to load AASX file: {str(e)}")
    
    def _load_xml(self, file_path: str) -> Dict[str, Any]:
        """Load data from XML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self._parse_xml_content(content)
            
        except Exception as e:
            raise ValueError(f"Failed to load XML file: {str(e)}")
    
    def _load_json(self, file_path: str) -> Dict[str, Any]:
        """Load data from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            raise ValueError(f"Failed to load JSON file: {str(e)}")
    
    def _load_yaml(self, file_path: str) -> Dict[str, Any]:
        """Load data from YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
                
        except Exception as e:
            raise ValueError(f"Failed to load YAML file: {str(e)}")
    
    def _parse_xml_content(self, content: str) -> Dict[str, Any]:
        """Parse XML content to dictionary."""
        try:
            root = ET.fromstring(content)
            return self._xml_to_dict(root)
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML content: {str(e)}")
    
    def _xml_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """Convert XML element to dictionary."""
        result = {}
        
        # Add attributes
        if element.attrib:
            result['@attributes'] = dict(element.attrib)
        
        # Add text content
        if element.text and element.text.strip():
            result['@text'] = element.text.strip()
        
        # Add child elements
        for child in element:
            child_data = self._xml_to_dict(child)
            child_tag = child.tag
            
            # Handle namespaces
            if '}' in child_tag:
                child_tag = child_tag.split('}')[-1]
            
            if child_tag in result:
                # Convert to list if multiple elements with same tag
                if not isinstance(result[child_tag], list):
                    result[child_tag] = [result[child_tag]]
                result[child_tag].append(child_data)
            else:
                result[child_tag] = child_data
        
        return result
    
    def _save_aasx(self, file_path: str, data: Dict[str, Any]) -> None:
        """Save data to AASX file."""
        try:
            with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Create AASX origin file
                if 'origin' in data:
                    origin_xml = self._dict_to_xml(data['origin'], 'aasx:origin')
                    zip_file.writestr('aasx/aasx-origin', origin_xml)
                
                # Create AAS content files
                if 'aas_content' in data:
                    for file_name, content in data['aas_content'].items():
                        if isinstance(content, dict):
                            xml_content = self._dict_to_xml(content, 'aas:root')
                            zip_file.writestr(file_name, xml_content)
                
                # Create metadata file
                metadata = {
                    'format': 'aasx',
                    'version': '1.0',
                    'created': str(datetime.now()),
                    'total_files': len(data.get('aas_content', {}))
                }
                zip_file.writestr('metadata.json', json.dumps(metadata, indent=2))
                
        except Exception as e:
            raise ValueError(f"Failed to save AASX file: {str(e)}")
    
    def _save_xml(self, file_path: str, data: Dict[str, Any]) -> None:
        """Save data to XML file."""
        try:
            xml_content = self._dict_to_xml(data, 'root')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
                
        except Exception as e:
            raise ValueError(f"Failed to save XML file: {str(e)}")
    
    def _save_json(self, file_path: str, data: Dict[str, Any]) -> None:
        """Save data to JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            raise ValueError(f"Failed to save JSON file: {str(e)}")
    
    def _save_yaml(self, file_path: str, data: Dict[str, Any]) -> None:
        """Save data to YAML file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
                
        except Exception as e:
            raise ValueError(f"Failed to save YAML file: {str(e)}")
    
    def _save_ttl(self, file_path: str, data: Dict[str, Any]) -> None:
        """Save data to TTL (Turtle) file."""
        try:
            ttl_content = self._dict_to_ttl(data)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(ttl_content)
                
        except Exception as e:
            raise ValueError(f"Failed to save TTL file: {str(e)}")
    
    def _dict_to_xml(self, data: Dict[str, Any], root_tag: str) -> str:
        """Convert dictionary to XML string."""
        root = ET.Element(root_tag)
        self._dict_to_xml_element(data, root)
        
        # Pretty print XML
        ET.indent(root, space="  ")
        return ET.tostring(root, encoding='unicode')
    
    def _dict_to_xml_element(self, data: Any, parent: ET.Element) -> None:
        """Convert dictionary to XML element recursively."""
        if isinstance(data, dict):
            for key, value in data.items():
                if key == '@attributes':
                    # Add attributes
                    for attr_key, attr_value in value.items():
                        parent.set(attr_key, str(attr_value))
                elif key == '@text':
                    # Add text content
                    parent.text = str(value)
                else:
                    # Create child element
                    child = ET.SubElement(parent, key)
                    self._dict_to_xml_element(value, child)
        elif isinstance(data, list):
            for item in data:
                self._dict_to_xml_element(item, parent)
        else:
            parent.text = str(data)
    
    def _dict_to_ttl(self, data: Dict[str, Any]) -> str:
        """Convert dictionary to TTL format."""
        lines = ['@prefix aas: <http://www.admin-shell.io/aas/3/0#> .', '']
        
        def process_dict(d: Dict[str, Any], prefix: str = '') -> None:
            for key, value in d.items():
                if key.startswith('@'):
                    continue
                
                if isinstance(value, dict):
                    lines.append(f'{prefix}aas:{key} [')
                    process_dict(value, prefix + '  ')
                    lines.append(f'{prefix}] .')
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            lines.append(f'{prefix}aas:{key} [')
                            process_dict(item, prefix + '  ')
                            lines.append(f'{prefix}] .')
                        else:
                            lines.append(f'{prefix}aas:{key} "{item}" .')
                else:
                    if isinstance(value, str):
                        lines.append(f'{prefix}aas:{key} "{value}" .')
                    else:
                        lines.append(f'{prefix}aas:{key} {value} .')
        
        process_dict(data)
        return '\n'.join(lines)


# Utility functions
def convert_aasx_to_json(aasx_path: str, json_path: str) -> bool:
    """Convert AASX file to JSON format."""
    converter = FormatConverter()
    return converter.convert_format(aasx_path, json_path, '.aasx', '.json')


def convert_aasx_to_xml(aasx_path: str, xml_path: str) -> bool:
    """Convert AASX file to XML format."""
    converter = FormatConverter()
    return converter.convert_format(aasx_path, xml_path, '.aasx', '.xml')


def convert_aasx_to_yaml(aasx_path: str, yaml_path: str) -> bool:
    """Convert AASX file to YAML format."""
    converter = FormatConverter()
    return converter.convert_format(aasx_path, yaml_path, '.aasx', '.yaml')


def convert_json_to_aasx(json_path: str, aasx_path: str) -> bool:
    """Convert JSON file to AASX format."""
    converter = FormatConverter()
    return converter.convert_format(json_path, aasx_path, '.json', '.aasx')


def convert_xml_to_aasx(xml_path: str, aasx_path: str) -> bool:
    """Convert XML file to AASX format."""
    converter = FormatConverter()
    return converter.convert_format(xml_path, aasx_path, '.xml', '.aasx')


def convert_yaml_to_aasx(yaml_path: str, aasx_path: str) -> bool:
    """Convert YAML file to AASX format."""
    converter = FormatConverter()
    return converter.convert_format(yaml_path, aasx_path, '.yaml', '.aasx')


def batch_convert_format(input_dir: str, output_dir: str, 
                        input_format: str, output_format: str) -> Dict[str, bool]:
    """
    Batch convert files from one format to another.
    
    Args:
        input_dir: Input directory path
        output_dir: Output directory path
        input_format: Input format extension
        output_format: Output format extension
        
    Returns:
        Dict[str, bool]: Mapping of input files to conversion success status
    """
    converter = FormatConverter()
    results = {}
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all files with input format
    input_files = list(input_path.glob(f"*{input_format}"))
    
    for input_file in input_files:
        output_file = output_path / f"{input_file.stem}{output_format}"
        
        try:
            success = converter.convert_format(
                str(input_file), 
                str(output_file), 
                input_format, 
                output_format
            )
            results[str(input_file)] = success
        except Exception as e:
            logger.error(f"Failed to convert {input_file}: {str(e)}")
            results[str(input_file)] = False
    
    return results


def validate_conversion(input_path: str, output_path: str, 
                       input_format: str, output_format: str) -> bool:
    """
    Validate that conversion was successful by checking output file.
    
    Args:
        input_path: Input file path
        output_path: Output file path
        input_format: Input format
        output_format: Output format
        
    Returns:
        bool: True if conversion appears successful, False otherwise
    """
    try:
        # Check if output file exists
        if not Path(output_path).exists():
            return False
        
        # Check file size (output should not be empty)
        if Path(output_path).stat().st_size == 0:
            return False
        
        # Basic format validation
        if output_format == '.json':
            with open(output_path, 'r') as f:
                json.load(f)
        elif output_format == '.xml':
            with open(output_path, 'r') as f:
                ET.parse(output_path)
        elif output_format == '.yaml':
            with open(output_path, 'r') as f:
                yaml.safe_load(f)
        elif output_format == '.aasx':
            with zipfile.ZipFile(output_path, 'r') as zip_file:
                if len(zip_file.namelist()) == 0:
                    return False
        
        return True
        
    except Exception:
        return False


# Import datetime for TTL conversion
from datetime import datetime
