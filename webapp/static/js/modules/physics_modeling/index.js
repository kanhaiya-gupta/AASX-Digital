/**
 * Physics Modeling - Main Entry Point
 * Orchestrates all physics modeling modules and provides the main interface
 */

// Import shared utilities
import ModelCreationOperations from './modules/model_creation/operations.js';
import SimulationOperations from './modules/simulation/operations.js';
import UseCaseOperations from './modules/use_cases/operations.js';
import PluginManagementOperations from './modules/plugin-management/operations.js';
import PhysicsModelingUtils from './shared/utils.js';
import PhysicsModelingAPI from './shared/api.js';

// Import visualization modules
import ThreeDViewer from './modules/visualization/3d_viewer.js';
import PhysicsCharts from './modules/visualization/charts.js';
import PhysicsExport from './modules/visualization/export.js';
import PhysicsComparison from './modules/visualization/comparison.js';
import PhysicsAnimation from './modules/visualization/animation.js';

// Import module UI components
import ModelCreationUI from './modules/model_creation/ui.js';

class PhysicsModelingMain {
    constructor() {
        this.modelCreationOps = new ModelCreationOperations();
        this.simulationOps = new SimulationOperations();
        this.useCaseOps = new UseCaseOperations();
        this.pluginOps = new PluginManagementOperations();
        this.utils = new PhysicsModelingUtils();
        this.api = new PhysicsModelingAPI();
        
        // Initialize visualization modules
        this.threeDViewer = null;
        this.physicsCharts = null;
        this.physicsExport = null;
        this.physicsComparison = null;
        this.physicsAnimation = null;
        
        // Initialize UI components
        this.modelCreationUI = null;
        
        // State management
        this.isInitialized = false;
        this.currentPage = null;
        this.moduleInstances = new Map();
        
        this.init();
    }

    async init() {
        console.log('Initializing Physics Modeling Main...');
        
        try {
            // Check if we're on the physics modeling page
            if (!this.isPhysicsModelingPage()) {
                console.log('Not on physics modeling page, skipping initialization');
                return;
            }

            // Initialize UI components
            await this.initializeUIComponents();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Load initial data
            await this.loadInitialData();
            
            // Start background processes
            this.startBackgroundProcesses();
            
            this.isInitialized = true;
            console.log('Physics Modeling Main initialized successfully');
            
        } catch (error) {
            console.error('Error initializing Physics Modeling Main:', error);
            this.utils.handleError(error, 'PhysicsModelingMain.init');
        }
    }

    /**
     * Check if we're on the physics modeling page
     */
    isPhysicsModelingPage() {
        return window.location.pathname.includes('/physics-modeling') || 
               document.getElementById('physics-modeling-container') !== null;
    }

    /**
     * Initialize UI components
     */
    async initializeUIComponents() {
        try {
            // Initialize model creation UI
            this.modelCreationUI = new ModelCreationUI();
            await this.modelCreationUI.init(); // Initialize the ModelCreationUI
            this.moduleInstances.set('modelCreation', this.modelCreationUI);
            

            
            // Initialize visualization modules
            await this.initializeVisualizationModules();
            
            // Setup tab content loading
            this.setupTabContentLoading();
            
        } catch (error) {
            console.error('Error initializing UI components:', error);
            throw error;
        }
    }

    /**
     * Initialize visualization modules
     */
    async initializeVisualizationModules() {
        try {
            // Initialize 3D viewer if container exists
            if (document.getElementById('3d-viewer-container')) {
                this.threeDViewer = new ThreeDViewer('3d-viewer-container');
                this.moduleInstances.set('threeDViewer', this.threeDViewer);
            }

            // Initialize charts module
            this.physicsCharts = new PhysicsCharts();
            this.moduleInstances.set('physicsCharts', this.physicsCharts);

            // Initialize export module
            this.physicsExport = new PhysicsExport();
            this.moduleInstances.set('physicsExport', this.physicsExport);

            // Initialize comparison module
            this.physicsComparison = new PhysicsComparison();
            this.moduleInstances.set('physicsComparison', this.physicsComparison);

            // Initialize animation module
            this.physicsAnimation = new PhysicsAnimation();
            this.moduleInstances.set('physicsAnimation', this.physicsAnimation);

            console.log('Visualization modules initialized successfully');
            
        } catch (error) {
            console.error('Error initializing visualization modules:', error);
            throw error;
        }
    }

    /**
     * Initialize the consolidated simulation form
     */
    async initializeSimulationForm() {
        try {
            // Load available twins
            const twins = await this.modelCreationOps.loadAvailableTwins();
            const twinSelect = document.getElementById('twin-select');
            if (twinSelect) {
                twinSelect.innerHTML = '<option value="">Select a digital twin...</option>';
                twins.forEach(twin => {
                    const option = document.createElement('option');
                    option.value = twin.twin_id;
                    option.textContent = twin.name || twin.twin_id;
                    twinSelect.appendChild(option);
                });
            }

            // Load available plugins
            const plugins = await this.pluginOps.loadAvailablePlugins();
            const pluginSelect = document.getElementById('plugin-select');
            if (pluginSelect) {
                pluginSelect.innerHTML = '<option value="">Select a plugin...</option>';
                // Fix: plugins is an object {success: true, data: [...]}, so we need to access plugins.data
                if (plugins.success && plugins.data) {
                    plugins.data.forEach(plugin => {
                        const option = document.createElement('option');
                        option.value = plugin.plugin_id;
                        option.textContent = plugin.name;
                        pluginSelect.appendChild(option);
                    });
                }
            }

            // Setup form submission handler
            const form = document.getElementById('simulation-form');
            if (form) {
                form.addEventListener('submit', (e) => {
                    e.preventDefault();
                    this.handleSimulationSubmit();
                });
            }

            // Setup plugin selection change handler
            if (pluginSelect) {
                pluginSelect.addEventListener('change', (e) => {
                    this.handlePluginSelectionChange(e.target.value);
                });
            }

        } catch (error) {
            console.error('Error initializing simulation form:', error);
            this.utils.handleError(error, 'initializeSimulationForm');
        }
    }

