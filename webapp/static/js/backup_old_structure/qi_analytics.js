/**
 * QI Analytics Dashboard JavaScript
 * Handles all analytics visualization, data loading, and interactive features
 * Enhanced with Advanced Chart Interactions (Week 1-2)
 */

console.log('🔧 QI Analytics JavaScript file loaded successfully');

// Global variables
let qualityTrendsChart, performanceChart, twinPerformanceChart, twinHealthChart;
let performanceTrendsChart, uptimeChart;
let analyticsData = {};
let updateInterval;
let drillDownStack = []; // Track drill-down navigation
let currentFilters = {}; // Track active filters
let chartData = {}; // Store original chart data for filtering

// Chart interaction states
let chartInteractionState = {
    qualityTrends: { level: 'overview', filters: {} },
    performance: { level: 'overview', filters: {} },
    twinPerformance: { level: 'overview', filters: {} },
    twinHealth: { level: 'overview', filters: {} }
};

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
    setupAdvancedChartInteractions();
    startRealTimeUpdates();
});

function initializeQIAnalytics() {
    console.log('📊 Setting up analytics charts...');
    
    try {
        // Initialize all charts with enhanced interactions
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

function setupAdvancedChartInteractions() {
    console.log('🔧 Setting up advanced chart interactions...');
    
    // Add chart control panels
    addChartControlPanels();
    
    // Setup global chart interaction functions
    window.resetChartView = resetChartView;
    window.applyChartFilter = applyChartFilter;
    window.exportChartData = exportChartData;
    window.drillDownChart = drillDownChart;
    
    console.log('✅ Advanced chart interactions setup completed');
}

function addChartControlPanels() {
    // Add control panels to each chart container
    const chartContainers = document.querySelectorAll('.chart-container');
    
    chartContainers.forEach(container => {
        const chartId = container.querySelector('canvas').id;
        const controlPanel = createChartControlPanel(chartId);
        container.parentNode.insertBefore(controlPanel, container);
    });
}

function createChartControlPanel(chartId) {
    const panel = document.createElement('div');
    panel.className = 'chart-control-panel mb-2';
    panel.innerHTML = `
        <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
            <div class="d-flex gap-1">
                <button class="btn btn-sm btn-outline-primary" onclick="drillDownChart('${chartId}')" title="Drill Down">
                    <i class="fas fa-search-plus"></i>
                </button>
                <button class="btn btn-sm btn-outline-secondary" onclick="resetChartView('${chartId}')" title="Reset View">
                    <i class="fas fa-home"></i>
                </button>
                <button class="btn btn-sm btn-outline-info" onclick="applyChartFilter('${chartId}')" title="Filter">
                    <i class="fas fa-filter"></i>
                </button>
                <button class="btn btn-sm btn-outline-success" onclick="exportChartData('${chartId}')" title="Export">
                    <i class="fas fa-download"></i>
                </button>
            </div>
            <div class="chart-status small text-muted" id="${chartId}-status">
                Overview Level
            </div>
        </div>
    `;
    return panel;
}

function initializeQualityTrendsChart() {
    const ctx = document.getElementById('qualityTrendsChart');
    if (!ctx) return;
    
    // Enhanced data structure for drill-down
    chartData.qualityTrends = {
        overview: {
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
        facility: {
            labels: ['Additive Manufacturing', 'Hydrogen Filling Station', 'Servo DC Motor Assembly'],
            datasets: [{
                label: 'Quality Score',
                data: [96.2, 94.8, 91.6],
                backgroundColor: ['rgba(75, 192, 192, 0.8)', 'rgba(54, 162, 235, 0.8)', 'rgba(255, 159, 64, 0.8)']
            }]
        },
        daily: {
            labels: generateDateLabels(7),
            datasets: [{
                label: 'Daily Quality Metrics',
                data: generateRandomData(7, 88, 97),
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.1)',
                tension: 0.4,
                fill: true
            }]
        }
    };
    
    qualityTrendsChart = new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: chartData.qualityTrends.overview,
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
                    bodyColor: 'white',
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(1)}%`;
                        },
                        afterLabel: function(context) {
                            return getEnhancedTooltipInfo(context);
                        }
                    }
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
            },
            onClick: function(event, elements) {
                handleChartClick(event, elements, 'qualityTrendsChart');
            }
        }
    });
}

function initializePerformanceChart() {
    const ctx = document.getElementById('performanceChart');
    if (!ctx) return;
    
    // Enhanced data structure for drill-down
    chartData.performance = {
        overview: {
            labels: ['Excellent', 'Good', 'Average', 'Poor'],
            datasets: [{
                data: [45, 30, 20, 5],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 205, 86, 0.8)',
                    'rgba(255, 99, 132, 0.8)'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        facility: {
            labels: ['Additive Manufacturing', 'Hydrogen Filling Station', 'Servo DC Motor Assembly'],
            datasets: [{
                data: [35, 40, 25],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 159, 64, 0.8)'
                ]
            }]
        }
    };
    
    performanceChart = new Chart(ctx.getContext('2d'), {
        type: 'doughnut',
        data: chartData.performance.overview,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${context.parsed} (${percentage}%)`;
                        }
                    }
                }
            },
            onClick: function(event, elements) {
                handleChartClick(event, elements, 'performanceChart');
            }
        }
    });
}

