# User-Based Architecture Proposal for AASX Digital Twin Framework

## 🎯 **Overview**

Transform the current project-centric system into a **user-based multi-tenant platform** where:
- **Users** can own multiple projects
- **Projects** belong to specific users
- **Access control** at user, project, and file levels
- **Collaboration** features for shared projects
- **Role-based permissions** for different user types

## 🏗️ **Enhanced Database Schema**

### **New Tables for User Management**

#### **1. users**
```sql
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
```

#### **2. user_sessions**
```sql
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
```

#### **3. project_permissions**
```sql
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
```

#### **4. user_activity_log**
```sql
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
```

### **Modified Existing Tables**

#### **Updated projects table**
```sql
ALTER TABLE projects ADD COLUMN owner_id VARCHAR(100) NOT NULL DEFAULT 'system';
ALTER TABLE projects ADD COLUMN is_public BOOLEAN DEFAULT 0;
ALTER TABLE projects ADD COLUMN access_level VARCHAR(20) DEFAULT 'private'; -- 'private', 'shared', 'public'
ALTER TABLE projects ADD COLUMN collaborators TEXT; -- JSON array of user IDs

-- Add foreign key
ALTER TABLE projects ADD CONSTRAINT fk_projects_owner 
    FOREIGN KEY (owner_id) REFERENCES users(user_id);
```

#### **Updated twins table**
```sql
ALTER TABLE twins ADD COLUMN created_by VARCHAR(100);
ALTER TABLE twins ADD COLUMN last_modified_by VARCHAR(100);

-- Add foreign keys
ALTER TABLE twins ADD CONSTRAINT fk_twins_created_by 
    FOREIGN KEY (created_by) REFERENCES users(user_id);
ALTER TABLE twins ADD CONSTRAINT fk_twins_modified_by 
    FOREIGN KEY (last_modified_by) REFERENCES users(user_id);
```

#### **Updated project_files table**
```sql
ALTER TABLE project_files ADD COLUMN uploaded_by VARCHAR(100);
ALTER TABLE project_files ADD COLUMN last_modified_by VARCHAR(100);

-- Add foreign keys
ALTER TABLE project_files ADD CONSTRAINT fk_files_uploaded_by 
    FOREIGN KEY (uploaded_by) REFERENCES users(user_id);
ALTER TABLE project_files ADD CONSTRAINT fk_files_modified_by 
    FOREIGN KEY (last_modified_by) REFERENCES users(user_id);
```

## 🔐 **Permission System**

### **Permission Levels**
1. **Owner**: Full control (create, read, update, delete, share)
2. **Admin**: Full control except ownership transfer
3. **Editor**: Create, read, update (no delete, no share)
4. **Viewer**: Read-only access
5. **Public**: Anyone can view (for public projects)

### **Permission Matrix**
| Action | Owner | Admin | Editor | Viewer | Public |
|--------|-------|-------|--------|--------|--------|
| View Project | ✅ | ✅ | ✅ | ✅ | ✅ |
| Create Files | ✅ | ✅ | ✅ | ❌ | ❌ |
| Edit Files | ✅ | ✅ | ✅ | ❌ | ❌ |
| Delete Files | ✅ | ✅ | ❌ | ❌ | ❌ |
| Share Project | ✅ | ❌ | ❌ | ❌ | ❌ |
| Delete Project | ✅ | ❌ | ❌ | ❌ | ❌ |
| Manage Users | ✅ | ✅ | ❌ | ❌ | ❌ |

## 🏢 **Multi-Tenant Architecture**

### **User Isolation**
- **Data Segregation**: Users can only access their own projects
- **Resource Limits**: Per-user quotas for storage, processing, twins
- **Billing**: Per-user usage tracking and billing
- **Customization**: User-specific settings and preferences

### **Organization Support**
```sql
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
```

## 🔄 **API Changes**

