"""
Mesh Generator for Physics Modeling
Handles mesh generation, optimization, and quality assessment
"""

import asyncio
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class MeshType(Enum):
    """Types of mesh generation"""
    STRUCTURED = "structured"
    UNSTRUCTURED = "unstructured"
    HYBRID = "hybrid"
    ADAPTIVE = "adaptive"

class ElementType(Enum):
    """Types of mesh elements"""
    TRIANGLE = "triangle"
    QUADRILATERAL = "quadrilateral"
    TETRAHEDRON = "tetrahedron"
    HEXAHEDRON = "hexahedron"
    PRISM = "prism"
    PYRAMID = "pyramid"

@dataclass
class MeshConfig:
    """Configuration for mesh generation"""
    mesh_type: MeshType = MeshType.UNSTRUCTURED
    element_type: ElementType = ElementType.TRIANGLE
    resolution: float = 1.0
    quality_threshold: float = 0.3
    max_aspect_ratio: float = 10.0
    min_angle: float = 15.0
    max_angle: float = 165.0
    smoothing_iterations: int = 5
    refinement_levels: int = 3
    boundary_layer_thickness: float = 0.1
    use_adaptive_refinement: bool = True

class MeshGenerator:
    """Mesh generation and optimization for physics modeling"""
    
    def __init__(self, config: Optional[MeshConfig] = None):
        self.config = config or MeshConfig()
        self.mesh_history = []
        self.quality_metrics = {}
        logger.info("✅ Mesh Generator initialized")
    
    async def generate_mesh(self, geometry_data: Dict[str, Any], 
                           physics_type: str = "structural") -> Dict[str, Any]:
        """Generate mesh based on geometry and physics requirements"""
        await asyncio.sleep(0)
        
        start_time = datetime.now()
        logger.info(f"🔄 Generating {self.config.mesh_type.value} mesh for {physics_type}")
        
        try:
            # Validate geometry data
            validation_result = await self._validate_geometry(geometry_data)
            if not validation_result['valid']:
                raise ValueError(f"Geometry validation failed: {validation_result['errors']}")
            
            # Generate base mesh
            base_mesh = await self._generate_base_mesh(geometry_data, physics_type)
            
            # Optimize mesh quality
            optimized_mesh = await self._optimize_mesh_quality(base_mesh)
            
            # Apply physics-specific refinements
            refined_mesh = await self._apply_physics_refinements(optimized_mesh, physics_type)
            
            # Final quality assessment
            quality_assessment = await self._assess_mesh_quality(refined_mesh)
            
            # Generate mesh statistics
            mesh_stats = await self._generate_mesh_statistics(refined_mesh)
            
            generation_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'mesh_data': refined_mesh,
                'mesh_config': self.config.__dict__,
                'physics_type': physics_type,
                'generation_time': generation_time,
                'quality_assessment': quality_assessment,
                'mesh_statistics': mesh_stats,
                'success': True
            }
            
            # Record mesh generation history
            self.mesh_history.append({
                'timestamp': datetime.now(),
                'physics_type': physics_type,
                'mesh_type': self.config.mesh_type.value,
                'element_type': self.config.element_type.value,
                'generation_time': generation_time,
                'quality_score': quality_assessment['overall_quality'],
                'success': True
            })
            
            logger.info(f"✅ Mesh generation completed in {generation_time:.3f}s")
            return result
            
        except Exception as e:
            generation_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Mesh generation failed: {str(e)}")
            
            self.mesh_history.append({
                'timestamp': datetime.now(),
                'physics_type': physics_type,
                'mesh_type': self.config.mesh_type.value,
                'element_type': self.config.element_type.value,
                'generation_time': generation_time,
                'success': False,
                'error': str(e)
            })
            
            return {
                'success': False,
                'error': str(e),
                'generation_time': generation_time
            }
    
    async def _validate_geometry(self, geometry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input geometry data"""
        await asyncio.sleep(0)
        
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        required_keys = ['vertices', 'faces', 'dimensions']
        for key in required_keys:
            if key not in geometry_data:
                validation_result['errors'].append(f"Missing required key: {key}")
                validation_result['valid'] = False
        
        if not validation_result['valid']:
            return validation_result
        
        # Validate vertices
        vertices = geometry_data['vertices']
        if not isinstance(vertices, np.ndarray) or vertices.ndim != 2:
            validation_result['errors'].append("Vertices must be a 2D numpy array")
            validation_result['valid'] = False
        
        # Validate faces
        faces = geometry_data['faces']
        if not isinstance(faces, np.ndarray) or faces.ndim != 2:
            validation_result['errors'].append("Faces must be a 2D numpy array")
            validation_result['valid'] = False
        
        # Validate dimensions
        dimensions = geometry_data['dimensions']
        if not isinstance(dimensions, (int, float)) or dimensions <= 0:
            validation_result['errors'].append("Dimensions must be a positive number")
            validation_result['valid'] = False
        
        return validation_result
    
    async def _generate_base_mesh(self, geometry_data: Dict[str, Any], 
                                 physics_type: str) -> Dict[str, Any]:
        """Generate the base mesh structure"""
        await asyncio.sleep(0)
        
        vertices = geometry_data['vertices']
        faces = geometry_data['faces']
        dimensions = geometry_data['dimensions']
        
        if self.config.mesh_type == MeshType.STRUCTURED:
            mesh = await self._generate_structured_mesh(vertices, faces, dimensions)
        elif self.config.mesh_type == MeshType.UNSTRUCTURED:
            mesh = await self._generate_unstructured_mesh(vertices, faces, dimensions)
        elif self.config.mesh_type == MeshType.HYBRID:
            mesh = await self._generate_hybrid_mesh(vertices, faces, dimensions)
        else:
            mesh = await self._generate_adaptive_mesh(vertices, faces, dimensions)
        
        return mesh
    
    async def _generate_structured_mesh(self, vertices: np.ndarray, 
                                      faces: np.ndarray, dimensions: float) -> Dict[str, Any]:
        """Generate structured mesh"""
        await asyncio.sleep(0)
        
        # Create regular grid based on bounding box
        bbox_min = np.min(vertices, axis=0)
        bbox_max = np.max(vertices, axis=0)
        
        # Calculate grid spacing
        grid_spacing = dimensions / self.config.resolution
        
        # Generate grid points
        x_coords = np.arange(bbox_min[0], bbox_max[0] + grid_spacing, grid_spacing)
        y_coords = np.arange(bbox_min[1], bbox_max[1] + grid_spacing, grid_spacing)
        
        if vertices.shape[1] == 3:  # 3D
            z_coords = np.arange(bbox_min[2], bbox_max[2] + grid_spacing, grid_spacing)
            grid_points = np.array(np.meshgrid(x_coords, y_coords, z_coords)).reshape(3, -1).T
        else:  # 2D
            grid_points = np.array(np.meshgrid(x_coords, y_coords)).reshape(2, -1).T
        
        # Create elements
        if self.config.element_type == ElementType.QUADRILATERAL:
            elements = await self._create_quadrilateral_elements(x_coords, y_coords)
        elif self.config.element_type == ElementType.HEXAHEDRON:
            elements = await self._create_hexahedron_elements(x_coords, y_coords, z_coords)
        else:
            elements = await self._create_triangular_elements(x_coords, y_coords)
        
        return {
            'vertices': grid_points,
            'elements': elements,
            'mesh_type': 'structured',
            'element_type': self.config.element_type.value,
            'grid_spacing': grid_spacing
        }
    
    async def _generate_unstructured_mesh(self, vertices: np.ndarray, 
                                        faces: np.ndarray, dimensions: float) -> Dict[str, Any]:
        """Generate unstructured mesh using Delaunay triangulation"""
        await asyncio.sleep(0)
        
        # For simplicity, create a triangulation of the input vertices
        # In practice, this would use a proper triangulation library
        
        # Create triangular elements from faces
        if faces.shape[1] == 3:
            elements = faces
        elif faces.shape[1] == 4:
            # Split quadrilaterals into triangles
            elements = []
            for face in faces:
                elements.append([face[0], face[1], face[2]])
                elements.append([face[0], face[2], face[3]])
            elements = np.array(elements)
        else:
            # Create simple triangulation
            elements = await self._simple_triangulation(vertices)
        
        return {
            'vertices': vertices,
            'elements': elements,
            'mesh_type': 'unstructured',
            'element_type': 'triangle',
            'original_faces': faces
        }
    
    async def _generate_hybrid_mesh(self, vertices: np.ndarray, 
                                   faces: np.ndarray, dimensions: float) -> Dict[str, Any]:
        """Generate hybrid mesh combining structured and unstructured regions"""
        await asyncio.sleep(0)
        
        # Identify boundary and interior regions
        boundary_vertices = await self._identify_boundary_vertices(vertices, faces)
        interior_vertices = await self._identify_interior_vertices(vertices, faces)
        
        # Generate structured mesh for interior
        interior_mesh = await self._generate_structured_mesh(interior_vertices, np.array([]), dimensions)
        
        # Generate unstructured mesh for boundary
        boundary_mesh = await self._generate_unstructured_mesh(boundary_vertices, faces, dimensions)
        
        # Combine meshes
        combined_vertices = np.vstack([interior_mesh['vertices'], boundary_mesh['vertices']])
        combined_elements = np.vstack([interior_mesh['elements'], boundary_mesh['elements']])
        
        return {
            'vertices': combined_vertices,
            'elements': combined_elements,
            'mesh_type': 'hybrid',
            'element_type': 'mixed',
            'interior_mesh': interior_mesh,
            'boundary_mesh': boundary_mesh
        }
    
    async def _generate_adaptive_mesh(self, vertices: np.ndarray, 
                                     faces: np.ndarray, dimensions: float) -> Dict[str, Any]:
        """Generate adaptive mesh based on solution gradients"""
        await asyncio.sleep(0)
        
        # Start with coarse mesh
        coarse_mesh = await self._generate_unstructured_mesh(vertices, faces, dimensions * 2)
        
        # Simulate solution gradients for refinement
        solution_gradients = await self._estimate_solution_gradients(coarse_mesh)
        
        # Refine based on gradients
        refined_mesh = await self._refine_mesh_by_gradients(coarse_mesh, solution_gradients)
        
        return {
            'vertices': refined_mesh['vertices'],
            'elements': refined_mesh['elements'],
            'mesh_type': 'adaptive',
            'element_type': 'triangle',
            'refinement_levels': self.config.refinement_levels,
            'gradient_threshold': 0.1
        }
    
    async def _optimize_mesh_quality(self, mesh: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize mesh quality through smoothing and optimization"""
        await asyncio.sleep(0)
        
        vertices = mesh['vertices']
        elements = mesh['elements']
        
        # Apply Laplacian smoothing
        for _ in range(self.config.smoothing_iterations):
            vertices = await self._laplacian_smoothing(vertices, elements)
        
        # Optimize element quality
        optimized_elements = await self._optimize_element_quality(vertices, elements)
        
        # Remove low-quality elements
        quality_scores = await self._calculate_element_quality(vertices, optimized_elements)
        good_elements_mask = quality_scores > self.config.quality_threshold
        
        return {
            **mesh,
            'vertices': vertices,
            'elements': optimized_elements[good_elements_mask],
            'quality_scores': quality_scores[good_elements_mask],
            'optimization_applied': True
        }
    
    async def _apply_physics_refinements(self, mesh: Dict[str, Any], 
                                        physics_type: str) -> Dict[str, Any]:
        """Apply physics-specific mesh refinements"""
        await asyncio.sleep(0)
        
        if physics_type == "structural":
            return await self._apply_structural_refinements(mesh)
        elif physics_type == "thermal":
            return await self._apply_thermal_refinements(mesh)
        elif physics_type == "fluid":
            return await self._apply_fluid_refinements(mesh)
        elif physics_type == "electromagnetic":
            return await self._apply_electromagnetic_refinements(mesh)
        else:
            return mesh
    
    async def _assess_mesh_quality(self, mesh: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall mesh quality"""
        await asyncio.sleep(0)
        
        vertices = mesh['vertices']
        elements = mesh['elements']
        
        # Calculate various quality metrics
        aspect_ratios = await self._calculate_aspect_ratios(vertices, elements)
        angles = await self._calculate_element_angles(vertices, elements)
        areas_volumes = await self._calculate_areas_volumes(vertices, elements)
        
        # Overall quality score
        overall_quality = np.mean([
            np.mean(aspect_ratios),
            np.mean(angles),
            np.mean(areas_volumes)
        ])
        
        quality_assessment = {
            'overall_quality': overall_quality,
            'aspect_ratios': {
                'mean': np.mean(aspect_ratios),
                'min': np.min(aspect_ratios),
                'max': np.max(aspect_ratios),
                'std': np.std(aspect_ratios)
            },
            'angles': {
                'mean': np.mean(angles),
                'min': np.min(angles),
                'max': np.max(angles),
                'std': np.std(angles)
            },
            'areas_volumes': {
                'mean': np.mean(areas_volumes),
                'min': np.min(areas_volumes),
                'max': np.max(areas_volumes),
                'std': np.std(areas_volumes)
            },
            'quality_distribution': {
                'excellent': np.sum(quality_scores > 0.8),
                'good': np.sum((quality_scores > 0.6) & (quality_scores <= 0.8)),
                'acceptable': np.sum((quality_scores > 0.4) & (quality_scores <= 0.6)),
                'poor': np.sum(quality_scores <= 0.4)
            }
        }
        
        # Store quality metrics
        mesh_id = f"mesh_{len(self.mesh_history)}"
        self.quality_metrics[mesh_id] = quality_assessment
        
        return quality_assessment
    
    async def _generate_mesh_statistics(self, mesh: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive mesh statistics"""
        await asyncio.sleep(0)
        
        vertices = mesh['vertices']
        elements = mesh['elements']
        
        stats = {
            'total_vertices': len(vertices),
            'total_elements': len(elements),
            'mesh_dimension': vertices.shape[1],
            'element_type': mesh.get('element_type', 'unknown'),
            'mesh_type': mesh.get('mesh_type', 'unknown'),
            'bounding_box': {
                'min': np.min(vertices, axis=0).tolist(),
                'max': np.max(vertices, axis=0).tolist(),
                'extent': (np.max(vertices, axis=0) - np.min(vertices, axis=0)).tolist()
            },
            'element_connectivity': {
                'min_connectivity': np.min([len(set(element)) for element in elements]),
                'max_connectivity': np.max([len(set(element)) for element in elements]),
                'avg_connectivity': np.mean([len(set(element)) for element in elements])
            }
        }
        
        return stats
    
    # Helper methods for mesh generation
    async def _create_quadrilateral_elements(self, x_coords: np.ndarray, 
                                           y_coords: np.ndarray) -> np.ndarray:
        """Create quadrilateral elements from coordinate arrays"""
        await asyncio.sleep(0)
        
        elements = []
        for i in range(len(x_coords) - 1):
            for j in range(len(y_coords) - 1):
                # Calculate vertex indices
                v1 = i * len(y_coords) + j
                v2 = i * len(y_coords) + j + 1
                v3 = (i + 1) * len(y_coords) + j + 1
                v4 = (i + 1) * len(y_coords) + j
                elements.append([v1, v2, v3, v4])
        
        return np.array(elements)
    
    async def _create_hexahedron_elements(self, x_coords: np.ndarray, 
                                         y_coords: np.ndarray, 
                                         z_coords: np.ndarray) -> np.ndarray:
        """Create hexahedron elements from coordinate arrays"""
        await asyncio.sleep(0)
        
        elements = []
        for i in range(len(x_coords) - 1):
            for j in range(len(y_coords) - 1):
                for k in range(len(z_coords) - 1):
                    # Calculate vertex indices for hexahedron
                    base = i * len(y_coords) * len(z_coords) + j * len(z_coords) + k
                    v1 = base
                    v2 = base + 1
                    v3 = base + len(z_coords) + 1
                    v4 = base + len(z_coords)
                    v5 = base + len(y_coords) * len(z_coords)
                    v6 = base + len(y_coords) * len(z_coords) + 1
                    v7 = base + len(y_coords) * len(z_coords) + len(z_coords) + 1
                    v8 = base + len(y_coords) * len(z_coords) + len(z_coords)
                    elements.append([v1, v2, v3, v4, v5, v6, v7, v8])
        
        return np.array(elements)
    
    async def _create_triangular_elements(self, x_coords: np.ndarray, 
                                        y_coords: np.ndarray) -> np.ndarray:
        """Create triangular elements from coordinate arrays"""
        await asyncio.sleep(0)
        
        elements = []
        for i in range(len(x_coords) - 1):
            for j in range(len(y_coords) - 1):
                # Calculate vertex indices
                v1 = i * len(y_coords) + j
                v2 = i * len(y_coords) + j + 1
                v3 = (i + 1) * len(y_coords) + j
                v4 = (i + 1) * len(y_coords) + j + 1
                
                # Split into two triangles
                elements.append([v1, v2, v3])
                elements.append([v2, v4, v3])
        
        return np.array(elements)
    
    async def _simple_triangulation(self, vertices: np.ndarray) -> np.ndarray:
        """Simple triangulation for demonstration"""
        await asyncio.sleep(0)
        
        # Create a simple triangulation (fan triangulation from centroid)
        centroid = np.mean(vertices, axis=0)
        elements = []
        
        for i in range(len(vertices) - 1):
            elements.append([len(vertices), i, i + 1])
        elements.append([len(vertices), len(vertices) - 1, 0])
        
        # Add centroid as last vertex
        vertices_with_centroid = np.vstack([vertices, centroid])
        
        return np.array(elements)
    
    async def _identify_boundary_vertices(self, vertices: np.ndarray, 
                                         faces: np.ndarray) -> np.ndarray:
        """Identify boundary vertices"""
        await asyncio.sleep(0)
        
        # Simple boundary detection (vertices that appear in faces)
        boundary_indices = np.unique(faces.flatten())
        return vertices[boundary_indices]
    
    async def _identify_interior_vertices(self, vertices: np.ndarray, 
                                         faces: np.ndarray) -> np.ndarray:
        """Identify interior vertices"""
        await asyncio.sleep(0)
        
        # Interior vertices are those not on the boundary
        boundary_indices = set(faces.flatten())
        interior_indices = [i for i in range(len(vertices)) if i not in boundary_indices]
        return vertices[interior_indices]
    
    async def _estimate_solution_gradients(self, mesh: Dict[str, Any]) -> np.ndarray:
        """Estimate solution gradients for adaptive refinement"""
        await asyncio.sleep(0)
        
        # Mock gradient estimation
        vertices = mesh['vertices']
        gradients = np.random.rand(len(vertices), vertices.shape[1]) * 0.1
        return gradients
    
    async def _refine_mesh_by_gradients(self, mesh: Dict[str, Any], 
                                       gradients: np.ndarray) -> Dict[str, Any]:
        """Refine mesh based on gradient information"""
        await asyncio.sleep(0)
        
        # Simple refinement: add vertices where gradients are high
        high_gradient_mask = np.linalg.norm(gradients, axis=1) > 0.05
        high_gradient_vertices = mesh['vertices'][high_gradient_mask]
        
        # Add new vertices
        new_vertices = np.vstack([mesh['vertices'], high_gradient_vertices])
        
        # Update elements (simplified)
        new_elements = mesh['elements'].copy()
        
        return {
            **mesh,
            'vertices': new_vertices,
            'elements': new_elements
        }
    
    async def _laplacian_smoothing(self, vertices: np.ndarray, 
                                  elements: np.ndarray) -> np.ndarray:
        """Apply Laplacian smoothing to vertices"""
        await asyncio.sleep(0)
        
        smoothed_vertices = vertices.copy()
        
        for i, vertex in enumerate(vertices):
            # Find neighboring vertices
            neighbors = []
            for element in elements:
                if i in element:
                    for j in element:
                        if j != i:
                            neighbors.append(j)
            
            if neighbors:
                neighbor_coords = vertices[neighbors]
                smoothed_vertices[i] = np.mean(neighbor_coords, axis=0)
        
        return smoothed_vertices
    
    async def _optimize_element_quality(self, vertices: np.ndarray, 
                                       elements: np.ndarray) -> np.ndarray:
        """Optimize element quality through edge swapping"""
        await asyncio.sleep(0)
        
        # Simple optimization: keep original elements
        # In practice, this would implement edge swapping, node relocation, etc.
        return elements
    
    async def _calculate_element_quality(self, vertices: np.ndarray, 
                                        elements: np.ndarray) -> np.ndarray:
        """Calculate quality scores for elements"""
        await asyncio.sleep(0)
        
        quality_scores = []
        
        for element in elements:
            element_vertices = vertices[element]
            
            if len(element) == 3:  # Triangle
                quality = await self._calculate_triangle_quality(element_vertices)
            elif len(element) == 4:  # Quadrilateral
                quality = await self._calculate_quadrilateral_quality(element_vertices)
            else:
                quality = 0.5  # Default quality
            
            quality_scores.append(quality)
        
        return np.array(quality_scores)
    
    async def _calculate_triangle_quality(self, vertices: np.ndarray) -> float:
        """Calculate quality of triangular element"""
        await asyncio.sleep(0)
        
        # Calculate edge lengths
        edges = []
        for i in range(3):
            edge = vertices[(i + 1) % 3] - vertices[i]
            edges.append(np.linalg.norm(edge))
        
        # Calculate area
        area = 0.5 * abs(np.cross(vertices[1] - vertices[0], vertices[2] - vertices[0]))
        
        # Quality based on equilateral triangle ratio
        if area > 0:
            quality = area / (np.sum(edges) ** 2) * 12 * np.sqrt(3)
        else:
            quality = 0
        
        return min(quality, 1.0)
    
    async def _calculate_quadrilateral_quality(self, vertices: np.ndarray) -> float:
        """Calculate quality of quadrilateral element"""
        await asyncio.sleep(0)
        
        # Calculate edge lengths
        edges = []
        for i in range(4):
            edge = vertices[(i + 1) % 4] - vertices[i]
            edges.append(np.linalg.norm(edge))
        
        # Calculate area
        area = abs(np.cross(vertices[1] - vertices[0], vertices[2] - vertices[0]))
        
        # Quality based on square ratio
        if area > 0:
            quality = area / (np.sum(edges) ** 2) * 16
        else:
            quality = 0
        
        return min(quality, 1.0)
    
    async def _calculate_aspect_ratios(self, vertices: np.ndarray, 
                                      elements: np.ndarray) -> np.ndarray:
        """Calculate aspect ratios for elements"""
        await asyncio.sleep(0)
        
        aspect_ratios = []
        
        for element in elements:
            element_vertices = vertices[element]
            
            if len(element) == 3:  # Triangle
                aspect_ratio = await self._calculate_triangle_aspect_ratio(element_vertices)
            elif len(element) == 4:  # Quadrilateral
                aspect_ratio = await self._calculate_quadrilateral_aspect_ratio(element_vertices)
            else:
                aspect_ratio = 1.0  # Default aspect ratio
            
            aspect_ratios.append(aspect_ratio)
        
        return np.array(aspect_ratios)
    
    async def _calculate_triangle_aspect_ratio(self, vertices: np.ndarray) -> float:
        """Calculate aspect ratio of triangular element"""
        await asyncio.sleep(0)
        
        # Calculate edge lengths
        edges = []
        for i in range(3):
            edge = vertices[(i + 1) % 3] - vertices[i]
            edges.append(np.linalg.norm(edge))
        
        # Aspect ratio = longest edge / shortest edge
        if min(edges) > 0:
            return max(edges) / min(edges)
        else:
            return float('inf')
    
    async def _calculate_quadrilateral_aspect_ratio(self, vertices: np.ndarray) -> float:
        """Calculate aspect ratio of quadrilateral element"""
        await asyncio.sleep(0)
        
        # Calculate edge lengths
        edges = []
        for i in range(4):
            edge = vertices[(i + 1) % 4] - vertices[i]
            edges.append(np.linalg.norm(edge))
        
        # Aspect ratio = longest edge / shortest edge
        if min(edges) > 0:
            return max(edges) / min(edges)
        else:
            return float('inf')
    
    async def _calculate_element_angles(self, vertices: np.ndarray, 
                                       elements: np.ndarray) -> np.ndarray:
        """Calculate angles for elements"""
        await asyncio.sleep(0)
        
        angles = []
        
        for element in elements:
            element_vertices = vertices[element]
            
            if len(element) == 3:  # Triangle
                element_angles = await self._calculate_triangle_angles(element_vertices)
            elif len(element) == 4:  # Quadrilateral
                element_angles = await self._calculate_quadrilateral_angles(element_vertices)
            else:
                element_angles = [90.0] * len(element)  # Default angles
            
            angles.extend(element_angles)
        
        return np.array(angles)
    
    async def _calculate_triangle_angles(self, vertices: np.ndarray) -> List[float]:
        """Calculate angles of triangular element"""
        await asyncio.sleep(0)
        
        angles = []
        
        for i in range(3):
            v1 = vertices[i]
            v2 = vertices[(i + 1) % 3]
            v3 = vertices[(i + 2) % 3]
            
            # Calculate vectors
            vec1 = v2 - v1
            vec2 = v3 - v1
            
            # Calculate angle
            cos_angle = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            cos_angle = np.clip(cos_angle, -1.0, 1.0)
            angle = np.arccos(cos_angle) * 180 / np.pi
            
            angles.append(angle)
        
        return angles
    
    async def _calculate_quadrilateral_angles(self, vertices: np.ndarray) -> List[float]:
        """Calculate angles of quadrilateral element"""
        await asyncio.sleep(0)
        
        angles = []
        
        for i in range(4):
            v1 = vertices[i]
            v2 = vertices[(i + 1) % 4]
            v3 = vertices[(i + 2) % 4]
            
            # Calculate vectors
            vec1 = v2 - v1
            vec2 = v3 - v1
            
            # Calculate angle
            cos_angle = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            cos_angle = np.clip(cos_angle, -1.0, 1.0)
            angle = np.arccos(cos_angle) * 180 / np.pi
            
            angles.append(angle)
        
        return angles
    
    async def _calculate_areas_volumes(self, vertices: np.ndarray, 
                                      elements: np.ndarray) -> np.ndarray:
        """Calculate areas/volumes for elements"""
        await asyncio.sleep(0)
        
        areas_volumes = []
        
        for element in elements:
            element_vertices = vertices[element]
            
            if len(element) == 3:  # Triangle
                area_volume = await self._calculate_triangle_area(element_vertices)
            elif len(element) == 4:  # Quadrilateral
                area_volume = await self._calculate_quadrilateral_area(element_vertices)
            else:
                area_volume = 1.0  # Default area/volume
            
            areas_volumes.append(area_volume)
        
        return np.array(areas_volumes)
    
    async def _calculate_triangle_area(self, vertices: np.ndarray) -> float:
        """Calculate area of triangular element"""
        await asyncio.sleep(0)
        
        # Area = 0.5 * |cross product|
        area = 0.5 * abs(np.cross(vertices[1] - vertices[0], vertices[2] - vertices[0]))
        return area
    
    async def _calculate_quadrilateral_area(self, vertices: np.ndarray) -> float:
        """Calculate area of quadrilateral element"""
        await asyncio.sleep(0)
        
        # Area = 0.5 * |cross product| (approximate for non-planar quads)
        area = 0.5 * abs(np.cross(vertices[1] - vertices[0], vertices[2] - vertices[0]))
        return area
    
    # Physics-specific refinement methods
    async def _apply_structural_refinements(self, mesh: Dict[str, Any]) -> Dict[str, Any]:
        """Apply structural analysis specific refinements"""
        await asyncio.sleep(0)
        
        # Refine around stress concentration areas
        # For now, return the mesh as-is
        return mesh
    
    async def _apply_thermal_refinements(self, mesh: Dict[str, Any]) -> Dict[str, Any]:
        """Apply thermal analysis specific refinements"""
        await asyncio.sleep(0)
        
        # Refine around heat sources and boundaries
        # For now, return the mesh as-is
        return mesh
    
    async def _apply_fluid_refinements(self, mesh: Dict[str, Any]) -> Dict[str, Any]:
        """Apply fluid dynamics specific refinements"""
        await asyncio.sleep(0)
        
        # Refine around boundaries and high-gradient regions
        # For now, return the mesh as-is
        return mesh
    
    async def _apply_electromagnetic_refinements(self, mesh: Dict[str, Any]) -> Dict[str, Any]:
        """Apply electromagnetic analysis specific refinements"""
        await asyncio.sleep(0)
        
        # Refine around conductors and high-field regions
        # For now, return the mesh as-is
        return mesh
    
    async def get_mesh_generation_summary(self) -> Dict[str, Any]:
        """Get summary of all mesh generation operations"""
        await asyncio.sleep(0)
        
        total_operations = len(self.mesh_history)
        successful_operations = sum(1 for op in self.mesh_history if op.get('success', False))
        failed_operations = total_operations - successful_operations
        
        avg_generation_time = 0
        avg_quality_score = 0
        
        if successful_operations > 0:
            generation_times = [op['generation_time'] for op in self.mesh_history if op.get('success', False)]
            quality_scores = [op['quality_score'] for op in self.mesh_history if op.get('success', False) and 'quality_score' in op]
            
            avg_generation_time = sum(generation_times) / len(generation_times)
            if quality_scores:
                avg_quality_score = sum(quality_scores) / len(quality_scores)
        
        return {
            'total_operations': total_operations,
            'successful_operations': successful_operations,
            'failed_operations': failed_operations,
            'success_rate': successful_operations / total_operations if total_operations > 0 else 0,
            'average_generation_time': avg_generation_time,
            'average_quality_score': avg_quality_score,
            'physics_types_processed': list(set(op['physics_type'] for op in self.mesh_history)),
            'mesh_types_generated': list(set(op['mesh_type'] for op in self.mesh_history)),
            'recent_operations': self.mesh_history[-5:] if self.mesh_history else []
        }
    
    async def reset_statistics(self) -> None:
        """Reset all statistics and history"""
        await asyncio.sleep(0)
        
        self.mesh_history.clear()
        self.quality_metrics.clear()
        logger.info("🔄 Mesh Generator statistics reset")
