/**
 * Knowledge Graph Visualization UI Component
 * Handles graph display and interaction
 */

let network = null;
let nodes = new vis.DataSet([]);
let edges = new vis.DataSet([]);

export async function initGraphVisualization() {
    console.log('🔧 Initializing Knowledge Graph Visualization component...');
    
    try {
        // Initialize vis.js network
        const container = document.getElementById('graph-container');
        if (!container) {
            console.warn('Graph container not found');
            return;
        }
        
        // Ensure container is empty and properly positioned
        container.innerHTML = '';
        container.style.position = 'relative';
        container.style.height = '400px';
        container.style.width = '100%';
        
        const data = { nodes, edges };
        const options = {
            nodes: {
                shape: 'dot',
                size: 16,
                font: {
                    size: 12,
                    face: 'Arial'
                },
                borderWidth: 2,
                shadow: true
            },
            edges: {
                width: 2,
                shadow: true,
                smooth: {
                    type: 'continuous'
                }
            },
            physics: {
                stabilization: false,
                barnesHut: {
                    gravitationalConstant: -80000,
                    springConstant: 0.001,
                    springLength: 200
                }
            },
            interaction: {
                navigationButtons: true,
                keyboard: true
            }
        };
        
        network = new vis.Network(container, data, options);
        
        // Set up event listeners
        network.on('click', function(params) {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                showNodeDetails(nodeId);
            }
        });
        
        // Show initial message
        showGraphMessage("Select a file to view its graph visualization");
        
        console.log('✅ Knowledge Graph Visualization component initialized');
        
    } catch (error) {
        console.error('❌ Failed to initialize Graph Visualization component:', error);
    }
}

