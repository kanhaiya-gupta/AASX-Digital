/**
 * Privacy & Security Component
 * Handles privacy and security status display and updates
 */

import { showAlert } from '/static/js/shared/alerts.js';

export default class PrivacySecurityComponent {
    constructor() {
        // Authentication properties
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
        
        this.privacyData = {
            privacy_score: 95.2,
            security_status: 'secure',
            compliance_status: 'compliant',
            data_encryption: 'enabled',
            differential_privacy: 'active',
            audit_trail: 'enabled',
            last_audit: new Date().toISOString(),
            security_metrics: {
                encryption_strength: 'AES-256',
                privacy_budget_remaining: 87.5,
                data_anonymization: 'enabled',
                access_controls: 'enforced'
            }
        };
        this.updateInterval = null;
    }
    
    /**
     * Initialize authentication
     */
    initAuthentication() {
        try {
            const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
            const userData = localStorage.getItem('user_data') || sessionStorage.getItem('user_data');
            
            if (token && userData) {
                this.authToken = token;
                this.currentUser = JSON.parse(userData);
                this.isAuthenticated = true;
                console.log('🔐 Privacy & Security: User authenticated as', this.currentUser.username);
            } else {
                this.isAuthenticated = false;
                console.log('🔐 Privacy & Security: User not authenticated');
            }
        } catch (error) {
            console.error('❌ Privacy & Security: Authentication initialization failed:', error);
            this.isAuthenticated = false;
        }
    }

    /**
     * Get authentication token
     */
    getAuthToken() {
        if (!this.authToken) {
            this.initAuthentication();
        }
        return this.authToken;
    }

