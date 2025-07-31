/**
 * Custom Dashboard Builder
 * Phase 2.3: Analytics Integration - Custom Dashboard Creation
 */

console.log('🏗️ Dashboard Builder JS loaded');

// Dashboard state
let dashboardState = {
    isBuilderMode: false,
    widgets: [],
    layout: [],
    currentTemplate: null
};

// Widget configurations
const widgetConfigs = {
    'kpi-card': {
        name: 'KPI Card',
        icon: 'fas fa-chart-line',
        size: { w: 3, h: 2 },
        configurable: true,
        dataSource: 'kpi'
    },
    'line-chart': {
        name: 'Line Chart',
        icon: 'fas fa-chart-line',
        size: { w: 6, h: 4 },
        configurable: true,
        dataSource: 'trends'
    },
    'pie-chart': {
        name: 'Pie Chart',
        icon: 'fas fa-chart-pie',
        size: { w: 4, h: 4 },
        configurable: true,
        dataSource: 'distribution'
    },
    'bar-chart': {
        name: 'Bar Chart',
        icon: 'fas fa-chart-bar',
        size: { w: 6, h: 4 },
        configurable: true,
        dataSource: 'comparison'
    },
    'table': {
        name: 'Data Table',
        icon: 'fas fa-table',
        size: { w: 12, h: 6 },
        configurable: true,
        dataSource: 'tabular'
    },
    'gauge': {
        name: 'Gauge',
        icon: 'fas fa-tachometer-alt',
        size: { w: 3, h: 3 },
        configurable: true,
        dataSource: 'performance'
    }
};

// Dashboard templates
const dashboardTemplates = {
    'executive': {
        name: 'Executive Dashboard',
        description: 'High-level overview for executives',
        widgets: [
            { type: 'kpi-card', position: { x: 0, y: 0 }, config: { metric: 'overall_quality' } },
            { type: 'kpi-card', position: { x: 3, y: 0 }, config: { metric: 'compliance_rate' } },
            { type: 'kpi-card', position: { x: 6, y: 0 }, config: { metric: 'efficiency_index' } },
            { type: 'kpi-card', position: { x: 9, y: 0 }, config: { metric: 'risk_score' } },
            { type: 'line-chart', position: { x: 0, y: 2 }, config: { title: 'Quality Trends' } },
            { type: 'pie-chart', position: { x: 6, y: 2 }, config: { title: 'Performance Distribution' } }
        ]
    },
    'operational': {
        name: 'Operational Dashboard',
        description: 'Detailed operational metrics',
        widgets: [
            { type: 'line-chart', position: { x: 0, y: 0 }, config: { title: 'Daily Performance' } },
            { type: 'bar-chart', position: { x: 6, y: 0 }, config: { title: 'Facility Comparison' } },
            { type: 'table', position: { x: 0, y: 4 }, config: { title: 'Detailed Metrics' } },
            { type: 'gauge', position: { x: 9, y: 2 }, config: { title: 'System Health' } }
        ]
    },
    'analytical': {
        name: 'Analytical Dashboard',
        description: 'Deep dive analytics',
        widgets: [
            { type: 'line-chart', position: { x: 0, y: 0 }, config: { title: 'Trend Analysis' } },
            { type: 'pie-chart', position: { x: 6, y: 0 }, config: { title: 'Data Distribution' } },
            { type: 'bar-chart', position: { x: 0, y: 4 }, config: { title: 'Comparative Analysis' } },
            { type: 'table', position: { x: 6, y: 4 }, config: { title: 'Detailed Data' } }
        ]
    },
    'monitoring': {
        name: 'Monitoring Dashboard',
        description: 'Real-time monitoring',
        widgets: [
            { type: 'gauge', position: { x: 0, y: 0 }, config: { title: 'System Status' } },
            { type: 'gauge', position: { x: 3, y: 0 }, config: { title: 'Performance' } },
            { type: 'gauge', position: { x: 6, y: 0 }, config: { title: 'Uptime' } },
            { type: 'line-chart', position: { x: 0, y: 3 }, config: { title: 'Real-time Trends' } },
            { type: 'table', position: { x: 6, y: 3 }, config: { title: 'Live Data' } }
        ]
    }
};

