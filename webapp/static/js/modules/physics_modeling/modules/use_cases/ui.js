/**
 * Use Cases UI
 * Handles UI interactions for physics modeling use cases
 */

import UseCaseOperations from './operations.js';
import PhysicsModelingUtils from '../../shared/utils.js';

class UseCaseUI {
    constructor() {
        this.ops = new UseCaseOperations();
        this.utils = new PhysicsModelingUtils();
        this.currentUseCases = [];
        this.currentFilters = {
            category: 'all',
            searchTerm: ''
        };
    }

    /**
     * Initialize use cases UI
     */
    async init() {
        console.log('Initializing Use Cases UI...');
        
        try {
            // Load initial use cases
            await this.loadUseCases();
            
            // Setup event listeners
            this.setupEventListeners();
            
            console.log('Use Cases UI initialized successfully');
        } catch (error) {
            console.error('Error initializing Use Cases UI:', error);
            this.utils.handleError(error, 'UseCaseUI.init');
        }
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Category filter
        const categoryFilter = document.getElementById('use-case-category-filter');
        if (categoryFilter) {
            categoryFilter.addEventListener('change', (event) => {
                this.currentFilters.category = event.target.value;
                this.applyFilters();
            });
        }

        // Search filter
        const searchFilter = document.getElementById('use-case-search-filter');
        if (searchFilter) {
            searchFilter.addEventListener('input', this.utils.debounce((event) => {
                this.currentFilters.searchTerm = event.target.value;
                this.applyFilters();
            }, 300));
        }

        // Refresh button
        const refreshBtn = document.getElementById('use-cases-refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadUseCases();
            });
        }
    }

    /**
     * Load use cases from database
     */
    async loadUseCases() {
        try {
            this.showLoadingState();
            
            const result = await this.ops.loadUseCases();
            
            if (result.success) {
                this.currentUseCases = result.data || [];
                this.renderUseCases(this.currentUseCases);
                this.updateStatistics();
            } else {
                this.renderErrorState(result.message);
            }
        } catch (error) {
            console.error('Error loading use cases:', error);
            this.renderErrorState('Failed to load use cases');
        }
    }

    /**
     * Show loading state
     */
    showLoadingState() {
        const container = document.getElementById('use-cases-container');
        if (!container) return;

        container.innerHTML = `
            <div class="text-center text-muted">
                <i class="fas fa-spinner fa-spin fa-2x mb-3"></i>
                <p>Loading use cases...</p>
            </div>
        `;
    }

    /**
     * Render use cases in the UI
     */
    renderUseCases(useCases) {
        const container = document.getElementById('use-cases-container');
        if (!container) return;

        if (!useCases || useCases.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i class="fas fa-info-circle fa-2x mb-3"></i>
                    <p>No use cases available</p>
                    <button class="btn btn-outline-primary btn-sm" onclick="window.UseCaseUI.loadUseCases()">
                        <i class="fas fa-refresh me-2"></i>Refresh
                    </button>
                </div>
            `;
            return;
        }

        const useCasesHTML = useCases.map(useCase => {
            const icon = this.ops.getUseCaseIcon(useCase.category || useCase.model_type);
            const color = this.ops.getUseCaseColor(useCase.category || useCase.model_type);
            
            return `
                <div class="col-md-4 mb-3">
                    <div class="card card-hover h-100">
                        <div class="card-body text-center">
                            <i class="${icon} fa-3x ${color} mb-3"></i>
                            <h6>${useCase.name}</h6>
                            <p class="text-muted small">${useCase.description || 'No description available'}</p>
                            ${useCase.examples && useCase.examples.length > 0 ? 
                                `<p class="text-muted small"><strong>Examples:</strong> ${useCase.examples.join(', ')}</p>` : 
                                ''
                            }
                            <div class="mt-3">
                                <button class="btn btn-outline-primary btn-sm me-2" onclick="exploreUseCase('${useCase.id}')">
                                    <i class="fas fa-search me-1"></i>Explore
                                </button>
                                <button class="btn btn-outline-secondary btn-sm" onclick="window.UseCaseUI.showUseCaseDetails('${useCase.id}')">
                                    <i class="fas fa-info-circle me-1"></i>Details
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = `
            <div class="row">
                ${useCasesHTML}
            </div>
        `;
    }

    /**
     * Render error state
     */
    renderErrorState(message) {
        const container = document.getElementById('use-cases-container');
        if (!container) return;

        container.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
                <div class="mt-2">
                    <button class="btn btn-outline-danger btn-sm" onclick="window.UseCaseUI.loadUseCases()">
                        <i class="fas fa-refresh me-2"></i>Try Again
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Apply filters to use cases
     */
    applyFilters() {
        let filteredUseCases = [...this.currentUseCases];

        // Apply category filter
        if (this.currentFilters.category && this.currentFilters.category !== 'all') {
            filteredUseCases = this.ops.filterUseCasesByCategory(filteredUseCases, this.currentFilters.category);
        }

        // Apply search filter
        if (this.currentFilters.searchTerm) {
            filteredUseCases = this.ops.searchUseCases(filteredUseCases, this.currentFilters.searchTerm);
        }

        this.renderUseCases(filteredUseCases);
        this.updateFilterInfo(filteredUseCases.length);
    }

    /**
     * Update filter information
     */
    updateFilterInfo(filteredCount) {
        const filterInfo = document.getElementById('use-cases-filter-info');
        if (filterInfo) {
            filterInfo.textContent = `Showing ${filteredCount} of ${this.currentUseCases.length} use cases`;
        }
    }

    /**
     * Update statistics
     */
    async updateStatistics() {
        try {
            const statsResult = await this.ops.getUseCaseStatistics();
            if (statsResult.success) {
                this.renderStatistics(statsResult.data);
            }
        } catch (error) {
            console.error('Error updating statistics:', error);
        }
    }

    /**
     * Render statistics
     */
    renderStatistics(stats) {
        const statsContainer = document.getElementById('use-cases-statistics');
        if (!statsContainer || !stats) return;

        statsContainer.innerHTML = `
            <div class="row text-center">
                <div class="col-md-3">
                    <div class="card bg-primary text-white">
                        <div class="card-body">
                            <h4>${stats.total_use_cases || 0}</h4>
                            <small>Total Use Cases</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-success text-white">
                        <div class="card-body">
                            <h4>${stats.active_use_cases || 0}</h4>
                            <small>Active Use Cases</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-info text-white">
                        <div class="card-body">
                            <h4>${stats.categories || 0}</h4>
                            <small>Categories</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-warning text-white">
                        <div class="card-body">
                            <h4>${stats.models_created || 0}</h4>
                            <small>Models Created</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Show use case details modal
     */
    async showUseCaseDetails(useCaseId) {
        try {
            const result = await this.ops.getUseCase(useCaseId);
            
            if (result.success) {
                const useCase = result.data;
                this.renderUseCaseDetailsModal(useCase);
            } else {
                this.utils.showError('Failed to load use case details');
            }
        } catch (error) {
            this.utils.handleError(error, 'showUseCaseDetails');
        }
    }

    /**
     * Render use case details modal
     */
    renderUseCaseDetailsModal(useCase) {
        const modal = new bootstrap.Modal(document.getElementById('useCaseDetailsModal'));
        const content = document.getElementById('useCaseDetailsContent');
        
        const icon = this.ops.getUseCaseIcon(useCase.category || useCase.model_type);
        const color = this.ops.getUseCaseColor(useCase.category || useCase.model_type);
        
        content.innerHTML = `
            <div class="text-center mb-3">
                <i class="${icon} fa-4x ${color}"></i>
                <h4 class="mt-2">${useCase.name}</h4>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <h6>Basic Information</h6>
                    <table class="table table-sm">
                        <tr><td>Category:</td><td>${useCase.category || 'N/A'}</td></tr>
                        <tr><td>Model Type:</td><td>${useCase.model_type || 'N/A'}</td></tr>
                        <tr><td>Created:</td><td>${useCase.created_at || 'N/A'}</td></tr>
                        <tr><td>Updated:</td><td>${useCase.updated_at || 'N/A'}</td></tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6>Description</h6>
                    <p class="text-muted">${useCase.description || 'No description available'}</p>
                    
                    ${useCase.examples && useCase.examples.length > 0 ? `
                        <h6>Examples</h6>
                        <ul class="list-unstyled">
                            ${useCase.examples.map(example => `<li><i class="fas fa-check text-success me-2"></i>${example}</li>`).join('')}
                        </ul>
                    ` : ''}
                </div>
            </div>
            
            ${useCase.parameters ? `
                <div class="mt-3">
                    <h6>Default Parameters</h6>
                    <pre class="bg-light p-2 rounded">${JSON.stringify(useCase.parameters, null, 2)}</pre>
                </div>
            ` : ''}
            
            <div class="text-center mt-3">
                <button class="btn btn-primary" onclick="exploreUseCase('${useCase.id}')">
                    <i class="fas fa-play me-2"></i>Use This Template
                </button>
            </div>
        `;
        
        modal.show();
    }

    /**
     * Create model from use case
     */
    async createModelFromUseCase(useCaseId, twinId, customParameters = {}) {
        try {
            this.utils.showProgress('Creating model from use case...');
            
            const result = await this.ops.createModelFromUseCase(useCaseId, twinId, customParameters);
            
            this.utils.hideProgress();
            
            if (result.success) {
                this.utils.showSuccess('Model created successfully from use case!');
                return result.data;
            } else {
                this.utils.showError(result.message);
                return null;
            }
        } catch (error) {
            this.utils.hideProgress();
            this.utils.handleError(error, 'createModelFromUseCase');
            return null;
        }
    }

    /**
     * Refresh use cases
     */
    async refresh() {
        await this.loadUseCases();
        this.utils.showSuccess('Use cases refreshed successfully!');
    }
}

// Make it globally accessible
window.UseCaseUI = UseCaseUI;

export default UseCaseUI; 