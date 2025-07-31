/**
 * Twin Registry Real-time Monitoring Module
 * Handles real-time updates, WebSocket connections, and live data streaming
 */

export default class TwinRegistryRealtime {
    constructor() {
        this.isInitialized = false;
        this.websocket = null;
        this.realtimeData = {
            twins: new Map(),
            events: [],
            connections: [],
            status: 'disconnected'
        };
        this.eventHandlers = new Map();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.config = {
            websocketUrl: 'ws://localhost:8080/ws/twin-registry',
            heartbeatInterval: 30000, // 30 seconds
            eventRetention: 1000, // Keep last 1000 events
            autoReconnect: true,
            enableHeartbeat: true
        };
        this.heartbeatInterval = null;
        this.lastHeartbeat = null;
    }

    /**
     * Initialize Real-time Monitoring
     */
    async init() {
        console.log('🔄 Initializing Twin Registry Real-time Monitoring...');

        try {
            // Setup event handlers
            this.setupEventHandlers();

            // Initialize WebSocket connection
            await this.initializeWebSocket();

            // Setup heartbeat
            this.setupHeartbeat();

            this.isInitialized = true;
            console.log('✅ Twin Registry Real-time Monitoring initialized');

        } catch (error) {
            console.error('❌ Twin Registry Real-time Monitoring initialization failed:', error);
            throw error;
        }
    }

    /**
     * Setup event handlers
     */
    setupEventHandlers() {
        // Twin registration events
        this.eventHandlers.set('twin_registered', (data) => {
            this.handleTwinRegistered(data);
        });

        this.eventHandlers.set('twin_updated', (data) => {
            this.handleTwinUpdated(data);
        });

        this.eventHandlers.set('twin_deleted', (data) => {
            this.handleTwinDeleted(data);
        });

        // Status change events
        this.eventHandlers.set('twin_status_changed', (data) => {
            this.handleTwinStatusChanged(data);
        });

        // Health events
        this.eventHandlers.set('health_update', (data) => {
            this.handleHealthUpdate(data);
        });

        // Performance events
        this.eventHandlers.set('performance_update', (data) => {
            this.handlePerformanceUpdate(data);
        });

        // System events
        this.eventHandlers.set('system_event', (data) => {
            this.handleSystemEvent(data);
        });

        // Connection events
        this.eventHandlers.set('connection_event', (data) => {
            this.handleConnectionEvent(data);
        });
    }

    /**
     * Initialize WebSocket connection
     */
    async initializeWebSocket() {
        try {
            this.websocket = new WebSocket(this.config.websocketUrl);
            
            this.websocket.onopen = () => {
                this.handleWebSocketOpen();
            };

            this.websocket.onmessage = (event) => {
                this.handleWebSocketMessage(event);
            };

            this.websocket.onclose = (event) => {
                this.handleWebSocketClose(event);
            };

            this.websocket.onerror = (error) => {
                this.handleWebSocketError(error);
            };

        } catch (error) {
            console.error('❌ Failed to initialize WebSocket:', error);
            throw error;
        }
    }

    /**
     * Setup heartbeat
     */
    setupHeartbeat() {
        if (!this.config.enableHeartbeat) {
            return;
        }

        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
        }

