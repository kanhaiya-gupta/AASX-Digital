"""
Test Models
==========

Test script to verify the Pydantic models are working correctly.
"""

import sys
import os
from datetime import datetime

# Add the parent directory to the path so we can import our models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (
    CoreSystemRegistry, CoreSystemMetrics,
    Organization, UseCase, Project, File, ProjectUseCaseLink,
    User, CustomRole, RoleAssignment, UserMetrics
)


def test_core_system_models():
    """Test core system models."""
    print("🧪 Testing Core System Models...")
    
    # Test CoreSystemRegistry
    registry = CoreSystemRegistry(
        registry_id="test-registry-001",
        system_name="Test System",
        registry_name="Test Registry",
        created_at="2025-08-20T10:00:00Z",
        updated_at="2025-08-20T10:00:00Z",
        registry_type="hybrid",
        workflow_source="both"
    )
    print(f"✅ Created CoreSystemRegistry: {registry.system_name}")
    
    # Test CoreSystemMetrics
    metrics = CoreSystemMetrics(
        metric_id="test-metric-001",
        registry_id="test-registry-001",
        metric_type="performance",
        metric_timestamp="2025-08-20T10:00:00Z",
        created_at="2025-08-20T10:00:00Z",
        updated_at="2025-08-20T10:00:00Z"
    )
    print(f"✅ Created CoreSystemMetrics: {metrics.metric_id}")
    
    return True


def test_business_domain_models():
    """Test business domain models."""
    print("🧪 Testing Business Domain Models...")
    
    # Test Organization
    org = Organization(
        org_id="test-org-001",
        name="Test Organization",
        created_at="2025-08-20T10:00:00Z",
        updated_at="2025-08-20T10:00:00Z",
        description="A test organization",
        company_size="smb",
        subscription_tier="standard"
    )
    print(f"✅ Created Organization: {org.name}")
    
    # Test UseCase
    use_case = UseCase(
        use_case_id="test-use-case-001",
        name="Test Use Case",
        created_at="2025-08-20T10:00:00Z",
        updated_at="2025-08-20T10:00:00Z",
        description="A test use case",
        data_domain="thermal",
        business_criticality="medium"
    )
    print(f"✅ Created UseCase: {use_case.name}")
    
    # Test Project
    project = Project(
        project_id="test-project-001",
        name="Test Project",
        created_at="2025-08-20T10:00:00Z",
        updated_at="2025-08-20T10:00:00Z",
        description="A test project",
        project_phase="development",
        priority_level="high"
    )
    print(f"✅ Created Project: {project.name}")
    
    # Test File
    file_obj = File(
        filename="test.txt",
        original_filename="original_test.txt",
        project_id="test-project-001",
        filepath="/path/to/test.txt",
        created_at="2025-08-20T10:00:00Z",
        updated_at="2025-08-20T10:00:00Z",
        file_type="text",
        source_type="manual_upload"
    )
    print(f"✅ Created File: {file_obj.filename}")
    
    # Test ProjectUseCaseLink
    link = ProjectUseCaseLink(
        project_id="test-project-001",
        use_case_id="test-use-case-001",
        created_at="2025-08-20T10:00:00Z"
    )
    print(f"✅ Created ProjectUseCaseLink: {link.project_id}")
    
    return True


