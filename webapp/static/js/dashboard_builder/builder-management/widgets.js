/**
 * Dashboard Widgets Management
 * Handles widget types, creation, and management
 */

export default class DashboardWidgets {
    constructor() {
        this.isInitialized = false;
        this.widgetTypes = {
            chart: {
                name: 'Chart Widget',
                icon: 'fas fa-chart-bar',
                description: 'Display data in various chart formats',
                defaultWidth: 6,
                defaultHeight: 4,
                configurable: true,
                dataSources: ['api', 'static', 'database']
            },
            metric: {
                name: 'Metric Widget',
                icon: 'fas fa-tachometer-alt',
                description: 'Display key performance indicators',
                defaultWidth: 3,
                defaultHeight: 2,
                configurable: true,
                dataSources: ['api', 'static', 'database']
            },
            table: {
                name: 'Table Widget',
                icon: 'fas fa-table',
                description: 'Display data in tabular format',
                defaultWidth: 8,
                defaultHeight: 6,
                configurable: true,
                dataSources: ['api', 'static', 'database']
            },
            gauge: {
                name: 'Gauge Widget',
                icon: 'fas fa-dial',
                description: 'Display progress or percentage values',
                defaultWidth: 4,
                defaultHeight: 3,
                configurable: true,
                dataSources: ['api', 'static', 'database']
            },
            text: {
                name: 'Text Widget',
                icon: 'fas fa-font',
                description: 'Display text content or markdown',
                defaultWidth: 4,
                defaultHeight: 2,
                configurable: true,
                dataSources: ['static', 'markdown']
            },
            image: {
                name: 'Image Widget',
                icon: 'fas fa-image',
                description: 'Display images or logos',
                defaultWidth: 3,
                defaultHeight: 3,
                configurable: true,
                dataSources: ['url', 'upload']
            },
            iframe: {
                name: 'IFrame Widget',
                icon: 'fas fa-external-link-alt',
                description: 'Embed external content or web pages',
                defaultWidth: 6,
                defaultHeight: 4,
                configurable: true,
                dataSources: ['url']
            },
            progress: {
                name: 'Progress Widget',
                icon: 'fas fa-tasks',
                description: 'Display progress bars or completion status',
                defaultWidth: 4,
                defaultHeight: 2,
                configurable: true,
                dataSources: ['api', 'static', 'database']
            }
        };
        this.customWidgets = [];
    }

