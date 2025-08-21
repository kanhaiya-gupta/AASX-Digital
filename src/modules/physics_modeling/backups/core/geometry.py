"""
Geometry for Physics Modeling

This module defines the Geometry class and related components for handling
geometric representations in physics-based simulations.
"""

import json
import logging
import numpy as np
import copy
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class Geometry:
    """
    Geometric representation for physics modeling
    
    This class represents geometric entities used in physics simulations
    including meshes, boundaries, and spatial domains.
    """
    
    name: str
    geometry_type: str  # "mesh", "boundary", "domain", "cad"
    dimension: int = 3  # 1D, 2D, or 3D
    
    # Geometric data
    vertices: Optional[np.ndarray] = None  # Nx3 array of vertex coordinates
    elements: Optional[np.ndarray] = None  # MxN array of element connectivity
    element_types: Optional[List[str]] = None  # List of element types (e.g., "tet", "hex", "tri")
    
    # Boundary information
    boundaries: Dict[str, Any] = field(default_factory=dict)  # Boundary conditions and regions
    regions: Dict[str, Any] = field(default_factory=dict)  # Material regions
    
    # Metadata
    units: str = "meters"
    file_path: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate geometry after initialization"""
        self.validate_geometry()
    
    def validate_geometry(self) -> bool:
        """Validate geometry data for consistency"""
        errors = []
        
        # Check dimension
        if self.dimension not in [1, 2, 3]:
            errors.append("Dimension must be 1, 2, or 3")
        
        # Check vertices if provided
        if self.vertices is not None:
            if not isinstance(self.vertices, np.ndarray):
                errors.append("Vertices must be a numpy array")
            elif self.vertices.shape[1] != self.dimension:
                errors.append(f"Vertices must have {self.dimension} columns for {self.dimension}D geometry")
        
        # Check elements if provided
        if self.elements is not None:
            if not isinstance(self.elements, np.ndarray):
                errors.append("Elements must be a numpy array")
            elif self.vertices is not None:
                max_vertex_index = self.vertices.shape[0] - 1
                if np.max(self.elements) > max_vertex_index:
                    errors.append("Element indices exceed vertex count")
        
        # Check element types if provided
        if self.element_types is not None and self.elements is not None:
            if len(self.element_types) != self.elements.shape[0]:
                errors.append("Number of element types must match number of elements")
        
        if errors:
            logger.warning(f"Geometry validation errors for {self.name}: {errors}")
            return False
        
        return True
    
    def get_vertex_count(self) -> int:
        """Get number of vertices"""
        return self.vertices.shape[0] if self.vertices is not None else 0
    
    def get_element_count(self) -> int:
        """Get number of elements"""
        return self.elements.shape[0] if self.elements is not None else 0
    
    def get_bounding_box(self) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """Get bounding box of geometry"""
        if self.vertices is None:
            return None
        
        min_coords = np.min(self.vertices, axis=0)
        max_coords = np.max(self.vertices, axis=0)
        return min_coords, max_coords
    
    def get_center(self) -> Optional[np.ndarray]:
        """Get center of geometry"""
        if self.vertices is None:
            return None
        
        return np.mean(self.vertices, axis=0)
    
    def get_volume(self) -> Optional[float]:
        """Calculate volume of geometry (3D) or area (2D)"""
        if self.elements is None or self.vertices is None:
            return None
        
        if self.dimension == 2:
            return self._calculate_area()
        elif self.dimension == 3:
            return self._calculate_volume()
        else:
            return None
    
    def _calculate_area(self) -> float:
        """Calculate area of 2D geometry"""
        # Simple triangulation-based area calculation
        total_area = 0.0
        
        for element in self.elements:
            if len(element) == 3:  # Triangle
                v1, v2, v3 = self.vertices[element]
                # Cross product for triangle area
                area = 0.5 * abs(np.cross(v2 - v1, v3 - v1))
                total_area += area
        
        return total_area
    
    def _calculate_volume(self) -> float:
        """Calculate volume of 3D geometry"""
        # Simple tetrahedron-based volume calculation
        total_volume = 0.0
        
        for element in self.elements:
            if len(element) == 4:  # Tetrahedron
                v1, v2, v3, v4 = self.vertices[element]
                # Volume of tetrahedron
                volume = abs(np.dot(v4 - v1, np.cross(v2 - v1, v3 - v1))) / 6.0
                total_volume += volume
        
        return total_volume
    
    def add_boundary(self, name: str, boundary_data: Dict[str, Any]) -> None:
        """Add a boundary to the geometry"""
        self.boundaries[name] = boundary_data
    
    def add_region(self, name: str, region_data: Dict[str, Any]) -> None:
        """Add a material region to the geometry"""
        self.regions[name] = region_data
    
    def get_boundary_vertices(self, boundary_name: str) -> Optional[np.ndarray]:
        """Get vertices for a specific boundary"""
        if boundary_name in self.boundaries:
            boundary = self.boundaries[boundary_name]
            if 'vertex_indices' in boundary:
                indices = boundary['vertex_indices']
                return self.vertices[indices]
        return None
    
    def get_region_elements(self, region_name: str) -> Optional[np.ndarray]:
        """Get elements for a specific region"""
        if region_name in self.regions:
            region = self.regions[region_name]
            if 'element_indices' in region:
                indices = region['element_indices']
                return self.elements[indices]
        return None
    
    def transform(self, transformation_matrix: np.ndarray) -> None:
        """Apply transformation matrix to vertices"""
        if self.vertices is not None:
            # Apply transformation to vertices
            homogeneous_vertices = np.hstack([self.vertices, np.ones((self.vertices.shape[0], 1))])
            transformed_vertices = (transformation_matrix @ homogeneous_vertices.T).T
            self.vertices = transformed_vertices[:, :self.dimension]
    
    def scale(self, scale_factor: Union[float, np.ndarray]) -> None:
        """Scale geometry by factor"""
        if self.vertices is not None:
            if isinstance(scale_factor, (int, float)):
                scale_matrix = np.eye(self.dimension) * scale_factor
            else:
                scale_matrix = np.diag(scale_factor)
            
            self.vertices = self.vertices @ scale_matrix.T
    
    def translate(self, translation_vector: np.ndarray) -> None:
        """Translate geometry by vector"""
        if self.vertices is not None:
            self.vertices += translation_vector
    
    def rotate(self, rotation_matrix: np.ndarray) -> None:
        """Rotate geometry using rotation matrix"""
        if self.vertices is not None:
            self.vertices = self.vertices @ rotation_matrix.T
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert geometry to dictionary representation"""
        return {
            "name": self.name,
            "geometry_type": self.geometry_type,
            "dimension": self.dimension,
            "vertices": self.vertices.tolist() if self.vertices is not None else None,
            "elements": self.elements.tolist() if self.elements is not None else None,
            "element_types": self.element_types,
            "boundaries": self.boundaries,
            "regions": self.regions,
            "units": self.units,
            "file_path": self.file_path,
            "properties": self.properties
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Geometry':
        """Create geometry from dictionary representation"""
        # Convert lists back to numpy arrays
        if data.get('vertices') is not None:
            data['vertices'] = np.array(data['vertices'])
        if data.get('elements') is not None:
            data['elements'] = np.array(data['elements'])
        
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert geometry to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Geometry':
        """Create geometry from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def save_to_file(self, file_path: str) -> None:
        """Save geometry to file"""
        file_path = Path(file_path)
        
        if file_path.suffix.lower() == '.json':
            with open(file_path, 'w') as f:
                f.write(self.to_json())
        else:
            # For other formats, save as JSON with custom extension
            json_path = file_path.with_suffix('.json')
            with open(json_path, 'w') as f:
                f.write(self.to_json())
        
        logger.info(f"Geometry saved to {file_path}")
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'Geometry':
        """Load geometry from file"""
        file_path = Path(file_path)
        
        if file_path.suffix.lower() == '.json':
            with open(file_path, 'r') as f:
                data = json.load(f)
        else:
            # Try to load as JSON regardless of extension
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
            except:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        geometry = cls.from_dict(data)
        geometry.file_path = str(file_path)
        return geometry
    
    def __str__(self) -> str:
        return f"Geometry({self.name}, type={self.geometry_type}, dim={self.dimension})"
    
    def __repr__(self) -> str:
        return f"Geometry(name='{self.name}', geometry_type='{self.geometry_type}', dimension={self.dimension})"
    
    def copy(self) -> 'Geometry':
        """Create a deep copy of the geometry"""
        return copy.deepcopy(self)
    
    def __eq__(self, other: object) -> bool:
        """Compare geometries for equality"""
        if not isinstance(other, Geometry):
            return False
        
        # Compare basic attributes
        if (self.name != other.name or 
            self.geometry_type != other.geometry_type or
            self.dimension != other.dimension or
            self.units != other.units or
            self.file_path != other.file_path or
            self.properties != other.properties or
            self.boundaries != other.boundaries or
            self.regions != other.regions):
            return False
        
        # Compare numpy arrays
        if self.vertices is not None and other.vertices is not None:
            if not np.array_equal(self.vertices, other.vertices):
                return False
        elif self.vertices != other.vertices:
            return False
        
        if self.elements is not None and other.elements is not None:
            if not np.array_equal(self.elements, other.elements):
                return False
        elif self.elements != other.elements:
            return False
        
        # Compare element types
        if self.element_types != other.element_types:
            return False
        
        return True


# Geometry creation utilities
class GeometryUtils:
    """Utility functions for creating common geometries"""
    
    @staticmethod
    def create_cube(name: str = "cube", size: float = 1.0, center: np.ndarray = None) -> Geometry:
        """Create a cube geometry"""
        if center is None:
            center = np.array([0.0, 0.0, 0.0])
        
        # Define vertices
        half_size = size / 2.0
        vertices = np.array([
            [-half_size, -half_size, -half_size],  # 0
            [ half_size, -half_size, -half_size],  # 1
            [ half_size,  half_size, -half_size],  # 2
            [-half_size,  half_size, -half_size],  # 3
            [-half_size, -half_size,  half_size],  # 4
            [ half_size, -half_size,  half_size],  # 5
            [ half_size,  half_size,  half_size],  # 6
            [-half_size,  half_size,  half_size],  # 7
        ]) + center
        
        # Define elements (tetrahedra)
        elements = np.array([
            [0, 1, 2, 4],  # tet 1
            [1, 2, 5, 4],  # tet 2
            [2, 6, 5, 4],  # tet 3
            [2, 3, 6, 4],  # tet 4
            [2, 3, 6, 7],  # tet 5
        ])
        
        element_types = ["tet"] * len(elements)
        
        # Define boundaries
        boundaries = {
            "bottom": {"vertex_indices": [0, 1, 2, 3]},
            "top": {"vertex_indices": [4, 5, 6, 7]},
            "front": {"vertex_indices": [0, 1, 5, 4]},
            "back": {"vertex_indices": [2, 3, 7, 6]},
            "left": {"vertex_indices": [0, 3, 7, 4]},
            "right": {"vertex_indices": [1, 2, 6, 5]},
        }
        
        return Geometry(
            name=name,
            geometry_type="mesh",
            dimension=3,
            vertices=vertices,
            elements=elements,
            element_types=element_types,
            boundaries=boundaries
        )
    
    @staticmethod
    def create_sphere(name: str = "sphere", radius: float = 1.0, center: np.ndarray = None, 
                     resolution: int = 8) -> Geometry:
        """Create a sphere geometry using icosahedron subdivision"""
        if center is None:
            center = np.array([0.0, 0.0, 0.0])
        
        # Create icosahedron vertices
        phi = (1.0 + np.sqrt(5.0)) / 2.0
        vertices = np.array([
            [0, 1, phi], [0, -1, phi], [0, 1, -phi], [0, -1, -phi],
            [1, phi, 0], [-1, phi, 0], [1, -phi, 0], [-1, -phi, 0],
            [phi, 0, 1], [-phi, 0, 1], [phi, 0, -1], [-phi, 0, -1]
        ])
        
        # Normalize to unit sphere
        vertices = vertices / np.linalg.norm(vertices, axis=1, keepdims=True)
        
        # Scale by radius and translate
        vertices = vertices * radius + center
        
        # Create icosahedron faces (triangles)
        elements = np.array([
            [0, 1, 2], [0, 2, 4], [0, 4, 8], [0, 8, 1],
            [1, 8, 5], [1, 5, 2], [2, 5, 6], [2, 6, 4],
            [4, 6, 9], [4, 9, 8], [8, 9, 5], [5, 9, 6],
            [3, 7, 10], [3, 10, 11], [3, 11, 7],
            [7, 11, 6], [7, 6, 10], [10, 6, 9], [10, 9, 11],
            [11, 9, 5], [11, 5, 7], [7, 5, 6]
        ])
        
        element_types = ["tri"] * len(elements)
        
        return Geometry(
            name=name,
            geometry_type="mesh",
            dimension=3,
            vertices=vertices,
            elements=elements,
            element_types=element_types
        )
    
    @staticmethod
    def create_cylinder(name: str = "cylinder", radius: float = 1.0, height: float = 2.0,
                       center: np.ndarray = None, resolution: int = 16) -> Geometry:
        """Create a cylinder geometry"""
        if center is None:
            center = np.array([0.0, 0.0, 0.0])
        
        # Create vertices for top and bottom circles
        angles = np.linspace(0, 2*np.pi, resolution, endpoint=False)
        
        # Bottom circle
        bottom_vertices = np.column_stack([
            radius * np.cos(angles),
            radius * np.sin(angles),
            np.full(resolution, -height/2)
        ])
        
        # Top circle
        top_vertices = np.column_stack([
            radius * np.cos(angles),
            radius * np.sin(angles),
            np.full(resolution, height/2)
        ])
        
        # Center points
        bottom_center = np.array([0, 0, -height/2])
        top_center = np.array([0, 0, height/2])
        
        # Combine all vertices
        vertices = np.vstack([bottom_center, bottom_vertices, top_vertices, top_center])
        vertices += center
        
        # Create triangular elements
        elements = []
        
        # Bottom face triangles
        for i in range(resolution):
            elements.append([0, 1 + i, 1 + ((i + 1) % resolution)])
        
        # Top face triangles
        top_start = 1 + resolution
        for i in range(resolution):
            elements.append([len(vertices) - 1, top_start + i, top_start + ((i + 1) % resolution)])
        
        # Side triangles
        for i in range(resolution):
            next_i = (i + 1) % resolution
            # First triangle
            elements.append([1 + i, 1 + next_i, top_start + i])
            # Second triangle
            elements.append([1 + next_i, top_start + next_i, top_start + i])
        
        elements = np.array(elements)
        element_types = ["tri"] * len(elements)
        
        return Geometry(
            name=name,
            geometry_type="mesh",
            dimension=3,
            vertices=vertices,
            elements=elements,
            element_types=element_types
        )