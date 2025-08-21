"""
Pre-built Cypher Queries for AASX Analytics

This module contains a collection of pre-built Cypher queries for common
AASX data analytics operations in Neo4j.
"""

class CypherQueries:
    """
    Collection of pre-built Cypher queries for AASX analytics.
    
    Provides ready-to-use queries for common graph analytics operations
    on AASX data in Neo4j.
    """
    
    # Basic Statistics Queries
    BASIC_STATS = """
    MATCH (n:Node)
    RETURN count(n) as total_nodes
    UNION
    MATCH ()-[r:RELATES_TO]->()
    RETURN count(r) as total_relationships
    """
    
    NODE_TYPE_DISTRIBUTION = """
    MATCH (n:Node)
    RETURN n.type as entity_type, count(*) as count
    ORDER BY count DESC
    """
    
    RELATIONSHIP_TYPE_DISTRIBUTION = """
    MATCH ()-[r:RELATES_TO]->()
    RETURN r.type as relationship_type, count(*) as count
    ORDER BY count DESC
    """
    
    # Quality Analysis Queries
    QUALITY_DISTRIBUTION = """
    MATCH (n:Node)
    WHERE n.quality_level IS NOT NULL
    RETURN n.type as entity_type, 
           n.quality_level as quality_level, 
           count(*) as count
    ORDER BY entity_type, quality_level
    """
    
    HIGH_QUALITY_ASSETS = """
    MATCH (n:Node {type: 'asset'})
    WHERE n.quality_level = 'HIGH'
    RETURN n.id as id,
           n.description as description,
           n.quality_level as quality_level,
           n.compliance_status as compliance_status
    ORDER BY n.description
    """
    
    QUALITY_BY_ENTITY_TYPE = """
    MATCH (n:Node)
    WHERE n.quality_level IS NOT NULL
    RETURN n.type as entity_type,
           n.quality_level as quality_level,
           count(*) as count,
           round(count(*) * 100.0 / size(collect(n)), 2) as percentage
    ORDER BY entity_type, quality_level
    """
    
    # Compliance Analysis Queries
    COMPLIANCE_DISTRIBUTION = """
    MATCH (n:Node)
    WHERE n.compliance_status IS NOT NULL
    RETURN n.type as entity_type,
           n.compliance_status as compliance_status,
           count(*) as count
    ORDER BY entity_type, compliance_status
    """
    
    COMPLIANCE_SUMMARY = """
    MATCH (n:Node)
    WHERE n.compliance_status IS NOT NULL
    RETURN n.compliance_status as status,
           count(*) as count,
           round(count(*) * 100.0 / size(collect(n)), 2) as percentage
    ORDER BY count DESC
    """
    
    NON_COMPLIANT_ENTITIES = """
    MATCH (n:Node)
    WHERE n.compliance_status = 'NON_COMPLIANT'
    RETURN n.id as id,
           n.type as type,
           n.description as description,
           n.quality_level as quality_level
    ORDER BY n.type, n.description
    """
    
    # Relationship Analysis Queries
    RELATIONSHIP_PATTERNS = """
    MATCH (source:Node)-[r:RELATES_TO]->(target:Node)
    RETURN r.type as relationship_type,
           source.type as source_type,
           target.type as target_type,
           count(*) as count
    ORDER BY count DESC
    """
    
    ASSETS_WITH_MOST_SUBMODELS = """
    MATCH (asset:Node {type: 'asset'})-[r:RELATES_TO]->(submodel:Node {type: 'submodel'})
    RETURN asset.id as asset_id,
           asset.description as asset_description,
           count(submodel) as submodel_count
    ORDER BY submodel_count DESC
    """
    
    ISOLATED_NODES = """
    MATCH (n:Node)
    WHERE NOT (n)-[:RELATES_TO]-()
    RETURN n.id as id,
           n.type as type,
           n.description as description,
           n.quality_level as quality_level
    ORDER BY n.type, n.description
    """
    
    # Path Analysis Queries
    SHORTEST_PATH = """
    MATCH path = shortestPath(
        (source:Node {id: $source_id})-[*]-(target:Node {id: $target_id})
    )
    RETURN length(path) as path_length,
           [node in nodes(path) | node.id] as node_ids,
           [node in nodes(path) | node.type] as node_types
    """
    
    ALL_PATHS = """
    MATCH path = (source:Node {id: $source_id})-[*1..5]-(target:Node {id: $target_id})
    RETURN length(path) as path_length,
           [node in nodes(path) | node.id] as node_ids
    ORDER BY path_length
    LIMIT 10
    """
    
    # Search Queries
    SEARCH_ENTITIES = """
    MATCH (n:Node)
    WHERE toLower(n.description) CONTAINS toLower($search_term)
       OR toLower(n.id) CONTAINS toLower($search_term)
    RETURN n.id as id,
           n.type as type,
           n.description as description,
           n.quality_level as quality_level
    ORDER BY n.type, n.description
    """
    
    SEARCH_BY_TYPE = """
    MATCH (n:Node {type: $entity_type})
    WHERE toLower(n.description) CONTAINS toLower($search_term)
       OR toLower(n.id) CONTAINS toLower($search_term)
    RETURN n.id as id,
           n.type as type,
           n.description as description,
           n.quality_level as quality_level
    ORDER BY n.description
    """
    
    # Advanced Analytics Queries
    CONNECTED_COMPONENTS = """
    CALL gds.alpha.scc.stream('aasx_graph')
    YIELD nodeId, componentId
    RETURN componentId,
           count(*) as size
    ORDER BY size DESC
    """
    
    PAGE_RANK = """
    CALL gds.pageRank.stream('aasx_graph')
    YIELD nodeId, score
    MATCH (n:Node) WHERE id(n) = nodeId
    RETURN n.id as id,
           n.type as type,
           n.description as description,
           score
    ORDER BY score DESC
    LIMIT 20
    """
    
    COMMUNITY_DETECTION = """
    CALL gds.louvain.stream('aasx_graph')
    YIELD nodeId, communityId
    MATCH (n:Node) WHERE id(n) = nodeId
    RETURN communityId,
           collect(n.id) as nodes,
           count(*) as size
    ORDER BY size DESC
    """
    
    # Network Metrics Queries
    AVERAGE_DEGREE = """
    MATCH (n:Node)
    WITH n, size((n)-[:RELATES_TO]-()) as degree
    RETURN avg(degree) as average_degree,
           max(degree) as max_degree,
           min(degree) as min_degree
    """
    
    DEGREE_DISTRIBUTION = """
    MATCH (n:Node)
    WITH n, size((n)-[:RELATES_TO]-()) as degree
    RETURN degree,
           count(*) as count
    ORDER BY degree
    """
    
    # Quality Infrastructure Specific Queries
    QI_COMPLIANCE_ANALYSIS = """
    MATCH (n:Node)
    WHERE n.compliance_status IS NOT NULL
    WITH n.type as entity_type,
         n.compliance_status as status,
         count(*) as count
    RETURN entity_type,
           status,
           count,
           round(count * 100.0 / sum(count) OVER (PARTITION BY entity_type), 2) as percentage
    ORDER BY entity_type, count DESC
    """
    
    QUALITY_NETWORK_ANALYSIS = """
    MATCH (n:Node)
    WHERE n.quality_level IS NOT NULL
    WITH n.quality_level as quality,
         count(*) as count
    RETURN quality,
           count,
           round(count * 100.0 / sum(count) OVER (), 2) as percentage
    ORDER BY count DESC
    """
    
    ASSET_SUBMODEL_RELATIONSHIPS = """
    MATCH (asset:Node {type: 'asset'})-[r:RELATES_TO]->(submodel:Node {type: 'submodel'})
    RETURN asset.id as asset_id,
           asset.description as asset_description,
           submodel.id as submodel_id,
           submodel.description as submodel_description,
           r.type as relationship_type
    ORDER BY asset.description, submodel.description
    """
    
    # Maintenance and Utility Queries
    CLEAR_DATABASE = """
    MATCH (n) DETACH DELETE n
    """
    
    CREATE_INDEXES = """
    CREATE INDEX node_id_index IF NOT EXISTS FOR (n:Node) ON (n.id);
    CREATE INDEX node_type_index IF NOT EXISTS FOR (n:Node) ON (n.type);
    CREATE INDEX node_quality_index IF NOT EXISTS FOR (n:Node) ON (n.quality_level);
    CREATE INDEX rel_type_index IF NOT EXISTS FOR ()-[r:RELATES_TO]-() ON (r.type);
    """
    
    GET_INDEXES = """
    SHOW INDEXES
    """
    
    # Custom Query Templates
    @staticmethod
    def find_related_entities(entity_id: str, max_depth: int = 2) -> str:
        """Generate query to find related entities within max_depth"""
        return f"""
        MATCH path = (start:Node {{id: '{entity_id}'}})-[*1..{max_depth}]-(related:Node)
        WHERE start <> related
        RETURN DISTINCT related.id as id,
               related.type as type,
               related.description as description,
               length(path) as distance
        ORDER BY distance, related.type
        """
    
    @staticmethod
    def get_entities_by_quality(quality_level: str, entity_type: str = None) -> str:
        """Generate query to get entities by quality level"""
        if entity_type:
            return f"""
            MATCH (n:Node {{type: '{entity_type}', quality_level: '{quality_level}'}})
            RETURN n.id as id,
                   n.description as description,
                   n.quality_level as quality_level,
                   n.compliance_status as compliance_status
            ORDER BY n.description
            """
        else:
            return f"""
            MATCH (n:Node {{quality_level: '{quality_level}'}})
            RETURN n.id as id,
                   n.type as type,
                   n.description as description,
                   n.compliance_status as compliance_status
            ORDER BY n.type, n.description
            """
    
    @staticmethod
    def get_entities_by_compliance(compliance_status: str, entity_type: str = None) -> str:
        """Generate query to get entities by compliance status"""
        if entity_type:
            return f"""
            MATCH (n:Node {{type: '{entity_type}', compliance_status: '{compliance_status}'}})
            RETURN n.id as id,
                   n.description as description,
                   n.quality_level as quality_level,
                   n.compliance_status as compliance_status
            ORDER BY n.description
            """
        else:
            return f"""
            MATCH (n:Node {{compliance_status: '{compliance_status}'}})
            RETURN n.id as id,
                   n.type as type,
                   n.description as description,
                   n.quality_level as quality_level
            ORDER BY n.type, n.description
            """ 