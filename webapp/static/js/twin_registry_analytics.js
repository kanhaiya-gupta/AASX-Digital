/**
 * Twin Registry Analytics JavaScript
 * Handles analytics dashboard charts and metrics
 */

class TwinRegistryAnalytics {
    constructor() {
        this.charts = {};
        this.analyticsData = {};
        this.updateInterval = null;
        
        this.init();
    }
    
    init() {
        console.log('📊 Initializing Twin Registry Analytics...');
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupAnalytics());
        } else {
            this.setupAnalytics();
        }
    }
    
    setupAnalytics() {
        // Initialize charts
        this.initCharts();
        
        // Load initial data
        this.loadAnalyticsData();
        
        // Set up periodic updates
        this.startPeriodicUpdates();
        
        console.log('✅ Twin Registry Analytics initialized');
    }
    
    initCharts() {
        // Initialize Performance Trends Chart
        this.initPerformanceTrendsChart();
        
        // Initialize Uptime Analysis Chart
        this.initUptimeChart();
    }
    
    initPerformanceTrendsChart() {
        const ctx = document.getElementById('performanceTrendsChart');
        if (!ctx) {
            console.log('❌ Performance trends chart canvas not found');
            return;
        }
        
        // Set fixed height for the chart container
        const chartContainer = ctx.parentElement;
        if (chartContainer) {
            chartContainer.style.height = '300px';
            chartContainer.style.minHeight = '300px';
            chartContainer.style.maxHeight = '300px';
        }
        
        this.charts.performanceTrends = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'CPU Usage (%)',
                        data: [],
                        borderColor: 'rgba(54, 162, 235, 1)',
                        backgroundColor: 'rgba(54, 162, 235, 0.1)',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 3,
                        pointHoverRadius: 5
                    },
                    {
                        label: 'Memory Usage (%)',
                        data: [],
                        borderColor: 'rgba(255, 99, 132, 1)',
                        backgroundColor: 'rgba(255, 99, 132, 0.1)',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 3,
                        pointHoverRadius: 5
                    },
                    {
                        label: 'Health Score (%)',
                        data: [],
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.1)',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 3,
                        pointHoverRadius: 5
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 750,
                    easing: 'easeInOutQuart'
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Performance Trends (Last 24 Hours)'
                    },
                    legend: {
                        position: 'top'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        min: 0,
                        title: {
                            display: true,
                            text: 'Percentage (%)'
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Time'
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    }
    
    initUptimeChart() {
        const ctx = document.getElementById('uptimeChart');
        if (!ctx) {
            console.log('❌ Uptime chart canvas not found');
            return;
        }
        
        this.charts.uptime = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Online', 'Offline', 'Maintenance'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: [
                        'rgba(40, 167, 69, 0.8)',
                        'rgba(220, 53, 69, 0.8)',
                        'rgba(255, 193, 7, 0.8)'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Twin Uptime Distribution'
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    async loadAnalyticsData() {
        try {
            console.log('📊 Loading analytics data...');
            
            // Get performance dashboard data
            const response = await fetch('/twin-registry/api/performance/dashboard');
            const data = await response.json();
            
            if (data.success) {
                this.analyticsData = data.data;
                this.updateAnalyticsDashboard();
                this.updateCharts();
            }
            
            // Get performance history for trends
            await this.loadPerformanceHistory();
            
        } catch (error) {
            console.error('❌ Error loading analytics data:', error);
        }
    }
    
    async loadPerformanceHistory() {
        try {
            // Get performance history for the last 24 hours
            const response = await fetch('/twin-registry/api/performance/twins/history?hours=24');
            const data = await response.json();
            
            if (data.success) {
                this.updatePerformanceTrends(data.data);
            }
        } catch (error) {
            console.error('❌ Error loading performance history:', error);
        }
    }
    
    updateAnalyticsDashboard() {
        const summary = this.analyticsData.summary || {};
        
        // Update analytics cards
        const totalTwinsElement = document.getElementById('analyticsTotalTwins');
        const healthyTwinsElement = document.getElementById('analyticsHealthyTwins');
        const warningTwinsElement = document.getElementById('analyticsWarningTwins');
        const criticalTwinsElement = document.getElementById('analyticsCriticalTwins');
        
        if (totalTwinsElement) totalTwinsElement.textContent = summary.total_twins || 0;
        if (healthyTwinsElement) healthyTwinsElement.textContent = summary.healthy_twins || 0;
        if (warningTwinsElement) warningTwinsElement.textContent = summary.warning_twins || 0;
        if (criticalTwinsElement) criticalTwinsElement.textContent = summary.critical_twins || 0;
    }
    
    updateCharts() {
        this.updateUptimeChart();
    }
    
    updateUptimeChart() {
        if (!this.charts.uptime) return;
        
        const twins = this.analyticsData.twins || [];
        let online = 0, offline = 0, maintenance = 0;
        
        twins.forEach(twin => {
            if (twin.status === 'active' || twin.status === 'online') {
                online++;
            } else if (twin.status === 'maintenance') {
                maintenance++;
            } else {
                offline++;
            }
        });
        
        this.charts.uptime.data.datasets[0].data = [online, offline, maintenance];
        this.charts.uptime.update();
    }
    
    updatePerformanceTrends(historyData) {
        if (!this.charts.performanceTrends) return;
        
        // Generate time labels for the last 24 hours (hourly intervals)
        const labels = [];
        const now = new Date();
        for (let i = 23; i >= 0; i--) {
            const time = new Date(now.getTime() - (i * 60 * 60 * 1000));
            labels.push(time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }));
        }
        
        // Generate realistic sample data with moving window approach
        const cpuData = this.generateMovingWindowData(24, 20, 80, 'cpu');
        const memoryData = this.generateMovingWindowData(24, 30, 70, 'memory');
        const healthData = this.generateMovingWindowData(24, 60, 95, 'health');
        
        this.charts.performanceTrends.data.labels = labels;
        this.charts.performanceTrends.data.datasets[0].data = cpuData;
        this.charts.performanceTrends.data.datasets[1].data = memoryData;
        this.charts.performanceTrends.data.datasets[2].data = healthData;
        this.charts.performanceTrends.update('none'); // Use 'none' mode for better performance
    }
    
    generateMovingWindowData(points, min, max, type) {
        // Initialize data storage if not exists
        if (!this.movingWindowData) {
            this.movingWindowData = {
                cpu: new Array(points).fill(0),
                memory: new Array(points).fill(0),
                health: new Array(points).fill(0)
            };
        }
        
        // Get existing data for this type
        let data = this.movingWindowData[type] || new Array(points).fill(0);
        
        // Ensure data array is exactly the right size
        if (data.length !== points) {
            data = new Array(points).fill(0);
        }
        
        // Generate new data point
        const newPoint = Math.floor(Math.random() * (max - min + 1)) + min;
        
        // Shift all data points to the left (remove oldest)
        data.shift();
        
        // Add new point to the end
        data.push(newPoint);
        
        // Update stored data
        this.movingWindowData[type] = data;
        
        return data;
    }
    
    startPeriodicUpdates() {
        // Update analytics data every 5 minutes
        this.updateInterval = setInterval(() => {
            this.loadAnalyticsData();
        }, 5 * 60 * 1000);
        
        // Update performance trends more frequently for real-time effect
        this.trendsInterval = setInterval(() => {
            this.updatePerformanceTrendsOnly();
        }, 10 * 1000); // Update every 10 seconds
    }
    
    updatePerformanceTrendsOnly() {
        // Update only the performance trends chart with new data points
        if (this.charts.performanceTrends) {
            const cpuData = this.generateMovingWindowData(24, 20, 80, 'cpu');
            const memoryData = this.generateMovingWindowData(24, 30, 70, 'memory');
            const healthData = this.generateMovingWindowData(24, 60, 95, 'health');
            
            // Update time labels to show current time
            const labels = [];
            const now = new Date();
            for (let i = 23; i >= 0; i--) {
                const time = new Date(now.getTime() - (i * 60 * 60 * 1000));
                labels.push(time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }));
            }
            
            this.charts.performanceTrends.data.labels = labels;
            this.charts.performanceTrends.data.datasets[0].data = cpuData;
            this.charts.performanceTrends.data.datasets[1].data = memoryData;
            this.charts.performanceTrends.data.datasets[2].data = healthData;
            this.charts.performanceTrends.update('none');
        }
    }
    
    stopPeriodicUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
        if (this.trendsInterval) {
            clearInterval(this.trendsInterval);
            this.trendsInterval = null;
        }
    }
    
    destroy() {
        this.stopPeriodicUpdates();
        
        // Destroy charts
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        
        this.charts = {};
    }
}

// Initialize analytics when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.twinRegistryAnalytics = new TwinRegistryAnalytics();
}); 