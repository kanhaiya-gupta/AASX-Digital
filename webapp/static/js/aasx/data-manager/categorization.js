/**
 * Project Categorization Module
 * Handles project categorization by physics type and use cases
 */

export class ProjectCategorizer {
    constructor() {
        this.categoryConfigs = {
            'thermal': { 
                name: 'Thermal Analysis', 
                icon: 'fas fa-fire', 
                color: 'text-danger', 
                description: 'Heat transfer, thermal management, and temperature analysis for electronics, engines, and industrial processes',
                examples: 'CPU cooling, battery thermal management, solar panels, aerospace thermal protection'
            },
            'structural': { 
                name: 'Structural Analysis', 
                icon: 'fas fa-cube', 
                color: 'text-warning', 
                description: 'Stress analysis, deformation, and structural integrity for mechanical components and systems',
                examples: 'Bridge design, aircraft wings, pressure vessels, automotive chassis'
            },
            'fluid_dynamics': { 
                name: 'Fluid Dynamics Analysis', 
                icon: 'fas fa-water', 
                color: 'text-info', 
                description: 'Fluid flow, aerodynamics, and hydrodynamic analysis for optimal performance',
                examples: 'Aircraft aerodynamics, automotive design, wind turbines, marine vessels'
            },
            'multi_physics': { 
                name: 'Multi-Physics Analysis', 
                icon: 'fas fa-link', 
                color: 'text-success', 
                description: 'Complex interactions between multiple physical phenomena and coupled systems',
                examples: 'Fluid-structure interaction, thermal-structural coupling, electrochemical systems'
            },
            'industrial': { 
                name: 'Industrial Applications Analysis', 
                icon: 'fas fa-industry', 
                color: 'text-secondary', 
                description: 'Manufacturing processes, industrial systems, and infrastructure optimization',
                examples: 'Additive manufacturing, chemical reactors, power plants, hydrogen infrastructure'
            },
            'other': { 
                name: 'Other Projects Analysis', 
                icon: 'fas fa-folder', 
                color: 'text-muted', 
                description: 'General projects and miscellaneous analysis categories',
                examples: 'Research projects, custom analysis, experimental setups'
            }
        };
    }

    /**
     * Categorize projects by physics type
     * @param {Array} projects - Array of project objects
     * @returns {Object} Categorized projects
     */
    groupProjectsByCategory(projects) {
        console.log('📋 Categorizing projects by physics type...');
        
        const categories = {
            'thermal': { name: 'Thermal Analysis', projects: [] },
            'structural': { name: 'Structural Analysis', projects: [] },
            'fluid_dynamics': { name: 'Fluid Dynamics Analysis', projects: [] },
            'multi_physics': { name: 'Multi-Physics Analysis', projects: [] },
            'industrial': { name: 'Industrial Applications Analysis', projects: [] },
            'other': { name: 'Other Projects Analysis', projects: [] }
        };
        
        // Track processed projects to avoid duplication
        const processedProjects = new Set();
        
        projects.forEach(project => {
            // Skip if already processed
            if (processedProjects.has(project.project_id)) {
                return;
            }
            
            let category = this.determineProjectCategory(project);
            
            if (category && categories[category]) {
                categories[category].projects.push(project);
                processedProjects.add(project.project_id);
                console.log(`📁 Added project "${project.name}" to category "${category}" (physics_type: ${project.metadata?.physics_type || 'none'})`);
            }
        });
        
        // Log categorization results
        console.log('📊 Project categorization results:');
        Object.entries(categories).forEach(([key, data]) => {
            console.log(`  ${data.name}: ${data.projects.length} projects`);
        });
        
        return categories;
    }

    /**
     * Determine the category for a single project
     * @param {Object} project - Project object
     * @returns {string} Category key
     */
    determineProjectCategory(project) {
        // Check metadata first
        if (project.metadata && project.metadata.physics_type) {
            const physicsType = project.metadata.physics_type.toLowerCase();
            return this.mapPhysicsTypeToCategory(physicsType);
        }
        
        // Check tags if no metadata
        if (project.tags && Array.isArray(project.tags)) {
            const tags = project.tags.map(tag => tag.toLowerCase());
            return this.mapTagsToCategory(tags);
        }
        
        // Default to other if no classification found
        return 'other';
    }

