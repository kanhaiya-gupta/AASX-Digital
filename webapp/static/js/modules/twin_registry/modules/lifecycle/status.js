/**
 * Lifecycle Status Module
 * Handles status tracking and health monitoring
 */

export default class LifecycleStatus {
    constructor(apiBaseUrl) {
        this.apiBaseUrl = apiBaseUrl;
        this.endpoints = {
            status: '/twins/{twin_id}/lifecycle/status',
            events: '/twins/{twin_id}/lifecycle/events'
        };
    }

    async getTwinStatus(twinId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}${this.endpoints.status.replace('{twin_id}', twinId)}`);
            const result = await response.json();

            if (response.ok) {
                return result;
            } else {
                console.error(`Failed to get status for twin ${twinId}:`, result);
                return null;
            }
        } catch (error) {
            console.error(`❌ Failed to get status for twin ${twinId}:`, error);
            throw error;
        }
    }

    async getTwinEvents(twinId, limit = 10) {
        try {
            const response = await fetch(`${this.apiBaseUrl}${this.endpoints.events.replace('{twin_id}', twinId)}?limit=${limit}`);
            const result = await response.json();

            if (response.ok) {
                return result;
            } else {
                console.error(`Failed to get events for twin ${twinId}:`, result);
                return null;
            }
        } catch (error) {
            console.error(`❌ Failed to get events for twin ${twinId}:`, error);
            throw error;
        }
    }

    getStatusBadgeClass(status) {
        const statusClasses = {
            'running': 'bg-success',
            'stopped': 'bg-secondary',
            'syncing': 'bg-warning',
            'error': 'bg-danger',
            'starting': 'bg-info',
            'stopping': 'bg-warning',
            'unknown': 'bg-light text-dark'
        };
        return statusClasses[status] || 'bg-light text-dark';
    }

    getHealthScoreClass(score) {
        if (score >= 90) return 'text-success';
        if (score >= 75) return 'text-warning';
        if (score >= 60) return 'text-info';
        return 'text-danger';
    }

    getStatusAlertClass(status) {
        const alertClasses = {
            'running': 'success',
            'stopped': 'secondary',
            'syncing': 'warning',
            'error': 'danger',
            'starting': 'info',
            'stopping': 'warning'
        };
        return alertClasses[status] || 'info';
    }
} 