/**
 * AI/RAG System Frontend JavaScript
 * Handles AI/RAG system interactions and UI updates
 */

class AIRAGSystem {
    constructor() {
        this.apiClient = new APIClient();
        this.uiHelper = new UIHelper(this.apiClient);
        this.init();
    }

    // Shared formatting function for responses
    formatResponseText(text) {
        if (!text) return 'No analysis available';
        
        // Convert markdown-style formatting to HTML
        return text
            // Convert ### headers to h3 (do this first to avoid conflicts)
            .replace(/###\s+(.*?)(?=\n|$)/g, '<h3 class="mt-3 mb-2">$1</h3>')
            // Convert ## headers to h4
            .replace(/##\s+(.*?)(?=\n|$)/g, '<h4 class="mt-3 mb-2">$1</h4>')
            // Convert # headers to h5
            .replace(/^#\s+(.*?)(?=\n|$)/gm, '<h5 class="mt-3 mb-2">$1</h5>')
            // Convert **bold** to <strong>bold</strong>
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Convert *italic* to <em>italic</em> (but not if it's part of a list)
            .replace(/(?<!-)\*(.*?)\*(?!-)/g, '<em>$1</em>')
            // Convert line breaks to <br> tags
            .replace(/\n/g, '<br>')
            // Convert double line breaks to paragraph breaks
            .replace(/<br><br>/g, '</p><p>')
            // Wrap in paragraph tags
            .replace(/^(.+)$/, '<p>$1</p>')
            // Clean up empty paragraphs
            .replace(/<p><\/p>/g, '')
            .replace(/<p><br><\/p>/g, '')
            // Clean up any remaining double <br> tags
            .replace(/<br><br>/g, '<br>');
    }

    async init() {
        console.log('🤖 Initializing AI/RAG System...');
        
        // Hide loading spinner initially
        this.showQueryLoading(false);
        
        // Load initial data
        await this.loadSystemStatus();
        await this.loadSystemStats();
        await this.loadCollections();
        
        // Setup event listeners
        this.setupEventListeners();
        
        console.log('✅ AI/RAG System initialized');
    }

    setupEventListeners() {
        // Query submission
        const submitBtn = document.getElementById('submit-query');
        if (submitBtn) {
            submitBtn.addEventListener('click', () => this.submitQuery());
        }

        // Individual demo query buttons
        const demoQueryBtns = document.querySelectorAll('.demo-query-btn');
        demoQueryBtns.forEach(btn => {
            if (btn.id !== 'run-all-demos') { // Skip the "Run All Demos" button
                btn.addEventListener('click', () => this.runSingleDemoQuery(btn));
            }
        });

        // Run all demos button
        const runAllDemosBtn = document.getElementById('run-all-demos');
        if (runAllDemosBtn) {
            runAllDemosBtn.addEventListener('click', () => this.runAllDemoQueries());
        }

        // Analysis type changes
        const analysisTypeSelect = document.getElementById('analysis-type');
        if (analysisTypeSelect) {
            analysisTypeSelect.addEventListener('change', () => this.onAnalysisTypeChange());
        }

        // Collection changes
        const collectionSelect = document.getElementById('collection-select');
        if (collectionSelect) {
            collectionSelect.addEventListener('change', () => this.onCollectionChange());
        }

        // Index data button
        const indexDataBtn = document.getElementById('index-data');
        if (indexDataBtn) {
            indexDataBtn.addEventListener('click', () => this.indexData());
        }

        // Clear response button
        const clearBtn = document.getElementById('clear-response');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearResponse());
        }
    }

    async submitQuery() {
        const queryInput = document.getElementById('query-input');
        const analysisTypeSelect = document.getElementById('analysis-type');
        const collectionSelect = document.getElementById('collection-select');
        
        if (!queryInput || !queryInput.value.trim()) {
            this.uiHelper.showError('Please enter a query');
            return;
        }

        const query = queryInput.value.trim();
        const analysisType = analysisTypeSelect ? analysisTypeSelect.value : 'general';
        const collection = collectionSelect ? collectionSelect.value : 'aasx_assets';

        this.showQueryLoading(true);
        this.hideResponse();

        try {
            console.log(`🔍 Submitting query: ${query} (${analysisType})`);
            
            const response = await this.apiClient.queryAIRAG(query, analysisType, collection);
            
            console.log('✅ Query response received:', response);
            this.displayResponse(response);
            
        } catch (error) {
            console.error('❌ Query failed:', error);
            this.uiHelper.showError(`Query failed: ${error.message}`);
        } finally {
            this.showQueryLoading(false);
        }
    }

    async runSingleDemoQuery(button) {
        const query = button.getAttribute('data-query');
        if (!query) {
            this.uiHelper.showError('No query found for this demo');
            return;
        }

        // Set the query in the input field
        const queryInput = document.getElementById('query-input');
        if (queryInput) {
            queryInput.value = query;
        }

        // Submit the query
        await this.submitQuery();
    }

    async runAllDemoQueries() {
        const runAllBtn = document.getElementById('run-all-demos');
        if (runAllBtn) {
            runAllBtn.disabled = true;
            runAllBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Running All Demos...';
        }

        this.hideResponse();

        try {
            console.log('🚀 Running all demo queries...');
            
            // Get all demo queries
            const demoButtons = document.querySelectorAll('.demo-query-btn');
            const queries = [];
            
            for (const btn of demoButtons) {
                if (btn.id !== 'run-all-demos') {
                    const query = btn.getAttribute('data-query');
                    if (query) {
                        queries.push(query);
                    }
                }
            }

            console.log('📝 Demo queries to run:', queries);
            
            // Run each query
            const results = [];
            for (const query of queries) {
                try {
                    console.log(`🔍 Running demo query: ${query}`);
                    const response = await this.apiClient.queryAIRAG(query, 'general', 'aasx_assets');
                    results.push({
                        query: query,
                        response: response,
                        error: null
                    });
                } catch (error) {
                    console.error(`❌ Demo query failed: ${query}`, error);
                    results.push({
                        query: query,
                        response: null,
                        error: error.message
                    });
                }
            }
            
            console.log('✅ All demo results received:', results);
            this.displayDemoResults(results);
            
        } catch (error) {
            console.error('❌ Running all demos failed:', error);
            this.uiHelper.showError(`Running all demos failed: ${error.message}`);
        } finally {
            if (runAllBtn) {
                runAllBtn.disabled = false;
                runAllBtn.innerHTML = '<i class="fas fa-rocket me-2"></i>Run All Demos';
            }
        }
    }

    async loadSystemStatus() {
        try {
            console.log('🔍 Loading system status...');
            
            const status = await this.apiClient.checkAllServices();
            
            console.log('✅ System status received:', status);
            console.log('🔍 Knowledge Graph status:', status.kg);
            console.log('🔍 Knowledge Graph neo4j_status:', status.kg?.neo4j_status);
            console.log('🔍 ETL status:', status.etl);
            console.log('🔍 AI/RAG status:', status.ai_rag);
            
            // Update status indicators
            console.log('🔍 Updating Qdrant status:', status.ai_rag?.qdrant_status);
            console.log('🔍 Updating Neo4j status:', status.kg?.neo4j_status);
            console.log('🔍 Updating OpenAI status:', status.ai_rag?.openai_status);
            console.log('🔍 Updating ETL status:', status.etl?.status);
            console.log('🔍 Updating System status:', status.system?.status);
            
            this.updateStatusIndicator('qdrant', status.ai_rag?.qdrant_status || 'error');
            this.updateStatusIndicator('qdrant-client', status.ai_rag?.qdrant_status || 'error'); // Qdrant client uses same status
            this.updateStatusIndicator('neo4j', status.kg?.neo4j_status || 'error');
            this.updateStatusIndicator('openai', status.ai_rag?.openai_status || 'error');
            this.updateStatusIndicator('etl', status.etl?.status || 'error');
            this.updateStatusIndicator('system', status.system?.status || 'error');
            
        } catch (error) {
            console.error('❌ Failed to load system status:', error);
            this.updateStatusIndicator('qdrant', 'error');
            this.updateStatusIndicator('qdrant-client', 'error');
            this.updateStatusIndicator('neo4j', 'error');
            this.updateStatusIndicator('openai', 'error');
            this.updateStatusIndicator('etl', 'error');
            this.updateStatusIndicator('system', 'error');
        }
    }

    async loadSystemStats() {
        try {
            console.log('📊 Loading system stats...');
            
            const stats = await this.apiClient.getAIRAGStats();
            
            console.log('✅ System stats received:', stats);
            this.displaySystemStats(stats);
            
        } catch (error) {
            console.error('❌ Failed to load system stats:', error);
            const container = document.getElementById('system-stats');
            if (container) {
                container.innerHTML = '<div class="text-danger">Failed to load statistics</div>';
            }
        }
    }

    async loadCollections() {
        try {
            console.log('🗂️ Loading collections...');
            
            const collections = await this.apiClient.getCollections();
            
            console.log('✅ Collections received:', collections);
            this.displayCollections(collections);
            
        } catch (error) {
            console.error('❌ Failed to load collections:', error);
            const container = document.getElementById('collections-info');
            if (container) {
                container.innerHTML = '<div class="text-danger">Failed to load collections</div>';
            }
        }
    }

    async indexData() {
        const indexBtn = document.getElementById('index-data');
        if (indexBtn) {
            indexBtn.disabled = true;
            indexBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Indexing...';
        }

        try {
            console.log('📝 Indexing ETL data...');
            
            const result = await this.apiClient.indexETLData();
            
            console.log('✅ Indexing completed:', result);
            this.uiHelper.showSuccess('Data indexing completed successfully');
            
            // Reload stats after indexing
            await this.loadSystemStats();
            await this.loadCollections();
            
        } catch (error) {
            console.error('❌ Indexing failed:', error);
            this.uiHelper.showError(`Indexing failed: ${error.message}`);
        } finally {
            if (indexBtn) {
                indexBtn.disabled = false;
                indexBtn.innerHTML = '<i class="fas fa-upload me-2"></i>Index Data';
            }
        }
    }

    updateStatusIndicator(service, status) {
        const indicator = document.getElementById(`status-${service}`);
        console.log(`🔍 Updating ${service} indicator:`, indicator, 'with status:', status);
        if (indicator) {
            const isHealthy = status === 'healthy' || status === 'connected' || status === 'configured' || status === 'available';
            console.log(`🔍 ${service} isHealthy:`, isHealthy);
            indicator.className = `badge ${isHealthy ? 'bg-success' : 'bg-danger'}`;
            indicator.textContent = isHealthy ? 'Connected' : 'Error';
            console.log(`✅ ${service} indicator updated to:`, indicator.textContent);
        } else {
            console.error(`❌ ${service} indicator element not found`);
        }
    }

    displaySystemStats(stats) {
        const container = document.getElementById('system-stats');
        if (!container) return;
        
        let html = `
            <div class="row text-center">
                <div class="col-6 mb-3">
                    <div class="border rounded p-2">
                        <h6 class="text-primary">Collections</h6>
                        <h4>${stats.collections_count || 0}</h4>
                    </div>
                </div>
                <div class="col-6 mb-3">
                    <div class="border rounded p-2">
                        <h6 class="text-success">Total Points</h6>
                        <h4>${stats.total_points || 0}</h4>
                    </div>
                </div>
                <div class="col-6 mb-3">
                    <div class="border rounded p-2">
                        <h6 class="text-info">Assets</h6>
                        <h4>${stats.assets_count || 0}</h4>
                    </div>
                </div>
                <div class="col-6 mb-3">
                    <div class="border rounded p-2">
                        <h6 class="text-warning">Submodels</h6>
                        <h4>${stats.submodels_count || 0}</h4>
                    </div>
                </div>
            </div>
        `;

        if (stats.last_indexed) {
            html += `
                <div class="mt-3">
                    <small class="text-muted">
                        <i class="fas fa-clock me-1"></i>
                        Last indexed: ${new Date(stats.last_indexed).toLocaleString()}
                    </small>
                </div>
            `;
        }

        container.innerHTML = html;
    }

    displayCollections(collections) {
        const container = document.getElementById('collections-info');
        if (!container) return;
        
        if (!collections || collections.length === 0) {
            container.innerHTML = '<div class="text-muted">No collections available</div>';
            return;
        }

        let html = '';
        collections.forEach(collection => {
            html += `
                <div class="collection-badge">
                    <i class="fas fa-database me-1"></i>
                    ${collection.name}
                    <span class="badge bg-light text-dark ms-1">${collection.points_count || 0}</span>
                </div>
            `;
        });

        container.innerHTML = html;
    }

    displayResponse(response) {
        const responseSection = document.getElementById('response-section');
        const responseContent = document.getElementById('response-content');
        
        if (!responseSection || !responseContent) return;

        const formattedResponse = this.formatResponseText(response.analysis || response.response);

        let html = `
            <div class="response-content">
                <h5 class="text-primary mb-3">
                    <i class="fas fa-robot me-2"></i>
                    AI Analysis
                </h5>
                <div class="mb-3">
                    <strong>Query:</strong> ${response.query || 'N/A'}
                </div>
                <div class="mb-3">
                    <strong>Analysis Type:</strong> ${response.analysis_type || 'General'}
                </div>
                <div class="mb-3">
                    <strong>Response:</strong>
                    <div class="mt-2 response-text">${formattedResponse}</div>
                </div>
        `;

        if (response.sources && response.sources.length > 0) {
            html += `
                <div class="mb-3">
                    <strong>Sources:</strong>
                    <ul class="mt-2">
                        ${response.sources.map(source => `<li>${source}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if (response.confidence) {
            html += `
                <div class="mb-3">
                    <strong>Confidence:</strong>
                    <div class="progress">
                        <div class="progress-bar" role="progressbar" style="width: ${response.confidence * 100}%">
                            ${Math.round(response.confidence * 100)}%
                        </div>
                    </div>
                </div>
            `;
        }

        if (response.model) {
            html += `
                <div class="mb-3">
                    <strong>Model:</strong> ${response.model}
                </div>
            `;
        }

        html += '</div>';
        responseContent.innerHTML = html;
        responseSection.style.display = 'block';
    }

    displayDemoResults(results) {
        const responseSection = document.getElementById('response-section');
        const responseContent = document.getElementById('response-content');
        
        if (!responseSection || !responseContent) return;

        let html = `
            <div class="response-content">
                <h5 class="text-primary mb-3">
                    <i class="fas fa-rocket me-2"></i>
                    Demo Results (${results.length} queries)
                </h5>
        `;

        results.forEach((result, index) => {
            const responseText = result.error ? 
                `<div class="text-danger">Error: ${result.error}</div>` :
                `<div class="response-text">${this.formatResponseText(result.response?.analysis || result.response?.response || 'No response')}</div>`;
            
            html += `
                <div class="card mb-3">
                    <div class="card-header bg-light">
                        <strong>Query ${index + 1}:</strong> ${result.query}
                    </div>
                    <div class="card-body">
                        ${responseText}
                    </div>
                </div>
            `;
        });

        html += '</div>';
        responseContent.innerHTML = html;
        responseSection.style.display = 'block';
    }

    showQueryLoading(show) {
        const loading = document.getElementById('query-loading');
        const submitBtn = document.getElementById('submit-query');
        
        if (show) {
            if (loading) loading.style.display = 'block';
            if (submitBtn) submitBtn.disabled = true;
        } else {
            if (loading) loading.style.display = 'none';
            if (submitBtn) submitBtn.disabled = false;
        }
    }

    hideResponse() {
        const responseSection = document.getElementById('response-section');
        if (responseSection) {
            responseSection.style.display = 'none';
        }
    }

    clearResponse() {
        const queryInput = document.getElementById('query-input');
        if (queryInput) {
            queryInput.value = '';
        }
        this.hideResponse();
    }

    onAnalysisTypeChange() {
        // Could add logic to update query suggestions based on analysis type
        console.log('Analysis type changed');
    }

    onCollectionChange() {
        // Could add logic to update available data based on collection
        console.log('Collection changed');
    }
}

// Initialize the AI/RAG system when the page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Initializing AI/RAG System...');
    new AIRAGSystem();
}); 