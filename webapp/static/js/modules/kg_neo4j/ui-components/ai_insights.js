/**
 * AI Insights Tab Component - World Class Edition
 * ES6 Class-based implementation with central authentication integration
 * Features sophisticated AI-powered graph analysis and insights generation
 */

import { AuthManager } from '../../auth/auth_manager.js';
import { Logger } from '../../utils/logger.js';
import { ApiClient } from '../../api/api_client.js';

class KGAIInsightsComponent {
    constructor() {
        this.authManager = new AuthManager();
        this.logger = new Logger('KGAIInsightsComponent');
        this.apiClient = new ApiClient();
        
        // State management
        this.config = {
            confidenceThreshold: 0.8,
            aiModelType: 'gpt-4',
            analysisDepth: 'comprehensive',
            maxInsights: 50,
            autoRefresh: true
        };
        
        this.insights = [];
        this.metrics = {};
        this.currentGraphId = null;
        this.isInitialized = false;
        this.isTabActive = false;
        
        // AI model configurations
        this.aiModels = {
            'gpt-4': {
                name: 'GPT-4',
                capabilities: ['pattern_recognition', 'semantic_analysis', 'relationship_discovery'],
                maxTokens: 8192,
                costPerToken: 0.00003
            },
            'claude-3': {
                name: 'Claude-3',
                capabilities: ['logical_reasoning', 'context_understanding', 'hypothesis_generation'],
                maxTokens: 100000,
                costPerToken: 0.000015
            },
            'llama-2': {
                name: 'Llama-2',
                capabilities: ['code_analysis', 'technical_insights', 'performance_optimization'],
                maxTokens: 4096,
                costPerToken: 0.0000006
            }
        };
        
        // Initialize the component
        this.init();
    }
    
    /**
     * Initialize the AI Insights Component
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
            this.logger.error('Failed to initialize AI Insights Component:', error);
        }
    }
    
    /**
     * Initialize component functionality
     */
    async initializeComponent() {
        if (this.isInitialized) return;
        
        this.logger.info('🧠 Initializing AI Insights Component');
        
        try {
            // Load configuration
            await this.loadAIConfig();
            
            // Set up event listeners
            this.initEventListeners();
            
            // Load initial data
            await this.loadInitialData();
            
            this.isInitialized = true;
            this.logger.info('✅ AI Insights Component initialized');
            
        } catch (error) {
            this.logger.error('Failed to initialize AI Insights Component:', error);
        }
    }
    
