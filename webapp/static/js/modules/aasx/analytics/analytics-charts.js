/**
 * Analytics Charts Manager for AASX-ETL Frontend
 * 
 * This module integrates the Analytics tab with real-time analytics data
 * from our backend APIs, replacing static placeholder values and implementing
 * interactive charts and data visualization.
 * 
 * Phase 5.2: Frontend Data Integration
 */

class AnalyticsCharts {
    constructor() {
        this.analyticsService = null;
        this.isInitialized = false;
        this.charts = new Map();
        this.currentTab = 'performance';
        this.updateInterval = null;
        this.updateFrequency = 45000; // 45 seconds (slightly different from dashboard)
    }

    /**
     * Initialize the analytics tab integration
     */
    async init() {
        if (this.isInitialized) {
            console.log('⚠️ Analytics Tab Integration already initialized, skipping...');
            return;
        }

        console.log('🔄 Analytics Tab Integration initializing...');

        try {
            // Wait for analytics API to be available
            await this.waitForAnalyticsAPI();
            
            // Initialize analytics service
            this.analyticsService = new window.AnalyticsAPI();
            await this.analyticsService.init();
            
            // Wait for analytics tab to be available in DOM
            await this.waitForAnalyticsTabDOM();
            
            // Load initial analytics data
            await this.loadAnalyticsData();
            
            // Set up tab switching
            this.setupTabSwitching();
            
            // Set up auto-refresh
            this.setupAutoRefresh();
            
            // Set up manual refresh button
            this.setupRefreshButton();
            
            this.isInitialized = true;
            console.log('✅ Analytics Tab Integration initialized successfully');
            
        } catch (error) {
            console.error('❌ Failed to initialize Analytics Tab Integration:', error);
            this.isInitialized = false;
        }
    }

    /**
     * Wait for analytics API to be available
     */
    async waitForAnalyticsAPI() {
        console.log('⏳ Analytics Charts: Waiting for AnalyticsAPI...');
        
        while (!window.AnalyticsAPI) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        console.log('✅ Analytics Charts: AnalyticsAPI available');
    }

    /**
     * Wait for analytics tab to be available in DOM
     */
    async waitForAnalyticsTabDOM() {
        console.log('⏳ Analytics Charts: Waiting for analytics tab...');
        
        while (!document.querySelector('#analytics-tab')) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        console.log('✅ Analytics Charts: Analytics tab available');
    }

    /**
     * Load and display analytics data
     */
    async loadAnalyticsData() {
        try {
            console.log('📊 Loading analytics data...');
            
            // Show loading state
            this.showLoadingState();
            
            // Load analytics overview stats
            await this.loadAnalyticsOverview();
            
            // Load chart data for current tab
            await this.loadChartData(this.currentTab);
            
            // Hide loading state
            this.hideLoadingState();
            
            console.log('✅ Analytics data loaded successfully');
            
        } catch (error) {
            console.error('❌ Failed to load analytics data:', error);
            this.hideLoadingState();
            this.showErrorState('Failed to load analytics data');
        }
    }

    /**
     * Load analytics overview statistics
     */
    async loadAnalyticsOverview() {
        try {
            // Get dashboard metrics for analytics overview
            const dashboardMetrics = await this.analyticsService.getDashboardMetrics();
            
            if (dashboardMetrics.success && dashboardMetrics.data) {
                this.updateAnalyticsOverview(dashboardMetrics.data);
            }
            
        } catch (error) {
            console.error('❌ Failed to load analytics overview:', error);
        }
    }

    /**
     * Update analytics overview cards with real data
     */
    updateAnalyticsOverview(data) {
        // Update Total Analytics
        const totalAnalyticsElement = document.getElementById('totalAnalytics');
        if (totalAnalyticsElement) {
            totalAnalyticsElement.textContent = data.total_projects || 0;
        }

        // Update Average Processing Time
        const avgProcessingTimeElement = document.getElementById('avgProcessingTime');
        if (avgProcessingTimeElement) {
            const avgTime = data.avg_processing_time || 0;
            avgProcessingTimeElement.textContent = `${avgTime.toFixed(1)}s`;
        }

        // Update Success Rate
        const successRateElement = document.getElementById('successRate');
        if (successRateElement) {
            const successRate = data.success_rate || 0;
            successRateElement.textContent = `${successRate.toFixed(1)}%`;
        }

        // Update Data Volume
        const dataVolumeElement = document.getElementById('dataVolume');
        if (dataVolumeElement) {
            const dataVolume = data.total_files || 0;
            dataVolumeElement.textContent = `${dataVolume} files`;
        }
    }

