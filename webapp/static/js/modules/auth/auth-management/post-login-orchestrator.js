/**
 * Post-Login Orchestrator
 * =======================
 * 
 * This module handles all post-login orchestration tasks:
 * 1. Load AASX-ETL modules after successful login
 * 2. Trigger data loading across all AASX-ETL components
 * 3. Cache user data for instant module access
 * 4. Future: Load other modules (Digital Twin, AI/RAG, etc.)
 * 
 * @author AASX Framework Team
 * @version 1.0.0
 * @since 2025-08-12
 * @module auth/auth-management/post-login-orchestrator
 */

class PostLoginOrchestrator {
    constructor() {
        this.isInitialized = false;
        this.aasxModulesLoaded = false;
        this.kgNeo4jModulesLoaded = false;
        this.aiRagModulesLoaded = false;
        this.twinRegistryModulesLoaded = false;
        this.certificateManagerModulesLoaded = false;
        this.federatedLearningModulesLoaded = false;
        this.physicsModelingModulesLoaded = false;
        this.userDataLoaded = false;
        this.retryAttempts = 0;
        this.maxRetries = 5;
        
        console.log('🎭 Post-Login Orchestrator: Initializing...');
        this.init();
    }
    
    init() {
        if (this.isInitialized) return;
        
        console.log('🎭 Post-Login Orchestrator: Setting up event listeners...');
        
        // Listen for login success event
        window.addEventListener('loginSuccess', this.handleLoginSuccess.bind(this));
        
        this.isInitialized = true;
        console.log('✅ Post-Login Orchestrator: Initialized successfully');
    }
    
    /**
     * Handle login success event
     * @param {Event} event - Login success event
     */
    async handleLoginSuccess(event) {
        console.log('🎉 Post-Login Orchestrator: Login success detected, starting orchestration...');
        console.log('📋 Post-Login Orchestrator: Event details:', event);
        console.log('🔧 Post-Login Orchestrator: Current status:', this.getStatus());
        
        try {
            // Reset state for new login
            console.log('🔄 Post-Login Orchestrator: Phase 0 - Resetting state...');
            this.resetState();
            console.log('✅ Post-Login Orchestrator: State reset completed');
            
            // Phase 1: Load all modules
            console.log('📦 Post-Login Orchestrator: Phase 1 - Loading all modules...');
            await this.loadAllModules();
            console.log('✅ Post-Login Orchestrator: Phase 1 completed - All modules loaded');
            
            // Phase 2: Trigger data loading
            console.log('🚀 Post-Login Orchestrator: Phase 2 - Triggering data loading...');
            await this.triggerAllModulesDataLoading();
            console.log('✅ Post-Login Orchestrator: Phase 2 completed - Data loading triggered');
            
            // Phase 3: Cache data for instant access
            console.log('💾 Post-Login Orchestrator: Phase 3 - Caching user data...');
            this.cacheUserData();
            console.log('✅ Post-Login Orchestrator: Phase 3 completed - Data cached');
            
            // Phase 4: Show success notification
            console.log('🎉 Post-Login Orchestrator: Phase 4 - Showing success notification...');
            this.showSuccessNotification();
            console.log('✅ Post-Login Orchestrator: Phase 4 completed - Success notification shown');
            
            console.log('🎯 Post-Login Orchestrator: ALL PHASES COMPLETED SUCCESSFULLY!');
            console.log('📊 Post-Login Orchestrator: Final status:', this.getStatus());
            
        } catch (error) {
            console.error('❌ Post-Login Orchestrator: Failed to complete orchestration:', error);
            console.error('🔍 Post-Login Orchestrator: Error details:', {
                message: error.message,
                stack: error.stack,
                currentStatus: this.getStatus(),
                event: event
            });
            this.handleOrchestrationError(error);
            
            // 🚫 CRITICAL FIX: Re-throw the error so the auth system knows orchestration failed
            throw error;
        }
    }
    
