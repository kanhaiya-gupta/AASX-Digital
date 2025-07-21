#!/usr/bin/env python3
"""
Debug XML Content from AASX Files
=================================

This script extracts and analyzes the actual XML content from AASX files
to understand why the .NET processor is not finding the expected elements.
"""

import zipfile
import xml.etree.ElementTree as ET
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_xml_from_aasx(aasx_file_path: str):
    """
    Extract XML files from AASX and analyze their structure.
    """
    logger.info(f"Extracting XML from: {aasx_file_path}")
    
    xml_files = []
    
    try:
        with zipfile.ZipFile(aasx_file_path, 'r') as zip_file:
            # List all files in the AASX
            file_list = zip_file.namelist()
            logger.info(f"Files in AASX: {file_list}")
            
            # Extract XML files
            for file_name in file_list:
                if file_name.endswith('.xml') or file_name.endswith('.aas.xml'):
                    logger.info(f"Found XML file: {file_name}")
                    
                    # Read XML content
                    xml_content = zip_file.read(file_name).decode('utf-8')
                    xml_files.append({
                        'filename': file_name,
                        'content': xml_content
                    })
                    
                    # Parse and analyze XML structure
                    analyze_xml_structure(file_name, xml_content)
    
    except Exception as e:
        logger.error(f"Error extracting from AASX: {e}")
    
    return xml_files

def analyze_xml_structure(filename: str, xml_content: str):
    """
    Analyze the structure of an XML file to understand element names and structure.
    """
    logger.info(f"\n=== XML STRUCTURE ANALYSIS: {filename} ===")
    
    try:
        # Parse XML
        root = ET.fromstring(xml_content)
        
        # Get namespace information
        logger.info("XML Namespace Analysis:")
        logger.info(f"Root tag: {root.tag}")
        
        # Extract namespace from root tag if present
        if '}' in root.tag:
            namespace = root.tag.split('}')[0].strip('{')
            logger.info(f"Root namespace: {namespace}")
        
        # Show all attributes of root element
        if root.attrib:
            logger.info("Root attributes:")
            for key, value in root.attrib.items():
                logger.info(f"  {key} = {value}")
        
        # Show immediate children
        logger.info("Root children:")
        for child in root:
            logger.info(f"  - {child.tag}")
            if child.attrib:
                logger.info(f"    Attributes: {child.attrib}")
            if child.text and child.text.strip():
                logger.info(f"    Text: {child.text.strip()}")
        
        # Search for AAS elements without namespace assumptions
        logger.info("\nSearching for AAS elements (all namespaces):")
        
        # Get all elements recursively
        all_elements = root.findall(".//*")
        logger.info(f"Total elements found: {len(all_elements)}")
        
        # Look for elements that might be AAS-related
        aas_keywords = ['asset', 'submodel', 'identification', 'idShort', 'id', 'description', 'kind', 'category', 'aas']
        found_elements = []
        
        for elem in all_elements:
            elem_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            if any(keyword in elem_name.lower() for keyword in aas_keywords):
                found_elements.append(elem)
        
        logger.info(f"Found {len(found_elements)} potential AAS elements:")
        for elem in found_elements[:10]:  # Show first 10
            elem_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            logger.info(f"  - {elem.tag} (local name: {elem_name})")
            if elem.text and elem.text.strip():
                logger.info(f"    Text: {elem.text.strip()}")
            if elem.attrib:
                logger.info(f"    Attributes: {elem.attrib}")
        
        # Save the XML content for manual inspection
        output_file = f"debug_xml_{filename.replace('/', '_').replace('.', '_')}.xml"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        logger.info(f"XML content saved to: {output_file}")
        
        # Also save a simplified view
        simplified_file = f"debug_xml_simplified_{filename.replace('/', '_').replace('.', '_')}.txt"
        with open(simplified_file, 'w', encoding='utf-8') as f:
            f.write("XML Structure Summary:\n")
            f.write(f"Root: {root.tag}\n")
            f.write("Children:\n")
            for child in root:
                f.write(f"  {child.tag}\n")
                if child.attrib:
                    f.write(f"    Attrs: {child.attrib}\n")
                if child.text and child.text.strip():
                    f.write(f"    Text: {child.text.strip()}\n")
        logger.info(f"Simplified structure saved to: {simplified_file}")
        
    except Exception as e:
        logger.error(f"Error analyzing XML structure: {e}")
        # Show raw content for debugging
        logger.info("Raw XML content (first 500 chars):")
        logger.info(xml_content[:500])

def main():
    """
    Main function to analyze AASX files.
    """
    # Find AASX files
    aasx_dir = Path("aasx-generator/data/samples_aasx/servodcmotor")
    if not aasx_dir.exists():
        logger.error(f"AASX directory not found: {aasx_dir}")
        return
    
    aasx_files = list(aasx_dir.glob("*.aasx"))
    if not aasx_files:
        logger.error("No AASX files found")
        return
    
    logger.info(f"Found {len(aasx_files)} AASX files")
    
    # Analyze first file
    first_file = aasx_files[0]
    logger.info(f"Analyzing: {first_file}")
    
    xml_files = extract_xml_from_aasx(str(first_file))
    
    logger.info(f"\n=== SUMMARY ===")
    logger.info(f"Extracted {len(xml_files)} XML files")
    for xml_file in xml_files:
        logger.info(f"  - {xml_file['filename']}")

if __name__ == "__main__":
    main() 