/**
 * Statistics Module
 * Handles system statistics loading, digital twin statistics, collections information, and data visualization
 */

// Global variables for statistics
let systemStats = {};
let digitalTwinStats = {};
let collectionsData = [];
let statsRefreshInterval = null;

// Authentication variables
let isAuthenticated = false;
let currentUser = null;
let authToken = null;

/**
 * Initialize authentication
 */
function initAuthentication() {
    try {
        // Check if user is authenticated
        if (typeof getCurrentUser === 'function') {
            currentUser = getCurrentUser();
            if (currentUser) {
                isAuthenticated = true;
                authToken = getAuthToken();
                console.log('🔐 Statistics: User authenticated:', currentUser.username);
            } else {
                console.log('🔐 Statistics: User not authenticated');
                isAuthenticated = false;
            }
        } else {
            console.warn('⚠️ Statistics: getCurrentUser function not available');
            isAuthenticated = false;
        }
    } catch (error) {
        console.error('❌ Statistics: Authentication initialization error:', error);
        isAuthenticated = false;
    }
}

/**
 * Get authentication token
 */
function getAuthToken() {
    try {
        // Try to get token from localStorage/sessionStorage
        return localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
    } catch (error) {
        console.warn('⚠️ Statistics: Could not get auth token:', error);
        return null;
    }
}

/**
 * Get authentication headers for API calls
 */
function getAuthHeaders() {
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    return headers;
}

/**
 * Initialize statistics module
 */
export async function initStatistics() {
    console.log('🔍 Statistics Module: Initializing...');
    
    try {
        // Initialize authentication
        initAuthentication();
        
        // Load initial statistics
        await loadSystemStats();
        await loadCollections();
        await loadDigitalTwinStatistics();
        
        // Set up periodic refresh (every 60 seconds)
        statsRefreshInterval = setInterval(async () => {
            await loadSystemStats();
            await loadCollections();
            await loadDigitalTwinStatistics();
        }, 60000);
        
        console.log('✅ Statistics Module: Initialized successfully');
    } catch (error) {
        console.error('❌ Statistics Module: Initialization failed:', error);
        throw error;
    }
}

/**
 * Load system statistics
 */
export async function loadSystemStats() {
    console.log('📊 Statistics Module: Loading system stats...');
    
    try {
        const response = await fetch('/api/ai-rag/stats', {
            headers: getAuthHeaders()
        });
        const data = await response.json();
        
        console.log('✅ Statistics Module: System stats received:', data);
        systemStats = data;
        
        updateSystemStatsDisplay(data);
        
    } catch (error) {
        console.error('❌ Statistics Module: Error loading system stats:', error);
        displaySystemStatsError();
    }
}

/**
 * Update system statistics display
 */
function updateSystemStatsDisplay(data) {
    const statsContainer = document.getElementById('system-stats');
    if (!statsContainer) {
        console.warn('Statistics Module: System stats container not found');
        return;
    }
    
    const statsHtml = `
        <div class="row text-center">
            <div class="col-4">
                <div class="border-end">
                    <h4 class="text-primary mb-1">${data.collections_count || 0}</h4>
                    <small class="text-muted">Collections</small>
                </div>
            </div>
            <div class="col-4">
                <div class="border-end">
                    <h4 class="text-success mb-1">${data.total_points || 0}</h4>
                    <small class="text-muted">Total Points</small>
                </div>
            </div>
            <div class="col-4">
                <h4 class="text-info mb-1">${data.assets_count || 0}</h4>
                <small class="text-muted">Assets</small>
            </div>
        </div>
        <hr class="my-2">
        <div class="row">
            <div class="col-6">
                <small class="text-muted">
                    <i class="fas fa-database me-1"></i>${data.qdrant_status || 'Unknown'}
                </small>
            </div>
            <div class="col-6">
                <small class="text-muted">
                    <i class="fas fa-project-diagram me-1"></i>${data.neo4j_status || 'Unknown'}
                </small>
            </div>
        </div>
    `;
    
    statsContainer.innerHTML = statsHtml;
}

/**
 * Display system statistics error
 */
function displaySystemStatsError() {
    const statsContainer = document.getElementById('system-stats');
    if (statsContainer) {
        statsContainer.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Could not load system statistics
            </div>
        `;
    }
}

/**
 * Load collections information
 */
export async function loadCollections() {
    console.log('🗂️ Statistics Module: Loading collections...');
    
    try {
        const response = await fetch('/api/ai-rag/collections', {
            headers: getAuthHeaders()
        });
        const data = await response.json();
        
        console.log('✅ Statistics Module: Collections received:', data);
        collectionsData = data || [];
        
        updateCollectionsDisplay(data);
        
    } catch (error) {
        console.error('❌ Statistics Module: Error loading collections:', error);
        displayCollectionsError();
    }
}

/**
 * Update collections display
 */
function updateCollectionsDisplay(data) {
    const collectionsContainer = document.getElementById('collections-info');
    if (!collectionsContainer) {
        console.warn('Statistics Module: Collections container not found');
        return;
    }
    
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
        
        collectionsContainer.innerHTML = collectionsHtml + footer;
    } else {
        collectionsContainer.innerHTML = `
            <div class="text-center text-muted">
                <i class="fas fa-database fa-2x mb-2"></i>
                <p>No collections available</p>
            </div>
        `;
    }
}

/**
 * Display collections error
 */
function displayCollectionsError() {
    const collectionsContainer = document.getElementById('collections-info');
    if (collectionsContainer) {
        collectionsContainer.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Could not load collections
            </div>
        `;
    }
}

