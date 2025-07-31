/**
 * Advanced Filters and Search Functionality
 * Phase 2.3: Analytics Integration - Advanced Filtering
 */

console.log('🔍 Advanced Filters JS loaded');

// Global filter state
let advancedFiltersState = {
    dateRange: '30',
    customStartDate: null,
    customEndDate: null,
    facility: '',
    metricType: '',
    performanceThreshold: 80,
    search: '',
    status: '',
    sortBy: 'date_desc'
};

// Filter presets
let filterPresets = {};

// Initialize advanced filters
document.addEventListener('DOMContentLoaded', function() {
    initializeAdvancedFilters();
    loadFilterPresets();
});

function initializeAdvancedFilters() {
    console.log('🔍 Initializing advanced filters...');
    
    // Date range filter
    const dateRangeFilter = document.getElementById('dateRangeFilter');
    if (dateRangeFilter) {
        dateRangeFilter.addEventListener('change', function() {
            if (this.value === 'custom') {
                document.getElementById('customDateRange').style.display = 'block';
            } else {
                document.getElementById('customDateRange').style.display = 'none';
                advancedFiltersState.dateRange = this.value;
                advancedFiltersState.customStartDate = null;
                advancedFiltersState.customEndDate = null;
            }
        });
    }

    // Custom date inputs
    const startDate = document.getElementById('startDate');
    const endDate = document.getElementById('endDate');
    if (startDate) {
        startDate.addEventListener('change', function() {
            advancedFiltersState.customStartDate = this.value;
        });
    }
    if (endDate) {
        endDate.addEventListener('change', function() {
            advancedFiltersState.customEndDate = this.value;
        });
    }

    // Performance threshold slider
    const thresholdSlider = document.getElementById('performanceThreshold');
    const thresholdValue = document.getElementById('thresholdValue');
    if (thresholdSlider && thresholdValue) {
        thresholdSlider.addEventListener('input', function() {
            advancedFiltersState.performanceThreshold = this.value;
            thresholdValue.textContent = this.value + '%';
        });
    }

    // Search input with debouncing
    const searchInput = document.getElementById('searchFilter');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                advancedFiltersState.search = this.value;
                applyAdvancedFilters();
            }, 500);
        });
    }

    // Other filter inputs
    const filterInputs = ['facilityFilter', 'metricTypeFilter', 'statusFilter', 'sortFilter'];
    filterInputs.forEach(inputId => {
        const input = document.getElementById(inputId);
        if (input) {
            input.addEventListener('change', function() {
                advancedFiltersState[inputId.replace('Filter', '')] = this.value;
            });
        }
    });

    console.log('✅ Advanced filters initialized');
}

// Apply advanced filters
async function applyAdvancedFilters() {
    console.log('🔍 Applying advanced filters:', advancedFiltersState);
    
    try {
        // Show loading state
        showFilterLoading(true);
        
        // Build filter parameters
        const filterParams = buildFilterParams();
        
        // Fetch filtered data
        const filteredData = await AnalyticsIntegration.filterAnalyticsData(filterParams);
        
        // Update charts and tables with filtered data
        updateChartsWithFilteredData(filteredData);
        
        // Update results count
        updateFilteredResultsCount(filteredData);
        
        // Save current filters
        saveCurrentFilters();
        
        console.log('✅ Advanced filters applied successfully');
        
    } catch (error) {
        console.error('❌ Error applying advanced filters:', error);
        showNotification('Error applying filters', 'error');
    } finally {
        showFilterLoading(false);
    }
}

// Build filter parameters for API
function buildFilterParams() {
    const params = {};
    
    // Date range
    if (advancedFiltersState.dateRange === 'custom' && advancedFiltersState.customStartDate && advancedFiltersState.customEndDate) {
        params.startDate = advancedFiltersState.customStartDate;
        params.endDate = advancedFiltersState.customEndDate;
    } else {
        params.timeframe = advancedFiltersState.dateRange + 'd';
    }
    
    // Other filters
    if (advancedFiltersState.facility) params.facility = advancedFiltersState.facility;
    if (advancedFiltersState.metricType) params.metricType = advancedFiltersState.metricType;
    if (advancedFiltersState.performanceThreshold) params.threshold = advancedFiltersState.performanceThreshold;
    if (advancedFiltersState.search) params.search = advancedFiltersState.search;
    if (advancedFiltersState.status) params.status = advancedFiltersState.status;
    if (advancedFiltersState.sortBy) params.sortBy = advancedFiltersState.sortBy;
    
    return params;
}

