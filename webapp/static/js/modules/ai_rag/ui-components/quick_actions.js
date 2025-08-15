/**
 * Quick Actions Module
 * Handles demo query buttons, AASX-specific queries, action button handlers, and query templates
 */

// Demo queries for different scenarios
const demoQueries = {
    manufacturing: [
        "What are the quality issues in our manufacturing assets?",
        "Assess the risk level of our critical equipment",
        "How can we optimize our production efficiency?",
        "What are the main assets in our digital twin system?"
    ],
    aasx: [
        "Show me all AASX files in our system",
        "What digital twins are available for analysis?",
        "List all projects with their associated assets",
        "What are the relationships between assets in our AASX models?"
    ],
    analytics: [
        "Analyze the performance trends of our equipment",
        "What are the key metrics for our production line?",
        "Identify potential bottlenecks in our manufacturing process",
        "Generate a summary of our asset health status"
    ],
    maintenance: [
        "What maintenance activities are scheduled?",
        "Which assets require immediate attention?",
        "What are the predicted failure risks?",
        "How can we improve our maintenance strategy?"
    ]
};

// Authentication variables
let isAuthenticated = false;
let currentUser = null;
let authToken = null;

/**
 * Wait for central auth system to be ready
 */
async function waitForAuthSystem() {
    console.log('🔐 Quick Actions: Waiting for central auth system...');
    
    if (window.authSystemReady && window.authManager) {
        console.log('🔐 Quick Actions: Auth system already ready');
        return;
    }
    
    return new Promise((resolve) => {
        const handleReady = () => {
            console.log('🚀 Quick Actions: Auth system ready event received');
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
            console.warn('⚠️ Quick Actions: Timeout waiting for auth system');
            resolve();
        }, 10000);
    });
}

/**
 * Update authentication state from central auth manager
 */
function updateAuthState() {
    if (!window.authManager) {
        console.log('⚠️ Quick Actions: No auth manager available');
        return;
    }
    
    try {
        const sessionInfo = window.authManager.getSessionInfo();
        console.log('🔐 Quick Actions: Auth state update:', sessionInfo);
        
        if (sessionInfo && sessionInfo.isAuthenticated) {
            isAuthenticated = true;
            currentUser = sessionInfo.user;
            authToken = window.authManager.getStoredToken();
            console.log('🔐 Quick Actions: User authenticated:', currentUser.username);
        } else {
            isAuthenticated = false;
            currentUser = null;
            authToken = null;
            console.log('🔐 Quick Actions: User not authenticated (demo mode)');
        }
    } catch (error) {
        console.warn('⚠️ Quick Actions: Error updating auth state:', error);
        isAuthenticated = false;
        currentUser = null;
        authToken = null;
    }
}

/**
 * Setup authentication listeners
 */
function setupAuthListeners() {
    // Listen for auth state changes
    window.addEventListener('authStateChanged', () => {
        console.log('🔄 Quick Actions: Auth state changed, updating...');
        updateAuthState();
    });
    
    // Listen for login success
    window.addEventListener('loginSuccess', async () => {
        console.log('🔐 Quick Actions: Login success detected');
        updateAuthState();
        // Refresh data after login
        setupDemoQueryListeners();
        setupActionButtonListeners();
    });
    
    // Listen for logout
    window.addEventListener('logout', () => {
        console.log('🔐 Quick Actions: Logout detected');
        updateAuthState();
        // Clear sensitive data after logout
        // No sensitive data to clear in quick actions
    });
}

/**
 * Get authentication headers for API calls
 */
function getAuthHeaders() {
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
 * Initialize quick actions module
 */
export async function initQuickActions() {
    console.log('🔍 Quick Actions Module: Initializing...');
    
    try {
        // ✅ CORRECT: Wait for central auth system first
        await waitForAuthSystem();
        
        // ✅ CORRECT: Update auth state from central system
        updateAuthState();
        
        // ✅ CORRECT: Listen for auth state changes
        setupAuthListeners();
        
        // Set up demo query event listeners
        setupDemoQueryListeners();
        
        // Set up action button listeners
        setupActionButtonListeners();
        
        console.log('✅ Quick Actions Module: Initialized with central auth integration');
    } catch (error) {
        console.error('❌ Quick Actions Module: Initialization failed:', error);
        throw error;
    }
}

/**
 * Set up demo query event listeners
 */
function setupDemoQueryListeners() {
    // Demo query buttons
    const demoButtons = document.querySelectorAll('.demo-query-btn');
    demoButtons.forEach(button => {
        button.addEventListener('click', function() {
            const query = this.getAttribute('data-query');
            if (query) {
                document.getElementById('query-input').value = query;
                // Import and call submitQuery from query_interface module
                import('./query_interface.js').then(module => {
                    module.submitQuery();
                });
            }
        });
    });
    
    // Run all demos button
    const runAllButton = document.getElementById('run-all-demos');
    if (runAllButton) {
        runAllButton.addEventListener('click', runAllDemos);
    }
}

/**
 * Set up action button event listeners
 */
function setupActionButtonListeners() {
    // AASX-specific action buttons
    const aasxButtons = document.querySelectorAll('.aasx-action-btn');
    aasxButtons.forEach(button => {
        button.addEventListener('click', function() {
            const action = this.getAttribute('data-action');
            const query = this.getAttribute('data-query');
            
            if (action === 'query' && query) {
                document.getElementById('query-input').value = query;
                import('./query_interface.js').then(module => {
                    module.submitQuery();
                });
            } else if (action === 'analyze') {
                runAASXAnalysis();
            } else if (action === 'export') {
                exportAASXData();
            }
        });
    });
}

/**
 * Run all demo queries sequentially
 */
export async function runAllDemos() {
    console.log('🚀 Quick Actions Module: Running all demos...');
    
    const allQueries = [
        ...demoQueries.manufacturing,
        ...demoQueries.aasx,
        ...demoQueries.analytics
    ];
    
    let currentIndex = 0;
    
    async function runNextDemo() {
        if (currentIndex < allQueries.length) {
            const query = allQueries[currentIndex];
            document.getElementById('query-input').value = query;
            
            // Import and call submitQuery
            const queryModule = await import('./query_interface.js');
            await queryModule.submitQuery();
            
            currentIndex++;
            
            // Wait for response before running next demo
            setTimeout(runNextDemo, 5000);
        }
    }
    
    runNextDemo();
}

/**
 * Run AASX-specific analysis
 */
async function runAASXAnalysis() {
    console.log('🔍 Quick Actions Module: Running AASX analysis...');
    
    try {
        const response = await fetch('/api/ai-rag/aasx-analysis', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                analysis_type: 'comprehensive',
                include_relationships: true,
                include_metadata: true
            })
        });
        
        const data = await response.json();
        console.log('✅ Quick Actions Module: AASX analysis completed:', data);
        
        // Display results
        displayAASXAnalysisResults(data);
        
    } catch (error) {
        console.error('❌ Quick Actions Module: AASX analysis failed:', error);
        displayError('Failed to run AASX analysis. Please try again.');
    }
}

