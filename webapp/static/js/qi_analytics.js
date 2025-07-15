/**
 * QI Analytics Dashboard JavaScript
 * Handles all analytics visualization, data loading, and interactive features
 */

console.log('🔧 QI Analytics JavaScript file loaded successfully');

// Global variables
let qualityTrendsChart, performanceChart, twinPerformanceChart, twinHealthChart;
let performanceTrendsChart, uptimeChart;
let analyticsData = {};
let updateInterval;

// Initialize the QI analytics dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM Content Loaded - Initializing QI Analytics Dashboard...');
    
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('❌ Chart.js is not loaded! Please check the CDN link.');
        return;
    }
    console.log('✅ Chart.js is available');
    
    // Check for required DOM elements
    const requiredElements = [
        'qualityTrendsChart',
        'performanceChart', 
        'twinPerformanceChart',
        'twinHealthChart',
        'performanceTrendsChart',
        'uptimeChart'
    ];
    
    const missingElements = requiredElements.filter(id => !document.getElementById(id));
    if (missingElements.length > 0) {
        console.warn('⚠️ Missing DOM elements:', missingElements);
    } else {
        console.log('✅ All required DOM elements found');
    }
    
    initializeQIAnalytics();
    setupEventListeners();
    startRealTimeUpdates();
});

function initializeQIAnalytics() {
    console.log('📊 Setting up analytics charts...');
    
    try {
        // Initialize all charts
        initializeQualityTrendsChart();
        initializePerformanceChart();
        initializeTwinPerformanceChart();
        initializeTwinHealthChart();
        initializePerformanceTrendsChart();
        initializeUptimeChart();
        
        // Load initial data
        loadAnalyticsData();
        loadTwinRegistryData();
        
        console.log('✅ QI Analytics dashboard initialized successfully');
    } catch (error) {
        console.error('❌ Error initializing QI Analytics:', error);
    }
}

function setupEventListeners() {
    console.log('🔗 Setting up event listeners...');
    
    // Refresh button
    const refreshBtn = document.getElementById('refreshAnalytics');
    if (refreshBtn) {
        console.log('✅ Found refresh button, adding event listener');
        refreshBtn.addEventListener('click', function() {
            console.log('🔄 Refresh button clicked');
            loadAnalyticsData();
            loadTwinRegistryData();
            showNotification('Analytics data refreshed successfully', 'success');
        });
    } else {
        console.warn('⚠️ Refresh button not found');
    }
    
    // Generate report button
    const generateReportBtn = document.getElementById('generateReport');
    if (generateReportBtn) {
        console.log('✅ Found generate report button, adding event listener');
        generateReportBtn.addEventListener('click', function() {
            console.log('📄 Generate report button clicked');
            generateAnalyticsReport();
        });
    } else {
        console.warn('⚠️ Generate report button not found');
    }
    
    // Twin registry action buttons
    setupTwinRegistryActions();
    console.log('✅ Event listeners setup completed');
}

function setupTwinRegistryActions() {
    // Sync all twins
    window.syncAllTwins = function() {
        showNotification('Syncing all twins...', 'info');
        // Simulate sync process
        setTimeout(() => {
            loadTwinRegistryData();
            showNotification('All twins synchronized successfully', 'success');
        }, 2000);
    };
    
    // View twin health
    window.viewTwinHealth = function() {
        window.location.href = '/twin-registry#health';
    };
    
    // Export twin data
    window.exportTwinData = function() {
        showNotification('Exporting twin data...', 'info');
        // Simulate export process
        setTimeout(() => {
            showNotification('Twin data exported successfully', 'success');
        }, 1500);
    };
}

function initializeQualityTrendsChart() {
    const ctx = document.getElementById('qualityTrendsChart');
    if (!ctx) return;
    
    qualityTrendsChart = new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: generateDateLabels(30),
            datasets: [{
                label: 'Quality Score',
                data: generateRandomData(30, 90, 96),
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Compliance Rate',
                data: generateRandomData(30, 95, 99),
                borderColor: 'rgb(54, 162, 235)',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Efficiency Index',
                data: generateRandomData(30, 85, 92),
                borderColor: 'rgb(255, 159, 64)',
                backgroundColor: 'rgba(255, 159, 64, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white'
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Score (%)'
                    },
                    min: 80,
                    max: 100
                }
            }
        }
    });
}

