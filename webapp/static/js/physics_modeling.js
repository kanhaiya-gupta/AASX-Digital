/**
 * Physics Modeling Frontend JavaScript
 * Handles the physics modeling GUI interactions and API calls
 */

class PhysicsModelingUI {
    constructor() {
        this.currentSimulation = null;
        this.activeSimulations = new Map();
        this.availableModels = [];
        this.availableTwins = [];
        this.systemStatus = {};
        
        this.init();
    }

    async init() {
        console.log('Initializing Physics Modeling UI...');
        
        // Initialize event listeners
        this.setupEventListeners();
        
        // Load initial data
        await this.loadSystemStatus();
        await this.loadAvailableTwins();
        await this.loadAvailableModels();
        
        // Load use cases
        await this.loadAllUseCases();
        
        // Start status updates
        this.startStatusUpdates();
        
        console.log('Physics Modeling UI initialized successfully');
    }

    setupEventListeners() {
        // Model creation form
        document.getElementById('model-creation-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.createPhysicsModel();
        });

        // Twin selection change
        document.getElementById('twin-select').addEventListener('change', (e) => {
            this.onTwinSelectionChange(e.target.value);
        });

        // Refresh twins button
        document.getElementById('refresh-twins-btn').addEventListener('click', async () => {
            await this.refreshTwins();
        });

        // Physics type selection change
        document.getElementById('physics-type-select').addEventListener('change', (e) => {
            this.onPhysicsTypeChange(e.target.value);
        });

        // Simulation controls
        document.getElementById('start-simulation-btn').addEventListener('click', () => {
            this.startSimulation();
        });

        document.getElementById('pause-simulation-btn').addEventListener('click', () => {
            this.pauseSimulation();
        });

        document.getElementById('stop-simulation-btn').addEventListener('click', () => {
            this.stopSimulation();
        });

        // Validation
        document.getElementById('validate-model-btn').addEventListener('click', () => {
            this.validateModel();
        });

        // Configuration validation
        document.getElementById('validate-config-btn').addEventListener('click', () => {
            this.validateConfiguration();
        });

        // Template loading
        document.getElementById('load-template-btn').addEventListener('click', () => {
            this.loadTemplate();
        });

        // Visualization controls
        document.getElementById('visualization-type').addEventListener('change', (e) => {
            this.updateVisualization(e.target.value);
        });

        document.getElementById('visualization-variable').addEventListener('change', (e) => {
            this.updateVisualizationVariable(e.target.value);
        });

        document.getElementById('time-slider').addEventListener('input', (e) => {
            this.updateTimeStep(e.target.value);
        });

        // Export results
        document.getElementById('export-results-btn').addEventListener('click', () => {
            this.exportResults();
        });

        // Use Cases functionality
        document.getElementById('load-all-use-cases-btn').addEventListener('click', () => {
            this.loadAllUseCases();
        });

        document.getElementById('famous-examples-btn').addEventListener('click', () => {
            this.showFamousExamples();
        });

        document.getElementById('optimization-targets-btn').addEventListener('click', () => {
            this.showOptimizationTargets();
        });

        document.getElementById('hydrogen-economy-btn').addEventListener('click', () => {
            this.showHydrogenEconomy();
        });

