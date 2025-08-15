/**
 * Federated Learning UI Module
 * Handles user interface management, form handling, and UI interactions
 */

export default class FederatedLearningUI {
    constructor() {
        // Authentication properties
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
        
        this.isInitialized = false;
        this.config = {
            apiBaseUrl: '/api/federated-learning',
            containerId: 'federated-learning-container',
            theme: 'light',
            language: 'en',
            autoRefresh: true,
            refreshInterval: 30000,
            animationsEnabled: true,
            notificationsEnabled: true,
            confirmationsEnabled: true,
            chartsEnabled: true,
            realtimeUpdates: true
        };

        this.containers = new Map();
        this.forms = new Map();
        this.tables = new Map();
        this.modals = new Map();
        this.charts = new Map();
        this.refreshIntervals = new Map();
        this.chartUpdateInterval = null;
    }

    /**
     * Wait for central authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Federated Learning UI: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Federated Learning UI: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Federated Learning UI: Auth system ready event received');
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
                console.warn('⚠️ Federated Learning UI: Timeout waiting for auth system');
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
            console.log('🔐 Federated Learning UI: Auth state updated', {
                isAuthenticated: this.isAuthenticated,
                user: this.currentUser?.username || 'anonymous'
            });
        } else {
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
            console.log('🔐 Federated Learning UI: No auth manager available');
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
     * Clear sensitive data on logout
     */
    clearSensitiveData() {
        // Clear any cached data that might be user-specific
        this.containers.clear();
        this.forms.clear();
        this.tables.clear();
        this.modals.clear();
        this.charts.clear();
        console.log('🧹 Federated Learning UI: Sensitive data cleared');
    }

