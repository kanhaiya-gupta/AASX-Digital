/**
 * Cross-Twin Insights Component
 * Handles cross-twin insights display and updates
 */

import { showAlert } from '../../shared/alerts.js';

export default class CrossTwinInsightsComponent {
    constructor() {
        this.insightsData = {
            insights: [
                {
                    type: 'performance_correlation',
                    title: 'Performance Correlation Detected',
                    description: 'Additive Manufacturing and Hydrogen Filling Station show similar performance patterns during peak hours.',
                    confidence: 0.85,
                    twins: ['twin_1', 'twin_3'],
                    timestamp: new Date().toISOString()
                },
                {
                    type: 'anomaly_detection',
                    title: 'Anomaly Pattern Identified',
                    description: 'Smart Grid Substation shows unusual behavior that correlates with energy consumption patterns.',
                    confidence: 0.92,
                    twins: ['twin_2'],
                    timestamp: new Date().toISOString()
                },
                {
                    type: 'optimization_opportunity',
                    title: 'Optimization Opportunity',
                    description: 'Cross-twin learning suggests 15% efficiency improvement potential through shared parameters.',
                    confidence: 0.78,
                    twins: ['twin_1', 'twin_2', 'twin_3'],
                    timestamp: new Date().toISOString()
                }
            ],
            relationships: [
                { source: 'twin_1', target: 'twin_2', strength: 0.7, type: 'performance' },
                { source: 'twin_1', target: 'twin_3', strength: 0.8, type: 'efficiency' },
                { source: 'twin_2', target: 'twin_3', strength: 0.6, type: 'energy' }
            ]
        };
        this.updateInterval = null;
    }
    
    async init() {
        console.log('🔧 Initializing Cross-Twin Insights Component...');
        
        try {
            await this.loadCrossTwinInsights();
            this.setupEventListeners();
            this.startAutoRefresh();
            
            console.log('✅ Cross-Twin Insights Component initialized');
        } catch (error) {
            console.error('❌ Failed to initialize Cross-Twin Insights Component:', error);
            throw error;
        }
    }
    
    async loadCrossTwinInsights() {
        try {
            console.log('📊 Loading cross-twin insights...');
            
            // Simulate API call - replace with actual API call
            const response = await fetch('/api/federated-learning/insights/cross-twin');
            if (response.ok) {
                const result = await response.json();
                if (result.status === 'success' && result.data) {
                    this.insightsData = result.data;
                } else {
                    console.warn('⚠️ Failed to load cross-twin insights, using default data');
                }
            } else {
                console.warn('⚠️ Failed to load cross-twin insights, using default data');
            }
            
            this.displayCrossTwinInsights();
        } catch (error) {
            console.error('❌ Error loading cross-twin insights:', error);
            // Use default data on error
            this.displayCrossTwinInsights();
        }
    }
    
    displayCrossTwinInsights() {
        const container = document.getElementById('crossTwinInsights');
        if (!container) {
            console.warn('⚠️ Cross-twin insights container not found');
            return;
        }
        
        container.innerHTML = '';
        
        // Check if insights data exists and has required properties
        if (!this.insightsData) {
            this.insightsData = {
                insights: [],
                relationships: [],
                total_federated_twins: 0,
                active_twins: 0,
                ready_twins: 0,
                avg_contribution_score: 0,
                avg_health_score: 0,
                avg_data_quality: 0,
                twin_types: {},
                performance_distribution: { high_performers: 0, medium_performers: 0, low_performers: 0 },
                health_distribution: { healthy: 0, moderate: 0, poor: 0 },
                top_contributors: [],
                insights: []
            };
        }
        
        // Ensure arrays exist
        if (!this.insightsData.insights) this.insightsData.insights = [];
        if (!this.insightsData.relationships) this.insightsData.relationships = [];
        if (!this.insightsData.top_contributors) this.insightsData.top_contributors = [];
        
        // Display summary statistics
        const summarySection = this.createSummarySection();
        container.appendChild(summarySection);
        
        // Display top contributors
        if (this.insightsData.top_contributors && this.insightsData.top_contributors.length > 0) {
            const contributorsSection = this.createContributorsSection();
            container.appendChild(contributorsSection);
        }
        
        // Display insights
        if (this.insightsData.insights && this.insightsData.insights.length > 0) {
            this.insightsData.insights.forEach(insight => {
                const insightCard = this.createInsightCard(insight);
                container.appendChild(insightCard);
            });
        } else {
            // Display default insight
            const defaultInsight = this.createDefaultInsight();
            container.appendChild(defaultInsight);
        }
        
        console.log('📊 Cross-twin insights display updated');
    }
    
