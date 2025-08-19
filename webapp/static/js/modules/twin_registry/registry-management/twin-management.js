/**
 * Twin Registry Twin Management Module
 * Handles twin management functionality with central authentication integration
 */

export default class TwinRegistryTwinManagement {
    constructor() {
        this.isInitialized = false;
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
        this.twinsData = [];
        this.filteredTwins = [];
        this.currentPage = 1;
        this.pageSize = 10;
        this.totalPages = 1;
        this.totalTwins = 0;
        
        // Twin management specific element IDs
        this.elementIds = {
            twinsTable: 'twin_registry_twinsTable',
            twinsTableBody: 'twin_registry_twinsTableBody',
            searchInput: 'twin_registry_twinSearch',
            typeFilter: 'twin_registry_typeFilter',
            statusFilter: 'twin_registry_statusFilter',
            ownerFilter: 'twin_registry_ownerFilter',
            clearFiltersBtn: 'twin_registry_clearFilters',
            addTwinBtn: 'twin_registry_addTwinBtn',

            paginationContainer: 'twin_registry_pagination',
            prevPageBtn: 'twin_registry_prevPage',
            nextPageBtn: 'twin_registry_nextPage',
            pageInfo: 'twin_registry_pageInfo',
            refreshBtn: 'twin_registry_refreshBtn',
            exportBtn: 'twin_registry_exportBtn',
            importBtn: 'twin_registry_importBtn'
        };
        
        this.currentFilters = {
            type: '',
            status: '',
            owner: ''
        };
        

        this.refreshInterval = null;
    }

    /**
     * Initialize Twin Management
     */
    async init() {
        console.log('🔧 Initializing Twin Registry Twin Management...');
        
        try {
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Load initial twins data
            await this.loadTwinsData();
            
            // Setup auto-refresh
            this.setupAutoRefresh();
            
            this.isInitialized = true;
            console.log('✅ Twin Registry Twin Management initialized');
            
        } catch (error) {
            console.error('❌ Twin Registry Twin Management initialization failed:', error);
            throw error;
        }
    }

    /**
     * Wait for central authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Twin Registry Twin Management: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Twin Registry Twin Management: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Twin Registry Twin Management: Auth system ready event received');
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
                console.warn('⚠️ Twin Registry Twin Management: Timeout waiting for auth system');
                resolve();
            }, 10000);
        });
    }

    /**
     * Update authentication state from central auth manager
     */
    updateAuthState() {
        if (!window.authManager) {
            console.log('⚠️ Twin Registry Twin Management: No auth manager available');
            return;
        }
        
        try {
            // Check if new auth system is available
            if (typeof window.authManager.getSessionInfo === 'function') {
                const sessionInfo = window.authManager.getSessionInfo();
                console.log('🔐 Twin Registry Twin Management: Auth state update (new system):', sessionInfo);
                
                if (sessionInfo && sessionInfo.isAuthenticated) {
                    this.isAuthenticated = true;
                    this.currentUser = {
                        user_id: sessionInfo.user_id,
                        username: sessionInfo.username,
                        role: sessionInfo.role,
                        organization_id: sessionInfo.organization_id
                    };
                    this.authToken = window.authManager.getStoredToken();
                    console.log('🔐 Twin Registry Twin Management: User authenticated:', this.currentUser.username);
                } else {
                    this.isAuthenticated = false;
                    this.currentUser = null;
                    this.authToken = null;
                    console.log('🔐 Twin Registry Twin Management: User not authenticated');
                }
            } else if (typeof window.authManager.isAuthenticated === 'function') {
                // Fallback to old auth system
                const isAuthenticated = window.authManager.isAuthenticated();
                console.log('🔐 Twin Registry Twin Management: Auth state update (old system):', isAuthenticated);
                
                if (isAuthenticated) {
                    this.isAuthenticated = true;
                    this.currentUser = {
                        user_id: 'unknown',
                        username: 'authenticated_user',
                        role: 'user',
                        organization_id: 'unknown'
                    };
                    this.authToken = window.authManager.getStoredToken();
                    console.log('🔐 Twin Registry Twin Management: User authenticated (legacy)');
                } else {
                    this.isAuthenticated = false;
                    this.currentUser = null;
                    this.authToken = null;
                    console.log('🔐 Twin Registry Twin Management: User not authenticated (legacy)');
                }
            } else {
                console.log('⚠️ Twin Registry Twin Management: Unknown auth manager API');
                this.isAuthenticated = false;
                this.currentUser = null;
                this.authToken = null;
            }
        } catch (error) {
            console.warn('⚠️ Twin Registry Twin Management: Error updating auth state:', error);
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
        }
    }

