#!/usr/bin/env python3
"""
Analyze AASX file contents to identify all embedded files.
"""

import zipfile
import json
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_aasx_contents(aasx_file_path: str):
    """
    Analyze all contents of an AASX file.
    """
    logger.info(f"Analyzing AASX contents: {aasx_file_path}")
    
    try:
        with zipfile.ZipFile(aasx_file_path, 'r') as zip_file:
            # Get all files
            file_list = zip_file.namelist()
            
            logger.info(f"Total files in AASX: {len(file_list)}")
            
            # Categorize files
            categories = {
                'xml_files': [],
                'json_files': [],
                'image_files': [],
                'document_files': [],
                'relationship_files': [],
                'content_type_files': [],
                'other_files': []
            }
            
            for filename in file_list:
                ext = Path(filename).suffix.lower()
                
                if filename.endswith('.xml'):
                    if filename.startswith('[Content_Types]'):
                        categories['content_type_files'].append(filename)
                    elif '_rels' in filename or filename.endswith('.rels'):
                        categories['relationship_files'].append(filename)
                    else:
                        categories['xml_files'].append(filename)
                elif filename.endswith('.json'):
                    categories['json_files'].append(filename)
                elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
                    categories['image_files'].append(filename)
                elif ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf']:
                    categories['document_files'].append(filename)
                else:
                    categories['other_files'].append(filename)
            
            # Log results
            logger.info("=== AASX CONTENTS ANALYSIS ===")
            for category, files in categories.items():
                if files:
                    logger.info(f"{category.upper()}: {len(files)} files")
                    for file in files:
                        try:
                            file_info = zip_file.getinfo(file)
                            logger.info(f"  - {file} ({file_info.file_size} bytes)")
                        except:
                            logger.info(f"  - {file}")
            
            # Extract and analyze specific files
            logger.info("\n=== DETAILED ANALYSIS ===")
            
            # Analyze XML files
            for xml_file in categories['xml_files']:
                logger.info(f"\nAnalyzing XML: {xml_file}")
                try:
                    with zip_file.open(xml_file) as f:
                        content = f.read().decode('utf-8')
                        logger.info(f"  Size: {len(content)} characters")
                        logger.info(f"  First 200 chars: {content[:200]}...")
                except Exception as e:
                    logger.error(f"  Error reading {xml_file}: {e}")
            
            # Analyze image files
            for img_file in categories['image_files']:
                logger.info(f"\nAnalyzing Image: {img_file}")
                try:
                    file_info = zip_file.getinfo(img_file)
                    logger.info(f"  Size: {file_info.file_size} bytes")
                    logger.info(f"  Compression: {file_info.compress_type}")
                except Exception as e:
                    logger.error(f"  Error analyzing {img_file}: {e}")
            
            # Analyze document files
            for doc_file in categories['document_files']:
                logger.info(f"\nAnalyzing Document: {doc_file}")
                try:
                    file_info = zip_file.getinfo(doc_file)
                    logger.info(f"  Size: {file_info.file_size} bytes")
                    logger.info(f"  Compression: {file_info.compress_type}")
                except Exception as e:
                    logger.error(f"  Error analyzing {doc_file}: {e}")
            
            # Save detailed analysis
            analysis_result = {
                'timestamp': datetime.now().isoformat(),
                'aasx_file': aasx_file_path,
                'total_files': len(file_list),
                'categories': categories,
                'file_details': {}
            }
            
            # Add file details
            for filename in file_list:
                try:
                    file_info = zip_file.getinfo(filename)
                    analysis_result['file_details'][filename] = {
                        'size': file_info.file_size,
                        'compressed_size': file_info.compress_size,
                        'compression_type': file_info.compress_type,
                        'date_time': file_info.date_time
                    }
                except Exception as e:
                    analysis_result['file_details'][filename] = {'error': str(e)}
            
            # Save to JSON
            output_file = f"aasx_contents_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"\nDetailed analysis saved to: {output_file}")
            
            return analysis_result
            
    except Exception as e:
        logger.error(f"Error analyzing AASX file: {e}")
        raise

def main():
    """
    Main function to analyze AASX files.
    """
    # Find AASX files
    # Find AASX files
    aasx_dir = Path("aasx-generator/data/samples_aasx/servodcmotor")
    if not aasx_dir.exists():
        logger.error(f"AASX directory not found: {aasx_dir}")
        return
    
    aasx_files = list(aasx_dir.rglob("*.aasx"))
    
    if not aasx_files:
        logger.error("No AASX files found in current directory or subdirectories")
        return
    
    logger.info(f"Found {len(aasx_files)} AASX files")
    
    # Analyze first file
    first_file = str(aasx_files[0])
    logger.info(f"Analyzing first file: {first_file}")
    
    result = analyze_aasx_contents(first_file)
    
    logger.info("=== ANALYSIS COMPLETE ===")
    logger.info("Check the generated JSON file for detailed results")

if __name__ == "__main__":
    main() 