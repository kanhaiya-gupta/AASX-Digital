#!/usr/bin/env python3
"""
Script to analyze AAS XML content and compare with structured JSON data
to identify any additional information that might not be captured.
"""

import json
import xml.etree.ElementTree as ET
import re
from pathlib import Path
from typing import Dict, List, Set, Any
import argparse

def extract_xml_content_from_json(json_file_path: str) -> Dict[str, str]:
    """Extract XML content from the structured JSON file."""
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    xml_content = {}
    if 'aasXmlContent' in data:
        for filename, content_info in data['aasXmlContent'].items():
            if 'content' in content_info:
                xml_content[filename] = content_info['content']
    
    return xml_content

def parse_xml_content(xml_content: str) -> Dict[str, Any]:
    """Parse XML content and extract all elements, attributes, and text."""
    try:
        # Decode HTML entities
        xml_content = xml_content.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        
        root = ET.fromstring(xml_content)
        
        def extract_element_info(element, path=""):
            info = {
                'tag': element.tag,
                'path': path,
                'attributes': dict(element.attrib),
                'text': element.text.strip() if element.text and element.text.strip() else None,
                'children': []
            }
            
            for child in element:
                child_info = extract_element_info(child, f"{path}/{child.tag}" if path else child.tag)
                info['children'].append(child_info)
            
            return info
        
        return extract_element_info(root)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return {}

def extract_structured_data_info(json_file_path: str) -> Dict[str, Any]:
    """Extract information from structured data for comparison."""
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    def flatten_dict(d, parent_key='', sep='.'):
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        items.extend(flatten_dict(item, f"{new_key}[{i}]", sep=sep).items())
                    else:
                        items.append((f"{new_key}[{i}]", item))
            else:
                items.append((new_key, v))
        return dict(items)
    
    return flatten_dict(data)

def analyze_xml_elements(xml_info: Dict[str, Any], path="") -> List[Dict[str, Any]]:
    """Recursively analyze XML elements and extract all information."""
    elements = []
    
    element_info = {
        'path': path,
        'tag': xml_info.get('tag', ''),
        'attributes': xml_info.get('attributes', {}),
        'text': xml_info.get('text'),
        'full_path': f"{path}.{xml_info.get('tag', '')}" if path else xml_info.get('tag', '')
    }
    elements.append(element_info)
    
    for child in xml_info.get('children', []):
        child_path = f"{path}.{xml_info.get('tag', '')}" if path else xml_info.get('tag', '')
        elements.extend(analyze_xml_elements(child, child_path))
    
    return elements

def compare_xml_with_structured(xml_elements: List[Dict], structured_data: Dict[str, Any]) -> Dict[str, Any]:
    """Compare XML elements with structured data to find differences."""
    comparison = {
        'xml_only_elements': [],
        'xml_only_attributes': [],
        'xml_only_text_values': [],
        'structured_only_keys': [],
        'matching_elements': [],
        'summary': {}
    }
    
    # Extract all structured data keys
    structured_keys = set(structured_data.keys())
    
    # Analyze XML elements
    xml_paths = set()
    xml_attributes = set()
    xml_text_values = set()
    
    for element in xml_elements:
        path = element['full_path']
        xml_paths.add(path)
        
        # Check attributes
        for attr_name, attr_value in element['attributes'].items():
            xml_attributes.add(f"{path}.@{attr_name}")
        
        # Check text content
        if element['text']:
            xml_text_values.add(f"{path}: {element['text']}")
    
    # Find XML-only elements
    for element in xml_elements:
        path = element['full_path']
        if not any(key.endswith(path.split('.')[-1]) for key in structured_keys):
            comparison['xml_only_elements'].append({
                'path': path,
                'tag': element['tag'],
                'attributes': element['attributes'],
                'text': element['text']
            })
    
    # Find XML-only attributes
    for attr_path in xml_attributes:
        if not any(attr_path.split('.')[-1] in key for key in structured_keys):
            comparison['xml_only_attributes'].append(attr_path)
    
    # Find XML-only text values
    for text_value in xml_text_values:
        path_part = text_value.split(':')[0]
        if not any(path_part.split('.')[-1] in key for key in structured_keys):
            comparison['xml_only_text_values'].append(text_value)
    
    # Find structured-only keys
    for key in structured_keys:
        if not any(key.split('.')[-1] in path for path in xml_paths):
            comparison['structured_only_keys'].append(key)
    
    # Summary
    comparison['summary'] = {
        'total_xml_elements': len(xml_elements),
        'total_xml_attributes': len(xml_attributes),
        'total_xml_text_values': len(xml_text_values),
        'total_structured_keys': len(structured_keys),
        'xml_only_elements_count': len(comparison['xml_only_elements']),
        'xml_only_attributes_count': len(comparison['xml_only_attributes']),
        'xml_only_text_values_count': len(comparison['xml_only_text_values']),
        'structured_only_keys_count': len(comparison['structured_only_keys'])
    }
    
    return comparison

