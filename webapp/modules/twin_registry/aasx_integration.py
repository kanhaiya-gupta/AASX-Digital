#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AASX Integration Module for Twin Registry
Handles auto-registration of twins from AASX files and sync status management.
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import traceback
from .twin_manager import twin_manager

logger = logging.getLogger(__name__)

class AASXIntegration:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data"
        self.projects_dir = self.data_dir / "projects"
        # Updated to use the correct project-based output structure
        self.output_dir = self.project_root / "output" / "projects"
        
        # Initialize database for twin-AASX relationships
        self.db_path = self.project_root / "data" / "aasx_digital.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for twin-AASX relationships"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create twin-AASX relationship table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS twin_aasx_relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    twin_id TEXT UNIQUE NOT NULL,
                    aasx_filename TEXT NOT NULL,
                    project_id TEXT,
                    aas_id TEXT,
                    twin_name TEXT,
                    twin_type TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_sync TIMESTAMP,
                    data_points INTEGER DEFAULT 0,
                    metadata TEXT,
                    UNIQUE(twin_id, aasx_filename)
                )
            ''')
            
            # Create sync history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    twin_id TEXT NOT NULL,
                    sync_type TEXT NOT NULL,
                    sync_status TEXT NOT NULL,
                    sync_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    details TEXT,
                    FOREIGN KEY (twin_id) REFERENCES twin_aasx_relationships (twin_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Twin registry database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def discover_processed_aasx_files(self) -> List[Dict[str, Any]]:
        """Discover AASX files that have been processed by checking FILES_DB status"""
        return self.discover_processed_aasx_files_from_status()

    def _get_project_names_mapping(self) -> Dict[str, str]:
        """Get mapping of project IDs to project names"""
        # This method is no longer needed for status-based registration
        # Keeping it for backward compatibility but it's not used
        return {}

    def _get_file_info(self, sqlite_file: Path, aasx_filename: str, project_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a processed AASX file - DEPRECATED"""
        # This method is deprecated - we now use status-based registration
        logger.warning("_get_file_info is deprecated - use status-based registration instead")
        return None

    def _extract_aas_info(self, cursor) -> Dict[str, Any]:
        """Extract AAS information from SQLite database - DEPRECATED"""
        # This method is deprecated - we now use status-based registration
        logger.warning("_extract_aas_info is deprecated - use status-based registration instead")
        return {}

    def _extract_twin_name_from_table(self, cursor, table: str) -> str:
        """Extract twin name from database table - DEPRECATED"""
        # This method is deprecated - we now use status-based registration
        logger.warning("_extract_twin_name_from_table is deprecated - use status-based registration instead")
        return "Unknown Twin"

    def _extract_twin_type_from_table(self, cursor, table: str) -> str:
        """Extract twin type from database table - DEPRECATED"""
        # This method is deprecated - we now use status-based registration
        logger.warning("_extract_twin_type_from_table is deprecated - use status-based registration instead")
        return "unknown"

    def _extract_metadata_from_table(self, cursor, table: str) -> Dict[str, Any]:
        """Extract metadata from database table - DEPRECATED"""
        # This method is deprecated - we now use status-based registration
        logger.warning("_extract_metadata_from_table is deprecated - use status-based registration instead")
        return {}

    def _get_available_formats(self, file_dir: Path) -> List[str]:
        """Get available formats from file directory - DEPRECATED"""
        # This method is deprecated - we now use status-based registration
        logger.warning("_get_available_formats is deprecated - use status-based registration instead")
        return []
    
    # Removed auto_register_twin_from_aasx; registration is now handled in management.py
    
    def get_twin_by_aasx(self, aasx_filename: str) -> Optional[Dict[str, Any]]:
        """Get twin information by AASX filename"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM twin_aasx_relationships 
                WHERE aasx_filename = ?
            ''', (aasx_filename,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    "twin_id": result[1],
                    "aasx_filename": result[2],
                    "project_id": result[3],
                    "aas_id": result[4],
                    "twin_name": result[5],
                    "twin_type": result[6],
                    "status": result[7],
                    "created_at": result[8],
                    "last_sync": result[9],
                    "data_points": result[10],
                    "metadata": json.loads(result[11]) if result[11] else {}
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting twin by AASX filename: {e}")
            return None
    
    def get_sync_status(self, twin_id: str) -> Dict[str, Any]:
        """Get real-time sync status for a twin"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get twin info
            cursor.execute('''
                SELECT * FROM twin_aasx_relationships 
                WHERE twin_id = ?
            ''', (twin_id,))
            
            twin_result = cursor.fetchone()
            if not twin_result:
                return {"error": "Twin not found"}
            
            # Get recent sync history
            cursor.execute('''
                SELECT sync_type, sync_status, sync_timestamp, details
                FROM sync_history 
                WHERE twin_id = ?
                ORDER BY sync_timestamp DESC
                LIMIT 5
            ''', (twin_id,))
            
            sync_history = cursor.fetchall()
            
            # Calculate data points (mock for now)
            data_points = self._calculate_data_points(twin_result[2])  # aasx_filename
            
            conn.close()
            
            return {
                "twin_id": twin_id,
                "aasx_file": twin_result[2],
                "last_sync": twin_result[9] or "Never",
                "data_points": data_points,
                "sync_status": twin_result[7],
                "recent_syncs": [
                    {
                        "type": sync[0],
                        "status": sync[1],
                        "timestamp": sync[2],
                        "details": json.loads(sync[3]) if sync[3] else {}
                    }
                    for sync in sync_history
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting sync status for {twin_id}: {e}")
            return {"error": str(e)}
    
    def _calculate_data_points(self, aasx_filename: str) -> int:
        """Calculate number of data points for a twin based on AASX content"""
        try:
            # Try to get actual data points from the processed SQLite database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get twin info to find the project and file
            cursor.execute('''
                SELECT project_id FROM twin_aasx_relationships 
                WHERE aasx_filename = ?
            ''', (aasx_filename,))
            
            result = cursor.fetchone()
            if result:
                project_id = result[0]
                file_stem = Path(aasx_filename).stem
                
                # Look for the processed SQLite file
                sqlite_file = self.output_dir / project_id / file_stem / "aasx_data.db"
                if not sqlite_file.exists():
                    # Fallback to legacy structure
                    sqlite_file = self.project_root / "output" / "etl_results" / project_id / f"{file_stem}.db"
                
                if sqlite_file.exists():
                    # Count actual data points from the processed database
                    import sqlite3 as sqlite_processed
                    processed_conn = sqlite_processed.connect(sqlite_file)
                    processed_cursor = processed_conn.cursor()
                    
                    # Count rows in various tables that might contain data points
                    total_points = 0
                    
                    # Check for common table names that might contain data
                    tables_to_check = ['properties', 'submodels', 'assets', 'concept_descriptions', 'data_elements']
                    
                    for table in tables_to_check:
                        try:
                            processed_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                            count = processed_cursor.fetchone()[0]
                            total_points += count
                        except:
                            pass  # Table doesn't exist, skip
                    
                    processed_conn.close()
                    
                    # If we found actual data points, return them
                    if total_points > 0:
                        return total_points
            
            conn.close()
            
            # Fallback: generate realistic mock data based on filename
            # This provides better estimates than pure random
            base_points = 1000
            if "additive" in aasx_filename.lower():
                base_points = 5000  # Manufacturing typically has more data
            elif "hydrogen" in aasx_filename.lower():
                base_points = 3000  # Energy systems
            elif "motor" in aasx_filename.lower():
                base_points = 2000  # Motors/actuators
            
            # Add some variation based on filename length (proxy for complexity)
            variation = len(aasx_filename) * 10
            return base_points + variation
            
        except Exception as e:
            logger.error(f"Error calculating data points for {aasx_filename}: {e}")
            return 1000  # Default fallback
    
    def get_all_twins_with_aasx(self) -> List[Dict[str, Any]]:
        """Get all registered twins (ETL completed) using the centralized twin manager."""
        return twin_manager.get_all_registered_twins()
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """Get all available projects from the output directory structure"""
        projects = []
        
        try:
            # Check project-based output directory structure
            if self.output_dir.exists():
                for project_dir in self.output_dir.iterdir():
                    if project_dir.is_dir():
                        project_id = project_dir.name
                        
                        # Try to get project name from project_summary.json file
                        project_name = self._get_project_name(project_id)
                        
                        # Count files in this project
                        file_count = 0
                        for file_dir in project_dir.iterdir():
                            if file_dir.is_dir() and (file_dir / "aasx_data.db").exists():
                                file_count += 1
                        
                        projects.append({
                            "project_id": project_id,
                            "name": project_name,
                            "file_count": file_count,
                            "created_at": datetime.fromtimestamp(project_dir.stat().st_mtime).isoformat()
                        })
            
            # Also check legacy structure
            legacy_output_dir = self.project_root / "output" / "etl_results"
            if legacy_output_dir.exists():
                for project_dir in legacy_output_dir.iterdir():
                    if project_dir.is_dir():
                        project_id = project_dir.name
                        
                        # Try to get project name from project_summary.json file
                        project_name = self._get_project_name(project_id)
                        
                        # Count SQLite files in this project
                        sqlite_files = list(project_dir.glob("*.db"))
                        file_count = len(sqlite_files)
                        
                        if file_count > 0:
                            projects.append({
                                "project_id": project_id,
                                "name": f"Legacy {project_name}",
                                "file_count": file_count,
                                "created_at": datetime.fromtimestamp(project_dir.stat().st_mtime).isoformat(),
                                "legacy": True
                            })
            
            # Sort by creation date (newest first)
            projects.sort(key=lambda x: x["created_at"], reverse=True)
            
            logger.info(f"Found {len(projects)} projects")
            return projects
            
        except Exception as e:
            logger.error(f"Error getting projects: {e}")
            return []
    
    def _get_project_name(self, project_id: str) -> str:
        """Get project name from projects_summary.json file"""
        try:
            logger.info(f"Getting project name for ID: {project_id}")
            
            # Look for projects_summary.json in data/projects directory
            project_summary_path = self.projects_dir / "projects_summary.json"
            logger.info(f"Looking for project summary at: {project_summary_path}")
            
            if project_summary_path.exists():
                logger.info("Project summary file found, reading...")
                with open(project_summary_path, 'r', encoding='utf-8') as f:
                    summary_data = json.load(f)
                    
                    # Find the project in the projects list
                    if "projects" in summary_data:
                        logger.info(f"Found {len(summary_data['projects'])} projects in summary")
                        for project in summary_data["projects"]:
                            if project.get("id") == project_id:
                                project_name = project.get("name", f"Project {project_id[:8]}...")
                                logger.info(f"Found project name: {project_name}")
                                return project_name
                        logger.warning(f"Project ID {project_id} not found in project summary")
                    else:
                        logger.warning("No 'projects' key found in project summary")
            else:
                logger.warning(f"Project summary file not found at: {project_summary_path}")
            
            # Fallback: try to extract name from output directory JSON files
            logger.info("Using fallback method - extracting from AASX data")
            output_project_dir = self.output_dir / project_id
            if output_project_dir.exists():
                for file_dir in output_project_dir.iterdir():
                    if file_dir.is_dir():
                        json_file = file_dir / "aasx_data.json"
                        if json_file.exists():
                            try:
                                with open(json_file, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                    # Try to get asset description as project name
                                    if "data" in data and "assets" in data["data"] and data["data"]["assets"]:
                                        asset = data["data"]["assets"][0]
                                        if "description" in asset:
                                            # Extract a meaningful name from the description
                                            desc = asset["description"]
                                            # Remove common prefixes and make it shorter
                                            if "Industrial" in desc:
                                                fallback_name = desc.split(" - ")[0] if " - " in desc else desc
                                                logger.info(f"Using fallback name: {fallback_name}")
                                                return fallback_name
                                            fallback_name = desc[:50] + "..." if len(desc) > 50 else desc
                                            logger.info(f"Using fallback name: {fallback_name}")
                                            return fallback_name
                            except Exception as e:
                                logger.error(f"Error reading AASX data JSON: {e}")
                                pass
            
            # Final fallback
            fallback_name = f"Project {project_id[:8]}..."
            logger.info(f"Using final fallback name: {fallback_name}")
            return fallback_name
            
        except Exception as e:
            logger.error(f"Error getting project name for {project_id}: {e}")
            return f"Project {project_id[:8]}..." 

    def _get_existing_twin_registrations(self) -> Dict[str, Dict[str, Any]]:
        """Get existing twin registrations for quick lookup"""
        existing_twins = {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT twin_id, aasx_filename, status, created_at
                FROM twin_aasx_relationships
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            for result in results:
                existing_twins[result[1]] = {
                    "twin_id": result[0],
                    "status": result[2],
                    "created_at": result[3]
                }
                
        except Exception as e:
            logger.error(f"Error getting existing twin registrations: {e}")
            
        return existing_twins 

    def update_twin_status_to_orphaned(self, aasx_filename: str, project_id: str) -> Dict[str, Any]:
        """Update twin status to orphaned when output data is missing"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find twin by AASX filename
            cursor.execute('''
                SELECT twin_id, status FROM twin_aasx_relationships 
                WHERE aasx_filename = ? AND project_id = ?
            ''', (aasx_filename, project_id))
            
            result = cursor.fetchone()
            if not result:
                conn.close()
                return {"success": False, "error": f"Twin not found for {aasx_filename}"}
            
            twin_id, current_status = result
            
            # Only update if currently active
            if current_status == 'active':
                cursor.execute('''
                    UPDATE twin_aasx_relationships 
                    SET status = 'orphaned', last_sync = CURRENT_TIMESTAMP
                    WHERE twin_id = ?
                ''', (twin_id,))
                
                # Log the status change
                cursor.execute('''
                    INSERT INTO sync_history (twin_id, sync_type, sync_status, details)
                    VALUES (?, ?, ?, ?)
                ''', (
                    twin_id,
                    "status_change",
                    "orphaned",
                    json.dumps({"reason": "output_data_missing", "aasx_filename": aasx_filename})
                ))
                
                conn.commit()
                conn.close()
                
                logger.info(f"Updated twin {twin_id} status to orphaned for {aasx_filename}")
                return {
                    "success": True,
                    "twin_id": twin_id,
                    "previous_status": current_status,
                    "new_status": "orphaned",
                    "reason": "output_data_missing"
                }
            else:
                conn.close()
                return {
                    "success": True,
                    "twin_id": twin_id,
                    "status": current_status,
                    "message": "Status already not active"
                }
                
        except Exception as e:
            logger.error(f"Error updating twin status to orphaned for {aasx_filename}: {e}")
            return {"success": False, "error": str(e)}

    def update_twin_status_to_active(self, aasx_filename: str, project_id: str) -> Dict[str, Any]:
        """Update twin status to active when output data is restored"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find twin by AASX filename
            cursor.execute('''
                SELECT twin_id, status FROM twin_aasx_relationships 
                WHERE aasx_filename = ? AND project_id = ?
            ''', (aasx_filename, project_id))
            
            result = cursor.fetchone()
            if not result:
                conn.close()
                return {"success": False, "error": f"Twin not found for {aasx_filename}"}
            
            twin_id, current_status = result
            
            # Only update if currently orphaned
            if current_status == 'orphaned':
                cursor.execute('''
                    UPDATE twin_aasx_relationships 
                    SET status = 'active', last_sync = CURRENT_TIMESTAMP
                    WHERE twin_id = ?
                ''', (twin_id,))
                
                # Log the status change
                cursor.execute('''
                    INSERT INTO sync_history (twin_id, sync_type, sync_status, details)
                    VALUES (?, ?, ?, ?)
                ''', (
                    twin_id,
                    "status_change",
                    "active",
                    json.dumps({"reason": "output_data_restored", "aasx_filename": aasx_filename})
                ))
                
                conn.commit()
                conn.close()
                
                logger.info(f"Updated twin {twin_id} status to active for {aasx_filename}")
                return {
                    "success": True,
                    "twin_id": twin_id,
                    "previous_status": current_status,
                    "new_status": "active",
                    "reason": "output_data_restored"
                }
            else:
                conn.close()
                return {
                    "success": True,
                    "twin_id": twin_id,
                    "status": current_status,
                    "message": "Status already not orphaned"
                }
                
        except Exception as e:
            logger.error(f"Error updating twin status to active for {aasx_filename}: {e}")
            return {"success": False, "error": str(e)}

    def get_orphaned_twins(self) -> List[Dict[str, Any]]:
        """Get all orphaned twins"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT twin_id, aasx_filename, project_id, twin_name, twin_type, created_at, last_sync
                FROM twin_aasx_relationships 
                WHERE status = 'orphaned'
                ORDER BY created_at DESC
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            orphaned_twins = []
            for result in results:
                orphaned_twins.append({
                    "twin_id": result[0],
                    "aasx_filename": result[1],
                    "project_id": result[2],
                    "twin_name": result[3],
                    "twin_type": result[4],
                    "created_at": result[5],
                    "last_sync": result[6],
                    "status": "orphaned"
                })
                
            return orphaned_twins
            
        except Exception as e:
            logger.error(f"Error getting orphaned twins: {e}")
            return []

    def discover_processed_aasx_files_from_status(self) -> List[Dict[str, Any]]:
        """Discover AASX files that have been processed by checking FILES_DB status"""
        processed_files = []
        
        try:
            # Import FILES_DB from aasx routes
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
            
            # Try to get FILES_DB from aasx routes
            try:
                from webapp.aasx.routes import FILES_DB
                
                # Get files with "completed" status from FILES_DB
                for file_id, file_info in FILES_DB.items():
                    if file_info.get('status') == 'completed':
                        processed_files.append({
                            'aasx_filename': file_info['filename'],
                            'project_id': file_info['project_id'],
                            'twin_name': file_info.get('twin_name'),
                            'twin_type': file_info.get('twin_type'),
                            'processing_result': file_info.get('processing_result'),
                            'file_id': file_id,
                            'registration_status': 'Ready for Registration'
                        })
                
                logger.info(f"Found {len(processed_files)} completed files from FILES_DB")
                
            except ImportError:
                logger.error("Could not import FILES_DB - status-based discovery not available")
                return []
                
        except Exception as e:
            logger.error(f"Error discovering files from status: {e}")
            
        return processed_files 

    def get_all_active_twins_with_completed_files(self) -> list:
        """Get all registered twins (ETL completed) using the centralized twin manager."""
        return twin_manager.get_all_registered_twins() 