    /**
     * Reset orchestrator state for new login
     */
    resetState() {
        console.log('🔄 Post-Login Orchestrator: Resetting state for new login...');
        this.aasxModulesLoaded = false;
        this.kgNeo4jModulesLoaded = false;
        this.aiRagModulesLoaded = false;
        this.twinRegistryModulesLoaded = false;
        this.certificateManagerModulesLoaded = false;
        this.federatedLearningModulesLoaded = false;
        this.physicsModelingModulesLoaded = false;
        this.userDataLoaded = false;
        this.retryAttempts = 0;
    }
    
    /**
     * Load all modules
     */
    async loadAllModules() {
        console.log('📦 Post-Login Orchestrator: Loading all modules...');
        
        // Load AASX-ETL modules
        await this.loadAASXETLModules();
        
        // Load Knowledge Graph Neo4j modules
        await this.loadKnowledgeGraphModules();
        
        // Load AI/RAG modules
        await this.loadAIRagModules();
        
        // Load Twin Registry modules
        await this.loadTwinRegistryModules();
        
        // Load Certificate Manager modules
        await this.loadCertificateManagerModules();
        
        // Load Federated Learning modules
        await this.loadFederatedLearningModules();
        
        // Load Physics Modeling modules
        await this.loadPhysicsModelingModules();
        
        console.log('✅ Post-Login Orchestrator: All modules loaded successfully');
    }
    
    /**
     * Load AASX-ETL modules
     */
    async loadAASXETLModules() {
        if (this.aasxModulesLoaded) {
            console.log('🔄 Post-Login Orchestrator: AASX-ETL modules already loaded');
            return;
        }
        
        try {
            console.log('📦 Post-Login Orchestrator: Loading AASX-ETL modules...');
            
            // Check if AASX-ETL modules are already available
            if (window.aasxModules) {
                console.log('✅ Post-Login Orchestrator: AASX-ETL modules already available');
                this.aasxModulesLoaded = true;
                return;
            }
            
            // Try to import AASX-ETL modules
            try {
                const aasxModule = await import('/static/js/modules/aasx/index.js');
                console.log('✅ Post-Login Orchestrator: AASX-ETL modules imported successfully');
                
                // 🚫 CRITICAL FIX: Ensure AASX modules are initialized and accessible
                if (window.initializeAASXIfNeeded) {
                    console.log('🚀 Post-Login Orchestrator: Initializing AASX modules...');
                    await window.initializeAASXIfNeeded();
                    console.log('✅ Post-Login Orchestrator: AASX modules initialized successfully');
                }
                
                this.aasxModulesLoaded = true;
            } catch (importError) {
                console.log('⚠️ Post-Login Orchestrator: Could not import AASX-ETL modules, waiting for initialization...');
                // Wait for modules to be initialized by other means
                await this.waitForAASXModules();
            }
            
        } catch (error) {
            console.error('❌ Post-Login Orchestrator: Failed to load AASX-ETL modules:', error);
            // Don't throw error, continue with other modules
        }
    }
    