/**
 * Export AASX data
 */
async function exportAASXData() {
    console.log('📤 Quick Actions Module: Exporting AASX data...');
    
    try {
        const response = await fetch('/api/ai-rag/export-aasx', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                format: 'json',
                include_metadata: true,
                include_relationships: true
            })
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `aasx_export_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            console.log('✅ Quick Actions Module: AASX data exported successfully');
        } else {
            throw new Error('Export failed');
        }
        
    } catch (error) {
        console.error('❌ Quick Actions Module: AASX export failed:', error);
        displayError('Failed to export AASX data. Please try again.');
    }
}

/**
 * Display AASX analysis results
 */
function displayAASXAnalysisResults(data) {
    const responseSection = document.getElementById('response-section');
    const responseContent = document.getElementById('response-content');
    
    const resultsHtml = `
        <div class="mb-4">
            <h6 class="text-primary fw-bold">
                <i class="fas fa-project-diagram me-2"></i>
                AASX Analysis Results
            </h6>
            <div class="bg-light p-4 rounded border">
                <div class="row">
                    <div class="col-md-6">
                        <h6 class="text-success">📊 Statistics</h6>
                        <ul class="list-unstyled">
                            <li><strong>Total Assets:</strong> ${data.total_assets || 'N/A'}</li>
                            <li><strong>Total Relationships:</strong> ${data.total_relationships || 'N/A'}</li>
                            <li><strong>Projects:</strong> ${data.projects_count || 'N/A'}</li>
                            <li><strong>Digital Twins:</strong> ${data.digital_twins_count || 'N/A'}</li>
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <h6 class="text-info">🔗 Key Relationships</h6>
                        <ul class="list-unstyled">
                            ${data.key_relationships ? data.key_relationships.map(rel => 
                                `<li><i class="fas fa-link text-primary me-1"></i>${rel}</li>`
                            ).join('') : '<li>No relationships found</li>'}
                        </ul>
                    </div>
                </div>
                
                ${data.insights ? `
                <hr>
                <h6 class="text-warning">💡 Insights</h6>
                <div class="bg-white p-3 rounded">
                    ${data.insights}
                </div>
                ` : ''}
            </div>
        </div>
    `;
    
    responseContent.innerHTML = resultsHtml;
    responseSection.style.display = 'block';
    responseSection.scrollIntoView({ behavior: 'smooth' });
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
 * Get demo queries by category
 */
export function getDemoQueries(category = 'all') {
    if (category === 'all') {
        return {
            manufacturing: demoQueries.manufacturing,
            aasx: demoQueries.aasx,
            analytics: demoQueries.analytics,
            maintenance: demoQueries.maintenance
        };
    }
    return demoQueries[category] || [];
}

/**
 * Add custom demo query
 */
export function addDemoQuery(category, query) {
    if (!demoQueries[category]) {
        demoQueries[category] = [];
    }
    demoQueries[category].push(query);
    console.log(`✅ Quick Actions Module: Added demo query to ${category}: ${query}`);
}

/**
 * Run specific category of demos
 */
export async function runCategoryDemos(category) {
    console.log(`🚀 Quick Actions Module: Running ${category} demos...`);
    
    const queries = demoQueries[category] || [];
    let currentIndex = 0;
    
    async function runNextDemo() {
        if (currentIndex < queries.length) {
            const query = queries[currentIndex];
            document.getElementById('query-input').value = query;
            
            const queryModule = await import('./query_interface.js');
            await queryModule.submitQuery();
            
            currentIndex++;
            setTimeout(runNextDemo, 5000);
        }
    }
    
    runNextDemo();
}

/**
 * Cleanup quick actions module
 */
export function cleanupQuickActions() {
    console.log('🧹 Quick Actions Module: Cleaned up');
} 