/**
 * System Logs Module
 * 
 * Manages log viewing, filtering, and analysis for the AASX-ETL platform
 * with user-based access control and real-time log monitoring.
 * 
 * Phase 6: System Monitoring & Management
 */

class SystemLogs {
    constructor() {
        this.baseUrl = '/api/aasx-etl/system';
        this.isInitialized = false;
        this.systemCore = null;
        
        // Log data
        this.logs = [];
        this.logSummary = {};
        this.logTrends = {};
        
        // Filter settings
        this.currentFilters = {
            level: null,
            service: null,
            hours: 24,
            query: '',
            limit: 1000
        };
        
        // Log viewing state
        this.currentPage = 1;
        this.logsPerPage = 50;
        this.totalLogs = 0;
        
        // Real-time log monitoring
        this.isLiveMonitoring = false;
        this.liveUpdateInterval = null;
        this.liveUpdateFrequency = 5000; // 5 seconds
        
        // Event listeners
        this.logUpdateCallbacks = [];
        this.errorCallbacks = [];
        
        // Initialize
        this.init();
    }
    
    async init() {
        try {
            console.log('🔄 System Logs: Initializing...');
            
            // Wait for System Core
            await this.waitForSystemCore();
            
            // Initialize log monitoring
            this.initializeLogMonitoring();
            
            this.isInitialized = true;
            console.log('✅ System Logs: Initialized successfully');
            
        } catch (error) {
            console.error('❌ System Logs: Initialization failed:', error);
        }
    }
    
    async waitForSystemCore() {
        return new Promise((resolve, reject) => {
            const maxWaitTime = 10000; // 10 seconds
            const startTime = Date.now();
            
            const checkSystemCore = () => {
                if (window.systemCore && window.systemCore.isInitialized) {
                    this.systemCore = window.systemCore;
                    resolve();
                } else if (Date.now() - startTime > maxWaitTime) {
                    reject(new Error('Timeout waiting for System Core'));
                } else {
                    setTimeout(checkSystemCore, 100);
                }
            };
            
            checkSystemCore();
        });
    }
    
    initializeLogMonitoring() {
        try {
            // Subscribe to system updates
            if (this.systemCore) {
                this.systemCore.onHealthUpdate((data) => {
                    // Handle system health updates if needed
                });
                
                this.systemCore.onError((error) => {
                    this.handleError(error);
                });
            }
            
            // Initial log fetch
            this.fetchLogs();
            
            console.log('✅ System Logs: Log monitoring initialized');
            
        } catch (error) {
            console.error('❌ System Logs: Failed to initialize log monitoring:', error);
        }
    }
    
