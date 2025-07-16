/**
 * Certificate Manager JavaScript
 * Handles all certificate management functionality, validation, and user interactions
 */

console.log('🔧 Certificate Manager JavaScript file loaded successfully');

// Global variables
let certificateData = [];
let currentCertificate = null;
let updateInterval;

// Initialize the certificate manager
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM Content Loaded - Initializing Certificate Manager...');
    
    // Check for required DOM elements
    const requiredElements = [
        'issueCertificate',
        'refreshCertificates',
        'exportCertificates',
        'bulkRenewal',
        'certificateTable'
    ];
    
    const missingElements = requiredElements.filter(id => !document.getElementById(id));
    if (missingElements.length > 0) {
        console.warn('⚠️ Missing DOM elements:', missingElements);
    } else {
        console.log('✅ All required DOM elements found');
    }
    
    initializeCertificateManager();
    setupEventListeners();
    loadCertificateData();
    startRealTimeUpdates();
});

function initializeCertificateManager() {
    console.log('📋 Setting up certificate manager...');
    
    try {
        // Initialize certificate data
        certificateData = [
            {
                id: 'CERT-001',
                type: 'Quality Assurance',
                issuedTo: 'Additive Manufacturing Facility',
                issueDate: '2024-01-15',
                expiryDate: '2025-01-15',
                status: 'valid',
                description: 'Quality assurance certification for additive manufacturing processes'
            },
            {
                id: 'CERT-002',
                type: 'Safety Compliance',
                issuedTo: 'Hydrogen Filling Station',
                issueDate: '2023-06-20',
                expiryDate: '2024-12-20',
                status: 'expiring_soon',
                description: 'Safety compliance certification for hydrogen handling'
            },
            {
                id: 'CERT-003',
                type: 'Performance',
                issuedTo: 'Servo DC Motor Assembly',
                issueDate: '2023-03-10',
                expiryDate: '2024-03-10',
                status: 'expired',
                description: 'Performance certification for motor assembly operations'
            }
        ];
        
        console.log('✅ Certificate manager initialized successfully');
    } catch (error) {
        console.error('❌ Error initializing certificate manager:', error);
    }
}

function setupEventListeners() {
    console.log('🔗 Setting up event listeners...');
    
    // View certificate
    $(document).on('click', '.view-cert', function() {
        const certId = $(this).data('id');
        console.log('👁️ View certificate clicked:', certId);
        viewCertificate(certId);
    });
    
    // Download certificate
    $(document).on('click', '.download-cert', function() {
        const certId = $(this).data('id');
        console.log('📥 Download certificate clicked:', certId);
        downloadCertificate(certId);
    });
    
    // Renew certificate
    $(document).on('click', '.renew-cert', function() {
        const certId = $(this).data('id');
        console.log('🔄 Renew certificate clicked:', certId);
        renewCertificate(certId, $(this));
    });
    
    // Issue new certificate
    const issueBtn = document.getElementById('issueCertificate');
    if (issueBtn) {
        console.log('✅ Found issue certificate button, adding event listener');
        issueBtn.addEventListener('click', function() {
            console.log('➕ Issue new certificate button clicked');
            issueNewCertificate();
        });
    } else {
        console.warn('⚠️ Issue certificate button not found');
    }
    
    // Refresh certificates
    const refreshBtn = document.getElementById('refreshCertificates');
    if (refreshBtn) {
        console.log('✅ Found refresh certificates button, adding event listener');
        refreshBtn.addEventListener('click', function() {
            console.log('🔄 Refresh certificates button clicked');
            refreshCertificates();
        });
    } else {
        console.warn('⚠️ Refresh certificates button not found');
    }
    
    // Export certificates
    const exportBtn = document.getElementById('exportCertificates');
    if (exportBtn) {
        console.log('✅ Found export certificates button, adding event listener');
        exportBtn.addEventListener('click', function() {
            console.log('📤 Export certificates button clicked');
            exportCertificates();
        });
    } else {
        console.warn('⚠️ Export certificates button not found');
    }
    
    // Bulk renewal
    const bulkRenewalBtn = document.getElementById('bulkRenewal');
    if (bulkRenewalBtn) {
        console.log('✅ Found bulk renewal button, adding event listener');
        bulkRenewalBtn.addEventListener('click', function() {
            console.log('🔄 Bulk renewal button clicked');
            bulkRenewal();
        });
    } else {
        console.warn('⚠️ Bulk renewal button not found');
    }
    
    console.log('✅ Event listeners setup completed');
}