// Update charts with filtered data
function updateChartsWithFilteredData(data) {
    if (!data) return;
    
    // Update quality trends chart
    if (window.qualityTrendsChart && data.quality_data) {
        window.qualityTrendsChart.data = data.quality_data;
        window.qualityTrendsChart.update();
    }
    
    // Update performance chart
    if (window.performanceChart && data.performance_data) {
        window.performanceChart.data = data.performance_data;
        window.performanceChart.update();
    }
    
    // Update twin performance chart
    if (window.twinPerformanceChart && data.twin_performance_data) {
        window.twinPerformanceChart.data = data.twin_performance_data;
        window.twinPerformanceChart.update();
    }
    
    // Update tables
    updateTablesWithFilteredData(data);
}

// Update tables with filtered data
function updateTablesWithFilteredData(data) {
    // Update quality metrics table
    const qualityTable = document.querySelector('#qualityMetricsTable tbody');
    if (qualityTable && data.quality_metrics) {
        qualityTable.innerHTML = '';
        data.quality_metrics.forEach(metric => {
            const row = createTableRow(metric);
            qualityTable.appendChild(row);
        });
    }
    
    // Update recent events table
    const eventsTable = document.querySelector('#recentEventsTable tbody');
    if (eventsTable && data.recent_events) {
        eventsTable.innerHTML = '';
        data.recent_events.forEach(event => {
            const row = createEventRow(event);
            eventsTable.appendChild(row);
        });
    }
}

