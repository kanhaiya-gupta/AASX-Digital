/**
 * Integration Tab Component - World Class Edition
 * ES6 Class-based implementation with central authentication integration
 * Features sophisticated cross-module integration, data flow monitoring, and system connectivity
 */

import { AuthManager } from '../../auth/auth_manager.js';
import { Logger } from '../../utils/logger.js';
import { ApiClient } from '../../api/api_client.js';

class KGIntegrationComponent {
    constructor() {
        this.authManager = new AuthManager();
        this.logger = new Logger('KGIntegrationComponent');
        this.apiClient = new ApiClient();
        
        this.integrations = {};
        this.dataFlowData = [];
        this.monitoringInterval = null;
        this.isInitialized = false;
        this.isTabActive = false;
        
        // Integration statuses
        this.STATUS = {
            CONNECTED: 'connected',
            DISCONNECTED: 'disconnected',
            LIMITED: 'limited',
            ERROR: 'error',
            PENDING: 'pending'
        };
        
        // Module types
        this.MODULE_TYPES = {
            AASX_ETL: 'aasx_etl',
            TWIN_REGISTRY: 'twin_registry',
            AI_RAG: 'ai_rag',
            NEO4J: 'neo4j',
            EXTERNAL_API: 'external_api'
        };
        
        // Mock data for demonstration
        this.mockIntegrations = {
            [this.MODULE_TYPES.AASX_ETL]: {
                id: 'aasx_etl_001',
                name: 'AASX-ETL Module',
                type: this.MODULE_TYPES.AASX_ETL,
                status: this.STATUS.CONNECTED,
                connectionTime: new Date().toISOString(),
                lastSync: new Date(Date.now() - 5 * 60 * 1000).toISOString(), // 5 minutes ago
                metrics: {
                    filesProcessed: 156,
                    dataTransferred: '2.3 GB',
                    syncFrequency: '5 minutes',
                    errorRate: 0.02
                },
                config: {
                    endpoint: 'http://localhost:8000/api/aasx',
                    syncInterval: 300,
                    batchSize: 1000,
                    compression: true
                }
            },
            [this.MODULE_TYPES.TWIN_REGISTRY]: {
                id: 'twin_registry_001',
                name: 'Twin Registry Module',
                type: this.MODULE_TYPES.TWIN_REGISTRY,
                status: this.STATUS.CONNECTED,
                connectionTime: new Date().toISOString(),
                lastSync: new Date(Date.now() - 10 * 60 * 1000).toISOString(), // 10 minutes ago
                metrics: {
                    activeTwins: 89,
                    dataTransferred: '1.8 GB',
                    syncFrequency: '10 minutes',
                    errorRate: 0.01
                },
                config: {
                    endpoint: 'http://localhost:8000/api/twin-registry',
                    syncInterval: 600,
                    batchSize: 500,
                    compression: true
                }
            },
            [this.MODULE_TYPES.AI_RAG]: {
                id: 'ai_rag_001',
                name: 'AI/RAG Module',
                type: this.MODULE_TYPES.AI_RAG,
                status: this.STATUS.LIMITED,
                connectionTime: new Date().toISOString(),
                lastSync: new Date(Date.now() - 30 * 60 * 1000).toISOString(), // 30 minutes ago
                metrics: {
                    aiModels: 3,
                    dataTransferred: '450 MB',
                    syncFrequency: '30 minutes',
                    errorRate: 0.15
                },
                config: {
                    endpoint: 'http://localhost:8000/api/ai-rag',
                    syncInterval: 1800,
                    batchSize: 100,
                    compression: false
                }
            }
        };
        
        // Mock logs data
        this.mockLogs = [
            {
                timestamp: new Date().toISOString(),
                level: 'info',
                module: 'aasx_etl',
                message: 'Data synchronization completed successfully',
                details: { filesProcessed: 12, dataSize: '45 MB' }
            },
            {
                timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
                level: 'warning',
                module: 'twin_registry',
                message: 'High latency detected in twin registry connection',
                details: { latency: '2.3s', threshold: '1.0s' }
            },
            {
                timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
                level: 'error',
                module: 'ai_rag',
                message: 'Failed to establish connection with AI service',
                details: { errorCode: 'CONNECTION_TIMEOUT', retryCount: 3 }
            }
        ];
        
        // Initialize the component
        this.init();
    }
    
