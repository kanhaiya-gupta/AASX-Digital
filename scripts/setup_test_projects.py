#!/usr/bin/env python3
"""
Setup Test Projects Script
Creates test projects and sample AASX files for testing the enhanced ETL pipeline.
"""

import os
import json
import uuid
from datetime import datetime
from pathlib import Path
import shutil

def create_test_projects():
    """Create test projects with sample AASX files"""
    
    # Base directories
    base_dir = Path("data")
    projects_dir = base_dir / "projects"
    
    # Create directories if they don't exist
    projects_dir.mkdir(parents=True, exist_ok=True)
    
    # Test projects configuration
    test_projects = [
        {
            "id": str(uuid.uuid4()),
            "name": "Additive Manufacturing 3D Printing",
            "description": "Digital twin models for 3D printing equipment and processes",
            "tags": ["manufacturing", "3d-printing", "additive-manufacturing", "quality-control"],
            "files": [
                {
                    "name": "printer_model_1.aasx",
                    "description": "High-precision industrial 3D printer model",
                    "size": 2048576  # 2MB
                },
                {
                    "name": "printer_model_2.aasx", 
                    "description": "Multi-material 3D printer configuration",
                    "size": 1536000  # 1.5MB
                }
            ]
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Hydrogen Filling Station",
            "description": "Digital twin for hydrogen refueling station infrastructure",
            "tags": ["energy", "hydrogen", "fueling-station", "safety"],
            "files": [
                {
                    "name": "station_layout.aasx",
                    "description": "Complete hydrogen station layout and safety systems",
                    "size": 3072000  # 3MB
                }
            ]
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Smart Grid Substation",
            "description": "Digital twin for smart grid substation monitoring and control",
            "tags": ["energy", "smart-grid", "substation", "monitoring"],
            "files": [
                {
                    "name": "substation_config.aasx",
                    "description": "Smart grid substation configuration and monitoring setup",
                    "size": 2560000  # 2.5MB
                }
            ]
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Quality Control Laboratory",
            "description": "Digital twin for quality control and testing laboratory equipment",
            "tags": ["quality-control", "laboratory", "testing", "compliance"],
            "files": [
                {
                    "name": "lab_equipment.aasx",
                    "description": "Quality control laboratory equipment and calibration data",
                    "size": 1792000  # 1.75MB
                },
                {
                    "name": "testing_procedures.aasx",
                    "description": "Standard testing procedures and quality metrics",
                    "size": 1280000  # 1.25MB
                }
            ]
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Industrial IoT Sensors",
            "description": "Digital twin for industrial IoT sensor networks and data collection",
            "tags": ["iot", "sensors", "data-collection", "monitoring"],
            "files": [
                {
                    "name": "sensor_network.aasx",
                    "description": "Industrial IoT sensor network configuration",
                    "size": 1024000  # 1MB
                },
                {
                    "name": "data_pipeline.aasx",
                    "description": "Data pipeline and analytics configuration",
                    "size": 1536000  # 1.5MB
                }
            ]
        }
    ]
    
    # Create projects and files
    created_projects = []
    
    for project in test_projects:
        project_dir = projects_dir / project["id"]
        project_dir.mkdir(exist_ok=True)
        
        # Create project metadata
        project_metadata = {
            "id": project["id"],
            "name": project["name"],
            "description": project["description"],
            "tags": project["tags"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "file_count": len(project["files"]),
            "total_size": sum(f["size"] for f in project["files"])
        }
        
        # Save project metadata
        with open(project_dir / "project.json", "w") as f:
            json.dump(project_metadata, f, indent=2)
        
        # Create sample AASX files
        project_files = []
        for file_info in project["files"]:
            file_path = project_dir / file_info["name"]
            
            # Create a sample AASX file (simplified structure)
            sample_aasx_content = create_sample_aasx_content(
                project["name"], 
                file_info["name"], 
                file_info["description"]
            )
            
            with open(file_path, "w") as f:
                json.dump(sample_aasx_content, f, indent=2)
            
            # Create file metadata
            file_metadata = {
                "id": str(uuid.uuid4()),
                "filename": file_info["name"],
                "original_filename": file_info["name"],
                "project_id": project["id"],
                "filepath": str(file_path),
                "size": file_info["size"],
                "upload_date": datetime.now().isoformat(),
                "description": file_info["description"],
                "status": "uploaded",
                "processing_result": None
            }
            
            project_files.append(file_metadata)
        
        # Save project files metadata
        with open(project_dir / "files.json", "w") as f:
            json.dump(project_files, f, indent=2)
        
        created_projects.append(project_metadata)
        print(f"✅ Created project: {project['name']} ({len(project['files'])} files)")
    
    # Create a summary file
    summary = {
        "created_at": datetime.now().isoformat(),
        "total_projects": len(created_projects),
        "total_files": sum(p["file_count"] for p in created_projects),
        "total_size": sum(p["total_size"] for p in created_projects),
        "projects": created_projects
    }
    
    with open(projects_dir / "projects_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n🎉 Successfully created {len(created_projects)} test projects!")
    print(f"📁 Total files: {summary['total_files']}")
    print(f"💾 Total size: {format_file_size(summary['total_size'])}")
    print(f"📄 Summary saved to: {projects_dir / 'projects_summary.json'}")
    
    return created_projects

def create_sample_aasx_content(project_name, filename, description):
    """Create sample AASX content structure"""
    
    # Generate a unique asset ID based on project and filename
    asset_id = f"asset_{project_name.lower().replace(' ', '_')}_{filename.replace('.aasx', '')}"
    
    return {
        "aas": {
            "assetAdministrationShells": [
                {
                    "id": asset_id,
                    "idShort": filename.replace('.aasx', ''),
                    "description": [
                        {
                            "language": "en",
                            "text": description
                        }
                    ],
                    "asset": {
                        "id": f"asset_{asset_id}",
                        "idShort": "main_asset"
                    },
                    "submodels": [
                        {
                            "id": f"submodel_{asset_id}_technical",
                            "idShort": "TechnicalData",
                            "description": [
                                {
                                    "language": "en",
                                    "text": "Technical specifications and parameters"
                                }
                            ],
                            "submodelElements": [
                                {
                                    "id": f"property_{asset_id}_model",
                                    "idShort": "ModelNumber",
                                    "description": [
                                        {
                                            "language": "en",
                                            "text": "Equipment model number"
                                        }
                                    ],
                                    "valueType": "string",
                                    "value": "MODEL-2024-001"
                                },
                                {
                                    "id": f"property_{asset_id}_manufacturer",
                                    "idShort": "Manufacturer",
                                    "description": [
                                        {
                                            "language": "en",
                                            "text": "Equipment manufacturer"
                                        }
                                    ],
                                    "valueType": "string",
                                    "value": "Quality Industries Inc."
                                }
                            ]
                        },
                        {
                            "id": f"submodel_{asset_id}_quality",
                            "idShort": "QualityAssurance",
                            "description": [
                                {
                                    "language": "en",
                                    "text": "Quality assurance and compliance data"
                                }
                            ],
                            "submodelElements": [
                                {
                                    "id": f"property_{asset_id}_certification",
                                    "idShort": "CertificationStatus",
                                    "description": [
                                        {
                                            "language": "en",
                                            "text": "Current certification status"
                                        }
                                    ],
                                    "valueType": "string",
                                    "value": "CERTIFIED"
                                },
                                {
                                    "id": f"property_{asset_id}_last_inspection",
                                    "idShort": "LastInspection",
                                    "description": [
                                        {
                                            "language": "en",
                                            "text": "Date of last quality inspection"
                                        }
                                    ],
                                    "valueType": "date",
                                    "value": "2024-01-15"
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        "metadata": {
            "project_name": project_name,
            "filename": filename,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "aas_version": "3.0"
        }
    }

def format_file_size(bytes):
    """Format file size in human readable format"""
    if bytes == 0:
        return "0 B"
    k = 1024
    sizes = ['B', 'KB', 'MB', 'GB']
    i = int(math.floor(math.log(bytes) / math.log(k)))
    return f"{bytes / math.pow(k, i):.2f} {sizes[i]}"

def create_test_database():
    """Create test database entries for the web application"""
    
    # This would create the in-memory database entries that the web app expects
    # For now, we'll create a JSON file that can be loaded by the web app
    
    import math
    
    # Load the projects we just created
    projects_dir = Path("data/projects")
    summary_file = projects_dir / "projects_summary.json"
    
    if not summary_file.exists():
        print("❌ No test projects found. Run create_test_projects() first.")
        return
    
    with open(summary_file, "r") as f:
        summary = json.load(f)
    
    # Create database entries
    projects_db = {}
    files_db = {}
    
    for project in summary["projects"]:
        project_id = project["id"]
        project_dir = projects_dir / project_id
        
        # Load project files
        files_file = project_dir / "files.json"
        if files_file.exists():
            with open(files_file, "r") as f:
                project_files = json.load(f)
            
            # Add files to files_db
            for file_info in project_files:
                files_db[file_info["id"]] = file_info
        
        # Add project to projects_db
        projects_db[project_id] = project
    
    # Save database entries
    db_data = {
        "projects": projects_db,
        "files": files_db,
        "created_at": datetime.now().isoformat()
    }
    
    with open("data/test_database.json", "w") as f:
        json.dump(db_data, f, indent=2)
    
    print(f"✅ Created test database with {len(projects_db)} projects and {len(files_db)} files")
    print(f"📄 Database saved to: data/test_database.json")

def main():
    """Main function to set up test environment"""
    print("🚀 Setting up test projects for AASX ETL Pipeline...")
    print("=" * 60)
    
    # Create test projects
    projects = create_test_projects()
    
    print("\n" + "=" * 60)
    print("📊 Test Projects Summary:")
    print("=" * 60)
    
    for i, project in enumerate(projects, 1):
        print(f"{i}. {project['name']}")
        print(f"   📁 Files: {project['file_count']}")
        print(f"   💾 Size: {format_file_size(project['total_size'])}")
        print(f"   🏷️  Tags: {', '.join(project['tags'])}")
        print()
    
    # Create test database
    print("=" * 60)
    print("🗄️  Creating test database...")
    create_test_database()
    
    print("\n" + "=" * 60)
    print("✅ Test environment setup complete!")
    print("=" * 60)
    print("🎯 Next steps:")
    print("1. Start the web application: python main.py")
    print("2. Navigate to: http://localhost:8000/aasx/")
    print("3. Test the project management features")
    print("4. Upload and process AASX files")
    print("=" * 60)

if __name__ == "__main__":
    import math
    main() 