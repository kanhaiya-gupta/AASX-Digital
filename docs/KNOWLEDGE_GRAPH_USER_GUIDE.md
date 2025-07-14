# Knowledge Graph User Guide

## Overview

The Knowledge Graph Explorer is now designed to be user-friendly for both beginners and experts. This guide will help you get started and make the most of the new features.

## 🎯 Getting Started

### Step 1: Check System Status
- Look at the **System Status** section at the top of the page
- Green dots indicate everything is working properly
- Red dots indicate issues that need to be resolved
- Click "Check Status" in the onboarding section to verify connections

### Step 2: Load Your Data
- Click "Load Data" in the onboarding section or use the **Data Management** panel
- Enter the path to your processed AAS data (usually `output/etl_results`)
- The system will import your data into Neo4j automatically
- You'll see a success message when the import is complete

### Step 3: Start Exploring
- Use the **Quick Actions** buttons for instant insights
- Try the **Query Examples** to learn how to write queries
- Write your own queries in the main query interface

## 🚀 Quick Actions

The **Quick Actions** section provides one-click access to common queries:

### Graph Overview
- Shows a summary of what's in your knowledge graph
- Displays node types and their counts
- Perfect for understanding your data structure

### Find Assets
- Lists all assets from your AAS data
- Shows asset names and descriptions
- Helps you identify what physical objects are represented

### View Relationships
- Shows how different nodes are connected
- Displays relationship types and counts
- Useful for understanding data dependencies

### Run Analysis
- Performs comprehensive graph analysis
- Provides network statistics and insights
- Exports results for further analysis

## 📚 Query Examples

The **Query Examples** section provides clickable examples with explanations:

### 🔍 Basic: Find All Nodes
```cypher
MATCH (n) RETURN n LIMIT 10
```
**What it does:** Shows the first 10 nodes in your graph. This is a good starting point to see what data you have.

### 🏭 Assets: Find All Assets
```cypher
MATCH (n:Asset) RETURN n.idShort as Asset, n.description as Description LIMIT 10
```
**What it does:** Shows only asset nodes with their names and descriptions. Assets represent physical objects in your AAS data.

### 📋 Submodels: Find All Submodels
```cypher
MATCH (n:Submodel) RETURN n.idShort as Submodel, n.description as Description LIMIT 10
```
**What it does:** Shows submodel nodes and their properties. Submodels contain detailed information about assets.

### 🔗 Relationships: Show Connections
```cypher
MATCH (n)-[r]->(m) RETURN n.idShort as From, type(r) as Relationship, m.idShort as To LIMIT 10
```
**What it does:** Shows how nodes are connected to each other. This helps you understand the structure of your data.

### 📊 Properties: Show Node Details
```cypher
MATCH (n) RETURN n.idShort as Name, keys(n) as Properties LIMIT 5
```
**What it does:** Shows what properties each node has. This helps you understand what information is available.

### 🏷️ Labels: Show All Types
```cypher
CALL db.labels() YIELD label RETURN label as NodeType ORDER BY label
```
**What it does:** Lists all different types of nodes in your graph. This gives you an overview of your data categories.

### 🔗 Connection Types: Show Relationships
```cypher
CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType as ConnectionType ORDER BY relationshipType
```
**What it does:** Lists all types of connections between nodes. This shows you how different data elements relate to each other.

## 🔧 Writing Your Own Queries

### Basic Cypher Query Structure

Cypher queries follow this basic pattern:
```cypher
MATCH (pattern) 
WHERE (conditions) 
RETURN (what to show) 
LIMIT (number of results)
```

### Common Patterns

#### Find nodes by type:
```cypher
MATCH (n:Asset) RETURN n
```

#### Find nodes with specific properties:
```cypher
MATCH (n) WHERE n.idShort CONTAINS "Motor" RETURN n
```

#### Find connected nodes:
```cypher
MATCH (n)-[r]->(m) RETURN n, r, m
```

#### Count nodes:
```cypher
MATCH (n:Asset) RETURN count(n) as AssetCount
```

### Tips for Writing Queries

1. **Start simple:** Begin with `MATCH (n) RETURN n LIMIT 10` to see what data you have
2. **Use labels:** Filter by node type using `:Label` (e.g., `:Asset`, `:Submodel`)
3. **Limit results:** Always use `LIMIT` to avoid overwhelming results
4. **Be specific:** Use `WHERE` clauses to filter results
5. **Format output:** Use `AS` to give columns meaningful names

## 📊 Understanding Results

### Table View
- Results are displayed in a table format
- Click column headers to sort
- Hover over cells to see full content
- Use the search box to filter results

### Graph View
- Some queries can be visualized as a graph
- Nodes are colored by type
- Relationships are shown as arrows
- Drag nodes to rearrange the layout

## 🛠️ Troubleshooting

### Common Issues

#### "No results returned"
- Your graph might be empty - try loading data first
- The query might be too specific - try a broader query
- Check if you're using the correct node labels

#### "Connection failed"
- Make sure Neo4j is running
- Check the connection settings
- Verify the database is accessible

#### "Query syntax error"
- Check your Cypher syntax
- Use the query examples as templates
- Refer to the help tooltip for basic syntax

### Getting Help

1. **Use the help tooltip** next to the query interface
2. **Try the query examples** - they're tested and working
3. **Start with simple queries** and build complexity gradually
4. **Check the system status** to ensure everything is connected

## 🎓 Learning Resources

### Cypher Query Language
- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/current/)
- [Cypher Cheat Sheet](https://neo4j.com/docs/cypher-cheat-sheet/current/)

### AAS (Asset Administration Shell)
- [AAS Specification](https://www.plattform-i40.de/I40/Redaktion/EN/Downloads/Publikation/Details_of_the_Asset_Administration_Shell_Part1_V3.html)
- [AAS Examples](https://github.com/admin-shell-io/aas-specs/tree/master/examples)

### Knowledge Graphs
- [Neo4j Graph Database](https://neo4j.com/developer/graph-database/)
- [Graph Database Concepts](https://neo4j.com/developer/graph-database/)

## 🔄 Advanced Features

### Graph Analysis
- Click "Run Analysis" to get comprehensive insights
- View network statistics and metrics
- Export results for further analysis

### Data Management
- Load new data from ETL output
- Preview imports before committing
- Clear data when needed
- Refresh connections

### Query Management
- Save frequently used queries
- Build complex queries step by step
- Export query results

## 📈 Best Practices

1. **Start with exploration:** Use quick actions and examples to understand your data
2. **Build incrementally:** Start with simple queries and add complexity
3. **Use meaningful names:** Give your query results descriptive column names
4. **Limit results:** Always use LIMIT to manage result size
5. **Document queries:** Save useful queries for future reference
6. **Validate data:** Use analysis tools to check data quality

## 🎉 Success Stories

### Example Workflows

#### Asset Inventory Analysis
1. Use "Find Assets" quick action
2. Filter by specific asset types
3. Analyze relationships between assets
4. Export results for reporting

#### Data Quality Check
1. Run "Graph Overview" to see data structure
2. Use "Properties" query to check data completeness
3. Analyze relationships for consistency
4. Generate quality report

#### System Architecture Mapping
1. Load AAS data from multiple systems
2. Use relationship queries to map connections
3. Visualize system dependencies
4. Identify integration points

---

**Need more help?** Check the system status, try the query examples, or refer to the troubleshooting section above. 