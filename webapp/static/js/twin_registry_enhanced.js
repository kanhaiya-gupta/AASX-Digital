/**
 * Enhanced Twin Registry Management JavaScript
 * Phase 2.2.2: Complete Twin Registry Management
 * Handles twin lifecycle, operations, configuration, and advanced monitoring
 */

class TwinRegistryEnhanced {
    constructor() {
        this.selectedTwins = new Set();
        this.twinConfigurations = {};
        this.twinEvents = {};
        this.twinHealth = {};
        this.currentTwinId = null;
        
        // UI elements
        this.enhancedPanel = null;
        this.enhancedTable = null;
        
        // Initialize
        this.init();
    }
    
    init() {
        console.log('🔧 Initializing Enhanced Twin Registry Management...');
        
        // Create enhanced management UI
        this.createEnhancedUI();
        
        // Load initial data
        this.loadTwinSummary();
        
        // Bind event handlers
        this.bindEnhancedEvents();
        
        console.log('✅ Enhanced Twin Registry Management initialized');
    }
    
    createEnhancedUI() {
        // Create enhanced management panel
        this.createEnhancedPanel();
    }
    
    createEnhancedPanel() {
        const container = document.querySelector('.container-fluid');
        if (!container) {
            console.error('❌ Container not found');
            return;
        }
        
        // Check if panel already exists
        if (document.getElementById('enhancedPanel')) {
            console.log('✅ Enhanced panel already exists');
            return;
        }
        
        const panel = document.createElement('div');
        panel.className = 'row mb-4';
        panel.id = 'enhancedPanel';
        panel.innerHTML = `
            <div class="col-12">
                <div class="card shadow">
                    <div class="card-header py-3 d-flex justify-content-between align-items-center">
                        <h6 class="m-0 font-weight-bold text-primary">
                            <i class="fas fa-cogs"></i>
                            Enhanced Twin Management
                        </h6>
                        <div class="btn-group" role="group">
                            <button class="btn btn-sm btn-outline-primary" id="refreshEnhanced">
                                <i class="fas fa-sync-alt"></i> Refresh
                            </button>
                            <button class="btn btn-sm btn-success" id="createTwinBtn">
                                <i class="fas fa-plus"></i> Create Twin
                            </button>
                            <button class="btn btn-sm btn-warning" id="bulkStartBtn" disabled>
                                <i class="fas fa-play"></i> Start Selected
                            </button>
                            <button class="btn btn-sm btn-danger" id="bulkStopBtn" disabled>
                                <i class="fas fa-stop"></i> Stop Selected
                            </button>
                            <button class="btn btn-sm btn-outline-secondary" id="exportDataBtn">
                                <i class="fas fa-download"></i> Export
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="row mb-3">
                            <div class="col-md-4">
                                <input type="text" class="form-control" id="twinSearch" placeholder="Search twins...">
                            </div>
                            <div class="col-md-2">
                                <select class="form-select" id="typeFilter">
                                    <option value="">All Types</option>
                                    <option value="manufacturing">Manufacturing</option>
                                    <option value="energy">Energy</option>
                                    <option value="component">Component</option>
                                    <option value="facility">Facility</option>
                                    <option value="process">Process</option>
                                    <option value="generic">Generic</option>
                                </select>
                            </div>
                            <div class="col-md-2">
                                <select class="form-select" id="statusFilter">
                                    <option value="">All Status</option>
                                    <option value="active">Active</option>
                                    <option value="inactive">Inactive</option>
                                    <option value="error">Error</option>
                                    <option value="maintenance">Maintenance</option>
                                </select>
                            </div>
                            <div class="col-md-2">
                                <select class="form-select" id="ownerFilter">
                                    <option value="">All Owners</option>
                                    <option value="system">System</option>
                                    <option value="admin">Admin</option>
                                    <option value="user">User</option>
                                </select>
                            </div>
                            <div class="col-md-2">
                                <button class="btn btn-outline-secondary w-100" id="clearFilters">
                                    <i class="fas fa-times"></i> Clear
                                </button>
                            </div>
                        </div>
                        <div class="table-responsive">
                            <table class="table table-hover" id="enhancedTwinTable">
                                <thead>
                                    <tr>
                                        <th>
                                            <input type="checkbox" id="selectAll">
                                        </th>
                                        <th data-sort="twin_name">Twin Name <i class="fas fa-sort"></i></th>
                                        <th data-sort="twin_type">Type <i class="fas fa-sort"></i></th>
                                        <th data-sort="status">Status <i class="fas fa-sort"></i></th>
                                        <th data-sort="health">Health <i class="fas fa-sort"></i></th>
                                        <th data-sort="owner">Owner <i class="fas fa-sort"></i></th>
                                        <th data-sort="last_sync">Last Sync <i class="fas fa-sort"></i></th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <!-- Enhanced twin rows will be inserted here -->
                                </tbody>
                            </table>
                        </div>
                        <div class="d-flex justify-content-between align-items-center mt-3">
                            <div class="text-muted">
                                Showing <span id="showingCount">0</span> of <span id="totalCount">0</span> twins
                            </div>
                            <div class="btn-group" role="group">
                                <button class="btn btn-sm btn-outline-secondary" id="prevPage" disabled>
                                    <i class="fas fa-chevron-left"></i> Previous
                                </button>
                                <span class="btn btn-sm btn-outline-secondary disabled" id="pageInfo">Page 1</span>
                                <button class="btn btn-sm btn-outline-secondary" id="nextPage" disabled>
                                    Next <i class="fas fa-chevron-right"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Find the existing twin registry management section and insert after it
        const twinRegistrySection = container.querySelector('#twinRegistryTable');
        if (twinRegistrySection) {
            const twinRegistryRow = twinRegistrySection.closest('.row');
            if (twinRegistryRow && twinRegistryRow.parentNode) {
                // Insert after the twin registry management section
                twinRegistryRow.parentNode.insertBefore(panel, twinRegistryRow.nextSibling);
                console.log('✅ Enhanced panel inserted after twin registry management section');
            } else {
                container.appendChild(panel);
                console.log('✅ Enhanced panel appended to container (fallback)');
            }
        } else {
            // If no twin registry table found, append to the end
            container.appendChild(panel);
            console.log('✅ Enhanced panel appended to container (no twin registry table found)');
        }
        
        this.enhancedPanel = panel;
        this.enhancedTable = panel.querySelector('#enhancedTwinTable');
        
        console.log('✅ Enhanced panel created successfully');
    }
    
    bindEnhancedEvents() {
        // Create twin button
        document.addEventListener('click', (e) => {
            if (e.target.id === 'createTwinBtn' || e.target.closest('#createTwinBtn')) {
                this.showCreateTwinModal();
            }
        });
        
        // Refresh button
        document.addEventListener('click', (e) => {
            if (e.target.id === 'refreshEnhanced' || e.target.closest('#refreshEnhanced')) {
                this.loadTwinSummary();
            }
        });
        
        // Search and filters
        document.addEventListener('input', (e) => {
            if (e.target.id === 'twinSearch') {
                this.filterTwins();
            }
        });
        
        document.addEventListener('change', (e) => {
            if (['typeFilter', 'statusFilter', 'ownerFilter'].includes(e.target.id)) {
                this.filterTwins();
            }
        });
        
        // Clear filters
        document.addEventListener('click', (e) => {
            if (e.target.id === 'clearFilters' || e.target.closest('#clearFilters')) {
                this.clearFilters();
            }
        });
        
        // Bulk operations
        document.addEventListener('click', (e) => {
            if (e.target.id === 'bulkStartBtn' || e.target.closest('#bulkStartBtn')) {
                this.bulkStartTwins();
            }
            if (e.target.id === 'bulkStopBtn' || e.target.closest('#bulkStopBtn')) {
                this.bulkStopTwins();
            }
        });
        
        // Export data
        document.addEventListener('click', (e) => {
            if (e.target.id === 'exportDataBtn' || e.target.closest('#exportDataBtn')) {
                this.exportTwinData();
            }
        });
        
        // Table sorting
        document.addEventListener('click', (e) => {
            if (e.target.closest('[data-sort]')) {
                const sortField = e.target.closest('[data-sort]').dataset.sort;
                this.sortTable(sortField);
            }
        });
        
        // Pagination
        document.addEventListener('click', (e) => {
            if (e.target.id === 'prevPage' || e.target.closest('#prevPage')) {
                this.previousPage();
            }
            if (e.target.id === 'nextPage' || e.target.closest('#nextPage')) {
                this.nextPage();
            }
        });
        
        // Modal events
        this.bindModalEvents();
    }
    
    bindModalEvents() {
        // Create twin modal events
        document.addEventListener('click', (e) => {
            if (e.target.id === 'generateTwinId') {
                this.generateTwinId();
            }
            if (e.target.id === 'saveCreateTwin') {
                this.createTwin();
            }
        });
        
        // Edit twin modal events
        document.addEventListener('click', (e) => {
            if (e.target.id === 'saveEditTwin') {
                this.updateTwin();
            }
        });
        
        // Delete twin modal events
        document.addEventListener('click', (e) => {
            if (e.target.id === 'confirmDeleteTwin') {
                this.deleteTwin();
            }
        });
        
        // Twin details modal events
        document.addEventListener('click', (e) => {
            if (e.target.id === 'editTwinFromDetails') {
                this.editTwinFromDetails();
            }
        });
    }
    
    async loadTwinSummary() {
        console.log('📊 Loading enhanced twin summary...');
        try {
            const response = await fetch('/twin-registry/api/twins/summary');
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.updateEnhancedTable(data.data);
                    this.updateTwinSelectors(data.data);
                } else {
                    console.error('❌ Error loading twin summary:', data.error);
                    this.showNotification('Error loading twin data', 'error');
                }
            } else {
                console.error('❌ HTTP Error:', response.status);
                this.showNotification('Failed to load twin data', 'error');
            }
        } catch (error) {
            console.error('❌ Error loading twin summary:', error);
            this.showNotification('Network error loading twin data', 'error');
        }
    }
    
    updateEnhancedTable(twins) {
        const tbody = this.enhancedTable.querySelector('tbody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        if (twins.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center text-muted py-4">
                        <i class="fas fa-inbox fa-2x mb-2"></i>
                        <br>No twins found
                    </td>
                </tr>
            `;
            return;
        }
        
