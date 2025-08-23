/**
 * Instance UI Module
 * Handles UI updates and interactions for instance management
 */

export class InstanceUI {
    constructor() {
        this.activeModals = new Set();
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
    }

    async init() {
        try {
            console.log('🔄 Initializing Instance UI...');
            
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            console.log('✅ Instance UI initialized');
        } catch (error) {
            console.error('❌ Instance UI initialization failed:', error);
            throw error;
        }
    }

    updateInstanceTable(instances) {
        const tableBody = document.getElementById('instanceTableBody');
        if (!tableBody) return;

        tableBody.innerHTML = '';

        if (instances.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center text-muted">
                        <i class="fas fa-inbox me-2"></i>No instances found
                    </td>
                </tr>
            `;
            return;
        }

        instances.forEach(instance => {
            const row = this.createInstanceRow(instance);
            tableBody.appendChild(row);
        });
    }

    createInstanceRow(instance) {
        const row = document.createElement('tr');
        
        const createdDate = new Date(instance.created_at).toLocaleString();
        const statusClass = this.getStatusClass(instance.is_active);
        const typeClass = this.getInstanceTypeClass(instance.instance_data?.type || 'version');
        
        row.innerHTML = `
            <td>
                <span class="version-number">${instance.version || 'v1'}</span>
            </td>
            <td>
                <code class="text-muted">${instance.instance_id?.substring(0, 8)}...</code>
            </td>
            <td>${instance.instance_data?.twin_name || 'Unknown Twin'}</td>
            <td>
                <span class="instance-type-badge ${typeClass}">
                    ${instance.instance_data?.type || 'version'}
                </span>
            </td>
            <td>${createdDate}</td>
            <td>${instance.created_by || 'System'}</td>
            <td>
                <span class="instance-status ${statusClass}">
                    ${instance.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td>
                <span class="instance-size">
                    ${this.formatInstanceSize(instance.instance_data)}
                </span>
            </td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    <button class="btn btn-outline-primary" onclick="viewInstanceDetails('${instance.instance_id}')" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    ${instance.is_active ? '' : `
                        <button class="btn btn-outline-success" onclick="activateInstance('${instance.instance_id}')" title="Activate">
                            <i class="fas fa-play"></i>
                        </button>
                    `}
                    <button class="btn btn-outline-warning" onclick="restoreInstance('${instance.instance_id}')" title="Restore">
                        <i class="fas fa-undo"></i>
                    </button>
                    <button class="btn btn-outline-danger" onclick="deleteInstance('${instance.instance_id}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;

        return row;
    }

    updateInstanceSummary(summary) {
        const elements = {
            totalInstances: document.getElementById('totalInstances'),
            activeInstances: document.getElementById('activeInstances'),
            latestVersion: document.getElementById('latestVersion'),
            instanceHistory: document.getElementById('instanceHistory')
        };

        if (elements.totalInstances) elements.totalInstances.textContent = summary.total;
        if (elements.activeInstances) elements.activeInstances.textContent = summary.active;
        if (elements.latestVersion) elements.latestVersion.textContent = summary.latest_version;
        if (elements.instanceHistory) elements.instanceHistory.textContent = summary.history;
    }

    updateTwinFilter() {
        const filter = document.getElementById('instanceTwinFilter');
        if (!filter) return;

        // This would typically load twins from the backend
        // For now, we'll add a placeholder
        if (filter.children.length <= 1) {
            filter.innerHTML = `
                <option value="">All Twins</option>
                <option value="twin1">Twin 1</option>
                <option value="twin2">Twin 2</option>
            `;
        }
    }

    updateInstanceTypeUI(instanceType) {
        const descriptionField = document.getElementById('instanceDescription');
        if (!descriptionField) return;

        const descriptions = {
            snapshot: 'Quick snapshot of current twin state',
            backup: 'Full backup with all data and metadata',
            version: 'New version with incremental changes',
            branch: 'Branch for experimental changes'
        };

        descriptionField.placeholder = descriptions[instanceType] || 'Instance description';
    }

    toggleSelectAll(checked) {
        const checkboxes = document.querySelectorAll('#instanceTableBody input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.checked = checked;
        });

        this.updateSelectedCount();
    }

    updateSelectedCount() {
        const selectedCount = document.querySelectorAll('#instanceTableBody input[type="checkbox"]:checked').length;
        const countElement = document.getElementById('selectedCount');
        if (countElement) {
            countElement.textContent = selectedCount;
        }

        // Update bulk operation buttons
        const bulkButtons = ['bulkStartBtn', 'bulkStopBtn', 'bulkSyncBtn'];
        bulkButtons.forEach(btnId => {
            const btn = document.getElementById(btnId);
            if (btn) {
                btn.disabled = selectedCount === 0;
            }
        });
    }

    showInstanceDetails(instance) {
        const modal = document.getElementById('instanceDetailsModal');
        const content = document.getElementById('instanceDetailsContent');
        
        if (!modal || !content) return;

        const createdDate = new Date(instance.created_at).toLocaleString();
        const metadata = instance.instance_metadata || {};
        
        content.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Instance Information</h6>
                    <table class="table table-sm">
                        <tr><td><strong>Instance ID:</strong></td><td><code>${instance.instance_id}</code></td></tr>
                        <tr><td><strong>Version:</strong></td><td>${instance.version || 'v1'}</td></tr>
                        <tr><td><strong>Type:</strong></td><td>${instance.instance_data?.type || 'version'}</td></tr>
                        <tr><td><strong>Created:</strong></td><td>${createdDate}</td></tr>
                        <tr><td><strong>Created By:</strong></td><td>${instance.created_by || 'System'}</td></tr>
                        <tr><td><strong>Status:</strong></td><td>
                            <span class="instance-status ${this.getStatusClass(instance.is_active)}">
                                ${instance.is_active ? 'Active' : 'Inactive'}
                            </span>
                        </td></tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6>Metadata</h6>
                    <pre class="bg-light p-2 rounded"><code>${JSON.stringify(metadata, null, 2)}</code></pre>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-12">
                    <h6>Instance Data</h6>
                    <pre class="bg-light p-2 rounded"><code>${JSON.stringify(instance.instance_data, null, 2)}</code></pre>
                </div>
            </div>
        `;

        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
        this.activeModals.add(modalInstance);
    }

    showInstanceComparison(comparison) {
        const modal = document.getElementById('instanceComparisonModal');
        const instance1Details = document.getElementById('instance1Details');
        const instance2Details = document.getElementById('instance2Details');
        const differences = document.getElementById('instanceDifferences');
        
        if (!modal || !instance1Details || !instance2Details || !differences) return;

        // Populate instance details
        instance1Details.innerHTML = this.formatInstanceComparison(comparison.instance1);
        instance2Details.innerHTML = this.formatInstanceComparison(comparison.instance2);

        // Show differences
        differences.innerHTML = `
            <div class="comparison-diff">
                <h6>Key Differences:</h6>
                <ul>
                    ${comparison.differences?.map(diff => `<li>${diff}</li>`).join('') || '<li>No significant differences found</li>'}
                </ul>
            </div>
        `;

        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
        this.activeModals.add(modalInstance);
    }

    formatInstanceComparison(instance) {
        if (!instance) return '<p class="text-muted">No instance selected</p>';

        return `
            <div class="card">
                <div class="card-body">
                    <h6>${instance.instance_data?.twin_name || 'Unknown Twin'}</h6>
                    <p><strong>Version:</strong> ${instance.version || 'v1'}</p>
                    <p><strong>Type:</strong> ${instance.instance_data?.type || 'version'}</p>
                    <p><strong>Created:</strong> ${new Date(instance.created_at).toLocaleString()}</p>
                    <p><strong>Status:</strong> 
                        <span class="instance-status ${this.getStatusClass(instance.is_active)}">
                            ${instance.is_active ? 'Active' : 'Inactive'}
                        </span>
                    </p>
                </div>
            </div>
        `;
    }

    showSuccess(message) {
        // Create or update success alert
        this.showAlert(message, 'success');
    }

    showError(message) {
        // Create or update error alert
        this.showAlert(message, 'danger');
    }

    showAlert(message, type) {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert-auto-dismiss');
        existingAlerts.forEach(alert => alert.remove());

        // Create new alert
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show alert-auto-dismiss`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Add to page
        const container = document.querySelector('.container-fluid') || document.body;
        container.insertBefore(alert, container.firstChild);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }

    getStatusClass(isActive) {
        return isActive ? 'active' : 'inactive';
    }

    getInstanceTypeClass(type) {
        const typeClasses = {
            snapshot: 'snapshot',
            backup: 'backup',
            version: 'version',
            branch: 'branch'
        };
        return typeClasses[type] || 'version';
    }

    formatInstanceSize(instanceData) {
        if (!instanceData) return '0 KB';
        
        // Calculate approximate size based on data complexity
        const dataSize = JSON.stringify(instanceData).length;
        const kb = Math.round(dataSize / 1024);
        
        if (kb < 1024) {
            return `${kb} KB`;
        } else {
            const mb = (kb / 1024).toFixed(1);
            return `${mb} MB`;
        }
    }

    /**
     * Wait for central authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Instance UI: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Instance UI: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Instance UI: Auth system ready event received');
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
                console.warn('⚠️ Instance UI: Timeout waiting for auth system');
                resolve();
            }, 10000);
        });
    }

    /**
     * Update authentication state
     */
    updateAuthState() {
        if (window.authManager) {
            this.isAuthenticated = window.authManager.isAuthenticated();
            this.currentUser = null; // User info not needed currently
            this.authToken = window.authManager.getStoredToken();
            console.log('🔐 Instance UI: Auth state updated', {
                isAuthenticated: this.isAuthenticated,
                user: this.currentUser?.username || 'anonymous'
            });
        } else {
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
            console.log('🔐 Instance UI: No auth manager available');
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
        });

        window.addEventListener('logout', () => {
            this.updateAuthState();
            // Clear sensitive data when user logs out
            this.clearSensitiveData();
        });
    }

    /**
     * Clear sensitive data on logout
     */
    clearSensitiveData() {
        // Clear any cached data that might be user-specific
        console.log('🧹 Instance UI: Sensitive data cleared');
    }

    cleanup() {
        // Close all active modals
        this.activeModals.forEach(modal => {
            if (modal && typeof modal.hide === 'function') {
                modal.hide();
            }
        });
        this.activeModals.clear();
    }
} 