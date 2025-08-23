/**
 * System Services Module
 * 
 * Manages service status monitoring, health checks, and service dependency tracking
 * for the AASX-ETL platform with user-based access control.
 * 
 * Phase 6: System Monitoring & Management
 */

class SystemServices {
    constructor() {
        this.baseUrl = '/api/aasx-etl/system';
        this.isInitialized = false;
        this.systemCore = null;
        
        // Service status data
        this.serviceStatus = {};
        this.serviceHealth = {};
        this.dependencies = {};
        
        // Service definitions
        this.coreServices = {
            'aasx_etl_api': {
                name: 'AASX-ETL API',
                description: 'Core AASX-ETL processing API',
                critical: true,
                checkInterval: 30
            },
            'database': {
                name: 'Database',
                description: 'SQLite database service',
                critical: true,
                checkInterval: 15
            },
            'authentication': {
                name: 'Authentication',
                description: 'User authentication service',
                critical: true,
                checkInterval: 20
            },
            'file_storage': {
                name: 'File Storage',
                description: 'File upload and storage service',
                critical: false,
                checkInterval: 45
            }
        };
        
        // Initialize
        this.init();
    }
    
    async init() {
        try {
            console.log('🔄 System Services: Initializing...');
            
            // Wait for System Core
            await this.waitForSystemCore();
            
            // Initialize service monitoring
            this.initializeServiceMonitoring();
            
            this.isInitialized = true;
            console.log('✅ System Services: Initialized successfully');
            
        } catch (error) {
            console.error('❌ System Services: Initialization failed:', error);
        }
    }
    
    async waitForSystemCore() {
        return new Promise((resolve, reject) => {
            const maxWaitTime = 10000; // 10 seconds
            const startTime = Date.now();
            
            const checkSystemCore = () => {
                if (window.systemCore && window.systemCore.isInitialized) {
                    this.systemCore = window.systemCore;
                    resolve();
                } else if (Date.now() - startTime > maxWaitTime) {
                    reject(new Error('Timeout waiting for System Core'));
                } else {
                    setTimeout(checkSystemCore, 100);
                }
            };
            
            checkSystemCore();
        });
    }
    
    initializeServiceMonitoring() {
        try {
            // Subscribe to service status updates
            if (this.systemCore) {
                this.systemCore.onHealthUpdate((data) => {
                    if (data.services) {
                        this.updateServiceStatus(data.services);
                    }
                });
            }
            
            // Start service health checks
            this.startServiceHealthChecks();
            
            console.log('✅ System Services: Service monitoring initialized');
            
        } catch (error) {
            console.error('❌ System Services: Failed to initialize service monitoring:', error);
        }
    }
    
    startServiceHealthChecks() {
        try {
            // Check each service at its specified interval
            Object.entries(this.coreServices).forEach(([serviceId, serviceConfig]) => {
                setInterval(() => {
                    this.checkServiceHealth(serviceId);
                }, serviceConfig.checkInterval * 1000);
                
                // Initial check
                this.checkServiceHealth(serviceId);
            });
            
            console.log('✅ System Services: Service health checks started');
            
        } catch (error) {
            console.error('❌ System Services: Failed to start health checks:', error);
        }
    }
    
    async checkServiceHealth(serviceId) {
        try {
            if (!this.systemCore || !this.systemCore.isAuthenticated) {
                return;
            }
            
            const serviceConfig = this.coreServices[serviceId];
            if (!serviceConfig) {
                return;
            }
            
            // Check service health via System Core
            const serviceStatus = this.systemCore.getServiceStatus();
            if (serviceStatus && serviceStatus.services && serviceStatus.services[serviceId]) {
                this.updateServiceStatus({ [serviceId]: serviceStatus.services[serviceId] });
            }
            
        } catch (error) {
            console.error(`❌ System Services: Failed to check health for ${serviceId}:`, error);
        }
    }
    
    updateServiceStatus(services) {
        try {
            Object.entries(services).forEach(([serviceId, status]) => {
                this.serviceStatus[serviceId] = status;
                
                // Update service health
                this.updateServiceHealth(serviceId, status);
                
                // Check dependencies
                this.checkServiceDependencies(serviceId, status);
                
                // Notify listeners
                this.notifyServiceUpdate(serviceId, status);
            });
            
        } catch (error) {
            console.error('❌ System Services: Failed to update service status:', error);
        }
    }
    
