-- AASX Digital Database Schema with User Management (Fixed for SQLite)
-- Database: aasx_digital.db
-- Purpose: Centralized storage for users, projects, files, twins, and processing data
-- Features: Multi-tenant, user-based access control, collaboration

-- ============================================================================
-- USER MANAGEMENT TABLES
-- ============================================================================

CREATE TABLE users (
    user_id VARCHAR(100) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    organization VARCHAR(255),
    role VARCHAR(20) DEFAULT 'user', -- 'admin', 'user', 'viewer'
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'inactive', 'suspended'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    preferences TEXT, -- JSON object for user preferences
    metadata TEXT -- JSON object for additional metadata
);

CREATE TABLE user_sessions (
    session_id VARCHAR(100) PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    is_active BOOLEAN DEFAULT 1,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE user_activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(100) NOT NULL,
    activity_type VARCHAR(50) NOT NULL, -- 'login', 'project_create', 'file_upload', etc.
    resource_type VARCHAR(50), -- 'project', 'file', 'twin'
    resource_id VARCHAR(100),
    details TEXT, -- JSON object with activity details
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================================================
-- ORGANIZATION SUPPORT
-- ============================================================================

CREATE TABLE organizations (
    org_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    domain VARCHAR(255),
    plan_type VARCHAR(20) DEFAULT 'basic', -- 'basic', 'pro', 'enterprise'
    max_users INTEGER DEFAULT 10,
    max_projects INTEGER DEFAULT 100,
    max_storage_gb INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active'
);

CREATE TABLE user_organizations (
    user_id VARCHAR(100) NOT NULL,
    org_id VARCHAR(100) NOT NULL,
    role VARCHAR(20) DEFAULT 'member', -- 'owner', 'admin', 'member'
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (user_id, org_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (org_id) REFERENCES organizations(org_id) ON DELETE CASCADE
);

-- ============================================================================
-- PROJECTS TABLE (Enhanced with User Management)
-- ============================================================================

CREATE TABLE projects (
    project_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    tags TEXT, -- JSON array of tags
    file_count INTEGER DEFAULT 0,
    total_size BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT, -- JSON object for additional metadata
    
    -- User management fields
    owner_id VARCHAR(100) NOT NULL,
    is_public BOOLEAN DEFAULT 0,
    access_level VARCHAR(20) DEFAULT 'private', -- 'private', 'shared', 'public'
    collaborators TEXT, -- JSON array of user IDs
    
    -- Foreign key constraints
    FOREIGN KEY (owner_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE project_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id VARCHAR(100) NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    permission_type VARCHAR(20) NOT NULL, -- 'owner', 'admin', 'editor', 'viewer'
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    granted_by VARCHAR(100),
    expires_at TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES users(user_id),
    
    UNIQUE(project_id, user_id)
);

-- ============================================================================
-- PROJECT FILES TABLE (Enhanced with User Management)
-- ============================================================================

CREATE TABLE project_files (
    file_id VARCHAR(100) PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    project_id VARCHAR(100) NOT NULL,
    filepath TEXT NOT NULL,
    size BIGINT NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    status VARCHAR(20) DEFAULT 'uploaded',
    file_type VARCHAR(10),
    file_type_description VARCHAR(100),
    processing_result TEXT, -- JSON object with processing details
    twin_id VARCHAR(100), -- Reference to twin if registered
    
    -- User management fields
    uploaded_by VARCHAR(100),
    last_modified_by VARCHAR(100),
    
    -- Foreign key constraints
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(user_id),
    FOREIGN KEY (last_modified_by) REFERENCES users(user_id)
);

-- ============================================================================
-- TWINS TABLE (Enhanced with User Management)
-- ============================================================================

CREATE TABLE twins (
    twin_id VARCHAR(100) PRIMARY KEY,
    aasx_filename VARCHAR(255) NOT NULL,
    project_id VARCHAR(100) NOT NULL,
    aas_id VARCHAR(100),
    twin_name VARCHAR(255),
    twin_type VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_sync TIMESTAMP,
    data_points INTEGER DEFAULT 0,
    metadata TEXT, -- JSON object with twin metadata
    
    -- User management fields
    created_by VARCHAR(100),
    last_modified_by VARCHAR(100),
    
    -- Foreign key constraints
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (aasx_filename) REFERENCES project_files(filename) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(user_id),
    FOREIGN KEY (last_modified_by) REFERENCES users(user_id)
);

-- ============================================================================
-- PROCESSING RESULTS TABLE
-- ============================================================================

CREATE TABLE processing_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id VARCHAR(100) NOT NULL,
    project_id VARCHAR(100) NOT NULL,
    processing_status VARCHAR(20) NOT NULL,
    processing_time REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    output_directory TEXT,
    extraction_results TEXT, -- JSON object with detailed results
    error_message TEXT,
    
    -- User management fields
    processed_by VARCHAR(100),
    
    -- Foreign key constraints
    FOREIGN KEY (file_id) REFERENCES project_files(file_id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (processed_by) REFERENCES users(user_id)
);

-- ============================================================================
-- TWIN MANAGEMENT TABLES
-- ============================================================================

CREATE TABLE twin_health_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    twin_id VARCHAR(100) NOT NULL,
    uptime_percentage REAL,
    response_time_ms REAL,
    error_rate REAL,
    data_quality_score REAL,
    last_health_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- User management fields
    checked_by VARCHAR(100),
    
    -- Foreign key constraints
    FOREIGN KEY (twin_id) REFERENCES twins(twin_id) ON DELETE CASCADE,
    FOREIGN KEY (checked_by) REFERENCES users(user_id)
);

CREATE TABLE twin_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    twin_id VARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_message TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user VARCHAR(100) DEFAULT 'system',
    metadata TEXT, -- JSON object with event metadata
    
    -- Foreign key constraints
    FOREIGN KEY (twin_id) REFERENCES twins(twin_id) ON DELETE CASCADE,
    FOREIGN KEY (user) REFERENCES users(user_id)
);

CREATE TABLE twin_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    twin_id VARCHAR(100) NOT NULL,
    operation_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    result TEXT,
    error_message TEXT,
    user VARCHAR(100) DEFAULT 'system',
    
    -- Foreign key constraints
    FOREIGN KEY (twin_id) REFERENCES twins(twin_id) ON DELETE CASCADE,
    FOREIGN KEY (user) REFERENCES users(user_id)
);