// Initialize dashboard builder
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboardBuilder();
    loadSavedDashboard();
});

function initializeDashboardBuilder() {
    console.log('🏗️ Initializing dashboard builder...');
    
    // Initialize drag and drop
    initializeDragAndDrop();
    
    // Load default dashboard if none saved
    if (dashboardState.widgets.length === 0) {
        loadDashboardTemplate('executive');
    }
    
    console.log('✅ Dashboard builder initialized');
}

function initializeDragAndDrop() {
    // Widget library items
    const widgetItems = document.querySelectorAll('.widget-item');
    widgetItems.forEach(item => {
        item.addEventListener('dragstart', handleDragStart);
        item.addEventListener('dragend', handleDragEnd);
    });
    
    // Dashboard canvas
    const dashboardGrid = document.getElementById('dashboardGrid');
    if (dashboardGrid) {
        dashboardGrid.addEventListener('dragover', handleDragOver);
        dashboardGrid.addEventListener('drop', handleDrop);
        dashboardGrid.addEventListener('dragenter', handleDragEnter);
        dashboardGrid.addEventListener('dragleave', handleDragLeave);
    }
}

function handleDragStart(e) {
    const widgetType = e.target.dataset.widgetType;
    e.dataTransfer.setData('text/plain', widgetType);
    e.target.classList.add('dragging');
    console.log('🔄 Started dragging widget:', widgetType);
}

function handleDragEnd(e) {
    e.target.classList.remove('dragging');
    console.log('🔄 Finished dragging widget');
}

function handleDragOver(e) {
    e.preventDefault();
}

function handleDragEnter(e) {
    e.preventDefault();
    e.target.closest('.dashboard-grid')?.classList.add('drop-zone', 'active');
}

function handleDragLeave(e) {
    e.target.closest('.dashboard-grid')?.classList.remove('drop-zone', 'active');
}

function handleDrop(e) {
    e.preventDefault();
    const dashboardGrid = e.target.closest('.dashboard-grid');
    if (!dashboardGrid) return;
    
    dashboardGrid.classList.remove('drop-zone', 'active');
    
    const widgetType = e.dataTransfer.getData('text/plain');
    const rect = dashboardGrid.getBoundingClientRect();
    const x = Math.floor((e.clientX - rect.left) / (rect.width / 12));
    const y = Math.floor((e.clientY - rect.top) / 50); // Approximate row height
    
    addWidgetToDashboard(widgetType, { x, y });
    console.log('➕ Added widget to dashboard:', widgetType, 'at position:', { x, y });
}

