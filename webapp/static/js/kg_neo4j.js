// Neo4j Management Hub JavaScript
// Focused on launching and managing Neo4j tools

console.log('🔧 Neo4j Management Hub JavaScript loaded');

// ============================================================================
// DOCKER NEO4J FUNCTIONS
// ============================================================================

async function checkConnectionStatus() {
    console.log('🔍 Checking Docker Neo4j connection status...');
    
    try {
        const response = await fetch('/kg-neo4j/api/status');
        const data = await response.json();
        
        updateDockerStatus(data);
        
        if (data.success) {
            showNotification('✅ Docker Neo4j connection successful', 'success');
        } else {
            showNotification('❌ Docker Neo4j connection failed: ' + data.error, 'error');
        }
        
        return data.success;
    } catch (error) {
        console.error('Error checking connection status:', error);
        showNotification('❌ Failed to check Docker Neo4j status', 'error');
        updateDockerStatus({ success: false, error: error.message });
        return false;
    }
}

function updateDockerStatus(data) {
    const statusContainer = document.getElementById('docker-status');
    if (!statusContainer) return;
    
    const statusItems = statusContainer.querySelectorAll('.status-item');
    
    // Update Container Status
    if (statusItems[0]) {
        const statusIndicator = statusItems[0].querySelector('.status-indicator');
        const statusValue = statusItems[0].querySelector('.status-value');
        
        if (data.docker_running) {
            statusIndicator.className = 'status-indicator status-running';
            statusValue.innerHTML = '<span class="status-indicator status-running"></span>Running';
        } else {
            statusIndicator.className = 'status-indicator status-stopped';
            statusValue.innerHTML = '<span class="status-indicator status-stopped"></span>Stopped';
        }
    }
    
    // Update Browser Access status
    if (statusItems[1]) {
        const statusIndicator = statusItems[1].querySelector('.status-indicator');
        const statusValue = statusItems[1].querySelector('.status-value');
        
        if (data.browser_accessible) {
            statusIndicator.className = 'status-indicator status-running';
            statusValue.innerHTML = '<span class="status-indicator status-running"></span>Available';
        } else {
            statusIndicator.className = 'status-indicator status-stopped';
            statusValue.innerHTML = '<span class="status-indicator status-stopped"></span>Unavailable';
        }
    }
}

async function checkDockerStatus() {
    console.log('🐳 Checking Docker status...');
    
    try {
        const response = await fetch('/kg-neo4j/api/docker-status');
        const data = await response.json();
        
        if (data.success) {
            showNotification(`🐳 Docker: ${data.status}`, 'info');
        } else {
            showNotification('❌ Failed to check Docker status', 'error');
        }
        
        return data;
    } catch (error) {
        console.error('Error checking Docker status:', error);
        showNotification('❌ Docker status check failed', 'error');
        return { success: false, error: error.message };
    }
}

// ============================================================================
// LOCAL NEO4J FUNCTIONS
// ============================================================================

async function checkLocalStatus() {
    console.log('🖥️ Checking Local Neo4j status...');
    
    try {
        const response = await fetch('/kg-neo4j/api/local/status');
        const data = await response.json();
        
        updateLocalStatus(data);
        
        if (data.success) {
            if (data.application_running) {
                showNotification('✅ Local Neo4j Desktop is running', 'success');
            } else {
                showNotification('ℹ️ Local Neo4j Desktop is not running', 'info');
            }
        } else {
            showNotification('❌ Failed to check Local Neo4j status: ' + data.error, 'error');
        }
        
        return data.success;
    } catch (error) {
        console.error('Error checking local status:', error);
        showNotification('❌ Failed to check Local Neo4j status', 'error');
        updateLocalStatus({ success: false, error: error.message });
        return false;
    }
}

