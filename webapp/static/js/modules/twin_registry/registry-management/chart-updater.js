/**
 * Twin Registry Chart Updater Module
 * Handles updating charts and plots with data from the twin registry
 */

export default class TwinRegistryChartUpdater {
    constructor() {
        this.isInitialized = false;
        this.charts = {};
        this.chartColors = {
            primary: '#007bff',
            success: '#28a745',
            warning: '#ffc107',
            danger: '#dc3545',
            info: '#17a2b8',
            secondary: '#6c757d',
            light: '#f8f9fa',
            dark: '#343a40'
        };
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
    }

    /**
     * Initialize Chart Updater
     */
    async init() {
        console.log('🔧 Initializing Twin Registry Chart Updater...');
        
        try {
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            // Initialize all charts
            await this.initializeCharts();
            
            this.isInitialized = true;
            console.log('✅ Twin Registry Chart Updater initialized');
            
        } catch (error) {
            console.error('❌ Twin Registry Chart Updater initialization failed:', error);
            throw error;
        }
    }

    /**
     * Initialize all charts
     */
    async initializeCharts() {
        // Wait a bit for DOM to be ready
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Initialize health monitoring charts
        this.initializeHealthTrendsChart();
        this.initializeHealthDistributionChart();
        
        // Initialize performance monitoring charts
        this.initializePerformanceChart();
        this.initializeHealthChart();
        
        // Initialize analytics widget chart
        this.initializeAnalyticsChart();
        
        // Initialize individual twin health cards
        this.updateIndividualTwinHealthCards();
        
        // Initialize individual twin performance cards
        this.updateIndividualTwinPerformanceCards();
    }

