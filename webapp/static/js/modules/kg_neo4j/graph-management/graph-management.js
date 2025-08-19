/**
 * Graph Management Module - Knowledge Graph Operations
 * @description Manages knowledge graph operations with authentication integration
 * @author AASX Framework Team
 * @version 1.0.0
 * @since 2025-01-27
 * @module kg_neo4j/graph-management/graph-management
 */

/**
 * Graph Management Class
 * @description Handles all graph management operations with proper authentication
 * @class GraphManagement
 * @author AASX Framework Team
 * @version 1.0.0
 * @since 2025-01-27
 */
export default class GraphManagement {
    // Private fields
    #isInitialized = false;
    #authSystem = null;
    #permissions = null;
    #sessionManager = null;
    #apiBaseUrl = '/api/kg_neo4j';
    #currentGraphs = [];
    #selectedGraphs = new Set();
    #config = {};
    #filters = {
        status: 'all',
        type: 'all',
        source: 'all',
        lifecycle: 'all'
    };
    
    /**
     * Create a GraphManagement instance
     * @param {Object} options - Configuration options
     * @param {string} options.apiBaseUrl - Base URL for API endpoints
     * @param {boolean} options.debug - Enable debug logging
     */
    constructor(options = {}) {
        this.#apiBaseUrl = options.apiBaseUrl || '/api/kg_neo4j';
        this.#config = {
            debug: options.debug ?? false
        };
        
        // Bind methods to preserve context
        this.refreshKnowledgeGraphData = this.refreshKnowledgeGraphData.bind(this);
        this.exportKnowledgeGraphData = this.exportKnowledgeGraphData.bind(this);
        this.kgShowRelationshipModal = this.kgShowRelationshipModal.bind(this);
        this.kgShowRelationships = this.kgShowRelationships.bind(this);
        this.kgViewGraphDetails = this.kgViewGraphDetails.bind(this);
        this.kgEditGraph = this.kgEditGraph.bind(this);
        this.kgSaveAllConfigurations = this.kgSaveAllConfigurations.bind(this);
        this.kgResetToDefaults = this.kgResetToDefaults.bind(this);
        this.handleKGConfigurationTabClick = this.handleKGConfigurationTabClick.bind(this);
    }
    
    /**
     * Initialize the graph management system
     * @param {Object} authSystem - Authentication system instance
     * @returns {Promise<void>}
     */
    async initialize(authSystem) {
        try {
            if (this.#isInitialized) {
                console.warn('GraphManagement already initialized');
                return;
            }
            
            // Store auth system references
            this.#authSystem = authSystem;
            this.#permissions = window.Permissions;
            this.#sessionManager = window.SessionManager;
            
            // Verify authentication
            if (!this.#authSystem || !this.#permissions) {
                throw new Error('Authentication system not available');
            }
            
            // Check permissions
            if (!this.#permissions.hasPermission('kg_neo4j', 'view')) {
                throw new Error('Insufficient permissions for Knowledge Graph access');
            }
            
            this.#isInitialized = true;
            this.#log('GraphManagement initialized successfully');
            
            // Initialize UI event listeners
            this.#initializeEventListeners();
            
        } catch (error) {
            this.#log('GraphManagement initialization failed:', error);
            throw error;
        }
    }
    
    /**
     * Check if user has permission for specific operation
     * @param {string} operation - Operation to check
     * @returns {boolean}
     */
    #hasPermission(operation) {
        if (!this.#permissions) return false;
        return this.#permissions.hasPermission('kg_neo4j', operation);
    }
    
    /**
     * Get authenticated API headers
     * @returns {Object}
     */
    #getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (this.#sessionManager && this.#sessionManager.getToken()) {
            headers['Authorization'] = `Bearer ${this.#sessionManager.getToken()}`;
        }
        
        return headers;
    }
    
    /**
     * Make authenticated API request
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise<Object>}
     */
    async #apiRequest(endpoint, options = {}) {
        const url = `${this.#apiBaseUrl}${endpoint}`;
        const config = {
            method: 'GET',
            headers: this.#getAuthHeaders(),
            ...options
        };
        
        if (options.body) {
            config.body = JSON.stringify(options.body);
        }
        
        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                if (response.status === 401) {
                    // Handle authentication error
                    this.#handleAuthError();
                    return null;
                }
                throw new Error(`API request failed: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            this.#log('API request failed:', error);
            throw error;
        }
    }
    
    /**
     * Handle authentication errors
     */
    #handleAuthError() {
        this.#log('Authentication error detected');
        // Redirect to login or show auth modal
        if (window.AuthUIManager) {
            window.AuthUIManager.showLoginModal();
        }
    }
    
    /**
     * Initialize event listeners
     */
    #initializeEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('kg-refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', this.refreshKnowledgeGraphData);
        }
        
        // Export button
        const exportBtn = document.getElementById('kg-export-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', this.exportKnowledgeGraphData);
        }
        
        // Filter changes
        const filterSelects = document.querySelectorAll('.kg-filter-select');
        filterSelects.forEach(select => {
            select.addEventListener('change', this.#handleFilterChange.bind(this));
        });
        
        // Bulk operations
        const bulkSelectAll = document.getElementById('kg-bulk-select-all');
        if (bulkSelectAll) {
            bulkSelectAll.addEventListener('change', this.#handleBulkSelectAll.bind(this));
        }
        
        // Graph selection
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('kg-graph-checkbox')) {
                this.#handleGraphSelection(e);
            }
        });
    }
    
    /**
     * Handle filter changes
     * @param {Event} event - Change event
     */
    #handleFilterChange(event) {
        const filterType = event.target.dataset.filter;
        const value = event.target.value;
        
        this.#filters[filterType] = value;
        this.#applyFilters();
    }
    
    /**
     * Apply current filters to graph list
     */
    #applyFilters() {
        const graphRows = document.querySelectorAll('.kg-graph-row');
        
        graphRows.forEach(row => {
            const status = row.dataset.status;
            const type = row.dataset.type;
            const source = row.dataset.source;
            const lifecycle = row.dataset.lifecycle;
            
            const statusMatch = this.#filters.status === 'all' || status === this.#filters.status;
            const typeMatch = this.#filters.type === 'all' || type === this.#filters.type;
            const sourceMatch = this.#filters.source === 'all' || source === this.#filters.source;
            const lifecycleMatch = this.#filters.lifecycle === 'all' || lifecycle === this.#filters.lifecycle;
            
            if (statusMatch && typeMatch && sourceMatch && lifecycleMatch) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }
    
    /**
     * Handle bulk select all
     * @param {Event} event - Change event
     */
    #handleBulkSelectAll(event) {
        const isChecked = event.target.checked;
        const checkboxes = document.querySelectorAll('.kg-graph-checkbox');
        
        checkboxes.forEach(checkbox => {
            checkbox.checked = isChecked;
            this.#handleGraphSelection({ target: checkbox });
        });
    }
    
    /**
     * Handle individual graph selection
     * @param {Event} event - Change event
     */
    #handleGraphSelection(event) {
        const checkbox = event.target;
        const graphId = checkbox.value;
        
        if (checkbox.checked) {
            this.#selectedGraphs.add(graphId);
        } else {
            this.#selectedGraphs.delete(graphId);
        }
        
        this.#updateBulkOperationsVisibility();
    }
    
    /**
     * Update bulk operations panel visibility
     */
    #updateBulkOperationsVisibility() {
        const bulkPanel = document.querySelector('.kg-bulk-operations');
        if (bulkPanel) {
            if (this.#selectedGraphs.size > 0) {
                bulkPanel.style.display = 'block';
            } else {
                bulkPanel.style.display = 'none';
            }
        }
    }
    
    /**
     * Log messages with debug option
     * @param {...any} args - Arguments to log
     */
    #log(...args) {
        if (this.#config.debug) {
            console.log('[GraphManagement]', ...args);
        }
    }
    
    // ===== PUBLIC API METHODS =====
    
    /**
     * Refresh knowledge graph data
     * @returns {Promise<void>}
     */
    async refreshKnowledgeGraphData() {
        if (!this.#hasPermission('view')) {
            this.#log('Permission denied: view');
            return;
        }
        
        try {
            this.#log('Refreshing knowledge graph data...');
            
            // Show loading state
            this.#showLoadingState();
            
            // Fetch graphs data
            const data = await this.#apiRequest('/graphs');
            
            if (data) {
                this.#currentGraphs = data.graphs || [];
                this.#updateGraphTable();
                this.#updateHealthCards();
                this.#updateSourceOverview();
            }
            
            this.#hideLoadingState();
            this.#log('Data refresh completed');
            
        } catch (error) {
            this.#hideLoadingState();
            this.#log('Data refresh failed:', error);
            this.#showError('Failed to refresh data');
        }
    }
    
    /**
     * Export knowledge graph data
     * @returns {Promise<void>}
     */
    async exportKnowledgeGraphData() {
        if (!this.#hasPermission('export')) {
            this.#log('Permission denied: export');
            return;
        }
        
        try {
            this.#log('Exporting knowledge graph data...');
            
            const data = await this.#apiRequest('/graphs/export');
            
            if (data) {
                // Create and download file
                const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `kg_export_${new Date().toISOString().split('T')[0]}.json`;
                a.click();
                URL.revokeObjectURL(url);
            }
            
        } catch (error) {
            this.#log('Export failed:', error);
            this.#showError('Failed to export data');
        }
    }
    
    /**
     * Show relationship modal
     * @param {string} graphId - Graph ID
     */
    kgShowRelationshipModal(graphId) {
        if (!this.#hasPermission('view_relationships')) {
            this.#log('Permission denied: view_relationships');
            return;
        }
        
        this.#log('Showing relationship modal for graph:', graphId);
        // Implementation for relationship modal
    }
    
    /**
     * Show relationships
     * @param {string} graphId - Graph ID
     */
    kgShowRelationships(graphId) {
        if (!this.#hasPermission('view_relationships')) {
            this.#log('Permission denied: view_relationships');
            return;
        }
        
        this.#log('Showing relationships for graph:', graphId);
        // Implementation for showing relationships
    }
    
    /**
     * View graph details
     * @param {string} graphId - Graph ID
     */
    kgViewGraphDetails(graphId) {
        if (!this.#hasPermission('view')) {
            this.#log('Permission denied: view');
            return;
        }
        
        this.#log('Viewing graph details for:', graphId);
        // Implementation for viewing graph details
    }
    
    /**
     * Edit graph
     * @param {string} graphId - Graph ID
     */
    kgEditGraph(graphId) {
        if (!this.#hasPermission('edit')) {
            this.#log('Permission denied: edit');
            return;
        }
        
        this.#log('Editing graph:', graphId);
        // Implementation for editing graph
    }
    
    /**
     * Save all configurations
     * @returns {Promise<void>}
     */
    async kgSaveAllConfigurations() {
        if (!this.#hasPermission('edit')) {
            this.#log('Permission denied: edit');
            return;
        }
        
        try {
            this.#log('Saving all configurations...');
            // Implementation for saving configurations
        } catch (error) {
            this.#log('Save failed:', error);
            this.#showError('Failed to save configurations');
        }
    }
    
    /**
     * Reset to defaults
     * @returns {Promise<void>}
     */
    async kgResetToDefaults() {
        if (!this.#hasPermission('admin')) {
            this.#log('Permission denied: admin');
            return;
        }
        
        try {
            this.#log('Resetting to defaults...');
            // Implementation for resetting to defaults
        } catch (error) {
            this.#log('Reset failed:', error);
            this.#showError('Failed to reset to defaults');
        }
    }
    
    /**
     * Handle configuration tab click
     * @param {Event} event - Click event
     */
    handleKGConfigurationTabClick(event) {
        this.#log('Configuration tab clicked');
        // Implementation for configuration tab handling
    }
    
    // ===== UI UPDATE METHODS =====
    
    /**
     * Update graph table
     */
    #updateGraphTable() {
        const tbody = document.querySelector('.kg-table tbody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        this.#currentGraphs.forEach(graph => {
            const row = this.#createGraphRow(graph);
            tbody.appendChild(row);
        });
    }
    
    /**
     * Create graph table row
     * @param {Object} graph - Graph data
     * @returns {HTMLElement}
     */
    #createGraphRow(graph) {
        const row = document.createElement('tr');
        row.className = 'kg-graph-row';
        row.dataset.status = graph.status;
        row.dataset.type = graph.type;
        row.dataset.source = graph.source;
        row.dataset.lifecycle = graph.lifecycle;
        
        row.innerHTML = `
            <td>
                <input type="checkbox" class="kg-graph-checkbox" value="${graph.id}">
            </td>
            <td>${graph.name}</td>
            <td><span class="kg-status-badge kg-status-${graph.status}">${graph.status}</span></td>
            <td>${graph.type}</td>
            <td>${graph.source}</td>
            <td>${graph.nodes_count}</td>
            <td>${graph.relationships_count}</td>
            <td>
                <div class="kg-action-buttons">
                    <button class="kg-btn kg-btn-sm" onclick="window.graphManagement.kgViewGraphDetails('${graph.id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="kg-btn kg-btn-sm" onclick="window.graphManagement.kgEditGraph('${graph.id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="kg-btn kg-btn-sm" onclick="window.graphManagement.kgShowRelationships('${graph.id}')">
                        <i class="fas fa-project-diagram"></i>
                    </button>
                </div>
            </td>
        `;
        
        return row;
    }
    
    /**
     * Update health cards
     */
    #updateHealthCards() {
        const totalGraphs = this.#currentGraphs.length;
        const activeGraphs = this.#currentGraphs.filter(g => g.status === 'active').length;
        const totalNodes = this.#currentGraphs.reduce((sum, g) => sum + (g.nodes_count || 0), 0);
        const pendingGraphs = this.#currentGraphs.filter(g => g.status === 'pending').length;
        
        this.#updateHealthCard('total-graphs', totalGraphs);
        this.#updateHealthCard('active-graphs', activeGraphs);
        this.#updateHealthCard('total-nodes', totalNodes);
        this.#updateHealthCard('pending-graphs', pendingGraphs);
    }
    
    /**
     * Update health card value
     * @param {string} cardId - Card ID
     * @param {number} value - Value to display
     */
    #updateHealthCard(cardId, value) {
        const card = document.getElementById(cardId);
        if (card) {
            const valueElement = card.querySelector('.kg-health-value');
            if (valueElement) {
                valueElement.textContent = value.toLocaleString();
            }
        }
    }
    
    /**
     * Update source overview
     */
    #updateSourceOverview() {
        const sources = {
            aasx: this.#currentGraphs.filter(g => g.source === 'AASX-ETL').length,
            twin: this.#currentGraphs.filter(g => g.source === 'Twin Registry').length,
            ai: this.#currentGraphs.filter(g => g.source === 'AI/RAG').length
        };
        
        Object.entries(sources).forEach(([source, count]) => {
            const card = document.querySelector(`.kg-source-${source} .kg-source-count`);
            if (card) {
                card.textContent = count;
            }
        });
    }
    
    /**
     * Show loading state
     */
    #showLoadingState() {
        const loadingElement = document.querySelector('.kg-loading');
        if (loadingElement) {
            loadingElement.style.display = 'block';
        }
    }
    
    /**
     * Hide loading state
     */
    #hideLoadingState() {
        const loadingElement = document.querySelector('.kg-loading');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
    }
    
    /**
     * Show error message
     * @param {string} message - Error message
     */
    #showError(message) {
        // Implementation for showing error messages
        console.error('[GraphManagement Error]', message);
    }
    
    /**
     * Cleanup resources
     */
    cleanup() {
        this.#isInitialized = false;
        this.#currentGraphs = [];
        this.#selectedGraphs.clear();
        this.#log('GraphManagement cleaned up');
    }
}

// Export singleton instance
export const graphManagement = new GraphManagement();
