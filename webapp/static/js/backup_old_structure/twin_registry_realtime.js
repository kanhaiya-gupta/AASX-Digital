/**
 * Twin Registry Real-Time JavaScript
 * Phase 2.1: Real-Time Sync Foundation
 * Handles WebSocket connections and real-time twin updates
 */

class TwinRegistryRealtime {
    constructor() {
        this.websocket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1 second
        
        // Real-time data
        this.twinStatuses = {};
        this.subscribedTwins = new Set();
        
        // UI elements
        this.statusIndicator = null;
        this.realtimePanel = null;
        this.twinStatusCards = {};
        
        // Initialize
        this.init();
    }
    
    init() {
        console.log('🔄 Initializing Twin Registry Real-Time...');
        
        // Initialize UI elements
        this.initUI();
        
        // Connect to WebSocket
        this.connectWebSocket();
        
        // Set up periodic health checks
        this.startHealthChecks();
        
        console.log('✅ Twin Registry Real-Time initialized');
    }
    
    initUI() {
        // Create real-time status indicator
        this.createStatusIndicator();
        
        // Create real-time panel
        this.createRealtimePanel();
        
        // Update existing twin cards with real-time indicators
        this.updateTwinCards();
    }
    
    createStatusIndicator() {
        // Add real-time status indicator to the header
        const header = document.querySelector('.d-flex.justify-content-between.align-items-center');
        if (header) {
            const statusDiv = document.createElement('div');
            statusDiv.className = 'realtime-status-indicator';
            statusDiv.innerHTML = `
                <div class="d-flex align-items-center">
                    <span class="status-dot" id="realtimeStatusDot"></span>
                    <span class="status-text ms-2" id="realtimeStatusText">Connecting...</span>
                    <span class="connection-count ms-2 badge bg-secondary" id="connectionCount">0</span>
                </div>
            `;
            
            // Insert before the buttons
            const buttonsDiv = header.querySelector('.d-flex.gap-2');
            if (buttonsDiv) {
                header.insertBefore(statusDiv, buttonsDiv);
            }
            
            this.statusIndicator = statusDiv;
        }
    }
    
