/**
 * Debounce Manager
 * Handles debouncing functionality for performance optimization
 */

export class DebounceManager {
    constructor() {
        this.isInitialized = false;
        this.debounceTimers = new Map();
    }

    /**
     * Initialize debounce manager
     */
    async init() {
        if (this.isInitialized) return;
        
        console.log('⏱️ Initializing Debounce Manager...');
        
        try {
            this.isInitialized = true;
            console.log('✅ Debounce Manager initialized');
            
        } catch (error) {
            console.error('❌ Debounce Manager initialization failed:', error);
            throw error;
        }
    }

    /**
     * Create debounced function
     */
    create(func, wait, immediate = false) {
        if (!this.isInitialized) {
            console.warn('Debounce Manager not initialized');
            return func;
        }

        let timeout;
        
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func(...args);
            };
            
            const callNow = immediate && !timeout;
            
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            
            if (callNow) func(...args);
        };
    }

    /**
     * Create debounced function with unique key
     */
    createWithKey(key, func, wait, immediate = false) {
        if (!this.isInitialized) {
            console.warn('Debounce Manager not initialized');
            return func;
        }

        // Clear existing timer for this key
        this.clear(key);
        
        // Create new debounced function
        const debouncedFunc = this.create(func, wait, immediate);
        
        // Store timer reference
        this.debounceTimers.set(key, debouncedFunc);
        
        return debouncedFunc;
    }

    /**
     * Clear debounce timer by key
     */
    clear(key) {
        const timer = this.debounceTimers.get(key);
        if (timer) {
            this.debounceTimers.delete(key);
        }
    }

    /**
     * Clear all debounce timers
     */
    clearAll() {
        this.debounceTimers.clear();
    }

    /**
     * Get debounce timer by key
     */
    get(key) {
        return this.debounceTimers.get(key);
    }

    /**
     * Check if debounce timer exists for key
     */
    has(key) {
        return this.debounceTimers.has(key);
    }

    /**
     * Get all debounce timer keys
     */
    getKeys() {
        return Array.from(this.debounceTimers.keys());
    }

    /**
     * Get debounce timer count
     */
    getCount() {
        return this.debounceTimers.size;
    }

    /**
     * Cleanup debounce manager
     */
    destroy() {
        this.clearAll();
        this.isInitialized = false;
        console.log('🧹 Debounce Manager destroyed');
    }
} 