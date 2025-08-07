/**
 * AASX ETL Pipeline Core
 * Main ETL pipeline functionality for AASX file processing
 */

import { formatFileSize, getFileStatusInfo } from '/static/js/shared/utils.js';
import { showSuccess, showError, showWarning } from '/static/js/shared/alerts.js';

export class AASXETLPipeline {
    constructor() {
        this.isProcessing = false;
        this.isInitialized = false;
        this.progressInterval = null;
        this.currentProgress = {
            extract: 0,
            transform: 0,
            load: 0,
            overall: 0
        };
        this.files = [];
        this.selectedFiles = new Set();
    }

    async init() {
        console.log('🚀 AASX ETL Pipeline initializing...');
        
        try {
            // Initialize event listeners
            this.initializeEventListeners();
            
            // Initialize progress circles
            this.initializeProgressCircles();
            
            // Load initial files
            await this.refreshFiles();
            
            this.isInitialized = true;
            console.log('✅ AASX ETL Pipeline initialized successfully');
            
        } catch (error) {
            console.error('❌ AASX ETL Pipeline initialization failed:', error);
            showError('Failed to initialize ETL Pipeline');
        }
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
        
        console.log('📋 ETL Pipeline event listeners setup complete');
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
        
        try {
            const radius = circle.r.baseVal.value;
            const circumference = radius * 2 * Math.PI;
            const offset = circumference - (progress / 100) * circumference;
            
            circle.style.strokeDasharray = `${circumference} ${circumference}`;
            circle.style.strokeDashoffset = offset;
            text.textContent = `${Math.round(progress)}%`;
        } catch (error) {
            console.warn(`Error updating progress circle ${elementId}:`, error.message);
        }
    }

    async runETLPipeline() {
        console.log('🚀 ETL Pipeline execution started');
        
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
            console.log('📡 Making API call to /api/aasx/etl/run');
            console.log('📤 Request payload:', {
                files: selectedFiles,
                config: config
            });
            
            // Combine files and config into a single request body
            const requestBody = {
                ...config,
                files: selectedFiles
            };
            
            console.log('📤 Request payload:', requestBody);
            
            const response = await fetch('/api/aasx-etl/etl/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
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
        const processedFiles = result.processedFiles || 0;
        const duration = result.duration || 0;
        
        const resultsHtml = `
            <div class="alert alert-success">
                <h5><i class="fas fa-check-circle"></i> ETL Pipeline Completed Successfully</h5>
                <p>Processed ${processedFiles} files in ${duration} seconds</p>
            </div>
            <div class="row">
                <div class="col-md-6">
                    <h6>Output Formats Generated:</h6>
                    <ul>
                        ${outputFormats.length > 0 ? outputFormats.map(format => `<li>${format}</li>`).join('') : '<li>No output formats specified</li>'}
                    </ul>
                </div>
                <div class="col-md-6">
                    <h6>Export Formats:</h6>
                    <ul>
                        ${exportFormats.length > 0 ? exportFormats.map(format => `<li>${format}</li>`).join('') : '<li>No export formats specified</li>'}
                    </ul>
                </div>
            </div>
            <div class="mt-3">
                <h6>Processing Details:</h6>
                <pre class="bg-light p-2 rounded">${JSON.stringify(result, null, 2)}</pre>
            </div>
        `;
        
        $('#etlResults').html(resultsHtml);
    }

    async refreshFiles() {
        try {
            const projectId = $('#etlProjectSelect').val();
            if (!projectId) {
                this.files = [];
                this.renderFileList();
                return;
            }

            const response = await fetch(`/api/aasx-etl/projects/${projectId}/files`);
            if (response.ok) {
                this.files = await response.json();
                this.renderFileList();
                console.log(`📁 Loaded ${this.files.length} files for project ${projectId}`);
            } else {
                console.warn('No files found for project:', projectId);
                this.files = [];
                this.renderFileList();
            }
        } catch (error) {
            console.warn('Failed to load files:', error.message);
            this.files = [];
            this.renderFileList();
        }
    }

    getSelectedFiles() {
        const selected = Array.from(this.selectedFiles);
        console.log('📁 getSelectedFiles() called, selected files:', selected);
        console.log('📁 this.selectedFiles Set contents:', this.selectedFiles);
        
        // Send simple hierarchy information - let backend do reverse engineering
        const selectedFilesWithHierarchy = [];
        
        for (const filename of selected) {
            // Get use case and project information from the current selection
            const useCaseSelect = $('#etlUseCaseSelect');
            const projectSelect = $('#etlProjectSelect');
            
            const useCaseName = useCaseSelect.find('option:selected').text();
            const projectName = projectSelect.find('option:selected').text();
            
            selectedFilesWithHierarchy.push({
                filename: filename,
                use_case_name: useCaseName,
                project_name: projectName
            });
            
            console.log(`📋 File hierarchy: ${useCaseName}/${projectName}/${filename}`);
        }
        
        console.log('📁 Selected files with hierarchy:', selectedFilesWithHierarchy);
        return selectedFilesWithHierarchy;
    }

    toggleSelectAll(checked) {
        if (checked) {
            this.files.forEach(file => this.selectedFiles.add(file.filename));
        } else {
            this.selectedFiles.clear();
        }
        this.updateSelectedCount();
        this.renderFileList();
    }

    invertSelection() {
        this.files.forEach(file => {
            if (this.selectedFiles.has(file.filename)) {
                this.selectedFiles.delete(file.filename);
            } else {
                this.selectedFiles.add(file.filename);
            }
        });
        this.updateSelectedCount();
        this.renderFileList();
    }

    updateSelectedCount() {
        const count = this.selectedFiles.size;
        $('#selectedFileCount').text(count);
        $('#totalFileCount').text(this.files.length);
    }

    getETLConfiguration() {
        return {
            outputFormats: this.getSelectedOutputFormats(),
            exportFormats: this.getSelectedExportFormats(),
            processingMode: $('#processingMode').val(),
            batchSize: parseInt($('#batchSize').val()) || 10
        };
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
                exportFormats: ['csv'],
                processingMode: 'single',
                batchSize: 5
            },
            'standard': {
                outputFormats: ['json', 'xml'],
                exportFormats: ['csv', 'excel'],
                processingMode: 'batch',
                batchSize: 10
            },
            'comprehensive': {
                outputFormats: ['json', 'xml', 'yaml', 'rdf'],
                exportFormats: ['csv', 'excel', 'pdf'],
                processingMode: 'batch',
                batchSize: 20
            }
        };