function updateLocalStatus(data) {
    const statusContainer = document.getElementById('local-status');
    if (!statusContainer) return;
    
    const statusItems = statusContainer.querySelectorAll('.status-item');
    
    // Update Application Status
    if (statusItems[0]) {
        const statusIndicator = statusItems[0].querySelector('.status-indicator');
        const statusValue = statusItems[0].querySelector('.status-value');
        
        if (data.application_running) {
            statusIndicator.className = 'status-indicator status-running';
            statusValue.innerHTML = '<span class="status-indicator status-running"></span>Running';
        } else {
            statusIndicator.className = 'status-indicator status-stopped';
            statusValue.innerHTML = '<span class="status-indicator status-stopped"></span>Not Running';
        }
    }
    
    // Update Connection Status
    if (statusItems[1]) {
        const statusIndicator = statusItems[1].querySelector('.status-indicator');
        const statusValue = statusItems[1].querySelector('.status-value');
        
        if (data.connection_available) {
            statusIndicator.className = 'status-indicator status-running';
            statusValue.innerHTML = '<span class="status-indicator status-running"></span>Connected';
        } else {
            statusIndicator.className = 'status-indicator status-stopped';
            statusValue.innerHTML = '<span class="status-indicator status-stopped"></span>Not Connected';
        }
    }
}

async function launchLocalNeo4jDesktop() {
    console.log('🖥️ Launching Local Neo4j Desktop...');
    
    try {
        showNotification('🖥️ Launching Neo4j Desktop...', 'info');
        
        const response = await fetch('/kg-neo4j/api/local/launch', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('✅ ' + data.message, 'success');
            
            // Wait a moment for the application to start
            setTimeout(() => {
                checkLocalStatus();
            }, 3000);
            
        } else {
            showNotification('❌ Failed to launch Neo4j Desktop: ' + data.error, 'error');
        }
        
        return data.success;
    } catch (error) {
        console.error('Error launching Neo4j Desktop:', error);
        showNotification('❌ Failed to launch Neo4j Desktop', 'error');
        return false;
    }
}

async function getLocalNeo4jInfo() {
    console.log('ℹ️ Getting Local Neo4j info...');
    
    try {
        const response = await fetch('/kg-neo4j/api/local/info');
        const data = await response.json();
        
        if (data.success) {
            console.log('Local Neo4j Info:', data);
            return data;
        } else {
            console.error('Failed to get local Neo4j info:', data.error);
            return null;
        }
    } catch (error) {
        console.error('Error getting local Neo4j info:', error);
        return null;
    }
}

// ============================================================================
// NEO4J TOOL LAUNCHING FUNCTIONS
// ============================================================================

function launchDockerBrowser() {
    console.log('🌐 Launching Docker Neo4j Browser...');
    
    // Open Docker Neo4j Browser in new tab
    const browserUrl = 'http://localhost:7475';
    window.open(browserUrl, '_blank');
    
    showNotification('🌐 Docker Neo4j Browser opened in new tab', 'success');
}

function launchLocalBrowser() {
    console.log('🌐 Launching Local Neo4j Browser...');
    
    // Open Local Neo4j Browser in new tab
    const browserUrl = 'http://localhost:7474';
    window.open(browserUrl, '_blank');
    
    showNotification('🌐 Local Neo4j Browser opened in new tab', 'success');
}

// ============================================================================
// DOCKER MANAGEMENT FUNCTIONS
// ============================================================================

async function startNeo4jDocker() {
    console.log('🚀 Starting Docker Neo4j container...');
    
    try {
        showNotification('🚀 Starting Docker Neo4j container...', 'info');
        
        const response = await fetch('/kg-neo4j/api/docker/start', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('✅ Docker Neo4j container started successfully', 'success');
            
            // Wait a moment for the container to fully start
            setTimeout(() => {
                checkConnectionStatus();
                checkDockerStatus();
            }, 3000);
            
        } else {
            showNotification('❌ Failed to start Docker container: ' + data.error, 'error');
        }
        
        return data.success;
    } catch (error) {
        console.error('Error starting Docker container:', error);
        showNotification('❌ Failed to start Docker container', 'error');
        return false;
    }
}

