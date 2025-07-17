/**
 * Federated Learning Dashboard JavaScript
 * Handles federated learning functionality and real-time updates
 */

class FederatedLearningDashboard {
    constructor() {
        this.federationStatus = 'inactive';
        this.aggregationRounds = 0;
        this.activeTwins = 3;
        this.avgHealthScore = 79.4;
        this.websocket = null;
        this.charts = {};
        this.updateInterval = null;
        
        this.init();
    }
    
    init() {
        console.log('🧠 Initializing Federated Learning Dashboard...');
        
        // Initialize charts
        this.initializeCharts();
        
        // Load initial data
        this.loadFederationStatus();
        this.loadTwinPerformance();
        this.loadCrossTwinInsights();
        this.loadPrivacySecurity();
        this.loadFederationMetrics();
        this.loadRealTimeMetrics();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Start real-time updates
        this.startRealTimeUpdates();
        
        console.log('✅ Federated Learning Dashboard initialized');
    }
    
    initializeCharts() {
        // Federation Chart
        const federationCtx = document.getElementById('federationChart');
        if (federationCtx) {
            this.charts.federation = new Chart(federationCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Health Score',
                        data: [],
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Aggregation Rounds',
                        data: [],
                        borderColor: '#f093fb',
                        backgroundColor: 'rgba(240, 147, 251, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        // Real-time Chart
        const realTimeCtx = document.getElementById('realTimeChart');
        if (realTimeCtx) {
            this.charts.realTime = new Chart(realTimeCtx, {
                type: 'bar',
                data: {
                    labels: ['Twin 1', 'Twin 2', 'Twin 3'],
                    datasets: [{
                        label: 'Health Score',
                        data: [77.0, 80.9, 80.4],
                        backgroundColor: [
                            'rgba(102, 126, 234, 0.8)',
                            'rgba(240, 147, 251, 0.8)',
                            'rgba(79, 172, 254, 0.8)'
                        ]
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
    }
    
    setupEventListeners() {
        // Federation control buttons
        document.getElementById('startFederation')?.addEventListener('click', () => {
            this.startFederation();
        });
        
        document.getElementById('stopFederation')?.addEventListener('click', () => {
            this.stopFederation();
        });
        
        document.getElementById('runCycle')?.addEventListener('click', () => {
            this.runFederatedCycle();
        });
    }
    
    async startFederation() {
        try {
            const button = document.getElementById('startFederation');
            button.disabled = true;
            button.innerHTML = '<span class="loading-spinner"></span> Starting...';
            
            const response = await fetch('/federated-learning/api/federation/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    auto_start_cycles: true,
                    cycle_interval: 300
                })
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                this.showNotification('Federation started successfully!', 'success');
                this.federationStatus = 'active';
                this.updateFederationStatus();
            } else {
                this.showNotification('Failed to start federation', 'error');
            }
        } catch (error) {
            console.error('Error starting federation:', error);
            this.showNotification('Error starting federation', 'error');
        } finally {
            const button = document.getElementById('startFederation');
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-play me-2"></i>Start Federation';
        }
    }
    
    async stopFederation() {
        try {
            const button = document.getElementById('stopFederation');
            button.disabled = true;
            button.innerHTML = '<span class="loading-spinner"></span> Stopping...';
            
            const response = await fetch('/federated-learning/api/federation/stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    save_state: true
                })
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                this.showNotification('Federation stopped successfully!', 'success');
                this.federationStatus = 'inactive';
                this.updateFederationStatus();
            } else {
                this.showNotification('Failed to stop federation', 'error');
            }
        } catch (error) {
            console.error('Error stopping federation:', error);
            this.showNotification('Error stopping federation', 'error');
        } finally {
            const button = document.getElementById('stopFederation');
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-stop me-2"></i>Stop Federation';
        }
    }
    
    async runFederatedCycle() {
        try {
            const button = document.getElementById('runCycle');
            button.disabled = true;
            button.innerHTML = '<span class="loading-spinner"></span> Running...';
            
            const response = await fetch('/federated-learning/api/federation/cycle', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                this.showNotification('Federated learning cycle completed!', 'success');
                this.aggregationRounds = result.data.aggregation_round;
                this.updateFederationStatus();
                this.loadFederationMetrics();
            } else {
                this.showNotification('Failed to run federated cycle', 'error');
            }
        } catch (error) {
            console.error('Error running federated cycle:', error);
            this.showNotification('Error running federated cycle', 'error');
        } finally {
            const button = document.getElementById('runCycle');
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-sync me-2"></i>Run Cycle';
        }
    }
    
    async loadFederationStatus() {
        try {
            const response = await fetch('/federated-learning/api/federation/status');
            const result = await response.json();
            
            if (result.status === 'success') {
                const data = result.data;
                this.federationStatus = data.is_active ? 'active' : 'inactive';
                this.aggregationRounds = data.aggregation_round || 0;
                this.activeTwins = data.twins_count || 3;
                
                this.updateFederationStatus();
            }
        } catch (error) {
            console.error('Error loading federation status:', error);
        }
    }
    
    updateFederationStatus() {
        // Update status display
        const statusElement = document.getElementById('federationStatus');
        if (statusElement) {
            statusElement.textContent = this.federationStatus.charAt(0).toUpperCase() + this.federationStatus.slice(1);
            statusElement.className = this.federationStatus === 'active' ? 'fw-bold text-success' : 'fw-bold text-danger';
        }
        
        // Update aggregation rounds
        const roundsElement = document.getElementById('aggregationRounds');
        if (roundsElement) {
            roundsElement.textContent = this.aggregationRounds;
        }
        
        // Update active twins
        const twinsElement = document.getElementById('activeTwins');
        if (twinsElement) {
            twinsElement.textContent = this.activeTwins;
        }
    }
    
    async loadTwinPerformance() {
        try {
            const response = await fetch('/federated-learning/api/twins/performance');
            const result = await response.json();
            
            if (result.status === 'success') {
                this.displayTwinPerformance(result.data);
            }
        } catch (error) {
            console.error('Error loading twin performance:', error);
        }
    }
    
    displayTwinPerformance(twinData) {
        const container = document.getElementById('twinPerformanceCards');
        if (!container) return;
        
        const twinNames = {
            'twin_1': 'Additive Manufacturing',
            'twin_2': 'Smart Grid Substation',
            'twin_3': 'Hydrogen Filling Station'
        };
        
        const twinColors = {
            'twin_1': '#667eea',
            'twin_2': '#f093fb',
            'twin_3': '#4facfe'
        };
        
        let html = '';
        
        Object.entries(twinData).forEach(([twinId, data]) => {
            const twinInfo = data.twin_info || {};
            const performance = data.local_performance || {};
            const cpu = performance.cpu_usage !== undefined ? Number(performance.cpu_usage).toFixed(2) : '0.00';
            const mem = performance.memory_usage !== undefined ? Number(performance.memory_usage).toFixed(2) : '0.00';
            html += `
                <div class="col-md-4 mb-3">
                    <div class="card h-100">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <h6 class="card-title mb-0">${twinNames[twinId] || twinId}</h6>
                                <span class="twin-status ${twinInfo.status === 'good' ? 'active' : 'warning'}"></span>
                            </div>
                            <div class="row text-center">
                                <div class="col-4">
                                    <small class="text-muted">Health</small>
                                    <div class="fw-bold" style="color: ${twinColors[twinId]}">${twinInfo.health_score || 0}%</div>
                                </div>
                                <div class="col-4">
                                    <small class="text-muted">CPU</small>
                                    <div class="fw-bold">${cpu}%</div>
                                </div>
                                <div class="col-4">
                                    <small class="text-muted">Memory</small>
                                    <div class="fw-bold">${mem}%</div>
                                </div>
                            </div>
                            <div class="progress progress-federated mt-2">
                                <div class="progress-bar" style="width: ${twinInfo.health_score || 0}%; background-color: ${twinColors[twinId]}"></div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }
    
    async loadCrossTwinInsights() {
        try {
            const response = await fetch('/federated-learning/api/insights/cross-twin');
            const result = await response.json();
            
            if (result.status === 'success') {
                this.displayCrossTwinInsights(result.data);
            }
        } catch (error) {
            console.error('Error loading cross-twin insights:', error);
        }
    }
    
    displayCrossTwinInsights(insights) {
        const container = document.getElementById('crossTwinInsights');
        if (!container) return;
        
        let html = '';
        
        // Display key insights
        const keyInsights = [
            {
                title: 'Manufacturing-Energy Efficiency',
                content: insights.manufacturing_energy_efficiency?.optimization_opportunity || 'Optimization opportunity available',
                strength: insights.manufacturing_energy_efficiency?.relationship_strength || 0.85
            },
            {
                title: 'Cross-Domain Safety',
                content: insights.cross_domain_safety?.optimization_opportunity || 'Safety enhancement across domains',
                strength: insights.cross_domain_safety?.relationship_strength || 0.92
            },
            {
                title: 'Real-Time Optimization',
                content: insights.real_time_optimization?.optimization_opportunity || 'Real-time system optimization',
                strength: insights.real_time_optimization?.relationship_strength || 0.88
            }
        ];
        
        keyInsights.forEach(insight => {
            html += `
                <div class="insight-card">
                    <div class="insight-title">${insight.title}</div>
                    <div class="insight-content">${insight.content}</div>
                    <div class="mt-2">
                        <small class="text-muted">Relationship Strength: ${(insight.strength * 100).toFixed(0)}%</small>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }
    
    async loadPrivacySecurity() {
        const container = document.getElementById('privacySecurity');
        if (!container) return;
        
        const privacyInfo = {
            'Differential Privacy': 'Applied with ε=0.3-1.0',
            'Data Anonymization': 'High level enabled',
            'Local Processing': '100% data localization',
            'Secure Aggregation': 'FedAvg with noise injection',
            'Privacy Budget': 'Managed per twin'
        };
        
        let html = '';
        Object.entries(privacyInfo).forEach(([feature, status]) => {
            html += `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <span class="text-muted">${feature}</span>
                    <span class="badge bg-success">${status}</span>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }
    
    async loadFederationMetrics() {
        try {
            const response = await fetch('/federated-learning/api/metrics/federation');
            const result = await response.json();
            
            if (result.status === 'success') {
                this.displayFederationMetrics(result.data);
            }
        } catch (error) {
            console.error('Error loading federation metrics:', error);
        }
    }
    
    displayFederationMetrics(metrics) {
        const container = document.getElementById('federationMetrics');
        if (!container) return;
        
        const metricsData = {
            'Aggregation Rounds': metrics.aggregation_round || 0,
            'Active Twins': metrics.active_twins || 3,
            'Model Size': `${(metrics.model_size || 2250000).toLocaleString()} params`,
            'Federation Health': `${(metrics.federation_health || 79.4).toFixed(1)}%`
        };
        
        let html = '';
        Object.entries(metricsData).forEach(([metric, value]) => {
            html += `
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <span class="text-muted">${metric}</span>
                    <span class="fw-bold">${value}</span>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }
    
    async loadRealTimeMetrics() {
        try {
            const response = await fetch('/federated-learning/api/twins/performance');
            const result = await response.json();
            
            if (result.status === 'success') {
                this.updateRealTimeChart(result.data);
                this.displayRealTimeMetrics(result.data);
            }
        } catch (error) {
            console.error('Error loading real-time metrics:', error);
        }
    }
    
    updateRealTimeChart(twinData) {
        if (!this.charts.realTime) return;
        
        const labels = [];
        const data = [];
        
        Object.entries(twinData).forEach(([twinId, twinInfo]) => {
            const twinDataInfo = twinInfo.twin_info || {};
            labels.push(twinId.replace('twin_', 'Twin '));
            data.push(twinDataInfo.health_score || 0);
        });
        
        this.charts.realTime.data.labels = labels;
        this.charts.realTime.data.datasets[0].data = data;
        this.charts.realTime.update();
    }
    
    displayRealTimeMetrics(twinData) {
        const container = document.getElementById('realTimeMetrics');
        if (!container) return;
        
        let totalHealth = 0;
        let count = 0;
        
        Object.values(twinData).forEach(data => {
            const twinInfo = data.twin_info || {};
            totalHealth += twinInfo.health_score || 0;
            count++;
        });
        
        const avgHealth = count > 0 ? totalHealth / count : 0;
        
        const metrics = {
            'Average Health Score': `${avgHealth.toFixed(1)}%`,
            'Total Twins': count,
            'Last Update': new Date().toLocaleTimeString(),
            'Connection Status': 'Connected'
        };
        
        let html = '';
        Object.entries(metrics).forEach(([metric, value]) => {
            html += `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <span class="text-muted small">${metric}</span>
                    <span class="fw-bold small">${value}</span>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }
    
    startRealTimeUpdates() {
        // Update every 5 seconds
        this.updateInterval = setInterval(() => {
            this.loadFederationStatus();
            this.loadRealTimeMetrics();
        }, 5000);
        
        // Setup WebSocket for real-time updates
        this.setupWebSocket();
    }
    
    setupWebSocket() {
        try {
            this.websocket = new WebSocket(`ws://${window.location.host}/federated-learning/ws/federated-learning`);
            
            this.websocket.onopen = () => {
                console.log('🔗 WebSocket connected for federated learning');
                document.getElementById('connectionStatus').textContent = 'Connected';
            };
            
            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleRealTimeUpdate(data);
            };
            
            this.websocket.onclose = () => {
                console.log('🔗 WebSocket disconnected');
                document.getElementById('connectionStatus').textContent = 'Disconnected';
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                document.getElementById('connectionStatus').textContent = 'Error';
            };
        } catch (error) {
            console.error('Error setting up WebSocket:', error);
        }
    }
    
    handleRealTimeUpdate(data) {
        // Update federation status
        if (data.federation_status) {
            this.federationStatus = data.federation_status.is_active ? 'active' : 'inactive';
            this.aggregationRounds = data.federation_status.aggregation_round || 0;
            this.updateFederationStatus();
        }
        
        // Update twin performance
        if (data.twin_performance) {
            this.updateRealTimeChart(data.twin_performance);
            this.displayRealTimeMetrics(data.twin_performance);
        }
    }
    
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
                notification.remove();
            }
        }, 5000);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initializing Federated Learning Dashboard...');
    window.federatedLearningDashboard = new FederatedLearningDashboard();
}); 