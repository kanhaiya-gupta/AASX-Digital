/**
 * Knowledge Graph System Status UI Component
 * Handles system status display and monitoring
 */

export async function initSystemStatus() {
    console.log('🔧 Initializing Knowledge Graph System Status component...');
    
    try {
        // Initialize status indicators
        await updateSystemStatus();
        
        // Set up periodic status updates
        setInterval(updateSystemStatus, 30000); // Update every 30 seconds
        
        console.log('✅ Knowledge Graph System Status component initialized');
        
    } catch (error) {
        console.error('❌ Failed to initialize System Status component:', error);
    }
}

async function updateSystemStatus() {
    try {
        const response = await fetch('/api/kg-neo4j/status');
        const status = await response.json();
        
        updateStatusIndicator('status-docker', status.docker_status);
        updateStatusIndicator('status-local', status.local_status);
        updateStatusIndicator('status-browser', status.browser_status);
        updateStatusIndicator('status-connection', status.connection_status);
        updateStatusIndicator('status-data', status.data_status);
        updateStatusIndicator('status-performance', status.performance_status);
        
    } catch (error) {
        console.error('Failed to update system status:', error);
    }
}

function updateStatusIndicator(elementId, status) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const icon = element.querySelector('i');
    if (!icon) return;
    
    // Update icon color based on status
    icon.className = icon.className.replace(/text-\w+/, '');
    
    switch (status) {
        case 'connected':
            icon.classList.add('text-success');
            break;
        case 'disconnected':
            icon.classList.add('text-danger');
            break;
        case 'warning':
            icon.classList.add('text-warning');
            break;
        default:
            icon.classList.add('text-muted');
    }
} 