    updateServiceHealth(serviceId, status) {
        try {
            const serviceConfig = this.coreServices[serviceId];
            if (!serviceConfig) {
                return;
            }
            
            // Calculate health score
            let healthScore = 100;
            let healthStatus = 'healthy';
            
            if (status.status === 'offline') {
                healthScore = 0;
                healthStatus = 'critical';
            } else if (status.status === 'critical') {
                healthScore = 25;
                healthStatus = 'critical';
            } else if (status.status === 'warning') {
                healthScore = 50;
                healthStatus = 'warning';
            } else if (status.status === 'unknown') {
                healthScore = 75;
                healthStatus = 'warning';
            }
            
            // Consider response time
            if (status.response_time) {
                if (status.response_time > 5.0) {
                    healthScore = Math.max(0, healthScore - 25);
                    if (healthScore < 50) healthStatus = 'warning';
                } else if (status.response_time > 2.0) {
                    healthScore = Math.max(0, healthScore - 10);
                }
            }
            
            this.serviceHealth[serviceId] = {
                serviceId,
                name: serviceConfig.name,
                description: serviceConfig.description,
                status: status.status,
                healthScore,
                healthStatus,
                responseTime: status.response_time,
                lastCheck: status.last_check,
                critical: serviceConfig.critical,
                timestamp: new Date().toISOString()
            };
            
        } catch (error) {
            console.error(`❌ System Services: Failed to update health for ${serviceId}:`, error);
        }
    }
    
    checkServiceDependencies(serviceId, status) {
        try {
            // Define service dependencies
            const dependencies = {
                'aasx_etl_api': ['database', 'authentication'],
                'file_storage': ['database'],
                'authentication': ['database']
            };
            
            const serviceDeps = dependencies[serviceId] || [];
            
            serviceDeps.forEach(depId => {
                const depStatus = this.serviceStatus[depId];
                if (depStatus && depStatus.status === 'offline') {
                    // Dependency is down, mark this service as degraded
                    if (this.serviceHealth[serviceId]) {
                        this.serviceHealth[serviceId].healthStatus = 'warning';
                        this.serviceHealth[serviceId].healthScore = Math.max(0, this.serviceHealth[serviceId].healthScore - 25);
                        this.serviceHealth[serviceId].dependencyIssue = `Dependency ${depId} is offline`;
                    }
                }
            });
            
        } catch (error) {
            console.error(`❌ System Services: Failed to check dependencies for ${serviceId}:`, error);
        }
    }
    
    getServiceStatus(serviceId = null) {
        try {
            if (serviceId) {
                return this.serviceStatus[serviceId] || null;
            }
            return this.serviceStatus;
        } catch (error) {
            console.error('❌ System Services: Failed to get service status:', error);
            return {};
        }
    }
    
    getServiceHealth(serviceId = null) {
        try {
            if (serviceId) {
                return this.serviceHealth[serviceId] || null;
            }
            return this.serviceHealth;
        } catch (error) {
            console.error('❌ System Services: Failed to get service health:', error);
            return {};
        }
    }
    
    getOverallSystemHealth() {
        try {
            const services = Object.values(this.serviceHealth);
            if (services.length === 0) {
                return {
                    overallStatus: 'unknown',
                    overallScore: 0,
                    healthyServices: 0,
                    totalServices: 0,
                    criticalIssues: 0
                };
            }
            
            // Calculate overall health
            const totalScore = services.reduce((sum, service) => sum + service.healthScore, 0);
            const overallScore = Math.round(totalScore / services.length);
            
            const healthyServices = services.filter(s => s.healthStatus === 'healthy').length;
            const criticalIssues = services.filter(s => s.healthStatus === 'critical').length;
            
            let overallStatus = 'healthy';
            if (criticalIssues > 0) {
                overallStatus = 'critical';
            } else if (overallScore < 80) {
                overallStatus = 'warning';
            }
            
            return {
                overallStatus,
                overallScore,
                healthyServices,
                totalServices: services.length,
                criticalIssues,
                timestamp: new Date().toISOString()
            };
            
        } catch (error) {
            console.error('❌ System Services: Failed to get overall health:', error);
            return {
                overallStatus: 'error',
                overallScore: 0,
                healthyServices: 0,
                totalServices: 0,
                criticalIssues: 0
            };
        }
    }
    