    /**
     * Initialize event listeners
     */
    initEventListeners() {
        // Confidence threshold slider
        const confidenceSlider = document.getElementById('kg_confidenceThreshold');
        if (confidenceSlider) {
            confidenceSlider.addEventListener('input', (e) => {
                const value = e.target.value;
                this.config.confidenceThreshold = parseFloat(value);
                this.updateConfidenceDisplay(value);
            });
        }

        // AI model type changes
        const aiModelSelect = document.getElementById('kg_aiModelType');
        if (aiModelSelect) {
            aiModelSelect.addEventListener('change', () => {
                this.config.aiModelType = aiModelSelect.value;
                this.updateAIModelConfig();
            });
        }

        // Analysis depth changes
        const analysisDepthSelect = document.getElementById('kg_analysisDepth');
        if (analysisDepthSelect) {
            analysisDepthSelect.addEventListener('change', () => {
                this.config.analysisDepth = analysisDepthSelect.value;
                this.updateAIAnalysisConfig();
            });
        }
        
        // Auto-refresh toggle
        const autoRefreshToggle = document.getElementById('kg_autoRefresh');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', (e) => {
                this.config.autoRefresh = e.target.checked;
                this.toggleAutoRefresh();
            });
        }
    }
    
    /**
     * Update confidence threshold display
     */
    updateConfidenceDisplay(value) {
        const confidenceValue = document.getElementById('kg_confidenceValue');
        if (confidenceValue) {
            confidenceValue.textContent = Math.round(value * 100) + '%';
        }
    }
    
    /**
     * Update AI model configuration
     */
    updateAIModelConfig() {
        const model = this.aiModels[this.config.aiModelType];
        if (!model) return;
        
        // Update model capabilities display
        const capabilitiesEl = document.getElementById('kg_modelCapabilities');
        if (capabilitiesEl) {
            capabilitiesEl.textContent = model.capabilities.join(', ');
        }
        
        // Update cost information
        const costEl = document.getElementById('kg_modelCost');
        if (costEl) {
            costEl.textContent = `$${model.costPerToken.toFixed(8)} per token`;
        }
        
        this.logger.info(`AI model changed to: ${model.name}`);
    }
    
    /**
     * Update AI analysis configuration
     */
    updateAIAnalysisConfig() {
        this.logger.info(`Analysis depth changed to: ${this.config.analysisDepth}`);
        
        // Update UI elements based on analysis depth
        const depthElements = document.querySelectorAll('[data-analysis-depth]');
        depthElements.forEach(element => {
            const requiredDepth = element.dataset.analysisDepth;
            if (requiredDepth === this.config.analysisDepth || requiredDepth === 'all') {
                element.style.display = 'block';
            } else {
                element.style.display = 'none';
            }
        });
    }
    
    /**
     * Toggle auto-refresh functionality
     */
    toggleAutoRefresh() {
        if (this.config.autoRefresh) {
            this.startAutoRefresh();
        } else {
            this.stopAutoRefresh();
        }
    }
    
    /**
     * Start auto-refresh
     */
    startAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
        }
        
        this.autoRefreshInterval = setInterval(() => {
            if (this.isTabActive) {
                this.refreshAIInsights();
            }
        }, 300000); // 5 minutes
        
        this.logger.info('Auto-refresh started');
    }
    
    /**
     * Stop auto-refresh
     */
    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
        
        this.logger.info('Auto-refresh stopped');
    }
    
    /**
     * Load initial data
     */
    async loadInitialData() {
        try {
            // Get current graph ID
            this.currentGraphId = this.getCurrentGraphId();
            
            if (this.currentGraphId) {
                // Load existing AI insights
                await this.loadExistingAIInsights();
                
                // Load AI metrics
                await this.updateAIMetrics();
            } else {
                // Generate mock data for demonstration
                this.generateMockData();
            }
        } catch (error) {
            this.logger.error('Error loading initial data:', error);
            // Fallback to mock data
            this.generateMockData();
        }
    }
    
    /**
     * Load existing AI insights
     */
    async loadExistingAIInsights() {
        try {
            const response = await this.apiClient.get('/api/ai-insights/list', {
                params: { graphId: this.currentGraphId },
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.insights = response.data.insights || [];
                this.updateInsightsDisplay();
            }
            
        } catch (error) {
            this.logger.error('Failed to load existing AI insights:', error);
        }
    }
    
    /**
     * Update AI metrics
     */
    async updateAIMetrics() {
        try {
            const response = await this.apiClient.get('/api/ai-insights/metrics', {
                params: { graphId: this.currentGraphId },
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.metrics = response.data.metrics || {};
                this.updateMetricsDisplay();
            }
            
        } catch (error) {
            this.logger.error('Failed to update AI metrics:', error);
        }
    }
    
    /**
     * Generate AI insights
     */
    async generateAIInsights() {
        try {
            this.logger.info('🧠 Generating AI insights...');
            
            const requestData = {
                graphId: this.currentGraphId,
                modelType: this.config.aiModelType,
                analysisDepth: this.config.analysisDepth,
                confidenceThreshold: this.config.confidenceThreshold,
                maxInsights: this.config.maxInsights
            };
            
            const response = await this.apiClient.post('/api/ai-insights/generate', requestData, {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.insights = response.data.insights || [];
                this.updateInsightsDisplay();
                this.showSuccess('AI insights generated successfully');
                
                // Update metrics
                await this.updateAIMetrics();
                
            } else {
                this.showError(response.message || 'Failed to generate AI insights');
            }
            
        } catch (error) {
            this.logger.error('Failed to generate AI insights:', error);
            this.showError('Failed to generate AI insights');
        }
    }
    
    /**
     * Create AI graph visualization
     */
    async createAIGraph() {
        try {
            this.logger.info('📊 Creating AI graph visualization...');
            
            const requestData = {
                graphId: this.currentGraphId,
                insights: this.insights,
                visualizationType: 'ai_enhanced',
                layout: 'force_directed'
            };
            
            const response = await this.apiClient.post('/api/ai-insights/visualize', requestData, {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.showSuccess('AI graph visualization created successfully');
                // Trigger graph update
                if (window.loadGraphData) {
                    window.loadGraphData();
                }
            } else {
                this.showError(response.message || 'Failed to create AI graph visualization');
            }
            
        } catch (error) {
            this.logger.error('Failed to create AI graph visualization:', error);
            this.showError('Failed to create AI graph visualization');
        }
    }
    
    /**
     * Save AI configuration
     */
    async saveAIConfig() {
        try {
            this.logger.info('💾 Saving AI configuration...');
            
            const response = await this.apiClient.post('/api/ai-insights/config', this.config, {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.showSuccess('AI configuration saved successfully');
                // Store in localStorage as backup
                localStorage.setItem('kg_ai_config', JSON.stringify(this.config));
            } else {
                this.showError(response.message || 'Failed to save AI configuration');
            }
            
        } catch (error) {
            this.logger.error('Failed to save AI configuration:', error);
            this.showError('Failed to save AI configuration');
        }
    }
    
    /**
     * Refresh AI insights
     */
    async refreshAIInsights() {
        try {
            this.logger.info('🔄 Refreshing AI insights...');
            
            await Promise.all([
                this.loadExistingAIInsights(),
                this.updateAIMetrics()
            ]);
            
            this.showSuccess('AI insights refreshed successfully');
            
        } catch (error) {
            this.logger.error('Failed to refresh AI insights:', error);
            this.showError('Failed to refresh AI insights');
        }
    }
    
    /**
     * Export AI insights
     */
    async exportAIInsights() {
        try {
            if (this.insights.length === 0) {
                this.showError('No insights to export');
                return;
            }
            
            const exportData = {
                insights: this.insights,
                metadata: {
                    generatedAt: new Date().toISOString(),
                    graphId: this.currentGraphId,
                    modelType: this.config.aiModelType,
                    analysisDepth: this.config.analysisDepth
                }
            };
            
            // Create download link
            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `ai_insights_${this.currentGraphId}_${Date.now()}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            this.showSuccess('AI insights exported successfully');
            
        } catch (error) {
            this.logger.error('Failed to export AI insights:', error);
            this.showError('Failed to export AI insights');
        }
    }
    
    /**
     * Export AI analytics
     */
    async exportAIAnalytics() {
        try {
            if (Object.keys(this.metrics).length === 0) {
                this.showError('No analytics data to export');
                return;
            }
            
            const exportData = {
                metrics: this.metrics,
                metadata: {
                    exportedAt: new Date().toISOString(),
                    graphId: this.currentGraphId,
                    config: this.config
                }
            };
            
            // Create download link
            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `ai_analytics_${this.currentGraphId}_${Date.now()}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            this.showSuccess('AI analytics exported successfully');
            
        } catch (error) {
            this.logger.error('Failed to export AI analytics:', error);
            this.showError('Failed to export AI analytics');
        }
    }
    
    /**
     * Generate AI report
     */
    async generateAIReport() {
        try {
            this.logger.info('📋 Generating AI report...');
            
            const reportData = {
                graphId: this.currentGraphId,
                insights: this.insights,
                metrics: this.metrics,
                config: this.config,
                timestamp: new Date().toISOString()
            };
            
            const response = await this.apiClient.post('/api/ai-insights/report', reportData, {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                // Create download link for report
                const blob = new Blob([response.data.report], { type: 'text/html' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `ai_report_${this.currentGraphId}_${Date.now()}.html`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                this.showSuccess('AI report generated successfully');
            } else {
                this.showError(response.message || 'Failed to generate AI report');
            }
            
        } catch (error) {
            this.logger.error('Failed to generate AI report:', error);
            this.showError('Failed to generate AI report');
        }
    }
    
    /**
     * Configure AI models
     */
    async configureAIModels() {
        try {
            this.logger.info('⚙️ Configuring AI models...');
            
            // Show configuration modal
            this.showAIConfigModal();
            
        } catch (error) {
            this.logger.error('Failed to configure AI models:', error);
            this.showError('Failed to configure AI models');
        }
    }
    
    /**
     * Save advanced AI configuration
     */
    async saveAdvancedAIConfig() {
        try {
            this.logger.info('💾 Saving advanced AI configuration...');
            
            // Get advanced config values
            const advancedConfig = {
                ...this.config,
                customParameters: this.getCustomParameters(),
                modelSpecificConfig: this.getModelSpecificConfig()
            };
            
            const response = await this.apiClient.post('/api/ai-insights/advanced-config', advancedConfig, {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.showSuccess('Advanced AI configuration saved successfully');
                localStorage.setItem('kg_ai_advanced_config', JSON.stringify(advancedConfig));
            } else {
                this.showError(response.message || 'Failed to save advanced AI configuration');
            }
            
        } catch (error) {
            this.logger.error('Failed to save advanced AI configuration:', error);
            this.showError('Failed to save advanced AI configuration');
        }
    }
    
    /**
     * Schedule AI insights
     */
    async scheduleAIInsights() {
        try {
            this.logger.info('📅 Scheduling AI insights...');
            
            const scheduleData = {
                graphId: this.currentGraphId,
                frequency: 'daily',
                time: '09:00',
                config: this.config,
                enabled: true
            };
            
            const response = await this.apiClient.post('/api/ai-insights/schedule', scheduleData, {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.showSuccess('AI insights scheduled successfully');
            } else {
                this.showError(response.message || 'Failed to schedule AI insights');
            }
            
        } catch (error) {
            this.logger.error('Failed to schedule AI insights:', error);
            this.showError('Failed to schedule AI insights');
        }
    }
    
    /**
     * Show AI help
     */
    showAIHelp() {
        try {
            this.showNotification('AI Insights Help: Use the Generate Insights button to analyze your knowledge graph with AI. Configure models and parameters as needed.', 'info');
        } catch (error) {
            this.logger.error('Error showing AI help:', error);
            this.showError('Failed to show help');
        }
    }
    
    /**
     * Get custom parameters
     */
    getCustomParameters() {
        const params = {};
        
        // Get custom parameter inputs
        const customParamInputs = document.querySelectorAll('[data-custom-param]');
        customParamInputs.forEach(input => {
            const key = input.dataset.customParam;
            const value = input.value;
            if (value) {
                params[key] = value;
            }
        });
        
        return params;
    }
    
    /**
     * Get model-specific configuration
     */
    getModelSpecificConfig() {
        const model = this.aiModels[this.config.aiModelType];
        if (!model) return {};
        
        const config = {};
        
        // Get model-specific inputs
        const modelInputs = document.querySelectorAll(`[data-model="${this.config.aiModelType}"]`);
        modelInputs.forEach(input => {
            const key = input.name || input.id;
            const value = input.value;
            if (value) {
                config[key] = value;
            }
        });
        
        return config;
    }
    
    /**
     * Update insights display
     */
    updateInsightsDisplay() {
        const insightsContainer = document.getElementById('kg_aiInsightsContainer');
        if (!insightsContainer) return;
        
        if (this.insights.length === 0) {
            insightsContainer.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-brain fa-3x text-muted mb-3"></i>
                    <p class="text-muted">No AI insights generated yet. Click "Generate Insights" to get started.</p>
                </div>
            `;
            return;
        }
        
        let insightsHTML = '';
        this.insights.forEach((insight, index) => {
            insightsHTML += `
                <div class="insight-item card mb-3" data-insight-id="${insight.id}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1">
                                <h6 class="card-title">${insight.title}</h6>
                                <p class="card-text">${insight.description}</p>
                                <div class="insight-meta">
                                    <small class="text-muted">
                                        Confidence: ${(insight.confidence * 100).toFixed(1)}% | 
                                        Type: ${insight.type} | 
                                        Generated: ${new Date(insight.generatedAt).toLocaleString()}
                                    </small>
                                </div>
                            </div>
                            <div class="btn-group btn-group-sm">
                                <button class="btn btn-outline-primary btn-sm" onclick="kgAIInsights.viewInsightDetails(${index})">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="btn btn-outline-success btn-sm" onclick="kgAIInsights.applyInsight(${index})">
                                    <i class="fas fa-check"></i>
                                </button>
                                <button class="btn btn-outline-info btn-sm" onclick="kgAIInsights.shareInsight(${index})">
                                    <i class="fas fa-share"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        insightsContainer.innerHTML = insightsHTML;
    }
    
    /**
     * Update metrics display
     */
    updateMetricsDisplay() {
        const metricsContainer = document.getElementById('kg_aiMetricsContainer');
        if (!metricsContainer) return;
        
        const metrics = this.metrics;
        if (Object.keys(metrics).length === 0) return;
        
        let metricsHTML = `
            <div class="row">
                <div class="col-md-3">
                    <div class="text-center">
                        <h4 class="text-primary">${metrics.totalInsights || 0}</h4>
                        <small class="text-muted">Total Insights</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h4 class="text-success">${(metrics.averageConfidence * 100 || 0).toFixed(1)}%</h4>
                        <small class="text-muted">Avg Confidence</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h4 class="text-info">${metrics.insightsToday || 0}</h4>
                        <small class="text-muted">Today's Insights</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h4 class="text-warning">${metrics.modelUsage || 0}</h4>
                        <small class="text-muted">Model Usage</small>
                    </div>
                </div>
            </div>
        `;
        
        metricsContainer.innerHTML = metricsHTML;
    }
    
    /**
     * Generate mock data for demonstration
     */
    generateMockData() {
        this.insights = [
            {
                id: 'insight_001',
                title: 'High Centrality Node Detected',
                description: 'Node "Product_Assembly_001" shows unusually high betweenness centrality, suggesting it\'s a critical bottleneck in the supply chain.',
                confidence: 0.92,
                type: 'performance_analysis',
                generatedAt: new Date().toISOString()
            },
            {
                id: 'insight_002',
                title: 'Anomalous Relationship Pattern',
                description: 'Detected unusual relationship density between manufacturing and quality control nodes, indicating potential process optimization opportunities.',
                confidence: 0.87,
                type: 'pattern_recognition',
                generatedAt: new Date().toISOString()
            },
            {
                id: 'insight_003',
                title: 'Resource Allocation Optimization',
                description: 'AI analysis suggests redistributing 15% of resources from over-utilized nodes to under-utilized ones could improve efficiency by 23%.',
                confidence: 0.94,
                type: 'optimization_recommendation',
                generatedAt: new Date().toISOString()
            }
        ];
        
        this.metrics = {
            totalInsights: 3,
            averageConfidence: 0.91,
            insightsToday: 3,
            modelUsage: 1
        };
        
        this.updateInsightsDisplay();
        this.updateMetricsDisplay();
    }
    
    /**
     * Load AI configuration
     */
    async loadAIConfig() {
        try {
            // Try to load from API first
            const response = await this.apiClient.get('/api/ai-insights/config', {
                headers: await this.authManager.getAuthHeaders()
            });
            
            if (response.success) {
                this.config = { ...this.config, ...response.data.config };
            }
            
        } catch (error) {
            this.logger.warn('Failed to load AI config from API, using defaults');
            
            // Fallback to localStorage
            const savedConfig = localStorage.getItem('kg_ai_config');
            if (savedConfig) {
                try {
                    this.config = { ...this.config, ...JSON.parse(savedConfig) };
                } catch (e) {
                    this.logger.warn('Failed to parse saved config, using defaults');
                }
            }
        }
        
        // Apply configuration to UI
        this.applyConfigToUI();
    }
    
    /**
     * Apply configuration to UI elements
     */
    applyConfigToUI() {
        // Update confidence threshold
        const confidenceSlider = document.getElementById('kg_confidenceThreshold');
        if (confidenceSlider) {
            confidenceSlider.value = this.config.confidenceThreshold;
            this.updateConfidenceDisplay(this.config.confidenceThreshold);
        }
        
        // Update AI model type
        const aiModelSelect = document.getElementById('kg_aiModelType');
        if (aiModelSelect) {
            aiModelSelect.value = this.config.aiModelType;
            this.updateAIModelConfig();
        }
        
        // Update analysis depth
        const analysisDepthSelect = document.getElementById('kg_analysisDepth');
        if (analysisDepthSelect) {
            analysisDepthSelect.value = this.config.analysisDepth;
            this.updateAIAnalysisConfig();
        }
        
        // Update auto-refresh
        const autoRefreshToggle = document.getElementById('kg_autoRefresh');
        if (autoRefreshToggle) {
            autoRefreshToggle.checked = this.config.autoRefresh;
            this.toggleAutoRefresh();
        }
    }
    
    /**
     * Get current graph ID
     */
    getCurrentGraphId() {
        // Try to get from URL or global state
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('graph_id') || window.currentGraphId || null;
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
     * Set tab active state
     */
    setTabActive(active) {
        this.isTabActive = active;
        
        if (active && this.config.autoRefresh) {
            this.startAutoRefresh();
        } else {
            this.stopAutoRefresh();
        }
    }
    
    /**
     * Cleanup resources
     */
    destroy() {
        // Clear intervals
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
        }
        
        this.logger.info('AI Insights Component destroyed');
    }
}

// Create global instance
const kgAIInsights = new KGAIInsightsComponent();

// Expose methods globally for HTML onclick calls
window.kgGenerateAIInsights = () => kgAIInsights.generateAIInsights();
window.kgCreateAIGraph = () => kgAIInsights.createAIGraph();
window.kgSaveAIConfig = () => kgAIInsights.saveAIConfig();
window.kgRefreshAIInsights = () => kgAIInsights.refreshAIInsights();
window.kgExportAIInsights = () => kgAIInsights.exportAIInsights();
window.kgExportAIAnalytics = () => kgAIInsights.exportAIAnalytics();
window.kgGenerateAIReport = () => kgAIInsights.generateAIReport();
window.kgConfigureAIModels = () => kgAIInsights.configureAIModels();
window.kgSaveAdvancedAIConfig = () => kgAIInsights.saveAdvancedAIConfig();
window.kgScheduleAIInsights = () => kgAIInsights.scheduleAIInsights();
window.kgShowAIHelp = () => kgAIInsights.showAIHelp();
window.kgRefreshInsights = () => kgAIInsights.refreshAIInsights();

// Export the class
export { KGAIInsightsComponent };
