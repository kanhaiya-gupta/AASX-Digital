/**
 * AI RAG Core Module
 * Handles core RAG functionality and query processing
 * Query-only interface for processed AASX data
 */

export default class AIRAGCore {
    constructor() {
        this.isInitialized = false;
        this.config = {
            apiBaseUrl: '/api/ai-rag',
            llmModel: 'gpt-3.5-turbo',
            maxTokens: 4000
        };
        
        this.conversations = new Map();
    }

    /**
     * Initialize the AI RAG Core
     */
    async init() {
        console.log('🔧 Initializing AI RAG Core...');
        
        try {
            // Load configuration
            await this.loadConfiguration();
            
            // Load existing conversations
            await this.loadExistingConversations();
            
            this.isInitialized = true;
            console.log('✅ AI RAG Core initialized');
            
        } catch (error) {
            console.error('❌ AI RAG Core initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load configuration from server
     */
    async loadConfiguration() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/config`);
            if (response.ok) {
                const serverConfig = await response.json();
                this.config = { ...this.config, ...serverConfig.config };
            }
        } catch (error) {
            console.warn('Could not load server configuration, using defaults:', error);
        }
    }

    /**
     * Load existing conversations from local storage
     */
    async loadExistingConversations() {
        const storedConversations = localStorage.getItem('ai_rag_conversations');
        if (storedConversations) {
            try {
                const conversations = JSON.parse(storedConversations);
                conversations.forEach(conv => {
                    this.conversations.set(conv.id, conv);
                });
            } catch (error) {
                console.warn('Failed to load stored conversations:', error);
            }
        }
    }

    /**
     * Load digital twin data from Twin Registry
     */
    async loadDigitalTwinData() {
        try {
            // Get digital twins from Twin Registry API
            const response = await fetch('/api/twin-registry/twins');
            if (response.ok) {
                const twins = await response.json();
                return twins;
            }
        } catch (error) {
            console.warn('Could not load digital twin data:', error);
        }
        return [];
    }

    /**
     * Query processed data using RAG system
     */
    async queryProcessedData(query, options = {}) {
        try {
            const requestData = {
                query: query,
                technique_id: options.technique_id,
                project_id: options.project_id,
                search_limit: options.search_limit || 10,
                llm_model: options.llm_model || this.config.llmModel,
                enable_auto_selection: options.enable_auto_selection !== false
            };

            const response = await fetch(`${this.config.apiBaseUrl}/query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error(`Query failed: ${response.statusText}`);
            }

            const result = await response.json();
            return result;

        } catch (error) {
            console.error('Error querying processed data:', error);
            throw error;
        }
    }

    /**
     * Get system status
     */
    async getSystemStatus() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/status`);
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.warn('Could not get system status:', error);
        }
        return null;
    }

    /**
     * Get available RAG techniques
     */
    async getAvailableTechniques() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/techniques`);
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.warn('Could not get available techniques:', error);
        }
        return [];
    }

    /**
     * Create a new conversation
     */
    createConversation(title = 'New Conversation') {
        const conversation = {
            id: this.generateConversationId(),
            title: title,
            messages: [],
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };
        
        this.conversations.set(conversation.id, conversation);
        this.saveConversationsToLocalStorage();
        
        return conversation;
    }

    /**
     * Generate conversation ID
     */
    generateConversationId() {
        return `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Add message to conversation
     */
    addMessage(conversationId, message) {
        const conversation = this.conversations.get(conversationId);
        if (conversation) {
            const messageObj = {
                id: this.generateMessageId(),
                content: message.content,
                role: message.role, // 'user' or 'assistant'
                timestamp: new Date().toISOString(),
                metadata: message.metadata || {}
            };
            
            conversation.messages.push(messageObj);
            conversation.updatedAt = new Date().toISOString();
            
            this.conversations.set(conversationId, conversation);
            this.saveConversationsToLocalStorage();
            
            return messageObj;
        }
    }

    /**
     * Generate message ID
     */
    generateMessageId() {
        return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Get conversation by ID
     */
    getConversation(id) {
        return this.conversations.get(id);
    }

    /**
     * Get all conversations
     */
    getAllConversations() {
        return Array.from(this.conversations.values());
    }

    /**
     * Delete conversation
     */
    deleteConversation(id) {
        this.conversations.delete(id);
        this.saveConversationsToLocalStorage();
    }

    /**
     * Save conversations to local storage
     */
    saveConversationsToLocalStorage() {
        const conversationsArray = Array.from(this.conversations.values());
        localStorage.setItem('ai_rag_conversations', JSON.stringify(conversationsArray));
    }

    /**
     * Refresh data from server
     */
    async refreshData() {
        try {
            // Refresh configuration
            await this.loadConfiguration();
            
            // Refresh system status
            await this.getSystemStatus();
            
            console.log('✅ Data refreshed successfully');
        } catch (error) {
            console.error('❌ Failed to refresh data:', error);
        }
    }

    /**
     * Get system statistics
     */
    getStatistics() {
        return {
            conversations: this.conversations.size,
            totalMessages: Array.from(this.conversations.values())
                .reduce((total, conv) => total + conv.messages.length, 0),
            isInitialized: this.isInitialized,
            config: this.config
        };
    }

    /**
     * Clean up resources
     */
    destroy() {
        this.conversations.clear();
        this.isInitialized = false;
        console.log('🧹 AI RAG Core destroyed');
    }
} 