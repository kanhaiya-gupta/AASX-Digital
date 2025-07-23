import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

def get_project_dir(base_dir: Path, project_id: str) -> Path:
    """
    Get the path to a project directory.
    """
    return base_dir / project_id


def create_project(base_dir: Path, project_id: str, metadata: Dict[str, Any]) -> Path:
    """
    Create a project directory and project.json if not exists.
    Returns the project directory path.
    """
    project_dir = get_project_dir(base_dir, project_id)
    project_dir.mkdir(parents=True, exist_ok=True)
    project_json = project_dir / "project.json"
    if not project_json.exists():
        with open(project_json, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
    return project_dir


def load_files_manifest(project_dir: Path) -> list:
    """
    Load files.json manifest as a list. Returns empty list if not exists.
    """
    files_json = project_dir / "files.json"
    if files_json.exists():
        with open(files_json, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_files_manifest(project_dir: Path, files: list):
    """
    Save the files.json manifest.
    """
    files_json = project_dir / "files.json"
    with open(files_json, "w", encoding="utf-8") as f:
        json.dump(files, f, indent=2)


def register_file(project_dir: Path, file_info: Dict[str, Any]):
    """
    Add or update a file entry in files.json.
    """
    files = load_files_manifest(project_dir)
    for i, entry in enumerate(files):
        if entry["filename"] == file_info["filename"]:
            files[i] = file_info  # Update existing
            break
    else:
        files.append(file_info)  # Add new
    save_files_manifest(project_dir, files)


def check_duplicate_file(project_dir: Path, filename: str) -> bool:
    """
    Return True if file already exists in files.json.
    """
    files = load_files_manifest(project_dir)
    return any(entry["filename"] == filename for entry in files)


def update_processing_status(project_dir: Path, filename: str, status: str, result: Optional[Any] = None):
    """
    Update the status and (optionally) processing result for a file in files.json.
    """
    files = load_files_manifest(project_dir)
    for entry in files:
        if entry["filename"] == filename:
            entry["status"] = status
            if result is not None:
                entry["processing_result"] = result
            break
    save_files_manifest(project_dir, files)


def load_project_metadata(project_dir: Path) -> Dict[str, Any]:
    """
    Load project.json metadata.
    """
    project_json = project_dir / "project.json"
    if project_json.exists():
        with open(project_json, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_project_metadata(project_dir: Path, metadata: Dict[str, Any]):
    """
    Save project.json metadata.
    """
    project_json = project_dir / "project.json"
    with open(project_json, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2) 