def main():
    parser = argparse.ArgumentParser(description='Analyze AAS XML vs Structured Data')
    parser.add_argument('json_file', help='Path to the structured JSON file')
    parser.add_argument('--output', '-o', help='Output file for detailed analysis')
    args = parser.parse_args()
    
    print("🔍 Analyzing AAS XML vs Structured Data...")
    print(f"📁 Input file: {args.json_file}")
    
    # Extract XML content from JSON
    print("\n📖 Extracting XML content from JSON...")
    xml_content_dict = extract_xml_content_from_json(args.json_file)
    
    if not xml_content_dict:
        print("❌ No XML content found in the JSON file!")
        return
    
    print(f"✅ Found {len(xml_content_dict)} XML files in JSON")
    
    # Extract structured data
    print("\n📊 Extracting structured data...")
    structured_data = extract_structured_data_info(args.json_file)
    print(f"✅ Found {len(structured_data)} structured data keys")
    
    # Analyze each XML file
    all_comparisons = {}
    
    for filename, xml_content in xml_content_dict.items():
        print(f"\n🔍 Analyzing {filename}...")
        
        # Parse XML
        xml_info = parse_xml_content(xml_content)
        if not xml_info:
            print(f"❌ Failed to parse XML for {filename}")
            continue
        
        # Analyze XML elements
        xml_elements = analyze_xml_elements(xml_info)
        print(f"✅ Found {len(xml_elements)} XML elements")
        
        # Compare with structured data
        comparison = compare_xml_with_structured(xml_elements, structured_data)
        all_comparisons[filename] = comparison
        
        # Print summary
        summary = comparison['summary']
        print(f"📈 Summary for {filename}:")
        print(f"   XML Elements: {summary['total_xml_elements']}")
        print(f"   XML Attributes: {summary['total_xml_attributes']}")
        print(f"   XML Text Values: {summary['total_xml_text_values']}")
        print(f"   Structured Keys: {summary['total_structured_keys']}")
        print(f"   XML-only Elements: {summary['xml_only_elements_count']}")
        print(f"   XML-only Attributes: {summary['xml_only_attributes_count']}")
        print(f"   XML-only Text Values: {summary['xml_only_text_values_count']}")
        print(f"   Structured-only Keys: {summary['structured_only_keys_count']}")
    
    # Overall analysis
    print("\n" + "="*60)
    print("🎯 OVERALL ANALYSIS")
    print("="*60)
    
    total_xml_only_elements = sum(c['summary']['xml_only_elements_count'] for c in all_comparisons.values())
    total_xml_only_attributes = sum(c['summary']['xml_only_attributes_count'] for c in all_comparisons.values())
    total_xml_only_text_values = sum(c['summary']['xml_only_text_values_count'] for c in all_comparisons.values())
    
    print(f"📊 Total XML-only elements across all files: {total_xml_only_elements}")
    print(f"📊 Total XML-only attributes across all files: {total_xml_only_attributes}")
    print(f"📊 Total XML-only text values across all files: {total_xml_only_text_values}")
    
    if total_xml_only_elements == 0 and total_xml_only_attributes == 0 and total_xml_only_text_values == 0:
        print("\n✅ CONCLUSION: All XML information is captured in structured data!")
        print("   This means external data → AASX conversion is fully possible.")
    else:
        print("\n⚠️  CONCLUSION: Some XML information is NOT captured in structured data!")
        print("   This might limit external data → AASX conversion.")
    
    # Save detailed analysis if requested
    if args.output:
        print(f"\n💾 Saving detailed analysis to {args.output}...")
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(all_comparisons, f, indent=2, ensure_ascii=False)
        print("✅ Detailed analysis saved!")
    
    # Show examples of XML-only content
    print("\n🔍 EXAMPLES OF XML-ONLY CONTENT:")
    print("-" * 40)
    
    for filename, comparison in all_comparisons.items():
        if comparison['xml_only_elements']:
            print(f"\n📄 {filename} - XML-only elements:")
            for element in comparison['xml_only_elements'][:5]:  # Show first 5
                print(f"   {element['path']}: {element['tag']}")
                if element['attributes']:
                    print(f"     Attributes: {element['attributes']}")
                if element['text']:
                    print(f"     Text: {element['text'][:100]}...")
        
        if comparison['xml_only_attributes']:
            print(f"\n📄 {filename} - XML-only attributes:")
            for attr in comparison['xml_only_attributes'][:5]:  # Show first 5
                print(f"   {attr}")
        
        if comparison['xml_only_text_values']:
            print(f"\n📄 {filename} - XML-only text values:")
            for text in comparison['xml_only_text_values'][:5]:  # Show first 5
                print(f"   {text}")

if __name__ == "__main__":
    main() 