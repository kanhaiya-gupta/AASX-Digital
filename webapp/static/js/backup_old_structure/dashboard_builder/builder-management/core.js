/**
 * Dashboard Builder Core
 * Main class for dashboard builder functionality
 */

export default class DashboardBuilderCore {
    constructor() {
        this.isInitialized = false;
        this.currentDashboard = null;
        this.dashboards = [];
        this.config = {
            gridSize: 12,
            minWidgetWidth: 2,
            minWidgetHeight: 2,
            snapToGrid: true,
            autoSave: true,
            autoSaveInterval: 30000 // 30 seconds
        };
        this.autoSaveTimer = null;
    }

    /**
     * Initialize the Dashboard Builder Core
     */
    async init() {
        console.log('🔧 Dashboard Builder Core initializing...');
        
        try {
            // Load configuration
            await this.loadConfiguration();
            
            // Load existing dashboards
            await this.loadDashboards();
            
            // Set up auto-save if enabled
            if (this.config.autoSave) {
                this.setupAutoSave();
            }
            
            this.isInitialized = true;
            console.log('✅ Dashboard Builder Core initialized');
            
        } catch (error) {
            console.error('❌ Dashboard Builder Core initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load dashboard configuration
     */
    async loadConfiguration() {
        try {
            const response = await fetch('/api/dashboard-builder/config');
            if (response.ok) {
                const config = await response.json();
                this.config = { ...this.config, ...config };
            }
        } catch (error) {
            console.warn('⚠️ Could not load dashboard configuration, using defaults:', error);
        }
    }

    /**
     * Load existing dashboards
     */
    async loadDashboards() {
        try {
            const response = await fetch('/api/dashboard-builder/dashboards');
            if (response.ok) {
                this.dashboards = await response.json();
                console.log(`📊 Loaded ${this.dashboards.length} dashboards`);
            }
        } catch (error) {
            console.warn('⚠️ Could not load dashboards:', error);
            this.dashboards = [];
        }
    }

    /**
     * Create a new dashboard
     */
    async createDashboard(name, description = '', layout = 'grid') {
        const dashboard = {
            id: this.generateId(),
            name,
            description,
            layout,
            widgets: [],
            theme: 'default',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            settings: {
                gridSize: this.config.gridSize,
                snapToGrid: this.config.snapToGrid
            }
        };

        try {
            const response = await fetch('/api/dashboard-builder/dashboards', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dashboard)
            });

            if (response.ok) {
                this.dashboards.push(dashboard);
                this.currentDashboard = dashboard;
                console.log(`✅ Created dashboard: ${name}`);
                return dashboard;
            } else {
                throw new Error('Failed to create dashboard');
            }
        } catch (error) {
            console.error('❌ Error creating dashboard:', error);
            throw error;
        }
    }

    /**
     * Load a dashboard
     */
    async loadDashboard(dashboardId) {
        try {
            const response = await fetch(`/api/dashboard-builder/dashboards/${dashboardId}`);
            if (response.ok) {
                this.currentDashboard = await response.json();
                console.log(`📊 Loaded dashboard: ${this.currentDashboard.name}`);
                return this.currentDashboard;
            } else {
                throw new Error('Dashboard not found');
            }
        } catch (error) {
            console.error('❌ Error loading dashboard:', error);
            throw error;
        }
    }

    /**
     * Save current dashboard
     */
    async saveDashboard() {
        if (!this.currentDashboard) {
            console.warn('⚠️ No dashboard to save');
            return;
        }

        try {
            this.currentDashboard.updatedAt = new Date().toISOString();
            
            const response = await fetch(`/api/dashboard-builder/dashboards/${this.currentDashboard.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.currentDashboard)
            });

            if (response.ok) {
                console.log(`💾 Saved dashboard: ${this.currentDashboard.name}`);
                return true;
            } else {
                throw new Error('Failed to save dashboard');
            }
        } catch (error) {
            console.error('❌ Error saving dashboard:', error);
            throw error;
        }
    }

    /**
     * Delete a dashboard
     */
    async deleteDashboard(dashboardId) {
        try {
            const response = await fetch(`/api/dashboard-builder/dashboards/${dashboardId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.dashboards = this.dashboards.filter(d => d.id !== dashboardId);
                if (this.currentDashboard && this.currentDashboard.id === dashboardId) {
                    this.currentDashboard = null;
                }
                console.log(`🗑️ Deleted dashboard: ${dashboardId}`);
                return true;
            } else {
                throw new Error('Failed to delete dashboard');
            }
        } catch (error) {
            console.error('❌ Error deleting dashboard:', error);
            throw error;
        }
    }

    /**
     * Add widget to current dashboard
     */
    addWidget(widget) {
        if (!this.currentDashboard) {
            console.warn('⚠️ No dashboard selected');
            return false;
        }

        widget.id = this.generateId();
        widget.position = this.calculateWidgetPosition(widget);
        widget.createdAt = new Date().toISOString();
        
        this.currentDashboard.widgets.push(widget);
        console.log(`➕ Added widget: ${widget.type} to dashboard`);
        
        return widget;
    }

    /**
     * Remove widget from current dashboard
     */
    removeWidget(widgetId) {
        if (!this.currentDashboard) {
            console.warn('⚠️ No dashboard selected');
            return false;
        }

        this.currentDashboard.widgets = this.currentDashboard.widgets.filter(w => w.id !== widgetId);
        console.log(`➖ Removed widget: ${widgetId} from dashboard`);
        
        return true;
    }

    /**
     * Update widget position
     */
    updateWidgetPosition(widgetId, x, y, width, height) {
        if (!this.currentDashboard) {
            console.warn('⚠️ No dashboard selected');
            return false;
        }

        const widget = this.currentDashboard.widgets.find(w => w.id === widgetId);
        if (widget) {
            widget.position = { x, y, width, height };
            widget.updatedAt = new Date().toISOString();
            console.log(`📍 Updated widget position: ${widgetId}`);
            return true;
        }

        return false;
    }

    /**
     * Calculate widget position based on grid
     */
    calculateWidgetPosition(widget) {
        const existingWidgets = this.currentDashboard.widgets;
        let x = 0, y = 0;
        
        // Find the next available position
        while (this.isPositionOccupied(x, y, widget.defaultWidth || 2, widget.defaultHeight || 2)) {
            x += widget.defaultWidth || 2;
            if (x + (widget.defaultWidth || 2) > this.config.gridSize) {
                x = 0;
                y += widget.defaultHeight || 2;
            }
        }

        return {
            x,
            y,
            width: widget.defaultWidth || 2,
            height: widget.defaultHeight || 2
        };
    }

    /**
     * Check if position is occupied
     */
    isPositionOccupied(x, y, width, height) {
        return this.currentDashboard.widgets.some(widget => {
            const pos = widget.position;
            return !(x + width <= pos.x || x >= pos.x + pos.width ||
                    y + height <= pos.y || y >= pos.y + pos.height);
        });
    }

    /**
     * Setup auto-save functionality
     */
    setupAutoSave() {
        if (this.autoSaveTimer) {
            clearInterval(this.autoSaveTimer);
        }

        this.autoSaveTimer = setInterval(() => {
            if (this.currentDashboard) {
                this.saveDashboard().catch(error => {
                    console.warn('⚠️ Auto-save failed:', error);
                });
            }
        }, this.config.autoSaveInterval);

        console.log(`⏰ Auto-save enabled (${this.config.autoSaveInterval / 1000}s interval)`);
    }

    /**
     * Generate unique ID
     */
    generateId() {
        return 'db_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Get current dashboard
     */
    getCurrentDashboard() {
        return this.currentDashboard;
    }

    /**
     * Get all dashboards
     */
    getAllDashboards() {
        return this.dashboards;
    }

    /**
     * Get configuration
     */
    getConfiguration() {
        return this.config;
    }

    /**
     * Update configuration
     */
    async updateConfiguration(newConfig) {
        this.config = { ...this.config, ...newConfig };
        
        try {
            const response = await fetch('/api/dashboard-builder/config', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.config)
            });

            if (response.ok) {
                console.log('✅ Configuration updated');
                
                // Restart auto-save if interval changed
                if (this.config.autoSave) {
                    this.setupAutoSave();
                }
                
                return true;
            } else {
                throw new Error('Failed to update configuration');
            }
        } catch (error) {
            console.error('❌ Error updating configuration:', error);
            throw error;
        }
    }

    /**
     * Refresh dashboard data
     */
    async refreshData() {
        await this.loadDashboards();
        console.log('🔄 Dashboard data refreshed');
    }

    /**
     * Destroy the core instance
     */
    destroy() {
        if (this.autoSaveTimer) {
            clearInterval(this.autoSaveTimer);
            this.autoSaveTimer = null;
        }
        
        this.isInitialized = false;
        this.currentDashboard = null;
        this.dashboards = [];
        
        console.log('🧹 Dashboard Builder Core destroyed');
    }
} 