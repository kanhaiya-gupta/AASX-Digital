/**
 * Use Cases UI Component
 * Handles predefined use cases and templates for common physics simulations
 */

export class UseCasesUIComponent {
    constructor() {
        // Authentication properties
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
        
        this.isInitialized = false;
        this.availableUseCases = [];
        this.useCaseTemplates = [];
        this.useCaseCategories = [
            'fluid-dynamics',
            'structural-analysis',
            'thermal-analysis',
            'electromagnetic',
            'quantum-mechanics',
            'particle-physics'
        ];
        
        // UI elements
        this.elements = {
            useCasesContainer: null,
            useCasesList: null,
            templateGallery: null,
            categoryFilter: null,
            searchInput: null,
            detailsPanel: null
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
            this.loadUserUseCases();
            this.enableAuthenticatedFeatures();
        } else {
            this.loadDemoUseCases();
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
        
        console.log('🔐 Initializing Use Cases UI Component...');
        
        try {
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            this.initializeUI();
            this.setupEventListeners();
            await this.loadUseCases();
            await this.loadUseCaseTemplates();
            
            this.isInitialized = true;
            console.log('✅ Use Cases UI Component initialized');
        } catch (error) {
            console.error('❌ Use Cases UI Component initialization failed:', error);
            throw error;
        }
    }

    initializeUI() {
        // Initialize UI elements
        this.elements.useCasesContainer = document.getElementById('use-cases-container');
        this.elements.useCasesList = document.getElementById('use-cases-list');
        this.elements.templateGallery = document.getElementById('template-gallery');
        this.elements.categoryFilter = document.getElementById('use-case-category-filter');
        this.elements.searchInput = document.getElementById('use-case-search');
        this.elements.detailsPanel = document.getElementById('use-case-details');

        if (!this.elements.useCasesContainer) {
            console.warn('⚠️ Use cases container not found');
            return;
        }

        // Initialize category filter
        this.initializeCategoryFilter();
    }

    initializeCategoryFilter() {
        if (!this.elements.categoryFilter) return;

        const filterHtml = `
            <option value="">All Categories</option>
            ${this.useCaseCategories.map(category => 
                `<option value="${category}">${category.replace('-', ' ').toUpperCase()}</option>`
            ).join('')}
        `;

        this.elements.categoryFilter.innerHTML = filterHtml;
    }

    setupEventListeners() {
        // Category filter change
        if (this.elements.categoryFilter) {
            this.elements.categoryFilter.addEventListener('change', (e) => {
                this.filterUseCasesByCategory(e.target.value);
            });
        }

        // Search functionality
        if (this.elements.searchInput) {
            this.elements.searchInput.addEventListener('input', (e) => {
                this.searchUseCases(e.target.value);
            });
        }

        // Refresh button
        const refreshBtn = document.getElementById('refresh-use-cases');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshUseCases());
        }
    }

    async loadUseCases() {
        try {
            const response = await fetch('/api/physics-modeling/use-cases', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                this.availableUseCases = data.useCases || [];
                this.displayUseCases();
            }
        } catch (error) {
            console.error('❌ Failed to load use cases:', error);
        }
    }

    async loadUseCaseTemplates() {
        try {
            const response = await fetch('/api/physics-modeling/use-cases/templates', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                this.useCaseTemplates = data.templates || [];
                this.displayTemplates();
            }
        } catch (error) {
            console.error('❌ Failed to load use case templates:', error);
        }
    }

    displayUseCases() {
        if (!this.elements.useCasesList) return;

        const useCasesHtml = this.availableUseCases.map(useCase => `
            <div class="use-case-item" data-category="${useCase.category}" data-id="${useCase.id}">
                <div class="use-case-header">
                    <h5 class="use-case-name">${useCase.name}</h5>
                    <span class="use-case-category">${useCase.category}</span>
                    <span class="use-case-difficulty ${useCase.difficulty}">${useCase.difficulty}</span>
                </div>
                <div class="use-case-description">${useCase.description}</div>
                <div class="use-case-meta">
                    <span class="use-case-author">By: ${useCase.author}</span>
                    <span class="use-case-rating">⭐ ${useCase.rating}/5</span>
                    <span class="use-case-downloads">${useCase.downloads} downloads</span>
                </div>
                <div class="use-case-actions">
                    <button onclick="loadUseCase('${useCase.id}')" class="btn btn-sm btn-primary">Load</button>
                    <button onclick="viewUseCaseDetails('${useCase.id}')" class="btn btn-sm btn-secondary">Details</button>
                    <button onclick="cloneUseCase('${useCase.id}')" class="btn btn-sm btn-success">Clone</button>
                </div>
            </div>
        `).join('');

        this.elements.useCasesList.innerHTML = useCasesHtml;
    }

    displayTemplates() {
        if (!this.elements.templateGallery) return;

        const templatesHtml = this.useCaseTemplates.map(template => `
            <div class="template-item" data-category="${template.category}">
                <div class="template-preview">
                    <img src="${template.previewImage || '/static/images/template-placeholder.png'}" alt="${template.name}" />
                </div>
                <div class="template-info">
                    <h6 class="template-name">${template.name}</h6>
                    <p class="template-description">${template.description}</p>
                    <div class="template-meta">
                        <span class="template-category">${template.category}</span>
                        <span class="template-version">v${template.version}</span>
                    </div>
                </div>
                <div class="template-actions">
                    <button onclick="useTemplate('${template.id}')" class="btn btn-sm btn-primary">Use Template</button>
                    <button onclick="previewTemplate('${template.id}')" class="btn btn-sm btn-secondary">Preview</button>
                </div>
            </div>
        `).join('');

        this.elements.templateGallery.innerHTML = templatesHtml;
    }

    async loadUseCase(useCaseId) {
        try {
            const response = await fetch(`/api/physics-modeling/use-cases/${useCaseId}/load`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const result = await response.json();
                console.log('✅ Use case loaded successfully:', result);
                
                // Emit event for other components to handle
                window.dispatchEvent(new CustomEvent('useCaseLoaded', {
                    detail: { useCase: result }
                }));
                
                // Show success message
                this.showMessage('Use case loaded successfully', 'success');
            } else {
                throw new Error('Failed to load use case');
            }
        } catch (error) {
            console.error('❌ Failed to load use case:', error);
            this.showMessage('Failed to load use case', 'error');
        }
    }

    async viewUseCaseDetails(useCaseId) {
        try {
            const response = await fetch(`/api/physics-modeling/use-cases/${useCaseId}/details`, {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const useCase = await response.json();
                this.displayUseCaseDetails(useCase);
            }
        } catch (error) {
            console.error('❌ Failed to load use case details:', error);
        }
    }

    displayUseCaseDetails(useCase) {
        if (!this.elements.detailsPanel) return;

        const detailsHtml = `
            <div class="use-case-details">
                <div class="details-header">
                    <h4>${useCase.name}</h4>
                    <button onclick="closeUseCaseDetails()" class="btn btn-sm btn-secondary">Close</button>
                </div>
                <div class="details-content">
                    <div class="detail-section">
                        <h5>Description</h5>
                        <p>${useCase.description}</p>
                    </div>
                    <div class="detail-section">
                        <h5>Parameters</h5>
                        <div class="parameters-list">
                            ${Object.entries(useCase.parameters || {}).map(([key, value]) => `
                                <div class="parameter-item">
                                    <span class="parameter-name">${key}:</span>
                                    <span class="parameter-value">${value}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    <div class="detail-section">
                        <h5>Requirements</h5>
                        <ul>
                            <li><strong>Physics Engine:</strong> ${useCase.requirements?.physicsEngine || 'Standard'}</li>
                            <li><strong>Memory:</strong> ${useCase.requirements?.memory || '1GB'}</li>
                            <li><strong>Plugins:</strong> ${(useCase.requirements?.plugins || []).join(', ') || 'None'}</li>
                        </ul>
                    </div>
                    <div class="detail-section">
                        <h5>Examples</h5>
                        <div class="examples-gallery">
                            ${(useCase.examples || []).map(example => `
                                <div class="example-item">
                                    <img src="${example.image}" alt="${example.title}" />
                                    <span class="example-title">${example.title}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
                <div class="details-actions">
                    <button onclick="loadUseCase('${useCase.id}')" class="btn btn-primary">Load Use Case</button>
                    <button onclick="cloneUseCase('${useCase.id}')" class="btn btn-success">Clone</button>
                    <button onclick="shareUseCase('${useCase.id}')" class="btn btn-info">Share</button>
                </div>
            </div>
        `;

        this.elements.detailsPanel.innerHTML = detailsHtml;
    }

    async cloneUseCase(useCaseId) {
        try {
            const response = await fetch(`/api/physics-modeling/use-cases/${useCaseId}/clone`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const result = await response.json();
                console.log('✅ Use case cloned successfully:', result);
                this.showMessage('Use case cloned successfully', 'success');
                
                // Refresh the use cases list
                await this.loadUseCases();
            } else {
                throw new Error('Failed to clone use case');
            }
        } catch (error) {
            console.error('❌ Failed to clone use case:', error);
            this.showMessage('Failed to clone use case', 'error');
        }
    }

    async useTemplate(templateId) {
        try {
            const response = await fetch(`/api/physics-modeling/use-cases/templates/${templateId}/use`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const result = await response.json();
                console.log('✅ Template applied successfully:', result);
                this.showMessage('Template applied successfully', 'success');
                
                // Emit event for other components to handle
                window.dispatchEvent(new CustomEvent('templateApplied', {
                    detail: { template: result }
                }));
            } else {
                throw new Error('Failed to apply template');
            }
        } catch (error) {
            console.error('❌ Failed to apply template:', error);
            this.showMessage('Failed to apply template', 'error');
        }
    }

    filterUseCasesByCategory(category) {
        const useCaseItems = document.querySelectorAll('.use-case-item');
        const templateItems = document.querySelectorAll('.template-item');
        
        useCaseItems.forEach(item => {
            const itemCategory = item.getAttribute('data-category');
            if (!category || itemCategory === category) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
        
        templateItems.forEach(item => {
            const itemCategory = item.getAttribute('data-category');
            if (!category || itemCategory === category) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }

    searchUseCases(query) {
        const searchTerm = query.toLowerCase();
        const useCaseItems = document.querySelectorAll('.use-case-item');
        const templateItems = document.querySelectorAll('.template-item');
        
        useCaseItems.forEach(item => {
            const useCaseName = item.querySelector('.use-case-name').textContent.toLowerCase();
            const useCaseDescription = item.querySelector('.use-case-description').textContent.toLowerCase();
            
            if (useCaseName.includes(searchTerm) || useCaseDescription.includes(searchTerm)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
        
        templateItems.forEach(item => {
            const templateName = item.querySelector('.template-name').textContent.toLowerCase();
            const templateDescription = item.querySelector('.template-description').textContent.toLowerCase();
            
            if (templateName.includes(searchTerm) || templateDescription.includes(searchTerm)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }

    async refreshUseCases() {
        try {
            await Promise.all([
                this.loadUseCases(),
                this.loadUseCaseTemplates()
            ]);
            console.log('✅ Use cases refreshed');
            this.showMessage('Use cases refreshed successfully', 'success');
        } catch (error) {
            console.error('❌ Failed to refresh use cases:', error);
            this.showMessage('Failed to refresh use cases', 'error');
        }
    }

    async loadUserUseCases() {
        await Promise.all([
            this.loadUseCases(),
            this.loadUseCaseTemplates()
        ]);
    }

    async loadDemoUseCases() {
        try {
            const response = await fetch('/api/physics-modeling/use-cases/demo');
            
            if (response.ok) {
                const data = await response.json();
                this.availableUseCases = data.useCases || [];
                this.useCaseTemplates = data.templates || [];
                this.displayUseCases();
                this.displayTemplates();
            }
        } catch (error) {
            console.error('❌ Failed to load demo use cases:', error);
        }
    }

    showMessage(message, type = 'info') {
        // Create a simple message display
        const messageDiv = document.createElement('div');
        messageDiv.className = `alert alert-${type} alert-dismissible fade show`;
        messageDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at the top of the container
        if (this.elements.useCasesContainer) {
            this.elements.useCasesContainer.insertBefore(messageDiv, this.elements.useCasesContainer.firstChild);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.remove();
                }
            }, 5000);
        }
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
        console.log('🧹 Cleaning up Use Cases UI Component...');
        
        // Remove event listeners
        this.eventListeners.forEach(({ event, handler }) => {
            window.removeEventListener(event, handler);
        });
        
        // Clear sensitive data
        this.clearSensitiveData();
        
        this.isInitialized = false;
        console.log('✅ Use Cases UI Component cleaned up');
    }

    async refresh() {
        if (this.isAuthenticated) {
            await this.loadUserUseCases();
        } else {
            await this.loadDemoUseCases();
        }
    }
}