CREATE TABLE sync_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    twin_id VARCHAR(100) NOT NULL,
    sync_type VARCHAR(50) NOT NULL,
    sync_status VARCHAR(20) NOT NULL,
    sync_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details TEXT, -- JSON object with sync details
    
    -- User management fields
    synced_by VARCHAR(100),
    
    -- Foreign key constraints
    FOREIGN KEY (twin_id) REFERENCES twins(twin_id) ON DELETE CASCADE,
    FOREIGN KEY (synced_by) REFERENCES users(user_id)
);

CREATE TABLE performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    twin_id VARCHAR(100) NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    value REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    unit VARCHAR(20) NOT NULL,
    description TEXT,
    
    -- User management fields
    recorded_by VARCHAR(100),
    
    -- Foreign key constraints
    FOREIGN KEY (twin_id) REFERENCES twins(twin_id) ON DELETE CASCADE,
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- ============================================================================
-- SYSTEM CONFIGURATION TABLE
-- ============================================================================

CREATE TABLE system_config (
    config_key VARCHAR(100) PRIMARY KEY,
    config_value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    
    FOREIGN KEY (updated_by) REFERENCES users(user_id)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- User indexes
CREATE INDEX idx_username ON users(username);
CREATE INDEX idx_email ON users(email);
CREATE INDEX idx_role ON users(role);
CREATE INDEX idx_status ON users(status);
CREATE INDEX idx_created_at ON users(created_at);

-- User sessions indexes
CREATE INDEX idx_user_id ON user_sessions(user_id);
CREATE INDEX idx_token_hash ON user_sessions(token_hash);
CREATE INDEX idx_expires_at ON user_sessions(expires_at);
CREATE INDEX idx_is_active ON user_sessions(is_active);

-- User activity indexes
CREATE INDEX idx_activity_user_id ON user_activity_log(user_id);
CREATE INDEX idx_activity_type ON user_activity_log(activity_type);
CREATE INDEX idx_resource_type ON user_activity_log(resource_type);
CREATE INDEX idx_timestamp ON user_activity_log(timestamp);

-- Organization indexes
CREATE INDEX idx_org_name ON organizations(name);
CREATE INDEX idx_org_domain ON organizations(domain);
CREATE INDEX idx_org_plan_type ON organizations(plan_type);
CREATE INDEX idx_org_status ON organizations(status);

-- User organization indexes
CREATE INDEX idx_uo_user_id ON user_organizations(user_id);
CREATE INDEX idx_uo_org_id ON user_organizations(org_id);
CREATE INDEX idx_uo_role ON user_organizations(role);

-- Project indexes
CREATE INDEX idx_project_owner_id ON projects(owner_id);
CREATE INDEX idx_project_is_public ON projects(is_public);
CREATE INDEX idx_project_access_level ON projects(access_level);
CREATE INDEX idx_project_created_at ON projects(created_at);
CREATE INDEX idx_project_updated_at ON projects(updated_at);

-- Project permissions indexes
CREATE INDEX idx_permission_project_id ON project_permissions(project_id);
CREATE INDEX idx_permission_user_id ON project_permissions(user_id);
CREATE INDEX idx_permission_type ON project_permissions(permission_type);
CREATE INDEX idx_permission_expires_at ON project_permissions(expires_at);

-- Project files indexes
CREATE INDEX idx_file_project_id ON project_files(project_id);
CREATE INDEX idx_file_filename ON project_files(filename);
CREATE INDEX idx_file_status ON project_files(status);
CREATE INDEX idx_file_twin_id ON project_files(twin_id);
CREATE INDEX idx_file_upload_date ON project_files(upload_date);
CREATE INDEX idx_file_uploaded_by ON project_files(uploaded_by);
CREATE INDEX idx_file_last_modified_by ON project_files(last_modified_by);

-- Twins indexes
CREATE INDEX idx_twin_project_id ON twins(project_id);
CREATE INDEX idx_twin_status ON twins(status);
CREATE INDEX idx_twin_filename ON twins(aasx_filename);
CREATE INDEX idx_twin_type ON twins(twin_type);
CREATE INDEX idx_twin_created_by ON twins(created_by);
CREATE INDEX idx_twin_last_modified_by ON twins(last_modified_by);

-- Processing results indexes
CREATE INDEX idx_processing_file_id ON processing_results(file_id);
CREATE INDEX idx_processing_project_id ON processing_results(project_id);
CREATE INDEX idx_processing_status ON processing_results(processing_status);
CREATE INDEX idx_processing_timestamp ON processing_results(timestamp);
CREATE INDEX idx_processing_processed_by ON processing_results(processed_by);

-- Twin health indexes
CREATE INDEX idx_health_twin_id ON twin_health_metrics(twin_id);
CREATE INDEX idx_health_last_check ON twin_health_metrics(last_health_check);
CREATE INDEX idx_health_checked_by ON twin_health_metrics(checked_by);

-- Twin events indexes
CREATE INDEX idx_events_twin_id ON twin_events(twin_id);
CREATE INDEX idx_events_type ON twin_events(event_type);
CREATE INDEX idx_events_severity ON twin_events(severity);
CREATE INDEX idx_events_timestamp ON twin_events(timestamp);
CREATE INDEX idx_events_user ON twin_events(user);

-- Twin operations indexes
CREATE INDEX idx_operations_twin_id ON twin_operations(twin_id);
CREATE INDEX idx_operations_type ON twin_operations(operation_type);
CREATE INDEX idx_operations_status ON twin_operations(status);
CREATE INDEX idx_operations_started_at ON twin_operations(started_at);
CREATE INDEX idx_operations_user ON twin_operations(user);

-- Sync history indexes
CREATE INDEX idx_sync_twin_id ON sync_history(twin_id);
CREATE INDEX idx_sync_type ON sync_history(sync_type);
CREATE INDEX idx_sync_status ON sync_history(sync_status);
CREATE INDEX idx_sync_timestamp ON sync_history(sync_timestamp);
CREATE INDEX idx_sync_synced_by ON sync_history(synced_by);

-- Performance metrics indexes
CREATE INDEX idx_metrics_twin_id ON performance_metrics(twin_id);
CREATE INDEX idx_metrics_type ON performance_metrics(metric_type);
CREATE INDEX idx_metrics_timestamp ON performance_metrics(timestamp);
CREATE INDEX idx_metrics_recorded_by ON performance_metrics(recorded_by);

-- Composite indexes for common query patterns
CREATE INDEX idx_project_owner_access_level ON projects(owner_id, access_level);
CREATE INDEX idx_file_project_status ON project_files(project_id, status);
CREATE INDEX idx_twin_project_status ON twins(project_id, status);
CREATE INDEX idx_permission_project_user ON project_permissions(project_id, user_id);
CREATE INDEX idx_activity_user_timestamp ON user_activity_log(user_id, timestamp);
CREATE INDEX idx_session_user_active ON user_sessions(user_id, is_active);
CREATE INDEX idx_org_user_role ON user_organizations(org_id, role);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- User Project Summary View
CREATE VIEW user_project_summary AS
SELECT 
    u.user_id,
    u.username,
    u.full_name,
    u.organization,
    p.project_id,
    p.name as project_name,
    p.description,
    p.tags,
    p.file_count,
    p.total_size,
    p.created_at,
    p.updated_at,
    pp.permission_type,
    COUNT(pf.file_id) as actual_file_count,
    COUNT(t.twin_id) as actual_twin_count,
    SUM(pf.size) as actual_total_size,
    COUNT(CASE WHEN pf.status = 'completed' THEN 1 END) as completed_files,
    COUNT(CASE WHEN pf.status = 'not_processed' THEN 1 END) as pending_files,
    COUNT(CASE WHEN pf.status = 'error' THEN 1 END) as error_files
FROM users u
JOIN project_permissions pp ON u.user_id = pp.user_id
JOIN projects p ON pp.project_id = p.project_id
LEFT JOIN project_files pf ON p.project_id = pf.project_id
LEFT JOIN twins t ON p.project_id = t.project_id
GROUP BY u.user_id, u.username, u.full_name, u.organization, p.project_id, p.name, p.description, p.tags, p.file_count, p.total_size, p.created_at, p.updated_at, pp.permission_type;

-- Organization Summary View
CREATE VIEW organization_summary AS
SELECT 
    o.org_id,
    o.name as org_name,
    o.description,
    o.plan_type,
    o.max_users,
    o.max_projects,
    o.max_storage_gb,
    COUNT(uo.user_id) as current_users,
    COUNT(p.project_id) as current_projects,
    SUM(p.total_size) as current_storage_bytes
FROM organizations o
LEFT JOIN user_organizations uo ON o.org_id = uo.org_id
LEFT JOIN users u ON uo.user_id = u.user_id
LEFT JOIN projects p ON u.user_id = p.owner_id
GROUP BY o.org_id, o.name, o.description, o.plan_type, o.max_users, o.max_projects, o.max_storage_gb;

-- User Activity Summary View
CREATE VIEW user_activity_summary AS
SELECT 
    u.user_id,
    u.username,
    u.full_name,
    ual.activity_type,
    COUNT(*) as activity_count,
    MAX(ual.timestamp) as last_activity
FROM users u
JOIN user_activity_log ual ON u.user_id = ual.user_id
GROUP BY u.user_id, u.username, u.full_name, ual.activity_type;

-- ============================================================================
-- TRIGGERS FOR DATA CONSISTENCY
-- ============================================================================

-- Update project file count and total size when files are added/removed
CREATE TRIGGER update_project_stats_insert
AFTER INSERT ON project_files
BEGIN
    UPDATE projects 
    SET 
        file_count = (SELECT COUNT(*) FROM project_files WHERE project_id = NEW.project_id),
        total_size = (SELECT COALESCE(SUM(size), 0) FROM project_files WHERE project_id = NEW.project_id),
        updated_at = CURRENT_TIMESTAMP
    WHERE project_id = NEW.project_id;
END;

CREATE TRIGGER update_project_stats_delete
AFTER DELETE ON project_files
BEGIN
    UPDATE projects 
    SET 
        file_count = (SELECT COUNT(*) FROM project_files WHERE project_id = OLD.project_id),
        total_size = (SELECT COALESCE(SUM(size), 0) FROM project_files WHERE project_id = OLD.project_id),
        updated_at = CURRENT_TIMESTAMP
    WHERE project_id = OLD.project_id;
END;

-- Update file status when processing results are added
CREATE TRIGGER update_file_status_processing
AFTER INSERT ON processing_results
BEGIN
    UPDATE project_files 
    SET 
        status = NEW.processing_status,
        processing_result = json_object(
            'status', NEW.processing_status,
            'processing_time', NEW.processing_time,
            'timestamp', NEW.timestamp,
            'output_directory', NEW.output_directory,
            'extraction_results', NEW.extraction_results,
            'error_message', NEW.error_message
        ),
        updated_at = CURRENT_TIMESTAMP,
        last_modified_by = NEW.processed_by
    WHERE file_id = NEW.file_id;
END;

-- Log user activity automatically
CREATE TRIGGER log_project_creation
AFTER INSERT ON projects
BEGIN
    INSERT INTO user_activity_log (user_id, activity_type, resource_type, resource_id, details)
    VALUES (NEW.owner_id, 'project_create', 'project', NEW.project_id, 
            json_object('project_name', NEW.name, 'project_id', NEW.project_id));
END;

CREATE TRIGGER log_file_upload
AFTER INSERT ON project_files
BEGIN
    INSERT INTO user_activity_log (user_id, activity_type, resource_type, resource_id, details)
    VALUES (NEW.uploaded_by, 'file_upload', 'file', NEW.file_id, 
            json_object('filename', NEW.filename, 'project_id', NEW.project_id, 'size', NEW.size));
END;

-- ============================================================================
-- INITIAL DATA INSERTION
-- ============================================================================

-- Create default admin user
INSERT INTO users (user_id, username, email, password_hash, full_name, role, status) VALUES
('admin', 'admin', 'admin@aasx-digital.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK8.', 'System Administrator', 'admin', 'active');

-- Create default organization
INSERT INTO organizations (org_id, name, description, plan_type) VALUES
('default', 'Default Organization', 'Default organization for system users', 'enterprise');

-- Add admin to default organization
INSERT INTO user_organizations (user_id, org_id, role) VALUES
('admin', 'default', 'owner');

-- System configuration
INSERT INTO system_config (config_key, config_value, description, updated_by) VALUES
('database_version', '2.0.0', 'Current database schema version with user management', 'admin'),
('migration_date', datetime('now'), 'Date when user management migration was completed', 'admin'),
('system_name', 'AASX Digital Twin Platform', 'System name', 'admin'),
('max_file_size', '104857600', 'Maximum file size in bytes (100MB)', 'admin'),
('supported_formats', '["aasx", "json", "yaml", "rdf"]', 'Supported file formats', 'admin'),
('processing_timeout', '300', 'Processing timeout in seconds', 'admin'),
('default_user_role', 'user', 'Default role for new users', 'admin'),
('session_timeout_hours', '24', 'Session timeout in hours', 'admin'),
('max_projects_per_user', '100', 'Maximum projects per user', 'admin'),
('max_files_per_project', '1000', 'Maximum files per project', 'admin'); 