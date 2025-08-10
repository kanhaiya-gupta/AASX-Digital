/**
 * Shared API Communication Layer
 * Handles all API calls to the physics modeling backend services
 */

import { getAuthToken, getAuthHeaders, isAuthenticated, getCurrentUser, initModuleAuth } from '../../../shared/auth-helper.js';

export default class PhysicsModelingAPI {
    constructor() {
        this.baseURL = '/api/physics-modeling';
        this.endpoints = {
            models: `${this.baseURL}/models`,
            simulations: `${this.baseURL}/simulations`,
            validation: `${this.baseURL}/validation`,
            useCases: `${this.baseURL}/use-cases`,
            system: `${this.baseURL}/system`,
            twins: `${this.baseURL}/twins`,
            plugins: `${this.baseURL}/plugins`,
            health: `${this.baseURL}/health`
        };
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
    }

    /**
     * Initialize authentication
     */
    initAuthentication() {
        try {
            // Use centralized auth helper functions
            this.currentUser = getCurrentUser();
            this.isAuthenticated = isAuthenticated();
            this.authToken = getAuthToken();
            
            if (this.isAuthenticated) {
                console.log('🔐 Physics Modeling API: User authenticated:', this.currentUser?.username);
            } else {
                console.log('🔐 Physics Modeling API: User not authenticated');
            }
        } catch (error) {
            console.error('❌ Physics Modeling API: Authentication initialization error:', error);
            this.isAuthenticated = false;
        }
    }

    /**
     * Get authentication headers for API calls
     */
    getAuthHeaders() {
        // Use centralized auth helper for consistent token management
        return getAuthHeaders();
    }