function addWidgetToDashboard(widgetType, position) {
    const widgetId = `widget_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const widgetConfig = widgetConfigs[widgetType];
    
    if (!widgetConfig) {
        console.error('❌ Unknown widget type:', widgetType);
        return;
    }
    
    const widget = {
        id: widgetId,
        type: widgetType,
        position: position,
        config: { ...widgetConfig },
        size: widgetConfig.size
    };
    
    dashboardState.widgets.push(widget);
    renderWidget(widget);
    saveDashboardState();
}

function renderWidget(widget) {
    const dashboardGrid = document.getElementById('dashboardGrid');
    if (!dashboardGrid) return;
    
    const widgetElement = document.createElement('div');
    widgetElement.className = 'dashboard-widget';
    widgetElement.id = widget.id;
    
    // Ensure widget has proper size configuration
    const widgetConfig = widgetConfigs[widget.type];
    if (!widgetConfig) {
        console.error('❌ Unknown widget type:', widget.type);
        return;
    }
    
    // Use widget config size if not defined in widget
    const size = widget.size || widgetConfig.size || { w: 3, h: 2 };
    
    widgetElement.style.gridColumn = `${widget.position.x + 1} / span ${size.w}`;
    widgetElement.style.gridRow = `${widget.position.y + 1} / span ${size.h}`;
    
    widgetElement.innerHTML = `
        <div class="widget-header">
            <div class="widget-title">
                <i class="${widgetConfig.icon} me-2"></i>
                ${widgetConfig.name}
            </div>
            <div class="widget-controls">
                <button class="btn btn-sm btn-outline-primary" onclick="configureWidget('${widget.id}')" title="Configure">
                    <i class="fas fa-cog"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="removeWidget('${widget.id}')" title="Remove">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </div>
        <div class="widget-content" id="widget-content-${widget.id}">
            ${getWidgetContent(widget)}
        </div>
    `;
    
    // Make widget draggable within dashboard
    widgetElement.draggable = true;
    widgetElement.addEventListener('dragstart', handleWidgetDragStart);
    widgetElement.addEventListener('dragend', handleWidgetDragEnd);
    
    dashboardGrid.appendChild(widgetElement);
    
    // Initialize widget-specific functionality
    initializeWidget(widget);
}

function getWidgetContent(widget) {
    switch (widget.type) {
        case 'kpi-card':
            return `
                <div class="text-center">
                    <div class="h3 text-primary" id="kpi-value-${widget.id}">--</div>
                    <div class="text-muted">Loading...</div>
                </div>
            `;
        case 'line-chart':
            return `<canvas id="chart-${widget.id}" width="400" height="200"></canvas>`;
        case 'pie-chart':
            return `<canvas id="chart-${widget.id}" width="300" height="300"></canvas>`;
        case 'bar-chart':
            return `<canvas id="chart-${widget.id}" width="400" height="200"></canvas>`;
        case 'table':
            return `
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead><tr><th>Metric</th><th>Value</th></tr></thead>
                        <tbody id="table-body-${widget.id}">
                            <tr><td colspan="2" class="text-center">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>
            `;
        case 'gauge':
            return `<canvas id="chart-${widget.id}" width="200" height="200"></canvas>`;
        default:
            return '<div class="text-center text-muted">Widget content</div>';
    }
}

function initializeWidget(widget) {
    // Load data and initialize widget
    loadWidgetData(widget);
}

async function loadWidgetData(widget) {
    try {
        const data = await AnalyticsIntegration.fetchAnalyticsData({
            metricType: widget.config.dataSource,
            timeframe: '30d'
        });
        
        updateWidgetContent(widget, data);
    } catch (error) {
        console.error('❌ Error loading widget data:', error);
        updateWidgetContent(widget, null);
    }
}

function updateWidgetContent(widget, data) {
    const contentElement = document.getElementById(`widget-content-${widget.id}`);
    if (!contentElement) return;
    
    switch (widget.type) {
        case 'kpi-card':
            updateKPICard(widget, data);
            break;
        case 'line-chart':
        case 'pie-chart':
        case 'bar-chart':
        case 'gauge':
            updateChart(widget, data);
            break;
        case 'table':
            updateTable(widget, data);
            break;
    }
}

function updateKPICard(widget, data) {
    const valueElement = document.getElementById(`kpi-value-${widget.id}`);
    if (valueElement) {
        if (data && data.summary) {
            const metric = widget.config.metric || 'overall_quality';
            const value = data.summary[metric] || 'N/A';
            valueElement.textContent = typeof value === 'number' ? value.toFixed(1) + '%' : value;
        } else {
            valueElement.textContent = 'N/A';
        }
    }
}

function updateChart(widget, data) {
    const canvas = document.getElementById(`chart-${widget.id}`);
    if (!canvas) return;
    
    // Create chart based on widget type and data
    const ctx = canvas.getContext('2d');
    if (window.widgetCharts && window.widgetCharts[widget.id]) {
        window.widgetCharts[widget.id].destroy();
    }
    
    if (!window.widgetCharts) window.widgetCharts = {};
    
    const chartConfig = getChartConfig(widget.type, data);
    window.widgetCharts[widget.id] = new Chart(ctx, chartConfig);
}

function getChartConfig(chartType, data) {
    // Basic chart configurations
    const baseConfig = {
        responsive: true,
        maintainAspectRatio: false
    };
    
    switch (chartType) {
        case 'line-chart':
            return {
                ...baseConfig,
                type: 'line',
                data: {
                    labels: data?.labels || [],
                    datasets: [{
                        label: 'Data',
                        data: data?.data || [],
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.1)',
                        tension: 0.4
                    }]
                }
            };
        case 'pie-chart':
            return {
                ...baseConfig,
                type: 'doughnut',
                data: {
                    labels: data?.labels || [],
                    datasets: [{
                        data: data?.data || [],
                        backgroundColor: [
                            'rgba(75, 192, 192, 0.8)',
                            'rgba(54, 162, 235, 0.8)',
                            'rgba(255, 205, 86, 0.8)',
                            'rgba(255, 99, 132, 0.8)'
                        ]
                    }]
                }
            };
        case 'bar-chart':
            return {
                ...baseConfig,
                type: 'bar',
                data: {
                    labels: data?.labels || [],
                    datasets: [{
                        label: 'Data',
                        data: data?.data || [],
                        backgroundColor: 'rgba(75, 192, 192, 0.8)'
                    }]
                }
            };
        case 'gauge':
            return {
                ...baseConfig,
                type: 'doughnut',
                data: {
                    labels: ['Value', 'Remaining'],
                    datasets: [{
                        data: [data?.value || 0, 100 - (data?.value || 0)],
                        backgroundColor: ['rgba(75, 192, 192, 0.8)', 'rgba(201, 203, 207, 0.3)']
                    }]
                },
                options: {
                    cutout: '80%',
                    plugins: {
                        legend: { display: false }
                    }
                }
            };
        default:
            return baseConfig;
    }
}

function updateTable(widget, data) {
    const tableBody = document.getElementById(`table-body-${widget.id}`);
    if (!tableBody) return;
    
    if (data && data.summary) {
        tableBody.innerHTML = Object.entries(data.summary)
            .map(([key, value]) => `
                <tr>
                    <td>${key.replace(/_/g, ' ').toUpperCase()}</td>
                    <td>${typeof value === 'number' ? value.toFixed(2) : value}</td>
                </tr>
            `).join('');
    } else {
        tableBody.innerHTML = '<tr><td colspan="2" class="text-center text-muted">No data available</td></tr>';
    }
}

// Widget management functions
function configureWidget(widgetId) {
    const widget = dashboardState.widgets.find(w => w.id === widgetId);
    if (!widget) return;
    
    // Show configuration modal
    showWidgetConfigModal(widget);
}

function removeWidget(widgetId) {
    const widgetElement = document.getElementById(widgetId);
    if (widgetElement) {
        widgetElement.remove();
    }
    
    dashboardState.widgets = dashboardState.widgets.filter(w => w.id !== widgetId);
    saveDashboardState();
    
    console.log('➖ Removed widget:', widgetId);
}

function showWidgetConfigModal(widget) {
    // Create and show configuration modal
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Configure ${widget.config.name}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label">Title</label>
                        <input type="text" class="form-control" id="widget-title-${widget.id}" value="${widget.config.name}">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Data Source</label>
                        <select class="form-select" id="widget-datasource-${widget.id}">
                            <option value="kpi" ${widget.config.dataSource === 'kpi' ? 'selected' : ''}>KPI Data</option>
                            <option value="trends" ${widget.config.dataSource === 'trends' ? 'selected' : ''}>Trends Data</option>
                            <option value="distribution" ${widget.config.dataSource === 'distribution' ? 'selected' : ''}>Distribution Data</option>
                        </select>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="saveWidgetConfig('${widget.id}')">Save</button>
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
}

function saveWidgetConfig(widgetId) {
    const widget = dashboardState.widgets.find(w => w.id === widgetId);
    if (!widget) return;
    
    const title = document.getElementById(`widget-title-${widgetId}`).value;
    const dataSource = document.getElementById(`widget-datasource-${widgetId}`).value;
    
    widget.config.name = title;
    widget.config.dataSource = dataSource;
    
    // Re-render widget
    const widgetElement = document.getElementById(widgetId);
    if (widgetElement) {
        widgetElement.remove();
    }
    renderWidget(widget);
    
    // Close modal
    const modal = bootstrap.Modal.getInstance(document.querySelector('.modal'));
    if (modal) modal.hide();
    
    saveDashboardState();
}

// Dashboard management functions
function toggleDashboardBuilder() {
    const builder = document.getElementById('dashboardBuilder');
    if (builder) {
        dashboardState.isBuilderMode = !dashboardState.isBuilderMode;
        builder.style.display = dashboardState.isBuilderMode ? 'block' : 'none';
        
        const button = document.querySelector('button[onclick="toggleDashboardBuilder()"]');
        if (button) {
            button.innerHTML = dashboardState.isBuilderMode ? 
                '<i class="fas fa-eye me-1"></i>View Mode' : 
                '<i class="fas fa-cog me-1"></i>Builder Mode';
        }
    }
}

function saveCustomDashboard() {
    const dashboardName = prompt('Enter dashboard name:');
    if (dashboardName) {
        const dashboardData = {
            name: dashboardName,
            widgets: dashboardState.widgets,
            layout: dashboardState.layout,
            timestamp: new Date().toISOString()
        };
        
        const savedDashboards = JSON.parse(localStorage.getItem('custom_dashboards') || '{}');
        savedDashboards[dashboardName] = dashboardData;
        localStorage.setItem('custom_dashboards', JSON.stringify(savedDashboards));
        
        showNotification(`Dashboard "${dashboardName}" saved successfully`, 'success');
    }
}

function loadCustomDashboard() {
    const savedDashboards = JSON.parse(localStorage.getItem('custom_dashboards') || '{}');
    const dashboardNames = Object.keys(savedDashboards);
    
    if (dashboardNames.length === 0) {
        showNotification('No saved dashboards found', 'info');
        return;
    }
    
    const dashboardName = prompt(`Enter dashboard name to load:\n\nAvailable dashboards:\n${dashboardNames.join('\n')}`);
    
    if (dashboardName && savedDashboards[dashboardName]) {
        const dashboardData = savedDashboards[dashboardName];
        dashboardState.widgets = dashboardData.widgets || [];
        dashboardState.layout = dashboardData.layout || [];
        
        renderDashboard();
        showNotification(`Dashboard "${dashboardName}" loaded successfully`, 'success');
    }
}

function loadDashboardTemplate(templateName) {
    const template = dashboardTemplates[templateName];
    if (!template) {
        console.error('❌ Unknown template:', templateName);
        return;
    }
    
    dashboardState.widgets = template.widgets.map(widget => ({
        ...widget,
        id: `widget_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    }));
    dashboardState.currentTemplate = templateName;
    
    renderDashboard();
    showNotification(`Template "${template.name}" loaded successfully`, 'success');
}

