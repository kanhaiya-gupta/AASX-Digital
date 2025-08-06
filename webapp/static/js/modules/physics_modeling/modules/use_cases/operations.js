/**
 * Use Cases Operations
 * Handles business logic for physics modeling use cases
 */

import PhysicsModelingAPI from '../../shared/api.js';
import PhysicsModelingUtils from '../../shared/utils.js';

class UseCaseOperations {
    constructor() {
        this.api = new PhysicsModelingAPI();
        this.utils = new PhysicsModelingUtils();
    }

    /**
     * Load all use cases from the database
     */
    async loadUseCases(category = null) {
        try {
            const useCases = await this.api.getUseCases(category);
            return {
                success: true,
                data: useCases,
                message: 'Use cases loaded successfully'
            };
        } catch (error) {
            console.error('Error loading use cases:', error);
            return {
                success: false,
                error: error.message,
                message: 'Failed to load use cases'
            };
        }
    }

    /**
     * Get specific use case by ID
     */
    async getUseCase(useCaseId) {
        try {
            const useCase = await this.api.getUseCase(useCaseId);
            return {
                success: true,
                data: useCase,
                message: 'Use case loaded successfully'
            };
        } catch (error) {
            console.error('Error loading use case:', error);
            return {
                success: false,
                error: error.message,
                message: 'Failed to load use case'
            };
        }
    }

    /**
     * Get use case templates
     */
    async getUseCaseTemplates(category = null) {
        try {
            const templates = await this.api.getUseCaseTemplates(category);
            return {
                success: true,
                data: templates,
                message: 'Use case templates loaded successfully'
            };
        } catch (error) {
            console.error('Error loading use case templates:', error);
            return {
                success: false,
                error: error.message,
                message: 'Failed to load use case templates'
            };
        }
    }

    /**
     * Get use case statistics
     */
    async getUseCaseStatistics() {
        try {
            const statistics = await this.api.getUseCaseStatistics();
            return {
                success: true,
                data: statistics,
                message: 'Use case statistics loaded successfully'
            };
        } catch (error) {
            console.error('Error loading use case statistics:', error);
            return {
                success: false,
                error: error.message,
                message: 'Failed to load use case statistics'
            };
        }
    }

    /**
     * Get famous examples
     */
    async getFamousExamples() {
        try {
            const examples = await this.api.getFamousExamples();
            return {
                success: true,
                data: examples,
                message: 'Famous examples loaded successfully'
            };
        } catch (error) {
            console.error('Error loading famous examples:', error);
            return {
                success: false,
                error: error.message,
                message: 'Failed to load famous examples'
            };
        }
    }

    /**
     * Get optimization targets
     */
    async getOptimizationTargets() {
        try {
            const targets = await this.api.getOptimizationTargets();
            return {
                success: true,
                data: targets,
                message: 'Optimization targets loaded successfully'
            };
        } catch (error) {
            console.error('Error loading optimization targets:', error);
            return {
                success: false,
                error: error.message,
                message: 'Failed to load optimization targets'
            };
        }
    }

    /**
     * Create model from use case
     */
    async createModelFromUseCase(useCaseId, twinId, customParameters = {}) {
        try {
            const result = await this.api.createModelFromUseCase(useCaseId, {
                twin_id: twinId,
                custom_parameters: customParameters
            });
            return {
                success: true,
                data: result,
                message: 'Model created from use case successfully'
            };
        } catch (error) {
            console.error('Error creating model from use case:', error);
            return {
                success: false,
                error: error.message,
                message: 'Failed to create model from use case'
            };
        }
    }

    /**
     * Get icon for use case category
     */
    getUseCaseIcon(category) {
        const iconMap = {
            'thermal': 'fas fa-fire',
            'structural': 'fas fa-cog',
            'fluid': 'fas fa-wind',
            'electromagnetic': 'fas fa-bolt',
            'multi_physics': 'fas fa-layer-group',
            'default': 'fas fa-lightbulb'
        };
        return iconMap[category] || iconMap.default;
    }

    /**
     * Get color for use case category
     */
    getUseCaseColor(category) {
        const colorMap = {
            'thermal': 'text-warning',
            'structural': 'text-info',
            'fluid': 'text-success',
            'electromagnetic': 'text-danger',
            'multi_physics': 'text-primary',
            'default': 'text-secondary'
        };
        return colorMap[category] || colorMap.default;
    }

    /**
     * Filter use cases by category
     */
    filterUseCasesByCategory(useCases, category) {
        if (!category || category === 'all') {
            return useCases;
        }
        return useCases.filter(useCase => 
            useCase.category === category || useCase.model_type === category
        );
    }

    /**
     * Search use cases by name or description
     */
    searchUseCases(useCases, searchTerm) {
        if (!searchTerm) {
            return useCases;
        }
        const term = searchTerm.toLowerCase();
        return useCases.filter(useCase => 
            useCase.name.toLowerCase().includes(term) ||
            (useCase.description && useCase.description.toLowerCase().includes(term)) ||
            (useCase.examples && useCase.examples.some(example => 
                example.toLowerCase().includes(term)
            ))
        );
    }
}

export default UseCaseOperations; 