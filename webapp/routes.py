@webapp.route('/kg-neo4j/api/available-folders')
def get_available_folders():
    """Get list of available data folders"""
    try:
        from kg_neo4j.neo4j_service import get_available_data_folders
        folders = get_available_data_folders()
        return jsonify({
            "success": True,
            "folders": folders,
            "base_path": "output/etl_results"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@webapp.route('/kg-neo4j/api/stats')
def get_kg_stats():
    """Get Knowledge Graph statistics"""
    try:
        from kg_neo4j.neo4j_service import get_graph_stats
        stats = get_graph_stats()
        return jsonify({
            "success": True,
            "stats": stats
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500 