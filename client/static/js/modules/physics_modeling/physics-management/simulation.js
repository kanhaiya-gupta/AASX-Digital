/**
 * Physics Modeling Simulation Manager
 * Handles simulation lifecycle, execution, and management
 */

export class SimulationManager {
    constructor() {
        // Authentication properties
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
        
        this.isInitialized = false;
        this.activeSimulations = [];
        this.simulationQueue = [];
        this.simulationHistory = [];
        this.simulationConfig = {
            maxConcurrentSimulations: 5,
            defaultTimeout: 3600000, // 1 hour
            autoSaveInterval: 300000, // 5 minutes
            maxRetries: 3
        };
    }

    /**
     * Wait for central authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Simulation Manager: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Simulation Manager: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Simulation Manager: Auth system ready event received');
                window.removeEventListener('authSystemReady', handleReady);
                resolve();
            };
            
            window.addEventListener('authSystemReady', handleReady);
            
            // Fallback: check periodically
            const checkInterval = setInterval(() => {
                if (window.authSystemReady && window.authManager) {
                    clearInterval(checkInterval);
                    window.removeEventListener('authSystemReady', handleReady);
                    resolve();
                }
            }, 100);
            
            // Timeout after 10 seconds
            setTimeout(() => {
                clearInterval(checkInterval);
                window.removeEventListener('authSystemReady', handleReady);
                console.warn('⚠️ Simulation Manager: Timeout waiting for auth system');
                resolve();
            }, 10000);
        });
    }

    /**
     * Update authentication state
     */
    updateAuthState() {
        if (window.authManager) {
            this.isAuthenticated = window.authManager.isAuthenticated();
            this.currentUser = null; // User info not needed currently
            this.authToken = window.authManager.getStoredToken();
            console.log('🔐 Simulation Manager: Auth state updated', {
                isAuthenticated: this.isAuthenticated,
                user: this.currentUser?.username || 'anonymous'
            });
        } else {
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
            console.log('🔐 Simulation Manager: No auth manager available');
        }
    }

    /**
     * Setup authentication event listeners
     */
    setupAuthListeners() {
        window.addEventListener('authStateChanged', () => {
            this.updateAuthState();
        });

        window.addEventListener('loginSuccess', () => {
            this.updateAuthState();
        });

        window.addEventListener('logout', () => {
            this.updateAuthState();
            // Clear sensitive data when user logs out
            this.clearSensitiveData();
        });
    }

    /**
     * Clear sensitive data on logout
     */
    clearSensitiveData() {
        // Clear any cached data that might be user-specific
        this.activeSimulations = [];
        this.simulationQueue = [];
        this.simulationHistory = [];
        console.log('🧹 Simulation Manager: Sensitive data cleared');
    }

    /**
     * Get authentication headers
     */
    getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (this.authToken) {
            headers['Authorization'] = `Bearer ${this.authToken}`;
        }
        