    createRealtimePanel() {
        // Create real-time monitoring panel
        const container = document.querySelector('.container-fluid');
        if (container) {
            const panel = document.createElement('div');
            panel.className = 'row mb-4';
            panel.id = 'realtimePanel';
            panel.innerHTML = `
                <div class="col-12">
                    <div class="card shadow">
                        <div class="card-header py-3 d-flex justify-content-between align-items-center">
                            <h6 class="m-0 font-weight-bold text-primary">
                                <i class="fas fa-broadcast-tower"></i>
                                Real-Time Twin Monitoring
                            </h6>
                            <div class="btn-group" role="group">
                                <button class="btn btn-sm btn-outline-primary" id="refreshRealtime">
                                    <i class="fas fa-sync-alt"></i> Refresh
                                </button>
                                <button class="btn btn-sm btn-outline-success" id="startAllSync">
                                    <i class="fas fa-play"></i> Start All Sync
                                </button>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="row" id="realtimeTwinStatus">
                                <!-- Real-time twin status cards will be inserted here -->
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Find the existing real-time monitoring section in the template
            const existingRealtimeSection = container.querySelector('#realtimePanelBody');
            if (existingRealtimeSection) {
                // If the real-time section already exists in the template, don't create a new one
                console.log('Real-time section already exists in template, skipping dynamic creation');
                this.realtimePanel = existingRealtimeSection.closest('.row');
                return;
            }
            
            // Only insert if we don't have an existing real-time section
            // Look for the twin registry management section to insert after it
            const twinRegistrySection = container.querySelector('#twinRegistryTable');
            if (twinRegistrySection) {
                const twinRegistryRow = twinRegistrySection.closest('.row');
                if (twinRegistryRow && twinRegistryRow.parentNode) {
                    twinRegistryRow.parentNode.insertBefore(panel, twinRegistryRow.nextSibling);
                }
            } else {
                // Fallback: append to the end of the container
                container.appendChild(panel);
            }
            
            this.realtimePanel = panel;
            
            // Bind event handlers
            this.bindRealtimeEvents();
        }
    }
    
    bindRealtimeEvents() {
        // Refresh real-time data
        document.getElementById('refreshRealtime')?.addEventListener('click', () => {
            this.refreshRealtimeData();
        });
        
        // Start all sync
        document.getElementById('startAllSync')?.addEventListener('click', () => {
            this.startAllTwinSync();
        });
    }
    
    connectWebSocket() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/twin-registry/ws/twin-sync`;
            
            console.log('🔌 Connecting to WebSocket:', wsUrl);
            
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = (event) => {
                console.log('✅ WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.reconnectDelay = 1000;
                this.updateConnectionStatus('connected');
                
                // Subscribe to all existing twins
                this.subscribeToAllTwins();
            };
            
            this.websocket.onmessage = (event) => {
                this.handleWebSocketMessage(event.data);
            };
            
            this.websocket.onclose = (event) => {
                console.log('❌ WebSocket disconnected:', event.code, event.reason);
                this.isConnected = false;
                this.updateConnectionStatus('disconnected');
                
                // Attempt to reconnect
                this.attemptReconnect();
            };
            
            this.websocket.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                this.updateConnectionStatus('error');
            };
            
        } catch (error) {
            console.error('❌ Error connecting to WebSocket:', error);
            this.updateConnectionStatus('error');
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`🔄 Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            
            setTimeout(() => {
                this.connectWebSocket();
            }, this.reconnectDelay);
            
            // Exponential backoff
            this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000);
        } else {
            console.error('❌ Max reconnection attempts reached');
            this.updateConnectionStatus('failed');
        }
    }
    
    handleWebSocketMessage(data) {
        try {
            const message = JSON.parse(data);
            console.log('📨 WebSocket message received:', message.type);
            
            switch (message.type) {
                case 'initial_status':
                    this.handleInitialStatus(message.data);
                    break;
                    
                case 'twin_update':
                    this.handleTwinUpdate(message.twin_id, message.data);
                    break;
                    
                case 'subscribed':
                    console.log(`✅ Subscribed to twin: ${message.twin_id}`);
                    break;
                    
                case 'unsubscribed':
                    console.log(`❌ Unsubscribed from twin: ${message.twin_id}`);
                    break;
                    
                case 'sync_started':
                    this.handleSyncStarted(message.twin_id);
                    break;
                    
                case 'pong':
                    // Handle ping/pong for connection health
                    break;
                    
                default:
                    console.log('📨 Unknown message type:', message.type);
            }
            
        } catch (error) {
            console.error('❌ Error parsing WebSocket message:', error);
        }
    }
    
    handleInitialStatus(data) {
        console.log('📊 Received initial status for', data.twins.length, 'twins');
        console.log('📊 Twin data:', data.twins);
        
        // Update twin statuses
        data.twins.forEach(twin => {
            this.twinStatuses[twin.twin_id] = twin;
            console.log(`📊 Twin ${twin.twin_id}: status=${twin.sync_status}, subscribers=${twin.subscribers}, data_points=${twin.data_points}`);
        });

        // Subscribe to all actual twins after loading statuses
        this.subscribeToAllTwins();
        
        // Update UI
        this.updateRealtimePanel();
        this.updateTwinCards();
        
        // Update connection status to reflect current subscriber count
        this.updateConnectionStatus('connected');
    }
    
    handleTwinUpdate(twinId, data) {
        console.log(`🔄 Twin update for ${twinId}:`, data.status);
        
        // Update twin status
        if (twinId in this.twinStatuses) {
            this.twinStatuses[twinId] = { ...this.twinStatuses[twinId], ...data };
        } else {
            this.twinStatuses[twinId] = data;
        }
        
        // Update UI
        this.updateTwinCard(twinId);
        this.updateRealtimePanel();
    }
    
    handleSyncStarted(twinId) {
        console.log(`🔄 Sync started for twin: ${twinId}`);
        this.showNotification(`Sync started for twin ${twinId}`, 'info');
    }
    
    subscribeToAllTwins() {
        // Subscribe to all twins that are available in the real-time status
        Object.keys(this.twinStatuses).forEach(twinId => {
            this.subscribeToTwin(twinId);
        });
    }
    
    subscribeToTwin(twinId) {
        if (this.isConnected && this.websocket) {
            const message = {
                type: 'subscribe',
                twin_id: twinId
            };
            
            this.websocket.send(JSON.stringify(message));
            this.subscribedTwins.add(twinId);
            this.updateConnectionStatus('connected'); // Update status after subscribing
        }
    }
    
    unsubscribeFromTwin(twinId) {
        if (this.isConnected && this.websocket) {
            const message = {
                type: 'unsubscribe',
                twin_id: twinId
            };
            
            this.websocket.send(JSON.stringify(message));
            this.subscribedTwins.delete(twinId);
            this.updateConnectionStatus('disconnected'); // Update status after unsubscribing
        }
    }
    
    updateConnectionStatus(status) {
        console.log('🔄 Updating connection status:', status, 'Subscribers:', this.subscribedTwins.size);
        
        const statusDot = document.getElementById('realtimeStatusDot');
        const statusText = document.getElementById('realtimeStatusText');
        const connectionCount = document.getElementById('connectionCount');
        
        // Also update the real-time monitoring panel elements
        const realtimeStatus = document.getElementById('realtimeStatus');
        const realtimeStatusText = document.getElementById('realtimeStatusText');
        const realtimeStatusDetails = document.getElementById('realtimeStatusDetails');
        const subscriberCount = document.getElementById('subscriberCount');
        const lastUpdate = document.getElementById('lastUpdate');
        
        console.log('🔍 Found elements:', {
            realtimeStatusText: !!realtimeStatusText,
            realtimeStatusDetails: !!realtimeStatusDetails,
            subscriberCount: !!subscriberCount,
            lastUpdate: !!lastUpdate
        });
        
        if (statusDot && statusText) {
            statusDot.className = 'status-dot';
            
            switch (status) {
                case 'connected':
                    statusDot.classList.add('connected');
                    statusText.textContent = 'Real-Time Connected';
                    if (realtimeStatusText) realtimeStatusText.textContent = 'Connected';
                    if (realtimeStatusDetails) realtimeStatusDetails.textContent = 'Real-time monitoring active';
                    break;
                    
                case 'disconnected':
                    statusDot.classList.add('disconnected');
                    statusText.textContent = 'Disconnected';
                    if (realtimeStatusText) realtimeStatusText.textContent = 'Disconnected';
                    if (realtimeStatusDetails) realtimeStatusDetails.textContent = 'Connection lost';
                    break;
                    
                case 'error':
                    statusDot.classList.add('error');
                    statusText.textContent = 'Connection Error';
                    if (realtimeStatusText) realtimeStatusText.textContent = 'Error';
                    if (realtimeStatusDetails) realtimeStatusDetails.textContent = 'Connection error occurred';
                    break;
                    
                case 'failed':
                    statusDot.classList.add('failed');
                    statusText.textContent = 'Connection Failed';
                    if (realtimeStatusText) realtimeStatusText.textContent = 'Failed';
                    if (realtimeStatusDetails) realtimeStatusDetails.textContent = 'Connection failed';
                    break;
                    
                default:
                    statusDot.classList.add('connecting');
                    statusText.textContent = 'Connecting...';
                    if (realtimeStatusText) realtimeStatusText.textContent = 'Connecting...';
                    if (realtimeStatusDetails) realtimeStatusDetails.textContent = 'Establishing connection';
            }
        }
        
        // Update subscriber count in both header and panel
        const subscriberCountValue = this.subscribedTwins.size;
        console.log('📊 Updating subscriber count to:', subscriberCountValue);
        
        if (connectionCount) {
            connectionCount.textContent = subscriberCountValue;
        }
        if (subscriberCount) {
            subscriberCount.textContent = subscriberCountValue;
        }
        
        // Update last update timestamp
        const now = new Date().toLocaleTimeString();
        if (lastUpdate) {
            lastUpdate.textContent = now;
        }
        
        console.log('✅ Connection status updated');
    }
    
    updateRealtimePanel() {
        console.log('🔄 Updating real-time panel...');
        const container = document.getElementById('realtimeTwinStatus');
        if (!container) {
            console.log('❌ Real-time panel container not found');
            return;
        }
        
        // Ensure the container is visible even if the panel is collapsed
        // This allows the JavaScript to update the content
        const panelBody = document.getElementById('realtimePanelBody');
        if (panelBody && panelBody.style.display === 'none') {
            console.log('📋 Real-time panel is collapsed, but updating content anyway');
        }
        
        console.log(`🔄 Creating ${Object.keys(this.twinStatuses).length} twin cards`);
        container.innerHTML = '';
        
        Object.values(this.twinStatuses).forEach(twin => {
            console.log(`🔄 Adding card for twin: ${twin.twin_id}`);
            const card = this.createTwinStatusCard(twin);
            container.appendChild(card);
        });
        
        if (Object.keys(this.twinStatuses).length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center text-muted">
                    <i class="fas fa-info-circle fa-2x mb-3"></i>
                    <p>No twins available for real-time monitoring</p>
                </div>
            `;
        }
        
        console.log('✅ Real-time panel updated');
    }
    
