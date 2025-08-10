/**
 * Federation Status Component
 * Handles federation status display and updates
 */

import { showAlert } from '/static/js/shared/alerts.js';

export default class FederationStatusComponent {
    constructor() {
        // Authentication properties
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
        
        this.statusData = {
            federationStatus: 'inactive',
            aggregationRounds: 0,
            activeTwins: 0,
            avgHealthScore: 0
        };
        this.updateInterval = null;
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
                console.log('🔐 Federation Status: User authenticated as', this.currentUser.username);
            } else {
                this.isAuthenticated = false;
                console.log('🔐 Federation Status: User not authenticated');
            }
        } catch (error) {
            console.error('❌ Federation Status: Authentication initialization failed:', error);
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
        console.log('🔧 Initializing Federation Status Component...');
        
        try {
            // Initialize authentication
            this.initAuthentication();
            
            await this.loadFederationStatus();
            this.setupEventListeners();
            this.startAutoRefresh();
            
            console.log('✅ Federation Status Component initialized');
        } catch (error) {
            console.error('❌ Failed to initialize Federation Status Component:', error);
            throw error;
        }
    }
    
    async loadFederationStatus() {
        try {
            // Check authentication
            if (!this.isAuthenticated) {
                console.warn('⚠️ Federation Status: User not authenticated, skipping status load');
                return;
            }
            
            console.log('📊 Loading federation status...');
            
            // Get real federation status from API
            const response = await fetch('/api/federated-learning/federation/status', {
                headers: this.getAuthHeaders()
            });
            if (response.ok) {
                const result = await response.json();
                if (result.status === 'success' && result.data) {
                    const data = result.data;
                    this.statusData = {
                        federationStatus: data.status || 'inactive',
                        aggregationRounds: data.max_rounds || 0,
                        activeTwins: data.active_twins || 0,
                        avgHealthScore: data.avg_health_score || 0
                    };
                } else {
                    console.warn('⚠️ Failed to load federation status, using default data');
                }
            } else {
                console.warn('⚠️ Failed to load federation status, using default data');
            }
            
            this.updateStatusDisplay();
        } catch (error) {
            console.error('❌ Error loading federation status:', error);
            // Use default data on error
            this.updateStatusDisplay();
        }
    }
    
    updateStatusDisplay() {
        const { federationStatus, aggregationRounds, activeTwins, avgHealthScore } = this.statusData;
        
        // Update status elements
        const statusElement = document.getElementById('federationStatus');
        const roundsElement = document.getElementById('aggregationRounds');
        const twinsElement = document.getElementById('activeTwins');
        const healthElement = document.getElementById('avgHealthScore');
        
        if (statusElement) {
            statusElement.textContent = federationStatus.charAt(0).toUpperCase() + federationStatus.slice(1);
            statusElement.className = `fw-bold text-${this.getStatusColor(federationStatus)} mb-1`;
        }
        
        if (roundsElement) {
            roundsElement.textContent = aggregationRounds;
        }
        
        if (twinsElement) {
            twinsElement.textContent = activeTwins;
        }
        
        if (healthElement) {
            healthElement.textContent = `${avgHealthScore.toFixed(1)}%`;
        }
        
        console.log('📊 Federation status display updated');
    }
    
    getStatusColor(status) {
        switch (status.toLowerCase()) {
            case 'active':
                return 'success';
            case 'inactive':
                return 'danger';
            case 'starting':
            case 'stopping':
                return 'warning';
            default:
                return 'secondary';
        }
    }
    
    setupEventListeners() {
        // Listen for federation status updates from other components
        window.addEventListener('federationStatusUpdated', (event) => {
            this.statusData = { ...this.statusData, ...event.detail };
            this.updateStatusDisplay();
        });
        
        console.log('🔧 Federation Status event listeners setup complete');
    }
    
    startAutoRefresh() {
        // Refresh status every 30 seconds
        this.updateInterval = setInterval(() => {
            this.loadFederationStatus();
        }, 30000);
        
        console.log('🔄 Federation Status auto-refresh started');
    }
    
    async refresh() {
        await this.loadFederationStatus();
    }
    
    async cleanup() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
        
        console.log('🧹 Federation Status Component cleaned up');
    }
} 