### **Authentication Endpoints**
```python
# New authentication routes
@app.route('/api/auth/register', methods=['POST'])
@app.route('/api/auth/login', methods=['POST'])
@app.route('/api/auth/logout', methods=['POST'])
@app.route('/api/auth/refresh', methods=['POST'])
@app.route('/api/auth/profile', methods=['GET', 'PUT'])
```

### **User Management Endpoints**
```python
# User management routes
@app.route('/api/users', methods=['GET'])  # Admin only
@app.route('/api/users/<user_id>', methods=['GET', 'PUT', 'DELETE'])
@app.route('/api/users/<user_id>/projects', methods=['GET'])
@app.route('/api/users/<user_id>/activity', methods=['GET'])
```

### **Modified Project Endpoints**
```python
# Updated project routes with user context
@app.route('/api/projects', methods=['GET'])  # Returns user's projects
@app.route('/api/projects', methods=['POST'])  # Creates project for current user
@app.route('/api/projects/<project_id>/share', methods=['POST'])
@app.route('/api/projects/<project_id>/permissions', methods=['GET', 'PUT'])
```

### **Permission Middleware**
```python
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract user from JWT token
        # Verify user permissions for requested resource
        pass
    return decorated_function

def require_permission(permission_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user has required permission
            pass
        return decorated_function
    return decorator
```

## 🎨 **Frontend Changes**

### **User Interface Updates**
1. **Login/Register Pages**: User authentication
2. **User Dashboard**: Personal overview and settings
3. **Project Sharing**: Invite collaborators
4. **Permission Management**: Manage project access
5. **User Profile**: Personal information and preferences

### **Navigation Structure**
```
Dashboard (User Overview)
├── My Projects
├── Shared with Me
├── Public Projects
├── Activity Log
└── Settings
    ├── Profile
    ├── Preferences
    ├── Security
    └── Billing
```

## 📊 **Data Migration Strategy**

### **Phase 1: Schema Migration**
1. Add user tables to existing database
2. Create default admin user
3. Migrate existing projects to admin user
4. Update foreign key constraints

### **Phase 2: User Onboarding**
1. Create user registration system
2. Implement authentication
3. Add permission checks to existing APIs
4. Create user management interface

### **Phase 3: Advanced Features**
1. Organization support
2. Advanced permission system
3. Collaboration features
4. Usage analytics and billing

## 🔧 **Implementation Benefits**

### **For Users**
- **Personal Workspace**: Own projects and data
- **Collaboration**: Share projects with team members
- **Security**: Data isolation and access control
- **Customization**: Personal settings and preferences

### **For Organizations**
- **Multi-User Support**: Team collaboration
- **Resource Management**: Usage quotas and limits
- **Audit Trail**: Complete activity logging
- **Scalability**: Support for large teams

### **For Platform**
- **Monetization**: User-based billing and plans
- **Analytics**: Usage patterns and insights
- **Compliance**: Data governance and privacy
- **Growth**: Scalable user base

## 🚀 **Implementation Timeline**

### **Week 1-2: Foundation**
- Database schema updates
- User authentication system
- Basic permission middleware

### **Week 3-4: Core Features**
- User registration and login
- Project ownership and permissions
- Updated API endpoints

### **Week 5-6: Frontend**
- User interface updates
- Authentication flows
- Permission management UI

### **Week 7-8: Advanced Features**
- Organization support
- Collaboration features
- Usage analytics

## 💡 **Migration Considerations**

### **Existing Data**
- All current projects become owned by default admin user
- Existing twins and files maintain their relationships
- No data loss during migration

### **Backward Compatibility**
- API endpoints maintain existing structure
- Add user context as additional parameters
- Gradual migration of existing integrations

### **Security**
- JWT-based authentication
- Role-based access control
- Data encryption for sensitive information
- Audit logging for all user actions

---

**Status**: 🎯 **Ready for Implementation**

This user-based architecture transforms the current project-centric system into a robust multi-tenant platform while maintaining all existing functionality and adding powerful collaboration features. 