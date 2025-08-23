/**
 * AI RAG Generator Module
 * Handles text generation, response creation, and AI model management
 */

export default class AIRAGGenerator {
    constructor() {
        this.isInitialized = false;
        this.config = {
            apiBaseUrl: '/api/ai-rag',
            defaultModel: 'gpt-3.5-turbo',
            maxTokens: 4000,
            temperature: 0.7,
            topP: 0.9,
            frequencyPenalty: 0.0,
            presencePenalty: 0.0,
            maxRetries: 3,
            retryDelay: 1000,
            streamingEnabled: true
        };
        
        this.models = new Map();
        this.templates = new Map();
        this.generationHistory = new Map();
        this.activeGenerations = new Set();
        this.streamingConnections = new Map();
        
        // Authentication properties (will be updated by global auth manager)
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
    }

    /**
     * Wait for central auth system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 AI RAG Generator: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 AI RAG Generator: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 AI RAG Generator: Auth system ready event received');
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
                console.warn('⚠️ AI RAG Generator: Timeout waiting for auth system');
                resolve();
            }, 10000);
        });
    }

    /**
     * Update authentication state from central auth manager
     */
    updateAuthState() {
        if (!window.authManager) {
            console.log('⚠️ AI RAG Generator: No auth manager available');
            return;
        }
        
        try {
            const sessionInfo = window.authManager.getSessionInfo();
            console.log('🔐 AI RAG Generator: Auth state update:', sessionInfo);
            
            if (sessionInfo && sessionInfo.isAuthenticated) {
                this.isAuthenticated = true;
                this.currentUser = {
                    user_id: sessionInfo.user_id,
                    username: sessionInfo.username,
                    role: sessionInfo.role,
                    organization_id: sessionInfo.organization_id
                };
                this.authToken = window.authManager.getStoredToken();
                console.log('🔐 AI RAG Generator: User authenticated:', this.currentUser.username);
            } else {
                this.isAuthenticated = false;
                this.currentUser = null;
                this.authToken = null;
                console.log('🔐 AI RAG Generator: User not authenticated (demo mode)');
            }
        } catch (error) {
            console.warn('⚠️ AI RAG Generator: Error updating auth state:', error);
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
        }
    }

    /**
     * Setup authentication listeners
     */
    setupAuthListeners() {
        // Listen for auth state changes
        window.addEventListener('authStateChanged', () => {
            console.log('🔄 AI RAG Generator: Auth state changed, updating...');
            this.updateAuthState();
        });
        
        // Listen for login success
        window.addEventListener('loginSuccess', async () => {
            console.log('🔐 AI RAG Generator: Login success detected');
            this.updateAuthState();
            // Refresh data after login
            this.loadGenerationHistory();
        });
        
        // Listen for logout
        window.addEventListener('logout', () => {
            console.log('🔐 AI RAG Generator: Logout detected');
            this.updateAuthState();
            // Clear sensitive data after logout
            this.generationHistory.clear();
        });
    }

    /**
     * Get authentication headers for API calls
     */
    getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        // ✅ CORRECT: Get token from central auth manager
        if (window.authManager) {
            const token = window.authManager.getStoredToken();
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
        }
        
