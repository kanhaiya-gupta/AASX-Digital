/**
 * Neo4j Operations Tab JavaScript Module - World Class Edition
 * ES6 Class-based implementation with central authentication integration
 * Features sophisticated Docker management, performance monitoring, and graph operations
 */

import { AuthManager } from '../../auth/auth_manager.js';
import { Logger } from '../../utils/logger.js';
import { ApiClient } from '../../api/api_client.js';

class Neo4jOpsManager {
    constructor() {
        this.authManager = new AuthManager();
        this.logger = new Logger('Neo4jOpsManager');
        this.apiClient = new ApiClient();
        
        // State management
        this.containerStatus = {
            running: false,
            containerId: null,
            image: null,
            created: null,
            size: null,
            command: null,
            uptime: '0h',
            memory: '0 MB',
            port: '7474'
        };
        
        this.performanceMetrics = {
            cpu: 0,
            memory: 0,
            disk: 0,
            network: 0
        };
        
        this.queryHistory = [];
        this.logSettings = {
            level: 'all',
            lines: 500,
            follow: false
        };
        
        // DOM elements cache
        this.elements = {};
        
        // Initialize the manager
        this.init();
    }
    
    /**
     * Initialize the Neo4j OPS manager
     */
    async init() {
        try {
            // Check authentication
            if (!await this.authManager.isAuthenticated()) {
                this.logger.warn('User not authenticated, redirecting to login');
                window.location.href = '/login';
                return;
            }
            
            // Cache DOM elements
            this.cacheElements();
            
            // Bind event listeners
            this.bindEventListeners();
            
            // Initialize real-time updates
            this.initializeRealTimeUpdates();
            
            // Load initial data
            await this.loadInitialData();
            
            this.logger.info('Neo4j OPS Manager initialized successfully');
            
        } catch (error) {
            this.logger.error('Failed to initialize Neo4j OPS Manager:', error);
            this.showError('Failed to initialize Neo4j OPS Manager');
        }
    }
    
    /**
     * Cache DOM elements for performance
     */
    cacheElements() {
        this.elements = {
            // Status elements
            status: document.getElementById('neo4j-status'),
            uptime: document.getElementById('neo4j-uptime'),
            memory: document.getElementById('neo4j-memory'),
            port: document.getElementById('neo4j-port'),
            
            // Container info
            containerId: document.getElementById('container-id'),
            containerImage: document.getElementById('container-image'),
            containerCreated: document.getElementById('container-created'),
            containerSize: document.getElementById('container-size'),
            containerCommand: document.getElementById('container-command'),
            
            // Performance elements
            cpuUsageBar: document.getElementById('cpu-usage-bar'),
            cpuUsageText: document.getElementById('cpu-usage-text'),
            memoryUsageBar: document.getElementById('memory-usage-bar'),
            memoryUsageText: document.getElementById('memory-usage-text'),
            diskUsageBar: document.getElementById('disk-usage-bar'),
            diskUsageText: document.getElementById('disk-usage-text'),
            networkIO: document.getElementById('network-io'),
            
            // Form elements
            graphFile: document.getElementById('graph-file'),
            graphFormat: document.getElementById('graph-format'),
            exportFormat: document.getElementById('export-format'),
            exportQuery: document.getElementById('export-query'),
            
            // Query elements
            cypherQuery: document.getElementById('cypher-query'),
            queryParameters: document.getElementById('query-parameters'),
            queryHistory: document.getElementById('query-history'),
            queryResults: document.getElementById('query-results-container'),
            
            // Log elements
            logLevel: document.getElementById('log-level'),
            logLines: document.getElementById('log-lines'),
            logFollow: document.getElementById('log-follow'),
            containerLogs: document.getElementById('container-logs'),
            
            // Buttons
            startBtn: document.getElementById('start-btn'),
            stopBtn: document.getElementById('stop-btn'),
            restartBtn: document.getElementById('restart-btn'),
            removeBtn: document.getElementById('remove-btn')
        };
    }
    