function viewCertificate(certId) {
    const certificate = certificateData.find(cert => cert.id === certId);
    if (certificate) {
        currentCertificate = certificate;
        showCertificateModal(certificate);
    } else {
        showNotification('Certificate not found', 'error');
    }
}

function downloadCertificate(certId) {
    const certificate = certificateData.find(cert => cert.id === certId);
    if (certificate) {
        showNotification('Downloading certificate...', 'info');
        
        // Simulate download process
        setTimeout(() => {
            const certificateBlob = new Blob([
                JSON.stringify(certificate, null, 2)
            ], { type: 'application/json' });
            
            const url = URL.createObjectURL(certificateBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${certId}-certificate.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            showNotification('Certificate downloaded successfully', 'success');
        }, 1000);
    } else {
        showNotification('Certificate not found', 'error');
    }
}

function renewCertificate(certId, button) {
    const certificate = certificateData.find(cert => cert.id === certId);
    if (certificate) {
        button.prop('disabled', true);
        button.html('<i class="fas fa-spinner fa-spin"></i> Renewing...');
        
        showNotification('Renewing certificate...', 'info');
        
        setTimeout(() => {
            // Update certificate expiry date
            const newExpiryDate = new Date();
            newExpiryDate.setFullYear(newExpiryDate.getFullYear() + 1);
            certificate.expiryDate = newExpiryDate.toISOString().split('T')[0];
            certificate.status = 'valid';
            
            button.prop('disabled', false);
            button.html('<i class="fas fa-redo"></i> Renew');
            
            console.log('✅ Certificate renewal completed for:', certId);
            showNotification('Certificate renewed successfully', 'success');
            
            // Refresh the table
            updateCertificateTable();
        }, 2000);
    } else {
        showNotification('Certificate not found', 'error');
    }
}

function issueNewCertificate() {
    showNotification('Opening certificate issuance form...', 'info');
    
    // Create modal for new certificate
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'issueCertificateModal';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-plus me-2"></i>
                        Issue New Certificate
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="newCertificateForm">
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="certType" class="form-label">Certificate Type</label>
                                <select class="form-select" id="certType" required>
                                    <option value="">Select Type</option>
                                    <option value="Quality Assurance">Quality Assurance</option>
                                    <option value="Safety Compliance">Safety Compliance</option>
                                    <option value="Performance">Performance</option>
                                    <option value="Environmental">Environmental</option>
                                    <option value="Security">Security</option>
                                </select>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="issuedTo" class="form-label">Issued To</label>
                                <input type="text" class="form-control" id="issuedTo" required>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="issueDate" class="form-label">Issue Date</label>
                                <input type="date" class="form-control" id="issueDate" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="expiryDate" class="form-label">Expiry Date</label>
                                <input type="date" class="form-control" id="expiryDate" required>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="description" class="form-label">Description</label>
                            <textarea class="form-control" id="description" rows="3"></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="submitNewCertificate()">Issue Certificate</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Set default dates
    const today = new Date();
    const nextYear = new Date();
    nextYear.setFullYear(today.getFullYear() + 1);
    
    document.getElementById('issueDate').value = today.toISOString().split('T')[0];
    document.getElementById('expiryDate').value = nextYear.toISOString().split('T')[0];
    
    // Show the modal
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
    
    // Remove modal from DOM after it's hidden
    modal.addEventListener('hidden.bs.modal', function() {
        document.body.removeChild(modal);
    });
}

function submitNewCertificate() {
    const form = document.getElementById('newCertificateForm');
    const formData = new FormData(form);
    
    // Validate form
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    // Create new certificate
    const newCertificate = {
        id: `CERT-${String(certificateData.length + 1).padStart(3, '0')}`,
        type: document.getElementById('certType').value,
        issuedTo: document.getElementById('issuedTo').value,
        issueDate: document.getElementById('issueDate').value,
        expiryDate: document.getElementById('expiryDate').value,
        status: 'valid',
        description: document.getElementById('description').value
    };
    
    // Add to certificate data
    certificateData.push(newCertificate);
    
    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('issueCertificateModal'));
    if (modal) {
        modal.hide();
    }
    
    // Update table
    updateCertificateTable();
    
    showNotification('Certificate issued successfully', 'success');
    console.log('✅ New certificate issued:', newCertificate);
}