        // Tab change events for use cases
        document.querySelectorAll('#useCaseTabs button[data-bs-toggle="tab"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                const target = e.target.getAttribute('data-bs-target').substring(1);
                this.loadUseCasesForCategory(target);
            });
        });
    }

    async loadSystemStatus() {
        try {
            const response = await fetch('/physics-modeling/api/status');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            this.systemStatus = await response.json();
            this.updateStatusIndicators();
            this.updateSystemInfo();
        } catch (error) {
            console.error('Error loading system status:', error);
            this.showError('Failed to load system status');
        }
    }

    async loadAvailableTwins() {
        try {
            const response = await fetch('/physics-modeling/api/twins');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            this.availableTwins = data.twins || data;
            this.populateTwinSelect();
        } catch (error) {
            console.error('Error loading available twins:', error);
            this.showError('Failed to load available twins');
        }
    }

    async loadAvailableModels() {
        try {
            const response = await fetch('/physics-modeling/api/models');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            this.availableModels = data.models || data;
            this.populateModelsList();
            this.populateSimulationModelSelect();
        } catch (error) {
            console.error('Error loading available models:', error);
            this.showError('Failed to load available models');
        }
    }

    populateTwinSelect() {
        const select = document.getElementById('twin-select');
        select.innerHTML = '<option value="">Select a digital twin...</option>';
        
        if (!this.availableTwins || this.availableTwins.length === 0) {
            select.innerHTML = '<option value="" disabled>No digital twins available</option>';
            return;
        }
        
        this.availableTwins.forEach(twin => {
            const option = document.createElement('option');
            option.value = twin.twin_id;
            
            // Create a more informative display text
            let displayText = `${twin.name}`;
            
            // Add type if available
            if (twin.type) {
                displayText += ` (${twin.type})`;
            }
            
            // Add data points if available
            if (twin.data_points) {
                displayText += ` - ${twin.data_points} data points`;
            }
            
            // Add status indicator
            const status = twin.status || 'unknown';
            const statusIcon = status === 'active' ? '🟢' : status === 'inactive' ? '🔴' : '🟡';
            displayText += ` ${statusIcon}`;
            
            option.textContent = displayText;
            
            // Add description as title attribute for tooltip
            if (twin.description) {
                option.title = twin.description;
            }
            
            select.appendChild(option);
        });
        
        // Add a refresh button or indicator if twins were loaded
        if (this.availableTwins.length > 0) {
            console.log(`✅ Loaded ${this.availableTwins.length} digital twins`);
        }
    }

    populateModelsList() {
        const container = document.getElementById('models-list');
        container.innerHTML = '';

        if (this.availableModels.length === 0) {
            container.innerHTML = '<p class="text-muted text-center">No models available</p>';
            return;
        }

        this.availableModels.forEach(model => {
            const modelCard = this.createModelCard(model);
            container.appendChild(modelCard);
        });
    }

    createModelCard(model) {
        const card = document.createElement('div');
        card.className = 'card mb-2 border-0 bg-light';
        
        const statusClass = this.getStatusClass(model.status);
        const statusIcon = this.getStatusIcon(model.status);
        
        card.innerHTML = `
            <div class="card-body p-2">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="mb-1">${model.name}</h6>
                        <small class="text-muted d-block">
                            <i class="fas fa-atom me-1"></i>${model.type}
                        </small>
                        <small class="text-muted">
                            <i class="fas fa-clock me-1"></i>${new Date(model.created_at).toLocaleDateString()}
                        </small>
                    </div>
                    <div class="text-end">
                        <span class="badge ${statusClass}">${statusIcon} ${model.status}</span>
                    </div>
                </div>
                <div class="mt-2">
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="physicsUI.runModel('${model.model_id}')">
                        <i class="fas fa-play"></i> Run
                    </button>
                    <button class="btn btn-sm btn-outline-info me-1" onclick="physicsUI.viewModel('${model.model_id}')">
                        <i class="fas fa-eye"></i> View
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="physicsUI.deleteModel('${model.model_id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
        
        return card;
    }

    populateSimulationModelSelect() {
        const select = document.getElementById('simulation-model-select');
        select.innerHTML = '<option value="">Select a model...</option>';
        
        this.availableModels
            .filter(model => model.status === 'ready')
            .forEach(model => {
                const option = document.createElement('option');
                option.value = model.model_id;
                option.textContent = model.name;
                select.appendChild(option);
            });
    }

    updateStatusIndicators() {
        // Update physics framework status
        const frameworkStatus = document.getElementById('status-physics-framework');
        if (this.systemStatus.physics_framework_available) {
            frameworkStatus.innerHTML = '<i class="fas fa-atom fa-2x text-success"></i>';
        } else {
            frameworkStatus.innerHTML = '<i class="fas fa-atom fa-2x text-danger"></i>';
        }

        // Update twin connector status
        const twinStatus = document.getElementById('status-twin-connector');
        if (this.systemStatus.twin_connector_status === 'connected') {
            twinStatus.innerHTML = '<i class="fas fa-link fa-2x text-success"></i>';
        } else {
            twinStatus.innerHTML = '<i class="fas fa-link fa-2x text-danger"></i>';
        }

        // Update AI/RAG status
        const aiRagStatus = document.getElementById('status-ai-rag');
        if (this.systemStatus.ai_rag_connector_status === 'connected') {
            aiRagStatus.innerHTML = '<i class="fas fa-brain fa-2x text-success"></i>';
        } else {
            aiRagStatus.innerHTML = '<i class="fas fa-brain fa-2x text-danger"></i>';
        }

        // Update models count
        const modelsStatus = document.getElementById('status-models');
        modelsStatus.innerHTML = `<i class="fas fa-cube fa-2x text-info"></i><br><small>${this.systemStatus.available_models}</small>`;

        // Update simulations count
        const simulationsStatus = document.getElementById('status-simulations');
        simulationsStatus.innerHTML = `<i class="fas fa-play-circle fa-2x text-warning"></i><br><small>${this.systemStatus.active_simulations}</small>`;

        // Update validation status
        const validationStatus = document.getElementById('status-validation');
        validationStatus.innerHTML = '<i class="fas fa-check-circle fa-2x text-success"></i>';
    }

    updateSystemInfo() {
        document.getElementById('models-count').textContent = this.systemStatus.available_models || 0;
        document.getElementById('simulations-count').textContent = this.systemStatus.active_simulations || 0;
        document.getElementById('twins-count').textContent = this.availableTwins.length;
        document.getElementById('validations-count').textContent = '0'; // TODO: Add validation count
    }

    async createPhysicsModel() {
        const formData = this.getFormData();
        
        if (!formData.twin_id || !formData.model_type) {
            this.showError('Please select a digital twin and physics type');
            return;
        }

        this.showProgress('Creating physics model...');

        try {
            const response = await fetch('/physics-modeling/api/models/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                const result = await response.json();
                this.hideProgress();
                this.showSuccess(`Physics model created successfully! Model ID: ${result.model_id}`);
                
                // Reload models list
                await this.loadAvailableModels();
                
                // Reset form
                document.getElementById('model-creation-form').reset();
                
            } else {
                const error = await response.json();
                this.hideProgress();
                this.showError(`Failed to create model: ${error.detail}`);
            }
        } catch (error) {
            this.hideProgress();
            console.error('Error creating physics model:', error);
            this.showError('Failed to create physics model');
        }
    }

    getFormData() {
        const twinId = document.getElementById('twin-select').value;
        const modelType = document.getElementById('physics-type-select').value;
        const solverSettings = document.getElementById('solver-select').value;
        const useAiInsights = document.getElementById('ai-insights-toggle').checked;
        
        let materialProperties = {};
        let boundaryConditions = {};
        
        try {
            const materialText = document.getElementById('material-properties').value;
            if (materialText) {
                materialProperties = JSON.parse(materialText);
            }
        } catch (e) {
            console.warn('Invalid material properties JSON');
        }
        
        try {
            const boundaryText = document.getElementById('boundary-conditions').value;
            if (boundaryText) {
                boundaryConditions = JSON.parse(boundaryText);
            }
        } catch (e) {
            console.warn('Invalid boundary conditions JSON');
        }

        return {
            twin_id: twinId,
            model_type: modelType,
            material_properties: materialProperties,
            boundary_conditions: boundaryConditions,
            solver_settings: { solver: solverSettings },
            use_ai_insights: useAiInsights
        };
    }

    async startSimulation() {
        const modelId = document.getElementById('simulation-model-select').value;
        const simulationType = document.getElementById('simulation-type-select').value;
        const timeRange = parseFloat(document.getElementById('time-range').value);

        if (!modelId) {
            this.showError('Please select a model to simulate');
            return;
        }

        this.showProgress('Starting simulation...');

        try {
            const response = await fetch('/physics-modeling/api/simulations/run', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    model_id: modelId,
                    simulation_type: simulationType,
                    time_range: { end_time: timeRange }
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.hideProgress();
                this.showSuccess(`Simulation started! ID: ${result.simulation_id}`);
                
                // Add to active simulations
                this.activeSimulations.set(result.simulation_id, {
                    ...result,
                    startTime: new Date()
                });
                
                this.updateActiveSimulations();
                this.monitorSimulation(result.simulation_id);
                
            } else {
                const error = await response.json();
                this.hideProgress();
                this.showError(`Failed to start simulation: ${error.detail}`);
            }
        } catch (error) {
            this.hideProgress();
            console.error('Error starting simulation:', error);
            this.showError('Failed to start simulation');
        }
    }

    async monitorSimulation(simulationId) {
        const checkStatus = async () => {
            try {
                const response = await fetch(`/physics-modeling/api/simulations/${simulationId}/status`);
                if (response.ok) {
                    const status = await response.json();
                    
                    // Update active simulations
                    if (this.activeSimulations.has(simulationId)) {
                        this.activeSimulations.set(simulationId, {
                            ...this.activeSimulations.get(simulationId),
                            ...status
                        });
                    }
                    
                    this.updateActiveSimulations();
                    
                    if (status.status === 'completed') {
                        this.showSuccess(`Simulation ${simulationId} completed successfully!`);
                        this.displayResults(status);
                        this.activeSimulations.delete(simulationId);
                        this.updateActiveSimulations();
                    } else if (status.status === 'failed') {
                        this.showError(`Simulation ${simulationId} failed: ${status.error}`);
                        this.activeSimulations.delete(simulationId);
                        this.updateActiveSimulations();
                    } else {
                        // Continue monitoring
                        setTimeout(checkStatus, 2000);
                    }
                }
            } catch (error) {
                console.error('Error monitoring simulation:', error);
            }
        };
        
        checkStatus();
    }

    updateActiveSimulations() {
        const container = document.getElementById('active-simulations');
        container.innerHTML = '';

        if (this.activeSimulations.size === 0) {
            container.innerHTML = '<p class="text-muted text-center">No active simulations</p>';
            return;
        }

        this.activeSimulations.forEach((simulation, id) => {
            const simulationCard = this.createSimulationCard(simulation, id);
            container.appendChild(simulationCard);
        });
    }

    createSimulationCard(simulation, id) {
        const card = document.createElement('div');
        card.className = 'card mb-2 border-0 bg-light';
        
        const progress = simulation.progress || 0;
        const statusClass = simulation.status === 'running' ? 'text-success' : 'text-warning';
        
        card.innerHTML = `
            <div class="card-body p-2">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="mb-1">Simulation ${id.slice(0, 8)}</h6>
                        <small class="text-muted d-block">
                            <i class="fas fa-cube me-1"></i>Model: ${simulation.model_id}
                        </small>
                        <small class="text-muted">
                            <i class="fas fa-clock me-1"></i>${simulation.execution_time.toFixed(1)}s
                        </small>
                    </div>
                    <div class="text-end">
                        <span class="badge ${statusClass}">${simulation.status}</span>
                    </div>
                </div>
                <div class="progress mt-2" style="height: 4px;">
                    <div class="progress-bar" style="width: ${progress}%"></div>
                </div>
                <small class="text-muted">${progress.toFixed(1)}% complete</small>
            </div>
        `;
        
        return card;
    }

    async validateModel() {
        const modelId = document.getElementById('simulation-model-select').value;
        const validationData = document.getElementById('validation-data').value;

        if (!modelId) {
            this.showError('Please select a model to validate');
            return;
        }

        if (!validationData) {
            this.showError('Please provide validation data');
            return;
        }

        let parsedData;
        try {
            parsedData = JSON.parse(validationData);
        } catch (e) {
            this.showError('Invalid JSON format for validation data');
            return;
        }

        this.showProgress('Validating model...');

        try {
            const response = await fetch('/physics-modeling/api/models/validate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    model_id: modelId,
                    validation_data: parsedData
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.hideProgress();
                this.showValidationResults(result);
            } else {
                const error = await response.json();
                this.hideProgress();
                this.showError(`Validation failed: ${error.detail}`);
            }
        } catch (error) {
            this.hideProgress();
            console.error('Error validating model:', error);
            this.showError('Failed to validate model');
        }
    }

    showValidationResults(result) {
        const container = document.getElementById('validation-results');
        container.style.display = 'block';
        
        container.innerHTML = `
            <div class="card border-success">
                <div class="card-body">
                    <h6 class="card-title text-success">
                        <i class="fas fa-check-circle me-1"></i>Validation Complete
                    </h6>
                    <div class="row">
                        <div class="col-6">
                            <p class="mb-1"><strong>Accuracy Score:</strong></p>
                            <h4 class="text-success">${(result.accuracy_score * 100).toFixed(1)}%</h4>
                        </div>
                        <div class="col-6">
                            <p class="mb-1"><strong>Status:</strong></p>
                            <span class="badge bg-success">${result.status}</span>
                        </div>
                    </div>
                    <div class="mt-3">
                        <h6>Metrics:</h6>
                        <ul class="list-unstyled">
                            <li><strong>RMSE:</strong> ${result.validation_metrics.rmse}</li>
                            <li><strong>MAE:</strong> ${result.validation_metrics.mae}</li>
                            <li><strong>R²:</strong> ${result.validation_metrics.r_squared}</li>
                            <li><strong>Correlation:</strong> ${result.validation_metrics.correlation}</li>
                        </ul>
                    </div>
                </div>
            </div>
        `;
    }

    validateConfiguration() {
        const formData = this.getFormData();
        let isValid = true;
        let errors = [];

        if (!formData.twin_id) {
            errors.push('Digital twin is required');
            isValid = false;
        }

        if (!formData.model_type) {
            errors.push('Physics type is required');
            isValid = false;
        }

        if (errors.length > 0) {
            this.showError('Configuration validation failed:\n' + errors.join('\n'));
        } else {
            this.showSuccess('Configuration is valid!');
        }
    }

    loadTemplate() {
        const modelType = document.getElementById('physics-type-select').value;
        
        if (!modelType) {
            this.showError('Please select a physics type first');
            return;
        }

        const templates = {
            thermal: {
                material_properties: {
                    density: 7850,
                    thermal_conductivity: 50,
                    specific_heat: 460,
                    emissivity: 0.8
                },
                boundary_conditions: {
                    temperature: 25,
                    heat_flux: 1000,
                    convection_coefficient: 10
                }
            },
            structural: {
                material_properties: {
                    density: 7850,
                    youngs_modulus: 200e9,
                    poissons_ratio: 0.3,
                    yield_strength: 250e6
                },
                boundary_conditions: {
                    displacement: 0,
                    force: 1000,
                    pressure: 1e6
                }
            },
            fluid: {
                material_properties: {
                    density: 1000,
                    viscosity: 1e-3,
                    thermal_conductivity: 0.6
                },
                boundary_conditions: {
                    velocity: 1.0,
                    pressure: 101325,
                    temperature: 20
                }
            }
        };

        const template = templates[modelType];
        if (template) {
            document.getElementById('material-properties').value = JSON.stringify(template.material_properties, null, 2);
            document.getElementById('boundary-conditions').value = JSON.stringify(template.boundary_conditions, null, 2);
            this.showSuccess(`Loaded ${modelType} template`);
        } else {
            this.showError('No template available for selected physics type');
        }
    }

    onTwinSelectionChange(twinId) {
        if (twinId) {
            const twin = this.availableTwins.find(t => t.twin_id === twinId);
            if (twin) {
                // Update physics type options based on available physics
                this.updatePhysicsTypeOptions(twin.available_physics);
            }
        }
    }

    updatePhysicsTypeOptions(availablePhysics) {
        const select = document.getElementById('physics-type-select');
        const currentValue = select.value;
        
        select.innerHTML = '<option value="">Select physics type...</option>';
        
        const physicsTypes = {
            thermal: 'Thermal Analysis',
            structural: 'Structural Analysis',
            fluid: 'Fluid Dynamics',
            electromagnetic: 'Electromagnetic',
            multi_physics: 'Multi-Physics'
        };
        
        availablePhysics.forEach(physics => {
            if (physicsTypes[physics]) {
                const option = document.createElement('option');
                option.value = physics;
                option.textContent = physicsTypes[physics];
                select.appendChild(option);
            }
        });
        
        // Restore previous selection if still valid
        if (currentValue && availablePhysics.includes(currentValue)) {
            select.value = currentValue;
        }
    }

    onPhysicsTypeChange(physicsType) {
        // Update solver options based on physics type
        const solverSelect = document.getElementById('solver-select');
        
        const solverOptions = {
            thermal: ['fenics', 'sfepy'],
            structural: ['fenics', 'sfepy'],
            fluid: ['openfoam', 'fenics'],
            electromagnetic: ['fenics', 'custom'],
            multi_physics: ['fenics', 'openfoam', 'custom']
        };
        
        if (solverOptions[physicsType]) {
            solverSelect.innerHTML = '';
            solverOptions[physicsType].forEach(solver => {
                const option = document.createElement('option');
                option.value = solver;
                option.textContent = this.getSolverDisplayName(solver);
                solverSelect.appendChild(option);
            });
        }
    }

    getSolverDisplayName(solver) {
        const names = {
            fenics: 'FEniCS (FEA)',
            openfoam: 'OpenFOAM (CFD)',
            sfepy: 'SfePy (FEA)',
            custom: 'Custom Solver'
        };
        return names[solver] || solver;
    }

    getStatusClass(status) {
        const classes = {
            ready: 'bg-success',
            training: 'bg-warning',
            error: 'bg-danger',
            completed: 'bg-info'
        };
        return classes[status] || 'bg-secondary';
    }

    getStatusIcon(status) {
        const icons = {
            ready: 'fas fa-check',
            training: 'fas fa-spinner fa-spin',
            error: 'fas fa-exclamation-triangle',
            completed: 'fas fa-flag-checkered'
        };
        return icons[status] || 'fas fa-question';
    }

    displayResults(results) {
        const modal = new bootstrap.Modal(document.getElementById('resultsModal'));
        const content = document.getElementById('results-content');
        
        content.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Simulation Results</h6>
                    <ul class="list-unstyled">
                        <li><strong>Execution Time:</strong> ${results.execution_time.toFixed(2)}s</li>
                        <li><strong>Status:</strong> ${results.status}</li>
                        <li><strong>Progress:</strong> ${results.progress.toFixed(1)}%</li>
                    </ul>
                </div>
                <div class="col-md-6">
                    <h6>Results Summary</h6>
                    <div id="results-chart" style="height: 200px;"></div>
                </div>
            </div>
            <div class="mt-3">
                <h6>Raw Data</h6>
                <pre class="bg-light p-2 rounded"><code>${JSON.stringify(results.results, null, 2)}</code></pre>
            </div>
        `;
        
        modal.show();
    }

    updateVisualization(type) {
        console.log('Updating visualization type:', type);
        // TODO: Implement visualization updates
    }

    updateVisualizationVariable(variable) {
        console.log('Updating visualization variable:', variable);
        // TODO: Implement variable updates
    }

    updateTimeStep(time) {
        document.getElementById('time-display').textContent = `${time}s`;
        // TODO: Implement time step updates
    }

    exportResults() {
        // TODO: Implement results export
        this.showSuccess('Results exported successfully!');
    }

    pauseSimulation() {
        // TODO: Implement simulation pause
        this.showInfo('Simulation paused');
    }

    stopSimulation() {
        // TODO: Implement simulation stop
        this.showInfo('Simulation stopped');
    }

    runModel(modelId) {
        document.getElementById('simulation-model-select').value = modelId;
        this.showInfo('Model selected for simulation');
    }

    viewModel(modelId) {
        // TODO: Implement model viewing
        this.showInfo('Opening model viewer...');
    }

    deleteModel(modelId) {
        if (confirm('Are you sure you want to delete this model?')) {
            // TODO: Implement model deletion
            this.showSuccess('Model deleted successfully');
        }
    }

    startStatusUpdates() {
        // Update status every 30 seconds
        setInterval(() => {
            this.loadSystemStatus();
        }, 30000);
    }

    showProgress(message) {
        document.getElementById('progress-message').textContent = message;
        const modal = new bootstrap.Modal(document.getElementById('progressModal'));
        modal.show();
    }

    hideProgress() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('progressModal'));
        if (modal) {
            modal.hide();
        }
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'danger');
    }

    showInfo(message) {
        this.showNotification(message, 'info');
    }

    showWarning(message) {
        this.showNotification(message, 'warning');
    }

    showNotification(message, type) {
        // Create toast notification
        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }

    // Use Cases Methods
    async loadAllUseCases() {
        try {
            const response = await fetch('/physics-modeling/api/use-cases');
            if (response.ok) {
                this.useCases = await response.json();
                this.loadUseCasesForCategory('thermal'); // Load initial category
                this.showSuccess('Use cases loaded successfully');
            }
        } catch (error) {
            console.error('Failed to load use cases:', error);
            this.showError('Failed to load use cases');
        }
    }

    async loadUseCasesForCategory(category) {
        const container = document.getElementById(`${category}-use-cases`);
        if (!container) return;

        container.innerHTML = '<div class="col-12 text-center"><i class="fas fa-spinner fa-spin fa-2x text-muted"></i></div>';

        try {
            const response = await fetch(`/physics-modeling/api/use-cases/${category}`);
            if (response.ok) {
                const useCases = await response.json();
                this.displayUseCases(container, useCases, category);
            }
        } catch (error) {
            console.error(`Failed to load ${category} use cases:`, error);
            container.innerHTML = '<div class="col-12 text-center text-danger">Failed to load use cases</div>';
        }
    }

    displayUseCases(container, useCases, category) {
        container.innerHTML = '';

        if (!useCases || useCases.length === 0) {
            container.innerHTML = '<div class="col-12 text-center text-muted">No use cases available for this category</div>';
            return;
        }

        useCases.forEach(useCase => {
            const useCaseCard = this.createUseCaseCard(useCase, category);
            container.appendChild(useCaseCard);
        });
    }

    createUseCaseCard(useCase, category) {
        const col = document.createElement('div');
        col.className = 'col-lg-6 col-md-6 col-12 mb-3';

        const card = document.createElement('div');
        card.className = 'card h-100 border-0 shadow-sm use-case-card';
        card.setAttribute('data-use-case', useCase.name);

        const categoryIcons = {
            thermal: 'fas fa-fire',
            structural: 'fas fa-cube',
            fluid: 'fas fa-water',
            multi: 'fas fa-link',
            industrial: 'fas fa-industry'
        };

        const categoryColors = {
            thermal: 'bg-danger',
            structural: 'bg-primary',
            fluid: 'bg-info',
            multi: 'bg-success',
            industrial: 'bg-warning'
        };

        const icon = categoryIcons[category] || 'fas fa-atom';
        const color = categoryColors[category] || 'bg-secondary';

        card.innerHTML = `
            <div class="card-header ${color} text-white">
                <div class="d-flex justify-content-between align-items-center">
                    <h6 class="mb-0">
                        <i class="${icon} me-2"></i>${useCase.name}
                    </h6>
                    <span class="badge bg-light text-dark">${useCase.industry || 'General'}</span>
                </div>
            </div>
            <div class="card-body">
                <p class="card-text text-muted small">${useCase.description || 'No description available'}</p>
                
                <div class="mb-2">
                    <small class="text-muted">
                        <i class="fas fa-bullseye me-1"></i>
                        <strong>Challenge:</strong> ${useCase.challenge || 'Not specified'}
                    </small>
                </div>

                <div class="mb-2">
                    <small class="text-muted">
                        <i class="fas fa-atom me-1"></i>
                        <strong>Physics Focus:</strong> ${useCase.physics_focus || 'Multi-physics'}
                    </small>
                </div>

                ${useCase.famous_examples ? `
                <div class="mb-2">
                    <small class="text-muted">
                        <i class="fas fa-star me-1"></i>
                        <strong>Famous Examples:</strong>
                    </small>
                    <div class="mt-1">
                        ${useCase.famous_examples.slice(0, 3).map(example => 
                            `<span class="badge bg-outline-secondary me-1">${example}</span>`
                        ).join('')}
                        ${useCase.famous_examples.length > 3 ? 
                            `<span class="badge bg-outline-secondary">+${useCase.famous_examples.length - 3} more</span>` : 
                            ''
                        }
                    </div>
                </div>
                ` : ''}

                ${useCase.expected_results ? `
                <div class="mb-2">
                    <small class="text-muted">
                        <i class="fas fa-chart-line me-1"></i>
                        <strong>Expected Results:</strong>
                    </small>
                    <div class="mt-1">
                        ${Object.entries(useCase.expected_results).slice(0, 2).map(([key, value]) => 
                            `<span class="badge bg-outline-success me-1">${key}: ${value}</span>`
                        ).join('')}
                        ${Object.keys(useCase.expected_results).length > 2 ? 
                            `<span class="badge bg-outline-success">+${Object.keys(useCase.expected_results).length - 2} more</span>` : 
                            ''
                        }
                    </div>
                </div>
                ` : ''}

                ${useCase.german_context ? `
                <div class="mb-2">
                    <small class="text-muted">
                        <i class="fas fa-flag me-1"></i>
                        <strong>German Context:</strong>
                    </small>
                    <div class="mt-1">
                        <span class="badge bg-outline-warning me-1">${useCase.german_context.national_strategy}</span>
                        <span class="badge bg-outline-info">${useCase.german_context.target_2030}</span>
                    </div>
                </div>
                ` : ''}
            </div>
            <div class="card-footer bg-light">
                <div class="d-flex gap-2">
                    <button class="btn btn-sm btn-primary flex-fill" onclick="physicsUI.loadUseCase('${useCase.name}')">
                        <i class="fas fa-download me-1"></i>Load Template
                    </button>
                    <button class="btn btn-sm btn-outline-info" onclick="physicsUI.viewUseCaseDetails('${useCase.name}')">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-success" onclick="physicsUI.createModelFromUseCase('${useCase.name}')">
                        <i class="fas fa-plus"></i>
                    </button>
                </div>
            </div>
        `;

        col.appendChild(card);
        return col;
    }

    async showFamousExamples() {
        try {
            const response = await fetch('/physics-modeling/api/use-cases/famous-examples');
            if (response.ok) {
                const examples = await response.json();
                this.displayFamousExamples(examples);
            }
        } catch (error) {
            console.error('Failed to load famous examples:', error);
            this.showError('Failed to load famous examples');
        }
    }

    displayFamousExamples(examples) {
        const modal = new bootstrap.Modal(document.getElementById('resultsModal'));
        const content = document.getElementById('results-content');
        
        let html = '<h4><i class="fas fa-star text-warning me-2"></i>Famous Examples by Industry</h4>';
        
        Object.entries(examples).forEach(([industry, industryExamples]) => {
            html += `
                <div class="card mb-3">
                    <div class="card-header bg-light">
                        <h6 class="mb-0"><i class="fas fa-industry me-2"></i>${industry}</h6>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            ${industryExamples.map(example => `
                                <div class="col-md-6 col-12 mb-2">
                                    <span class="badge bg-primary me-1">${example}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;
        });
        
        content.innerHTML = html;
        modal.show();
    }

    async showOptimizationTargets() {
        try {
            const response = await fetch('/physics-modeling/api/use-cases/optimization-targets');
            if (response.ok) {
                const targets = await response.json();
                this.displayOptimizationTargets(targets);
            }
        } catch (error) {
            console.error('Failed to load optimization targets:', error);
            this.showError('Failed to load optimization targets');
        }
    }

    displayOptimizationTargets(targets) {
        const modal = new bootstrap.Modal(document.getElementById('resultsModal'));
        const content = document.getElementById('results-content');
        
        let html = '<h4><i class="fas fa-bullseye text-info me-2"></i>Optimization Targets by Use Case</h4>';
        
        Object.entries(targets).forEach(([useCaseName, useCaseTargets]) => {
            html += `
                <div class="card mb-3">
                    <div class="card-header bg-light">
                        <h6 class="mb-0"><i class="fas fa-target me-2"></i>${useCaseName}</h6>
                    </div>
                    <div class="card-body">
                        <ul class="list-unstyled mb-0">
                            ${useCaseTargets.map(target => `
                                <li class="mb-1">
                                    <i class="fas fa-check text-success me-2"></i>${target}
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                </div>
            `;
        });
        
        content.innerHTML = html;
        modal.show();
    }

    async showHydrogenEconomy() {
        try {
            const response = await fetch('/physics-modeling/api/use-cases/hydrogen-economy');
            if (response.ok) {
                const hydrogenUseCase = await response.json();
                this.displayHydrogenEconomy(hydrogenUseCase);
            }
        } catch (error) {
            console.error('Failed to load hydrogen economy use case:', error);
            this.showError('Failed to load hydrogen economy use case');
        }
    }

    displayHydrogenEconomy(hydrogenUseCase) {
        const modal = new bootstrap.Modal(document.getElementById('resultsModal'));
        const content = document.getElementById('results-content');
        
        const html = `
            <div class="text-center mb-4">
                <h3><i class="fas fa-leaf text-success me-2"></i>Hydrogen Economy Infrastructure Analysis</h3>
                <p class="text-muted">Critical for Germany's energy transition</p>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <div class="card mb-3">
                        <div class="card-header bg-success text-white">
                            <h6 class="mb-0"><i class="fas fa-flag me-2"></i>German National Strategy</h6>
                        </div>
                        <div class="card-body">
                            <ul class="list-unstyled mb-0">
                                <li><strong>Strategy:</strong> ${hydrogenUseCase.german_context.national_strategy}</li>
                                <li><strong>2030 Target:</strong> ${hydrogenUseCase.german_context.target_2030}</li>
                                <li><strong>2040 Target:</strong> ${hydrogenUseCase.german_context.target_2040}</li>
                                <li><strong>Key Regions:</strong> ${hydrogenUseCase.german_context.key_regions.join(', ')}</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="card mb-3">
                        <div class="card-header bg-info text-white">
                            <h6 class="mb-0"><i class="fas fa-industry me-2"></i>Industrial Partners</h6>
                        </div>
                        <div class="card-body">
                            <div class="d-flex flex-wrap gap-1">
                                ${hydrogenUseCase.german_context.industrial_partners.map(partner => 
                                    `<span class="badge bg-light text-dark">${partner}</span>`
                                ).join('')}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card mb-3">
                <div class="card-header bg-warning text-dark">
                    <h6 class="mb-0"><i class="fas fa-bullseye me-2"></i>Optimization Targets</h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        ${hydrogenUseCase.optimization_targets.map(target => `
                            <div class="col-md-6 mb-2">
                                <i class="fas fa-check text-success me-2"></i>${target}
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h6 class="mb-0"><i class="fas fa-chart-line me-2"></i>Expected Results</h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        ${Object.entries(hydrogenUseCase.expected_results).map(([metric, value]) => `
                            <div class="col-md-6 mb-2">
                                <strong>${metric}:</strong> <span class="badge bg-outline-primary">${value}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
        
        content.innerHTML = html;
        modal.show();
    }

    loadUseCase(useCaseName) {
        // Load use case template into the form
        this.showInfo(`Loading template for: ${useCaseName}`);
        // TODO: Implement template loading from use case
    }

    viewUseCaseDetails(useCaseName) {
        // Show detailed view of use case
        this.showInfo(`Viewing details for: ${useCaseName}`);
        // TODO: Implement detailed view
    }

    async createModelFromUseCase(useCaseName) {
        try {
            const response = await fetch('/physics-modeling/api/models/create-from-use-case', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ use_case_name: useCaseName })
            });

            if (response.ok) {
                const result = await response.json();
                this.showSuccess(`Model created from use case: ${useCaseName}`);
                await this.loadAvailableModels();
            } else {
                const error = await response.json();
                this.showError(`Failed to create model: ${error.detail}`);
            }
        } catch (error) {
            console.error('Error creating model from use case:', error);
            this.showError('Failed to create model from use case');
        }
    }

    async refreshTwins() {
        const refreshBtn = document.getElementById('refresh-twins-btn');
        const originalIcon = refreshBtn.innerHTML;
        
        try {
            // Show loading state
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            refreshBtn.disabled = true;
            
            // Reload twins
            await this.loadAvailableTwins();
            
            // Show success message
            this.showSuccess(`Refreshed twin list - ${this.availableTwins.length} twins available`);
            
        } catch (error) {
            console.error('Error refreshing twins:', error);
            this.showError('Failed to refresh twin list');
        } finally {
            // Restore button state
            refreshBtn.innerHTML = originalIcon;
            refreshBtn.disabled = false;
        }
    }
}

// Initialize the physics modeling UI when the page loads
let physicsUI;
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Initializing Physics Modeling UI...');
    physicsUI = new PhysicsModelingUI();
    
    // Export for global access
    window.physicsUI = physicsUI;
    console.log('✅ Physics Modeling UI initialized and exported to window.physicsUI');
});

// Fallback initialization for immediate access
if (document.readyState === 'loading') {
    // Document is still loading, wait for DOMContentLoaded
    document.addEventListener('DOMContentLoaded', () => {
        if (!window.physicsUI) {
            console.log('🔄 Fallback initialization of Physics Modeling UI...');
            window.physicsUI = new PhysicsModelingUI();
        }
    });
} else {
    // Document is already loaded, initialize immediately
    console.log('⚡ Document already loaded, initializing Physics Modeling UI immediately...');
    window.physicsUI = new PhysicsModelingUI();
}