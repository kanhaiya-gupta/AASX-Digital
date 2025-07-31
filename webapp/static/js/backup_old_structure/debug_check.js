/**
 * Debug Check Script
 * Verifies that all JavaScript files are loading correctly and identifies issues
 */

console.log('🔍 Debug Check Script Loaded');

// Check if jQuery is available
function checkJQuery() {
    if (typeof $ !== 'undefined') {
        console.log('✅ jQuery is available');
        return true;
    } else {
        console.error('❌ jQuery is NOT available');
        return false;
    }
}

// Check if Bootstrap is available
function checkBootstrap() {
    if (typeof bootstrap !== 'undefined') {
        console.log('✅ Bootstrap is available');
        return true;
    } else {
        console.error('❌ Bootstrap is NOT available');
        return false;
    }
}

// Check if Chart.js is available
function checkChartJS() {
    if (typeof Chart !== 'undefined') {
        console.log('✅ Chart.js is available');
        return true;
    } else {
        console.error('❌ Chart.js is NOT available');
        return false;
    }
}

// Check if D3.js is available
function checkD3JS() {
    if (typeof d3 !== 'undefined') {
        console.log('✅ D3.js is available');
        return true;
    } else {
        console.error('❌ D3.js is NOT available');
        return false;
    }
}

// Check if shared utilities are available
function checkSharedUtils() {
    if (typeof AASXUtils !== 'undefined') {
        console.log('✅ AASXUtils is available');
        return true;
    } else {
        console.error('❌ AASXUtils is NOT available');
        return false;
    }
}

// Check if shared API is available
function checkSharedAPI() {
    if (typeof AASXAPI !== 'undefined') {
        console.log('✅ AASXAPI is available');
        return true;
    } else {
        console.error('❌ AASXAPI is NOT available');
        return false;
    }
}

// Check if main framework is available
function checkMainFramework() {
    if (typeof AASXFramework !== 'undefined') {
        console.log('✅ AASXFramework is available');
        return true;
    } else {
        console.error('❌ AASXFramework is NOT available');
        return false;
    }
}

// Check for common DOM elements
function checkDOMElements() {
    const commonElements = [
        'navbar',
        'main-content',
        'footer'
    ];
    
    const missingElements = [];
    commonElements.forEach(id => {
        if (!document.getElementById(id)) {
            missingElements.push(id);
        }
    });
    
    if (missingElements.length === 0) {
        console.log('✅ All common DOM elements found');
        return true;
    } else {
        console.warn('⚠️ Missing DOM elements:', missingElements);
        return false;
    }
}

// Check for JavaScript errors
function checkForErrors() {
    const originalError = console.error;
    const errors = [];
    
    console.error = function(...args) {
        errors.push(args.join(' '));
        originalError.apply(console, args);
    };
    
    // Wait a bit for any errors to occur
    setTimeout(() => {
        console.error = originalError;
        
        if (errors.length === 0) {
            console.log('✅ No JavaScript errors detected');
        } else {
            console.error('❌ JavaScript errors detected:', errors);
        }
    }, 1000);
}

// Check module-specific functionality
function checkModuleFunctionality() {
    const currentPath = window.location.pathname;
    
    if (currentPath.includes('/ai-rag')) {
        console.log('🔍 Checking AI/RAG functionality...');
        checkAI_RAGFunctionality();
    } else if (currentPath.includes('/kg-neo4j')) {
        console.log('🔍 Checking Knowledge Graph functionality...');
        checkKnowledgeGraphFunctionality();
    } else if (currentPath.includes('/certificates')) {
        console.log('🔍 Checking Certificate Manager functionality...');
        checkCertificateManagerFunctionality();
    } else if (currentPath.includes('/analytics')) {
        console.log('🔍 Checking Analytics functionality...');
        checkAnalyticsFunctionality();
    } else if (currentPath.includes('/twin-registry')) {
        console.log('🔍 Checking Twin Registry functionality...');
        checkTwinRegistryFunctionality();
    } else if (currentPath.includes('/federated-learning')) {
        console.log('🔍 Checking Federated Learning functionality...');
        checkFederatedLearningFunctionality();
    } else if (currentPath.includes('/aasx')) {
        console.log('🔍 Checking AASX functionality...');
        checkAASXFunctionality();
    }
}