    /**
     * Bind event listeners to DOM elements
     */
    bindEventListeners() {
        // Container control buttons
        if (this.elements.startBtn) {
            this.elements.startBtn.addEventListener('click', () => this.startNeo4j());
        }
        if (this.elements.stopBtn) {
            this.elements.stopBtn.addEventListener('click', () => this.stopNeo4j());
        }
        if (this.elements.restartBtn) {
            this.elements.restartBtn.addEventListener('click', () => this.restartNeo4j());
        }
        if (this.elements.removeBtn) {
            this.elements.removeBtn.addEventListener('click', () => this.removeNeo4j());
        }
        
        // Form submissions
        const importForm = document.querySelector('.import-form');
        if (importForm) {
            importForm.addEventListener('submit', (e) => this.handleImportSubmit(e));
        }
        
        const exportForm = document.querySelector('.export-form');
        if (exportForm) {
            exportForm.addEventListener('submit', (e) => this.handleExportSubmit(e));
        }
        
        // Query execution
        const executeBtn = document.querySelector('[onclick="executeCypherQuery()"]');
        if (executeBtn) {
            executeBtn.addEventListener('click', () => this.executeCypherQuery());
        }
        
        // Log settings
        if (this.elements.logLevel) {
            this.elements.logLevel.addEventListener('change', () => this.applyLogSettings());
        }
        if (this.elements.logLines) {
            this.elements.logLines.addEventListener('change', () => this.applyLogSettings());
        }
        if (this.elements.logFollow) {
            this.elements.logFollow.addEventListener('change', () => this.applyLogSettings());
        }
        
        // File input change
        if (this.elements.graphFile) {
            this.elements.graphFile.addEventListener('change', (e) => this.handleFileSelection(e));
        }
    }
    
    /**
     * Initialize real-time updates
     */
    initializeRealTimeUpdates() {
        // Update status every 5 seconds
        setInterval(() => this.refreshNeo4jStatus(), 5000);
        
        // Update performance metrics every 3 seconds
        setInterval(() => this.updatePerformanceMetrics(), 3000);
        
        // Update logs if following is enabled
        setInterval(() => this.updateLogsIfFollowing(), 2000);
    }
    
    /**
     * Load initial data
     */
    async loadInitialData() {
        try {
            await Promise.all([
                this.refreshNeo4jStatus(),
                this.loadQueryHistory(),
                this.loadLogSettings()
            ]);
        } catch (error) {
            this.logger.error('Failed to load initial data:', error);
        }
    }
    