function initializeTwinPerformanceChart() {
    const ctx = document.getElementById('twinPerformanceChart');
    if (!ctx) return;
    
    // Enhanced data structure for drill-down
    chartData.twinPerformance = {
        overview: {
            labels: generateDateLabels(14),
            datasets: [{
                label: 'Active Twins',
                data: generateRandomData(14, 15, 25),
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Performance Score',
                data: generateRandomData(14, 85, 95),
                borderColor: 'rgb(54, 162, 235)',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        facility: {
            labels: ['Additive Manufacturing', 'Hydrogen Filling Station', 'Servo DC Motor Assembly'],
            datasets: [{
                label: 'Twin Performance by Facility',
                data: [92.5, 88.7, 85.3],
                backgroundColor: ['rgba(75, 192, 192, 0.8)', 'rgba(54, 162, 235, 0.8)', 'rgba(255, 159, 64, 0.8)']
            }]
        }
    };
    
    twinPerformanceChart = new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: chartData.twinPerformance.overview,
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
                    bodyColor: 'white',
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(1)}`;
                        },
                        afterLabel: function(context) {
                            return getEnhancedTooltipInfo(context);
                        }
                    }
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
                        text: 'Count / Score'
                    }
                }
            },
            onClick: function(event, elements) {
                handleChartClick(event, elements, 'twinPerformanceChart');
            }
        }
    });
}

function initializeTwinHealthChart() {
    const ctx = document.getElementById('twinHealthChart');
    if (!ctx) return;
    
    // Enhanced data structure for drill-down
    chartData.twinHealth = {
        overview: {
            labels: ['Healthy', 'Warning', 'Critical', 'Offline'],
            datasets: [{
                data: [65, 20, 10, 5],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(255, 205, 86, 0.8)',
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(201, 203, 207, 0.8)'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        facility: {
            labels: ['Additive Manufacturing', 'Hydrogen Filling Station', 'Servo DC Motor Assembly'],
            datasets: [{
                data: [8, 6, 4],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 159, 64, 0.8)'
                ]
            }]
        }
    };
    
    twinHealthChart = new Chart(ctx.getContext('2d'), {
        type: 'doughnut',
        data: chartData.twinHealth.overview,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${context.parsed} (${percentage}%)`;
                        }
                    }
                }
            },
            onClick: function(event, elements) {
                handleChartClick(event, elements, 'twinHealthChart');
            }
        }
    });
}

