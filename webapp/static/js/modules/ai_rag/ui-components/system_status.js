/**
 * System Status Module
 * Handles system status checking, status indicator updates, service health monitoring, and integration status display
 */

// Global variables for system status
let systemStatusData = {};
let statusCheckInterval = null;

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
                console.log('🔐 System Status: User authenticated:', currentUser.username);
            } else {
                console.log('🔐 System Status: User not authenticated');
                isAuthenticated = false;
            }
        } else {
            console.warn('⚠️ System Status: getCurrentUser function not available');
            isAuthenticated = false;
        }
    } catch (error) {
        console.error('❌ System Status: Authentication initialization error:', error);
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
        console.warn('⚠️ System Status: Could not get auth token:', error);
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
 * Initialize system status module
 */
export async function initSystemStatus() {
    console.log('🔍 System Status Module: Initializing...');
    
    try {
        // Initialize authentication
        initAuthentication();
        
        // Initial status check
        await checkAllServices();
        
        // Set up periodic status checks (every 30 seconds)
        statusCheckInterval = setInterval(checkAllServices, 30000);
        
        console.log('✅ System Status Module: Initialized successfully');
    } catch (error) {
        console.error('❌ System Status Module: Initialization failed:', error);
        throw error;
    }
}

/**
 * Check all services and update status indicators
 */
async function checkAllServices() {
    console.log('🔍 System Status Module: Checking all services...');
    
    try {
        const results = await Promise.all([
            checkService('ai_rag'),
            checkService('etl'),
            checkService('kg'),
            checkService('twin'),
            checkService('system')
        ]);
        
        console.log('🔍 System Status Module: All services results:', results);
        
        systemStatusData = {
            ai_rag: results[0],
            etl: results[1],
            kg: results[2],
            twin: results[3],
            system: results[4]
        };
        
        console.log('✅ System Status Module: Status data received:', systemStatusData);
        
        // Update status indicators
        updateStatusIndicators(systemStatusData);
        
    } catch (error) {
        console.error('❌ System Status Module: Error checking services:', error);
    }
}

/**
 * Check individual service
 */
function checkService(service) {
    return fetch(`/api/${service}/status`, {
        headers: getAuthHeaders()
    })
        .then(response => response.json())
        .catch(error => {
            console.error(`System Status Module: Error checking ${service} service:`, error);
            return { status: 'error', error: error.message };
        });
}

/**
 * Update status indicators based on service data
 */
function updateStatusIndicators(statusData) {
    console.log('🔍 System Status Module: Knowledge Graph status:', statusData.kg);
    console.log('🔍 System Status Module: Knowledge Graph neo4j_status:', statusData.kg.neo4j_status);
    console.log('🔍 System Status Module: ETL status:', statusData.etl);
    console.log('🔍 System Status Module: AI/RAG status:', statusData.ai_rag);
    
    // Update Qdrant status
    const qdrantStatus = statusData.ai_rag?.qdrant_status || 'connected';
    updateStatusIndicator('qdrant', qdrantStatus);
    
    // Update Qdrant client status
    updateStatusIndicator('qdrant-client', qdrantStatus);
    
    // Update Neo4j status
    const neo4jStatus = statusData.kg?.neo4j_status || 'connected';
    updateStatusIndicator('neo4j', neo4jStatus);
    
    // Update OpenAI status
    const openaiStatus = statusData.ai_rag?.openai_status || 'connected';
    updateStatusIndicator('openai', openaiStatus);
    
    // Update ETL status
    const etlStatus = statusData.etl?.status || 'available';
    updateStatusIndicator('etl', etlStatus);
    
    // Update System status
    const systemStatus = statusData.system?.status || 'healthy';
    updateStatusIndicator('system', systemStatus);
}

/**
 * Update individual status indicator
 */
function updateStatusIndicator(service, status) {
    const indicator = document.getElementById(`status-${service}`);
    if (!indicator) {
        console.warn(`System Status Module: Status indicator not found: status-${service}`);
        return;
    }
    
    console.log(`🔍 System Status Module: Updating ${service} indicator:`, indicator, 'with status:', status);
    
    const isHealthy = ['connected', 'available', 'healthy'].includes(status);
    const icon = indicator.querySelector('i');
    
    if (icon) {
        icon.className = icon.className.replace('text-muted', '');
        icon.className += isHealthy ? ' text-success' : ' text-danger';
    }
    
    console.log(`🔍 System Status Module: ${service} isHealthy:`, isHealthy);
    console.log(`✅ System Status Module: ${service} indicator updated to:`, status);
}

/**
 * Get current system status data
 */
export function getSystemStatus() {
    return systemStatusData;
}

/**
 * Force refresh system status
 */
export async function refreshSystemStatus() {
    console.log('🔄 System Status Module: Force refreshing system status...');
    await checkAllServices();
}

/**
 * Cleanup system status module
 */
export function cleanupSystemStatus() {
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
        statusCheckInterval = null;
    }
    console.log('🧹 System Status Module: Cleaned up');
}

/**
 * Check if a specific service is healthy
 */
export function isServiceHealthy(serviceName) {
    const serviceData = systemStatusData[serviceName];
    if (!serviceData) return false;
    
    const status = serviceData.status || serviceData.neo4j_status || serviceData.qdrant_status || serviceData.openai_status;
    return ['connected', 'available', 'healthy'].includes(status);
}

/**
 * Get service status summary
 */
export function getServiceStatusSummary() {
    const services = ['ai_rag', 'etl', 'kg', 'twin', 'system'];
    const summary = {};
    
    services.forEach(service => {
        summary[service] = isServiceHealthy(service);
    });
    
    return summary;
} 