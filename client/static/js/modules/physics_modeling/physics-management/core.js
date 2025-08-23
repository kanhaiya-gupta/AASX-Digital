/**
 * Physics Modeling Core Module
 * Handles core physics modeling functionality and system management
 */

export class PhysicsModelingCore {
    constructor() {
        // Authentication properties
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
        
        this.isInitialized = false;
        this.systemConfig = {
            maxSimulations: 10,
            maxPlugins: 50,
            simulationTimeout: 3600000, // 1 hour
            autoSaveInterval: 300000, // 5 minutes
            maxTwinConnections: 100
        };
        this.systemMetrics = {
            cpuUsage: 0,
            memoryUsage: 0,
            diskUsage: 0,
            networkLatency: 0
        };
        this.errorLog = [];
        this.performanceLog = [];
    }

    /**
     * Wait for central authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Physics Modeling Core: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Physics Modeling Core: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Physics Modeling Core: Auth system ready event received');
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
                console.warn('⚠️ Physics Modeling Core: Timeout waiting for auth system');
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
            console.log('🔐 Physics Modeling Core: Auth state updated', {
                isAuthenticated: this.isAuthenticated,
                user: this.currentUser?.username || 'anonymous'
            });
        } else {
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
            console.log('🔐 Physics Modeling Core: No auth manager available');
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
        this.errorLog = [];
        this.performanceLog = [];
        console.log('🧹 Physics Modeling Core: Sensitive data cleared');
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
     * Initialize the core module
     */
    async init() {
        if (this.isInitialized) return;
        
        console.log('🔐 Initializing Physics Modeling Core...');
        
        try {
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            // Load system configuration
            await this.loadSystemConfiguration();
            
            // Initialize system monitoring
            this.initializeSystemMonitoring();
            
            this.isInitialized = true;
            console.log('✅ Physics Modeling Core initialized');
            
        } catch (error) {
            console.error('❌ Physics Modeling Core initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load system configuration
     */
    async loadSystemConfiguration() {
        try {
            const response = await fetch('/api/physics-modeling/config', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const config = await response.json();
                this.systemConfig = { ...this.systemConfig, ...config };
                console.log('✅ System configuration loaded');
            }
        } catch (error) {
            console.warn('⚠️ Could not load system config, using defaults:', error);
        }
    }

    /**
     * Initialize system monitoring
     */
    initializeSystemMonitoring() {
        // Start monitoring system metrics
        setInterval(() => {
            this.updateSystemMetrics();
        }, 30000); // Update every 30 seconds
        
        console.log('📊 System monitoring initialized');
    }

    /**
     * Update system metrics
     */
    async updateSystemMetrics() {
        try {
            const response = await fetch('/api/physics-modeling/system-metrics', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const metrics = await response.json();
                this.systemMetrics = { ...this.systemMetrics, ...metrics };
            }
        } catch (error) {
            console.warn('⚠️ Could not update system metrics:', error);
        }
    }

    /**
     * Get system status
     */
    async getSystemStatus() {
        try {
            const response = await fetch('/api/physics-modeling/system-status', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                return await response.json();
            }
            
            // Fallback to local status
            return {
                status: this.systemMetrics.cpuUsage < 80 ? 'healthy' : 'warning',
                timestamp: new Date().toISOString(),
                metrics: this.systemMetrics
            };
        } catch (error) {
            console.error('❌ Error getting system status:', error);
            return {
                status: 'error',
                timestamp: new Date().toISOString(),
                error: error.message
            };
        }
    }

    /**
     * Get available digital twins
     */
    async getAvailableTwins() {
        try {
            const response = await fetch('/api/physics-modeling/twins', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                return await response.json();
            }
            
            // Fallback to mock data
            return this.getMockTwins();
        } catch (error) {
            console.error('❌ Error getting available twins:', error);
            return this.getMockTwins();
        }
    }

    /**
     * Validate simulation parameters
     */
    validateSimulationParameters(params) {
        const errors = [];
        
        if (!params.twinId) {
            errors.push('Digital twin ID is required');
        }
        
        if (!params.pluginId) {
            errors.push('Plugin ID is required');
        }
        
        if (params.duration && params.duration > this.systemConfig.simulationTimeout) {
            errors.push(`Simulation duration exceeds maximum allowed time (${this.systemConfig.simulationTimeout / 60000} minutes)`);
        }
        
        return {
            isValid: errors.length === 0,
            errors: errors
        };
    }

    /**
     * Get system configuration
     */
    getSystemConfiguration() {
        return { ...this.systemConfig };
    }

    /**
     * Update system configuration
     */
    async updateSystemConfiguration(newConfig) {
        try {
            const response = await fetch('/api/physics-modeling/config', {
                method: 'PUT',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(newConfig)
            });
            
            if (response.ok) {
                this.systemConfig = { ...this.systemConfig, ...newConfig };
                console.log('✅ System configuration updated');
                return true;
            }
            
            return false;
        } catch (error) {
            console.error('❌ Error updating system configuration:', error);
            return false;
        }
    }

    /**
     * Log error
     */
    logError(error, context) {
        const errorEntry = {
            timestamp: new Date().toISOString(),
            error: error.message || error,
            context: context,
            stack: error.stack
        };
        
        this.errorLog.push(errorEntry);
        
        // Keep only last 100 errors
        if (this.errorLog.length > 100) {
            this.errorLog = this.errorLog.slice(-100);
        }
        
        console.error('❌ Physics Modeling Core Error:', errorEntry);
    }

    /**
     * Log performance metric
     */
    logPerformanceMetric(operation, duration, metadata = {}) {
        const metric = {
            timestamp: new Date().toISOString(),
            operation: operation,
            duration: duration,
            metadata: metadata
        };
        
        this.performanceLog.push(metric);
        
        // Keep only last 1000 metrics
        if (this.performanceLog.length > 1000) {
            this.performanceLog = this.performanceLog.slice(-1000);
        }
    }

    /**
     * Get error log
     */
    getErrorLog() {
        return [...this.errorLog];
    }

    /**
     * Get performance log
     */
    getPerformanceLog() {
        return [...this.performanceLog];
    }

    /**
     * Mock data methods
     */
    getMockTwins() {
        return [
            {
                id: 'twin-001',
                name: 'Thermal System Twin',
                type: 'thermal',
                status: 'active',
                created_at: '2024-01-15T10:30:00Z',
                last_updated: '2024-01-15T14:45:00Z'
            },
            {
                id: 'twin-002',
                name: 'Structural Bridge Twin',
                type: 'structural',
                status: 'active',
                created_at: '2024-01-15T11:15:00Z',
                last_updated: '2024-01-15T14:30:00Z'
            },
            {
                id: 'twin-003',
                name: 'Fluid Dynamics Twin',
                type: 'fluid',
                status: 'active',
                created_at: '2024-01-15T12:00:00Z',
                last_updated: '2024-01-15T14:15:00Z'
            },
            {
                id: 'twin-004',
                name: 'Electromagnetic Twin',
                type: 'electromagnetic',
                status: 'active',
                created_at: '2024-01-15T12:45:00Z',
                last_updated: '2024-01-15T14:00:00Z'
            },
            {
                id: 'twin-005',
                name: 'Mechanical Assembly Twin',
                type: 'mechanical',
                status: 'active',
                created_at: '2024-01-15T13:30:00Z',
                last_updated: '2024-01-15T13:45:00Z'
            },
            {
                id: 'twin-006',
                name: 'Chemical Process Twin',
                type: 'chemical',
                status: 'active',
                created_at: '2024-01-15T14:00:00Z',
                last_updated: '2024-01-15T13:30:00Z'
            }
        ];
    }

    /**
     * Cleanup
     */
    destroy() {
        this.errorLog = [];
        this.performanceLog = [];
        this.isInitialized = false;
        console.log('🧹 Physics Modeling Core destroyed');
    }
}