    getServiceSummary() {
        try {
            const services = Object.values(this.serviceHealth);
            const summary = {
                total: services.length,
                healthy: services.filter(s => s.healthStatus === 'healthy').length,
                warning: services.filter(s => s.healthStatus === 'warning').length,
                critical: services.filter(s => s.healthStatus === 'critical').length,
                unknown: services.filter(s => s.healthStatus === 'unknown').length,
                criticalServices: services.filter(s => s.critical && s.healthStatus === 'critical').length,
                timestamp: new Date().toISOString()
            };
            
            return summary;
            
        } catch (error) {
            console.error('❌ System Services: Failed to get service summary:', error);
            return {
                total: 0,
                healthy: 0,
                warning: 0,
                critical: 0,
                unknown: 0,
                criticalServices: 0,
                timestamp: new Date().toISOString()
            };
        }
    }
    
    getServiceTrends(hours = 24) {
        try {
            // This would typically fetch historical data from the backend
            // For now, return current status as trend
            const currentHealth = this.getOverallSystemHealth();
            
            return {
                current: currentHealth,
                trend: 'stable', // Placeholder for actual trend calculation
                period: hours,
                timestamp: new Date().toISOString()
            };
            
        } catch (error) {
            console.error('❌ System Services: Failed to get service trends:', error);
            return {
                current: null,
                trend: 'unknown',
                period: hours,
                timestamp: new Date().toISOString()
            };
        }
    }
    
    // Event handling
    onServiceUpdate(callback) {
        if (!this.serviceUpdateCallbacks) {
            this.serviceUpdateCallbacks = [];
        }
        this.serviceUpdateCallbacks.push(callback);
    }
    
    notifyServiceUpdate(serviceId, status) {
        try {
            if (this.serviceUpdateCallbacks) {
                this.serviceUpdateCallbacks.forEach(callback => {
                    try {
                        callback(serviceId, status);
                    } catch (error) {
                        console.error('❌ System Services: Service update callback error:', error);
                    }
                });
            }
        } catch (error) {
            console.error('❌ System Services: Failed to notify service update:', error);
        }
    }
    
    // Utility methods
    getServiceStatusColor(status) {
        const colors = {
            'healthy': 'success',
            'warning': 'warning',
            'critical': 'danger',
            'offline': 'secondary',
            'unknown': 'info'
        };
        return colors[status] || 'secondary';
    }
    
    getHealthStatusColor(healthStatus) {
        const colors = {
            'healthy': 'success',
            'warning': 'warning',
            'critical': 'danger',
            'unknown': 'info'
        };
        return colors[healthStatus] || 'secondary';
    }
    
    formatResponseTime(seconds) {
        if (seconds < 1) {
            return `${(seconds * 1000).toFixed(0)}ms`;
        } else {
            return `${seconds.toFixed(2)}s`;
        }
    }
    
    formatTimestamp(timestamp) {
        try {
            if (!timestamp) return 'Never';
            
            const date = new Date(timestamp);
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMs / 3600000);
            
            if (diffMins < 1) {
                return 'Just now';
            } else if (diffMins < 60) {
                return `${diffMins}m ago`;
            } else if (diffHours < 24) {
                return `${diffHours}h ago`;
            } else {
                return date.toLocaleDateString();
            }
        } catch (error) {
            return 'Unknown';
        }
    }
    
    // Service management methods
    async restartService(serviceId) {
        try {
            if (!this.systemCore || !this.systemCore.isAuthenticated) {
                throw new Error('Not authenticated');
            }
            
            const response = await fetch(`${this.baseUrl}/services/${serviceId}/restart`, {
                method: 'POST',
                headers: this.systemCore.getAuthHeaders()
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            console.log(`✅ System Services: Service ${serviceId} restart initiated`);
            return true;
            
        } catch (error) {
            console.error(`❌ System Services: Failed to restart service ${serviceId}:`, error);
            return false;
        }
    }
    
    async getServiceLogs(serviceId, hours = 24) {
        try {
            if (!this.systemCore || !this.systemCore.isAuthenticated) {
                throw new Error('Not authenticated');
            }
            
            const response = await fetch(`${this.baseUrl}/services/${serviceId}/logs?hours=${hours}`, {
                method: 'GET',
                headers: this.systemCore.getAuthHeaders()
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            return data.logs || [];
            
        } catch (error) {
            console.error(`❌ System Services: Failed to get logs for service ${serviceId}:`, error);
            return [];
        }
    }
    
    // Cleanup method
    cleanup() {
        try {
            // Clear any intervals or timers
            if (this.serviceUpdateCallbacks) {
                this.serviceUpdateCallbacks = [];
            }
            
            console.log('🧹 System Services: Cleanup completed');
            
        } catch (error) {
            console.error('❌ System Services: Cleanup failed:', error);
        }
    }
}

// Export for use in other modules
window.SystemServices = SystemServices;