        return headers;
    }

    /**
     * Initialize the Generator
     */
    async init() {
        console.log('🔧 Initializing AI RAG Generator...');
        
        try {
            // ✅ CORRECT: Wait for central auth system first
            await this.waitForAuthSystem();
            
            // ✅ CORRECT: Update auth state from central system
            this.updateAuthState();
            
            // ✅ CORRECT: Listen for auth state changes
            this.setupAuthListeners();
            
            // Load configuration
            await this.loadConfiguration();
            
            // Load available models
            await this.loadModels();
            
            // Initialize templates
            this.initializeTemplates();
            
            // Load generation history
            this.loadGenerationHistory();
            
            this.isInitialized = true;
            console.log('✅ AI RAG Generator initialized with central auth integration');
            
        } catch (error) {
            console.error('❌ AI RAG Generator initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load configuration from server
     */
    async loadConfiguration() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/generator-config`, {
                headers: this.getAuthHeaders()
            });
            if (response.ok) {
                const serverConfig = await response.json();
                this.config = { ...this.config, ...serverConfig };
            }
        } catch (error) {
            console.warn('Could not load generator configuration, using defaults:', error);
        }
    }

    /**
     * Load available models
     */
    async loadModels() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/models`, {
                headers: this.getAuthHeaders()
            });
            if (response.ok) {
                const models = await response.json();
                models.forEach(model => {
                    this.models.set(model.id, model);
                });
            }
        } catch (error) {
            console.warn('Could not load models, using defaults:', error);
            // Set default models
            this.models.set('gpt-3.5-turbo', {
                id: 'gpt-3.5-turbo',
                name: 'GPT-3.5 Turbo',
                provider: 'openai',
                maxTokens: 4096,
                costPerToken: 0.000002
            });
            this.models.set('gpt-4', {
                id: 'gpt-4',
                name: 'GPT-4',
                provider: 'openai',
                maxTokens: 8192,
                costPerToken: 0.00003
            });
        }
    }

    /**
     * Initialize response templates
     */
    initializeTemplates() {
        this.templates.set('qa', {
            name: 'Question & Answer',
            description: 'Generate answers to questions based on retrieved context',
            systemPrompt: `You are a helpful AI assistant. Answer questions based on the provided context. 
            If the context doesn't contain enough information to answer the question, say so. 
            Always cite your sources when possible.`,
            userPrompt: `Context: {context}\n\nQuestion: {question}\n\nAnswer:`
        });
        
        this.templates.set('summary', {
            name: 'Document Summary',
            description: 'Generate summaries of documents or text passages',
            systemPrompt: `You are an expert at summarizing documents. Create concise, accurate summaries 
            that capture the key points and main ideas.`,
            userPrompt: `Please summarize the following text:\n\n{text}\n\nSummary:`
        });
        
        this.templates.set('explanation', {
            name: 'Technical Explanation',
            description: 'Explain technical concepts in simple terms',
            systemPrompt: `You are a technical expert who can explain complex concepts in simple terms. 
            Use clear language and provide examples when helpful.`,
            userPrompt: `Please explain the following technical concept in simple terms:\n\n{concept}\n\nExplanation:`
        });
        
        this.templates.set('code', {
            name: 'Code Generation',
            description: 'Generate code based on requirements and context',
            systemPrompt: `You are an expert programmer. Generate clean, well-documented code based on 
            the requirements. Include comments and follow best practices.`,
            userPrompt: `Requirements: {requirements}\n\nContext: {context}\n\nCode:`
        });
        
        this.templates.set('analysis', {
            name: 'Data Analysis',
            description: 'Analyze data and provide insights',
            systemPrompt: `You are a data analyst. Analyze the provided data and provide meaningful insights, 
            trends, and recommendations.`,
            userPrompt: `Data: {data}\n\nAnalysis:`
        });
    }

    /**
     * Load generation history from local storage
     */
    loadGenerationHistory() {
        const stored = localStorage.getItem('ai_rag_generation_history');
        if (stored) {
            try {
                const history = JSON.parse(stored);
                history.forEach(entry => {
                    this.generationHistory.set(entry.id, entry);
                });
            } catch (error) {
                console.warn('Failed to load generation history:', error);
            }
        }
    }

    /**
     * Save generation history to local storage
     */
    saveGenerationHistory() {
        const historyArray = Array.from(this.generationHistory.values());
        localStorage.setItem('ai_rag_generation_history', JSON.stringify(historyArray));
    }

    /**
     * Generate response
     */
    async generateResponse(prompt, context = '', options = {}) {
        const generationId = this.generateGenerationId();
        
        try {
            this.activeGenerations.add(generationId);
            
            // Validate inputs
            this.validateGenerationInputs(prompt, context, options);
            
            // Prepare generation parameters
            const params = this.prepareGenerationParams(prompt, context, options);
            
            // Generate response
            const response = await this.performGeneration(params, options);
            
            // Save to history
            this.saveGenerationToHistory(generationId, params, response, options);
            
            return response;
            
        } catch (error) {
            console.error('Generation failed:', error);
            this.saveGenerationToHistory(generationId, { prompt, context }, { error: error.message }, options);
            throw error;
        } finally {
            this.activeGenerations.delete(generationId);
        }
    }

    /**
     * Generate generation ID
     */
    generateGenerationId() {
        return `gen_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Validate generation inputs
     */
    validateGenerationInputs(prompt, context, options) {
        if (!prompt || typeof prompt !== 'string') {
            throw new Error('Prompt must be a non-empty string');
        }
        
        if (prompt.trim().length === 0) {
            throw new Error('Prompt cannot be empty');
        }
        
        if (context && typeof context !== 'string') {
            throw new Error('Context must be a string');
        }
        
        if (options.model && !this.models.has(options.model)) {
            throw new Error(`Model '${options.model}' is not available`);
        }
    }

    /**
     * Prepare generation parameters
     */
    prepareGenerationParams(prompt, context, options) {
        const model = this.models.get(options.model || this.config.defaultModel);
        
        const params = {
            model: model.id,
            prompt: prompt,
            context: context,
            maxTokens: Math.min(options.maxTokens || this.config.maxTokens, model.maxTokens),
            temperature: options.temperature || this.config.temperature,
            topP: options.topP || this.config.topP,
            frequencyPenalty: options.frequencyPenalty || this.config.frequencyPenalty,
            presencePenalty: options.presencePenalty || this.config.presencePenalty,
            template: options.template || 'qa',
            streaming: options.streaming !== false && this.config.streamingEnabled
        };
        
        // Apply template if specified
        if (params.template && this.templates.has(params.template)) {
            const template = this.templates.get(params.template);
            params.systemPrompt = template.systemPrompt;
            params.userPrompt = template.userPrompt
                .replace('{context}', context)
                .replace('{question}', prompt)
                .replace('{text}', context)
                .replace('{concept}', prompt)
                .replace('{requirements}', prompt)
                .replace('{data}', context);
        }
        
        return params;
    }

    /**
     * Perform generation
     */
    async performGeneration(params, options) {
        const maxRetries = options.maxRetries || this.config.maxRetries;
        let lastError = null;
        
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                if (params.streaming) {
                    return await this.performStreamingGeneration(params);
                } else {
                    return await this.performStandardGeneration(params);
                }
            } catch (error) {
                lastError = error;
                console.warn(`Generation attempt ${attempt} failed:`, error);
                
                if (attempt < maxRetries) {
                    await this.delay(this.config.retryDelay * attempt);
                }
            }
        }
        
        throw lastError || new Error('Generation failed after all retries');
    }

    /**
     * Perform standard generation
     */
    async performStandardGeneration(params) {
        const response = await fetch(`${this.config.apiBaseUrl}/generate`, {
            method: 'POST',
            headers: this.getAuthHeaders(),
            body: JSON.stringify(params)
        });
        
        if (!response.ok) {
            throw new Error('Generation request failed');
        }
        
        const result = await response.json();
        return this.processGenerationResult(result);
    }

    /**
     * Perform streaming generation
     */
    async performStreamingGeneration(params) {
        return new Promise((resolve, reject) => {
            const eventSource = new EventSource(`${this.config.apiBaseUrl}/generate/stream?${new URLSearchParams(params)}`);
            let response = {
                text: '',
                tokens: [],
                metadata: {}
            };
            
            eventSource.onmessage = (event) => {
                const data = JSON.parse(event.data);
                
                if (data.type === 'token') {
                    response.text += data.token;
                    response.tokens.push(data.token);
                } else if (data.type === 'metadata') {
                    response.metadata = { ...response.metadata, ...data.metadata };
                } else if (data.type === 'complete') {
                    response.metadata = { ...response.metadata, ...data.metadata };
                    eventSource.close();
                    resolve(this.processGenerationResult(response));
                } else if (data.type === 'error') {
                    eventSource.close();
                    reject(new Error(data.error));
                }
            };
            
            eventSource.onerror = (error) => {
                eventSource.close();
                reject(error);
            };
            
            // Store connection for potential cleanup
            this.streamingConnections.set(params.model, eventSource);
        });
    }

    /**
     * Process generation result
     */
    processGenerationResult(result) {
        return {
            text: result.text || result.content || '',
            tokens: result.tokens || [],
            metadata: {
                model: result.model || result.metadata?.model,
                tokensUsed: result.tokensUsed || result.metadata?.tokensUsed,
                cost: result.cost || result.metadata?.cost,
                generationTime: result.generationTime || result.metadata?.generationTime,
                timestamp: new Date().toISOString()
            },
            raw: result
        };
    }

    /**
     * Save generation to history
     */
    saveGenerationToHistory(generationId, params, response, options) {
        const historyEntry = {
            id: generationId,
            prompt: params.prompt,
            context: params.context,
            model: params.model,
            template: params.template,
            response: response.text || response.error,
            metadata: response.metadata || {},
            timestamp: new Date().toISOString(),
            status: response.error ? 'error' : 'success'
        };
        
        this.generationHistory.set(generationId, historyEntry);
        
        // Keep only last 1000 generations
        if (this.generationHistory.size > 1000) {
            const entries = Array.from(this.generationHistory.entries());
            entries.sort((a, b) => new Date(b[1].timestamp) - new Date(a[1].timestamp));
            this.generationHistory = new Map(entries.slice(0, 1000));
        }
        
        this.saveGenerationHistory();
    }

    /**
     * Generate RAG response with context retrieval
     */
    async generateRAGResponse(question, contextDocuments = [], options = {}) {
        // Prepare context from documents
        const context = this.prepareContextFromDocuments(contextDocuments);
        
        // Generate response using RAG template
        const ragOptions = {
            ...options,
            template: 'qa',
            context: context
        };
        
        return await this.generateResponse(question, context, ragOptions);
    }

    /**
     * Prepare context from documents
     */
    prepareContextFromDocuments(documents) {
        if (!documents || documents.length === 0) {
            return '';
        }
        
        return documents.map((doc, index) => {
            const source = doc.source || doc.documentId || `Document ${index + 1}`;
            const content = doc.content || doc.text || doc.snippet || '';
            return `Source: ${source}\nContent: ${content}\n`;
        }).join('\n---\n');
    }

    /**
     * Get available models
     */
    getAvailableModels() {
        return Array.from(this.models.values());
    }

    /**
     * Get model by ID
     */
    getModel(modelId) {
        return this.models.get(modelId);
    }

    /**
     * Get available templates
     */
    getAvailableTemplates() {
        return Array.from(this.templates.values());
    }

    /**
     * Get template by ID
     */
    getTemplate(templateId) {
        return this.templates.get(templateId);
    }

    /**
     * Get generation history
     */
    getGenerationHistory(limit = 50) {
        const entries = Array.from(this.generationHistory.values());
        entries.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        return entries.slice(0, limit);
    }

    /**
     * Get generation by ID
     */
    getGeneration(generationId) {
        return this.generationHistory.get(generationId);
    }

    /**
     * Clear generation history
     */
    clearGenerationHistory() {
        this.generationHistory.clear();
        this.saveGenerationHistory();
    }

    /**
     * Estimate generation cost
     */
    estimateCost(prompt, context, modelId) {
        const model = this.models.get(modelId || this.config.defaultModel);
        if (!model) return null;
        
        const totalTokens = this.estimateTokenCount(prompt + context);
        const cost = totalTokens * model.costPerToken;
        
        return {
            estimatedTokens: totalTokens,
            estimatedCost: cost,
            model: model.id,
            costPerToken: model.costPerToken
        };
    }

    /**
     * Estimate token count
     */
    estimateTokenCount(text) {
        // Simple estimation: ~4 characters per token
        return Math.ceil(text.length / 4);
    }

    /**
     * Cancel active generation
     */
    cancelGeneration(generationId) {
        if (this.activeGenerations.has(generationId)) {
            this.activeGenerations.delete(generationId);
            
            // Close streaming connection if exists
            const connection = this.streamingConnections.get(generationId);
            if (connection) {
                connection.close();
                this.streamingConnections.delete(generationId);
            }
            
            return true;
        }
        return false;
    }

    /**
     * Cancel all active generations
     */
    cancelAllGenerations() {
        const cancelled = this.activeGenerations.size;
        
        // Close all streaming connections
        this.streamingConnections.forEach(connection => {
            connection.close();
        });
        this.streamingConnections.clear();
        
        this.activeGenerations.clear();
        return cancelled;
    }

    /**
     * Get active generations
     */
    getActiveGenerations() {
        return Array.from(this.activeGenerations);
    }

    /**
     * Delay utility
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Refresh models
     */
    async refreshModels() {
        await this.loadModels();
        console.log('🔄 AI RAG Generator models refreshed');
    }

    /**
     * Get generation statistics
     */
    getStatistics() {
        const totalGenerations = this.generationHistory.size;
        const successfulGenerations = Array.from(this.generationHistory.values())
            .filter(gen => gen.status === 'success').length;
        const failedGenerations = totalGenerations - successfulGenerations;
        
        return {
            totalGenerations,
            successfulGenerations,
            failedGenerations,
            activeGenerations: this.activeGenerations.size,
            availableModels: this.models.size,
            availableTemplates: this.templates.size
        };
    }

    /**
     * Destroy the generator
     */
    destroy() {
        // Cancel all active generations
        this.cancelAllGenerations();
        
        // Clear data
        this.models.clear();
        this.templates.clear();
        this.generationHistory.clear();
        this.isInitialized = false;
        
        console.log('🧹 AI RAG Generator destroyed');
    }
} 