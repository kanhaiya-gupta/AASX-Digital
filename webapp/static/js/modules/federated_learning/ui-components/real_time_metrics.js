/**
 * Real-time Metrics Component
 * Handles real-time monitoring display and WebSocket updates
 */

import { showAlert } from '/static/js/shared/alerts.js';

export default class RealTimeMetricsComponent {
    constructor() {
        this.realTimeData = {
            twins: [],
            total_twins: 0,
            active_twins: 0,
            avg_health_score: 0
        };
        this.chart = null;
        this.websocket = null;
        this.updateInterval = null;
        this.connectionStatus = 'Connected';
    }
    
    async init() {
        console.log('🔧 Initializing Real-time Metrics Component...');
        
        try {
            await this.loadRealTimeMetrics();
            this.initializeChart();
            this.setupEventListeners();
            this.setupWebSocket();
            this.startAutoRefresh();
            
            console.log('✅ Real-time Metrics Component initialized');
        } catch (error) {
            console.error('❌ Failed to initialize Real-time Metrics Component:', error);
            throw error;
        }
    }
    
    async loadRealTimeMetrics() {
        try {
            console.log('📊 Loading real-time metrics...');
            
            // Get real-time metrics from API
            const response = await fetch('/api/federated-learning/monitoring/real-time');
            if (response.ok) {
                const result = await response.json();
                if (result.status === 'success' && result.data) {
                    this.realTimeData = result.data;
                } else {
                    console.warn('⚠️ Failed to load real-time metrics, using default data');
                }
            } else {
                console.warn('⚠️ Failed to load real-time metrics, using default data');
            }
            
            this.displayRealTimeMetrics();
        } catch (error) {
            console.error('❌ Error loading real-time metrics:', error);
            // Use default data on error
            this.displayRealTimeMetrics();
        }
    }
    