    /**
     * Start Neo4j container
     */
    async startNeo4j() {
        try {
            this.setButtonLoading(this.elements.startBtn, true);
            
            const response = await this.apiClient.post('/api/neo4j/start', {}, {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.showSuccess('Neo4j container started successfully');
                await this.refreshNeo4jStatus();
            } else {
                this.showError(response.message || 'Failed to start Neo4j container');
            }
            
        } catch (error) {
            this.logger.error('Failed to start Neo4j:', error);
            this.showError('Failed to start Neo4j container');
        } finally {
            this.setButtonLoading(this.elements.startBtn, false);
        }
    }
    
    /**
     * Stop Neo4j container
     */
    async stopNeo4j() {
        try {
            this.setButtonLoading(this.elements.stopBtn, true);
            
            const response = await this.apiClient.post('/api/neo4j/stop', {}, {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.showSuccess('Neo4j container stopped successfully');
                await this.refreshNeo4jStatus();
            } else {
                this.showError(response.message || 'Failed to stop Neo4j container');
            }
            
        } catch (error) {
            this.logger.error('Failed to stop Neo4j:', error);
            this.showError('Failed to stop Neo4j container');
        } finally {
            this.setButtonLoading(this.elements.stopBtn, false);
        }
    }
    
    /**
     * Restart Neo4j container
     */
    async restartNeo4j() {
        try {
            this.setButtonLoading(this.elements.restartBtn, true);
            
            const response = await this.apiClient.post('/api/neo4j/restart', {}, {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.showSuccess('Neo4j container restarted successfully');
                await this.refreshNeo4jStatus();
            } else {
                this.showError(response.message || 'Failed to restart Neo4j container');
            }
            
        } catch (error) {
            this.logger.error('Failed to restart Neo4j:', error);
            this.showError('Failed to restart Neo4j container');
        } finally {
            this.setButtonLoading(this.elements.restartBtn, false);
        }
    }
    
    /**
     * Remove Neo4j container
     */
    async removeNeo4j() {
        if (!confirm('Are you sure you want to remove the Neo4j container? This action cannot be undone.')) {
            return;
        }
        
        try {
            this.setButtonLoading(this.elements.removeBtn, true);
            
            const response = await this.apiClient.delete('/api/neo4j/remove', {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.showSuccess('Neo4j container removed successfully');
                await this.refreshNeo4jStatus();
            } else {
                this.showError(response.message || 'Failed to remove Neo4j container');
            }
            
        } catch (error) {
            this.logger.error('Failed to remove Neo4j:', error);
            this.showError('Failed to remove Neo4j container');
        } finally {
            this.setButtonLoading(this.elements.removeBtn, false);
        }
    }
    
    /**
     * Refresh Neo4j status
     */
    async refreshNeo4jStatus() {
        try {
            const response = await this.apiClient.get('/api/neo4j/status', {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.updateContainerStatus(response.data);
            }
            
        } catch (error) {
            this.logger.error('Failed to refresh Neo4j status:', error);
        }
    }
    
    /**
     * Update container status display
     */
    updateContainerStatus(statusData) {
        this.containerStatus = { ...this.containerStatus, ...statusData };
        
        // Update status display
        if (this.elements.status) {
            this.elements.status.textContent = statusData.running ? 'Running' : 'Stopped';
            this.elements.status.className = statusData.running ? 'text-success' : 'text-danger';
        }
        
        if (this.elements.uptime) {
            this.elements.uptime.textContent = statusData.uptime || '0h';
        }
        
        if (this.elements.memory) {
            this.elements.memory.textContent = statusData.memory || '0 MB';
        }
        
        if (this.elements.port) {
            this.elements.port.textContent = statusData.port || '7474';
        }
        
        // Update container info table
        if (this.elements.containerId) {
            this.elements.containerId.textContent = statusData.containerId || 'N/A';
        }
        if (this.elements.containerImage) {
            this.elements.containerImage.textContent = statusData.image || 'N/A';
        }
        if (this.elements.containerCreated) {
            this.elements.containerCreated.textContent = statusData.created || 'N/A';
        }
        if (this.elements.containerSize) {
            this.elements.containerSize.textContent = statusData.size || 'N/A';
        }
        if (this.elements.containerCommand) {
            this.elements.containerCommand.textContent = statusData.command || 'N/A';
        }
        
        // Update button states
        this.updateButtonStates(statusData.running);
    }
    
    /**
     * Update button states based on container status
     */
    updateButtonStates(isRunning) {
        if (this.elements.startBtn) {
            this.elements.startBtn.disabled = isRunning;
            this.elements.startBtn.classList.toggle('btn-success', !isRunning);
            this.elements.startBtn.classList.toggle('btn-secondary', isRunning);
        }
        
        if (this.elements.stopBtn) {
            this.elements.stopBtn.disabled = !isRunning;
            this.elements.stopBtn.classList.toggle('btn-warning', isRunning);
            this.elements.stopBtn.classList.toggle('btn-secondary', !isRunning);
        }
        
        if (this.elements.restartBtn) {
            this.elements.restartBtn.disabled = !isRunning;
        }
        
        if (this.elements.removeBtn) {
            this.elements.removeBtn.disabled = isRunning;
        }
    }
    
    /**
     * Update performance metrics
     */
    async updatePerformanceMetrics() {
        try {
            const response = await this.apiClient.get('/api/neo4j/performance', {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.updatePerformanceDisplay(response.data);
            }
            
        } catch (error) {
            this.logger.error('Failed to update performance metrics:', error);
        }
    }
    
    /**
     * Update performance display
     */
    updatePerformanceDisplay(metrics) {
        this.performanceMetrics = { ...this.performanceMetrics, ...metrics };
        
        // Update CPU usage
        if (this.elements.cpuUsageBar && this.elements.cpuUsageText) {
            const cpuPercent = Math.round(metrics.cpu || 0);
            this.elements.cpuUsageBar.style.width = `${cpuPercent}%`;
            this.elements.cpuUsageText.textContent = `${cpuPercent}%`;
        }
        
        // Update memory usage
        if (this.elements.memoryUsageBar && this.elements.memoryUsageText) {
            const memoryPercent = Math.round(metrics.memory || 0);
            this.elements.memoryUsageBar.style.width = `${memoryPercent}%`;
            this.elements.memoryUsageText.textContent = `${metrics.memoryUsed || 0} MB / ${metrics.memoryTotal || 0} MB`;
        }
        
        // Update disk usage
        if (this.elements.diskUsageBar && this.elements.diskUsageText) {
            const diskPercent = Math.round(metrics.disk || 0);
            this.elements.diskUsageBar.style.width = `${diskPercent}%`;
            this.elements.diskUsageText.textContent = `${metrics.diskUsed || 0} MB / ${metrics.diskTotal || 0} MB`;
        }
        
        // Update network I/O
        if (this.elements.networkIO) {
            this.elements.networkIO.value = `${metrics.network || 0} KB/s`;
        }
    }
    
    /**
     * Handle graph data import
     */
    async handleImportSubmit(event) {
        event.preventDefault();
        
        try {
            const formData = new FormData();
            const file = this.elements.graphFile.files[0];
            
            if (!file) {
                this.showError('Please select a file to import');
                return;
            }
            
            formData.append('file', file);
            formData.append('format', this.elements.graphFormat.value);
            formData.append('clearExisting', document.getElementById('clear-existing').checked);
            formData.append('createIndexes', document.getElementById('create-indexes').checked);
            formData.append('validateData', document.getElementById('validate-data').checked);
            
            const response = await this.apiClient.post('/api/neo4j/import', formData, {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.showSuccess('Graph data imported successfully');
                this.elements.graphFile.value = '';
            } else {
                this.showError(response.message || 'Failed to import graph data');
            }
            
        } catch (error) {
            this.logger.error('Failed to import graph data:', error);
            this.showError('Failed to import graph data');
        }
    }
    
    /**
     * Handle graph data export
     */
    async handleExportSubmit(event) {
        event.preventDefault();
        
        try {
            const exportData = {
                format: this.elements.exportFormat.value,
                query: this.elements.exportQuery.value,
                includeProperties: document.getElementById('include-properties').checked,
                includeLabels: document.getElementById('include-labels').checked,
                includeRelationships: document.getElementById('include-relationships').checked
            };
            
            const response = await this.apiClient.post('/api/neo4j/export', exportData, {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                // Create download link
                const blob = new Blob([response.data], { type: 'application/octet-stream' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `neo4j_export_${Date.now()}.${exportData.format}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                this.showSuccess('Graph data exported successfully');
            } else {
                this.showError(response.message || 'Failed to export graph data');
            }
            
        } catch (error) {
            this.logger.error('Failed to export graph data:', error);
            this.showError('Failed to export graph data');
        }
    }
    
    /**
     * Execute Cypher query
     */
    async executeCypherQuery() {
        try {
            const query = this.elements.cypherQuery.value.trim();
            if (!query) {
                this.showError('Please enter a Cypher query');
                return;
            }
            
            let parameters = {};
            try {
                const paramsText = this.elements.queryParameters.value.trim();
                if (paramsText) {
                    parameters = JSON.parse(paramsText);
                }
            } catch (e) {
                this.showError('Invalid JSON parameters');
                return;
            }
            
            const response = await this.apiClient.post('/api/neo4j/query', {
                query,
                parameters
            }, {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.displayQueryResults(response.data);
                this.saveQueryToHistory(query);
            } else {
                this.showError(response.message || 'Query execution failed');
            }
            
        } catch (error) {
            this.logger.error('Failed to execute Cypher query:', error);
            this.showError('Failed to execute query');
        }
    }
    
    /**
     * Display query results
     */
    displayQueryResults(results) {
        if (!this.elements.queryResults) return;
        
        if (!results || results.length === 0) {
            this.elements.queryResults.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-info-circle fa-3x text-muted mb-3"></i>
                    <p class="text-muted">Query executed successfully. No results returned.</p>
                </div>
            `;
            return;
        }
        
        // Create results table
        let tableHTML = `
            <div class="table-responsive">
                <table class="table table-striped table-hover">
                    <thead class="table-dark">
                        <tr>
        `;
        
        // Add headers
        const firstResult = results[0];
        Object.keys(firstResult).forEach(key => {
            tableHTML += `<th>${key}</th>`;
        });
        tableHTML += '</tr></thead><tbody>';
        
        // Add data rows
        results.forEach(row => {
            tableHTML += '<tr>';
            Object.values(row).forEach(value => {
                const displayValue = typeof value === 'object' ? JSON.stringify(value) : String(value);
                tableHTML += `<td>${displayValue}</td>`;
            });
            tableHTML += '</tr>';
        });
        
        tableHTML += '</tbody></table></div>';
        
        this.elements.queryResults.innerHTML = tableHTML;
    }
    
    /**
     * Save query to history
     */
    saveQueryToHistory(query) {
        if (!query.trim()) return;
        
        // Remove if already exists
        this.queryHistory = this.queryHistory.filter(q => q !== query);
        
        // Add to beginning
        this.queryHistory.unshift(query);
        
        // Keep only last 10 queries
        if (this.queryHistory.length > 10) {
            this.queryHistory = this.queryHistory.slice(0, 10);
        }
        
        // Save to localStorage
        localStorage.setItem('neo4j_query_history', JSON.stringify(this.queryHistory));
        
        // Update select dropdown
        this.updateQueryHistoryDropdown();
    }
    
    /**
     * Load query history
     */
    loadQueryHistory() {
        try {
            const saved = localStorage.getItem('neo4j_query_history');
            if (saved) {
                this.queryHistory = JSON.parse(saved);
                this.updateQueryHistoryDropdown();
            }
        } catch (error) {
            this.logger.error('Failed to load query history:', error);
        }
    }
    
    /**
     * Update query history dropdown
     */
    updateQueryHistoryDropdown() {
        if (!this.elements.queryHistory) return;
        
        // Clear existing options except the first one
        while (this.elements.queryHistory.children.length > 1) {
            this.elements.queryHistory.removeChild(this.elements.queryHistory.lastChild);
        }
        
        // Add history options
        this.queryHistory.forEach(query => {
            const option = document.createElement('option');
            option.value = query;
            option.textContent = query.length > 50 ? query.substring(0, 50) + '...' : query;
            this.elements.queryHistory.appendChild(option);
        });
    }
    
    /**
     * Load query from history
     */
    loadQueryFromHistory() {
        if (!this.elements.queryHistory || !this.elements.cypherQuery) return;
        
        const selectedQuery = this.elements.queryHistory.value;
        if (selectedQuery) {
            this.elements.cypherQuery.value = selectedQuery;
        }
    }
    
    /**
     * Clear query fields
     */
    clearQuery() {
        if (this.elements.cypherQuery) {
            this.elements.cypherQuery.value = '';
        }
        if (this.elements.queryParameters) {
            this.elements.queryParameters.value = '';
        }
    }
    
    /**
     * Clear query results
     */
    clearResults() {
        if (this.elements.queryResults) {
            this.elements.queryResults.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-database fa-3x text-muted mb-3"></i>
                    <p class="text-muted">No query results yet. Execute a Cypher query to see results here.</p>
                </div>
            `;
        }
    }
    
    /**
     * Apply log settings
     */
    async applyLogSettings() {
        try {
            this.logSettings = {
                level: this.elements.logLevel.value,
                lines: this.elements.logLines.value,
                follow: this.elements.logFollow.checked
            };
            
            // Save to localStorage
            localStorage.setItem('neo4j_log_settings', JSON.stringify(this.logSettings));
            
            // Refresh logs
            await this.refreshLogs();
            
            this.showSuccess('Log settings applied successfully');
            
        } catch (error) {
            this.logger.error('Failed to apply log settings:', error);
            this.showError('Failed to apply log settings');
        }
    }
    
    /**
     * Load log settings
     */
    loadLogSettings() {
        try {
            const saved = localStorage.getItem('neo4j_log_settings');
            if (saved) {
                this.logSettings = JSON.parse(saved);
                
                // Apply to DOM
                if (this.elements.logLevel) {
                    this.elements.logLevel.value = this.logSettings.level;
                }
                if (this.elements.logLines) {
                    this.elements.logLines.value = this.logSettings.lines;
                }
                if (this.elements.logFollow) {
                    this.elements.logFollow.checked = this.logSettings.follow;
                }
            }
        } catch (error) {
            this.logger.error('Failed to load log settings:', error);
        }
    }
    
    /**
     * Refresh container logs
     */
    async refreshLogs() {
        try {
            const response = await this.apiClient.get('/api/neo4j/logs', {
                params: this.logSettings,
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success && this.elements.containerLogs) {
                this.elements.containerLogs.textContent = response.data.logs || 'No logs available';
                
                // Auto-scroll if following is enabled
                if (this.logSettings.follow) {
                    this.elements.containerLogs.scrollTop = this.elements.containerLogs.scrollHeight;
                }
            }
            
        } catch (error) {
            this.logger.error('Failed to refresh logs:', error);
        }
    }
    
    /**
     * Update logs if following is enabled
     */
    updateLogsIfFollowing() {
        if (this.logSettings.follow) {
            this.refreshLogs();
        }
    }
    
    /**
     * Clear container logs
     */
    clearLogs() {
        if (this.elements.containerLogs) {
            this.elements.containerLogs.textContent = '';
        }
    }
    
    /**
     * Download container logs
     */
    async downloadLogs() {
        try {
            const response = await this.apiClient.get('/api/neo4j/logs/download', {
                params: this.logSettings,
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                // Create download link
                const blob = new Blob([response.data], { type: 'text/plain' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `neo4j_logs_${Date.now()}.txt`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                this.showSuccess('Logs downloaded successfully');
            } else {
                this.showError(response.message || 'Failed to download logs');
            }
            
        } catch (error) {
            this.logger.error('Failed to download logs:', error);
            this.showError('Failed to download logs');
        }
    }
    
    /**
     * Export query results
     */
    exportResults() {
        const resultsContainer = this.elements.queryResults;
        if (!resultsContainer || resultsContainer.innerHTML.includes('No query results yet')) {
            this.showError('No results to export');
            return;
        }
        
        // Create CSV from table data
        const table = resultsContainer.querySelector('table');
        if (!table) return;
        
        let csv = '';
        const rows = table.querySelectorAll('tr');
        
        rows.forEach(row => {
            const cols = row.querySelectorAll('th, td');
            const rowData = Array.from(cols).map(col => `"${col.textContent}"`);
            csv += rowData.join(',') + '\n';
        });
        
        // Download CSV
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `neo4j_results_${Date.now()}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        this.showSuccess('Results exported successfully');
    }
    
    /**
     * Handle file selection
     */
    handleFileSelection(event) {
        const file = event.target.files[0];
        if (file) {
            // Auto-detect format based on file extension
            const extension = file.name.split('.').pop().toLowerCase();
            if (this.elements.graphFormat) {
                switch (extension) {
                    case 'json':
                        this.elements.graphFormat.value = 'json';
                        break;
                    case 'csv':
                        this.elements.graphFormat.value = 'csv';
                        break;
                    case 'xml':
                        this.elements.graphFormat.value = 'xml';
                        break;
                    default:
                        this.elements.graphFormat.value = 'auto';
                }
            }
        }
    }
    
    /**
     * Set button loading state
     */
    setButtonLoading(button, isLoading) {
        if (!button) return;
        
        if (isLoading) {
            button.classList.add('loading');
            button.disabled = true;
        } else {
            button.classList.remove('loading');
            button.disabled = false;
        }
    }
    
    /**
     * Show success message
     */
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    /**
     * Show error message
     */
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
    
    /**
     * Export Neo4j operations report
     */
    async exportNeo4jReport() {
        try {
            const reportData = {
                timestamp: new Date().toISOString(),
                containerStatus: this.containerStatus,
                performanceMetrics: this.performanceMetrics,
                queryHistory: this.queryHistory,
                logSettings: this.logSettings
            };
            
            const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `neo4j_ops_report_${Date.now()}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            this.showSuccess('Operations report exported successfully');
            
        } catch (error) {
            this.logger.error('Failed to export operations report:', error);
            this.showError('Failed to export operations report');
        }
    }
    
    /**
     * Show Neo4j OPS help
     */
    showNeo4jOpsHelp() {
        const helpContent = `
            <div class="modal fade" id="neo4jHelpModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Neo4j Operations Help</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <h6>Container Management</h6>
                            <ul>
                                <li><strong>Start:</strong> Starts the Neo4j Docker container</li>
                                <li><strong>Stop:</strong> Stops the running container</li>
                                <li><strong>Restart:</strong> Restarts the container</li>
                                <li><strong>Remove:</strong> Removes the container (use with caution)</li>
                            </ul>
                            
                            <h6>Performance Monitoring</h6>
                            <ul>
                                <li>Real-time CPU, memory, and disk usage</li>
                                <li>Network I/O monitoring</li>
                                <li>Performance charts and metrics</li>
                            </ul>
                            
                            <h6>Graph Operations</h6>
                            <ul>
                                <li>Import data from JSON, CSV, or XML files</li>
                                <li>Export data in various formats</li>
                                <li>Configure import/export options</li>
                            </ul>
                            
                            <h6>Cypher Queries</h6>
                            <ul>
                                <li>Execute Cypher queries directly</li>
                                <li>Save and load query history</li>
                                <li>View results in formatted tables</li>
                            </ul>
                            
                            <h6>Container Logs</h6>
                            <ul>
                                <li>View real-time container logs</li>
                                <li>Filter by log level</li>
                                <li>Configure log display settings</li>
                            </ul>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal if present
        const existingModal = document.getElementById('neo4jHelpModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Add new modal
        document.body.insertAdjacentHTML('beforeend', helpContent);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('neo4jHelpModal'));
        modal.show();
        
        // Clean up after modal is hidden
        document.getElementById('neo4jHelpModal').addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
    }
    
    /**
     * Cleanup resources
     */
    destroy() {
        // Clear intervals
        if (this.statusInterval) {
            clearInterval(this.statusInterval);
        }
        if (this.performanceInterval) {
            clearInterval(this.performanceInterval);
        }
        if (this.logsInterval) {
            clearInterval(this.logsInterval);
        }
        
        // Remove event listeners
        // (Event listeners will be automatically cleaned up when DOM elements are removed)
        
        this.logger.info('Neo4j OPS Manager destroyed');
    }
}

// Export the class
export { Neo4jOpsManager };

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Check if we're on the Neo4j OPS tab
    if (document.querySelector('.kg-neo4j-ops-tab')) {
        window.neo4jOpsManager = new Neo4jOpsManager();
    }
});

// Global functions for backward compatibility (if needed)
window.startNeo4j = () => window.neo4jOpsManager?.startNeo4j();
window.stopNeo4j = () => window.neo4jOpsManager?.stopNeo4j();
window.restartNeo4j = () => window.neo4jOpsManager?.restartNeo4j();
window.removeNeo4j = () => window.neo4jOpsManager?.removeNeo4j();
window.refreshNeo4jStatus = () => window.neo4jOpsManager?.refreshNeo4jStatus();
window.executeCypherQuery = () => window.neo4jOpsManager?.executeCypherQuery();
window.clearQuery = () => window.neo4jOpsManager?.clearQuery();
window.saveQuery = () => window.neo4jOpsManager?.saveQueryToHistory();
window.loadQueryFromHistory = () => window.neo4jOpsManager?.loadQueryFromHistory();
window.clearResults = () => window.neo4jOpsManager?.clearResults();
window.exportResults = () => window.neo4jOpsManager?.exportResults();
window.refreshLogs = () => window.neo4jOpsManager?.refreshLogs();
window.clearLogs = () => window.neo4jOpsManager?.clearLogs();
window.downloadLogs = () => window.neo4jOpsManager?.downloadLogs();
window.applyLogSettings = () => window.neo4jOpsManager?.applyLogSettings();
window.importGraphData = () => window.neo4jOpsManager?.handleImportSubmit(new Event('submit'));
window.exportGraphData = () => window.neo4jOpsManager?.handleExportSubmit(new Event('submit'));
window.exportNeo4jReport = () => window.neo4jOpsManager?.exportNeo4jReport();
window.showNeo4jOpsHelp = () => window.neo4jOpsManager?.showNeo4jOpsHelp();