    /**
     * Initialize the Widgets Management
     */
    async init() {
        console.log('🔧 Dashboard Widgets Management initializing...');
        
        try {
            // Load custom widgets
            await this.loadCustomWidgets();
            
            // Register widget event handlers
            this.registerEventHandlers();
            
            this.isInitialized = true;
            console.log('✅ Dashboard Widgets Management initialized');
            
        } catch (error) {
            console.error('❌ Dashboard Widgets Management initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load custom widgets from server
     */
    async loadCustomWidgets() {
        try {
            const response = await fetch('/api/dashboard-builder/widgets/custom');
            if (response.ok) {
                this.customWidgets = await response.json();
                console.log(`📦 Loaded ${this.customWidgets.length} custom widgets`);
            }
        } catch (error) {
            console.warn('⚠️ Could not load custom widgets:', error);
            this.customWidgets = [];
        }
    }

    /**
     * Register event handlers for widget interactions
     */
    registerEventHandlers() {
        // Widget drag and drop
        document.addEventListener('dragstart', this.handleDragStart.bind(this));
        document.addEventListener('dragover', this.handleDragOver.bind(this));
        document.addEventListener('drop', this.handleDrop.bind(this));
        
        // Widget resize
        document.addEventListener('mousedown', this.handleResizeStart.bind(this));
        document.addEventListener('mousemove', this.handleResizeMove.bind(this));
        document.addEventListener('mouseup', this.handleResizeEnd.bind(this));
        
        console.log('🎯 Widget event handlers registered');
    }

    /**
     * Create a new widget
     */
    createWidget(type, config = {}) {
        const widgetType = this.widgetTypes[type] || this.getCustomWidgetType(type);
        
        if (!widgetType) {
            throw new Error(`Unknown widget type: ${type}`);
        }

        const widget = {
            type,
            title: config.title || widgetType.name,
            description: config.description || widgetType.description,
            config: {
                dataSource: config.dataSource || widgetType.dataSources[0],
                dataUrl: config.dataUrl || '',
                refreshInterval: config.refreshInterval || 0,
                ...config
            },
            style: {
                backgroundColor: config.backgroundColor || '#ffffff',
                borderColor: config.borderColor || '#e0e0e0',
                textColor: config.textColor || '#333333',
                fontSize: config.fontSize || '14px',
                ...config.style
            },
            defaultWidth: widgetType.defaultWidth,
            defaultHeight: widgetType.defaultHeight,
            createdAt: new Date().toISOString()
        };

        console.log(`➕ Created widget: ${type} - ${widget.title}`);
        return widget;
    }

    /**
     * Get widget type definition
     */
    getWidgetType(type) {
        return this.widgetTypes[type] || this.getCustomWidgetType(type);
    }

    /**
     * Get custom widget type
     */
    getCustomWidgetType(type) {
        return this.customWidgets.find(w => w.type === type);
    }

    /**
     * Get all available widget types
     */
    getAllWidgetTypes() {
        return {
            ...this.widgetTypes,
            ...this.customWidgets.reduce((acc, widget) => {
                acc[widget.type] = widget;
                return acc;
            }, {})
        };
    }

    /**
     * Update widget configuration
     */
    updateWidgetConfig(widgetId, newConfig) {
        // This would typically be called from the core module
        console.log(`⚙️ Updated widget config: ${widgetId}`, newConfig);
        return true;
    }

    /**
     * Get widget data
     */
    async getWidgetData(widget) {
        const { dataSource, dataUrl } = widget.config;
        
        try {
            switch (dataSource) {
                case 'api':
                    return await this.fetchApiData(dataUrl);
                case 'static':
                    return widget.config.staticData || [];
                case 'database':
                    return await this.fetchDatabaseData(dataUrl);
                case 'markdown':
                    return widget.config.markdownContent || '';
                case 'url':
                    return dataUrl;
                default:
                    return null;
            }
        } catch (error) {
            console.error(`❌ Error fetching widget data for ${widget.type}:`, error);
            return null;
        }
    }

    /**
     * Fetch data from API
     */
    async fetchApiData(url) {
        const response = await fetch(url);
        if (response.ok) {
            return await response.json();
        } else {
            throw new Error(`API request failed: ${response.status}`);
        }
    }

    /**
     * Fetch data from database
     */
    async fetchDatabaseData(query) {
        const response = await fetch('/api/dashboard-builder/data/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        
        if (response.ok) {
            return await response.json();
        } else {
            throw new Error(`Database query failed: ${response.status}`);
        }
    }

    /**
     * Handle widget drag start
     */
    handleDragStart(event) {
        if (event.target.classList.contains('widget-item')) {
            const widgetType = event.target.dataset.widgetType;
            event.dataTransfer.setData('text/plain', widgetType);
            event.dataTransfer.effectAllowed = 'copy';
            console.log(`🎯 Started dragging widget: ${widgetType}`);
        }
    }

    /**
     * Handle widget drag over
     */
    handleDragOver(event) {
        if (event.target.classList.contains('dashboard-canvas')) {
            event.preventDefault();
            event.dataTransfer.dropEffect = 'copy';
        }
    }

    /**
     * Handle widget drop
     */
    handleDrop(event) {
        if (event.target.classList.contains('dashboard-canvas')) {
            event.preventDefault();
            const widgetType = event.dataTransfer.getData('text/plain');
            
            // Get drop position
            const rect = event.target.getBoundingClientRect();
            const x = Math.floor((event.clientX - rect.left) / (rect.width / 12));
            const y = Math.floor((event.clientY - rect.top) / (rect.height / 8));
            
            console.log(`📥 Dropped widget ${widgetType} at position (${x}, ${y})`);
            
            // Create and add widget
            const widget = this.createWidget(widgetType);
            widget.position = { x, y, width: widget.defaultWidth, height: widget.defaultHeight };
            
            // Dispatch event for core module to handle
            window.dispatchEvent(new CustomEvent('widgetDropped', {
                detail: { widget, position: { x, y } }
            }));
        }
    }

    /**
     * Handle resize start
     */
    handleResizeStart(event) {
        if (event.target.classList.contains('widget-resize-handle')) {
            const widget = event.target.closest('.widget');
            if (widget) {
                this.resizingWidget = {
                    element: widget,
                    startX: event.clientX,
                    startY: event.clientY,
                    startWidth: widget.offsetWidth,
                    startHeight: widget.offsetHeight
                };
                console.log('🔧 Started resizing widget');
            }
        }
    }

    /**
     * Handle resize move
     */
    handleResizeMove(event) {
        if (this.resizingWidget) {
            const deltaX = event.clientX - this.resizingWidget.startX;
            const deltaY = event.clientY - this.resizingWidget.startY;
            
            const newWidth = Math.max(100, this.resizingWidget.startWidth + deltaX);
            const newHeight = Math.max(100, this.resizingWidget.startHeight + deltaY);
            
            this.resizingWidget.element.style.width = newWidth + 'px';
            this.resizingWidget.element.style.height = newHeight + 'px';
        }
    }

    /**
     * Handle resize end
     */
    handleResizeEnd(event) {
        if (this.resizingWidget) {
            const widgetId = this.resizingWidget.element.dataset.widgetId;
            const newWidth = this.resizingWidget.element.offsetWidth;
            const newHeight = this.resizingWidget.element.offsetHeight;
            
            console.log(`📏 Finished resizing widget ${widgetId} to ${newWidth}x${newHeight}`);
            
            // Dispatch event for core module to handle
            window.dispatchEvent(new CustomEvent('widgetResized', {
                detail: { widgetId, width: newWidth, height: newHeight }
            }));
            
            this.resizingWidget = null;
        }
    }

    /**
     * Render widget HTML
     */
    renderWidget(widget) {
        const widgetType = this.getWidgetType(widget.type);
        if (!widgetType) {
            return '<div class="widget-error">Unknown widget type</div>';
        }

        return `
            <div class="widget" data-widget-id="${widget.id}" data-widget-type="${widget.type}">
                <div class="widget-header">
                    <h5 class="widget-title">${widget.title}</h5>
                    <div class="widget-actions">
                        <button class="btn btn-sm btn-outline-secondary widget-settings" title="Settings">
                            <i class="fas fa-cog"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger widget-remove" title="Remove">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
                <div class="widget-content" id="widget-content-${widget.id}">
                    <div class="widget-loading">
                        <i class="fas fa-spinner fa-spin"></i> Loading...
                    </div>
                </div>
                <div class="widget-resize-handle"></div>
            </div>
        `;
    }

    /**
     * Refresh widgets
     */
    async refreshWidgets() {
        await this.loadCustomWidgets();
        console.log('🔄 Widgets refreshed');
    }

    /**
     * Destroy the widgets instance
     */
    destroy() {
        // Remove event listeners
        document.removeEventListener('dragstart', this.handleDragStart);
        document.removeEventListener('dragover', this.handleDragOver);
        document.removeEventListener('drop', this.handleDrop);
        document.removeEventListener('mousedown', this.handleResizeStart);
        document.removeEventListener('mousemove', this.handleResizeMove);
        document.removeEventListener('mouseup', this.handleResizeEnd);
        
        this.isInitialized = false;
        this.customWidgets = [];
        this.resizingWidget = null;
        
        console.log('🧹 Dashboard Widgets Management destroyed');
    }
} 