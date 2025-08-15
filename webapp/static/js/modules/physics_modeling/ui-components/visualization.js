/**
 * Visualization UI Component
 * Handles 3D visualization, charts, and data export
 */

export class VisualizationUIComponent {
    constructor() {
        // Authentication properties
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
        
        this.isInitialized = false;
        this.activeVisualizations = [];
        this.visualizationConfig = {
            renderQuality: 'high',
            enableShadows: true,
            enableAntialiasing: true,
            backgroundColor: '#000000',
            gridSize: 100
        };
        this.chartTypes = [
            'line',
            'scatter',
            'surface',
            'contour',
            'vector',
            'heatmap'
        ];
        
        // UI elements
        this.elements = {
            visualizationContainer: null,
            chartContainer: null,
            threeDContainer: null,
            exportPanel: null,
            settingsPanel: null,
            legendPanel: null
        };
        
        // Event listeners
        this.eventListeners = [];
    }

    // Central Authentication Methods
    async waitForAuthSystem() {
        return new Promise((resolve) => {
            if (window.authSystemReady && window.authManager) {
                resolve();
            } else {
                const handleReady = () => {
                    window.removeEventListener('authSystemReady', handleReady);
                    resolve();
                };
                window.addEventListener('authSystemReady', handleReady);
            }
        });
    }

    updateAuthState() {
        if (window.authManager) {
            this.isAuthenticated = window.authManager.isAuthenticated;
            this.currentUser = window.authManager.currentUser;
            this.authToken = window.authManager.getStoredToken();
        }
    }

    setupAuthListeners() {
        const handleAuthChange = () => {
            this.updateAuthState();
            this.handleAuthStateChange();
        };

        window.addEventListener('authStateChanged', handleAuthChange);
        window.addEventListener('loginSuccess', handleAuthChange);
        window.addEventListener('logout', handleAuthChange);

        this.eventListeners.push(
            { event: 'authStateChanged', handler: handleAuthChange },
            { event: 'loginSuccess', handler: handleAuthChange },
            { event: 'logout', handler: handleAuthChange }
        );
    }

    handleAuthStateChange() {
        if (this.isAuthenticated) {
            this.loadUserVisualizations();
            this.enableAuthenticatedFeatures();
        } else {
            this.loadDemoVisualizations();
            this.disableAuthenticatedFeatures();
        }
    }

    clearSensitiveData() {
        this.currentUser = null;
        this.authToken = null;
        this.isAuthenticated = false;
    }

    getAuthHeaders() {
        return this.authToken ? { 'Authorization': `Bearer ${this.authToken}` } : {};
    }

    async init() {
        if (this.isInitialized) return;
        
        console.log('🔐 Initializing Visualization UI Component...');
        
        try {
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            this.initializeUI();
            this.setupEventListeners();
            await this.loadVisualizationConfiguration();
            
            this.isInitialized = true;
            console.log('✅ Visualization UI Component initialized');
        } catch (error) {
            console.error('❌ Visualization UI Component initialization failed:', error);
            throw error;
        }
    }

    initializeUI() {
        // Initialize UI elements
        this.elements.visualizationContainer = document.getElementById('visualization-container');
        this.elements.chartContainer = document.getElementById('chart-container');
        this.elements.threeDContainer = document.getElementById('3d-container');
        this.elements.exportPanel = document.getElementById('export-panel');
        this.elements.settingsPanel = document.getElementById('visualization-settings');
        this.elements.legendPanel = document.getElementById('legend-panel');

        if (!this.elements.visualizationContainer) {
            console.warn('⚠️ Visualization container not found');
            return;
        }

        // Initialize chart type selector
        this.initializeChartTypeSelector();
    }

    initializeChartTypeSelector() {
        const chartTypeSelect = document.getElementById('chart-type-select');
        if (!chartTypeSelect) return;

        const optionsHtml = this.chartTypes.map(type => 
            `<option value="${type}">${type.charAt(0).toUpperCase() + type.slice(1)}</option>`
        ).join('');

        chartTypeSelect.innerHTML = optionsHtml;
    }

