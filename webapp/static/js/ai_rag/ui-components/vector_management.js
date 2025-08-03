/**
 * Vector Management Module
 * Handles vector DB operations, backup functionality, data management, and statistics display
 */

// Global variables for vector management
let vectorDbInfo = {};
let vectorDataStats = {};
let backupStatus = {};

/**
 * Initialize vector management module
 */
export async function initVectorManagement() {
    console.log('🔍 Vector Management Module: Initializing...');
    
    try {
        // Load initial vector database information
        await refreshVectorDbInfo();
        await loadVectorDataStats();
        
        // Set up event listeners for vector management
        setupVectorManagementEventListeners();
        
        console.log('✅ Vector Management Module: Initialized successfully');
    } catch (error) {
        console.error('❌ Vector Management Module: Initialization failed:', error);
        throw error;
    }
}

/**
 * Set up event listeners for vector management
 */
function setupVectorManagementEventListeners() {
    console.log('🔧 Vector Management Module: Setting up event listeners...');
    
    // Refresh vector database info
    const refreshBtn = document.getElementById('refresh-vector-info-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshVectorDbInfo);
    }
    
    // Show data statistics
    const showStatsBtn = document.getElementById('show-data-stats-btn');
    if (showStatsBtn) {
        showStatsBtn.addEventListener('click', showDataStats);
    }
    
    // Show stored documents
    const showDocsBtn = document.getElementById('show-stored-documents-btn');
    if (showDocsBtn) {
        showDocsBtn.addEventListener('click', showStoredDocuments);
    }
    
    // Create metadata backup
    const metadataBackupBtn = document.getElementById('create-metadata-backup-btn');
    if (metadataBackupBtn) {
        metadataBackupBtn.addEventListener('click', () => createBackup('metadata'));
    }
    
    // Create full backup
    const fullBackupBtn = document.getElementById('create-full-backup-btn');
    if (fullBackupBtn) {
        fullBackupBtn.addEventListener('click', () => createBackup('full'));
    }
    
    // Show backup history
    const backupHistoryBtn = document.getElementById('show-backup-history-btn');
    if (backupHistoryBtn) {
        backupHistoryBtn.addEventListener('click', showBackupHistory);
    }
    
    // Clear vector data
    const clearDataBtn = document.getElementById('clear-vector-data-btn');
    if (clearDataBtn) {
        clearDataBtn.addEventListener('click', clearGlobalVectorData);
    }
    
    console.log('✅ Vector Management Module: Event listeners set up');
}

/**
 * Refresh vector database information
 */
export async function refreshVectorDbInfo() {
    console.log('🔄 Vector Management Module: Refreshing vector DB info...');
    
    try {
        const response = await fetch('/api/ai-rag/vector-db-info');
        const data = await response.json();
        
        console.log('✅ Vector Management Module: Vector DB info received:', data);
        vectorDbInfo = data;
        
        updateVectorDbInfoDisplay(data);
        
    } catch (error) {
        console.error('❌ Vector Management Module: Error refreshing vector DB info:', error);
        displayVectorDbError();
    }
}

/**
 * Update vector database information display
 */
function updateVectorDbInfoDisplay(data) {
    const infoContainer = document.getElementById('vector-db-info');
    if (!infoContainer) {
        console.warn('Vector Management Module: Vector DB info container not found');
        return;
    }
    
    const infoHtml = `
        <div class="row">
            <div class="col-md-6">
                <div class="d-flex align-items-center mb-2">
                    <i class="fas fa-database text-primary me-2"></i>
                    <div>
                        <small class="text-muted d-block">Database</small>
                        <span class="fw-semibold">${data.database_name || 'Unknown'}</span>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="d-flex align-items-center mb-2">
                    <i class="fas fa-server text-success me-2"></i>
                    <div>
                        <small class="text-muted d-block">Status</small>
                        <span class="fw-semibold">${data.status || 'Unknown'}</span>
                    </div>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6">
                <div class="d-flex align-items-center mb-2">
                    <i class="fas fa-layer-group text-info me-2"></i>
                    <div>
                        <small class="text-muted d-block">Collections</small>
                        <span class="fw-semibold">${data.collections_count || 0}</span>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="d-flex align-items-center mb-2">
                    <i class="fas fa-chart-bar text-warning me-2"></i>
                    <div>
                        <small class="text-muted d-block">Total Points</small>
                        <span class="fw-semibold">${data.total_points || 0}</span>
                    </div>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-12">
                <div class="d-flex align-items-center">
                    <i class="fas fa-hdd text-secondary me-2"></i>
                    <div>
                        <small class="text-muted d-block">Storage</small>
                        <span class="fw-semibold">${data.storage_size || 'Unknown'}</span>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    infoContainer.innerHTML = infoHtml;
}

/**
 * Display vector database error
 */
function displayVectorDbError() {
    const infoContainer = document.getElementById('vector-db-info');
    if (infoContainer) {
        infoContainer.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Could not load vector database information
            </div>
        `;
    }
}

