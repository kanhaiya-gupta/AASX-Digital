/**
 * Twin Registry Health Monitoring Module
 * Handles comprehensive health monitoring, real-time system status, and proactive health management
 */

class HealthMonitor {
    constructor() {
        this.monitoringActive = false;
        this.updateInterval = 30; // seconds
        this.healthCheckFrequency = 60; // seconds
        this.alertRetention = 7; // days
        this.autoAcknowledge = false;
        this.charts = {};
        this.alerts = [];
        this.healthData = {};
        this.monitoringInterval = null;
        this.healthCheckInterval = null;
        
        this.initialize();
    }

    async initialize() {
        try {
            await this.loadHealthData();
            this.setupEventListeners();
            this.initializeCharts();
            this.updateHealthSummary();
            this.loadHealthAlerts();
            this.loadMonitoringConfiguration();
        } catch (error) {
            console.error('Failed to initialize Health Monitor:', error);
            this.showError('Failed to initialize health monitoring system');
        }
    }

    setupEventListeners() {
        // Monitoring controls
        document.getElementById('twin_registry_startMonitoring')?.addEventListener('click', () => this.startMonitoring());
        document.getElementById('twin_registry_stopMonitoring')?.addEventListener('click', () => this.stopMonitoring());
        document.getElementById('twin_registry_refreshHealth')?.addEventListener('click', () => this.refreshHealthData());
        
        // System health controls
        document.getElementById('twin_registry_systemHealthMetric')?.addEventListener('change', () => this.updateSystemHealthChart());
        document.getElementById('twin_registry_refreshSystemHealth')?.addEventListener('click', () => this.refreshSystemHealth());
        
        // Health analytics controls
        document.getElementById('twin_registry_healthAnalyticsMetric')?.addEventListener('change', () => this.updateHealthAnalyticsChart());
        document.getElementById('twin_registry_healthTimeRange')?.addEventListener('change', () => this.updateHealthAnalyticsChart());
        document.getElementById('twin_registry_refreshHealthAnalytics')?.addEventListener('click', () => this.refreshHealthAnalytics());
        
        // Distribution controls
        document.getElementById('twin_registry_distributionFilter')?.addEventListener('change', () => this.updateDistributionChart());
        document.getElementById('twin_registry_refreshDistribution')?.addEventListener('click', () => this.refreshDistribution());
        
        // Alert controls
        document.getElementById('twin_registry_alertSeverity')?.addEventListener('change', () => this.filterAlerts());
        document.getElementById('twin_registry_acknowledgeAll')?.addEventListener('click', () => this.acknowledgeAllAlerts());
        document.getElementById('twin_registry_refreshAlerts')?.addEventListener('click', () => this.refreshAlerts());
        
        // Configuration controls
        document.getElementById('twin_registry_saveConfig')?.addEventListener('click', () => this.saveConfiguration());
        document.getElementById('twin_registry_resetConfig')?.addEventListener('click', () => this.resetConfiguration());
        document.getElementById('twin_registry_exportHealthData')?.addEventListener('click', () => this.exportHealthData());
        document.getElementById('twin_registry_viewHealthHistory')?.addEventListener('click', () => this.viewHealthHistory());
        
        // Threshold inputs
        document.getElementById('twin_registry_criticalThreshold')?.addEventListener('change', (e) => this.updateThreshold('critical', e.target.value));
        document.getElementById('twin_registry_warningThreshold')?.addEventListener('change', (e) => this.updateThreshold('warning', e.target.value));
        
        // Settings
        document.getElementById('twin_registry_updateInterval')?.addEventListener('change', (e) => this.updateSetting('updateInterval', e.target.value));
        document.getElementById('twin_registry_healthCheckFreq')?.addEventListener('change', (e) => this.updateSetting('healthCheckFrequency', e.target.value));
        document.getElementById('twin_registry_alertRetention')?.addEventListener('change', (e) => this.updateSetting('alertRetention', e.target.value));
        document.getElementById('twin_registry_autoAcknowledge')?.addEventListener('change', (e) => this.updateSetting('autoAcknowledge', e.target.checked));
    }

