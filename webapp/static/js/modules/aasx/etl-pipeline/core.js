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
        

        
        // Initialize UI components
        this.initializeProgressCircles();
        this.setupModeSwitching();
        this.initializeEventListeners();
        
        // Load initial data
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
        $('#runSelectedPipeline').on('click', () => {
            console.log('🔘 Run Selected Pipeline button clicked');
            this.runETLPipeline();
        });
        $('#runAllData').on('click', () => {
            console.log('🔘 Run All Data button clicked');
            this.runETLPipeline();
        });
        $('#refreshEtlFiles').on('click', () => this.refreshFiles());
        
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
        $('#etlProjectSelect').on('change', () => this.refreshFiles());
        
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
    }

    updateConversionModeDisplay() {
        // ETL Pipeline header should stay as "ETL Pipeline Management" always
        // Only the tab colors should change, not the main header
        console.log(`🔄 ETL Pipeline mode updated to: ${this.conversionMode}`);
    }

    updateFileListForExtraction() {
        // Update file list to show AASX files for extraction
        const fileListContainer = $('#etlFilesList');
        if (fileListContainer.length) {
            fileListContainer.find('.file-item').each((index, element) => {
                const fileName = $(element).find('.file-name').text();
                if (fileName.toLowerCase().endsWith('.aasx')) {
                    $(element).show();
                } else {
                    $(element).hide();
                }
            });
        }
    }

    updateFileListForGeneration() {
        // Update file list to show structured data files for generation
        const fileListContainer = $('#etlFilesList');
        if (fileListContainer.length) {
            fileListContainer.find('.file-item').each((index, element) => {
                const fileName = $(element).find('.file-name').text();
                if (fileName.toLowerCase().endsWith('.zip') || 
                    fileName.toLowerCase().endsWith('.json') ||
                    fileName.toLowerCase().endsWith('.yaml')) {
                    $(element).show();
                } else {
                    $(element).hide();
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
                ? '/api/aasx-etl/etl/extract' 
                : '/api/aasx-etl/etl/generate';
            
            console.log(`📡 Making API call to ${endpoint}`);
            console.log('📤 Request payload:', {
                files: selectedFiles,
                config: config,
                mode: this.conversionMode
            });
            
            // Combine files and config into a single request body
            const requestBody = {
                ...config,
                files: selectedFiles,
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
                if (this.isFileCompatibleWithMode(file.name)) {
                    this.selectedFiles.add(file.name);
                }
            });
        } else {
            this.selectedFiles.clear();
        }
        
        this.updateSelectedCount();
        this.renderFileList();
    }

    isFileCompatibleWithMode(fileName) {
        if (this.conversionMode === 'aasx-to-structured') {
            return fileName.toLowerCase().endsWith('.aasx');
        } else {
            return fileName.toLowerCase().endsWith('.zip') || 
                   fileName.toLowerCase().endsWith('.json') ||
                   fileName.toLowerCase().endsWith('.yaml');
        }
    }

    invertSelection() {
        console.log('🔘 Invert Selection');
        
        this.files.forEach(file => {
            if (this.isFileCompatibleWithMode(file.name)) {
                if (this.selectedFiles.has(file.name)) {
                    this.selectedFiles.delete(file.name);
                } else {
                    this.selectedFiles.add(file.name);
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
            .filter(file => this.isFileCompatibleWithMode(file.name))
            .map(file => `
                <div class="file-item d-flex align-items-center p-3 border-bottom">
                    <div class="form-check me-3">
                        <input class="form-check-input" type="checkbox" 
                               id="file_${file.name}" 
                               ${this.selectedFiles.has(file.name) ? 'checked' : ''}
                               onchange="window.aasxETLPipeline.toggleFileSelection('${file.name}', this.checked)">
                    </div>
                    <div class="file-icon me-3">
                        <i class="fas fa-${this.getFileIcon(file.name)} text-primary"></i>
                    </div>
                    <div class="file-info flex-grow-1">
                        <div class="file-name fw-bold">${file.name}</div>
                        <div class="file-details text-muted">
                            <small>${formatFileSize(file.size)} • ${file.uploadDate}</small>
                        </div>
                    </div>
                    <div class="file-status">
                        <span class="badge bg-${this.getFileStatusColor(file.status)}">
                            ${this.getFileStatusText(file.status)}
                        </span>
                    </div>
                </div>
            `).join('');

        container.html(fileItems);
        this.updateSelectedCount();
    }

    getFileIcon(fileName) {
        if (fileName.toLowerCase().endsWith('.aasx')) return 'file-archive';
        if (fileName.toLowerCase().endsWith('.zip')) return 'file-archive';
        if (fileName.toLowerCase().endsWith('.json')) return 'file-code';
        if (fileName.toLowerCase().endsWith('.yaml')) return 'file-alt';
        return 'file';
    }

    toggleFileSelection(filename, checked) {
        if (checked) {
            this.selectedFiles.add(filename);
        } else {
            this.selectedFiles.delete(filename);
        }
        this.updateSelectedCount();
    }

    getFileStatusColor(status) {
        const colors = {
            'ready': 'success',
            'processing': 'warning',
            'completed': 'success',
            'failed': 'danger',
            'pending': 'secondary'
        };
        return colors[status] || 'secondary';
    }

    getFileStatusText(status) {
        const texts = {
            'ready': 'Ready',
            'processing': 'Processing',
            'completed': 'Completed',
            'failed': 'Failed',
            'pending': 'Pending'
        };
        return texts[status] || 'Unknown';
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
}

// Export for use in other modules
window.AASXETLPipeline = AASXETLPipeline;

export default AASXETLPipeline; 