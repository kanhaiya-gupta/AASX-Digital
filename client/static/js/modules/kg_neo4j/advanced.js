/**
 * Knowledge Graph Advanced Tab JavaScript Module - World Class Edition
 * ES6 Class-based implementation with central authentication integration
 * Features sophisticated workflow management, analytics, ML integration, and enterprise-grade operations
 */

import { AuthManager } from '../../auth/auth_manager.js';
import { Logger } from '../../utils/logger.js';
import { ApiClient } from '../../api/api_client.js';

class AdvancedOperationsManager {
    constructor() {
        this.authManager = new AuthManager();
        this.logger = new Logger('AdvancedOperationsManager');
        this.apiClient = new ApiClient();
        
        // State management
        this.workflowState = {
            currentWorkflow: null,
            workflows: [],
            isEditing: false,
            selectedNodes: [],
            selectedConnections: []
        };
        
        this.analyticsState = {
            metrics: {
                nodeCount: 0,
                relationshipCount: 0,
                graphDensity: 0,
                averageDegree: 0,
                clusteringCoefficient: 0,
                diameter: 0,
                centrality: {}
            },
            charts: {},
            lastUpdated: null
        };
        
        this.mlState = {
            models: [],
            activeModel: null,
            trainingStatus: {},
            predictions: [],
            accuracy: 0
        };
        
        this.optimizationState = {
            recommendations: [],
            performanceMetrics: {},
            lastOptimization: null,
            optimizationHistory: []
        };
        
        this.systemHealth = {
            status: 'healthy',
            metrics: {},
            alerts: [],
            lastCheck: null
        };
        
        // DOM elements cache
        this.elements = {};
        
        // Initialize the manager
        this.init();
    }
    
    /**
     * Initialize the Advanced Operations Manager
     */
    async init() {
        try {
            // Check authentication
            if (!await this.authManager.isAuthenticated()) {
                this.logger.warn('User not authenticated, redirecting to login');
                window.location.href = '/login';
                return;
            }
            
            // Cache DOM elements
            this.cacheElements();
            
            // Bind event listeners
            this.bindEventListeners();
            
            // Initialize real-time updates
            this.initializeRealTimeUpdates();
            
            // Load initial data
            await this.loadInitialData();
            
            this.logger.info('Advanced Operations Manager initialized successfully');
            
        } catch (error) {
            this.logger.error('Failed to initialize Advanced Operations Manager:', error);
            this.showError('Failed to initialize Advanced Operations Manager');
        }
    }
    
    /**
     * Cache DOM elements for performance
     */
    cacheElements() {
        this.elements = {
            // Workflow elements
            workflowCanvas: document.getElementById('workflow-canvas'),
            workflowToolbar: document.querySelector('.workflow-toolbar'),
            workflowProperties: document.querySelector('.workflow-properties'),
            
            // Analytics elements
            analyticsMetrics: document.querySelector('.analytics-metrics'),
            analyticsCharts: document.querySelector('.analytics-charts'),
            
            // ML elements
            mlModels: document.querySelector('.ml-models'),
            mlConfiguration: document.querySelector('.ml-configuration'),
            
            // Optimization elements
            optimizationTools: document.querySelector('.optimization-tools'),
            optimizationResults: document.getElementById('optimization-results-container'),
            
            // System health elements
            healthMetrics: document.querySelector('.health-metrics'),
            healthStatus: document.querySelector('.health-status'),
            
            // Form elements
            transformationInput: document.querySelector('.transformation-input'),
            transformationOutput: document.querySelector('.transformation-output'),
            
            // Buttons
            createWorkflowBtn: document.querySelector('[onclick="createWorkflow()"]'),
            refreshBtn: document.querySelector('[onclick="refreshAdvancedOps()"]'),
            runOptimizationBtn: document.querySelector('[onclick="runOptimization()"]'),
            trainModelBtn: document.querySelector('[onclick="trainModel()"]'),
            exportWorkflowBtn: document.querySelector('[onclick="exportWorkflow()"]'),
            importWorkflowBtn: document.querySelector('[onclick="importWorkflow()"]')
        };
    }
    
