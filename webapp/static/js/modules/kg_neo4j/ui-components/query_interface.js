/**
 * Knowledge Graph Query Interface UI Component
 * Handles Cypher query execution and results display
 */

import { showAlert } from '/static/js/shared/alerts.js';

export async function initQueryInterface() {
    console.log('🔧 Initializing Knowledge Graph Query Interface component...');
    
    try {
        // Set up event listeners
        const executeBtn = document.getElementById('execute-query');
        const clearBtn = document.getElementById('clear-query');
        const examplesBtn = document.getElementById('examples-query');
        const queryTextarea = document.getElementById('cypher-query');
        
        if (executeBtn) {
            executeBtn.addEventListener('click', executeQuery);
        }
        
        if (clearBtn) {
            clearBtn.addEventListener('click', clearQuery);
        }
        
        if (examplesBtn) {
            examplesBtn.addEventListener('click', showExamplesModal);
        }
        
        if (queryTextarea) {
            // Add keyboard shortcut (Ctrl+Enter to execute)
            queryTextarea.addEventListener('keydown', function(e) {
                if (e.ctrlKey && e.key === 'Enter') {
                    executeQuery();
                }
            });
        }
        
        // Set up examples modal functionality
        setupExamplesModal();
        
        console.log('✅ Knowledge Graph Query Interface component initialized');
        
    } catch (error) {
        console.error('❌ Failed to initialize Query Interface component:', error);
    }
}

async function executeQuery() {
    const queryTextarea = document.getElementById('cypher-query');
    const query = queryTextarea?.value?.trim();
    
    if (!query) {
        showAlert('Please enter a Cypher query', 'warning');
        return;
    }
    
    try {
        showLoading('Executing query...');
        
        const response = await fetch('/api/kg-neo4j/execute-query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayQueryResults(result.data);
            showAlert('Query executed successfully', 'success');
        } else {
            showAlert(`Query failed: ${result.error}`, 'error');
        }
        
    } catch (error) {
        console.error('Query execution failed:', error);
        showAlert('Query execution failed', 'error');
    } finally {
        hideLoading();
    }
}

function clearQuery() {
    const queryTextarea = document.getElementById('cypher-query');
    if (queryTextarea) {
        queryTextarea.value = '';
    }
}

function displayQueryResults(data) {
    // Implementation for displaying query results
    console.log('Query results:', data);
    
    // Create results display area if it doesn't exist
    let resultsArea = document.getElementById('query-results');
    if (!resultsArea) {
        resultsArea = document.createElement('div');
        resultsArea.id = 'query-results';
        resultsArea.className = 'mt-3';
        document.getElementById('cypher-query').parentNode.appendChild(resultsArea);
    }
    
    // Display results based on data type
    if (Array.isArray(data)) {
        displayTableResults(data, resultsArea);
    } else {
        displayJsonResults(data, resultsArea);
    }
}

function displayTableResults(data, container) {
    if (data.length === 0) {
        container.innerHTML = '<div class="alert alert-info">No results found</div>';
        return;
    }
    
    const table = document.createElement('table');
    table.className = 'table table-striped table-sm';
    
    // Create header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    const columns = Object.keys(data[0]);
    
    columns.forEach(column => {
        const th = document.createElement('th');
        th.textContent = column;
        headerRow.appendChild(th);
    });
    
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Create body
    const tbody = document.createElement('tbody');
    data.forEach(row => {
        const tr = document.createElement('tr');
        columns.forEach(column => {
            const td = document.createElement('td');
            td.textContent = JSON.stringify(row[column]);
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    
    table.appendChild(tbody);
    container.innerHTML = '';
    container.appendChild(table);
}

function displayJsonResults(data, container) {
    container.innerHTML = `<pre class="bg-light p-3 rounded">${JSON.stringify(data, null, 2)}</pre>`;
}

function showLoading(message = 'Loading...') {
    // Simple loading indicator
    const executeBtn = document.getElementById('execute-query');
    if (executeBtn) {
        executeBtn.disabled = true;
        executeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Executing...';
    }
}

function hideLoading() {
    // Restore button state
    const executeBtn = document.getElementById('execute-query');
    if (executeBtn) {
        executeBtn.disabled = false;
        executeBtn.innerHTML = '<i class="fas fa-play me-2"></i>Execute Query';
    }
}

function setupExamplesModal() {
    // Set up copy button functionality
    const copyBtn = document.getElementById('copy-query-btn');
    if (copyBtn) {
        copyBtn.addEventListener('click', copySelectedQuery);
    }
    
    // Set up click handlers for example queries
    document.addEventListener('click', function(e) {
        if (e.target.closest('.example-query code')) {
            const codeElement = e.target.closest('.example-query code');
            selectQueryForCopy(codeElement);
        }
    });
}

function showExamplesModal() {
    const modal = new bootstrap.Modal(document.getElementById('examplesModal'));
    modal.show();
}

function selectQueryForCopy(codeElement) {
    // Remove previous selections
    document.querySelectorAll('.example-query code').forEach(code => {
        code.classList.remove('selected-query');
    });
    
    // Add selection to clicked element
    codeElement.classList.add('selected-query');
    codeElement.style.backgroundColor = '#007bff';
    codeElement.style.color = 'white';
    
    // Enable copy button
    const copyBtn = document.getElementById('copy-query-btn');
    if (copyBtn) {
        copyBtn.disabled = false;
    }
}

function copySelectedQuery() {
    const selectedCode = document.querySelector('.example-query code.selected-query');
    if (!selectedCode) {
        showAlert('Please select a query first', 'warning');
        return;
    }
    
    const queryText = selectedCode.textContent;
    
    // Copy to clipboard
    navigator.clipboard.writeText(queryText).then(() => {
        showAlert('Query copied to clipboard!', 'success');
        
        // Also paste it into the query textarea
        const queryTextarea = document.getElementById('cypher-query');
        if (queryTextarea) {
            queryTextarea.value = queryText;
        }
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('examplesModal'));
        if (modal) {
            modal.hide();
        }
    }).catch(err => {
        console.error('Failed to copy query:', err);
        showAlert('Failed to copy query to clipboard', 'error');
    });
} 