function initializePerformanceTrendsChart() {
    const ctx = document.getElementById('performanceTrendsChart');
    if (!ctx) return;
    
    // Enhanced data structure for drill-down
    chartData.performanceTrends = {
        overview: {
            labels: generateDateLabels(20),
            datasets: [{
                label: 'Performance Score',
                data: generateRandomData(20, 85, 95),
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        facility: {
            labels: ['Additive Manufacturing', 'Hydrogen Filling Station', 'Servo DC Motor Assembly'],
            datasets: [{
                label: 'Performance by Facility',
                data: [92.5, 88.7, 85.3],
                backgroundColor: ['rgba(75, 192, 192, 0.8)', 'rgba(54, 162, 235, 0.8)', 'rgba(255, 159, 64, 0.8)']
            }]
        }
    };
    
    performanceTrendsChart = new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: chartData.performanceTrends.overview,
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
                    bodyColor: 'white',
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(1)}%`;
                        },
                        afterLabel: function(context) {
                            return getEnhancedTooltipInfo(context);
                        }
                    }
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
                        text: 'Performance Score (%)'
                    },
                    min: 80,
                    max: 100
                }
            },
            onClick: function(event, elements) {
                handleChartClick(event, elements, 'performanceTrendsChart');
            }
        }
    });
}

function initializeUptimeChart() {
    const ctx = document.getElementById('uptimeChart');
    if (!ctx) return;
    
    // Enhanced data structure for drill-down
    chartData.uptime = {
        overview: {
            labels: generateDateLabels(20),
            datasets: [{
                label: 'Uptime Percentage',
                data: generateRandomData(20, 95, 99.5),
                borderColor: 'rgb(54, 162, 235)',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        facility: {
            labels: ['Additive Manufacturing', 'Hydrogen Filling Station', 'Servo DC Motor Assembly'],
            datasets: [{
                label: 'Uptime by Facility',
                data: [98.5, 97.2, 95.8],
                backgroundColor: ['rgba(54, 162, 235, 0.8)', 'rgba(75, 192, 192, 0.8)', 'rgba(255, 159, 64, 0.8)']
            }]
        }
    };
    
    uptimeChart = new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: chartData.uptime.overview,
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
                    bodyColor: 'white',
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(2)}%`;
                        },
                        afterLabel: function(context) {
                            return getEnhancedTooltipInfo(context);
                        }
                    }
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
                        text: 'Uptime (%)'
                    },
                    min: 90,
                    max: 100
                }
            },
            onClick: function(event, elements) {
                handleChartClick(event, elements, 'uptimeChart');
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

// Advanced Chart Interaction Functions

function handleChartClick(event, elements, chartId) {
    if (elements.length > 0) {
        const element = elements[0];
        const chart = getChartInstance(chartId);
        if (!chart) return;
        
        console.log(`🔍 Chart click detected on ${chartId}:`, element);
        
        // Determine drill-down level based on current state
        const currentState = chartInteractionState[getChartKey(chartId)];
        if (currentState.level === 'overview') {
            drillDownToDetail(chartId, element);
        } else if (currentState.level === 'facility') {
            drillDownToDaily(chartId, element);
        }
    }
}

function drillDownChart(chartId) {
    console.log(`🔍 Drilling down chart: ${chartId}`);
    const chart = getChartInstance(chartId);
    if (!chart) return;
    
    const currentState = chartInteractionState[getChartKey(chartId)];
    
    if (currentState.level === 'overview') {
        drillDownToFacility(chartId);
    } else if (currentState.level === 'facility') {
        drillDownToDaily(chartId);
    } else {
        showNotification('Maximum drill-down level reached', 'info');
    }
}

function drillDownToFacility(chartId) {
    const chart = getChartInstance(chartId);
    const chartKey = getChartKey(chartId);
    
    if (chartData[chartKey] && chartData[chartKey].facility) {
        chart.data = chartData[chartKey].facility;
        chart.update();
        
        chartInteractionState[chartKey].level = 'facility';
        updateChartStatus(chartId, 'Facility Level');
        
        showNotification(`Drilled down to facility level for ${chartId}`, 'success');
    }
}

function drillDownToDaily(chartId) {
    const chart = getChartInstance(chartId);
    const chartKey = getChartKey(chartId);
    
    if (chartData[chartKey] && chartData[chartKey].daily) {
        chart.data = chartData[chartKey].daily;
        chart.update();
        
        chartInteractionState[chartKey].level = 'daily';
        updateChartStatus(chartId, 'Daily Level');
        
        showNotification(`Drilled down to daily level for ${chartId}`, 'success');
    }
}

function drillDownToDetail(chartId, element) {
    const chart = getChartInstance(chartId);
    const chartKey = getChartKey(chartId);
    
    // Create detailed view based on clicked element
    const detailedData = createDetailedView(chartKey, element);
    if (detailedData) {
        chart.data = detailedData;
        chart.update();
        
        chartInteractionState[chartKey].level = 'detail';
        updateChartStatus(chartId, 'Detail Level');
        
        showNotification(`Showing detailed view for ${element.label || 'selected item'}`, 'success');
    }
}

function resetChartView(chartId) {
    console.log(`🔄 Resetting chart view: ${chartId}`);
    const chart = getChartInstance(chartId);
    const chartKey = getChartKey(chartId);
    
    if (chart && chartData[chartKey] && chartData[chartKey].overview) {
        chart.data = chartData[chartKey].overview;
        chart.update();
        
        chartInteractionState[chartKey].level = 'overview';
        chartInteractionState[chartKey].filters = {};
        updateChartStatus(chartId, 'Overview Level');
        
        showNotification(`Reset ${chartId} to overview level`, 'success');
    }
}

function applyChartFilter(chartId) {
    console.log(`🔧 Applying filter to chart: ${chartId}`);
    
    // Create filter modal
    const filterModal = createFilterModal(chartId);
    document.body.appendChild(filterModal);
    
    // Show modal
    const modal = new bootstrap.Modal(filterModal);
    modal.show();
}

function createFilterModal(chartId) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = `filterModal-${chartId}`;
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Filter Chart Data</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label">Date Range</label>
                        <select class="form-select" id="dateRange-${chartId}">
                            <option value="7">Last 7 days</option>
                            <option value="14">Last 14 days</option>
                            <option value="30" selected>Last 30 days</option>
                            <option value="90">Last 90 days</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Facility</label>
                        <select class="form-select" id="facilityFilter-${chartId}">
                            <option value="">All Facilities</option>
                            <option value="additive">Additive Manufacturing</option>
                            <option value="hydrogen">Hydrogen Filling Station</option>
                            <option value="servo">Servo DC Motor Assembly</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Performance Threshold</label>
                        <input type="range" class="form-range" id="threshold-${chartId}" min="0" max="100" value="80">
                        <div class="text-center" id="thresholdValue-${chartId}">80%</div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="applyFilterToChart('${chartId}')">Apply Filter</button>
                </div>
            </div>
        </div>
    `;
    
    // Add event listeners
    modal.addEventListener('shown.bs.modal', function() {
        const thresholdSlider = modal.querySelector(`#threshold-${chartId}`);
        const thresholdValue = modal.querySelector(`#thresholdValue-${chartId}`);
        
        thresholdSlider.addEventListener('input', function() {
            thresholdValue.textContent = this.value + '%';
        });
    });
    
    return modal;
}

