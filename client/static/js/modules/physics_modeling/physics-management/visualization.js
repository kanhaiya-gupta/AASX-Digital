/**
 * Physics Modeling Visualization Manager
 * Handles 3D visualization, charts, and data export
 */

export class VisualizationManager {
    constructor() {
        // Authentication properties
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
        
        this.isInitialized = false;
        this.activeVisualizations = [];
        this.visualizationConfig = {
            maxConcurrentVisualizations: 5,
            autoSaveInterval: 60000, // 1 minute
            defaultQuality: 'high',
            supportedFormats: ['png', 'jpg', 'svg', 'pdf', 'obj', 'stl']
        };
        this.chartTypes = [
            'line',
            'scatter',
            'surface',
            'contour',
            'vector',
            'heatmap',
            '3d-scatter'
        ];
    }

    /**
     * Wait for central authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Visualization Manager: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Visualization Manager: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Visualization Manager: Auth system ready event received');
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
                console.warn('⚠️ Visualization Manager: Timeout waiting for auth system');
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
            console.log('🔐 Visualization Manager: Auth state updated', {
                isAuthenticated: this.isAuthenticated,
                user: this.currentUser?.username || 'anonymous'
            });
        } else {
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
            console.log('🔐 Visualization Manager: No auth manager available');
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
        this.activeVisualizations = [];
        console.log('🧹 Visualization Manager: Sensitive data cleared');
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
     * Initialize the visualization manager
     */
    async init() {
        if (this.isInitialized) return;
        
        console.log('🔐 Initializing Visualization Manager...');
        
        try {
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            // Load visualization configuration
            await this.loadVisualizationConfiguration();
            
            this.isInitialized = true;
            console.log('✅ Visualization Manager initialized');
            
        } catch (error) {
            console.error('❌ Visualization Manager initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load visualization configuration
     */
    async loadVisualizationConfiguration() {
        try {
            const response = await fetch('/api/physics-modeling/visualization/config', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const config = await response.json();
                this.visualizationConfig = { ...this.visualizationConfig, ...config };
                console.log('✅ Visualization configuration loaded');
            }
        } catch (error) {
            console.warn('⚠️ Could not load visualization config, using defaults:', error);
        }
    }

    /**
     * Create 3D visualization
     */
    async create3DVisualization(simulationId, options = {}) {
        try {
            console.log(`🎨 Creating 3D visualization for simulation: ${simulationId}`);
            
            const visualization = {
                id: this.generateVisualizationId(),
                simulationId: simulationId,
                type: '3d',
                status: 'creating',
                options: {
                    quality: options.quality || this.visualizationConfig.defaultQuality,
                    format: options.format || 'webgl',
                    ...options
                },
                createdAt: new Date().toISOString()
            };
            
            // Add to active visualizations
            this.activeVisualizations.push(visualization);
            
            // Make API call to create visualization
            const response = await fetch('/api/physics-modeling/visualization/3d', {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({
                    simulationId: simulationId,
                    options: visualization.options
                })
            });
            
            if (!response.ok) {
                throw new Error(`Failed to create 3D visualization: ${response.statusText}`);
            }
            
            const result = await response.json();
            visualization.data = result.data;
            visualization.status = 'ready';
            
            console.log(`✅ 3D visualization created successfully: ${visualization.id}`);
            return visualization;
            
        } catch (error) {
            console.error(`❌ Error creating 3D visualization:`, error);
            throw error;
        }
    }

    /**
     * Create chart visualization
     */
    async createChart(simulationId, chartType, data, options = {}) {
        try {
            console.log(`📊 Creating ${chartType} chart for simulation: ${simulationId}`);
            
            if (!this.chartTypes.includes(chartType)) {
                throw new Error(`Unsupported chart type: ${chartType}`);
            }
            
            const chart = {
                id: this.generateVisualizationId(),
                simulationId: simulationId,
                type: 'chart',
                chartType: chartType,
                status: 'creating',
                data: data,
                options: {
                    responsive: true,
                    interactive: true,
                    ...options
                },
                createdAt: new Date().toISOString()
            };
            
            // Add to active visualizations
            this.activeVisualizations.push(chart);
            
            // Make API call to create chart
            const response = await fetch('/api/physics-modeling/visualization/chart', {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({
                    simulationId: simulationId,
                    chartType: chartType,
                    data: data,
                    options: chart.options
                })
            });
            
            if (!response.ok) {
                throw new Error(`Failed to create chart: ${response.statusText}`);
            }
            
            const result = await response.json();
            chart.config = result.config;
            chart.status = 'ready';
            
            console.log(`✅ Chart created successfully: ${chart.id}`);
            return chart;
            
        } catch (error) {
            console.error(`❌ Error creating chart:`, error);
            throw error;
        }
    }

    /**
     * Export visualization
     */
    async exportVisualization(visualizationId, format, options = {}) {
        try {
            console.log(`📤 Exporting visualization ${visualizationId} in ${format} format`);
            
            const visualization = this.activeVisualizations.find(v => v.id === visualizationId);
            if (!visualization) {
                throw new Error('Visualization not found');
            }
            
            if (!this.visualizationConfig.supportedFormats.includes(format)) {
                throw new Error(`Unsupported export format: ${format}`);
            }
            
            // Make API call to export visualization
            const response = await fetch(`/api/physics-modeling/visualization/${visualizationId}/export`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({
                    format: format,
                    options: options
                })
            });
            
            if (!response.ok) {
                throw new Error(`Failed to export visualization: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            // Trigger download
            this.downloadFile(result.downloadUrl, result.filename);
            
            console.log(`✅ Visualization exported successfully: ${result.filename}`);
            return result;
            
        } catch (error) {
            console.error(`❌ Error exporting visualization:`, error);
            throw error;
        }
    }

    /**
     * Update visualization
     */
    async updateVisualization(visualizationId, updates) {
        try {
            console.log(`🔄 Updating visualization: ${visualizationId}`);
            
            const visualization = this.activeVisualizations.find(v => v.id === visualizationId);
            if (!visualization) {
                throw new Error('Visualization not found');
            }
            
            // Make API call to update visualization
            const response = await fetch(`/api/physics-modeling/visualization/${visualizationId}`, {
                method: 'PUT',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(updates)
            });
            
            if (!response.ok) {
                throw new Error(`Failed to update visualization: ${response.statusText}`);
            }
            
            // Update local visualization
            Object.assign(visualization, updates);
            
            console.log(`✅ Visualization updated successfully: ${visualizationId}`);
            return visualization;
            
        } catch (error) {
            console.error(`❌ Error updating visualization:`, error);
            throw error;
        }
    }

    /**
     * Delete visualization
     */
    async deleteVisualization(visualizationId) {
        try {
            console.log(`🗑️ Deleting visualization: ${visualizationId}`);
            
            // Make API call to delete visualization
            const response = await fetch(`/api/physics-modeling/visualization/${visualizationId}`, {
                method: 'DELETE',
                headers: this.getAuthHeaders()
            });
            
            if (!response.ok) {
                throw new Error(`Failed to delete visualization: ${response.statusText}`);
            }
            
            // Remove from active visualizations
            this.activeVisualizations = this.activeVisualizations.filter(v => v.id !== visualizationId);
            
            console.log(`✅ Visualization deleted successfully: ${visualizationId}`);
            
        } catch (error) {
            console.error(`❌ Error deleting visualization:`, error);
            throw error;
        }
    }

    /**
     * Get visualization by ID
     */
    getVisualizationById(visualizationId) {
        return this.activeVisualizations.find(v => v.id === visualizationId);
    }

    /**
     * Get visualizations by simulation ID
     */
    getVisualizationsBySimulation(simulationId) {
        return this.activeVisualizations.filter(v => v.simulationId === simulationId);
    }

    /**
     * Get visualization statistics
     */
    getVisualizationStatistics() {
        const totalVisualizations = this.activeVisualizations.length;
        const byType = {};
        const byStatus = {};
        
        this.activeVisualizations.forEach(viz => {
            byType[viz.type] = (byType[viz.type] || 0) + 1;
            byStatus[viz.status] = (byStatus[viz.status] || 0) + 1;
        });
        
        return {
            total: totalVisualizations,
            byType: byType,
            byStatus: byStatus
        };
    }

    /**
     * Generate unique visualization ID
     */
    generateVisualizationId() {
        return `viz-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Download file helper
     */
    downloadFile(url, filename) {
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    /**
     * Cleanup
     */
    destroy() {
        this.activeVisualizations = [];
        this.isInitialized = false;
        console.log('🧹 Visualization Manager destroyed');
    }
}