    /**
     * Load Knowledge Graph Neo4j modules
     */
    async loadKnowledgeGraphModules() {
        if (this.kgNeo4jModulesLoaded) {
            console.log('🔄 Post-Login Orchestrator: Knowledge Graph modules already loaded');
            return;
        }
        
        try {
            console.log('📦 Post-Login Orchestrator: Loading Knowledge Graph Neo4j modules...');
            
            // Try to import Knowledge Graph modules
            try {
                const kgModule = await import('/static/js/modules/kg_neo4j/index.js');
                console.log('✅ Post-Login Orchestrator: Knowledge Graph modules imported successfully');
                
                                // Initialize Knowledge Graph modules if needed
                if (window.initializeKGIfNeeded) {
                    console.log('🚀 Post-Login Orchestrator: Initializing Knowledge Graph modules...');
                    await window.initializeKGIfNeeded();
                    console.log('✅ Post-Login Orchestrator: Knowledge Graph modules initialized successfully');
                }
                
                // 🔐 CRITICAL FIX: Set Knowledge Graph modules in global window for data loading triggers
                if (window.kgModules) {
                    console.log('✅ Post-Login Orchestrator: Knowledge Graph modules already in window.kgModules');
                } else {
                    // Create a placeholder for modules that will be populated by the KG initialization
                    window.kgModules = {
                        dataManagement: null,
                        analyticsDashboard: null,
                        graphVisualization: null,
                        queryInterface: null,
                        systemStatus: null,
                        dockerManagement: null
                    };
                    console.log('✅ Post-Login Orchestrator: Created window.kgModules placeholder');
                }
                
                this.kgNeo4jModulesLoaded = true;
             } catch (importError) {
                 console.log('⚠️ Post-Login Orchestrator: Could not import Knowledge Graph modules, waiting for initialization...');
                 // Wait for modules to be initialized by other means
                 await this.waitForKnowledgeGraphModules();
             }
            
        } catch (error) {
            console.error('❌ Post-Login Orchestrator: Failed to load Knowledge Graph modules:', error);
            // Don't throw error, continue with other modules
        }
    }
    
    /**
     * Load AI/RAG modules
     */
    async loadAIRagModules() {
        if (this.aiRagModulesLoaded) {
            console.log('🔄 Post-Login Orchestrator: AI/RAG modules already loaded');
            return;
        }
        
        try {
            console.log('📦 Post-Login Orchestrator: Loading AI/RAG modules...');
            
            // Try to import AI/RAG modules
            try {
                const aiRagModule = await import('/static/js/modules/ai_rag/index.js');
                console.log('✅ Post-Login Orchestrator: AI/RAG modules imported successfully');
                
                // Initialize AI/RAG modules if needed
                if (window.initializeAIRAGModuleIfNeeded) {
                    console.log('🚀 Post-Login Orchestrator: Initializing AI/RAG modules...');
                    await window.initializeAIRAGModuleIfNeeded();
                    console.log('✅ Post-Login Orchestrator: AI/RAG modules initialized successfully');
                }
                
                this.aiRagModulesLoaded = true;
             } catch (importError) {
                 console.log('⚠️ Post-Login Orchestrator: Could not import AI/RAG modules, waiting for initialization...');
                 // Wait for modules to be initialized by other means
                 await this.waitForAIRagModules();
             }
            
        } catch (error) {
            console.error('❌ Post-Login Orchestrator: Failed to load AI/RAG modules:', error);
            // Don't throw error, continue with other modules
        }
    }
    
    /**
     * Wait for AASX-ETL modules to be available
     */
    async waitForAASXModules() {
        console.log('⏳ Post-Login Orchestrator: Waiting for AASX-ETL modules to be available...');
        
        return new Promise((resolve, reject) => {
            const checkInterval = setInterval(() => {
                if (window.aasxModules) {
                    console.log('✅ Post-Login Orchestrator: AASX-ETL modules now available');
                    clearInterval(checkInterval);
                    this.aasxModulesLoaded = true;
                    resolve();
                }
                
                // Increment retry attempts
                this.retryAttempts++;
                
                // Timeout after max retries
                if (this.retryAttempts >= this.maxRetries) {
                    clearInterval(checkInterval);
                    const error = new Error('Timeout waiting for AASX-ETL modules');
                    console.warn('⚠️ Post-Login Orchestrator: Timeout waiting for AASX-ETL modules');
                    reject(error);
                }
            }, 200); // Check every 200ms
        });
    }
    
    /**
     * Wait for Knowledge Graph modules to be available
     */
    async waitForKnowledgeGraphModules() {
        console.log('⏳ Post-Login Orchestrator: Waiting for Knowledge Graph modules to be available...');
        
        return new Promise((resolve, reject) => {
            const checkInterval = setInterval(() => {
                if (window.kgModules) {
                    console.log('✅ Post-Login Orchestrator: Knowledge Graph modules now available');
                    clearInterval(checkInterval);
                    this.kgNeo4jModulesLoaded = true;
                    resolve();
                }
                
                // Increment retry attempts
                this.retryAttempts++;
                
                // Timeout after max retries
                if (this.retryAttempts >= this.maxRetries) {
                    clearInterval(checkInterval);
                    const error = new Error('Timeout waiting for Knowledge Graph modules');
                    console.warn('⚠️ Post-Login Orchestrator: Timeout waiting for Knowledge Graph modules');
                    reject(error);
                }
            }, 200); // Check every 200ms
        });
    }
    