function resetDashboard() {
    if (confirm('Are you sure you want to reset the dashboard? This will remove all widgets.')) {
        dashboardState.widgets = [];
        dashboardState.layout = [];
        dashboardState.currentTemplate = null;
        
        const dashboardGrid = document.getElementById('dashboardGrid');
        if (dashboardGrid) {
            dashboardGrid.innerHTML = '';
        }
        
        saveDashboardState();
        showNotification('Dashboard reset successfully', 'success');
    }
}

function renderDashboard() {
    const dashboardGrid = document.getElementById('dashboardGrid');
    if (!dashboardGrid) return;
    
    dashboardGrid.innerHTML = '';
    dashboardState.widgets.forEach(widget => {
        renderWidget(widget);
    });
}

function saveDashboardState() {
    localStorage.setItem('dashboard_state', JSON.stringify(dashboardState));
}

function loadSavedDashboard() {
    const saved = localStorage.getItem('dashboard_state');
    if (saved) {
        dashboardState = { ...dashboardState, ...JSON.parse(saved) };
        renderDashboard();
    }
}

// Widget drag and drop within dashboard
function handleWidgetDragStart(e) {
    e.dataTransfer.setData('text/plain', e.target.id);
    e.target.classList.add('dragging');
}

function handleWidgetDragEnd(e) {
    e.target.classList.remove('dragging');
}

// Export functions to global scope
window.toggleDashboardBuilder = toggleDashboardBuilder;
window.saveCustomDashboard = saveCustomDashboard;
window.loadCustomDashboard = loadCustomDashboard;
window.loadDashboardTemplate = loadDashboardTemplate;
window.resetDashboard = resetDashboard;
window.configureWidget = configureWidget;
window.removeWidget = removeWidget;
window.saveWidgetConfig = saveWidgetConfig; 