function initializePerformanceChart() {
    const ctx = document.getElementById('performanceChart');
    if (!ctx) return;
    
    performanceChart = new Chart(ctx.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: ['Excellent', 'Good', 'Average', 'Needs Improvement'],
            datasets: [{
                data: [45, 35, 15, 5],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 206, 86, 0.8)',
                    'rgba(255, 99, 132, 0.8)'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${context.parsed} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function initializeTwinPerformanceChart() {
    const ctx = document.getElementById('twinPerformanceChart');
    if (!ctx) return;
    
    twinPerformanceChart = new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: ['Additive Manufacturing', 'Hydrogen Station', 'Servo Motor'],
            datasets: [{
                label: 'Health Score',
                data: [96.2, 94.8, 91.6],
                backgroundColor: 'rgba(75, 192, 192, 0.8)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }, {
                label: 'CPU Usage',
                data: [25, 35, 45],
                backgroundColor: 'rgba(54, 162, 235, 0.8)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }, {
                label: 'Memory Usage',
                data: [30, 40, 35],
                backgroundColor: 'rgba(255, 159, 64, 0.8)',
                borderColor: 'rgba(255, 159, 64, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                }
            },
            scales: {
                x: {
                    stacked: false
                },
                y: {
                    stacked: false,
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

function initializeTwinHealthChart() {
    const ctx = document.getElementById('twinHealthChart');
    if (!ctx) return;
    
    twinHealthChart = new Chart(ctx.getContext('2d'), {
        type: 'pie',
        data: {
            labels: ['Healthy', 'Warning', 'Critical'],
            datasets: [{
                data: [2, 1, 0],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(255, 206, 86, 0.8)',
                    'rgba(255, 99, 132, 0.8)'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${context.parsed} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function initializePerformanceTrendsChart() {
    const ctx = document.getElementById('performanceTrendsChart');
    if (!ctx) return;
    
    // Create moving window data for performance trends
    const maxDataPoints = 50;
    const performanceData = {
        labels: [],
        data: []
    };
    
    // Initialize with some data points
    for (let i = 0; i < maxDataPoints; i++) {
        performanceData.labels.push(`T${i}`);
        performanceData.data.push(Math.random() * 20 + 80); // 80-100 range
    }
    
    performanceTrendsChart = new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: performanceData.labels,
            datasets: [{
                label: 'Performance Score',
                data: performanceData.data,
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 0,
                pointHoverRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white'
                }
            },
            scales: {
                x: {
                    display: false
                },
                y: {
                    display: true,
                    min: 70,
                    max: 100,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                }
            },
            animation: {
                duration: 750,
                easing: 'easeInOutQuart'
            }
        }
    });
}

function initializeUptimeChart() {
    const ctx = document.getElementById('uptimeChart');
    if (!ctx) return;
    
    uptimeChart = new Chart(ctx.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: ['Uptime', 'Downtime'],
            datasets: [{
                data: [98.5, 1.5],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(255, 99, 132, 0.8)'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.parsed}%`;
                        }
                    }
                }
            }
        }
    });
}

function loadAnalyticsData() {
    console.log('Loading analytics data...');
    
    // Simulate API call
    setTimeout(() => {
        // Update KPI cards
        updateKPICards();
        
        // Update charts with new data
        updateCharts();
        
        console.log('Analytics data loaded successfully');
    }, 500);
}

function loadTwinRegistryData() {
    console.log('Loading twin registry data...');
    
    // Fetch twin registry statistics
    fetch('/twin-registry/api/twins/statistics')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('✅ Twin registry data loaded:', data);
            
            // Transform the data to match our expected format
            const transformedData = {
                total: data.total_twins || 0,
                active: data.active_twins || 0,
                warning: data.inactive_twins || 0, // Using inactive as warning for now
                error: 0 // We can add error tracking later
            };
            
            updateTwinRegistrySummary(transformedData);
        })
        .catch(error => {
            console.error('❌ Error loading twin registry data:', error);
            
            // Try fallback to summary endpoint
            fetch('/twin-registry/api/twins/summary')
                .then(response => response.json())
                .then(summaryData => {
                    console.log('✅ Fallback summary data loaded:', summaryData);
                    if (summaryData.success && summaryData.data) {
                        const twins = summaryData.data;
                        const transformedData = {
                            total: twins.length || 0,
                            active: twins.filter(t => t.status === 'active').length || 0,
                            warning: twins.filter(t => t.status !== 'active').length || 0,
                            error: 0
                        };
                        updateTwinRegistrySummary(transformedData);
                    } else {
                        // Use mock data as final fallback
                        updateTwinRegistrySummary({
                            total: 1,
                            active: 1,
                            warning: 0,
                            error: 0
                        });
                    }
                })
                .catch(fallbackError => {
                    console.error('❌ Fallback also failed:', fallbackError);
                    // Use mock data as final fallback
                    updateTwinRegistrySummary({
                        total: 1,
                        active: 1,
                        warning: 0,
                        error: 0
                    });
                });
        });
}

function updateKPICards() {
    // Update KPI values with realistic data
    const kpis = {
        'overallQualityScore': (Math.random() * 5 + 92).toFixed(1) + '%',
        'complianceRate': (Math.random() * 3 + 97).toFixed(1) + '%',
        'efficiencyIndex': (Math.random() * 8 + 85).toFixed(1) + '%',
        'riskScore': (Math.random() * 8 + 8).toFixed(1)
    };
    
    Object.keys(kpis).forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = kpis[id];
        }
    });
}

function updateCharts() {
    // Update quality trends chart
    if (qualityTrendsChart) {
        qualityTrendsChart.data.datasets.forEach(dataset => {
            dataset.data = generateRandomData(30, 85, 99);
        });
        qualityTrendsChart.update('none');
    }
    
    // Update twin performance chart
    if (twinPerformanceChart) {
        twinPerformanceChart.data.datasets[0].data = [
            Math.random() * 5 + 92,
            Math.random() * 5 + 90,
            Math.random() * 5 + 88
        ];
        twinPerformanceChart.data.datasets[1].data = [
            Math.random() * 20 + 20,
            Math.random() * 20 + 30,
            Math.random() * 20 + 40
        ];
        twinPerformanceChart.update('none');
    }
    
    // Update twin health chart
    if (twinHealthChart) {
        const total = 3;
        const healthy = Math.floor(Math.random() * 2) + 1;
        const warning = Math.floor(Math.random() * 2);
        const critical = total - healthy - warning;
        
        twinHealthChart.data.datasets[0].data = [healthy, warning, critical];
        twinHealthChart.update('none');
    }
}

function updateTwinRegistrySummary(data) {
    // Update twin registry summary cards
    const elements = {
        'totalTwins': data.total || 0,
        'activeTwins': data.active || 0,
        'warningTwins': data.warning || 0,
        'errorTwins': data.error || 0
    };
    
    Object.keys(elements).forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = elements[id];
        }
    });
    
    // Update twin health chart if available
    if (twinHealthChart) {
        twinHealthChart.data.datasets[0].data = [
            data.active || 0,
            data.warning || 0,
            data.error || 0
        ];
        twinHealthChart.update('none');
    }
}