    /**
     * Wait for AI/RAG modules to be available
     */
    async waitForAIRagModules() {
        console.log('⏳ Post-Login Orchestrator: Waiting for AI/RAG modules to be available...');
        
        return new Promise((resolve, reject) => {
            const checkInterval = setInterval(() => {
                if (window.aiRAGCore && window.initializeAIRAGModuleIfNeeded) {
                    console.log('✅ Post-Login Orchestrator: AI/RAG modules now available');
                    clearInterval(checkInterval);
                    this.aiRagModulesLoaded = true;
                    resolve();
                }
                
                // Increment retry attempts
                this.retryAttempts++;
                
                // Timeout after max retries
                if (this.retryAttempts >= this.maxRetries) {
                    clearInterval(checkInterval);
                    const error = new Error('Timeout waiting for AI/RAG modules');
                    console.warn('⚠️ Post-Login Orchestrator: Timeout waiting for AI/RAG modules');
                    reject(error);
                }
            }, 200); // Check every 200ms
        });
    }
    
    /**
     * Wait for Twin Registry modules to be available
     */
    async waitForTwinRegistryModules() {
        console.log('⏳ Post-Login Orchestrator: Waiting for Twin Registry modules to be available...');
        
        return new Promise((resolve, reject) => {
            const checkInterval = setInterval(() => {
                if (window.twinRegistryCore && window.initializeTwinRegistryIfNeeded) {
                    console.log('✅ Post-Login Orchestrator: Twin Registry modules now available');
                    clearInterval(checkInterval);
                    this.twinRegistryModulesLoaded = true;
                    resolve();
                }
                
                // Increment retry attempts
                this.retryAttempts++;
                
                // Timeout after max retries
                if (this.retryAttempts >= this.maxRetries) {
                    clearInterval(checkInterval);
                    const error = new Error('Timeout waiting for Twin Registry modules');
                    console.warn('⚠️ Post-Login Orchestrator: Timeout waiting for Twin Registry modules');
                    reject(error);
                }
            }, 200); // Check every 200ms
        });
    }
    
    /**
     * Wait for Certificate Manager modules to be available
     */
    async waitForCertificateManagerModules() {
        console.log('⏳ Post-Login Orchestrator: Waiting for Certificate Manager modules to be available...');
        
        return new Promise((resolve, reject) => {
            const checkInterval = setInterval(() => {
                if (window.certificateManagerModules) {
                    console.log('✅ Post-Login Orchestrator: Certificate Manager modules now available');
                    clearInterval(checkInterval);
                    this.certificateManagerModulesLoaded = true;
                    resolve();
                }
                
                // Increment retry attempts
                this.retryAttempts++;
                
                // Timeout after max retries
                if (this.retryAttempts >= this.maxRetries) {
                    clearInterval(checkInterval);
                    const error = new Error('Timeout waiting for Certificate Manager modules');
                    console.warn('⚠️ Post-Login Orchestrator: Timeout waiting for Certificate Manager modules');
                    reject(error);
                }
            }, 200); // Check every 200ms
        });
    }
    
