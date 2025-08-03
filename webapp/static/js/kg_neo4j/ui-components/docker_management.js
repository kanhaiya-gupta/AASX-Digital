/**
 * Docker Management Component
 * Handles Neo4j Docker container operations and monitoring
 */

class DockerManagementComponent {
    constructor() {
        this.apiBaseUrl = '/api/kg-neo4j';
        this.containerName = 'aasx-digital-neo4j';
        this.autoRefreshInterval = null;
        this.logsAutoRefreshInterval = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadDockerStatus();
        this.startAutoRefresh();
    }

    bindEvents() {
        // Docker control buttons
        document.getElementById('docker-start-btn')?.addEventListener('click', () => {
            this.startContainer();
        });

        document.getElementById('docker-stop-btn')?.addEventListener('click', () => {
            this.stopContainer();
        });

        document.getElementById('docker-restart-btn')?.addEventListener('click', () => {
            this.restartContainer();
        });

        document.getElementById('docker-refresh-btn')?.addEventListener('click', () => {
            this.loadDockerStatus();
        });

        // Test connection
        document.getElementById('test-connection-btn')?.addEventListener('click', () => {
            this.testConnection();
        });

        // Logs controls
        document.getElementById('refresh-logs-btn')?.addEventListener('click', () => {
            this.loadContainerLogs();
        });

        document.getElementById('clear-logs-btn')?.addEventListener('click', () => {
            this.clearLogs();
        });

        document.getElementById('auto-refresh-logs')?.addEventListener('change', (e) => {
            if (e.target.checked) {
                this.startLogsAutoRefresh();
            } else {
                this.stopLogsAutoRefresh();
            }
        });

        // Additional Quick Access buttons
        document.getElementById('copy-connection-string-btn')?.addEventListener('click', () => {
            this.copyConnectionString();
        });

        document.getElementById('show-examples-btn')?.addEventListener('click', () => {
            this.showExamplesModal();
        });

        document.getElementById('open-cypher-shell-btn')?.addEventListener('click', () => {
            this.showCypherShellCommand();
        });
    }

    async loadDockerStatus() {
        try {
            this.showLoading('Loading Docker status...');
            
            const response = await fetch(`${this.apiBaseUrl}/docker-status`);
            const data = await response.json();
            
            if (data.success) {
                this.updateStatusDisplay(data.status);
                this.updateContainerDetails(data.details);
            } else {
                this.showError('Failed to load Docker status');
            }
        } catch (error) {
            console.error('Error loading Docker status:', error);
            this.showError('Error loading Docker status');
        } finally {
            this.hideLoading();
        }
    }

    async startContainer() {
        try {
            this.showLoading('Starting Neo4j container...');
            
            const response = await fetch(`${this.apiBaseUrl}/docker/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('Neo4j container started successfully');
                // Wait a moment for container to fully start
                setTimeout(() => {
                    this.loadDockerStatus();
                }, 3000);
            } else {
                this.showError(data.error || 'Failed to start container');
            }
        } catch (error) {
            console.error('Error starting container:', error);
            this.showError('Failed to start container');
        } finally {
            this.hideLoading();
        }
    }

    async stopContainer() {
        try {
            this.showLoading('Stopping Neo4j container...');
            
            const response = await fetch(`${this.apiBaseUrl}/docker/stop`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('Neo4j container stopped successfully');
                this.loadDockerStatus();
            } else {
                this.showError(data.error || 'Failed to stop container');
            }
        } catch (error) {
            console.error('Error stopping container:', error);
            this.showError('Failed to stop container');
        } finally {
            this.hideLoading();
        }
    }

    async restartContainer() {
        try {
            this.showLoading('Restarting Neo4j container...');
            
            // First stop, then start
            await this.stopContainer();
            
            // Wait a moment before starting
            setTimeout(async () => {
                await this.startContainer();
            }, 2000);
            
        } catch (error) {
            console.error('Error restarting container:', error);
            this.showError('Failed to restart container');
            this.hideLoading();
        }
    }

    async testConnection() {
        try {
            this.showLoading('Testing Neo4j connection...');
            
            const response = await fetch(`${this.apiBaseUrl}/status`);
            const data = await response.json();
            
            if (data.success && data.status.connected) {
                this.showSuccess('Neo4j connection successful');
            } else {
                this.showError('Neo4j connection failed');
            }
            
            // Refresh the Docker status to update the connection badge
            await this.loadDockerStatus();
            
        } catch (error) {
            console.error('Error testing connection:', error);
            this.showError('Connection test failed');
        } finally {
            this.hideLoading();
        }
    }

    async loadContainerLogs() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/docker/logs`);
            const data = await response.json();
            
            if (data.success) {
                this.updateLogsDisplay(data.logs);
            } else {
                this.updateLogsDisplay('Failed to load logs');
            }
        } catch (error) {
            console.error('Error loading logs:', error);
            this.updateLogsDisplay('Error loading logs');
        }
    }

    updateLogsDisplay(logs) {
        const logsElement = document.getElementById('container-logs');
        if (logsElement) {
            logsElement.textContent = logs || 'No logs available';
            // Auto-scroll to bottom
            logsElement.scrollTop = logsElement.scrollHeight;
        }
    }

    clearLogs() {
        const logsElement = document.getElementById('container-logs');
        if (logsElement) {
            logsElement.textContent = 'Logs cleared';
        }
    }