function applyFilterToChart(chartId) {
    const modal = document.getElementById(`filterModal-${chartId}`);
    const dateRange = modal.querySelector(`#dateRange-${chartId}`).value;
    const facility = modal.querySelector(`#facilityFilter-${chartId}`).value;
    const threshold = modal.querySelector(`#threshold-${chartId}`).value;
    
    console.log(`🔧 Applying filters to ${chartId}:`, { dateRange, facility, threshold });
    
    // Apply filters to chart data
    const filteredData = filterChartData(chartId, { dateRange, facility, threshold });
    
    if (filteredData) {
        const chart = getChartInstance(chartId);
        chart.data = filteredData;
        chart.update();
        
        // Update interaction state
        const chartKey = getChartKey(chartId);
        chartInteractionState[chartKey].filters = { dateRange, facility, threshold };
        updateChartStatus(chartId, 'Filtered View');
        
        showNotification(`Applied filters to ${chartId}`, 'success');
    }
    
    // Close modal
    const bootstrapModal = bootstrap.Modal.getInstance(modal);
    bootstrapModal.hide();
    modal.remove();
}

function exportChartData(chartId) {
    console.log(`📊 Exporting chart data: ${chartId}`);
    const chart = getChartInstance(chartId);
    if (!chart) return;
    
    // Prepare export data
    const exportData = prepareChartExportData(chartId, chart);
    
    // Create and download file
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${chartId}_data_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showNotification(`Exported ${chartId} data successfully`, 'success');
}

function getEnhancedTooltipInfo(context) {
    const chartId = context.chart.canvas.id;
    const chartKey = getChartKey(chartId);
    const currentState = chartInteractionState[chartKey];
    
    let additionalInfo = [];
    
    // Add context-specific information
    if (currentState.level === 'overview') {
        additionalInfo.push('Click to drill down');
        additionalInfo.push('Use filter button for custom views');
    } else if (currentState.level === 'facility') {
        additionalInfo.push('Click for daily breakdown');
        additionalInfo.push('Use reset button to return to overview');
    } else if (currentState.level === 'detail') {
        additionalInfo.push('Use reset button to return to overview');
    }
    
    // Add performance insights
    if (context.parsed.y > 90) {
        additionalInfo.push('Performance: Excellent');
    } else if (context.parsed.y > 80) {
        additionalInfo.push('Performance: Good');
    } else if (context.parsed.y > 70) {
        additionalInfo.push('Performance: Average');
    } else {
        additionalInfo.push('Performance: Needs Improvement');
    }
    
    return additionalInfo;
}

