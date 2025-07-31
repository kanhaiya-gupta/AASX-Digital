/**
 * AI RAG Core Module
 * Handles core RAG functionality, document processing, and system management
 */

export default class AIRAGCore {
    constructor() {
        this.isInitialized = false;
        this.config = {
            apiBaseUrl: '/api/ai-rag',
            maxDocumentSize: 10 * 1024 * 1024, // 10MB
            supportedFormats: ['pdf', 'txt', 'docx', 'md', 'json', 'xml'],
            chunkSize: 1000,
            overlapSize: 200,
            embeddingModel: 'text-embedding-ada-002',
            maxTokens: 4000
        };
        
        this.documents = new Map();
        this.chunks = new Map();
        this.embeddings = new Map();
        this.conversations = new Map();
        this.processingQueue = [];
        this.isProcessing = false;
    }

    /**
     * Initialize the AI RAG Core
     */
    async init() {
        console.log('🔧 Initializing AI RAG Core...');
        
        try {
            // Load configuration
            await this.loadConfiguration();
            
            // Initialize document storage
            await this.initializeDocumentStorage();
            
            // Load existing documents
            await this.loadExistingDocuments();
            
            // Start processing queue
            this.startProcessingQueue();
            
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
                this.config = { ...this.config, ...serverConfig };
            }
        } catch (error) {
            console.warn('Could not load server configuration, using defaults:', error);
        }
    }

    /**
     * Initialize document storage
     */
    async initializeDocumentStorage() {
        // Initialize local storage for documents
        const storedDocs = localStorage.getItem('ai_rag_documents');
        if (storedDocs) {
            try {
                const docs = JSON.parse(storedDocs);
                docs.forEach(doc => {
                    this.documents.set(doc.id, doc);
                });
            } catch (error) {
                console.warn('Failed to load stored documents:', error);
            }
        }
    }

    /**
     * Load existing documents from server
     */
    async loadExistingDocuments() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/documents`);
            if (response.ok) {
                const documents = await response.json();
                documents.forEach(doc => {
                    this.documents.set(doc.id, doc);
                });
            }
        } catch (error) {
            console.warn('Could not load existing documents:', error);
        }
    }

    /**
     * Start processing queue
     */
    startProcessingQueue() {
        setInterval(() => {
            this.processQueue();
        }, 1000);
    }

    /**
     * Process documents in queue
     */
    async processQueue() {
        if (this.isProcessing || this.processingQueue.length === 0) {
            return;
        }

        this.isProcessing = true;
        
        try {
            const document = this.processingQueue.shift();
            await this.processDocument(document);
        } catch (error) {
            console.error('Error processing document:', error);
        } finally {
            this.isProcessing = false;
        }
    }

    /**
     * Add document to processing queue
     */
    addToProcessingQueue(document) {
        this.processingQueue.push(document);
        this.updateProcessingStatus(document.id, 'queued');
    }

    /**
     * Process a single document
     */
    async processDocument(document) {
        try {
            this.updateProcessingStatus(document.id, 'processing');
            
            // Extract text from document
            const text = await this.extractText(document);
            
            // Chunk the text
            const chunks = this.createChunks(text);
            
            // Generate embeddings
            const embeddings = await this.generateEmbeddings(chunks);
            
            // Store chunks and embeddings
            this.chunks.set(document.id, chunks);
            this.embeddings.set(document.id, embeddings);
            
            // Update document status
            this.updateDocument(document.id, {
                status: 'processed',
                chunkCount: chunks.length,
                processedAt: new Date().toISOString()
            });
            
            this.updateProcessingStatus(document.id, 'completed');
            
        } catch (error) {
            console.error('Error processing document:', error);
            this.updateProcessingStatus(document.id, 'failed', error.message);
        }
    }

    /**
     * Extract text from document
     */
    async extractText(document) {
        const formData = new FormData();
        formData.append('file', document.file);
        
        const response = await fetch(`${this.config.apiBaseUrl}/extract-text`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Failed to extract text from document');
        }
        
        const result = await response.json();
        return result.text;
    }

    /**
     * Create chunks from text
     */
    createChunks(text) {
        const chunks = [];
        let start = 0;
        
        while (start < text.length) {
            const end = Math.min(start + this.config.chunkSize, text.length);
            let chunk = text.substring(start, end);
            
            // Try to break at sentence boundaries
            if (end < text.length) {
                const lastPeriod = chunk.lastIndexOf('.');
                const lastNewline = chunk.lastIndexOf('\n');
                const breakPoint = Math.max(lastPeriod, lastNewline);
                
                if (breakPoint > start + this.config.chunkSize * 0.7) {
                    chunk = text.substring(start, breakPoint + 1);
                    start = breakPoint + 1;
                } else {
                    start = end;
                }
            } else {
                start = end;
            }
            
            chunks.push({
                id: `${document.id}_chunk_${chunks.length}`,
                text: chunk.trim(),
                start: start - chunk.length,
                end: start
            });
        }
        
        return chunks;
    }

    /**
     * Generate embeddings for chunks
     */
    async generateEmbeddings(chunks) {
        const response = await fetch(`${this.config.apiBaseUrl}/generate-embeddings`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                chunks: chunks.map(chunk => chunk.text),
                model: this.config.embeddingModel
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate embeddings');
        }
        
        const result = await response.json();
        return result.embeddings;
    }

    /**
     * Upload document
     */
    async uploadDocument(file, metadata = {}) {
        const document = {
            id: this.generateDocumentId(),
            name: file.name,
            size: file.size,
            type: file.type,
            uploadedAt: new Date().toISOString(),
            status: 'uploaded',
            metadata: metadata,
            file: file
        };
        
        // Validate file
        if (!this.validateFile(file)) {
            throw new Error('Invalid file format or size');
        }
        
        // Add to documents
        this.documents.set(document.id, document);
        
        // Add to processing queue
        this.addToProcessingQueue(document);
        
        // Save to server
        await this.saveDocumentToServer(document);
        
        // Save to local storage
        this.saveToLocalStorage();
        
        return document;
    }

    /**
     * Validate file
     */
    validateFile(file) {
        const extension = file.name.split('.').pop().toLowerCase();
        const isValidFormat = this.config.supportedFormats.includes(extension);
        const isValidSize = file.size <= this.config.maxDocumentSize;
        
        return isValidFormat && isValidSize;
    }

    /**
     * Generate document ID
     */
    generateDocumentId() {
        return `doc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Save document to server
     */
    async saveDocumentToServer(document) {
        const formData = new FormData();
        formData.append('file', document.file);
        formData.append('metadata', JSON.stringify(document.metadata));
        
        const response = await fetch(`${this.config.apiBaseUrl}/documents`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Failed to save document to server');
        }
    }

    /**
     * Save to local storage
     */
    saveToLocalStorage() {
        const docsArray = Array.from(this.documents.values());
        localStorage.setItem('ai_rag_documents', JSON.stringify(docsArray));
    }

    /**
     * Update document
     */
    updateDocument(id, updates) {
        const document = this.documents.get(id);
        if (document) {
            Object.assign(document, updates);
            this.documents.set(id, document);
            this.saveToLocalStorage();
        }
    }

    /**
     * Update processing status
     */
    updateProcessingStatus(id, status, error = null) {
        this.updateDocument(id, {
            status: status,
            error: error,
            lastUpdated: new Date().toISOString()
        });
        
        // Dispatch event
        window.dispatchEvent(new CustomEvent('aiRAGDocumentStatusUpdate', {
            detail: { id, status, error }
        }));
    }

    /**
     * Delete document
     */
    async deleteDocument(id) {
        try {
            // Delete from server
            const response = await fetch(`${this.config.apiBaseUrl}/documents/${id}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error('Failed to delete document from server');
            }
            
            // Remove from local storage
            this.documents.delete(id);
            this.chunks.delete(id);
            this.embeddings.delete(id);
            
            this.saveToLocalStorage();
            
            return true;
            
        } catch (error) {
            console.error('Error deleting document:', error);
            throw error;
        }
    }

    /**
     * Get document by ID
     */
    getDocument(id) {
        return this.documents.get(id);
    }

    /**
     * Get all documents
     */
    getAllDocuments() {
        return Array.from(this.documents.values());
    }

    /**
     * Get documents by status
     */
    getDocumentsByStatus(status) {
        return Array.from(this.documents.values()).filter(doc => doc.status === status);
    }

    /**
     * Search documents
     */
    searchDocuments(query) {
        return Array.from(this.documents.values()).filter(doc => 
            doc.name.toLowerCase().includes(query.toLowerCase()) ||
            (doc.metadata && doc.metadata.description && 
             doc.metadata.description.toLowerCase().includes(query.toLowerCase()))
        );
    }

    /**
     * Create conversation
     */
    createConversation(title = 'New Conversation') {
        const conversation = {
            id: this.generateConversationId(),
            title: title,
            createdAt: new Date().toISOString(),
            messages: [],
            documents: []
        };
        
        this.conversations.set(conversation.id, conversation);
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
            message.id = this.generateMessageId();
            message.timestamp = new Date().toISOString();
            conversation.messages.push(message);
        }
    }

    /**
     * Generate message ID
     */
    generateMessageId() {
        return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Get conversation
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
    }

    /**
     * Refresh data
     */
    async refreshData() {
        await this.loadExistingDocuments();
        console.log('🔄 AI RAG Core data refreshed');
    }

    /**
     * Get system statistics
     */
    getStatistics() {
        const totalDocuments = this.documents.size;
        const processedDocuments = this.getDocumentsByStatus('processed').length;
        const processingDocuments = this.getDocumentsByStatus('processing').length;
        const failedDocuments = this.getDocumentsByStatus('failed').length;
        const totalConversations = this.conversations.size;
        
        return {
            totalDocuments,
            processedDocuments,
            processingDocuments,
            failedDocuments,
            totalConversations,
            queueLength: this.processingQueue.length,
            isProcessing: this.isProcessing
        };
    }

    /**
     * Destroy the core module
     */
    destroy() {
        this.isProcessing = false;
        this.processingQueue = [];
        this.documents.clear();
        this.chunks.clear();
        this.embeddings.clear();
        this.conversations.clear();
        this.isInitialized = false;
        
        console.log('🧹 AI RAG Core destroyed');
    }
} 