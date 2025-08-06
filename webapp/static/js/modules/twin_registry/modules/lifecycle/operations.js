/**
 * Lifecycle Operations Module
 * Handles start/stop/sync operations for twins
 */

export default class LifecycleOperations {
    constructor(apiBaseUrl) {
        this.apiBaseUrl = apiBaseUrl;
        this.endpoints = {
            start: '/twins/{twin_id}/lifecycle/start',
            stop: '/twins/{twin_id}/lifecycle/stop',
            sync: '/twins/{twin_id}/lifecycle/sync'
        };
        this.activeOperations = new Map();
    }

    async startTwin(twinId, user = 'system') {
        try {
            if (this.activeOperations.has(twinId)) {
                throw new Error(`Operation already in progress for twin ${twinId}`);
            }

            this.activeOperations.set(twinId, 'starting');

            const response = await fetch(`${this.apiBaseUrl}${this.endpoints.start.replace('{twin_id}', twinId)}?user=${user}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            const result = await response.json();
            this.activeOperations.delete(twinId);
            return result;

        } catch (error) {
            this.activeOperations.delete(twinId);
            throw error;
        }
    }

    async stopTwin(twinId, user = 'system') {
        try {
            if (this.activeOperations.has(twinId)) {
                throw new Error(`Operation already in progress for twin ${twinId}`);
            }

            this.activeOperations.set(twinId, 'stopping');

            const response = await fetch(`${this.apiBaseUrl}${this.endpoints.stop.replace('{twin_id}', twinId)}?user=${user}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            const result = await response.json();
            this.activeOperations.delete(twinId);
            return result;

        } catch (error) {
            this.activeOperations.delete(twinId);
            throw error;
        }
    }

    async syncTwin(twinId, syncData = {}, user = 'system') {
        try {
            if (this.activeOperations.has(twinId)) {
                throw new Error(`Operation already in progress for twin ${twinId}`);
            }

            this.activeOperations.set(twinId, 'syncing');

            const response = await fetch(`${this.apiBaseUrl}${this.endpoints.sync.replace('{twin_id}', twinId)}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    twin_id: twinId,
                    sync_type: syncData.sync_type || 'full',
                    force: syncData.force || false
                })
            });

            const result = await response.json();
            this.activeOperations.delete(twinId);
            return result;

        } catch (error) {
            this.activeOperations.delete(twinId);
            throw error;
        }
    }

    async restartTwin(twinId, user = 'system') {
        try {
            await this.stopTwin(twinId, user);
            await new Promise(resolve => setTimeout(resolve, 1000));
            await this.startTwin(twinId, user);
        } catch (error) {
            throw error;
        }
    }

    isOperationInProgress(twinId) {
        return this.activeOperations.has(twinId);
    }

    getActiveOperations() {
        return Array.from(this.activeOperations.entries());
    }
} 