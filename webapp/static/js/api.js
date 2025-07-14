/**
 * API Client for QI Digital Platform
 * Handles all communication between frontend and backend services
 */

class APIClient {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
        this.endpoints = {
            // AI/RAG System
            ai_rag: {
                query: '/ai-rag/query',
                demo: '/ai-rag/demo',
                stats: '/ai-rag/stats',
                collections: '/ai-rag/collections',
                index_data: '/ai-rag/index-data'
            },
            // ETL Pipeline
            etl: {
                status: '/etl/status',
                process: '/etl/process',
                results: '/etl/results',
                config: '/etl/config'
            },
            // Knowledge Graph
            kg: {
                status: '/kg-neo4j/api/status',
                query: '/kg-neo4j/api/query',
                graph: '/kg-neo4j/api/graph',
                stats: '/kg-neo4j/api/stats',
                load_data: '/kg-neo4j/api/load-data'
            },
            // Twin Registry
            twin: {
                list: '/twin-registry/twins',
                create: '/twin-registry/twins',
                update: '/twin-registry/twins',
                delete: '/twin-registry/twins',
                status: '/twin-registry/status'
            },
            // Analytics
            analytics: {
                dashboard: '/analytics/dashboard',
                metrics: '/analytics/metrics',
                reports: '/analytics/reports'
            },
            // System
            system: {
                health: '/health',
                status: '/status'
            }
        };
    }

    /**
     * Make HTTP request with error handling
     */
    async request(endpoint, options = {}) {
        const url = this.baseURL + endpoint;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            console.error(`API request failed for ${endpoint}:`, error);
            throw error;
        }
    }

    /**
     * AI/RAG System API Methods
     */
    async queryAIRAG(query, analysisType = 'general', collection = 'aasx_assets') {
        return this.request(this.endpoints.ai_rag.query, {
            method: 'POST',
            body: JSON.stringify({
                query: query,
                analysis_type: analysisType,
                collection: collection
            })
        });
    }

    async runDemoQueries() {
        return this.request(this.endpoints.ai_rag.demo, {
            method: 'POST'
        });
    }

    async getAIRAGStats() {
        return this.request(this.endpoints.ai_rag.stats);
    }

    async getCollections() {
        return this.request(this.endpoints.ai_rag.collections);
    }

    async indexETLData() {
        return this.request(this.endpoints.ai_rag.index_data, {
            method: 'POST'
        });
    }

    /**
     * ETL Pipeline API Methods
     */
    async getETLStatus() {
        return this.request(this.endpoints.etl.status);
    }

    async processETL(inputDir = null, outputDir = null) {
        return this.request(this.endpoints.etl.process, {
            method: 'POST',
            body: JSON.stringify({
                input_dir: inputDir,
                output_dir: outputDir
            })
        });
    }

    async getETLResults() {
        return this.request(this.endpoints.etl.results);
    }

    async getETLConfig() {
        return this.request(this.endpoints.etl.config);
    }

    /**
     * Knowledge Graph API Methods
     */
    async getKGStatus() {
        return this.request(this.endpoints.kg.status);
    }

    async queryKG(query) {
        return this.request(this.endpoints.kg.query, {
            method: 'POST',
            body: JSON.stringify({ query: query })
        });
    }

    async getGraphData() {
        return this.request(this.endpoints.kg.graph);
    }

    async getKGStats() {
        return this.request(this.endpoints.kg.stats);
    }

    async loadKGData(dataPath) {
        return this.request(this.endpoints.kg.load_data, {
            method: 'POST',
            body: JSON.stringify({ data_path: dataPath })
        });
    }

    /**
     * Twin Registry API Methods
     */
    async getTwins() {
        return this.request(this.endpoints.twin.list);
    }

    async createTwin(twinData) {
        return this.request(this.endpoints.twin.create, {
            method: 'POST',
            body: JSON.stringify(twinData)
        });
    }

    async updateTwin(id, twinData) {
        return this.request(`${this.endpoints.twin.update}/${id}`, {
            method: 'PUT',
            body: JSON.stringify(twinData)
        });
    }

    async deleteTwin(id) {
        return this.request(`${this.endpoints.twin.delete}/${id}`, {
            method: 'DELETE'
        });
    }

    async getTwinStatus() {
        return this.request(this.endpoints.twin.status);
    }

    /**
     * Analytics API Methods
     */
    async getDashboardData() {
        return this.request(this.endpoints.analytics.dashboard);
    }

    async getMetrics() {
        return this.request(this.endpoints.analytics.metrics);
    }

    async getReports() {
        return this.request(this.endpoints.analytics.reports);
    }

    /**
     * System API Methods
     */
    async getHealth() {
        return this.request(this.endpoints.system.health);
    }

    async getSystemStatus() {
        return this.request(this.endpoints.system.status);
    }

    /**
     * Utility Methods
     */
    async checkAllServices() {
        const services = {
            ai_rag: this.getAIRAGStats(),
            etl: this.getETLStatus(),
            kg: this.getKGStatus(),
            twin: this.getTwinStatus(),
            system: this.getHealth()
        };

        const results = {};
        for (const [service, promise] of Object.entries(services)) {
            try {
                console.log(`🔍 Checking ${service} service...`);
                results[service] = await promise;
                console.log(`✅ ${service} service result:`, results[service]);
            } catch (error) {
                console.error(`❌ ${service} service error:`, error);
                results[service] = { error: error.message, status: 'error' };
            }
        }

        console.log('🔍 All services results:', results);
        return results;
    }
}

