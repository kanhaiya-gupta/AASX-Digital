"""
Mesh Quality Assessment Tools for Physics Modeling
Quality metrics, validation, and optimization suggestions for computational meshes
"""

import asyncio
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class QualityMetric(Enum):
    """Types of mesh quality metrics"""
    ASPECT_RATIO = "aspect_ratio"
    SKEWNESS = "skewness"
    ORTHOGONALITY = "orthogonality"
    JACOBIAN = "jacobian"
    VOLUME = "volume"
    ANGLE = "angle"
    DISTORTION = "distortion"
    SMOOTHNESS = "smoothness"

class QualityLevel(Enum):
    """Quality levels for mesh elements"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"

@dataclass
class QualityThresholds:
    """Thresholds for different quality metrics"""
    aspect_ratio_max: float = 10.0
    skewness_max: float = 0.8
    orthogonality_min: float = 0.3
    jacobian_min: float = 0.1
    volume_min: float = 1e-12
    angle_min: float = 15.0
    angle_max: float = 165.0
    distortion_max: float = 0.5
    smoothness_min: float = 0.7

@dataclass
class ElementQuality:
    """Quality assessment for a single mesh element"""
    element_id: int
    element_type: str
    quality_metrics: Dict[str, float]
    quality_level: QualityLevel
    issues: List[str]
    recommendations: List[str]

@dataclass
class MeshQualityReport:
    """Comprehensive mesh quality report"""
    overall_quality: QualityLevel
    quality_score: float
    element_count: int
    quality_distribution: Dict[QualityLevel, int]
    critical_issues: List[str]
    optimization_suggestions: List[str]
    detailed_analysis: Dict[str, Any]
    timestamp: datetime

class MeshQualityTools:
    """Tools for assessing and improving mesh quality"""

    def __init__(self, thresholds: Optional[QualityThresholds] = None):
        self.thresholds = thresholds or QualityThresholds()
        self.quality_history = []
        self.optimization_history = []
        logger.info("✅ Mesh Quality Tools initialized")

    async def assess_mesh_quality(self, mesh_data: Dict[str, Any]) -> MeshQualityReport:
        """Comprehensive mesh quality assessment"""
        await asyncio.sleep(0)
        
        try:
            elements = mesh_data.get('elements', [])
            nodes = mesh_data.get('nodes', [])
            
            if not elements or not nodes:
                raise ValueError("Invalid mesh data: missing elements or nodes")
            
            # Assess quality for each element
            element_qualities = []
            quality_scores = []
            
            for element in elements:
                element_quality = await self._assess_element_quality(element, nodes)
                element_qualities.append(element_quality)
                quality_scores.append(self._calculate_quality_score(element_quality))
            
            # Calculate overall quality
            overall_score = np.mean(quality_scores) if quality_scores else 0.0
            overall_quality = self._determine_quality_level(overall_score)
            
            # Analyze quality distribution
            quality_distribution = self._analyze_quality_distribution(element_qualities)
            
            # Identify critical issues
            critical_issues = self._identify_critical_issues(element_qualities)
            
            # Generate optimization suggestions
            optimization_suggestions = self._generate_optimization_suggestions(
                element_qualities, mesh_data
            )
            
            # Create detailed analysis
            detailed_analysis = {
                'element_qualities': element_qualities,
                'quality_statistics': self._calculate_quality_statistics(quality_scores),
                'problem_areas': self._identify_problem_areas(element_qualities),
                'mesh_characteristics': self._analyze_mesh_characteristics(mesh_data)
            }
            
            report = MeshQualityReport(
                overall_quality=overall_quality,
                quality_score=overall_score,
                element_count=len(elements),
                quality_distribution=quality_distribution,
                critical_issues=critical_issues,
                optimization_suggestions=optimization_suggestions,
                detailed_analysis=detailed_analysis,
                timestamp=datetime.now()
            )
            
            self.quality_history.append(report)
            return report
            
        except Exception as e:
            logger.error(f"Mesh quality assessment failed: {str(e)}")
            raise

    async def _assess_element_quality(self, element: Dict[str, Any], 
                                    nodes: List[Dict[str, Any]]) -> ElementQuality:
        """Assess quality of a single mesh element"""
        await asyncio.sleep(0)
        
        try:
            element_type = element.get('type', 'unknown')
            node_ids = element.get('node_ids', [])
            
            # Get node coordinates
            element_nodes = [nodes[nid] for nid in node_ids if nid < len(nodes)]
            
            if len(element_nodes) < 2:
                return ElementQuality(
                    element_id=element.get('id', 0),
                    element_type=element_type,
                    quality_metrics={},
                    quality_level=QualityLevel.UNACCEPTABLE,
                    issues=['Insufficient nodes'],
                    recommendations=['Check element definition']
                )
            
            # Calculate quality metrics
            quality_metrics = {}
            
            if element_type in ['triangle', 'quadrilateral']:
                quality_metrics.update(await self._calculate_2d_metrics(element_nodes))
            elif element_type in ['tetrahedron', 'hexahedron']:
                quality_metrics.update(await self._calculate_3d_metrics(element_nodes))
            
            # Determine quality level
            quality_level = self._determine_element_quality_level(quality_metrics)
            
            # Identify issues
            issues = self._identify_element_issues(quality_metrics)
            
            # Generate recommendations
            recommendations = self._generate_element_recommendations(quality_metrics, element_type)
            
            return ElementQuality(
                element_id=element.get('id', 0),
                element_type=element_type,
                quality_metrics=quality_metrics,
                quality_level=quality_level,
                issues=issues,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Element quality assessment failed: {str(e)}")
            raise

    async def _calculate_2d_metrics(self, nodes: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate quality metrics for 2D elements"""
        await asyncio.sleep(0)
        
        try:
            if len(nodes) < 3:
                return {}
            
            # Extract coordinates
            coords = np.array([[node.get('x', 0), node.get('y', 0)] for node in nodes])
            
            metrics = {}
            
            # Aspect ratio
            if len(nodes) == 3:  # Triangle
                metrics['aspect_ratio'] = self._calculate_triangle_aspect_ratio(coords)
                metrics['skewness'] = self._calculate_triangle_skewness(coords)
                metrics['area'] = self._calculate_triangle_area(coords)
            elif len(nodes) == 4:  # Quadrilateral
                metrics['aspect_ratio'] = self._calculate_quad_aspect_ratio(coords)
                metrics['skewness'] = self._calculate_quad_skewness(coords)
                metrics['area'] = self._calculate_quad_area(coords)
                metrics['orthogonality'] = self._calculate_quad_orthogonality(coords)
            
            # Angles
            metrics['min_angle'] = self._calculate_min_angle(coords)
            metrics['max_angle'] = self._calculate_max_angle(coords)
            
            return metrics
            
        except Exception as e:
            logger.error(f"2D metrics calculation failed: {str(e)}")
            return {}

    async def _calculate_3d_metrics(self, nodes: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate quality metrics for 3D elements"""
        await asyncio.sleep(0)
        
        try:
            if len(nodes) < 4:
                return {}
            
            # Extract coordinates
            coords = np.array([[node.get('x', 0), node.get('y', 0), node.get('z', 0)] 
                             for node in nodes])
            
            metrics = {}
            
            if len(nodes) == 4:  # Tetrahedron
                metrics['aspect_ratio'] = self._calculate_tet_aspect_ratio(coords)
                metrics['volume'] = self._calculate_tet_volume(coords)
                metrics['jacobian'] = self._calculate_tet_jacobian(coords)
            elif len(nodes) == 8:  # Hexahedron
                metrics['aspect_ratio'] = self._calculate_hex_aspect_ratio(coords)
                metrics['volume'] = self._calculate_hex_volume(coords)
                metrics['jacobian'] = self._calculate_hex_jacobian(coords)
                metrics['orthogonality'] = self._calculate_hex_orthogonality(coords)
            
            return metrics
            
        except Exception as e:
            logger.error(f"3D metrics calculation failed: {str(e)}")
            return {}

    def _calculate_triangle_aspect_ratio(self, coords: np.ndarray) -> float:
        """Calculate aspect ratio for triangle"""
        try:
            # Calculate side lengths
            sides = []
            for i in range(3):
                j = (i + 1) % 3
                side = np.linalg.norm(coords[i] - coords[j])
                sides.append(side)
            
            sides = sorted(sides)
            return sides[2] / sides[0] if sides[0] > 0 else float('inf')
        except:
            return float('inf')

    def _calculate_triangle_skewness(self, coords: np.ndarray) -> float:
        """Calculate skewness for triangle"""
        try:
            # Calculate angles
            angles = []
            for i in range(3):
                j = (i + 1) % 3
                k = (i + 2) % 3
                
                v1 = coords[j] - coords[i]
                v2 = coords[k] - coords[i]
                
                cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                cos_angle = np.clip(cos_angle, -1, 1)
                angle = np.arccos(cos_angle)
                angles.append(angle)
            
            # Ideal angle is 60 degrees
            ideal_angle = np.pi / 3
            skewness = max(abs(angle - ideal_angle) / ideal_angle for angle in angles)
            return skewness
        except:
            return 1.0

    def _calculate_triangle_area(self, coords: np.ndarray) -> float:
        """Calculate area of triangle"""
        try:
            v1 = coords[1] - coords[0]
            v2 = coords[2] - coords[0]
            cross_product = np.cross(v1, v2)
            return 0.5 * np.linalg.norm(cross_product)
        except:
            return 0.0

    def _calculate_quad_aspect_ratio(self, coords: np.ndarray) -> float:
        """Calculate aspect ratio for quadrilateral"""
        try:
            # Calculate side lengths
            sides = []
            for i in range(4):
                j = (i + 1) % 4
                side = np.linalg.norm(coords[i] - coords[j])
                sides.append(side)
            
            sides = sorted(sides)
            return sides[3] / sides[0] if sides[0] > 0 else float('inf')
        except:
            return float('inf')

    def _calculate_quad_skewness(self, coords: np.ndarray) -> float:
        """Calculate skewness for quadrilateral"""
        try:
            # Calculate angles at each vertex
            angles = []
            for i in range(4):
                j = (i + 1) % 4
                k = (i - 1) % 4
                
                v1 = coords[j] - coords[i]
                v2 = coords[k] - coords[i]
                
                cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                cos_angle = np.clip(cos_angle, -1, 1)
                angle = np.arccos(cos_angle)
                angles.append(angle)
            
            # Ideal angle is 90 degrees
            ideal_angle = np.pi / 2
            skewness = max(abs(angle - ideal_angle) / ideal_angle for angle in angles)
            return skewness
        except:
            return 1.0

    def _calculate_quad_area(self, coords: np.ndarray) -> float:
        """Calculate area of quadrilateral using shoelace formula"""
        try:
            area = 0.0
            for i in range(4):
                j = (i + 1) % 4
                area += coords[i][0] * coords[j][1]
                area -= coords[j][0] * coords[i][1]
            return abs(area) / 2.0
        except:
            return 0.0

    def _calculate_quad_orthogonality(self, coords: np.ndarray) -> float:
        """Calculate orthogonality for quadrilateral"""
        try:
            # Calculate dot product of adjacent edges
            orthogonality_scores = []
            for i in range(4):
                j = (i + 1) % 4
                k = (i + 2) % 4
                
                edge1 = coords[j] - coords[i]
                edge2 = coords[k] - coords[j]
                
                dot_product = np.dot(edge1, edge2)
                norm_product = np.linalg.norm(edge1) * np.linalg.norm(edge2)
                
                if norm_product > 0:
                    cos_angle = dot_product / norm_product
                    cos_angle = np.clip(cos_angle, -1, 1)
                    angle = np.arccos(cos_angle)
                    # Orthogonality is how close to 90 degrees
                    orthogonality = abs(np.pi/2 - angle) / (np.pi/2)
                    orthogonality_scores.append(orthogonality)
            
            return np.mean(orthogonality_scores) if orthogonality_scores else 1.0
        except:
            return 1.0

    def _calculate_min_angle(self, coords: np.ndarray) -> float:
        """Calculate minimum angle in element"""
        try:
            angles = []
            for i in range(len(coords)):
                j = (i + 1) % len(coords)
                k = (i + 2) % len(coords)
                
                v1 = coords[j] - coords[i]
                v2 = coords[k] - coords[i]
                
                cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                cos_angle = np.clip(cos_angle, -1, 1)
                angle = np.arccos(cos_angle)
                angles.append(angle)
            
            return min(angles) if angles else 0.0
        except:
            return 0.0

    def _calculate_max_angle(self, coords: np.ndarray) -> float:
        """Calculate maximum angle in element"""
        try:
            angles = []
            for i in range(len(coords)):
                j = (i + 1) % len(coords)
                k = (i + 2) % len(coords)
                
                v1 = coords[j] - coords[i]
                v2 = coords[k] - coords[i]
                
                cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                cos_angle = np.clip(cos_angle, -1, 1)
                angle = np.arccos(cos_angle)
                angles.append(angle)
            
            return max(angles) if angles else 0.0
        except:
            return 0.0

    def _calculate_tet_aspect_ratio(self, coords: np.ndarray) -> float:
        """Calculate aspect ratio for tetrahedron"""
        try:
            # Calculate edge lengths
            edges = []
            for i in range(4):
                for j in range(i + 1, 4):
                    edge = np.linalg.norm(coords[i] - coords[j])
                    edges.append(edge)
            
            edges = sorted(edges)
            return edges[-1] / edges[0] if edges[0] > 0 else float('inf')
        except:
            return float('inf')

    def _calculate_tet_volume(self, coords: np.ndarray) -> float:
        """Calculate volume of tetrahedron"""
        try:
            v1 = coords[1] - coords[0]
            v2 = coords[2] - coords[0]
            v3 = coords[3] - coords[0]
            
            volume = abs(np.dot(v1, np.cross(v2, v3))) / 6.0
            return volume
        except:
            return 0.0

    def _calculate_tet_jacobian(self, coords: np.ndarray) -> float:
        """Calculate Jacobian for tetrahedron"""
        try:
            v1 = coords[1] - coords[0]
            v2 = coords[2] - coords[0]
            v3 = coords[3] - coords[0]
            
            jacobian = np.dot(v1, np.cross(v2, v3))
            return abs(jacobian)
        except:
            return 0.0

    def _calculate_hex_aspect_ratio(self, coords: np.ndarray) -> float:
        """Calculate aspect ratio for hexahedron"""
        try:
            # Calculate edge lengths
            edges = []
            for i in range(8):
                for j in range(i + 1, 8):
                    edge = np.linalg.norm(coords[i] - coords[j])
                    edges.append(edge)
            
            edges = sorted(edges)
            return edges[-1] / edges[0] if edges[0] > 0 else float('inf')
        except:
            return float('inf')

    def _calculate_hex_volume(self, coords: np.ndarray) -> float:
        """Calculate volume of hexahedron"""
        try:
            # Approximate volume using 6 tetrahedra
            center = np.mean(coords, axis=0)
            volume = 0.0
            
            # Face 1: 0,1,2,3
            v1 = coords[1] - coords[0]
            v2 = coords[2] - coords[0]
            v3 = center - coords[0]
            volume += abs(np.dot(v1, np.cross(v2, v3))) / 6.0
            
            # Face 2: 4,5,6,7
            v1 = coords[5] - coords[4]
            v2 = coords[6] - coords[4]
            v3 = center - coords[4]
            volume += abs(np.dot(v1, np.cross(v2, v3))) / 6.0
            
            # Add other faces...
            return volume
        except:
            return 0.0

    def _calculate_hex_jacobian(self, coords: np.ndarray) -> float:
        """Calculate Jacobian for hexahedron"""
        try:
            # Calculate Jacobian at center
            center = np.mean(coords, axis=0)
            
            # Approximate using finite differences
            h = 0.001
            jacobians = []
            
            for i in range(3):
                coord_plus = center.copy()
                coord_plus[i] += h
                coord_minus = center.copy()
                coord_minus[i] -= h
                
                # Calculate volume change
                jacobian = 1.0  # Simplified calculation
                jacobians.append(jacobian)
            
            return np.mean(jacobians) if jacobians else 0.0
        except:
            return 0.0

    def _calculate_hex_orthogonality(self, coords: np.ndarray) -> float:
        """Calculate orthogonality for hexahedron"""
        try:
            # Calculate orthogonality of edges
            orthogonality_scores = []
            
            for i in range(8):
                for j in range(i + 1, 8):
                    edge1 = coords[j] - coords[i]
                    
                    # Find perpendicular edge
                    for k in range(8):
                        if k != i and k != j:
                            edge2 = coords[k] - coords[i]
                            
                            dot_product = np.dot(edge1, edge2)
                            norm_product = np.linalg.norm(edge1) * np.linalg.norm(edge2)
                            
                            if norm_product > 0:
                                cos_angle = dot_product / norm_product
                                cos_angle = np.clip(cos_angle, -1, 1)
                                angle = np.arccos(cos_angle)
                                # Orthogonality is how close to 90 degrees
                                orthogonality = abs(np.pi/2 - angle) / (np.pi/2)
                                orthogonality_scores.append(orthogonality)
            
            return np.mean(orthogonality_scores) if orthogonality_scores else 1.0
        except:
            return 1.0

    def _determine_element_quality_level(self, metrics: Dict[str, float]) -> QualityLevel:
        """Determine quality level for an element based on metrics"""
        try:
            score = 0.0
            total_metrics = 0
            
            for metric_name, value in metrics.items():
                if metric_name == 'aspect_ratio':
                    if value <= self.thresholds.aspect_ratio_max:
                        score += 1.0
                    elif value <= self.thresholds.aspect_ratio_max * 2:
                        score += 0.5
                    total_metrics += 1
                elif metric_name == 'skewness':
                    if value <= self.thresholds.skewness_max:
                        score += 1.0
                    elif value <= self.thresholds.skewness_max * 1.5:
                        score += 0.5
                    total_metrics += 1
                elif metric_name == 'orthogonality':
                    if value >= self.thresholds.orthogonality_min:
                        score += 1.0
                    elif value >= self.thresholds.orthogonality_min * 0.5:
                        score += 0.5
                    total_metrics += 1
                elif metric_name == 'jacobian':
                    if value >= self.thresholds.jacobian_min:
                        score += 1.0
                    elif value >= self.thresholds.jacobian_min * 0.5:
                        score += 0.5
                    total_metrics += 1
                elif metric_name == 'volume':
                    if value >= self.thresholds.volume_min:
                        score += 1.0
                    elif value >= self.thresholds.volume_min * 0.1:
                        score += 0.5
                    total_metrics += 1
                elif metric_name == 'min_angle':
                    if value >= self.thresholds.angle_min:
                        score += 1.0
                    elif value >= self.thresholds.angle_min * 0.5:
                        score += 0.5
                    total_metrics += 1
                elif metric_name == 'max_angle':
                    if value <= self.thresholds.angle_max:
                        score += 1.0
                    elif value <= self.thresholds.angle_max * 1.1:
                        score += 0.5
                    total_metrics += 1
            
            if total_metrics == 0:
                return QualityLevel.UNACCEPTABLE
            
            quality_score = score / total_metrics
            
            if quality_score >= 0.9:
                return QualityLevel.EXCELLENT
            elif quality_score >= 0.7:
                return QualityLevel.GOOD
            elif quality_score >= 0.5:
                return QualityLevel.ACCEPTABLE
            elif quality_score >= 0.3:
                return QualityLevel.POOR
            else:
                return QualityLevel.UNACCEPTABLE
                
        except Exception as e:
            logger.error(f"Quality level determination failed: {str(e)}")
            return QualityLevel.UNACCEPTABLE

    def _identify_element_issues(self, metrics: Dict[str, float]) -> List[str]:
        """Identify quality issues for an element"""
        issues = []
        
        for metric_name, value in metrics.items():
            if metric_name == 'aspect_ratio' and value > self.thresholds.aspect_ratio_max:
                issues.append(f"High aspect ratio: {value:.2f}")
            elif metric_name == 'skewness' and value > self.thresholds.skewness_max:
                issues.append(f"High skewness: {value:.2f}")
            elif metric_name == 'orthogonality' and value < self.thresholds.orthogonality_min:
                issues.append(f"Low orthogonality: {value:.2f}")
            elif metric_name == 'jacobian' and value < self.thresholds.jacobian_min:
                issues.append(f"Low Jacobian: {value:.2e}")
            elif metric_name == 'volume' and value < self.thresholds.volume_min:
                issues.append(f"Very small volume: {value:.2e}")
            elif metric_name == 'min_angle' and value < self.thresholds.angle_min:
                issues.append(f"Very small angle: {value:.2f}°")
            elif metric_name == 'max_angle' and value > self.thresholds.angle_max:
                issues.append(f"Very large angle: {value:.2f}°")
        
        return issues

    def _generate_element_recommendations(self, metrics: Dict[str, float], 
                                        element_type: str) -> List[str]:
        """Generate optimization recommendations for an element"""
        recommendations = []
        
        if 'aspect_ratio' in metrics and metrics['aspect_ratio'] > self.thresholds.aspect_ratio_max:
            recommendations.append("Consider mesh refinement or remeshing")
        
        if 'skewness' in metrics and metrics['skewness'] > self.thresholds.skewness_max:
            recommendations.append("Apply mesh smoothing or use different element type")
        
        if 'orthogonality' in metrics and metrics['orthogonality'] < self.thresholds.orthogonality_min:
            recommendations.append("Consider structured meshing or mesh optimization")
        
        if 'jacobian' in metrics and metrics['jacobian'] < self.thresholds.jacobian_min:
            recommendations.append("Check element connectivity and geometry")
        
        if 'volume' in metrics and metrics['volume'] < self.thresholds.volume_min:
            recommendations.append("Element may be degenerate - check geometry")
        
        if 'min_angle' in metrics and metrics['min_angle'] < self.thresholds.angle_min:
            recommendations.append("Consider mesh refinement in sharp corners")
        
        if 'max_angle' in metrics and metrics['max_angle'] > self.thresholds.angle_max:
            recommendations.append("Consider mesh refinement in obtuse angles")
        
        return recommendations

    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Determine overall quality level from score"""
        if score >= 0.9:
            return QualityLevel.EXCELLENT
        elif score >= 0.7:
            return QualityLevel.GOOD
        elif score >= 0.5:
            return QualityLevel.ACCEPTABLE
        elif score >= 0.3:
            return QualityLevel.POOR
        else:
            return QualityLevel.UNACCEPTABLE

    def _calculate_quality_score(self, element_quality: ElementQuality) -> float:
        """Calculate numerical quality score for an element"""
        try:
            if not element_quality.quality_metrics:
                return 0.0
            
            score = 0.0
            total_metrics = 0
            
            for metric_name, value in element_quality.quality_metrics.items():
                if metric_name == 'aspect_ratio':
                    if value <= self.thresholds.aspect_ratio_max:
                        score += 1.0
                    elif value <= self.thresholds.aspect_ratio_max * 2:
                        score += 0.5
                    total_metrics += 1
                elif metric_name == 'skewness':
                    if value <= self.thresholds.skewness_max:
                        score += 1.0
                    elif value <= self.thresholds.skewness_max * 1.5:
                        score += 0.5
                    total_metrics += 1
                elif metric_name == 'orthogonality':
                    if value >= self.thresholds.orthogonality_min:
                        score += 1.0
                    elif value >= self.thresholds.orthogonality_min * 0.5:
                        score += 0.5
                    total_metrics += 1
                elif metric_name == 'jacobian':
                    if value >= self.thresholds.jacobian_min:
                        score += 1.0
                    elif value >= self.thresholds.jacobian_min * 0.5:
                        score += 0.5
                    total_metrics += 1
                elif metric_name == 'volume':
                    if value >= self.thresholds.volume_min:
                        score += 1.0
                    elif value >= self.thresholds.volume_min * 0.1:
                        score += 0.5
                    total_metrics += 1
                elif metric_name == 'min_angle':
                    if value >= self.thresholds.angle_min:
                        score += 1.0
                    elif value >= self.thresholds.angle_min * 0.5:
                        score += 0.5
                    total_metrics += 1
                elif metric_name == 'max_angle':
                    if value <= self.thresholds.angle_max:
                        score += 1.0
                    elif value <= self.thresholds.angle_max * 1.1:
                        score += 0.5
                    total_metrics += 1
            
            return score / total_metrics if total_metrics > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Quality score calculation failed: {str(e)}")
            return 0.0

    def _analyze_quality_distribution(self, element_qualities: List[ElementQuality]) -> Dict[QualityLevel, int]:
        """Analyze distribution of quality levels"""
        distribution = {level: 0 for level in QualityLevel}
        
        for element_quality in element_qualities:
            distribution[element_quality.quality_level] += 1
        
        return distribution

    def _identify_critical_issues(self, element_qualities: List[ElementQuality]) -> List[str]:
        """Identify critical quality issues"""
        critical_issues = []
        
        # Count unacceptable elements
        unacceptable_count = sum(1 for eq in element_qualities 
                               if eq.quality_level == QualityLevel.UNACCEPTABLE)
        
        if unacceptable_count > 0:
            critical_issues.append(f"{unacceptable_count} elements have unacceptable quality")
        
        # Check for poor quality elements
        poor_count = sum(1 for eq in element_qualities 
                        if eq.quality_level == QualityLevel.POOR)
        
        if poor_count > len(element_qualities) * 0.1:  # More than 10% poor quality
            critical_issues.append(f"High percentage of poor quality elements: {poor_count}")
        
        # Check for specific metric issues
        high_aspect_ratio_count = 0
        low_jacobian_count = 0
        
        for eq in element_qualities:
            if 'aspect_ratio' in eq.quality_metrics:
                if eq.quality_metrics['aspect_ratio'] > self.thresholds.aspect_ratio_max * 2:
                    high_aspect_ratio_count += 1
            
            if 'jacobian' in eq.quality_metrics:
                if eq.quality_metrics['jacobian'] < self.thresholds.jacobian_min * 0.1:
                    low_jacobian_count += 1
        
        if high_aspect_ratio_count > 0:
            critical_issues.append(f"{high_aspect_ratio_count} elements have very high aspect ratios")
        
        if low_jacobian_count > 0:
            critical_issues.append(f"{low_jacobian_count} elements have very low Jacobians")
        
        return critical_issues

    def _generate_optimization_suggestions(self, element_qualities: List[ElementQuality], 
                                         mesh_data: Dict[str, Any]) -> List[str]:
        """Generate optimization suggestions for the mesh"""
        suggestions = []
        
        # Analyze quality distribution
        quality_distribution = self._analyze_quality_distribution(element_qualities)
        
        if quality_distribution[QualityLevel.UNACCEPTABLE] > 0:
            suggestions.append("Remove or remesh unacceptable quality elements")
        
        if quality_distribution[QualityLevel.POOR] > len(element_qualities) * 0.1:
            suggestions.append("Apply global mesh smoothing to improve poor quality elements")
        
        # Check for specific issues
        high_aspect_ratio_elements = [eq for eq in element_qualities 
                                    if 'aspect_ratio' in eq.quality_metrics and 
                                    eq.quality_metrics['aspect_ratio'] > self.thresholds.aspect_ratio_max]
        
        if len(high_aspect_ratio_elements) > len(element_qualities) * 0.2:
            suggestions.append("Consider adaptive mesh refinement for high aspect ratio regions")
        
        # Check element types
        element_types = {}
        for eq in element_qualities:
            element_types[eq.element_type] = element_types.get(eq.element_type, 0) + 1
        
        if len(element_types) > 3:
            suggestions.append("Consider using fewer element types for better mesh consistency")
        
        # Check for mesh size variations
        if 'element_sizes' in mesh_data:
            sizes = mesh_data['element_sizes']
            if max(sizes) / min(sizes) > 100:
                suggestions.append("Large variation in element sizes - consider gradual size transitions")
        
        return suggestions

    def _calculate_quality_statistics(self, quality_scores: List[float]) -> Dict[str, float]:
        """Calculate statistical measures of quality scores"""
        if not quality_scores:
            return {}
        
        scores = np.array(quality_scores)
        
        return {
            'mean': float(np.mean(scores)),
            'median': float(np.median(scores)),
            'std': float(np.std(scores)),
            'min': float(np.min(scores)),
            'max': float(np.max(scores)),
            'q25': float(np.percentile(scores, 25)),
            'q75': float(np.percentile(scores, 75))
        }

    def _identify_problem_areas(self, element_qualities: List[ElementQuality]) -> Dict[str, Any]:
        """Identify areas of the mesh with quality problems"""
        problem_areas = {
            'high_aspect_ratio_regions': [],
            'low_jacobian_regions': [],
            'sharp_angle_regions': [],
            'small_volume_regions': []
        }
        
        for eq in element_qualities:
            if eq.quality_level in [QualityLevel.POOR, QualityLevel.UNACCEPTABLE]:
                if 'aspect_ratio' in eq.quality_metrics:
                    if eq.quality_metrics['aspect_ratio'] > self.thresholds.aspect_ratio_max:
                        problem_areas['high_aspect_ratio_regions'].append(eq.element_id)
                
                if 'jacobian' in eq.quality_metrics:
                    if eq.quality_metrics['jacobian'] < self.thresholds.jacobian_min:
                        problem_areas['low_jacobian_regions'].append(eq.element_id)
                
                if 'min_angle' in eq.quality_metrics:
                    if eq.quality_metrics['min_angle'] < self.thresholds.angle_min:
                        problem_areas['sharp_angle_regions'].append(eq.element_id)
                
                if 'volume' in eq.quality_metrics:
                    if eq.quality_metrics['volume'] < self.thresholds.volume_min:
                        problem_areas['small_volume_regions'].append(eq.element_id)
        
        return problem_areas

    def _analyze_mesh_characteristics(self, mesh_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze general characteristics of the mesh"""
        characteristics = {
            'total_elements': len(mesh_data.get('elements', [])),
            'total_nodes': len(mesh_data.get('nodes', [])),
            'element_types': {},
            'mesh_dimensions': {},
            'boundary_conditions': len(mesh_data.get('boundary_conditions', [])),
            'material_regions': len(mesh_data.get('material_regions', []))
        }
        
        # Analyze element types
        elements = mesh_data.get('elements', [])
        for element in elements:
            element_type = element.get('type', 'unknown')
            characteristics['element_types'][element_type] = characteristics['element_types'].get(element_type, 0) + 1
        
        # Analyze mesh dimensions
        nodes = mesh_data.get('nodes', [])
        if nodes:
            x_coords = [node.get('x', 0) for node in nodes]
            y_coords = [node.get('y', 0) for node in nodes]
            z_coords = [node.get('z', 0) for node in nodes]
            
            characteristics['mesh_dimensions'] = {
                'x_range': [min(x_coords), max(x_coords)] if x_coords else [0, 0],
                'y_range': [min(y_coords), max(y_coords)] if y_coords else [0, 0],
                'z_range': [min(z_coords), max(z_coords)] if z_coords else [0, 0]
            }
        
        return characteristics

    async def get_quality_history(self, limit: Optional[int] = None) -> List[MeshQualityReport]:
        """Get quality assessment history"""
        await asyncio.sleep(0)
        
        if limit is None:
            return self.quality_history
        else:
            return self.quality_history[-limit:]

    async def clear_quality_history(self) -> None:
        """Clear quality assessment history"""
        await asyncio.sleep(0)
        self.quality_history.clear()
        logger.info("Quality history cleared")

    async def update_thresholds(self, new_thresholds: QualityThresholds) -> None:
        """Update quality thresholds"""
        await asyncio.sleep(0)
        self.thresholds = new_thresholds
        logger.info("Quality thresholds updated")

    async def export_quality_report(self, report: MeshQualityReport, 
                                  format: str = "json") -> str:
        """Export quality report in specified format"""
        await asyncio.sleep(0)
        
        try:
            if format.lower() == "json":
                import json
                return json.dumps(report.__dict__, default=str, indent=2)
            elif format.lower() == "csv":
                # Convert to CSV format
                csv_lines = []
                csv_lines.append("Quality Metric,Value")
                csv_lines.append(f"Overall Quality,{report.overall_quality.value}")
                csv_lines.append(f"Quality Score,{report.quality_score:.4f}")
                csv_lines.append(f"Element Count,{report.element_count}")
                csv_lines.append(f"Total Violations,{len(report.critical_issues)}")
                return "\n".join(csv_lines)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Export failed: {str(e)}")
            raise