    /**
     * Handle simulation form submission
     */
    async handleSimulationSubmit() {
        try {
            const twinId = document.getElementById('twin-select').value;
            const pluginId = document.getElementById('plugin-select').value;
            const simulationName = document.getElementById('simulation-name').value;
            const parametersText = document.getElementById('simulation-parameters').value;

            if (!twinId || !pluginId) {
                this.utils.showNotification('Please select both a digital twin and a plugin', 'warning');
                return;
            }

            let parameters = {};
            if (parametersText.trim()) {
                try {
                    parameters = JSON.parse(parametersText);
                } catch (e) {
                    this.utils.showNotification('Invalid JSON format in parameters field', 'error');
                    return;
                }
            }

            const simulationData = { 
                twin_id: twinId, 
                plugin_id: pluginId, 
                parameters: parameters 
            };
            
            if (simulationName) {
                simulationData.name = simulationName;
            }

            const result = await this.simulationOps.runSimulation(simulationData);
            if (result.success) {
                this.utils.showNotification('Simulation started successfully!', 'success');
                // Refresh active simulations list
                await this.loadActiveSimulations();
            } else {
                this.utils.showNotification(result.error || 'Failed to start simulation', 'error');
            }
        } catch (error) {
            console.error('Error handling simulation submit:', error);
            this.utils.handleError(error, 'handleSimulationSubmit');
        }
    }

    /**
     * Handle Plugin Selection Change
     */
    async handlePluginSelectionChange(pluginId) {
        try {
            if (!pluginId) {
                const infoDisplay = document.getElementById('plugin-info-display');
                if (infoDisplay) {
                    infoDisplay.innerHTML = '<p class="text-muted">Select a plugin to view its details and capabilities</p>';
                }
                return;
            }

            // Get plugin details
            const pluginDetails = await this.pluginOps.getPluginDetails(pluginId);
            
            if (pluginDetails.success) {
                const plugin = pluginDetails.data;
                const infoDisplay = document.getElementById('plugin-info-display');
                
                if (infoDisplay) {
                    infoDisplay.innerHTML = `
                        <div class="mb-3">
                            <h6>${plugin.name}</h6>
                            <p class="text-muted small">${plugin.description}</p>
                        </div>
                        <div class="mb-3">
                            <strong>Category:</strong> ${plugin.category}<br>
                            <strong>Version:</strong> ${plugin.version}
                        </div>
                        <div class="mb-3">
                            <strong>Parameters:</strong>
                            <ul class="list-unstyled small">
                                ${plugin.parameters.map(param => `<li>• ${param.name}: ${param.type}</li>`).join('')}
                            </ul>
                        </div>
                        <div class="mb-3">
                            <strong>Capabilities:</strong>
                            <ul class="list-unstyled small">
                                ${plugin.solver_capabilities.map(cap => `<li>• ${cap.name}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }
            } else {
                this.utils.showError('Failed to load plugin details');
            }

        } catch (error) {
            console.error('Error handling plugin selection change:', error);
            this.utils.handleError(error, 'handlePluginSelectionChange');
        }
    }

    /**
     * Setup global event listeners
     */
    setupEventListeners() {
        // Listen for model list refresh events
        document.addEventListener('modelListRefresh', (event) => {
            this.handleModelListRefresh(event);
        });

        // Listen for simulation status updates
        document.addEventListener('simulationStatusUpdate', (event) => {
            this.handleSimulationStatusUpdate(event);
        });

        // Listen for page visibility changes
        document.addEventListener('visibilitychange', () => {
            this.handleVisibilityChange();
        });

        // Listen for window resize events
        window.addEventListener('resize', this.utils.debounce(() => {
            this.handleWindowResize();
        }, 250));

        // Listen for beforeunload events
        window.addEventListener('beforeunload', () => {
            this.handleBeforeUnload();
        });

        // Listen for custom events
        document.addEventListener('physicsDataRefresh', () => {
            this.refreshAllData();
        });

        document.addEventListener('physicsDataExport', () => {
            this.exportAllData();
        });

        document.addEventListener('modelDetailsFetch', (event) => {
            this.showModelDetails(event.detail.modelId);
        });

        document.addEventListener('simulationResultsFetch', (event) => {
            this.showSimulationResults(event.detail.simulationId);
        });

        document.addEventListener('useCaseExplore', (event) => {
            this.exploreUseCase(event.detail.useCaseId);
        });
    }

    /**
     * Setup tab content loading
     */
    setupTabContentLoading() {
        const tabs = document.querySelectorAll('#physicsTabs .nav-link');
        tabs.forEach(tab => {
            tab.addEventListener('shown.bs.tab', (event) => {
                const targetId = event.target.getAttribute('data-bs-target').substring(1);
                this.loadTabContent(targetId);
            });
        });

        // Load initial tab content
        this.loadTabContent('simulation');
    }

