/**
 * Analysis UI Component
 * Handles data analysis, post-processing, and result interpretation
 */

export class AnalysisUIComponent {
    constructor() {
        // Authentication properties
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
        
        this.isInitialized = false;
        this.activeAnalyses = [];
        this.analysisConfig = {
            defaultMethod: 'fft',
            precision: 'high',
            enableParallel: true,
            maxWorkers: 4
        };
        this.analysisTypes = [
            'fft',
            'statistical',
            'spectral',
            'correlation',
            'regression',
            'clustering'
        ];
        
        // UI elements
        this.elements = {
            analysisContainer: null,
            analysisForm: null,
            resultsDisplay: null,
            progressIndicator: null,
            methodSelector: null,
            parameterPanel: null
        };
        
        // Event listeners
        this.eventListeners = [];
    }

    // Central Authentication Methods
    async waitForAuthSystem() {
        return new Promise((resolve) => {
            if (window.authSystemReady && window.authManager) {
                resolve();
            } else {
                const handleReady = () => {
                    window.removeEventListener('authSystemReady', handleReady);
                    resolve();
                };
                window.addEventListener('authSystemReady', handleReady);
            }
        });
    }

    updateAuthState() {
        if (window.authManager) {
            this.isAuthenticated = window.authManager.isAuthenticated;
            this.currentUser = window.authManager.currentUser;
            this.authToken = window.authManager.getStoredToken();
        }
    }

    setupAuthListeners() {
        const handleAuthChange = () => {
            this.updateAuthState();
            this.handleAuthStateChange();
        };

        window.addEventListener('authStateChanged', handleAuthChange);
        window.addEventListener('loginSuccess', handleAuthChange);
        window.addEventListener('logout', handleAuthChange);

        this.eventListeners.push(
            { event: 'authStateChanged', handler: handleAuthChange },
            { event: 'loginSuccess', handler: handleAuthChange },
            { event: 'logout', handler: handleAuthChange }
        );
    }

    handleAuthStateChange() {
        if (this.isAuthenticated) {
            this.loadUserAnalyses();
            this.enableAuthenticatedFeatures();
        } else {
            this.loadDemoAnalyses();
            this.disableAuthenticatedFeatures();
        }
    }

    clearSensitiveData() {
        this.currentUser = null;
        this.authToken = null;
        this.isAuthenticated = false;
    }

    getAuthHeaders() {
        return this.authToken ? { 'Authorization': `Bearer ${this.authToken}` } : {};
    }

    async init() {
        if (this.isInitialized) return;
        
        console.log('🔐 Initializing Analysis UI Component...');
        
        try {
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            this.initializeUI();
            this.setupEventListeners();
            await this.loadAnalysisConfiguration();
            
            this.isInitialized = true;
            console.log('✅ Analysis UI Component initialized');
        } catch (error) {
            console.error('❌ Analysis UI Component initialization failed:', error);
            throw error;
        }
    }

    initializeUI() {
        // Initialize UI elements
        this.elements.analysisContainer = document.getElementById('analysis-container');
        this.elements.analysisForm = document.getElementById('analysis-form');
        this.elements.resultsDisplay = document.getElementById('analysis-results');
        this.elements.progressIndicator = document.getElementById('analysis-progress');
        this.elements.methodSelector = document.getElementById('analysis-method');
        this.elements.parameterPanel = document.getElementById('analysis-parameters');

        if (!this.elements.analysisContainer) {
            console.warn('⚠️ Analysis container not found');
            return;
        }

        // Initialize method selector
        this.initializeMethodSelector();
    }

    initializeMethodSelector() {
        if (!this.elements.methodSelector) return;

        const optionsHtml = this.analysisTypes.map(type => 
            `<option value="${type}">${type.toUpperCase()}</option>`
        ).join('');

        this.elements.methodSelector.innerHTML = optionsHtml;
    }