async function stopNeo4jDocker() {
    console.log('🛑 Stopping Docker Neo4j container...');
    
    try {
        showNotification('🛑 Stopping Docker Neo4j container...', 'info');
        
        const response = await fetch('/kg-neo4j/api/docker/stop', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('✅ Docker Neo4j container stopped successfully', 'success');
            
            // Update status immediately
            setTimeout(() => {
                checkConnectionStatus();
                checkDockerStatus();
            }, 1000);
            
        } else {
            showNotification('❌ Failed to stop Docker container: ' + data.error, 'error');
        }
        
        return data.success;
    } catch (error) {
        console.error('Error stopping Docker container:', error);
        showNotification('❌ Failed to stop Docker container', 'error');
        return false;
    }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after shorter time: 2 seconds for success, 3 seconds for others
    const timeout = type === 'success' ? 2000 : 3000;
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, timeout);
}

function showLocalHelp() {
    console.log('❓ Showing Local help...');
    showNotification('📖 Neo4j Desktop Setup: Download from neo4j.com/desktop', 'info');
}

function refreshAllStatus() {
    checkConnectionStatus();
    checkLocalStatus();
}

// ============================================================================
// VISUALIZATION PAGE FUNCTIONS
// ============================================================================

// Global variables for visualization
let currentProject = null;
let currentFile = null;
let graphData = null;

