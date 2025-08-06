/**
 * Advanced Charts Module
 * Handles 2D visualization of physics simulation data using Chart.js
 */

import PhysicsModelingAPI from '../../shared/api.js';
import PhysicsModelingUtils from '../../shared/utils.js';

class PhysicsCharts {
    constructor() {
        this.charts = new Map();
        this.chartConfigs = new Map();
        this.dataSources = new Map();
        this.updateIntervals = new Map();
        this.isInitialized = false;
        
        this.api = new PhysicsModelingAPI();
        this.utils = new PhysicsModelingUtils();
        
        // Chart.js configuration defaults
        this.defaultConfig = {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 750,
                easing: 'easeInOutQuart'
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#666',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    display: true,
                    title: {
                        display: true,
                        text: 'Time (s)'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Value'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        };
        
        this.init();
    }

    /**
     * Initialize the charts module
     */
    async init() {
        try {
            console.log('Initializing Physics Charts...');
            
            // Check if Chart.js is available
            if (typeof Chart === 'undefined') {
                throw new Error('Chart.js is not loaded. Please include Chart.js in your HTML.');
            }
            
            // Set global Chart.js defaults
            this.setGlobalDefaults();
            
            this.isInitialized = true;
            console.log('Physics Charts initialized successfully');
            
        } catch (error) {
            console.error('Error initializing Physics Charts:', error);
            this.utils.handleError(error, 'PhysicsCharts.init');
        }
    }

    /**
     * Set global Chart.js defaults
     */
    setGlobalDefaults() {
        Chart.defaults.font.family = "'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
        Chart.defaults.font.size = 12;
        Chart.defaults.color = '#666';
        Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
    }

    /**
     * Create a new chart
     */
    createChart(containerId, type = 'line', config = {}) {
        try {
            const container = document.getElementById(containerId);
            if (!container) {
                throw new Error(`Container with ID '${containerId}' not found`);
            }

            // Create canvas if it doesn't exist
            let canvas = container.querySelector('canvas');
            if (!canvas) {
                canvas = document.createElement('canvas');
                container.appendChild(canvas);
            }

            // Merge configuration
            const chartConfig = this.mergeConfig(this.defaultConfig, config);
            chartConfig.type = type;

            // Create chart
            const chart = new Chart(canvas, chartConfig);
            
            // Store chart reference
            this.charts.set(containerId, chart);
            this.chartConfigs.set(containerId, chartConfig);
            
            console.log(`Chart created: ${containerId} (${type})`);
            return chart;
            
        } catch (error) {
            console.error('Error creating chart:', error);
            this.utils.handleError(error, 'PhysicsCharts.createChart');
            return null;
        }
    }

    /**
     * Create a time series chart for simulation data
     */
    createTimeSeriesChart(containerId, title = 'Simulation Results') {
        const config = {
            data: {
                datasets: []
            },
            options: {
                plugins: {
                    title: {
                        display: true,
                        text: title,
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        display: true,
                        title: {
                            display: true,
                            text: 'Time (s)'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Value'
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        };

        return this.createChart(containerId, 'line', config);
    }

    /**
     * Create a scatter plot for parameter analysis
     */
    createScatterChart(containerId, title = 'Parameter Analysis') {
        const config = {
            data: {
                datasets: []
            },
            options: {
                plugins: {
                    title: {
                        display: true,
                        text: title,
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        display: true,
                        title: {
                            display: true,
                            text: 'X Parameter'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Y Parameter'
                        }
                    }
                }
            }
        };

        return this.createChart(containerId, 'scatter', config);
    }

    /**
     * Create a bar chart for comparison data
     */
    createBarChart(containerId, title = 'Comparison Results') {
        const config = {
            data: {
                labels: [],
                datasets: []
            },
            options: {
                plugins: {
                    title: {
                        display: true,
                        text: title,
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'category',
                        display: true
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Value'
                        }
                    }
                }
            }
        };

        return this.createChart(containerId, 'bar', config);
    }

    /**
     * Create a heatmap chart for 2D data
     */
    createHeatmapChart(containerId, title = '2D Heatmap') {
        const config = {
            data: {
                datasets: [{
                    label: 'Heatmap',
                    data: [],
                    backgroundColor: (context) => {
                        const value = context.dataset.data[context.dataIndex]?.v;
                        if (value === undefined) return 'rgba(0, 0, 0, 0)';
                        
                        // Create color gradient based on value
                        const normalized = (value - this.minValue) / (this.maxValue - this.minValue);
                        const hue = (1 - normalized) * 240; // Blue to Red
                        return `hsl(${hue}, 70%, 50%)`;
                    }
                }]
            },
            options: {
                plugins: {
                    title: {
                        display: true,
                        text: title,
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const value = context.dataset.data[context.dataIndex]?.v;
                                return `Value: ${value?.toFixed(3) || 'N/A'}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        display: true,
                        title: {
                            display: true,
                            text: 'X Position'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Y Position'
                        }
                    }
                }
            }
        };

        return this.createChart(containerId, 'scatter', config);
    }

    /**
     * Add dataset to chart
     */
    addDataset(containerId, dataset) {
        const chart = this.charts.get(containerId);
        if (!chart) {
            console.error(`Chart not found: ${containerId}`);
            return;
        }

        // Generate color if not provided
        if (!dataset.borderColor) {
            dataset.borderColor = this.generateColor(chart.data.datasets.length);
        }
        if (!dataset.backgroundColor) {
            dataset.backgroundColor = this.generateColor(chart.data.datasets.length, 0.2);
        }

        chart.data.datasets.push(dataset);
        chart.update('active');
    }

    /**
     * Update chart data
     */
    updateChartData(containerId, data) {
        const chart = this.charts.get(containerId);
        if (!chart) {
            console.error(`Chart not found: ${containerId}`);
            return;
        }

        if (data.datasets) {
            chart.data.datasets = data.datasets;
        }
        if (data.labels) {
            chart.data.labels = data.labels;
        }

        chart.update('active');
    }

    /**
     * Add data point to chart
     */
    addDataPoint(containerId, datasetIndex, x, y) {
        const chart = this.charts.get(containerId);
        if (!chart || !chart.data.datasets[datasetIndex]) {
            console.error(`Chart or dataset not found: ${containerId}, ${datasetIndex}`);
            return;
        }

        chart.data.datasets[datasetIndex].data.push({ x, y });
        
        // Limit data points to prevent memory issues
        const maxPoints = 1000;
        if (chart.data.datasets[datasetIndex].data.length > maxPoints) {
            chart.data.datasets[datasetIndex].data.shift();
        }

        chart.update('none');
    }

    /**
     * Load simulation results into chart
     */
    async loadSimulationResults(containerId, simulationId) {
        try {
            this.utils.showProgress('Loading simulation results...');
            
            const results = await this.api.getSimulationResults(simulationId);
            
            if (!results.success) {
                throw new Error('Failed to load simulation results');
            }

            const chart = this.charts.get(containerId);
            if (!chart) {
                throw new Error(`Chart not found: ${containerId}`);
            }

            // Process simulation data
            const processedData = this.processSimulationData(results.data);
            
            // Update chart
            this.updateChartData(containerId, processedData);
            
            this.utils.hideProgress();
            this.utils.showSuccess('Simulation results loaded');
            
        } catch (error) {
            this.utils.hideProgress();
            console.error('Error loading simulation results:', error);
            this.utils.handleError(error, 'PhysicsCharts.loadSimulationResults');
        }
    }

    /**
     * Process simulation data for charting
     */
    processSimulationData(simulationData) {
        const datasets = [];
        const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'];
        
        // Process time series data
        if (simulationData.time_series) {
            simulationData.time_series.forEach((series, index) => {
                datasets.push({
                    label: series.name || `Series ${index + 1}`,
                    data: series.data.map((point, i) => ({
                        x: point.time || i,
                        y: point.value
                    })),
                    borderColor: colors[index % colors.length],
                    backgroundColor: colors[index % colors.length] + '20',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.1
                });
            });
        }

        // Process scalar results
        if (simulationData.scalar_results) {
            const scalarData = simulationData.scalar_results.map((result, index) => ({
                x: index,
                y: result.value
            }));
            
            datasets.push({
                label: 'Scalar Results',
                data: scalarData,
                borderColor: '#FF6384',
                backgroundColor: '#FF638420',
                borderWidth: 2,
                fill: false
            });
        }

        return { datasets };
    }

    /**
     * Start real-time data updates
     */
    startRealTimeUpdates(containerId, dataSource, interval = 1000) {
        if (this.updateIntervals.has(containerId)) {
            this.stopRealTimeUpdates(containerId);
        }

        const updateInterval = setInterval(async () => {
            try {
                const data = await this.fetchRealTimeData(dataSource);
                this.updateRealTimeData(containerId, data);
            } catch (error) {
                console.error('Error updating real-time data:', error);
            }
        }, interval);

        this.updateIntervals.set(containerId, updateInterval);
        this.dataSources.set(containerId, dataSource);
        
        console.log(`Real-time updates started for: ${containerId}`);
    }

    /**
     * Stop real-time data updates
     */
    stopRealTimeUpdates(containerId) {
        const interval = this.updateIntervals.get(containerId);
        if (interval) {
            clearInterval(interval);
            this.updateIntervals.delete(containerId);
            this.dataSources.delete(containerId);
            console.log(`Real-time updates stopped for: ${containerId}`);
        }
    }

    /**
     * Fetch real-time data from source
     */
    async fetchRealTimeData(dataSource) {
        // This would fetch data from various sources (WebSocket, API, etc.)
        // For now, return mock data
        return {
            timestamp: Date.now(),
            values: Math.random() * 100
        };
    }

    /**
     * Update chart with real-time data
     */
    updateRealTimeData(containerId, data) {
        const chart = this.charts.get(containerId);
        if (!chart || chart.data.datasets.length === 0) return;

        // Add new data point to first dataset
        const dataset = chart.data.datasets[0];
        dataset.data.push({
            x: data.timestamp,
            y: data.values
        });

        // Remove old data points (keep last 100)
        if (dataset.data.length > 100) {
            dataset.data.shift();
        }

        chart.update('none');
    }

    /**
     * Export chart as image
     */
    exportChart(containerId, format = 'png') {
        const chart = this.charts.get(containerId);
        if (!chart) {
            console.error(`Chart not found: ${containerId}`);
            return;
        }

        const canvas = chart.canvas;
        const link = document.createElement('a');
        link.download = `physics_chart_${Date.now()}.${format}`;
        link.href = canvas.toDataURL(`image/${format}`);
        link.click();
    }

    /**
     * Export chart data as CSV
     */
    exportChartData(containerId) {
        const chart = this.charts.get(containerId);
        if (!chart) {
            console.error(`Chart not found: ${containerId}`);
            return;
        }

        let csv = 'Dataset,Time,Value\n';
        
        chart.data.datasets.forEach((dataset, datasetIndex) => {
            dataset.data.forEach(point => {
                csv += `${dataset.label || `Dataset ${datasetIndex + 1}`},${point.x},${point.y}\n`;
            });
        });

        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `physics_chart_data_${Date.now()}.csv`;
        link.click();
        URL.revokeObjectURL(url);
    }

    /**
     * Clear chart data
     */
    clearChart(containerId) {
        const chart = this.charts.get(containerId);
        if (!chart) {
            console.error(`Chart not found: ${containerId}`);
            return;
        }

        chart.data.datasets.forEach(dataset => {
            dataset.data = [];
        });
        chart.data.labels = [];
        chart.update('active');
    }

    /**
     * Destroy chart
     */
    destroyChart(containerId) {
        const chart = this.charts.get(containerId);
        if (chart) {
            chart.destroy();
            this.charts.delete(containerId);
            this.chartConfigs.delete(containerId);
            this.stopRealTimeUpdates(containerId);
            console.log(`Chart destroyed: ${containerId}`);
        }
    }

    /**
     * Generate color for dataset
     */
    generateColor(index, alpha = 1) {
        const colors = [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
            '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
        ];
        
        const color = colors[index % colors.length];
        if (alpha === 1) return color;
        
        // Convert hex to rgba
        const r = parseInt(color.slice(1, 3), 16);
        const g = parseInt(color.slice(3, 5), 16);
        const b = parseInt(color.slice(5, 7), 16);
        
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    /**
     * Merge configuration objects
     */
    mergeConfig(defaultConfig, customConfig) {
        return JSON.parse(JSON.stringify({
            ...defaultConfig,
            ...customConfig,
            options: {
                ...defaultConfig.options,
                ...customConfig.options,
                plugins: {
                    ...defaultConfig.options?.plugins,
                    ...customConfig.options?.plugins
                },
                scales: {
                    ...defaultConfig.options?.scales,
                    ...customConfig.options?.scales
                }
            }
        }));
    }

    /**
     * Get chart instance
     */
    getChart(containerId) {
        return this.charts.get(containerId);
    }

    /**
     * Get all charts
     */
    getAllCharts() {
        return Array.from(this.charts.keys());
    }

    /**
     * Check if chart exists
     */
    hasChart(containerId) {
        return this.charts.has(containerId);
    }

    /**
     * Get chart configuration
     */
    getChartConfig(containerId) {
        return this.chartConfigs.get(containerId);
    }

    /**
     * Update chart options
     */
    updateChartOptions(containerId, options) {
        const chart = this.charts.get(containerId);
        if (!chart) {
            console.error(`Chart not found: ${containerId}`);
            return;
        }

        Object.assign(chart.options, options);
        chart.update('active');
    }

    /**
     * Resize chart
     */
    resizeChart(containerId) {
        const chart = this.charts.get(containerId);
        if (chart) {
            chart.resize();
        }
    }

    /**
     * Dispose of all charts
     */
    dispose() {
        this.charts.forEach((chart, containerId) => {
            this.destroyChart(containerId);
        });
        
        this.charts.clear();
        this.chartConfigs.clear();
        this.dataSources.clear();
        this.updateIntervals.clear();
        
        this.isInitialized = false;
        console.log('Physics Charts disposed');
    }
}

// Export the charts class
export default PhysicsCharts; 