    async loadHealthData() {
        try {
            this.showLoading();
            
            // Load system health
            const systemHealthResponse = await fetch('/api/twin-registry/health/system', {
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });

            if (systemHealthResponse.ok) {
                const systemHealth = await systemHealthResponse.json();
                this.healthData.system = systemHealth;
            }

            // Load registry health
            const registryHealthResponse = await fetch('/api/twin-registry/health/registry', {
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });

            if (registryHealthResponse.ok) {
                const registryHealth = await registryHealthResponse.json();
                this.healthData.registry = registryHealth;
            }

            // Load twin health data
            const twinsResponse = await fetch('/api/twin-registry/twins', {
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });

            if (twinsResponse.ok) {
                const twinsData = await twinsResponse.json();
                this.healthData.twins = twinsData.twins || [];
            }
            
        } catch (error) {
            console.error('Failed to load health data:', error);
            this.showError('Failed to load health data');
        } finally {
            this.hideLoading();
        }
    }

    async loadHealthAlerts() {
        try {
            // Load active alerts
            const alertsResponse = await fetch('/api/twin-registry/alerts', {
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });

            if (alertsResponse.ok) {
                const alertsData = await alertsResponse.json();
                this.alerts = alertsData.alerts || [];
                this.updateAlertsDisplay();
            }
        } catch (error) {
            console.error('Failed to load health alerts:', error);
        }
    }

    loadMonitoringConfiguration() {
        // Load configuration from localStorage or use defaults
        const config = {
            updateInterval: localStorage.getItem('health_updateInterval') || 30,
            healthCheckFrequency: localStorage.getItem('health_healthCheckFreq') || 60,
            alertRetention: localStorage.getItem('health_alertRetention') || 7,
            autoAcknowledge: localStorage.getItem('health_autoAcknowledge') === 'true',
            criticalThreshold: localStorage.getItem('health_criticalThreshold') || 60,
            warningThreshold: localStorage.getItem('health_warningThreshold') || 75
        };

        // Update UI with loaded configuration
        document.getElementById('twin_registry_updateInterval').value = config.updateInterval;
        document.getElementById('twin_registry_healthCheckFreq').value = config.healthCheckFrequency;
        document.getElementById('twin_registry_alertRetention').value = config.alertRetention;
        document.getElementById('twin_registry_autoAcknowledge').checked = config.autoAcknowledge;
        document.getElementById('twin_registry_criticalThreshold').value = config.criticalThreshold;
        document.getElementById('twin_registry_warningThreshold').value = config.warningThreshold;

        // Update internal state
        this.updateInterval = parseInt(config.updateInterval);
        this.healthCheckFrequency = parseInt(config.healthCheckFrequency);
        this.alertRetention = parseInt(config.alertRetention);
        this.autoAcknowledge = config.autoAcknowledge;
    }

    async startMonitoring() {
        try {
            const response = await fetch('/api/twin-registry/monitoring/start', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.monitoringActive = true;
                this.updateMonitoringStatus();
                this.startMonitoringIntervals();
                this.showSuccess('Real-time monitoring started successfully');
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Failed to start monitoring:', error);
            this.showError('Failed to start monitoring');
        }
    }

    async stopMonitoring() {
        try {
            const response = await fetch('/api/twin-registry/monitoring/stop', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.monitoringActive = false;
                this.updateMonitoringStatus();
                this.stopMonitoringIntervals();
                this.showSuccess('Real-time monitoring stopped successfully');
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Failed to stop monitoring:', error);
            this.showError('Failed to stop monitoring');
        }
    }

    startMonitoringIntervals() {
        // Start health data update interval
        this.monitoringInterval = setInterval(() => {
            this.updateHealthData();
        }, this.updateInterval * 1000);

        // Start health check interval
        this.healthCheckInterval = setInterval(() => {
            this.performHealthCheck();
        }, this.healthCheckFrequency * 1000);

        // Update UI
        document.getElementById('twin_registry_startMonitoring').disabled = true;
        document.getElementById('twin_registry_stopMonitoring').disabled = false;
        document.getElementById('twin_registry_liveIndicator').style.display = 'flex';
    }

    stopMonitoringIntervals() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = null;
        }

        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
            this.healthCheckInterval = null;
        }

