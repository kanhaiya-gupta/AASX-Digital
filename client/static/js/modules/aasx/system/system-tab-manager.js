/**
 * System Tab Manager for AASX-ETL Frontend
 * 
 * This module manages the system sub-tabs with custom JavaScript handling
 * to prevent navigation issues and ensure proper tab visibility.
 * 
 * Phase 6: System Monitoring & Management
 */

class SystemTabManager {
    constructor() {
        this.isInitialized = false;
        this.currentTab = 'system_overview';
        this.systemSection = null;
    }

    /**
     * Initialize the system tab manager
     */
    async init() {
        if (this.isInitialized) {
            console.log('⚠️ System Tab Manager already initialized, skipping...');
            return;
        }

        console.log('🔄 System Tab Manager initializing...');

        try {
            // Wait for system section to be available in DOM
            await this.waitForSystemSection();
            
            // Ensure initial tab is visible
            this.ensureInitialTabVisible();
            
            // Set up tab switching
            this.setupTabSwitching();
            
            this.isInitialized = true;
            console.log('✅ System Tab Manager initialized successfully');
            
        } catch (error) {
            console.error('❌ Failed to initialize System Tab Manager:', error);
            this.isInitialized = false;
        }
    }

    /**
     * Wait for system section to be available in DOM
     */
    async waitForSystemSection() {
        console.log('⏳ Waiting for system section...');
        
        let attempts = 0;
        const maxAttempts = 50; // 5 seconds max wait
        
        while (!document.querySelector('.aasx-system-section') && attempts < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, 100));
            attempts++;
        }
        
        if (attempts >= maxAttempts) {
            throw new Error('System section not found after 5 seconds');
        }
        
        this.systemSection = document.querySelector('.aasx-system-section');
        console.log(`✅ System section available after ${attempts * 100}ms`);
        
        // Additional wait to ensure sub-tabs are loaded
        await new Promise(resolve => setTimeout(resolve, 200));
    }

    /**
     * Ensure the initial tab is visible (fixes Bootstrap CSS visibility issue)
     */
    ensureInitialTabVisible() {
        console.log('🔍 System: Ensuring initial tab is visible...');
        
        // CRITICAL FIX: Force system sub-tab buttons to be visible
        let subTabButtons = document.querySelectorAll('.aasx-system-tabs .nav-link');
        console.log(`🔍 System: Found ${subTabButtons.length} system sub-tab buttons`);
        
        // If no sub-tabs found, wait a bit and try again
        if (subTabButtons.length === 0) {
            console.log('🔍 System: No sub-tabs found, waiting and retrying...');
            setTimeout(() => {
                this.ensureInitialTabVisible();
            }, 500);
            return;
        }
        
        subTabButtons.forEach((button, index) => {
            // Force visibility with inline styles - OVERRIDE ALL CSS
            button.style.display = 'inline-block !important';
            button.style.visibility = 'visible !important';
            button.style.opacity = '1 !important';
            button.style.color = '#6c757d !important'; // Ensure text color is visible
            button.style.fontSize = '14px !important'; // Ensure font size is visible
            button.style.fontWeight = '500 !important'; // Ensure font weight is visible
            button.style.textDecoration = 'none !important'; // Remove any text decoration
            
            // Force the text content to be visible
            const textContent = button.textContent.trim();
            console.log(`🔍 System: Button ${index + 1} - "${textContent}" - Made visible with inline styles`);
            
            // Additional check: if text is empty, try to get it from innerHTML
            if (!textContent) {
                const innerHTML = button.innerHTML;
                console.log(`🔍 System: Button ${index + 1} innerHTML: ${innerHTML}`);
            }
        });
        
        // Get all SYSTEM tab panes (not main AASX tabs)
        const allSystemTabPanes = document.querySelectorAll('.aasx-system-section .tab-pane');
        console.log(`🔍 System: Found ${allSystemTabPanes.length} system tab panes:`, Array.from(allSystemTabPanes).map(pane => ({
            id: pane.id,
            classes: pane.className
        })));
        
        // Get the first system tab pane (should be system_overview)
        const firstSystemTabPane = document.querySelector('.aasx-system-section .tab-pane');
        if (firstSystemTabPane) {
            console.log(`🔍 System: First system tab pane: ${firstSystemTabPane.id}`);
            console.log(`🔍 System: Before fix - classes: ${firstSystemTabPane.className}`);
            
            // Ensure it has the correct classes for visibility
            firstSystemTabPane.classList.add('active', 'show');
            
            console.log(`🔍 System: After fix - classes: ${firstSystemTabPane.className}`);
            console.log(`✅ System: Initial system tab made visible: ${firstSystemTabPane.id}`);
        } else {
            console.warn('⚠️ System: No system tab panes found for initial visibility');
        }
        
        // Log final state of system tab panes only
        console.log(`🔍 System: Final system tab pane states:`, Array.from(allSystemTabPanes).map(pane => ({
            id: pane.id,
            classes: pane.className
        })));
    }

    /**
     * Set up tab switching functionality
     */
    setupTabSwitching() {
        const tabButtons = document.querySelectorAll('.aasx-system-section [data-tab]');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', async (e) => {
                e.preventDefault();
                
                const tabName = button.getAttribute('data-tab');
                if (!tabName) return;
                
                console.log(`🔄 Switching to system tab: ${tabName}`);
                
                this.currentTab = tabName;
                
                // Update active tab styling
                this.updateActiveTab(tabName);
                
                // Show the corresponding tab content
                this.showTabContent(tabName);
                
                console.log(`✅ System tab switch to ${tabName} completed`);
            });
        });
    }
    
    /**
     * Update active tab styling
     */
    updateActiveTab(activeTabName) {
        // Remove active class from all tabs
        document.querySelectorAll('.aasx-system-section [data-tab]').forEach(button => {
            button.classList.remove('active');
        });
        
        // Add active class to clicked tab
        const activeButton = document.querySelector(`[data-tab="${activeTabName}"]`);
        if (activeButton) {
            activeButton.classList.add('active');
        }
    }
    
    /**
     * Show tab content for specific tab
     */
    showTabContent(tabName) {
        console.log(`🔍 Showing system tab content for: ${tabName}`);
        
        // Debug: Log all SYSTEM tab panes (not main AASX tabs)
        const allSystemPanes = document.querySelectorAll('.aasx-system-section .tab-pane');
        console.log(`🔍 Found ${allSystemPanes.length} system tab panes:`, Array.from(allSystemPanes).map(pane => ({
            id: pane.id,
            classes: pane.className,
            visible: pane.classList.contains('active')
        })));
        
        // Hide all SYSTEM tab content by removing active/show classes
        // CRITICAL: Only target system sub-tabs, not main AASX tabs
        document.querySelectorAll('.aasx-system-section .tab-pane').forEach(pane => {
            pane.classList.remove('active', 'show');
            console.log(`🔍 Hidden system tab pane: ${pane.id}`);
        });
        
        // Show the selected system tab content
        const targetPane = document.getElementById(tabName);
        if (targetPane) {
            // Add classes for visibility and transitions
            targetPane.classList.add('active', 'show');
            
            console.log(`✅ System tab content shown for: ${tabName}`);
            console.log(`🔍 Target pane classes after: ${targetPane.className}`);
        } else {
            console.warn(`⚠️ System tab content not found for: ${tabName}`);
        }
        
        // Debug: Log final state of system tab panes only
        console.log(`🔍 Final system tab pane states:`, Array.from(allSystemPanes).map(pane => ({
            id: pane.id,
            classes: pane.className,
            visible: pane.classList.contains('active')
        })));
    }

    /**
     * Cleanup resources
     */
    destroy() {
        this.isInitialized = false;
        console.log('🗑️ System Tab Manager destroyed');
    }
}

// Export for use in other modules
window.SystemTabManager = SystemTabManager;


