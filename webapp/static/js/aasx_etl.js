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
        this.currentProgress = { extract: 0, transform: 0, load: 0, overall: 0 };
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
                    embeddingModel: "all-mpnet-base-v2",
                    maxWorkers: 6,
                    memoryLimit: 0,
                    qualityThreshold: 0.9,
                    chunkSize: 512
                }
            }
        };
        
        this.initializeEventListeners();
        this.initializeProgressCircles();
        // Only update selected count if the element exists (for backward compatibility)
        if (document.getElementById('selectedCount')) {
            this.updateSelectedCount();
        }
    }

    initializeEventListeners() {
        // Main ETL Pipeline button
        document.getElementById('runETLPipeline')?.addEventListener('click', () => {
            this.runETLPipeline();
        });

        // File processing buttons
        document.querySelectorAll('.process-file').forEach(button => {
            button.addEventListener('click', (e) => {
                const filename = e.target.closest('.process-file').dataset.filename;
                this.processSingleFile(filename);
            });
        });

        // File selection
        document.getElementById('selectAll')?.addEventListener('click', () => this.selectAllFiles());
        document.getElementById('deselectAll')?.addEventListener('click', () => this.deselectAllFiles());
        document.getElementById('invertSelection')?.addEventListener('click', () => this.invertSelection());
        document.getElementById('selectAllCheckbox')?.addEventListener('change', (e) => {
            this.toggleSelectAll(e.target.checked);
        });

        // File checkboxes
        document.querySelectorAll('.file-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                this.updateFileSelection(e.target);
            });
        });

        // Processing mode
        document.querySelectorAll('input[name="processingMode"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.updateProcessingMode(e.target.value);
            });
        });

        // Preset loading
        document.querySelectorAll('[data-preset]').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const preset = e.target.dataset.preset;
                this.loadPreset(preset);
            });
        });

        // Configuration controls
        document.getElementById('savePreset')?.addEventListener('click', () => this.savePreset());
        document.getElementById('resetConfig')?.addEventListener('click', () => this.resetConfig());

        // Range sliders
        document.getElementById('maxWorkers')?.addEventListener('input', (e) => {
            document.getElementById('maxWorkersValue').textContent = e.target.value;
        });

        document.getElementById('qualityThreshold')?.addEventListener('input', (e) => {
            document.getElementById('qualityThresholdValue').textContent = e.target.value;
        });

        // Pipeline-specific range sliders
        document.getElementById('pipelineMaxWorkers')?.addEventListener('input', (e) => {
            document.getElementById('pipelineMaxWorkersValue').textContent = e.target.value;
        });

        document.getElementById('pipelineQualityThreshold')?.addEventListener('input', (e) => {
            document.getElementById('pipelineQualityThresholdValue').textContent = e.target.value;
        });

        // ETL Actions
        document.getElementById('processAllFiles')?.addEventListener('click', () => this.runETLPipeline());
        document.getElementById('processSelectedFiles')?.addEventListener('click', () => this.processSelectedFiles());
        document.getElementById('processBatch')?.addEventListener('click', () => this.processBatchFiles());
        document.getElementById('exportRAGDataset')?.addEventListener('click', () => this.exportRAGDataset());
        document.getElementById('exportResults')?.addEventListener('click', () => this.exportResults());
        document.getElementById('viewPipelineStats')?.addEventListener('click', () => this.viewPipelineStats());
        document.getElementById('validateFiles')?.addEventListener('click', () => this.validateFiles());

        // File action dropdowns
        document.querySelectorAll('[data-action]').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const action = e.target.dataset.action;
                const filename = e.target.dataset.filename;
                this.handleFileAction(action, filename);
            });
        });

        // RAG Search
        document.getElementById('searchRAG')?.addEventListener('click', () => {
            this.performRAGSearch();
        });

        // Refresh files
        document.getElementById('refreshFiles')?.addEventListener('click', () => {
            this.refreshFiles();
        });

        // Launch Explorer button - handled by ProjectManager
        // document.getElementById('launchExplorer')?.addEventListener('click', () => {
        //     this.showLaunchExplorerModal();
        // });

        // Export format controls
        document.getElementById('selectAllFormats')?.addEventListener('click', () => {
            this.selectAllExportFormats();
        });

        document.getElementById('deselectAllFormats')?.addEventListener('click', () => {
            this.deselectAllExportFormats();
        });
    }

    initializeProgressCircles() {
        // Initialize progress circles with CSS
        const style = document.createElement('style');
        style.textContent = `
            .progress-circle {
                width: 80px;
                height: 80px;
                border-radius: 50%;
                background: conic-gradient(#007bff 0deg, #e9ecef 0deg);
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto;
                position: relative;
            }
            .progress-circle::before {
                content: '';
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: white;
                position: absolute;
            }
            .progress-text {
                position: relative;
                z-index: 1;
                font-weight: bold;
                color: #007bff;
            }
        `;
        document.head.appendChild(style);
    }

    async runETLPipeline() {
        try {
            this.showETLProgress();
            this.updateETLStatus('Starting ETL pipeline...', 'info');
            
            const config = this.getETLConfiguration();
            const outputFormats = this.getSelectedOutputFormats();
            
            // Start progress simulation
            this.startProgressSimulation();
            
            const response = await fetch('/aasx/api/etl/run', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    config: config,
                    output_formats: outputFormats
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            // Stop progress simulation
            this.stopProgressSimulation();
            
            if (result.success) {
                // Update progress with final values from backend
                if (result.progress) {
                    this.updateETLProgress(
                        result.progress.extract,
                        result.progress.transform,
                        result.progress.load,
                        result.progress.overall
                    );
                }
                
                // Stop any remaining animations
                const progressBar = document.getElementById('overallProgressBar');
                if (progressBar) {
                    progressBar.classList.remove('progress-bar-animated');
                }
                
                this.updateETLStatus('ETL pipeline completed successfully!', 'success');
                this.showETLResults(result);
            } else {
                throw new Error(result.error || 'ETL pipeline failed');
            }
        } catch (error) {
            console.error('ETL Pipeline Error:', error);
            this.stopProgressSimulation();
            this.updateETLStatus(`ETL pipeline failed: ${error.message}`, 'danger');
        }
    }

    startProgressSimulation() {
        this.progressInterval = setInterval(() => {
            // Simulate realistic progress (using integers)
            const currentExtract = Math.min(90, this.currentProgress.extract + Math.round(Math.random() * 5));
            const currentTransform = Math.min(90, this.currentProgress.transform + Math.round(Math.random() * 3));
            const currentLoad = Math.min(90, this.currentProgress.load + Math.round(Math.random() * 4));
            const currentOverall = Math.min(90, Math.round((currentExtract + currentTransform + currentLoad) / 3));
            
            this.updateETLProgress(currentExtract, currentTransform, currentLoad, currentOverall);
        }, 500);
    }

    stopProgressSimulation() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
        
        // Ensure progress bar stops animating
        const progressBar = document.getElementById('overallProgressBar');
        if (progressBar) {
            progressBar.classList.remove('progress-bar-animated');
        }
    }

    async processSingleFile(filename) {
        if (this.isProcessing) {
            this.showAlert('ETL pipeline is already running', 'warning');
            return;
        }

        this.isProcessing = true;
        this.updateFileStatus(filename, 'processing');
        this.showETLProgress();
        this.startProgressSimulation();

        try {
            this.updateFileStatus(filename, 'processing');
            this.updateETLStatus(`Processing ${filename}...`, 'info');
            
            const response = await fetch('/aasx/api/etl/process-file', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    filename: filename,
                    config: this.getETLConfiguration()
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            this.stopProgressSimulation();
            
            if (result.success) {
                // Update progress with final values
                if (result.progress) {
                    this.updateETLProgress(
                        result.progress.extract,
                        result.progress.transform,
                        result.progress.load,
                        result.progress.overall
                    );
                }
                
                // Stop any remaining animations
                const progressBar = document.getElementById('overallProgressBar');
                if (progressBar) {
                    progressBar.classList.remove('progress-bar-animated');
                }
                
                this.updateFileStatus(filename, 'completed');
                this.updateETLStatus(`${filename} processed successfully!`, 'success');
                this.showFileResults(filename, result);
            } else {
                this.updateFileStatus(filename, 'failed');
                throw new Error(result.error || 'File processing failed');
            }
        } catch (error) {
            console.error('Process File Error:', error);
            this.stopProgressSimulation();
            this.updateFileStatus(filename, 'failed');
            this.updateETLStatus(`Failed to process ${filename}: ${error.message}`, 'danger');
        } finally {
            this.isProcessing = false;
        }
    }

    async processAllFiles() {
        try {
            this.updateETLStatus('Processing all files...', 'info');
            
            const response = await fetch('/aasx/api/etl/process-batch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    config: this.getETLConfiguration()
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                this.updateETLStatus('All files processed successfully!', 'success');
                this.updateFileStatuses(result.processed_files);
                this.showETLResults(result);
            } else {
                throw new Error(result.error || 'Batch processing failed');
            }
        } catch (error) {
            console.error('Process All Files Error:', error);
            this.updateETLStatus(`Batch processing failed: ${error.message}`, 'danger');
        }
    }

    async performRAGSearch() {
        const query = document.getElementById('ragQuery').value.trim();
        if (!query) {
            this.showAlert('Please enter a search query', 'warning');
            return;
        }

        try {
            this.updateETLStatus('Performing RAG search...', 'info');
            
            const response = await fetch('/aasx/api/rag/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    top_k: 5
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                this.updateETLStatus('RAG search completed!', 'success');
                this.displayRAGResults(result.results, query);
            } else {
                throw new Error(result.error || 'RAG search failed');
            }
        } catch (error) {
            console.error('RAG Search Error:', error);
            this.updateETLStatus(`RAG search failed: ${error.message}`, 'danger');
        }
    }

    displayRAGResults(results, query) {
        const resultsContainer = document.getElementById('searchResults');
        
        if (results.length === 0) {
            resultsContainer.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle"></i>
                    No results found for "${query}"
                </div>
            `;
            return;
        }

        let html = `
            <h6>Search Results for "${query}" (${results.length} results)</h6>
            <div class="list-group">
        `;

        results.forEach((result, index) => {
            const similarity = (1 - result.similarity) * 100; // Convert distance to similarity
            const badgeClass = similarity > 80 ? 'bg-success' : similarity > 60 ? 'bg-warning' : 'bg-secondary';
            
            html += `
                <div class="list-group-item">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <h6 class="mb-1">
                                <span class="badge ${badgeClass} me-2">${result.metadata.entity_type}</span>
                                ${result.metadata.entity_id || 'Unknown ID'}
                            </h6>
                            <p class="mb-1">${result.document}</p>
                            <small class="text-muted">
                                Quality: ${result.metadata.quality_level || 'N/A'} | 
                                Compliance: ${result.metadata.compliance_status || 'N/A'}
                            </small>
                        </div>
                        <div class="text-end">
                            <span class="badge bg-primary">${similarity.toFixed(1)}%</span>
                        </div>
                    </div>
                </div>
            `;
        });

        html += '</div>';
        resultsContainer.innerHTML = html;
    }

    async exportRAGDataset() {
        try {
            this.updateETLStatus('Exporting RAG dataset...', 'info');
            
            const response = await fetch('/aasx/api/rag/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                // Trigger download
                const link = document.createElement('a');
                link.href = result.download_url;
                link.download = 'rag_dataset.json';
                link.click();
                this.updateETLStatus('RAG dataset exported successfully!', 'success');
            } else {
                throw new Error(result.error || 'Export failed');
            }
        } catch (error) {
            console.error('Export RAG Dataset Error:', error);
            this.updateETLStatus(`Export failed: ${error.message}`, 'danger');
        }
    }

    async viewPipelineStats() {
        try {
            this.updateETLStatus('Loading pipeline statistics...', 'info');
            
            const response = await fetch('/aasx/api/etl/stats');

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                this.updateETLStatus('Statistics loaded successfully!', 'success');
                this.showPipelineStats(result.stats);
            } else {
                throw new Error(result.error || 'Failed to load statistics');
            }
        } catch (error) {
            console.error('View Stats Error:', error);
            this.updateETLStatus(`Failed to load statistics: ${error.message}`, 'danger');
        }
    }

    showPipelineStats(stats) {
        const modal = new bootstrap.Modal(document.getElementById('etlResultsModal'));
        const content = document.getElementById('etlResultsContent');
        
        content.innerHTML = `
            <h6>Pipeline Statistics</h6>
            <div class="row">
                <div class="col-md-6">
                    <table class="table table-sm">
                        <tbody>
                            <tr><td>Files Processed:</td><td>${stats.files_processed || 0}</td></tr>
                            <tr><td>Files Failed:</td><td>${stats.files_failed || 0}</td></tr>
                            <tr><td>Total Processing Time:</td><td>${(stats.total_processing_time || 0).toFixed(2)}s</td></tr>
                            <tr><td>Extract Time:</td><td>${(stats.extract_time || 0).toFixed(2)}s</td></tr>
                            <tr><td>Transform Time:</td><td>${(stats.transform_time || 0).toFixed(2)}s</td></tr>
                            <tr><td>Load Time:</td><td>${(stats.load_time || 0).toFixed(2)}s</td></tr>
                        </tbody>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6>Component Statistics</h6>
                    <div class="mb-3">
                        <strong>Processor:</strong>
                        <ul class="list-unstyled ms-3">
                            <li>Files processed: ${stats.component_stats?.processor?.files_processed || 0}</li>
                            <li>Success rate: ${((stats.component_stats?.processor?.success_rate || 0) * 100).toFixed(1)}%</li>
                        </ul>
                    </div>
                    <div class="mb-3">
                        <strong>Transformer:</strong>
                        <ul class="list-unstyled ms-3">
                            <li>Transformations applied: ${stats.component_stats?.transformer?.transformations_applied || 0}</li>
                            <li>Output formats: ${stats.component_stats?.transformer?.output_formats || 0}</li>
                        </ul>
                    </div>
                    <div class="mb-3">
                        <strong>Loader:</strong>
                        <ul class="list-unstyled ms-3">
                            <li>Database records: ${stats.component_stats?.loader?.database_records || 0}</li>
                            <li>Vector embeddings: ${stats.component_stats?.loader?.vector_embeddings || 0}</li>
                        </ul>
                    </div>
                </div>
            </div>
        `;
        
        modal.show();
    }

    getETLConfiguration() {
        // Check if we're using pipeline-specific configuration
        const usePipelineConfig = document.getElementById('pipelineHybridProcessing') !== null;
        
        if (usePipelineConfig) {
            return {
                extract: {
                    enable_hybrid_processing: document.getElementById('pipelineHybridProcessing')?.checked || false,
                    enable_validation: document.getElementById('pipelineEnableValidation')?.checked || false,
                    enable_backup: document.getElementById('pipelineEnableBackup')?.checked || false,
                    parallel_processing: document.getElementById('pipelineParallelProcessing')?.checked || false
                },
                transform: {
                    enable_quality_checks: document.getElementById('pipelineEnableQualityChecks')?.checked || false,
                    enable_enrichment: document.getElementById('pipelineEnableEnrichment')?.checked || false,
                    normalize_ids: document.getElementById('pipelineNormalizeIds')?.checked || false,
                    output_formats: this.getSelectedPipelineOutputFormats(),
                    include_metadata: true
                },
                load: {
                    enable_sqlite: document.getElementById('pipelineEnableSQLite')?.checked || false,
                    enable_vector_db: document.getElementById('pipelineEnableVectorDB')?.checked || false,
                    enable_rag_export: document.getElementById('pipelineEnableRAGExport')?.checked || false,
                    vector_db_type: document.getElementById('pipelineVectorDBType')?.value || 'qdrant',
                    embedding_model: document.getElementById('pipelineEmbeddingModel')?.value || 'all-MiniLM-L6-v2',
                    qdrant_url: 'http://localhost:6333',
                    qdrant_collection_prefix: 'aasx',
                    output_directory: 'output/etl_results',
                    database_path: 'aasx_data.db',
                    vector_db_path: 'vector_db',
                    export_formats: this.getSelectedPipelineExportFormats()
                },
                advanced: {
                    max_workers: parseInt(document.getElementById('pipelineMaxWorkers')?.value || '4'),
                    memory_limit: parseInt(document.getElementById('pipelineMemoryLimit')?.value || '0'),
                    quality_threshold: parseFloat(document.getElementById('pipelineQualityThreshold')?.value || '0.8'),
                    chunk_size: parseInt(document.getElementById('pipelineChunkSize')?.value || '512')
                }
            };
        } else {
            // Fallback to original configuration for backward compatibility
            return {
                extract: {
                    enable_hybrid_processing: document.getElementById('enableHybridProcessing')?.checked || false,
                    enable_validation: document.getElementById('enableValidation')?.checked || false
                },
                transform: {
                    enable_quality_checks: document.getElementById('enableQualityChecks')?.checked || false,
                    enable_enrichment: document.getElementById('enableEnrichment')?.checked || false,
                    output_formats: this.getSelectedOutputFormats(),
                    include_metadata: true
                },
                load: {
                    enable_vector_db: document.getElementById('enableVectorDB')?.checked || false,
                    enable_rag_export: document.getElementById('enableRAGExport')?.checked || false,
                    vector_db_type: document.getElementById('vectorDBType')?.value || 'qdrant',
                    qdrant_url: 'http://localhost:6333',
                    qdrant_collection_prefix: 'aasx',
                    output_directory: 'output/etl_results',
                    database_path: 'aasx_data.db',
                    vector_db_path: 'vector_db',
                    export_formats: this.getSelectedExportFormats()
                },
                parallel_processing: false,
                max_workers: 4
            };
        }
    }

    getSelectedOutputFormats() {
        const formats = [];
        if (document.getElementById('formatJson')?.checked) formats.push('json');
        if (document.getElementById('formatCsv')?.checked) formats.push('csv');
        if (document.getElementById('formatGraph')?.checked) formats.push('graph');
        return formats.length > 0 ? formats : ['json'];
    }

    getSelectedExportFormats() {
        const formats = [];
        if (document.getElementById('formatJson')?.checked) formats.push('json');
        if (document.getElementById('formatYaml')?.checked) formats.push('yaml');
        if (document.getElementById('formatCsv')?.checked) formats.push('csv');
        if (document.getElementById('formatGraph')?.checked) formats.push('graph');
        if (document.getElementById('formatRag')?.checked) formats.push('rag');
        if (document.getElementById('formatVectorDb')?.checked) formats.push('vector_db');
        if (document.getElementById('formatSqlite')?.checked) formats.push('sqlite');
        return formats.length > 0 ? formats : ['json', 'vector_db', 'sqlite'];
    }

    getSelectedPipelineOutputFormats() {
        const formats = [];
        if (document.getElementById('pipelineFormatJson')?.checked) formats.push('json');
        if (document.getElementById('pipelineFormatCsv')?.checked) formats.push('csv');
        if (document.getElementById('pipelineFormatGraph')?.checked) formats.push('graph');
        return formats.length > 0 ? formats : ['json'];
    }

    getSelectedPipelineExportFormats() {
        const formats = [];
        if (document.getElementById('pipelineFormatJson')?.checked) formats.push('json');
        if (document.getElementById('pipelineFormatYaml')?.checked) formats.push('yaml');
        if (document.getElementById('pipelineFormatCsv')?.checked) formats.push('csv');
        if (document.getElementById('pipelineFormatGraph')?.checked) formats.push('graph');
        if (document.getElementById('pipelineFormatRag')?.checked) formats.push('rag');
        if (document.getElementById('pipelineFormatVectorDb')?.checked) formats.push('vector_db');
        if (document.getElementById('pipelineFormatSqlite')?.checked) formats.push('sqlite');
        return formats.length > 0 ? formats : ['json', 'vector_db', 'sqlite'];
    }

    showETLProgress() {
        document.getElementById('etlProgress').style.display = 'block';
        this.updateETLProgress(0, 0, 0, 0);
    }

    updateETLProgress(extract, transform, load, overall) {
        // Ensure all values are integers
        this.currentProgress = { 
            extract: Math.round(extract), 
            transform: Math.round(transform), 
            load: Math.round(load), 
            overall: Math.round(overall) 
        };
        
        // Update progress circles
        this.updateProgressCircle('extractProgress', this.currentProgress.extract);
        this.updateProgressCircle('transformProgress', this.currentProgress.transform);
        this.updateProgressCircle('loadProgress', this.currentProgress.load);
        this.updateProgressCircle('overallProgress', this.currentProgress.overall);
        
        // Update progress bar
        const progressBar = document.getElementById('overallProgressBar');
        if (progressBar) {
            progressBar.style.width = `${this.currentProgress.overall}%`;
            progressBar.setAttribute('aria-valuenow', this.currentProgress.overall);
            
            // Remove animation when complete
            if (this.currentProgress.overall >= 100) {
                progressBar.classList.remove('progress-bar-animated');
            }
        }
    }

    updateProgressCircle(elementId, progress) {
        const element = document.getElementById(elementId);
        if (element) {
            const degrees = (progress / 100) * 360;
            element.style.background = `conic-gradient(#007bff ${degrees}deg, #e9ecef ${degrees}deg)`;
            element.querySelector('.progress-text').textContent = `${Math.round(progress)}%`;
        }
    }

    updateETLStatus(message, type = 'info') {
        const statusElement = document.getElementById('etlStatusText');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = `text-${type === 'error' ? 'danger' : type}`;
            console.log(`📝 Status updated: ${message} (${type})`);
        } else {
            console.error('❌ Status element not found: etlStatusText');
        }
    }

    updateFileStatus(filename, status) {
        const statusElement = document.getElementById(`status-${filename}`);
        if (statusElement) {
            const statusClasses = {
                'pending': 'bg-secondary',
                'processing': 'bg-warning',
                'completed': 'bg-success',
                'failed': 'bg-danger'
            };
            
            statusElement.className = `badge ${statusClasses[status] || 'bg-secondary'}`;
            statusElement.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        }
    }

    updateFileStatuses(processedFiles) {
        if (processedFiles) {
            Object.entries(processedFiles).forEach(([filename, status]) => {
                this.updateFileStatus(filename, status);
            });
        }
    }

    showETLResults(result) {
        const etlResultsElement = document.getElementById('etlResults');
        if (etlResultsElement) {
            etlResultsElement.style.display = 'block';
        }
        
        // Update statistics with null checks
        const statsElements = {
            'statsFilesProcessed': result.files_processed || 0,
            'statsFilesFailed': result.files_failed || 0,
            'statsTotalTime': `${(result.total_time || 0).toFixed(2)}s`,
            'statsDBRecords': result.database_records || 0,
            'statsVectorEmbeddings': result.vector_embeddings || 0
        };
        
        Object.entries(statsElements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
        
        // Update output files
        const outputFilesList = document.getElementById('outputFilesList');
        if (outputFilesList) {
            if (result.files_exported && result.files_exported.length > 0) {
                let html = '<ul class="list-unstyled">';
                result.files_exported.forEach(file => {
                    html += `<li><i class="fas fa-file text-primary me-2"></i>${file}</li>`;
                });
                html += '</ul>';
                outputFilesList.innerHTML = html;
            } else {
                outputFilesList.innerHTML = '<p class="text-muted">No output files generated.</p>';
            }
        }
    }

    showFileResults(filename, result) {
        const modal = new bootstrap.Modal(document.getElementById('etlResultsModal'));
        const content = document.getElementById('etlResultsContent');
        
        content.innerHTML = `
            <h6>Processing Results for ${filename}</h6>
            <div class="row">
                <div class="col-md-6">
                    <h6>Processing Status</h6>
                    <p><strong>Status:</strong> <span class="badge bg-success">Completed</span></p>
                    <p><strong>Processing Time:</strong> ${(result.processing_time || 0).toFixed(2)}s</p>
                    
                    <h6 class="mt-3">Phase Results</h6>
                    <ul class="list-unstyled">
                        <li><strong>Extract:</strong> ${result.extract_result?.success ? 'Success' : 'Failed'}</li>
                        <li><strong>Transform:</strong> ${result.transform_result?.success ? 'Success' : 'Failed'}</li>
                        <li><strong>Load:</strong> ${result.load_result?.success ? 'Success' : 'Failed'}</li>
                    </ul>
                </div>
                <div class="col-md-6">
                    <h6>Output Details</h6>
                    <p><strong>Files Exported:</strong> ${result.load_result?.files_exported?.length || 0}</p>
                    <p><strong>Database Records:</strong> ${result.load_result?.database_records || 0}</p>
                    <p><strong>Vector Embeddings:</strong> ${result.load_result?.vector_embeddings || 0}</p>
                </div>
            </div>
        `;
        
        modal.show();
    }

    async openFile(filename) {
        try {
            const response = await fetch(`/aasx/api/open/${encodeURIComponent(filename)}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const result = await response.json();
            
            if (result.success) {
                this.showAlert('File opened successfully!', 'success');
            } else {
                throw new Error(result.error || 'Failed to open file');
            }
        } catch (error) {
            console.error('Open File Error:', error);
            this.showAlert(`Failed to open file: ${error.message}`, 'danger');
        }
    }

    async viewFileResults(filename) {
        try {
            const response = await fetch(`/aasx/api/results/${encodeURIComponent(filename)}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const result = await response.json();
            
            if (result.success) {
                this.showFileResults(filename, result.data);
            } else {
                throw new Error(result.error || 'Failed to load results');
            }
        } catch (error) {
            console.error('View Results Error:', error);
            this.showAlert(`Failed to load results: ${error.message}`, 'danger');
        }
    }

    async refreshFiles() {
        try {
            const response = await fetch('/aasx/api/refresh');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            // Reload the page to show updated files
            window.location.reload();
        } catch (error) {
            console.error('Refresh Error:', error);
            this.showAlert(`Failed to refresh files: ${error.message}`, 'danger');
        }
    }

    async exportResults() {
        try {
            const response = await fetch('/aasx/api/etl/export-results', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                // Trigger download
                const link = document.createElement('a');
                link.href = result.download_url;
                link.download = 'etl_results.json';
                link.click();
                this.showAlert('Results exported successfully!', 'success');
            } else {
                throw new Error(result.error || 'Export failed');
            }

        } catch (error) {
            console.error('Export Error:', error);
            this.showAlert(`Export failed: ${error.message}`, 'danger');
        }
    }

    showAlert(message, type = 'info') {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    // File Selection Methods
    selectAllFiles() {
        document.querySelectorAll('.file-checkbox').forEach(checkbox => {
            checkbox.checked = true;
            this.selectedFiles.add(checkbox.dataset.filename);
        });
        const selectAllCheckbox = document.getElementById('selectAllCheckbox');
        if (selectAllCheckbox) {
            selectAllCheckbox.checked = true;
        }
        this.updateSelectedCount();
    }

    deselectAllFiles() {
        document.querySelectorAll('.file-checkbox').forEach(checkbox => {
            checkbox.checked = false;
            this.selectedFiles.delete(checkbox.dataset.filename);
        });
        const selectAllCheckbox = document.getElementById('selectAllCheckbox');
        if (selectAllCheckbox) {
            selectAllCheckbox.checked = false;
        }
        this.updateSelectedCount();
    }

    invertSelection() {
        document.querySelectorAll('.file-checkbox').forEach(checkbox => {
            checkbox.checked = !checkbox.checked;
            if (checkbox.checked) {
                this.selectedFiles.add(checkbox.dataset.filename);
            } else {
                this.selectedFiles.delete(checkbox.dataset.filename);
            }
        });
        this.updateSelectedCount();
    }

    toggleSelectAll(checked) {
        document.querySelectorAll('.file-checkbox').forEach(checkbox => {
            checkbox.checked = checked;
            if (checked) {
                this.selectedFiles.add(checkbox.dataset.filename);
            } else {
                this.selectedFiles.delete(checkbox.dataset.filename);
            }
        });
        this.updateSelectedCount();
    }

    updateFileSelection(checkbox) {
        if (checkbox.checked) {
            this.selectedFiles.add(checkbox.dataset.filename);
        } else {
            this.selectedFiles.delete(checkbox.dataset.filename);
        }
        this.updateSelectedCount();
    }

    updateSelectedCount() {
        const count = this.selectedFiles.size;
        const selectedCountElement = document.getElementById('selectedCount');
        if (selectedCountElement) {
            selectedCountElement.textContent = `${count} selected`;
        }
    }

    // Preset Management
    loadPreset(presetName) {
        const preset = this.presets[presetName];
        if (!preset) return;

        // Show confirmation
        if (confirm(`Load "${preset.name}" preset?\n\n${preset.description}`)) {
            const config = preset.config;
            
            // Apply configuration
            Object.keys(config).forEach(key => {
                const element = document.getElementById(key);
                if (element) {
                    if (element.type === 'checkbox') {
                        element.checked = config[key];
                    } else if (element.type === 'range') {
                        element.value = config[key];
                        // Update display value
                        const displayElement = document.getElementById(key + 'Value');
                        if (displayElement) {
                            displayElement.textContent = config[key];
                        }
                    } else {
                        element.value = config[key];
                    }
                }
            });

            this.showAlert(`Loaded "${preset.name}" preset successfully!`, 'success');
        }
    }

    savePreset() {
        const presetName = prompt('Enter preset name:');
        if (!presetName) return;

        const config = this.getETLConfiguration();
        const preset = {
            name: presetName,
            description: prompt('Enter preset description:') || 'Custom configuration',
            config: config
        };

        // Save to localStorage
        const savedPresets = JSON.parse(localStorage.getItem('aasx_presets') || '{}');
        savedPresets[presetName] = preset;
        localStorage.setItem('aasx_presets', JSON.stringify(savedPresets));

        this.showAlert(`Preset "${presetName}" saved successfully!`, 'success');
    }

    resetConfig() {
        if (confirm('Reset all configuration to defaults?')) {
            this.loadPreset('standard');
        }
    }

    // Processing Mode
    updateProcessingMode(mode) {
        const selectedMode = document.querySelector(`input[name="processingMode"][value="${mode}"]`);
        if (selectedMode) {
            selectedMode.checked = true;
        }
    }

    // File Actions
    handleFileAction(action, filename) {
        switch (action) {
            case 'validate':
                this.validateSingleFile(filename);
                break;
            case 'preview':
                this.previewFile(filename);
                break;
            case 'download':
                this.downloadFile(filename);
                break;
            case 'info':
                this.showFileInfo(filename);
                break;
        }
    }

    validateSingleFile(filename) {
        this.showAlert(`Validating ${filename}...`, 'info');
        // Implementation for single file validation
    }

    processSelectedFiles() {
        if (this.selectedFiles.size === 0) {
            this.showAlert('Please select files to process', 'warning');
            return;
        }
        this.showAlert(`Processing ${this.selectedFiles.size} selected files...`, 'info');
        // Implementation for processing selected files
    }

    processBatchFiles() {
        this.showAlert('Starting batch processing...', 'info');
        // Implementation for batch processing
    }

    validateFiles() {
        this.showAlert('Validating all files...', 'info');
        // Implementation for validating all files
    }

    previewFile(filename) {
        this.showAlert(`Previewing ${filename}...`, 'info');
        // Implementation for file preview
    }

    downloadFile(filename) {
        window.open(`/aasx/api/packages/${encodeURIComponent(filename)}/download`, '_blank');
    }

    showFileInfo(filename) {
        fetch(`/aasx/api/packages/${encodeURIComponent(filename)}`)
            .then(response => response.json())
            .then(data => {
                const info = `
                    <div class="modal fade" id="fileInfoModal" tabindex="-1">
                        <div class="modal-dialog modal-lg">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title">File Information: ${filename}</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                </div>
                                <div class="modal-body">
                                    <div class="row">
                                        <div class="col-md-6">
                                            <h6>Package Details</h6>
                                            <p><strong>ID:</strong> ${data.package_id || 'N/A'}</p>
                                            <p><strong>Name:</strong> ${data.name || 'N/A'}</p>
                                            <p><strong>Version:</strong> ${data.version || 'N/A'}</p>
                                            <p><strong>Description:</strong> ${data.description || 'N/A'}</p>
                                        </div>
                                        <div class="col-md-6">
                                            <h6>Contents</h6>
                                            <p><strong>Assets:</strong> ${data.assets ? data.assets.length : 0}</p>
                                            <p><strong>Submodels:</strong> ${data.submodels ? data.submodels.length : 0}</p>
                                        </div>
                                    </div>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                // Remove existing modal if any
                const existingModal = document.getElementById('fileInfoModal');
                if (existingModal) {
                    existingModal.remove();
                }
                
                // Add new modal to body
                document.body.insertAdjacentHTML('beforeend', info);
                
                // Show modal
                const modal = new bootstrap.Modal(document.getElementById('fileInfoModal'));
                modal.show();
            })
            .catch(error => {
                console.error('Error fetching file info:', error);
                this.showAlert(`Failed to load file information: ${error.message}`, 'danger');
            });
    }

    showLaunchExplorerModal() {
        // Show the launch explorer modal
        const modal = new bootstrap.Modal(document.getElementById('launchExplorerModal'));
        modal.show();
    }

    selectAllExportFormats() {
        const formatCheckboxes = [
            'formatJson', 'formatYaml', 'formatCsv', 'formatGraph', 
            'formatRag', 'formatVectorDb', 'formatSqlite'
        ];
        
        formatCheckboxes.forEach(id => {
            const checkbox = document.getElementById(id);
            if (checkbox) {
                checkbox.checked = true;
            }
        });
        
        this.showAlert('All export formats selected', 'success', 2000);
    }

    deselectAllExportFormats() {
        const formatCheckboxes = [
            'formatJson', 'formatYaml', 'formatCsv', 'formatGraph', 
            'formatRag', 'formatVectorDb', 'formatSqlite'
        ];
        
        formatCheckboxes.forEach(id => {
            const checkbox = document.getElementById(id);
            if (checkbox) {
                checkbox.checked = false;
            }
        });
        
        this.showAlert('All export formats deselected', 'warning', 2000);
    }
}

// Project Management and File Upload functionality
class ProjectManager {
    constructor() {
        this.projects = [];
        this.currentProject = null;
        this.init();
    }

    async init() {
        await this.loadProjects();
        this.setupEventListeners();
        this.updateStats();
    }

    setupEventListeners() {
        // Prevent multiple event listener bindings
        if (this.eventListenersSetup) {
            console.log('⚠️ Event listeners already setup, skipping...');
            return;
        }
        
        console.log('🔧 Setting up ProjectManager event listeners...');
        
        // Project creation
        $('#createProject').on('click', () => {
            console.log('🔧 Create Project button clicked!');
            this.showCreateProjectModal();
        });
        $('#saveProject').on('click', () => this.createProject());
        
        // Project management - removed loadTestProjects button (redundant with refresh)
        
        // File upload
        $('#fileUploadForm').on('submit', (e) => this.handleFileUpload(e));
        $('#urlUploadForm').on('submit', (e) => this.handleUrlUpload(e));
        
        // Modal events
        $('#projectModal').on('hidden.bs.modal', () => this.resetCreateProjectForm());
        
        // ETL Pipeline Management Event Listeners
        $('#etlProjectSelect').on('change', () => this.onPipelineProjectChange());
        $('input[name="pipelineMode"]').on('change', () => this.onPipelineModeChange());
        $('#refreshPipelineStatus').on('click', () => this.refreshPipelineStatus());
        $('#refreshEtlFiles').on('click', () => this.refreshEtlFiles());
        $('#runSelectedPipeline').on('click', () => this.runSelectedPipeline());
        $('#runAllData').on('click', () => this.runAllDataPipeline());
        
        // Pipeline configuration event listeners
        $('#pipelineFormatJson, #pipelineFormatYaml, #pipelineFormatCsv, #pipelineFormatGraph, #pipelineFormatRag, #pipelineFormatVectorDb').on('change', () => this.updatePipelineConfiguration());
        $('#pipelineEnableValidation, #pipelineEnableEnrichment, #pipelineEnableQualityChecks, #pipelineParallelProcessing').on('change', () => this.updatePipelineConfiguration());
        
        // Launch Explorer button - remove any existing listeners first
        $('#launchExplorer').off('click').on('click', () => {
            console.log('🚀 Launch Explorer button clicked!');
            launchExplorer('direct');
        });
        
        // Refresh button
        $('#refreshFiles').on('click', () => {
            this.refreshAndSync();
        });
        
        // Project & File Management Event Listeners
        $('#manageProjectSelect').on('change', () => this.onManageProjectChange());
        $('#manageFileSelect').on('change', () => this.onManageFileChange());
        $('#viewProjectDetails').on('click', () => this.viewSelectedProject());
        $('#deleteProject').on('click', () => this.deleteSelectedProject());
        $('#viewFileDetails').on('click', () => this.viewSelectedFile());
        $('#deleteFile').on('click', () => this.deleteSelectedFile());
        $('#processFile').on('click', () => this.processSelectedFile());
        
        this.eventListenersSetup = true;
        console.log('✅ ProjectManager event listeners setup complete');
    }

    async loadTestProjects() {
        try {
            const response = await fetch('/aasx/api/projects/load-test', {
                method: 'POST'
            });
            
            if (response.ok) {
                const result = await response.json();
                this.projects = result.projects || [];
                this.renderProjects();
                this.updateProjectSelects();
                this.updateStats();
                this.showSuccessMessage(`Loaded ${result.projects_count} projects with ${result.files_count} files!`);
            } else {
                console.error('Failed to load projects');
            }
        } catch (error) {
            console.error('Error loading projects:', error);
        }
    }

    async loadProjects() {
        try {
            console.log('🔄 Loading projects...');
            const response = await fetch('/aasx/api/projects');
            console.log('📡 Response status:', response.status);
            
            if (response.ok) {
                this.projects = await response.json();
                console.log('📦 Loaded projects:', this.projects);
                this.renderProjects();
                this.updateProjectSelects();
                this.updateStats();
                
                // Debug: Check if stats elements exist
                console.log('🔍 Checking stats elements:');
                console.log('totalProjects element:', $('#totalProjects').length);
                console.log('totalFiles element:', $('#totalFiles').length);
                console.log('totalSize element:', $('#totalSize').length);
                console.log('processedFiles element:', $('#processedFiles').length);
            } else {
                console.error('❌ Failed to load projects:', response.status);
            }
        } catch (error) {
            console.error('❌ Error loading projects:', error);
        }
    }

    renderProjects() {
        const projectsList = $('#projectsList');
        
        if (this.projects.length === 0) {
            projectsList.html(`
                <div class="text-center text-muted py-4">
                    <i class="fas fa-folder-open fa-3x mb-3"></i>
                    <h5>No Projects Created</h5>
                    <p>Create your first project to start organizing AASX files</p>
                    <button class="btn btn-success" onclick="projectManager.showCreateProjectModal()">
                        <i class="fas fa-plus"></i>
                        Create First Project
                    </button>
                </div>
            `);
            return;
        }

        const projectsHtml = this.projects.map(project => this.renderProjectCard(project)).join('');
        projectsList.html(`
            <div class="row">
                ${projectsHtml}
            </div>
        `);
    }

    renderProjectCard(project) {
        const fileCount = project.file_count || 0;
        const totalSize = this.formatFileSize(project.total_size || 0);
        const createdDate = new Date(project.created_at).toLocaleDateString();
        
        return `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card h-100 border-success">
                    <div class="card-header bg-success text-white d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">
                            <i class="fas fa-folder"></i>
                            ${project.name}
                        </h6>
                        <div class="dropdown">
                            <button class="btn btn-sm btn-outline-light dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                <i class="fas fa-ellipsis-v"></i>
                            </button>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="#" onclick="projectManager.viewProject('${project.id}')">
                                    <i class="fas fa-eye text-primary"></i> View Details
                                </a></li>
                                <li><a class="dropdown-item" href="#" onclick="projectManager.uploadToProject('${project.id}')">
                                    <i class="fas fa-upload text-info"></i> Upload File
                                </a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item text-danger" href="#" onclick="projectManager.deleteProject('${project.id}')">
                                    <i class="fas fa-trash"></i> Delete Project
                                </a></li>
                            </ul>
                        </div>
                    </div>
                    <div class="card-body">
                        <p class="card-text text-muted">${project.description || 'No description'}</p>
                        <div class="row text-center">
                            <div class="col-6">
                                <h6 class="text-success">${fileCount}</h6>
                                <small class="text-muted">Files</small>
                            </div>
                            <div class="col-6">
                                <h6 class="text-info">${totalSize}</h6>
                                <small class="text-muted">Size</small>
                            </div>
                        </div>
                        <div class="mt-2">
                            ${project.tags && project.tags.length > 0 ? 
                                project.tags.map(tag => `<span class="badge bg-secondary me-1">${tag}</span>`).join('') : 
                                '<span class="text-muted">No tags</span>'
                            }
                        </div>
                    </div>
                    <div class="card-footer text-muted">
                        <small>Created: ${createdDate}</small>
                    </div>
                </div>
            </div>
        `;
    }

    updateProjectSelects() {
        console.log('🔍 Updating project selects with projects:', this.projects);
        const options = this.projects.map(project => {
            console.log('🔍 Project option:', project.id, project.name);
            return `<option value="${project.id}">${project.name}</option>`;
        }).join('');
        
        $('#uploadProjectSelect, #urlProjectSelect, #etlProjectSelect, #manageProjectSelect').html(`
            <option value="">Choose a project...</option>
            ${options}
        `);
    }

    updateStats() {
        console.log('🔍 Updating stats with projects:', this.projects);
        
        const totalProjects = this.projects.length;
        const totalFiles = this.projects.reduce((sum, p) => sum + (p.file_count || 0), 0);
        const totalSize = this.projects.reduce((sum, p) => sum + (p.total_size || 0), 0);
        
        // Calculate processed files based on file status
        let processedFiles = 0;
        this.projects.forEach(project => {
            if (project.files) {
                processedFiles += project.files.filter(file => 
                    file.processing_status === 'completed'
                ).length;
            }
        });

        console.log('📊 Stats calculated:', {
            totalProjects,
            totalFiles,
            totalSize,
            processedFiles
        });

        // Update all stat elements (both in main dashboard and project management)
        $('.total-projects, #totalProjects').text(totalProjects);
        $('.total-files, #totalFiles').text(totalFiles);
        $('.total-size, #totalSize').text(this.formatFileSize(totalSize));
        $('.processed-files, #processedFiles').text(processedFiles);
        
        console.log('✅ Stats updated in DOM');
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    getFileStatusInfo(status) {
        const statusMap = {
            'not_processed': {
                label: 'Not Processed',
                badgeClass: 'bg-secondary',
                description: 'File has been uploaded but not processed yet'
            },
            'uploaded': {
                label: 'Not Processed',
                badgeClass: 'bg-secondary',
                description: 'File has been uploaded but not processed yet'
            },
            'processing': {
                label: 'Processing',
                badgeClass: 'bg-warning',
                description: 'File is currently being processed'
            },
            'completed': {
                label: 'Completed',
                badgeClass: 'bg-success',
                description: 'File has been processed successfully'
            },
            'error': {
                label: 'Error',
                badgeClass: 'bg-danger',
                description: 'File processing failed'
            },
            'failed': {
                label: 'Failed',
                badgeClass: 'bg-danger',
                description: 'File processing failed'
            },
            'queued': {
                label: 'Queued',
                badgeClass: 'bg-info',
                description: 'File is queued for processing'
            }
        };
        
        return statusMap[status] || statusMap['not_processed'];
    }

    showCreateProjectModal() {
        console.log('🔧 Showing project creation modal...');
        $('#projectModal').modal('show');
    }

    resetCreateProjectForm() {
        $('#projectForm')[0].reset();
    }

    async createProject() {
        const name = $('#projectName').val().trim();
        const description = $('#projectDescription').val().trim();
        const tags = $('#projectTags').val().trim().split(',').map(t => t.trim()).filter(t => t);

        if (!name) {
            alert('Project name is required');
            return;
        }

        try {
            const response = await fetch('/aasx/api/projects', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: name,
                    description: description || null,
                    tags: tags.length > 0 ? tags : null
                })
            });

            if (response.ok) {
                const newProject = await response.json();
                this.projects.push(newProject);
                this.renderProjects();
                this.updateProjectSelects();
                this.updateStats();
                $('#projectModal').modal('hide');
                this.showSuccessMessage('Project created successfully!');
            } else {
                const error = await response.json();
                alert('Failed to create project: ' + error.detail);
            }
        } catch (error) {
            console.error('Error creating project:', error);
            alert('Error creating project');
        }
    }

    async deleteProject(projectId) {
        if (!confirm('Are you sure you want to delete this project? This will also delete all files in the project.')) {
            return;
        }

        try {
            const response = await fetch(`/aasx/api/projects/${projectId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.projects = this.projects.filter(p => p.id !== projectId);
                this.renderProjects();
                this.updateProjectSelects();
                this.updateStats();
                this.showSuccessMessage('Project deleted successfully!');
            } else {
                const error = await response.json();
                alert('Failed to delete project: ' + error.detail);
            }
        } catch (error) {
            console.error('Error deleting project:', error);
            alert('Error deleting project');
        }
    }

    async viewProject(projectId) {
        try {
            const response = await fetch(`/aasx/api/projects/${projectId}`);
            if (response.ok) {
                const project = await response.json();
                const filesResponse = await fetch(`/aasx/api/projects/${projectId}/files`);
                const files = filesResponse.ok ? await filesResponse.json() : [];
                
                this.showProjectDetails(project, files);
            } else {
                alert('Failed to load project details');
            }
        } catch (error) {
            console.error('Error loading project details:', error);
            alert('Error loading project details');
        }
    }

    showProjectDetails(project, files) {
        const filesHtml = files.map(file => `
            <tr>
                <td>${file.original_filename}</td>
                <td>${this.formatFileSize(file.size)}</td>
                <td>${new Date(file.upload_date).toLocaleDateString()}</td>
                <td>
                    <span class="badge bg-${this.getStatusBadgeColor(file.status)}">${file.status}</span>
                </td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="projectManager.processFile('${project.id}', '${file.id}')">
                        <i class="fas fa-cogs"></i> Process
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="projectManager.deleteFile('${project.id}', '${file.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');

        $('#projectDetailsContent').html(`
            <div class="row">
                <div class="col-md-6">
                    <h6>Project Information</h6>
                    <table class="table table-sm">
                        <tr><td>Name:</td><td>${project.name}</td></tr>
                        <tr><td>Description:</td><td>${project.description || 'No description'}</td></tr>
                        <tr><td>Created:</td><td>${new Date(project.created_at).toLocaleString()}</td></tr>
                        <tr><td>Files:</td><td>${project.file_count}</td></tr>
                        <tr><td>Total Size:</td><td>${this.formatFileSize(project.total_size)}</td></tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6>Tags</h6>
                    <div>
                        ${project.tags && project.tags.length > 0 ? 
                            project.tags.map(tag => `<span class="badge bg-secondary me-1">${tag}</span>`).join('') : 
                            '<span class="text-muted">No tags</span>'
                        }
                    </div>
                </div>
            </div>
            <hr>
            <h6>Files (${files.length})</h6>
            ${files.length > 0 ? `
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Filename</th>
                                <th>Size</th>
                                <th>Upload Date</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${filesHtml}
                        </tbody>
                    </table>
                </div>
            ` : '<p class="text-muted">No files uploaded yet.</p>'}
        `);

        $('#projectDetailsModal').modal('show');
    }

    getStatusBadgeColor(status) {
        switch (status) {
            case 'uploaded': return 'info';
            case 'processing': return 'warning';
            case 'completed': return 'success';
            case 'error': return 'danger';
            case 'failed': return 'danger';
            case 'not_processed': return 'secondary';
            default: return 'secondary';
        }
    }

    async handleFileUpload(e) {
        e.preventDefault();
        
        const projectId = $('#uploadProjectSelect').val();
        const fileInput = $('#aasxFileInput')[0];
        const description = $('#fileDescription').val();

        if (!projectId) {
            alert('Please select a project');
            return;
        }

        if (!fileInput.files[0]) {
            alert('Please select a file');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        if (description) {
            formData.append('description', description);
        }

        try {
            const response = await fetch(`/aasx/api/projects/${projectId}/upload`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const fileInfo = await response.json();
                await this.loadProjects(); // Refresh projects to update stats
                
                // Refresh file lists in UI components
                await this.refreshFileLists(projectId);
                
                this.showSuccessMessage('File uploaded successfully!');
                $('#fileUploadForm')[0].reset();
            } else {
                const error = await response.json();
                if (response.status === 409) {
                    // Duplicate file error
                    alert('⚠️ Duplicate File: ' + error.detail);
                } else {
                    alert('Failed to upload file: ' + error.detail);
                }
            }
        } catch (error) {
            console.error('Error uploading file:', error);
            alert('Error uploading file');
        }
    }

    async handleUrlUpload(e) {
        e.preventDefault();
        
        const projectId = $('#urlProjectSelect').val();
        const url = $('#aasxFileUrl').val();
        const description = $('#urlFileDescription').val();

        if (!projectId) {
            alert('Please select a project');
            return;
        }

        if (!url) {
            alert('Please enter a URL');
            return;
        }

        try {
            const response = await fetch(`/aasx/api/projects/${projectId}/upload-url`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    project_id: projectId,
                    file_url: url,
                    file_description: description || null
                })
            });

            if (response.ok) {
                const fileInfo = await response.json();
                await this.loadProjects(); // Refresh projects to update stats
                
                // Refresh file lists in UI components
                await this.refreshFileLists(projectId);
                
                this.showSuccessMessage('File downloaded and uploaded successfully!');
                $('#urlUploadForm')[0].reset();
            } else {
                const error = await response.json();
                if (response.status === 409) {
                    // Duplicate file error
                    alert('⚠️ Duplicate File: ' + error.detail);
                } else {
                    alert('Failed to upload file from URL: ' + error.detail);
                }
            }
        } catch (error) {
            console.error('Error uploading file from URL:', error);
            alert('Error uploading file from URL');
        }
    }

    async processFile(projectId, fileId) {
        try {
            const response = await fetch(`/aasx/api/projects/${projectId}/files/${fileId}/process`, {
                method: 'POST'
            });

            if (response.ok) {
                const result = await response.json();
                this.showFileProcessingResult(result);
                await this.loadProjects(); // Refresh to update file status
            } else {
                const error = await response.json();
                alert('Failed to process file: ' + error.detail);
            }
        } catch (error) {
            console.error('Error processing file:', error);
            alert('Error processing file');
        }
    }

    async deleteFile(projectId, fileId) {
        if (!confirm('Are you sure you want to delete this file?')) {
            return;
        }

        try {
            const response = await fetch(`/aasx/api/projects/${projectId}/files/${fileId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                await this.loadProjects(); // Refresh projects to update stats
                
                // Refresh file lists in UI components
                await this.refreshFileLists(projectId);
                
                this.showSuccessMessage('File deleted successfully!');
                $('#projectDetailsModal').modal('hide');
            } else {
                const error = await response.json();
                alert('Failed to delete file: ' + error.detail);
            }
        } catch (error) {
            console.error('Error deleting file:', error);
            alert('Error deleting file');
        }
    }

    async refreshFileLists(projectId) {
        // Refresh ETL Pipeline Management file list if this project is selected
        const etlProjectId = $('#etlProjectSelect').val();
        if (etlProjectId === projectId) {
            await this.loadProjectFiles(projectId);
        }
        
        // Refresh Project & File Management dropdowns if this project is selected
        const manageProjectId = $('#manageProjectSelect').val();
        if (manageProjectId === projectId) {
            await this.onManageProjectChange();
        }
    }

    async refreshAndSync() {
        try {
            console.log('🔄 Starting refresh and sync...');
            
            // Show loading state
            const refreshButton = $('#refreshFiles');
            const originalText = refreshButton.html();
            refreshButton.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Syncing...');
            
            // First, sync memory with disk
            const syncResponse = await fetch('/aasx/api/projects/sync', {
                method: 'POST'
            });
            
            if (syncResponse.ok) {
                const syncResult = await syncResponse.json();
                console.log('✅ Sync completed:', syncResult);
                
                if (syncResult.files_removed > 0) {
                    this.showSuccessMessage(`Sync completed! Removed ${syncResult.files_removed} orphaned files.`);
                } else {
                    this.showSuccessMessage('Sync completed! All files are up to date.');
                }
            } else {
                console.error('❌ Sync failed:', syncResponse.status);
                this.showErrorMessage('Failed to sync projects with disk');
            }
            
            // Then, refresh the projects data
            await this.loadProjects();
            
            // Refresh all file lists for currently selected projects
            const etlProjectId = $('#etlProjectSelect').val();
            if (etlProjectId) {
                await this.loadProjectFiles(etlProjectId);
            }
            
            const manageProjectId = $('#manageProjectSelect').val();
            if (manageProjectId) {
                await this.onManageProjectChange();
            }
            
            console.log('✅ Refresh and sync completed successfully');
            
        } catch (error) {
            console.error('❌ Error during refresh and sync:', error);
            this.showErrorMessage('Error during refresh and sync: ' + error.message);
        } finally {
            // Restore button state
            const refreshButton = $('#refreshFiles');
            refreshButton.prop('disabled', false).html(originalText);
        }
    }

    showFileProcessingResult(result) {
        $('#fileProcessingContent').html(`
            <div class="alert alert-${result.status === 'completed' ? 'success' : 'danger'}">
                <h6>Processing Result</h6>
                <p><strong>Status:</strong> ${result.status}</p>
                <p><strong>Processing Time:</strong> ${result.processing_time || 'N/A'}</p>
                ${result.error ? `<p><strong>Error:</strong> ${result.error}</p>` : ''}
            </div>
            ${result.status === 'completed' ? `
                <div class="row">
                    <div class="col-md-6">
                        <h6>Processing Statistics</h6>
                        <ul class="list-unstyled">
                            <li><strong>Files Exported:</strong> ${result.load_result?.files_exported?.length || 0}</li>
                            <li><strong>Database Records:</strong> ${result.load_result?.database_records || 0}</li>
                            <li><strong>Vector Embeddings:</strong> ${result.load_result?.vector_embeddings || 0}</li>
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <h6>Output Files</h6>
                        <ul class="list-unstyled">
                            ${result.load_result?.files_exported?.map(file => `<li><code>${file}</code></li>`).join('') || '<li>No files exported</li>'}
                        </ul>
                    </div>
                </div>
            ` : ''}
        `);

        $('#fileProcessingModal').modal('show');
    }

    showSuccessMessage(message) {
        // Use the global notification system if available
        if (window.AASXFramework && window.AASXFramework.showNotification) {
            window.AASXFramework.showNotification(message, 'success');
        } else {
            alert(message);
        }
    }

    showErrorMessage(message) {
        // Use the global notification system if available
        if (window.AASXFramework && window.AASXFramework.showNotification) {
            window.AASXFramework.showNotification(message, 'error');
        } else {
            alert('Error: ' + message);
        }
    }

    uploadToProject(projectId) {
        $('#uploadProjectSelect').val(projectId);
        $('#urlProjectSelect').val(projectId);
        // Scroll to upload section
        $('html, body').animate({
            scrollTop: $('#fileUploadForm').offset().top - 100
        }, 500);
    }

    // ETL Pipeline Management Methods
    async onPipelineProjectChange() {
        const projectId = $('#etlProjectSelect').val();
        if (projectId) {
            await this.loadProjectFiles(projectId);
        } else {
            this.clearPipelineFileSelection();
        }
    }

    onPipelineModeChange() {
        const mode = $('input[name="pipelineMode"]:checked').val();
        this.updatePipelineModeUI(mode);
    }

    async loadProjectFiles(projectId) {
        try {
            const response = await fetch(`/aasx/api/projects/${projectId}/files`);
            if (response.ok) {
                const files = await response.json();
                this.renderPipelineFileSelection(files);
            } else {
                console.error('Failed to load project files');
                this.clearPipelineFileSelection();
            }
        } catch (error) {
            console.error('Error loading project files:', error);
            this.clearPipelineFileSelection();
        }
    }

    async refreshEtlFiles() {
        const projectId = $('#etlProjectSelect').val();
        if (projectId) {
            console.log('🔄 Refreshing ETL files for project:', projectId);
            await this.loadProjectFiles(projectId);
            this.showSuccessMessage('File list refreshed successfully!');
        } else {
            this.showErrorMessage('Please select a project first');
        }
    }

    renderPipelineFileSelection(files) {
        const fileSelection = $('#etlFilesList');
        
        if (files.length === 0) {
            fileSelection.html(`
                <div class="text-center text-muted py-4">
                    <i class="fas fa-file-alt fa-3x mb-3"></i>
                    <h5>No Files Available</h5>
                    <p>This project has no files for ETL processing</p>
                </div>
            `);
            return;
        }

        const filesHtml = files.map(file => {
            // Get processing status for this file
            const status = file.status || 'not_processed';
            const statusInfo = this.getFileStatusInfo(status);
            
            return `
                <div class="form-check mb-4 p-3 border rounded">
                    <input class="form-check-input pipeline-file-checkbox" type="checkbox" 
                           id="pipeline-file-${file.id}" value="${file.id}" 
                           data-filename="${file.original_filename}"
                           ${status === 'completed' ? 'disabled' : ''}>
                    <label class="form-check-label w-100" for="pipeline-file-${file.id}">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <div class="d-flex align-items-center mb-2">
                                    <i class="fas fa-file-archive text-primary me-3"></i>
                                    <h6 class="mb-0 me-4">${file.original_filename}</h6>
                                    <span class="badge ${statusInfo.badgeClass} fs-6">${statusInfo.label}</span>
                                </div>
                                <div class="ms-5">
                                    <p class="text-muted mb-1">${file.description || 'No description'}</p>
                                    ${status === 'completed' ? '<p class="text-success mb-0"><i class="fas fa-check-circle me-2"></i>Already processed successfully</p>' : ''}
                                    ${status === 'failed' ? '<p class="text-danger mb-0"><i class="fas fa-exclamation-triangle me-2"></i>Previous processing failed</p>' : ''}
                                    ${status === 'processing' ? '<p class="text-warning mb-0"><i class="fas fa-spinner fa-spin me-2"></i>Currently processing</p>' : ''}
                                </div>
                            </div>
                            <div class="col-md-4 text-end">
                                <div class="text-muted">
                                    <i class="fas fa-weight-hanging me-1"></i>
                                    ${this.formatFileSize(file.size)}
                                </div>
                            </div>
                        </div>
                    </label>
                </div>
            `;
        }).join('');

        fileSelection.html(`
            <div class="mb-2">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="pipelineSelectAllFiles">
                    <label class="form-check-label" for="pipelineSelectAllFiles">
                        <strong>Select All Files</strong>
                    </label>
                </div>
            </div>
            <hr>
            <div class="pipeline-files-list">
                ${filesHtml}
            </div>
        `);

        // Add event listeners for file selection
        $('#pipelineSelectAllFiles').on('change', (e) => {
            const checked = e.target.checked;
            // Only select files that are not completed
            $('.pipeline-file-checkbox:not(:disabled)').prop('checked', checked);
            this.updatePipelineFileSelection();
        });

        $('.pipeline-file-checkbox').on('change', () => {
            this.updatePipelineFileSelection();
        });
    }

    clearPipelineFileSelection() {
        $('#etlFilesList').html(`
            <div class="text-center text-muted py-4">
                <i class="fas fa-file-alt fa-3x mb-3"></i>
                <h5>No Files Available</h5>
                <p>Select a project to view available files for ETL processing</p>
            </div>
        `);
    }

    updatePipelineModeUI(mode) {
        const fileSelection = $('#pipelineFileSelection');
        
        switch (mode) {
            case 'single':
                fileSelection.find('.pipeline-file-checkbox').prop('type', 'radio').attr('name', 'singleFile');
                break;
            case 'all':
                fileSelection.find('.pipeline-file-checkbox').prop('type', 'checkbox').removeAttr('name');
                $('#pipelineSelectAllFiles').prop('checked', true).trigger('change');
                break;
            case 'selected':
                fileSelection.find('.pipeline-file-checkbox').prop('type', 'checkbox').removeAttr('name');
                break;
        }
    }

    updatePipelineFileSelection() {
        const selectedFiles = $('.pipeline-file-checkbox:checked');
        const totalFiles = $('.pipeline-file-checkbox').length;
        
        // Update any counters or UI elements
        console.log(`Selected ${selectedFiles.length} of ${totalFiles} files for pipeline processing`);
    }

    updatePipelineProjectSelects() {
        const options = this.projects.map(project => 
            `<option value="${project.id}">${project.name}</option>`
        ).join('');
        
        $('#etlProjectSelect').html(`
            <option value="">Choose a project...</option>
            ${options}
        `);
    }

    getETLConfiguration() {
        const formats = [];
        if ($('#formatJson').is(':checked')) formats.push('json');
        if ($('#formatYaml').is(':checked')) formats.push('yaml');
        if ($('#formatCsv').is(':checked')) formats.push('csv');
        if ($('#formatGraph').is(':checked')) formats.push('graph');
        if ($('#formatRag').is(':checked')) formats.push('rag');
        if ($('#formatVectorDb').is(':checked')) formats.push('vector_db');

        const options = {
            hybrid_processing: $('#hybridProcessing').is(':checked'),
            enable_validation: $('#enableValidation').is(':checked'),
            enable_backup: $('#enableBackup').is(':checked'),
            parallel_processing: $('#parallelProcessing').is(':checked'),
            enable_quality_checks: $('#enableQualityChecks').is(':checked'),
            enable_enrichment: $('#enableEnrichment').is(':checked'),
            normalize_ids: $('#normalizeIds').is(':checked'),
            enable_sqlite: $('#enableSQLite').is(':checked'),
            enable_vector_db: $('#enableVectorDB').is(':checked'),
            enable_rag_export: $('#enableRAGExport').is(':checked'),
            vector_db_type: $('#vectorDBType').val(),
            embedding_model: $('#embeddingModel').val(),
            batch_size: parseInt($('#batchSize').val()) || 10,
            max_workers: parseInt($('#maxWorkers').val()) || 4,
            memory_limit: parseInt($('#memoryLimit').val()) || 0,
            quality_threshold: parseFloat($('#qualityThreshold').val()) || 0.8,
            chunk_size: parseInt($('#chunkSize').val()) || 512,
            output_formats: formats
        };

        console.log('ETL configuration:', options);
        return options;
    }

    async refreshPipelineStatus() {
        try {
            // This would call an API to get current pipeline status
            const response = await fetch('/aasx/api/etl/stats');
            if (response.ok) {
                const stats = await response.json();
                this.updatePipelineStatusDisplay(stats);
            }
        } catch (error) {
            console.error('Error refreshing pipeline status:', error);
        }
    }

    updatePipelineStatusDisplay(stats) {
        // Update the pipeline status indicator
        const indicator = $('.pipeline-status-indicator');
        const statusText = indicator.find('p');
        const statusIcon = indicator.find('i');

        // Update processed/pending counts
        $('#pipelineProcessedFiles').text(stats.processed_files || 0);
        $('#pipelinePendingFiles').text(stats.pending_files || 0);

        // Update status indicator
        if (stats.is_running) {
            statusIcon.removeClass().addClass('fas fa-spinner fa-spin fa-2x text-warning');
            statusText.text('Processing...');
        } else if (stats.processed_files > 0) {
            statusIcon.removeClass().addClass('fas fa-check-circle fa-2x text-success');
            statusText.text('Completed');
        } else {
            statusIcon.removeClass().addClass('fas fa-circle fa-2x text-secondary');
            statusText.text('Ready');
        }
    }

    async runSelectedPipeline() {
        const projectId = $('#etlProjectSelect').val();
        const selectedFiles = $('.pipeline-file-checkbox:checked');
        const config = this.getETLConfiguration();

        if (!projectId) {
            alert('Please select a project');
            return;
        }

        if (selectedFiles.length === 0) {
            alert('Please select at least one file');
            return;
        }

        const fileIds = selectedFiles.map((i, el) => $(el).val()).get();

        try {
            // First, get the file information for the selected files
            const filesResponse = await fetch(`/aasx/api/projects/${projectId}/files`);
            if (!filesResponse.ok) {
                throw new Error('Failed to load project files');
            }
            
            const allFiles = await filesResponse.json();
            const selectedFileInfo = allFiles.filter(file => fileIds.includes(file.id));
            const filenames = selectedFileInfo.map(file => file.original_filename);

            // Prepare ETL configuration in the format expected by the backend
            const etlConfig = {
                extract: {
                    hybrid_processing: config.hybrid_processing,
                    enable_validation: config.enable_validation,
                    enable_backup: config.enable_backup
                },
                transform: {
                    enable_quality_checks: config.enable_quality_checks,
                    enable_enrichment: config.enable_enrichment,
                    normalize_ids: config.normalize_ids
                },
                load: {
                    output_formats: config.output_formats,
                    enable_sqlite: config.enable_sqlite,
                    enable_vector_db: config.enable_vector_db,
                    enable_rag_export: config.enable_rag_export,
                    vector_db_type: config.vector_db_type,
                    embedding_model: config.embedding_model,
                    batch_size: config.batch_size,
                    memory_limit: config.memory_limit,
                    quality_threshold: config.quality_threshold,
                    chunk_size: config.chunk_size
                },
                files: filenames,
                project_id: projectId, // Pass project ID for project-based output
                parallel_processing: config.parallel_processing,
                max_workers: config.max_workers
            };

            console.log('Running ETL pipeline with config:', etlConfig);

            // Show success message immediately when button is clicked
            this.showSuccessMessage(`ETL pipeline started successfully! Processing ${filenames.length} files.`);
            
            // Show progress immediately when button is clicked
            this.startPipelineStatusPolling();
            
            // Show processing indicator
            this.updatePipelineStatusDisplay({ is_running: true });

            // Call the ETL pipeline API
            const response = await fetch('/aasx/api/etl/run', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(etlConfig)
            });

            if (response.ok) {
                const result = await response.json();
                
                // Update file statuses to processing
                selectedFileInfo.forEach(file => {
                    this.updateFileStatusInList(file.original_filename, 'processing');
                });
            } else {
                const error = await response.json();
                alert('Failed to start pipeline: ' + error.detail);
                this.updatePipelineStatusDisplay({ is_running: false });
            }
        } catch (error) {
            console.error('Error running pipeline:', error);
            alert('Error starting pipeline: ' + error.message);
            this.updatePipelineStatusDisplay({ is_running: false });
        }
    }

    async runAllDataPipeline() {
        const projectId = $('#etlProjectSelect').val();
        const config = this.getETLConfiguration();

        if (!projectId) {
            alert('Please select a project first');
            return;
        }

        // Confirm with user before running on all data
        const confirmed = confirm('This will run ETL on ALL files in the selected project. Are you sure you want to continue?');
        if (!confirmed) {
            return;
        }

        try {
            // Get all files in the project
            const filesResponse = await fetch(`/aasx/api/projects/${projectId}/files`);
            if (!filesResponse.ok) {
                throw new Error('Failed to load project files');
            }
            
            const allFiles = await filesResponse.json();
            const filenames = allFiles.map(file => file.original_filename);

            if (filenames.length === 0) {
                alert('No files found in the selected project');
                return;
            }

            // Prepare ETL configuration in the format expected by the backend
            const etlConfig = {
                extract: {
                    hybrid_processing: config.hybrid_processing,
                    enable_validation: config.enable_validation,
                    enable_backup: config.enable_backup
                },
                transform: {
                    enable_quality_checks: config.enable_quality_checks,
                    enable_enrichment: config.enable_enrichment,
                    normalize_ids: config.normalize_ids
                },
                load: {
                    output_formats: config.output_formats,
                    enable_sqlite: config.enable_sqlite,
                    enable_vector_db: config.enable_vector_db,
                    enable_rag_export: config.enable_rag_export,
                    vector_db_type: config.vector_db_type,
                    embedding_model: config.embedding_model,
                    batch_size: config.batch_size,
                    memory_limit: config.memory_limit,
                    quality_threshold: config.quality_threshold,
                    chunk_size: config.chunk_size
                },
                files: filenames,
                project_id: projectId, // Pass project ID for project-based output
                parallel_processing: config.parallel_processing,
                max_workers: config.max_workers
            };

            console.log('Running ETL on all data with config:', etlConfig);

            // Show success message immediately when button is clicked
            this.showSuccessMessage(`ETL pipeline started successfully! Processing all ${filenames.length} files in the project.`);
            
            // Show progress immediately when button is clicked
            this.startPipelineStatusPolling();
            
            // Show processing indicator
            this.updatePipelineStatusDisplay({ is_running: true });

            // Call the ETL pipeline API
            const response = await fetch('/aasx/api/etl/run', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(etlConfig)
            });

            if (response.ok) {
                const result = await response.json();
                
                // Update all file statuses to processing
                allFiles.forEach(file => {
                    this.updateFileStatusInList(file.original_filename, 'processing');
                });
            } else {
                const error = await response.json();
                alert('Failed to start pipeline: ' + error.detail);
                this.updatePipelineStatusDisplay({ is_running: false });
            }
        } catch (error) {
            console.error('Error running ETL on all data:', error);
            alert('Error starting pipeline: ' + error.message);
            this.updatePipelineStatusDisplay({ is_running: false });
        }
    }

    startPipelineStatusPolling() {
        console.log('🚀 Starting pipeline status polling...');
        
        // Show the ETL progress section
        const progressSection = $('#etlProgress');
        console.log('🔍 Progress section element:', progressSection.length);
        progressSection.show();
        console.log('✅ Progress section shown');
        
        this.updateETLStatus('ETL pipeline is starting...', 'info');
        
        // Initialize progress to 0
        this.updateETLProgress(0, 0, 0, 0);
        
        // Smart progress tracking with backend completion detection
        let lastBackendUpdate = Date.now();
        let consecutiveNoUpdates = 0;
        let backendCompleted = false;
        let currentPhase = 'extract';
        let extractProgress = 0;
        let transformProgress = 0;
        let loadProgress = 0;
        let overallProgress = 0;
        
        // Progressive simulation that adapts to backend status
        this.progressSimulation = setInterval(() => {
            // If backend completed, finish the simulation
            if (backendCompleted) {
                clearInterval(this.progressSimulation);
                this.progressSimulation = null;
                this.updateETLProgress(100, 100, 100, 100);
                this.updateETLStatus('ETL pipeline completed successfully!', 'success');
                setTimeout(() => {
                    this.stopPipelineStatusPolling();
                }, 3000);
                return;
            }
            
            // Continue simulation based on current phase
            switch (currentPhase) {
                case 'extract':
                    extractProgress += 2;
                    if (extractProgress >= 100) {
                        extractProgress = 100;
                        currentPhase = 'transform';
                        this.updateETLStatus('Extraction completed. Starting transformation...', 'info');
                    }
                    break;
                case 'transform':
                    transformProgress += 3;
                    if (transformProgress >= 100) {
                        transformProgress = 100;
                        currentPhase = 'load';
                        this.updateETLStatus('Transformation completed. Starting loading...', 'info');
                    }
                    break;
                case 'load':
                    loadProgress += 4;
                    if (loadProgress >= 100) {
                        loadProgress = 100;
                        currentPhase = 'waiting';
                        this.updateETLStatus('Loading completed. Waiting for backend completion...', 'info');
                    }
                    break;
                case 'waiting':
                    // Keep showing 100% while waiting for backend
                    break;
            }
            
            // Calculate overall progress
            overallProgress = Math.round((extractProgress + transformProgress + loadProgress) / 3);
            
            // Update progress display
            this.updateETLProgress(extractProgress, transformProgress, loadProgress, overallProgress);
            
        }, 200); // Slightly slower for better UX
        
        // Poll backend every second for completion detection
        this.pipelineStatusInterval = setInterval(async () => {
            try {
                const response = await fetch('/aasx/api/etl/progress');
                if (response.ok) {
                    const progress = await response.json();
                    
                    if (progress.is_running) {
                        // Backend is still running, reset counters
                        lastBackendUpdate = Date.now();
                        consecutiveNoUpdates = 0;
                        this.updateETLStatus(`Processing: ${progress.current_file || 'Files'}...`, 'info');
                    } else {
                        // Backend is not running, check completion status
                        if (progress.overall_progress >= 100) {
                            // Backend completed successfully
                            backendCompleted = true;
                            console.log('✅ Backend completed successfully with 100% progress');
                        } else {
                            // Backend stopped but not completed, check if it's been 2+ seconds
                            consecutiveNoUpdates++;
                            if (consecutiveNoUpdates >= 2) {
                                backendCompleted = true;
                                console.log('✅ Backend completed after 2+ seconds of no updates');
                            } else {
                                this.updateETLStatus('Backend processing completed. Finalizing...', 'info');
                            }
                        }
                    }
                } else {
                    // HTTP error, count as no update
                    consecutiveNoUpdates++;
                    if (consecutiveNoUpdates >= 2) {
                        backendCompleted = true;
                        console.log('✅ Backend completed after 2+ consecutive errors');
                    }
                }
            } catch (error) {
                console.error('❌ Error polling backend progress:', error);
                consecutiveNoUpdates++;
                if (consecutiveNoUpdates >= 2) {
                    backendCompleted = true;
                    console.log('✅ Backend completed after 2+ consecutive errors');
                }
            }
        }, 1000); // Poll every 1 second
    }

    updateETLStatus(message, type = 'info') {
        const statusElement = document.getElementById('etlStatusText');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = `text-${type === 'error' ? 'danger' : type}`;
            console.log(`📝 Status updated: ${message} (${type})`);
        } else {
            console.error('❌ Status element not found: etlStatusText');
        }
    }

    updateETLProgress(extract, transform, load, overall) {
        console.log('🔄 Updating ETL progress:', { extract, transform, load, overall });
        
        // Update progress circles
        this.updateProgressCircle('extractProgress', extract);
        this.updateProgressCircle('transformProgress', transform);
        this.updateProgressCircle('loadProgress', load);
        this.updateProgressCircle('overallProgress', overall);
        
        // Update progress bar
        const progressBar = document.getElementById('overallProgressBar');
        if (progressBar) {
            progressBar.style.width = `${overall}%`;
            progressBar.setAttribute('aria-valuenow', overall);
            console.log('📊 Progress bar updated to:', overall + '%');
        } else {
            console.error('❌ Progress bar element not found');
        }
    }

    updateProgressCircle(elementId, progress) {
        const element = document.getElementById(elementId);
        if (element) {
            const progressText = element.querySelector('.progress-text');
            if (progressText) {
                progressText.textContent = `${progress}%`;
            }
            // Calculate degrees for conic gradient (360 degrees = 100%)
            const degrees = (progress / 100) * 360;
            element.style.setProperty('--progress', `${degrees}deg`);
            element.setAttribute('data-progress', progress);
            // Directly set the background for compatibility
            element.style.background = `conic-gradient(#007bff 0deg, #007bff ${degrees}deg, #e9ecef ${degrees}deg, #e9ecef 360deg)`;
            console.log(`✅ Updated ${elementId} to ${progress}% (${degrees}deg)`);
        } else {
            console.error(`❌ Progress circle element not found: ${elementId}`);
        }
    }

    stopPipelineStatusPolling() {
        if (this.pipelineStatusInterval) {
            clearInterval(this.pipelineStatusInterval);
            this.pipelineStatusInterval = null;
        }
        
        // Clear any progress simulation interval
        if (this.progressSimulation) {
            clearInterval(this.progressSimulation);
            this.progressSimulation = null;
        }
        
        // Hide the progress section after a longer delay to show completion
        setTimeout(() => {
            $('#etlProgress').hide();
        }, 8000); // Show completion for 8 seconds total
    }

    // Project & File Management Methods
    async onManageProjectChange() {
        const projectId = $('#manageProjectSelect').val();
        const fileSelect = $('#manageFileSelect');
        const fileButtons = $('#viewFileDetails, #deleteFile, #processFile');
        
        if (!projectId) {
            fileSelect.html('<option value="">Choose a file...</option>').prop('disabled', true);
            fileButtons.prop('disabled', true);
            return;
        }
        
        try {
            const response = await fetch(`/aasx/api/projects/${projectId}/files`);
            if (response.ok) {
                const files = await response.json();
                const options = files.map(file => 
                    `<option value="${file.id}">${file.original_filename} (${this.formatFileSize(file.size)})</option>`
                ).join('');
                
                fileSelect.html(`<option value="">Choose a file...</option>${options}`).prop('disabled', false);
            } else {
                console.error('Failed to load project files');
                fileSelect.html('<option value="">No files available</option>').prop('disabled', true);
            }
        } catch (error) {
            console.error('Error loading project files:', error);
            fileSelect.html('<option value="">Error loading files</option>').prop('disabled', true);
        }
    }

    onManageFileChange() {
        const fileId = $('#manageFileSelect').val();
        const fileButtons = $('#viewFileDetails, #deleteFile, #processFile');
        
        if (fileId) {
            fileButtons.prop('disabled', false);
        } else {
            fileButtons.prop('disabled', true);
        }
    }

    async viewSelectedProject() {
        const projectId = $('#manageProjectSelect').val();
        if (!projectId) {
            alert('Please select a project first');
            return;
        }
        
        await this.viewProject(projectId);
    }

    async deleteSelectedProject() {
        const projectId = $('#manageProjectSelect').val();
        if (!projectId) {
            alert('Please select a project first');
            return;
        }
        
        await this.deleteProject(projectId);
        
        // Refresh the project select dropdowns
        this.updateProjectSelects();
        this.updateManageProjectSelect();
    }

    async viewSelectedFile() {
        const projectId = $('#manageProjectSelect').val();
        const fileId = $('#manageFileSelect').val();
        
        if (!projectId || !fileId) {
            alert('Please select both a project and a file');
            return;
        }
        
        try {
            const response = await fetch(`/aasx/api/projects/${projectId}/files/${fileId}`);
            if (response.ok) {
                const file = await response.json();
                this.showFileDetails(file);
            } else {
                alert('Failed to load file details');
            }
        } catch (error) {
            console.error('Error loading file details:', error);
            alert('Error loading file details');
        }
    }

    async deleteSelectedFile() {
        const projectId = $('#manageProjectSelect').val();
        const fileId = $('#manageFileSelect').val();
        
        if (!projectId || !fileId) {
            alert('Please select both a project and a file');
            return;
        }
        
        if (!confirm('Are you sure you want to delete this file? This action cannot be undone.')) {
            return;
        }
        
        await this.deleteFile(projectId, fileId);
        
        // The deleteFile method now handles refreshing all file lists
        // No need to call onManageProjectChange() again
    }

    async processSelectedFile() {
        const projectId = $('#manageProjectSelect').val();
        const fileId = $('#manageFileSelect').val();
        
        if (!projectId || !fileId) {
            alert('Please select both a project and a file');
            return;
        }
        
        await this.processSingleFileFromProject(projectId, fileId);
    }

    showFileDetails(file) {
        const detailsHtml = `
            <div class="row">
                <div class="col-md-6">
                    <h6>File Information</h6>
                    <table class="table table-sm">
                        <tr><td>Filename:</td><td>${file.original_filename}</td></tr>
                        <tr><td>Size:</td><td>${this.formatFileSize(file.size)}</td></tr>
                        <tr><td>Upload Date:</td><td>${new Date(file.upload_date).toLocaleString()}</td></tr>
                        <tr><td>Status:</td><td><span class="badge bg-${this.getStatusBadgeColor(file.status)}">${file.status}</span></td></tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6>Description</h6>
                    <p>${file.description || 'No description provided'}</p>
                </div>
            </div>
            ${file.processing_result ? `
                <hr>
                <h6>Processing Results</h6>
                <pre class="bg-light p-3 rounded">${JSON.stringify(file.processing_result, null, 2)}</pre>
            ` : ''}
        `;
        
        // Create a modal to show file details
        const modalHtml = `
            <div class="modal fade" id="fileDetailsModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-file me-2"></i>File Details
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            ${detailsHtml}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal if any
        $('#fileDetailsModal').remove();
        
        // Add new modal to body and show it
        $('body').append(modalHtml);
        $('#fileDetailsModal').modal('show');
        
        // Clean up modal when hidden
        $('#fileDetailsModal').on('hidden.bs.modal', function() {
            $(this).remove();
        });
    }

    updateManageProjectSelect() {
        const options = this.projects.map(project => 
            `<option value="${project.id}">${project.name}</option>`
        ).join('');
        
        $('#manageProjectSelect').html(`
            <option value="">Choose a project...</option>
            ${options}
        `);
    }

    updateFileStatusInList(filename, status) {
        // Update file status in the ETL files list
        const fileRow = $(`.pipeline-file-checkbox[data-filename="${filename}"]`).closest('.file-item');
        if (fileRow.length > 0) {
            const statusBadge = fileRow.find('.status-badge');
            const statusText = this.getFileStatusInfo(status).text;
            const statusColor = this.getStatusBadgeColor(status);
            
            statusBadge.removeClass().addClass(`badge bg-${statusColor} status-badge`).text(statusText);
            
            // Disable checkbox if processing or completed
            if (status === 'processing' || status === 'completed') {
                fileRow.find('.pipeline-file-checkbox').prop('disabled', true);
            } else {
                fileRow.find('.pipeline-file-checkbox').prop('disabled', false);
            }
        }
    }

    async processSingleFileFromProject(projectId, fileId) {
        try {
            // Get file information
            const filesResponse = await fetch(`/aasx/api/projects/${projectId}/files`);
            if (!filesResponse.ok) {
                throw new Error('Failed to load project files');
            }
            
            const allFiles = await filesResponse.json();
            const fileInfo = allFiles.find(file => file.id === fileId);
            
            if (!fileInfo) {
                throw new Error('File not found');
            }

            const config = this.getETLConfiguration();
            
            // Prepare ETL configuration for single file
            const etlConfig = {
                extract: {
                    hybrid_processing: config.hybrid_processing,
                    enable_validation: config.enable_validation,
                    enable_backup: config.enable_backup
                },
                transform: {
                    enable_quality_checks: config.enable_quality_checks,
                    enable_enrichment: config.enable_enrichment,
                    normalize_ids: config.normalize_ids
                },
                load: {
                    output_formats: config.output_formats,
                    enable_sqlite: config.enable_sqlite,
                    enable_vector_db: config.enable_vector_db,
                    enable_rag_export: config.enable_rag_export,
                    vector_db_type: config.vector_db_type,
                    embedding_model: config.embedding_model,
                    batch_size: config.batch_size,
                    memory_limit: config.memory_limit,
                    quality_threshold: config.quality_threshold,
                    chunk_size: config.chunk_size
                },
                files: [fileInfo.original_filename],
                parallel_processing: false,
                max_workers: 1
            };

            console.log('Processing single file with config:', etlConfig);

            // Update file status to processing
            this.updateFileStatusInList(fileInfo.original_filename, 'processing');

            // Call the ETL pipeline API
            const response = await fetch('/aasx/api/etl/process-file', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(etlConfig)
            });

            if (response.ok) {
                const result = await response.json();
                this.showSuccessMessage(`File ${fileInfo.original_filename} processed successfully!`);
                
                // Update file status to completed
                this.updateFileStatusInList(fileInfo.original_filename, 'completed');
                
                // Show results
                this.showFileProcessingResult(result);
            } else {
                const error = await response.json();
                this.updateFileStatusInList(fileInfo.original_filename, 'error');
                alert('Failed to process file: ' + error.detail);
            }
        } catch (error) {
            console.error('Error processing file:', error);
            alert('Error processing file: ' + error.message);
        }
    }
}

// Global function for launch explorer (called from HTML onclick)
let isLaunchingExplorer = false;

async function launchExplorer(method) {
    // Prevent multiple simultaneous launches
    if (isLaunchingExplorer) {
        console.log('⚠️ Explorer launch already in progress, skipping...');
        return;
    }
    
    isLaunchingExplorer = true;
    console.log(`🚀 Launching AASX Explorer with method: ${method}`);
    
    try {
        switch (method) {
            case 'direct':
                await launchExplorerDirect();
                break;
            case 'script':
                await downloadLauncherScript();
                break;
            case 'manual':
                showManualInstructions();
                break;
            default:
                console.error('Unknown launch method:', method);
        }
    } finally {
        isLaunchingExplorer = false;
    }
}

async function launchExplorerDirect() {
    try {
        // Call the backend API to launch the explorer
        const response = await fetch('/aasx/api/explorer/launch', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            const result = await response.json();
            showAlert(`✅ ${result.message}`, 'success', 3000);
            
            // Close the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('launchExplorerModal'));
            if (modal) {
                modal.hide();
            }
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to launch explorer');
        }
    } catch (error) {
        console.error('Error launching explorer:', error);
        showAlert(`❌ Launch failed: ${error.message}`, 'danger', 5000);
        
        // Fallback to instructions if API fails
        const fallbackInstructions = `
🚀 Launch Instructions:
1. Open terminal in project directory
2. Run: \`python scripts/launch_explorer.py\`
3. Or manually open: ./AasxPackageExplorer/AasxPackageExplorer.exe
        `;
        
        showAlert(fallbackInstructions, 'info', 8000);
    }
}

async function downloadLauncherScript() {
    try {
        // Call the backend API to download the script
        const response = await fetch('/aasx/api/explorer/launch-script', {
            method: 'GET',
        });
        
        if (response.ok) {
            // Get the blob from the response
            const blob = await response.blob();
            
            // Create a download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'launch_explorer.py';
            
            // Trigger the download
            document.body.appendChild(a);
            a.click();
            
            // Clean up
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showAlert('✅ Script downloaded!', 'success', 3000);
            
            // Close the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('launchExplorerModal'));
            if (modal) {
                modal.hide();
            }
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to download script');
        }
    } catch (error) {
        console.error('Error downloading script:', error);
        showAlert(`❌ Download failed: ${error.message}`, 'danger', 5000);
        
        // Fallback to information about the existing script
        const fallbackInfo = `
📥 Script Location: \`scripts/launch_explorer.py\`
💡 Use existing script: \`python scripts/launch_explorer.py\`
        `;
        
        showAlert(fallbackInfo, 'info', 6000);
    }
}

function showManualInstructions() {
    // Show manual instructions in a new modal or alert
    const instructions = `
🚀 Manual Launch Instructions:

**Quick Launch:**
1. Open terminal in project directory
2. Run: \`python scripts/launch_explorer.py\`

**Manual Launch:**
1. Navigate to AasxPackageExplorer folder
2. Double-click AasxPackageExplorer.exe

📁 Location: ./AasxPackageExplorer/AasxPackageExplorer.exe

💡 The launcher script provides automatic detection and error handling.
    `;
    
    showAlert(instructions, 'info', 8000);
}

function showAlert(message, type = 'info', timeout = 5000) {
    // Create a Bootstrap alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Insert at the top of the page
    const container = document.querySelector('.container-fluid');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
    }
    
    // Auto-dismiss after specified timeout (default 5 seconds)
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, timeout);
}

// Initialize the AASX ETL Pipeline when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔍 AASX template scripts block loaded');
    
    // Prevent multiple initializations
    if (window.aasxETLPipeline || window.projectManager) {
        console.log('⚠️ Components already initialized, skipping...');
        return;
    }
    
    // Test if aasx_etl.js loads
    console.log('🔍 Testing if aasx_etl.js loads...');
    
    // Initialize the pipeline
    window.aasxETLPipeline = new AASXETLPipeline();
    
    console.log('🔍 After aasx_etl.js load attempt');
    
    // Check if class was created successfully
    if (window.aasxETLPipeline) {
        console.log('✅ AASXETLPipeline class initialized successfully');
    } else {
        console.log('❌ AASXETLPipeline class not found');
    }
    
    // Initialize Project Manager
    console.log('🔍 Initializing Project Manager...');
    window.projectManager = new ProjectManager();
    
    if (window.projectManager) {
        console.log('✅ ProjectManager class initialized successfully');
        // Initialize and load projects
        window.projectManager.init().then(() => {
            console.log('✅ ProjectManager initialized and projects loaded');
        }).catch(error => {
            console.error('❌ Error initializing ProjectManager:', error);
        });
    } else {
        console.log('❌ ProjectManager class not found');
    }
});