    /**
     * Load chart data for specific tab
     */
    async loadChartData(tabName) {
        try {
            console.log(`📈 Loading chart data for tab: ${tabName}`);
            
            let chartData;
            
            switch (tabName) {
                case 'performance':
                    chartData = await this.analyticsService.getPerformanceMetricsChart(30);
                    break;
                case 'trends':
                    chartData = await this.analyticsService.getProcessingTrendsChart(30);
                    break;
                case 'insights':
                    chartData = await this.analyticsService.getQualityMetricsChart(30);
                    break;
                case 'reports':
                    chartData = await this.analyticsService.getUserBehaviorChart(30);
                    break;
                default:
                    chartData = await this.analyticsService.getPerformanceMetricsChart(30);
            }
            
            if (chartData.success && chartData.data) {
                this.renderChart(tabName, chartData.data);
            }
            
        } catch (error) {
            console.error(`❌ Failed to load chart data for ${tabName}:`, error);
            this.showChartError(tabName);
        }
    }

    /**
     * Render chart for specific tab
     */
    renderChart(tabName, chartData) {
        const chartContainer = document.querySelector(`#${tabName}-chart-container`);
        if (!chartContainer) {
            console.warn(`⚠️ Chart container not found for tab: ${tabName}`);
            return;
        }

        // Clear existing chart
        if (this.charts.has(tabName)) {
            this.charts.get(tabName).destroy();
            this.charts.delete(tabName);
        }

        // Create canvas for chart
        chartContainer.innerHTML = `<canvas id="${tabName}-chart"></canvas>`;
        const canvas = document.getElementById(`${tabName}-chart`);

        if (!canvas) {
            console.error(`❌ Canvas element not found for tab: ${tabName}`);
            return;
        }

        try {
            // Create Chart.js chart
            const chart = new Chart(canvas, {
                type: this.getChartType(tabName),
                data: this.formatChartData(tabName, chartData),
                options: this.getChartOptions(tabName)
            });

            this.charts.set(tabName, chart);
            console.log(`✅ Chart rendered for tab: ${tabName}`);

        } catch (error) {
            console.error(`❌ Failed to render chart for ${tabName}:`, error);
            this.showChartError(tabName);
        }
    }

    /**
     * Get chart type for specific tab
     */
    getChartType(tabName) {
        switch (tabName) {
            case 'performance':
                return 'line';
            case 'trends':
                return 'bar';
            case 'insights':
                return 'doughnut';
            case 'reports':
                return 'radar';
            default:
                return 'line';
        }
    }

    /**
     * Format chart data for Chart.js
     */
    formatChartData(tabName, chartData) {
        // Default chart data structure
        let formattedData = {
            labels: [],
            datasets: [{
                label: 'Data',
                data: [],
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)'
            }]
        };

        // Customize based on tab and data structure
        switch (tabName) {
            case 'performance':
                if (chartData.labels && chartData.datasets) {
                    formattedData = chartData;
                }
                break;
            case 'trends':
                if (chartData.labels && chartData.datasets) {
                    formattedData = chartData;
                }
                break;
            case 'insights':
                if (chartData.labels && chartData.datasets) {
                    formattedData = chartData;
                }
                break;
            case 'reports':
                if (chartData.labels && chartData.datasets) {
                    formattedData = chartData;
                }
                break;
        }

