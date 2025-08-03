-- AASX Digital Database Schema
-- Database: aasx_digital.db
-- Purpose: Centralized storage for projects, files, twins, and processing data

-- ============================================================================
-- PROJECTS TABLE
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
    metadata TEXT -- JSON object for additional metadata
);

-- ============================================================================
-- PROJECT FILES TABLE
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
    
    -- Foreign key constraints
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    
    -- Indexes for performance
    INDEX idx_project_id (project_id),
    INDEX idx_filename (filename),
    INDEX idx_status (status),
    INDEX idx_twin_id (twin_id),
    INDEX idx_upload_date (upload_date)
);

-- ============================================================================
-- TWINS TABLE (Enhanced from existing twin_aasx_relationships)
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
    
    -- Foreign key constraints
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (aasx_filename) REFERENCES project_files(filename) ON DELETE CASCADE,
    
    -- Indexes for performance
    INDEX idx_project_id (project_id),
    INDEX idx_status (status),
    INDEX idx_filename (aasx_filename),
    INDEX idx_twin_type (twin_type)
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
    
    -- Foreign key constraints
    FOREIGN KEY (file_id) REFERENCES project_files(file_id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_file_id (file_id),
    INDEX idx_project_id (project_id),
    INDEX idx_status (processing_status),
    INDEX idx_timestamp (timestamp)
);

-- ============================================================================
-- TWIN HEALTH METRICS TABLE
-- ============================================================================
CREATE TABLE twin_health_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    twin_id VARCHAR(100) NOT NULL,
    uptime_percentage REAL,
    response_time_ms REAL,
    error_rate REAL,
    data_quality_score REAL,
    last_health_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    FOREIGN KEY (twin_id) REFERENCES twins(twin_id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_twin_id (twin_id),
    INDEX idx_last_check (last_health_check)
);

-- ============================================================================
-- TWIN EVENTS TABLE
-- ============================================================================
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
    
    -- Indexes
    INDEX idx_twin_id (twin_id),
    INDEX idx_event_type (event_type),
    INDEX idx_severity (severity),
    INDEX idx_timestamp (timestamp)
);

-- ============================================================================
-- TWIN OPERATIONS TABLE
-- ============================================================================
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
    
    -- Indexes
    INDEX idx_twin_id (twin_id),
    INDEX idx_operation_type (operation_type),
    INDEX idx_status (status),
    INDEX idx_started_at (started_at)
);

-- ============================================================================
-- SYNC HISTORY TABLE
-- ============================================================================
CREATE TABLE sync_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    twin_id VARCHAR(100) NOT NULL,
    sync_type VARCHAR(50) NOT NULL,
    sync_status VARCHAR(20) NOT NULL,
    sync_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details TEXT, -- JSON object with sync details
    
    -- Foreign key constraints
    FOREIGN KEY (twin_id) REFERENCES twins(twin_id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_twin_id (twin_id),
    INDEX idx_sync_type (sync_type),
    INDEX idx_sync_status (sync_status),
    INDEX idx_sync_timestamp (sync_timestamp)
);

-- ============================================================================
-- PERFORMANCE METRICS TABLE
-- ============================================================================
CREATE TABLE performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    twin_id VARCHAR(100) NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    value REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    unit VARCHAR(20) NOT NULL,
    description TEXT,
    
    -- Foreign key constraints
    FOREIGN KEY (twin_id) REFERENCES twins(twin_id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_twin_id (twin_id),
    INDEX idx_metric_type (metric_type),
    INDEX idx_timestamp (timestamp)
);

-- ============================================================================
-- SYSTEM CONFIGURATION TABLE
-- ============================================================================
CREATE TABLE system_config (
    config_key VARCHAR(100) PRIMARY KEY,
    config_value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Project Summary View
CREATE VIEW project_summary AS
SELECT 
    p.project_id,
    p.name,
    p.description,
    p.tags,
    p.file_count,
    p.total_size,
    p.created_at,
    p.updated_at,
    COUNT(pf.file_id) as actual_file_count,
    COUNT(t.twin_id) as actual_twin_count,
    SUM(pf.size) as actual_total_size,
    COUNT(CASE WHEN pf.status = 'completed' THEN 1 END) as completed_files,
    COUNT(CASE WHEN pf.status = 'not_processed' THEN 1 END) as pending_files,
    COUNT(CASE WHEN pf.status = 'error' THEN 1 END) as error_files
FROM projects p
LEFT JOIN project_files pf ON p.project_id = pf.project_id
LEFT JOIN twins t ON p.project_id = t.project_id
GROUP BY p.project_id, p.name, p.description, p.tags, p.file_count, p.total_size, p.created_at, p.updated_at;

-- File Status Summary View
CREATE VIEW file_status_summary AS
SELECT 
    project_id,
    status,
    COUNT(*) as file_count,
    SUM(size) as total_size,
    AVG(size) as avg_size
FROM project_files
GROUP BY project_id, status;

-- Twin Status Summary View
CREATE VIEW twin_status_summary AS
SELECT 
    project_id,
    status,
    twin_type,
    COUNT(*) as twin_count,
    SUM(data_points) as total_data_points
FROM twins
GROUP BY project_id, status, twin_type;

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
        updated_at = CURRENT_TIMESTAMP
    WHERE file_id = NEW.file_id;
END;

-- ============================================================================
-- INITIAL DATA INSERTION (System Configuration)
-- ============================================================================

INSERT INTO system_config (config_key, config_value, description) VALUES
('database_version', '1.0.0', 'Current database schema version'),
('migration_date', datetime('now'), 'Date when migration was completed'),
('system_name', 'AASX Digital Twin Platform', 'System name'),
('max_file_size', '104857600', 'Maximum file size in bytes (100MB)'),
('supported_formats', '["aasx", "json", "yaml", "rdf"]', 'Supported file formats'),
('processing_timeout', '300', 'Processing timeout in seconds');

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Additional composite indexes for common query patterns
CREATE INDEX idx_project_status ON project_files(project_id, status);
CREATE INDEX idx_twin_project_status ON twins(project_id, status);
CREATE INDEX idx_processing_file_status ON processing_results(file_id, processing_status);
CREATE INDEX idx_events_twin_timestamp ON twin_events(twin_id, timestamp);
CREATE INDEX idx_operations_twin_type ON twin_operations(twin_id, operation_type);
CREATE INDEX idx_metrics_twin_type_timestamp ON performance_metrics(twin_id, metric_type, timestamp);

-- ============================================================================
-- COMMENTS AND DOCUMENTATION
-- ============================================================================

-- Add comments to tables for documentation
PRAGMA table_info(projects);
PRAGMA table_info(project_files);
PRAGMA table_info(twins);
PRAGMA table_info(processing_results);
PRAGMA table_info(twin_health_metrics);
PRAGMA table_info(twin_events);
PRAGMA table_info(twin_operations);
PRAGMA table_info(sync_history);
PRAGMA table_info(performance_metrics);
PRAGMA table_info(system_config); 