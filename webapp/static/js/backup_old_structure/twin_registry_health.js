/**
 * Twin Registry Health Monitoring JavaScript
 * Dedicated health monitoring and analytics for digital twins
 */

class TwinRegistryHealth {
    constructor() {
        this.healthData = {};
        this.healthAlerts = [];
        this.healthCharts = {};
        this.updateInterval = null;
        this.isMonitoring = false;
        
        // Initialize
        this.init();
    }
    
    init() {
        console.log('💓 Initializing Twin Registry Health Monitoring...');
        
        // Bind event handlers
        this.bindHealthEvents();
        
        // Start monitoring
        this.startHealthMonitoring();
        
        console.log('✅ Twin Registry Health Monitoring initialized');
    }
    
    bindHealthEvents() {
        // Refresh health data
        document.getElementById('refreshHealth')?.addEventListener('click', () => {
            this.refreshHealthData();
        });
        
        // Start/stop health monitoring
        document.getElementById('startHealthMonitoring')?.addEventListener('click', () => {
            if (this.isMonitoring) {
                this.stopHealthMonitoring();
            } else {
                this.startHealthMonitoring();
            }
        });
        
        // Export health report
        document.getElementById('exportHealthReport')?.addEventListener('click', () => {
            this.exportHealthReport();
        });
    }
    
    startHealthMonitoring() {
        if (this.isMonitoring) return;
        
        this.isMonitoring = true;
        this.updateInterval = setInterval(() => {
            this.refreshHealthData();
        }, 30000); // Update every 30 seconds
        
        // Update button
        const startBtn = document.getElementById('startHealthMonitoring');
        if (startBtn) {
            startBtn.innerHTML = '<i class="fas fa-stop"></i> Stop Monitoring';
            startBtn.classList.remove('btn-outline-light');
            startBtn.classList.add('btn-outline-danger');
        }
        
        // Initial load
        this.refreshHealthData();
        
        console.log('💓 Health monitoring started');
    }
    
    stopHealthMonitoring() {
        if (!this.isMonitoring) return;
        
        this.isMonitoring = false;
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
        
        // Update button
        const startBtn = document.getElementById('startHealthMonitoring');
        if (startBtn) {
            startBtn.innerHTML = '<i class="fas fa-play"></i> Start Monitoring';
            startBtn.classList.remove('btn-outline-danger');
            startBtn.classList.add('btn-outline-light');
        }
        
        console.log('💓 Health monitoring stopped');
    }
    
    async refreshHealthData() {
        try {
            console.log('💓 Refreshing health data...');
            
            // Get health data from performance API (since health is part of performance)
            const response = await fetch('/twin-registry/api/performance/twins');
            const data = await response.json();
            
            if (data.success) {
                this.healthData = {};
                data.data.forEach(twin => {
                    this.healthData[twin.twin_id] = {
                        twin_id: twin.twin_id,
                        twin_name: twin.twin_name,
                        health_score: twin.health_score,
                        status: twin.status,
                        uptime_seconds: twin.uptime_seconds,
                        last_health_check: new Date().toISOString()
                    };
                });
                
                this.updateHealthDashboard();
                this.updateHealthCards();
                this.updateHealthCharts();
            }
            
            // Get health alerts
            const alertsResponse = await fetch('/twin-registry/api/performance/alerts');
            const alertsData = await alertsResponse.json();
            
            if (alertsData.success) {
                this.healthAlerts = alertsData.data.filter(alert => 
                    alert.alert_type.includes('health') || 
                    alert.alert_type.includes('performance') ||
                    alert.severity === 'critical'
                );
                this.updateHealthAlerts();
            }
            
            console.log('✅ Health data refreshed');
            
        } catch (error) {
            console.error('❌ Error refreshing health data:', error);
        }
    }
    