/**
 * Load digital twin statistics
 */
export async function loadDigitalTwinStatistics() {
    console.log('🤖 Statistics Module: Loading digital twin statistics...');
    
    try {
        const response = await fetch('/api/ai-rag/digital-twin-stats', {
            headers: getAuthHeaders()
        });
        const data = await response.json();
        
        console.log('✅ Statistics Module: Digital twin stats received:', data);
        digitalTwinStats = data;
        
        updateDigitalTwinStatisticsDisplay(data);
        
    } catch (error) {
        console.error('❌ Statistics Module: Error loading digital twin statistics:', error);
        displayDigitalTwinStatsError();
    }
}

/**
 * Update digital twin statistics display
 */
function updateDigitalTwinStatisticsDisplay(data) {
    const twinStatsContainer = document.getElementById('digital-twin-stats');
    if (!twinStatsContainer) {
        console.warn('Statistics Module: Digital twin stats container not found');
        return;
    }
    
    const statsHtml = `
        <div class="row text-center">
            <div class="col-6">
                <div class="border-end">
                    <h5 class="text-primary mb-1">${data.total_twins || 'N/A'}</h5>
                    <small class="text-muted">Total Twins</small>
                </div>
            </div>
            <div class="col-6">
                <h5 class="text-success mb-1">${data.active_twins || 'N/A'}</h5>
                <small class="text-muted">Active Twins</small>
            </div>
        </div>
        <hr class="my-2">
        <div class="row">
            <div class="col-12">
                <small class="text-muted">
                    <i class="fas fa-project-diagram me-1"></i>
                    ${data.projects_with_twins || 'N/A'} Projects with Twins
                </small>
            </div>
        </div>
    `;
    
    twinStatsContainer.innerHTML = statsHtml;
}

/**
 * Display digital twin statistics error
 */
function displayDigitalTwinStatsError() {
    const twinStatsContainer = document.getElementById('digital-twin-stats');
    if (twinStatsContainer) {
        twinStatsContainer.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Could not load digital twin statistics
            </div>
        `;
    }
}

/**
 * Get current system statistics
 */
export function getSystemStats() {
    return systemStats;
}

/**
 * Get current collections data
 */
export function getCollectionsData() {
    return collectionsData;
}

/**
 * Get current digital twin statistics
 */
export function getDigitalTwinStats() {
    return digitalTwinStats;
}

/**
 * Force refresh all statistics
 */
export async function refreshAllStatistics() {
    console.log('🔄 Statistics Module: Force refreshing all statistics...');
    
    await Promise.all([
        loadSystemStats(),
        loadCollections(),
        loadDigitalTwinStatistics()
    ]);
}

/**
 * Create statistics chart (if Chart.js is available)
 */
export function createStatisticsChart(containerId, data, type = 'bar') {
    const container = document.getElementById(containerId);
    if (!container) {
        console.warn(`Statistics Module: Chart container ${containerId} not found`);
        return null;
    }
    
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.warn('Statistics Module: Chart.js not available');
        return null;
    }
    
    const ctx = container.getContext('2d');
    if (!ctx) {
        console.warn('Statistics Module: Could not get canvas context');
        return null;
    }
    
    return new Chart(ctx, {
        type: type,
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'System Statistics'
                }
            }
        }
    });
}

/**
 * Generate statistics summary
 */
export function generateStatisticsSummary() {
    return {
        system: {
            collections: systemStats.collections_count || 0,
            totalPoints: systemStats.total_points || 0,
            assets: systemStats.assets_count || 0,
            qdrantStatus: systemStats.qdrant_status || 'Unknown',
            neo4jStatus: systemStats.neo4j_status || 'Unknown'
        },
        collections: {
            count: collectionsData.length,
            topCollections: collectionsData.slice(0, 5).map(c => ({
                name: c.name,
                points: c.points_count || 0
            }))
        },
        digitalTwins: {
            total: digitalTwinStats.total_twins || 'N/A',
            active: digitalTwinStats.active_twins || 'N/A',
            projects: digitalTwinStats.projects_with_twins || 'N/A'
        }
    };
}

/**
 * Cleanup statistics module
 */
export function cleanupStatistics() {
    if (statsRefreshInterval) {
        clearInterval(statsRefreshInterval);
        statsRefreshInterval = null;
    }
    console.log('🧹 Statistics Module: Cleaned up');
} 