/**
 * API Client
 * Main API client for handling all backend communication
 */

export class APIClient {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
        this.endpoints = {
            // Auth System
            auth: {
                login: '/api/auth/login',
                logout: '/api/auth/logout',
                register: '/api/auth/register',
                profile: '/api/auth/profile',
                refresh: '/api/auth/refresh',
                validate: '/api/auth/validate',
                changePassword: '/api/auth/change-password',
                resetPassword: '/api/auth/reset-password',
                verifyEmail: '/api/auth/verify-email'
            },
            // AASX ETL Pipeline
            aasx_etl: {
                status: '/aasx-etl/status',
                process: '/aasx-etl/process',
                results: '/aasx-etl/results',
                config: '/aasx-etl/config',
                upload: '/aasx-etl/upload',
                download: '/aasx-etl/download'
            },
            // AI/RAG System
            ai_rag: {
                query: '/ai-rag/query',
                demo: '/ai-rag/demo',
                stats: '/ai-rag/stats',
                collections: '/ai-rag/collections',
                index_data: '/ai-rag/index-data',
                techniques: '/ai-rag/techniques',
                technique_recommendations: '/ai-rag/techniques/recommendations',
                technique_execute: '/ai-rag/techniques/execute',
                technique_compare: '/ai-rag/techniques/compare'
            },
            // Knowledge Graph
            kg_neo4j: {
                status: '/kg-neo4j/api/status',
                query: '/kg-neo4j/api/query',
                graph: '/kg-neo4j/api/graph',
                stats: '/kg-neo4j/api/stats',
                load_data: '/kg-neo4j/api/load-data',
                nodes: '/kg-neo4j/api/nodes',
                relationships: '/kg-neo4j/api/relationships'
            },
            // Twin Registry
            twin_registry: {
                list: '/twin-registry/twins',
                create: '/twin-registry/twins',
                update: '/twin-registry/twins',
                delete: '/twin-registry/twins',
                status: '/twin-registry/status',
                monitor: '/twin-registry/monitor',
                health: '/twin-registry/health'
            },
            // Certificate Manager
            certificate_manager: {
                list: '/certificate-manager/certificates',
                create: '/certificate-manager/certificates',
                update: '/certificate-manager/certificates',
                delete: '/certificate-manager/certificates',
                validate: '/certificate-manager/validate',
                revoke: '/certificate-manager/revoke',
                templates: '/certificate-manager/templates',
                export: '/certificate-manager/export'
            },
            // Federated Learning
            federated_learning: {
                status: '/federated-learning/status',
                models: '/federated-learning/models',
                train: '/federated-learning/train',
                evaluate: '/federated-learning/evaluate',
                deploy: '/federated-learning/deploy',
                participants: '/federated-learning/participants',
                rounds: '/federated-learning/rounds'
            },
            // Physics Modeling
            physics_modeling: {
                status: '/physics-modeling/status',
                models: '/physics-modeling/models',
                simulate: '/physics-modeling/simulate',
                analyze: '/physics-modeling/analyze',
                visualize: '/physics-modeling/visualize',
                plugins: '/physics-modeling/plugins',
                use_cases: '/physics-modeling/use-cases'
            },
            // Analytics (Dashboard)
            analytics: {
                dashboard: '/analytics/dashboard',
                metrics: '/analytics/metrics',
                reports: '/analytics/reports'
            },
            // System
            system: {
                health: '/health',
                status: '/status'
            }
        };
    }

    /**
     * Make HTTP request with error handling
     */
    async request(endpoint, options = {}) {
        const url = this.baseURL + endpoint;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            console.error(`API request failed for ${endpoint}:`, error);
            throw error;
        }
    }

    /**
     * Auth System API Methods
     */
    async login(credentials) {
        return this.request(this.endpoints.auth.login, {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
    }

    async logout() {
        return this.request(this.endpoints.auth.logout);
    }

    async register(userData) {
        return this.request(this.endpoints.auth.register, {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    async getProfile() {
        return this.request(this.endpoints.auth.profile);
    }

    async refreshToken() {
        return this.request(this.endpoints.auth.refresh);
    }

    async validateToken() {
        return this.request(this.endpoints.auth.validate);
    }

    async changePassword(currentPassword, newPassword) {
        return this.request(this.endpoints.auth.changePassword, {
            method: 'POST',
            body: JSON.stringify({ current_password: currentPassword, new_password: newPassword })
        });
    }

    async resetPassword(email) {
        return this.request(this.endpoints.auth.resetPassword, {
            method: 'POST',
            body: JSON.stringify({ email })
        });
    }

    async verifyEmail(token) {
        return this.request(this.endpoints.auth.verifyEmail, {
            method: 'POST',
            body: JSON.stringify({ token })
        });
    }

    /**
     * AASX ETL Pipeline API Methods
     */
    async getAASXETLStatus() {
        return this.request(this.endpoints.aasx_etl.status);
    }

    async processAASXETL(inputDir = null, outputDir = null) {
        const requestBody = {};
        if (inputDir) requestBody.input_dir = inputDir;
        if (outputDir) requestBody.output_dir = outputDir;
        
        return this.request(this.endpoints.aasx_etl.process, {
            method: 'POST',
            body: JSON.stringify(requestBody)
        });
    }

    async getAASXETLResults() {
        return this.request(this.endpoints.aasx_etl.results);
    }

    async getAASXETLConfig() {
        return this.request(this.endpoints.aasx_etl.config);
    }

    async uploadAASXData(file) {
        const formData = new FormData();
        formData.append('file', file);
        return this.request(this.endpoints.aasx_etl.upload, {
            method: 'POST',
            body: formData
        });
    }

    async downloadAASXData(filePath) {
        return this.request(this.endpoints.aasx_etl.download, {
            method: 'GET',
            responseType: 'blob' // Assuming responseType is supported by fetch
        });
    }

    /**
     * AI/RAG System API Methods
     */
    async queryAIRAG(query, analysisType = 'general', collection = 'aasx_assets', config = {}) {
        const requestBody = {
            query: query,
            analysis_type: analysisType,
            collection: collection,
            ...config
        };
        
        return this.request(this.endpoints.ai_rag.query, {
            method: 'POST',
            body: JSON.stringify(requestBody)
        });
    }

    async runDemoQueries() {
        return this.request(this.endpoints.ai_rag.demo, { method: 'POST' });
    }

    async getAIRAGStats() {
        return this.request(this.endpoints.ai_rag.stats);
    }

    async getCollections() {
        return this.request(this.endpoints.ai_rag.collections);
    }

    async indexETLData() {
        return this.request(this.endpoints.ai_rag.index_data, { method: 'POST' });
    }

    async getRAGTechniques() {
        return this.request(this.endpoints.ai_rag.techniques);
    }

    async getTechniqueRecommendations(query) {
        return this.request(this.endpoints.ai_rag.technique_recommendations, {
            method: 'POST',
            body: JSON.stringify({ query })
        });
    }

    async executeRAGTechnique(query, techniqueId, parameters = {}) {
        const requestBody = {
            query: query,
            technique_id: techniqueId,
            parameters: parameters
        };
        
        return this.request(this.endpoints.ai_rag.technique_execute, {
            method: 'POST',
            body: JSON.stringify(requestBody)
        });
    }

    async compareRAGTechniques(query, techniqueIds = null, parameters = {}) {
        const requestBody = {
            query: query,
            technique_ids: techniqueIds,
            parameters: parameters
        };
        
        return this.request(this.endpoints.ai_rag.technique_compare, {
            method: 'POST',
            body: JSON.stringify(requestBody)
        });
    }

    /**
     * Knowledge Graph API Methods
     */
    async getKGStatus() {
        return this.request(this.endpoints.kg_neo4j.status);
    }

    async queryKG(query) {
        return this.request(this.endpoints.kg_neo4j.query, {
            method: 'POST',
            body: JSON.stringify({ query })
        });
    }

    async getGraphData() {
        return this.request(this.endpoints.kg_neo4j.graph);
    }

    async getKGStats() {
        return this.request(this.endpoints.kg_neo4j.stats);
    }

    async loadKGData(dataPath) {
        return this.request(this.endpoints.kg_neo4j.load_data, {
            method: 'POST',
            body: JSON.stringify({ data_path: dataPath })
        });
    }

    async getKGNodes() {
        return this.request(this.endpoints.kg_neo4j.nodes);
    }

    async getKGRelationships() {
        return this.request(this.endpoints.kg_neo4j.relationships);
    }

    /**
     * Twin Registry API Methods
     */
    async getTwins() {
        return this.request(this.endpoints.twin_registry.list);
    }

    async createTwin(twinData) {
        return this.request(this.endpoints.twin_registry.create, {
            method: 'POST',
            body: JSON.stringify(twinData)
        });
    }

    async updateTwin(id, twinData) {
        return this.request(`${this.endpoints.twin_registry.update}/${id}`, {
            method: 'PUT',
            body: JSON.stringify(twinData)
        });
    }

    async deleteTwin(id) {
        return this.request(`${this.endpoints.twin_registry.delete}/${id}`, {
            method: 'DELETE'
        });
    }

    async getTwinStatus() {
        return this.request(this.endpoints.twin_registry.status);
    }

    async getTwinMonitor() {
        return this.request(this.endpoints.twin_registry.monitor);
    }

    async getTwinHealth() {
        return this.request(this.endpoints.twin_registry.health);
    }

    /**
     * Certificate Manager API Methods
     */
    async getCertificates() {
        return this.request(this.endpoints.certificate_manager.list);
    }

    async createCertificate(certData) {
        return this.request(this.endpoints.certificate_manager.create, {
            method: 'POST',
            body: JSON.stringify(certData)
        });
    }

    async updateCertificate(id, certData) {
        return this.request(`${this.endpoints.certificate_manager.update}/${id}`, {
            method: 'PUT',
            body: JSON.stringify(certData)
        });
    }

    async deleteCertificate(id) {
        return this.request(`${this.endpoints.certificate_manager.delete}/${id}`, {
            method: 'DELETE'
        });
    }

    async validateCertificate(certData) {
        return this.request(this.endpoints.certificate_manager.validate, {
            method: 'POST',
            body: JSON.stringify(certData)
        });
    }

    async revokeCertificate(certData) {
        return this.request(this.endpoints.certificate_manager.revoke, {
            method: 'POST',
            body: JSON.stringify(certData)
        });
    }

    async getCertificateTemplates() {
        return this.request(this.endpoints.certificate_manager.templates);
    }

    async exportCertificates() {
        return this.request(this.endpoints.certificate_manager.export, {
            method: 'GET',
            responseType: 'blob' // Assuming responseType is supported by fetch
        });
    }

    /**
     * Federated Learning API Methods
     */
    async getFederatedLearningStatus() {
        return this.request(this.endpoints.federated_learning.status);
    }

    async getFederatedLearningModels() {
        return this.request(this.endpoints.federated_learning.models);
    }

    async trainFederatedModel(modelId, dataPath) {
        const requestBody = {
            model_id: modelId,
            data_path: dataPath
        };
        return this.request(this.endpoints.federated_learning.train, {
            method: 'POST',
            body: JSON.stringify(requestBody)
        });
    }

    async evaluateFederatedModel(modelId, testDataPath) {
        const requestBody = {
            model_id: modelId,
            test_data_path: testDataPath
        };
        return this.request(this.endpoints.federated_learning.evaluate, {
            method: 'POST',
            body: JSON.stringify(requestBody)
        });
    }

    async deployFederatedModel(modelId, deploymentConfig) {
        const requestBody = {
            model_id: modelId,
            deployment_config: deploymentConfig
        };
        return this.request(this.endpoints.federated_learning.deploy, {
            method: 'POST',
            body: JSON.stringify(requestBody)
        });
    }

    async getFederatedLearningParticipants() {
        return this.request(this.endpoints.federated_learning.participants);
    }

    async getFederatedLearningRounds() {
        return this.request(this.endpoints.federated_learning.rounds);
    }

    /**
     * Physics Modeling API Methods
     */
    async getPhysicsModelingStatus() {
        return this.request(this.endpoints.physics_modeling.status);
    }

    async getPhysicsModels() {
        return this.request(this.endpoints.physics_modeling.models);
    }

    async simulatePhysicsModel(modelId, parameters) {
        const requestBody = {
            model_id: modelId,
            parameters: parameters
        };
        return this.request(this.endpoints.physics_modeling.simulate, {
            method: 'POST',
            body: JSON.stringify(requestBody)
        });
    }

    async analyzePhysicsModel(modelId, dataPath) {
        const requestBody = {
            model_id: modelId,
            data_path: dataPath
        };
        return this.request(this.endpoints.physics_modeling.analyze, {
            method: 'POST',
            body: JSON.stringify(requestBody)
        });
    }

    async visualizePhysicsModel(modelId, dataPath) {
        const requestBody = {
            model_id: modelId,
            data_path: dataPath
        };
        return this.request(this.endpoints.physics_modeling.visualize, {
            method: 'POST',
            body: JSON.stringify(requestBody)
        });
    }

    async getPhysicsModelingPlugins() {
        return this.request(this.endpoints.physics_modeling.plugins);
    }

    async getPhysicsModelingUseCases() {
        return this.request(this.endpoints.physics_modeling.use_cases);
    }

    /**
     * Analytics API Methods
     */
    async getDashboardData() {
        return this.request(this.endpoints.analytics.dashboard);
    }

    async getMetrics() {
        return this.request(this.endpoints.analytics.metrics);
    }

    async getReports() {
        return this.request(this.endpoints.analytics.reports);
    }

    /**
     * System API Methods
     */
    async getHealth() {
        return this.request(this.endpoints.system.health);
    }

    async getSystemStatus() {
        return this.request(this.endpoints.system.status);
    }

    /**
     * Check all services status
     */
    async checkAllServices() {
        try {
            const results = await Promise.allSettled([
                this.getHealth(),
                this.getAASXETLStatus(),
                this.getKGStatus(),
                this.getTwinStatus(),
                this.getAIRAGStats()
            ]);

            return {
                health: results[0].status === 'fulfilled' ? results[0].value : null,
                aasx_etl: results[1].status === 'fulfilled' ? results[1].value : null,
                kg: results[2].status === 'fulfilled' ? results[2].value : null,
                twin: results[3].status === 'fulfilled' ? results[3].value : null,
                ai_rag: results[4].status === 'fulfilled' ? results[4].value : null
            };
        } catch (error) {
            console.error('Error checking services:', error);
            throw error;
        }
    }
} 