// Create table row for quality metrics
function createTableRow(metric) {
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>${metric.facility}</td>
        <td>${metric.quality_score}%</td>
        <td>${metric.compliance}%</td>
        <td>${metric.efficiency}%</td>
        <td><span class="badge bg-${getStatusColor(metric.status)}">${metric.status}</span></td>
    `;
    return row;
}

// Create table row for events
function createEventRow(event) {
    const row = document.createElement('tr');
    row.innerHTML = `
        <td><strong class="text-${event.type}">${event.title}</strong><br><small class="text-muted">${event.facility}</small></td>
        <td><small class="text-muted">${event.timestamp}</small></td>
    `;
    return row;
}

// Get status color for badges
function getStatusColor(status) {
    const colors = {
        'excellent': 'success',
        'good': 'info',
        'average': 'warning',
        'poor': 'danger',
        'critical': 'dark'
    };
    return colors[status.toLowerCase()] || 'secondary';
}

// Update filtered results count
function updateFilteredResultsCount(data) {
    const countElement = document.getElementById('filteredResultsCount');
    if (countElement) {
        const totalResults = data?.total_results || 0;
        countElement.textContent = totalResults;
    }
}

// Reset all filters
function resetAllFilters() {
    console.log('🔄 Resetting all filters...');
    
    advancedFiltersState = {
        dateRange: '30',
        customStartDate: null,
        customEndDate: null,
        facility: '',
        metricType: '',
        performanceThreshold: 80,
        search: '',
        status: '',
        sortBy: 'date_desc'
    };
    
    // Reset form inputs
    const form = document.getElementById('advancedFiltersForm');
    if (form) form.reset();
    
    // Hide custom date range
    const customDateRange = document.getElementById('customDateRange');
    if (customDateRange) customDateRange.style.display = 'none';
    
    // Reset threshold display
    const thresholdValue = document.getElementById('thresholdValue');
    if (thresholdValue) thresholdValue.textContent = '80%';
    
    // Apply reset filters
    applyAdvancedFilters();
    
    showNotification('All filters reset', 'success');
}

// Clear search
function clearSearch() {
    const searchInput = document.getElementById('searchFilter');
    if (searchInput) {
        searchInput.value = '';
        advancedFiltersState.search = '';
        applyAdvancedFilters();
    }
}

// Save filter preset
function saveFilterPreset() {
    const presetName = prompt('Enter preset name:');
    if (presetName) {
        filterPresets[presetName] = { ...advancedFiltersState };
        localStorage.setItem('analytics_filter_presets', JSON.stringify(filterPresets));
        showNotification(`Filter preset "${presetName}" saved`, 'success');
    }
}

// Load filter presets
function loadFilterPresets() {
    const saved = localStorage.getItem('analytics_filter_presets');
    if (saved) {
        filterPresets = JSON.parse(saved);
    }
}

// Load filter preset
function loadFilterPreset() {
    if (Object.keys(filterPresets).length === 0) {
        showNotification('No saved presets found', 'info');
        return;
    }
    
    const presetNames = Object.keys(filterPresets);
    const presetName = prompt(`Enter preset name to load:\n\nAvailable presets:\n${presetNames.join('\n')}`);
    
    if (presetName && filterPresets[presetName]) {
        advancedFiltersState = { ...filterPresets[presetName] };
        applyFiltersToForm();
        applyAdvancedFilters();
        showNotification(`Filter preset "${presetName}" loaded`, 'success');
    }
}

// Apply filters to form
function applyFiltersToForm() {
    // Date range
    const dateRangeFilter = document.getElementById('dateRangeFilter');
    if (dateRangeFilter) {
        dateRangeFilter.value = advancedFiltersState.dateRange;
        if (advancedFiltersState.dateRange === 'custom') {
            document.getElementById('customDateRange').style.display = 'block';
        }
    }
    
    // Custom dates
    if (advancedFiltersState.customStartDate) {
        const startDate = document.getElementById('startDate');
        if (startDate) startDate.value = advancedFiltersState.customStartDate;
    }
    if (advancedFiltersState.customEndDate) {
        const endDate = document.getElementById('endDate');
        if (endDate) endDate.value = advancedFiltersState.customEndDate;
    }
    
    // Other filters
    const filterMappings = {
        'facilityFilter': 'facility',
        'metricTypeFilter': 'metricType',
        'statusFilter': 'status',
        'sortFilter': 'sortBy'
    };
    
    Object.entries(filterMappings).forEach(([elementId, filterKey]) => {
        const element = document.getElementById(elementId);
        if (element && advancedFiltersState[filterKey]) {
            element.value = advancedFiltersState[filterKey];
        }
    });
    
    // Performance threshold
    const thresholdSlider = document.getElementById('performanceThreshold');
    const thresholdValue = document.getElementById('thresholdValue');
    if (thresholdSlider && thresholdValue) {
        thresholdSlider.value = advancedFiltersState.performanceThreshold;
        thresholdValue.textContent = advancedFiltersState.performanceThreshold + '%';
    }
    
    // Search
    const searchInput = document.getElementById('searchFilter');
    if (searchInput && advancedFiltersState.search) {
        searchInput.value = advancedFiltersState.search;
    }
}

// Export filtered data
async function exportFilteredData() {
    console.log('📊 Exporting filtered data...');
    
    try {
        const filterParams = buildFilterParams();
        const data = await AnalyticsIntegration.filterAnalyticsData(filterParams);
        
        if (data) {
            const exportData = {
                exportDate: new Date().toISOString(),
                filters: advancedFiltersState,
                data: data
            };
            
            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `analytics_filtered_data_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            showNotification('Filtered data exported successfully', 'success');
        }
    } catch (error) {
        console.error('❌ Error exporting filtered data:', error);
        showNotification('Error exporting data', 'error');
    }
}

// Save current filters
function saveCurrentFilters() {
    localStorage.setItem('analytics_current_filters', JSON.stringify(advancedFiltersState));
}

// Load current filters
function loadCurrentFilters() {
    const saved = localStorage.getItem('analytics_current_filters');
    if (saved) {
        advancedFiltersState = { ...advancedFiltersState, ...JSON.parse(saved) };
        applyFiltersToForm();
    }
}

// Show/hide filter loading state
function showFilterLoading(show) {
    const applyButton = document.querySelector('button[onclick="applyAdvancedFilters()"]');
    if (applyButton) {
        if (show) {
            applyButton.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Applying...';
            applyButton.disabled = true;
        } else {
            applyButton.innerHTML = '<i class="fas fa-filter me-1"></i>Apply Filters';
            applyButton.disabled = false;
        }
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Use existing notification system or create simple alert
    if (typeof showNotification === 'function') {
        showNotification(message, type);
    } else {
        alert(`${type.toUpperCase()}: ${message}`);
    }
}

// Export functions to global scope
window.applyAdvancedFilters = applyAdvancedFilters;
window.resetAllFilters = resetAllFilters;
window.clearSearch = clearSearch;
window.saveFilterPreset = saveFilterPreset;
window.loadFilterPreset = loadFilterPreset;
window.exportFilteredData = exportFilteredData; 