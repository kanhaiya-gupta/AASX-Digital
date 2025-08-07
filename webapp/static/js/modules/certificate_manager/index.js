/**
 * Certificate Manager - Phase 5 Frontend
 * Main entry point for certificate management interface
 * 
 * This file orchestrates all certificate manager modules and provides
 * the main initialization and coordination logic.
 */

console.log('📦 Certificate Manager index.js: Module loading started...');

// Import modules (ES6 module imports)
console.log('📦 Certificate Manager index.js: Importing certificate manager modules...');

// Import certificate management modules
import { CertificateCore } from './certificate-management/core.js';
import { DashboardManager } from './certificate-management/dashboard.js';
import { CertificateViewer } from './certificate-management/viewer.js';
import { ExportHandler } from './certificate-management/export-handler.js';

// Import UI component modules
import { StatusIndicator } from './ui-components/status-indicator.js';
import { VersionTimeline } from './ui-components/version-timeline.js';
import { ExportButtons } from './ui-components/export-buttons.js';

console.log('✅ Certificate Manager index.js: Certificate manager modules imported');

// Global state management
const CertificateManager = {
    // Core state
    state: {
        certificates: [],
        currentCertificate: null,
        filters: {
            status: 'all',
            search: '',
            dateRange: null
        },
        ui: {
            loading: false,
            error: null,
            activeModal: null
        }
    },

    // Module instances
    modules: {
        core: null,
        dashboard: null,
        viewer: null,
        exportHandler: null,
        statusIndicator: null,
        versionTimeline: null,
        exportButtons: null
    },

    // Event system
    events: {
        listeners: {},
        emit(event, data) {
            if (this.listeners[event]) {
                this.listeners[event].forEach(callback => callback(data));
            }
        },
        on(event, callback) {
            if (!this.listeners[event]) {
                this.listeners[event] = [];
            }
            this.listeners[event].push(callback);
        },
        off(event, callback) {
            if (this.listeners[event]) {
                this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
            }
        }
    },

    // Initialize the certificate manager
    async init() {
        try {
            console.log('🚀 Certificate Manager: Initializing...');
            
            // Initialize core module
            await this.initCore();
            
            // Initialize UI modules
            await this.initUIModules();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Load initial data
            await this.loadInitialData();
            
            console.log('✅ Certificate Manager: Initialized successfully');
            
        } catch (error) {
            console.error('❌ Error initializing Certificate Manager:', error);
            this.showError('Failed to initialize Certificate Manager');
        }
    },

    // Initialize core functionality
    async initCore() {
        console.log('📋 Certificate Manager: Initializing core module...');
        
        // Initialize imported modules
        this.modules.core = new CertificateCore();
        this.modules.dashboard = new DashboardManager();
        this.modules.viewer = new CertificateViewer();
        this.modules.exportHandler = new ExportHandler();
        
        console.log('✅ Certificate Manager: Core module initialized');
    },

    // Initialize UI modules
    async initUIModules() {
        console.log('🎨 Certificate Manager: Initializing UI modules...');
        
        // Initialize UI component modules
        this.modules.statusIndicator = new StatusIndicator();
        this.modules.versionTimeline = new VersionTimeline();
        this.modules.exportButtons = new ExportButtons();
        
        // Initialize UI components
        await this.modules.statusIndicator.init();
        await this.modules.versionTimeline.init();
        await this.modules.exportButtons.init();
        
        console.log('✅ Certificate Manager: UI modules initialized');
    },

    // Setup event listeners
    setupEventListeners() {
        console.log('🔗 Certificate Manager: Setting up event listeners...');
        
        // Search functionality
        const searchInput = document.getElementById('search-certificates');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.state.filters.search = e.target.value;
                this.filterCertificates();
            });
        }
        
        // Filter functionality
        document.addEventListener('click', (e) => {
            if (e.target.matches('[onclick*="filterByStatus"]')) {
                e.preventDefault();
                const status = e.target.getAttribute('onclick').match(/'([^']+)'/)[1];
                this.state.filters.status = status;
                this.filterCertificates();
            }
        });
        
        console.log('✅ Certificate Manager: Event listeners setup complete');
    },

    // Load initial data
    async loadInitialData() {
        try {
            console.log('📊 Certificate Manager: Loading initial data...');
            
            this.setLoading(true);
            
            // Load certificates using the core module
            const certificates = await this.modules.core.loadCertificates();
            this.state.certificates = certificates;
            
            // Update UI using the dashboard module
            this.modules.dashboard.updateStats(certificates);
            this.modules.dashboard.updateTable(certificates, true); // Force update for initial load
            
            this.setLoading(false);
            
            console.log('✅ Certificate Manager: Initial data loaded');
            
        } catch (error) {
            console.error('❌ Error loading initial data:', error);
            this.setLoading(false);
            this.showError('Failed to load certificate data');
        }
    },

    // View certificate details
    async viewCertificate(certificateId) {
        try {
            console.log('👁️ Certificate Manager: Viewing certificate:', certificateId);
            
            // Set the current certificate
            const certificate = this.state.certificates.find(cert => cert.certificate_id === certificateId);
            if (certificate) {
                this.state.currentCertificate = certificate;
                console.log('✅ Current certificate set:', certificate);
            } else {
                console.warn('⚠️ Certificate not found:', certificateId);
            }
            
            const result = await this.modules.viewer.loadCertificate(certificateId);
            console.log('✅ Certificate loaded for viewing:', result);
            
            // Show certificate viewer modal
            console.log('🔄 Showing certificate viewer modal...');
            this.showModal('certificateViewerModal');
            
        } catch (error) {
            console.error('❌ Error viewing certificate:', error);
            this.showError('Failed to load certificate details');
        }
    },

    // Export certificate
    async exportCertificate(certificateId) {
        try {
            console.log('📤 Certificate Manager: Exporting certificate:', certificateId);
            
            // Set the current certificate
            const certificate = this.state.certificates.find(cert => cert.certificate_id === certificateId);
            if (certificate) {
                this.state.currentCertificate = certificate;
                console.log('✅ Current certificate set for export:', certificate);
            }
            
            // Show export options modal
            console.log('🔄 Showing export options modal...');
            this.showModal('exportOptionsModal');
            
        } catch (error) {
            console.error('❌ Error exporting certificate:', error);
            this.showError('Failed to export certificate');
        }
    },

    // Show certificate actions
    showCertificateActions(certificateId) {
        console.log('⚙️ Certificate Manager: Showing actions for:', certificateId);
        
        // Set the current certificate
        const certificate = this.state.certificates.find(cert => cert.certificate_id === certificateId);
        if (certificate) {
            this.state.currentCertificate = certificate;
            console.log('✅ Current certificate set for actions:', certificate);
        } else {
            console.warn('⚠️ Certificate not found for actions:', certificateId);
        }
        
        console.log('🔄 Showing certificate actions modal...');
        this.showModal('certificateActionsModal');
    },

    // Show status indicator
    showStatusIndicator(certificateId) {
        console.log('📊 Certificate Manager: Showing status for:', certificateId);
        
        // Set the current certificate
        const certificate = this.state.certificates.find(cert => cert.certificate_id === certificateId);
        if (certificate) {
            this.state.currentCertificate = certificate;
        }
        
        this.showModal('statusIndicatorModal');
    },

    // Show version history
    showVersionHistory(certificateId) {
        console.log('📜 Certificate Manager: Showing history for:', certificateId);
        
        // Set the current certificate
        const certificate = this.state.certificates.find(cert => cert.certificate_id === certificateId);
        if (certificate) {
            this.state.currentCertificate = certificate;
        }
        
        this.showModal('versionHistoryModal');
    },

    // Set loading state
    setLoading(loading) {
        this.state.ui.loading = loading;
        const indicator = document.getElementById('loading-indicator');
        if (indicator) {
            indicator.style.display = loading ? 'flex' : 'none';
        }
    },

    // Show modal
    showModal(modalId) {
        console.log('🔄 Certificate Manager: Attempting to show modal:', modalId);
        
        const modal = document.getElementById(modalId);
        if (modal) {
            console.log('✅ Modal element found:', modal);
            console.log('🔍 Modal current display:', modal.style.display);
            console.log('🔍 Modal current classes:', modal.className);
            
            // Use Bootstrap 5 modal API
            if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                console.log('🚀 Using Bootstrap 5 Modal API');
                const bootstrapModal = new bootstrap.Modal(modal);
                bootstrapModal.show();
                console.log('✅ Bootstrap 5 modal shown');
            } else if (typeof $ !== 'undefined' && $.fn.modal) {
                console.log('🚀 Using Bootstrap 4/jQuery Modal API');
                $(modal).modal('show');
                console.log('✅ Bootstrap 4 modal shown');
            } else {
                console.log('🚀 Using fallback modal display');
                // Fallback to basic display
                modal.style.display = 'block';
                modal.classList.add('show');
                document.body.classList.add('modal-open');
                console.log('✅ Fallback modal shown');
            }
            this.state.ui.activeModal = modalId;
            console.log('✅ Modal state updated:', this.state.ui.activeModal);
        } else {
            console.error('❌ Modal element not found:', modalId);
        }
    },

    // Close modal
    closeModal() {
        if (this.state.ui.activeModal) {
            const modal = document.getElementById(this.state.ui.activeModal);
            if (modal) {
                if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                    const bootstrapModal = bootstrap.Modal.getInstance(modal);
                    if (bootstrapModal) {
                        bootstrapModal.hide();
                    }
                } else if (typeof $ !== 'undefined' && $.fn.modal) {
                    // Fallback to Bootstrap 4/jQuery
                    $(modal).modal('hide');
                } else {
                    // Fallback to basic display
                    modal.style.display = 'none';
                    modal.classList.remove('show');
                    document.body.classList.remove('modal-open');
                }
            }
            this.state.ui.activeModal = null;
        }
    },

    // Show error message
    showError(message) {
        console.error('❌ Error:', message);
        if (typeof showNotification === 'function') {
            showNotification(message, 'error');
        } else {
            alert('Error: ' + message);
        }
    },

    showSuccess(message) {
        console.log('✅ Success:', message);
        if (typeof showNotification === 'function') {
            showNotification(message, 'success');
        }
    },

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString();
        } catch (error) {
            return dateString;
        }
    },

    filterCertificates() {
        let filtered = [...this.state.certificates];
        
        // Apply search filter
        if (this.state.filters.search) {
            const searchTerm = this.state.filters.search.toLowerCase();
            filtered = filtered.filter(cert => 
                cert.certificate_id.toLowerCase().includes(searchTerm) ||
                cert.twin_name.toLowerCase().includes(searchTerm) ||
                cert.project_name.toLowerCase().includes(searchTerm)
            );
        }
        
        // Apply status filter
        if (this.state.filters.status !== 'all') {
            filtered = filtered.filter(cert => cert.status === this.state.filters.status);
        }
        
        // Update table using the dashboard module
        this.modules.dashboard.updateTable(filtered, true); // Force update for filtering
    },

    toggleSelectAll(checked) {
        const checkboxes = document.querySelectorAll('.certificate-select');
        checkboxes.forEach(checkbox => {
            checkbox.checked = checked;
        });
    },

    // Global functions for template access
    createNewCertificate() {
        console.log('Create new certificate clicked');
        this.showSuccess('Create certificate functionality will be implemented in Phase 6');
    },

    refreshDashboard() {
        console.log('Refresh dashboard clicked');
        this.loadInitialData();
    },

    exportSelected() {
        const selectedCertificates = Array.from(document.querySelectorAll('.certificate-select:checked'))
            .map(checkbox => checkbox.value);
        
        if (selectedCertificates.length === 0) {
            this.showError('Please select certificates to export');
            return;
        }
        
        console.log('Exporting selected certificates:', selectedCertificates);
        this.showSuccess(`Exporting ${selectedCertificates.length} certificates`);
    },

    bulkActions() {
        console.log('Bulk actions clicked');
        this.showSuccess('Bulk actions will be implemented in Phase 6');
    }
};

