/**
 * Knowledge Graph Neo4j Visualization Module
 * Handles graph rendering, interactive features, and visual customization
 */

export default class KGVisualization {
    constructor() {
        this.isInitialized = false;
        this.config = {
            apiBaseUrl: '/api/kg-neo4j',
            containerId: 'graph-container',
            width: 800,
            height: 600,
            nodeSize: 20,
            linkDistance: 100,
            charge: -300,
            gravity: 0.1,
            alpha: 0.3,
            colors: {
                default: '#1f77b4',
                person: '#ff7f0e',
                organization: '#2ca02c',
                location: '#d62728',
                concept: '#9467bd',
                event: '#8c564b',
                relationship: '#e377c2'
            },
            nodeLabels: true,
            linkLabels: true,
            zoomEnabled: true,
            panEnabled: true,
            dragEnabled: true,
            tooltipEnabled: true,
            animationEnabled: true,
            autoLayout: true,
            layoutAlgorithm: 'force', // force, hierarchical, circular, random
            updateInterval: 1000
        };

        this.container = null;
        this.svg = null;
        this.simulation = null;
        this.nodes = [];
        this.links = [];
        this.nodeElements = [];
        this.linkElements = [];
        this.labelElements = [];
        this.tooltip = null;
        this.zoom = null;
        this.drag = null;
        this.colorScale = null;
        this.layouts = {};
        this.animations = {};
        this.interactions = {};
        this.eventListeners = new Map();
    }

