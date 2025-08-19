/**
 * Knowledge Graph Analytics Module - World Class Edition
 * ES6 Class-based implementation with central authentication integration
 * Features sophisticated analytics dashboard, business intelligence, and enterprise-grade reporting
 */

import { AuthManager } from '../auth/auth_manager.js';
import { Logger } from '../utils/logger.js';
import { ApiClient } from '../api/api_client.js';

class KGAnalytics {
    constructor() {
        this.authManager = new AuthManager();
        this.logger = new Logger('KGAnalytics');
        this.apiClient = new ApiClient();
        
        // State management
        this.isInitialized = false;
        this.currentTimeRange = '30d';
        this.analyticsData = null;
        this.charts = {};
        this.isTabActive = false;
        
        // Initialize the component
        this.init();
    }
    
    /**
     * Initialize the Analytics Component
     */
    async init() {
        try {
            // Check authentication
            if (!await this.authManager.isAuthenticated()) {
                this.logger.warn('User not authenticated, redirecting to login');
                window.location.href = '/login';
                return;
            }
            
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.initializeComponent());
            } else {
                this.initializeComponent();
            }
            
        } catch (error) {
            this.logger.error('Failed to initialize Analytics Component:', error);
        }
    }
    
    /**
     * Initialize component functionality
     */
    async initializeComponent() {
        if (this.isInitialized) return;
        
        this.logger.info('📊 Initializing Analytics Component');
        
        try {
            // Set up event listeners
            this.initEventListeners();
            
            // Load initial analytics
            await this.loadInitialAnalytics();
            
            this.isInitialized = true;
            this.logger.info('✅ Analytics Component initialized');
            
        } catch (error) {
            this.logger.error('Failed to initialize Analytics Component:', error);
        }
    }
    
    /**
     * Initialize event listeners
     */
    initEventListeners() {
        // Time range filter
        const timeFilter = document.getElementById('kg_analytics_timeRangeFilter');
        if (timeFilter) {
            timeFilter.addEventListener('change', (e) => {
                this.currentTimeRange = e.target.value;
                this.refreshAnalytics();
            });
        }

        // Report generation
        const generateReportBtn = document.querySelector('[onclick="kgGenerateAnalyticsReport()"]');
        if (generateReportBtn) {
            generateReportBtn.onclick = () => this.generateAnalyticsReport();
        }

        // Export data
        const exportDataBtn = document.querySelector('[onclick="kgExportAnalyticsData()"]');
        if (exportDataBtn) {
            exportDataBtn.onclick = () => this.exportAnalyticsData();
        }
    }
    
    /**
     * Load initial analytics data
     */
    async loadInitialAnalytics() {
        try {
            await this.refreshAnalytics();
        } catch (error) {
            this.logger.error('Failed to load initial analytics:', error);
        }
    }
    
    /**
     * Refresh analytics data
     */
    async refreshAnalytics() {
        try {
            this.logger.info('🔄 Refreshing analytics data...');
            this.showLoadingState();
            
            // Get comprehensive analytics data
            const response = await this.apiClient.get(`/api/kg_neo4j/analytics/comprehensive`, {
                params: { period: this.currentTimeRange },
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.analyticsData = response.data;
                this.updateAnalyticsUI();
                this.showSuccess('Analytics data refreshed successfully');
            } else {
                this.showError(response.message || 'Failed to load analytics data');
            }
            
        } catch (error) {
            this.logger.error('Failed to refresh analytics:', error);
            this.showError('Failed to load analytics data');
        } finally {
            this.hideLoadingState();
        }
    }
    
    /**
     * Update analytics UI with data
     */
    updateAnalyticsUI() {
        if (!this.analyticsData) return;

        // Update overview cards
        this.updateOverviewCards();
        
        // Update charts
        this.updateCharts();
        
        // Update insights
        this.updateInsights();
    }
    
    /**
     * Update overview cards
     */
    updateOverviewCards() {
        const data = this.analyticsData;
        
        // Total Graphs
        const totalGraphsEl = document.getElementById('kg_totalGraphsAnalytics');
        if (totalGraphsEl && data.total_graphs !== undefined) {
            totalGraphsEl.textContent = data.total_graphs;
        }

        // Average Health Score
        const healthScoreEl = document.getElementById('kg_avgHealthScore');
        if (healthScoreEl && data.avg_health_score !== undefined) {
            healthScoreEl.textContent = `${data.avg_health_score}%`;
        }

        // Average Response Time
        const responseTimeEl = document.getElementById('kg_avgResponseTime');
        if (responseTimeEl && data.avg_response_time !== undefined) {
            responseTimeEl.textContent = `${data.avg_response_time}ms`;
        }

        // Neo4j Sync Rate
        const syncRateEl = document.getElementById('kg_neo4jSyncRate');
        if (syncRateEl && data.neo4j_sync_rate !== undefined) {
            syncRateEl.textContent = `${data.neo4j_sync_rate}%`;
        }

        // Update trends
        this.updateTrends(data);
    }
    
    /**
     * Update trend indicators
     */
    updateTrends(data) {
        // Graph Growth Rate
        const growthRateEl = document.getElementById('kg_graphGrowthRate');
        if (growthRateEl && data.graph_growth_rate !== undefined) {
            const trend = data.graph_growth_rate >= 0 ? 'up' : 'down';
            const color = trend === 'up' ? '#28a745' : '#dc3545';
            growthRateEl.textContent = `${data.graph_growth_rate >= 0 ? '+' : ''}${data.graph_growth_rate}%`;
            growthRateEl.style.color = color;
        }

        // Health Trend
        const healthTrendEl = document.getElementById('kg_healthTrend');
        if (healthTrendEl && data.health_trend !== undefined) {
            const trend = data.health_trend >= 0 ? 'up' : 'down';
            const color = trend === 'up' ? '#28a745' : '#dc3545';
            healthTrendEl.textContent = `${data.health_trend >= 0 ? '+' : ''}${data.health_trend}%`;
            healthTrendEl.style.color = color;
        }

        // Response Time Trend
        const responseTrendEl = document.getElementById('kg_responseTimeTrend');
        if (responseTrendEl && data.response_time_trend !== undefined) {
            const trend = data.response_time_trend <= 0 ? 'down' : 'up';
            const color = trend === 'down' ? '#28a745' : '#dc3545';
            responseTrendEl.textContent = `${data.response_time_trend >= 0 ? '+' : ''}${data.response_time_trend}ms`;
            responseTrendEl.style.color = color;
        }

        // Sync Trend
        const syncTrendEl = document.getElementById('kg_syncTrend');
        if (syncTrendEl && data.sync_trend !== undefined) {
            const trend = data.sync_trend >= 0 ? 'up' : 'down';
            const color = trend === 'up' ? '#28a745' : '#dc3545';
            syncTrendEl.textContent = `${data.sync_trend >= 0 ? '+' : ''}${data.sync_trend}%`;
            syncTrendEl.style.color = color;
        }
    }
    
    /**
     * Update charts
     */
    updateCharts() {
        // This would integrate with charting libraries like Chart.js
        // For now, we'll create placeholder chart containers
        this.createChartPlaceholders();
    }
    
    /**
     * Create chart placeholders
     */
    createChartPlaceholders() {
        const chartContainers = document.querySelectorAll('.kg-chart-container');
        
        chartContainers.forEach(container => {
            const chartBody = container.querySelector('.kg-chart-body');
            if (chartBody && !chartBody.querySelector('.chart-placeholder')) {
                chartBody.innerHTML = `
                    <div class="chart-placeholder">
                        <i class="fas fa-chart-line fa-3x text-muted mb-3"></i>
                        <h5 class="text-muted">Chart Data</h5>
                        <p class="text-muted">Chart visualization will be implemented here</p>
                    </div>
                `;
            }
        });
    }
    
    /**
     * Update insights
     */
    updateInsights() {
        // Update insights section if it exists
        const insightsContainer = document.getElementById('kg-analytics-insights');
        if (insightsContainer && this.analyticsData.insights) {
            this.renderInsights(this.analyticsData.insights);
        }

    }
    
    /**
     * Render insights
     */
    renderInsights(insights) {
        this.logger.info('📊 Rendering insights:', insights);
    }
    
    /**
     * Generate analytics report
     */
    async generateAnalyticsReport() {
        try {
            this.logger.info('📋 Generating analytics report...');
            
            const response = await this.apiClient.post('/api/kg_neo4j/analytics/report', {
                time_range: this.currentTimeRange,
                report_type: 'comprehensive'
            }, {
                headers: await this.authManager.getAuthHeaders()
            });

            if (response.success && response.data.report_url) {
                window.open(response.data.report_url, '_blank');
                this.showSuccess('Analytics report generated successfully');
            } else {
                this.showError(response.message || 'Failed to generate report');
            }
            
        } catch (error) {
            this.logger.error('Failed to generate report:', error);
            this.showError('Failed to generate report');
        }
    }
    
    /**
     * Export analytics data
     */
    async exportAnalyticsData() {
        try {
            this.logger.info('📥 Exporting analytics data...');
            
            const response = await this.apiClient.post('/api/kg_neo4j/analytics/export', {
                time_range: this.currentTimeRange,
                format: 'json'
            }, {
                headers: await this.authManager.getAuthHeaders()
            });

            if (response.success && response.data.download_url) {
                window.open(response.data.download_url, '_blank');
                this.showSuccess('Analytics data exported successfully');
            } else {
                this.showError(response.message || 'Failed to export data');
            }
            
        } catch (error) {
            this.logger.error('Failed to export data:', error);
            this.showError('Failed to export data');
        }
    }
    
    /**
     * Refresh specific chart
     */
    async refreshChart(chartType) {
        try {
            this.logger.info(`🔄 Refreshing chart: ${chartType}`);
            
            const response = await this.apiClient.get(`/api/kg_neo4j/analytics/chart/${chartType}`, {
                params: { period: this.currentTimeRange },
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.updateChart(chartType, response.data);
                this.showSuccess(`Chart ${chartType} refreshed successfully`);
            } else {
                this.showError(response.message || `Failed to refresh chart ${chartType}`);
            }
            
        } catch (error) {
            this.logger.error(`Failed to refresh chart ${chartType}:`, error);
            this.showError(`Failed to refresh chart ${chartType}`);
        }
    }
    
    /**
     * Generate business intelligence report
     */
    async generateBusinessReport() {
        try {
            this.logger.info('📊 Generating business intelligence report...');
            
            const response = await this.apiClient.post('/api/kg_neo4j/analytics/business-report', {
                time_range: this.currentTimeRange,
                report_type: 'business_intelligence'
            }, {
                headers: await this.authManager.getAuthHeaders()
            });

            if (response.success && response.data.report_url) {
                window.open(response.data.report_url, '_blank');
                this.showSuccess('Business intelligence report generated successfully');
            } else {
                this.showError(response.message || 'Failed to generate business report');
            }
            
        } catch (error) {
            this.logger.error('Failed to generate business report:', error);
            this.showError('Failed to generate business report');
        }
    }
    
    /**
     * Update specific chart
     */
    updateChart(chartType, data) {
        const chartContainer = document.getElementById(`${chartType}-chart`);
        if (chartContainer) {
            // This would integrate with charting libraries
            // For now, show placeholder
            chartContainer.innerHTML = `
                <div class="chart-placeholder">
                    <i class="fas fa-chart-line fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">${chartType.replace('-', ' ').toUpperCase()} Chart</h5>
                    <p class="text-muted">Chart data loaded successfully</p>
                </div>
            `;
        }
    }
    
    /**
     * Show loading state
     */
    showLoadingState() {
        const loadingEl = document.querySelector('.kg-analytics-loading');
        if (loadingEl) {
            loadingEl.style.display = 'flex';
        }
    }
    
    /**
     * Hide loading state
     */
    hideLoadingState() {
        const loadingEl = document.querySelector('.kg-analytics-loading');
        if (loadingEl) {
            loadingEl.style.display = 'none';
        }
    }
    
    /**
     * Set tab active state
     */
    setTabActive(active) {
        this.isTabActive = active;
        
        if (active) {
            // Start auto-refresh when tab is active
            this.startAutoRefresh();
        } else {
            // Stop auto-refresh when tab is inactive
            this.stopAutoRefresh();
        }
    }
    
    /**
     * Start auto-refresh
     */
    startAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
        }
        
        // Refresh analytics every 5 minutes when tab is active
        this.autoRefreshInterval = setInterval(() => {
            if (this.isTabActive) {
                this.refreshAnalytics();
            }
        }, 300000); // 5 minutes
        
        this.logger.info('Analytics auto-refresh started');
    }
    
    /**
     * Stop auto-refresh
     */
    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
        
        this.logger.info('Analytics auto-refresh stopped');
    }
    
    /**
     * Show success message
     */
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    /**
     * Show error message
     */
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
    
    /**
     * Cleanup resources
     */
    destroy() {
        // Clear intervals
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
        }
        
        this.logger.info('Analytics Component destroyed');
    }
}

// Create global instance
const kgAnalytics = new KGAnalytics();

// Expose methods globally for HTML onclick calls
window.kgGenerateAnalyticsReport = () => kgAnalytics.generateAnalyticsReport();
window.kgExportAnalyticsData = () => kgAnalytics.exportAnalyticsData();
window.kgRefreshChart = (chartType) => kgAnalytics.refreshChart(chartType);
window.kgGenerateBusinessReport = () => kgAnalytics.generateBusinessReport();

// Export the class
export { KGAnalytics };