// Export the initialization function for ES6 module import
export async function initCertificateManager() {
    console.log('🚀 Certificate Manager: Starting initialization...');
    
    try {
        await CertificateManager.init();
        console.log('✅ Certificate Manager: Initialization complete');
        
        // Make CertificateManager globally available for template functions
        window.CertificateManager = CertificateManager;
        
        // Global functions for template access
        window.createNewCertificate = () => CertificateManager.createNewCertificate();
        window.refreshDashboard = () => CertificateManager.refreshDashboard();
        window.viewCertificate = (id) => CertificateManager.viewCertificate(id);
        window.exportCertificate = (id) => CertificateManager.exportCertificate(id);
        window.showCertificateActions = (id) => CertificateManager.showCertificateActions(id);
        window.exportSelected = () => CertificateManager.exportSelected();
        window.bulkActions = () => CertificateManager.bulkActions();
        window.toggleSelectAll = (checked) => CertificateManager.toggleSelectAll(checked);
        window.filterByStatus = (status) => {
            CertificateManager.state.filters.status = status;
            CertificateManager.filterCertificates();
        };
        
        return CertificateManager;
        
    } catch (error) {
        console.error('❌ Certificate Manager: Initialization failed:', error);
        throw error;
    }
}

console.log('✅ Certificate Manager index.js: Module loading complete'); 