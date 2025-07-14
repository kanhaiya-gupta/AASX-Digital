#!/usr/bin/env python3
"""
Quick Test Projects Creator
Creates test projects quickly for immediate testing of the web interface.
"""

import os
import json
import uuid
from datetime import datetime
from pathlib import Path

def create_quick_test_projects():
    """Create test projects quickly"""
    
    # Create base directories
    projects_dir = Path("data/projects")
    projects_dir.mkdir(parents=True, exist_ok=True)
    
    # Test projects
    test_projects = [
        {
            "id": str(uuid.uuid4()),
            "name": "Additive Manufacturing 3D Printing",
            "description": "Digital twin models for 3D printing equipment and processes",
            "tags": ["manufacturing", "3d-printing", "additive-manufacturing", "quality-control"],
            "file_count": 2,
            "total_size": 3584576
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Hydrogen Filling Station",
            "description": "Digital twin for hydrogen refueling station infrastructure",
            "tags": ["energy", "hydrogen", "fueling-station", "safety"],
            "file_count": 1,
            "total_size": 3072000
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Smart Grid Substation",
            "description": "Digital twin for smart grid substation monitoring and control",
            "tags": ["energy", "smart-grid", "substation", "monitoring"],
            "file_count": 1,
            "total_size": 2560000
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Quality Control Laboratory",
            "description": "Digital twin for quality control and testing laboratory equipment",
            "tags": ["quality-control", "laboratory", "testing", "compliance"],
            "file_count": 2,
            "total_size": 3072000
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Industrial IoT Sensors",
            "description": "Digital twin for industrial IoT sensor networks and data collection",
            "tags": ["iot", "sensors", "data-collection", "monitoring"],
            "file_count": 2,
            "total_size": 2560000
        }
    ]
    
    # Create projects and sample files
    projects_db = {}
    files_db = {}
    
    for project in test_projects:
        project_id = project["id"]
        project_dir = projects_dir / project_id
        project_dir.mkdir(exist_ok=True)
        
        # Add timestamps
        project["created_at"] = datetime.now().isoformat()
        project["updated_at"] = datetime.now().isoformat()
        
        # Create sample files for this project
        project_files = []
        for i in range(project["file_count"]):
            file_id = str(uuid.uuid4())
            filename = f"sample_file_{i+1}.aasx"
            file_path = project_dir / filename
            
            # Create a simple sample file
            sample_content = {
                "project": project["name"],
                "filename": filename,
                "description": f"Sample AASX file {i+1} for {project['name']}",
                "created_at": datetime.now().isoformat(),
                "asset_id": f"asset_{project_id}_{i}",
                "submodels": ["TechnicalData", "QualityAssurance", "Documentation"]
            }
            
            with open(file_path, "w") as f:
                json.dump(sample_content, f, indent=2)
            
            # Create file metadata
            file_info = {
                "id": file_id,
                "filename": filename,
                "original_filename": filename,
                "project_id": project_id,
                "filepath": str(file_path),
                "size": project["total_size"] // project["file_count"],
                "upload_date": datetime.now().isoformat(),
                "description": f"Sample AASX file {i+1}",
                "status": "uploaded",
                "processing_result": None
            }
            
            project_files.append(file_info)
            files_db[file_id] = file_info
        
        # Add project to database
        projects_db[project_id] = project
        
        print(f"✅ Created project: {project['name']} ({project['file_count']} files)")
    
    # Save database
    db_data = {
        "projects": projects_db,
        "files": files_db,
        "created_at": datetime.now().isoformat()
    }
    
    with open("data/test_database.json", "w") as f:
        json.dump(db_data, f, indent=2)
    
    print(f"\n🎉 Created {len(projects_db)} test projects with {len(files_db)} files!")
    print(f"📄 Database saved to: data/test_database.json")
    
    return projects_db, files_db

if __name__ == "__main__":
    create_quick_test_projects() 