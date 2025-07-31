/**
 * Dashboard Layouts Management
 * Handles different layout types and grid systems
 */

export default class DashboardLayouts {
    constructor() {
        this.isInitialized = false;
        this.layoutTypes = {
            grid: {
                name: 'Grid Layout',
                icon: 'fas fa-th',
                description: 'Responsive grid-based layout',
                supports: ['responsive', 'drag-drop', 'resize'],
                defaultColumns: 12,
                breakpoints: {
                    xs: 0,
                    sm: 576,
                    md: 768,
                    lg: 992,
                    xl: 1200
                }
            },
            flex: {
                name: 'Flex Layout',
                icon: 'fas fa-boxes',
                description: 'Flexible box-based layout',
                supports: ['flexible', 'auto-size', 'wrap'],
                defaultDirection: 'row',
                wrap: true
            },
            masonry: {
                name: 'Masonry Layout',
                icon: 'fas fa-bars',
                description: 'Pinterest-style masonry layout',
                supports: ['auto-height', 'responsive', 'gaps'],
                columns: 3,
                gap: 16
            },
            carousel: {
                name: 'Carousel Layout',
                icon: 'fas fa-images',
                description: 'Sliding carousel layout',
                supports: ['slides', 'navigation', 'auto-play'],
                slidesToShow: 3,
                autoPlay: false
            },
            tabs: {
                name: 'Tabs Layout',
                icon: 'fas fa-folder',
                description: 'Tabbed content layout',
                supports: ['tabs', 'content-switching', 'responsive'],
                defaultTab: 0,
                tabPosition: 'top'
            },
            accordion: {
                name: 'Accordion Layout',
                icon: 'fas fa-list',
                description: 'Collapsible accordion layout',
                supports: ['collapse', 'expand', 'multiple'],
                allowMultiple: false,
                defaultExpanded: []
            }
        };
        this.currentLayout = null;
        this.layoutInstances = new Map();
    }

