/**
 * Twin Registry JavaScript
 * Handles AASX Integration and twin management functionality
 */

// Setup auto-generation functionality
function setupAutoGeneration() {
    console.log('Setting up auto-generation functionality...');
    // This function can be used for any auto-generation features
    // Currently not needed, but keeping for future use
}

$(document).ready(function() {
    console.log('Twin Registry JavaScript loaded');
    
    // Setup auto-generation
    setupAutoGeneration();
    
    // AASX Integration Section Toggle
    $('#showAASXSection').click(function() {
        console.log('=== AASX INTEGRATION BUTTON CLICKED ===');
        const aasxSection = $('#aasxSection');
        const addTwinButton = $('#addTwin');
        const twinRegistryTable = $('#twinRegistryTable');

        console.log('AASX Section visibility before:', aasxSection.is(':visible'));
        console.log('AASX Section element:', aasxSection.length > 0 ? 'Found' : 'NOT FOUND');

        if (aasxSection.is(':visible')) {
            console.log('Hiding AASX section...');
            aasxSection.hide();
            addTwinButton.show();
            twinRegistryTable.show();
            $(this).html('<i class="fas fa-file-archive"></i> AASX Integration');
        } else {
            console.log('Showing AASX section...');
            aasxSection.show();
            addTwinButton.hide();
            twinRegistryTable.hide();
            $(this).html('<i class="fas fa-plus"></i> Add Twin');
            
            console.log('AASX Section visibility after show:', aasxSection.is(':visible'));
            
            // Don't auto-load projects - let user control this manually
            console.log('AASX section opened - user can manually load projects');
        }
    });
    
    // Load projects
    $('#loadProjects').click(function() {
        console.log('Loading projects...');
        const button = $(this);
        button.prop('disabled', true);
        button.html('<i class="fas fa-spinner fa-spin"></i> Loading...');
        
        fetch('/twin-registry/api/aasx/projects')
            .then(response => response.json())
            .then(data => {
                console.log('Projects loaded:', data);
                displayProjects(data.projects);
                $('#projectsList').show();
                $('#projectSelection').show();
                $('#aasxFilesList').hide(); // Hide files list when showing projects
                showNotification(`Loaded ${data.total_count} projects`, 'success');
            })
            .catch(error => {
                console.error('Error loading projects:', error);
                showNotification('Error loading projects', 'error');
            })
            .finally(() => {
                button.prop('disabled', false);
                button.html('<i class="fas fa-folder"></i> Load Projects');
            });
    });
    
    // Discover AASX files (shows ALL files across ALL projects)
    $('#discoverAASXFiles').click(function() {
        console.log('Discovering ALL AASX files...');
        const button = $(this);
        button.prop('disabled', true);
        button.html('<i class="fas fa-spinner fa-spin"></i> Discovering...');
        
        fetch('/twin-registry/api/aasx/discover')
            .then(response => response.json())
            .then(data => {
                console.log('All AASX files discovered:', data);
                displayAASXFiles(data.files, 'All Projects');
                $('#aasxFilesList').show();
                $('#projectsList').hide(); // Hide projects when showing all files
                showNotification(`Discovered ${data.total_count} processed AASX files across all projects`, 'success');
            })
            .catch(error => {
                console.error('Error discovering AASX files:', error);
                showNotification('Error discovering AASX files', 'error');
            })
            .finally(() => {
                button.prop('disabled', false);
                button.html('<i class="fas fa-search"></i> Discover All Files');
            });
    });
    
    // Back to Projects button
    $('#backToProjects').click(function() {
        $('#aasxFilesList').hide();
        $('#projectsList').show();
        showNotification('Returned to projects view', 'info');
    });
    
    // Register All Twins button
    $('#registerAllTwins').click(function() {
        console.log('Registering all twins...');
        const button = $(this);
        button.prop('disabled', true);
        button.html('<i class="fas fa-spinner fa-spin"></i> Registering All...');
        
        fetch('/twin-registry/api/aasx/auto-register-all', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('All twins registered:', data);
            showNotification(`Successfully registered ${data.registered_count} twins!`, 'success');
            // Refresh the current view
            if ($('#aasxFilesList').is(':visible')) {
                // If we're viewing files, refresh the files list
                const currentProjectId = $('#projectSelect').val();
                if (currentProjectId) {
                    loadProjectFiles(currentProjectId);
                }
            } else {
                // If we're viewing projects, refresh the projects list
                $('#loadProjects').click();
            }
        })
        .catch(error => {
            console.error('Error registering all twins:', error);
            showNotification('Error registering twins', 'error');
        })
        .finally(() => {
            button.prop('disabled', false);
            button.html('<i class="fas fa-magic"></i> Register All Twins');
        });
    });
    
    // Project selection change
    $('#projectSelect').change(function() {
        const projectId = $(this).val();
        if (projectId) {
            loadProjectFiles(projectId);
        }
    });
    
    // Auto-register project
    $('#autoRegisterProject').click(function() {
        const projectId = $('#projectSelect').val();
        if (!projectId) {
            showNotification('Please select a project first', 'warning');
            return;
        }
        
        const button = $(this);
        button.prop('disabled', true);
        button.html('<i class="fas fa-spinner fa-spin"></i> Registering...');
        
        fetch(`/twin-registry/api/aasx/projects/${projectId}/auto-register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            showNotification(`Project registration: ${data.successful_registrations} successful, ${data.failed_registrations} failed`, 'success');
            // Refresh the project files
            loadProjectFiles(projectId);
        })
        .catch(error => {
            console.error('Error auto-registering project:', error);
            showNotification('Error auto-registering project', 'error');
        })
        .finally(() => {
            button.prop('disabled', false);
            button.html('<i class="fas fa-magic"></i> Auto-Register Project');
        });
    });
    
    // Display projects
    function displayProjects(projects) {
        const tbody = $('#projectsTable tbody');
        tbody.empty();
        
        projects.forEach(project => {
            const legacyBadge = project.legacy ? '<span class="badge bg-warning ms-2">Legacy</span>' : '';
            tbody.append(`
                <tr>
                    <td><code>${project.project_id}</code></td>
                    <td>${project.name}${legacyBadge}</td>
                    <td><span class="badge bg-info">${project.file_count} files</span></td>
                    <td>${new Date(project.created_at).toLocaleDateString()}</td>
                    <td>
                        <div class="btn-group" role="group">
                            <button class="btn btn-sm btn-primary load-project-files" data-project-id="${project.project_id}" title="View files for this project">
                                <i class="fas fa-folder-open"></i> View Files
                            </button>
                            <button class="btn btn-sm btn-outline-info discover-project-files" data-project-id="${project.project_id}" title="Discover all files for this project">
                                <i class="fas fa-search"></i> Discover Files
                            </button>
                            <button class="btn btn-sm btn-outline-success auto-register-project" data-project-id="${project.project_id}" title="Auto-register all twins for this project">
                                <i class="fas fa-magic"></i> Auto-Register
                            </button>
                        </div>
                    </td>
                </tr>
            `);
        });
        
        // Bind event handlers
        $('.load-project-files').click(function() {
            const projectId = $(this).data('project-id');
            $('#projectSelect').val(projectId).trigger('change');
        });
        
        $('.discover-project-files').click(function() {
            const projectId = $(this).data('project-id');
            const projectName = $(this).closest('tr').find('td:eq(1)').text().trim();
            discoverProjectFiles(projectId, projectName);
        });
        
        $('.auto-register-project').click(function() {
            const projectId = $(this).data('project-id');
            const projectName = $(this).closest('tr').find('td:eq(1)').text().trim();
            autoRegisterProject(projectId, projectName);
        });
    }
    
    // Discover project files (when Discover Files is clicked for a specific project)
    function discoverProjectFiles(projectId, projectName) {
        console.log(`Discovering files for project: ${projectId} (${projectName})`);
        
        fetch(`/twin-registry/api/aasx/projects/${projectId}/files`)
            .then(response => response.json())
            .then(data => {
                displayAASXFiles(data.files, projectName);
                $('#aasxFilesList').show();
                $('#projectsList').hide(); // Hide projects when showing files
                showNotification(`Discovered ${data.total_count} files for ${projectName}`, 'success');
            })
            .catch(error => {
                console.error('Error discovering project files:', error);
                showNotification('Error discovering project files', 'error');
            });
    }
    
    // Auto-register project (when Auto-Register is clicked for a specific project)
    function autoRegisterProject(projectId, projectName) {
        console.log(`Auto-registering twins for project: ${projectId} (${projectName})`);
        
        const button = $(`.auto-register-project[data-project-id="${projectId}"]`);
        button.prop('disabled', true);
        button.html('<i class="fas fa-spinner fa-spin"></i> Registering...');
        
        fetch(`/twin-registry/api/aasx/projects/${projectId}/auto-register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(`Project ${projectName}: ${data.successful_registrations} successful, ${data.failed_registrations} failed`, 'success');
                // Refresh the projects list to show updated status
                $('#loadProjects').click();
            } else {
                showNotification(`Error auto-registering project ${projectName}: ${data.error}`, 'error');
            }
        })
        .catch(error => {
            console.error('Error auto-registering project:', error);
            showNotification('Error auto-registering project', 'error');
        })
        .finally(() => {
            button.prop('disabled', false);
            button.html('<i class="fas fa-magic"></i> Auto-Register');
        });
    }
    
    // Load project files (when View Files is clicked)
    function loadProjectFiles(projectId) {
        console.log(`Loading files for project: ${projectId}`);
        
        fetch(`/twin-registry/api/aasx/projects/${projectId}/files`)
            .then(response => response.json())
            .then(data => {
                // Get project name for display
                const projectName = $('#projectSelect option:selected').text() || `Project ${projectId}`;
                displayAASXFiles(data.files, projectName);
                $('#aasxFilesList').show();
                $('#projectsList').hide(); // Hide projects when showing files
                showNotification(`Loaded ${data.total_count} files for ${projectName}`, 'success');
            })
            .catch(error => {
                console.error('Error loading project files:', error);
                showNotification('Error loading project files', 'error');
            });
    }
    
    // Display AASX files with project context
    function displayAASXFiles(files, projectContext = '') {
        const tbody = $('#aasxFilesTable tbody');
        tbody.empty();
        
        // Update table header to show context
        const tableHeader = $('#aasxFilesTable thead tr');
        if (projectContext && projectContext !== 'All Projects') {
            tableHeader.find('th:eq(1)').html(`Project <small class="text-muted">(${projectContext})</small>`);
        } else {
            tableHeader.find('th:eq(1)').html('Project');
        }
        
        if (files.length === 0) {
            tbody.append('<tr><td colspan="8" class="text-center text-muted">No processed AASX files found.</td></tr>');
            $('#registerAllTwins').hide();
            return;
        }
        
        let unregisteredCount = 0;
        
        files.forEach(file => {
            const isRegistered = file.twin_id ? 'Registered' : 'Not Registered';
            const statusClass = file.twin_id ? 'success' : 'warning';
            
            if (!file.twin_id) {
                unregisteredCount++;
            }
            
            // Format available formats as badges
            const formatBadges = (file.available_formats || []).map(format => 
                `<span class="badge bg-secondary me-1">${format}</span>`
            ).join('');
            
            // Use project_name if available, otherwise fallback to project_id
            const projectDisplay = file.project_name || file.project_id || 'Unknown Project';
            
            tbody.append(`
                <tr>
                    <td><i class="fas fa-file-archive text-primary me-2"></i>${file.aasx_filename}</td>
                    <td><span class="badge bg-secondary">${projectDisplay}</span></td>
                    <td>${new Date(file.processed_at).toLocaleString()}</td>
                    <td>${file.twin_name || 'N/A'}</td>
                    <td><span class="badge bg-info">${file.twin_type || 'unknown'}</span></td>
                    <td>${formatBadges || '<span class="text-muted">None</span>'}</td>
                    <td><span class="badge bg-${statusClass}">${isRegistered}</span></td>
                    <td>
                        ${file.twin_id ? 
                            `<button class="btn btn-sm btn-primary view-sync-status" data-twin-id="${file.twin_id}">
                                <i class="fas fa-sync"></i> Sync Status
                            </button>` :
                            `<button class="btn btn-sm btn-success register-twin" data-filename="${file.aasx_filename}" data-project="${file.project_id}">
                                <i class="fas fa-plus"></i> Register Twin
                            </button>`
                        }
                    </td>
                </tr>
            `);
        });
        
        // Show/hide Register All Twins button based on unregistered count
        if (unregisteredCount > 0) {
            $('#registerAllTwins').show().html(`<i class="fas fa-magic"></i> Register All Twins (${unregisteredCount})`);
        } else {
            $('#registerAllTwins').hide();
        }
        
        // Bind event handlers
        $('.register-twin').click(function() {
            const filename = $(this).data('filename');
            const project = $(this).data('project');
            registerTwinFromAASX(filename, project, $(this));
        });
        
        $('.view-sync-status').click(function() {
            const twinId = $(this).data('twin-id');
            viewSyncStatus(twinId);
        });
    }
    
    // Register twin from AASX
    function registerTwinFromAASX(filename, project, button) {
        button.prop('disabled', true);
        button.html('<i class="fas fa-spinner fa-spin"></i> Registering...');
        
        fetch('/twin-registry/api/twins/register-from-aasx', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                aasx_filename: filename,
                project_id: project
            })
        })
        .then(response => response.json())
        .then(data => {
            showNotification(`Twin ${data.twin_id} registered successfully!`, 'success');
            
            // Refresh the current files view
            if ($('#aasxFilesList').is(':visible')) {
                // If we're viewing files for a specific project, refresh that project's files
                const currentProjectId = $('#projectSelect').val();
                if (currentProjectId) {
                    loadProjectFiles(currentProjectId);
                } else {
                    // If we're viewing all files, refresh the discover view
                    const currentProjectName = $('#aasxFilesTable thead tr th:eq(1)').text().replace('Project', '').replace(/[()]/g, '').trim();
                    if (currentProjectName && currentProjectName !== 'Project') {
                        discoverProjectFiles(project, currentProjectName);
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error registering twin:', error);
            showNotification('Error registering twin', 'error');
        })
        .finally(() => {
            button.prop('disabled', false);
            button.html('<i class="fas fa-plus"></i> Register Twin');
        });
    }
    
    // View sync status
    function viewSyncStatus(twinId) {
        fetch(`/twin-registry/api/twins/${twinId}/sync-status`)
            .then(response => response.json())
            .then(data => {
                const status = data.sync_status || 'unknown';
                const lastSync = data.last_sync || 'Never';
                const dataPoints = data.data_points || 0;
                
                showNotification(`Twin ${twinId}: Status ${status}, Last Sync: ${lastSync}, Data Points: ${dataPoints}`, 'info');
            })
            .catch(error => {
                console.error('Error getting sync status:', error);
                showNotification('Error getting sync status', 'error');
            });
    }
    
    // Show notification
    function showNotification(message, type) {
        if (window.AASXFramework && window.AASXFramework.showNotification) {
            window.AASXFramework.showNotification(message, type);
        } else {
            alert(message);
        }
    }
    
    // Legacy button handlers for backward compatibility
    $('#discoverAASX').click(function() {
        $('#showAASXSection').click();
        setTimeout(() => $('#discoverAASXFiles').click(), 600);
    });
    
    $('#autoRegisterAll').click(function() {
        $('#showAASXSection').click();
        setTimeout(() => $('#loadProjects').click(), 600);
    });
    
    // Other twin registry functionality
    $('#refreshRegistry').click(function() {
        location.reload();
    });
    
    // Export data
    $('#exportData').click(function() {
        alert('Exporting twin registry data...');
    });
    
    // Bulk update
    $('#bulkUpdate').click(function() {
        alert('Bulk update functionality');
    });
    
    console.log('Twin Registry event handlers bound');
}); 