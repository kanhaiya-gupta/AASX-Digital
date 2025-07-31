// Twin Registry JavaScript Functions

// Form validation and data collection
function collectFormData() {
    var formData = {
        basic: {
            twinId: $('#twinId').val(),
            twinName: $('#twinName').val(),
            twinType: $('#twinType').val(),
            twinCategory: $('#twinCategory').val()
        },
        asset: {
            assetId: $('#assetId').val(),
            assetLocation: $('#assetLocation').val(),
            assetModel: $('#assetModel').val(),
            assetManufacturer: $('#assetManufacturer').val(),
            assetSerialNumber: $('#assetSerialNumber').val(),
            assetInstallationDate: $('#assetInstallationDate').val()
        },
        config: {
            syncFrequency: $('#syncFrequency').val(),
            dataRetention: $('#dataRetention').val(),
            alertThreshold: $('#alertThreshold').val(),
            twinStatus: $('#twinStatus').val()
        },
        dataSource: {
            dataSourceType: $('#dataSourceType').val(),
            dataFormat: $('#dataFormat').val(),
            dataEndpoints: $('#dataEndpoints').val().split('\n').filter(endpoint => endpoint.trim() !== '')
        },
        aas: {
            aasId: $('#aasId').val(),
            aasVersion: $('#aasVersion').val(),
            aasSubmodels: $('#aasSubmodels').val().split(',').map(submodel => submodel.trim()).filter(submodel => submodel !== '')
        },
        metadata: {
            description: $('#twinDescription').val(),
            tags: $('#twinTags').val().split(',').map(tag => tag.trim()).filter(tag => tag !== '')
        }
    };
    return formData;
}

function validateFormData(formData, isCreate) {
    var errors = [];
    
    // Required field validation
    if (!formData.basic.twinId) {
        errors.push('Twin ID is required');
    }
    if (!formData.basic.twinName) {
        errors.push('Twin Name is required');
    }
    if (!formData.basic.twinType) {
        errors.push('Twin Type is required');
    }
    
    // Additional validation for create mode
    if (isCreate) {
        if (!formData.asset.assetId) {
            errors.push('Asset ID is required for active twins');
        }
        if (!formData.dataSource.dataSourceType) {
            errors.push('Primary Data Source is required for active twins');
        }
    }
    
    // Twin ID format validation
    if (formData.basic.twinId && !/^[A-Z0-9\-_]+$/.test(formData.basic.twinId)) {
        errors.push('Twin ID should contain only uppercase letters, numbers, hyphens, and underscores');
    }
    
    if (errors.length > 0) {
        showAlert('error', 'Validation errors: ' + errors.join(', '));
        return false;
    }
    
    return true;
}

function saveTwinAsDraft(formData) {
    // Add draft status
    formData.status = 'draft';
    formData.createdAt = new Date().toISOString();
    
    // Simulate API call
    console.log('Saving as draft:', formData);
    
    // Show success message
    showAlert('success', 'Digital twin saved as draft successfully!');
    
    // Close modal
    $('#addTwinModal').modal('hide');
    
    // Reset form
    $('#addTwinForm')[0].reset();
}

function createNewTwin(formData) {
    // Add creation metadata
    formData.status = formData.config.twinStatus || 'active';
    formData.createdAt = new Date().toISOString();
    formData.lastSync = new Date().toISOString();
    formData.dataPoints = 0;
    
    // Simulate API call to create twin
    console.log('Creating new twin:', formData);
    
    // Add to table (in real implementation, this would come from the server)
    addTwinToTable({
        twinId: formData.basic.twinId,
        name: formData.basic.twinName,
        type: formData.basic.twinType,
        status: formData.status,
        lastSync: 'Just now',
        dataPoints: 0
    });
    
    // Show success message
    showAlert('success', 'Digital twin created successfully!');
    
    // Close modal
    $('#addTwinModal').modal('hide');
    
    // Reset form
    $('#addTwinForm')[0].reset();
    
    // Update metrics
    updateTwinMetrics();
}