        return formattedData;
    }

    /**
     * Get chart options for Chart.js
     */
    getChartOptions(tabName) {
        const baseOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: this.getChartTitle(tabName)
                }
            }
        };

        // Customize options based on tab
        switch (tabName) {
            case 'performance':
                baseOptions.scales = {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Performance Score'
                        }
                    }
                };
                break;
            case 'trends':
                baseOptions.scales = {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Count'
                        }
                    }
                };
                break;
        }

        return baseOptions;
    }

    /**
     * Get chart title for specific tab
     */
    getChartTitle(tabName) {
        switch (tabName) {
            case 'performance':
                return 'Performance Metrics';
            case 'trends':
                return 'Processing Trends';
            case 'insights':
                return 'Quality Insights';
            case 'reports':
                return 'User Behavior';
            default:
                return 'Analytics Data';
        }
    }

    /**
     * Show chart error state
     */
    showChartError(tabName) {
        const chartContainer = document.querySelector(`#${tabName}-chart-container`);
        if (chartContainer) {
            chartContainer.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                    <p>Failed to load chart data</p>
                    <button class="btn btn-sm btn-outline-primary" onclick="analyticsTabIntegration.loadChartData('${tabName}')">
                        <i class="fas fa-redo"></i> Retry
                    </button>
                </div>
            `;
        }
    }

    /**
     * Set up tab switching functionality
     */
    setupTabSwitching() {
        const tabButtons = document.querySelectorAll('[data-bs-target^="#analytics-"]');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', async (e) => {
                const targetId = e.target.getAttribute('data-bs-target');
                const tabName = targetId.replace('#analytics-', '');
                
                console.log(`🔄 Switching to analytics tab: ${tabName}`);
                this.currentTab = tabName;
                
                // Load chart data for the new tab
                await this.loadChartData(tabName);
            });
        });
    }

    /**
     * Show loading state
     */
    showLoadingState() {
        const analyticsStats = document.querySelectorAll('.aasx-analytics-number');
        analyticsStats.forEach(stat => {
            stat.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        });
        
        // Add loading class to analytics section
        const analyticsSection = document.querySelector('.aasx-analytics-section');
        if (analyticsSection) {
            analyticsSection.classList.add('loading');
        }
    }

    /**
     * Hide loading state
     */
    hideLoadingState() {
        // Remove loading class from analytics section
        const analyticsSection = document.querySelector('.aasx-analytics-section');
        if (analyticsSection) {
            analyticsSection.classList.remove('loading');
        }
    }

    /**
     * Show error state
     */
    showErrorState(message) {
        console.error('❌ Analytics Error:', message);
        
        // Show error in analytics stats
        const analyticsStats = document.querySelectorAll('.aasx-analytics-number');
        analyticsStats.forEach(stat => {
            stat.innerHTML = '<i class="fas fa-exclamation-triangle text-warning"></i>';
            stat.title = message;
        });
    }

    /**
     * Set up auto-refresh functionality
     */
    setupAutoRefresh() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        this.updateInterval = setInterval(async () => {
            if (this.isInitialized) {
                console.log('🔄 Auto-refreshing analytics data...');
                await this.loadAnalyticsData();
            }
        }, this.updateFrequency);
        
        console.log(`🔄 Analytics auto-refresh set to ${this.updateFrequency / 1000} seconds`);
    }

    /**
     * Set up manual refresh button
     */
    setupRefreshButton() {
        const refreshBtn = document.getElementById('refreshAnalyticsBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', async () => {
                console.log('🔄 Manual analytics refresh triggered');
                
                // Show loading state
                refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Refreshing...</span>';
                refreshBtn.disabled = true;
                
                try {
                    await this.loadAnalyticsData();
                    console.log('✅ Manual analytics refresh completed');
                } catch (error) {
                    console.error('❌ Manual analytics refresh failed:', error);
                } finally {
                    // Restore button state
                    refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> <span>Refresh</span>';
                    refreshBtn.disabled = false;
                }
            });
        }
    }

    /**
     * Refresh analytics data manually
     */
    async refreshAnalytics() {
        if (this.isInitialized) {
            await this.loadAnalyticsData();
        }
    }

    /**
     * Stop auto-refresh
     */
    stopAutoRefresh() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
            console.log('🛑 Analytics auto-refresh stopped');
        }
    }

    /**
     * Cleanup resources
     */
    destroy() {
        this.stopAutoRefresh();
        
        // Destroy all charts
        this.charts.forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts.clear();
        
        this.isInitialized = false;
        console.log('🗑️ Analytics Tab Integration destroyed');
    }
}

// Export for use in other modules
window.AnalyticsCharts = AnalyticsCharts;