        twins.forEach(twin => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <input type="checkbox" class="twin-checkbox" value="${twin.twin_id}">
                </td>
                <td>
                    <strong>${twin.twin_name}</strong>
                    <br><small class="text-muted">${twin.twin_id}</small>
                </td>
                <td>
                    <span class="badge bg-primary">${twin.twin_type}</span>
                    <br><small class="text-muted">v${twin.version}</small>
                </td>
                <td>
                    <span class="badge ${this.getStatusColor(twin.status)}">${twin.status}</span>
                </td>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="progress flex-grow-1 me-2" style="height: 6px;">
                            <div class="progress-bar ${this.getHealthColor(twin.health)}" 
                                 style="width: ${twin.health}%"></div>
                        </div>
                        <small>${twin.health}%</small>
                    </div>
                </td>
                <td>${twin.owner}</td>
                <td>${this.formatTime(twin.last_sync)}</td>
                <td>
                    <div class="btn-group" role="group">
                        <button class="btn btn-sm btn-primary view-twin" data-id="${twin.twin_id}" title="View Details">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-secondary edit-twin" data-id="${twin.twin_id}" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-info sync-twin" data-id="${twin.twin_id}" title="Sync">
                            <i class="fas fa-sync"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger delete-twin" data-id="${twin.twin_id}" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
        
        // Bind row event handlers
        this.bindRowEvents();
        
        // Update counts
        document.getElementById('showingCount').textContent = twins.length;
        document.getElementById('totalCount').textContent = twins.length;
    }
    
