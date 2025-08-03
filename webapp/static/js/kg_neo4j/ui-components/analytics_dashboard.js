/**
 * Knowledge Graph Analytics Dashboard UI Component
 * Handles analytics display and updates
 */

export async function initAnalyticsDashboard() {
    console.log('🔧 Initializing Knowledge Graph Analytics Dashboard component...');
    
    try {
        // Load initial analytics
        await updateAnalytics();
        
        // Set up periodic updates
        setInterval(updateAnalytics, 60000); // Update every minute
        
        console.log('✅ Knowledge Graph Analytics Dashboard component initialized');
        
    } catch (error) {
        console.error('❌ Failed to initialize Analytics Dashboard component:', error);
    }
}

async function updateAnalytics() {
    try {
        const response = await fetch('/api/kg-neo4j/database-stats');
        const data = await response.json();
        
        if (data.success) {
            updateAnalyticsDisplay(data.stats);
        }
        
    } catch (error) {
        console.error('Failed to update analytics:', error);
    }
}

function updateAnalyticsDisplay(stats) {
    const totalNodes = document.getElementById('total-nodes');
    const totalRelationships = document.getElementById('total-relationships');
    const totalLabels = document.getElementById('total-labels');
    const totalTypes = document.getElementById('total-types');
    
    if (totalNodes) totalNodes.textContent = stats.total_nodes || 0;
    if (totalRelationships) totalRelationships.textContent = stats.total_relationships || 0;
    if (totalLabels) totalLabels.textContent = stats.total_labels || 0;
    if (totalTypes) totalTypes.textContent = stats.total_relationship_types || 0;
} 