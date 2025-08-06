/**
 * Auto Refresh Management Component
 * Handles automatic data refresh for dashboards and real-time updates
 */

export class AutoRefreshManager {
    constructor() {
        this.isInitialized = false;
        this.refreshIntervals = new Map();
        this.refreshCallbacks = new Map();
    }

    /**
     * Initialize auto refresh management
     */
    async init() {
        if (this.isInitialized) return;
        
        console.log('🔄 Initializing Auto Refresh Manager...');
        
        try {
            // Set up auto-refresh for dashboard
            if (window.location.pathname === '/') {
                this.setupDashboardAutoRefresh();
            }
            
            this.isInitialized = true;
            console.log('✅ Auto Refresh Manager initialized');
            
        } catch (error) {
            console.error('❌ Auto Refresh Manager initialization failed:', error);
            throw error;
        }
    }

    /**
     * Setup auto-refresh for dashboard
     */
    setupDashboardAutoRefresh() {
        // Refresh every 30 seconds
        this.startRefresh('dashboard', 30000, () => {
            this.refreshDashboardData();
        });
    }

    /**
     * Refresh dashboard data
     */
    refreshDashboardData() {
        console.log('Refreshing dashboard data...');
        
        // Update activity feed
        this.updateActivityFeed();
        
        // Update KPI cards
        this.updateKPICards();
        
        // Update charts
        this.updateCharts();
    }

    /**
     * Update activity feed
     */
    updateActivityFeed() {
        fetch('/api/activity/latest')
            .then(response => response.json())
            .then(data => {
                console.log('Activity data updated:', data);
                // Update activity feed UI
                this.updateActivityFeedUI(data);
            })
            .catch(error => {
                console.error('Error updating activity feed:', error);
            });
    }

    /**
     * Update KPI cards
     */
    updateKPICards() {
        fetch('/api/dashboard/kpis')
            .then(response => response.json())
            .then(data => {
                console.log('KPI data updated:', data);
                // Update KPI cards UI
                this.updateKPICardsUI(data);
            })
            .catch(error => {
                console.error('Error updating KPI cards:', error);
            });
    }

    /**
     * Update charts
     */
    updateCharts() {
        fetch('/api/dashboard/charts')
            .then(response => response.json())
            .then(data => {
                console.log('Chart data updated:', data);
                // Update charts UI
                this.updateChartsUI(data);
            })
            .catch(error => {
                console.error('Error updating charts:', error);
            });
    }

    /**
     * Start refresh interval
     */
    startRefresh(name, interval, callback) {
        // Clear existing interval if any
        this.stopRefresh(name);
        
        // Store callback
        this.refreshCallbacks.set(name, callback);
        
        // Start new interval
        const intervalId = setInterval(callback, interval);
        this.refreshIntervals.set(name, intervalId);
        
        console.log(`🔄 Started refresh interval: ${name} (${interval}ms)`);
    }

    /**
     * Stop refresh interval
     */
    stopRefresh(name) {
        const intervalId = this.refreshIntervals.get(name);
        if (intervalId) {
            clearInterval(intervalId);
            this.refreshIntervals.delete(name);
            this.refreshCallbacks.delete(name);
            console.log(`⏹️ Stopped refresh interval: ${name}`);
        }
    }

    /**
     * Stop all refresh intervals
     */
    stopAllRefresh() {
        this.refreshIntervals.forEach((intervalId, name) => {
            clearInterval(intervalId);
            console.log(`⏹️ Stopped refresh interval: ${name}`);
        });
        
        this.refreshIntervals.clear();
        this.refreshCallbacks.clear();
    }

    /**
     * Get refresh status
     */
    getRefreshStatus() {
        const status = {};
        this.refreshIntervals.forEach((intervalId, name) => {
            status[name] = {
                active: true,
                callback: this.refreshCallbacks.get(name)
            };
        });
        return status;
    }

    /**
     * Update activity feed UI
     */
    updateActivityFeedUI(data) {
        const activityContainer = document.getElementById('activityFeed');
        if (activityContainer && data.activities) {
            // Update activity feed content
            activityContainer.innerHTML = data.activities.map(activity => `
                <div class="activity-item">
                    <span class="activity-time">${activity.timestamp}</span>
                    <span class="activity-text">${activity.description}</span>
                </div>
            `).join('');
        }
    }

    /**
     * Update KPI cards UI
     */
    updateKPICardsUI(data) {
        if (data.kpis) {
            data.kpis.forEach(kpi => {
                const kpiElement = document.getElementById(`kpi-${kpi.id}`);
                if (kpiElement) {
                    const valueElement = kpiElement.querySelector('.kpi-value');
                    if (valueElement) {
                        valueElement.textContent = kpi.value;
                    }
                }
            });
        }
    }

    /**
     * Update charts UI
     */
    updateChartsUI(data) {
        if (data.charts) {
            data.charts.forEach(chart => {
                const chartElement = document.getElementById(`chart-${chart.id}`);
                if (chartElement && window.Chart) {
                    // Update chart data
                    const chartInstance = Chart.getChart(chartElement);
                    if (chartInstance) {
                        chartInstance.data = chart.data;
                        chartInstance.update();
                    }
                }
            });
        }
    }

    /**
     * Cleanup auto refresh manager
     */
    destroy() {
        this.stopAllRefresh();
        this.isInitialized = false;
        console.log('🧹 Auto Refresh Manager destroyed');
    }
} 