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
     * Wait for central authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Training Management: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Training Management: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Training Management: Auth system ready event received');
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
                console.warn('⚠️ Training Management: Timeout waiting for auth system');
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
            console.log('🔐 Training Management: Auth state updated', {
                isAuthenticated: this.isAuthenticated,
                user: this.currentUser?.username || 'anonymous'
            });
        } else {
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
            console.log('🔐 Training Management: No auth manager available');
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
        this.federationStatus = 'inactive';
        this.isProcessing = false;
        console.log('🧹 Training Management: Sensitive data cleared');
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
    
    async init() {
        console.log('🔧 Initializing Training Management Component...');
        
        try {
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
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