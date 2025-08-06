/**
 * Quality Intelligence Analytics Visualization Module
 * Handles charts, dashboards, and interactive visualizations
 */

export default class QIVisualization {
    constructor() {
        this.isInitialized = false;
        this.config = {
            apiBaseUrl: '/api/qi-analytics',
            containerId: 'qi-charts-container',
            width: 800,
            height: 600,
            theme: 'light',
            colors: {
                primary: '#1f77b4',
                secondary: '#ff7f0e',
                success: '#2ca02c',
                warning: '#d62728',
                danger: '#9467bd',
                info: '#8c564b',
                light: '#e377c2',
                dark: '#7f7f7f'
            },
            chartTypes: ['line', 'bar', 'pie', 'scatter', 'area', 'heatmap', 'gauge', 'funnel'],
            animationEnabled: true,
            responsiveEnabled: true,
            exportEnabled: true,
            realtimeEnabled: true,
            updateInterval: 5000
        };

        this.charts = new Map();
        this.dashboards = new Map();
        this.templates = new Map();
        this.themes = new Map();
        this.animations = {};
        this.exporters = new Map();
        this.realtimeConnections = new Map();
        this.eventListeners = new Map();
    }

    /**
     * Initialize the Visualization
     */
    async init() {
        console.log('🔧 Initializing Quality Intelligence Visualization...');

        try {
            // Load configuration
            await this.loadConfiguration();

            // Initialize chart library
            this.initializeChartLibrary();

            // Initialize themes
            this.initializeThemes();

            // Initialize templates
            this.initializeTemplates();

            // Initialize animations
            this.initializeAnimations();

            // Initialize exporters
            this.initializeExporters();

            // Initialize realtime connections
            if (this.config.realtimeEnabled) {
                this.initializeRealtimeConnections();
            }

            // Set up event listeners
            this.setupEventListeners();

            this.isInitialized = true;
            console.log('✅ Quality Intelligence Visualization initialized');

        } catch (error) {
            console.error('❌ Quality Intelligence Visualization initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load configuration from server
     */
    async loadConfiguration() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/visualization-config`);
            if (response.ok) {
                const config = await response.json();
                this.config = { ...this.config, ...config };
            }
        } catch (error) {
            console.warn('Could not load visualization configuration from server, using defaults:', error);
        }
    }

    /**
     * Initialize chart library
     */
    initializeChartLibrary() {
        // Check if Chart.js is available
        if (typeof Chart === 'undefined') {
            console.warn('Chart.js not found. Please include Chart.js library.');
            return;
        }

        // Set global Chart.js configuration
        Chart.defaults.font.family = 'Arial, sans-serif';
        Chart.defaults.font.size = 12;
        Chart.defaults.color = '#333333';
        Chart.defaults.responsive = this.config.responsiveEnabled;
        Chart.defaults.animation = this.config.animationEnabled;
    }

    /**
     * Initialize themes
     */
    initializeThemes() {
        // Light theme
        this.themes.set('light', {
            backgroundColor: '#ffffff',
            textColor: '#333333',
            gridColor: '#e0e0e0',
            borderColor: '#cccccc',
            colors: [
                '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
            ]
        });

        // Dark theme
        this.themes.set('dark', {
            backgroundColor: '#1a1a1a',
            textColor: '#ffffff',
            gridColor: '#404040',
            borderColor: '#666666',
            colors: [
                '#4fc3f7', '#ffb74d', '#81c784', '#e57373', '#ba68c8',
                '#ff8a65', '#f06292', '#a1887f', '#d4e157', '#4dd0e1'
            ]
        });

        // Corporate theme
        this.themes.set('corporate', {
            backgroundColor: '#f8f9fa',
            textColor: '#495057',
            gridColor: '#dee2e6',
            borderColor: '#adb5bd',
            colors: [
                '#007bff', '#6c757d', '#28a745', '#dc3545', '#ffc107',
                '#17a2b8', '#6f42c1', '#fd7e14', '#20c997', '#e83e8c'
            ]
        });
    }

    /**
     * Initialize templates
     */
    initializeTemplates() {
        // Line chart template
        this.templates.set('line', {
            type: 'line',
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Line Chart'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        // Bar chart template
        this.templates.set('bar', {
            type: 'bar',
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Bar Chart'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        // Pie chart template
        this.templates.set('pie', {
            type: 'pie',
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Pie Chart'
                    }
                }
            }
        });

        // Scatter chart template
        this.templates.set('scatter', {
            type: 'scatter',
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Scatter Chart'
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom'
                    }
                }
            }
        });

        // Area chart template
        this.templates.set('area', {
            type: 'line',
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Area Chart'
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

    /**
     * Initialize animations
     */
    initializeAnimations() {
        this.animations = {
            // Fade in animation
            fadeIn: {
                duration: 1000,
                easing: 'easeInOut',
                from: { opacity: 0 },
                to: { opacity: 1 }
            },

            // Slide in animation
            slideIn: {
                duration: 800,
                easing: 'easeOut',
                from: { transform: 'translateX(-100%)' },
                to: { transform: 'translateX(0)' }
            },

            // Scale in animation
            scaleIn: {
                duration: 600,
                easing: 'easeOut',
                from: { transform: 'scale(0.8)', opacity: 0 },
                to: { transform: 'scale(1)', opacity: 1 }
            },

            // Bounce animation
            bounce: {
                duration: 1200,
                easing: 'easeOut',
                keyframes: [
                    { offset: 0, transform: 'scale(0.3)', opacity: 0 },
                    { offset: 0.5, transform: 'scale(1.05)' },
                    { offset: 0.7, transform: 'scale(0.9)' },
                    { offset: 1, transform: 'scale(1)', opacity: 1 }
                ]
            }
        };
    }

    /**
     * Initialize exporters
     */
    initializeExporters() {
        // PNG exporter
        this.exporters.set('png', {
            export: (chart) => {
                return chart.toBase64Image('image/png', 1.0);
            },
            mimeType: 'image/png',
            extension: 'png'
        });

        // JPEG exporter
        this.exporters.set('jpeg', {
            export: (chart) => {
                return chart.toBase64Image('image/jpeg', 0.8);
            },
            mimeType: 'image/jpeg',
            extension: 'jpg'
        });

        // PDF exporter
        this.exporters.set('pdf', {
            export: async (chart) => {
                // This would require a PDF library like jsPDF
                console.warn('PDF export requires jsPDF library');
                return null;
            },
            mimeType: 'application/pdf',
            extension: 'pdf'
        });

        // SVG exporter
        this.exporters.set('svg', {
            export: (chart) => {
                return chart.toBase64Image('image/svg+xml', 1.0);
            },
            mimeType: 'image/svg+xml',
            extension: 'svg'
        });
    }

    /**
     * Initialize realtime connections
     */
    initializeRealtimeConnections() {
        // Set up WebSocket connections for real-time chart updates
        const wsUrl = this.config.apiBaseUrl.replace('http', 'ws') + '/realtime';
        
        try {
            const ws = new WebSocket(wsUrl);
            
            ws.onopen = () => {
                console.log('QI Visualization realtime connection established');
                this.realtimeConnections.set('main', ws);
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleRealtimeData(data);
            };
            
            ws.onerror = (error) => {
                console.error('QI Visualization realtime connection error:', error);
            };
            
            ws.onclose = () => {
                console.log('QI Visualization realtime connection closed');
                this.realtimeConnections.delete('main');
                
                // Attempt to reconnect
                setTimeout(() => {
                    this.initializeRealtimeConnections();
                }, 5000);
            };
        } catch (error) {
            console.error('Failed to setup realtime connection:', error);
        }
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Listen for data updates
        window.addEventListener('qiDataRefreshed', (event) => {
            this.updateCharts(event.detail.data);
        });

        // Listen for metric updates
        window.addEventListener('qiMetricRealtimeUpdate', (event) => {
            this.updateChartData(event.detail.metricId, event.detail.value, event.detail.timestamp);
        });

        // Listen for KPI updates
        window.addEventListener('qiKPIRealtimeUpdate', (event) => {
            this.updateKPIChart(event.detail.kpiId, event.detail.value, event.detail.timestamp);
        });
    }

    /**
     * Create a chart
     */
    createChart(containerId, type, data, options = {}) {
        if (!this.isInitialized) {
            console.warn('Visualization not initialized');
            return null;
        }

        const container = document.getElementById(containerId);
        if (!container) {
            throw new Error(`Container with ID '${containerId}' not found`);
        }

        // Get template
        const template = this.templates.get(type);
        if (!template) {
            throw new Error(`Chart type '${type}' not supported`);
        }

        // Merge options
        const chartOptions = this.mergeOptions(template.options, options);

        // Create canvas
        const canvas = document.createElement('canvas');
        container.appendChild(canvas);

        // Create chart
        const chart = new Chart(canvas, {
            type: template.type,
            data: this.prepareChartData(data, type),
            options: chartOptions
        });

        // Store chart reference
        this.charts.set(containerId, {
            chart,
            type,
            data,
            options: chartOptions,
            container
        });

        // Apply animation
        if (this.config.animationEnabled) {
            this.applyAnimation(container, 'fadeIn');
        }

        // Dispatch event
        window.dispatchEvent(new CustomEvent('qiChartCreated', {
            detail: { containerId, type, chart }
        }));

        return chart;
    }

    /**
     * Update chart data
     */
    updateChartData(containerId, newData, animate = true) {
        const chartInfo = this.charts.get(containerId);
        if (!chartInfo) {
            console.warn(`Chart with container ID '${containerId}' not found`);
            return;
        }

        const { chart, type } = chartInfo;

        // Update data
        chart.data = this.prepareChartData(newData, type);
        chartInfo.data = newData;

        // Update chart
        if (animate) {
            chart.update('active');
        } else {
            chart.update('none');
        }

        // Dispatch event
        window.dispatchEvent(new CustomEvent('qiChartUpdated', {
            detail: { containerId, data: newData }
        }));
    }

    /**
     * Update specific chart data point
     */
    updateChartDataPoint(containerId, datasetIndex, index, value) {
        const chartInfo = this.charts.get(containerId);
        if (!chartInfo) {
            console.warn(`Chart with container ID '${containerId}' not found`);
            return;
        }

        const { chart } = chartInfo;

        // Update data point
        if (chart.data.datasets[datasetIndex] && chart.data.datasets[datasetIndex].data[index] !== undefined) {
            chart.data.datasets[datasetIndex].data[index] = value;
            chart.update('active');
        }
    }

    /**
     * Add data point to chart
     */
    addDataPoint(containerId, datasetIndex, label, value) {
        const chartInfo = this.charts.get(containerId);
        if (!chartInfo) {
            console.warn(`Chart with container ID '${containerId}' not found`);
            return;
        }

        const { chart } = chartInfo;

        // Add label if not exists
        if (!chart.data.labels.includes(label)) {
            chart.data.labels.push(label);
        }

        // Add data point
        if (chart.data.datasets[datasetIndex]) {
            chart.data.datasets[datasetIndex].data.push(value);
            chart.update('active');
        }
    }

    /**
     * Remove data point from chart
     */
    removeDataPoint(containerId, index) {
        const chartInfo = this.charts.get(containerId);
        if (!chartInfo) {
            console.warn(`Chart with container ID '${containerId}' not found`);
            return;
        }

        const { chart } = chartInfo;

        // Remove label
        if (chart.data.labels[index]) {
            chart.data.labels.splice(index, 1);
        }

        // Remove data from all datasets
        chart.data.datasets.forEach(dataset => {
            if (dataset.data[index] !== undefined) {
                dataset.data.splice(index, 1);
            }
        });

        chart.update('active');
    }

    /**
     * Create dashboard
     */
    createDashboard(containerId, layout, charts = []) {
        const container = document.getElementById(containerId);
        if (!container) {
            throw new Error(`Container with ID '${containerId}' not found`);
        }

        // Clear container
        container.innerHTML = '';

        // Create dashboard layout
        const dashboard = this.createDashboardLayout(container, layout);

        // Create charts
        charts.forEach(chartConfig => {
            const chartContainer = document.createElement('div');
            chartContainer.id = chartConfig.id;
            chartContainer.className = 'dashboard-chart';
            chartContainer.style.gridArea = chartConfig.position;
            
            dashboard.appendChild(chartContainer);
            
            this.createChart(chartConfig.id, chartConfig.type, chartConfig.data, chartConfig.options);
        });

        // Store dashboard reference
        this.dashboards.set(containerId, {
            container,
            layout,
            charts: charts.map(c => c.id)
        });

        // Apply animation
        if (this.config.animationEnabled) {
            this.applyAnimation(container, 'scaleIn');
        }

        return dashboard;
    }

    /**
     * Create dashboard layout
     */
    createDashboardLayout(container, layout) {
        const dashboard = document.createElement('div');
        dashboard.className = 'dashboard';
        dashboard.style.display = 'grid';
        dashboard.style.gap = '20px';
        dashboard.style.padding = '20px';
        dashboard.style.height = '100%';

        // Apply grid layout
        if (layout.grid) {
            dashboard.style.gridTemplateColumns = layout.grid.columns || 'repeat(auto-fit, minmax(300px, 1fr))';
            dashboard.style.gridTemplateRows = layout.grid.rows || 'auto';
        }

        container.appendChild(dashboard);
        return dashboard;
    }

    /**
     * Prepare chart data
     */
    prepareChartData(data, type) {
        const theme = this.themes.get(this.config.theme);
        
        switch (type) {
            case 'line':
            case 'area':
                return {
                    labels: data.labels || [],
                    datasets: data.datasets.map((dataset, index) => ({
                        label: dataset.label,
                        data: dataset.data,
                        borderColor: dataset.color || theme.colors[index % theme.colors.length],
                        backgroundColor: type === 'area' ? 
                            this.hexToRgba(dataset.color || theme.colors[index % theme.colors.length], 0.2) : 
                            'transparent',
                        borderWidth: 2,
                        fill: type === 'area',
                        tension: 0.4
                    }))
                };

            case 'bar':
                return {
                    labels: data.labels || [],
                    datasets: data.datasets.map((dataset, index) => ({
                        label: dataset.label,
                        data: dataset.data,
                        backgroundColor: dataset.color || theme.colors[index % theme.colors.length],
                        borderColor: dataset.borderColor || theme.borderColor,
                        borderWidth: 1
                    }))
                };

            case 'pie':
            case 'doughnut':
                return {
                    labels: data.labels || [],
                    datasets: [{
                        data: data.values || [],
                        backgroundColor: data.colors || theme.colors,
                        borderColor: theme.borderColor,
                        borderWidth: 1
                    }]
                };

            case 'scatter':
                return {
                    datasets: data.datasets.map((dataset, index) => ({
                        label: dataset.label,
                        data: dataset.data,
                        backgroundColor: dataset.color || theme.colors[index % theme.colors.length],
                        borderColor: dataset.borderColor || theme.borderColor,
                        pointRadius: dataset.pointRadius || 6,
                        pointHoverRadius: dataset.pointHoverRadius || 8
                    }))
                };

            default:
                return data;
        }
    }

    /**
     * Merge options
     */
    mergeOptions(templateOptions, customOptions) {
        const theme = this.themes.get(this.config.theme);
        
        return {
            ...templateOptions,
            ...customOptions,
            plugins: {
                ...templateOptions.plugins,
                ...customOptions.plugins
            },
            scales: {
                ...templateOptions.scales,
                ...customOptions.scales
            }
        };
    }

    /**
     * Apply animation
     */
    applyAnimation(element, animationType) {
        const animation = this.animations[animationType];
        if (!animation) return;

        if (animation.keyframes) {
            // Keyframe animation
            element.animate(animation.keyframes, {
                duration: animation.duration,
                easing: animation.easing
            });
        } else {
            // Simple animation
            element.style.transition = `all ${animation.duration}ms ${animation.easing}`;
            Object.assign(element.style, animation.from);
            
            requestAnimationFrame(() => {
                Object.assign(element.style, animation.to);
            });
        }
    }

    /**
     * Handle realtime data
     */
    handleRealtimeData(data) {
        switch (data.type) {
            case 'chart_update':
                this.updateChartData(data.chartId, data.data, true);
                break;
            case 'chart_add_point':
                this.addDataPoint(data.chartId, data.datasetIndex, data.label, data.value);
                break;
            case 'chart_remove_point':
                this.removeDataPoint(data.chartId, data.index);
                break;
            default:
                console.log('Unknown realtime data type:', data.type);
        }
    }

    /**
     * Export chart
     */
    exportChart(containerId, format = 'png') {
        const chartInfo = this.charts.get(containerId);
        if (!chartInfo) {
            throw new Error(`Chart with container ID '${containerId}' not found`);
        }

        const exporter = this.exporters.get(format);
        if (!exporter) {
            throw new Error(`Export format '${format}' not supported`);
        }

        const { chart } = chartInfo;
        const dataUrl = exporter.export(chart);
        
        if (dataUrl) {
            // Create download link
            const link = document.createElement('a');
            link.download = `chart.${exporter.extension}`;
            link.href = dataUrl;
            link.click();
        }

        return dataUrl;
    }

    /**
     * Set theme
     */
    setTheme(themeName) {
        if (!this.themes.has(themeName)) {
            throw new Error(`Theme '${themeName}' not found`);
        }

        this.config.theme = themeName;
        
        // Update all charts with new theme
        for (const [containerId, chartInfo] of this.charts) {
            const theme = this.themes.get(themeName);
            const { chart, data, type } = chartInfo;
            
            chart.data = this.prepareChartData(data, type);
            chart.update('none');
        }
    }

    /**
     * Get chart instance
     */
    getChart(containerId) {
        const chartInfo = this.charts.get(containerId);
        return chartInfo ? chartInfo.chart : null;
    }

    /**
     * Destroy chart
     */
    destroyChart(containerId) {
        const chartInfo = this.charts.get(containerId);
        if (chartInfo) {
            chartInfo.chart.destroy();
            this.charts.delete(containerId);
            
            // Dispatch event
            window.dispatchEvent(new CustomEvent('qiChartDestroyed', {
                detail: { containerId }
            }));
        }
    }

    /**
     * Refresh charts
     */
    async refreshCharts() {
        try {
            // Update all charts with latest data
            for (const [containerId, chartInfo] of this.charts) {
                const { chart, data, type } = chartInfo;
                chart.data = this.prepareChartData(data, type);
                chart.update('none');
            }
            
            console.log('Charts refreshed');
        } catch (error) {
            console.error('Charts refresh failed:', error);
            throw error;
        }
    }

    /**
     * Utility function to convert hex to rgba
     */
    hexToRgba(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    /**
     * Destroy the visualization
     */
    destroy() {
        this.isInitialized = false;
        
        // Destroy all charts
        for (const [containerId, chartInfo] of this.charts) {
            chartInfo.chart.destroy();
        }
        this.charts.clear();
        
        // Close realtime connections
        for (const [key, connection] of this.realtimeConnections) {
            if (connection && connection.readyState === WebSocket.OPEN) {
                connection.close();
            }
        }
        this.realtimeConnections.clear();
        
        this.dashboards.clear();
        this.templates.clear();
        this.themes.clear();
        this.animations = {};
        this.exporters.clear();
        this.eventListeners.clear();
        
        console.log('🧹 Quality Intelligence Visualization destroyed');
    }
} 