    setupEventListeners() {
        // Chart type change
        const chartTypeSelect = document.getElementById('chart-type-select');
        if (chartTypeSelect) {
            chartTypeSelect.addEventListener('change', (e) => {
                this.changeChartType(e.target.value);
            });
        }

        // Export buttons
        const exportButtons = document.querySelectorAll('[data-export-format]');
        exportButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const format = e.target.getAttribute('data-export-format');
                this.exportVisualization(format);
            });
        });

        // Settings form
        const settingsForm = document.getElementById('visualization-settings-form');
        if (settingsForm) {
            settingsForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.updateVisualizationSettings();
            });
        }

        // 3D controls
        const threeDControls = document.querySelectorAll('[data-3d-control]');
        threeDControls.forEach(control => {
            control.addEventListener('click', (e) => {
                const action = e.target.getAttribute('data-3d-control');
                this.handle3DControl(action);
            });
        });
    }

    async loadVisualizationConfiguration() {
        try {
            const response = await fetch('/api/physics-modeling/visualization/config', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const config = await response.json();
                this.visualizationConfig = { ...this.visualizationConfig, ...config };
                this.updateSettingsUI();
            }
        } catch (error) {
            console.error('❌ Failed to load visualization configuration:', error);
        }
    }

    updateSettingsUI() {
        const renderQualitySelect = document.getElementById('render-quality');
        if (renderQualitySelect) {
            renderQualitySelect.value = this.visualizationConfig.renderQuality;
        }

        const shadowsCheckbox = document.getElementById('enable-shadows');
        if (shadowsCheckbox) {
            shadowsCheckbox.checked = this.visualizationConfig.enableShadows;
        }

        const antialiasingCheckbox = document.getElementById('enable-antialiasing');
        if (antialiasingCheckbox) {
            antialiasingCheckbox.checked = this.visualizationConfig.enableAntialiasing;
        }

        const backgroundColorInput = document.getElementById('background-color');
        if (backgroundColorInput) {
            backgroundColorInput.value = this.visualizationConfig.backgroundColor;
        }
    }

    async createVisualization(data, type = 'line') {
        try {
            const response = await fetch('/api/physics-modeling/visualization/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeaders()
                },
                body: JSON.stringify({
                    data: data,
                    type: type,
                    config: this.visualizationConfig
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.activeVisualizations.push(result.visualizationId);
                this.displayVisualization(result);
                return result.visualizationId;
            } else {
                throw new Error('Failed to create visualization');
            }
        } catch (error) {
            console.error('❌ Failed to create visualization:', error);
            throw error;
        }
    }

    displayVisualization(visualization) {
        if (visualization.type === '3d') {
            this.display3DVisualization(visualization);
        } else {
            this.displayChartVisualization(visualization);
        }
    }

    displayChartVisualization(visualization) {
        if (!this.elements.chartContainer) return;

        const chartHtml = `
            <div class="chart-visualization" id="chart-${visualization.id}">
                <div class="chart-header">
                    <h4>${visualization.title || 'Chart Visualization'}</h4>
                    <div class="chart-controls">
                        <button onclick="zoomChart('${visualization.id}')" class="btn btn-sm btn-secondary">Zoom</button>
                        <button onclick="resetChart('${visualization.id}')" class="btn btn-sm btn-secondary">Reset</button>
                    </div>
                </div>
                <div class="chart-content">
                    <canvas id="chart-canvas-${visualization.id}" width="800" height="400"></canvas>
                </div>
                <div class="chart-legend">
                    ${this.generateLegend(visualization.data)}
                </div>
            </div>
        `;

        this.elements.chartContainer.innerHTML = chartHtml;
        this.renderChart(visualization);
    }

    display3DVisualization(visualization) {
        if (!this.elements.threeDContainer) return;

        const threeDHtml = `
            <div class="3d-visualization" id="3d-${visualization.id}">
                <div class="3d-header">
                    <h4>${visualization.title || '3D Visualization'}</h4>
                    <div class="3d-controls">
                        <button data-3d-control="rotate" class="btn btn-sm btn-secondary">Rotate</button>
                        <button data-3d-control="pan" class="btn btn-sm btn-secondary">Pan</button>
                        <button data-3d-control="zoom" class="btn btn-sm btn-secondary">Zoom</button>
                        <button data-3d-control="reset" class="btn btn-sm btn-secondary">Reset</button>
                    </div>
                </div>
                <div class="3d-content">
                    <canvas id="3d-canvas-${visualization.id}" width="800" height="600"></canvas>
                </div>
            </div>
        `;

        this.elements.threeDContainer.innerHTML = threeDHtml;
        this.render3DVisualization(visualization);
    }

    renderChart(visualization) {
        const canvas = document.getElementById(`chart-canvas-${visualization.id}`);
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Basic chart rendering (this would be replaced with a proper charting library)
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.beginPath();
        
        if (visualization.data && visualization.data.length > 0) {
            const stepX = canvas.width / (visualization.data.length - 1);
            const maxY = Math.max(...visualization.data.map(d => d.y || d));
            const minY = Math.min(...visualization.data.map(d => d.y || d));
            const rangeY = maxY - minY || 1;
            
            visualization.data.forEach((point, index) => {
                const x = index * stepX;
                const y = canvas.height - ((point.y || point) - minY) / rangeY * canvas.height;
                
                if (index === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
        }
        
        ctx.stroke();
    }

    render3DVisualization(visualization) {
        const canvas = document.getElementById(`3d-canvas-${visualization.id}`);
        if (!canvas) return;

        // This would be replaced with Three.js or similar 3D rendering
        const ctx = canvas.getContext('2d');
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Basic 3D rendering placeholder
        ctx.fillStyle = '#ffffff';
        ctx.font = '16px Arial';
        ctx.fillText('3D Visualization - Use Three.js for proper 3D rendering', 50, 50);
    }

    generateLegend(data) {
        if (!data || !Array.isArray(data)) return '';

        return data.map((series, index) => `
            <div class="legend-item">
                <span class="legend-color" style="background-color: ${series.color || '#ffffff'}"></span>
                <span class="legend-label">${series.label || `Series ${index + 1}`}</span>
            </div>
        `).join('');
    }

    async changeChartType(type) {
        try {
            const currentVisualization = this.activeVisualizations[this.activeVisualizations.length - 1];
            if (!currentVisualization) return;

            const response = await fetch(`/api/physics-modeling/visualization/${currentVisualization}/change-type`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeaders()
                },
                body: JSON.stringify({ type: type })
            });

            if (response.ok) {
                const result = await response.json();
                this.displayVisualization(result);
            }
        } catch (error) {
            console.error('❌ Failed to change chart type:', error);
        }
    }

    async exportVisualization(format) {
        try {
            const currentVisualization = this.activeVisualizations[this.activeVisualizations.length - 1];
            if (!currentVisualization) {
                alert('No active visualization to export');
                return;
            }

            const response = await fetch(`/api/physics-modeling/visualization/${currentVisualization}/export`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeaders()
                },
                body: JSON.stringify({ format: format })
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `visualization.${format}`;
                a.click();
                window.URL.revokeObjectURL(url);
            }
        } catch (error) {
            console.error('❌ Failed to export visualization:', error);
        }
    }

    async updateVisualizationSettings() {
        try {
            const form = document.getElementById('visualization-settings-form');
            if (!form) return;

            const formData = new FormData(form);
            const settings = {};
            
            for (const [key, value] of formData.entries()) {
                if (key === 'enableShadows' || key === 'enableAntialiasing') {
                    settings[key] = value === 'on';
                } else {
                    settings[key] = value;
                }
            }

            this.visualizationConfig = { ...this.visualizationConfig, ...settings };
            
            const response = await fetch('/api/physics-modeling/visualization/config', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeaders()
                },
                body: JSON.stringify(settings)
            });

            if (response.ok) {
                console.log('✅ Visualization settings updated');
                this.updateActiveVisualizations();
            }
        } catch (error) {
            console.error('❌ Failed to update visualization settings:', error);
        }
    }

    updateActiveVisualizations() {
        this.activeVisualizations.forEach(visualizationId => {
            // Update each active visualization with new settings
            this.refreshVisualization(visualizationId);
        });
    }

    async refreshVisualization(visualizationId) {
        try {
            const response = await fetch(`/api/physics-modeling/visualization/${visualizationId}/refresh`, {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const visualization = await response.json();
                this.displayVisualization(visualization);
            }
        } catch (error) {
            console.error('❌ Failed to refresh visualization:', error);
        }
    }

    handle3DControl(action) {
        switch (action) {
            case 'rotate':
                this.enable3DRotation();
                break;
            case 'pan':
                this.enable3DPanning();
                break;
            case 'zoom':
                this.enable3DZooming();
                break;
            case 'reset':
                this.reset3DView();
                break;
        }
    }

    enable3DRotation() {
        console.log('🔄 3D rotation enabled');
        // Implement 3D rotation controls
    }

    enable3DPanning() {
        console.log('🖱️ 3D panning enabled');
        // Implement 3D panning controls
    }

    enable3DZooming() {
        console.log('🔍 3D zooming enabled');
        // Implement 3D zooming controls
    }

    reset3DView() {
        console.log('🔄 3D view reset');
        // Reset 3D camera to default position
    }

    async loadUserVisualizations() {
        try {
            const response = await fetch('/api/physics-modeling/visualization/user', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                this.activeVisualizations = data.visualizations || [];
                this.displayVisualizationHistory();
            }
        } catch (error) {
            console.error('❌ Failed to load user visualizations:', error);
        }
    }

    async loadDemoVisualizations() {
        try {
            const response = await fetch('/api/physics-modeling/visualization/demo');
            
            if (response.ok) {
                const data = await response.json();
                this.activeVisualizations = data.visualizations || [];
                this.displayVisualizationHistory();
            }
        } catch (error) {
            console.error('❌ Failed to load demo visualizations:', error);
        }
    }

    displayVisualizationHistory() {
        if (!this.elements.visualizationContainer) return;

        const historyHtml = this.activeVisualizations.map(viz => `
            <div class="visualization-history-item">
                <div class="viz-info">
                    <span class="viz-name">${viz.title || 'Untitled'}</span>
                    <span class="viz-type">${viz.type}</span>
                    <span class="viz-date">${new Date(viz.createdAt).toLocaleDateString()}</span>
                </div>
                <div class="viz-actions">
                    <button onclick="loadVisualization('${viz.id}')" class="btn btn-sm btn-primary">Load</button>
                    <button onclick="exportVisualization('${viz.id}')" class="btn btn-sm btn-secondary">Export</button>
                </div>
            </div>
        `).join('');

        const historyContainer = document.createElement('div');
        historyContainer.className = 'visualization-history';
        historyContainer.innerHTML = `
            <h4>Visualization History</h4>
            ${historyHtml}
        `;

        this.elements.visualizationContainer.appendChild(historyContainer);
    }

    enableAuthenticatedFeatures() {
        // Enable features that require authentication
        const authOnlyElements = document.querySelectorAll('[data-auth-only]');
        authOnlyElements.forEach(element => {
            element.disabled = false;
            element.style.display = 'block';
        });
    }

    disableAuthenticatedFeatures() {
        // Disable features that require authentication
        const authOnlyElements = document.querySelectorAll('[data-auth-only]');
        authOnlyElements.forEach(element => {
            element.disabled = true;
            element.style.display = 'none';
        });
    }

    async cleanup() {
        console.log('🧹 Cleaning up Visualization UI Component...');
        
        // Remove event listeners
        this.eventListeners.forEach(({ event, handler }) => {
            window.removeEventListener(event, handler);
        });
        
        // Clear sensitive data
        this.clearSensitiveData();
        
        this.isInitialized = false;
        console.log('✅ Visualization UI Component cleaned up');
    }

    async refresh() {
        if (this.isAuthenticated) {
            await this.loadUserVisualizations();
        } else {
            await this.loadDemoVisualizations();
        }
    }
}