    /**
     * Map physics type to category
     * @param {string} physicsType - Physics type string
     * @returns {string} Category key
     */
    mapPhysicsTypeToCategory(physicsType) {
        const mapping = {
            'thermal': 'thermal',
            'structural': 'structural',
            'fluid_dynamics': 'fluid_dynamics',
            'fluid-dynamics': 'fluid_dynamics',
            'multi_physics': 'multi_physics',
            'multi-physics': 'multi_physics',
            'industrial': 'industrial'
        };
        
        return mapping[physicsType] || 'other';
    }

    /**
     * Map tags to category
     * @param {Array} tags - Array of tag strings
     * @returns {string} Category key
     */
    mapTagsToCategory(tags) {
        if (tags.some(tag => tag.includes('thermal'))) {
            return 'thermal';
        } else if (tags.some(tag => tag.includes('structural'))) {
            return 'structural';
        } else if (tags.some(tag => tag.includes('fluid') || tag.includes('aerodynamic'))) {
            return 'fluid_dynamics';
        } else if (tags.some(tag => tag.includes('multi') || tag.includes('coupling'))) {
            return 'multi_physics';
        } else if (tags.some(tag => tag.includes('industrial') || tag.includes('manufacturing'))) {
            return 'industrial';
        } else {
            return 'other';
        }
    }

    /**
     * Get category configuration
     * @param {string} categoryKey - Category key
     * @returns {Object} Category configuration
     */
    getCategoryConfig(categoryKey) {
        return this.categoryConfigs[categoryKey] || this.categoryConfigs['other'];
    }

    /**
     * Get all category configurations
     * @returns {Object} All category configurations
     */
    getAllCategoryConfigs() {
        return this.categoryConfigs;
    }

    /**
     * Filter projects by use case
     * @param {Array} projects - Array of projects
     * @param {string} useCase - Use case to filter by
     * @returns {Array} Filtered projects
     */
    filterProjectsByUseCase(projects, useCase) {
        if (!useCase) return [];
        
        return projects.filter(project => {
            // Check if project has metadata with physics_type
            if (project.metadata && project.metadata.physics_type) {
                return project.metadata.physics_type.toLowerCase() === useCase.toLowerCase();
            }
            
            // Check tags for use case
            if (project.tags && Array.isArray(project.tags)) {
                return project.tags.some(tag => 
                    tag.toLowerCase().includes(useCase.toLowerCase()) ||
                    tag.toLowerCase().includes(useCase.replace('_', ' ').toLowerCase())
                );
            }
            
            return false;
        });
    }

    /**
     * Get category statistics
     * @param {Object} categories - Categorized projects
     * @returns {Object} Statistics object
     */
    getCategoryStatistics(categories) {
        const stats = {
            totalProjects: 0,
            categoryCounts: {},
            largestCategory: null,
            smallestCategory: null
        };
        
        Object.entries(categories).forEach(([key, data]) => {
            const count = data.projects.length;
            stats.totalProjects += count;
            stats.categoryCounts[key] = count;
            
            if (!stats.largestCategory || count > stats.categoryCounts[stats.largestCategory]) {
                stats.largestCategory = key;
            }
            
            if (!stats.smallestCategory || count < stats.categoryCounts[stats.smallestCategory]) {
                stats.smallestCategory = key;
            }
        });
        
        return stats;
    }

    /**
     * Validate project categorization
     * @param {Object} categories - Categorized projects
     * @returns {Object} Validation results
     */
    validateCategorization(categories) {
        const validation = {
            isValid: true,
            errors: [],
            warnings: []
        };
        
        // Check for empty categories
        Object.entries(categories).forEach(([key, data]) => {
            if (data.projects.length === 0) {
                validation.warnings.push(`Category "${key}" has no projects`);
            }
        });
        
        // Check for duplicate projects
        const allProjectIds = [];
        Object.values(categories).forEach(data => {
            data.projects.forEach(project => {
                if (allProjectIds.includes(project.project_id)) {
                    validation.errors.push(`Project "${project.name}" appears in multiple categories`);
                    validation.isValid = false;
                } else {
                    allProjectIds.push(project.project_id);
                }
            });
        });
        
        return validation;
    }
}

// Export the class
export default ProjectCategorizer; 