function checkAI_RAGFunctionality() {
    const elements = [
        'rag-technique-select',
        'llm-model-select',
        'analysis-type-select',
        'submit-query',
        'clear-query',
        'query-input'
    ];
    
    const missingElements = elements.filter(id => !document.getElementById(id));
    if (missingElements.length === 0) {
        console.log('✅ All AI/RAG elements found');
    } else {
        console.warn('⚠️ Missing AI/RAG elements:', missingElements);
    }
}

function checkKnowledgeGraphFunctionality() {
    const elements = [
        'docker-status',
        'local-status',
        'launch-docker-browser',
        'launch-local-browser',
        'start-docker-neo4j',
        'stop-docker-neo4j'
    ];
    
    const missingElements = elements.filter(id => !document.getElementById(id));
    if (missingElements.length === 0) {
        console.log('✅ All Knowledge Graph elements found');
    } else {
        console.warn('⚠️ Missing Knowledge Graph elements:', missingElements);
    }
}

function checkCertificateManagerFunctionality() {
    const elements = [
        'issueCertificate',
        'refreshCertificates',
        'exportCertificates',
        'bulkRenewal',
        'certificateTable'
    ];
    
    const missingElements = elements.filter(id => !document.getElementById(id));
    if (missingElements.length === 0) {
        console.log('✅ All Certificate Manager elements found');
    } else {
        console.warn('⚠️ Missing Certificate Manager elements:', missingElements);
    }
}

function checkAnalyticsFunctionality() {
    const elements = [
        'analytics-dashboard',
        'quality-metrics-chart',
        'performance-metrics-chart',
        'filter-panel'
    ];
    
    const missingElements = elements.filter(id => !document.getElementById(id));
    if (missingElements.length === 0) {
        console.log('✅ All Analytics elements found');
    } else {
        console.warn('⚠️ Missing Analytics elements:', missingElements);
    }
}

function checkTwinRegistryFunctionality() {
    const elements = [
        'twins-performance',
        'twin-health-overview',
        'performance-alerts',
        'real-time-monitoring'
    ];
    
    const missingElements = elements.filter(id => !document.getElementById(id));
    if (missingElements.length === 0) {
        console.log('✅ All Twin Registry elements found');
    } else {
        console.warn('⚠️ Missing Twin Registry elements:', missingElements);
    }
}

function checkFederatedLearningFunctionality() {
    const elements = [
        'startFederation',
        'runCycle',
        'stopFederation',
        'twins-performance',
        'cross-twin-insights'
    ];
    
    const missingElements = elements.filter(id => !document.getElementById(id));
    if (missingElements.length === 0) {
        console.log('✅ All Federated Learning elements found');
    } else {
        console.warn('⚠️ Missing Federated Learning elements:', missingElements);
    }
}

function checkAASXFunctionality() {
    const elements = [
        'projects-container',
        'files-container',
        'upload-form',
        'processing-status'
    ];
    
    const missingElements = elements.filter(id => !document.getElementById(id));
    if (missingElements.length === 0) {
        console.log('✅ All AASX elements found');
    } else {
        console.warn('⚠️ Missing AASX elements:', missingElements);
    }
}

// Run all checks
function runAllChecks() {
    console.log('🔍 Running comprehensive debug checks...');
    
    checkJQuery();
    checkBootstrap();
    checkChartJS();
    checkD3JS();
    checkSharedUtils();
    checkSharedAPI();
    checkMainFramework();
    checkDOMElements();
    checkForErrors();
    checkModuleFunctionality();
    
    console.log('✅ Debug checks completed');
}

// Run checks when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM loaded - running debug checks...');
    setTimeout(runAllChecks, 500);
});

// Export for manual testing
window.DebugCheck = {
    runAllChecks,
    checkJQuery,
    checkBootstrap,
    checkChartJS,
    checkD3JS,
    checkSharedUtils,
    checkSharedAPI,
    checkMainFramework,
    checkDOMElements,
    checkForErrors,
    checkModuleFunctionality
}; 