"""
Graph data processor for graph JSON files.
"""

import json
from pathlib import Path
from typing import Dict, Any
from .base_processor import BaseDataProcessor


class GraphDataProcessor(BaseDataProcessor):
    """Processor for graph data files."""
    
    def can_process(self, file_path: Path) -> bool:
        """Check if this processor can handle the given file."""
        return file_path.suffix.lower() == '.json' and '_graph' in file_path.name
    
    def process(self, project_id: str, file_info: Dict[str, Any], file_path: Path) -> Dict[str, Any]:
        """Process graph data file."""
        try:
            self.logger.info(f"Processing graph data file: {file_path}")
            
            # Load graph data
            with open(file_path, 'r', encoding='utf-8') as f:
                graph_data = json.load(f)
            
            # Extract meaningful text from graph data
            text_content = self._extract_text_from_graph_data(graph_data)
            
            self.logger.info(f"Extracted graph text content: {text_content[:100]}...")
            
            if not text_content:
                return self._create_skipped_result(file_info, file_path, "No extractable text content from graph")
            
            # Generate embedding
            embedding = self._generate_embedding(text_content, file_path)
            if not embedding:
                return self._create_error_result(file_info, file_path, "Failed to generate embedding for graph")
            
            # Prepare metadata
            metadata = {
                'project_id': project_id,
                'file_id': file_info.get('file_id'),
                'source_file': file_path.name,
                'content_type': 'graph_data',
                'content_preview': text_content[:200] + "..." if len(text_content) > 200 else text_content,
                'file_path': str(file_path),
                'embedding_model': self.text_embedding_manager.get_model().get_model_info() if self.text_embedding_manager else None,
                'graph_nodes_count': len(graph_data.get('nodes', [])),
                'graph_edges_count': len(graph_data.get('edges', []))
            }
            
            # Upload to vector database
            success = self._upload_to_vector_db(embedding, metadata, file_path)
            if not success:
                return self._create_error_result(file_info, file_path, "Failed to upload graph to vector database")
            
            # Save embedding locally
            vector_data = {
                'id': self.vector_db.generate_vector_id(project_id, file_path.name),
                'vector': embedding,
                'payload': metadata
            }
            self._save_embedding_locally(project_id, file_path, vector_data)
            
            return self._create_success_result(file_info, file_path, vector_data['id'])
            
        except Exception as e:
            self.logger.error(f"Exception processing graph {file_path}: {e}")
            return self._create_error_result(file_info, file_path, str(e))
    
    def _extract_text_from_graph_data(self, graph_data: Dict[str, Any]) -> str:
        """Extract meaningful text from graph data."""
        text_parts = []
        
        # Extract from nodes
        if 'nodes' in graph_data:
            for node in graph_data['nodes']:
                node_text = f"Node: {node.get('idShort', node.get('id', ''))}"
                if node.get('type'):
                    node_text += f" (Type: {node['type']})"
                if node.get('category'):
                    node_text += f" (Category: {node['category']})"
                if node.get('kind'):
                    node_text += f" (Kind: {node['kind']})"
                if node.get('description'):
                    node_text += f" - {node['description']}"
                text_parts.append(node_text)
        
        # Extract from edges
        if 'edges' in graph_data:
            for edge in graph_data['edges']:
                edge_text = f"Relationship: {edge.get('relationship_type', edge.get('type', ''))}"
                if edge.get('source') and edge.get('target'):
                    edge_text += f" from {edge['source']} to {edge['target']}"
                text_parts.append(edge_text)
        
        # If no meaningful content found, create a basic description
        if not text_parts:
            text_parts.append("AASX Digital Twin Graph Structure")
            if 'nodes' in graph_data and graph_data['nodes']:
                node_types = {}
                for node in graph_data['nodes']:
                    node_type = node.get('type', 'Unknown')
                    node_types[node_type] = node_types.get(node_type, 0) + 1
                
                for node_type, count in node_types.items():
                    text_parts.append(f"Contains {count} {node_type} nodes")
            
            if 'edges' in graph_data and graph_data['edges']:
                edge_types = {}
                for edge in graph_data['edges']:
                    edge_type = edge.get('type', edge.get('relationship_type', 'Unknown'))
                    edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
                
                for edge_type, count in edge_types.items():
                    text_parts.append(f"Contains {count} {edge_type} relationships")
        
        extracted_text = " ".join(text_parts)
        self.logger.info(f"Extracted graph text length: {len(extracted_text)} characters")
        return extracted_text 