/**
 * AASX ETL Pipeline Core - Bidirectional
 * Main ETL pipeline functionality for bidirectional AASX conversion
 * Supports: AASX → Structured Data + Documents AND Structured Data + Documents → AASX
 */

import { formatFileSize, getFileStatusInfo } from '/static/js/shared/utils.js';
import { showSuccess, showError, showWarning } from '/static/js/shared/alerts.js';

export class AASXETLPipeline {
    constructor() {
        this.conversionMode = 'aasx-to-structured';
        this.processingMode = 'batch';
        this.batchSize = 10;
        this.files = [];
        this.selectedFiles = new Set();
        this.isProcessing = false;
        this.currentProgress = { overall: 0 };
        this.progressInterval = null;
        
        // Authentication state (will be updated by global auth manager)
        this.isAuthenticated = false;
        this.currentUser = null;
    }

    async init() {
        console.log('🚀 AASX ETL Pipeline initializing...');
        
        // Wait for auth manager to be ready first
        await this.waitForAuthManager();
        
        // Initialize UI components
        this.initializeProgressCircles();
        this.setupModeSwitching();
        this.initializeEventListeners();
        
        // Initialize dropdowns and load initial data
        await this.initializeDropdowns();
        await this.refreshFiles();
        
        console.log('✅ AASX ETL Pipeline initialized');
    }





    /**
     * Wait for global auth manager to be ready
     */
    async waitForAuthManager() {
        console.log('🔐 ETL Pipeline: Waiting for global auth manager...');
        
        // Wait for global auth manager to be ready
        while (!window.authManager) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        console.log('✅ ETL Pipeline: Global auth manager ready');
        
        // Initial auth state setup
        this.updateAuthState();
        
        // Listen for auth changes
        window.addEventListener('authStateChanged', () => {
            console.log('🔄 ETL Pipeline: Auth state changed, updating...');
            this.updateAuthState();
        });
        
        // 🚫 CRITICAL FIX: Remove duplicate loginSuccess listener - PostLoginOrchestrator handles this
        // window.addEventListener('loginSuccess', async () => {
        //     console.log('🔐 ETL Pipeline: Login success detected');
        //     this.updateAuthState();
        //     
        //     // 🚀 WORLD-CLASS: Immediately refresh user data after login
        //     console.log('🔄 ETL Pipeline: Refreshing user data after login...');
        //     try {
        //             await this.refreshFiles();
        //             console.log('✅ ETL Pipeline: User data refreshed successfully after login');
        //         } catch (summary: '❌ ETL Pipeline: Failed to refresh user data after login:', error);
        //         }
        // });
        
        window.addEventListener('logout', () => {
            console.log('🔐 ETL Pipeline: Logout detected');
            this.updateAuthState();
        });
    }

    /**
     * Update authentication state from global auth manager
     */
    updateAuthState() {
        if (!window.authManager) return;
        
        try {
            const sessionInfo = window.authManager.getSessionInfo();
            console.log('🔐 ETL Pipeline: Auth state update:', sessionInfo);
            
            // Update local state based on global auth manager
            this.isAuthenticated = sessionInfo.isAuthenticated;
            this.currentUser = sessionInfo.user;
            
        } catch (error) {
            console.warn('⚠️ ETL Pipeline: Error updating auth state:', error);
        }
    }

    /**
     * Get current authentication state from global auth manager
     */
    getCurrentAuthState() {
        // Try multiple ways to get the auth state
        if (window.authSystemManager && window.authSystemManager.authManager) {
            const state = window.authSystemManager.authManager.getCurrentState();
            console.log('🔐 ETL Pipeline: Got auth state from authSystemManager:', state);
            return state;
        }
        
        // Fallback: check if we have a stored token
        const token = this.getStoredToken();
        if (token) {
            console.log('🔐 ETL Pipeline: Using fallback auth state (token exists)');
            return { isAuthenticated: true, user: { username: 'authenticated_user' } };
        }
        
        console.log('🔐 ETL Pipeline: No auth state available, defaulting to unauthenticated');
        return { isAuthenticated: false, user: null };
    }

    /**
     * Get authentication headers for API calls
     */
    getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        // Get current auth state and token
        const currentAuthState = this.getCurrentAuthState();
        const token = this.getStoredToken();
        
        if (!token) {
            console.log(`🔐 ETL Pipeline: No auth token available - making unauthenticated request (Auth: ${currentAuthState.isAuthenticated ? 'Yes' : 'No'})`);
        } else {
            console.log(`🔐 ETL Pipeline: Auth token available - making authenticated request (User: ${currentAuthState.user?.username || 'Unknown'})`);
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        return headers;
    }

    /**
     * Get stored authentication token
     * @returns {string|null} Stored token or null
     */
    getStoredToken() {
        try {
            // Try to get token from auth manager first
            if (window.authManager && typeof window.authManager.getStoredToken === 'function') {
                return window.authManager.getStoredToken();
            }
            
            // Fallback to localStorage
            return localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
        } catch (error) {
            console.warn('⚠️ Could not retrieve stored token:', error);
            return null;
        }
    }