    updateStatusDisplay(status) {
        // Update container status
        const containerStatusIcon = document.getElementById('docker-container-status');
        const containerStatusText = document.getElementById('container-status-text');
        
        if (containerStatusIcon && containerStatusText) {
            if (status.running) {
                containerStatusIcon.className = 'status-icon running';
                containerStatusText.textContent = 'Running';
            } else {
                containerStatusIcon.className = 'status-icon stopped';
                containerStatusText.textContent = 'Stopped';
            }
        }

        // Update connection status
        const connectionStatusIcon = document.getElementById('docker-connection-status');
        const connectionStatusText = document.getElementById('connection-status-text');
        const connectionStatusBadge = document.getElementById('connection-status-badge');
        
        if (connectionStatusIcon && connectionStatusText) {
            if (status.connected) {
                connectionStatusIcon.className = 'status-icon running';
                connectionStatusText.textContent = 'Connected';
                if (connectionStatusBadge) {
                    connectionStatusBadge.textContent = 'Connected';
                    connectionStatusBadge.className = 'connected';
                }
            } else {
                connectionStatusIcon.className = 'status-icon stopped';
                connectionStatusText.textContent = 'Disconnected';
                if (connectionStatusBadge) {
                    connectionStatusBadge.textContent = 'Disconnected';
                    connectionStatusBadge.className = 'disconnected';
                }
            }
        }

        // Update health status
        const healthStatusIcon = document.getElementById('docker-health-status');
        const healthStatusText = document.getElementById('health-status-text');
        
        if (healthStatusIcon && healthStatusText) {
            if (status.healthy) {
                healthStatusIcon.className = 'status-icon running';
                healthStatusText.textContent = 'Healthy';
            } else {
                healthStatusIcon.className = 'status-icon stopped';
                healthStatusText.textContent = 'Unhealthy';
            }
        }

        // Update port status
        const portStatusText = document.getElementById('port-status-text');
        if (portStatusText) {
            portStatusText.textContent = status.ports || '7474';
        }
    }

    updateContainerDetails(details) {
        if (!details) return;

        // Update container details
        const containerName = document.getElementById('container-name');
        const containerImage = document.getElementById('container-image');
        const portMapping = document.getElementById('port-mapping');
        const memoryUsage = document.getElementById('memory-usage');
        const cpuUsage = document.getElementById('cpu-usage');
        const uptime = document.getElementById('uptime');

        if (containerName) containerName.textContent = details.name || this.containerName;
        if (containerImage) containerImage.textContent = details.image || 'neo4j:latest';
        if (portMapping) portMapping.textContent = details.ports || '7474:7474, 7687:7687';
        if (memoryUsage) memoryUsage.textContent = details.memory || '--';
        if (cpuUsage) cpuUsage.textContent = details.cpu || '--';
        if (uptime) uptime.textContent = details.uptime || '--';
    }

    startAutoRefresh() {
        // Refresh status every 30 seconds
        this.autoRefreshInterval = setInterval(() => {
            this.loadDockerStatus();
        }, 30000);
    }

    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
    }

    startLogsAutoRefresh() {
        // Refresh logs every 10 seconds
        this.logsAutoRefreshInterval = setInterval(() => {
            this.loadContainerLogs();
        }, 10000);
    }

    stopLogsAutoRefresh() {
        if (this.logsAutoRefreshInterval) {
            clearInterval(this.logsAutoRefreshInterval);
            this.logsAutoRefreshInterval = null;
        }
    }

    showLoading(message) {
        const loadingElement = document.getElementById('docker-loading-indicator');
        if (loadingElement) {
            const loadingText = loadingElement.querySelector('.loading-text');
            if (loadingText) {
                loadingText.textContent = message;
            }
            loadingElement.style.display = 'flex';
        }
    }

    hideLoading() {
        const loadingElement = document.getElementById('docker-loading-indicator');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type) {
        // Simple notification display
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at the top of the card body
        const cardBody = document.querySelector('.docker-management-container .card-body');
        cardBody.insertBefore(notification, cardBody.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    copyConnectionString() {
        const connectionString = 'cypher-shell -u neo4j -p Neo4j123 -a neo4j://localhost:7687';
        
        navigator.clipboard.writeText(connectionString).then(() => {
            this.showSuccess('Connection string copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy connection string:', err);
            this.showError('Failed to copy connection string');
        });
    }

    showExamplesModal() {
        // Trigger the examples modal from the query interface
        const examplesBtn = document.getElementById('examples-query');
        if (examplesBtn) {
            examplesBtn.click();
        } else {
            this.showError('Examples modal not available');
        }
    }

    showCypherShellCommand() {
        const command = 'cypher-shell -u neo4j -p Neo4j123 -a neo4j://localhost:7687';
        const message = `
            <strong>Cypher Shell Command:</strong><br>
            <code>${command}</code><br><br>
            <small>Copy this command to your terminal to connect to Neo4j using Cypher Shell.</small>
        `;
        
        // Create a modal to show the command
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-terminal me-2"></i>Cypher Shell Command
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${message}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" id="copy-cypher-command-btn">
                            <i class="fas fa-copy me-2"></i>Copy Command
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Show the modal
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        // Add copy functionality
        document.getElementById('copy-cypher-command-btn')?.addEventListener('click', () => {
            navigator.clipboard.writeText(command).then(() => {
                this.showSuccess('Command copied to clipboard!');
                bootstrapModal.hide();
            }).catch(err => {
                console.error('Failed to copy command:', err);
                this.showError('Failed to copy command');
            });
        });
        
        // Clean up modal when hidden
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }

    cleanup() {
        this.stopAutoRefresh();
        this.stopLogsAutoRefresh();
    }
}

// Export for modular usage
export default DockerManagementComponent; 