        // Update UI
        document.getElementById('twin_registry_startMonitoring').disabled = false;
        document.getElementById('twin_registry_stopMonitoring').disabled = true;
        document.getElementById('twin_registry_liveIndicator').style.display = 'none';
    }

    updateMonitoringStatus() {
        document.getElementById('twin_registry_monitoringActive').textContent = this.monitoringActive ? 'Yes' : 'No';
        document.getElementById('twin_registry_lastUpdate').textContent = this.monitoringActive ? 'Just now' : 'Never';
        document.getElementById('twin_registry_monitoredTwins').textContent = this.healthData.twins?.length || 0;
        document.getElementById('twin_registry_dataPoints').textContent = this.monitoringActive ? 'Live' : '0';
    }

    async updateHealthData() {
        try {
            await this.loadHealthData();
            this.updateHealthSummary();
            this.updateSystemHealthChart();
            this.updateHealthAnalyticsChart();
            this.updateDistributionChart();
            this.checkHealthThresholds();
        } catch (error) {
            console.error('Failed to update health data:', error);
        }
    }

    async performHealthCheck() {
        try {
            // Perform comprehensive health check
            const healthCheckResponse = await fetch('/api/twin-registry/health', {
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });

            if (healthCheckResponse.ok) {
                const healthCheck = await healthCheckResponse.json();
                this.processHealthCheckResults(healthCheck);
            }
        } catch (error) {
            console.error('Failed to perform health check:', error);
        }
    }

    processHealthCheckResults(healthCheck) {
        // Process health check results and update alerts
        if (healthCheck.overall_status === 'critical') {
            this.createAlert('critical', 'System Health Critical', 'Overall system health is in critical condition');
        } else if (healthCheck.overall_status === 'warning') {
            this.createAlert('warning', 'System Health Warning', 'System health requires attention');
        }

        // Update last update time
        document.getElementById('twin_registry_lastUpdate').textContent = 'Just now';
    }

    updateHealthSummary() {
        if (!this.healthData.twins) return;

        const totalTwins = this.healthData.twins.length;
        const excellentCount = this.healthData.twins.filter(twin => (twin.overall_health_score || 0) >= 90).length;
        const goodCount = this.healthData.twins.filter(twin => (twin.overall_health_score || 0) >= 75 && (twin.overall_health_score || 0) < 90).length;
        const warningCount = this.healthData.twins.filter(twin => (twin.overall_health_score || 0) >= 60 && (twin.overall_health_score || 0) < 75).length;
        const criticalCount = this.healthData.twins.filter(twin => (twin.overall_health_score || 0) < 60).length;

        // Update summary cards
        document.getElementById('twin_registry_excellentCount').textContent = excellentCount;
        document.getElementById('twin_registry_goodCount').textContent = goodCount;
        document.getElementById('twin_registry_warningCount').textContent = warningCount;
        document.getElementById('twin_registry_criticalCount').textContent = criticalCount;

        // Update progress bars
        this.updateProgressBars(excellentCount, goodCount, warningCount, criticalCount, totalTwins);
    }

    updateProgressBars(excellent, good, warning, critical, total) {
        if (total === 0) return;

        const excellentPercent = (excellent / total) * 100;
        const goodPercent = (good / total) * 100;
        const warningPercent = (warning / total) * 100;
        const criticalPercent = (critical / total) * 100;

        // Update progress bars in health cards
        const progressBars = document.querySelectorAll('.tr-health-progress .tr-progress-bar');
        if (progressBars.length >= 4) {
            progressBars[0].style.width = `${excellentPercent}%`;
            progressBars[1].style.width = `${goodPercent}%`;
            progressBars[2].style.width = `${warningPercent}%`;
            progressBars[3].style.width = `${criticalPercent}%`;
        }
    }

    initializeCharts() {
        this.initializeSystemHealthChart();
        this.initializeHealthAnalyticsChart();
        this.initializeDistributionChart();
    }

    initializeSystemHealthChart() {
        const ctx = document.getElementById('twin_registry_systemHealthChart');
        if (!ctx) return;

        this.charts.systemHealth = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
                datasets: [{
                    label: 'CPU Health',
                    data: [85, 82, 88, 90, 87, 89],
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Memory Health',
                    data: [92, 89, 91, 88, 90, 87],
                    borderColor: '#17a2b8',
                    backgroundColor: 'rgba(23, 162, 184, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Storage Health',
                    data: [95, 94, 96, 93, 95, 94],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    initializeHealthAnalyticsChart() {
        const ctx = document.getElementById('twin_registry_healthAnalyticsChart');
        if (!ctx) return;

        this.charts.healthAnalytics = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Health Trend', 'Correlation', 'Prediction', 'Benchmark'],
                datasets: [{
                    label: 'Health Metrics',
                    data: [85, 78, 92, 88],
                    backgroundColor: [
                        'rgba(220, 53, 69, 0.8)',
                        'rgba(23, 162, 184, 0.8)',
                        'rgba(40, 167, 69, 0.8)',
                        'rgba(255, 193, 7, 0.8)'
                    ],
                    borderColor: [
                        '#dc3545',
                        '#17a2b8',
                        '#28a745',
                        '#ffc107'
                    ],
                    borderWidth: 2
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
                        max: 100,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    initializeDistributionChart() {
        const ctx = document.getElementById('twin_registry_healthDistributionChart');
        if (!ctx) return;

        this.charts.distribution = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Excellent', 'Good', 'Warning', 'Critical'],
                datasets: [{
                    data: [45, 30, 20, 5],
                    backgroundColor: ['#28a745', '#17a2b8', '#ffc107', '#dc3545'],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }

    updateSystemHealthChart() {
        const metric = document.getElementById('twin_registry_systemHealthMetric')?.value || 'overview';
        
        if (!this.charts.systemHealth) return;

        let newData;
        let newLabels;

        switch (metric) {
            case 'overview':
                newLabels = ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'];
                newData = [
                    [85, 82, 88, 90, 87, 89], // CPU
                    [92, 89, 91, 88, 90, 87], // Memory
                    [95, 94, 96, 93, 95, 94]  // Storage
                ];
                break;
            case 'resources':
                newLabels = ['CPU', 'Memory', 'Storage', 'Network'];
                newData = [
                    [89, 87, 91, 88, 90, 86],
                    [92, 89, 91, 88, 90, 87],
                    [95, 94, 96, 93, 95, 94],
                    [88, 86, 90, 87, 89, 85]
                ];
                break;
            case 'processes':
                newLabels = ['Main Process', 'Worker 1', 'Worker 2', 'Monitor'];
                newData = [
                    [95, 94, 96, 93, 95, 94],
                    [88, 86, 90, 87, 89, 85],
                    [92, 89, 91, 88, 90, 87],
                    [90, 88, 92, 89, 91, 88]
                ];
                break;
            case 'network':
                newLabels = ['Latency', 'Throughput', 'Packet Loss', 'Jitter'];
                newData = [
                    [85, 82, 88, 90, 87, 89],
                    [92, 89, 91, 88, 90, 87],
                    [88, 86, 90, 87, 89, 85],
                    [90, 88, 92, 89, 91, 88]
                ];
                break;
        }

        this.charts.systemHealth.data.labels = newLabels;
        this.charts.systemHealth.data.datasets.forEach((dataset, index) => {
            if (newData[index]) {
                dataset.data = newData[index];
            }
        });
        this.charts.systemHealth.update();
    }

    updateHealthAnalyticsChart() {
        const metric = document.getElementById('twin_registry_healthAnalyticsMetric')?.value || 'trends';
        const timeRange = document.getElementById('twin_registry_healthTimeRange')?.value || '24h';
        
        if (!this.charts.healthAnalytics) return;

        let newData;
        let newLabels;

        switch (metric) {
            case 'trends':
                newLabels = ['Health Trend', 'Correlation', 'Prediction', 'Benchmark'];
                newData = [85, 78, 92, 88];
                break;
            case 'correlation':
                newLabels = ['Performance', 'Reliability', 'Efficiency', 'Quality'];
                newData = [82, 85, 79, 88];
                break;
            case 'prediction':
                newLabels = ['1 Hour', '6 Hours', '12 Hours', '24 Hours'];
                newData = [89, 87, 84, 81];
                break;
            case 'benchmarking':
                newLabels = ['Industry Avg', 'Best Practice', 'Target', 'Current'];
                newData = [75, 90, 85, 88];
                break;
        }

        this.charts.healthAnalytics.data.labels = newLabels;
        this.charts.healthAnalytics.data.datasets[0].data = newData;
        this.charts.healthAnalytics.update();
    }

    updateDistributionChart() {
        const filter = document.getElementById('twin_registry_distributionFilter')?.value || 'all';
        
        if (!this.charts.distribution) return;

        let newData;
        let newLabels;

        switch (filter) {
            case 'all':
                newLabels = ['Excellent', 'Good', 'Warning', 'Critical'];
                newData = [45, 30, 20, 5];
                break;
            case 'active':
                newLabels = ['Excellent', 'Good', 'Warning'];
                newData = [50, 35, 15];
                break;
            case 'critical':
                newLabels = ['Critical', 'Warning', 'Good'];
                newData = [10, 25, 65];
                break;
        }

        this.charts.distribution.data.labels = newLabels;
        this.charts.distribution.data.datasets[0].data = newData;
        this.charts.distribution.update();
    }

    updateSystemHealthMetrics() {
        if (!this.healthData.system) return;

        // Update CPU health
        const cpuHealth = 100 - (this.healthData.system.cpu_usage || 0);
        document.getElementById('twin_registry_cpuHealth').textContent = `${cpuHealth}%`;
        this.updateSystemStatus('cpuHealth', cpuHealth);

        // Update Memory health
        const memoryHealth = 100 - (this.healthData.system.memory_usage || 0);
        document.getElementById('twin_registry_memoryHealth').textContent = `${memoryHealth}%`;
        this.updateSystemStatus('memoryHealth', memoryHealth);

        // Update Storage health
        const storageHealth = 100 - (this.healthData.system.disk_usage || 0);
        document.getElementById('twin_registry_storageHealth').textContent = `${storageHealth}%`;
        this.updateSystemStatus('storageHealth', storageHealth);

        // Update Network health
        const networkHealth = 85; // Placeholder - would come from actual network metrics
        document.getElementById('twin_registry_networkHealth').textContent = `${networkHealth}%`;
        this.updateSystemStatus('networkHealth', networkHealth);
    }

    updateSystemStatus(metricId, value) {
        const statusElement = document.getElementById(`twin_registry_${metricId}`).nextElementSibling;
        const trendElement = statusElement.nextElementSibling;

        if (value >= 90) {
            statusElement.className = 'tr-system-status tr-status-healthy';
            statusElement.textContent = 'Healthy';
        } else if (value >= 75) {
            statusElement.className = 'tr-system-status tr-status-warning';
            statusElement.textContent = 'Warning';
        } else {
            statusElement.className = 'tr-system-status tr-status-critical';
            statusElement.textContent = 'Critical';
        }

        // Update trend (simplified - would be calculated from historical data)
        const trend = Math.random() > 0.5 ? 'up' : 'down';
        const trendValue = Math.floor(Math.random() * 15) + 1;
        
        trendElement.className = `tr-system-trend tr-trend-${trend}`;
        trendElement.innerHTML = `<i class="fas fa-arrow-${trend}"></i><span>${trend === 'up' ? '+' : '-'}${trendValue}%</span>`;
    }

    updateDistributionDetails() {
        if (!this.healthData.twins) return;

        const totalTwins = this.healthData.twins.length;
        const healthScores = this.healthData.twins.map(twin => twin.overall_health_score || 0).filter(score => score > 0);
        const averageHealth = healthScores.length > 0 ? Math.round(healthScores.reduce((a, b) => a + b, 0) / healthScores.length) : 0;
        const healthiestTwin = this.healthData.twins.reduce((best, twin) => 
            (twin.overall_health_score || 0) > (best.overall_health_score || 0) ? twin : best
        );
        const needsAttention = this.healthData.twins.filter(twin => (twin.overall_health_score || 0) < 75).length;

        document.getElementById('twin_registry_totalTwins').textContent = totalTwins;
        document.getElementById('twin_registry_averageHealth').textContent = `${averageHealth}%`;
        document.getElementById('twin_registry_healthiestTwin').textContent = healthiestTwin.twin_name || 'Unknown';
        document.getElementById('twin_registry_needsAttention').textContent = needsAttention;

        // Update health recommendations
        this.updateHealthRecommendations(averageHealth, needsAttention);
    }

    updateHealthRecommendations(averageHealth, needsAttention) {
        const recommendationsContainer = document.getElementById('twin_registry_healthRecommendations');
        if (!recommendationsContainer) return;

        let recommendations = [];

        if (averageHealth < 70) {
            recommendations.push('System health is below optimal levels. Review resource allocation and performance bottlenecks.');
        }

        if (needsAttention > 0) {
            recommendations.push(`${needsAttention} twins require immediate attention. Prioritize critical health issues.`);
        }

        if (averageHealth >= 90) {
            recommendations.push('System health is excellent. Continue monitoring and preventive maintenance.');
        }

        if (recommendations.length === 0) {
            recommendations.push('No immediate actions required. System health is stable.');
        }

        recommendationsContainer.innerHTML = recommendations.map(rec => 
            `<div class="tr-recommendation-item">
                <i class="fas fa-lightbulb text-warning"></i>
                <span>${rec}</span>
            </div>`
        ).join('');
    }

    updateAlertsDisplay() {
        const criticalCount = this.alerts.filter(alert => alert.severity === 'critical').length;
        const warningCount = this.alerts.filter(alert => alert.severity === 'warning').length;
        const infoCount = this.alerts.filter(alert => alert.severity === 'info').length;

        document.getElementById('twin_registry_criticalAlerts').textContent = criticalCount;
        document.getElementById('twin_registry_warningAlerts').textContent = warningCount;
        document.getElementById('twin_registry_infoAlerts').textContent = infoCount;

        this.renderAlertsList();
    }

    renderAlertsList() {
        const alertsContainer = document.getElementById('twin_registry_alertsContainer');
        if (!alertsContainer) return;

        if (this.alerts.length === 0) {
            alertsContainer.innerHTML = `
                <div class="tr-no-alerts">
                    <i class="fas fa-check-circle text-success"></i>
                    <span>No active alerts</span>
                </div>
            `;
            return;
        }

        const alertsHtml = this.alerts.slice(0, 5).map(alert => `
            <div class="tr-alert-item tr-alert-${alert.severity}" onclick="healthMonitor.viewAlertDetails('${alert.id}')">
                <div class="tr-alert-header">
                    <i class="fas fa-${this.getAlertIcon(alert.severity)}"></i>
                    <span class="tr-alert-title">${alert.title}</span>
                    <span class="tr-alert-time">${this.formatTime(alert.timestamp)}</span>
                </div>
                <div class="tr-alert-message">${alert.message}</div>
            </div>
        `).join('');

        alertsContainer.innerHTML = alertsHtml;
    }

    getAlertIcon(severity) {
        switch (severity) {
            case 'critical': return 'times-circle';
            case 'warning': return 'exclamation-triangle';
            case 'info': return 'info-circle';
            default: return 'info-circle';
        }
    }

    createAlert(severity, title, message) {
        const alert = {
            id: Date.now().toString(),
            severity,
            title,
            message,
            timestamp: new Date().toISOString(),
            acknowledged: false
        };

        this.alerts.unshift(alert);
        this.updateAlertsDisplay();

        // Auto-acknowledge if enabled
        if (this.autoAcknowledge) {
            setTimeout(() => this.acknowledgeAlert(alert.id), 5000);
        }
    }

    async acknowledgeAlert(alertId) {
        try {
            const response = await fetch(`/api/twin-registry/alerts/${alertId}/acknowledge`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const alert = this.alerts.find(a => a.id === alertId);
                if (alert) {
                    alert.acknowledged = true;
                    this.alerts = this.alerts.filter(a => a.id !== alertId);
                    this.updateAlertsDisplay();
                }
            }
        } catch (error) {
            console.error('Failed to acknowledge alert:', error);
        }
    }

    async acknowledgeAllAlerts() {
        try {
            const response = await fetch('/api/twin-registry/alerts/acknowledge-all', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.alerts = [];
                this.updateAlertsDisplay();
                this.showSuccess('All alerts acknowledged');
            }
        } catch (error) {
            console.error('Failed to acknowledge all alerts:', error);
        }
    }

    filterAlerts() {
        const severity = document.getElementById('twin_registry_alertSeverity')?.value || 'all';
        
        if (severity === 'all') {
            this.renderAlertsList();
        } else {
            const filteredAlerts = this.alerts.filter(alert => alert.severity === severity);
            this.renderFilteredAlerts(filteredAlerts);
        }
    }

    renderFilteredAlerts(filteredAlerts) {
        const alertsContainer = document.getElementById('twin_registry_alertsContainer');
        if (!alertsContainer) return;

        if (filteredAlerts.length === 0) {
            alertsContainer.innerHTML = `
                <div class="tr-no-alerts">
                    <i class="fas fa-filter text-muted"></i>
                    <span>No alerts match the selected severity</span>
                </div>
            `;
            return;
        }

        const alertsHtml = filteredAlerts.map(alert => `
            <div class="tr-alert-item tr-alert-${alert.severity}" onclick="healthMonitor.viewAlertDetails('${alert.id}')">
                <div class="tr-alert-header">
                    <i class="fas fa-${this.getAlertIcon(alert.severity)}"></i>
                    <span class="tr-alert-title">${alert.title}</span>
                    <span class="tr-alert-time">${this.formatTime(alert.timestamp)}</span>
                </div>
                <div class="tr-alert-message">${alert.message}</div>
            </div>
        `).join('');

        alertsContainer.innerHTML = alertsHtml;
    }

    checkHealthThresholds() {
        if (!this.healthData.twins) return;

        const criticalThreshold = parseInt(document.getElementById('twin_registry_criticalThreshold')?.value || 60);
        const warningThreshold = parseInt(document.getElementById('twin_registry_warningThreshold')?.value || 75);

        this.healthData.twins.forEach(twin => {
            const healthScore = twin.overall_health_score || 0;
            
            if (healthScore < criticalThreshold) {
                this.createAlert('critical', `Twin Health Critical: ${twin.twin_name}`, 
                    `Twin ${twin.twin_name} has critical health score: ${healthScore}%`);
            } else if (healthScore < warningThreshold) {
                this.createAlert('warning', `Twin Health Warning: ${twin.twin_name}`, 
                    `Twin ${twin.twin_name} has warning health score: ${healthScore}%`);
            }
        });
    }

    updateThreshold(type, value) {
        localStorage.setItem(`health_${type}Threshold`, value);
        this.checkHealthThresholds();
    }

    updateSetting(setting, value) {
        localStorage.setItem(`health_${setting}`, value);
        
        switch (setting) {
            case 'updateInterval':
                this.updateInterval = parseInt(value);
                if (this.monitoringActive) {
                    this.stopMonitoringIntervals();
                    this.startMonitoringIntervals();
                }
                break;
            case 'healthCheckFrequency':
                this.healthCheckFrequency = parseInt(value);
                if (this.monitoringActive) {
                    this.stopMonitoringIntervals();
                    this.startMonitoringIntervals();
                }
                break;
            case 'alertRetention':
                this.alertRetention = parseInt(value);
                break;
            case 'autoAcknowledge':
                this.autoAcknowledge = value;
                break;
        }
    }

    async saveConfiguration() {
        try {
            const config = {
                updateInterval: this.updateInterval,
                healthCheckFrequency: this.healthCheckFrequency,
                alertRetention: this.alertRetention,
                autoAcknowledge: this.autoAcknowledge,
                criticalThreshold: document.getElementById('twin_registry_criticalThreshold')?.value,
                warningThreshold: document.getElementById('twin_registry_warningThreshold')?.value
            };

            const response = await fetch('/api/twin-registry/monitoring/config', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            });

            if (response.ok) {
                this.showSuccess('Configuration saved successfully');
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Failed to save configuration:', error);
            this.showError('Failed to save configuration');
        }
    }

    resetConfiguration() {
        // Reset to default values
        document.getElementById('twin_registry_updateInterval').value = 30;
        document.getElementById('twin_registry_healthCheckFreq').value = 60;
        document.getElementById('twin_registry_alertRetention').value = 7;
        document.getElementById('twin_registry_autoAcknowledge').checked = false;
        document.getElementById('twin_registry_criticalThreshold').value = 60;
        document.getElementById('twin_registry_warningThreshold').value = 75;

        // Update internal state
        this.updateSetting('updateInterval', 30);
        this.updateSetting('healthCheckFrequency', 60);
        this.updateSetting('alertRetention', 7);
        this.updateSetting('autoAcknowledge', false);

        this.showSuccess('Configuration reset to defaults');
    }

    async exportHealthData() {
        try {
            const healthReport = {
                timestamp: new Date().toISOString(),
                systemHealth: this.healthData.system,
                registryHealth: this.healthData.registry,
                twinsHealth: this.healthData.twins,
                alerts: this.alerts,
                configuration: {
                    updateInterval: this.updateInterval,
                    healthCheckFrequency: this.healthCheckFrequency,
                    alertRetention: this.alertRetention,
                    autoAcknowledge: this.autoAcknowledge
                }
            };

            const blob = new Blob([JSON.stringify(healthReport, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `health_report_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            this.showSuccess('Health data exported successfully');
        } catch (error) {
            console.error('Failed to export health data:', error);
            this.showError('Failed to export health data');
        }
    }

    viewHealthHistory() {
        // Implementation for viewing health history
        this.showInfo('Health history feature coming soon');
    }

    viewAlertDetails(alertId) {
        const alert = this.alerts.find(a => a.id === alertId);
        if (!alert) return;

        const modal = new bootstrap.Modal(document.getElementById('twin_registry_alertDetailsModal'));
        const title = document.getElementById('twin_registry_alertDetailsTitle');
        const content = document.getElementById('twin_registry_alertDetailsContent');

        title.innerHTML = `<i class="fas fa-exclamation-triangle"></i> Alert Details - ${alert.severity.toUpperCase()}`;
        
        content.innerHTML = `
            <div class="tr-alert-details">
                <div class="tr-alert-detail-item">
                    <strong>Title:</strong> ${alert.title}
                </div>
                <div class="tr-alert-detail-item">
                    <strong>Message:</strong> ${alert.message}
                </div>
                <div class="tr-alert-detail-item">
                    <strong>Severity:</strong> 
                    <span class="tr-severity-badge tr-severity-${alert.severity}">${alert.severity.toUpperCase()}</span>
                </div>
                <div class="tr-alert-detail-item">
                    <strong>Timestamp:</strong> ${this.formatTime(alert.timestamp)}
                </div>
                <div class="tr-alert-detail-item">
                    <strong>Status:</strong> ${alert.acknowledged ? 'Acknowledged' : 'Active'}
                </div>
            </div>
        `;

        modal.show();
    }

    refreshHealthData() {
        this.updateHealthData();
        this.showSuccess('Health data refreshed');
    }

    refreshSystemHealth() {
        this.updateSystemHealthChart();
        this.updateSystemHealthMetrics();
        this.showSuccess('System health refreshed');
    }

    refreshHealthAnalytics() {
        this.updateHealthAnalyticsChart();
        this.showSuccess('Health analytics refreshed');
    }

    refreshDistribution() {
        this.updateDistributionChart();
        this.updateDistributionDetails();
        this.showSuccess('Distribution data refreshed');
    }

    refreshAlerts() {
        this.loadHealthAlerts();
        this.showSuccess('Alerts refreshed');
    }

    showLoading() {
        // Show loading state
        const healthCards = document.querySelectorAll('.tr-health-card');
        healthCards.forEach(card => {
            card.style.opacity = '0.6';
        });
    }

    hideLoading() {
        // Hide loading state
        const healthCards = document.querySelectorAll('.tr-health-card');
        healthCards.forEach(card => {
            card.style.opacity = '1';
        });
    }

    getAuthToken() {
        return window.authManager?.getToken() || '';
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} minutes ago`;
        if (diffHours < 24) return `${diffHours} hours ago`;
        if (diffDays < 7) return `${diffDays} days ago`;
        return date.toLocaleDateString();
    }

    showSuccess(message) {
        console.log('✅', message);
    }

    showError(message) {
        console.error('❌', message);
    }

    showWarning(message) {
        console.warn('⚠️', message);
    }

    showInfo(message) {
        console.log('ℹ️', message);
    }
}

// Initialize health monitor when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.healthMonitor = new HealthMonitor();
});

// Export for global access
window.HealthMonitor = HealthMonitor;