function refreshCertificates() {
    showNotification('Refreshing certificates...', 'info');
    
    // Simulate refresh process
    setTimeout(() => {
        loadCertificateData();
        updateCertificateTable();
        showNotification('Certificates refreshed successfully', 'success');
    }, 1000);
}

function exportCertificates() {
    showNotification('Exporting certificates...', 'info');
    
    setTimeout(() => {
        const exportData = {
            timestamp: new Date().toISOString(),
            certificates: certificateData,
            summary: {
                total: certificateData.length,
                valid: certificateData.filter(c => c.status === 'valid').length,
                expiring_soon: certificateData.filter(c => c.status === 'expiring_soon').length,
                expired: certificateData.filter(c => c.status === 'expired').length
            }
        };
        
        const exportBlob = new Blob([
            JSON.stringify(exportData, null, 2)
        ], { type: 'application/json' });
        
        const url = URL.createObjectURL(exportBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `certificates-export-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showNotification('Certificates exported successfully', 'success');
    }, 1500);
}

function bulkRenewal() {
    const expiringCertificates = certificateData.filter(cert => 
        cert.status === 'expiring_soon' || cert.status === 'expired'
    );
    
    if (expiringCertificates.length === 0) {
        showNotification('No certificates need renewal', 'info');
        return;
    }
    
    showNotification(`Renewing ${expiringCertificates.length} certificates...`, 'info');
    
    // Simulate bulk renewal process
    setTimeout(() => {
        expiringCertificates.forEach(cert => {
            const newExpiryDate = new Date();
            newExpiryDate.setFullYear(newExpiryDate.getFullYear() + 1);
            cert.expiryDate = newExpiryDate.toISOString().split('T')[0];
            cert.status = 'valid';
        });
        
        updateCertificateTable();
        showNotification(`${expiringCertificates.length} certificates renewed successfully`, 'success');
    }, 2000);
}

function loadCertificateData() {
    console.log('📋 Loading certificate data...');
    
    // In a real application, this would fetch from an API
    // For now, we're using the initialized data
    console.log('✅ Certificate data loaded:', certificateData.length, 'certificates');
}

function updateCertificateTable() {
    console.log('🔄 Updating certificate table...');
    
    const tableBody = document.querySelector('#certificateTable tbody');
    if (!tableBody) {
        console.warn('⚠️ Certificate table body not found');
        return;
    }
    
    // Clear existing rows
    tableBody.innerHTML = '';
    
    // Add certificate rows
    certificateData.forEach(cert => {
        const row = document.createElement('tr');
        
        // Determine status badge
        let statusBadge = '';
        let certIcon = '';
        switch (cert.status) {
            case 'valid':
                statusBadge = '<span class="badge bg-success">Valid</span>';
                certIcon = '<i class="fas fa-certificate text-success me-2"></i>';
                break;
            case 'expiring_soon':
                statusBadge = '<span class="badge bg-warning">Expiring Soon</span>';
                certIcon = '<i class="fas fa-certificate text-warning me-2"></i>';
                break;
            case 'expired':
                statusBadge = '<span class="badge bg-danger">Expired</span>';
                certIcon = '<i class="fas fa-certificate text-danger me-2"></i>';
                break;
        }
        
        row.innerHTML = `
            <td>
                ${certIcon}
                <strong>${cert.id}</strong>
            </td>
            <td><span class="badge bg-primary">${cert.type}</span></td>
            <td>${cert.issuedTo}</td>
            <td>${cert.issueDate}</td>
            <td>${cert.expiryDate}</td>
            <td>${statusBadge}</td>
            <td>
                <div class="btn-group" role="group">
                    <button class="btn btn-sm btn-primary view-cert" data-id="${cert.id}">
                        <i class="fas fa-eye"></i>
                        View
                    </button>
                    <button class="btn btn-sm btn-outline-secondary download-cert" data-id="${cert.id}">
                        <i class="fas fa-download"></i>
                        Download
                    </button>
                    <button class="btn btn-sm btn-outline-warning renew-cert" data-id="${cert.id}">
                        <i class="fas fa-redo"></i>
                        Renew
                    </button>
                </div>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
    
    console.log('✅ Certificate table updated');
}

function showCertificateModal(certificate) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'certificateModal';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-certificate me-2"></i>
                        Certificate Details - ${certificate.id}
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Certificate Information</h6>
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item d-flex justify-content-between">
                                    <strong>ID:</strong>
                                    <span>${certificate.id}</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <strong>Type:</strong>
                                    <span>${certificate.type}</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <strong>Issued To:</strong>
                                    <span>${certificate.issuedTo}</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <strong>Issue Date:</strong>
                                    <span>${certificate.issueDate}</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <strong>Expiry Date:</strong>
                                    <span>${certificate.expiryDate}</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <strong>Status:</strong>
                                    <span>${certificate.status}</span>
                                </li>
                            </ul>
                        </div>
                        <div class="col-md-6">
                            <h6>Description</h6>
                            <p class="text-muted">${certificate.description || 'No description available'}</p>
                            
                            <h6>Actions</h6>
                            <div class="d-grid gap-2">
                                <button class="btn btn-outline-primary" onclick="downloadCertificate('${certificate.id}')">
                                    <i class="fas fa-download me-2"></i>
                                    Download Certificate
                                </button>
                                <button class="btn btn-outline-warning" onclick="renewCertificate('${certificate.id}', $(this))">
                                    <i class="fas fa-redo me-2"></i>
                                    Renew Certificate
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Show the modal
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
    
    // Remove modal from DOM after it's hidden
    modal.addEventListener('hidden.bs.modal', function() {
        document.body.removeChild(modal);
    });
}

function startRealTimeUpdates() {
    // Update certificate status every 30 seconds
    updateInterval = setInterval(() => {
        updateCertificateStatuses();
    }, 30000);
}

function updateCertificateStatuses() {
    const today = new Date();
    certificateData.forEach(cert => {
        const expiryDate = new Date(cert.expiryDate);
        const daysUntilExpiry = Math.ceil((expiryDate - today) / (1000 * 60 * 60 * 24));
        
        if (daysUntilExpiry < 0) {
            cert.status = 'expired';
        } else if (daysUntilExpiry <= 30) {
            cert.status = 'expiring_soon';
        } else {
            cert.status = 'valid';
        }
    });
    
    updateCertificateTable();
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// Global functions for external access
window.CertificateManager = {
    viewCertificate: function(certId) {
        console.log('🔧 CertificateManager.viewCertificate called with:', certId);
        viewCertificate(certId);
    },
    
    downloadCertificate: function(certId) {
        console.log('🔧 CertificateManager.downloadCertificate called with:', certId);
        downloadCertificate(certId);
    },
    
    renewCertificate: function(certId) {
        console.log('🔧 CertificateManager.renewCertificate called with:', certId);
        renewCertificate(certId, null);
    },
    
    issueNewCertificate: function() {
        console.log('🔧 CertificateManager.issueNewCertificate called');
        issueNewCertificate();
    },
    
    refreshCertificates: function() {
        console.log('🔧 CertificateManager.refreshCertificates called');
        refreshCertificates();
    },
    
    exportCertificates: function() {
        console.log('🔧 CertificateManager.exportCertificates called');
        exportCertificates();
    },
    
    bulkRenewal: function() {
        console.log('🔧 CertificateManager.bulkRenewal called');
        bulkRenewal();
    }
};

console.log('🔧 CertificateManager global object created');
console.log('🔍 Certificate Manager functions available:');
console.log('  - View certificates: ✅');
console.log('  - Download certificates: ✅');
console.log('  - Renew certificates: ✅');
console.log('  - Issue new certificates: ✅');
console.log('  - Refresh certificates: ✅');
console.log('  - Export certificates: ✅');
console.log('  - Bulk renewal: ✅');

// Cleanup function
function cleanup() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
}

// Cleanup on page unload
window.addEventListener('beforeunload', cleanup); 