    /**
     * Setup authentication listeners
     */
    setupAuthListeners() {
        // Listen for auth state changes
        window.addEventListener('authStateChanged', () => {
            console.log('🔄 Twin Registry Twin Management: Auth state changed, updating...');
            this.updateAuthState();
            this.handleAuthStateChange();
        });
        
        // Listen for login success
        window.addEventListener('loginSuccess', async () => {
            console.log('🔐 Twin Registry Twin Management: Login success detected');
            this.updateAuthState();
            await this.handleLoginSuccess();
        });
        
        // Listen for logout
        window.addEventListener('logout', () => {
            console.log('🔐 Twin Registry Twin Management: Logout detected');
            this.updateAuthState();
            this.handleLogout();
        });
    }

    /**
     * Handle login success
     */
    async handleLoginSuccess() {
        try {
            await this.loadTwinsData();
            console.log('✅ Twin Registry Twin Management: User data refreshed after login');
        } catch (error) {
            console.error('❌ Twin Registry Twin Management: Failed to refresh user data after login:', error);
        }
    }

    /**
     * Handle logout
     */
    handleLogout() {
        this.twinsData = [];
        this.filteredTwins = [];

        this.currentUser = null;
        this.isAuthenticated = false;
        this.updateTwinsTable();
        console.log('🔐 Twin Registry Twin Management: User data cleared after logout');
    }

    /**
     * Handle auth state change
     */
    handleAuthStateChange() {
        if (this.isAuthenticated && this.currentUser) {
            this.showAuthenticatedFeatures();
        } else {
            this.showDemoMode();
        }
    }

    /**
     * Show authenticated user features
     */
    showAuthenticatedFeatures() {
        console.log('🔐 Twin Registry Twin Management: Showing authenticated user features');
        this.enableTwinManagement();
    }

    /**
     * Show demo mode
     */
    showDemoMode() {
        console.log('🔐 Twin Registry Twin Management: Showing demo mode');
        this.disableTwinManagement();
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById(this.elementIds.searchInput);
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
        }

        // Filter functionality
        const typeFilter = document.getElementById(this.elementIds.typeFilter);
        const statusFilter = document.getElementById(this.elementIds.statusFilter);
        const ownerFilter = document.getElementById(this.elementIds.ownerFilter);
        const clearFiltersBtn = document.getElementById(this.elementIds.clearFiltersBtn);

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
        const prevPageBtn = document.getElementById(this.elementIds.prevPageBtn);
        const nextPageBtn = document.getElementById(this.elementIds.nextPageBtn);

        if (prevPageBtn) {
            prevPageBtn.addEventListener('click', () => this.previousPage());
        }
        if (nextPageBtn) {
            nextPageBtn.addEventListener('click', () => this.nextPage());
        }





        // Action buttons
        const addTwinBtn = document.getElementById(this.elementIds.addTwinBtn);
        const refreshBtn = document.getElementById(this.elementIds.refreshBtn);
        const exportBtn = document.getElementById(this.elementIds.exportBtn);
        const importBtn = document.getElementById(this.elementIds.importBtn);