    /**
     * Bind event listeners to DOM elements
     */
    bindEventListeners() {
        // Workflow management
        if (this.elements.createWorkflowBtn) {
            this.elements.createWorkflowBtn.addEventListener('click', () => this.createWorkflow());
        }
        
        if (this.elements.refreshBtn) {
            this.elements.refreshBtn.addEventListener('click', () => this.refreshAdvancedOps());
        }
        
        // Optimization
        if (this.elements.runOptimizationBtn) {
            this.elements.runOptimizationBtn.addEventListener('click', () => this.runOptimization());
        }
        
        // ML operations
        if (this.elements.trainModelBtn) {
            this.elements.trainModelBtn.addEventListener('click', () => this.trainModel());
        }
        
        // Import/Export
        if (this.elements.exportWorkflowBtn) {
            this.elements.exportWorkflowBtn.addEventListener('click', () => this.exportWorkflow());
        }
        
        if (this.elements.importWorkflowBtn) {
            this.elements.importWorkflowBtn.addEventListener('click', () => this.importWorkflow());
        }
        
        // Form submissions
        const transformationForm = document.querySelector('.transformation-form');
        if (transformationForm) {
            transformationForm.addEventListener('submit', (e) => this.handleTransformationSubmit(e));
        }
        
        // Workflow canvas interactions
        if (this.elements.workflowCanvas) {
            this.initializeWorkflowCanvas();
        }
    }
    
    /**
     * Initialize real-time updates
     */
    initializeRealTimeUpdates() {
        // Update analytics every 10 seconds
        setInterval(() => this.updateAnalytics(), 10000);
        
        // Update system health every 15 seconds
        setInterval(() => this.updateSystemHealth(), 15000);
        
        // Update ML status every 20 seconds
        setInterval(() => this.updateMLStatus(), 20000);
        
        // Update optimization status every 30 seconds
        setInterval(() => this.updateOptimizationStatus(), 30000);
    }
    
    /**
     * Load initial data
     */
    async loadInitialData() {
        try {
            await Promise.all([
                this.loadWorkflows(),
                this.loadAnalytics(),
                this.loadMLModels(),
                this.loadOptimizationHistory(),
                this.loadSystemHealth()
            ]);
        } catch (error) {
            this.logger.error('Failed to load initial data:', error);
        }
    }
    