def test_auth_models():
    """Test authentication models."""
    print("🧪 Testing Authentication Models...")
    
    # Test User
    user = User(
        user_id="test-user-001",
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        password_hash="hashed_password_123",
        role="user",
        created_at="2025-08-20T10:00:00Z",
        updated_at="2025-08-20T10:00:00Z"
    )
    print(f"✅ Created User: {user.username}")
    
    # Test CustomRole
    role = CustomRole(
        role_id="test-role-001",
        role_name="Test Role",
        role_type="custom",
        created_at="2025-08-20T10:00:00Z",
        updated_at="2025-08-20T10:00:00Z"
    )
    print(f"✅ Created CustomRole: {role.role_name}")
    
    # Test RoleAssignment
    assignment = RoleAssignment(
        assignment_id="test-assignment-001",
        user_id="test-user-001",
        role_id="test-role-001",
        assignment_type="direct",
        assigned_at="2025-08-20T10:00:00Z",
        created_at="2025-08-20T10:00:00Z",
        updated_at="2025-08-20T10:00:00Z"
    )
    print(f"✅ Created RoleAssignment: {assignment.assignment_id}")
    
    # Test UserMetrics
    user_metrics = UserMetrics(
        metric_id="test-user-metric-001",
        user_id="test-user-001",
        metric_type="login",
        metric_timestamp="2025-08-20T10:00:00Z",
        created_at="2025-08-20T10:00:00Z",
        updated_at="2025-08-20T10:00:00Z"
    )
    print(f"✅ Created UserMetrics: {user_metrics.metric_id}")
    
    return True


def test_model_validation():
    """Test model validation."""
    print("🧪 Testing Model Validation...")
    
    try:
        # Test invalid email
        User(
            user_id="test-user-002",
            username="testuser2",
            email="invalid-email",  # Invalid email format
            full_name="Test User 2",
            password_hash="hashed_password_123",
            role="user",
            created_at="2025-08-20T10:00:00Z",
            updated_at="2025-08-20T10:00:00Z"
        )
        print("❌ Should have caught invalid email format")
        return False
    except ValueError as e:
        print(f"✅ Correctly caught validation error: {e}")
    
    try:
        # Test invalid health score
        CoreSystemRegistry(
            registry_id="test-registry-002",
            system_name="Test System 2",
            registry_name="Test Registry 2",
            created_at="2025-08-20T10:00:00Z",
            updated_at="2025-08-20T10:00:00Z",
            health_score=150.0  # Invalid health score > 100
        )
        print("❌ Should have caught invalid health score")
        return False
    except ValueError as e:
        print(f"✅ Correctly caught validation error: {e}")
    
    return True


def test_model_methods():
    """Test model methods."""
    print("🧪 Testing Model Methods...")
    
    # Test Organization methods
    org = Organization(
        org_id="test-org-002",
        name="Test Organization 2",
        created_at="2025-08-20T10:00:00Z",
        updated_at="2025-08-20T10:00:00Z"
    )
    org.add_partner("Partner A")
    org.add_partner("Partner B")
    print(f"✅ Organization partners: {org.partner_ecosystem}")
    
    org.remove_partner("Partner A")
    print(f"✅ After removing Partner A: {org.partner_ecosystem}")
    
    # Test Project methods
    project = Project(
        project_id="test-project-002",
        name="Test Project 2",
        created_at="2025-08-20T10:00:00Z",
        updated_at="2025-08-20T10:00:00Z"
    )
    project.add_tag("important")
    project.add_tag("urgent")
    print(f"✅ Project tags: {project.tags}")
    
    project.update_phase("completed")
    print(f"✅ Project phase updated to: {project.project_phase}")
    print(f"✅ Project completed: {project.is_completed}")
    
    # Test User methods
    user = User(
        user_id="test-user-003",
        username="testuser3",
        email="test3@example.com",
        full_name="Test User 3",
        password_hash="hashed_password_123",
        role="user",
        created_at="2025-08-20T10:00:00Z",
        updated_at="2025-08-20T10:00:00Z"
    )
    
    skills = user.get_skills()
    print(f"✅ User skills: {skills}")
    
    permissions = user.get_permissions()
    print(f"✅ User permissions: {permissions}")
    
    has_read = user.has_permission("read")
    print(f"✅ Has read permission: {has_read}")
    
    return True


def main():
    """Run all model tests."""
    print("🚀 Starting Model Tests...")
    
    success = True
    
    # Test core system models
    success &= test_core_system_models()
    
    # Test business domain models
    success &= test_business_domain_models()
    
    # Test authentication models
    success &= test_auth_models()
    
    # Test model validation
    success &= test_model_validation()
    
    # Test model methods
    success &= test_model_methods()
    
    if success:
        print("\n🎉 All tests passed! Models are working correctly.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
    
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
