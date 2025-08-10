/**
 * Federated Learning Core Module
 * Handles core federated learning operations, federation management, and real-time updates
 */

export default class FederatedLearningCore {
    constructor() {
        this.isInitialized = false;
        
        // Authentication properties
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
        
        this.config = {
            apiBaseUrl: '/api/federated-learning',
            maxParticipants: 100,
            maxRounds: 1000,
            roundTimeout: 300000, // 5 minutes
            aggregationTimeout: 600000, // 10 minutes
            minParticipants: 2,
            batchSize: 32,
            learningRate: 0.01,
            epochs: 10,
            modelType: 'neural_network',
            supportedAlgorithms: ['fedavg', 'fedprox', 'fedsgd', 'scaffold'],
            defaultAlgorithm: 'fedavg',
            cacheEnabled: true,
            cacheExpiry: 300000, // 5 minutes
            realtimeEnabled: true,
            autoStart: false
        };

        this.federation = {
            id: null,
            status: 'inactive', // inactive, active, paused, completed, failed
            algorithm: this.config.defaultAlgorithm,
            participants: new Map(),
            rounds: [],
            currentRound: 0,
            totalRounds: 0,
            startTime: null,
            endTime: null,
            metrics: {
                accuracy: 0,
                loss: 0,
                convergence: 0,
                communicationCost: 0,
                privacyLevel: 0
            }
        };

        this.models = new Map();
        this.datasets = new Map();
        this.participants = new Map();
        this.rounds = new Map();
        this.metrics = new Map();
        this.cache = new Map();
        this.operations = [];
        this.isProcessing = false;
        this.websocket = null;
        this.realtimeConnections = new Map();
        this.statistics = {
            totalFederations: 0,
            activeFederations: 0,
            completedFederations: 0,
            failedFederations: 0,
            totalParticipants: 0,
            totalRounds: 0,
            totalModels: 0,
            lastUpdate: null
        };
    }

    /**
     * Initialize authentication
     */
    initAuthentication() {
        try {
            // Check if user is authenticated
            const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
            const userData = localStorage.getItem('user_data') || sessionStorage.getItem('user_data');
            
            if (token && userData) {
                this.authToken = token;
                this.currentUser = JSON.parse(userData);
                this.isAuthenticated = true;
                console.log('🔐 Federated Learning: User authenticated as', this.currentUser.username);
            } else {
                this.isAuthenticated = false;
                console.log('🔐 Federated Learning: User not authenticated');
            }
        } catch (error) {
            console.error('❌ Federated Learning: Authentication initialization failed:', error);
            this.isAuthenticated = false;
        }
    }

    /**
     * Get authentication token
     */
    getAuthToken() {
        if (!this.authToken) {
            this.initAuthentication();
        }
        return this.authToken;
    }

