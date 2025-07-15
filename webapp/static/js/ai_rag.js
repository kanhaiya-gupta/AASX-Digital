// AI/RAG System JavaScript
console.log('🤖 Initializing AI/RAG System...');

// Global variables
let currentTechnique = 'basic';
let currentModel = 'gpt-3.5-turbo';
let currentAnalysisType = 'general';

// Initialize the system
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initializing AI/RAG System...');
    
    // Initialize system status
    initializeSystemStatus();
    
    // Initialize RAG techniques
    initializeRAGTechniques();
    
    // Set up event listeners
    setupEventListeners();
    
    // Load initial data
    loadSystemStats();
    loadCollections();
    
    console.log('✅ AI/RAG System initialized');
});

// Initialize system status
function initializeSystemStatus() {
    console.log('🔍 Loading system status...');
    
    // Check all services
    Promise.all([
        checkService('ai_rag'),
        checkService('etl'),
        checkService('kg'),
        checkService('twin'),
        checkService('system')
    ]).then(results => {
        console.log('🔍 All services results:', results);
        
        const statusData = {
            ai_rag: results[0],
            etl: results[1],
            kg: results[2],
            twin: results[3],
            system: results[4]
        };
        
        console.log('✅ System status received:', statusData);
        
        // Update status indicators
        updateStatusIndicators(statusData);
    }).catch(error => {
        console.error('❌ Error loading system status:', error);
    });
}

// Check individual service
function checkService(service) {
    return fetch(`/api/${service}/status`)
        .then(response => response.json())
        .catch(error => {
            console.error(`Error checking ${service} service:`, error);
            return { status: 'error', error: error.message };
        });
}

// Update status indicators
function updateStatusIndicators(statusData) {
    console.log('🔍 Knowledge Graph status:', statusData.kg);
    console.log('🔍 Knowledge Graph neo4j_status:', statusData.kg.neo4j_status);
    console.log('🔍 ETL status:', statusData.etl);
    console.log('🔍 AI/RAG status:', statusData.ai_rag);
    
    // Update Qdrant status
    const qdrantStatus = statusData.ai_rag.qdrant_status || 'connected';
    updateStatusIndicator('qdrant', qdrantStatus);
    
    // Update Qdrant client status
    updateStatusIndicator('qdrant-client', qdrantStatus);
    
    // Update Neo4j status
    const neo4jStatus = statusData.kg.neo4j_status || 'connected';
    updateStatusIndicator('neo4j', neo4jStatus);
    
    // Update OpenAI status
    const openaiStatus = statusData.ai_rag.openai_status || 'connected';
    updateStatusIndicator('openai', openaiStatus);
    
    // Update ETL status
    const etlStatus = statusData.etl.status || 'available';
    updateStatusIndicator('etl', etlStatus);
    
    // Update System status
    const systemStatus = statusData.system.status || 'healthy';
    updateStatusIndicator('system', systemStatus);
}

// Update individual status indicator
function updateStatusIndicator(service, status) {
    const indicator = document.getElementById(`status-${service}`);
    if (!indicator) {
        console.warn(`Status indicator not found: status-${service}`);
        return;
    }
    
    console.log(`🔍 Updating ${service} indicator:`, indicator, 'with status:', status);
    
    const isHealthy = ['connected', 'available', 'healthy'].includes(status);
    const icon = indicator.querySelector('i');
    
    if (icon) {
        icon.className = icon.className.replace('text-muted', '');
        icon.className += isHealthy ? ' text-success' : ' text-danger';
    }
    
    console.log(`🔍 ${service} isHealthy:`, isHealthy);
    console.log(`✅ ${service} indicator updated to:`, status);
}

