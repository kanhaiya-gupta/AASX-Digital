"""
AASX Graph Analyzer
Provides comprehensive graph analysis for AASX knowledge graph data
"""

import logging
import pandas as pd
from typing import Dict, List, Any, Optional
from neo4j import GraphDatabase, Driver, Session

logger = logging.getLogger(__name__)

class AASXGraphAnalyzer:
    """Analyzes AASX knowledge graph data"""
    
    def __init__(self, uri: str, user: str, password: str):
        """Initialize analyzer with Neo4j connection"""
        self.uri = uri
        self.user = user
        self.password = password
        self.driver: Optional[Driver] = None
        self._connect()
    
    def _connect(self):
        """Establish connection to Neo4j"""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            logger.info(f"Graph analyzer connected to Neo4j at {self.uri}")
        except Exception as e:
            logger.error(f"Failed to connect graph analyzer to Neo4j: {e}")
            raise
    
    def get_network_statistics(self) -> pd.DataFrame:
        """Get comprehensive network statistics"""
        try:
            with self.driver.session() as session:
                # Basic counts
                result = session.run("MATCH (n) RETURN count(n) as total_nodes")
                total_nodes = result.single()['total_nodes']
                
                result = session.run("MATCH ()-[r]->() RETURN count(r) as total_relationships")
                total_relationships = result.single()['total_relationships']
                
                # Calculate density
                if total_nodes > 1:
                    max_edges = total_nodes * (total_nodes - 1)
                    density = total_relationships / max_edges if max_edges > 0 else 0
                else:
                    density = 0
                
                # Connected components
                result = session.run("""
                    CALL gds.wcc.stream('neo4j')
                    YIELD componentId, nodeId
                    RETURN count(DISTINCT componentId) as components
                """)
                try:
                    components = result.single()['components']
                except:
                    components = 1  # Fallback if GDS not available
                
                # Average degree
                if total_nodes > 0:
                    avg_degree = (2 * total_relationships) / total_nodes
                else:
                    avg_degree = 0
                
                stats = pd.DataFrame([{
                    'Metric': 'Total Nodes',
                    'Value': total_nodes
                }, {
                    'Metric': 'Total Relationships',
                    'Value': total_relationships
                }, {
                    'Metric': 'Network Density',
                    'Value': round(density, 4)
                }, {
                    'Metric': 'Connected Components',
                    'Value': components
                }, {
                    'Metric': 'Average Degree',
                    'Value': round(avg_degree, 2)
                }])
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get network statistics: {e}")
            return pd.DataFrame()
    
    def get_quality_distribution(self) -> pd.DataFrame:
        """Analyze quality distribution of nodes"""
        try:
            with self.driver.session() as session:
                # Get quality scores if available
                result = session.run("""
                    MATCH (n)
                    WHERE n.quality IS NOT NULL
                    RETURN n.quality as quality, count(n) as count
                    ORDER BY quality
                """)
                
                quality_data = []
                for record in result:
                    quality_data.append({
                        'Quality Level': record['quality'],
                        'Count': record['count'],
                        'Percentage': 0  # Will calculate below
                    })
                
                if quality_data:
                    total = sum(item['Count'] for item in quality_data)
                    for item in quality_data:
                        item['Percentage'] = round((item['Count'] / total) * 100, 2)
                
                return pd.DataFrame(quality_data)
                
        except Exception as e:
            logger.error(f"Failed to get quality distribution: {e}")
            return pd.DataFrame()
    
    def analyze_compliance_network(self) -> pd.DataFrame:
        """Analyze compliance with standards"""
        try:
            with self.driver.session() as session:
                # Check for compliance-related properties
                result = session.run("""
                    MATCH (n)
                    WHERE n.compliance IS NOT NULL OR n.standard IS NOT NULL
                    RETURN 
                        coalesce(n.compliance, 'Unknown') as compliance,
                        coalesce(n.standard, 'Unknown') as standard,
                        count(n) as count
                    ORDER BY count DESC
                """)
                
                compliance_data = []
                for record in result:
                    compliance_data.append({
                        'Compliance': record['compliance'],
                        'Standard': record['standard'],
                        'Count': record['count']
                    })
                
                return pd.DataFrame(compliance_data)
                
        except Exception as e:
            logger.error(f"Failed to analyze compliance: {e}")
            return pd.DataFrame()
    
    def get_entity_type_distribution(self) -> pd.DataFrame:
        """Get distribution of entity types"""
        try:
            with self.driver.session() as session:
                # Get all labels and their counts
                result = session.run("""
                    CALL db.labels() YIELD label
                    MATCH (n)
                    WHERE n:`{label}`
                    RETURN label, count(n) as count
                    ORDER BY count DESC
                """)
                
                entity_data = []
                for record in result:
                    entity_data.append({
                        'Entity Type': record['label'],
                        'Count': record['count']
                    })
                
                return pd.DataFrame(entity_data)
                
        except Exception as e:
            logger.error(f"Failed to get entity distribution: {e}")
            return pd.DataFrame()
    
    def analyze_relationships(self) -> pd.DataFrame:
        """Analyze relationship types and patterns"""
        try:
            with self.driver.session() as session:
                # Get relationship types and counts
                result = session.run("""
                    CALL db.relationshipTypes() YIELD relationshipType
                    MATCH ()-[r:`{relationshipType}`]->()
                    RETURN relationshipType, count(r) as count
                    ORDER BY count DESC
                """)
                
                rel_data = []
                for record in result:
                    rel_data.append({
                        'Relationship Type': record['relationshipType'],
                        'Count': record['count']
                    })
                
                return pd.DataFrame(rel_data)
                
        except Exception as e:
            logger.error(f"Failed to analyze relationships: {e}")
            return pd.DataFrame()
    
    def get_centrality_metrics(self) -> pd.DataFrame:
        """Calculate centrality metrics for nodes"""
        try:
            with self.driver.session() as session:
                # Try to use GDS for centrality calculation
                try:
                    result = session.run("""
                        CALL gds.pageRank.stream('neo4j')
                        YIELD nodeId, score
                        RETURN nodeId, score
                        ORDER BY score DESC
                        LIMIT 10
                    """)
                    
                    centrality_data = []
                    for record in result:
                        centrality_data.append({
                            'Node ID': record['nodeId'],
                            'PageRank Score': round(record['score'], 4)
                        })
                    
                    return pd.DataFrame(centrality_data)
                    
                except:
                    # Fallback: simple degree centrality
                    result = session.run("""
                        MATCH (n)
                        OPTIONAL MATCH (n)-[r]-()
                        RETURN n.id as node_id, count(r) as degree
                        ORDER BY degree DESC
                        LIMIT 10
                    """)
                    
                    centrality_data = []
                    for record in result:
                        centrality_data.append({
                            'Node ID': record['node_id'],
                            'Degree Centrality': record['degree']
                        })
                    
                    return pd.DataFrame(centrality_data)
                
        except Exception as e:
            logger.error(f"Failed to get centrality metrics: {e}")
            return pd.DataFrame()
    
    def find_communities(self) -> pd.DataFrame:
        """Find communities in the graph"""
        try:
            with self.driver.session() as session:
                # Try to use GDS for community detection
                try:
                    result = session.run("""
                        CALL gds.louvain.stream('neo4j')
                        YIELD nodeId, communityId
                        RETURN communityId, count(nodeId) as size
                        ORDER BY size DESC
                    """)
                    
                    community_data = []
                    for record in result:
                        community_data.append({
                            'Community ID': record['communityId'],
                            'Size': record['size']
                        })
                    
                    return pd.DataFrame(community_data)
                    
                except:
                    # Fallback: connected components
                    result = session.run("""
                        CALL gds.wcc.stream('neo4j')
                        YIELD componentId, nodeId
                        RETURN componentId, count(nodeId) as size
                        ORDER BY size DESC
                    """)
                    
                    community_data = []
                    for record in result:
                        community_data.append({
                            'Component ID': record['componentId'],
                            'Size': record['size']
                        })
                    
                    return pd.DataFrame(community_data)
                
        except Exception as e:
            logger.error(f"Failed to find communities: {e}")
            return pd.DataFrame()
    
    def get_graph_summary(self) -> Dict[str, Any]:
        """Get a comprehensive graph summary"""
        try:
            summary = {}
            
            # Basic stats
            summary['network_stats'] = self.get_network_statistics().to_dict('records')
            summary['entity_distribution'] = self.get_entity_type_distribution().to_dict('records')
            summary['relationship_analysis'] = self.analyze_relationships().to_dict('records')
            summary['quality_distribution'] = self.get_quality_distribution().to_dict('records')
            summary['compliance_analysis'] = self.analyze_compliance_network().to_dict('records')
            
            # Advanced metrics
            summary['centrality_metrics'] = self.get_centrality_metrics().to_dict('records')
            summary['communities'] = self.find_communities().to_dict('records')
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get graph summary: {e}")
            return {}
    
    def close(self):
        """Close the Neo4j connection"""
        if self.driver:
            self.driver.close()
            logger.info("Graph analyzer connection closed") 