    /**
     * Wait for Federated Learning modules to be available
     */
    async waitForFederatedLearningModules() {
        console.log('⏳ Post-Login Orchestrator: Waiting for Federated Learning modules to be available...');
        
        return new Promise((resolve, reject) => {
            const checkInterval = setInterval(() => {
                if (window.federatedLearningModules) {
                    console.log('✅ Post-Login Orchestrator: Federated Learning modules now available');
                    clearInterval(checkInterval);
                    this.federatedLearningModulesLoaded = true;
                    resolve();
                }
                
                // Increment retry attempts
                this.retryAttempts++;
                
                // Timeout after max retries
                if (this.retryAttempts >= this.maxRetries) {
                    clearInterval(checkInterval);
                    const error = new Error('Timeout waiting for Federated Learning modules');
                    console.warn('⚠️ Post-Login Orchestrator: Timeout waiting for Federated Learning modules');
                    reject(error);
                }
            }, 200); // Check every 200ms
        });
    }
    
    /**
     * Wait for Physics Modeling modules to be available
     */
    async waitForPhysicsModelingModules() {
        console.log('⏳ Post-Login Orchestrator: Waiting for Physics Modeling modules to be available...');
        
        return new Promise((resolve, reject) => {
            const checkInterval = setInterval(() => {
                if (window.physicsModelingModules) {
                    console.log('✅ Post-Login Orchestrator: Physics Modeling modules now available');
                    clearInterval(checkInterval);
                    this.physicsModelingModulesLoaded = true;
                    resolve();
                }
                
                // Increment retry attempts
                this.retryAttempts++;
                
                // Timeout after max retries
                if (this.retryAttempts >= this.maxRetries) {
                    clearInterval(checkInterval);
                    const error = new Error('Timeout waiting for Physics Modeling modules');
                    console.warn('⚠️ Post-Login Orchestrator: Timeout waiting for Physics Modeling modules');
                    reject(error);
                }
            }, 200); // Check every 200ms
        });
    }
    
    /**
     * Load Twin Registry modules
     */
    async loadTwinRegistryModules() {
        if (this.twinRegistryModulesLoaded) {
            console.log('🔄 Post-Login Orchestrator: Twin Registry modules already loaded');
            return;
        }
        
        try {
            console.log('📦 Post-Login Orchestrator: Loading Twin Registry modules...');
            
            // Try to import Twin Registry modules
            try {
                const twinRegistryModule = await import('/static/js/modules/twin_registry/index.js');
                console.log('✅ Post-Login Orchestrator: Twin Registry modules imported successfully');
                
                // Initialize Twin Registry modules if needed
                if (window.initializeTwinRegistryIfNeeded) {
                    console.log('🚀 Post-Login Orchestrator: Initializing Twin Registry modules...');
                    await window.initializeTwinRegistryIfNeeded();
                    console.log('✅ Post-Login Orchestrator: Twin Registry modules initialized successfully');
                }
                
                this.twinRegistryModulesLoaded = true;
            } catch (importError) {
                console.log('⚠️ Post-Login Orchestrator: Could not import Twin Registry modules, waiting for initialization...');
                // Wait for modules to be initialized by other means
                await this.waitForTwinRegistryModules();
            }
            
        } catch (error) {
            console.error('❌ Post-Login Orchestrator: Failed to load Twin Registry modules:', error);
            // Don't throw error, continue with other modules
        }
    }
    
    /**
     * Load Certificate Manager modules
     */
    async loadCertificateManagerModules() {
        if (this.certificateManagerModulesLoaded) {
            console.log('🔄 Post-Login Orchestrator: Certificate Manager modules already loaded');
            return;
        }
        
        try {
            console.log('📦 Post-Login Orchestrator: Loading Certificate Manager modules...');
            
            // Try to import Certificate Manager modules
            try {
                const certManagerModule = await import('/static/js/modules/certificate_manager/index.js');
                console.log('✅ Post-Login Orchestrator: Certificate Manager modules imported successfully');
                
                // Initialize Certificate Manager modules if needed
                if (window.initializeCertificateManagerIfNeeded) {
                    console.log('🚀 Post-Login Orchestrator: Initializing Certificate Manager modules...');
                    await window.initializeCertificateManagerIfNeeded();
                    console.log('✅ Post-Login Orchestrator: Certificate Manager modules initialized successfully');
                }
                
                                 this.certificateManagerModulesLoaded = true;
             } catch (importError) {
                 console.log('⚠️ Post-Login Orchestrator: Could not import Certificate Manager modules, waiting for initialization...');
                 // Wait for modules to be initialized by other means
                 await this.waitForCertificateManagerModules();
             }
            
        } catch (error) {
            console.error('❌ Post-Login Orchestrator: Failed to load Certificate Manager modules:', error);
            // Don't throw error, continue with other modules
        }
    }
    
