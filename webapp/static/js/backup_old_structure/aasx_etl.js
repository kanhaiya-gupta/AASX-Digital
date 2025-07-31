/**
 * AASX ETL Pipeline JavaScript
 * 
 * Handles the frontend functionality for the AASX ETL pipeline including:
 * - ETL pipeline execution
 * - Progress tracking
 * - Results display
 * - RAG search functionality
 * - Configuration management
 */

console.log('🚀 aasx_etl.js loaded successfully');

class AASXETLPipeline {
    constructor() {
        this.isProcessing = false;
        this.currentProgress = { overall: 0 };
        this.progressInterval = null;
        this.selectedFiles = new Set();
        this.presets = {
            quick: {
                name: "Quick Processing",
                description: "Fast processing with minimal validation",
                config: {
                    enableHybridProcessing: true,
                    enableValidation: false,
                    enableBackup: false,
                    enableParallelProcessing: true,
                    enableQualityChecks: false,
                    enableEnrichment: false,
                    enableNormalization: false,
                    formatJson: true,
                    formatCsv: true,
                    formatYaml: false,
                    formatGraph: false,
                    formatRag: false,
                    formatVectorDb: false,
                    formatSqlite: true,
                    enableSQLite: true,
                    enableVectorDB: false,
                    enableRAGExport: false,
                    vectorDBType: "qdrant",
                    embeddingModel: "all-MiniLM-L6-v2",
                    maxWorkers: 8,
                    memoryLimit: 0,
                    qualityThreshold: 0.5,
                    chunkSize: 256
                }
            },
            standard: {
                name: "Standard Processing",
                description: "Balanced processing with quality checks",
                config: {
                    enableHybridProcessing: true,
                    enableValidation: true,
                    enableBackup: true,
                    enableParallelProcessing: false,
                    enableQualityChecks: true,
                    enableEnrichment: true,
                    enableNormalization: true,
                    formatJson: true,
                    formatCsv: true,
                    formatYaml: true,
                    formatGraph: true,
                    formatRag: true,
                    formatVectorDb: true,
                    formatSqlite: true,
                    enableSQLite: true,
                    enableVectorDB: true,
                    enableRAGExport: true,
                    vectorDBType: "qdrant",
                    embeddingModel: "all-MiniLM-L6-v2",
                    maxWorkers: 4,
                    memoryLimit: 0,
                    qualityThreshold: 0.8,
                    chunkSize: 512
                }
            },
            comprehensive: {
                name: "Comprehensive Analysis",
                description: "Full analysis with all features enabled",
                config: {
                    enableHybridProcessing: true,
                    enableValidation: true,
                    enableBackup: true,
                    enableParallelProcessing: true,
                    enableQualityChecks: true,
                    enableEnrichment: true,
                    enableNormalization: true,
                    formatJson: true,
                    formatCsv: true,
                    formatYaml: true,
                    formatGraph: true,
                    formatRag: true,
                    formatVectorDb: true,
                    formatSqlite: true,
                    enableSQLite: true,
                    enableVectorDB: true,
                    enableRAGExport: true,
                    vectorDBType: "qdrant",
                    embeddingModel: "all-MiniLM-L6-v2",
                    maxWorkers: 2,
                    memoryLimit: 0,
                    qualityThreshold: 0.9,
                    chunkSize: 1024
                }
            }
        };
    }

