/**
 * Twin Registry Performance Monitoring JavaScript
 * Phase 2.2.1: Real-Time Performance Metrics
 * Handles performance monitoring, charts, and alerts
 */

class TwinRegistryPerformance {
    constructor() {
        this.performanceData = {};
        this.alerts = [];
        this.charts = {};
        this.updateInterval = null;
        this.isMonitoring = false;
        
        // UI elements
        this.performancePanel = null;
        this.alertsPanel = null;
        this.dashboardPanel = null;
        
        // Initialize
        this.init();
    }
    
    init() {
        console.log('📊 Initializing Twin Registry Performance Monitoring...');
        
        // Create performance monitoring UI
        this.createPerformanceUI();
        
        // Start monitoring
        this.startMonitoring();
        
        console.log('✅ Twin Registry Performance Monitoring initialized');
    }
    
    createPerformanceUI() {
        // Check if performance monitoring section already exists in template
        const existingPerformanceSection = document.querySelector('#performanceTwinSelect');
        if (existingPerformanceSection) {
            console.log('Performance monitoring section already exists in template, using existing elements');
            this.performancePanel = existingPerformanceSection.closest('.card');
            this.alertsPanel = document.querySelector('#recentAlerts')?.closest('.card');
            this.dashboardPanel = document.querySelector('#performanceMetrics')?.closest('.card');
            return;
        }
        
        // Only create new panels if they don't exist in the template
        this.createPerformancePanel();
        this.createAlertsPanel();
        this.createDashboardPanel();
    }
    
    createPerformancePanel() {
        const container = document.querySelector('.container-fluid');
        if (!container) return;
        
        const panel = document.createElement('div');
        panel.className = 'row mb-4';
        panel.id = 'performancePanel';
        panel.innerHTML = `
            <div class="col-12">
                <div class="card shadow">
                    <div class="card-header py-3 d-flex justify-content-between align-items-center">
                        <h6 class="m-0 font-weight-bold text-primary">
                            <i class="fas fa-chart-line"></i>
                            Twin Performance Monitoring
                        </h6>
                        <div class="btn-group" role="group">
                            <button class="btn btn-sm btn-outline-primary" id="refreshPerformance">
                                <i class="fas fa-sync-alt"></i> Refresh
                            </button>
                            <button class="btn btn-sm btn-outline-success" id="startMonitoring">
                                <i class="fas fa-play"></i> Start Monitoring
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="row" id="performanceTwinCards">
                            <!-- Performance twin cards will be inserted here -->
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Insert after the real-time panel
        const realtimePanel = container.querySelector('#realtimePanel');
        if (realtimePanel) {
            realtimePanel.parentNode.insertBefore(panel, realtimePanel.nextSibling);
        } else {
            container.appendChild(panel);
        }
        
        this.performancePanel = panel;
        
        // Bind event handlers
        this.bindPerformanceEvents();
    }
    
    createAlertsPanel() {
        const container = document.querySelector('.container-fluid');
        if (!container) return;
        
        const panel = document.createElement('div');
        panel.className = 'row mb-4';
        panel.id = 'alertsPanel';
        panel.innerHTML = `
            <div class="col-12">
                <div class="card shadow">
                    <div class="card-header py-3 d-flex justify-content-between align-items-center">
                        <h6 class="m-0 font-weight-bold text-warning">
                            <i class="fas fa-exclamation-triangle"></i>
                            Performance Alerts
                        </h6>
                        <span class="badge bg-warning" id="alertCount">0</span>
                    </div>
                    <div class="card-body">
                        <div id="alertsList">
                            <!-- Alerts will be inserted here -->
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Insert after the performance panel
        const performancePanel = container.querySelector('#performancePanel');
        if (performancePanel) {
            performancePanel.parentNode.insertBefore(panel, performancePanel.nextSibling);
        } else {
            container.appendChild(panel);
        }
        
        this.alertsPanel = panel;
    }
    
