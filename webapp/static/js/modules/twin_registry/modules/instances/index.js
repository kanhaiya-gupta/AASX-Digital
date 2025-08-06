/**
 * Instance Management Module - Main Orchestrator
 * Handles twin instance management, versioning, and snapshots
 */

import { InstanceOperations } from './operations.js';
import { InstanceUI } from './ui.js';

class InstanceManager {
    constructor(baseUrl = '/api/twin-registry') {
        this.baseUrl = baseUrl;
        this.operations = null;
        this.ui = null;
        this.isInitialized = false;
    }

    async init() {
        try {
            console.log('🔄 Initializing Instance Manager...');
            
            // Initialize sub-modules
            this.operations = new InstanceOperations(this.baseUrl);
            this.ui = new InstanceUI();
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Load initial data
            await this.loadInstanceData();
            
            this.isInitialized = true;
            console.log('✅ Instance Manager initialized');
            
            // Dispatch ready event
            document.dispatchEvent(new CustomEvent('instanceManagerReady'));
            
        } catch (error) {
            console.error('❌ Instance Manager initialization failed:', error);
            throw error;
        }
    }

    setupEventListeners() {
        // Instance creation form
        const instanceForm = document.getElementById('instanceCreationForm');
        if (instanceForm) {
            instanceForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.createInstance();
            });
        }

        // Twin filter change
        const twinFilter = document.getElementById('instanceTwinFilter');
        if (twinFilter) {
            twinFilter.addEventListener('change', async (e) => {
                await this.loadInstanceData(e.target.value);
            });
        }

        // Instance type change
        const instanceType = document.getElementById('instanceType');
        if (instanceType) {
            instanceType.addEventListener('change', (e) => {
                this.ui.updateInstanceTypeUI(e.target.value);
            });
        }

        // Select all checkbox
        const selectAllCheckbox = document.getElementById('selectAllTwins');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                this.ui.toggleSelectAll(e.target.checked);
            });
        }

        // Listen for external events
        document.addEventListener('twinInstanceCreated', (e) => {
            this.loadInstanceData();
        });

        document.addEventListener('twinInstanceUpdated', (e) => {
            this.loadInstanceData();
        });
    }

    async loadInstanceData(twinId = null) {
        try {
            console.log('📊 Loading instance data...');
            
            const instances = await this.operations.getInstances(twinId);
            const summary = await this.operations.getInstanceSummary(twinId);
            
            // Update UI
            this.ui.updateInstanceTable(instances);
            this.ui.updateInstanceSummary(summary);
            this.ui.updateTwinFilter();
            
            console.log('✅ Instance data loaded');
            
        } catch (error) {
            console.error('❌ Failed to load instance data:', error);
            this.ui.showError('Failed to load instance data');
        }
    }

    async createInstance() {
        try {
            const twinId = document.getElementById('instanceTwinSelect').value;
            const instanceType = document.getElementById('instanceType').value;
            const description = document.getElementById('instanceDescription').value;

            if (!twinId) {
                this.ui.showError('Please select a twin');
                return;
            }

            const instanceData = {
                twin_id: twinId,
                instance_data: {
                    type: instanceType,
                    description: description,
                    created_at: new Date().toISOString()
                },
                instance_metadata: {
                    source: 'ui_creation',
                    user: 'system'
                },
                created_by: 'system'
            };

            const result = await this.operations.createInstance(instanceData);
            
            if (result.success) {
                this.ui.showSuccess('Instance created successfully');
                document.getElementById('instanceCreationForm').reset();
                
                // Reload data
                await this.loadInstanceData();
                
                // Dispatch event
                document.dispatchEvent(new CustomEvent('twinInstanceCreated', { 
                    detail: { instance: result.instance } 
                }));
            } else {
                this.ui.showError(result.message || 'Failed to create instance');
            }
            
        } catch (error) {
            console.error('❌ Failed to create instance:', error);
            this.ui.showError('Failed to create instance');
        }
    }

    async createSnapshot() {
        try {
            const twinId = document.getElementById('instanceTwinSelect').value;
            
            if (!twinId) {
                this.ui.showError('Please select a twin for snapshot');
                return;
            }

            const result = await this.operations.createSnapshot(twinId);
            
            if (result.success) {
                this.ui.showSuccess('Snapshot created successfully');
                await this.loadInstanceData();
            } else {
                this.ui.showError(result.message || 'Failed to create snapshot');
            }
            
        } catch (error) {
            console.error('❌ Failed to create snapshot:', error);
            this.ui.showError('Failed to create snapshot');
        }
    }

    async createBackup() {
        try {
            const twinId = document.getElementById('instanceTwinSelect').value;
            
            if (!twinId) {
                this.ui.showError('Please select a twin for backup');
                return;
            }

            const result = await this.operations.createBackup(twinId);
            
            if (result.success) {
                this.ui.showSuccess('Backup created successfully');
                await this.loadInstanceData();
            } else {
                this.ui.showError(result.message || 'Failed to create backup');
            }
            
        } catch (error) {
            console.error('❌ Failed to create backup:', error);
            this.ui.showError('Failed to create backup');
        }
    }

    async compareInstances() {
        try {
            const instance1Id = document.getElementById('instance1Select').value;
            const instance2Id = document.getElementById('instance2Select').value;

            if (!instance1Id || !instance2Id) {
                this.ui.showError('Please select two instances to compare');
                return;
            }

            const result = await this.operations.compareInstances(instance1Id, instance2Id);
            
            if (result.success) {
                this.ui.showInstanceComparison(result.comparison);
            } else {
                this.ui.showError(result.message || 'Failed to compare instances');
            }
            
        } catch (error) {
            console.error('❌ Failed to compare instances:', error);
            this.ui.showError('Failed to compare instances');
        }
    }

    async activateInstance(instanceId) {
        try {
            const result = await this.operations.activateInstance(instanceId);
            
            if (result.success) {
                this.ui.showSuccess('Instance activated successfully');
                await this.loadInstanceData();
            } else {
                this.ui.showError(result.message || 'Failed to activate instance');
            }
            
        } catch (error) {
            console.error('❌ Failed to activate instance:', error);
            this.ui.showError('Failed to activate instance');
        }
    }

    async restoreInstance(instanceId) {
        try {
            const result = await this.operations.restoreInstance(instanceId);
            
            if (result.success) {
                this.ui.showSuccess('Instance restored successfully');
                await this.loadInstanceData();
            } else {
                this.ui.showError(result.message || 'Failed to restore instance');
            }
            
        } catch (error) {
            console.error('❌ Failed to restore instance:', error);
            this.ui.showError('Failed to restore instance');
        }
    }

    async deleteInstance(instanceId) {
        try {
            if (!confirm('Are you sure you want to delete this instance? This action cannot be undone.')) {
                return;
            }

            const result = await this.operations.deleteInstance(instanceId);
            
            if (result.success) {
                this.ui.showSuccess('Instance deleted successfully');
                await this.loadInstanceData();
            } else {
                this.ui.showError(result.message || 'Failed to delete instance');
            }
            
        } catch (error) {
            console.error('❌ Failed to delete instance:', error);
            this.ui.showError('Failed to delete instance');
        }
    }

    async viewInstanceDetails(instanceId) {
        try {
            const result = await this.operations.getInstanceDetails(instanceId);
            
            if (result.success) {
                this.ui.showInstanceDetails(result.instance);
            } else {
                this.ui.showError(result.message || 'Failed to load instance details');
            }
            
        } catch (error) {
            console.error('❌ Failed to load instance details:', error);
            this.ui.showError('Failed to load instance details');
        }
    }

    // Public methods for external use
    async refreshInstanceData() {
        await this.loadInstanceData();
    }

    async getInstanceSummary(twinId = null) {
        return await this.operations.getInstanceSummary(twinId);
    }

    async getInstances(twinId = null) {
        return await this.operations.getInstances(twinId);
    }

    // Cleanup method
    cleanup() {
        console.log('🧹 Cleaning up Instance Manager...');
        this.isInitialized = false;
    }
}

export default InstanceManager; 