    /**
     * Initialize the Integration Component
     */
    async init() {
        try {
            // Check authentication
            if (!await this.authManager.isAuthenticated()) {
                this.logger.warn('User not authenticated, redirecting to login');
                window.location.href = '/login';
                return;
            }
            
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.initializeComponent());
            } else {
                this.initializeComponent();
            }
            
        } catch (error) {
            this.logger.error('Failed to initialize Integration Component:', error);
        }
    }
    
    /**
     * Initialize component functionality
     */
    async initializeComponent() {
        if (this.isInitialized) return;
        
        this.logger.info('🔗 Initializing Integration Component');
        
        try {
            // Load integrations
            await this.loadIntegrations();
            
            // Set up event listeners
            this.initEventListeners();
            
            // Start monitoring
            this.startMonitoring();
            
            this.isInitialized = true;
            this.logger.info('✅ Integration Component initialized');
            
        } catch (error) {
            this.logger.error('Failed to initialize Integration Component:', error);
        }
    }
    
    /**
     * Initialize event listeners
     */
    initEventListeners() {
        // Integration management buttons
        const createBtn = document.getElementById('create-integration-btn');
        if (createBtn) {
            createBtn.addEventListener('click', () => this.showCreateIntegrationModal());
        }
        
        const refreshBtn = document.getElementById('refresh-integrations-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshIntegrations());
        }
        
        const dataFlowBtn = document.getElementById('refresh-dataflow-btn');
        if (dataFlowBtn) {
            dataFlowBtn.addEventListener('click', () => this.refreshDataFlow());
        }
        
        // Configuration buttons
        const aasxConfigBtn = document.getElementById('configure-aasx-btn');
        if (aasxConfigBtn) {
            aasxConfigBtn.addEventListener('click', () => this.configureIntegration('aasx_etl'));
        }
        
        const twinConfigBtn = document.getElementById('configure-twin-btn');
        if (twinConfigBtn) {
            twinConfigBtn.addEventListener('click', () => this.configureIntegration('twin_registry'));
        }
        
        const aiConfigBtn = document.getElementById('configure-ai-btn');
        if (aiConfigBtn) {
            aiConfigBtn.addEventListener('click', () => this.configureIntegration('ai_rag'));
        }
        
        // Form submissions
        const integrationForm = document.getElementById('integration-form');
        if (integrationForm) {
            integrationForm.addEventListener('submit', (e) => this.handleIntegrationSubmit(e));
        }
    }
    
    /**
     * Load integrations from API
     */
    async loadIntegrations() {
        try {
            const response = await this.apiClient.get('/api/integrations/list', {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.integrations = response.data.integrations || {};
            } else {
                // Fallback to mock data
                this.integrations = { ...this.mockIntegrations };
            }
            
            this.updateIntegrationsDisplay();
            
        } catch (error) {
            this.logger.error('Failed to load integrations, using mock data:', error);
            this.integrations = { ...this.mockIntegrations };
            this.updateIntegrationsDisplay();
        }
    }
    
    /**
     * Update integrations display
     */
    updateIntegrationsDisplay() {
        const integrationsContainer = document.getElementById('integrations-container');
        if (!integrationsContainer) return;
        
        let integrationsHTML = '';
        
        Object.values(this.integrations).forEach(integration => {
            const statusClass = this.getStatusClass(integration.status);
            const lastSync = new Date(integration.lastSync).toLocaleString();
            
            integrationsHTML += `
                <div class="integration-item card mb-3" data-integration-id="${integration.id}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1">
                                <h6 class="card-title">${integration.name}</h6>
                                <div class="integration-meta mb-2">
                                    <span class="badge bg-${statusClass} me-2">${integration.status}</span>
                                    <small class="text-muted">
                                        Last sync: ${lastSync} | 
                                        Files: ${integration.metrics.filesProcessed || 0} | 
                                        Data: ${integration.metrics.dataTransferred || '0 MB'}
                                    </small>
                                </div>
                                <div class="integration-metrics">
                                    <small class="text-muted">
                                        Sync Frequency: ${integration.metrics.syncFrequency} | 
                                        Error Rate: ${(integration.metrics.errorRate * 100).toFixed(1)}%
                                    </small>
                                </div>
                            </div>
                            <div class="btn-group btn-group-sm">
                                <button class="btn btn-outline-primary btn-sm" onclick="kgIntegration.configureIntegration('${integration.type}')">
                                    <i class="fas fa-cog"></i>
                                </button>
                                <button class="btn btn-outline-success btn-sm" onclick="kgIntegration.testIntegrationConnection('${integration.type}')">
                                    <i class="fas fa-plug"></i>
                                </button>
                                <button class="btn btn-outline-info btn-sm" onclick="kgIntegration.viewIntegrationLogs('${integration.type}')">
                                    <i class="fas fa-list"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        integrationsContainer.innerHTML = integrationsHTML;
    }
    
    /**
     * Get status class for styling
     */
    getStatusClass(status) {
        switch (status) {
            case this.STATUS.CONNECTED: return 'success';
            case this.STATUS.LIMITED: return 'warning';
            case this.STATUS.ERROR: return 'danger';
            case this.STATUS.PENDING: return 'info';
            default: return 'secondary';
        }
    }
    
    /**
     * Show create integration modal
     */
    showCreateIntegrationModal() {
        try {
            this.logger.info('📝 Showing create integration modal');
            
            // Create modal HTML
            const modalHTML = `
                <div class="modal fade" id="createIntegrationModal" tabindex="-1" aria-labelledby="createIntegrationModalLabel" aria-hidden="true">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="createIntegrationModalLabel">Create New Integration</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <form id="integration-form">
                                    <div class="row">
                                        <div class="col-md-6">
                                            <div class="mb-3">
                                                <label for="integration-name" class="form-label">Integration Name</label>
                                                <input type="text" class="form-control" id="integration-name" required>
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="mb-3">
                                                <label for="integration-type" class="form-label">Module Type</label>
                                                <select class="form-select" id="integration-type" required>
                                                    <option value="">Select type...</option>
                                                    <option value="aasx_etl">AASX-ETL</option>
                                                    <option value="twin_registry">Twin Registry</option>
                                                    <option value="ai_rag">AI/RAG</option>
                                                    <option value="external_api">External API</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="mb-3">
                                        <label for="integration-endpoint" class="form-label">Endpoint URL</label>
                                        <input type="url" class="form-control" id="integration-endpoint" required>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-6">
                                            <div class="mb-3">
                                                <label for="integration-sync-interval" class="form-label">Sync Interval (seconds)</label>
                                                <input type="number" class="form-control" id="integration-sync-interval" value="300" min="60">
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="mb-3">
                                                <label for="integration-batch-size" class="form-label">Batch Size</label>
                                                <input type="number" class="form-control" id="integration-batch-size" value="1000" min="1">
                                            </div>
                                        </div>
                                    </div>
                                    <div class="mb-3">
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" id="integration-compression" checked>
                                            <label class="form-check-label" for="integration-compression">
                                                Enable compression
                                            </label>
                                        </div>
                                    </div>
                                </form>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                <button type="submit" form="integration-form" class="btn btn-primary">Create Integration</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Remove existing modal if present
            const existingModal = document.getElementById('createIntegrationModal');
            if (existingModal) {
                existingModal.remove();
            }
            
            // Add new modal
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('createIntegrationModal'));
            modal.show();
            
            // Clean up after modal is hidden
            document.getElementById('createIntegrationModal').addEventListener('hidden.bs.modal', function() {
                this.remove();
            });
            
        } catch (error) {
            this.logger.error('Failed to show create integration modal:', error);
            this.showError('Failed to show create integration modal');
        }
    }
    
    /**
     * Handle integration form submission
     */
    async handleIntegrationSubmit(event) {
        event.preventDefault();
        
        try {
            const formData = new FormData(event.target);
            const integrationData = {
                name: formData.get('integration-name') || document.getElementById('integration-name').value,
                type: formData.get('integration-type') || document.getElementById('integration-type').value,
                endpoint: formData.get('integration-endpoint') || document.getElementById('integration-endpoint').value,
                config: {
                    syncInterval: parseInt(document.getElementById('integration-sync-interval').value) || 300,
                    batchSize: parseInt(document.getElementById('integration-batch-size').value) || 1000,
                    compression: document.getElementById('integration-compression').checked
                }
            };
            
            const response = await this.apiClient.post('/api/integrations/create', integrationData, {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.showSuccess('Integration created successfully');
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('createIntegrationModal'));
                if (modal) {
                    modal.hide();
                }
                
                // Refresh integrations
                await this.loadIntegrations();
                
            } else {
                this.showError(response.message || 'Failed to create integration');
            }
            
        } catch (error) {
            this.logger.error('Failed to create integration:', error);
            this.showError('Failed to create integration');
        }
    }
    
    /**
     * Configure integration
     */
    async configureIntegration(moduleType) {
        try {
            this.logger.info(`⚙️ Configuring integration: ${moduleType}`);
            
            const integration = this.integrations[moduleType];
            if (!integration) {
                this.showError('Integration not found');
                return;
            }
            
            // Show configuration modal
            this.showConfigurationModal(integration);
            
        } catch (error) {
            this.logger.error('Failed to configure integration:', error);
            this.showError('Failed to configure integration');
        }
    }
    
    /**
     * Show configuration modal
     */
    showConfigurationModal(integration) {
        try {
            const modalHTML = `
                <div class="modal fade" id="configIntegrationModal" tabindex="-1" aria-labelledby="configIntegrationModalLabel" aria-hidden="true">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="configIntegrationModalLabel">Configure ${integration.name}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <form id="config-form">
                                    <div class="mb-3">
                                        <label for="config-endpoint" class="form-label">Endpoint URL</label>
                                        <input type="url" class="form-control" id="config-endpoint" value="${integration.config.endpoint}" required>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-6">
                                            <div class="mb-3">
                                                <label for="config-sync-interval" class="form-label">Sync Interval (seconds)</label>
                                                <input type="number" class="form-control" id="config-sync-interval" value="${integration.config.syncInterval}" min="60">
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="mb-3">
                                                <label for="config-batch-size" class="form-label">Batch Size</label>
                                                <input type="number" class="form-control" id="config-batch-size" value="${integration.config.batchSize}" min="1">
                                            </div>
                                        </div>
                                    </div>
                                    <div class="mb-3">
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" id="config-compression" ${integration.config.compression ? 'checked' : ''}>
                                            <label class="form-check-label" for="config-compression">
                                                Enable compression
                                            </label>
                                        </div>
                                    </div>
                                </form>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                <button type="button" class="btn btn-primary" onclick="kgIntegration.saveIntegrationConfig('${integration.type}')">Save Configuration</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Remove existing modal if present
            const existingModal = document.getElementById('configIntegrationModal');
            if (existingModal) {
                existingModal.remove();
            }
            
            // Add new modal
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('configIntegrationModal'));
            modal.show();
            
            // Clean up after modal is hidden
            document.getElementById('configIntegrationModal').addEventListener('hidden.bs.modal', function() {
                this.remove();
            });
            
        } catch (error) {
            this.logger.error('Failed to show configuration modal:', error);
            this.showError('Failed to show configuration modal');
        }
    }
    
    /**
     * Save integration configuration
     */
    async saveIntegrationConfig(moduleType) {
        try {
            this.logger.info(`💾 Saving configuration for: ${moduleType}`);
            
            const integration = this.integrations[moduleType];
            if (!integration) {
                this.showError('Integration not found');
                return;
            }
            
            const configData = {
                endpoint: document.getElementById('config-endpoint').value,
                syncInterval: parseInt(document.getElementById('config-sync-interval').value),
                batchSize: parseInt(document.getElementById('config-batch-size').value),
                compression: document.getElementById('config-compression').checked
            };
            
            const response = await this.apiClient.put(`/api/integrations/${integration.id}/config`, configData, {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                // Update local integration
                integration.config = configData;
                integration.config.endpoint = configData.endpoint;
                
                this.showSuccess('Configuration saved successfully');
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('configIntegrationModal'));
                if (modal) {
                    modal.hide();
                }
                
                // Update display
                this.updateIntegrationsDisplay();
                
            } else {
                this.showError(response.message || 'Failed to save configuration');
            }
            
        } catch (error) {
            this.logger.error('Failed to save integration configuration:', error);
            this.showError('Failed to save configuration');
        }
    }
    
    /**
     * Test integration connection
     */
    async testIntegrationConnection(moduleType) {
        try {
            this.logger.info(`🔌 Testing connection for: ${moduleType}`);
            
            const integration = this.integrations[moduleType];
            if (!integration) {
                this.showError('Integration not found');
                return;
            }
            
            const response = await this.apiClient.post(`/api/integrations/${integration.id}/test`, {}, {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.showSuccess('Connection test successful');
                
                // Update integration status
                integration.status = this.STATUS.CONNECTED;
                integration.lastSync = new Date().toISOString();
                
                // Update display
                this.updateIntegrationsDisplay();
                
            } else {
                this.showError(response.message || 'Connection test failed');
                
                // Update integration status
                integration.status = this.STATUS.ERROR;
                
                // Update display
                this.updateIntegrationsDisplay();
            }
            
        } catch (error) {
            this.logger.error('Failed to test integration connection:', error);
            this.showError('Connection test failed');
        }
    }
    
    /**
     * View integration logs
     */
    async viewIntegrationLogs(moduleType) {
        try {
            this.logger.info(`📋 Viewing logs for: ${moduleType}`);
            
            const integration = this.integrations[moduleType];
            if (!integration) {
                this.showError('Integration not found');
                return;
            }
            
            // Show logs modal
            this.showLogsModal(integration);
            
        } catch (error) {
            this.logger.error('Failed to view integration logs:', error);
            this.showError('Failed to view logs');
        }
    }
    
    /**
     * Show logs modal
     */
    showLogsModal(integration) {
        try {
            const logs = this.mockLogs.filter(log => log.module === integration.type);
            
            let logsHTML = '';
            if (logs.length === 0) {
                logsHTML = '<p class="text-muted">No logs available for this integration.</p>';
            } else {
                logs.forEach(log => {
                    const timestamp = new Date(log.timestamp).toLocaleString();
                    const levelClass = this.getLogLevelClass(log.level);
                    
                    logsHTML += `
                        <div class="log-entry mb-2 p-2 border rounded">
                            <div class="d-flex justify-content-between align-items-start">
                                <div class="flex-grow-1">
                                    <span class="badge bg-${levelClass} me-2">${log.level.toUpperCase()}</span>
                                    <small class="text-muted">${timestamp}</small>
                                    <p class="mb-1 mt-1">${log.message}</p>
                                    ${log.details ? `<small class="text-muted">${JSON.stringify(log.details)}</small>` : ''}
                                </div>
                            </div>
                        </div>
                    `;
                });
            }
            
            const modalHTML = `
                <div class="modal fade" id="logsModal" tabindex="-1" aria-labelledby="logsModalLabel" aria-hidden="true">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="logsModalLabel">${integration.name} - Logs</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="logs-container">
                                    ${logsHTML}
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                                <button type="button" class="btn btn-primary" onclick="kgIntegration.exportIntegrationLogs()">Export Logs</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Remove existing modal if present
            const existingModal = document.getElementById('logsModal');
            if (existingModal) {
                existingModal.remove();
            }
            
            // Add new modal
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('logsModal'));
            modal.show();
            
            // Clean up after modal is hidden
            document.getElementById('logsModal').addEventListener('hidden.bs.modal', function() {
                this.remove();
            });
            
        } catch (error) {
            this.logger.error('Failed to show logs modal:', error);
            this.showError('Failed to show logs');
        }
    }
    
    /**
     * Get log level class for styling
     */
    getLogLevelClass(level) {
        switch (level.toLowerCase()) {
            case 'error': return 'danger';
            case 'warning': return 'warning';
            case 'info': return 'info';
            case 'debug': return 'secondary';
            default: return 'secondary';
        }
    }
    
    /**
     * Refresh integrations
     */
    async refreshIntegrations() {
        try {
            this.logger.info('🔄 Refreshing integrations...');
            
            await this.loadIntegrations();
            this.showSuccess('Integrations refreshed successfully');
            
        } catch (error) {
            this.logger.error('Failed to refresh integrations:', error);
            this.showError('Failed to refresh integrations');
        }
    }
    
    /**
     * Refresh data flow
     */
    refreshDataFlow() {
        try {
            this.logger.info('🔄 Refreshing data flow...');
            
            // Generate new mock data
            this.generateMockDataFlowData();
            
            // Update display
            this.updateDataFlowDisplay();
            
            this.showSuccess('Data flow refreshed successfully');
            
        } catch (error) {
            this.logger.error('Failed to refresh data flow:', error);
            this.showError('Failed to refresh data flow');
        }
    }
    
    /**
     * Generate mock data flow data
     */
    generateMockDataFlowData() {
        this.dataFlowData = [
            { timestamp: new Date().toISOString(), source: 'aasx_etl', target: 'neo4j', dataSize: '45 MB', status: 'success' },
            { timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(), source: 'twin_registry', target: 'neo4j', dataSize: '23 MB', status: 'success' },
            { timestamp: new Date(Date.now() - 10 * 60 * 1000).toISOString(), source: 'ai_rag', target: 'neo4j', dataSize: '12 MB', status: 'warning' },
            { timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(), source: 'external_api', target: 'neo4j', dataSize: '67 MB', status: 'success' }
        ];
    }
    
    /**
     * Update data flow display
     */
    updateDataFlowDisplay() {
        const dataFlowContainer = document.getElementById('dataflow-container');
        if (!dataFlowContainer) return;
        
        let dataFlowHTML = '';
        
        this.dataFlowData.forEach(flow => {
            const timestamp = new Date(flow.timestamp).toLocaleString();
            const statusClass = this.getStatusClass(flow.status);
            
            dataFlowHTML += `
                <div class="dataflow-item card mb-2">
                    <div class="card-body py-2">
                        <div class="d-flex justify-content-between align-items-center">
                            <div class="flex-grow-1">
                                <small class="text-muted">${timestamp}</small>
                                <div class="dataflow-route">
                                    <strong>${flow.source}</strong> → <strong>${flow.target}</strong>
                                </div>
                                <small class="text-muted">${flow.dataSize}</small>
                            </div>
                            <span class="badge bg-${statusClass}">${flow.status}</span>
                        </div>
                    </div>
                </div>
            `;
        });
        
        dataFlowContainer.innerHTML = dataFlowHTML;
    }
    
    /**
     * Start monitoring
     */
    startMonitoring() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
        }
        
        // Monitor integrations every 30 seconds
        this.monitoringInterval = setInterval(() => {
            if (this.isTabActive) {
                this.checkIntegrationHealth();
            }
        }, 30000);
        
        this.logger.info('Integration monitoring started');
    }
    
    /**
     * Check integration health
     */
    async checkIntegrationHealth() {
        try {
            for (const [type, integration] of Object.entries(this.integrations)) {
                if (integration.status === this.STATUS.CONNECTED) {
                    // Check if integration is still healthy
                    const lastSync = new Date(integration.lastSync);
                    const now = new Date();
                    const timeSinceLastSync = (now - lastSync) / 1000; // seconds
                    
                    if (timeSinceLastSync > integration.config.syncInterval * 2) {
                        integration.status = this.STATUS.WARNING;
                        this.logger.warn(`Integration ${type} showing warning signs`);
                    }
                }
            }
            
            // Update display
            this.updateIntegrationsDisplay();
            
        } catch (error) {
            this.logger.error('Failed to check integration health:', error);
        }
    }
    
    /**
     * Export integration logs
     */
    async exportIntegrationLogs() {
        try {
            const exportData = {
                integrations: this.integrations,
                logs: this.mockLogs,
                dataFlow: this.dataFlowData,
                exportTime: new Date().toISOString()
            };
            
            // Create download link
            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `integration_logs_${Date.now()}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            this.showSuccess('Integration logs exported successfully');
            
        } catch (error) {
            this.logger.error('Failed to export integration logs:', error);
            this.showError('Failed to export logs');
        }
    }
    
    /**
     * Clear integration logs
     */
    clearIntegrationLogs() {
        try {
            this.mockLogs = [];
            this.showSuccess('Integration logs cleared successfully');
        } catch (error) {
            this.logger.error('Failed to clear integration logs:', error);
            this.showError('Failed to clear logs');
        }
    }
    
    /**
     * Filter logs
     */
    filterLogs() {
        try {
            this.logger.info('🔍 Filtering logs...');
            this.showSuccess('Log filtering feature coming soon!');
        } catch (error) {
            this.logger.error('Failed to filter logs:', error);
            this.showError('Failed to filter logs');
        }
    }
    
    /**
     * Show integration settings
     */
    showIntegrationSettings() {
        try {
            this.logger.info('⚙️ Showing integration settings...');
            this.showSuccess('Integration settings feature coming soon!');
        } catch (error) {
            this.logger.error('Failed to show integration settings:', error);
            this.showError('Failed to show settings');
        }
    }
    
    /**
     * Show integration help
     */
    showIntegrationHelp() {
        try {
            this.showNotification('Integration Help: Manage connections between different modules, monitor data flow, and configure synchronization settings.', 'info');
        } catch (error) {
            this.logger.error('Failed to show integration help:', error);
            this.showError('Failed to show help');
        }
    }
    
    /**
     * Show integration documentation
     */
    showIntegrationDocs() {
        try {
            this.logger.info('📚 Showing integration documentation...');
            this.showSuccess('Integration documentation feature coming soon!');
        } catch (error) {
            this.logger.error('Failed to show integration documentation:', error);
            this.showError('Failed to show documentation');
        }
    }
    
    /**
     * Set tab active state
     */
    setTabActive(active) {
        this.isTabActive = active;
        
        if (active) {
            this.startMonitoring();
        } else {
            this.stopMonitoring();
        }
    }
    
    /**
     * Stop monitoring
     */
    stopMonitoring() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = null;
        }
        
        this.logger.info('Integration monitoring stopped');
    }
    
    /**
     * Show success message
     */
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    /**
     * Show error message
     */
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
    
    /**
     * Cleanup resources
     */
    destroy() {
        // Clear intervals
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
        }
        
        this.logger.info('Integration Component destroyed');
    }
}

// Create global instance
const kgIntegration = new KGIntegrationComponent();

// Expose methods globally for HTML onclick calls
window.createIntegration = () => kgIntegration.showCreateIntegrationModal();
window.refreshIntegrations = () => kgIntegration.refreshIntegrations();
window.refreshDataFlow = () => kgIntegration.refreshDataFlow();
window.configureAASXIntegration = () => kgIntegration.configureIntegration('aasx_etl');
window.configureTwinIntegration = () => kgIntegration.configureIntegration('twin_registry');
window.configureAIIntegration = () => kgIntegration.configureIntegration('ai_rag');
window.saveIntegrationConfig = (moduleType) => kgIntegration.saveIntegrationConfig(moduleType);
window.testIntegrationConnection = (moduleType) => kgIntegration.testIntegrationConnection(moduleType);
window.createNewIntegration = () => kgIntegration.createNewIntegration();
window.exportIntegrationLogs = () => kgIntegration.exportIntegrationLogs();
window.clearIntegrationLogs = () => kgIntegration.clearIntegrationLogs();
window.filterLogs = () => kgIntegration.filterLogs();
window.showIntegrationSettings = () => kgIntegration.showIntegrationSettings();
window.showIntegrationHelp = () => kgIntegration.showIntegrationHelp();
window.showIntegrationDocs = () => kgIntegration.showIntegrationDocs();

// Export the class
export { KGIntegrationComponent };
