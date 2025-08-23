/**
 * Twin Performance Component
 * Handles twin performance display and updates
 */

import { showAlert } from '/static/js/shared/alerts.js';

export default class TwinPerformanceComponent {
    constructor() {
        // Authentication properties
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
        
        this.twinData = {
            twin_1: {
                id: 'twin_1',
                type: 'additive_manufacturing',
                name: 'Example AAS Additive Manufacturing',
                health_score: 77.0,
                status: 'good',
                uptime: '6d 0h 0m',
                performance_metrics: {
                    cpu_usage: 18.0,
                    memory_usage: 38.0,
                    response_time: 2.0,
                    error_rate: 1.5
                }
            },
            twin_2: {
                id: 'twin_2',
                type: 'smart_grid_substation',
                name: 'Example AAS Smart Grid Substation',
                health_score: 80.9,
                status: 'good',
                uptime: '1h 0m',
                performance_metrics: {
                    cpu_usage: 5.0,
                    memory_usage: 43.4,
                    response_time: 2.0,
                    error_rate: 0.5
                }
            },
            twin_3: {
                id: 'twin_3',
                type: 'hydrogen_filling_station',
                name: 'Example AAS Hydrogen Filling Station',
                health_score: 80.4,
                status: 'good',
                uptime: '3d 0h 0m',
                performance_metrics: {
                    cpu_usage: 18.0,
                    memory_usage: 47.2,
                    response_time: 0.1,
                    error_rate: 1.5
                }
            }
        };
        this.updateInterval = null;
    }
    
