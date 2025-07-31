# CSS Architecture Documentation

## Overview
This directory contains modular CSS files for the AASX Data Management & Processing system. The CSS is organized into separate files for better maintainability and reusability.

## File Structure

### Core CSS Files

#### `data-management.css`
**Purpose**: Styles for the Data Management interface components
**Components**:
- Use Case Cards (`.use-case-card`)
- Project Cards (`.project-card`)
- Category Sections (`.category-section`)
- Navigation and Breadcrumbs
- Loading and Empty States
- Responsive Design
- Animations and Transitions
- Custom Scrollbars

**Key Features**:
- Hierarchical display (Use Cases → Projects → Files)
- Interactive card hover effects
- Responsive grid layouts
- Smooth animations
- Loading state indicators

#### `aasx.css`
**Purpose**: Styles for the AASX processing interface and dashboard
**Components**:
- Main Dashboard Layout (`.aasx-dashboard`)
- Header and Navigation (`.aasx-header`)
- Statistics Cards (`.stats-card`)
- Processing Interface (`.processing-interface`)
- File Upload Area (`.file-upload-area`)
- Progress Bars and Status Indicators
- ETL Pipeline Visualization (`.etl-pipeline`)
- Sidebar Components (`.aasx-sidebar`)
- Buttons and Alerts
- Tables and Data Display
- Loading Animations

**Key Features**:
- Modern gradient backgrounds
- Interactive processing status
- ETL step visualization
- Responsive design
- Custom animations

## CSS Classes Reference

### Data Management Classes

#### Use Case Cards
```css
.use-case-card          /* Main use case card container */
.use-case-card:hover    /* Hover state with elevation */
.use-case-stats         /* Statistics section within card */
```

#### Project Cards
```css
.project-card           /* Main project card container */
.project-card:hover     /* Hover state with elevation */
.project-stats          /* Statistics section within card */
```

#### Navigation
```css
#useCasesContainer      /* Container for use case cards */
#projectsContainer      /* Container for project cards */
#projectsSection        /* Projects view section */
#backToUseCases         /* Back navigation button */
```

### AASX Processing Classes

#### Statistics Cards
```css
.stats-card             /* Main statistics card */
.stats-card.bg-primary  /* Primary color theme */
.stats-card.bg-success  /* Success color theme */
.stats-card.bg-warning  /* Warning color theme */
.stats-card.bg-info     /* Info color theme */
.stats-card.bg-danger   /* Danger color theme */
```

#### Processing Interface
```css
.processing-interface   /* Main processing container */
.file-upload-area       /* File upload drop zone */
.progress-container     /* Progress bar container */
.processing-status      /* Status indicators */
```

#### ETL Pipeline
```css
.etl-pipeline           /* ETL visualization container */
.etl-step              /* Individual ETL step */
.etl-step.extract      /* Extract step styling */
.etl-step.transform    /* Transform step styling */
.etl-step.load         /* Load step styling */
```

## Color Scheme

### Primary Colors
- **Primary Blue**: `#007bff` → `#0056b3`
- **Success Green**: `#28a745` → `#1e7e34`
- **Warning Yellow**: `#ffc107` → `#e0a800`
- **Info Cyan**: `#17a2b8` → `#138496`
- **Danger Red**: `#dc3545` → `#c82333`

### Neutral Colors
- **Light Gray**: `#f8f9fa`
- **Medium Gray**: `#6c757d`
- **Dark Gray**: `#495057`
- **Border Gray**: `#e9ecef`

## Responsive Design

### Breakpoints
- **Mobile**: `max-width: 768px`
- **Tablet**: `768px - 1024px`
- **Desktop**: `min-width: 1024px`

### Mobile Adaptations
- Reduced padding and margins
- Smaller font sizes
- Stacked layouts
- Touch-friendly button sizes

## Animations

### Transitions
- **Card Hover**: `transform: translateY(-2px)` with shadow
- **Button Hover**: `transform: translateY(-2px)` with shadow
- **Progress Bars**: `width` transition with `0.6s ease`

### Keyframes
- **fadeInUp**: Slide up with fade in
- **spin**: Loading spinner rotation
- **pulse**: Pulsing effect for active elements

## Usage Guidelines

### Adding New Components
1. Determine if it belongs to Data Management or AASX Processing
2. Add styles to the appropriate CSS file
3. Follow the existing naming conventions
4. Include responsive design considerations
5. Add hover states and transitions

### Modifying Existing Styles
1. Maintain the existing color scheme
2. Preserve responsive behavior
3. Test hover states and animations
4. Ensure accessibility standards

### Best Practices
- Use CSS custom properties for consistent colors
- Implement progressive enhancement
- Maintain consistent spacing with rem units
- Use semantic class names
- Include focus states for accessibility

## Browser Support
- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Performance Considerations
- CSS is minified in production
- Critical CSS is inlined
- Non-critical CSS is loaded asynchronously
- Images are optimized and lazy-loaded

## Maintenance
- Regular review of unused CSS
- Performance monitoring
- Accessibility audits
- Cross-browser testing
- Mobile responsiveness testing 