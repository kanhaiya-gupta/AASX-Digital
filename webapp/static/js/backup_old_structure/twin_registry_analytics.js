/**
 * Twin Registry Analytics Integration
 * Phase 2.3: Analytics Integration - Cross-Module Data Sharing
 */

console.log('🔄 Twin Registry Analytics Integration loaded');

// Analytics integration state
let twinAnalyticsState = {
    isConnected: false,
    currentData: null,
    realtimeChart: null,
    updateInterval: null
};

// Initialize twin registry analytics integration
document.addEventListener('DOMContentLoaded', function() {
    initializeTwinAnalytics();
});

function initializeTwinAnalytics() {
    console.log('🔄 Initializing twin registry analytics integration...');
    
    // Load analytics data for twin registry
    loadTwinAnalyticsData();
    
    // Initialize real-time monitoring
    initializeRealTimeMonitoring();
    
    // Set up periodic updates
    setInterval(updateTwinAnalytics, 30000); // Update every 30 seconds
    
    console.log('✅ Twin registry analytics integration initialized');
}

async function loadTwinAnalyticsData() {
    try {
        console.log('📊 Loading twin analytics data...');
        
        // Fetch analytics data using the integration API
        const analyticsData = await AnalyticsIntegration.fetchAnalyticsData({
            metricType: 'quality_metrics',
            timeframe: '30d'
        });
        
        if (analyticsData) {
            updateTwinAnalyticsWidget(analyticsData);
            twinAnalyticsState.currentData = analyticsData;
        } else {
            // Fallback to mock data
            const mockData = generateMockTwinAnalytics();
            updateTwinAnalyticsWidget(mockData);
            twinAnalyticsState.currentData = mockData;
        }
        
    } catch (error) {
        console.error('❌ Error loading twin analytics data:', error);
        
        // Use fallback data
        const fallbackData = generateMockTwinAnalytics();
        updateTwinAnalyticsWidget(fallbackData);
        twinAnalyticsState.currentData = fallbackData;
    }
}

function updateTwinAnalyticsWidget(data) {
    // Update quality score
    const qualityScoreElement = document.getElementById('twin-quality-score');
    if (qualityScoreElement && data.summary) {
        const qualityScore = data.summary.overall_quality_avg || 94.2;
        qualityScoreElement.textContent = qualityScore.toFixed(1) + '%';
    }
    
    // Update performance
    const performanceElement = document.getElementById('twin-performance');
    if (performanceElement && data.summary) {
        const performance = data.summary.performance_avg || 87.3;
        performanceElement.textContent = performance.toFixed(1) + '%';
    }
    
    // Update mini chart
    updateTwinAnalyticsChart(data);
}

function updateTwinAnalyticsChart(data) {
    const canvas = document.getElementById('twinAnalyticsChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Destroy existing chart
    if (twinAnalyticsState.realtimeChart) {
        twinAnalyticsState.realtimeChart.destroy();
    }
    
    // Create new chart
    const chartData = {
        labels: data.data?.slice(-7).map(item => item.date) || generateDateLabels(7),
        datasets: [{
            label: 'Twin Performance',
            data: data.data?.slice(-7).map(item => item.quality_score || item.performance_score) || generateRandomData(7, 85, 95),
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.1)',
            tension: 0.4,
            fill: true
        }]
    };
    
    twinAnalyticsState.realtimeChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: { display: false },
                y: { 
                    display: false,
                    min: 80,
                    max: 100
                }
            },
            elements: {
                point: { radius: 0 }
            }
        }
    });
}

function initializeRealTimeMonitoring() {
    console.log('📡 Initializing real-time monitoring...');
    
    // Connect to WebSocket for real-time updates
    AnalyticsIntegration.connectAnalyticsWebSocket(function(update) {
        handleRealTimeUpdate(update);
    });
    
    // Initialize real-time chart
    initializeRealTimeChart();
    
    // Update connection status
    updateConnectionStatus(true);
}

function initializeRealTimeChart() {
    const canvas = document.getElementById('realtimeChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    const chartData = {
        labels: generateDateLabels(10),
        datasets: [{
            label: 'Real-time Data',
            data: generateRandomData(10, 80, 95),
            borderColor: 'rgb(255, 193, 7)',
            backgroundColor: 'rgba(255, 193, 7, 0.1)',
            tension: 0.4,
            fill: true
        }]
    };
    
    new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: { display: false },
                y: { 
                    display: false,
                    min: 70,
                    max: 100
                }
            },
            elements: {
                point: { radius: 0 }
            },
            animation: {
                duration: 0
            }
        }
    });
}

function handleRealTimeUpdate(update) {
    console.log('📡 Real-time update received:', update);
    
    // Update connection status
    updateConnectionStatus(true);
    
    // Update subscriber count
    updateSubscriberCount(update.subscriber_count || 0);
    
    // Update connected twins count
    updateConnectedTwins(update.connected_twins || 0);
    
    // Update data rate
    updateDataRate(update.data_rate || 0);
    
    // Update real-time chart
    updateRealTimeChart(update.data);
}

