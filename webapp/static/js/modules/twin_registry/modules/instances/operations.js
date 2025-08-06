/**
 * Instance Operations Module
 * Handles API calls for instance management operations
 */

export class InstanceOperations {
    constructor(baseUrl = '/api/twin-registry') {
        this.baseUrl = baseUrl;
    }

    async createInstance(instanceData) {
        try {
            const response = await fetch(`${this.baseUrl}/instances`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(instanceData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return { success: true, instance: result };
            
        } catch (error) {
            console.error('Error creating instance:', error);
            return { success: false, message: error.message };
        }
    }

    async getInstances(twinId = null) {
        try {
            let url = `${this.baseUrl}/instances`;
            if (twinId) {
                url += `?twin_id=${twinId}`;
            }

            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            // Return the instances array from the response, or empty array if not found
            return result.instances || [];
            
        } catch (error) {
            console.error('Error getting instances:', error);
            return [];
        }
    }

    async getInstanceDetails(instanceId) {
        try {
            const response = await fetch(`${this.baseUrl}/instances/${instanceId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return { success: true, instance: result };
            
        } catch (error) {
            console.error('Error getting instance details:', error);
            return { success: false, message: error.message };
        }
    }

    async getInstanceSummary(twinId = null) {
        try {
            const instances = await this.getInstances(twinId);
            // getInstances now returns the instances array directly
            
            const summary = {
                total: instances.length,
                active: instances.filter(i => i.is_active).length,
                latest_version: 'v1',
                history: instances.length
            };

            if (instances.length > 0) {
                const versions = instances.map(i => i.version).sort();
                summary.latest_version = versions[versions.length - 1];
            }

            return summary;
            
        } catch (error) {
            console.error('Error getting instance summary:', error);
            return { total: 0, active: 0, latest_version: 'v1', history: 0 };
        }
    }

    async createSnapshot(twinId) {
        try {
            const snapshotData = {
                twin_id: twinId,
                instance_data: {
                    type: 'snapshot',
                    description: `Snapshot created at ${new Date().toISOString()}`,
                    created_at: new Date().toISOString()
                },
                instance_metadata: {
                    source: 'snapshot_creation',
                    user: 'system'
                },
                created_by: 'system'
            };

            return await this.createInstance(snapshotData);
            
        } catch (error) {
            console.error('Error creating snapshot:', error);
            return { success: false, message: error.message };
        }
    }

    async createBackup(twinId) {
        try {
            const backupData = {
                twin_id: twinId,
                instance_data: {
                    type: 'backup',
                    description: `Backup created at ${new Date().toISOString()}`,
                    created_at: new Date().toISOString()
                },
                instance_metadata: {
                    source: 'backup_creation',
                    user: 'system'
                },
                created_by: 'system'
            };

            return await this.createInstance(backupData);
            
        } catch (error) {
            console.error('Error creating backup:', error);
            return { success: false, message: error.message };
        }
    }

    async compareInstances(instance1Id, instance2Id) {
        try {
            const response = await fetch(`${this.baseUrl}/instances/compare`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    instance1_id: instance1Id,
                    instance2_id: instance2Id
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return { success: true, comparison: result };
            
        } catch (error) {
            console.error('Error comparing instances:', error);
            return { success: false, message: error.message };
        }
    }

    async activateInstance(instanceId) {
        try {
            const response = await fetch(`${this.baseUrl}/instances/${instanceId}/activate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return { success: true, result };
            
        } catch (error) {
            console.error('Error activating instance:', error);
            return { success: false, message: error.message };
        }
    }

    async restoreInstance(instanceId) {
        try {
            const response = await fetch(`${this.baseUrl}/instances/${instanceId}/restore`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return { success: true, result };
            
        } catch (error) {
            console.error('Error restoring instance:', error);
            return { success: false, message: error.message };
        }
    }

    async deleteInstance(instanceId) {
        try {
            const response = await fetch(`${this.baseUrl}/instances/${instanceId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return { success: true, result };
            
        } catch (error) {
            console.error('Error deleting instance:', error);
            return { success: false, message: error.message };
        }
    }

    async getTwinInstances(twinId) {
        try {
            const response = await fetch(`${this.baseUrl}/twins/${twinId}/instances`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return result;
            
        } catch (error) {
            console.error('Error getting twin instances:', error);
            return [];
        }
    }
} 