        if (addTwinBtn) {
            addTwinBtn.addEventListener('click', () => this.showAddTwinModal());
        }
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadTwinsData());
        }
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportTwinsData());
        }
        if (importBtn) {
            importBtn.addEventListener('click', () => this.importTwinsData());
        }

        // Listen for custom refresh events
        window.addEventListener('twinRegistryRefresh', () => {
            this.loadTwinsData();
        });
    }

    /**
     * Load twins data
     */
    async loadTwinsData() {
        try {
            console.log('📊 Loading twins data...');
            this.showLoading();
            
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
                
                this.twinsData = data.twins || [];
                this.totalTwins = data.pagination?.total_count || 0;
                this.totalPages = data.pagination?.total_pages || 1;
                
                // Apply filters
                this.applyFilters();
                
                // Update UI
                this.updateTwinsTable();
                this.updatePagination();
                
                console.log(`✅ Loaded ${this.twinsData.length} twins`);
            } else {
                throw new Error(`Failed to load twins: ${response.status}`);
            }
            
            this.hideLoading();
            
        } catch (error) {
            console.error('❌ Failed to load twins data:', error);
            this.hideLoading();
            this.showError('Failed to load twins data. Please try again.');
        }
    }

    /**
     * Apply filters to twins data
     */
    applyFilters() {
        this.filteredTwins = this.twinsData.filter(twin => {
            if (this.currentFilters.type && twin.twin_type !== this.currentFilters.type) {
                return false;
            }
            if (this.currentFilters.status && twin.integration_status !== this.currentFilters.status) {
                return false;
            }
            if (this.currentFilters.owner && twin.owner_team !== this.currentFilters.owner) {
                return false;
            }
            return true;
        });
    }

    /**
     * Handle search
     */
    handleSearch(query) {
        if (!query.trim()) {
            this.applyFilters();
        } else {
            const searchLower = query.toLowerCase();
            this.filteredTwins = this.twinsData.filter(twin => {
                return twin.twin_name.toLowerCase().includes(searchLower) ||
                       twin.twin_id.toLowerCase().includes(searchLower) ||
                       twin.registry_name.toLowerCase().includes(searchLower);
            });
        }
        
        this.currentPage = 1;
        this.updateTwinsTable();
        this.updatePagination();
    }

    /**
     * Handle filter change
     */
    handleFilterChange(filterType, value) {
        this.currentFilters[filterType] = value;
        this.currentPage = 1;
        this.applyFilters();
        this.updateTwinsTable();
        this.updatePagination();
    }

    /**
     * Clear filters
     */
    clearFilters() {
        this.currentFilters = {
            type: '',
            status: '',
            owner: ''
        };
        
        // Reset filter dropdowns
        const typeFilter = document.getElementById(this.elementIds.typeFilter);
        const statusFilter = document.getElementById(this.elementIds.statusFilter);
        const ownerFilter = document.getElementById(this.elementIds.ownerFilter);
        
        if (typeFilter) typeFilter.value = '';
        if (statusFilter) statusFilter.value = '';
        if (ownerFilter) ownerFilter.value = '';
        
        this.currentPage = 1;
        this.applyFilters();
        this.updateTwinsTable();
        this.updatePagination();
    }

    /**
     * Update twins table
     */
    updateTwinsTable() {
        const tableBody = document.getElementById(this.elementIds.twinsTableBody);
        if (!tableBody) return;

        if (this.filteredTwins.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="11" class="text-center text-muted">
                        <i class="fas fa-inbox fa-2x mb-2"></i>
                        <p>No twins found</p>
                    </td>
                </tr>
            `;
            return;
        }

        const startIndex = (this.currentPage - 1) * this.pageSize;
        const endIndex = Math.min(startIndex + this.pageSize, this.filteredTwins.length);
        const pageTwins = this.filteredTwins.slice(startIndex, endIndex);

        const tableRows = pageTwins.map(twin => this.createTwinTableRow(twin));
        tableBody.innerHTML = tableRows.join('');
    }

    /**
     * Create twin table row
     */
    createTwinTableRow(twin) {

        const statusClass = this.getStatusClass(twin.integration_status);
        const healthClass = this.getHealthClass(twin.overall_health_score);
        
        return `
            <tr data-twin-id="${twin.twin_id}">
                <td>
                    <div class="d-flex flex-column">
                        <div class="fw-bold text-primary">${twin.twin_name}</div>
                        <div class="text-muted small">ID: ${twin.twin_id}</div>
                    </div>
                </td>
                <td>
                    <span class="badge bg-secondary">${twin.twin_category || 'N/A'}</span>
                </td>
                <td>
                    <span class="badge bg-info">${twin.twin_type || 'Unknown'}</span>
                </td>
                <td>
                    <span class="badge bg-warning">${twin.twin_priority || 'N/A'}</span>
                </td>
                <td>
                    <span class="badge ${statusClass}">${twin.integration_status || 'Unknown'}</span>
                </td>
                <td>
                    <span class="badge ${healthClass}">${twin.overall_health_score || 0}%</span>
                </td>
                <td>
                    <span class="badge bg-primary">${twin.lifecycle_phase || 'Unknown'}</span>
                </td>
                <td>
                    <span class="badge bg-secondary">${twin.operational_status || 'Unknown'}</span>
                </td>
                <td>
                    <span class="badge bg-dark">${twin.security_level || 'N/A'}</span>
                </td>
                <td>
                    <div class="text-muted small">
                        ${twin.last_sync || 'Never'}
                    </div>
                </td>
                <td>
                    <div class="d-flex flex-column gap-1">
                        <button class="btn btn-outline-primary btn-sm" 
                                onclick="this.viewTwinDetails('${twin.twin_id}')"
                                title="View Details">
                            <i class="fas fa-eye"></i>
                            View
                        </button>
                        <button class="btn btn-outline-info btn-sm" 
                                onclick="window.open('/aasx-etl', '_blank')"
                                title="Manage via AASX-ETL">
                            <i class="fas fa-external-link-alt"></i>
                            AASX-ETL
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }

    /**
     * Get status class for badge
     */
    getStatusClass(status) {
        switch (status) {
            case 'active': return 'bg-success';
            case 'inactive': return 'bg-secondary';
            case 'error': return 'bg-danger';
            case 'warning': return 'bg-warning';
            default: return 'bg-secondary';
        }
    }

    /**
     * Get health class for badge
     */
    getHealthClass(healthScore) {
        if (healthScore >= 90) return 'bg-success';
        if (healthScore >= 70) return 'bg-warning';
        return 'bg-danger';
    }

    /**
     * Update pagination
     */
    updatePagination() {
        const paginationContainer = document.getElementById(this.elementIds.paginationContainer);
        if (!paginationContainer) return;

        const startRecord = (this.currentPage - 1) * this.pageSize + 1;
        const endRecord = Math.min(this.currentPage * this.pageSize, this.filteredTwins.length);

        paginationContainer.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div class="page-info">
                    Showing ${startRecord} to ${endRecord} of ${this.filteredTwins.length} twins
                </div>
                <div class="pagination-controls">
                    <button class="btn btn-outline-primary btn-sm" 
                            id="${this.elementIds.prevPageBtn}"
                            ${this.currentPage === 1 ? 'disabled' : ''}>
                        <i class="fas fa-chevron-left"></i> Previous
                    </button>
                    <span class="mx-2">Page ${this.currentPage} of ${this.totalPages}</span>
                    <button class="btn btn-outline-primary btn-sm" 
                            id="${this.elementIds.nextPageBtn}"
                            ${this.currentPage === this.totalPages ? 'disabled' : ''}>
                        Next <i class="fas fa-chevron-right"></i>
                    </button>
                </div>
            </div>
        `;

        // Re-attach event listeners
        this.setupPaginationListeners();
    }

    /**
     * Setup pagination listeners
     */
    setupPaginationListeners() {
        const prevPageBtn = document.getElementById(this.elementIds.prevPageBtn);
        const nextPageBtn = document.getElementById(this.elementIds.nextPageBtn);

        if (prevPageBtn) {
            prevPageBtn.addEventListener('click', () => this.previousPage());
        }
        if (nextPageBtn) {
            nextPageBtn.addEventListener('click', () => this.nextPage());
        }
    }

    /**
     * Previous page
     */
    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.updateTwinsTable();
            this.updatePagination();
        }
    }

    /**
     * Next page
     */
    nextPage() {
        if (this.currentPage < this.totalPages) {
            this.currentPage++;
            this.updateTwinsTable();
            this.updatePagination();
        }
    }

    /**
     * Show add twin modal
     */
    showAddTwinModal() {
        // Implementation for showing add twin modal
        console.log('➕ Showing add twin modal');
        // You can implement modal functionality here
    }

    /**
     * View twin details
     */
    viewTwinDetails(twinId) {
        // Implementation for viewing twin details
        console.log(`👁️ Viewing details for twin ${twinId}`);
        // You can implement modal or navigation functionality here
    }

    /**
     * Edit twin
     */
    editTwin(twinId) {
        // Implementation for editing twin
        console.log(`✏️ Editing twin ${twinId}`);
        // You can implement modal or navigation functionality here
    }

    /**
     * Clone twin
     */
    cloneTwin(twinId) {
        // Implementation for cloning twin
        console.log(`📋 Cloning twin ${twinId}`);
        // You can implement modal or navigation functionality here
    }

    /**
     * Export twin
     */
    exportTwin(twinId) {
        // Implementation for exporting twin
        console.log(`📤 Exporting twin ${twinId}`);
        // You can implement export functionality here
    }

    /**
     * Export twins data
     */
    exportTwinsData() {
        try {
            const dataStr = JSON.stringify(this.filteredTwins, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(dataBlob);
            
            const link = document.createElement('a');
            link.href = url;
            link.download = 'twin-registry-twins.json';
            link.click();
            
            URL.revokeObjectURL(url);
            console.log('📤 Twins data exported successfully');
        } catch (error) {
            console.error('❌ Failed to export twins data:', error);
            this.showError('Failed to export twins data');
        }
    }

    /**
     * Import twins data
     */
    importTwinsData() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.onchange = async (event) => {
            const file = event.target.files[0];
            if (!file) return;

            try {
                const text = await file.text();
                const twins = JSON.parse(text);
                
                // Validate imported twins
                if (Array.isArray(twins)) {
                    this.showSuccess(`Successfully imported ${twins.length} twins`);
                    console.log('📥 Twins data imported successfully');
                    
                    // Refresh data
                    await this.loadTwinsData();
                } else {
                    throw new Error('Invalid twins data format');
                }
            } catch (error) {
                console.error('❌ Failed to import twins data:', error);
                this.showError('Failed to import twins data. Invalid file format.');
            }
        };
        
        input.click();
    }

    /**
     * Enable twin management
     */
    enableTwinManagement() {
        const buttons = document.querySelectorAll('.twin-management-btn');
        buttons.forEach(button => {
            button.disabled = false;
        });
    }

    /**
     * Disable twin management
     */
    disableTwinManagement() {
        const buttons = document.querySelectorAll('.twin-management-btn');
        buttons.forEach(button => {
            button.disabled = true;
        });
    }

    /**
     * Setup auto-refresh
     */
    setupAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }

        this.refreshInterval = setInterval(async () => {
            if (this.isAuthenticated) {
                await this.loadTwinsData();
            }
        }, 30000); // Refresh every 30 seconds
    }

    /**
     * Show loading state
     */
    showLoading() {
        const tableBody = document.getElementById(this.elementIds.twinsTableBody);
        if (tableBody) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="11" class="text-center">
                        <i class="fas fa-spinner fa-spin fa-2x mb-2"></i>
                        <p>Loading twins...</p>
                    </td>
                </tr>
            `;
        }
    }

    /**
     * Hide loading state
     */
    hideLoading() {
        // Loading state will be replaced by actual data
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        console.log('✅ Twin Management Success:', message);
        // You can implement a toast notification system here
        alert(message);
    }

    /**
     * Show error message
     */
    showError(message) {
        console.error('❌ Twin Management Error:', message);
        // You can implement a toast notification system here
        alert(message);
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
     * Cleanup resources
     */
    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        this.isInitialized = false;
        console.log('🧹 Twin Registry Twin Management destroyed');
    }
}
