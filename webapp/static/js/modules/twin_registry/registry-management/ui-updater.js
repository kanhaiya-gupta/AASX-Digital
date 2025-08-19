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
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
        
        // Twin Registry specific element IDs
        this.elementIds = {
            tabs: 'twin_registry_tabs',
            tabContent: 'twin_registry_tab_content',
            management: 'twin_registry_management',
            monitoring: 'twin_registry_monitoring',
            performance: 'twin_registry_performance',
            analytics: 'twin_registry_analytics',
            lifecycle: 'twin_registry_lifecycle',
            instances: 'twin_registry_instances',
            configuration: 'twin_registry_configuration'
        };
    }

    /**
     * Initialize UI Updater
     */
    async init() {
        console.log('🔧 Initializing Twin Registry UI Updater...');
        
        try {
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
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
        const refreshBtn = document.getElementById('twin_registry_refreshAllBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshAllData());
        }

        // Search functionality
        const searchInput = document.getElementById('twin_registry_twinSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
        }

        // Filter functionality
        const typeFilter = document.getElementById('twin_registry_typeFilter');
        const statusFilter = document.getElementById('twin_registry_statusFilter');
        const ownerFilter = document.getElementById('twin_registry_ownerFilter');
        const clearFiltersBtn = document.getElementById('twin_registry_clearFilters');

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
        const prevPageBtn = document.getElementById('twin_registry_prevPage');
        const nextPageBtn = document.getElementById('twin_registry_nextPage');

        if (prevPageBtn) {
            prevPageBtn.addEventListener('click', () => this.previousPage());
        }
        if (nextPageBtn) {
            nextPageBtn.addEventListener('click', () => this.nextPage());
        }



        // Individual twin selection



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
            
            // Load data for all tabs to ensure they have data when switched to
            await this.loadAllTabData();
            
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
     * Load data for all tabs
     */
    async loadAllTabData() {
        try {
            console.log('🔄 Loading data for all tabs...');
            
            // Load health monitoring data
            if (window.twinRegistryHealth) {
                await window.twinRegistryHealth.loadHealthData();
            }
            
            // Load performance data
            if (window.twinRegistryPerformance) {
                await window.twinRegistryPerformance.loadPerformanceData();
            }
            
            // Load analytics data
            if (window.twinRegistryAnalytics) {
                await window.twinRegistryAnalytics.loadAnalyticsData();
            }
            
            // Load lifecycle data
            if (window.twinRegistryLifecycle) {
                await window.twinRegistryLifecycle.loadLifecycleData();
            }
            
            // Load instances data
            if (window.twinRegistryInstances) {
                await window.twinRegistryInstances.loadInstancesData();
            }
            
            // Load configuration data
            if (window.twinRegistryConfiguration) {
                await window.twinRegistryConfiguration.loadConfigurationData();
            }
            
            console.log('✅ All tab data loaded');
            
        } catch (error) {
            console.error('❌ Failed to load all tab data:', error);
        }
    }
    
    /**
     * Refresh all data including all tabs
     */
    async refreshAllData() {
        try {
            console.log('🔄 Refreshing all data...');
            this.showLoading();
            
            // Refresh twins data
            await this.loadTwinsData();
            
            // Refresh all tab data
            await this.loadAllTabData();
            
            // Update charts
            if (window.twinRegistryChartUpdater) {
                const statsData = await this.getStatsData();
                const twinsData = await this.getTwinsData();
                window.twinRegistryChartUpdater.updateChartsWithData(twinsData, statsData);
            }
            
            this.hideLoading();
            console.log('✅ All data refreshed successfully');
            
        } catch (error) {
            console.error('❌ Failed to refresh all data:', error);
            this.hideLoading();
            this.showError('Failed to refresh data. Please try again.');
        }
    }

    /**
     * Load and display statistics
     */
    async loadStatistics() {
        try {
            const response = await fetch('/api/twin-registry/twins/statistics', {
            headers: this.getAuthHeaders()
        });
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

            const response = await fetch(`/api/twin-registry/twins?${params}`, {
            headers: this.getAuthHeaders()
        });
            if (response.ok) {
                const data = await response.json();
                console.log('📊 Twins data received:', data);
                
                // Update twins table with the twins array
                this.updateTwinsTable(data);
                
                // Update statistics with the statistics object
                if (data.statistics) {
                    this.updateStatistics(data.statistics);
                } else {
                    // Create statistics from the twins data if not provided
                    const stats = {
                        total_twins: data.pagination?.total_count || data.twins?.length || 0,
                        active_twins: data.twins?.filter(t => t.operational_status === 'running').length || 0,
                        error_twins: data.twins?.filter(t => t.health_status === 'critical').length || 0
                    };
                    this.updateStatistics(stats);
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
        const totalTwinsElement = document.getElementById('twin_registry_totalTwins');
        const activeTwinsElement = document.getElementById('twin_registry_activeTwins');
        const totalDataPointsElement = document.getElementById('twin_registry_totalDataPoints');
        const activeAlertsElement = document.getElementById('twin_registry_activeAlerts');

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
        const analyticsTotalTwins = document.getElementById('twin_registry_analyticsTotalTwins');
        const analyticsHealthyTwins = document.getElementById('twin_registry_analyticsHealthyTwins');
        const analyticsWarningTwins = document.getElementById('twin_registry_analyticsWarningTwins');
        const analyticsCriticalTwins = document.getElementById('twin_registry_analyticsCriticalTwins');

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
        const showingStartElement = document.getElementById('twin_registry_showingStart');
        const showingEndElement = document.getElementById('twin_registry_showingEnd');
        const totalRecordsElement = document.getElementById('twin_registry_totalRecords');

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
        
        const tableBody = document.getElementById('twin_registry_twinTableBody');
        const emptyState = document.getElementById('twin_registry_emptyTwins');
        const loadingState = document.getElementById('twin_registry_loadingTwins');

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
        
        // Get health status and score from the correct API fields
        const healthStatus = twin.health_status || 'unknown';
        const healthScore = twin.overall_health_score || 0;
        
        // Get last sync time
        const lastSync = twin.updated_at ? new Date(twin.updated_at).toLocaleString() : 'Never';
        
        row.innerHTML = `
            <td>
                <code class="text-primary">${twin.twin_id.substring(0, 8)}...</code>
                <button class="btn btn-sm btn-link p-0 ms-1" onclick="copyToClipboard('${twin.twin_id}')" title="Copy ID">
                    <i class="fas fa-copy"></i>
                </button>
            </td>
            <td>
                <div class="fw-bold">${twin.twin_name || 'Unnamed Twin'}</div>
                <small class="text-muted">${twin.workflow_source === 'aasx_file' ? 'AASX File' : 'Structured Data'}</small>
            </td>
            <td>
                <span class="badge bg-secondary">${twin.twin_category || 'Unknown'}</span>
            </td>
            <td>
                <span class="badge bg-secondary">${twin.twin_type || 'Unknown'}</span>
            </td>
            <td>
                <span class="badge bg-${this.getStatusBadgeColor(twin.twin_priority)}">${twin.twin_priority || 'Unknown'}</span>
            </td>
            <td>
                <span class="badge bg-${this.getStatusBadgeColor(twin.integration_status)}">${twin.integration_status || 'Unknown'}</span>
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
                <span class="badge bg-info">${twin.lifecycle_phase || 'Unknown'}</span>
            </td>
            <td>
                <span class="badge bg-${this.getStatusBadgeColor(twin.operational_status)}">${twin.operational_status || 'Unknown'}</span>
            </td>
            <td>
                <span class="badge bg-secondary">${twin.security_level || 'Unknown'}</span>
            </td>
            <td>
                <small class="text-muted">${lastSync}</small>
            </td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    <button class="btn btn-outline-primary" onclick="viewTwin('${twin.twin_id}')" title="View Twin Details">
                        <i class="fas fa-eye"></i>
                        View
                    </button>
                    <button class="btn btn-outline-info" onclick="window.open('/aasx-etl', '_blank')" title="Manage via AASX-ETL">
                        <i class="fas fa-external-link-alt"></i>
                        AASX-ETL
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
        // Use the twin_category field from the API response
        if (twin.twin_category) {
            return twin.twin_category.charAt(0).toUpperCase() + twin.twin_category.slice(1);
        }
        
        // Fallback: try to extract from name
        const name = twin.twin_name || '';
        if (name.includes('Robotic')) return 'Robotic System';
        if (name.includes('Manufacturing')) return 'Manufacturing';
        if (name.includes('Servo')) return 'Servo Motor';
        if (name.includes('Process')) return 'Process';
        if (name.includes('Facility')) return 'Facility';
        if (name.includes('Component')) return 'Component';
        if (name.includes('Energy')) return 'Energy';
        
        return 'Unknown';
    }

    /**
     * Get status badge color
     */
    getStatusBadgeColor(status) {
        if (!status) return 'secondary';
        
        switch (status.toLowerCase()) {
            case 'active':
            case 'running':
            case 'online':
            case 'completed':
            case 'real_time':
                return 'success';
            case 'inactive':
            case 'stopped':
            case 'offline':
                return 'secondary';
            case 'error':
            case 'critical':
                return 'danger';
            case 'maintenance':
            case 'warning':
            case 'degraded':
            case 'paused':
            case 'scheduled':
                return 'warning';
            case 'high':
            case 'normal':
            case 'low':
            case 'standard':
            case 'internal':
            case 'confidential':
            case 'secret':
            case 'top_secret':
                return 'info';
            default:
                return 'secondary';
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
        const prevBtn = document.getElementById('twin_registry_prevPage');
        const nextBtn = document.getElementById('twin_registry_nextPage');
        
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
     * Export twins data
     */
    async exportTwins(format = "json", twinType = null, status = null) {
        try {
            const params = new URLSearchParams();
            if (format) params.append('format', format);
            if (twinType) params.append('twin_type', twinType);
            if (status) params.append('status', status);

            const response = await fetch(`/api/twin-registry/export/twins?${params}`, {
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const result = await response.json();
                return result;
            } else {
                throw new Error(`Export failed: ${response.status}`);
            }
        } catch (error) {
            console.error('Error exporting twins:', error);
            return { success: false, message: error.message };
        }
    }

    /**
     * Export metrics data
     */
    async exportMetrics(format = "json", registryId = null, timeRange = "30d") {
        try {
            const params = new URLSearchParams();
            if (format) params.append('format', format);
            if (registryId) params.append('registry_id', registryId);
            if (timeRange) params.append('time_range', timeRange);

            const response = await fetch(`/api/twin-registry/export/metrics?${params}`, {
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const result = await response.json();
                return result;
            } else {
                throw new Error(`Export failed: ${response.status}`);
            }
        } catch (error) {
            console.error('Error exporting metrics:', error);
            return { success: false, message: error.message };
        }
    }

    /**
     * Export relationships data
     */
    async exportRelationships(format = "json", sourceTwinId = null, targetTwinId = null) {
        try {
            const params = new URLSearchParams();
            if (format) params.append('format', format);
            if (sourceTwinId) params.append('source_twin_id', sourceTwinId);
            if (targetTwinId) params.append('target_twin_id', targetTwinId);

            const response = await fetch(`/api/twin-registry/export/relationships?${params}`, {
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const result = await response.json();
                return result;
            } else {
                throw new Error(`Export failed: ${response.status}`);
            }
        } catch (error) {
            console.error('Error exporting relationships:', error);
            return { success: false, message: error.message };
        }
    }

    /**
     * Export instances data
     */
    async exportInstances(format = "json", twinId = null) {
        try {
            const params = new URLSearchParams();
            if (format) params.append('format', format);
            if (twinId) params.append('twin_id', twinId);

            const response = await fetch(`/api/twin-registry/export/instances?${params}`, {
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const result = await response.json();
                return result;
            } else {
                throw new Error(`Export failed: ${response.status}`);
            }
        } catch (error) {
            console.error('Error exporting instances:', error);
            return { success: false, message: error.message };
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
        const loadingState = document.getElementById('twin_registry_loadingTwins');
        const emptyState = document.getElementById('twin_registry_emptyTwins');
        
        if (loadingState) loadingState.style.display = 'block';
        if (emptyState) emptyState.style.display = 'none';
    }

    /**
     * Hide loading state
     */
    hideLoading() {
        const loadingState = document.getElementById('twin_registry_loadingTwins');
        if (loadingState) loadingState.style.display = 'none';
    }

    /**
     * Show empty state
     */
    showEmptyState() {
        const emptyState = document.getElementById('twin_registry_emptyTwins');
        const loadingState = document.getElementById('twin_registry_loadingTwins');
        
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
     * Search twins by various criteria
     */
    async searchTwins(query = "", twinType = "", status = "", projectId = null, limit = 50) {
        try {
            const params = new URLSearchParams();
            if (query) params.append('query', query);
            if (twinType) params.append('twin_type', twinType);
            if (status) params.append('status', status);
            if (projectId) params.append('project_id', projectId);
            if (limit) params.append('limit', limit.toString());

            const response = await fetch(`/api/twin-registry/twins/search?${params}`, {
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const result = await response.json();
                return result;
            } else {
                throw new Error(`Search failed: ${response.status}`);
            }
        } catch (error) {
            console.error('Error searching twins:', error);
            return { success: false, data: [], total_count: 0 };
        }
    }

    /**
     * Wait for central authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Twin Registry UI Updater: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Twin Registry UI Updater: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Twin Registry UI Updater: Auth system ready event received');
                window.removeEventListener('authSystemReady', handleReady);
                resolve();
            };
            
            window.addEventListener('authSystemReady', handleReady);
            
            // Fallback: check periodically
            const checkInterval = setInterval(() => {
                if (window.authSystemReady && window.authManager) {
                    clearInterval(checkInterval);
                    window.removeEventListener('authSystemReady', handleReady);
                    resolve();
                }
            }, 100);
            
            // Timeout after 10 seconds
            setTimeout(() => {
                clearInterval(checkInterval);
                window.removeEventListener('authSystemReady', handleReady);
                console.warn('⚠️ Twin Registry UI Updater: Timeout waiting for auth system');
                resolve();
            }, 10000);
        });
    }

    /**
     * Update authentication state
     */
    updateAuthState() {
        if (window.authManager) {
            // Check if new auth system is available
        if (typeof window.authManager.getSessionInfo === 'function') {
            const sessionInfo = window.authManager.getSessionInfo();
            this.isAuthenticated = sessionInfo && sessionInfo.isAuthenticated;
        } else if (typeof window.authManager.isAuthenticated === 'function') {
            this.isAuthenticated = window.authManager.isAuthenticated();
        } else {
            this.isAuthenticated = false;
        }
            this.currentUser = null; // User info not needed currently
            this.authToken = window.authManager.getStoredToken();
            console.log('🔐 Twin Registry UI Updater: Auth state updated', {
                isAuthenticated: this.isAuthenticated,
                user: this.currentUser?.username || 'anonymous'
            });
        } else {
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
            console.log('🔐 Twin Registry UI Updater: No auth manager available');
        }
    }

    /**
     * Setup authentication event listeners
     */
    setupAuthListeners() {
        window.addEventListener('authStateChanged', () => {
            this.updateAuthState();
        });

        window.addEventListener('loginSuccess', () => {
            this.updateAuthState();
            // Refresh data when user logs in
            this.refreshAllData();
        });

        window.addEventListener('logout', () => {
            this.updateAuthState();
            // Clear sensitive data when user logs out
            this.clearSensitiveData();
        });
    }

    /**
     * Get authentication headers for API calls
     */
    getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (this.authToken) {
            headers['Authorization'] = `Bearer ${this.authToken}`;
        }
        
        return headers;
    }

    /**
     * Clear sensitive data on logout
     */
    clearSensitiveData() {
        // Clear any cached data that might be user-specific
        this.lastStatsData = null;
        this.lastTwinsData = null;
        console.log('🧹 Twin Registry UI Updater: Sensitive data cleared');
    }

    /**
     * Destroy the UI updater
     */
    destroy() {
        this.isInitialized = false;
        console.log('🧹 Twin Registry UI Updater destroyed');
    }
}

// Global utility functions for Twin Registry
window.twinRegistryCopyToClipboard = function(text) {
    navigator.clipboard.writeText(text).then(() => {
        console.log('Copied to clipboard:', text);
    });
};

window.twinRegistryViewTwin = function(twinId) {
    console.log('View twin:', twinId);
    // Implement twin viewing functionality
};

window.twinRegistryStartTwin = function(twinId) {
    console.log('Start twin:', twinId);
    // Implement twin start functionality
};

window.twinRegistryStopTwin = function(twinId) {
    console.log('Stop twin:', twinId);
    // Implement twin stop functionality
};

 