    /**
     * Load content for specific tab
     */
    async loadTabContent(tabId) {
        const tabContent = document.getElementById(tabId);
        if (!tabContent) return;

        // Show loading spinner
        tabContent.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;

        try {
            switch (tabId) {
                case 'simulation':
                    await this.loadSimulationContent(tabContent);
                    break;
                case 'plugins':
                    await this.loadPluginManagementContent(tabContent);
                    break;
                case 'visualization':
                    await this.loadVisualizationContent(tabContent);
                    break;
                case 'analysis':
                    await this.loadAnalysisContent(tabContent);
                    break;
                case 'use-cases':
                    await this.loadUseCasesContent(tabContent);
                    break;
                case 'system':
                    await this.loadSystemContent(tabContent);
                    break;
                default:
                    tabContent.innerHTML = '<p class="text-muted">Content not available</p>';
            }
        } catch (error) {
            console.error(`Error loading tab content for ${tabId}:`, error);
            tabContent.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Failed to load content. Please try refreshing the page.
                </div>
            `;
        }
    }

    /**
     * Load initial data
     */
    async loadInitialData() {
        try {
            // Load system status
            await this.loadSystemStatus();
            
            // Load available models
            await this.modelCreationOps.loadAvailableModels();
            
            // Load active simulations
            await this.loadActiveSimulations();
            
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.utils.handleError(error, 'loadInitialData');
        }
    }

    /**
     * Load Simulation tab content - Consolidated plugin selection and simulation control
     */
    async loadSimulationContent(container) {
        container.innerHTML = `
            <div class="row">
                <div class="col-lg-8">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="fas fa-play me-2"></i>Run Simulation
                            </h5>
                        </div>
                        <div class="card-body">
                            <form id="simulation-form">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="twin-select" class="form-label">Digital Twin</label>
                                            <select class="form-select" id="twin-select" required>
                                                <option value="">Select a digital twin...</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="plugin-select" class="form-label">Plugin</label>
                                            <select class="form-select" id="plugin-select" required>
                                                <option value="">Select a plugin...</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="simulation-name" class="form-label">Simulation Name (Optional)</label>
                                            <input type="text" class="form-control" id="simulation-name" placeholder="Enter a name for this simulation...">
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="simulation-parameters" class="form-label">Parameters (Optional)</label>
                                            <textarea class="form-control" id="simulation-parameters" rows="3" 
                                                placeholder='Enter parameters as JSON (e.g., {"temperature": 300, "pressure": 101325})'></textarea>
                                        </div>
                                    </div>
                                </div>
                                <div class="text-end">
                                    <button type="submit" class="btn btn-primary">
                                        <i class="fas fa-play me-2"></i>Run Simulation
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">
                                <i class="fas fa-info-circle me-2"></i>Plugin Information
                            </h6>
                        </div>
                        <div class="card-body">
                            <div id="plugin-info-display">
                                <p class="text-muted">Select a plugin to view its details and capabilities</p>
                            </div>
                        </div>
                    </div>
                    <div class="card mt-3">
                        <div class="card-header">
                            <h6 class="mb-0">
                                <i class="fas fa-running me-2"></i>Active Simulations
                            </h6>
                        </div>
                        <div class="card-body">
                            <div id="active-simulations-list">
                                <div class="text-center text-muted">
                                    <i class="fas fa-spinner fa-spin"></i> Loading simulations...
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Initialize the consolidated form and load data
        await this.initializeSimulationForm();
        await this.loadActiveSimulations();
    }

    /**
     * Load Plugin Management tab content
     */
    async loadPluginManagementContent(container) {
        container.innerHTML = `
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="fas fa-puzzle-piece me-2"></i>Available Plugins
                            </h5>
                        </div>
                        <div class="card-body">
                            <div id="available-plugins-container">
                                <div class="text-center text-muted">
                                    <i class="fas fa-spinner fa-spin"></i> Loading plugins...
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="fas fa-info-circle me-2"></i>Plugin Details
                            </h5>
                        </div>
                        <div class="card-body">
                            <div id="plugin-details-container">
                                <p class="text-muted">Select a plugin to view its details</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Load available plugins
        await this.loadAvailablePlugins();
    }

    /**
     * Load available plugins
     */
    async loadAvailablePlugins() {
        try {
            const result = await this.pluginOps.loadAvailablePlugins();
            
            if (result.success) {
                const container = document.getElementById('available-plugins-container');
                this.pluginOps.createPluginSelectionUI(container, (pluginId) => {
                    this.showPluginDetails(pluginId);
                });
            } else {
                console.error('Failed to load plugins:', result.error);
                const container = document.getElementById('available-plugins-container');
                container.innerHTML = '<p class="text-danger">Failed to load plugins</p>';
            }
        } catch (error) {
            console.error('Error loading plugins:', error);
        }
    }

    /**
     * Show plugin details
     */
    showPluginDetails(pluginId) {
        const container = document.getElementById('plugin-details-container');
        this.pluginOps.createPluginDetailsUI(container, pluginId);
        
        // Update selected plugin
        this.pluginOps.selectPlugin(pluginId);
        
        // Update UI to show selected plugin
        this.updatePluginSelectionUI(pluginId);
    }

    /**
     * Update plugin selection UI
     */
    updatePluginSelectionUI(selectedPluginId) {
        // Remove previous selections
        document.querySelectorAll('.plugin-select-btn').forEach(btn => {
            btn.classList.remove('active', 'btn-primary');
            btn.classList.add('list-group-item-action');
        });
        
        // Highlight selected plugin
        const selectedBtn = document.querySelector(`[data-plugin-id="${selectedPluginId}"]`);
        if (selectedBtn) {
            selectedBtn.classList.add('active', 'btn-primary');
            selectedBtn.classList.remove('list-group-item-action');
        }
    }

    /**
     * Load Visualization tab content
     */
    async loadVisualizationContent(container) {
        container.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">
                                <i class="fas fa-chart-line me-2"></i>2D Charts
                            </h6>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="physics-chart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">
                                <i class="fas fa-cube me-2"></i>3D Viewer
                            </h6>
                        </div>
                        <div class="card-body">
                            <div id="3d-viewer-container" style="height: 300px;">
                                <div class="text-center text-muted">
                                    <i class="fas fa-cube fa-3x mb-3"></i>
                                    <p>3D visualization will be loaded here</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Initialize visualization modules
        if (this.physicsCharts) {
            this.physicsCharts.initChart('physics-chart');
        }
    }

    /**
     * Load Analysis tab content
     */
    async loadAnalysisContent(container) {
        container.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">
                                <i class="fas fa-microscope me-2"></i>Model Validation
                            </h6>
                        </div>
                        <div class="card-body">
                            <div id="validation-results">
                                <div class="text-center text-muted">
                                    <i class="fas fa-spinner fa-spin"></i> Loading validation data...
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">
                                <i class="fas fa-chart-bar me-2"></i>Performance Metrics
                            </h6>
                        </div>
                        <div class="card-body">
                            <div id="performance-metrics">
                                <div class="text-center text-muted">
                                    <i class="fas fa-spinner fa-spin"></i> Loading metrics...
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Load Use Cases tab content
     */
    async loadUseCasesContent(container) {
        container.innerHTML = `
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="fas fa-lightbulb me-2"></i>Physics Modeling Use Cases
                            </h5>
                        </div>
                        <div class="card-body">
                            <div id="use-cases-container">
                                <div class="text-center text-muted">
                                    <i class="fas fa-spinner fa-spin"></i> Loading use cases...
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Load use cases directly
        await this.loadUseCases();
    }

    /**
     * Load use cases with simple display
     */
    async loadUseCases() {
        try {
            const response = await this.api.getUseCases();
            // The API returns raw response: {use_cases: [...]}
            if (response && response.use_cases) {
                this.renderUseCases(response.use_cases);
            } else {
                this.renderUseCasesError('Failed to load use cases');
            }
        } catch (error) {
            console.error('Error loading use cases:', error);
            this.renderUseCasesError('Failed to load use cases. Please try refreshing the page.');
        }
    }

    /**
     * Render use cases in simple format
     */
    renderUseCases(useCases) {
        const container = document.getElementById('use-cases-container');
        if (!container) return;

        if (!useCases || useCases.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i class="fas fa-info-circle fa-2x mb-3"></i>
                    <p>No use cases available</p>
                </div>
            `;
            return;
        }

        const useCasesHTML = useCases.map(useCase => `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card h-100 card-hover">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="card-title mb-0">
                                <i class="fas fa-lightbulb me-2 text-primary"></i>
                                ${useCase.name}
                            </h6>
                            ${useCase.project_count ? `<span class="badge bg-info">${useCase.project_count} projects</span>` : ''}
                        </div>
                        <p class="card-text text-muted small">${useCase.description}</p>
                        <div class="mb-2">
                            <span class="badge bg-secondary">${useCase.category}</span>
                        </div>
                        <div class="small text-muted mb-3">
                            <strong>Examples:</strong><br>
                            ${useCase.examples ? useCase.examples.slice(0, 2).join(', ') : 'No examples available'}
                        </div>
                        <button class="btn btn-outline-primary btn-sm" 
                                onclick="window.PhysicsModeling.exploreUseCase('${useCase.id}')">
                            <i class="fas fa-arrow-right me-1"></i>Explore
                        </button>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = `
            <div class="row">
                ${useCasesHTML}
            </div>
        `;
    }

    /**
     * Render use cases error
     */
    renderUseCasesError(message) {
        const container = document.getElementById('use-cases-container');
        if (!container) return;

        container.innerHTML = `
            <div class="text-center text-danger">
                <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
                <p>${message}</p>
            </div>
        `;
    }

    /**
     * Load System tab content
     */
    async loadSystemContent(container) {
        container.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">
                                <i class="fas fa-server me-2"></i>System Status
                            </h6>
                        </div>
                        <div class="card-body">
                            <div id="system-status-details">
                                <div class="text-center text-muted">
                                    <i class="fas fa-spinner fa-spin"></i> Loading system status...
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">
                                <i class="fas fa-tachometer-alt me-2"></i>Performance Metrics
                            </h6>
                        </div>
                        <div class="card-body">
                            <div id="system-performance">
                                <div class="text-center text-muted">
                                    <i class="fas fa-spinner fa-spin"></i> Loading performance data...
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Load system data
        await this.loadSystemStatus();
    }

    /**
     * Load system status
     */
    async loadSystemStatus() {
        try {
            const status = await this.api.getSystemStatus();
            this.updateSystemStatusUI(status);
        } catch (error) {
            console.error('Error loading system status:', error);
        }
    }

    /**
     * Load active simulations
     */
    async loadActiveSimulations() {
        try {
            const result = await this.simulationOps.listSimulations({ status: 'running' });
            if (result.success) {
                this.updateActiveSimulationsUI(result.data);
            }
        } catch (error) {
            console.error('Error loading active simulations:', error);
        }
    }

    /**
     * Start background processes
     */
    startBackgroundProcesses() {
        // Start periodic system status updates
        this.startSystemStatusUpdates();
        
        // Start simulation monitoring
        this.startSimulationMonitoring();
        
        // Start cleanup processes
        this.startCleanupProcesses();
    }

    /**
     * Start system status updates
     */
    startSystemStatusUpdates() {
        setInterval(async () => {
            try {
                await this.loadSystemStatus();
            } catch (error) {
                console.error('Error updating system status:', error);
            }
        }, 30000); // Update every 30 seconds
    }

    /**
     * Start simulation monitoring
     */
    startSimulationMonitoring() {
        setInterval(async () => {
            try {
                // Get active simulations count
                const countResult = await this.simulationOps.getActiveSimulationsCount();
                if (countResult.success) {
                    this.updateActiveSimulationsCount(countResult.data);
                }
            } catch (error) {
                console.error('Error monitoring simulations:', error);
            }
        }, 10000); // Check every 10 seconds
    }

    /**
     * Start cleanup processes
     */
    startCleanupProcesses() {
        setInterval(() => {
            try {
                // Cleanup completed simulations
                this.simulationOps.cleanupCompletedSimulations();
                
                // Cleanup old notifications
                this.cleanupOldNotifications();
                
            } catch (error) {
                console.error('Error in cleanup processes:', error);
            }
        }, 60000); // Run every minute
    }

    /**
     * Update system status UI
     */
    updateSystemStatusUI(status) {
        // Update status dashboard cards
        const totalPluginsElement = document.getElementById('total-plugins');
        const activeSimulationsElement = document.getElementById('active-simulations');
        const availableTwinsElement = document.getElementById('available-twins');
        const systemStatusElement = document.getElementById('system-status');

        if (totalPluginsElement) {
            totalPluginsElement.textContent = status.available_models || 0;
        }
        if (activeSimulationsElement) {
            activeSimulationsElement.textContent = status.active_simulations || 0;
        }
        if (availableTwinsElement) {
            availableTwinsElement.textContent = status.available_twins || 0;
        }
        if (systemStatusElement) {
            const statusText = status.physics_framework_available ? 'Healthy' : 'Degraded';
            systemStatusElement.textContent = statusText;
        }

        // Update system status details if on system tab
        const systemStatusDetails = document.getElementById('system-status-details');
        if (systemStatusDetails) {
            systemStatusDetails.innerHTML = `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <span>Physics Framework:</span>
                    <span class="badge bg-${status.physics_framework_available ? 'success' : 'danger'}">
                        ${status.physics_framework_available ? 'Available' : 'Unavailable'}
                    </span>
                </div>
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <span>Twin Registry:</span>
                    <span class="badge bg-${status.twin_connector_status === 'available' ? 'success' : 'warning'}">
                        ${status.twin_connector_status}
                    </span>
                </div>
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <span>AI/RAG System:</span>
                    <span class="badge bg-${status.ai_rag_connector_status === 'available' ? 'success' : 'warning'}">
                        ${status.ai_rag_connector_status}
                    </span>
                </div>
                <div class="d-flex justify-content-between align-items-center">
                    <span>Last Updated:</span>
                    <small class="text-muted">${new Date(status.timestamp).toLocaleString()}</small>
                </div>
            `;
        }
    }

    /**
     * Update performance metrics
     */
    updatePerformanceMetrics(performance) {
        // Update CPU usage
        const cpuElement = document.getElementById('system-cpu-usage');
        if (cpuElement && performance.cpu_usage !== undefined) {
            cpuElement.style.width = `${performance.cpu_usage}%`;
            const cpuText = document.getElementById('cpu-usage-text');
            if (cpuText) {
                cpuText.textContent = `${performance.cpu_usage}%`;
            }
        }

        // Update memory usage
        const memoryElement = document.getElementById('system-memory-usage');
        if (memoryElement && performance.memory_usage !== undefined) {
            memoryElement.style.width = `${performance.memory_usage}%`;
            const memoryText = document.getElementById('memory-usage-text');
            if (memoryText) {
                memoryText.textContent = `${performance.memory_usage}%`;
            }
        }

        // Update disk usage
        const diskElement = document.getElementById('system-disk-usage');
        if (diskElement && performance.disk_usage !== undefined) {
            diskElement.style.width = `${performance.disk_usage}%`;
            const diskText = document.getElementById('disk-usage-text');
            if (diskText) {
                diskText.textContent = `${performance.disk_usage}%`;
            }
        }
    }

    /**
     * Update active simulations UI
     */
    updateActiveSimulationsUI(simulations) {
        const container = document.getElementById('active-simulations-container');
        if (!container) return;

        // Clear existing content
        container.innerHTML = '';

        if (simulations.length === 0) {
            container.innerHTML = '<p class="text-muted">No active simulations</p>';
            return;
        }

        // Add simulation cards
        simulations.forEach(simulation => {
            const card = this.createSimulationCard(simulation);
            container.appendChild(card);
        });
    }

    /**
     * Create simulation card
     */
    createSimulationCard(simulation) {
        const card = document.createElement('div');
        card.className = 'card mb-2';
        card.innerHTML = `
            <div class="card-body p-2">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title mb-1">${simulation.name || simulation.id}</h6>
                        <small class="text-muted">${simulation.simulation_type}</small>
                    </div>
                    <div class="text-end">
                        <span class="badge bg-${this.utils.getStatusClass(simulation.status)}">
                            ${simulation.status}
                        </span>
                        <br>
                        <small class="text-muted">${this.utils.formatDuration(simulation.elapsed_time || 0)}</small>
                    </div>
                </div>
                <div class="progress mt-2" style="height: 4px;">
                    <div class="progress-bar" style="width: ${simulation.progress || 0}%"></div>
                </div>
            </div>
        `;
        return card;
    }

    /**
     * Update active simulations count
     */
    updateActiveSimulationsCount(count) {
        const countElement = document.getElementById('running-simulations');
        if (countElement) {
            countElement.textContent = count;
        }
    }

    /**
     * Handle model list refresh
     */
    handleModelListRefresh(event) {
        console.log('Model list refresh triggered:', event.detail);
        
        // Refresh model lists in all relevant modules
        this.modelCreationOps.loadAvailableModels();
        
        // Update UI components that display models
        this.updateModelLists();
    }

    /**
     * Handle simulation status update
     */
    handleSimulationStatusUpdate(event) {
        console.log('Simulation status update:', event.detail);
        
        const { simulationId, status } = event.detail;
        
        // Update simulation status in UI
        this.updateSimulationStatus(simulationId, status);
        
        // Update active simulations count
        this.updateActiveSimulationsCountUI();
    }

    /**
     * Update simulation status
     */
    updateSimulationStatus(simulationId, status) {
        // Find and update the simulation card
        const simulationCard = document.querySelector(`[data-simulation-id="${simulationId}"]`);
        if (simulationCard) {
            const statusBadge = simulationCard.querySelector('.badge');
            if (statusBadge) {
                statusBadge.className = `badge bg-${this.utils.getStatusClass(status.status)}`;
                statusBadge.textContent = status.status;
            }
            
            const progressBar = simulationCard.querySelector('.progress-bar');
            if (progressBar && status.progress !== undefined) {
                progressBar.style.width = `${status.progress}%`;
            }
        }
    }

    /**
     * Update active simulations count UI
     */
    async updateActiveSimulationsCountUI() {
        try {
            const result = await this.simulationOps.getActiveSimulationsCount();
            if (result.success) {
                this.updateActiveSimulationsCount(result.data);
            }
        } catch (error) {
            console.error('Error updating active simulations count:', error);
        }
    }

    /**
     * Update model lists
     */
    updateModelLists() {
        // Update model selection dropdowns
        const modelSelects = document.querySelectorAll('[id*="model-select"]');
        modelSelects.forEach(select => {
            if (select.id === 'simulation-model-select') {
                this.populateSimulationModelSelect();
            }
        });
    }

    /**
     * Populate simulation model select
     */
    async populateSimulationModelSelect() {
        const select = document.getElementById('simulation-model-select');
        if (!select) return;

        try {
            const models = await this.modelCreationOps.loadAvailableModels();
            
            // Clear existing options
            select.innerHTML = '<option value="">Select a model...</option>';
            
            // Add model options
            models.forEach(model => {
                const option = document.createElement('option');
                option.value = model.id;
                option.textContent = `${model.name} (${model.physics_type})`;
                select.appendChild(option);
            });
        } catch (error) {
            console.error('Error populating simulation model select:', error);
        }
    }

    /**
     * Handle visibility change
     */
    handleVisibilityChange() {
        if (document.hidden) {
            // Page is hidden, pause some updates
            console.log('Page hidden, pausing updates');
        } else {
            // Page is visible, resume updates
            console.log('Page visible, resuming updates');
            this.loadInitialData();
        }
    }

    /**
     * Handle window resize
     */
    handleWindowResize() {
        // Handle responsive layout adjustments
        console.log('Window resized, adjusting layout');
        
        // Update chart sizes if needed
        this.updateChartSizes();
    }

    /**
     * Update chart sizes
     */
    updateChartSizes() {
        // Update chart containers to fit new window size
        const chartContainers = document.querySelectorAll('.chart-container');
        chartContainers.forEach(container => {
            // Trigger chart resize if charts are implemented
            const event = new Event('resize');
            container.dispatchEvent(event);
        });
    }

    /**
     * Handle before unload
     */
    handleBeforeUnload() {
        // Cleanup resources before page unload
        console.log('Page unloading, cleaning up resources');
        
        // Stop all monitoring intervals
        this.simulationOps.monitoringIntervals.forEach((interval, simulationId) => {
            this.simulationOps.stopSimulationMonitoring(simulationId);
        });
        
        // Save any unsaved state
        this.saveState();
    }

    /**
     * Save current state
     */
    saveState() {
        try {
            const state = {
                currentPage: this.currentPage,
                timestamp: Date.now()
            };
            
            this.utils.setLocalStorage('physics_modeling_state', state);
        } catch (error) {
            console.error('Error saving state:', error);
        }
    }

    /**
     * Load saved state
     */
    loadState() {
        try {
            const state = this.utils.getLocalStorage('physics_modeling_state');
            if (state) {
                this.currentPage = state.currentPage;
            }
        } catch (error) {
            console.error('Error loading state:', error);
        }
    }

    /**
     * Cleanup old notifications
     */
    cleanupOldNotifications() {
        const toasts = document.querySelectorAll('.toast');
        const now = Date.now();
        
        toasts.forEach(toast => {
            const timestamp = toast.getAttribute('data-timestamp');
            if (timestamp && (now - parseInt(timestamp)) > 30000) { // 30 seconds
                toast.remove();
            }
        });
    }

    /**
     * Get module instance
     */
    getModuleInstance(moduleName) {
        return this.moduleInstances.get(moduleName);
    }

    /**
     * Refresh all data
     */
    async refreshAllData() {
        try {
            this.utils.showProgress('Refreshing data...');
            
            // Refresh all data sources
            await Promise.all([
                this.loadSystemStatus(),
                this.modelCreationOps.loadAvailableTwins(),
                this.modelCreationOps.loadAvailableModels(),
                this.loadActiveSimulations()
            ]);
            
            this.utils.hideProgress();
            this.utils.showSuccess('Data refreshed successfully!');
        } catch (error) {
            this.utils.hideProgress();
            this.utils.handleError(error, 'refreshAllData');
        }
    }

    /**
     * Export all data
     */
    async exportAllData() {
        try {
            this.utils.showProgress('Preparing export...');
            
            // Collect all data
            const exportData = {
                timestamp: new Date().toISOString(),
                system_status: await this.api.getSystemStatus(),
                models: await this.modelCreationOps.loadAvailableModels(),
                twins: await this.modelCreationOps.loadAvailableTwins(),
                simulations: await this.simulationOps.listSimulations()
            };
            
            // Create and download file
            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `physics_modeling_export_${Date.now()}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            this.utils.hideProgress();
            this.utils.showSuccess('Data exported successfully!');
        } catch (error) {
            this.utils.hideProgress();
            this.utils.handleError(error, 'exportAllData');
        }
    }

    /**
     * Show model details modal
     */
    async showModelDetails(modelId) {
        try {
            const model = await this.modelCreationOps.getModel(modelId);
            if (model.success) {
                const modal = new bootstrap.Modal(document.getElementById('modelDetailsModal'));
                const content = document.getElementById('modelDetailsContent');
                
                content.innerHTML = `
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Model Information</h6>
                            <table class="table table-sm">
                                <tr><td>Name:</td><td>${model.data.name || 'N/A'}</td></tr>
                                <tr><td>Type:</td><td>${model.data.physics_type || 'N/A'}</td></tr>
                                <tr><td>Status:</td><td><span class="badge bg-success">${model.data.status || 'Active'}</span></td></tr>
                                <tr><td>Created:</td><td>${model.data.created_at || 'N/A'}</td></tr>
                            </table>
                        </div>
                        <div class="col-md-6">
                            <h6>Configuration</h6>
                            <pre class="bg-light p-2 rounded">${JSON.stringify(model.data.configuration || {}, null, 2)}</pre>
                        </div>
                    </div>
                `;
                
                modal.show();
            } else {
                this.utils.showError('Failed to load model details');
            }
        } catch (error) {
            this.utils.handleError(error, 'showModelDetails');
        }
    }

    /**
     * Show simulation results modal
     */
    async showSimulationResults(simulationId) {
        try {
            const results = await this.simulationOps.getSimulationResults(simulationId);
            if (results.success) {
                const modal = new bootstrap.Modal(document.getElementById('simulationResultsModal'));
                const content = document.getElementById('simulationResultsContent');
                
                content.innerHTML = `
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Simulation Results</h6>
                            <table class="table table-sm">
                                <tr><td>Status:</td><td><span class="badge bg-success">${results.data.status || 'Completed'}</span></td></tr>
                                <tr><td>Progress:</td><td>${results.data.progress || 100}%</td></tr>
                                <tr><td>Execution Time:</td><td>${results.data.execution_time || 0}s</td></tr>
                            </table>
                        </div>
                        <div class="col-md-6">
                            <h6>Results Data</h6>
                            <pre class="bg-light p-2 rounded">${JSON.stringify(results.data.results || {}, null, 2)}</pre>
                        </div>
                    </div>
                `;
                
                modal.show();
            } else {
                this.utils.showError('Failed to load simulation results');
            }
        } catch (error) {
            this.utils.handleError(error, 'showSimulationResults');
        }
    }

    /**
     * Explore use case
     */
    async exploreUseCase(useCaseId) {
        try {
            // Get use case details
            const useCaseResponse = await this.api.getUseCase(useCaseId);
            if (!useCaseResponse || !useCaseResponse.id) {
                this.utils.showError('Use case not found');
                return;
            }
            
            const useCase = useCaseResponse;
            
            // Get associated projects
            let projects = [];
            try {
                const projectsResponse = await this.api.getUseCaseProjects(useCaseId);
                if (projectsResponse && projectsResponse.projects) {
                    projects = projectsResponse.projects;
                }
            } catch (projectError) {
                console.warn('Could not load projects for use case:', projectError);
                // Continue without projects
            }
            
            // Show use case details modal with projects
            this.showUseCaseDetailsModal(useCase, projects);
            
        } catch (error) {
            this.utils.handleError(error, 'exploreUseCase');
        }
    }

    /**
     * Show use case details modal with associated projects
     */
    showUseCaseDetailsModal(useCase, projects) {
        // Update modal title
        const modalTitle = document.getElementById('useCaseDetailsModalLabel');
        if (modalTitle) {
            modalTitle.innerHTML = `<i class="fas fa-lightbulb me-2"></i>${useCase.name}`;
        }
        
        // Update modal content
        const modalContent = document.getElementById('useCaseDetailsContent');
        if (modalContent) {
            modalContent.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <h6><i class="fas fa-info-circle me-2"></i>Use Case Details</h6>
                        <p class="text-muted">${useCase.description}</p>
                        <div class="mb-3">
                            <span class="badge bg-primary">${useCase.category}</span>
                            <span class="badge bg-secondary">${useCase.model_type}</span>
                        </div>
                        ${useCase.examples && useCase.examples.length > 0 ? `
                            <div class="mb-3">
                                <strong>Examples:</strong>
                                <ul class="list-unstyled">
                                    ${useCase.examples.map(example => `<li><i class="fas fa-check text-success me-2"></i>${example}</li>`).join('')}
                                </ul>
                            </div>
                        ` : ''}
                    </div>
                    <div class="col-md-6">
                        <h6><i class="fas fa-project-diagram me-2"></i>Associated Projects (${projects.length})</h6>
                        ${projects.length > 0 ? `
                            <div class="list-group">
                                ${projects.map(project => `
                                    <div class="list-group-item">
                                        <div class="d-flex w-100 justify-content-between">
                                            <h6 class="mb-1">${project.name}</h6>
                                            <small class="text-muted">${project.access_level || 'N/A'}</small>
                                        </div>
                                        <p class="mb-1 small">${project.description || 'No description available'}</p>
                                        <small class="text-muted">Created: ${new Date(project.created_at).toLocaleDateString()}</small>
                                    </div>
                                `).join('')}
                            </div>
                        ` : `
                            <div class="text-center text-muted">
                                <i class="fas fa-info-circle fa-2x mb-3"></i>
                                <p>No projects associated with this use case yet.</p>
                            </div>
                        `}
                    </div>
                </div>
            `;
        }
        
        // Update modal footer with create model button
        const modalFooter = document.querySelector('#useCaseDetailsModal .modal-footer');
        if (modalFooter) {
            modalFooter.innerHTML = `
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                <button type="button" class="btn btn-primary" onclick="window.PhysicsModeling.createModelFromUseCase('${useCase.id}')">
                    <i class="fas fa-plus me-2"></i>Create Model from Use Case
                </button>
            `;
        }
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('useCaseDetailsModal'));
        modal.show();
    }

    /**
     * Create model from use case (called from modal)
     */
    createModelFromUseCase(useCaseId) {
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('useCaseDetailsModal'));
        if (modal) {
            modal.hide();
        }
        
        // Switch to model creation tab and pre-populate
        const modelCreationTab = document.getElementById('model-creation-tab');
        if (modelCreationTab) {
            const tab = new bootstrap.Tab(modelCreationTab);
            tab.show();
        }
        
        // Pre-populate the model creation form
        this.api.getUseCase(useCaseId).then(useCase => {
            this.prePopulateModelForm(useCase);
            this.utils.showSuccess(`Loaded use case: ${useCase.name}`);
        }).catch(error => {
            this.utils.handleError(error, 'createModelFromUseCase');
        });
    }