/**
 * Backup vector data
 */
export async function backupVectorData() {
    console.log('💾 Vector Management Module: Starting vector data backup...');
    
    const statusDiv = document.getElementById('data-management-status');
    if (statusDiv) {
        statusDiv.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-spinner fa-spin me-2"></i>
                Creating backup of vector data...
            </div>
        `;
    }
    
    try {
        const response = await fetch('/api/ai-rag/backup-vector-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                include_metadata: true,
                include_relationships: true,
                compression: true
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            backupStatus = data;
            statusDiv.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    <strong>Backup Created Successfully!</strong><br>
                    <small class="text-muted">
                        File: ${data.backup_file}<br>
                        Size: ${data.backup_size}<br>
                        Collections: ${data.collections_backed_up}
                    </small>
                </div>
            `;
            console.log('✅ Vector Management Module: Backup completed successfully:', data);
        } else {
            statusDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Backup Failed:</strong> ${data.error}<br>
                    <small class="text-muted">Check server logs for details</small>
                </div>
            `;
        }
        
    } catch (error) {
        console.error('❌ Vector Management Module: Backup error:', error);
        statusDiv.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                <strong>Error:</strong> Network error while creating backup<br>
                <small class="text-muted">Please try again or check server status</small>
            </div>
        `;
    }
}

/**
 * Clear vector data
 */
export async function clearVectorData() {
    console.log('🗑️ Vector Management Module: Clearing vector data...');
    
    if (!confirm('Are you sure you want to clear all vector data? This action cannot be undone.')) {
        return;
    }
    
    const statusDiv = document.getElementById('data-management-status');
    if (statusDiv) {
        statusDiv.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-spinner fa-spin me-2"></i>
                Clearing vector data...
            </div>
        `;
    }
    
    try {
        const response = await fetch('/api/ai-rag/clear-vector-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                confirm_clear: true,
                include_collections: true
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            statusDiv.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    <strong>Vector Data Cleared Successfully!</strong><br>
                    <small class="text-muted">
                        Collections removed: ${data.collections_removed}<br>
                        Points removed: ${data.points_removed}
                    </small>
                </div>
            `;
            
            // Refresh vector DB info after clearing
            await refreshVectorDbInfo();
            await loadVectorDataStats();
            
            console.log('✅ Vector Management Module: Vector data cleared successfully:', data);
        } else {
            statusDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Failed to Clear Data:</strong> ${data.error}<br>
                    <small class="text-muted">Check server logs for details</small>
                </div>
            `;
        }
        
    } catch (error) {
        console.error('❌ Vector Management Module: Clear data error:', error);
        statusDiv.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                <strong>Error:</strong> Network error while clearing data<br>
                <small class="text-muted">Please try again or check server status</small>
            </div>
        `;
    }
}

/**
 * Show data statistics
 */