// Load system statistics
function loadSystemStats() {
    console.log('📊 Loading system stats...');
    
    fetch('/ai-rag/stats')
        .then(response => response.json())
        .then(data => {
            console.log('✅ System stats received:', data);
            
            const statsHtml = `
                <div class="row text-center">
                    <div class="col-4">
                        <div class="border-end">
                            <h4 class="text-primary mb-1">${data.collections_count}</h4>
                            <small class="text-muted">Collections</small>
                        </div>
                    </div>
                    <div class="col-4">
                        <div class="border-end">
                            <h4 class="text-success mb-1">${data.total_points}</h4>
                            <small class="text-muted">Total Points</small>
                        </div>
                    </div>
                    <div class="col-4">
                        <h4 class="text-info mb-1">${data.assets_count}</h4>
                        <small class="text-muted">Assets</small>
                    </div>
                </div>
                <hr class="my-2">
                <div class="row">
                    <div class="col-6">
                        <small class="text-muted">
                            <i class="fas fa-database me-1"></i>${data.qdrant_status}
                        </small>
                    </div>
                    <div class="col-6">
                        <small class="text-muted">
                            <i class="fas fa-project-diagram me-1"></i>${data.neo4j_status}
                        </small>
                    </div>
                </div>
            `;
            
            document.getElementById('system-stats').innerHTML = statsHtml;
        })
        .catch(error => {
            console.error('❌ Error loading system stats:', error);
            document.getElementById('system-stats').innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Could not load system statistics
                </div>
            `;
        });
}

// Load collections
function loadCollections() {
    console.log('🗂️ Loading collections...');
    
    fetch('/ai-rag/collections')
        .then(response => response.json())
        .then(data => {
            console.log('✅ Collections received:', data);
            
            if (data && data.length > 0) {
                const collectionsHtml = data.slice(0, 5).map(collection => `
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="text-truncate me-2">${collection.name}</span>
                        <span class="badge bg-light text-dark ms-1">${collection.points_count || 0}</span>
                    </div>
                `).join('');
                
                const remainingCount = Math.max(0, data.length - 5);
                const footer = remainingCount > 0 ? 
                    `<small class="text-muted">+${remainingCount} more collections</small>` : '';
                
                document.getElementById('collections-info').innerHTML = collectionsHtml + footer;
            } else {
                document.getElementById('collections-info').innerHTML = `
                    <div class="text-center text-muted">
                        <i class="fas fa-database fa-2x mb-2"></i>
                        <p>No collections available</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('❌ Error loading collections:', error);
            document.getElementById('collections-info').innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Could not load collections
                </div>
            `;
        });
}

// Initialize RAG techniques
function initializeRAGTechniques() {
    console.log('🔧 Loading RAG techniques...');
    
    fetch('/ai-rag/techniques')
        .then(response => response.json())
        .then(data => {
            console.log('✅ Loaded RAG techniques:', data);
            
            // Update technique selector
            const techniqueSelect = document.getElementById('rag-technique-select');
            if (techniqueSelect && data.techniques) {
                techniqueSelect.innerHTML = data.techniques.map(technique => 
                    `<option value="${technique.id}">${technique.name}</option>`
                ).join('');
            }
            
            // Load initial technique info
            updateTechniqueInfo('basic');
        })
        .catch(error => {
            console.error('❌ Error loading RAG techniques:', error);
        });
}

// Update technique information
function updateTechniqueInfo(techniqueId) {
    const techniqueInfo = {
        basic: {
            title: 'Basic RAG',
            description: 'Simple retrieval + generation approach using vector search and LLM',
            bestFor: 'Simple queries, quick responses',
            performance: 'Fastest, lowest resource usage',
            icon: 'fas fa-rocket',
            color: 'text-success'
        },
        hybrid: {
            title: 'Hybrid RAG',
            description: 'Combines dense vector search with sparse keyword search for better coverage',
            bestFor: 'Complex queries requiring both semantic and keyword matching',
            performance: 'Balanced speed and accuracy',
            icon: 'fas fa-layer-group',
            color: 'text-info'
        },
        multi_step: {
            title: 'Multi-Step RAG',
            description: 'Iterative refinement approach with multiple retrieval and generation steps',
            bestFor: 'Complex analytical questions requiring deep reasoning',
            performance: 'Highest accuracy, moderate speed',
            icon: 'fas fa-stairs',
            color: 'text-warning'
        },
        graph: {
            title: 'Graph RAG',
            description: 'Leverages knowledge graph relationships for enhanced context retrieval',
            bestFor: 'Questions about relationships, connections, and structured data',
            performance: 'Excellent for graph-based queries',
            icon: 'fas fa-project-diagram',
            color: 'text-primary'
        },
        advanced: {
            title: 'Advanced RAG',
            description: 'Sophisticated approach with reranking, filtering, and advanced context combination',
            bestFor: 'Production systems requiring high-quality responses',
            performance: 'Best quality, higher resource usage',
            icon: 'fas fa-crown',
            color: 'text-danger'
        }
    };
    
    const technique = techniqueInfo[techniqueId] || techniqueInfo.basic;
    
    // Update technique title
    const titleElement = document.getElementById('technique-title');
    if (titleElement) {
        titleElement.textContent = technique.title;
    }
    
    // Update technique description
    const descriptionElement = document.getElementById('technique-description');
    if (descriptionElement) {
        descriptionElement.innerHTML = `
            <p class="mb-1 small">${technique.description}</p>
            <p class="mb-1 small"><strong>Best For:</strong> ${technique.bestFor}</p>
            <p class="mb-0 small"><strong>Performance:</strong> ${technique.performance}</p>
        `;
    }
    
    // Update technique icon
    const iconElement = document.querySelector('.technique-icon i');
    if (iconElement) {
        iconElement.className = `${technique.icon} fa-2x ${technique.color}`;
    }
}

// Set up event listeners
function setupEventListeners() {
    // RAG technique selector
    const techniqueSelect = document.getElementById('rag-technique-select');
    if (techniqueSelect) {
        techniqueSelect.addEventListener('change', function() {
            currentTechnique = this.value;
            updateTechniqueInfo(currentTechnique);
        });
    }
    
    // LLM model selector
    const modelSelect = document.getElementById('llm-model-select');
    if (modelSelect) {
        modelSelect.addEventListener('change', function() {
            currentModel = this.value;
        });
    }
    
    // Analysis type selector
    const analysisSelect = document.getElementById('analysis-type-select');
    if (analysisSelect) {
        analysisSelect.addEventListener('change', function() {
            currentAnalysisType = this.value;
        });
    }
    
    // Submit query button
    const submitButton = document.getElementById('submit-query');
    if (submitButton) {
        submitButton.addEventListener('click', submitQuery);
    }
    
    // Clear query button
    const clearButton = document.getElementById('clear-query');
    if (clearButton) {
        clearButton.addEventListener('click', clearQuery);
    }
    
    // Demo query buttons
    const demoButtons = document.querySelectorAll('.demo-query-btn');
    demoButtons.forEach(button => {
        button.addEventListener('click', function() {
            const query = this.getAttribute('data-query');
            if (query) {
                document.getElementById('query-input').value = query;
                submitQuery();
            }
        });
    });
    
    // Run all demos button
    const runAllButton = document.getElementById('run-all-demos');
    if (runAllButton) {
        runAllButton.addEventListener('click', runAllDemos);
    }
}

// Submit query
function submitQuery() {
    const queryInput = document.getElementById('query-input');
    const query = queryInput.value.trim();
    
    if (!query) {
        alert('Please enter a question to analyze.');
        return;
    }
    
    // Show loading state
    const loadingDiv = document.getElementById('query-loading');
    const submitButton = document.getElementById('submit-query');
    
    loadingDiv.style.display = 'block';
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Analyzing...';
    
    // Prepare request data
    const requestData = {
        query: query,
        analysis_type: currentAnalysisType,
        llm_model: currentModel,
        rag_technique: currentTechnique,
        top_k: 5,
        similarity_threshold: 0.7,
        enable_reranking: false,
        enable_graph_context: true,
        enable_metadata_filtering: false
    };
    
    console.log('🔍 Submitting query:', requestData);
    
    // Submit the query
    fetch('/ai-rag/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        console.log('✅ Query response received:', data);
        displayResults(data);
    })
    .catch(error => {
        console.error('❌ Query error:', error);
        displayError('Failed to analyze query. Please try again.');
    })
    .finally(() => {
        // Hide loading state
        loadingDiv.style.display = 'none';
        submitButton.disabled = false;
        submitButton.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Analyze with AI';
    });
}

// Display results
function displayResults(data) {
    const responseSection = document.getElementById('response-section');
    const responseContent = document.getElementById('response-content');
    
    // Format the analysis text for better readability
    const formattedAnalysis = formatAnalysisText(data.analysis);
    
    const resultsHtml = `
        <div class="mb-4">
            <h6 class="text-primary fw-bold">
                <i class="fas fa-question-circle me-2"></i>
                Your Question
            </h6>
            <div class="bg-primary bg-opacity-10 p-3 rounded border-start border-primary border-4">
                <p class="mb-0 fw-semibold">${data.query}</p>
            </div>
        </div>
        
        <div class="mb-4">
            <h6 class="text-success fw-bold">
                <i class="fas fa-lightbulb me-2"></i>
                AI Analysis
            </h6>
            <div class="bg-light p-4 rounded border">
                <div class="analysis-content">
                    ${formattedAnalysis}
                </div>
            </div>
        </div>
        
        ${data.context && data.context.length > 0 ? `
        <div class="mb-4">
            <h6 class="text-info fw-bold">
                <i class="fas fa-search me-2"></i>
                Retrieved Context (${data.context.length} sources)
            </h6>
            <div class="bg-light p-3 rounded border">
                ${data.context.map((ctx, index) => `
                    <div class="mb-3 p-3 bg-white rounded border">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <span class="badge bg-info">Source ${index + 1}</span>
                            <small class="text-muted">${ctx.length} characters</small>
                        </div>
                        <p class="mb-0 small text-dark">${formatContextText(ctx)}</p>
                    </div>
                `).join('')}
            </div>
        </div>
        ` : ''}
        
        <div class="row mt-4">
            <div class="col-md-6">
                <div class="d-flex align-items-center">
                    <i class="fas fa-brain text-success me-2"></i>
                    <div>
                        <small class="text-muted d-block">Technique Used</small>
                        <span class="fw-semibold">${data.technique_name || data.rag_technique}</span>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="d-flex align-items-center">
                    <i class="fas fa-robot text-primary me-2"></i>
                    <div>
                        <small class="text-muted d-block">AI Model</small>
                        <span class="fw-semibold">${data.model || currentModel}</span>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    responseContent.innerHTML = resultsHtml;
    responseSection.style.display = 'block';
    
    // Scroll to results
    responseSection.scrollIntoView({ behavior: 'smooth' });
}

// Format analysis text for better readability
function formatAnalysisText(text) {
    if (!text) return '';
    
    // Convert markdown-style formatting to HTML (similar to the old class-based approach)
    let formatted = text
        // Convert ### headers to h3
        .replace(/###\s+(.*?)(?=\n|$)/g, '<h3 class="mt-3 mb-2">$1</h3>')
        // Convert ## headers to h4
        .replace(/##\s+(.*?)(?=\n|$)/g, '<h4 class="mt-3 mb-2">$1</h4>')
        // Convert # headers to h5
        .replace(/^#\s+(.*?)(?=\n|$)/gm, '<h5 class="mt-3 mb-2">$1</h5>')
        // Convert **bold** to <strong>bold</strong>
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Convert *italic* to <em>italic</em> (but not if it's part of a list)
        .replace(/(?<!-)\*(.*?)\*(?!-)/g, '<em>$1</em>')
        // Format URLs as clickable links
        .replace(/(https?:\/\/[^\s\)]+?)(?=\s|$|\)|\.\s|\.$)/g, '<a href="$1" target="_blank" class="text-primary">$1</a>')
        // Add line breaks between numbered lists that appear on the same line
        .replace(/(\d+\.\s+[^1]*?)(?=\s*\d+\.\s+)/g, '$1<br>')
        // Add line breaks between bullet points that appear on the same line (only at start of line or after whitespace)
        .replace(/(\s*-\s+[^-]*?)(?=\s*-\s+)/g, '$1<br>')
        // Convert line breaks to <br> tags (but be more conservative)
        .replace(/\n/g, '<br>')
        // Clean up excessive line breaks
        .replace(/<br><br><br>/g, '<br><br>')
        .replace(/<br><br><br>/g, '<br><br>');
    
    return formatted;
}

// Format context text for better readability
function formatContextText(text) {
    if (!text) return '';
    
    // Truncate if too long
    const maxLength = 300;
    let formatted = text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    
    // Format URLs - ensure complete URLs are formatted as clickable links
    // Use a precise pattern that stops at the end of the URL
    formatted = formatted.replace(/(https?:\/\/[^\s\)]+?)(?=\s|$|\)|\.\s|\.$)/g, '<a href="$1" target="_blank" class="text-primary">$1</a>');
    
    // Format bold text
    formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    return formatted;
}

// Display error
function displayError(message) {
    const responseSection = document.getElementById('response-section');
    const responseContent = document.getElementById('response-content');
    
    responseContent.innerHTML = `
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
        </div>
    `;
    
    responseSection.style.display = 'block';
    responseSection.scrollIntoView({ behavior: 'smooth' });
}

// Clear query
function clearQuery() {
    document.getElementById('query-input').value = '';
    document.getElementById('response-section').style.display = 'none';
}

// Run all demos
function runAllDemos() {
    const demoQueries = [
        "What are the quality issues in our manufacturing assets?",
        "Assess the risk level of our critical equipment",
        "How can we optimize our production efficiency?",
        "What are the main assets in our digital twin system?"
    ];
    
    let currentIndex = 0;
    
    function runNextDemo() {
        if (currentIndex < demoQueries.length) {
            const query = demoQueries[currentIndex];
            document.getElementById('query-input').value = query;
            submitQuery();
            currentIndex++;
            
            // Wait for response before running next demo
            setTimeout(runNextDemo, 3000);
        }
    }
    
    runNextDemo();
} 