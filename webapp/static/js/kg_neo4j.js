// Neo4j Management Hub JavaScript
// Focused on launching and managing Neo4j tools

console.log('🔧 Neo4j Management Hub JavaScript loaded');

// ============================================================================
// DOCKER NEO4J FUNCTIONS
// ============================================================================

async function checkConnectionStatus() {
    console.log('🔍 Checking Docker Neo4j connection status...');
    
    try {
        const response = await fetch('/kg-neo4j/api/status');
        const data = await response.json();
        
        updateDockerStatus(data);
        
        if (data.success) {
            showNotification('✅ Docker Neo4j connection successful', 'success');
        } else {
            showNotification('❌ Docker Neo4j connection failed: ' + data.error, 'error');
        }
        
        return data.success;
    } catch (error) {
        console.error('Error checking connection status:', error);
        showNotification('❌ Failed to check Docker Neo4j status', 'error');
        updateDockerStatus({ success: false, error: error.message });
        return false;
    }
}

function updateDockerStatus(data) {
    const statusContainer = document.getElementById('docker-status');
    if (!statusContainer) return;
    
    const statusItems = statusContainer.querySelectorAll('.status-item');
    
    // Update Container Status
    if (statusItems[0]) {
        const statusIndicator = statusItems[0].querySelector('.status-indicator');
        const statusValue = statusItems[0].querySelector('.status-value');
        
        if (data.docker_running) {
            statusIndicator.className = 'status-indicator status-running';
            statusValue.innerHTML = '<span class="status-indicator status-running"></span>Running';
        } else {
            statusIndicator.className = 'status-indicator status-stopped';
            statusValue.innerHTML = '<span class="status-indicator status-stopped"></span>Stopped';
        }
    }
    
    // Update Browser Access status
    if (statusItems[1]) {
        const statusIndicator = statusItems[1].querySelector('.status-indicator');
        const statusValue = statusItems[1].querySelector('.status-value');
        
        if (data.browser_accessible) {
            statusIndicator.className = 'status-indicator status-running';
            statusValue.innerHTML = '<span class="status-indicator status-running"></span>Available';
        } else {
            statusIndicator.className = 'status-indicator status-stopped';
            statusValue.innerHTML = '<span class="status-indicator status-stopped"></span>Unavailable';
        }
    }
}

async function checkDockerStatus() {
    console.log('🐳 Checking Docker status...');
    
    try {
        const response = await fetch('/kg-neo4j/api/docker-status');
        const data = await response.json();
        
        if (data.success) {
            showNotification(`🐳 Docker: ${data.status}`, 'info');
        } else {
            showNotification('❌ Failed to check Docker status', 'error');
        }
        
        return data;
    } catch (error) {
        console.error('Error checking Docker status:', error);
        showNotification('❌ Docker status check failed', 'error');
        return { success: false, error: error.message };
    }
}

// ============================================================================
// LOCAL NEO4J FUNCTIONS
// ============================================================================

async function checkLocalStatus() {
    console.log('🖥️ Checking Local Neo4j status...');
    
    try {
        const response = await fetch('/kg-neo4j/api/local/status');
        const data = await response.json();
        
        updateLocalStatus(data);
        
        if (data.success) {
            if (data.application_running) {
                showNotification('✅ Local Neo4j Desktop is running', 'success');
            } else {
                showNotification('ℹ️ Local Neo4j Desktop is not running', 'info');
            }
        } else {
            showNotification('❌ Failed to check Local Neo4j status: ' + data.error, 'error');
        }
        
        return data.success;
    } catch (error) {
        console.error('Error checking local status:', error);
        showNotification('❌ Failed to check Local Neo4j status', 'error');
        updateLocalStatus({ success: false, error: error.message });
        return false;
    }
}

function updateLocalStatus(data) {
    const statusContainer = document.getElementById('local-status');
    if (!statusContainer) return;
    
    const statusItems = statusContainer.querySelectorAll('.status-item');
    
    // Update Application Status
    if (statusItems[0]) {
        const statusIndicator = statusItems[0].querySelector('.status-indicator');
        const statusValue = statusItems[0].querySelector('.status-value');
        
        if (data.application_running) {
            statusIndicator.className = 'status-indicator status-running';
            statusValue.innerHTML = '<span class="status-indicator status-running"></span>Running';
        } else {
            statusIndicator.className = 'status-indicator status-stopped';
            statusValue.innerHTML = '<span class="status-indicator status-stopped"></span>Not Running';
        }
    }
    
    // Update Connection Status
    if (statusItems[1]) {
        const statusIndicator = statusItems[1].querySelector('.status-indicator');
        const statusValue = statusItems[1].querySelector('.status-value');
        
        if (data.connection_available) {
            statusIndicator.className = 'status-indicator status-running';
            statusValue.innerHTML = '<span class="status-indicator status-running"></span>Connected';
        } else {
            statusIndicator.className = 'status-indicator status-stopped';
            statusValue.innerHTML = '<span class="status-indicator status-stopped"></span>Not Connected';
        }
    }
}