    /**
     * Load Federated Learning modules
     */
    async loadFederatedLearningModules() {
        if (this.federatedLearningModulesLoaded) {
            console.log('🔄 Post-Login Orchestrator: Federated Learning modules already loaded');
            return;
        }
        
        try {
            console.log('📦 Post-Login Orchestrator: Loading Federated Learning modules...');
            
            // Try to import Federated Learning modules
            try {
                const flModule = await import('/static/js/modules/federated_learning/index.js');
                console.log('✅ Post-Login Orchestrator: Federated Learning modules imported successfully');
                
                // Initialize Federated Learning modules if needed
                if (window.initializeFederatedLearningIfNeeded) {
                    console.log('🚀 Post-Login Orchestrator: Initializing Federated Learning modules...');
                    await window.initializeFederatedLearningIfNeeded();
                    console.log('✅ Post-Login Orchestrator: Federated Learning modules initialized successfully');
                }
                
                this.federatedLearningModulesLoaded = true;
            } catch (importError) {
                console.log('⚠️ Post-Login Orchestrator: Could not import Federated Learning modules, waiting for initialization...');
                // Wait for modules to be initialized by other means
                await this.waitForFederatedLearningModules();
            }
            
        } catch (error) {
            console.error('❌ Post-Login Orchestrator: Failed to load Federated Learning modules:', error);
            // Don't throw error, continue with other modules
        }
    }
    
    /**
     * Load Physics Modeling modules
     */
    async loadPhysicsModelingModules() {
        if (this.physicsModelingModulesLoaded) {
            console.log('🔄 Post-Login Orchestrator: Physics Modeling modules already loaded');
            return;
        }
        
        try {
            console.log('📦 Post-Login Orchestrator: Loading Physics Modeling modules...');
            
            // Try to import Physics Modeling modules
            try {
                const physicsModule = await import('/static/js/modules/physics_modeling/index.js');
                console.log('✅ Post-Login Orchestrator: Physics Modeling modules imported successfully');
                
                // Initialize Physics Modeling modules if needed
                if (window.initializePhysicsModelingIfNeeded) {
                    console.log('🚀 Post-Login Orchestrator: Initializing Physics Modeling modules...');
                    await window.initializePhysicsModelingIfNeeded();
                    console.log('✅ Post-Login Orchestrator: Physics Modeling modules initialized successfully');
                }
                
                                 this.physicsModelingModulesLoaded = true;
             } catch (importError) {
                 console.log('⚠️ Post-Login Orchestrator: Could not import Physics Modeling modules, waiting for initialization...');
                 // Wait for modules to be initialized by other means
                 await this.waitForPhysicsModelingModules();
             }
            
        } catch (error) {
            console.error('❌ Post-Login Orchestrator: Failed to load Physics Modeling modules:', error);
            // Don't throw error, continue with other modules
        }
    }
    
    /**
     * Trigger data loading in all modules
     */
    async triggerAllModulesDataLoading() {
        if (this.userDataLoaded) {
            console.log('🔄 Post-Login Orchestrator: User data already loaded');
            return;
        }
        
        try {
            console.log('🚀 Post-Login Orchestrator: Triggering data loading in all modules...');
            
            // Trigger data refresh in AASX-ETL modules
            await this.triggerAASXETLDataLoading();
            
            // Trigger data refresh in Knowledge Graph modules
            await this.triggerKnowledgeGraphDataLoading();
            
            // Trigger data refresh in other modules as needed
            // (Add more module data loading triggers here)
            
            this.userDataLoaded = true;
            console.log('✅ Post-Login Orchestrator: All modules data loading completed');
            
        } catch (error) {
            console.error('❌ Post-Login Orchestrator: Failed to trigger all modules data loading:', error);
            // Don't throw error, continue
        }
    }
    
