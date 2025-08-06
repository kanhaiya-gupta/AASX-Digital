/**
 * Dashboard Themes Management
 * Handles theme management and styling
 */

export default class DashboardThemes {
    constructor() {
        this.isInitialized = false;
        this.themes = {
            default: {
                name: 'Default Theme',
                description: 'Clean and professional default theme',
                colors: {
                    primary: '#007bff',
                    secondary: '#6c757d',
                    success: '#28a745',
                    danger: '#dc3545',
                    warning: '#ffc107',
                    info: '#17a2b8',
                    light: '#f8f9fa',
                    dark: '#343a40',
                    background: '#ffffff',
                    surface: '#f8f9fa',
                    text: '#212529',
                    textSecondary: '#6c757d',
                    border: '#dee2e6'
                },
                fonts: {
                    primary: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                    secondary: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                    monospace: 'SF Mono, Monaco, Inconsolata, "Roboto Mono", monospace'
                },
                spacing: {
                    xs: '4px',
                    sm: '8px',
                    md: '16px',
                    lg: '24px',
                    xl: '32px'
                },
                borderRadius: {
                    sm: '4px',
                    md: '8px',
                    lg: '12px',
                    xl: '16px'
                },
                shadows: {
                    sm: '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
                    md: '0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23)',
                    lg: '0 10px 20px rgba(0,0,0,0.19), 0 6px 6px rgba(0,0,0,0.23)'
                }
            },
            dark: {
                name: 'Dark Theme',
                description: 'Modern dark theme for reduced eye strain',
                colors: {
                    primary: '#0d6efd',
                    secondary: '#6c757d',
                    success: '#198754',
                    danger: '#dc3545',
                    warning: '#ffc107',
                    info: '#0dcaf0',
                    light: '#212529',
                    dark: '#f8f9fa',
                    background: '#121212',
                    surface: '#1e1e1e',
                    text: '#ffffff',
                    textSecondary: '#b0b0b0',
                    border: '#2d2d2d'
                },
                fonts: {
                    primary: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                    secondary: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                    monospace: 'SF Mono, Monaco, Inconsolata, "Roboto Mono", monospace'
                },
                spacing: {
                    xs: '4px',
                    sm: '8px',
                    md: '16px',
                    lg: '24px',
                    xl: '32px'
                },
                borderRadius: {
                    sm: '4px',
                    md: '8px',
                    lg: '12px',
                    xl: '16px'
                },
                shadows: {
                    sm: '0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.4)',
                    md: '0 3px 6px rgba(0,0,0,0.4), 0 3px 6px rgba(0,0,0,0.5)',
                    lg: '0 10px 20px rgba(0,0,0,0.5), 0 6px 6px rgba(0,0,0,0.6)'
                }
            },
            corporate: {
                name: 'Corporate Theme',
                description: 'Professional corporate theme with blue accents',
                colors: {
                    primary: '#1e3a8a',
                    secondary: '#64748b',
                    success: '#059669',
                    danger: '#dc2626',
                    warning: '#d97706',
                    info: '#0891b2',
                    light: '#f1f5f9',
                    dark: '#0f172a',
                    background: '#ffffff',
                    surface: '#f8fafc',
                    text: '#1e293b',
                    textSecondary: '#64748b',
                    border: '#e2e8f0'
                },
                fonts: {
                    primary: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                    secondary: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                    monospace: 'SF Mono, Monaco, Inconsolata, "Roboto Mono", monospace'
                },
                spacing: {
                    xs: '4px',
                    sm: '8px',
                    md: '16px',
                    lg: '24px',
                    xl: '32px'
                },
                borderRadius: {
                    sm: '2px',
                    md: '4px',
                    lg: '6px',
                    xl: '8px'
                },
                shadows: {
                    sm: '0 1px 2px rgba(0,0,0,0.05)',
                    md: '0 4px 6px rgba(0,0,0,0.1)',
                    lg: '0 10px 15px rgba(0,0,0,0.1)'
                }
            },
            modern: {
                name: 'Modern Theme',
                description: 'Contemporary theme with rounded corners and gradients',
                colors: {
                    primary: '#6366f1',
                    secondary: '#8b5cf6',
                    success: '#10b981',
                    danger: '#ef4444',
                    warning: '#f59e0b',
                    info: '#06b6d4',
                    light: '#f8fafc',
                    dark: '#0f172a',
                    background: '#ffffff',
                    surface: '#f8fafc',
                    text: '#1e293b',
                    textSecondary: '#64748b',
                    border: '#e2e8f0'
                },
                fonts: {
                    primary: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                    secondary: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                    monospace: 'SF Mono, Monaco, Inconsolata, "Roboto Mono", monospace'
                },
                spacing: {
                    xs: '4px',
                    sm: '8px',
                    md: '16px',
                    lg: '24px',
                    xl: '32px'
                },
                borderRadius: {
                    sm: '8px',
                    md: '12px',
                    lg: '16px',
                    xl: '24px'
                },
                shadows: {
                    sm: '0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06)',
                    md: '0 4px 6px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.06)',
                    lg: '0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05)'
                }
            }
        };
        this.currentTheme = 'default';
        this.customThemes = [];
    }