        const preset = presets[presetName];
        if (preset) {
            // Apply preset configuration
            $('input[name="outputFormat"]').prop('checked', false);
            preset.outputFormats.forEach(format => {
                $(`input[name="outputFormat"][value="${format}"]`).prop('checked', true);
            });

            $('input[name="exportFormat"]').prop('checked', false);
            preset.exportFormats.forEach(format => {
                $(`input[name="exportFormat"][value="${format}"]`).prop('checked', true);
            });

            $('#processingMode').val(preset.processingMode);
            $('#batchSize').val(preset.batchSize);

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
        $('input[name="outputFormat"]').prop('checked', false);
        $('input[name="exportFormat"]').prop('checked', false);
        $('#processingMode').val('single');
        $('#batchSize').val('10');
        showInfo('Configuration reset to defaults');
    }

    renderFileList() {
        const container = $('#etlFilesList');
        if (!container.length) {
            console.warn('ETL file list container not found');
            return;
        }

        if (this.files.length === 0) {
            container.html(`
                <div class="text-center py-4">
                    <i class="fas fa-file-upload fa-3x text-muted mb-3"></i>
                    <h6 class="text-muted">No AASX files available</h6>
                    <p class="text-muted small">Upload AASX files to projects to start ETL processing</p>
                </div>
            `);
            this.updateSelectedCount();
            return;
        }

        let html = '';
        this.files.forEach(file => {
            const isSelected = this.selectedFiles.has(file.filename);
            const statusColor = this.getFileStatusColor(file.status || 'not_processed');
            const statusText = this.getFileStatusText(file.status || 'not_processed');
            
            html += `
                <div class="file-item d-flex align-items-center p-2 border-bottom">
                    <div class="form-check me-3">
                        <input class="form-check-input" type="checkbox" 
                               id="file_${file.file_id}" 
                               ${isSelected ? 'checked' : ''}
                               onchange="window.aasxETLPipeline.toggleFileSelection('${file.filename}', this.checked)">
                    </div>
                    <div class="flex-grow-1">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h6 class="mb-1">${file.filename}</h6>
                                <small class="text-muted">${file.description || 'No description'}</small>
                                <br>
                                <small class="text-muted">
                                    <i class="fas fa-folder me-1"></i>${file.project_name || 'Unknown Project'}
                                    <span class="mx-2">•</span>
                                    <i class="fas fa-hdd me-1"></i>${formatFileSize(file.size || 0)}
                                </small>
                            </div>
                            <span class="badge ${statusColor}">${statusText}</span>
                        </div>
                    </div>
                </div>
            `;
        });

        container.html(html);
        this.updateSelectedCount();
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
            'processed': 'bg-success',
            'processing': 'bg-warning',
            'failed': 'bg-danger',
            'not_processed': 'bg-secondary'
        };
        return colors[status] || 'bg-secondary';
    }

    getFileStatusText(status) {
        const texts = {
            'processed': 'Processed',
            'processing': 'Processing',
            'failed': 'Failed',
            'not_processed': 'Pending'
        };
        return texts[status] || 'Unknown';
    }

    // Cleanup method
    destroy() {
        this.stopProgressSimulation();
        this.isInitialized = false;
        console.log('🧹 AASX ETL Pipeline destroyed');
    }
}

// Export the class
export default AASXETLPipeline; 