    /**
     * Get authentication headers
     */
    getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        const token = this.getAuthToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        return headers;
    }

    /**
     * Initialize the Federated Learning Core
     */
    async init() {
        console.log('🔧 Initializing Federated Learning Core...');

        try {
            // Initialize authentication
            this.initAuthentication();
            
            // Load configuration
            await this.loadConfiguration();

            // Initialize federation system
            await this.initializeFederationSystem();

            // Initialize real-time connections
            if (this.config.realtimeEnabled) {
                this.initializeRealtimeConnections();
            }

            // Initialize cache
            if (this.config.cacheEnabled) {
                this.initializeCache();
            }

            // Start operation queue
            this.startOperationQueue();

            this.isInitialized = true;
            console.log('✅ Federated Learning Core initialized');

        } catch (error) {
            console.error('❌ Federated Learning Core initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load configuration from server
     */
    async loadConfiguration() {
        try {
            // Check authentication
            if (!this.isAuthenticated) {
                console.warn('⚠️ Federated Learning: User not authenticated, skipping configuration load');
                return;
            }
            
            const response = await fetch(`${this.config.apiBaseUrl}/config`, {
                headers: this.getAuthHeaders()
            });
            if (response.ok) {
                const config = await response.json();
                this.config = { ...this.config, ...config };
            }
        } catch (error) {
            console.warn('Could not load federated learning configuration from server, using defaults:', error);
        }
    }

    /**
     * Initialize federation system
     */
    async initializeFederationSystem() {
        try {
            // Check authentication
            if (!this.isAuthenticated) {
                throw new Error('User not authenticated');
            }
            
            const response = await fetch(`${this.config.apiBaseUrl}/initialize`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });
            
            if (!response.ok) {
                throw new Error(`Failed to initialize federation system: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.federation.id = data.federationId;
            
            console.log('Federation system initialized');
        } catch (error) {
            console.error('Federation system initialization failed:', error);
            throw error;
        }
    }

    /**
     * Initialize real-time connections
     */
    initializeRealtimeConnections() {
        // Set up WebSocket connection
        this.setupWebSocket();
        
        // Set up real-time update intervals
        setInterval(() => {
            this.updateRealtimeMetrics();
        }, 5000);
    }

    /**
     * Initialize cache system
     */
    initializeCache() {
        // Set up cache cleanup interval
        setInterval(() => {
            this.cleanupCache();
        }, this.config.cacheExpiry);
    }

    /**
     * Start operation queue
     */
    startOperationQueue() {
        setInterval(() => {
            this.processOperationQueue();
        }, 1000);
    }

    /**
     * Create a new federation
     */
    async createFederation(federationConfig) {
        try {
            // Check authentication
            if (!this.isAuthenticated) {
                throw new Error('User not authenticated');
            }
            
            const response = await fetch(`${this.config.apiBaseUrl}/federations`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(federationConfig)
            });

            if (response.ok) {
                const federation = await response.json();
                
                // Update local state
                this.federation = { ...this.federation, ...federation };
                this.federations.set(federation.id, federation);
                
                this.updateStatistics();
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('federationCreated', {
                    detail: { federation }
                }));

                return federation;
            } else {
                throw new Error(`Failed to create federation: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Federation creation failed:', error);
            throw error;
        }
    }

    /**
     * Start federation
     */
    async startFederation(federationId = null) {
        try {
            // Check authentication
            if (!this.isAuthenticated) {
                throw new Error('User not authenticated');
            }
            
            const id = federationId || this.federation.id;
            if (!id) {
                throw new Error('No federation ID provided');
            }

            const response = await fetch(`${this.config.apiBaseUrl}/federations/${id}/start`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const result = await response.json();
                
                // Update federation status
                this.federation.status = 'active';
                this.federation.startTime = new Date().toISOString();
                
                // Start real-time updates
                this.startRealtimeUpdates();
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('federationStarted', {
                    detail: { federationId: id, result }
                }));

                return result;
            } else {
                throw new Error(`Failed to start federation: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Federation start failed:', error);
            throw error;
        }
    }

    /**
     * Stop federation
     */
    async stopFederation(federationId = null) {
        try {
            // Check authentication
            if (!this.isAuthenticated) {
                throw new Error('User not authenticated');
            }
            
            const id = federationId || this.federation.id;
            if (!id) {
                throw new Error('No federation ID provided');
            }

            const response = await fetch(`${this.config.apiBaseUrl}/federations/${id}/stop`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const result = await response.json();
                
                // Update federation status
                this.federation.status = 'inactive';
                this.federation.endTime = new Date().toISOString();
                
                // Stop real-time updates
                this.stopRealtimeUpdates();
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('federationStopped', {
                    detail: { federationId: id, result }
                }));

                return result;
            } else {
                throw new Error(`Failed to stop federation: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Federation stop failed:', error);
            throw error;
        }
    }

    /**
     * Add participant to federation
     */
    async addParticipant(federationId, participantConfig) {
        try {
            // Check authentication
            if (!this.isAuthenticated) {
                throw new Error('User not authenticated');
            }
            
            const response = await fetch(`${this.config.apiBaseUrl}/federations/${federationId}/participants`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(participantConfig)
            });

            if (response.ok) {
                const participant = await response.json();
                
                // Update local state
                this.participants.set(participant.id, participant);
                this.federation.participants.set(participant.id, participant);
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('participantAdded', {
                    detail: { federationId, participant }
                }));

                return participant;
            } else {
                throw new Error(`Failed to add participant: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Participant addition failed:', error);
            throw error;
        }
    }

    /**
     * Remove participant from federation
     */
    async removeParticipant(federationId, participantId) {
        try {
            // Check authentication
            if (!this.isAuthenticated) {
                throw new Error('User not authenticated');
            }
            
            const response = await fetch(`${this.config.apiBaseUrl}/federations/${federationId}/participants/${participantId}`, {
                method: 'DELETE',
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                // Update local state
                this.participants.delete(participantId);
                this.federation.participants.delete(participantId);
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('participantRemoved', {
                    detail: { federationId, participantId }
                }));

                return true;
            } else {
                throw new Error(`Failed to remove participant: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Participant removal failed:', error);
            throw error;
        }
    }

    /**
     * Run federated learning round
     */
    async runFederatedRound(federationId, roundConfig = {}) {
        try {
            // Check authentication
            if (!this.isAuthenticated) {
                throw new Error('User not authenticated');
            }
            
            const response = await fetch(`${this.config.apiBaseUrl}/federations/${federationId}/rounds`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(roundConfig)
            });

            if (response.ok) {
                const round = await response.json();
                
                // Update local state
                this.rounds.set(round.id, round);
                this.federation.rounds.push(round);
                this.federation.currentRound = round.roundNumber;
                
                // Update metrics
                this.updateFederationMetrics(round);
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('federatedRoundCompleted', {
                    detail: { federationId, round }
                }));

                return round;
            } else {
                throw new Error(`Failed to run federated round: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Federated round failed:', error);
            throw error;
        }
    }

    /**
     * Get federation status
     */
    async getFederationStatus(federationId = null) {
        try {
            // Check authentication
            if (!this.isAuthenticated) {
                throw new Error('User not authenticated');
            }
            
            const id = federationId || this.federation.id;
            if (!id) {
                throw new Error('No federation ID provided');
            }

            const response = await fetch(`${this.config.apiBaseUrl}/federations/${id}/status`, {
                headers: this.getAuthHeaders()
            });
            if (response.ok) {
                const status = await response.json();
                
                // Update local state
                this.federation = { ...this.federation, ...status };
                
                return status;
            } else {
                throw new Error(`Failed to get federation status: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Failed to get federation status:', error);
            throw error;
        }
    }

    /**
     * Get federation metrics
     */
    async getFederationMetrics(federationId = null) {
        try {
            // Check authentication
            if (!this.isAuthenticated) {
                throw new Error('User not authenticated');
            }
            
            const id = federationId || this.federation.id;
            if (!id) {
                throw new Error('No federation ID provided');
            }

            const response = await fetch(`${this.config.apiBaseUrl}/federations/${id}/metrics`, {
                headers: this.getAuthHeaders()
            });
            if (response.ok) {
                const metrics = await response.json();
                
                // Update local state
                this.federation.metrics = { ...this.federation.metrics, ...metrics };
                
                return metrics;
            } else {
                throw new Error(`Failed to get federation metrics: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Failed to get federation metrics:', error);
            throw error;
        }
    }

    /**
     * Get participant performance
     */
    async getParticipantPerformance(federationId, participantId) {
        try {
            // Check authentication
            if (!this.isAuthenticated) {
                throw new Error('User not authenticated');
            }
            
            const response = await fetch(`${this.config.apiBaseUrl}/federations/${federationId}/participants/${participantId}/performance`, {
                headers: this.getAuthHeaders()
            });
            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Failed to get participant performance: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Failed to get participant performance:', error);
            throw error;
        }
    }

    /**
     * Get cross-participant insights
     */
    async getCrossParticipantInsights(federationId) {
        try {
            // Check authentication
            if (!this.isAuthenticated) {
                throw new Error('User not authenticated');
            }
            
            const response = await fetch(`${this.config.apiBaseUrl}/federations/${federationId}/insights`, {
                headers: this.getAuthHeaders()
            });
            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Failed to get cross-participant insights: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Failed to get cross-participant insights:', error);
            throw error;
        }
    }

    /**
     * Setup WebSocket connection
     */
    setupWebSocket() {
        try {
            this.websocket = new WebSocket(`${this.config.apiBaseUrl.replace('http', 'ws')}/ws`);
            
            this.websocket.onopen = () => {
                console.log('🔌 Federated Learning WebSocket connected');
            };
            
            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleRealtimeUpdate(data);
            };
            
            this.websocket.onclose = () => {
                console.log('🔌 Federated Learning WebSocket disconnected');
                // Attempt to reconnect after 5 seconds
                setTimeout(() => {
                    this.setupWebSocket();
                }, 5000);
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        } catch (error) {
            console.error('Failed to setup WebSocket:', error);
        }
    }

    /**
     * Handle real-time updates
     */
    handleRealtimeUpdate(data) {
        try {
            switch (data.type) {
                case 'federation_status_update':
                    this.handleFederationStatusUpdate(data.payload);
                    break;
                case 'participant_update':
                    this.handleParticipantUpdate(data.payload);
                    break;
                case 'round_update':
                    this.handleRoundUpdate(data.payload);
                    break;
                case 'metrics_update':
                    this.handleMetricsUpdate(data.payload);
                    break;
                case 'error':
                    this.handleError(data.payload);
                    break;
                default:
                    console.warn('Unknown real-time update type:', data.type);
            }
        } catch (error) {
            console.error('Failed to handle real-time update:', error);
        }
    }

    /**
     * Handle federation status update
     */
    handleFederationStatusUpdate(payload) {
        this.federation = { ...this.federation, ...payload };
        
        // Dispatch event
        window.dispatchEvent(new CustomEvent('federationStatusUpdated', {
            detail: { federation: this.federation }
        }));
    }

    /**
     * Handle participant update
     */
    handleParticipantUpdate(payload) {
        this.participants.set(payload.id, payload);
        this.federation.participants.set(payload.id, payload);
        
        // Dispatch event
        window.dispatchEvent(new CustomEvent('participantUpdated', {
            detail: { participant: payload }
        }));
    }

    /**
     * Handle round update
     */
    handleRoundUpdate(payload) {
        this.rounds.set(payload.id, payload);
        
        // Dispatch event
        window.dispatchEvent(new CustomEvent('roundUpdated', {
            detail: { round: payload }
        }));
    }

    /**
     * Handle metrics update
     */
    handleMetricsUpdate(payload) {
        this.federation.metrics = { ...this.federation.metrics, ...payload };
        
        // Dispatch event
        window.dispatchEvent(new CustomEvent('metricsUpdated', {
            detail: { metrics: this.federation.metrics }
        }));
    }

    /**
     * Handle error
     */
    handleError(payload) {
        console.error('Federated Learning Error:', payload);
        
        // Dispatch event
        window.dispatchEvent(new CustomEvent('federatedLearningError', {
            detail: { error: payload }
        }));
    }

    /**
     * Start real-time updates
     */
    startRealtimeUpdates() {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({
                type: 'start_updates',
                federationId: this.federation.id
            }));
        }
    }

    /**
     * Stop real-time updates
     */
    stopRealtimeUpdates() {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({
                type: 'stop_updates',
                federationId: this.federation.id
            }));
        }
    }

    /**
     * Update real-time metrics
     */
    async updateRealtimeMetrics() {
        try {
            if (this.federation.status === 'active') {
                await this.getFederationMetrics();
                await this.getFederationStatus();
            }
        } catch (error) {
            console.error('Failed to update real-time metrics:', error);
        }
    }

    /**
     * Update federation metrics
     */
    updateFederationMetrics(round) {
        if (round.metrics) {
            this.federation.metrics = {
                ...this.federation.metrics,
                ...round.metrics
            };
        }
    }

    /**
     * Process operation queue
     */
    async processOperationQueue() {
        if (this.isProcessing || this.operations.length === 0) {
            return;
        }

        this.isProcessing = true;

        try {
            const batch = this.operations.splice(0, 5);
            
            for (const operation of batch) {
                try {
                    const result = await operation.execute();
                    operation.resolve(result);
                } catch (error) {
                    operation.reject(error);
                }
            }
        } finally {
            this.isProcessing = false;
        }
    }

    /**
     * Add operation to queue
     */
    addToOperationQueue(operation) {
        return new Promise((resolve, reject) => {
            this.operations.push({
                execute: operation,
                resolve,
                reject
            });
        });
    }

    /**
     * Cleanup cache
     */
    cleanupCache() {
        const now = Date.now();
        for (const [key, value] of this.cache.entries()) {
            if (now - value.timestamp > this.config.cacheExpiry) {
                this.cache.delete(key);
            }
        }
    }

    /**
     * Update statistics
     */
    updateStatistics() {
        this.statistics = {
            totalFederations: this.federations.size,
            activeFederations: Array.from(this.federations.values()).filter(f => f.status === 'active').length,
            completedFederations: Array.from(this.federations.values()).filter(f => f.status === 'completed').length,
            failedFederations: Array.from(this.federations.values()).filter(f => f.status === 'failed').length,
            totalParticipants: this.participants.size,
            totalRounds: this.rounds.size,
            totalModels: this.models.size,
            lastUpdate: new Date().toISOString()
        };
    }

    /**
     * Get federation statistics
     */
    getStatistics() {
        return { ...this.statistics };
    }

    /**
     * Clear cache
     */
    clearCache() {
        this.cache.clear();
        console.log('Federated Learning cache cleared');
    }

    /**
     * Refresh data
     */
    async refreshData() {
        try {
            // Check authentication
            if (!this.isAuthenticated) {
                console.warn('⚠️ Federated Learning: User not authenticated, skipping data refresh');
                return;
            }
            
            // Refresh federation status
            if (this.federation.id) {
                await this.getFederationStatus();
                await this.getFederationMetrics();
            }
            
            // Update statistics
            this.updateStatistics();
            
            // Dispatch event
            window.dispatchEvent(new CustomEvent('federatedLearningDataRefreshed'));
        } catch (error) {
            console.error('Data refresh failed:', error);
            throw error;
        }
    }

    /**
     * Destroy the core module
     */
    destroy() {
        this.isInitialized = false;
        
        // Close WebSocket connection
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        
        // Clear all data structures
        this.federations.clear();
        this.models.clear();
        this.datasets.clear();
        this.participants.clear();
        this.rounds.clear();
        this.metrics.clear();
        this.cache.clear();
        this.operations = [];
        this.realtimeConnections.clear();
        
        console.log('🧹 Federated Learning Core destroyed');
    }
} 