    bindRowEvents() {
        // View twin details
        document.querySelectorAll('.view-twin').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const twinId = e.target.closest('.view-twin').dataset.id;
                this.viewTwinDetails(twinId);
            });
        });
        
        // Edit twin
        document.querySelectorAll('.edit-twin').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const twinId = e.target.closest('.edit-twin').dataset.id;
                this.editTwin(twinId);
            });
        });
        
        // Sync twin
        document.querySelectorAll('.sync-twin').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const twinId = e.target.closest('.sync-twin').dataset.id;
                this.syncTwin(twinId);
            });
        });
        
        // Delete twin
        document.querySelectorAll('.delete-twin').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const twinId = e.target.closest('.delete-twin').dataset.id;
                this.showDeleteConfirmation(twinId);
            });
        });
        
        // Checkbox selection
        document.querySelectorAll('.twin-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const twinId = e.target.value;
                const selected = e.target.checked;
                this.toggleTwinSelection(twinId, selected);
            });
        });
        
        // Select all checkbox
        const selectAll = document.getElementById('selectAll');
        if (selectAll) {
            selectAll.addEventListener('change', (e) => {
                this.toggleSelectAll(e.target.checked);
            });
        }
    }
    
    // Modal Functions
    showCreateTwinModal() {
        const modal = new bootstrap.Modal(document.getElementById('createTwinModal'));
        modal.show();
    }
    
    generateTwinId() {
        const timestamp = Date.now().toString(36);
        const random = Math.random().toString(36).substr(2, 5);
        const twinId = `DT-${timestamp}-${random}`.toUpperCase();
        document.getElementById('createTwinId').value = twinId;
    }
    
    async createTwin() {
        const form = document.getElementById('createTwinForm');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        const twinData = {
            twin_id: document.getElementById('createTwinId').value,
            twin_name: document.getElementById('createTwinName').value,
            twin_type: document.getElementById('createTwinType').value,
            description: document.getElementById('createTwinDescription').value,
            version: document.getElementById('createTwinVersion').value,
            owner: document.getElementById('createTwinOwner').value,
            tags: document.getElementById('createTwinTags').value.split(',').map(t => t.trim()).filter(t => t),
            metadata: {
                auto_start: document.getElementById('createAutoStart').checked,
                monitoring_enabled: document.getElementById('createMonitoringEnabled').checked,
                alerting_enabled: document.getElementById('createAlertingEnabled').checked,
                data_retention: document.getElementById('createDataRetention').checked,
                location: document.getElementById('createLocation').value,
                manufacturer: document.getElementById('createManufacturer').value,
                model: document.getElementById('createModel').value,
                serial_number: document.getElementById('createSerialNumber').value
            }
        };
        
        try {
            const response = await fetch('/twin-registry/api/twins', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(twinData)
            });
            
            if (response.ok) {
                const result = await response.json();
                this.showNotification('Twin created successfully', 'success');
                bootstrap.Modal.getInstance(document.getElementById('createTwinModal')).hide();
                this.loadTwinSummary();
            } else {
                const error = await response.json();
                this.showNotification(`Error creating twin: ${error.detail}`, 'error');
            }
        } catch (error) {
            console.error('Error creating twin:', error);
            this.showNotification('Network error creating twin', 'error');
        }
    }
    
    async editTwin(twinId) {
        this.currentTwinId = twinId;
        
        try {
            const response = await fetch(`/twin-registry/api/twins/${twinId}`);
            if (response.ok) {
                const twin = await response.json();
                this.populateEditForm(twin);
                
                const modal = new bootstrap.Modal(document.getElementById('editTwinModal'));
                modal.show();
            } else {
                this.showNotification('Error loading twin data', 'error');
            }
        } catch (error) {
            console.error('Error loading twin:', error);
            this.showNotification('Network error loading twin', 'error');
        }
    }
    
    populateEditForm(twin) {
        document.getElementById('editTwinId').value = twin.twin_id;
        document.getElementById('editTwinName').value = twin.twin_name;
        document.getElementById('editTwinType').value = twin.twin_type;
        document.getElementById('editTwinVersion').value = twin.version || '1.0.0';
        document.getElementById('editTwinOwner').value = twin.owner || 'system';
        document.getElementById('editTwinDescription').value = twin.description || '';
        document.getElementById('editTwinTags').value = (twin.tags || []).join(', ');
        
        // Settings
        const settings = twin.settings || {};
        document.getElementById('editAutoStart').checked = settings.auto_start !== false;
        document.getElementById('editMonitoringEnabled').checked = settings.monitoring_enabled !== false;
        document.getElementById('editAlertingEnabled').checked = settings.alerting_enabled !== false;
        document.getElementById('editDataRetention').checked = settings.data_retention !== false;
    }
    
    async updateTwin() {
        const form = document.getElementById('editTwinForm');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        const updateData = {
            twin_name: document.getElementById('editTwinName').value,
            twin_type: document.getElementById('editTwinType').value,
            description: document.getElementById('editTwinDescription').value,
            version: document.getElementById('editTwinVersion').value,
            owner: document.getElementById('editTwinOwner').value,
            tags: document.getElementById('editTwinTags').value.split(',').map(t => t.trim()).filter(t => t),
            settings: {
                auto_start: document.getElementById('editAutoStart').checked,
                monitoring_enabled: document.getElementById('editMonitoringEnabled').checked,
                alerting_enabled: document.getElementById('editAlertingEnabled').checked,
                data_retention: document.getElementById('editDataRetention').checked
            }
        };
        
        try {
            const response = await fetch(`/twin-registry/api/twins/${this.currentTwinId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updateData)
            });
            
            if (response.ok) {
                this.showNotification('Twin updated successfully', 'success');
                bootstrap.Modal.getInstance(document.getElementById('editTwinModal')).hide();
                this.loadTwinSummary();
            } else {
                const error = await response.json();
                this.showNotification(`Error updating twin: ${error.detail}`, 'error');
            }
        } catch (error) {
            console.error('Error updating twin:', error);
            this.showNotification('Network error updating twin', 'error');
        }
    }
    
    showDeleteConfirmation(twinId) {
        this.currentTwinId = twinId;
        
        // Get twin name for confirmation
        const row = document.querySelector(`[data-id="${twinId}"]`).closest('tr');
        const twinName = row.querySelector('td:nth-child(2) strong').textContent;
        
        document.getElementById('deleteTwinName').textContent = twinName;
        
        const modal = new bootstrap.Modal(document.getElementById('deleteTwinModal'));
        modal.show();
    }
    
    async deleteTwin() {
        try {
            const response = await fetch(`/twin-registry/api/twins/${this.currentTwinId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.showNotification('Twin deleted successfully', 'success');
                bootstrap.Modal.getInstance(document.getElementById('deleteTwinModal')).hide();
                this.loadTwinSummary();
            } else {
                const error = await response.json();
                this.showNotification(`Error deleting twin: ${error.detail}`, 'error');
            }
        } catch (error) {
            console.error('Error deleting twin:', error);
            this.showNotification('Network error deleting twin', 'error');
        }
    }
    
    async viewTwinDetails(twinId) {
        this.currentTwinId = twinId;
        
        try {
            // Load basic info
            const response = await fetch(`/twin-registry/api/twins/${twinId}`);
            if (response.ok) {
                const twin = await response.json();
                this.populateTwinDetails(twin);
                
                // Load health data
                this.loadTwinHealthForDetails(twinId);
                
                // Load recent events
                this.loadTwinEventsForDetails(twinId);
                
                const modal = new bootstrap.Modal(document.getElementById('twinDetailsModal'));
                modal.show();
            } else {
                this.showNotification('Error loading twin details', 'error');
            }
        } catch (error) {
            console.error('Error loading twin details:', error);
            this.showNotification('Network error loading twin details', 'error');
        }
    }
    
    populateTwinDetails(twin) {
        // Basic Information
        document.getElementById('twinBasicInfo').innerHTML = `
            <table class="table table-sm">
                <tr><td><strong>Twin ID:</strong></td><td>${twin.twin_id}</td></tr>
                <tr><td><strong>Name:</strong></td><td>${twin.twin_name}</td></tr>
                <tr><td><strong>Type:</strong></td><td><span class="badge bg-primary">${twin.twin_type}</span></td></tr>
                <tr><td><strong>Version:</strong></td><td>${twin.version || '1.0.0'}</td></tr>
                <tr><td><strong>Owner:</strong></td><td>${twin.owner || 'system'}</td></tr>
                <tr><td><strong>Description:</strong></td><td>${twin.description || 'No description'}</td></tr>
                <tr><td><strong>Tags:</strong></td><td>${(twin.tags || []).map(t => `<span class="badge bg-secondary">${t}</span>`).join(' ') || 'No tags'}</td></tr>
            </table>
        `;
        
        // Configuration
        const settings = twin.settings || {};
        document.getElementById('twinConfiguration').innerHTML = `
            <table class="table table-sm">
                <tr><td><strong>Auto Start:</strong></td><td>${settings.auto_start ? 'Yes' : 'No'}</td></tr>
                <tr><td><strong>Monitoring:</strong></td><td>${settings.monitoring_enabled ? 'Enabled' : 'Disabled'}</td></tr>
                <tr><td><strong>Alerting:</strong></td><td>${settings.alerting_enabled ? 'Enabled' : 'Disabled'}</td></tr>
                <tr><td><strong>Data Retention:</strong></td><td>${settings.data_retention ? 'Enabled' : 'Disabled'}</td></tr>
                <tr><td><strong>Location:</strong></td><td>${settings.location || 'Not specified'}</td></tr>
                <tr><td><strong>Manufacturer:</strong></td><td>${settings.manufacturer || 'Not specified'}</td></tr>
                <tr><td><strong>Model:</strong></td><td>${settings.model || 'Not specified'}</td></tr>
                <tr><td><strong>Serial Number:</strong></td><td>${settings.serial_number || 'Not specified'}</td></tr>
            </table>
        `;
    }
    
    async loadTwinHealthForDetails(twinId) {
        try {
            const response = await fetch(`/twin-registry/api/twins/${twinId}/health`);
            if (response.ok) {
                const health = await response.json();
                document.getElementById('twinHealthStatus').innerHTML = `
                    <div class="row text-center">
                        <div class="col-6">
                            <div class="border rounded p-3">
                                <h4 class="text-primary">${health.overall_health}%</h4>
                                <small class="text-muted">Overall Health</small>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="border rounded p-3">
                                <h4 class="text-success">${health.performance_health}%</h4>
                                <small class="text-muted">Performance</small>
                            </div>
                        </div>
                    </div>
                    <div class="row text-center mt-2">
                        <div class="col-6">
                            <div class="border rounded p-3">
                                <h4 class="text-info">${health.connectivity_health}%</h4>
                                <small class="text-muted">Connectivity</small>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="border rounded p-3">
                                <h4 class="text-warning">${health.data_health}%</h4>
                                <small class="text-muted">Data Quality</small>
                            </div>
                        </div>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error loading health data:', error);
        }
    }
    
    async loadTwinEventsForDetails(twinId) {
        try {
            const response = await fetch(`/twin-registry/api/twins/${twinId}/events?limit=5`);
            if (response.ok) {
                const events = await response.json();
                const eventsHtml = events.length > 0 ? 
                    events.map(event => `
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <div>
                                <strong class="text-${this.getSeverityColor(event.severity)}">${event.event_type}</strong>
                                <br><small class="text-muted">${event.event_message}</small>
                            </div>
                            <small class="text-muted">${this.formatTime(event.timestamp)}</small>
                        </div>
                    `).join('') : 
                    '<p class="text-muted">No recent events</p>';
                
                document.getElementById('twinRecentEvents').innerHTML = eventsHtml;
            }
        } catch (error) {
            console.error('Error loading events:', error);
        }
    }
    
    editTwinFromDetails() {
        bootstrap.Modal.getInstance(document.getElementById('twinDetailsModal')).hide();
        this.editTwin(this.currentTwinId);
    }
    
    // Utility Functions
    toggleTwinSelection(twinId, selected) {
        if (selected) {
            this.selectedTwins.add(twinId);
        } else {
            this.selectedTwins.delete(twinId);
        }
        this.updateBulkButtons();
    }
    
    toggleSelectAll(selectAll) {
        const checkboxes = document.querySelectorAll('.twin-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.checked = selectAll;
            this.toggleTwinSelection(checkbox.value, selectAll);
        });
    }
    
    updateBulkButtons() {
        const hasSelection = this.selectedTwins.size > 0;
        document.getElementById('bulkStartBtn').disabled = !hasSelection;
        document.getElementById('bulkStopBtn').disabled = !hasSelection;
    }
    
    filterTwins() {
        // Implementation for filtering twins
        console.log('Filtering twins...');
    }
    
    clearFilters() {
        document.getElementById('twinSearch').value = '';
        document.getElementById('typeFilter').value = '';
        document.getElementById('statusFilter').value = '';
        document.getElementById('ownerFilter').value = '';
        this.filterTwins();
    }
    
    sortTable(field) {
        // Implementation for sorting table
        console.log('Sorting by:', field);
    }
    
    previousPage() {
        // Implementation for pagination
        console.log('Previous page');
    }
    
    nextPage() {
        // Implementation for pagination
        console.log('Next page');
    }
    
    async bulkStartTwins() {
        const twinIds = Array.from(this.selectedTwins);
        try {
            const response = await fetch('/twin-registry/api/twins/bulk/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ twin_ids: twinIds })
            });
            
            if (response.ok) {
                this.showNotification(`Started ${twinIds.length} twins`, 'success');
                this.loadTwinSummary();
            } else {
                this.showNotification('Error starting twins', 'error');
            }
        } catch (error) {
            console.error('Error starting twins:', error);
            this.showNotification('Network error starting twins', 'error');
        }
    }
    
    async bulkStopTwins() {
        const twinIds = Array.from(this.selectedTwins);
        try {
            const response = await fetch('/twin-registry/api/twins/bulk/stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ twin_ids: twinIds })
            });
            
            if (response.ok) {
                this.showNotification(`Stopped ${twinIds.length} twins`, 'success');
                this.loadTwinSummary();
            } else {
                this.showNotification('Error stopping twins', 'error');
            }
        } catch (error) {
            console.error('Error stopping twins:', error);
            this.showNotification('Network error stopping twins', 'error');
        }
    }
    
    async syncTwin(twinId) {
        try {
            const response = await fetch(`/twin-registry/api/twins/${twinId}/sync`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    twin_id: twinId,
                    sync_type: 'manual',
                    force: false
                })
            });
            
            if (response.ok) {
                this.showNotification('Twin sync initiated', 'success');
                this.loadTwinSummary();
            } else {
                this.showNotification('Error syncing twin', 'error');
            }
        } catch (error) {
            console.error('Error syncing twin:', error);
            this.showNotification('Network error syncing twin', 'error');
        }
    }
    
    exportTwinData() {
        // Implementation for exporting twin data
        console.log('Exporting twin data...');
        this.showNotification('Export feature coming soon', 'info');
    }
    
    updateTwinSelectors(twins) {
        // Update any twin selectors in the UI
        console.log('Updated twin selectors with', twins.length, 'twins');
    }
    
    getStatusColor(status) {
        const colors = {
            'active': 'bg-success',
            'inactive': 'bg-secondary',
            'error': 'bg-danger',
            'maintenance': 'bg-warning',
            'starting': 'bg-info',
            'stopping': 'bg-warning'
        };
        return colors[status] || 'bg-secondary';
    }
    
    getHealthColor(health) {
        if (health >= 80) return 'bg-success';
        if (health >= 60) return 'bg-warning';
        return 'bg-danger';
    }
    
    getSeverityColor(severity) {
        const colors = {
            'info': 'info',
            'warning': 'warning',
            'error': 'danger',
            'critical': 'danger'
        };
        return colors[severity] || 'info';
    }
    
    formatTime(timestamp) {
        if (!timestamp) return 'Never';
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
        return date.toLocaleDateString();
    }
    
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
                notification.remove();
            }
        }, 5000);
    }
}

// Initialize when DOM is ready
// DISABLED: Enhanced Twin Management is redundant with Twin Registry Management
// document.addEventListener('DOMContentLoaded', () => {
//     new TwinRegistryEnhanced();
// }); 