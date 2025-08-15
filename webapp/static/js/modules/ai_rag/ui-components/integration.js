/**
 * Integration Module
 * Handles ETL pipeline connection, digital twin data loading, project/file selection, and cross-module communication
 */

// Global variables for integration
let etlStatus = {};
let digitalTwinData = {};
let projectData = {};
let selectedProject = null;
let selectedTwin = null;

// Authentication variables
let isAuthenticated = false;
let currentUser = null;
let authToken = null;

/**
 * Wait for central auth system to be ready
 */
async function waitForAuthSystem() {
    console.log('🔐 Integration: Waiting for central auth system...');
    
    if (window.authSystemReady && window.authManager) {
        console.log('🔐 Integration: Auth system already ready');
        return;
    }
    
    return new Promise((resolve) => {
        const handleReady = () => {
            console.log('🚀 Integration: Auth system ready event received');
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
            console.warn('⚠️ Integration: Timeout waiting for auth system');
            resolve();
        }, 10000);
    });
}

/**
 * Update authentication state from central auth manager
 */
function updateAuthState() {
    if (!window.authManager) {
        console.log('⚠️ Integration: No auth manager available');
        return;
    }
    
    try {
        const sessionInfo = window.authManager.getSessionInfo();
        console.log('🔐 Integration: Auth state update:', sessionInfo);
        
        if (sessionInfo && sessionInfo.isAuthenticated) {
            isAuthenticated = true;
            currentUser = sessionInfo.user;
            authToken = window.authManager.getStoredToken();
            console.log('🔐 Integration: User authenticated:', currentUser.username);
        } else {
            isAuthenticated = false;
            currentUser = null;
            authToken = null;
            console.log('🔐 Integration: User not authenticated (demo mode)');
        }
    } catch (error) {
        console.warn('⚠️ Integration: Error updating auth state:', error);
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
        console.log('🔄 Integration: Auth state changed, updating...');
        updateAuthState();
    });
    
    // Listen for login success
    window.addEventListener('loginSuccess', async () => {
        console.log('🔐 Integration: Login success detected');
        updateAuthState();
        // Refresh data after login
        await loadETLStatus();
        await loadDigitalTwinData();
        await loadProjectData();
    });
    
    // Listen for logout
    window.addEventListener('logout', () => {
        console.log('🔐 Integration: Logout detected');
        updateAuthState();
        // Clear sensitive data after logout
        selectedProject = null;
        selectedTwin = null;
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
 * Initialize integration module
 */
export async function initIntegration() {
    console.log('🔍 Integration Module: Initializing...');
    
    try {
        // ✅ CORRECT: Wait for central auth system first
        await waitForAuthSystem();
        
        // ✅ CORRECT: Update auth state from central system
        updateAuthState();
        
        // ✅ CORRECT: Listen for auth state changes
        setupAuthListeners();
        
        // Load ETL pipeline status
        await loadETLStatus();
        
        // Load digital twin data
        await loadDigitalTwinData();
        
        // Load project data
        await loadProjectData();
        
        // Set up integration event listeners
        setupIntegrationEventListeners();
        
        // Set up cross-module communication
        setupCrossModuleCommunication();
        
        console.log('✅ Integration Module: Initialized with central auth integration');
    } catch (error) {
        console.error('❌ Integration Module: Initialization failed:', error);
        throw error;
    }
}

/**
 * Set up integration event listeners
 */
function setupIntegrationEventListeners() {
    // Project selection dropdown
    const projectSelect = document.getElementById('project-select');
    if (projectSelect) {
        projectSelect.addEventListener('change', function() {
            selectedProject = this.value;
            loadProjectDetails(selectedProject);
            updateDigitalTwinSelection(selectedProject);
        });
    }
    
    // Digital twin selection dropdown
    const twinSelect = document.getElementById('twin-select');
    if (twinSelect) {
        twinSelect.addEventListener('change', function() {
            selectedTwin = this.value;
            loadTwinDetails(selectedTwin);
        });
    }
    
    // ETL refresh button
    const etlRefreshButton = document.getElementById('refresh-etl-status');
    if (etlRefreshButton) {
        etlRefreshButton.addEventListener('click', loadETLStatus);
    }
    
    // Load project data button
    const loadProjectButton = document.getElementById('load-project-data');
    if (loadProjectButton) {
        loadProjectButton.addEventListener('click', loadProjectData);
    }
}

/**
 * Set up cross-module communication
 */
function setupCrossModuleCommunication() {
    // Listen for system status updates
    window.addEventListener('systemStatusUpdated', (event) => {
        console.log('🔍 Integration Module: System status updated:', event.detail);
        updateIntegrationStatus(event.detail);
    });
    
    // Listen for query completion
    window.addEventListener('queryCompleted', (event) => {
        console.log('🔍 Integration Module: Query completed:', event.detail);
        updateQueryIntegration(event.detail);
    });
    
    // Listen for statistics updates
    window.addEventListener('statisticsUpdated', (event) => {
        console.log('🔍 Integration Module: Statistics updated:', event.detail);
        updateStatisticsIntegration(event.detail);
    });
}

/**
 * Load ETL pipeline status
 */
export async function loadETLStatus() {
    console.log('🔄 Integration Module: Loading ETL status...');
    
    try {
        const response = await fetch('/api/ai-rag/etl/status', {
            headers: getAuthHeaders()
        });
        const data = await response.json();
        
        console.log('✅ Integration Module: ETL status received:', data);
        etlStatus = data;
        
        updateETLStatusDisplay(data);
        
        // Dispatch event for other modules
        window.dispatchEvent(new CustomEvent('etlStatusUpdated', {
            detail: data
        }));
        
    } catch (error) {
        console.error('❌ Integration Module: Error loading ETL status:', error);
        displayETLStatusError();
    }
}

/**
 * Update ETL status display
 */
function updateETLStatusDisplay(data) {
    const etlStatusContainer = document.getElementById('etl-status');
    if (!etlStatusContainer) {
        console.warn('Integration Module: ETL status container not found');
        return;
    }
    
    const statusHtml = `
        <div class="row">
            <div class="col-md-6">
                <div class="d-flex align-items-center mb-2">
                    <i class="fas fa-cogs text-primary me-2"></i>
                    <div>
                        <small class="text-muted d-block">Pipeline Status</small>
                        <span class="fw-semibold">${data.status || 'Unknown'}</span>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="d-flex align-items-center mb-2">
                    <i class="fas fa-clock text-info me-2"></i>
                    <div>
                        <small class="text-muted d-block">Last Run</small>
                        <span class="fw-semibold">${data.last_run || 'Never'}</span>
                    </div>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6">
                <div class="d-flex align-items-center mb-2">
                    <i class="fas fa-file-alt text-success me-2"></i>
                    <div>
                        <small class="text-muted d-block">Files Processed</small>
                        <span class="fw-semibold">${data.files_processed || 0}</span>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="d-flex align-items-center mb-2">
                    <i class="fas fa-exclamation-triangle text-warning me-2"></i>
                    <div>
                        <small class="text-muted d-block">Errors</small>
                        <span class="fw-semibold">${data.errors || 0}</span>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    etlStatusContainer.innerHTML = statusHtml;
}

/**
 * Display ETL status error
 */
function displayETLStatusError() {
    const etlStatusContainer = document.getElementById('etl-status');
    if (etlStatusContainer) {
        etlStatusContainer.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Could not load ETL pipeline status
            </div>
        `;
    }
}

/**
 * Load digital twin data from Twin Registry
 */
export async function loadDigitalTwinData() {
    console.log('🤖 Integration Module: Loading digital twin data...');
    
    try {
        // Use Twin Registry API instead of AI/RAG endpoint
        const response = await fetch('/api/twin-registry/twins', {
            headers: getAuthHeaders()
        });
        const data = await response.json();
        
        console.log('✅ Integration Module: Digital twin data received:', data);
        digitalTwinData = data;
        
        updateDigitalTwinDataDisplay(data);
        
        // Dispatch event for other modules
        window.dispatchEvent(new CustomEvent('digitalTwinDataUpdated', {
            detail: data
        }));
        
    } catch (error) {
        console.error('❌ Integration Module: Error loading digital twin data:', error);
        displayDigitalTwinDataError();
    }
}

/**
 * Update digital twin data display
 */
function updateDigitalTwinDataDisplay(data) {
    const twinDataContainer = document.getElementById('digital-twin-data');
    if (!twinDataContainer) {
        console.warn('Integration Module: Digital twin data container not found');
        return;
    }
    
    if (data && data.twins && data.twins.length > 0) {
        const twinsHtml = data.twins.slice(0, 5).map(twin => {
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
                // Fallback to id but make it more readable
                displayName = `Digital Twin (${twin.id || twin.file_id})`;
            }
            
            return `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <span class="text-truncate me-2" title="${displayName}">${displayName}</span>
                    <span class="badge bg-light text-dark ms-1">${twin.status || 'Unknown'}</span>
                </div>
            `;
        }).join('');
        
        const remainingCount = Math.max(0, data.twins.length - 5);
        const footer = remainingCount > 0 ? 
            `<small class="text-muted">+${remainingCount} more twins</small>` : '';
        
        twinDataContainer.innerHTML = twinsHtml + footer;
    } else {
        twinDataContainer.innerHTML = `
            <div class="text-center text-muted">
                <i class="fas fa-robot fa-2x mb-2"></i>
                <p>No digital twins available</p>
            </div>
        `;
    }
}

