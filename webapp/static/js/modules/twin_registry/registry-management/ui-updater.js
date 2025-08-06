/**
 * Twin Registry UI Updater Module
 * Handles updating the UI elements with data from the twin registry
 */

export default class TwinRegistryUIUpdater {
    constructor() {
        this.isInitialized = false;
        this.currentPage = 1;
        this.pageSize = 10;
        this.currentFilters = {
            type: '',
            status: '',
            owner: ''
        };
    }

    /**
     * Initialize UI Updater
     */
    async init() {
        console.log('🔧 Initializing Twin Registry UI Updater...');
        
        try {
            // Setup event listeners
            this.setupEventListeners();
            
            // Initial data load
            await this.loadAndDisplayData();
            
            this.isInitialized = true;
            console.log('✅ Twin Registry UI Updater initialized');
            
        } catch (error) {
            console.error('❌ Twin Registry UI Updater initialization failed:', error);
            throw error;
        }
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('refreshAllBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadAndDisplayData());
        }

        // Search functionality
        const searchInput = document.getElementById('twinSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
        }

        // Filter functionality
        const typeFilter = document.getElementById('typeFilter');
        const statusFilter = document.getElementById('statusFilter');
        const ownerFilter = document.getElementById('ownerFilter');
        const clearFiltersBtn = document.getElementById('clearFilters');

        if (typeFilter) {
            typeFilter.addEventListener('change', (e) => this.handleFilterChange('type', e.target.value));
        }
        if (statusFilter) {
            statusFilter.addEventListener('change', (e) => this.handleFilterChange('status', e.target.value));
        }
        if (ownerFilter) {
            ownerFilter.addEventListener('change', (e) => this.handleFilterChange('owner', e.target.value));
        }
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', () => this.clearFilters());
        }

        // Pagination
        const prevPageBtn = document.getElementById('prevPage');
        const nextPageBtn = document.getElementById('nextPage');

        if (prevPageBtn) {
            prevPageBtn.addEventListener('click', () => this.previousPage());
        }
        if (nextPageBtn) {
            nextPageBtn.addEventListener('click', () => this.nextPage());
        }