    createDashboardPanel() {
        const container = document.querySelector('.container-fluid');
        if (!container) return;
        
        const panel = document.createElement('div');
        panel.className = 'row mb-4';
        panel.id = 'dashboardPanel';
        panel.innerHTML = `
            <div class="col-12">
                <div class="card shadow">
                    <div class="card-header py-3">
                        <h6 class="m-0 font-weight-bold text-info">
                            <i class="fas fa-tachometer-alt"></i>
                            Performance Dashboard
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-3">
                                <div class="card bg-primary text-white">
                                    <div class="card-body text-center">
                                        <h4 id="totalTwins">0</h4>
                                        <p>Total Twins</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card bg-success text-white">
                                    <div class="card-body text-center">
                                        <h4 id="healthyTwins">0</h4>
                                        <p>Healthy</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card bg-warning text-white">
                                    <div class="card-body text-center">
                                        <h4 id="warningTwins">0</h4>
                                        <p>Warning</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card bg-danger text-white">
                                    <div class="card-body text-center">
                                        <h4 id="criticalTwins">0</h4>
                                        <p>Critical</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-md-6">
                                <canvas id="performanceChart"></canvas>
                            </div>
                            <div class="col-md-6">
                                <canvas id="healthChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Insert after the alerts panel
        const alertsPanel = container.querySelector('#alertsPanel');
        if (alertsPanel) {
            alertsPanel.parentNode.insertBefore(panel, alertsPanel.nextSibling);
        } else {
            container.appendChild(panel);
        }
        
        this.dashboardPanel = panel;
    }
    
    bindPerformanceEvents() {
        // Refresh performance data
        document.getElementById('refreshPerformance')?.addEventListener('click', () => {
            this.refreshPerformanceData();
        });
        
        // Start/stop monitoring
        document.getElementById('startMonitoring')?.addEventListener('click', () => {
            if (this.isMonitoring) {
                this.stopMonitoring();
            } else {
                this.startMonitoring();
            }
        });
        
        // New performance card buttons
        document.getElementById('refreshPerformanceCards')?.addEventListener('click', () => {
            this.refreshPerformanceData();
        });
        
        document.getElementById('startPerformanceMonitoring')?.addEventListener('click', () => {
            if (this.isMonitoring) {
                this.stopMonitoring();
            } else {
                this.startMonitoring();
            }
        });
        
        // Performance twin select change
        document.getElementById('performanceTwinSelect')?.addEventListener('change', () => {
            this.updatePerformanceMetrics();
        });
    }
    
    startMonitoring() {
        if (this.isMonitoring) return;
        
        this.isMonitoring = true;
        this.updateInterval = setInterval(() => {
            this.refreshPerformanceData();
        }, 30000); // Update every 30 seconds
        
        // Update button
        const startBtn = document.getElementById('startMonitoring');
        if (startBtn) {
            startBtn.innerHTML = '<i class="fas fa-stop"></i> Stop Monitoring';
            startBtn.classList.remove('btn-outline-success');
            startBtn.classList.add('btn-outline-danger');
        }
        
        // Initial load
        this.refreshPerformanceData();
        
        console.log('📊 Performance monitoring started');
    }
    
    stopMonitoring() {
        if (!this.isMonitoring) return;
        
        this.isMonitoring = false;
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
        
        // Update button
        const startBtn = document.getElementById('startMonitoring');
        if (startBtn) {
            startBtn.innerHTML = '<i class="fas fa-play"></i> Start Monitoring';
            startBtn.classList.remove('btn-outline-danger');
            startBtn.classList.add('btn-outline-success');
        }
        
        console.log('📊 Performance monitoring stopped');
    }
    
    async refreshPerformanceData() {
        try {
            console.log('📊 Refreshing performance data...');
            
            // Get performance data
            const response = await fetch('/twin-registry/api/performance/twins');
            const data = await response.json();
            
            if (data.success) {
                this.performanceData = {};
                data.data.forEach(twin => {
                    this.performanceData[twin.twin_id] = twin;
                });
                
                this.updatePerformanceCards();
                this.updateDashboard();
                this.populateTwinSelector(); // Add this line
                this.updatePerformanceMetrics(); // Add this line
            }
            
            // Get alerts
            const alertsResponse = await fetch('/twin-registry/api/performance/alerts');
            const alertsData = await alertsResponse.json();
            
            if (alertsData.success) {
                this.alerts = alertsData.data;
                this.updateAlerts();
            }
            
            console.log('✅ Performance data refreshed');
            
        } catch (error) {
            console.error('❌ Error refreshing performance data:', error);
        }
    }
    
    populateTwinSelector() {
        const selector = document.getElementById('performanceTwinSelect');
        if (!selector) return;
        
        // Clear existing options
        selector.innerHTML = '<option value="">Choose a twin...</option>';
        
        // Add options for each twin
        Object.values(this.performanceData).forEach(twin => {
            const option = document.createElement('option');
            option.value = twin.twin_id;
            option.textContent = twin.twin_name;
            selector.appendChild(option);
        });
        
        // If there's only one twin, select it automatically
        if (Object.keys(this.performanceData).length === 1) {
            const firstTwinId = Object.keys(this.performanceData)[0];
            selector.value = firstTwinId;
            this.updatePerformanceMetrics();
        }
    }
    
    updatePerformanceCards() {
        const container = document.getElementById('performanceTwinCards');
        if (!container) return;
        
        if (Object.keys(this.performanceData).length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center text-muted py-4">
                    <i class="fas fa-chart-line fa-3x mb-3"></i>
                    <h6>No Performance Data Available</h6>
                    <p class="mb-0">Performance monitoring will start when twins are active</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = Object.values(this.performanceData).map(twin => this.createPerformanceCard(twin)).join('');
    }
    
    createPerformanceCard(twin) {
        const healthClass = this.getHealthClass(twin.health_score);
        const healthIcon = this.getHealthIcon(twin.health_score);
        
        return `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card h-100 border-${healthClass}">
                    <div class="card-header py-2">
                        <div class="d-flex justify-content-between align-items-center">
                            <h6 class="mb-0 text-truncate" title="${twin.twin_name}">${twin.twin_name}</h6>
                            <span class="badge bg-${healthClass}">${twin.status}</span>
                        </div>
                    </div>
                    <div class="card-body p-3">
                        <div class="row text-center mb-3">
                            <div class="col-6">
                                <div class="border rounded p-2">
                                    <h5 class="text-primary mb-0">${twin.health_score}%</h5>
                                    <small class="text-muted">Health Score</small>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="border rounded p-2">
                                    <h5 class="text-info mb-0">${this.formatUptime(twin.uptime_seconds)}</h5>
                                    <small class="text-muted">Uptime</small>
                                </div>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-6">
                                <small class="text-muted">CPU Usage</small>
                                <div class="progress mb-2" style="height: 6px;">
                                    <div class="progress-bar bg-${this.getProgressColor(twin.cpu_usage)}" 
                                         style="width: ${twin.cpu_usage}%"></div>
                                </div>
                                <small>${twin.cpu_usage}%</small>
                            </div>
                            <div class="col-6">
                                <small class="text-muted">Memory Usage</small>
                                <div class="progress mb-2" style="height: 6px;">
                                    <div class="progress-bar bg-${this.getProgressColor(twin.memory_usage)}" 
                                         style="width: ${twin.memory_usage}%"></div>
                                </div>
                                <small>${twin.memory_usage}%</small>
                            </div>
                        </div>
                        
                        <div class="row mt-2">
                            <div class="col-6">
                                <small class="text-muted">Response Time</small>
                                <div class="fw-bold">${twin.response_time}s</div>
                            </div>
                            <div class="col-6">
                                <small class="text-muted">Error Rate</small>
                                <div class="fw-bold text-${this.getErrorColor(twin.error_rate)}">${twin.error_rate}%</div>
                            </div>
                        </div>
                        
                        <div class="mt-3">
                            <button class="btn btn-sm btn-outline-primary w-100 view-details-btn" 
                                    onclick="twinRegistryPerformance.showTwinDetails('${twin.twin_id}')">
                                <i class="fas fa-chart-bar"></i> View Details
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    updateAlerts() {
        // Update recent alerts in the real-time panel
        const recentAlertsContainer = document.getElementById('recentAlerts');
        if (recentAlertsContainer) {
            if (this.alerts.length === 0) {
                recentAlertsContainer.innerHTML = `
                    <div class="text-center text-muted py-3">
                        <i class="fas fa-bell-slash fa-2x mb-2"></i>
                        <p class="mb-0">No recent alerts</p>
                    </div>
                `;
            } else {
                // Show only the most recent 3 alerts
                const recentAlerts = this.alerts.slice(0, 3);
                recentAlertsContainer.innerHTML = recentAlerts.map(alert => `
                    <div class="alert alert-${this.getAlertSeverity(alert.severity)} alert-dismissible fade show mb-2" role="alert">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <strong>${alert.alert_type.replace('_', ' ').toUpperCase()}</strong>
                                <br><small class="text-muted">${alert.twin_id}</small>
                                <br>${alert.message}
                            </div>
                            <button type="button" class="btn-close" data-bs-dismiss="alert" 
                                    onclick="twinRegistryPerformance.resolveAlert(${alert.id})"></button>
                        </div>
                        <small class="text-muted">${new Date(alert.timestamp).toLocaleString()}</small>
                    </div>
                `).join('');
            }
        }
        
        // Update main alerts panel
        const alertsListContainer = document.getElementById('alertsList');
        const alertCountElement = document.getElementById('alertCount');
        
        if (alertsListContainer) {
            if (this.alerts.length === 0) {
                alertsListContainer.innerHTML = `
                    <div class="text-center text-muted py-4">
                        <i class="fas fa-check-circle fa-3x mb-3"></i>
                        <h6>No Active Alerts</h6>
                        <p class="mb-0">All twins are performing within normal parameters</p>
                    </div>
                `;
            } else {
                alertsListContainer.innerHTML = this.alerts.map(alert => `
                    <div class="alert alert-${this.getAlertSeverity(alert.severity)} alert-dismissible fade show mb-3" role="alert">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <strong>${alert.alert_type.replace('_', ' ').toUpperCase()}</strong>
                                <br><small class="text-muted">${alert.twin_id}</small>
                                <br>${alert.message}
                            </div>
                            <button type="button" class="btn-close" data-bs-dismiss="alert" 
                                    onclick="twinRegistryPerformance.resolveAlert(${alert.id})"></button>
                        </div>
                        <small class="text-muted">${new Date(alert.timestamp).toLocaleString()}</small>
                    </div>
                `).join('');
            }
        }
        
        if (alertCountElement) {
            alertCountElement.textContent = this.alerts.length;
        }
    }
    
    updateDashboard() {
        // Update summary cards - use existing template elements
        const totalTwins = Object.keys(this.performanceData).length;
        const healthyTwins = Object.values(this.performanceData).filter(t => t.health_score >= 75).length;
        const warningTwins = Object.values(this.performanceData).filter(t => 60 <= t.health_score && t.health_score < 75).length;
        const criticalTwins = Object.values(this.performanceData).filter(t => t.health_score < 60).length;
        
        // Update existing template elements
        const totalTwinsElement = document.getElementById('totalTwins');
        const activeTwinsElement = document.getElementById('activeTwins');
        const totalDataPointsElement = document.getElementById('totalDataPoints');
        const activeAlertsElement = document.getElementById('activeAlerts');
        
        if (totalTwinsElement) totalTwinsElement.textContent = totalTwins;
        if (activeTwinsElement) activeTwinsElement.textContent = healthyTwins;
        if (totalDataPointsElement) {
            const totalDataPoints = Object.values(this.performanceData).reduce((sum, twin) => sum + (twin.data_points || 0), 0);
            totalDataPointsElement.textContent = totalDataPoints;
        }
        if (activeAlertsElement) {
            const alertCount = this.alerts.filter(alert => alert.status === 'active').length;
            activeAlertsElement.textContent = alertCount;
        }
        
        // Update analytics dashboard elements
        const analyticsTotalTwins = document.getElementById('analyticsTotalTwins');
        const analyticsHealthyTwins = document.getElementById('analyticsHealthyTwins');
        const analyticsWarningTwins = document.getElementById('analyticsWarningTwins');
        const analyticsCriticalTwins = document.getElementById('analyticsCriticalTwins');
        
        if (analyticsTotalTwins) analyticsTotalTwins.textContent = totalTwins;
        if (analyticsHealthyTwins) analyticsHealthyTwins.textContent = healthyTwins;
        if (analyticsWarningTwins) analyticsWarningTwins.textContent = warningTwins;
        if (analyticsCriticalTwins) analyticsCriticalTwins.textContent = criticalTwins;
        
        // Update performance metrics for selected twin
        this.updatePerformanceMetrics();
        
        // Update charts if they exist
        this.updateCharts();
        
        // Update performance cards
        this.updatePerformanceCards();
    }
    
    updatePerformanceMetrics() {
        const selectedTwinId = document.getElementById('performanceTwinSelect')?.value;
        if (!selectedTwinId || !this.performanceData[selectedTwinId]) {
            return;
        }
        
        const twin = this.performanceData[selectedTwinId];
        
        // Update performance metric elements
        const cpuElement = document.getElementById('cpuUsage');
        const memoryElement = document.getElementById('memoryUsage');
        const responseElement = document.getElementById('responseTime');
        const healthElement = document.getElementById('healthScore');
        
        if (cpuElement) cpuElement.textContent = `${twin.cpu_usage}%`;
        if (memoryElement) memoryElement.textContent = `${twin.memory_usage}%`;
        if (responseElement) responseElement.textContent = `${twin.response_time}ms`;
        if (healthElement) healthElement.textContent = `${twin.health_score}%`;
    }
    
    updateCharts() {
        // Performance chart (CPU vs Memory) - only if element exists
        const performanceCtx = document.getElementById('performanceChart');
        if (performanceCtx) {
            const labels = Object.values(this.performanceData).map(t => t.twin_name);
            const cpuData = Object.values(this.performanceData).map(t => t.cpu_usage);
            const memoryData = Object.values(this.performanceData).map(t => t.memory_usage);
            
            if (this.charts.performance) {
                this.charts.performance.destroy();
            }
            
            this.charts.performance = new Chart(performanceCtx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'CPU Usage (%)',
                            data: cpuData,
                            backgroundColor: 'rgba(54, 162, 235, 0.5)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Memory Usage (%)',
                            data: memoryData,
                            backgroundColor: 'rgba(255, 99, 132, 0.5)',
                            borderColor: 'rgba(255, 99, 132, 1)',
                            borderWidth: 1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Resource Usage by Twin'
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
        
        // Health chart (pie chart) - only if element exists
        const healthCtx = document.getElementById('healthChart');
        if (healthCtx) {
            const healthyCount = Object.values(this.performanceData).filter(t => t.health_score >= 75).length;
            const warningCount = Object.values(this.performanceData).filter(t => 60 <= t.health_score && t.health_score < 75).length;
            const criticalCount = Object.values(this.performanceData).filter(t => t.health_score < 60).length;
            
            if (this.charts.health) {
                this.charts.health.destroy();
            }
            
            this.charts.health = new Chart(healthCtx, {
                type: 'pie',
                data: {
                    labels: ['Healthy', 'Warning', 'Critical'],
                    datasets: [{
                        data: [healthyCount, warningCount, criticalCount],
                        backgroundColor: [
                            'rgba(40, 167, 69, 0.8)',
                            'rgba(255, 193, 7, 0.8)',
                            'rgba(220, 53, 69, 0.8)'
                        ],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Twin Health Distribution'
                        }
                    }
                }
            });
        }
    }
    
    async showTwinDetails(twinId) {
        try {
            const response = await fetch(`/twin-registry/api/performance/twins/${twinId}`);
            const data = await response.json();
            
            if (data.success) {
                this.showTwinDetailsModal(data.data);
            }
        } catch (error) {
            console.error('Error fetching twin details:', error);
        }
    }
    
    showTwinDetailsModal(twin) {
        // Create modal for detailed twin performance
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'twinDetailsModal';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Performance Details: ${twin.twin_name}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Current Metrics</h6>
                                <table class="table table-sm">
                                    <tr><td>Health Score:</td><td><span class="badge bg-${this.getHealthClass(twin.health_score)}">${twin.health_score}%</span></td></tr>
                                    <tr><td>CPU Usage:</td><td>${twin.cpu_usage}%</td></tr>
                                    <tr><td>Memory Usage:</td><td>${twin.memory_usage}%</td></tr>
                                    <tr><td>Response Time:</td><td>${twin.response_time}s</td></tr>
                                    <tr><td>Error Rate:</td><td>${twin.error_rate}%</td></tr>
                                    <tr><td>Throughput:</td><td>${twin.throughput} points/sec</td></tr>
                                    <tr><td>Uptime:</td><td>${this.formatUptime(twin.uptime_seconds)}</td></tr>
                                </table>
                            </div>
                            <div class="col-md-6">
                                <h6>Performance History</h6>
                                <canvas id="twinHistoryChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Show the modal
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
        
        // Clean up when modal is hidden
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }
    
    getHealthIcon(score) {
        if (score >= 75) return 'fas fa-heart text-success';
        if (score >= 60) return 'fas fa-exclamation-triangle text-warning';
        return 'fas fa-times-circle text-danger';
    }
    
    getHealthClass(score) {
        if (score >= 75) return 'success';
        if (score >= 60) return 'warning';
        return 'danger';
    }
    
    getProgressColor(value) {
        if (value >= 80) return 'danger';
        if (value >= 60) return 'warning';
        return 'success';
    }
    
    getErrorColor(errorRate) {
        if (errorRate >= 10) return 'danger';
        if (errorRate >= 5) return 'warning';
        return 'success';
    }
    
    getAlertSeverity(severity) {
        switch (severity) {
            case 'critical': return 'danger';
            case 'warning': return 'warning';
            case 'info': return 'info';
            default: return 'secondary';
        }
    }
    
    formatUptime(seconds) {
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        
        if (days > 0) return `${days}d ${hours}h ${minutes}m`;
        if (hours > 0) return `${hours}h ${minutes}m`;
        return `${minutes}m`;
    }
}

// Initialize performance monitoring
const performanceMonitor = new TwinRegistryPerformance();