// Load projects for visualization dropdown
async function loadProjects() {
    console.log('📁 Loading projects for visualization...');
    
    try {
        const response = await fetch('/kg-neo4j/api/projects');
        const data = await response.json();
        
        if (data.success) {
            const projectSelect = document.getElementById('project-select');
            if (!projectSelect) {
                console.error('Project select element not found');
                return;
            }
            
            // Clear existing options except the first one
            projectSelect.innerHTML = '<option value="">Choose a project...</option>';
            
            // Add project options
            data.projects.forEach(project => {
                const option = document.createElement('option');
                option.value = project.project_id;
                option.textContent = project.name || project.project_id;
                projectSelect.appendChild(option);
            });
            
            console.log(`✅ Loaded ${data.projects.length} projects`);
            // After loading projects, do not show a notification for success
            // Remove or comment out any line like:
            // showNotification(`✅ Loaded ${projects.length} projects`, 'success');
            // Only show notifications for errors.
        } else {
            console.error('Failed to load projects:', data.error);
            showNotification('❌ Failed to load projects: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error loading projects:', error);
        showNotification('❌ Error loading projects', 'error');
    }
}

// Load files for selected project
async function loadFiles(projectId) {
    console.log(`📄 Loading files for project: ${projectId}`);
    
    try {
        const response = await fetch(`/kg-neo4j/api/projects/${projectId}/files`);
        const data = await response.json();
        
        if (data.success) {
            const fileSelect = document.getElementById('file-select');
            if (!fileSelect) {
                console.error('File select element not found');
                return;
            }
            
            // Clear existing options except the first one
            fileSelect.innerHTML = '<option value="">Choose a file...</option>';
            
            // Add file options
            data.files.forEach(file => {
                const option = document.createElement('option');
                option.value = file.id;
                const filename = file.original_filename || file.filename || file.id;
                const graphStatus = file.graph_exists ? ' (Graph Available)' : ' (No Graph)';
                option.textContent = filename + graphStatus;
                option.dataset.graphExists = file.graph_exists;
                fileSelect.appendChild(option);
            });
            
            // Enable file select
            fileSelect.disabled = false;
            
            console.log(`✅ Loaded ${data.files.length} files for project ${projectId}`);
            // showNotification(`✅ Loaded ${data.files.length} files`, 'success'); // Removed notification
        } else {
            console.error('Failed to load files:', data.error);
            showNotification('❌ Failed to load files: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error loading files:', error);
        showNotification('❌ Error loading files', 'error');
    }
}

// Handle project selection change
function onProjectChange() {
    const projectSelect = document.getElementById('project-select');
    const fileSelect = document.getElementById('file-select');
    
    if (!projectSelect || !fileSelect) return;
    
    const selectedProjectId = projectSelect.value;
    
    if (selectedProjectId) {
        currentProject = selectedProjectId;
        loadFiles(selectedProjectId);
    } else {
        currentProject = null;
        currentFile = null;
        fileSelect.innerHTML = '<option value="">Choose a file...</option>';
        fileSelect.disabled = true;
    }
}

// Handle file selection change
function onFileChange() {
    const fileSelect = document.getElementById('file-select');
    
    if (!fileSelect) return;
    
    const selectedFileId = fileSelect.value;
    
    if (selectedFileId) {
        currentFile = selectedFileId;
        const selectedOption = fileSelect.options[fileSelect.selectedIndex];
        const graphExists = selectedOption.dataset.graphExists === 'true';
        
        if (!graphExists) {
            showNotification('⚠️ Selected file has no graph data available', 'warning');
        }
    } else {
        currentFile = null;
    }
}

// View graph for selected project/file
async function viewGraph() {
    console.log('🔍 Viewing graph...');
    
    if (!currentProject) {
        showNotification('❌ Please select a project first', 'error');
        return;
    }
    
    if (!currentFile) {
        showNotification('❌ Please select a file first', 'error');
        return;
    }
    
    try {
        showLoadingSpinner(true);
        
        // Try to get file-specific graph data first
        const response = await fetch(`/kg-neo4j/api/files/${currentFile}/graph-data`);
        const data = await response.json();
        
        if (data.success && data.graph_data) {
            graphData = data.graph_data;
            renderGraph(graphData);
            // Use metadata from graph data for statistics
            const stats = data.statistics || data.graph_data.metadata || {};
            updateStatistics(stats);
            showNotification('✅ Graph loaded successfully', 'success');
        } else {
            // Fallback to project graph data
            const projectResponse = await fetch(`/kg-neo4j/api/projects/${currentProject}/graph-data`);
            const projectData = await projectResponse.json();
            
            if (projectData.success && projectData.graph_data) {
                graphData = projectData.graph_data;
                renderGraph(graphData);
                // Use metadata from graph data for statistics
                const stats = projectData.statistics || projectData.graph_data.metadata || {};
                updateStatistics(stats);
                showNotification('✅ Project graph loaded successfully', 'success');
            } else {
                showNotification('❌ No graph data available for selected file/project', 'error');
            }
        }
    } catch (error) {
        console.error('Error loading graph:', error);
        showNotification('❌ Error loading graph: ' + error.message, 'error');
    } finally {
        showLoadingSpinner(false);
    }
}

// Render graph using D3.js
function renderGraph(graphData) {
    console.log('🎨 Rendering graph...');
    console.log('Graph data structure:', Object.keys(graphData || {}));
    
    const graphCanvas = document.getElementById('graph-canvas');
    if (!graphCanvas) {
        console.error('Graph canvas element not found');
        return;
    }
    
    // Clear existing graph
    graphCanvas.innerHTML = '';
    
    // Handle various data formats and structures
    if (!graphData) {
        console.error('No graph data provided');
        return;
    }
    
    // Extract nodes from various possible formats
    let nodes = [];
    if (graphData.nodes) {
        nodes = graphData.nodes;
    } else if (graphData.vertices) {
        nodes = graphData.vertices;
    } else if (Array.isArray(graphData)) {
        // If graphData is an array, assume it's nodes
        nodes = graphData;
    } else {
        console.error('No nodes found in graph data');
        console.log('Available keys:', Object.keys(graphData));
        return;
    }
    
    // Extract edges/links from various possible formats
    let edges = [];
    if (graphData.edges) {
        edges = graphData.edges;
    } else if (graphData.links) {
        edges = graphData.links;
    } else if (graphData.relationships) {
        edges = graphData.relationships;
    } else if (graphData.connections) {
        edges = graphData.connections;
    }
    
    if (!edges || edges.length === 0) {
        console.warn('No edges/links found in graph data - rendering nodes only');
    }
    
    console.log(`Found ${nodes.length} nodes and ${edges.length} edges`);
    
    // Create node map for efficient lookup
    const nodeMap = new Map();
    nodes.forEach(node => {
        // Handle various node ID formats
        const nodeId = node.id || node.node_id || node.vertex_id || node.key || node.name;
        if (nodeId) {
            nodeMap.set(nodeId, node);
        }
    });
    
    // Transform edges to use node references
    const transformedEdges = edges.map(edge => {
        // Handle various source/target formats
        const sourceId = edge.source_id || edge.source || edge.from || edge.start || edge.origin;
        const targetId = edge.target_id || edge.target || edge.to || edge.end || edge.destination;
        
        // Handle cases where source/target might be objects
        const source = typeof sourceId === 'object' ? sourceId : nodeMap.get(sourceId);
        const target = typeof targetId === 'object' ? targetId : nodeMap.get(targetId);
        
        return {
            source: source,
            target: target,
            type: edge.type || edge.relationship_type || edge.edge_type || 'relationship',
            properties: edge.properties || edge.attributes || edge.data || {}
        };
    }).filter(edge => edge.source && edge.target); // Filter out edges with missing nodes
    
    console.log(`Transformed ${transformedEdges.length} edges from ${edges.length} total`);
    
    // Set up D3.js visualization
    const width = graphCanvas.clientWidth;
    const height = graphCanvas.clientHeight;
    
    // Create SVG with zoom support
    const svg = d3.select(graphCanvas)
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    // Create zoom behavior
    const zoom = d3.zoom()
        .scaleExtent([0.1, 10]) // Min and max zoom levels
        .wheelDelta(event => -event.deltaY * 0.002) // Adjust wheel zoom sensitivity
        .on('zoom', (event) => {
            // Apply zoom transform to the main group
            mainGroup.attr('transform', event.transform);
            
            // Update zoom level display if it exists
            updateZoomLevel(event.transform.k);
        });
    
    // Apply zoom to SVG
    svg.call(zoom);
    
    // Add zoom level indicator
    const zoomIndicator = svg.append('text')
        .attr('x', 10)
        .attr('y', 20)
        .attr('font-size', '12px')
        .attr('fill', '#666')
        .attr('pointer-events', 'none')
        .text('Zoom: 100%');
    
    function updateZoomLevel(scale) {
        const percentage = Math.round(scale * 100);
        zoomIndicator.text(`Zoom: ${percentage}%`);
    }
    
    // Create main group for all graph elements
    const mainGroup = svg.append('g');
    
    // Create force simulation
    const simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(transformedEdges).id(d => d.id || d.node_id || d.vertex_id || d.key || d.name).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2));
    
    // Create links
    const links = mainGroup.append('g')
        .selectAll('line')
        .data(transformedEdges)
        .enter().append('line')
        .attr('stroke', '#999')
        .attr('stroke-opacity', 0.6)
        .attr('stroke-width', 2);
    
    // Create nodes
    const nodeElements = mainGroup.append('g')
        .selectAll('circle')
        .data(nodes)
        .enter().append('circle')
        .attr('r', 8)
        .attr('fill', d => getNodeColor(d.type || d.node_type || d.category || 'default'))
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));
    
    // Add labels
    const labels = mainGroup.append('g')
        .selectAll('text')
        .data(nodes)
        .enter().append('text')
        .text(d => {
            // Handle various label formats
            return d.id_short || d.label || d.name || d.title || d.display_name || 
                   (d.id ? d.id.split('/').pop() : 'Unknown');
        })
        .attr('font-size', '12px')
        .attr('text-anchor', 'middle')
        .attr('dy', '0.35em');
    
    // Update positions on simulation tick
    simulation.on('tick', () => {
        links
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        nodeElements
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
        
        labels
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    });
    
    // Drag functions
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    
    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    
    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
    
    // Store zoom reference globally for external control
    window.currentZoom = zoom;
    window.currentSvg = svg;
    
    console.log('✅ Graph rendered successfully with zoom support');
}