    setupEventListeners() {
        // Analysis form submission
        if (this.elements.analysisForm) {
            this.elements.analysisForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.startAnalysis();
            });
        }

        // Method change
        if (this.elements.methodSelector) {
            this.elements.methodSelector.addEventListener('change', (e) => {
                this.updateParameterPanel(e.target.value);
            });
        }

        // Parameter changes
        const parameterInputs = document.querySelectorAll('[data-analysis-param]');
        parameterInputs.forEach(input => {
            input.addEventListener('change', (e) => {
                this.updateAnalysisConfig(e.target.name, e.target.value);
            });
        });
    }

    async loadAnalysisConfiguration() {
        try {
            const response = await fetch('/api/physics-modeling/analysis/config', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const config = await response.json();
                this.analysisConfig = { ...this.analysisConfig, ...config };
                this.updateConfigurationUI();
            }
        } catch (error) {
            console.error('❌ Failed to load analysis configuration:', error);
        }
    }

    updateConfigurationUI() {
        const methodSelect = document.getElementById('analysis-method');
        if (methodSelect) {
            methodSelect.value = this.analysisConfig.defaultMethod;
        }

        const precisionSelect = document.getElementById('analysis-precision');
        if (precisionSelect) {
            precisionSelect.value = this.analysisConfig.precision;
        }

        const parallelCheckbox = document.getElementById('enable-parallel');
        if (parallelCheckbox) {
            parallelCheckbox.checked = this.analysisConfig.enableParallel;
        }

        const maxWorkersInput = document.getElementById('max-workers');
        if (maxWorkersInput) {
            maxWorkersInput.value = this.analysisConfig.maxWorkers;
        }
    }

    updateParameterPanel(method) {
        if (!this.elements.parameterPanel) return;

        const parameters = this.getMethodParameters(method);
        const parametersHtml = Object.entries(parameters).map(([key, config]) => `
            <div class="form-group">
                <label for="${key}">${config.label}</label>
                <input 
                    type="${config.type}" 
                    id="${key}" 
                    name="${key}" 
                    value="${config.default}" 
                    min="${config.min || ''}" 
                    max="${config.max || ''}"
                    step="${config.step || ''}"
                    data-analysis-param
                />
                <small class="form-text">${config.description}</small>
            </div>
        `).join('');

        this.elements.parameterPanel.innerHTML = parametersHtml;
    }

    getMethodParameters(method) {
        const parameterConfigs = {
            fft: {
                windowSize: {
                    label: 'Window Size',
                    type: 'number',
                    default: 1024,
                    min: 64,
                    max: 8192,
                    description: 'Size of the FFT window'
                },
                overlap: {
                    label: 'Overlap',
                    type: 'number',
                    default: 0.5,
                    min: 0,
                    max: 0.9,
                    step: 0.1,
                    description: 'Overlap between consecutive windows'
                }
            },
            statistical: {
                confidenceLevel: {
                    label: 'Confidence Level',
                    type: 'number',
                    default: 0.95,
                    min: 0.8,
                    max: 0.99,
                    step: 0.01,
                    description: 'Statistical confidence level'
                },
                outlierThreshold: {
                    label: 'Outlier Threshold',
                    type: 'number',
                    default: 2.0,
                    min: 1.0,
                    max: 5.0,
                    step: 0.1,
                    description: 'Standard deviations for outlier detection'
                }
            },
            spectral: {
                frequencyResolution: {
                    label: 'Frequency Resolution',
                    type: 'number',
                    default: 1.0,
                    min: 0.1,
                    max: 10.0,
                    step: 0.1,
                    description: 'Frequency resolution in Hz'
                },
                smoothingFactor: {
                    label: 'Smoothing Factor',
                    type: 'number',
                    default: 0.1,
                    min: 0.0,
                    max: 1.0,
                    step: 0.01,
                    description: 'Spectral smoothing factor'
                }
            }
        };

        return parameterConfigs[method] || {};
    }

    async startAnalysis() {
        try {
            const formData = new FormData(this.elements.analysisForm);
            const analysisParams = {
                method: formData.get('method'),
                parameters: this.getFormParameters(),
                config: this.analysisConfig
            };

            this.showProgress('Starting analysis...');
            
            const response = await fetch('/api/physics-modeling/analysis/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeaders()
                },
                body: JSON.stringify(analysisParams)
            });

            if (response.ok) {
                const result = await response.json();
                this.activeAnalyses.push(result.analysisId);
                this.showProgress('Analysis running...');
                this.monitorAnalysisProgress(result.analysisId);
            } else {
                throw new Error('Failed to start analysis');
            }
        } catch (error) {
            console.error('❌ Failed to start analysis:', error);
            this.showProgress('Analysis failed to start');
        }
    }

    getFormParameters() {
        const parameters = {};
        const parameterInputs = document.querySelectorAll('[data-analysis-param]');
        
        parameterInputs.forEach(input => {
            const value = input.type === 'number' ? parseFloat(input.value) : input.value;
            parameters[input.name] = value;
        });
        
        return parameters;
    }

    async monitorAnalysisProgress(analysisId) {
        const checkProgress = async () => {
            try {
                const response = await fetch(`/api/physics-modeling/analysis/${analysisId}/status`, {
                    headers: this.getAuthHeaders()
                });
                
                if (response.ok) {
                    const status = await response.json();
                    this.updateProgress(status.progress);
                    this.showProgress(status.status);
                    
                    if (status.status === 'completed') {
                        this.loadAnalysisResults(analysisId);
                        this.activeAnalyses = this.activeAnalyses.filter(id => id !== analysisId);
                    } else if (status.status === 'running') {
                        setTimeout(checkProgress, 2000);
                    }
                }
            } catch (error) {
                console.error('❌ Failed to check analysis progress:', error);
            }
        };
        
        checkProgress();
    }

    async loadAnalysisResults(analysisId) {
        try {
            const response = await fetch(`/api/physics-modeling/analysis/${analysisId}/results`, {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const results = await response.json();
                this.displayResults(results);
                this.saveAnalysisHistory(results);
            }
        } catch (error) {
            console.error('❌ Failed to load analysis results:', error);
        }
    }

    displayResults(results) {
        if (!this.elements.resultsDisplay) return;

        const resultsHtml = `
            <div class="analysis-results">
                <h4>Analysis Results</h4>
                <div class="result-summary">
                    <div class="summary-item">
                        <span class="label">Method:</span>
                        <span class="value">${results.method}</span>
                    </div>
                    <div class="summary-item">
                        <span class="label">Duration:</span>
                        <span class="value">${results.duration}s</span>
                    </div>
                    <div class="summary-item">
                        <span class="label">Status:</span>
                        <span class="value">${results.status}</span>
                    </div>
                </div>
                <div class="result-data">
                    <h5>Data</h5>
                    <pre>${JSON.stringify(results.data, null, 2)}</pre>
                </div>
                <div class="result-metadata">
                    <h5>Metadata</h5>
                    <ul>
                        <li><strong>Parameters:</strong> ${JSON.stringify(results.parameters)}</li>
                        <li><strong>Timestamp:</strong> ${new Date(results.timestamp).toLocaleString()}</li>
                        <li><strong>Version:</strong> ${results.version}</li>
                    </ul>
                </div>
                <div class="result-actions">
                    <button onclick="exportAnalysis('${results.id}')" class="btn btn-primary">Export</button>
                    <button onclick="visualizeAnalysis('${results.id}')" class="btn btn-secondary">Visualize</button>
                </div>
            </div>
        `;

        this.elements.resultsDisplay.innerHTML = resultsHtml;
    }

    saveAnalysisHistory(results) {
        // Save to local history
        const history = JSON.parse(localStorage.getItem('analysisHistory') || '[]');
        history.unshift({
            id: results.id,
            method: results.method,
            timestamp: results.timestamp,
            status: results.status
        });
        
        // Keep only last 50 analyses
        if (history.length > 50) {
            history.splice(50);
        }
        
        localStorage.setItem('analysisHistory', JSON.stringify(history));
    }

    updateProgress(progress) {
        if (this.elements.progressIndicator) {
            this.elements.progressIndicator.style.width = `${progress}%`;
            this.elements.progressIndicator.setAttribute('aria-valuenow', progress);
        }
    }

    showProgress(message) {
        const progressElement = document.getElementById('analysis-status');
        if (progressElement) {
            progressElement.textContent = message;
        }
    }

    updateAnalysisConfig(key, value) {
        this.analysisConfig[key] = value;
        
        // Save configuration
        this.saveAnalysisConfiguration();
    }

    async saveAnalysisConfiguration() {
        try {
            const response = await fetch('/api/physics-modeling/analysis/config', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeaders()
                },
                body: JSON.stringify(this.analysisConfig)
            });

            if (response.ok) {
                console.log('✅ Analysis configuration saved');
            }
        } catch (error) {
            console.error('❌ Failed to save analysis configuration:', error);
        }
    }

    async loadUserAnalyses() {
        try {
            const response = await fetch('/api/physics-modeling/analysis/user', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                this.displayAnalysisHistory(data.analyses || []);
            }
        } catch (error) {
            console.error('❌ Failed to load user analyses:', error);
        }
    }

    async loadDemoAnalyses() {
        try {
            const response = await fetch('/api/physics-modeling/analysis/demo');
            
            if (response.ok) {
                const data = await response.json();
                this.displayAnalysisHistory(data.analyses || []);
            }
        } catch (error) {
            console.error('❌ Failed to load demo analyses:', error);
        }
    }

    displayAnalysisHistory(analyses) {
        if (!this.elements.resultsDisplay) return;

        const historyHtml = analyses.map(analysis => `
            <div class="analysis-history-item">
                <div class="analysis-info">
                    <span class="analysis-method">${analysis.method}</span>
                    <span class="analysis-date">${new Date(analysis.timestamp).toLocaleDateString()}</span>
                    <span class="analysis-status ${analysis.status}">${analysis.status}</span>
                </div>
                <div class="analysis-actions">
                    <button onclick="viewAnalysis('${analysis.id}')" class="btn btn-sm btn-primary">View</button>
                    <button onclick="exportAnalysis('${analysis.id}')" class="btn btn-sm btn-secondary">Export</button>
                </div>
            </div>
        `).join('');

        this.elements.resultsDisplay.innerHTML = `
            <div class="analysis-history">
                <h4>Analysis History</h4>
                ${historyHtml}
            </div>
        `;
    }

    enableAuthenticatedFeatures() {
        // Enable features that require authentication
        const authOnlyElements = document.querySelectorAll('[data-auth-only]');
        authOnlyElements.forEach(element => {
            element.disabled = false;
            element.style.display = 'block';
        });
    }

    disableAuthenticatedFeatures() {
        // Disable features that require authentication
        const authOnlyElements = document.querySelectorAll('[data-auth-only]');
        authOnlyElements.forEach(element => {
            element.disabled = true;
            element.style.display = 'none';
        });
    }

    async cleanup() {
        console.log('🧹 Cleaning up Analysis UI Component...');
        
        // Remove event listeners
        this.eventListeners.forEach(({ event, handler }) => {
            window.removeEventListener(event, handler);
        });
        
        // Clear sensitive data
        this.clearSensitiveData();
        
        this.isInitialized = false;
        console.log('✅ Analysis UI Component cleaned up');
    }

    async refresh() {
        if (this.isAuthenticated) {
            await this.loadUserAnalyses();
        } else {
            await this.loadDemoAnalyses();
        }
    }
}