    /**
     * Trigger data loading in AASX-ETL modules
     */
    async triggerAASXETLDataLoading() {
        try {
            console.log('🚀 Post-Login Orchestrator: Triggering data loading in AASX-ETL modules...');
            
            // Trigger data refresh in all AASX-ETL modules
            if (window.aasxModules) {
                const modules = window.aasxModules;
                
                // Data Manager Core - Load projects
                if (modules.dataManager && typeof modules.dataManager.loadProjects === 'function') {
                    console.log('📊 Post-Login Orchestrator: Loading user projects...');
                    await modules.dataManager.loadProjects();
                } else {
                    console.warn('⚠️ Post-Login Orchestrator: Data Manager not available or missing loadProjects method');
                }
                
                // ETL Pipeline - Load use cases
                if (modules.etlPipeline && typeof modules.etlPipeline.loadUseCases === 'function') {
                    console.log('📊 Post-Login Orchestrator: Loading user use cases...');
                    await modules.etlPipeline.loadUseCases();
                } else {
                    console.warn('⚠️ Post-Login Orchestrator: ETL Pipeline not available or missing loadUseCases method');
                }
            } else {
                console.warn('⚠️ Post-Login Orchestrator: AASX modules not available');
            }
        } catch (error) {
            console.error('❌ Post-Login Orchestrator: Failed to trigger AASX-ETL data loading:', error);
            // Don't throw error, continue
        }
    }
    
    /**
     * Trigger data loading in Knowledge Graph modules
     */
    async triggerKnowledgeGraphDataLoading() {
        try {
            console.log('🚀 Post-Login Orchestrator: Triggering data loading in Knowledge Graph modules...');
            
            // Trigger data refresh in Knowledge Graph modules
            if (window.kgModules) {
                const modules = window.kgModules;
                
                // Data Management - Load projects and files
                if (modules.dataManagement && typeof modules.dataManagement.loadUseCases === 'function') {
                    console.log('📊 Post-Login Orchestrator: Loading Knowledge Graph use cases...');
                    await modules.dataManagement.loadUseCases();
                } else {
                    console.warn('⚠️ Post-Login Orchestrator: Knowledge Graph Data Management not available or missing loadUseCases method');
                }
                
                // Analytics Dashboard - Refresh data
                if (modules.analyticsDashboard && typeof modules.analyticsDashboard.refreshAnalyticsDashboard === 'function') {
                    console.log('📊 Post-Login Orchestrator: Refreshing Knowledge Graph analytics...');
                    await modules.analyticsDashboard.refreshAnalyticsDashboard();
                } else {
                    console.warn('⚠️ Post-Login Orchestrator: Knowledge Graph Analytics Dashboard not available or missing refreshAnalyticsDashboard method');
                }
            } else {
                console.warn('⚠️ Post-Login Orchestrator: Knowledge Graph modules not available');
            }
        } catch (error) {
            console.error('❌ Post-Login Orchestrator: Failed to trigger Knowledge Graph data loading:', error);
            // Don't throw error, continue
        }
    }
    
    /**
     * Cache user data for instant access
     */
    cacheUserData() {
        console.log('💾 Post-Login Orchestrator: Caching user data for instant access...');
        
        try {
            // Store user data in global state for other modules to access
            if (window.aasxModules) {
                // Cache projects
                if (window.aasxModules.dataManager && window.aasxModules.dataManager.projects) {
                    window.userDataCache = window.userDataCache || {};
                    window.userDataCache.projects = window.aasxModules.dataManager.projects;
                    console.log('💾 Post-Login Orchestrator: Projects cached successfully');
                }
                
                // Cache use cases
                if (window.aasxModules.dropdownManager && window.aasxModules.dropdownManager.useCases) {
                    window.userDataCache = window.userDataCache || {};
                    window.userDataCache.useCases = window.aasxModules.dropdownManager.useCases;
                    console.log('💾 Post-Login Orchestrator: Use cases cached successfully');
                }
                
                // Cache files
                if (window.aasxModules.etlPipeline && window.aasxModules.etlPipeline.files) {
                    window.userDataCache = window.userDataCache || {};
                    window.userDataCache.files = window.aasxModules.etlPipeline.files;
                    console.log('💾 Post-Login Orchestrator: Files cached successfully');
                }
            }
            
            console.log('✅ Post-Login Orchestrator: User data caching completed');
            
        } catch (error) {
            console.error('❌ Post-Login Orchestrator: Failed to cache user data:', error);
        }
    }
    