    /**
     * Pre-populate model creation form with use case data
     */
    prePopulateModelForm(useCase) {
        // Set physics type
        const physicsTypeSelect = document.getElementById('physics-type-select');
        if (physicsTypeSelect && useCase.model_type) {
            physicsTypeSelect.value = useCase.model_type;
            // Trigger change event to update dependent fields
            physicsTypeSelect.dispatchEvent(new Event('change'));
        }

        // Set model name with use case prefix
        const modelNameInput = document.getElementById('model-name');
        if (modelNameInput && useCase.name) {
            modelNameInput.value = `${useCase.name} Model`;
        }

        // Store use case data for form submission
        if (this.modelCreationUI) {
            this.modelCreationUI.currentUseCase = useCase;
        }
    }

    /**
     * Public API for external access
     */
    getPublicAPI() {
        return {
            // Model creation
            createModel: (data) => this.modelCreationOps.createModel(data),
            getModels: (filters) => this.modelCreationOps.loadAvailableModels(filters),
            
            // Simulation
            runSimulation: (data) => this.simulationOps.runSimulation(data),
            getSimulationStatus: (id) => this.simulationOps.getSimulationStatus(id),
            cancelSimulation: (id) => this.simulationOps.cancelSimulation(id),
            
            // Visualization
            visualization: {
                threeDViewer: this.threeDViewer,
                charts: this.physicsCharts,
                export: this.physicsExport,
                comparison: this.physicsComparison,
                animation: this.physicsAnimation
            },
            
            // Utilities
            utils: this.utils,
            api: this.api,
            getModuleInstance: this.getModuleInstance.bind(this)
        };
    }
}

// Initialize the main application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.PhysicsModeling = new PhysicsModelingMain();
});

// Export initialization function for template usage
export async function initPhysicsModelingModule() {
    try {
        console.log('🔧 Initializing Physics Modeling Module...');
        const physicsModeling = new PhysicsModelingMain();
        await physicsModeling.init();
        window.PhysicsModeling = physicsModeling;
        console.log('✅ Physics Modeling Module initialized successfully');
        return physicsModeling;
    } catch (error) {
        console.error('❌ Failed to initialize Physics Modeling Module:', error);
        throw error;
    }
}

// Export for module usage
export default PhysicsModelingMain;