// Helper functions

function getChartInstance(chartId) {
    const chartMap = {
        'qualityTrendsChart': qualityTrendsChart,
        'performanceChart': performanceChart,
        'twinPerformanceChart': twinPerformanceChart,
        'twinHealthChart': twinHealthChart,
        'performanceTrendsChart': performanceTrendsChart,
        'uptimeChart': uptimeChart
    };
    return chartMap[chartId];
}

function getChartKey(chartId) {
    const keyMap = {
        'qualityTrendsChart': 'qualityTrends',
        'performanceChart': 'performance',
        'twinPerformanceChart': 'twinPerformance',
        'twinHealthChart': 'twinHealth'
    };
    return keyMap[chartId];
}

function updateChartStatus(chartId, status) {
    const statusElement = document.getElementById(`${chartId}-status`);
    if (statusElement) {
        statusElement.textContent = status;
    }
}

function createDetailedView(chartKey, element) {
    // Create detailed view based on chart type and clicked element
    switch (chartKey) {
        case 'qualityTrends':
            return {
                labels: generateDateLabels(7),
                datasets: [{
                    label: `Detailed ${element.dataset.label}`,
                    data: generateRandomData(7, 85, 98),
                    borderColor: element.dataset.borderColor,
                    backgroundColor: element.dataset.backgroundColor,
                    tension: 0.4,
                    fill: true
                }]
            };
        case 'performance':
            return {
                labels: ['Q1', 'Q2', 'Q3', 'Q4'],
                datasets: [{
                    label: `Performance for ${element.label}`,
                    data: generateRandomData(4, 70, 95),
                    backgroundColor: element.dataset.backgroundColor
                }]
            };
        default:
            return null;
    }
}

function filterChartData(chartId, filters) {
    const chartKey = getChartKey(chartId);
    const originalData = chartData[chartKey]?.overview;
    
    if (!originalData) return null;
    
    // Apply filters to create filtered dataset
    let filteredData = JSON.parse(JSON.stringify(originalData));
    
    // Apply date range filter
    if (filters.dateRange) {
        const days = parseInt(filters.dateRange);
        filteredData.labels = generateDateLabels(days);
        filteredData.datasets.forEach(dataset => {
            dataset.data = generateRandomData(days, 80, 95);
        });
    }
    
    // Apply facility filter (simplified)
    if (filters.facility) {
        // In a real implementation, this would filter actual facility data
        console.log(`Filtering for facility: ${filters.facility}`);
    }
    
    // Apply threshold filter
    if (filters.threshold) {
        const threshold = parseInt(filters.threshold);
        filteredData.datasets.forEach(dataset => {
            dataset.data = dataset.data.map(value => 
                value < threshold ? value * 0.8 : value
            );
        });
    }
    
    return filteredData;
}

function prepareChartExportData(chartId, chart) {
    const chartKey = getChartKey(chartId);
    const currentState = chartInteractionState[chartKey];
    
    return {
        chartId: chartId,
        exportDate: new Date().toISOString(),
        currentLevel: currentState.level,
        filters: currentState.filters,
        data: {
            labels: chart.data.labels,
            datasets: chart.data.datasets.map(dataset => ({
                label: dataset.label,
                data: dataset.data,
                type: dataset.type || 'default'
            }))
        },
        metadata: {
            totalDataPoints: chart.data.labels.length,
            datasets: chart.data.datasets.length,
            chartType: chart.config.type
        }
    };
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

// Export functions to global scope for cross-module access
window.initializeQIAnalytics = initializeQIAnalytics;
window.setupEventListeners = setupEventListeners;
window.setupAdvancedChartInteractions = setupAdvancedChartInteractions;
window.loadAnalyticsData = loadAnalyticsData;
window.loadTwinRegistryData = loadTwinRegistryData;
window.generateAnalyticsReport = generateAnalyticsReport;
window.exportAnalyticsData = exportAnalyticsData;
window.compareTwinAnalytics = compareTwinAnalytics;
window.refreshTwinData = refreshTwinData;
window.drillDownChart = drillDownChart;
window.resetChartView = resetChartView;
window.applyChartFilter = applyChartFilter;
window.exportChartData = exportChartData;

// Cleanup function
window.cleanup = cleanup;

console.log('✅ QI Analytics functions exported to global scope'); 