    createTwinStatusCard(twin) {
        console.log(`🎴 Creating card for twin ${twin.twin_id}: subscribers=${twin.subscribers}, data_points=${twin.data_points}`);
        
        const card = document.createElement('div');
        card.className = 'col-md-4 col-lg-3 mb-3';
        card.id = `realtime-card-${twin.twin_id}`;
        
        const statusClass = this.getStatusClass(twin.sync_status);
        const statusIcon = this.getStatusIcon(twin.sync_status);
        
        // Use twin_name if available, otherwise use a shortened twin_id
        const displayName = twin.twin_name || this.shortenTwinId(twin.twin_id);
        
        card.innerHTML = `
            <div class="card h-100 border-${statusClass}">
                <div class="card-body p-3">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="card-title mb-0 text-truncate" title="${twin.twin_name || twin.twin_id}">${displayName}</h6>
                        <span class="badge bg-${statusClass}">${twin.sync_status}</span>
                    </div>
                    <p class="card-text small text-muted mb-2">
                        <i class="fas fa-cube me-1"></i>${this.shortenTwinId(twin.twin_id)}
                    </p>
                    <div class="row text-center">
                        <div class="col-6">
                            <small class="text-muted">Data Points</small>
                            <div class="fw-bold">${this.formatNumber(twin.data_points || 0)}</div>
                        </div>
                        <div class="col-6">
                            <small class="text-muted">Subscribers</small>
                            <div class="fw-bold">${twin.subscribers || 0}</div>
                        </div>
                    </div>
                    <div class="mt-2">
                        <button class="btn btn-sm btn-outline-primary w-100 sync-twin-btn" 
                                data-twin-id="${twin.twin_id}">
                            <i class="fas fa-sync-alt"></i> Sync Now
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Bind sync button
        const syncBtn = card.querySelector('.sync-twin-btn');
        syncBtn.addEventListener('click', () => {
            this.startTwinSync(twin.twin_id);
        });
        
        return card;
    }
    
    updateTwinCards() {
        // Update existing twin registry table with real-time indicators
        const twinRows = document.querySelectorAll('#twinRegistryTable tbody tr');
        twinRows.forEach(row => {
            const twinId = row.querySelector('[data-id]')?.getAttribute('data-id');
            if (twinId && this.twinStatuses[twinId]) {
                this.updateTwinCard(twinId);
            }
        });
    }
    
    updateTwinCard(twinId) {
        const twin = this.twinStatuses[twinId];
        if (!twin) return;
        
        // Update status in the main table
        const row = document.querySelector(`#twinRegistryTable tbody tr [data-id="${twinId}"]`)?.closest('tr');
        if (row) {
            const statusCell = row.querySelector('td:nth-child(4)');
            if (statusCell) {
                const statusClass = this.getStatusClass(twin.sync_status);
                statusCell.innerHTML = `<span class="badge bg-${statusClass}">${twin.sync_status}</span>`;
            }
        }
        
        // Update real-time card if it exists
        const realtimeCard = document.getElementById(`realtime-card-${twinId}`);
        if (realtimeCard) {
            const newCard = this.createTwinStatusCard(twin);
            realtimeCard.replaceWith(newCard);
        }
    }
    