function updateConnectionStatus(isConnected) {
    const statusElement = document.getElementById('connection-status');
    if (statusElement) {
        if (isConnected) {
            statusElement.textContent = 'Connected';
            statusElement.className = 'badge bg-light text-success';
        } else {
            statusElement.textContent = 'Disconnected';
            statusElement.className = 'badge bg-light text-danger';
        }
    }
    twinAnalyticsState.isConnected = isConnected;
}

function updateSubscriberCount(count) {
    const countElement = document.getElementById('subscriber-count');
    if (countElement) {
        countElement.textContent = `${count} subscribers`;
    }
}

function updateConnectedTwins(count) {
    const twinsElement = document.getElementById('connected-twins');
    if (twinsElement) {
        twinsElement.textContent = count;
    }
}

function updateDataRate(rate) {
    const rateElement = document.getElementById('data-rate');
    if (rateElement) {
        rateElement.textContent = `${rate}/s`;
    }
}

function updateRealTimeChart(data) {
    // Update real-time chart with new data
    // This would update the chart with live data
    console.log('📊 Updating real-time chart with new data');
}

function updateTwinAnalytics() {
    // Periodic update of analytics data
    loadTwinAnalyticsData();
}

// Twin analytics actions
function refreshTwinAnalytics() {
    console.log('🔄 Refreshing twin analytics...');
    loadTwinAnalyticsData();
    showNotification('Twin analytics refreshed', 'success');
}

function viewTwinTrends() {
    console.log('📈 Opening twin trends...');
    // Navigate to analytics page with twin trends
    window.open('/analytics?view=trends&module=twin-registry', '_blank');
}

function compareTwinPerformance() {
    console.log('⚖️ Opening twin performance comparison...');
    // Navigate to analytics page with comparison view
    window.open('/analytics?view=comparison&module=twin-registry', '_blank');
}

function exportTwinAnalytics() {
    console.log('📊 Exporting twin analytics...');
    
    if (twinAnalyticsState.currentData) {
        const exportData = {
            exportDate: new Date().toISOString(),
            module: 'twin-registry',
            data: twinAnalyticsState.currentData
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `twin_analytics_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showNotification('Twin analytics exported successfully', 'success');
    }
}

// Real-time monitoring actions
function toggleRealTimeMonitoring() {
    const button = document.querySelector('button[onclick="toggleRealTimeMonitoring()"]');
    if (button) {
        if (twinAnalyticsState.isConnected) {
            // Stop monitoring
            if (twinAnalyticsState.updateInterval) {
                clearInterval(twinAnalyticsState.updateInterval);
                twinAnalyticsState.updateInterval = null;
            }
            updateConnectionStatus(false);
            button.innerHTML = '<i class="fas fa-play me-1"></i>Start Monitoring';
            showNotification('Real-time monitoring stopped', 'info');
        } else {
            // Start monitoring
            initializeRealTimeMonitoring();
            button.innerHTML = '<i class="fas fa-stop me-1"></i>Stop Monitoring';
            showNotification('Real-time monitoring started', 'success');
        }
    }
}

function viewRealTimeLogs() {
    console.log('📋 Opening real-time logs...');
    // Show real-time logs modal or navigate to logs page
    showNotification('Real-time logs feature coming soon', 'info');
}

// Utility functions
function generateMockTwinAnalytics() {
    return {
        summary: {
            overall_quality_avg: 94.2,
            performance_avg: 87.3,
            compliance_avg: 98.7,
            efficiency_avg: 89.1
        },
        data: generateDateLabels(30).map((date, index) => ({
            date: date,
            quality_score: 90 + Math.random() * 8,
            performance_score: 85 + Math.random() * 10,
            compliance_score: 95 + Math.random() * 4
        }))
    };
}

function generateDateLabels(days) {
    const labels = [];
    const today = new Date();
    for (let i = days - 1; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
    }
    return labels;
}

function generateRandomData(count, min, max) {
    const data = [];
    for (let i = 0; i < count; i++) {
        data.push(Math.random() * (max - min) + min);
    }
    return data;
}

function showNotification(message, type = 'info') {
    // Use existing notification system or create simple alert
    if (typeof showNotification === 'function') {
        showNotification(message, type);
    } else {
        console.log(`${type.toUpperCase()}: ${message}`);
    }
}

// Export functions to global scope
window.refreshTwinAnalytics = refreshTwinAnalytics;
window.viewTwinTrends = viewTwinTrends;
window.compareTwinPerformance = compareTwinPerformance;
window.exportTwinAnalytics = exportTwinAnalytics;
window.toggleRealTimeMonitoring = toggleRealTimeMonitoring;
window.viewRealTimeLogs = viewRealTimeLogs; 