    /**
     * Initialize the Visualization
     */
    async init() {
        console.log('🔧 Initializing Knowledge Graph Visualization...');

        try {
            // Load configuration
            await this.loadConfiguration();

            // Initialize container
            this.initializeContainer();

            // Initialize SVG
            this.initializeSVG();

            // Initialize scales and colors
            this.initializeScales();

            // Initialize layouts
            this.initializeLayouts();

            // Initialize interactions
            this.initializeInteractions();

            // Initialize tooltip
            this.initializeTooltip();

            // Initialize animations
            this.initializeAnimations();

            // Set up event listeners
            this.setupEventListeners();

            this.isInitialized = true;
            console.log('✅ Knowledge Graph Visualization initialized');

        } catch (error) {
            console.error('❌ Knowledge Graph Visualization initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load configuration from server
     */
    async loadConfiguration() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/visualization-config`);
            if (response.ok) {
                const config = await response.json();
                this.config = { ...this.config, ...config };
            }
        } catch (error) {
            console.warn('Could not load visualization configuration from server, using defaults:', error);
        }
    }

    /**
     * Initialize container
     */
    initializeContainer() {
        this.container = document.getElementById(this.config.containerId);
        if (!this.container) {
            throw new Error(`Container with ID '${this.config.containerId}' not found`);
        }

        // Set container dimensions
        this.container.style.width = this.config.width + 'px';
        this.container.style.height = this.config.height + 'px';
        this.container.style.position = 'relative';
        this.container.style.overflow = 'hidden';
    }

    /**
     * Initialize SVG
     */
    initializeSVG() {
        // Create SVG element
        this.svg = d3.select(this.container)
            .append('svg')
            .attr('width', this.config.width)
            .attr('height', this.config.height)
            .style('background-color', '#ffffff');

        // Initialize zoom behavior
        if (this.config.zoomEnabled) {
            this.zoom = d3.zoom()
                .scaleExtent([0.1, 10])
                .on('zoom', (event) => {
                    this.svg.select('g').attr('transform', event.transform);
                });

            this.svg.call(this.zoom);
        }

        // Create main group for graph elements
        this.svg.append('g').attr('class', 'graph-group');
    }

    /**
     * Initialize scales and colors
     */
    initializeScales() {
        // Create color scale for node types
        this.colorScale = d3.scaleOrdinal()
            .domain(['Person', 'Organization', 'Location', 'Concept', 'Event', 'default'])
            .range([
                this.config.colors.person,
                this.config.colors.organization,
                this.config.colors.location,
                this.config.colors.concept,
                this.config.colors.event,
                this.config.colors.default
            ]);

        // Create size scale for nodes
        this.sizeScale = d3.scaleLinear()
            .domain([0, 100])
            .range([5, 30]);
    }

    /**
     * Initialize layouts
     */
    initializeLayouts() {
        // Force-directed layout
        this.layouts.force = () => {
            return d3.forceSimulation()
                .force('link', d3.forceLink().id(d => d.id).distance(this.config.linkDistance))
                .force('charge', d3.forceManyBody().strength(this.config.charge))
                .force('center', d3.forceCenter(this.config.width / 2, this.config.height / 2))
                .force('gravity', d3.forceGravity().strength(this.config.gravity));
        };

        // Hierarchical layout
        this.layouts.hierarchical = () => {
            return d3.forceSimulation()
                .force('link', d3.forceLink().id(d => d.id).distance(this.config.linkDistance))
                .force('charge', d3.forceManyBody().strength(-100))
                .force('center', d3.forceCenter(this.config.width / 2, this.config.height / 2))
                .force('x', d3.forceX().strength(0.1))
                .force('y', d3.forceY().strength(0.1));
        };

        // Circular layout
        this.layouts.circular = () => {
            return d3.forceSimulation()
                .force('link', d3.forceLink().id(d => d.id).distance(this.config.linkDistance))
                .force('charge', d3.forceManyBody().strength(-50))
                .force('center', d3.forceCenter(this.config.width / 2, this.config.height / 2))
                .force('radial', d3.forceRadial(100, this.config.width / 2, this.config.height / 2).strength(0.5));
        };

        // Random layout
        this.layouts.random = () => {
            return d3.forceSimulation()
                .force('link', d3.forceLink().id(d => d.id).distance(this.config.linkDistance))
                .force('center', d3.forceCenter(this.config.width / 2, this.config.height / 2));
        };
    }

    /**
     * Initialize interactions
     */
    initializeInteractions() {
        // Drag behavior
        if (this.config.dragEnabled) {
            this.drag = d3.drag()
                .on('start', (event, d) => {
                    if (!event.active) this.simulation.alphaTarget(0.3).restart();
                    d.fx = d.x;
                    d.fy = d.y;
                })
                .on('drag', (event, d) => {
                    d.fx = event.x;
                    d.fy = event.y;
                })
                .on('end', (event, d) => {
                    if (!event.active) this.simulation.alphaTarget(0);
                    d.fx = null;
                    d.fy = null;
                });
        }

        // Pan behavior
        if (this.config.panEnabled) {
            this.pan = d3.drag()
                .on('drag', (event) => {
                    const transform = d3.zoomTransform(this.svg.node());
                    const newTransform = transform.translate(event.dx, event.dy);
                    this.svg.select('g').attr('transform', newTransform);
                });
        }
    }

    /**
     * Initialize tooltip
     */
    initializeTooltip() {
        if (this.config.tooltipEnabled) {
            this.tooltip = d3.select('body')
                .append('div')
                .attr('class', 'kg-tooltip')
                .style('position', 'absolute')
                .style('background', 'rgba(0, 0, 0, 0.8)')
                .style('color', 'white')
                .style('padding', '8px')
                .style('border-radius', '4px')
                .style('font-size', '12px')
                .style('pointer-events', 'none')
                .style('opacity', 0);
        }
    }

    /**
     * Initialize animations
     */
    initializeAnimations() {
        if (this.config.animationEnabled) {
            this.animations = {
                // Node entrance animation
                nodeEnter: (selection) => {
                    return selection
                        .style('opacity', 0)
                        .style('transform', 'scale(0)')
                        .transition()
                        .duration(500)
                        .style('opacity', 1)
                        .style('transform', 'scale(1)');
                },

                // Link entrance animation
                linkEnter: (selection) => {
                    return selection
                        .style('opacity', 0)
                        .style('stroke-width', 0)
                        .transition()
                        .duration(300)
                        .style('opacity', 1)
                        .style('stroke-width', 2);
                },

                // Node exit animation
                nodeExit: (selection) => {
                    return selection
                        .transition()
                        .duration(300)
                        .style('opacity', 0)
                        .style('transform', 'scale(0)')
                        .remove();
                },

                // Link exit animation
                linkExit: (selection) => {
                    return selection
                        .transition()
                        .duration(300)
                        .style('opacity', 0)
                        .style('stroke-width', 0)
                        .remove();
                }
            };
        }
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Listen for graph data updates
        window.addEventListener('kgDataRefreshed', (event) => {
            this.updateGraph(event.detail.data);
        });

        // Listen for node creation
        window.addEventListener('kgNodeCreated', (event) => {
            this.addNode(event.detail.node);
        });

        // Listen for node updates
        window.addEventListener('kgNodeUpdated', (event) => {
            this.updateNode(event.detail.node);
        });

        // Listen for node deletion
        window.addEventListener('kgNodeDeleted', (event) => {
            this.removeNode(event.detail.nodeId);
        });

        // Listen for relationship creation
        window.addEventListener('kgRelationshipCreated', (event) => {
            this.addLink(event.detail.relationship);
        });

        // Listen for relationship updates
        window.addEventListener('kgRelationshipUpdated', (event) => {
            this.updateLink(event.detail.relationship);
        });

        // Listen for relationship deletion
        window.addEventListener('kgRelationshipDeleted', (event) => {
            this.removeLink(event.detail.relationshipId);
        });
    }

    /**
     * Load graph data
     */
    async loadGraphData() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/graph-data`);
            if (response.ok) {
                const data = await response.json();
                this.nodes = data.nodes || [];
                this.links = data.relationships || [];
                this.renderGraph();
            } else {
                throw new Error(`Failed to load graph data: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Load graph data failed:', error);
            throw error;
        }
    }

    /**
     * Render the graph
     */
    renderGraph() {
        if (!this.isInitialized) {
            console.warn('Visualization not initialized');
            return;
        }

        const graphGroup = this.svg.select('.graph-group');

        // Clear existing elements
        graphGroup.selectAll('*').remove();

        // Create links
        this.renderLinks(graphGroup);

        // Create nodes
        this.renderNodes(graphGroup);

        // Create labels
        if (this.config.nodeLabels) {
            this.renderNodeLabels(graphGroup);
        }

        if (this.config.linkLabels) {
            this.renderLinkLabels(graphGroup);
        }

        // Initialize simulation
        this.initializeSimulation();

        // Dispatch event
        window.dispatchEvent(new CustomEvent('kgGraphRendered', {
            detail: {
                nodes: this.nodes.length,
                links: this.links.length
            }
        }));
    }

    /**
     * Render nodes
     */
    renderNodes(container) {
        this.nodeElements = container.selectAll('.node')
            .data(this.nodes, d => d.id)
            .enter()
            .append('circle')
            .attr('class', 'node')
            .attr('r', d => this.sizeScale(d.weight || 1))
            .attr('fill', d => this.colorScale(d.labels?.[0] || 'default'))
            .attr('stroke', '#ffffff')
            .attr('stroke-width', 2)
            .style('cursor', 'pointer');

        // Apply drag behavior
        if (this.drag) {
            this.nodeElements.call(this.drag);
        }

        // Add tooltip
        if (this.tooltip) {
            this.nodeElements
                .on('mouseover', (event, d) => {
                    this.showTooltip(event, this.createNodeTooltip(d));
                })
                .on('mouseout', () => {
                    this.hideTooltip();
                });
        }

        // Add click handler
        this.nodeElements.on('click', (event, d) => {
            this.handleNodeClick(d);
        });

        // Apply entrance animation
        if (this.animations.nodeEnter) {
            this.animations.nodeEnter(this.nodeElements);
        }
    }

    /**
     * Render links
     */
    renderLinks(container) {
        this.linkElements = container.selectAll('.link')
            .data(this.links, d => d.id)
            .enter()
            .append('line')
            .attr('class', 'link')
            .attr('stroke', this.config.colors.relationship)
            .attr('stroke-width', 2)
            .attr('stroke-opacity', 0.6)
            .style('cursor', 'pointer');

        // Add tooltip
        if (this.tooltip) {
            this.linkElements
                .on('mouseover', (event, d) => {
                    this.showTooltip(event, this.createLinkTooltip(d));
                })
                .on('mouseout', () => {
                    this.hideTooltip();
                });
        }

        // Add click handler
        this.linkElements.on('click', (event, d) => {
            this.handleLinkClick(d);
        });

        // Apply entrance animation
        if (this.animations.linkEnter) {
            this.animations.linkEnter(this.linkElements);
        }
    }

    /**
     * Render node labels
     */
    renderNodeLabels(container) {
        this.labelElements = container.selectAll('.node-label')
            .data(this.nodes, d => d.id)
            .enter()
            .append('text')
            .attr('class', 'node-label')
            .attr('text-anchor', 'middle')
            .attr('dy', '.35em')
            .attr('font-size', '10px')
            .attr('fill', '#333333')
            .text(d => d.properties?.name || d.properties?.title || d.id)
            .style('pointer-events', 'none');
    }

    /**
     * Render link labels
     */
    renderLinkLabels(container) {
        container.selectAll('.link-label')
            .data(this.links, d => d.id)
            .enter()
            .append('text')
            .attr('class', 'link-label')
            .attr('text-anchor', 'middle')
            .attr('font-size', '8px')
            .attr('fill', '#666666')
            .text(d => d.type)
            .style('pointer-events', 'none');
    }

    /**
     * Initialize simulation
     */
    initializeSimulation() {
        if (this.simulation) {
            this.simulation.stop();
        }

        const layout = this.layouts[this.config.layoutAlgorithm];
        if (!layout) {
            console.warn(`Layout algorithm '${this.config.layoutAlgorithm}' not found, using force`);
            this.simulation = this.layouts.force();
        } else {
            this.simulation = layout();
        }

        this.simulation
            .nodes(this.nodes)
            .on('tick', () => {
                this.updatePositions();
            });

        this.simulation.force('link')
            .links(this.links);

        this.simulation.alpha(this.config.alpha).restart();
    }

    /**
     * Update positions during simulation
     */
    updatePositions() {
        // Update link positions
        this.linkElements
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        // Update node positions
        this.nodeElements
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);

        // Update node label positions
        if (this.config.nodeLabels) {
            this.labelElements
                .attr('x', d => d.x)
                .attr('y', d => d.y);
        }

        // Update link label positions
        if (this.config.linkLabels) {
            this.svg.selectAll('.link-label')
                .attr('x', d => (d.source.x + d.target.x) / 2)
                .attr('y', d => (d.source.y + d.target.y) / 2);
        }
    }

    /**
     * Add a node to the graph
     */
    addNode(node) {
        this.nodes.push(node);
        this.renderGraph();
    }

    /**
     * Update a node in the graph
     */
    updateNode(node) {
        const index = this.nodes.findIndex(n => n.id === node.id);
        if (index !== -1) {
            this.nodes[index] = node;
            this.renderGraph();
        }
    }

    /**
     * Remove a node from the graph
     */
    removeNode(nodeId) {
        this.nodes = this.nodes.filter(n => n.id !== nodeId);
        this.links = this.links.filter(l => l.source !== nodeId && l.target !== nodeId);
        this.renderGraph();
    }

    /**
     * Add a link to the graph
     */
    addLink(relationship) {
        this.links.push(relationship);
        this.renderGraph();
    }

    /**
     * Update a link in the graph
     */
    updateLink(relationship) {
        const index = this.links.findIndex(l => l.id === relationship.id);
        if (index !== -1) {
            this.links[index] = relationship;
            this.renderGraph();
        }
    }

    /**
     * Remove a link from the graph
     */
    removeLink(relationshipId) {
        this.links = this.links.filter(l => l.id !== relationshipId);
        this.renderGraph();
    }

    /**
     * Update the entire graph
     */
    updateGraph(data) {
        this.nodes = data.nodes || this.nodes;
        this.links = data.relationships || this.links;
        this.renderGraph();
    }

    /**
     * Show tooltip
     */
    showTooltip(event, content) {
        if (this.tooltip) {
            this.tooltip
                .html(content)
                .style('left', (event.pageX + 10) + 'px')
                .style('top', (event.pageY - 10) + 'px')
                .transition()
                .duration(200)
                .style('opacity', 1);
        }
    }

    /**
     * Hide tooltip
     */
    hideTooltip() {
        if (this.tooltip) {
            this.tooltip
                .transition()
                .duration(200)
                .style('opacity', 0);
        }
    }

    /**
     * Create node tooltip content
     */
    createNodeTooltip(node) {
        return `
            <div>
                <strong>${node.properties?.name || node.properties?.title || 'Node'}</strong><br>
                Type: ${node.labels?.join(', ') || 'Unknown'}<br>
                ID: ${node.id}<br>
                ${Object.entries(node.properties || {}).map(([key, value]) => 
                    `${key}: ${value}`
                ).join('<br>')}
            </div>
        `;
    }

    /**
     * Create link tooltip content
     */
    createLinkTooltip(link) {
        return `
            <div>
                <strong>${link.type}</strong><br>
                From: ${link.source}<br>
                To: ${link.target}<br>
                ${Object.entries(link.properties || {}).map(([key, value]) => 
                    `${key}: ${value}`
                ).join('<br>')}
            </div>
        `;
    }

    /**
     * Handle node click
     */
    handleNodeClick(node) {
        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('kgNodeClicked', {
            detail: { node }
        }));

        // Highlight connected nodes
        this.highlightConnectedNodes(node.id);
    }

    /**
     * Handle link click
     */
    handleLinkClick(link) {
        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('kgLinkClicked', {
            detail: { link }
        }));
    }

    /**
     * Highlight connected nodes
     */
    highlightConnectedNodes(nodeId) {
        // Reset all nodes
        this.nodeElements
            .attr('opacity', 0.3)
            .attr('stroke-width', 2);

        // Highlight selected node
        this.nodeElements.filter(d => d.id === nodeId)
            .attr('opacity', 1)
            .attr('stroke-width', 4);

        // Highlight connected nodes
        const connectedNodeIds = new Set();
        this.links.forEach(link => {
            if (link.source === nodeId || link.target === nodeId) {
                connectedNodeIds.add(link.source === nodeId ? link.target : link.source);
            }
        });

        this.nodeElements.filter(d => connectedNodeIds.has(d.id))
            .attr('opacity', 0.8)
            .attr('stroke-width', 3);
    }

    /**
     * Reset highlighting
     */
    resetHighlighting() {
        this.nodeElements
            .attr('opacity', 1)
            .attr('stroke-width', 2);
    }

    /**
     * Zoom to fit
     */
    zoomToFit() {
        if (this.zoom) {
            const bounds = this.svg.select('.graph-group').node().getBBox();
            const fullWidth = this.config.width;
            const fullHeight = this.config.height;
            const width = bounds.width;
            const height = bounds.height;
            const midX = bounds.x + width / 2;
            const midY = bounds.y + height / 2;

            if (width === 0 || height === 0) return;

            const scale = 0.9 / Math.max(width / fullWidth, height / fullHeight);
            const translate = [fullWidth / 2 - scale * midX, fullHeight / 2 - scale * midY];

            this.svg.transition().duration(750).call(
                this.zoom.transform,
                d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale)
            );
        }
    }

    /**
     * Set layout algorithm
     */
    setLayoutAlgorithm(algorithm) {
        if (this.layouts[algorithm]) {
            this.config.layoutAlgorithm = algorithm;
            this.initializeSimulation();
        } else {
            console.warn(`Layout algorithm '${algorithm}' not found`);
        }
    }

    /**
     * Export graph as image
     */
    exportAsImage(format = 'png') {
        const svgElement = this.svg.node();
        const svgData = new XMLSerializer().serializeToString(svgElement);
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();

        canvas.width = this.config.width;
        canvas.height = this.config.height;

        img.onload = () => {
            ctx.drawImage(img, 0, 0);
            const dataURL = canvas.toDataURL(`image/${format}`);
            
            // Create download link
            const link = document.createElement('a');
            link.download = `knowledge-graph.${format}`;
            link.href = dataURL;
            link.click();
        };

        img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
    }

    /**
     * Refresh graph
     */
    async refreshGraph() {
        try {
            await this.loadGraphData();
            console.log('Graph refreshed');
        } catch (error) {
            console.error('Graph refresh failed:', error);
            throw error;
        }
    }

    /**
     * Destroy the visualization
     */
    destroy() {
        this.isInitialized = false;
        
        if (this.simulation) {
            this.simulation.stop();
            this.simulation = null;
        }

        if (this.svg) {
            this.svg.remove();
            this.svg = null;
        }

        if (this.tooltip) {
            this.tooltip.remove();
            this.tooltip = null;
        }

        this.nodes = [];
        this.links = [];
        this.nodeElements = [];
        this.linkElements = [];
        this.labelElements = [];
        this.zoom = null;
        this.drag = null;
        this.colorScale = null;
        this.layouts = {};
        this.animations = {};
        this.interactions = {};
        this.eventListeners.clear();

        console.log('🧹 Knowledge Graph Visualization destroyed');
    }
} 