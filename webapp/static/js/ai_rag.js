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
        
        // Initialize technique information
        this.techniqueInfo = {
            basic: {
                title: 'Basic RAG',
                description: 'Simple retrieval + generation approach using vector search and LLM',
                bestFor: 'Simple queries, quick responses, baseline performance comparison',
                performance: 'Fastest, lowest resource usage',
                icon: 'fas fa-rocket',
                color: 'success',
                speed: 'Fast',
                memory: 'Low',
                complexity: 'Simple',
                features: ['Standard vector similarity search', 'Simple context combination', 'Basic prompt engineering', 'Minimal configuration required']
            },
            hybrid: {
                title: 'Hybrid RAG',
                description: 'Dense + sparse retrieval approach using vector search and keyword matching',
                bestFor: 'Queries with specific keywords, mixed semantic and exact matching needs',
                performance: 'Moderate performance, better results',
                icon: 'fas fa-layer-group',
                color: 'info',
                speed: 'Medium',
                memory: 'Medium',
                complexity: 'Moderate',
                features: ['Combines dense vector search with sparse keyword search', 'Weighted scoring of results', 'Deduplication of results', 'Enhanced relevance through multiple retrieval methods']
            },
            multi_step: {
                title: 'Multi-Step RAG',
                description: 'Iterative refinement approach with multiple retrieval and generation steps',
                bestFor: 'Complex queries requiring deep analysis, research-style questions',
                performance: 'Slower, more thorough analysis',
                icon: 'fas fa-route',
                color: 'warning',
                speed: 'Slow',
                memory: 'High',
                complexity: 'Complex',
                features: ['Multi-step query refinement', 'Iterative context retrieval', 'Query evolution based on intermediate results', 'Step-by-step analysis']
            },
            graph: {
                title: 'Graph RAG',
                description: 'Knowledge graph integration approach using graph queries and relationships',
                bestFor: 'Queries about relationships and connections, structural analysis questions',
                performance: 'Depends on graph size and complexity',
                icon: 'fas fa-project-diagram',
                color: 'primary',
                speed: 'Variable',
                memory: 'Medium',
                complexity: 'Moderate',
                features: ['Graph-based context retrieval', 'Relationship-aware search', 'Structural insights from knowledge graph', 'Enhanced understanding of entity connections']
            },
            advanced: {
                title: 'Advanced RAG',
                description: 'Multi-modal + reasoning approach with advanced context processing',
                bestFor: 'Complex, multi-faceted queries, comprehensive analysis requirements',
                performance: 'Most resource-intensive, most comprehensive',
                icon: 'fas fa-brain',
                color: 'danger',
                speed: 'Slowest',
                memory: 'Highest',
                complexity: 'Very Complex',
                features: ['Multi-modal context combination', 'Advanced filtering and reranking', 'Sophisticated reasoning capabilities', 'Metadata analysis and insights']
            }
        };
        
        // Load initial data
        await this.loadSystemStatus();
        await this.loadSystemStats();
        await this.loadCollections();
        await this.loadRAGTechniques();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Initialize technique display
        this.updateTechniqueInfo('basic');
        
        console.log('✅ AI/RAG System initialized');
    }
    
    async loadRAGTechniques() {
        try {
            console.log('🔧 Loading RAG techniques...');
            const response = await this.apiClient.getRAGTechniques();
            
            if (response.techniques) {
                // Store techniques for later use
                this.availableTechniques = response.techniques;
                console.log(`✅ Loaded ${response.techniques.length} RAG techniques`);
                
                // Update technique selection UI if available
                this.updateTechniqueSelection();
            }
        } catch (error) {
            console.error('❌ Failed to load RAG techniques:', error);
        }
    }
    
    updateTechniqueSelection() {
        const techniqueContainer = document.getElementById('rag-techniques-container');
        if (!techniqueContainer || !this.availableTechniques) return;
        
        techniqueContainer.innerHTML = '';
        
        this.availableTechniques.forEach(technique => {
            const div = document.createElement('div');
            div.className = 'form-check';
            div.innerHTML = `
                <input class="form-check-input" type="radio" name="rag-technique" 
                       id="technique-${technique.id}" value="${technique.id}" 
                       ${technique.id === 'basic' ? 'checked' : ''}>
                <label class="form-check-label" for="technique-${technique.id}">
                    <strong>${technique.name}</strong>
                    <small class="text-muted d-block">${technique.description}</small>
                </label>
            `;
            techniqueContainer.appendChild(div);
        });
    }
    
    async getTechniqueRecommendations(query) {
        try {
            const response = await this.apiClient.getTechniqueRecommendations(query);
            return response.recommendations || [];
        } catch (error) {
            console.error('Failed to get technique recommendations:', error);
            return [];
        }
    }
    
    async executeRAGTechnique(query, techniqueId, parameters = {}) {
        try {
            const response = await this.apiClient.executeRAGTechnique(query, techniqueId, parameters);
            return response;
        } catch (error) {
            console.error('Failed to execute RAG technique:', error);
            throw error;
        }
    }
    
    async compareRAGTechniques(query, techniqueIds = null, parameters = {}) {
        try {
            const response = await this.apiClient.compareRAGTechniques(query, techniqueIds, parameters);
            return response;
        } catch (error) {
            console.error('Failed to compare RAG techniques:', error);
            throw error;
        }
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

        // RAG technique changes
        const ragTechniqueRadios = document.querySelectorAll('input[name="rag-technique"]');
        ragTechniqueRadios.forEach(radio => {
            radio.addEventListener('change', () => this.onRAGTechniqueChange());
        });

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
        const analysisTypeSelect = document.querySelector('input[name="analysis-type"]:checked');
        const collectionSelect = document.getElementById('collection-select');
        const llmModelSelect = document.getElementById('llm-model-select');
        const ragTechniqueSelect = document.querySelector('input[name="rag-technique"]:checked');
        
        if (!queryInput || !queryInput.value.trim()) {
            this.uiHelper.showError('Please enter a query');
            return;
        }

        const query = queryInput.value.trim();
        const analysisType = analysisTypeSelect ? analysisTypeSelect.value : 'general';
        const collection = collectionSelect ? collectionSelect.value : 'aasx_assets';
        const llmModel = llmModelSelect ? llmModelSelect.value : 'gpt-3.5-turbo';
        const ragTechnique = ragTechniqueSelect ? ragTechniqueSelect.value : 'basic';
        
        // Get RAG configuration
        const topK = document.getElementById('top-k-select')?.value || '5';
        const similarityThreshold = document.getElementById('similarity-threshold')?.value || '0.7';
        
        // Technique-specific parameters
        const ragParams = {
            top_k: parseInt(topK),
            similarity_threshold: parseFloat(similarityThreshold)
        };
        
        // Add technique-specific parameters
        switch (ragTechnique) {
            case 'hybrid':
                const denseWeight = document.getElementById('dense-weight')?.value || '0.7';
                const sparseWeight = document.getElementById('sparse-weight')?.value || '0.3';
                ragParams.dense_weight = parseFloat(denseWeight);
                ragParams.sparse_weight = parseFloat(sparseWeight);
                break;
                
            case 'multi_step':
                const maxSteps = document.getElementById('max-steps')?.value || '3';
                const refinementTemp = document.getElementById('refinement-temp')?.value || '0.3';
                ragParams.max_steps = parseInt(maxSteps);
                ragParams.refinement_temperature = parseFloat(refinementTemp);
                break;
                
            case 'graph':
                const graphQueryType = document.getElementById('graph-query-type')?.value || 'auto';
                const maxGraphResults = document.getElementById('max-graph-results')?.value || '10';
                ragParams.graph_query_type = graphQueryType;
                ragParams.max_graph_results = parseInt(maxGraphResults);
                break;
                
            case 'advanced':
                const enableReranking = document.getElementById('enable-reranking')?.checked || false;
                const enableGraphContext = document.getElementById('enable-graph-context')?.checked || false;
                const enableMetadataFiltering = document.getElementById('enable-metadata-filtering')?.checked || false;
                const reasoningMode = document.getElementById('reasoning-mode')?.value || 'standard';
                ragParams.enable_reranking = enableReranking;
                ragParams.enable_graph_context = enableGraphContext;
                ragParams.enable_metadata_filtering = enableMetadataFiltering;
                ragParams.reasoning_mode = reasoningMode;
                break;
        }

        this.showQueryLoading(true);
        this.hideResponse();

        try {
            console.log(`🔍 Submitting query: ${query} (${analysisType}) with ${llmModel} and ${ragTechnique} technique`);
            
            const response = await this.apiClient.queryAIRAG(
                query, 
                analysisType, 
                collection,
                {
                    llm_model: llmModel,
                    rag_technique: ragTechnique,
                    ...ragParams
                }
            );
            
            console.log('✅ Query response received:', response);
            console.log('🔍 Response keys:', Object.keys(response));
            console.log('🔍 Technique info:', {
                technique_name: response.technique_name,
                rag_technique: response.rag_technique,
                technique: response.technique
            });
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
            this.updateStatusIndicator('neo4j', status.kg?.success ? 'connected' : 'error');
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
                    <strong>RAG Technique:</strong> 
                    <span class="badge bg-success">${response.technique_name || response.rag_technique || 'Basic RAG'}</span>
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
    
    onRAGTechniqueChange() {
        const selectedTechnique = document.querySelector('input[name="rag-technique"]:checked');
        if (selectedTechnique) {
            const techniqueId = selectedTechnique.value;
            this.updateTechniqueInfo(techniqueId);
        }
    }
    
    updateTechniqueInfo(techniqueId) {
        const info = this.techniqueInfo[techniqueId];
        if (!info) return;
        
        // Update title
        const titleElement = document.getElementById('technique-title');
        if (titleElement) {
            titleElement.textContent = info.title;
        }
        
        // Update card header color
        const cardHeader = document.querySelector('#rag-technique-info .card-header');
        if (cardHeader) {
            cardHeader.className = `card-header bg-${info.color} text-white`;
        }
        
        // Update description
        const descriptionElement = document.getElementById('technique-description');
        if (descriptionElement) {
            descriptionElement.innerHTML = `
                <p class="mb-2"><strong>Description:</strong> ${info.description}</p>
                <p class="mb-2"><strong>Best For:</strong> ${info.bestFor}</p>
                <p class="mb-2"><strong>Performance:</strong> ${info.performance}</p>
                <div class="mt-3">
                    <strong>Key Features:</strong>
                    <ul class="list-unstyled mt-1">
                        ${info.features.map(feature => `<li><i class="fas fa-check text-${info.color} me-2"></i>${feature}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        // Update icon
        const iconElement = document.querySelector('.technique-icon i');
        if (iconElement) {
            iconElement.className = `${info.icon} fa-2x text-${info.color}`;
        }
        
        // Update stats
        const statsElement = document.querySelector('.technique-stats');
        if (statsElement) {
            statsElement.innerHTML = `
                <small class="text-muted">
                    <div><i class="fas fa-tachometer-alt me-1"></i>Speed: ${info.speed}</div>
                    <div><i class="fas fa-memory me-1"></i>Memory: ${info.memory}</div>
                    <div><i class="fas fa-brain me-1"></i>Complexity: ${info.complexity}</div>
                </small>
            `;
        }
        
        // Update configuration options based on technique
        this.updateTechniqueConfiguration(techniqueId);
    }
    
    updateTechniqueConfiguration(techniqueId) {
        const configElement = document.getElementById('technique-config');
        if (!configElement) return;
        
        let configHTML = '<h6><i class="fas fa-cog me-2"></i>Configuration Options</h6>';
        
        // Common options
        configHTML += `
            <div class="row">
                <div class="col-md-6">
                    <label class="form-label">Top K Results:</label>
                    <select class="form-select form-select-sm" id="top-k-select">
                        <option value="3">3 results</option>
                        <option value="5" selected>5 results</option>
                        <option value="10">10 results</option>
                        <option value="15">15 results</option>
                    </select>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Similarity Threshold:</label>
                    <select class="form-select form-select-sm" id="similarity-threshold">
                        <option value="0.5">0.5 (Loose)</option>
                        <option value="0.7" selected>0.7 (Balanced)</option>
                        <option value="0.8">0.8 (Strict)</option>
                        <option value="0.9">0.9 (Very Strict)</option>
                    </select>
                </div>
            </div>
        `;
        
        // Technique-specific options
        switch (techniqueId) {
            case 'hybrid':
                configHTML += `
                    <div class="row mt-2">
                        <div class="col-md-6">
                            <label class="form-label">Dense Weight:</label>
                            <select class="form-select form-select-sm" id="dense-weight">
                                <option value="0.6">0.6</option>
                                <option value="0.7" selected>0.7</option>
                                <option value="0.8">0.8</option>
                                <option value="0.9">0.9</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Sparse Weight:</label>
                            <select class="form-select form-select-sm" id="sparse-weight">
                                <option value="0.1">0.1</option>
                                <option value="0.2">0.2</option>
                                <option value="0.3" selected>0.3</option>
                                <option value="0.4">0.4</option>
                            </select>
                        </div>
                    </div>
                `;
                break;
                
            case 'multi_step':
                configHTML += `
                    <div class="row mt-2">
                        <div class="col-md-6">
                            <label class="form-label">Max Steps:</label>
                            <select class="form-select form-select-sm" id="max-steps">
                                <option value="2">2 steps</option>
                                <option value="3" selected>3 steps</option>
                                <option value="4">4 steps</option>
                                <option value="5">5 steps</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Refinement Temperature:</label>
                            <select class="form-select form-select-sm" id="refinement-temp">
                                <option value="0.1">0.1 (Conservative)</option>
                                <option value="0.3" selected>0.3 (Balanced)</option>
                                <option value="0.5">0.5 (Creative)</option>
                                <option value="0.7">0.7 (Very Creative)</option>
                            </select>
                        </div>
                    </div>
                `;
                break;
                
            case 'graph':
                configHTML += `
                    <div class="row mt-2">
                        <div class="col-md-6">
                            <label class="form-label">Graph Query Type:</label>
                            <select class="form-select form-select-sm" id="graph-query-type">
                                <option value="auto" selected>Auto-detect</option>
                                <option value="entity">Entity-focused</option>
                                <option value="relationship">Relationship-focused</option>
                                <option value="hierarchical">Hierarchical</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Max Graph Results:</label>
                            <select class="form-select form-select-sm" id="max-graph-results">
                                <option value="5">5 results</option>
                                <option value="10" selected>10 results</option>
                                <option value="15">15 results</option>
                                <option value="20">20 results</option>
                            </select>
                        </div>
                    </div>
                `;
                break;
                
            case 'advanced':
                configHTML += `
                    <div class="row mt-2">
                        <div class="col-md-6">
                            <label class="form-label">Enable Reranking:</label>
                            <div class="form-check form-switch">
                                <input class="form-check-input" type="checkbox" id="enable-reranking" checked>
                                <label class="form-check-label" for="enable-reranking">Use advanced reranking</label>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Enable Metadata Filtering:</label>
                            <div class="form-check form-switch">
                                <input class="form-check-input" type="checkbox" id="enable-metadata-filtering">
                                <label class="form-check-label" for="enable-metadata-filtering">Filter by metadata</label>
                            </div>
                        </div>
                    </div>
                    <div class="row mt-2">
                        <div class="col-md-6">
                            <label class="form-label">Enable Graph Context:</label>
                            <div class="form-check form-switch">
                                <input class="form-check-input" type="checkbox" id="enable-graph-context" checked>
                                <label class="form-check-label" for="enable-graph-context">Include graph data</label>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Reasoning Mode:</label>
                            <select class="form-select form-select-sm" id="reasoning-mode">
                                <option value="standard" selected>Standard</option>
                                <option value="enhanced">Enhanced</option>
                                <option value="comprehensive">Comprehensive</option>
                            </select>
                        </div>
                    </div>
                `;
                break;
        }
        
        configElement.innerHTML = configHTML;
    }
}

// Initialize the AI/RAG system when the page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Initializing AI/RAG System...');
    new AIRAGSystem();
}); 