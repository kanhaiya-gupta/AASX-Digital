"""
AI RAG Graph Exporter
=====================

Exports graphs to various formats for storage and integration.
"""

import logging
import json
import os
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pathlib import Path

from ..graph_models.graph_structure import GraphStructure

logger = logging.getLogger(__name__)


class GraphExporter:
    """
    Graph Exporter for AI RAG Graph Generation
    
    Exports graphs to various formats including Cypher, GraphML, JSON-LD,
    and visualization formats for storage and integration with other systems.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the graph exporter.
        
        Args:
            config: Configuration dictionary for export parameters
        """
        self.config = config or self._get_default_config()
        self.export_stats = {
            "total_graphs_exported": 0,
            "exports_by_format": {},
            "export_time_ms": 0,
            "export_sizes": []
        }
        
        logger.info("✅ GraphExporter initialized with configuration")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for graph export."""
        return {
            "output_directory": "output/graphs/ai_rag",
            "supported_formats": ["cypher", "graphml", "jsonld", "png", "svg", "html"],
            "default_format": "cypher",
            "create_directories": True,
            "overwrite_existing": False,
            "include_metadata": True,
            "include_visualization": True,
            "cypher_options": {
                "include_properties": True,
                "include_attributes": True,
                "include_labels": True
            },
            "graphml_options": {
                "include_properties": True,
                "include_attributes": True,
                "include_positions": True
            },
            "jsonld_options": {
                "include_context": True,
                "include_properties": True,
                "include_metadata": True
            },
            "visualization_options": {
                "node_size": 20,
                "edge_width": 2,
                "color_scheme": "default",
                "layout": "force_directed"
            }
        }
    
    async def export_graph(
        self,
        graph: GraphStructure,
        output_formats: Optional[List[str]] = None,
        output_directory: Optional[str] = None,
        include_metadata: Optional[bool] = None,
        include_visualization: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Export a graph to specified formats.
        
        Args:
            graph: Graph structure to export
            output_formats: List of formats to export (default: all supported)
            output_directory: Custom output directory
            include_metadata: Whether to include metadata in exports
            include_visualization: Whether to generate visualizations
            
        Returns:
            Dict: Export results including file paths and metadata
        """
        start_time = datetime.now()
        logger.info(f"📤 Starting graph export: {graph.graph_name} to formats: {output_formats or self.config['supported_formats']}")
        
        try:
            # Use provided parameters or defaults
            formats = output_formats or self.config["supported_formats"]
            output_dir = output_directory or self.config["output_directory"]
            include_meta = include_metadata if include_metadata is not None else self.config["include_metadata"]
            include_viz = include_visualization if include_visualization is not None else self.config["include_visualization"]
            
            # Create output directory
            if self.config["create_directories"]:
                os.makedirs(output_dir, exist_ok=True)
            
            # Create graph-specific subdirectory
            graph_dir = os.path.join(output_dir, graph.graph_id)
            os.makedirs(graph_dir, exist_ok=True)
            
            export_results = {
                "graph_id": graph.graph_id,
                "graph_name": graph.graph_name,
                "export_timestamp": datetime.now().isoformat(),
                "output_directory": graph_dir,
                "exported_files": [],
                "export_metadata": {},
                "errors": [],
                "warnings": []
            }
            
            # Export to each requested format
            for format_type in formats:
                if format_type in self.config["supported_formats"]:
                    try:
                        format_result = await self._export_to_format(
                            graph, format_type, graph_dir, include_meta, include_viz
                        )
                        export_results["exported_files"].extend(format_result["files"])
                        export_results["export_metadata"][format_type] = format_result["metadata"]
                        
                        if format_result["errors"]:
                            export_results["errors"].extend(format_result["errors"])
                        
                        if format_result["warnings"]:
                            export_results["warnings"].extend(format_result["warnings"])
                            
                    except Exception as e:
                        error_msg = f"Failed to export to {format_type}: {str(e)}"
                        export_results["errors"].append(error_msg)
                        logger.error(f"❌ {error_msg}")
                else:
                    warning_msg = f"Unsupported format: {format_type}"
                    export_results["warnings"].append(warning_msg)
                    logger.warning(f"⚠️ {warning_msg}")
            
            # Update export statistics
            self._update_export_stats(export_results, start_time)
            
            logger.info(f"✅ Graph export completed: {graph.graph_name} - {len(export_results['exported_files'])} files exported")
            return export_results
            
        except Exception as e:
            logger.error(f"❌ Graph export failed: {e}")
            return {
                "graph_id": graph.graph_id,
                "graph_name": graph.graph_name,
                "export_timestamp": datetime.now().isoformat(),
                "output_directory": "",
                "exported_files": [],
                "export_metadata": {},
                "errors": [f"Export failed: {str(e)}"],
                "warnings": []
            }
    
    async def _export_to_format(
        self,
        graph: GraphStructure,
        format_type: str,
        output_dir: str,
        include_metadata: bool,
        include_visualization: bool
    ) -> Dict[str, Any]:
        """Export graph to a specific format."""
        result = {
            "files": [],
            "metadata": {},
            "errors": [],
            "warnings": []
        }
        
        try:
            if format_type == "cypher":
                cypher_result = await self._export_to_cypher(graph, output_dir, include_metadata)
                result["files"].extend(cypher_result["files"])
                result["metadata"].update(cypher_result["metadata"])
                
            elif format_type == "graphml":
                graphml_result = await self._export_to_graphml(graph, output_dir, include_metadata)
                result["files"].extend(graphml_result["files"])
                result["metadata"].update(graphml_result["metadata"])
                
            elif format_type == "jsonld":
                jsonld_result = await self._export_to_jsonld(graph, output_dir, include_metadata)
                result["files"].extend(jsonld_result["files"])
                result["metadata"].update(jsonld_result["metadata"])
                
            elif format_type in ["png", "svg", "html"] and include_visualization:
                viz_result = await self._export_visualization(graph, output_dir, format_type)
                result["files"].extend(viz_result["files"])
                result["metadata"].update(viz_result["metadata"])
            
            return result
            
        except Exception as e:
            result["errors"].append(f"Format export error: {str(e)}")
            return result
    
    async def _export_to_cypher(
        self,
        graph: GraphStructure,
        output_dir: str,
        include_metadata: bool
    ) -> Dict[str, Any]:
        """Export graph to Cypher format."""
        result = {
            "files": [],
            "metadata": {}
        }
        
        try:
            cypher_file = os.path.join(output_dir, f"{graph.graph_id}.cypher")
            
            with open(cypher_file, 'w', encoding='utf-8') as f:
                # Write header
                f.write(f"// AI RAG Graph Export: {graph.graph_name}\n")
                f.write(f"// Generated: {datetime.now().isoformat()}\n")
                f.write(f"// Graph ID: {graph.graph_id}\n")
                f.write(f"// Nodes: {graph.node_count}, Edges: {graph.edge_count}\n\n")
                
                # Create nodes
                for node in graph.nodes:
                    node_props = self._format_node_properties(node, include_metadata)
                    f.write(f"CREATE (n{node.node_id}:{node.node_type} {node_props})\n")
                
                f.write("\n")
                
                # Create relationships
                for edge in graph.edges:
                    rel_props = self._format_edge_properties(edge, include_metadata)
                    f.write(f"CREATE (n{edge.source_node_id})-[:{edge.relationship_type} {rel_props}]->(n{edge.target_node_id})\n")
                
                f.write("\n")
                
                # Add constraints and indexes
                f.write("// Add constraints and indexes\n")
                f.write(f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{graph.graph_id}) REQUIRE n.node_id IS UNIQUE\n")
            
            result["files"].append({
                "path": cypher_file,
                "format": "cypher",
                "size_bytes": os.path.getsize(cypher_file)
            })
            
            result["metadata"]["cypher"] = {
                "node_count": graph.node_count,
                "edge_count": graph.edge_count,
                "cypher_version": "4.4+"
            }
            
            logger.info(f"✅ Exported Cypher file: {cypher_file}")
            
        except Exception as e:
            logger.error(f"❌ Cypher export failed: {e}")
            raise
        
        return result
    
    async def _export_to_graphml(
        self,
        graph: GraphStructure,
        output_dir: str,
        include_metadata: bool
    ) -> Dict[str, Any]:
        """Export graph to GraphML format."""
        result = {
            "files": [],
            "metadata": {}
        }
        
        try:
            graphml_file = os.path.join(output_dir, f"{graph.graph_id}.graphml")
            
            # Generate GraphML content
            graphml_content = self._generate_graphml_content(graph, include_metadata)
            
            with open(graphml_file, 'w', encoding='utf-8') as f:
                f.write(graphml_content)
            
            result["files"].append({
                "path": graphml_file,
                "format": "graphml",
                "size_bytes": os.path.getsize(graphml_file)
            })
            
            result["metadata"]["graphml"] = {
                "node_count": graph.node_count,
                "edge_count": graph.edge_count,
                "graphml_version": "1.0"
            }
            
            logger.info(f"✅ Exported GraphML file: {graphml_file}")
            
        except Exception as e:
            logger.error(f"❌ GraphML export failed: {e}")
            raise
        
        return result
    
    async def _export_to_jsonld(
        self,
        graph: GraphStructure,
        output_dir: str,
        include_metadata: bool
    ) -> Dict[str, Any]:
        """Export graph to JSON-LD format."""
        result = {
            "files": [],
            "metadata": {}
        }
        
        try:
            jsonld_file = os.path.join(output_dir, f"{graph.graph_id}.jsonld")
            
            # Generate JSON-LD content
            jsonld_content = self._generate_jsonld_content(graph, include_metadata)
            
            with open(jsonld_file, 'w', encoding='utf-8') as f:
                json.dump(jsonld_content, f, indent=2, ensure_ascii=False)
            
            result["files"].append({
                "path": jsonld_file,
                "format": "jsonld",
                "size_bytes": os.path.getsize(jsonld_file)
            })
            
            result["metadata"]["jsonld"] = {
                "node_count": graph.node_count,
                "edge_count": graph.edge_count,
                "jsonld_version": "1.1"
            }
            
            logger.info(f"✅ Exported JSON-LD file: {jsonld_file}")
            
        except Exception as e:
            logger.error(f"❌ JSON-LD export failed: {e}")
            raise
        
        return result
    
    async def _export_visualization(
        self,
        graph: GraphStructure,
        output_dir: str,
        format_type: str
    ) -> Dict[str, Any]:
        """Export graph visualization."""
        result = {
            "files": [],
            "metadata": {}
        }
        
        try:
            if format_type == "html":
                # Generate interactive HTML visualization
                html_file = os.path.join(output_dir, f"{graph.graph_id}_visualization.html")
                html_content = self._generate_html_visualization(graph)
                
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                result["files"].append({
                    "path": html_file,
                    "format": "html",
                    "size_bytes": os.path.getsize(html_file)
                })
                
            elif format_type in ["png", "svg"]:
                # For PNG/SVG, we would typically use a visualization library
                # This is a placeholder for actual image generation
                warning_msg = f"Image export to {format_type} not yet implemented"
                result["warnings"].append(warning_msg)
                logger.warning(f"⚠️ {warning_msg}")
            
            result["metadata"]["visualization"] = {
                "format": format_type,
                "node_count": graph.node_count,
                "edge_count": graph.edge_count
            }
            
            logger.info(f"✅ Exported visualization: {format_type}")
            
        except Exception as e:
            logger.error(f"❌ Visualization export failed: {e}")
            raise
        
        return result
    
    def _format_node_properties(self, node: Any, include_metadata: bool) -> str:
        """Format node properties for Cypher export."""
        props = {}
        
        # Basic properties
        props["node_id"] = node.node_id
        props["node_label"] = node.node_label
        props["node_type"] = node.node_type
        props["confidence_score"] = node.confidence_score
        
        if include_metadata:
            # Additional properties
            if node.properties_dict:
                props.update(node.properties_dict)
            
            if node.source_text:
                props["source_text"] = node.source_text[:100] + "..." if len(node.source_text) > 100 else node.source_text
        
        # Convert to Cypher format
        cypher_props = []
        for key, value in props.items():
            if value is not None:
                if isinstance(value, str):
                    cypher_props.append(f'{key}: "{value}"')
                else:
                    cypher_props.append(f'{key}: {value}')
        
        return "{" + ", ".join(cypher_props) + "}"
    
    def _format_edge_properties(self, edge: Any, include_metadata: bool) -> str:
        """Format edge properties for Cypher export."""
        props = {}
        
        # Basic properties
        props["edge_id"] = edge.edge_id
        props["relationship_type"] = edge.relationship_type
        props["relationship_label"] = edge.relationship_label
        props["weight"] = edge.weight
        props["confidence_score"] = edge.confidence_score
        props["is_directed"] = edge.is_directed
        
        if include_metadata:
            # Additional properties
            if edge.properties_dict:
                props.update(edge.properties_dict)
            
            if edge.source_text:
                props["source_text"] = edge.source_text[:100] + "..." if len(edge.source_text) > 100 else edge.source_text
        
        # Convert to Cypher format
        cypher_props = []
        for key, value in props.items():
            if value is not None:
                if isinstance(value, str):
                    cypher_props.append(f'{key}: "{value}"')
                else:
                    cypher_props.append(f'{key}: {value}')
        
        return "{" + ", ".join(cypher_props) + "}"
    
    def _generate_graphml_content(self, graph: GraphStructure, include_metadata: bool) -> str:
        """Generate GraphML content."""
        # This is a simplified GraphML generation
        # In a real implementation, you would use a proper GraphML library
        
        graphml = f"""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
         http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
  <key id="node_type" for="node" attr.name="node_type" attr.type="string"/>
  <key id="node_label" for="node" attr.name="node_label" attr.type="string"/>
  <key id="confidence" for="node" attr.name="confidence" attr.type="double"/>
  <key id="edge_type" for="edge" attr.name="edge_type" attr.type="string"/>
  <key id="weight" for="edge" attr.name="weight" attr.type="double"/>
  
  <graph id="{graph.graph_id}" edgedefault="directed">
"""
        
        # Add nodes
        for node in graph.nodes:
            graphml += f'    <node id="{node.node_id}">'
            graphml += f'      <data key="node_type">{node.node_type}</data>'
            graphml += f'      <data key="node_label">{node.node_label}</data>'
            graphml += f'      <data key="confidence">{node.confidence_score}</data>'
            graphml += '    </node>\n'
        
        # Add edges
        for edge in graph.edges:
            graphml += f'    <edge id="{edge.edge_id}" source="{edge.source_node_id}" target="{edge.target_node_id}">'
            graphml += f'      <data key="edge_type">{edge.relationship_type}</data>'
            graphml += f'      <data key="weight">{edge.weight}</data>'
            graphml += '    </edge>\n'
        
        graphml += "  </graph>\n</graphml>"
        
        return graphml
    
    def _generate_jsonld_content(self, graph: GraphStructure, include_metadata: bool) -> str:
        """Generate JSON-LD content."""
        context = {
            "@context": {
                "@vocab": "https://ai-rag.example.org/ontology#",
                "airag": "https://ai-rag.example.org/ontology#",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "owl": "http://www.w3.org/2002/07/owl#"
            }
        }
        
        graph_data = {
            "@id": f"airag:Graph_{graph.graph_id}",
            "@type": "airag:KnowledgeGraph",
            "airag:graphName": graph.graph_name,
            "airag:graphType": graph.graph_type,
            "airag:nodeCount": graph.node_count,
            "airag:edgeCount": graph.edge_count,
            "airag:hasNode": [],
            "airag:hasEdge": []
        }
        
        # Add nodes
        for node in graph.nodes:
            node_data = {
                "@id": f"airag:Node_{node.node_id}",
                "@type": f"airag:{node.node_type.capitalize()}",
                "rdfs:label": node.node_label,
                "airag:confidenceScore": node.confidence_score
            }
            
            if include_metadata and node.properties_dict:
                for key, value in node.properties_dict.items():
                    node_data[f"airag:{key}"] = value
            
            graph_data["airag:hasNode"].append(node_data)
        
        # Add edges
        for edge in graph.edges:
            edge_data = {
                "@id": f"airag:Edge_{edge.edge_id}",
                "@type": f"airag:{edge.relationship_type.capitalize()}",
                "airag:sourceNode": f"airag:Node_{edge.source_node_id}",
                "airag:targetNode": f"airag:Node_{edge.target_node_id}",
                "airag:weight": edge.weight,
                "airag:confidenceScore": edge.confidence_score
            }
            
            if include_metadata and edge.properties_dict:
                for key, value in edge.properties_dict.items():
                    edge_data[f"airag:{key}"] = value
            
            graph_data["airag:hasEdge"].append(edge_data)
        
        return [context, graph_data]
    
    def _generate_html_visualization(self, graph: GraphStructure) -> str:
        """Generate HTML visualization."""
        # This is a simplified HTML visualization
        # In a real implementation, you would use a proper graph visualization library like D3.js
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI RAG Graph: {graph.graph_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .graph-info {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .graph-stats {{ display: flex; gap: 20px; }}
        .stat {{ text-align: center; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
        .stat-label {{ font-size: 12px; color: #666; }}
        .visualization {{ border: 1px solid #ddd; padding: 20px; min-height: 400px; }}
        .node {{ display: inline-block; margin: 5px; padding: 8px 12px; background: #007bff; color: white; border-radius: 15px; font-size: 12px; }}
        .edge {{ margin: 5px; padding: 5px; background: #28a745; color: white; border-radius: 10px; font-size: 11px; }}
    </style>
</head>
<body>
    <h1>AI RAG Graph Visualization</h1>
    
    <div class="graph-info">
        <h2>{graph.graph_name}</h2>
        <p><strong>Graph ID:</strong> {graph.graph_id}</p>
        <p><strong>Type:</strong> {graph.graph_type}</p>
        <p><strong>Category:</strong> {graph.graph_category}</p>
        
        <div class="graph-stats">
            <div class="stat">
                <div class="stat-value">{graph.node_count}</div>
                <div class="stat-label">Nodes</div>
            </div>
            <div class="stat">
                <div class="stat-value">{graph.edge_count}</div>
                <div class="stat-label">Edges</div>
            </div>
            <div class="stat">
                <div class="stat-value">{graph.graph_density:.3f}</div>
                <div class="stat-label">Density</div>
            </div>
            <div class="stat">
                <div class="stat-value">{graph.overall_quality_score:.3f}</div>
                <div class="stat-label">Quality</div>
            </div>
        </div>
    </div>
    
    <div class="visualization">
        <h3>Graph Structure</h3>
        <p>This is a simplified visualization. For interactive exploration, use the exported Cypher or GraphML files.</p>
        
        <h4>Nodes ({graph.node_count})</h4>
"""
        
        # Add node representations
        for node in graph.nodes:
            html += f'        <span class="node" title="{node.node_type}: {node.node_label}">{node.node_label}</span>\n'
        
        html += f"""
        <h4>Relationships ({graph.edge_count})</h4>
"""
        
        # Add edge representations
        for edge in graph.edges:
            html += f'        <span class="edge" title="{edge.relationship_type}">{edge.relationship_type}</span>\n'
        
        html += """
    </div>
    
    <div style="margin-top: 20px; padding: 15px; background: #e9ecef; border-radius: 5px;">
        <h4>Export Information</h4>
        <p><strong>Generated:</strong> """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        <p><strong>Formats Available:</strong> Cypher (.cypher), GraphML (.graphml), JSON-LD (.jsonld)</p>
        <p><strong>Note:</strong> This HTML file provides a basic overview. For detailed analysis, use the exported graph files.</p>
    </div>
</body>
</html>"""
        
        return html
    
    def _update_export_stats(self, export_results: Dict[str, Any], start_time: datetime) -> None:
        """Update export statistics."""
        end_time = datetime.now()
        export_time = (end_time - start_time).total_seconds() * 1000
        
        self.export_stats["total_graphs_exported"] += 1
        self.export_stats["export_time_ms"] += export_time
        
        # Count exports by format
        for file_info in export_results["exported_files"]:
            format_type = file_info["format"]
            self.export_stats["exports_by_format"][format_type] = \
                self.export_stats["exports_by_format"].get(format_type, 0) + 1
            
            # Track file sizes
            if "size_bytes" in file_info:
                self.export_stats["export_sizes"].append(file_info["size_bytes"])
    
    def get_export_stats(self) -> Dict[str, Any]:
        """Get export statistics."""
        stats = self.export_stats.copy()
        
        # Calculate average export time
        if stats["total_graphs_exported"] > 0:
            stats["avg_export_time_ms"] = stats["export_time_ms"] / stats["total_graphs_exported"]
        else:
            stats["avg_export_time_ms"] = 0.0
        
        # Calculate average file size
        if stats["export_sizes"]:
            stats["avg_file_size_bytes"] = sum(stats["export_sizes"]) / len(stats["export_sizes"])
        else:
            stats["avg_file_size_bytes"] = 0.0
        
        # Calculate export rate
        if stats["export_time_ms"] > 0:
            stats["exports_per_second"] = stats["total_graphs_exported"] / (stats["export_time_ms"] / 1000)
        else:
            stats["exports_per_second"] = 0.0
        
        return stats
    
    def reset_stats(self) -> None:
        """Reset export statistics."""
        self.export_stats = {
            "total_graphs_exported": 0,
            "exports_by_format": {},
            "export_time_ms": 0,
            "export_sizes": []
        }
        logger.info("🔄 Graph export statistics reset")
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update export configuration."""
        self.config.update(new_config)
        logger.info("⚙️ Graph export configuration updated")