    updateHealthDashboard() {
        const totalTwins = Object.keys(this.healthData).length;
        const excellentCount = Object.values(this.healthData).filter(t => t.health_score >= 90).length;
        const goodCount = Object.values(this.healthData).filter(t => 75 <= t.health_score && t.health_score < 90).length;
        const warningCount = Object.values(this.healthData).filter(t => 60 <= t.health_score && t.health_score < 75).length;
        const criticalCount = Object.values(this.healthData).filter(t => t.health_score < 60).length;
        
        // Update health overview cards
        const excellentElement = document.getElementById('healthExcellent');
        const goodElement = document.getElementById('healthGood');
        const warningElement = document.getElementById('healthWarning');
        const criticalElement = document.getElementById('healthCritical');
        
        if (excellentElement) excellentElement.textContent = excellentCount;
        if (goodElement) goodElement.textContent = goodCount;
        if (warningElement) warningElement.textContent = warningCount;
        if (criticalElement) criticalElement.textContent = criticalCount;
    }
    
    updateHealthCards() {
        const container = document.getElementById('healthTwinCards');
        if (!container) return;
        
        if (Object.keys(this.healthData).length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center text-muted py-4">
                    <i class="fas fa-heartbeat fa-3x mb-3"></i>
                    <h6>No Health Data Available</h6>
                    <p class="mb-0">Health monitoring will start when twins are active</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = Object.values(this.healthData).map(twin => this.createHealthCard(twin)).join('');
    }
    
    createHealthCard(twin) {
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
                                    <h5 class="text-${healthClass} mb-0">${twin.health_score}%</h5>
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
                        
                        <div class="mb-3">
                            <small class="text-muted">Health Score</small>
                            <div class="progress mb-2" style="height: 8px;">
                                <div class="progress-bar bg-${healthClass}" 
                                     style="width: ${twin.health_score}%"></div>
                            </div>
                            <small>${twin.health_score}% - ${this.getHealthStatus(twin.health_score)}</small>
                        </div>
                        
                        <div class="mt-3">
                            <button class="btn btn-sm btn-outline-primary w-100 view-health-details-btn" 
                                    onclick="twinRegistryHealth.showHealthDetails('${twin.twin_id}')">
                                <i class="fas fa-heartbeat"></i> View Health Details
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    updateHealthCharts() {
        // Health trends chart
        const trendsCtx = document.getElementById('healthTrendsChart');
        if (trendsCtx) {
            const labels = Object.values(this.healthData).map(t => t.twin_name);
            const healthScores = Object.values(this.healthData).map(t => t.health_score);
            
            if (this.healthCharts.trends) {
                this.healthCharts.trends.destroy();
            }
            
            this.healthCharts.trends = new Chart(trendsCtx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Health Score (%)',
                        data: healthScores,
                        borderColor: 'rgba(220, 53, 69, 1)',
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Twin Health Score Trends'
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
        
        // Health distribution chart
        const distributionCtx = document.getElementById('healthDistributionChart');
        if (distributionCtx) {
            const excellentCount = Object.values(this.healthData).filter(t => t.health_score >= 90).length;
            const goodCount = Object.values(this.healthData).filter(t => 75 <= t.health_score && t.health_score < 90).length;
            const warningCount = Object.values(this.healthData).filter(t => 60 <= t.health_score && t.health_score < 75).length;
            const criticalCount = Object.values(this.healthData).filter(t => t.health_score < 60).length;
            
            if (this.healthCharts.distribution) {
                this.healthCharts.distribution.destroy();
            }
            
            this.healthCharts.distribution = new Chart(distributionCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Excellent', 'Good', 'Warning', 'Critical'],
                    datasets: [{
                        data: [excellentCount, goodCount, warningCount, criticalCount],
                        backgroundColor: [
                            'rgba(40, 167, 69, 0.8)',
                            'rgba(23, 162, 184, 0.8)',
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
                            text: 'Health Score Distribution'
                        }
                    }
                }
            });
        }
    }
    
    updateHealthAlerts() {
        const container = document.getElementById('healthAlerts');
        if (!container) return;
        
        if (this.healthAlerts.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted py-3">
                    <i class="fas fa-check-circle fa-2x mb-2"></i>
                    <p class="mb-0">No health alerts - all twins are healthy</p>
                </div>
            `;
        } else {
            container.innerHTML = this.healthAlerts.map(alert => `
                <div class="alert alert-${this.getAlertSeverity(alert.severity)} alert-dismissible fade show mb-3" role="alert">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <strong>${alert.alert_type.replace('_', ' ').toUpperCase()}</strong>
                            <br><small class="text-muted">${alert.twin_id}</small>
                            <br>${alert.message}
                        </div>
                        <button type="button" class="btn-close" data-bs-dismiss="alert" 
                                onclick="twinRegistryHealth.resolveHealthAlert(${alert.id})"></button>
                    </div>
                    <small class="text-muted">${new Date(alert.timestamp).toLocaleString()}</small>
                </div>
            `).join('');
        }
    }
    
    async showHealthDetails(twinId) {
        try {
            const response = await fetch(`/twin-registry/api/performance/twins/${twinId}`);
            const data = await response.json();
            
            if (data.success) {
                this.showHealthDetailsModal(data.data);
            }
        } catch (error) {
            console.error('Error fetching health details:', error);
        }
    }
    
    showHealthDetailsModal(twin) {
        // Create modal for detailed health information
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'healthDetailsModal';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Health Details: ${twin.twin_name}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Health Metrics</h6>
                                <table class="table table-sm">
                                    <tr><td>Health Score:</td><td><span class="badge bg-${this.getHealthClass(twin.health_score)}">${twin.health_score}%</span></td></tr>
                                    <tr><td>Status:</td><td>${twin.status}</td></tr>
                                    <tr><td>Uptime:</td><td>${this.formatUptime(twin.uptime_seconds)}</td></tr>
                                    <tr><td>Last Health Check:</td><td>${new Date(twin.last_health_check).toLocaleString()}</td></tr>
                                </table>
                            </div>
                            <div class="col-md-6">
                                <h6>Health History</h6>
                                <canvas id="healthHistoryChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
        
        // Clean up modal when hidden
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }
    
    async resolveHealthAlert(alertId) {
        try {
            const response = await fetch(`/twin-registry/api/performance/alerts/${alertId}/resolve`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                this.refreshHealthData();
                this.showNotification('Health alert resolved successfully', 'success');
            }
        } catch (error) {
            console.error('Error resolving health alert:', error);
            this.showNotification('Error resolving health alert', 'error');
        }
    }
    
    exportHealthReport() {
        const report = {
            timestamp: new Date().toISOString(),
            total_twins: Object.keys(this.healthData).length,
            health_summary: {
                excellent: Object.values(this.healthData).filter(t => t.health_score >= 90).length,
                good: Object.values(this.healthData).filter(t => 75 <= t.health_score && t.health_score < 90).length,
                warning: Object.values(this.healthData).filter(t => 60 <= t.health_score && t.health_score < 75).length,
                critical: Object.values(this.healthData).filter(t => t.health_score < 60).length
            },
            twins: Object.values(this.healthData),
            alerts: this.healthAlerts
        };
        
        const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `health_report_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification('Health report exported successfully', 'success');
    }
    
    getHealthClass(healthScore) {
        if (healthScore >= 90) return 'success';
        if (healthScore >= 75) return 'info';
        if (healthScore >= 60) return 'warning';
        return 'danger';
    }
    
    getHealthIcon(healthScore) {
        if (healthScore >= 90) return 'fas fa-heartbeat';
        if (healthScore >= 75) return 'fas fa-check-circle';
        if (healthScore >= 60) return 'fas fa-exclamation-triangle';
        return 'fas fa-times-circle';
    }
    
    getHealthStatus(healthScore) {
        if (healthScore >= 90) return 'Excellent';
        if (healthScore >= 75) return 'Good';
        if (healthScore >= 60) return 'Warning';
        return 'Critical';
    }
    
    getAlertSeverity(severity) {
        switch (severity.toLowerCase()) {
            case 'critical': return 'danger';
            case 'warning': return 'warning';
            case 'info': return 'info';
            default: return 'secondary';
        }
    }
    
    formatUptime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        return `${hours}h ${minutes}m`;
    }
    
    showNotification(message, type = 'info') {
        // Create a simple notification
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
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
    
    destroy() {
        this.stopHealthMonitoring();
        
        // Destroy charts
        Object.values(this.healthCharts).forEach(chart => {
            if (chart) chart.destroy();
        });
        
        console.log('💓 Twin Registry Health Monitoring destroyed');
    }
}

// Initialize health monitoring
const twinRegistryHealth = new TwinRegistryHealth(); 