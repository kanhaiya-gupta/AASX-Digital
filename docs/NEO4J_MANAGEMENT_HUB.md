# Neo4j Management Hub

The Neo4j Management Hub is a simplified interface for launching and managing Neo4j tools within the AASX Digital Twin Analytics Framework. Instead of trying to replicate Neo4j's functionality, it focuses on being a launcher and manager for Neo4j's professional tools.

## Overview

The Neo4j Management Hub provides:
- **Docker Container Management**: Start, stop, and monitor Neo4j containers
- **Tool Launcher**: Quick access to Neo4j Browser and Desktop
- **Status Monitoring**: Real-time monitoring of Neo4j services
- **Connection Management**: Easy access to Neo4j connection information

## Features

### 🚀 Quick Launch Tools
- **Neo4j Browser**: Opens the web-based graph interface
- **Neo4j Desktop**: Launches the full desktop application
- **Docker Management**: Start/stop Neo4j containers

### 📊 System Status
- **Neo4j Service**: Connection status to Neo4j database
- **Docker Status**: Container health and status
- **Browser Access**: Web interface accessibility
- **Active Connections**: Number of current connections

### 🔗 Connection Information
- **Neo4j URI**: `neo4j://localhost:7688`
- **Username**: `neo4j`
- **Browser URL**: `http://localhost:7474`
- **Admin URL**: `http://localhost:7688`

### 📁 Data Management
- **Neo4j handles all data operations**: Import, export, backup, and management
- **Use Neo4j Browser**: Built-in data import/export tools
- **Use Neo4j Desktop**: Advanced data management capabilities

## Getting Started

### 1. Start Neo4j Container
1. Navigate to the Neo4j Management Hub
2. Click "Start Docker" to launch the Neo4j container
3. Wait for the container to fully start (check status indicators)

### 2. Access Neo4j Browser
1. Click "Neo4j Browser" to open the web interface
2. Login with:
   - Username: `neo4j`
   - Password: `password`

### 3. Import Data Using Neo4j Tools
1. Use Neo4j Browser's built-in import tools
2. Use Neo4j Desktop for advanced data management
3. Follow Neo4j's official documentation for data operations

### 4. Analyze with Neo4j Tools
1. Use Neo4j Browser for interactive graph visualization
2. Write Cypher queries for data analysis
3. Use Neo4j Desktop for advanced operations

## Docker Management

### Manual Docker Commands
```bash
# Start Neo4j container
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -e NEO4J_PLUGINS='["apoc"]' \
  neo4j:latest

# Stop container
docker stop neo4j

# Remove container
docker rm neo4j

# View logs
docker logs -f neo4j
```

### Using the Management Script
```bash
# Check status
python backend/kg_neo4j/manage_neo4j.py status

# Start Neo4j
python backend/kg_neo4j/manage_neo4j.py start

# Stop Neo4j
python backend/kg_neo4j/manage_neo4j.py stop

# View logs
python backend/kg_neo4j/manage_neo4j.py logs
```

## API Endpoints

### Status Endpoints
- `GET /kg-neo4j/api/status` - Get system status
- `GET /kg-neo4j/api/docker-status` - Get Docker status

### Docker Management
- `POST /kg-neo4j/api/docker/start` - Start Neo4j container
- `POST /kg-neo4j/api/docker/stop` - Stop Neo4j container

## Neo4j Browser Features

Once you access Neo4j Browser, you can:

### Data Import/Export
- **CSV Import**: Import data from CSV files
- **JSON Import**: Import data from JSON files
- **Database Export**: Export data in various formats
- **Backup/Restore**: Full database backup and restore

### Basic Queries
```cypher
// Show all nodes
MATCH (n) RETURN n LIMIT 10

// Show all relationships
MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 10

// Count nodes by type
MATCH (n) RETURN n.type as NodeType, count(n) as Count
```