    getStatusClass(status) {
        switch (status) {
            case 'online': return 'success';
            case 'syncing': return 'warning';
            case 'error': return 'danger';
            case 'offline': return 'secondary';
            default: return 'info';
        }
    }
    
    getStatusIcon(status) {
        switch (status) {
            case 'online': return 'fas fa-check-circle';
            case 'syncing': return 'fas fa-sync-alt fa-spin';
            case 'error': return 'fas fa-exclamation-triangle';
            case 'offline': return 'fas fa-times-circle';
            default: return 'fas fa-question-circle';
        }
    }
    
    startTwinSync(twinId) {
        if (!this.isConnected) {
            this.showNotification('Not connected to real-time service', 'error');
            return;
        }
        
        const message = {
            type: 'sync_request',
            twin_id: twinId
        };
        
        this.websocket.send(JSON.stringify(message));
        this.showNotification(`Sync requested for twin ${twinId}`, 'info');
    }
    
    startAllTwinSync() {
        const twinIds = Object.keys(this.twinStatuses);
        if (twinIds.length === 0) {
            this.showNotification('No twins available for sync', 'warning');
            return;
        }
        
        twinIds.forEach(twinId => {
            this.startTwinSync(twinId);
        });
        
        this.showNotification(`Sync requested for ${twinIds.length} twins`, 'info');
    }
    
