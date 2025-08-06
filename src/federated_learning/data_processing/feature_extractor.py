"""
Feature Extractor
================

Extract features from AASX data for federated learning.
"""

from typing import Dict, Any, List, Optional
import logging
import json
import re

logger = logging.getLogger(__name__)

class FeatureExtractor:
    """Extract features from AASX data for federated learning"""
    
    def __init__(self):
        self.data_validator = DataValidator()
        self.logger = logger
    
    def extract_features(self, aasx_data: Dict[str, Any]) -> List[float]:
        """Extract features from any AASX data structure"""
        try:
            self.logger.info("Extracting features from AASX data")
            
            features = []
            
            # Extract from JSON data
            if 'json' in aasx_data:
                json_features = self.extract_from_json(aasx_data['json'])
                features.extend(json_features)
            
            # Extract from graph data
            if 'graph' in aasx_data:
                graph_features = self.extract_from_graph(aasx_data['graph'])
                features.extend(graph_features)
            
            # Extract from RDF data
            if 'rdf' in aasx_data:
                rdf_features = self.extract_from_rdf(aasx_data['rdf'])
                features.extend(rdf_features)
            
            # Validate extracted features
            if self.data_validator.validate_features(features):
                self.logger.info(f"Successfully extracted {len(features)} features")
                return features
            else:
                self.logger.warning("Feature validation failed, returning empty list")
                return []
                
        except Exception as e:
            self.logger.error(f"Error extracting features: {str(e)}")
            return []
    
    def extract_from_json(self, json_data: Dict[str, Any]) -> List[float]:
        """Extract features from structured JSON data"""
        try:
            features = []
            
            # Extract numeric features
            numeric_features = self._extract_numeric_features(json_data)
            features.extend(numeric_features)
            
            # Extract categorical features
            categorical_features = self._extract_categorical_features(json_data)
            features.extend(categorical_features)
            
            # Extract structural features
            structural_features = self._extract_structural_features(json_data)
            features.extend(structural_features)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Error extracting features from JSON: {str(e)}")
            return []
    
    def extract_from_graph(self, graph_data: Dict[str, Any]) -> List[float]:
        """Extract features from graph data"""
        try:
            features = []
            
            # Extract graph topology features
            topology_features = self._extract_graph_topology_features(graph_data)
            features.extend(topology_features)
            
            # Extract node features
            node_features = self._extract_node_features(graph_data)
            features.extend(node_features)
            
            # Extract edge features
            edge_features = self._extract_edge_features(graph_data)
            features.extend(edge_features)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Error extracting features from graph: {str(e)}")
            return []
    
    def extract_from_rdf(self, rdf_data: str) -> List[float]:
        """Extract features from RDF data"""
        try:
            features = []
            
            # Extract RDF structure features
            structure_features = self._extract_rdf_structure_features(rdf_data)
            features.extend(structure_features)
            
            # Extract semantic features
            semantic_features = self._extract_semantic_features(rdf_data)
            features.extend(semantic_features)
            
            # Extract ontology features
            ontology_features = self._extract_ontology_features(rdf_data)
            features.extend(ontology_features)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Error extracting features from RDF: {str(e)}")
            return []
    
    def _extract_numeric_features(self, data: Any) -> List[float]:
        """Extract numeric features from data"""
        features = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (int, float)):
                    features.append(float(value))
                elif isinstance(value, dict):
                    features.extend(self._extract_numeric_features(value))
                elif isinstance(value, list):
                    features.extend(self._extract_numeric_features(value))
        
        elif isinstance(data, list):
            for item in data:
                features.extend(self._extract_numeric_features(item))
        
        return features
    
    def _extract_categorical_features(self, data: Any) -> List[float]:
        """Extract categorical features from data"""
        features = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    # Convert string to numeric feature using hash
                    hash_value = hash(value) % 1000  # Normalize to 0-999
                    features.append(float(hash_value))
                elif isinstance(value, dict):
                    features.extend(self._extract_categorical_features(value))
                elif isinstance(value, list):
                    features.extend(self._extract_categorical_features(value))
        
        elif isinstance(data, list):
            for item in data:
                features.extend(self._extract_categorical_features(item))
        
        return features
    
    def _extract_structural_features(self, data: Any) -> List[float]:
        """Extract structural features from data"""
        features = []
        
        if isinstance(data, dict):
            # Number of keys
            features.append(float(len(data)))
            
            # Average key length
            if data:
                avg_key_length = sum(len(str(key)) for key in data.keys()) / len(data)
                features.append(avg_key_length)
            
            # Recursively extract from nested structures
            for value in data.values():
                features.extend(self._extract_structural_features(value))
        
        elif isinstance(data, list):
            # List length
            features.append(float(len(data)))
            
            # Recursively extract from list items
            for item in data:
                features.extend(self._extract_structural_features(item))
        
        return features
    
    def _extract_graph_topology_features(self, graph_data: Dict[str, Any]) -> List[float]:
        """Extract graph topology features"""
        features = []
        
        try:
            # Number of nodes
            nodes = graph_data.get('nodes', [])
            features.append(float(len(nodes)))
            
            # Number of edges
            edges = graph_data.get('edges', [])
            features.append(float(len(edges)))
            
            # Graph density
            if len(nodes) > 1:
                max_edges = len(nodes) * (len(nodes) - 1) / 2
                density = len(edges) / max_edges if max_edges > 0 else 0
                features.append(density)
            else:
                features.append(0.0)
            
            # Average node degree
            if nodes and edges:
                total_degree = sum(len(edge.get('source', [])) + len(edge.get('target', [])) for edge in edges)
                avg_degree = total_degree / len(nodes)
                features.append(avg_degree)
            else:
                features.append(0.0)
            
        except Exception as e:
            self.logger.error(f"Error extracting graph topology features: {str(e)}")
            features.extend([0.0, 0.0, 0.0, 0.0])
        
        return features
    
    def _extract_node_features(self, graph_data: Dict[str, Any]) -> List[float]:
        """Extract node features from graph"""
        features = []
        
        try:
            nodes = graph_data.get('nodes', [])
            
            if nodes:
                # Average node properties
                node_properties = []
                for node in nodes:
                    if isinstance(node, dict):
                        node_properties.append(len(node))
                
                if node_properties:
                    features.append(float(sum(node_properties) / len(node_properties)))
                else:
                    features.append(0.0)
                
                # Node type distribution
                node_types = {}
                for node in nodes:
                    if isinstance(node, dict):
                        node_type = node.get('type', 'unknown')
                        node_types[node_type] = node_types.get(node_type, 0) + 1
                
                features.append(float(len(node_types)))
                
            else:
                features.extend([0.0, 0.0])
            
        except Exception as e:
            self.logger.error(f"Error extracting node features: {str(e)}")
            features.extend([0.0, 0.0])
        
        return features
    
    def _extract_edge_features(self, graph_data: Dict[str, Any]) -> List[float]:
        """Extract edge features from graph"""
        features = []
        
        try:
            edges = graph_data.get('edges', [])
            
            if edges:
                # Average edge properties
                edge_properties = []
                for edge in edges:
                    if isinstance(edge, dict):
                        edge_properties.append(len(edge))
                
                if edge_properties:
                    features.append(float(sum(edge_properties) / len(edge_properties)))
                else:
                    features.append(0.0)
                
                # Edge type distribution
                edge_types = {}
                for edge in edges:
                    if isinstance(edge, dict):
                        edge_type = edge.get('type', 'unknown')
                        edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
                
                features.append(float(len(edge_types)))
                
            else:
                features.extend([0.0, 0.0])
            
        except Exception as e:
            self.logger.error(f"Error extracting edge features: {str(e)}")
            features.extend([0.0, 0.0])
        
        return features
    
    def _extract_rdf_structure_features(self, rdf_data: str) -> List[float]:
        """Extract RDF structure features"""
        features = []
        
        try:
            # Count triples
            triple_count = len(re.findall(r'<[^>]+>\s+<[^>]+>\s+<[^>]+>', rdf_data))
            features.append(float(triple_count))
            
            # Count subjects
            subjects = set(re.findall(r'<([^>]+)>\s+<[^>]+>\s+<[^>]+>', rdf_data))
            features.append(float(len(subjects)))
            
            # Count predicates
            predicates = set(re.findall(r'<[^>]+>\s+<([^>]+)>\s+<[^>]+>', rdf_data))
            features.append(float(len(predicates)))
            
            # Count objects
            objects = set(re.findall(r'<[^>]+>\s+<[^>]+>\s+<([^>]+)>', rdf_data))
            features.append(float(len(objects)))
            
        except Exception as e:
            self.logger.error(f"Error extracting RDF structure features: {str(e)}")
            features.extend([0.0, 0.0, 0.0, 0.0])
        
        return features
    
    def _extract_semantic_features(self, rdf_data: str) -> List[float]:
        """Extract semantic features from RDF"""
        features = []
        
        try:
            # Count different namespaces
            namespaces = set(re.findall(r'xmlns:(\w+)', rdf_data))
            features.append(float(len(namespaces)))
            
            # Count literal values
            literal_count = len(re.findall(r'"[^"]*"', rdf_data))
            features.append(float(literal_count))
            
            # Count blank nodes
            blank_node_count = len(re.findall(r'_:', rdf_data))
            features.append(float(blank_node_count))
            
        except Exception as e:
            self.logger.error(f"Error extracting semantic features: {str(e)}")
            features.extend([0.0, 0.0, 0.0])
        
        return features
    
    def _extract_ontology_features(self, rdf_data: str) -> List[float]:
        """Extract ontology features from RDF"""
        features = []
        
        try:
            # Count class definitions
            class_count = len(re.findall(r'rdf:type.*owl:Class', rdf_data, re.IGNORECASE))
            features.append(float(class_count))
            
            # Count property definitions
            property_count = len(re.findall(r'rdf:type.*owl:(ObjectProperty|DatatypeProperty)', rdf_data, re.IGNORECASE))
            features.append(float(property_count))
            
            # Count subclass relationships
            subclass_count = len(re.findall(r'rdfs:subClassOf', rdf_data, re.IGNORECASE))
            features.append(float(subclass_count))
            
        except Exception as e:
            self.logger.error(f"Error extracting ontology features: {str(e)}")
            features.extend([0.0, 0.0, 0.0])
        
        return features 