        // Select all functionality
        const selectAllCheckbox = document.getElementById('selectAll');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => this.toggleSelectAll(e.target.checked));
        }

        // Individual twin selection
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('twin-select')) {
                this.updateBulkActionButtons();
            }
        });

        // Bulk action buttons
        const bulkStartBtn = document.getElementById('bulkStartBtn');
        const bulkStopBtn = document.getElementById('bulkStopBtn');
        const bulkSyncBtn = document.getElementById('bulkSyncBtn');
        const bulkDeleteBtn = document.getElementById('bulkDeleteBtn');

        if (bulkStartBtn) {
            bulkStartBtn.addEventListener('click', () => this.bulkStartTwins());
        }
        if (bulkStopBtn) {
            bulkStopBtn.addEventListener('click', () => this.bulkStopTwins());
        }
        if (bulkSyncBtn) {
            bulkSyncBtn.addEventListener('click', () => this.bulkSyncTwins());
        }
        if (bulkDeleteBtn) {
            bulkDeleteBtn.addEventListener('click', () => this.bulkDeleteTwins());
        }
    }

    /**
     * Load and display data
     */
    async loadAndDisplayData() {
        try {
            console.log('🔄 Loading and displaying data...');
            this.showLoading();
            
            // Load twins data (which includes statistics)
            await this.loadTwinsData();
            
            // Update charts with the loaded data
            if (window.twinRegistryChartUpdater) {
                const statsData = await this.getStatsData();
                const twinsData = await this.getTwinsData();
                window.twinRegistryChartUpdater.updateChartsWithData(twinsData, statsData);
            }
            
            this.hideLoading();
            console.log('✅ Data loaded and displayed successfully');
            
        } catch (error) {
            console.error('❌ Failed to load and display data:', error);
            this.hideLoading();
            this.showError('Failed to load data. Please try again.');
        }
    }

    /**
     * Load and display statistics
     */
    async loadStatistics() {
        try {
            const response = await fetch('/api/twin-registry/twins/statistics');
            if (response.ok) {
                const stats = await response.json();
                this.updateStatistics(stats);
                this.lastStatsData = stats; // Store for chart updates
            }
        } catch (error) {
            console.error('❌ Failed to load statistics:', error);
        }
    }

    /**
     * Load and display twins data
     */
    async loadTwinsData() {
        try {
            const params = new URLSearchParams({
                page: this.currentPage,
                page_size: this.pageSize,
                twin_type: this.currentFilters.type,
                status: this.currentFilters.status,
                project_id: this.currentFilters.owner
            });

            const response = await fetch(`/api/twin-registry/twins?${params}`);
            if (response.ok) {
                const data = await response.json();
                console.log('📊 Twins data received:', data);
                
                // Update twins table with the twins array
                this.updateTwinsTable(data);
                
                // Update statistics with the statistics object
                if (data.statistics) {
                    this.updateStatistics(data.statistics);
                }
                
                this.lastTwinsData = data; // Store for chart updates
            }
        } catch (error) {
            console.error('❌ Failed to load twins data:', error);
        }
    }

    /**
     * Update statistics display
     */
    updateStatistics(stats) {
        console.log('🔄 Updating statistics with data:', stats);
        
        // Update main statistics
        const totalTwinsElement = document.getElementById('totalTwins');
        const activeTwinsElement = document.getElementById('activeTwins');
        const totalDataPointsElement = document.getElementById('totalDataPoints');
        const activeAlertsElement = document.getElementById('activeAlerts');

        if (totalTwinsElement) {
            totalTwinsElement.textContent = stats.total_twins || 0;
        }
        if (activeTwinsElement) {
            activeTwinsElement.textContent = stats.active_twins || 0;
        }
        if (totalDataPointsElement) {
            // Calculate total data points from twins metadata
            const dataPoints = this.calculateTotalDataPoints(stats);
            totalDataPointsElement.textContent = dataPoints;
        }
        if (activeAlertsElement) {
            activeAlertsElement.textContent = stats.error_twins || 0;
        }

        // Update analytics section data
        const analyticsTotalTwins = document.getElementById('analyticsTotalTwins');
        const analyticsHealthyTwins = document.getElementById('analyticsHealthyTwins');
        const analyticsWarningTwins = document.getElementById('analyticsWarningTwins');
        const analyticsCriticalTwins = document.getElementById('analyticsCriticalTwins');

        if (analyticsTotalTwins) {
            analyticsTotalTwins.textContent = stats.total_twins || 0;
        }
        if (analyticsHealthyTwins) {
            analyticsHealthyTwins.textContent = stats.active_twins || 0;
        }
        if (analyticsWarningTwins) {
            analyticsWarningTwins.textContent = 0; // No warning twins in current data
        }
        if (analyticsCriticalTwins) {
            analyticsCriticalTwins.textContent = stats.error_twins || 0;
        }

        // Update pagination info
        const showingStartElement = document.getElementById('showingStart');
        const showingEndElement = document.getElementById('showingEnd');
        const totalRecordsElement = document.getElementById('totalRecords');

        if (showingStartElement && showingEndElement && totalRecordsElement) {
            const start = (this.currentPage - 1) * this.pageSize + 1;
            const end = Math.min(this.currentPage * this.pageSize, stats.total_twins || 0);
            
            showingStartElement.textContent = stats.total_twins > 0 ? start : 0;
            showingEndElement.textContent = end;
            totalRecordsElement.textContent = stats.total_twins || 0;
        }

        // Update pagination buttons
        this.updatePaginationButtons(stats.total_twins || 0);
    }

    /**
     * Update twins table
     */
    updateTwinsTable(data) {
        console.log('🔄 Updating twins table with data:', data);
        
        const tableBody = document.getElementById('twinTableBody');
        const emptyState = document.getElementById('emptyTwins');
        const loadingState = document.getElementById('loadingTwins');

        if (!tableBody) {
            console.error('❌ Table body element not found');
            return;
        }

        // Clear existing content
        tableBody.innerHTML = '';

        if (!data.twins || data.twins.length === 0) {
            console.log('⚠️ No twins data found, showing empty state');
            this.showEmptyState();
            return;
        }

        console.log(`📋 Found ${data.twins.length} twins to display`);

        // Hide empty state
        if (emptyState) emptyState.style.display = 'none';
        if (loadingState) loadingState.style.display = 'none';

        // Populate table
        data.twins.forEach(twin => {
            const row = this.createTwinTableRow(twin);
            tableBody.appendChild(row);
        });
    }

    /**
     * Create a table row for a twin
     */
    createTwinTableRow(twin) {
        const row = document.createElement('tr');
        
        // Extract twin type from name or metadata
        const twinType = this.extractTwinType(twin);
        
        // Get health status
        const healthStatus = twin.health_status || 'unknown';
        const healthScore = twin.health_score || 0;
        
        // Get last sync time
        const lastSync = twin.updated_at ? new Date(twin.updated_at).toLocaleString() : 'Never';
        
        row.innerHTML = `
            <td>
                <input type="checkbox" class="form-check-input twin-select" value="${twin.twin_id}">
            </td>
            <td>
                <code class="text-primary">${twin.twin_id.substring(0, 8)}...</code>
                <button class="btn btn-sm btn-link p-0 ms-1" onclick="copyToClipboard('${twin.twin_id}')" title="Copy ID">
                    <i class="fas fa-copy"></i>
                </button>
            </td>
            <td>
                <div class="fw-bold">${twin.twin_name || 'Unnamed Twin'}</div>
                <small class="text-muted">${twin.file_id ? 'File: ' + twin.file_id.substring(0, 8) + '...' : 'No file'}</small>
            </td>
            <td>
                <span class="badge bg-secondary">${twinType}</span>
            </td>
            <td>
                <span class="badge bg-${this.getStatusBadgeColor(twin.status)}">${twin.status}</span>
            </td>
            <td>
                <div class="d-flex align-items-center">
                    <div class="progress me-2" style="width: 60px; height: 6px;">
                        <div class="progress-bar bg-${this.getHealthBadgeColor(healthScore)}" 
                             style="width: ${healthScore}%"></div>
                    </div>
                    <small class="text-muted">${healthScore}%</small>
                </div>
            </td>
            <td>
                <span class="badge bg-info">System</span>
            </td>
            <td>
                <small class="text-muted">${lastSync}</small>
            </td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    <button class="btn btn-outline-primary" onclick="viewTwin('${twin.twin_id}')" title="View">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-outline-success" onclick="startTwin('${twin.twin_id}')" title="Start">
                        <i class="fas fa-play"></i>
                    </button>
                    <button class="btn btn-outline-warning" onclick="stopTwin('${twin.twin_id}')" title="Stop">
                        <i class="fas fa-stop"></i>
                    </button>
                    <button class="btn btn-outline-danger" onclick="deleteTwin('${twin.twin_id}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;

        return row;
    }

    /**
     * Extract twin type from twin data
     */
    extractTwinType(twin) {
        // Try to extract from name first
        const name = twin.twin_name || '';
        if (name.includes('Robotic')) return 'Robotic System';
        if (name.includes('Manufacturing')) return 'Manufacturing';
        if (name.includes('Servo')) return 'Servo Motor';
        if (name.includes('Process')) return 'Process';
        
        // Try to extract from metadata
        if (twin.metadata && twin.metadata.etl_results) {
            const etlResults = twin.metadata.etl_results;
            if (etlResults.results && etlResults.results.json) {
                const output = etlResults.results.json.output || '';
                if (output.includes('ServoDCMotor')) return 'Servo Motor';
                if (output.includes('Manufacturing')) return 'Manufacturing';
            }
        }
        
        return 'Unknown';
    }

    /**
     * Get status badge color
     */
    getStatusBadgeColor(status) {
        switch (status?.toLowerCase()) {
            case 'active': return 'success';
            case 'inactive': return 'secondary';
            case 'error': return 'danger';
            case 'maintenance': return 'warning';
            default: return 'secondary';
        }
    }

    /**
     * Get health badge color
     */
    getHealthBadgeColor(score) {
        if (score >= 90) return 'success';
        if (score >= 75) return 'info';
        if (score >= 60) return 'warning';
        return 'danger';
    }

    /**
     * Calculate total data points from statistics
     */
    calculateTotalDataPoints(stats) {
        // This is a simplified calculation - in a real implementation,
        // you would sum up data points from all twins
        return stats.total_twins * 10; // Mock calculation
    }

    /**
     * Update pagination buttons
     */
    updatePaginationButtons(totalRecords) {
        const prevBtn = document.getElementById('prevPage');
        const nextBtn = document.getElementById('nextPage');
        
        if (prevBtn) {
            prevBtn.disabled = this.currentPage <= 1;
        }
        
        if (nextBtn) {
            const totalPages = Math.ceil(totalRecords / this.pageSize);
            nextBtn.disabled = this.currentPage >= totalPages;
        }
    }

    /**
     * Handle search
     */
    handleSearch(query) {
        // Implement search functionality
        console.log('Search query:', query);
        // For now, just reload data
        this.loadAndDisplayData();
    }

    /**
     * Handle filter change
     */
    handleFilterChange(filterType, value) {
        this.currentFilters[filterType] = value;
        this.currentPage = 1; // Reset to first page
        this.loadAndDisplayData();
    }

    /**
     * Clear filters
     */
    clearFilters() {
        this.currentFilters = { type: '', status: '', owner: '' };
        this.currentPage = 1;
        
        // Reset filter dropdowns
        const typeFilter = document.getElementById('typeFilter');
        const statusFilter = document.getElementById('statusFilter');
        const ownerFilter = document.getElementById('ownerFilter');
        
        if (typeFilter) typeFilter.value = '';
        if (statusFilter) statusFilter.value = '';
        if (ownerFilter) ownerFilter.value = '';
        
        this.loadAndDisplayData();
    }

    /**
     * Previous page
     */
    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.loadAndDisplayData();
        }
    }

    /**
     * Next page
     */
    nextPage() {
        this.currentPage++;
        this.loadAndDisplayData();
    }

    /**
     * Toggle select all
     */
    toggleSelectAll(checked) {
        const checkboxes = document.querySelectorAll('.twin-select');
        checkboxes.forEach(checkbox => {
            checkbox.checked = checked;
        });
        this.updateBulkActionButtons();
    }

    /**
     * Update bulk action buttons
     */
    updateBulkActionButtons() {
        const selectedCount = document.querySelectorAll('.twin-select:checked').length;
        const bulkButtons = ['bulkStartBtn', 'bulkStopBtn', 'bulkSyncBtn', 'bulkDeleteBtn'];
        
        bulkButtons.forEach(btnId => {
            const btn = document.getElementById(btnId);
            if (btn) {
                btn.disabled = selectedCount === 0;
            }
        });
    }

    /**
     * Bulk start twins
     */
    async bulkStartTwins() {
        const selectedTwins = this.getSelectedTwinIds();
        if (selectedTwins.length === 0) return;

        try {
            const response = await fetch('/api/twin-registry/twins/bulk/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ twin_ids: selectedTwins, user: 'system' })
            });

            if (response.ok) {
                console.log('Bulk start successful');
                await this.loadAndDisplayData();
            }
        } catch (error) {
            console.error('Bulk start failed:', error);
        }
    }

    /**
     * Bulk stop twins
     */
    async bulkStopTwins() {
        const selectedTwins = this.getSelectedTwinIds();
        if (selectedTwins.length === 0) return;

        try {
            const response = await fetch('/api/twin-registry/twins/bulk/stop', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ twin_ids: selectedTwins, user: 'system' })
            });

            if (response.ok) {
                console.log('Bulk stop successful');
                await this.loadAndDisplayData();
            }
        } catch (error) {
            console.error('Bulk stop failed:', error);
        }
    }

    /**
     * Bulk sync twins
     */
    async bulkSyncTwins() {
        const selectedTwins = this.getSelectedTwinIds();
        if (selectedTwins.length === 0) return;

        console.log('Bulk sync twins:', selectedTwins);
        // Implement bulk sync functionality
    }

    /**
     * Bulk delete twins
     */
    async bulkDeleteTwins() {
        const selectedTwins = this.getSelectedTwinIds();
        if (selectedTwins.length === 0) return;

        if (!confirm(`Are you sure you want to delete ${selectedTwins.length} twins?`)) {
            return;
        }

        try {
            // Delete twins one by one (or implement bulk delete endpoint)
            for (const twinId of selectedTwins) {
                const response = await fetch(`/api/twin-registry/twins/${twinId}`, {
                    method: 'DELETE'
                });
                if (!response.ok) {
                    console.error(`Failed to delete twin ${twinId}`);
                }
            }
            
            console.log('Bulk delete completed');
            await this.loadAndDisplayData();
        } catch (error) {
            console.error('Bulk delete failed:', error);
        }
    }

    /**
     * Get selected twin IDs
     */
    getSelectedTwinIds() {
        const checkboxes = document.querySelectorAll('.twin-select:checked');
        return Array.from(checkboxes).map(cb => cb.value);
    }

    /**
     * Show loading state
     */
    showLoading() {
        const loadingState = document.getElementById('loadingTwins');
        const emptyState = document.getElementById('emptyTwins');
        
        if (loadingState) loadingState.style.display = 'block';
        if (emptyState) emptyState.style.display = 'none';
    }

    /**
     * Hide loading state
     */
    hideLoading() {
        const loadingState = document.getElementById('loadingTwins');
        if (loadingState) loadingState.style.display = 'none';
    }

    /**
     * Show empty state
     */
    showEmptyState() {
        const emptyState = document.getElementById('emptyTwins');
        const loadingState = document.getElementById('loadingTwins');
        
        if (emptyState) emptyState.style.display = 'block';
        if (loadingState) loadingState.style.display = 'none';
    }

    /**
     * Show error message
     */
    showError(message) {
        // You can implement a toast notification system here
        console.error('Error:', message);
        alert(message);
    }

    /**
     * Refresh data
     */
    async refreshData() {
        await this.loadAndDisplayData();
    }

    /**
     * Get stored stats data for chart updates
     */
    async getStatsData() {
        return this.lastStatsData || {};
    }

    /**
     * Get stored twins data for chart updates
     */
    async getTwinsData() {
        return this.lastTwinsData || {};
    }

    /**
     * Destroy the UI updater
     */
    destroy() {
        this.isInitialized = false;
        console.log('🧹 Twin Registry UI Updater destroyed');
    }
}

// Global utility functions
window.copyToClipboard = function(text) {
    navigator.clipboard.writeText(text).then(() => {
        console.log('Copied to clipboard:', text);
    });
};

window.viewTwin = function(twinId) {
    console.log('View twin:', twinId);
    // Implement twin viewing functionality
};

window.startTwin = function(twinId) {
    console.log('Start twin:', twinId);
    // Implement twin start functionality
};

window.stopTwin = function(twinId) {
    console.log('Stop twin:', twinId);
    // Implement twin stop functionality
};

window.deleteTwin = function(twinId) {
    if (confirm('Are you sure you want to delete this twin?')) {
        console.log('Delete twin:', twinId);
        // Implement twin deletion functionality
    }
}; 