// Get node color based on type
function getNodeColor(type) {
    if (!type) return '#6b7280'; // Default gray for unknown types
    
    const normalizedType = type.toLowerCase();
    
    const colors = {
        // AAS-specific types
        'asset': '#3b82f6',
        'submodel': '#10b981',
        'property': '#f59e0b',
        'document': '#ef4444',
        'relationship': '#8b5cf6',
        'aas': '#3b82f6',
        'submodel_element': '#10b981',
        'property': '#f59e0b',
        'collection': '#8b5cf6',
        'reference': '#6366f1',
        'constraint': '#ec4899',
        
        // Generic graph types
        'node': '#6b7280',
        'vertex': '#6b7280',
        'entity': '#3b82f6',
        'object': '#10b981',
        'item': '#f59e0b',
        'element': '#8b5cf6',
        
        // Common categories
        'person': '#3b82f6',
        'organization': '#10b981',
        'location': '#f59e0b',
        'event': '#ef4444',
        'concept': '#8b5cf6',
        'product': '#06b6d4',
        'service': '#84cc16',
        'process': '#f97316',
        
        // Manufacturing/Industrial
        'machine': '#3b82f6',
        'equipment': '#10b981',
        'sensor': '#f59e0b',
        'actuator': '#ef4444',
        'controller': '#8b5cf6',
        'system': '#06b6d4',
        'component': '#84cc16',
        'part': '#f97316',
        
        // Data/Information
        'data': '#3b82f6',
        'information': '#10b981',
        'file': '#f59e0b',
        'database': '#ef4444',
        'api': '#8b5cf6',
        'interface': '#06b6d4',
        'model': '#84cc16',
        'schema': '#f97316',
        
        // Default fallbacks
        'default': '#6b7280',
        'unknown': '#6b7280',
        'other': '#6b7280'
    };
    
    // Try exact match first
    if (colors[normalizedType]) {
        return colors[normalizedType];
    }
    
    // Try partial matches
    for (const [key, color] of Object.entries(colors)) {
        if (normalizedType.includes(key) || key.includes(normalizedType)) {
            return color;
        }
    }
    
    // Generate a consistent color based on the type string
    let hash = 0;
    for (let i = 0; i < normalizedType.length; i++) {
        hash = normalizedType.charCodeAt(i) + ((hash << 5) - hash);
    }
    
    // Generate a color from the hash
    const hue = Math.abs(hash) % 360;
    return `hsl(${hue}, 70%, 60%)`;
}

