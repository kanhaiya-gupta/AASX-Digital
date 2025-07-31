/**
 * Certificate UI Module
 * Handles user interface management, form handling, and UI interactions
 */

export default class CertificateUI {
    constructor() {
        this.isInitialized = false;
        this.config = {
            apiBaseUrl: '/api/certificate-manager',
            containerId: 'certificate-manager-container',
            theme: 'light',
            language: 'en',
            autoRefresh: true,
            refreshInterval: 30000, // 30 seconds
            animationsEnabled: true,
            notificationsEnabled: true,
            confirmationsEnabled: true,
            maxDisplayItems: 50,
            paginationEnabled: true,
            itemsPerPage: 20,
            searchEnabled: true,
            filterEnabled: true,
            sortEnabled: true
        };

        this.containers = new Map();
        this.forms = new Map();
        this.tables = new Map();
        this.modals = new Map();
        this.notifications = new Map();
        this.eventListeners = new Map();
        this.refreshIntervals = new Map();
        this.currentPage = 1;
        this.currentFilters = {};
        this.currentSort = {};
        this.searchQuery = '';
    }

    /**
     * Initialize the Certificate UI
     */
    async init() {
        console.log('🔧 Initializing Certificate UI...');

        try {
            // Load configuration
            await this.loadConfiguration();

            // Initialize UI components
            this.initializeUIComponents();

            // Set up event listeners
            this.setupEventListeners();

            // Initialize forms
            this.initializeForms();

            // Initialize tables
            this.initializeTables();

            // Initialize modals
            this.initializeModals();

            // Start auto-refresh
            if (this.config.autoRefresh) {
                this.startAutoRefresh();
            }

            this.isInitialized = true;
            console.log('✅ Certificate UI initialized');

        } catch (error) {
            console.error('❌ Certificate UI initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load configuration from server
     */
    async loadConfiguration() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/ui-config`);
            if (response.ok) {
                const config = await response.json();
                this.config = { ...this.config, ...config };
            }
        } catch (error) {
            console.warn('Could not load UI configuration from server, using defaults:', error);
        }
    }

    /**
     * Initialize UI components
     */
    initializeUIComponents() {
        // Main container
        const mainContainer = document.getElementById(this.config.containerId);
        if (mainContainer) {
            this.containers.set('main', mainContainer);
        }

        // Certificate list container
        const listContainer = document.getElementById('certificate-list-container');
        if (listContainer) {
            this.containers.set('list', listContainer);
        }

        // Certificate details container
        const detailsContainer = document.getElementById('certificate-details-container');
        if (detailsContainer) {
            this.containers.set('details', detailsContainer);
        }

        // Certificate form container
        const formContainer = document.getElementById('certificate-form-container');
        if (formContainer) {
            this.containers.set('form', formContainer);
        }

        // Search container
        const searchContainer = document.getElementById('certificate-search-container');
        if (searchContainer) {
            this.containers.set('search', searchContainer);
        }

        // Filter container
        const filterContainer = document.getElementById('certificate-filter-container');
        if (filterContainer) {
            this.containers.set('filter', filterContainer);
        }
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Listen for certificate events
        window.addEventListener('certificateCreated', (event) => {
            this.handleCertificateCreated(event.detail);
        });

        window.addEventListener('certificateUpdated', (event) => {
            this.handleCertificateUpdated(event.detail);
        });

        window.addEventListener('certificateDeleted', (event) => {
            this.handleCertificateDeleted(event.detail);
        });

        window.addEventListener('certificateValidated', (event) => {
            this.handleCertificateValidated(event.detail);
        });

        window.addEventListener('certificateStored', (event) => {
            this.handleCertificateStored(event.detail);
        });

        window.addEventListener('certificateImported', (event) => {
            this.handleCertificateImported(event.detail);
        });

        // Listen for form submissions
        document.addEventListener('submit', (event) => {
            this.handleFormSubmission(event);
        });

        // Listen for button clicks
        document.addEventListener('click', (event) => {
            this.handleButtonClick(event);
        });

        // Listen for search input
        document.addEventListener('input', (event) => {
            this.handleSearchInput(event);
        });

        // Listen for filter changes
        document.addEventListener('change', (event) => {
            this.handleFilterChange(event);
        });
    }

    /**
     * Initialize forms
     */
    initializeForms() {
        // Certificate creation form
        const createForm = document.getElementById('certificate-create-form');
        if (createForm) {
            this.forms.set('create', createForm);
            this.setupFormValidation(createForm);
        }

        // Certificate import form
        const importForm = document.getElementById('certificate-import-form');
        if (importForm) {
            this.forms.set('import', importForm);
            this.setupFormValidation(importForm);
        }

        // Certificate search form
        const searchForm = document.getElementById('certificate-search-form');
        if (searchForm) {
            this.forms.set('search', searchForm);
        }

        // Certificate filter form
        const filterForm = document.getElementById('certificate-filter-form');
        if (filterForm) {
            this.forms.set('filter', filterForm);
        }
    }

    /**
     * Initialize tables
     */
    initializeTables() {
        // Certificate list table
        const listTable = document.getElementById('certificate-list-table');
        if (listTable) {
            this.tables.set('list', listTable);
            this.setupTableSorting(listTable);
            this.setupTablePagination(listTable);
        }

        // Certificate details table
        const detailsTable = document.getElementById('certificate-details-table');
        if (detailsTable) {
            this.tables.set('details', detailsTable);
        }
    }

    /**
     * Initialize modals
     */
    initializeModals() {
        // Certificate details modal
        const detailsModal = document.getElementById('certificate-details-modal');
        if (detailsModal) {
            this.modals.set('details', detailsModal);
            this.setupModalClose(detailsModal);
        }

        // Certificate creation modal
        const createModal = document.getElementById('certificate-create-modal');
        if (createModal) {
            this.modals.set('create', createModal);
            this.setupModalClose(createModal);
        }

        // Certificate import modal
        const importModal = document.getElementById('certificate-import-modal');
        if (importModal) {
            this.modals.set('import', importModal);
            this.setupModalClose(importModal);
        }

        // Certificate confirmation modal
        const confirmModal = document.getElementById('certificate-confirm-modal');
        if (confirmModal) {
            this.modals.set('confirm', confirmModal);
            this.setupModalClose(confirmModal);
        }
    }

    /**
     * Start auto-refresh
     */
    startAutoRefresh() {
        const interval = setInterval(() => {
            this.refreshCertificateList();
        }, this.config.refreshInterval);

        this.refreshIntervals.set('list', interval);
    }

    /**
     * Handle certificate created event
     */
    handleCertificateCreated(detail) {
        const { certificate } = detail;
        
        // Add to table
        this.addCertificateToTable(certificate);
        
        // Show notification
        this.showNotification('Certificate created successfully', 'success');
        
        // Close modal if open
        this.closeModal('create');
        
        // Update statistics
        this.updateStatistics();
    }

    /**
     * Handle certificate updated event
     */
    handleCertificateUpdated(detail) {
        const { certificate } = detail;
        
        // Update table row
        this.updateCertificateInTable(certificate);
        
        // Show notification
        this.showNotification('Certificate updated successfully', 'success');
        
        // Update statistics
        this.updateStatistics();
    }

    /**
     * Handle certificate deleted event
     */
    handleCertificateDeleted(detail) {
        const { certificateId } = detail;
        
        // Remove from table
        this.removeCertificateFromTable(certificateId);
        
        // Show notification
        this.showNotification('Certificate deleted successfully', 'success');
        
        // Update statistics
        this.updateStatistics();
    }

    /**
     * Handle certificate validated event
     */
    handleCertificateValidated(detail) {
        const { certificate, results } = detail;
        
        // Update validation status in table
        this.updateCertificateValidationStatus(certificate.id, results);
        
        // Show validation results
        this.showValidationResults(certificate, results);
    }

    /**
     * Handle certificate stored event
     */
    handleCertificateStored(detail) {
        const { certificate } = detail;
        
        // Show notification
        this.showNotification('Certificate stored successfully', 'success');
    }

    /**
     * Handle certificate imported event
     */
    handleCertificateImported(detail) {
        const { certificates } = detail;
        
        // Add to table
        certificates.forEach(cert => {
            this.addCertificateToTable(cert);
        });
        
        // Show notification
        this.showNotification(`${certificates.length} certificates imported successfully`, 'success');
        
        // Close modal if open
        this.closeModal('import');
        
        // Update statistics
        this.updateStatistics();
    }

    /**
     * Handle form submission
     */
    handleFormSubmission(event) {
        const form = event.target;
        const formId = form.id;

        if (formId === 'certificate-create-form') {
            event.preventDefault();
            this.handleCreateFormSubmission(form);
        } else if (formId === 'certificate-import-form') {
            event.preventDefault();
            this.handleImportFormSubmission(form);
        } else if (formId === 'certificate-search-form') {
            event.preventDefault();
            this.handleSearchFormSubmission(form);
        } else if (formId === 'certificate-filter-form') {
            event.preventDefault();
            this.handleFilterFormSubmission(form);
        }
    }

    /**
     * Handle create form submission
     */
    async handleCreateFormSubmission(form) {
        try {
            const formData = new FormData(form);
            const certificateData = this.parseFormData(formData);
            
            // Validate form data
            if (!this.validateCertificateData(certificateData)) {
                return;
            }

            // Show loading state
            this.showLoadingState(form);

            // Create certificate
            const core = window.CertificateManagerModule.getCore();
            await core.createCertificate(certificateData);

            // Reset form
            form.reset();
            this.hideLoadingState(form);

        } catch (error) {
            console.error('Create form submission failed:', error);
            this.showNotification('Failed to create certificate', 'error');
            this.hideLoadingState(form);
        }
    }

    /**
     * Handle import form submission
     */
    async handleImportFormSubmission(form) {
        try {
            const formData = new FormData(form);
            const files = formData.get('certificates');
            
            if (!files || files.length === 0) {
                this.showNotification('Please select files to import', 'warning');
                return;
            }

            // Show loading state
            this.showLoadingState(form);

            // Import certificates
            const storage = window.CertificateManagerModule.getStorage();
            const certificates = await this.parseCertificateFiles(files);
            await storage.importCertificates(certificates);

            // Reset form
            form.reset();
            this.hideLoadingState(form);

        } catch (error) {
            console.error('Import form submission failed:', error);
            this.showNotification('Failed to import certificates', 'error');
            this.hideLoadingState(form);
        }
    }

    /**
     * Handle search form submission
     */
    handleSearchFormSubmission(form) {
        const formData = new FormData(form);
        const query = formData.get('search-query');
        
        this.searchQuery = query;
        this.refreshCertificateList();
    }

    /**
     * Handle filter form submission
     */
    handleFilterFormSubmission(form) {
        const formData = new FormData(form);
        const filters = {};
        
        for (const [key, value] of formData.entries()) {
            if (value) {
                filters[key] = value;
            }
        }
        
        this.currentFilters = filters;
        this.currentPage = 1;
        this.refreshCertificateList();
    }

    /**
     * Handle button click
     */
    handleButtonClick(event) {
        const button = event.target;
        const action = button.dataset.action;
        const certificateId = button.dataset.certificateId;

        if (!action) return;

        switch (action) {
            case 'view-certificate':
                this.viewCertificate(certificateId);
                break;
            case 'edit-certificate':
                this.editCertificate(certificateId);
                break;
            case 'delete-certificate':
                this.deleteCertificate(certificateId);
                break;
            case 'validate-certificate':
                this.validateCertificate(certificateId);
                break;
            case 'export-certificate':
                this.exportCertificate(certificateId);
                break;
            case 'renew-certificate':
                this.renewCertificate(certificateId);
                break;
            case 'revoke-certificate':
                this.revokeCertificate(certificateId);
                break;
            case 'open-create-modal':
                this.openModal('create');
                break;
            case 'open-import-modal':
                this.openModal('import');
                break;
            case 'close-modal':
                this.closeModal(button.dataset.modalId);
                break;
            case 'refresh-list':
                this.refreshCertificateList();
                break;
            case 'clear-filters':
                this.clearFilters();
                break;
            case 'export-list':
                this.exportCertificateList();
                break;
        }
    }

    /**
     * Handle search input
     */
    handleSearchInput(event) {
        const input = event.target;
        if (input.id === 'search-query') {
            // Debounce search
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => {
                this.searchQuery = input.value;
                this.refreshCertificateList();
            }, 500);
        }
    }

    /**
     * Handle filter change
     */
    handleFilterChange(event) {
        const select = event.target;
        if (select.classList.contains('filter-select')) {
            const filterName = select.name;
            const filterValue = select.value;
            
            if (filterValue) {
                this.currentFilters[filterName] = filterValue;
            } else {
                delete this.currentFilters[filterName];
            }
            
            this.currentPage = 1;
            this.refreshCertificateList();
        }
    }

    /**
     * View certificate details
     */
    async viewCertificate(certificateId) {
        try {
            const storage = window.CertificateManagerModule.getStorage();
            const certificate = await storage.retrieveCertificate(certificateId);
            
            this.displayCertificateDetails(certificate);
            this.openModal('details');
        } catch (error) {
            console.error('Failed to view certificate:', error);
            this.showNotification('Failed to load certificate details', 'error');
        }
    }

    /**
     * Edit certificate
     */
    async editCertificate(certificateId) {
        try {
            const storage = window.CertificateManagerModule.getStorage();
            const certificate = await storage.retrieveCertificate(certificateId);
            
            this.populateEditForm(certificate);
            this.openModal('create');
        } catch (error) {
            console.error('Failed to edit certificate:', error);
            this.showNotification('Failed to load certificate for editing', 'error');
        }
    }

    /**
     * Delete certificate
     */
    async deleteCertificate(certificateId) {
        if (!this.config.confirmationsEnabled || this.showConfirmation('Are you sure you want to delete this certificate?')) {
            try {
                const storage = window.CertificateManagerModule.getStorage();
                await storage.deleteCertificate(certificateId);
            } catch (error) {
                console.error('Failed to delete certificate:', error);
                this.showNotification('Failed to delete certificate', 'error');
            }
        }
    }

    /**
     * Validate certificate
     */
    async validateCertificate(certificateId) {
        try {
            const storage = window.CertificateManagerModule.getStorage();
            const validator = window.CertificateManagerModule.getValidator();
            
            const certificate = await storage.retrieveCertificate(certificateId);
            await validator.validateCertificate(certificate);
        } catch (error) {
            console.error('Failed to validate certificate:', error);
            this.showNotification('Failed to validate certificate', 'error');
        }
    }

    /**
     * Export certificate
     */
    async exportCertificate(certificateId) {
        try {
            const storage = window.CertificateManagerModule.getStorage();
            const blob = await storage.exportCertificates([certificateId]);
            
            // Create download link
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `certificate-${certificateId}.pem`;
            link.click();
            
            this.showNotification('Certificate exported successfully', 'success');
        } catch (error) {
            console.error('Failed to export certificate:', error);
            this.showNotification('Failed to export certificate', 'error');
        }
    }

    /**
     * Renew certificate
     */
    async renewCertificate(certificateId) {
        try {
            const core = window.CertificateManagerModule.getCore();
            await core.renewCertificate(certificateId);
        } catch (error) {
            console.error('Failed to renew certificate:', error);
            this.showNotification('Failed to renew certificate', 'error');
        }
    }

    /**
     * Revoke certificate
     */
    async revokeCertificate(certificateId) {
        const reason = prompt('Enter revocation reason:');
        if (reason) {
            try {
                const core = window.CertificateManagerModule.getCore();
                await core.revokeCertificate(certificateId, reason);
            } catch (error) {
                console.error('Failed to revoke certificate:', error);
                this.showNotification('Failed to revoke certificate', 'error');
            }
        }
    }

    /**
     * Refresh certificate list
     */
    async refreshCertificateList() {
        try {
            const storage = window.CertificateManagerModule.getStorage();
            const certificates = await storage.getCertificatesByFilter(this.currentFilters);
            
            this.displayCertificateList(certificates);
        } catch (error) {
            console.error('Failed to refresh certificate list:', error);
            this.showNotification('Failed to refresh certificate list', 'error');
        }
    }

    /**
     * Display certificate list
     */
    displayCertificateList(certificates) {
        const table = this.tables.get('list');
        if (!table) return;

        // Apply search filter
        let filteredCertificates = certificates;
        if (this.searchQuery) {
            filteredCertificates = certificates.filter(cert => 
                cert.subject?.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                cert.issuer?.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                cert.serialNumber?.toLowerCase().includes(this.searchQuery.toLowerCase())
            );
        }

        // Apply sorting
        if (this.currentSort.field) {
            filteredCertificates.sort((a, b) => {
                const aVal = a[this.currentSort.field];
                const bVal = b[this.currentSort.field];
                
                if (this.currentSort.direction === 'asc') {
                    return aVal > bVal ? 1 : -1;
                } else {
                    return aVal < bVal ? 1 : -1;
                }
            });
        }

        // Apply pagination
        if (this.config.paginationEnabled) {
            const startIndex = (this.currentPage - 1) * this.config.itemsPerPage;
            const endIndex = startIndex + this.config.itemsPerPage;
            filteredCertificates = filteredCertificates.slice(startIndex, endIndex);
        }

        // Clear table
        const tbody = table.querySelector('tbody');
        tbody.innerHTML = '';

        // Add rows
        filteredCertificates.forEach(certificate => {
            const row = this.createCertificateTableRow(certificate);
            tbody.appendChild(row);
        });

        // Update pagination
        if (this.config.paginationEnabled) {
            this.updatePagination(certificates.length);
        }
    }

    /**
     * Create certificate table row
     */
    createCertificateTableRow(certificate) {
        const row = document.createElement('tr');
        row.dataset.certificateId = certificate.id;

        const expiryDate = new Date(certificate.notAfter);
        const daysUntilExpiry = Math.ceil((expiryDate - new Date()) / (1000 * 60 * 60 * 24));
        
        const statusClass = this.getStatusClass(certificate.status, daysUntilExpiry);

        row.innerHTML = `
            <td>${certificate.subject || 'N/A'}</td>
            <td>${certificate.issuer || 'N/A'}</td>
            <td>${certificate.serialNumber || 'N/A'}</td>
            <td><span class="status-badge ${statusClass}">${certificate.status}</span></td>
            <td>${expiryDate.toLocaleDateString()}</td>
            <td>${daysUntilExpiry > 0 ? `${daysUntilExpiry} days` : 'Expired'}</td>
            <td>
                <button class="btn btn-sm btn-primary" data-action="view-certificate" data-certificate-id="${certificate.id}">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-warning" data-action="edit-certificate" data-certificate-id="${certificate.id}">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger" data-action="delete-certificate" data-certificate-id="${certificate.id}">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;

        return row;
    }

    /**
     * Get status class
     */
    getStatusClass(status, daysUntilExpiry) {
        if (status === 'revoked') return 'status-revoked';
        if (status === 'expired' || daysUntilExpiry <= 0) return 'status-expired';
        if (daysUntilExpiry <= 30) return 'status-warning';
        return 'status-active';
    }

    /**
     * Display certificate details
     */
    displayCertificateDetails(certificate) {
        const container = this.containers.get('details');
        if (!container) return;

        const expiryDate = new Date(certificate.notAfter);
        const daysUntilExpiry = Math.ceil((expiryDate - new Date()) / (1000 * 60 * 60 * 24));

        container.innerHTML = `
            <div class="certificate-details">
                <h3>Certificate Details</h3>
                <div class="detail-grid">
                    <div class="detail-item">
                        <label>Subject:</label>
                        <span>${certificate.subject || 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <label>Issuer:</label>
                        <span>${certificate.issuer || 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <label>Serial Number:</label>
                        <span>${certificate.serialNumber || 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <label>Status:</label>
                        <span class="status-badge ${this.getStatusClass(certificate.status, daysUntilExpiry)}">${certificate.status}</span>
                    </div>
                    <div class="detail-item">
                        <label>Valid From:</label>
                        <span>${new Date(certificate.notBefore).toLocaleString()}</span>
                    </div>
                    <div class="detail-item">
                        <label>Valid Until:</label>
                        <span>${expiryDate.toLocaleString()}</span>
                    </div>
                    <div class="detail-item">
                        <label>Days Until Expiry:</label>
                        <span>${daysUntilExpiry > 0 ? daysUntilExpiry : 'Expired'}</span>
                    </div>
                </div>
                <div class="certificate-actions">
                    <button class="btn btn-primary" data-action="validate-certificate" data-certificate-id="${certificate.id}">
                        Validate
                    </button>
                    <button class="btn btn-success" data-action="export-certificate" data-certificate-id="${certificate.id}">
                        Export
                    </button>
                    <button class="btn btn-warning" data-action="renew-certificate" data-certificate-id="${certificate.id}">
                        Renew
                    </button>
                    <button class="btn btn-danger" data-action="revoke-certificate" data-certificate-id="${certificate.id}">
                        Revoke
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        if (!this.config.notificationsEnabled) return;

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close">&times;</button>
            </div>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);

        // Close button
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        });
    }

    /**
     * Show confirmation dialog
     */
    showConfirmation(message) {
        if (!this.config.confirmationsEnabled) return true;
        return confirm(message);
    }

    /**
     * Open modal
     */
    openModal(modalId) {
        const modal = this.modals.get(modalId);
        if (modal) {
            modal.style.display = 'block';
            modal.classList.add('show');
        }
    }

    /**
     * Close modal
     */
    closeModal(modalId) {
        const modal = this.modals.get(modalId);
        if (modal) {
            modal.classList.remove('show');
            setTimeout(() => {
                modal.style.display = 'none';
            }, 300);
        }
    }

    /**
     * Setup modal close
     */
    setupModalClose(modal) {
        const closeBtn = modal.querySelector('.modal-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.closeModal(modal.id);
            });
        }

        // Close on backdrop click
        modal.addEventListener('click', (event) => {
            if (event.target === modal) {
                this.closeModal(modal.id);
            }
        });
    }

    /**
     * Setup form validation
     */
    setupFormValidation(form) {
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateInput(input);
            });
        });
    }

    /**
     * Validate input
     */
    validateInput(input) {
        const value = input.value.trim();
        const isValid = value.length > 0;
        
        if (isValid) {
            input.classList.remove('invalid');
            input.classList.add('valid');
        } else {
            input.classList.remove('valid');
            input.classList.add('invalid');
        }
        
        return isValid;
    }

    /**
     * Setup table sorting
     */
    setupTableSorting(table) {
        const headers = table.querySelectorAll('th[data-sort]');
        
        headers.forEach(header => {
            header.addEventListener('click', () => {
                const field = header.dataset.sort;
                const currentDirection = this.currentSort.direction;
                
                this.currentSort = {
                    field,
                    direction: currentDirection === 'asc' ? 'desc' : 'asc'
                };
                
                this.refreshCertificateList();
            });
        });
    }

    /**
     * Setup table pagination
     */
    setupTablePagination(table) {
        const paginationContainer = table.parentNode.querySelector('.pagination');
        if (paginationContainer) {
            this.paginationContainer = paginationContainer;
        }
    }

    /**
     * Update pagination
     */
    updatePagination(totalItems) {
        if (!this.paginationContainer) return;

        const totalPages = Math.ceil(totalItems / this.config.itemsPerPage);
        
        let paginationHTML = '';
        
        // Previous button
        paginationHTML += `
            <button class="btn btn-sm" ${this.currentPage === 1 ? 'disabled' : ''} 
                    data-action="change-page" data-page="${this.currentPage - 1}">
                Previous
            </button>
        `;
        
        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= this.currentPage - 2 && i <= this.currentPage + 2)) {
                paginationHTML += `
                    <button class="btn btn-sm ${i === this.currentPage ? 'btn-primary' : ''}" 
                            data-action="change-page" data-page="${i}">
                        ${i}
                    </button>
                `;
            } else if (i === this.currentPage - 3 || i === this.currentPage + 3) {
                paginationHTML += '<span class="pagination-ellipsis">...</span>';
            }
        }
        
        // Next button
        paginationHTML += `
            <button class="btn btn-sm" ${this.currentPage === totalPages ? 'disabled' : ''} 
                    data-action="change-page" data-page="${this.currentPage + 1}">
                Next
            </button>
        `;
        
        this.paginationContainer.innerHTML = paginationHTML;
    }

    /**
     * Show loading state
     */
    showLoadingState(form) {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        }
    }

    /**
     * Hide loading state
     */
    hideLoadingState(form) {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Submit';
        }
    }

    /**
     * Parse form data
     */
    parseFormData(formData) {
        const data = {};
        for (const [key, value] of formData.entries()) {
            data[key] = value;
        }
        return data;
    }

    /**
     * Validate certificate data
     */
    validateCertificateData(data) {
        const requiredFields = ['subject', 'issuer'];
        
        for (const field of requiredFields) {
            if (!data[field] || data[field].trim() === '') {
                this.showNotification(`Please fill in the ${field} field`, 'warning');
                return false;
            }
        }
        
        return true;
    }

    /**
     * Parse certificate files
     */
    async parseCertificateFiles(files) {
        const certificates = [];
        
        for (const file of files) {
            try {
                const content = await this.readFileAsText(file);
                const certificate = this.parseCertificateContent(content, file.name);
                if (certificate) {
                    certificates.push(certificate);
                }
            } catch (error) {
                console.error(`Failed to parse file ${file.name}:`, error);
            }
        }
        
        return certificates;
    }

    /**
     * Read file as text
     */
    readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (event) => resolve(event.target.result);
            reader.onerror = reject;
            reader.readAsText(file);
        });
    }

    /**
     * Parse certificate content
     */
    parseCertificateContent(content, filename) {
        // Basic PEM parsing
        if (content.includes('-----BEGIN CERTIFICATE-----')) {
            return {
                content,
                filename,
                format: 'pem'
            };
        }
        
        // Try to parse as JSON
        try {
            const json = JSON.parse(content);
            return {
                content: json,
                filename,
                format: 'json'
            };
        } catch (error) {
            // Assume it's raw certificate data
            return {
                content,
                filename,
                format: 'raw'
            };
        }
    }

    /**
     * Update statistics
     */
    updateStatistics() {
        // This would update any statistics display in the UI
        // Implementation depends on the specific UI requirements
    }

    /**
     * Clear filters
     */
    clearFilters() {
        this.currentFilters = {};
        this.searchQuery = '';
        this.currentPage = 1;
        
        // Reset form inputs
        const filterForm = this.forms.get('filter');
        if (filterForm) {
            filterForm.reset();
        }
        
        const searchForm = this.forms.get('search');
        if (searchForm) {
            searchForm.reset();
        }
        
        this.refreshCertificateList();
    }

    /**
     * Export certificate list
     */
    async exportCertificateList() {
        try {
            const storage = window.CertificateManagerModule.getStorage();
            const certificates = await storage.getCertificatesByFilter(this.currentFilters);
            
            const csv = this.convertToCSV(certificates);
            const blob = new Blob([csv], { type: 'text/csv' });
            
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = 'certificates.csv';
            link.click();
            
            this.showNotification('Certificate list exported successfully', 'success');
        } catch (error) {
            console.error('Failed to export certificate list:', error);
            this.showNotification('Failed to export certificate list', 'error');
        }
    }

    /**
     * Convert to CSV
     */
    convertToCSV(certificates) {
        const headers = ['Subject', 'Issuer', 'Serial Number', 'Status', 'Valid From', 'Valid Until'];
        const rows = certificates.map(cert => [
            cert.subject || '',
            cert.issuer || '',
            cert.serialNumber || '',
            cert.status || '',
            cert.notBefore || '',
            cert.notAfter || ''
        ]);
        
        return [headers, ...rows].map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
    }

    /**
     * Refresh UI
     */
    async refreshUI() {
        try {
            await this.refreshCertificateList();
            this.updateStatistics();
            
            // Dispatch event
            window.dispatchEvent(new CustomEvent('certificateUIRefreshed'));
        } catch (error) {
            console.error('UI refresh failed:', error);
            throw error;
        }
    }

    /**
     * Destroy the UI module
     */
    destroy() {
        this.isInitialized = false;
        
        // Clear intervals
        for (const [key, interval] of this.refreshIntervals) {
            clearInterval(interval);
        }
        this.refreshIntervals.clear();
        
        // Clear containers
        this.containers.clear();
        this.forms.clear();
        this.tables.clear();
        this.modals.clear();
        this.notifications.clear();
        this.eventListeners.clear();
        
        console.log('🧹 Certificate UI destroyed');
    }
} 