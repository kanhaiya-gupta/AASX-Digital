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
        
        // Authentication state (will be updated by global auth manager)
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
    }

    /**
     * Initialize the AI RAG Core
     */
    async init() {
        console.log('🔧 Initializing AI RAG Core...');
        
        try {
            // ✅ CORRECT: Wait for central auth system first
            await this.waitForAuthSystem();
            
            // ✅ CORRECT: Update auth state from central system
            this.updateAuthState();
            
            // ✅ CORRECT: Listen for auth state changes
            this.setupAuthListeners();
            
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
     * Wait for central auth system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 AI RAG Core: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 AI RAG Core: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 AI RAG Core: Auth system ready event received');
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
                console.warn('⚠️ AI RAG Core: Timeout waiting for auth system');
                resolve();
            }, 10000);
        });
    }

    /**
     * Update authentication state from central auth manager
     */
    updateAuthState() {
        if (!window.authManager) {
            console.log('⚠️ AI RAG Core: No auth manager available');
            return;
        }
        
        try {
            const sessionInfo = window.authManager.getSessionInfo();
            console.log('🔐 AI RAG Core: Auth state update:', sessionInfo);
            
            if (sessionInfo && sessionInfo.isAuthenticated) {
                this.isAuthenticated = true;
                this.currentUser = {
                    user_id: sessionInfo.user_id,
                    username: sessionInfo.username,
                    role: sessionInfo.role,
                    organization_id: sessionInfo.organization_id
                };
                this.authToken = window.authManager.getStoredToken();
                console.log('🔐 AI RAG Core: User authenticated:', this.currentUser.username);
            } else {
                this.isAuthenticated = false;
                this.currentUser = null;
                this.authToken = null;
                console.log('🔐 AI RAG Core: User not authenticated (demo mode)');
            }
        } catch (error) {
            console.warn('⚠️ AI RAG Core: Error updating auth state:', error);
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
            console.log('🔄 AI RAG Core: Auth state changed, updating...');
            this.updateAuthState();
            this.handleAuthStateChange();
        });
        
        // Listen for login success
        window.addEventListener('loginSuccess', async () => {
            console.log('🔐 AI RAG Core: Login success detected');
            this.updateAuthState();
            await this.handleLoginSuccess();
        });
        
        // Listen for logout
        window.addEventListener('logout', () => {
            console.log('🔐 AI RAG Core: Logout detected');
            this.updateAuthState();
            this.handleLogout();
        });
    }

    /**
     * Handle login success
     */
    async handleLoginSuccess() {
        // Refresh user-specific data after login
        try {
            await this.loadExistingConversations();
            console.log('✅ AI RAG Core: User data refreshed after login');
        } catch (error) {
            console.error('❌ AI RAG Core: Failed to refresh user data after login:', error);
        }
    }

    /**
     * Handle logout
     */
    handleLogout() {
        // Clear user-specific data
        this.conversations.clear();
        this.currentUser = null;
        this.isAuthenticated = false;
        console.log('🔐 AI RAG Core: User data cleared after logout');
    }

    /**
     * Handle auth state change
     */
    handleAuthStateChange() {
        if (this.isAuthenticated && this.currentUser) {
            if (this.currentUser.is_demo) {
                // Show demo features prominently
                this.showDemoFeatures();
                this.showLoginPrompt();
            } else {
                // Show authenticated user features
                this.showAuthenticatedFeatures();
                this.hideLoginPrompt();
            }
        } else {
            // Show demo mode
            this.showDemoMode();
        }
    }

    /**
     * Show demo features
     */
    showDemoFeatures() {
        // Highlight impressive demo capabilities
        this.displayMessage(
            '🎉 Experience the full power of AI/RAG system! ' +
            'Create your account to save your conversations and access advanced features.'
        );
        
        // Show login/signup buttons prominently
        this.showLoginButtons();
    }

    /**
     * Show login buttons
     */
    showLoginButtons() {
        // Add login/signup buttons to the UI
        const loginButton = document.createElement('button');
        loginButton.textContent = 'Sign In to Save Your Work';
        loginButton.className = 'btn btn-primary btn-lg';
        loginButton.onclick = () => window.location.href = '/auth';
        
        const signupButton = document.createElement('button');
        signupButton.textContent = 'Create Free Account';
        signupButton.className = 'btn btn-outline-primary btn-lg';
        signupButton.onclick = () => window.location.href = '/auth?mode=signup';
        
        // Add to prominent location in UI
        this.addProminentButtons(loginButton, signupButton);
    }

    /**
     * Show authenticated features
     */
    showAuthenticatedFeatures() {
        // Hide demo prompts and show authenticated user features
        this.hideLoginPrompt();
        console.log('🔐 AI RAG Core: Showing authenticated user features');
    }

    /**
     * Show demo mode
     */
    showDemoMode() {
        // Show demo content and encourage signup
        this.showDemoFeatures();
    }

    /**
     * Hide login prompt
     */
    hideLoginPrompt() {
        // Remove login/signup buttons from UI
        const loginButtons = document.querySelectorAll('.ai-rag-login-buttons');
        loginButtons.forEach(button => button.remove());
    }

    /**
     * Add prominent buttons to UI
     */
    addProminentButtons(loginButton, signupButton) {
        // Add a container for the buttons
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'ai-rag-login-buttons';
        buttonContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background: rgba(255, 255, 255, 0.95);
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            display: flex;
            flex-direction: column;
            gap: 10px;
        `;
        
        buttonContainer.appendChild(loginButton);
        buttonContainer.appendChild(signupButton);
        
        // Add to body
        document.body.appendChild(buttonContainer);
    }

    /**
     * Display message to user
     */
    displayMessage(message) {
        console.log('💬 AI RAG Core:', message);
        // You can implement a more sophisticated message display system here
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
} 
} 