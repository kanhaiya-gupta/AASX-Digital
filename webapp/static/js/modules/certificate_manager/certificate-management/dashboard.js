/**
 * Certificate Manager - Dashboard Module
 * Handles dashboard functionality, statistics, and table management
 */

export class DashboardManager {
    constructor() {
        // Authentication properties
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
        
        this.certificates = [];
        this.filters = {
            status: 'all',
            search: '',
            dateRange: null
        };
        this.sortBy = 'created_at';
        this.sortOrder = 'desc';
    }

    /**
     * Wait for central authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Dashboard Manager: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Dashboard Manager: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Dashboard Manager: Auth system ready event received');
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
                console.warn('⚠️ Dashboard Manager: Timeout waiting for auth system');
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
            console.log('🔐 Dashboard Manager: Auth state updated', {
                isAuthenticated: this.isAuthenticated,
                user: this.currentUser?.username || 'anonymous'
            });
        } else {
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
            console.log('🔐 Dashboard Manager: No auth manager available');
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
        this.certificates = [];
        this.filters = {
            status: 'all',
            search: '',
            dateRange: null
        };
        console.log('🧹 Dashboard Manager: Sensitive data cleared');
    }

    /**
     * Get authentication headers
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
     * Initialize dashboard
     */
    async init() {
        console.log('📊 Initializing dashboard manager...');
        
        try {
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            this.setupEventListeners();
            
            console.log('✅ Dashboard manager initialized');
            
        } catch (error) {
            console.error('❌ Error initializing dashboard manager:', error);
            this.showError('Failed to initialize dashboard manager');
        }
    }

    /**
     * Update dashboard statistics
     */
    updateStats(certificates) {
        console.log('📊 Updating dashboard statistics...');
        
        try {
            // Calculate statistics
            const stats = this.calculateStats(certificates);
            
            // Update UI elements
            this.updateStatCards(stats);
            this.updateCharts(stats);
            
            console.log('✅ Dashboard statistics updated');
            
        } catch (error) {
            console.error('❌ Error updating statistics:', error);
        }
    }

    /**
     * Calculate statistics from certificates
     */
    calculateStats(certificates) {
        const total = certificates.length;
        const active = certificates.filter(c => c.status === 'active').length;
        const pending = certificates.filter(c => c.status === 'pending').length;
        const completed = certificates.filter(c => c.status === 'completed').length;
        const verified = certificates.filter(c => c.verification_status === 'verified').length;
        
        const averageHealthScore = total > 0 
            ? Math.round(certificates.reduce((sum, cert) => sum + (cert.health_score || 0), 0) / total)
            : 0;
        
        return {
            total,
            active,
            pending,
            completed,
            verified,
            averageHealthScore,
            recentExports: Math.floor(Math.random() * 50) + 10 // Mock data
        };
    }

    /**
     * Update stat cards
     */
    updateStatCards(stats) {
        // Total certificates
        const totalElement = document.getElementById('total-certificates');
        if (totalElement) {
            totalElement.textContent = stats.total;
        }
        
        // Active certificates
        const activeElement = document.getElementById('active-certificates');
        if (activeElement) {
            activeElement.textContent = stats.active;
        }
        
        // Pending certificates
        const pendingElement = document.getElementById('pending-certificates');
        if (pendingElement) {
            pendingElement.textContent = stats.pending;
        }
        
        // Recent exports
        const exportsElement = document.getElementById('recent-exports');
        if (exportsElement) {
            exportsElement.textContent = stats.recentExports;
        }
    }

    /**
     * Update charts
     */
    updateCharts(stats) {
        // This would update any charts on the dashboard
        console.log('📈 Charts would be updated with stats:', stats);
    }

    /**
     * Update certificate table
     */
    updateTable(certificates, forceUpdate = false) {
        console.log('📋 Updating certificate table...');
        
        try {
            const tbody = document.getElementById('certificates-tbody');
            if (!tbody) {
                console.warn('Certificate table body not found');
                return;
            }
            
            // Check if table already has content and we're not forcing an update
            if (!forceUpdate && tbody.children.length > 0) {
                console.log('📋 Table already has content, skipping update');
                return;
            }
            
            // Add a small delay to prevent immediate overwriting of static content
            setTimeout(() => {
                // Clear existing rows
                tbody.innerHTML = '';
                
                // Add certificate rows
                certificates.forEach(certificate => {
                    const row = this.createCertificateRow(certificate);
                    tbody.appendChild(row);
                });
                
                console.log(`✅ Table updated with ${certificates.length} certificates`);
            }, 100); // 100ms delay
            
        } catch (error) {
            console.error('❌ Error updating table:', error);
        }
    }

