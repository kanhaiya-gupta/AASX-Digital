/**
 * Simulation UI Component
 * Handles simulation interface, controls, and user interactions
 */

export class SimulationUIComponent {
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
            timeStep: 0.01,
            maxIterations: 1000,
            convergenceThreshold: 1e-6,
            outputFormat: 'json'
        };
        
        // UI elements
        this.elements = {
            simulationContainer: null,
            controlPanel: null,
            statusDisplay: null,
            progressBar: null,
            resultsPanel: null,
            parameterForm: null
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
            this.loadUserSimulations();
            this.enableAuthenticatedFeatures();
        } else {
            this.loadDemoSimulations();
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
        
        console.log('🔐 Initializing Simulation UI Component...');
        
        try {
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            this.initializeUI();
            this.setupEventListeners();
            await this.loadSimulationConfiguration();
            
            this.isInitialized = true;
            console.log('✅ Simulation UI Component initialized');
        } catch (error) {
            console.error('❌ Simulation UI Component initialization failed:', error);
            throw error;
        }
    }

    initializeUI() {
        // Initialize UI elements
        this.elements.simulationContainer = document.getElementById('simulation-container');
        this.elements.controlPanel = document.getElementById('simulation-control-panel');
        this.elements.statusDisplay = document.getElementById('simulation-status');
        this.elements.progressBar = document.getElementById('simulation-progress');
        this.elements.resultsPanel = document.getElementById('simulation-results');
        this.elements.parameterForm = document.getElementById('simulation-parameters');

        if (!this.elements.simulationContainer) {
            console.warn('⚠️ Simulation container not found');
            return;
        }

        // Initialize UI state
        this.updateStatusDisplay('Ready');
        this.updateProgressBar(0);
    }

    setupEventListeners() {
        // Start simulation button
        const startBtn = document.getElementById('start-simulation');
        if (startBtn) {
            startBtn.addEventListener('click', () => this.startSimulation());
        }

        // Stop simulation button
        const stopBtn = document.getElementById('stop-simulation');
        if (stopBtn) {
            stopBtn.addEventListener('click', () => this.stopSimulation());
        }

        // Pause simulation button
        const pauseBtn = document.getElementById('pause-simulation');
        if (pauseBtn) {
            pauseBtn.addEventListener('click', () => this.pauseSimulation());
        }

        // Parameter form submission
        if (this.elements.parameterForm) {
            this.elements.parameterForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.updateSimulationParameters();
            });
        }
    }

    async loadSimulationConfiguration() {
        try {
            const response = await fetch('/api/physics-modeling/simulation/config', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const config = await response.json();
                this.simulationConfig = { ...this.simulationConfig, ...config };
                this.updateParameterForm();
            }
        } catch (error) {
            console.error('❌ Failed to load simulation configuration:', error);
        }
    }

    updateParameterForm() {
        if (!this.elements.parameterForm) return;

        // Update form fields with current configuration
        const timeStepInput = this.elements.parameterForm.querySelector('[name="timeStep"]');
        if (timeStepInput) timeStepInput.value = this.simulationConfig.timeStep;

        const maxIterationsInput = this.elements.parameterForm.querySelector('[name="maxIterations"]');
        if (maxIterationsInput) maxIterationsInput.value = this.simulationConfig.maxIterations;

        const convergenceInput = this.elements.parameterForm.querySelector('[name="convergenceThreshold"]');
        if (convergenceInput) convergenceInput.value = this.simulationConfig.convergenceThreshold;
    }

    async startSimulation() {
        try {
            this.updateStatusDisplay('Starting simulation...');
            this.updateProgressBar(0);

            const parameters = this.getFormParameters();
            
            const response = await fetch('/api/physics-modeling/simulation/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeaders()
                },
                body: JSON.stringify(parameters)
            });

            if (response.ok) {
                const result = await response.json();
                this.activeSimulations.push(result.simulationId);
                this.updateStatusDisplay('Simulation running');
                this.startProgressMonitoring(result.simulationId);
            } else {
                throw new Error('Failed to start simulation');
            }
        } catch (error) {
            console.error('❌ Failed to start simulation:', error);
            this.updateStatusDisplay('Failed to start simulation');
        }
    }

    async stopSimulation() {
        try {
            this.updateStatusDisplay('Stopping simulation...');
            
            for (const simulationId of this.activeSimulations) {
                await fetch(`/api/physics-modeling/simulation/${simulationId}/stop`, {
                    method: 'POST',
                    headers: this.getAuthHeaders()
                });
            }
            
            this.activeSimulations = [];
            this.updateStatusDisplay('Simulation stopped');
            this.updateProgressBar(0);
        } catch (error) {
            console.error('❌ Failed to stop simulation:', error);
        }
    }

    async pauseSimulation() {
        try {
            this.updateStatusDisplay('Pausing simulation...');
            
            for (const simulationId of this.activeSimulations) {
                await fetch(`/api/physics-modeling/simulation/${simulationId}/pause`, {
                    method: 'POST',
                    headers: this.getAuthHeaders()
                });
            }
            
            this.updateStatusDisplay('Simulation paused');
        } catch (error) {
            console.error('❌ Failed to pause simulation:', error);
        }
    }

    getFormParameters() {
        if (!this.elements.parameterForm) return {};

        const formData = new FormData(this.elements.parameterForm);
        const parameters = {};
        
        for (const [key, value] of formData.entries()) {
            parameters[key] = parseFloat(value) || value;
        }
        
        return parameters;
    }

    async updateSimulationParameters() {
        try {
            const parameters = this.getFormParameters();
            this.simulationConfig = { ...this.simulationConfig, ...parameters };
            
            const response = await fetch('/api/physics-modeling/simulation/config', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeaders()
                },
                body: JSON.stringify(parameters)
            });

            if (response.ok) {
                console.log('✅ Simulation parameters updated');
            }
        } catch (error) {
            console.error('❌ Failed to update simulation parameters:', error);
        }
    }

    async startProgressMonitoring(simulationId) {
        const checkProgress = async () => {
            try {
                const response = await fetch(`/api/physics-modeling/simulation/${simulationId}/status`, {
                    headers: this.getAuthHeaders()
                });
                
                if (response.ok) {
                    const status = await response.json();
                    this.updateProgressBar(status.progress);
                    this.updateStatusDisplay(status.status);
                    
                    if (status.status === 'completed') {
                        this.loadSimulationResults(simulationId);
                        this.activeSimulations = this.activeSimulations.filter(id => id !== simulationId);
                    } else if (status.status === 'running') {
                        setTimeout(checkProgress, 1000);
                    }
                }
            } catch (error) {
                console.error('❌ Failed to check simulation progress:', error);
            }
        };
        
        checkProgress();
    }

    async loadSimulationResults(simulationId) {
        try {
            const response = await fetch(`/api/physics-modeling/simulation/${simulationId}/results`, {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const results = await response.json();
                this.displayResults(results);
                this.simulationHistory.push(results);
            }
        } catch (error) {
            console.error('❌ Failed to load simulation results:', error);
        }
    }

    displayResults(results) {
        if (!this.elements.resultsPanel) return;

        const resultsHtml = `
            <div class="simulation-result">
                <h4>Simulation Results</h4>
                <div class="result-metrics">
                    <div class="metric">
                        <span class="label">Duration:</span>
                        <span class="value">${results.duration}s</span>
                    </div>
                    <div class="metric">
                        <span class="label">Iterations:</span>
                        <span class="value">${results.iterations}</span>
                    </div>
                    <div class="metric">
                        <span class="label">Convergence:</span>
                        <span class="value">${results.converged ? 'Yes' : 'No'}</span>
                    </div>
                </div>
                <div class="result-data">
                    <pre>${JSON.stringify(results.data, null, 2)}</pre>
                </div>
            </div>
        `;

        this.elements.resultsPanel.innerHTML = resultsHtml;
    }

    updateStatusDisplay(status) {
        if (this.elements.statusDisplay) {
            this.elements.statusDisplay.textContent = status;
        }
    }

    updateProgressBar(progress) {
        if (this.elements.progressBar) {
            this.elements.progressBar.style.width = `${progress}%`;
            this.elements.progressBar.setAttribute('aria-valuenow', progress);
        }
    }

    async loadUserSimulations() {
        try {
            const response = await fetch('/api/physics-modeling/simulation/user', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                this.simulationHistory = data.simulations || [];
                this.displaySimulationHistory();
            }
        } catch (error) {
            console.error('❌ Failed to load user simulations:', error);
        }
    }

    async loadDemoSimulations() {
        try {
            const response = await fetch('/api/physics-modeling/simulation/demo');
            
            if (response.ok) {
                const data = await response.json();
                this.simulationHistory = data.simulations || [];
                this.displaySimulationHistory();
            }
        } catch (error) {
            console.error('❌ Failed to load demo simulations:', error);
        }
    }

    displaySimulationHistory() {
        if (!this.elements.resultsPanel) return;

        const historyHtml = this.simulationHistory.map(sim => `
            <div class="simulation-history-item">
                <div class="simulation-info">
                    <span class="simulation-name">${sim.name}</span>
                    <span class="simulation-date">${new Date(sim.createdAt).toLocaleDateString()}</span>
                </div>
                <div class="simulation-actions">
                    <button onclick="viewSimulation('${sim.id}')" class="btn btn-sm btn-primary">View</button>
                    <button onclick="exportSimulation('${sim.id}')" class="btn btn-sm btn-secondary">Export</button>
                </div>
            </div>
        `).join('');

        this.elements.resultsPanel.innerHTML = `
            <div class="simulation-history">
                <h4>Simulation History</h4>
                ${historyHtml}
            </div>
        `;
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
        console.log('🧹 Cleaning up Simulation UI Component...');
        
        // Remove event listeners
        this.eventListeners.forEach(({ event, handler }) => {
            window.removeEventListener(event, handler);
        });
        
        // Clear sensitive data
        this.clearSensitiveData();
        
        this.isInitialized = false;
        console.log('✅ Simulation UI Component cleaned up');
    }

    async refresh() {
        if (this.isAuthenticated) {
            await this.loadUserSimulations();
        } else {
            await this.loadDemoSimulations();
        }
    }
}