export async function showDataStats() {
    console.log('📊 Vector Management Module: Fetching vector data stats...');
    
    const statusDiv = document.getElementById('data-management-status');
    if (statusDiv) {
        statusDiv.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-spinner fa-spin me-2"></i>
                Loading data statistics...
            </div>
        `;
    }
    
    try {
        const response = await fetch('/api/ai-rag/vector-data-stats');
        const data = await response.json();
        
        console.log('✅ Vector Management Module: Vector data stats received:', data);
        vectorDataStats = data;
        
        if (data.success) {
            let statsHtml = `
                <div class="alert alert-info">
                    <h6><i class="fas fa-chart-bar me-2"></i>Vector Database Statistics</h6>
                    <div class="row">
                        <div class="col-6">
                            <strong>Total Collections:</strong> ${data.total_collections}<br>
                            <strong>Total Points:</strong> ${data.total_points}<br>
                            <strong>Total Storage:</strong> ${data.total_storage}
                        </div>
                        <div class="col-6">
                            <strong>Largest Collection:</strong> ${data.largest_collection}
                        </div>
                    </div>
                    <hr>
                    <h6>Collection Breakdown:</h6>
                    <ul class="list-unstyled">
            `;
            
            data.collection_stats.forEach(collection => {
                statsHtml += `
                    <li class="mb-1">
                        <strong>${collection.name}:</strong> ${collection.points} points (${collection.storage})
                    </li>
                `;
            });
            
            statsHtml += '</ul></div>';
            statusDiv.innerHTML = statsHtml;
        } else {
            statusDiv.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-info-circle me-2"></i>
                    Could not load data statistics: ${data.error || 'Unknown error'}
                </div>
            `;
        }
        
    } catch (error) {
        console.error('❌ Vector Management Module: Error fetching data stats:', error);
        statusDiv.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Could not load data statistics: ${error.message || 'Network error'}
            </div>
        `;
    }
}

/**
 * Load vector data statistics
 */
export async function loadVectorDataStats() {
    console.log('📊 Vector Management Module: Loading vector data stats...');
    
    try {
        const response = await fetch('/api/ai-rag/vector-data-stats');
        const data = await response.json();
        
        if (data.success) {
            vectorDataStats = data;
            console.log('✅ Vector Management Module: Vector data stats loaded:', data);
        }
        
    } catch (error) {
        console.error('❌ Vector Management Module: Error loading vector data stats:', error);
    }
}

/**
 * Get current vector database information
 */
export function getVectorDbInfo() {
    return vectorDbInfo;
}

/**
 * Get current vector data statistics
 */
export function getVectorDataStats() {
    return vectorDataStats;
}

/**
 * Get current backup status
 */
export function getBackupStatus() {
    return backupStatus;
}

/**
 * Force refresh all vector management data
 */
export async function refreshAllVectorData() {
    console.log('🔄 Vector Management Module: Force refreshing all vector data...');
    
    await Promise.all([
        refreshVectorDbInfo(),
        loadVectorDataStats()
    ]);
}

/**
 * Generate vector management summary
 */
export function generateVectorManagementSummary() {
    return {
        database: {
            name: vectorDbInfo.database_name || 'Unknown',
            status: vectorDbInfo.status || 'Unknown',
            collections: vectorDbInfo.collections_count || 0,
            totalPoints: vectorDbInfo.total_points || 0,
            storageSize: vectorDbInfo.storage_size || 'Unknown'
        },
        statistics: {
            totalCollections: vectorDataStats.total_collections || 0,
            totalPoints: vectorDataStats.total_points || 0,
            totalStorage: vectorDataStats.total_storage || 'Unknown',
            largestCollection: vectorDataStats.largest_collection || 'Unknown'
        },
        backup: {
            lastBackup: backupStatus.backup_file || 'None',
            backupSize: backupStatus.backup_size || 'Unknown',
            collectionsBackedUp: backupStatus.collections_backed_up || 0
        }
    };
}

/**
 * Cleanup vector management module
 */
export function cleanupVectorManagement() {
    console.log('🧹 Vector Management Module: Cleaned up');
} 

// Add missing functions that are referenced in the HTML
export async function createBackup(type) {
    console.log(`🔄 Vector Management Module: Creating ${type} backup...`);
    
    try {
        const response = await fetch('/api/ai-rag/backup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ type })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            console.log(`✅ Vector Management Module: ${type} backup created successfully`);
            updateBackupStatus(`✅ ${type} backup created successfully`);
        } else {
            console.error(`❌ Vector Management Module: ${type} backup failed:`, result);
            updateBackupStatus(`❌ ${type} backup failed: ${result.detail || 'Unknown error'}`);
        }
        
    } catch (error) {
        console.error(`❌ Vector Management Module: Error creating ${type} backup:`, error);
        updateBackupStatus(`❌ ${type} backup failed: ${error.message}`);
    }
}

export async function showBackupHistory() {
    console.log('🔄 Vector Management Module: Loading backup history...');
    
    try {
        const response = await fetch('/api/ai-rag/backup/history');
        const history = await response.json();
        
        if (response.ok) {
            console.log('✅ Vector Management Module: Backup history loaded:', history);
            displayBackupHistory(history);
        } else {
            console.error('❌ Vector Management Module: Failed to load backup history:', history);
            updateBackupStatus('❌ Failed to load backup history');
        }
        
    } catch (error) {
        console.error('❌ Vector Management Module: Error loading backup history:', error);
        updateBackupStatus('❌ Error loading backup history');
    }
}

export async function clearGlobalVectorData() {
    console.log('🔄 Vector Management Module: Clearing global vector data...');
    
    if (!confirm('Are you sure you want to clear all global vector data? This action cannot be undone.')) {
        return;
    }
    
    const statusDiv = document.getElementById('data-management-status');
    if (statusDiv) {
        statusDiv.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-spinner fa-spin me-2"></i>
                Clearing all vector data from Qdrant...
            </div>
        `;
    }
    
    try {
        const response = await fetch('/api/ai-rag/clear-vector-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                confirm_clear: true,
                include_collections: true
            })
        });
        
        const result = await response.json();
        
        if (response.ok && result.status === 'success') {
            console.log('✅ Vector Management Module: Global vector data cleared successfully');
            statusDiv.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    <strong>All Vector Data Cleared Successfully!</strong><br>
                    <small class="text-muted">
                        Message: ${result.message}<br>
                        All documents and embeddings have been removed from Qdrant.
                    </small>
                </div>
            `;
            
            // Refresh all displays to show empty state
            await refreshVectorDbInfo();
            await loadVectorDataStats();
        } else {
            console.error('❌ Vector Management Module: Failed to clear vector data:', result);
            statusDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Failed to Clear Vector Data:</strong><br>
                    <small class="text-muted">${result.error || result.detail || 'Unknown error'}</small>
                </div>
            `;
        }
        
    } catch (error) {
        console.error('❌ Vector Management Module: Error clearing vector data:', error);
        statusDiv.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                <strong>Error:</strong> Network error while clearing data<br>
                <small class="text-muted">Please try again or check server status</small>
            </div>
        `;
    }
}

/**
 * Show stored documents list
 */
export async function showStoredDocuments() {
    console.log('📄 Vector Management Module: Fetching stored documents...');
    
    const statusDiv = document.getElementById('data-management-status');
    if (statusDiv) {
        statusDiv.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-spinner fa-spin me-2"></i>
                Loading stored documents...
            </div>
        `;
    }
    
    try {
        const response = await fetch('/api/ai-rag/documents?limit=50');
        const data = await response.json();
        
        console.log('✅ Vector Management Module: Stored documents received:', data);
        
        if (data.success) {
            let docsHtml = `
                <div class="alert alert-info">
                    <h6><i class="fas fa-file-alt me-2"></i>Stored Documents in Qdrant</h6>
                    <p><strong>Total Documents:</strong> ${data.total_documents}</p>
                    <hr>
                    <h6>Document List:</h6>
                    <div class="table-responsive">
                        <table class="table table-sm table-striped">
                            <thead>
                                <tr>
                                    <th>File ID</th>
                                    <th>Project ID</th>
                                    <th>Content Type</th>
                                    <th>Document Type</th>
                                </tr>
                            </thead>
                            <tbody>
            `;
            
            data.documents.forEach(doc => {
                docsHtml += `
                    <tr>
                        <td><code>${doc.file_id}</code></td>
                        <td><small>${doc.project_id}</small></td>
                        <td><span class="badge bg-primary">${doc.content_type}</span></td>
                        <td><span class="badge bg-secondary">${doc.document_type}</span></td>
                    </tr>
                `;
            });
            
            docsHtml += `
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
            statusDiv.innerHTML = docsHtml;
        } else {
            statusDiv.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-info-circle me-2"></i>
                    Could not load documents: ${data.error || 'Unknown error'}
                </div>
            `;
        }
        
    } catch (error) {
        console.error('❌ Vector Management Module: Error fetching documents:', error);
        statusDiv.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Could not load documents: ${error.message || 'Network error'}
            </div>
        `;
    }
}

function updateBackupStatus(message) {
    const statusContainer = document.getElementById('backup-status');
    if (statusContainer) {
        statusContainer.innerHTML = `<div class="alert alert-info alert-sm">${message}</div>`;
    }
}

function updateDataManagementStatus(message) {
    const statusContainer = document.getElementById('data-management-status');
    if (statusContainer) {
        statusContainer.innerHTML = `<div class="alert alert-info alert-sm">${message}</div>`;
    }
}

function displayBackupHistory(history) {
    const statusContainer = document.getElementById('backup-status');
    if (statusContainer) {
        if (history && history.length > 0) {
            const historyHtml = history.map(backup => `
                <div class="alert alert-info alert-sm">
                    <strong>${backup.type}</strong> - ${backup.timestamp}
                    <br><small>Size: ${backup.size || 'Unknown'}</small>
                </div>
            `).join('');
            statusContainer.innerHTML = historyHtml;
        } else {
            statusContainer.innerHTML = '<div class="alert alert-warning alert-sm">No backup history found</div>';
        }
    }
} 