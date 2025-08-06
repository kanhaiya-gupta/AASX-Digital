/**
 * Configuration Operations Module
 * Handles configuration management operations
 */

export class ConfigurationOperations {
    constructor(baseUrl = '/api/twin-registry') {
        this.baseUrl = baseUrl;
        this.endpoints = {
            get: '/configuration',
            save: '/configuration',
            reset: '/configuration/reset',
            export: '/configuration/export',
            import: '/configuration/import',
            validate: '/configuration/validate'
        };
    }

    async getConfiguration() {
        try {
            const response = await fetch(`${this.baseUrl}${this.endpoints.get}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching configuration:', error);
            throw error;
        }
    }

    async saveConfiguration(configData) {
        try {
            const response = await fetch(`${this.baseUrl}${this.endpoints.save}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(configData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error saving configuration:', error);
            throw error;
        }
    }

    async resetConfiguration() {
        try {
            const response = await fetch(`${this.baseUrl}${this.endpoints.reset}`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error resetting configuration:', error);
            throw error;
        }
    }

    async exportConfiguration(format = 'json') {
        try {
            const response = await fetch(`${this.baseUrl}${this.endpoints.export}?format=${format}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error exporting configuration:', error);
            throw error;
        }
    }

    async importConfiguration(configData) {
        try {
            const response = await fetch(`${this.baseUrl}${this.endpoints.import}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(configData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error importing configuration:', error);
            throw error;
        }
    }

    async validateConfiguration(configData) {
        try {
            const response = await fetch(`${this.baseUrl}${this.endpoints.validate}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(configData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error validating configuration:', error);
            throw error;
        }
    }
} 