        this.heartbeatInterval = setInterval(() => {
            this.sendHeartbeat();
        }, this.config.heartbeatInterval);
    }

    /**
     * Handle WebSocket open
     */
    handleWebSocketOpen() {
        console.log('🔗 WebSocket connection established');
        this.realtimeData.status = 'connected';
        this.reconnectAttempts = 0;

        // Dispatch connection event
        window.dispatchEvent(new CustomEvent('twinRegistryRealtimeConnected', {
            detail: { timestamp: Date.now() }
        }));

        // Request initial data
        this.requestInitialData();
    }

    /**
     * Handle WebSocket message
     */
    handleWebSocketMessage(event) {
        try {
            const data = JSON.parse(event.data);
            this.processRealtimeEvent(data);
        } catch (error) {
            console.error('❌ Failed to parse WebSocket message:', error);
        }
    }

    /**
     * Handle WebSocket close
     */
    handleWebSocketClose(event) {
        console.log('🔌 WebSocket connection closed:', event.code, event.reason);
        this.realtimeData.status = 'disconnected';

        // Dispatch disconnection event
        window.dispatchEvent(new CustomEvent('twinRegistryRealtimeDisconnected', {
            detail: { 
                code: event.code, 
                reason: event.reason, 
                timestamp: Date.now() 
            }
        }));

        // Attempt reconnection if enabled
        if (this.config.autoReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.attemptReconnection();
        }
    }

    /**
     * Handle WebSocket error
     */
    handleWebSocketError(error) {
        console.error('❌ WebSocket error:', error);
        this.realtimeData.status = 'error';
    }

    /**
     * Process real-time event
     */
    processRealtimeEvent(data) {
        const { type, payload, timestamp } = data;

        // Add to events history
        this.realtimeData.events.push({
            type,
            payload,
            timestamp: timestamp || Date.now()
        });

        // Limit event history
        if (this.realtimeData.events.length > this.config.eventRetention) {
            this.realtimeData.events = this.realtimeData.events.slice(-this.config.eventRetention);
        }

        // Handle event based on type
        const handler = this.eventHandlers.get(type);
        if (handler) {
            handler(payload);
        } else {
            console.warn('⚠️ Unknown event type:', type);
        }

        // Dispatch general event
        window.dispatchEvent(new CustomEvent('twinRegistryRealtimeEvent', {
            detail: { type, payload, timestamp }
        }));
    }

    /**
     * Handle twin registered event
     */
    handleTwinRegistered(data) {
        const { twin } = data;
        this.realtimeData.twins.set(twin.id, twin);

        // Dispatch specific event
        window.dispatchEvent(new CustomEvent('twinRegistryTwinRegistered', {
            detail: { twin, timestamp: Date.now() }
        }));

        console.log('📝 Twin registered in real-time:', twin.id);
    }

    /**
     * Handle twin updated event
     */
    handleTwinUpdated(data) {
        const { twin } = data;
        this.realtimeData.twins.set(twin.id, twin);

        // Dispatch specific event
        window.dispatchEvent(new CustomEvent('twinRegistryTwinUpdated', {
            detail: { twin, timestamp: Date.now() }
        }));

        console.log('🔄 Twin updated in real-time:', twin.id);
    }

    /**
     * Handle twin deleted event
     */
    handleTwinDeleted(data) {
        const { twinId } = data;
        this.realtimeData.twins.delete(twinId);

        // Dispatch specific event
        window.dispatchEvent(new CustomEvent('twinRegistryTwinDeleted', {
            detail: { twinId, timestamp: Date.now() }
        }));

        console.log('🗑️ Twin deleted in real-time:', twinId);
    }

    /**
     * Handle twin status changed event
     */
    handleTwinStatusChanged(data) {
        const { twinId, oldStatus, newStatus } = data;
        const twin = this.realtimeData.twins.get(twinId);
        
        if (twin) {
            twin.status = newStatus;
            this.realtimeData.twins.set(twinId, twin);
        }

        // Dispatch specific event
        window.dispatchEvent(new CustomEvent('twinRegistryTwinStatusChanged', {
            detail: { twinId, oldStatus, newStatus, timestamp: Date.now() }
        }));

        console.log(`🔄 Twin status changed: ${twinId} ${oldStatus} → ${newStatus}`);
    }

    /**
     * Handle health update event
     */
    handleHealthUpdate(data) {
        // Dispatch specific event
        window.dispatchEvent(new CustomEvent('twinRegistryHealthUpdate', {
            detail: { healthData: data, timestamp: Date.now() }
        }));

        console.log('🏥 Health update received');
    }

    /**
     * Handle performance update event
     */
    handlePerformanceUpdate(data) {
        // Dispatch specific event
        window.dispatchEvent(new CustomEvent('twinRegistryPerformanceUpdate', {
            detail: { performanceData: data, timestamp: Date.now() }
        }));

        console.log('⚡ Performance update received');
    }

    /**
     * Handle system event
     */
    handleSystemEvent(data) {
        // Dispatch specific event
        window.dispatchEvent(new CustomEvent('twinRegistrySystemEvent', {
            detail: { systemEvent: data, timestamp: Date.now() }
        }));

        console.log('🔧 System event received:', data.type);
    }

    /**
     * Handle connection event
     */
    handleConnectionEvent(data) {
        this.realtimeData.connections.push({
            ...data,
            timestamp: Date.now()
        });

        // Limit connections history
        if (this.realtimeData.connections.length > 100) {
            this.realtimeData.connections = this.realtimeData.connections.slice(-100);
        }

        // Dispatch specific event
        window.dispatchEvent(new CustomEvent('twinRegistryConnectionEvent', {
            detail: { connectionEvent: data, timestamp: Date.now() }
        }));

        console.log('🔗 Connection event received:', data.type);
    }

    /**
     * Send heartbeat
     */
    sendHeartbeat() {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            const heartbeat = {
                type: 'heartbeat',
                timestamp: Date.now()
            };

            this.websocket.send(JSON.stringify(heartbeat));
            this.lastHeartbeat = Date.now();
        }
    }

    /**
     * Request initial data
     */
    requestInitialData() {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            const request = {
                type: 'request_initial_data',
                timestamp: Date.now()
            };

            this.websocket.send(JSON.stringify(request));
        }
    }

    /**
     * Attempt reconnection
     */
    attemptReconnection() {
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

        console.log(`🔄 Attempting reconnection ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${delay}ms`);

        setTimeout(async () => {
            try {
                await this.initializeWebSocket();
            } catch (error) {
                console.error('❌ Reconnection failed:', error);
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.attemptReconnection();
                }
            }
        }, delay);
    }

    /**
     * Send message to WebSocket
     */
    sendMessage(type, payload = {}) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            const message = {
                type,
                payload,
                timestamp: Date.now()
            };

            this.websocket.send(JSON.stringify(message));
            return true;
        } else {
            console.warn('⚠️ WebSocket not connected, cannot send message');
            return false;
        }
    }

    /**
     * Subscribe to twin updates
     */
    subscribeToTwin(twinId) {
        return this.sendMessage('subscribe_twin', { twinId });
    }

    /**
     * Unsubscribe from twin updates
     */
    unsubscribeFromTwin(twinId) {
        return this.sendMessage('unsubscribe_twin', { twinId });
    }

    /**
     * Subscribe to all twins
     */
    subscribeToAllTwins() {
        return this.sendMessage('subscribe_all_twins');
    }

    /**
     * Unsubscribe from all twins
     */
    unsubscribeFromAllTwins() {
        return this.sendMessage('unsubscribe_all_twins');
    }

    /**
     * Get real-time twin data
     */
    getRealtimeTwin(twinId) {
        return this.realtimeData.twins.get(twinId) || null;
    }

    /**
     * Get all real-time twins
     */
    getAllRealtimeTwins() {
        return Array.from(this.realtimeData.twins.values());
    }

    /**
     * Get real-time events
     */
    getRealtimeEvents(limit = 50) {
        return this.realtimeData.events.slice(-limit);
    }

    /**
     * Get connection status
     */
    getConnectionStatus() {
        return this.realtimeData.status;
    }

    /**
     * Get connection statistics
     */
    getConnectionStats() {
        return {
            status: this.realtimeData.status,
            reconnectAttempts: this.reconnectAttempts,
            lastHeartbeat: this.lastHeartbeat,
            eventCount: this.realtimeData.events.length,
            twinCount: this.realtimeData.twins.size,
            connectionCount: this.realtimeData.connections.length
        };
    }

    /**
     * Clear real-time data
     */
    clearRealtimeData() {
        this.realtimeData.twins.clear();
        this.realtimeData.events = [];
        this.realtimeData.connections = [];
    }

    /**
     * Update real-time configuration
     */
    updateConfiguration(newConfig) {
        this.config = { ...this.config, ...newConfig };
        
        if (newConfig.websocketUrl && this.websocket) {
            // Reconnect with new URL
            this.websocket.close();
            this.initializeWebSocket();
        }

        if (newConfig.enableHeartbeat !== undefined) {
            if (newConfig.enableHeartbeat) {
                this.setupHeartbeat();
            } else if (this.heartbeatInterval) {
                clearInterval(this.heartbeatInterval);
            }
        }
    }

    /**
     * Refresh real-time data
     */
    async refreshRealtimeData() {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.requestInitialData();
        }
    }

    /**
     * Destroy Real-time Monitoring
     */
    destroy() {
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }

        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
        }

        this.eventHandlers.clear();
        this.realtimeData.twins.clear();
        this.realtimeData.events = [];
        this.realtimeData.connections = [];

        this.isInitialized = false;
        console.log('🧹 Twin Registry Real-time Monitoring destroyed');
    }
} 