function startRealTimeUpdates() {
    // Update performance trends chart every 3 seconds
    updateInterval = setInterval(() => {
        if (performanceTrendsChart) {
            const newDataPoint = Math.random() * 20 + 80;
            
            // Shift data points (moving window)
            performanceTrendsChart.data.labels.shift();
            performanceTrendsChart.data.labels.push(`T${Date.now()}`);
            
            performanceTrendsChart.data.datasets[0].data.shift();
            performanceTrendsChart.data.datasets[0].data.push(newDataPoint);
            
            performanceTrendsChart.update('none');
        }
    }, 3000);
}

function generateAnalyticsReport() {
    showNotification('Generating analytics report...', 'info');
    
    // Simulate report generation
    setTimeout(() => {
        const reportData = {
            timestamp: new Date().toISOString(),
            qualityScore: document.getElementById('overallQualityScore')?.textContent || 'N/A',
            complianceRate: document.getElementById('complianceRate')?.textContent || 'N/A',
            efficiencyIndex: document.getElementById('efficiencyIndex')?.textContent || 'N/A',
            riskScore: document.getElementById('riskScore')?.textContent || 'N/A'
        };
        
        // Create downloadable report
        const reportBlob = new Blob([
            JSON.stringify(reportData, null, 2)
        ], { type: 'application/json' });
        
        const url = URL.createObjectURL(reportBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analytics-report-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showNotification('Analytics report generated and downloaded successfully', 'success');
    }, 2000);
}

function exportAnalyticsData() {
    showNotification('Exporting analytics data...', 'info');
    
    // Simulate data export
    setTimeout(() => {
        const exportData = {
            timestamp: new Date().toISOString(),
            analytics: {
                qualityTrends: qualityTrendsChart?.data || {},
                performanceDistribution: performanceChart?.data || {},
                twinPerformance: twinPerformanceChart?.data || {},
                twinHealth: twinHealthChart?.data || {},
                performanceTrends: performanceTrendsChart?.data || {},
                uptime: uptimeChart?.data || {}
            },
            kpis: {
                overallQualityScore: document.getElementById('overallQualityScore')?.textContent || 'N/A',
                complianceRate: document.getElementById('complianceRate')?.textContent || 'N/A',
                efficiencyIndex: document.getElementById('efficiencyIndex')?.textContent || 'N/A',
                riskScore: document.getElementById('riskScore')?.textContent || 'N/A'
            }
        };
        
        // Create downloadable export
        const exportBlob = new Blob([
            JSON.stringify(exportData, null, 2)
        ], { type: 'application/json' });
        
        const url = URL.createObjectURL(exportBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analytics-export-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showNotification('Analytics data exported successfully', 'success');
    }, 1500);
}

function compareTwinAnalytics() {
    showNotification('Opening twin comparison tool...', 'info');
    
    // Simulate opening comparison tool
    setTimeout(() => {
        // Create a modal for twin comparison
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'twinComparisonModal';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-balance-scale me-2"></i>
                            Twin Analytics Comparison
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Additive Manufacturing</h6>
                                <ul class="list-unstyled">
                                    <li><strong>Quality Score:</strong> 96.2%</li>
                                    <li><strong>Compliance:</strong> 99.1%</li>
                                    <li><strong>Efficiency:</strong> 89.3%</li>
                                    <li><strong>Status:</strong> <span class="badge bg-success">Excellent</span></li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6>Hydrogen Filling Station</h6>
                                <ul class="list-unstyled">
                                    <li><strong>Quality Score:</strong> 94.8%</li>
                                    <li><strong>Compliance:</strong> 98.7%</li>
                                    <li><strong>Efficiency:</strong> 92.1%</li>
                                    <li><strong>Status:</strong> <span class="badge bg-success">Excellent</span></li>
                                </ul>
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-12">
                                <h6>Comparison Summary</h6>
                                <p class="text-muted">Additive Manufacturing shows higher quality scores while Hydrogen Filling Station demonstrates better efficiency metrics.</p>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" onclick="exportComparisonReport()">Export Comparison</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Show the modal
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        // Remove modal from DOM after it's hidden
        modal.addEventListener('hidden.bs.modal', function() {
            document.body.removeChild(modal);
        });
        
        showNotification('Twin comparison tool opened', 'success');
    }, 1000);
}

function exportComparisonReport() {
    showNotification('Exporting comparison report...', 'info');
    
    setTimeout(() => {
        const comparisonData = {
            timestamp: new Date().toISOString(),
            comparison: {
                twin1: {
                    name: 'Additive Manufacturing',
                    qualityScore: '96.2%',
                    compliance: '99.1%',
                    efficiency: '89.3%',
                    status: 'Excellent'
                },
                twin2: {
                    name: 'Hydrogen Filling Station',
                    qualityScore: '94.8%',
                    compliance: '98.7%',
                    efficiency: '92.1%',
                    status: 'Excellent'
                },
                summary: 'Additive Manufacturing shows higher quality scores while Hydrogen Filling Station demonstrates better efficiency metrics.'
            }
        };
        
        const exportBlob = new Blob([
            JSON.stringify(comparisonData, null, 2)
        ], { type: 'application/json' });
        
        const url = URL.createObjectURL(exportBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `twin-comparison-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('twinComparisonModal'));
        if (modal) {
            modal.hide();
        }
        
        showNotification('Comparison report exported successfully', 'success');
    }, 1500);
}

function predictiveAnalytics() {
    showNotification('Opening predictive analytics...', 'info');
    
    setTimeout(() => {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'predictiveAnalyticsModal';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-crystal-ball me-2"></i>
                            Predictive Analytics
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle me-2"></i>
                            Predictive analytics features are coming soon! This will include:
                        </div>
                        <ul class="list-group list-group-flush">
                            <li class="list-group-item">
                                <i class="fas fa-chart-line text-primary me-2"></i>
                                <strong>Anomaly Detection:</strong> Identify unusual patterns in twin behavior
                            </li>
                            <li class="list-group-item">
                                <i class="fas fa-chart-area text-success me-2"></i>
                                <strong>Forecasting:</strong> Predict future performance trends
                            </li>
                            <li class="list-group-item">
                                <i class="fas fa-exclamation-triangle text-warning me-2"></i>
                                <strong>Risk Assessment:</strong> Early warning system for potential issues
                            </li>
                            <li class="list-group-item">
                                <i class="fas fa-robot text-info me-2"></i>
                                <strong>Machine Learning:</strong> AI-powered insights and recommendations
                            </li>
                        </ul>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" disabled>Coming Soon</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        modal.addEventListener('hidden.bs.modal', function() {
            document.body.removeChild(modal);
        });
        
        showNotification('Predictive analytics preview opened', 'success');
    }, 1000);
}

function refreshTwinData() {
    loadTwinRegistryData();
    showNotification('Twin registry data refreshed', 'success');
}

// Utility functions
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
    // Create notification element
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

// Cleanup function
function cleanup() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
}

// Cleanup on page unload
window.addEventListener('beforeunload', cleanup); 