    async fetchLogs(filters = null) {
        try {
            if (!this.systemCore || !this.systemCore.isAuthenticated) {
                console.warn('⚠️ System Logs: Cannot fetch logs - not authenticated');
                return;
            }
            
            // Update filters if provided
            if (filters) {
                this.currentFilters = { ...this.currentFilters, ...filters };
            }
            
            // Build query parameters
            const params = new URLSearchParams();
            if (this.currentFilters.level) params.append('level', this.currentFilters.level);
            if (this.currentFilters.service) params.append('service', this.currentFilters.service);
            if (this.currentFilters.hours) params.append('hours', this.currentFilters.hours);
            if (this.currentFilters.query) params.append('query', this.currentFilters.query);
            if (this.currentFilters.limit) params.append('limit', this.currentFilters.limit);
            
            const response = await fetch(`${this.baseUrl}/logs?${params.toString()}`, {
                method: 'GET',
                headers: this.systemCore.getAuthHeaders()
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.logs = data.logs || [];
            this.totalLogs = this.logs.length;
            
            // Reset pagination
            this.currentPage = 1;
            
            // Notify listeners
            this.notifyLogUpdate();
            
            console.log(`📊 System Logs: Fetched ${this.logs.length} logs`);
            
        } catch (error) {
            console.error('❌ System Logs: Failed to fetch logs:', error);
            this.handleError(error);
        }
    }
    
    async fetchLogSummary(hours = 24) {
        try {
            if (!this.systemCore || !this.systemCore.isAuthenticated) {
                return;
            }
            
            const response = await fetch(`${this.baseUrl}/logs/summary?hours=${hours}`, {
                method: 'GET',
                headers: this.systemCore.getAuthHeaders()
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.logSummary = data.summary || {};
            
            console.log('📊 System Logs: Log summary updated');
            
        } catch (error) {
            console.error('❌ System Logs: Failed to fetch log summary:', error);
            this.handleError(error);
        }
    }
    
    async fetchLogTrends(hours = 24) {
        try {
            if (!this.systemCore || !this.systemCore.isAuthenticated) {
                return;
            }
            
            const response = await fetch(`${this.baseUrl}/logs/trends?hours=${hours}`, {
                method: 'GET',
                headers: this.systemCore.getAuthHeaders()
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.logTrends = data.trends || {};
            
            console.log('📊 System Logs: Log trends updated');
            
        } catch (error) {
            console.error('❌ System Logs: Failed to fetch log trends:', error);
            this.handleError(error);
        }
    }
    
    async searchLogs(query, filters = {}) {
        try {
            if (!query || !query.trim()) {
                return this.fetchLogs(filters);
            }
            
            const searchFilters = { ...this.currentFilters, ...filters, query: query.trim() };
            await this.fetchLogs(searchFilters);
            
            console.log(`🔍 System Logs: Search completed for "${query}"`);
            
        } catch (error) {
            console.error('❌ System Logs: Search failed:', error);
            this.handleError(error);
        }
    }
    
    async getErrorLogs(hours = 24) {
        try {
            const filters = { ...this.currentFilters, level: 'error', hours };
            await this.fetchLogs(filters);
            
            console.log('📊 System Logs: Error logs fetched');
            
        } catch (error) {
            console.error('❌ System Logs: Failed to fetch error logs:', error);
            this.handleError(error);
        }
    }
    
    async getServiceLogs(service, hours = 24) {
        try {
            const filters = { ...this.currentFilters, service, hours };
            await this.fetchLogs(filters);
            
            console.log(`📊 System Logs: Service logs fetched for ${service}`);
            
        } catch (error) {
            console.error(`❌ System Logs: Failed to fetch service logs for ${service}:`, error);
            this.handleError(error);
        }
    }
    
    startLiveMonitoring() {
        try {
            if (this.isLiveMonitoring) {
                console.log('🔄 System Logs: Live monitoring already active');
                return;
            }
            
            console.log('🚀 System Logs: Starting live monitoring...');
            
            this.isLiveMonitoring = true;
            this.liveUpdateInterval = setInterval(() => {
                this.fetchLogs();
            }, this.liveUpdateFrequency);
            
            console.log('✅ System Logs: Live monitoring started');
            
        } catch (error) {
            console.error('❌ System Logs: Failed to start live monitoring:', error);
            this.handleError(error);
        }
    }
    
    stopLiveMonitoring() {
        try {
            if (this.liveUpdateInterval) {
                clearInterval(this.liveUpdateInterval);
                this.liveUpdateInterval = null;
            }
            
            this.isLiveMonitoring = false;
            console.log('🛑 System Logs: Live monitoring stopped');
            
        } catch (error) {
            console.error('❌ System Logs: Failed to stop live monitoring:', error);
        }
    }
    
    // Pagination methods
    getPaginatedLogs(page = 1, perPage = null) {
        try {
            const logsPerPage = perPage || this.logsPerPage;
            const startIndex = (page - 1) * logsPerPage;
            const endIndex = startIndex + logsPerPage;
            
            return this.logs.slice(startIndex, endIndex);
        } catch (error) {
            console.error('❌ System Logs: Failed to get paginated logs:', error);
            return [];
        }
    }
    
    getTotalPages() {
        try {
            return Math.ceil(this.totalLogs / this.logsPerPage);
        } catch (error) {
            console.error('❌ System Logs: Failed to calculate total pages:', error);
            return 1;
        }
    }
    
    goToPage(page) {
        try {
            const totalPages = this.getTotalPages();
            if (page >= 1 && page <= totalPages) {
                this.currentPage = page;
                this.notifyLogUpdate();
                return true;
            }
            return false;
        } catch (error) {
            console.error('❌ System Logs: Failed to go to page:', error);
            return false;
        }
    }
    
    // Filter methods
    setFilter(filter, value) {
        try {
            this.currentFilters[filter] = value;
            this.currentPage = 1; // Reset to first page
            this.fetchLogs();
        } catch (error) {
            console.error(`❌ System Logs: Failed to set filter ${filter}:`, error);
        }
    }
    
    clearFilters() {
        try {
            this.currentFilters = {
                level: null,
                service: null,
                hours: 24,
                query: '',
                limit: 1000
            };
            this.currentPage = 1;
            this.fetchLogs();
        } catch (error) {
            console.error('❌ System Logs: Failed to clear filters:', error);
        }
    }
    
    getAvailableLevels() {
        try {
            const levels = [...new Set(this.logs.map(log => log.level))];
            return levels.sort();
        } catch (error) {
            console.error('❌ System Logs: Failed to get available levels:', error);
            return [];
        }
    }
    
    getAvailableServices() {
        try {
            const services = [...new Set(this.logs.map(log => log.service))];
            return services.sort();
        } catch (error) {
            console.error('❌ System Logs: Failed to get available services:', error);
            return [];
        }
    }
    
    // Data access methods
    getLogs() {
        return this.logs;
    }
    
    getLogSummary() {
        return this.logSummary;
    }
    
    getLogTrends() {
        return this.logTrends;
    }
    
    getCurrentFilters() {
        return { ...this.currentFilters };
    }
    
    getPaginationInfo() {
        return {
            currentPage: this.currentPage,
            totalPages: this.getTotalPages(),
            logsPerPage: this.logsPerPage,
            totalLogs: this.totalLogs,
            startIndex: (this.currentPage - 1) * this.logsPerPage + 1,
            endIndex: Math.min(this.currentPage * this.logsPerPage, this.totalLogs)
        };
    }
    
    // Event handling
    onLogUpdate(callback) {
        this.logUpdateCallbacks.push(callback);
    }
    
    onError(callback) {
        this.errorCallbacks.push(callback);
    }
    
    notifyLogUpdate() {
        this.logUpdateCallbacks.forEach(callback => {
            try {
                callback({
                    logs: this.getPaginatedLogs(this.currentPage),
                    pagination: this.getPaginationInfo(),
                    filters: this.getCurrentFilters()
                });
            } catch (error) {
                console.error('❌ System Logs: Log update callback error:', error);
            }
        });
    }
    
    handleError(error) {
        console.error('❌ System Logs: Error occurred:', error);
        
        this.errorCallbacks.forEach(callback => {
            try {
                callback(error);
            } catch (callbackError) {
                console.error('❌ System Logs: Error callback error:', callbackError);
            }
        });
    }
    
    // Utility methods
    getLevelColor(level) {
        const colors = {
            'debug': 'secondary',
            'info': 'info',
            'warning': 'warning',
            'error': 'danger',
            'critical': 'danger'
        };
        return colors[level] || 'secondary';
    }
    
    getServiceColor(service) {
        const colors = {
            'aasx_etl': 'primary',
            'database': 'success',
            'authentication': 'info',
            'file_storage': 'warning'
        };
        return colors[service] || 'secondary';
    }
    
    formatTimestamp(timestamp) {
        try {
            if (!timestamp) return 'Unknown';
            
            const date = new Date(timestamp);
            return date.toLocaleString();
        } catch (error) {
            return 'Invalid';
        }
    }
    
    formatLogMessage(message, maxLength = 100) {
        try {
            if (!message) return '';
            
            if (message.length <= maxLength) {
                return message;
            }
            
            return message.substring(0, maxLength) + '...';
        } catch (error) {
            return 'Error formatting message';
        }
    }
    
    formatLogDetails(log) {
        try {
            const details = {
                timestamp: this.formatTimestamp(log.timestamp),
                level: log.level,
                service: log.service,
                message: this.formatLogMessage(log.message),
                user: log.user_id || 'System',
                source: log.source_file ? `${log.source_file}:${log.line_number}` : 'Unknown'
            };
            
            if (log.extra_data) {
                details.extra = JSON.stringify(log.extra_data);
            }
            
            return details;
        } catch (error) {
            console.error('❌ System Logs: Failed to format log details:', error);
            return {};
        }
    }
    
    // Export methods
    exportLogs(format = 'json') {
        try {
            let content = '';
            let filename = `system_logs_${new Date().toISOString().split('T')[0]}`;
            
            if (format === 'json') {
                content = JSON.stringify(this.logs, null, 2);
                filename += '.json';
            } else if (format === 'csv') {
                content = this.convertLogsToCSV();
                filename += '.csv';
            } else if (format === 'txt') {
                content = this.convertLogsToText();
                filename += '.txt';
            }
            
            // Create download link
            const blob = new Blob([content], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
            
            URL.revokeObjectURL(url);
            
            console.log(`📤 System Logs: Exported ${this.logs.length} logs as ${format}`);
            
        } catch (error) {
            console.error('❌ System Logs: Failed to export logs:', error);
            this.handleError(error);
        }
    }
    
    convertLogsToCSV() {
        try {
            if (this.logs.length === 0) return '';
            
            const headers = ['Timestamp', 'Level', 'Service', 'Message', 'User', 'Source'];
            const rows = this.logs.map(log => [
                log.timestamp,
                log.level,
                log.service,
                log.message,
                log.user_id || 'System',
                log.source_file ? `${log.source_file}:${log.line_number}` : 'Unknown'
            ]);
            
            return [headers, ...rows]
                .map(row => row.map(cell => `"${cell}"`).join(','))
                .join('\n');
                
        } catch (error) {
            console.error('❌ System Logs: Failed to convert logs to CSV:', error);
            return '';
        }
    }
    
    convertLogsToText() {
        try {
            if (this.logs.length === 0) return '';
            
            return this.logs.map(log => 
                `[${log.timestamp}] ${log.level.toUpperCase()} - ${log.service}: ${log.message}`
            ).join('\n');
            
        } catch (error) {
            console.error('❌ System Logs: Failed to convert logs to text:', error);
            return '';
        }
    }
    
    // Cleanup method
    cleanup() {
        try {
            this.stopLiveMonitoring();
            this.logUpdateCallbacks = [];
            this.errorCallbacks = [];
            console.log('🧹 System Logs: Cleanup completed');
        } catch (error) {
            console.error('❌ System Logs: Cleanup failed:', error);
        }
    }
}

// Export for use in other modules
window.SystemLogs = SystemLogs;
