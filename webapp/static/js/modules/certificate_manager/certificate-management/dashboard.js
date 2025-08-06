/**
 * Certificate Manager - Dashboard Module
 * Handles dashboard functionality, statistics, and table management
 */

export class DashboardManager {
    constructor() {
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
     * Initialize dashboard
     */
    async init() {
        console.log('📊 Initializing dashboard manager...');
        
        try {
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
    updateTable(certificates) {
        console.log('📋 Updating certificate table...');
        
        try {
            const tbody = document.getElementById('certificates-tbody');
            if (!tbody) {
                console.warn('Certificate table body not found');
                return;
            }
            
            // Clear existing rows
            tbody.innerHTML = '';
            
            // Add certificate rows
            certificates.forEach(certificate => {
                const row = this.createCertificateRow(certificate);
                tbody.appendChild(row);
            });
            
            console.log(`✅ Table updated with ${certificates.length} certificates`);
            
        } catch (error) {
            console.error('❌ Error updating table:', error);
        }
    }

    /**
     * Create certificate table row
     */
    createCertificateRow(certificate) {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>
                <input type="checkbox" class="certificate-select" value="${certificate.certificate_id}">
            </td>
            <td>
                <div class="certificate-id">
                    <span class="id-text">${certificate.certificate_id}</span>
                    <button class="btn btn-sm btn-link copy-id" data-id="${certificate.certificate_id}">
                        <i class="fas fa-copy"></i>
                    </button>
                </div>
            </td>
            <td>
                <div class="twin-info">
                    <div class="twin-name">${certificate.twin_name}</div>
                    <div class="twin-id">${certificate.twin_id}</div>
                </div>
            </td>
            <td>
                <div class="project-info">
                    <div class="project-name">${certificate.project_name}</div>
                    <div class="use-case">${certificate.use_case_name}</div>
                </div>
            </td>
            <td>
                <div class="status-info">
                    <span class="badge badge-${this.getStatusClass(certificate.status)}">
                        ${certificate.status}
                    </span>
                    <div class="health-score">
                        <div class="progress">
                            <div class="progress-bar bg-${this.getHealthScoreClass(certificate.health_score)}" 
                                 style="width: ${certificate.health_score}%"></div>
                        </div>
                        <span class="score-text">${certificate.health_score}%</span>
                    </div>
                </div>
            </td>
            <td>
                <div class="date-info">
                    <div class="created-date">${this.formatDate(certificate.created_at)}</div>
                    <div class="updated-date">Updated: ${this.formatDate(certificate.updated_at)}</div>
                </div>
            </td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-outline-primary" onclick="window.CertificateManager.viewCertificate('${certificate.certificate_id}')" title="View Certificate">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-success" onclick="window.CertificateManager.exportCertificate('${certificate.certificate_id}')" title="Export Certificate">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-info" onclick="window.CertificateManager.showCertificateActions('${certificate.certificate_id}')" title="More Actions">
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
            'active': 'success',
            'pending': 'warning',
            'completed': 'info',
            'error': 'danger',
            'in_progress': 'primary'
        };
        return statusMap[status] || 'secondary';
    }

    /**
     * Get health score class
     */
    getHealthScoreClass(score) {
        if (score >= 90) return 'success';
        if (score >= 70) return 'warning';
        return 'danger';
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