async function launchLocalNeo4jDesktop() {
    console.log('🖥️ Launching Local Neo4j Desktop...');
    
    try {
        showNotification('🖥️ Launching Neo4j Desktop...', 'info');
        
        const response = await fetch('/kg-neo4j/api/local/launch', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('✅ ' + data.message, 'success');
            
            // Wait a moment for the application to start
            setTimeout(() => {
                checkLocalStatus();
            }, 3000);
            
        } else {
            showNotification('❌ Failed to launch Neo4j Desktop: ' + data.error, 'error');
        }
        
        return data.success;
    } catch (error) {
        console.error('Error launching Neo4j Desktop:', error);
        showNotification('❌ Failed to launch Neo4j Desktop', 'error');
        return false;
    }
}

async function getLocalNeo4jInfo() {
    console.log('ℹ️ Getting Local Neo4j info...');
    
    try {
        const response = await fetch('/kg-neo4j/api/local/info');
        const data = await response.json();
        
        if (data.success) {
            console.log('Local Neo4j Info:', data);
            return data;
        } else {
            console.error('Failed to get local Neo4j info:', data.error);
            return null;
        }
    } catch (error) {
        console.error('Error getting local Neo4j info:', error);
        return null;
    }
}

// ============================================================================
// NEO4J TOOL LAUNCHING FUNCTIONS
// ============================================================================

function launchDockerBrowser() {
    console.log('🌐 Launching Docker Neo4j Browser...');
    
    // Open Docker Neo4j Browser in new tab
    const browserUrl = 'http://localhost:7475';
    window.open(browserUrl, '_blank');
    
    showNotification('🌐 Docker Neo4j Browser opened in new tab', 'success');
}

function launchLocalBrowser() {
    console.log('🌐 Launching Local Neo4j Browser...');
    
    // Open Local Neo4j Browser in new tab
    const browserUrl = 'http://localhost:7474';
    window.open(browserUrl, '_blank');
    
    showNotification('🌐 Local Neo4j Browser opened in new tab', 'success');
}

// ============================================================================
// DOCKER MANAGEMENT FUNCTIONS
// ============================================================================

async function startNeo4jDocker() {
    console.log('🚀 Starting Docker Neo4j container...');
    
    try {
        showNotification('🚀 Starting Docker Neo4j container...', 'info');
        
        const response = await fetch('/kg-neo4j/api/docker/start', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('✅ Docker Neo4j container started successfully', 'success');
            
            // Wait a moment for the container to fully start
            setTimeout(() => {
                checkConnectionStatus();
                checkDockerStatus();
            }, 3000);
            
        } else {
            showNotification('❌ Failed to start Docker container: ' + data.error, 'error');
        }
        
        return data.success;
    } catch (error) {
        console.error('Error starting Docker container:', error);
        showNotification('❌ Failed to start Docker container', 'error');
        return false;
    }
}

async function stopNeo4jDocker() {
    console.log('🛑 Stopping Docker Neo4j container...');
    
    try {
        showNotification('🛑 Stopping Docker Neo4j container...', 'info');
        
        const response = await fetch('/kg-neo4j/api/docker/stop', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('✅ Docker Neo4j container stopped successfully', 'success');
            
            // Update status immediately
            setTimeout(() => {
                checkConnectionStatus();
                checkDockerStatus();
            }, 1000);
            
        } else {
            showNotification('❌ Failed to stop Docker container: ' + data.error, 'error');
        }
        
        return data.success;
    } catch (error) {
        console.error('Error stopping Docker container:', error);
        showNotification('❌ Failed to stop Docker container', 'error');
        return false;
    }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after shorter time: 2 seconds for success, 3 seconds for others
    const timeout = type === 'success' ? 2000 : 3000;
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, timeout);
}

function showLocalHelp() {
    console.log('❓ Showing Local help...');
    showNotification('📖 Neo4j Desktop Setup: Download from neo4j.com/desktop', 'info');
}

function refreshAllStatus() {
    checkConnectionStatus();
    checkLocalStatus();
}

// ============================================================================
// INITIALIZATION
// ============================================================================

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Neo4j Management Hub initialized');
    
    // Initial status check
    setTimeout(() => {
        refreshAllStatus();
    }, 1000);
});

// Export functions for global access
window.kgNeo4j = {
    checkConnectionStatus,
    checkDockerStatus,
    checkLocalStatus,
    launchDockerBrowser,
    launchLocalBrowser,
    launchLocalNeo4jDesktop,
    startNeo4jDocker,
    stopNeo4jDocker,
    showNotification,
    showLocalHelp,
    refreshAllStatus,
    getLocalNeo4jInfo
}; 