    /**
     * Show success notification
     */
    showSuccessNotification() {
        console.log('🎉 Post-Login Orchestrator: Showing success notification...');
        
        try {
            // Show user data section if it exists on the current page
            const userDataSection = document.getElementById('userDataSection');
            if (userDataSection) {
                userDataSection.style.display = 'block';
                console.log('✅ Post-Login Orchestrator: User data section displayed');
            }
            
            // You can add more UI updates here
            // For example, updating navigation, showing user info, etc.
            
        } catch (error) {
            console.error('❌ Post-Login Orchestrator: Failed to show success notification:', error);
        }
    }
    
    /**
     * Handle orchestration errors
     */
    handleOrchestrationError(error) {
        console.error('❌ Post-Login Orchestrator: Error handling orchestration:', error);
        
        // Log error details
        console.error('Error details:', {
            message: error.message,
            stack: error.stack,
            aasxModulesLoaded: this.aasxModulesLoaded,
            kgNeo4jModulesLoaded: this.kgNeo4jModulesLoaded,
            aiRagModulesLoaded: this.aiRagModulesLoaded,
            twinRegistryModulesLoaded: this.twinRegistryModulesLoaded,
            certificateManagerModulesLoaded: this.certificateManagerModulesLoaded,
            federatedLearningModulesLoaded: this.federatedLearningModulesLoaded,
            physicsModelingModulesLoaded: this.physicsModelingModulesLoaded,
            userDataLoaded: this.userDataLoaded,
            retryAttempts: this.retryAttempts
        });
        
        // You can add error recovery logic here
        // For example, retry mechanisms, fallback data loading, etc.
    }
    
    /**
     * Get orchestrator status
     */
    getStatus() {
        return {
            isInitialized: this.isInitialized,
            aasxModulesLoaded: this.aasxModulesLoaded,
            kgNeo4jModulesLoaded: this.kgNeo4jModulesLoaded,
            aiRagModulesLoaded: this.aiRagModulesLoaded,
            twinRegistryModulesLoaded: this.twinRegistryModulesLoaded,
            certificateManagerModulesLoaded: this.certificateManagerModulesLoaded,
            federatedLearningModulesLoaded: this.federatedLearningModulesLoaded,
            physicsModelingModulesLoaded: this.physicsModelingModulesLoaded,
            userDataLoaded: this.userDataLoaded,
            retryAttempts: this.retryAttempts,
            maxRetries: this.maxRetries
        };
    }
    
    /**
     * Manually trigger orchestration (for testing/debugging)
     */
    async manualTrigger() {
        console.log('🔧 Post-Login Orchestrator: Manual trigger requested...');
        await this.handleLoginSuccess({});
    }
}

// Export for module system
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PostLoginOrchestrator;
}

// Default export for ES6 modules
export default PostLoginOrchestrator;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎭 Post-Login Orchestrator: DOM ready, initializing...');
    window.postLoginOrchestrator = new PostLoginOrchestrator();
});

// Also initialize immediately if DOM is already ready
if (document.readyState === 'loading') {
    // DOM is still loading, wait for DOMContentLoaded
} else {
    // DOM is already ready, initialize immediately
    console.log('🎭 Post-Login Orchestrator: DOM already ready, initializing immediately...');
    window.postLoginOrchestrator = new PostLoginOrchestrator();
}