// Update statistics display
function updateStatistics(stats) {
    // Handle both API statistics and graph metadata
    const totalNodes = stats.total_nodes || stats.totalNodes || stats.node_count || stats.vertices_count || 0;
    const totalEdges = stats.total_relationships || stats.total_edges || stats.totalEdges || stats.edge_count || stats.links_count || 0;
    
    // Count nodes by type from graph data if available
    let assetNodes = stats.asset_nodes || 0;
    let submodelNodes = stats.submodel_nodes || 0;
    let propertyNodes = stats.property_nodes || 0;
    let documentNodes = stats.document_nodes || 0;
    
    if (graphData && graphData.nodes) {
        const nodes = graphData.nodes;
        assetNodes = nodes.filter(n => {
            const type = (n.type || n.node_type || n.category || '').toLowerCase();
            return type === 'asset' || type === 'aas' || type.includes('asset');
        }).length;
        
        submodelNodes = nodes.filter(n => {
            const type = (n.type || n.node_type || n.category || '').toLowerCase();
            return type === 'submodel' || type.includes('submodel');
        }).length;
        
        propertyNodes = nodes.filter(n => {
            const type = (n.type || n.node_type || n.category || '').toLowerCase();
            return type === 'property' || type.includes('property');
        }).length;
        
        documentNodes = nodes.filter(n => {
            const type = (n.type || n.node_type || n.category || '').toLowerCase();
            return type === 'document' || type.includes('document');
        }).length;
    }
    
    // Update the display elements
    const nodeCountElement = document.getElementById('nodeCount');
    const edgeCountElement = document.getElementById('edgeCount');
    const assetCountElement = document.getElementById('assetCount');
    const submodelCountElement = document.getElementById('submodelCount');
    
    if (nodeCountElement) nodeCountElement.textContent = totalNodes;
    if (edgeCountElement) edgeCountElement.textContent = totalEdges;
    if (assetCountElement) assetCountElement.textContent = assetNodes;
    if (submodelCountElement) submodelCountElement.textContent = submodelNodes;
    
    console.log(`Statistics updated: ${totalNodes} nodes, ${totalEdges} edges, ${assetNodes} assets, ${submodelNodes} submodels`);
}

// Show/hide loading spinner
function showLoadingSpinner(show) {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        spinner.style.display = show ? 'block' : 'none';
    }
}

// Initialize visualization page
function initializeVisualization() {
    console.log('🚀 Initializing visualization page...');
    
    // Load projects on page load
    loadProjects();
    
    // Add event listeners
    const projectSelect = document.getElementById('project-select');
    const fileSelect = document.getElementById('file-select');
    
    if (projectSelect) {
        projectSelect.addEventListener('change', onProjectChange);
    }
    
    if (fileSelect) {
        fileSelect.addEventListener('change', onFileChange);
    }
    
    console.log('✅ Visualization page initialized');
}

