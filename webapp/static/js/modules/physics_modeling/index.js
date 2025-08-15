/**
 * Physics Modeling - Main Entry Point
 * Orchestrates all physics modeling modules and provides the main interface
 */

// Import core modules
import { PhysicsModelingCore } from './physics-management/core.js';
import { SimulationManager } from './physics-management/simulation.js';
import { PluginManager } from './physics-management/plugin-management.js';
import { VisualizationManager } from './physics-management/visualization.js';
import { AnalysisManager } from './physics-management/analysis.js';
import { UseCaseManager } from './physics-management/use-cases.js';
import { SystemManager } from './physics-management/system.js';

// Import UI component modules
import { SimulationUI } from './ui-components/simulation.js';
import { PluginManagementUI } from './ui-components/plugin-management.js';
import { VisualizationUI } from './ui-components/visualization.js';
import { AnalysisUI } from './ui-components/analysis.js';
import { UseCaseUI } from './ui-components/use-cases.js';
import { SystemUI } from './ui-components/system.js';

console.log('📦 Physics Modeling index.js: Module loading started...');

// Global state management
const PhysicsModeling = {
    // Core state
    state: {
        currentTab: 'simulation',
        activeSimulations: [],
        availablePlugins: [],
        systemStatus: 'healthy',
        twins: [],
        ui: {
            loading: false,
            error: null,
            activeModal: null
        }
    },

    // Module instances
    modules: {
        core: null,
        simulation: null,
        pluginManagement: null,
        visualization: null,
        analysis: null,
        useCases: null,
        system: null
    },

    // UI component instances
    ui: {
        simulation: null,
        pluginManagement: null,
        visualization: null,
        analysis: null,
        useCases: null,
        system: null
    },

    // Event system
    events: {
        listeners: {},
        emit(event, data) {
            if (this.listeners[event]) {
                this.listeners[event].forEach(callback => callback(data));
            }
        },
        on(event, callback) {
            if (!this.listeners[event]) {
                this.listeners[event] = [];
            }
            this.listeners[event].push(callback);
        },
        off(event, callback) {
            if (this.listeners[event]) {
                this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
            }
        }
    },

    // Initialize the physics modeling system
    async init() {
        try {
            console.log('🚀 Physics Modeling: Initializing...');
            
            // Wait for central authentication system to be ready
            await new Promise((resolve) => {
                if (window.authSystemReady && window.authManager) {
                    console.log('🔐 Physics Modeling: Auth system already ready');
                    resolve();
                } else {
                    console.log('🔐 Physics Modeling: Waiting for auth system...');
                    const handleReady = () => {
                        console.log('🚀 Physics Modeling: Auth system ready');
                        window.removeEventListener('authSystemReady', handleReady);
                        resolve();
                    };
                    window.addEventListener('authSystemReady', handleReady);
                }
            });
            
            // Initialize core module
            await this.initCore();
            
            // Initialize UI modules
            await this.initUIModules();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Load initial data
            await this.loadInitialData();
            
            console.log('✅ Physics Modeling: Initialized successfully');
            
        } catch (error) {
            console.error('❌ Error initializing Physics Modeling:', error);
            this.showError('Failed to initialize Physics Modeling');
        }
    },

    // Initialize core functionality
    async initCore() {
        console.log('📋 Physics Modeling: Initializing core module...');
        
        // Initialize imported modules
        this.modules.core = new PhysicsModelingCore();
        this.modules.simulation = new SimulationManager();
        this.modules.pluginManagement = new PluginManager();
        this.modules.visualization = new VisualizationManager();
        this.modules.analysis = new AnalysisManager();
        this.modules.useCases = new UseCaseManager();
        this.modules.system = new SystemManager();
        
        console.log('✅ Physics Modeling: Core module initialized');
    },

    // Initialize UI modules
    async initUIModules() {
        console.log('🎨 Physics Modeling: Initializing UI modules...');
        
        // Initialize UI component modules
        this.ui.simulation = new SimulationUI();
        this.ui.pluginManagement = new PluginManagementUI();
        this.ui.visualization = new VisualizationUI();
        this.ui.analysis = new AnalysisUI();
        this.ui.useCases = new UseCaseUI();
        this.ui.system = new SystemUI();
        
        // Initialize UI components
        await this.ui.simulation.init();
        await this.ui.pluginManagement.init();
        await this.ui.visualization.init();
        await this.ui.analysis.init();
        await this.ui.useCases.init();
        await this.ui.system.init();
        
        console.log('✅ Physics Modeling: UI modules initialized');
    },

    // Setup event listeners
    setupEventListeners() {
        console.log('🔗 Physics Modeling: Setting up event listeners...');
        
        // Tab switching
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-bs-toggle="tab"]')) {
                const targetTab = e.target.getAttribute('data-bs-target').replace('#', '');
                this.switchTab(targetTab);
            }
        });
        
        // Global physics modeling events
        this.events.on('simulationStarted', (data) => {
            this.handleSimulationStarted(data);
        });
        
        this.events.on('simulationCompleted', (data) => {
            this.handleSimulationCompleted(data);
        });
        
        this.events.on('pluginInstalled', (data) => {
            this.handlePluginInstalled(data);
        });
        
        console.log('✅ Physics Modeling: Event listeners setup complete');
    },

    // Load initial data
    async loadInitialData() {
        try {
            console.log('📊 Physics Modeling: Loading initial data...');
            
            this.setLoading(true);
            
            // Load system status
            const systemStatus = await this.modules.core.getSystemStatus();
            this.state.systemStatus = systemStatus.status;
            
            // Load available twins
            const twins = await this.modules.core.getAvailableTwins();
            this.state.twins = twins;
            
            // Load active simulations
            const simulations = await this.modules.simulation.getActiveSimulations();
            this.state.activeSimulations = simulations;
            
            // Load available plugins
            const plugins = await this.modules.pluginManagement.getAvailablePlugins();
            this.state.availablePlugins = plugins;
            
            // Update UI
            this.updateStatusDashboard();
            
            this.setLoading(false);
            
            console.log('✅ Physics Modeling: Initial data loaded');
            
        } catch (error) {
            console.error('❌ Error loading initial data:', error);
            this.setLoading(false);
            this.showError('Failed to load initial data');
        }
    },

    // Switch tabs
    switchTab(tabName) {
        console.log('🔄 Switching to tab:', tabName);
        this.state.currentTab = tabName;
        
        // Update active tab styling
        document.querySelectorAll('.pm-tab-link').forEach(tab => {
            tab.classList.remove('active');
        });
        
        const activeTab = document.querySelector(`[data-bs-target="#${tabName}"]`);
        if (activeTab) {
            activeTab.classList.add('active');
        }
        
        // Emit tab change event
        this.events.emit('tabChanged', { tab: tabName });
    },

    // Handle simulation started
    handleSimulationStarted(data) {
        console.log('🚀 Simulation started:', data);
        this.state.activeSimulations.push(data);
        this.updateStatusDashboard();
        this.showSuccess(`Simulation "${data.name}" started successfully`);
    },

    // Handle simulation completed
    handleSimulationCompleted(data) {
        console.log('✅ Simulation completed:', data);
        this.state.activeSimulations = this.state.activeSimulations.filter(
            sim => sim.id !== data.id
        );
        this.updateStatusDashboard();
        this.showSuccess(`Simulation "${data.name}" completed successfully`);
    },

    // Handle plugin installed
    handlePluginInstalled(data) {
        console.log('🔌 Plugin installed:', data);
        this.state.availablePlugins.push(data);
        this.updateStatusDashboard();
        this.showSuccess(`Plugin "${data.name}" installed successfully`);
    },

    // Update status dashboard
    updateStatusDashboard() {
        // Update plugin count
        const totalPlugins = document.getElementById('total-plugins');
        if (totalPlugins) {
            totalPlugins.textContent = this.state.availablePlugins.length;
        }
        
        // Update active simulations count
        const activeSimulations = document.getElementById('active-simulations');
        if (activeSimulations) {
            activeSimulations.textContent = this.state.activeSimulations.length;
        }
        
        // Update available twins count
        const availableTwins = document.getElementById('available-twins');
        if (availableTwins) {
            availableTwins.textContent = this.state.twins.length;
        }
        
        // Update system status
        const systemStatus = document.getElementById('system-status');
        if (systemStatus) {
            systemStatus.textContent = this.state.systemStatus;
        }
    },

    // Set loading state
    setLoading(loading) {
        this.state.ui.loading = loading;
        
        // Show/hide loading indicator
        const loadingIndicator = document.getElementById('physics-loading');
        if (loadingIndicator) {
            loadingIndicator.style.display = loading ? 'block' : 'none';
        }
        
        // Disable/enable buttons during loading
        const buttons = document.querySelectorAll('.pm-btn');
        buttons.forEach(button => {
            button.disabled = loading;
        });
    },

    // Show error message
    showError(message) {
        console.error('❌ Error:', message);
        this.state.ui.error = message;
        
        if (typeof showNotification === 'function') {
            showNotification(message, 'error');
        } else {
            alert('Error: ' + message);
        }
    },

    // Show success message
    showSuccess(message) {
        console.log('✅ Success:', message);
        
        if (typeof showNotification === 'function') {
            showNotification(message, 'success');
        }
    },

    // Global functions for template access
    startSimulation() {
        console.log('Start simulation clicked');
        this.ui.simulation.showStartSimulationModal();
    },

    refreshDashboard() {
        console.log('Refresh dashboard clicked');
        this.loadInitialData();
    },

    installPlugin() {
        console.log('Install plugin clicked');
        this.ui.pluginManagement.showInstallPluginModal();
    },

    viewSimulation(simulationId) {
        console.log('View simulation clicked:', simulationId);
        this.ui.simulation.showSimulationDetails(simulationId);
    },

    pauseSimulation(simulationId) {
        console.log('Pause simulation clicked:', simulationId);
        this.modules.simulation.pauseSimulation(simulationId);
    },

    resumeSimulation(simulationId) {
        console.log('Resume simulation clicked:', simulationId);
        this.modules.simulation.resumeSimulation(simulationId);
    },

    stopSimulation(simulationId) {
        console.log('Stop simulation clicked:', simulationId);
        this.modules.simulation.stopSimulation(simulationId);
    },

    exportResults() {
        console.log('Export results clicked');
        this.ui.visualization.showExportModal();
    }
};