### AASX-Specific Queries
```cypher
// Find all assets
MATCH (n) WHERE n.type = "asset" RETURN n

// Find submodels
MATCH (n) WHERE n.type = "submodel" RETURN n

// Show asset relationships
MATCH (a:Asset)-[r]->(b) RETURN a, r, b
```

### Graph Visualization
- Interactive node and relationship display
- Drag and drop to rearrange
- Zoom and pan controls
- Node filtering and highlighting

## Data Management with Neo4j

### Importing Data
1. **CSV Files**: Use `LOAD CSV` Cypher command
2. **JSON Files**: Use `apoc.load.json` procedure
3. **Database Files**: Use Neo4j Desktop import tools
4. **APOC Procedures**: Advanced import capabilities

### Exporting Data
1. **CSV Export**: Use `CALL apoc.export.csv`
2. **JSON Export**: Use `CALL apoc.export.json`
3. **GraphML Export**: Use `CALL apoc.export.graphml`
4. **Database Backup**: Use Neo4j Desktop backup tools

### Example Import Commands
```cypher
// Import CSV data
LOAD CSV WITH HEADERS FROM 'file:///data.csv' AS row
CREATE (:Node {id: row.id, name: row.name})

// Import JSON data
CALL apoc.load.json('file:///data.json') YIELD value
CREATE (:Node {properties: value})
```

## Troubleshooting

### Container Won't Start
1. Check Docker is running: `docker --version`
2. Check port availability: `netstat -an | grep 7474`
3. View container logs: `docker logs neo4j`

### Can't Access Browser
1. Verify container is running: `docker ps`
2. Check port mapping: `docker port neo4j`
3. Try accessing: `http://localhost:7474`

### Data Import Issues
1. Use Neo4j Browser's built-in import tools
2. Check file permissions and paths
3. Review Neo4j import documentation
4. Use Neo4j Desktop for complex imports

### Connection Problems
1. Check Neo4j service status in the Management Hub
2. Verify credentials: `neo4j/password`
3. Test connection: `curl http://localhost:7474`

## Best Practices

### Data Management
- Use Neo4j's built-in import/export tools
- Follow Neo4j's data modeling best practices
- Use APOC procedures for advanced operations
- Regular database backups

### Performance
- Limit query results with `LIMIT`
- Use indexes for large datasets
- Monitor memory usage in Neo4j Browser
- Use Neo4j Desktop for performance tuning

### Security
- Change default password in production
- Use environment variables for credentials
- Restrict network access in production
- Regular security updates

## Integration with AASX Framework

The Neo4j Management Hub integrates with the AASX Digital Twin Analytics Framework:

1. **ETL Pipeline**: Processed AASX data can be imported using Neo4j tools
2. **AI/RAG System**: Can query Neo4j data for AI analysis
3. **Analytics**: Graph data supports advanced analytics
4. **Digital Twins**: Neo4j stores twin relationships and properties

## Next Steps

After setting up Neo4j:

1. **Explore Data**: Use Neo4j Browser to explore your AASX data
2. **Import Data**: Use Neo4j's built-in import tools
3. **Write Queries**: Create Cypher queries for specific analysis
4. **Build Visualizations**: Create graph visualizations for insights
5. **Integrate with AI**: Use graph data in the AI/RAG system
6. **Scale Up**: Add more data sources and relationships

## Support

For issues with the Neo4j Management Hub:
1. Check the troubleshooting section above
2. Review Docker logs: `docker logs neo4j`
3. Check system status in the web interface
4. Use the management script for command-line operations

For Neo4j-specific issues:
- [Neo4j Documentation](https://neo4j.com/docs/)
- [Cypher Query Language](https://neo4j.com/docs/cypher-manual/current/)
- [Neo4j Browser Guide](https://neo4j.com/docs/browser-manual/current/)
- [Data Import Guide](https://neo4j.com/docs/cypher-manual/current/clauses/load-csv/) 