// Auto-initialize if on visualization page (fallback)
if (document.getElementById('project-select') && document.getElementById('file-select')) {
    // Only initialize if not already done by the HTML template
    if (typeof window.visualizationInitialized === 'undefined') {
        document.addEventListener('DOMContentLoaded', function() {
            if (typeof loadProjects === 'function') {
                loadProjects();
            }
        });
    }
} 

// Get current zoom level
function getCurrentZoomLevel() {
    if (!window.currentSvg) {
        return 1;
    }
    
    try {
        const transform = d3.zoomTransform(window.currentSvg.node());
        return transform.k;
    } catch (error) {
        console.error('Error getting zoom level:', error);
        return 1;
    }
}

// Zoom control functions
function zoomIn() {
    console.log('🔍 Zooming in...');
    
    if (!window.currentSvg || !window.currentZoom) {
        showNotification('⚠️ No active graph to zoom', 'warning');
        return;
    }
    
    try {
        // Get current transform
        const currentTransform = d3.zoomTransform(window.currentSvg.node());
        const newScale = Math.min(currentTransform.k * 1.5, 10); // Zoom in by 1.5x, max 10x
        
        // Apply new zoom
        window.currentSvg
            .transition()
            .duration(300)
            .call(window.currentZoom.transform, currentTransform.scale(newScale));
        
        const percentage = Math.round(newScale * 100);
        showNotification(`🔍 Zoomed in to ${percentage}%`, 'success');
    } catch (error) {
        console.error('Error zooming in:', error);
        showNotification('❌ Error zooming in', 'error');
    }
}

function zoomOut() {
    console.log('🔍 Zooming out...');
    
    if (!window.currentSvg || !window.currentZoom) {
        showNotification('⚠️ No active graph to zoom', 'warning');
        return;
    }
    
    try {
        // Get current transform
        const currentTransform = d3.zoomTransform(window.currentSvg.node());
        const newScale = Math.max(currentTransform.k / 1.5, 0.1); // Zoom out by 1.5x, min 0.1x
        
        // Apply new zoom
        window.currentSvg
            .transition()
            .duration(300)
            .call(window.currentZoom.transform, currentTransform.scale(newScale));
        
        const percentage = Math.round(newScale * 100);
        showNotification(`🔍 Zoomed out to ${percentage}%`, 'success');
    } catch (error) {
        console.error('Error zooming out:', error);
        showNotification('❌ Error zooming out', 'error');
    }
}

function fitToScreen() {
    console.log('📐 Fitting to screen...');
    
    if (!window.currentSvg || !window.currentZoom) {
        showNotification('⚠️ No active graph to fit', 'warning');
        return;
    }
    
    try {
        const graphCanvas = document.getElementById('graph-canvas');
        if (!graphCanvas) {
            showNotification('❌ Graph canvas not found', 'error');
            return;
        }
        
        const width = graphCanvas.clientWidth;
        const height = graphCanvas.clientHeight;
        
        // Reset zoom and fit to screen
        window.currentSvg
            .transition()
            .duration(500)
            .call(window.currentZoom.transform, d3.zoomIdentity);
        
        showNotification('📐 Fitted to screen (100%)', 'success');
    } catch (error) {
        console.error('Error fitting to screen:', error);
        showNotification('❌ Error fitting to screen', 'error');
    }
}

// Enhanced reset view function
function resetView() {
    console.log('🔄 Resetting graph view...');
    
    if (!window.currentSvg || !window.currentZoom) {
        showNotification('⚠️ No active graph to reset', 'warning');
        return;
    }
    
    try {
        // Reset zoom and pan
        window.currentSvg
            .transition()
            .duration(500)
            .call(window.currentZoom.transform, d3.zoomIdentity);
        
        showNotification('🔄 Graph view reset to 100%', 'success');
    } catch (error) {
        console.error('Error resetting view:', error);
        showNotification('❌ Error resetting view', 'error');
    }
} 