/**
 * UI Helper Class for API Integration
 */
class UIHelper {
    constructor(apiClient) {
        this.api = apiClient;
        this.loadingStates = new Map();
    }

    /**
     * Show loading state for an element
     */
    showLoading(elementId, message = 'Loading...') {
        const element = document.getElementById(elementId);
        if (element) {
            this.loadingStates.set(elementId, element.innerHTML);
            element.innerHTML = `
                <div class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">${message}</p>
                </div>
            `;
        }
    }

    /**
     * Hide loading state for an element
     */
    hideLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element && this.loadingStates.has(elementId)) {
            element.innerHTML = this.loadingStates.get(elementId);
            this.loadingStates.delete(elementId);
        }
    }

    /**
     * Show success message
     */
    showSuccess(message, duration = 3000) {
        this.showNotification(message, 'success', duration);
    }

    /**
     * Show error message
     */
    showError(message, duration = 5000) {
        this.showNotification(message, 'danger', duration);
    }

    /**
     * Show warning message
     */
    showWarning(message, duration = 4000) {
        this.showNotification(message, 'warning', duration);
    }

    /**
     * Show info message
     */
    showInfo(message, duration = 3000) {
        this.showNotification(message, 'info', duration);
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info', duration = 3000) {
        const notificationId = 'notification-' + Date.now();
        const notification = document.createElement('div');
        notification.id = notificationId;
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto-remove after duration
        setTimeout(() => {
            const element = document.getElementById(notificationId);
            if (element) {
                element.remove();
            }
        }, duration);
    }

    /**
     * Update status indicator
     */
    updateStatusIndicator(service, status) {
        const indicator = document.getElementById(`status-${service}`);
        if (indicator) {
            const statusClass = status === 'healthy' ? 'text-success' : 'text-danger';
            const statusIcon = status === 'healthy' ? 'fa-check-circle' : 'fa-exclamation-circle';
            
            indicator.className = `fas ${statusIcon} ${statusClass}`;
            indicator.title = `${service}: ${status}`;
        }
    }

    /**
     * Update progress bar
     */
    updateProgress(progressId, percentage, message = '') {
        const progressBar = document.getElementById(progressId);
        if (progressBar) {
            const progressElement = progressBar.querySelector('.progress-bar');
            const messageElement = progressBar.querySelector('.progress-message');
            
            if (progressElement) {
                progressElement.style.width = `${percentage}%`;
                progressElement.setAttribute('aria-valuenow', percentage);
            }
            
            if (messageElement && message) {
                messageElement.textContent = message;
            }
        }
    }

    /**
     * Create data table
     */
    createDataTable(containerId, data, columns) {
        const container = document.getElementById(containerId);
        if (!container) return;

        let tableHTML = `
            <table class="table table-striped table-hover">
                <thead class="table-dark">
                    <tr>
        `;
        
        columns.forEach(column => {
            tableHTML += `<th>${column.title}</th>`;
        });
        
        tableHTML += '</tr></thead><tbody>';
        
        data.forEach(row => {
            tableHTML += '<tr>';
            columns.forEach(column => {
                const value = column.render ? column.render(row[column.key]) : row[column.key];
                tableHTML += `<td>${value}</td>`;
            });
            tableHTML += '</tr>';
        });
        
        tableHTML += '</tbody></table>';
        
        container.innerHTML = tableHTML;
    }

    /**
     * Create chart using Chart.js
     */
    createChart(canvasId, data, type = 'line') {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const ctx = canvas.getContext('2d');
        return new Chart(ctx, {
            type: type,
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                }
            }
        });
    }
}

/**
 * Initialize API client and UI helper
 */
const apiClient = new APIClient();
const uiHelper = new UIHelper(apiClient);

/**
 * Global error handler
 */
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    uiHelper.showError('An unexpected error occurred. Please try again.');
});

/**
 * Export for use in other modules
 */
window.APIClient = APIClient;
window.UIHelper = UIHelper;
window.apiClient = apiClient;
window.uiHelper = uiHelper; 