    refreshRealtimeData() {
        // Refresh real-time data via API
        fetch('/twin-registry/api/twins/realtime/status')
            .then(response => response.json())
            .then(data => {
                this.handleInitialStatus(data);
                this.showNotification('Real-time data refreshed', 'success');
            })
            .catch(error => {
                console.error('Error refreshing real-time data:', error);
                this.showNotification('Error refreshing data', 'error');
            });
    }
    
    startHealthChecks() {
        // Send periodic ping to keep connection alive
        setInterval(() => {
            if (this.isConnected && this.websocket) {
                this.websocket.send(JSON.stringify({ type: 'ping' }));
            }
        }, 30000); // Every 30 seconds
    }
    
    showNotification(message, type) {
        if (window.AASXFramework && window.AASXFramework.showNotification) {
            window.AASXFramework.showNotification(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
    
    disconnect() {
        if (this.websocket) {
            this.websocket.close();
        }
    }

    shortenTwinId(twinId) {
        // Shorten long twin IDs for display
        if (twinId.length > 20) {
            return twinId.substring(0, 17) + '...';
        }
        return twinId;
    }

    formatNumber(num) {
        // Format large numbers with K, M suffixes
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }
}

// Initialize real-time functionality when DOM is ready
$(document).ready(function() {
    console.log('🚀 Initializing Twin Registry Real-Time...');
    window.twinRegistryRealtime = new TwinRegistryRealtime();
});

// Add CSS for real-time indicators
const realtimeCSS = `
<style>
.realtime-status-indicator {
    display: flex;
    align-items: center;
    padding: 0.5rem 1rem;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    backdrop-filter: blur(10px);
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #6c757d;
    transition: all 0.3s ease;
}

.status-dot.connected {
    background: #28a745;
    box-shadow: 0 0 10px rgba(40, 167, 69, 0.5);
}

.status-dot.disconnected {
    background: #ffc107;
    box-shadow: 0 0 10px rgba(255, 193, 7, 0.5);
}

.status-dot.error {
    background: #dc3545;
    box-shadow: 0 0 10px rgba(220, 53, 69, 0.5);
}

.status-dot.failed {
    background: #6c757d;
    box-shadow: 0 0 10px rgba(108, 117, 125, 0.5);
}

.status-dot.connecting {
    background: #17a2b8;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

.status-text {
    font-size: 0.875rem;
    font-weight: 500;
    color: white;
}

.connection-count {
    font-size: 0.75rem;
}

#realtimePanel .card {
    transition: all 0.3s ease;
}

#realtimePanel .card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.sync-twin-btn {
    transition: all 0.3s ease;
}

.sync-twin-btn:hover {
    transform: scale(1.05);
}
</style>
`;

document.head.insertAdjacentHTML('beforeend', realtimeCSS); 