    /**
     * Initialize the Themes Management
     */
    async init() {
        console.log('🔧 Dashboard Themes Management initializing...');
        
        try {
            // Load custom themes
            await this.loadCustomThemes();
            
            // Apply default theme
            this.applyTheme(this.currentTheme);
            
            // Set up theme event handlers
            this.setupEventHandlers();
            
            this.isInitialized = true;
            console.log('✅ Dashboard Themes Management initialized');
            
        } catch (error) {
            console.error('❌ Dashboard Themes Management initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load custom themes from server
     */
    async loadCustomThemes() {
        try {
            const response = await fetch('/api/dashboard-builder/themes/custom');
            if (response.ok) {
                this.customThemes = await response.json();
                // Merge custom themes with built-in themes
                this.customThemes.forEach(theme => {
                    this.themes[theme.id] = theme;
                });
                console.log(`📦 Loaded ${this.customThemes.length} custom themes`);
            }
        } catch (error) {
            console.warn('⚠️ Could not load custom themes:', error);
            this.customThemes = [];
        }
    }

    /**
     * Setup event handlers for theme interactions
     */
    setupEventHandlers() {
        // Theme change events
        document.addEventListener('themeChanged', this.handleThemeChange.bind(this));
        
        // Color scheme preference changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', this.handleColorSchemeChange.bind(this));
        
        console.log('🎯 Theme event handlers registered');
    }

    /**
     * Apply theme to dashboard
     */
    applyTheme(themeName) {
        const theme = this.themes[themeName];
        if (!theme) {
            console.warn(`⚠️ Theme not found: ${themeName}, falling back to default`);
            themeName = 'default';
            theme = this.themes[themeName];
        }

        this.currentTheme = themeName;
        
        // Generate CSS variables
        const cssVariables = this.generateCSSVariables(theme);
        
        // Apply to document root
        this.applyCSSVariables(cssVariables);
        
        // Update theme-specific classes
        this.updateThemeClasses(themeName);
        
        // Dispatch theme change event
        window.dispatchEvent(new CustomEvent('themeApplied', {
            detail: { theme: themeName, themeData: theme }
        }));
        
        console.log(`🎨 Applied theme: ${theme.name}`);
    }

    /**
     * Generate CSS variables from theme
     */
    generateCSSVariables(theme) {
        const variables = {};
        
        // Color variables
        Object.entries(theme.colors).forEach(([key, value]) => {
            variables[`--color-${key}`] = value;
        });
        
        // Font variables
        Object.entries(theme.fonts).forEach(([key, value]) => {
            variables[`--font-${key}`] = value;
        });
        
        // Spacing variables
        Object.entries(theme.spacing).forEach(([key, value]) => {
            variables[`--spacing-${key}`] = value;
        });
        
        // Border radius variables
        Object.entries(theme.borderRadius).forEach(([key, value]) => {
            variables[`--radius-${key}`] = value;
        });
        
        // Shadow variables
        Object.entries(theme.shadows).forEach(([key, value]) => {
            variables[`--shadow-${key}`] = value;
        });
        
        return variables;
    }

    /**
     * Apply CSS variables to document
     */
    applyCSSVariables(variables) {
        const root = document.documentElement;
        
        Object.entries(variables).forEach(([property, value]) => {
            root.style.setProperty(property, value);
        });
    }

    /**
     * Update theme-specific classes
     */
    updateThemeClasses(themeName) {
        // Remove existing theme classes
        document.body.classList.remove('theme-default', 'theme-dark', 'theme-corporate', 'theme-modern');
        
        // Add new theme class
        document.body.classList.add(`theme-${themeName}`);
        
        // Update dashboard containers
        const dashboardContainers = document.querySelectorAll('.dashboard-layout');
        dashboardContainers.forEach(container => {
            container.classList.remove('theme-default', 'theme-dark', 'theme-corporate', 'theme-modern');
            container.classList.add(`theme-${themeName}`);
        });
    }

    /**
     * Create custom theme
     */
    async createCustomTheme(themeData) {
        const theme = {
            id: this.generateThemeId(),
            name: themeData.name,
            description: themeData.description,
            colors: { ...this.themes.default.colors, ...themeData.colors },
            fonts: { ...this.themes.default.fonts, ...themeData.fonts },
            spacing: { ...this.themes.default.spacing, ...themeData.spacing },
            borderRadius: { ...this.themes.default.borderRadius, ...themeData.borderRadius },
            shadows: { ...this.themes.default.shadows, ...themeData.shadows },
            isCustom: true,
            createdAt: new Date().toISOString()
        };

        try {
            const response = await fetch('/api/dashboard-builder/themes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(theme)
            });

            if (response.ok) {
                this.themes[theme.id] = theme;
                this.customThemes.push(theme);
                console.log(`✅ Created custom theme: ${theme.name}`);
                return theme;
            } else {
                throw new Error('Failed to create custom theme');
            }
        } catch (error) {
            console.error('❌ Error creating custom theme:', error);
            throw error;
        }
    }

    /**
     * Update custom theme
     */
    async updateCustomTheme(themeId, updates) {
        const theme = this.themes[themeId];
        if (!theme || !theme.isCustom) {
            throw new Error('Theme not found or not custom');
        }

        const updatedTheme = { ...theme, ...updates, updatedAt: new Date().toISOString() };

        try {
            const response = await fetch(`/api/dashboard-builder/themes/${themeId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updatedTheme)
            });

            if (response.ok) {
                this.themes[themeId] = updatedTheme;
                console.log(`✅ Updated custom theme: ${updatedTheme.name}`);
                return updatedTheme;
            } else {
                throw new Error('Failed to update custom theme');
            }
        } catch (error) {
            console.error('❌ Error updating custom theme:', error);
            throw error;
        }
    }

    /**
     * Delete custom theme
     */
    async deleteCustomTheme(themeId) {
        const theme = this.themes[themeId];
        if (!theme || !theme.isCustom) {
            throw new Error('Theme not found or not custom');
        }

        try {
            const response = await fetch(`/api/dashboard-builder/themes/${themeId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                delete this.themes[themeId];
                this.customThemes = this.customThemes.filter(t => t.id !== themeId);
                
                // Switch to default theme if current theme was deleted
                if (this.currentTheme === themeId) {
                    this.applyTheme('default');
                }
                
                console.log(`🗑️ Deleted custom theme: ${theme.name}`);
                return true;
            } else {
                throw new Error('Failed to delete custom theme');
            }
        } catch (error) {
            console.error('❌ Error deleting custom theme:', error);
            throw error;
        }
    }

    /**
     * Export theme as CSS
     */
    exportThemeAsCSS(themeName) {
        const theme = this.themes[themeName];
        if (!theme) {
            throw new Error(`Theme not found: ${themeName}`);
        }

        const cssVariables = this.generateCSSVariables(theme);
        let css = `/* ${theme.name} Theme */\n`;
        css += `/* ${theme.description} */\n\n`;
        css += `:root {\n`;
        
        Object.entries(cssVariables).forEach(([property, value]) => {
            css += `  ${property}: ${value};\n`;
        });
        
        css += `}\n\n`;
        css += `/* Theme-specific styles */\n`;
        css += `.theme-${themeName} {\n`;
        css += `  background-color: var(--color-background);\n`;
        css += `  color: var(--color-text);\n`;
        css += `  font-family: var(--font-primary);\n`;
        css += `}\n`;

        return css;
    }

    /**
     * Import theme from CSS
     */
    async importThemeFromCSS(cssContent, themeName) {
        // Parse CSS and extract variables
        const variables = this.parseCSSVariables(cssContent);
        
        // Create theme object
        const themeData = {
            name: themeName,
            description: `Imported theme: ${themeName}`,
            colors: this.extractColorsFromVariables(variables),
            fonts: this.extractFontsFromVariables(variables),
            spacing: this.extractSpacingFromVariables(variables),
            borderRadius: this.extractBorderRadiusFromVariables(variables),
            shadows: this.extractShadowsFromVariables(variables)
        };

        return await this.createCustomTheme(themeData);
    }

    /**
     * Parse CSS variables from CSS content
     */
    parseCSSVariables(cssContent) {
        const variables = {};
        const regex = /--([^:]+):\s*([^;]+);/g;
        let match;
        
        while ((match = regex.exec(cssContent)) !== null) {
            variables[match[1]] = match[2].trim();
        }
        
        return variables;
    }

    /**
     * Extract colors from CSS variables
     */
    extractColorsFromVariables(variables) {
        const colors = {};
        Object.entries(variables).forEach(([key, value]) => {
            if (key.startsWith('color-')) {
                const colorName = key.replace('color-', '');
                colors[colorName] = value;
            }
        });
        return colors;
    }

    /**
     * Extract fonts from CSS variables
     */
    extractFontsFromVariables(variables) {
        const fonts = {};
        Object.entries(variables).forEach(([key, value]) => {
            if (key.startsWith('font-')) {
                const fontName = key.replace('font-', '');
                fonts[fontName] = value;
            }
        });
        return fonts;
    }

    /**
     * Extract spacing from CSS variables
     */
    extractSpacingFromVariables(variables) {
        const spacing = {};
        Object.entries(variables).forEach(([key, value]) => {
            if (key.startsWith('spacing-')) {
                const spacingName = key.replace('spacing-', '');
                spacing[spacingName] = value;
            }
        });
        return spacing;
    }

    /**
     * Extract border radius from CSS variables
     */
    extractBorderRadiusFromVariables(variables) {
        const borderRadius = {};
        Object.entries(variables).forEach(([key, value]) => {
            if (key.startsWith('radius-')) {
                const radiusName = key.replace('radius-', '');
                borderRadius[radiusName] = value;
            }
        });
        return borderRadius;
    }

    /**
     * Extract shadows from CSS variables
     */
    extractShadowsFromVariables(variables) {
        const shadows = {};
        Object.entries(variables).forEach(([key, value]) => {
            if (key.startsWith('shadow-')) {
                const shadowName = key.replace('shadow-', '');
                shadows[shadowName] = value;
            }
        });
        return shadows;
    }

    /**
     * Generate unique theme ID
     */
    generateThemeId() {
        return 'theme_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Handle theme change
     */
    handleThemeChange(event) {
        const { themeName } = event.detail;
        this.applyTheme(themeName);
    }

    /**
     * Handle color scheme change
     */
    handleColorSchemeChange(event) {
        const prefersDark = event.matches;
        
        // Auto-switch to dark theme if user prefers dark mode
        if (prefersDark && this.currentTheme === 'default') {
            this.applyTheme('dark');
        } else if (!prefersDark && this.currentTheme === 'dark') {
            this.applyTheme('default');
        }
    }

    /**
     * Get all themes
     */
    getAllThemes() {
        return this.themes;
    }

    /**
     * Get current theme
     */
    getCurrentTheme() {
        return this.currentTheme;
    }

    /**
     * Get theme data
     */
    getThemeData(themeName) {
        return this.themes[themeName];
    }

    /**
     * Get custom themes
     */
    getCustomThemes() {
        return this.customThemes;
    }

    /**
     * Refresh themes
     */
    async refreshThemes() {
        await this.loadCustomThemes();
        console.log('🔄 Themes refreshed');
    }

    /**
     * Destroy the themes instance
     */
    destroy() {
        // Remove event listeners
        document.removeEventListener('themeChanged', this.handleThemeChange);
        
        this.isInitialized = false;
        this.currentTheme = 'default';
        this.customThemes = [];
        
        console.log('🧹 Dashboard Themes Management destroyed');
    }
} 