    /**
     * Create new workflow
     */
    async createWorkflow() {
        try {
            this.setButtonLoading(this.elements.createWorkflowBtn, true);
            
            const workflowData = {
                name: `Workflow_${Date.now()}`,
                description: 'New advanced workflow',
                type: 'graph_transformation',
                status: 'draft'
            };
            
            const response = await this.apiClient.post('/api/workflows/create', workflowData, {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.workflowState.currentWorkflow = response.data;
                this.showSuccess('New workflow created successfully');
                await this.loadWorkflows();
                this.initializeWorkflowCanvas();
            } else {
                this.showError(response.message || 'Failed to create workflow');
            }
            
        } catch (error) {
            this.logger.error('Failed to create workflow:', error);
            this.showError('Failed to create workflow');
        } finally {
            this.setButtonLoading(this.elements.createWorkflowBtn, false);
        }
    }
    
    /**
     * Refresh advanced operations
     */
    async refreshAdvancedOps() {
        try {
            this.setButtonLoading(this.elements.refreshBtn, true);
            
            await Promise.all([
                this.loadWorkflows(),
                this.loadAnalytics(),
                this.loadMLModels(),
                this.loadOptimizationHistory(),
                this.loadSystemHealth()
            ]);
            
            this.showSuccess('Advanced operations refreshed successfully');
            
        } catch (error) {
            this.logger.error('Failed to refresh advanced operations:', error);
            this.showError('Failed to refresh operations');
        } finally {
            this.setButtonLoading(this.elements.refreshBtn, false);
        }
    }
    
    /**
     * Load workflows
     */
    async loadWorkflows() {
        try {
            const response = await this.apiClient.get('/api/workflows/list', {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.workflowState.workflows = response.data.workflows || [];
                this.updateWorkflowList();
            }
            
        } catch (error) {
            this.logger.error('Failed to load workflows:', error);
        }
    }
    
    /**
     * Update workflow list display
     */
    updateWorkflowList() {
        const workflowList = document.getElementById('workflow-list');
        if (!workflowList) return;
        
        if (this.workflowState.workflows.length === 0) {
            workflowList.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-project-diagram fa-3x text-muted mb-3"></i>
                    <p class="text-muted">No workflows created yet. Create your first workflow to get started.</p>
                </div>
            `;
            return;
        }
        
        let workflowHTML = '';
        this.workflowState.workflows.forEach(workflow => {
            workflowHTML += `
                <div class="workflow-item p-3 border rounded mb-2" data-workflow-id="${workflow.id}">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-1">${workflow.name}</h6>
                            <small class="text-muted">${workflow.description}</small>
                        </div>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary btn-sm" onclick="advancedManager.editWorkflow('${workflow.id}')">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-outline-success btn-sm" onclick="advancedManager.runWorkflow('${workflow.id}')">
                                <i class="fas fa-play"></i>
                            </button>
                            <button class="btn btn-outline-danger btn-sm" onclick="advancedManager.deleteWorkflow('${workflow.id}')">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });
        
        workflowList.innerHTML = workflowHTML;
    }
    
    /**
     * Load analytics data
     */
    async loadAnalytics() {
        try {
            const response = await this.apiClient.get('/api/analytics/graph-metrics', {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.analyticsState.metrics = response.data.metrics || {};
                this.analyticsState.lastUpdated = new Date();
                this.updateAnalyticsDisplay();
            }
            
        } catch (error) {
            this.logger.error('Failed to load analytics:', error);
        }
    }
    
    /**
     * Update analytics display
     */
    updateAnalyticsDisplay() {
        const metrics = this.analyticsState.metrics;
        
        // Update metric cards
        if (this.elements.analyticsMetrics) {
            const nodeCountEl = this.elements.analyticsMetrics.querySelector('#node-count');
            const relationshipCountEl = this.elements.analyticsMetrics.querySelector('#relationship-count');
            const graphDensityEl = this.elements.analyticsMetrics.querySelector('#graph-density');
            const avgDegreeEl = this.elements.analyticsMetrics.querySelector('#avg-degree');
            
            if (nodeCountEl) nodeCountEl.textContent = metrics.nodeCount || 0;
            if (relationshipCountEl) relationshipCountEl.textContent = metrics.relationshipCount || 0;
            if (graphDensityEl) graphDensityEl.textContent = (metrics.graphDensity || 0).toFixed(4);
            if (avgDegreeEl) avgDegreeEl.textContent = (metrics.averageDegree || 0).toFixed(2);
        }
        
        // Update charts if available
        this.updateAnalyticsCharts();
    }
    
    /**
     * Update analytics charts
     */
    updateAnalyticsCharts() {
        if (!this.elements.analyticsCharts) return;
        
        // Placeholder for chart updates
        // In a real implementation, this would integrate with Chart.js or similar
        this.elements.analyticsCharts.innerHTML = `
            <div class="text-center">
                <i class="fas fa-chart-line fa-3x text-muted mb-3"></i>
                <p class="text-muted">Advanced analytics charts will be displayed here</p>
                <small class="text-muted">Last updated: ${this.analyticsState.lastUpdated?.toLocaleTimeString() || 'Never'}</small>
            </div>
        `;
    }
    
    /**
     * Load ML models
     */
    async loadMLModels() {
        try {
            const response = await this.apiClient.get('/api/ml/models', {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.mlState.models = response.data.models || [];
                this.updateMLModelsDisplay();
            }
            
        } catch (error) {
            this.logger.error('Failed to load ML models:', error);
        }
    }
    
    /**
     * Update ML models display
     */
    updateMLModelsDisplay() {
        if (!this.elements.mlModels) return;
        
        const modelsContainer = this.elements.mlModels.querySelector('.ml-models-list');
        if (!modelsContainer) return;
        
        if (this.mlState.models.length === 0) {
            modelsContainer.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-brain fa-3x text-muted mb-3"></i>
                    <p class="text-muted">No ML models available. Train a new model to get started.</p>
                </div>
            `;
            return;
        }
        
        let modelsHTML = '';
        this.mlState.models.forEach(model => {
            modelsHTML += `
                <div class="form-check">
                    <input class="form-check-input" type="radio" name="ml-model" id="model-${model.id}" value="${model.id}">
                    <label class="form-check-label" for="model-${model.id}">
                        <strong>${model.name}</strong>
                        <br>
                        <small class="text-muted">
                            Type: ${model.type} | Accuracy: ${(model.accuracy * 100).toFixed(1)}% | 
                            Last trained: ${new Date(model.lastTrained).toLocaleDateString()}
                        </small>
                    </label>
                </div>
            `;
        });
        
        modelsContainer.innerHTML = modelsHTML;
    }
    
    /**
     * Train ML model
     */
    async trainModel() {
        try {
            this.setButtonLoading(this.elements.trainModelBtn, true);
            
            const selectedModel = document.querySelector('input[name="ml-model"]:checked');
            if (!selectedModel) {
                this.showError('Please select a model to train');
                return;
            }
            
            const modelId = selectedModel.value;
            const response = await this.apiClient.post('/api/ml/train', {
                modelId: modelId,
                parameters: this.getMLTrainingParameters()
            }, {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.showSuccess('Model training started successfully');
                this.mlState.trainingStatus[modelId] = 'training';
                this.updateMLTrainingStatus();
            } else {
                this.showError(response.message || 'Failed to start model training');
            }
            
        } catch (error) {
            this.logger.error('Failed to train model:', error);
            this.showError('Failed to train model');
        } finally {
            this.setButtonLoading(this.elements.trainModelBtn, false);
        }
    }
    
    /**
     * Get ML training parameters
     */
    getMLTrainingParameters() {
        const params = {};
        
        // Get parameters from form inputs
        const learningRate = document.getElementById('learning-rate');
        const epochs = document.getElementById('epochs');
        const batchSize = document.getElementById('batch-size');
        
        if (learningRate) params.learningRate = parseFloat(learningRate.value);
        if (epochs) params.epochs = parseInt(epochs.value);
        if (batchSize) params.batchSize = parseInt(batchSize.value);
        
        return params;
    }
    
    /**
     * Update ML training status
     */
    updateMLTrainingStatus() {
        Object.keys(this.mlState.trainingStatus).forEach(modelId => {
            const status = this.mlState.trainingStatus[modelId];
            if (status === 'training') {
                // Update UI to show training progress
                const modelElement = document.getElementById(`model-${modelId}`);
                if (modelElement) {
                    const label = modelElement.nextElementSibling;
                    if (label) {
                        label.innerHTML += ' <span class="badge bg-warning">Training...</span>';
                    }
                }
            }
        });
    }
    
    /**
     * Run optimization
     */
    async runOptimization() {
        try {
            this.setButtonLoading(this.elements.runOptimizationBtn, true);
            
            const optimizationType = document.getElementById('optimization-type')?.value || 'general';
            const optimizationParams = this.getOptimizationParameters();
            
            const response = await this.apiClient.post('/api/optimization/run', {
                type: optimizationType,
                parameters: optimizationParams
            }, {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.showSuccess('Optimization started successfully');
                this.optimizationState.lastOptimization = new Date();
                await this.loadOptimizationResults();
            } else {
                this.showError(response.message || 'Failed to start optimization');
            }
            
        } catch (error) {
            this.logger.error('Failed to run optimization:', error);
            this.showError('Failed to run optimization');
        } finally {
            this.setButtonLoading(this.elements.runOptimizationBtn, false);
        }
    }
    
    /**
     * Get optimization parameters
     */
    getOptimizationParameters() {
        const params = {};
        
        // Get parameters from form inputs
        const maxIterations = document.getElementById('max-iterations');
        const tolerance = document.getElementById('tolerance');
        const algorithm = document.getElementById('algorithm');
        
        if (maxIterations) params.maxIterations = parseInt(maxIterations.value);
        if (tolerance) params.tolerance = parseFloat(tolerance.value);
        if (algorithm) params.algorithm = algorithm.value;
        
        return params;
    }
    
    /**
     * Load optimization results
     */
    async loadOptimizationResults() {
        try {
            const response = await this.apiClient.get('/api/optimization/results', {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.optimizationState.recommendations = response.data.recommendations || [];
                this.optimizationState.performanceMetrics = response.data.metrics || {};
                this.updateOptimizationDisplay();
            }
            
        } catch (error) {
            this.logger.error('Failed to load optimization results:', error);
        }
    }
    
    /**
     * Update optimization display
     */
    updateOptimizationDisplay() {
        if (!this.elements.optimizationResults) return;
        
        const recommendations = this.optimizationState.recommendations;
        const metrics = this.optimizationState.performanceMetrics;
        
        if (recommendations.length === 0) {
            this.elements.optimizationResults.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-tools fa-3x text-muted mb-3"></i>
                    <p class="text-muted">No optimization results available. Run optimization to see recommendations.</p>
                </div>
            `;
            return;
        }
        
        let resultsHTML = `
            <div class="optimization-summary mb-4">
                <h6>Performance Metrics</h6>
                <div class="row">
                    <div class="col-md-3">
                        <div class="text-center">
                            <h4 class="text-primary">${(metrics.performanceGain || 0).toFixed(2)}%</h4>
                            <small class="text-muted">Performance Gain</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <h4 class="text-success">${(metrics.efficiencyImprovement || 0).toFixed(2)}%</h4>
                            <small class="text-muted">Efficiency Improvement</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <h4 class="text-info">${metrics.optimizationTime || 0}s</h4>
                            <small class="text-muted">Optimization Time</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <h4 class="text-warning">${metrics.resourceSavings || 0}%</h4>
                            <small class="text-muted">Resource Savings</small>
                        </div>
                    </div>
                </div>
            </div>
            <div class="optimization-recommendations">
                <h6>Recommendations</h6>
                <div class="list-group">
        `;
        
        recommendations.forEach((rec, index) => {
            resultsHTML += `
                <div class="list-group-item">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="mb-1">${rec.title}</h6>
                            <p class="mb-1">${rec.description}</p>
                            <small class="text-muted">Priority: ${rec.priority}</small>
                        </div>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary btn-sm" onclick="advancedManager.applyRecommendation(${index})">
                                Apply
                            </button>
                            <button class="btn btn-outline-info btn-sm" onclick="advancedManager.viewRecommendationDetails(${index})">
                                Details
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });
        
        resultsHTML += '</div></div>';
        this.elements.optimizationResults.innerHTML = resultsHTML;
    }
    
    /**
     * Load system health
     */
    async loadSystemHealth() {
        try {
            const response = await this.apiClient.get('/api/system/health', {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.systemHealth = { ...this.systemHealth, ...response.data };
                this.updateSystemHealthDisplay();
            }
            
        } catch (error) {
            this.logger.error('Failed to load system health:', error);
        }
    }
    
    /**
     * Update system health display
     */
    updateSystemHealthDisplay() {
        if (!this.elements.healthStatus) return;
        
        const healthContainer = this.elements.healthStatus.querySelector('.health-status-list');
        if (!healthContainer) return;
        
        const metrics = this.systemHealth.metrics;
        let healthHTML = '';
        
        Object.entries(metrics).forEach(([key, value]) => {
            const status = this.getHealthStatus(value);
            healthHTML += `
                <div class="d-flex justify-content-between align-items-center">
                    <span>${this.formatHealthMetricName(key)}</span>
                    <span class="badge bg-${status.color}">${status.text}</span>
                </div>
            `;
        });
        
        healthContainer.innerHTML = healthHTML;
    }
    
    /**
     * Get health status for metric
     */
    getHealthStatus(value) {
        if (typeof value === 'number') {
            if (value >= 90) return { color: 'success', text: 'Excellent' };
            if (value >= 75) return { color: 'info', text: 'Good' };
            if (value >= 60) return { color: 'warning', text: 'Fair' };
            return { color: 'danger', text: 'Poor' };
        }
        
        if (typeof value === 'string') {
            if (value === 'healthy') return { color: 'success', text: 'Healthy' };
            if (value === 'warning') return { color: 'warning', text: 'Warning' };
            if (value === 'error') return { color: 'danger', text: 'Error' };
            return { color: 'secondary', text: 'Unknown' };
        }
        
        return { color: 'secondary', text: 'N/A' };
    }
    
    /**
     * Format health metric name
     */
    formatHealthMetricName(key) {
        return key
            .replace(/([A-Z])/g, ' $1')
            .replace(/^./, str => str.toUpperCase())
            .trim();
    }
    
    /**
     * Initialize workflow canvas
     */
    initializeWorkflowCanvas() {
        if (!this.elements.workflowCanvas) return;
        
        // Placeholder for workflow canvas initialization
        // In a real implementation, this would integrate with a workflow engine like jsPlumb or similar
        this.elements.workflowCanvas.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-project-diagram fa-4x text-muted mb-4"></i>
                <h5 class="text-muted">Workflow Canvas</h5>
                <p class="text-muted">Drag and drop workflow components here to build your graph transformation workflow</p>
                <button class="btn btn-primary" onclick="advancedManager.addWorkflowNode()">
                    <i class="fas fa-plus me-2"></i>Add Node
                </button>
            </div>
        `;
    }
    
    /**
     * Handle transformation form submission
     */
    async handleTransformationSubmit(event) {
        event.preventDefault();
        
        try {
            const formData = new FormData(event.target);
            const transformationData = {
                inputFormat: formData.get('input-format'),
                outputFormat: formData.get('output-format'),
                transformationRules: formData.get('transformation-rules'),
                options: {
                    preserveProperties: formData.get('preserve-properties') === 'on',
                    createIndexes: formData.get('create-indexes') === 'on',
                    validateOutput: formData.get('validate-output') === 'on'
                }
            };
            
            const response = await this.apiClient.post('/api/transformations/execute', transformationData, {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.showSuccess('Transformation executed successfully');
                this.displayTransformationResults(response.data);
            } else {
                this.showError(response.message || 'Transformation failed');
            }
            
        } catch (error) {
            this.logger.error('Failed to execute transformation:', error);
            this.showError('Failed to execute transformation');
        }
    }
    
    /**
     * Display transformation results
     */
    displayTransformationResults(results) {
        const resultsContainer = document.getElementById('transformation-results');
        if (!resultsContainer) return;
        
        resultsContainer.innerHTML = `
            <div class="alert alert-success">
                <h6><i class="fas fa-check-circle me-2"></i>Transformation Completed</h6>
                <p class="mb-2">Successfully transformed ${results.inputCount || 0} input items to ${results.outputCount || 0} output items.</p>
                <small class="text-muted">Processing time: ${results.processingTime || 0}ms</small>
            </div>
        `;
    }
    
    /**
     * Export workflow
     */
    async exportWorkflow() {
        try {
            if (!this.workflowState.currentWorkflow) {
                this.showError('No workflow selected for export');
                return;
            }
            
            const response = await this.apiClient.get('/api/workflows/export', {
                params: { workflowId: this.workflowState.currentWorkflow.id },
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                // Create download link
                const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `workflow_${this.workflowState.currentWorkflow.name}_${Date.now()}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                this.showSuccess('Workflow exported successfully');
            } else {
                this.showError(response.message || 'Failed to export workflow');
            }
            
        } catch (error) {
            this.logger.error('Failed to export workflow:', error);
            this.showError('Failed to export workflow');
        }
    }
    
    /**
     * Import workflow
     */
    async importWorkflow() {
        try {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.json';
            input.onchange = async (event) => {
                const file = event.target.files[0];
                if (!file) return;
                
                try {
                    const content = await file.text();
                    const workflowData = JSON.parse(content);
                    
                    const response = await this.apiClient.post('/api/workflows/import', workflowData, {
                        headers: await this.authManager.getAuthHeaders()
                    });
                    
                    if (response.success) {
                        this.showSuccess('Workflow imported successfully');
                        await this.loadWorkflows();
                    } else {
                        this.showError(response.message || 'Failed to import workflow');
                    }
                    
                } catch (error) {
                    this.logger.error('Failed to import workflow:', error);
                    this.showError('Failed to import workflow');
                }
            };
            
            input.click();
            
        } catch (error) {
            this.logger.error('Failed to import workflow:', error);
            this.showError('Failed to import workflow');
        }
    }
    
    /**
     * Set button loading state
     */
    setButtonLoading(button, isLoading) {
        if (!button) return;
        
        if (isLoading) {
            button.classList.add('loading');
            button.disabled = true;
        } else {
            button.classList.remove('loading');
            button.disabled = false;
        }
    }
    
    /**
     * Show success message
     */
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    /**
     * Show error message
     */
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
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
    
    /**
     * Cleanup resources
     */
    destroy() {
        // Clear intervals
        if (this.analyticsInterval) {
            clearInterval(this.analyticsInterval);
        }
        if (this.healthInterval) {
            clearInterval(this.healthInterval);
        }
        if (this.mlInterval) {
            clearInterval(this.mlInterval);
        }
        if (this.optimizationInterval) {
            clearInterval(this.optimizationInterval);
        }
        
        this.logger.info('Advanced Operations Manager destroyed');
    }
}

// Export the class
export { AdvancedOperationsManager };

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Check if we're on the Advanced tab
    if (document.querySelector('.kg-advanced-tab')) {
        window.advancedManager = new AdvancedOperationsManager();
    }
});

// Global functions for backward compatibility (if needed)
window.createWorkflow = () => window.advancedManager?.createWorkflow();
window.refreshAdvancedOps = () => window.advancedManager?.refreshAdvancedOps();
window.runOptimization = () => window.advancedManager?.runOptimization();
window.trainModel = () => window.advancedManager?.trainModel();
window.exportWorkflow = () => window.advancedManager?.exportWorkflow();
window.importWorkflow = () => window.advancedManager?.importWorkflow();
window.addWorkflowNode = () => window.advancedManager?.addWorkflowNode();
window.applyRecommendation = (index) => window.advancedManager?.applyRecommendation(index);
window.viewRecommendationDetails = (index) => window.advancedManager?.viewRecommendationDetails(index);