    initializeEventListeners() {
        // ETL Pipeline Controls
        $('#runETLBtn').on('click', () => this.runETLPipeline());
        $('#stopETLBtn').on('click', () => this.stopETLPipeline());
        $('#resetETLBtn').on('click', () => this.resetETLPipeline());

        // File Selection
        $('#selectAllFiles').on('change', (e) => this.toggleSelectAll(e.target.checked));
        $('.file-checkbox').on('change', (e) => this.updateFileSelection(e.target));

        // Preset Management
        $('#loadPresetBtn').on('click', () => this.loadPreset($('#presetSelect').val()));
        $('#savePresetBtn').on('click', () => this.savePreset());
        $('#resetConfigBtn').on('click', () => this.resetConfig());

        // RAG Search
        $('#ragSearchForm').on('submit', (e) => {
            e.preventDefault();
            this.performRAGSearch();
        });

        // Export Controls
        $('#exportResultsBtn').on('click', () => this.exportResults());
        $('#viewStatsBtn').on('click', () => this.viewPipelineStats());

        // Explorer Integration
        $('#launchExplorerBtn').on('click', () => this.showLaunchExplorerModal());
        $('#downloadLauncherBtn').on('click', () => this.downloadLauncherScript());

        // Progress Circles
        this.initializeProgressCircles();
    }

    initializeProgressCircles() {
        try {
            // Initialize progress circles with 0 progress
            this.updateProgressCircle('extractProgress', 0);
            this.updateProgressCircle('transformProgress', 0);
            this.updateProgressCircle('loadProgress', 0);
            this.updateProgressCircle('overallProgress', 0);
        } catch (error) {
            console.warn('Progress circles initialization failed:', error.message);
        }
    }

    async runETLPipeline() {
        if (this.isProcessing) {
            this.showAlert('Pipeline is already running', 'warning');
            return;
        }

        const config = this.getETLConfiguration();
        const selectedFiles = this.getSelectedFiles();

        if (selectedFiles.length === 0) {
            this.showAlert('Please select at least one file to process', 'warning');
            return;
        }

        this.isProcessing = true;
        this.showETLProgress();
        this.startProgressSimulation();

        try {
            const response = await fetch('/aasx/api/etl/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    files: selectedFiles,
                    config: config
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.showETLResults(result);
            } else {
                const error = await response.json();
                this.showAlert(`ETL Pipeline failed: ${error.detail}`, 'danger');
            }
        } catch (error) {
            this.showAlert(`ETL Pipeline error: ${error.message}`, 'danger');
        } finally {
            this.isProcessing = false;
            this.stopProgressSimulation();
        }
    }

    startProgressSimulation() {
        this.progressInterval = setInterval(() => {
            this.currentProgress.overall += Math.random() * 5;
            if (this.currentProgress.overall > 100) this.currentProgress.overall = 100;
            this.updateETLProgress(
                this.currentProgress.overall * 0.3,
                this.currentProgress.overall * 0.4,
                this.currentProgress.overall * 0.3,
                this.currentProgress.overall
            );
        }, 500);
    }