    /**
     * Create certificate table row with enhanced structure
     */
    createCertificateRow(certificate) {
        const row = document.createElement('tr');
        row.className = 'cm-certificate-row';
        
        // Get status badge class and icon
        const statusClass = this.getStatusClass(certificate.status);
        const statusIcon = this.getStatusIcon(certificate.status);
        
        // Get progress class based on health score
        const progressClass = this.getProgressClass(certificate.health_score || 0);
        
        row.innerHTML = `
            <td class="cm-checkbox-column">
                <div class="form-check">
                    <input type="checkbox" class="form-check-input cm-certificate-checkbox certificate-select" value="${certificate.certificate_id}">
                </div>
            </td>
            <td class="cm-id-column">
                <div class="cm-certificate-info">
                    <div class="cm-certificate-id fw-bold text-primary">${certificate.certificate_id}</div>
                    <div class="cm-certificate-name small text-muted">${certificate.twin_name || 'N/A'}</div>
                </div>
            </td>
            <td class="cm-twin-column">
                <div class="cm-twin-info">
                    <div class="cm-twin-id fw-semibold">${certificate.twin_id || 'N/A'}</div>
                    <div class="cm-twin-type small text-muted">${certificate.twin_name || 'N/A'}</div>
                </div>
            </td>
            <td class="cm-project-column">
                <div class="cm-project-info">
                    <div class="cm-project-name fw-semibold">${certificate.project_name || 'N/A'}</div>
                    <div class="cm-project-category small text-muted">${certificate.use_case_name || 'N/A'}</div>
                </div>
            </td>
            <td class="cm-status-column">
                <span class="cm-status-badge cm-status-${statusClass}">
                    <i class="${statusIcon} me-1"></i>${this.capitalizeFirst(certificate.status)}
                </span>
            </td>
            <td class="cm-progress-column">
                <div class="cm-progress-container">
                    <div class="cm-progress-bar">
                        <div class="cm-progress-fill ${progressClass}" style="width: ${certificate.health_score || 0}%"></div>
                    </div>
                    <div class="cm-progress-text small fw-semibold">${certificate.health_score || 0}%</div>
                </div>
            </td>
            <td class="cm-created-column">
                <div class="cm-date-info">
                    <div class="cm-created-date small fw-semibold">${this.formatDate(certificate.created_at)}</div>
                    <div class="cm-updated-date small text-muted">Updated: ${this.formatDate(certificate.updated_at)}</div>
                </div>
            </td>
            <td class="cm-actions-column">
                <div class="cm-actions-buttons">
                    <button class="cm-btn cm-btn-view btn btn-outline-primary btn-sm me-1" 
                            onclick="window.CertificateManager.viewCertificate('${certificate.certificate_id}')" 
                            title="View Certificate">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="cm-btn cm-btn-actions btn btn-outline-secondary btn-sm" 
                            onclick="window.CertificateManager.showCertificateActions('${certificate.certificate_id}')" 
                            title="More Actions">
                        <i class="fas fa-ellipsis-v"></i>
                    </button>
                </div>
            </td>
        `;
        
        return row;
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('search-certificates');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filters.search = e.target.value;
                this.applyFilters();
            });
        }
        
        // Filter dropdowns
        const statusFilter = document.getElementById('status-filter');
        if (statusFilter) {
            statusFilter.addEventListener('change', (e) => {
                this.filters.status = e.target.value;
                this.applyFilters();
            });
        }
        
        // Sort functionality
        document.addEventListener('click', (e) => {
            if (e.target.matches('.sort-header')) {
                const column = e.target.dataset.column;
                this.toggleSort(column);
            }
        });
        
        // Copy ID functionality
        document.addEventListener('click', (e) => {
            if (e.target.matches('.copy-id')) {
                const id = e.target.dataset.id;
                this.copyToClipboard(id);
            }
        });
        
        // Select all functionality
        const selectAllCheckbox = document.getElementById('select-all');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                this.toggleSelectAll(e.target.checked);
            });
        }
    }

    /**
     * Apply filters
     */
    applyFilters() {
        console.log('🔍 Applying filters:', this.filters);
        
        // This would trigger a filter update in the main module
        if (window.CertificateManager) {
            window.CertificateManager.filterCertificates();
        }
    }

    /**
     * Toggle sort
     */
    toggleSort(column) {
        if (this.sortBy === column) {
            this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortBy = column;
            this.sortOrder = 'asc';
        }
        
        // Update sort indicators
        document.querySelectorAll('.sort-header').forEach(header => {
            header.classList.remove('sort-asc', 'sort-desc');
        });
        
        const currentHeader = document.querySelector(`[data-column="${column}"]`);
        if (currentHeader) {
            currentHeader.classList.add(`sort-${this.sortOrder}`);
        }
        
        // Trigger sort
        this.applyFilters();
    }

    /**
     * Toggle select all
     */
    toggleSelectAll(checked) {
        const checkboxes = document.querySelectorAll('.certificate-select');
        checkboxes.forEach(checkbox => {
            checkbox.checked = checked;
        });
        
        this.updateBulkActions();
    }

    /**
     * Update bulk actions
     */
    updateBulkActions() {
        const selectedCount = document.querySelectorAll('.certificate-select:checked').length;
        const bulkActionsContainer = document.getElementById('bulk-actions');
        
        if (bulkActionsContainer) {
            if (selectedCount > 0) {
                bulkActionsContainer.style.display = 'block';
                bulkActionsContainer.innerHTML = `
                    <div class="bulk-actions-content">
                        <span class="selected-count">${selectedCount} certificate(s) selected</span>
                        <button class="btn btn-sm btn-outline-primary" onclick="exportSelected()">
                            <i class="fas fa-download"></i> Export Selected
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteSelected()">
                            <i class="fas fa-trash"></i> Delete Selected
                        </button>
                    </div>
                `;
            } else {
                bulkActionsContainer.style.display = 'none';
            }
        }
    }

    /**
     * Copy to clipboard
     */
    copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                this.showSuccess('ID copied to clipboard');
            }).catch(() => {
                this.fallbackCopyToClipboard(text);
            });
        } else {
            this.fallbackCopyToClipboard(text);
        }
    }

    /**
     * Fallback copy to clipboard
     */
    fallbackCopyToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        
        try {
            document.execCommand('copy');
            this.showSuccess('ID copied to clipboard');
        } catch (err) {
            this.showError('Failed to copy ID');
        }
        
        document.body.removeChild(textArea);
    }

    /**
     * Get status class
     */
    getStatusClass(status) {
        const statusMap = {
            'active': 'active',
            'pending': 'pending',
            'completed': 'completed',
            'ready': 'ready',
            'error': 'error',
            'in_progress': 'pending'
        };
        return statusMap[status] || 'pending';
    }

    /**
     * Get status icon
     */
    getStatusIcon(status) {
        const iconMap = {
            'active': 'fas fa-check-circle',
            'pending': 'fas fa-clock',
            'completed': 'fas fa-check',
            'ready': 'fas fa-check',
            'error': 'fas fa-exclamation-circle',
            'in_progress': 'fas fa-clock'
        };
        return iconMap[status] || 'fas fa-clock';
    }

    /**
     * Get progress class based on health score
     */
    getProgressClass(score) {
        if (score >= 90) return 'cm-progress-excellent';
        if (score >= 70) return 'cm-progress-good';
        if (score >= 50) return 'cm-progress-warning';
        return 'cm-progress-danger';
    }

    /**
     * Capitalize first letter
     */
    capitalizeFirst(str) {
        if (!str) return 'N/A';
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    /**
     * Format date
     */
    formatDate(dateString) {
        if (!dateString) return 'N/A';
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString();
        } catch (error) {
            return dateString;
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        console.error('❌ Error:', message);
        if (typeof showNotification === 'function') {
            showNotification(message, 'error');
        } else {
            alert('Error: ' + message);
        }
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        console.log('✅ Success:', message);
        if (typeof showNotification === 'function') {
            showNotification(message, 'success');
        }
    }

    /**
     * Cleanup
     */
    destroy() {
        // Remove event listeners
        const searchInput = document.getElementById('search-certificates');
        if (searchInput) {
            searchInput.removeEventListener('input', this.handleSearch);
        }
        
        // Reset state
        this.certificates = [];
        this.filters = {
            status: 'all',
            search: '',
            dateRange: null
        };
    }
}

// Export the class
export default DashboardManager; 