/**
 * Training Management Component
 * Handles federation training controls and management
 */

import { showAlert } from '/static/js/shared/alerts.js';

export default class TrainingManagementComponent {
    constructor() {
        // Authentication properties
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
        
        this.federationStatus = 'inactive';
        this.isProcessing = false;
    }
    
    /**
     * Initialize authentication
     */
    initAuthentication() {
        try {
            // Check if user is authenticated
            const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
            const userData = localStorage.getItem('user_data') || sessionStorage.getItem('user_data');
            
            if (token && userData) {
                this.authToken = token;
                this.currentUser = JSON.parse(userData);
                this.isAuthenticated = true;
                console.log('🔐 Training Management: User authenticated as', this.currentUser.username);
            } else {
                this.isAuthenticated = false;
                console.log('🔐 Training Management: User not authenticated');
            }
        } catch (error) {
            console.error('❌ Training Management: Authentication initialization failed:', error);
            this.isAuthenticated = false;
        }
    }

    /**
     * Get authentication token
     */
    getAuthToken() {
        if (!this.authToken) {
            this.initAuthentication();
        }
        return this.authToken;
    }

    /**
     * Get authentication headers
     */
    getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        const token = this.getAuthToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        return headers;
    }
    
    async init() {
        console.log('🔧 Initializing Training Management Component...');
        
        try {
            // Initialize authentication
            this.initAuthentication();
            
            this.setupEventListeners();
            
            console.log('✅ Training Management Component initialized');
        } catch (error) {
            console.error('❌ Failed to initialize Training Management Component:', error);
            throw error;
        }
    }
    
    setupEventListeners() {
        // Federation control buttons
        const startButton = document.getElementById('startFederation');
        const stopButton = document.getElementById('stopFederation');
        const runCycleButton = document.getElementById('runCycle');
        
        if (startButton) {
            startButton.addEventListener('click', () => this.startFederation());
        }
        
        if (stopButton) {
            stopButton.addEventListener('click', () => this.stopFederation());
        }
        
        if (runCycleButton) {
            runCycleButton.addEventListener('click', () => this.runFederatedCycle());
        }
        
        console.log('🔧 Training Management event listeners setup complete');
    }
    
    async startFederation() {
        if (this.isProcessing) {
            showAlert('Federation operation already in progress', 'warning');
            return;
        }
        
        try {
            this.isProcessing = true;
            this.updateButtonStates();
            
            console.log('🚀 Starting federated learning federation...');
            
            const response = await fetch('/api/federated-learning/federation/start', {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({
                    auto_start_cycles: true,
                    cycle_interval: 300
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                this.federationStatus = 'active';
                
                showAlert('Federation started successfully', 'success');
                console.log('✅ Federation started:', result);
                
                // Dispatch status update event
                window.dispatchEvent(new CustomEvent('federationStatusUpdated', {
                    detail: { federationStatus: 'active' }
                }));
                
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to start federation');
            }
            
        } catch (error) {
            console.error('❌ Error starting federation:', error);
            showAlert(`Failed to start federation: ${error.message}`, 'error');
        } finally {
            this.isProcessing = false;
            this.updateButtonStates();
        }
    }
    
    async stopFederation() {
        if (this.isProcessing) {
            showAlert('Federation operation already in progress', 'warning');
            return;
        }
        
        try {
            this.isProcessing = true;
            this.updateButtonStates();
            
            console.log('🛑 Stopping federated learning federation...');
            
            const response = await fetch('/api/federated-learning/federation/stop', {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({
                    save_state: true
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                this.federationStatus = 'inactive';
                
                showAlert('Federation stopped successfully', 'success');
                console.log('✅ Federation stopped:', result);
                
                // Dispatch status update event
                window.dispatchEvent(new CustomEvent('federationStatusUpdated', {
                    detail: { federationStatus: 'inactive' }
                }));
                
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to stop federation');
            }
            
        } catch (error) {
            console.error('❌ Error stopping federation:', error);
            showAlert(`Failed to stop federation: ${error.message}`, 'error');
        } finally {
            this.isProcessing = false;
            this.updateButtonStates();
        }
    }
    
    async runFederatedCycle() {
        if (this.isProcessing) {
            showAlert('Federation operation already in progress', 'warning');
            return;
        }
        
        try {
            this.isProcessing = true;
            this.updateButtonStates();
            
            console.log('🔄 Running federated learning cycle...');
            
            const response = await fetch('/api/federated-learning/training/cycle', {
                method: 'POST',
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const result = await response.json();
                
                showAlert('Federated learning cycle completed successfully', 'success');
                console.log('✅ Federated cycle completed:', result);
                
                // Dispatch metrics update event
                window.dispatchEvent(new CustomEvent('federationMetricsUpdated', {
                    detail: result.data || {}
                }));
                
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to run federated cycle');
            }
            
        } catch (error) {
            console.error('❌ Error running federated cycle:', error);
            showAlert(`Failed to run federated cycle: ${error.message}`, 'error');
        } finally {
            this.isProcessing = false;
            this.updateButtonStates();
        }
    }
    
    updateButtonStates() {
        const startButton = document.getElementById('startFederation');
        const stopButton = document.getElementById('stopFederation');
        const runCycleButton = document.getElementById('runCycle');
        
        const isActive = this.federationStatus === 'active';
        const isDisabled = this.isProcessing;
        
        if (startButton) {
            startButton.disabled = isDisabled || isActive;
            startButton.innerHTML = isDisabled ? 
                '<i class="fas fa-spinner fa-spin me-2"></i>Starting...' : 
                '<i class="fas fa-play me-2"></i>Start Federation';
        }
        
        if (stopButton) {
            stopButton.disabled = isDisabled || !isActive;
            stopButton.innerHTML = isDisabled ? 
                '<i class="fas fa-spinner fa-spin me-2"></i>Stopping...' : 
                '<i class="fas fa-stop me-2"></i>Stop Federation';
        }
        
        if (runCycleButton) {
            runCycleButton.disabled = isDisabled || !isActive;
            runCycleButton.innerHTML = isDisabled ? 
                '<i class="fas fa-spinner fa-spin me-2"></i>Running...' : 
                '<i class="fas fa-sync me-2"></i>Run Cycle';
        }
    }
    
    async refresh() {
        // Training management doesn't need regular refresh
        // It's event-driven based on user actions
    }
    
    async cleanup() {
        // Remove event listeners if needed
        console.log('🧹 Training Management Component cleaned up');
    }
} 