    initializeChart() {
        const ctx = document.getElementById('realTimeChart');
        if (!ctx) {
            console.warn('⚠️ Real-time chart canvas not found');
            return;
        }
        
        // Get real twin data for chart
        const twins = this.realTimeData.twins || [];
        const labels = twins.map(twin => twin.twin_name || 'Unknown Twin');
        const data = twins.map(twin => twin.health_score || 0);
        
        this.chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels.length > 0 ? labels : ['No Twins'],
                datasets: [{
                    label: 'Health Score',
                    data: data.length > 0 ? data : [0],
                    backgroundColor: [
                        'rgba(102, 126, 234, 0.8)',
                        'rgba(240, 147, 251, 0.8)',
                        'rgba(79, 172, 254, 0.8)'
                    ],
                    borderColor: [
                        'rgba(102, 126, 234, 1)',
                        'rgba(240, 147, 251, 1)',
                        'rgba(79, 172, 254, 1)'
                    ],
                    borderWidth: 1
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
        
        console.log('📊 Real-time chart initialized');
    }
    
    displayRealTimeMetrics() {
        const container = document.getElementById('realTimeMetrics');
        if (!container) {
            console.warn('⚠️ Real-time metrics container not found');
            return;
        }
        
        // Get real twin data from the database
        const twins = this.realTimeData.twins || [];
        const totalTwins = this.realTimeData.total_twins || 0;
        const activeTwins = this.realTimeData.active_twins || 0;
        const avgHealthScore = this.realTimeData.avg_health_score || 0;
        
        // Create twin display HTML
        let twinHtml = '';
        if (twins.length > 0) {
            twins.forEach((twin, index) => {
                const healthScore = twin.health_score || 0;
                const status = twin.federated_status || 'inactive';
                const statusColor = status === 'active' ? 'success' : 'secondary';
                const textColor = index === 0 ? 'primary' : index === 1 ? 'info' : 'success';
                
                twinHtml += `
                    <div class="col-6 mb-3">
                        <div class="text-center">
                            <div class="h6 fw-bold text-${textColor}">${healthScore.toFixed(1)}%</div>
                            <small class="text-muted">${twin.twin_name || `Twin ${index + 1}`}</small>
                            <br><small class="badge bg-${statusColor}">${status}</small>
                        </div>
                    </div>
                `;
            });
        } else {
            // Show placeholder when no twins
            twinHtml = `
                <div class="col-12 mb-3">
                    <div class="text-center">
                        <div class="h6 fw-bold text-muted">No Twins Available</div>
                        <small class="text-muted">No digital twins found in database</small>
                    </div>
                </div>
            `;
        }
        
        container.innerHTML = `
            <div class="row">
                <div class="col-12 mb-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">Connection Status</small>
                        <span class="badge bg-${this.getConnectionStatusColor()}">${this.connectionStatus}</span>
                    </div>
                </div>
            </div>
            
            <div class="row">
                ${twinHtml}
            </div>
            
            <div class="row">
                <div class="col-6 mb-3">
                    <div class="text-center">
                        <div class="h6 fw-bold text-warning">${avgHealthScore.toFixed(1)}%</div>
                        <small class="text-muted">Average</small>
                    </div>
                </div>
                <div class="col-6 mb-3">
                    <div class="text-center">
                        <div class="h6 fw-bold text-info">${activeTwins}/${totalTwins}</div>
                        <small class="text-muted">Active/Total</small>
                    </div>
                </div>
            </div>
            
            <hr class="my-3">
            
            <div class="text-center">
                <small class="text-muted">
                    <i class="fas fa-clock me-1"></i>
                    Last updated: ${new Date().toLocaleTimeString()}
                </small>
            </div>
        `;
        
        console.log('📊 Real-time metrics display updated');
    }
    
    updateRealTimeChart() {
        if (this.chart) {
            const twins = this.realTimeData.twins || [];
            const labels = twins.map(twin => twin.twin_name || 'Unknown Twin');
            const data = twins.map(twin => twin.health_score || 0);
            
            this.chart.data.labels = labels.length > 0 ? labels : ['No Twins'];
            this.chart.data.datasets[0].data = data.length > 0 ? data : [0];
            this.chart.update('none');
            
            console.log('📊 Real-time chart updated');
        }
    }
    
    getAverageHealthScore() {
        const twins = this.realTimeData.twins || [];
        if (twins.length === 0) return 0;
        
        const scores = twins.map(twin => twin.health_score || 0);
        return scores.reduce((sum, score) => sum + score, 0) / scores.length;
    }
    
    getConnectionStatusColor() {
        switch (this.connectionStatus.toLowerCase()) {
            case 'connected':
                return 'success';
            case 'connecting':
                return 'warning';
            case 'disconnected':
                return 'danger';
            default:
                return 'secondary';
        }
    }
    
    setupWebSocket() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/federated-learning`;
            
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('🔌 WebSocket connected');
                this.connectionStatus = 'Connected';
                this.updateConnectionStatus();
            };
            
            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleRealTimeUpdate(data);
                } catch (error) {
                    console.error('❌ Error parsing WebSocket message:', error);
                }
            };
            
            this.websocket.onclose = () => {
                console.log('🔌 WebSocket disconnected');
                this.connectionStatus = 'Disconnected';
                this.updateConnectionStatus();
            };
            
            this.websocket.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                this.connectionStatus = 'Error';
                this.updateConnectionStatus();
            };
            
        } catch (error) {
            console.error('❌ Failed to setup WebSocket:', error);
            this.connectionStatus = 'Error';
            this.updateConnectionStatus();
        }
    }
    
    handleRealTimeUpdate(data) {
        if (data.type === 'real_time_update') {
            this.realTimeData = { ...this.realTimeData, ...data.twin_data };
            this.displayRealTimeMetrics();
            this.updateRealTimeChart();
            
            console.log('📊 Real-time data updated via WebSocket');
        }
    }
    
    updateConnectionStatus() {
        const statusElement = document.getElementById('connectionStatus');
        if (statusElement) {
            statusElement.textContent = this.connectionStatus;
            statusElement.className = `badge bg-${this.getConnectionStatusColor()} text-dark`;
        }
    }
    
    setupEventListeners() {
        // Listen for real-time updates from other components
        window.addEventListener('realTimeMetricsUpdated', (event) => {
            this.realTimeData = { ...this.realTimeData, ...event.detail };
            this.displayRealTimeMetrics();
            this.updateRealTimeChart();
        });
        
        console.log('🔧 Real-time Metrics event listeners setup complete');
    }
    
    startAutoRefresh() {
        // Refresh real-time data every 30 seconds
        this.updateInterval = setInterval(() => {
            this.loadRealTimeMetrics();
        }, 30000);
        
        console.log('🔄 Real-time Metrics auto-refresh started');
    }
    
    async refresh() {
        await this.loadRealTimeMetrics();
        this.updateRealTimeChart();
    }
    
    async cleanup() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
        
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
        
        console.log('🧹 Real-time Metrics Component cleaned up');
    }
} 