export function showGraphMessage(message) {
    const container = document.getElementById('graph-container');
    if (container) {
        // Clear any existing content
        container.innerHTML = '';
        
        // Create message overlay
        const messageDiv = document.createElement('div');
        messageDiv.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            background: rgba(255, 255, 255, 0.95);
            z-index: 1000;
            color: #666;
            font-size: 16px;
        `;
        messageDiv.innerHTML = `
            <div style="text-align: center;">
                <i class="fas fa-project-diagram" style="font-size: 48px; margin-bottom: 16px; color: #ddd;"></i>
                <p>${message}</p>
            </div>
        `;
        
        // Add message to container
        container.appendChild(messageDiv);
        
        // Store reference to remove later
        container._messageOverlay = messageDiv;
    }
}

export function hideGraphMessage() {
    const container = document.getElementById('graph-container');
    if (container && container._messageOverlay) {
        container.removeChild(container._messageOverlay);
        container._messageOverlay = null;
    }
}

export async function loadGraphData() {
    try {
        const response = await fetch('/api/kg-neo4j/graph-data');
        const data = await response.json();
        
        if (data.success) {
            // Clear existing data
            nodes.clear();
            edges.clear();
            
            // Add nodes
            if (data.nodes) {
                const processedNodes = data.nodes.map(node => ({
                    id: node.id,
                    label: node.label || node.id,
                    title: node.properties?.description || node.label || node.id,
                    group: node.label || 'default',
                    color: getNodeColor(node.label),
                    size: 16
                }));
                nodes.add(processedNodes);
            }
            
            // Add relationships (convert to edges format)
            if (data.relationships) {
                const processedEdges = data.relationships.map(rel => ({
                    id: rel.id,
                    from: rel.source,
                    to: rel.target,
                    label: rel.type,
                    title: rel.type,
                    color: getEdgeColor(rel.type),
                    width: 2,
                    arrows: 'to'
                }));
                edges.add(processedEdges);
            }
            
            console.log(`Loaded ${data.nodes?.length || 0} nodes and ${data.relationships?.length || 0} relationships`);
        }
        
    } catch (error) {
        console.error('Failed to load graph data:', error);
    }
}

export function loadGraphDataFromImport(graphData) {
    try {
        console.log('🎨 Loading graph data from import:', graphData);
        
        // Hide any existing message overlay
        hideGraphMessage();
        
        // Ensure network is initialized
        const container = document.getElementById('graph-container');
        if (!container) {
            console.error('Graph container not found');
            return;
        }
        
        // If network doesn't exist, create it
        if (!network) {
            console.log('🔄 Recreating network instance...');
            container.innerHTML = '';
            container.style.position = 'relative';
            container.style.height = '400px';
            container.style.width = '100%';
            
            const data = { nodes, edges };
            const options = {
                nodes: {
                    shape: 'dot',
                    size: 12,
                    font: {
                        size: 10,
                        face: 'Arial',
                        color: '#333'
                    },
                    borderWidth: 1,
                    shadow: false,
                    color: {
                        background: '#ffffff',
                        border: '#2B7CE9',
                        highlight: {
                            background: '#D2E5FF',
                            border: '#2B7CE9'
                        }
                    }
                },
                edges: {
                    width: 1,
                    shadow: false,
                    smooth: {
                        type: 'continuous',
                        forceDirection: 'none'
                    },
                    color: {
                        color: '#848484',
                        highlight: '#848484',
                        hover: '#848484'
                    }
                },
                physics: {
                    enabled: true,
                    stabilization: {
                        enabled: true,
                        iterations: 1000,
                        updateInterval: 100
                    },
                    barnesHut: {
                        gravitationalConstant: -2000,
                        centralGravity: 0.3,
                        springLength: 150,
                        springConstant: 0.04,
                        damping: 0.09,
                        avoidOverlap: 0.5
                    }
                },
                interaction: {
                    navigationButtons: true,
                    keyboard: true,
                    hover: true,
                    tooltipDelay: 200
                },
                layout: {
                    improvedLayout: true,
                    hierarchical: {
                        enabled: false,
                        direction: 'UD',
                        sortMethod: 'directed'
                    }
                }
            };
            
            network = new vis.Network(container, data, options);
            
            // Set up event listeners
            network.on('click', function(params) {
                if (params.nodes.length > 0) {
                    const nodeId = params.nodes[0];
                    showNodeDetails(nodeId);
                }
            });
        }
        
        // Clear existing data
        nodes.clear();
        edges.clear();
        
        // Process and add nodes with ID validation
        if (graphData.nodes && Array.isArray(graphData.nodes)) {
            const processedNodes = [];
            const seenNodeIds = new Set();
            
            graphData.nodes.forEach((node, index) => {
                // Generate a unique ID
                let nodeId = node.id || node.node_id || node.name || node.idShort;
                
                // If no ID or empty ID, generate one
                if (!nodeId || nodeId === '') {
                    nodeId = `node_${index}_${Date.now()}`;
                }
                
                // Ensure ID is a string
                nodeId = String(nodeId);
                
                // If ID already exists, make it unique
                if (seenNodeIds.has(nodeId)) {
                    nodeId = `${nodeId}_${index}`;
                }
                
                seenNodeIds.add(nodeId);
                
                // Create a better label for AAS nodes
                let nodeLabel = node.idShort || node.name || node.label;
                if (!nodeLabel && node.id) {
                    // Extract short name from long URLs
                    if (node.id.includes('/')) {
                        nodeLabel = node.id.split('/').pop();
                    } else {
                        nodeLabel = node.id;
                    }
                }
                
                // Create a detailed tooltip
                let tooltip = nodeLabel;
                if (node.description) tooltip += `\nDescription: ${node.description}`;
                if (node.type) tooltip += `\nType: ${node.type}`;
                if (node.value) tooltip += `\nValue: ${node.value}`;
                
                const processedNode = {
                    id: nodeId,
                    label: nodeLabel || nodeId,
                    title: tooltip,
                    group: node.type || node.group || 'default',
                    color: getNodeColor(node.type || node.group),
                    size: node.size || 12
                };
                
                processedNodes.push(processedNode);
            });
            
            if (processedNodes.length > 0) {
                nodes.add(processedNodes);
                console.log(`✅ Added ${processedNodes.length} nodes to visualization`);
            }
        }
        
        // Process and add edges with ID validation
        let edgeData = graphData.edges || graphData.relationships || [];
        if (Array.isArray(edgeData)) {
            const processedEdges = [];
            const seenEdgeIds = new Set();
            
            edgeData.forEach((edge, index) => {
                // Generate a unique ID for the edge
                let edgeId = edge.id;
                if (!edgeId || edgeId === '') {
                    const source = edge.source || edge.from || '';
                    const target = edge.target || edge.to || '';
                    edgeId = `${source}-${target}`;
                }
                
                // Ensure ID is a string
                edgeId = String(edgeId);
                
                // If ID already exists, make it unique
                if (seenEdgeIds.has(edgeId)) {
                    edgeId = `${edgeId}_${index}`;
                }
                
                seenEdgeIds.add(edgeId);
                
                const processedEdge = {
                    id: edgeId,
                    from: edge.source || edge.from,
                    to: edge.target || edge.to,
                    label: edge.label || edge.type || edge.relationship_type || '',
                    title: edge.title || edge.description || edge.label || edge.type || '',
                    color: getEdgeColor(edge.type || edge.relationship_type),
                    width: edge.width || 2,
                    arrows: 'to'
                };
                
                processedEdges.push(processedEdge);
            });
            
            if (processedEdges.length > 0) {
                edges.add(processedEdges);
                console.log(`✅ Added ${processedEdges.length} edges to visualization`);
            }
        }
        
        console.log(`🎯 Total: ${nodes.length} nodes and ${edges.length} edges loaded`);
        
    } catch (error) {
        console.error('❌ Error loading graph data from import:', error);
    }
}

function getNodeColor(type) {
    const colors = {
        'Asset': '#1f77b4',
        'Submodel': '#ff7f0e',
        'SubSubmodel': '#ff7f0e',
        'Property': '#2ca02c',
        'Operation': '#d62728',
        'Event': '#9467bd',
        'Relationship': '#8c564b',
        'Identification': '#17a2b8',
        'Manufacturer': '#28a745',
        'GLN': '#6f42c1',
        'ProductDesignation': '#fd7e14',
        'SerialNumber': '#e83e8c',
        'default': '#6c757d'
    };
    return colors[type] || colors.default;
}

function getEdgeColor(type) {
    const colors = {
        'contains': '#1f77b4',
        'references': '#ff7f0e',
        'implements': '#2ca02c',
        'extends': '#d62728',
        'default': '#7f7f7f'
    };
    return colors[type] || colors.default;
}

function showNodeDetails(nodeId) {
    // Implementation for showing node details
    console.log('Showing details for node:', nodeId);
} 