function addTwinToTable(twin) {
    var newRow = `
        <tr>
            <td>
                <i class="fas fa-cube text-primary me-2"></i>
                <strong>${twin.twinId}</strong>
            </td>
            <td>${twin.name}</td>
            <td><span class="badge bg-primary">${twin.type}</span></td>
            <td><span class="badge bg-success">${twin.status}</span></td>
            <td>${twin.lastSync}</td>
            <td>${twin.dataPoints}</td>
            <td>
                <div class="btn-group" role="group">
                    <button class="btn btn-sm btn-primary view-twin" data-id="${twin.twinId}">
                        <i class="fas fa-eye"></i>
                        View
                    </button>
                    <button class="btn btn-sm btn-outline-secondary edit-twin" data-id="${twin.twinId}">
                        <i class="fas fa-edit"></i>
                        Edit
                    </button>
                    <button class="btn btn-sm btn-outline-info sync-twin" data-id="${twin.twinId}">
                        <i class="fas fa-sync"></i>
                        Sync
                    </button>
                </div>
            </td>
        </tr>
    `;
    
    $('#twinRegistryTable tbody').prepend(newRow);
}

function updateTwinMetrics(twinId) {
    // Simulate updating metrics based on selected twin
    var metrics = {
        'DT-001': { uptime: '94.2%', efficiency: '87.3%', response: '2.3s', alerts: 3 },
        'DT-002': { uptime: '96.8%', efficiency: '92.1%', response: '1.8s', alerts: 1 },
        'DT-003': { uptime: '78.5%', efficiency: '65.2%', response: '4.1s', alerts: 5 }
    };
    
    var twin = metrics[twinId] || metrics['DT-001'];
    
    $('#twinMetrics').html(`
        <div class="row text-center">
            <div class="col-6">
                <div class="border rounded p-3">
                    <h4 class="text-primary">${twin.uptime}</h4>
                    <small class="text-muted">Uptime</small>
                </div>
            </div>
            <div class="col-6">
                <div class="border rounded p-3">
                    <h4 class="text-success">${twin.efficiency}</h4>
                    <small class="text-muted">Efficiency</small>
                </div>
            </div>
        </div>
        <div class="row text-center mt-3">
            <div class="col-6">
                <div class="border rounded p-3">
                    <h4 class="text-info">${twin.response}</h4>
                    <small class="text-muted">Response Time</small>
                </div>
            </div>
            <div class="col-6">
                <div class="border rounded p-3">
                    <h4 class="text-warning">${twin.alerts}</h4>
                    <small class="text-muted">Alerts</small>
                </div>
            </div>
        </div>
    `);
}

// Auto-generation functions
function setupAutoGeneration() {
    // Auto-generate Twin ID based on type and name
    $('#twinType, #twinName').on('change keyup', function() {
        var type = $('#twinType').val();
        var name = $('#twinName').val();
        
        if (type && name) {
            var prefix = type.substring(0, 2).toUpperCase();
            var namePart = name.replace(/[^A-Z0-9]/gi, '').substring(0, 8).toUpperCase();
            var timestamp = new Date().getTime().toString().slice(-4);
            var suggestedId = `${prefix}-${namePart}-${timestamp}`;
            
            if (!$('#twinId').val()) {
                $('#twinId').val(suggestedId);
            }
        }
    });

    // Auto-generate Asset ID if not provided
    $('#assetModel, #assetManufacturer').on('change keyup', function() {
        var model = $('#assetModel').val();
        var manufacturer = $('#assetManufacturer').val();
        
        if (model && manufacturer && !$('#assetId').val()) {
            var prefix = manufacturer.substring(0, 3).toUpperCase();
            var modelPart = model.replace(/[^A-Z0-9]/gi, '').substring(0, 6).toUpperCase();
            var timestamp = new Date().getFullYear().toString().slice(-2) + 
                           (new Date().getMonth() + 1).toString().padStart(2, '0');
            var suggestedAssetId = `${prefix}-${modelPart}-${timestamp}`;
            
            $('#assetId').val(suggestedAssetId);
        }
    });
} 