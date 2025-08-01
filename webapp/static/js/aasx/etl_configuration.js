/**
 * ETL Configuration Management
 * Handles ETL configuration form, validation, and dynamic updates
 */

class ETLConfigurationManager {
    constructor() {
        this.config = {
            processingMode: 'standard',
            parallelProcessing: true,
            dataQuality: 'basic',
            outputFormats: ['json', 'yaml'],
            databaseExport: ['sqlite'],
            federatedLearning: false,
            aiRag: false,
            embeddingModel: 'openai'
        };
        
        // Don't auto-initialize - let the caller decide when to init
    }
    
    init() {
        // Check if the ETL configuration form exists before initializing
        const etlConfigForm = document.getElementById('etlConfigForm');
        if (!etlConfigForm) {
            console.log('⚠️ ETL Configuration form not found, skipping initialization');
            return false;
        }
        
        this.bindEvents();
        this.updateConfigurationSummary();
        this.validateConfiguration();
        return true;
    }
    
    bindEvents() {
        // Processing mode changes
        document.querySelectorAll('input[name="processingMode"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.config.processingMode = e.target.value;
                this.updateConfigurationSummary();
                this.validateConfiguration();
            });
        });
        
        // Data quality changes
        document.querySelectorAll('input[name="dataQuality"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.config.dataQuality = e.target.value;
                this.updateConfigurationSummary();
                this.validateConfiguration();
            });
        });
        
        // Parallel processing
        const parallelCheckbox = document.getElementById('parallelProcessing');
        if (parallelCheckbox) {
            parallelCheckbox.addEventListener('change', (e) => {
                this.config.parallelProcessing = e.target.checked;
                this.updateConfigurationSummary();
            });
        }
        
        // Output formats
        const formatCheckboxes = ['jsonExport', 'yamlExport', 'graphExport', 'rdfExport'];
        formatCheckboxes.forEach(id => {
            const checkbox = document.getElementById(id);
            if (checkbox) {
                checkbox.addEventListener('change', (e) => {
                    this.updateOutputFormats();
                    this.updateConfigurationSummary();
                    this.validateConfiguration();
                });
            }
        });
        
        // Database export
        const dbCheckboxes = ['sqliteExport', 'vectorDbExport'];
        dbCheckboxes.forEach(id => {
            const checkbox = document.getElementById(id);
            if (checkbox) {
                checkbox.addEventListener('change', (e) => {
                    this.updateDatabaseExport();
                    this.updateConfigurationSummary();
                    this.validateConfiguration();
                });
            }
        });
        
        // Federated learning
        const flCheckbox = document.getElementById('enableFederatedLearning');
        if (flCheckbox) {
            flCheckbox.addEventListener('change', (e) => {
                this.config.federatedLearning = e.target.checked;
                this.updateConfigurationSummary();
                this.validateConfiguration();
            });
        }
        
        // AI/RAG processing
        const aiRagCheckbox = document.getElementById('enableAiRag');
        if (aiRagCheckbox) {
            aiRagCheckbox.addEventListener('change', (e) => {
                this.config.aiRag = e.target.checked;
                this.toggleEmbeddingModelSection();
                this.updateConfigurationSummary();
                this.validateConfiguration();
            });
        }
        
        // Embedding model selection
        const embeddingSelect = document.getElementById('embeddingModel');
        if (embeddingSelect) {
            embeddingSelect.addEventListener('change', (e) => {
                this.config.embeddingModel = e.target.value;
                this.updateConfigurationSummary();
                this.validateConfiguration();
            });
        }
    }
    
    updateOutputFormats() {
        this.config.outputFormats = [];
        
        if (document.getElementById('jsonExport')?.checked) {
            this.config.outputFormats.push('json');
        }
        if (document.getElementById('yamlExport')?.checked) {
            this.config.outputFormats.push('yaml');
        }
        if (document.getElementById('graphExport')?.checked) {
            this.config.outputFormats.push('graph');
        }
        if (document.getElementById('rdfExport')?.checked) {
            this.config.outputFormats.push('rdf');
        }
    }
    
    updateDatabaseExport() {
        this.config.databaseExport = [];
        
        if (document.getElementById('sqliteExport')?.checked) {
            this.config.databaseExport.push('sqlite');
        }
        if (document.getElementById('vectorDbExport')?.checked) {
            this.config.databaseExport.push('vector_db');
        }
    }
    
    toggleEmbeddingModelSection() {
        const embeddingSection = document.getElementById('embeddingModelSection');
        if (embeddingSection) {
            embeddingSection.style.display = this.config.aiRag ? 'block' : 'none';
        }
    }
    
    updateConfigurationSummary() {
        // Update processing summary
        const processingSummary = document.getElementById('processingSummary');
        if (processingSummary) {
            processingSummary.textContent = this.config.processingMode === 'standard' ? 'Standard' : 'Enhanced';
        }
        
        // Update quality summary
        const qualitySummary = document.getElementById('qualitySummary');
        if (qualitySummary) {
            qualitySummary.textContent = this.config.dataQuality === 'basic' ? 'Basic' : 'Enhanced';
        }
        
        // Update formats summary
        const formatsSummary = document.getElementById('formatsSummary');
        if (formatsSummary) {
            formatsSummary.textContent = this.config.outputFormats.join(', ') || 'None';
        }
        
        // Update database summary
        const databaseSummary = document.getElementById('databaseSummary');
        if (databaseSummary) {
            databaseSummary.textContent = this.config.databaseExport.join(', ') || 'None';
        }
        
        // Update privacy summary
        const privacySummary = document.getElementById('privacySummary');
        if (privacySummary) {
            privacySummary.textContent = this.config.federatedLearning ? 'Federated Learning Enabled' : 'Standard';
        }
        
        // Update AI summary
        const aiSummary = document.getElementById('aiSummary');
        if (aiSummary) {
            aiSummary.textContent = this.config.aiRag ? 'Enabled' : 'Disabled';
        }
    }
    
    validateConfiguration() {
        const validationMessages = document.getElementById('validationMessages');
        if (!validationMessages) return;
        
        validationMessages.innerHTML = '';
        const errors = [];
        const warnings = [];
        
        // Validation rules
        if (this.config.outputFormats.length === 0) {
            errors.push('At least one output format must be selected');
        }
        
        if (this.config.databaseExport.length === 0) {
            errors.push('At least one database export must be selected');
        }
        
        if (this.config.vectorDbExport && !this.config.aiRag) {
            warnings.push('Vector DB export requires AI/RAG processing to be enabled');
        }
        
        if (this.config.federatedLearning && !this.config.aiRag) {
            warnings.push('Federated learning works best with AI/RAG processing enabled');
        }
        
        if (this.config.aiRag && this.config.embeddingModel === 'openai') {
            // Check if OpenAI API key is available (this would be checked on the backend)
            warnings.push('OpenAI API key will be required for AI/RAG processing');
        }
        
        // Display errors
        errors.forEach(error => {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'alert alert-danger alert-sm';
            errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle me-1"></i>${error}`;
            validationMessages.appendChild(errorDiv);
        });
        
        // Display warnings
        warnings.forEach(warning => {
            const warningDiv = document.createElement('div');
            warningDiv.className = 'alert alert-warning alert-sm';
            warningDiv.innerHTML = `<i class="fas fa-exclamation-circle me-1"></i>${warning}`;
            validationMessages.appendChild(warningDiv);
        });
        
        return errors.length === 0;
    }
    
    getConfiguration() {
        return {
            ...this.config,
            // Add additional computed properties
            isValid: this.validateConfiguration(),
            timestamp: new Date().toISOString(),
            version: '1.0.0'
        };
    }
    
    setConfiguration(config) {
        this.config = { ...this.config, ...config };
        
        // Update UI elements
        this.updateUIFromConfig();
        this.updateConfigurationSummary();
        this.validateConfiguration();
    }
    
    updateUIFromConfig() {
        // Update processing mode
        const processingRadio = document.querySelector(`input[name="processingMode"][value="${this.config.processingMode}"]`);
        if (processingRadio) {
            processingRadio.checked = true;
        }
        
        // Update data quality
        const qualityRadio = document.querySelector(`input[name="dataQuality"][value="${this.config.dataQuality}"]`);
        if (qualityRadio) {
            qualityRadio.checked = true;
        }
        
        // Update parallel processing
        const parallelCheckbox = document.getElementById('parallelProcessing');
        if (parallelCheckbox) {
            parallelCheckbox.checked = this.config.parallelProcessing;
        }
        
        // Update output formats
        const formatMapping = {
            'json': 'jsonExport',
            'yaml': 'yamlExport',
            'graph': 'graphExport',
            'rdf': 'rdfExport'
        };
        
        Object.entries(formatMapping).forEach(([format, elementId]) => {
            const checkbox = document.getElementById(elementId);
            if (checkbox) {
                checkbox.checked = this.config.outputFormats.includes(format);
            }
        });
        
        // Update database export
        const dbMapping = {
            'sqlite': 'sqliteExport',
            'vector_db': 'vectorDbExport'
        };
        
        Object.entries(dbMapping).forEach(([db, elementId]) => {
            const checkbox = document.getElementById(elementId);
            if (checkbox) {
                checkbox.checked = this.config.databaseExport.includes(db);
            }
        });
        
        // Update federated learning
        const flCheckbox = document.getElementById('enableFederatedLearning');
        if (flCheckbox) {
            flCheckbox.checked = this.config.federatedLearning;
        }
        
        // Update AI/RAG
        const aiRagCheckbox = document.getElementById('enableAiRag');
        if (aiRagCheckbox) {
            aiRagCheckbox.checked = this.config.aiRag;
        }
        
        // Update embedding model
        const embeddingSelect = document.getElementById('embeddingModel');
        if (embeddingSelect) {
            embeddingSelect.value = this.config.embeddingModel;
        }
        
        // Update embedding model section visibility
        this.toggleEmbeddingModelSection();
    }
    
    resetToDefaults() {
        this.setConfiguration({
            processingMode: 'standard',
            parallelProcessing: true,
            dataQuality: 'basic',
            outputFormats: ['json', 'yaml'],
            databaseExport: ['sqlite'],
            federatedLearning: false,
            aiRag: false,
            embeddingModel: 'openai'
        });
    }
}

// Export for use in other modules
export default ETLConfigurationManager; 