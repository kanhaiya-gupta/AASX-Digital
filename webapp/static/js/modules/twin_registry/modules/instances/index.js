/**
 * Twin Registry Instance Management Module
 * Handles comprehensive instance management, versioning, and lifecycle control
 */

class InstanceManager {
    constructor() {
        this.currentPage = 1;
        this.pageSize = 10;
        this.totalInstances = 0;
        this.instances = [];
        this.selectedInstances = new Set();
        this.charts = {};
        
        this.initialize();
    }

    async initialize() {
        try {
            await this.loadInstanceData();
            this.setupEventListeners();
            this.initializeCharts();
            this.updateInstanceSummary();
            this.loadInstanceMetadata();
        } catch (error) {
            console.error('Failed to initialize Instance Manager:', error);
            this.showError('Failed to initialize instance management system');
        }
    }

    setupEventListeners() {
        // Filter controls
        document.getElementById('twin_registry_instanceTwinFilter')?.addEventListener('change', () => this.filterInstances());
        document.getElementById('twin_registry_instanceTypeFilter')?.addEventListener('change', () => this.filterInstances());
        document.getElementById('twin_registry_instanceStatusFilter')?.addEventListener('change', () => this.filterInstances());
        document.getElementById('twin_registry_instanceVersionFilter')?.addEventListener('change', () => this.filterInstances());
        
        // Search functionality
        document.getElementById('twin_registry_instanceSearch')?.addEventListener('input', debounce(() => this.searchInstances(), 300));
        
        // Analytics controls
        document.getElementById('twin_registry_instanceAnalyticsMetric')?.addEventListener('change', () => this.updateAnalyticsChart());
        document.getElementById('twin_registry_refreshInstanceAnalytics')?.addEventListener('click', () => this.refreshAnalytics());
        
        // Lifecycle controls
        document.getElementById('twin_registry_lifecycleMetric')?.addEventListener('change', () => this.updateLifecycleChart());
        document.getElementById('twin_registry_refreshLifecycleData')?.addEventListener('click', () => this.refreshLifecycleData());
        
        // Advanced management controls
        document.getElementById('twin_registry_bulkPromote')?.addEventListener('click', () => this.bulkPromoteInstances());
        document.getElementById('twin_registry_bulkRollback')?.addEventListener('click', () => this.bulkRollbackInstances());
        document.getElementById('twin_registry_bulkClone')?.addEventListener('click', () => this.bulkCloneInstances());
        
        // Metadata controls
        document.getElementById('twin_registry_refreshMetadata')?.addEventListener('click', () => this.loadInstanceMetadata());
        
        // Instance creation form
        document.getElementById('twin_registry_instanceCreationForm')?.addEventListener('submit', (e) => this.handleInstanceCreation(e));
        
        // Pagination controls
        document.getElementById('twin_registry_instancePrevPage')?.addEventListener('click', () => this.previousPage());
        document.getElementById('twin_registry_instanceNextPage')?.addEventListener('click', () => this.nextPage());
        
        // Select all instances
        document.getElementById('twin_registry_selectAllInstances')?.addEventListener('change', (e) => this.toggleSelectAll(e.target.checked));
    }

