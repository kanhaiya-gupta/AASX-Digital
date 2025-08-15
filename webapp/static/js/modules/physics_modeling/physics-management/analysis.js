/**
 * Analysis Manager
 * Handles data analysis, post-processing, and result interpretation
 */

export class AnalysisManager {
    constructor() {
        // Authentication properties
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
        
        this.isInitialized = false;
        this.activeAnalyses = [];
        this.analysisConfig = {
            defaultMethod: 'fft',
            precision: 'high',
            enableParallel: true,
            maxWorkers: 4
        };
        this.analysisTypes = [
            'fft',
            'statistical',
            'spectral',
            'correlation',
            'regression',
            'clustering'
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
            this.loadUserAnalyses();
        } else {
            this.loadDemoAnalyses();
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
        
        console.log('🔐 Initializing Analysis Manager...');
        
        try {
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            await this.loadAnalysisConfiguration();
            await this.loadExistingAnalyses();
            
            this.isInitialized = true;
            console.log('✅ Analysis Manager initialized');
        } catch (error) {
            console.error('❌ Analysis Manager initialization failed:', error);
            throw error;
        }
    }

    async loadAnalysisConfiguration() {
        try {
            const response = await fetch('/api/physics-modeling/analysis/config', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const config = await response.json();
                this.analysisConfig = { ...this.analysisConfig, ...config };
            }
        } catch (error) {
            console.error('❌ Failed to load analysis configuration:', error);
        }
    }

    async loadExistingAnalyses() {
        try {
            const response = await fetch('/api/physics-modeling/analysis/list', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                this.activeAnalyses = data.analyses || [];
            }
        } catch (error) {
            console.error('❌ Failed to load existing analyses:', error);
        }
    }

    async startAnalysis(data, method, parameters = {}) {
        try {
            const analysisParams = {
                data: data,
                method: method,
                parameters: { ...this.analysisConfig, ...parameters }
            };

            const response = await fetch('/api/physics-modeling/analysis/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeaders()
                },
                body: JSON.stringify(analysisParams)
            });

            if (response.ok) {
                const result = await response.json();
                this.activeAnalyses.push(result.analysisId);
                return result.analysisId;
            } else {
                throw new Error('Failed to start analysis');
            }
        } catch (error) {
            console.error('❌ Failed to start analysis:', error);
            throw error;
        }
    }

    async getAnalysisStatus(analysisId) {
        try {
            const response = await fetch(`/api/physics-modeling/analysis/${analysisId}/status`, {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('❌ Failed to get analysis status:', error);
        }
        return null;
    }

    async getAnalysisResults(analysisId) {
        try {
            const response = await fetch(`/api/physics-modeling/analysis/${analysisId}/results`, {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('❌ Failed to get analysis results:', error);
        }
        return null;
    }

    async cancelAnalysis(analysisId) {
        try {
            const response = await fetch(`/api/physics-modeling/analysis/${analysisId}/cancel`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                this.activeAnalyses = this.activeAnalyses.filter(id => id !== analysisId);
                return true;
            }
        } catch (error) {
            console.error('❌ Failed to cancel analysis:', error);
        }
        return false;
    }

    async exportAnalysis(analysisId, format = 'json') {
        try {
            const response = await fetch(`/api/physics-modeling/analysis/${analysisId}/export`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeaders()
                },
                body: JSON.stringify({ format: format })
            });

            if (response.ok) {
                return await response.blob();
            }
        } catch (error) {
            console.error('❌ Failed to export analysis:', error);
        }
        return null;
    }

    async loadUserAnalyses() {
        try {
            const response = await fetch('/api/physics-modeling/analysis/user', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                this.activeAnalyses = data.analyses || [];
            }
        } catch (error) {
            console.error('❌ Failed to load user analyses:', error);
        }
    }

    async loadDemoAnalyses() {
        try {
            const response = await fetch('/api/physics-modeling/analysis/demo');
            
            if (response.ok) {
                const data = await response.json();
                this.activeAnalyses = data.analyses || [];
            }
        } catch (error) {
            console.error('❌ Failed to load demo analyses:', error);
        }
    }

    getAnalysisHistory() {
        return this.activeAnalyses;
    }

    async cleanup() {
        console.log('🧹 Cleaning up Analysis Manager...');
        this.clearSensitiveData();
        this.isInitialized = false;
        console.log('✅ Analysis Manager cleaned up');
    }
}