    /**
     * Initialize the Layouts Management
     */
    async init() {
        console.log('🔧 Dashboard Layouts Management initializing...');
        
        try {
            // Load custom layouts
            await this.loadCustomLayouts();
            
            // Initialize default layout
            this.currentLayout = this.layoutTypes.grid;
            
            // Set up layout event handlers
            this.setupEventHandlers();
            
            this.isInitialized = true;
            console.log('✅ Dashboard Layouts Management initialized');
            
        } catch (error) {
            console.error('❌ Dashboard Layouts Management initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load custom layouts from server
     */
    async loadCustomLayouts() {
        try {
            const response = await fetch('/api/dashboard-builder/layouts/custom');
            if (response.ok) {
                const customLayouts = await response.json();
                Object.assign(this.layoutTypes, customLayouts);
                console.log(`📦 Loaded ${Object.keys(customLayouts).length} custom layouts`);
            }
        } catch (error) {
            console.warn('⚠️ Could not load custom layouts:', error);
        }
    }

    /**
     * Setup event handlers for layout interactions
     */
    setupEventHandlers() {
        // Layout change events
        document.addEventListener('layoutChanged', this.handleLayoutChange.bind(this));
        
        // Responsive breakpoint changes
        window.addEventListener('resize', this.handleResize.bind(this));
        
        // Layout-specific events
        document.addEventListener('tabChanged', this.handleTabChange.bind(this));
        document.addEventListener('accordionToggle', this.handleAccordionToggle.bind(this));
        
        console.log('🎯 Layout event handlers registered');
    }

    /**
     * Apply layout to dashboard
     */
    applyLayout(layoutType, container, widgets = []) {
        const layout = this.layoutTypes[layoutType];
        if (!layout) {
            throw new Error(`Unknown layout type: ${layoutType}`);
        }

        // Clear existing layout
        this.clearLayout(container);
        
        // Apply new layout
        switch (layoutType) {
            case 'grid':
                return this.applyGridLayout(container, widgets, layout);
            case 'flex':
                return this.applyFlexLayout(container, widgets, layout);
            case 'masonry':
                return this.applyMasonryLayout(container, widgets, layout);
            case 'carousel':
                return this.applyCarouselLayout(container, widgets, layout);
            case 'tabs':
                return this.applyTabsLayout(container, widgets, layout);
            case 'accordion':
                return this.applyAccordionLayout(container, widgets, layout);
            default:
                return this.applyCustomLayout(container, widgets, layout);
        }
    }

    /**
     * Apply grid layout
     */
    applyGridLayout(container, widgets, layout) {
        container.className = 'dashboard-layout grid-layout';
        container.style.display = 'grid';
        container.style.gridTemplateColumns = `repeat(${layout.defaultColumns}, 1fr)`;
        container.style.gap = '16px';
        container.style.padding = '16px';

        widgets.forEach(widget => {
            const widgetElement = this.createWidgetElement(widget);
            widgetElement.style.gridColumn = `span ${widget.position?.width || widget.defaultWidth || 2}`;
            widgetElement.style.gridRow = `span ${widget.position?.height || widget.defaultHeight || 2}`;
            container.appendChild(widgetElement);
        });

        this.currentLayout = layout;
        console.log('📐 Applied grid layout');
        return container;
    }

    /**
     * Apply flex layout
     */
    applyFlexLayout(container, widgets, layout) {
        container.className = 'dashboard-layout flex-layout';
        container.style.display = 'flex';
        container.style.flexDirection = layout.defaultDirection || 'row';
        container.style.flexWrap = layout.wrap ? 'wrap' : 'nowrap';
        container.style.gap = '16px';
        container.style.padding = '16px';

        widgets.forEach(widget => {
            const widgetElement = this.createWidgetElement(widget);
            widgetElement.style.flex = `1 1 ${widget.position?.width || widget.defaultWidth || 200}px`;
            widgetElement.style.minHeight = `${widget.position?.height || widget.defaultHeight || 150}px`;
            container.appendChild(widgetElement);
        });

        this.currentLayout = layout;
        console.log('📐 Applied flex layout');
        return container;
    }

    /**
     * Apply masonry layout
     */
    applyMasonryLayout(container, widgets, layout) {
        container.className = 'dashboard-layout masonry-layout';
        container.style.columnCount = layout.columns;
        container.style.columnGap = `${layout.gap}px`;
        container.style.padding = '16px';

        widgets.forEach(widget => {
            const widgetElement = this.createWidgetElement(widget);
            widgetElement.style.breakInside = 'avoid';
            widgetElement.style.marginBottom = `${layout.gap}px`;
            container.appendChild(widgetElement);
        });

        this.currentLayout = layout;
        console.log('📐 Applied masonry layout');
        return container;
    }

    /**
     * Apply carousel layout
     */
    applyCarouselLayout(container, widgets, layout) {
        container.className = 'dashboard-layout carousel-layout';
        container.style.display = 'flex';
        container.style.overflow = 'hidden';
        container.style.position = 'relative';
        container.style.padding = '16px';

        const carouselContainer = document.createElement('div');
        carouselContainer.className = 'carousel-container';
        carouselContainer.style.display = 'flex';
        carouselContainer.style.transition = 'transform 0.3s ease';

        widgets.forEach((widget, index) => {
            const widgetElement = this.createWidgetElement(widget);
            widgetElement.style.flex = `0 0 ${100 / layout.slidesToShow}%`;
            widgetElement.style.marginRight = '16px';
            carouselContainer.appendChild(widgetElement);
        });

        container.appendChild(carouselContainer);

        // Add navigation controls
        if (widgets.length > layout.slidesToShow) {
            this.addCarouselNavigation(container, carouselContainer, widgets.length, layout);
        }

        this.currentLayout = layout;
        console.log('📐 Applied carousel layout');
        return container;
    }

    /**
     * Apply tabs layout
     */
    applyTabsLayout(container, widgets, layout) {
        container.className = 'dashboard-layout tabs-layout';
        container.style.padding = '16px';

        const tabsContainer = document.createElement('div');
        tabsContainer.className = 'tabs-container';

        const tabList = document.createElement('div');
        tabList.className = 'tab-list';
        tabList.style.display = 'flex';
        tabList.style.borderBottom = '1px solid #ddd';
        tabList.style.marginBottom = '16px';

        const tabContent = document.createElement('div');
        tabContent.className = 'tab-content';

        widgets.forEach((widget, index) => {
            // Create tab button
            const tabButton = document.createElement('button');
            tabButton.className = `tab-button ${index === layout.defaultTab ? 'active' : ''}`;
            tabButton.textContent = widget.title || `Tab ${index + 1}`;
            tabButton.style.padding = '8px 16px';
            tabButton.style.border = 'none';
            tabButton.style.background = index === layout.defaultTab ? '#007bff' : 'transparent';
            tabButton.style.color = index === layout.defaultTab ? 'white' : '#333';
            tabButton.style.cursor = 'pointer';
            tabButton.onclick = () => this.switchTab(tabContent, widgets, index);

            tabList.appendChild(tabButton);

            // Create tab content
            const tabPanel = document.createElement('div');
            tabPanel.className = `tab-panel ${index === layout.defaultTab ? 'active' : ''}`;
            tabPanel.style.display = index === layout.defaultTab ? 'block' : 'none';
            
            const widgetElement = this.createWidgetElement(widget);
            tabPanel.appendChild(widgetElement);
            tabContent.appendChild(tabPanel);
        });

        tabsContainer.appendChild(tabList);
        tabsContainer.appendChild(tabContent);
        container.appendChild(tabsContainer);

        this.currentLayout = layout;
        console.log('📐 Applied tabs layout');
        return container;
    }

    /**
     * Apply accordion layout
     */
    applyAccordionLayout(container, widgets, layout) {
        container.className = 'dashboard-layout accordion-layout';
        container.style.padding = '16px';

        widgets.forEach((widget, index) => {
            const accordionItem = document.createElement('div');
            accordionItem.className = 'accordion-item';
            accordionItem.style.border = '1px solid #ddd';
            accordionItem.style.marginBottom = '8px';

            const accordionHeader = document.createElement('div');
            accordionHeader.className = 'accordion-header';
            accordionHeader.textContent = widget.title || `Section ${index + 1}`;
            accordionHeader.style.padding = '12px 16px';
            accordionHeader.style.background = '#f8f9fa';
            accordionHeader.style.cursor = 'pointer';
            accordionHeader.style.fontWeight = 'bold';
            accordionHeader.onclick = () => this.toggleAccordion(accordionContent, accordionHeader);

            const accordionContent = document.createElement('div');
            accordionContent.className = 'accordion-content';
            accordionContent.style.padding = '16px';
            accordionContent.style.display = layout.defaultExpanded.includes(index) ? 'block' : 'none';

            const widgetElement = this.createWidgetElement(widget);
            accordionContent.appendChild(widgetElement);

            accordionItem.appendChild(accordionHeader);
            accordionItem.appendChild(accordionContent);
            container.appendChild(accordionItem);
        });

        this.currentLayout = layout;
        console.log('📐 Applied accordion layout');
        return container;
    }

    /**
     * Apply custom layout
     */
    applyCustomLayout(container, widgets, layout) {
        container.className = `dashboard-layout custom-layout ${layout.type}`;
        
        // Apply custom CSS if provided
        if (layout.styles) {
            Object.assign(container.style, layout.styles);
        }

        // Apply custom rendering logic if provided
        if (layout.render) {
            layout.render(container, widgets);
        } else {
            // Default fallback to grid
            this.applyGridLayout(container, widgets, this.layoutTypes.grid);
        }

        this.currentLayout = layout;
        console.log(`📐 Applied custom layout: ${layout.name}`);
        return container;
    }

    /**
     * Create widget element
     */
    createWidgetElement(widget) {
        const element = document.createElement('div');
        element.className = 'widget-container';
        element.dataset.widgetId = widget.id;
        element.dataset.widgetType = widget.type;
        element.innerHTML = `
            <div class="widget" style="
                background-color: ${widget.style?.backgroundColor || '#ffffff'};
                border: 1px solid ${widget.style?.borderColor || '#e0e0e0'};
                border-radius: 4px;
                padding: 12px;
                height: 100%;
            ">
                <div class="widget-header">
                    <h5 style="margin: 0; color: ${widget.style?.textColor || '#333333'}; font-size: ${widget.style?.fontSize || '14px'};">${widget.title}</h5>
                </div>
                <div class="widget-content">
                    <div class="widget-placeholder">
                        <i class="fas fa-cube"></i>
                        <p>${widget.type} Widget</p>
                    </div>
                </div>
            </div>
        `;
        return element;
    }

    /**
     * Add carousel navigation
     */
    addCarouselNavigation(container, carouselContainer, totalWidgets, layout) {
        const navigation = document.createElement('div');
        navigation.className = 'carousel-navigation';
        navigation.style.position = 'absolute';
        navigation.style.top = '50%';
        navigation.style.transform = 'translateY(-50%)';
        navigation.style.width = '100%';
        navigation.style.display = 'flex';
        navigation.style.justifyContent = 'space-between';
        navigation.style.padding = '0 16px';
        navigation.style.pointerEvents = 'none';

        const prevButton = document.createElement('button');
        prevButton.innerHTML = '<i class="fas fa-chevron-left"></i>';
        prevButton.className = 'btn btn-sm btn-outline-primary';
        prevButton.style.pointerEvents = 'auto';
        prevButton.onclick = () => this.navigateCarousel(carouselContainer, -1, totalWidgets, layout);

        const nextButton = document.createElement('button');
        nextButton.innerHTML = '<i class="fas fa-chevron-right"></i>';
        nextButton.className = 'btn btn-sm btn-outline-primary';
        nextButton.style.pointerEvents = 'auto';
        nextButton.onclick = () => this.navigateCarousel(carouselContainer, 1, totalWidgets, layout);

        navigation.appendChild(prevButton);
        navigation.appendChild(nextButton);
        container.appendChild(navigation);
    }

    /**
     * Navigate carousel
     */
    navigateCarousel(carouselContainer, direction, totalWidgets, layout) {
        const currentIndex = parseInt(carouselContainer.dataset.currentIndex || '0');
        const maxIndex = Math.max(0, totalWidgets - layout.slidesToShow);
        const newIndex = Math.max(0, Math.min(maxIndex, currentIndex + direction));
        
        carouselContainer.dataset.currentIndex = newIndex;
        carouselContainer.style.transform = `translateX(-${newIndex * (100 / layout.slidesToShow)}%)`;
    }

    /**
     * Switch tab
     */
    switchTab(tabContent, widgets, tabIndex) {
        const tabPanels = tabContent.querySelectorAll('.tab-panel');
        const tabButtons = document.querySelectorAll('.tab-button');

        tabPanels.forEach((panel, index) => {
            panel.style.display = index === tabIndex ? 'block' : 'none';
        });

        tabButtons.forEach((button, index) => {
            button.classList.toggle('active', index === tabIndex);
            button.style.background = index === tabIndex ? '#007bff' : 'transparent';
            button.style.color = index === tabIndex ? 'white' : '#333';
        });

        // Dispatch event
        window.dispatchEvent(new CustomEvent('tabChanged', { detail: { tabIndex } }));
    }

    /**
     * Toggle accordion
     */
    toggleAccordion(content, header) {
        const isExpanded = content.style.display === 'block';
        content.style.display = isExpanded ? 'none' : 'block';
        header.style.background = isExpanded ? '#f8f9fa' : '#e9ecef';

        // Dispatch event
        window.dispatchEvent(new CustomEvent('accordionToggle', { 
            detail: { 
                widgetId: content.querySelector('.widget-container')?.dataset.widgetId,
                expanded: !isExpanded 
            } 
        }));
    }

    /**
     * Clear layout
     */
    clearLayout(container) {
        container.innerHTML = '';
        container.className = '';
        container.style = '';
    }

    /**
     * Handle layout change
     */
    handleLayoutChange(event) {
        const { layoutType, container, widgets } = event.detail;
        this.applyLayout(layoutType, container, widgets);
    }

    /**
     * Handle resize
     */
    handleResize() {
        // Trigger responsive updates if needed
        if (this.currentLayout && this.currentLayout.supports?.includes('responsive')) {
            this.updateResponsiveLayout();
        }
    }

    /**
     * Handle tab change
     */
    handleTabChange(event) {
        console.log('📑 Tab changed:', event.detail);
    }

    /**
     * Handle accordion toggle
     */
    handleAccordionToggle(event) {
        console.log('📋 Accordion toggled:', event.detail);
    }

    /**
     * Update responsive layout
     */
    updateResponsiveLayout() {
        const width = window.innerWidth;
        const breakpoints = this.currentLayout.breakpoints;

        if (breakpoints) {
            let currentBreakpoint = 'xs';
            for (const [breakpoint, minWidth] of Object.entries(breakpoints)) {
                if (width >= minWidth) {
                    currentBreakpoint = breakpoint;
                }
            }

            // Apply responsive adjustments
            this.applyResponsiveAdjustments(currentBreakpoint);
        }
    }

    /**
     * Apply responsive adjustments
     */
    applyResponsiveAdjustments(breakpoint) {
        const containers = document.querySelectorAll('.dashboard-layout');
        containers.forEach(container => {
            if (container.classList.contains('grid-layout')) {
                const columns = this.getResponsiveColumns(breakpoint);
                container.style.gridTemplateColumns = `repeat(${columns}, 1fr)`;
            }
        });
    }

    /**
     * Get responsive columns
     */
    getResponsiveColumns(breakpoint) {
        const columnMap = {
            xs: 1,
            sm: 2,
            md: 4,
            lg: 6,
            xl: 12
        };
        return columnMap[breakpoint] || 12;
    }

    /**
     * Get layout types
     */
    getLayoutTypes() {
        return this.layoutTypes;
    }

    /**
     * Get current layout
     */
    getCurrentLayout() {
        return this.currentLayout;
    }

    /**
     * Refresh layouts
     */
    async refreshLayouts() {
        await this.loadCustomLayouts();
        console.log('🔄 Layouts refreshed');
    }

    /**
     * Destroy the layouts instance
     */
    destroy() {
        // Remove event listeners
        document.removeEventListener('layoutChanged', this.handleLayoutChange);
        window.removeEventListener('resize', this.handleResize);
        document.removeEventListener('tabChanged', this.handleTabChange);
        document.removeEventListener('accordionToggle', this.handleAccordionToggle);
        
        this.isInitialized = false;
        this.currentLayout = null;
        this.layoutInstances.clear();
        
        console.log('🧹 Dashboard Layouts Management destroyed');
    }
} 