/**
 * Display digital twin data error
 */
function displayDigitalTwinDataError() {
    const twinDataContainer = document.getElementById('digital-twin-data');
    if (twinDataContainer) {
        twinDataContainer.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Could not load digital twin data
            </div>
        `;
    }
}

/**
 * Load project data from AASX API
 */
export async function loadProjectData() {
    console.log('📁 Integration Module: Loading project data...');
    
    try {
        // Use AASX API instead of AI/RAG endpoint
        const response = await fetch('/api/aasx/projects', {
            headers: getAuthHeaders()
        });
        const data = await response.json();
        
        console.log('✅ Integration Module: Project data received:', data);
        projectData = data;
        
        updateProjectSelection(data);
        
        // Dispatch event for other modules
        window.dispatchEvent(new CustomEvent('projectDataUpdated', {
            detail: data
        }));
        
    } catch (error) {
        console.error('❌ Integration Module: Error loading project data:', error);
        displayProjectDataError();
    }
}

/**
 * Update project selection dropdown
 */
function updateProjectSelection(data) {
    // COMMENTED OUT: This was conflicting with query_interface.js project loading
    // The query_interface.js module handles project dropdown population
    console.log('📁 Integration Module: Project selection update skipped - handled by query_interface.js');
    return;
    
    /*
    const projectSelect = document.getElementById('project-select');
    if (!projectSelect) {
        console.warn('Integration Module: Project select not found');
        return;
    }
    
    if (data && data.projects && data.projects.length > 0) {
        // Keep the default option and add projects
        const defaultOption = '<option value="">All Projects (Default)</option>';
        const projectOptions = data.projects.map(project => 
            `<option value="${project.id}">${project.name}</option>`
        ).join('');
        
        projectSelect.innerHTML = defaultOption + projectOptions;
    } else {
        // Keep the default option even when no projects are available
        projectSelect.innerHTML = '<option value="">All Projects (Default)</option><option value="" disabled>No projects available</option>';
    }
    */
}

/**
 * Update digital twin selection based on project
 */
function updateDigitalTwinSelection(projectId) {
    const twinSelect = document.getElementById('twin-select');
    if (!twinSelect) {
        console.warn('Integration Module: Twin select not found');
        return;
    }
    
    if (!projectId) {
        // Preserve the default option from HTML template
        twinSelect.innerHTML = '<option value="">All Digital Twins (Default)</option>';
        return;
    }
    
    const project = projectData.projects?.find(p => p.id === projectId);
    if (project && project.twins && project.twins.length > 0) {
        // Keep the default option and add project-specific twins
        const defaultOption = '<option value="">All Digital Twins (Default)</option>';
        const twinOptions = project.twins.map(twin => {
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
                // Fallback to id but make it more readable
                displayName = `Digital Twin (${twin.id})`;
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
            
            return `<option value="${twin.id}">${displayName}</option>`;
        }).join('');
        
        twinSelect.innerHTML = defaultOption + twinOptions;
    } else {
        // Keep the default option even when no twins are available
        twinSelect.innerHTML = '<option value="">All Digital Twins (Default)</option><option value="" disabled>No twins available for this project</option>';
    }
}

/**
 * Load project details
 */
async function loadProjectDetails(projectId) {
    if (!projectId) return;
    
    console.log('🔍 Integration Module: Loading project details for:', projectId);
    
    try {
        const response = await fetch(`/ai-rag/project/${projectId}`, {
            headers: getAuthHeaders()
        });
        const data = await response.json();
        
        console.log('✅ Integration Module: Project details received:', data);
        
        // Update project details display
        updateProjectDetailsDisplay(data);
        
    } catch (error) {
        console.error('❌ Integration Module: Error loading project details:', error);
    }
}

/**
 * Update project details display
 */
function updateProjectDetailsDisplay(data) {
    const projectDetailsContainer = document.getElementById('project-details');
    if (!projectDetailsContainer) {
        console.warn('Integration Module: Project details container not found');
        return;
    }
    
    const detailsHtml = `
        <div class="card">
            <div class="card-header">
                <h6 class="mb-0"><i class="fas fa-folder me-2"></i>Project Details</h6>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <strong>Name:</strong> ${data.name || 'Unknown'}<br>
                        <strong>Status:</strong> ${data.status || 'Unknown'}<br>
                        <strong>Created:</strong> ${data.created || 'Unknown'}
                    </div>
                    <div class="col-md-6">
                        <strong>Files:</strong> ${data.files_count || 0}<br>
                        <strong>Twins:</strong> ${data.twins_count || 0}<br>
                        <strong>Size:</strong> ${data.size || 'Unknown'}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    projectDetailsContainer.innerHTML = detailsHtml;
}

/**
 * Load twin details
 */
async function loadTwinDetails(twinId) {
    if (!twinId) return;
    
    console.log('🔍 Integration Module: Loading twin details for:', twinId);
    
    try {
        const response = await fetch(`/ai-rag/twin/${twinId}`, {
            headers: getAuthHeaders()
        });
        const data = await response.json();
        
        console.log('✅ Integration Module: Twin details received:', data);
        
        // Update twin details display
        updateTwinDetailsDisplay(data);
        
    } catch (error) {
        console.error('❌ Integration Module: Error loading twin details:', error);
    }
}

/**
 * Update twin details display
 */
function updateTwinDetailsDisplay(data) {
    const twinDetailsContainer = document.getElementById('twin-details');
    if (!twinDetailsContainer) {
        console.warn('Integration Module: Twin details container not found');
        return;
    }
    
    const detailsHtml = `
        <div class="card">
            <div class="card-header">
                <h6 class="mb-0"><i class="fas fa-robot me-2"></i>Digital Twin Details</h6>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <strong>Name:</strong> ${data.name || 'Unknown'}<br>
                        <strong>Type:</strong> ${data.type || 'Unknown'}<br>
                        <strong>Status:</strong> ${data.status || 'Unknown'}
                    </div>
                    <div class="col-md-6">
                        <strong>Assets:</strong> ${data.assets_count || 0}<br>
                        <strong>Relationships:</strong> ${data.relationships_count || 0}<br>
                        <strong>Last Updated:</strong> ${data.last_updated || 'Unknown'}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    twinDetailsContainer.innerHTML = detailsHtml;
}

/**
 * Display project data error
 */
function displayProjectDataError() {
    const projectSelect = document.getElementById('project-select');
    if (projectSelect) {
        // Keep the default option even on error
        projectSelect.innerHTML = '<option value="">All Projects (Default)</option><option value="" disabled>Error loading projects</option>';
    }
}

/**
 * Update integration status based on system status
 */
function updateIntegrationStatus(systemStatus) {
    console.log('🔍 Integration Module: Updating integration status:', systemStatus);
    
    // Update ETL integration status
    const etlIntegrationStatus = document.getElementById('etl-integration-status');
    if (etlIntegrationStatus) {
        const etlHealthy = systemStatus.etl?.status === 'available';
        etlIntegrationStatus.innerHTML = `
            <span class="badge ${etlHealthy ? 'bg-success' : 'bg-danger'}">
                <i class="fas fa-${etlHealthy ? 'check' : 'times'} me-1"></i>
                ETL ${etlHealthy ? 'Connected' : 'Disconnected'}
            </span>
        `;
    }
}

/**
 * Update query integration
 */
function updateQueryIntegration(queryData) {
    console.log('🔍 Integration Module: Updating query integration:', queryData);
    
    // Update query context with project/twin information
    if (selectedProject || selectedTwin) {
        const contextInfo = document.getElementById('query-context-info');
        if (contextInfo) {
            let contextText = '';
            if (selectedProject) {
                const project = projectData.projects?.find(p => p.id === selectedProject);
                contextText += `Project: ${project?.name || selectedProject}`;
            }
            if (selectedTwin) {
                const twin = projectData.projects?.find(p => p.id === selectedProject)?.twins?.find(t => t.id === selectedTwin);
                contextText += ` | Twin: ${twin?.name || selectedTwin}`;
            }
            
            contextInfo.innerHTML = `
                <small class="text-muted">
                    <i class="fas fa-info-circle me-1"></i>
                    ${contextText}
                </small>
            `;
        }
    }
}

/**
 * Update statistics integration
 */
function updateStatisticsIntegration(statisticsData) {
    console.log('🔍 Integration Module: Updating statistics integration:', statisticsData);
    
    // Update statistics with ETL and project information
    const integrationStatsContainer = document.getElementById('integration-stats');
    if (integrationStatsContainer) {
        const statsHtml = `
            <div class="row text-center">
                <div class="col-4">
                    <h6 class="text-primary">${etlStatus.files_processed || 0}</h6>
                    <small class="text-muted">Files Processed</small>
                </div>
                <div class="col-4">
                    <h6 class="text-success">${projectData.projects?.length || 0}</h6>
                    <small class="text-muted">Projects</small>
                </div>
                <div class="col-4">
                    <h6 class="text-info">${digitalTwinData.twins?.length || 0}</h6>
                    <small class="text-muted">Digital Twins</small>
                </div>
            </div>
        `;
        
        integrationStatsContainer.innerHTML = statsHtml;
    }
}

/**
 * Get current ETL status
 */
export function getETLStatus() {
    return etlStatus;
}

/**
 * Get current digital twin data
 */
export function getDigitalTwinData() {
    return digitalTwinData;
}

/**
 * Get current project data
 */
export function getProjectData() {
    return projectData;
}

/**
 * Get selected project
 */
export function getSelectedProject() {
    return selectedProject;
}

/**
 * Get selected twin
 */
export function getSelectedTwin() {
    return selectedTwin;
}

/**
 * Force refresh all integration data
 */
export async function refreshAllIntegrationData() {
    console.log('🔄 Integration Module: Force refreshing all integration data...');
    
    await Promise.all([
        loadETLStatus(),
        loadDigitalTwinData(),
        loadProjectData()
    ]);
}

/**
 * Generate integration summary
 */
export function generateIntegrationSummary() {
    return {
        etl: {
            status: etlStatus.status || 'Unknown',
            lastRun: etlStatus.last_run || 'Never',
            filesProcessed: etlStatus.files_processed || 0,
            errors: etlStatus.errors || 0
        },
        digitalTwins: {
            total: digitalTwinData.twins?.length || 0,
            active: digitalTwinData.twins?.filter(t => t.status === 'active').length || 0
        },
        projects: {
            total: projectData.projects?.length || 0,
            selected: selectedProject,
            selectedTwin: selectedTwin
        }
    };
}

/**
 * Cleanup integration module
 */
export function cleanupIntegration() {
    console.log('🧹 Integration Module: Cleaned up');
} 