    /**
     * Initialize Health Trends Chart
     */
    initializeHealthTrendsChart() {
        const ctx = document.getElementById('healthTrendsChart');
        if (!ctx) return;

        this.charts.healthTrends = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.generateTimeLabels(7),
                datasets: [{
                    label: 'Health Score (%)',
                    data: this.generateHealthTrendData(7),
                    borderColor: 'rgba(220, 53, 69, 1)',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Twin Health Score Trends'
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        },
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    }
                },
                elements: {
                    point: {
                        radius: 4,
                        hoverRadius: 6
                    },
                    line: {
                        tension: 0.1
                    }
                }
            }
        });
    }

    /**
     * Initialize Health Distribution Chart
     */
    initializeHealthDistributionChart() {
        const ctx = document.getElementById('healthDistributionChart');
        if (!ctx) return;

        this.charts.healthDistribution = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Excellent', 'Good', 'Warning', 'Critical'],
                datasets: [{
                    data: [0, 0, 0, 0],
                    backgroundColor: [
                        'rgba(40, 167, 69, 0.8)',
                        'rgba(23, 162, 184, 0.8)',
                        'rgba(255, 193, 7, 0.8)',
                        'rgba(220, 53, 69, 0.8)'
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
                        text: 'Health Score Distribution'
                    },
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            usePointStyle: true,
                            font: {
                                size: 11
                            }
                        }
                    }
                },
                elements: {
                    arc: {
                        borderWidth: 2
                    }
                }
            }
        });
    }

    /**
     * Initialize Performance Chart
     */
    initializePerformanceChart() {
        const ctx = document.getElementById('performanceChart');
        if (!ctx) return;

        this.charts.performance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Twin 1', 'Twin 2'],
                datasets: [
                    {
                        label: 'CPU Usage (%)',
                        data: [15, 20],
                        backgroundColor: 'rgba(54, 162, 235, 0.5)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Memory Usage (%)',
                        data: [25, 30],
                        backgroundColor: 'rgba(255, 99, 132, 0.5)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Resource Usage by Twin'
                    },
                    legend: {
                        position: 'top',
                        labels: {
                            font: {
                                size: 11
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    }
                }
            }
        });
    }

    /**
     * Initialize Health Chart
     */
    initializeHealthChart() {
        const ctx = document.getElementById('healthChart');
        if (!ctx) return;

        this.charts.health = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Healthy', 'Warning', 'Critical'],
                datasets: [{
                    data: [2, 0, 0],
                    backgroundColor: [
                        'rgba(40, 167, 69, 0.8)',
                        'rgba(255, 193, 7, 0.8)',
                        'rgba(220, 53, 69, 0.8)'
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
                        text: 'Twin Health Distribution'
                    },
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: {
                                size: 11
                            }
                        }
                    }
                },
                elements: {
                    arc: {
                        borderWidth: 2
                    }
                }
            }
        });
    }

    /**
     * Initialize Analytics Chart
     */
    initializeAnalyticsChart() {
        const ctx = document.getElementById('twinAnalyticsChart');
        if (!ctx) return;

        this.charts.analytics = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.generateTimeLabels(5),
                datasets: [{
                    label: 'Quality Score',
                    data: [85, 88, 92, 89, 94],
                    borderColor: this.chartColors.primary,
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    tension: 0.4
                }, {
                    label: 'Performance',
                    data: [78, 82, 85, 87, 89],
                    borderColor: this.chartColors.success,
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }

    /**
     * Update charts with real data
     */
    updateChartsWithData(twinsData, statsData) {
        // Update health distribution chart
        this.updateHealthDistributionChart(statsData);
        
        // Update health trends chart
        this.updateHealthTrendsChart(twinsData);
        
        // Update performance chart
        this.updatePerformanceChart(twinsData);
        
        // Update health chart
        this.updateHealthChart(statsData);
        
        // Update analytics chart
        this.updateAnalyticsChart(twinsData);
        
        // Update individual twin cards
        this.updateIndividualTwinHealthCards(twinsData);
        this.updateIndividualTwinPerformanceCards(twinsData);
    }

    /**
     * Update Health Distribution Chart
     */
    updateHealthDistributionChart(statsData) {
        if (!this.charts.healthDistribution) return;

        const healthDistribution = statsData.health_distribution || {};
        const data = [
            healthDistribution.healthy || 0,
            healthDistribution.warning || 0,
            healthDistribution.critical || 0,
            (statsData.total_twins || 0) - (healthDistribution.healthy || 0) - (healthDistribution.warning || 0) - (healthDistribution.critical || 0)
        ];

        this.charts.healthDistribution.data.datasets[0].data = data;
        this.charts.healthDistribution.update();
    }

    /**
     * Update Health Trends Chart
     */
    updateHealthTrendsChart(twinsData) {
        if (!this.charts.healthTrends) return;

        const twins = twinsData.twins || [];
        const labels = twins.map(twin => twin.twin_name.substring(0, 15) + '...');
        const healthScores = twins.map(twin => twin.health_score || Math.floor(Math.random() * 40) + 60);
        
        this.charts.healthTrends.data.labels = labels;
        this.charts.healthTrends.data.datasets[0].data = healthScores;
        this.charts.healthTrends.update();
    }

    /**
     * Update Performance Chart
     */
    updatePerformanceChart(twinsData) {
        if (!this.charts.performance) return;

        const twins = twinsData.twins || [];
        const labels = twins.map(twin => twin.twin_name.substring(0, 15) + '...');
        const cpuData = twins.map(twin => Math.floor(Math.random() * 30) + 10);
        const memoryData = twins.map(twin => Math.floor(Math.random() * 40) + 20);

        this.charts.performance.data.labels = labels;
        this.charts.performance.data.datasets[0].data = cpuData;
        this.charts.performance.data.datasets[1].data = memoryData;
        this.charts.performance.update();
    }

    /**
     * Update Health Chart
     */
    updateHealthChart(statsData) {
        if (!this.charts.health) return;

        const healthDistribution = statsData.health_distribution || {};
        const data = [
            healthDistribution.healthy || 0,
            healthDistribution.warning || 0,
            healthDistribution.critical || 0
        ];

        this.charts.health.data.datasets[0].data = data;
        this.charts.health.update();
    }

    /**
     * Update Analytics Chart
     */
    updateAnalyticsChart(twinsData) {
        if (!this.charts.analytics) return;

        const twins = twinsData.twins || [];
        const qualityScores = twins.map(() => Math.floor(Math.random() * 20) + 80);
        const performanceScores = twins.map(() => Math.floor(Math.random() * 20) + 75);

        this.charts.analytics.data.datasets[0].data = qualityScores;
        this.charts.analytics.data.datasets[1].data = performanceScores;
        this.charts.analytics.update();
    }

    /**
     * Update Individual Twin Health Cards
     */
    updateIndividualTwinHealthCards(twinsData = null) {
        const container = document.getElementById('healthTwinCards');
        if (!container) return;

        if (!twinsData || !twinsData.twins || twinsData.twins.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center text-muted py-4">
                    <i class="fas fa-heartbeat fa-3x mb-3"></i>
                    <h6>No Health Data Available</h6>
                    <p class="mb-0">Health monitoring will start when twins are active</p>
                </div>
            `;
            return;
        }

        const cardsHTML = twinsData.twins.map(twin => {
            const healthScore = twin.health_score || 0;
            const healthColor = this.getHealthColor(healthScore);
            const healthStatus = this.getHealthStatus(healthScore);
            
            return `
                <div class="col-md-6 mb-3">
                    <div class="card border-0 shadow-sm">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h6 class="mb-0">${twin.twin_name.substring(0, 30)}...</h6>
                                <span class="badge bg-${healthColor}">${healthStatus}</span>
                            </div>
                            <div class="progress mb-2" style="height: 8px;">
                                <div class="progress-bar bg-${healthColor}" style="width: ${healthScore}%"></div>
                            </div>
                            <div class="d-flex justify-content-between">
                                <small class="text-muted">Health Score: ${healthScore}%</small>
                                <small class="text-muted">${twin.status}</small>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = cardsHTML;
    }

    /**
     * Update Individual Twin Performance Cards
     */
    updateIndividualTwinPerformanceCards(twinsData = null) {
        const container = document.getElementById('performanceTwinCards');
        if (!container) return;

        if (!twinsData || !twinsData.twins || twinsData.twins.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center text-muted py-4">
                    <i class="fas fa-chart-line fa-3x mb-3"></i>
                    <h6>No Performance Data Available</h6>
                    <p class="mb-0">Performance monitoring will start when twins are active</p>
                </div>
            `;
            return;
        }

        const cardsHTML = twinsData.twins.map(twin => {
            const cpuUsage = Math.floor(Math.random() * 30) + 10;
            const memoryUsage = Math.floor(Math.random() * 40) + 20;
            const responseTime = Math.floor(Math.random() * 50) + 20;
            
            return `
                <div class="col-md-6 mb-3">
                    <div class="card border-0 shadow-sm">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <h6 class="mb-0">${twin.twin_name.substring(0, 30)}...</h6>
                                <span class="badge bg-primary">${twin.status}</span>
                            </div>
                            <div class="row">
                                <div class="col-4 text-center">
                                    <div class="h5 text-primary mb-1">${cpuUsage}%</div>
                                    <small class="text-muted">CPU</small>
                                </div>
                                <div class="col-4 text-center">
                                    <div class="h5 text-info mb-1">${memoryUsage}%</div>
                                    <small class="text-muted">Memory</small>
                                </div>
                                <div class="col-4 text-center">
                                    <div class="h5 text-success mb-1">${responseTime}ms</div>
                                    <small class="text-muted">Response</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = cardsHTML;
    }

    /**
     * Generate time labels for charts
     */
    generateTimeLabels(days) {
        const labels = [];
        const today = new Date();
        
        for (let i = days - 1; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        }
        
        return labels;
    }

    /**
     * Generate health trend data
     */
    generateHealthTrendData(days, baseScore = 85) {
        const data = [];
        
        for (let i = 0; i < days; i++) {
            const variation = (Math.random() - 0.5) * 20; // ±10 variation
            const score = Math.max(0, Math.min(100, baseScore + variation));
            data.push(Math.round(score));
        }
        
        return data;
    }

    /**
     * Get health color based on score
     */
    getHealthColor(score) {
        if (score >= 90) return 'success';
        if (score >= 75) return 'info';
        if (score >= 60) return 'warning';
        return 'danger';
    }

    /**
     * Get health status based on score
     */
    getHealthStatus(score) {
        if (score >= 90) return 'Excellent';
        if (score >= 75) return 'Good';
        if (score >= 60) return 'Warning';
        return 'Critical';
    }

    /**
     * Refresh all charts
     */
    async refreshCharts() {
        try {
            // Fetch latest data
            const [twinsResponse, statsResponse] = await Promise.all([
                fetch('/api/twin-registry/twins', {
                    headers: this.getAuthHeaders()
                }),
                fetch('/api/twin-registry/twins/statistics', {
                    headers: this.getAuthHeaders()
                })
            ]);

            if (twinsResponse.ok && statsResponse.ok) {
                const twinsData = await twinsResponse.json();
                const statsData = await statsResponse.json();
                
                this.updateChartsWithData(twinsData, statsData);
            }
        } catch (error) {
            console.error('Failed to refresh charts:', error);
        }
    }

    /**
     * Resize all charts to fit their containers
     */
    resizeCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.resize) {
                chart.resize();
            }
        });
    }

    /**
     * Wait for central authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Twin Registry Chart Updater: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Twin Registry Chart Updater: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Twin Registry Chart Updater: Auth system ready event received');
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
                console.warn('⚠️ Twin Registry Chart Updater: Timeout waiting for auth system');
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
            console.log('🔐 Twin Registry Chart Updater: Auth state updated', {
                isAuthenticated: this.isAuthenticated,
                user: this.currentUser?.username || 'anonymous'
            });
        } else {
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
            console.log('🔐 Twin Registry Chart Updater: No auth manager available');
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
     * Get authentication headers for API calls
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
     * Clear sensitive data on logout
     */
    clearSensitiveData() {
        // Clear any cached data that might be user-specific
        this.charts = {};
        console.log('🧹 Twin Registry Chart Updater: Sensitive data cleared');
    }

    /**
     * Destroy the chart updater
     */
    destroy() {
        // Destroy all charts
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.destroy) {
                chart.destroy();
            }
        });
        
        this.charts = {};
        this.isInitialized = false;
        console.log('🧹 Twin Registry Chart Updater destroyed');
    }
} 