    /**
     * Wait for central authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Twin Performance: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Twin Performance: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Twin Performance: Auth system ready event received');
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
                console.warn('⚠️ Twin Performance: Timeout waiting for auth system');
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
            console.log('🔐 Twin Performance: Auth state updated', {
                isAuthenticated: this.isAuthenticated,
                user: this.currentUser?.username || 'anonymous'
            });
        } else {
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
            console.log('🔐 Twin Performance: No auth manager available');
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
        this.twinData = {};
        console.log('🧹 Twin Performance: Sensitive data cleared');
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
        console.log('🔧 Initializing Twin Performance Component...');
        
        try {
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            await this.loadTwinPerformance();
            this.setupEventListeners();
            this.startAutoRefresh();
            
            console.log('✅ Twin Performance Component initialized');
        } catch (error) {
            console.error('❌ Failed to initialize Twin Performance Component:', error);
            throw error;
        }
    }
    
    async loadTwinPerformance() {
        try {
            // Check authentication
            if (!this.isAuthenticated) {
                console.warn('⚠️ Twin Performance: User not authenticated, skipping performance load');
                return;
            }
            
            console.log('📊 Loading twin performance data...');
            
            // Simulate API call - replace with actual API call
            const response = await fetch('/api/federated-learning/twins/performance', {
                headers: this.getAuthHeaders()
            });
            if (response.ok) {
                const result = await response.json();
                if (result.status === 'success' && result.data && result.data.twins) {
                    this.twinData = result.data.twins;
                } else {
                    console.warn('⚠️ Failed to load twin performance, using default data');
                }
            } else {
                console.warn('⚠️ Failed to load twin performance, using default data');
            }
            
            this.displayTwinPerformance();
        } catch (error) {
            console.error('❌ Error loading twin performance:', error);
            // Use default data on error
            this.displayTwinPerformance();
        }
    }
    
    displayTwinPerformance() {
        const container = document.getElementById('twinPerformanceCards');
        if (!container) {
            console.warn('⚠️ Twin performance container not found');
            return;
        }
        
        container.innerHTML = '';
        
        // Ensure twinData is an array
        if (!Array.isArray(this.twinData)) {
            this.twinData = [];
        }
        
        if (this.twinData.length === 0) {
            // Display no data message
            container.innerHTML = `
                <div class="col-12">
                    <div class="text-center py-4">
                        <i class="fas fa-info-circle text-muted mb-3" style="font-size: 3rem;"></i>
                        <h5 class="text-muted">No Twin Performance Data</h5>
                        <p class="text-muted">No digital twins are currently available for performance monitoring.</p>
                    </div>
                </div>
            `;
        } else {
            this.twinData.forEach(twin => {
                const card = this.createTwinCard(twin);
                container.appendChild(card);
            });
        }
        
        console.log('📊 Twin performance display updated');
    }
    
    createTwinCard(twin) {
        const col = document.createElement('div');
        col.className = 'col-md-4 mb-3';
        
        // Ensure twin has required properties
        const twinName = twin.twin_name || twin.twin_id || 'Unknown Twin';
        const twinType = twin.twin_type || 'unknown';
        const healthScore = twin.health_score || 0;
        const federatedStatus = twin.federated_status || 'inactive';
        const contributionScore = twin.contribution_score || 0;
        const roundNumber = twin.round_number || 0;
        
        const statusColor = this.getStatusColor(federatedStatus);
        const healthColor = this.getHealthColor(healthScore);
        
        col.innerHTML = `
            <div class="card federated-card h-100">
                <div class="card-header bg-gradient-${statusColor} text-white">
                    <div class="d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">
                            <i class="fas fa-microchip me-2"></i>
                            ${twinName}
                        </h6>
                        <span class="badge bg-light text-dark">${twinType.replace('_', ' ')}</span>
                    </div>
                </div>
                <div class="card-body">
                    <div class="row text-center">
                        <div class="col-6">
                            <div class="mb-2">
                                <span class="h4 fw-bold text-${healthColor}">${healthScore.toFixed(1)}%</span>
                            </div>
                            <small class="text-muted">Health Score</small>
                        </div>
                        <div class="col-6">
                            <div class="mb-2">
                                <span class="h6 fw-bold">${(contributionScore * 100).toFixed(1)}%</span>
                            </div>
                            <small class="text-muted">Contribution</small>
                        </div>
                    </div>
                    
                    <hr class="my-3">
                    
                    <div class="row">
                        <div class="col-6">
                            <small class="text-muted">Federated Status</small>
                            <div class="fw-bold text-capitalize">${federatedStatus}</div>
                        </div>
                        <div class="col-6">
                            <small class="text-muted">Round Number</small>
                            <div class="fw-bold">${roundNumber}</div>
                        </div>
                    </div>
                    
                    <div class="row mt-2">
                        <div class="col-6">
                            <small class="text-muted">Data Quality</small>
                            <div class="fw-bold">${(twin.data_quality || 0).toFixed(1)}%</div>
                        </div>
                        <div class="col-6">
                            <small class="text-muted">Last Sync</small>
                            <div class="fw-bold small">${twin.last_sync ? new Date(twin.last_sync).toLocaleDateString() : 'Never'}</div>
                        </div>
                    </div>
                    
                    <div class="mt-3">
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">Federated Health</small>
                            <span class="badge bg-${this.getHealthColor(twin.federated_health || 'unknown')}">
                                ${twin.federated_health || 'unknown'}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        return col;
    }
    
    getStatusColor(status) {
        switch (status.toLowerCase()) {
            case 'good':
                return 'success';
            case 'warning':
                return 'warning';
            case 'error':
                return 'danger';
            default:
                return 'secondary';
        }
    }
    
    getHealthColor(healthScore) {
        if (healthScore >= 80) return 'success';
        if (healthScore >= 60) return 'warning';
        return 'danger';
    }
    
    setupEventListeners() {
        // Listen for twin performance updates from other components
        window.addEventListener('twinPerformanceUpdated', (event) => {
            this.twinData = { ...this.twinData, ...event.detail };
            this.displayTwinPerformance();
        });
        
        console.log('🔧 Twin Performance event listeners setup complete');
    }
    
    startAutoRefresh() {
        // Refresh performance data every 60 seconds
        this.updateInterval = setInterval(() => {
            this.loadTwinPerformance();
        }, 60000);
        
        console.log('🔄 Twin Performance auto-refresh started');
    }
    
    async refresh() {
        await this.loadTwinPerformance();
    }
    
    async cleanup() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
        
        console.log('🧹 Twin Performance Component cleaned up');
    }
} 