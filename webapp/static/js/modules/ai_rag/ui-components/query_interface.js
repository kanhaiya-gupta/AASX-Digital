/**
 * Query Interface Module
 * Handles query submission, results display, loading states, and error handling
 */

console.log('🚨 QUERY INTERFACE MODULE LOADED - VERSION 2025-08-03-09-25 🚨');

// Global variables for query interface
let currentTechnique = 'auto';
let currentModel = 'gpt-3.5-turbo';
let currentAnalysisType = 'general';
let autoSelectEnabled = true; // Track if auto-select is enabled

/**
 * Initialize query interface module
 */
export async function initQueryInterface() {
    console.log('🚀 Query Interface Module: FUNCTION CALLED - Starting initialization...');
    console.log('🔍 Query Interface Module: Initializing...');
    console.log('🔍 Query Interface Module: DOM ready state:', document.readyState);
    
    // Check if all required elements exist
    const requiredElements = [
        'project-select',
        'twin-select', 
        'rag-technique-select',
        'llm-model-select',
        'analysis-type-select'
    ];
    
    console.log('🔍 Query Interface Module: Checking for elements...');
    const missingElements = [];
    for (const elementId of requiredElements) {
        const element = document.getElementById(elementId);
        console.log(`🔍 Query Interface Module: Element ${elementId}:`, element ? 'FOUND' : 'NOT FOUND');
        if (!element) {
            missingElements.push(elementId);
        }
    }
    
    if (missingElements.length > 0) {
        console.error('❌ Query Interface Module: Missing required elements:', missingElements);
        console.error('❌ Query Interface Module: This might indicate the analysis configuration component is not loaded');
    } else {
        console.log('✅ Query Interface Module: All required elements found');
    }
    
    try {
        console.log('🔧 Query Interface Module: Setting up event listeners...');
        // Set up event listeners
        setupQueryEventListeners();
        
        console.log('🔧 Query Interface Module: Waiting for DOM...');
        // Wait a bit for DOM to be fully loaded
        await new Promise(resolve => setTimeout(resolve, 100));
        
        console.log('🔧 Query Interface Module: Initializing RAG techniques...');
        // Initialize RAG techniques
        await initializeRAGTechniques();
        
        console.log('🔧 Query Interface Module: Initializing projects...');
        // Initialize projects and digital twins
        await initializeProjects();
        
        console.log('🔧 Query Interface Module: Initializing digital twins...');
        await initializeDigitalTwins();
        
        console.log('✅ Query Interface Module: Initialized successfully');
    } catch (error) {
        console.error('❌ Query Interface Module: Initialization failed:', error);
        throw error;
    }
}

/**
 * Set up event listeners for query interface
 */