    /**
     * Initialize the Federated Learning UI
     */
    async init() {
        try {
            console.log('🔄 Initializing Federated Learning UI...');
            
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            await this.loadConfiguration();
            this.initializeUIComponents();
            this.setupEventListeners();
            this.initializeForms();
            this.initializeTables();
            this.initializeModals();
            
            if (this.config.chartsEnabled) {
                this.initializeCharts();
            }

            if (this.config.autoRefresh) {
                this.startAutoRefresh();
            }

            if (this.config.realtimeUpdates) {
                this.startRealtimeUpdates();
            }

            this.isInitialized = true;
            console.log('✅ Federated Learning UI initialized');

        } catch (error) {
            console.error('❌ Federated Learning UI initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load configuration from server
     */
    async loadConfiguration() {
        try {
            // Check authentication
            if (!this.isAuthenticated) {
                console.warn('⚠️ Federated Learning UI: User not authenticated, skipping configuration load');
                return;
            }
            
            const response = await fetch(`${this.config.apiBaseUrl}/ui-config`, {
                headers: this.getAuthHeaders()
            });
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
        const containers = [
            'main', 'status', 'participants', 'rounds', 'metrics', 'privacy',
            'federation-chart', 'realtime-chart', 'convergence-chart'
        ];

        containers.forEach(id => {
            const element = document.getElementById(`${id}-container`) || document.getElementById(id);
            if (element) {
                this.containers.set(id, element);
            }
        });
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Federation events
        window.addEventListener('federationCreated', (event) => {
            this.handleFederationCreated(event.detail);
        });

        window.addEventListener('federationStarted', (event) => {
            this.handleFederationStarted(event.detail);
        });

        window.addEventListener('federationStopped', (event) => {
            this.handleFederationStopped(event.detail);
        });

        window.addEventListener('participantAdded', (event) => {
            this.handleParticipantAdded(event.detail);
        });

        window.addEventListener('federatedRoundCompleted', (event) => {
            this.handleRoundCompleted(event.detail);
        });

        window.addEventListener('modelsAggregated', (event) => {
            this.handleModelsAggregated(event.detail);
        });

        window.addEventListener('privacyMetricsUpdated', (event) => {
            this.handlePrivacyMetricsUpdated(event.detail);
        });

        // Form and button events
        document.addEventListener('submit', (event) => {
            this.handleFormSubmission(event);
        });

        document.addEventListener('click', (event) => {
            this.handleButtonClick(event);
        });
    }

    /**
     * Initialize forms
     */
    initializeForms() {
        const formIds = ['federation-create-form', 'participant-add-form', 'round-config-form', 'privacy-settings-form'];
        
        formIds.forEach(id => {
            const form = document.getElementById(id);
            if (form) {
                this.forms.set(id, form);
                this.setupFormValidation(form);
            }
        });
    }

    /**
     * Initialize tables
     */
    initializeTables() {
        const tableIds = ['participant-list-table', 'round-history-table', 'privacy-events-table'];
        
        tableIds.forEach(id => {
            const table = document.getElementById(id);
            if (table) {
                this.tables.set(id, table);
                this.setupTableSorting(table);
            }
        });
    }

    /**
     * Initialize modals
     */
    initializeModals() {
        const modalIds = ['federation-details-modal', 'federation-create-modal', 'participant-add-modal', 'privacy-settings-modal'];
        
        modalIds.forEach(id => {
            const modal = document.getElementById(id);
            if (modal) {
                this.modals.set(id, modal);
                this.setupModalClose(modal);
            }
        });
    }

    /**
     * Initialize charts
     */
    initializeCharts() {
        // Federation Chart
        const federationCtx = document.getElementById('federationChart');
        if (federationCtx) {
            this.charts.federation = new Chart(federationCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Health Score',
                        data: [],
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Aggregation Rounds',
                        data: [],
                        borderColor: '#f093fb',
                        backgroundColor: 'rgba(240, 147, 251, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'top' } },
                    scales: { y: { beginAtZero: true } }
                }
            });
        }

        // Real-time Chart
        const realTimeCtx = document.getElementById('realTimeChart');
        if (realTimeCtx) {
            this.charts.realTime = new Chart(realTimeCtx, {
                type: 'bar',
                data: {
                    labels: ['Twin 1', 'Twin 2', 'Twin 3'],
                    datasets: [{
                        label: 'Health Score',
                        data: [77.0, 80.9, 80.4],
                        backgroundColor: [
                            'rgba(102, 126, 234, 0.8)',
                            'rgba(240, 147, 251, 0.8)',
                            'rgba(79, 172, 254, 0.8)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'top' } },
                    scales: { y: { beginAtZero: true, max: 100 } }
                }
            });
        }

        // Convergence Chart
        const convergenceCtx = document.getElementById('convergenceChart');
        if (convergenceCtx) {
            this.charts.convergence = new Chart(convergenceCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Convergence',
                        data: [],
                        borderColor: '#4facfe',
                        backgroundColor: 'rgba(79, 172, 254, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'top' } },
                    scales: { y: { beginAtZero: true, max: 1 } }
                }
            });
        }
    }

    /**
     * Start auto-refresh
     */
    startAutoRefresh() {
        const interval = setInterval(() => {
            this.refreshFederationData();
        }, this.config.refreshInterval);

        this.refreshIntervals.set('federation', interval);
    }

    /**
     * Start real-time updates
     */
    startRealtimeUpdates() {
        this.chartUpdateInterval = setInterval(() => {
            this.updateCharts();
        }, 5000);
    }

    /**
     * Handle federation created event
     */
    handleFederationCreated(detail) {
        const { federation } = detail;
        this.updateFederationStatus(federation);
        this.showNotification('Federation created successfully', 'success');
        this.closeModal('create');
        this.updateCharts();
    }

    /**
     * Handle federation started event
     */
    handleFederationStarted(detail) {
        const { federationId } = detail;
        this.updateFederationStatus({ id: federationId, status: 'active' });
        this.showNotification('Federation started successfully', 'success');
        this.updateCharts();
    }

    /**
     * Handle federation stopped event
     */
    handleFederationStopped(detail) {
        const { federationId } = detail;
        this.updateFederationStatus({ id: federationId, status: 'inactive' });
        this.showNotification('Federation stopped successfully', 'success');
        this.updateCharts();
    }

    /**
     * Handle participant added event
     */
    handleParticipantAdded(detail) {
        const { participant } = detail;
        this.addParticipantToTable(participant);
        this.showNotification('Participant added successfully', 'success');
        this.closeModal('participant');
        this.updateCharts();
    }

    /**
     * Handle round completed event
     */
    handleRoundCompleted(detail) {
        const { round } = detail;
        this.addRoundToTable(round);
        this.updateCharts();
        this.showNotification(`Round ${round.roundNumber} completed`, 'info');
    }

    /**
     * Handle models aggregated event
     */
    handleModelsAggregated(detail) {
        const { algorithm, convergence } = detail;
        this.updateConvergenceChart(convergence);
        this.showNotification(`Models aggregated using ${algorithm}`, 'success');
    }

    /**
     * Handle privacy metrics updated event
     */
    handlePrivacyMetricsUpdated(detail) {
        const { metrics } = detail;
        this.updatePrivacyDisplay(metrics);
    }

    /**
     * Handle form submission
     */
    handleFormSubmission(event) {
        const form = event.target;
        const formId = form.id;

        event.preventDefault();

        switch (formId) {
            case 'federation-create-form':
                this.handleCreateFormSubmission(form);
                break;
            case 'participant-add-form':
                this.handleParticipantFormSubmission(form);
                break;
            case 'round-config-form':
                this.handleRoundFormSubmission(form);
                break;
            case 'privacy-settings-form':
                this.handlePrivacyFormSubmission(form);
                break;
        }
    }

    /**
     * Handle create form submission
     */
    async handleCreateFormSubmission(form) {
        try {
            const formData = new FormData(form);
            const federationData = this.parseFormData(formData);
            
            if (!this.validateFederationData(federationData)) return;

            this.showLoadingState(form);
            const core = window.FederatedLearningModule.getCore();
            await core.createFederation(federationData);
            form.reset();
            this.hideLoadingState(form);

        } catch (error) {
            console.error('Create form submission failed:', error);
            this.showNotification('Failed to create federation', 'error');
            this.hideLoadingState(form);
        }
    }

    /**
     * Handle participant form submission
     */
    async handleParticipantFormSubmission(form) {
        try {
            const formData = new FormData(form);
            const participantData = this.parseFormData(formData);
            
            if (!this.validateParticipantData(participantData)) return;

            this.showLoadingState(form);
            const core = window.FederatedLearningModule.getCore();
            await core.addParticipant(participantData.federationId, participantData);
            form.reset();
            this.hideLoadingState(form);

        } catch (error) {
            console.error('Participant form submission failed:', error);
            this.showNotification('Failed to add participant', 'error');
            this.hideLoadingState(form);
        }
    }

    /**
     * Handle round form submission
     */
    async handleRoundFormSubmission(form) {
        try {
            const formData = new FormData(form);
            const roundData = this.parseFormData(formData);
            
            if (!this.validateRoundData(roundData)) return;

            this.showLoadingState(form);
            const core = window.FederatedLearningModule.getCore();
            await core.runFederatedRound(roundData.federationId, roundData);
            form.reset();
            this.hideLoadingState(form);

        } catch (error) {
            console.error('Round form submission failed:', error);
            this.showNotification('Failed to run federated round', 'error');
            this.hideLoadingState(form);
        }
    }

    /**
     * Handle privacy form submission
     */
    async handlePrivacyFormSubmission(form) {
        try {
            const formData = new FormData(form);
            const privacyData = this.parseFormData(formData);
            
            if (!this.validatePrivacyData(privacyData)) return;

            this.showLoadingState(form);
            const privacy = window.FederatedLearningModule.getPrivacy();
            await privacy.checkPrivacyCompliance(privacyData);
            form.reset();
            this.hideLoadingState(form);

        } catch (error) {
            console.error('Privacy form submission failed:', error);
            this.showNotification('Failed to update privacy settings', 'error');
            this.hideLoadingState(form);
        }
    }

    /**
     * Handle button click
     */
    handleButtonClick(event) {
        const button = event.target;
        const action = button.dataset.action;
        const federationId = button.dataset.federationId;
        const participantId = button.dataset.participantId;

        if (!action) return;

        switch (action) {
            case 'start-federation':
                this.startFederation(federationId);
                break;
            case 'stop-federation':
                this.stopFederation(federationId);
                break;
            case 'view-federation':
                this.viewFederation(federationId);
                break;
            case 'remove-participant':
                this.removeParticipant(federationId, participantId);
                break;
            case 'run-round':
                this.runRound(federationId);
                break;
            case 'open-create-modal':
                this.openModal('create');
                break;
            case 'open-participant-modal':
                this.openModal('participant');
                break;
            case 'open-privacy-modal':
                this.openModal('privacy');
                break;
            case 'close-modal':
                this.closeModal(button.dataset.modalId);
                break;
            case 'refresh-data':
                this.refreshFederationData();
                break;
        }
    }

    /**
     * Start federation
     */
    async startFederation(federationId) {
        try {
            const core = window.FederatedLearningModule.getCore();
            await core.startFederation(federationId);
        } catch (error) {
            console.error('Failed to start federation:', error);
            this.showNotification('Failed to start federation', 'error');
        }
    }

    /**
     * Stop federation
     */
    async stopFederation(federationId) {
        try {
            const core = window.FederatedLearningModule.getCore();
            await core.stopFederation(federationId);
        } catch (error) {
            console.error('Failed to stop federation:', error);
            this.showNotification('Failed to stop federation', 'error');
        }
    }

    /**
     * View federation details
     */
    async viewFederation(federationId) {
        try {
            const core = window.FederatedLearningModule.getCore();
            const status = await core.getFederationStatus(federationId);
            const metrics = await core.getFederationMetrics(federationId);
            
            this.displayFederationDetails({ ...status, ...metrics });
            this.openModal('details');
        } catch (error) {
            console.error('Failed to view federation:', error);
            this.showNotification('Failed to load federation details', 'error');
        }
    }

    /**
     * Remove participant
     */
    async removeParticipant(federationId, participantId) {
        if (!this.config.confirmationsEnabled || this.showConfirmation('Are you sure you want to remove this participant?')) {
            try {
                const core = window.FederatedLearningModule.getCore();
                await core.removeParticipant(federationId, participantId);
            } catch (error) {
                console.error('Failed to remove participant:', error);
                this.showNotification('Failed to remove participant', 'error');
            }
        }
    }

    /**
     * Run federated round
     */
    async runRound(federationId) {
        try {
            const core = window.FederatedLearningModule.getCore();
            await core.runFederatedRound(federationId);
        } catch (error) {
            console.error('Failed to run round:', error);
            this.showNotification('Failed to run federated round', 'error');
        }
    }

    /**
     * Refresh federation data
     */
    async refreshFederationData() {
        try {
            const core = window.FederatedLearningModule.getCore();
            const status = await core.getFederationStatus();
            const metrics = await core.getFederationMetrics();
            
            this.updateFederationStatus(status);
            this.updateFederationMetrics(metrics);
            this.updateCharts();
        } catch (error) {
            console.error('Failed to refresh federation data:', error);
            this.showNotification('Failed to refresh federation data', 'error');
        }
    }

    /**
     * Update federation status display
     */
    updateFederationStatus(status) {
        const container = this.containers.get('status');
        if (!container) return;

        const statusClass = this.getStatusClass(status.status);
        
        container.innerHTML = `
            <div class="federation-status">
                <h3>Federation Status</h3>
                <div class="status-grid">
                    <div class="status-item">
                        <label>Status:</label>
                        <span class="status-badge ${statusClass}">${status.status}</span>
                    </div>
                    <div class="status-item">
                        <label>Algorithm:</label>
                        <span>${status.algorithm || 'N/A'}</span>
                    </div>
                    <div class="status-item">
                        <label>Current Round:</label>
                        <span>${status.currentRound || 0}</span>
                    </div>
                    <div class="status-item">
                        <label>Total Rounds:</label>
                        <span>${status.totalRounds || 0}</span>
                    </div>
                    <div class="status-item">
                        <label>Participants:</label>
                        <span>${status.participants ? status.participants.size : 0}</span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Update federation metrics display
     */
    updateFederationMetrics(metrics) {
        const container = this.containers.get('metrics');
        if (!container) return;

        container.innerHTML = `
            <div class="federation-metrics">
                <h3>Federation Metrics</h3>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <label>Accuracy:</label>
                        <span>${(metrics.accuracy * 100).toFixed(2)}%</span>
                    </div>
                    <div class="metric-item">
                        <label>Loss:</label>
                        <span>${metrics.loss.toFixed(4)}</span>
                    </div>
                    <div class="metric-item">
                        <label>Convergence:</label>
                        <span>${(metrics.convergence * 100).toFixed(2)}%</span>
                    </div>
                    <div class="metric-item">
                        <label>Communication Cost:</label>
                        <span>${metrics.communicationCost.toFixed(2)}</span>
                    </div>
                    <div class="metric-item">
                        <label>Privacy Level:</label>
                        <span>${(metrics.privacyLevel * 100).toFixed(2)}%</span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Update privacy display
     */
    updatePrivacyDisplay(metrics) {
        const container = this.containers.get('privacy');
        if (!container) return;

        container.innerHTML = `
            <div class="privacy-metrics">
                <h3>Privacy Metrics</h3>
                <div class="privacy-grid">
                    <div class="privacy-item">
                        <label>Differential Privacy:</label>
                        <span>${metrics.differentialPrivacy ? 'Enabled' : 'Disabled'}</span>
                    </div>
                    <div class="privacy-item">
                        <label>Secure Aggregation:</label>
                        <span>${metrics.secureAggregation ? 'Enabled' : 'Disabled'}</span>
                    </div>
                    <div class="privacy-item">
                        <label>Encryption:</label>
                        <span>${metrics.encryption ? 'Enabled' : 'Disabled'}</span>
                    </div>
                    <div class="privacy-item">
                        <label>Anonymization:</label>
                        <span>${metrics.anonymization ? 'Enabled' : 'Disabled'}</span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Update charts
     */
    async updateCharts() {
        try {
            if (this.charts.federation) {
                const core = window.FederatedLearningModule.getCore();
                const status = await core.getFederationStatus();
                const metrics = await core.getFederationMetrics();
                this.updateFederationChart(status, metrics);
            }

            if (this.charts.convergence) {
                const aggregator = window.FederatedLearningModule.getAggregator();
                const convergenceHistory = aggregator.getConvergenceHistory();
                this.updateConvergenceChart(convergenceHistory);
            }
        } catch (error) {
            console.error('Failed to update charts:', error);
        }
    }

    /**
     * Update federation chart
     */
    updateFederationChart(status, metrics) {
        const chart = this.charts.federation;
        if (!chart) return;

        const now = new Date().toLocaleTimeString();
        
        chart.data.labels.push(now);
        chart.data.datasets[0].data.push(metrics.accuracy * 100);
        chart.data.datasets[1].data.push(status.currentRound);

        if (chart.data.labels.length > 20) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
            chart.data.datasets[1].data.shift();
        }

        chart.update();
    }

    /**
     * Update convergence chart
     */
    updateConvergenceChart(convergenceHistory) {
        const chart = this.charts.convergence;
        if (!chart) return;

        const labels = convergenceHistory.map(item => `Round ${item.round}`);
        const data = convergenceHistory.map(item => item.convergence);

        chart.data.labels = labels;
        chart.data.datasets[0].data = data;
        chart.update();
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

        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);

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
                const currentDirection = this.currentSort?.direction;
                
                this.currentSort = {
                    field,
                    direction: currentDirection === 'asc' ? 'desc' : 'asc'
                };
                
                this.refreshTableData(table);
            });
        });
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
     * Validate federation data
     */
    validateFederationData(data) {
        const requiredFields = ['name', 'algorithm'];
        
        for (const field of requiredFields) {
            if (!data[field] || data[field].trim() === '') {
                this.showNotification(`Please fill in the ${field} field`, 'warning');
                return false;
            }
        }
        
        return true;
    }

    /**
     * Validate participant data
     */
    validateParticipantData(data) {
        const requiredFields = ['federationId', 'name'];
        
        for (const field of requiredFields) {
            if (!data[field] || data[field].trim() === '') {
                this.showNotification(`Please fill in the ${field} field`, 'warning');
                return false;
            }
        }
        
        return true;
    }

    /**
     * Validate round data
     */
    validateRoundData(data) {
        const requiredFields = ['federationId'];
        
        for (const field of requiredFields) {
            if (!data[field] || data[field].trim() === '') {
                this.showNotification(`Please fill in the ${field} field`, 'warning');
                return false;
            }
        }
        
        return true;
    }

    /**
     * Validate privacy data
     */
    validatePrivacyData(data) {
        return true;
    }

    /**
     * Get status class
     */
    getStatusClass(status) {
        switch (status) {
            case 'active': return 'status-active';
            case 'inactive': return 'status-inactive';
            case 'paused': return 'status-paused';
            case 'completed': return 'status-completed';
            case 'failed': return 'status-failed';
            default: return 'status-unknown';
        }
    }

    /**
     * Add participant to table
     */
    addParticipantToTable(participant) {
        // Implementation for adding participant to table
    }

    /**
     * Add round to table
     */
    addRoundToTable(round) {
        // Implementation for adding round to table
    }

    /**
     * Display federation details
     */
    displayFederationDetails(details) {
        // Implementation for displaying federation details
    }

    /**
     * Refresh table data
     */
    refreshTableData(table) {
        // Implementation for refreshing table data
    }

    /**
     * Refresh UI
     */
    async refreshUI() {
        try {
            await this.refreshFederationData();
            this.updateCharts();
            
            window.dispatchEvent(new CustomEvent('federatedLearningUIRefreshed'));
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
        
        if (this.chartUpdateInterval) {
            clearInterval(this.chartUpdateInterval);
            this.chartUpdateInterval = null;
        }
        
        // Clear all data structures
        this.containers.clear();
        this.forms.clear();
        this.tables.clear();
        this.modals.clear();
        this.charts.clear();
        
        console.log('🧹 Federated Learning UI destroyed');
    }
} 