// Export the initialization function for ES6 module import
export async function initPhysicsModeling() {
    console.log('🚀 Physics Modeling: Starting initialization...');
    
    try {
        await PhysicsModeling.init();
        console.log('✅ Physics Modeling: Initialization complete');
        
        // Make PhysicsModeling globally available for template functions
        window.PhysicsModeling = PhysicsModeling;
        
        // Global functions for template access
        window.startSimulation = () => PhysicsModeling.startSimulation();
        window.refreshDashboard = () => PhysicsModeling.refreshDashboard();
        window.installPlugin = () => PhysicsModeling.installPlugin();
        window.viewSimulation = (id) => PhysicsModeling.viewSimulation(id);
        window.pauseSimulation = (id) => PhysicsModeling.pauseSimulation(id);
        window.resumeSimulation = (id) => PhysicsModeling.resumeSimulation(id);
        window.stopSimulation = (id) => PhysicsModeling.stopSimulation(id);
        window.exportResults = () => PhysicsModeling.exportResults();
        
        return PhysicsModeling;
        
    } catch (error) {
        console.error('❌ Physics Modeling: Initialization failed:', error);
        throw error;
    }
}

console.log('✅ Physics Modeling index.js: Module loading complete');

// Global initialization function for post-login orchestrator
window.initializePhysicsModelingIfNeeded = async function() {
    console.log('🔐 Physics Modeling: Checking if initialization is needed...');
    
    if (!window.PhysicsModeling || !window.PhysicsModeling.state) {
        console.log('🚀 Physics Modeling: Initializing from post-login orchestrator...');
        try {
            await initPhysicsModeling();
            console.log('✅ Physics Modeling: Initialized from post-login orchestrator');
        } catch (error) {
            console.error('❌ Physics Modeling: Failed to initialize from post-login orchestrator:', error);
        }
    } else {
        console.log('✅ Physics Modeling: Already initialized, skipping');
    }
};
