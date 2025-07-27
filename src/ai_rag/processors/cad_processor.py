"""
CAD processor for technical drawings and CAD files.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from .base_processor import BaseDataProcessor


class CADProcessor(BaseDataProcessor):
    """Processor for CAD files and technical drawings."""
    
    def can_process(self, file_path: Path) -> bool:
        """Check if this processor can handle the given file."""
        return file_path.suffix.lower() in [
            # AutoCAD formats
            '.dwg', '.dxf', '.dwt', '.dws',
            # 3D CAD formats
            '.step', '.stp', '.iges', '.igs', '.stl', '.obj', '.ply', '.3ds', '.dae',
            # Other CAD formats
            '.sldprt', '.sldasm', '.prt', '.asm', '.ipt', '.iam', '.catpart', '.catproduct',
            '.par', '.psm', '.asm', '.x_t', '.x_b', '.sat', '.neu', '.neu',
            # Vector graphics (often used for technical drawings)
            '.svg', '.ai', '.eps', '.cdr',
            # Image formats that might contain technical drawings
            '.tiff', '.tif', '.bmp', '.png', '.jpg', '.jpeg'
        ]
    
    def process(self, project_id: str, file_info: Dict[str, Any], file_path: Path) -> Dict[str, Any]:
        """Process CAD file."""
        try:
            self.logger.info(f"Processing CAD file: {file_path}")
            
            # Extract text and metadata from CAD file
            cad_data = self._extract_cad_content(file_path)
            
            if not cad_data:
                return self._create_skipped_result(file_info, file_path, "No content extracted from CAD file")
            
            # Generate technical analysis
            technical_content = self._generate_technical_analysis(cad_data, file_path)
            
            if not technical_content:
                return self._create_skipped_result(file_info, file_path, "No meaningful technical content generated")
            
            self.logger.info(f"Generated technical content: {technical_content[:100]}...")
            
            # Generate embedding
            embedding = self._generate_embedding(technical_content, file_path)
            if not embedding:
                return self._create_error_result(file_info, file_path, "Failed to generate embedding for CAD file")
            
            # Get CAD metadata
            cad_metadata = self._get_cad_metadata(file_path, cad_data)
            
            # Prepare metadata
            metadata = {
                'project_id': project_id,
                'file_id': file_info.get('file_id'),
                'source_file': file_path.name,
                'content_type': 'cad',
                'content_preview': technical_content[:200] + "..." if len(technical_content) > 200 else technical_content,
                'file_path': str(file_path),
                'embedding_model': self.text_embedding_manager.get_model().get_model_info() if self.text_embedding_manager else None,
                'cad_type': file_path.suffix.lower(),
                'text_length': len(technical_content),
                'cad_metadata': cad_metadata
            }
            
            # Upload to vector database
            success = self._upload_to_vector_db(embedding, metadata, file_path)
            if not success:
                return self._create_error_result(file_info, file_path, "Failed to upload CAD file to vector database")
            
            # Save embedding locally
            vector_data = {
                'id': self.vector_db.generate_vector_id(project_id, file_path.name),
                'vector': embedding,
                'payload': metadata
            }
            self._save_embedding_locally(project_id, file_path, vector_data)
            
            return self._create_success_result(file_info, file_path, vector_data['id'])
            
        except Exception as e:
            self.logger.error(f"Exception processing CAD file {file_path}: {e}")
            return self._create_error_result(file_info, file_path, str(e))
    
    def _extract_cad_content(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract content from CAD file based on its type."""
        file_extension = file_path.suffix.lower()
        
        try:
            if file_extension in ['.dwg', '.dxf']:
                return self._extract_autocad_content(file_path)
            elif file_extension in ['.step', '.stp', '.iges', '.igs']:
                return self._extract_step_iges_content(file_path)
            elif file_extension in ['.stl', '.obj', '.ply']:
                return self._extract_3d_mesh_content(file_path)
            elif file_extension in ['.svg', '.ai', '.eps']:
                return self._extract_vector_content(file_path)
            elif file_extension in ['.tiff', '.tif', '.bmp', '.png', '.jpg', '.jpeg']:
                return self._extract_image_content(file_path)
            else:
                return self._extract_generic_cad_content(file_path)
                
        except Exception as e:
            self.logger.error(f"Failed to extract content from {file_path}: {e}")
            return None
    
    def _extract_autocad_content(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract content from AutoCAD files (DWG, DXF)."""
        try:
            # Try ezdxf for DXF files
            if file_path.suffix.lower() == '.dxf':
                try:
                    import ezdxf
                    doc = ezdxf.readfile(str(file_path))
                    
                    # Extract text entities
                    text_entities = []
                    for entity in doc.entitydb.values():
                        if hasattr(entity, 'dxftype'):
                            if entity.dxftype() == 'TEXT':
                                text_entities.append(entity.dxf.text)
                            elif entity.dxftype() == 'MTEXT':
                                text_entities.append(entity.dxf.text)
                            elif entity.dxftype() == 'DIMENSION':
                                if hasattr(entity.dxf, 'text'):
                                    text_entities.append(entity.dxf.text)
                    
                    # Extract layer information
                    layers = list(doc.layers)
                    
                    return {
                        'type': 'autocad_dxf',
                        'text_entities': text_entities,
                        'layers': [layer.dxf.name for layer in layers],
                        'total_entities': len(doc.entitydb),
                        'text_count': len(text_entities)
                    }
                    
                except ImportError:
                    self.logger.warning("ezdxf not available for DXF extraction")
                except Exception as e:
                    self.logger.warning(f"DXF extraction failed: {e}")
            
            # Try ODA File Converter or other tools for DWG files
            if file_path.suffix.lower() == '.dwg':
                # DWG files are binary and require specialized tools
                # For now, we'll extract basic metadata
                return {
                    'type': 'autocad_dwg',
                    'text_entities': [],
                    'layers': [],
                    'total_entities': 0,
                    'text_count': 0,
                    'note': 'DWG file - requires specialized tools for full extraction'
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"AutoCAD extraction failed for {file_path}: {e}")
            return None
    
    def _extract_step_iges_content(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract content from STEP/IGES files."""
        try:
            # Try OCE (OpenCascade) for STEP/IGES files
            try:
                from OCC.Core.STEPControl import STEPControl_Reader
                from OCC.Core.IFSelect import IFSelect_RetDone
                from OCC.Core.TopoDS import TopoDS_Shape
                from OCC.Core.BRep import BRep_Tool
                from OCC.Core.TopExp import TopExp_Explorer
                from OCC.Core.TopAbs import TopAbs_FACE, TopAbs_EDGE, TopAbs_VERTEX
                
                if file_path.suffix.lower() in ['.step', '.stp']:
                    reader = STEPControl_Reader()
                    status = reader.ReadFile(str(file_path))
                    
                    if status == IFSelect_RetDone:
                        reader.TransferRoots()
                        shape = reader.OneShape()
                        
                        # Extract geometric information
                        faces = []
                        edges = []
                        vertices = []
                        
                        explorer = TopExp_Explorer(shape, TopAbs_FACE)
                        while explorer.More():
                            face = explorer.Current()
                            faces.append(str(face))
                            explorer.Next()
                        
                        explorer = TopExp_Explorer(shape, TopAbs_EDGE)
                        while explorer.More():
                            edge = explorer.Current()
                            edges.append(str(edge))
                            explorer.Next()
                        
                        explorer = TopExp_Explorer(shape, TopAbs_VERTEX)
                        while explorer.More():
                            vertex = explorer.Current()
                            vertices.append(str(vertex))
                            explorer.Next()
                        
                        return {
                            'type': 'step',
                            'faces': len(faces),
                            'edges': len(edges),
                            'vertices': len(vertices),
                            'total_components': len(faces) + len(edges) + len(vertices)
                        }
                
            except ImportError:
                self.logger.warning("OCE (OpenCascade) not available for STEP/IGES extraction")
            except Exception as e:
                self.logger.warning(f"STEP/IGES extraction failed: {e}")
            
            # Fallback: extract as text file
            return self._extract_generic_cad_content(file_path)
            
        except Exception as e:
            self.logger.error(f"STEP/IGES extraction failed for {file_path}: {e}")
            return None
    
    def _extract_3d_mesh_content(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract content from 3D mesh files (STL, OBJ, PLY)."""
        try:
            # Try trimesh for mesh files
            try:
                import trimesh
                mesh = trimesh.load(str(file_path))
                
                return {
                    'type': '3d_mesh',
                    'vertices': len(mesh.vertices),
                    'faces': len(mesh.faces),
                    'bounds': mesh.bounds.tolist(),
                    'volume': float(mesh.volume) if hasattr(mesh, 'volume') else None,
                    'surface_area': float(mesh.area) if hasattr(mesh, 'area') else None,
                    'is_watertight': mesh.is_watertight if hasattr(mesh, 'is_watertight') else None
                }
                
            except ImportError:
                self.logger.warning("trimesh not available for 3D mesh extraction")
            except Exception as e:
                self.logger.warning(f"3D mesh extraction failed: {e}")
            
            # Fallback: extract as text file
            return self._extract_generic_cad_content(file_path)
            
        except Exception as e:
            self.logger.error(f"3D mesh extraction failed for {file_path}: {e}")
            return None
    
    def _extract_vector_content(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract content from vector graphics files."""
        try:
            if file_path.suffix.lower() == '.svg':
                # Extract text from SVG
                import xml.etree.ElementTree as ET
                
                tree = ET.parse(file_path)
                root = tree.getroot()
                
                # Extract text elements
                text_elements = []
                for elem in root.iter():
                    if elem.tag.endswith('text') or elem.tag.endswith('tspan'):
                        text = ''.join(elem.itertext()).strip()
                        if text:
                            text_elements.append(text)
                
                # Extract metadata
                width = root.get('width', 'unknown')
                height = root.get('height', 'unknown')
                viewbox = root.get('viewBox', 'unknown')
                
                return {
                    'type': 'vector_svg',
                    'text_elements': text_elements,
                    'dimensions': f"{width}x{height}",
                    'viewbox': viewbox,
                    'text_count': len(text_elements)
                }
            
            # For other vector formats, extract as text
            return self._extract_generic_cad_content(file_path)
            
        except Exception as e:
            self.logger.error(f"Vector extraction failed for {file_path}: {e}")
            return None
    
    def _extract_image_content(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract content from image files that might contain technical drawings."""
        try:
            from PIL import Image
            
            with Image.open(file_path) as img:
                # Basic image metadata
                metadata = {
                    'type': 'image_technical',
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height
                }
                
                # Try OCR for text extraction
                text_content = self._extract_text_from_image(file_path)
                if text_content:
                    metadata['text_content'] = text_content
                    metadata['text_length'] = len(text_content)
                
                return metadata
                
        except Exception as e:
            self.logger.error(f"Image extraction failed for {file_path}: {e}")
            return None
    
    def _extract_text_from_image(self, file_path: Path) -> Optional[str]:
        """Extract text from image using OCR (reuse from ImageProcessor)."""
        try:
            # Try Tesseract OCR
            try:
                import pytesseract
                from PIL import Image
                
                image = Image.open(file_path)
                text = pytesseract.image_to_string(image)
                return text.strip() if text.strip() else None
                
            except ImportError:
                self.logger.warning("pytesseract not available")
            except Exception as e:
                self.logger.warning(f"Tesseract OCR failed: {e}")
            
            return None
            
        except Exception as e:
            self.logger.error(f"Text extraction from image failed: {e}")
            return None
    
    def _extract_generic_cad_content(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract content from generic CAD files as text."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                return None
            
            return {
                'type': 'generic_cad',
                'content': content,
                'content_length': len(content),
                'lines': len(content.split('\n'))
            }
            
        except UnicodeDecodeError:
            # Try binary file analysis
            try:
                with open(file_path, 'rb') as f:
                    content = f.read(1024)  # Read first 1KB
                
                return {
                    'type': 'binary_cad',
                    'file_size': file_path.stat().st_size,
                    'header_bytes': content[:100].hex(),
                    'note': 'Binary CAD file - limited text extraction possible'
                }
                
            except Exception as e:
                self.logger.error(f"Binary file analysis failed: {e}")
                return None
        except Exception as e:
            self.logger.error(f"Generic CAD extraction failed: {e}")
            return None
    
    def _generate_technical_analysis(self, cad_data: Dict[str, Any], file_path: Path) -> Optional[str]:
        """Generate technical analysis of CAD content."""
        try:
            analysis_parts = []
            
            cad_type = cad_data.get('type', 'unknown')
            analysis_parts.append(f"CAD file type: {cad_type}")
            
            if cad_type == 'autocad_dxf':
                analysis_parts.append(f"AutoCAD DXF file with {cad_data.get('total_entities', 0)} entities")
                if cad_data.get('text_entities'):
                    analysis_parts.append(f"Text elements: {'; '.join(cad_data['text_entities'][:10])}")
                if cad_data.get('layers'):
                    analysis_parts.append(f"Layers: {', '.join(cad_data['layers'][:10])}")
                    
            elif cad_type == 'autocad_dwg':
                analysis_parts.append("AutoCAD DWG file (binary format)")
                analysis_parts.append("Note: Requires specialized tools for full extraction")
                
            elif cad_type == 'step':
                analysis_parts.append(f"STEP file with {cad_data.get('faces', 0)} faces, {cad_data.get('edges', 0)} edges, {cad_data.get('vertices', 0)} vertices")
                
            elif cad_type == '3d_mesh':
                analysis_parts.append(f"3D mesh with {cad_data.get('vertices', 0)} vertices, {cad_data.get('faces', 0)} faces")
                if cad_data.get('volume'):
                    analysis_parts.append(f"Volume: {cad_data['volume']:.2f}")
                if cad_data.get('surface_area'):
                    analysis_parts.append(f"Surface area: {cad_data['surface_area']:.2f}")
                    
            elif cad_type == 'vector_svg':
                analysis_parts.append(f"Vector SVG file: {cad_data.get('dimensions', 'unknown dimensions')}")
                if cad_data.get('text_elements'):
                    analysis_parts.append(f"Text elements: {'; '.join(cad_data['text_elements'][:10])}")
                    
            elif cad_type == 'image_technical':
                analysis_parts.append(f"Technical image: {cad_data.get('width', 0)}x{cad_data.get('height', 0)} pixels")
                if cad_data.get('text_content'):
                    analysis_parts.append(f"Extracted text: {cad_data['text_content'][:200]}...")
                    
            elif cad_type == 'generic_cad':
                content = cad_data.get('content', '')
                analysis_parts.append(f"Generic CAD file with {len(content)} characters")
                analysis_parts.append(f"Content preview: {content[:200]}...")
                
            elif cad_type == 'binary_cad':
                analysis_parts.append(f"Binary CAD file: {cad_data.get('file_size', 0)} bytes")
                analysis_parts.append("Binary format - limited text extraction")
            
            # Add technical drawing indicators
            technical_indicators = self._detect_technical_indicators(cad_data)
            if technical_indicators:
                analysis_parts.append(f"Technical indicators: {technical_indicators}")
            
            return "\n".join(analysis_parts) if analysis_parts else None
            
        except Exception as e:
            self.logger.error(f"Technical analysis failed for {file_path}: {e}")
            return None
    
    def _detect_technical_indicators(self, cad_data: Dict[str, Any]) -> Optional[str]:
        """Detect technical drawing indicators in CAD content."""
        try:
            indicators = []
            
            # Check for technical drawing keywords
            tech_keywords = [
                'dimension', 'tolerance', 'material', 'finish', 'scale', 'view', 'section',
                'detail', 'assembly', 'part', 'component', 'drawing', 'blueprint', 'specification',
                'technical', 'engineering', 'manufacturing', 'production', 'quality', 'inspection'
            ]
            
            content = str(cad_data).lower()
            found_keywords = [keyword for keyword in tech_keywords if keyword in content]
            
            if found_keywords:
                indicators.append(f"Technical keywords: {', '.join(found_keywords[:5])}")
            
            # Check for measurement patterns
            import re
            measurement_patterns = [
                r'\d+\.?\d*\s*(mm|cm|m|in|ft|yd)',  # Metric and imperial units
                r'\d+\.?\d*\s*±\s*\d+\.?\d*',      # Tolerances
                r'[A-Z]{1,2}\d+',                  # Part numbers
                r'REV\s*\d+',                      # Revision numbers
            ]
            
            for pattern in measurement_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    indicators.append(f"Measurements/tolerances found: {len(matches)} instances")
                    break
            
            return "; ".join(indicators) if indicators else None
            
        except Exception as e:
            self.logger.error(f"Technical indicator detection failed: {e}")
            return None
    
    def _get_cad_metadata(self, file_path: Path, cad_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get metadata about the CAD file."""
        try:
            metadata = {
                'file_size': file_path.stat().st_size,
                'cad_type': cad_data.get('type', 'unknown'),
                'file_extension': file_path.suffix.lower()
            }
            
            # Add type-specific metadata
            if cad_data.get('type') == 'autocad_dxf':
                metadata.update({
                    'total_entities': cad_data.get('total_entities', 0),
                    'text_count': cad_data.get('text_count', 0),
                    'layer_count': len(cad_data.get('layers', []))
                })
            elif cad_data.get('type') == 'step':
                metadata.update({
                    'faces': cad_data.get('faces', 0),
                    'edges': cad_data.get('edges', 0),
                    'vertices': cad_data.get('vertices', 0)
                })
            elif cad_data.get('type') == '3d_mesh':
                metadata.update({
                    'vertices': cad_data.get('vertices', 0),
                    'faces': cad_data.get('faces', 0),
                    'volume': cad_data.get('volume'),
                    'surface_area': cad_data.get('surface_area')
                })
            elif cad_data.get('type') == 'image_technical':
                metadata.update({
                    'width': cad_data.get('width'),
                    'height': cad_data.get('height'),
                    'format': cad_data.get('format')
                })
            
            return metadata
            
        except Exception as e:
            self.logger.warning(f"Failed to get CAD metadata for {file_path}: {e}")
            return {
                'cad_type': cad_data.get('type', 'unknown'),
                'error': str(e)
            } 