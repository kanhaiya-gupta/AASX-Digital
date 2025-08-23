/**
 * Use Cases Manager
 * Handles predefined use cases and templates for common physics simulations
 */

export class UseCaseManager {
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
    }

    handleAuthStateChange() {
        if (this.isAuthenticated) {
            this.loadUserUseCases();
        } else {
            this.loadDemoUseCases();
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
        
        console.log('🔐 Initializing Use Case Manager...');
        
        try {
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            await this.loadUseCases();
            await this.loadUseCaseTemplates();
            
            this.isInitialized = true;
            console.log('✅ Use Case Manager initialized');
        } catch (error) {
            console.error('❌ Use Case Manager initialization failed:', error);
            throw error;
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
            }
        } catch (error) {
            console.error('❌ Failed to load use case templates:', error);
        }
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
                return result;
            } else {
                throw new Error('Failed to load use case');
            }
        } catch (error) {
            console.error('❌ Failed to load use case:', error);
            throw error;
        }
    }

    async getUseCaseDetails(useCaseId) {
        try {
            const response = await fetch(`/api/physics-modeling/use-cases/${useCaseId}/details`, {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('❌ Failed to get use case details:', error);
        }
        return null;
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
                return result;
            } else {
                throw new Error('Failed to clone use case');
            }
        } catch (error) {
            console.error('❌ Failed to clone use case:', error);
            throw error;
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
                return result;
            } else {
                throw new Error('Failed to apply template');
            }
        } catch (error) {
            console.error('❌ Failed to apply template:', error);
            throw error;
        }
    }

    async createUseCase(useCaseData) {
        try {
            const response = await fetch('/api/physics-modeling/use-cases/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeaders()
                },
                body: JSON.stringify(useCaseData)
            });

            if (response.ok) {
                const result = await response.json();
                this.availableUseCases.push(result.useCase);
                return result.useCase;
            } else {
                throw new Error('Failed to create use case');
            }
        } catch (error) {
            console.error('❌ Failed to create use case:', error);
            throw error;
        }
    }

    async updateUseCase(useCaseId, updateData) {
        try {
            const response = await fetch(`/api/physics-modeling/use-cases/${useCaseId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeaders()
                },
                body: JSON.stringify(updateData)
            });

            if (response.ok) {
                const result = await response.json();
                // Update local use case
                const index = this.availableUseCases.findIndex(uc => uc.id === useCaseId);
                if (index !== -1) {
                    this.availableUseCases[index] = result.useCase;
                }
                return result.useCase;
            } else {
                throw new Error('Failed to update use case');
            }
        } catch (error) {
            console.error('❌ Failed to update use case:', error);
            throw error;
        }
    }

    async deleteUseCase(useCaseId) {
        try {
            const response = await fetch(`/api/physics-modeling/use-cases/${useCaseId}`, {
                method: 'DELETE',
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                // Remove from local list
                this.availableUseCases = this.availableUseCases.filter(uc => uc.id !== useCaseId);
                return true;
            } else {
                throw new Error('Failed to delete use case');
            }
        } catch (error) {
            console.error('❌ Failed to delete use case:', error);
            throw error;
        }
    }

    async loadUserUseCases() {
        try {
            const response = await fetch('/api/physics-modeling/use-cases/user', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                this.availableUseCases = data.useCases || [];
            }
        } catch (error) {
            console.error('❌ Failed to load user use cases:', error);
        }
    }

    async loadDemoUseCases() {
        try {
            const response = await fetch('/api/physics-modeling/use-cases/demo');
            
            if (response.ok) {
                const data = await response.json();
                this.availableUseCases = data.useCases || [];
                this.useCaseTemplates = data.templates || [];
            }
        } catch (error) {
            console.error('❌ Failed to load demo use cases:', error);
        }
    }

    getUseCasesByCategory(category) {
        if (!category) return this.availableUseCases;
        return this.availableUseCases.filter(useCase => useCase.category === category);
    }

    searchUseCases(query) {
        const searchTerm = query.toLowerCase();
        return this.availableUseCases.filter(useCase => 
            useCase.name.toLowerCase().includes(searchTerm) ||
            useCase.description.toLowerCase().includes(searchTerm)
        );
    }

    getUseCaseById(useCaseId) {
        return this.availableUseCases.find(useCase => useCase.id === useCaseId);
    }

    getTemplatesByCategory(category) {
        if (!category) return this.useCaseTemplates;
        return this.useCaseTemplates.filter(template => template.category === category);
    }

    async refreshUseCases() {
        try {
            await Promise.all([
                this.loadUseCases(),
                this.loadUseCaseTemplates()
            ]);
            console.log('✅ Use cases refreshed');
        } catch (error) {
            console.error('❌ Failed to refresh use cases:', error);
        }
    }

    async cleanup() {
        console.log('🧹 Cleaning up Use Case Manager...');
        this.clearSensitiveData();
        this.isInitialized = false;
        console.log('✅ Use Case Manager cleaned up');
    }
}