    setupModeSwitching() {
        // Only target tabs within the ETL Pipeline section
        const etlSection = document.querySelector('.aasx-etl-pipeline-section');
        if (!etlSection) {
            console.error('❌ ETL Pipeline section not found');
            return;
        }
        
        const modeTabs = etlSection.querySelectorAll('.aasx-etl-mode-tab');
        
        modeTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const mode = tab.dataset.mode;
                this.switchConversionMode(mode);
            });
        });
    }

    initializeEventListeners() {
        // ETL pipeline controls
        $('#startEtlBtn').on('click', () => {
            console.log('🔘 Start ETL button clicked');
            this.runETLPipeline();
        });
        $('#runSelectedPipeline').on('click', () => {
            console.log('🔘 Run Selected Pipeline button clicked');
            this.runETLPipeline();
        });
        $('#runAllData').on('click', () => {
            console.log('🔘 Run All Data button clicked');
            this.runETLPipeline();
        });
        // Refresh button
        $('#refreshEtlFiles').on('click', async () => {
            console.log('🔄 ETL Pipeline: Refresh button clicked');
            
            // Refresh dropdowns first
            if (window.dropdownManager) {
                await window.dropdownManager.refreshETLPipelineDropdowns();
            }
            
            // Then refresh files
            await this.refreshFiles();
        });
        
        // File selection
        $('#selectAllFiles').on('change', (e) => this.toggleSelectAll(e.target.checked));
        $('#invertSelection').on('click', () => this.invertSelection());
        
        // Configuration
        $('#resetConfig').on('click', () => this.resetConfig());
        $('#savePreset').on('click', () => this.savePreset());
        

        
        // Preset loading
        $('.preset-btn').on('click', (e) => {
            const presetName = $(e.target).data('preset');
            this.loadPreset(presetName);
        });
        
        // Project selection change
        $('#etlProjectSelect').on('change', () => {
            const projectId = $('#etlProjectSelect').val();
            if (!projectId) {
                // Clear files when no project is selected
                this.files = [];
                this.selectedFiles.clear();
                this.renderFileList();
            } else {
                // Refresh files for selected project
                this.refreshFiles();
            }
        });
        
        console.log('📋 ETL Pipeline (Bidirectional) event listeners setup complete');
    }



    switchConversionMode(mode) {
        console.log(`🔄 Switching conversion mode to: ${mode}`);
        
        this.conversionMode = mode;
        
        // Update active tab using vanilla JavaScript (like file upload)
        const etlSection = document.querySelector('.aasx-etl-pipeline-section');
        const allTabs = etlSection.querySelectorAll('.aasx-etl-mode-tab');
        
        allTabs.forEach(tab => {
            tab.classList.remove('active');
        });
        
        const activeTab = etlSection.querySelector(`[data-mode="${mode}"]`);
        if (activeTab) {
            activeTab.classList.add('active');
        }
        
        // Show/hide relevant configuration sections
        if (mode === 'aasx-to-structured') {
            $('#aasxToStructuredConfig').show();
            $('#structuredToAasxConfig').hide();
        } else {
            $('#aasxToStructuredConfig').hide();
            $('#structuredToAasxConfig').show();
        }
        
        // Update display
        this.updateConversionModeDisplay();
        
        // 🔄 Refresh data when switching modes to provide clean slate
        this.refreshDataForModeSwitch();
    }
    
    refreshDataForModeSwitch() {
        console.log(`🔄 Refreshing data for mode switch to: ${this.conversionMode}`);
        
        // Show refresh indicator
        this.showModeChangeIndicator();
        
        // Clear current selections
        this.selectedFiles.clear();
        this.updateSelectedCount();
        
        // Reset dropdowns to default state
        this.resetDropdowns();
        
        // Reload use cases and projects
        this.loadProjectsAndUseCases();
        
        // Clear file list until new project is selected
        this.clearFileList();
        
        // Update UI to reflect fresh state
        this.updateUIForFreshState();
    }
    
    showModeChangeIndicator() {
        // Show a brief indicator that the mode has changed
        const modeText = this.conversionMode === 'aasx-to-structured' ? 'AASX → Structured' : 'Structured → AASX';
        console.log(`🔄 Mode switched to: ${modeText}`);
        
        // You can add a toast notification here if needed
        // For now, console log provides feedback
    }
    
    resetDropdowns() {
        console.log('🔄 Resetting dropdowns for fresh mode');
        
        // Reset use case dropdown
        const useCaseSelect = document.querySelector('#useCaseSelect');
        if (useCaseSelect) {
            useCaseSelect.selectedIndex = 0;
        }
        
        // Reset project dropdown
        const projectSelect = document.querySelector('#projectSelect');
        if (projectSelect) {
            projectSelect.innerHTML = '<option value="">Select a project...</option>';
            projectSelect.selectedIndex = 0;
        }
    }
    
    clearFileList() {
        console.log('🔄 Clearing file list for mode switch');
        
        const container = $('#fileListContainer');
        if (container.length) {
            container.html(`
                <div class="text-center text-muted py-4">
                    <i class="fas fa-arrow-up fa-3x mb-3"></i>
                    <p>Select a use case and project to view available files</p>
                </div>
            `);
        }
    }
    
    updateUIForFreshState() {
        console.log('🔄 Updating UI for fresh state');
        
        // Disable ETL button until files are selected
        const startButton = document.querySelector('#startEtlBtn');
        if (startButton) {
            startButton.disabled = true;
            startButton.textContent = 'Select Files to Process';
        }
        
        // Update file count display
        this.updateSelectedCount();
    }

    updateConversionModeDisplay() {
        // ETL Pipeline header should stay as "ETL Pipeline Management" always
        // Only the tab colors should change, not the main header
        console.log(`🔄 ETL Pipeline mode updated to: ${this.conversionMode}`);
    }

    updateFileListForExtraction() {
        // Update file list to show files uploaded for extraction (job_type = 'extraction')
        const fileListContainer = $('#etlFilesList');
        if (fileListContainer.length) {
            fileListContainer.find('.file-item').each((index, element) => {
                const fileElement = $(element);
                const jobType = fileElement.data('job-type') || fileElement.attr('data-job-type');
                if (jobType === 'extraction') {
                    fileElement.show();
                } else {
                    fileElement.hide();
                }
            });
        }
    }

    updateFileListForGeneration() {
        // Update file list to show files uploaded for generation (job_type = 'generation')
        const fileListContainer = $('#etlFilesList');
        if (fileListContainer.length) {
            fileListContainer.find('.file-item').each((index, element) => {
                const fileElement = $(element);
                const jobType = fileElement.data('job-type') || fileElement.attr('data-job-type');
                if (jobType === 'generation') {
                    fileElement.show();
                } else {
                    fileElement.hide();
                }
            });
        }
    }

    initializeProgressCircles() {
        try {
            // Initialize overall progress circle with 0 progress
            this.updateProgressCircle('overallProgress', 0);
        } catch (error) {
            console.warn('Progress circles initialization failed:', error.message);
        }
    }

    updateProgressCircle(elementId, progress) {
        const element = document.getElementById(elementId);
        if (!element) {
            console.warn(`Progress circle element not found: ${elementId}`);
            return;
        }
        
        const circle = element.querySelector('.progress-ring__circle');
        const text = element.querySelector('.progress-text');
        
        if (!circle || !text) {
            console.warn(`Progress circle components not found in element: ${elementId}`);
            return;
        }
        
        const radius = circle.r.baseVal.value;
        const circumference = radius * 2 * Math.PI;
        
        circle.style.strokeDasharray = `${circumference} ${circumference}`;
        circle.style.strokeDashoffset = circumference;
        
        const offset = circumference - (progress / 100) * circumference;
        circle.style.strokeDashoffset = offset;
        
        text.textContent = `${Math.round(progress)}%`;
    }

    getETLConfiguration() {
        // Get configuration from the ETL configuration form
        const config = {
            processingMode: 'standard',
            parallelProcessing: true,
            dataQuality: 'basic',
            outputFormats: ['json', 'yaml'],
            databaseExport: ['sqlite'],
            federatedLearningConsent: 'not_allowed',
            aiRag: false,
            embeddingModel: 'openai'
        };
        
        try {
            // Get federated learning consent from radio buttons
            const federatedLearningRadio = document.querySelector('input[name="federatedLearningConsent"]:checked');
            if (federatedLearningRadio) {
                config.federatedLearningConsent = federatedLearningRadio.value;
            }
            
            // Get processing mode
            const processingModeRadio = document.querySelector('input[name="processingMode"]:checked');
            if (processingModeRadio) {
                config.processingMode = processingModeRadio.value;
            }
            
            // Get data quality
            const dataQualityRadio = document.querySelector('input[name="dataQuality"]:checked');
            if (dataQualityRadio) {
                config.dataQuality = dataQualityRadio.value;
            }
            
            // Get parallel processing
            const parallelCheckbox = document.getElementById('parallelProcessing');
            if (parallelCheckbox) {
                config.parallelProcessing = parallelCheckbox.checked;
            }
            
            // Get AI/RAG setting
            const aiRagCheckbox = document.getElementById('enableAiRag');
            if (aiRagCheckbox) {
                config.aiRag = aiRagCheckbox.checked;
            }
            
            // Get embedding model
            const embeddingSelect = document.getElementById('embeddingModel');
            if (embeddingSelect) {
                config.embeddingModel = embeddingSelect.value;
            }
            
            console.log('📋 ETL Configuration retrieved:', config);
        } catch (error) {
            console.warn('⚠️ Error getting ETL configuration, using defaults:', error);
        }
        
        return config;
    }

    async runETLPipeline() {
        console.log(`🚀 ETL Pipeline execution started (Mode: ${this.conversionMode})`);
        
        if (this.isProcessing) {
            console.log('⚠️ Pipeline is already running, aborting');
            showWarning('Pipeline is already running');
            return;
        }

        const config = this.getETLConfiguration();
        const selectedFiles = this.getSelectedFiles();
        
        console.log('📋 ETL Configuration:', config);
        console.log('📁 Selected Files:', selectedFiles);

        if (selectedFiles.length === 0) {
            console.log('⚠️ No files selected, aborting');
            showWarning('Please select at least one file to process');
            return;
        }

        console.log('✅ Starting ETL processing...');
        this.isProcessing = true;
        this.showETLProgress();
        this.startProgressSimulation();

        try {
            const endpoint = this.conversionMode === 'aasx-to-structured' 
                ? '/api/aasx-etl/etl/extract-aasx' 
                : '/api/aasx-etl/etl/generate-aasx';
            
            console.log(`📡 Making API call to ${endpoint}`);
            console.log('📤 Request payload:', {
                files: selectedFiles,
                config: config,
                mode: this.conversionMode
            });
            
            // Create request body with IDs (no reverse engineering needed!)
            const useCaseId = $('#useCaseSelect').val();
            const projectId = $('#etlProjectSelect').val();
            
            const requestBody = {
                ...config,
                use_case_id: useCaseId,
                project_id: projectId,
                file_ids: selectedFiles,  // These are now file IDs, not filenames
                conversionMode: this.conversionMode
            };
            
            console.log('📤 Request payload:', requestBody);
            
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(requestBody)
            });

            console.log('📡 API Response status:', response.status);
            console.log('📡 API Response ok:', response.ok);

            if (response.ok) {
                const result = await response.json();
                console.log('✅ API call successful, result:', result);
                this.showETLResults(result);
            } else {
                const error = await response.json();
                console.log('❌ API call failed, error:', error);
                showError(`ETL Pipeline failed: ${error.detail}`);
            }
        } catch (error) {
            console.log('💥 API call exception:', error);
            showError(`ETL Pipeline error: ${error.message}`);
        } finally {
            console.log('🏁 ETL Pipeline execution finished');
            this.isProcessing = false;
            this.stopProgressSimulation();
        }
    }

    startProgressSimulation() {
        this.progressInterval = setInterval(() => {
            this.currentProgress.overall += Math.random() * 5;
            if (this.currentProgress.overall > 100) this.currentProgress.overall = 100;
            this.updateETLProgress(this.currentProgress.overall);
        }, 500);
    }

    stopProgressSimulation() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
    }

    updateETLProgress(overall) {
        this.updateProgressCircle('overallProgress', overall);
    }

    showETLProgress() {
        $('#etlProgressSection').show();
        $('#etlResultsSection').hide();
    }

    showETLResults(result) {
        $('#etlProgressSection').hide();
        $('#etlResultsSection').show();
        
        // Safely handle undefined arrays
        const outputFormats = result.outputFormats || [];
        const exportFormats = result.exportFormats || [];
        
        // Update results display based on conversion mode
        if (this.conversionMode === 'aasx-to-structured') {
            this.showExtractionResults(result);
        } else {
            this.showGenerationResults(result);
        }
    }

    showExtractionResults(result) {
        const resultsContainer = $('#etlResultsContent');
        if (!resultsContainer.length) return;

        const html = `
            <div class="etl-results-section">
                <h4><i class="fas fa-file-archive text-primary"></i> Extraction Results</h4>
                <div class="row g-3">
                    <div class="col-md-6">
                        <div class="result-stat">
                            <span class="result-number">${result.filesProcessed || 0}</span>
                            <span class="result-label">Files Processed</span>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="result-stat">
                            <span class="result-number">${result.documentsExtracted || 0}</span>
                            <span class="result-label">Documents Extracted</span>
                        </div>
                    </div>
                </div>
                
                <div class="mt-3">
                    <h5>Output Formats Generated:</h5>
                    <div class="output-formats">
                        ${this.renderOutputFormats(result.outputFormats || [])}
                    </div>
                </div>
                
                <div class="mt-3">
                    <h5>Export Formats:</h5>
                    <div class="export-formats">
                        ${this.renderExportFormats(result.exportFormats || [])}
                    </div>
                </div>
            </div>
        `;
        
        resultsContainer.html(html);
    }

    showGenerationResults(result) {
        const resultsContainer = $('#etlResultsContent');
        if (!resultsContainer.length) return;

        const html = `
            <div class="etl-results-section">
                <h4><i class="fas fa-file-code text-success"></i> Generation Results</h4>
                <div class="row g-3">
                    <div class="col-md-6">
                        <div class="result-stat">
                            <span class="result-number">${result.aasxFilesGenerated || 0}</span>
                            <span class="result-label">AASX Files Generated</span>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="result-stat">
                            <span class="result-number">${result.documentsIncluded || 0}</span>
                            <span class="result-label">Documents Included</span>
                        </div>
                    </div>
                </div>
                
                <div class="mt-3">
                    <h5>Generated AASX Files:</h5>
                    <div class="generated-files">
                        ${this.renderGeneratedFiles(result.generatedFiles || [])}
                    </div>
                </div>
                
                <div class="mt-3">
                    <h5>Processing Summary:</h5>
                    <div class="processing-summary">
                        <p><strong>Total Records:</strong> ${result.totalRecords || 0}</p>
                        <p><strong>Valid Records:</strong> ${result.validRecords || 0}</p>
                        <p><strong>Processing Time:</strong> ${result.processingTime || 'Unknown'}</p>
                    </div>
                </div>
            </div>
        `;
        
        resultsContainer.html(html);
    }

    renderOutputFormats(formats) {
        if (formats.length === 0) return '<p class="text-muted">No output formats generated</p>';
        
        return formats.map(format => `
            <span class="badge bg-primary me-2">
                <i class="fas fa-${this.getFormatIcon(format)}"></i>
                ${format.toUpperCase()}
            </span>
        `).join('');
    }

    renderExportFormats(formats) {
        if (formats.length === 0) return '<p class="text-muted">No export formats generated</p>';
        
        return formats.map(format => `
            <span class="badge bg-success me-2">
                <i class="fas fa-${this.getFormatIcon(format)}"></i>
                ${format.toUpperCase()}
            </span>
        `).join('');
    }

    renderGeneratedFiles(files) {
        if (files.length === 0) return '<p class="text-muted">No files generated</p>';
        
        return files.map(file => `
            <div class="generated-file-item">
                <i class="fas fa-file-archive text-success me-2"></i>
                <span class="file-name">${file.name}</span>
                <span class="file-size text-muted">(${file.size})</span>
            </div>
        `).join('');
    }

    getFormatIcon(format) {
        const icons = {
            'json': 'file-code',
            'yaml': 'file-alt',
            'xml': 'file-code',
            'rdf': 'sitemap',
            'graph': 'project-diagram',
            'sqlite': 'database',
            'vector_db': 'brain',
            'csv': 'file-csv',
            'excel': 'file-excel',
            'pdf': 'file-pdf'
        };
        return icons[format] || 'file';
    }

    async refreshFiles() {
        console.log('🔄 Refreshing ETL files...');
        // Get current auth state from global auth manager
        const currentAuthState = this.getCurrentAuthState();
        console.log(`🔐 ETL Pipeline: Auth state: ${currentAuthState.isAuthenticated ? 'Authenticated' : 'Demo mode'}`);
        
        try {
            const projectId = $('#etlProjectSelect').val();
            if (!projectId) {
                console.log('⚠️ No project selected, clearing file list');
                this.files = [];
                this.selectedFiles.clear();
                this.renderFileList();
                return;
            }

            const response = await fetch(`/api/aasx-etl/projects/${projectId}/files`, {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                this.files = data.files || [];
                console.log(`✅ Loaded ${this.files.length} files for project ${projectId}`);
            } else {
                console.error('❌ Failed to load files:', response.status);
                this.files = [];
            }
        } catch (error) {
            console.error('❌ Error loading files:', error);
            this.files = [];
        }
        
        // Clear selected files when refreshing
        this.selectedFiles.clear();
        this.renderFileList();
    }

    getSelectedFiles() {
        return Array.from(this.selectedFiles);
    }

    toggleSelectAll(checked) {
        console.log(`🔘 Select All: ${checked}`);
        
        if (checked) {
            // Select all files based on current mode
            this.files.forEach(file => {
                if (this.isFileCompatibleWithMode(file)) {
                    this.selectedFiles.add(file.file_id);
                }
            });
        } else {
            this.selectedFiles.clear();
        }
        
        this.updateSelectedCount();
        this.renderFileList();
    }

    isFileCompatibleWithMode(file) {
        // ✅ Updated to use job_type instead of filename extensions
        if (this.conversionMode === 'aasx-to-structured') {
            return file.job_type === 'extraction';
        } else {
            return file.job_type === 'generation';
        }
    }

    invertSelection() {
        console.log('🔘 Invert Selection');
        
        this.files.forEach(file => {
            if (this.isFileCompatibleWithMode(file)) {
                if (this.selectedFiles.has(file.file_id)) {
                    this.selectedFiles.delete(file.file_id);
                } else {
                    this.selectedFiles.add(file.file_id);
                }
            }
        });
        
        this.updateSelectedCount();
        this.renderFileList();
    }

    updateSelectedCount() {
        const count = this.selectedFiles.size;
        $('#selectedFilesCount').text(count);
        console.log(`📊 Selected files count: ${count}`);
    }

    getETLConfiguration() {
        const baseConfig = {
            conversionMode: this.conversionMode,
            processingMode: $('#processingMode').val(),
            batchSize: parseInt($('#batchSize').val()) || 10
        };

        if (this.conversionMode === 'aasx-to-structured') {
            return {
                ...baseConfig,
                outputFormats: this.getSelectedOutputFormats(),
                exportFormats: this.getSelectedExportFormats(),
                extractStructuredData: $('#extractStructuredData').is(':checked'),
                extractDocuments: $('#extractDocuments').is(':checked')
            };
        } else {
            return {
                ...baseConfig,
                includeStructuredData: $('#includeStructuredData').is(':checked'),
                includeDocuments: $('#includeDocuments').is(':checked'),
                outputFileName: $('#outputAasxFileName').val() || 'generated.aasx'
            };
        }
    }

    getSelectedOutputFormats() {
        const formats = [];
        console.log('🔍 Reading output formats from ETL configuration...');
        
        // Check each output format checkbox
        if ($('#jsonExport').is(':checked')) formats.push('json');
        if ($('#yamlExport').is(':checked')) formats.push('yaml');
        if ($('#graphExport').is(':checked')) formats.push('graph');
        if ($('#rdfExport').is(':checked')) formats.push('rdf');
        
        console.log('📋 Selected output formats:', formats);
        return formats;
    }

    getSelectedExportFormats() {
        const formats = [];
        console.log('🔍 Reading export formats from ETL configuration...');
        
        // Check each export format checkbox
        if ($('#sqliteExport').is(':checked')) formats.push('sqlite');
        if ($('#vectorDbExport').is(':checked')) formats.push('vector_db');
        
        console.log('📋 Selected export formats:', formats);
        return formats;
    }

    loadPreset(presetName) {
        const presets = {
            'minimal': {
                outputFormats: ['json'],
                exportFormats: ['sqlite'],
                processingMode: 'single',
                batchSize: 5,
                extractStructuredData: true,
                extractDocuments: false
            },
            'standard': {
                outputFormats: ['json', 'yaml'],
                exportFormats: ['sqlite', 'vector_db'],
                processingMode: 'batch',
                batchSize: 10,
                extractStructuredData: true,
                extractDocuments: true
            },
            'comprehensive': {
                outputFormats: ['json', 'yaml', 'graph', 'rdf'],
                exportFormats: ['sqlite', 'vector_db'],
                processingMode: 'batch',
                batchSize: 20,
                extractStructuredData: true,
                extractDocuments: true
            }
        };

        const preset = presets[presetName];
        if (preset) {
            // Apply preset configuration
            $('#jsonExport').prop('checked', preset.outputFormats.includes('json'));
            $('#yamlExport').prop('checked', preset.outputFormats.includes('yaml'));
            $('#graphExport').prop('checked', preset.outputFormats.includes('graph'));
            $('#rdfExport').prop('checked', preset.outputFormats.includes('rdf'));
            
            $('#sqliteExport').prop('checked', preset.exportFormats.includes('sqlite'));
            $('#vectorDbExport').prop('checked', preset.exportFormats.includes('vector_db'));
            
            $('#processingMode').val(preset.processingMode);
            $('#batchSize').val(preset.batchSize);
            
            if (preset.extractStructuredData !== undefined) {
                $('#extractStructuredData').prop('checked', preset.extractStructuredData);
            }
            if (preset.extractDocuments !== undefined) {
                $('#extractDocuments').prop('checked', preset.extractDocuments);
            }

            showSuccess(`Loaded ${presetName} preset`);
        }
    }

    savePreset() {
        const config = this.getETLConfiguration();
        const presetName = prompt('Enter preset name:');
        
        if (presetName) {
            // Save to localStorage for now
            const presets = JSON.parse(localStorage.getItem('etlPresets') || '{}');
            presets[presetName] = config;
            localStorage.setItem('etlPresets', JSON.stringify(presets));
            showSuccess(`Preset "${presetName}" saved`);
        }
    }

    resetConfig() {
        // Reset output formats
        $('#jsonExport, #yamlExport, #graphExport, #rdfExport').prop('checked', false);
        $('#sqliteExport, #vectorDbExport').prop('checked', false);
        
        // Reset processing options
        $('#processingMode').val('single');
        $('#batchSize').val('10');
        
        // Reset extraction options
        $('#extractStructuredData, #extractDocuments').prop('checked', true);
        
        // Reset generation options
        $('#includeStructuredData, #includeDocuments').prop('checked', true);
        $('#outputAasxFileName').val('generated.aasx');
        
        showSuccess('Configuration reset to defaults');
    }

    renderFileList() {
        const container = $('#etlFilesList');
        if (!container.length) return;

        if (this.files.length === 0) {
            container.html(`
                <div class="text-center text-muted py-4">
                    <i class="fas fa-folder-open fa-3x mb-3"></i>
                    <p>No files found for ${this.conversionMode === 'aasx-to-structured' ? 'AASX extraction' : 'AASX generation'}</p>
                </div>
            `);
            return;
        }

        const fileItems = this.files
            .filter(file => this.isFileCompatibleWithMode(file))
            .map(file => {
                const statusColor = this.getFileStatusColor(file.status);
                const statusText = this.getFileStatusText(file.status);
                const processingStatus = this.getProcessingStatus(file);
                const fileIcon = this.getFileIcon(file.filename || file.name);
                const sourceIcon = file.source_type === 'url_upload' ? 'globe' : 'upload';
                const isProcessing = this.isFileProcessing(file);
                const isProcessed = this.isFileProcessed(file);
                const isSelectable = !isProcessing && !isProcessed;
                
                return `
                <div class="file-item-enhanced border rounded mb-3 p-4 shadow-sm bg-white ${!isSelectable ? 'file-not-selectable' : ''}">
                    <!-- Header Section -->
                    <div class="file-header d-flex align-items-start justify-content-between mb-3">
                        <div class="d-flex align-items-start">
                            <div class="form-check me-3 mt-1">
                                <input class="form-check-input" type="checkbox" 
                                       id="file_${file.file_id || file.filename}" 
                                       ${this.selectedFiles.has(file.file_id) ? 'checked' : ''}
                                       ${!isSelectable ? 'disabled' : ''}
                                       onchange="window.aasxETLPipeline.toggleFileSelection('${file.file_id}', this.checked)">
                            </div>
                            <div class="file-icon-large me-3">
                                <div class="icon-container p-3 rounded-3 bg-light border">
                                    <i class="fas fa-${fileIcon} fa-2x text-primary"></i>
                                </div>
                            </div>
                            <div class="file-main-info">
                                <h6 class="file-name mb-1 fw-bold text-dark">${file.filename || file.name}</h6>
                                <div class="file-meta d-flex align-items-center gap-3 text-muted mb-2">
                                    <span><i class="fas fa-weight-hanging me-1"></i>${formatFileSize(file.file_size || file.size)}</span>
                                    <span><i class="fas fa-calendar-alt me-1"></i>${this.formatDate(file.created_at || file.uploadDate)}</span>
                                    <span><i class="fas fa-${sourceIcon} me-1"></i>${file.source_type === 'url_upload' ? 'URL Upload' : 'Manual Upload'}</span>
                                    <span class="badge bg-${this.getOriginalFileStatusColor(file.status)} ms-2">${this.getOriginalFileStatusText(file.status)}</span>
                                </div>
                                ${file.description ? `<p class="file-description mb-2 text-muted small">${file.description}</p>` : ''}
                            </div>
                        </div>
                        <div class="file-status-section text-end">
                            <div class="file-availability-status">
                                <small class="text-muted d-block">ETL Status</small>
                                <span class="badge bg-${statusColor} fs-6">${statusText}</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Metadata Section -->
                    <div class="file-metadata">
                        <div class="row g-3">
                            <div class="col-md-3">
                                <small class="text-muted d-block">File Type</small>
                                <span class="fw-medium">${file.file_type || this.getFileTypeFromName(file.filename || file.name)}</span>
                            </div>
                            <div class="col-md-3">
                                <small class="text-muted d-block">Job Type</small>
                                <span class="badge bg-info">${file.job_type || 'Unknown'}</span>
                            </div>
                            <div class="col-md-3">
                                <small class="text-muted d-block">Project</small>
                                <span class="fw-medium">${file.project_name || 'Unknown Project'}</span>
                            </div>
                            <div class="col-md-3">
                                <small class="text-muted d-block">Use Case</small>
                                <span class="fw-medium">${file.use_case_name || 'Unknown Use Case'}</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Actions Section -->
                    <div class="file-actions mt-3 pt-3 border-top d-flex justify-content-between align-items-center">
                        <div class="file-actions-left">
                            ${file.source_url ? `<a href="${file.source_url}" target="_blank" class="btn btn-outline-secondary btn-sm me-2"><i class="fas fa-external-link-alt me-1"></i>Source</a>` : ''}
                            <button class="btn btn-outline-primary btn-sm me-2" onclick="window.aasxETLPipeline.viewFileDetails('${file.file_id}')">
                                <i class="fas fa-info-circle me-1"></i>Details
                            </button>
                        </div>
                        <div class="file-actions-right">
                            <small class="text-muted">
                                ${isSelectable ? 
                                    `Ready for ${file.job_type === 'extraction' ? 'AASX → Structured' : 'Structured → AASX'} processing` :
                                    `${isProcessed ? 'Already processed' : 'Currently processing'} - Not available for ETL`
                                }
                            </small>
                        </div>
                    </div>
                </div>
                `;
            }).join('');

        container.html(fileItems);
        this.updateSelectedCount();
    }

    getProcessingStatus(file) {
        // Determine processing status based on file status and processing history
        const status = file.status || 'not_processed';
        
        switch (status) {
            case 'processed':
            case 'completed':
                return { color: 'success', text: 'Processed' };
            case 'processing':
            case 'in_progress':
                return { color: 'warning', text: 'Processing' };
            case 'failed':
            case 'error':
                return { color: 'danger', text: 'Failed' };
            case 'not_processed':
            case 'pending':
            default:
                return { color: 'secondary', text: 'Unprocessed' };
        }
    }

    getFileTypeFromName(filename) {
        const ext = filename.toLowerCase().split('.').pop();
        const typeMap = {
            'aasx': 'AAS Package',
            'zip': 'Archive',
            'json': 'JSON Data',
            'yaml': 'YAML Config',
            'yml': 'YAML Config',
            'xml': 'XML Document'
        };
        return typeMap[ext] || 'Unknown';
    }

    formatDate(dateString) {
        if (!dateString) return 'Unknown';
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        } catch (e) {
            return 'Invalid Date';
        }
    }

    viewFileDetails(fileId) {
        // Implementation for viewing detailed file information
        console.log(`🔍 Viewing details for file: ${fileId}`);
        // TODO: Implement file details modal or navigation
        alert(`File details feature coming soon for file: ${fileId}`);
    }

    isFileProcessing(file) {
        // Check if file is currently being processed
        const status = file.status || 'not_processed';
        return status === 'processing' || status === 'in_progress';
    }

    isFileProcessed(file) {
        // Check if file has already been processed successfully
        const status = file.status || 'not_processed';
        return status === 'processed' || status === 'completed';
    }

    getFileIcon(fileName) {
        if (fileName.toLowerCase().endsWith('.aasx')) return 'file-archive';
        if (fileName.toLowerCase().endsWith('.zip')) return 'file-archive';
        if (fileName.toLowerCase().endsWith('.json')) return 'file-code';
        if (fileName.toLowerCase().endsWith('.yaml')) return 'file-alt';
        return 'file';
    }

    toggleFileSelection(fileId, checked) {
        if (checked) {
            this.selectedFiles.add(fileId);
        } else {
            this.selectedFiles.delete(fileId);
        }
        this.updateSelectedCount();
    }

    getFileStatusColor(status) {
        // Simplified colors to match availability logic
        const processingStates = ['processing', 'in_progress'];
        const completedStates = ['completed', 'processed'];
        
        if (processingStates.includes(status)) {
            return 'warning';     // Orange for processing
        } else if (completedStates.includes(status)) {
            return 'info';        // Blue for already processed
        } else {
            return 'success';     // Green for available
        }
    }

    getFileStatusText(status) {
        // Simplified to show processing availability for ETL
        const processingStates = ['processing', 'in_progress'];
        const completedStates = ['completed', 'processed'];
        
        if (processingStates.includes(status)) {
            return 'Processing';  // Cannot be selected
        } else if (completedStates.includes(status)) {
            return 'Processed';   // Cannot be selected (already done)
        } else {
            return 'Available';   // Can be selected for processing
        }
    }

    getOriginalFileStatusText(status) {
        // Traditional file status for the top badge
        const texts = {
            'not_processed': 'Unprocessed',
            'ready': 'Ready',
            'active': 'Active',
            'processing': 'Processing',
            'completed': 'Completed', 
            'processed': 'Processed',
            'failed': 'Failed',
            'error': 'Error',
            'pending': 'Pending'
        };
        return texts[status] || 'Active';
    }

    getOriginalFileStatusColor(status) {
        // Traditional colors for the top badge
        const colors = {
            'not_processed': 'secondary',
            'ready': 'success',
            'active': 'success',
            'processing': 'warning',
            'completed': 'info',
            'processed': 'info', 
            'failed': 'danger',
            'error': 'danger',
            'pending': 'secondary'
        };
        return colors[status] || 'success';
    }

    destroy() {
        // Clean up event listeners
        $('#runSelectedPipeline, #runAllData, #refreshEtlFiles').off('click');
        $('#selectAllFiles').off('change');
        $('#invertSelection, #resetConfig, #savePreset').off('click');
        $('.preset-btn').off('click');
        $('#etlProjectSelect').off('change');
        
        // Clean up vanilla JavaScript event listeners
        const modeTabs = document.querySelectorAll('.aasx-mode-tab');
        modeTabs.forEach(tab => {
            tab.removeEventListener('click', () => {});
        });
        
        // Clear intervals
        this.stopProgressSimulation();
        
        this.isInitialized = false;
        console.log('🧹 AASX ETL Pipeline destroyed');
    }

    /**
     * Initialize dropdowns and integrate with dropdown manager
     */
    async initializeDropdowns() {
        console.log('🔄 ETL Pipeline: Initializing dropdowns...');
        
        // Wait for dropdown manager to be ready
        await this.waitForDropdownManager();
        
        // Populate ETL Pipeline dropdowns
        if (window.dropdownManager.populateETLPipelineDropdownsOnDemand()) {
            console.log('✅ ETL Pipeline: Dropdowns populated successfully');
        } else {
            console.warn('⚠️ ETL Pipeline: Failed to populate dropdowns');
        }
        
        // Set up use case change handler
        this.setupUseCaseChangeHandler();
        
        console.log('✅ ETL Pipeline: Dropdowns initialized');
    }

    /**
     * Wait for dropdown manager to be ready
     */
    async waitForDropdownManager() {
        console.log('⏳ ETL Pipeline: Waiting for dropdown manager...');
        
        // Wait for dropdown manager to be ready with proper timeout
        let attempts = 0;
        const maxAttempts = 50; // 5 seconds max wait
        
        while (!window.dropdownManager || !window.dropdownManager.isReady()) {
            if (attempts >= maxAttempts) {
                console.error('❌ ETL Pipeline: Timeout waiting for dropdown manager');
                throw new Error('Dropdown manager not ready after timeout');
            }
            await new Promise(resolve => setTimeout(resolve, 100));
            attempts++;
        }
        
        console.log('✅ ETL Pipeline: Dropdown manager ready');
    }

    /**
     * Set up use case change handler to load projects
     */
    setupUseCaseChangeHandler() {
        const useCaseSelect = document.getElementById('useCaseSelect');
        if (useCaseSelect) {
            useCaseSelect.addEventListener('change', async (e) => {
                const useCaseId = e.target.value;
                console.log(`🔄 ETL Pipeline: Use case changed to ${useCaseId}`);
                
                if (useCaseId) {
                    await this.loadProjectsForUseCase(useCaseId);
                } else {
                    // Clear project dropdown
                    const projectSelect = document.getElementById('etlProjectSelect');
                    if (projectSelect) {
                        projectSelect.innerHTML = '<option value="">Choose a project...</option>';
                    }
                    // Clear files
                    this.files = [];
                    this.selectedFiles.clear();
                    this.renderFileList();
                }
            });
        }
        
        // Add project change handler
        this.setupProjectChangeHandler();
    }
    
    /**
     * Set up project change handler to load files
     */
    setupProjectChangeHandler() {
        const projectSelect = document.getElementById('etlProjectSelect');
        if (projectSelect) {
            projectSelect.addEventListener('change', async (e) => {
                const projectId = e.target.value;
                console.log(`🔄 ETL Pipeline: Project changed to ${projectId}`);
                
                if (projectId) {
                    await this.refreshFiles();
                } else {
                    // Clear files when no project selected
                    this.files = [];
                    this.selectedFiles.clear();
                    this.renderFileList();
                }
            });
        }
    }

    /**
     * Load projects for a selected use case
     */
    async loadProjectsForUseCase(useCaseId) {
        try {
            console.log(`🔍 ETL Pipeline: Loading projects for use case ${useCaseId}`);
            
            // Use the dropdown manager to load projects
            const projects = await window.dropdownManager.loadProjectsForUseCase(useCaseId);
            
            // Find the project select element
            const projectSelect = document.getElementById('etlProjectSelect');
            if (!projectSelect) return;
            
            // Clear existing options
            projectSelect.innerHTML = '<option value="">Choose a project...</option>';
            
            // Add projects
            if (projects && projects.length > 0) {
                projects.forEach(project => {
                    const option = document.createElement('option');
                    option.value = project.project_id;
                    option.textContent = project.name;
                    projectSelect.appendChild(option);
                });
                
                console.log(`✅ ETL Pipeline: Populated project dropdown with ${projects.length} options`);
            } else {
                projectSelect.innerHTML = '<option value="">Choose a project...</option><option value="" disabled>No projects available for this use case</option>';
                console.log('⚠️ ETL Pipeline: No projects available for the selected use case');
            }
            
            // Clear files when project changes
            this.files = [];
            this.selectedFiles.clear();
            this.renderFileList();
        } catch (error) {
            console.error('❌ ETL Pipeline: Failed to load projects:', error);
        }
    }
}

// Export for use in other modules
window.AASXETLPipeline = AASXETLPipeline;

export default AASXETLPipeline; 