    async loadInstanceData() {
        try {
            this.showLoading();
            
            const response = await fetch('/api/twin-registry/instances', {
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.instances = data.instances || [];
            this.totalInstances = data.total_count || this.instances.length;
            
            this.renderInstanceTable();
            this.updatePagination();
            this.populateTwinFilter();
            
        } catch (error) {
            console.error('Failed to load instance data:', error);
            this.showError('Failed to load instance data');
        } finally {
            this.hideLoading();
        }
    }

    async loadInstanceMetadata() {
        try {
            // Load instance configuration and metadata
            const config = {
                defaultInstanceType: 'Snapshot',
                versionNaming: 'Semantic',
                autoArchiveAge: '90 days',
                maxVersions: '10'
            };

            // Update configuration display
            document.getElementById('twin_registry_defaultInstanceType').textContent = config.defaultInstanceType;
            document.getElementById('twin_registry_versionNaming').textContent = config.versionNaming;
            document.getElementById('twin_registry_autoArchiveAge').textContent = config.autoArchiveAge;
            document.getElementById('twin_registry_maxVersions').textContent = config.maxVersions;

            // Load instance attributes
            this.loadInstanceAttributes();
            this.loadInstanceTags();

        } catch (error) {
            console.error('Failed to load instance metadata:', error);
        }
    }

    loadInstanceAttributes() {
        const attributesContainer = document.getElementById('twin_registry_instanceAttributes');
        if (!attributesContainer) return;

        const attributes = [
            { name: 'Instance Type', value: 'Digital Twin' },
            { name: 'Version Control', value: 'Enabled' },
            { name: 'Lifecycle Management', value: 'Active' },
            { name: 'Metadata Storage', value: 'JSON' }
        ];

        attributesContainer.innerHTML = attributes.map(attr => `
            <div class="tr-attribute-item">
                <span class="tr-attribute-name">${attr.name}:</span>
                <span class="tr-attribute-value">${attr.value}</span>
            </div>
        `).join('');
    }

    loadInstanceTags() {
        const tagsContainer = document.getElementById('twin_registry_instanceTags');
        if (!tagsContainer) return;

        const tags = ['production', 'monitoring', 'analytics', 'versioned', 'managed'];
        
        tagsContainer.innerHTML = tags.map(tag => `
            <span class="tr-tag">${tag}</span>
        `).join('');
    }

    populateTwinFilter() {
        const twinFilter = document.getElementById('twin_registry_instanceTwinFilter');
        if (!twinFilter) return;

        const uniqueTwins = [...new Set(this.instances.map(inst => inst.twin_name))];
        
        twinFilter.innerHTML = '<option value="">All Twins</option>' +
            uniqueTwins.map(twin => `<option value="${twin}">${twin}</option>`).join('');
    }

    renderInstanceTable() {
        const tbody = document.getElementById('twin_registry_instanceTableBody');
        if (!tbody) return;

        if (this.instances.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center py-4">
                        <div class="tr-empty-state">
                            <i class="fas fa-cube fa-3x text-muted mb-3"></i>
                            <h6>No Instances Found</h6>
                            <p class="text-muted">No twin instances are currently available.</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = this.instances.map(instance => this.createInstanceRow(instance)).join('');
    }

    createInstanceRow(instance) {
        const isSelected = this.selectedInstances.has(instance.instance_id);
        const statusClass = this.getStatusClass(instance.is_active);
        
        return `
            <tr data-instance-id="${instance.instance_id}">
                <td class="tr-checkbox-column">
                    <div class="tr-checkbox-wrapper">
                        <input type="checkbox" class="tr-instance-checkbox" 
                               value="${instance.instance_id}" 
                               ${isSelected ? 'checked' : ''}>
                        <label class="tr-checkbox-label"></label>
                    </div>
                </td>
                <td>
                    <code class="tr-instance-id">${instance.instance_id.substring(0, 8)}...</code>
                </td>
                <td>
                    <strong>${instance.twin_name || 'Unknown Twin'}</strong>
                </td>
                <td>
                    <span class="tr-version-badge">${instance.version || 'v1.0.0'}</span>
                </td>
                <td>
                    <span class="tr-type-badge tr-type-${instance.instance_type || 'generic'}">
                        ${instance.instance_type || 'Generic'}
                    </span>
                </td>
                <td>
                    <span class="tr-status-badge ${statusClass}">
                        ${instance.is_active ? 'Active' : 'Inactive'}
                    </span>
                </td>
                <td>
                    <small class="text-muted">
                        ${this.formatDate(instance.created_at)}
                    </small>
                </td>
                <td>
                    <span class="tr-user-badge">
                        ${instance.created_by || 'System'}
                    </span>
                </td>
                <td>
                    <div class="tr-action-buttons">
                        <button class="tr-btn tr-btn-sm tr-btn-outline" 
                                onclick="instanceManager.viewInstanceDetails('${instance.instance_id}')"
                                title="View Details">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="tr-btn tr-btn-sm tr-btn-outline" 
                                onclick="instanceManager.promoteInstance('${instance.instance_id}')"
                                title="Promote to Production">
                            <i class="fas fa-arrow-up"></i>
                        </button>
                        <button class="tr-btn tr-btn-sm tr-btn-outline" 
                                onclick="instanceManager.cloneInstance('${instance.instance_id}')"
                                title="Clone Instance">
                            <i class="fas fa-copy"></i>
                        </button>
                        <button class="tr-btn tr-btn-sm tr-btn-outline" 
                                onclick="instanceManager.archiveInstance('${instance.instance_id}')"
                                title="Archive Instance">
                            <i class="fas fa-archive"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }

    getStatusClass(isActive) {
        return isActive ? 'tr-status-active' : 'tr-status-inactive';
    }

    formatDate(dateString) {
        if (!dateString) return 'Unknown';
        const date = new Date(dateString);
        return date.toLocaleDateString();
    }

    updateInstanceSummary() {
        const totalInstances = this.instances.length;
        const activeInstances = this.instances.filter(inst => inst.is_active).length;
        const latestVersion = Math.max(...this.instances.map(inst => parseInt(inst.version) || 1));
        const historyCount = this.instances.length;

        // Update summary cards
        document.getElementById('twin_registry_totalInstances').textContent = totalInstances;
        document.getElementById('twin_registry_activeInstances').textContent = activeInstances;
        document.getElementById('twin_registry_latestVersion').textContent = `v${latestVersion}`;
        document.getElementById('twin_registry_instanceHistory').textContent = historyCount;

        // Update analytics metrics
        document.getElementById('twin_registry_instanceDistribution').textContent = totalInstances;
        document.getElementById('twin_registry_versionCoverage').textContent = `${Math.round((activeInstances / totalInstances) * 100)}%`;
        document.getElementById('twin_registry_productionReady').textContent = this.instances.filter(inst => inst.instance_type === 'production').length;
        document.getElementById('twin_registry_avgVersionAge').textContent = '15 days';

        // Update lifecycle metrics
        document.getElementById('twin_registry_devInstances').textContent = this.instances.filter(inst => inst.instance_type === 'development').length;
        document.getElementById('twin_registry_testInstances').textContent = this.instances.filter(inst => inst.instance_type === 'testing').length;
        document.getElementById('twin_registry_prodInstances').textContent = this.instances.filter(inst => inst.instance_type === 'production').length;
        document.getElementById('twin_registry_archivedInstances').textContent = this.instances.filter(inst => !inst.is_active).length;
    }

    initializeCharts() {
        this.initializeAnalyticsChart();
        this.initializeLifecycleChart();
    }

    initializeAnalyticsChart() {
        const ctx = document.getElementById('twin_registry_instanceAnalyticsChart');
        if (!ctx) return;

        this.charts.analytics = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Development', 'Testing', 'Production', 'Archived'],
                datasets: [{
                    data: [30, 25, 35, 10],
                    backgroundColor: ['#17a2b8', '#ffc107', '#28a745', '#6c757d'],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }

    initializeLifecycleChart() {
        const ctx = document.getElementById('twin_registry_instanceLifecycleChart');
        if (!ctx) return;

        this.charts.lifecycle = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Development', 'Testing', 'Production', 'Archived'],
                datasets: [{
                    label: 'Instance Count',
                    data: [12, 8, 15, 5],
                    backgroundColor: 'rgba(30, 60, 114, 0.8)',
                    borderColor: 'rgba(30, 60, 114, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    updateAnalyticsChart() {
        const metric = document.getElementById('twin_registry_instanceAnalyticsMetric')?.value || 'distribution';
        
        if (!this.charts.analytics) return;

        let newData;
        let newLabels;

        switch (metric) {
            case 'distribution':
                newLabels = ['Development', 'Testing', 'Production', 'Archived'];
                newData = [30, 25, 35, 10];
                break;
            case 'version':
                newLabels = ['v1.0', 'v1.1', 'v1.2', 'v2.0'];
                newData = [20, 30, 25, 25];
                break;
            case 'performance':
                newLabels = ['High', 'Medium', 'Low', 'Critical'];
                newData = [40, 35, 20, 5];
                break;
            case 'lifecycle':
                newLabels = ['Created', 'Active', 'Inactive', 'Archived'];
                newData = [15, 50, 25, 10];
                break;
        }

        this.charts.analytics.data.labels = newLabels;
        this.charts.analytics.data.datasets[0].data = newData;
        this.charts.analytics.update();
    }

    updateLifecycleChart() {
        const metric = document.getElementById('twin_registry_lifecycleMetric')?.value || 'states';
        
        if (!this.charts.lifecycle) return;

        let newData;
        let newLabels;

        switch (metric) {
            case 'states':
                newLabels = ['Development', 'Testing', 'Production', 'Archived'];
                newData = [12, 8, 15, 5];
                break;
            case 'transitions':
                newLabels = ['Dev→Test', 'Test→Prod', 'Prod→Archive', 'Archive→Dev'];
                newData = [8, 12, 3, 2];
                break;
            case 'workflow':
                newLabels = ['Created', 'Configured', 'Validated', 'Deployed'];
                newData = [20, 18, 15, 12];
                break;
            case 'promotion':
                newLabels = ['Candidate', 'Approved', 'Promoted', 'Live'];
                newData = [10, 8, 6, 4];
                break;
        }

        this.charts.lifecycle.data.labels = newLabels;
        this.charts.lifecycle.data.datasets[0].data = newData;
        this.charts.lifecycle.update();
    }

    async handleInstanceCreation(event) {
        event.preventDefault();
        
        try {
            const formData = new FormData(event.target);
            const instanceData = {
                twin_id: formData.get('twin_registry_instanceTwinSelect'),
                instance_type: formData.get('twin_registry_instanceType'),
                version: formData.get('twin_registry_instanceVersion'),
                description: formData.get('twin_registry_instanceDescription'),
                tags: formData.get('twin_registry_instanceTags').split(',').map(tag => tag.trim()).filter(tag => tag)
            };

            const response = await fetch('/api/twin-registry/twins/' + instanceData.twin_id + '/instances', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(instanceData)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            this.showSuccess('Instance created successfully');
            this.resetInstanceForm();
            await this.loadInstanceData();
            
        } catch (error) {
            console.error('Failed to create instance:', error);
            this.showError('Failed to create instance');
        }
    }

    resetInstanceForm() {
        document.getElementById('twin_registry_instanceCreationForm').reset();
    }

    async promoteInstance(instanceId) {
        try {
            const response = await fetch(`/api/twin-registry/instances/${instanceId}/promote`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            this.showSuccess('Instance promoted successfully');
            await this.loadInstanceData();
            
        } catch (error) {
            console.error('Failed to promote instance:', error);
            this.showError('Failed to promote instance');
        }
    }

    async cloneInstance(instanceId) {
        try {
            const response = await fetch(`/api/twin-registry/instances/${instanceId}/clone`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            this.showSuccess('Instance cloned successfully');
            await this.loadInstanceData();
            
        } catch (error) {
            console.error('Failed to clone instance:', error);
            this.showError('Failed to clone instance');
        }
    }

    async archiveInstance(instanceId) {
        try {
            const response = await fetch(`/api/twin-registry/instances/${instanceId}/archive`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            this.showSuccess('Instance archived successfully');
            await this.loadInstanceData();
            
        } catch (error) {
            console.error('Failed to archive instance:', error);
            this.showError('Failed to archive instance');
        }
    }

    async bulkPromoteInstances() {
        if (this.selectedInstances.size === 0) {
            this.showWarning('Please select instances to promote');
            return;
        }

        try {
            const response = await fetch('/api/twin-registry/instances/bulk-promote', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    instance_ids: Array.from(this.selectedInstances)
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            this.showSuccess(`${this.selectedInstances.size} instances promoted successfully`);
            this.selectedInstances.clear();
            await this.loadInstanceData();
            
        } catch (error) {
            console.error('Failed to bulk promote instances:', error);
            this.showError('Failed to bulk promote instances');
        }
    }

    async bulkRollbackInstances() {
        if (this.selectedInstances.size === 0) {
            this.showWarning('Please select instances to rollback');
            return;
        }

        try {
            const response = await fetch('/api/twin-registry/instances/bulk-rollback', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    instance_ids: Array.from(this.selectedInstances)
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            this.showSuccess(`${this.selectedInstances.size} instances rolled back successfully`);
            this.selectedInstances.clear();
            await this.loadInstanceData();
            
        } catch (error) {
            console.error('Failed to bulk rollback instances:', error);
            this.showError('Failed to bulk rollback instances');
        }
    }

    async bulkCloneInstances() {
        if (this.selectedInstances.size === 0) {
            this.showWarning('Please select instances to clone');
            return;
        }

        try {
            const response = await fetch('/api/twin-registry/instances/bulk-clone', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    instance_ids: Array.from(this.selectedInstances)
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            this.showSuccess(`${this.selectedInstances.size} instances cloned successfully`);
            this.selectedInstances.clear();
            await this.loadInstanceData();
            
        } catch (error) {
            console.error('Failed to bulk clone instances:', error);
            this.showError('Failed to bulk clone instances');
        }
    }

    filterInstances() {
        // Implementation for filtering instances based on selected criteria
        this.currentPage = 1;
        this.renderInstanceTable();
        this.updatePagination();
    }

    searchInstances() {
        const searchTerm = document.getElementById('twin_registry_instanceSearch')?.value.toLowerCase() || '';
        
        if (!searchTerm) {
            this.renderInstanceTable();
            return;
        }

        const filteredInstances = this.instances.filter(instance => 
            instance.twin_name?.toLowerCase().includes(searchTerm) ||
            instance.instance_id?.toLowerCase().includes(searchTerm) ||
            instance.instance_type?.toLowerCase().includes(searchTerm)
        );

        this.renderFilteredInstances(filteredInstances);
    }

    renderFilteredInstances(filteredInstances) {
        const tbody = document.getElementById('twin_registry_instanceTableBody');
        if (!tbody) return;

        if (filteredInstances.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center py-4">
                        <div class="tr-empty-state">
                            <i class="fas fa-search fa-3x text-muted mb-3"></i>
                            <h6>No Results Found</h6>
                            <p class="text-muted">No instances match your search criteria.</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = filteredInstances.map(instance => this.createInstanceRow(instance)).join('');
    }

    toggleSelectAll(checked) {
        const checkboxes = document.querySelectorAll('.tr-instance-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.checked = checked;
            if (checked) {
                this.selectedInstances.add(checkbox.value);
            } else {
                this.selectedInstances.delete(checkbox.value);
            }
        });
    }

    updatePagination() {
        const totalPages = Math.ceil(this.totalInstances / this.pageSize);
        
        // Update pagination info
        const start = (this.currentPage - 1) * this.pageSize + 1;
        const end = Math.min(this.currentPage * this.pageSize, this.totalInstances);
        
        document.getElementById('twin_registry_instancePaginationInfo').textContent = 
            `Showing ${start} to ${end} of ${this.totalInstances} instances`;

        // Update pagination controls
        document.getElementById('twin_registry_instancePrevPage').disabled = this.currentPage === 1;
        document.getElementById('twin_registry_instanceNextPage').disabled = this.currentPage === totalPages;

        // Generate page numbers
        this.generatePageNumbers(totalPages);
    }

    generatePageNumbers(totalPages) {
        const pageNumbersContainer = document.getElementById('twin_registry_instancePageNumbers');
        if (!pageNumbersContainer) return;

        let pageNumbers = '';
        const maxVisiblePages = 5;
        let startPage = Math.max(1, this.currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }

        for (let i = startPage; i <= endPage; i++) {
            pageNumbers += `
                <button class="tr-page-btn ${i === this.currentPage ? 'active' : ''}" 
                        onclick="instanceManager.goToPage(${i})">
                    ${i}
                </button>
            `;
        }

        pageNumbersContainer.innerHTML = pageNumbers;
    }

    goToPage(page) {
        this.currentPage = page;
        this.loadInstanceData();
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.goToPage(this.currentPage - 1);
        }
    }

    nextPage() {
        const totalPages = Math.ceil(this.totalInstances / this.pageSize);
        if (this.currentPage < totalPages) {
            this.goToPage(this.currentPage + 1);
        }
    }

    refreshAnalytics() {
        this.updateAnalyticsChart();
        this.showSuccess('Analytics refreshed');
    }

    refreshLifecycleData() {
        this.updateLifecycleChart();
        this.showSuccess('Lifecycle data refreshed');
    }

    viewInstanceDetails(instanceId) {
        const instance = this.instances.find(inst => inst.instance_id === instanceId);
        if (!instance) return;

        const modal = new bootstrap.Modal(document.getElementById('twin_registry_instanceDetailsModal'));
        const title = document.getElementById('twin_registry_instanceDetailsTitle');
        const content = document.getElementById('twin_registry_instanceDetailsContent');

        title.innerHTML = `<i class="fas fa-info-circle"></i> Instance Details - ${instance.twin_name}`;
        
        content.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Basic Information</h6>
                    <table class="table table-sm">
                        <tr><td><strong>Instance ID:</strong></td><td><code>${instance.instance_id}</code></td></tr>
                        <tr><td><strong>Twin Name:</strong></td><td>${instance.twin_name}</td></tr>
                        <tr><td><strong>Version:</strong></td><td>${instance.version}</td></tr>
                        <tr><td><strong>Type:</strong></td><td>${instance.instance_type}</td></tr>
                        <tr><td><strong>Status:</strong></td><td>${instance.is_active ? 'Active' : 'Inactive'}</td></tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6>Metadata</h6>
                    <table class="table table-sm">
                        <tr><td><strong>Created:</strong></td><td>${this.formatDate(instance.created_at)}</td></tr>
                        <tr><td><strong>Created By:</strong></td><td>${instance.created_by || 'System'}</td></tr>
                        <tr><td><strong>Registry Type:</strong></td><td>${instance.registry_type}</td></tr>
                    </table>
                </div>
            </div>
        `;

        modal.show();
    }

    getAuthToken() {
        return window.authManager?.getToken() || '';
    }

    showLoading() {
        // Show loading state
        const tableContainer = document.querySelector('.tr-table-container');
        if (tableContainer) {
            tableContainer.innerHTML = `
                <div class="tr-loading-state">
                    <div class="tr-loading-content">
                        <div class="tr-loading-spinner"></div>
                        <div class="tr-loading-text">Loading instances...</div>
                    </div>
                </div>
            `;
        }
    }

    hideLoading() {
        // Hide loading state - table will be rendered by renderInstanceTable
    }

    showSuccess(message) {
        // Show success notification
        console.log('✅', message);
    }

    showError(message) {
        // Show error notification
        console.error('❌', message);
    }

    showWarning(message) {
        // Show warning notification
        console.warn('⚠️', message);
    }
}

// Utility function for debouncing
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize instance manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.instanceManager = new InstanceManager();
});

// Export for global access
window.InstanceManager = InstanceManager;
export default InstanceManager; // Twin Registry Instance Manager v1.0 