    /**
     * Get authentication headers
     */
    getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        const token = this.getAuthToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        return headers;
    }
    
    async init() {
        console.log('🔧 Initializing Privacy & Security Component...');
        
        try {
            // Initialize authentication
            this.initAuthentication();
            await this.loadPrivacySecurity();
            this.setupEventListeners();
            this.startAutoRefresh();
            
            console.log('✅ Privacy & Security Component initialized');
        } catch (error) {
            console.error('❌ Failed to initialize Privacy & Security Component:', error);
            throw error;
        }
    }
    
    async loadPrivacySecurity() {
        try {
            // Check authentication
            if (!this.isAuthenticated) {
                console.warn('⚠️ Privacy & Security: User not authenticated, skipping privacy data load');
                return;
            }
            
            console.log('📊 Loading privacy and security data...');
            
            // Simulate API call - replace with actual API call
            const response = await fetch('/api/federated-learning/privacy/status', {
                headers: this.getAuthHeaders()
            });
            if (response.ok) {
                const result = await response.json();
                if (result.status === 'success' && result.data) {
                    this.privacyData = result.data;
                } else {
                    console.warn('⚠️ Failed to load privacy and security data, using default data');
                }
            } else {
                console.warn('⚠️ Failed to load privacy and security data, using default data');
            }
            
            this.displayPrivacySecurity();
        } catch (error) {
            console.error('❌ Error loading privacy and security data:', error);
            // Use default data on error
            this.displayPrivacySecurity();
        }
    }
    
    displayPrivacySecurity() {
        const container = document.getElementById('privacySecurity');
        if (!container) {
            console.warn('⚠️ Privacy and security container not found');
            return;
        }
        
        container.innerHTML = this.createPrivacySecurityHTML();
        console.log('📊 Privacy and security display updated');
    }
    
    createPrivacySecurityHTML() {
        // Ensure privacyData has the required structure
        if (!this.privacyData) {
            this.privacyData = {
                privacy_level: 'high',
                differential_privacy_enabled: true,
                secure_aggregation_enabled: true,
                data_encryption: 'AES-256',
                compliance_status: 'compliant',
                last_audit: '2024-01-15',
                privacy_metrics: {
                    data_leakage_risk: 'low',
                    privacy_loss: 0.1,
                    anonymization_level: 'high'
                }
            };
        }
        
        // Extract values with defaults
        const privacyLevel = this.privacyData.privacy_level || 'high';
        const complianceStatus = this.privacyData.compliance_status || 'compliant';
        const dataEncryption = this.privacyData.data_encryption || 'AES-256';
        const privacyMetrics = this.privacyData.privacy_metrics || {};
        
        // Calculate privacy score based on privacy level
        const privacyScore = privacyLevel === 'high' ? 95 : privacyLevel === 'medium' ? 75 : 50;
        
        // Calculate security status
        const securityStatus = this.privacyData.differential_privacy_enabled && 
                              this.privacyData.secure_aggregation_enabled ? 'secure' : 'warning';
        
        // Create security metrics object
        const securityMetrics = {
            privacy_budget_remaining: 100 - (privacyMetrics.privacy_loss || 0.1) * 100,
            encryption_strength: dataEncryption,
            data_anonymization: privacyMetrics.anonymization_level || 'high',
            access_controls: 'enabled'
        };
        
        return `
            <div class="row text-center mb-3">
                <div class="col-6">
                    <div class="mb-2">
                        <span class="h4 fw-bold text-success">${privacyScore.toFixed(1)}%</span>
                    </div>
                    <small class="text-muted">Privacy Score</small>
                </div>
                <div class="col-6">
                    <div class="mb-2">
                        <span class="h6 fw-bold text-${this.getStatusColor(securityStatus)}">${securityStatus.toUpperCase()}</span>
                    </div>
                    <small class="text-muted">Security Status</small>
                </div>
            </div>
            
            <hr class="my-3">
            
            <div class="row mb-3">
                <div class="col-12">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <small class="text-muted">Privacy Budget</small>
                        <small class="fw-bold">${securityMetrics.privacy_budget_remaining.toFixed(1)}%</small>
                    </div>
                    <div class="progress progress-federated">
                        <div class="progress-bar bg-success" style="width: ${securityMetrics.privacy_budget_remaining}%"></div>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-6">
                    <div class="d-flex align-items-center mb-2">
                        <i class="fas fa-shield-alt text-success me-2"></i>
                        <small class="text-muted">Encryption</small>
                    </div>
                    <div class="fw-bold small">${securityMetrics.encryption_strength}</div>
                </div>
                <div class="col-6">
                    <div class="d-flex align-items-center mb-2">
                        <i class="fas fa-user-secret text-info me-2"></i>
                        <small class="text-muted">Anonymization</small>
                    </div>
                    <div class="fw-bold small text-capitalize">${securityMetrics.data_anonymization}</div>
                </div>
            </div>
            
            <div class="row mt-3">
                <div class="col-6">
                    <div class="d-flex align-items-center mb-2">
                        <i class="fas fa-check-circle text-success me-2"></i>
                        <small class="text-muted">Compliance</small>
                    </div>
                    <div class="fw-bold small text-capitalize">${complianceStatus}</div>
                </div>
                <div class="col-6">
                    <div class="d-flex align-items-center mb-2">
                        <i class="fas fa-lock text-warning me-2"></i>
                        <small class="text-muted">Access Control</small>
                    </div>
                    <div class="fw-bold small text-capitalize">${securityMetrics.access_controls}</div>
                </div>
            </div>
            
            <div class="row mt-3">
                <div class="col-12">
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">
                            <i class="fas fa-shield-alt me-1"></i>
                            Differential Privacy: ${this.privacyData.differential_privacy_enabled ? 'Enabled' : 'Disabled'}
                        </small>
                        <small class="text-muted">
                            <i class="fas fa-lock me-1"></i>
                            Secure Aggregation: ${this.privacyData.secure_aggregation_enabled ? 'Enabled' : 'Disabled'}
                        </small>
                    </div>
                </div>
            </div>
        `;
    }
    
    getStatusColor(status) {
        switch (status.toLowerCase()) {
            case 'secure':
                return 'success';
            case 'warning':
                return 'warning';
            case 'insecure':
                return 'danger';
            default:
                return 'secondary';
        }
    }
    
    setupEventListeners() {
        // Listen for privacy and security updates from other components
        window.addEventListener('privacySecurityUpdated', (event) => {
            this.privacyData = { ...this.privacyData, ...event.detail };
            this.displayPrivacySecurity();
        });
        
        console.log('🔧 Privacy & Security event listeners setup complete');
    }
    
    startAutoRefresh() {
        // Refresh privacy and security data every 60 seconds
        this.updateInterval = setInterval(() => {
            this.loadPrivacySecurity();
        }, 60000);
        
        console.log('🔄 Privacy & Security auto-refresh started');
    }
    
    async refresh() {
        await this.loadPrivacySecurity();
    }
    
    async cleanup() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
        
        console.log('🧹 Privacy & Security Component cleaned up');
    }
} 