    /**
     * Generic API request method
     */
    async request(endpoint, options = {}) {
        // Initialize authentication
        this.initAuthentication();
        
        const defaultOptions = {
            headers: this.getAuthHeaders(),
            credentials: 'same-origin'
        };

        const config = { ...defaultOptions, ...options };

        try {
            const response = await fetch(endpoint, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    /**
     * Model Management API calls
     */
    async createModel(modelData) {
        return this.request(this.endpoints.models + '/create', {
            method: 'POST',
            body: JSON.stringify(modelData)
        });
    }

    async getModels(filters = {}) {
        const params = new URLSearchParams(filters);
        return this.request(`${this.endpoints.models}?${params}`);
    }

    async getModel(modelId) {
        return this.request(`${this.endpoints.models}/${modelId}`);
    }

    async updateModel(modelId, modelData) {
        return this.request(`${this.endpoints.models}/${modelId}`, {
            method: 'PUT',
            body: JSON.stringify(modelData)
        });
    }

    async deleteModel(modelId) {
        return this.request(`${this.endpoints.models}/${modelId}`, {
            method: 'DELETE'
        });
    }

    /**
     * Simulation API calls
     */
    async runSimulation(simulationData) {
        return this.request(this.endpoints.simulations + '/run', {
            method: 'POST',
            body: JSON.stringify(simulationData)
        });
    }

    async getSimulationStatus(simulationId) {
        return this.request(`${this.endpoints.simulations}/${simulationId}/status`);
    }

    async cancelSimulation(simulationId) {
        return this.request(`${this.endpoints.simulations}/${simulationId}/cancel`, {
            method: 'POST'
        });
    }

    async getSimulationResults(simulationId) {
        return this.request(`${this.endpoints.simulations}/${simulationId}/results`);
    }

    async listSimulations(filters = {}) {
        const params = new URLSearchParams(filters);
        return this.request(`${this.endpoints.simulations}?${params}`);
    }

    async getActiveSimulationsCount() {
        return this.request(`${this.endpoints.simulations}/active/count`);
    }

    /**
     * Validation API calls
     */
    async validateModel(modelId, validationData = {}) {
        return this.request(`${this.endpoints.validation}/validate`, {
            method: 'POST',
            body: JSON.stringify({ model_id: modelId, ...validationData })
        });
    }

    async getValidationResults(modelId) {
        return this.request(`${this.endpoints.validation}/${modelId}/results`);
    }

    async compareModels(modelIds) {
        return this.request(`${this.endpoints.validation}/compare`, {
            method: 'POST',
            body: JSON.stringify({ model_ids: modelIds })
        });
    }

    async generateValidationReport(modelId) {
        return this.request(`${this.endpoints.validation}/${modelId}/report`);
    }

    async listValidations(filters = {}) {
        const params = new URLSearchParams(filters);
        return this.request(`${this.endpoints.validation}?${params}`);
    }

    /**
     * Use Cases API calls
     */
    async getUseCases(category = null) {
        const params = category ? `?category=${category}` : '';
        return this.request(`${this.endpoints.useCases}${params}`);
    }

    async getUseCase(useCaseId) {
        return this.request(`${this.endpoints.useCases}/${useCaseId}`);
    }

    async getUseCaseProjects(useCaseId) {
        return this.request(`${this.endpoints.useCases}/${useCaseId}/projects`);
    }

    async createUseCase(useCaseData) {
        return this.request(this.endpoints.useCases, {
            method: 'POST',
            body: JSON.stringify(useCaseData)
        });
    }

    async updateUseCase(useCaseId, useCaseData) {
        return this.request(`${this.endpoints.useCases}/${useCaseId}`, {
            method: 'PUT',
            body: JSON.stringify(useCaseData)
        });
    }

    async deleteUseCase(useCaseId) {
        return this.request(`${this.endpoints.useCases}/${useCaseId}`, {
            method: 'DELETE'
        });
    }

    async getUseCaseTemplates() {
        return this.request(`${this.endpoints.useCases}/templates`);
    }

    async getUseCaseStatistics() {
        return this.request(`${this.endpoints.useCases}/statistics`);
    }

    async getFamousExamples() {
        return this.request(`${this.endpoints.useCases}/famous-examples`);
    }

    async getOptimizationTargets() {
        return this.request(`${this.endpoints.useCases}/optimization-targets`);
    }

    async getHydrogenEconomyUseCase() {
        return this.request(`${this.endpoints.useCases}/hydrogen-economy`);
    }

    async createModelFromUseCase(useCaseName, modelData = {}) {
        return this.request(`${this.endpoints.useCases}/${useCaseName}/create-model`, {
            method: 'POST',
            body: JSON.stringify(modelData)
        });
    }

    /**
     * System API calls
     */
    async getSystemStatus() {
        return this.request(this.endpoints.system + '/status');
    }

    async getSystemHealth() {
        return this.request(this.endpoints.health);
    }

    async getSystemPerformance() {
        return this.request(`${this.endpoints.system}/performance`);
    }

    async getSystemMetrics() {
        return this.request(`${this.endpoints.system}/metrics`);
    }

    async runSystemDiagnostics() {
        return this.request(`${this.endpoints.system}/diagnostics`, {
            method: 'POST'
        });
    }

    /**
     * Twin Registry API calls
     */
    async getAvailableTwins() {
        return this.request(this.endpoints.twins);
    }

    async getTwinDetails(twinId) {
        return this.request(`${this.endpoints.twins}/${twinId}`);
    }

    async refreshTwins() {
        return this.request(`${this.endpoints.twins}/refresh`, {
            method: 'POST'
        });
    }

    /**
     * Plugin Management API calls
     */
    async getAvailablePlugins() {
        return this.request(this.endpoints.plugins);
    }

    async getPluginsForTwin(twinId) {
        return this.request(`${this.endpoints.plugins}/${twinId}`);
    }

    async getPluginDetails(pluginId) {
        return this.request(`${this.endpoints.plugins}/${pluginId}/details`);
    }

    /**
     * Updated Simulation API calls for plugin-based simulations
     */
    async runSimulationWithPlugin(simulationData) {
        return this.request(this.endpoints.simulations + '/run', {
            method: 'POST',
            body: JSON.stringify(simulationData)
        });
    }
}

// Export the API class
export default PhysicsModelingAPI; 