function setupQueryEventListeners() {
    // RAG technique selector
    const techniqueSelect = document.getElementById('rag-technique-select');
    if (techniqueSelect) {
        techniqueSelect.addEventListener('change', function() {
            const selectedValue = this.value;
            if (selectedValue === '') {
                // Auto-select option chosen
                autoSelectEnabled = true;
                currentTechnique = 'auto';
                updateTechniqueInfo('auto');
                console.log('🔧 Query Interface Module: Auto-select enabled');
            } else {
                // Specific technique chosen
                autoSelectEnabled = false;
                currentTechnique = selectedValue;
                updateTechniqueInfo(selectedValue);
                
                // Clear any auto-selection notification
                const notification = document.getElementById('technique-recommendation-notification');
                if (notification) {
                    notification.style.display = 'none';
                }
                
                // Reset any auto-selected indicators in the dropdown
                const techniqueSelect = document.getElementById('rag-technique-select');
                if (techniqueSelect) {
                    Array.from(techniqueSelect.options).forEach(option => {
                        if (option.textContent.includes('(Auto-selected)')) {
                            option.textContent = option.textContent.replace(' (Auto-selected)', '');
                        }
                    });
                }
                
                console.log('🔧 Query Interface Module: Technique manually selected:', selectedValue);
            }
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
    
    // Query input for auto-selection
    const queryInput = document.getElementById('query-input');
    if (queryInput) {
        // Add debounced event listener for auto-selection
        let debounceTimer;
        queryInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                // ONLY call auto-selection if user has explicitly chosen "Auto-select"
                // NEVER override a manual selection
                if (autoSelectEnabled && this.value.trim().length > 10) {
                    // Only auto-select if query is substantial enough
                    getTechniqueRecommendation(this.value.trim());
                }
            }, 1000); // 1 second debounce
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
}

/**
 * Initialize RAG techniques
 */
async function initializeRAGTechniques() {
    console.log('🔧 Query Interface Module: Loading RAG techniques...');
    
    // Check if technique select element exists
    const techniqueSelect = document.getElementById('rag-technique-select');
    if (!techniqueSelect) {
        console.error('❌ Query Interface Module: RAG technique select element not found!');
        return;
    }
    console.log('✅ Query Interface Module: RAG technique select element found');
    
    try {
        const response = await fetch('/api/ai-rag/techniques');
        const data = await response.json();
        
        console.log('✅ Query Interface Module: Loaded RAG techniques:', data);
        
        // Update technique selector
        if (techniqueSelect) {
            // Handle both response formats: {techniques: [...]} and direct array
            const techniques = data.techniques || data;
            
            if (techniques && techniques.length > 0) {
                // Keep the Auto-select option and add the techniques
                const autoSelectOption = '<option value="">Auto-select (Recommended)</option>';
                const techniqueOptions = techniques.map(technique => 
                    `<option value="${technique.id}">${technique.name}</option>`
                ).join('');
                
                techniqueSelect.innerHTML = autoSelectOption + techniqueOptions;
                // Set default to Auto-select
                techniqueSelect.value = '';
                console.log(`✅ Query Interface Module: Loaded ${techniques.length} techniques`);
            } else {
                console.log('⚠️ Query Interface Module: No techniques found in response');
                // Keep at least the Auto-select option
                techniqueSelect.innerHTML = '<option value="">Auto-select (Recommended)</option>';
                // Set default to Auto-select
                techniqueSelect.value = '';
            }
        }
        
        // Load initial technique info - default to auto-select
        updateTechniqueInfo('auto');
        
        // Ensure the selector is set to Auto-select by default
        if (techniqueSelect) {
            techniqueSelect.value = '';
        }
        
    } catch (error) {
        console.error('❌ Query Interface Module: Error loading RAG techniques:', error);
        console.error('❌ Query Interface Module: Error details:', {
            message: error.message,
            stack: error.stack
        });
        
        // Ensure Auto-select option is available even on error
        const techniqueSelect = document.getElementById('rag-technique-select');
        if (techniqueSelect) {
            techniqueSelect.innerHTML = '<option value="">Auto-select (Recommended)</option>';
            techniqueSelect.value = '';
        }
    }
}

/**
 * Initialize projects dropdown
 */
async function initializeProjects() {
    console.log('🚀 Query Interface Module: initializeProjects FUNCTION CALLED!');
    console.log('🔧 Query Interface Module: Loading projects...');
    console.log('🔧 Query Interface Module: initializeProjects function called');
    
    // Check if project select element exists
    const projectSelect = document.getElementById('project-select');
    if (!projectSelect) {
        console.error('❌ Query Interface Module: Project select element not found!');
        return;
    }
    console.log('✅ Query Interface Module: Project select element found');
    
    try {
        console.log('🔧 Query Interface Module: Making API call to /api/ai-rag/projects');
        const response = await fetch('/api/ai-rag/projects');
        const data = await response.json();
        
        console.log('✅ Query Interface Module: Loaded projects:', data);
        
        // Update project selector
        if (projectSelect) {
            // Keep the default option
            const defaultOption = '<option value="">All Projects (Default)</option>';
            
            // Handle both response formats: {projects: [...]} and direct array
            const projects = data.projects || data;
            
            console.log('🔧 Query Interface Module: Projects array:', projects);
            console.log('🔧 Query Interface Module: Projects array length:', projects ? projects.length : 'undefined');
            console.log('🔧 Query Interface Module: First project:', projects && projects.length > 0 ? projects[0] : 'none');
            
            // Debug: Check the current state of the select element
            console.log('🔧 Query Interface Module: Project select element before update:', projectSelect);
            console.log('🔧 Query Interface Module: Project select innerHTML before update:', projectSelect.innerHTML);
            console.log('🔧 Query Interface Module: Project select style.display:', projectSelect.style.display);
            console.log('🔧 Query Interface Module: Project select parent element:', projectSelect.parentElement);
            console.log('🔧 Query Interface Module: Project select parent style.display:', projectSelect.parentElement ? projectSelect.parentElement.style.display : 'no parent');
            
            if (projects && projects.length > 0) {
                const projectOptions = projects.map(project => {
                    console.log('🔧 Query Interface Module: Processing project:', project);
                    console.log('🔧 Query Interface Module: Project ID field:', project.project_id || project.id);
                    console.log('🔧 Query Interface Module: Project name field:', project.name);
                    // Use project_id if available, otherwise fall back to id
                    const projectId = project.project_id || project.id;
                    return `<option value="${projectId}">${project.name}</option>`;
                }).join('');
                
                console.log('🔧 Query Interface Module: Generated project options:', projectOptions);
                console.log('🔧 Query Interface Module: Final HTML to set:', defaultOption + projectOptions);
                
                projectSelect.innerHTML = defaultOption + projectOptions;
                console.log(`✅ Query Interface Module: Loaded ${projects.length} projects`);
                console.log('🔧 Query Interface Module: Project select innerHTML after setting:', projectSelect.innerHTML);
                
                // Debug: Check if the element is visible and accessible
                console.log('🔧 Query Interface Module: Project select offsetHeight:', projectSelect.offsetHeight);
                console.log('🔧 Query Interface Module: Project select offsetWidth:', projectSelect.offsetWidth);
                console.log('🔧 Query Interface Module: Project select getBoundingClientRect():', projectSelect.getBoundingClientRect());
            } else {
                projectSelect.innerHTML = defaultOption + '<option value="" disabled>No projects available</option>';
                console.log('⚠️ Query Interface Module: No projects found in response');
            }
        }
        
    } catch (error) {
        console.error('❌ Query Interface Module: Error loading projects:', error);
        console.error('❌ Query Interface Module: Error details:', {
            message: error.message,
            stack: error.stack
        });
        // Set fallback message
        if (projectSelect) {
            projectSelect.innerHTML = '<option value="">All Projects (Default)</option><option value="" disabled>No projects available</option>';
        }
    }
}

/**
 * Initialize digital twins dropdown
 */
async function initializeDigitalTwins() {
    console.log('🔧 Query Interface Module: Loading digital twins...');
    console.log('🔧 Query Interface Module: initializeDigitalTwins function called');
    
    // Check if twin select element exists
    const twinSelect = document.getElementById('twin-select');
    if (!twinSelect) {
        console.error('❌ Query Interface Module: Digital twin select element not found!');
        return;
    }
    console.log('✅ Query Interface Module: Digital twin select element found');
    
    try {
        console.log('🔧 Query Interface Module: Making API call to /api/twin-registry/twins');
        const response = await fetch('/api/twin-registry/twins');
        const data = await response.json();
        
        console.log('✅ Query Interface Module: Loaded digital twins:', data);
        
        // Update twin selector
        if (twinSelect) {
            // Keep the default option
            const defaultOption = '<option value="">All Digital Twins (Default)</option>';
            
            // Handle both response formats: {twins: [...]} and direct array
            const twins = data.twins || data;
            
            if (twins && twins.length > 0) {
                const twinOptions = twins.map(twin => {
                    // Create a user-friendly display name
                    let displayName = '';
                    
                    // Try to use the most descriptive name available
                    if (twin.name && twin.name.trim()) {
                        displayName = twin.name;
                    } else if (twin.twin_name && twin.twin_name.trim()) {
                        displayName = twin.twin_name;
                    } else if (twin.display_name && twin.display_name.trim()) {
                        displayName = twin.display_name;
                    } else if (twin.original_filename && twin.original_filename.trim()) {
                        displayName = twin.original_filename;
                    } else if (twin.filename && twin.filename.trim()) {
                        displayName = twin.filename;
                    } else {
                        // Fallback to file_id but make it more readable
                        displayName = `Digital Twin (${twin.file_id})`;
                    }
                    
                    // Add type information if available
                    if (twin.type && twin.type.trim()) {
                        displayName += ` (${twin.type})`;
                    }
                    
                    // Add status indicator if available
                    if (twin.status) {
                        const statusIcon = twin.status === 'active' ? '🟢' : twin.status === 'inactive' ? '🔴' : '🟡';
                        displayName += ` ${statusIcon}`;
                    }
                    
                    return `<option value="${twin.file_id}">${displayName}</option>`;
                }).join('');
                
                twinSelect.innerHTML = defaultOption + twinOptions;
                console.log(`✅ Query Interface Module: Loaded ${twins.length} digital twins`);
            } else {
                twinSelect.innerHTML = defaultOption + '<option value="" disabled>No digital twins available</option>';
                console.log('⚠️ Query Interface Module: No digital twins found in response');
            }
        }
        
    } catch (error) {
        console.error('❌ Query Interface Module: Error loading digital twins:', error);
        console.error('❌ Query Interface Module: Error details:', {
            message: error.message,
            stack: error.stack
        });
        // Set fallback message
        if (twinSelect) {
            twinSelect.innerHTML = '<option value="">All Digital Twins (Default)</option><option value="" disabled>No digital twins available</option>';
        }
    }
}

/**
 * Update technique information display
 */
function updateTechniqueInfo(techniqueId) {
    const techniqueInfo = {
        auto: {
            title: 'Auto-select (Recommended)',
            description: 'System will automatically select the best RAG technique based on your query',
            bestFor: 'All query types, optimal performance',
            performance: 'Intelligent selection, balanced approach',
            icon: 'fas fa-magic',
            color: 'text-success'
        },
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
    
    const technique = techniqueInfo[techniqueId] || techniqueInfo.auto;
    
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

/**
 * Get technique recommendation for auto-selection
 */
async function getTechniqueRecommendation(query) {
    // CRITICAL: Double-check that auto-select is still enabled
    // This prevents any race conditions or edge cases
    if (!autoSelectEnabled || !query || query.length < 10) {
        console.log('🔧 Query Interface Module: Skipping recommendation - auto-select disabled or query too short');
        return;
    }
    
    console.log('🔧 Query Interface Module: Getting technique recommendation for query:', query.substring(0, 50) + '...');
    
    try {
        const response = await fetch('/api/ai-rag/techniques/recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ Query Interface Module: Technique recommendations received:', data);
        
        if (data.recommendations && data.recommendations.length > 0) {
            // Get the best recommendation
            const bestRecommendation = data.recommendations[0];
            const recommendedTechnique = bestRecommendation.technique_id;
            
            console.log('🔧 Query Interface Module: Best technique recommended:', recommendedTechnique);
            
            // CRITICAL: Triple-check that auto-select is still enabled before making ANY changes
            // This ensures we never override a user's manual selection
            if (autoSelectEnabled) {
                console.log('🔧 Query Interface Module: Auto-select still enabled, updating UI with recommendation');
                
                // Update the technique selector to show the recommended technique
                updateTechniqueSelectorWithRecommendation(recommendedTechnique, bestRecommendation);
                
                // Update current technique
                currentTechnique = recommendedTechnique;
                
                // Update technique info display
                updateTechniqueInfo(recommendedTechnique);
                
                // Show recommendation notification
                showRecommendationNotification(bestRecommendation);
            } else {
                console.log('🔧 Query Interface Module: Auto-select disabled during recommendation processing - preserving user selection');
            }
        }
        
    } catch (error) {
        console.error('❌ Query Interface Module: Error getting technique recommendation:', error);
        // Don't show error to user for auto-selection failures
    }
}

/**
 * Update technique selector to show recommended technique
 */
function updateTechniqueSelectorWithRecommendation(recommendedTechnique, recommendation) {
    // CRITICAL: Final safety check - never override if auto-select is disabled
    if (!autoSelectEnabled) {
        console.log('🔧 Query Interface Module: Safety check - auto-select disabled, not updating selector');
        return;
    }
    
    const techniqueSelect = document.getElementById('rag-technique-select');
    if (!techniqueSelect) return;
    
    // Find the option for the recommended technique
    const option = techniqueSelect.querySelector(`option[value="${recommendedTechnique}"]`);
    if (option) {
        // Temporarily select the recommended technique
        techniqueSelect.value = recommendedTechnique;
        
        // Add a visual indicator that this was auto-selected
        option.textContent = `${option.textContent} (Auto-selected)`;
        
        // Remove the indicator after 5 seconds
        setTimeout(() => {
            if (option.textContent.includes('(Auto-selected)')) {
                option.textContent = option.textContent.replace(' (Auto-selected)', '');
            }
        }, 5000);
    }
}

/**
 * Show recommendation notification
 */
function showRecommendationNotification(recommendation) {
    // Create or update notification element
    let notification = document.getElementById('technique-recommendation-notification');
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'technique-recommendation-notification';
        notification.className = 'alert alert-info alert-dismissible fade show mt-2';
        notification.innerHTML = `
            <i class="fas fa-lightbulb me-2"></i>
            <strong>Auto-selected:</strong> ${recommendation.technique_name} 
            <small class="text-muted">(${recommendation.confidence_score}% confidence)</small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert after the technique selector
        const techniqueSelect = document.getElementById('rag-technique-select');
        if (techniqueSelect && techniqueSelect.parentElement) {
            techniqueSelect.parentElement.appendChild(notification);
        }
    } else {
        // Update existing notification
        notification.innerHTML = `
            <i class="fas fa-lightbulb me-2"></i>
            <strong>Auto-selected:</strong> ${recommendation.technique_name} 
            <small class="text-muted">(${recommendation.confidence_score}% confidence)</small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        notification.style.display = 'block';
    }
    
    // Auto-hide after 8 seconds
    setTimeout(() => {
        if (notification) {
            notification.style.display = 'none';
        }
    }, 8000);
}

/**
 * Submit query to AI/RAG system
 */
export async function submitQuery() {
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
    
    // Get selected values from dropdowns
    const projectSelect = document.getElementById('project-select');
    const twinSelect = document.getElementById('twin-select');
    const selectedProjectId = projectSelect ? projectSelect.value : null;
    const selectedFileId = twinSelect ? twinSelect.value : null;
    
    // Handle auto-selection for technique
    let techniqueId = currentTechnique;
    console.log('🔧 Query Interface Module: Current technique before processing:', currentTechnique);
    console.log('🔧 Query Interface Module: Auto-select enabled:', autoSelectEnabled);
    
    if (autoSelectEnabled) {
        // If auto-select is enabled, don't specify technique_id to let backend auto-select
        techniqueId = null;
        console.log('🔧 Query Interface Module: Auto-select enabled, setting technique_id to null');
    } else {
        console.log('🔧 Query Interface Module: Manual selection, using technique_id:', techniqueId);
    }
    
    // Prepare request data - match QueryRequest model
    const requestData = {
        query: query,
        technique_id: techniqueId,
        project_id: selectedProjectId || null,
        search_limit: 10,
        llm_model: currentModel,
        enable_auto_selection: autoSelectEnabled
    };
    
    // If a specific digital twin is selected, use enhanced query
    const endpoint = selectedFileId ? '/api/ai-rag/enhanced-query' : '/api/ai-rag/query';
    if (selectedFileId) {
        requestData.file_id = selectedFileId;
    }
    
    console.log('🔍 Query Interface Module: Submitting query:', requestData);
    console.log('🔍 Query Interface Module: Request details:', {
        technique_id: requestData.technique_id,
        enable_auto_selection: requestData.enable_auto_selection,
        llm_model: requestData.llm_model
    });
    
    try {
        // Submit the query
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        console.log('✅ Query Interface Module: Query response received:', data);
        displayResults(data);
        
    } catch (error) {
        console.error('❌ Query Interface Module: Query error:', error);
        displayError('Failed to analyze query. Please try again.');
    } finally {
        // Hide loading state
        loadingDiv.style.display = 'none';
        submitButton.disabled = false;
        submitButton.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Analyze with AI';
    }
}

/**
 * Display query results
 */
function displayResults(data) {
    const responseSection = document.getElementById('response-section');
    const responseContent = document.getElementById('response-content');
    
    // Format the answer text for better readability
    const formattedAnswer = formatAnalysisText(data.answer || data.analysis || 'No answer provided');
    
    const resultsHtml = `
        <div class="mb-4">
            <h6 class="text-primary fw-bold">
                <i class="fas fa-question-circle me-2"></i>
                Your Question
            </h6>
            <div class="bg-primary bg-opacity-10 p-3 rounded border-start border-primary border-4">
                <p class="mb-0 fw-semibold">${data.query || 'No query provided'}</p>
            </div>
        </div>
        
        <div class="mb-4">
            <h6 class="text-success fw-bold">
                <i class="fas fa-lightbulb me-2"></i>
                AI Analysis
            </h6>
            <div class="bg-light p-4 rounded border">
                <div class="analysis-content">
                    ${formattedAnswer}
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
                        <span class="fw-semibold">
                            ${data.technique_name || data.technique_id || 'Unknown'}
                            ${autoSelectEnabled && data.technique_id ? ' (Auto-selected)' : ''}
                        </span>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="d-flex align-items-center">
                    <i class="fas fa-robot text-primary me-2"></i>
                    <div>
                        <small class="text-muted d-block">AI Model</small>
                        <span class="fw-semibold">${data.llm_model || currentModel}</span>
                    </div>
                </div>
            </div>
        </div>
        
        ${data.execution_time ? `
        <div class="row mt-3">
            <div class="col-md-6">
                <div class="d-flex align-items-center">
                    <i class="fas fa-clock text-warning me-2"></i>
                    <div>
                        <small class="text-muted d-block">Execution Time</small>
                        <span class="fw-semibold">${data.execution_time.toFixed(2)}s</span>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="d-flex align-items-center">
                    <i class="fas fa-search text-info me-2"></i>
                    <div>
                        <small class="text-muted d-block">Search Results</small>
                        <span class="fw-semibold">${data.search_results_count || 0}</span>
                    </div>
                </div>
            </div>
        </div>
        ` : ''}
    `;
    
    responseContent.innerHTML = resultsHtml;
    responseSection.style.display = 'block';
    
    // Scroll to results
    responseSection.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Format analysis text for better readability
 */
function formatAnalysisText(text) {
    if (!text) return '';
    
    // Convert markdown-style formatting to HTML
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
        // Add line breaks between bullet points that appear on the same line
        .replace(/(\s*-\s+[^-]*?)(?=\s*-\s+)/g, '$1<br>')
        // Convert line breaks to <br> tags
        .replace(/\n/g, '<br>')
        // Clean up excessive line breaks
        .replace(/<br><br><br>/g, '<br><br>')
        .replace(/<br><br><br>/g, '<br><br>');
    
    return formatted;
}

/**
 * Format context text for better readability
 */
function formatContextText(text) {
    if (!text) return '';
    
    // Truncate if too long
    const maxLength = 300;
    let formatted = text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    
    // Format URLs as clickable links
    formatted = formatted.replace(/(https?:\/\/[^\s\)]+?)(?=\s|$|\)|\.\s|\.$)/g, '<a href="$1" target="_blank" class="text-primary">$1</a>');
    
    // Format bold text
    formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    return formatted;
}

/**
 * Display error message
 */
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

/**
 * Clear query input and hide results
 */
export function clearQuery() {
    document.getElementById('query-input').value = '';
    document.getElementById('response-section').style.display = 'none';
    
    // Reset auto-selection
    autoSelectEnabled = true;
    currentTechnique = 'auto';
    
    // Reset technique selector to auto-select
    const techniqueSelect = document.getElementById('rag-technique-select');
    if (techniqueSelect) {
        techniqueSelect.value = '';
        // Clear any auto-selected indicators
        Array.from(techniqueSelect.options).forEach(option => {
            if (option.textContent.includes('(Auto-selected)')) {
                option.textContent = option.textContent.replace(' (Auto-selected)', '');
            }
        });
    }
    
    // Update technique info to show auto-select
    updateTechniqueInfo('auto');
    
    // Clear any auto-selection notification
    const notification = document.getElementById('technique-recommendation-notification');
    if (notification) {
        notification.style.display = 'none';
    }
}

/**
 * Get current query configuration
 */
export function getQueryConfig() {
    return {
        technique: currentTechnique,
        model: currentModel,
        analysisType: currentAnalysisType
    };
}

/**
 * Set query configuration
 */
export function setQueryConfig(config) {
    if (config.technique) currentTechnique = config.technique;
    if (config.model) currentModel = config.model;
    if (config.analysisType) currentAnalysisType = config.analysisType;
}

/**
 * Cleanup query interface module
 */
export function cleanupQueryInterface() {
    console.log('🧹 Query Interface Module: Cleaned up');
} 