    stopProgressSimulation() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
    }

    async processSingleFile(filename) {
        const config = this.getETLConfiguration();
        
        try {
            const response = await fetch('/aasx/api/etl/process-single', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    filename: filename,
                    config: config
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.showFileResults(filename, result);
            } else {
                const error = await response.json();
                this.showAlert(`Failed to process ${filename}: ${error.detail}`, 'danger');
            }
        } catch (error) {
            this.showAlert(`Error processing ${filename}: ${error.message}`, 'danger');
        }
    }

    async processAllFiles() {
        const files = this.getAllFiles();
        for (const file of files) {
            await this.processSingleFile(file);
        }
    }

    async performRAGSearch() {
        const query = $('#ragQuery').val().trim();
        if (!query) {
            this.showAlert('Please enter a search query', 'warning');
            return;
        }

        try {
            const response = await fetch('/aasx/api/rag/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            });

            if (response.ok) {
                const results = await response.json();
                this.displayRAGResults(results, query);
            } else {
                const error = await response.json();
                this.showAlert(`RAG search failed: ${error.detail}`, 'danger');
            }
        } catch (error) {
            this.showAlert(`RAG search error: ${error.message}`, 'danger');
        }
    }

    displayRAGResults(results, query) {
        const resultsHtml = results.map(result => `
            <div class="card mb-3">
                <div class="card-body">
                    <h6 class="card-title">${result.filename}</h6>
                    <p class="card-text">${result.content}</p>
                    <small class="text-muted">Score: ${result.score.toFixed(3)}</small>
                </div>
            </div>
        `).join('');

        $('#ragResults').html(`
            <h5>Search Results for: "${query}"</h5>
            <div class="mb-3">
                <span class="badge bg-info">${results.length} results found</span>
            </div>
            ${resultsHtml}
        `);
    }

    async exportRAGDataset() {
        try {
            const response = await fetch('/aasx/api/rag/export', {
                method: 'POST'
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'rag_dataset.json';
                a.click();
                window.URL.revokeObjectURL(url);
                this.showAlert('RAG dataset exported successfully', 'success');
            } else {
                const error = await response.json();
                this.showAlert(`Export failed: ${error.detail}`, 'danger');
            }
        } catch (error) {
            this.showAlert(`Export error: ${error.message}`, 'danger');
        }
    }

    async viewPipelineStats() {
        try {
            const response = await fetch('/aasx/api/etl/stats');
            if (response.ok) {
                const stats = await response.json();
                this.showPipelineStats(stats);
            } else {
                this.showAlert('Failed to load pipeline statistics', 'danger');
            }
        } catch (error) {
            this.showAlert(`Error loading stats: ${error.message}`, 'danger');
        }
    }

    showPipelineStats(stats) {
        const statsHtml = `
            <div class="row">
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h3 class="text-primary">${stats.totalFiles}</h3>
                            <p class="card-text">Total Files</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h3 class="text-success">${stats.processedFiles}</h3>
                            <p class="card-text">Processed</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h3 class="text-warning">${stats.pendingFiles}</h3>
                            <p class="card-text">Pending</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h3 class="text-danger">${stats.failedFiles}</h3>
                            <p class="card-text">Failed</p>
                        </div>
                    </div>
                </div>
            </div>
        `;

        $('#pipelineStatsModal .modal-body').html(statsHtml);
        $('#pipelineStatsModal').modal('show');
    }

    getETLConfiguration() {
        return {
            enableHybridProcessing: $('#enableHybridProcessing').is(':checked'),
            enableValidation: $('#enableValidation').is(':checked'),
            enableBackup: $('#enableBackup').is(':checked'),
            enableParallelProcessing: $('#enableParallelProcessing').is(':checked'),
            enableQualityChecks: $('#enableQualityChecks').is(':checked'),
            enableEnrichment: $('#enableEnrichment').is(':checked'),
            enableNormalization: $('#enableNormalization').is(':checked'),
            formatJson: $('#formatJson').is(':checked'),
            formatCsv: $('#formatCsv').is(':checked'),
            formatYaml: $('#formatYaml').is(':checked'),
            formatGraph: $('#formatGraph').is(':checked'),
            formatRag: $('#formatRag').is(':checked'),
            formatVectorDb: $('#formatVectorDb').is(':checked'),
            formatSqlite: $('#formatSqlite').is(':checked'),
            enableSQLite: $('#enableSQLite').is(':checked'),
            enableVectorDB: $('#enableVectorDB').is(':checked'),
            enableRAGExport: $('#enableRAGExport').is(':checked'),
            vectorDBType: $('#vectorDBType').val(),
            embeddingModel: $('#embeddingModel').val(),
            maxWorkers: parseInt($('#maxWorkers').val()),
            memoryLimit: parseInt($('#memoryLimit').val()),
            qualityThreshold: parseFloat($('#qualityThreshold').val()),
            chunkSize: parseInt($('#chunkSize').val())
        };
    }

    getSelectedOutputFormats() {
        const formats = [];
        if ($('#formatJson').is(':checked')) formats.push('json');
        if ($('#formatCsv').is(':checked')) formats.push('csv');
        if ($('#formatYaml').is(':checked')) formats.push('yaml');
        if ($('#formatGraph').is(':checked')) formats.push('graph');
        if ($('#formatRag').is(':checked')) formats.push('rag');
        if ($('#formatVectorDb').is(':checked')) formats.push('vector_db');
        if ($('#formatSqlite').is(':checked')) formats.push('sqlite');
        return formats;
    }

    getSelectedExportFormats() {
        const formats = [];
        if ($('#enableSQLite').is(':checked')) formats.push('sqlite');
        if ($('#enableVectorDB').is(':checked')) formats.push('vector_db');
        if ($('#enableRAGExport').is(':checked')) formats.push('rag');
        return formats;
    }

    getSelectedPipelineOutputFormats() {
        return this.getSelectedOutputFormats();
    }

    getSelectedPipelineExportFormats() {
        return this.getSelectedExportFormats();
    }

    showETLProgress() {
        $('#etlProgressSection').show();
        $('#etlResultsSection').hide();
    }

    updateETLProgress(extract, transform, load, overall) {
        this.updateProgressCircle('extractProgress', extract);
        this.updateProgressCircle('transformProgress', transform);
        this.updateProgressCircle('loadProgress', load);
        this.updateProgressCircle('overallProgress', overall);
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

    updateETLStatus(message, type = 'info') {
        const statusHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        $('#etlStatus').html(statusHtml);
    }

    updateFileStatus(filename, status) {
        const statusInfo = this.getFileStatusInfo(status);
        const statusHtml = `
            <span class="badge bg-${statusInfo.color}">
                <i class="fas fa-${statusInfo.icon}"></i>
                ${statusInfo.text}
            </span>
        `;
        $(`[data-filename="${filename}"] .file-status`).html(statusHtml);
    }

    updateFileStatuses(processedFiles) {
        processedFiles.forEach(file => {
            this.updateFileStatus(file.filename, file.status);
        });
    }

    showETLResults(result) {
        $('#etlProgressSection').hide();
        $('#etlResultsSection').show();
        
        const resultsHtml = `
            <div class="alert alert-success">
                <h5><i class="fas fa-check-circle"></i> ETL Pipeline Completed Successfully</h5>
                <p>Processed ${result.processedFiles} files in ${result.duration} seconds</p>
            </div>
            <div class="row">
                <div class="col-md-6">
                    <h6>Output Formats Generated:</h6>
                    <ul>
                        ${result.outputFormats.map(format => `<li>${format}</li>`).join('')}
                    </ul>
                </div>
                <div class="col-md-6">
                    <h6>Export Formats:</h6>
                    <ul>
                        ${result.exportFormats.map(format => `<li>${format}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
        
        $('#etlResults').html(resultsHtml);
    }

    showFileResults(filename, result) {
        const resultsHtml = `
            <div class="card">
                <div class="card-header">
                    <h6>Results for ${filename}</h6>
                </div>
                <div class="card-body">
                    <p><strong>Status:</strong> ${result.status}</p>
                    <p><strong>Processing Time:</strong> ${result.processingTime} seconds</p>
                    <p><strong>Output Size:</strong> ${result.outputSize}</p>
                    ${result.errors ? `<p><strong>Errors:</strong> ${result.errors}</p>` : ''}
                </div>
            </div>
        `;
        
        $('#fileResults').html(resultsHtml);
    }

    async openFile(filename) {
        try {
            const response = await fetch(`/aasx/api/files/${filename}/open`);
            if (response.ok) {
                const result = await response.json();
                this.showAlert(`File opened: ${result.message}`, 'success');
            } else {
                this.showAlert('Failed to open file', 'danger');
            }
        } catch (error) {
            this.showAlert(`Error opening file: ${error.message}`, 'danger');
        }
    }

    async viewFileResults(filename) {
        try {
            const response = await fetch(`/aasx/api/files/${filename}/results`);
            if (response.ok) {
                const results = await response.json();
                this.showFileResults(filename, results);
            } else {
                this.showAlert('No results available for this file', 'warning');
            }
        } catch (error) {
            this.showAlert(`Error loading results: ${error.message}`, 'danger');
        }
    }

    async refreshFiles() {
        try {
            const response = await fetch('/aasx/api/files');
            if (response.ok) {
                const files = await response.json();
                this.renderFileList(files);
            } else {
                this.showAlert('Failed to refresh files', 'danger');
            }
        } catch (error) {
            this.showAlert(`Error refreshing files: ${error.message}`, 'danger');
        }
    }

    async exportResults() {
        try {
            const response = await fetch('/aasx/api/etl/export', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    formats: this.getSelectedExportFormats()
                })
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'aasx_etl_results.zip';
                a.click();
                window.URL.revokeObjectURL(url);
                this.showAlert('Results exported successfully', 'success');
            } else {
                const error = await response.json();
                this.showAlert(`Export failed: ${error.detail}`, 'danger');
            }
        } catch (error) {
            this.showAlert(`Export error: ${error.message}`, 'danger');
        }
    }

    showAlert(message, type = 'info', timeout = 5000) {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const alertElement = $(alertHtml);
        $('#alertsContainer').append(alertElement);
        
        if (timeout > 0) {
            setTimeout(() => {
                alertElement.alert('close');
            }, timeout);
        }
    }

    selectAllFiles() {
        $('.file-checkbox').prop('checked', true).trigger('change');
    }

    deselectAllFiles() {
        $('.file-checkbox').prop('checked', false).trigger('change');
    }

    invertSelection() {
        $('.file-checkbox').each(function() {
            $(this).prop('checked', !$(this).is(':checked')).trigger('change');
        });
    }

    toggleSelectAll(checked) {
        $('.file-checkbox').prop('checked', checked).trigger('change');
    }

    updateFileSelection(checkbox) {
        const filename = checkbox.value;
        if (checkbox.checked) {
            this.selectedFiles.add(filename);
        } else {
            this.selectedFiles.delete(filename);
        }
        this.updateSelectedCount();
    }

    updateSelectedCount() {
        const count = this.selectedFiles.size;
        $('#selectedCount').text(count);
        $('#runETLBtn').prop('disabled', count === 0);
    }

    loadPreset(presetName) {
        if (!this.presets[presetName]) {
            this.showAlert('Invalid preset name', 'warning');
            return;
        }

        const preset = this.presets[presetName];
        const config = preset.config;

        // Update form fields
        Object.keys(config).forEach(key => {
            const element = $(`#${key}`);
            if (element.length > 0) {
                if (element.attr('type') === 'checkbox') {
                    element.prop('checked', config[key]);
                } else {
                    element.val(config[key]);
                }
            }
        });

        this.showAlert(`Loaded preset: ${preset.name}`, 'success');
    }

    savePreset() {
        const name = prompt('Enter preset name:');
        if (!name) return;

        const config = this.getETLConfiguration();
        this.presets[name] = {
            name: name,
            description: 'Custom preset',
            config: config
        };

        this.showAlert(`Preset "${name}" saved successfully`, 'success');
    }

    resetConfig() {
        this.loadPreset('standard');
        this.showAlert('Configuration reset to standard preset', 'info');
    }

    updateProcessingMode(mode) {
        $('#processingMode').text(mode);
        this.showAlert(`Processing mode changed to: ${mode}`, 'info');
    }

    handleFileAction(action, filename) {
        switch (action) {
            case 'process':
                this.processSingleFile(filename);
                break;
            case 'view':
                this.viewFileResults(filename);
                break;
            case 'open':
                this.openFile(filename);
                break;
            default:
                this.showAlert(`Unknown action: ${action}`, 'warning');
        }
    }

    validateSingleFile(filename) {
        this.showAlert(`Validating ${filename}...`, 'info');
        // Implementation would go here
    }

    processSelectedFiles() {
        const selectedFiles = Array.from(this.selectedFiles);
        selectedFiles.forEach(file => this.processSingleFile(file));
    }

    processBatchFiles() {
        this.runETLPipeline();
    }

    validateFiles() {
        this.showAlert('Validating all files...', 'info');
        // Implementation would go here
    }

    previewFile(filename) {
        this.showAlert(`Previewing ${filename}...`, 'info');
        // Implementation would go here
    }

    downloadFile(filename) {
        this.showAlert(`Downloading ${filename}...`, 'info');
        // Implementation would go here
    }

    showFileInfo(filename) {
        this.showAlert(`Showing info for ${filename}...`, 'info');
        // Implementation would go here
    }

    showLaunchExplorerModal() {
        $('#launchExplorerModal').modal('show');
    }

    selectAllExportFormats() {
        $('#enableSQLite, #enableVectorDB, #enableRAGExport').prop('checked', true);
    }

    deselectAllExportFormats() {
        $('#enableSQLite, #enableVectorDB, #enableRAGExport').prop('checked', false);
    }

    updatePipelineFileSelection() {
        const selectedFiles = Array.from(this.selectedFiles);
        $('#pipelineFileSelection').text(selectedFiles.join(', ') || 'No files selected');
    }

    clearPipelineFileSelection() {
        this.selectedFiles.clear();
        $('.file-checkbox').prop('checked', false);
        this.updateSelectedCount();
        this.updatePipelineFileSelection();
    }

    updatePipelineModeUI(mode) {
        $('#pipelineMode').text(mode);
        this.showAlert(`Processing mode changed to: ${mode}`, 'info');
    }

    updatePipelineFileSelection() {
        const selectedFiles = Array.from(this.selectedFiles);
        $('#pipelineFileSelection').text(selectedFiles.join(', ') || 'No files selected');
    }

    updatePipelineProjectSelects() {
        // This would be handled by project_manager.js
        if (window.projectManager) {
            window.projectManager.updateProjectSelects();
        }
    }

    async refreshPipelineStatus() {
        try {
            const response = await fetch('/aasx/api/etl/status');
            if (response.ok) {
                const stats = await response.json();
                this.updatePipelineStatusDisplay(stats);
            }
        } catch (error) {
            console.error('Error refreshing pipeline status:', error);
        }
    }

    updatePipelineStatusDisplay(stats) {
        $('#pipelineStatus').html(`
            <div class="row">
                <div class="col-md-3">
                    <div class="text-center">
                        <h4 class="text-primary">${stats.totalFiles}</h4>
                        <small>Total Files</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h4 class="text-success">${stats.processedFiles}</h4>
                        <small>Processed</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h4 class="text-warning">${stats.pendingFiles}</h4>
                        <small>Pending</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h4 class="text-danger">${stats.failedFiles}</h4>
                        <small>Failed</small>
                    </div>
                </div>
            </div>
        `);
    }

    async runSelectedPipeline() {
        if (this.selectedFiles.size === 0) {
            this.showAlert('Please select files to process', 'warning');
            return;
        }

        const config = this.getETLConfiguration();
        const selectedFiles = Array.from(this.selectedFiles);

        this.isProcessing = true;
        this.showETLProgress();
        this.startProgressSimulation();

        try {
            const response = await fetch('/aasx/api/etl/run-selected', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    files: selectedFiles,
                    config: config
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.showETLResults(result);
            } else {
                const error = await response.json();
                this.showAlert(`Pipeline failed: ${error.detail}`, 'danger');
            }
        } catch (error) {
            this.showAlert(`Pipeline error: ${error.message}`, 'danger');
        } finally {
            this.isProcessing = false;
            this.stopProgressSimulation();
        }
    }

    async runAllDataPipeline() {
        this.isProcessing = true;
        this.showETLProgress();
        this.startProgressSimulation();

        try {
            const response = await fetch('/aasx/api/etl/run-all', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    config: this.getETLConfiguration()
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.showETLResults(result);
            } else {
                const error = await response.json();
                this.showAlert(`All-data pipeline failed: ${error.detail}`, 'danger');
            }
        } catch (error) {
            this.showAlert(`All-data pipeline error: ${error.message}`, 'danger');
        } finally {
            this.isProcessing = false;
            this.stopProgressSimulation();
        }
    }

    startPipelineStatusPolling() {
        this.statusPollingInterval = setInterval(() => {
            this.refreshPipelineStatus();
        }, 5000); // Poll every 5 seconds
    }

    stopPipelineStatusPolling() {
        if (this.statusPollingInterval) {
            clearInterval(this.statusPollingInterval);
            this.statusPollingInterval = null;
        }
    }

    getFileStatusInfo(status) {
        const statusInfo = {
            'pending': { color: 'warning', icon: 'clock', text: 'Pending' },
            'processing': { color: 'info', icon: 'cog', text: 'Processing' },
            'completed': { color: 'success', icon: 'check', text: 'Completed' },
            'failed': { color: 'danger', icon: 'times', text: 'Failed' },
            'skipped': { color: 'secondary', icon: 'minus', text: 'Skipped' }
        };
        return statusInfo[status] || { color: 'secondary', icon: 'question', text: 'Unknown' };
    }

    getSelectedFiles() {
        return Array.from(this.selectedFiles);
    }

    getAllFiles() {
        return $('.file-checkbox').map(function() {
            return this.value;
        }).get();
    }

    renderFileList(files) {
        const filesHtml = files.map(file => `
            <div class="file-item" data-filename="${file.filename}">
                <div class="form-check">
                    <input class="form-check-input file-checkbox" type="checkbox" value="${file.filename}">
                    <label class="form-check-label">
                        ${file.filename}
                    </label>
                </div>
                <div class="file-status">
                    <span class="badge bg-secondary">Unknown</span>
                </div>
                <div class="file-actions">
                    <button class="btn btn-sm btn-outline-primary" onclick="etlPipeline.processSingleFile('${file.filename}')">
                        <i class="fas fa-cog"></i> Process
                    </button>
                </div>
            </div>
        `).join('');

        $('#fileList').html(filesHtml);
    }
}