    createSummarySection() {
        const section = document.createElement('div');
        section.className = 'mb-4';
        
        section.innerHTML = `
            <div class="row">
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="card-title">${this.insightsData.total_federated_twins || 0}</h5>
                            <p class="card-text">Total Federated Twins</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="card-title">${this.insightsData.active_twins || 0}</h5>
                            <p class="card-text">Active Twins</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="card-title">${(this.insightsData.avg_contribution_score || 0).toFixed(2)}</h5>
                            <p class="card-text">Avg Contribution</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="card-title">${(this.insightsData.avg_health_score || 0).toFixed(1)}</h5>
                            <p class="card-text">Avg Health Score</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        return section;
    }
    
    createContributorsSection() {
        const section = document.createElement('div');
        section.className = 'mb-4';
        
        section.innerHTML = `
            <h6><i class="fas fa-trophy me-2"></i>Top Contributors</h6>
            <div class="row">
                ${this.insightsData.top_contributors.map(contributor => `
                    <div class="col-md-6 mb-2">
                        <div class="d-flex justify-content-between align-items-center p-2 border rounded">
                            <div>
                                <strong>${contributor.twin_name || contributor.twin_id}</strong>
                                <br><small class="text-muted">Health: ${contributor.health_score || 0}</small>
                            </div>
                            <div class="text-end">
                                <span class="badge bg-primary">${(contributor.contribution_score || 0).toFixed(2)}</span>
                                <br><small class="text-muted">Rounds: ${contributor.rounds || 0}</small>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        return section;
    }
    
    createDefaultInsight() {
        const card = document.createElement('div');
        card.className = 'insight-card mb-3';
        
        card.innerHTML = `
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <div class="insight-title">Federated Learning Status</div>
                    <div class="insight-content">
                        ${this.insightsData.total_federated_twins > 0 
                            ? `Currently monitoring ${this.insightsData.total_federated_twins} federated twins with ${this.insightsData.active_twins} active participants.`
                            : 'No federated twins are currently active. Start federation to see insights.'}
                    </div>
                </div>
                <div class="ms-3">
                    <span class="badge bg-info">Status</span>
                </div>
            </div>
        `;
        
        return card;
    }
    
    createInsightCard(insight) {
        const card = document.createElement('div');
        card.className = 'insight-card mb-3';
        
        const confidenceColor = this.getConfidenceColor(insight.confidence);
        
        card.innerHTML = `
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <div class="insight-title">${insight.title}</div>
                    <div class="insight-content">${insight.description}</div>
                    <div class="mt-2">
                        <small class="text-muted">
                            <i class="fas fa-users me-1"></i>
                            ${insight.twins.length} twin${insight.twins.length > 1 ? 's' : ''} involved
                        </small>
                    </div>
                </div>
                <div class="ms-3">
                    <span class="badge bg-${confidenceColor}">${(insight.confidence * 100).toFixed(0)}%</span>
                </div>
            </div>
        `;
        
        return card;
    }
    
    createRelationshipSection() {
        const section = document.createElement('div');
        section.className = 'mt-4';
        
        const title = document.createElement('h6');
        title.className = 'mb-3';
        title.innerHTML = '<i class="fas fa-project-diagram me-2"></i>Twin Relationships';
        section.appendChild(title);
        
        const relationshipContainer = document.createElement('div');
        relationshipContainer.className = 'd-flex flex-wrap gap-2';
        
        this.insightsData.relationships.forEach(rel => {
            const node = this.createRelationshipNode(rel);
            relationshipContainer.appendChild(node);
        });
        
        section.appendChild(relationshipContainer);
        return section;
    }
    
    createRelationshipNode(relationship) {
        const node = document.createElement('span');
        node.className = `relationship-node ${relationship.type}`;
        node.innerHTML = `
            ${relationship.source.replace('twin_', 'Twin ')} ↔ ${relationship.target.replace('twin_', 'Twin ')}
            <small class="ms-2 opacity-75">${(relationship.strength * 100).toFixed(0)}%</small>
        `;
        
        return node;
    }
    
    getConfidenceColor(confidence) {
        if (confidence >= 0.8) return 'success';
        if (confidence >= 0.6) return 'warning';
        return 'danger';
    }
    
    setupEventListeners() {
        // Listen for insights updates from other components
        window.addEventListener('crossTwinInsightsUpdated', (event) => {
            this.insightsData = { ...this.insightsData, ...event.detail };
            this.displayCrossTwinInsights();
        });
        
        console.log('🔧 Cross-Twin Insights event listeners setup complete');
    }
    
    startAutoRefresh() {
        // Refresh insights every 120 seconds
        this.updateInterval = setInterval(() => {
            this.loadCrossTwinInsights();
        }, 120000);
        
        console.log('🔄 Cross-Twin Insights auto-refresh started');
    }
    
    async refresh() {
        await this.loadCrossTwinInsights();
    }
    
    async cleanup() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
        
        console.log('🧹 Cross-Twin Insights Component cleaned up');
    }
} 