        return headers;
    }

    /**
     * Initialize the simulation manager
     */
    async init() {
        if (this.isInitialized) return;
        
        console.log('🔐 Initializing Simulation Manager...');
        
        try {
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            // Load simulation configuration
            await this.loadSimulationConfiguration();
            
            // Load existing simulations
            await this.loadExistingSimulations();
            
            this.isInitialized = true;
            console.log('✅ Simulation Manager initialized');
            
        } catch (error) {
            console.error('❌ Simulation Manager initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load simulation configuration
     */
    async loadSimulationConfiguration() {
        try {
            const response = await fetch('/api/physics-modeling/simulation/config', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const config = await response.json();
                this.simulationConfig = { ...this.simulationConfig, ...config };
                console.log('✅ Simulation configuration loaded');
            }
        } catch (error) {
            console.warn('⚠️ Could not load simulation config, using defaults:', error);
        }
    }

    /**
     * Load existing simulations
     */
    async loadExistingSimulations() {
        try {
            const response = await fetch('/api/physics-modeling/simulations', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const simulations = await response.json();
                this.activeSimulations = simulations.filter(sim => sim.status === 'running' || sim.status === 'paused');
                this.simulationHistory = simulations.filter(sim => sim.status === 'completed' || sim.status === 'failed');
                console.log(`✅ Loaded ${this.activeSimulations.length} active simulations and ${this.simulationHistory.length} completed simulations`);
            }
        } catch (error) {
            console.warn('⚠️ Could not load existing simulations, using mock data:', error);
            this.loadMockSimulations();
        }
    }

    /**
     * Start a new simulation
     */
    async startSimulation(simulationParams) {
        try {
            console.log('🚀 Starting simulation with params:', simulationParams);
            
            // Validate parameters
            const validation = this.validateSimulationParams(simulationParams);
            if (!validation.isValid) {
                throw new Error(`Invalid simulation parameters: ${validation.errors.join(', ')}`);
            }
            
            // Check if we can start more simulations
            if (this.activeSimulations.length >= this.simulationConfig.maxConcurrentSimulations) {
                throw new Error('Maximum concurrent simulations reached');
            }
            
            // Create simulation object
            const simulation = {
                id: this.generateSimulationId(),
                name: simulationParams.name || `Simulation ${Date.now()}`,
                twinId: simulationParams.twinId,
                pluginId: simulationParams.pluginId,
                parameters: simulationParams.parameters || {},
                status: 'starting',
                startTime: new Date().toISOString(),
                progress: 0,
                estimatedDuration: simulationParams.estimatedDuration || 3600000,
                retryCount: 0
            };
            
            // Add to active simulations
            this.activeSimulations.push(simulation);
            
            // Start the simulation
            await this.executeSimulation(simulation);
            
            // Emit event
            if (window.PhysicsModeling) {
                window.PhysicsModeling.events.emit('simulationStarted', simulation);
            }
            
            console.log('✅ Simulation started successfully:', simulation.id);
            return simulation;
            
        } catch (error) {
            console.error('❌ Error starting simulation:', error);
            throw error;
        }
    }

    /**
     * Execute a simulation
     */
    async executeSimulation(simulation) {
        try {
            console.log(`🔄 Executing simulation ${simulation.id}...`);
            
            // Update status
            simulation.status = 'running';
            simulation.startTime = new Date().toISOString();
            
            // Make API call to start simulation
            const response = await fetch('/api/physics-modeling/simulations/start', {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({
                    simulationId: simulation.id,
                    twinId: simulation.twinId,
                    pluginId: simulation.pluginId,
                    parameters: simulation.parameters
                })
            });
            
            if (!response.ok) {
                throw new Error(`Failed to start simulation: ${response.statusText}`);
            }
            
            // Start progress monitoring
            this.monitorSimulationProgress(simulation);
            
        } catch (error) {
            console.error(`❌ Error executing simulation ${simulation.id}:`, error);
            simulation.status = 'failed';
            simulation.error = error.message;
            
            // Retry logic
            if (simulation.retryCount < this.simulationConfig.maxRetries) {
                simulation.retryCount++;
                console.log(`🔄 Retrying simulation ${simulation.id} (attempt ${simulation.retryCount})`);
                setTimeout(() => this.executeSimulation(simulation), 5000);
            }
        }
    }

    /**
     * Monitor simulation progress
     */
    monitorSimulationProgress(simulation) {
        const progressInterval = setInterval(async () => {
            try {
                // Get progress from API
                const response = await fetch(`/api/physics-modeling/simulations/${simulation.id}/progress`, {
                    headers: this.getAuthHeaders()
                });
                
                if (response.ok) {
                    const progressData = await response.json();
                    simulation.progress = progressData.progress;
                    simulation.status = progressData.status;
                    
                    // Check if simulation is complete
                    if (simulation.status === 'completed' || simulation.status === 'failed') {
                        clearInterval(progressInterval);
                        this.handleSimulationComplete(simulation);
                    }
                }
            } catch (error) {
                console.warn(`⚠️ Error monitoring simulation ${simulation.id} progress:`, error);
            }
        }, 5000); // Check every 5 seconds
    }

    /**
     * Handle simulation completion
     */
    handleSimulationComplete(simulation) {
        console.log(`✅ Simulation ${simulation.id} completed with status: ${simulation.status}`);
        
        // Remove from active simulations
        this.activeSimulations = this.activeSimulations.filter(sim => sim.id !== simulation.id);
        
        // Add to history
        simulation.endTime = new Date().toISOString();
        this.simulationHistory.push(simulation);
        
        // Emit event
        if (window.PhysicsModeling) {
            window.PhysicsModeling.events.emit('simulationCompleted', simulation);
        }
    }

    /**
     * Pause a simulation
     */
    async pauseSimulation(simulationId) {
        try {
            console.log(`⏸️ Pausing simulation ${simulationId}...`);
            
            const simulation = this.activeSimulations.find(sim => sim.id === simulationId);
            if (!simulation) {
                throw new Error('Simulation not found');
            }
            
            if (simulation.status !== 'running') {
                throw new Error('Simulation is not running');
            }
            
            // Make API call to pause simulation
            const response = await fetch(`/api/physics-modeling/simulations/${simulationId}/pause`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });
            
            if (!response.ok) {
                throw new Error(`Failed to pause simulation: ${response.statusText}`);
            }
            
            simulation.status = 'paused';
            console.log(`✅ Simulation ${simulationId} paused successfully`);
            
        } catch (error) {
            console.error(`❌ Error pausing simulation ${simulationId}:`, error);
            throw error;
        }
    }

    /**
     * Resume a simulation
     */
    async resumeSimulation(simulationId) {
        try {
            console.log(`▶️ Resuming simulation ${simulationId}...`);
            
            const simulation = this.activeSimulations.find(sim => sim.id === simulationId);
            if (!simulation) {
                throw new Error('Simulation not found');
            }
            
            if (simulation.status !== 'paused') {
                throw new Error('Simulation is not paused');
            }
            
            // Make API call to resume simulation
            const response = await fetch(`/api/physics-modeling/simulations/${simulationId}/resume`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });
            
            if (!response.ok) {
                throw new Error(`Failed to resume simulation: ${response.statusText}`);
            }
            
            simulation.status = 'running';
            console.log(`✅ Simulation ${simulationId} resumed successfully`);
            
        } catch (error) {
            console.error(`❌ Error resuming simulation ${simulationId}:`, error);
            throw error;
        }
    }

    /**
     * Stop a simulation
     */
    async stopSimulation(simulationId) {
        try {
            console.log(`⏹️ Stopping simulation ${simulationId}...`);
            
            const simulation = this.activeSimulations.find(sim => sim.id === simulationId);
            if (!simulation) {
                throw new Error('Simulation not found');
            }
            
            // Make API call to stop simulation
            const response = await fetch(`/api/physics-modeling/simulations/${simulationId}/stop`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });
            
            if (!response.ok) {
                throw new Error(`Failed to stop simulation: ${response.statusText}`);
            }
            
            simulation.status = 'stopped';
            simulation.endTime = new Date().toISOString();
            
            // Remove from active simulations
            this.activeSimulations = this.activeSimulations.filter(sim => sim.id !== simulationId);
            
            // Add to history
            this.simulationHistory.push(simulation);
            
            console.log(`✅ Simulation ${simulationId} stopped successfully`);
            
        } catch (error) {
            console.error(`❌ Error stopping simulation ${simulationId}:`, error);
            throw error;
        }
    }

    /**
     * Get active simulations
     */
    getActiveSimulations() {
        return [...this.activeSimulations];
    }

    /**
     * Get simulation history
     */
    getSimulationHistory() {
        return [...this.simulationHistory];
    }

    /**
     * Get simulation by ID
     */
    getSimulationById(simulationId) {
        const active = this.activeSimulations.find(sim => sim.id === simulationId);
        if (active) return active;
        
        return this.simulationHistory.find(sim => sim.id === simulationId);
    }

    /**
     * Validate simulation parameters
     */
    validateSimulationParams(params) {
        const errors = [];
        
        if (!params.twinId) {
            errors.push('Digital twin ID is required');
        }
        
        if (!params.pluginId) {
            errors.push('Plugin ID is required');
        }
        
        if (params.estimatedDuration && params.estimatedDuration > this.simulationConfig.defaultTimeout) {
            errors.push(`Estimated duration exceeds maximum allowed time (${this.simulationConfig.defaultTimeout / 60000} minutes)`);
        }
        
        return {
            isValid: errors.length === 0,
            errors: errors
        };
    }

    /**
     * Generate unique simulation ID
     */
    generateSimulationId() {
        return `sim-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Load mock simulations for testing
     */
    loadMockSimulations() {
        this.activeSimulations = [
            {
                id: 'sim-001',
                name: 'Thermal Analysis Simulation',
                twinId: 'twin-001',
                pluginId: 'thermal-plugin-001',
                status: 'running',
                startTime: '2024-01-15T14:00:00Z',
                progress: 65,
                estimatedDuration: 1800000
            },
            {
                id: 'sim-002',
                name: 'Structural Analysis Simulation',
                twinId: 'twin-002',
                pluginId: 'structural-plugin-001',
                status: 'paused',
                startTime: '2024-01-15T13:30:00Z',
                progress: 45,
                estimatedDuration: 2400000
            }
        ];
        
        this.simulationHistory = [
            {
                id: 'sim-003',
                name: 'Fluid Dynamics Simulation',
                twinId: 'twin-003',
                pluginId: 'fluid-plugin-001',
                status: 'completed',
                startTime: '2024-01-15T12:00:00Z',
                endTime: '2024-01-15T13:00:00Z',
                progress: 100,
                estimatedDuration: 3600000
            }
        ];
    }

    /**
     * Cleanup
     */
    destroy() {
        this.activeSimulations = [];
        this.simulationQueue = [];
        this.simulationHistory = [];
        this.isInitialized = false;
        console.log('🧹 Simulation Manager destroyed');
    }
}