// Initialize ETL Pipeline when DOM is ready
$(document).ready(() => {
    window.etlPipeline = new AASXETLPipeline();
    etlPipeline.initializeEventListeners();
});

// Global utility functions
async function launchExplorer(method) {
    try {
        const response = await fetch('/aasx/api/explorer/launch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ method: method })
        });

        if (response.ok) {
            const result = await response.json();
            showAlert(`Explorer launched: ${result.message}`, 'success');
        } else {
            const error = await response.json();
            showAlert(`Failed to launch explorer: ${error.detail}`, 'danger');
        }
    } catch (error) {
        showAlert(`Error launching explorer: ${error.message}`, 'danger');
    }
}

async function launchExplorerDirect() {
    try {
        window.open('/explorer', '_blank');
        showAlert('Explorer opened in new tab', 'success');
    } catch (error) {
        showAlert(`Error opening explorer: ${error.message}`, 'danger');
    }
}

async function downloadLauncherScript() {
    try {
        const response = await fetch('/aasx/api/explorer/download-launcher');
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'aasx_explorer_launcher.bat';
            a.click();
            window.URL.revokeObjectURL(url);
            showAlert('Launcher script downloaded successfully', 'success');
        } else {
            showAlert('Failed to download launcher script', 'danger');
        }
    } catch (error) {
        showAlert(`Error downloading launcher: ${error.message}`, 'danger');
    }
}

function showManualInstructions() {
    const instructions = `
        <h5>Manual Explorer Launch Instructions</h5>
        <ol>
            <li>Navigate to the AASX Package Explorer directory</li>
            <li>Run the executable: <code>AasxPackageExplorer.exe</code></li>
            <li>Use File > Open to load AASX files</li>
            <li>Explore the digital twin structure</li>
        </ol>
    `;
    
    $('#manualInstructionsModal .modal-body').html(instructions);
    $('#manualInstructionsModal').modal('show');
}

function showAlert(message, type = 'info', timeout = 5000) {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const alertElement = $(alertHtml);
    $('#alertsContainer').append(alertElement);
    
    if (timeout > 0) {
        setTimeout(() => {
            alertElement.alert('close');
        }, timeout);
    }
}